#!/usr/bin/env python3
"""Publish a small verified snapshot; exclude machine paths, datasets and weights."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import fmean


def sha(path):
    with Path(path).open("rb") as handle:
        digest = hashlib.sha256()
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
        return digest.hexdigest()


def verify(hashes):
    for path, digest in hashes.items():
        if sha(path) != digest:
            raise ValueError(f"Changed evidence: {path}")


def build(root, target):
    retention_root = root / "experiments/retention_screen_campaign_20260906_c/analysis"
    receipt = json.loads((retention_root / "receipt.json").read_text())
    if receipt["complete"] is not True:
        raise ValueError("Retention screen incomplete")
    verify(receipt["input_hashes"])
    verify(receipt.get("output_hashes", receipt.get("outputs", {})))
    retention = json.loads((retention_root / "analysis.json").read_text())
    rows = []
    origin = next(
        r for r in retention["rows"] if r["arm"] == "origin" and r["preset"] == "phys_000"
    )
    for arm in ["origin", "R0", "R1", "R2"]:
        endpoint = [
            r
            for r in retention["rows"]
            if r["arm"] == arm and r["iteration"] == (0 if arm == "origin" else 2000)
        ]
        nominal = next(r for r in endpoint if r["preset"] == "phys_000")
        rows.append(
            {
                "arm": arm,
                "global_mpjpe_mm": nominal["global_mpjpe_mm"],
                "local_mpjpe_mm": nominal["local_mpjpe_mm"],
                "global_change_pct": 100
                * (nominal["global_mpjpe_mm"] / origin["global_mpjpe_mm"] - 1),
                "hard_qualified_pct": 100
                * fmean(
                    r["tracking_success_rate"]
                    for r in endpoint
                    if r["preset"] in ["ch_push_350", "ch_push_fric_350_150"]
                ),
                "retained_all_sampled": (
                    True
                    if arm == "origin"
                    else retention["endpoints"][arm]["retained_at_all_sampled_checkpoints"]
                ),
            }
        )
    screen_root = root / "experiments/long_motion_screen_20260907_a"
    plan = json.loads((screen_root / "plan.json").read_text())
    status = json.loads((screen_root / "status.json").read_text())
    if (
        status["state"] != "complete"
        or len(status["cells"]) != 8
        or sha(screen_root / "plan.json") != status["plan_sha256"]
    ):
        raise ValueError("Incomplete or mismatched motion screen")
    verify(plan["inputs"])
    verify(plan["code_hashes"])
    cells = []
    for cell in plan["cells"]:
        saved = status["cells"][cell["id"]]
        if saved["state"] != "complete":
            raise ValueError("Incomplete cell")
        output = Path(cell["output"])
        verify(
            {
                str(output / "metrics_eval.json"): saved["validation"]["metrics_sha256"],
                str(output / "recovery/native_audit.jsonl"): saved["validation"]["measurement"][
                    "audit_sha256"
                ],
                str(output / "recovery/recovery_trace.jsonl"): saved["validation"]["measurement"][
                    "trace_sha256"
                ],
            }
        )
        metrics = json.loads((output / "metrics_eval.json").read_text())
        episodes = metrics["eval/qualified/episodes"]
        if len(episodes) != 128 or metrics["eval/qualified/missing_pose_episodes"] != 0:
            raise ValueError("Incomplete first-episode panel")
        for output_key, episode_key in [
            ("completion_rate", "completed"),
            ("tracking_success_rate", "tracking_qualified"),
            ("global_mpjpe_mm", "global_mpjpe_mm"),
            ("local_mpjpe_mm", "local_mpjpe_mm"),
        ]:
            if (
                abs(fmean(row[episode_key] for row in episodes) - saved["summary"][output_key])
                > 1e-9
            ):
                raise ValueError("Public summary does not reconcile with episodes")
        cells.append(
            {
                **{
                    k: cell[k]
                    for k in [
                        "motion",
                        "motion_key",
                        "arm",
                        "seed",
                        "preset",
                        "checkpoint_iteration",
                        "checkpoint_sha256",
                    ]
                },
                "summary": saved["summary"],
                "metrics_sha256": saved["validation"]["metrics_sha256"],
                "wandb_url": saved["wandb_url"],
            }
        )
    recovery_path = root / "experiments/recovery_execution_v2_20260907_a/analysis.json"
    recovery = json.loads(recovery_path.read_text())
    verify(recovery["input_hashes"])
    data = {
        "kind": "lucid_public_recovery_progress_v1",
        "snapshot_utc": datetime.now(timezone.utc).isoformat(),
        "live_feed": False,
        "scope": "SONIC development evidence; one trained origin; evaluation aliases are not independent trained policies.",
        "retention": {
            "rows": rows,
            "completed_at": receipt["completed_at"],
            "training_transitions_per_arm": 49152000,
            "analysis_sha256": sha(retention_root / "analysis.json"),
            "receipt_sha256": sha(retention_root / "receipt.json"),
        },
        "motion_screen": {
            "state": "complete",
            "completed_at": status["time_utc"],
            "plan_sha256": sha(screen_root / "plan.json"),
            "status_sha256": sha(screen_root / "status.json"),
            "source_commit": plan["commit"],
            "aliases_per_cell": 128,
            "cells": cells,
            "comparisons": status["comparisons"],
            "wandb_url": status["wandb_url"],
        },
        "recorder": {
            "cells_completed": recovery["cells_completed"],
            "nonzero_push_events": recovery["nonzero_push_events"],
            "analysis_sha256": sha(recovery_path),
            "scope": recovery["scope"],
        },
        "next_step": "Establish a high-quality shared multi-motion origin, then retention coverage, recovery calibration and matched feedback comparisons.",
    }
    text = json.dumps(data, indent=2, allow_nan=False) + "\n"
    if "/home/" in text or "/data/" in text:
        raise ValueError("Machine path in public snapshot")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    plot_retention(rows, target.parent.parent / "img/recovery")
    print(
        json.dumps(
            {
                "public_snapshot": str(target),
                "sha256": sha(target),
                "verified_motion_cells": len(cells),
            }
        )
    )


def plot_retention(rows, folder):
    """Export the same evidence as a shareable figure in three formats."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "svg.hashsalt": "lucid-retention-20260907",
            "font.size": 11,
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    fig, ax = plt.subplots(figsize=(10, 4.6), layout="constrained")
    ax.axvspan(-3, 10, color="#e8f0eb", zorder=0)
    ax.axvline(10, color="#176a64", lw=1.3, ls="--")
    colors = {"origin": "#58696d", "R0": "#9a432d", "R1": "#176a64", "R2": "#9a432d"}
    offsets = {"origin": (10, -8), "R0": (-25, 13), "R1": (15, -5), "R2": (12, 0)}
    for row in rows:
        arm = row["arm"]
        ax.scatter(
            row["global_change_pct"],
            row["hard_qualified_pct"],
            s=115 if arm == "R1" else 65,
            c=colors[arm],
            marker="D" if arm == "R1" else "o",
            zorder=3,
        )
        ax.annotate(
            "Origin" if arm == "origin" else arm,
            (row["global_change_pct"], row["hard_qualified_pct"]),
            xytext=offsets[arm],
            textcoords="offset points",
            weight="bold",
            color=colors[arm],
        )
    ax.text(11.5, 40.1, "+10% nominal global-error budget", color="#176a64", fontsize=10)
    ax.set(
        xlim=(-3, 85),
        ylim=(39, 56),
        xlabel="Nominal global MPJPE change versus origin (%)",
        ylabel="Hard-condition tracking-qualified execution (%)",
    )
    ax.grid(axis="y", color="#e1e7e4", lw=0.8)
    ax.set_axisbelow(True)
    folder.mkdir(parents=True, exist_ok=True)
    for ext in ["svg", "png", "pdf"]:
        fig.savefig(
            folder / f"retention_tradeoff.{ext}",
            dpi=180,
            metadata={"Creator": "LUCID verified development snapshot"},
        )
    svg = folder / "retention_tradeoff.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.source_root, args.output)
