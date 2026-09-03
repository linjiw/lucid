#!/usr/bin/env python3
"""How many episodes did a run actually spend at each difficulty?

Widening a uniform range lowers the density everywhere inside it, so a condition
can stay formally "inside the training support" while being practised far less
than before. Intended support is therefore not exposure, and a curriculum that
reports the first is not reporting the second.

This measures the second, from telemetry the runs already wrote. Every training
iteration logs the episodes each cohort ended, and each cohort's intensity is
known from the curriculum trace, so the episodes can be summed into intensity
bins over the whole run. The result is what the policy actually practised.

usage: realized_exposure.py RUN_DIR [RUN_DIR ...] [--out receipts/analysis/...]
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

#: The common accounting unit. Every iteration, each cohort trains all of its environments
#: for the same rollout length at that cohort's intensity, so environment-iterations are
#: comparable across arms with and without cohorts and need no episode data. Episode counts
#: are NOT comparable across intensities: a harder cohort ends more, shorter episodes, which
#: inflates its share for a reason that has nothing to do with how much it was practised.
UNITS = ("env_iterations", "episodes")

BINS = [(0.0, 0.5), (0.5, 0.9), (0.9, 1.1), (1.1, 1.4), (1.4, 1.75), (1.75, 10.0)]
LABELS = ["below 0.5", "0.5-0.9", "at the envelope", "1.1-1.4", "1.4-1.75", "above 1.75"]


def stratum_intensities(curriculum_rows: list[dict], strata: int) -> dict[int, list[float]]:
    """Per-iteration intensity of each stratum, from the frontier trajectory."""
    out: dict[int, list[float]] = {}
    for record in curriculum_rows:
        absolute = record.get("stratum_lambdas")
        frontier = record.get("frontier", record.get("lambda"))
        values: list[float] = []
        if isinstance(absolute, list) and absolute:
            for level in absolute:
                if isinstance(level, dict):
                    values.append(max(level.values()) if level else float(frontier or 1.0))
                else:
                    values.append(float(level))
        elif frontier is not None:
            # No explicit vector: strata are even fractions of the frontier, and a
            # single-stratum arm sits at the frontier itself.
            values = ([float(frontier)] if strata <= 1
                      else [float(frontier) * (k + 1) / strata for k in range(strata)])
        for index, value in enumerate(values):
            out.setdefault(index, []).append(value)
    return out


def exposure_from_dispatch(crows: list[dict]) -> tuple[list[float], float] | None:
    """Fallback for arms with no survival telemetry.

    Every iteration's cohort telemetry carries a cumulative count of environment
    resets per stratum. Differencing it gives the environments actually drawn at
    each stratum's intensity that iteration, which is exposure in the same sense
    as an episode count and is recorded for every arm that has cohorts.
    """
    totals = [0.0] * len(BINS)
    grand = 0.0
    previous: dict[str, float] = {}
    for record in crows:
        tace = record.get("tace") or {}
        dispatch = tace.get("dispatch") or {}
        if not dispatch:
            continue
        term = next(iter(dispatch.values()))
        counts = term.get("env_counts") or {}
        lambdas = tace.get("stratum_lambdas") or []
        for index, value in enumerate(lambdas):
            key = f"focus_s{index}"
            now = float(counts.get(key, 0.0))
            delta = max(0.0, now - previous.get(key, 0.0))
            previous[key] = now
            level = max(value.values()) if isinstance(value, dict) and value else float(value)
            grand += delta
            for b, (lo, hi) in enumerate(BINS):
                if lo <= level < hi:
                    totals[b] += delta
                    break
    return (totals, grand) if grand > 0 else None


def exposure_env_iterations(crows: list[dict]) -> tuple[list[float], float] | None:
    """Environment-iterations per intensity band, the unit every arm can be counted in.

    Each iteration contributes ``cohort size`` to the band its intensity falls in, for every
    cohort. A single-cohort arm contributes all of its environments to the band holding its
    pinned intensity, which is why a pinned arm reads 100% in this unit exactly as it does in
    any other.
    """
    totals = [0.0] * len(BINS)
    grand = 0.0
    for record in crows:
        tace = record.get("tace") or {}
        sizes = tace.get("stratum_sizes")
        lambdas = tace.get("stratum_lambdas")
        if sizes and lambdas and len(sizes) == len(lambdas):
            pairs = [(float(n), (max(v.values()) if isinstance(v, dict) and v else float(v)))
                     for n, v in zip(sizes, lambdas)]
        else:
            value = record.get("frontier_lambda", record.get("lambda"))
            if value is None:
                continue
            pairs = [(1.0, float(value))]  # one cohort; the weight cancels in the share
        for weight, level in pairs:
            grand += weight
            for b, (lo, hi) in enumerate(BINS):
                if lo <= level < hi:
                    totals[b] += weight
                    break
    return (totals, grand) if grand > 0 else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run_dirs", nargs="+", type=Path)
    ap.add_argument("--unit", choices=UNITS, default="env_iterations",
                    help="common accounting unit; env_iterations is comparable across arms")
    ap.add_argument("--out", type=Path, default=Path("receipts/analysis/lucid_realized_exposure_20260902.json"))
    a = ap.parse_args(argv)
    report: dict = {
        "kind": "lucid_realized_exposure",
        "schema_version": 2,
        "question": "How many training episodes did each run actually spend at each difficulty, as opposed to which difficulties were formally inside its support?",
        "method": "Exposure per cohort per iteration, binned by that cohort's intensity from the curriculum trace and summed over the run. The default unit is environment-iterations, which every arm can be counted in and which does not vary with episode length; episodes are available as an alternative but are NOT comparable across intensities, because a harder cohort ends more and shorter episodes.",
        "unit": None,
        "bins": {label: list(edges) for label, edges in zip(LABELS, BINS)},
        "runs": {},
    }
    for run_dir in a.run_dirs:
        survival = sorted(glob.glob(str(run_dir / "survival_*.jsonl")))
        curriculum = sorted(glob.glob(str(run_dir / "curriculum_*.jsonl")))
        if not curriculum:
            continue
        crows = [json.loads(line) for line in open(curriculum[0])]
        srows = [json.loads(line) for line in open(survival[0])] if survival else []
        if a.unit == "env_iterations":
            counted = exposure_env_iterations(crows)
            if counted is None:
                continue
            totals, total_episodes = counted
            report["runs"][run_dir.name + "@" + run_dir.parent.name] = {
                "path": str(run_dir),
                "exposure_source": "environment-iterations per cohort intensity",
                "unit": "env_iterations",
                "total_units": int(total_episodes),
                "episodes_by_difficulty": {l: int(t) for l, t in zip(LABELS, totals)},
                "share_by_difficulty": {l: round(t / total_episodes, 4) for l, t in zip(LABELS, totals)},
                "share_at_or_below_the_envelope": round(sum(totals[:3]) / total_episodes, 4),
            }
            continue
        by_step = {int(r.get("global_step", 0)): r for r in crows}
        strata = max((len(r.get("per_stratum") or []) for r in srows), default=1) or 1
        totals = [0.0] * len(BINS)
        total_episodes = 0.0
        for row in srows:
            step = int(row.get("global_step", 0))
            record = by_step.get(step)
            if record is None:
                continue
            per = row.get("per_stratum") or []
            if per:
                absolute = (record.get("tace") or {}).get("stratum_lambdas") or record.get("stratum_lambdas")
                frontier = record.get("frontier", record.get("lambda")) or 1.0
                for entry in per:
                    index = int(entry["stratum"])
                    episodes = float(entry.get("episodes") or 0)
                    if isinstance(absolute, list) and index < len(absolute):
                        level = absolute[index]
                        value = (max(level.values()) if isinstance(level, dict) and level
                                 else float(level) if not isinstance(level, dict) else float(frontier))
                    else:
                        value = float(frontier) * (index + 1) / max(1, strata)
                    total_episodes += episodes
                    for b, (lo, hi) in enumerate(BINS):
                        if lo <= value < hi:
                            totals[b] += episodes
                            break
            else:
                episodes = float(row.get("episodes_ended") or 0)
                value = float(record.get("frontier", record.get("lambda")) or 0.0)
                total_episodes += episodes
                for b, (lo, hi) in enumerate(BINS):
                    if lo <= value < hi:
                        totals[b] += episodes
                        break
        source = "episodes ended per cohort"
        if total_episodes <= 0:
            fallback = exposure_from_dispatch(crows)
            if fallback is None:
                # A single-cohort arm at a pinned intensity: exposure is exact.
                pinned = [float(r.get("lambda")) for r in crows if r.get("lambda") is not None]
                if not pinned:
                    continue
                totals = [0.0] * len(BINS)
                for value in pinned:
                    for b, (lo, hi) in enumerate(BINS):
                        if lo <= value < hi:
                            totals[b] += 1.0
                            break
                total_episodes = float(len(pinned))
                source = "iterations at the pinned intensity (single cohort)"
            else:
                totals, total_episodes = fallback
                source = "environment resets per cohort"
        report["runs"][run_dir.name + "@" + run_dir.parent.name] = {
            "path": str(run_dir),
            "exposure_source": source,
            "total_episodes": int(total_episodes),
            "episodes_by_difficulty": {l: int(t) for l, t in zip(LABELS, totals)},
            "share_by_difficulty": {l: round(t / total_episodes, 4) for l, t in zip(LABELS, totals)},
            "share_at_or_below_the_envelope": round(sum(totals[:3]) / total_episodes, 4),
        }

    report["unit"] = a.unit
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=1) + "\n")
    width = max((len(k) for k in report["runs"]), default=10)
    print(f"{'run':{width}} {'units':>12} " + " ".join(f"{l:>16}" for l in LABELS) + f" {'<= envelope':>12}")
    for name, run in report["runs"].items():
        cells = " ".join(f"{100 * run['share_by_difficulty'][l]:15.1f}%" for l in LABELS)
        print(f"{name:{width}} {run.get('total_units', run.get('total_episodes', 0)):>12,} {cells} {100 * run['share_at_or_below_the_envelope']:11.1f}%")
    print(f"\nshare of all {a.unit} whose cohort sat in that intensity band")
    print(f"receipt -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
