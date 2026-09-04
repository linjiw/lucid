#!/usr/bin/env python3
"""Compare all frozen effort-ladder metrics and publish the benchmark to W&B."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

OLD_MANIFEST = Path(
    "/home/linjiw/lucid-sonic/manifests/effort_point040_isolated_ladder_20260904/"
    "curriculum_robustness_ne512_20260904_074254.json"
)
NEW_MANIFEST_DIR = Path(
    "/home/linjiw/lucid-sonic/manifests/effort_point030_isolated_ladder_20260904"
)
GPU_AUDIT = Path(
    "/home/linjiw/lucid-sonic/outputs/effort_point030_isolated_ladder_20260904/"
    "gpu_audit_20260904_145313.log"
)
EFFORT_BY_PRESET = {
    "act_iso_off": 1.00,
    "act_iso_point_075": 0.75,
    "act_iso_point_050": 0.50,
    "act_iso_point_040": 0.40,
    "act_iso_point_035": 0.35,
    "act_iso_point_030": 0.30,
    "act_iso_point_025": 0.25,
}
POLICIES = {
    "nominal": {
        "label": "Nominal-trained",
        "color": "#7f7f7f",
        "manifest": "old",
        "mode": "act_off",
        "wandb_id": "effort-eval-nominal-s8600-h6000-20260904",
    },
    "point_040": {
        "label": "Point-0.40-trained",
        "color": "#4c78a8",
        "manifest": "old",
        "mode": "act_point",
        "wandb_id": "effort-eval-p040-s8600-h6000-20260904",
    },
    "point_030": {
        "label": "Point-0.30-trained",
        "color": "#e45756",
        "manifest": "new",
        "mode": "act_point",
        "wandb_id": "effort-eval-p030-s8600-h6000-20260904",
    },
}
REGIONS = ("", "_legs", "_vr_3points", "_other_upper_bodies", "_foot")
POSE_METRICS = tuple(
    f"eval/all/{metric}{region}"
    for metric in ("mpjpe_g", "mpjpe_l", "mpjpe_pa")
    for region in REGIONS
)
DYNAMICS_METRICS = tuple(
    f"eval/all/{metric}{region}"
    for metric in ("vel_dist", "accel_dist")
    for region in REGIONS
)
SUCCESS_CONDITIONED_METRICS = tuple(
    f"eval/success/{metric}{region}"
    for metric in ("mpjpe_g", "mpjpe_l", "mpjpe_pa", "vel_dist", "accel_dist")
    for region in REGIONS
)
QUALITY_METRICS = (
    "eval/quality/action_rate",
    "eval/quality/action_acceleration",
    "eval/quality/foot_slip_total_m",
    "eval/quality/foot_slip_per_step_m",
    "eval/quality/contact_impulse_total",
    "eval/quality/contact_force_peak",
    "eval/quality/undesired_contact_rate",
    "eval/quality/num_undesired_bodies",
    "eval/quality/torque_saturation",
    "eval/quality/joint_limit_proximity",
    "eval/quality/energy_proxy",
    "eval/quality/steps",
)
METRIC_GROUPS = {
    "completion": (
        "eval/success/success_rate",
        "eval/success/progress_rate",
    ),
    "all_episode_pose": POSE_METRICS,
    "all_episode_dynamics": DYNAMICS_METRICS,
    "quality": QUALITY_METRICS,
    "success_conditioned": SUCCESS_CONDITIONED_METRICS,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def newest_manifest(path: Path) -> Path:
    matches = sorted(path.glob("curriculum_robustness_ne512_*.json"))
    if not matches:
        raise FileNotFoundError(
            f"no completed point-0.30 evaluation manifest under {path}"
        )
    return matches[-1]


def load_rows(manifest_path: Path, mode: str) -> list[dict[str, float]]:
    manifest = json.loads(manifest_path.read_text())
    if not manifest.get("verified"):
        raise ValueError(f"evaluation is not fully verified: {manifest_path}")
    by_preset: dict[str, dict[str, Any]] = {}
    for run in manifest["runs"].values():
        if run["mode"] == mode:
            by_preset[run["preset"]] = run
    if set(by_preset) != set(EFFORT_BY_PRESET):
        raise ValueError(
            f"ladder mismatch for {mode}: got {sorted(by_preset)}, expected {sorted(EFFORT_BY_PRESET)}"
        )
    rows: list[dict[str, float]] = []
    for preset, effort in EFFORT_BY_PRESET.items():
        run = by_preset[preset]
        metrics = json.loads(Path(run["metrics_path"]).read_text())
        row: dict[str, float] = {"effort_scale": effort}
        for key, value in metrics.items():
            if isinstance(value, (int, float)) and math.isfinite(float(value)):
                row[key] = float(value)
        row["eval/success/success_count"] = round(
            row["eval/success/success_rate"] * manifest["protocol"]["num_envs"]
        )
        rows.append(row)
    return sorted(rows, key=lambda row: row["effort_scale"])


def short_title(key: str) -> str:
    prefixes = (
        ("eval/success/", "success · "),
        ("eval/all/", "all episodes · "),
        ("eval/quality/", "quality · "),
    )
    for prefix, replacement in prefixes:
        if key.startswith(prefix):
            return (replacement + key[len(prefix) :]).replace("_", " ")
    return key.replace("_", " ")


def plot_group(
    rows_by_policy: dict[str, list[dict[str, float]]],
    keys: tuple[str, ...],
    output: Path,
    title: str,
    columns: int = 3,
) -> None:
    keys = tuple(
        key
        for key in keys
        if any(any(key in row for row in rows) for rows in rows_by_policy.values())
    )
    nrows = math.ceil(len(keys) / columns)
    fig, axes = plt.subplots(
        nrows, columns, figsize=(5.0 * columns, 3.1 * nrows), squeeze=False
    )
    for axis, key in zip(axes.flat, keys):
        for policy_id, rows in rows_by_policy.items():
            points = [(row["effort_scale"], row[key]) for row in rows if key in row]
            if not points:
                continue
            x = np.asarray([point[0] for point in points])
            y = np.asarray([point[1] for point in points])
            meta = POLICIES[policy_id]
            axis.plot(
                x,
                y,
                marker="o",
                markersize=3.4,
                linewidth=1.55,
                color=meta["color"],
                label=meta["label"],
            )
        axis.set_title(short_title(key), fontsize=10)
        axis.set_xlim(0.23, 1.02)
        axis.set_xticks([0.25, 0.30, 0.35, 0.40, 0.50, 0.75, 1.00])
        axis.grid(alpha=0.22, linewidth=0.6)
        axis.tick_params(labelsize=8)
        if key.endswith(("success_rate", "progress_rate")):
            axis.set_ylim(-0.03, 1.03)
    for axis in axes.flat[len(keys) :]:
        axis.set_visible(False)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.suptitle(
        title
        + "\n512 matched replicates per point · h6000 checkpoints · all other DR nominal",
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
    fig.supxlabel("Frozen evaluation effort scale (left is harder)")
    fig.tight_layout(rect=(0, 0, 1, 0.865))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight", dpi=150)
    plt.close(fig)


def find_row(rows: list[dict[str, float]], effort: float) -> dict[str, float]:
    return next(row for row in rows if abs(row["effort_scale"] - effort) < 1e-8)


def write_receipt(
    rows_by_policy: dict[str, list[dict[str, float]]],
    manifests: dict[str, Path],
    output: Path,
) -> dict[str, Any]:
    policies: dict[str, Any] = {}
    for policy_id, rows in rows_by_policy.items():
        meta = POLICIES[policy_id]
        train_point = {"nominal": 1.0, "point_040": 0.40, "point_030": 0.30}[policy_id]
        at_train = find_row(rows, train_point)
        policies[policy_id] = {
            "label": meta["label"],
            "training_effort_scale": train_point,
            "wandb_id": meta["wandb_id"],
            "at_training_plant": {
                key: at_train.get(key)
                for key in (
                    "eval/success/success_count",
                    "eval/success/success_rate",
                    "eval/success/progress_rate",
                    "eval/all/mpjpe_g",
                    "eval/all/mpjpe_l",
                    "eval/quality/energy_proxy",
                    "eval/quality/torque_saturation",
                    "eval/quality/foot_slip_per_step_m",
                    "eval/quality/undesired_contact_rate",
                )
            },
            "ladder": rows,
        }
    receipt = {
        "kind": "lucid_effort_barrier_frozen_ladder_curve_comparison",
        "schema_version": 1,
        "created_at": datetime.now().astimezone().isoformat(),
        "protocol": {
            "checkpoint_horizon": 6000,
            "checkpoint_seed": 8600,
            "evaluation_seed": 8700,
            "replicates_per_cell": 512,
            "panel": "fresh-physics aliases of walk_hands_on_back_loop_002__A066_M",
            "effort_points": sorted(EFFORT_BY_PRESET.values()),
            "other_event_dr": "nominal",
            "other_actuator_dr": "nominal",
            "latency_steps": 0,
            "no_learning": True,
        },
        "source_manifests": {
            name: {"path": str(path), "sha256": sha256(path)}
            for name, path in manifests.items()
        },
        "execution_isolation": {
            "preflight_stable_idle_seconds": 60,
            "gpu_audit_path": str(GPU_AUDIT),
            "gpu_audit_sha256": sha256(GPU_AUDIT),
            "observed_gpu_pids": [
                413059,
                414457,
                416199,
                417527,
                418903,
                420360,
                421884,
            ],
            "unexpected_external_gpu_pids": [],
            "transient_empty_cmdline_reads": [413059, 421884],
            "accepted": True,
            "note": (
                "The two transient empty /proc cmdline reads resolved on the next sample to the "
                "first and seventh evaluator. Every observed CUDA PID subsequently matched the "
                "frozen point-0.30 checkpoint path; no external CUDA PID appeared."
            ),
        },
        "metric_families": {name: list(keys) for name, keys in METRIC_GROUPS.items()},
        "policies": policies,
        "bounded_interpretation": (
            "The ladder measures same-clip plant adaptation and robustness, not unseen-motion "
            "generalization. Success-conditioned metrics are undefined or selection-biased when "
            "completion is low; all-episode metrics remain the primary quality curves."
        ),
        "not_verified": [
            "between-checkpoint-seed variability",
            "unseen-motion generalization",
            "episode-masked contact-quality metrics",
            "hardware transfer",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def publish_wandb(
    rows_by_policy: dict[str, list[dict[str, float]]],
    receipt: dict[str, Any],
    entity: str,
    project: str,
) -> dict[str, str]:
    import wandb

    urls: dict[str, str] = {}
    for policy_id, rows in rows_by_policy.items():
        meta = POLICIES[policy_id]
        run = wandb.init(
            entity=entity,
            project=project,
            id=meta["wandb_id"],
            resume="allow",
            name=f"Frozen ladder · {meta['label']} · s8600 · h6000",
            group="effort-point-frozen-ladder-h6000",
            job_type="frozen-policy-eval",
            tags=[
                "lucid",
                "barrier-study",
                "effort-point",
                "frozen-eval",
                "matched-h6000",
            ],
            config={
                **receipt["protocol"],
                "policy": policy_id,
                "training_effort_scale": receipt["policies"][policy_id][
                    "training_effort_scale"
                ],
            },
            notes=(
                "Frozen-policy effort-only ladder. All non-target DR is nominal. Each row is "
                "512 fresh physics/noise replicates of the same training clip."
            ),
            settings=wandb.Settings(mode="online"),
        )
        run.define_metric("effort_scale")
        run.define_metric("*", step_metric="effort_scale")
        for row in rows:
            run.log(row)
        urls[policy_id] = run.url
        run.finish()
    return urls


def create_report(entity: str, project: str) -> str:
    import wandb_workspaces.reports.v2 as wr

    runset = wr.Runset(
        entity=entity,
        project=project,
        name="Frozen effort ladder · h6000",
        filters="Group = 'effort-point-frozen-ladder-h6000'",
        run_settings={
            meta["wandb_id"]: wr.RunSettings(color=meta["color"])
            for meta in POLICIES.values()
        },
        pinned_columns=["run:name", "config:training_effort_scale.value"],
    )
    blocks: list[Any] = [
        wr.MarkdownBlock(
            text=(
                "## Reading contract\n"
                "All policies are frozen h6000 checkpoints at seed 8600. Each effort point has "
                "512 matched fresh-physics replicates of the same hands-on-back clip; all other "
                "event and actuator DR is nominal and latency is zero. This measures plant "
                "adaptation, not unseen-motion or seed generalization. Success-conditioned metrics "
                "become selection-biased when completion falls; read all-episode curves first."
            )
        ),
        wr.TableOfContents(),
    ]
    for group, keys in METRIC_GROUPS.items():
        blocks.append(wr.H1(text=group.replace("_", " ").title()))
        blocks.append(
            wr.PanelGrid(
                runsets=[runset],
                hide_run_sets=group != "completion",
                panels=[
                    wr.LinePlot(
                        title=short_title(key),
                        x="effort_scale",
                        y=[key],
                        range_x=(0.23, 1.02),
                        max_runs_to_show=3,
                        legend_position="south",
                        legend_template="${run:name}",
                        point_visualization_method="bucketing-gorilla",
                    )
                    for key in keys
                ],
            )
        )
    report = wr.Report(
        entity=entity,
        project=project,
        title="LUCID Effort Barrier — Frozen h6000 Benchmark",
        description="All frozen-policy outcome and quality curves: nominal vs point 0.40 vs point 0.30 training.",
        blocks=blocks,
        width="fluid",
    )
    report.save()
    return report.url


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--point030-manifest", type=Path)
    parser.add_argument(
        "--figure-dir",
        type=Path,
        default=Path("/home/linjiw/lucid/site/img/effort_barrier"),
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path(
            "/home/linjiw/lucid/receipts/analysis/effort_barrier_frozen_ladder_curves_20260904.json"
        ),
    )
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--entity", default="16726")
    parser.add_argument("--project", default="lucid-campaign")
    args = parser.parse_args()

    manifests = {
        "point040_and_nominal": OLD_MANIFEST,
        "point030": args.point030_manifest or newest_manifest(NEW_MANIFEST_DIR),
    }
    rows_by_policy = {
        policy_id: load_rows(
            manifests[
                meta["manifest"] == "new" and "point030" or "point040_and_nominal"
            ],
            meta["mode"],
        )
        for policy_id, meta in POLICIES.items()
    }
    for group, keys in METRIC_GROUPS.items():
        plot_group(
            rows_by_policy,
            keys,
            args.figure_dir / f"frozen_{group}.webp",
            f"Effort barrier frozen benchmark · {group.replace('_', ' ')}",
        )
    receipt = write_receipt(rows_by_policy, manifests, args.receipt)
    urls = (
        publish_wandb(rows_by_policy, receipt, args.entity, args.project)
        if args.publish
        else {}
    )
    report_url = create_report(args.entity, args.project) if args.publish else ""
    receipt["wandb"] = {"run_urls": urls, "report_url": report_url}
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                "receipt": str(args.receipt),
                "wandb_urls": urls,
                "report_url": report_url,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
