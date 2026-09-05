#!/usr/bin/env python3
"""Parse matched effort-barrier logs, plot every scalar, and optionally publish to W&B.

The SONIC console log is the durable source of record for these runs.  This tool
normalizes its Rich-formatted scalar blocks into one schema so that runs launched
on different days can be compared without relying on a surviving temporary W&B
offline directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
ITERATION_RE = re.compile(r"Learning iteration\s+(\d+)")
NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
SCALAR_RE = re.compile(rf"^\s*│\s*(.+?):\s*({NUMBER})(?:s)?\s*│\s*$")
COMPUTE_RE = re.compile(rf"Computation:\s*({NUMBER})\s*steps/s")
COLLECTION_RE = re.compile(rf"Collection:\s*({NUMBER})s")
LEARNING_RE = re.compile(rf"Learning\s+({NUMBER})s")

KEY_MAP = {
    "Mean action noise std": "Train/mean_action_noise_std",
    "Mean entropy": "Train/mean_entropy",
    "Mean rewards": "Train/mean_rewards",
    "Mean length": "Train/mean_length",
    "Total episodes": "Counters/total_episodes",
    "Total timesteps": "Counters/total_timesteps",
    "Iteration time": "Perf/iteration_time_s",
    "Total time": "Perf/total_time_s",
    "ETA": "Perf/eta_s",
}

RUNS = {
    "nominal": {
        "label": "Nominal (historical)",
        "color": "#7f7f7f",
        "log": Path(
            "/home/linjiw/lucid-sonic/outputs/"
            "curriculum_comparison_ne1024_20260829_000249_s8600_off.log"
        ),
        "wandb_id": "effort-nominal-s8600-h6000-historical-20260829",
        "effort_scale": 1.00,
        "source_experiment": "curriculum_comparison_ne1024_20260829_000249",
        "checkpoint": Path(
            "/home/linjiw/lucid/GR00T-WholeBodyControl/logs_rl/lucid-campaign/manager/"
            "universal_token/all_modes/sonic_release_test-20260829_000251/model_step_006000.pt"
        ),
    },
    "point_030": {
        "label": "Point 0.30",
        "color": "#e45756",
        "log": Path(
            "/home/linjiw/lucid-sonic/outputs/effort_barrier_point030_phase2/"
            "curriculum_comparison_ne1024_20260904_080627_s8600_act_point.log"
        ),
        "wandb_id": "effort-p030-s8600-h6000-20260904",
        "effort_scale": 0.30,
        "source_experiment": "curriculum_comparison_ne1024_20260904_080627",
        "checkpoint": Path(
            "/home/linjiw/lucid/GR00T-WholeBodyControl/logs_rl/lucid-campaign/manager/"
            "universal_token/all_modes/sonic_release_test-20260904_080628/model_step_006000.pt"
        ),
    },
    "point_040": {
        "label": "Point 0.40",
        "color": "#4c78a8",
        "log": Path(
            "/home/linjiw/lucid-sonic/outputs/effort_barrier_point040_phase2/"
            "curriculum_comparison_ne1024_20260903_175242_s8600_act_point.log"
        ),
        "wandb_id": "effort-p040-s8600-h6000-20260904",
        "effort_scale": 0.40,
        "source_experiment": "curriculum_comparison_ne1024_20260903_175242",
        "checkpoint": Path(
            "/home/linjiw/lucid/GR00T-WholeBodyControl/logs_rl/lucid-campaign/manager/"
            "universal_token/all_modes/sonic_release_test-20260903_175244/model_step_006000.pt"
        ),
    },
}

WANDB_REPORT_URL = (
    "https://wandb.ai/16726/lucid-campaign/reports/"
    "LUCID-Effort-Barrier-—-Point-0.30-vs-0.40--VmlldzoxNzg3MTQ2NA=="
)

PLOT_GROUPS = {
    "overview": [
        "Env/Episode_Termination/time_out",
        "Train/mean_rewards",
        "Train/mean_length",
        "Env/Metrics/motion/error_body_pos",
        "Env/Metrics/motion/error_joint_pos",
        "Env/Metrics/motion/error_body_ang_vel",
    ],
    "rewards": [
        "Env/Episode_Reward/tracking_anchor_pos",
        "Env/Episode_Reward/tracking_anchor_ori",
        "Env/Episode_Reward/tracking_relative_body_pos",
        "Env/Episode_Reward/tracking_relative_body_ori",
        "Env/Episode_Reward/tracking_body_linvel",
        "Env/Episode_Reward/tracking_body_angvel",
        "Env/Episode_Reward/tracking_vr_5point_local",
        "Env/Episode_Reward/action_rate_l2",
        "Env/Episode_Reward/joint_limit",
        "Env/Episode_Reward/undesired_contacts",
        "Env/Episode_Reward/anti_shake_ang_vel",
        "Env/Episode_Reward/feet_acc",
    ],
    "tracking": [
        "Env/Metrics/motion/error_anchor_pos",
        "Env/Metrics/motion/error_anchor_rot",
        "Env/Metrics/motion/error_anchor_lin_vel",
        "Env/Metrics/motion/error_anchor_ang_vel",
        "Env/Metrics/motion/error_body_pos",
        "Env/Metrics/motion/error_body_rot",
        "Env/Metrics/motion/error_joint_pos",
        "Env/Metrics/motion/error_joint_vel",
        "Env/Metrics/motion/error_body_lin_vel",
        "Env/Metrics/motion/error_body_ang_vel",
    ],
    "terminations": [
        "Env/Episode_Termination/time_out",
        "Env/Episode_Termination/anchor_pos",
        "Env/Episode_Termination/anchor_ori_full",
        "Env/Episode_Termination/ee_body_pos",
        "Env/Episode_Termination/foot_pos_xyz",
    ],
    "sampler": [
        "Env/adp_samp/num_episodes_min",
        "Env/adp_samp/num_episodes_max",
        "Env/adp_samp/num_episodes_mean",
        "Env/adp_samp/num_failures_min",
        "Env/adp_samp/num_failures_max",
        "Env/adp_samp/num_failures_mean",
        "Env/adp_samp/failure_rate_min",
        "Env/adp_samp/failure_rate_max",
        "Env/adp_samp/failure_rate_mean",
        "Env/adp_samp/prob_max",
        "Env/adp_samp/prob_min",
        "Env/adp_samp/prob_mean",
        "Env/adp_samp/prob_max_over_uniform",
        "Env/adp_samp/effective_num_bins",
        "Env/adp_samp/num_concentrated_bins",
        "Env/adp_samp/episodes_max_over_mean",
    ],
    "optimization": [
        "Train/mean_action_noise_std",
        "Train/mean_entropy",
        "Perf/steps_per_second",
        "Perf/collection_time_s",
        "Perf/learning_time_s",
        "Perf/iteration_time_s",
        "Perf/total_time_s",
        "Perf/eta_s",
        "Counters/total_episodes",
        "Counters/total_timesteps",
    ],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_key(key: str) -> str:
    key = " ".join(key.strip().split())
    return KEY_MAP.get(key, key)


def parse_log(
    path: Path, *, allow_compatible_consecutive_duplicates: bool = False
) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    row: dict[str, float] | None = None
    pending_compute = ""
    with path.open(errors="replace") as handle:
        for raw_line in handle:
            line = ANSI_RE.sub("", raw_line.rstrip("\n"))
            match = ITERATION_RE.search(line)
            if match:
                if row is not None:
                    rows.append(row)
                row = {"iteration": float(match.group(1))}
                pending_compute = ""
                continue
            if row is None:
                continue
            if "Computation:" in line:
                pending_compute = line
                compute = COMPUTE_RE.search(line)
                collection = COLLECTION_RE.search(line)
                if compute:
                    row["Perf/steps_per_second"] = float(compute.group(1))
                if collection:
                    row["Perf/collection_time_s"] = float(collection.group(1))
                continue
            if pending_compute and "Learning " in line:
                pending_compute += " " + line
                collection = COLLECTION_RE.search(pending_compute)
                learning = LEARNING_RE.search(pending_compute)
                if collection:
                    row["Perf/collection_time_s"] = float(collection.group(1))
                if learning:
                    row["Perf/learning_time_s"] = float(learning.group(1))
                pending_compute = ""
                continue
            scalar = SCALAR_RE.match(line)
            if scalar:
                row[canonical_key(scalar.group(1))] = float(scalar.group(2))
    if row is not None:
        rows.append(row)
    if not rows:
        raise ValueError(f"no iteration blocks parsed from {path}")
    if allow_compatible_consecutive_duplicates:
        # Some launcher logs mirror one Rich table as two adjacent fragments:
        # their shared fields agree and the second fragment supplies the remaining
        # columns. Merge only that compatible case; a conflicting repeat remains a
        # hard error so presentation can never choose silently between samples.
        canonical_rows: list[dict[str, float]] = []
        for row in rows:
            if canonical_rows and row["iteration"] == canonical_rows[-1]["iteration"]:
                conflicts = {
                    key: (canonical_rows[-1][key], value)
                    for key, value in row.items()
                    if key in canonical_rows[-1] and canonical_rows[-1][key] != value
                }
                if conflicts:
                    raise ValueError(
                        f"conflicting duplicate iteration {int(row['iteration'])} "
                        f"in {path}: {conflicts}"
                    )
                canonical_rows[-1].update(row)
                continue
            canonical_rows.append(row)
        rows = canonical_rows
    iterations = [int(row["iteration"]) for row in rows]
    if iterations != sorted(set(iterations)):
        raise ValueError(f"non-monotone or duplicated iteration blocks in {path}")
    return rows


def at_or_before(rows: list[dict[str, float]], horizon: int) -> list[dict[str, float]]:
    return [row for row in rows if row["iteration"] <= horizon]


def series(rows: list[dict[str, float]], key: str) -> tuple[np.ndarray, np.ndarray]:
    pairs = [
        (row["iteration"], row[key])
        for row in rows
        if key in row and math.isfinite(row[key])
    ]
    if not pairs:
        return np.array([]), np.array([])
    return np.asarray([p[0] for p in pairs]), np.asarray([p[1] for p in pairs])


def rolling_mean(values: np.ndarray, window: int = 50) -> np.ndarray:
    if values.size == 0:
        return values
    cumulative = np.cumsum(np.insert(values, 0, 0.0))
    out = np.empty(values.size, dtype=float)
    for index in range(values.size):
        start = max(0, index + 1 - window)
        out[index] = (cumulative[index + 1] - cumulative[start]) / (index + 1 - start)
    return out


def short_title(key: str) -> str:
    replacements = (
        ("Env/Episode_Reward/", "reward · "),
        ("Env/Metrics/motion/error_", "error · "),
        ("Env/Episode_Termination/", "termination · "),
        ("Env/adp_samp/", "sampler · "),
        ("Train/", "train · "),
        ("Perf/", "perf · "),
        ("Counters/", "counter · "),
    )
    for prefix, replacement in replacements:
        if key.startswith(prefix):
            return (replacement + key[len(prefix) :]).replace("_", " ")
    return key.replace("_", " ")


def plot_group(
    rows_by_run: dict[str, list[dict[str, float]]],
    keys: Iterable[str],
    output: Path,
    title: str,
    columns: int = 3,
) -> None:
    keys = [
        key
        for key in keys
        if any(series(rows, key)[0].size for rows in rows_by_run.values())
    ]
    nrows = math.ceil(len(keys) / columns)
    fig, axes = plt.subplots(
        nrows, columns, figsize=(5.0 * columns, 3.0 * nrows), squeeze=False
    )
    for axis, key in zip(axes.flat, keys):
        for run_id, rows in rows_by_run.items():
            x, y = series(rows, key)
            if not x.size:
                continue
            meta = RUNS[run_id]
            axis.plot(x, y, color=meta["color"], alpha=0.08, linewidth=0.55)
            axis.plot(
                x,
                rolling_mean(y),
                color=meta["color"],
                linewidth=1.65,
                label=meta["label"],
            )
        axis.set_title(short_title(key), fontsize=10)
        axis.set_xlim(0, 6000)
        axis.grid(alpha=0.22, linewidth=0.6)
        axis.tick_params(labelsize=8)
    for axis in axes.flat[len(keys) :]:
        axis.set_visible(False)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.suptitle(
        title + "\nraw traces faint · trailing-50 mean solid · equal horizon h6000",
        y=0.995,
        linespacing=1.35,
        fontsize=13,
    )
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, 0.915),
    )
    fig.supxlabel("PPO iteration")
    fig.tight_layout(rect=(0, 0, 1, 0.865))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight", dpi=150)
    plt.close(fig)


def metric_value(
    rows: list[dict[str, float]], iteration: int, key: str
) -> float | None:
    for row in rows:
        if int(row["iteration"]) == iteration:
            return row.get(key)
    return None


def trailing(
    rows: list[dict[str, float]], horizon: int, key: str, window: int = 50
) -> float:
    values = [row[key] for row in rows if row["iteration"] <= horizon and key in row][
        -window:
    ]
    if len(values) != window:
        raise ValueError(f"only {len(values)} values for {key} at h{horizon}")
    return float(np.mean(values))


def first_crossing(
    rows: list[dict[str, float]], key: str, threshold: float
) -> int | None:
    for row in rows:
        if row.get(key, -math.inf) >= threshold:
            return int(row["iteration"])
    return None


def first_trailing_crossing(
    rows: list[dict[str, float]], key: str, threshold: float, window: int = 50
) -> int | None:
    values: list[float] = []
    for row in rows:
        if key not in row:
            continue
        values.append(row[key])
        if len(values) >= window and float(np.mean(values[-window:])) >= threshold:
            return int(row["iteration"])
    return None


def summary_for(rows: list[dict[str, float]], horizon: int) -> dict[str, Any]:
    keys = sorted({key for row in rows for key in row if key != "iteration"})
    horizon_rows = [row for row in rows if row["iteration"] <= horizon]
    return {
        "first_logged_iteration": int(rows[0]["iteration"]),
        "last_logged_iteration": int(rows[-1]["iteration"]),
        "equal_comparison_horizon": horizon,
        "scalar_count": len(keys),
        "scalar_keys": keys,
        "iteration_1500": {
            key: metric_value(rows, 1500, key)
            for key in (
                "Env/Episode_Termination/time_out",
                "Train/mean_rewards",
                "Train/mean_length",
            )
        },
        "iteration_2000": {
            key: metric_value(rows, 2000, key)
            for key in (
                "Env/Episode_Termination/time_out",
                "Train/mean_rewards",
                "Train/mean_length",
            )
        },
        "iteration_6000": {
            key: metric_value(rows, 6000, key)
            for key in (
                "Env/Episode_Termination/time_out",
                "Train/mean_rewards",
                "Train/mean_length",
            )
        },
        "trailing_50_at_6000": {
            key: trailing(rows, horizon, key)
            for key in (
                "Env/Episode_Termination/time_out",
                "Train/mean_rewards",
                "Train/mean_length",
            )
        },
        "curve_mean_iterations_1_6000": {
            key: float(np.mean([row[key] for row in horizon_rows if key in row]))
            for key in (
                "Env/Episode_Termination/time_out",
                "Train/mean_rewards",
                "Train/mean_length",
            )
        },
        "first_trailing_50_crossings": {
            f"time_out_ge_{threshold:.2f}": first_trailing_crossing(
                rows, "Env/Episode_Termination/time_out", threshold
            )
            for threshold in (0.30, 0.50, 0.70, 0.90, 0.95)
        },
        "first_single_iteration_time_out_ge_070": first_crossing(
            rows, "Env/Episode_Termination/time_out", 0.70
        ),
        "first_trailing_50_time_out_ge_070": first_trailing_crossing(
            rows, "Env/Episode_Termination/time_out", 0.70
        ),
    }


def write_receipt(
    rows_by_run: dict[str, list[dict[str, float]]], output: Path, horizon: int
) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "kind": "lucid_effort_barrier_learning_curve_comparison",
        "schema_version": 1,
        "created_at": datetime.now().astimezone().isoformat(),
        "comparison_contract": {
            "horizon": horizon,
            "seed": 8600,
            "num_envs": 1024,
            "from_scratch": True,
            "motion": "walk_hands_on_back_loop_002__A066_M",
            "other_event_dr": "nominal",
            "other_actuator_dr": "nominal",
            "latency_steps": 0,
            "primary_matched_pair": "point 0.30 versus point 0.40",
            "primary_pair_only_intended_difference": "common all-joint effort scale: 0.30 versus 0.40",
            "historical_benchmark": "nominal effort scale 1.00 from the earlier 2026-08-29 campaign",
        },
        "configuration_audit": {
            "code_sha_both_point_runs": "cfd26b4a500af300727178778b2405ea0712b981",
            "point_pair_environment_optimizer_reward_termination_match": True,
            "non_learning_differences": [
                "timestamped output, branch, observer, and capsule paths",
                "snapshot bookkeeping: point 0.40 also listed h500/h1000; point 0.30 listed h8000",
                "YAML dictionary ordering of zero-valued term overrides",
            ],
            "learning_parameter_difference": "effort_limit_scale_range [0.40, 0.40] versus [0.30, 0.30]",
            "historical_nominal_caveat": (
                "same reported seed/environment/motion/no-DR contract and h6000 horizon, but "
                "launched on 2026-08-29 under an earlier code snapshot; use it as a benchmark, "
                "not as the claim-bearing randomized third arm"
            ),
        },
        "curve_rendering": {
            "raw": "shown faint",
            "smooth": "causal trailing-50 arithmetic mean",
            "x_axis": "PPO iteration",
            "all_logged_scalars_included": True,
        },
        "wandb": {
            "report_url": WANDB_REPORT_URL,
            "project": "16726/lucid-campaign",
            "group": "effort-point-barrier-h6000",
            "telemetry_note": "lossless normalized replay from the durable SONIC scalar logs",
        },
        "runs": {},
        "bounded_interpretation": (
            "The historical nominal arm takes off first, followed by point 0.40 and point 0.30. "
            "Both point settings learn directly from scratch at seed 8600 on one clip. Point 0.30 "
            "takes off later and remains worse at the equal h6000 horizon; this is "
            "a difficulty effect, not a curriculum-barrier result because the preregistered "
            "C1 direct-learning failure condition was false."
        ),
        "not_verified": [
            "between-training-seed variability",
            "unseen-motion generalization",
            "hardware transfer",
            "a curriculum benefit; no recovery curriculum is part of this comparison",
        ],
    }
    for run_id, rows in rows_by_run.items():
        meta = RUNS[run_id]
        receipt["runs"][run_id] = {
            "label": meta["label"],
            "effort_scale": meta["effort_scale"],
            "source_experiment": meta["source_experiment"],
            "source_log": str(meta["log"]),
            "source_log_sha256": sha256(meta["log"]),
            "checkpoint": str(meta["checkpoint"]),
            "checkpoint_sha256": sha256(meta["checkpoint"]),
            "wandb_id": meta["wandb_id"],
            "summary": summary_for(rows, horizon),
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def publish_wandb(
    rows_by_run: dict[str, list[dict[str, float]]],
    receipt: dict[str, Any],
    entity: str,
    project: str,
    horizon: int,
) -> dict[str, str]:
    import wandb

    urls: dict[str, str] = {}
    api = wandb.Api(timeout=60)
    for run_id, rows in rows_by_run.items():
        meta = RUNS[run_id]
        try:
            existing = api.run(f"{entity}/{project}/{meta['wandb_id']}")
        except wandb.errors.CommError:
            existing = None
        if (
            existing is not None
            and existing.state == "finished"
            and existing.summary.get("equal_comparison_horizon") == horizon
        ):
            urls[run_id] = existing.url
            continue
        run = wandb.init(
            entity=entity,
            project=project,
            id=meta["wandb_id"],
            resume="allow",
            name=f"{meta['label']} · direct · s8600 · h6000",
            group="effort-point-barrier-h6000",
            job_type="from-scratch-direct",
            tags=[
                "lucid",
                "barrier-study",
                "effort-point",
                "matched-h6000",
                "seed-8600",
            ],
            config={
                **receipt["comparison_contract"],
                "effort_scale": meta["effort_scale"],
                "source_experiment": meta["source_experiment"],
                "source_log_sha256": receipt["runs"][run_id]["source_log_sha256"],
                "checkpoint_sha256": receipt["runs"][run_id]["checkpoint_sha256"],
                "telemetry_source": "durable SONIC console scalar blocks",
                "curve_scope": "iterations 0 through 6000 inclusive",
            },
            notes=(
                "Matched LUCID common-point effort study. Replayed losslessly from the durable "
                "SONIC scalar log into a shared schema because the original temporary offline "
                "W&B directory was not durable for both runs."
            ),
        )
        run.define_metric("iteration")
        run.define_metric("*", step_metric="iteration")
        for row in at_or_before(rows, horizon):
            run.log(row)
        for key, value in receipt["runs"][run_id]["summary"].items():
            if not isinstance(value, (dict, list)):
                run.summary[key] = value
        run.summary["barrier_C1_at_iter1500"] = (
            receipt["runs"][run_id]["summary"]["iteration_1500"][
                "Env/Episode_Termination/time_out"
            ]
            < 0.30
        )
        run.summary["directly_learned"] = True
        urls[run_id] = run.url
        run.finish()
    return urls


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--horizon", type=int, default=6000)
    parser.add_argument(
        "--figure-dir",
        type=Path,
        default=Path("/home/linjiw/lucid/site/img/effort_barrier"),
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path(
            "/home/linjiw/lucid/receipts/analysis/"
            "effort_barrier_learning_curves_20260904.json"
        ),
    )
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--entity", default="16726")
    parser.add_argument("--project", default="lucid-campaign")
    args = parser.parse_args()

    rows_by_run = {
        run_id: at_or_before(parse_log(meta["log"]), args.horizon)
        for run_id, meta in RUNS.items()
    }
    parsed_keys = {key for rows in rows_by_run.values() for row in rows for key in row}
    declared_keys = {key for keys in PLOT_GROUPS.values() for key in keys} | {
        "iteration"
    }
    missing_from_plots = sorted(parsed_keys - declared_keys)
    missing_from_logs = sorted(declared_keys - parsed_keys)
    if missing_from_plots or missing_from_logs:
        raise ValueError(
            f"plot/schema mismatch; unplotted={missing_from_plots}, absent={missing_from_logs}"
        )

    for group, keys in PLOT_GROUPS.items():
        plot_group(
            rows_by_run,
            keys,
            args.figure_dir / f"training_{group}.webp",
            f"Effort barrier training · {group}",
        )
    receipt = write_receipt(rows_by_run, args.receipt, args.horizon)
    urls = (
        publish_wandb(rows_by_run, receipt, args.entity, args.project, args.horizon)
        if args.publish
        else {}
    )
    print(json.dumps({"receipt": str(args.receipt), "wandb_urls": urls}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
