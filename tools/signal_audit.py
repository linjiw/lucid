#!/usr/bin/env python3
"""Signal admissibility audit: is a candidate curriculum signal anchored?

Read-only. Touches no GPU, no artifact, no checkpoint.

A difficulty controller's signal must be *anchored*: monotone in competence
while difficulty is held fixed. If it is not, the controller is steering on a
quantity that moves for reasons unrelated to how the policy is doing, and no
amount of gain tuning repairs that.

This script tests three candidate signals against exactly that requirement,
using arms whose applied lambda is pinned at 1.0 for essentially all of
training (fixed DR, and the monotone ratchet, which is distributionally
identical to it). Difficulty is constant by construction in those runs, so any
systematic movement in a signal is movement in the *instrument*, and any
non-monotonicity is disqualifying.

  latent gap p90   the LUCID manuscript's signal, from the frozen temporal
                   autoencoder, measured on ONE tracked environment
  mean return      the guard signal, and the monitor anyone would reach for
  time-out rate    the fraction of episodes that ended by reaching the end of
                   the clip rather than by a termination condition, over the
                   whole 1,024-environment population

Reported per arm:

  spearman         rank correlation of the signal against the iteration index.
                   An anchored signal tracks competence, and competence rises
                   over a run at fixed difficulty, so this should be strongly
                   positive.
  monotone_frac    fraction of consecutive block-mean pairs that do not
                   decrease. 1.0 is perfectly monotone.
  reversals        how many times the block-mean series changes direction. An
                   anchored signal has few; a drifting one has many.
  range/spread     the signal's own spread, to show a wandering signal is not
                   merely noisy but wanders over most of its range.

usage: signal_audit.py [--out audit.json]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import statistics
from typing import Any

ARTIFACTS = Path("/home/linjiw/lucid-sonic/artifacts/curriculum_comparison")
OUTPUTS = Path("/home/linjiw/lucid-sonic/outputs")

#: Arms whose applied lambda is constant at 1.0 for all but a brief warm-up.
#: These are the only runs where "difficulty held fixed" is true by
#: construction, which is what makes the anchoring test valid.
FIXED_DIFFICULTY_ARMS = {
    "fixed@s8600": ("curriculum_comparison_ne1024_20260829_000249/seed_8600/fixed", None),
    "fixed@s8601": ("curriculum_comparison_ne1024_20260829_000249/seed_8601/fixed", None),
    "fixed@s8602": ("curriculum_comparison_ne1024_20260901_044118/seed_8602/fixed", None),
    "ratchet@s8600": (
        "curriculum_comparison_ne1024_20260831_231901/seed_8600/lucid_ratchet_rg",
        None,
    ),
    "ratchet@s8601": (
        "curriculum_comparison_ne1024_20260831_144022/seed_8601/lucid_ratchet_rg",
        None,
    ),
}

#: Arms whose lambda moved. Reported separately and never pooled with the
#: fixed-difficulty arms: in these runs a signal may move because difficulty
#: moved, which is exactly the confound the anchoring test must avoid.
MOVING_DIFFICULTY_ARMS = {
    "lucid_rg@s8601 (evacuated)": (
        "curriculum_comparison_ne1024_20260829_000249/seed_8601/lucid_rg",
        None,
    ),
    "lucid_s4_rg@s8600 (evacuated)": (
        "curriculum_comparison_ne1024_20260829_000249/seed_8600/lucid_s4_rg",
        None,
    ),
    "off@s8600 (no randomization)": (
        "curriculum_comparison_ne1024_20260829_000249/seed_8600/off",
        None,
    ),
}

ITERATION = re.compile(r"Learning iteration (\d+)")
TIMEOUT = re.compile(r"Episode_Termination/time_out:\s*([0-9.]+)")
REWARD = re.compile(r"Mean rewards:\s*(-?[0-9.]+)")


def parse_log(path: Path) -> dict[int, dict[str, float]]:
    """Per-iteration time-out rate and mean reward, keyed by iteration.

    Parsed by iteration header rather than by line position, so a truncated or
    interleaved log cannot silently shift the series.
    """
    rows: dict[int, dict[str, float]] = {}
    current: int | None = None
    if not path.exists():
        return rows
    with path.open(errors="ignore") as handle:
        for line in handle:
            found = ITERATION.search(line)
            if found:
                current = int(found.group(1))
                continue
            if current is None:
                continue
            found = TIMEOUT.search(line)
            if found:
                rows.setdefault(current, {})["time_out"] = float(found.group(1))
                continue
            found = REWARD.search(line)
            if found:
                rows.setdefault(current, {})["mean_reward"] = float(found.group(1))
    return rows


def parse_observer(path: Path) -> dict[int, float]:
    """Per-iteration latent gap p90, keyed by global step."""
    rows: dict[int, float] = {}
    if not path.exists():
        return rows
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            value = record.get("latent_p90")
            if value is not None:
                rows[int(record["global_step"])] = float(value)
    return rows


def parse_curriculum(path: Path) -> dict[int, float]:
    rows: dict[int, float] = {}
    if not path.exists():
        return rows
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if "lambda" in record:
                rows[int(record["global_step"])] = float(record["lambda"])
    return rows


def spearman(xs: list[float], ys: list[float]) -> float | None:
    """Rank correlation, ties averaged. No SciPy dependency."""
    if len(xs) < 3 or len(xs) != len(ys):
        return None

    def rank(values: list[float]) -> list[float]:
        order = sorted(range(len(values)), key=lambda i: values[i])
        ranks = [0.0] * len(values)
        index = 0
        while index < len(order):
            stop = index
            while stop + 1 < len(order) and values[order[stop + 1]] == values[order[index]]:
                stop += 1
            shared = (index + stop) / 2.0 + 1.0
            for position in range(index, stop + 1):
                ranks[order[position]] = shared
            index = stop + 1
        return ranks

    rx, ry = rank(xs), rank(ys)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def blocks(steps: list[int], values: list[float], count: int = 40) -> list[float]:
    """Block means, to judge trend rather than per-iteration noise."""
    if not values:
        return []
    size = max(1, len(values) // count)
    out = []
    for start in range(0, len(values), size):
        chunk = values[start : start + size]
        if chunk:
            out.append(statistics.fmean(chunk))
    return out


def describe(name: str, steps: list[int], values: list[float]) -> dict[str, Any]:
    if len(values) < 10:
        return {"signal": name, "n": len(values), "note": "too few samples"}
    means = blocks(steps, values)
    pairs = list(zip(means, means[1:]))
    rising = sum(1 for a, b in pairs if b >= a)
    directions = [1 if b > a else (-1 if b < a else 0) for a, b in pairs if b != a]
    reversals = sum(1 for a, b in zip(directions, directions[1:]) if a != b)
    return {
        "signal": name,
        "n": len(values),
        "spearman_vs_iteration": (
            None
            if spearman([float(s) for s in steps], values) is None
            else round(spearman([float(s) for s in steps], values), 4)
        ),
        "monotone_frac": round(rising / len(pairs), 4) if pairs else None,
        "reversals": reversals,
        "block_min": round(min(means), 4),
        "block_max": round(max(means), 4),
        "first_block": round(means[0], 4),
        "last_block": round(means[-1], 4),
        "p10": round(sorted(values)[len(values) // 10], 4),
        "p90": round(sorted(values)[9 * len(values) // 10], 4),
    }


def audit(label: str, relative: str) -> dict[str, Any]:
    directory = ARTIFACTS / relative
    branch = None
    for candidate in directory.glob("observer_*.jsonl"):
        branch = candidate.name[len("observer_") : -len(".jsonl")]
        break
    if branch is None:
        return {"arm": label, "error": f"no observer jsonl under {directory}"}
    gaps = parse_observer(directory / f"observer_{branch}.jsonl")
    lambdas = parse_curriculum(directory / f"curriculum_{branch}.jsonl")
    log = parse_log(OUTPUTS / f"{branch}.log")

    shared = sorted(set(gaps) & set(log) & set(lambdas))
    if not shared:
        # Observer and log may key iterations differently by one; fall back to
        # the intersection of whichever two are present.
        shared = sorted(set(gaps) & set(log))
    gap_series = [gaps[s] for s in shared]
    timeout_series = [log[s]["time_out"] for s in shared if "time_out" in log[s]]
    timeout_steps = [s for s in shared if "time_out" in log[s]]
    reward_series = [log[s]["mean_reward"] for s in shared if "mean_reward" in log[s]]
    reward_steps = [s for s in shared if "mean_reward" in log[s]]
    lam = [lambdas[s] for s in shared if s in lambdas]

    return {
        "arm": label,
        "branch": branch,
        "iterations_matched": len(shared),
        "lambda_min": round(min(lam), 4) if lam else None,
        "lambda_max": round(max(lam), 4) if lam else None,
        "lambda_final": round(lam[-1], 4) if lam else None,
        "signals": [
            describe("latent_gap_p90", shared, gap_series),
            describe("time_out_rate", timeout_steps, timeout_series),
            describe("mean_return", reward_steps, reward_series),
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    report: dict[str, Any] = {
        "kind": "lucid_signal_admissibility_audit",
        "schema_version": 1,
        "question": (
            "Is the signal monotone in competence while applied difficulty is "
            "held fixed? A signal that is not cannot drive a difficulty controller."
        ),
        "fixed_difficulty_arms": [],
        "moving_difficulty_arms": [],
    }
    for label, (relative, _) in FIXED_DIFFICULTY_ARMS.items():
        report["fixed_difficulty_arms"].append(audit(label, relative))
    for label, (relative, _) in MOVING_DIFFICULTY_ARMS.items():
        report["moving_difficulty_arms"].append(audit(label, relative))

    def summarise(entries: list[dict[str, Any]], signal: str) -> dict[str, Any]:
        rows = [
            item
            for entry in entries
            for item in entry.get("signals", [])
            if item["signal"] == signal and item.get("spearman_vs_iteration") is not None
        ]
        if not rows:
            return {}
        return {
            "arms": len(rows),
            "spearman_min": min(r["spearman_vs_iteration"] for r in rows),
            "spearman_max": max(r["spearman_vs_iteration"] for r in rows),
            "spearman_mean": round(
                statistics.fmean(r["spearman_vs_iteration"] for r in rows), 4
            ),
            "monotone_frac_mean": round(statistics.fmean(r["monotone_frac"] for r in rows), 4),
            "reversals_mean": round(statistics.fmean(r["reversals"] for r in rows), 2),
        }

    report["verdict_at_fixed_difficulty"] = {
        signal: summarise(report["fixed_difficulty_arms"], signal)
        for signal in ("latent_gap_p90", "time_out_rate", "mean_return")
    }
    text = json.dumps(report, indent=2)
    if args.out:
        args.out.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
