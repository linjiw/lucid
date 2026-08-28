CONFIDENTIAL. Limited circulation. For review only.
LUCID: Latent-Understanding Curriculum for Informed Domain
Randomization in Humanoid Control
Anonymous Authors
Abstract— Domain Randomization (DR) is widely used for
sim-to-real transfer, yet existing DR curricula are fragile:
Introducing challenging perturbations too early or too abruptly
can cause sharp performance degradation and training collapse,
especially in inherently unstable training tasks like humanoid
motion tracking. To address this issue, we propose Latent-
Understanding Curriculum for Informed Domain Randomiza-
tion (LUCID), a feedback-driven DR scheduler that adjusts
randomization based on the mismatch between commanded
and executed actions. Specifically, LUCID computes a gap
between short windows of commanded joint targets and realized
joint motion under DR perturbation in a latent space using
a pre-trained temporal encoder. This latent representation
provides a structural understanding of valid motion, naturally
filtering out noise. A Proportional–Integral (PI) controller then
adjusts the overall intensity of the DR perturbations based
on this latent gap, ensuring the environment only becomes
harder when the robot demonstrates stable control. In sim-
ulation, LUCID enables stable training without collapse while
introducing and expanding DR factors, including challenging
latency perturbations. Policies trained with LUCID achieve
higher motion-tracking performance across diverse motion
tests than fixed DR, expert-designed schedules, and automatic
domain randomization methods. In sim-to-sim and sim-to-
real transfer, LUCID improves success from 66.7% to 80.0%
when transferred from Isaac Lab to MuJoCo and from 46.7%
to 73.4% on a physical Unitree G1 (vs. Automatic Domain
Randomization), corresponding to +19.9% and +57.2% relative
gains, while reducing mean latent mismatch by 23.1% and
27.8%, respectively.
I. INTRODUCTION
Sim-to-real transfer for high-dimensional humanoid con-
trol remains a central challenge in robotics [1]. Recent
Reinforcement Learning (RL) systems show that whole-body
motion tracking can serve as a scalable objective for learning
diverse, natural behaviors in simulation, from early motion-
imitation frameworks to large-scale trackers that report in-
creasingly capable zero-shot deployment on hardware [2]–
[7]. Despite this progress, real-world performance is still
sensitive to modeling error and hard-to-model effects such
as contact interactions, actuator and sensing characteristics,
and end-to-end latency [8]–[12]. These sensitivities motivate
domain randomization (DR), which aims to reduce the reality
gap by training policies on a distribution of simulated envi-
ronments rather than a single nominal model [13]–[15]. In
dynamics-focused DR, parameters such as masses, inertias,
friction, joint offsets, motor strength, observation noise, and
actuation/observation delay are randomized so that the real
world is more likely to fall within the policy’s training
distribution [16]. However, DR is not “cost-free”: multiple
studies observe that the choice of sampling distribution
and its evolution can strongly affect learning. For example,
uniform sampling over wide ranges can yield high-variance
or suboptimal policies, and overly aggressive randomization
can drive overly conservative behaviors or even prevent
learning [17]–[19].
As a result, DR is often paired with a curriculum that
increases perturbation strength over training [20]–[22]. A
canonical example is Automatic Domain Randomization
(ADR), which expands randomization bounds based on
performance thresholds [23]. Related self-paced approaches
adapt the training distribution to balance robustness and
learning progress [24], [25]. While these curricula reduce
manual tuning, many practical implementations still rely on
coarse, generic outcome feedback such as episodic return or
success rate to decide when to increase difficulty [18]. In
humanoid motion tracking, a key difficulty is that generic
outcome metrics can be delayed and may not provide an
immediate signal that tracking is becoming unstable. More-
over, these outcome metrics do not fully capture how a
policy achieves return: RL policies can exhibit undesirable
high-frequency oscillations or jitter that are problematic for
hardware even when task success remains high [26], [27].
Misguided by such metrics, DR curricula may introduce
challenging perturbations too early or too abruptly, causing
sharp performance degradation and even training collapse,
especially under timing-related effects such as latency. These
issues motivate a more direct feedback signal for DR
scheduling in humanoid tracking.
A natural idea is to monitor humanoid command–
execution mismatch: Common tracking policies output target
joint commands (e.g., desired joint positions) that are tracked
by a low-level controller; under strong DR perturbations the
executed joint motion can lag behind or deviate from the
commanded targets. However, such a mismatch measured
directly in humanoid joint space can be noisy, making it a
fragile curriculum signal.
In this work, we propose LUCID (Latent-Understanding
Curriculum for Informed Domain Randomization), a
feedback-driven DR scheduler that adjusts randomization
based on the mismatch between commanded and executed
actions in a latent space. Specifically, LUCID computes a la-
tent gap between short windows of commanded joint targets
and realized joint motion under DR perturbations using a pre-
trained temporal encoder. This latent representation provides
a structural understanding of valid motion and naturally
filters out high-frequency noise. A Proportional–Integral (PI)
controller then adjusts the overall intensity of DR perturba-
tions based on this latent gap, ensuring the environment only
becomes harder when the robot demonstrates stable control.
Manuscript 1615 submitted to 2026 IEEE/RSJ International Conference
on Intelligent Robots and Systems (IROS). Received March 5, 2026.
CONFIDENTIAL. Limited circulation. For review only.
Our contributions can be summarized as:
• A latent command–execution mismatch metric com-
puted from a pre-trained temporal encoder, providing
a robust feedback signal for DR scheduling;
• A feedback-driven DR scheduler based on a determin-
istic PI controller that adjusts DR intensity to maintain
stability and maximize robustness during training; and
• Experiments on humanoid motion tracking showing im-
proved stability and robustness and improved zero-shot
transfer on a physical Unitree G1 humanoid compared
to fixed DR, expert-designed schedules, and automatic
DR methods.
II. RELATED WORK
We review related work in learning humanoid motion
tracking and sim-to-real transfer, as well as existing DR
curricula and ADR methods.
A. Learning Humanoid Motion Tracking and Sim-to-Real
Transfer
RL has enabled humanoid motion imitation and track-
ing policies that generate diverse whole-body behaviors in
simulation [2], [7]. More recent large-scale tracking systems
further expanded motion coverage and reported increasingly
capable zero-shot deployment on hardware [3], [4]. Across
these pipelines, sim-to-real transfer remains sensitive to hard-
to-model effects such as contact interactions, actuator and
sensing characteristics, and end-to-end latency [12], [28].
To improve robustness, many systems incorporated DR by
randomizing physics and actuation-related parameters during
training [16], [19], [29]. However, practical humanoid track-
ing pipelines often rely on fixed or manually tuned DR ranges
and schedules, and training stability can depend strongly on
when and how quickly perturbations are introduced.
B. DR Curricula and ADR Methods
A common baseline is fixed DR or expert-designed sched-
ules that increase perturbation magnitudes according to a
hand-crafted timetable [20]–[22]. These approaches are sim-
ple and reproducible, but they are open-loop: the schedule
does not adapt to the policy’s current tracking stability. Con-
sequently, they can introduce difficult perturbations too early
(destabilizing learning) or too late (encouraging overfitting to
nominal dynamics), which is especially risky in contact-rich
humanoid motion tracking.
To reduce manual tuning, automatic curricula adapt ran-
domization based on performance [30], [31]. ADR expands
randomization bounds when the policy meets performance
thresholds under the current range [23], and related self-
paced methods update the training distribution to balance
robustness and learning progress [25], [32]. In many imple-
mentations, the feedback signal remains a coarse episodic
outcome (e.g., return or success rate) [18], [23], [24]. For
humanoid tracking, such outcome signals can be delayed
and may not provide early warning that tracking is becoming
unstable; failures such as falls can occur abruptly, and timing-
related effects such as latency can degrade tracking before
success metrics clearly reflect it [12]. Moreover, outcome
metrics do not fully capture how return is achieved: policies
may maintain task success while exhibiting high-frequency
oscillations or jitter that are undesirable for hardware [26],
[27].
Another line of work focuses on how to sample within the
randomized range. Active Domain Randomization (ActDR),
for example, argues that uniform sampling can produce
suboptimal, high-variance policies and proposes learning
a sampling strategy that emphasizes informative variations
[17]. While learned schedulers can improve robustness, they
add algorithmic complexity and additional hyperparameters:
the scheduler must learn (often from scratch) while the
control policy is also learning, which can increase instability
in large-scale humanoid tracking.
Finally, timing and latency are repeatedly identified as
important contributors to sim-to-real failure, and prior work
addressed them by randomizing delays during training [11].
Latency perturbations, however, can be particularly desta-
bilizing when introduced too early or too aggressively in
highly dynamic control, reinforcing the need for curricula
that regulate difficulty carefully.
C. Contrast to LUCID
To address the limitations discussed above, LUCID is
a feedback-driven DR scheduler designed for humanoid
motion tracking with four coupled design choices, in contrast
to existing approaches: (i) Closed-loop difficulty regulation:
instead of open-loop, hand-crafted timetables, LUCID con-
tinuously adjusts the overall DR intensity based on the pol-
icy’s current tracking behavior; (ii) Stability feedback beyond
episodic outcomes: rather than relying solely on delayed
return/success signals, LUCID uses a more direct signal
derived from command–execution mismatch; (iii) Latent
mismatch for contact-rich tracking: to make this mismatch
reliable under contacts and impacts, LUCID computes a
latent gap between short windows of commanded targets
and realized motion using a pre-trained temporal Variational
AutoEncoder (VAE) [33], which attenuates contact transients
and noises that dominate raw joint-space error; and (iv)
Simple, deterministic scheduling: instead of introducing a
second learned component (and its tuning burden), LUCID
uses a deterministic PI controller to scale DR intensity,
increasing difficulty only when the robot demonstrates stable
control.
III. APPROACH
LUCID follows a simple principle: the environment should
become harder only when the robot continues to execute
the policy’s commanded behavior stably. To implement this,
LUCID measures the mismatch between commanded and
executed actions using a latent gap computed by a pre-
trained temporal encoder. A PI controller then adjusts the
overall intensity of DR perturbations to keep this latent gap
near a target level. Fig. 1 shows an overview of LUCID.
Manuscript 1615 submitted to 2026 IEEE/RSJ International Conference
on Intelligent Robots and Systems (IROS). Received March 5, 2026.
CONFIDENTIAL. Limited circulation. For review only.
Encoder Pretraining
Motion Clips
LUCID Framework
Latent
Encoder Decoder Recon.
Loss
Student RL
Student
Window
buffer
Trajectory Environment
Domain
Randomization
(DR)
Simulator/
Real World
Command
Student RL Latent Gap PI Controller DR Scheduling
Policy
Command
Environment
Trajectory
Quantile
Statistics
PI Update
Return Guard
DR Scale
Pre-trained
Encoder
Latent
Gap
Noise
Push
Friction
Delay
Window
buffer
Fig. 1: Overview of LUCID. (Left) We pre-train a temporal VAE encoder on motion windows using a self-supervised
reconstruction objective. During RL training, the tracking policy outputs commanded joint targets qcmd
t , which are executed
by the low-level controller and simulator dynamics (under domain randomization) to produce realized joint motion qexec
t.
(Right) LUCID stacks short command/execution windows, embeds them with the frozen encoder, and computes a latent
command–execution gap δt. At the end of each curriculum epoch, a PI controller summarizes δt with a high-quantile statistic
and updates the scalar DR intensity λ (with a return guard). The updated λ scales all DR channels for the next epoch.
A. Problem Setup: Motion Tracking with Domain Random-
ization
We model humanoid motion tracking as a Partially
Observable Markov Decision Process (POMDP), M=
⟨S,A,O,Tϕ,Ω,R,γ⟩, with each component indicating the
state space, action space, observation space, transition dy-
namics, observation function, reward function, and discount
factor. At time step t, the policy observes ot ∼Ω(·|st)
and outputs an action at ∈A. In our tracking architecture,
at is implemented as target joint positions sent to a low-
level joint controller. The transition dynamics depends on
domain parameters ϕ ∈ RK (e.g., mass, inertia, friction,
motor strength, sensor noise, and latency):
st+1 ∼Tϕ(st+1 |st,at), rt = R(st,at).
LUCID uses a scalar DR multiplier λk ∈[0,1] at cur-
riculum epoch k to scale the overall randomization intensity.
At the start of each episode in epoch k, each randomized
parameter ϕi is sampled from a symmetric interval around a
nominal value:
ϕi ∼U ϕ0
i−λk∆ϕmax
i , ϕ0
i + λk∆ϕmax
i , (1)
where ϕ0
i is the nominal value of parameter ϕi (for i=
1,...,K) and ∆ϕmax
i is its maximum deviation.
B. Command and Execution Windows
At time t, let qcmd
t ∈R|A| denote the commanded joint
targets produced by the policy, and let qexec
t ∈R|A| denote
the realized joint positions. Under strong DR perturbations,
qexec
t can lag behind or deviate from qcmd
t . We form short
temporal windows of length H with stride s:
ct = stack qcmd
t−(H−1)s:t:s ∈RH×|A|
xt = stack qexec
t−(H−1)s:t:s ∈RH×|A|
,
.
Here stack(·) stacks the H vectors in time order, i.e., ct =
[qcmd
t−(H−1)s; qcmd
t−(H−2)s;...; qcmd
t ] and similarly for xt. A raw
joint-space mismatch such as ∥ct−xt∥is often noisy in
humanoid locomotion because contact transients (e.g., foot
impacts) can produce large short-lived deviations. LUCID
therefore computes mismatch in a latent space that preserves
motion structure while attenuating high-frequency noise.
C. Pre-training the Temporal Encoder with a VAE
LUCID uses a pre-trained temporal encoder implemented
as the encoder of a temporal VAE [33]. The VAE is trained
in a self-supervised manner: each input window is also the
reconstruction target, so no labels are required.
a) Training data: We construct a dataset Dof motion
windows w ∈ RH×|A| from a broad set of reference
humanoid motions. During pre-training, we apply noise and
transient-like corruptions to encourage robustness to short
spikes while preserving the underlying motion structure.
b) Model: The VAE consists of an encoder qη(z |w)
and a decoder: pψ(w |z) denotes the probabilistic decoder
(parameterized by ψ), and Dψ(z) is the neural network
that implements it by outputting a reconstructionˆ
w with
a standard Gaussian prior p(z) = N(0,I). The encoder
outputs a diagonal Gaussian approximate posterior:
qη(z|w) = N µη(w), diag(σ2
η(w)).
We sample latent variables using the reparameterization trick:
z= µη(w) + ση(w) ⊙ϵ, ϵ∼N(0,I),
where ⊙denotes elementwise multiplication.
We train the VAE by maximizing the evidence lower
bound (ELBO):
LELBO(w) = Eqη (z|w)[log pψ(w|z)]−KL(qη(z|w) ∥p(z)).
(2)
Manuscript 1615 submitted to 2026 IEEE/RSJ International Conference
on Intelligent Robots and Systems (IROS). Received March 5, 2026.
Algorithm 1 LUCID: DR Scheduling with Latent Gap and
PI Control
.
CONFIDENTIAL. Limited circulation. For review only.
We use a Gaussian decoder, so the reconstruction term
reduces to a mean-squared error loss. We therefore minimize:
LVAE(w) = Eqη (z|w) ∥w−Dψ(z)∥2
F
Lrecon(w)
+ β KL(qη(z|w) ∥N(0,I))
LKL(w)
The first term is the reconstruction loss of w with Frobenius
norm ∥·∥F, while the second term is the KL divergence be-
tween the latent and normal distribution. After pre-training,
we freeze the encoder parameters η and use µη(·) as a
deterministic embedding during RL training.
D. Latent Gap Between Commanded and Executed Motion
Given command and execution windows (ct,xt), we com-
pute deterministic latent embeddings using the frozen VAE
encoder mean:
hcmd
t = µη(ct), hexec
t = µη(xt).
We normalize embeddings to unit length:
hcmd
hexec
zcmd
t =
t
, zexec
t
∥hcmd
t =
t ∥2 + ϵ
∥hexec
t ∥2 + ϵ
,
We define the per-step latent gap as cosine distance:
δt = 1−(zcmd
t )⊤zexec
t. (3)
E. PI Controller for Scheduling DR Intensity
We define a curriculum epoch k as a fixed block of
PPO training with a fixed λk; the set {δt}t∈epoch k includes
all timesteps from all rollouts collected during that epoch.
LUCID updates the DR multiplier once per curriculum
epoch. We first summarize the latent gap within epoch k
using a high percentile p (0.9) to emphasize near-failure
behavior:
1: Input: dataset D; nominal/ranges {ϕ0
i,∆ϕmax
i }K
i=1; PPO con-
fig; epoch length N; window (H,s); quantile p; target ∆target;
¯
PI params (Kp,Ki,α,Imax); guard (
Rmin,γDR)
2: Output: trained policy πθ
3: Pre-train temporal VAE on D; freeze encoder mean µη(·)
4: Initialize θ; λ←0; I ←0; c←0 (c as a low-return counter)
5: for epoch k= 0,1,2,... until training budget do
6: Set DR Scale: use λ to scale all DR ranges for this epoch
7: For each episode rollout: sample ϕi ∼ U(ϕ0
i−
λ∆ϕmax
i , ϕ0
i + λ∆ϕmax
i ) and apply ϕ in simulator
8: Collect rollouts with πθ; log {qcmd
t ,qexec
t }N
t=1 and episodic
returns
9: Update πθ with PPO on collected rollouts
10: Build windows (ct,xt) from logs; compute δt = 1−
(zcmd
t )⊤zexec
t using frozen µη(·)
11: ∆k ←Quantile({δt}t∈epoch k,p);¯
Rk ←mean episodic
return in epoch k
12: c←
¯
c+ 1,
Rk <¯
Rmin
0, otherwise
13: if c≥2 then
14: I ←0; λ←γDRλ; c←0
15: else
16: ek ←∆target
−∆k
17: I ←clip(I+ ek,−Imax, Imax)
18: uk ←clip(Kpek + KiI,−1, 1)
19: λ←clip(λ+ αuk, 0, 1)
20: end if
21: end for
22: return πθ
∆k = Quantile ({δt}t∈epoch k; p).
We choose a target level ∆target from nominal training at
λ = 0 by evaluating a policy on a standardized motion set
and setting ∆target = µnom + 3σnom. Here µnom and σnom are
the mean and standard deviation of the aggregated signal
∆ measured on nominal rollouts (trained/evaluated at λ=
0) over a standardized motion set. We interpret ∆target as
a “stable tracking” reference level for the latent mismatch
signal.
a) PI formulation.: At epoch k, the measured signal is
yk = ∆k, the setpoint is r= ∆target, and the error is
ek = r−yk = ∆target −∆k.
A positive error indicates that mismatch is below the target
(tracking remains stable), so DR can be increased; a negative
error indicates mismatch above target, so DR should be
reduced. We implement a discrete-time PI controller with
integral clamping:
I0 = 0, Ik = clip(Ik−1 + ek,−Imax, Imax),
uk = clip(Kpek + KiIk,−1, 1),
λk+1 = clip(λk + αuk, 0, 1).
Here Imax >0 bounds the integral state (anti-windup), and
clip(x,a,b) = min(max(x,a),b) enforces output saturation.
Kp and Ki are the proportional and integral gains, and
α bounds how much λ can change per epoch. Integral
clamping provides anti-windup, preventing the integral state
from growing without bound under saturation.
The updated multiplier λk+1 is applied to domain random-
ization in the next curriculum epoch. Specifically, for each
randomized simulator parameter ϕi we scale its deviation
range by λk+1 and sample episode parameters as in Eq. (1).
Thus, a single scalar λ uniformly scales the overall DR
intensity across all channels (e.g., noise, pushes, friction, and
delay), while keeping their relative ranges fixed.
F. Return Guard
To prevent issuing overly aggressive DR scales, we add a
return guard. Let¯
Rk denote the mean episodic return over
rollouts collected in epoch k. If the average epoch return falls
below a predefined value¯
Rmin for two consecutive epochs,
we reset the integral state and decay DR:
Ik ←0, λk+1 ←γDR λk.
Algorithm 1 shows the pseudo code of LUCID.
IV. EXPERIMENTS
We evaluate LUCID in simulation and on a physical
Unitree G1 humanoid. Our experiments are designed to
validate three claims: (1) LUCID improves robustness under
Manuscript 1615 submitted to 2026 IEEE/RSJ International Conference
on Intelligent Robots and Systems (IROS). Received March 5, 2026.
CONFIDENTIAL. Limited circulation. For review only.
TABLE I: Domain randomization ranges used in our experiments. Units: m, rad, m/s, rad/s, and ms.
Term Range Term Range
Dynamics / Initialization
Friction (static) [0.3, 1.6] Friction (dynamic) [0.3, 1.2]
Restitution [0.0, 0.5] Joint offset (rad) ±0.01
CoM offset x (m) ±0.025 CoM offset y,z (m) ±0.05
Root pos offset x,y (m) ±0.05 Root pos offset z (m) ±0.01
Root rot offset roll,pitch (rad) ±0.10 Root rot offset yaw (rad) ±0.20
Root vel offset vx,vy (m/s) ±0.50 Root vel offset vz (m/s) ±0.20
Root ang vel roll,pitch (rad/s) ±0.52 Root ang vel yaw (rad/s) ±0.78
Joint reset perturb. (rad) ±0.10– –
Observation Noise
Base lin vel noise (m/s) ±0.50 Base ang vel noise (rad/s) ±0.20
Joint pos noise (rad) ±0.01 Joint vel noise (rad/s) ±0.50
Anchor pos noise (m) ±0.25 Anchor ori noise (rad) ±0.05
External Perturbations
Push interval (s) [1.0, 3.0] Push scale [0.0, 1.0]
Push impulse vx,vy (m/s) ±0.50 Push impulse vz (m/s) ±0.20
Actuation delay (ms) [0, 40]– –
out-of-distribution (OOD) perturbations; (2) LUCID yields a
more stable DR curriculum during training (avoiding abrupt
instability when introducing challenging perturbations); and
(3) when evaluated under the same fixed OOD perturbation
presets (with scheduling disabled), policies trained with
LUCID exhibit smaller and smoother command–execution
mismatch (latent gap) and correspondingly smaller perfor-
mance drops.
A. Experimental Setup
We train humanoid motion-tracking policies in Isaac Lab
using a Unitree G1 model. The policy outputs target joint
positions at 50 Hz, tracked by a low-level joint controller.
Unless otherwise stated, we train each method for the same
budget of 3 ×107 environment steps with 4096 parallel
environments and report results over 5 seeds. Evaluation
uses deterministic actions and shared episode seeds across
methods.
1) DR Configuration: We randomize dynamics, initializa-
tion offsets, observation noise, external pushes, and actuation
delay to improve sim-to-real robustness [9]–[11]. All meth-
ods use the same DR term set and the same maximum ranges
(Table I); methods differ only in how the global DR intensity
is scheduled (Fixed-DR, ADR, or LUCID).
For actuation delay, we implement a First In, First Out
buffer at 50 Hz and randomize the delay uniformly in the
range shown in Table I during training (0–40 ms).
B. Baselines
We compare against DR scheduling baselines commonly
used in practice: Fixed-DR, an expert-designed schedule;
and ADR, an outcome-driven curriculum based on episodic
return [23]. We also include LUCID (Raw Mismatch), which
keeps the same PI controller but replaces the latent gap with a
raw joint-space window mismatch. All methods use identical
PPO settings, reward structure, DR term set, and training
budget; only the curriculum scheduler differs.
C. Evaluation Presets and Metrics
We evaluate each final policy under three fixed evaluation
presets (i.e., no curriculum updates during evaluation): (i)
ID-Clean, where all domain parameters are set to nominal
values; (ii) OOD-Heavy DR, where we enable the full DR
term set and, at the start of each episode, sample every
randomized term from the uniform ranges in Table I (i.e.,
the maximum perturbation bounds); and (iii) Latency Stress,
where we isolate timing mismatch by fixing actuation de-
lay to an unseen value of 60 ms while keeping all other
parameters nominal. The Latency Stress preset intentionally
exceeds the maximum delay used in training (40 ms), testing
robustness to out-of-range delay without confounding effects
from additional DR changes.
We report Success Rate (SR, no fall before the time limit)
and tracking quality: mean per-keypoint error (MPKPE)
Empkpe (mm) and mean per-joint error (MPJPE) Empjpe (rad).
To directly measure command–execution consistency, we
compute the latent gap δt (Eq. (3)) using the same frozen
encoder for all methods. We evaluate δt over a fixed horizon
ofTeval=100 control steps. If an episode terminates early due
to a fall at tterm, we set δt ← 2 for all remaining steps
t∈[tterm,Teval]. We report the per-episode mean.
D. Simulation Results: Robustness and Gap Regulation
Table II summarizes performance across the three pre-
sets. Across presets, LUCID achieves higher SRs while
maintaining a smaller latent gap, indicating that improved
robustness coincides with more consistent command and
execution rather than only higher episodic outcomes.
Under ID-Clean, LUCID matches or exceeds the strongest
baseline on SR while maintaining a low latent gap, indicating
that training with an adaptive DR curriculum does not
sacrifice nominal tracking performance. Under OOD-Heavy
DR, LUCID attains the highest SR and the lowest latent
mismatch, suggesting improved robustness to large parameter
perturbations. Under the Latency Stress preset (60 ms, unseen
Manuscript 1615 submitted to 2026 IEEE/RSJ International Conference
on Intelligent Robots and Systems (IROS). Received March 5, 2026.
CONFIDENTIAL. Limited circulation. For review only.
TABLE II: Simulation results from IsaacLab. Higher success is better; lower gap and error are better.
Method ID SR ↑ OOD SR ↑¯
δ (OOD) ↓ Latency SR ↑¯
δ (Latency) ↓ Empkpe ↓ Empjpe ↓
Fixed-DR ADR 80.4 ±1.8 61.7 ±2.3 0.156 ±0.012 52.6 ±2.7 0.241 ±0.018 112.4 ±3.6 0.312 ±0.015
81.2 ±1.5 68.9 ±1.9 0.131 ±0.010 60.3 ±2.1 0.209 ±0.016 104.8 ±3.1 0.287 ±0.013
LUCID (Raw Mismatch) 82.6 ±1.4 62.5 ±1.7 0.149 ±0.009 58.8 ±1.8 0.213 ±0.014 105.6 ±2.8 0.292 ±0.011
LUCID (Ours) 84.3 ±1.2 78.4 ±1.5 0.082 ±0.007 74.2 ±1.6 0.141 ±0.011 91.3 ±2.4 0.240 ±0.009
Fixed-DR
ADR
LUCID
Gap t (lower is better)
0.10
0.09
0.08
0.07
0.06
0.05
0.0 0.5 1.0 1.5 2.0
Time (s)
Command-Execution Gap Under OOD Perturbations (AMASS)
Median ± IQR across episodes and seeds
OOD-Heavy DR
0.30 Latency Stress (60 ms)
Fixed-DR
0.25
ADR
LUCID
0.20
0.15
0.10
0.05
0.0 0.5 1.0 1.5 2.0
Time (s)
Fig. 2: Temporal command–execution mismatch under OOD
evaluation presets. We plot the latent gap δt (median ±
interquartile range across episodes and seeds) over the first
Teval=100 control steps for OOD-Heavy DR and Latency
Stress (60 ms). The initial flat prefix reflects window warmup
before the first valid embedding is available.
TABLE III: Sim-to-sim and sim-to-real transfer on 5 motions
(3 trials/motion). Mean ±std across motions.
Method
MuJoCo
SR (%) ↑/¯
δ ↓
Unitree G1
SR (%) ↑/¯
δ ↓
Fixed-DR 60.0±14.9 / 0.15±0.02 26.7±14.9 / 0.22±0.04
ADR 66.7±23.6 / 0.13±0.01 46.7±18.3 / 0.18±0.03
LUCID (Ours) 80.0±18.2 / 0.10±0.01 73.4±14.9 / 0.13±0.02
ADR and 60.0% for Fixed-DR) while also reducing the latent
gap to 0.10 (vs. 0.13 and 0.15). On the physical Unitree G1,
the advantage is larger: LUCID achieves 73.4% success (vs.
46.7% and 26.7%) and the lowest mismatch 0.13±0.02 (vs.
0.18 and 0.22).
These results are consistent with our hypothesis that reg-
ulating a motion-structure-aware command–execution mis-
match during training yields policies whose commands
remain more realizable under dynamics and timing mis-
match. Fig. 2 visualizes this effect over time: under both
OOD-Heavy DR and the unseen 60 ms Latency Stress pre-
set, LUCID maintains a lower median latent gap with a
tighter interquartile-range band, indicating not only a smaller
average mismatch but also reduced variability and fewer
abrupt mismatch spikes early in the episode. Importantly,
the improvements are not limited to higher episodic success:
LUCID also reduces¯
δ in both transfer domains, and the
largest gap reduction coincides with the largest success
improvement on real hardware, where small command–
execution mismatch can accumulate and trigger falls over
time.
in training), LUCID again achieves higher success with a
lower latent gap, indicating improved tolerance to timing
mismatch.
E. Cross-Simulator and Sim-to-Real Transfer
To evaluate transfer beyond the Isaac Lab training sim-
ulator, we perform a cross-domain transfer evaluation by
deploying the same policy checkpoints trained in Isaac Lab to
(i) a different physics engine (MuJoCo) and (ii) a physical
Unitree G1 humanoid. Because MuJoCo differs in contact
modeling and numerical integration, this test probes whether
robustness reflects improved command realizability rather
than overfitting to Isaac Lab-specific simulation details.
a) Protocol.: We select 5 motions and execute 3 trials
per motion (15 trials total) in each target domain. A trial
is considered successful if the robot completes the full
motion horizon without falling or triggering a safety stop.
To quantify command realizability, we compute the latent
command–execution gap δt using the same frozen encoder
as in simulation and summarize each trial by its mean¯
δ. For
reporting, we compute success rate (SR) as the fraction of
successful trials out of the 15 total trials in the domain, and
report it as a percentage. We report¯
δ as mean ±std across
the 15 trials. Table III reports each result as SR (%) /¯
δ.
b) Results and discussion.: Table III shows that LUCID
provides the strongest transfer to both MuJoCo and hardware.
In MuJoCo, LUCID improves SR to 80.0% (vs. 66.7% for
V. CONCLUSIONS AND FUTURE WORK
We present LUCID, a closed-loop curriculum for DR in
humanoid motion tracking. Instead of relying on delayed
episodic outcomes, LUCID uses a latent command–execution
mismatch signal, computed from short command/execution
windows via a frozen temporal encoder, to decide when to
increase or decrease randomization intensity. A simple PI
controller converts this signal into a deterministic schedule,
making training difficulty rise only when tracking remains
stable. In simulation, LUCID improves robustness to OOD
dynamics and is especially effective under severe, unseen
latency stress, while also reducing curriculum fragility when
expanding delay perturbations. In sim-to-sim and sim-to-real
transfer, LUCID improves SR by 19.9% in MuJoCo and
57.2% on Unitree G1 (vs. ADR), while reducing mean latent
mismatch by 23.1% and 27.8%, respectively.
There are several promising directions for future work.
First, while the frozen temporal encoder provides a robust
and low-overhead latent representation, it may be beneficial
to explore alternative self-supervised objectives (e.g., con-
trastive or masked modeling) or lightweight online adaptation
to better match the policy’s evolving behaviors and the
statistics of real hardware data. Finally, another interesting
direction is applying the same latent mismatch regulation
principle beyond joint-position tracking—for example, to
torque control, whole-body force objectives, or contact-aware
representations—and studying theoretical links between mis-
match regulation and curriculum stability in contact-rich RL.
Manuscript 1615 submitted to 2026 IEEE/RSJ International Conference
on Intelligent Robots and Systems (IROS). Received March 5, 2026.
CONFIDENTIAL. Limited circulation. For review only.
REFERENCES
[1] N. Jakobi, P. Husbands, and I. Harvey, “Noise and the reality gap: The
use of simulation in evolutionary robotics,” in European conference
on artificial life. Springer, 1995, pp. 704–720.
[2] X. B. Peng, P. Abbeel, S. Levine, and M. van de Panne, “Deepmimic:
Example-guided deep reinforcement learning of physics-based char-
acter skills,” arXiv preprint arXiv:1804.02717, 2018.
[3] Q. Liao, T. E. Truong, X. Huang, Y. Gao, G. Tevet, K. Sreenath, and
C. K. Liu, “Beyondmimic: From motion tracking to versatile humanoid
control via guided diffusion,” arXiv preprint arXiv:2508.08241, 2025.
[4] Z. Luo, Y. Yuan, T. Wang et al., “Sonic: Supersizing motion
tracking for natural humanoid whole-body control,” arXiv preprint
arXiv:2511.07820, 2025.
[5] N. Heess, D. Tb, S. Sriram, J. Lemmon, J. Merel, G. Wayne, Y. Tassa,
T. Erez, Z. Wang, S. Eslami et al., “Emergence of locomotion
behaviours in rich environments,” arXiv preprint arXiv:1707.02286,
2017.
[6] J. Merel, L. Hasenclever, A. Galashov, A. Ahuja, V. Pham, G. Wayne,
Y. W. Teh, and N. Heess, “Neural probabilistic motor primitives for
humanoid control,” arXiv preprint arXiv:1811.11711, 2018.
[7] X. B. Peng, Z. Ma, P. Abbeel, S. Levine, and A. Kanazawa, “Amp:
Adversarial motion priors for stylized physics-based character con-
trol,” ACM Transactions on Graphics (ToG), vol. 40, no. 4, pp. 1–20,
2021.
[8] W. Zhao, J. P. Queralta, and T. Westerlund, “Sim-to-real transfer in
deep reinforcement learning for robotics: a survey,” in 2020 IEEE
symposium series on computational intelligence (SSCI). IEEE, 2020,
pp. 737–744.
[9] X. B. Peng, M. Andrychowicz, W. Zaremba, and P. Abbeel, “Sim-to-
real transfer of robotic control with dynamics randomization,” in 2018
IEEE international conference on robotics and automation (ICRA).
IEEE, 2018, pp. 3803–3810.
[10] J. Tan, T. Zhang, E. Coumans, A. Iscen, Y. Bai, D. Hafner, S. Bo-
hez, and V. Vanhoucke, “Sim-to-real: Learning agile locomotion for
quadruped robots,” arXiv preprint arXiv:1804.10332, 2018.
[11] C. S. Imai, M. Zhang, Y. Zhang, M. Kierebi´ nski, R. Yang, Y. Qin, and
X. Wang, “Vision-guided quadrupedal locomotion in the wild with
multi-modal delay randomization,” in 2022 IEEE/RSJ international
conference on intelligent robots and systems (IROS). IEEE, 2022,
pp. 5556–5563.
[12] Y. Bouteiller, S. Ramstedt, G. Beltrame, C. Pal, and J. Binas, “Rein-
forcement learning with random delays,” in International conference
on learning representations, 2020.
[13] J. Tobin, R. Fong, A. Ray, J. Schneider, W. Zaremba, and P. Abbeel,
“Domain randomization for transferring deep neural networks from
simulation to the real world,” in 2017 IEEE/RSJ international con-
ference on intelligent robots and systems (IROS). IEEE, 2017, pp.
23–30.
[14] F. Sadeghi and S. Levine, “Cad2rl: Real single-image flight without a
single real image,” arXiv preprint arXiv:1611.04201, 2016.
[15] J. Tremblay, A. Prakash, D. Acuna, M. Brophy, V. Jampani, C. Anil,
T. To, E. Cameracci, S. Boochoon, and S. Birchfield, “Training deep
networks with synthetic data: Bridging the reality gap by domain
randomization,” in Proceedings of the IEEE conference on computer
vision and pattern recognition workshops, 2018, pp. 969–977.
[16] L. Pinto, M. Andrychowicz, P. Welinder, W. Zaremba, and P. Abbeel,
“Asymmetric actor critic for image-based robot learning,” arXiv
preprint arXiv:1710.06542, 2017.
[17] B. Mehta, M. Diaz, F. Golemo, C. J. Pal, and L. Paull, “Active domain
randomization,” arXiv preprint arXiv:1904.04762, 2019.
[18] G. Tiboni, P. Klink, J. Peters, T. Tommasi, C. D’Eramo, and G. Chal-
vatzaki, “Domain randomization via entropy maximization,” arXiv
preprint arXiv:2311.01885, 2023.
[19] A. Rajeswaran, S. Ghotra, B. Ravindran, and S. Levine, “Epopt:
Learning robust neural network policies using model ensembles,”
arXiv preprint arXiv:1610.01283, 2016.
[20] Y. Bengio, J. Louradour, R. Collobert, and J. Weston, “Curriculum
learning,” in Proceedings of the 26th annual international conference
on machine learning, 2009, pp. 41–48.
[21] S. Narvekar, B. Peng, M. Leonetti, J. Sinapov, M. E. Taylor, and
P. Stone, “Curriculum learning for reinforcement learning domains:
A framework and survey,” Journal of Machine Learning Research,
vol. 21, no. 181, pp. 1–50, 2020.
[22] R. Portelas, C. Colas, K. Hofmann, and P.-Y. Oudeyer, “Teacher algo-
rithms for curriculum learning of deep rl in continuously parameterized
environments,” in Conference on Robot Learning. PMLR, 2020, pp.
835–853.
[23] OpenAI, I. Akkaya, M. Andrychowicz et al., “Solving rubik’s cube
with a robot hand,” arXiv preprint arXiv:1910.07113, 2019, introduces
Automatic Domain Randomization (ADR).
[24] P. Klink, H. Abdulsamad, B. Belousov, and J. Peters, “Self-paced
contextual reinforcement learning,” in Conference on Robot Learning.
PMLR, 2020, pp. 513–529.
[25] C. Florensa, D. Held, M. Wulfmeier, M. Zhang, and P. Abbeel, “Re-
verse curriculum generation for reinforcement learning,” in Conference
on robot learning. PMLR, 2017, pp. 482–495.
[26] G. Christmann, Y.-S. Luo, H. Mandala, and W.-C. Chen, “Benchmark-
ing smoothness and reducing high-frequency oscillations in continuous
control policies,” in 2024 IEEE/RSJ International Conference on
Intelligent Robots and Systems (IROS). IEEE, 2024, pp. 627–634.
[27] S. Mysore, B. Mabsout, R. Mancuso, and K. Saenko, “Regularizing
action policies for smooth control with reinforcement learning,” in
2021 IEEE International Conference on Robotics and Automation
(ICRA). IEEE, 2021, pp. 1810–1816.
[28] H. Ju, R. Juan, R. Gomez, K. Nakamura, and G. Li, “Transferring
policy of deep reinforcement learning from simulation to reality for
robotics,” Nature Machine Intelligence, vol. 4, no. 12, pp. 1077–1087,
2022.
[29] Y. Chebotar, A. Handa, V. Makoviychuk, M. Macklin, J. Issac,
N. Ratliff, and D. Fox, “Closing the sim-to-real loop: Adapting simula-
tion randomization with real world experience,” in 2019 international
conference on robotics and automation (ICRA). IEEE, 2019, pp.
8973–8979.
[30] L. Wang, Z. Xu, P. Stone, and X. Xiao, “Gacl: Grounded adaptive
curriculum learning with active task and performance monitoring,” in
2025 IEEE/RSJ International Conference on Intelligent Robots and
Systems (IROS). IEEE, 2025, pp. 591–596.
[31] L. Wang, T. Xu, Y. Lu, and X. Xiao, “Reward training wheels:
Adaptive auxiliary rewards for robotics reinforcement learning,” in
2025 IEEE/RSJ International Conference on Intelligent Robots and
Systems (IROS). IEEE, 2025, pp. 15 262–15 267.
[32] M. Dennis, N. Jaques, E. Vinitsky, A. Bayen, S. Russell, A. Critch,
and S. Levine, “Emergent complexity and zero-shot transfer via
unsupervised environment design,” Advances in neural information
processing systems, vol. 33, pp. 13 049–13 061, 2020.
[33] P. K. Diederik and W. Max, “An introduction to variational autoen-
coders,” Foundations and Trends® in Machine Learning, vol. 12, no. 4,
pp. 307–392, 2019.
Manuscript 1615 submitted to 2026 IEEE/RSJ International Conference
on Intelligent Robots and Systems (IROS). Received March 5, 2026.