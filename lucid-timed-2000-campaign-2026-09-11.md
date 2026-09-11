# Fixed-budget timed curriculum campaign — September 11, 2026

## Decision and active execution

The user requested at least 2,000 epochs and evaluation. Here the executable budget
is **2,000 outer PPO iterations per arm**, each containing 256 environments × 24
transitions, or **12,288,000 transitions per arm**. PPO's internal optimization
passes are separate. This is a continuation from a competent original policy,
with a fresh optimizer and identical reference-policy anchoring in both arms;
it is not training from scratch or evidence of convergence.

Compare uniform sampling against the existing finite-bank PLR adaptation on
`walk_hands_on_back_loop_002__A066_M`. Both retain 64 nominal environments and
192 practice environments. All other native policy, reward, anchor and task
settings match the validated 64-update pilot. The latent observer is disabled.
The historical trace collector is deliberately preserved; its `done` labels do
not separate timeout from physical termination.

- Frozen source: `/home/linjiw/lucid-timed-2000-20260911`, commit `7119f5c`.
- Campaign: `/home/linjiw/lucid-sonic/experiments/timed_replay_2000_20260911_a`.
- Campaign SHA256: `64d9692235fefa7a4f0215e0a58cd027620ded5a571fa3ad8bc7d35705f1a858`.
- Training plan SHA256: `8bbb2930b605637959bcafb5322c6698a7f2a82e6d3eb44492d94abb1cc6f074`.
- Source/input hashes and exact commands: `campaign.json` and `train/plan.json`.
- Online group: `timed_replay_2000_20260911`, entity `16726`, project `lucid-sonic`.
- [Read-only campaign monitor](https://wandb.ai/16726/lucid-sonic/runs/timedwatch-64d9692235fefa7a).
- [Uniform training](https://wandb.ai/16726/lucid-sonic/runs/timed-3bec9f439a23fe6a).

At the initial execution check, uniform completed six iterations. PLR and all
new endpoint evaluations remained queued. GPU free memory initially fell below
7,500 MiB; the launcher waited and then started when the gate passed. The source
and inputs are checked before every stage. The supervisor runs independently of
the chat, stops on an error, and preserves logs and status in `sequence/receipt.json`.
There is no automatic simulator restart or claim of exact simulator resume.
A capacity wait is bounded at 24 hours; a failure requires inspection rather than
silently changing the experiment. The online monitor labels queueing separately
from active training and does not substitute its process statistics for GPU work.

Validation before launch: the frozen runtime suite passed **2,059 tests** (six
warnings); the sequence runner passed **three additional tests** covering ordering,
failure propagation, and rejection of changed source. Changed launchers passed
Ruff and Python compilation. Existing source behavior from the short pilot is
retained; no new latent or factorized training method is implied by these tests.

## Predeclared endpoint evaluation

Use the fixed final iteration 2,000 for both arms, with the original policy as a
third comparator. A midpoint capsule is diagnostic only and cannot replace a
failed final checkpoint. No checkpoint selection uses these evaluations.

| Panel | Seeds | Conditions per policy | Episodes per cell |
|---|---|---|---:|
| Development validation | 9130 | nominal; full physics with zero actuator delay; timed 1.5 m/s + 60 ms | 128 |
| Held-out endpoint test | 9140, 9141, 9142 | same three, plus out-of-range timed 2 m/s + 80 ms | 128 |

Total: **45 cells and 5,760 episode aliases**. These are repetitions of one motion,
not 5,760 independent motions or independent training seeds. Seeds are matched
across policies. No test results may tune this campaign; future tuning must label
these seeds development data and reserve a new test.

The training bank contains 64 tapes: four push magnitudes × four delay magnitudes
× four fixed realizations. Evaluation draws event realizations using a distinct
split/seed. Push onset, direction and burst duration vary according to the
specified simulator law. A push is a planar **velocity increment**, not an impulse
in N·s. Delay is implemented by target reissue at 5 ms physics ticks. Bursts last
0.10–0.495 s, with onset at 0.60–2.495 s. This does not model persistent latency,
all packet-network effects, or arbitrary deployment disturbances. The 2 m/s and
80 ms magnitudes exceed training maxima of 1.5 m/s and 60 ms. Full-physics
randomization is evaluated separately and explicitly pins actuator delay to zero.

For nominal and full-physics retention, compare each trained arm with its matched
origin cell: completion must drop by no more than two percentage points, and
both global and local MPJPE must remain within 1.10 times the original. Report
all checks per seed. A stress gain that fails retention is a tradeoff, not an
unqualified improvement. Observed pre-termination tracking and survival remain
separate; endpoint completion does not independently establish recovery quality.

Each seed's analysis records training curves, condition assignment frequencies,
delivery audits, retention checks, metric hashes and online URLs. Assignment
frequency explains what was practiced, not whether it caused learning. Training
reward changes with the teacher's distribution and is not a fixed robustness score.

## Research interpretation and next framework

GACL uses a teacher with task/performance history, a learned task generator,
antagonist-based regret, and alternating reference/synthetic task sampling. Its
latent representation encodes environments, whereas LUCID's encoder represents
motion windows; these are different roles. Our nominal cohort and reference-policy
anchor do not constitute a faithful GACL implementation. The useful design lesson
is to retain task history and independently defined reference exposure while
adapting practice. [GACL](https://arxiv.org/html/2508.02988v1)

PAIRED uses an antagonist–protagonist return difference to favor tasks with
achievable improvement potential. A high command discrepancy or value error is
not that regret and does not prove solvability. We are not training the extra
antagonist or adversarial generator in this campaign.
[PAIRED](https://arxiv.org/abs/2012.02096)

The official PLR implementation includes absolute return–value error, partial
rollout accumulation, score updates and staleness. Our existing finite-bank,
ordered-segment adaptation must remain explicitly labeled; this campaign does
not establish parity with all upstream PLR episode-buffer semantics.
[Official PLR sampler](https://github.com/facebookresearch/level-replay/blob/main/level_replay/level_sampler.py)

The proposed next distinction is **severity selection versus event realization**.
Let the teacher choose push/delay severity `c`, then draw onset, direction and
duration `u` from a fixed reference law. The joint sampling distribution is
`p_k(c, u) = p_k(c) p_ref(u | c)`. If independence is deliberately chosen, use
`p_ref(u)` and state that assumption. Severity is controllable curriculum
information; the policy receives no privileged future event schedule. This is
our hypothesis, not an established transfer guarantee or a SAMPLR implementation.
The existing CPU-tested factorized adapter is not integrated into this campaign.
A subsequent matched uniform/PLR × exact/fresh-event study should isolate that
change before combining it with a new feedback representation.

## What the teacher should observe

Keep separate measurements with identifiable roles before considering a learned
fusion or scalar score:

| Measurement | Definition and intended role | Qualification |
|---|---|---|
| Exposure | requested and delivered perturbation, command age, time since onset, coverage and staleness | verifies whether a condition was actually experienced |
| Execution deviation | phase-calibrated causal raw/EMA error and corrected latent discrepancy | empirical proxies; nonzero PD error can generate legitimate torque |
| Task quality | independent reference tracking, motion phase/timing, completion | prevents low-motion or low-discrepancy behavior from appearing sufficient |
| Recovery | predeclared post-event tracking/base-state restoration, with physical failure and timeout separated | needs validated new labels; old trace `done` is insufficient |
| Learning history | matched-policy-version performance on fixed probe conditions, counts and uncertainty | changes under adaptive training exposure alone are confounded |
| Retention | fixed nominal and original-envelope tracking/completion relative to the original | constrains forgetting independently of the teacher score |

The corrected encoder still reconstructs issued PD targets less accurately than
measured motion. Thus, first compare corrected latent command–execution discrepancy
against causal EMA under identical calibration. A second, distinct candidate is
latent **reference–realized motion** discrepancy, whose two inputs are motion
trajectories; it measures tracking and must not be renamed command execution.
A conditional expected-execution model could later account for command history,
phase and loading, but its calibration and benefit need evidence before use.
None of these candidates is a stability certificate or a counterfactual utility
estimator, whose documented gates remain closed.

Use joint-order-checked windows, past-only timestamps, reset-safe buffers and
nominal phase calibration. Assess incremental information beyond EMA and dense
tracking on policy/checkpoint-held-out data; adjacent overlapping windows are not
independent samples. Examine short versus long windows for fast latency transients
and sustained deviations. Only future, independently defined physical degradation
labels can justify detection-lead-time claims. Keep such representation tests
separate from the 2,000-update performance comparison now running.
