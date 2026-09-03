# When Training Gets Easier: Training-Range Collapse in Humanoid Control

**Working draft, reframed 2026-09-02.** Every number in this draft is measured and traceable
to a receipt listed in Appendix B. Proposed work is confined to Section 9 and is labelled as
such. Project title for the ongoing work: *Expanding Training Ranges for Humanoid Control*.

## Abstract

Domain randomization exposes a robot to varied physical conditions during training. When an
adaptive curriculum is allowed to narrow those conditions, a higher training reward can
reflect easier training rather than a better policy. We study this problem in simulated
humanoid motion tracking on a Unitree G1, training on a single motion for 8,000 iterations.
Two of six runs of a curriculum that could expand or shrink its ranges ended with nearly
collapsed ranges. These runs earned the highest training returns of the twelve runs we
scored, and the lowest robustness on a physics ladder that the curriculum did not control;
across all twelve runs, terminal return and robustness are inversely ranked (Spearman
−0.73). One collapsed run scores 14.2 success-AUC points below fixed domain randomization
on the same seed. To prevent shrinkage we test a rule that allows training ranges to expand
or stay fixed but never shrink. Across three seeds it blocked all 2,033 requested reductions,
and its robustness was within a preregistered margin of fixed domain randomization (mean
difference +0.60 points, sample standard deviation 2.25), which establishes noninferiority
and not an advantage. An audit of five candidate readiness signals shows that time-out
survival tracks competence while the learned mismatch signal used by the collapsing
curriculum does not. Replaying the exported policies in MuJoCo with independently
implemented randomization preserves the ordering: beyond the training envelope, both
never-shrink and fixed policies survive 38% of physics draws where the collapsed policy
survives 16% and an unrandomized policy 3%. A prototype that tests proposed conditions
before expanding raised the training-range scale from 1.0 to 1.5 in four steps. Finally we
measure whether a curriculum could allocate practice by learning progress, as recent
multi-dimensional curricula do: from scratch the progress signal is clear, but once the
policy is competent it falls to between 0.01 and 0.08 of its own noise floor, and closing
that gap would need roughly 170 times the episodes per decision window. Whether adaptive
expansion improves robustness over a preset schedule remains open; the present results
show why better policies must be distinguished from easier training.

## 1. Introduction

A humanoid policy trained in simulation must work on a robot whose mass, friction, actuator
delay, and disturbances differ from the simulator's nominal values. Domain randomization
handles this by training on ranges of those parameters instead of single values. The width
of the ranges matters: ranges that are too wide can stall learning, and ranges that are too
narrow leave the policy brittle. Adaptive curricula try to resolve this by widening or
narrowing the ranges as the policy improves.

This paper asks one question about such curricula:

> **Is the robot getting better, or is its training getting easier?**

The two are hard to tell apart from inside training. A curriculum that measures the policy
on its own training distribution and is allowed to narrow that distribution can raise its
score by narrowing. Training return goes up, the dashboard looks healthy, and the policy has
seen less of the physics it will face at deployment. We call the end state
**training-range collapse**.

We measured this directly. In a 29-DoF humanoid motion-tracking task, an adaptive
curriculum driven by a learned mismatch signal shrank its ranges in every one of six runs and
collapsed them in two. The collapsed runs had the highest terminal training returns and the
lowest robustness on an evaluation ladder the curriculum did not control. The cost is not
cosmetic: one collapse loses 14.2 success-AUC points against fixed randomization trained on
the same seed.

The fix we test is deliberately small. A range may expand or stay where it is, but it may
not shrink. This rule blocks the mechanism of collapse without adding a new signal, a new
network, or a new hyperparameter. Across three seeds it refused every one of 2,033
requested reductions and ended within a preregistered margin of fixed domain randomization.
It does not train a better policy than fixed randomization; on our evidence it trains an
equivalent one, which is the point. Whatever an adaptive curriculum adds must be shown
against that baseline with the collapse pathway closed.

**Contributions.** All four are measured on the same testbed.

1. **A measured failure mode.** We show that an adaptive curriculum that can narrow its own
   training ranges collapses them in two of six long runs, and that terminal training
   return and held-out robustness are inversely ranked across twelve runs (Section 4).
2. **A rule that prevents it.** Training ranges that never shrink block all 2,033 requested
   reductions over three seeds and are noninferior to fixed randomization under a rule fixed
   before the data existed (Section 5).
3. **Which signals can be trusted.** An audit at fixed difficulty shows that time-out
   survival tracks competence (rank correlation +0.99 with training progress) and the
   learned mismatch signal does not (−0.04), which explains why the collapsing curriculum
   collapsed (Section 6).
4. **Robustness is per-parameter and interactive.** A 55-cell sweep shows that pushes limit
   healthy policies while mass, center-of-mass, and joint offsets can be widened to three
   times their range at little cost, and that widening all channels together costs about six
   success points more than the sum of the individual costs (Section 7).

We also replay the exported policies in a second simulator with independently implemented
randomization (Section 8). The ordering survives. Finally we describe the range-expansion
curriculum this evidence motivates, report a scalar prototype that expanded ranges in four
evidence-triggered steps, and state the test it must pass before we credit it (Section 9).

## 2. Background and Related Work

**Domain randomization** trains on a distribution of physical parameters so that the
deployed system falls inside or near the training distribution [1–4]. **Adaptive
randomization** changes that distribution during training. Automatic Domain Randomization
expands boundaries after performance at the boundary passes a threshold [5]; active and
entropy-based methods choose which domains to sample [6,7]; self-paced and teacher-based
curricula trade difficulty against learning progress [8,9]; level-replay methods emphasize
informative levels [14,15]. Several of these methods are allowed to make training easier
when the policy struggles. That freedom is the subject of this paper.

The never-shrink rule we test is close to the boundary rule in Automatic Domain
Randomization. We do not claim it as new. Our contribution is the measurement of what goes
wrong without it in long humanoid runs, the demonstration that the rule alone recovers fixed
randomization's robustness, and the audit of which signals could safely drive expansion.

**Humanoid motion tracking.** DeepMimic, adversarial motion priors, BeyondMimic, and SONIC
learn reference-conditioned whole-body control [10–13]. We use SONIC as the sole testbed. It
provides a 29-DoF Unitree G1 model, a 50 Hz policy, Isaac Lab training, and a MuJoCo model.

**Evaluation beyond reward.** Training return depends on the distribution it is measured
on. We therefore score every policy on a frozen physics ladder that the curriculum never
sees, and report success and restricted-mean progress rather than reward [17].

## 3. Setup

**Task.** A policy tracks one reference clip (`walk_hands_on_back_loop_002`, 4 s) on a
29-DoF G1 in Isaac Lab, 1,024 parallel environments, 8,000 PPO iterations, trained from
scratch. The actor sees a ten-step history of gravity direction, base angular velocity,
joint positions, joint velocities, and previous actions, plus ten future reference frames.

**Randomized parameters.** Six channels: rigid-body mass, torso center of mass, joint
default offset, ground friction, action delay, and external pushes. A scale λ multiplies
every channel's configured deviation; λ = 1 is the training envelope and λ = 0 is nominal
physics. Friction is clipped at a physical floor, which binds at λ ≥ 1.5.

**Compared training arms.**

| Arm | Training ranges |
|---|---|
| No randomization | λ = 0 throughout |
| Fixed randomization | λ = 1 throughout |
| Adaptive, may shrink | λ set by a PI controller on a learned mismatch signal, λ ∈ [0, 1] |
| Adaptive, never shrinks | same controller, but a requested decrease is refused |

Two variants of the adaptive controller and three seeds give the six adaptive runs.

**Evaluation.** Each final policy is scored on a frozen ladder of physics scales
{0, 0.5, 1, 1.25, 1.5, 2} with 512 episodes per cell. The primary outcome is the area under
the success-versus-scale curve over the beyond-envelope cells (**frontier AUC**, reported in
points, 0–100) and over the in-envelope cells. Restricted-mean progress is a secondary
outcome. The ladder is never visible to any curriculum.

## 4. The Problem: Training-Range Collapse

### 4.1 Why a curriculum that can shrink will shrink

Let the curriculum observe a score $\bar Y(\theta,\lambda)$ on its own training
distribution and move λ toward a set point $Y^*$ with an integral rule
$\dot\lambda = K(\bar Y - Y^*)$. Wider ranges lower the score,
$\partial \bar Y/\partial\lambda < 0$. When learning stalls and the score sits below the set
point, the controller lowers λ, which raises the score without any change in the policy.
If the policy adapts to hard physics more slowly than the controller moves λ, shrinking is
the fast response of the coupled system, and the gain $K$ sets the speed of collapse rather
than its direction. This is a conditional statement about one common controller form, not a
theorem about every adaptive curriculum; a deadband, saturation, or policy recovery can
interrupt it. It says where to look.

### 4.2 What we observed

Every one of the six adaptive runs applied at least one reduction. Two ended near λ = 0
after having reached the full envelope earlier in training.

**Table 1. Collapsed runs against the runs that held their ranges.**

| Outcome | Collapsed run A | Collapsed run B | Range-holding runs (min–max) |
|---|---:|---:|---:|
| Final scale λ | 0.062 | 0.012 | 1.000 |
| Mean return, last 500 iterations | **15.29** | **14.40** | 10.98–12.28 |
| Frontier success AUC (points) | 73.99 | 69.73 | 61.20–91.31 |

The collapsed runs have the two highest terminal returns among the twelve arm–seed pairs we
scored. Across the twelve, terminal return and frontier AUC have Spearman rank correlation
−0.73: the runs that look best from inside training are the ones that retreated furthest
from the deployment physics. Grouped, the collapsed runs average return 14.84 and AUC 71.9;
the range-holding runs average return 11.60 and AUC 83.3.

**Cost.** Collapsed run A was chosen for scoring before its evaluation existed. It scores
14.19 points below fixed randomization on the same seed and 17.32 points below the
never-shrink version of the same controller on the same seed.

This differs from ordinary forgetting. Forgetting means later training damages an earlier
skill. Collapse means the curriculum removes the conditions that would reveal the damage and
then grades itself on the easier replacement.

## 5. A Rule That Prevents Shrinkage

We keep the same controller and refuse every requested decrease. The range may expand or
hold; it may not shrink.

**Mechanism.** Across three seeds the rule refused 453, 951, and 629 requested reductions,
2,033 in total, and applied none. All three runs ended at the full envelope. These requests
are correlated controller events, not independent samples; their role is to show sustained
pressure toward easier training across the long runs. The sample size for any policy
comparison is three seeds.

**Robustness.** The comparison follows a rule fixed before the data: for each of four AUC
components the never-shrink arm must be within 2 points (frontier) or 1 point (in-envelope)
of fixed randomization on at least two of three paired seeds.

**Table 2. Never-shrink versus fixed randomization, frontier success AUC (points).**

| Seed | Never-shrink | Fixed | Difference |
|---:|---:|---:|---:|
| 8600 | 90.30 | 90.46 | −0.16 |
| 8601 | 91.31 | 88.18 | +3.13 |
| 8602 | 82.03 | 83.20 | −1.17 |
| **Mean** | | | **+0.60** (SD 2.25) |

All four components pass on all three seeds (frontier success +0.60, in-envelope success
+0.07, frontier progress +0.50, in-envelope progress +0.01). Two seeds favour fixed
randomization slightly. The supported claim is exact: with shrinkage removed, the adaptive
controller trains a policy equivalent to fixed randomization within the declared margins.
It does not train a better one. Retaining the ranges also does not by itself guarantee that
the policy retains its skills; that is what Table 2 measures.

**Why it ties.** Training telemetry records how many episodes each training
cohort ran and at what intensity, so realized practice can be counted rather than
assumed. The never-shrink arm spent 99.2 percent of its training exposure at the
envelope, against 100 percent for fixed randomization. In realized practice the
two arms are the same experiment, which is what the outcome says.

**Seed effect.** Between-seed offsets in frontier AUC reach 7.8 points on the same arm.
Any claimed advantage of a curriculum over fixed randomization must be paired by seed and
must clear this before it is believed.

## 6. Which Signals Can Guide Expansion

A signal that drives an expanding curriculum must move with competence when difficulty is
fixed, and must respond to difficulty in the right direction. We audited five signals on
five runs at pinned difficulty and on the two collapses.

**Table 3. Readiness-signal audit.**

| Signal | Rank correlation with training iteration at fixed λ | Direction reversals | Behaviour during the two collapses | Use |
|---|---:|---:|---|---|
| Time-out survival | +0.987 | 4.6 | rises when ranges shrink | readiness signal, but only if measured on proposed conditions |
| Mean return | +0.973 | 3.2 | rewards shrinking strongly | diagnostic only |
| Learned mismatch | −0.037 | 19.2 | −0.03 / +0.03 against λ | rejected |
| Foot slip per step | −0.531 | 17.0 | +0.75 / +0.71 against λ | corroborating measurement |
| Torque saturation | −0.312 | 7.2 | sign flips across arms | cost, not a gate |

The learned mismatch signal that drove the collapsing curriculum is neither anchored to
competence nor consistently controlled by difficulty; its direction is set by the arm rather
than the policy. That is why the controller in Section 4 had nothing to hold it at the
envelope. Survival is well anchored but is exactly the signal a shrinking controller can
inflate. It becomes usable only when measured on the proposed harder conditions rather than
the current ones, and when a failed test can hold but never shrink the ranges.

## 7. Robustness Is Per-Parameter and Interactive

We widened one channel at a time on frozen policies, holding the others at the envelope,
512 episodes per cell, one seed.

**Table 4. Success when one channel is widened beyond its training range.**

| Policy | All channels 2× | Mass 2× / 3× | Center of mass 2× / 3× | Joint offset 2× / 3× | Push 2× / 3× | First to fail |
|---|---:|---:|---:|---:|---:|---|
| Fixed | 0.820 | 0.992 / 0.949 | 0.988 / 0.988 | 0.992 / 0.990 | **0.912 / 0.746** | push |
| Never-shrink | 0.842 | 0.990 / 0.938 | 0.992 / 0.982 | 0.994 / 0.986 | **0.928 / 0.770** | push |
| Adaptive, held ranges | 0.795 | 0.980 / 0.951 | 0.986 / 0.975 | 0.994 / 0.980 | **0.910 / 0.705** | push |
| Adaptive, collapsed | 0.518 | 0.873 / 0.682 | 0.928 / 0.818 | 0.967 / 0.955 | **0.811 / 0.570** | push |
| No randomization | 0.334 | 0.795 / 0.643 | **0.654 / 0.393** | 0.900 / 0.891 | 0.736 / 0.443 | center of mass |

For the three healthy policies, pushes at twice the range cost 6–8 points while mass, center
of mass, and joint offsets cost at most 1.4 points and stay above 0.938 at three times the
range. The unrandomized policy fails first under center-of-mass shift instead. Which
parameter binds depends on the policy, so it must be measured for the policy being trained
rather than assumed from the simulator.

Widening everything together costs more than the parts. For the fixed policy the individual
2× losses sum to 0.111 while the joint 2× cell loses 0.174, about six points that no sum of
single-channel losses predicts. The joint cell widens five channels at once, so we do not
attribute the residual to any pair; a pairwise sweep is the test.

## 8. Does the Ordering Survive a Change of Simulator and Motion?

**Second simulator.** We exported the final policies to ONNX and replayed them in MuJoCo
with our own implementation of the six channels, scaled by the same λ. This is a sim-to-sim
check of the exported policy, not the hardware deployment path, and MuJoCo's randomization is
a labelled approximation of Isaac's. A run passes if the pelvis stays within 0.5 m of the
reference to the end of the clip. Seeds are shared across arms, 32 per cell.

**Table 5. MuJoCo survival of exported policies (pass rate over 32 physics draws).**

| Policy | All channels, λ 1 / 1.5 / 2 | Physics only (no pushes), λ 1 / 1.5 / 2 |
|---|---:|---:|
| No randomization | 31 / 12 / 0 % | 59 / 16 / 3 % |
| Adaptive, collapsed (seed 8601) | 56 / 19 / 9 % | 84 / 31 / 16 % |
| Never-shrink (seed 8601) | 47 / 22 / 16 % | 66 / 50 / 38 % |
| Fixed (seed 8601, paired) | 47 / 25 / 12 % | 75 / 47 / 38 % |
| Fixed (seed 8600) | 78 / 34 / 16 % | 94 / 56 / 31 % |

Pushes are the binding channel in MuJoCo as in Isaac, and absolute survival is far below the
Isaac scores because the randomization differs; the gap is reported, not tuned. The
ordering is what transfers. Beyond the training envelope without pushes, the never-shrink
and paired fixed policies tie at 38%, the collapsed policy reaches 16%, and the
unrandomized policy 3%. Between the two seeds of fixed randomization the difference is as
large as between methods, which repeats the seed effect of Section 5. Videos with every
draw marked pass or fall accompany the paper.

**Second motion.** On an untrained clip of the same family (`walk_hands_on_back_loop_003`,
128 episodes per cell), success at λ 1.5 is 0.80 for fixed, 0.73 for the range-holding
adaptive run, 0.40 for the collapsed run, and 0.18 without randomization. Rank correlation
of the arm ordering with the trained clip is 0.8 and 1.0 across the two cells. This is one
nearby clip, not motion generalization.

## 9. Where Should the Extra Training Go?

Sections 4 to 7 fix what a curriculum may do and what it may listen to. They do
not show that any curriculum improves the policy. The question that decides that
comes first, and we have not answered it:

> Can we improve humanoid control by spending more training on difficult but
> learnable physical conditions, while preserving performance on conditions
> already learned?

### 9.1 Difficult is not the same as learnable

Section 7 says pushes bind and mass, center of mass, and joint offsets are
nearly free. It does not say that practising pushes would help. A condition can
be hard because the policy lacks practice at it, because the observation cannot
support the required response, or because the reference motion is incompatible
with that disturbance. Only the first is repaired by any curriculum, and every
component of an expansion curriculum silently assumes the first. Nothing we have
measured separates them.

### 9.2 The screen that separates them

Five branches leave the same competent policy with the same architecture,
reward, motion, environment count, iteration budget, and seed. The only
difference is what a fixed quarter of the same 1,024 environments practises, and
that share is taken out of the standard mixture rather than added to it, so no
branch trains on more episodes than another.

| Branch | What the 256-environment share practises | Origin success there |
|---|---|---:|
| Plain continuation | nothing; every environment at the envelope | — |
| Matched control | the envelope, like every other environment | — |
| Manageable channels | mass, center of mass, joint offset at 3× | 0.949 / 0.988 / 0.990 |
| The bottleneck | pushes at 3× | 0.746 |
| The combination | pushes at 2× with friction at 1.5× | 0.912 and 0.973 alone |

The practised levels are read off Section 7 rather than chosen, so "difficult"
means a measured success level. Every branch is scored on one frozen thirteen
cell suite that includes ordinary conditions the policy already handles, the
practised cells, and two cells above every level any branch practises. The
starting policy is scored on the same suite, so improvement is measured against
the starting point as well as against the matched control. Each cell is labelled
in support or held out for each branch from that branch's own realized training
vectors, and a cell inside a branch's support may not carry a generalization
claim for it.

The margins and rules were frozen before any branch trained. A gain of five
points or more is meaningful; a difference under two points is a tie; a branch
that gains on its target while losing more than two points on an
already-learned cell is reported as a trade-off, not an improvement.

**Every outcome ends something.** If dedicated practice at the failing push
level does not move push, then push failure is not a practice deficit, no
allocation scheduler can repair it by exposure, and the expansion direction
loses its justification. If practising the manageable channels helps as much as
practising the bottleneck, then extra exposure helps wherever it is aimed and
choosing channels buys nothing. If practising the combination does not beat
practising the channel alone above the practised corner, the combination test is
dropped.

### 9.3 What a curriculum would have to ask, and what that costs — Measured

Our gate asks whether the policy can already handle a harder condition, and
expands when success is high. A curriculum that improves the policy has to ask a
different question: would practising this help? That is a question about
improvement, and it has to be estimated by repeatedly evaluating conditions that
do not change, because a score that rose after the test got easier is the failure
this paper is about.

We measured whether that estimate is available. Training runs record survival per
iteration for each training cohort, and each cohort sits at a fixed condition for
as long as the curriculum does not move, so the longest window in which the range
never moved gives per-condition series at genuinely fixed difficulty. Against a
null that keeps the same values and destroys their time order, we asked how wide
a window must be before the sign of the local trend can be trusted.

The answer depends entirely on whether the policy is still learning the task.
From scratch, survival at every cohort climbs about 120 points over 3,362
iterations and the sign of the local trend is reliable once the window reaches
200 to 400 iterations. Warm-started from a policy that has already solved the
envelope, which is the state any expansion curriculum operates in, the whole
1,590-iteration window moves each cohort by between −1.2 and +3.6 points, and the
local trend sits between 0.01 and 0.08 times its own noise floor at a 100
iteration window. The sign agrees with the window's own trend 42 to 68 percent of
the time, which is a coin flip. On the largest cohort, closing that gap would take
roughly 170 times the episodes per window: about 14,000 episodes per iteration, or
a window of about 17,000 iterations at present cohort sizes.

This is not an estimator defect. A competent policy's episode-end survival at a
fixed condition is flat within noise, so there is little left to detect, and one
bit per episode is too coarse to resolve it. The consequence for design is
concrete. An online allocator driven by episode-end survival or by reward
progress cannot make trustworthy per-condition decisions at this budget, so the
effect of practice has to be measured end to end against frozen evaluation cells,
as Section 9.2 does. We audited the obvious candidate for a
finer signal. Per-step foot slip yields hundreds of samples per episode instead
of one bit, and Section 6 found it the only body-grounded signal with a
consistent difficulty response. It does have the resolution: in the eight cells
where success separates the three healthy policies by at most twice its own
cell-to-cell reproducibility, slip separates them by two to three times its own.
It does not have the validity. Reading slip at an easy cell to predict success at
a harder one ranks the three healthy policies in exactly the wrong order, in all
four pairs of cells we tried, putting the least robust first every time. Low slip
is a conservative gait rather than a robust one, which is consistent with slip
improving whenever difficulty is cut. Three policies and one seed do not settle
it, but they remove the reason to build on it.

So no online per-condition progress signal is available to us at present. That is
the case for measuring the effect of practice end to end, against frozen
evaluation cells, as Section 9.2 does.

### 9.4 Stated support is not practice — Measured

There is a second reason to measure the effect of practice end to end. Widening a
uniform range lowers the density everywhere inside it, so a condition can remain
formally inside the training support while being practised much less than
before. Counting the episodes each cohort actually ran, at the intensity it ran
them, separates the two.

| Run | At the envelope | Above 1.4 | At or below the envelope |
|---|---:|---:|---:|
| Fixed randomization | 100.0% | 0.0% | 100.0% |
| Never-shrink | 99.2% | 0.0% | 100.0% |
| Probe gate that reached 1.5 | 41.5% | 13.7% | 63.1% |

The gate reports a final range of 1.5 and spent 13.7 percent of its training
exposure above 1.4. It also spent 41.5 percent at the envelope, where fixed
randomization spends 100 percent. The frontier practice was bought with envelope
practice rather than added to it, which is a direct explanation for expansion
arms tying fixed randomization rather than beating it: with the environment count
held constant, widening a range is a reallocation, and the reallocation is the
treatment. That is the design the screen in Section 9.2 makes explicit and
controls, and it is why any comparison here reports realized exposure per band
rather than the range a curriculum claims.

### 9.5 The hurdle any such curriculum must clear

Beating the narrow fixed baseline of Section 5 would establish nothing. The
comparators are fixed randomization over the wider target range, a preset
expansion schedule reaching the same final ranges, and a preset per-parameter
schedule with the same practice mixture. Preset schedules are built from
development runs and frozen before the confirmation seeds are trained; a
schedule may never be derived from the run it is compared against. Resources are
matched including any probe cost, and realized exposure is reported per branch.
The primary claim is chosen in advance: better robustness at equal cost, or a
fixed robustness target reached at lower cost.

If such a curriculum works, the components then have to be separated: choosing
which parameter to emphasize, choosing when to change the emphasis, checking
combinations, and maintaining earlier practice. Each is kept only if an
experiment could show it is unnecessary.

## 10. Limitations

All capability results come from one training motion and one primary simulator, with one
nearby untrained clip and one sim-to-sim replay. The channel sweep uses one seed; the
ordering is informative, exact gaps are not. Three seeds bound the never-shrink comparison
to a noninferiority statement, and the number of seeds a claim needs depends on
the variability and the size of the effect claimed rather than on a convention
[19]. The MuJoCo replay uses our own randomization and the ONNX
policy, not the deployment binary. The proposed curriculum has a scalar prototype only.
Nothing here has been run on hardware.

## 11. Conclusion

An adaptive curriculum should not be allowed to pass its own test by making the test
easier. In long humanoid training runs, the curriculum that could do so did: it earned the
highest training returns while losing the physics its policy would need. Refusing to shrink
training ranges removes that path and recovers the robustness of fixed randomization, no
more and no less. Survival measured on proposed conditions is the one signal in our audit
that can drive expansion safely, and robustness must be widened parameter by parameter with
combinations checked. Whether doing so beats a preset schedule is the next experiment.

## Appendix A. Vocabulary

Terms used in earlier drafts and their replacements in this one.

| Earlier | Here |
|---|---|
| Difficulty evacuation | Training-range collapse |
| Endogenous exam trap | Scores can improve because training gets easier |
| Monotone support / ratchet | Training ranges that never shrink |
| Mechanism inoculation | Preventing range shrinkage |
| Anisotropic frontiers | A separate range for each physical parameter |
| Candidate-level population probes | Testing the proposed expansion |
| Joint-corner sentinel | A test of combined parameter changes |
| Retained rehearsal tail | Continued practice on earlier conditions |
| Open-loop ramp | A preset expansion schedule |
| Safety receipt | A record of blocked range reductions |
| MAnD-Ex | The range-expansion curriculum |

## Appendix B. Evidence ledger (remove before submission)

| Section | Receipt |
|---|---|
| 4 | `receipts/analysis/lucid_return_inversion_20260901.json`, `lucid_p3_readout_20260901.json` |
| 5 | `receipts/analysis/lucid_phase0_analysis_20260901.json` (H_R2 decision), ratchet guard logs |
| 6 | `receipts/analysis/lucid_signal_audit_20260901.json`, `lucid_physical_signal_audit_20260902.json` |
| 7 | `receipts/analysis/lucid_channel_attribution_20260902.json` |
| 8 | `receipts/analysis/mujoco_sim2sim_20260902/`, `lucid_heldout_motion_20260901.json` |
| all | `receipts/analysis/lucid_draft_number_verification_20260902.json` — every number above re-checked against its receipt or the raw training trace |
| 9 | `receipts/analysis/lucid_progress_signal_audit_20260902.json` and `..._warmstart_20260902.json`; preregistration `lucid_practice_allocation_screen_preregistration_20260902.json`; training trace `artifacts/.../curriculum_comparison_ne1024_20260901_232720/seed_8600/gate_150/curriculum_*.jsonl` (the gate run itself; `lucid_gate_feasibility_20260901.json` is a replay proxy, not this run), preregistration `lucid_support_expansion_screen_preregistration_20260901.json` |

## References

[1] J. Tobin et al., "Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World," IROS, 2017.
[2] X. B. Peng et al., "Sim-to-Real Transfer of Robotic Control with Dynamics Randomization," ICRA, 2018.
[3] J. Tan et al., "Sim-to-Real: Learning Agile Locomotion for Quadruped Robots," RSS, 2018.
[4] A. Rajeswaran et al., "EPOpt: Learning Robust Neural Network Policies Using Model Ensembles," 2016.
[5] OpenAI et al., "Solving Rubik's Cube with a Robot Hand," 2019.
[6] B. Mehta et al., "Active Domain Randomization," CoRL, 2019.
[7] G. Tiboni et al., "Domain Randomization via Entropy Maximization," ICLR, 2024.
[8] P. Klink et al., "Self-Paced Contextual Reinforcement Learning," CoRL, 2020.
[9] R. Portelas et al., "Teacher Algorithms for Curriculum Learning of Deep RL in Continuously Parameterized Environments," CoRL, 2020.
[10] X. B. Peng et al., "DeepMimic," 2018.
[11] X. B. Peng et al., "AMP: Adversarial Motion Priors," 2021.
[12] Z. Luo et al., "SONIC: Supersizing Motion Tracking for Natural Humanoid Whole-Body Control," 2025.
[13] Q. Liao et al., "BeyondMimic," 2025.
[14] M. Dennis et al., "Emergent Complexity and Zero-Shot Transfer via Unsupervised Environment Design," NeurIPS, 2020.
[15] M. Jiang et al., "Prioritized Level Replay," ICML, 2021.
[17] G. Christmann et al., "Benchmarking Smoothness and Reducing High-Frequency Oscillations in Continuous Control Policies," IROS, 2024.
[18] TransCurriculum: history-informed curriculum scheduling across task dimensions, arXiv:2603.14156.
[19] R. Agarwal et al., "Deep Reinforcement Learning at the Edge of the Statistical Precipice," NeurIPS, 2021.
