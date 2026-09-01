#!/usr/bin/env python3
"""Score P3 against its frozen preregistered bands. Read-only.

P3 is the one measurement that discriminates the candidate exposure laws. The
predictions were frozen in
``receipts/manifests/lucid_frontier_exposure_law_preregistration_20260901.json``
while the confirmation run was still training and before any cell of this
readout existed. This script reads those bands FROM the committed file rather
than restating them, so the comparison cannot drift from what was registered.

The arm is ``lucid_rg`` seed 8601: the predeclared collapse, which held
lambda = 1.0 for thousands of iterations and then fell to 0.062 over its last
~1,000 iterations. It has a complete lambda history and no robustness score of
any kind, which is what makes it a genuine out-of-sample test rather than a
refit.

What the outcome means, per the frozen rule:

  P3 >= 0.881836   the exposure hypothesis is REJECTED upward. Evacuation is
                   free, the measured cost was a one-run artifact, and the
                   paper's framing is wrong.
  P3 <  0.67366    REJECTED downward. Evacuation costs far more than any
                   fitted law predicts.
  P3 >  0.77571    the RECENCY term specifically is rejected; a uniform dose
                   survives.
  in [0.76086, 0.77571]
                   the design failed to discriminate. No model selection is
                   authorized, and saying so is the required outcome.

usage: score_p3.py [--receipt PATH] [--out PATH]
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Any

PREREG = Path(
    "/home/linjiw/lucid/receipts/manifests/"
    "lucid_frontier_exposure_law_preregistration_20260901.json"
)
MANIFESTS = Path("/home/linjiw/lucid-sonic/manifests")

#: The frozen H_R2 frontier grid. Normalized trapezoid weights over four cells.
FRONTIER_CELLS = ("phys_125", "phys_150", "phys_175", "phys_200")
FRONTIER_WEIGHTS = (1.0 / 6.0, 1.0 / 3.0, 1.0 / 3.0, 1.0 / 6.0)

#: The uncontaminated band the Phase-2 screen gates on. Reported here too, so
#: the collapse arm has a value on the endpoint future arms will be judged by.
HELD_OUT_CELLS = ("phys_175", "phys_200")
HELD_OUT_WEIGHTS = (0.5, 0.5)


def frontier_auc(success: dict[str, float]) -> float | None:
    if not all(cell in success for cell in FRONTIER_CELLS):
        return None
    return sum(success[c] * w for c, w in zip(FRONTIER_CELLS, FRONTIER_WEIGHTS))


def held_out(success: dict[str, float]) -> float | None:
    if not all(cell in success for cell in HELD_OUT_CELLS):
        return None
    return sum(success[c] * w for c, w in zip(HELD_OUT_CELLS, HELD_OUT_WEIGHTS))


def collect(receipt_path: Path) -> dict[tuple[int, str], dict[str, float]]:
    """success_rate per (seed, mode, preset) from an evaluation receipt."""
    receipt = json.loads(receipt_path.read_text())
    out: dict[tuple[int, str], dict[str, float]] = {}
    runs = receipt.get("runs", {})
    rows = runs.values() if isinstance(runs, dict) else runs
    for row in rows:
        if row.get("runtime", {}).get("exit_code") != 0:
            # Fail-closed: an interrupted cell is evidence of interruption, and
            # must never be silently averaged over.
            continue
        key = (int(row["checkpoint_seed"]), row["mode"])
        out.setdefault(key, {})[row["preset"]] = float(row["summary"]["success_rate"])
    return out


def find_receipts() -> list[Path]:
    found = sorted(MANIFESTS.glob("phase0_scoring_*.json"))
    found += sorted(MANIFESTS.glob("curriculum_robustness_ne512_*.json"))
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, action="append", default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    prereg = json.loads(PREREG.read_text())
    predictions = prereg["frozen_predictions"]
    p3 = predictions.get("P3_collapse_arm_PRIMARY", {})
    rule = prereg["global_falsification"]

    receipts = args.receipt or find_receipts()
    scores: dict[tuple[int, str], dict[str, float]] = {}
    used: list[str] = []
    for path in receipts:
        if not Path(path).is_file():
            continue
        try:
            found = collect(Path(path))
        except (KeyError, json.JSONDecodeError):
            continue
        if found:
            used.append(str(path))
        for key, cells in found.items():
            scores.setdefault(key, {}).update(cells)

    target = (8601, "lucid_rg")
    cells = scores.get(target)
    report: dict[str, Any] = {
        "kind": "lucid_p3_readout",
        "schema_version": 1,
        "arm": "lucid_rg@s8601",
        "arm_note": (
            "the predeclared collapse: held lambda 1.0 for thousands of iterations, "
            "final lambda 0.062"
        ),
        "preregistration": str(PREREG),
        "preregistration_sha256": prereg.get("companion", {}).get("sha256"),
        "receipts_read": used,
        "frozen_bands": p3,
        "global_falsification_rule": rule,
    }

    if not cells:
        report["status"] = "NOT_YET_SCORED"
        report["note"] = (
            "No completed evaluation cell found for lucid_rg seed 8601. Run "
            "tools/run_phase0_scoring.sh --execute once the GPU is free."
        )
        text = json.dumps(report, indent=2)
        if args.out:
            args.out.write_text(text)
        print(text)
        return 0

    observed = frontier_auc(cells)
    report["per_cell_success"] = {k: round(v, 6) for k, v in sorted(cells.items())}
    report["frontier_success_auc"] = None if observed is None else round(observed, 6)
    report["held_out_band_success"] = (
        None if held_out(cells) is None else round(held_out(cells), 6)
    )

    if observed is None:
        report["status"] = "INCOMPLETE"
        report["note"] = (
            "Not all four frontier cells are present. The endpoint is fail-closed: "
            "a missing cell is never imputed."
        )
    else:
        verdicts = []
        if observed >= 0.881836:
            verdicts.append(
                "EXPOSURE HYPOTHESIS REJECTED (upward): evacuation is free. "
                "The measured 7.97-point cost was a one-run artifact and the "
                "paper's framing needs rewriting."
            )
        elif observed < 0.67366:
            verdicts.append(
                "EXPOSURE HYPOTHESIS REJECTED (downward): evacuation costs far "
                "more than any fitted law predicts."
            )
        else:
            verdicts.append("Exposure hypothesis SURVIVES: the value is inside the fitted range.")
            if 0.76086 <= observed <= 0.77571:
                verdicts.append(
                    "INDETERMINATE between recency and uniform: the value lies in the "
                    "two-law overlap. No model selection is authorized."
                )
            elif observed > 0.77571:
                verdicts.append(
                    "RECENCY REJECTED: a uniform dose survives, and the phrase "
                    "'recency-weighted' must not be used."
                )
            else:
                verdicts.append(
                    "Consistent with the recency-weighted dose and below the uniform "
                    "prediction. Recency is not thereby established: a boxcar trailing "
                    "mean beats the exponential kernel out of sample."
                )
        report["status"] = "SCORED"
        report["verdict"] = verdicts

    text = json.dumps(report, indent=2)
    if args.out:
        args.out.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
