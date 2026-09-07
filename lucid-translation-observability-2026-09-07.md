# Physical translation observability: the next controller-foundation gate

**Completed 2026-09-07T03:35:22.846304+00:00:** All four cells and all 12 motion/phase instrument checks passed. In 6,144 horizontal-shift comparisons, active raw actor terms, assembled proprioception, G1 encoder outputs and action means were exactly unchanged. The critic's displacement input and every yaw positive control changed. [Verified online analysis](https://wandb.ai/16726/lucid-sonic/runs/xy-analysis-16a601292e5c293a).

## Result and research decision

| Check | Complete-campaign result |
| --- | ---: |
| Base states, four motions × three phases × 128 environments | 1,536 |
| Horizontal translation comparisons | 6,144 |
| Comparisons including identity/yaw controls | 9,216 |
| Maximum active raw actor / assembled proprioception change under translation | 0 / 0 |
| Maximum G1 encoder / action-mean change under translation | 0 / 0 |
| Smallest per-environment critic coordinate change across translation trials | 0.20498 m |
| Smallest per-environment G1 encoder max-coordinate change under yaw control | 0.17588 |
| Maximum rigid-translation geometry residual | 1.67e-6 m |
| Maximum restored-state difference | 0 |

All prior-history buffers and control clocks remained unchanged. The campaign used 10,752 actor-forward sample presentations including paired baselines, and 216.73 seconds measured simulator-process wall time, excluding setup/queue/analysis. These are information diagnostics, not robustness or training-efficiency scores.

The conclusion is conditional and specific: **for the tested released G1 checkpoint and identical past information, current horizontal path displacement is absent from the active actor information**. A policy may still recover from disturbances using other cues or different histories; this experiment does not test that efficacy or prove that all forms of recovery are impossible.

The next controller step is the [common path-error input and migration contract](lucid-common-path-input-design-2026-09-07.md), followed by numerical/live no-op validation and a bounded common-controller learning pilot. The two-coordinate addition must be shared by every eventual F/S/G/L arm. Preserve the return-to-path objective and attribute any input-access benefit to the controller change. Do not claim an observer or curriculum benefit from it.

Evidence: `/home/linjiw/lucid-sonic/analysis/translation_observability_20260907_a/analysis.json`, input/source/phase-report hashes, per-environment deltas and online W&B receipts. A preflight analysis-script path-type error was fixed before its W&B run; the failed preflight script/log remain alongside the successful analysis. No simulator rerun or measurement threshold change occurred.

September 7, 2026 UTC. This experiment follows the [released-controller comparison](lucid-shared-origin-contract-2026-09-07.md) and the user's request to continue toward protected multi-motion recovery.

## Why this experiment comes before robustness continuation

The released controller completed and qualified on all four original development motions in both native and LUCID execution paths. This resolves the immediate choice of shared-origin candidate. It does not establish whether the deployed actor knows its horizontal displacement from the reference path.

The paper's target remains useful robustness beyond equally protected fixed practice, with per-motion retention and actual return to the requested task. A training-side recovery observer cannot provide missing information to the deployed actor. We will not silently substitute local-pose recovery for path recovery.

## Frozen experimental design

- Four original development motions; same released weights (`e6bdab3f64a39336b3d41877d4f497d05f58af275f288ec0e6746c283ded8909`), active G1 encoder and LUCID zero-delay execution path.
- Seed 8750; 128 environments per motion; three declared reference phases: 20%, 50%, 80%.
- At each phase: unchanged-state repeat, ±0.25 m along world x, ±0.25 m along world y, and a +0.25-radian world-yaw positive control.
- Root pose is written to the actual simulator, and freshly read body poses validate rigid translation. Reference coordinates/time, root world velocity, joint positions/velocities, previous action and prior observation histories stay fixed. No simulator step occurs between paired states.
- Fresh raw terms are recomputed. Current processed observations replace the newest entry in cloned history tensors; prior entries and original circular buffers remain unchanged. A stale `update_history=False` result is not used as proof.
- Noise RNG is matched across pairs and restored afterward. Unsupported stateful modifiers/noise models fail explicitly. The real G1 encoder and actor execute on the reconstructed inputs.
- The critic's reference-relative position term must detect every translation; the G1 encoder must detect the orientation control. Failed intervention/control/restoration is an invalid instrument, not evidence of absent actor information.

This is 9,216 intervention comparisons including controls, drawn from 1,536 base states (four motions × three phases × 128 environments). They are correlated diagnostic states from one checkpoint, not independent trained policies.

The preregistered numerical checks are 5e-5 m for geometry/restoration, 1e-6 for held-fixed state and active raw-term invariance, and 1e-5 for assembled input/encoder invariance and no-op action repeat. Each environment must show >0.1 coordinate change in the critic translation term; every yaw-control encoder output must change by >1e-5. All actual deltas are retained, including action changes, irrespective of the invariance verdict.

Post-intervention rollout outcomes are **diagnostic only**. Even after state restoration, these runs do not establish no-op simulator trajectory equivalence, nominal competence, or recovery success. No PPO update or policy change occurs.

## Execution and reproducibility

Source worktree: `/home/linjiw/lucid-translation-observability`, commit `f2d5ff5`.
CPU suite: **2,140 passed**, five pre-existing deprecation warnings, 39.87 seconds. Black and Ruff pass on the three added files.

Plan: `/home/linjiw/lucid-sonic/experiments/translation_observability_20260907_a/plan.json`.
SHA-256: `16a601292e5c293afa63ce2a9a87464e3bfd72c3387f73d5607a13a7af8cc88a`.
[Online W&B campaign](https://wandb.ai/16726/lucid-sonic/runs/xy-16a601292e5c293afa).

The detached supervisor runs cells serially behind the existing 11,000-MiB free-memory gate and stops on execution or instrument-validation failure. It logs one named online W&B run per motion, source/checkpoint/plan hashes, runtime, phase receipts and numerical control outcomes. Source and inputs are hash-frozen. Retries require a new directory and preserve the original outcome.

The adjacent `status.json` is authoritative for live/completed status. Each cell stores `recovery/observability_phase_{0.2,0.5,0.8}.json`, including per-environment differences, restoration checks, raw terms, assembled actor inputs, encoder outputs and action means.

## Decision rules

1. If horizontal shifts alter actor information and controls pass, retain the current common interface and proceed to tighter competence validation and multi-motion R1 buffer collection.
2. If the shifts change task displacement and critic information while actor inputs/encoder remain invariant, qualify the limitation to this controller/modality/paired-state contract. Test a common path-error observation/interface remedy separately before curriculum comparisons. Do not claim that more PPO training alone can distinguish observationally identical states with the same history.
3. If controls or restoration fail, fix the measurement in a fresh source/experiment and preserve the failed receipt. No scientific observability conclusion follows from that run.

After this gate, the experiment order remains: independently validated solved repertoire → balanced R1 preservation → isolated disturbance/recovery calibration → strong direct prediction baselines → four-arm F/S/G/L comparison under a shared total resource contract. The utility allocator and learned recovery observer remain gated.
