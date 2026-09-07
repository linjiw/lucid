# Common path-input implementation and controller-repair status

**Latest:** The 128-iteration pilot completed successfully. Original actor weights remained exact; the native action-noise clamp changed std by at most 1.06e-5 and is recorded separately. Final new-weight norm is 0.28983. Cost: 786,432 PPO transitions, 655,616 anchor sample presentations, 5,122 anchor forwards, and 295.07 s inside training (17.53 s measured anchor forwards included). Final checkpoint SHA `b33a22ae6ec5f938c9a647274ca7d51065184c2620b6af9ed80d1ec353bc11cd`. The frozen 16-cell [initial/final evaluation](https://wandb.ai/16726/lucid-sonic/runs/path-eval-45c38aed42ba0eb1) is now running; efficacy and per-motion retention remain pending. Historical snapshots below retain their original stage status.

September 7, 2026 UTC. This is common-controller foundation work for the [ideal paper](site/index.html#plan), not evidence for a curriculum advantage.

## Evidence and decisions

The released controller solves all four original development candidates under the broad development screen. The physical-state comparison nevertheless found identical active actor information/actions for otherwise matched horizontal displacements. A common horizontal reference-minus-robot path input is now implemented, scaled by 0.3 m and expressed in robot heading coordinates, without clipping. Original observation histories and the G1 encoder retain their interfaces. Two zero-initialized columns extend the first dynamic decoder layer from 2048 × 994 to 2048 × 996.

CPU migrations pass strict checkpoint loading, original-weight preservation, exact tested action/encoder equality, finite new-column gradients, and exact serialization/reload. These checks are necessary but do not establish rollout parity.

The first native 9-cell campaign completed and failed its preregistered nominal agreement gate: curved walking changed from 101.6985 to 100.2058 mm global MPJPE, an absolute 1.4926 mm difference versus a 1.0170 mm allowance. All four motions still completed and qualified at 100%. The improvement in this metric does not override the failed no-op gate.

A split first-layer computation preserves the original matrix multiplication dimensions, adding the two-coordinate contribution separately. Its CPU migration also passes. The second campaign's eight nominal cells are complete: control global change +0.1988 mm, arc −0.5553 mm, sideways +1.1823 mm, stoop +0.4828 mm. Sideways exceeds its 1.1120 mm allowance. This second no-op gate therefore also fails, even though completion and broad qualification remain 100% in every cell. Do not launch PPO from either failed gate or quietly increase tolerances. A same-input GPU computation diagnostic is next; the arithmetic hypothesis is not established by the two rollout outcomes.

## Prepared bounded learning pilot

Source `3885a55`, `/home/linjiw/lucid-path-repair-pilot`, adds a prospective common-controller pilot. It requires completed, passing native gates before a plan can be frozen. PPO has **not started** at this snapshot.

- One released shared origin, all four original development motions, fixed equal motion allocation; these motions are adaptation/development data.
- 256 environments, 128 PPO iterations, 24 transitions/environment/iteration: 786,432 training transitions.
- 128 nominal environments and 128 environments receiving fixed 0.5 m/s horizontal root-velocity increments, with four balanced directions and 2.5–3.5 s event intervals. Record realized events. These are training disturbances, not isolated recovery labels.
- Freeze original actor parameters; learn the 4,096 added first-layer weights and the critic. Use a fresh optimizer, constant actor learning rate 2e-5, and no weight decay. Audit original actor weights at each iteration; separately record the native action-noise clamp.
- Nominal protection uses 4 motions × 16 phase bins × 32 qualified frozen-origin states = 2,048 histories. Anchor coefficient 1, 256 sampled histories/update, physical forward batches at most 128. This is nominal-only protection, not a completed multi-motion R1 envelope extension.
- Keep the released tracking objective. No learned observer, feedback gate, utility estimator, or residual allocator is involved.
- Require online W&B and log training/anchor costs separately. Evaluate actual nominal retention and disturbed trajectories before judging path-recovery efficacy; recovery bands and tighter competence criteria remain open.

CPU suite: 2,148 passed, 5 warnings. Focused new logic tests cover fixed exposure balance, exact old-column preservation under Adam, and rejecting incomplete anchor coverage. Changed-file Ruff and Black checks pass. Repository-wide `make run-checks` stops on existing import-format failures across upstream/vendor files; unrelated files were not reformatted.

## Receipts

Generated artifacts remain outside Git.

- First CPU migration: `/home/linjiw/lucid-sonic/experiments/path_input_migration_20260907_a`, [W&B](https://wandb.ai/16726/lucid-sonic/runs/path-migrate-0cefca30592e148c).
- First native campaign: `/home/linjiw/lucid-sonic/experiments/path_input_native_gates_20260907_a`, plan SHA `30c8891ae0811bffe85af7fb3b3c49d812f0934becb16e60d2aa2d243d514c48`, [W&B](https://wandb.ai/16726/lucid-sonic/runs/path-gates-30c8891ae0811bff).
- Split CPU migration: `/home/linjiw/lucid-sonic/experiments/path_input_migration_20260907_b`, plan SHA `e74b3d704bd4701a98d89ac620b8161df807c3d9077d77d8d80b533930efc127`, [W&B](https://wandb.ai/16726/lucid-sonic/runs/path-migrate-e74b3d704bd4701a).
- Split native campaign: `/home/linjiw/lucid-sonic/experiments/path_input_native_gates_20260907_b`, plan SHA `c49dd480419e05c0310b7c32b3e9b664397894db8cf581c06c9a8f68d9485993`, [W&B](https://wandb.ai/16726/lucid-sonic/runs/path-gates-c49dd480419e05c0).
- CPU and formatting logs: `/home/linjiw/lucid-sonic/outputs/path_repair_cpu_tests.log`, `path_repair_make_checks.log`.

## Update: direct live gate passes; PPO has started

Both original cross-process agreement campaigns remain failed. The [gate amendment](lucid-path-noop-gate-amendment-2026-09-07.md) was written before the new live outcomes. It replaces the cross-process agreement criterion for this bounded pilot with paired action comparisons on every live observation, retaining the original 1e-5 action tolerance and requiring all four motions to complete/qualify. The unresolved source of cross-process divergence is not asserted to be exclusively physics noise.

The new gate passes: control 201, arc 531, sideways 561 and stoop 408 full-batch policy forwards; all action differences exactly zero. That is 217,728 matched action-vector comparisons. All four empirical completion/qualification rates are 100%. The physical information test also passed at all three tested phases for the identical migrated checkpoint. The nominal buffer contains 2,048 qualified histories balanced across motion and phase.

The first automatic PPO attempt failed before simulator/PPO startup because Hydra parsed W&B entity `16726` as an integer. It has zero training updates and a separately labeled backfilled online failure receipt. Source `3885a55` and its failed plan remain intact. A new worktree quotes the entity explicitly, preserving the scientific design and starting fresh.

**The second attempt is training online:** [controller-repair/path-input/protected-fixed/m4/s8762/i128](https://wandb.ai/16726/lucid-sonic/runs/wnb1cavy). Startup verifies the exact migrated policy, fresh optimizer, zero nominal anchor loss and four motion keys. Live per-iteration checks confirm fixed 64-environment allocation per motion and unchanged original actor parameters. New input weights are updating; real nonzero velocity increments are recorded. Initial W&B verification at iteration 20 recorded new-weight norm 0.09726 and 102,656 anchor sample presentations. These are learning/instrument signals, not retained-quality or recovery results.

A 16-cell initial/final evaluation was frozen during training: four motions × nominal/horizontal-push conditions × two checkpoint stages, 128 aliases/cell, seed 8765. It uses the existing first-episode qualified tracking measurements and raw recovery recorder. Horizontal push evaluation uses independent uniform increments in ±0.5 m/s per horizontal axis every 2.5–3.5 seconds, with zero vertical/angular increments. It is a development stress panel; no calibrated recovery-success endpoint is claimed. Final checkpoint hashes will be bound after training, without choosing among intermediate outcomes.

Evidence:

- GPU diagnostic: `/home/linjiw/lucid-sonic/experiments/path_input_gpu_diagnostic_20260907_a/receipt.json`, [W&B](https://wandb.ai/16726/lucid-sonic/runs/path-gpu-d87a190cb4b36659).
- Passing live gate: `/home/linjiw/lucid-sonic/experiments/path_input_shadow_gates_20260907_a`, source `9fe87e6`, plan `5e6c2551ee23e83e723d8b98e65266156d94db0b53ac353eb9ad4dd8d7e3cacf`, [W&B](https://wandb.ai/16726/lucid-sonic/runs/path-shadow-5e6c2551ee23e83e).
- Training: `/home/linjiw/lucid-sonic/experiments/path_repair_pilot_s8762_20260907_b`, plan `59ac46c63026773c1978296f90b9598a68e18eab20c4ac9618562e38d3e336c1`. `train/initialization.json`, `practice_initialization.json`, `exposure.jsonl` and `push_events.jsonl` are live receipts.
- Evaluation: `/home/linjiw/lucid-sonic/experiments/path_repair_pilot_evaluation_20260907_a/plan.json`, source `4f667e2`. Final results pending.

## Independent final-checkpoint and delivered-exposure audit

The read-only audit passed. Every old decoder column is exact; all 4,096 new coordinates are nonzero, and the only other changed actor-state entry is the recorded native `std` clamp. Verified training allocation is 196,608 transitions per motion. The simulator received 2,047 nonzero push events: control 480, arc 549, sideways 527, stoop 491. Direction counts are 512/512/512/511; actual event counts vary with episode timing despite fixed environment allocation. Velocity-write roundoff is at most 5.96e-8 m/s, and no event targets the nominal cohort. [Online audit](https://wandb.ai/16726/lucid-sonic/runs/path-training-audit-6642e03c6a5c); receipt `/home/linjiw/lucid-sonic/analysis/path_repair_training_audit_20260907_a/receipt.json`.

The initial/final evaluator is active under plan SHA `45c38aed42ba0eb188f078db07a9bb107607434fc3516285ae4951b4d31b6087`. Its complete CPU suite passed 2,148 tests before launch. First completed nominal pairs show control global MPJPE 89.77 → 83.82 mm (−6.62%) and arc 103.78 → 92.87 mm (−10.51%), with 100% completion/qualification in both arms. These are partial development outcomes, not a completed four-motion retention or disturbance-recovery result. The serial supervisor will run all 16 cells and produce per-motion analysis automatically; a failed cell prevents a complete result.

Public page deployment of `8f76147` succeeded and its served HTML was checked for the completed-pilot status. The public page remains a dated snapshot, not an automatically refreshed dashboard.
