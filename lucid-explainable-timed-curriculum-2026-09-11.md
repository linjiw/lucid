# Explainable timed-disturbance curricula: implementation and next tests

SONIC, one motion (`walk_hands_on_back_loop_002__A066_M`), September 11, 2026.
This is a method-development record. Implementation checks are not evidence of
improved final-policy robustness. The completed baseline results remain in
[lucid-ued-post-baseline-2026-09-11.md](lucid-ued-post-baseline-2026-09-11.md).

## What the evidence changes

The protected 2,000-iteration continuation improved combined push/friction
completion from 265/512 to 324/512, but nominal global tracking error exceeded
the predefined 10% retention margin. Three fresh evaluation seeds confirmed the
nominal drift. Short shared-delay bursts had perfect completion despite worse
tracking. Thus neither survival nor execution mismatch alone is an adequate
measure of the capability we want to preserve and expand.

The next comparison starts both arms from the original competent policy and its
validated reference-anchor buffer. It does not select a favorable intermediate
checkpoint or inherit the failed endpoint. The fixed R1 result is a historical
reference; uniform timed practice is the matched control for the new process.

## Teacher information: keep meanings separate

The proposed teacher context is a structured vector, not a single latent norm:

| Information | Purpose | Required controls |
|---|---|---|
| Task completion, phase progress, dense global/local tracking | Distinguish tracking from merely avoiding falls | Fixed validation distribution, all episode outcomes |
| Issued-to-applied target discrepancy and realized packet age | Identify transport degradation | Timestamp audit; unavailable on deployments without application timestamps |
| Applied-target-to-measured-motion discrepancy | Describe execution under loading and contact | Phase/load calibration; PD effort is not failure |
| Frozen temporal features of those histories | Test whether temporal structure adds information | Causal filtered error, PCA/random features, identical history and calibration budget |
| Base tilt/angular velocity, contacts, action rate, torque saturation | Detect whole-body degradation invisible to joint targets | Independent measurements and missing-data masks |
| Delivered disturbance dose, elapsed exposure, pre-event failure | Distinguish untested conditions from successful recovery | Episode identity, immutable tape ID, per-event delivery audit |
| Recent per-condition outcomes, score age and sample count | Make uncertainty and forgetting visible | Keep policy version and observation count; no adjacent-window random split |

Where application timestamps exist, raw target errors decompose exactly as
`q_issued - q_measured = (q_issued - q_applied) + (q_applied - q_measured)`.
Distances in a nonlinear latent space do **not** inherit that additive identity.
A useful latent signal should retain sustained lag, bias and unstable oscillation
while reducing specified nuisance sensitivity. Its training objective alone does
not establish that property. Report corrupt-to-clean pretraining accurately;
test pre-failure discrimination at matched false-alarm rates and checkpoint-held-out
splits before giving latent feedback responsibility for curriculum decisions.

Tracking and physical measurements belong to past/current student experience.
The simulator teacher may know which condition it assigned; future event times
and directions must never be added to actor observations. Do not let a teacher
use future outcome labels when computing an online score.

## Implemented comparison and interpretation

The new runtime seam resamples immutable training tapes only at episode reset.
PPO transitions retain the condition ID captured **before** `env.step`, because
native automatic reset chooses the next episode's condition before returning.
A native rollout completes GAE first; the adapter reads unnormalized stored
returns and values before optimization, leaving PPO tensors unchanged. Terminal
segments and segments truncated by a PPO update are labeled separately.

Uniform and PLR use the same bank and nominal cohort. Each decision records its
full sampling distribution, chosen probability, selection reason, condition/tape
fingerprint and policy version. PLR combines rank-based value-L1 priority with
staleness and unseen-condition sampling. A high residual is critic surprise;
it is not a measured marginal training benefit. This is an adaptation of the
[released PLR sampler](https://github.com/facebookresearch/level-replay/blob/main/level_replay/level_sampler.py),
not a complete reproduction of its original benchmark. Valid zero residuals
are retained and tie breaking is explicit.

The integration smoke uses 256 environments, 64 permanently nominal, eight PPO
iterations per arm, training seed 9111 and private teacher seed 9112. The 64-tape
training bank crosses planar velocity increments {0, 0.5, 1.0, 1.5} m/s with shared
bursts {0, 20, 40, 60} ms and four keyed event realizations. Onsets are sampled
from [0.600, 2.500) s and durations from [0.100, 0.500) s in 5 ms ticks. Packets
reissue held physical targets every physics tick. This is not a control-rate
network queue. Background native pushes and actuator delays are zeroed and
checked at the live event manager. Both arms retain the same reference-anchor
loss, fresh optimizer recipe, actor, observations, rewards and transition budget.

These amplitudes are not all outside historical training support. The experiment
changes event timing and transport coupling; name that process explicitly.
Training starts from random native reference phases, whereas full-motion evaluation
uses its evaluator's start convention. Record that difference when interpreting
whether a perturbation was easy because of its contact phase.

## Framework to test after integration

Use a fixed nominal rehearsal share plus a condition-selection distribution;
keep retention validation outside the teacher's training reward. Compare uniform,
PLR-value, dense task feedback, filtered execution feedback and latent feedback
with the same task bank, protection mechanism, teacher update cadence and budget.
Only the feedback representation changes in the signal comparison. A later
schedule-replay control asks whether responding to this particular student helps
beyond reproducing an equally difficult exposure trace.

A finite regret teacher is a separate extension. [PAIRED](https://arxiv.org/html/2012.02096v2)
uses an independently trained antagonist to approximate achievable return on the
same task. A frozen nominal reference used for anchoring cannot substitute for
that antagonist. [GACL](https://arxiv.org/html/2508.02988v1) motivates conditioning
on task/performance history and mixing reference tasks with generated tasks.
Our finite bank and fixed nominal cohort are controlled adaptations, not GACL's
learned task generator or a demonstration of deployment-distribution grounding.
Count antagonist/teacher training, probes and encoder training in total cost.
The counterfactual utility estimator and residual allocator remain gated.

Explainability requires both decision records and discriminating experiments:
show selections, delivered exposure, priority/age, fixed-validation performance
and retention interventions over training. A persuasive explanation would show
that an execution feature changes decisions at matched outcome feedback, and that
removing it reduces held-out robustness without improving nominal retention.
A plotted latent curve alone cannot support that attribution.

## Validation and final evaluation

Before longer training, require completed capsules, online W&B verification,
correct episode attribution, valid selection probabilities, observed event
writes, finite unnormalized scores and the expected policy-update sequence.
The eight-iteration smoke is not a retention or efficacy gate.

Then freeze a budgeted matched pilot and a fixed validation panel before launch.
Use nominal global/local error and completion for retention, and separate
tracking-qualified completion, survival and recovery for timed stress. Report
unreached disturbances and unfinished observation windows rather than replacing
them with favorable scores. Compare policies on common event tapes and preserve
all failures. Extend delay duration and cadence as explicit axes, including
longer bursts and jitter; the existing short-delay survival ceiling cannot test
all timing uncertainty. Reserve fresh tape seeds, directions/onsets and selected
compositions for final testing, and distinguish held-out event realizations from
out-of-range values and unseen temporal processes. Require independent training
seeds before a superiority claim or expansion to more motions.

## Execution record

The first frozen attempt (`timed_replay_smoke_20260911_a`) stopped before training
because GPU free memory fell below 7,500 MiB when another evaluation started.
Its failed receipt is preserved. The replacement campaign
`/home/linjiw/lucid-sonic/experiments/timed_replay_smoke_20260911_b` uses a bounded
30-minute capacity wait and source commit `14fa3a3` in
`/home/linjiw/lucid-timed-plr-20260911b`. Its receipt determines the actual execution
status. Each executed arm enables native online W&B in `16726/lucid-sonic`, with
source/plan/bank fingerprints and a verified run URL. A capacity wait is not a
training run and has no fabricated online result.

CPU validation: 1,973 tests passed before adding the decision-audit module;
focused audit tests are recorded separately. Teacher RNG state round-trips, but
full simulator resume remains unsupported. No utility estimator, residual
allocator, student–antagonist loop or latent-teacher performance is claimed here.

### Completed native training smoke

Attempt B reached simulator initialization but failed before the first PPO update:
the generated disabled-observer config omitted its `_target_`, leaving an OmegaConf
mapping where the callback handler expected an object. The failed online run is
[recorded here](https://wandb.ai/16726/lucid-sonic/runs/timed-91c5381c64067cd4).
Attempt C corrects that launcher configuration in source commit `87c6fcc` at
`/home/linjiw/lucid-timed-plr-20260911c`; earlier frozen worktrees remain unchanged.

Both C arms completed eight updates and 49,152 transitions each. Their online runs
are verified finished: [uniform](https://wandb.ai/16726/lucid-sonic/runs/timed-63097f1dc1fd649f)
and [PLR](https://wandb.ai/16726/lucid-sonic/runs/timed-f042e9c47ada6791).
The receipt is `/home/linjiw/lucid-sonic/experiments/timed_replay_smoke_20260911_c/receipt.json`.
All 467 pre-first-update event/selection/score records match exactly after removing
arm/reason labels. This checks common initialization and scoring before feedback
changes selection; it is not simulator-resume equivalence.

Uniform records 319 practice assignments plus 99 fixed-nominal assignments;
PLR records 214 unseen selections, 110 replay selections and 99 fixed-nominal
assignments. These include unfinished episodes. A constant 25% environment cohort
does not imply exactly 25% of episode resets. Mean selection entropy is 4.159 nats
for uniform and 2.911 for PLR. PLR therefore changes the sampled distribution;
that alone does not establish improved learning.

Every recorded push matches its tape's time and requested velocity increment:
164 writes for uniform, 169 for PLR. Delay-boundary timing/request/packet-age
checks pass for 399 and 378 boundaries, respectively; 165 and 152 positive-delay
onsets are reached. These counts are not full-episode robustness scores, and
interior training packet ages were not audited by this post-hoc boundary check.
Final capsules, source/bank fingerprints, raw scores, decision probabilities and
reference-anchor cost logs are retained outside Git.

The six-cell frozen-policy follow-up is
`/home/linjiw/lucid-sonic/experiments/timed_replay_validation_20260911_a`:
origin/uniform/PLR × nominal/1.5 m/s + 60 ms, 128 aliases, fresh evaluation seed
9120. It uses the previously validated evaluation source snapshot
`/home/linjiw/lucid-ued-eval-20260911b`, with plan and source hashes. This is a
small development comparison; full-physics retention, long-run learning,
independent training seeds and final held-out testing remain outstanding.

One ancillary diagnostic needs investigation before it becomes a teacher input:
nominal aggregate “undesired contact” is near one, with high pelvis/torso
fractions. Net contact force does not distinguish ground contact from self-contact.
The observation should not be interpreted as a near-universal fall or ground
collision rate. No contact-based quality claim is made from these aggregates.

### Candidate execution representation for the next signal comparison

Keep the existing shared motion encoder as a baseline, but distinguish two
research hypotheses. First, a frozen embedding of issued and measured joint
windows may summarize discrepancy better than causal filtering. Second, a
conditional temporal model may distinguish expected PD tracking offsets from
unexpected execution degradation. The latter would condition on recent measured
position/velocity, issued targets, reference phase and available contact/load
indicators, and represent the residual from expected execution. It requires its
own training data and validation; it is not implemented by merely changing the
name of the existing VAE distance.

For either candidate, use past-only windows with explicit control/physics
timestamps and reset masks. Report a vector with magnitude, persistence and
change, calibrated against phase-conditioned nominal validation statistics.
Expose the valid-window count and missing/unsupported phases to the teacher.
Do not force the same representation to suppress every high-frequency component:
a single sensor spike, a real impact and persistent oscillation have different
consequences. Matched nuisance and consequential-perturbation probes, and
independent pre-failure prediction, must decide which distinctions the encoder
actually preserves. With one motion, phase memorization is an especially plausible
alternative explanation; checkpoint-held-out tests and later held-out motions
are required before generalizing the representation claim.

### Completed development validation and decision

All six evaluations completed, covering 768 episode aliases. All scored-event
audits pass with zero measured transport-age mismatches. The same validation
tapes are paired across policies and disjoint from the training bank.

| Policy | Nominal completion | Nominal global/local MPJPE (mm) | Combined-stress completion | Delay reached under stress |
|---|---:|---:|---:|---:|
| Original checkpoint | 128/128 | 132.27 / 28.49 | 75/128 (58.59%) | 113/128 |
| Uniform, +8 updates | 128/128 | 132.23 / 28.69 | 82/128 (64.06%) | 115/128 |
| PLR, +8 updates | 128/128 | 133.99 / 28.15 | 79/128 (61.72%) | 113/128 |

Both continuations meet the inherited nominal-only error/completion margins.
This does not establish full-physics retention, which this small follow-up did
not evaluate. Uniform improves stress completion by seven episodes relative to
the origin; PLR improves it by four and trails uniform by three. Eight updates,
one continuation seed and 128 event realizations do not establish a curriculum
ranking. These are development measurements, not untouched final-test results.
All 128 stress episodes reach the push. Episodes that fail before the delay remain
failures; they do not count as successful delay recovery.

Observed stress global MPJPE is 380.31, 401.78 and 392.14 mm for origin, uniform
and PLR, respectively. Longer survival changes which trajectory portions are
observed, so these values do not independently establish better/worse recovery.
Reference-qualified completion and independently measured recovery are still
needed. Do not report the survival improvements as improved motion quality.

[Analysis and recorded provenance](/home/linjiw/lucid-sonic/experiments/timed_replay_analysis_20260911_a/analysis.json),
[condition-selection figure](/home/linjiw/lucid-sonic/experiments/timed_replay_analysis_20260911_a/condition_choices.png),
[verified online analysis](https://wandb.ai/16726/lucid-sonic/runs/timedanalysis-5dcb694c3e12).
The figure shows PLR concentrating assignments on some stronger combined tasks;
it does not show that those choices were more useful. Raw decision and exposure
records make that distinction inspectable.

Next, run a matched budgeted pilot with checkpoints fixed in advance and include
nominal **and full-physics** retention, dense tracking, push/delay delivery and
recovery on a fixed validation panel. Keep uniform as a serious control. Do not
increase teacher complexity or claim that latent feedback solves the problem
based on this smoke. Collect causal execution histories during that pilot so
filtered/latent features can be tested against dense task feedback on held-out
checkpoints before becoming teacher inputs. Finite antagonist-based regret is
still a separate experiment with its own compute accounting.

The original policy's W&B seed/iteration labels were corrected after validation:
seed 8600, checkpoint iteration 8000, zero additional continuation iterations.
The initial labels had used the comparison continuation seed 9111 and relative
iteration zero. This metadata correction is recorded separately in
`timed_replay_validation_20260911_a/origin_metadata_correction.json`; frozen plans,
commands, checkpoints and measurements were not rewritten.

The full CPU suite passes 1,979 tests with five warnings. A focused regression
also exercises instantiation of the generated disabled callback. Research files
pass Ruff and diff whitespace checks; repository-wide pre-existing formatting
failures are not represented as fixed. All launched work in this campaign is
complete; no longer training campaign is silently running.
