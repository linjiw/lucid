# Recovery event capture: implementation and next measurement gate

**Latest analysis, September 7, 01:06 UTC:** R1 remains the selected protected baseline from the completed 83-cell development screen. The four-cell contact diagnostic is complete. The separately preregistered eight-cell execution/retention parity campaign now passes all four pairs, covering 1,024 evaluation aliases and 380 aligned nonzero push events. Contact diagnostics remain unvalidated and the original all-metric gate remains failed. Recovery-band calibration and feedback efficacy are next. See the [research-direction update](lucid-research-direction-update-2026-09-07.md).

The implementation and runtime snapshots below are retained as historical evidence.


**Latest integration:** the [native adapter and evaluation audit](lucid-native-recovery-capture-status-2026-09-06.md) are implemented at `56dc1bc`, with 2,094 passing CPU tests. Live IsaacLab parity remains pending; the eight-cell simulator matrix now has an [online supervisor](https://wandb.ai/16726/lucid-sonic/runs/rec-3ae0529d4649aaef377c) and waits for the frozen GPU-capacity gate. The component-level evidence below is retained as its original implementation record.


September 6, 2026. Advances G1 of the [ideal-paper execution plan](lucid-ideal-paper-execution-plan-2026-09-06.md). This is CPU-validated measurement infrastructure, not a live recovery observer or a policy improvement.

Implementation is isolated in `/home/linjiw/lucid-recovery-event-capture`, commit `be23e92`. It contains the existing recovery components/scorer (cherry-picked as `0907e87`) on top of the running campaign's repaired training source. The running `/home/linjiw/lucid-anchor-start-repair` is untouched.

## What the new seam does

`gear_sonic/research/practice_utility/push_event_capture.py` wraps one existing native push callable. Disabled mode returns that same callable object. Enabled mode obtains cloned, detached pre/post event snapshots, calls the native function exactly once, preserves its result, and emits a record. It samples no perturbation and introduces no recovery decision.

Each affected environment is bound to recording ID, episode ID, motion ID, reference phase, control step, timestamp and a per-episode event ordinal. The record retains configured velocity ranges, actual before/after six-dimensional world velocity, their difference, and provided tracking components. Linear/angular units are m/s and rad/s. This is not a measured force impulse. Post-write samples precede the next physics response and cannot be interpreted as recovered motion.

Copying the pre-event tensors prevents a native in-place update from corrupting the evidence. Missing headings remain JSON null with their validity flags. Duplicate/wrong environment ordering, invalid clocks/shapes/ranges and identity changes inside the native call fail validation. Native failures and sink errors propagate without retrying an already applied push. Such attempts remain failed measurement attempts in the outer experiment receipt; they do not become recovery labels.

The snapshot callback must supply verified event-time data and be read-only/RNG-free. The recorder checks internal identity correspondence, but cannot prove that a caller chose the right simulator fields or timestamps. Its current tests use synthetic callbacks. It is not yet registered with IsaacLab's event manager and does not yet collect the post-event trajectory.

## Validation and provenance

- 15 new CPU contract tests cover disabled identity, exact RNG progression, native return, affected-environment order, pre-event alias protection, missing-component serialization, repeated pushes/resets, invalid identities, native exceptions and sink failures.
- Full CPU suite: **2,076 passed**, 5 warnings, 40.97 seconds.
- Black and Ruff pass for both additions.
- CPU log: `/home/linjiw/lucid-sonic/outputs/recovery_event_capture_cpu_20260906_a.log`.
- Source/test/log hashes and scope: `/home/linjiw/lucid-sonic/analysis/recovery_event_capture_20260906_a/receipt.json`.
- [W&B CPU validation](https://wandb.ai/16726/lucid-sonic/runs/rec-event-cpu-20260906-a), explicitly tagged CPU-only and not-efficacy.

## Next simulator experiment card — design, not a launched plan

**Question:** does event/trajectory logging preserve the frozen origin's execution and correctly align perturbation, reset, reference and terminal state?

**Changed variable:** recorder off/on. Same frozen origin, raw actor input/action path, reference motion, RNG seeds, dynamics, actuator delay and simulator settings. No learning and no adaptive allocation. The existing origin and development motion are appropriate for instrument validation; this is not a new motion-generalization test.

**Proposed small matrix:** two conditions (nominal and the original envelope), two dedicated development seeds, two recorder modes, 128 environments each: eight cells / 1,024 episode aliases. Freeze actual seeds, clip/file hashes and commands only after the snapshot/trajectory adapter is implemented and CPU-tested. Include the identical native push process in both modes; a zero velocity-range event is separately labeled and cannot demonstrate perturbation recovery. This is not the final observer dataset or a power calculation.

**Adapter requirements before freezing:** obtain episode identity from an explicit reset seam, not inference from a later done flag; read phase/reference/executed body frames at the interval callback after resets and command update; verify post-write root velocity reflects the native write; sample subsequent physical poses before reset overwrites them; retain original termination and timeout masks before downstream callbacks alter them. Log issued commands and delivered actuator commands separately if collecting prediction inputs. Bind simulator/module/config hashes and timestamp semantics.

**Pass conditions:** recorder modes produce exact matching actions, RNG progression, commanded references, event draws, termination identities and frozen-policy metrics under the established deterministic paired-run contract. Every recorded event matches the instrumented seam; each trajectory sample has unique episode/time identity; no post-reset frame is labeled as recovery of the previous episode. Verify full reference/body/quaternion correspondence and signed heading with controlled known transforms. Declare unresolved precision or timing mismatches rather than widening tolerances after outcomes. Measure additional wall time and per-process memory; no throughput claim follows from CPU tests.

**After passing:** dedicated origin rollouts calibrate phase coverage and task bands; freeze bands, dwell, horizon and overlap policy before collecting/scoring learning outcomes. The current isolated-event scorer must not label double-push recovery without a separate pair-level endpoint. Then create causal prediction datasets with split assignment before windowing and full-episode/motion/origin separation, following G2. Compare direct error/derivative/history features before committing to a learned encoder.

All actual simulator cells must have online W&B, immutable commands/source hashes and explicit names such as `recovery-noop/<condition>/s<seed>/<off|on>`. The current 83-cell retention campaign has priority. No additional GPU job or physical robot experiment was launched for this CPU preparation.
