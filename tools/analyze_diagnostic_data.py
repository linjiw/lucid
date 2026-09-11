"""Recompute retention, threshold sensitivity and historical contrasts portably."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
from statistics import fmean, stdev

from scipy.stats import spearmanr, t

PROTECTED = ("phys_000", "phys_100")
HARD = ("ch_push_350", "ch_push_fric_350_150")
CONDITIONS = (*PROTECTED, "ch_push_300", *HARD)
ITERATIONS = (250, 500, 1000, 1500, 2000)
GLOBAL_GRID = (400, 500, 600, 700, 800)
LOCAL_GRID = (40, 45, 50, 55, 60)


def read_data(data: Path, name: str):
    path = data / name
    manifest = json.loads((data / "manifest.json").read_text())
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["files"][name]:
        raise ValueError(f"Package hash mismatch: {name}")
    raw = gzip.decompress(path.read_bytes()) if name.endswith(".gz") else path.read_bytes()
    return json.loads(raw)


def summarize(episodes: list[dict], global_mm: float = 600, local_mm: float = 50) -> dict:
    if not episodes or len({r["motion_index"] for r in episodes}) != len(episodes):
        raise ValueError("Missing/duplicate episodes")
    for row in episodes:
        if row["valid_samples"] <= 0 or any(
            not math.isfinite(row[k]) for k in ("global_mpjpe_mm", "local_mpjpe_mm")
        ):
            raise ValueError("Invalid pose measurement")
    return {
        "n": len(episodes),
        "global_mm": fmean(r["global_mpjpe_mm"] for r in episodes),
        "local_mm": fmean(r["local_mpjpe_mm"] for r in episodes),
        "completion": fmean(r["completed"] for r in episodes),
        "qualification": fmean(
            r["completed"] and r["global_mpjpe_mm"] <= global_mm and r["local_mpjpe_mm"] <= local_mm
            for r in episodes
        ),
    }


def retention_gate(current: dict, origin: dict) -> dict:
    constituents = []
    for condition in PROTECTED:
        row, base = current[condition], origin[condition]
        if min(base["global_mm"], base["local_mm"]) <= 0:
            raise ValueError("Undefined origin-relative error")
        constituents.append(
            {
                "condition": condition,
                **row,
                "origin_global_mm": base["global_mm"],
                "origin_local_mm": base["local_mm"],
                "origin_completion": base["completion"],
                "global_increase_pct": 100
                * (row["global_mm"] - base["global_mm"])
                / base["global_mm"],
                "local_increase_pct": 100 * (row["local_mm"] - base["local_mm"]) / base["local_mm"],
                "completion_loss_pp": 100 * base["completion"] - 100 * row["completion"],
            }
        )
    d = max(r[k] for r in constituents for k in ("global_increase_pct", "local_increase_pct"))
    loss = max(r["completion_loss_pp"] for r in constituents)
    return {"D_pct": d, "L_pp": loss, "passes": d <= 10 and loss <= 2, "constituents": constituents}


def auc(cells: dict, metric: str, frontier: bool = True) -> float:
    rungs = (125, 150, 175, 200) if frontier else (0, 25, 50, 75, 100)
    values = [cells[f"phys_{r:03d}"][metric] for r in rungs]
    return sum((a + b) / 2 for a, b in zip(values, values[1:])) / (len(values) - 1)


def analyze(data: Path) -> dict:
    panels = read_data(data, "retention_episodes.json.gz")["panels"]
    index = {}
    for p in panels:
        key = (p["continuation_seed"], p["arm"], p["iteration"], p["condition"])
        if key in index:
            raise ValueError("Duplicate panel")
        index[key] = p
    rows, trajectories, sensitivity, frontiers = [], [], [], []
    for seed, arms in [(8600, ("R0", "R1", "R2")), (8601, ("R0", "R1"))]:
        origin = {c: summarize(index[seed, "origin", 0, c]["episodes"]) for c in CONDITIONS}
        baseline_hard = 100 * fmean(origin[c]["qualification"] for c in HARD)
        for arm in ("origin", *arms):
            for iteration in ((0,) if arm == "origin" else ITERATIONS):
                current = {
                    c: summarize(index[seed, arm, iteration, c]["episodes"]) for c in CONDITIONS
                }
                for condition, summary in current.items():
                    rows.append(
                        {
                            "seed": seed,
                            "arm": arm,
                            "iteration": iteration,
                            "condition": condition,
                            **summary,
                        }
                    )
                gate = retention_gate(current, origin)
                trajectories.append(
                    {
                        "seed": seed,
                        "arm": arm,
                        "iteration": iteration,
                        **gate,
                        "hard_qualification_pct": 100
                        * fmean(current[c]["qualification"] for c in HARD),
                        "origin_hard_qualification_pct": baseline_hard,
                    }
                )
                for g in GLOBAL_GRID:
                    for l in LOCAL_GRID:
                        q = fmean(
                            summarize(index[seed, arm, iteration, c]["episodes"], g, l)[
                                "qualification"
                            ]
                            for c in HARD
                        )
                        base = fmean(
                            summarize(index[seed, "origin", 0, c]["episodes"], g, l)[
                                "qualification"
                            ]
                            for c in HARD
                        )
                        sensitivity.append(
                            {
                                "seed": seed,
                                "arm": arm,
                                "iteration": iteration,
                                "global_threshold_mm": g,
                                "local_threshold_mm": l,
                                "hard_qualification_pct": 100 * q,
                                "gain_pp": 100 * (q - base),
                            }
                        )
            if arm != "origin":
                feasible = [
                    r for r in trajectories if r["seed"] == seed and r["arm"] == arm and r["passes"]
                ]
                best = (
                    max(feasible, key=lambda r: (r["hard_qualification_pct"], -r["iteration"]))
                    if feasible
                    else None
                )
                frontiers.append(
                    {
                        "seed": seed,
                        "arm": arm,
                        "feasible_iterations": [r["iteration"] for r in feasible],
                        "exploratory_best": best,
                        "held_out": False,
                    }
                )
    historical = read_data(data, "historical.json")["rows"]
    returns = [r["terminal_return"] for r in historical]
    scores = [auc(r["cells"], "success_rate") for r in historical]
    # Frozen endpoint precision, rather than six-decimal copies in the inversion receipt.
    precise = read_data(data, "tolerance.json")["arms"]
    contrasts = []
    for metric in ("success_rate", "progress_rate"):
        for band, margin in (("frontier_auc", 2), ("in_envelope_auc", 1)):
            modes = [k for k in precise if k != "fixed"]
            if len(modes) != 1:
                raise ValueError("Ambiguous never-shrink arm")
            diffs = [
                100
                * (
                    precise[modes[0]][metric][band]["per_seed"][str(s)]["auc"]
                    - precise["fixed"][metric][band]["per_seed"][str(s)]["auc"]
                )
                for s in (8600, 8601, 8602)
            ]
            avg, sd = fmean(diffs), stdev(diffs)
            contrasts.append(
                {
                    "metric": metric,
                    "band": band,
                    "seeds": [8600, 8601, 8602],
                    "differences_pp": diffs,
                    "mean_pp": avg,
                    "sample_sd_pp": sd,
                    "one_sided_95_t_lower_pp": avg - t.ppf(0.95, 2) * sd / math.sqrt(3),
                    "margin_pp": margin,
                    "seed_passes": sum(x >= -margin for x in diffs),
                    "empirical_rule_passes": sum(x >= -margin for x in diffs) >= 2,
                }
            )
    return {
        "rows": rows,
        "retention": trajectories,
        "early_stopping": frontiers,
        "sensitivity": sensitivity,
        "contrasts": contrasts,
        "return_auc_spearman": float(spearmanr(returns, scores).statistic),
        "scope": "Development panels; same trained origin; no paired-rollout inference or held-out checkpoint selection.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    for row in result["early_stopping"]:
        best = row["exploratory_best"]
        print(
            row["seed"],
            row["arm"],
            "feasible",
            row["feasible_iterations"],
            "best",
            None if best is None else (best["iteration"], best["hard_qualification_pct"]),
        )
    print("Correlation", result["return_auc_spearman"], "frontier contrast", result["contrasts"][0])


if __name__ == "__main__":
    main()
