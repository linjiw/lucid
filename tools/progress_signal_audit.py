#!/usr/bin/env python3
"""Can a curriculum tell which conditions are still improving?

A curriculum that allocates practice by learning progress needs an estimate of
progress at a FIXED condition. TransCurriculum computes it as the current
average reward minus a per-bin exponential moving average; the guidance we are
working to asks for the same thing, estimated by repeated evaluation of
conditions that do not change. Neither says how much evidence that estimate
needs before its SIGN is trustworthy, and on a humanoid the per-condition sample
is small: a stratum of 128 environments ends only a handful of episodes per
iteration.

This tool measures that, offline, from training runs that already exist. It uses
the window of a run in which the frontier did not move, so every stratum is a
genuinely fixed condition, and it asks three questions.

1. **Noise floor.** Shuffle each stratum's per-iteration survival series in time,
   destroying any real trend, and measure how often a windowed slope of width W
   still comes out with a given sign and magnitude. That is the false-progress
   rate a gate would run at.
2. **Detection.** With the series in its true order, how wide must W be before
   the windowed slope agrees with the whole-window trend most of the time?
3. **Discrimination.** Do the strata plateau at different times? Allocation by
   progress is only useful if, at some point in training, some conditions are
   still improving and others are not.

It reports the numbers and refuses to recommend a threshold that its own noise
floor cannot support.

usage: progress_signal_audit.py RUN_DIR [RUN_DIR ...] [--out receipts/analysis/...]
"""

from __future__ import annotations

import argparse
import glob
import json
import math
from pathlib import Path
import random
import statistics


def load(run_dir: Path) -> tuple[list[dict], list[tuple[int, float]]]:
    """Per-iteration survival rows, and the frontier trajectory beside them."""
    survival = sorted(glob.glob(str(run_dir / "survival_*.jsonl")))
    curriculum = sorted(glob.glob(str(run_dir / "curriculum_*.jsonl")))
    if not survival:
        return [], []
    rows = [json.loads(line) for line in open(survival[0])]
    frontier: list[tuple[int, float]] = []
    if curriculum:
        for line in open(curriculum[0]):
            record = json.loads(line)
            lam = record.get("frontier", record.get("lambda"))
            if lam is not None:
                frontier.append((int(record.get("global_step", 0)), float(lam)))
    return rows, frontier


def stable_window(frontier: list[tuple[int, float]]) -> tuple[int, int, float]:
    """The longest run of iterations over which the frontier never moved."""
    if not frontier:
        return 0, 0, 0.0
    best = (0, 0, 0.0)
    start, value = frontier[0]
    for step, lam in frontier[1:]:
        if abs(lam - value) > 1e-9:
            if step - start > best[1] - best[0]:
                best = (start, step, value)
            start, value = step, lam
    if frontier[-1][0] - start > best[1] - best[0]:
        best = (start, frontier[-1][0], value)
    return best


def slope(series: list[float]) -> float:
    """Least-squares slope per iteration, in survival points."""
    n = len(series)
    if n < 3:
        return 0.0
    mean_x = (n - 1) / 2.0
    mean_y = statistics.fmean(series)
    num = sum((i - mean_x) * (y - mean_y) for i, y in enumerate(series))
    den = sum((i - mean_x) ** 2 for i in range(n))
    return 0.0 if den == 0 else 100.0 * num / den


def audit_stratum(series: list[float], windows: list[int], trials: int, rng: random.Random) -> dict:
    total = slope(series) * len(series)  # total change over the window, in points
    out: dict[str, dict] = {}
    for width in windows:
        if len(series) < width + 5:
            continue
        starts = range(0, len(series) - width, max(1, width // 4))
        true = [slope(series[s : s + width]) for s in starts]
        # Null: same values, order destroyed. Any slope here is noise.
        null: list[float] = []
        shuffled = list(series)
        for _ in range(trials):
            rng.shuffle(shuffled)
            s = rng.randrange(0, max(1, len(shuffled) - width))
            null.append(slope(shuffled[s : s + width]))
        null_abs = sorted(abs(v) for v in null)
        p95 = null_abs[int(0.95 * (len(null_abs) - 1))] if null_abs else 0.0
        agree = (
            sum(1 for v in true if (v > 0) == (total > 0)) / len(true) if true else 0.0
        )
        detected = sum(1 for v in true if abs(v) > p95) / len(true) if true else 0.0
        out[str(width)] = {
            "null_p95_abs_slope_pts_per_iter": round(p95, 5),
            "true_slope_mean_pts_per_iter": round(statistics.fmean(true), 5) if true else None,
            "sign_agrees_with_window_trend": round(agree, 3),
            "fraction_above_noise_floor": round(detected, 3),
        }
    return {"total_change_pts": round(total, 2), "by_window": out}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run_dirs", nargs="+", type=Path)
    ap.add_argument("--windows", type=int, nargs="+", default=[25, 50, 100, 200, 400])
    ap.add_argument("--trials", type=int, default=400)
    ap.add_argument("--out", type=Path, default=Path("receipts/analysis/lucid_progress_signal_audit_20260902.json"))
    a = ap.parse_args(argv)
    rng = random.Random(8600)

    report: dict = {
        "kind": "lucid_progress_signal_audit",
        "schema_version": 1,
        "question": "How much evidence does an estimate of learning progress at a FIXED condition need before its sign can be trusted, and do conditions plateau at different times?",
        "method": "Per-iteration per-stratum survival from the longest window in which the frontier never moved, so every stratum is a fixed condition. The null is the same series with its time order destroyed.",
        "runs": {},
    }
    for run_dir in a.run_dirs:
        rows, frontier = load(run_dir)
        if not rows:
            print(f"no survival telemetry in {run_dir}")
            continue
        lo, hi, lam = stable_window(frontier)
        window_rows = [r for r in rows if lo <= int(r.get("global_step", 0)) < hi]
        by_stratum: dict[int, list[float]] = {}
        episodes: dict[int, list[int]] = {}
        for row in window_rows:
            for entry in row.get("per_stratum") or []:
                index = int(entry["stratum"])
                if entry.get("survival") is None:
                    continue
                by_stratum.setdefault(index, []).append(float(entry["survival"]))
                episodes.setdefault(index, []).append(int(entry.get("episodes", 0)))
        run_report = {
            "frontier_held_at": lam,
            "iterations": [lo, hi],
            "iterations_used": len(window_rows),
            "strata": {},
        }
        for index in sorted(by_stratum):
            series = by_stratum[index]
            eps = episodes.get(index, [])
            run_report["strata"][str(index)] = {
                "episodes_per_iteration_median": statistics.median(eps) if eps else None,
                "survival_first_10pct": round(statistics.fmean(series[: max(1, len(series) // 10)]), 4),
                "survival_last_10pct": round(statistics.fmean(series[-max(1, len(series) // 10) :]), 4),
                **audit_stratum(series, a.windows, a.trials, rng),
            }
        report["runs"][str(run_dir)] = run_report

    # Cross-run reading
    plateaued, improving = [], []
    for run in report["runs"].values():
        for index, stratum in run["strata"].items():
            change = stratum["total_change_pts"]
            (improving if change >= 5.0 else plateaued).append((run["frontier_held_at"], index, change))
    report["discrimination"] = {
        "strata_still_improving_by_5pts_or_more": len(improving),
        "strata_plateaued": len(plateaued),
        "reading": (
            "conditions inside one run plateau at different times, so allocation by progress has "
            "something to separate" if improving and plateaued else
            "every condition in the window moves the same way, so progress cannot separate them here"),
    }
    smallest_usable = {}
    for name, run in report["runs"].items():
        for index, stratum in run["strata"].items():
            for width, stats in stratum["by_window"].items():
                if stats["sign_agrees_with_window_trend"] >= 0.8 and stats["fraction_above_noise_floor"] >= 0.5:
                    smallest_usable.setdefault(index, int(width))
                    break
    report["smallest_window_with_trustworthy_sign_per_stratum"] = smallest_usable
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=1) + "\n")

    for name, run in report["runs"].items():
        print(f"\n{Path(name).parent.name}/{Path(name).name}  frontier held at {run['frontier_held_at']} "
              f"for iterations {run['iterations'][0]}-{run['iterations'][1]}")
        print(f"{'stratum':>7} {'eps/it':>7} {'first':>7} {'last':>7} {'change':>8}   " +
              "  ".join(f"W={w:<4}" for w in a.windows))
        for index in sorted(run["strata"], key=int):
            s = run["strata"][index]
            cells = []
            for w in a.windows:
                stat = s["by_window"].get(str(w))
                cells.append("   -   " if stat is None else f"{stat['sign_agrees_with_window_trend']:.2f}   ")
            print(f"{index:>7} {str(s['episodes_per_iteration_median']):>7} {s['survival_first_10pct']:>7.3f} "
                  f"{s['survival_last_10pct']:>7.3f} {s['total_change_pts']:>8.1f}   " + "".join(cells))
    print("\nW = window width in iterations; the number is how often a windowed slope's sign")
    print("agrees with the trend over the whole stable window. 0.50 is a coin flip.")
    print(f"\nreceipt -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
