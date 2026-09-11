# LUCID after the 2,000-iteration baseline

September 11, 2026. SONIC only; one motion, `walk_hands_on_back_loop_002__A066_M`. This note continues the [method specification](lucid-ued-methods-and-baseline-2026-09-11.md). Results below are development evidence, not hardware transfer or a comparison of learned curricula. **All 47 evaluation cells are complete; see the final status and next-comparison decision at the end.**

## Training audit and recovery

The protected R1 continuation with seed 8612 completed 2,000 PPO iterations: 49,152,000 student transitions and 40,000 optimizer updates. Its process exited successfully. Wall time was 6,910.12 seconds including startup/export. The anchor added 10,240,000 sample presentations in 80,000 forward calls; measured anchor forward time was 228.50 seconds. These are extra computations, not additional environment transitions.

The original launcher then failed to parse an absolute Rich-wrapped logging directory. The resolved configuration and all five checkpoints existed. Recovery uses the explicit directory from the recorded training command, runs the original training validator, and checks exact tensor equality between the previous and recovered final exports. The original plan, training log, capsules and failed receipt remain preserved. A second recovery attempt encountered integer keys in nested W&B summaries; its failure is also retained. JSON-normalizing those keys fixed receipt publication.

- Training: [verified online run](https://wandb.ai/16726/lucid-sonic/runs/ued-1fc8d3b06340c154).
- Original plan: `/home/linjiw/lucid-sonic/experiments/latent_ued_baseline_20260911_a/plan.json`, SHA256 `eb5148d7a1052cdc1d67140adfcec0c97d3b45718a66f99e54fda5a5b76631bb`.
- Active recovery receipt: `/home/linjiw/lucid-sonic/experiments/latent_ued_baseline_recovery_20260911_c/receipt.json`.
- Final checkpoint: `/home/linjiw/lucid-sonic/experiments/latent_ued_baseline_20260911_a/train_R1/final_checkpoint.pt`, SHA256 `79a50190eb5f5030cafe39a517b65ed1a7d9618a3723c224ac9ae2527253c0b8`.
- Original training/evaluation source remains `/home/linjiw/lucid-latent-ued`, commit `a42dd61975222ac74eeb17cf3253aeaf8210b2a3`, checked against the frozen plan before each cell.

The machine's loaded NVIDIA kernel module is 595.84 and its installed userspace libraries are 595.91.07. NVML and renderer discovery fail, but CUDA allocations and headless physics evaluation work. Recovery explicitly substitutes `cudaMemGetInfo` for memory capacity checks and reports GPU utilization as unavailable. No system driver replacement or reboot was performed. The resulting timing cannot be used as a clean throughput benchmark.

## Fixed-panel evaluation protocol

The unchanged plan evaluates the origin and iterations 250, 500, 1,000, 1,500 and 2,000 under five conditions, each with 512 aliases of the same motion. This is 30 cells and 15,360 episode aliases, not 15,360 independent training runs. The conditions are nominal, inherited full-range physics DR with zero actuator delay, push scale 3×, push scale 3.5×, and the inherited combined push/friction condition. The last three are legacy event semantics, not the new shared-transport latency bursts.

Retention requires completion no more than two percentage points below the origin and mean global/local tracking errors no more than 10% above it, at both nominal and inherited DR conditions for all five saved checkpoints. These are the previously specified empirical margins, not sequential confidence guarantees. All observed episodes contribute to errors; failed episodes have shorter observation windows. Survival and tracking-qualified completion are reported separately.

The analysis script produces fixed-distribution curves and paired alias bootstrap intervals. These intervals describe within-panel variation for this continuation seed; they do not quantify variation across training seeds. No endpoint is selected by stress-test performance. The final checkpoint stays the predeclared endpoint if the retention gate passes.

Training reward alone is inconclusive: average reward decreased from 10.86 in iterations 1–250 to 9.41 in 1,751–2,000 while average episode length increased from 180.73 to 185.45. The final two 250-iteration blocks have similar mean reward/length, but that does not establish convergence in robustness or tracking. Fixed-panel curves are the relevant next evidence.

## Timed-disturbance instrumentation

The next frozen-policy development panel uses 128 aliases, disjointly keyed validation event tapes and a fixed evaluation seed. Conditions include isolated and combined planar velocity increments of 0.5, 1.0 and 1.5 m/s, and action-transport bursts of 20, 40 and 60 ms. Onsets vary across episodes; no future event schedule is added to the actor. A velocity increment is not a measured force impulse.

The transport applies the newest arrived physical joint-target packet and discards obsolete arrivals. Packets are reissued each 5 ms physics tick. This is explicitly different from a control-rate network model and from the baseline's independent actuator-group delay. Unseen temporal processes and out-of-range lag must be labeled separately.

The native evaluator performs an additional reset after callback setup. The runtime therefore binds scored episode IDs immediately before the first evaluation step. Post-failure automatic replay episodes cannot contribute to perturbation-exposure counts. CPU tests cover this identity rule, exact queue timing, reset isolation, missing/duplicate push writes, incorrect velocity increments, and partial exposure.

Before perturbed cells, native versus no-op metrics must match exactly. Every perturbed cell then audits commanded packet ages against the specified burst process, checks push write time and magnitude, and reports how many scored episodes actually reached each event. A policy that falls before the push still fails unconditional evaluation; it cannot count as having survived a push.

Follow-up source is frozen separately at `/home/linjiw/lucid-ued-eval-20260911`; the source manifest is `/home/linjiw/lucid-sonic/manifests/ued_eval_source_snapshot_20260911.json`. Its watcher state is `/home/linjiw/lucid-sonic/experiments/latent_ued_followup_20260911_b/state.json`. It reads the recovered baseline receipt, verifies metric hashes and stops if retention fails.

## Research decision: execution information should inform the teacher, not define its reward

The main comparison should keep task outcomes, reference rehearsal, policy architecture and teacher loss fixed, then add either filtered execution features or learned execution features. Avoid rewarding the teacher for producing a large latent gap. That objective could favor incoherent commands, benign PD loading, or tasks the student cannot learn. A latent veto is a separate ablation: it might suppress useful difficult practice even when tracking remains competent.

Use three explicit components:

1. **Task and exposure state:** assigned push/delay process, realized episode/event counts, score age and replay frequency. Missing exposure cannot be interpreted as successful practice.
2. **Competence state:** unconditional tracking-qualified completion, observed tracking error, independent recovery and retained reference performance. Failure, low-quality completion and early termination remain distinct.
3. **Execution features:** issued–measured and applied–measured temporal residuals, calibrated by nominal reference phase, plus persistence and change. Keep transport age and effort as diagnostic/context channels. No individual feature certifies stability.

The decisive question is whether adding learned execution features improves later fixed-panel outcomes beyond adding equally calibrated causal filtering. Prediction of failure is a prerequisite diagnostic, not sufficient evidence of curriculum benefit. An additional supervised failure predictor must have equally supervised nonlatent controls.

For this small disturbance bank, begin with explicit task descriptors. GACL's task VAE compresses the task domain; it is a different object from LUCID's execution encoder. A finite-bank GACL-inspired teacher should be named as an adaptation. Compare last-task/performance context first; recurrent history is an additional experiment, not assumed to reproduce the paper's reported teacher. [GACL](https://arxiv.org/html/2508.02988v1).

PAIRED-style regret requires a separately trained antagonist on matched tasks. Initialize both robot learners from the retained baseline, keep actor information and rollout counts matched, and report signed regret including negative and both-fail cases. A frozen reference policy supplies rehearsal targets, not a replacement antagonist. Count antagonist learning and teacher/probe cost in addition to student transitions. [PAIRED](https://arxiv.org/html/2012.02096v2).

The released PLR sampler computes absolute unnormalized return–value residuals and flushes partial scores at optimizer boundaries. The new `replay_rollout_scores.py` implements explicit terminal versus PPO-boundary records with condition identity and policy version. It rejects a condition switch inside an episode, and retains valid zero scores. This is a scoring adapter, not an already-integrated SONIC PLR training loop. [Released sampler](https://github.com/facebookresearch/level-replay/blob/main/level_replay/level_sampler.py).

The next training comparison remains protected uniform versus PLR-value, followed by finite PAIRED/GACL controls and matched filtered/latent teacher inputs. First collect and validate an anchor buffer tied to the new endpoint; the old buffer binds the original policy. Freeze training, validation and untouched test tapes before tuning. Do not expand to multiple motions until held-out temporal-process performance and retained tracking improve across independent continuation seeds.

## Evidence status

At this note's creation, checkpoint evaluations are running. No result from PLR, PAIRED, GACL, a latent teacher, or the new timed panel is claimed yet. Completion and analysis receipts, rather than this prose, determine which stages have finished. Final measured results will be appended below.

### Additional source findings

The baseline's resolved push ranges are ±0.5 m/s in each planar coordinate before scaling; its 3× stratum therefore includes ±1.5 m/s per coordinate, as well as vertical and angular disturbances. The installed Isaac event adds these sampled increments to current root velocity despite its “setting velocity” name. Consequently the new 1.5 m/s planar-only tape is **not** an out-of-range push relative to the policy's training history. It tests a controlled disturbance process. The legacy actuation delay samples 0–8 physics ticks (0–40 ms); 12 ticks is buffer capacity, not the realized training range. The 60 ms shared burst changes both lag support and temporal/coupling process, so it does not isolate magnitude alone.

The implemented VAE pretraining does use corrupted inputs and clean reconstruction targets. Its loss is squared reconstruction error plus beta-weighted KL, rather than an unqualified standard ELBO. Documentation now states that this encourages invariance to the specified corruptions; it does not prove that contact transients are irrelevant or that latent features improve curriculum decisions.

The recurrent teacher adapter now accepts the initial hidden state used when sampling a trajectory chunk. Recomputing its training likelihood from zero hidden state would otherwise evaluate a different policy context. A regression test checks chunk-versus-full-history agreement. These CPU-tested teacher/scoring components still require native training integration and comparative robot results.

## Completed fixed-panel result

All 30 evaluation cells completed and were verified online. Nine of ten retention checks pass. The failed check is iteration 2,000 under nominal conditions: mean per-episode global MPJPE is 140.912 mm versus 127.928 mm at the origin. The 10% limit is 140.721 mm; the excess is **0.191 mm**. Nominal completion and tracking-qualified completion remain 512/512, and local error improves. This is a borderline global-tracking retention failure, not evidence of catastrophic collapse.

| Condition | Origin completion | +2,000 completion | Origin tracking-qualified | +2,000 tracking-qualified |
|---|---:|---:|---:|---:|
| Nominal | 512/512 | 512/512 | 512/512 | 512/512 |
| Full-range physics DR, zero actuator delay | 509/512 | 511/512 | 502/512 | 505/512 |
| Push scale 3× | 382/512 | 423/512 | 316/512 | 353/512 |
| Push scale 3.5× | 332/512 | 374/512 | 251/512 | 288/512 |
| Push 3.5× + friction 1.5× | 265/512 | 324/512 | 187/512 | 226/512 |

Combined-stress completion improves by 11.52 percentage points and tracking-qualified completion by 7.62 points. Observed global error increases under the stress conditions, even as more episodes complete; differing pretermination observation lengths complicate that comparison. These results support a survival/quality tradeoff worth investigating, not a uniform improvement in all tracking metrics.

The endpoint is not consistently better than iteration 1,500 under stress, so no robustness-convergence claim is warranted. A paired alias bootstrap for the final nominal margin gives an exploratory 95% interval of approximately −3.48 to +3.73 mm around the 10% limit. This motivates fresh evaluation seeds; it does not retroactively change the original deterministic gate.

- [Complete analysis and tables](/home/linjiw/lucid-sonic/experiments/latent_ued_baseline_analysis_20260911_a/results.md).
- [Fixed-panel curves](/home/linjiw/lucid-sonic/experiments/latent_ued_baseline_analysis_20260911_a/fixed_panel_curves.png).
- [Verified online analysis](https://wandb.ai/16726/lucid-sonic/runs/ued-analysis-a6593061ac8c), explicitly labeled analysis of completed experiments.

The queued endpoint anchor collection stopped without collecting or training. Its frozen plan remains available at `/home/linjiw/lucid-sonic/experiments/latent_ued_anchor_collection_20260911_a/plan.json`. A separate **frozen-policy diagnostic**, rather than curriculum admission, runs the timed panel at `/home/linjiw/lucid-sonic/experiments/latent_ued_timed_diagnostic_20260911_b`. Native/no-op equality and scored-episode event audits are still mandatory.

A further source audit found that Isaac writes joint targets during reset without advancing physics. The runtime now advances event time only when native `_sim_step_counter` advances, rejects skipped/backwards counters, and preserves nonphysics reset writes. The first queued snapshot was superseded before simulator launch. The active runtime snapshot is `/home/linjiw/lucid-ued-eval-20260911b`; source hashes are in `/home/linjiw/lucid-sonic/manifests/ued_eval_source_snapshot_20260911b.json`.

The diagnostic's capacity threshold is 7,500 MiB, recorded in its plan. This is based on the completed 512-environment evaluations consuming about 4,250 MiB above their starting memory usage; the new panel has 128 environments. Another user's training process remains untouched. GPU utilization and uncontended throughput remain unavailable.

A six-cell nominal confirmation is frozen at `/home/linjiw/lucid-sonic/experiments/latent_ued_nominal_confirmation_20260911_a/plan.json`: origin versus endpoint, 512 aliases, seeds 9012/9013/9014. It waits for the timed diagnostic to release the GPU. This estimates sensitivity to evaluation randomness for the same trained policy and does not add independent training seeds, change the original gate, or choose a more favorable checkpoint.

### Interpretation of the initial delay sweep

The isolated 20, 40 and 60 ms bursts each retain 128/128 completion in the current timed panel, while global MPJPE rises from 145.33 mm nominally to 155.56 mm at 60 ms. This is a survival ceiling for these short bursts, not evidence that latency is universally easy. It motivates dense tracking feedback and a later independently frozen duration/jitter sweep. A success-only curriculum would receive identical completion rates here; filtered or learned execution features must still beat dense tracking feedback to establish added value.

The historical `phys_100` evaluation pins actuation delay to zero. It is full-range **physics** DR, not the joint training distribution over physics and latency. The training run itself did sample 0–40 ms actuator delays. Keep that distinction in the paper and any merged tables.

### Suggested paper paragraph grounded in this baseline

Before comparing curriculum teachers, we evaluated whether extended fixed practice preserved a competent one-motion tracking policy. We continued training for 2,000 PPO iterations using a fixed disturbance mixture and reference anchoring. Under the combined push/friction condition, completion increased from 265/512 to 324/512 episodes, while tracking-qualified completion increased from 187/512 to 226/512. Nominal completion remained 512/512, but mean global tracking error increased from 127.93 to 140.91 mm, narrowly exceeding the predefined 10% retention limit. These results motivate evaluating curriculum decisions using both perturbation robustness and retained motion quality. They also show why survival alone is insufficient as either a curriculum objective or a validation metric.

The corresponding method question is: **Does temporal execution feedback improve disturbance selection beyond task competence, value residuals, and causal filtering when adapting an already competent humanoid policy?** The finite PLR and regret-teacher adapters provide controlled experimental implementations; their comparative policy-training results remain to be collected.

## Final status and next comparison

**Completed: 47 evaluation cells, 19,840 episode aliases.** These comprise the 30-cell checkpoint sweep, 11-cell timed delivery panel (including native/no-op controls), and six fresh-seed nominal comparisons. Every executed cell was logged online. The consolidated receipt is `/home/linjiw/lucid-sonic/manifests/lucid_ued_post_baseline_20260911.json`.

The fresh nominal results confirm the tracking drift across evaluation randomness:

| Evaluation seed | Origin global MPJPE (mm) | Endpoint global MPJPE (mm) | Increase |
|---|---:|---:|---:|
| 9012 | 123.10 | 139.67 | 13.47% |
| 9013 | 125.80 | 138.44 | 10.05% |
| 9014 | 122.78 | 138.00 | 12.40% |

Both policies complete all 512 episodes in each fresh-seed cell, and endpoint local error is lower. None of the three additional global-error comparisons meets the original 10% margin. These are evaluation seeds for one trained endpoint, not three independent training replications. [Detailed confirmation](/home/linjiw/lucid-sonic/experiments/latent_ued_nominal_confirmation_analysis_20260911_a/results.md), [verified online analysis](https://wandb.ai/16726/lucid-sonic/runs/ued-analysis-851ba75801f7).

All ten scored-event audits and native/no-op equality pass in the timed panel. The strongest joint condition, a 1.5 m/s planar velocity increment plus a 60 ms burst, completes 99/128 episodes (77.34%). All 128 reach the push, but only 120 reach the delay. The corresponding push-only condition completes 106/128. The combined condition's lower observed global error does not establish better tracking because failed episodes have different observation lengths. [Timed results](/home/linjiw/lucid-sonic/experiments/latent_ued_timed_analysis_20260911_a/results.md), [severity map](/home/linjiw/lucid-sonic/experiments/latent_ued_timed_analysis_20260911_a/timed_panel.png), [verified online analysis](https://wandb.ai/16726/lucid-sonic/runs/ued-analysis-3ff26ca94960).

**Decision:** do not adopt the 2,000-iteration endpoint as a newly retained starting policy. Start the forthcoming matched uniform/PLR comparison, and later filtered/latent teacher comparisons, from the same already competent original checkpoint and its validated anchor buffer. This preserves a common initialization and avoids inheriting the measured nominal drift. The completed R1 run remains a legacy fixed-practice reference; a new uniform timed-task control is still necessary because its disturbance process differs from legacy R1. No favorable intermediate checkpoint is selected from the stress results.

PLR trajectory scoring, teacher context/grounding, recurrent-state handling, and timed transport now have CPU-tested components. Native PLR/student integration and the trained student–antagonist loop remain implementation work; no PLR, PAIRED, GACL or latent-teacher robot-training result is claimed. A longer-duration/jitter delay sweep should be frozen independently because survival is saturated in the tested short-burst delay-only cells. Independent recovery measurement and causal signal-validation trajectories remain necessary before attributing any benefit to the representation.

The full SONIC CPU suite passes **1,967 tests** with five warnings. Thirteen changed workflow/core files pass Ruff and Black checks. `make run-checks` still fails pre-existing repository-wide import-format checks; unrelated files were not reformatted. Native actor/environment Python and YAML sources are identical between the baseline and timed worktrees. The timed worktree includes additional quality-telemetry reporting, so its ancillary torque/contact measurements are not silently pooled with historical telemetry.
