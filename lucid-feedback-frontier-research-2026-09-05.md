LUCID research direction: feedback for quality-preserving capability expansion

Date: 2026-09-05. Status: evidence synthesis and proposed experiments. This note does not amend frozen decisions, authorize a utility estimator, or launch training.

**Recommendation.** Make the next research question: can feedback expand the set of uncertain dynamics under which a humanoid completes its task with acceptable tracking and physical quality, more efficiently than a strong frozen curriculum? Add recovery and quality information first. Test whether observation history is the limiting factor before introducing a new dynamics latent. The current results justify productive push practice; they do not yet justify an online practice selector or a claim about the robot's fundamental learning limit.

**Evidence checked.** Read the September 5 confirmation memo alongside the August 20 handoff, design §§2–4, September 1 signal audit/research plan, September 2 handoff, September 3 hard-DR survey, and September 4 decision and effort-status notes. Later measured results supersede older live-process and barrier hypotheses. In particular, `lucid-latest-report.md` is an older September 1 ledger despite its filename; the September 5 memo is the current confirmation source.

The existing confirmation analyzer was rerun from its original evaluation and training manifests: every returned field reproduced the frozen analysis. All 117 cells' recorded scalars matched their raw metrics files; all nine training console logs matched the publication receipt's SHA-256 hashes. This checks data consistency, not physical validity of every sensor-derived metric. No simulator was run.

Local sources: [confirmation memo](lucid-practice-allocation-confirmation-2026-09-05.md), [frozen analysis](receipts/analysis/lucid_practice_allocation_confirmation_20260905.json), [preregistration](receipts/manifests/lucid_practice_allocation_confirmation_preregistration_20260904.json), [signal audit](lucid-handoff-2026-09-02.md), [next-stage decision](lucid-next-stage-decision-2026-09-04.md), and [effort result](lucid-effort-point-status-2026-09-04.md).

**What the data actually establishes.** The independent unit is a solved origin policy plus continuation-training seed. Each arm trained for 1,500 PPO iterations with 1,024 environments; 25% of environments were reallocated. The 512 evaluation replicates per cell concern one hands-on-back clip, not 512 motions. The following are three-seed means; all ± values below are sample SD across paired seed differences, including discovery seed 8600.

| Frozen cell | Null success % | Push practice % | Placebo % | Push minus Null, points |
| --- | ---: | ---: | ---: | ---: |
| Clean `phys_000` | 100.00 | 100.00 | 100.00 | 0.00 ± 0.00 |
| Standard mixed DR `phys_100` | 99.41 | 99.28 | 99.48 | −0.13 ± 0.23 |
| Mixed DR 2× | 79.56 | 84.51 | 85.22 | +4.95 ± 5.87 |
| Push 2× | 91.80 | 93.23 | 93.23 | +1.43 ± 2.46 |
| Push 3× | 75.78 | 82.36 | 76.56 | +6.58 ± 2.64 |
| Push 3.5× | 62.11 | 74.22 | 65.62 | +12.11 ± 3.81 |
| Push 3.5× + Friction 1.5× | 55.92 | 66.08 | 57.10 | +10.16 ± 3.53 |

The untouched confirmation seeds pass D1: their Push 3× gains are +3.91 and +6.64 points, mean +5.27. This is a pass of the declared practical rule, not a population-significance result. D2 is a different endpoint: Push minus Placebo over the unweighted 13-cell macro. Its new-seed mean is +3.08, below +5; its all-three-seed mean is +2.03 ± 2.29. D2 remains unpassed.

Exploratorily, Push minus Placebo is +5.79 points on Push 3×, +8.59 on Push 3.5×, and +8.98 on the held-out composition. These local advantages coexist with a −0.72-point difference on mixed DR 2× and −1.76 on Mass 3×. This suggests specialization and cross-condition tradeoffs. It does not permit replacing the original macro endpoint after seeing the results. Deployment weights should be justified and frozen for a future study, with cell-level outcomes retained.

The larger difference at 3.5× is consistent with improved robustness near a steeper part of the response curve. Three tested push levels do not identify a continuous frontier shift or explain its mechanism. Friction alone is near ceiling, and composition gains cannot establish that friction adaptation itself improved. The training time-out means, approximately 0.966/0.898/0.952 for Null/Push/Placebo, are distribution-dependent diagnostics.

**The newly emphasized limitation is clean quality.** The original memo's “nominal” retention endpoint is `phys_100`, which is the standard mixed-DR envelope. `phys_000` is the clean cell. Both deserve separate reporting.

| Push minus Null | Clean `phys_000` | Standard mixed DR `phys_100` |
| --- | ---: | ---: |
| Global MPJPE, successful episodes, mm | +26.37 ± 21.91 | +31.17 ± 22.04 |
| Local MPJPE, successful episodes, mm | +3.73 ± 1.11 | +4.05 ± 0.98 |
| Local leg MPJPE, successful episodes, mm | +5.55 ± 0.07 | +6.22 ± 0.51 |
| Mechanical-power proxy | +11.13 ± 1.70 | +10.76 ± 1.73 |
| Torque-saturation fraction, percentage points | +0.87 ± 0.58 | +0.82 ± 0.56 |

All arms complete all clean replicates, so the clean pose comparison does not have the survivor-population change present at harder cells. Leg-local error rises on every seed, which supports examining lower-body recovery/tracking tradeoffs; it does not establish a particular recovery strategy. The power signal uses `abs(applied_torque * joint_vel)` summed over joints, averaged over the batch and steps. It is neither battery energy nor a validated measurement of realized motor output. The current quality telemetry needs episode masking and torque-source validation before use as a physical harm gate. Ground versus self-contact must be resolved before the undesired-contact proxy can grade a decision.

**Define the boundary we intend to improve.** Let a context include motion and phase, dynamics parameters, their temporal process, and simulator/model identity. Write `x = (motion, phase, parameters, process, model)`. Define `Q(episode)` as completion AND frozen tracking-quality criteria AND validated physical-quality criteria. A future objective is

`J_Q(policy) = sum_x w_deploy(x) * P(Q = 1 | policy, x)`.

The weights remain independent of the adaptive training distribution. Also report per-family outcomes and a prespecified lower-tail measure, so easy cells cannot conceal hard failures. A quality-qualified frontier at threshold `p*` is the set of tested contexts with sufficiently supported `P(Q=1) >= p*`. Do not report raw volume in arbitrary DR coordinates; coordinate scaling and unmeasured deployment probabilities would make it misleading.

Four different limits require different responses:

| Limit | Discriminating evidence | Appropriate response |
| --- | --- | --- |
| Current competence | This frozen policy fails a context | More training may help; no barrier claim |
| Trainability at budget B | Direct training versus staged training, identical task/observations and total budget | Curriculum may improve access or speed |
| Available information / policy representation | Controlled comparison with additional history or diagnostic privileged context | Better inference or representation may be needed |
| Task feasibility with acceptable quality | A successful quality-qualified witness establishes achievability in scope; a validated physical contradiction can rule out particular requirements | Reconsider task constraints or hardware |

Failure of several policies is not proof of physical infeasibility. Point effort 0.40 and 0.30 already learned directly in the tested setup, so they cannot be cited as established curriculum barriers. Their completion witnesses also do not certify clean-quality feasibility. A curriculum can improve finite-budget learning without changing physical limits or the representational capacity of a fixed policy class.

**Feedback should be a small vector with separate decision roles.** Avoid folding every diagnostic into an uncalibrated weighted score.

| Signal | What to record | Role and limitation |
| --- | --- | --- |
| Candidate competence | Population completion and normalized progress at a fixed proposed condition, with uncertainty and sample count | Controls expansion; current-distribution reward does not |
| Quality and retention | Clean and retained-condition pose error, slip, action smoothness, validated saturation/contact; paired changes and tails | Constrains expansion; completion alone misses measured costs |
| Recovery | Post-disturbance error trajectory, recovery time, persistent deviation, phase/contact regime, failure type | Distinguishes brief useful recovery from sustained tracking loss; unrecovered trials remain failures or censored observations |
| Physical response | Stance-conditioned foot motion, velocity response to action, per-joint effort demand and margin | Diagnoses mechanisms; energy and saturation are not universal competence scores |
| Dynamics uncertainty | Action-conditioned prediction error, calibrated model disagreement, confidence in history-derived dynamics features | Directs limited diagnostic probes only after calibration; prediction surprise is not practice utility |
| Practice response | Paired change after a fixed practice dose at a named horizon, plus quality-cost vector | Required evidence for future allocation utility; short noisy slopes do not substitute |

The existing latent p90 is inadmissible as a standalone scheduling signal: fixed-difficulty telemetry did not show reliable competence anchoring, and the original observer sampled one environment. Foot slip responds to difficulty but also improves when difficulty is removed. Use both as diagnostics under a fixed candidate panel; neither rehabilitates the old bidirectional scalar controller.

For recovery, use perturbation-relative time windows and reference phase. Keep global/root deviation separate from articulation error: temporarily moving the body to recover may be useful, while never recovering the path remains a task cost. Align action and sensor timestamps, especially under delay. Aggregate by environment and episode before estimating uncertainty; adjacent steps are not independent trials.

**What a useful latent could contain.** The most promising candidate is a compact representation of control-relevant dynamics inferred from recent proprioception, commands, and actions. It would encode how the robot responds, including delay/persistence, available control authority, and contact response. Its supervisory targets could be short-horizon joint/base-velocity response and contact changes. Separate this from the motion-reconstruction latent and from quality metrics.

Use only deployment-available history at inference. In simulation, known DR parameters can supervise or diagnose the representation, but they must not leak to the deployed policy or future observations. A dynamics latent need not recover a uniquely identifiable friction coefficient or mass; several parameter settings can produce indistinguishable responses. Report uncertainty over those ambiguities instead of forcing a confident label.

Before connecting a new latent to a controller: compare raw errors, phase/contact-conditioned raw errors, history-based predictors, and a small learned representation on held-out motions, policy stages, seeds, and DR processes. Require incremental calibration or predictive value for future recovery/quality failures. Offline prediction earns an instrumentation claim; only a controlled training experiment can establish curriculum value. Population sampling, time-shuffle controls, constant-input controls, and held-out process shifts should expose leakage and spurious shortcuts.

This proposal is informed by [RMA](https://arxiv.org/html/2107.04034v1), which estimates control-relevant extrinsics from state/action history for quadruped adaptation. RMA supports the mechanism as a research precedent, not its effectiveness for SONIC humanoid tracking. Adding the latent to the policy would change the architecture contract and belongs in a separate future study. Start with a diagnostic observer; keep the current actor, critic, PPO, and reward fixed for the curriculum comparison.

**Uncertain DR must include the process, not only the range.** Distinguish parameter uncertainty, time variation within an episode, simulator mismatch, and uncertainty in our learned measurements. They need different experiments.

Prioritize the following candidates:

1. Push and push–friction compositions, stratified by motion phase, direction, and recovery opportunity. This is the measured productive axis. Log actual disturbance timing and velocity change; a range multiplier is not itself a physical impulse measurement.
2. Deployment-calibrated command/observation latency with persistence and bursts. Equal marginal delay distributions can require different behavior when correlation time changes. A shared command delay and independent per-joint delays are different plants.
3. Contact uncertainty on coherent surfaces or transitions, with the material writer and solver checked. Pair friction with recovery demands rather than relying only on a marginal sweep. Contact changes require their own evaluator contract.
4. Correlated actuator effects only where model or hardware evidence supports them. Point-effort cases are useful adaptation and quality controls, not a revived barrier claim. Avoid introducing a thermal narrative through an unvalidated short-episode integrator.

Do not assume progressively faster parameter changes are always realistic or learnable. When unobserved dynamics change faster than history can identify them, the useful intervention may be a robust policy or improved sensing rather than another curriculum stage. Random mass changes every step can teach responses to an implausible process.

For sim-to-real, first obtain or locate synchronized command/state timestamps, joint position/velocity, available torque estimates, and contact-relevant traces from the intended G1 setup. Use a calibration split to define plausible distributions and a disjoint final evaluation split. [DROPO](https://arxiv.org/abs/2201.08434) provides a precedent for estimating DR distributions from offline real trajectories. Until such data exist, call chosen ranges simulation stress priors, not measured deployment uncertainty.

**A curriculum that can explore without losing competence.** Preserve a fixed retention cohort and an accepted support set; reserve a small, fixed-budget cohort for candidate practice. New candidate support is separate from accepted support. A failed candidate is held for diagnosis rather than silently changing the evaluation distribution. Maintain exposure floors on previously accepted conditions and monitor quality, not just the maximum historical range.

The loop is: train under the current mixture; evaluate or summarize the designated candidate on an isolated fixed panel; check competence and retention/quality limits; either accept the next small expansion or hold; log actual per-environment dispatch and realized transitions. Use a frozen round-robin candidate order initially. This tests timing without smuggling in an unvalidated utility selector.

Candidate practice must actually produce training data at a controlled dose. If the probe is evaluation-only and the candidate is never practiced, requiring high success can permanently block entry into a useful but initially unsuccessful region. Conversely, probe practice is an intervention and its samples must count in every resource comparison. Prespecify capped decision windows, minimum evidence, hysteresis, and a repeated-look error rule; repeatedly checking ordinary confidence intervals until one passes overstates certainty.

Keep support expansion and density allocation conceptually separate. The first asks whether a condition is ready for larger exposure. The second asks whether practicing it is better than spending the same transitions elsewhere. The current D1 and D2 decisions demonstrate why these questions cannot share a label.

At a stalled candidate, record hypotheses rather than a single “unlearnable” label: insufficient dose, poor recovery-state coverage, hidden dynamics, quality conflict, numerical/model mismatch, or physical limits. Distinguish diagnostic exploration of environment parameters from action/state exploration inside the policy. A future simulator-only recovery-initialization curriculum would change state visitation and requires a separate matched control and evaluation from ordinary initial states.

**Smallest decisive experiment sequence.**

1. **Complete measurement and the existing comparison contract.** Audit episode masks, clean versus standard-DR labels, torque-source semantics, and contact semantics. Freeze clean local/global tracking and nominal-completion margins from development evidence and task requirements before new outcomes. Do not retrofit quality-qualified success from aggregate means. Complete the runtime vector-yoke integration already specified by the September 5 memo; its CPU builder exists, but runtime integration and quality thresholds remain pending. Run required CPU tests before simulator work.
2. **Finish the planned three-arm comparison.** Static hard-practice reallocation; a frozen asymmetric preset/yoked schedule from development seed 8600; and a one-way candidate probe gate. Match origins/restarts, optimizer steps, environment counts, practice density, candidate endpoints, retention structure, and evaluation panels. Replay actual stratum dispatch vectors, including the known probe-rotation distinction. Report when an arm fails to reach its candidate endpoint; do not post-select only arms that got there. The development yoke tests whether feedback adapts across origins; it does not magically equalize every new arm's realized exposure.
3. **Grade benefit and cost prospectively.** Choose either a primary quality-qualified held-out gain at fixed total resources or a primary reduction in cost to a fixed quality-qualified endpoint. A second endpoint is secondary unless multiplicity is specified. Count training, online probes, development search, final evaluation, wall time, and failed simulator starts. Use paired origin-level differences and uncertainty, not episode-level pseudoreplication. Three origins can screen repeatability; size stronger confirmation from the paired variance and prespecified effect, with fresh confirmation seeds when earlier seeds informed tuning.
4. **If timing earns value, test the new feedback increment.** Compare completion-only and completion-plus-recovery/quality feedback with identical schedules available, probe budgets, and final grading criteria. Then test whether adding a dynamics observer improves decisions enough to pay for its cost. Freeze intermediate comparisons; do not combine several new components into the first positive result.
5. **If hidden dynamics appear limiting, isolate adaptation.** In a separate architecture study, use a factorial comparison: existing versus history-conditioned policy, each under fixed DR and curriculum. An additional privileged-context diagnostic can provide a positive witness that information helps, but its failure would not prove an information limit. A history benefit under both samplers supports adaptation; an incremental curriculum benefit is needed for the curriculum claim.
6. **Expand transfer evidence.** Add free-arm locomotion, turning/lateral motion, and a distinct whole-body task, with motion-family splits. Evaluate unseen process shapes and compositions. Use a calibrated second simulator and solver/timestep sensitivity tests to assess model dependence, then physical closed-loop tests under a separate protocol. Sim-to-sim improvement is an intermediate result; hardware completion and quality establish the hardware claim.

**Positioning and stop rules.** Success-gated distribution expansion already has strong precedent in [DORAEMON](https://arxiv.org/abs/2311.01885); learning-progress scheduling is established by [ALP-GMM](https://arxiv.org/abs/1910.07224). [PolySim](https://arxiv.org/abs/2510.01708) specifically studies simulator diversity for humanoid transfer. This is a focused primary-source check, not an exhaustive novelty survey. Merely adding these ideas together is not yet a contribution.

The prospective contribution is a measured distinction between capability, productive practice, and dynamics uncertainty, coupled to quality-preserving frontier expansion under a reproducible resource contract. It must outperform a competent frozen design or demonstrably reduce selection cost. If the probe ties the preset, close adaptive timing for this setting and prioritize motion diversity/transfer. If a latent only predicts failures but does not improve decisions, retain it as a diagnostic. If history improves robustness but curriculum adds nothing, report adaptation as the effective component. If gains disappear under solver refinement or cross-simulator evaluation, investigate model exploitation before claiming physical robustness.

The utility estimator and residual allocator remain gated by the existing identifiability and proxy-insufficiency requirements. Current exploratory push-specific advantages do not override the frozen D2 result.

**Reproducible analysis artifacts.** Generated data remain outside Git:

- [Reanalysis receipt](/home/linjiw/lucid-sonic/analysis/feedback_frontier_20260905/reanalysis.json), including original-source hashes, all cell contrasts, and clean-quality summaries.
- [Cell-level CSV](/home/linjiw/lucid-sonic/analysis/feedback_frontier_20260905/success_by_cell.csv).
- [Figure PNG](/home/linjiw/lucid-sonic/analysis/feedback_frontier_20260905/robustness_quality.png) and [PDF](/home/linjiw/lucid-sonic/analysis/feedback_frontier_20260905/robustness_quality.pdf).
- [Reproduction script](/home/linjiw/lucid-sonic/analysis/feedback_frontier_20260905/reproduce.py).

Reproduce with `/home/linjiw/isaaclab-install/env_isaaclab/bin/python /home/linjiw/lucid-sonic/analysis/feedback_frontier_20260905/reproduce.py`. This reanalyzes existing files and generates local plots; it does not train a policy or publish to W&B.
