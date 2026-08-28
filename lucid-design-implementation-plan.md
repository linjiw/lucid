# LUCID Research Program — Design & Implementation Plan

**Version:** v1 · 2026-08-17
**Inputs reconciled:** `lucid-original-paper.md` (IROS-2026 manuscript, scalar LUCID), `lucid-proposal.md` (Counterfactual Practice Utility over LUCID), `lucid-sonic.md` (SONIC-grounded design, 29 sections)
**Code on disk:** `GR00T-WholeBodyControl/` (SONIC, upstream `c374bae`), `whole_body_tracking/` (BeyondMimic, upstream `cd65172`). Neither contains LUCID code yet.

> **v2 addendum (2026-08-17, after environment setup): Part I below was written assuming a greenfield SONIC.
> It is not greenfield.** The user's main line at `/home/robotixx/GR00T-WholeBodyControl` already carries two
> large research programs (LACE and Track-B/ZPD) plus frozen data artifacts that this program should consume
> rather than rebuild. **Read [Part II](#part-ii--reconciliation-with-existing-work-v2) before acting on
> Part I sections 5, 6, or 10.** Part I's scientific design stands; its build plan is amended there.

---

## 0. Verdict in one paragraph

The three documents describe a single research trajectory: (1) LUCID v1 showed that a *mechanism-level* signal — latent command–execution mismatch — is a better curriculum feedback than episodic outcome; (2) the proposal argues that *any* present-time signal (mismatch, failure, TD error) is a state descriptor, not a measure of the *marginal value of practice*, and proposes measuring that value causally; (3) the SONIC plan grounds this on a released generalist controller whose native failure-based sampler is exactly the hypothesis to audit. I adopt (3) as the primary, claim-bearing program, keep LUCID's latent gap as a first-class *proxy and mechanism diagnostic* (not a scheduler), and keep the BeyondMimic G1 stack as a cheap DR/latency sandbox in which LUCID v1's infrastructure (VAE encoder, FIFO delay, DR presets) is preserved and reused. The program is strictly gated: **no learned scheduler is trained until a paired counterfactual measurement shows difficulty proxies are insufficient.** The best possible early result — "failure rate or latent gap already predicts long-horizon utility" — is a valid paper, not a failure.

---

## 1. Reconciliation of the three inputs

| Topic | Original paper | Proposal | SONIC plan | **Decision** |
|---|---|---|---|---|
| Curriculum knob | Global scalar λ over all DR channels via PI | Residual reweighting over LUCID's ρ_k | Residual reweighting over SONIC's native bin sampler ρ_k(b) | Motion-bin residual on SONIC first; DR-side residual only in the physics extension (§4.10). Scalar λ is not carried forward as a method (repo evidence cited in `lucid-sonic.md` §1.3). |
| Feedback signal | p90 latent gap δ | Multi-horizon counterfactual utility U_H | U_H with exact dose normalisation + harm vector | Adopt SONIC-plan definition (efficacy + harm vector + 3-class label). Latent gap becomes one audited proxy. |
| Context unit | epoch-level DR intensity | x=(m, φ, c) | x=b (50-frame bin) first, then (b,g,s) | x=b first (fewest confounds). |
| Horizons | — | H∈{5,20,100} | H∈{8,32,128} PPO iters, to be re-frozen after throughput pilot | Placeholder {8,32,128}; freeze after Phase-0 pilot in **environment transitions and policy-drift KL**, not iterations. |
| Objective | SR, MPKPE, MPJPE, δ̄ | J_Q = tracking × quality-indicator | Macro-mean quality-qualified success over families + independent quality outcomes | Adopt SONIC-plan §6 (macro-mean over families; frozen thresholds). |
| Contexts per stage | — | 24–32 | 24 stratified | 24, stratified by failure quartile × family × contact regime; 12 confirmed. |
| Baselines | Fixed-DR, ADR, raw-mismatch | +failure/error/LP/PLR samplers | +uniform, failure-calibrated residual, random residual, yoked, oracle | Full SONIC-plan control set (§16). Yoked-schedule and failure-calibrated residual are mandatory. |
| Hardware | 5 motions × 3 trials | larger set, CIs | 20–30 motions × ≥5 reps, Wilson + hierarchical bootstrap, MuJoCo gate first | Adopt SONIC-plan §19. |
| Testbed | BeyondMimic-style G1 in Isaac Lab (Table-I terms are BeyondMimic DR terms) | unspecified | SONIC released ckpt | **Two testbeds** (§3). |

Conflicts I resolved on my own judgment:
- The proposal's `x=(m,φ,c)` from day one is too many confounds for a first causal study; SONIC plan's motion-only stage wins.
- The proposal's `ρ_k` = LUCID's DR distribution assumes scalar LUCID stays; it does not. Base distribution is SONIC native.
- The IROS manuscript's latency emphasis is preserved but deferred to Track 3 (SONIC `level0_4` events have no delay channel; adding one needs an identity test first).

---

## 2. Research goal and claim ladder

**Goal.** Decide *where limited humanoid training budget should be spent* so that deployment robustness (sim-to-sim, sim-to-real, unseen motions and perturbation compositions) improves — and do so with a signal that is causal, not merely a difficulty proxy.

Claim ladder (from `lucid-sonic.md` §26; each level requires its own evidence, and the abstract may not outrun the level reached):

| Level | Claim | Evidence required |
|---|---|---|
| L0 | Reproducible paired branch protocol | no-op parity, resume equivalence, ε=0 identity |
| L1 | Current difficulty (failure, error, latent gap) is not a sufficient predictor of long-horizon practice utility | fresh-seed-confirmed reversals in the phase portrait |
| L2 | Utility is predictable across held-out families / policy stages | leave-one-family/stage-out |
| L3 | Identity-preserving utility residual beats SONIC native sampler at equal compute | native, uniform, random-residual, failure-calibrated, yoked, oracle |
| L4 | Gains transfer to unseen motion content and unseen perturbation compositions | frozen final test |
| L5 | Gains transfer to G1 hardware without clean-quality loss | MuJoCo gate, hardware CIs, independent quality metrics |

---

## 3. Program architecture

### 3.1 Two testbeds, distinct roles

| | **Testbed A — SONIC** (`GR00T-WholeBodyControl`) | **Testbed B — BeyondMimic fork** (`whole_body_tracking`) |
|---|---|---|
| Role | Primary, claim-bearing (L1–L5) | Sandbox: LUCID-v1 infrastructure, DR/latency channels, fast iteration on gap probe & quality metrics |
| Why | Released generalist ckpt; native failure sampler is *the* hypothesis to audit; all-modes controller | LUCID v1 setting (G1, Isaac Lab, 50 Hz, Table-I DR terms incl. FIFO delay); ~10× cheaper per run; single-motion runs |
| What gets built here | SamplerAdapter, BranchCapsule, dose accounting, quality eval, residual allocator | LUCID-v1 port (VAE pretrain, δ_t probe, PI scheduler kept only as a *baseline*), latency FIFO, DR severity cells |
| Constraint | Do **not** modify actor-critic, token/FSQ, PPO objective, rewards | Do **not** let sandbox results appear in claim-bearing tables |

Cross-testbed contract: the frozen temporal-VAE encoder and the quality-metric library are shared Python packages, so δ_t and QSuccess mean the same thing in both.

### 3.2 Four tracks

- **T0 Infrastructure** (weeks 1–3): hooks, capsules, telemetry, quality evaluator, tests. Gate: no-op parity.
- **T1 Measurement** (weeks 4–6): oracle screening + confirmation, phase portrait, proxy audit. Gates A (identifiability) and B (proxy insufficiency). **Scientific decision point.**
- **T2 Method** (weeks 7–10, only if Gate B passes): estimator → residual sampler → equal-compute comparison.
- **T3 Physics & transfer** (weeks 11–14+): (b,g,s) contexts, latency FIFO, held-out compositions, MuJoCo gate, hardware.

---

## 4. Design decisions

### 4.1 Context and base distribution
- `x = b` = native SONIC bin (`adp_samp_bin_size=50` frames ≈ 1 s at 50 Hz). Identity is `ContextKey(motion_hash, bin_index, …)`, never a loader-order integer.
- Base distribution `ρ_k(b)` = live snapshot of `MotionLibBase._sampling_prob` / `_sampling_batch_prob` after `update_adaptive_sampling_probabilities()`; we never re-implement the sampler.

### 4.2 Intervention
- Local kernel: bin `b` ± 1 neighbour, exponential in frame distance within the same clip.
- `ρ_{k,b}^ε = (1−ε)ρ_k + ε κ_b`, ε=0.10 (dose–response pilot at ε∈{0.05,0.10,0.20} before freezing).
- Equal compute: same #env steps, #PPO updates, optimizer, motion pool. Compare intervention vs *continued-training control*, never vs source checkpoint.

### 4.3 Dose
Record realised kernel-weighted exposure per branch: `D_H^a(b)=Σ w_b(x_{e,t})`. Utility is normalised by ΔD, not by nominal εH. Every branch emits a DoseReport (intended vs actual bins, completed steps, KL, entropy, coverage).

### 4.4 Horizons and labels
- Nested {H_s,H_m,H_l} saved from one intervention branch; frozen after pilot.
- Label vector `U = [U_{H_s}, U_{H_m}, U_{H_l}]` for efficacy + harm vector `h = [ΔJ_clean, ΔE_action, ΔE_slip, ΔE_contact, ΔE_sat]` + 3-class {safe-positive, neutral, harmful}.
- Named failure cases to hunt: immediate-only, delayed-useful, reversal-harmful.

### 4.5 Deployment objective
`J_eff = MacroMean_f QSuccess_f` over motion families on a frozen dev suite; QSuccess requires completion ∧ MPJPE≤τ_p ∧ slip≤τ_s ∧ HF-action≤τ_h ∧ contact≤τ_c ∧ saturation≤τ_τ. Thresholds frozen from (1) sim/robot safety limits, (2) nominal SONIC rollouts, (3) pre-registered baseline quantiles. Never retuned per method. Final test suite hashes are inaccessible to label builder, estimator, and HP selection (`test_no_test_leakage.py`).

### 4.6 Proxies recorded per context (before branching)
Native (raw failure count, smoothed rate, sampling prob, staleness); RL (advantage, value loss, TD residual, entropy, KL, grad norm, clip fraction, gradient-alignment estimate `η ĝ_Q·g_x − β‖g_x‖²`); **LUCID** (`q_cmd`/`q_exec` windows, raw mismatch, frozen-VAE latent gap median/p90/slope/variance, contact-conditioned gap); motion structure (root speed, contact transitions, single-support/flight fraction, reference jerk, spectral complexity).

### 4.7 Estimator (gated)
Complexity ladder: constant → failure-monotonic → isotonic → ridge/elastic-net → GBT → small MLP; sequence model only on demonstrated representational bottleneck. Outputs Û_{H_s,m,l}, p̂_harm, bootstrap σ_U. Online score `s = Û_{H_l} − βσ_U`, zero residual mass if p̂_harm>δ. CV: leave-one-family/stage/source-out + fresh seeds.

### 4.8 Residual sampler (gated)
`q_k = (1−α)ρ_k + α·ρ_k exp(s/τ)/Z`, with KL(q‖ρ)≤ε_KL, per-bin/per-motion caps, family coverage floors, small diagnostic mass on harmful bins. Identity: α=0 or constant s ⇒ q=ρ. Dev grid α∈{0.10,0.25}, ε_KL∈{0.02,0.05}; freeze one before main run. Applied at the `ImResampleCallback` integration point; estimator refreshed on a slower cadence; distribution+estimator hashes logged per rollout.

### 4.9 Controls (mandatory)
Native SONIC · uniform · failure-calibrated residual (same α/KL/entropy/floors) · random residual · MPJPE sampler · absolute-learning-progress · PLR-style TD/value-loss · LUCID-gap residual · utility residual · oracle (small pool) · yoked replay of seed A's schedule on seed B.

### 4.10 Physics extension (T3)
Groups g∈{material, mass/CoM, push, reference-noise, latency}, severity s∈{0..3}, one group at a time; branch-level physics config first (SONIC events are `startup`/`reset`/`interval` mode; per-env context-conditioned events only after branch-level effect is shown). Latency via FIFO on the action path in `ManagerEnvWrapper.step`; d∈{0,1,2,3} ↔ {0,20,40,60} ms; d=0 must be trajectory-identical to native. Held-out compositions (latency×low-friction, CoM×push, …). Test additivity `U(b,g,s)` vs `U(b)+U(g,s)`.

---

## 5. Implementation plan (code-level, checked against the repo)

### 5.1 Repository setup
1. Fork both repos; create immutable tags `sonic-audit-base` (=`c374bae`) and `bm-lucid-base` (=`cd65172`). Never track moving `main` during a campaign.
2. New namespaces (no edits to upstream semantics):
   - `GR00T-WholeBodyControl/gear_sonic/research/practice_utility/` — as in `lucid-sonic.md` §7.1 (schema, context_registry, sampler_adapter, intervention, dose_accounting, rng_capsule, branch_capsule, quality_metrics, latent_gap_probe, utility_label, proxy_features, estimator, residual_allocator, audit, reports).
   - `lucid_common/` (new small package, installed into both envs): `temporal_vae/` (encoder, pretrain script, window builder), `quality/` (action/slip/contact/torque metrics), `manifests/` (hashing, split tools).
   - `whole_body_tracking/source/whole_body_tracking/whole_body_tracking/lucid/` — LUCID-v1 port (PI scheduler as baseline, δ_t probe, DR scale hooks, FIFO delay).
3. Pin env: Isaac Lab / Isaac Sim versions per each repo's README; record `pip freeze` and CUDA in `manifests/env_receipt.json`.

### 5.2 SamplerAdapter (SONIC) — hooks into `gear_sonic/utils/motion_lib/motion_lib_base.py`
Verified attributes/methods to wrap (no rewriting):
- `_sampling_prob`, `_sampling_batch_prob`, `_curr_motion_ids`, `sample_motions(n)` (multinomial over `_sampling_batch_prob`).
- Adaptive bins: `init_adaptive_sampling()`, `adp_samp_bins`, `adp_samp_frame_to_bin`, `adp_samp_num_episodes`, `adp_samp_num_failures`, `adp_samp_failure_rate(_raw)`, `adp_samp_failure_rate_max_over_mean`, `uniform_sampling_rate`, `sync_and_compute_adaptive_sampling(accelerator, sync_across_gpus)`, `update_adaptive_sampling_probabilities()`.
Adapter methods: `snapshot_native_distribution()`, `freeze_motion_pool(manifest)`, `set_intervention(ctx, ε, radius)`, `set_residual_distribution(prob, manifest_id)`, `clear_override()`, `get_exact_dose_report()`.
Mechanism: an override tensor consulted inside a thin subclass/monkeypatch of `update_adaptive_sampling_probabilities()`; when override is `None`, byte-identical native path. Bin→frame kernel uses `adp_samp_frame_to_bin` and per-motion frame starts. Dose counters increment where episodes are assigned bins (the same place `adp_samp_num_episodes` is incremented) so control and intervention are counted identically.
Distributed: dose tensors gathered exactly like `adp_samp_stats` in `sync_and_compute_adaptive_sampling`.

### 5.3 BranchCapsule — extends `gear_sonic/trl/callbacks/model_save_callback.py`
`ModelSaveCallback.save_checkpoint(...)` already saves model + `env.get_env_state_dict()`; it does **not** save RNG. Add `PracticeCapsuleCallback` writing `capsule_step_XXXXXX.pt` = {policy, value, optimizer, LR-scheduler, trainer `state`, env state, sampler state (all `adp_samp_*` + `_sampling_prob`), python/numpy/torch-cpu/torch-cuda RNG, context RNG, resolved-config hash, pool manifest hash, dev-suite hash, source commit, sha256}. Loader must restore in this order: RNG → env/sampler → model/optim → trainer state. `local_seed` handling in `ppo_trainer.py` (`torch.manual_seed(args.seed)` then `torch.manual_seed(self.local_seed)`) must be replayed identically on resume.

### 5.4 Counter-based randomness
Keyed generator `ξ = f(pair_id, env_id, episode_index, channel)` for friction/push/action-noise/minibatch-shuffle channels; only the context selector differs between paired branches. Because GPU physics is not bitwise deterministic, we (i) enable deterministic flags where available, (ii) save RNG receipts, (iii) estimate the noise floor from ε=0 branches, (iv) never write "same seed" as "identical trajectory".

### 5.5 Telemetry — `gear_sonic/envs/wrapper/manager_env_wrapper.py::step`
`extras` already carries `env_actions` and `adp_samp/*` stats. Add under `extras["practice"]`: motion_hash, bin_id, `q_cmd` (PD target after action transform), `q_exec` (joint pos), contact mask, applied torque if exposed, termination reason, perturbation fingerprint. Ring buffers of length H·s feed the LUCID gap probe. Keep it off by default (`practice_utility.enabled=false` ⇒ zero-cost path).

### 5.6 Quality evaluator — subclass of `gear_sonic/trl/callbacks/im_eval_callback.py`
`PracticeQualityEvalCallback` keeps upstream outputs (success, MPJPE-L, vel/acc distance) and adds: Δa, Δ²a, HF spectral energy (all/legs/ankles/wrists/torso), foot slip (contact-masked horizontal velocity, per-metre, touchdown, stance), non-foot contact rate, peak/integrated impulse, contact timing error, saturation fraction, RMS torque, energy proxy, joint-limit proximity, episode length, termination reason. Fixed horizon T_eval with early-termination fill (as in LUCID v1: δ_t←2 after fall). Recomputed from state/actions, not from reward terms.

### 5.7 LUCID gap probe (`lucid_common/temporal_vae`)
- Port LUCID-v1: windows (H, s) of joint targets; temporal VAE (β-VAE, Gaussian decoder), noise/transient corruptions during pretraining; frozen `μ_η`; unit-normalised cosine gap δ_t; p90 per epoch.
- Pretraining data: reference joint trajectories from the SONIC motion pool (G1 dof space) and BeyondMimic LAFAN1 — one encoder per dof-space, versioned by hash. Encoder is **frozen before** any branch campaign.
- Probe outputs per (context, checkpoint): median, p90, slope, variance, contact-conditioned gap → `proxy_features`.

### 5.8 Campaign tooling (`scripts/practice_utility/`)
`build_motion_pool.py` (512-clip debug pool, dedup by trajectory hash), `create_probe_manifest.py`, `snapshot_native_sampler.py`, `run_branch.py` (Hydra + `accelerate launch`), `evaluate_branch.py`, `build_utility_labels.py` (parquet), `run_proxy_audit.py` (phase portrait + ranking/calibration tables), later `train_utility_estimator.py`, `run_residual_curriculum.py`, `audit_campaign.py`. Command interface as in `lucid-sonic.md` §23.

### 5.9 Residual allocator (T2, gated)
`ResidualAllocator.compute(ρ, s, α, ε_KL, floors, caps) → q` with a bisection on temperature to satisfy KL; unit-tested identity/KL/coverage. Wired through `ImResampleCallback` mode `residual` (modes: `native | frozen_pool | residual`).

### 5.10 Physics extension & latency (T3)
- SONIC: `gear_sonic/config/manager_env/events/terms/*.yaml` (`physics_material`, `base_com`, `add_joint_default_pos` = startup; `randomize_rigid_body_mass` = reset; `push_robot` = interval). Severity cells as separate frozen Hydra presets; branch-level first.
- Latency: FIFO in `ManagerEnvWrapper.step` before `env.step`; identity test d=0; shift test d=1 = exactly one 20 ms step.
- BeyondMimic sandbox: same FIFO and severity cells ported to `tracking_env_cfg.py` events; used to iterate quickly and to reproduce LUCID-v1's Table-I presets (ID-Clean, OOD-Heavy, Latency-60ms) as *evaluation* presets.

### 5.11 Sim-to-sim & hardware
Use the SONIC MuJoCo bridge (`gear_sonic_deploy/`) for the sim-to-sim gate; check obs/action conventions and clean parity first. Hardware only after clean non-inferiority + sim-to-sim gain + no quality damage + no family regression. Protocol per §4/§19 of the SONIC plan.

### 5.12 Config
`gear_sonic/config/research/practice_utility/{base,oracle_screen,oracle_confirm,residual_train,physics_extension}.yaml`, `config/callbacks/practice_*.yaml`, experiment presets `exp/manager/universal_token/all_modes/sonic_practice_{audit,residual}.yaml`. Every run stores its resolved config hash; `final_test.accessible=false` by default.

### 5.13 Tests (`tests/practice_utility/`)
Unit: sampler (non-neg, sums to 1, ε=0 identity, constant-score identity, KL exact, floors/caps, kernel boundaries); dose (intended vs actual, termination-adjusted, distributed aggregation, no double count); metrics (stationary foot ⇒ 0 slip, known slide ⇒ known slip, sinusoid ⇒ spectral peak, torque at limit ⇒ saturation 1, early-termination fill).
Integration: **no-op parity** (native vs research-enabled, all hooks off: trajectories/rewards/terminations/probs); **resume equivalence** (20 iters vs 10+capsule+10); distributed sampler; ε=0 branch noise floor; latency identity; leakage (final-test hashes absent from labels/estimator/HP artefacts).

---

## 6. Schedule, gates, and compute tiers

| Week | Milestone | Exit gate |
|---|---|---|
| 1 | Fork/tag, install both stacks, released-ckpt eval, throughput profile, env receipt | baseline reproduces; obs/action conventions verified |
| 2 | BranchCapsule, counter RNG, frozen pool, dose counters, resume-equivalence, ε=0 identity | hooks-off == native; branch noise floor measured |
| 3 | Quality evaluator, LUCID VAE encoder frozen, gap probe, 3-stage checkpoint selection (pre-registered progress thresholds), 24-context manifest | metrics interpretable; bad-quality rows cannot be "positive"; final test sealed |
| 4–5 | Oracle screening: 3 stages × 24 ctx × 2 seeds, shared control, nested horizons; labels; phase portrait | **Gate A** identifiability · **Gate B** proxy insufficiency |
| 6 | Scientific decision: A (simple signal suffices → calibration paper) / B (measurement paper) / C (residual authorised) | written decision memo with figures |
| 7–10 | (C only) estimator ladder, uncertainty, residual sampler, all controls, equal-compute comparison, yoked replay | positive paired lower-95% CI on J_eff, clean non-inferiority, no hard-stratum regression |
| 11–14 | Physics groups, severity cells, latency FIFO, held-out compositions, MuJoCo gate | sim-to-sim gain without quality damage |
| final | Hardware (20–30 motions × ≥5 reps, randomised order, Wilson + hierarchical bootstrap) | L5 evidence |

Compute tiers (fill in once GPU budget is known):
- **Tier S (1–2 GPUs):** debug pool 512 clips, 1024–2048 envs, screening with 1 seed + shared control, horizons shortened; claims capped at L1.
- **Tier M (4–8 GPUs):** as planned above; confirmation with 4 fresh seeds and independent controls; L1–L3.
- **Tier L (≥16 GPUs):** full 4096-env confirmation, physics extension, L4–L5.
Cost levers already designed in: shared control for screening, nested horizons, two-stage context count (24→12), estimator gate, hardware gate.

---

## 7. Deliverables

1. **Code:** research namespace + `lucid_common` + BeyondMimic LUCID-v1 port, all behind flags with no-op parity tests.
2. **Artefacts:** frozen manifests (pool, dev suite, final test), capsules, `utility_labels_v*.parquet`, proxy-audit report, phase-portrait figure.
3. **Decision memo (week 6)** choosing outcome A/B/C.
4. **Paper** at the highest honestly reached claim level (titles per outcome: "Difficulty ≠ Practice Utility…" for L1; "Practice What Transfers…" for L3+).
5. **Preserved LUCID-v1 assets:** encoder, δ_t probe, DR presets — reused as proxy/diagnostic and evaluation presets, so the IROS work is not discarded but re-positioned (Outcome B in `lucid-sonic.md` §27 is the best-case landing for the latent gap: a practice-allocation signal rather than a global λ).

---

## 8. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Branch noise ≥ between-context signal (Gate A fails) | ε dose–response pilot; coarser contexts (family-level); paired replicates; report as measurement limit, do not hide with a bigger estimator |
| GPU non-determinism breaks pairing | counter RNG + receipts + ε=0 noise floor; report tolerances |
| Dose swallowed by early termination | termination-adjusted dose; kernel radius 1; monitor ΔD>0 |
| Latent gap improves while reward/episode length worsen (seen in repo evidence) | efficacy + harm vector; QSuccess gating; gap never the sole outcome |
| Overfitting to selected top contexts | screening FDR, fresh-seed confirmation, frozen context set, independent controls |
| Acceleration mistaken for asymptotic gain | report AUC and sufficiently-trained final separately; fixed-wide/native "catch-up" check |
| Sandbox results leak into claims | testbed-B results labelled sandbox; final tables SONIC-only |
| Hardware budget spent on weak sim evidence | MuJoCo gate with four conditions before any G1 trial |

---

## 9. Open questions (answer these to unblock; defaults assumed otherwise)

1. **Compute:** how many GPUs and for how long? (default: plan Tier M, run Tier S first)
2. **Where is the LUCID-v1 code** (VAE, PI scheduler, DR presets)? It is not in `whole_body_tracking/`; the plan assumes a private fork exists and will be ported into `whole_body_tracking/.../lucid/`.
3. **IROS-2026 outcome** for manuscript 1615 — affects whether L1 material is a new paper or a revision.
4. **Hardware access** to Unitree G1 and the SONIC deployment stack — affects when T3 hardware can be scheduled.
5. **Motion data:** is BONES-SEED processed locally (`data/motion_lib_bones_seed/robot_filtered`)?

---

## 10. Immediate next actions (week 1)

```bash
# 1. tag baselines
cd ~/lucid/GR00T-WholeBodyControl && git tag sonic-audit-base c374bae
cd ~/lucid/whole_body_tracking     && git tag bm-lucid-base cd65172

# 2. verify SONIC released checkpoint evaluates (headless, once)
python gear_sonic/eval_agent_trl.py +checkpoint=sonic_release/last.pt +headless=true +run_once=true

# 3. scaffold research namespace + tests (empty modules, no-op parity test first)
mkdir -p gear_sonic/research/practice_utility tests/practice_utility scripts/practice_utility

# 4. throughput profile: 512-clip pool, 1024/2048/4096 envs, iterations/hour → freeze H_s,H_m,H_l
# 5. write manifests/env_receipt.json (pip freeze, CUDA, driver, Isaac versions, git SHAs)
```

First code to land, in order: `schema.py` (ContextKey/BranchCapsule/UtilityRecord) → `sampler_adapter.py` snapshot + override → `test_sampler_identity.py` + no-op parity → capsule save/load + resume-equivalence → dose counters → quality evaluator → VAE pretrain → probe manifest → first ε=0 and ε=0.10 branches on one checkpoint.

---
---

# Part II — Reconciliation with existing work (v2)

**Added 2026-08-17 after environment setup and a full inventory of the machine.** Part I assumed a greenfield SONIC checkout. That assumption was wrong. This part records what already exists, what must not be rebuilt, and how Part I is amended.

## 11. What already exists on this machine

### 11.1 Three working copies, one lineage

| Path | Role | State |
|---|---|---|
| `~/lucid/GR00T-WholeBodyControl` | pristine upstream `c374bae`, tagged `sonic-audit-base` | clean; this program's build base |
| `~/groot-wbc-sonic-sim-trackb` | Track-B / ZPD curriculum sampler | fork `linjiw/groot-wbc-sonic-sim-trackb`, branch `agent/official-bones-zpd-handoff`, older upstream base |
| `~/GR00T-WholeBodyControl` | **main line**, branch `research/cg-wbc-v0-golden-path` | 104 commits ahead of `c374bae`; 524 files / ~120k insertions; superset of Track-B |

### 11.2 LACE — a *different* research program on the same testbed

`~/GR00T-WholeBodyControl/gear_sonic/research/lace/` — 37–38 modules, ~35k lines, **untracked in git** (invisible to `git log`/`git diff`; its 31 test modules *are* committed). Design doc: `0813-design-plan.md` ("LACE × SONIC — Failure Geometry and Training Transfer", v0.3).

LACE's question is **not** ours: *does a frozen, policy-conditioned failure representation predict cross-motion training transfer?* It factorizes failure *type* from failure *frequency* (`a_m = P(fail|m)`, `q_m(c) = P(c | resolved failure, m)`). Ours asks whether extra practice in a context causally improves later deployment.

**Everything upstream of GPU execution is done and SHA-256 frozen. Everything downstream is empty.**

Frozen artifacts under `/data/robotixx/groot-wbc-sonic-research/lace/manifests/` (24 files, 22 MB):
- **Five-way source-group-disjoint splits** at both scales — `D_atlas / D_controller / D_curriculum / D_geometry / D_test`. scale512: 512 motions / 268 source groups (D_curriculum 233). headline: 4950 motions / 487 groups (D_curriculum 1996, D_geometry 822, D_test 569/41 groups, **never opened**). Grouping rule is BONES actor provenance, which prevents performer leakage — exactly the dedup discipline Part I §4.5/§10.2 demands.
- **Reference-length inventories** per partition with per-motion source SHA-256, source FPS, and an exact rational resampling rule (no float rounding). `D_test` inventories deliberately not built.
- **Reference-feasibility covariates** (26-dim kinematic schema: joint velocity/accel quantiles, limit proximity/excess, root speed, foot support/flight fractions, contact transitions, clearance). Explicitly "kinematic proxy, not dynamic feasibility proof". Establishes that SONIC's own `filter_and_copy_bones_data.py` is only a *filename keyword filter*, not a feasibility test.
- **8 representation-blind source panels** frozen from D_curriculum using only provenance + duration, before any rollout was inspected.
- **Equal-KL intervention plan** — per-panel upweighting solved by bisection so every row has identical KL (0.05 nats) from a uniform base, `max_probability_ratio` 3.0, ESS fraction 0.891.
- **856-row probe schedule** with deterministic seed derivation (`sha256_canonical_json_uint32_prefix_v1`) and tie-to-lower quantization.
- **Throughput sweep plan** for SONIC-Lite S at N_env ∈ {128, 256, 512, 1024}.

Artifact directories: `atlases/` holds only synthetic 2-motion contract smokes (`scientific_use: false`); `rollouts/` holds **2 episode rows**; `throughput/` has **zero executed cells**; `checkpoints/` has the released checkpoint plus a Lite-S initialization but **no trained policy**.

**Why it stopped: hardware, not implementation.** The autoresearch ledger records that the four throughput cells "remain unlaunched because a foreign process leaves 23,246 MiB free below the frozen 28,672 MiB gate."

### 11.3 Track-B / ZPD — a relevant *negative* result

A ZPD "learnability" teacher signal was added to the adaptive sampler and run head-to-head against SONIC's native failure-rate sampler (seed 0, 128 motions, 200 iterations, 614,400 transitions per arm):

| | ZPD learnability | native failure-rate |
|---|---|---|
| success | 0.5625 | **0.5781** |
| MPJPE-L (mm) | 43.00 | **42.38** |
| effective bins | 608 | 283 |
| max prob / uniform | 6.74 | 17.68 |

The mechanism activated (the distribution really did spread) but AUC favoured the control on every registered metric, and **both arms degraded from the released checkpoint**. This is direct evidence for Part I's gating discipline: a difficulty-proxy reparameterization of the sampler did not beat native failure sampling. It also raises a prior concern — short continuations from the released checkpoint on a small pool *degrade* it, which our paired-branch design must absorb (the control branch degrades too, so the paired difference remains the right estimand, but the noise floor may be large).

### 11.4 Other main-line work (not ours, do not touch)
Kimodo / counterfactual-scene dataset generation: 30 modules, ~45 tests, live rollouts as recent as 2026-08-17. `docs/research_plan_predictive_latent_correction_v3.md` describes a latent-residual correction idea — **plan only, no code**.

## 12. Overlap verdict — build vs reuse

| Component (Part I §5) | Verdict |
|---|---|
| Cohort selection, source-disjoint splits, reference-length inventories, feasibility covariates, panels, equal-KL intervention plan, probe schedule | **REUSE as frozen data.** Consume from `/data/.../lace/manifests/`. Never regenerate — regeneration would break their SHA locks and their preregistration. |
| Motion pools (512 / 4950, `robot_filtered` + `smpl_filtered`) | **REUSE.** Already converted; symlinked read-only. |
| Released checkpoint | **REUSE.** sha256 `e6bdab3f…`, verified. |
| ZPD/learnability sampler + paired-experiment harness | **DO NOT REBUILD.** Built, run, negative. |
| LACE atlas / probes / signatures / representations / storage locks | **DO NOT REBUILD.** Different RQ; 35k lines exist. |
| Counterfactual-scene / Kimodo dataset pipeline | **DO NOT TOUCH.** Unrelated program, actively running. |
| **BranchCapsule (RNG capture), exact dose accounting, paired branch-and-continue runner, multi-horizon utility labels, quality-qualified `J_eff` + harm vector, LUCID latent-gap/VAE probe, residual utility sampler** | **BUILD — genuinely absent everywhere.** Zero hits across both working copies. This is the whole contribution. |

Note the asymmetry that makes this program worth doing: LACE froze an *equal-KL intervention plan* but has never measured what an intervention *causally buys*. Our paired branch-and-continue is precisely the missing measurement, and it can run **on LACE's own frozen panels and splits**. The two programs are complementary, not competing.

## 13. Amendments to Part I

- **§5.1 build location.** Build in `~/lucid/GR00T-WholeBodyControl` (tagged `sonic-audit-base`) as planned, but consume LACE manifests as *inputs*. Rationale: LACE's frozen artifacts are **data**, portable across checkouts; the LACE *source* mainly exists to build them, and that build is finished. This keeps the two programs separable and leaves a later merge open. **Open decision for the user — see §15.1.**
- **§5.2 SamplerAdapter.** Design confirmed correct against the code, with one refinement: the single context-selection point is `MotionLibBase.sample_motion_ids_and_time_steps()` (multinomial over `adp_sampling_active_prob` restricted to `adp_samp_active_motion_bins`; `adp_samp_bins[bin] = (orig_motion_id, bin_start, bin_end)`). Dose must be counted **at draw time there**, not only where `adp_samp_num_episodes` is incremented in `update_adaptive_sampling_stats()` — the latter is episode-*end* bookkeeping. Record both drawn dose (intended exposure) and completed dose (termination-adjusted), per Part I §4.3.
- **§4.5 suites.** Map LACE partitions onto our roles instead of inventing new splits: `D_curriculum` → adaptation pool; `D_geometry` → development deployment suite `D_dev` (utility labels, estimator selection); `D_test` → frozen final test, kept unopened; `D_atlas` → proxy/feature fitting; `D_controller` → reserved.
- **§4.2 intervention.** Support two granularities: our bin-level ε-kernel (radius 1) *and* LACE's frozen panel-level equal-KL dose. The latter costs nothing extra to run and makes the utility measurement directly informative for LACE's RQ1 as well.
- **§6 schedule.** Week 1–3 infrastructure shrinks: pools, splits, panels, checkpoint, and feasibility covariates already exist. Week 1 reduces to env + baseline + throughput profile (**done**, §14). The saved time goes into the branch capsule and dose accounting, which are the genuinely novel and highest-risk pieces.

## 14. Environment as built (week-1 exit gate)

| Item | Value |
|---|---|
| conda env | `sonic` (clone of `flow_isaaclab`), Python 3.11.14 |
| Isaac | IsaacLab 2.3.2 · IsaacSim 5.1.0 — matches SONIC's declared version |
| torch | 2.7.0+cu128, `arch_list` includes `sm_120` |
| GPU | RTX 5090 (32.6 GB), capability (12, 0) — Blackwell needs the cu128 build; the older `env_isaaclab` (torch 2.5.1) would **not** work |
| deps | `pip install -e gear_sonic[training]` with torch/numpy constraints; psutil held at 5.9.8 for isaacsim-kernel |
| known conflict | isaacsim-kernel pins numpy 1.26.0, gear_sonic pins 1.26.4 — patch-level, validated by a successful Isaac Sim launch |
| data root | `/data/robotixx/lucid-sonic` (on `/data`, 129 GB free; `/` is at 94%) |
| pools | `pools/debug512` (512 clips), `pools/adapt4950` (4950), `pools/metadata` — all symlinks, no copies |
| checkpoint | `sonic_release/last.pt` → sha256 `e6bdab3f64a3…`, 469,418,283 B |
| run env | `source /data/robotixx/lucid-sonic/lucid_env.sh` — sets `TMPDIR` under our data root because `/tmp/isaaclab` is owned by another user (`bwang25`) on this host |
| receipt | `/data/robotixx/lucid-sonic/manifests/env_receipt.json` |
| tags | `sonic-audit-base` = `c374bae`, `bm-lucid-base` = `cd65172` |

Downloads avoided by reusing existing data: BONES-SEED `g1.tar.gz` (23.5 GB), SMPL tar parts (32.3 GB), plus the CSV→motion_lib conversion. `smpl_motion_file: dummy` is supported upstream, so the 32 GB SMPL pack is optional for a G1-encoder-only oracle.

## 15. Revised risks

### 15.1 GPU contention is now the dominant feasibility risk
The RTX 5090 is **shared** and persistently loaded by other users' jobs (~21–25 GB of 32.6 GB resident, ~90% utilization during setup; `/tmp/isaaclab` owned by `bwang25`). LACE's entire GPU program is blocked on exactly this — its frozen launch gate requires 28,672 MiB free and a foreign process left 23,246 MiB.

This matters more for us than for LACE: a paired branch-and-continue campaign is **2 × contexts × seeds × horizons** training runs, far more GPU-hours than LACE's one probe sweep. Concretely, Part I's screening design (3 stages × 24 contexts × 2 seeds, shared control) is ~150 continuations.

Mitigations, in order:
1. Re-scope to **Tier S** (Part I §6): 512-clip pool, small `num_envs`, short horizons, 1 screening seed, shared control — enough for Gate A (identifiability) only.
2. Use LACE's **SONIC-Lite S** initialization (9.6 MB actor/critic already built) instead of the 42M release model for infrastructure and noise-floor work.
3. Treat the noise floor as the first measurement, not an afterthought: run the ε=0 paired branches **before** committing to any campaign size, and size the campaign from the measured variance.
4. Negotiate exclusive GPU windows, or add GPUs. **Without either, Part I's confirmation campaign (4 fresh seeds, independent paired controls) is not affordable on this host.**

### 15.2 Continuation degrades the released checkpoint
Track-B observed that both arms degraded from the release checkpoint under short continuation on a small pool. Paired differencing still identifies the treatment effect, but the *variance* may swamp between-context differences — which is Falsification 2 / Gate A. Budget for this explicitly: measure ε=0 branch spread first.

### 15.3 LACE source is untracked
35k lines in `gear_sonic/research/lace/` are not in git. If we consume LACE manifests, we depend on artifacts whose generator is not version-controlled. Mitigation: we consume the **manifests plus their `*_lock.json` SHA-256 digests** (in `configs/research/lace/`), and record those digests in our own receipts, so provenance survives even if the generator changes.

## 16. Revised immediate next actions

1. ✅ env `sonic` built and verified; ✅ data + checkpoint wired; ✅ repos tagged; ✅ receipt written.
2. ✅ Released checkpoint loads, steps, and runs headless on the 512-pool.
3. ✅ Throughput measured (§18). **A full-suite eval did not complete in 50 min and was stopped**; a bounded 300-step probe completed and gave the numbers below.
4. ✅ `schema.py`, `intervention.py`, `sampler_adapter.py`, `rng_capsule.py`, `branch_capsule.py`.
5. ✅ `motion_pool.py`, `split.py`, `probe_manifest.py` — pool, splits, and frozen campaign design.
6. ✅ `quality_metrics.py`, `latent_gap_probe.py`, `utility_label.py` (Gate A), `proxy_audit.py` (Gate B), `callbacks.py`.
7. ◻ **Re-measure throughput on an idle GPU** — everything downstream is sized from it.
8. ◻ ε=0 paired branches → measured noise floor → size the screening campaign from it.
9. ◻ Proxy-feature extraction from live rollouts; branch-runner CLI.
10. ⛔ Estimator and residual allocator — **deliberately not built**. Gate B authorizes them or nothing does.

## 18. Measured throughput (2026-08-18)

Bounded probe: released checkpoint, 512-clip pool, `num_envs=64`, headless, stopped at 300 policy steps.

| | |
|---|---|
| wall / startup / stepping | 503.6 s / 58.2 s / 443.5 s |
| policy steps · env-steps | 0.68 /s · **43 /s** |
| peak RSS | 6.4 GB |
| concurrent GPU processes | **8** (89% util, 31.3/32.6 GB resident) |

**This is a contention number, not a hardware number.** The card was shared with the user's own Kimodo/counterfactual render jobs and `ued_bench` jax jobs throughout.

Implications at the measured rate (SONIC uses `num_steps_per_env = 24`):

| `num_envs` | min / PPO iter | hours / branch (H_l = 128) |
|---|---|---|
| 64 | 0.6 | 1.3 |
| 512 | 4.7 | 10.0 |
| 4096 | 37.8 | 80.6 |

A 3-stage × 24-context × 2-seed screening campaign is 100 continuations (96 intervention + 4 shared control) ≈ **128 GPU-hours even at `num_envs=64`**, and `num_envs=4096` is unreachable. Receipt: `/data/robotixx/lucid-sonic/manifests/throughput_receipt_ne64.json`.

**Consequence for the programme:** re-measure on an idle GPU before sizing anything. If the idle rate is not at least ~20× the contended rate, the campaign must drop to Tier S (1 seed, shared control, short horizons, Claim Level 1 only) or move to more GPUs.

## 17. Decisions the user should make

1. **Build location.** Continue in the clean `~/lucid` checkout (current choice, keeps programs separable), or move into the main line `~/GR00T-WholeBodyControl` where LACE's source lives and reuse its modules directly? Choosing the main line would let us reuse `interventions.py` / `fixed_distribution.py` / `compute.py` instead of writing equivalents, at the cost of entangling two research programs in one untracked tree.
2. **Relationship to LACE.** Is practice utility meant to *supersede* LACE's RQ1, run *alongside* it, or *serve* it (our paired branches would measure what LACE's frozen equal-KL doses actually buy)? The third framing is the cheapest and makes both programs stronger.
3. **GPU budget.** Is exclusive access to the 5090 obtainable, or should the program be scoped to Tier S / Claim Level 1 on this host?
4. **Track-B negative result.** Should it be written up as evidence for the Part I §2 L1 claim, or set aside?


## 19. Live smoke verification (2026-08-18)

Two paired branches run inside real SONIC training — released checkpoint, 512-clip pool, `num_envs=64`, 5 PPO iterations, ε=0.25, kernel radius 1. Both exited 0 (376 s and 360 s). Receipt: `/data/robotixx/lucid-sonic/manifests/smoke_receipt.json`.

| | control | intervention |
|---|---|---|
| armed | false | true |
| episodes drawn | 76 | 80 |
| kernel mass drawn | 0.000 | 1.736 |
| bins touched | 60 | 63 |
| **draws on the target motion** | **0** | **5** |

Realized extra kernel dose **1.736** — the utility denominator, computed from real draws rather than from nominal `ε·H`.

The intervention landed exactly where designed: the target bin reached sampling probability **0.146** against **0.0068** for the highest non-kernel context (**21×**), with both radius-1 neighbours boosted (0.056, 0.055), and the distribution still summing to **1.000000**.

Verified live: callback installs without disturbing the native computation; the control arm leaves the distribution untouched; dose is recorded per bin and per motion; capsules carry model, optimizer, the 4107-bin sampler counters, and full RNG including CUDA state.

### 19.1 Three defects only a live run could surface

1. **`_motion_fps` is a per-motion tensor upstream, not a scalar.** `float()` on it raised and killed the run at install. Bins live on the resampled *simulation* timeline keyed by dataset-wide motion id, while `_motion_fps` holds *source* clip rates keyed by batch-local id — mixing the indexing schemes attaches the wrong rate to a clip. Now resolved via the scalar `_sim_fps`. **The CPU suite could not have caught this**: my fake used a scalar. Both fakes now mirror the real types and the contract test asserts them directly.
2. **SONIC loads resident motions with replacement**, so one global bin occupies several positions in `adp_samp_active_motion_bins` — 18 of 535 live entries were duplicates. Verified (not assumed) that the kernel covers every copy, the distribution stays normalized, and dose is counted per draw rather than per copy.
3. **A snapshot at install captures the sampler's prior, not its statistics.** `adp_samp_num_episodes` and `num_failures` both start at `init_num_failures`, so all 535 contexts read failure rate exactly **1.0** — one distinct value. Stratifying a campaign on that gives it *no difficulty axis at all*. Added `snapshot_at_step`; after 3 iterations the same pool shows **63 distinct failure rates**. `assign_failure_quartiles` now refuses a degenerate candidate set rather than manufacturing four strata from ties.

### 19.2 Still unverified (needs GPU time, not new code)

- **Resume equivalence** from a capsule — two runs of the same branch.
- **Bitwise no-op parity**, native vs research-disabled — two full runs.
- Multi-horizon capsule reuse across a full 128-iteration branch.

## 20. Pretrained instruments

| encoder | clips | windows | recon (train → final) | holdout | noise control | fingerprint |
|---|---|---|---|---|---|---|
| `lucid_encoder_debug512.pt` | 309 | 60,375 | 46.4 → 2.41 | 2.33 | 494.9 | `c7518a45…` |
| `lucid_encoder_adapt4950.pt` | 2,973 | — | 24.1 → 1.95 | 1.79 | 14,686.5 | `52fd470b…` |

Both trained **only on the adaptation split** (dev and test withheld entirely), resampled 30 fps → 50 Hz to match the rate at which the gap is measured, then frozen and fingerprinted.

Validated on 25 **test-partition** clips the encoder never saw: raw joint-space error rates a one-frame contact-like transient and a sustained deviation of a quarter the per-frame magnitude as **exactly equal** (ratio 1.000), while the latent gap ranks the transient at **0.149** of the drift — a **6.7× relative down-ranking**. That is LUCID's central claim, measured on the real instrument rather than asserted.


## 21. First adaptation run and a costed campaign (2026-08-18)

A controlled continuation of the released checkpoint on the 512-clip pool, `num_envs=256`, 24 PPO iterations. Receipt: `manifests/adaptation_receipt.json`.

### 21.1 Real training throughput

| `num_envs` | s / iteration | env-steps/s | h per 128-iter branch |
|---|---|---|---|
| 64 | 58.5 | 26 | 2.08 |
| 256 | **70.7** | 87 | 2.51 |

**Iteration time is nearly flat in `num_envs`** — 4× the data for 21% more wall-clock. So *horizon length, not environment count, is the cost driver*, and a campaign should use the largest `num_envs` that fits and buy its savings from shorter horizons. This inverts the naive assumption that small `num_envs` is the cheap option; small `num_envs` is merely *noisier* for almost the same price.

### 21.2 The transient is large, and it changes the design

| | iteration 1 | iteration 24 |
|---|---|---|
| mean reward | 0.48 | **17.83** |
| mean episode length | 13.4 | **222.7** |

Continuation from the released checkpoint is a 37× reward transient, not a perturbation. Two consequences:

- **Branch origins must be stage capsules, not the cold checkpoint.** A branch launched cold spends its whole horizon inside the transient, where variance is largest and the policy is not the policy whose practice utility we mean to measure. This is what motivated `export_sonic_checkpoint` (§19-era capsules could archive a branch but not seed one — a defect found only when wiring the real campaign).
- Track-B's observation that continuation *degrades* the release checkpoint is reproduced and explained: the degradation is the start of this transient, and it recovers well past the starting point by iteration 24.

### 21.3 The frozen campaign

`probe_screen_v1_late` (`ee844e25…`), built from the post-warm-up snapshot (step 20: **2148** active bins over **195** motions, **334 distinct failure rates** — against *one* distinct value at step 0):

| | |
|---|---|
| candidates | 1413 (735 correctly excluded as dev/test) |
| contexts | 24, spanning all four failure quartiles (6/5/7/6) |
| families | 10 |
| contact regimes | aerial 2 · dynamic 9 · steady 13 |
| horizons | H_s 4 · H_m 12 · H_l 32 iterations |
| branches | 48 intervention + 2 shared controls |
| **estimated cost** | **31.4 GPU-hours** (0.63 h per branch) |

31 GPU-hours is affordable — a materially different conclusion from the 128–226 hours implied by the contended measurement, and it comes entirely from measuring rather than assuming.


## 22. The noise floor, measured — and what it costs the campaign (2026-08-18)

Three ε=0 pairs plus three controls at different seeds, `num_envs=256`, 8 iterations, from the released checkpoint. Receipt: `artifacts/noise_floor/noise_floor_v2.json`.

### 22.1 Two floors, three orders of magnitude apart

| floor | what it measures | Mean rewards | Mean length |
|---|---|---|---|
| **machinery** (ε=0, same seed) | does arming the path perturb a run that should be unchanged? | **0.000000** | **0.000000** |
| **divergence** (controls, different seeds) | noise a real intervention actually faces | sd 0.765 (**7.04%**) | sd 5.94 (**4.68%**) |

The machinery floor is *exactly zero* across all 8 iterations and every metric — the ε=0 identity guarantee confirmed end-to-end on hardware, not just in unit tests.

**But it is the wrong number to size a campaign with, and reporting it alone would have been self-flattering.** Both arms of an ε=0 pair share their entire random stream, so no trajectory divergence is possible by construction. A real intervention diverges the moment it samples a different bin. The honest floor is the cross-seed one: **≈7% relative on mean reward**.

### 22.2 This threatens the planned dose

At one seed per context, an intervention must move mean reward by roughly 7% (and ~14% for a 2σ separation) to be distinguishable from seed noise. An ε=0.10 kernel over **one bin among 2148 resident** is a very small perturbation; its expected effect is plausibly well below that.

Five ways to close the gap, in order of attractiveness:

1. **Start branches from a settled stage capsule, not cold.** The measured divergence is inflated by the adaptation transient — reward climbs 0.26 → 10 over the 8 iterations measured, and per-iteration relative divergence swings between 1.2% and 28.5%. A settled origin should shrink it materially. This is now possible (`export_sonic_checkpoint`, §21.2) and is the **first thing to re-measure**.
2. **Coarser contexts** — intervene on a motion family rather than one bin. Exactly the plan's Falsification-2 fallback, and it multiplies the dose.
3. **Larger ε.** Cheap, but it drifts from "local intervention" semantics and changes the estimand.
4. **Longer horizons**, letting effects accumulate.
5. **More seeds.** Noise falls as 1/√n, so resolving a 1% effect against 7% needs ~100 seeds per context. Not affordable, and worth stating so plainly rather than discovering later.

**Gate A is not yet passed or failed** — it cannot be decided until utility labels exist to compare against this floor. What is settled is the denominator, and that it is large enough to matter.

### 22.3 A branch died, and the fix matters

`floor_s1002_intervention` exited 1 at install: its context was not in that seed's resident motion batch, and `_build_kernel` refused. The refusal was correct; the *behaviour* was not. SONIC holds only part of the pool loaded — **195 of 512 motions** in the measured run — so a randomly chosen context is absent at install more often than not, and a campaign would have lost most of its branches this way.

Arming is now fail-soft: a branch that cannot arm starts disarmed, retries on every step (a resample may bring its motion into residence), and records `armed_steps`, `arm_attempts`, `first_armed_step`, and `never_armed` in its dose report. A branch that never arms delivers no dose, and `build_utility_record` already refuses to label it. The failure belongs at label time, loudly — not at install.


## 23. Live LUCID, and a noise floor cut by two thirds (2026-08-18)

### 23.1 The latent gap now runs live, and behaves as LUCID predicts

Two things were built but never connected: the quality telemetry's `observe()` was called from nowhere, and the LUCID gap had no source of live command/execution data. `PracticeObserverCallback` patches `ManagerEnvWrapper.step` (trainer callbacks fire per *iteration*; the gap needs H consecutive *steps*).

`q_cmd` is `robot.data.joint_pos_target` — the PD target, not the raw policy output, since the action manager rescales before the controller sees it. Verified live: `command_source: joint_pos_target`, encoder fingerprint matching the frozen artifact, 9 gap samples from 24 steps (exactly right for a 16-frame window), and `missing_signals: []`.

Over 13 iterations of adaptation:

| | iteration 1 | iteration 13 | change |
|---|---|---|---|
| **latent** gap (median) | 0.190 | 0.019 | **10×** |
| **raw** joint mismatch | 7.20 | 4.66 | 1.5× |

**The latent gap is roughly seven times more responsive to the policy improving than raw joint error.** That is LUCID's premise showing up in live data, and it is the first evidence in this programme that the latent representation earns its place as a *signal*, independent of whether it predicts practice utility.

### 23.2 The floor, re-measured from a settled origin

Three controls per condition, `num_envs=256`, 8 iterations:

| origin | reward rel-sd (final iter) | reward rel-sd (last-4 mean) | length rel-sd (last-4) |
|---|---|---|---|
| cold (released checkpoint) | 7.04% | **10.62%** | 7.05% |
| settled (`model_step_000024`) | 4.77% | **3.33%** | 3.14% |

**Starting from a settled checkpoint cuts the practical floor by 69%.** The hypothesis in §22.2 was right: the cold-origin figure was mostly adaptation transient, not irreducible noise.

Two design consequences, both now implemented:

- **Branch origins must be settled stage checkpoints.** Enabled by `export_sonic_checkpoint`, validated on a real capsule (55 policy + 17 value tensors, provenance intact).
- **Efficacy is averaged over the last 4 iterations, not read at a single point.** Same runs, a third less noise, no extra compute. `DEFAULT_EFFICACY_WINDOW = 4`.

With a ~3.3% floor, a single-seed intervention needs ≈3.3% (1σ) or ≈6.6% (2σ) movement to register — against ≈10.6% before. Whether an ε=0.10 kernel on one bin among 2148 reaches that is now the open empirical question, and it is a much closer call than it was.

### 23.3 Resume restores more than weights, and still shows a transient

`env.load_env_state_dict` *is* called on resume, so sampler counters and motion state come back. Yet a resumed run still restarts at low reward — because reward here scales with episode length, and episodes restart. The lesson is not that resume is broken but that **the first iterations after any restart are the noisiest**, which is exactly why efficacy is now averaged over a trailing window rather than sampled at a point.

### 23.4 Two more defects, both found only by running

1. **Sensor/articulation index crossing.** Contact forces are indexed by the `ContactSensor`'s prim-discovery ordering, velocities by the articulation's. Resolving both from the robot read forces off the wrong bodies — the first live run reported a 99% undesired-contact rate against SONIC's own reward term implying ≈0.006. Each index set now comes from its own owner; four tests run a deliberately shuffled sensor ordering.
2. **Capsules held CUDA tensors**, so opening one required free GPU memory — unavailable during the very run that produced it. Tensors are now moved to CPU recursively and every reader uses `map_location="cpu"`.

That is **twice** a fake simpler than reality hid a live-only defect (`_motion_fps` was the first). Fakes now mirror upstream types *and* orderings, and the contract tests assert them.


## 24. The LUCID curriculum, implemented on SONIC (2026-08-18)

The manuscript's actual method now runs against a live SONIC environment: frozen encoder → latent command-execution gap → PI controller → scalar DR intensity λ → every randomization channel scaled around its nominal.

### 24.1 Faithful to the paper, with one discipline added

`dr_controller.py` implements the loop as written — high-quantile gap (not the mean, so a calm epoch with a few near-failures still registers), integral clamping for anti-windup, α bounding a single epoch's move, and the return guard that decays λ and clears the integral after two consecutive low-return epochs.

The guard earns its keep for a specific reason: **a fallen robot tracks its own commands beautifully at the point of no return**, so the gap alone cannot see that failure. An epoch with *no* gap samples holds λ still rather than guessing — moving difficulty on no evidence is precisely the failure the scheduler exists to prevent.

The added discipline: the callback logs λ and the gap that drove it and measures *nothing* about whether the curriculum worked. Outcomes are measured separately, from simulator state, under presets the curriculum never sees. Scoring a scheduler with its own control signal would make any improvement partly definitional.

### 24.2 δ_target is calibrated, not chosen

Per the manuscript, `δ_target = μ + 3σ` of the gap at λ = 0. Measured on 24 samples from settled-origin runs: median p90 0.123, **μ+3σ = 0.778**. A hand-picked constant would not transfer between encoders, whose latent scales differ, so `calibrate_target` is part of the method rather than a convenience.

### 24.3 Coverage is reported, not assumed

λ scaling is exact at both ends — λ=0 collapses every range to its nominal, λ=1 restores the configured maximum precisely, so a curriculum at full intensity is indistinguishable from fixed DR. Scaling is always recomputed from a captured baseline; compounding epoch on epoch would drive every range to zero within a few updates.

**But only some channels can be scheduled at all.** IsaacLab event terms declare a mode, and only `reset` and `interval` terms re-read their ranges after startup:

| channel | mode | schedulable at runtime |
|---|---|---|
| body mass | `reset` | ✅ |
| external push | `interval` | ✅ |
| friction / restitution | `startup` | ❌ |
| base CoM | `startup` | ❌ |
| joint-default offset | `startup` | ❌ |

`scalable_terms` names exactly which channels a run actually moved, so a curriculum cannot claim credit for randomization it never touched. This is a property of SONIC's configuration, not of the controller, and closing the gap means per-env reset-conditioned events — the plan's §5.10 physics extension.

### 24.4 Three arms, one code path

`mode ∈ {lucid, fixed, off}` so the comparison arms differ only in how λ is chosen: scheduled by the gap, pinned at 1.0, or pinned at 0. 825 CPU tests cover the controller, the scaling, and the callback.

### 24.5 Status: implemented and queued, blocked on GPU capacity

The three-arm run (16 iterations each from the settled origin, seed 4000) is **implemented and launched behind a capacity gate**. It failed twice on GPU out-of-memory: PhysX reserves a **fixed ~640 MB contact buffer regardless of `num_envs`**, so dropping 256 → 128 envs did not help — the card was at 29.1/32.6 GB with eight other processes and under 3 GB free.

The driver now waits for 6 GB before each arm rather than failing at scene construction. **No training-performance comparison should be read from this session; the arms have not yet run.** What is established is that the curriculum is implemented, unit-tested, and configured, with δ_target calibrated from real measurements.

---

## 25. Continuation results (2026-08-20)

### 25.1 Baseline and idle-GPU throughput

The continuation began from `research/practice-utility` at `811f084`: 912 CPU tests
passed, the diff remained confined to research/scripts/tests/config/docs, and the RTX
5090 had 30,986 MiB free. At 256 environments, a matched six-iteration probe measured:

| runner | env-steps/s | median iteration | observer penalty |
|---|---:|---:|---:|
| native | 3725.9 | 1.649 s | — |
| observer | 3603.5 | 1.705 s | 3.28% |

The earlier 86.9 env-steps/s measurement was contention, not normal capacity. Including
measured startup, the frozen 50-branch × 32-iteration screen is approximately 1.0 serial
GPU-hour. Receipts: `throughput_idle_native_ne256_20260820_110244.json` and
`throughput_idle_observer_ne256_20260820_105657.json`.

### 25.2 A config label hid a missing latency mechanism

The first fixed-λ A/B was exactly null. Live instrumentation then showed zero delayed
actuator groups in both arms. `_to_delayed` had copied the parent dataclass field
`class_type=ImplicitActuator` into `DelayedImplicitActuatorCfg`; the config name changed,
but the factory still built the base class. The patch now omits that discriminator,
patches the resolved environment config at `custom_instantiate`, and audits the actual
actuator instances and lag buffers. The two null receipts are retained as defect evidence.

This corrects the 2026-08-19 claim: its five non-latency channels were live, but its
reported latency was implied by λ rather than executed. The old three-arm comparison is
therefore a five-channel plumbing result and cannot support latency-robustness claims.

### 25.3 Corrected fixed-λ latency A/B

`latency_ab_ne256_20260820_112516.json` compares delay-only λ=0 and λ=1 for 12
iterations, 256 environments, seed 8200, and a settled origin. Both arms instantiated
five delayed groups. λ=0 had 1280/1280 zero lags; λ=1 averaged 3.68 steps (18.4 ms), with
88.1% nonzero and a maximum of eight steps.

| last-4 metric | λ=1 vs λ=0 |
|---|---:|
| reward | **−35.8%** |
| episode length | **−18.1%** |
| torque saturation | **+32.7%** |
| energy proxy | **+52.5%** |
| foot slip / step | **+21.3%** |

The delay mechanism is behaviorally active by a wide margin over the preregistered
3.33% reward / 3.14% length floors. This is one-seed mechanism validation, not curriculum
efficacy.

### 25.4 Revised frontier

The first-iteration anomaly was an arm-initialization bug, not RNG consumption. Off mode
inherited `fixed_lambda=1` during warmup. It now starts at λ=0, and warmup records are
written rather than only held in memory. A four-iteration, same-seed live pair
(`curriculum_warmup_parity_ne128_20260820_114047.json`) showed exact equality in reward,
length, entropy, and action-noise statistics for all three treatment-free rollouts;
lucid then advanced to λ=0.0316 while off remained at zero.

Installed-but-disabled research callbacks are also exact no-ops. In
`noop_parity_ne128_20260820_114521.json`, native SONIC and the same command with both
observer and curriculum callbacks disabled matched reward, length, entropy, and action
noise at zero tolerance for all four iterations.

### 25.5 Resume equivalence fails the L0 gate

`resume_equivalence_ne128_20260820_120104.json` executes the preregistered design:
20 uninterrupted iterations versus a capsule at step 10 followed by a resumed run through
step 20. The resume loaded policy, value, optimizer, LR scheduler, trainer, environment,
sampler, and capsule RNG state. It also exposed and fixed two live defects: the capsule
saver had omitted positional trainer state, and the resumed HF `max_steps` must remain the
absolute target (20), not the remaining count (10).

The mechanism then completed, but equivalence failed: resumed last-4 reward was 17.015
versus 13.216 (+28.7%), and length 204.0 versus 164.8 (+23.8%). These exceed the
settled-origin 3.33%/3.14% one-sigma rules by a wide margin. SONIC unconditionally calls
`reset_all()` at every train start, so exact post-split identity is structurally
impossible with the current capsule; the trailing-window mismatch shows the restart
effect does not wash out within ten iterations either.

This rejects uninterrupted-vs-resumed trajectory identity. The paired protocol must use
synchronized fresh restarts, which is tested below.

### 25.6 Symmetric restart identity resolves the usable L0 boundary

`restart_pair_equivalence_ne128_20260820_142104.json` restores two branches from the
same step-10 checkpoint and capsule. Both branches therefore take SONIC's unavoidable
fresh reset. All ten subsequent iterations match exactly at zero tolerance on reward,
episode length, entropy, and action-noise statistics. This is the actual boundary used
by paired causal branches, so L0 passes for a symmetric-restart estimand. Seamless live
trajectory continuation remains unsupported and must not be mixed with restarted arms.

### 25.7 Corrected three-seed curriculum retraining

`curriculum_comparison_ne128_20260820_143058.json` contains 3 modes × 3 paired seeds ×
32 iterations from the settled step-24 origin. Every branch instantiated five delayed
actuator groups, scaled all six DR terms, completed, and exported a SONIC-compatible
checkpoint. The callback now reads SONIC's native `objective/rewards` key, so the return
guard is live. Controller gains were bounded to `ki=0.02`, `integral_max=1.0`; the
integral contribution is at most 0.02 even when clamped.

| last-4 cross-seed mean | LUCID | fixed DR | no DR |
|---|---:|---:|---:|
| reward | 17.73 | 10.03 | 20.16 |
| episode length | 210.6 | 155.5 | 233.8 |
| realized delay (steps) | 1.76 | 3.89 | 0.00 |
| final λ | 0.756 | 1.000 | 0.000 |

LUCID is stable and substantially better than immediate full DR during training (+76.8%
reward, +35.4% length), but trails clean no-DR training (−12.0% reward, −10.0% length).
That establishes healthy curriculum mechanics and a real robustness/training tradeoff,
not held-out efficacy.

### 25.8 Frozen-policy deployment-DR evaluation

`curriculum_robustness_ne128_20260820_153754.json` evaluates all nine final checkpoints
with no learning, matched evaluation seeds 8700–8702, and the same frozen 102-motion
content-dev panel. Because the 32-iteration training used all debug512 motions, this is
fresh-physics robustness, not unseen-motion generalization. The three presets are clean
nominal physics, fresh draws from the complete six-channel training envelope, and full
non-latency DR with fixed 60 ms actuation latency (12 physics steps, outside the trained
0–40 ms range).

An initial pilot was invalidated: `eval_agent_trl.py` removes `push_robot` because SONIC
marks it train-only. The corrected command clears `train_only_events`, and every run
records all six active terms, configured ranges, five live delayed-actuator groups, and
the actual lag histogram. All 27 runs completed 102 motions, no quality channel was
missing, and checkpoint hashes were unchanged.

| cross-seed mean (sample sd) | LUCID | fixed DR | no DR |
|---|---:|---:|---:|
| clean success | **83.99% (1.13)** | 80.39% (3.53) | 83.01% (0.57) |
| clean progress | **89.82%** | 88.38% | 89.72% |
| full-DR success | 54.25% (1.50) | **56.54% (5.99)** | 50.65% (4.08) |
| full-DR progress | 70.21% | **72.88%** | 68.40% |
| 60 ms success | 0.00% | 0.00% | 0.00% |
| 60 ms progress | 8.30% | **10.61%** | 7.93% |

LUCID improves full-DR success over no DR by 3.59 percentage points but trails fixed DR
by 2.29 points. It preserves clean success better than fixed (+3.59 points). Under full
DR, auxiliary batch diagnostics suggest fewer undesired contacts for LUCID (0.108) than
fixed (0.112) and off (0.124), but slightly higher foot slip and torque saturation than
fixed, and energy is 179.7 versus 162.6. These diagnostics include auto-reset
environments after their scored motion terminates, so a per-episode safety claim remains
open. All three fail catastrophically at 60 ms; low MPJPE in that condition is an
early-termination artifact rather than good tracking.

This is evidence that SONIC's DR curriculum path works, not that the current curriculum
is deployment-ready or superior. MJLab remains a fallback cross-simulator benchmark,
not the first response to this policy-level gap. The longer-budget/terminal-λ proposal
was tested next and revised by §25.9.

### 25.9 Terminal full-DR continuation is a negative result

Two autoresearch iterations tested whether LUCID's terminal λ=0.756 simply left it
underexposed to full DR. Both restarted the original step-32 LUCID and fixed checkpoints
with full policy/value/optimizer/trainer/environment/sampler/capsule state, then trained
both methods at λ=1 for equal compute. The frozen evaluator, motion panel, checkpoint
seeds, evaluation seeds, and three presets were unchanged.

| cross-seed result | step 32 | +4 full-DR iterations | +16 full-DR iterations |
|---|---:|---:|---:|
| LUCID clean success | **83.99%** | 79.41% | 76.80% |
| LUCID full-DR success | **54.25%** | 51.31% | 51.96% |
| LUCID fixed-60 ms success | 0.00% | 0.00% | 0.00% |
| LUCID fixed-60 ms progress | 8.30% | 8.47% | **9.35%** |
| fixed clean success | **80.39%** | 78.10% | 71.57% |
| fixed full-DR success | **56.54%** | 55.88% | 49.35% |
| fixed fixed-60 ms progress | 10.61% | 10.78% | **12.04%** |

The four-iteration study failed every preregistered keep condition: LUCID full-DR
success was below its 56.25% improvement threshold, LUCID trailed its matched fixed
control by 4.58 points, and clean success was below the 80.99% retention floor. The
sixteen-iteration study also regressed absolute clean and full-DR performance. Slightly
better 60 ms progress without any completed motion is not deployment robustness.

Receipts: `curriculum_consolidation_ne128_20260820_174016.json` and
`curriculum_robustness_ne128_20260820_174608.json` (+16), then
`curriculum_consolidation_ne128_20260820_182935.json` and
`curriculum_robustness_ne128_20260820_183317.json` (+4). The experiment ledger is
`autoresearch/improve-260820-1735/`.

Decision: retain the original step-32 LUCID checkpoints and close abrupt post-hoc λ=1
continuation as an improvement path. If deployment requires 60 ms, the next matched
study must put actual 0–60 ms delay draws in training and integrate a smooth terminal
ramp inside the original equal-compute budget. The alternative is a measured deployment
latency contract below 40 ms. Do not tune this choice against the frozen final test.

1. Close the 60 ms deployment gap with matched in-budget 0–60 ms SONIC retraining or a
   verified sub-40 ms deployment latency budget; do not append another hard λ=1 phase.
2. Launch the resized probe screen with symmetric fresh restarts, then enforce Gate A
   and Gate B before any estimator or allocator work.

### 25.10 Distributional latency audit and disjoint confirmation

`latency_curriculum_audit_20260820_231532.json` verifies the live latency semantics of
all nine step-32 training arms. The configured envelope was 0–8 physics steps (0–40 ms),
with five delayed actuator groups and all six DR terms scalable. LUCID remained at zero
during warmup, and its λ/realized-mean-delay correlations were 0.980–0.982. The event
was reset-mode: each actuator group sampled independently at an environment's episode
reset and retained that lag until its next reset. Consequently, current buffers can lag
the latest λ after a curriculum update. Historical training did not use one shared
command-vector delay or within-episode jitter; LUCID's terminal quantization produced an
observed maximum of six steps (30 ms), although fixed exercised all eight steps.

The preregistered discovery receipt
`latency_distribution_discovery_ne32_20260820_232545.json` evaluates 66 frozen-policy
runs: three policies crossed with 22 cells spanning non-latency DR scales 0, 0.5, and 1;
fixed 0/20/40/60 ms; common and independent per-episode uniforms; 0.2–0.5 s common
jitter; and rare 60 ms bursts. Its 18 motions/15 canonical groups were chosen by an
outcome-blind hash split. Fixed 60 ms caused zero success for every policy, while
distributed delays were substantially less destructive and changed policy ordering.
Thus maximum latency alone is not a valid robustness descriptor; support, coupling,
dwell time, resampling cadence, and non-latency physics all matter.

Only nominal non-latency physics plus shared per-episode U(0,60 ms) satisfied the frozen
selection rule in discovery (success/progress: LUCID 27.78/42.34%, fixed 16.67/39.82%,
off 16.67/41.11%). It was confirmed without modification on the disjoint remaining 84
motions/63 canonical groups, all three checkpoint seeds, and fresh paired evaluation
seeds 9200–9202. All nine runs completed; aggregate telemetry matched every requested
latency process, all checkpoint hashes were unchanged, and canonical overlap with
discovery was zero.

| holdout mean (sample sd) | LUCID | fixed DR | no DR |
|---|---:|---:|---:|
| success | 46.03% (4.81) | **46.43% (7.24)** | 44.05% (8.58) |
| progress | 56.71% (3.27) | **58.29% (5.95)** | 55.27% (5.78) |

Against fixed, LUCID's paired mean deltas were −0.40 success points and −1.58
progress points, favorable in one of three seeds. Against no DR they were +1.98 and
+1.43 points, favorable in two seeds, but descriptive hierarchical-bootstrap 95%
intervals crossed zero: [−5.16,+9.13] and [−2.35,+5.33] points. With only three
independent checkpoint blocks, an exact two-sided sign-flip test cannot attain p<0.25.
The preregistered directional-replication criterion fails. Analysis receipt:
`latency_distribution_analysis_20260821_042612.json`.

This closes the hypothesis that the retained LUCID policy has a broad latency-process
advantage. The fair conclusion is narrower: the curriculum mechanism was live, LUCID
preserved clean performance better than fixed DR in the earlier evaluation, and latency
process specification materially changes measured robustness. The next equal-compute
training experiment must model a shared command-vector lag, expose actual 0–60 ms
support, and apply a curriculum to both amplitude and resampling cadence; it must report
episode-static and jittered cells rather than tune to the discovery winner. This remains
fresh-physics evaluation on training-seen debug512 motions, not unseen-motion, hardware,
or real-world evidence. MJLab is a later cross-simulator benchmark, not a fix for this
identified training-distribution mismatch.
