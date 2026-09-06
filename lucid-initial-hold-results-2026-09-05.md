# LUCID fixed-initial-DR diagnostic: completed results and next control

The diagnostic completed all 12 cells at **2026-09-06 01:43:50 UTC** (September 5 EDT). Training held the initial E0 cohort distribution fixed for 2,000 iterations. Expansion is not necessary for clean-tracking degradation in this setting: global MPJPE rises **28.20%** relative to the solved origin. Holding the initial mixture nevertheless produces substantially smaller drift than the prior expanding/hard-support pilot. This is one development seed, one G1 hands-on-back motion, and simulation only.

## Retention trajectory

The frozen retention rules allow at most a two-point completion loss and 10% increases in clean global/local MPJPE relative to the reference. The supplemental diagnostic applies those margins to the origin. It is an engineering screen, not a statistical non-inferiority test.

| Iteration | Clean completion | Global MPJPE | Local MPJPE | Global change vs origin | Both pose margins pass |
| ---: | ---: | ---: | ---: | ---: | --- |
| Origin | 100.00% | 128.57 mm | 28.33 mm | — | Reference |
| 250 | 99.80% | 118.25 mm | 28.95 mm | −8.03% | Yes |
| 500 | 100.00% | 146.72 mm | 29.44 mm | +14.12% | No |
| 1,000 | 100.00% | 141.17 mm | 28.95 mm | +9.80% | Yes |
| 1,500 | 100.00% | 183.99 mm | 30.27 mm | +43.10% | No |
| 2,000 | 100.00% | 164.83 mm | 29.59 mm | +28.20% | No |

The first **observed** breach is at 500 iterations. The 1,000-iteration point returns just inside the margin before a later breach. Thus observed drift is not monotone; the snapshot grid cannot determine exact onset, persistent failure, or retention between checkpoints. The single failure at 250 remains visible; that stage's matched-subset probe-resolution analysis is ineligible because truncated episode means cannot certify full-motion retention.

Final clean completion and tracking-qualified success are both 100%. Qualification uses the much looser 600 mm global/50 mm local thresholds, so it does not establish preservation of the starting policy's tracking accuracy. The continuous origin-relative signal is essential here.

## Frozen endpoint outcomes

Each evaluation has 512 matched aliases of the same motion, with evaluation seed 8700. Aliases are simulator replicates, not independent motions or training seeds.

| Condition | Completion | Tracking-qualified success |
| --- | ---: | ---: |
| Clean | 100.00% | 100.00% |
| Standard mixed DR | 98.83% | 96.88% |
| Push 3× | 75.59% | 60.35% |
| Push 3.5× | 65.04% | 48.24% |
| Push 3.5× + Friction 1.5× | 55.47% | 39.06% |

The frozen two-cell held-out tracking average is **43.65%**. For descriptive context, the previous pilot measured static 39.16%, replay 37.01%, and gate 40.33%. Fixed initial exposure is therefore +4.49, +6.64, and +3.32 points respectively on this development comparison. These cross-campaign descriptive differences do not establish superiority across independent origins.

On the directly shared Push 3.5× condition, origin completion/qualification were 64.84%/49.02%, versus 65.04%/48.24% after the diagnostic. There is no meaningful demonstrated improvement over the origin on that cell. The origin lacks the composition evaluation, so no origin-relative two-cell average is inferred.

Training subprocess time was **9,686.06 seconds (2.69 hours)**; evaluations totalled **431.22 seconds (7.19 minutes)**. Total campaign elapsed time was about 2 hours 49 minutes. These shared-GPU wall times do not establish uncontended throughput.

## Research decision

A veto that merely prevents expansion cannot by itself guarantee retention: the no-expansion mixture still drifts. Investigate the training-retention mechanism before deploying a more elaborate curriculum controller. The tested mixture includes low strata, a frontier at 1.0, and the fixed initial 1.125 joint-offset probe; it is not a reconstruction of the origin's original training distribution. Distribution shift, reference coverage, optimization history, and tracking incentives remain possible contributors.

The next matched control restores AdamW history while preserving fresh environment/scheduler/trainer initialization. This isolates one candidate contributor. Any useful future curriculum must track continuous reference-relative quality, retained-condition completion, and target competence separately. Recovery and dynamics-history features remain prediction-gated later additions, especially for temporally uncertain DR. No utility selector or residual allocator is authorized by these results.

## Implementation and next launch

Commit `e981e97` in `/home/linjiw/lucid-optimizer-history` adds a reconstructed source parameter binding, an opt-in before-rollout history callback, and a paired fresh/restore driver. The full CPU suite passed **1,940 tests**, four warnings, 52.14 seconds. Black/Ruff and whitespace checks pass. The initial smoke attempt has not yet established simulator integration.

The mapping audit found that exported `model_config.yaml` alphabetizes encoder keys. Using that ordering gives wrong optimizer correspondence even though policy weights load by name. The reconstruction instead uses the **original training config** for module registration and only the export's resolved environment dimensions. It strictly loads all policy/value state, matches complete checkpoint registration order, and verifies all 69 optimizer moment shapes in groups 35/34. Runtime additionally requires exact live optimizer names, equal starting weights, fresh optimizer state, zero local training iteration, and matching initial learning rates.

The source checkpoint has no historical named-optimizer metadata or populated capsule source-commit field. The binding is explicitly a reconstruction under the pinned model/Transformers grouping implementation, not recovered original metadata. This provenance limitation remains in the binding receipt. Synthetic numerical parity does not replace live mapping and smoke checks.

The next campaign starts with 10 smoke cells: origin evaluations and two 16-iteration arms, each with an eight-iteration clean snapshot and clean/Push-3.5× endpoint evaluations. A hard gate then requires all 55 policy and 17 value tensors in the fresh arm to equal the previous initial-hold smoke checkpoint exactly. Any failed cell, input change, or failed parity stops the supervisor without retry.

Only after that gate and verified smoke analysis, the supervisor launches the frozen **22-cell paired pilot**: 2,000 iterations per arm, four intermediate clean snapshots per arm, and five endpoint conditions per arm. The two arms use the same initial DR assignments, origin, seed, motion, 1,024 environments, PPO settings, and scheduler initialization/update law. Restored history includes first/second moments and Adam bias-correction counters; it does not restore a source learning rate, scheduler, environment, or global training counter. All starting and realized learning rates remain auditable.

Given prior measurements, budget approximately 3–5.5 training wall-hours for the pair plus evaluations and capacity waiting. The immutable driver queues at 11,000 MiB free GPU memory and does not terminate other jobs. Monitoring and final analysis run automatically, with local outputs only.

Supervisor PID **1569403** started at **2026-09-06 02:02:59 UTC**. Plans:

At 02:04:59 UTC the first smoke evaluation was **waiting for GPU capacity**, with no simulator cell yet complete and no monitor warnings. Launching the supervisor does not mean training has begun; current receipts and the live status distinguish capacity waiting from simulator execution.

- Smoke: `/home/linjiw/lucid-sonic/experiments/optimizer_history_smoke_20260905_a/plan.json`; SHA-256 `863f4c831b483c099b32612a32fa18cc7224781ffe10fe8b8182713d537cd96d`.
- Paired pilot: `/home/linjiw/lucid-sonic/experiments/optimizer_history_pilot_20260905_a/plan.json`; SHA-256 `4bceec920b0a0399f75d90d1a5b4f880f227f4f7b4af9506a391a3ef8f19a00c`.

Current schedule: [campaign status](/home/linjiw/lucid-sonic/experiments/optimizer_history_campaign_20260905/status.json). Source binding and launch details are in the same directory. Completed diagnostic: [verified report](/home/linjiw/lucid-sonic/analysis/initial_hold_retention_20260905_a/report.md) and [receipt](/home/linjiw/lucid-sonic/analysis/initial_hold_retention_20260905_a/receipt.json); both original and supplemental analysis output hashes were reverified before interpreting the result. Generated checkpoints and experiment data remain outside Git.
