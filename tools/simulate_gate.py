#!/usr/bin/env python3
"""Replay the survival gate law over a recorded survival series. Read-only.

Two uses.

**Before Phase 2**, as a feasibility check: run the frozen gate law against the
per-iteration time-out series of a completed fixed-DR run, under assumptions
about how much harder the probe stratum is than the frontier. The probe is
never as easy as the frontier, so the zero-penalty case is a strict upper bound
on how fast the gate can expand.

**After Phase 2**, as the threshold sensitivity analysis: gate_150 records
probe survival every iteration in ``survival_<branch>.jsonl``, so the law can
be replayed at any threshold against the ACTUAL probe series at zero GPU cost.
That converts "the gate stalled at 1.25" from a dead end into a measurement of
how conservative the frozen threshold was.

usage: simulate_gate.py --log LOG [--survival-jsonl PATH] [--thresholds 0.7 0.8 0.9]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, "/home/linjiw/lucid/GR00T-WholeBodyControl")

from gear_sonic.research.practice_utility.survival_gate import (  # noqa: E402
    SurvivalGateConfig,
    SurvivalGateController,
)

ITERATION = re.compile(r"Learning iteration (\d+)")
TIMEOUT = re.compile(r"Episode_Termination/time_out:\s*([0-9.]+)")


def series_from_log(path: Path) -> list[float]:
    """Population time-out rate per iteration, from a training log."""
    rows: dict[int, float] = {}
    current: int | None = None
    for line in path.open(errors="ignore"):
        found = ITERATION.search(line)
        if found:
            current = int(found.group(1))
            continue
        if current is None:
            continue
        found = TIMEOUT.search(line)
        if found:
            rows[current] = float(found.group(1))
    return [rows[k] for k in sorted(rows)]


def series_from_jsonl(path: Path) -> list[tuple[float | None, int]]:
    """Actual probe survival per iteration, from a gate arm's own telemetry."""
    out: list[tuple[float | None, int]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        index = record.get("probe_index")
        strata = record.get("per_stratum") or []
        if index is None or index >= len(strata):
            out.append((None, 0))
            continue
        entry = strata[index]
        out.append((entry.get("survival"), int(entry.get("episodes", 0))))
    return out


def replay(
    survival: list[tuple[float | None, int]],
    threshold: float,
    **overrides,
) -> dict:
    config = SurvivalGateConfig(
        threshold=threshold,
        window=overrides.get("window", 200),
        step_size=0.125,
        probe_offset=0.125,
        dwell=overrides.get("dwell", 200),
        min_episodes=overrides.get("min_episodes", 200),
        lambda_max=1.5,
        probe_max=1.5,
    )
    gate = SurvivalGateController(config, initial_lambda=1.0)
    fired: list[int] = []
    for index, (rate, episodes) in enumerate(survival):
        step = gate.update(probe_survival=rate, probe_episodes=episodes)
        if step.fired:
            fired.append(index)
    return {
        "threshold": threshold,
        "expansions": gate.expansions,
        "final_frontier": round(gate.frontier, 4),
        "fired_at": fired,
        "applied_decreases": sum(1 for s in gate.history if s.applied_decrease),
        "incidents": len(gate.incidents),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, default=None)
    parser.add_argument("--survival-jsonl", type=Path, default=None)
    parser.add_argument("--thresholds", type=float, nargs="+", default=[0.6, 0.7, 0.8, 0.9])
    parser.add_argument(
        "--probe-penalty",
        type=float,
        nargs="+",
        default=[0.0, 0.05, 0.12],
        help="log mode only: points of survival the probe loses per expansion step",
    )
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    report: dict = {"kind": "lucid_gate_replay", "schema_version": 1}

    if args.survival_jsonl:
        observed = series_from_jsonl(args.survival_jsonl)
        report["source"] = str(args.survival_jsonl)
        report["source_kind"] = "actual probe survival"
        report["iterations"] = len(observed)
        report["replays"] = [replay(observed, t) for t in args.thresholds]
    elif args.log:
        population = series_from_log(args.log)
        report["source"] = str(args.log)
        report["source_kind"] = (
            "population time-out rate of a fixed-DR run, used as a PROXY for probe "
            "survival. The probe trains above the frontier and is strictly harder, so "
            "the zero-penalty row is an upper bound on expansion speed, not a prediction."
        )
        report["iterations"] = len(population)
        rows = []
        for penalty in args.probe_penalty:
            for threshold in args.thresholds:
                proxy: list[tuple[float | None, int]] = []
                gate_steps = 0
                for rate in population:
                    proxy.append((max(0.0, rate - penalty * (1 + gate_steps)), 10))
                # Penalty compounds per expansion, so recompute inside replay by
                # running a stateful pass rather than a precomputed series.
                result = replay_with_penalty(population, threshold, penalty)
                result["probe_penalty_per_step"] = penalty
                rows.append(result)
                del proxy, gate_steps
        report["replays"] = rows
    else:
        parser.error("pass --log or --survival-jsonl")

    text = json.dumps(report, indent=2)
    if args.out:
        args.out.write_text(text)
    print(text)
    return 0


def replay_with_penalty(population: list[float], threshold: float, penalty: float) -> dict:
    """Proxy replay where the probe loses ``penalty`` per expansion already taken."""
    config = SurvivalGateConfig(
        threshold=threshold,
        window=200,
        step_size=0.125,
        probe_offset=0.125,
        dwell=200,
        min_episodes=200,
        lambda_max=1.5,
        probe_max=1.5,
    )
    gate = SurvivalGateController(config, initial_lambda=1.0)
    fired: list[int] = []
    for index, rate in enumerate(population):
        probe = max(0.0, rate - penalty * (1 + gate.expansions))
        step = gate.update(probe_survival=probe, probe_episodes=10)
        if step.fired:
            fired.append(index)
    return {
        "threshold": threshold,
        "expansions": gate.expansions,
        "final_frontier": round(gate.frontier, 4),
        "fired_at": fired,
    }


if __name__ == "__main__":
    raise SystemExit(main())
