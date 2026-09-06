# LUCID optimizer-history control: preparation and numerical validation

Date: September 5 EDT / September 6 UTC. Companion [continuation audit](lucid-continuation-contract-audit-2026-09-05.md) and [research plan](lucid-quality-frontier-research-plan-2026-09-05.md).

**Execution update:** the fixed-initial diagnostic has finished with a tracking-retention breach. The [completed-results and launch memo](lucid-initial-hold-results-2026-09-05.md) records the implemented runtime/binding work, 1,940 passing CPU tests, and the newly started smoke-gated paired campaign. The preparation sections below preserve their earlier state; the simulator gate is pending, and source parameter names are reconstructed with an explicit provenance limitation.

## Question and scope

Does resetting AdamW history contribute to the clean-tracking loss observed during solved-policy training? The completed frontier pilot establishes tracking drift, and the loader audit establishes fresh optimizer state in its arms. Neither establishes a causal connection. The running fixed-initial-DR diagnostic first asks whether expansion is necessary for that drift.

This control is a prepared diagnostic component, not a new curriculum method. It does not estimate utility, select DR channels, add a learned latent, or establish a capacity boundary. A simulator comparison remains conditional on the fixed-initial run's outcome and the parameter-binding checks below.

## Implemented component

Checkout `/home/linjiw/lucid-optimizer-history`, branch `research/optimizer-history`, commit `abb04dc` adds:

- `gear_sonic/research/practice_utility/optimizer_history.py`: a strict AdamW history transplant into a fresh optimizer. It restores first/second moments and Adam's per-parameter step counters while preserving the recipient's parameter groups and learning rates. It requires matching ordered source/target parameter names, group sizes, shapes, dtypes, and algorithm settings; malformed, non-finite, negative-second-moment, or incomplete history is rejected before loading. It rejects repeated restoration into an already initialized optimizer.
- `scripts/practice_utility/validate_optimizer_history.py`: a CPU numerical experiment against a real checkpoint, with immutable-output receipt, checkpoint/source hashes, and native-loader comparison.
- Ten focused tests cover exact subsequent-update parity at matched learning rates, preservation of configured recipient learning rates, exact paired numerical restarts, reordered names, malformed history, and repeat restoration.

The helper exposes no simulator or trainer hook. It cannot restore environment state, a scheduler, policy weights, or the trainer's global counter. Those remain the responsibility of the separate, matched restart protocol.

Validation: the full CPU suite passed **1,930 tests**, five warnings, 50.06 seconds; all ten focused cases passed, as did Black/Ruff and whitespace checks. Full log: `/home/linjiw/lucid-sonic/outputs/optimizer_history_cpu_20260905.log`.

## Real-checkpoint numerical result

The origin checkpoint contains **69 optimizer state entries**, grouped **35/34**, with Adam step **160,000** for every parameter. This is an optimizer-update counter, distinct from the origin's 8,000 PPO-iteration counter. Both saved group learning rates are `2e-5`.

All restored history tensors exactly match native AdamW loading. One subsequent synthetic update also matches exactly for all 69 parameter tensors. The experiment uses zero-initialized synthetic tensors with the saved moment shapes and a constant gradient of 0.125. It validates numerical restoration and compatibility with the saved history. It does **not** validate SONIC policy parameter ordering, trajectory equivalence, learning performance, or the cause of tracking loss.

Evidence: [validation.json](/home/linjiw/lucid-sonic/analysis/optimizer_history_numerical_20260905_a/validation.json) and [receipt.json](/home/linjiw/lucid-sonic/analysis/optimizer_history_numerical_20260905_a/receipt.json). The original checkpoint and running experiment were read only.

Reproduce with a fresh output directory:

```bash
export LUCID_REPO=/home/linjiw/lucid-optimizer-history
source /home/linjiw/lucid/env/lucid_env.sh
cd "$LUCID_REPO"
python scripts/practice_utility/validate_optimizer_history.py \
  --checkpoint /home/linjiw/lucid-sonic/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260829_000249/seed_8600/fixed/final_checkpoint.pt \
  --output-dir /home/linjiw/lucid-sonic/analysis/optimizer_history_numerical_reproduction
```

## Prospective simulator comparison

If the fixed-initial run breaches origin-relative retention, compare fresh history and restored history using the same solved policy/value weights, fresh environment reset, local iteration counter zero, seed, initial cohort mixture, motion, PPO/reward configuration, and 2,000-iteration budget. Start both arms through the same new launcher and audit path. Preserve scheduler initialization and its configured update law in both arms, and record realized learning rates; the restored arm must not import the source scheduler or a source training counter. The treatment includes Adam's moments **and bias-correction counters**, not moments alone.

Before launching, close the following implementation requirements:

1. Recover and independently audit the historical source optimizer's ordered **named** parameters against the pinned source model and optimizer-construction code. The old checkpoint has positional optimizer IDs. The CPU experiment's synthetic slot labels are not a substitute. Bind the recovered manifest to checkpoint/config/source hashes, then require exact recipient name order and shape agreement. If source ordering cannot be established, do not claim a clean history-only intervention.
2. Add an opt-in runtime seam after policy/value loading and optimizer construction, before the first rollout. Validate zero recipient training updates, matching model weights, and fresh optimizer state. Record restoration evidence and fail on conflicting full-resume settings.
3. Run a symmetric smoke with and without restoration through that seam. Verify the fresh arm's no-op parity against the existing path, parameter mapping, preserved initial learning rates/scheduler/counters, exact DR assignment, and valid capsule/evaluation exports. Numerical CPU parity alone does not satisfy this simulator gate.
4. Freeze a new immutable two-arm plan before its long outcomes. Preserve clean snapshot evaluations and all five endpoint conditions, with the same completion and pose margins. Report all training, probe, and startup costs. Use the existing initial-hold result as development evidence; a freshly executed matched pair avoids mixing old/new runtime seams in the causal comparison.

Primary development question: whether restored history reduces clean global and local tracking degradation relative to the fresh-history control and meets the origin-relative retention margins. Held-out tracking-qualified success remains visible to expose a retention/robustness tradeoff. One paired seed can diagnose this setting; it cannot establish a general method effect. A favorable result requires subsequent independent origins before a broad claim.

If holding initial exposure already retains quality, prioritize the origin-relative expansion-veto experiment. The history component remains available for later sensitivity analysis. If restoration fails to preserve quality, investigate retained-condition coverage and tracking incentives with separate interventions; avoid bundling a reference-policy loss, retention practice, and optimizer changes into an uninterpretable single treatment.

Recovery and dynamics-history feedback remain later stages: first demonstrate incremental prediction of recoverability and quality failure on held-out policy stages/processes, then test scheduling value with the actor fixed. No sim-to-real claim follows from this CPU experiment or the one-motion simulation diagnostic.
