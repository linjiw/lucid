"""Build paper figures using only the declared anonymous data package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import fmean

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from analyze_diagnostic_data import GLOBAL_GRID, LOCAL_GRID, analyze, auc, read_data

ROOT = Path(__file__).resolve().parents[1]
COLORS = {"R0": "#b44236", "R1": "#167887", "R2": "#a8781c"}
MODES = {
    "lucid_rg": ("A", "o", "#b44236"),
    "lucid_s4_rg": ("B", "s", "#a8781c"),
    "lucid_ratchet_rg": ("N", "^", "#167887"),
    "fixed": ("F", "D", "#625e92"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "paper/figures")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.size": 8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.hashsalt": "diagnostic-20260908",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )

    def save(fig, name):
        fig.tight_layout()
        for suffix in ("pdf", "svg", "png"):
            metadata = (
                {"CreationDate": None, "ModDate": None}
                if suffix == "pdf"
                else ({"Date": None} if suffix == "svg" else {})
            )
            fig.savefig(
                args.output / f"{name}.{suffix}", dpi=200, bbox_inches="tight", metadata=metadata
            )
        plt.close(fig)

    historical = read_data(args.data, "historical.json")["rows"]
    traces = read_data(args.data, "range_traces.json.gz")
    analysis = analyze(args.data)
    fig, axs = plt.subplots(1, 3, figsize=(7, 2.5), gridspec_kw={"width_ratios": [1, 1, 1.35]})
    for ax, mode in zip(axs, ("lucid_rg", "lucid_s4_rg")):
        for seed, color in zip((8600, 8601, 8602), ("#167887", "#b44236", "#625e92")):
            trace = next(t for t in traces if t["arm"] == f"{mode}@s{seed}")["records"]
            ax.plot(
                [r["global_step"] for r in trace],
                [r["lambda"] for r in trace],
                color=color,
                label=str(seed),
                lw=1,
            )
        ax.set(
            xlabel="Training iteration",
            ylabel="Range scale λ",
            ylim=(-0.03, 1.06),
            title=f"Variant {MODES[mode][0]}",
        )
        ax.set_xticks([0, 4000, 8000], ["0", "4k", "8k"])
    axs[0].legend(frameon=False, fontsize=7, loc="lower left")
    for mode, (label, marker, color) in MODES.items():
        for r in [r for r in historical if r["mode"] == mode]:
            x, y = r["terminal_return"], 100 * auc(r["cells"], "success_rate")
            axs[2].scatter(x, y, marker=marker, color=color, s=28)
            point_label = f"{label}{r['seed']-8600}"
            offsets = {
                "A0": (-12, -8),
                "F1": (4, 0),
                "N0": (-4, 3),
                "N1": (-6, 9),
                "N2": (-13, 0),
                "A2": (3, -8),
                "F2": (3, 4),
            }
            axs[2].annotate(
                point_label,
                (x, y),
                xytext=offsets.get(point_label, (3, 3)),
                textcoords="offset points",
                fontsize=6,
            )
    axs[2].set(
        xlabel="Terminal training return",
        ylabel="Frontier success AUC (points)",
        title="12 policies; Spearman −0.73",
        xlim=(10.7, 16.2),
        ylim=(57, 97),
    )
    save(fig, "return_inversion")

    fig, axs = plt.subplots(2, 2, figsize=(3.5, 2.65))
    for ax, contrast in zip(axs.flat, analysis["contrasts"]):
        ax.axvline(0, color=".65", lw=0.7)
        ax.axvline(-contrast["margin_pp"], color="#b44236", ls="--", lw=0.8)
        ax.scatter(contrast["differences_pp"], [0, 1, 2], color="#167887", s=22)
        ax.set(
            yticks=[0, 1, 2],
            yticklabels=["8600", "8601", "8602"],
            ylim=(-0.5, 2.5),
            xlim=(-2.5, 3.8),
            title=("Frontier" if contrast["band"] == "frontier_auc" else "Envelope")
            + " "
            + contrast["metric"].split("_")[0],
        )
        ax.invert_yaxis()
    for ax in axs[1]:
        ax.set_xlabel("Never-shrink − fixed (pp)")
    save(fig, "paired_seeds")

    fig, axs = plt.subplots(1, 3, figsize=(7, 2.65))
    for seed, arms in ((8600, ("R0", "R1", "R2")), (8601, ("R0", "R1"))):
        for arm in arms:
            rows = [r for r in analysis["retention"] if r["arm"] == arm and r["seed"] == seed]
            style = dict(
                color=COLORS[arm],
                marker="o" if seed == 8600 else "s",
                ls="-" if seed == 8600 else "--",
                ms=3,
                lw=1,
                label=f"{arm}, {seed}",
            )
            xs = [0] + [r["iteration"] for r in rows]
            axs[0].plot(xs, [0] + [r["D_pct"] for r in rows], **style)
            axs[1].plot(xs, [0] + [r["L_pp"] for r in rows], **style)
            axs[2].plot(
                [0] + [r["D_pct"] for r in rows],
                [rows[0]["origin_hard_qualification_pct"]]
                + [r["hard_qualification_pct"] for r in rows],
                **style,
            )
    axs[0].axhline(10, color=".4", ls=":")
    axs[1].axhline(2, color=".4", ls=":")
    axs[2].axvline(10, color=".4", ls=":")
    origin = next(r for r in analysis["retention"] if r["arm"] == "origin")
    axs[2].scatter(
        [0], [origin["hard_qualification_pct"]], color="black", marker="*", s=65, zorder=5
    )
    axs[2].annotate(
        "Origin",
        (0, origin["hard_qualification_pct"]),
        xytext=(5, -10),
        textcoords="offset points",
        fontsize=7,
    )
    axs[0].set(xlabel="Continuation iteration", ylabel="Worst tested error increase D (%)")
    axs[1].set(
        xlabel="Continuation iteration", ylabel="Worst completion loss L (pp)", ylim=(-0.15, 2.25)
    )
    axs[2].set(xlabel="Worst tested error increase D (%)", ylabel="Hard qualification (%)")
    axs[0].legend(frameon=False, fontsize=6, ncol=2)
    save(fig, "retention_trajectory")

    fig, axs = plt.subplots(1, 2, figsize=(3.5, 2.1), sharey=True)
    for ax, seed in zip(axs, (8600, 8601)):
        rows = [
            r
            for r in analysis["sensitivity"]
            if r["seed"] == seed and r["arm"] == "R1" and r["iteration"] == 2000
        ]
        z = np.array(
            [
                [
                    next(
                        r["gain_pp"]
                        for r in rows
                        if r["global_threshold_mm"] == g and r["local_threshold_mm"] == l
                    )
                    for l in LOCAL_GRID
                ]
                for g in GLOBAL_GRID
            ]
        )
        ax.imshow(z, origin="lower", vmin=0, vmax=10, cmap="YlGnBu", aspect="auto")
        for i in range(5):
            for j in range(5):
                ax.text(
                    j,
                    i,
                    f"{z[i,j]:.1f}",
                    ha="center",
                    va="center",
                    fontsize=5,
                    color="white" if z[i, j] > 5 else "black",
                )
        ax.scatter([2], [2], s=150, facecolors="none", edgecolors="#b44236", lw=1)
        ax.set(
            xticks=range(5),
            xticklabels=LOCAL_GRID,
            yticks=range(5),
            yticklabels=GLOBAL_GRID,
            xlabel="Local threshold (mm)",
            title=f"Seed {seed}",
        )
    axs[0].set_ylabel("Global threshold (mm)")
    save(fig, "threshold_sensitivity")

    mujoco = read_data(args.data, "mujoco.json")
    fig, ax = plt.subplots(figsize=(3.5, 2.35))
    for arm, label, marker, color in [
        ("off_s8600", "No DR, 8600", "o", "#444444"),
        ("lucid_collapsed_s8601", "A collapsed, 8601", "s", "#b44236"),
        ("ratchet_s8601", "Never-shrink, 8601", "^", "#167887"),
        ("fixed_s8601", "Fixed, 8601", "v", "#a8781c"),
        ("fixed_s8600", "Fixed, 8600", "D", "#625e92"),
    ]:
        rates = [
            100
            * fmean(
                r["completed"]
                for r in mujoco
                if r["arm"] == arm and not r["pushes"] and r["scale"] == scale
            )
            for scale in (1, 1.5, 2)
        ]
        ax.plot([1, 1.5, 2], rates, marker=marker, color=color, label=label, ms=3, lw=1)
    ax.set(xlabel="Physics scale (pushes disabled)", ylabel="Completion (%)", xticks=[1, 1.5, 2])
    ax.legend(frameon=False, fontsize=6)
    save(fig, "mujoco_ladder")
    provenance = {
        "data_manifest_sha256": hashlib.sha256(
            (args.data / "manifest.json").read_bytes()
        ).hexdigest(),
        "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "outputs": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(args.output.glob("*.pdf"))
        },
        "scope": "Existing simulation records; seeds 8600 and 8601 share one continuation origin.",
    }
    (args.output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print("Wrote figures to", args.output)


if __name__ == "__main__":
    main()
