# LUCID practice-allocation confirmation and next-stage decision

Date: 2026-09-05 EDT
Status: complete, frozen 117-cell audit passed

## Bottom line

Extra Push 3× practice is productive under the tested G1/SONIC continuation
contract, but the experiment does **not** establish that an online channel selector is
worth building.

- The preregistered D1 confirmation passed. Push practice improved frozen Push 3×
  success by **+3.91** and **+6.64 points** on the two untouched confirmation seeds;
  their mean is **+5.27 points**, just above the frozen +5 threshold. Adding the
  discovery seed gives **+6.58 ± 2.64 points** (mean ± sample SD, n=3).
- Transfer above the practised dose is larger: Push 3.5× improves by
  **+12.11 ± 3.81 points**, and Push 3.5× + Friction 1.5× by
  **+10.16 ± 3.53 points** across the three seeds.
- D2 did not pass. Push allocation beat the equal-density manageable-channel placebo
  by **+1.70** and **+4.46 points** on the two confirmation seeds, for a
  **+3.08-point** mean below the frozen +5 threshold. This is positive direction, but
  not authorization for a practice-utility selector.
- The preregistered nominal-completion retention guard passed: Push practice changed
  `phys_100` success by 0.00, -0.39, and 0.00 points across seeds.
- Completion is not the whole story. At nominal physics, Push practice raises
  success-conditioned global MPJPE by **31.17 ± 22.04 mm**, local MPJPE by
  **4.05 ± 0.98 mm**, the mechanical-power proxy by **10.76 ± 1.73**, and torque
  saturation by **0.82 ± 0.56 points**. These are descriptive secondary outcomes,
  not preregistered harm decisions, but they are consistent enough that the next
  study must be quality-qualified.

The bounded scientific claim is therefore: on one hands-on-back clip, two new solved
origins confirm that the measured push shortfall contains a practice deficit at this
dose and 1,500-iteration budget. The experiment does not show statistical population
significance, unseen-motion generalization, hardware transfer, or the value of an
adaptive selector.

## Experimental contract

The independent unit is a solved origin policy plus its continuation-training seed.
Seed 8600 was discovery evidence and did not grade confirmation. Seeds 8601 and 8602
loaded independently trained solved fixed-DR origins. Each arm used 1,024 environments
for 1,500 PPO iterations:

| Arm | Retained cohort | Reallocated 25% cohort |
| --- | --- | --- |
| `prac_null` | λ=1 mixed DR | λ=1 mixed DR |
| `prac_push` | λ=1 mixed DR | Push only at 3× |
| `prac_easy` | λ=1 mixed DR | Mass + CoM + joint offset at 3× |

The arm order was balanced across the three seeds. Every frozen cell used 512 matched
replicates, the same within-seed evaluation seed, and no learning. The 13 cells cover
nominal and mixed physics, Push 2×/3×/3.5×, the three manageable channels at 3×,
Friction 1.5×, and Push–Friction compositions. The instrument audit found all
**117/117** expected arm–seed–cell evaluations and all **79/79** scalar metrics in
every cell.

## Frozen decisions

| Decision | Seed 8600 | Seed 8601 | Seed 8602 | Confirmation decision |
| --- | ---: | ---: | ---: | --- |
| Push 3×: `prac_push - prac_null` | +9.18 | +3.91 | +6.64 | **Confirmed**, new-seed mean +5.27 |
| 13-cell macro: `prac_push - prac_easy` | -0.08 | +1.70 | +4.46 | **Did not clear +5**, new-seed mean +3.08 |
| Nominal: `prac_push - prac_null` | 0.00 | -0.39 | 0.00 | No >2-point completion loss |

The full macro success rates are:

| Seed | Null | Push practice | Manageable placebo |
| --- | ---: | ---: | ---: |
| 8600 | 85.20 | 87.88 | 87.95 |
| 8601 | 85.77 | 88.21 | 86.51 |
| 8602 | 85.55 | 91.21 | 86.75 |

## How the learning curves should be read

All arms are warm-start continuations, so there is no from-scratch takeoff question.
The training distributions deliberately differ. The Push arm's lower training reward
and time-out rate mean that 25% of its environments are actually experiencing the hard
Push 3× condition; they are not frozen-policy outcome comparisons. At iteration 1,500,
the three-seed trailing-50 time-out levels are approximately 0.966 for Null, 0.898 for
Push, and 0.952 for the manageable placebo. Only the matched frozen panel grades the
claim.

The public [W&B report](https://wandb.ai/16726/lucid-campaign/reports/LUCID-Practice-Allocation-%E2%80%94-Three-Seed-Push-Confirmation--VmlldzoxNzg3NDM0Mw==)
contains all 55 training scalars for nine runs and all 79 evaluation scalars for nine
frozen-policy runs. It separates the preregistered eight-metric summary from
all-episode pose/dynamics, success-conditioned pose/dynamics, physical-quality,
delay-instrumentation, and protocol panels.

## Quality and metric caveats

At Push 3×, the three-seed success gain is +6.58 points and progress gain is +1.22
points, but success-conditioned local MPJPE rises by 2.74 mm, the power proxy by 3.86,
and torque saturation by 0.75 points. At nominal physics the completion rate is flat,
yet the pose and energetic costs remain. The likely interpretation is a more forceful,
less precise recovery gait—not a free robustness improvement.

The current `undesired_contact_rate` is retained in receipts and W&B for audit
completeness, but it does not grade any decision. Its net-contact source has not been
validated as ground-only for this hands-on-back motion and can include contact on the
torso/pelvis side of legitimate self-contact. It must be repaired or renamed before it
is used as a harm gate.

## Next research priority

The next claim-bearing question is **not** “can a selector identify Push?” D2 did not
authorize that claim. It is:

> Can a one-way forward probe act as a capability/frontier guard and match or improve
> a frozen asymmetric preset under equal resources, while preserving clean tracking
> quality and accounting for the cost of its decisions?

Work proceeds serially:

1. **CPU contract and quality gate.** Add a vector-yoked replay comparator for the
   existing one-way `box_fast_300_ng` trace. Require exact environment identities,
   stratum sizes, channel vectors, no decreases, resume parity, and deterministic
   receipts. Freeze quality non-inferiority rules before seeing new-arm outcomes. The
   contact proxy cannot be one of those rules until its semantics are validated.
2. **Matched three-arm study.** Compare a fixed hard-example reallocation, a frozen
   asymmetric preset/yoked schedule derived only from development seed 8600, and the
   one-way forward-probe gate. Match origin, environment count, optimizer steps,
   practice density, candidate endpoint, and evaluation panel. Report realized
   exposure rather than stated support.
3. **Decision rule.** Credit online probing only if it improves a frozen held-out
   endpoint by the prespecified margin or reaches a matched endpoint with lower total
   selection cost, while passing nominal success and tracking-quality retention. A
   win against blind uniform 3× width is insufficient; that unsafe baseline is already
   known to be damaged.
4. **Resource accounting.** Count training GPU-hours, online probe episodes, offline
   evaluation episodes, wall time, and failed/retried simulator starts. A lower search
   bill is an outcome, not an assumption.

CPU-contract progress on 2026-09-05: the canonical vector-yoke builder is implemented
at nested commit `22475f3` and passes the full 1,852-test practice-utility suite. Applied
to the development `box_fast_300_ng` trace, it preserved 2,000 iterations, six channels,
and the fixed eight-stratum sizes `[43, 43, 43, 43, 42, 42, 640, 128]`; it reconstructed
only the ten explicitly marked warm-up rows and produced canonical digest
`cfa2375645d39acb3fcb8f5ab36ce6e2515023c81a849c1a0609259c22872581`. The audit also
found 39 rotation steps where the probe vector used for the just-completed decision is
not the probe vector dispatched for the next rollout. The yoke therefore stores the
actual per-stratum dispatch vectors rather than replaying the headline
`probe_vector`. A 731/1,269 split-resume replay matched the uninterrupted 2,000-row
sequence exactly. Runtime callback integration and the quality thresholds remain to be
completed before any GPU arm is authorized.

No utility estimator or residual allocator is authorized. If the online probe ties
the frozen preset, the result closes adaptive timing for this setup and redirects the
program to motion diversity and transfer.

## Evidence of record

- Frozen preregistration:
  `receipts/manifests/lucid_practice_allocation_confirmation_preregistration_20260904.json`
- Seed-aware analysis:
  `receipts/analysis/lucid_practice_allocation_confirmation_20260905.json`
- W&B publication and source-hash audit:
  `receipts/analysis/lucid_practice_allocation_wandb_20260905.json`
- SONIC analysis code: `gear_sonic/research/practice_utility/practice_confirmation.py`
  at nested commit `85ff922`; vector-yoke contract at nested commit `22475f3`
- All simulator logs, checkpoints, per-replicate metrics, and training/evaluation
  manifests remain outside Git under `/home/linjiw/lucid-sonic/`.
