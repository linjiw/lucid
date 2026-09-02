#!/usr/bin/env python3
"""Stitch the MuJoCo DR explainer into labelled side-by-side videos.

Input: the directory written by the MuJoCo batch:

    <root>/sweep/<arm>/lam<λ>/seed*.json     8-seed survival, no video
    <root>/video/<arm>/lam<λ>.mp4            one shared-seed rendering

Output in <root>/final/:

    mujoco_explainer_lam<λ>.mp4   three arms side by side at one difficulty
    mujoco_explainer_grid.mp4     3 arms x 3 difficulties in one frame
    mujoco_explainer_story.mp4    nominal, heavy, extreme in sequence

Each panel is captioned with two numbers and says which is which: the
MuJoCo survival over eight physics seeds at this lambda (what this player
measures), and the 512-episode success the same checkpoint scored in the
Isaac evaluator at the matching ladder cell (the paper's number). The two
simulators randomize differently and are never pooled.
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stitch_dr_explainer import FONT, esc, ledger_success  # noqa: E402

ARMS = [
    ("off_s8600", "no randomization", 8600, "off"),
    ("fixed_s8600", "full DR, fixed", 8600, "fixed"),
    ("ratchet_s8601", "full DR, monotone ratchet", 8601, "lucid_ratchet_rg"),
]
LAMS = [("0", "nominal physics  (λ 0)", "phys_000"),
        ("1.0", "training envelope  (λ 1.0)", "phys_100"),
        ("1.5", "heavy randomization  (λ 1.5)", "phys_150"),
        ("2.0", "extreme randomization  (λ 2.0)", "phys_200")]


def survival(root: Path, arm: str, lam: str) -> tuple[int, int]:
    files = sorted(glob.glob(str(root / "sweep" / arm / f"lam{lam}" / "seed*.json")))
    ok = 0
    for f in files:
        try:
            ok += not json.loads(Path(f).read_text())["result"]["fell"]
        except (KeyError, json.JSONDecodeError):
            pass
    return ok, len(files)


def label(lines: list[str], size: int = 28) -> str:
    parts = [f"drawbox=x=0:y=0:w=iw:h={size * (len(lines) + 1)}:color=black@0.5:t=fill"]
    for i, line in enumerate(lines):
        parts.append(f"drawtext=fontfile={FONT}:text='{esc(line)}':x=22:y={14 + i * size}:fontsize={size - 6}:fontcolor=white")
    return ",".join(parts)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path)
    a = ap.parse_args(argv)
    final = a.root / "final"
    final.mkdir(exist_ok=True)
    labelled: dict[tuple[str, str], Path] = {}
    captions: dict = {}
    for lam, lam_label, preset in LAMS:
        captions[lam] = {}
        for arm, arm_label, seed, mode in ARMS:
            src = a.root / "video" / arm / f"lam{lam}.mp4"
            if not src.is_file():
                print(f"missing footage: {src}", file=sys.stderr)
                return 1
            ok, n = survival(a.root, arm, lam)
            ledger = ledger_success(seed, mode, preset)
            captions[lam][arm] = {"mujoco_survived": ok, "mujoco_seeds": n, "isaac_ledger_success": ledger}
            shared = (a.root / "video" / f"shared_seed_lam{lam}.txt")
            seed_txt = f" (this draw: seed {shared.read_text().strip()})" if shared.is_file() else ""
            lines = [
                arm_label,
                lam_label,
                f"MuJoCo: {ok}/{n} physics seeds survived the clip{seed_txt}",
                f"Isaac ledger, 512 episodes: {'n/a' if ledger is None else f'{100 * ledger:.1f}% success'}",
            ]
            out = final / f"{arm}_lam{lam}.mp4"
            run(["ffmpeg", "-y", "-i", str(src), "-vf", label(lines), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(out)])
            labelled[(arm, lam)] = out
    for lam, _, _ in LAMS:
        inputs = []
        for arm, *_ in ARMS:
            inputs += ["-i", str(labelled[(arm, lam)])]
        run(["ffmpeg", "-y", *inputs, "-filter_complex", "[0:v][1:v][2:v]hstack=inputs=3[v]", "-map", "[v]",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(final / f"mujoco_explainer_lam{lam}.mp4")])
    inputs, layout, idx = [], [], 0
    for r, (lam, _, _) in enumerate(LAMS):
        for c, (arm, *_) in enumerate(ARMS):
            inputs += ["-i", str(labelled[(arm, lam)])]
            layout.append(f"{'+'.join(['w0'] * c) or '0'}_{'+'.join(['h0'] * r) or '0'}")
            idx += 1
    run(["ffmpeg", "-y", *inputs, "-filter_complex",
         f"{''.join(f'[{i}:v]' for i in range(idx))}xstack=inputs={idx}:layout={'|'.join(layout)}[v]",
         "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", str(final / "mujoco_explainer_grid.mp4")])
    concat = final / "concat.txt"
    concat.write_text("".join(f"file '{final / f'mujoco_explainer_lam{lam}.mp4'}'\n" for lam, _, _ in LAMS))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(final / "mujoco_explainer_story.mp4")])
    (final / "captions.json").write_text(json.dumps(captions, indent=2))
    print(json.dumps({"final_dir": str(final), "captions": captions}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
