# Task formulation and proposed algorithm

**Status: specified, unimplemented and unmeasured.** No value below is a newly calibrated robot tolerance. Numeric bands, horizons, budgets, weights, corruption parameters and resource limits must be frozen in an approved campaign before confirmation. The initial feedback study uses constant anchoring; the constrained learner is gated on that study.

## 1. Task and information contract

A trial has an immutable reference recording and a time-indexed trajectory

$$r(t)=(p^*(t),R^*(t),q^*(t),\dot q^*(t)),\qquad t\in[0,T].$$

The world frame W is gravity aligned. A single yaw/translation transform maps the prerecorded reference frame F into W at trial initialization. Save that transform, recording hash, resampling convention, initial frame, and clock origin. The reference advances with elapsed monotonic task time, at the frozen control cadence; do not pause it after a push, search for a closer phase, restart the clip, recenter its translation, or change its yaw after scoring starts. Logged reference queries must resolve to the same frame/timestamp regardless of policy. Task phase may be randomized **before** a trial according to a common frozen schedule, with enough remaining recording for its full horizon. No loops or terminal pose holds may be silently introduced to create time.

Choose a path-and-stop whole-body motion that admits a physically plausible pre-disturbance window and return horizon. Require nominal competence per motion and protected condition, including articulation and effort. Retaining an incompetent origin is not success. An unreachable time-indexed command after a sufficiently large disturbance is a legitimate failure, not a reason to move the evaluation target. Report the severity boundary of feasibility. Geometric path following or bounded retiming is a separately named task if later studied.

| Quantity | Actor during training and deployment | Critic / measurement |
|---|---|---|
| Base tracker observation | Existing exact proprioceptive history: joint positions/velocities, IMU angular velocity/projected gravity, previous actions; immutable reference lookahead through the existing encoder | Same plus permitted privileged simulator state |
| Added feedback | Estimated reference-relative planar displacement and heading, age, validity; uncertainty estimate only if the estimator actually outputs one | Oracle state may supervise or measure, never silently replace actor data |
| Disturbance schedule, actual parameters | Not exposed unless a separately declared comparator gives it to every method | Logged for application verification and event-aligned metrics |
| Origin actions / buffer | Training-only targets on cached observations; constant coefficient in first study | No deployment teacher call |
| Clock and reference | Prerecorded trajectory and monotonic synchronized playback, available in principle on hardware | Independent reference copy for scoring |
| Ground truth | Never fed into estimated arm | Simulation truth or independent hardware measurement with its own uncertainty |

**Localization source:** use a timestamped external root-pose stream as the first concrete deployment contract, e.g. a calibrated optical tracking rigid body plus the robot IMU. This is a proposed instrumented-lab setting, not an installed or verified estimator. Source availability, calibration, root-to-marker transform, packet timing and independent evaluation ground truth are open prerequisites. The existing path-input code uses simulator truth and supplies no estimator.

Let a packet have capture time s, arrival time a and valid flag v. At controller time t, use only packets with a≤t. A causal estimator predicts pose to t; log the latest contributing measurement time s and age t−s. Do not compare a delayed position with a current reference without declaring that choice. A simpler direct-delay baseline instead forms both reference and measured error at s and supplies age; its controller must handle staleness. Zero-order hold, constant-velocity prediction and a small filter are reasonable candidates; use the simplest that meets the sensor contract. A filter driven by synthetic packets is an implemented **simulation estimator**, not evidence of physical localization.

Estimated feedback in the planar heading frame is

$$\hat e^p_t=R_z(\hat\psi_{t|t})^\top[p^*_{xy}(t)-\hat p_{xy,t|t}],\qquad
\hat e^\psi_t=\operatorname{wrap}(\psi^*(t)-\hat\psi_{t|t}).$$

Represent heading by sine/cosine if needed to avoid a discontinuity. Supply validity and age explicitly; missing is not zero error. Freeze a fallback (for the first residual implementation, smoothly suppress the correction when feedback is invalid, using a specified ramp) and count its outcomes. “No correction” is not a safe-controller guarantee. True localization covariance cannot be inferred by labeling a scalar confidence head uncertainty.

The required comparison is Z/O/E: zero-feedback, oracle-feedback and implemented estimated-feedback. An N arm with directly corrupted oracle error is a **sensor-model stress test**, not E. If E is unavailable, run only engineering checks and name the missing estimator; do not declare the realistic-feedback gate passed.

## 2. Separate task errors and effort

All evaluation errors use the immutable reference and independent measurement at the same timestamp:

$$e_p(t)=\|p_{xy}(t)-p^*_{xy}(t)\|_2,\quad
 e_z(t)=|p_z(t)-p_z^*(t)|,\quad
 e_\psi(t)=|\operatorname{wrap}(\psi(t)-\psi^*(t))|.$$

Define isolated articulation through joint-space configuration, not global-minus-local MPJPE:

$$e_q(t)=\sqrt{\frac{1}{J}\sum_j d_j(q_j(t),q^*_j(t))^2}.$$

For the G1's bounded joints, d is direct joint-angle difference in radians; wrap only genuinely periodic joints. Report joint-velocity RMSE separately. Root tilt error (gravity direction or roll/pitch) remains a separate posture quantity and cannot be hidden by joint agreement. Primary bands include e_p, e_z, e_psi, e_q and tilt; an abbreviated three-band diagram must not silently drop the others.

For continuity with historical work, also report global body MPJPE and own-root-subtracted local MPJPE with exact body lists and masks. An additional yaw-aligned local body metric may isolate body arrangement from heading, but must be labeled differently. Root displacement is computed from root positions, never by subtracting norms. Heading becomes ill-defined near a vertical projected heading axis; restrict the initial upright-recovery task accordingly and mark invalid geometry, rather than fabricate a yaw through a singularity.

Report measured/simulated executed torque, positive mechanical work $\sum_j\int\max(\tau_j\dot q_j,0)dt$, absolute mechanical power, target rate and torque-saturation occupancy. These are separate from completion and tracking. Requested torque is not executed torque; simulated mechanical energy is not battery consumption. A bounded action correction does not bound contact forces or ensure thermal safety.

## 3. Event schedule, recovery and primary denominator

Freeze N trial IDs with origin, motion recording, initialization, condition, disturbance onset d and end e, plus post-event horizon H and dwell D≤H. Disturbance time is scheduled externally, not triggered only when a particular policy looks ready. A physical failure before d remains in N and has outcome zero. Identify actual disturbance application: velocity increment has units m/s; a force pulse records world/body frame, body, application point, force, start/end and integrated impulse. Keep transport delay distinct from independently sampled actuator-group lags.

Let $b_i>0$ be frozen task-error bands and

$$I(t)=\mathbb1[\forall i\in\{p,z,\psi,q,\mathrm{tilt}\}:e_i(t)\le b_i].$$

On a fixed sample grid, continuous dwell means every scheduled sample in a contiguous D-duration interval passes; missing ground-truth samples cannot satisfy dwell. Use integer control ticks to avoid floating-point/off-by-one ambiguity; include both endpoints, so D seconds at step Δ requires D/Δ+1 consecutive samples when D/Δ is integral. The continuous claim is only at the recorded sampling resolution unless higher-rate evidence is available.

Define the first admissible entry time

$$\tau=\inf\{u\in[e,e+H-D]: I(t)=1\ \text{for all sampled }t\in[u,u+D]\}.$$

Let F mark any physical failure, reset, human intervention or reference alteration from trial start through e+H. A pre-event competence failure is also a primary trial failure; do not condition N on the policy having a good state at d. Then

$$Y=\mathbb1[\tau<\infty\ \land\ F=0\ \land\text{pre-event task criterion passes}],
\qquad P_{\mathrm{MR}}=N^{-1}\sum_nY_n.$$

Successful rejection means the pre-event criterion passes and all samples from d through e+H remain in band without failure; label it **maintained**. Other Y=1 trials are **regained**. Both count toward P_MR. An episode already inside at e can have τ=e, including a departure/return during the pulse. Never compare only the policy-dependent subset that departed. Report departures and maintained/regained counts descriptively.

A later band relapse after the successful dwell is recorded in a separate relapse rate and the fixed-horizon error-time outcome; a later physical failure/intervention invalidates Y. This definition tests a D-duration return, not permanent invariance. If a task needs “stay until end,” freeze that stricter success criterion as a separate primary protocol before seeing results.

Define failure-aware time to completed dwell: T_D=(τ−e)+D on success and H otherwise. Maintained trials have T_D=D, the minimum certifiable dwell time. Report return-start time separately if useful, with a cap H on failures. Do not treat falls/interventions as benign right-censoring or compute primary recovery time only among successes.

Disturbance writer failure with no policy failure is an instrument error, not successful rejection. Keep the scheduled ID in the intention-to-test denominator as no demonstrated success, report invalid trials, and stop confirmation for repair under a declared rerun rule. A policy failing before its scheduled push is a policy failure, not an instrument error. Zero-amplitude controls are labeled controls, not successful disturbance trials. Repeated pushes are a later separately scheduled protocol; no second disturbance enters the initial isolated-event horizon.

## 4. Finite-horizon recovery objective and protected costs

Use undiscounted episodic costs (γ=1) to match fixed-horizon evaluation. Let $\ell_i(t)=\min(e_i(t)/b_i,M_i)$, with finite prespecified cap M_i≥1. Define absorbing failure: from the first physical failure onward, set each tracking cost to M_i through the scheduled horizon. Preserve actual pre-failure measurements and report uncapped live errors separately. Missing measurement data is not evidence of low cost; invalidate the instrument record and apply the declared conservative reporting treatment.

For a disturbance trajectory, let K index a fixed scored window containing the pulse and H post-event seconds. Set $w_i\ge0,\sum_iw_i=1$, and

$$L_D(\zeta)=\frac{1}{K}\sum_{t\in\mathcal W}\sum_iw_i\ell_i(t)
       +\kappa(1-Y),\qquad J_D(\phi)=\mathbb E_{\mathcal D_D,\pi_\phi}[L_D].$$

This is an explicit failure-aware error objective plus a maintained-or-regained terminal cost; it is not exactly maximizing success alone. Freeze κ and weights and report the success/error tradeoff. Use absorbing costs for pre-disturbance failures too. Dense costs provide learning signal before any complete recovery; the terminal term aligns learning with the sustained criterion. The dwell counter, event schedule and remaining horizon are included in the privileged critic state, making the event-dependent cost Markov in that augmented state. They are not secretly exposed to the actor.

For each protected condition c (nominal/original envelope crossed with named motion families), define current-policy rollout costs

$$C_{ic}(\phi)=\mathbb E_{\mathcal D_c,\pi_\phi}\left[K_c^{-1}\sum_t\ell_i(t)\right],
\qquad C_{Fc}(\phi)=\Pr(\text{noncompletion or intervention}\mid c).$$

Use a separately frozen protected normalization $s_i$ in place of recovery b_i if budgets are specified in physical units; record the conversion once. Protected caps/failure padding are the same for origin and adapted policies. Include effort as a named protected cost if required; do not hide it in an unreported reward weight. A stopped robot must not appear efficient merely because power logging ended: accompany measured energy with failure probability and an explicitly conservative absorbing task cost; fabricated post-failure joules are not physical energy.

Measure $C^0_{ic}$ from the frozen origin on independent calibration rollouts. Specify absolute nonnegative degradation allowance ε_ic in the same units and an absolute competence ceiling U_ic:

$$B_{ic}=\min(C^0_{ic}+\epsilon_{ic},U_{ic}).$$

A relative allowance may be translated to ε=δC0 only when C0 is positive and well estimated; absolute budgets handle zero/near-zero baselines. For failure probability use $B_{Fc}=\min(C^0_{Fc}+\epsilon_{Fc},1-S_{\min,c})$. Origin feasibility and its uncertainty must be established first. A frozen point estimate B is an empirical training target, not a guarantee about the true origin expectation.

The proposed optimization is

$$\min_\phi\ J_D(\phi)+\beta A(\phi)
\quad\text{subject to}\quad C_k(\phi)\le B_k\quad\forall k=(i,c),$$

where $A=\mathbb E_{o\sim\mathcal B_0}\|[\mu_\phi(o)-\mu_0(o)]/s_a\|_2^2$ and β is constant; the fixed per-action scale $s_a$ preserves the historical anchor normalization. The cached anchor is an auxiliary penalty, not the constraint. Keep the same β in initial comparisons; sweep β with equal tuning budgets in the strong baseline. Constraint rollouts come from the **current policy**, not cached teacher states. Each family is represented explicitly to prevent a pooled average from hiding skill loss.

## 5. Economical policy and consistent optimization

Candidate mean policy:

$$\mu_\phi(o)=\mu_0(h,r)+B_a\tanh f_\phi(h,r,\hat e,\mathrm{age},v),$$

with diagonal per-joint correction scale B_a fixed from the deployment contract and a zero final output layer. Freeze base weights, encoder, normalizer and action std after canonicalizing any native std clamp. The initial observation-to-mean function and, with shared random variates, initial stochastic actions must match the origin. Zero all final outputs, not every layer, so gradients can reach the output layer. Parameter count and bound are tuned equally for residual baselines. The existing two-column decoder extension is a simpler alternative.

For PPO training, use $a\sim\mathcal N(\mu_\phi,\Sigma_0)$ with fixed nonzero Σ0 initially; log the sampled action and correct log probability. B_a bounds the **mean correction**, not Gaussian samples or actuator torques. If action clipping follows sampling, the sampler/likelihood pair and executed action must be recorded consistently; never score a clipped action under the unclipped density as if it were the sample. Deterministic deployment uses μ. Statistical optimization of the stochastic training policy does not guarantee deterministic deployment constraints: evaluate both and gate the deployed mean policy separately. A future bounded squashed distribution requires its change-of-variables density and a new parity contract.

For positive cost violation, the Lagrangian is

$$\mathcal L(\phi,\nu)=J_D(\phi)+\beta A(\phi)
+\sum_k\nu_k(C_k(\phi)-B_k),\qquad\nu_k\ge0.$$

Minimize in φ, maximize in ν. For a cost signal c_t with full finite-horizon cost-to-go G_t and an action-independent baseline V_t,

$$\nabla_\phi C(\phi)=\mathbb E_{\pi_\phi}\left[\sum_t\nabla_\phi\log\pi_\phi(a_t\mid o_t)(G_t-V_t)\right].$$

Causal likelihood-ratio gradients apply even though simulator states and completion indicators are not differentiable. Do not backpropagate through saved trajectory errors as though this were a differentiable simulator. Normalize c_t by the episode horizon once when defining the return; do not divide again by an arbitrarily variable number of surviving steps. Episode batches average over episodes and **sum** over their action steps. Fixed-length transition sampling needs the corresponding horizon scaling. Complete-episode Monte Carlo advantages give the reference estimator; truncated rollout/GAE approximations must preserve terminal versus truncation bootstrap semantics and be validated separately.

At each outer iteration sample fresh trajectories from fixed cohorts D_D and every D_c under π_old. Retain separate cost-value heads. Let ρ_t=π_φ(a_t|o_t)/π_old(a_t|o_t) and $\bar\rho=\mathrm{clip}(\rho,1-\delta,1+\delta)$. A consistent **cost-minimizing** clipped surrogate is

$$U_c(\phi)=\widehat{\mathbb E}_{\tau\mid c}\sum_t
\max\{\rho_t\hat A^c_t,\bar\rho_t\hat A^c_t\}.$$

Update the actor by minimizing $U_D+\sum_k\nu_kU_k+\beta A$ for a frozen small number of epochs, with a recorded KL stop rule. The max is the sign-reversed analogue of reward PPO's min; swapping signs inconsistently would reward cost increases. Per-cohort conditional means implement the displayed objective. If using one mixture batch with sampling probability q_c, multiply each cohort contribution by 1/q_c; otherwise changing the number of protected environments changes the objective. Do not standardize each cost advantage independently without compensating scales and multipliers. Fixed physical normalization is preferable.

Use an independent fresh **training** cost batch from the updated π_{k+1} for dual updates:

$$\nu_j\leftarrow\max\{0,\nu_j+\eta_j[\widehat C_j(\pi_{k+1})-B_j]\}.$$

Positive violation increases pressure to reduce that cost. Gradients do not propagate through ν or the cost estimate in this update. Update each multiplier once per fresh rollout estimate, not once per reused PPO minibatch. A smoothed estimate or capped multiplier changes the algorithm and needs a declared setting; saturation is not constraint satisfaction. This fresh batch is optimization data, **not held-out validation**. Account for its simulator cost. A simpler variant reuses the current outer-iteration pre-update rollouts with a one-iteration lag; test it if fresh-cost sampling dominates the budget.

This uses standard policy-gradient/Lagrangian ideas and a PPO-style heuristic. It is not the trust-region algorithm in [Constrained Policy Optimization](https://arxiv.org/abs/1705.10528), and it inherits no CPO guarantee. [PPO](https://arxiv.org/abs/1707.06347) clipping and a KL stop do not bound unseen task degradation. No safety, reachability, monotonic improvement or universal retention theorem is claimed.

## 6. Algorithm and simplification tests

```text
Require approved frozen protocol, competent origin and passed information gate.
Freeze reference/splits/budgets; calibrate origin costs; cache anchor observations.
Initialize common feedback adapter or correction at zero; verify action parity.
For each declared post-training iteration:
    Collect full disturbed and protected current-policy episodes at fixed exposure.
    Verify event application, fixed reference, sensor causality and cohort identities.
    Form absorbing, fixed-horizon cost returns and separate cost advantages.
    Update cost critics and actor with cost-sign-correct PPO surrogate + constant anchor.
    Collect fresh protected training-cost batches; update nonnegative multipliers.
    Log original-unit costs, violations, multipliers, KL, drift and all computation.
At predeclared checkpoints:
    Evaluate deterministic deployment on development panels with frozen budgets.
    Select by the frozen feasible-checkpoint rule; no feasible candidate => return origin.
After recipe selection:
    Lock everything and evaluate once on independent confirmation panels/origins.
```

Returning the origin is a deployment-selection fallback, not evidence that the optimizer enforced constraints during learning. Report infeasible iterates, failure to produce an adapted feasible checkpoint, and time to feasible improvement.

| Component | Simpler alternative making it unnecessary | Test that rejects its necessity |
|---|---|---|
| Estimated global feedback | Zero-feedback history or supported proportional outer loop | Same recovery frontier without learned feedback use |
| State estimator/prediction | Valid timestamped direct pose with age | Equivalent recovery under measured sensing conditions |
| Bounded residual | Existing two-column input extension or ordinary fine-tuning | Same quality/recovery at equal resources |
| Constant anchor | No anchor with constrained costs | No additional feasible-frontier benefit from anchor |
| Rollout constraints/duals | Tuned fixed anchor or fixed cost-penalty sweep | Matches budget attainment and recovery with equal validation/tuning cost |
| Multiple family costs | Pooled cost with per-family reporting | Pooling meets every relevant family budget with adequate precision |
| Fresh dual batch | Lagged reuse of current rollout cost | Same stability and budget attainment at lower cost |
| Dynamics model / curriculum | Fixed DR and ordinary history | No frontier gain justifying extra teacher/model/exposure computation |
