#!/usr/bin/env python3
"""Read out the warm-start expansion prototype against its preregistered rules.

Read-only. Inputs are the comparison driver's training receipt(s) for the
prototype experiment and the scoring receipt(s) written by
run_expansion_prototype_scoring.sh. Outputs, per arm:

  mechanism   from the arm's curriculum jsonl: final frontier (scalar and, for
              box arms, per channel), expansions and when they fired, channels
              visited, applied decreases (must be 0), guard trips
  endpoints   primary {phys_175, phys_200} mean success; asymmetric primary
              {ch_mass_300, ch_com_300, ch_joint_300} mean; push at 2x/3x;
              in-support cells reported and labelled
  rules       R1 box_150 vs gate_150 (primary, +/-0.03)
              R6 box_asym vs ramp_asym (asym primary, +/-0.03)
              R5 width: fixed_150 vs best of gate/box/ramp (primary, +0.03)
              R7 fixed_asym vs fixed_150 on the asym cells (informational)
              R3 zero decreases on every arm; R4 box mechanism (>= 3 channels
              visited and >= 1 expansion, else STALLED)

usage: analyze_expansion_prototype.py --training-receipt R [--training-receipt R2]
           [--scoring-dir DIR ...] [--out readout.json]
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
import statistics
from typing import Any

LUCID_ROOT = Path("/home/linjiw/lucid-sonic")
PRIMARY = ("phys_175", "phys_200")
WIDE = ("phys_250", "phys_300")
ASYM_PRIMARY = ("ch_mass_300", "ch_com_300", "ch_joint_300")
PUSH = ("ch_push_200", "ch_push_300")
IN_SUPPORT_150 = ("phys_100", "phys_125", "phys_150")
ALL_CELLS = ("phys_100", "phys_125", "phys_150", "phys_175", "phys_200", "phys_250", "phys_300", "ch_fric_150", "ch_fric_200",
             "ch_mass_200", "ch_mass_300", "ch_com_200", "ch_com_300", "ch_joint_200", "ch_joint_300",
             "ch_push_200", "ch_push_300")
ASYM_ARMS = {"box_asym", "ramp_asym", "fixed_asym"}
THRESHOLD = 0.03


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def mechanism(mode: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    steps = [r for r in rows if not r.get("warmup_hold")]
    lam = [float(r["lambda"]) for r in steps if isinstance(r.get("lambda"), (int, float))]
    decreases = sum(1 for a, b in zip(lam, lam[1:]) if b < a - 1e-9)
    applied = sum(1 for r in steps if r.get("applied_decrease"))
    out: dict[str, Any] = {
        "mode": mode,
        "rows": len(rows),
        "lambda_first": lam[0] if lam else None,
        "lambda_final": lam[-1] if lam else None,
        "lambda_max": max(lam) if lam else None,
        "scalar_decreases_in_trace": decreases,
        "applied_decrease_flags": applied,
        "guard_trip_iterations": sum(1 for r in steps if r.get("guard_tripped")),
        "fired": [(r.get("global_step"), r.get("frontier_before"), r.get("frontier_after")) for r in steps if r.get("fired")],
    }
    out["expansions"] = len(out["fired"])
    out["first_fire_iteration"] = out["fired"][0][0] if out["fired"] else None
    box = [r for r in steps if r.get("mode") == "box"]
    if box:
        last = box[-1]
        vec = last.get("frontier_vector") or {}
        out["frontier_vector_final"] = vec
        out["channel_expansions"] = last.get("channel_expansions")
        out["channel_visits"] = last.get("channel_visits")
        out["channels_visited"] = sum(1 for v in (last.get("channel_visits") or {}).values() if v > 0)
        out["fired"] = [(r.get("global_step"), r.get("active_channel"), (r.get("frontier_vector") or {}).get(r.get("active_channel"))) for r in box if r.get("fired")]
        out["expansions"] = len(out["fired"])
        out["first_fire_iteration"] = out["fired"][0][0] if out["fired"] else None
        # Per-channel monotonicity from the trace itself, not the controller's flag.
        prev: dict[str, float] = {}
        vector_decreases = 0
        for r in box:
            v = r.get("frontier_vector") or {}
            for k, x in v.items():
                if k in prev and x < prev[k] - 1e-9:
                    vector_decreases += 1
                prev[k] = x
        out["vector_decreases_in_trace"] = vector_decreases
        out["withheld_counts"] = {}
        for r in box:
            w = r.get("withheld")
            out["withheld_counts"][w] = out["withheld_counts"].get(w, 0) + 1
        out["stalled"] = out["channels_visited"] < 3 or out["expansions"] < 1
    return out


def collect_scores(dirs: list[Path]) -> dict[tuple[str, str], float]:
    cells: dict[tuple[str, str], float] = {}
    for d in dirs:
        for path in glob.glob(str(d / "**" / "*.json"), recursive=True):
            try:
                receipt = json.loads(Path(path).read_text())
            except (OSError, ValueError):
                continue
            if receipt.get("kind") != "lucid_frozen_checkpoint_robustness_evaluation":
                continue
            for run in receipt.get("runs", {}).values():
                if run.get("complete") and (run.get("summary") or {}).get("success_rate") is not None:
                    cells[(run["mode"], run["preset"])] = float(run["summary"]["success_rate"])
    return cells


def mean_of(cells: dict[tuple[str, str], float], mode: str, presets: tuple[str, ...]) -> float | None:
    vals = [cells[(mode, p)] for p in presets if (mode, p) in cells]
    return statistics.fmean(vals) if len(vals) == len(presets) else None


def verdict(delta: float | None, pos: str, neg: str, flat: str) -> str:
    if delta is None:
        return "not scored"
    if delta >= THRESHOLD:
        return pos
    if delta <= -THRESHOLD:
        return neg
    return flat


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-receipt", type=Path, action="append", required=True)
    parser.add_argument("--scoring-dir", type=Path, action="append", default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    scoring_dirs = args.scoring_dir or [Path(p) for p in sorted(glob.glob(str(LUCID_ROOT / "manifests" / "expansion_prototype_scoring_*")))]
    cells = collect_scores(scoring_dirs)

    arms: dict[str, dict[str, Any]] = {}
    for receipt_path in args.training_receipt:
        receipt = json.loads(receipt_path.read_text())
        for arm in receipt.get("arms", {}).values():
            mode = arm["mode"]
            cur = Path(arm["curriculum_path"]) if arm.get("curriculum_path") else None
            rows = read_jsonl(cur) if cur and cur.exists() else []
            entry = {
                "seed": arm.get("seed"), "complete": arm.get("complete"), "checkpoint": arm.get("checkpoint"),
                "training_receipt": str(receipt_path), "mechanism": mechanism(mode, rows) if rows else None,
                "cells": {p: cells.get((mode, p)) for p in ALL_CELLS},
                "primary_phys175_200": mean_of(cells, mode, PRIMARY),
            "wide_corner_phys250_300": mean_of(cells, mode, WIDE),
                "asym_primary_mass_com_joint_3x": mean_of(cells, mode, ASYM_PRIMARY),
                "push_2x_3x": mean_of(cells, mode, PUSH),
                "in_support_labelled": list(IN_SUPPORT_150) + (["phys_175", "phys_200"] if mode in ASYM_ARMS else []),
            }
            arms[mode] = entry

    def p(mode: str) -> float | None:
        return arms.get(mode, {}).get("primary_phys175_200")

    def a(mode: str) -> float | None:
        return arms.get(mode, {}).get("asym_primary_mass_com_joint_3x")

    def w(mode: str) -> float | None:
        return arms.get(mode, {}).get("wide_corner_phys250_300")

    rules: dict[str, Any] = {}
    d1 = None if p("box_150") is None or p("gate_150") is None else p("box_150") - p("gate_150")
    rules["R1_box_vs_gate_primary"] = {"delta": d1, "verdict": verdict(d1, "box advances to a from-scratch cell vs gate_150", "box shelved; diagnose frontier_vector offline", "no scalar-vs-vector difference at this budget")}
    d6 = None if a("box_asym") is None or a("ramp_asym") is None else a("box_asym") - a("ramp_asym")
    rules["R6_box_asym_vs_ramp_asym_asym_primary"] = {"delta": d6, "verdict": verdict(d6, "box_asym advances to a from-scratch cell vs ramp_asym", "box_asym shelved; diagnose offline", "no feedback effect on the asymmetric box at this budget")}
    best_sched = [x for x in (p("gate_150"), p("box_150"), p("ramp_150")) if x is not None]
    d5 = None if p("fixed_150") is None or not best_sched else p("fixed_150") - max(best_sched)
    rules["R5_width_wins"] = {"delta": d5, "verdict": "width without scheduling wins at this budget (headline)" if d5 is not None and d5 >= THRESHOLD else ("not scored" if d5 is None else "scheduling not beaten by plain width by >= 0.03")}
    d7 = None if a("fixed_asym") is None or a("fixed_150") is None else a("fixed_asym") - a("fixed_150")
    rules["R7_fixed_asym_vs_fixed_150_asym_cells"] = {"delta": d7, "reading": "informational: what widening the cheap channels buys on their own cells"}
    r2 = None if p("gate_150") is None or p("ramp_150") is None else p("gate_150") - p("ramp_150")
    rules["R2_gate_vs_ramp_primary"] = {"delta": r2, "reading": "informational at this budget"}
    d8 = None if w("gate_300") is None or w("fixed_300") is None else w("gate_300") - w("fixed_300")
    rules["R8_gate_vs_blind_width_wide_corner"] = {"delta": d8, "verdict": verdict(d8, "feedback beats blind width where width is unsafe", "blind width wins even at 3.0; report the frontier the gate stopped at", "no difference at this budget")}
    d9 = None if w("box_fast_300") is None or w("gate_300") is None else w("box_fast_300") - w("gate_300")
    rules["R9_box_vs_gate_wide_corner"] = {"delta": d9, "verdict": verdict(d9, "the per-channel box beats the scalar gate where width is unsafe", "the box is worse than the scalar gate", "no scalar-vs-vector difference at this budget")}
    d11 = None if w("gate_300_ng") is None or w("gate_300") is None else w("gate_300_ng") - w("gate_300")
    rules["R11_guard_free_gate_vs_guarded"] = {"delta": d11, "reading": "where the survival probe alone stops; read with the arm's final frontier"}
    # R10 / R12: damage at nominal physics. The origin scores 0.994 there and
    # paired noise at saturation is about 1 point, so 0.97 is the line.
    rules["R10_damage_at_phys_100"] = {
        mode: {"phys_100": e["cells"].get("phys_100"),
               "verdict": ("not scored" if e["cells"].get("phys_100") is None
                           else ("DAMAGED" if e["cells"]["phys_100"] < 0.97 else "healthy"))}
        for mode, e in arms.items()}
    rules["R3_zero_decreases"] = {
        mode: {"scalar_decreases_in_trace": (e["mechanism"] or {}).get("scalar_decreases_in_trace"), "vector_decreases_in_trace": (e["mechanism"] or {}).get("vector_decreases_in_trace"), "applied_decrease_flags": (e["mechanism"] or {}).get("applied_decrease_flags")}
        for mode, e in arms.items() if e["mechanism"]}
    rules["R3_all_zero"] = all(
        (v["scalar_decreases_in_trace"] or 0) == 0 and (v["vector_decreases_in_trace"] or 0) == 0 and (v["applied_decrease_flags"] or 0) == 0
        for v in rules["R3_zero_decreases"].values())
    rules["R4_box_mechanism"] = {mode: ("STALLED" if (e["mechanism"] or {}).get("stalled") else "expanded") for mode, e in arms.items() if mode.startswith("box") and e["mechanism"]}

    report = {"kind": "lucid_expansion_prototype_readout", "schema_version": 1, "threshold": THRESHOLD,
              "scoring_dirs": [str(d) for d in scoring_dirs], "cells_found": len(cells), "arms": arms, "rules": rules,
              "caveats": ["single seed; paired noise on the two-cell band ~2.7 points", "warm start from the fixed@s8600 final; from-scratch confirmation is Phase 2's job",
                          "asym arms: phys_175/phys_200 are IN SUPPORT on mass/CoM/joint and are labelled, not gated on"]}
    text = json.dumps(report, indent=2, default=str)
    if args.out:
        args.out.write_text(text)

    order = ["fixed", "fixed_150", "ramp_150", "gate_150", "box_150", "fixed_asym", "ramp_asym", "box_asym"]
    order += ["gate_300", "fixed_300", "box_fast_300", "gate_300_ng"]
    print(f"{'arm':13s} {'final λ':>8s} {'exp':>4s} {'dec':>4s} | {'p100':>6s} {'p150':>6s} {'p175':>6s} {'p200':>6s} {'PRIM':>6s} | {'p250':>6s} {'p300':>6s} {'WIDE':>6s} | {'ASYM':>6s} {'push3':>6s}")
    for mode in order:
        e = arms.get(mode)
        if not e:
            continue
        m = e["mechanism"] or {}
        c = e["cells"]
        fmt = lambda v: f"{v:6.3f}" if isinstance(v, (int, float)) else f"{'-':>6s}"
        lam = m.get("lambda_final")
        vec = m.get("frontier_vector_final")
        lam_s = f"{lam:8.3f}" if isinstance(lam, (int, float)) else f"{'-':>8s}"
        print(f"{mode:13s} {lam_s} {m.get('expansions', '-'):>4} {str((m.get('scalar_decreases_in_trace') or 0) + (m.get('vector_decreases_in_trace') or 0)):>4s} | {fmt(c.get('phys_100'))} {fmt(c.get('phys_150'))} {fmt(c.get('phys_175'))} {fmt(c.get('phys_200'))} {fmt(e['primary_phys175_200'])} | {fmt(c.get('phys_250'))} {fmt(c.get('phys_300'))} {fmt(e['wide_corner_phys250_300'])} | {fmt(e['asym_primary_mass_com_joint_3x'])} {fmt(c.get('ch_push_300'))}")
        if vec:
            print(f"{'':11s} frontier_vector {json.dumps({k.replace('randomize_','').replace('add_joint_default_pos','joint').replace('physics_material','fric').replace('base_com','com').replace('rigid_body_mass','mass').replace('action_delay','delay').replace('push_robot','push'): round(v,3) for k,v in vec.items()})}  visits {m.get('channel_visits')}")
    print()
    for k, v in rules.items():
        if isinstance(v, dict) and "delta" in v:
            d = v["delta"]
            print(f"{k}: delta={'-' if d is None else f'{d:+.4f}'}  {v.get('verdict') or v.get('reading')}")
    print("R3 zero decreases on every arm:", rules["R3_all_zero"], "| R4:", rules["R4_box_mechanism"])
    print("R10 damage at phys_100:", {k: v["verdict"] for k, v in rules["R10_damage_at_phys_100"].items() if v["verdict"] != "not scored"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
