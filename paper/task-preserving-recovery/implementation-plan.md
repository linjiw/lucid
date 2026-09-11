# Implementation dependencies: fix, test, then defer

**This is a dependency plan, not a launch script.** The present pass adds a read-only evidence auditor and local research documents. It does not implement or enable a new policy, estimator, allocator, curriculum or constrained optimizer. Research code belongs under `GR00T-WholeBodyControl/gear_sonic/research/practice_utility/`, drivers under `scripts/practice_utility/`, and tests under `tests/practice_utility/`. Preserve upstream behavior through opt-in seams. Generated data and launch receipts remain outside Git.

## Existing code checked

| Existing location | What was checked | Reuse boundary / necessary change |
|---|---|---|
| `/home/linjiw/lucid-anchor-start-repair/.../reference_anchor_trainer.py` | `_compute_loss` calls upstream PPO then adds constant β times anchor loss. Beta-zero no-op; single-process, fresh-branch restriction | Reuse as the fixed-anchor baseline. Resume is explicitly unsupported; do not promise resumable constrained training by inheriting this class. No protected cost gradient or dual update exists here. |
| Same worktree, `reference_anchor.py:143–187` | Fixed buffer, isolated sampling RNG, deterministic student means, per-action scaling, summed squared errors divided by batch size; forward batch limit preserves numerical behavior | Preserve exact normalization when comparing β. Cache validity and physical forward shape matter. Anchoring does not penalize changed future states or variance. |
| Same worktree, `qualified_pose.py` | Pre-step first-episode mask, global and root-relative local body errors, completion-gated qualification | Retain historical metrics. Add separate root/heading/joint errors and fixed-horizon failure-aware outcomes; never silently change historical schema. |
| Same worktree, `retention_screen.py` | Empirical sampled-checkpoint ratios and completion margins | This is analysis/selection, not a constrained optimizer. Its paired standard errors require actual pairing evidence; identity aliases alone are insufficient. |
| `/home/linjiw/lucid-path-repair-run/.../path_input.py` and `path_input_isaac.py` | Two-coordinate path error from `command.anchor_pos_w`, `robot_anchor_pos_w` and true robot quaternion; 0.3 m scale; corruption disabled | A synchronized oracle seam. Add a named source interface before calling it estimated/deployable feedback. Preserve original actor input bytes in the parity control. |
| Same worktree, `path_practice_callback.py` | Fixed 256-env/four-motion allocation and 0.5 m/s velocity write; logs before, write argument after, IDs and reference steps | This is campaign-specific, not a general calibrated force interface. Verify post-write readback/event timing and isolate pulses; do not turn logged requested values into measured physical forces. |
| `/home/linjiw/lucid-path-pilot-eval/.../native_recovery_recorder.py` | Instance hooks label physical resets/reference resampling, reject duplicate/rewound reference samples; terminal samples separately labeled | Useful recorder seam. Add immutable original-reference identity, estimator packets and actuator data. Never join segments across reset to create a successful dwell. |
| Main repo `tools/mujoco_player.py:549–598` | `fell` flag is path departure; `outcome` uses terminal pelvis height; full-clip flag preserves time after departure | Add explicit event-based physical failure and common task scorer before recovery claims. Keep old fields/schema interpretable. |
| Main SONIC deployment `.../include/robot_parameters.hpp` and observation registry | Heading-offset state and named heading-difference observation exist | Playback/heading machinery is not absent. Freeze evaluation alignment and forbid operator/reference changes during a trial. Position estimator/runner execution/parity remain unverified here. |

Paths containing `...` abbreviate `gear_sonic/research/practice_utility/` except the explicitly named deployment path. These sources live in different worktrees. A fresh checkout of the main SONIC branch does not automatically contain them. Integrate only the chosen minimal dependency chain, preserve source SHAs and rerun contracts; do not merge all experimental worktrees indiscriminately.

## Dependency order and acceptance tests

### D0. Source and evidence inventory — first

Create a source manifest distinguishing tracked commit, dirty diff and extra files for the selected implementation. Tie origin checkpoints, normalization, action std, robot model and configs together. Follow actual plan output paths on resumed/reused campaigns. Keep a machine-readable verified/reported/proposed split and record parent experiment IDs.

The new `tools/audit_task_preserving_evidence.py` reaggregates existing episode records and verifies metric/plan bindings. Run output is private; it is an analysis artifact, not a new research evaluation run. Its 135-panel/69,120-record audit is described in the ledger. Extend only if a material claim requires additional raw evidence.

Simpler alternative: use one known source worktree without migration. Reject this dependency’s success if imports resolve to a different checkout, dirty source cannot be reconstructed, or model/config hashes disagree.

### D1. Immutable task and measurement schema — before any new evaluation

Proposed modules: `task_reference_contract.py`, `task_recovery_metrics.py` and matching tests. Pure CPU scoring takes timestamped reference/truth errors, application stamps and terminal events; it never invents pose from MPJPE. Protocol fields require explicit calibrated values—no default “passing” tolerance.

Test:

- Rejection without band departure counts as success; departure plus contiguous dwell counts as regain.
- A single boundary excursion breaks dwell; exact inclusive threshold and last admissible entry are handled consistently.
- Post-dwell physical failure, reset, recentering, intervention and reference-clock restart invalidate trial success.
- Missing timestamps/ground truth cannot produce dwell; duplicate/out-of-order ticks are rejected; terminal-pre-reset poses are never interpreted as next-episode recovery.
- Pre-push failure remains in the scheduled denominator; undelivered disturbance is an instrument error, not rejection; legitimate zero-push controls retain a separate label.
- Fixed-horizon failure padding cannot improve by terminating earlier with otherwise equal costs; conditional time cannot replace capped all-trial time.
- Root-only translation, heading-only rotation, joint-only change and joint robot/reference transforms affect exactly the intended error components.

Simpler alternative: a tested offline scorer over an existing recorder. Do not build a new live evaluator if that suffices. No simulator launch needed for these synthetic contract tests; synthetic cases are unit tests, not robot results.

### D2. Common oracle/estimated input and export parity

Proposed interface: `LocalizationPacket` with capture/arrival times, frame ID, pose, validity and optional characterized covariance; `TaskFeedbackProvider` supplies timestamp-aligned feedback. O uses simulator truth explicitly; N applies declared corruption; E processes causal packets through an actual implemented estimator. The actor cannot choose a hidden oracle fallback.

Test delayed packet arrival, noncausal future samples, dropout, outlier/relocalization, frame transforms and reference synchronization. Test that neutral added input and zero adapter give origin mean/actions/distribution on identical observations after the native std convention is canonicalized. Verify frozen buffers/normalization and old parameter bytes. Test finite gradients and checkpoint round trip; nominal trajectories alone are insufficient to validate numerical parity.

A simple timestamped pose feed can replace a filter. A two-column decoder extension can replace an action residual. An estimator is unnecessary if reliable direct pose already meets the fault contract, but that direct measurement still needs validation. A scalar “uncertainty” head is deferred.

### D3. Event application and long-horizon evaluator

Extend the native recorder through opt-in seams. Freeze event times independent of policy, sufficient recording duration, readback after application, force/velocity units, actual lag buffer and actuator limits. Keep task-band departure distinct from physical failure. Use a consistent single-event scoring interval, without automatic reference reset. Emit original/ref-conditioned trajectories separately if a controller modifies its input reference.

Meaningful tests: zero-write identity; known velocity increment recovered from before/readback states; known force/time integration units; event never applied to protected cohort; no hidden push outside the manifest; repeated event IDs rejected; clipping/latency capacity mismatches fail before launch. CPU tests precede a separately approved bounded live parity check.

Simpler alternative: fixed pulses and deterministic physics draws; no event scheduler learner. If recurrent motion loops are required only because clips are too short, choose longer feasible recordings instead.

### D4. Fixed-DR matched feedback pilot — first training gate

Use the existing origin/anchor scaffolding with common interfaces. Record all data and computations online via native callback, or attach the approved read-only monitor to frozen campaigns. Verify the actual online run URL. The earlier A/B logging gap stays unverified until independently resolved; `WANDB_MODE=online` is not sufficient.

Z/O/E use identical constant anchor, fixed motion mixture, matching origin and trainable scope. No learned curriculum. New numeric thresholds and budgets require a frozen protocol and resource decision. Stop if the realistic-feedback gate fails.

Simpler alternative: supported classical outer loop with the same sensing and fixed evaluator reference. Do not build constrained training if ordinary feedback does not solve the basic information problem.

### D5. Protected-rollout optimization — only after D4

Proposed modules: `protected_rollout_costs.py`, `cost_value_heads.py`, `retention_constrained_trainer.py`. Preserve the native trainer as a disabled-path baseline. Implement the specific minimization objective and fixed physical cost scaling from the formulation; do not use historical checkpoint-gate Booleans as dense training costs.

Tests before integration:

- Exact enumerated finite-horizon MDP: likelihood-ratio cost gradient matches finite differences.
- Positive cost violation increases multiplier; feasible negative violation decreases it to a nonnegative floor.
- Cost-clipped PPO uses the minimizing sign; no detached cost tensor pretends to provide actor gradients.
- Unequal cohort sampling reproduces the same declared conditional objective with correct weighting; fixed horizon normalization is applied once.
- Absorbing physical failure includes remaining scheduled costs; true termination and a rollout chunk boundary bootstrap differently.
- Teacher targets and origin parameters stay fixed; action std/normalization identity is explicit.
- Beta zero and multipliers zero recover the chosen base optimizer path; disabling all seams preserves upstream behavior.
- Save/resume includes actor/critics, optimizer moments, multipliers, RNGs, packet/history states, cohort/event schedule, normalizers, cost statistics and log cursors. Refuse unsupported resume rather than silently starting a different optimizer.
- Per-update accounting includes anchor and fresh protected dual-batch work. A multiplier cap/oscillation is logged as a diagnostic, never treated as a satisfied constraint.

Compare fixed anchoring and fixed rollout penalties with equal tuning budgets before keeping adaptive multipliers. A primal–dual update is not a new CPO implementation and gives no hard guarantee.

### D6. Confirmation, export and physical integration — later

Add recording-group/origin lineage, held-out panel guards, per-origin reporting, familywise retention uncertainty and resource ledger before confirmation. Final-test data cannot enter dual updates, anchor selection, checkpoint selection or hyperparameter tuning. Support deterministic deployment evaluation separately from stochastic training costs.

Export parity uses exact saved observation/action traces and a complete sensor-to-actuator contract. Reconcile torque limits and delay semantics across simulators first. Building the runner and bench/simulator tests precede hardware authorization; this plan neither starts the robot nor authorizes a deployment. No speculative safety property follows from code inspection.

## Defer explicitly

- Utility estimator and residual practice allocator: historical Gate A/B remain binding. A policy action residual is a different component and does not waive those gates.
- Learned DR curriculum, uncertainty-driven scheduling, new world model or adaptive anchor gate: add only when a fixed recipe fails for a specific measured reason and a matched ablation can distinguish it.
- Full-body manipulation, arbitrary post-fall recovery, autonomous onboard localization and broad terrain claims: expand only after the fixed-path task works.
- Hardware efficacy, paper submission and public-page changes: require their own authorized action and actual evidence.

The complete algorithm remains proposed. Finishing a recorder, passing CPU tests, or observing a larger experiment inventory must never change its status to “validated recovery method.”
