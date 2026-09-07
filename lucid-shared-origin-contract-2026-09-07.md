# LUCID shared-controller foundation: next-stage research contract

**Physical observability result, September 7 UTC:** The four-motion/three-phase physical-state experiment completed. All 6,144 horizontal translations changed measured task/critic displacement while active actor inputs, encoder outputs and action means remained exactly unchanged; instrument controls passed. The next step is a common path-error input, no-op validation and a bounded controller-repair pilot before multi-motion R1/curriculum training. See the [completed experiment](lucid-translation-observability-2026-09-07.md) and [common-input design](lucid-common-path-input-design-2026-09-07.md).

**Completed September 7, 03:14 UTC:** All eight released-controller cells finished. Every motion in both paths achieved 100% completion and tracking qualification (128 aliases per cell). Select the released checkpoint as the shared-origin candidate; no nominal retraining is warranted by this screen. Tight competence validation and paired-state path-error observability still precede R1 continuation. [Verified W&B analysis](https://wandb.ai/16726/lucid-sonic/runs/path-analysis-7570c657d2dfbb94).

## Completed path-screen results

First-episode development endpoints; each native/LUCID entry uses the same released checkpoint and seed. All eight cells complete and qualify at 100% under the existing broad limits.

| Motion | Native global / local MPJPE (mm) | LUCID global / local MPJPE (mm) |
| --- | ---: | ---: |
| Control | 90.68 / 28.61 | 87.22 / 28.52 |
| Curved walking | 101.25 / 19.95 | 99.57 / 19.85 |
| Sideways walking | 114.33 / 21.90 | 112.99 / 21.87 |
| Stooping | 107.93 / 24.34 | 110.53 / 24.37 |

The local origin and its R1 continuation qualified on none of the three longer candidates; the released controller qualifies on all three in both paths. This resolves the immediate controller-choice question in favor of the released weights. It does not identify which part of the local origin's training history caused its limited repertoire, nor establish duration-only failure or physical infeasibility.

Every compared runtime contract field matches across paths after excluding recording identity and the intentionally different actuator types. Initial measured native-state hashes match for each pair; RNG hashes differ, so the small numerical differences are not an exact-parity result or a demonstrated actuator effect. All frozen source/input files and recorded metric/trace hashes verified. Measured evaluation wall time totals 476.09 seconds, excluding preparation, capacity waits, native-smoke attempts and analysis. Shared-GPU times are not an efficiency ranking.

Artifacts: `/home/linjiw/lucid-sonic/analysis/shared_origin_contract_20260907_a/path_screen_analysis.json` and `controller_path_comparison.{png,pdf,svg}`. The receipt also includes first-segment time-window diagnostics and observed denominators. The native-smoke cost receipt preserves 20.62 / 157.16 / 155.93 seconds from launch to final status for attempts a/b/c; these include preparation and any waits. Exact simulator-only runtime was not retained for the two failed attempts and is not invented.

September 7, 2026 UTC. This prospectively refines the [ideal-paper plan](lucid-ideal-paper-execution-plan-2026-09-06.md) using the user's latest guidance. The pasted guidance is the available source; its linked sandbox attachment is not present in this workspace.

## Decision and scientific target

Keep R1 as the selected development protection recipe. First identify a capable shared controller and verify the information required for return-to-path control. Then extend R1 over the controller's solved repertoire. Do not launch another broad optimizer, curriculum, utility-estimator, residual-allocator, or learned-observer sweep now.

The intended result is **recovery feedback that improves useful robustness over equally protected fixed practice at a common total resource budget, subject to per-motion retention**. The existing +5.18 percentage-point R1 result is against the frozen origin, not against protected fixed practice. Three continuation seeds from one origin are not three independent origins.

## Foundation comparison frozen before evaluation

| Comparison | Purpose and interpretation |
| --- | --- |
| Existing local origin, original four development motions | Preserve all prior outcomes: one solved control and three unsolved longer candidates under the broad development screen |
| Released default weights, native official sample evaluation | Establish a working released-checkpoint/configuration/sample path before interpreting the project panel |
| Released weights, native module and native actuators, four original candidates | Test released capability under the common nominal measurement contract |
| Same weights, LUCID execution wrapper at zero delay, same four candidates | Test the actuator/wrapper integration under matched nominal conditions |

The last two paths share the LUCID nominal event configuration, alias panel and measurement callback. They are not independent implementations of the entire official evaluator. Native execution uses `python -m gear_sonic.eval_agent_trl`; LUCID execution uses `eval_with_delay.py --max-delay 12 -- ...` with zero sampled delay. Different implementations can consume RNG differently even at the same seed; attribute differences cautiously and inspect traces/configuration before assigning a cause.

The path screen uses four motions × two paths × 128 evaluation aliases = 1,024 episodes, seed 8730. All original candidates remain: hands-on-back control, curved walking, sideways walking and stooping. They belong to the existing development split; no claim of being absent from foundation-model pretraining is made. This is one released controller, not 1,024 independent policies. The same broad frozen development qualification thresholds are retained for comparability, not promoted to a definition of high quality.

Source: `/home/linjiw/lucid-origin-path-screen`, commit `ee9d49b`.
Plan: `/home/linjiw/lucid-sonic/experiments/released_origin_path_screen_20260907_a/plan.json`.
Plan SHA-256: `7570c657d2dfbb94ee896a5a9f7986e90ff9448ff626bdc83a8f020723a739c6`.
[Online W&B campaign](https://wandb.ai/16726/lucid-sonic/runs/paths-7570c657d2dfbb94ee).
The adjacent `status.json`, per-cell logs and `supervisor.log` are the live execution record. The detached serial supervisor starts each cell when the existing 11,000-MiB free-memory gate permits and stops on validation or execution failure. Every cell has an explicit online run name, checkpoint/plan/source hashes, metrics and contract receipt.

Validation: 2,131 CPU tests passed before the final read-only metadata refinement; all six focused path/metadata tests passed afterward. Black and Ruff pass on all three added files. The focused metadata test checks first-capture-only behavior, unchanged reference tensors, and actual reference indices. The callback records resolved joint ordering, actuator types, observation terms, actor normalization contract and reference indices without extra observation or policy calls.

## Completed native sample check and preserved failures

The local released weights and config match the current official Hugging Face release:

- Weights: SHA-256 `e6bdab3f64a39336b3d41877d4f497d05f58af275f288ec0e6746c283ded8909`.
- Config: SHA-256 `f08187795fa16a839a28bc1c18e0555d38d9420e03733744341cdcb56ab629c7`.

The successful native sample run used the stock evaluation callback/configuration, G1 encoder, two distinct official sample references, two environments and seed 8740. It completed 2,002 steps and reported 100% completion, 117.3375 mm global MPJPE and 18.0033 mm local MPJPE. These stock aggregate metrics are not interchangeable with the first-episode qualification endpoint used in the project screen. This small smoke is a compatibility result, not a repertoire or robustness claim.

Receipt: `/home/linjiw/lucid-sonic/experiments/released_native_sample_20260907_c/status.json`; [W&B](https://wandb.ai/16726/lucid-sonic/runs/native-eb6dc04a30ca8847b9). Simulator wall time: 152.19 seconds, excluding preparation and previous attempts.

Two development failures remain preserved. Attempt `a` failed before evaluation because direct script launch shadowed the installed `trl` package with `gear_sonic/trl`. Attempt `b` completed the rollout but produced no metric file because the official entrypoint replaces the callback output path with `eval_output_dir`. The successful attempt uses module invocation and `++eval_output_dir=...`. Neither failure is a failed robot-control outcome. Their source worktrees and receipts remain intact, and their costs belong in development accounting.

## Information and duration diagnostics

Saved local and released default G1 configurations both supply reference joint position/velocity and reference-to-robot orientation to the G1 encoder. Proprioception supplies gravity, angular velocity, relative joint state and previous action. Horizontal reference displacement appears in the critic's privileged inputs, but no corresponding horizontal displacement term was found in this actor input contract.

A real-weight boundary experiment replayed 16 frozen local-origin actor histories, one per anchor phase bin. Adding one to every critic-only input value changed neither G1 encoder output nor action means: exact equality, maximum action difference zero. [Online diagnostic](https://wandb.ai/16726/lucid-sonic/runs/boundary-e35ff6d6b400b0a573). This verifies critic exclusion; **it is not a physical horizontal-displacement intervention**. The paired-state observability check is still required before declaring the return-to-path objective supported by the common controller.

The configured G1 reference sequence has ten frames at actual nominal offsets 0.0, 0.1, …, 0.9 seconds (50-Hz reference, five-index stride). The SMPL spacing is 0.02 seconds. “Ten future frames” therefore does not establish a common lookahead across modalities. The new runtime callback captures actual indices, including any current-frame/end-of-clip effects.

First-reference-segment analysis of the completed local-origin traces shows substantial early articulation error:

| Motion | Global / articulation, first 0.5 s (mm) | Global / articulation, 0.5–1 s (mm) |
| --- | ---: | ---: |
| Control | 31.8 / 18.9 | 74.2 / 30.3 |
| Curved walk | 85.0 / 61.3 | 204.5 / 87.6 |
| Sideways walk | 69.8 / 61.8 | 124.6 / 81.7 |
| Stoop | 111.6 / 78.6 | 249.6 / 91.3 |

Each listed window contains observations from all 128 aliases. Means are computed per episode and then across episodes. Later windows retain their observed denominators; they do not turn terminated or reset episodes into successes. The result argues against attributing all error to late accumulated drift. It does not isolate duration from motion identity/structure, establish physical infeasibility, or replace full-motion evaluation.

Evidence and scripts: `/home/linjiw/lucid-sonic/analysis/shared_origin_contract_20260907_a/` (`contract_and_prefixes.json`, `actor_boundary_plan.json`, `actor_boundary_result.json`, release manifests and input hashes).

## Ordered exit criteria

1. **Choose the common controller.** Released success in both paths favors reuse; native success with LUCID failure calls for integration repair; common failure calls for bounded motion/reference investigation and, if warranted, motion-balanced shared adaptation. No result is presumed before the full panel finishes.
2. **Establish observability and solved coverage.** Require at least two distinct longer solved motions before the first recovery study. Keep the original four-candidate denominator visible. Freeze task-relevant absolute criteria and independent validation episodes; include tails and sustained errors. If path-error observation must be added, give every method the same interface and separately evaluate this controller change.
3. **Extend R1 over the solved repertoire.** Balance teacher-buffer sampling by motion and normalized phase; cache raw actor inputs/teacher targets and normalization/encoder contracts. Compare fixed hard practice with and without the selected protection through the existing 2,000-iteration trajectory. Retain lower-LR control only where needed. Check nominal and original-envelope retention separately for every motion, then replicate continuation seeds and fresh origins.
4. **Calibrate event recovery.** Freeze motion/phase bands, dwell and horizon before grading continuations. Require an uninterrupted window, retain pre-event failures and unresolved/non-recovery outcomes, collect matched no-disturbance controls, and record actual nonzero events. Control subtraction is diagnostic and cannot replace absolute qualification.
5. **Test useful information.** Split whole episodes/source motions/origins before windows. Compare current errors, errors/derivatives/phase, a strong causal same-history predictor and the structured observer. Report calibration and useful lead time. Initially let the observer change confirmation-probe timing while candidate order and practice dose stay fixed; measured execution and retention still determine admission.
6. **Run F/S/G/L.** Protected fixed practice, protected frozen schedule, protected direct-feedback gate, and the same gate plus observer share controller, protection, candidate set and total resource accounting. Primary outcome: held-out recovery-qualified execution at a common total budget, subject to all per-motion retention constraints. Finite repeated looks/error control are frozen per fixed policy snapshot; changing snapshots are not pooled as a single Bernoulli experiment. Bounded candidate practice prevents admission deadlock.
7. **Scale only a supported effect.** Add independent origins, intact motion splits, new timing/direction/composition, final-policy independent-simulator checks and then measured hardware trials. Earlier proposed 24/8/16 motion counts and 960 hardware episodes are possible study scopes, not immediate prerequisites.

Total resource reporting includes simulator transitions, anchor collection/presentations/forwards, probes, observer training, evaluation overhead and failed development attempts. Actual exposure may differ between scheduling arms; the intervention is the allocation, while total cost and allowed conditions are shared.

## Sources checked

- [Official model card](https://github.com/NVlabs/GR00T-WholeBodyControl/blob/main/docs/source/model_card.md): released variants and compatibility context.
- [Official training guide](https://nvlabs.github.io/GR00T-WholeBodyControl/user_guide/training.html): checkpoint continuation and motion-path configuration.
- [Official observation configuration](https://nvlabs.github.io/GR00T-WholeBodyControl/references/observation_config.html): modality-specific temporal specification; actual local runtime remains decisive.

## Next bounded measurement: paired-state horizontal observability

Use a dedicated diagnostic after the controller-path panel, with the selected released weights if their capability passes. At declared motion phases, compare otherwise identical state snapshots under horizontal robot translations of ±0.25 m along each world axis, keeping reference/world alignment, root orientation and velocity, joint state, reference clock, previous commands and prior observation history fixed. These are counterfactual information tests, not push-recovery trials.

Validate the intervention through independently read robot/root/body positions and reference-relative translation. Compare the freshly evaluated raw actor observation terms, assembled actor inputs, active G1 encoder output and action means. The critic's reference-relative position term supplies a positive measurement control; a separate orientation intervention checks that the selected actor-input comparison can detect a relevant change. Match observation-noise RNG across comparisons and report tolerances before execution.

Do not use `observation_manager.compute(update_history=False)` alone as the proof: for history-enabled terms Isaac Lab returns the existing circular buffer, which can hide a real change in freshly computed raw observations. Reconstruct the counterfactual current frame while preserving prior history, or compare the fresh terms explicitly and verify their placement in the actor's history. Do not advance physics, change reference phase, or let a reset/teleport masquerade as recovery. Record exact controller/source contracts and all tested states.

If horizontal translation changes the required corrective target but not actor information, retain the stronger path-recovery scientific goal and explicitly evaluate a common observation/interface remedy before comparing curricula. A training-only observer does not repair missing information in the deployed actor. This diagnostic remains pending; critic-only invariance is not its replacement.
