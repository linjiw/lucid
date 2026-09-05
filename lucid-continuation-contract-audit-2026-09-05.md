# LUCID continuation contract audit

Date: 2026-09-05. This audit supplements the [completed pilot](lucid-quality-frontier-pilot-results-2026-09-05.md); it does not change its frozen endpoints, receipts, or running successor experiment.

## Findings

The pilot and initial-distribution diagnostic load the solved origin's policy and value weights with fresh optimization state. The saved configuration contains `algo.config.load_optimizer=True`, but the active SONIC loader restores optimizer and scheduler state only when the separate top-level `resume` argument is true. That argument is absent, hence false, in the three audited continuation configurations: the completed gate, initial-hold smoke, and running initial-hold pilot.

The audit executes the actual `TRLPPOTrainer.load_checkpoint` on CPU with recording recipients. With `resume=False`, policy and value restore calls each execute once; optimizer, scheduler, and environment restore calls do not execute, and the recipient's initialized counter remains zero. With `resume=True`, all five restore calls execute and the source's counter of 8,000 is restored. Recording recipients establish loader behavior, not numerical optimizer or simulator resume equivalence. The normal training path subsequently resets the environment, so the audit does not establish seamless environment continuation either.

The source optimizer's two recorded group learning rates are both `2e-5`, matching the continuation's configured starting rate. There is no evidence here of an initial nominal learning-rate jump. Accumulated optimizer history is discarded. This restart contract is shared across the compared arms; it does not invalidate their inter-arm comparisons. Its contribution to origin-relative tracking drift remains an untested causal hypothesis.

Saved `manager_env` settings match the origin exactly, including rewards, observations, actions, and terminations. Algorithm differences are the training horizon and output directory. Runtime curriculum callbacks deliberately change DR assignments beyond those saved environment settings, so config equality does not imply identical training distributions.

The new 16-iteration initial-hold smoke and the earlier 16-iteration replay smoke have exactly equal tensors for all **55 policy entries and 17 value entries**. Their initial schedules coincide. This is observed checkpoint parity for this smoke pair, supporting the snapshot instrumentation; it is not a universal simulator determinism claim.

## Current experiment and decision

All six initial-hold smoke cells completed, including the eight-iteration intermediate snapshot. At eight iterations, clean completion and tracking-qualified success were both 100%, with global/local errors 119.06/28.49 mm. At sixteen iterations both remained 100%, with errors 124.61/27.76 mm; the origin measured 128.57/28.33 mm. These short-run measurements validate the path and cannot establish long-run retention.

The 2,000-iteration diagnostic is running under frozen commit `e5437b8`. Its monitor reported 95 iterations and no warnings at 23:09:54 UTC. It holds the E0 initial cohort mixture, including its initial joint-offset probe, rather than reconstructing the origin's original training distribution. It will evaluate saved clean snapshots at 250, 500, 1,000, and 1,500 iterations after training, then the five endpoint conditions. The supervisor checks progress every minute and automatically performs receipt-verified analysis after completion.

The research decision remains conditional on that result:

1. If holding initial exposure preserves quality, test an origin-relative quality veto against matched survival feedback and fixed controls, pricing probe costs equally.
2. If quality drifts without expansion, first isolate the training-retention mechanism. A prospective optimizer-history control should keep policy/value initialization, initial DR assignments, fresh environment, local training counter, learning-rate schedule, and update budget matched while varying only restoration of optimizer history. Native `resume=True` also changes scheduler and trainer-state restoration, so it is not a drop-in implementation of that control.
3. Add retention practice or a policy-reference constraint only through separate controlled comparisons if needed. Recovery or dynamics-history signals must show incremental predictive value before they guide curriculum decisions. Neither outcome identifies a robot's physical capacity boundary or establishes sim-to-real transfer.

No running training behavior was changed by this audit. Utility selection and residual allocation remain behind the original failed/unmet gates.

## Implementation, validation, and reproducibility

Audit checkout: `/home/linjiw/lucid-continuation-contract`, branch `research/continuation-contract`, commit `5c204a8483b4ffdce647e5038de0935fb70b7b7b`.

Added `scripts/practice_utility/audit_continuation_contract.py` and five focused tests in `tests/practice_utility/test_continuation_contract_audit.py`. All five passed; Black, Ruff, and whitespace checks passed. The separate frozen initial-hold runtime previously passed the full 1,908-test CPU suite. The new audit does not modify that runtime.

The audit verifies checkpoint/config hashes before and after reading, records its source hashes, and compares actual checkpoint tensors. Its outputs are [audit.json](/home/linjiw/lucid-sonic/analysis/continuation_contract_20260905_a/audit.json) and [receipt.json](/home/linjiw/lucid-sonic/analysis/continuation_contract_20260905_a/receipt.json). Audit output SHA-256: `64f41dfbf30c00e4c8b81383f4a08287306b736b688e86a8ecc5af828ee7e4e7`.

Reproduction command, using a fresh output directory:

```bash
export LUCID_REPO=/home/linjiw/lucid-continuation-contract
source /home/linjiw/lucid/env/lucid_env.sh
cd "$LUCID_REPO"
python scripts/practice_utility/audit_continuation_contract.py \
  --origin-checkpoint /home/linjiw/lucid-sonic/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260829_000249/seed_8600/fixed/final_checkpoint.pt \
  --origin-config /home/linjiw/lucid-sonic/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260829_000249/seed_8600/fixed/config.yaml \
  --continuation-config /home/linjiw/lucid-sonic/experiments/quality_frontier_pilot_20260905_a/train_gate/config.yaml \
  --continuation-config /home/linjiw/lucid-sonic/experiments/initial_hold_smoke_20260905_a/train_initial/config.yaml \
  --continuation-config /home/linjiw/lucid-origin-retention/logs_rl/TRL_G1_Track/manager/universal_token/all_modes/sonic_release_test-20260905_185644/config.yaml \
  --parity-checkpoints /home/linjiw/lucid-sonic/experiments/quality_frontier_smoke_20260905_b/train_replay/final_checkpoint.pt /home/linjiw/lucid-sonic/experiments/initial_hold_smoke_20260905_a/train_initial/final_checkpoint.pt \
  --output-dir /home/linjiw/lucid-sonic/analysis/continuation_contract_20260905_reproduction
```

Live schedule and progress: [campaign status](/home/linjiw/lucid-sonic/experiments/initial_hold_campaign_20260905/status.json). Smoke analysis: `/home/linjiw/lucid-sonic/analysis/initial_hold_smoke_20260905_a/`. Generated artifacts remain outside Git.
