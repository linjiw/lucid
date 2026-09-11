# Native recovery capture: G1 integration status

**Latest analysis, September 7, 01:06 UTC:** R1 remains the selected protected baseline from the completed 83-cell development screen. The four-cell contact diagnostic is complete. The separately preregistered eight-cell execution/retention parity campaign now passes all four pairs, covering 1,024 evaluation aliases and 380 aligned nonzero push events. Contact diagnostics remain unvalidated and the original all-metric gate remains failed. Recovery-band calibration and feedback efficacy are next. See the [research-direction update](lucid-research-direction-update-2026-09-07.md).

The implementation and runtime snapshots below are retained as historical evidence.


September 6, 2026. Companion to the [ideal-paper execution plan](lucid-ideal-paper-execution-plan-2026-09-06.md) and [generic event capture contract](lucid-recovery-event-capture-status-2026-09-06.md).

The native adapter and evaluation callback are implemented in `/home/linjiw/lucid-recovery-event-capture`, latest commit `56dc1bc`. This is measurement infrastructure. Live IsaacLab parity, calibrated recovery labels, observer prediction value, and curriculum benefit remain unverified.

## Implemented measurement path

`NativeRecoveryRecorder` wraps the existing native environment step, reset, motion resampling, command update and interval push on one environment instance. Each native function is called once. It adds no RecorderManager term: the pinned IsaacLab implementation would otherwise insert an additional observation computation when recorder terms are active.

Samples use explicit native reference and executed body positions/quaternions, with pelvis translation, wrapped heading, root-relative MPJPE and heading-aligned articulation measured separately. Samples after physics and command update precede the interval push. Push records retain pre/post world root velocities and configured velocity ranges. These reads use the robot data mirror; live read-back still needs validation. They are velocity increments, not force or impulse measurements.

Physical resets and reference resampling have separate generations. This distinction matters because SONIC's `_resample_command` writes joint and root state even when normal termination has not occurred. A tracking segment ends at either boundary. Terminal poses are captured before reset overwrites them, with original termination/timeout masks, and explicitly marked diagnostic-only. A reset or reference teleport cannot establish recovery of the preceding event. Untracked backward phase changes or motion identity changes fail measurement.

`RecoveryMeasurementEvalCallback` is an opt-in subclass of the existing qualified evaluator. It attaches after the evaluation setup/reset and restores native methods and the original push configuration at completion or an environment-step failure. Traces are exclusive, single-use files; attempts do not overwrite or resume earlier recordings.

Both recorder modes use the same native-step audit. SHA-256 digests cover native action-manager inputs, returned observations/rewards/termination/timeouts, explicit reference/executed poses, motion cursors, root velocity and Python/NumPy/Torch RNG state. Existing CUDA generators are read without initializing CUDA in CPU tests. The audit returns the original native results and adds no policy forward pass. Native action-manager inputs are not claimed to be delivered motor commands, and this is not yet a predictor-training dataset.

Existing evaluation metrics are returned unchanged. Separate files contain `native_audit.jsonl`, optional `recovery_trace.jsonl`, and a successful `measurement_receipt.json` with content hashes, counts and wall time. Failed attempts require an outer failed-run receipt; partial traces cannot serve as successful measurements.

## Validation

The CPU suite checks exact native outputs and RNG progression with recording off/on, matched audit-file bytes, no extra observation calls, native function call counts, event-time phase, pre/post push velocity, reset versus reference-only boundaries, original termination flags, hook restoration, refused overwrite, failed sinks and untracked reference changes. These use a synthetic environment matching the audited call order; they do not establish live physics parity.

Initial integrated validation at commit `604058b`: **2,093 tests passed**, 4 warnings, 39.15 seconds, including 17 new contracts. [W&B validation](https://wandb.ai/16726/lucid-sonic/runs/rec-native-cpu-20260906-a) is finished. The receipt is `/home/linjiw/lucid-sonic/analysis/recovery_native_adapter_20260906_a/receipt.json`.

The final motion-identity guard also passed the full suite: **2,094 tests**, 4 warnings, 38.63 seconds, including 18 new contracts, at commit `56dc1bc`. [Final W&B validation](https://wandb.ai/16726/lucid-sonic/runs/rec-native-cpu-20260906-b); receipt `/home/linjiw/lucid-sonic/analysis/recovery_native_adapter_20260906_b/receipt.json`. Black and Ruff pass on all four additions. Earlier receipts are retained.

## Next experiment gate

Run the already specified eight-cell recorder-off/on instrument matrix: nominal and original-envelope physics, two dedicated development seeds, and 128 aliases per cell. Freeze the seeds, input/source/module hashes and commands before launching. Compare exact audits and existing evaluation outcomes; retain any mismatch as a failed instrument gate. Quantify logging overhead. A zero-increment event does not demonstrate disturbance recovery.

The callback target is `gear_sonic.research.practice_utility.recovery_measurement_callback.RecoveryMeasurementEvalCallback`. In addition to the existing threshold arguments, its explicit options are `recovery_output_dir`, `recovery_recording_id`, and `recovery_recording_enabled`. Both modes need separate output directories and the identical parent evaluation configuration. Every simulator cell requires an online W&B run with condition, seed and mode in its name, grouped under the frozen measurement campaign.

**The eight-cell matrix is now supervised**, with seeds 8710/8711, nominal/original-envelope physics and recording off/on. It starts when at least 11,000 MiB is free; other jobs currently occupy the shared GPU. [Online W&B campaign](https://wandb.ai/16726/lucid-sonic/runs/rec-3ae0529d4649aaef377c). Frozen plan: `/home/linjiw/lucid-sonic/experiments/recovery_noop_20260907_a/plan.json`, SHA-256 `3ae0529d4649aaef377c2630c041d6ef49750d7266129e24b56a7539a20f7702`; supervisor PID 2572263. The launcher and eleven new contract tests are committed at `0c81b00`; the full CPU suite passes 2,105 tests (4 warnings, 39.03 seconds). The driver stops on an invalid cell or exact parity mismatch and preserves failed attempts. The completed 83-cell retention campaign selected R1; see the [completed retention results](lucid-retention-repair-results-2026-09-06.md). Its source and endpoints were preserved. Once the measurement gate passes, collect development calibration rollouts and freeze bands, dwell and horizon before scoring learned policies. Learned observers and allocation remain gated by the paper plan.

Historical operational snapshot at September 6, 17:59 UTC: R0 1,729/2,000 iterations, five origin evaluation cells complete, no supervisor warnings. The campaign remains online at https://wandb.ai/16726/lucid-sonic/runs/ret-46911b8054776113fe91. All 1,039 campaign-bound source files were rehashed unchanged during this implementation.

Live update, September 7 00:26 UTC: `phys_000_s8710_off` completed at exit 0 with 128 scored aliases and 200 native steps. `phys_000_s8710_on` is capacity-gated. No off/on pair has passed yet. The first cell took 50.01 seconds end-to-end after capacity admission; 27.04 seconds were recorded inside capture. Full audit and metrics hashes are in the campaign status receipt.
