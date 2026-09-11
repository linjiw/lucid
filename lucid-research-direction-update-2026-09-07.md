# Research direction after the retention screen and live recorder diagnosis

**Common-controller update, September 7 UTC:** Released SONIC solves the four development motions. The common path-input migration now passes a versioned live same-state gate with zero action difference across 217,728 comparisons; both earlier cross-process gates remain failed. The protected four-motion PPO pilot completed all 128 iterations. Initial/final nominal and push evaluation is now running. See the [experiment ledger and limitations](lucid-common-path-input-status-2026-09-07.md) and [live W&B run](https://wandb.ai/16726/lucid-sonic/runs/wnb1cavy).

**Physical observability result, September 7 UTC:** The four-motion/three-phase physical-state experiment completed. All 6,144 horizontal translations changed measured task/critic displacement while active actor inputs, encoder outputs and action means remained exactly unchanged; instrument controls passed. The next step is a common path-error input, no-op validation and a bounded controller-repair pilot before multi-motion R1/curriculum training. See the [completed experiment](lucid-translation-observability-2026-09-07.md) and [common-input design](lucid-common-path-input-design-2026-09-07.md).

**Controller-foundation result, September 7, 03:14 UTC:** All eight released-controller cells completed: 100% completion and tracking qualification on all four development motions in both native and LUCID paths. The local origin/R1 had qualified on none of the three longer candidates. Select the released weights as the shared-origin candidate; validate tighter competence and horizontal recovery-error observability before multi-motion R1 continuation. See the [complete comparison, next-stage contract and evidence](lucid-shared-origin-contract-2026-09-07.md).

**Completed longer-motion screen, September 7, 01:57 UTC:** All eight cells finished. Both origin and R1 have 0% tracking-qualified execution on all three longer development motions. Curved walking and sideways walking largely survive but fail quality; stooping has 0% completion. The control passes retention (+8.79% global, -0.97% local). Establish a high-quality shared multi-motion origin before recovery calibration. The [current public page](https://linjiw.github.io/lucid/) reports all outcomes and the revised roadmap.

September 7, 2026 UTC. Evidence-led update to the [ideal-paper plan](lucid-ideal-paper-execution-plan-2026-09-06.md). This changes prospective priorities and explicitly versions the measurement gate; it does not rewrite completed results.

## What the results support

**Keep the target: faithful recovery with retained motion quality. Use R1 as the protected fixed-practice baseline, then test whether feedback adds value.** R1's success raises the standard for the curriculum comparison: future feedback must improve on a controller that already receives the same retention mechanism.

The 83-cell retention screen supports a useful development result. R1 stays within empirical clean and original-envelope retention budgets at all five sampled checkpoints. Its final held-out tracking-qualified score improves from 42.77% to 47.95%, while clean global error rises 4.33% and local error falls 0.83%. R0/R2 gain more unconstrained robustness but fail retention. This is one origin, one motion, and one evaluation seed. The +5.18 points is against the frozen origin, not against protected fixed practice; it cannot satisfy the future feedback-versus-fixed effect target.

Two details matter for the paper:

1. R2 still has 100% nominal tracking-qualified completion under the broad 600/50-mm development thresholds, despite +27.83% clean global error. Absolute qualification and origin-relative retention answer different questions. Neither completion nor a single qualification scalar replaces the retention constraints.
2. R1's closest sampled clean-global margin is at 500 iterations: +7.35%, leaving 2.65 percentage points under the 10% empirical budget. Its mean difference from 1.10× origin is −3.39 mm, with descriptive standard error 1.87 mm. This is not a simultaneous confidence guarantee. Its hard-condition score is also non-monotonic: 50.10% at 500 versus 47.95% at the frozen 2,000-iteration endpoint. Keep the endpoint; do not select the earlier favorable checkpoint after seeing the trajectory.

The contribution we still need is the incremental value of recovery information for training decisions. Anchoring, broader randomization ranges, a positive latent correlation, or more evaluations cannot substitute for that experiment. If direct error/history features are sufficient, use them and narrow the observer claim.

## What happened to the recorder gate

The original eight-cell instrument campaign stopped after its first off/on pair. Both cells executed 128 aliases for 200 native steps. Every recorded native audit byte matched, including action-manager inputs, observations, rewards, terminations/timeouts, reference/executed tracked poses and RNG state. One metric differed: accumulated contact telemetry changed by 6.55×10⁻⁸, approximately 2.36×10⁻¹¹ relative. The original all-metric-exact gate remains **failed**.

A separately frozen four-cell diagnostic then ran off/off/on/on at the same nominal seed, capturing raw contact forces while preserving the existing calculation. All six pairwise execution audits match exactly. Raw contact inputs do not: even off/off differs in 3,429 tensor elements across 188/200 steps, with maximum absolute difference 0.0001220703125 N. CPU replay of the differing inputs also differs. The discrepancy therefore is not solely a downstream reduction artifact and cannot be attributed solely to toggling the recovery recorder. The underlying simulator mechanism is not identified by this experiment.

This warrants a **new, narrower execution-parity gate**, not a retroactive pass or a wider numeric tolerance. The version-two protocol requires exact native audits and all metrics except five explicitly named contact-sensor-derived diagnostic outputs: impulse proxy, peak contact force, undesired-contact rate, and the two foot-slip aggregates. Those values and the full all-metric equality verdict remain reported. Action, actuator, missing-signal metadata, delay, tracking, retention and outcome comparisons remain exact. No physical safety claim follows from passing this gate.

The amendment was frozen before new runs. The new eight-cell campaign **completed and passed all four version-two pairs**, using seeds 8720/8721, nominal/original-envelope conditions and 128 aliases in each recorder mode: 1,024 evaluation aliases total. It recorded 760 uniquely identified, aligned interval events, including 380 nonzero original-envelope velocity increments. No checked event changed pose inside the velocity-write call. All full-metric equality flags remain false because of contact telemetry; this does not alter the version-two execution verdict or rehabilitate the original gate. Total measured evaluation wall time was 349.51 seconds, excluding capacity waits and development preparation. [W&B campaign](https://wandb.ai/16726/lucid-sonic/runs/rec-f60769da7efb7f7431e1); [verified analysis](https://wandb.ai/16726/lucid-sonic/runs/rec-execution-analysis-20260907-a).

## The next data bottleneck is recovery-window coverage

The recorded four-second nominal clip contains 191 interval events, all with zero velocity increment. They demonstrate event capture, not disturbance recovery. Quarter-phase counts are 0/54/84/53. Only 31/191 events have at least two seconds of uninterrupted observed trajectory before the next event, segment boundary or trace end; 138/191 have at least one second. A two-second endpoint would leave most events unresolved in this capture. These are descriptive coverage counts, not recovery rates.

Do not choose a shorter horizon merely to obtain more favorable labels. Select a task-relevant recovery horizon, then provide sufficient motion duration and event placement to observe it. Reference resampling writes simulator state and ends the segment; it cannot be used to extend a recovery window across a teleport.

A metadata-based inventory found 26 clips of at least eight seconds among walking/crouching candidates in the existing adaptation/development splits: 16 adaptation and 10 development. Source motion content, frame counts, FPS and file hashes were verified. No clip from the existing test split was selected. These are candidates, not demonstrated nominal capabilities; names/family labels are insufficient to establish motion semantics. The turn/exercise categories have no qualifying non-test clip under this duration filter. Composition, a different horizon, or another documented motion source requires separate validation.

## Next work, in order

| Stage | Concrete next work | Evidence required before proceeding |
| --- | --- | --- |
| G1 execution check completed | All eight cells and four exact execution/retention pairs pass; 380 nonzero events have matching phase/time/segment identity | Preserve the original failed gate and contact limitations; recovery calibration remains open |
| Establish usable observation windows | Screen candidate reference durations and origin nominal capability; preregister an isolated-push timing protocol that leaves the chosen horizon and dwell observable | Adequate phase coverage, explicit boundary/overlap accounting and no invented recovery from reset frames |
| Calibrate quality components | Use origin-only calibration episodes, separate validation episodes and explicit task tolerances; report translation, heading and articulation separately | Frozen phase bands, dwell, horizon and failure/censoring rules before grading continued policies |
| Test recovery prediction | Split complete episodes/motions/origins before windows; compare current errors, derivatives, simple history and a strong same-history predictor before a new encoder | Held-out predictive/calibration benefit beyond direct features; no future-input leakage |
| Test feedback value | Protected fixed vs development-frozen schedule vs quality/recovery feedback, all with the same R1 retention recipe | Prespecified qualified-execution endpoint improves under a shared total-resource contract and all retention constraints |
| Broaden the result | Additional development learning seeds, then fresh solved origins and shared multi-motion training, temporal/combination transfer, independent simulator and hardware | Distinguish same-origin continuation-seed replication from independent-origin confirmation and unseen pretraining data |

The next training comparison should answer an identified learning question. Do not launch a large encoder or curriculum grid while labels and observation windows remain unresolved. CPU preparation and bounded simulator measurements can proceed now. The utility estimator and residual allocator remain gated.

## Resources and evidence locations

Each retention arm used 49,152,000 simulator transitions. R1 additionally used 10,240,000 anchor sample presentations and 80,000 student forwards. Account for these, origin-buffer collection, probes, observer training, measurement overhead and failed development attempts. Shared-GPU wall times do not establish an efficiency ranking. The four contact repeats add 512 diagnostic episode aliases; they are not additional independent trained policies.

- [Retention results and full evidence links](lucid-retention-repair-results-2026-09-06.md).
- Original failure/coverage receipt: `/home/linjiw/lucid-sonic/analysis/recovery_noop_diagnosis_20260907_a/diagnosis.json`.
- Raw-contact diagnostic: `/home/linjiw/lucid-sonic/experiments/contact_repeatability_20260907_a/analysis.json`; [W&B](https://wandb.ai/16726/lucid-sonic/runs/contact-4ea486de9cb8a553).
- Versioned gate amendment: `/home/linjiw/lucid-sonic/analysis/recovery_execution_gate_amendment_20260907_a/amendment.json`.
- New frozen plan: `/home/linjiw/lucid-sonic/experiments/recovery_execution_v2_20260907_a/plan.json`, SHA-256 `f60769da7efb7f7431e18e1b67a7e5bb560efcea17416afd4e4feb4fc3b6560a`.
- Motion inventory: `/home/linjiw/lucid-sonic/analysis/recovery_motion_inventory_20260907_a/inventory.json` and `candidates.csv`.
- Contact diagnostic source `877bac8`: 2,113 CPU tests passed. Execution-gate source `84dfd53`: 2,111 CPU tests passed in its separate worktree. Both include their new focused contracts; counts differ because the diagnostic-only module is not part of the production measurement worktree.

Final validation: all 11 frozen input files and 1,208 source files match their plan hashes. The completed execution report and receipt are `/home/linjiw/lucid-sonic/experiments/recovery_execution_v2_20260907_a/analysis.json` and `analysis_receipt.json`. No learned recovery model or new continuation training was launched in this measurement stage.
