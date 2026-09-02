# LUCID handoff — Phase 0 closed, Phase 2 gated and ready

Snapshot: 2026-09-01 21:00 EDT. Supersedes `lucid-handoff-2026-09-01-phase1.md`
operationally. The scientific ledger is `lucid-latest-report.md`; the forward
plan is `lucid-research-plan-2026-09-01.md`.

## Read this first

**Every driver must be launched through a wrapper that sources the environment.**
Two variables are required and neither is optional:

```bash
source /home/linjiw/lucid/env/lucid_env.sh   # exports LUCID_ROOT and OMNI_KIT_ACCEPT_EULA
export PATH="/home/linjiw/isaaclab-install/env_isaaclab/bin:$PATH"
```

- Without `LUCID_ROOT`, `paths.py` falls back to `/data/robotixx/lucid-sonic`,
  which does not exist here, and every manifest and pool path silently resolves
  under a missing root.
- Without `OMNI_KIT_ACCEPT_EULA=YES`, Isaac blocks on an interactive EULA prompt
  and every cell dies with "Unable to bootstrap inner kit kernel: EOF when
  reading a line". That is what killed the first Phase-0 attempt, receipt
  `...161052`, which is retained as excluded evidence.

## Completed and frozen

| artifact | SHA-256 | state |
|---|---|---|
| H_R2 confirmation analysis | `8656575f…70cc3c` | 0444, **pass** |
| Phase-0 aggregate analysis | `fa513677…ab9f20fd` | 0444 |
| `lucid_s4_rg@s8602` audit | `f5299176…6438f64` | 0444 |
| Phase-2 preregistration | `b1346bb6…71184e` | frozen, amendments A1–A6 |

### H_R2 — pass, and it authorizes exactly one thing

The monotone ratchet is a **stable, noninferior safety constraint** against late
anti-gating. It is **not** a superiority result and the receipt says so itself
(`superiority_claim_authorized: false`). Do not upgrade this claim.

Per-seed ratchet-minus-fixed frontier success: −0.16, +3.13, −1.17 points. Mean
+0.60, paired SD 2.25. **Two of three seeds favour fixed.** The safety evidence
is the strong part: 2,033 downward requests refused across three seeds, zero
applied, zero unguarded, terminal high-λ fraction 1.0 on every seed, against
6 of 6 unconstrained cells moving down and 2 of 6 evacuating.

### Phase 0 — 36/36 cells, four arms scored

`lucid_rg@s8601` (P3) 0.739909 · `lucid_s4_rg@s8601` 0.778971 ·
`lucid_rg@s8602` 0.801758 · `lucid_s4_rg@s8602` 0.611979.

P3 landed inside the recency band, below the uniform band, outside the two-law
overlap, and far below the 0.881836 that would have meant evacuation is free.
Evacuation costs 14.19 points against the same seed's fixed baseline and 17.32
against the ratcheted version of the same controller.

Two limits were found and are recorded in the report:

1. **The exposure law has no seed term and needs one.** The seed effect is 7.8
   points, about 4× the law's residual SD. It was invisible in the original fit
   because that fit held only seeds 8600 and 8601, which differ by ~0.6 points.
   The seed offset used to rescue three of four residuals is **post-hoc**; raw
   residuals are reported alongside.
2. **The physics ladder is not uniformly spaced.** Every arm's largest
   single-cell drop is at phys_150, the first cell where the static-friction
   floor clamps to 0.05. Foot-slip growth orders the drops. n = 4,
   correlational, no friction-held-fixed control.

The anomalous `lucid_s4_rg@s8602` is audited: sound instrument, sound run, did
not evacuate, second of four in-envelope, and loses 42.0 points across the
friction clamp against 17.9–26.6 for its siblings. It is brittle to loss of
friction, not globally weaker.

## Phase 2 — INTERRUPTED 2026-09-02 07:27 EDT after arm 1 of 5

The driver received SIGTERM during the second arm; its log ends `Terminated`.
The session that launched it did not send the signal. At the same minute a
different run was started from an interactive terminal using the
development-branch box-mode code as a `--checkpoint` continuation, and an
unrelated project's job queued behind it. **Do not kill those processes; they
are not this programme's.**

| arm | state |
|---|---|
| `gate_150` | **complete and valid**, all four mechanism gates pass (G1 0 · G2 0.0000 · G3 7,990 · G4 5,891) |
| `ramp_150` | **void** — interrupted at 1,787/8,000. Fail-closed: never resume. Directory preserved as evidence. |
| `fixed_150`, `fixed_u150`, `fixed` | not started |

No Phase-2 cell is scored; no rule changes. Amendment A9.

**To resume** once `nvidia-smi` shows no compute process: rerun
`tools/run_phase2_screen.sh --execute` through the env wrapper. It will refuse
while the GPU is busy. It must either reuse `gate_150` after hash revalidation
or the analysis must combine the preserved `gate_150` with a fresh four-arm
experiment id; the interrupted `ramp_150` is excluded either way. The decisive
D2 contrast cannot be read until `ramp_150` exists from scratch.

## Phase 2 — original launch record (superseded above)

**Experiment:** `curriculum_comparison_ne1024_20260901_232720`, driver
`run_phase2_screen.sh` (survives session resumes; it is `nohup`'d). Artifacts
under `$LUCID_ROOT/artifacts/curriculum_comparison/<experiment>/seed_8600/<arm>/`.

**The first launch (`…232033`) is VOID** and retained as excluded evidence. Three
minutes in, the gate's probe strata had never been handed to its observer: the
curriculum's `on_train_begin` runs before the observer registers itself, so the
lookup returned None and `set_strata` was never called. The gate would have held
its frontier at 1.0 for the whole run with no evidence reaching it, which in the
lambda trace is indistinguishable from an honest decision not to expand. Fixed
in SONIC `8fa9732` (lazy binding in `_survival_observer`, regression test
`TestLateObserverRegistration` fails on the parent commit). Amendment A8.
Launcher repointed to `8fa9732`; worktree `/home/linjiw/lucid-phase2` rebuilt.

**Verified live on the relaunch** before letting it run: the observer's own
`survival_*.jsonl` shows `probe_index: 7` and eight per-stratum rows with
episode counts proportional to stratum size (116 of 128 probe envs, 567 of 640
frontier envs at iteration 24). At iteration 406 the gate had a full window of
20,813 probe episodes, mean probe survival 0.007, and was withholding as
`below_threshold` — correct at that stage of training.

**Always check the observer's file, not the curriculum's flag.** The
curriculum's `survival_observer_present: true` was true throughout the void run.

### gate_150 is complete — all four mechanism gates pass

G1 applied decreases 0 · G2 max frontier drop 0.0000 · G3 probe rows 7,990/8,000
· G4 ceiling reached at iteration 5,891. Four expansions at 3,362 / 4,103 /
4,790 / 5,891, each firing at window mean ≈0.800. 2,110 iterations at 1.5.

**Phase 3 design correction (do not patch the live worktree):** the relative
return guard tripped 914 times from iteration 5,950 to 8,000, all `freeze`.
The reference return (9.39) was set at easier support; after the frontier
reached 1.5, return settled at 6.85–7.33, below 0.75 × 9.39, so the guard was
comparing a harder present against an easier past. It changed nothing here
because the gate was already at its ceiling. It would have frozen expansion for
500 iterations in any run where the 25% return drop arrived earlier. Before
Phase 3, reset the guard's best-return reference on every expansion, or replace
the return guard with a probe-survival floor, which is support-relative by
construction.

### Reading progress

```bash
E=$LUCID_ROOT/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260901_232720
tail -1 $E/seed_8600/gate_150/curriculum_*.jsonl | jq '{global_step,frontier_lambda,window_mean,withheld,fired,applied_decrease}'
tail -1 $E/seed_8600/gate_150/survival_*.jsonl  | jq '{global_step,probe_index,per_stratum:[.per_stratum[6,7]]}'
```

Expected timeline from the feasibility replay: first expansion plausibly
2,800–4,600 iterations depending on how much harder the probe is than the
frontier; a stall below 1.5 is a preregistered outcome (A4), diagnosed offline
with `tools/simulate_gate.py --survival-jsonl`.

## Phase 2 — original launch notes (superseded above)

Clean detached worktree at `/home/linjiw/lucid-phase2`, commit `dd0fd61`, zero
untracked entries. All nine preregistration-pinned files verified against the
latest hashes recorded across the preregistration and amendments A1–A6.

```bash
source /home/linjiw/lucid/env/lucid_env.sh
export PATH="/home/linjiw/isaaclab-install/env_isaaclab/bin:$PATH"
/home/linjiw/lucid/tools/run_phase2_screen.sh --execute
```

The launcher refuses unless five gates pass, each checked rather than assumed:
frozen preregistration blob, clean worktree at the pinned commit, code-state
provenance, resources (GPU idle, ≥10 GiB VRAM, ≥60 GiB disk), and a
**fail-closed gate that exercises the delay-buffer guard at `--max-delay 8` and
requires it to refuse** — so 27 GPU-hours are never committed to a guard that
was not proven live.

Five arms, seed 8600, 1024 envs × 8000 iterations, ~27 GPU-h serial, in order:
`gate_150`, `ramp_150`, `fixed_150`, `fixed_u150`, `fixed`. The feedback arm
runs first so its telemetry is inspected earliest.

### Reading the result

**The decisive contrast is `gate_150` vs `ramp_150`, never vs `fixed`.** Those
two share stratum count, sizes, probe placement and terminal support, so they
differ only in how the frontier moves. Beating fixed randomization would only
show that difficulty rose — the trap the ratchet fell into.

Primary endpoint: mean success on {phys_175, phys_200}, threshold +0.05. Per
amendment A5 that threshold is **1.83 SD** of measured paired noise (2.74
points, from three H_R2 seeds on this exact band), not the 2.3 SD the
preregistration originally claimed. Report any near-threshold result at its
true strength. One seed screens; it does not decide.

Per amendment A4, a **stalled gate is a result, not a failed screen**. If it
stalls it trains on less support than the ramp, so losing is expected and is
evidence the threshold was conservative, not that feedback is useless. Diagnose
it offline for free with
`tools/simulate_gate.py --survival-jsonl <survival_*.jsonl>`; never lower the
threshold and rerun the same seed.

Also keep phys_150 broken out in the Phase-2 tables: a third of the frozen
endpoint's weight sits on the first post-clamp cell.

## Resume point

1. If `run_phase2_screen.sh` is in flight, leave it. It is serial and
   fail-closed; receipts land in
   `/home/linjiw/lucid-sonic/manifests/support_expansion_<stamp>/`.
2. After training, score the five arms with the **current** evaluator (not the
   `ca057e6` pin — that pin is only for cells that must be byte-comparable with
   the historical ledger), then run `analyze_support_screen.py`, whose primary
   endpoint is already the uncontaminated `{phys_175, phys_200}` band.
3. The Tier-2 preregistration that `run_support_screen.sh` audits must be
   written and SHA-pinned **after** the analyzer change of commit `c501ad6`;
   any run against the old one fails closed at `audit_preregistration`.
4. Held-out motion evidence: `tools/analyze_heldout_motion.py`. Orderings only;
   it is near-motion, not motion generalization, and k128 is never pooled with
   k512.

## Rules that still bind

- `~/lucid-ratchet-confirm` is claim-bearing at `ca057e6`. Do not patch it.
- The historical bridge must be built from `ca057e6` as a four-file additive
  worktree, not from current HEAD.
- Do not mix instruments in one comparison. `ca057e6` for ledger-comparable
  cells; current HEAD throughout Phase 2.
- Evaluation is fail-closed: an interrupted cell is evidence, never resumed.
- Do not stage the untracked Gate-A/learnability files or
  `GR00T-WholeBodyControl-plr/`; preserve the PLR queue-status mirror.
- The PLR 2×2 (~65 GPU-h) stays parked; its signal factor is moot after the gap
  finding.

## Standing limitations

- One clip for every k512 number; three near-neighbour walking clips at k128.
- One seed screens. Seed SD ≈1.6 pts (4-cell AUC), ≈2.2–2.7 pts (2-cell band),
  and the between-seed effect on absolute capability reaches 7.8 pts.
- Above λ ≈ 1.385 the ladder tests grip, mass and push rather than slip.
- Terms without a dispatcher apply the frontier intensity to every environment
  including the probe, so the probe leads the frontier only on dispatched
  channels.
- Joint-error metrics are contaminated at high λ and rank nothing.
- No hardware. Nothing in this programme has run on a G1.
