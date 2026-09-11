# Bounded development pilot request — September 11

Proposed, not authorized or launched. Use only the existing local RTX 5080, at most **4 cumulative GPU process-hours and 8 elapsed campaign hours**, including simulator startup, failed attempts, validation and teacher computation. No spending, hardware, publication or submission. Stop at either cap; unused time does not authorize more seeds or tuning. Record actual time after each process. Recheck available memory before launch; the existing 11,000 MiB free-memory gate currently is not met (9,208 MiB at inspection). Never stop unrelated GPU processes.

1. Measurement: at most four simulator invocations and 60 GPU-minutes, including the prepared nominal capture, a terminal boundary audit, and a scheduled nonzero event with pre-write, readback and post-physics velocities. Preserve every attempt. Use long enough clips for the scored event, unlike the short nominal instrumentation clip. Stop if raw truth cannot be independently bound to joint order, reference time, fixed world registration and actual delivery. No scorer success from an asserted delivery Boolean alone.
2. Competence and development freeze: at most twelve evaluation invocations and 60 GPU-minutes on existing checkpoints; no new origin training. Select one shared origin competent on at least three distinct sufficiently long development recordings. Freeze task-justified component bands, pre-event window, dwell, horizon, failures, nominal/envelope budgets and all scheduled IDs before adapting policies. If no origin qualifies, report infeasible at this budget and stop. No weakening bands to make the origin pass.
3. Feedback pilot, conditional on both gates: remaining time up to 120 GPU-minutes; three continuation runs, one seed each, at most 256 optimizer iterations and 128 environments per arm. Z/O/N share origin, trainable correction capacity, fixed DR, constant action anchoring, exposure, optimizer and evaluation schedule. N is explicitly corrupted oracle, not estimated localization. Require same-input initial action parity and no privileged leakage. Allow at most 72 evaluation invocations, at most 32 rollout copies per condition. Freeze exact development conditions, corruption settings and one terminal-checkpoint comparison before launching training. No best-checkpoint search or replacement seeds. If interrupted arms cannot reach matched exposure within the cap, report inconclusive.

The caps are maximum permission requested, not promised throughput or an already frozen scientific protocol. This is a development pilot, not confirmation; no held-out confirmation data are used. Log every simulator run online to `16726/lucid-sonic`, in a dated campaign group with stage/arm/seed/iteration/condition and verified run URLs. Missing online logging stops further launches until resolved within the same caps. Log all attempted runs, hashes, teacher/anchor forwards, transitions and time; do not upload datasets/checkpoints or credentials.

The first concrete prepared plan is:
`/home/linjiw/lucid-sonic/experiments/task_truth_collection_d1_20260911_a/collection_plan.json`

SHA256: `a868fd6cec33da94bda1265dd714902933094f982a09e2c84c97d649b0341da7`.
All 19 input/source bindings were rehashed successfully. This command is for execution **after budget authorization and the free-memory gate**, with a 15-minute per-process cap inside the total cap:

```bash
source /home/linjiw/lucid/env/lucid_env.sh
timeout --signal=TERM --kill-after=30s 15m python scripts/practice_utility/collect_native_task_truth.py \
  --source-plan /home/linjiw/lucid-sonic/experiments/recovery_execution_v2_20260907_a/plan.json \
  --cell phys_000_s8720_on \
  --output /home/linjiw/lucid-sonic/experiments/task_truth_collection_d1_20260911_a \
  --execute-plan-sha256 a868fd6cec33da94bda1265dd714902933094f982a09e2c84c97d649b0341da7
```

A timeout is an attempted run, never a reason to overwrite the output. The inherited collection callback currently uses the September 10 instrumentation group; record that explicitly for this prepared plan. Subsequent scientific plans must use the actual campaign date. This first capture is an instrumentation check on a historical origin, not the choice of a competent multi-motion origin or a calibrated recovery trial.

Decisions: no oracle gain triggers bounded diagnosis of measurement, timing, feasibility, control/reward and actuation; only oracle gain identifies a sensing/latency question; usable-feedback gain permits consideration of the retention method in a separately sized next campaign. No curriculum, estimator, residual allocator or constrained optimizer is authorized by this pilot.
