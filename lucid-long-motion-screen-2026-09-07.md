# Nominal multi-motion retention screen — September 7, 2026

**Completed longer-motion screen, September 7, 01:57 UTC:** All eight cells finished. Both origin and R1 have 0% tracking-qualified execution on all three longer development motions. Curved walking and sideways walking largely survive but fail quality; stooping has 0% completion. The control passes retention (+8.79% global, -0.97% local). Establish a high-quality shared multi-motion origin before recovery calibration. The [current public page](https://linjiw.github.io/lucid/) reports all outcomes and the revised roadmap.

The next experiment is a bounded development evaluation of frozen origin versus the selected R1 endpoint. It addresses the current bottleneck: the four-second development clip leaves too few uninterrupted recovery windows, and longer candidates are not yet demonstrated capabilities of either policy.

The campaign supervisor was launched at **01:25:15 UTC**, PID **2694410**. It logs online to [W&B](https://wandb.ai/16726/lucid-sonic/runs/motion-cb05d12074a0278415). Cells start serially when the existing 11,000-MiB free-memory threshold is met. Starting the supervisor is distinct from starting simulator execution; inspect the cell log and status receipt for the live state.

## Frozen comparison

| Motion | Source key | Duration | Role |
|---|---|---:|---|
| Original control | walk_hands_on_back_loop_002__A066_M | 4.00 s | Previously measured motion |
| Curved walking | walk_arc_cw_loop_R_002__A229 | 10.63 s | Development candidate |
| Sideways walking | walk_sideway_135_loop_003__A037 | 11.23 s | Development candidate |
| Neutral stooping | neutral_stoop_down_R_001__A104 | 8.17 s | Development candidate |

Eight cells: four motions × origin/R1, each with 128 distinct aliases and evaluation seed 8730, nominal physics. The R1 checkpoint is the preselected 2,000-iteration endpoint. The three new clips were selected by metadata, duration and intended motion diversity before observing outcomes. Names are descriptive metadata, not a validated motion taxonomy. All come from the existing development partition; none comes from the final test partition. No claim that the base model has never seen them is warranted.

Report all cells, including poor origin performance. Evaluate +10% empirical mean global/local-error limits and a −2 percentage-point completion limit separately for each motion. The broad 600/50-mm tracking qualification is a separate development measure. A poor origin cannot demonstrate a previously solved capability that R1 must retain. These are evaluation replicates from one trained origin, not 1,024 independent policy samples or a confidence-certified retention claim.

The execution-validated recorder captures translation, heading, root-relative pose and heading-aligned articulation traces. No recovery bands, recovery rates or safety qualifications are inferred from this nominal screen. Native zero-increment interval events are not pushes. Future recovery windows must stop at reference resampling, physical reset, overlap or trace end.

## Evidence and validation

- Source worktree: `/home/linjiw/lucid-long-motion-screen`, commit `a1b8816`.
- Plan: `/home/linjiw/lucid-sonic/experiments/long_motion_screen_20260907_a/plan.json`.
- Plan SHA-256: `cb05d12074a0278415c156bfc04bcec435ce938791939cf922c1599e04847368`.
- Runtime state and per-motion comparisons: campaign `status.json`; exact detached command in `launch.json`.
- CPU suite: **2,119 passed**, five warnings; final import smoke: eight passed. New files pass Black, Ruff and isort. Initial pytest entry-point collection imported the installed checkout; that failed invocation is preserved, then corrected with `python -m pytest` against this worktree.
- Test and preparation receipts: `/home/linjiw/lucid-sonic/analysis/long_motion_screen_preparation_20260907_a/`.
- Each online cell records stage, arm, seed, checkpoint iteration, condition, source/plan/checkpoint hashes, metrics and capture receipt hashes, plus measured runtime. Raw motion packs, checkpoint weights and credentials are not uploaded.

## Research decision after this screen

If origin and R1 execute longer motions with retained quality, collect independent origin calibration/validation episodes and preregister isolated perturbations with adequate horizon and dwell. If R1 loses longer-motion quality, expand the retained-motion data contract and test a shared multi-motion anchor repair before attributing robustness gains to feedback. If origin itself lacks these motions, establish a genuinely solved shared-motion origin first. All outcomes remain in the screen; later development selection must be disclosed.

The central method comparison remains protected fixed practice versus a development-frozen schedule versus recovery feedback, with identical preservation mechanisms and a full resource budget. This screen launches evaluation, not another PPO continuation or an observer-training grid. The utility estimator and residual allocator remain gated.

Live verification at 2026-09-07T01:27:47.930903+00:00: supervisor alive; 0/8 cells complete; simulator started=False. GPU snapshot: 12588 MiB, 57 %. All 21 frozen inputs and 1210 source files match their hashes. W&B campaign and first cell were also independently verified through its API.

**Execution confirmed at 2026-09-07T01:28:36.992036+00:00:** capacity cleared and the first native simulator evaluation is running, with advancing sequence progress in its log. The earlier queued snapshot is historical.
