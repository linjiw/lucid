# LUCID Effort-Point Status — 2026-09-04

This note supersedes the operational conclusions in the 2026-09-03 effort-point
assessment. It does not alter the broader LUCID handoff or paper plan.

## Bottom line

Point 0.40 is **hard but directly learnable**, not a curriculum barrier at seed 8600.
The run was in the preregistered gray zone at iteration 1500 (`time_out = 0.5997`),
crossed the direct-learning threshold by iteration 2000 (`0.7743`), and sustained a
trailing-50 mean of `0.952524` at iteration 6000. It stopped after trainer step 7500,
not 8000; the last 50 logged iterations average `0.959536`.

Equal-step frozen evaluation at horizon 6000 shows a real adaptation effect. With every
other event and actuator channel pinned at nominal, the 0.40-trained policy beats the
nominally trained policy at the 0.40 plant by 512/512 versus 379/512 completions
(+25.98 percentage points).

## Isolated common-point ladder

Both checkpoints are from-scratch seed-8600 policies at 6000 PPO iterations. Each cell
uses evaluation seed 8700 and 512 physics/noise replicates of the same hands-on-back
clip. These are not 512 motions and not unseen-motion evidence.

| effort scale | nominal-trained | 0.40-trained | difference |
|---:|---:|---:|---:|
| 1.00 | 512/512 | 512/512 | 0.00 pts |
| 0.75 | 511/512 | 512/512 | +0.20 pts |
| 0.50 | 506/512 | 512/512 | +1.17 pts |
| 0.40 | 379/512 | 512/512 | +25.98 pts |
| 0.35 | 187/512 | 512/512 | +63.48 pts |
| 0.30 | 27/512 | 511/512 | +94.53 pts |
| 0.25 | 0/512 | 192/512 | +37.50 pts |

The policy trained at 0.40 is therefore an empirical feasibility witness down to 0.30.
The earlier statement that 0.35 or 0.30 may lie in a physically unlearnable abyss is
falsified for this policy and clip. The static CoP calculation remains a useful support
bound, but it cannot prove dynamic-task infeasibility or that a stepping strategy was
used.

The learned policy is also specialized. At nominal torque, both policies complete all
replicates, but global MPJPE is 262.7 mm for the 0.40-trained policy versus 91.4 mm for
the nominal policy. At its own 0.40 plant the adapted policy improves to 153.1 mm. Thus
completion alone should not be described as nominal-quality imitation.

## Protocol corrections

The original frozen screen left `non_latency_dr_scale = 1.0`; its six inherited event
channels were not nominal. That curve remains a valid combined-stress observation but
is not an isolated causal curve for torque capacity. The new `act_iso_*` cells preserve
the historical preset semantics while explicitly setting background DR and latency to
zero. All 29 effort limits matched the PhysX readback in every new cell.

The near-1.0 undesired-contact rate of the adapted policy is an unresolved diagnostic,
not evidence of stepping or crawling. The current metric includes contacts after scored
episodes auto-reset and does not distinguish ground from self-contact; the hands-on-back
clip makes that distinction especially important.

A targeted joint audit at point 0.30 shows that ankle pitch is the most cap-active
lower-body group (19.8% left, 16.7% right), ahead of hip roll (9.0% right, 4.5% left)
and knee (2.2% right). Upper-body joints saturate much more heavily because the all-joint
derating also constrains the hands-on-back command. Torso contact occurs on 99.7% and
pelvis contact on 79.9% of sampled steps. These traces support reduced ankle authority,
but they also make a clean stepping-strategy claim premature. The audit explicitly
labels `robot.data.applied_torque` as a pre-PhysX *requested* torque; the verified PhysX
cap, not that request tensor, bounds the realized effort.

## Next decision

Use point 0.30 for the next direct-from-scratch seed-8600 arm. It is the deepest tested
point with near-perfect success from an adapted policy and near-total failure from the
nominal policy. Keep the iteration-1500 tripwire: `< 0.30` is C1; `>= 0.70` is direct
takeoff; the gray zone continues unchanged to iteration 2000. Only if C1 fires should a
from-scratch open-loop ramp to the same 0.30 endpoint run. The mean-matched range
`U[0.25, 0.35]` is a separate distribution-shape test, not proof of a curriculum barrier.

The point-0.30 arm reached the iteration-1500 tripwire at `time_out = 0.5235`,
with mean episode length `110.77` and mean reward `6.83572`. This is the
predeclared gray zone: it does **not** satisfy C1 (`< 0.30`) and it has not yet
reached direct takeoff (`>= 0.70`). Keep the arm unchanged through iteration
2000; do not launch the conditional ramp from this gray-zone observation.

The arm continues running as experiment
`curriculum_comparison_ne1024_20260904_080627`, branch
`curriculum_comparison_ne1024_20260904_080627_s8600_act_point`, in managed execution
session `24268`. Its live log is
`/home/linjiw/lucid-sonic/outputs/effort_barrier_point030_phase2/curriculum_comparison_ne1024_20260904_080627_s8600_act_point.log`.

Claim-bearing sources are the isolated-ladder receipt and its frozen analysis receipt:

- `/home/linjiw/lucid-sonic/manifests/effort_point040_isolated_ladder_20260904/curriculum_robustness_ne512_20260904_074254.json`
- `/home/linjiw/lucid/receipts/manifests/effort_point040_isolated_ladder_analysis_20260904.json`
- `/home/linjiw/lucid/receipts/manifests/effort_point030_iter1500_milestone_20260904.json`
