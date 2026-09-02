#!/usr/bin/env python3
"""Parallel MuJoCo survival sweep over arms x lambdas x seeds, with fall times.

Runs tools/mujoco_player.py without video across a grid and writes one table:

    <out>/sweep.json   {arm: {lam: {seed: {"fell": bool, "t_end": s, ...}}}}
    <out>/summary.md   pass rates per arm x lambda, and mean time-to-fall

Seeds are shared across arms at each lambda, so every arm faces the identical
sequence of physics draws and pushes. That makes per-seed comparison fair and
lets a video later show the same draw side by side.

usage: mujoco_sweep.py --out DIR [--lams 0 0.5 1.0 1.5 2.0] [--seeds 32] [--jobs 6]
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import subprocess
import sys

PY = "/home/linjiw/isaaclab-install/env_isaaclab/bin/python"
PLAYER = Path(__file__).resolve().parent / "mujoco_player.py"
CLIP = "/home/linjiw/lucid-sonic/pools/debug512/robot_filtered/walk_hands_on_back_loop_002__A066_M.pkl"
A = Path("/home/linjiw/lucid-sonic/artifacts/curriculum_comparison")

ARMS = {
    "off_s8600": A / "curriculum_comparison_ne1024_20260829_000249/seed_8600/off/exported/model_step_008000_g1.onnx",
    "lucid_collapsed_s8601": A / "curriculum_comparison_ne1024_20260829_000249/seed_8601/lucid_rg/exported/model_step_008000_g1.onnx",
    "fixed_s8600": A / "curriculum_comparison_ne1024_20260829_000249/seed_8600/fixed/exported/model_step_008000_g1.onnx",
    "ratchet_s8601": A / "curriculum_comparison_ne1024_20260831_144022/seed_8601/lucid_ratchet_rg/exported/model_step_008000_g1.onnx",
}
LABEL = {
    "off_s8600": "no randomization",
    "lucid_collapsed_s8601": "feedback curriculum, unconstrained (collapsed to λ 0.06)",
    "fixed_s8600": "fixed full DR",
    "ratchet_s8601": "feedback curriculum + monotone ratchet (ours)",
}


def one(arm: str, onnx: Path, lam: float, seed: int, out: Path) -> tuple[str, float, int, dict]:
    d = out / "runs" / arm / f"lam{lam:g}"
    d.mkdir(parents=True, exist_ok=True)
    js = d / f"seed{seed}.json"
    if js.is_file():
        return arm, lam, seed, json.loads(js.read_text())["result"]
    env = dict(os.environ, MUJOCO_GL="egl", PYOPENGL_PLATFORM="egl")
    cmd = [PY, str(PLAYER), "--onnx", str(onnx), "--clip", CLIP, "--out", str(d / f"seed{seed}.mp4"),
           "--lam", f"{lam:g}", "--seed", str(seed), "--no-video"]
    proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if proc.returncode != 0 or not js.is_file():
        return arm, lam, seed, {"fell": None, "t_end": None, "error": True}
    return arm, lam, seed, json.loads(js.read_text())["result"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--lams", type=float, nargs="+", default=[0, 0.5, 1.0, 1.5, 2.0])
    ap.add_argument("--seeds", type=int, default=32)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--arms", nargs="+", default=list(ARMS))
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    arms = {k: ARMS[k] for k in a.arms}
    for k, p in arms.items():
        if not p.is_file():
            print(f"missing onnx for {k}: {p}", file=sys.stderr)
            return 1
    jobs = [(arm, onnx, lam, seed) for lam in a.lams for arm in arms for seed in range(1, a.seeds + 1)
            for onnx in [arms[arm]]]
    table: dict = {arm: {f"{lam:g}": {} for lam in a.lams} for arm in arms}
    done = 0
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = [ex.submit(one, arm, onnx, lam, seed, a.out) for arm, onnx, lam, seed in jobs]
        for f in as_completed(futs):
            arm, lam, seed, res = f.result()
            table[arm][f"{lam:g}"][str(seed)] = res
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(jobs)}", file=sys.stderr, flush=True)
    (a.out / "sweep.json").write_text(json.dumps({"arms": {k: str(v) for k, v in arms.items()}, "labels": LABEL,
                                                   "lams": a.lams, "seeds": a.seeds, "table": table}, indent=1))
    lines = ["| arm | " + " | ".join(f"λ {lam:g}" for lam in a.lams) + " |", "|---|" + "---|" * len(a.lams)]
    for arm in arms:
        cells = []
        for lam in a.lams:
            rs = [r for r in table[arm][f"{lam:g}"].values() if r.get("fell") is not None]
            ok = sum(1 for r in rs if not r["fell"])
            tf = [r["t_end"] for r in rs if r["fell"]]
            mt = f", fall {sum(tf) / len(tf):.1f}s" if tf else ""
            cells.append(f"{ok}/{len(rs)} ({100 * ok / max(1, len(rs)):.0f}%{mt})")
        lines.append(f"| {LABEL.get(arm, arm)} | " + " | ".join(cells) + " |")
    (a.out / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
