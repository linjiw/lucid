# Preregistration — curriculum necessity, screening then confirmation

**Written 2026-08-28, ~11:40 EDT, on the second host.**

**Outcome-blindness statement.** This document was written in a session in which
reads outside `/home/linjiw/lucid` were blocked. The Stage 8 evaluation, the
256-environment batch-size control, the 32-iteration budget curve and the
latency ladder were all either in flight or unstarted, and none of their
receipts were readable. Everything below is therefore outcome-blind with respect
to every stage after Stage 7's evaluation, by capability rather than by
discipline. The only outcomes consulted are the ones already recorded in
`fable.md`: the untrained-origin reference and the Stage 7 decomposition, both
of which are **screening-grade** (three training seeds).

**Grade discipline.** Every result produced so far in this programme is
screening-grade. No three-seed comparison in this or any earlier stage may be
described as confirmatory. Confirmatory claims require five training seeds and
the intervals in §6.

---

## 1. Why this matrix exists, and what would make it unnecessary

With PPO, "easy to hard" losing to direct mixed training is the *expected*
result. A curriculum earns its place only when the target distribution contains
something that equal-budget direct mixed training cannot reach — because reward
is sparse there or exploration stalls. If direct mixed already learns the
hardest informative bin, then a curriculum is at best neutral and at worst adds
forgetting, and the correct output of this programme is that finding.

Two measurements already constrain the design:

- The untrained settled origin scores 89.54 / 66.01 / 60.46 / 56.21 across
  `id_clean` / `dr_050` / `dr_full` / `dr_125` (profile AUC 68.07). It is
  *already* robust to the five non-latency channels.
- Held out, plain PPO continuation with **no DR at all** (`off`) loses 23.0
  profile-AUC points against that origin, 95% CI [−28.3, −17.9], paired over
  102 motions × 3 seeds — about 90% of the damage that the full six-channel
  envelope does. The full envelope adds a further 2.65 points whose interval
  covers zero.

So the dominant effect in this testbed is **fine-tuning damage, not
randomization damage**, and no curriculum question can be answered until a
fine-tuning configuration exists that is not destructive. Stages 12 (32
iterations) and 10 (256 environments) are in the queue to find one. This matrix
is conditional on them: **if neither yields a configuration whose no-DR
continuation stays within 5 profile-AUC points of the origin, the matrix is not
run**, and the recorded conclusion is that this testbed cannot support a
curriculum comparison at accessible scale.

## 2. The non-destructive baseline gate (Gate 0)

Run before anything in §3.

- **Gate 0 passes** if some configuration `C` (iterations, `num_envs`) has
  `off`-continuation profile AUC within **5 points** of the untrained origin,
  three seeds, with the paired interval overlapping that band.
- If Gate 0 fails at both 32 iterations and 256 environments, stop. Record:
  *fine-tuning of the released SONIC policy at accessible scale is destructive
  independently of domain randomization, and the curriculum question is not
  askable on this testbed.* Do not tune further to rescue it.
- Every arm in §3 then uses `C` — same iterations, same `num_envs`, same origin.

## 3. The matrix

All arms share: the settled step-24 origin (`sha256 2fcb299a659c9cb2…`), the
`debug512` pool, the frozen 102-motion `content_dev` panel, evaluation seeds
8700–8702, and configuration `C` from Gate 0.

| # | arm | what it is |
|---|---|---|
| 1 | `origin` | no fine-tuning at all. The reference, not a treatment. |
| 2 | `off` | continuation at nominal physics. Isolates fine-tuning damage. |
| 3 | `mixed` | **direct mixed**: the complete target difficulty mixture from step 0. |
| 4 | `expand` | expanding support, uniform over `[0, d_max]`; only `d_max` advances. |
| 5 | `expand_cons` | arm 4 with the **final 40% of the budget** on the full target mixture. |
| 6 | `expand_ew` | error-weighted expansion with the **15% easy-bin floor**. |
| 7 | `lat_lucid` | latency-only / per-channel schedule; the other five channels nominal. |
| 8a | `mixed_desc_oracle` | arm 3 plus the true normalised difficulty in the observation. **Privileged.** |
| 8b | `mixed_desc_hist` | arm 3 plus an observable action/state-history context. **Deployable.** |

Arm 3 and the consolidation phase of arm 5 use the *same sampler object*
(`FixedMixtureSampler`), so "the baseline" and "the curriculum's finish" are
provably one distribution rather than two implementations meant to agree.

Arms 8a/8b are reported separately from the main claim. 8a reads simulator
randomization parameters that are not available on hardware; it bounds what
descriptor conditioning could buy and **may not support a deployment claim**.
8b uses only quantities a real robot has. A no-descriptor baseline (arm 3) is
always shown beside both.

### Frozen sampler settings

- Bins: `DifficultyBins.uniform(5)` → centres 0, 0.25, 0.5, 0.75, 1.0.
- Easy bins: the leading 40% of bins → indices {0, 1}.
- Easy-bin aggregate floor: **0.15** (inside the preregistered 0.10–0.20 band).
- Error weighting: `lag = 2` updates, `update_every = 2`, `smoothing = 0.5`,
  `temperature = 1.0`. Frozen here; not tuned against outcomes.
- Coverage: `min_samples_per_active_bin = 8` per PPO update; **fail closed**.
- `d_max` schedule for arms 4–6: linear from 0 to 1 over the first 60% of the
  budget, then held at 1. Arms 4 and 6 therefore also finish on the full
  mixture; arm 5 differs only in that its final 40% is *uniform* target mixture
  rather than whatever the sampler's weighting says.

## 4. Budget equality

Every arm gets identical: total environment steps, number of PPO updates,
rollout size (`num_steps_per_env`), `num_envs`, and evaluation calls. No arm
receives a learning-rate warm restart, an extra consolidation budget, or an
extra evaluation that another does not.

If any arm requires a different rollout size, both the **environment-step axis**
and the **optimizer-step axis** are reported, and the comparison is labelled
budget-unmatched on whichever axis differs.

At support-expansion transitions (arms 4–6) the learning rate follows a frozen
schedule and the entropy coefficient has a nonzero floor. Arm 3 receives the
*same* schedule as a function of step count even though it has no transitions,
so the schedule is never an advantage one arm has and another does not.

## 5. Staged execution

**Screening — 3 seeds (8600–8602), arms 1–7.** Explicitly labelled
screening-grade. Its only job is to kill arms.

**Confirmation — 5 seeds (8600–8604), surviving arms only.** An arm survives
screening if it passes Gate B and is not dominated on Gate C by a simpler arm.
Arms 8a/8b enter only if the confirmatory set is non-empty.

## 6. Gates and frozen thresholds

Thresholds are frozen here and may not move after outcomes are read.

- **Gate A — learnability.** On the hardest *rankable* bin, selected by
  `learnability_gate.select_hard_bin` from the **origin's** success only (60 ms
  cells banned by name; saturated bins excluded by measurement): direct mixed
  (arm 3) must either fail to beat the origin by ≥ 5 points, or be beaten there
  by some curriculum arm by ≥ 5 points, for curriculum necessity to remain
  plausible. Otherwise record **`curriculum_unnecessary`** and stop escalating.
- **Gate B — retention.** A curriculum arm must not lose more than **3 points**
  of `id_clean` success against arm 3 after consolidation, nor more than
  **8 points** against the origin.
- **Gate C — robustness.** Any improvement must appear in stratified per-bin
  success and in **worst-bin** success, with a paired 95% interval excluding
  zero — not in training reward, and not only in the macro mean.
- **Gate D — capability extension.** A confirmatory arm must improve at least
  one preregistered **non-saturated** OOD bin (`dr_125`, or a ladder rung
  strictly above the training envelope that is rankable) without failing Gate B.

A failed gate stops that branch and the negative is recorded. Gates are not
re-ordered, re-weighted, or re-thresholded after the fact.

## 7. Evaluation protocol

- Fixed held-out evaluation seed panel, stratified by difficulty. Report
  **every bin**, the success-vs-difficulty curve, the macro average, the profile
  AUC, and **worst-bin** success. No single collapsed mean is a result.
- All difficulty bins evaluated periodically **during** training, to produce
  retention/forgetting curves and locate the exact update at which easy-bin
  competence is lost.
- Uncertainty is hierarchical over training seed, evaluation seed and motion,
  via the paired motion-level bootstrap. Frames are never treated as replicates.
- `latency_60ms` / `lat_60ms` are retained as **failure bounds** and are barred
  from ranking. Ladder rungs at 10/20/30/40 ms supply the rankable latency axis
  if any of them proves non-saturated.
- The 102-motion panel is an **in-pool** partition. Every result on it is
  *fresh-physics robustness*. Motion generalization requires held-out motion
  families and is not claimed until those exist. Deployment is not claimed from
  simulation at all.

## 8. What would make this programme report a negative

Any of the following, on its own, is a complete and publishable result and must
not be tuned around:

1. Gate 0 fails: fine-tuning is destructive at every accessible configuration.
2. Gate A returns `curriculum_unnecessary`: direct mixed already learns the
   hardest informative bin.
3. Gates B–D fail for every curriculum arm.

The diagnosis already in hand — that the collapse is fine-tuning-induced rather
than DR-induced, that channel attribution present in training reward vanishes
held out, that an absolute return floor is not portable across reward scales,
that the anchor cohort contaminated both the return guard and its own target
envelope, and that two endpoints were saturated — stands regardless of which
way these gates fall.
