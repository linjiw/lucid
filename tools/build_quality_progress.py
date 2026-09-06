#!/usr/bin/env python3
"""Export verified research summaries and a retention plot for the public site.

This builds static assets only; it never changes experiments or deploys the site.
Raw checkpoints, episode datasets, process IDs, and machine paths are not exported.
"""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def build(source_root: Path, site: Path) -> dict[str, Any]:
    provenance = []

    def read_analysis(label, filename="analysis.json"):
        folder = source_root / "analysis" / label
        receipt_path = folder / "receipt.json"
        receipt = json.loads(receipt_path.read_text())
        assert receipt["complete"] is True
        outputs = receipt.get("output_hashes", receipt.get("outputs", {}))
        path = folder / filename
        assert str(path) in outputs
        for name, digest in {**receipt.get("input_hashes", {}), **outputs}.items():
            assert sha(Path(name)) == digest, name
        provenance.append(
            {
                "analysis": label,
                "file": filename,
                "file_sha256": sha(path),
                "receipt_sha256": sha(receipt_path),
            }
        )
        return json.loads(path.read_text())

    frontier = read_analysis("quality_frontier_origin_audit_20260905")
    initial = read_analysis("initial_hold_retention_20260905_a")
    smoke = read_analysis("optimizer_history_smoke_20260905_a")
    probes = read_analysis("initial_hold_probe_budget_20260905_a")
    roots = read_analysis("frontier_root_bounds_20260905_a")
    initial_roots = read_analysis("initial_hold_root_bounds_20260905_a")
    campaign = source_root / "experiments/optimizer_history_campaign_20260905"
    state = json.loads((campaign / "status.json").read_text())
    parity_path = campaign / "smoke_noop_parity.json"
    parity = json.loads(parity_path.read_text())
    for field in ("policy_state_dict", "value_state_dict"):
        assert parity[field]["all_equal"] is True
    assert sha(Path(parity["reference"])) == parity["reference_sha256"]
    assert sha(Path(parity["current"])) == parity["current_sha256"]
    public = {
        "kind": "lucid_public_research_progress_v1",
        "snapshot_utc": state["time_utc"],
        "live_feed": False,
        "scope": "One development seed, one motion, simulation; 512 aliases are not independent motions.",
        "frontier_pilot": frontier,
        "fixed_initial_diagnostic": initial,
        "optimizer_smoke": smoke,
        "probe_budget": probes,
        "frontier_root_bounds": roots,
        "initial_root_bounds": initial_roots,
        "active_campaign": {
            "stage": state["stage"],
            "state": state["state"],
            "cells": state.get("cells", []),
            "warnings": state.get("warnings", []),
        },
        "smoke_parity": {
            field: parity[field] for field in ("policy_state_dict", "value_state_dict")
        },
        "provenance": provenance,
    }
    data = site / "data/research-progress-2026-09-06.json"
    data.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(public, indent=2, allow_nan=False) + "\n"
    assert "/home/" not in text and "/data/robotixx" not in text
    data.write_text(text)

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["svg.hashsalt"] = "lucid-retention-20260906"
    order = ["origin", "initial_250", "initial_500", "initial_1000", "initial_1500", "initial"]
    indexed = {r["arm"]: r for r in initial["rows"] if r["preset"] == "phys_000"}
    values = [indexed[arm]["legacy_global_mpjpe_mm"] for arm in order]
    steps = [0, 250, 500, 1000, 1500, 2000]
    threshold = 1.1 * values[0]
    fig, ax = plt.subplots(figsize=(10, 3.9))
    ax.axhline(threshold, color="#a8432b", linestyle="--", label="Origin +10% retention margin")
    ax.axhline(values[0], color="#5f6b7a", linestyle=":", label="Solved origin")
    ax.plot(steps, values, color="#2e5a87", linestyle="--", alpha=0.45, zorder=1)
    ax.scatter(
        steps, values, c=["#a8432b" if v > threshold else "#2e5a87" for v in values], s=65, zorder=2
    )
    for x, y in zip(steps, values):
        ax.annotate(
            f"{y:.2f}", (x, y), xytext=(0, 10), textcoords="offset points", ha="center", fontsize=10
        )
    ax.set(
        xticks=steps,
        ylim=(100, 210),
        xlabel="Training iteration · initial DR mixture held fixed",
        ylabel="Clean global MPJPE (mm)",
        title="Completion stays high while tracking drifts",
    )
    ax.grid(axis="y", alpha=0.2)
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    fig.tight_layout()
    dest = site / "img/quality_frontier"
    dest.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest / "initial_retention.svg", metadata={"Date": None})
    svg_path = dest / "initial_retention.svg"
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text().splitlines()) + "\n")
    fig.savefig(dest / "initial_retention.png", dpi=160)
    plt.close(fig)
    return public


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--site", type=Path, default=Path("site"))
    args = parser.parse_args()
    result = build(args.source_root, args.site)
    print(json.dumps({"snapshot_utc": result["snapshot_utc"], "state": result["active_campaign"]}))
