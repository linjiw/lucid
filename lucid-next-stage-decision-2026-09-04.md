# LUCID Next-Stage Decision Memo — 2026-09-04

This memo reconciles the concentrated-effort experiment with the completed
per-channel attribution, practice-allocation, and expansion screens. It is an
operational research plan, not a claim that the pending experiments succeeded.

## 1. Evidence that changes the plan

1. **Point effort 0.40 is not a curriculum barrier in the tested setting.** A
   seed-8600 policy trained directly from scratch crossed `time_out = 0.70` by
   iteration 2000 and reached a trailing-50 mean of `0.952524` at iteration
   6000.
2. **Point effort 0.30 is empirically achievable, but only within the tested
   scope.** The point-0.40 checkpoint completed 511 of 512 evaluation episodes
   at point 0.30 on one hands-on-back clip in Isaac Lab. This is a feasibility
   witness for that policy, clip, simulator, and evaluation contract; it is not
   a universal physical-feasibility result.
3. **Robustness is strongly policy-dependent and anisotropic.** Among the six
   inherited DR channels and the healthy seed-8600 policies, push is the largest
   measured single-channel loss. Mass, CoM, and joint-offset perturbations are
   much less consequential at 3x. The weak policies have a different ordering,
   so the frontier is a property of policy plus plant, not of physics alone.
4. **Push has already passed the practice-deficit screen.** In the preregistered
   warm-start allocation study, `prac_push` scored 82.2% at Push 3x versus 73.0%
   for `prac_null` (+9.18 points). It also gained +8.20 points at held-out Push
   3.5x and +10.55 points at held-out Push 3.5x + Friction 1.5x.
5. **The same screen does not yet justify intelligent channel selection.** Over
   the common thirteen-cell suite, `prac_push` and the manageable-channel
   placebo differed by -0.07 points. Targeted push practice helps at its own
   target, but broad robustness improved similarly when the extra density was
   allocated elsewhere.
6. **Expansion feedback has not beaten a good preset.** The one-seed asymmetric
   box and matched open-loop asymmetric ramp differed by -0.39 points on the
   preregistered primary aggregate. A scalar gate did beat blind width at the
   unsafe wide corner by +9.375 points, which supports frontier protection, not
   adaptive-training superiority.

## 2. Corrections to the proposed theory

### Retain

- A curriculum barrier requires a feasible endpoint, direct-from-scratch
  failure, and recovery through staging to the identical endpoint.
- Concentrated point targets are the right place to look because they remove
  the near-nominal whole episodes supplied by ordinary interval DR.
- Practice productivity must be screened before designing an allocator.
- Any adaptive support controller must be one-way. Allowing the evaluated
  range to contract creates an observed path for training-range collapse.
- Per-channel frontiers are necessary when the measured failure surface is
  anisotropic.

### Narrow

- The static CoP calculation is a support/authority bound, not a proof of RL
  non-learnability or of a gait transition.
- “Push is the only fatal weakness” becomes “push is the dominant tested
  single-channel loss for the healthy policies under this evaluation panel.”
- “Contraction necessarily causes difficulty evacuation” becomes “the tested
  bidirectional controllers contain a structural escape route, and two of six
  long runs used it; projecting out decreases closed that route.”
- “No gain from one practice dose proves a hard wall” is too strong. A null
  would only rule out useful practice under that origin, dose, budget, and
  optimizer. In this project the relevant test was positive anyway.

### Do not use as a proof

- **CLT language.** Independent per-joint interval draws may concentrate some
  aggregate loads and may permit kinematic compensation, but the nonlinear
  closed-loop plant is not reduced to a central-limit-theorem argument. The
  mean-matched range arm is an empirical distribution-shape/compensation test.
- **A banned-parameter list.** Delay above 60 ms, rough terrain, thermal decay,
  and independent friction are deprioritized or unmeasured candidates, not
  universal physical dead zones.
- **Pyramid stairs as an established C1 barrier.** They are an exploratory
  contact-geometry candidate requiring their own feasibility and direct-learning
  screens, and they should not enter the claim-bearing SONIC table yet.

## 3. Operational barrier definition

For endpoint `e`, use four gates:

| Gate | Required observation | What it licenses |
|---|---|---|
| F — endpoint witness | A frozen policy completes the exact endpoint under isolated physics | The endpoint is eligible for a learning test in that scope |
| C1 — direct failure | The direct point arm remains below the preregistered takeoff threshold at the named horizon | A one-seed barrier candidate |
| C2 — staged recovery | A preset monotone ramp reaches the same endpoint, budget, terminal exposure, and evaluation panel while direct does not | A one-seed curriculum-barrier candidate |
| R — repeats | The C1/C2 contrast repeats across checkpoint seeds with dispersion reported | A repeatable claim in the tested architecture, motion set, simulator, and budget |

Completion is the primary learnability outcome. MPJPE, contact-mode diagnostics,
and nominal-plant retention remain secondary outcomes so a highly specialized
or contact-heavy solution is not described as nominal-quality imitation.

## 4. Serial next-stage plan

### Phase 0 — finish the live point-0.30 decision

- Keep the direct seed-8600 run untouched through iteration 1500.
- At iteration 1500:
  - `< 0.30`: C1 candidate; continue the direct arm and queue the preset ramp to
    point 0.30. The mean-matched `U[0.25, 0.35]` arm remains a separate
    distribution-shape test.
  - `0.30–0.70`: gray zone; make no decision before iteration 2000.
  - `>= 0.70`: direct takeoff; continue to the evaluation horizon and close the
    effort-barrier direction for this tested architecture/clip/budget if it
    remains learned.
- Because there is one RTX 5080, conditional arms run serially; the tripwire
  does not authorize interrupting the direct arm.

### Phase 1 — do not repeat the completed practice screen

The proposed Push 3x warm-start study is already complete. The next informative
use of compute is a minimal confirmation of the surviving uncertainty:

- repeat `{prac_null, prac_push, prac_easy}` on seeds 8601 and 8602;
- score Push 3x, held-out Push 3.5x, held-out Push+Friction 3.5x/1.5x,
  `phys_100` retention, and the frozen broad macro;
- ask separately whether push practice is productive and whether choosing push
  beats allocating the same density to a manageable-channel placebo.

The first question has a +9.18-point seed-8600 signal. The second is currently a
-0.07-point tie and is the harder requirement for an adaptive selector.

### Phase 2 — only a matched online-vs-preset test can justify a scheduler

If Phase 1 repeats the practice benefit, compare:

1. a static fixed reallocation with the same hard-example density;
2. a preset asymmetric schedule frozen from development data;
3. a one-way forward-probe gate with the same endpoints, environment count,
   optimization budget, and reported realized exposure.

The probe may estimate **current capability at a proposed frontier**. It may not
be described as estimating practice utility: the existing progress-signal audit
found that per-condition learning slopes on a competent policy are below the
noise floor at affordable windows. The adaptive arm earns its complexity only
if it improves the preregistered frozen robustness outcome or reaches a matched
target with less total selection cost. Count online probe episodes, offline
slice evaluations, wall time, and GPU-hours together.

The earlier seed-8600 screen already found no asymmetric feedback advantage over
the matched ramp at 2000 iterations. Therefore a new run must change a named
limitation—confirmation seeds, longer frontier exposure, or an exposure-matched
comparator—not simply rerun the same box controller.

### Phase 3 — expand scope only after the current claims settle

- A discrete stair-height benchmark can be screened as a new geometric contact
  axis, starting with a feasibility certificate and a direct-from-scratch
  ladder. It is a separate study, not supporting evidence for the effort result.
- Increase motion diversity before claiming a general humanoid barrier.
- Keep BeyondMimic results as sandbox evidence and out of claim-bearing SONIC
  tables.
- Do not build the utility estimator or residual allocator until the documented
  identifiability and proxy gates pass.

## 5. Provisional contribution statement

If point 0.30 also learns directly, the strongest defensible contribution is a
negative/mechanistic one: in this humanoid tracking setup, severe frozen-policy
failure and static torque bounds did not predict a from-scratch curriculum
barrier; concentrated targets were the correct test, but point effort down to
the deepest feasible tested endpoint remained directly learnable. Separately,
hard-condition practice improved push robustness, while the chosen channel did
not improve the broad suite over a matched hard-practice placebo at one seed.

If direct point 0.30 fails and the matched ramp succeeds, describe it as a
one-seed barrier candidate until the paired multi-seed contrast is complete.

## 6. Claim-bearing receipts

- `lucid-effort-point-status-2026-09-04.md`
- `receipts/analysis/lucid_channel_attribution_20260902.json`
- `receipts/analysis/lucid_practice_allocation_readout.json`
- `receipts/analysis/lucid_expansion_prototype_20260902.json`
- `receipts/analysis/lucid_progress_signal_audit_warmstart_20260902.json`
- `receipts/analysis/lucid_why_no_curriculum_wins_20260903.json`
