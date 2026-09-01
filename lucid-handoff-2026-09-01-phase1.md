# LUCID handoff — Phase 1 complete, Phase 0 staged

Snapshot: 2026-09-01 16:00 EDT. Supersedes the operational sections of
`lucid-handoff-2026-09-01.md`. The scientific ledger is
`lucid-latest-report.md`; the forward plan is `lucid-research-plan-2026-09-01.md`.

## Read this first

**Set `LUCID_ROOT` before running anything.** `env/lucid_env.sh` exports it.
Without it, `gear_sonic/research/practice_utility/paths.py` falls back to
`/data/robotixx/lucid-sonic`, which does not exist on this host, and every
manifest, artifact, output and pool path silently resolves under a missing
root. This caused four phantom test failures earlier today that were reported
as pre-existing in three commit messages; the correction is recorded in
`receipts/manifests/lucid_support_expansion_screen_amendment_20260901.json`.

```bash
source /home/linjiw/lucid/env/lucid_env.sh    # or: export LUCID_ROOT=/home/linjiw/lucid-sonic
```

With it set, `tests/practice_utility` is **1635 passed, 0 failed**.

## Live state

The H_R2 confirmation driver (PID 221231) finished training ratchet seed 8602
at 8,000 iterations and is scoring its four 14-cell ladders. It owns the GPU.
Nothing else may start until it releases it.

Read the verdict with `tools/hr2_readout.sh` once
`.../ratchet_confirmation_20260831/lucid_ratchet_confirmation_analysis.json`
exists. Do not enter `~/lucid-ratchet-confirm`; it is the claim-bearing
worktree at `ca057e6` and the driver re-hashes it at every boundary.

## What changed today

### The reframe

Inside the nominal box a feedback curriculum has nothing to buy. Fixed
randomization reaches lambda = 1 by iteration ~80, saturates in-envelope
(phys_000..100 reads 0.9988 for fixed and 0.981 even for `off`), and episode
survival passes 0.93 by iteration 5,000-6,000, so roughly the last third of
training runs on a solved distribution. The only measured effect of feedback
in that box is harm: 2 of 6 unconstrained cells evacuated difficulty. The
ratchet that deletes that failure is distributionally identical to fixed DR
over 98.75% of training.

So the question moved to where fixed DR is not already optimal: deciding when
it is safe to widen support past lambda = 1.

### Signal admissibility, measured

`tools/signal_audit.py`, receipt at
`receipts/analysis/lucid_signal_audit_20260901.json`. Across the five runs
whose applied lambda is pinned at 1.0, rank correlation against the iteration
index:

| signal | range across 5 arms | mean | monotone | reversals |
|---|---|---|---|---|
| latent gap p90 | −0.30 to +0.11 | −0.04 | 54% | 19.2 |
| time-out rate | +0.985 to +0.992 | +0.987 | 92% | 4.6 |
| mean return | +0.967 to +0.980 | +0.973 | 95% | 3.2 |

Difficulty is constant in those runs, so competence is the only thing left
moving. The latent gap does not track it. That is a disqualification measured
on five independent runs, independent of any controller tuning.

The gap is worse than uninformative: its direction is set by the arm. The same
correlation is **−0.66** in the no-randomization arm, **≈0** in the fixed arms,
and **+0.39** and **+0.50** in the two arms that evacuated. In those two the
gap *rose* while lambda was being cut, which is exactly the sign that drives a
PI controller to cut further. The collapse loop is visible in the instrument.

Mean return **is** anchored at fixed difficulty. An earlier draft of the
admissibility table claimed otherwise and was corrected from this data. Return
is disqualified instead for being unbounded and scale-drifting (1.4 to about
12 here, 15.9 on a collapsed arm), so no fixed threshold has a stable meaning.

### New code (branch `research/practice-utility`, HEAD `eb899de`)

Two new curriculum modes, built as a matched pair:

- **`gate`** — holds a 12.5% probe stratum one step **above** the frontier and
  expands only when the probe's trailing-window survival clears a threshold.
  Reading the signal at the candidate level removes the fixed point that both
  the gap and the return have.
- **`ramp`** — widens the frontier on a fixed linear schedule and reads
  nothing. Shares stratum count, stratum sizes, probe placement and terminal
  support with the gate, so the arms differ in exactly one thing.

Both are monotone by construction. No code path lowers the frontier by
controller request; the return guard defaults to freezing expansion rather
than contracting support; every applied decrease is recorded as an incident in
both controller state and the run receipt. Consolidation is refused on both
modes, because it pins lambda at 1.0 and would silently contract a 1.5 arm.

New files: `survival_gate.py` (pure controller, no simulator dependency),
`survival_observer.py` (per-stratum episode survival, modelled on
`margin_observer.py`). Arms `gate_150` and `ramp_150` in
`run_curriculum_comparison.py`.

The delay-buffer capacity check is now gated on the arm's effective lambda
ceiling rather than on membership of the fixed-lambda table. An expansion arm
launched at the default `--max-delay` would otherwise have trained latency at
1.0x while its telemetry claimed 1.5x.

**Identity preserved.** The top-stratum `None` shortcut, and therefore
bit-identity with every pre-existing receipt, is untouched for any arm that
places no stratum above the frontier.

### Evaluation instrument

- `run_curriculum_robustness_eval.py` now refuses to launch a latency cell
  whose requested steps exceed `--max-delay`, and gains `lat_80ms`,
  `lat_100ms`, `lat_120ms`. Existing preset values are unchanged.
- `analyze_support_screen.py` moves the primary endpoint to
  `{phys_175, phys_200}` at equal weight with a +0.05 threshold. phys_125 and
  phys_150 are inside the training support of any 1.5 arm; they are reported,
  labelled per role, and gate nothing. schema_version 1 → 2.

### Preregistrations frozen

| file | SHA-256 |
|---|---|
| `lucid_support_expansion_screen_preregistration_20260901.json` | `b1346bb6…71184e` |
| `lucid_support_expansion_screen_amendment_20260901.json` | additive, filed before any cell |

## Next actions, in order

### 1. Read out H_R2 (0 GPU)

```bash
source /home/linjiw/lucid/env/lucid_env.sh
/home/linjiw/lucid/tools/hr2_readout.sh
```

A pass authorizes only "the monotone ratchet is a stable, noninferior safety
constraint against late anti-gating". It does not authorize superiority and
does not rehabilitate the latent gap.

### 2. Score P3 (~10 min GPU)

```bash
/home/linjiw/lucid/tools/run_phase0_scoring.sh --execute
/home/linjiw/lucid/tools/score_p3.py --out receipts/analysis/lucid_p3_readout.json
```

Scores the four unscored controller finals, headed by `lucid_rg@s8601`, the
predeclared collapse. Runs from a `ca057e6`-pinned worktree so the instrument
is byte-identical to the seven historically scored arms; the driver refuses to
start while the GPU is busy and verifies the evaluator's SHA-256.

The frozen bands, read from the committed preregistration by the scorer:

| outcome | meaning |
|---|---|
| ≥ 0.881836 | exposure hypothesis rejected upward. **Evacuation is free and our framing is wrong.** |
| < 0.67366 | rejected downward: evacuation costs more than any fitted law |
| > 0.77571 | recency rejected; a uniform dose survives |
| in [0.76086, 0.77571] | discriminates nothing; no model selection authorized |

### 3. Held-out motion evidence (~25 min GPU)

```bash
/home/linjiw/lucid/tools/run_heldout_motion_scoring.sh --execute
```

Five seed-8600 arms on k128 panels of three previously unused clips, at
phys_100/150/200. Panels are already built. This is near-motion
generalization, not the general claim, and k128 numbers must never be pooled
with the k512 ladder.

### 4. Launch Phase 2 (~27 GPU-h, ~1.2 days)

```bash
python scripts/practice_utility/run_curriculum_comparison.py \
  --from-scratch --num-envs 1024 --iterations 8000 --warmup-iterations 10 \
  --horizons 500 1000 2000 4000 6000 --seeds 8600 \
  --modes gate_150 ramp_150 fixed_150 fixed_u150 fixed \
  --max-delay 12 --termination-thresholds default \
  --motion-file $LUCID_ROOT/pools/subsets/m1_hob002/robot_filtered \
  --smpl-motion-file dummy \
  --encoder $LUCID_ROOT/artifacts/lucid_encoder_debug512.pt \
  --execute
```

`--max-delay 12` is mandatory and the launcher enforces it. The probe is
capped at the frontier ceiling, so every 1.5 arm's maximum applied intensity is
exactly 1.5 and needs 12 delay steps. That cap is not packaging: an uncapped
probe at 1.625 would give the expansion arms strictly more support than
fixed_150 and fixed_u150, confounding "the gate helped" with "the gate trained
harder".

The decisive contrast is **gate_150 against ramp_150**, never against fixed.
Beating fixed randomization would only show that difficulty rose. Decision
rules D1–D4 and mechanism gates G1–G4 are frozen in the preregistration.

A gate that never expands is a scientific result, not a failed screen. Do not
lower the threshold after seeing the trajectory.

## Rules that still bind

- The `~/lucid-ratchet-confirm` worktree is claim-bearing at `ca057e6`. Do not
  patch it or replace it with the development branch.
- The historical bridge must be built as a clean four-file additive worktree
  from `ca057e6`, not from current HEAD. Current HEAD's evaluator hashes to
  `b21863bb`, not the pinned `308e2415`.
- Do not mix instruments within one comparison. The `ca057e6` evaluator is for
  anything that must be byte-comparable with the seven historically scored
  arms; Phase 2 uses current HEAD throughout.
- Evaluation is fail-closed: an interrupted cell is evidence, never resumed.
- Do not stage the untracked Gate-A/learnability files or the
  `GR00T-WholeBodyControl-plr/` worktree. Preserve the modified PLR
  queue-status mirror as unrelated append-only state.
- The PLR 2×2 (12 cells, ~65 GPU-h) stays parked: its signal factor is moot
  after the gap finding.

## Known limitations carried forward

- Everything is one clip until item 3 above runs, and near-motion after it.
- One seed screens; it does not decide. Seed SD is ~1.6 pts on the 4-cell AUC
  and ~2.2 pts on the 2-cell held-out band.
- Above lambda ≈ 1.385 the static-friction floor clamps, so the ladder tests
  grip, mass and push rather than slip past that point.
- Terms without a dispatcher apply the frontier intensity to every environment
  including the probe, so the probe is one step above the frontier only on
  dispatched channels. The dispatched set is recorded per run in the TACE
  telemetry.
- No hardware. Nothing in this programme has run on a G1.
