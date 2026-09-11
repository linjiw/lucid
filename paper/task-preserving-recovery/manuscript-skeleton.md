# LUCID task-preserving recovery research prospectus

**Methods-paper prospectus — September 10, 2026. All proposed-method results are unmeasured. Not a submission manuscript.**

September 11 gate: recovery is **NOT DEMONSTRATED**. Reserve the intended methods-paper title until real recordings demonstrate recovery. The deadline diagnostic remains separately maintained in `paper/when-training-gets-easier.md`.

## Abstract — provisional, with explicit result slots

A humanoid can withstand a disturbance yet fail to resume its commanded task. Post-training for disturbance handling can also degrade a tracker’s original motion quality. We study adaptation to a fixed, time-indexed whole-body trajectory under dynamics variation and imperfect localization, with explicit budgets on original tracking degradation. The proposed LUCID procedure combines common task-relative feedback with current-policy protected-rollout costs during post-training. A bounded correction over a frozen tracker is one implementation; the scientific question is whether budget-aware updates improve the recovery–retention tradeoff beyond equally tuned feedback, adapters and anchoring. Recovery requires maintaining or regaining frozen task-error bands for a specified dwell within a fixed horizon, without changing the reference; failures and interventions remain in the denominator. [UNMEASURED: independent origins, motion-recording split and evaluated sensing source.] [UNMEASURED: primary recovery effect and uncertainty at valid retention budgets, including strongest baseline.] [UNMEASURED: sim2sim or hardware result, if supported.] These experiments will determine whether explicit rollout budgets provide a useful post-training capability or whether simpler protected adaptation suffices.

Do not convert the final two sentences to a favorable conclusion before measuring them. A negative outcome warrants a different abstract and possibly the diagnostic title.

## 1. Introduction — draft opening and argument

A humanoid that remains upright after a disturbance has not necessarily recovered its task. For a robot following a prescribed route while executing a whole-body motion, continuing the movement at a displaced location can miss the intended stopping point or interaction geometry. The relevant outcome is sustained return to the commanded trajectory, together with the ability to perform the original motion accurately when undisturbed.

Adaptation can make those objectives compete. In our separate diagnostic continuation study, nominal completion remained at 100% while unanchored global tracking error increased by 76.56% and 60.58% on two continuation seeds from one origin and one short walking motion. Cached origin-action anchoring limited the corresponding increases to 4.33% and 6.46%. These findings motivate preservation during adaptation; they do not establish multi-motion recovery or a new constrained learner.

Existing work already supplies much of the necessary machinery. Global feedback, smooth reference correction, history-informed adapters and preservation regularization are established approaches. Our proposed question is narrower: when adapting an already capable tracker, does training against measured rollout-level retention budgets yield more sustained recovery at acceptable original-task degradation than tuning those simpler mechanisms? The evaluation keeps the task trajectory unchanged and distinguishes imperfect measured feedback from privileged simulator state.

[UNMEASURED contribution paragraph: report only the observed frontier benefit or budget-attainment result, its independent-origin scope and its sensing/transfer limits. Do not claim novel residual learning, generic recovery or safety.]

## 2. Related work and task compatibility

Use the verified [closest-work matrix](closest-work.md) to build three short paragraphs: fixed/global tracking and command interfaces; post-training/adapters/preservation; recovery and dynamics alignment. Emphasize CLOT and Any2Track as the nearest alternatives. Explain StableMimic’s reference realignment and Stubborn’s task representation without treating their native task as a failed fixed-path benchmark. Cite PPF, ResMimic, ASAP, BeyondMimic, SONIC and YAHMP for their actual mechanisms. Include standard policy-gradient/PPO/constrained optimization references without inheriting guarantees.

## 3. Task-preserving recovery

State the fixed world/reference transform, monotonic clock, initialization, motion duration and actor/critic information. Define root/path, height, heading, articulation, tilt and effort separately. Describe the actual localization source and timestamp/validity handling; if only synthetic corruption exists, narrow the claim accordingly.

Use the implemented `task-restoration-v2` endpoint: maintained tracking stays in every band throughout the event and horizon; durable return requires an entry after the event with at least the specified dwell and every remaining sample in band through the endpoint. Temporary return followed by terminal relapse fails the primary endpoint. A later durable return can succeed, with the earlier relapse still reported. Keep physical failures, interventions and observed pre-event failures in F; retain unresolved instrumentation in U and report N = S + F + U separately for disturbed trials and zero controls. Accounting bounds are not confidence intervals. The capped, failure-padded cost is a reporting convention, not observed post-failure motion or an implemented learning objective. Task-specific bands, dwell, horizon and retention budgets remain unfrozen pending development recording validation.

## 4. Post-training method

Describe the common feedback interface before the correction architecture. Derive the recovery objective, protected rollout costs, Lagrangian, minimizing PPO surrogate and multiplier update from [the algorithm specification](formulation-and-algorithm.md). Specify constant anchoring, current-policy protected trajectories, cost scaling, cohort weights and total computation. Show that a post-hoc checkpoint selection rule is distinct from the implemented update.

Include algorithm pseudocode and a clear statement: the bounded mean correction and empirical retention checks provide no hard safety or retention guarantee. State which policy distribution is optimized and which deterministic policy is deployed.

## 5. Experiments

Begin with protocol/instrument verification and competent multi-motion origins. Then report Z/O/E fixed-DR feedback ablation, preservation/architecture baselines, the recovery–retention frontier, independent-origin confirmation and held-out sensing/dynamics faults. Report failures and additional cost. Include sim2sim and hardware only at their completed scope. The newer three-motion DR screen is a separate motivation cohort; it is not a treatment arm or replication of this method.

## 6. Discussion and limitations

Discuss the strongest competing explanation, where the simpler baseline works, sensitivity to budgets and reference feasibility, origin/pretraining overlap, localization dependence, confidence limitations and actuator mismatch. Separate empirical budget attainment from any mathematical guarantee. An inability to produce a feasible improved policy is a result; do not omit that origin or return only successful checkpoints.

## 7. Conclusion — conditional template

[UNMEASURED: specify whether rollout-budget post-training improved recovery at matched retention and resources.] [UNMEASURED: state conditions, independent-origin coverage and sensing/transfer scope.] If a tuned fixed anchor or outer loop matches the method, conclude that the tested task does not require the extra optimizer and retain the supported measurement lesson.

## Figure plan

| Figure | Message and content | Evidence required / falsifying visual |
|---|---|---|
| 1. One task, three outcomes | Same reference route and articulation; maintained, displaced-but-upright, regained. Overlay immutable path and disturbance timing | Actual paired trial footage with synchronized bands. Clearly mark any schematic as conceptual; no fabricated robot result. |
| 2. Algorithm and information boundary | Base tracker + correction, actor-visible estimator packets, training-only cost critics/teacher, fixed evaluator reference | Implemented data flow; show privileged channels absent from actor. If direct pose/outer loop suffices, simplify diagram. |
| 3. Recovery–retention frontier — primary | Per-origin method points with budget boundary, uncertainty, original policy and equal tuning/compute | Confirmed held-out data. Overlapping/dominated frontier falsifies superiority. Do not plot invented example curves. |
| 4. Event-aligned task traces | Root, heading, articulation, effort, sensor age/validity, disturbance and contiguous dwell; include representative failure selected by a frozen rule | Full trajectories, not MPJPE reconstruction or hand-picked successful videos. |
| 5. Generalization and transfer | Per-origin effects and worst-condition sensing/dynamics matrix; sim2sim/hardware panels only if completed | Disjoint recordings and verified conditions. Show failed/inconclusive strata explicitly. |

## Table plan and unmeasured result template

| Table | Contents |
|---|---|
| 1. Task and provenance | Origins, original recording splits, sensing implementation, reference alignment, control/physics rates, event process, bands, budgets, horizons and failures |
| 2. Main frontier point | P_MR, capped dwell time, component errors, nominal/envelope protected changes, completion/failure, effort, worst-family violation and cost |
| 3. Mechanism ablations | Z/O/E; feedback × anchor; residual versus two-column/full fine-tuning; fixed penalties versus duals; closest adapters/pre-shift |
| 4. Resource and system contract | Transitions by cohort, independent origins, tuning/validation trials, anchor/teacher/world-model forwards, GPU time, deployment latency and actuator mismatch |

| Method | Origins | P_MR | Δpath / heading / articulation | Worst retention violation | Capped dwell time | Extra compute |
|---|---|---|---|---|---|---|
| Origin | UNMEASURED | UNMEASURED | Reference after calibration | UNMEASURED | UNMEASURED | Base pretraining |
| Feedback fine-tuning | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED |
| Tuned fixed anchoring | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED |
| Closest adapter/pre-shift mechanisms | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED |
| Supported outer loop | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED |
| Proposed rollout-budget procedure | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED |

Avoid squeezing all optional figures into a fixed page count. Prioritize task contract, frontier and discriminating ablation; external project pages cannot carry essential scientific warrant. Final author verification, source checking, disclosure and current venue rules remain required before submission.
