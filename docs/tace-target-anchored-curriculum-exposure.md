# LUCID Target-Anchored Curriculum Exposure

(Saved 2026-08-27 from user-provided design document. Written against a different
codebase layout — `src/unilab/...`, 4096 envs, `actsmooth050_policyact005` tracker — and
must be mapped onto the SONIC `research/practice-utility` branch before use; see
`~/lucid/fable.md` §8 for that mapping.)

## Minimal Design and Experiment Plan for Retained Mixed-Distribution Capability

### Working names

* **TACE:** Target-Anchored Curriculum Exposure, the schedule-agnostic exposure wrapper.
* **TA-SEQ:** TACE using the existing deterministic simple-to-hard schedule.
* **TA-LUCID:** TACE using an active online LUCID focus schedule.
* **TA-YOKED:** TACE using a prerecorded LUCID schedule without online feedback.

---

## 1. Executive decision

The next decisive experiment should **not** add a new encoder, curriculum metric, teacher network, factorized DR controller, gradient-alignment method, or off-policy replay buffer.

It should change only the distribution of environments supplied to the existing PPO learner.

The proposed training distribution is

$$
q_t(\xi)
=
\alpha p_{\mathrm{target}}(\xi)
+
(1-\alpha)p_{\mathrm{focus},t}(\xi),
$$

where:

* \(\xi\) is the complete task and domain-randomization configuration for an episode;
* \(p_{\mathrm{target}}\) is the frozen mixed-difficulty distribution used by the final evaluation and the existing Mixed PPO baseline;
* \(p_{\mathrm{focus},t}\) is the current curriculum distribution;
* \(\alpha\) is a small, fixed target-anchor ratio selected in a bounded pilot.

For the final 10% of the PPO budget, all environments train exclusively on \(p_{\mathrm{target}}\). This target-only consolidation aligns the final training objective with the final evaluation objective.

A separate **Sequential + Final Target Fine-Tune** control is required. It determines whether persistent target exposure matters or whether ordinary final mixed-distribution fine-tuning is sufficient.

The first experiment therefore answers one focused scientific question:

> Does preserving persistent support for the final target distribution eliminate backward forgetting and allow curriculum training to match or outperform mixed-difficulty PPO?

Only after this exposure hypothesis passes should active online LUCID be reintroduced.

---

## 2. Current evidence constraints

The new work must preserve the current project evidence status.

1. Use the LUCID-disabled `actsmooth050_policyact005` PPO tracker as the matched policy baseline for every new arm.

2. Do not launch another scalar-LUCID rescue, metric-v2 branch, APPO claim branch, disturbance escalation, or broad YAML search.

3. Treat scalar LUCID-Q, v21/v22, v27, and lower-only effort derating as historical diagnostics or negative controls rather than promoted methods.

4. Treat latent mismatch and guarded ability-margin quantities as mechanism diagnostics unless a separate alignment gate authorizes them as controller objectives.

5. Keep the following identical across compared arms:

   * policy architecture;
   * PPO implementation and optimizer;
   * reward function;
   * observation space;
   * termination rules;
   * low-level controller;
   * motion support and phase distribution;
   * maximum DR support;
   * total environment-step budget;
   * checkpoint-selection rule.

6. Record both intended and realized DR exposure. A curriculum claim is uninterpretable without knowing how much training time the policy actually received at each severity and perturbation combination.

7. Preserve failure-aware fixed-horizon evaluation. A method must not appear better merely because difficult episodes terminate early and stop contributing poor tracking or latent-gap measurements.

The new method is therefore an **exposure-sampler intervention**, not a redesign of LUCID's latent representation or control payload.

---

## 3. Research questions and hypotheses

### RQ1: Is the simple-to-hard failure primarily a distribution-support problem?

A sequential curriculum progressively replaces earlier experience with the current focus distribution. Mixed PPO retains broad coverage. The proposed target anchor preserves broad coverage while still concentrating most training on the curriculum frontier.

**H1:** TA-SEQ will reduce peak-to-final forgetting on previously mastered difficulty strata relative to sequential training.

### RQ2: Can curriculum preserve its optimization advantage while matching the final mixed objective?

**H2:** TA-SEQ will be noninferior to Mixed PPO on final target-distribution success and will improve target-evaluation learning-curve area, or reach comparable performance with fewer environment steps.

### RQ3: Is persistent anchoring useful, or is final mixed fine-tuning enough?

**H3:** TA-SEQ will outperform Sequential + Final Target Fine-Tune.

If these methods are equivalent, the simpler conclusion is that final target consolidation—not persistent anchoring—solves most of the distribution mismatch.

### RQ4: Does active LUCID feedback add value beyond schedule shape and exposure dose?

This question is tested only if the target-anchor hypothesis passes.

**H4:** TA-LUCID will outperform TA-YOKED under matched target-anchor ratios, schedule support, PPO budgets, and evaluation scenarios, with realized exposure dose verified within a preregistered tolerance.

---

## 4. Algorithm design

### 4.1 Freeze the target distribution

Create a versioned configuration called, conceptually, `P_TARGET_V1`.

It must be the exact mixed-difficulty sampler against which the policy is expected to perform at final evaluation or deployment.

Do not invent a new target mixture for this experiment. Reuse the existing Mixed PPO sampler so that the experiment asks a clean question.

The mathematical distribution may be shared between training and evaluation, but the following must be disjoint:

* curriculum-probe and final-test motion manifests;
* physics and randomization seeds;
* push-event seeds;
* latency and noise sequences;
* held-out OOD combinations.

Using the same distribution definition is not evaluation leakage. Reusing the same random instances would be.

### 4.2 Define the focus distribution

For the first experiment,

$$
p_{\mathrm{focus},t}
=
p_{\mathrm{ramp},t},
$$

where \(p_{\mathrm{ramp},t}\) is the exact existing deterministic simple-to-hard schedule.

Do not change its support, timing, or parameterization.

For the later active-LUCID experiment,

$$
p_{\mathrm{focus},t}
=
p_{\mathrm{LUCID},t}.
$$

The target anchor is a wrapper around the focus scheduler. It does not reinterpret or replace the focus scheduler.

### 4.3 Use fixed parallel-environment cohorts

For the first 90% of training, create a seeded random permutation of the parallel environment IDs and assign

$$
N_{\mathrm{anchor}}
=
\operatorname{round}(\alpha N),
$$

$$
N_{\mathrm{focus}}
=
N-N_{\mathrm{anchor}}.
$$

The first cohort is tagged `TARGET_ANCHOR`; the second is tagged `FOCUS`.

Keep this cohort assignment fixed for the run.

With synchronous vectorized PPO, every environment contributes one transition per simulator step. Fixed cohorts therefore make the **step-level training mixture exact** and keep the focus cohort large and stable enough for future controller updates.

For example, with 4,096 environments and \(\alpha=0.25\):

$$
N_{\mathrm{anchor}}=1024,
\qquad
N_{\mathrm{focus}}=3072.
$$

Randomize the environment permutation independently for every training seed and save it in the run manifest.

At each episode reset:

* a `TARGET_ANCHOR` environment samples its complete configuration from \(p_{\mathrm{target}}\);
* a `FOCUS` environment samples from \(p_{\mathrm{focus},t}\).

The sampled dynamics configuration remains fixed for the episode unless the channel is explicitly defined as an interval or event randomization.

Any interval randomization must preserve the environment's cohort semantics.

This is preferable to Bernoulli source selection at every reset. Reset-level selection can produce a policy-dependent step mixture because easy and hard episodes have different durations. Fixed vectorized cohorts preserve the intended compute allocation without introducing another adaptive controller.

### 4.4 Keep PPO fully on-policy

All target-anchor and focus trajectories enter the same PPO rollout buffer and PPO update.

No historical transitions are replayed.

In this design, "rehearsal" or "retention replay" means resampling older or mixed environments under the current policy—not replaying stored experience from an old policy.

This distinction is important because an ordinary trajectory-replay buffer would break the clean on-policy PPO comparison and add importance-weighting or stale-policy complications.

### 4.5 Add target-only consolidation

For normalized training progress \(u\in[0,1]\),

$$
q_u=
\begin{cases}
\alpha p_{\mathrm{target}}
+
(1-\alpha)p_{\mathrm{focus},u},
& u<0.90,\\[4pt]
p_{\mathrm{target}},
& u\ge 0.90.
\end{cases}
$$

At the consolidation boundary:

* switch every parallel-environment cohort to `TARGET_ANCHOR`;
* perform the same matched reset behavior across compared curriculum arms;
* freeze the focus scheduler;
* continue PPO with unchanged optimizer settings;
* use the final checkpoint as the primary result.

The consolidation phase prevents the final policy from remaining optimized for a curriculum-weighted objective that differs from the stated final target.

### 4.6 Separate optimization and controller cohorts

This rule is mandatory for any future TA-LUCID run.

The PPO learner uses all anchor and focus trajectories. The LUCID controller receives online training statistics only from `FOCUS` environments.

Anchor environments intentionally expose the policy to samples that may lie beyond its current frontier. Feeding their gap, return, or failure measurements into the PI update would change both:

1. the student's experience distribution; and
2. the teacher's feedback signal.

That would make the intervention difficult to interpret and could force the controller to retreat simply because the anchor did what it was designed to do.

Therefore:

* latent-gap quantiles from training rollouts use the focus cohort only;
* return-guard statistics from training rollouts use the focus cohort only;
* quality, hold, decay, or damage statistics derived from training rollouts use the focus cohort only;
* existing clean-shadow inputs retain their current semantics;
* if the focus cohort lacks the minimum reliable sample count, skip the controller update rather than adding anchor samples.

### 4.7 Initial anchor ratios

Use only

$$
\alpha\in\{0.25,0.50\}
$$

in the bounded pilot.

Start the seed-0 smoke with

$$
\alpha=0.25.
$$

This preserves 75% of the experience for curriculum-focused practice, maintains a large future controller cohort, and limits destabilizing exposure to hard target samples early in training.

Do not add a learned, forgetting-adaptive, or time-varying anchor ratio in this study.

Select one fixed value after the bounded pilot and freeze it before confirmatory runs.

---

## 5. Minimal implementation architecture

### 5.1 Code ownership

Keep the implementation in the DR scheduler and manager layer.

Recommended changes:

1. Add `src/unilab/dr/exposure_mixture.py` containing a small, schedule-agnostic exposure wrapper.

2. Integrate it in `src/unilab/dr/manager.py` at reset and interval-randomization entry points.

3. Reuse existing channel scaling and parameter sampling in `src/unilab/dr/dr_utils.py`.

4. Propagate environment IDs and fixed cohort state through the existing integration in `src/unilab/base/np_env.py`.

5. Add experiment arms through the existing PPO G1 motion-tracking configurations and LUCID campaign orchestration.

6. Add one focused analysis script, such as:

   `scripts/lucid_target_anchor_audit.py`

Do not modify:

* PPO loss construction;
* generalized advantage estimation;
* rollout storage;
* policy networks;
* reward terms;
* action projection;
* actuator behavior.

### 5.2 Suggested interface

```python
from dataclasses import dataclass
from enum import IntEnum

import numpy as np


class ExposureSource(IntEnum):
    TARGET_ANCHOR = 0
    FOCUS = 1


@dataclass
class ExposureBatch:
    source: np.ndarray
    episode_ids: np.ndarray
    intended_severity: np.ndarray
    realized_params: dict[str, np.ndarray]


class TargetAnchoredExposure:
    def source_for(self, env_ids: np.ndarray) -> np.ndarray:
        """Return the fixed source cohort for each environment."""
        ...

    def sample_for_reset(
        self,
        env_ids: np.ndarray,
        progress: float,
        focus_state: object,
        rng: np.random.Generator,
    ) -> ExposureBatch:
        """Sample full DR configurations using each environment's cohort."""
        ...
```

The wrapper should call two existing samplers:

```python
target_sampler.sample(env_ids, rng)
focus_sampler.sample(env_ids, progress, focus_state, rng)
```

It should not know PPO internals and should not calculate latent metrics.

### 5.3 Training-loop pseudocode

```python
for rollout in training:
    reset_ids = env.get_reset_env_ids()

    if reset_ids.size > 0:
        exposure = exposure_mixture.sample_for_reset(
            env_ids=reset_ids,
            progress=global_steps / total_steps,
            focus_state=focus_scheduler.state,
            rng=dr_rng,
        )

        dr_manager.apply_episode_randomization(
            env_ids=reset_ids,
            exposure=exposure,
        )

        env.store_episode_exposure(exposure)

    observations = env.observe()
    actions = policy(observations)

    next_obs, rewards, dones, info = env.step(actions)

    rollout_buffer.add(
        observations=observations,
        actions=actions,
        rewards=rewards,
        dones=dones,
        info=info,
    )

    if rollout_complete:
        # All anchor and focus rollouts are current-policy rollouts.
        ppo.update(rollout_buffer)

        if online_lucid_enabled and not consolidation_phase:
            focus_metrics = metrics.filter(source="FOCUS")

            if focus_metrics.num_valid >= min_controller_samples:
                lucid_scheduler.update(
                    focus_metrics=focus_metrics,
                    clean_shadow_metrics=current_clean_shadow_metrics,
                )
```

### 5.4 Conceptual configuration

```yaml
curriculum_exposure:
  mode: target_anchored

  anchor_ratio: 0.25

  target_sampler_ref: existing_mixed_difficulty_sampler
  focus_sampler_ref: existing_simple_to_hard_sampler

  assign_source_on: run_start
  fixed_parallel_env_cohorts: true
  sample_domain_parameters_on: episode_reset

  consolidation_fraction: 0.10

  controller_feedback_source: focus_only

  record_realized_parameters: true
  record_step_and_episode_exposure: true
```

The literal keys should follow the existing repository schema. The important part is the behavioral contract.

### 5.5 Normalization and policy inputs

The cohort tag is instrumentation only.

Do not append the tag to the policy observation. Doing so would turn this into a context-conditioned policy experiment rather than a curriculum-exposure experiment.

Keep the existing:

* observation normalization;
* return normalization;
* global PPO advantage normalization;
* minibatch construction.

Update normalization statistics using all on-policy rollouts exactly as in the reference learner.

Freeze normalization statistics during evaluation.

Log per-cohort:

* return distribution;
* advantage mean and variance;
* termination rate;
* contribution to PPO samples.

This reveals whether one cohort numerically dominates the shared update without changing PPO in the first experiment.

### 5.6 Required telemetry

Record both episode-level and environment-step-level information:

* configured anchor ratio;
* exact anchor and focus cohort sizes;
* seeded environment permutation;
* realized anchor and focus step fraction;
* realized anchor and focus episode fraction;
* source tag;
* focus-scheduler state;
* intended severity;
* realized normalized severity per channel;
* cumulative normalized DR dose;
* terminal support;
* combined-perturbation exposure;
* per-group activation frequency;
* controller update, hold, decay, veto, and saturation events;
* PPO KL, ratio, update count, and loss-guard events;
* clean performance;
* action and termination diagnostics;
* torque, clipping, and saturation diagnostics;
* frozen tracking metrics.

The intended schedule alone is not sufficient. Analysis must verify the perturbations that were actually applied.

### 5.7 Unit and integration tests

* [ ] `anchor_ratio=0` reproduces the focus-only sampler.
* [ ] `anchor_ratio=1` reproduces the mixed target sampler.
* [ ] Fixed seeds reproduce the same cohort permutation and parameter draws.
* [ ] The seeded permutation creates exactly the configured cohort sizes.
* [ ] The pre-consolidation step-level source fraction exactly matches the cohort ratio.
* [ ] No sampled parameter exceeds frozen maximum support.
* [ ] The environment cohort assignment remains fixed before consolidation.
* [ ] Episode parameters remain fixed until termination except for explicitly interval-randomized channels.
* [ ] Interval randomization obeys the environment's cohort.
* [ ] Early termination and reset do not corrupt exposure accounting.
* [ ] Realized episode and step exposure are both persisted.
* [ ] Active controller statistics exclude target-anchor environments.
* [ ] Consolidation begins at exactly the configured budget fraction.
* [ ] The focus scheduler freezes during consolidation.
* [ ] The cohort tag never enters the policy observation.
* [ ] PPO tensor shapes and update counts remain unchanged.
* [ ] Global advantage-normalization semantics remain unchanged.
* [ ] Evaluation freezes observation and return normalizers.
* [ ] Existing reset-neutral and RNG-preservation tests still pass.
* [ ] `make test-all` passes before promoted training.

---

## 6. Experiment plan

### Phase 0: No-training diagnosis

Before launching a new campaign, evaluate the best existing Mixed PPO, Sequential, and relevant historical LUCID checkpoints on one common evaluation manifest.

Produce:

1. checkpoint-by-difficulty success heatmap;
2. checkpoint-by-difficulty frozen tracking-error heatmap;
3. peak-to-final forgetting by stratum;
4. actual training exposure by severity over time;
5. final target-weighted success;
6. severity AUC;
7. worst-group success;
8. action and termination health.

This phase verifies that the observed result is genuinely caused by backward forgetting or distribution shift rather than:

* a configuration mismatch;
* a different policy baseline;
* unequal DR support;
* unequal training budget;
* unequal randomization dose;
* a checkpoint-selection artifact.

**Exit gate:** the sequential method must show a reproducible disadvantage under the frozen mixed evaluation while policy, reward, support, and budget are matched.

If it does not, stop and repair the comparison before implementing a new algorithm.

### Phase 1: Seed-0 implementation smoke

Use the reference PPO tracker and 10–15% of the normal training budget.

| Arm        | Training distribution                               | Purpose                       |
| ---------- | --------------------------------------------------- | ----------------------------- |
| Mixed PPO  | \(p_{\mathrm{target}}\) throughout                  | Generalist reference          |
| Sequential | \(p_{\mathrm{ramp},t}\) throughout                  | Reproduce the current failure |
| TA-SEQ-25  | \(0.25p_{\mathrm{target}}+0.75p_{\mathrm{ramp},t}\) | Test the minimal anchor       |

At smoke scale, the goal is mechanism and safety validation—not a performance claim.

#### Smoke gates

* source cohorts are active;
* cohort sizes are exact;
* target and focus support are correct;
* realized DR dose is persisted;
* the reference tracker reproduces expected nominal behavior;
* PPO KL and loss guards remain healthy;
* no gross clean-performance regression;
* no gross episode-length regression;
* no gross action-health or termination regression;
* interval-randomization semantics remain correct;
* the final artifact contains all required telemetry.

### Phase 2: Three-seed bounded pilot

Use three paired exploratory seeds and approximately 30–50% of the full training budget.

| Arm             | Purpose                            |
| --------------- | ---------------------------------- |
| Mixed PPO       | Final-objective reference          |
| Sequential + FT | Test final-only target fine-tuning |
| TA-SEQ-25       | Persistent 25% target support      |
| TA-SEQ-50       | Persistent 50% target support      |

All curriculum arms receive the same final 10% target-only consolidation.

For Sequential + FT, the first 90% remains purely sequential.

#### Anchor-ratio selection rule

Use only the frozen validation manifest.

1. The candidate must pass clean noninferiority.
2. It must not regress hard-stratum success.
3. Choose the ratio with higher target-weighted success.
4. If the difference is practically tied, choose the smaller ratio.
5. Freeze the selected ratio before confirmatory training.

Do not tune additional curriculum hyperparameters during this pilot.

#### Pilot promotion gate

* positive paired improvement over Sequential + FT in target success or severity AUC;
* visibly lower forgetting on previously mastered strata;
* no action-health regression;
* no termination-health regression;
* no PPO loss-stability regression;
* no support or dose-accounting failure.

If both ratios fail, stop.

Do not add adaptive replay, gradient alignment, or a more complicated teacher to rescue the experiment.

### Phase 3: Confirmatory full-budget campaign

After freezing the anchor ratio, run full-budget PPO on untouched training seeds.

Required arms:

1. Mixed PPO;
2. Sequential;
3. Sequential + Final Target Fine-Tune;
4. selected TA-SEQ.

An existing run may replace a newly trained arm only when all of the following hash-match the new experiment contract:

* policy configuration;
* initialization;
* motion manifest;
* PPO budget;
* maximum DR support;
* reward and termination definitions;
* checkpoint rule.

Otherwise, rerun the arm.

Use at least five untouched paired seeds for a paper-level claim.

When compute is constrained, the smallest decisive full-budget set is:

1. Mixed PPO;
2. Sequential + FT;
3. selected TA-SEQ.

A historical sequential result may be retained only when it is exactly matched.

### Phase 4: Active-LUCID attribution experiment

Run this phase only if TA-SEQ passes the confirmatory gate.

| Arm      | Focus schedule                    | Online feedback   |
| -------- | --------------------------------- | ----------------- |
| TA-SEQ   | Frozen expert ramp                | None              |
| TA-YOKED | Prerecorded active-LUCID schedule | None              |
| TA-LUCID | Online LUCID schedule             | Focus cohort only |

For every active TA-LUCID run:

1. record its focus schedule;
2. record its fixed cohort permutation;
3. record the intended parameter stream;
4. record applied support and normalized dose;
5. construct a yoked run that replays the focus schedule without feedback;
6. preserve the same anchor ratio and consolidation rule;
7. use paired policy initialization and evaluation manifests;
8. verify realized step-dose within a preregistered tolerance.

Policy-dependent termination can change episode counts and parameter-resampling frequency. Any remaining realized-dose difference must be reported rather than silently described as matched.

A positive LUCID-feedback claim requires TA-LUCID to beat TA-YOKED while preserving:

* clean quality;
* action health;
* termination health;
* hard-stratum performance;
* PPO stability.

If TA-LUCID and TA-YOKED are equivalent, attribute the result to schedule shape or exposure dose—not online latent feedback.

Do not launch a factorized-controller campaign in this phase.

---

## 7. Evaluation plan

### 7.1 Separate probe, validation, and test manifests

Maintain three evaluation roles:

1. **Probe:** inexpensive checkpoint diagnostics; never used for final claims.
2. **Validation:** anchor-ratio and checkpoint-rule decisions.
3. **Test:** untouched final reporting.

The final test manifest must remain unavailable to curriculum and hyperparameter decisions.

### 7.2 Primary endpoint

The primary endpoint is:

> Final-checkpoint target-distribution completion/success rate under the frozen `P_TARGET_V1` test manifest.

Use:

* deterministic policy actions;
* identical evaluation scenarios across methods;
* paired motion IDs;
* paired physics seeds;
* paired noise and latency sequences;
* paired push-event seeds.

The final checkpoint is primary.

A secondary result may select a checkpoint using a frozen validation rule and evaluate that checkpoint once on the untouched test set. It must be reported separately.

### 7.3 Difficulty-stratified capability curve

Evaluate every method on five fixed severity strata spanning the existing scalar curriculum support.

Use the project's actual severity semantics rather than inferring difficulty from return.

For checkpoint \(t\) and stratum \(b\), record

$$
S_{t,b}
=
\text{success rate at checkpoint }t
\text{ on stratum }b.
$$

Plot:

* final success versus severity;
* checkpoint × severity success heatmap;
* frozen tracking error versus severity;
* action health versus severity;
* termination health versus severity.

Define severity AUC using the trapezoidal rule over the fixed severity grid.

When \(p_{\mathrm{target}}\) is not uniform over severity, report target-weighted success separately from severity AUC.

### 7.4 Retention and forgetting

For each stratum \(b\), define

$$
F_b
=
\max_{t<T}S_{t,b}
-
S_{T,b}.
$$

Report:

* the complete checkpoint-by-stratum matrix;
* \(F_b\) for every stratum;
* target-weighted average forgetting;
* worst-stratum forgetting.

Peak measurements are noisy. Therefore compute the same statistic using:

1. raw checkpoint values; and
2. a preregistered three-checkpoint moving average.

Report both. Do not choose the smoother result after seeing which version favors the proposed method.

### 7.5 Required metrics

#### Primary independent outcome

* completion or success under `P_TARGET_V1`.

#### Core secondary outcomes

* frozen MPJPE, MPKPE, or the repository's frozen tracking errors;
* severity AUC;
* worst-group success;
* fall and termination rate;
* completion under a common horizon;
* action rate;
* action acceleration;
* high-frequency action energy;
* executed-action health;
* raw policy-action health;
* torque, clipping, saturation, and actuator-envelope violations where available;
* target-evaluation learning-curve area;
* exact DR dose and support coverage.

#### Mechanism diagnostics

* latent command–execution mismatch;
* guarded ability-margin diagnostics;
* PI update activity;
* hold, decay, veto, and saturation events.

Latent or ability metrics must never be the sole measures of policy quality.

### 7.6 OOD and compositional capability

Retain the existing fixed suites:

* clean or nominal;
* heavy OOD DR;
* unseen 60 ms latency stress;
* existing Stage C+ modes.

Add only one minimal compositional holdout initially.

Choose two perturbation factors that appear individually during training, but reserve their joint high-severity combination for final testing.

For example, the policy may see:

* high latency with nominal friction;
* low friction with nominal latency;

while the final compositional test contains:

* high latency and low friction together.

This measures whether the policy learned broadly reusable robustness rather than memorizing sampled combinations.

Do not create a large factorial OOD suite until the target-distribution result passes.

### 7.7 Failure-aware evaluation

Use a fixed horizon for every scenario.

When a policy falls or triggers a safety termination:

* count the trial as unsuccessful;
* retain the termination and failure metrics;
* apply the project's fixed-horizon padding rule to latent-gap summaries;
* do not average tracking metrics only over surviving steps without an explicit failure penalty.

### 7.8 Evaluation sizes

For intermediate probes:

* at least 32 episodes per severity stratum per training seed.

For final reporting:

* at least 128 balanced episodes per stratum per training seed;
* distribute episodes across held-out motions and paired randomization seeds;
* reweight the stratified estimates according to `P_TARGET_V1` for the primary result.

The counts may be increased if pilot uncertainty is too wide. Do not reduce them after observing results.

---

## 8. Statistical analysis and promotion criteria

### 8.1 Pairing and uncertainty

Use paired evaluation scenarios.

Report:

* every training seed individually;
* seed-level aggregate results;
* a hierarchical paired bootstrap that resamples training seeds and then evaluation scenarios within each seed.

Predeclare one primary comparison:

> Selected TA-SEQ versus Sequential + FT on final target-distribution success.

Other inferential comparisons are secondary. Correct for multiplicity when making formal significance claims across several secondary comparisons.

### 8.2 Paper-level promotion gates

A promoted method should satisfy all of the following:

1. The paired lower 95% confidence bound versus Sequential + FT is positive on the primary endpoint.

2. It is noninferior to Mixed PPO on final target success, using a predeclared two-percentage-point margin.

3. It improves worst-group success by at least five percentage points over the sequential comparator, unless the comparator is already near ceiling.

4. Clean success is noninferior within two percentage points.

5. There is no catastrophic hard-stratum regression.

6. Target-weighted forgetting is lower.

7. Action, termination, torque/saturation, and PPO-loss health do not meaningfully regress.

8. Cohort activation and exposure accounting are verified.

9. The result is confirmed on untouched seeds.

If TA-SEQ matches Mixed PPO at the final checkpoint but has a larger target-evaluation learning-curve area, the correct claim is **improved sample efficiency**, not superior final capability.

---

## 9. Interpretation map

| Result                                                   | Scientific interpretation                                                                        |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| TA-SEQ beats Sequential and matches Mixed                | Preserving target support fixes forgetting while retaining curriculum breadth.                   |
| TA-SEQ matches Sequential + FT                           | Final target consolidation is sufficient; persistent anchoring is unnecessary.                   |
| TA-SEQ beats Sequential + FT                             | Persistent target exposure matters beyond final fine-tuning.                                     |
| TA-SEQ improves early learning but matches Mixed finally | Curriculum improves sample efficiency rather than the final optimum.                             |
| TA-SEQ loses to Mixed                                    | The focus distribution biases PPO away from the target objective, or the anchor is insufficient. |
| TA-LUCID beats TA-YOKED                                  | Online feedback contributes beyond schedule shape and intended exposure.                         |
| TA-LUCID matches TA-YOKED                                | Schedule or dose explains the improvement; no online-feedback claim.                             |
| Latent gap improves while control quality worsens        | Proxy optimization failure; reject the candidate.                                                |
| All curricula lose to Mixed                              | Mixed PPO remains the strongest method; report a rigorous negative or mechanism result.          |

---

## 10. Deliberately deferred ideas

Do not include the following in the first decisive experiment:

* historical trajectory replay;
* gradient alignment;
* PCGrad-style PPO modifications;
* learned domain-weighting networks;
* forgetting-adaptive anchor ratios;
* factorized or per-channel curriculum control;
* new latent encoders;
* metric-v2 objectives;
* recurrent or history-conditioned policies;
* reward redesign;
* actuator projections;
* structural payload changes;
* hardware evaluation.

These ideas may become follow-up directions after the target-anchor hypothesis is established.

Adding them now would make a positive result difficult to attribute and a negative result difficult to diagnose.

---

## 11. Implementation and run checklist

### Before coding

* [ ] Freeze `P_TARGET_V1`.
* [ ] Freeze train, validation, probe, and test manifests.
* [ ] Record exact Mixed and Sequential configuration hashes.
* [ ] Confirm `actsmooth050_policyact005` as the shared tracker baseline.
* [ ] Version the primary endpoint and promotion gates.

### Coding

* [ ] Add the schedule-agnostic target-anchor wrapper.
* [ ] Add fixed environment-cohort state.
* [ ] Add focus-only controller masks.
* [ ] Add intended and realized exposure telemetry.
* [ ] Add consolidation-state handling.
* [ ] Add sampler and integration tests.
* [ ] Run `make test-all`.

### Smoke and pilot

* [ ] Complete the no-training checkpoint audit.
* [ ] Run the seed-0 smoke.
* [ ] Verify every sampler, PPO, and quality gate.
* [ ] Run the bounded three-seed \(\alpha\in\{0.25,0.50\}\) pilot.
* [ ] Select one ratio using only the frozen validation rule.
* [ ] Freeze the method before confirmatory training.

### Confirmation

* [ ] Run full-budget untouched paired seeds.
* [ ] Evaluate the final checkpoint on untouched target and OOD manifests.
* [ ] Produce capability curves and retention heatmaps.
* [ ] Produce intended and realized dose plots.
* [ ] Produce action and termination health tables.
* [ ] Run the preregistered paired analysis.
* [ ] Update the claim-evidence matrix before changing the paper narrative.

### Active-LUCID follow-up

* [ ] Begin only after TA-SEQ passes.
* [ ] Restrict controller feedback to the focus cohort.
* [ ] Create a schedule-matched TA-YOKED control.
* [ ] Verify realized dose within the preregistered tolerance.
* [ ] Require TA-LUCID to beat TA-YOKED before making an online-feedback claim.

---

## 12. Smallest useful first pull request

The first pull request should contain only:

1. the target-anchor exposure wrapper;
2. fixed cohort tagging;
3. exact exposure logging;
4. focus-only controller masking;
5. configurations for Mixed, Sequential, Sequential + FT, and TA-SEQ;
6. sampler and integration tests;
7. one seed-0 smoke manifest;
8. one retention and capability audit script.

This is the smallest implementation that directly tests the new hypothesis while respecting the project's existing negative evidence.

It is small enough to review, inexpensive enough to smoke-test, and scientifically strong enough to determine whether a larger campaign is justified.
