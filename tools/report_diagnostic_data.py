"""Write complete portable scalar tables and a concise development readout."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from analyze_diagnostic_data import analyze, auc, read_data


def csv_write(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    result = analyze(args.data)
    (args.output / "diagnostic.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    csv_write(args.output / "all_condition_scalars.csv", result["rows"])
    csv_write(args.output / "threshold_sensitivity.csv", result["sensitivity"])
    gates, constituents = [], []
    for row in result["retention"]:
        gates.append({k: v for k, v in row.items() if k != "constituents"})
        for cell in row["constituents"]:
            constituents.append(
                {"seed": row["seed"], "arm": row["arm"], "iteration": row["iteration"], **cell}
            )
    csv_write(args.output / "retention_summary.csv", gates)
    csv_write(args.output / "retention_constituents.csv", constituents)
    historical = read_data(args.data, "historical.json")["rows"]
    census = [
        {
            "arm": r["arm"],
            "mode": r["mode"],
            "seed": r["seed"],
            "origin": r["origin"],
            "iteration": r["checkpoint_iteration"],
            "checkpoint_sha256": r["cells"]["phys_125"]["checkpoint_sha256"],
            "evaluation_seed": r["cells"]["phys_125"]["evaluation_seed"],
            "terminal_return": r["terminal_return"],
            "final_lambda": (
                r["controller_state"]["controller"]["lambda_value"]
                if r["controller_state"]
                else r["final_lambda"]
            ),
            "frontier_success_auc_points": 100 * auc(r["cells"], "success_rate"),
        }
        for r in historical
    ]
    csv_write(args.output / "historical_census.csv", census)
    text = [
        "# Existing-data diagnostic readout",
        "",
        "Both continuation seeds share one trained origin and motion. Each cell contains 512 repeated-motion trials; rollout pairing is unverified. All values below are recomputed from the packaged episode measurements.",
        "",
        "| Seed | Arm | Iteration | D (%) | L (pp) | Hard Q (%) | Pass |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in gates:
        text.append(
            f"| {r['seed']} | {r['arm']} | {r['iteration']} | {r['D_pct']:.4f} | {r['L_pp']:.4f} | {r['hard_qualification_pct']:.4f} | {r['passes']} |"
        )
    text += [
        "",
        "No sampled R0 or R2 continuation checkpoint is feasible. R1's exploratory best-on-panel checkpoints are iteration 500 (seed 8600) and 1500 (seed 8601). The predeclared 2000-iteration endpoints remain primary; these retrospective choices are not held-out performance.",
        "",
        "All underlying global/local errors and completion rates, including failed episodes, are in retention_constituents.csv and all_condition_scalars.csv. The complete threshold grid for every checkpoint is in threshold_sensitivity.csv. Historical policy identities, checkpoint hashes and evaluation seeds are in historical_census.csv.",
    ]
    (args.output / "readout.md").write_text("\n".join(text) + "\n")
    print(
        f"Wrote {len(gates)} gate rows, {len(constituents)} protected cells and {len(result['sensitivity'])} sensitivity rows"
    )


if __name__ == "__main__":
    main()
