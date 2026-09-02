#!/usr/bin/env python3
"""Pair terminal training return against held-out frontier robustness. Read-only.

The claim under test is that training return is not a weak curriculum monitor
but an *inverted* one. The mechanism is not subtle: a controller that lowers
difficulty makes its own environments easier, which raises return, which the
monitor reports as progress. What was missing was enough scored pairs to show
it, and the arm that would show it most sharply -- the collapse with the
campaign's highest return -- was the one arm with no robustness score.

Return is the mean of the last ``--window`` iterations of ``Mean rewards`` in
the training log, matching how the exposure preregistration recorded it.

Frontier success AUC is the frozen phys_125..200 trapezoid. Cells are taken
from evaluation receipts, and an arm whose cells come from more than one
receipt is REPORTED AS CONTESTED rather than averaged: receipts predating
``dr_scaling.clamp_physical`` hold lambda>1 cells the preregistration excludes
at phys_125 and above.

usage: return_inversion.py [--out PATH] [--window 500]
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
import re
import statistics
from typing import Any

MANIFESTS = Path("/home/linjiw/lucid-sonic/manifests")
OUTPUTS = Path("/home/linjiw/lucid-sonic/outputs")

FRONTIER_CELLS = ("phys_125", "phys_150", "phys_175", "phys_200")
FRONTIER_WEIGHTS = (1.0 / 6.0, 1.0 / 3.0, 1.0 / 3.0, 1.0 / 6.0)

ITERATION = re.compile(r"Learning iteration (\d+)")
REWARD = re.compile(r"Mean rewards:\s*(-?[0-9.]+)")

#: Where each arm's training log lives, and its final applied lambda. Only arms
#: whose controller could move lambda are informative about inversion; fixed and
#: off are included as reference points with a constant lambda.
ARMS: dict[str, dict[str, Any]] = {
    "lucid_rg@s8601": {
        "log": "curriculum_comparison_ne1024_20260829_000249_s8601_lucid_rg.log",
        "seed": 8601, "mode": "lucid_rg", "final_lambda": 0.062, "evacuated": True,
    },
    "lucid_s4_rg@s8600": {
        "log": "curriculum_comparison_ne1024_20260829_000249_s8600_lucid_s4_rg.log",
        "seed": 8600, "mode": "lucid_s4_rg", "final_lambda": 0.012, "evacuated": True,
    },
    "lucid_rg@s8600": {
        "log": "curriculum_comparison_ne1024_20260829_000249_s8600_lucid_rg.log",
        "seed": 8600, "mode": "lucid_rg", "final_lambda": 1.0, "evacuated": False,
    },
    "lucid_s4_rg@s8601": {
        "log": "curriculum_comparison_ne1024_20260829_000249_s8601_lucid_s4_rg.log",
        "seed": 8601, "mode": "lucid_s4_rg", "final_lambda": 1.0, "evacuated": False,
    },
    "lucid_rg@s8602": {
        "log": "curriculum_comparison_ne1024_20260829_000249_s8602_lucid_rg.log",
        "seed": 8602, "mode": "lucid_rg", "final_lambda": 1.0, "evacuated": False,
    },
    "lucid_s4_rg@s8602": {
        "log": "curriculum_comparison_ne1024_20260829_000249_s8602_lucid_s4_rg.log",
        "seed": 8602, "mode": "lucid_s4_rg", "final_lambda": 1.0, "evacuated": False,
    },
    "lucid_ratchet_rg@s8601": {
        "log": "curriculum_comparison_ne1024_20260831_144022_s8601_lucid_ratchet_rg.log",
        "seed": 8601, "mode": "lucid_ratchet_rg", "final_lambda": 1.0, "evacuated": False,
    },
    "lucid_ratchet_rg@s8600": {
        "log": "curriculum_comparison_ne1024_20260831_231901_s8600_lucid_ratchet_rg.log",
        "seed": 8600, "mode": "lucid_ratchet_rg", "final_lambda": 1.0, "evacuated": False,
    },
    "lucid_ratchet_rg@s8602": {
        "log": "curriculum_comparison_ne1024_20260901_100208_s8602_lucid_ratchet_rg.log",
        "seed": 8602, "mode": "lucid_ratchet_rg", "final_lambda": 1.0, "evacuated": False,
    },
    "fixed@s8600": {
        "log": "curriculum_comparison_ne1024_20260829_000249_s8600_fixed.log",
        "seed": 8600, "mode": "fixed", "final_lambda": 1.0, "evacuated": False,
    },
    "fixed@s8601": {
        "log": "curriculum_comparison_ne1024_20260829_000249_s8601_fixed.log",
        "seed": 8601, "mode": "fixed", "final_lambda": 1.0, "evacuated": False,
    },
    "fixed@s8602": {
        "log": "curriculum_comparison_ne1024_20260901_044118_s8602_fixed.log",
        "seed": 8602, "mode": "fixed", "final_lambda": 1.0, "evacuated": False,
    },
}


def terminal_return(path: Path, window: int) -> float | None:
    rows: dict[int, float] = {}
    current: int | None = None
    if not path.exists():
        return None
    for line in path.open(errors="ignore"):
        found = ITERATION.search(line)
        if found:
            current = int(found.group(1))
            continue
        if current is None:
            continue
        found = REWARD.search(line)
        if found:
            rows[current] = float(found.group(1))
    if not rows:
        return None
    ordered = [rows[k] for k in sorted(rows)]
    return statistics.fmean(ordered[-window:])


#: Receipts written before ``dr_scaling.clamp_physical`` existed. The exposure
#: preregistration excludes their lambda>1 cells at phys_125 and above, so they
#: are skipped for exactly those cells and kept for the rest.
PRE_CLAMP_RECEIPTS = {"curriculum_robustness_ne512_20260829_214540.json"}


def receipt_paths() -> list[Path]:
    """Every evaluation receipt, including the H_R2 ladders.

    The confirmation's own ladders live under its manifest tree rather than the
    flat manifests directory, and without them the ratchet and fixed arms have
    no frontier score at all.
    """
    paths = sorted(MANIFESTS.glob("curriculum_robustness_ne512_*.json"))
    paths += sorted(MANIFESTS.glob("ratchet_confirmation_*/evaluation/*/*.json"))
    paths += sorted(MANIFESTS.glob("ratchet_screen_*/*/*.json"))
    return paths


def frontier_scores() -> tuple[dict, dict]:
    scores: dict[tuple[int, str], dict[str, float]] = {}
    provenance: dict[tuple[int, str, str], list[str]] = {}
    for path in receipt_paths():
        try:
            receipt = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        runs = receipt.get("runs", {})
        rows = runs.values() if isinstance(runs, dict) else runs
        for row in rows:
            if row.get("runtime", {}).get("exit_code") != 0:
                continue
            key = (int(row["checkpoint_seed"]), row["mode"])
            preset = row["preset"]
            if path.name in PRE_CLAMP_RECEIPTS and preset in FRONTIER_CELLS:
                # Preregistered supersession, not a judgement call made here.
                continue
            value = float(row["summary"]["success_rate"])
            provenance.setdefault((*key, preset), []).append((path.name, value))
            scores.setdefault(key, {})[preset] = value
    return scores, provenance


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", type=int, default=500)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    scores, provenance = frontier_scores()
    pairs = []
    for label, spec in ARMS.items():
        key = (spec["seed"], spec["mode"])
        cells = scores.get(key, {})
        # A cell supplied by two receipts is only a problem if they DISAGREE.
        # P2 established that the evaluator is bit-deterministic on this panel,
        # so identical values across receipts are replication, not contamination;
        # differing values mean two instruments and must not be averaged.
        contested = []
        for preset in FRONTIER_CELLS:
            sources = provenance.get((*key, preset), [])
            values = {round(v, 9) for _, v in sources}
            if len(values) > 1:
                contested.append(
                    {"cell": preset, "values": sorted(values),
                     "receipts": sorted({n for n, _ in sources})}
                )
        auc = None
        if all(c in cells for c in FRONTIER_CELLS) and not contested:
            auc = sum(cells[c] * w for c, w in zip(FRONTIER_CELLS, FRONTIER_WEIGHTS))
        pairs.append(
            {
                "arm": label,
                "seed": spec["seed"],
                "mode": spec["mode"],
                "final_lambda": spec["final_lambda"],
                "evacuated": spec["evacuated"],
                "terminal_return": (
                    None
                    if (r := terminal_return(OUTPUTS / spec["log"], args.window)) is None
                    else round(r, 4)
                ),
                "frontier_success_auc": None if auc is None else round(auc, 6),
                "contested_cells": contested or None,
                "sources": sorted(
                    {
                        name
                        for preset in FRONTIER_CELLS
                        for name, _ in provenance.get((*key, preset), [])
                    }
                ),
            }
        )

    scored = [p for p in pairs if p["terminal_return"] is not None and p["frontier_success_auc"]]
    report: dict[str, Any] = {
        "kind": "lucid_return_inversion",
        "schema_version": 1,
        "return_definition": f"mean of the last {args.window} iterations of 'Mean rewards'",
        "endpoint": "frontier success AUC, frozen phys_125..200 trapezoid",
        "pairs": pairs,
        "n_scored_pairs": len(scored),
    }

    if len(scored) >= 3:
        xs = [p["terminal_return"] for p in scored]
        ys = [p["frontier_success_auc"] for p in scored]
        mx, my = statistics.fmean(xs), statistics.fmean(ys)
        num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
        dx = sum((a - mx) ** 2 for a in xs) ** 0.5
        dy = sum((b - my) ** 2 for b in ys) ** 0.5
        def spearman(xs, ys):
            def rank(vals):
                order = sorted(range(len(vals)), key=lambda i: vals[i])
                out = [0.0] * len(vals)
                i = 0
                while i < len(order):
                    j = i
                    while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                        j += 1
                    shared = (i + j) / 2.0 + 1.0
                    for k in range(i, j + 1):
                        out[order[k]] = shared
                    i = j + 1
                return out
            rx, ry = rank(xs), rank(ys)
            mx, my = statistics.fmean(rx), statistics.fmean(ry)
            num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
            dx = sum((a - mx) ** 2 for a in rx) ** 0.5
            dy = sum((b - my) ** 2 for b in ry) ** 0.5
            return None if dx == 0 or dy == 0 else round(num / (dx * dy), 4)

        # Rank correlation is the better summary here: one arm (lucid_s4_rg@s8602)
        # is brittle to the friction clamp rather than to evacuation, and its low
        # frontier score at ordinary return drags a linear fit without changing
        # the ordering the claim is actually about.
        report["spearman_return_vs_frontier"] = spearman(
            [p["terminal_return"] for p in scored],
            [p["frontier_success_auc"] for p in scored],
        )
        report["highest_return_arms"] = [
            p["arm"]
            for p in sorted(scored, key=lambda x: -x["terminal_return"])[:2]
        ]
        report["highest_return_arms_all_evacuated"] = all(
            p["evacuated"]
            for p in sorted(scored, key=lambda x: -x["terminal_return"])[:2]
        )
        report["pearson_return_vs_frontier"] = (
            None if dx == 0 or dy == 0 else round(num / (dx * dy), 4)
        )
        controllers = [p for p in scored if p["mode"] != "fixed"]
        if len(controllers) >= 3:
            xs = [p["terminal_return"] for p in controllers]
            ys = [p["frontier_success_auc"] for p in controllers]
            mx, my = statistics.fmean(xs), statistics.fmean(ys)
            num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
            dx = sum((a - mx) ** 2 for a in xs) ** 0.5
            dy = sum((b - my) ** 2 for b in ys) ** 0.5
            report["pearson_controllers_only"] = (
                None if dx == 0 or dy == 0 else round(num / (dx * dy), 4)
            )
        evac = [p for p in scored if p["evacuated"]]
        held = [p for p in scored if not p["evacuated"]]
        if evac and held:
            report["evacuated_vs_held"] = {
                "evacuated_mean_return": round(
                    statistics.fmean(p["terminal_return"] for p in evac), 4
                ),
                "held_mean_return": round(
                    statistics.fmean(p["terminal_return"] for p in held), 4
                ),
                "evacuated_mean_frontier": round(
                    statistics.fmean(p["frontier_success_auc"] for p in evac), 6
                ),
                "held_mean_frontier": round(
                    statistics.fmean(p["frontier_success_auc"] for p in held), 6
                ),
            }

    text = json.dumps(report, indent=2)
    if args.out:
        args.out.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
