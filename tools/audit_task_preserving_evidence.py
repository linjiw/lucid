"""Read-only recomputation of the historical retention evidence; launches no experiment."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(private_root: Path) -> dict:
    result = {"kind": "existing_data_audit", "campaigns": [], "rows": [], "gates": []}
    for seed, name in [(8600, "retention_screen_campaign_20260906_c"),
                       (8601, "retention_second_seed_20260907_c")]:
        base = private_root / "experiments" / name / "pilot"
        plan_path, receipt_path = base / "plan.json", base / "receipt.json"
        plan = json.loads(plan_path.read_text())
        receipt = json.loads(receipt_path.read_text())
        if sha(plan_path) != receipt["plan_sha256"] or receipt["status"] != "complete":
            raise ValueError(f"Plan binding or completeness failed: {name}")
        if set(receipt["cells"]) != {c["id"] for c in plan["cells"]}:
            raise ValueError("Cell inventory differs")
        for cell in plan["cells"]:
            record = receipt["cells"][cell["id"]]
            if record["status"] != "complete":
                raise ValueError(f"Incomplete cell: {cell['id']}")
            if cell["kind"] != "evaluation":
                continue
            p = Path(cell["output"]) / "metrics_eval.json"
            if sha(p) != record["validation"]["metrics_sha256"]:
                raise ValueError(f"Metric hash mismatch: {p}")
            episodes = json.loads(p.read_text())["eval/qualified/episodes"]
            if len(episodes) != 512 or len({e["motion_index"] for e in episodes}) != 512:
                raise ValueError("Expected 512 unique aliases")
            if any(e["valid_samples"] <= 0 for e in episodes):
                raise ValueError("Missing scored samples")
            qualified = [bool(e["completed"] and e["global_mpjpe_mm"] <= 600
                              and e["local_mpjpe_mm"] <= 50) for e in episodes]
            if qualified != [e["tracking_qualified"] for e in episodes]:
                raise ValueError("Qualification does not match frozen thresholds")
            result["rows"].append({
                "seed": seed, "arm": cell["arm"], "iteration": cell["checkpoint_iteration"],
                "condition": cell["preset"], "metrics_path": str(p), "metrics_sha256": sha(p),
                "checkpoint_sha256_recorded": record["validation"]["checkpoint_sha256"],
                "n": len(episodes), "completion": statistics.fmean(e["completed"] for e in episodes),
                "qualification": statistics.fmean(qualified),
                "global_mm": statistics.fmean(e["global_mpjpe_mm"] for e in episodes),
                "local_mm": statistics.fmean(e["local_mpjpe_mm"] for e in episodes)})
        result["campaigns"].append({"seed": seed, "name": name, "cells": len(plan["cells"]),
            "plan_sha256": sha(plan_path), "receipt_sha256": sha(receipt_path),
            "origin_checkpoint_reported": plan["origin_checkpoint"],
            "anchor_sha256_reported": plan["buffer_sha256"]})
    rows = result["rows"]
    for seed in [8600, 8601]:
        origin = {r["condition"]: r for r in rows if r["seed"] == seed and r["arm"] == "origin"}
        for arm in (["R0", "R1", "R2"] if seed == 8600 else ["R0", "R1"]):
            for iteration in [250, 500, 1000, 1500, 2000]:
                panel = {r["condition"]: r for r in rows if (r["seed"], r["arm"], r["iteration"]) == (seed, arm, iteration)}
                changes = [100 * (panel[c][k] / origin[c][k] - 1)
                           for c in ["phys_000", "phys_100"] for k in ["global_mm", "local_mm"]]
                losses = [100 * (origin[c]["completion"] - panel[c]["completion"])
                          for c in ["phys_000", "phys_100"]]
                hard = ["ch_push_350", "ch_push_fric_350_150"]
                result["gates"].append({"seed": seed, "arm": arm, "iteration": iteration,
                    "max_error_increase_percent": max(changes), "max_completion_loss_pp": max(losses),
                    "pass": max(changes) <= 10 + 1e-10 and max(losses) <= 2 + 1e-10,
                    "nominal_global_increase_percent": 100*(panel['phys_000']['global_mm']/origin['phys_000']['global_mm']-1),
                    "hard_gain_pp": 100*statistics.fmean(panel[c]['qualification']-origin[c]['qualification'] for c in hard)})
    p = private_root / 'manifests/ratchet_confirmation_20260831/lucid_ratchet_confirmation_analysis.json'
    d = json.loads(p.read_text())['ratchet_vs_fixed']['success_rate']['frontier_auc']['per_seed']
    delta = [100*(v['ratchet']-v['fixed']) for v in d.values()]
    mean, sd = statistics.fmean(delta), statistics.stdev(delta)
    # Student-t 0.95 quantile with exactly two degrees of freedom.
    result['ratchet'] = {'source': str(p), 'sha256': sha(p), 'paired_deltas_pp': delta,
        'mean_pp': mean, 'sample_sd_pp': sd, 'one_sided_95_lower_pp': mean-2.919985580355516*sd/(3**0.5),
        'scope': 'Recomputed from aggregate per-policy AUCs; raw simulator trajectories not re-evaluated'}
    result['scope'] = ('Metric and plan hashes rechecked; episode metrics reaggregated. '
                       'Does not rerun simulation, rehash every model, establish perturbation-stream '
                       'identity, verify localization, or establish recovery.')
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--private-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = audit(args.private_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"panels": len(result["rows"]), "episodes": sum(r['n'] for r in result['rows']),
        "endpoints": [g for g in result['gates'] if g['iteration'] == 2000], 'ratchet': result['ratchet']}, indent=2))
