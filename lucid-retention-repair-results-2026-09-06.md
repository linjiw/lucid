# Retention repair: completed development results

**Latest analysis, September 7, 01:06 UTC:** R1 remains the selected protected baseline from the completed 83-cell development screen. The four-cell contact diagnostic is complete. The separately preregistered eight-cell execution/retention parity campaign now passes all four pairs, covering 1,024 evaluation aliases and 380 aligned nonzero push events. Contact diagnostics remain unvalidated and the original all-metric gate remains failed. Recovery-band calibration and feedback efficacy are next. See the [research-direction update](lucid-research-direction-update-2026-09-07.md).

The implementation and runtime snapshots below are retained as historical evidence.


Campaign `_c` completed September 6, 2026 at 22:52 UTC (18:52 EDT). All 83 long-screen cells finished: three 2,000-iteration continuations and 80 frozen-policy evaluations, totaling 40,960 scored episode aliases. The earlier 16-cell smoke also passed.

**Decision: carry R1, the reference-anchored fixed-practice recipe, forward as the protected baseline.** It is the only tested arm that passes the empirical clean and original-envelope retention checks at all five sampled checkpoints and improves the two-condition held-out tracking-qualified score at the final checkpoint. This is a development selection from one solved origin and one motion, not confirmation of a recovery observer or a feedback curriculum.

| Final policy | Clean global error (mm) | Change from origin | Clean local error (mm) | Held-out tracking-qualified score | Retained at every sampled checkpoint? |
| --- | ---: | ---: | ---: | ---: | --- |
| Frozen origin | 127.93 | +0.00% | 28.19 | 42.77% | Reference |
| R0: unanchored continuation | 225.87 | +76.56% | 30.21 | 49.02% | False |
| R1: reference anchoring | 133.47 | +4.33% | 27.96 | 47.95% | True |
| R2: lower fixed learning rate | 163.53 | +27.83% | 28.31 | 53.42% | False |

All four policies complete the clean evaluation at 100%; completion alone therefore hides the substantial R0/R2 global tracking degradation. R1 clean global error changes by +4.33% and local error by −0.83%. In the original envelope, R1 global error changes by +2.52%, local error by −0.67%, and completion by +0.39 percentage points.

The held-out score is the equally weighted tracking-qualified rate across Push 3.5× and Push 3.5× plus friction 1.5×. Origin scores 42.77%; R1 scores 47.95%, a +5.18 percentage-point improvement. R0 gains +6.25 points and R2 gains +10.64 points, but both exceed the retention budget. R1 therefore trades some of their unconstrained robustness gain for retained clean tracking; it does not dominate every metric.

## What the gate establishes

The frozen retention rule checks empirical episode-mean global/local error increases of at most 10%, and completion losses of at most two percentage points, separately in nominal and original-envelope conditions. R1 passes at 250, 500, 1,000, 1,500 and 2,000 iterations. The stored standard errors are descriptive fixed-look episode uncertainty. These passes are not simultaneous confidence guarantees or independent-training replication.

Tracking qualification uses the preregistered development episode-mean thresholds of 600 mm global and 50 mm local MPJPE. Those are not recovery, task-phase, or hardware tolerances. The reported +5.18 points is versus the frozen origin. It is not the future +5-point feedback-versus-protected-fixed curriculum target, and cannot satisfy that unrun comparison.

## Resources and remaining limits

Each training arm receives 49,152,000 simulator transitions. R1 additionally performs 40,000 anchor updates, 10,240,000 anchor sample presentations and 80,000 student forwards, with 207.37 seconds recorded inside those forwards. Thus transitions are matched, while total optimization work is not. Training wall times differ under shared-GPU conditions and do not establish an efficiency advantage. Collection, smoke, optimizer diagnosis and failed attempts remain separate development costs.

One development origin, one walking motion, and one evaluation seed support this result. The 512 aliases per condition improve rollout measurement; they do not create 512 independent trained policies. Event recovery, motion generalization, cross-origin confirmation, feedback benefit, independent-simulator transfer and hardware remain unverified.

## Next authorized stage

Use R1 as the common retention recipe for later fixed, frozen-schedule and feedback comparisons. First run the eight-cell frozen-origin recorder-off/on measurement test (two conditions × two development seeds × 128 aliases per mode). That experiment changes recording only and can fail without changing the retention finding. After valid event traces, collect development calibration data and freeze phase bands, dwell/horizon, overlap policy and causal dataset splits before observer training or grading policies.

## Evidence

- Full all-cell report: `/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_c/analysis/report.md`.
- Analysis and provenance: `/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_c/analysis/analysis.json` and `receipt.json`. All 120 input hashes were rechecked with no mismatch.
- Tradeoff figure: [PDF](/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_c/analysis/robustness_retention.pdf).
- [W&B campaign](https://wandb.ai/16726/lucid-sonic/runs/ret-46911b8054776113fe91).
- [Native recovery measurement status](lucid-native-recovery-capture-status-2026-09-06.md).

Execution update, September 7 00:24 UTC: the measurement campaign has been launched under its serial supervisor and is initially queued for GPU capacity, with [online W&B logging](https://wandb.ai/16726/lucid-sonic/runs/rec-3ae0529d4649aaef377c). No measurement result has yet passed.

At 00:26 UTC, the first measurement cell had completed (1/8), and the second was waiting for shared-GPU capacity. No paired parity verdict is available yet.
