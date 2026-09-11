# LUCID recovery measurement: offline validation and live integration contract

**Latest integration:** the [native adapter and evaluation audit](lucid-native-recovery-capture-status-2026-09-06.md) are implemented at `56dc1bc`, with 2,094 passing CPU tests. Live IsaacLab parity remains pending; the eight-cell simulator matrix now has an [online supervisor](https://wandb.ai/16726/lucid-sonic/runs/rec-3ae0529d4649aaef377c) and waits for the frozen GPU-capacity gate. The component-level evidence below is retained as its original implementation record.


September 6, 2026. The main claim-bearing priority remains the [retention-repair screen](lucid-retention-screen-execution-2026-09-06.md). This work prepares the measurements needed to distinguish temporary recovery deviations from persistent tracking damage. It does not alter the frozen training/evaluation campaign or claim that any learned policy recovers better.

Implementation is committed as `e145106` in `/home/linjiw/lucid-recovery-measurement`, branch `research/recovery-measurement`. The worktree is clean. Only research modules, a research validation script, and matching tests were added.

## What is implemented

[Tracking components](/home/linjiw/lucid-recovery-measurement/gear_sonic/research/practice_utility/recovery_components.py) measure world-frame pelvis translation, signed and absolute wrapped heading, translation-only root-relative MPJPE, heading-aligned articulation MPJPE, and the existing global MPJPE. Position errors are millimetres; headings are radians. Inputs use metres, Z-up coordinates, and unit wxyz quaternions. Body correspondence and the pelvis index are explicit; the command adapter looks up pelvis by name.

Translation-only local error subtracts each pelvis position but retains heading differences. Articulation additionally rotates each root-relative pose by its own inverse heading, preserving roll/pitch and limb errors. Body averages include pelvis, matching the existing global/local averaging convention. These norms are complementary diagnostics, not an additive decomposition of global error. A nearly vertical root-forward axis has undefined heading: it produces a false validity mask and missing heading/articulation, never zero error.

[Offline recovery scoring](/home/linjiw/lucid-recovery-measurement/gear_sonic/research/practice_utility/event_recovery.py) accepts one episode's timestamped component samples, actual event identities, an optional terminal boundary, and required immutable phase-dependent bands. It has no default robot tolerances and does not calibrate bands from scored policies.

The sample at the event boundary is pre-event; only later samples can start a return. A dwell of D control steps requires D+1 consecutive in-band observations, spanning D times the sample interval. The scorer records both return onset and confirmation time. All designated components must be inside their current reference-phase bands simultaneously. Horizon residual error is reported separately, so a later drift remains visible after an earlier confirmed return.

This initial isolated-event implementation uses an explicit conservative policy: another event at or before the horizon censors the earlier event, even if it returned before the second event. A terminal boundary at or before the horizon is a failure, even after an earlier return; samples at/after termination are excluded. Missing samples, undefined components, and truncated observation windows remain unresolved. Every event remains in the summary denominator. The summary separates confirmed recovery, known non-recovery, and unresolved fractions and shows the corresponding algebraic best/worst bounds. These are not statistical confidence intervals. Recovery-time medians are conditional on recovered events and cannot replace the fractions.

Pre-event tracking state is retained and flagged separately. An event with poor pre-event tracking is not silently removed; returning to a band from such a state is not by itself evidence of recovery from damage caused by that push. Repeated events are clustered within episodes; the implemented descriptive event fractions do not supply independent-origin inference. A temporal pair-transfer study will need its own predeclared pair-level endpoint rather than treating overlapping events as isolated successes.

## Source audit that changes the integration contract

The pinned wrapper maps `ref_body_pos_extend` to executed robot positions and `rigid_body_pos_extend` to reference positions. Existing global and translation-only local distance norms are symmetric under this reversal, which the regression test verifies. The new adapter reads `motion_command.body_pos_w/body_quat_w` as reference and `robot_body_pos_w/robot_body_quat_w` as executed, avoiding reversed signed heading. No historical metric or running code was changed. The origin uses 14 tracked bodies with pelvis at index zero.

The installed IsaacLab Push function actually adds a sampled six-dimensional velocity increment to current root velocity and writes it to simulation, despite documentation describing setting a random velocity. The event magnitude label alone is not a calibrated impulse in N·s. Live logging must retain the actual pre/post world linear and angular velocities, their difference, configured severity, environment/episode/event identities, reference phase and timestamp.

Interval events execute after physics, termination checks, resets and command update, and before observation computation. Therefore an ordinary whole-step pre-snapshot is not automatically the pose/phase immediately before the push. The future recorder must capture at the interval-event seam, account for resets already performed, and align the next physics response. Reusing only nominal interval timestamps or post-reset poses would invalidate event-level interpretation.

These findings are bound to the exact local source and origin config in the [source audit receipt](/home/linjiw/lucid-sonic/analysis/recovery_measurement_source_audit_20260906_a/audit.json). They establish code semantics; instantiated event timing and no-op parity still need simulator validation.

## Validation evidence

The analytical tests cover identity, pure translation, pure root yaw, a single hinge rotation, a single-body perturbation, root roll, angle wrapping, quaternion-sign equivalence, common world-frame transforms, reordered body names, batch-specific undefined heading, and compatibility with the existing global/local metrics. Recovery tests cover dwell and exact horizon boundaries, transient crossings, later drift, terminations before/at/after the horizon, reset exclusion, overlaps, missing samples, phase-varying bands, simultaneous component constraints, immutable bands and all-event denominators.

- **39 focused tests passed.**
- **2,035 full CPU tests passed**, five warnings, 43.44 s. [Full log](/home/linjiw/lucid-sonic/outputs/recovery_measurement_cpu_20260906_a.log).
- Black/Ruff pass on all five additions, and staged whitespace checks pass. Repository-wide `make run-checks` retains existing isort failures beginning in `motionbricks/`; root isort/Ruff ordering remains inconsistent. [Check log](/home/linjiw/lucid-sonic/outputs/recovery_measurement_run_checks_20260906_a.log).
- The final synthetic artifact is bound to committed source and has a checked output receipt: [validation JSON](/home/linjiw/lucid-sonic/analysis/recovery_measurement_synthetic_20260906_b/validation.json), [receipt](/home/linjiw/lucid-sonic/analysis/recovery_measurement_synthetic_20260906_b/receipt.json), [PNG figure](/home/linjiw/lucid-sonic/analysis/recovery_measurement_synthetic_20260906_b/synthetic_validation.png), [PDF figure](/home/linjiw/lucid-sonic/analysis/recovery_measurement_synthetic_20260906_b/synthetic_validation.pdf). The earlier `_a` artifact was a pre-commit development rendering and is not the final receipt.

The figure uses an illustrative 10-mm root band, 0.2-s dwell and 1-s horizon only to verify the scorer. None is a chosen humanoid recovery threshold. In the example, the sustained return begins at 0.4 s and confirms at 0.6 s; a brief crossing fails; an earlier sustained return followed by drift remains visible through a 30-mm horizon residual. These are synthetic constructions, not policy outcomes.

Reproduce in the pinned environment with a new output directory:

```bash
export LUCID_REPO=/home/linjiw/lucid-recovery-measurement
source /home/linjiw/lucid/env/lucid_env.sh
python -m pytest tests/practice_utility/
python scripts/practice_utility/validate_recovery_measurement.py \
  --output /home/linjiw/lucid-sonic/analysis/recovery_measurement_reproduction
```

## Execution status and next gate

At 05:57 UTC, the fresh-history arm and its evaluations were complete; restored history was at 695/2,000 with no supervisor warnings. Collection and retention-screen workers remained waiting on their verified prerequisites. No partial-history recipe was selected, no extra GPU job was launched, and no frozen campaign source was edited. [History status](/home/linjiw/lucid-sonic/experiments/optimizer_history_campaign_20260905/status.json), [repair status](/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_a/status.json).

After a viable quality-preserving repair, the next measurement gate is a separately frozen simulator no-op comparison with event logging, verified body/quaternion correspondence and event/termination alignment. Then use dedicated development origin rollouts to calibrate phase coverage and bands, and freeze bands, dwell, horizon, event eligibility and temporal-overlap policy before policy grading. No current recovery-qualified endpoint, adaptive allocation or hardware result is claimed or launched.

## Later September 6 update

The full retention smoke has now passed and campaign `_c` is running the long screen. The [ideal-paper plan](lucid-ideal-paper-execution-plan-2026-09-06.md) defines the incremental recovery-feedback claim and its stronger baselines. [Event-call capture is now CPU-implemented](lucid-recovery-event-capture-status-2026-09-06.md) in a separate worktree (`be23e92`, 2,076 passing full-suite tests). It preserves one native push call and captures cloned event-time snapshots with identity checks. The native simulator snapshot/trajectory adapter, live no-op parity, phase-band calibration and policy recovery evidence remain outstanding; the earlier integration gate is not claimed complete.
