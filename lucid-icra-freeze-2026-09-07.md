# ICRA diagnostic-paper science freeze — September 7, 2026

**Execution update:** the original R0 training completed; a W&B serialization error stopped orchestration afterward. The [logging repair and R1 continuation](lucid-retention-replication-repair-2026-09-07.md) preserve the science contract and original failed receipt. A seven-page PDF, five figures, reference identity audit and simulation-video draft are now prepared.

This execution contract applies the current `fable.md` and `fable.html`. The submission is **When Training Gets Easier: Range Collapse and Tracking Drift in Humanoid Robustness Training**. Recovery-aware curriculum development remains a separate future programme.

## Frozen claim–evidence map

| Claim | Evidence | Boundary |
|---|---|---|
| Adaptive range collapse can accompany increasing return | Six adaptive runs, two collapses; twelve scored runs, Spearman −0.73; collapse costs 14.19 AUC points versus paired fixed | Association and the tested feedback mechanism, not every ADR algorithm |
| Never-shrink blocks the observed contractions | 2,033 requests blocked across three seeds; mean difference +0.60, SD 2.25 versus fixed | Empirical tolerance decision; one-sided 95% lower bound −3.19 does not establish noninferiority or equivalence |
| Completion can conceal tracking loss | Original R0/R1/R2 screen: all nominal completion 100%; origin 127.93 mm, R0 225.87 mm global MPJPE | One origin, one motion; global error does not identify a unique compensation |
| Reference anchoring gives a protected development baseline | R1 endpoint 133.47 mm (+4.33%), all five sampled retention gates pass, hard qualification +5.18 pp versus origin | No curriculum advantage; added anchor computation; no recovery/hardware claim |

The September 5 frontier pilot uses a different evaluation panel: 128.57 → 324.50 mm for its gate, not 127.93 → 324.50. These denominators must not be mixed. Optimizer-history controls show drift in both branches; they do not uniquely identify PPO reward gradients as the cause. Marginal range nesting rules out unseen scalar values, not all scheduling benefits or all explanations of null results.

## Only new GPU work: second continuation seed

- Source checkout: `/home/linjiw/lucid-retention-second-seed`, commit `886c347`.
- Driver: `scripts/practice_utility/run_retention_second_seed.py`.
- Frozen plan: `/home/linjiw/lucid-sonic/experiments/retention_second_seed_20260907_b/pilot/plan.json`.
- SHA256: `f2ca969140d232579c70c8127df2c6ee775cf00917f3667ce976d9a17afd3f86`.
- Two training cells, R0 then R1, and 55 evaluation cells. Each arm: 1,024 environments × 24 transitions × 2,000 iterations = 49,152,000 transitions.
- PPO/environment seed changes 8600 → 8601. Origin, original motion, anchor buffer, cohort assignment seed 8600, anchor sampling seed 8610, evaluation seed 8700, thresholds, five conditions and checkpoint schedule remain fixed.
- Checkpoints: 250, 500, 1,000, 1,500, 2,000. Evaluate nominal, original envelope, Push 3×, Push 3.5×, and Push 3.5× plus friction 1.5×, 512 aliases each. No R2 replication or parameter search.
- Primary readout: per-checkpoint empirical retention. Hard-condition tracking qualification is secondary. Report both seeds separately before any across-seed summary; neither is an independent origin.
- Existing CPU suite: 2,022 passed, five warnings. New replication-contract tests: six passed. Plan input/code hashes verified before launch. Attempt `_a` was an unlaunched preflight plan superseded by formatted/tested source in `_b`; it produced no results.
- [Online W&B R0](https://wandb.ai/16726/lucid-sonic/runs/5zucanmo), group `retention_second_seed_20260907_b`. The executor opens a named online run before each training/evaluation cell and mirrors training console metrics. Receipts retain each run URL and validation.
- GPU gate: at least 11,000 MiB free, maximum 30-minute admission wait. No unrelated GPU processes are stopped. Do not reopen a broad campaign if the pair fails or misses the September 9 evidence cutoff.

Launch command (after sourcing `env/lucid_env.sh` with the checkout selected):

```bash
python -u scripts/practice_utility/run_retention_second_seed.py \
  --plan /home/linjiw/lucid-sonic/experiments/retention_second_seed_20260907_b/pilot/plan.json \
  --sha256 f2ca969140d232579c70c8127df2c6ee775cf00917f3667ce976d9a17afd3f86
```

## Writing and submission work

The manuscript has been reframed and reduced from approximately 7,000 to 4,330 words before figures. The earlier draft is preserved in `paper/archive/`; identifying provenance is separated into `paper/evidence-ledger.md`. The working manuscript still requires typesetting, reference checks, figure placement and a final claim review. No submission has occurred.

The official call, checked September 7, requires eight total pages including references and double-anonymous review. It does not support a separate supplementary PDF. Video windows are August 5–September 9 and September 17–22, with uploads unavailable September 10–16. The paper deadline is listed as September 15, 2026, “11:59 PST”; target an earlier submission rather than interpreting the ambiguous daylight abbreviation at the last minute. Video requirements: at most 20 MB/180 seconds, at least 480-pixel height and 20 fps, progressive MP4/MPEG/MPG.

[Official ICRA 2027 call](https://2027.ieee-icra.org/contribute/call-for-icra-2027-papers-now-accepting-submissions/).

## Completed engineering archived as future work

The path-input pilot completed 128 iterations and all 16 initial/final evaluation cells. Mean nominal tracking errors improved on all four development motions. Sideways disturbed completion fell from 128/128 to 126/128. No calibrated recovery bands exist; this is not recovery efficacy. The released controller and new path input are different from the local origin supporting this paper. Preserve their receipts without inserting them into the main comparison.

Next deliverables are the diagnostic figures, anonymous eight-page PDF, reference/claim audit, and second-seed results when available. Do not launch observer training, motion adaptation, additional path repair, utility allocation, or hardware trials under this freeze.
