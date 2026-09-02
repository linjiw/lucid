#!/usr/bin/env python3
"""Physical-signal admissibility audit: can a body-grounded metric gate difficulty?

Read-only. Touches no GPU, no artifact, no checkpoint.

The first audit (``signal_audit.py``) tested three candidate curriculum signals
-- the learned latent gap, mean return, and the episode time-out rate -- and
found the gap unanchored and return unbounded. The natural follow-up question
is whether a signal grounded in the *body* rather than in the reward or in a
learned representation does better: foot slip under load, actuator saturation,
mechanical work, joint-limit proximity, undesired contact. Every one of these is
already logged, population-wide, once per PPO iteration, by the practice
observer (``observer_*.jsonl``), and the frozen-policy evaluator writes the same
batch diagnostics for every ladder cell. So the question can be answered from
existing telemetry before any new controller is built.

Three properties are measured, each on data where it is identifiable:

1. **Anchoring** (training telemetry, applied lambda pinned at 1.0). Is the
   signal monotone in competence while difficulty is held fixed? Rank
   correlation against the iteration index, direction-agnostic monotone
   fraction, reversals, and a late-run saturation index: how much of the
   signal's whole-run range is still moving over the last quarter of training.
   A signal that has saturated cannot resolve further competence gains.

2. **Difficulty response** (frozen-policy ladders, competence pinned). For one
   frozen checkpoint scored at nine intensities from lambda = 0 to 2.0, does the
   signal move monotonically with difficulty, and does it track the outcome
   (success rate) across cells? This is the property a *probe-level* gate
   needs: the signal must respond to the difficulty it is measured at. Caveat
   carried from the evaluator receipts: batch diagnostics include auto-reset
   environments after their scored episode terminates, so tracking-error style
   metrics are contaminated; the audit reports the correlation and the caveat
   together.

3. **Authority under the actuator** (training telemetry, the two evacuations).
   Over the window where the unconstrained controller cut lambda, the
   correlation between applied lambda and each signal. The latent gap scored
   r = -0.20 here, which is why the retreat was total rather than partial.
   A body-grounded signal that responds to lambda with the right sign would at
   least have given the integrator a restoring force.

usage: physical_signal_audit.py [--out audit.json]
"""

from __future__ import annotations

import argparse
import glob
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import signal_audit as SA  # noqa: E402

LUCID_ROOT = Path("/home/linjiw/lucid-sonic")
RECEIPT_ROOTS = [LUCID_ROOT / "manifests", Path("/home/linjiw/lucid/receipts")]

#: Population-wide physical telemetry written by the practice observer every
#: iteration, with the direction in which the signal is expected to *improve*
#: as the policy gets better at fixed difficulty.
PHYSICAL_SIGNALS: dict[str, str] = {
    "foot_slip_per_step_m": "down",
    "torque_saturation": "down",
    "joint_limit_proximity": "down",
    "energy_proxy": "down",
    "undesired_contact_rate": "down",
    "contact_force_peak": "down",
    "contact_impulse_total": "down",
    "action_rate": "down",
    "action_acceleration": "down",
}
#: Reference signals from the first audit, for side-by-side comparison.
REFERENCE_SIGNALS: dict[str, str] = {
    "latent_p90": "down",
    "time_out_rate": "up",
    "mean_return": "up",
}
#: The evaluator writes these per cell.
EVAL_SIGNALS = ["foot_slip_per_step_m", "torque_saturation", "energy_proxy", "undesired_contact_rate"]
PHYS_LAMBDA = {
    "phys_000": 0.0, "phys_025": 0.25, "phys_050": 0.5, "phys_075": 0.75, "phys_100": 1.0,
    "phys_125": 1.25, "phys_150": 1.5, "phys_175": 1.75, "phys_200": 2.0,
}
#: Where each evacuation's descent began (first iteration after the last time
#: applied lambda was >= 0.95), so the authority window is the retreat itself.
COLLAPSE_ARMS = {
    "lucid_rg@s8601": "curriculum_comparison_ne1024_20260829_000249/seed_8601/lucid_rg",
    "lucid_s4_rg@s8600": "curriculum_comparison_ne1024_20260829_000249/seed_8600/lucid_s4_rg",
}


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    dx = math.sqrt(sum((a - mx) ** 2 for a in xs))
    dy = math.sqrt(sum((b - my) ** 2 for b in ys))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def parse_observer_all(path: Path) -> dict[int, dict[str, float]]:
    rows: dict[int, dict[str, float]] = {}
    if not path.exists():
        return rows
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            step = int(record["global_step"])
            rows[step] = {
                k: float(v)
                for k, v in record.items()
                if isinstance(v, (int, float)) and not isinstance(v, bool)
            }
    return rows


def describe(name: str, direction: str, steps: list[int], values: list[float]) -> dict[str, Any]:
    if len(values) < 10:
        return {"signal": name, "n": len(values), "note": "too few samples"}
    means = SA.blocks(steps, values)
    pairs = list(zip(means, means[1:]))
    rising = sum(1 for a, b in pairs if b >= a)
    falling = sum(1 for a, b in pairs if b <= a)
    directions = [1 if b > a else (-1 if b < a else 0) for a, b in pairs if b != a]
    reversals = sum(1 for a, b in zip(directions, directions[1:]) if a != b)
    rho = SA.spearman([float(s) for s in steps], values)
    span = max(means) - min(means)
    quarter = max(1, len(means) // 4)
    late = means[-quarter:]
    late_span = (max(late) - min(late)) / span if span > 0 else None
    late_trend = (late[-1] - late[0]) / span if span > 0 else None
    expected_sign = 1.0 if direction == "up" else -1.0
    return {
        "signal": name,
        "improves": direction,
        "n": len(values),
        "spearman_vs_iteration": None if rho is None else round(rho, 4),
        "sign_matches_improvement": None if rho is None else bool(rho * expected_sign > 0),
        "monotone_frac_directional": round(max(rising, falling) / len(pairs), 4) if pairs else None,
        "reversals": reversals,
        "block_min": round(min(means), 5),
        "block_max": round(max(means), 5),
        "first_block": round(means[0], 5),
        "last_block": round(means[-1], 5),
        # Fraction of the whole-run block range still traversed in the last
        # quarter of training. ~0 means saturated; ~1 means still moving.
        "late_quarter_range_frac": None if late_span is None else round(late_span, 4),
        "late_quarter_trend_frac": None if late_trend is None else round(late_trend, 4),
    }


def load_arm(relative: str) -> dict[str, Any] | None:
    directory = SA.ARTIFACTS / relative
    branch = None
    for candidate in directory.glob("observer_*.jsonl"):
        branch = candidate.name[len("observer_") : -len(".jsonl")]
        break
    if branch is None:
        return None
    observer = parse_observer_all(directory / f"observer_{branch}.jsonl")
    lambdas = SA.parse_curriculum(directory / f"curriculum_{branch}.jsonl")
    log = SA.parse_log(SA.OUTPUTS / f"{branch}.log")
    return {"branch": branch, "observer": observer, "lambdas": lambdas, "log": log}


def series(arm: dict[str, Any], signal: str, steps: list[int]) -> tuple[list[int], list[float]]:
    if signal == "time_out_rate":
        keep = [s for s in steps if "time_out" in arm["log"].get(s, {})]
        return keep, [arm["log"][s]["time_out"] for s in keep]
    if signal == "mean_return":
        keep = [s for s in steps if "mean_reward" in arm["log"].get(s, {})]
        return keep, [arm["log"][s]["mean_reward"] for s in keep]
    keep = [s for s in steps if signal in arm["observer"].get(s, {})]
    return keep, [arm["observer"][s][signal] for s in keep]


def anchoring(label: str, relative: str) -> dict[str, Any]:
    arm = load_arm(relative)
    if arm is None:
        return {"arm": label, "error": f"no observer jsonl under {relative}"}
    steps = sorted(set(arm["observer"]) & set(arm["log"]))
    lam = [arm["lambdas"][s] for s in steps if s in arm["lambdas"]]
    out = {
        "arm": label,
        "branch": arm["branch"],
        "iterations_matched": len(steps),
        "lambda_min": round(min(lam), 4) if lam else None,
        "lambda_max": round(max(lam), 4) if lam else None,
        "signals": [],
    }
    for signal, direction in {**REFERENCE_SIGNALS, **PHYSICAL_SIGNALS}.items():
        s, v = series(arm, signal, steps)
        out["signals"].append(describe(signal, direction, s, v))
    return out


def authority(label: str, relative: str) -> dict[str, Any]:
    arm = load_arm(relative)
    if arm is None:
        return {"arm": label, "error": f"no observer jsonl under {relative}"}
    lam = arm["lambdas"]
    steps = sorted(set(arm["observer"]) & set(lam))
    high = [s for s in steps if lam[s] >= 0.95]
    if not high:
        return {"arm": label, "error": "lambda never reached 0.95"}
    descent_start = high[-1] + 1
    window = [s for s in steps if s >= descent_start]
    before = [s for s in steps if descent_start - 300 <= s < descent_start]
    last = window[-300:] if len(window) >= 300 else window
    out = {
        "arm": label,
        "branch": arm["branch"],
        "descent_start_iteration": descent_start,
        "window_iterations": len(window),
        "lambda_at_descent_start": round(lam[descent_start] if descent_start in lam else lam[window[0]], 4),
        "lambda_final": round(lam[window[-1]], 4),
        "signals": [],
    }
    for signal, direction in {**REFERENCE_SIGNALS, **PHYSICAL_SIGNALS}.items():
        s, v = series(arm, signal, window)
        keep = [(lam[i], x) for i, x in zip(s, v) if i in lam]
        xs = [a for a, _ in keep]
        ys = [b for _, b in keep]
        r = pearson(xs, ys)
        rho = SA.spearman(xs, ys)
        _, v_before = series(arm, signal, before)
        _, v_last = series(arm, signal, last)
        mean_before = statistics.fmean(v_before) if v_before else None
        mean_last = statistics.fmean(v_last) if v_last else None
        relief = None
        if mean_before not in (None, 0) and mean_last is not None:
            change = (mean_last - mean_before) / abs(mean_before)
            relief = change if direction == "up" else -change
        out["signals"].append(
            {
                "signal": signal,
                "improves": direction,
                "n": len(xs),
                "pearson_lambda_vs_signal": None if r is None else round(r, 4),
                "spearman_lambda_vs_signal": None if rho is None else round(rho, 4),
                # Positive: the signal IMPROVED as lambda was cut, i.e. cutting
                # difficulty relieved the controller's own error (a signal that
                # rewards evacuation). Negative: it got worse regardless.
                "relative_improvement_last300_vs_pre_descent": None if relief is None else round(relief, 4),
                "mean_pre_descent": None if mean_before is None else round(mean_before, 5),
                "mean_last": None if mean_last is None else round(mean_last, 5),
            }
        )
    return out


def ladder_cells() -> list[dict[str, Any]]:
    cells: dict[tuple[str, int, str], dict[str, Any]] = {}
    for root in RECEIPT_ROOTS:
        for path in glob.glob(str(root / "**" / "*.json"), recursive=True):
            try:
                receipt = json.loads(Path(path).read_text())
            except (OSError, ValueError):
                continue
            if receipt.get("kind") != "lucid_frozen_checkpoint_robustness_evaluation":
                continue
            for run in receipt.get("runs", {}).values():
                if not run.get("complete") or run.get("preset") not in PHYS_LAMBDA:
                    continue
                summary = run.get("summary") or {}
                if summary.get("success_rate") is None:
                    continue
                key = (run["mode"], int(run["checkpoint_seed"]), run["preset"])
                cells[key] = {
                    "mode": run["mode"],
                    "seed": int(run["checkpoint_seed"]),
                    "preset": run["preset"],
                    "lambda_eval": PHYS_LAMBDA[run["preset"]],
                    "success_rate": float(summary["success_rate"]),
                    **{k: summary.get(k) for k in EVAL_SIGNALS},
                    "receipt": path,
                }
    return sorted(cells.values(), key=lambda c: (c["mode"], c["seed"], c["lambda_eval"]))


def difficulty_response(cells: list[dict[str, Any]]) -> dict[str, Any]:
    arms: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for cell in cells:
        arms.setdefault((cell["mode"], cell["seed"]), []).append(cell)
    per_arm = []
    for (mode, seed), rows in sorted(arms.items()):
        if len(rows) < 7:
            continue
        lam = [r["lambda_eval"] for r in rows]
        succ = [r["success_rate"] for r in rows]
        entry: dict[str, Any] = {
            "arm": f"{mode}@s{seed}",
            "cells": len(rows),
            "success_spearman_vs_lambda": round(SA.spearman(lam, succ) or 0.0, 4),
            "signals": {},
        }
        for signal in EVAL_SIGNALS:
            vals = [r[signal] for r in rows]
            if any(v is None for v in vals):
                continue
            entry["signals"][signal] = {
                "spearman_vs_lambda": round(SA.spearman(lam, vals) or 0.0, 4),
                "spearman_vs_success": round(SA.spearman(vals, succ) or 0.0, 4),
                "at_lambda_0": round(vals[0], 5),
                "at_lambda_1": round(next(r[signal] for r in rows if r["lambda_eval"] == 1.0), 5),
                "at_lambda_2": round(vals[-1], 5),
            }
        per_arm.append(entry)
    pooled: dict[str, Any] = {}
    frontier = [c for c in cells if c["lambda_eval"] >= 1.25]
    for signal in EVAL_SIGNALS:
        allv = [(c[signal], c["success_rate"]) for c in cells if c[signal] is not None]
        fv = [(c[signal], c["success_rate"]) for c in frontier if c[signal] is not None]
        pooled[signal] = {
            "cells": len(allv),
            "spearman_vs_success_all_cells": round(SA.spearman([a for a, _ in allv], [b for _, b in allv]) or 0.0, 4),
            "spearman_vs_success_frontier_cells": round(SA.spearman([a for a, _ in fv], [b for _, b in fv]) or 0.0, 4),
            "per_arm_spearman_vs_success_min": min(
                (e["signals"][signal]["spearman_vs_success"] for e in per_arm if signal in e["signals"]), default=None
            ),
            "per_arm_spearman_vs_success_max": max(
                (e["signals"][signal]["spearman_vs_success"] for e in per_arm if signal in e["signals"]), default=None
            ),
        }
    return {"arms": per_arm, "pooled": pooled, "cells_used": len(cells)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    report: dict[str, Any] = {
        "kind": "lucid_physical_signal_admissibility_audit",
        "schema_version": 1,
        "question": (
            "Does a body-grounded signal (foot slip, actuator saturation, work, joint-limit "
            "proximity, undesired contact) satisfy what a difficulty gate needs -- anchored at "
            "fixed difficulty, responsive to difficulty at fixed competence, and responsive to "
            "the actuator with the right sign -- better than the latent gap, return or survival?"
        ),
        "caveats": [
            "training telemetry is a population mean per iteration over all 1,024 environments, "
            "so it mixes strata in stratified arms and mixes episodes at every stage of survival",
            "evaluator batch diagnostics include auto-reset environments after their scored "
            "episode terminates (receipt: not_yet_verified), so per-cell physical means are "
            "contaminated in the same way the tracking-error metrics are; the difficulty-response "
            "correlations are reported with that contamination, not corrected for it",
        ],
        "anchoring_at_fixed_difficulty": [anchoring(l, r) for l, (r, _) in SA.FIXED_DIFFICULTY_ARMS.items()],
        "authority_under_evacuation": [authority(l, r) for l, r in COLLAPSE_ARMS.items()],
    }
    cells = ladder_cells()
    report["difficulty_response_frozen_policies"] = difficulty_response(cells)

    def summarise(entries: list[dict[str, Any]], signal: str) -> dict[str, Any]:
        rows = [
            item for entry in entries for item in entry.get("signals", [])
            if item["signal"] == signal and item.get("spearman_vs_iteration") is not None
        ]
        if not rows:
            return {}
        rhos = [r["spearman_vs_iteration"] for r in rows]
        return {
            "arms": len(rows),
            "improves": rows[0]["improves"],
            "spearman_min": min(rhos),
            "spearman_max": max(rhos),
            "spearman_mean": round(statistics.fmean(rhos), 4),
            "sign_consistent_across_arms": len({math.copysign(1, r) for r in rhos}) == 1,
            "sign_matches_improvement_all_arms": all(r["sign_matches_improvement"] for r in rows),
            "monotone_frac_mean": round(statistics.fmean(r["monotone_frac_directional"] for r in rows), 4),
            "reversals_mean": round(statistics.fmean(r["reversals"] for r in rows), 2),
            "late_quarter_range_frac_mean": round(
                statistics.fmean(r["late_quarter_range_frac"] for r in rows if r["late_quarter_range_frac"] is not None), 4
            ),
        }

    report["verdict_anchoring"] = {
        s: summarise(report["anchoring_at_fixed_difficulty"], s) for s in {**REFERENCE_SIGNALS, **PHYSICAL_SIGNALS}
    }

    def summarise_authority(signal: str) -> dict[str, Any]:
        rows = [
            item for entry in report["authority_under_evacuation"] for item in entry.get("signals", [])
            if item["signal"] == signal
        ]
        return {
            r_entry["arm"]: {
                "pearson": item["pearson_lambda_vs_signal"],
                "relief": item["relative_improvement_last300_vs_pre_descent"],
            }
            for r_entry in report["authority_under_evacuation"]
            for item in r_entry.get("signals", [])
            if item["signal"] == signal
        } if rows else {}

    report["verdict_authority"] = {s: summarise_authority(s) for s in {**REFERENCE_SIGNALS, **PHYSICAL_SIGNALS}}
    text = json.dumps(report, indent=2)
    if args.out:
        args.out.write_text(text)

    # Compact console view.
    print(f"{'signal':26s} {'dir':5s} {'rho_iter':>18s} {'mono':>6s} {'rev':>5s} {'late%':>6s} | {'r(lam) rg8601':>13s} {'relief':>7s} | {'r(lam) s4rg8600':>15s} {'relief':>7s}")
    for s in {**REFERENCE_SIGNALS, **PHYSICAL_SIGNALS}:
        a = report["verdict_anchoring"].get(s) or {}
        au = report["verdict_authority"].get(s) or {}
        rg = au.get("lucid_rg@s8601", {})
        s4 = au.get("lucid_s4_rg@s8600", {})
        if not a:
            print(f"{s:26s} (no data)")
            continue
        print(
            f"{s:26s} {a['improves']:5s} {a['spearman_min']:+.2f}..{a['spearman_max']:+.2f}({a['spearman_mean']:+.2f}) "
            f"{a['monotone_frac_mean']:6.2f} {a['reversals_mean']:5.1f} {100*a['late_quarter_range_frac_mean']:6.0f} | "
            f"{(rg.get('pearson') if rg.get('pearson') is not None else float('nan')):+13.3f} {(rg.get('relief') if rg.get('relief') is not None else float('nan')):+7.3f} | "
            f"{(s4.get('pearson') if s4.get('pearson') is not None else float('nan')):+15.3f} {(s4.get('relief') if s4.get('relief') is not None else float('nan')):+7.3f}"
        )
    print()
    dr = report["difficulty_response_frozen_policies"]
    print(f"frozen-policy ladders: {dr['cells_used']} cells, {len(dr['arms'])} arms with >=7 cells")
    for s, p in dr["pooled"].items():
        print(f"  {s:26s} rho(signal,success) all={p['spearman_vs_success_all_cells']:+.3f} frontier={p['spearman_vs_success_frontier_cells']:+.3f} per-arm [{p['per_arm_spearman_vs_success_min']}, {p['per_arm_spearman_vs_success_max']}]")
    for e in dr["arms"]:
        print(f"  {e['arm']:22s} success~lambda {e['success_spearman_vs_lambda']:+.2f}  " + "  ".join(
            f"{s[:10]}: lam{v['spearman_vs_lambda']:+.2f}/succ{v['spearman_vs_success']:+.2f}" for s, v in e["signals"].items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
