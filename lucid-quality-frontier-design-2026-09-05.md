# LUCID: quality-preserving expansion under uncertain dynamics

Version 1, 2026-09-05. Design accepted for staged implementation by the user on this date. Experimental launches remain conditional on the measurement and CPU gates below. Source analysis: [September 5 research memo](lucid-feedback-frontier-research-2026-09-05.md). Implementation checkout: `/home/linjiw/lucid-quality-frontier`, branch `research/quality-frontier`, starting at SONIC `22475f3`. The original checkout's uncommitted effort experiments are excluded.

## Research objective and scope

Improve the number and diversity of deployment-relevant conditions a humanoid can handle at a fixed training budget, while preserving tracking quality. The first method changes the training distribution and the decision instrument; it retains SONIC's actor, critic, tokens, PPO objective, rewards, termination thresholds, and motion sampler. The initial study is solved-origin continuation on one G1 hands-on-back motion. It cannot establish from-scratch barriers, unseen-motion generalization, or hardware robustness.

The observed bottleneck is a robustness–quality tradeoff: push practice improves held-out completion but worsens clean pose error. Existing survival feedback cannot detect that cost, and the historical latent gap does not reliably measure competence. The unproven hypothesis is that candidate-condition capability plus retention-quality feedback can improve the tradeoff relative to a frozen schedule. A second, conditional hypothesis is that history-derived dynamics information helps when hidden, persistent dynamics limit recovery.

Prospective contributions, contingent on evidence:

1. A measurement formulation separating candidate competence, tracking retention, and practice response, with explicit per-episode denominators.
2. A monotone support-expansion method whose quality veto and decision costs are compared against two frozen controls.
3. A staged evaluation of transfer across motion families, dynamics processes, and simulators, followed by separately scoped hardware evidence.

## Formal objective

Context `x=(motion family, motion phase, physical parameters, temporal process, simulator)`. Let `Q_track` be completion and passage of both episode-mean global and root-relative pose thresholds. Later `Q_physical` adds separately validated slip/contact/actuation requirements. The initial instrument reports **tracking-qualified success**, not physical safety or full quality-qualified success.

Optimize `J = sum_x w(x) P(Q_track=1 | policy,x)` over fixed evaluation weights. Report completion and each error metric alongside it; retain all failed episodes in the denominator. A support cell is certified only under an explicit success threshold and uncertainty rule. Never infer a continuous feasible volume from a few DR multipliers.

Distinguish current capability, finite-budget trainability, available information/representation, and physical task feasibility. Staging can change finite-budget access without increasing the physical limit. The effort-0.30 completion witness does not prove clean-quality feasibility and its direct learning closes its barrier claim in the tested scope.

## Method stages and feedback interfaces

**M0: measurement and matched controls.** Implement an absolute vector replay and a fixed allocation covering the per-stratum componentwise maximum of development seed 8600's `box_fast_300_ng` trace. Compare with the one-way box gate, capped at the source's realized per-channel frontier and probe maxima. This establishes the quality and exposure baseline before changing the decision law. The gate at this stage remains survival-only. Quality is an outcome and retention criterion, not yet an online input.

**M1: quality veto.** Once the M0 instrument is validated, add a population observer recording per-episode pose and recovery summaries with environment, motion, phase, parameter-version, and cohort identity. On fixed decision windows, allow expansion only when candidate competence clears the threshold and retained-condition quality meets frozen non-inferiority margins. A failed quality check holds support and prevents expansion; it does not lower the accepted frontier. Empty or non-finite evidence fails closed. Compare survival-only and survival-plus-quality gates under identical final grading.

The retained cohort is measured at its own fixed conditions. A low-intensity historical tail is not a clean cohort; clean quality is always evaluated separately. Before M1, choose either an explicit clean diagnostic cohort, identically budgeted in all arms, or isolated periodic frozen-policy clean probes. Prefer isolated probes for the first implementation because they avoid labeling mixed-intensity training metrics as clean quality. Their simulator and wall costs count.

**M2: recovery-conditioned information.** Add phase/contact-conditioned error, recovery time after push, persistent root deviation, and joint/body response summaries. Log applied disturbances and timestamps. Report non-recovery explicitly; do not average recovery time only over recoveries. A future dynamics observer predicts motion response from past sensor/action history; simulation parameters may supervise it but are absent at deployment. It must improve held-out prediction/calibration over raw-error and simple-history controls before influencing a scheduler.

**M3: policy adaptation, conditional.** If evidence implicates hidden dynamics, compare existing and history-conditioned policies under both fixed DR and curriculum. A privileged-context policy is a diagnostic witness, not a deployment comparator. This stage changes the architecture contract and uses separate configs, claims, and receipts. No utility estimator or residual allocator is implemented without the pre-existing identifiability and proxy-insufficiency gates.

## Curriculum state and exposure

### What enters the feedback, and why

Keep a structured observation rather than collapse every signal into one latent distance:

| Signal block | Initial measurement | Decision it can support | Required check |
| --- | --- | --- | --- |
| Competence | Completion and tracking-qualified completion at a named candidate condition | Accept or hold that candidate | Fixed denominator, sufficient evidence, declared uncertainty rule |
| Retention | Clean and retained-condition global/local tracking errors | Veto expansion when useful skills degrade | Same probe conditions, accounting for probe cost |
| Recovery | Disturbance-aligned error trajectory, time to a sustained recovery band, non-recovery fraction | Distinguish a transient challenge from persistent loss of control | Phase/contact conditioning and explicit censoring of non-recovery |
| Dynamics information | History of proprioception, commands, actions, and response residuals | Identify hidden-response ambiguity before changing the policy | Held-out prediction and calibration against simple-history baselines |
| Coverage and uncertainty | Sample counts, confidence width, process identity, distance from calibrated conditions | Request evidence or flag an untested region | No uncertainty-to-difficulty equivalence and no automatic promotion |

A future observer uses `z_t = f(o_{t-H:t}, a_{t-H:t-1}, reference_{t-H:t})`. Its output should predict control-relevant response, such as short-horizon joint/root motion and recovery probability. It need not reconstruct every randomized parameter: friction and actuation effects may be unidentifiable from one motion. Use simulation labels only as optional auxiliary supervision. A history latent is deployment-usable only if every input is available with the same timing on the robot.

Separate stochastic variation from ignorance. Repeated outcomes at a fixed condition estimate variability; predictor disagreement and held-out calibration diagnose uncertainty about response. Neither is evidence that a condition is learnable. Compare candidate histories with phase/contact-matched histories so a change of motion phase cannot masquerade as a dynamics change.

### Quality-veto state machine planned for M1

At a prespecified decision time, freeze a policy snapshot and obtain candidate and retention probes. Admit a candidate only if its competence lower confidence bound exceeds a frozen threshold and upper confidence bounds on retention loss stay within their margins. If evidence is pending or insufficient, remain in `hold`. If competence fails, retain the accepted frontier and rotate the candidate according to the frozen order. If retention fails, hold expansion and complete a prespecified consolidation block at the existing support before re-probing. Repeated vetoes trigger the finite-budget stop rule; they do not silently increase training time.

The first implementation will use scheduled isolated probes and a fixed candidate order. Every comparator pays the same probe cost, and probe transitions do not enter PPO. Freeze the competence threshold, probe size, check count, confidence procedure, consolidation duration, and total cost cap in a separate M1 protocol using E0 development data. These parameters are deliberately not inferred retrospectively from confirmation outcomes.

### Testing a hard-to-learn parameter

For each suspected difficult channel, compare direct practice at a fixed target against staged practice ending at that same target, from paired origins and with equal total environment steps. Add an easier neighboring target and a stronger-information policy only as separate diagnostic arms. A successful staged arm supports a finite-budget curriculum benefit; success from privileged or history information implicates observability or representation; failure of all tested learners leaves feasibility unresolved. An optimizer failure is not a physical impossibility certificate.

Start with one-channel ladders, then push–friction and latency–actuation interactions. Freeze directions and bounds in physical units as well as multipliers. Randomization over temporal persistence deserves its own axis: fixed delays, correlated delay changes, and rare bursts are different tasks even with equal marginal histograms. Spend a bounded, explicitly counted candidate budget near the measured frontier while maintaining coverage of accepted conditions. A failure-only sampler can concentrate on unrecoverable extremes; the candidate floor and fixed budget make that behavior observable and bounded without introducing an unvalidated utility selector.

The accepted frontier is a vector. Candidate exploration is a separate fixed-budget cohort. Candidate samples are training interventions, so exposure includes those samples even before the condition is accepted. The frozen candidate order initially removes channel selection as a confound. Probability floors retain earlier conditions; frontier contraction is never an ordinary controller action.

The historical M0 schedule has eight strata with 1,024 environments: `[43,43,43,43,42,42,640,128]`. Its six channels include latency. Despite its name, its terminal accepted push frontier is 1.625, not 3.0. The fixed control covers every per-stratum marginal range that the replay dispatches; the gate cannot exceed those bounds. The fixed top stratum can combine marginal extremes that the rotating replay did not jointly present, so joint-support shape and realized density remain explicit differences. Report actual vectors and counts, not a headline scalar. A temporal process is part of a cell's identity; episode-static versus bursty delay cannot share an identity merely because they have equal marginal ranges.

Source row k is a dispatch installed after PPO iteration k. Target rollout k+1 receives that row. The initial source warm-up dispatch is explicitly reconstructed by the canonicalizer. Replaying row k before target rollout k would shift the intervention; tests compare both pre-rollout and post-update sequences. The 39 historical probe rotations where decision and dispatched vectors differ are preserved.

A schedule-state restart stores canonical schedule hash, allocation mode, cursor, target step, and every stratum's environment IDs. It rejects altered membership, skips/repeats, modified schedules, and exhausted schedules. This is not seamless simulator resume. Causal training comparisons use symmetric fresh restarts from the same origin checkpoint.

September 5 implementation audit: these fresh restarts restore policy/value weights and reset optimizer/scheduler history. Saved reward, observation, action, and termination settings match the origin; runtime DR is changed by the experiment callbacks. The [continuation audit](lucid-continuation-contract-audit-2026-09-05.md) records the actual loader behavior. If the fixed-initial-distribution diagnostic still loses quality, isolate restart and retention mechanisms before assigning the loss to frontier expansion.

## Tracking measurement contract

The new evaluator is opt-in and retains legacy scalar keys unchanged. Before `env.step`, it reads reference/executed world-space body positions. Global MPJPE is mean Euclidean body error in mm. Local MPJPE subtracts each pose's root position before differencing. Body zero must be the root in this benchmark; the launch contract records the reference body order. Accumulate only while the environment belongs to its first scored episode and within its reference horizon. Consume `dones`, including time-outs, before the upstream evaluator mutates that tensor. Once ended, an environment cannot contribute reset-state poses.

Upstream completion remains the outcome definition; the new episode records must reconcile exactly with it. Each record includes motion/panel identity, completion, valid sample count, global/local error, and tracking qualification. Zero-sample episodes never qualify. Padded final-batch environments do not enter the panel denominator. Non-finite active observations and duplicate identities are errors. Aggregate fields cannot manufacture per-episode qualification.

The old physical telemetry remains descriptive. `applied_torque * joint_vel` is not battery energy; PhysX realization and episode masking need separate validation. Ground/self-contact semantics remain unresolved. No contact or power quantity grades M0's qualification.

## Decision rules and resource contract

M0 is a development experiment. Freeze its thresholds and quality-retention rules before any new policy outcomes. Initial engineering thresholds are global 600 mm and local 50 mm for episode means. These intentionally allow disturbance recovery and are not hardware tolerances. They are screening thresholds, not a claim of good absolute imitation. Separately require clean and standard-DR success loss no greater than 2 points and legacy clean global/local pose increase no greater than 10% versus the matched frozen control. Report the new masked errors too. Before confirmation, calibrate final thresholds using development data only and freeze a fresh manifest.

M1 uses prespecified decision times, minimum episode counts, and sequential error allocation (for example a finite number K of checks with alpha/K per check), not arbitrary repeated inspection of ordinary confidence intervals. Hierarchical dependence must be respected: episodes support a within-policy capability estimate; independent origin/training seeds support a method claim. Validate sensitivity to correlation and near-threshold noise before selecting the rule.

Fixed-resource and cost-to-target claims are different estimands. Choose one primary in confirmation. Cost includes policy training, candidate probes, offline design/evaluation, failed starts, and wall time. Source schedules are development costs, not free advice. Do not force a failed adaptive arm to appear endpoint-matched by excluding it; record its failure to reach the endpoint.

## Interfaces, files, and validation

- `vector_yoke_callback.py`: finite absolute replay and fixed per-stratum support control; shared application seam in `dr_curriculum.py`.
- `qualified_pose.py`: pure tensor measurement, thresholds, episode records, summaries.
- `qualified_eval_callback.py`: optional SONIC evaluator integration; output under `eval/qualified/`.
- `scripts/practice_utility/run_quality_frontier.py`: local, serial, fail-closed pilot runner; immutable input plan and incremental receipts.
- Matching tests under `tests/practice_utility/`; generated plans, schedules, logs, checkpoints, and receipts under `/home/linjiw/lucid-sonic/`.

CPU gates: canonical replay, exact assignment, event dispatch, no-op legacy behavior, split/resume schedule parity, fail-closed exhaustion, mask/reset/padding handling, finite measurements, fixed denominator, command construction, and receipt status. GPU gates: frozen-origin evaluation reconciles completion; bounded three-arm training smoke dispatches and exports correctly; final evaluator loads each arm's own resolved config. Never score a new checkpoint with an adjacent config inherited from another arm.

## Transfer and related work

First expand motion families, then hold out process shapes/compositions, then test a second simulator and solver/timestep sensitivity, then hardware. Prioritize push–friction recovery and measured latency persistence. Hardware calibration and evaluation splits must be disjoint; no unmeasured randomization range is described as the G1's real distribution.

[DORAEMON](https://arxiv.org/abs/2311.01885) motivates the strong expansion baseline; [ALP-GMM](https://arxiv.org/abs/1910.07224) establishes learning-progress curricula. [RMA](https://arxiv.org/html/2107.04034v1) motivates control-relevant history latents, [DROPO](https://arxiv.org/abs/2201.08434) motivates offline calibration, and [PolySim](https://arxiv.org/abs/2510.01708) motivates simulator-bias checks. Their existence prevents a novelty claim based only on combining components. The empirical question is which component improves this humanoid's tracking/robustness tradeoff at its full cost.
