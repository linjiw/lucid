# Anchor validation failure: diagnosed precision and batch-size contracts

September 6, 2026. The [completed optimizer comparison](lucid-optimizer-history-results-2026-09-06.md)
selects fresh history. Collection completed at 07:23:11 UTC with the planned
2,048 phase-balanced histories. The first retention-screen supervisor stopped at
07:24:08 UTC because CPU target replay exceeded the frozen action tolerance.
No smoke training or long repair arm ran in that failed attempt.

## Measured cause and repair

The pinned SONIC training and evaluation entrypoints both enable CUDA matmul and
cuDNN TensorFloat-32, disable cuDNN deterministic mode, and disable cuDNN benchmark.
The original CPU validator could load identical actor weights and input histories
but did not reproduce this numerical execution contract. The native collection
used 128 environments, which also fixes its physical forward batch size.

Replaying the same 2,048 stored records with the frozen origin on this RTX 5080:

| Replay | Records outside original tolerance | Maximum absolute action difference |
| --- | ---: | ---: |
| CPU, batch 128 | 2,048 | 0.0050239563 |
| Native CUDA TF32, batch 128 | 0 | **0 exactly** |
| Native CUDA TF32, direct batch 256 | 358 | 0.0034665316 |
| Native CUDA TF32, logical 256 split into physical 128 forwards | 0 | **0 exactly** |

The tolerance stays absolute 1e-4 and relative 1e-5. Differences are in native
pre-actuator action units, not directly measured physical pose errors. The stored
targets, observations, buffer membership and buffer hash are unchanged. Direct
batch-256 mismatch is a numerical batch-shape effect; its tiny squared-action
floor does not by itself predict a material behavioral difference.

Commit `8f83ea4` in `/home/linjiw/lucid-anchor-target-repair`, branch
`research/anchor-target-repair`, makes these changes under the research seam:

- The target validator requires complete native CUDA replay under explicit SONIC
  precision settings and restores the caller's backend settings afterward.
  CPU and unsplit-256 replay remain diagnostics. All three modes and source hashes
  are recorded; failed validation remains a failed receipt.
- The anchor still samples 256 histories with the same private RNG, sums squared
  normalized action-vector distances and divides by 256, with beta 1. It evaluates
  them in two physical batches of 128 to match collection. The full sampled
  origin check now has **exactly zero loss and zero parameter gradient**.
- Training receipts count both student forwards and preserve the existing combined
  PPO-plus-anchor backward. At 40,000 PPO updates, R1 still presents 10,240,000
  anchor samples, now with 80,000 separately counted student forward calls.
  Actual wall time captures the extra dispatch cost. Beta-zero arms take the same
  native loss path as before.
- Campaign preparation rejects CPU-only, incomplete, tolerance-weakened or
  mismatched-precision validation and requires the exact origin identity check.
  All scientific conditions, allocation, rates, horizon, snapshots and comparison
  rules remain as in the existing retention screen.

The initial exploratory precision check is retained at
`/home/linjiw/lucid-sonic/analysis/anchor_precision_repair_20260906_a/validation.json`:
it correctly fails the unsplit-256 check. The corrected prelaunch evidence is
[validation.json](/home/linjiw/lucid-sonic/analysis/anchor_precision_repair_20260906_b/validation.json).
The campaign independently recomputes it under committed source in
[collected_target_validation.json](/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_b/collected_target_validation.json).

This resolves a numerical instrumentation gate. It does not demonstrate that
behavioral anchoring preserves tracking or improves robustness.

## Validation and restarted experiment

The focused anchor/retention set passes **68 tests**. The final full CPU suite
passes **2,013 tests**, four warnings, 38.61 seconds.
[CPU log](/home/linjiw/lucid-sonic/outputs/anchor_precision_repair_cpu_20260906_b.log).
The new regression tests check the actual precision assignments in both upstream
entrypoints, restoration after errors, complete target replay, unchanged targets
and tolerance, native-only admission, and sample-budget/gradient identity with a
batch-size-sensitive actor. Black/Ruff and whitespace checks pass on the changes;
repository-wide `make run-checks` retains the existing isort failures beginning in
`motionbricks/`.
[Check log](/home/linjiw/lucid-sonic/outputs/anchor_precision_repair_run_checks_20260906_b.log).

This is a new, explicitly recorded restart after diagnosis, not an automatic retry
of the failed plan. The failed `_a` campaign, its decision, logs, status and source
checkout remain unchanged. The completed history comparison and collection are
reused through verified hashes.

New campaign: `/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_b/`.
Its immutable [campaign.json](/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_b/campaign.json)
has SHA-256 `2071c80693fe46d45457f9e551dae05397d190455b8ccf83ec4ccc2754f6561d`.
The [launch receipt](/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_b/launch.json)
binds the failed predecessor and exact new command. Supervisor PID 2022309 started
at approximately 14:38 UTC. Its own native target audit passed and the smoke began.

The 16-cell smoke must complete native/R0 checkpoint parity and all live contracts
before the supervisor creates and runs the 83-cell full screen. Every long arm has
2,000 iterations, every saved stage is evaluated at all five conditions, and all
80 evaluation cells must finish before the complete repair analysis. A smoke
performance number never selects the repair. The current
[status](/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_b/status.json)
and [supervisor log](/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_b/supervisor.log)
track execution separately from results.

Reproduce numerical validation with a new output path:

```bash
export LUCID_REPO=/home/linjiw/lucid-anchor-target-repair
source /home/linjiw/lucid/env/lucid_env.sh
python scripts/practice_utility/validate_collected_anchor.py \
  --buffer /home/linjiw/lucid-sonic/experiments/retention_repair_campaign_20260906_a/collection/anchor_buffer.pt \
  --buffer-sha256 3517adde328c64d14304f9fab2dfd96f4a4c744ebe2213b2cc6971ee295a4b85 \
  --binding /home/linjiw/lucid-sonic/experiments/optimizer_history_campaign_20260905/binding.json \
  --output /home/linjiw/lucid-sonic/analysis/anchor_precision_reproduction/validation.json
```
