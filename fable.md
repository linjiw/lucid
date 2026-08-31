# Fable's Guidance — LUCID → ICRA
**Originally written 2026-08-26 from results through 2026-08-21 04:30; live execution
checkpoint updated through the Aug. 27 CPU-contract and preregistration freeze.**
Sources reviewed: `lucid-handoff-2026-08-20.md` (fully updated through §25.10),
`lucid-design-implementation-plan.md` §25.1–25.10, the manifest directory
(`/data/robotixx/lucid-sonic/manifests/`, including the Aug. 26 origins/v2 manifest and
the Aug. 27 passive-dose/directional sidecars), and the `research/practice-utility`
branch state through `8a79ce7`.

**ICRA 2027 deadline (verified 2026-08-26):** contributed papers are due
**Tuesday, September 15, 2026 at 11:59 PM Pacific Time** (the official CFP labels the
zone "PST"). The initial manuscript is limited to **8 total pages, including references,
acknowledgments, figures, and tables**; papers over eight pages are returned without
review, and no extension is planned. The internal submission target is **September 14**.
The initial PDF must also use the ICRA double-column format and follow double-anonymous
review (omit authors and affiliations). The conference is May 24–28, 2027 in Seoul.
Sources: [official ICRA 2027
CFP](https://2027.ieee-icra.org/contribute/call-for-icra-2027-papers-now-accepting-submissions/)
and [IEEE RAS ICRA schedule](https://www.ieee-ras.org/conferences-workshops/fully-sponsored/icra/).

## Execution checkpoint — 2026-08-27 (live update)

- ✅ The full focused CPU suite passes: **1,126/1,126 tests** (one existing deprecation
  warning).
- ✅ The previously dirty Aug. 20–21 code is now preserved in two scoped commits:
  `b42b8b1` (latency/parity/restart identity) and `8e59857` (curriculum robustness,
  consolidation, and latency-distribution audits). Historical receipts still identify
  the exact dirty-run lineage with git SHA `811f084` plus launcher hashes; the new
  commits do not retroactively replace those hashes.
- ✅ The Track-A hardening is preserved in scoped commits: `c411d57`
  (hash-bound origins/manifests), `b747fb9` (fail-closed claims), `35ac757` (readiness
  audit), `2bfcb6f` (with-replacement resident-context canonicalization), and `0e9ba29`
  (settled-origin outcome record). Three later commits freeze the next contracts:
  `36b2776` (directional latent test), `49aea91` (horizon-scaling orchestration), and
  `8a79ce7` (passive shared-control dose measurement and live-smoke driver).
- ✅ Two matched, full settled origins were generated from clean commit `2bfcb6f` at
  absolute step 56. Both passed the frozen stability rule; their hash-bound origin map
  contains **652 common resident contexts** and is usable for outcome-blind manifest
  selection. Receipt:
  `/data/robotixx/lucid-sonic/manifests/probe_origins_ne256_20260826_122253_365435.json`.
- ✅ A new outcome-blind 24-context candidate manifest was frozen from that intersection:
  `probe_screen_v2_late_20260826.json` (logical manifest hash `17c178dc4c4f5a0d`,
  48 intervention branches + 2 seed-shared controls). Its creation receipt
  records clean Git state and byte-level pool, split, origin-map, and snapshot lineage.
- ✅ The outcome-blind passive-dose plan is frozen at
  `/data/robotixx/lucid-sonic/manifests/probe_screen_v2_late_20260826.passive_dose_plan_v2.json`
  (24 contexts; logical SHA `cc0954da50531a5a`; file SHA `6ae450d25693ebb4`). It was
  created from the exact v2 manifest on clean commit `8a79ce7`, without reading results.
- ✅ The leakage-free directional decision rule and design are frozen at
  `/data/robotixx/lucid-sonic/manifests/probe_screen_v2_late_20260826.directional_calibration_preregistration.json`.
  It binds a univariate affine-ridge test to deterministic 5×4 nested
  motion-family-held-out folds, a same-unit q95 noise deadband, family-macro metrics,
  and a hierarchical family/context bootstrap (algorithm SHA `ee1b857650749c4b`). The
  outcome-free v2 design is feasible: 48 rows, 24 contexts, 10 families, 5 rankable.
- ✅ Track B now has a claim-facing orchestrator in `49aea91` with exclusive immutable
  preregistration, hash-bound inputs, atomic incremental status/receipts, verified
  resume, and a three-sample idle-GPU gate that requires zero compute processes. Do not
  bypass it with `run_curriculum_comparison.py`. The Track-B preregistration sidecar and
  every new GPU branch/outcome remain **pending**.
- ⚠️ GPU occupancy is volatile. The earlier Aug. 26 `openpi` occupancy snapshot later
  cleared, but that is not launch authorization. Re-run the strict gate immediately
  before every simulator branch and recheck disk headroom before Track B.
- ⛔ **Do not launch `probe_screen_v1_late` with the current runner.** The frozen
  manifest was selected from a 256-environment step-20 resident sampler, while the only
  capsule proven for symmetric restart is a different 128-environment step-10 origin.
  That capsule does not serialize the resident motion/bin mapping, so it cannot prove
  that the 24 frozen contexts are present after restart. The runner also predates the
  capsule-resume result and lacks branch receipts.
- ⛔ The claim label path now fails closed instead of silently using its old exploratory
  fallback. It writes a blocked, non-claim receipt and does not assemble labels or run
  Gate A or the directional latent-proxy decision until the ready preflight and
  evaluation lineage exist. The exploratory mode still falls back to training reward
  and synthetic zero harms and must never enter a claim table. Also keep two decisions
  distinct: **latent-proxy predictiveness** (the paper claim) and **estimator
  authorization** (the code's inverse decision: authorized only when no simple proxy
  suffices).
- ⛔ No claim campaign launcher yet consumes a ready preflight's exact `BranchSpec` and
  writes atomic per-branch receipts. The low-level runner permits execution only with an
  explicit exploratory acknowledgement; this is an additional stop even after the data
  artifacts are frozen.

The fail-closed runner, origin/manifest builders, label boundary, campaign preflight,
passive-dose path, directional test, and Track-B orchestrator now exist and pass the CPU
suite. Their audit established two design facts that remain in force:

- The counter-stream helpers have no production call sites. Symmetric restart identity
  remains valid for unchanged branches, but an intervention that changes the trajectory
  does **not** have verified channel-wise common random numbers. The honest estimand is
  therefore a stochastic potential-outcome difference with a same-estimand empirical
  floor.
- `PracticeSamplerAdapter.record_completion()` is now wired, behind claim-mode seams, to
  SONIC's once-per-simulation-step `update_adaptive_sampling`. The callback records a
  dataset-global completed-step histogram, verifies the registry at receipt time, and
  projects the histogram through all 24 frozen kernels for intervention and shared
  control branches. This preserves the 48-intervention + 2-shared-control screen and
  does not intentionally change its sampling distribution. **CPU contracts are not live
  evidence:** the hash-bound CUDA shared-control smoke has not yet produced a passing
  receipt. That narrow smoke also does not claim paired no-callback bitwise identity,
  trajectory equivalence, intervention efficacy, or any treatment effect.

Immediate correction: the hash-bound settled origins and outcome-blind v2 context
selection, passive-dose plan, and directional design are complete. Next, run and pass the
live CUDA shared-control dose smoke; then freeze the per-context encoder/proxy features,
deployment-`J_eff` evaluator, same-estimand floor, and complete gate/evaluation
preregistration. A claim launcher must still consume the ready preflight's exact
`BranchSpec` objects and write atomic branch/evaluation receipts. The existing v2
preflight audit is intentionally `blocked`; the quoted ~1 GPU-hour remains a plausible
*branch-training* cost, not authorization to run an invalid campaign.

---

## Fable review — 2026-08-27: Codex progress, and how TACE fits

### A. Codex progress (Aug 26 → Aug 27): infrastructure is ahead of evidence

**Done, and genuinely good:** ten scoped commits (`b42b8b1`…`8a79ce7`), 1,126 CPU tests,
the Aug 20–21 dirty work preserved, hash-bound settled origins at step 56, an
outcome-blind 24-context v2 manifest, a frozen passive-dose plan, a frozen leakage-free
directional test, and a horizon-scaling orchestrator. These remove real degrees of
freedom and are the right *kind* of work.

**Not done:** a single GPU result. In 24 hours Track A cleared blockers and grew new ones
at the same rate (v1 manifest invalidated → v2 built → live dose smoke pending → claim
launcher missing → `BranchSpec` consumption missing). Track B's orchestrator exists but
its idle gate demands **≥28 GB free and zero compute processes** — at the moment of this
review the shared 5090 shows 22 GB used and 98% utilization from another user, so that
gate cannot pass and the study cannot start. Sept 1 is five days away and both tracks
have zero outcomes.

**Directives (override earlier text where they conflict):**

1. **Infrastructure freeze.** No new fail-closed gates, wrappers, orchestrators, or
   contract sidecars until a GPU receipt exists. Codex's next deliverable is a receipt,
   not a commit.
2. **Relax the Track-B GPU gate** to the free-memory gate every other driver already uses
   (`--min-free-mib` ≈ 12,000; Isaac needs ~6 GB + PhysX 640 MB + 256 envs). Drop
   `require_zero_compute_processes`. Log contention in the receipt; training metrics
   are valid under contention (handoff §2), only wall-clock is not.
3. **Track A: the live passive-dose smoke is the single next action.** If the claim
   launcher is not finished by Aug 29, run the v2 screen with `run_branch.py` under
   the exploratory acknowledgement, label every receipt `screen-grade`, and run Gate A
   on it. A screen-grade answer to "are utility labels identifiable?" on Sept 1 is
   worth more than a perfect launcher on Sept 5. Paper-grade confirmation on the
   retained subset can follow with pair-specific RNG if Gate A passes.
4. **Trim Track B** before it launches: budgets **32 / 128 / 256** (drop 64), export the
   final checkpoint plus intermediates at fixed fractions only, and benchmark one
   evaluation branch before freezing panel sizes. The 74 GB / 90 GiB disk estimate is a
   symptom of over-exporting.

### B. What the three documents say — and what they mean here

Saved to `~/lucid/docs/`: `tace-target-anchored-curriculum-exposure.md`,
`lucid-mc-iros-design-plan.md`, `curriculum-learning-cross-domain-review.md`.

**The literature review's core, in one line:** in a dense-reward regime where the
target distribution is learnable, a curriculum that *replaces* the training
distribution loses to mixed training; curricula that win **expand rather than replace
support, sample by learning progress, retain/replay mastered strata, and finish on the
full target mixture** (ADR, Rudin's terrain loop-back, SPRL/CURROT, PLR, DeepSeek-R1's
final stage). **Our data agrees exactly.** LUCID's intensity curriculum is
"expand-not-replace" by construction (nominal is always inside [φ₀ ± λΔ]), but it never
reached the target support — terminal λ = 0.756, maximum observed latency 30 ms of a
40 ms envelope — and it trails the mixed comparator (`fixed`, λ = 1 throughout) on
full-DR success by 2.29 pts while beating it on clean by 3.6 pts. That is a
distribution-support gap, which is precisely TACE's RQ1. TACE is therefore not a new
direction; it is the **minimal fix to the one measured deficit** of the curriculum you
already have.

**TACE → SONIC mapping (verified against the branch, Aug 27):**

| TACE concept | SONIC `research/practice-utility` reality | Work needed |
|---|---|---|
| Mixed PPO / `p_target` | `fixed` mode (λ = 1 sampler) — exists, is the comparator | none |
| Sequential (deterministic ramp) | does not exist; `lucid` is the adaptive analog | **skip TA-SEQ**; test TA-LUCID directly |
| Anchor cohort (α of envs at `p_target`) | λ is **global** — `dr_scaling.apply_lambda` rescales event-term ranges once | per-env λ: sample every reset-safe term and `sample_action_lags` at full support, then apply the per-env affine shrink x ↦ φ₀ + λ_env·(x − φ₀); anchor envs λ_env = 1; seeded fixed permutation in the receipt |
| Focus-only controller feedback (§4.6) | `observer.drain_gaps()` returns unlabeled floats | env-indexed gaps + cohort mask; **mandatory**, otherwise anchor envs' larger gap drives λ down — TACE's own warning |
| TA-YOKED | curriculum jsonl already logs λ per step | new mode `yoked` that replays a λ trajectory file — cheap |
| Final-10% target-only consolidation (§4.5) | **already tested and rejected** as an abrupt post-hoc phase (§25.9: both arms regressed) | treat consolidation as a *tested variable* (with/without), never an assumption; the §25.9 negative is prior evidence on H3 |
| Robustness profile s ∈ {0…1.25} (LUCID-MC E1) | `run_latency_distribution_sweep.py` already sweeps non-latency DR scale {0, 0.5, 1}; presets are `id_clean` / `dr_full` / `latency_60ms` | extend the grid to {0, 0.25, 0.5, 0.75, 1.0, 1.25}; report AUC + worst-bin + hierarchical bootstrap (already in the analysis script) |
| Retention / forgetting curve (E3, TACE §7.4) | horizon study exports checkpoints at each budget | evaluate every exported checkpoint on the clean panel — the retention curve is free |
| LUCID-MC per-channel λ + probe envs | same per-env-λ machinery, with a λ *vector* per env | **do not build for ICRA** — but implement λ_env as a per-channel vector now so MC is a config change for the next paper |
| Real-robot ≥50 trials, 1,400 GPU-h matrix | not achievable before Sept 15 | out of scope; cite as future work |

### C. The experiment: fold TACE into Track B as two extra arms

Do not run TACE as a separate campaign. Add arms to the horizon study so every
comparison shares seeds, origins, budgets, and panels:

- **Arms:** `fixed`, `lucid`, `off` (existing) + **`ta-lucid-25`** (α = 0.25 anchor,
  focus-only feedback, no consolidation) + **`ta-yoked-25`** (same anchor, replays the
  paired `ta-lucid-25` λ log). Optional if the seed-8600 smoke is clean: `ta-lucid-50`,
  and `ta-lucid-25+cons` (final 10% at λ = 1) as the consolidation test.
- **Budgets 32 / 128 / 256, five seeds, 256 envs, settled origin, six channels.**
  Cost ≈ (32+128+256) × 5 arms × 5 seeds ≈ 10,400 iterations ≈ 5 h idle, 15–30 h
  contended, plus evaluation. Contention trim rule (preregister it): drop budget 32 for
  the new arms and run `ta-yoked` at 256 only.
- **Primary endpoint:** full-DR success on the frozen 102-motion content-dev panel;
  **co-primary:** robustness-profile AUC over s ∈ {0…1.25}. Secondary: clean success,
  worst-bin success, retention curve, realized per-cohort dose.
- **Preregistered hypotheses:**
  - **H-A (headline):** `ta-lucid-25` is non-inferior to `fixed` on full-DR success
    (margin 2 pts) *and* superior on clean success by ≥ 2 pts.
  - **H-B (attribution):** `ta-lucid-25` > `ta-yoked-25` → online gap feedback matters;
    tie → the schedule shape/dose explains it, and say so.
  - **H-C (horizon):** `fixed` clean success declines from 32 → 256; TA arms do not.
- **Implementation is one Codex day:** per-env λ shrink in `events_reset_safe.py` and
  `sample_action_lags`, cohort tags + seeded permutation, env-indexed gaps with a focus
  mask in the observer/controller path, `yoked` mode, CPU tests mirroring upstream
  tensor shapes and orderings (the recurring lesson), then a 16-iteration seed-8600
  smoke whose receipt must show exact cohort sizes, per-cohort realized dose, and
  controller samples drawn from focus envs only.

**Sequence:** Aug 27 implement + smoke → Aug 28 launch Track B with TACE arms under the
relaxed gate, and pass the Track-A live dose smoke → Aug 29 v2 screen (claim launcher or
`run_branch.py` fallback) → Aug 30–31 evaluation + robustness profiles → **Sept 1
decision**.

### D. Consequence for the paper

If H-A holds, Path 2 gets the principled story the literature review hands you:
*"expand, retain, and anchor to the target"* — LUCID's latent gap is the focus
scheduler, the anchor cohort supplies persistent target support, and the audit
protocol is the backbone. Working title: *Target-Anchored, Gap-Gated Domain
Randomization for Humanoid Whole-Body Tracking*. If H-A fails but H-C holds, the
horizon result still carries Path 2. Path 1 (practice utility) is unchanged and still
decided by Gate A + the directional test. LUCID-MC, LUCID-Replay, shared-lag 0–60 ms
retraining, and hardware trials are the next paper — name them in Future Work, do not
start them.

---

## 0. TL;DR

You are **experiment-rich and claim-poor**, and the deadline math has flipped in your
favor: when the shared GPU is idle, the measured throughput makes every remaining
experiment 30–80× cheaper than when the campaign was sized. The single most important
fact in the whole program right now:

> **The claim-bearing experiment of the entire program — the probe screen → Gate A →
> latent predictiveness — has never been run; after its remaining live measurement
> contracts pass, branch training is likely ~1–2 serial GPU-hours.**

Everything else you've done in the last week was hygiene, mechanism validation, and
(honest, valuable) negative results. None of it is yet a paper headline. Gate A plus the
directional latent-proxy decision determines which of two papers you are writing, so
**run the valid campaign this week, before anything else**. In parallel, preregister and
launch the one curriculum experiment that can produce a positive headline: the
**horizon-scaling study** (§3.3 below), which your own consolidation data already hints
will favor LUCID.

Decision date: **Sept 1**. Paper path locked by then; writing starts no later than
Sept 5. The external deadline is Sept 15 at 11:59 PM Pacific Time; submit internally by
Sept 14 to retain one day of slack.

---

## 1. Honest inventory — what you actually have

### Assets (claim-bearing or audit-grade, receipted)

1. **A restart/audit foundation that survives zero-tolerance L0 checks.** No-op parity,
   warmup parity, and unchanged symmetric-restart identity all pass exactly; the
   asymmetric resume design was *proven* unsupported and replaced with two fresh
   restarts from one capsule. The 3.33% settled / 10.62% cold floors remain useful
   training-side evidence, but the paper's utility floor must be remeasured in the same
   deployment-`J_eff` and dose-normalized units. This is the methodological backbone,
   not yet a completed causal screen.
2. **The LUCID premise, live:** latent gap fell 10× while raw joint mismatch fell only
   1.5× over adaptation — the frozen encoder sees learning that joint-space metrics
   miss. (This motivates the directional latent-proxy decision but does not substitute
   for it.)
3. **A working gap-driven DR curriculum with a real, measured tradeoff:** LUCID trains
   stably where fixed full DR collapses training (+76.8% reward), preserves clean
   deployment success (83.99% vs fixed's 80.39%), gains +3.59 pts full-DR success over
   no-DR, but trails tuned fixed DR by 2.29 pts at the 32-iteration budget.
4. **A genuinely novel empirical finding about latency:** *maximum latency is not a
   robustness specification.* Fixed 60 ms is uniformly catastrophic, distributed
   delays are far less destructive, and the latency *process* (shared vs independent,
   static vs jittered, cadence) **changes the policy ranking**. This is §25.10's real
   contribution and it generalizes beyond LUCID.
5. **Three clean negative results** (scalar-λ dead; post-hoc λ=1 consolidation rejected
   with preregistered keep-conditions; the retained policies have no broad latency
   advantage on a disjoint holdout). These buy you reviewer trust and Related-Work
   sharpness; they are not headlines.
6. **Outcome-free measurement and analysis contracts are now frozen.** The v2 passive
   plan binds all 24 contexts to one exact global-bin projection, and the directional
   sidecar freezes a feasible motion-family-held-out test before any utility outcome is
   read. These remove degrees of freedom; they are not Gate-A or predictiveness results.

### Gaps (what blocks a paper today)

- **No Gate-A or directional latent-proxy result.** The program's central question — is
  counterfactual practice utility identifiable, and does the latent gap predict it? —
  is untested.
- **No passing live passive-dose smoke or claim launcher.** The CPU path and frozen plan
  are complete, but a live shared-control receipt, ready preflight, and atomic
  branch/evaluation campaign still separate code readiness from a causal result.
- **No positive differentiated result for the curriculum.** At 32 iterations LUCID
  does not beat tuned fixed DR on robustness. As it stands, the curriculum section is
  "interesting mechanism, honest tie."
- **All deployment evaluation is on fine-tuning-seen motions** (debug512, fresh physics
  only). The 4950-pool performer/content splits overlap debug512 and SONIC pretraining
  provenance is not yet closed, so a filtered panel may be called unseen during LUCID
  fine-tuning—not globally policy-unseen—unless that lineage is established.
- **Three seeds cannot support inference** — your own analysis notes a sign-flip test
  cannot reach p<0.25 with three blocks. Headline tables need **5 seeds minimum**.
- **The Aug. 20–21 dirty work is now preserved** in `b42b8b1` and `8e59857`.
  Historical receipts continue to cite dirty SHA `811f084` plus launcher hashes; do not
  rewrite that provenance as if the later preservation commits produced the runs.

---

## 2. The strategic read

The old sizing (31.4 GPU-hours under contention) made the probe screen feel like a
capstone to be earned. At the measured 3,600 env-steps/s idle rate it is **an
afternoon**. Meanwhile the
32-iteration curriculum budget — chosen under the same contention assumptions — is the
main reason the curriculum result is a tie: 32 iterations structurally favors fixed DR
(it front-loads exposure to the full envelope and hasn't had time to pay the
instability cost). Your own consolidation study is the tell:

> With +16 additional full-DR iterations, **fixed DR degraded from 80.39% → 71.57%
> clean and 56.54% → 49.35% full-DR**, while LUCID's controller — by construction —
> never exposes the policy to more DR than the gap justifies.

That is a testable, mechanistic hypothesis with a plausible positive answer:
**fixed DR is unstable over long horizons; gap-gated DR matches its robustness while
preserving clean performance as budget grows.** If the crossover exists, the headline
figure (success vs training budget, three arms, shaded seed-bands) draws itself.

So the strategy is a two-track race with a forced decision on Sept 1:

- **Track A (practice utility):** corrected probe screen → labels → Gate A → directional
  latent predictiveness. Likely ~1–2 GPU-hours of branch training after the remaining
  preflight blockers, plus evaluation and analysis. Decides the paper's identity.
- **Track B (curriculum):** horizon-scaling study + evaluation on content unseen during
  LUCID fine-tuning + 5 seeds. ~1–2 GPU-days total. Produces the positive result Track
  A's failure modes would need, and strengthens the paper even if Track A succeeds.

Do **not** start the process-aware 0–60 ms shared-lag retraining (handoff frontier
item A) before these two. It requires new mechanism code (shared command-vector lag +
cadence curriculum), new preregistration, and its predecessor just failed holdout —
it is the *right* follow-up science but the *wrong* three-weeks-to-deadline bet. It
goes in the paper as future work / analysis, not as a headline dependency.

---

## 3. This week, in order

### 3.1 Aug 26–27 — housekeeping and contract freeze

1. ✅ Preserve the staged work on `research/practice-utility`. The Aug. 20–21 work,
   Track-A hardening, directional design, horizon orchestrator, and passive-dose path are
   now in scoped commits through `8a79ce7`; **1,126 focused tests pass**, and no
   previously tracked upstream files were modified or deleted relative to main.
2. ✅ Verify the exact ICRA 2027 submission deadline and page limit; they are recorded
   at the top of this file.
3. ⚠️ `nvidia-smi` must be rechecked before every launch. Occupancy changed during Aug.
   26, so no earlier snapshot authorizes a later run; all sizing below assumes the prior
   ~3,600 env-steps/s idle measurement.

### 3.2 Track A — origins → corrected screen → Gate A → latent test (Aug 26–28)

- ✅ Treat `probe_screen_v1_late` as a frozen historical selection artifact, **not a
  launch manifest**. Two full, pool-bound origins now exist at step 56, and
  `probe_screen_v2_late_20260826.json` selects 24 contexts from their 652-context
  intersection without reading utility outcomes. This is a candidate selection manifest,
  not yet launch authorization.
- ✅ Passive completion accounting is now wired into the verified SONIC per-step path,
  and the exact 24-context hash-bound dose plan is frozen. CPU tests cover exact totals,
  registry stability, zero-drop fail-closed behavior, and shared projection through the
  same frozen kernels for intervention and control branches.
- ⛔ The live CUDA shared-control smoke is still pending. It must produce nonzero exact
  `H_s` totals, exact hook/observation counts, epsilon-zero control identity, a stable
  registry, zero dropped batches, and exact 24-context coverage. The narrow smoke does
  **not** establish paired no-callback distribution or trajectory identity and does not
  test intervention efficacy; keep those limits explicit.
- Keep the 50-branch v2 screening design. Repeating 48 epsilon-zero controls from the same
  two origin capsules would not create 48 independent streams because pair-key RNG is not
  integrated; genuine context-paired controls require a new RNG-fork protocol and belong
  in paper-grade confirmation on the retained subset.
- ✅ The complete leakage-free directional test is frozen before outcomes: folds, seeds,
  ridge grid, deadband source, metrics, bootstrap, and decision rule are all hash-bound
  in the directional sidecar. Still freeze the per-context latent features at the
  origins, deployment-side `J_eff` evaluation receipts, and same-estimand noise floor.
- Only then launch symmetric fresh restarts with last-4 efficacy and atomic receipts per
  branch. `build_utility_labels.py` must hash-link the manifest, ready preflight, H_l
  policy/capsule, dev suite, physics seeds, and evaluation receipt before it may mark an
  output claim-grade.
- Gate A asks whether utility labels are identifiable above the **same-unit** floor;
  latent-proxy predictiveness is a separate paper decision; inverse estimator
  authorization remains the opposite-direction machinery gate. Preregister the shared-
  control screen as a two-seed-block multi-arm design with context-grouped folds and
  seed/context-clustered resampling. With only two seed blocks, it is a screening/effect-
  size decision; a paper-grade causal claim needs fresh context-paired confirmation.

### 3.3 Track B — horizon-scaling curriculum study (launch only after freeze and gates)

The claim-facing orchestrator is implemented and CPU-tested, but its campaign
preregistration sidecar and every new GPU result are still pending. First run its default
dry mode to reserve and freeze the exact campaign; only then use `--resume --execute`
after the GPU and disk gates pass.

- **Arms:** lucid / fixed / off (unchanged code paths, six channels, corrected
  actuators).
- **Budgets:** 32 / 64 / 128 / 256 iterations. The orchestrator audits the sealed
  historical 32-iteration seeds 8600–8602 for exact command/config compatibility and
  artifact integrity, then adds new seeds 8603–8604. It preserves the historical dirty
  SHA `811f084` and different launcher digest as a separate lineage stratum rather than
  pretending the later clean launcher produced those runs.
- **Seeds:** five per (arm, budget). Budgets 64/128/256 use seeds 8600–8604; the combined
  32-iteration cell uses the three sealed historical seeds plus two new seeds. One
  deterministic campaign index spans every new budget, seed, and arm.
- **Evaluation:** the frozen-policy evaluator on (a) the existing 102-motion
  content-dev panel — clean + full-DR presets (drop the fixed-60 ms cell from the
  headline; keep it as an appendix limitation), and (b) **a frozen, bounded 4950-pool
  panel with exact debug512 overlaps removed**. Call this unseen during LUCID
  fine-tuning unless SONIC pretraining lineage supports a stronger statement. Report
  performer and content splits separately, as always.
- **Cost estimate:** the frozen implementation specifies **51 new branches / 6,912
  training iterations**. Training is roughly 4–5 h under the optimistic idle rate or
  ~12 h at the older measured rate. Evaluation is additional and can dominate: benchmark
  it first, then freeze bounded, non-overlapping panels rather than assuming the full
  4950 dev pools fit in one night. The training artifacts alone are estimated at ~74 GB;
  require at least 90 GiB free immediately before launch because the orchestrator does
  not yet enforce a disk-space gate.
- **Hypothesis to freeze in the training preregistration:** at 256 iterations, LUCID's
  full-DR success is non-inferior to fixed DR while its clean success is superior; fixed
  DR's clean success degrades with budget. The numerical non-inferiority margin, exact
  deployment panels, and analysis rule belong in a separate evaluator preregistration
  before any deployment outcome is opened. If the curves do not cross or converge,
  report that faithfully—the tie at 32 iterations then stands.

### 3.4 Sept 1 — decision point

Sit down with both receipts and pick the paper (see §4). Freeze the method and
experiment list. Anything not started by Sept 3 does not go in the paper.

---

## 4. The two papers (write one, salvage from the other)

### Path 1 — latent predictiveness passes: the practice-utility paper

**Working title:** *Counterfactual Practice Utility: Auditing What Motion Practice
Actually Buys a Humanoid Whole-Body Controller.*

Claims, in order of load-bearing:
1. A causal screening protocol plus fresh context-paired confirmation for measuring the
   deployment value of steering practice toward specific motion bins — with zero-
   tolerance restart identity, passive realized-dose accounting, measured same-estimand
   floors, settled origins, and preregistered gates.
2. Practice-utility labels are identifiable above the seed-noise floor (Gate A), with the
   screening effect replicated under fresh pair-specific streams for any paper claim.
3. A frozen latent-space gap predicts counterfactual utility — the LUCID
   premise, finally tested causally rather than correlationally.
4. (Only if time permits, and only if the latent-proxy decision passes:) a minimal
   preregistered greedy/top-k reallocation demo using the frozen proxy. This does **not**
   authorize a learned utility estimator; inverse-estimator authorization is a separate,
   opposite-direction gate. Do not build that estimator in three weeks.

The curriculum work appears as one section: an application of the same latent-gap
signal to DR scheduling, with the horizon-scaling figure and the honest fixed-DR
comparison. The latency-process finding (§25.10) becomes a strong subsection of the
evaluation ("what 'robustness' even means depends on the latency process").

### Path 2 — Gate A or latent predictiveness fails: the curriculum + audit paper

**Working title:** *Gap-Gated Domain Randomization: an Anytime Curriculum for Humanoid
Whole-Body Tracking, Audited.*

This path is only viable if Track B produces the crossover (or at least clean
non-inferiority + fixed-DR degradation at long horizons). Claims:
1. A latent-gap PI controller that schedules six DR channels (including actuation
   latency) and provably (live-audited) moves the physics it claims to move.
2. Fixed full-strength DR degrades with training budget; gap-gating matches its
   robustness while preserving clean performance and training stability (horizon
   figure = Fig. 1).
3. Generalization results on content unseen during LUCID fine-tuning (the second §3.3
   evaluation panel); do not call it globally policy-unseen without closing SONIC
   pretraining lineage.
4. The latency-process ranking-instability finding.
5. The audit methodology and negative results (consolidation rejection, proxy holdout
   failure) as evidence of rigor, plus the Gate-A/directional-decision failure reported
   honestly as a limitation of counterfactual identification at this scale.

If Track B *also* fails to differentiate — no crossover, gates failed — then the
honest ICRA submission does not exist. The fallback is the audit/negative-results
manuscript (RA-L or a workshop), and that decision also gets made Sept 1, not
Sept 12. Do not spend September torturing a tie into a claim.

### What both papers share (write these now, path-independent)

- Method/protocol section (restart estimand, floors, preregistration, receipts).
- The latency-process study section.
- Related work: BeyondMimic/SONIC lineage, DR curricula (ADR, DORAEMON-style
  gap/performance-gated approaches), latency-robustness literature, and the scalar-λ
  ms #1615 story as your own prior work being corrected.
- Limitations: fresh-physics vs hardware, single robot/simulator, ≤256-env scale,
  60 ms out-of-support failure, three-vs-five seed history.

---

## 5. Rules that stay in force (unchanged, deadline notwithstanding)

1. No learned practice-utility estimator or learned practice scheduler before the
   preregistered inverse estimator-authorization gate. No allocation experiment before
   the latent-proxy decision authorizes the frozen proxy. A deadline does not amend
   either gate law.
2. Every run: receipt, seeds, git SHA, verified/not-yet-verified split. Preregister
   before looking.
3. The frozen final test split stays untouched until the camera-ready table. The
   Aug 21 discovery/confirmation panels stay closed to training decisions.
4. Branches from settled origins; last-4 efficacy; performer and content splits
   reported separately.
5. Negative results go in the paper. The consolidation rejection and the holdout
   replication failure are *features* of this program's credibility — reviewers at
   ICRA see a hundred "our curriculum wins" papers and almost none with preregistered
   keep-conditions.
6. No MJLab, no hardware, no VR teleop work before submission. (I noticed
   `vr_wholebody_teleop.md` open in the IDE — if that's a hardware-demo idea, it's a
   post-submission idea.)
7. The 2027 CFP requires disclosure of AI-generated article content, naming the system,
   affected sections, and use. Authors should review that wording themselves before
   submission; do not send manuscript-under-review content through an AI system.

---

## 6. Writing timeline (Sept 15 external deadline; Sept 14 internal deadline)

| Date | Milestone |
|---|---|
| Aug 26 | Commit staged work; verify deadline; build/audit Track-A origins (no screen launch until preflight is ready) |
| Aug 27–28 | Pass the live dose smoke and complete Track-A preflight; freeze Track-B campaign, then launch either only if its gates pass |
| Aug 29–31 | Track B evaluation + fine-tuning-unseen panel; complete 5-seed cells |
| **Sept 1** | **Paper-path decision. Experiment list frozen.** |
| Sept 2–4 | Any gap-filling runs (started by Sept 3 or cut); figures scripted from receipts |
| Sept 5–8 | Full draft from a frozen outline; method+latency sections can start Aug 30 |
| Sept 9–11 | Simulated reviewer panel; revise against it |
| Sept 12–13 | Freeze results tables; citation, AI-usage-disclosure, anonymity, and format checks |
| **Sept 14** | **Internal submission deadline; submit with one day of slack** |
| Sept 15 | External deadline at 11:59 PM Pacific Time; contingency only |

Every figure should be generated by a script that reads only manifest JSONs — you
have receipts for everything; keep the paper reproducible from them.

---

## 7. One-line answers to questions you might ask next

- *"Should we widen the latency envelope to 0–60 ms in Track B training?"* No — that
  changes two variables at once. Keep the trained envelope at 0–40 ms; the 60 ms cell
  is reported as an out-of-support limitation. The shared-lag 0–60 study is the next
  paper (or the rebuttal experiment).
- *"Five seeds everywhere?"* Headline tables, yes. Mechanism/audit receipts, the
  existing evidence stands.
- *"What if Gate A passes but latent predictiveness fails?"* That is a real result — practice
  utility is measurable but the latent gap doesn't predict it — and it merges into
  Path 2 as its strongest subsection: report it, keep the curriculum headline.
- *"Can we still cite the 21× intervention smoke and the 10× gap-vs-mismatch
  finding?"* Yes — as mechanism validation and motivation respectively, never as
  efficacy.

---

## Execution log — Fable in charge (from 2026-08-27 01:00)

- **01:05** TACE implemented on `research/practice-utility` as `de19caa`: `tace.py`
  (seeded cohort assignment; `CohortDispatch` wraps each runtime-scalable event
  term's `func` and calls SONIC's own sampler twice — focus subset with the
  λ-scaled params, anchor subset with the captured λ=1 baseline; material buckets
  swapped to the pre-scaling full-range copy for the anchor call), curriculum
  callback gains `anchor_ratio / anchor_seed / consolidation_fraction /
  yoked_schedule_path` and mode `yoked`; the observer's tracked env is reserved
  as focus so the controller never reads anchor evidence. 25 new CPU tests,
  suite 1,152 green. No upstream file touched.
- **01:20** `23663c3`: `run_arm` waits for shared-GPU capacity instead of dying
  (`LUCID_GPU_WAIT_SECONDS`); evaluator takes arms from the training receipt,
  adds `dr_025/050/075` robustness-profile presets, compares every treatment
  vs fixed/off/lucid. Preregistration written **before any GPU run**:
  `manifests/tace_pilot_preregistration_20260827.json` (H-A non-inferiority to
  fixed on dr_full within 2 pts + clean superiority ≥ 2 pts; H-B ta_lucid >
  ta_yoked in ≥ 2/3 seeds; H-C mechanism).
- **01:25** Driver `scripts/practice_utility/run_tace_pilot.sh` launched detached:
  waits for ≥ 11 GB free (GPU was 27.9/32.6 GB, 99% util from two other users'
  jobs), then smoke (ta_lucid_25, seed 8600, 16 it) → 4 arms × 3 seeds × 32 it
  (lucid, fixed, ta_lucid_25, ta_yoked_25; 128 envs; settled step-24 origin;
  ~3.5 min per branch when idle) → frozen eval on id_clean / dr_050 / dr_full /
  latency_60ms. Progress: `outputs/tace_pilot_driver.log`.
- **14:04–19:47** GPU freed; smoke passed (cohorts 32/96 exact, anchor delay 3.7 steps
  every iteration, focus tracked λ). 4-arm × 3-seed × 32-iter pilot trained in 32 min,
  eval in 5 h. **Receipts:** `curriculum_comparison_ne128_20260827_140621.json`,
  `curriculum_robustness_ne128_20260827_143814.json`,
  `tace_pilot_analysis_20260827_194701.json`.

  | success % (3-seed mean) | lucid | fixed | ta_lucid_25 |
  |---|---:|---:|---:|
  | id_clean | 83.99 | 80.39 | **83.66** |
  | dr_050 | 59.15 | **66.01** | 59.15 |
  | dr_full | 54.25 | **56.54** | 55.56 |
  | coarse profile mean | 65.80 | **67.65** | 66.12 |

  Preregistered decisions: **H-A pass** (non-inferior to fixed on dr_full, −0.98 pt;
  clean +3.27, 3/3 seeds), **H-A2 fail** (+1.31 over lucid < 2 pts), **H-B void**
  (same-seed yoking is bit-identical to its source — deterministic sim; cross-seed
  yoked cell queued as stage 4), **H-C fail** (mean terminal λ 0.63 vs lucid 0.76; seed
  8602 stalled at 0.41 and scored 46% dr_full). Parity: `lucid` reproduced the Aug 20
  numbers exactly. Read: the anchor moves LUCID toward fixed's robustness without
  costing clean success, but 32 iterations leave every curriculum arm short of the
  envelope; fixed still owns the mid-intensity bin. **Stage 5 queued:** 128-iteration
  horizon cell (lucid / fixed / ta_lucid_25 / ta_lucid_50 × 3 seeds), preregistered in
  `tace_horizon_preregistration_20260827.json` (H-H1 fixed clean degrades with budget;
  H-H2 a TA arm matches fixed on dr_full with clean superiority; H-H3 curricula reach
  λ ≥ 0.9; H-H4 dose ordering 50 ≥ 25).
- **20:58 — Stage 4 (cross-seed yoked control) result.** `ta_yoked_25x` replays, for
  seed s, the λ trajectory `ta_lucid_25` learned on seed s+1 (same anchor cohort, no
  feedback). Receipts `curriculum_comparison_ne128_20260827_194726.json`,
  `curriculum_robustness_ne128_20260827_195421.json`.

  | success % | ta_lucid_25 | ta_yoked_25x | Δ per seed | favorable |
  |---|---:|---:|---|---|
  | id_clean | 83.66 | 77.45 | +7.8 / +9.8 / +1.0 | 3/3 |
  | dr_050 | 59.15 | 57.19 | +1.0 / +8.8 / −3.9 | 2/3 |
  | dr_full | 55.56 | 51.96 | +3.9 / +4.9 / +2.0 | 3/3 |

  **H-B passes with the correct control**: with schedule shape and anchor dose matched,
  the online latent-gap feedback is worth +3.6 pts dr_full and +6.2 pts clean on three
  seeds, favorable in every seed on both endpoints. This is the attribution evidence
  the IROS review (W1) said LUCID lacked. Caveat: three seeds, screening-grade; the
  yoked schedules are mismatched to their own trajectories by construction — that
  mismatch is exactly what online feedback corrects, which is the claim.
- **22:33 — Stage 5 training telemetry (128 it).** Training reward at 128 iterations is
  roughly half the 32-iteration values for *every* arm (lucid 17.7→9.6, fixed
  10.0→7.4, ta_25 8.7, ta_50 8.7). Curves: lucid peaks 17.7 at ≈it 47 — right after λ
  first reaches 1.0 (≈it 39) — then declines with 3–7 absolute return-guard trips
  (floor 8.0 was calibrated for the 32-it regime) that decay λ to 0.4–0.6. Entropy
  drifts up monotonically (13.3→13.8) in all arms. Receipt
  `curriculum_comparison_ne128_20260827_205857.json`. Two readings are possible —
  full-envelope DR destabilizes fine-tuning of the released policy, or PPO
  fine-tuning from this origin drifts regardless — so **stage 6 (`off` × 3 seeds ×
  128 it, commit `8969a0e`) is queued as the drift control**. Method lesson already
  clear: an absolute return floor is not a robust guard under reward drift; a
  trailing-relative guard is the fix for the next arm. Stage-5 eval running.
- **2026-08-28 01:12 — Stage 5 (128-it horizon) eval.** Receipt
  `curriculum_robustness_ne128_20260827_223254.json`.

  | success % (3-seed mean) | lucid@128 | fixed@128 | ta_lucid_25@128 | **ta_lucid_50@128** | (lucid / fixed @32) |
  |---|---:|---:|---:|---:|---|
  | id_clean | 56.86 | 57.19 | 57.84 | **66.01** | 83.99 / 80.39 |
  | dr_050 | 48.37 | 46.73 | 45.42 | **54.58** | 59.15 / 66.01 |
  | dr_full | 39.22 | 41.50 | 42.48 | **46.41** | 54.25 / 56.54 |

  **Every arm collapses between 32 and 128 iterations** — clean −27 pts for lucid, −23
  for fixed; dr_full −15 for both. H-H1 (fixed degrades) is true but vacuous because
  the curricula degrade just as much; H-H2 fails against a collapsing reference; H-H3
  fails (λ reached 1 at ≈it 39 then was decayed by guard trips); H-H4 **passes**
  strongly — the 50% anchor is best on all three presets and degrades least (clean
  +9 over every other arm). Interpretation pending two controls now running:
  (a) `off` × 128 it (stage 6, is it DR-induced or plain fine-tuning drift?), and
  (b) the **untrained origin checkpoint** under the same evaluator
  (`origin_step24_pseudo_receipt.json`) — if the origin already scores ≥ 84% clean,
  then *all* fine-tuning at 128 envs (32× smaller batches than SONIC's release
  training) has been net-destructive, and "capability" in this testbed means
  *retaining* the released policy's competence while adding robustness — which is
  exactly what the target anchor (and its dose ordering 50 > 25 > 0) is doing.
- **2026-08-28 02:20 — Stage 6 drift control (`off` × 3 seeds × 128 it):** training
  reward holds at 19–22 throughout (last-4 19.09 vs 20.16 at 32 it). **The 32→128
  collapse is DR-induced, not fine-tuning drift.** Training on the full six-channel
  envelope at this scale destroys the released policy; gap-gating did not protect
  because the gap stayed under the set-point, λ reached 1 by ≈it 39, and the absolute
  return guard (floor 8) was tuned for the 32-it regime. Receipt
  `curriculum_comparison_ne128_20260828_011255.json`; eval running. Next cell
  (channel attribution, preregistered below): `fixed_nolat` (five channels at λ=1,
  latency 0) vs `fixed_latonly` (latency at λ=1, rest nominal) × 3 seeds × 128 it — the
  Aug 20 λ=1 latency A/B (−35.8% reward) makes actuation latency the prime suspect.
  If confirmed, the paper's mechanism story is: *the full envelope is unsustainable
  because of one channel, and a scalar λ cannot express "everything except latency"*
  — which is the evidence LUCID-MC (per-channel gating) needs.
- **2026-08-28 03:30–04:45 — Second host brought up (`linjiw-ubuntu`, RTX 5080 16 GB).**
  Infrastructure only; **no research evidence was produced and no claim moved.** The
  workspace had never been checked out here: both submodules were empty and the Isaac
  stack was pointed at an upstream NVlabs clone, not the fork. What now exists is a
  second machine that can run the program end to end.

  *Portability.* 87 hardcoded `/data/robotixx/lucid-sonic` literals across 28 drivers
  now resolve through `gear_sonic/research/practice_utility/paths.py`, whose default is
  the original host's absolute path — that host is unchanged and byte-identical —
  overridable with `$LUCID_ROOT`. `env/lucid_env.sh` is host-independent (derives the
  workspace from its own path, auto-detects conda-`sonic` vs a uv venv). The
  `pyproject.toml` numpy edit that used to conflict on every pull is gone, replaced by
  `$UV_OVERRIDE`. Commits `878d107`, `7442e88` (fork); `d21fa90`, `aec4b6b` (workspace).
  **Launcher bytes changed**, so `launcher_sha256` in receipts written from here will not
  match pre-2026-08-28 receipts; old receipts keep their own hashes, so lineage is intact.

  *The frozen instrument was rebuilt and verified, not assumed.* BONES-SEED (gated on HF)
  pulled, 142,220 CSVs extracted, and the pools the frozen manifests name regenerated at
  120→30 fps. **512/512 `debug512` and 4950/4950 `adapt4950` clips are hash-identical to
  the frozen `content_sha256` values.** `env/write_pool_equivalence.py` compares all six
  manifests field by field and writes a `lucid_pool_equivalence` receipt
  (`pool_equivalence_20260828_042753.json`): every clip hash, motion key, split
  `assignment`, `group_partition`, `ratios`, `seed` and `stats` identical. Both encoders
  regenerated (`bdaf342b21b97704`, `ce5145020cf8c6e4`) — new instruments, not the
  originals. CPU suite **1,156 passed / 0 skipped**, up from 1,143/13: the trained-encoder
  tests now run, reading the frozen manifests via `paths.relocate()`.

  *⛔ Open decision — pool identity.* `pool_sha256` hashes `source_root`, an **absolute
  filesystem path**, so byte-identical data in a different directory gets a different
  identity by construction. The frozen v2 probe manifest, the passive-dose plan and the
  directional-calibration preregistration are all hash-bound to it and therefore **do not
  validate on this host**, even though the instrument is provably the same. Three options,
  none taken: (1) re-freeze downstream here, discarding the Aug-26 outcome-blind freeze and
  re-preregistering; (2) drop `source_root` from `pool_sha256`, making pool identity
  content-addressed and portable — defensible as a bug fix, since a content hash
  containing a path is not one — at the cost that no new run reproduces an old
  `pool_sha256`; (3) teach the hash gates about the equivalence receipt, preserving the
  outcome-blind freeze as an audited exception. **This is a lineage decision and is
  deliberately left to the PI.** Nothing hash-bound should be launched here until it is made.

  *Machine capability, measured (receipts `throughput_idle_*_20260828_*.json`).* On the
  real `debug512` pool at `num_envs=256`: native **605** env-steps/s, observer **595** —
  the observer callback costs **1.5%**, so instrumenting a branch is effectively free. The
  same config on the 2-motion `sample_data` pool runs at 5,116 env-steps/s, i.e. **the pool,
  not policy compute, sets iteration time** (8.5×). Budget ≈0.37 h per 128-iteration branch
  at 256 envs. The card is at 100% util and 8 GB of 16 GB by `num_envs=256` on `debug512`.
  These are idle-GPU numbers on a **dedicated** card — unlike the shared 5090, no capacity
  gate is needed here, which removes the blocker that stalled Track B on Aug 27.

  *Still missing here.* The settled origin `sonic_release_test-20260818_141446/
  model_step_000024.pt` is not transferable; regenerating it starts a **new branch lineage**
  and the TACE drivers pin that exact path. Only the 5,462 clips the frozen manifests name
  are converted to motion_lib PKLs; the other ~137k CSVs are extracted but unconverted.
  SMPL pack absent (`smpl_motion_file=dummy` is fine for all G1-encoder work).
  Setup and open questions: `docs/machine-setup.md`.
- **2026-08-28 05:35–06:10 — Second host taken off the blocks; LUCID-S designed,
  implemented, preregistered, and queued.** Two decisions the previous entry left
  to the PI are now made and acted on.

  *Decision 1 — the origin.* **Regenerate here and accept a new branch lineage.**
  The released checkpoint `sonic_release/last.pt` on this host is **byte-identical**
  to the one every earlier result used (sha256 `e6bdab3f64a3…`, 469,418,283 B —
  the value recorded in the design plan §14), so the root instrument is not in
  question; only the 24-step settled origin is. `scripts/practice_utility/make_settled_origin.py`
  reproduces it from stock SONIC (`+exp=…/sonic_release`, stock `level0_4` events,
  no research callbacks) and receipts the checkpoint's sha256 and the exact command.
  New origin: `sonic_release_test-20260828_054436/model_step_000024.pt`, sha256
  `2fcb299a659c9cb2…`; receipt `settled_origin_ne128_20260828_054435.json`. En route
  it exposed a launcher defect worth keeping: **`++algo.config.save_interval` is read
  by nothing.** Every practice-utility driver sets it to 100000 and relies on the
  capsule callback instead, so nobody noticed; a run that asks for a checkpoint
  through that key silently saves none. The cadence lives on
  `callbacks.model_save.save_frequency`.

  *The origin is validated, not assumed.* A 32-iteration `lucid`/`fixed` × 3-seed
  cell was run on it and compared to the Aug-20/27 table:

  | | this host | first host | |
  |---|---:|---:|---|
  | terminal λ (lucid) | **0.767** | 0.756 | +1.5% |
  | realized delay, fixed (steps) | **3.8918** | 3.89 | equal |
  | lucid ÷ fixed last-4 reward | **1.76** | 1.77 | equal |
  | last-4 reward, lucid / fixed | 15.12 / 8.59 | 17.73 / 10.03 | −15% level |

  The controller's fixed point, the realized DR dose and the arm *ratio* reproduce;
  the absolute reward level sits ~15% lower, consistent with a different settled
  origin and with `smpl_motion_file=dummy` here (the 32 GB SMPL pack is absent; it
  is now recorded in every receipt via a new `--smpl-motion-file` flag rather than
  being silently absorbed by a missing path). Receipt
  `curriculum_comparison_ne128_20260828_054615.json`.

  *Decision 2 — pool identity: deferred, and largely moot.* The evaluator reads the
  **frozen** pool/split manifests and re-roots their paths through `paths.relocate()`,
  so the 102-motion content-dev panel materialized here carries
  `pool_sha256 b065a498…`, `split_sha256 33784622…` and `motion_keys_sha256 f0c18255…`
  — **identical to the first host's**. Evaluation numbers are therefore cross-host
  comparable without any decision at all. `pool_sha256`'s path-dependence still blocks
  **Track A** (the probe screen recomputes it and compares). The intended fix is
  option 2+3 together: make the hash content-addressed and keep the Aug-26 outcome-blind
  freeze via the equivalence receipt. Not implemented — Track A is not on the path to
  the capability claim, and the infrastructure freeze stands.

  *The science: what the horizon collapse actually says.* Re-reading stage 5 by anchor
  fraction gives a **non-monotonic** clean-success curve — 0% → 56.86, 25% → 57.84,
  50% → **66.01**, 100% (`fixed`) → 57.19. The best arm is neither the most nor the
  least randomized; it is the one whose environments span the **widest range of
  intensities at once**. Stage 6 (`off` holds at 19–22 reward) already ruled out
  fine-tuning drift. Read together: *what preserves capability is intensity diversity
  across environments, and a scalar λ that moves one point cannot express it.*

  **LUCID-S** is that reading made literal, committed at `71a0f84`:
  1. `spread_strata = K` generalises TACE's anchor/focus split into K intensity strata,
     stratum k training at λ·(k+1)/K. λ becomes the **upper edge of a training mixture
     over (0, λ]** rather than its single value. The top stratum is served the event
     manager's own params, so K = 1 is the pre-strata path exactly.
  2. `return_guard="relative"` replaces the absolute floor. The floor (8.0) was
     calibrated at 32 iterations and fired continuously at 128, where reward had halved
     for *every* arm including `off` — decaying λ from 1.0 to 0.4–0.6 for reasons that
     had nothing to do with the policy. An absolute threshold also cannot separate "the
     environment got harder" from "the policy is failing". The replacement compares a
     return against the best of a trailing window of its own history.
  3. The evaluator may now **extrapolate past the training envelope** (`dr_125`,
     `dr_150`); the curriculum is still hard-capped at λ = 1, with a test pinning the
     asymmetry. Every robustness number in this programme so far was measured inside
     the envelope the policy trained on, which is exactly the wrong place to test a
     deployment claim.

  Suite **1,204 green** (was 1,156); 46 new tests.

  *Preregistered before launch*, on a clean tree at `71a0f84`:
  `lucid_support_expansion_preregistration_20260828.json` (logical sha
  `8825d19aed5badf3…`). Primary endpoint **robustness-profile AUC** over
  s ∈ {0, 0.5, 1.0, 1.25}; co-primary the `dr_125` extrapolation cell. H-S1 support
  expansion beats plain lucid by ≥ 2 pts AUC; H-S2 the relative guard ends at λ ≥ 0.9
  with ≤ 2 trips; H-S3 `ta_lucid_50_s4_rg` has the highest AUC, is non-inferior to
  `fixed` on dr_full and beats it on clean by ≥ 5; H-S4 it stays within 10 pts of the
  **untrained origin** on clean while `fixed` is > 20 pts below it; H-S5 it beats
  `fixed` on `dr_125` by ≥ 3 pts in ≥ 2/3 seeds. If every arm still collapses, the
  contribution is the diagnosis and the audit protocol, and that is what gets written.

  *Queued unattended* (`run_lucid_s_campaign.sh`): stage 7 channel attribution with
  same-host references (`fixed`, `off`, `lucid`, `fixed_nolat`, `fixed_latonly` ×
  3 seeds × 128 it) → stage 8 LUCID-S (5 arms × 3 seeds × 128 it) → evaluation of the
  untrained origin, stage 7 and stage 8 on five presets. Branch cost here is ~4 min at
  1.67 s/iteration on a dedicated card; the shared-GPU contention that stalled Track B
  on Aug 27 does not apply. `analyze_lucid_s.py` scores the five hypotheses from the
  receipts and was written and tested **before** the campaign existed — its end-to-end
  tests build receipts where every verdict is known by construction, and already caught
  a real defect (an empty `curriculum_path` resolves to `.`, a directory, so the
  existence check passed and the read raised).

- **2026-08-28 06:54 — Stage 7 (channel attribution, 128 it, same-host references).**
  Receipt `curriculum_comparison_ne128_20260828_055416.json`; 15 branches, all complete.
  Mechanism validated in-simulator before reading anything: `fixed_nolat` and `off` show
  max actuator lag 0 and 0% nonzero, `fixed_latonly` 3.74 steps at 86% nonzero.

  | last-4 reward | off | fixed_nolat | lucid | fixed_latonly | fixed |
  |---|---:|---:|---:|---:|---:|
  | 3-seed mean | **13.09** | 10.63 | 9.43 | 6.38 | **5.52** |
  | episode length | 162.6 | 141.2 | 136.0 | 100.3 | 95.5 |
  | latent gap p90 | 0.053 | **0.245** | 0.166 | **0.078** | 0.182 |

  **One channel carries the harm.** Reward lost against the no-DR control, per seed:
  the five non-latency channels *together* cost 2.34 / 2.27 / 2.76; actuation latency
  *alone* costs 4.55 / 8.27 / 7.31. Latency is 2.7× the rest combined, **in 3 of 3
  seeds**, and reaches 89% of the full envelope's damage. The losses are sub-additive
  (2.46 + 6.71 > 7.57), so there is mild interaction, but the ordering is not in doubt.
  This is the evidence LUCID-MC needed: *a scalar λ cannot express "everything except
  latency"*, and now there is a measured reason to want to.

  **And the curriculum's own signal is nearly blind to it.** `fixed_latonly` — the most
  damaging arm short of full DR — raises the latent command-execution gap to 0.078,
  barely above the no-DR control's 0.053 and *below* it in seed 8601 (0.026 vs 0.047).
  The least damaging arm, `fixed_nolat`, raises it most (0.245). The direction holds in
  2 of 3 seeds and the per-seed gap estimates are visibly noisy, so this is recorded as
  **"the gap does not rank channels by harm"**, not as an anti-correlation. It is still
  enough to explain the whole stage-5 failure: λ climbed to 1.0 by iteration 39 because
  the gap never objected, and the return guard was the only thing that ever pushed back.
  Under latency the robot tracks its *commands* in latent space perfectly well; the
  damage is somewhere the encoder does not look.

  **An absolute threshold does not survive a change of machine.** `lucid` here tripped its
  return guard **12 / 7 / 7** times against 3–7 on the first host, and ended at
  terminal λ **0.339** against 0.4–0.6 — same floor (8.0), same code, a reward level
  ~15% lower. That is independent confirmation of the defect the relative guard was
  built to fix, and it lands on stage 7's own preregistration too: H_L3's thresholds
  ("`fixed_nolat` > 15, `fixed_latonly` < 10") were calibrated where `off` = 19.1, and
  here `off` = 13.09. **As literally written H_L3 fails one clause.** Expressed as a
  fraction of the same-host no-DR control — the comparison it was plainly making —
  both clauses pass: 15/19.1 = 79% asked vs 81% observed, and 10/19.1 = 52% asked vs
  49% observed. Reported both ways; the absolute form is the one that broke, and it
  broke for exactly the reason the guard did. H_L1/H_L2 are evaluation hypotheses and
  are still pending.

  *One hygiene note.* The delayed-actuator process records ~640 nonzero assignments —
  one full population draw at the config default — **before** the curriculum callback
  binds. `off` and `fixed_nolat` show byte-identical nonzero histograms at the same seed,
  so it is a shared pre-bind transient and confounds nothing, and it does not exist in
  evaluation (`id_clean` runs show `action_delay_process_histogram: [5515]`, every
  assignment zero). Recorded, not claimed.

- **2026-08-28 06:54 — Stage 8 launched; LUCID-S verified live.** The first stratified
  branch (`lucid_s4`, seed 8600) shows the mechanism doing exactly what it was built to:
  4 strata of **exactly 32 environments each**, stratum λ = 0.240 / 0.480 / 0.720 / 0.960
  at λ = 0.9597, `delay_range` params [0, 1.92] / [0, 3.84] / [0, 5.76] / live, and —
  the part that matters — **realized actuator lag 1.03 / 1.70 / 2.48 / 3.08 steps**.
  The intensity mixture is physics the simulator installed, not a config assertion.
  Note a confound the design already anticipates: `lucid_s4` keeps the *absolute* guard,
  yet sits at λ = 0.96 where plain `lucid` was driven to 0.34 — because three quarters of
  its environments train easier, mean return stays above the floor. Mixture and λ
  trajectory therefore move together in that arm; `lucid_rg` (guard only) and
  `lucid_s4_rg` (both) are in the same campaign precisely to separate them.

  **Stage 9 preregistered** from stage-7 *training* telemetry only, before any evaluation
  existed: `lucid_latency_cap_preregistration_20260828.json` (logical sha `fc73eee1a235174a`).
  A 2×2 over {latency cap 0.5, no cap} × {anchor, no anchor}, the capped arms matched to
  stage 8's `lucid_s4_rg` / `ta_lucid_50_s4_rg` on seeds and origin. The cap is the
  midpoint of the 0–40 ms envelope, fixed in advance and not swept, and it is never graded
  on its own turf: `dr_full` (40 ms) and `latency_60ms` (60 ms) both test latency *outside*
  the capped training range, so a capped arm can only win by generalising past what it
  trained on. H_C3 is stated so that losing out-of-range latency robustness is reported as
  a **trade**, not buried under an AUC gain.

  **Stage 10 preregistered** as a validity control that runs whichever way stage 8 goes:
  `lucid_batch_size_control_preregistration_20260828.json` (logical sha `7b868634d66036ef`).
  Every horizon result here was measured at `num_envs=128` against a policy released after
  training at 4096. If full-envelope DR turns out to be sustainable at 256, the stage-5/6
  mechanism reading is a small-batch artifact and gets retracted in those words.

- **2026-08-28 07:48 — Stage 8 training (LUCID-S, 5 arms × 3 seeds × 128 it).** Receipt
  `curriculum_comparison_ne128_20260828_065416.json`; 15 branches, all complete. Evaluation
  is the endpoint and is still running — **training reward is not comparable across these
  arms**, because each trains on a different distribution, and it is reported below only
  as controller diagnostics.

  | arm | strata/guard | terminal λ | guard trips | realized delay |
  |---|---|---:|---|---:|
  | `lucid` (stage 7) | 1 / absolute | 0.339 | 12 / 7 / 7 | 1.49 |
  | `lucid_rg` | 1 / **relative** | **0.788** | 4 / 5 / 5 | 2.63 |
  | `lucid_s4` | 4 / absolute | 0.618 | 5 / 4 / 2 | 1.40 |
  | `lucid_s4_rg` | 4 / **relative** | 0.712 | 4 / 4 / 2 | 1.92 |
  | `ta_lucid_50` | 1 / absolute | **0.191** | **28 / 19 / 14** | 2.17 |
  | `ta_lucid_50_s4_rg` | 4 / **relative** | **0.838** | 4 / 4 / 2 | 3.03 |

  **H-S2 fails as written and succeeds as a direction.** I preregistered "terminal λ ≥ 0.9
  and ≤ 2 guard trips" for `lucid_rg`; it delivered 0.788 and 4/5/5. Against its own
  control `lucid`, though, the relative guard **cut trips from 12/7/7 to 4/5/5 and lifted
  terminal λ from 0.339 to 0.788**. The thresholds were too aggressive; the effect is large
  and in the predicted direction. Recorded as a failed hypothesis with its effect size, not
  rewritten.

  **A defect the campaign found on its own: the anchor cohort contaminates the return
  guard.** `ta_lucid_50` with the absolute floor tripped **28 / 19 / 14** times and ended at
  terminal λ **0.191** (0.035 / 0.130 / 0.406) — the focus half is training at essentially
  no randomization. TACE was careful to make the *gap* focus-only, and it worked: this arm
  has the lowest gap of any (0.066), because the focus environments really are easy. But the
  **return** the guard reads is population-wide, and half that population is pinned at λ = 1
  by construction. The anchor drags mean return under the floor permanently, so the guard
  fires forever. The isolation was applied to one controller input and not the other.

  Two consequences. First, it **re-reads the stage-5 result**: `ta_lucid_50@128` was the best
  arm on the first host (66.01 clean), and this says what it actually was — 50% of
  environments at λ = 1 and the other 50% at λ ≈ 0. That is not "a 50% anchor", it is the
  *widest two-point intensity mixture in the study*, which is precisely the mixture reading
  rather than a coincidence. Second, the fix is already in and is not a new mechanism: a
  guard that judges a return against **its own recent history** is immune to a constant
  cohort offset, and `ta_lucid_50_s4_rg` confirms it — same 50% anchor, 4/4/2 trips,
  terminal λ 0.838. So the relative guard earns its place twice over, for two independent
  reasons: reward scale does not port across machines, and a population return is not the
  focus cohort's return.

  Note also that `ta_lucid_50_s4_rg` carries the **highest realized latency dose of any arm**
  (3.03 steps). Given stage 7, that is the arm most exposed to the one channel that does the
  damage — which is exactly the tension stage 9's latency cap is preregistered to resolve.
  `lucid_s4` vs `lucid` and `lucid_s4` vs `lucid_s4_rg` separate strata from guard; the
  anchor arm's own decomposition (`ta_lucid_50_rg`) is **not** in this campaign, and whether
  it is worth an hour of GPU is deliberately left until the evaluation is in rather than
  guessed at now.

- **2026-08-28 08:05 — Two evaluation findings that reframe the study, both from the
  reference arms rather than the treatments.**

  **(1) The untrained origin beats every trained arm.** First origin cells (seed 8600,
  frozen policy, no learning): `id_clean` **90.20%**, `dr_050` 68.63%, `dr_full`
  **60.78%**, `dr_125` 55.88%. Against the first host's 128-iteration table — clean
  56.9–66.0, dr_full 39.2–46.4 for *every* arm including `fixed` — this says something
  the curriculum comparison could not: at `num_envs=128`, **DR fine-tuning of the
  released SONIC policy is net-destructive, and not only on clean capability but on the
  full-envelope robustness it is explicitly training for.** Every arm in the horizon
  study was worse than doing nothing. "Which curriculum is best" was the wrong question
  to be asking of that table.

  That makes the batch-size control the *interpretation-critical* experiment rather than
  a side check, so the queue was reordered to run it before the latency cap. SONIC's
  release policy was trained at 4,096 environments; every horizon result here is at 128.
  If full-envelope DR is sustainable at 256, the stage-5/6 mechanism reading is a
  small-batch artifact and gets retracted in those words.

  **(2) The deployment-latency endpoint was saturated, and had been all along.**
  `latency_60ms` reads **0.00%** for the untrained origin — and, checking back, 0.00%
  for lucid / fixed / ta_lucid_25 / ta_yoked_25 at 32 iterations *and* for lucid /
  fixed / ta_lucid_25 / ta_lucid_50 at 128, on the first host. Zero before training and
  zero after it, for every policy ever measured. That is not a robustness measurement,
  it is a floor, and no endpoint defined on it can rank anything — including H_C3 as
  written in the stage-9 preregistration, which is hereby superseded.

  Two things made it saturate: it stacks a fixed 60 ms **on top of the full six-channel
  envelope**, moving two axes at once; and 60 ms fixed on all five actuator groups is far
  harsher than the 0–40 ms sampled *independently per group* that training ever sees.
  Note the origin scores 60.78% on `dr_full` — which already contains 0–40 ms latency —
  and 0.00% once latency is pinned at 60 ms, so the marginal effect of that pin is the
  whole story.

  **Stage 11, the latency ladder**, replaces it: latency pinned at 10 / 20 / 30 / 40 /
  60 ms against **nominal** physics on every other channel, so latency is the only axis
  moving — which is also the question a deployment actually asks. Implemented as an
  eval-callback parameter rather than five configs, and reported: each receipt records
  which terms were really pinned, and a rung only counts as measured if every live lag
  sat at it. Preregistered before running at
  `lucid_latency_ladder_preregistration_20260828.json` (logical sha `3d7352d1d4c6c3ad`),
  with the saturation evidence stated as the reason, and with H_D3 written so that the
  capped arm *losing* margin at 40 ms is recorded as the expected direction of a trade
  rather than as a failure. Arms: origin, off, fixed, `ta_lucid_50_s4_rg`,
  `ta_lucid_50_latcap_s4_rg`.

  *Precision, not new hypotheses.* Every evaluated run records which of the 102 panel
  motions failed, so two arms at the same seed are paired motion by motion — 102 × 3
  paired observations instead of 3. `motion_paired.py` adds hierarchical paired bootstrap
  intervals (seeds resampled, then motions within each drawn seed) on exactly the
  differences the preregistrations already name, including the profile AUC, which is a
  fixed weighted sum (0.2 / 0.4 / 0.3 / 0.1) of the per-cell rates and so bootstraps at
  motion level too. The preregistered rules are still scored, unchanged, from the same
  three-seed means. Pairing is refused unless the panel order is provably shared.
  Suite **1,246 green**.

- **2026-08-28 08:41 — The untrained-origin reference, complete (3 eval seeds).**
  Receipt `curriculum_robustness_ne128_20260828_074808.json`. Frozen policy, no learning,
  the same 102-motion panel and eval seeds as every trained arm.

  | preset | mean | per seed |
  |---|---:|---|
  | `id_clean` | **89.54** | 90.20 / 91.18 / 87.25 |
  | `dr_050` | 66.01 | 68.63 / 66.67 / 62.75 |
  | `dr_full` | **60.46** | 60.78 / 62.75 / 57.84 |
  | `dr_125` | 56.21 | 55.88 / 63.73 / 49.02 |
  | `latency_60ms` | **0.00** | 0.00 / 0.00 / 0.00 |

  Profile AUC (0.2/0.4/0.3/0.1 over s ∈ {0, 0.5, 1, 1.25}) = **68.07**. That is the bar
  every arm has to clear, and on the first host's 128-iteration table none of them come
  close on any cell. It is also worth stating plainly that the origin degrades *gracefully*
  — 89.5 → 66.0 → 60.5 → 56.2 across the severity grid, and it is still above 56% at
  1.25× the training envelope it never trained on. The released policy is already
  substantially robust to the five non-latency channels; what it cannot do at all is
  tolerate a pinned 60 ms of actuation delay.

  **Stage 12, the budget dose-response, is queued as a direct consequence.** The horizon
  study can say DR fine-tuning hurts at 128 iterations; it cannot say whether some
  smaller budget helps, because the 32-iteration numbers were measured on the other host
  with a different origin. The 32-iteration parity cell already exists here and was never
  evaluated, so stage 12 adds `off` and `ta_lucid_50_s4_rg` at 32 iterations and
  evaluates all four — giving **0 → 32 → 128 iterations for four arms with origin, pool,
  panel and eval seeds all held fixed**. If no budget beats 68.07 AUC, the honest headline
  is that DR fine-tuning of this released policy at accessible scale is net-destructive,
  and the contribution is the diagnosis plus the audit protocol, exactly as the stage-8
  decision rule already commits us to.

  The decisive control for *why* is already in flight and needs nothing new: stage 7's
  evaluation contains `off`, so the decomposition origin → `off` → {`fixed_nolat`,
  `fixed_latonly`} → `fixed` separates the cost of fine-tuning at all from the cost of
  each channel group. If `off` lands near the origin, only DR is destructive; if `off`
  drops with it, the fine-tuning setup itself is (128 environments against a policy
  released from 4,096, at unchanged PPO hyperparameters), and stage 10 becomes the whole
  story.

  Driver chain, all four armed and sequential on the one card:
  campaign (origin → stage 7 → stage 8) → stage 10 → stage 9 → stage 12 → stage 11.

- **2026-08-28 08:50 — An anchor defect caught before it ran.** `TACE.install` handed the
  anchor cohort the *captured baseline*, so any arm that pins or caps a channel would
  still have given half its environments the full configured range for that channel. For
  the then-queued `ta_lucid_50_latcap_s4_rg` that is 50% of environments training at
  uncapped 0–40 ms latency: the cap would have been a claim about half the run, and
  **nothing in the receipt would have looked wrong.** The anchor now samples the arm's own
  target envelope — baseline for an unrestricted channel, baseline scaled to the channel's
  ceiling for a pinned or capped one, with the material term's anchor buckets redrawn at
  that ceiling. Arms with neither take an early return and are byte-identical, so stages 7,
  8, 10 and 12 are untouched. Six tests pin it.

  Second instance of one class of bug in this machinery: TACE made the *gap* focus-only but
  not the *return*, and now the anchor's *envelope* was the config's rather than the arm's.
  Both are "the cohort split was applied to one thing and not its neighbour", and both are
  invisible in aggregate telemetry.

- **2026-08-28 11:04 — Stage 7 evaluation. The mechanism story is overturned, including
  two conclusions recorded earlier in this log.** Receipt
  `curriculum_robustness_ne128_20260828_084051.json`; 75 cells, all complete.

  | arm | clean | dr_050 | dr_full | dr_125 | AUC | ΔAUC vs origin (95% CI) |
  |---|---:|---:|---:|---:|---:|---|
  | **origin** | 89.54 | 66.01 | 60.46 | 56.21 | **68.07** | — |
  | `lucid` | 63.73 | 46.73 | 42.48 | 36.27 | 47.81 | −20.26 [−26.3, −14.8] |
  | **`off`** | 61.11 | 45.10 | 36.60 | 37.91 | 45.03 | **−23.04 [−28.3, −17.9]** |
  | `fixed` | 53.27 | 42.16 | 38.89 | 32.03 | 42.39 | −25.69 [−31.4, −20.6] |
  | `fixed_nolat` | 60.78 | 39.54 | 35.29 | 33.66 | 41.93 | −26.14 [−30.7, −21.6] |
  | `fixed_latonly` | 56.21 | 41.83 | 35.29 | 33.99 | 41.96 | −26.11 [−33.4, −19.4] |

  Intervals are the paired motion-level bootstrap over 102 motions × 3 seeds.

  **`off` — no randomization at all — loses 23.0 of the 25.7 points that full DR loses.**
  Adding the entire six-channel envelope on top costs a further 2.65 points, CI
  [−7.1, +1.8], covering zero. **The collapse is fine-tuning-induced, not DR-induced**, and
  the envelope is close to irrelevant to it.

  Two corrections, sharing one shape:

  1. Stage 6 concluded "the 32→128 collapse is DR-induced, not fine-tuning drift" because
     `off` held its *training reward* at 19–22. But `off`'s training reward is measured on
     the nominal distribution `off` trains on. Held out, `off` is nearly as damaged as
     `fixed`. **Retracted.**
  2. The 06:54 entry above read stage 7's *training* telemetry as "latency carries 89% of
     the harm". Held out, `fixed_nolat` and `fixed_latonly` are indistinguishable:
     **−0.03 AUC, CI [−7.8, +9.1]**. There is no channel attribution in evaluation.
     **Retracted as a held-out claim**; it stands only as a statement about training reward.

  Both used a training-distribution metric to answer a held-out question — the same error
  the programme's own rules warn against, in a form the rules did not name.

  Preregistered channel-attribution hypotheses, scored: **H_L1 passes** (|latonly − fixed|
  = 2.94 ≤ 5), **H_L2 fails** (nolat − fixed = 7.52, not > 10). That preregistration's own
  rule for this case — "the envelope is unsustainable through more than one channel; report
  it, do not tune" — is what is being followed.

  One quiet positive: `lucid` is the only arm above `off` (+2.78, CI [−1.2, +6.6]) — best of
  the trained arms, not distinguishable from no-DR, and none beat doing nothing.

  **Consequences.** Stage 9 (the latency cap) was **dropped**: its premise was exactly the
  attribution that just failed. The tail was reordered to probe the only question left —
  is there a fine-tuning configuration that is not destructive — cheapest first: stage 12
  (32 iterations), then stage 10 (256 environments). Four sleeping drivers were replaced by
  one `run_tail.sh`.

- **2026-08-28 11:30–12:00 — CPU-side session: audit, Gate A, sampler safeguards,
  preregistered matrix. Nothing executed, nothing committed.**

  ⚠️ **Read this before trusting anything in this entry.** In this session, Bash execution,
  `git`, and every read outside `/home/linjiw/lucid` were blocked. So: the code and tests
  below are **written but never run**, no lint or format pass was made, no commit exists,
  and the live campaign's receipts and logs after Stage 7 could not be read at all. The
  running drivers were left strictly alone. Treat every artifact here as *unverified until
  the resume checklist at the end passes.*

  That constraint has one genuine benefit: the preregistration written this session is
  outcome-blind with respect to stages 8, 10, 12 and 13 **by capability**, not by
  discipline — their receipts were unreadable.

  *What was written.*

  - `scripts/practice_utility/audit_evaluation_receipt.py` — decides whether an evaluation
    receipt may be interpreted *at all*, before anybody reads its means. Checks cell
    coverage (every declared (mode, preset, seed) present exactly once and complete),
    checkpoint identity and immutability across evaluation, one panel everywhere, and that
    `mode_summary` is exactly rebuildable from the per-run summaries — a mean that cannot be
    reconstructed from its parts is not a measurement. Flags saturated presets as
    unrankable. Grades evidence, and **downgrades a "confirmatory" request to screening**
    when fewer than five training seeds are present.
  - `gear_sonic/research/practice_utility/bin_sampler.py` — expanding-support samplers with
    the safeguards: a preregistered aggregate **easy-bin floor** enforced *after* weighting
    (this is how an error-weighted curriculum quietly becomes a moving point again);
    **lagged, frozen** failure statistics so the sampler is not coupled to the batch it is
    about to draw; per-bin counts and Kish **effective sample size**; **fail-closed**
    coverage that raises rather than warns; `d_max` that may expand but not shrink;
    deterministic resume including the lag queue; and receipt fields. `FixedMixtureSampler`
    is deliberately the same object for both the direct-mixed baseline and the
    consolidation phase, so those are provably one distribution.
  - `gear_sonic/research/practice_utility/learnability_gate.py` and
    `scripts/practice_utility/run_gate_a.py` — Gate A. The hard bin is chosen by a frozen
    rule from the **reference arm only**, so the choice cannot be steered by which treatment
    looks good; saturated bins are excluded by measurement and the 60 ms cells by name,
    because they are a measured floor for every policy including the untrained one. The
    verdict is three-valued and **`curriculum_unnecessary` is a reportable finding**, not a
    failure.
  - `docs/preregistration-curriculum-matrix-2026-08-28.md` — screening (3 seeds) then
    confirmatory (5 seeds) matrix: origin, no-DR continuation, direct mixed, expanding
    support, expansion + 40% final mixed consolidation, error-weighted expansion with the
    15% easy-bin floor, latency-specific LUCID, and descriptor-conditioned oracle/deployable
    arms held separate from the main claim. Budget equality is specified on environment
    steps, PPO updates, rollout size and evaluation calls, with the transition LR schedule
    applied to the *baseline too* so it is never one arm's advantage. Gates 0/A/B/C/D with
    thresholds frozen in the document.

  *The gate that now precedes everything.* Gate 0: no curriculum question is askable until
  some configuration exists whose **no-DR continuation** stays within 5 profile-AUC points
  of the untrained origin. On present evidence `off` at 128 envs / 128 iterations is 23
  points below it. Stages 12 and 10 are the two probes. **If both fail, the matrix is not
  run** and the recorded result is that this testbed cannot support a curriculum comparison
  at accessible scale.

  *Also recorded as still-unimplemented:* per-bin reward/value scaling (PopArt-style)
  behind an ablatable flag with numerical no-op tests. Specified in the matrix document,
  deliberately **not** written blind — it touches the PPO path, and writing an untestable
  change to a shared optimizer is how a silent baseline shift gets introduced.

  **Resume checklist — run these in order before believing any of the above.**
  1. `pytest tests/practice_utility/` — the three new test files have never executed.
     Expect ~1,257 prior tests plus ~60 new.
  2. `make run-checks` (isort, Black, Ruff) on the submodule.
  3. `python scripts/practice_utility/audit_evaluation_receipt.py <stage 7 eval receipt>`
     and again for stage 8; both must print `interpretation allowed`.
  4. `bash sync_receipts.sh` (without push) to mirror the newly landed receipts.
  5. Read the tail of `$LUCID_ROOT/outputs/lucid_s_driver.log` to find where the campaign
     actually got to; the chain is stage 8 eval → stage 12 → stage 10 → stage 13 → ladder.
  6. Only then evaluate Gate 0 from stages 12 and 10, and only then run `run_gate_a.py`.
  7. Commit the submodule and workspace separately; do **not** push.

- **2026-08-28 11:40 — PI decision: stop fine-tuning the released checkpoint. Train from
  scratch, to convergence, on a training set sized to this hardware.**

  *Why the old design was answering the wrong question.* Stage 7's held-out decomposition
  showed plain no-DR continuation (`off`) costs **23.04 profile-AUC points** against the
  untrained origin (95% CI [−28.33, −17.88], paired over 102 motions × 3 seeds), and that
  adding the full six-channel envelope on top costs a further 2.65 (CI [−7.06, +1.76],
  covering zero). Every arm comparison anchored on the release checkpoint was therefore
  measuring **how fast we damage a policy trained on ~4 × 10⁹ transitions**, not whether a
  curriculum helps learning. Our fine-tuning budget is 3.9 × 10⁵ transitions — four orders
  of magnitude smaller — so this was never a fair fight, and the released policy is a
  poisoned baseline rather than a strong one.

  *And the training curves rule out the obvious objection.* If the arms were merely
  under-trained, reward would still be climbing at iteration 128. It is not: **every arm
  peaks between iteration 17 and 51 and declines monotonically thereafter**, `off`
  included (16.7 at it 51 → 12.85 over it 97–128). That is measured on each arm's *own*
  training distribution, so it is not a distribution-shift artifact, and held-out
  evaluation agrees (24 it → 89.5% clean, 128 it → 53–64%). Two independent metrics say
  longer is worse. The policy is being degraded, not slowly converging.

  *Why from-scratch is the better experiment, not just a different one.* A curriculum is a
  claim about **learning**. Testing it on a policy that had already learned inverted the
  question. From scratch, "start inside the frontier and expand support" is exactly the
  regime curricula are supposed to win in, and every arm starts equal — no arm inherits
  4 × 10⁹ transitions of prior competence.

  *What is held fixed, so nothing already measured is thrown away.* The evaluation
  instrument does not change. The content split's `dev` partition (102 motions,
  `motion_keys_sha256 f0c18255…`) remains the panel, with the same eval seeds and presets,
  so from-scratch numbers sit on the same axis as the origin's 89.54 / 66.01 / 60.46 /
  56.21 and every fine-tuned arm. Training draws only from the `adaptation` partition
  (308 motions), which the content linkage already separated from `dev` and `test`.
  `make_training_subset.py` builds seeded, symlink-only, receipted subsets and **refuses**
  to draw from `dev` or `test`. Built and verified: `train016` ⊂ `train064` ⊂ `train308`,
  nested, with **zero overlap with the dev panel**.

  *Feasibility before commitment.* A from-scratch campaign is tens of GPU-hours, so a
  bounded pilot runs first: three no-DR runs from fresh initialisation (train016 @512,
  train064 @512, train064 @1024, 300 iterations, capsules at 50/100/200). It asks only
  whether a fresh policy learns anything measurable here and at what pool size and batch.
  Smallest pool first — if a fresh policy cannot learn 16 motions it will not learn 64,
  and that is a twenty-minute finding rather than a thirty-hour one.

  *Launcher support.* `--from-scratch` omits the checkpoint override so the entire campaign
  machinery — arms, curriculum, cohorts, receipts — works unchanged on a fresh policy.
  `--horizons` exports a capsule at each named iteration count, so the convergence curve is
  measured **along one trajectory** rather than across separate runs, which is what "train
  until the metric stops improving" actually requires.

  *Cancelled.* The fine-tuning tail (stages 12, 10, 13 and the ladder) is dropped: all of
  it probed a baseline we are abandoning. Kept: stage 8's evaluation, because it answers a
  live preregistration and a frozen hypothesis should not be left unanswered; and the
  released checkpoint's own evaluation, which fixes the true zero point of the budget
  curve and documents why the pivot was made.

  *Note for whoever reads this next.* Another session is working in this repository
  concurrently — `bin_sampler.py`, `learnability_gate.py`, `run_gate_a.py`,
  `audit_evaluation_receipt.py` and their tests appeared untracked at 11:36. They are left
  alone and not committed here; three of their tests currently fail. The 1,257 tests
  belonging to this line of work all pass.

- **2026-08-28 11:40–14:10 — PI redirection: stop fine-tuning, train from scratch, and
  shrink the task until learning is observable.**

  *Why the old design was answering the wrong question.* Stage 7's held-out decomposition
  showed plain continuation with **no event-manager DR** (`off`) costs **23.04 profile-AUC
  points** against the untrained origin (95% CI [−28.33, −17.88], paired over 102 motions
  × 3 seeds), while adding the full six-channel envelope costs a further 2.65 (CI [−7.06,
  +1.76], covering zero). Every arm comparison anchored on the release checkpoint was
  measuring **how fast we damage a policy trained on 5.23 × 10¹¹ transitions across 128
  GPUs**, not whether a curriculum helps learning. The training curves rule out the
  "under-trained" objection: every arm peaks between iteration 17 and 51 and declines
  monotonically, `off` included.

  *Compute, corrected.* The release used **128 GPUs**; my earlier 4.08 × 10⁹-transition
  figure was single-GPU arithmetic and 128× low. But samples are the wrong currency: PPO
  performs `num_learning_epochs × num_mini_batches` = **20 gradient steps per iteration
  regardless of `num_envs`**. The release took 41,550 iterations = 831,000 gradient steps.
  20,000 iterations buys **~48% of its gradient steps** against ~0.09% of its samples.
  That is what makes a from-scratch probe arguable at all.

  *The real blocker was never compute — it was a termination threshold.* From scratch,
  under the stock **training** preset (which is stricter than the **eval** preset):
  `foot_pos_xyz` 0.55, `ee_body_pos` 0.38, `anchor_ori` 0.13, **`time_out` 0.0007** — 93%
  of episodes die on tracking error in 0.25 s and essentially none reach the end of a
  motion, against 76% time-out for the trained policy. `threshold_adaptive` is *not* a
  curriculum; it only loosens for crouching clips. Relaxing in two steps raised episode
  length 12.8 → 22.7 → **30.4**, but each step merely moved the wall between tracking
  terms, and **`anchor_pos` stayed at 0.000 throughout**: the robot never falls. It stands
  and is killed for limb placement.

  | thresholds | length | time_out | dominant term |
  |---|---:|---:|---|
  | strict (0.15/0.15/0.2/0.2) | 12.8 | 0.002 | foot 0.55, ee 0.38 |
  | `tracking/base` (0.25, no foot term) | 22.7 | 0.008 | **ee 0.903** |
  | upstream term defaults (0.5/0.5/0.5/1.0) | 30.4 | 0.003 | **foot 0.696** |

  Note `tracking/base` composes the *non-adaptive* terms at 0.25, **tighter** than the
  adaptive terms' own 0.5 default, and drops the low-pelvis allowance two clips need — so
  it was the wrong relaxation. The launcher now takes `--termination-thresholds default`,
  reverting the four thresholds the strict preset overrides to the values their own
  `terms/*.yaml` declare. Every number is upstream's; none is ours. Preregistered as **one**
  revert with no second relaxation (`lucid_scratch_probe_preregistration_20260828.json`,
  logical sha `c19f67d259fce645`).

  *A label that was wrong all day.* λ scales **event-manager** terms only. The motion
  command term applies reset randomization on every training reset regardless of λ — root
  velocity ±0.5 m/s, ±0.78 rad/s yaw, pelvis ±0.05 m, joints ±0.1 rad — because
  `dr_scaling` has **zero** references to the command manager. Arms at λ=0 were called
  "no DR" throughout, including in the stage-7 decomposition. They are *"no event-manager
  DR"*. Every receipt now records the distinction.

  *Five defects, all silent.* Four more found today, and the pattern is now the paper's
  methodological core — **every one produced a plausible number rather than an error**:
  (1) `profile_auc` returns points and `paired()` multiplied by 100 again, so H_S1's
  evidence read −137.25 for a true −1.37 pts; (2) `merge_summaries` used `dict.update()`,
  dropping seeds when two receipts share an arm; (3) the evaluator prints its receipt path
  *after* the try/finally, so the crashed stage-8 run wrote a complete 443 KB receipt that
  no driver could see — **my "wrote no receipt" was wrong, and 54 cells were nearly re-run
  on that basis**; (4) `LUCID_GPU_WAIT_SECONDS` defaulted to 0, making the capacity gate a
  kill switch rather than a queue, which is what killed stage 8 in the first place. All
  four fixed with regression tests; suite **1,262 green**.

  *Single-motion testbed.* With 16 diverse clips a fresh policy cannot track any of them
  well enough to see past the first second. On a single arms-still walk
  (`walk_hands_on_back_loop_002`, 4.03 s), `ee_body_pos` falls **0.903 → 0.000** and
  `anchor_pos` stays 0.000: the sole failure mode becomes foot placement (`foot_pos_xyz`
  0.977). That is a well-posed task with one axis of difficulty. Four candidates are under
  test, chosen from the pool's own `family` metadata **before any of them ran**.

  *Discipline note.* Choosing a clip after seeing which trains best would be selecting a
  result. What is being selected is a **testbed** on which from-scratch learning
  demonstrably happens; every curriculum arm then runs on that same fixed task. The
  selection is setup and is reported as setup. If none of the four learns, that is the
  answer to the feasibility question, and further clip-shopping would not be honest.

  *Infrastructure.* `--from-scratch` (verified fresh: `checkpoint: None`, `resume: None`,
  no "Resuming training from" in the log), `--horizons` for capsules along one trajectory,
  `--keys` for named single-motion subsets that still refuse `dev`/`test`, `--wandb-project`
  streaming live to `lucid-scratch`, and a measured VRAM model — peak = 4002 + 2.386·N MiB,
  so 1024 envs = 7,076 MiB total and 1280 = 7,887 (receipt `vram_ladder_20260828_131226`).

- **2026-08-28 16:07 — THE BASELINE WORKS. Plain single-motion tracking, from scratch.**
  Receipt `single_motion_baseline_milestone_20260828.json`;
  wandb `https://wandb.ai/16726/lucid-single-motion/runs/r5ovlrbg`.

  One 4.03 s walk clip (`walk_hands_on_back_loop_002__A066_M`, walk family, drawn from the
  `adaptation` partition, **zero overlap with the dev panel**), fresh initialisation,
  1024 envs, seed 8600, no event-manager DR, termination thresholds at their upstream
  term-file defaults. 2,538 iterations in two hours at 2.48 s/iter (9,894 env-steps/s,
  8.6 GB total device).

  | iterations | episode length | reward |
  |---|---:|---:|
  | 1–211 | 27.1 | 1.51 |
  | 423–633 | 39.2 | 2.76 |
  | 845–1055 | 100.0 | 6.87 |
  | 1267–1477 | 145.6 | 10.65 |
  | 2322–2532 | **174.5** | **13.57** |
  | (at ~2,900) | **184.6** | — |

  | termination | start | at ~2,900 |
  |---|---:|---:|
  | **`time_out`** (reached the END of the motion) | 0.000 | **0.987** |
  | `foot_pos_xyz` | 0.075 | 0.060 |
  | `ee_body_pos` / `anchor_pos` | 0.000 | 0.000 |

  Episode length **26.9 → 184.6** (6.9×), reward **1.41 → 13.6** (9.6×), and **98.7% of
  episodes now run the clip to completion** where none did at the start. The clip is
  4.03 s ≈ 201 control steps, so the mean episode covers ~92% of it. And it is genuinely
  *tracking*, not merely surviving: every tracking reward term rose 3–31×
  (`relative_body_ori` 30.9×, `vr_5point_local` 11.5×, `body_angvel` 10.5×,
  `body_linvel` 9.9×). Entropy −37.9 → 11.5, action-noise std 0.066 → 0.361.

  **What this settles.** The earlier from-scratch failure was the *task*, not the method:
  16 diverse clips (jumps, runs, dances) are unlearnable at this scale, one walk is
  comfortably learnable in two hours on one consumer GPU. It also retires the "not
  converged" objection from the fine-tuning era — here we can watch a policy go from
  nothing to competent, which is exactly the regime a curriculum claim belongs in.

  **What it does not settle.** Convergence (episode length is flattening but reward is
  still rising); generalisation (one motion, and the frozen 102-motion dev panel is not a
  meaningful test of a single-motion policy — the evaluator needs a change before the
  comparison can be scored); and anything about curricula, which is what comes next.

  This is now **the baseline every arm is measured against**: same motion, same fresh
  initialisation, same envs, same thresholds, same budget.

- **2026-08-30 01:30 — Seed 8600 complete for all four arms; the controller's failure
  caught live; two more silent defects; the MaxRL/PLR memo.**

  *The gap does not gate — it anti-gates.* With all four seed-8600 cells finished, the
  curriculum jsonl shows what the latent gap actually does over a from-scratch run.
  In `lucid_s4_rg` the gap q90 **rose monotonically with competence** — 0.435 (it 1–500)
  → 0.599 (2500–3000) → 0.705 (5500–6000) → 0.796 (7500–8000) — crossed the 0.778
  set-point near iteration 7000, and the PI controller then **cut λ from 0.96 to 0.15
  over the final 1,000 iterations**, with zero guard trips, while training return jumped
  11.9 → 14.4 because the policy was suddenly on easy physics. The controller reduced
  difficulty exactly when the policy was most capable. Its `final_checkpoint` is
  therefore trained on λ ≈ 0.15 for its last 500 iterations and is not the mixture arm;
  the **h6000 capsule** (λ ≈ 0.99) is, and has been exported and queued for evaluation.
  `lucid_rg`'s gap followed a different single-env path (peak 0.658 at it 1500–2000, then
  fell to 0.27) and stayed at λ = 1.000; both are one environment, 24 windows per
  iteration, so the two trajectories differ by sampling noise and phase coverage as much
  as by anything the policy did.

  *Why: the gap is phase-censored.* At constant physics (`off`, λ = 0 throughout) the gap
  is **non-monotone in competence**: 0.434 at 27-step episodes, **0.522 at 137 steps**,
  0.161 at 186 steps. A 27-step episode covers only the first half-second of the clip —
  the easiest phase, starting from the reference pose — so the 16-frame windows the
  encoder sees are easy *by construction* early on; the gap reads low, the controller's
  error term is positive, and λ ramps to 1 in 57 iterations. Only after ~2,500 iterations,
  when episodes cover the whole clip, does the gap become a competence measure. Any
  window-based error measured on short episodes will do the same. The error-vs-physics
  picture at convergence (fixed ÷ off, both converged): latent gap 3.63×, **torque
  saturation 3.80×**, undesired-contact 2.48×, anchor-pos (world) 2.34× but
  length-confounded (drift accumulates), local body-pos/joint-pos only 1.15–1.27× but
  clean in competence (corr −0.98). Physics shows up in *effort*, not kinematics, once
  the policy is competent — a converged policy tracks almost as well at λ = 1 and pays in
  torque. And the observer tracks **one environment** (`tracked_env=0`); per-stratum
  control was never possible on that basis.

  *Defect 6 — extrapolated friction was physically invalid.* At 1.5× the friction envelope
  [0.3, 1.6] centred on 0.95 becomes **[−0.025, 1.925]**; verified in the phys_150 receipt.
  PhysX does not accept negative friction, and dynamic could exceed static. Every
  extrapolated cell reported so far (phys_125, phys_150) carried that low tail, so the
  no-DR arm's 0.564 at phys_150 is partly a near-frictionless-ground number. Fixed at
  `f9e273b`: `clamp_physical` (friction ≥ 0.05, dynamic ≤ static, restitution ≤ 1, mass
  ratio ≥ 0.1), applied on the evaluation path only, recorded in the receipt. Those cells
  plus new phys_175 / phys_200 / lat_50ms are being re-evaluated now; earlier
  extrapolation numbers are superseded.

  *Defect 7 — receipt provenance.* The evaluator symlinks one resolved `config.yaml`
  beside every checkpoint it scores, so `fixed` and `lucid_rg` checkpoints sat beside a
  config saying `mode=off`. Nothing loaded wrongly (shared architecture); the provenance
  was false. Each arm now records its own `run_dir`. That is seven silent defects, every
  one of which would have produced a plausible number.

  *MaxRL / PLR memo (five verified reads).* Neither mechanism transfers as published:
  MaxRL is REINFORCE over binary terminal reward with rollout groups and no critic; we
  have PPO, GAE, dense reward, one trajectory per env, advantages normalised globally.
  The only honest MaxRL object is a per-stratum completion rate, and its weight
  w_T(p) = (1−(1−p)^T)/p is **inert everywhere we currently train** — in-envelope success
  is 0.91–1.00 and even phys_150 is 0.924, so w₄ ∈ [1.00, 1.11]. PLR transfers in shape
  (no external difficulty signal, score from the learner's own value error, a level
  notion we already have in strata) but its Value Correction Hypothesis is only
  half-satisfied here: the critic does not observe φ, and dense reward makes |GAE| on a
  solved level nonzero and intensity-scaled. What both papers say in unison, and every
  measurement agrees with, is a *target* not a mechanism: **the informative region is the
  frontier, and our frontier is outside the training envelope.** Ranked: P1 extended-
  support 2×2 (`fixed_150`, then `mix_150` only if a retention trade-off appears; 16.5
  GPU-h; needs `allow_extrapolation` threaded through the controller, friction clamps,
  `--max-delay 12` because the delay term **silently clamps** to capacity); P2 stratum-
  level replay, gated on P1 showing a trade-off; P3 zero-GPU instrumentation (per-stratum
  completion telemetry, per-episode φ in receipts, the set-point replay tool); P4 MaxRL
  weighting, predicted null unless λ_top ≥ 2. Set-point replay on the recorded trace: 0.778
  → mean λ 0.996; the manuscript's own μ+3σ rule → 1.075 → 0.998; the run mean 0.441 →
  bang-bang (46% of iterations at λ ≤ 0.05, 41% at ≥ 0.95). **No set-point closes this
  loop.** Committed story if P1 loses: the diagnosis, the frontier-centred instrument, and
  the audit protocol.

- **2026-08-30 02:20 — Signal design: what the recorded tracking errors actually are, and
  what the gap actually measures** (five reads, adversarially verified; two claims
  re-checked by hand against IsaacLab and the live config).

  *Every logged `Env/Metrics/motion/error_*` is a termination-composition statistic, not a
  tracking error.* Verified in IsaacLab `command_manager.reset()`: each metric is logged as
  `mean(metric[env_ids])` over the environments **being reset that step**, then zeroed.
  The per-env tensor is overwritten every control step, so what gets logged is the error
  at the last step before each episode ended — a mixture of "error at time-out" (≈0.04 for
  body_pos) and "error at failure" (≈0.23), weighted by the time-out fraction (two-component
  fit R² 0.985). That is why every error_* correlates −0.91…−0.98 with episode length: it is
  a proxy for the *share of episodes that failed*, which is competence, not difficulty.
  `error_joint_vel` is dominated by reference speed at the snapshot frame and is unusable.
  `error_anchor_pos` is world-frame and accumulates XY drift (the `anchor_pos` termination
  is z-only, so 0.000 there means "never dropped 0.5 m", not "no error"). Body velocities
  are in the world frame, not heading-aligned. Eval `mpjpe_*` averages *all* clip frames
  with no termination mask, and terminated envs restart at frame 0 and keep contributing;
  only the success/progress metrics are clean.

  *The latent gap is an effort meter.* Commanded = `joint_pos_target`, the pre-delay PD
  target, so `q_target − q = τ/Kp + (Kd/Kp)·q̇`: the gap is torque over stiffness. The
  encoder (a denoising autoencoder fit to reference clips only — no policy involved) embeds
  an uncentred latent whose cosine is posture-dominated: a 50% amplitude under-tracking
  moves the gap 0.015, a 0.3 rad steady offset 0.10–0.16 — ~1.4% sensitivity to dynamics,
  blind to foot placement. **The decisive test is the twin pair:** `fixed` and `lucid_rg`
  both sat at λ = 1 for their last 2,000 iterations under identical physics and read
  0.565 vs 0.305 — the gap separates two *policies* under one physics as strongly as it
  separates λ = 0 from λ = 1. It cannot be a difficulty signal. D3 is structurally
  impossible for it: `calibrate_target` (μ+3σ at λ = 0) reconstructed on this run gives
  0.744–0.853, above the λ = 1 q90 ceiling (0.44–0.57), and that ceiling is itself
  policy-dependent. **No constant binds.**

  *Two claims withdrawn or held.* "Failures cluster in phase" is **withdrawn**: the
  adaptive sampler credits a failure to the *next* episode's start bin (it runs after
  `_reset_idx` has already resampled the start), and `pre_failure_sample_window = 200` =
  the clip length pulls starts to frame 0, so bin-0's 91% share is a restart artefact; no
  phase-of-death data exists on disk. A reader also claimed the encoder was trained on
  MuJoCo-ordered joints and fed IsaacLab-ordered ones; the loader *does* have that
  permutation (`motion_lib_base.py:1597`) but the live config carries no
  `mujoco_to_isaaclab_dof`, so it is never applied — **unverified, not a defect**, pending
  a direct joint-name comparison.

  *The proposed signal (no encoder).* Use the **termination pre-image**: the per-body
  errors the termination terms already compute and discard via `.any()`, each divided by
  its in-force threshold read at runtime — m_feet = max ankle error / θ_foot, m_ee, m_pelvis,
  m_ori — so M = max(·) is "fraction of the way to being killed", unit-free, with argmax as
  the culprit body (D6). Horizon-matched: a prefix mean over the first K = 12 steps of each
  episode with coverage logged (D5). Reduced per cohort by TACE masks (D4). Self-calibrated
  by a **yardstick cohort of 64 envs held at λ = 0 in the same run**: R = q_F / q_Y, which
  is 1 at λ = 0 by construction, measures how much the dose degrades *this* policy relative
  to its own nominal execution (D1), and falls as it becomes robust (D2 in the robustness
  sense: eval foot-error ratio phys_150/phys_000 is 1.75 for the no-DR policy vs 1.19 for
  fixed). Controller: raise λ while R < R_lo, hold in band, lower above R_hi; screening
  band preregistered at R_lo = 1.10, R_hi = 1.30 from the between-arm ratios and the point
  where no-DR eval success first leaves 0.99. Hazard by cause and phase is the *guard and
  the outcome*, not the input — it saturates in-envelope (2–5 deaths per iteration late).
  Cost < 0.1 ms/step on device. Validation protocol V1–V7 preregistered on the logs on
  disk with frozen thresholds; on-disk analogues pass V1 (d = 3.9, twin ratio 4) and V2
  (monotone in the eval ladder, ≥ 5 SE per step); D2 is not evaluable on disk.

- **2026-08-30 02:30 — Corrected extrapolation ladder, and the mixture verdict.** Receipt
  `capability_benchmark_analysis_20260830.json` (supersedes every λ ≥ 1.25 cell of the
  29th: those ran with friction extrapolated to −0.025; these are clamped and the clamp is
  recorded per cell). Seed 8600, success over 512 episodes.

  | arm | λ=1.0 | 1.25 | 1.5 | 1.75 | **2.0** | 40 ms | **50 ms** | AUC[1,2] |
  |---|---:|---:|---:|---:|---:|---:|---:|---:|
  | no DR | 0.910 | 0.803 | 0.512 | 0.398 | **0.334** | 0.527 | **0.016** | 0.584 |
  | fixed | 0.994 | 0.979 | 0.924 | 0.891 | **0.820** | 1.000 | **1.000** | **0.925** |
  | lucid_rg | 0.994 | 0.975 | 0.920 | 0.844 | 0.795 | 1.000 | 0.998 | 0.908 |
  | lucid_s4_rg (final, post-collapse) | 0.969 | 0.908 | 0.732 | 0.646 | 0.518 | 0.998 | 0.918 | 0.758 |
  | **lucid_s4_rg (h6000, λ ≈ 0.99)** | 0.961 | 0.914 | 0.832 | 0.721 | 0.643 | 1.000 | 0.992 | 0.817 |

  Three things. **The extended ladder has resolution** — fixed falls to 0.820 at 2× physics
  — so a support test past λ = 1 is answerable. **The controller collapse cost real
  capability**: h6000 vs final is +10 pts at 1.5×, +12.5 at 2×, +7 at 50 ms. **But the intact
  mixture is still well below fixed at the frontier** (0.832 vs 0.924 at 1.5×, 0.643 vs
  0.820 at 2×; AUC[1,2] 0.817 vs 0.925) with **no nominal dividend** to show for it
  (in-envelope AUC 0.992 vs 0.999, both at ceiling). Three quarters of its environments
  train below the envelope edge; on a task where the envelope itself is learnable, that is
  simply less exposure to the hard end. The stage-5 "widest mixture retains best" result
  **does not transfer** from fine-tuning a competent policy to learning from scratch —
  one seed, but 10–18 points outside per-cell noise. The mixture story is dropped.

  What survives, and what it points at: capability tracks *exposure at the frontier*
  (fixed ≥ lucid_rg ≥ mixture ≥ none, in order of time spent at λ = 1), the in-envelope
  ladder cannot rank anything, and the one lever untested in training is support past
  λ = 1 — the `fixed_150` gate from the MaxRL/PLR memo. The margin arm remains worth its
  16.5 GPU-h because its claim is different: not "more capability" but "a loop that closes
  and does not anti-gate", which no signal in this programme has yet achieved.

## 2026-08-30 23:35 — the post-campaign queue had a mutual-kill race; margin arm re-chained third

Codex's PLR queue service (pid 1297554) and my margin driver both fire when the
campaign exits. Read the queue's code: its `gpu_idle_gate` is **one-shot** — any
compute PID on the card, or free VRAM < 12000 MiB, raises QueueError and the whole
~66 GPU-hour study records `failed` without launching. No wait, no retry. My margin
launcher waits at most 7200 s. Every branch of the race loses:
- Codex first (likely; 60 s tree-poll vs my 120 s): its 1024-env cell leaves
  ~9.5 GB free ≥ my 8000 MiB threshold → margin arm starts **concurrently** — the
  same 3-job collision that killed the stage-8 eval.
- Me first: Codex's gate sees < 12000 free → one-shot failure of a preregistered study.

Decision: re-chain my side only. Killed the sleeping driver (held no GPU), rewrote
`run_margin_arm.sh` to wait for the campaign marker AND for the PLR queue to reach a
terminal state (`phase` ∈ {complete, failed} in its queue_status manifest, or pid
1297554 gone), then run as before. New driver pid 1609515. Shortest-job-first argued
margin-first (16.5 h vs ~66 h) but forcing that means racing or killing another
session's live service — asymmetric risk against the user's explicit interest in the
PLR results. Serial order is now: campaign (seed 8602 running) → LUCID+PLR 2×2
(12 cells + 156 eval cells) → margin arm (3 seeds + 14-preset ladder).

Also launched: read-only adversarial audit workflow over the PLR worktree
(6 dimensions: PLR math vs paper, level/credit assignment, signal machinery,
launch safety, eval parity, test claims) — before it spends GPU-hours.

## 2026-08-31 00:05 — fixed_150 built, tested, preregistered, queued fourth; the deep report published

*The support-extension arm (memo P1) is implemented.* `allow_extrapolation` is
fixed-mode-only — the controller's config stays hard-capped in [0,1], so no
feedback loop can ever cross the envelope on its own initiative; only the
open-loop fixed mode can, explicitly. After every extrapolated apply the live
event config passes `clamp_physical` (friction floor 0.05, dynamic ≤ static)
with the report kept in the curriculum record and surfaced in the receipt
(`arm_spec.physical_clamp`); the dispatcher paths (strata, anchors) clamp their
scaled params through a new `clamp_params_physical`. The launcher refuses an
undersized delay buffer instead of letting `events_reset_safe` silently clamp
60 ms back to 40 (`fixed_150` requires `--max-delay 12`). 12 new tests; suite
**1,320 green**. Commits `5e5931a`, `45292b3`.

*Preregistered before any GPU:* `lucid_fixed150_support_preregistration_20260830.json`
(logical sha `d220c2490cfd07c0`). H_X1 support (+3 pts at phys_150/175/200 in
≥2/3 seeds vs fixed), H_X2 no nominal price (in-envelope AUC within 1 pt),
H_X3 latency frontier (+5 pts at 60 ms — the driver adds an eval-only
comparator top-up scoring the campaign arms at lat_60ms, which they were never
measured at), H_X4 manipulation check (clamp recorded, realized delay ~12
steps, else all cells void). Decision rule frozen: H_X1 pass ⇒ support is the
capability lever; H_X1 fail with H_X2 holding ⇒ capability saturates at the
envelope and the curriculum question shifts to efficiency.

*Queue is now four deep and strictly serial:* campaign (seed 8602 running) →
LUCID+PLR 2×2 (Codex, fires on campaign exit) → margin arm (waits for the PLR
study's terminal state) → fixed_150 (waits for "margin arm done"). Driver pids
1609515 (margin) and 1628399 (fixed_150), both sleeping grep loops holding no GPU.

*The deep status-and-analysis report is published* ("Anatomy of a Curriculum",
claude.ai artifact 287a1362): the fine-tuning era and the pivot, the baseline,
per-arm mechanistic reads with the live λ/gap trajectories, the five-way gap
post-mortem, the ten-defect catalog, MaxRL/PLR verdicts, the margin design,
and the queue. The PLR worktree audit workflow is still running; its verdict
gates nothing mechanically (Codex's queue fires regardless) but lands well
before the campaign ends, in time to flag anything fatal.

## 2026-08-31 00:45 — PLR worktree audit complete: core sound, eight confirmed majors, bridge planned

Seventeen agents, six dimensions, one skeptic per serious finding; receipt
`lucid_plr_worktree_audit_20260831.json`. **The implementation is real science,
not a rubber stamp**: PLR math reproduces Jiang et al. to ≤1e-12 (rank
h(S)^{1/β}, staleness, (1−ρ)P_S+ρP_C; the proportionate replay schedule is the
correct form for a fully-seen finite pool); `legacy_plant` is bit-identical to
the campaign's gap path; the next-episode-credit trap that sank my own
phase-clustering claim is genuinely avoided (bins captured pre-step, terminal
GAE credits the dying episode); the 1,490-test claim is exact (205 new tests
re-run green here). Levels = dataset-global 50-frame start bins (5 per clip).

**Confirmed after adversarial verification (severity as corrected):**
1. [major] All four arms override `pre_failure_sample_window` 200→0 — the 2×2
   is internally valid but its arms trained on a different start distribution
   than the campaign's; cross-campaign comparisons carry the caveat forever.
2. [major] Its frozen evaluator predates `clamp_physical` — its phys_125/150
   cells will carry the negative-friction tail my ladder superseded.
3. [major] Ladder trimmed: no lat_50ms / phys_175 / phys_200.
4. [major] The tracking-signal arms hard-code δ-target **0.778 — the legacy
   signal's replay value — uncalibrated for the new signal.** Same defect
   family as the anti-gating collapse; their λ trajectories must be read as
   exploratory, and the margin arm remains the only properly-calibrated
   signal test in the queue.
5. [major] Prereg `git_sha` pins nothing (implementation untracked at that
   commit); the per-file sha map does hold, so content identity survives.
6. [major] Runner cells inherit `LUCID_GPU_WAIT_SECONDS=1800`, not 7200.
7. [major] One-shot `gpu_idle_gate` (already defused on our side by the
   margin re-chain; residual risk only from a foreign process at fire time).
8. [major] No resume: one dead cell wastes the remaining hours and fails the
   campaign at final receipt validation.

Nothing on their side is editable — the queue validates its own file shas, so
any fix would break its launch. **Bridge instead:** after its receipts land,
re-score its 12 checkpoints on OUR clamped evaluator at phys_125..200 +
lat_50ms (eval-only, ~5 GPU-h, after fixed_150) so every cross-campaign
number shares one instrument. Caveat 1 is training-time and unbridgeable;
it gets written next to any cross-campaign claim.
