#!/usr/bin/env python3
"""Read out the single-channel attribution sweep.

Read-only. For every scored final, tabulates success on the eleven
single-channel cells (one term widened, the other four at lambda = 1, latency
pinned to zero) next to the scalar ladder's phys_100/125/150/200 cells from the
existing receipts, so the question "which physics broke the policy" gets a
number per channel instead of a guess.

Two derived quantities per arm:

  drop(channel, level) = success(phys_100) - success(ch_<channel>_<level>)
        the cost of widening that one channel, in success points.
  anisotropy = max over channels of drop at level 2.0 minus the min over
        channels of drop at 2.0. Zero means every channel hurts alike and a
        scalar lambda is the right actuator; large means the failure surface
        has a preferred direction and a per-channel box is worth building.

usage: analyze_channel_sweep.py [--sweep-dir DIR] [--out readout.json]
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Any

LUCID_ROOT = Path("/home/linjiw/lucid-sonic")
RECEIPT_ROOTS = [LUCID_ROOT / "manifests", Path("/home/linjiw/lucid/receipts")]
CHANNEL_CELLS = [
    "ch_fric_125", "ch_fric_150", "ch_fric_200",
    "ch_mass_200", "ch_mass_300",
    "ch_com_200", "ch_com_300",
    "ch_joint_200", "ch_joint_300",
    "ch_push_200", "ch_push_300",
]
SCALAR_CELLS = ["phys_100", "phys_125", "phys_150", "phys_175", "phys_200"]
METRICS = ["success_rate", "foot_slip_per_step_m", "torque_saturation", "energy_proxy", "undesired_contact_rate", "mpjpe_g"]


def collect(roots: list[Path], presets: set[str]) -> dict[tuple[str, int, str], dict[str, Any]]:
    cells: dict[tuple[str, int, str], dict[str, Any]] = {}
    for root in roots:
        for path in glob.glob(str(root / "**" / "*.json"), recursive=True):
            try:
                receipt = json.loads(Path(path).read_text())
            except (OSError, ValueError):
                continue
            if receipt.get("kind") != "lucid_frozen_checkpoint_robustness_evaluation":
                continue
            for run in receipt.get("runs", {}).values():
                if not run.get("complete") or run.get("preset") not in presets:
                    continue
                summary = run.get("summary") or {}
                if summary.get("success_rate") is None:
                    continue
                key = (run["mode"], int(run["checkpoint_seed"]), run["preset"])
                cells[key] = {
                    **{m: summary.get(m) for m in METRICS},
                    "channel_dr_scales": summary.get("channel_dr_scales"),
                    "dr_ranges": summary.get("dr_ranges"),
                    "receipt": path,
                    "created_at": receipt.get("created_at"),
                }
    return cells


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep-dir", type=Path, default=None, help="manifests dir of one sweep; default: newest channel_sweep_*")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    sweep_dir = args.sweep_dir
    if sweep_dir is None:
        candidates = sorted(glob.glob(str(LUCID_ROOT / "manifests" / "channel_sweep_*")))
        if not candidates:
            raise SystemExit("no channel_sweep_* manifests directory found")
        sweep_dir = Path(candidates[-1])
    channel = collect([sweep_dir], set(CHANNEL_CELLS))
    scalar = collect(RECEIPT_ROOTS, set(SCALAR_CELLS))
    arms = sorted({(m, s) for (m, s, _) in channel})
    table: list[dict[str, Any]] = []
    for mode, seed in arms:
        row: dict[str, Any] = {"arm": f"{mode}@s{seed}", "cells": {}, "scalar": {}}
        base = scalar.get((mode, seed, "phys_100"), {}).get("success_rate")
        for preset in SCALAR_CELLS:
            cell = scalar.get((mode, seed, preset))
            if cell:
                row["scalar"][preset] = {m: cell.get(m) for m in METRICS}
        for preset in CHANNEL_CELLS:
            cell = channel.get((mode, seed, preset))
            if not cell:
                continue
            entry = {m: cell.get(m) for m in METRICS}
            entry["drop_vs_phys_100"] = None if base is None else round(base - cell["success_rate"], 4)
            # Verify the marginal really is a marginal: exactly one term differs
            # from the lambda = 1 envelope in the realized ranges.
            entry["channel_dr_scales"] = cell.get("channel_dr_scales")
            row["cells"][preset] = entry
        drops_200 = {
            p.split("_")[1]: row["cells"][p]["drop_vs_phys_100"]
            for p in ("ch_fric_200", "ch_mass_200", "ch_com_200", "ch_joint_200", "ch_push_200")
            if p in row["cells"] and row["cells"][p]["drop_vs_phys_100"] is not None
        }
        if drops_200:
            worst = max(drops_200, key=drops_200.get)
            row["anisotropy_at_2x"] = {
                "drops": drops_200,
                "worst_channel": worst,
                "spread": round(max(drops_200.values()) - min(drops_200.values()), 4),
                "worst_share_of_total": round(drops_200[worst] / sum(drops_200.values()), 4) if sum(drops_200.values()) > 0 else None,
            }
        table.append(row)

    report = {
        "kind": "lucid_channel_attribution_readout",
        "schema_version": 1,
        "sweep_dir": str(sweep_dir),
        "cells_found": len(channel),
        "arms": table,
        "caveats": [
            "single seed (8600); paired within-seed noise on a single 512-episode cell is ~2-3 points",
            "channel cells widen one term from the lambda=1 envelope with the others at lambda=1; "
            "the friction floor clamps at 0.05 so ch_fric_150 and ch_fric_200 differ only in the high bound",
            "the scalar phys_* references come from earlier receipts scored with the pinned evaluator; "
            "the channel cells use the current evaluator, whose scalar path is unchanged",
        ],
    }
    text = json.dumps(report, indent=2)
    if args.out:
        args.out.write_text(text)

    levels = ["125", "150", "200", "300"]
    chans = ["fric", "mass", "com", "joint", "push"]
    print(f"sweep {sweep_dir.name}: {len(channel)} channel cells, {len(arms)} arms")
    hdr = f"{'arm':24s} {'p100':>6s} {'p125':>6s} {'p150':>6s} {'p200':>6s} |"
    for c in chans:
        for lv in levels:
            if f"ch_{c}_{lv}" in CHANNEL_CELLS:
                hdr += f" {c[:4]}{lv}"[:8].rjust(9)
    print(hdr)
    for row in table:
        line = f"{row['arm']:24s}"
        for p in ("phys_100", "phys_125", "phys_150", "phys_200"):
            v = row["scalar"].get(p, {}).get("success_rate")
            line += f" {v:6.3f}" if v is not None else f" {'-':>6s}"
        line += " |"
        for c in chans:
            for lv in levels:
                p = f"ch_{c}_{lv}"
                if p not in CHANNEL_CELLS:
                    continue
                v = row["cells"].get(p, {}).get("success_rate")
                line += f" {v:8.3f}" if v is not None else f" {'-':>8s}"
        print(line)
        if "anisotropy_at_2x" in row:
            a = row["anisotropy_at_2x"]
            print(f"{'':24s} drops@2x " + "  ".join(f"{k}={v:+.3f}" for k, v in a["drops"].items()) + f"  worst={a['worst_channel']} spread={a['spread']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
