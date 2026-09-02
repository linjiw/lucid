#!/usr/bin/env python3
"""Do the arm orderings survive a change of motion? Read-only.

Every robustness number this programme has produced comes from fresh physics
draws of ONE clip -- the clip every arm trained on. That is
memorized-motion-under-new-physics. This scores the same frozen policies on
three sibling clips none of them trained on.

What this can support
---------------------
One descriptive question: does the ORDERING of arms by robustness survive a
change of motion? If the ordering is stable, the differences between arms are
not purely artifacts of how well each memorized one clip. That is a real, if
modest, strengthening of every ordering claim in the programme.

What this cannot support
------------------------
It is NOT motion generalization in the general sense, and this tool will not
print a number that could be quoted as such.

* All three clips are walking motions drawn from the same adaptation partition
  as the training clip. They are near neighbours, not a held-out distribution.
* No arm was ever trained on these clips, and no baseline was trained on them
  either, so absolute success here cannot separate "the policy generalizes"
  from "these clips are easy" or "these clips resemble the training clip".
* Panels are k128; the main ladder is k512. Per-cell standard error is roughly
  twice as large. The two must never be pooled, and this tool refuses to
  combine them.

Ordering is compared with Spearman rank correlation against the trained-clip
ordering at the same cell, over the arms scored on both.

usage: analyze_heldout_motion.py [--out PATH] [--freeze]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
from typing import Any

MANIFESTS = Path("/home/linjiw/lucid-sonic/manifests")
CELLS = ("phys_100", "phys_150", "phys_200")

#: The trained clip's k512 reference, taken from receipts already in the ledger.
#: Used ONLY to rank arms, never pooled with the k128 numbers.
TRAINED_CLIP = "walk_hands_on_back_loop_002__A066_M"


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(xs) != len(ys):
        return None

    def rank(values: list[float]) -> list[float]:
        order = sorted(range(len(values)), key=lambda i: values[i])
        ranks = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            shared = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[order[k]] = shared
            i = j + 1
        return ranks

    rx, ry = rank(xs), rank(ys)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return None if dx == 0 or dy == 0 else num / (dx * dy)


def read(paths: list[Path]) -> dict:
    """success_rate by (clip, mode, preset), keeping the episode count."""
    out: dict = {}
    for path in paths:
        try:
            receipt = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        suite = receipt.get("protocol", {}).get("suite", {})
        panel = suite.get("replicate_panel", {})
        clip = panel.get("motion_key") or suite.get("motion_keys_sha256", "?")[:12]
        count = suite.get("motion_count")
        runs = receipt.get("runs", {})
        rows = runs.values() if isinstance(runs, dict) else runs
        for row in rows:
            if row.get("runtime", {}).get("exit_code") != 0 or not row.get("summary"):
                continue
            out.setdefault((clip, count), {}).setdefault(row["mode"], {})[row["preset"]] = {
                "success_rate": float(row["summary"]["success_rate"]),
                "progress_rate": float(row["summary"]["progress_rate"]),
            }
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path,
                        default=Path("/home/linjiw/lucid/receipts/analysis/"
                                     "lucid_heldout_motion_20260901.json"))
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args(argv)

    held = read(sorted(MANIFESTS.glob("curriculum_robustness_ne128_2026090*.json")))
    trained = read(
        sorted(MANIFESTS.glob("curriculum_robustness_ne512_*.json"))
        + sorted(MANIFESTS.glob("ratchet_confirmation_*/evaluation/*/*.json"))
    )

    # The trained-clip reference is whichever k512 panel holds the training clip.
    reference: dict[str, dict[str, float]] = {}
    for (clip, count), modes in trained.items():
        if count != 512:
            continue
        for mode, cells in modes.items():
            for preset, values in cells.items():
                reference.setdefault(mode, {})[preset] = values["success_rate"]

    clips: dict[str, Any] = {}
    for (clip, count), modes in sorted(held.items()):
        per_cell: dict[str, Any] = {}
        for preset in CELLS:
            scored = {m: c[preset]["success_rate"] for m, c in modes.items() if preset in c}
            shared = sorted(m for m in scored if preset in reference.get(m, {}))
            rho = spearman(
                [scored[m] for m in shared],
                [reference[m][preset] for m in shared],
            ) if len(shared) >= 3 else None
            per_cell[preset] = {
                "success_by_arm": {m: round(v, 6) for m, v in sorted(scored.items())},
                "arms_ranked_best_first": [
                    m for m, _ in sorted(scored.items(), key=lambda kv: -kv[1])
                ],
                "spearman_vs_trained_clip": None if rho is None else round(rho, 4),
                "arms_in_both": shared,
            }
        clips[clip] = {"episodes_per_cell": count, "cells": per_cell}

    rhos = [
        c["spearman_vs_trained_clip"]
        for clip in clips.values() for c in clip["cells"].values()
        if c["spearman_vs_trained_clip"] is not None
    ]

    report = {
        "kind": "lucid_heldout_motion_readout",
        "schema_version": 1,
        "created_at": "2026-09-01T21:20:00-04:00",
        "question": "Does the ordering of arms by robustness survive a change of motion?",
        "trained_clip": TRAINED_CLIP,
        "clips": clips,
        "ordering_stability": {
            "spearman_values": rhos,
            "n": len(rhos),
            "mean": None if not rhos else round(statistics.fmean(rhos), 4),
            "min": None if not rhos else min(rhos),
            "interpretation": (
                "Rank correlation of the arm ordering on an untrained clip against the "
                "ordering on the trained clip, at the same cell. High values mean the "
                "differences between arms are not purely an artifact of how well each "
                "memorized one clip."
            ),
        },
        "claim_boundaries": [
            "NOT motion generalization in the general sense. All three clips are walking "
            "motions from the same adaptation partition as the training clip.",
            "No arm trained on these clips and no baseline was trained on them, so absolute "
            "success here cannot separate 'the policy generalizes' from 'these clips are "
            "easy' or 'these clips resemble the training clip'.",
            "k128 panels; the main ladder is k512. Per-cell standard error is about twice "
            "as large and the two are never pooled.",
            "Authorizes no superiority claim for any training procedure. H_R2 remains a "
            "stability and noninferiority result for the monotone ratchet.",
            "An ordering that survives is evidence about ORDERINGS, not about absolute "
            "robustness on unseen motions.",
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists():
        os.chmod(args.out, 0o644)
    args.out.write_text(json.dumps(report, indent=2))
    digest = hashlib.sha256(args.out.read_bytes()).hexdigest()
    if args.freeze:
        os.chmod(args.out, 0o444)
    print(json.dumps(report, indent=2))
    print(f"\n# receipt: {args.out}\n# sha256: {digest}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
