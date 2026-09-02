#!/usr/bin/env python3
"""Build the MuJoCo explainer as a story: every seed shown, every failure marked.

For each (arm, lambda) it renders seeds 1..N (the player stops at the first
fall), then composes an N-tile grid in which each tile is captioned
``seed k · PASS`` in green or ``seed k · FELL at t s`` in red, a failed tile
freezes on its last frame so the fall stays on screen, and a header carries
the arm's label and its pass rate at that difficulty. Arms are then placed
side by side per difficulty and the difficulties are cut in sequence.

Every number on screen comes from the run that produced the tile; nothing
is typed in by hand.

usage: mujoco_story.py --out DIR --lams 0 1.0 1.5 [--seeds 8] [--arms ...]
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mujoco_sweep import ARMS, CLIP, LABEL, PLAYER, PY  # noqa: E402

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
TILE_W, TILE_H = 480, 270
FPS = 50
HOLD = 0.8  # seconds a failed tile freezes on its last frame
ISAAC_PRESET = {"0": "phys_000", "0.5": "phys_050", "1": "phys_100", "1.25": "phys_125", "1.5": "phys_150", "2": "phys_200"}
LAM_LABEL = {"0": "nominal physics (λ 0)", "0.5": "mild randomization (λ 0.5)", "1": "training envelope (λ 1.0)",
             "1.25": "beyond the envelope (λ 1.25)", "1.5": "heavy randomization (λ 1.5)", "2": "extreme (λ 2.0)"}


def esc(t: str) -> str:
    out = t.replace("\\", "\\\\")
    for ch in (":", ",", "'", "[", "]", ";"):
        out = out.replace(ch, "\\" + ch)
    return out


def ff(cmd: list[str]) -> None:
    p = subprocess.run(["ffmpeg", "-y", "-v", "error", *cmd], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    bad = [ln for ln in p.stderr.splitlines() if "Stray %" in ln or "rror" in ln]
    if p.returncode != 0 or bad:
        raise RuntimeError("ffmpeg: " + (bad[0] if bad else p.stderr[-400:]) + "\n  cmd: " + " ".join(cmd[:8]))


def render(arm: str, lam: str, seed: int, out: Path) -> dict:
    d = out / "tiles" / arm / f"lam{lam}"
    d.mkdir(parents=True, exist_ok=True)
    mp4, js = d / f"seed{seed}.mp4", d / f"seed{seed}.json"
    if not (mp4.is_file() and js.is_file()):
        env = dict(os.environ, MUJOCO_GL="egl", PYOPENGL_PLATFORM="egl")
        subprocess.run([PY, str(PLAYER), "--onnx", str(ARMS[arm]), "--clip", CLIP, "--out", str(mp4), "--lam", lam,
                        "--seed", str(seed), "--width", str(TILE_W), "--height", str(TILE_H)],
                       env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return json.loads(js.read_text())["result"]


def tile(arm: str, lam: str, seed: int, res: dict, out: Path, total: float) -> Path:
    src = out / "tiles" / arm / f"lam{lam}" / f"seed{seed}.mp4"
    dst = out / "tiles" / arm / f"lam{lam}" / f"seed{seed}_marked.mp4"
    fell = bool(res["fell"])
    text = f"seed {seed}  ·  FELL at {res['t_end']:.1f} s" if fell else f"seed {seed}  ·  PASS"
    color = "0xE0483A" if fell else "0x3FB950"
    # Freeze the last frame on a fall (tpad clones it), then pad every tile to
    # the same length with black so the grid stays aligned.
    vf = (f"scale={TILE_W}:{TILE_H},"
          f"tpad=stop_mode=clone:stop_duration={HOLD if fell else 0},"
          f"drawbox=x=0:y=0:w=iw:h=34:color=black@0.55:t=fill,"
          f"drawtext=fontfile={FONT}:text='{esc(text)}':x=10:y=8:fontsize=20:fontcolor={color}:expansion=none,"
          + (f"drawbox=x=0:y=0:w=iw:h=ih:color={color}@0.9:t=6," if fell else "")
          + f"tpad=stop_mode=add:stop_duration={total + HOLD + 0.5},trim=duration={total + HOLD + 0.5},fps={FPS}")
    ff(["-i", str(src), "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", str(dst)])
    return dst


def grid(arm: str, lam: str, tiles: list[Path], results: list[dict], out: Path, cols: int, isaac: float | None) -> Path:
    n = len(tiles)
    rows = (n + cols - 1) // cols
    passed = sum(1 for r in results if not r["fell"])
    dst = out / "grids" / f"{arm}_lam{lam}.mp4"
    dst.parent.mkdir(parents=True, exist_ok=True)
    inputs = []
    layout = []
    for i in range(n):
        inputs += ["-i", str(tiles[i])]
        c, r = i % cols, i // cols
        layout.append(f"{'+'.join(['w0'] * c) or '0'}_{'+'.join(['h0'] * r) or '0'}")
    header = 74
    hdr1 = LABEL[arm]
    hdr2 = f"{LAM_LABEL.get(lam, 'λ ' + lam)}   ·   MuJoCo pass rate {passed}/{n}"
    if isaac is not None:
        hdr2 += f"   ·   Isaac 512-episode score {100 * isaac:.1f}%"
    fc = f"{''.join(f'[{i}:v]' for i in range(n))}xstack=inputs={n}:layout={'|'.join(layout)}:fill=black[g];" \
         f"[g]pad=iw:ih+{header}:0:{header}:color=0x14181A[p];" \
         f"[p]drawtext=fontfile={FONT}:text='{esc(hdr1)}':x=16:y=12:fontsize=26:fontcolor=white:expansion=none," \
         f"drawtext=fontfile={FONT}:text='{esc(hdr2)}':x=16:y=44:fontsize=20:fontcolor=0xBFC8CC:expansion=none[v]"
    ff([*inputs, "-filter_complex", fc, "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", str(dst)])
    return dst


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--lams", nargs="+", default=["0", "1", "1.5"])
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--arms", nargs="+", default=list(ARMS))
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from stitch_dr_explainer import ledger_success  # noqa: E402

    seeds = list(range(1, a.seeds + 1))
    total = 4.0
    story_inputs = []
    manifest: dict = {}
    for lam in a.lams:
        manifest[lam] = {}
        per_arm = []
        for arm in a.arms:
            with ThreadPoolExecutor(max_workers=a.jobs) as ex:
                results = list(ex.map(lambda s: render(arm, lam, s, a.out), seeds))
            tiles = [tile(arm, lam, s, r, a.out, total) for s, r in zip(seeds, results)]
            arm_seed, mode = {"off_s8600": (8600, "off"), "fixed_s8600": (8600, "fixed"),
                              "ratchet_s8601": (8601, "lucid_ratchet_rg"),
                              "lucid_collapsed_s8601": (8601, "lucid_rg")}[arm]
            isaac = ledger_success(arm_seed, mode, ISAAC_PRESET.get(lam, ""))
            g = grid(arm, lam, tiles, results, a.out, a.cols, isaac)
            per_arm.append(g)
            manifest[lam][arm] = {"pass": sum(1 for r in results if not r["fell"]), "n": len(results),
                                  "fall_times": [r["t_end"] for r in results if r["fell"]], "isaac": isaac}
            print(f"  {arm} λ{lam}: {manifest[lam][arm]['pass']}/{len(results)} pass", file=sys.stderr, flush=True)
        # arms side by side for this difficulty (2 x 2 if four arms, else row)
        n = len(per_arm)
        cols = 2 if n == 4 else n
        inputs, layout = [], []
        for i, g in enumerate(per_arm):
            inputs += ["-i", str(g)]
            c, r = i % cols, i // cols
            layout.append(f"{'+'.join(['w0'] * c) or '0'}_{'+'.join(['h0'] * r) or '0'}")
        dst = a.out / f"story_lam{lam}.mp4"
        ff([*inputs, "-filter_complex", f"{''.join(f'[{i}:v]' for i in range(n))}xstack=inputs={n}:layout={'|'.join(layout)}:fill=black[v]",
            "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", str(dst)])
        story_inputs.append(dst)
    concat = a.out / "concat.txt"
    concat.write_text("".join(f"file '{p}'\n" for p in story_inputs))
    ff(["-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(a.out / "story.mp4")])
    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(json.dumps(manifest, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
