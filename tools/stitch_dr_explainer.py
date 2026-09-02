#!/usr/bin/env python3
"""Stitch the DR explainer footage into labelled side-by-side videos.

Input: the directory written by ``tools/render_dr_explainer.sh``:

    <root>/<arm>/<preset>/render_results/000000.mp4 ...
    <root>/<arm>/<preset>/metrics_eval.json           (the same cell's metrics)

Output, in <root>/final/:

    dr_explainer_<preset>.mp4   three arms side by side at one difficulty
    dr_explainer_grid.mp4       3 arms x 3 presets, one frame of truth
    dr_explainer_story.mp4      the three presets played in sequence

Each panel is labelled with the arm, what it trained on, the difficulty, and
the success rate the SAME checkpoint scored on the full 512-episode panel at
that cell, read from the frozen ledger receipts rather than from the four
rendered episodes. The footage shows one draw; the number is the measurement.

usage: stitch_dr_explainer.py <root> [--env-index 0]
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
import shutil
import subprocess
import sys

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MANIFESTS = Path("/home/linjiw/lucid-sonic/manifests")
PRE_CLAMP_RECEIPTS = {"curriculum_robustness_ne512_20260829_214540.json"}

ARMS = [
    ("off_s8600", "no randomization", 8600, "off"),
    ("fixed_s8600", "full DR, fixed", 8600, "fixed"),
    ("ratchet_s8601", "full DR, monotone ratchet", 8601, "lucid_ratchet_rg"),
]
PRESETS = [
    ("phys_000", "nominal physics  (lambda 0)"),
    ("phys_150", "heavy randomization  (lambda 1.5)"),
    ("phys_200", "extreme randomization  (lambda 2.0)"),
]


def ledger_success(seed: int, mode: str, preset: str) -> float | None:
    """The 512-episode success rate this exact checkpoint scored at this cell.

    Read from every evaluation receipt on disk; a cell supplied by more than
    one receipt must agree (the evaluator is bit-deterministic on this panel)
    or it is reported as unavailable rather than picked from.
    """
    paths = sorted(MANIFESTS.glob("curriculum_robustness_ne512_*.json"))
    paths += sorted(MANIFESTS.glob("ratchet_*/**/curriculum_robustness_ne512_*.json"))
    values: set[float] = set()
    frontier = {"phys_125", "phys_150", "phys_175", "phys_200"}
    for path in paths:
        # Preregistered supersession: this receipt predates dr_scaling.clamp_physical
        # and its lambda>1 cells are excluded at phys_125 and above.
        if path.name in PRE_CLAMP_RECEIPTS and preset in frontier:
            continue
        try:
            receipt = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        runs = receipt.get("runs", {})
        rows = runs.values() if isinstance(runs, dict) else runs
        for row in rows:
            if row.get("runtime", {}).get("exit_code") != 0:
                continue
            if int(row["checkpoint_seed"]) == seed and row["mode"] == mode and row["preset"] == preset:
                values.add(round(float(row["summary"]["success_rate"]), 6))
    if len(values) == 1:
        return values.pop()
    return None


def rendered_success(cell_dir: Path) -> float | None:
    """Success over the few rendered episodes, for the caption only."""
    for candidate in cell_dir.rglob("metrics_eval.json"):
        try:
            data = json.loads(candidate.read_text())
        except json.JSONDecodeError:
            continue
        terminated = data.get("eval/all_metrics_dict", {}).get("terminated")
        if terminated:
            return 1.0 - sum(bool(t) for t in terminated) / len(terminated)
    return None


def esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def label_filter(lines: list[str], size: int = 30) -> str:
    """Stacked drawtext lines, top-left, on a translucent strip."""
    parts = [f"drawbox=x=0:y=0:w=iw:h={size * (len(lines) + 1)}:color=black@0.45:t=fill"]
    for i, line in enumerate(lines):
        parts.append(
            f"drawtext=fontfile={FONT}:text='{esc(line)}':x=24:y={16 + i * size}:"
            f"fontsize={size - 6}:fontcolor=white"
        )
    return ",".join(parts)


def run(cmd: list[str]) -> None:
    print("  $", " ".join(cmd[:6]), "...", file=sys.stderr)
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--env-index", type=int, default=0)
    args = parser.parse_args(argv)

    if shutil.which("ffmpeg") is None:
        print("ffmpeg not found", file=sys.stderr)
        return 1
    final = args.root / "final"
    final.mkdir(exist_ok=True)
    labelled: dict[tuple[str, str], Path] = {}
    captions: dict[str, dict[str, dict[str, float | None]]] = {}

    for preset, preset_label in PRESETS:
        captions[preset] = {}
        for arm, arm_label, seed, mode in ARMS:
            cell = args.root / arm / preset
            videos = sorted(glob.glob(str(cell / "render_results" / "*.mp4")))
            if not videos:
                print(f"missing footage: {cell}", file=sys.stderr)
                return 1
            src = Path(videos[min(args.env_index, len(videos) - 1)])
            ledger = ledger_success(seed, mode, preset)
            shown = rendered_success(cell)
            captions[preset][arm] = {"ledger_success": ledger, "rendered_success": shown}
            ledger_txt = "n/a" if ledger is None else f"{100 * ledger:.1f}% success"
            lines = [
                arm_label,
                preset_label,
                f"512-episode score: {ledger_txt}",
            ]
            out = final / f"{arm}_{preset}_labelled.mp4"
            run(
                [
                    "ffmpeg", "-y", "-i", str(src), "-vf", label_filter(lines),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(out),
                ]
            )
            labelled[(arm, preset)] = out

    # One difficulty, three arms side by side.
    for preset, _ in PRESETS:
        inputs = []
        for arm, *_ in ARMS:
            inputs += ["-i", str(labelled[(arm, preset)])]
        out = final / f"dr_explainer_{preset}.mp4"
        run(
            [
                "ffmpeg", "-y", *inputs, "-filter_complex",
                "[0:v][1:v][2:v]hstack=inputs=3[v]", "-map", "[v]",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(out),
            ]
        )

    # The whole ladder in one frame: rows = difficulty, columns = arm.
    inputs = []
    layout = []
    idx = 0
    for r, (preset, _) in enumerate(PRESETS):
        for c, (arm, *_) in enumerate(ARMS):
            inputs += ["-i", str(labelled[(arm, preset)])]
            layout.append(f"{'+'.join(['w0'] * c) or '0'}_{'+'.join(['h0'] * r) or '0'}")
            idx += 1
    out = final / "dr_explainer_grid.mp4"
    run(
        [
            "ffmpeg", "-y", *inputs, "-filter_complex",
            f"{''.join(f'[{i}:v]' for i in range(idx))}xstack=inputs={idx}:layout={'|'.join(layout)}[v]",
            "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", str(out),
        ]
    )

    # The story: nominal, then heavy, then extreme, back to back.
    concat = final / "concat.txt"
    concat.write_text("".join(f"file '{final / f'dr_explainer_{p}.mp4'}'\n" for p, _ in PRESETS))
    run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
            "-c", "copy", str(final / "dr_explainer_story.mp4"),
        ]
    )

    (final / "captions.json").write_text(json.dumps(captions, indent=2))
    print(json.dumps({"final_dir": str(final), "captions": captions}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
