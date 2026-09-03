#!/usr/bin/env python3
"""Read out the actuator-channel screen: does any of them do anything?

Five frozen policies, thirteen cells, no training. The screen answers three
questions per channel, in this order, and stops at the first "no":

1. **Is it live?** Does the channel change a competent policy's outcome at all?
   A channel whose top rung leaves the fixed-DR policy where ``act_off`` found it
   is not randomizing anything, and this project has shipped exactly that bug
   before, so it is checked first and checked against the arm least likely to be
   fragile.
2. **Is it survivable?** Does at least one policy stay off the floor at the top
   rung? A severity nothing reaches is an unlearnable task. It is not a
   learnability barrier and must never be reported as one.
3. **Does it separate policies?** Does the spread across arms widen relative to
   ``act_off``? A channel that lowers everyone equally measures difficulty but
   not capability, and adds nothing the scalar ladder does not already have.

What this CANNOT answer is whether a curriculum helps. These are frozen policies:
the screen locates where a channel starts to matter so that training runs are
aimed somewhere sensible. Any barrier claim needs training at that severity.

usage: analyze_actuator_screen.py RECEIPT_DIR [RECEIPT_DIR ...] [--out PATH]
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
import statistics
import sys

BASELINE_CELL = "act_off"
#: The standard preset at its envelope. Against the baseline cell this is an A/A
#: null: same six channels, same intensities, the four new terms inert. A gap
#: between them is a wiring defect, not physics.
AA_CELL = "phys_100"
#: Which channel each cell varies, and its rung. Mirrors PRESET_ACTUATOR.
CHANNELS = {
    "effort": ("act_effort_050", "act_effort_100", "act_effort_150"),
    "friction": ("act_friction_050", "act_friction_100", "act_friction_200", "act_friction_300"),
    "armature": ("act_armature_100", "act_armature_200"),
    "velocity": ("act_velocity_050", "act_velocity_100", "act_velocity_150",
                 "act_velocity_200"),
}
#: The arm a "is it live" check is made against: competent and not fragile.
REFERENCE_ARM = "fixed"

LIVE_PTS = 5.0        # a change smaller than this is inside single-cell noise
FLOOR = 0.05          # below this the cell is a floor, not a measurement
SEPARATION_PTS = 5.0  # spread across arms that counts as separating policies
REDUNDANT_RHO = 0.7   # above this, the channel ranks policies as the old ladder does

#: Each arm's success on the widest cell of the EXISTING scalar ladder, which is
#: what a new channel has to say something different from. Measured, seed 8600,
#: 512 episodes: receipts/analysis/lucid_channel_attribution_20260902.json.
EXISTING_LADDER = {
    "fixed": 0.8203, "lucid_ratchet_rg": 0.8418, "lucid_rg": 0.7949,
    "lucid_s4_rg": 0.5176, "off": 0.3340,
}


def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        out = [0] * len(v)
        for pos, i in enumerate(order):
            out[i] = pos + 1
        return out
    if len(x) < 3:
        return None
    rx, ry, n = rank(x), rank(y), len(x)
    return round(1 - 6 * sum((a - b) ** 2 for a, b in zip(rx, ry)) / (n * (n * n - 1)), 2)
BITE = 0.90           # where the reference arm first drops below this


def load(dirs: list[Path]) -> dict[tuple[str, str], float]:
    cells: dict[tuple[str, str], float] = {}
    for directory in dirs:
        for path in sorted(glob.glob(str(directory / "*.json"))):
            receipt = json.loads(Path(path).read_text())
            for run in (receipt.get("runs") or {}).values():
                if not run.get("complete"):
                    continue
                summary = run.get("summary") or {}
                if summary.get("success_rate") is None:
                    continue
                cells[(run["mode"], run["preset"])] = float(summary["success_rate"])
    return cells


def pts(a, b):
    return None if a is None or b is None else round(100.0 * (a - b), 2)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt_dirs", nargs="+", type=Path)
    ap.add_argument("--out", type=Path,
                    default=Path("receipts/analysis/lucid_actuator_screen_readout.json"))
    a = ap.parse_args(argv)
    cells = load(a.receipt_dirs)
    if not cells:
        print("no completed cells found", file=sys.stderr)
        return 1
    arms = sorted({m for m, _ in cells})
    missing_baseline = [m for m in arms if (m, BASELINE_CELL) not in cells]

    report: dict = {
        "kind": "lucid_actuator_screen_readout",
        "schema_version": 1,
        "receipt_dirs": [str(d) for d in a.receipt_dirs],
        "baseline_cell": BASELINE_CELL,
        "reference_arm": REFERENCE_ARM,
        "thresholds": {"live_pts": LIVE_PTS, "floor": FLOOR,
                       "separation_pts": SEPARATION_PTS, "bite_below": BITE},
        "arms": arms,
        "arms_without_a_baseline_cell": missing_baseline,
        "channels": {},
    }

    for channel, ladder in CHANNELS.items():
        rungs = [c for c in ladder if any((m, c) in cells for m in arms)]
        entry: dict = {"cells_found": rungs, "cells_missing": [c for c in ladder if c not in rungs],
                       "by_arm": {}}
        for arm in arms:
            base = cells.get((arm, BASELINE_CELL))
            entry["by_arm"][arm] = {
                "baseline": base,
                "rungs": {c: cells.get((arm, c)) for c in rungs},
                "delta_pts": {c: pts(cells.get((arm, c)), base) for c in rungs},
            }
        top = rungs[-1] if rungs else None
        ref = entry["by_arm"].get(REFERENCE_ARM, {})
        top_delta = ref.get("delta_pts", {}).get(top) if top else None

        # 1. live
        live = top_delta is not None and abs(top_delta) >= LIVE_PTS
        # 2. survivable
        top_values = [cells[(m, top)] for m in arms if (m, top) in cells] if top else []
        survivable = bool(top_values) and max(top_values) > FLOOR
        # 3. separating
        base_values = [cells[(m, BASELINE_CELL)] for m in arms if (m, BASELINE_CELL) in cells]
        spread_top = (max(top_values) - min(top_values)) * 100 if len(top_values) > 1 else None
        spread_base = (max(base_values) - min(base_values)) * 100 if len(base_values) > 1 else None
        separates = (spread_top is not None and spread_base is not None
                     and spread_top - spread_base >= SEPARATION_PTS)
        # where it starts to matter
        bite_rung = next((c for c in rungs
                          if (ref.get("rungs", {}).get(c) or 1.0) < BITE), None)

        # 4. does it rank the policies any differently from the ladder we have?
        shared = [m for m in arms if m in EXISTING_LADDER and (m, top) in cells] if top else []
        redundancy = None
        if len(shared) >= 3:
            loss = [-(entry["by_arm"][m]["delta_pts"][top] or 0.0) for m in shared]
            redundancy = spearman([-EXISTING_LADDER[m] for m in shared], loss)

        entry.update({
            "top_rung": top,
            "rank_correlation_with_the_existing_ladder": redundancy,
            "measures_a_new_axis": (None if redundancy is None
                                    else bool(abs(redundancy) < REDUNDANT_RHO)),
            "reference_delta_at_top_pts": top_delta,
            "is_live": live,
            "is_survivable": survivable,
            "arm_spread_at_baseline_pts": None if spread_base is None else round(spread_base, 2),
            "arm_spread_at_top_pts": None if spread_top is None else round(spread_top, 2),
            "separates_policies": separates,
            "first_rung_below_bite": bite_rung,
            "verdict": (
                "NOT LIVE: the channel did not move the reference policy; check that it "
                "was actually applied before concluding anything about physics" if not live else
                "FLOOR: the top rung is unsurvivable for every policy, so it is an "
                "unlearnable difficulty rather than a barrier candidate" if not survivable else
                "CANDIDATE: live, survivable" + (" and it separates policies" if separates
                                                 else " but it lowers every policy alike")
                + ("" if redundancy is None else
                   f", and it ranks them much as the existing ladder does (rho {redundancy:+.2f}), "
                   "so it restates general robustness rather than measuring a new axis"
                   if abs(redundancy) >= REDUNDANT_RHO else
                   f", ranking them differently from the existing ladder (rho {redundancy:+.2f})")),
        })
        report["channels"][channel] = entry

    ranked = sorted(
        (c for c, e in report["channels"].items() if e["is_live"] and e["is_survivable"]),
        key=lambda c: -(report["channels"][c]["arm_spread_at_top_pts"] or 0))
    # The A/A null, checked before any channel is interpreted.
    aa = {}
    for arm in arms:
        aa[arm] = pts(cells.get((arm, BASELINE_CELL)), cells.get((arm, AA_CELL)))
    gaps = [abs(v) for v in aa.values() if v is not None]
    report["aa_null"] = {
        "cells": [AA_CELL, BASELINE_CELL],
        "per_arm_delta_pts": aa,
        "max_abs_gap_pts": None if not gaps else round(max(gaps), 2),
        "verdict": (
            "NOT RUN: one of the two cells is missing" if not gaps else
            "PASS: adding four inert terms changed nothing beyond single-cell noise"
            if max(gaps) < LIVE_PTS else
            "FAIL: the actuator preset differs from the standard one with every actuator "
            "channel at its nominal. Fix the wiring before reading any channel below."),
    }
    report["candidates_most_promising_first"] = ranked
    report["not_verified"] = [
        "frozen policies only: this locates where a channel matters, it does not show that "
        "training at that severity fails or that staging helps",
        "one evaluation seed per cell; single-cell noise here is 2-3 points",
        "a channel that reads NOT LIVE may be unapplied rather than harmless; check the run's "
        "own dr_scale_report and its PhysX read-back before drawing a physical conclusion",
        "torque_saturation and energy_proxy are normalized by the live effort limit, the exact "
        "buffer the effort channel rewrites, so under act_effort_* they move by construction. "
        "They are a presence check there, never an outcome",
    ]
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=1) + "\n")

    aa = report["aa_null"]
    print(f"A/A null ({AA_CELL} vs {BASELINE_CELL}): {aa['verdict']}")
    if aa["max_abs_gap_pts"] is not None:
        print(f"  largest per-arm gap {aa['max_abs_gap_pts']} points")

    for channel, e in report["channels"].items():
        print(f"\n{channel}  (baseline {BASELINE_CELL}; deltas in success points)")
        header = f"{'arm':22s} {'base':>7} " + " ".join(f"{c.replace('act_' + channel + '_', ''):>8}" for c in e["cells_found"])
        print(header)
        for arm in arms:
            row = e["by_arm"][arm]
            base = "  -  " if row["baseline"] is None else f"{100 * row['baseline']:7.1f}"
            deltas = " ".join("     -  " if row["delta_pts"][c] is None else f"{row['delta_pts'][c]:+8.1f}"
                              for c in e["cells_found"])
            print(f"{arm:22s} {base} {deltas}")
        print(f"  -> {e['verdict']}")
        if e.get("rank_correlation_with_the_existing_ladder") is not None:
            print(f"     rank correlation with the existing scalar ladder: "
                  f"{e['rank_correlation_with_the_existing_ladder']:+.2f}"
                  f"  (a new axis needs |rho| < {REDUNDANT_RHO})")
        if e["first_rung_below_bite"]:
            print(f"     reference arm first falls below {BITE:.2f} at {e['first_rung_below_bite']}")
    print(f"\ncandidates, most promising first: {ranked or 'none'}")
    print(f"receipt -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
