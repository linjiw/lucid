# LUCID retention-repair implementation and queued collection

**Latest execution, September 7, 00:24 UTC (September 6 EDT):** the full 83-cell retention screen is complete. [completed retention results](lucid-retention-repair-results-2026-09-06.md) select R1 as the protected development baseline: all five sampled checkpoints retain clean/original-envelope quality, with +5.18 percentage points on the final two-condition held-out tracking-qualified score. R0/R2 fail retention. This is one-origin, one-motion evidence. The eight-cell frozen-origin recovery recorder validation is now supervised and [logged online](https://wandb.ai/16726/lucid-sonic/runs/rec-3ae0529d4649aaef377c), initially queued at the 11,000 MiB GPU-capacity gate. Its source is frozen at `0c81b00`, and all 2,105 CPU tests pass. Recovery/feedback efficacy remains untested.


Snapshot: September 6, 2026, 04:49 UTC / 00:49 EDT. Prospective plan: [quality-preserving robustness expansion](lucid-retention-repair-plan-2026-09-06.md).

**Execution update:** the subsequent [retention-screen amendment](lucid-retention-screen-execution-2026-09-06.md) makes recipe selection, collected-target verification, matched smoke and full repair training executable behind the existing prerequisites. The snapshot below records the earlier collection-only state.

**Measurement preparation:** [offline component and recovery validation](lucid-recovery-measurement-status-2026-09-06.md) is complete while the existing campaign waits. Live event alignment and phase calibration remain gated.

## Implemented and validated

Implemented frozen-origin behavioral anchoring and phase-balanced collection in `/home/linjiw/lucid-retention-repair`, branch `research/retention-repair`, commit `940af951087a495938ee822fa41210bb06956580`. The checkout is clean. The original SONIC checkout's uncommitted work and the running optimizer-history source remain untouched. No upstream SONIC module was edited.

The opt-in trainer preserves SONIC's PPO and auxiliary token losses. It adds only the supervised origin action-mean term; beta zero returns the exact native loss path without buffer reads. Anchor forwards retain gradients while preserving module modes and rollout state. The initial implementation supports one training process and rejects anchored resume until its sampler-state contract is implemented.

Collection caches raw action-aligned dictionaries and episode masks from first episodes, filters by completed tracking qualification, and records origin hashes, condition, phase and episode identities. Assembly requires 64 competent records per condition per each of 16 phase bins, producing 2,048 histories. It rejects insufficient coverage. Cost records include collection transitions, teacher forwards, anchor presentations and forward time; backward work is combined with PPO and included in training wall time.

- Final full CPU suite: **1,964 passed**, four warnings, 39.09 s. [Log](/home/linjiw/lucid-sonic/outputs/retention_repair_cpu_20260906_b.log).
- **24 focused tests passed**: identity, corrective gradients, vector-norm normalization, existing-loss preservation, RNG/rollout state, masks/phase/reset boundaries, deterministic assembly, origin/hash/resume rejection, and failed-predecessor queue behavior.
- Black and Ruff pass on all ten additions; staged whitespace checks passed before commit. `make run-checks` fails at repository-wide isort, starting in existing `motionbricks/` files. Root isort and Ruff also prescribe different within-section ordering; additions follow the neighboring research modules' Ruff order. [Full check log](/home/linjiw/lucid-sonic/outputs/retention_repair_run_checks_20260906_a.log). No repository-wide reformat was made.
- The actual solved SONIC actor passes the synthetic CPU audit: identity loss and gradients are exactly **zero**; a 0.001 decoder-bias perturbation produces loss 0.0001643241 and summed squared gradient norm 0.003198149. This validates the numerical interface, not behavioral retention or realistic state coverage. [Bound validation](/home/linjiw/lucid-sonic/analysis/reference_anchor_cpu_20260906_b/validation.json).

The actor audit confirms wrapper history length one, raw dimensions actor 930 / tokenizer 1,761 / critic 1,645, and no actor-level running or batch normalization. Raw fields can themselves contain temporal information; wrapper length does not support an information-deficit claim.

Reproduction, after setting `LUCID_REPO=/home/linjiw/lucid-retention-repair` and sourcing `/home/linjiw/lucid/env/lucid_env.sh`:

```bash
python -m pytest tests/practice_utility/
python scripts/practice_utility/validate_reference_anchor.py \
  --checkpoint /home/linjiw/lucid-sonic/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260829_000249/seed_8600/fixed/final_checkpoint.pt \
  --training-config /home/linjiw/lucid/GR00T-WholeBodyControl/logs_rl/lucid-campaign/manager/universal_token/all_modes/sonic_release_test-20260829_000251/config.yaml \
  --model-config /home/linjiw/lucid-sonic/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260829_000249/seed_8600/fixed/model_config.yaml \
  --output /home/linjiw/lucid-sonic/analysis/reference_anchor_cpu_reproduction/validation.json
```

Use a fresh numerical output path; overwriting results is rejected.

## Current execution

**Later September 6 update:** the history comparison and 2,048-record origin collection completed. The original retention screen stopped before smoke because CPU teacher replay did not match native TF32 numerics. The [precision repair and new campaign](lucid-anchor-precision-repair-2026-09-06.md) verify exact targets and origin-anchor identity, preserve the failed attempt, and restart at the smoke gate. The execution observations below describe the earlier state.

The unchanged optimizer-history campaign is still running. At 04:49 UTC its fresh arm was at **1,858/2,000** iterations, with no warnings. Restoration and the full endpoint grid remain queued. No continuation recipe has been selected from partial results. [Live predecessor status](/home/linjiw/lucid-sonic/experiments/optimizer_history_campaign_20260905/status.json).

Created a dedicated training-side 128-alias collection panel using the adaptation clip. Collection seed 8610 differs from the seed-8700 scoring draws. Aliases are a simulator replication device, not new motions. [Panel receipt](/home/linjiw/lucid-sonic/manifests/replicate_panel_anchor_hob002_k128_20260906_a.json).

Frozen collection plan: [plan.json](/home/linjiw/lucid-sonic/experiments/anchor_collection_20260906_a/plan.json), SHA-256 `1ef5f55a7acf72ed309433f3916008739f23f6ce8ae65e281cef534d4717b424`. It binds 1,028 source/config files and the origin/panel inputs. Two planned cells collect clean and original-envelope origin rollouts, 128 episodes each. These are training-data collection and instrumentation, not method efficacy results.

Detached worker PID **1731840** polls once per minute for up to 24 hours. It verifies the complete predecessor plan, receipt, checkpoints, metrics and analysis before collection. The 11,000-MiB GPU memory gate still applies. A failed predecessor, changed input, invalid measurement or insufficient coverage stops the worker. There are no retries or automatic repair-training launches.

- [Launch receipt and exact command](/home/linjiw/lucid-sonic/experiments/retention_repair_campaign_20260906_a/launch.json), including code/test/numerical hashes and process start identity.
- [Worker status](/home/linjiw/lucid-sonic/experiments/retention_repair_campaign_20260906_a/collection/status.json), verified `waiting_for_optimizer_history` at 04:48:53 UTC.
- [Worker log](/home/linjiw/lucid-sonic/experiments/retention_repair_campaign_20260906_a/worker.log).
- Future cell receipt: `/home/linjiw/lucid-sonic/experiments/anchor_collection_20260906_a/receipt.json`.
- Future buffer/receipt: `/home/linjiw/lucid-sonic/experiments/retention_repair_campaign_20260906_a/collection/`.

## Outstanding gates

Read the full fresh/restored trajectories and document the common continuation recipe. Verify collected targets against the loaded origin, then run the matched three-arm fixed-mixture simulator smoke: beta-zero no-op, lower-rate optimizer groups, 768/256 membership, actual channel dispatch and valid exports. Freeze the full 2,000-iteration R0/R1/R2 execution plan only after these checks. This immutable repair-training plan and simulator validation remain outstanding; no simulator-tested anchor, repaired tracking or adaptive superiority is claimed.

The +10% retention margins remain unchanged. Future fixed, frozen-schedule and adaptive arms receive the same effective repair. Recovery components and their endpoint need synthetic and event-alignment validation before decision use. Utility estimation, residual allocation, new encoders and hardware retain their prior gates.
