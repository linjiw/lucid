# What real-world deployment would require

**September 2026.** LUCID's paper is a simulation-only diagnostic. The repository contains no hardware,
state-estimator, odometry or motion-capture result of any kind. The only non-Isaac transfer artifact is a
simulator-to-simulator MuJoCo check. This document lists, in order, what would have to be built and
measured to change that. For each tier: what must already be true, the work, the measurement that closes
it, and what would stop it.

Every internal number below is traced to a receipt. Every external citation was opened and checked; where
a figure could not be verified it is omitted rather than softened.

## The hardest obstacle

The deployed actor cannot see its own horizontal path error. In a paired-state experiment over 1,536 base
states and 6,144 horizontal translations of plus or minus 0.25 m, every actor-side observation term, the
G1 encoder output and the action means changed by exactly 0.0, while the critic-only anchor term moved
about 0.2496 in every environment and a 0.25 radian yaw control moved the actions by up to 0.7932. The
critic is discarded at deployment.

The minimal repair appends two input columns carrying reference-minus-robot horizontal displacement.
Traced in code, that input is a motion-library lookup indexed by the exact integer simulator clock, minus
the simulator's own robot body position. It is absolute, drift-free, and unavailable on a real G1. For
scale, the Pronto state estimator reports a proprioceptive-only relative pose error of 83 cm over 10 m
on ANYmal, about 8.3 percent, which exteroceptive LIDAR corrections reduce by roughly 60 percent. Leg
odometry alone does not supply the quantity this input needs, and its error is unbounded in exactly the
two coordinates the input consumes.

So the repaired controller is conditioned on a measurement the robot cannot make. No
deployment-compatibility claim should attach to it until a substitute is named and characterized. This is
a research problem, not an engineering detail.

## Tier 0. Controller prerequisites

**Enter when:** now. Nothing blocks this tier.

**Work.** Both preregistered cross-process rollout no-op gates for the two-column migration failed, at
-1.4926 mm against a 1.0170 mm allowance for curved walking and +1.1823 mm against 1.1120 mm for sideways
walking, and were never repaired. An amended same-state shadow test then passed with a maximum action
difference of exactly 0.0 over 1,701 policy forwards, so the divergence is not in the policy function and
remains unexplained. Report both outcomes wherever the migration is described, and bisect it by running
baseline against baseline in two processes before baseline against expanded.

Characterize the input's usable range: two scalars scaled by 0.3 m, with no clipping, no error model and
no history. Adopt a multi-motion origin, because the local seed-8600 origin and its anchored continuation
qualify on none of three longer development motions at nominal physics, with stooping at 0 percent
completion for both, while the released SONIC controller qualifies at 100 percent on all four under a
byte-identical thresholds file. Then scale past the 128-iteration pilot, which is roughly 2 percent of one
training cell.

**Closes when:** a path-error input trains to a comparable budget on a multi-motion origin, on two seeds,
with held-out motions in the panel, and the divergence is explained or bounded by a measured floor.

**Stops if:** the bisection shows the expanded path genuinely changes rollouts. The migration is then not
a no-op, and the expanded origin cannot be identified with the released one.

## Tier 1. Trustworthy disturbance and recovery measurement

**Enter when:** Tier 0 yields a controller that can represent path error, and a repertoire worth measuring.

**Work.** Repair or retire four verified randomization defects. Friction is drawn per collision shape and
each ankle roll link carries seven collision cylinders, so a wet-tile value of 0.30 sits 4.58 standard
deviations out of the foot-effective distribution. Interval-mode latency resets the delay buffer on every
resample, so jitter cells run 12 to 30 percent of episode time easier than their static arm. Actuator
limits are drawn per joint, so an effort range never presented a uniformly derated robot. Terrain
restitution is multiply-combined against a 0.0 default and has never affected the simulation. Three of the
four remain unfixed in the working tree. From this follows a rule: never report a channel inert until a
read-back confirms the simulator received it.

Then fix the observation window. The development clip is 4.03 seconds, and a capture recorded 191 interval
events, all with zero velocity increment, none in the first quarter of the reference phase, and only 31
with two uninterrupted observed seconds. An inventory of 26 clips of at least 8 seconds exists, 16 in the
adaptation split and 10 in development.

Finally, freeze a recovery contract before any policy is graded. Band, dwell and horizon are required
scorer inputs with no defaults, and the only bands that exist anywhere in the project are explicitly
synthetic. A repository-wide search for frozen phase bands, dwell or a recovery contract returns nothing.

**Closes when:** bands, dwell, horizon, event eligibility and the overlap policy are frozen in a receipt
built from origin-only calibration episodes, and disturbances are reported in the units they are actually
in.

**Stops if:** the selected clips cannot hold an observable window. Do not shorten the horizon to obtain
better labels.

## Tier 2. Does feedback earn its cost

**Enter when:** the recovery contract is frozen and the measurement defects are repaired.

**Work.** Run protected fixed randomization, a frozen open-loop schedule and the feedback arm at one
matched budget on the same origins, scored on the frozen recovery endpoint.

The priors are discouraging and should be stated up front. Across three seeds, extra practice helps by
6.58 points on average with sample standard deviation 2.64, and that decision is recorded as confirmed.
Choosing where to aim it is not: its preregistered rule required both confirmation seeds to be positive
and to average at least +5.0 points, they averaged 3.08, and the recorded verdict is inconclusive or
directionally adverse. Two channels combined are sub-additive by 8.4 points.
Fixed randomization withholds no marginal parameter value that a curriculum would introduce, so a
curriculum needs a concentrated target, and the one concentrated target this project actually trained was
directly learnable and plant-specific, with nominal tracking degrading from 91.44 to 262.74 mm global
error.

**Closes when:** the three arms are ranked on the frozen endpoint with a margin larger than the
between-training-seed effect this project has already measured, which reaches 9.3 points on the same arm.

**Stops if:** the arms tie. That is a publishable negative result and it ends the curriculum line for
hardware.

## Tier 3. Independent origins and a validated export

**Enter when:** Tier 2 has a decision, or its arms tie and the retention recipe alone carries forward.

**Work.** Every continuation result rests on one origin checkpoint and one 4.00 second motion. The
campaign receipt records a training origin count of one, and two continuations from one origin are two
seeds, not two origins. Repeat the frozen protocol on at least two independently trained origins and
report every origin, including failures.

Keep the MuJoCo sim-to-sim gate, which is standard practice before hardware, but state its limits:
absolute survival falls from an Isaac ladder value of 0.820 to 16 percent at the same nominal severity,
the ordering transfers only beyond the training envelope, and at nominal severity the collapsed policy
ranks best. Then stand up the runtime, which does not exist here: the vendored C++ ONNX deployment runner
has no receipt showing it was ever built or run.

**Closes when:** three bench numbers exist. End-to-end policy latency on the target onboard computer.
ONNX-versus-Isaac action parity on identical recorded observations. Joint-order and impedance agreement
between the exported metadata and the training configuration.

**Stops if:** parity fails. A policy that cannot reproduce its simulated actions from exported weights
must not be put on a robot.

## Tier 4. Hardware

**Enter when:** Tiers 0 to 3 are closed and a deployment-side position source is specified.

**Work.** Name the real position source and its error and drift. Specify how world and reference frames
are aligned at start and how clock skew is handled. Specify an evaluation ground truth that is not the
same sensor driving the control input. Then re-run the pilot in simulation with that estimator's measured
noise and drift injected, and report how much of the improvement survives.

For evaluation ground truth, calibrated optical motion capture is the standard: a controlled study of an
eight-camera Vicon system measured 0.153 mm mean absolute error statically and under 2 mm below 1 m/s.
Report its residual beside every tracking number.

Make the pushes physical. LUCID's disturbance is a root-velocity increment in metres per second and
radians per second written directly into simulator state, with no mass, no duration and no contact point
anywhere in the call, so it names no impulse in newton-seconds. A standardized humanoid protocol exists:
the RoboCup Humanoid League push-recovery challenge applies consecutive pushes to a walking robot's centre
of mass with a free-falling pendulum, whose bob mass and release height make the impulse computable and
map to the simulator quantity as a velocity change of impulse divided by robot mass. Log magnitude,
direction and application point for every trial.

Add a real-physics anchor. The strongest recent evidence locates the sim-to-real gain in actuation
modelling rather than randomization width: ASAP pre-trains in simulation, deploys on a Unitree G1, then
fits a delta action model from 100 collected real motion clips, and reports reducing motion tracking error
by up to 52.7 percent in sim-to-real tasks. Budget for attrition: the same campaign records that two
Unitree G1 robots were broken to some extent, attributing it to motor overheating and hardware failure
during data collection.

Safety precedes all of it. The rig needs a hardwired emergency stop that is independent of the control
software, a fall-arrest harness or gantry, and a fallback controller. A software stop flag inside the
control loop, such as the boolean in the vendored deployment runner, is none of these. For a humanoid,
simply cutting power is itself a hazard, because the robot falls.

**Closes when:** a preregistered trial set reports run counts, initial conditions, success criteria and a
stated statistical analysis. A bare success rate is not acceptable evidence.

**Stops if:** no external position source is available. Feeding the policy a drifting estimate whose error
distribution it has never seen is not a deployment.

## What we cannot claim today

No hardware result. No calibrated recovery: no band, dwell or horizon has ever been frozen, so no policy
has passed or failed a recovery test. No curriculum superiority. No impulse in newton-seconds. No
multi-motion retention and no independent origin, because the continuation evidence is one origin, one
motion and two continuation seeds. And no certification of imitation quality, because qualification uses
broad 600 mm global and 50 mm local development thresholds that are not robot tolerances.

## Sources

Internal evidence is receipted in `receipts/analysis/` and under the data root described in the
repository README. External sources, each opened and checked:

- Camurri, Ramezani, Nobili, Fallon. Pronto: A Multi-Sensor State Estimator for Legged Robots in
  Real-World Scenarios. Frontiers in Robotics and AI, 2020. doi:10.3389/frobt.2020.00068
- Merriaux, Dupuis, Boutteau, Vasseur, Savatier. A Study of Vicon System Positioning Performance.
  Sensors 17(7):1591, 2017. doi:10.3390/s17071591
- He et al. ASAP: Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body
  Skills. RSS 2025. arXiv:2502.01143
- Rodriguez et al. RoboCup Humanoid League push-recovery technical challenge. arXiv:1912.07405
- Gu, Wang, Chen. Humanoid-Gym, which makes an Isaac-to-MuJoCo sim-to-sim stage an explicit component of
  the zero-shot transfer pipeline. arXiv:2404.05695
- Kress-Gazit et al. Robot Learning as an Empirical Science: Best Practices for Policy Evaluation.
  arXiv:2409.09491

Claims that could not be verified against an opened source were dropped, including specific pendulum bob
masses and release heights, published push-magnitude norms in newtons or newton-seconds, and trial-count
conventions. Those figures must be established from primary sources before they are used to design a
protocol.
