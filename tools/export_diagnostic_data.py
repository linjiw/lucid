"""Export anonymous, compact diagnostic inputs from private receipts (no simulation).

The private source map is written beside, never inside, the portable data directory.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

import torch
import yaml

ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source_root, out = args.private_root, args.output
    out.mkdir(parents=True, exist_ok=True)
    sources, private = {}, {}

    def source(path: Path, expected: str | None = None) -> str:
        digest = sha(path)
        if expected is not None and digest != expected:
            raise ValueError(f"Source hash mismatch: {path}")
        sid = "source_" + digest
        sources[sid] = {"sha256": digest, "bytes": path.stat().st_size}
        private[sid] = str(path)
        return sid

    def read(path: Path, expected: str | None = None):
        source(path, expected)
        return json.loads(path.read_text())

    def write(name: str, data) -> None:
        raw = (
            json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
        ).encode()
        (out / name).write_bytes(gzip.compress(raw, mtime=0) if name.endswith(".gz") else raw)

    def anonymous(value):
        if isinstance(value, dict):
            return {anonymous(k): anonymous(v) for k, v in value.items()}
        if isinstance(value, list):
            return [anonymous(v) for v in value]
        if isinstance(value, str) and value.startswith("/"):
            return "private_path_" + hashlib.sha256(value.encode()).hexdigest()[:16]
        if isinstance(value, str) and ("wandb.ai/" in value or "github.com/linjiw" in value):
            return "private_online_provenance"
        return value

    campaigns = [
        (8600, "retention_screen_campaign_20260906_c"),
        (8601, "retention_second_seed_20260907_c"),
    ]
    panels, campaign_meta = [], []
    for seed, name in campaigns:
        base = source_root / "experiments" / name / "pilot"
        plan_path, receipt_path = base / "plan.json", base / "receipt.json"
        plan, receipt = read(plan_path), read(receipt_path)
        source(plan_path, receipt["plan_sha256"])
        if receipt["status"] != "complete" or any(
            r["status"] != "complete" for r in receipt["cells"].values()
        ):
            raise ValueError("Incomplete frozen campaign")
        campaign_meta.append(
            {
                "continuation_seed": seed,
                "plan_sha256": sha(plan_path),
                "source_commit": plan["git_sha"],
                "receipt_source": source(receipt_path),
                "cells": len(plan["cells"]),
                "panel_sha256": sha(Path(plan["panel_receipt"])),
            }
        )
        for cell in plan["cells"]:
            if cell["kind"] != "evaluation":
                continue
            record = receipt["cells"][cell["id"]]
            val = record["validation"]
            path = Path(cell["output"]) / "metrics_eval.json"
            metrics = read(path, val["metrics_sha256"])
            episodes = metrics["eval/qualified/episodes"]
            if len(episodes) != 512 or len({e["motion_index"] for e in episodes}) != 512:
                raise ValueError("Missing or duplicate episode identity")
            panels.append(
                {
                    "continuation_seed": seed,
                    "arm": cell["arm"],
                    "iteration": cell["checkpoint_iteration"],
                    "condition": cell["preset"],
                    "panel_id": f"retention_{seed}_512",
                    "evaluation_seed": plan["evaluation_seed"],
                    "checkpoint_sha256": val["checkpoint_sha256"],
                    "metrics_source": source(path),
                    "runtime_seconds": record["runtime"]["wall_seconds"],
                    "episodes": episodes,
                }
            )
    write("retention_episodes.json.gz", {"campaigns": campaign_meta, "panels": panels})

    inversion = read(ROOT / "receipts/analysis/lucid_return_inversion_20260901.json")
    historical, traces = [], []
    for pair in inversion["pairs"]:
        cells = {}
        checkpoints = []
        for filename in pair["sources"]:
            candidates = list((source_root / "manifests").rglob(filename))
            if len(candidates) != 1:
                raise ValueError(f"Expected one receipt: {filename}")
            receipt = read(candidates[0])
            for run in receipt["runs"].values():
                if run["mode"] != pair["mode"] or run["checkpoint_seed"] != pair["seed"]:
                    continue
                preset = run["preset"]
                if not preset.startswith("phys_"):
                    continue
                row = {
                    "success_rate": run["summary"]["success_rate"],
                    "progress_rate": run["summary"]["progress_rate"],
                    "checkpoint_sha256": run["checkpoint_sha256"],
                    "evaluation_seed": run["evaluation_seed"],
                    "receipt_source": source(candidates[0]),
                }
                if preset in cells and any(
                    cells[preset][k] != row[k] for k in row if k != "receipt_source"
                ):
                    raise ValueError(f"Conflicting historical cell: {pair['arm']} {preset}")
                cells[preset] = row
                checkpoint = Path(run["checkpoint"])
                if checkpoint not in checkpoints:
                    checkpoints.append(checkpoint)
        if not {"phys_125", "phys_150", "phys_175", "phys_200"}.issubset(cells):
            raise ValueError(f"Incomplete historical frontier {pair['arm']}")
        checkpoint = next(
            (p for p in checkpoints if list(p.parent.glob("curriculum_*.jsonl"))), checkpoint
        )
        states = list(checkpoint.parent.glob("curriculum_state*.json"))
        state = read(states[0]) if len(states) == 1 else None
        paths = list(checkpoint.parent.glob("curriculum_*.jsonl"))
        if len(paths) != 1:
            raise ValueError(f"Missing curriculum trace {pair['arm']}")
        source(paths[0])
        trace = [json.loads(line) for line in paths[0].read_text().splitlines() if line.strip()]
        compact = [
            {
                k: r[k]
                for k in (
                    "global_step",
                    "lambda",
                    "lambda_proposed",
                    "guard_tripped",
                    "shrink_blocked",
                )
                if k in r
            }
            for r in trace
        ]
        traces.append({"arm": pair["arm"], "source": source(paths[0]), "records": compact})
        historical.append(
            {
                **{
                    k: pair[k]
                    for k in ("arm", "mode", "seed", "terminal_return", "evacuated", "final_lambda")
                },
                "cells": cells,
                "checkpoint_iteration": 8000,
                "origin": "from_scratch",
                "controller_state": anonymous(state),
            }
        )
    write(
        "historical.json", {"rows": historical, "return_definition": inversion["return_definition"]}
    )
    write("range_traces.json.gz", traces)
    confirmation_path = (
        source_root
        / "manifests/ratchet_confirmation_20260831/lucid_ratchet_confirmation_analysis.json"
    )
    confirmation = read(confirmation_path)
    write(
        "tolerance.json",
        anonymous(
            {
                k: confirmation[k]
                for k in ("arms", "mechanism", "preregistered_decision", "frozen_contract")
            }
        ),
    )
    for filename, dest in [
        ("lucid_signal_audit_20260901.json", "signal_audit.json"),
        ("lucid_channel_attribution_20260902.json", "channel_sweep.json"),
        ("lucid_heldout_motion_20260901.json", "secondary_motion.json"),
    ]:
        path = ROOT / "receipts/analysis" / filename
        write(dest, anonymous(read(path)))

    mujoco = []
    for pushes, folder in [
        (False, "mujoco_sweep_nopush_20260902"),
        (True, "mujoco_sweep_20260902"),
    ]:
        for arm in (
            "off_s8600",
            "lucid_collapsed_s8601",
            "ratchet_s8601",
            "fixed_s8601",
            "fixed_s8600",
        ):
            for scale in ("1", "1.5", "2"):
                base = source_root / "artifacts" / folder / "runs" / arm / f"lam{scale}"
                paths = sorted(base.glob("seed*.json"))
                if len(paths) != 32:
                    raise ValueError(f"Missing MuJoCo draws: {base}")
                for path in paths:
                    payload = read(path)
                    mujoco.append(
                        {
                            "arm": arm,
                            "pushes": pushes,
                            "scale": float(scale),
                            "draw_id": path.stem,
                            "completed": not payload["result"]["fell"],
                            "source": source(path),
                        }
                    )
    write("mujoco.json", mujoco)
    anchor = (
        source_root
        / "experiments/retention_screen_campaign_20260906_c/collected_target_validation.json"
    )
    write("anchor_validation.json", anonymous(read(anchor)))
    buffer_path = (
        source_root / "experiments/retention_repair_campaign_20260906_a/collection/anchor_buffer.pt"
    )
    source(buffer_path, read(anchor)["buffer_sha256"])
    buffer = torch.load(buffer_path, map_location="cpu", weights_only=True)
    buffer_meta = {
        k: buffer[k]
        for k in (
            "origin_checkpoint_sha256",
            "origin_config_sha256",
            "origin_policy_sha256",
            "actor_contract",
            "phase_bins",
            "action_scale_contract",
            "collection_costs",
            "selection_seed",
            "per_condition_phase_bin",
        )
    }
    buffer_meta["records"] = len(buffer["records"])
    buffer_meta["condition_counts"] = {
        c: sum(r["condition"] == c for r in buffer["records"]) for c in ("phys_000", "phys_100")
    }
    encoder_path = source_root / "artifacts/lucid_encoder_debug512.pt"
    source(encoder_path)
    encoder = torch.load(encoder_path, map_location="cpu", weights_only=False)
    encoder_meta = {
        k: encoder[k]
        for k in (
            "num_joints",
            "window_length",
            "window_stride",
            "latent_dim",
            "hidden_channels",
            "control_hz",
            "num_train_windows",
            "clips_used",
            "seed",
            "epochs",
            "train_seconds",
        )
    }
    first_plan = read(
        source_root / "experiments/retention_screen_campaign_20260906_c/pilot/plan.json"
    )
    config_candidates = [
        Path(p)
        for p, digest in first_plan["inputs"].items()
        if digest == buffer["origin_config_sha256"]
    ]
    if len(config_candidates) != 1:
        raise ValueError("Origin configuration lineage ambiguous")
    source(config_candidates[0], buffer["origin_config_sha256"])
    config = yaml.safe_load(config_candidates[0].read_text())
    method = {
        "anchor": buffer_meta,
        "mismatch_encoder": encoder_meta,
        "origin_common_config": anonymous(
            {
                k: config[k]
                for k in (
                    "algo",
                    "manager_env",
                    "actor_prop_history_length",
                    "actor_actions_history_length",
                )
            }
        ),
        "configuration_scope": "Common reward/PPO/observation/physical settings. Controller identity comes from per-arm saved controller state, not copied config labels.",
    }
    method["executed_optimizer_start"] = []
    for seed, name in campaigns:
        plan = read(source_root / "experiments" / name / "pilot/plan.json")
        for cell in plan["cells"]:
            if cell["kind"] != "training":
                continue
            path = Path(cell["output"]) / "optimizer_history.json"
            payload = read(path)
            method["executed_optimizer_start"].append(
                {
                    "seed": seed,
                    "arm": cell["arm"],
                    "source": source(path),
                    **{
                        k: payload[k]
                        for k in (
                            "mode",
                            "learning_rates",
                            "learning_rate_policy",
                            "weights_equal_before_training",
                            "optimizer_state_entries",
                            "scheduler_restored",
                            "environment_restored",
                        )
                    },
                }
            )
    write("method.json", method)
    controls = []
    for campaign, arm in [
        ("quality_frontier_pilot_20260905_a", "origin"),
        ("quality_frontier_pilot_20260905_a", "gate"),
        ("initial_hold_pilot_20260905_a", "initial"),
        ("optimizer_history_pilot_20260905_a", "fresh"),
        ("optimizer_history_pilot_20260905_a", "restore"),
    ]:
        path = source_root / "experiments" / campaign / f"eval_{arm}_phys_000/metrics_eval.json"
        payload = read(path)
        controls.append(
            {
                "campaign": campaign,
                "arm": arm,
                "condition": "phys_000",
                "source": source(path),
                "legacy_global_mm": payload["eval/all/mpjpe_g"],
                "legacy_local_mm": payload["eval/all/mpjpe_l"],
                "completion": payload["eval/success/success_rate"],
            }
        )
    snapshot_path = ROOT / "site/data/recovery-progress-2026-09-07.json"
    snapshot = read(snapshot_path)["motion_screen"]
    secondary = [
        {
            k: r[k]
            for k in (
                "arm",
                "seed",
                "preset",
                "checkpoint_iteration",
                "checkpoint_sha256",
                "summary",
                "metrics_sha256",
            )
        }
        for r in snapshot["cells"]
        if r["motion"] == "control"
    ]
    cost = read(
        source_root / "experiments/retention_screen_campaign_20260906_c/analysis/analysis.json"
    )["training_costs"]
    write(
        "secondary_controls.json",
        {
            "legacy_controls": controls,
            "secondary_nominal_128": secondary,
            "secondary_snapshot_source": source(snapshot_path),
            "training_costs": anonymous(cost),
        },
    )
    write(
        "manifest.json",
        {
            "schema_version": 1,
            "sources": sources,
            "files": {
                p.name: sha(p)
                for p in sorted(out.iterdir())
                if p.is_file() and p.name != "manifest.json"
            },
            "scope": "Existing simulation records; no new experiment. Raw logs/checkpoints remain private.",
            "pairing": "Training-seed pairs only; perturbation streams not established as paired.",
        },
    )
    (out.parent / "private_source_map.json").write_text(json.dumps(private, indent=2) + "\n")
    print(
        f"Exported {len(panels)} continuation panels and {len(historical)} historical policies to {out}"
    )


if __name__ == "__main__":
    main()
