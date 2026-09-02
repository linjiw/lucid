# LUCID latest report — Tier 1–4 status and ratchet confirmation

Snapshot: 2026-09-01 14:45 EDT. This is the current result and handoff ledger.
It supersedes the older live-process state in `lucid-handoff-2026-08-31.md`
and the pre-result ending of `fable.md`; the current operational companion is
`lucid-handoff-2026-09-01.md`.

## PHASE 0 COMPLETE — 2026-09-01 20:45 EDT — four arms scored, two new limits found

All 36 cells completed at exit code 0. The aggregate analysis is frozen 0444 at
`receipts/analysis/lucid_phase0_analysis_20260901.json`, SHA-256
`fa513677dc419c3ae73d9dd75afa0490484e6b977286fe213485c172ab9f20fd`.

| arm | frontier AUC | exposure E | residual raw | residual after seed offset |
|---|---|---|---|---|
| `lucid_rg@s8601` (P3) | 0.739909 | 0.556 | +1.5 pts | +1.5 pts |
| `lucid_s4_rg@s8601` | 0.778971 | 0.624 | +2.7 pts | +2.7 pts |
| `lucid_rg@s8602` | 0.801758 | 1.000 | −9.8 pts | −2.1 pts |
| `lucid_s4_rg@s8602` | 0.611979 | 0.625 | −14.0 pts | −6.2 pts |

Instrument audit passes on every check that could have invalidated the
comparison: per-cell `dr_ranges` hash identically across all four arms, one
512-alias panel served every cell, every checkpoint SHA-256 is unchanged across
its ladder, and each evaluation seed follows its checkpoint seed. The first
scoring attempt died on the Isaac EULA prompt and produced nine rows with zero
usable cells; it is recorded in `excluded_receipts` and retained as evidence
rather than deleted.

### Limit 1: the exposure law has no seed term, and needs one

Both large raw residuals are seed-8602 arms. Removing a seed offset of −7.8
points, measured on the two arms that pin lambda and therefore differ across
seeds only by the seed, brings three of four arms within 2.7 points — near the
instrument's replicate noise floor. That adjustment is **post-hoc**, estimated
from two arms and applied to two others, and the raw residuals are reported
alongside it.

The seed effect (7.8 pts) exceeds the law's own residual SD (1.83 pts) by about
four times. This was invisible in the original seven-point fit because that fit
contained only seeds 8600 and 8601, which differ by about 0.6 points on the
lambda-pinned arms. **The law must not be quoted without a seed term, and its
residual SD understates its error on an unseen seed.** P3 itself is unaffected:
it is a seed-8601 arm at +1.5 points raw.

### Limit 2: the physics ladder is not uniformly spaced

Every one of the four arms has its largest single-cell drop at **phys_150** —
15.2, 12.1, 19.5 and 38.7 points. That cell is the first where the
static-friction floor reaches its physical clamp: the low bound falls from
0.1375 to 0.05 between phys_125 and phys_150, a 2.75× reduction in worst-case
grip, and near-frictionless ground becomes reachable for the first time. Foot
slip across that step grows 1.33×, 1.44×, 2.09× and 2.33× respectively, in the
same order as the success drops.

This is n = 4 and correlational; no arm was run with friction held fixed while
the other channels scaled, so it is a consistent mechanism rather than a
demonstrated cause. The consequence for the endpoint is concrete: the frozen
trapezoid puts a third of its weight on the first post-clamp cell, so any
frontier AUC mixes two regimes. Phase 2 already reports worst-cell success
alongside AUC, and phys_150 should stay broken out there.

### The anomalous arm, audited

`lucid_s4_rg@s8602` scores lowest of the four and remains 6.2 points below the
law after the seed offset. Full audit at
`receipts/analysis/lucid_s4rg_s8602_audit_20260901.json`. It is neither a
broken measurement nor a broken run:

- Instrument, panel, checkpoint and config lineage all check out; its config was
  resolved from its own Hydra run directory and is distinct from its siblings.
- **It did not evacuate.** It carries the highest high-lambda iteration count of
  the four (7,939 at λ ≥ 0.95), terminal λ = 1.0, zero guard trips, and its dose
  is within 0.0003 of `lucid_s4_rg@s8601`, which scores 0.779 against its 0.612.
- The loss is localized. In-envelope it ranks second of four, within 0.9 points
  of the best. It loses **42.0 points across the friction clamp** against 17.9
  to 26.6 for its siblings. It is not globally weaker; it is brittle to loss of
  friction.

Two contributors are named, neither established: the seed effect (better
supported, n = 2 lambda-pinned arms), and a high-torque-saturation gait
signature that appears in two of three stratified seeds (weak, correlational,
and confounded because the third stratified seed also evacuated).

## P3 READ OUT — 2026-09-01 16:19 EDT — the framing survives out of sample

`lucid_rg` seed 8601, the predeclared collapse, is scored. It held lambda = 1.0
for thousands of iterations and ended at 0.062, and until now had a complete
lambda history and no robustness score of any kind. On the frozen
phys_125..200 grid at 512 episodes per cell, with the evaluator byte-pinned at
`308e2415` so it is comparable to every historically scored arm:

**Frontier success AUC = 0.739909.**

Against predictions frozen while the confirmation was still training, and read
by the scorer from the committed preregistration rather than restated:

| law | point | t(5) prediction interval | outcome |
|---|---|---|---|
| recency-weighted | 0.72473 | [0.67376, 0.77569] | **inside** |
| uniform | 0.82567 | [0.76087, 0.89047] | **outside, below** |
| "evacuation is free" | ~0.882 | — | **rejected** |

The value falls outside the two-law overlap [0.76086, 0.77571], so the design
discriminated rather than failing to. The exposure hypothesis is not rejected
in either direction: it is neither at or above 0.881836 nor below 0.67366. The
recency term is not rejected either, since 0.7399 is below 0.77571.

### What this settles

**Evacuation is not free.** That was the outcome that would have refuted this
programme's central framing, and it did not occur. The prediction was
accurate to 1.5 points, which is inside the instrument's own ~1.8-point
resolution.

**The cost is larger than we had measured.** The 7.97-point figure came from
comparing one collapsed run against its own mid-training capsule. Measured
directly against contemporaries on the same seed:

| comparison | delta |
|---|---|
| collapsed `lucid_rg@s8601` vs `fixed@s8601` | **−14.19 pts** |
| collapsed `lucid_rg@s8601` vs `lucid_ratchet_rg@s8601` | **−17.32 pts** |

The second row is the cleanest statement of the Tier-1 contribution available:
the same controller, the same seed, the same everything, differing only by the
monotone projection that refuses downward requests. 17.3 points of frontier
success AUC.

**The return inversion is now extreme.** This arm carries the highest terminal
training return in the entire campaign (15.286) and the lowest frontier
robustness of any controller arm (0.7399). An evacuating controller grades
itself on an easier exam every iteration, and the training-return monitor
reports that as success.

### What this does NOT settle

Recency is **not** established. The preregistration's own identifiability
disclosure stands: a boxcar trailing mean beats the exponential kernel out of
sample (LOO Q^2 0.977 vs 0.969), only three of the fitted points carry exposure
leverage, and one new point does not earn the phrase "recency-weighted". What
is established is the direction of the effect and the magnitude of the cost.

## H_R2 READ OUT — 2026-09-01 16:08 EDT

The three-seed confirmation completed cleanly and the analysis receipt is
frozen read-only at SHA-256
`8656575f94925eb43527bd74be68f613aed41dfba57e4ca759c29e693670cc3c`. Every
boundary marker is `OK`; the instrument audit passed at 84 cells.

**Verdict: `pass`.** Noninferiority is authorized. Superiority is explicitly
NOT authorized, and the receipt records that itself
(`superiority_claim_authorized: false`).

All four preregistered AUC components passed their frozen 2-of-3 margin at 3/3:

| component | margin (pts) | mean delta (pts) | within/paired |
|---|---|---|---|
| success_rate : frontier AUC | 2.000 | +0.597 | 3/3 |
| success_rate : in-envelope AUC | 1.000 | +0.065 | 3/3 |
| progress_rate : frontier AUC | 2.000 | +0.495 | 3/3 |
| progress_rate : in-envelope AUC | 1.000 | +0.010 | 3/3 |

### The +3.125 is now settled: it was seed noise

Ratchet minus fixed on frontier success AUC, per seed:

| seed | ratchet | fixed | delta (pts) |
|---|---|---|---|
| 8600 | 0.902995 | 0.904622 | **−0.163** |
| 8601 | 0.913086 | 0.881836 | **+3.125** |
| 8602 | 0.820312 | 0.832031 | **−1.172** |

Mean +0.597 pts, paired SD 2.247 pts. **Two of three seeds favour fixed.** The
seed-8601 gain that the earlier draft called promising is the single positive
draw of three, and the sign flips across seeds. The superseding note filed on
2026-09-01 14:45 is confirmed by measurement rather than by argument.

The preregistered informative sub-test — ratchet minus fixed positive on BOTH
8600 and 8602 with each gap above +3.0 pts, prior probability about 0.4% under
pure seed noise — did **not** trigger. Both new seeds are negative. Nothing
beyond exposure needs to be invoked to explain the ratchet arm.

### The safety claim is now three-seed

All six H_R0 mechanism gates pass on all three ratchet seeds:

| seed | first lambda >= 0.95 | blocked PI decreases | applied decreases | unguarded | terminal high-lambda |
|---|---|---|---|---|---|
| 8600 | iteration 64 | 453 | **0** | 0 | 1.000 |
| 8601 | iteration 70 | 951 | **0** | 0 | 1.000 |
| 8602 | iteration 65 | 629 | **0** | 0 | 1.000 |

2,033 downward requests refused across three runs, zero applied. Against 6 of 6
unconstrained cells moving difficulty down and 2 of 6 evacuating it terminally.
That contrast, not a frontier gain, is the Tier-1 contribution.

### New: the between-seed effect is large, and it is not the arm

Seed means of frontier success AUC, pooling both arms: 8600 = 0.904,
8601 = 0.898, **8602 = 0.826**. Seed 8602 sits about 7.8 points below the other
two for *both* arms. Pooled across the six arm-seeds the SD is 4.0 points and
the range is 9.3 points, far wider than the 1.57-point identical-exposure
cluster the earlier analysis was calibrated on.

Two consequences. P1's band test reads FAIL for `fixed@s8602` and
`lucid_ratchet_rg@s8602`, both below the recency band — but P1 carries no
falsification weight by preregistration, and this is a seed effect on absolute
capability rather than evidence about exposure. And the honest noise figure for
a *paired* comparison is now measured, not assumed: **2.25 points on the
four-cell frontier AUC**. Any one-seed screen, including Phase 2, must be read
against that.

P2 passed exactly: fixed@s8600 re-scored to 2779/3072, bit-identical to the
prior value. The 3.958e-07 difference is entirely the preregistration's 6-dp
transcription. The evaluator and panel did not drift.

### What this authorizes

- The monotone ratchet is a stable, noninferior safety constraint against late
  anti-gating. Nothing more.
- It does not rehabilitate the latent gap, which the same-day signal audit
  disqualified on five runs.
- The historical bridge (P3) and the Tier-2 support screen are both unblocked
  by this receipt.

## Live continuation update

The targeted seed-8601 screen described below is complete, but the prospective
three-seed H_R2 continuation is still running. Ratchet seed 8600 completed and
was frozen read-only after 8,000 iterations: first lambda >= 0.95 at iteration
64, final lambda 1.0, 453 blocked PI decreases, zero guard trips/decreases, and
1,000/1,000 terminal high-lambda iterations. Fresh fixed seed 8602 also
completed 8,000 iterations and was frozen read-only. Their checkpoint hashes
are respectively `0a178eff...b2cc8` and `1e230abf...3e4e8`.

The third and final training cell is ratchet seed 8602 under driver PID 221231,
launcher PID 411832, and trainer PID 411845. At the latest audited snapshot it
had 2,303/8,000 rows, reached lambda >= 0.95 at iteration 65, held lambda 1.0,
blocked 84 downward PI requests, and had zero guard trips or applied decreases.
H0500/H1000/H2000 capsules exist and no fatal log signature is present. Five
of six claim-bearing checkpoints are now frozen. No new capability cell has
been scored (0/4 ladders, 0/56 new cells), so H_R2 remains undecidable. At the
observed rate, training is due around 15:31 EDT and the final analysis around
16:05 EDT if every remaining boundary succeeds.

After ratchet-8602 freezes, the driver will score four new 14-cell ladders and
write the immutable 84-cell analysis using the two frozen seed-8601 ladders.
The driver is fail-closed at every boundary: an interrupted `.started` cell
may not be resumed or silently retrained.

CPU-side research has advanced without entering the clean confirmation
worktree:

- SONIC commit `fca5576` hardens the expanding-support sampler state contract.
- SONIC commit `4ab0e8f` hardens fixed-150/fixed-u150 launch, telemetry, and
  evaluator contracts.
- SONIC commits `c62e506`, `bee67e8`, and `c64487a` provide the nonbinding
  historical `lucid_rg` bridge, bind its live alias tree, and add its dormant
  fail-closed supervisor. It activates only after all three H_R0 mechanism
  gates pass, validates 126 exact cells and frozen checkpoint/config/raw-eval
  provenance, and cannot alter H_R2.
- SONIC commits `c33662d`, `1290416`, and `1c947d2` add the Tier-2 support
  analyzer, pin its environment bootstrap, and add its dormant supervisor.
  The package requires a future immutable preregistration, exact H_R2 pass,
  fresh three-arm training, frozen checkpoints, and a 60-cell raw evaluation.
  No Tier-2 policy has launched.

Before any new H_R2 capability cell, an audit found that the frozen panel JSON
did not itself make its mutable 512-symlink tree immutable. The tree was still
exactly intact from its August 28 creation. Root commits `10849b9` and
`9726720` prospectively recorded and activated a byte-preserving permission
lock on the exact panel receipt, panel root/tree, and source inode. Names,
targets, hashes, inodes, and source bytes did not change, and active training
continued. This protects the four new ladders from accidental mutation; it is
not WORM storage and cannot retroactively prove the reused seed-8601 tree.

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
- The continuation trains exactly three new from-scratch cells in serial.
  Ratchet seed 8600 and fixed seed 8602 are complete/frozen; ratchet seed 8602
  is active. It freezes all six claim-bearing checkpoints before scoring four
  new 14-cell ladders, then combines them with the two immutable seed-8601
  ladders for an 84-cell H_R2 analysis.
- The serial driver remains live at PID 221231. The current experiment is
  `curriculum_comparison_ne1024_20260901_100208`, ratchet seed 8602. Reused
  fixed-8600, fixed-8601, and ratchet-8601 checkpoints remain read-only.

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

**Superseded 2026-09-01 14:45.** The `+3.125` figure must no longer be
described as promising. The ratchet's applied lambda is exactly 1.0 for
iterations 101-8000, so it and `fixed` share an identical training
distribution over 98.75% of training; the gap equals the full range of the
four-arm identical-exposure cluster and is not distinguishable from seed
noise. See "Zero-GPU findings of 2026-09-01" below. The Tier-1 contribution is
the deletion of the collapse mode (2 of 6 unconstrained cells evacuate
difficulty terminally; 0 of 3 ratchet cells move down at all), not a frontier
gain over fixed.

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

## Zero-GPU findings of 2026-09-01 (reframes Tier 1)

Three results were established from artifacts already on disk, while the H_R2
chain continued to train. They are preregistered in
[exposure law](receipts/manifests/lucid_frontier_exposure_law_preregistration_20260901.json),
[grid v2](receipts/manifests/lucid_frontier_grid_v2_preregistration_20260901.json)
and their [amendment](receipts/manifests/lucid_frontier_preregistration_amendment_20260901.json)
(commits `c9ccedb`, `4c40504`).

### 1. The ratchet is distributionally identical to fixed

`lucid_ratchet_rg` seed 8601 holds exactly one distinct applied lambda over
iterations 101-8000, equal to 1.0. The 951 blocked PI decrease requests never
moved the applied lambda by a float epsilon.

The ratchet and fixed arms therefore share an **identical training
distribution over 98.75% of training**, differing only by a ~78-iteration
warm-up ramp and RNG stream divergence. Two consequences follow:

- H_R2 noninferiority is close to structurally guaranteed and carries little
  information. It should be reported as a safety check, not a hard-won pass.
- The `+3.125` point seed-8601 gap is exactly the full range of the four-arm
  identical-exposure cluster (SD 1.57 pts). It is not distinguishable from
  seed noise, and no evaluation can make it a superiority result.
- A "fixed plus warm-up" control arm is unnecessary; the question is already
  settled arithmetically at zero GPU cost.

The ratchet's informative comparator is therefore the **unconstrained
controller**, not fixed.

### 2. Anti-gating frequency, and what it costs

| arm class | 8,000-iteration cells | any downward lambda movement | terminal evacuation |
|---|---:|---:|---:|
| unconstrained (`lucid_rg`, `lucid_s4_rg`) | 6 | 6 | **2** |
| monotone ratchet | 3 | **0** | 0 |

The two evacuations were total: `lucid_rg` seed 8601 ended at lambda 0.062 and
`lucid_s4_rg` seed 8600 at lambda 0.012. The failure is arm-independent -- seed
8600 killed `s4_rg` while seed 8601 killed `lucid_rg`. This corroborates the
2/6 ledger correction already recorded in the August preregistration. The
ratchet's zero is by construction, not by luck.

Harmonized onto the frozen `phys_125`-`phys_200` grid, the one scored collapse
cost **-7.97 points** of frontier success AUC between its intact h6000 capsule
(0.7770) and its collapsed final checkpoint (0.6973).

### 2b. The gap has no restoring force — why evacuation is total

Established 2026-09-01 from the two collapse trajectories, zero GPU.

The obvious reading of the collapse is that the controller chased a drifting
signal. The telemetry says something worse: **cutting difficulty does not reduce
the controller's own error**. Binned means over the collapse window:

| arm | iterations | mean lambda | mean gap q90 |
|---|---|---:|---:|
| `lucid_rg` s8601 | 5,000-5,500 | 0.991 | 0.680 |
| | 6,500-7,000 | 0.177 | 0.790 |
| | 7,500-8,000 | 0.234 | **0.814** |
| `lucid_s4_rg` s8600 | 5,000-5,500 | 0.997 | 0.687 |
| | 7,500-8,000 | 0.160 | **0.795** |

Over iterations 5,000-8,000 of `lucid_s4_rg` s8600 the correlation between
applied lambda and the measured gap is **r = -0.201**. A working difficulty
controller requires r > 0: lowering difficulty must lower the error. Here the
sign is wrong, and in the final 1,000 iterations of `lucid_rg` s8601 the gap is
still above its 0.778 target **474 times at lambda ~ 0.2**.

This is the mechanism of totality. An *inverted* signal settles at some
equilibrium; a signal the actuator cannot move gives the integrator no
restoring force at all, so lambda winds to the rail. It explains why both
collapses end near lambda = 0.01 rather than at a partial retreat.

It also corrects a tempting over-generalization. The three candidate signals do
not fail in the same way:

- **latent gap** - no authority, wrongly signed (r = -0.20). Fails the loop.
- **training return** - inverted. Improves when difficulty falls.
- **episode survival** - inverted and saturating (~0.95 after iteration 5-6k);
  the collapsed arm scores 0.988 against fixed's 0.948.

The unifying requirement is narrower and more useful than "do not use return":
a difficulty controller needs a signal whose response to its own actuator is
both non-trivial and correctly signed. None of the three satisfies both, and
two of them reward evacuation outright.

### 3. Training return is inverted, not merely uninformative

| arm | final lambda | mean return, last 500 | frontier success AUC |
|---|---:|---:|---:|
| `lucid_ratchet_rg` s8601 | 1.000 | 10.981 | 0.9131 |
| `lucid_rg` s8600 | 1.000 | 11.268 | 0.8828 |
| `lucid_s4_rg` s8600 | 0.012 | 14.401 | 0.6973 |
| `lucid_rg` s8601 | 0.062 | 15.286 | unscored |

The two collapsed arms carry the two highest terminal returns; the ratchet
carries the lowest return and the highest robustness. The mechanism is direct:
the controller evacuates difficulty, environments get easier, and return rises
exactly as robustness falls. Three scored pairs is suggestive, not established;
the mechanism is the load-bearing part.

### 4. The exposure law is NOT established, and P3 is the test

A regression of frontier success AUC on recency-weighted exposure fits at
R-squared 0.9882. **That is an artifact, not evidence.** The five
non-stratified points alone give residual SD 0.015709 -- equal to the replicate
noise floor -- and adding the two stratified points raises residual SD to
0.018306. Lack-of-fit F(2,3) is 1.90 against F_crit 9.55. Only three of seven
points carry exposure leverage, exactly one arm in the fit is stratified, and
the two stratified points are the same run at 6000 and 8000 iterations.

Recency is likewise unidentified: uniform mean exposure scores 0.9806, and a
boxcar trailing mean beats the exponential kernel out of sample (LOO Q-squared
0.977 against 0.969). The phrase "recency-weighted" is not yet earned.

One measurement discriminates. `lucid_rg` seed 8601 -- the predeclared collapse
-- has a complete lambda series and **no frontier AUC of any kind**. Scored on
the frozen grid it separates the candidate laws:

| hypothesis | predicted frontier success AUC | t(5) prediction interval |
|---|---:|---|
| recency, H=2000 | 0.7247 | [0.6738, 0.7757] |
| uniform | 0.8257 | [0.7609, 0.8905] |
| evacuation is free | ~0.8818 (= `fixed` s8601) | -- |

The intervals overlap on [0.7609, 0.7757]; an outcome there discriminates
nothing. Across single-variable models with R-squared above 0.97 the P3 point
prediction spans 25 points, so P3 selects a member of an equivalence class at
least as much as it confirms a law. It remains the cheapest and most
informative GPU-hour available, and it produces the collapse figure the whole
narrative rests on.

### 5. The Phase-2 endpoint is contaminated

The frozen `phys_125`-`phys_200` frontier grid stops being held out the moment
any arm trains at lambda 1.5. At that lambda the evaluation boxes for
`phys_125` and `phys_150` are subsets of the training box (verified: static
friction training range is `[0.05, 1.925]` after the physical clamp, and
`phys_150` evaluation is `[0.05, 1.925]` -- identical), and those two cells
carry exactly **50% of the frontier-AUC trapezoid weight**. `phys_150` is
bit-for-bit the arm's own training marginal with latency pinned to zero.

The fix needs no new evaluation cells: `{phys_175, phys_200}` at weights
`[1/2, 1/2]` is strictly outside every arm's support and is already in the
15-preset panel the support driver runs. It costs about 16% of endpoint
resolution in spread-per-noise-SD, which is the price of an uncontaminated
endpoint. `H_X1` is contaminated by the same mechanism and must be recomputed
or explicitly demoted.

Two silent-failure traps are now recorded as blocking: a `lat_120ms` cell run
at the default `--max-delay 12` would silently produce a 60 ms cell, and a
`ratchet-150` arm would silently train latency at 1.0x while claiming 1.5x
because the delay-buffer check is gated on `mode in ARM_FIXED_LAMBDA`.

## Latest findings by tier

### Tier 1 — signal and controller safety

**State:** selected-seed arm evaluated; two additional ratchet mechanism cells
complete/active; multi-seed capability decision pending.

- `lucid_ratchet_rg` is committed and tested. It projects away PI-law
  decreases while retaining the relative-return guard as the only legal brake.
- The completed seeds 8601 and 8600 both show that this constraint deletes the
  known zero-guard anti-gate path in live from-scratch runs. Active seed 8602
  is consistent so far but is not final.
- The default-off competence latch is implemented and tested but has never
  trained. It is not part of this result.
- The top-stratum failure band, dose/regret signal, twin-normalized gap cohort,
  return-delta-per-dose controller, and extrapolating ratchet remain proposals.
- The raw TemporalVAE latent gap remains falsified as a standalone scheduler.
  The ratchet succeeds by constraining its bad requests, not by making the
  signal semantically valid.

**Verdict:** Tier 1 is promising and has crossed its screening gate, but is not
confirmed. That frozen confirmation is now active: ratchet-8600 and the new
fixed-8602 comparator are complete, ratchet-8602 is training, and the paired
capability ladders remain unscored.

### Tier 2 — distribution and support expansion

**State:** implementation, strict analyzer, and dormant supervisor are ready;
no Tier-2 policy has trained.

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
  exists. The 52-test support supervisor remains inert until a clean detached
  worktree and new frozen preregistration bind its code, environment, inputs,
  comparator, and output roots. PLR over motion-bin x lambda-level cells is
  not implemented or run.

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
| Reboot recovery | Partial seed-8602/off remains evidence only; do not resume it. The original campaign fixed-8602 and original ladder remain missing. A distinct H_R2 replacement fixed-8602 cell is now complete/frozen; it does not retroactively complete the dead campaign. |
| Ratchet chain | Ratchet-8600 and fresh fixed-8602 complete/frozen; ratchet-8602 active at 2,303/8,000 with a clean interim mechanism trajectory. Five of six checkpoints are frozen. No new capability cell has been scored. |
| GPU | Owned by trainer PID 411845 under serial driver PID 221231. Do not start another GPU workflow. |
| New code | Confirmation `3457718`/`ca057e6`; historical bridge through `c64487a`; support screen through `1c947d2`. The active confirmation still runs only detached `ca057e6`. |
| Focused validation | 235 controller/freeze/confirmation/historical/support tests pass on current SONIC HEAD; focused historical and support supervisor suites pass 44/44 and 52/52 respectively. |
| Repository checks | `git diff --check` passes; full `make run-checks` remains blocked by unrelated pre-existing isort failures. |

The launch began at commit `fb57e86`, while the terminal receipt records
`3457718` because the launcher samples Git state when writing the receipt. The
post-launch provenance manifest proves that all executable files were
byte-identical. Keep this disclosed as a timing deviation; do not rewrite it.

## Ordered next plan

Revised 2026-09-01 14:45 after the zero-GPU findings above. The ordering is no
longer a preference: it is enforced by hash pins.

1. **Finish Tier 1 — active, unchanged.** Complete/freeze ratchet seed 8602,
   run the four queued 14-cell ladders, apply the immutable component-wise
   2-of-3 rule, and record the post-evaluation panel inventory. Report the
   verdict as a safety check. Do not call `+3.125` a superiority finding, and
   state plainly that the arms share a training distribution.
2. **Score P3 next, before any code change to the evaluator.** The 42-cell
   historical `lucid_rg` bridge is the single most informative remaining
   GPU-hour: it produces the collapse figure, tests the exposure hypothesis
   out of sample, and discriminates recency from uniform. Its activation
   accepts an H_R2 verdict of `pass` **or** `fail` and is gated only on the
   H_R0 mechanism gates, so an H_R2 fail does not block it.
   Blocking construction work: no commit on `research/practice-utility`
   satisfies the bridge's four-file additive closure from `ca057e6`, so a new
   clean detached worktree must be built with only those four files added.
3. **Then, and only then, change the evaluator.** `run_curriculum_robustness_eval.py`
   is byte-pinned at `308e2415` by the bridge and by the screen followup.
   Adding grid-v2 presets or the `--max-delay` assertion before P3 runs would
   break the bridge's own instrument pin. The v2 latency ladder additionally
   needs `--max-delay 24` against seven files that assert the literal command
   slice `['--max-delay','12','--']`.
4. **Land the Tier-2 endpoint fix before writing the Tier-2 preregistration.**
   `analyze_support_screen.py` must gain `HELD_OUT_GRID` and
   `IN_SUPPORT_FRONTIER`, and `H_X1` must be recomputed on held-out cells or
   explicitly demoted. The analyzer hashes itself and asserts the live git SHA,
   so the patch must be committed first and the preregistration pinned against
   the new commit afterwards. The patch as currently drafted breaks four
   existing tests and must ship with its fixture updates.
5. **Run Tier 2 only after that, with the corrected endpoint.** Primary is
   `{phys_175, phys_200}` at `[1/2, 1/2]`, threshold `>= 0.05` (2.26 SD of the
   recomputed band noise). `{phys_125, phys_150}` is report-only and must be
   labelled in-support for the extrapolating arms. Treat any winner as a
   one-seed screen.
6. **Do not build `ratchet-150` yet.** It is blocked at three independent code
   layers, costs about 40 production lines, and carries a silent-failure trap
   in the launcher's delay-buffer gate. More importantly, P3 decides whether
   the exposure framing survives at all; if evacuation turns out to be free,
   the safety-constrained-frontier narrative loses its motivating cost.
   A candidate monotone expansion gate already exists with zero new
   instrumentation: `Env/Episode_Termination/time_out` is in `state.log_history`
   every iteration, in the same dict the curriculum callback already reads.
7. **Advance Tier 4 in a separately frozen v2 instrument.** Held-out motion
   panels are feasible today (`m1_ffloop`, `m1_fwd003`, `m1_hob003` are
   siblings of the training pool). First-termination-masked quality is NOT
   recoverable offline -- no per-frame trajectories are saved anywhere -- so it
   requires a re-run with new instrumentation. The contamination is now
   demonstrated: at `phys_200`, failed episodes score mpjpe_g 262 against 434
   for successful ones, i.e. failures look better.
8. **Close legacy evidence separately.** Unchanged from the prior plan:
   rebuild rather than resume, and keep the dead preregistrations isolated.

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
- [panel preservation amendment](receipts/manifests/ratchet_confirmation_20260831/ratchet_confirmation_panel_preservation_amendment_20260901.json), SHA-256
  `9366af3faa0ff6714ddb50368937f88e5b3211dead2a6882427d6c168fe31af9`
- [panel preservation activation](receipts/manifests/ratchet_confirmation_20260831/ratchet_confirmation_panel_preservation_activation_20260901.json), SHA-256
  `8889cd94477a35278776c4481ea12dea9bd3b1ca77b6a9269b9dd82a04ce94e0`

External primary artifacts remain under `~/lucid-sonic/`. The final ratchet
checkpoint is:

`~/lucid-sonic/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260831_144022/seed_8601/lucid_ratchet_rg/final_checkpoint.pt`

Its SHA-256 is
`7df270768f6d4c424fb7f8d82516e516fed154dc3a6c4ef7d5f597b72a689a41`.
Generated checkpoints and per-episode artifacts remain outside Git by design.

## Workspace handoff notes

Do not fold the concurrent untracked Gate-A/learnability files or the separate
`GR00T-WholeBodyControl-plr/` worktree into this result. In particular,
`learnability_gate.py`, `run_gate_a.py`, `run_fixed_u150_arm.sh`, and the
generic `audit_evaluation_receipt.py` remain unrelated and uncommitted. The
generic auditor is not the validated strict ratchet/support analyzer.

The large modified PLR queue-status mirror is preserved but excluded from this
report commit because its append-only polling history belongs to the dead queue,
not the ratchet result.
