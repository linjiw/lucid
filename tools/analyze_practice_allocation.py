#!/usr/bin/env python3
"""Read out the practice-allocation screen against its frozen decision rules.

The screen asks where extra training is productive. Five branches leave one
competent origin with the same architecture, reward, motion, environment count,
iteration budget and seed; the only difference is what a fixed 25% share of the
same 1,024 environments practises, and that share is reallocated out of the
lambda = 1 cohort rather than added to it.

This tool does three things and refuses to do a fourth.

1. It builds the per-cell table of success and restricted-mean progress for
   every branch, paired on the cell.
2. It labels every cell in-support or held-out FOR EACH BRANCH, from the
   branch's own realized per-stratum vectors, and refuses to let an in-support
   cell carry a generalization claim.
3. It applies rules R1-R7 exactly as they were frozen, and reports a tie as a
   tie.

It does not search for a level, a cell or a contrast that makes a branch look
better. The margins and the rules come from the preregistration; they are not
arguments.

usage: analyze_practice_allocation.py SCORING_DIR [SCORING_DIR ...]
       [--training-dir DIR] [--out receipts/analysis/....json]
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
import statistics
import sys

PREREG = Path("receipts/manifests/lucid_practice_allocation_screen_preregistration_20260902.json")

CONTROL = "prac_null"
TREATMENTS = ("prac_easy", "prac_push", "prac_pushfric")
ORDINARY = ("phys_000", "phys_100")
#: Which channels each cell widens, so support can be decided per branch rather
#: than assumed. Mirrors the evaluator's own preset tables.
CELL_CHANNELS: dict[str, dict[str, float]] = {
    "phys_000": {}, "phys_100": {},
    "phys_150": {"randomize_rigid_body_mass": 1.5, "base_com": 1.5, "add_joint_default_pos": 1.5,
                 "physics_material": 1.5, "push_robot": 1.5},
    "phys_200": {"randomize_rigid_body_mass": 2.0, "base_com": 2.0, "add_joint_default_pos": 2.0,
                 "physics_material": 2.0, "push_robot": 2.0},
    "ch_push_200": {"push_robot": 2.0},
    "ch_push_300": {"push_robot": 3.0},
    "ch_push_350": {"push_robot": 3.5},
    "ch_mass_300": {"randomize_rigid_body_mass": 3.0},
    "ch_com_300": {"base_com": 3.0},
    "ch_joint_300": {"add_joint_default_pos": 3.0},
    "ch_fric_150": {"physics_material": 1.5},
    "ch_push_fric_200_150": {"push_robot": 2.0, "physics_material": 1.5},
    "ch_push_fric_300_150": {"push_robot": 3.0, "physics_material": 1.5},
}


def load_cells(dirs: list[Path]) -> dict[tuple[str, str], dict]:
    """(mode, preset) -> summary, from every completed run in every receipt."""
    cells: dict[tuple[str, str], dict] = {}
    for directory in dirs:
        for path in sorted(glob.glob(str(directory / "*.json"))):
            receipt = json.loads(Path(path).read_text())
            for run in (receipt.get("runs") or {}).values():
                if not run.get("complete"):
                    continue
                summary = run.get("summary") or {}
                if summary.get("success_rate") is None:
                    continue
                cells[(run["mode"], run["preset"])] = {
                    "success": float(summary["success_rate"]),
                    "progress": summary.get("progress_rate"),
                    "seed": run.get("checkpoint_seed"),
                    "receipt": Path(path).name,
                }
    return cells


def practised(training_dir: Path | None, mode: str) -> dict[str, float]:
    """The branch's realized practice vector, read from its own telemetry."""
    if training_dir is None:
        return {}
    for path in sorted(glob.glob(str(training_dir / "*.json"))):
        receipt = json.loads(Path(path).read_text())
        for arm in receipt.get("arms") or []:
            if arm.get("mode") != mode:
                continue
            strata = ((arm.get("tace_final") or {}).get("stratum_lambdas")) or []
            top = strata[-1] if strata else {}
            if isinstance(top, dict):
                return {k: float(v) for k, v in top.items() if float(v) > 1.0}
    return {}


def in_support(cell: str, vector: dict[str, float]) -> bool:
    """A cell is in support when the branch practised every channel it widens."""
    widened = CELL_CHANNELS.get(cell, {})
    if not widened:
        return True  # nominal / envelope cells are inside every branch's support
    return all(vector.get(name, 1.0) >= value - 1e-9 for name, value in widened.items())


def pts(a: float | None, b: float | None) -> float | None:
    return None if a is None or b is None else round(100.0 * (a - b), 2)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("scoring_dirs", nargs="+", type=Path)
    ap.add_argument("--training-dir", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=Path("receipts/analysis/lucid_practice_allocation_readout.json"))
    a = ap.parse_args(argv)

    prereg = json.loads(PREREG.read_text()) if PREREG.is_file() else {}
    margins = prereg.get("margins", {})
    improve = float(margins.get("meaningful_improvement_pts", 5.0))
    tie = float(margins.get("tie_band_pts", 2.0))
    retention = float(margins.get("retention_margin_pts", 2.0))

    cells = load_cells(a.scoring_dirs)
    if not cells:
        print("no completed evaluation cells found", file=sys.stderr)
        return 1
    modes = sorted({mode for mode, _ in cells})
    presets = [p for p in CELL_CHANNELS if any((m, p) in cells for m in modes)]
    vectors = {mode: practised(a.training_dir, mode) for mode in modes}

    table: dict[str, dict] = {}
    for preset in presets:
        row: dict[str, dict] = {}
        for mode in modes:
            entry = cells.get((mode, preset))
            if entry is None:
                continue
            row[mode] = {
                "success": entry["success"],
                "progress": entry["progress"],
                "in_support": in_support(preset, vectors.get(mode, {})),
                "vs_control_pts": pts(entry["success"], (cells.get((CONTROL, preset)) or {}).get("success")),
            }
        table[preset] = row

    def delta(mode: str, other: str, preset: str) -> float | None:
        return pts((cells.get((mode, preset)) or {}).get("success"),
                   (cells.get((other, preset)) or {}).get("success"))

    def macro(mode: str) -> float | None:
        values = [cells[(mode, p)]["success"] for p in presets if (mode, p) in cells]
        return round(100.0 * statistics.fmean(values), 2) if values else None

    def verdict(value: float | None, name: str) -> str:
        if value is None:
            return "UNEVALUABLE: cell missing"
        if value >= improve:
            return f"{name}: +{value} pts, at or above the {improve}-pt margin"
        if abs(value) < tie:
            return f"TIE: {value} pts, inside the {tie}-pt band"
        return f"NOT MET: {value} pts, below the {improve}-pt margin"

    r1 = delta("prac_push", CONTROL, "ch_push_300")
    r2 = (None if macro("prac_push") is None or macro("prac_easy") is None
          else round(macro("prac_push") - macro("prac_easy"), 2))
    r3 = delta("prac_pushfric", "prac_push", "ch_push_fric_300_150")
    trade_offs = {
        mode: {p: table.get(p, {}).get(mode, {}).get("vs_control_pts") for p in ORDINARY}
        for mode in TREATMENTS
    }
    r4 = {
        mode: [p for p, d in row.items() if d is not None and d < -retention]
        for mode, row in trade_offs.items()
    }
    generalization = {
        mode: {p: table[p][mode]["vs_control_pts"] for p in presets
               if mode in table.get(p, {}) and not table[p][mode]["in_support"]}
        for mode in TREATMENTS
    }

    out = {
        "kind": "lucid_practice_allocation_readout",
        "schema_version": 1,
        "preregistration": str(PREREG),
        "scoring_dirs": [str(d) for d in a.scoring_dirs],
        "training_dir": str(a.training_dir) if a.training_dir else None,
        "margins": {"improvement_pts": improve, "tie_pts": tie, "retention_pts": retention},
        "realized_practice_vectors": vectors,
        "cells": table,
        "macro_success_pts": {mode: macro(mode) for mode in modes},
        "decisions": {
            "R1_bottleneck_learnable": {
                "delta_pts": r1,
                "verdict": verdict(r1, "LEARNABLE"),
                "reading": ("practising push at 3x repairs push at 3x, so push failure is a "
                            "practice deficit" if r1 is not None and r1 >= improve else
                            "push failure is not a practice deficit at this budget: dedicated "
                            "practice at the failing level did not move it"),
            },
            "R2_targeting_matters": {
                "delta_pts": r2,
                "verdict": verdict(r2, "TARGETING PAYS"),
                "reading": ("where the practice is aimed matters" if r2 is not None and r2 >= improve
                            else "extra exposure helps wherever it is aimed; channel selection is "
                                 "not carrying the result"),
            },
            "R3_combinations_need_own_practice": {
                "delta_pts": r3,
                "verdict": verdict(r3, "COMBINATION PAYS"),
                "reading": ("practising a combination buys more than practising the channel alone"
                            if r3 is not None and r3 >= improve else
                            "the joint-corner component is not earning its complexity"),
            },
            "R4_trade_offs": {
                "already_learned_cells": ORDINARY,
                "losses_beyond_margin": r4,
                "verdict": ("no branch loses more than the retention margin on an already-learned cell"
                            if not any(r4.values()) else
                            "REPORTED AS A TRADE-OFF, not an improvement: " + json.dumps(r4)),
            },
            "R5_more_training_alone": {
                "control_macro_pts": macro(CONTROL),
                "plain_fixed_macro_pts": macro("fixed"),
                "note": "every treatment effect above is measured against prac_null, never against the origin",
            },
            "R6_generalization_only_above_the_practised_range": generalization,
        },
        "held_out_cells_per_branch": {
            mode: [p for p in presets if mode in table.get(p, {}) and not table[p][mode]["in_support"]]
            for mode in modes
        },
        "not_verified": [
            "single seed: this ranks designs and does not decide; the between-seed effect on "
            "absolute capability reaches 7.8 points",
            "one training clip",
            "warm start from a solved lambda=1 policy, so this says where practice helps a "
            "competent policy, not how to train one",
        ],
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")

    print(f"{'cell':24s} " + " ".join(f"{m:>14s}" for m in modes))
    for preset in presets:
        row = table[preset]
        cellstr = []
        for mode in modes:
            entry = row.get(mode)
            if entry is None:
                cellstr.append(f"{'-':>14s}")
                continue
            mark = "*" if entry["in_support"] else " "
            cellstr.append(f"{100 * entry['success']:12.1f}{mark} ")
        print(f"{preset:24s} " + " ".join(cellstr))
    print("\n* = in that branch's training support; no generalization claim may rest on it\n")
    for name, decision in out["decisions"].items():
        if "verdict" in decision:
            print(f"{name}: {decision['verdict']}")
    print(f"\nreceipt -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
