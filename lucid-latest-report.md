# LUCID latest report — Tier 1–4 status and ratchet confirmation

Snapshot: 2026-08-31 23:58 EDT. This is the current result and handoff ledger.
It supersedes the older live-process state in `lucid-handoff-2026-08-31.md`
and the pre-result ending of `fable.md`.

## Live continuation update

The targeted seed-8601 screen described below is complete, but the prospective
three-seed H_R2 continuation is still running. The first new cell is ratchet
seed 8600 under driver PID 221231 and trainer PID 222101. At the latest audited
snapshot it had 875/8,000 contiguous curriculum rows, reached lambda >= 0.95 at
iteration 64, remained at lambda 1.0, blocked 24 PI-requested decreases, and
had zero guard trips, zero applied lambda decreases, and no error signature.
No new capability cell has been scored, so H_R2 remains undecidable.

The exact serial order remains ratchet-8600, fresh fixed-8602, ratchet-8602,
then four new 14-cell ladders and the immutable 84-cell analysis. Reused
fixed-8600, fixed-8601, and ratchet-8601 checkpoints are already frozen
read-only. The driver is fail-closed at every cell boundary: an interrupted
`.started` cell may not be resumed or silently retrained.

CPU-side research has advanced without entering the clean confirmation
worktree:

- SONIC commit `fca5576` hardens the expanding-support sampler state contract.
- SONIC commit `4ab0e8f` hardens fixed-150/fixed-u150 launch, telemetry, and
  evaluator contracts.
- SONIC commit `c62e506` adds the nonbinding historical `lucid_rg` bridge. It
  activates only after all three H_R0 mechanism gates pass, validates 126 exact
  cells and frozen checkpoint/config provenance, and cannot alter H_R2.
- The Tier-2 support-screen analyzer is not committed yet. Independent review
  found incorrect candidate-preference semantics plus provenance and live
  mechanics gaps. Those are being fixed and adversarially tested before a
  commit or preregistration. No Tier-2 policy has launched.

## Confirmation package update

The positive one-seed screen has now been converted into a prospective,
reboot-safe three-seed continuation package. No new confirmation policy or
capability cell had run when the amendment was frozen.

- SONIC commit `ca057e658acc59773e798057980b827d65988441` hardens the analyzer,
  checkpoint freezer, and serial confirmation driver. The claim-bearing code
  runs from a clean detached worktree at `~/lucid-ratchet-confirm`; concurrent
  untracked Tier-2 files cannot enter its import path or Git state.
- The immutable [confirmation amendment](receipts/manifests/lucid_monotone_ratchet_confirmation_amendment_20260831.json)
  has SHA-256 `2064bf7a16ca159092c6ebeabfbf09bc2fe3c1b30ce359a64505503a83786044`.
  It preserves the parent endpoints, margins, seed mapping, panel, evaluator,
  and component-wise 2-of-3 H_R2 decision.
- Historical fixed seeds 8600/8601 now have explicit reconstructed bridge
  receipts. Seed 8600 uses a clean byte-identical checkpoint bundle and the
  real run config; the known invalid off-arm config beside the old artifact is
  excluded and disclosed.
- Preflight passed end to end: every frozen input hash, old seed-8601 receipt,
  checkpoint identity, resolved config source/SHA, 14-cell run set, and
  training contract reconciled.
- The continuation will train exactly three new from-scratch cells in serial:
  ratchet seed 8600, fixed seed 8602, and ratchet seed 8602. It freezes all six
  claim-bearing checkpoints before scoring four new 14-cell ladders, then
  combines them with the two immutable seed-8601 ladders for an 84-cell H_R2
  analysis.
- The serial driver is now live: PID 221231, with ratchet seed-8600 trainer PID
  222101 on experiment `curriculum_comparison_ne1024_20260831_231901`.
  Reused fixed-8600, fixed-8601, and ratchet-8601 checkpoints were frozen
  read-only before this first new cell started.

Chronology disclosure: the amendment's manually typed `created_at` was rounded
forward to 23:20 even though the file was written at 23:16:10, committed at
23:18:08, and the driver started at 23:18:41. The exact blob was therefore
prospective, but its display timestamp is inaccurate. It was not rewritten
after launch; the immutable [launch provenance receipt](receipts/manifests/ratchet_confirmation_20260831/ratchet_confirmation_launch_provenance_20260831.json)
records the correction (SHA-256
`189de9bb43610325cf4ac6931f064efe4372ae88344d8524fa9dd33adbcbed2b`).

This is a program continuation, not an independent blinded confirmation:
seed 8601 was post-selected and fixed-8600 capability was already known.
Even if all new deltas are positive, this design authorizes only the narrow
stability/noninferiority conclusion. Superiority remains unauthorized.

## Executive verdict

The first post-reboot experiment finished cleanly and **worked at its frozen
screening level**. The monotone ratchet prevented the known late anti-gate
collapse, trained for all 8,000 iterations, and passed every preregistered
one-seed noninferiority component against fixed domain randomization.

It is also a genuinely promising result at the held-out physics frontier:
relative to the seed-8601 fixed baseline, the ratchet gained 3.125 percentage
points of frontier success AUC and 1.933 points of restricted-mean progress AUC.
Those gains are descriptive, not yet a superiority claim.

The scientific status is therefore deliberately narrower than “solved”:

- **Mechanism:** pass. The ratchet deleted the observed collapse path.
- **Targeted seed-8601 screen:** pass. All frozen margins were met.
- **Three-seed training-procedure claim:** not yet decidable.
- **Adaptive-signal claim:** not supported. The raw latent gap remains invalid.
- **Motion generalization or hardware robustness:** not tested.

The earlier seed-8601 screen supervisor exited cleanly. The separate H_R2
continuation now owns the GPU as described in the live update above.

## What ran

| Item | Frozen setting | Final state |
|---|---|---|
| Treatment | `lucid_ratchet_rg`, seed 8601, 1,024 envs, 8,000 PPO iterations | Complete, exit 0 |
| Comparator | Existing fixed-DR seed-8601 checkpoint | Frozen and unchanged |
| Evaluation | Eval seed 8701, 512 aliases, 14 clamped physics/latency cells per arm | 28/28 cells complete |
| Primary metrics | Success and restricted-mean normalized episode progress | Complete |
| Decision | Targeted one-seed continuation screen | `screen_pass`; `screening_only` |

The treatment took 20,075 seconds (5.58 hours). Evaluation completed serially
for treatment and fixed, with no traceback, OOM, process kill, nonzero cell, or
checkpoint mutation.

## Tier-1 result: monotone ratchet versus fixed

### Mechanism result

| Check | Observation | Verdict |
|---|---:|---|
| Curriculum rows | 8,000 | pass |
| First iteration with lambda >= 0.95 | 70, deadline 500 | pass |
| Final lambda | 1.0 | pass |
| PI-requested decreases blocked | 951 | ratchet actively bound |
| Guard trips | 0 | no emergency brake needed |
| Actual lambda decreases | 0 | pass |
| Unguarded decreases | 0 | pass |
| Final 1,000 iterations at lambda >= 0.95 | 1,000/1,000 | pass |

This is stronger than a no-op observation. The latent-gap PI law asked to lower
difficulty 951 times; the ratchet refused every request and held the policy at
the frontier. The result validates the ratchet as a safety constraint. It does
not rehabilitate latent gap as a measure of learnable difficulty.

### Frozen capability endpoints

All AUCs are normalized trapezoidal AUCs. The in-envelope grid is
`phys_000`–`phys_100`; the frontier grid is `phys_125`–`phys_200`.

| Endpoint | Ratchet | Fixed | Ratchet - fixed | Frozen gate |
|---|---:|---:|---:|---|
| Frontier success AUC | 0.9131 | 0.8818 | **+3.125 pts** | pass |
| Frontier restricted-mean progress AUC | 0.9743 | 0.9550 | **+1.933 pts** | pass |
| In-envelope success AUC | 0.9990 | 0.9978 | +0.122 pts | pass |
| In-envelope progress AUC | 0.9997 | 0.9995 | +0.020 pts | pass |
| `lat_50ms` success, secondary | 0.9980 | 1.0000 | -0.195 pts | within margin |
| `lat_50ms` progress, secondary | 0.9987 | 1.0000 | -0.128 pts | within margin |

The favorable frontier difference is concentrated in the genuinely hard
cells, not manufactured by the saturated easy cells:

| Physics cell | Ratchet success | Fixed success | Delta | Ratchet progress | Fixed progress | Delta |
|---|---:|---:|---:|---:|---:|---:|
| `phys_125` | 0.9707 | 0.9785 | -0.781 pts | 0.9949 | 0.9946 | +0.034 pts |
| `phys_150` | 0.9414 | 0.9043 | +3.711 pts | 0.9830 | 0.9596 | +2.341 pts |
| `phys_175` | 0.8965 | 0.8535 | +4.297 pts | 0.9671 | 0.9417 | +2.543 pts |
| `phys_200` | 0.8320 | 0.7969 | +3.516 pts | 0.9505 | 0.9326 | +1.798 pts |

The latency ladder remains nearly saturated, so it provides no evidence that
the ratchet improves latency robustness.

### What can and cannot be concluded

The honest conclusion is: **the ratchet works mechanically and passed the
selected-seed continuation screen; its apparent frontier benefit now deserves
confirmatory seeds.** Seed 8601 was selected after its old `lucid_rg` collapse
was observed, so this run is post-selected mechanism evidence. Exactly three
paired training seeds are required before the frozen 2-of-3 noninferiority rule
or any directional claim can be evaluated.

The result also reinforces three earlier findings:

1. Raw training return is not a robustness ranking. The ratchet finished with
   lower return under sustained frontier difficulty than the historically
   collapsed seed-8601 controller reported after evacuating difficulty.
2. Frontier exposure recency is load-bearing. The ratchet kept all of its last
   1,000 iterations at high lambda and did not reproduce the late collapse.
3. Seed variation is material. Historical fixed seed 8600 had frontier success
   AUC 0.925, while fixed seed 8601 has 0.882. One paired seed cannot establish
   a training-procedure effect.

## Latest findings by tier

### Tier 1 — signal and controller safety

**State:** one arm implemented, trained, and evaluated; continuation gate
passed.

- `lucid_ratchet_rg` is committed and tested. It projects away PI-law
  decreases while retaining the relative-return guard as the only legal brake.
- The seed-8601 run proves that this constraint deletes the known zero-guard
  anti-gate path in a live from-scratch run.
- The default-off competence latch is implemented and tested but has never
  trained. It is not part of this result.
- The top-stratum failure band, dose/regret signal, twin-normalized gap cohort,
  return-delta-per-dose controller, and extrapolating ratchet remain proposals.
- The raw TemporalVAE latent gap remains falsified as a standalone scheduler.
  The ratchet succeeds by constraining its bad requests, not by making the
  signal semantically valid.

**Verdict:** Tier 1 is promising and has crossed its screening gate, but is not
confirmed. The next honest experiment is the frozen ratchet confirmation on
seeds 8600 and 8602, paired with fixed 8600/8601 and a newly trained fixed-8602
comparator.

### Tier 2 — distribution and support expansion

**State:** implementation seams are ready; no Tier-2 policy has trained.

- `fixed_u` and `fixed_u150` are committed and tested with eight deterministic
  levels and stratum sizes `[37,37,37,37,36,36,36,768]`, keeping 75% of the
  population at the top/frontier stratum.
- Fixed lambda=1.5 startup, warmup, physical clamping, delay-range enforcement,
  and telemetry now use the actual applied lambda. This fixes the pre-launch
  1.5-path defect found during the ratchet work.
- The old equal-split mixture is still negative evidence, not evidence against
  this new design: on seed 8600 its intact h6000 capsule scored frontier AUC
  0.817 versus fixed at 0.925 while placing only 25% of environments at the
  frontier. The proposed arm deliberately keeps 75% there.
- No `fixed_u`, `fixed_u150`, or pure fixed-150 training/evaluation receipt
  exists. PLR over motion-bin x lambda-level cells is not implemented or run.

**Verdict:** code-ready but experimentally unknown. The existing `fixed_u150`
preregistration is not launch-grade: its chronology is blemished and several
pinned hashes became stale after the fixes. File a new immutable launch record
and choose the comparator cohort before using GPU time.

### Tier 3 — difficulty-aware optimization

**State:** one launcher bug is fixed; no new optimizer experiment has run.

- `consolidation_fraction` now reaches unanchored arms instead of being silently
  dropped. Command-level tests pass.
- This does not turn the historical abrupt post-hoc consolidation result into a
  positive one; that earlier test was negative and does not answer a clean
  from-scratch with/without pair.
- Per-stratum advantage normalization/PopArt-lite, critic-only DR-context
  conditioning, and windowed phase-change LR/entropy handling remain
  unimplemented and untrained.

**Verdict:** no Tier-3 performance claim exists. Per-stratum advantage
normalization remains the cleanest next mechanism test, but only after a
Tier-2 mixture has shown enough signal to justify optimizer work.

### Tier 4 — evaluation and claim boundaries

**State:** the ratchet-specific decision instrument ran successfully; broader
instrument upgrades remain open.

- The strict analyzer verified 28 exact cells, 512 episodes per cell, matched
  training/evaluation seeds, the same panel and evaluator hashes, unchanged
  checkpoints, complete success/progress arrays, and no imputation.
- An independent recomputation from all 14,336 episode records reproduced every
  aggregate above.
- The evaluator receipts carry stale legacy metadata in `protocol.presets`
  even though their actual run records contain the frozen 14-cell ladder. The
  strict analyzer audited the actual run set, so the result stands; the metadata
  must be versioned and preregistered before confirmation rather than silently
  patched.
- The current panel is 512 aliases of the one training clip. It tests fresh
  physics draws for memorized motion tracking, not unseen-motion generalization.
- First-termination-masked prefix-K quality, alive masks, realized physics
  draws, per-channel/compositional cells, capsule retention, an online frontier
  probe, and held-out motion panels remain unimplemented or unrun. Unmasked
  MPJPE remains excluded from decisions.

**Verdict:** fit for this narrow ratchet screen, not yet a complete robustness
instrument.

## Current program status

| Workstream | Current truth |
|---|---|
| Reboot recovery | Partial seed-8602/off remains evidence only; do not resume it. Old campaign fixed-8602 and the original multi-seed ladder remain missing. |
| Ratchet chain | Seed-8601 screen complete; three-seed H_R2 continuation active on the first new training cell, ratchet seed 8600. No new capability cell has been scored. |
| GPU | Owned by trainer PID 222101 under serial driver PID 221231. Do not start another GPU workflow. |
| New code | Initial implementation `3457718`; hardened confirmation commit `ca057e658acc59773e798057980b827d65988441`. |
| Focused validation | 28 confirmation tests pass; all 1,385 tracked practice-utility tests pass with four existing warnings. Three failures belong only to concurrent untracked Tier-2 sampler tests and are excluded. |
| Repository checks | `git diff --check` passes; full `make run-checks` remains blocked by unrelated pre-existing isort failures. |

The launch began at commit `fb57e86`, while the terminal receipt records
`3457718` because the launcher samples Git state when writing the receipt. The
post-launch provenance manifest proves that all executable files were
byte-identical. Keep this disclosed as a timing deviation; do not rewrite it.

## Ordered next plan

1. **Confirmation instrument locked — complete.** The prospective amendment
   preserves the exact 14-cell semantics and treats stale legacy
   `protocol.presets` prose as non-authoritative; the immutable evaluator and
   audited run set remain binding so seed-8601 evidence is byte-identically
   reusable.
2. **Confirm Tier 1 — authorized next.** Train ratchet seeds 8600 and 8602 from scratch and the
   missing fixed seed 8602; evaluate all paired seeds on that exact instrument.
   Apply the frozen 2-of-3 rule. Do not call the current +3.125-point result a
   superiority finding.
3. **Run Tier 2 only after a fresh preregistration.** Re-pin `fixed_u`/`fixed_u150`
   code hashes, choose an honest fixed comparator, and test the 75%-frontier
   support design. Do not launch the stale shell/prereg pair.
4. **Use Tier-2 evidence to gate Tier 3.** If the support mixture retains the
   frontier but still shows optimization interference, preregister per-stratum
   advantage normalization as a clean ablation. Treat critic context as a new
   campaign generation.
5. **Advance Tier 4 in a frozen v2 instrument.** Add termination-safe quality
   metrics and held-out motions first; then realized-draw/channel attribution,
   compositional cells, and capsule retention.
6. **Close legacy evidence separately.** Rebuild—not resume—the killed
   seed-8602 comparators only where they are required by an explicit decision.
   Keep the dead PLR/margin/fixed-150 preregistrations isolated or amend them;
   their pinned hashes do not authorize launch from current HEAD.

## Durable evidence

Repository mirrors:

- [training receipt](receipts/manifests/curriculum_comparison_ne1024_20260831_144022.json), SHA-256
  `72d8f5cec69790e7ee34c867784c062e6abde68ee6f592ea635b225e51e5a169`
- [strict analysis](receipts/manifests/lucid_ratchet_screen_analysis_s8601_20260831.json), SHA-256
  `7c41e42ab378aeee1d22d57f113af7e09f2ed7672e124ed2068b2b5fa4e066d4`
- [ratchet evaluation receipt](receipts/manifests/ratchet_screen_20260831/treatment/curriculum_robustness_ne512_20260831_201524.json), SHA-256
  `82d918525b600fea25d415d6d3d17c0cf6c2400905c9f37428548a305b591b9b`
- [fixed evaluation receipt](receipts/manifests/ratchet_screen_20260831/fixed/curriculum_robustness_ne512_20260831_202312.json), SHA-256
  `1e4412413d45bc22384dc35924a932d6d41d745d62de0f2cd81df19ddb06cbb2`
- [preregistration](receipts/manifests/lucid_monotone_ratchet_preregistration_20260831.json)
- [endpoint clarification](receipts/manifests/lucid_monotone_ratchet_endpoint_clarification_20260831.json)
- [post-launch provenance bridge](receipts/manifests/lucid_ratchet_postlaunch_commit_provenance_20260831.json)

External primary artifacts remain under `~/lucid-sonic/`. The final ratchet
checkpoint is:

`~/lucid-sonic/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260831_144022/seed_8601/lucid_ratchet_rg/final_checkpoint.pt`

Its SHA-256 is
`7df270768f6d4c424fb7f8d82516e516fed154dc3a6c4ef7d5f597b72a689a41`.
Generated checkpoints and per-episode artifacts remain outside Git by design.

## Workspace handoff notes

Do not fold the concurrent untracked Gate-A/bin-sampler files or the separate
`GR00T-WholeBodyControl-plr/` worktree into this result. The untracked sampler
is not trainer-wired and still has three failing tests. The untracked generic
receipt auditor also misreads the stale evaluator metadata; it is not the
validated strict ratchet analyzer.

The large modified PLR queue-status mirror is preserved but excluded from this
report commit because its append-only polling history belongs to the dead queue,
not the ratchet result.
