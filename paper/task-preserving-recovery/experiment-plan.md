# Staged experiments and decision criteria

**Prospective plan; no launch authorization, frozen numeric tolerances or experiment results are implied.** The initial task is upright disturbance rejection/return to a fixed path, not unrestricted fall recovery. Failure boundaries must remain compatible with the robot and simulator contract. Extend to post-fall recovery only as a separate protocol.

## Stage 0 — Resolve the measurement and origin contract

Read-only work first: pin one source tree with an exact dirty-source archive if necessary; inventory candidate origins and motion recording lineage. The historical one-motion origin fails broader-motion qualification in the reported screen. The released tracker passes broad development criteria but must be tested against stricter task-specific competence. Do not treat the path-input pilot, DR-from-scratch arms, or R1 as interchangeable shared origins.

Required manifest fields before any simulator launch:

| Contract | Freeze explicitly |
|---|---|
| Robot/control | Model/URDF hash, joint order, PD targets/scales, gains, effort/velocity limits, armature, control/physics rates, action-delay process/capacity |
| Reference | Original recording IDs, mirrored/segment family IDs, splits, transform, reference clock, frame interpolation, start window and remaining duration |
| Task | Path, height, heading, articulation and tilt bands; dwell and horizon; nominal competence; failure/intervention definitions; absorbing-cost caps |
| Observation | Actor/critic term list, normalization, history initialization, localization source/filter, packet capture/arrival times, validity and fallback |
| Perturbation | Scheduled trial IDs, onset/duration, type/units/frame/body, channel combination, parameter draws and application verification |
| Optimization | Fixed cohort fractions/motion mix, constant anchor and teacher buffer, trainable parameters, seed hierarchy, endpoint/checkpoint rule and full compute budget |
| Logging | Native online W&B or approved immutable-campaign monitor; entity `16726`, project `lucid-sonic`, dated group; explicit arm/origin/continuation seed/iteration/condition; verified URL and source/plan/checkpoint/metric hashes |

**CPU gate:** same-input mean and stochastic-distribution parity; encoder and normalization parity; zero/no-op migration; gradients into added weights; saved/reloaded state identity; joint/reference coordinate invariance. Joint translation/yaw of robot+reference leaves relative errors unchanged; robot-only displacement changes the feedback. Mirror transforms obey joint/heading conventions. Packet reordering, stale ages, invalid flags and reference clock mismatches fail closed.

**Live gate, later and explicitly authorized:** shadow both policies on identical observations, independently of cross-process trajectory agreement. Log actual pre/post-write root velocities or applied forces and synchronized timestamps; distinguish a write argument from post-write readback and post-physics state. Check actuator lag in realized buffers, not just configuration. Record resets and reference resamples. No event starts too late for D+H; no recoverable band crossing terminates the scored trajectory. Zero-amplitude controls are excluded from disturbance claims but retained as controls.

**Decision:** instrument failure blocks interpretation. A failed broad-origin competence test redirects to selecting/calibrating a capable base, not building the constrained learner. An adequately tuned nominal origin/actuator configuration may eliminate much of the apparent problem.

## Stage 1 — Matched information test under fixed DR

One common backbone/input architecture, equal trainable parameter scope, fixed motion exposure, constant anchor β, equal episode/horizon budget and optimization settings. The primary Z/O/E arms differ only in added feedback source; each starts with zero contribution. Z receives neutral values and no information about actual error, O receives oracle error, E receives a causal implemented estimate from declared measurement packets. Validity/age treatment must not accidentally reveal the condition to only one arm. Add N (synthetically corrupted oracle) as a separate sensor-model diagnostic.

The same constant anchoring protects every arm, including Z. Use identical disturbed/protected cohorts and disable uncontrolled adaptive motion sampling. Evaluate the common unadapted origin too. A negative result from an output-only path adapter need not rule out all feedback-based control; test a supported ordinary fine-tuning comparator before rejecting the physical hypothesis.

Plot per-motion root/heading/articulation traces, event timing and band dwell, along with all-trial maintained-or-regained success and capped time. Classify data only after application and clock checks. Record seed-specific behavior, including nominal degradation. The pilot informs feasibility and variance, not a superiority claim.

**Decisions and falsifiers:**

- O fails to improve over Z under reliable instrumentation: investigate reward, reference feasibility, control authority, action scaling or optimization. Do not build a curriculum or dual learner to disguise an information failure.
- O helps, E does not: focus on sensing alignment, delay/fault tolerance or task scope. N helping is insufficient for an E pass.
- E helps but violates protection: evidence of a tradeoff; proceed to preservation comparisons only if a competent, useful feasible regime exists.
- E improves recovery with tolerable retention: advance to Stage 2; freeze this interface for all method baselines.
- A supported path outer loop matches E at lower cost: prioritize the outer loop; a learned correction is unnecessary for this setting.

## Stage 2 — Isolate preservation and constrain actual rollouts

First run feedback × constant-anchor/no-anchor comparisons. Then, only after Stage 1, compare the proposed cost-constrained learner with:

| Baseline | Matching and necessary label | What would make LUCID unnecessary |
|---|---|---|
| Ordinary feedback-enabled PPO fine-tuning | Same input, fixed DR, tuning access and protected rollout budget; if full backbone differs from residual, report capacity and a same-architecture variant | Matches recovery with retention without the extra preservation mechanism |
| Constant anchor strength sweep | Same architecture; prespecified β grid/search budget, same checkpoints and validation trials, equal total optimization exposure | Reaches the same recovery–retention frontier or target budget reliability |
| Fixed rollout-cost penalty sweep | Same current-policy protected data and normalized costs; optimize constant penalty weights instead of duals | Shows that cost instrumentation, rather than adaptive multipliers, explains the result |
| Existing two-column path adapter | Same feedback and anchor; disclose its smaller trainable capacity | Removes need for the bounded action-residual architecture |
| Any2Track-style adapter | Include history embedding and prediction task for the full mechanism; common task feedback for fair information; disclose reimplementation and pretraining costs | Equally effective skill-preserving adaptation without LUCID’s budget update |
| CLOT-style pre-shift with feedback | Observation pre-shift only; evaluation/reward reference stays fixed; matched style prior or separate prior ablation | Smooth task correction already reaches the same frontier |
| PPF-style reliable-state anchoring | Define reliability for this tracker; do not copy ALIP assumptions onto arbitrary motion | State-weighted regularization controls the tradeoff just as well |
| ResMimic-style residual | Same robot/reference inputs for this task; no irrelevant object-state advantage | Standard residual post-training suffices |
| Supported saturated path-error outer loop | Velocity/heading or reference-conditioning API already supported; no undocumented joint-offset hack; original evaluation target unchanged | Classical feedback solves recovery without post-training |

The outer loop can be $v_{cmd}=v^*+\operatorname{sat}(K_p e^p+K_d e^v)$ and $\omega_{cmd}=\omega^*+\operatorname{sat}(k_\psi e^\psi)$ when that command interface exists. With SONIC planner conditioning, preserve the commanded upper-body component where supported, expose every change, and score the original full reference. If the interface cannot express the target motion, this is a task-compatibility limit, not evidence that the outer loop loses. A compatible reference-window correction is another possible baseline but must not mutate the evaluator reference.

Use a fixed sufficient exploration horizon as a termination baseline before Stubborn-style stochastic termination/sampling. Native StableMimic and Stubborn recovery scores are separately informative; task-adapted implementations must be retrained/evaluated under this contract and labeled as such. Full faithful reproduction is not assumed merely because a module name matches.

**Main decision:** advance only for a prespecified practically meaningful recovery gain at valid budgets, or a prespecified improvement in probability of obtaining a feasible useful policy at equal resource/tuning budgets. If only auxiliary compute or validation selection explains the gain, withdraw the algorithmic claim. If fixed penalties match duals, remove multiplier adaptation from the claimed contribution.

## Stage 3 — Independent-origin confirmation and frontier

Use several independently trained competent origins, with continuation seeds nested within each. Three is an initial costing target, not a sufficiency rule. A released checkpoint plus multiple fine-tuning seeds is still one origin. If reproducing independent base training is infeasible, narrow the claim to adaptation of a specified released model and do not advertise independent-origin robustness.

Motion splits group by original capture recording, including mirrored variants and nearby segments. Freeze adaptation, tuning, origin-calibration and confirmation sets; identify family/performer overlap. “Unseen in post-training” is distinct from “unseen in pretraining.” For released SONIC origins whose exact exposure is unknown, report that uncertainty. Select motions for task coverage and feasibility before method outcomes: straight/curved walking, turns, sideways/backward motion, stopping and upper-body coordination. Use sufficient clip duration for the full recovery window; do not stitch arbitrary poses to fabricate long motion.

Hold out combinations as well as severity: push direction/phase, pulse magnitude/duration, friction × delay, payload/CoM × sensing age, persistent localization bias × drift, dropped/reordered packets, estimator outlier and relocalization faults. Explicitly distinguish dynamics delay from sensing delay and simulator velocity increments from physical force pulses. Define a finite operational envelope; a scalar λ is not a distributional distance and clipping can change regimes.

**Confirmation metrics:**

- All-trial maintained-or-regained success, maintained/regained counts, failure/intervention/invalid counts and task completion.
- Capped time to completed dwell, fixed-horizon failure-aware error-time and relapse rate; conditional successful-run timing only as a labeled secondary statistic.
- Continuous path, height, heading, articulation, joint velocity and body errors, with per-motion distributions and time traces.
- Original-unit protected cost changes per family/condition; maximum normalized budget violation; absolute competence; nominal and original-envelope failure probability.
- Executed effort, saturation, action rate, measured latency and sensing age/validity distributions.
- Entire recovery–retention frontier, all predeclared budget points, individual-origin results and uncertainty.

The primary frontier x-axis may be maximum protected normalized budget usage $\max_k(C_k-C_k^0)/\epsilon_k$ (only positive ε; exact-zero budgets reported separately), with feasibility ≤1 **and** absolute competence. Y-axis is P_MR. Supply physical-unit companion plots so a normalized worst-case statistic cannot hide the source of degradation. Show infeasible points and the original policy. Distinguish a descriptive cloud of all checkpoints from the frontier selected using only development data. Never take a test-set maximum and call it a deployable selection result.

## Statistical and resource contract

Predeclare Δ_R (minimum useful recovery gain), each ε, absolute ceilings, the primary budget/condition or familywise testing procedure, and decision confidence. Estimate pilot variability to choose rollout counts and independent origins; do not choose the confirmation effect size from the best observed result.

For each origin compute paired method differences using the common frozen recording/condition design. Continuation seeds are nested replicates. Report every origin and average origins equally for the primary origin-generalization estimand. Recording IDs are another shared clustering axis across origins: use crossed/hierarchical resampling consistent with that design, or a prespecified mixed-effects analysis, rather than treating 69,120 episodes as independent policy replicates. Very few origins yield unstable intervals; show raw effects and state the limit.

Use all-trial binary and capped continuous outcomes, so failures are not assumed to be noninformatively censored. Pair rollouts only when exogenous draws are keyed by recording/trial/event and actual application is verified; a common seed with policy-dependent resets does not establish pairing. Confidence for simultaneous retention across costs/conditions requires simultaneous bounds or a declared multiplicity correction. Absence of a significant gain is inconclusive unless a meaningful equivalence region is resolved.

A possible confirmation rule is lower confidence bound for the primary origin-averaged ΔP_MR above Δ_R, with simultaneous upper confidence bounds on all protected degradation costs below their budgets and absolute competence satisfied. Exact confidence procedure and units must be preregistered. If precision is insufficient, report inconclusive; do not repeatedly add seeds until it passes without a sequential design.

Match per-arm disturbed and protected training exposure, total simulator transitions, validation frequency/access, parameter-search trials and origin/anchor collection access. Report GPU wall time, simulator time, actor/teacher/world-model forwards, anchor presentations, optimizer steps, peak memory, deployment latency and human tuning. If dual training gets fresh protected batches, give competing methods the same total training budget and either the same data access or disclose an operational cost comparison. Report both transition-matched and total-compute-matched comparisons if extra learner compute is consequential. A method that requires more tuning or validation has not demonstrated a cheaper post-training procedure.

## Stage 4 — Sim2sim, then a bounded hardware claim

Freeze selected policies before transfer evaluation. Align joint mapping, normalization, history initialization, reference start/clock, PD gains, torque/velocity limits, armature and delay semantics. Same-input ONNX/native parity precedes end-to-end simulator comparisons. Historical MuJoCo uses different hip torque limits; fix or explicitly factor that mismatch before attributing a rank change to the recovery algorithm. Give both engines a common event/measurement schema; report residual model discrepancies and per-engine outcomes without pooling.

Hardware begins only after a separate approved protocol, built/tested runner, functioning localization and independent measurement, timing/parity checks and appropriate physical stop/fall-arrest arrangements. Start with one path-and-stop task and bounded characterized disturbances. Record force/time/contact geometry or a calibrated equivalent, every intervention, full horizon and thermal/torque limitations. An optical-lab result is a valid instrumented deployment, not onboard infrastructure-free autonomy.

If matching actuator dynamics erases the method’s advantage, prioritize calibration or alignment. If localization error erases it, narrow the sensing envelope or improve the estimator. If hardware is unavailable, the paper must state sim2sim only; no simulated trial count substitutes for sim2real efficacy.

## Immediate diagnostic revision versus longer programme

The current diagnostic can be revised without a new simulator run: correct arithmetic, preserve scope and identify the missing physical decomposition. Proposed frozen-policy replay and crossed early/late policy × narrow/wide distribution tests are separately authorized future evaluations. They must not delay or be invented to rescue a deadline.

The official [ICRA 2027 call](https://2027.ieee-icra.org/contribute/call-for-icra-2027-papers-now-accepting-submissions/) was checked September 10; treat the current call/portal as authority for deadlines and formatting. No submission schedule licenses assuming these new studies will succeed. Keep the diagnostic title and evidence freeze unless completed evidence actually supports the methods title. No paper was submitted or public page changed during this development pass.
