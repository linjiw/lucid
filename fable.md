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
