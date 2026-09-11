# Second continuation seed: completed replication result

**Completed September 7, 2026.** All 57 cells of the preregistered second-seed campaign finished. The
reference-anchored recipe R1 passes the empirical retention gate at every sampled checkpoint on a second
continuation seed, and the unanchored control R0 fails at every checkpoint, as it did on the first seed.
This is a same-origin seed replication. It is not an independent origin and not a hardware result.

## What was held fixed and what changed

The campaign is registered as a replication of the frozen first-seed plan, with `scientific_change`
recorded as PPO and environment seed 8600 to 8601 only. The origin checkpoint, the original motion, the
anchor buffer and its hash, the cohort assignment seed 8600, the anchor sampling seed 8610, the
evaluation seed 8700, the five conditions, the tracking thresholds and the checkpoint schedule were all
unchanged. R2 was not repeated, and no parameter search was run.

The frozen origin, re-evaluated inside the second campaign, reproduces its first-campaign values exactly
(127.9278 mm nominal global, 42.77% hard qualification). Both seeds are therefore measured against a
common reference, and that agreement is itself an instrument check.

## Result

| Policy | Seed 8600 global / increase | Seed 8600 hard qual. | Seed 8601 global / increase | Seed 8601 hard qual. | Five-checkpoint gate |
| --- | ---: | ---: | ---: | ---: | --- |
| Origin | 127.93 mm | 42.77% | 127.93 mm | 42.77% | Reference |
| R0 | 225.87 mm / +76.56% | 49.02% | 205.43 mm / +60.58% | 48.63% | Fail on both seeds |
| R1 | 133.47 mm / +4.33% | 47.95% | 136.20 mm / +6.46% | 50.49% | Pass on both seeds |

R1 gains 5.18 percentage points of hard-condition tracking qualification over the origin on the first
seed and 7.72 on the second. R0 buys a comparable unconstrained gain on both seeds and violates
retention on both, failing at the very first sampled checkpoint (iteration 250) in both campaigns.

The margins are not identical across seeds. R1's largest sampled nominal global increase is 7.35% at
500 iterations on seed 8600 and 9.67% at 1,000 iterations on seed 8601. The second figure sits 0.33
percentage points inside the 10% budget, so the gate is close to binding on this seed even though it
passes. R1's hard-qualification trajectory is again non-monotonic (46.68, 49.71, 47.46, 51.95, 50.49
across the five checkpoints); the frozen endpoint is 2,000 iterations and remains the reported value.

## Independent verification

Recomputed directly from the 512 per-episode records in each `eval/qualified/episodes` array rather
than from the campaign's own summary. Every endpoint value above reproduces. The gate was re-evaluated
from first principles as global increase at most 10%, local increase at most 10% and completion loss at
most 2 percentage points, applied separately under nominal and original-envelope conditions at all five
checkpoints: R1 passes all ten cells, R0 fails from the first.

## Scope

Two continuations from one origin are two seeds, not two independent origins. One origin and one
walking motion support the result. The 512 aliases per condition improve within-policy precision and do
not create independent trained policies. The retention gate is an empirical development decision, not a
simultaneous confidence guarantee over its ten cells. The 600 mm global and 50 mm local qualification
thresholds are broad development limits, not robot tolerances. Nothing here establishes recovery after
disturbance, multi-motion retention, curriculum benefit, or any hardware property.

## Evidence

- Frozen plan: `/home/linjiw/lucid-sonic/experiments/retention_second_seed_20260907_c/pilot/plan.json`,
  SHA-256 `57fbff80fbcd47f740f0e7bff9f7f84e7bef7892a92b50fd61396cb4ce7827cd`.
- Completed receipt and per-cell metric hashes: `pilot/receipt.json`, all 57 cells complete.
- Aggregate analysis: `analysis.json` (55 evaluation rows, 10 trajectory verdicts).
- Independent recomputation: `receipts/analysis/fable_independent_verification_20260907.json`.
- Reported in the manuscript in Section 8.3, Table 7.
