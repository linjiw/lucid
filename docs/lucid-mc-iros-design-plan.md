# LUCID-MC — elevator pitch and IROS-2026 strengthening plan

(Saved 2026-08-27 from user-provided documents. Written against the original LUCID-v1
/ BeyondMimic-style setup (4096 envs, 3e7 steps, real-G1 numbers 26.7/46.7/73.4). The
per-channel PI + probe-env idea and the evaluation protocol (E1–E9) are the reusable
parts; the compute table and real-robot campaign are not achievable before ICRA. See
`~/lucid/fable.md` §8.)

---

## Elevator version

**Core idea (one sentence):** A DR curriculum should get harder only along the channel the robot is currently failing on, and "failing" should be measured by whether commanded motion is still being realized — not by delayed episodic return.

**Method (LUCID-MC), three moves:**
1. *Signal.* A frozen temporal motion encoder embeds short windows of commanded vs. executed joint trajectories; their cosine distance in latent space is the "realizability gap." It filters contact noise and rises before return drops.
2. *Attribution.* A few percent of the parallel envs are single-channel probes (only delay randomized, only pushes, only dynamics…). Each probe group gives a clean per-channel gap with zero extra compute.
3. *Control.* One PI loop per channel drives its own intensity λ_c toward a fixed gap set-point (μ+3σ from nominal). Channels the policy tolerates expand fast; the destabilizing one (latency) expands only as fast as it's absorbed.

**Evaluation metric — the one-line answer:** Stop reporting three point presets and report a **robustness profile**: success rate as a function of DR intensity s, swept from 0 to 1.5× the training max, with IQM + bootstrap CIs over seeds. Summarize it with two numbers — **area under the profile** (overall capability) and **worst-bin SR** (did the curriculum sacrifice anything). Then two corroborators that don't depend on the encoder: a per-channel stress heatmap (each channel alone at 1×/1.5×/2×, latency swept to 100 ms) and real-robot SR over ≥50 trials with Wilson CIs plus action jerk.

**Why this framing sells:** the claim becomes "true capability = the whole curve, including beyond-training intensities," which is exactly what distinguishes generalization from fitting the current distribution.

---

# LUCID: Design and Experiment Plan for a Stronger IROS 2026 Submission

## 1. Diagnosis of the current draft

LUCID's core idea is strong and timely: use a frozen temporal motion encoder to measure a command-vs-executed *latent gap* and close a PI loop that expands domain randomization (DR) only as fast as the policy can absorb it. The sim-to-real numbers (G1 success 26.7 / 46.7 / 73.4 for Fixed-DR / ADR / LUCID) are a compelling headline, and the anchor-centered latency framing is well-motivated. But six reviewer risks threaten acceptance.

- **W1 (confounded comparison).** LUCID differs from ADR in *both* the feedback signal (latent gap vs. return) *and* the controller (PI vs. threshold bound-expansion). Without a {return, raw gap, latent gap} × {threshold-expansion, PI} factorization, the paper cannot attribute its gains. OpenAI's ADR (Akkaya et al. 2019) is a per-boundary threshold-expansion mechanism, while LUCID is a set-point regulator — two orthogonal design axes are being changed at once.
- **W2 (missing mixed-training baseline).** Fixed-DR is an expert *schedule*, not "full ranges from step 0." DORAEMON (Tiboni et al., ICLR 2024, arXiv:2311.01885) reports that a curriculum can beat sampling from the max-entropy distribution directly, but reviewers will still demand the uniform-wide-DR-from-start baseline explicitly.
- **W3 (single global λ).** The paper's own narrative says latency is uniquely destabilizing, yet one scalar scales all channels uniformly. Also, uniform sampling inside [φ0 ± λΔ] shifts probability mass *off* nominal as λ grows: the support expands but the *shape* of the difficulty distribution is uncontrolled and nominal configs get progressively under-sampled.
- **W4 (evaluation is three point-presets).** No robustness profile, no per-channel stress decomposition, no retention/forgetting curve, no training-dynamics figure, no sample-efficiency comparison, no early-warning analysis, no IQM + bootstrap CIs, and only 15 real-robot trials.
- **W5 (missing ablations).** Quantile p, Δ_target = μ+3σ, PI gains/α, return guard on/off, encoder choice, window H/stride s, epoch length, and "latent gap as an auxiliary reward" (to prove *scheduling* is the active ingredient).
- **W6 (metric circularity).** δ uses the same frozen encoder for training and evaluation. Needs an encoder-independent corroborator: tracking error, action smoothness/jerk (Christmann et al., IROS 2024, arXiv:2410.16632), and fall rate.

## 2. Recommended primary extension(s)

**LUCID-MC (multi-channel latent-gap PI with probe environments) as the headline new contribution**, with **LUCID-Replay (prioritized replay of DR parameter vectors) as a secondary contribution that doubles as an ablation.**

Novelty evidence: prioritized/regret-based sampling of DR dynamics parameters already exists (PLR, Jiang et al. ICML 2021; Replay-Guided AED, NeurIPS 2021, which frames DR as "a degenerate case of a random level generator without a curator"; RGDR 2025; Active DR, Mehta et al. CoRL 2019; DORAEMON ICLR 2024). By contrast, **per-channel latent-gap PI with dedicated single-channel probe environments** for unconfounded per-channel attribution is genuinely new.

### 2.1 LUCID-MC (primary)

Partition DR channels into C groups (suggested C = 5): dynamics; init-state; obs-noise; pushes; delay (0–40 ms). Maintain per-group λ_c ∈ [0,1].

**Probe-env allocation.** Reserve ρ_probe (default 3%, range 2–5%) of envs, split evenly across groups. In a probe env for group c, only group-c channels are randomized at λ_c; all others nominal. Yields an unconfounded per-channel latent gap Δ_k^c = 0.9-quantile of δ_t over probe envs of group c during epoch k. No extra rollout cost.

**Per-channel PI (one loop per group).**
```
for each group c:
    e_k^c  = Δ_target^c − Δ_k^c
    I_k^c  = clip(I_{k-1}^c + e_k^c, −I_max, I_max)
    u_k^c  = Kp · e_k^c + Ki · I_k^c
    λ_c    = clip(λ_c + clip(u_k^c, −α, +α), 0, 1)
```
Defaults: Kp = 0.5, Ki = 0.1, α = 0.05/epoch, I_max = 1.0. Δ_target^c = μ_nom^c + 3σ_nom^c from nominal probe rollouts. Return guard per group: if mean epoch return < R_min for 2 consecutive epochs, reset I_k^c and decay λ_c ← 0.8·λ_c. Compute overhead < 2%.

### 2.2 LUCID-Replay (secondary / ablation)

Buffer B (N = 2048) of DR parameter vectors φ tagged with episode-level latent gap, outcome, staleness. Fraction ρ = 0.25 of episodes draw φ from B; sampling P(φ) ∝ rank(g(φ))^(1/β) · (1 + η·c(φ)), β = 0.5, η = 0.1; exclude fallen φ above a gap ceiling. Must be contrasted with RGDR, ADR, and Replay-Guided AED.

## 3. Baseline and ablation matrix

Each run = 3e7 steps × 5 seeds (placeholder 8 GPU-h/seed; calibrate against measured throughput).

| # | Condition | Purpose | Priority |
|---|---|---|---|
| B1 | Full-range DR from start | W2 mixed baseline | Essential |
| B2 | Full-range DR + linear warm-up | W2 variant | Nice |
| B3 | Fixed-DR expert schedule | existing | Essential |
| B4 | ADR (return-driven) | existing | Essential |
| B5 | ADR driven by latent gap | W1 signal isolation | Essential |
| B6 | PI driven by return | W1 controller isolation | Essential |
| B7 | PI driven by raw joint mismatch | existing | Essential |
| B8 | LUCID (global λ) | existing headline | Essential |
| P1 | LUCID-MC | primary new | Essential |
| P2 | LUCID-Replay | secondary new | Essential |
| P3 | LUCID-MC + Replay | combined | Nice |
| A1 | LUCID + shaped (Beta) intensity sampling | W3 | Nice |
| A2 | LUCID + finish-on-target phase | close gap to mixed | Essential |
| A3 | Gap-as-auxiliary-reward (no scheduling) | prove scheduling matters | Essential |
| A4 | Encoder ablation (VAE/PCA/random-proj/contrastive) | W6/W5 | Essential |
| A5 | Window H / stride s sweep | W5 | Nice |
| A6 | Δ_target 2σ/3σ/4σ | W5 | Nice |
| A7 | Quantile p ∈ {0.75, 0.9, 0.95} | W5 | Nice |
| A8 | PI gain sensitivity | W5 | Nice |
| A9 | Return guard on/off | W5 | Essential |
| A10 | Plasticity mitigation (CBP / L2-init) | W7 | Nice |

Essential ≈ 13 cells ≈ 520 GPU-h; full ≈ 1400 GPU-h.

## 4. Evaluation protocol (E1–E9)

- **E1 Robustness profile.** SR and δ̄ vs. global intensity s ∈ {0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5} (>1.0 = OOD extrapolation); mean + 95% bootstrap CI over 5 seeds × ≥200 episodes/bin. Report normalized AUC and worst-bin SR.
- **E2 Per-channel stress.** Each channel individually at {1.0×, 1.5×, 2.0×}; latency sweep 0–100 ms in 10 ms steps.
- **E3 Retention/forgetting.** ID-Clean and OOD-Heavy SR every K epochs during training.
- **E4 Training dynamics.** λ_k (per-channel for MC) vs. epoch with seed spread; guard triggers, collapse counts.
- **E5 Early-warning lead-time.** Lead time between latent-gap threshold crossing and return drop; ROC-like comparison of latent gap vs raw mismatch vs return.
- **E6 Sample efficiency.** Env-steps to SR ≥ X under OOD-Heavy.
- **E7 Statistical reporting.** rliable: IQM + stratified bootstrap CIs (2000 resamples), performance profiles, probability of improvement.
- **E8 Real robot.** ≥10 motions × ≥5 trials; Wilson CIs; MPJPE, action jerk, fall count. MuJoCo sim-to-sim ≥100 ep/motion.
- **E9 Ablation table** (A4–A9) with IQM.

## 5. Figure and table plan

Fig 1 method schematic; Fig 2 robustness profile; Fig 3 per-channel stress heatmap + latency sweep; Fig 4 early-warning lead-time; Fig 5 training dynamics; Fig 6 retention curves; Fig 7 rliable panel; Fig 8 real robot. Tables: DR channels; main sim results (IQM+CI); 2×2 signal×controller factorization; sim-to-sim/real with CIs; ablations.

## 6. Prioritized 4–6 week execution schedule

- **Week 1 (de-risk core claim).** B1, B8, P1, and the 2×2 factorization (B4–B7). Decision D1: does LUCID-MC beat both LUCID and full-range DR on OOD/Latency with non-overlapping IQM CIs?
- **Week 2.** P2, P3, A2, A3, A9. Decision D2: if LUCID-Replay does not beat LUCID by ≥3 SR points, demote it to an ablation.
- **Week 3.** Encoder ablations A4 + A5; build E1–E3 sweeps.
- **Week 4.** Real-robot campaign; MuJoCo ≥100 ep/motion.
- **Week 5.** rliable aggregation, figures, E5.
- **Week 6.** Writing, buffer.

## 7. Suggested paper framing changes

Title: "LUCID-MC: Per-Channel Latent-Gap Curricula for Informed Domain Randomization in Humanoid Control."

Contributions: (1) latent-gap signal that provably rises before return collapses (E5); (2) per-channel PI curricula with cheap probe-env attribution; (3) rigorous evaluation protocol.

Negative-result presentation: if full-range DR matches LUCID asymptotically, reframe as sample efficiency + collapse avoidance + latency extrapolation. If Replay underperforms, present as evidence that intensity scheduling, not replay, is the active ingredient. If plasticity check shows dormant-neuron growth, cite Dohare et al. Nature 2024 and add continual backprop.

Related work to add: DORAEMON (arXiv:2311.01885); OpenAI ADR (arXiv:1910.07113); PLR (arXiv:2010.03934); Replay-Guided AED (arXiv:2110.02439); SAMPLR (arXiv:2207.05219); Active DR (arXiv:1904.04762); GACL (arXiv:2508.02988); CURROT / SPDL (arXiv:2004.11812); rliable; Christmann et al. IROS 2024 (arXiv:2410.16632); Dohare et al. Nature 2024; BeyondMimic (arXiv:2508.08241); ASAP (arXiv:2502.01143).

### Bottom line
Make LUCID-MC the headline, keep LUCID-Replay as secondary with a pre-committed fallback to demotion, run the 2×2 signal×controller factorization and the full-range-DR baseline to kill W1/W2, and rebuild evaluation around robustness profiles, per-channel stress, early-warning lead-time, retention curves, rliable aggregation, and ≥50 real-robot trials.
