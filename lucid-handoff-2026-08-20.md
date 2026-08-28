# LUCID Handoff — 2026-08-20

Audience: a coding/research agent (Codex) continuing the LUCID practice-utility program.
Read this file fully before touching anything. The authoritative long-form design doc is
`~/lucid/lucid-design-implementation-plan.md` (620 lines, sections 0–24); this handoff
summarizes it and adds the 2026-08-19 results that are not yet recorded there.

---

## 1. What this program is (and is not)

**Goal:** measure *counterfactual practice utility* — does steering a humanoid
whole-body-tracking policy's practice distribution toward specific motion bins causally
improve deployment performance? — audited on SONIC's native failure-based bin sampler.
The LUCID latent gap (distance between commanded and achieved motion in a frozen learned
latent space) is kept as a **proxy/diagnostic**, and separately as the feedback signal for
a **LUCID DR curriculum** (a PI controller that widens domain-randomization ranges as the
latent gap shrinks).

**Not the method:** scalar-λ LUCID scheduling (IROS-2026 ms #1615) is dead as the paper
claim — matched baselines explained its early gains, and the latent gap can improve while
reward degrades. Do not resurrect it as a headline method.

**Two testbeds:**
- `~/lucid/GR00T-WholeBodyControl` (SONIC, base tag `sonic-audit-base` = `c374bae`) —
  the **claim-bearing** testbed. All work lives on branch `research/practice-utility`.
- `~/lucid/whole_body_tracking` (BeyondMimic, `cd65172`) — DR/latency sandbox only.

**Strict gating:** the utility **estimator** and **residual allocator** are deliberately
NOT built. Gate A (identifiability of utility labels) and Gate B (proxy sufficiency)
authorize them, or nothing does. Do not build learned schedulers before the gates pass.

---

## 2. Environment — how to run anything

```bash
source <workspace>/env/lucid_env.sh   # IsaacLab 2.3.2 / IsaacSim 5.1.0 / torch 2.7.0+cu128
```

**Two hosts as of 2026-08-28.** The env script is host-independent: it derives the
workspace from its own path, auto-detects the python stack (conda env `sonic` on
`robotixx`, a uv venv on `linjiw-ubuntu`), and sets `LUCID_ROOT`. `docs/machine-setup.md`
records the second host, what its data root does and does not reproduce, and the open
`pool_sha256` lineage decision. The GPU notes below describe the shared 5090 on the
original host; the second host has a **dedicated** RTX 5080 (16 GB), so its capacity
gates are not contended — but its measured throughput is in the setup doc, not here.

Non-negotiable gotchas the script handles (never bypass it):
- `TMPDIR` must be `$LUCID_ROOT/tmp` (`/tmp/isaaclab` is owned by another user → PermissionError).
- `PYTHONPATH` must be unset (ROS Humble injects python3.10 site-packages into the 3.11 env, breaks pytest).
- `eval_agent_trl.py`: checkpoint `config.yaml` `eval_overrides` force `num_envs=1, headless=False`;
  CLI wins only with `+` prefix: `+headless=true +num_envs=N`, but plain `checkpoint=...`.
- `smpl_motion_file: dummy` is fine — the 32 GB SMPL pack is optional for G1-encoder work.

**GPU:** single shared RTX 5090 (32.6 GB). Capacity changes during the day; the 2026-08-20
three-seed curriculum run shared it with a 4,096-environment MJLab job but retained at
least 21.7 GB free. Its training metrics are valid; its contended throughput is not.
**Re-measure throughput on the idle GPU before sizing any campaign** — all prior
throughput numbers (43 env-steps/s at num_envs=64; 70.7 s/iter at num_envs=256) were
measured under heavy contention. PhysX reserves a fixed ~640 MB contact buffer regardless
of `num_envs`, so lowering `num_envs` never fixes OOM — only free GPU memory does.
Isaac Sim needs ~6 GB to start.

Data root: `/data/robotixx/lucid-sonic/` — `manifests/` (JSON receipts), `artifacts/`
(encoders, capsules, curriculum logs), `outputs/` (run logs), `pools/` (symlinked,
read-only). Every experiment writes a JSON receipt to `manifests/`; keep that discipline.

---

## 3. State of the code

Branch `research/practice-utility` in `~/lucid/GR00T-WholeBodyControl`: **30 commits over
base**, ~16k inserted lines across 61 files, **zero upstream files modified** (everything
under `gear_sonic/research/practice_utility/`, `scripts/practice_utility/`,
`tests/practice_utility/`; upstream seams are patched at runtime, never edited). 954 CPU
tests passed before the consolidation study; **957** pass after adding its driver/tests.

Entry points (`scripts/practice_utility/`): `build_motion_pool.py`,
`create_probe_manifest.py`, `pretrain_encoder.py`, `run_branch.py`, `run_noise_floor.py`,
`build_utility_labels.py`, `train_with_delay.py`, `run_restart_pair_equivalence.py`, and
`run_curriculum_comparison.py`. Equal-compute terminal-dose studies use
`run_curriculum_consolidation.py`. Frozen-policy deployment evaluation uses
`eval_with_delay.py` and `run_curriculum_robustness_eval.py`.

Frozen instruments: `artifacts/lucid_encoder_debug512.pt` and
`lucid_encoder_adapt4950.pt` (trained on the adaptation split only; fingerprint-checked
by the observer at runtime).

Complete and live-verified chain: motion pool → performer/content splits (built
separately — BONES-SEED transitive closure puts 91% of the 4950 pool in one component, so
one split cannot close performer and content leakage at once) → probe manifest → paired
control/intervention branches → utility labels → Gate A → Gate B.

**LUCID DR curriculum** (implemented, live-validated 2026-08-19):
- `dr_controller.py` — PI controller on latent-gap p90 (integral clamp, alpha bound,
  two-epoch return guard), `delta_target = 0.778` (calibrated as μ+3σ of real gaps).
- `dr_scaling.py` — λ scales event-term ranges from a captured baseline (λ=0 nominal,
  λ=1 configured max, exactly).
- `dr_curriculum.py` — callback with modes `lucid` / `fixed` / `off` (one code path).
- Startup-only DR channels (friction/physics-material, base CoM, joint-default, mass)
  were made **runtime-schedulable per environment**. These five non-latency channels
  were live in the 2026-08-19 runs.
- **Correction, 2026-08-20:** the latency config copied the base actuator's
  `class_type=ImplicitActuator`, so the earlier live robots used plain actuators despite
  their delayed config label. The resolved environment seam now installs
  `DelayedImplicitActuator` instances for all five G1 groups, and the observer audits the
  actual lag buffers. Six channels are schedulable in corrected runs:
  `add_joint_default_pos`, `base_com`, `physics_material`, `push_robot`,
  `randomize_action_delay`, `randomize_rigid_body_mass`.

---

## 4. Measured results (all have receipts in `/data/robotixx/lucid-sonic/manifests/`)

1. **Intervention works** (`smoke_receipt.json`): paired control/intervention inside real
   SONIC, num_envs=64, eps=0.25 → target bin p=0.146 vs 0.0068 next (21×), realized extra
   kernel dose 1.736.
2. **LUCID premise visible live** (`adaptation_receipt.json`): over 13 adaptation
   iterations the latent gap fell 10× (0.190→0.019) while raw joint mismatch fell only
   1.5× (7.20→4.66).
3. **Noise floors** (`noise_floor` runs): machinery floor (eps=0, same seed) is exactly 0;
   cross-seed floor is 10.62% rel-sd from a cold origin but **3.33% from a settled
   origin** (stage checkpoint via `export_sonic_checkpoint`), with efficacy averaged over
   the last 4 iterations. → Branches MUST start from a settled checkpoint; efficacy MUST
   be last-4-averaged.
4. **Frozen screening campaign** `probe_screen_v1_late.json`: sized at 31.4 GPU-hours
   under contention — resize on the idle GPU before launching.
5. **Curriculum live validation** (`lucid_curriculum_validation.json`, 2026-08-19):
   6 iters, num_envs=128, settled origin. λ climbed 0.09→0.65 over five updates under
   sustained low mismatch; gap data reached the controller every iteration (24 samples)
   after a callback-ordering fix; `undesired_contact_rate` reads ~0.14, not the pre-fix
   0.99. **Correction:** five non-latency channels moved, but the reported 26.1 ms latency
   was only implied by config; no delayed actuator was instantiated.
6. **Three-arm comparison ran to completion** (2026-08-19 evening, exit 0 all arms):
   16 iterations each, num_envs=128, seed 4000, settled origin, modes lucid/fixed/off.
   Artifacts: `/data/robotixx/lucid-sonic/artifacts/curriculum/{lucid,fixed,off}/`
   (curriculum jsonl, controller state, observer jsonl); logs in
   `/data/robotixx/lucid-sonic/outputs/curriculum_{lucid,fixed,off}.log`.
   - Last-4 mean rewards: lucid 14.74, fixed 15.15, off 14.92 — **all within the 3.33%
     cross-seed noise floor. This run validates the mechanism, not efficacy.** 16
     iterations is far too short to discriminate arms, and full-strength DR (fixed λ=1)
     did not visibly hurt training at this scale.
   - LUCID arm ended at λ=0.62 with the integral clamped at its 5.0 max (controller state
     json) — the integral term saturated; revisit `ki`/`integral_max` before longer runs.
   - **No model checkpoints were saved** (16 iters is below the save interval; run dirs
     `logs_rl/.../sonic_release_test-20260819_{172604,173802,175103}` hold only
     config.yaml/meta.yaml) — so no held-out evaluation of these arms is possible; the
     comparison must be re-run longer with checkpoint export.
   - **Resolved 2026-08-20:** this was not hidden RNG use. `off` constructed its
     controller with `fixed_lambda=1`, so `fixed` and `off` both ran full DR during
     warmup while `lucid` began at zero. Off mode now starts at λ=0 and warmup records
     are persisted. In `curriculum_warmup_parity_ne128_20260820_114047.json`, lucid and
     off matched exactly on all four printed training metrics for the first three
     treatment-free rollouts; lucid then raised λ to 0.0316 while off remained at zero.
7. **GPU occupancy audit** (`gpu_occupancy_audit.json`): documented the contention story;
   now moot since the GPU is idle, but the method (bounded-run wall-clock comparison,
   output-directory staleness) is the template for future audits.
8. **Idle-GPU throughput and corrected latency A/B** (2026-08-20): at 256 envs the
   native runner sustained 3725.9 env-steps/s and the observer 3603.5 env-steps/s, a
   3.28% penalty (`throughput_idle_{native,observer}_ne256_*.json`). The frozen
   50-branch × 32-iteration screen is therefore about 1.0 serial GPU-hour including
   startup, not 31.4 hours. In `latency_ab_ne256_20260820_112516.json`, λ=0 had all
   1280 live lags at zero; λ=1 had five delayed groups, mean 3.68 steps (18.4 ms), 88.1%
   nonzero. Last-4 reward fell 35.8%, episode length 18.1%, while torque saturation rose
   32.7% and the energy proxy 52.5%. The latency mechanism is decisively active; this is
   a one-seed mechanism test, not an efficacy result.
9. **Warmup and no-op hygiene** (2026-08-20):
   `curriculum_warmup_parity_ne128_20260820_114047.json` proves lucid/off are exact
   through three treatment-free rollouts after fixing off-mode initialization.
   `noop_parity_ne128_20260820_114521.json` proves native SONIC and both research
   callbacks installed-but-disabled match all four printed training metrics exactly for
   four iterations. Both checks use zero tolerance.
10. **Resume equivalence fails L0** (`resume_equivalence_ne128_20260820_120104.json`):
    the preregistered 20-vs-10+10 run loaded model, value, optimizer, trainer, environment,
    sampler, and capsule RNG state; both paths completed through step 20. Nevertheless,
    resumed last-4 reward was +28.7% and length +23.8% versus uninterrupted, far outside
    the 3.33%/3.14% limits. Exact identity is not expected because SONIC calls
    `reset_all()` on every train start, but the trailing-window failure is still decisive.
    Two launcher defects found en route are retained in earlier receipts: Hydra required
    `+resume=true`, and capsule export had omitted the positional trainer `state`.
11. **Symmetric restart identity passes L0**
    (`restart_pair_equivalence_ne128_20260820_142104.json`): SONIC does not serialize
    live simulator/episode state, so uninterrupted-vs-resumed trajectory identity is an
    unsupported contract. The actual paired-branch boundary is two fresh resets from
    one capsule. Two such branches matched exactly for all ten restored iterations at
    zero tolerance on reward, length, entropy, and action-noise statistics. Paired
    screening is therefore unblocked when both arms restart symmetrically.
12. **Corrected three-seed curriculum retraining completes**
    (`curriculum_comparison_ne128_20260820_143058.json`): nine 32-iteration branches,
    128 environments, seeds 8600–8602, settled origin, corrected six-channel DR, and
    nine exported checkpoints. LUCID ended at mean λ=0.756 and realized 1.76 delay steps;
    fixed DR realized 3.89, and off 0. Last-4 mean reward/length were 17.73/210.6 for
    LUCID, 10.03/155.5 fixed, and 20.16/233.8 off. Thus LUCID is stable and materially
    better than starting at full DR (+76.8% reward), but below clean no-DR training
    (−12.0% reward). This is training behavior, not held-out robustness efficacy.
13. **Fair frozen-policy DR evaluation completes**
    (`curriculum_robustness_ne128_20260820_153754.json`): all nine checkpoints were
    evaluated with no learning on the same 102-motion content-dev panel and matched
    evaluation seeds 8700–8702. This is fresh-physics robustness, not unseen-motion
    generalization, because training used all 512 motions. The evaluator initially
    removed `push_robot` as a train-only event; that pilot is invalid for claims. The
    corrected runner retains pushes and live-audits all six terms, five delayed groups,
    configured ranges, quality channels, and checkpoint hashes.

    | cross-seed mean success | LUCID | fixed DR | no DR |
    |---|---:|---:|---:|
    | clean nominal physics | **83.99%** | 80.39% | 83.01% |
    | fresh full training-envelope DR | 54.25% | **56.54%** | 50.65% |
    | full DR + fixed 60 ms latency | 0.00% | 0.00% | 0.00% |

    LUCID preserves clean performance and improves full-DR success over no DR by 3.59
    percentage points, but trails fixed DR by 2.29 points and 2.67 progress points at
    the 32-iteration budget. Auxiliary batch diagnostics suggest fewer undesired contacts
    than both references under full DR (0.108 vs 0.112 fixed / 0.124 off), but slightly
    more slip and torque saturation than fixed and 10.5% higher energy. Those diagnostics
    include auto-reset environments after their scored motion terminates and are not a
    per-episode safety claim. At 60 ms, fixed survives longest
    (10.61% progress vs 8.30% LUCID / 7.93% off) but no arm completes any motion.
    Therefore SONIC's DR pipeline works and measures a real curriculum tradeoff; the
    present policies are not deployment-ready for 60 ms latency, and LUCID cannot be
    claimed superior to tuned fixed DR from this run.
14. **Post-hoc full-DR consolidation is rejected** (2026-08-20). Two preregistered,
    full-state continuations restarted the step-32 LUCID and fixed checkpoints, gave
    both arms equal compute at λ=1, and re-ran the identical frozen 102-motion
    clean/full-DR/60 ms evaluation. The 16-iteration receipts are
    `curriculum_consolidation_ne128_20260820_174016.json` and
    `curriculum_robustness_ne128_20260820_174608.json`; the four-iteration receipts are
    `curriculum_consolidation_ne128_20260820_182935.json` and
    `curriculum_robustness_ne128_20260820_183317.json`.

    | success / 60 ms progress | original step 32 | +4 full-DR iters | +16 full-DR iters |
    |---|---:|---:|---:|
    | LUCID clean success | **83.99%** | 79.41% | 76.80% |
    | LUCID full-DR success | **54.25%** | 51.31% | 51.96% |
    | LUCID 60 ms progress | 8.30% | 8.47% | **9.35%** |
    | fixed clean success | **80.39%** | 78.10% | 71.57% |
    | fixed full-DR success | **56.54%** | 55.88% | 49.35% |
    | fixed 60 ms progress | 10.61% | 10.78% | **12.04%** |

    No continuation produced a 60 ms success. Both doses regressed LUCID's absolute
    clean and full-DR success; the longer dose degraded fixed DR even more. Higher
    relative performance against a collapsing control is not an improvement. Retain
    the original step-32 checkpoints and discard both continuation checkpoint sets.
    The negative result closes abrupt post-hoc λ=1 dosing as the next method.
15. **Distributional latency audit and holdout are complete** (2026-08-21).
    `latency_curriculum_audit_20260820_231532.json` verifies that all nine original
    training arms had five live delayed actuator groups and six scalable DR terms.
    The actual latency process was independent per actuator group, sampled on each
    environment reset, and held for the episode. LUCID's realized delay tracked λ
    closely (Pearson 0.980–0.982), but its final observed maximum was six steps
    (30 ms); it did not train on shared transport delay or within-episode jitter.

    A preregistered 66-run discovery sweep crossed 22 latency/physics cells with all
    three retained policies. Fixed 60 ms is catastrophic, but it is not a sufficient
    robustness benchmark: episode-static, jittered, burst, common, and independent
    delays produced different rankings. Only nominal non-latency physics with shared
    per-episode uniform 0–60 ms delay passed the outcome-blind selection rule. It then
    failed to replicate against fixed DR on a disjoint 84-motion, 63-content-group
    holdout with three checkpoint seeds and fresh physics seeds.

    | holdout mean (sample sd) | LUCID | fixed DR | no DR |
    |---|---:|---:|---:|
    | success | 46.03% (4.81) | **46.43% (7.24)** | 44.05% (8.58) |
    | progress | 56.71% (3.27) | **58.29% (5.95)** | 55.27% (5.78) |

    LUCID-minus-fixed was −0.40 success points and −1.58 progress points, favorable
    in only one of three seeds. LUCID-minus-no-DR was +1.98/+1.43 points, favorable in
    two seeds, but descriptive 95% hierarchical-bootstrap intervals crossed zero
    ([−5.16,+9.13] and [−2.35,+5.33] points). Directional replication therefore
    fails. Receipts are `latency_distribution_discovery_ne32_20260820_232545.json`,
    `latency_distribution_confirmation_ne128_20260821_013440.json`, and
    `latency_distribution_analysis_20260821_042612.json`. This is fresh-physics evidence
    on training-seen motions, not unseen-motion, hardware, or real-world evidence.

**Defect ledger — the recurring lesson:** *a fake simpler than upstream hides live-only
defects; fakes must mirror upstream types AND orderings.* Live-found defects so far:
`_motion_fps` is a per-motion tensor (use `_sim_fps`); SONIC loads motions WITH
replacement (a global bin occupies several active positions); a sampler snapshot at
install captures only the prior (use `snapshot_at_step>0`); capsules held CUDA tensors;
a sensor/articulation body-index crossing made undesired-contact read 0.99 instead of
~0.16 and under-counted foot slip 16×; callback ordering starved the controller of gap
samples; off mode inherited fixed mode's λ=1 during warmup; capsule export dropped the
positional trainer state; resumed `max_steps` must be the absolute target, not remaining
iterations; actuator patching only works
at the `custom_instantiate` seam; copying the
parent actuator's `class_type` silently defeated the delayed subclass; SONIC evaluation
silently removes `push_robot` unless `train_only_events` is explicitly cleared; the
historical delay event sampled five actuator groups independently even though a shared
command-transport lag was assumed in the paper narrative. Audits must inspect
instantiated classes, aggregate process histograms, coupling, resampling cadence, and
active event terms, not config labels or a final lag snapshot.

---

## 5. What is NOT done (the actual frontier)

Ordered by value; A and B are the claim-bearing work.

**A. Train against the latency process actually expected at deployment.** SONIC is
functioning correctly, so MJLab is a fallback cross-simulator benchmark rather than a
repair. The next equal-compute study should use a shared command-vector lag, actual
0–60 ms support, and a preregistered curriculum over both amplitude and resampling
cadence; include episode-static and interval-jitter evaluation rather than optimizing one
selected cell. Compare process-aware LUCID against a matched fixed distribution and no
latency DR across three seeds. Keep the 2026-08-21 discovery and confirmation panels
closed to training decisions, and reserve the final test split. Do **not** append another
abrupt full-DR phase: both prior continuation doses failed. Before hardware deployment,
also measure the real end-to-end latency distribution and add episode-masked physical-
quality metrics.

**B. The screening campaign → Gate A → Gate B (practice-utility track).**
L0 is resolved for the actual paired protocol: both branches must use symmetric fresh
restarts from one capsule. Never mix an uninterrupted arm with a restarted arm.
1. ✅ Re-measure throughput on the idle GPU: observer throughput is 3603.5 env-steps/s,
   native is 3725.9, and receipts are written.
2. Re-size and launch `probe_screen_v1_late` (paired control/intervention branches from
   settled origins, last-4 efficacy).
3. `build_utility_labels.py` → Gate A (identifiability vs the 3.33% floor) → Gate B
   (does the latent-gap proxy predict utility labels?).
4. **Only if Gate B passes**: build the estimator, then the residual allocator, per plan
   §4.7–4.8. If Gate A fails, the honest deliverable is the audit paper (negative/
   methodological result) — that is an acceptable outcome of this program.

**C. Hygiene:** bitwise no-op parity, warmup parity, and symmetric restart identity pass.
Uninterrupted-vs-resumed identity remains unsupported because the capsule cannot restore
live simulator/episode state; do not use that asymmetric design.

**D. Bookkeeping:** ✅ §25 now records the 2026-08-19/20 curriculum, throughput, latency,
correction, and frozen-policy DR-evaluation results; §24.5 remains as historical state at
the time it was written.

---

## 6. Rules of engagement (violating these invalidates results)

1. **Never modify upstream files** in `GR00T-WholeBodyControl` — research namespace +
   runtime patching only. `git diff --stat main...HEAD` must show only
   `research/`, `scripts/practice_utility/`, `tests/practice_utility/`, docs.
2. **Every experiment writes a JSON receipt** to `/data/robotixx/lucid-sonic/manifests/`
   with config, seeds, git SHA, and a `verified` / `not_yet_verified` split.
3. **Gates are law**: no estimator, no allocator, no learned scheduler before Gate B.
4. **Branches start from settled checkpoints; efficacy is last-4-averaged.** Cold-origin
   comparisons are noise.
5. **Fakes mirror upstream types and orderings** (tensors where upstream has tensors,
   with-replacement sampling, real callback order). CPU tests must stay green: run
   `pytest tests/practice_utility/` (needs the env sourced, PYTHONPATH unset).
6. **Report failures faithfully** — a gate that fails or an arm that loses is a result,
   not a bug to massage. Performer and content splits are reported separately, always.
7. The GPU is shared. Check `nvidia-smi` before launching; use the free-memory-gated
   driver pattern (`outputs/lucid_full_driver.log` came from such a script). Don't kill
   other users' jobs; audit and report instead (see `gpu_occupancy_audit.json`).

---

## 7. Prompt for Codex (copy-paste from here down)

```
You are continuing an active robotics research program (LUCID: counterfactual practice
utility + a latent-gap-driven DR curriculum for the SONIC humanoid whole-body-tracking
policy). A previous agent built and live-verified all the infrastructure; your job is to
run the claim-bearing experiments and keep the discipline.

FIRST, read these files end to end before running or editing anything:
1. /home/robotixx/lucid/lucid-handoff-2026-08-20.md   (current state, results, rules)
2. /home/robotixx/lucid/lucid-design-implementation-plan.md  (full design, gates, §0-24)

Working copy: /home/robotixx/lucid/GR00T-WholeBodyControl, branch research/practice-utility.
Environment: `source /data/robotixx/lucid-sonic/lucid_env.sh` before ANY python; never
bypass it (TMPDIR/PYTHONPATH/hydra gotchas are documented in the handoff §2).
Sanity check before starting work: `pytest tests/practice_utility/` must pass (CPU-only),
and `git diff --stat main...HEAD` must touch no upstream files.

Hard rules (from handoff §6): never edit upstream SONIC files; every experiment writes a
JSON receipt to /data/robotixx/lucid-sonic/manifests/ with config, seeds, git SHA, and an
explicit verified / not_yet_verified split; no estimator/allocator/learned scheduler
before Gate B passes; branches start from settled checkpoints and efficacy is averaged
over the last 4 iterations; report negative results faithfully; check nvidia-smi and gate
launches on free GPU memory (the RTX 5090 is shared; PhysX needs a fixed ~640 MB contact
buffer and Isaac Sim ~6 GB to start).

Work queue, in order (details and file paths in handoff §5):
1. ✅ Idle-GPU throughput measured: native 3725.9 and observer 3603.5 env-steps/s at
   256 envs; observer penalty 3.28%; receipts are in the manifest directory.
2. ✅ Corrected fixed-lambda latency A/B completed. Live λ=1 lag averaged 18.4 ms and
   last-4 reward fell 35.8%; see `latency_ab_ne256_20260820_112516.json`. Earlier
   six-channel claims were corrected because the base `class_type` defeated the delayed
   subclass.
3. ✅ Diagnose the first-iteration divergence: off incorrectly started at λ=1 during
   warmup. It now starts at zero; a live lucid/off pair matched exactly through all three
   treatment-free rollouts (`curriculum_warmup_parity_ne128_20260820_114047.json`).
4. ✅ Corrected three-arm curriculum retraining completed: 3 modes × 3 seeds × 32
   iterations, nine exported checkpoints, six live DR channels, and bounded integral
   contribution. See `curriculum_comparison_ne128_20260820_143058.json`.
5. ✅ L0 passes for symmetric fresh restarts from one capsule at zero tolerance. Seamless
   uninterrupted-vs-resumed identity remains unsupported. Re-size and launch the probe
   screening campaign (probe_screen_v1_late), then
   build_utility_labels.py -> Gate A -> Gate B. Only a Gate B pass authorizes building
   the estimator (plan §4.7); a Gate A failure is a reportable negative result, not a
   defect.
6. Hygiene: ✅ bitwise no-op parity, warmup parity, and symmetric restart identity.
   Retain the asymmetric resume failure as evidence for the unsupported contract.
7. ✅ Frozen-policy evaluation completed on all nine checkpoints. LUCID success was
   83.99% clean, 54.25% full DR, and 0% at 60 ms; fixed DR was 80.39%, 56.54%, and 0%.
   See `curriculum_robustness_ne128_20260820_153754.json`. SONIC works; do not pivot to
   MJLab merely because current policies fail beyond-range latency. The deployment
   blocker is now the 60 ms robustness gap.
8. ✅ Abrupt post-hoc full-DR consolidation was tested at +4 and +16 equal-compute
   iterations and rejected. LUCID clean/full-DR success became 79.41/51.31% and
   76.80/51.96%, respectively; 60 ms success stayed zero. See
   `curriculum_robustness_ne128_20260820_{183317,174608}.json`. Retain the original
   step-32 checkpoints. A future curriculum must use a preregistered smooth in-budget
   ramp and actual 0–60 ms training support, not another hard continuation.
9. ✅ The latency-process audit and preregistered distribution sweep are complete.
   Historical training used independent actuator-group lags sampled per episode, not a
   shared or jittered transport delay. Only shared per-episode U(0,60 ms) advanced from
   22-cell discovery, and it failed holdout replication against fixed DR: mean success/
   progress were 46.03/56.71% LUCID, 46.43/58.29% fixed, and 44.05/55.27% off. See
   `latency_distribution_analysis_20260821_042612.json`. Do not claim a general LUCID
   latency advantage. The next study is process-aware, equal-compute retraining with
   shared 0–60 ms support and explicit cadence variation; MJLab remains a later
   cross-simulator check.

When you finish any item, write the receipt, update the plan doc changelog, and summarize
what was verified vs still open. If a measurement contradicts the handoff, trust the
measurement, say so explicitly, and update the plan doc.
```
