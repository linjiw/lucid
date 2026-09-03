# LUCID research and experiment plan — 2026-09-01

Status snapshot: 2026-09-01 15:30 EDT. Companion to `lucid-latest-report.md`
(results ledger), `lucid-handoff-2026-09-01.md` (operational state), and
`site/lucid-paper.html` (the "Difficulty Evacuation" working draft). This file
is the forward plan: what we now believe, what the feedback-driven curriculum
idea can still buy, and the ordered experiments that decide it.

## 1. Where the program stands

### 1.1 Live state

- Ratchet seed 8602 is at ~7,400/8,000 iterations (driver PID 221231, trainer
  PID 411845). The four new 14-cell ladders and the 84-cell H_R2 analysis land
  about 16:05 EDT. Read out with `tools/hr2_readout.sh` only; do not touch the
  worktree at `~/lucid-ratchet-confirm` (commit `ca057e6`).
- Nothing else is on the GPU. Development SONIC HEAD is `1c947d2` on
  `research/practice-utility`; it is not the live worktree.

### 1.2 What the ne1024 campaign established

Single clip (`m1_hob002`), 1,024 envs, 8,000 PPO iterations, 512-alias physics
panel, evaluator byte-pinned. Seeds 8600–8602.

| Finding | Evidence | Grade |
|---|---|---|
| Unconstrained latent-gap PI controller evacuates difficulty | 2 of 6 cells end at λ=0.062 and λ=0.012 after holding λ=1.0 for thousands of iterations; all 6 moved down at some point; zero guard trips | Established (mechanism) |
| Evacuation costs frontier robustness | s4_rg s8600: 0.777 at the h6000 capsule vs 0.697 at final (−7.97 pts frontier AUC) | One run; P3 (lucid_rg s8601) is the out-of-sample test |
| Training return is an inverted monitor | Two collapsed arms carry the two highest terminal returns; the ratchet carries the lowest return and highest frontier AUC | 3 scored pairs; suggestive |
| Monotone ratchet deletes the failure by construction | 0 of 3 ratchet cells move down; 951/453/352+ decrease requests refused | Established |
| Ratchet ≡ fixed distributionally | Exactly one distinct applied λ (=1.0) over iterations 101–8000; identical training distribution for 98.75% of training | Established arithmetically |
| The +3.1-pt ratchet-minus-fixed gap is seed noise | Equals the full range of the four-arm identical-exposure cluster (SD 1.57 pts) | Established |
| Exposure "law" R²=0.988 is a two-support artifact | Five non-stratified points alone reproduce the replicate noise floor; recency not identified (boxcar beats exponential out of sample) | Established; see prereg |
| Frontier endpoint phys_125/150 is contaminated for any arm trained at λ=1.5 | phys_150 training box is bit-identical to the arm's own training marginal; 50% of endpoint weight | Established; fixed in grid-v2 prereg |
| In-envelope (λ≤1) is saturated for every DR arm | fixed reads 0.9988 on phys_000–100; even `off` reads 0.981 | Established |

### 1.3 New zero-GPU finding today: the gap is unanchored, survival is not

Observer telemetry exists for every arm, including fixed. At constant λ=1.0,
across fixed seeds 8600/8601/8602 and ratchet seeds 8600/8601, the latent-gap
p90 wanders between roughly 0.20 and 0.95 with no monotone relation to training
progress (e.g. fixed s8602: 0.60 → 0.88 → 0.23 → 0.95 → 0.24 at iterations
500/2000/4000/6000/8000). Over the same runs the episode time-out (survival)
rate rises monotonically from <0.02 to ≈0.95 by iteration 5,000–6,000 and stays
there. Approximate values were read from the training logs at proportional
line positions; exact per-iteration series should be extracted before
publication.

Three consequences:

1. The latent gap fails the anchoring requirement independently of the
   controller: it is not a function of competence even when difficulty is held
   fixed. It is also measured on a single tracked environment, versus a
   1,024-env population for survival.
2. Fixed DR at λ=1 has the task effectively solved for the last ~2,500–3,000
   iterations. That is unused training budget, and it is the concrete argument
   for expanding support past λ=1 rather than modulating within it.
3. Survival is anchored but still difficulty-relative: the collapsed lucid_rg
   s8601 reaches time-out 0.988, higher than fixed's 0.965, because it made its
   own exam easier. Survival is safe as a gate signal only under a monotone
   actuator and only when measured at the candidate difficulty, never the
   current one.

### 1.4 The diagnosis in one paragraph

Within a fixed box [0,1], a feedback curriculum has nothing to buy: fixed DR
reaches the top of the box immediately, saturates in-envelope, and scores ~0.90
frontier AUC. The only observed effect of feedback there is harm (evacuation).
Both the original LUCID signal (latent gap) and actuator (bidirectional λ) are
disqualified on this task. Feedback can still earn its place in exactly the
regimes where fixed DR is not trivially optimal: deciding *when* it is safe to
widen support beyond the nominal box, deciding *where* within a wide support
to spend samples, and handling per-motion difficulty heterogeneity. That is
the reframe for LUCID v2.

## 2. LUCID v2: the method contract

Every design choice below is forced by a measured failure in v1.

| Principle | v1 failure it answers |
|---|---|
| **M1. Monotone support.** Applied support never contracts by controller request. The return guard remains as an emergency brake only, and any applied decrease is logged and reported as an incident, not as adaptation. | 2/6 evacuations, 6/6 downward moves |
| **M2. Expand, don't replace.** Base strata (nominal through current frontier) are retained at a floor share; new difficulty is added as a stratum. | Exposure scored below own mid-training capsule; forgetting is the cost of evacuation |
| **M3. Probe-gated expansion.** A small probe stratum runs at the *candidate* next support level. Expansion fires only when the probe's survival rate clears a threshold over a trailing window. The signal is measured where we want to go, not where we are. | Gap and return both improve when difficulty falls; any signal measured at the current distribution has that fixed point |
| **M4. Signal admissibility.** A gate signal must be (a) anchored: monotone in competence at fixed difficulty, verified offline on existing telemetry; (b) population-wide, not single-env; (c) bounded and outcome-defined, not a learned statistic with a drifting reference. Episode time-out rate passes all three; latent gap fails (a) and (b); return fails (c) under a bidirectional actuator. | Latent gap p90 drift at fixed λ=1 |
| **M5. Open-loop matched control.** Any feedback arm is compared against an open-loop schedule with the same stratum structure and the same terminal support. Feedback is credited only if it beats that ramp. | Ratchet ≡ fixed; noninferiority to fixed was tautological |
| **M6. Support-stated endpoints.** The primary endpoint lies strictly outside the training support of every arm compared. Cells inside any arm's support are reported, labelled, and never gated on. | phys_125/150 contamination at λ=1.5 |
| **M7. Applied-support log is a first-class artifact.** Per-iteration stratum λ's, sizes, probe survival, and every refused decrease are recorded and plotted in every report. | Collapse was invisible to return |

Not in v2: per-channel λ (kept scalar for the screen; realized per-channel
ranges are logged so a per-channel follow-up is possible), competence latch
(code-complete, default off, excluded), per-stratum advantage normalization and
critic DR-context (Tier 3, gated on Phase 2 evidence of optimizer interference).

## 3. Experiment plan

Costs on the single RTX 5080 (16 GB): one 1,024-env × 8,000-iteration training
cell ≈ 5.4 GPU-h (19,239–20,075 s observed); one 512-episode evaluation cell
≈ 33 s wall (14-cell ladder ≈ 8 min; 42-cell bridge ≈ 23 min). Everything is
serial. Training dominates, so the plan front-loads evaluation-only work.

### Phase 0 — close the current chain (today/tomorrow, ≈1.5 GPU-h, all eval-only)

Ordered by information per GPU-minute. Items 0.1–0.2 are already preregistered
and must run before any evaluator change (the instrument is byte-pinned at
`308e2415`).

| # | Item | GPU | Decides |
|---|---|---|---|
| 0.1 | Read out H_R2 with `tools/hr2_readout.sh`; score P1 (near-certain pass) and P2 (determinism, expect exactly 0.000000) | 0 | Closes Tier 1. Pass authorizes only "stable/noninferior safety constraint" |
| 0.2 | Build the four-file additive bridge worktree from `ca057e6`, freeze the bridge prereg, run the 42-cell historical bridge; score **P3** = frontier AUC of lucid_rg s8601 | ≈25 min | Exposure framing: ≥0.882 means evacuation is free and the paper's framing is wrong; <0.674 means it costs more than any fitted law; >0.776 rejects recency; [0.761, 0.776] discriminates nothing |
| 0.3 | Retention curves: export capsules h4000/h6000 of lucid_rg s8601 and s4_rg s8600 (collapsed) and fixed s8600/s8601 (controls) via `branch_capsule.export_sonic_checkpoint`; score each on the four frontier cells | ≈20 min | Forgetting rate after evacuation vs stable arms; the only way to identify a recency term |
| 0.4 | Complete the return-inversion figure: score the three unscored finals (lucid_rg s8602, s4_rg s8601, s4_rg s8602) on the four frontier cells; add the three new H_R2 arms | ≈7 min | Figure 3 goes from 3 pairs to 11 |
| 0.5 | Held-out motion panels: build k128 alias panels for `m1_hob003`, `m1_ffloop`, `m1_fwd003`; score fixed s8600, ratchet s8600, s4_rg s8600 final, off s8600 at phys_100/150/200 | ≈20 min | First motion-generalization evidence at the frontier; a reviewer will ask |
| 0.6 | Signal audit figure from existing telemetry (no GPU): latent p90, time-out rate, and return vs iteration at fixed λ=1 for all fixed/ratchet arms; exact series from `observer_*.jsonl` and the training logs | 0 | Establishes M4 empirically |

Decision at end of Phase 0: freeze the "Difficulty Evacuation" paper (Section
5). Phase 2 proceeds regardless of P3's value; P3 changes the framing, not the
next experiment.

### Phase 1 — code prerequisites (CPU only, in parallel with Phase 0)

All on a branch the live confirmation worktree never sees; none may land in
`~/lucid-ratchet-confirm`. Each with focused tests per `AGENTS.md`.

| # | Change | Why | Blocking for |
|---|---|---|---|
| C1 | `run_curriculum_robustness_eval.py`: assert requested latency steps ≤ `--max-delay`; require ≥24 for lat_80/100/120 | Silent truncation would collapse three cells into one 60 ms cell | Any v2 latency cell |
| C2 | `analyze_support_screen.py`: `HELD_OUT_GRID` = {phys_175, phys_200}, weights 0.5/0.5, threshold +0.05; label phys_125/150 IN-SUPPORT for 1.5 arms | Grid-v2 prereg | Phase 2 prereg |
| C3 | `run_curriculum_comparison.py`: re-gate the delay-buffer check on the effective λ ceiling, not `mode in ARM_FIXED_LAMBDA` | A ratchet-150 at `--max-delay 8` would silently train latency at 1.0× | Any controller arm above 1.0 |
| C4 | Plumb `lambda_max` through `PIConfig`, `dr_curriculum`, `dr_scaling` for controller modes; refuse extrapolation unless `monotonic=true` | Three-layer hard cap at 1.0 today | gate_150 |
| C5 | Per-stratum termination telemetry: time-out and terminated counts per cohort per iteration → JSONL fields `stratum_timeout_rate`, `stratum_terminated_rate`, `probe_timeout_rate` | No timeout-rate signal exists anywhere in the code | gate_150, M7 |
| C6 | Probe stratum + survival gate: `signal="survival"`, threshold τ with dwell/hysteresis, step Δλ=0.125, monotone by construction; probe stratum runs at λ_F+Δλ | M3 | gate_150 |
| C7 | Open-loop `ramp_150` arm: reuse `yoked` mode to replay a synthetic linear λ_F schedule with the same stratum structure | M5 | Phase 2 |
| C8 | Evaluator instrument v2: persist per-episode time-out flag and termination step so first-termination-masked error and survival curves become computable | Tracking-quality metrics are contaminated and unrecoverable offline today | Tier 4; keep v1 for cross-comparison |
| C9 | Phase 2 preregistration (Section 3, Phase 2 decision rules), frozen with its SHA before launch | Discipline | Phase 2 launch |

### Phase 2 — one-seed screen: does feedback earn its place above λ=1? (≈27 GPU-h, ≈1.2 days)

Seed 8600, `m1_hob002`, 1,024 envs × 8,000 iterations, all arms capped at
λ_max=1.5 so {phys_175, phys_200} stays held out for every arm.

| Arm | Structure | Role |
|---|---|---|
| `fixed` (fresh) | λ=1.0 from step 0 | Fresh comparator under the new code; also a code-identity check against historical fixed s8600 (0.905), expected within seed noise |
| `fixed_150` | λ=1.5 from step 0, single stratum | Gate A: direct mixed training. If this alone works, curriculum need at 1.5 is not established |
| `fixed_u150` | 75% at 1.5 + 25% uniform tail, from step 0 | Expand-don't-replace without scheduling (M2 alone) |
| `ramp_150` | fixed_u structure; λ_F rises linearly 1.0→1.5 over iterations 1,000→5,000, open loop | M5 control: scheduling without feedback |
| `gate_150` | fixed_u structure + 12.5% probe stratum at λ_F+0.125; λ_F steps up by 0.125 when probe survival ≥ τ over a 200-iteration window; monotone; guard logged as incident | LUCID v2 |

Run order: gate_150, ramp_150, fixed_150, fixed_u150, fixed. The feedback arm
goes first so its mechanism telemetry is inspected earliest; if it stalls or
misbehaves, the remaining arms still answer the width question.

Endpoints (from the grid-v2 prereg, all frozen before launch):

- Primary: mean success on {phys_175, phys_200}. Noise cluster SD 0.022 on
  this band, so the decision threshold is +0.05 (≈2.3 SD).
- Companion: held-out progress rate ≥ comparator − 0.02.
- Same-support safety: phys_000–100 AUC ≥ comparator − 0.01 (one-sided; can
  only falsify "no nominal price").
- Manipulation check: fixed_150 must beat fixed at phys_150 (its own training
  marginal) or the arm is void.
- Report only: phys_125/150 labelled IN-SUPPORT; lat_60ms as a floor.

Decision rules:

1. **Width question.** If fixed_150 ≥ fixed + 0.05 on the primary with no
   same-support loss, direct mixed training at 1.5 works. The scientific
   question moves to λ_max=2.0 (grid-v2 endpoint phys_225–300), where direct
   mixed training is more likely to fail.
2. **Feedback question.** gate_150 is credited only if gate_150 ≥ ramp_150 +
   0.05 on the primary AND gate_150 ≥ fixed_150 − 0.02. Otherwise the
   recommendation is the open-loop ramp (or fixed_150), and the LUCID v2
   feedback claim is dropped.
3. **Mechanism gates for gate_150** (H_R0 analogue): zero applied decreases;
   probe telemetry present every iteration; λ_F reaches 1.5 by iteration
   6,000. A stall is a reportable result, not a failure of the screen.
4. **Mixture question.** fixed_u150 vs fixed_150 within ±0.02 means the tail
   costs nothing; fixed_u150 worse by >0.02 with fixed_150 clean is the only
   trigger for Tier 3 (optimizer interference).

Frozen qualitative predictions (to be written into C9 before launch): the
exposure dose model does not extend above λ≈1.385 because static friction
clamps, so only orderings are predicted. Expected: fixed_150 > fixed on the
primary (manipulation check), gate_150 reaches 1.5 before iteration 6,000
given that survival at λ=1 saturates near 5,000, and ramp_150 ≈ gate_150 is
the null.

### Phase 3 — multi-seed confirmation (≈22–43 GPU-h)

Winner vs its decisive control on seeds 8601 and 8602 (4 cells ≈ 22 GPU-h),
then seeds 8603 and 8604 (4 more cells) if the direction holds. Five seeds is
the confirmatory grade the 08-28 guidance set; three seeds stays labelled
screening. Same frozen endpoints; component-wise agreement across seeds
required for directional language.

### Phase 4 — motion generalization (≈33 GPU-h, new campaign generation)

Everything so far is memorized-motion-under-fresh-physics. Train on `train016`
(16 clips) with fixed vs the Phase-3 winner, 3 seeds; evaluate on (a) the
in-pool k128 panels for fresh-physics robustness and (b) held-out clips from
`train064` minus `train016` for motion generalization, on the held-out physics
band. Throughput at 16 motions needs a VRAM-ladder check first
(`run_vram_ladder.py` has used `train016`). If per-motion difficulty is
heterogeneous, the probe stratum becomes per-motion; that is the natural
extension of M3 and the first place a scalar λ is clearly the wrong
abstraction.

### Phase 5 — contingent (Tier 3)

Only if Phase 2 rule 4 fires: per-stratum advantage normalization, then
critic-only DR-context conditioning. If pure fixed_150 wins cleanly, confirm
width across seeds before adding optimizer complexity.

### Parked

- The queued PLR 2×2 (`lucid_plr_signal_ne1024_20260830`, 12 cells ≈ 65 GPU-h)
  is parked. Its signal factor is moot after the gap finding, and prioritized
  sampling over strata is better tested inside the Phase 2 stratum structure.
- A "fixed + warm-up" control arm: already settled arithmetically, do not run.
- Hardware: no G1 run until Phase 3 has a multi-seed winner.

## 4. Evaluation and claim-boundary upgrades (Tier 4 v2)

1. Primary endpoint strictly outside every arm's training support; training
   support stated next to every evaluation range in every table (M6).
2. Instrument v2 (C8): per-episode time-out and termination step → survival
   curves, restricted-mean failure time, first-termination-masked tracking
   error. Publish survival tables from existing arrays now; masked error only
   for new cells.
3. Held-out motion panels (Phase 0.5) as a standing part of the panel.
4. Worst-cell success reported alongside AUC; never a single mean.
5. Latency ladder 80/100/120 ms after C1; lat_60ms kept only as a floor.
6. ≥3 seeds for screening, 5 for confirmatory; seed SD ≈1.6 pts (4-cell AUC)
   and ≈2.2 pts (2-cell band) drive thresholds.
7. Applied-support log and refused-decrease count in every report (M7).
8. A headless rendering path for qualitative extrapolated-physics clips is
   desirable for reviewers but low priority; schedule after Phase 2.

## 5. Paper strategy

**Paper A — "Difficulty Evacuation" (freeze after Phase 0).** A failure-mode
paper with a clean mechanism, a measured cost, an inverted monitor, a one-line
fix with an honestly small claim, and the endpoint-contamination finding. Phase
0 adds the four things reviewers will ask for: P3 out of sample, retention
curves, an 11-pair return figure, and held-out-motion evidence. The signal
audit (0.6) becomes the figure that shows the gap is unanchored independent of
the controller. Three transferable claims stay as written: monotonicity over
stability, signal admissibility, support-stated endpoints.

**Paper B — LUCID v2 (contingent on Phase 2/3).** Feedback-gated monotone
support expansion. It exists only if gate_150 beats the open-loop ramp on a
held-out band across seeds. If width alone wins (fixed_150 ≈ ramp ≈ gate), the
result is still publishable as "support width, not scheduling, is what
matters," folded into Paper A's discussion rather than a separate method paper.

## 6. Risks

- Single GPU makes everything serial: Phase 2 ≈ 1.2 days, Phase 3 ≈ 1–2 days,
  Phase 4 ≈ 1.5 days plus throughput unknowns.
- Above λ≈1.385 the ladder tests grip, mass and push rather than slip; a
  λ=1.5 training arm may be degenerate on friction. The manipulation check
  (fixed_150 at phys_150) catches an inert arm.
- A 128-env probe stratum gives noisy survival estimates; the 200-iteration
  window and dwell are there for that, and the gate may stall. A stall is
  reported, and ramp_150 still answers the width question.
- Effects of ~3–5 pts against seed SD of 1.6–2.2 pts: one seed screens, it
  does not decide. Do not read Phase 2 as a result.
- Any edit to `dr_curriculum.py` or `dr_controller.py` before the live H_R2
  chain finishes aborts it (hash assertions at every boundary).

## 7. Immediate next actions

1. ~16:05 EDT: `tools/hr2_readout.sh`; record verdict in `lucid-latest-report.md`.
2. Phase 0.2 (bridge worktree, prereg, 42 cells) then 0.3–0.5 in one serial eval queue.
3. Phase 0.6 signal-audit extraction on CPU while the queue runs.
4. C1–C7 on `research/practice-utility` with tests; C9 prereg frozen; launch Phase 2 with gate_150 first.

## 8. Addendum 2026-09-02 — competence-grounded, per-channel expansion

Direction set 2026-09-02 (see the proposal text in the session): move from a
scalar λ toward asymmetric, competence-grounded active support expansion;
single-seed quick train/compare/analyze loops at this stage.

### 8.1 How the proposal maps onto what is built and measured

| Proposal element | Status | Where |
|---|---|---|
| Un-invertible competence metric (NPT, foot slip under load, actuator work margin) | **Measured offline, zero GPU.** Foot slip is the only body signal that responds to difficulty on every frozen policy (ρ=+1.00 vs λ on 14/14 ladders, −0.96..−1.00 vs success per arm) *and* to the actuator in both collapses (r≈+0.7 vs ≈0 for the latent gap). It is weakly anchored at fixed λ (ρ −0.53, 17 reversals) and it improves when λ is cut, so it rewards evacuation exactly as return does: admissible only under a monotone actuator at the probe. Torque saturation and undesired contact flip sign across arms; energy and action rate *rise* with competence (activity, not competence). Nothing beats time-out on anchoring. NPT is not logged per episode in training; time-out is its coarse proxy. | `tools/physical_signal_audit.py`, `receipts/analysis/lucid_physical_signal_audit_20260902.json` |
| Asymmetric box actuator (per-channel frontier) | **Built and tested, not yet trained.** `box_gate.py` + curriculum mode `box` + arm `box_150`. One 128-env probe visits channels in rotation; per-channel `SurvivalGateController`s on a shared clock; blocked channels retried next round; `channel_budget` timeout. Same 1.5 ceiling per channel as gate_150. | SONIC `eac9455` |
| Dual buffer: zero-gradient probes | Not built. The probe stratum trains (12.5% of the batch at the candidate level); that *is* the expansion. A `probe_grad=off` ablation would need PPO sample masking. Parked. | — |
| Exposure matrix (training support vs evaluation cells) | Already the M6 discipline; the channel cells make it per channel. | evaluator presets `ch_*` |
| Paired within-seed deltas | Already the reporting convention. | — |
| Failure-mode taxonomy | Blocked on instrument v2 (C8: per-episode termination step). | — |

### 8.2 The measurement that decides whether the box is worth training

Single-channel attribution sweep (`tools/run_channel_sweep.sh`): five seed-8600
finals × eleven cells that widen one term with the other four at λ=1 and
latency pinned to zero. Read out with `tools/analyze_channel_sweep.py`.

Decision: if one channel carries the scalar drop (anisotropic), the box is the
right actuator and box_150 runs in the prototype loop. If every single-channel
marginal is nearly free and the scalar ladder still drops, the failure surface
is an *interaction* (corner) effect — no axis-aligned probe sees it, and the
right probe is the joint corner, which is what the scalar gate already tests.
Either way the prototype loop runs both; the sweep decides the narrative and
which one gets the from-scratch cell.

### 8.3 The fast loop

`tools/run_expansion_prototype.sh`: five widening policies (box_150, gate_150,
ramp_150, fixed_150, fixed) warm-started from the fixed@s8600 final (λ=1
solved, time-out ≈0.95), 2,000 iterations each (~1.3 GPU-h), gate window
100 / dwell 50 / probe budget 300. Scored by
`tools/run_expansion_prototype_scoring.sh` on {phys_175, phys_200} plus the
ten channel marginals. Preregistered:
`receipts/manifests/lucid_expansion_prototype_preregistration_20260902.json`
(R1: box vs gate ±0.03; R3: zero decreases on every channel; R4: a stalled box
is reported as stalled, not as a loss; R5: width-wins rule).

Runs after Phase 2 releases the GPU (~2026-09-03 morning). The from-scratch
Phase 2 cell stays the confirmatory one; the prototype loop ranks designs.

### 8.4 Next design candidates, in order of information per GPU-hour

1. Prototype loop as above (≈6.7 GPU-h, one seed).
2. If the box earns it: `box_asym` — per-channel ceilings set from the sweep
   (cheap channels to 2.0–3.0, friction held at the clamp), which is the first
   arm that can *exceed* fixed_150's support where it is free and withhold it
   where it is not. Its endpoint must then be per-channel (M6).
3. Slip-augmented probe: per-stratum foot slip alongside per-stratum survival
   in `survival_observer.py`, so the probe can be judged on a continuous body
   signal where survival is saturated (in-envelope). Needs per-env telemetry.
4. Zero-gradient probe ablation (`probe_grad=off`), only if the probe's own
   training contribution is suspected of masking the gate's decision.

## 9. Addendum 2026-09-02 (evening) — the question that comes before the scheduler

Direction set by review on 2026-09-02: stop asking whether the training ranges
expand, and ask where extra training produces real improvement.

> Can we improve humanoid control by spending more training on difficult but
> learnable physical conditions, while preserving performance on conditions
> already learned?

### 9.1 Difficulty is not learnability

The attribution sweep says push binds and mass/CoM/joint are nearly free. It
does **not** say practice at push would help. A condition can be hard because
the policy lacks practice, because the observation cannot support the response,
or because the motion is incompatible with that disturbance. Only the first is
repaired by any curriculum. Nothing measured so far separates them, and every
proposed component of the range-expansion curriculum silently assumes the first.

### 9.2 Screen A — the practice-allocation screen (preregistered, ready to run)

Five branches leave the fixed@s8600 final with the same architecture, reward,
motion, 1,024 environments, 1,500 iterations and seed. The only difference is
what a fixed 25% share of the same environments practises, **reallocated** out
of the λ=1 cohort so no branch trains on more episodes.

| branch | the 256-env share trains on | measured origin success there |
|---|---|---|
| `fixed` | nothing (one stratum, all at λ=1) | — |
| `prac_null` | λ=1, like everyone else (matched control) | — |
| `prac_easy` | mass 3×, CoM 3×, joint 3× | 0.949 / 0.988 / 0.990 |
| `prac_push` | push 3× | 0.746 |
| `prac_pushfric` | push 2× with friction 1.5× | 0.912 and 0.973 alone |

Levels are read off the sweep, so "difficult" is a measured success level.
Frozen 13-cell suite, identical for every branch, including ordinary conditions
and two cells above every practised level. Rules R1–R7 frozen before any run;
`prereg: receipts/manifests/lucid_practice_allocation_screen_preregistration_20260902.json`.

**What each outcome ends.** R1: if dedicated practice at the failing push level
does not move push, push failure is not a practice deficit and no allocation
scheduler can fix it — the range-expansion direction loses its justification and
the paper stays a failure analysis. R2: if the placebo branch matches the push
branch on the broad suite, exposure helps wherever it is aimed and channel
selection is unnecessary. R3: if the pair branch does not beat the push branch
above the practised corner, the joint-corner component is dropped.

Cost ≈ 5.6 GPU-h, one seed. Runs when the GPU frees.
`tools/run_practice_allocation_screen.sh --execute` then
`tools/run_practice_allocation_scoring.sh <dir> --execute` then
`tools/analyze_practice_allocation.py`.

### 9.3 Measured 2026-09-02: the progress signal is not available online

Before building an allocator that reads learning progress, we measured whether
that signal exists at the cohort sizes and windows this loop provides.
`tools/progress_signal_audit.py`, receipts
`lucid_progress_signal_audit_20260902.json` and `..._warmstart_20260902.json`.

Method: take the longest window in which the frontier never moved, so every
stratum is a fixed condition; compare the windowed slope of per-stratum survival
against a null that keeps the values and destroys their time order.

| regime | window | change over it | trend / noise at W=100 | sign reliable? |
|---|---|---|---|---|
| from scratch (gate_150, λ held at 1.0) | 3,362 it | +101 to +123 pts | — | yes, at W=200–400 |
| warm start (gate_150, λ held at 1.5) | 1,590 it | −1.2 to +3.6 pts | **0.01–0.08** | **no, at any W ≤ 400** |

On the largest stratum (85 episodes/iteration) the noise floor is 13× the trend
at W=100; matching it needs ~170× the episodes per window, i.e. ~14,000 episodes
per iteration or a ~17,000-iteration window.

**Consequences.**
1. The gate's current cadence (window 100, dwell 50) cannot support a
   progress-based decision on a competent policy. A success-*level* gate still
   can, because a level is estimable from the same samples that a slope is not.
2. Practice effects must be measured end-to-end against frozen evaluation cells,
   which is what Screen A does. This finding raises Screen A's priority; it does
   not weaken it.
3. Design candidate 3 (slip-augmented probe) was promoted to the head of the
   queue on the reasoning that per-step slip yields hundreds of samples per
   episode instead of one bit. **It was then tested and demoted the same day**
   (§9.4).
4. Anything that reads reward progress per bin inherits this floor, including the
   published design in §9.6.

### 9.4 Measured 2026-09-02: slip has the resolution but not the validity

`receipts/analysis/lucid_slip_resolution_audit_20260902.json`, from the existing
channel sweep (5 policies x 16 cells x 512 episodes, seed 8600). Noise handle:
`ch_fric_150` vs `ch_fric_200` differ only in the high bound because the floor
clamps both, so their difference bounds cell noise (success 0.82 pts mean, slip
6.2% mean; contaminated by a real physical difference, so it over-estimates
noise and makes the test conservative).

**Resolution: yes.** In the eight cells where success separates the three healthy
policies by 0.2-2.1x its own noise, slip separates them by 2.2-3.1x its own.

**Validity: no.** Reading a signal at an easy cell to predict success at a harder
one: across all five policies slip does about as well as success (rho 0.70 vs
0.60). Among the three healthy policies, where the extra resolution would
actually be used, slip's ordering is **inverted in all four tests** — it ranks
the least robust of the three first, every time. Low slip is a conservative gait,
not a robust one, which matches the earlier finding that slip improves when
difficulty is cut.

**Consequence.** No online per-condition progress signal is currently available:
episode-end survival is too coarse once the policy is competent (§9.3), and the
one signal with enough samples does not rank competence. Practice effects must be
measured end to end against frozen evaluation cells, which is exactly what Screen
A does. Not powered (3 policies, 1 seed); what a proper test needs is listed in
the receipt.

### 9.6 Related work, checked 2026-09-02

TransCurriculum (IROS 2026, arXiv 2603.14156) schedules a Go1 over a
20×10×20 bin grid spanning command velocity, terrain difficulty and two
randomization parameters (friction, payload mass). A transformer teacher reads
per-bin reward history and predicts reward, success and **learning progress**,
computed as current average reward minus a per-bin EMA; weights expand outward
from bins where the policy already succeeds and are **never contracted**. It
ablates history (transformer vs RNN vs MLP) and dimensionality separately.

So multi-parameter scheduling, learning-history input, progress-driven
allocation and expansion-only support are all published. We claim none of them.
What it does not report, and what our programme is about: **no preset-schedule
baseline reaching the same final ranges**, so whether online decisions beat a
good hand-designed allocation is open; and its progress signal is read from
reward on the bin the curriculum controls, which is the signal our audit ranks
least trustworthy and, under a controller permitted to contract, the one that
drives collapse.

### 9.7 The gate must ask a different question

The built gate asks "can the policy already handle this?" and expands on high
success. A performance-improving curriculum must ask "would practising this
help?" — which is a question about *improvement*, estimated by repeated
evaluation of **unchanged** conditions, never by a score that rose because the
test got easier. Three groups follow: already learned (keep a floor of
practice), difficult and improving (allocate more), repeatedly failing without
improvement (step back and investigate rather than grind). Screen A supplies the
first measurements of that improvement signal; a learned teacher must earn its
complexity against a preset allocation before it is built.

### 9.4 The next hurdle, and what novelty survives

Beating the narrow fixed baseline establishes nothing. The comparators are fixed
randomization over the **wider** target range, a preset expansion schedule, and a
preset **per-parameter** schedule with the same practice mixture. Preset
schedules are built from screen runs and frozen before the confirmation seeds.

Two pieces of prior work bound the claim and are now in Related Work.
TransCurriculum already does history-informed scheduling across task dimensions
with separate history and dimensionality ablations, so "multiple parameters plus
learning history" is not novel by itself. Automatic Domain Randomization already
evaluates per-parameter boundaries and can expand or contract them, so a broad
claim about adaptive randomization needs a faithful performance-driven baseline,
not only the mismatch-driven controller we measured collapsing. What may remain
is narrow and must be demonstrated: **allocation by measured improvement on
fixed conditions, under non-shrinking support.**

### 9.5 Evaluation corrections carried into every future readout

- Name the held-out axis. Our ladder is held-out physics on one trained clip
  plus one nearby clip. It is not motion generalization.
- Once an arm trains or probes at 1.5, phys_125 and phys_150 are inside its
  support. Unseen parameter **values** and unseen **draws** inside a familiar
  range are reported separately and never pooled.
- Report realized exposure per cell per arm, not intended support. Widening a
  uniform range lowers the density at every fixed sub-range, so "still inside
  the range" does not mean "still practised".
- State whether probe episodes contribute to PPO updates, and count their cost
  either way. In Screen A there are no probes: the practice stratum trains, and
  that is the treatment.
- Choose the primary claim in advance: better robustness at equal cost, or a
  fixed robustness target reached at lower cost. Not whichever looks better.
- Five seeds are not automatically enough; the replication needed depends on the
  variability and the effect claimed. Our between-seed effect is 7.8 points.
