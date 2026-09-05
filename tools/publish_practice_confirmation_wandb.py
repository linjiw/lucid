#!/usr/bin/env python3
"""Publish the three-seed practice study and frozen evaluation to one W&B report.

Training is replayed losslessly from the durable SONIC console logs into a
stable comparison schema. Frozen evaluation is replayed from the completed
analysis receipt. The derived runs are presentation artifacts; the source logs,
checkpoints, and evaluation receipts remain the evidence of record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import publish_effort_barrier_wandb as LOGS

ROOT = Path("/home/linjiw/lucid")
DATA = Path("/home/linjiw/lucid-sonic")
GROUP_TRAIN = "practice-allocation-confirmation-train-20260904"
GROUP_EVAL = "practice-allocation-confirmation-eval-20260904"
REPORT_TITLE = "LUCID Practice Allocation — Three-Seed Push Confirmation"
ARMS = {
    "prac_null": {"label": "Null allocation", "color": "#7f7f7f"},
    "prac_push": {"label": "Push 3× practice", "color": "#e45756"},
    "prac_easy": {"label": "Manageable 3× placebo", "color": "#4c78a8"},
}
LOG_DIRS = {
    8600: DATA / "outputs/lucid_practice_allocation_ne1024_20260903_052617",
    8601: DATA / "outputs/practice_allocation_confirmation_20260904/s8601",
    8602: DATA / "outputs/practice_allocation_confirmation_20260904/s8602",
}
EXPERIMENTS = {
    8600: "curriculum_comparison_ne1024_20260903_052619",
    8601: "curriculum_comparison_ne1024_20260904_152713",
    8602: "curriculum_comparison_ne1024_20260904_184159",
}
CELL_ORDER = [
    "phys_000",
    "phys_100",
    "phys_150",
    "phys_200",
    "ch_push_200",
    "ch_push_300",
    "ch_mass_300",
    "ch_com_300",
    "ch_joint_300",
    "ch_fric_150",
    "ch_push_fric_300_150",
    "ch_push_350",
    "ch_push_fric_350_150",
]
EVAL_METRICS = (
    "success_rate",
    "progress_rate",
    "mpjpe_g",
    "mpjpe_l",
    "foot_slip_per_step_m",
    "undesired_contact_rate",
    "torque_saturation",
    "energy_proxy",
)
EVAL_TITLES = {
    "success_rate": "success rate",
    "progress_rate": "progress rate",
    "mpjpe_g": "global MPJPE (mm)",
    "mpjpe_l": "local MPJPE (mm)",
    "foot_slip_per_step_m": "foot slip per step (m)",
    "undesired_contact_rate": "non-allowed contact-sensor rate (audit proxy)",
    "torque_saturation": "torque saturation fraction",
    "energy_proxy": "mean absolute mechanical-power proxy",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_log(seed: int, mode: str) -> Path:
    path = LOG_DIRS[seed] / f"{EXPERIMENTS[seed]}_s{seed}_{mode}.log"
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def trailing(rows: list[dict[str, float]], key: str, window: int = 50) -> float | None:
    values = [float(row[key]) for row in rows if key in row][-window:]
    return statistics.fmean(values) if len(values) == window else None


def training_source_audit() -> dict[str, Any]:
    runs: dict[str, Any] = {}
    all_keys: set[str] = set()
    for seed in (8600, 8601, 8602):
        for mode in ARMS:
            path = source_log(seed, mode)
            rows = LOGS.parse_log(path, allow_compatible_consecutive_duplicates=True)
            keys = sorted({key for row in rows for key in row if key != "iteration"})
            all_keys.update(keys)
            runs[f"{seed}/{mode}"] = {
                "source_log": str(path),
                "source_log_sha256": sha256(path),
                "canonical_iteration_rows": len(rows),
                "first_iteration": int(rows[0]["iteration"]),
                "last_iteration": int(rows[-1]["iteration"]),
                "scalar_count": len(keys),
                "trailing50_at_h1500": {
                    key: trailing(rows, key)
                    for key in (
                        "Env/Episode_Termination/time_out",
                        "Train/mean_rewards",
                        "Train/mean_length",
                    )
                },
            }
    return {
        "mirrored_rich_blocks_canonicalized": (
            "compatible adjacent fragments are merged; conflicting repeats are rejected"
        ),
        "all_logged_scalars_published": True,
        "scalar_keys": sorted(all_keys),
        "runs": runs,
    }


def training_rows() -> dict[tuple[int, str], list[dict[str, float]]]:
    return {
        (seed, mode): LOGS.parse_log(
            source_log(seed, mode), allow_compatible_consecutive_duplicates=True
        )
        for seed in (8600, 8601, 8602)
        for mode in ARMS
    }


def plot_training_overview(output: Path) -> None:
    rows_by_run = training_rows()
    fig, axes = plt.subplots(2, 3, figsize=(15, 7), squeeze=False)
    for axis, key in zip(axes.flat, LOGS.PLOT_GROUPS["overview"]):
        for mode, meta in ARMS.items():
            traces = []
            x_ref = None
            for seed in (8600, 8601, 8602):
                x, y = LOGS.series(rows_by_run[(seed, mode)], key)
                smooth = LOGS.rolling_mean(y)
                axis.plot(x, smooth, color=meta["color"], alpha=0.22, linewidth=0.8)
                x_ref = x if x_ref is None else x_ref
                traces.append(smooth)
            stacked = np.stack(traces)
            mean = stacked.mean(axis=0)
            axis.fill_between(
                x_ref,
                stacked.min(axis=0),
                stacked.max(axis=0),
                color=meta["color"],
                alpha=0.10,
            )
            axis.plot(
                x_ref, mean, color=meta["color"], linewidth=1.9, label=meta["label"]
            )
        axis.set_title(LOGS.short_title(key), fontsize=10)
        axis.grid(alpha=0.2)
        axis.tick_params(labelsize=8)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.suptitle(
        "Practice-allocation training diagnostics · three seeds\n"
        "trailing-50 seed traces faint · three-seed mean solid · min–max band",
        fontsize=13,
    )
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, 0.91),
    )
    fig.supxlabel("continuation-training iteration")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_evaluation_summary(analysis: dict[str, Any], output: Path) -> None:
    fig, axes = plt.subplots(3, 3, figsize=(16, 11), squeeze=False)
    x = np.arange(len(CELL_ORDER))
    for axis, metric in zip(axes.flat, EVAL_METRICS):
        for mode, meta in ARMS.items():
            traces = np.asarray(
                [
                    [
                        analysis["cells"][preset][str(seed)][mode][metric]
                        for preset in CELL_ORDER
                    ]
                    for seed in (8600, 8601, 8602)
                ],
                dtype=float,
            )
            for trace in traces:
                axis.plot(x, trace, color=meta["color"], alpha=0.23, linewidth=0.8)
            axis.fill_between(
                x,
                traces.min(axis=0),
                traces.max(axis=0),
                color=meta["color"],
                alpha=0.10,
            )
            axis.plot(
                x,
                traces.mean(axis=0),
                color=meta["color"],
                linewidth=1.9,
                label=meta["label"],
            )
        axis.set_title(EVAL_TITLES[metric], fontsize=10)
        axis.grid(alpha=0.2)
        axis.tick_params(axis="y", labelsize=8)
        axis.set_xticks(x, [str(index + 1) for index in x], fontsize=7)
    axes.flat[-1].set_visible(False)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.suptitle(
        "Frozen 13-cell benchmark · 512 matched replicates per cell\n"
        "seed traces faint · three-seed mean solid · min–max band",
        fontsize=13,
    )
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, 0.925),
    )
    fig.supxlabel("cell index (ordered in the page caption and W&B report)")
    fig.tight_layout(rect=(0, 0.02, 1, 0.88))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)


def publish_training(entity: str, project: str) -> dict[str, str]:
    import wandb

    urls: dict[str, str] = {}
    api = wandb.Api(timeout=60)
    for seed in (8600, 8601, 8602):
        for mode, meta in ARMS.items():
            path = source_log(seed, mode)
            source_hash = sha256(path)
            rows = LOGS.parse_log(path, allow_compatible_consecutive_duplicates=True)
            run_id = f"prac-train-s{seed}-{mode.removeprefix('prac_')}-h1500-v1"
            try:
                existing = api.run(f"{entity}/{project}/{run_id}")
            except wandb.errors.CommError:
                existing = None
            if (
                existing is not None
                and existing.state == "finished"
                and existing.summary.get("source_log_sha256") == source_hash
                and existing.summary.get("last_logged_iteration") == 1500
            ):
                urls[f"{seed}/{mode}"] = existing.url
                continue
            run = wandb.init(
                entity=entity,
                project=project,
                id=run_id,
                resume="allow",
                name=f"{meta['label']} · s{seed} · h1500",
                group=GROUP_TRAIN,
                job_type="warm-start-practice-curve",
                tags=[
                    "lucid",
                    "practice-allocation",
                    "push-frontier",
                    "three-seed",
                    f"seed-{seed}",
                    mode,
                    "discovery" if seed == 8600 else "confirmation",
                ],
                config={
                    "checkpoint_seed": seed,
                    "mode": mode,
                    "role": "discovery" if seed == 8600 else "confirmation",
                    "num_envs": 1024,
                    "iterations": 1500,
                    "practice_fraction": 0.25,
                    "source_experiment": EXPERIMENTS[seed],
                    "source_log": str(path),
                    "source_log_sha256": source_hash,
                    "telemetry_source": "durable SONIC console scalar blocks",
                },
                notes=(
                    "Normalized, lossless replay of the original offline SONIC training log. "
                    "This run is a presentation artifact; the durable log and receipt are the "
                    "evidence of record."
                ),
                settings=wandb.Settings(mode="online"),
            )
            run.define_metric("iteration")
            run.define_metric("*", step_metric="iteration")
            for row in rows:
                run.log(row)
            run.summary["source_log_sha256"] = source_hash
            run.summary["last_logged_iteration"] = int(rows[-1]["iteration"])
            run.summary["scalar_count"] = len(
                {key for row in rows for key in row if key != "iteration"}
            )
            for key in (
                "Env/Episode_Termination/time_out",
                "Train/mean_rewards",
                "Train/mean_length",
            ):
                run.summary[f"trailing50/{key}"] = trailing(rows, key)
            urls[f"{seed}/{mode}"] = run.url
            run.finish()
    return urls


def eval_rows(analysis: dict[str, Any], seed: int, mode: str) -> list[dict[str, Any]]:
    rows = []
    for index, preset in enumerate(CELL_ORDER):
        cell = analysis["cells"][preset][str(seed)][mode]
        rows.append(
            {
                "cell_index": index,
                "cell/preset": preset,
                "cell/in_training_support": cell["in_training_support"],
                **{f"Eval/{metric}": cell[metric] for metric in EVAL_METRICS},
                **cell.get("reported_scalars", {}),
            }
        )
    return rows


def publish_evaluation(
    analysis: dict[str, Any], analysis_path: Path, entity: str, project: str
) -> dict[str, str]:
    import wandb

    analysis_hash = sha256(analysis_path)
    urls: dict[str, str] = {}
    api = wandb.Api(timeout=60)
    for seed in (8600, 8601, 8602):
        for mode, meta in ARMS.items():
            rows = eval_rows(analysis, seed, mode)
            run_id = f"prac-eval-s{seed}-{mode.removeprefix('prac_')}-13cell-v1"
            try:
                existing = api.run(f"{entity}/{project}/{run_id}")
            except wandb.errors.CommError:
                existing = None
            if (
                existing is not None
                and existing.state == "finished"
                and existing.summary.get("analysis_receipt_sha256") == analysis_hash
                and existing.summary.get("cell_count") == len(CELL_ORDER)
            ):
                urls[f"{seed}/{mode}"] = existing.url
                continue
            run = wandb.init(
                entity=entity,
                project=project,
                id=run_id,
                resume="allow",
                name=f"{meta['label']} · s{seed} · frozen 13-cell",
                group=GROUP_EVAL,
                job_type="frozen-practice-benchmark",
                tags=[
                    "lucid",
                    "practice-allocation",
                    "frozen-evaluation",
                    "three-seed",
                    f"seed-{seed}",
                    mode,
                ],
                config={
                    "checkpoint_seed": seed,
                    "evaluation_seed": 8700 + seed - 8600,
                    "mode": mode,
                    "cells": CELL_ORDER,
                    "episodes_per_cell": 512,
                    "analysis_receipt": str(analysis_path),
                    "analysis_receipt_sha256": analysis_hash,
                },
                notes=(
                    "Frozen-policy 13-cell benchmark replayed from the complete analysis "
                    "receipt. Each cell has 512 matched simulator replicates."
                ),
                settings=wandb.Settings(mode="online"),
            )
            run.define_metric("cell_index")
            run.define_metric("Eval/*", step_metric="cell_index")
            for row in rows:
                run.log(row)
            run.summary["macro_success_pts"] = analysis["macro_success_pts"][str(seed)][
                mode
            ]
            run.summary["analysis_receipt_sha256"] = analysis_hash
            run.summary["cell_count"] = len(CELL_ORDER)
            run.summary["reported_scalar_count"] = len(
                analysis["reported_scalar_audit"]["key_union"]
            )
            urls[f"{seed}/{mode}"] = run.url
            run.finish()
    return urls


def create_report(entity: str, project: str, analysis: dict[str, Any]) -> str:
    import wandb_workspaces.reports.v2 as wr

    colors = {
        f"prac-train-s{seed}-{mode.removeprefix('prac_')}-h1500-v1": wr.RunSettings(
            color=meta["color"]
        )
        for seed in (8600, 8601, 8602)
        for mode, meta in ARMS.items()
    }
    train = wr.Runset(
        entity=entity,
        project=project,
        name="Training curves · three seeds",
        filters=f"Group = '{GROUP_TRAIN}'",
        run_settings=colors,
        pinned_columns=["run:name", "config:checkpoint_seed", "config:mode"],
    )
    eval_runset = wr.Runset(
        entity=entity,
        project=project,
        name="Frozen 13-cell benchmark · three seeds",
        filters=f"Group = '{GROUP_EVAL}'",
        pinned_columns=["run:name", "config:checkpoint_seed", "config:mode"],
    )
    d1 = analysis["decisions"]["D1_push_practice_is_productive"]
    d2 = analysis["decisions"]["D2_selecting_push_beats_manageable_placebo"]
    scalar_keys = analysis["reported_scalar_audit"]["key_union"]
    blocks: list[Any] = [
        wr.MarkdownBlock(
            text=(
                "## Frozen reading contract\n"
                "Seeds 8601–8602 are the confirmation set; seed 8600 is discovery evidence. "
                "The independent unit is the solved origin policy plus continuation seed. "
                "Every frozen cell contains 512 matched simulator replicates of one "
                "hands-on-back clip. Training curves diagnose optimization; only frozen "
                "evaluation grades the decision.\n\n"
                f"**D1:** {d1['verdict']} (new-seed mean "
                f"{d1['confirmation_mean_pts']:+.2f} points).  "
                f"**D2:** {d2['verdict']} (new-seed mean "
                f"{d2['confirmation_mean_pts']:+.2f} points)."
            )
        ),
        wr.TableOfContents(),
        wr.H1(text="Training overview"),
        wr.PanelGrid(
            runsets=[train],
            panels=[
                wr.LinePlot(
                    title=LOGS.short_title(key),
                    x="iteration",
                    y=[key],
                    max_runs_to_show=9,
                    legend_position="south",
                    legend_template="${run:name}",
                    point_visualization_method="bucketing-gorilla",
                )
                for key in LOGS.PLOT_GROUPS["overview"]
            ],
        ),
    ]
    for group, keys in LOGS.PLOT_GROUPS.items():
        if group == "overview":
            continue
        blocks.extend(
            [
                wr.H1(text=f"Training · {group.title()}"),
                wr.PanelGrid(
                    runsets=[train],
                    hide_run_sets=True,
                    panels=[
                        wr.LinePlot(
                            title=LOGS.short_title(key),
                            x="iteration",
                            y=[key],
                            max_runs_to_show=9,
                            legend_position="south",
                            legend_template="${run:name}",
                            point_visualization_method="bucketing-gorilla",
                        )
                        for key in keys
                    ],
                ),
            ]
        )
    blocks.extend(
        [
            wr.H1(text="Frozen benchmark"),
            wr.MarkdownBlock(
                text=(
                    "Cell order: `"
                    + " → ".join(CELL_ORDER)
                    + "`. Success and progress are rates; MPJPE is millimetres. The "
                    "non-allowed-contact series is published for completeness but is an "
                    "audit proxy: the current net-contact signal has not been validated as "
                    "ground-only for this hands-on-back clip, so it does not grade decisions."
                )
            ),
            wr.PanelGrid(
                runsets=[eval_runset],
                panels=[
                    wr.LinePlot(
                        title=EVAL_TITLES[metric],
                        x="cell_index",
                        y=[f"Eval/{metric}"],
                        max_runs_to_show=9,
                        legend_position="south",
                        legend_template="${run:name}",
                        point_visualization_method="bucketing-gorilla",
                    )
                    for metric in EVAL_METRICS
                ],
            ),
        ]
    )
    metric_groups = (
        ("All-episode pose and dynamics", "eval/all/"),
        ("Success-conditioned pose and dynamics", "eval/success/"),
        ("Physical-quality telemetry", "eval/quality/"),
        ("Delay instrumentation", "eval/delay/"),
        ("Protocol scalars", "eval/protocol/"),
    )
    for title, prefix in metric_groups:
        keys = [key for key in scalar_keys if key.startswith(prefix)]
        if not keys:
            continue
        blocks.extend(
            [
                wr.H1(text=f"Frozen benchmark · {title}"),
                wr.PanelGrid(
                    runsets=[eval_runset],
                    hide_run_sets=True,
                    panels=[
                        wr.LinePlot(
                            title=key.removeprefix(prefix).replace("_", " "),
                            x="cell_index",
                            y=[key],
                            max_runs_to_show=9,
                            legend_position="south",
                            legend_template="${run:name}",
                            point_visualization_method="bucketing-gorilla",
                        )
                        for key in keys
                    ],
                ),
            ]
        )
    report = wr.Report(
        entity=entity,
        project=project,
        title=REPORT_TITLE,
        description=(
            "All training scalar curves and frozen outcome/quality metrics for null, push, "
            "and manageable-channel allocations across one discovery and two confirmation seeds."
        ),
        blocks=blocks,
        width="fluid",
    )
    report.save()
    return report.url


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--analysis",
        type=Path,
        default=ROOT
        / "receipts/analysis/lucid_practice_allocation_confirmation_20260905.json",
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        default=ROOT
        / "receipts/analysis/lucid_practice_allocation_wandb_20260905.json",
    )
    parser.add_argument(
        "--figure-dir",
        type=Path,
        default=ROOT / "site/img/practice_confirmation",
    )
    parser.add_argument("--entity", default="16726")
    parser.add_argument("--project", default="lucid-campaign")
    args = parser.parse_args()

    analysis = json.loads(args.analysis.read_text())
    if not analysis["instrument_audit"]["complete"]:
        raise ValueError("refusing to publish an incomplete evaluation matrix")
    if not analysis["reported_scalar_audit"][
        "all_expected_cells_have_reported_scalars"
    ]:
        raise ValueError(
            "refusing to publish an incomplete all-scalar evaluation matrix"
        )
    training_audit = training_source_audit()
    figure_paths = {
        "training_overview": args.figure_dir / "training_overview.webp",
        "frozen_summary": args.figure_dir / "frozen_summary.webp",
    }
    plot_training_overview(figure_paths["training_overview"])
    plot_evaluation_summary(analysis, figure_paths["frozen_summary"])
    training_urls = publish_training(args.entity, args.project)
    evaluation_urls = publish_evaluation(
        analysis, args.analysis, args.entity, args.project
    )
    report_url = create_report(args.entity, args.project, analysis)
    receipt = {
        "kind": "lucid_practice_allocation_wandb_publication",
        "schema_version": 1,
        "created_at": datetime.now().astimezone().isoformat(),
        "analysis": str(args.analysis),
        "analysis_sha256": sha256(args.analysis),
        "training_source_audit": training_audit,
        "figures": {
            name: {"path": str(path), "sha256": sha256(path)}
            for name, path in figure_paths.items()
        },
        "training_run_urls": training_urls,
        "evaluation_run_urls": evaluation_urls,
        "report_url": report_url,
        "telemetry_note": (
            "Training runs are lossless normalized replays from durable console logs; "
            "evaluation runs are lossless replays from the complete analysis receipt."
        ),
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
