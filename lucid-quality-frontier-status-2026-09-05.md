# LUCID quality-frontier execution status

Date: 2026-09-05. Companion [design](lucid-quality-frontier-design-2026-09-05.md) and [research plan](lucid-quality-frontier-research-plan-2026-09-05.md).

## Implementation

Isolated SONIC worktree: `/home/linjiw/lucid-quality-frontier`, branch `research/quality-frontier`. Commit `bdb4dbc` adds the runtime vector replay, fixed per-stratum support allocation, bounded box-gate comparator, first-episode tracking qualification, and the serial pilot runner. Commit `35f19a2` fixes reconciliation with the upstream `eval/success/success_rate` namespace and adds a regression test. Original worktree changes are preserved.

The new callback records both the vectors used for the completed rollout and those dispatched for the next. Replay resume checks exact environment membership, cursor, allocation mode, and source digest. The evaluator reports tracking-qualified success separately from legacy metrics; physical quality remains unvalidated. The online quality veto and dynamics latent are planned later stages, not implemented features.

## CPU validation

- Final `python -m pytest tests/practice_utility/`: **1,861 passed**, four warnings, 40.21 s. Log: `/home/linjiw/lucid-sonic/outputs/quality_frontier_cpu_fix_20260905.log`.
- Initial focused replay/measurement/runner contracts: 26 passed. The post-fix measurement suite has 12 passing cases, including two new completion-reconciliation cases.
- Black and Ruff pass on the eight new files. `git diff --check` passes.
- `make run-checks` stops at pre-existing repository-wide isort errors, beginning in `motionbricks/`; log: `/home/linjiw/lucid-sonic/outputs/quality_frontier_run_checks_20260905.log`. These upstream files were not reformatted.
- An initial bare `pytest` invocation imported launch modules through the original editable checkout; it is excluded. `python -m pytest` from the isolated checkout resolves the intended source and passes.

## GPU integration attempt A

Immutable plan: `/home/linjiw/lucid-sonic/experiments/quality_frontier_smoke_20260905_a/plan.json`.
SHA-256: `20ac3da1c0ceed6b0744c5da6c22a37219789c138a2bd5371c2572042a03e21c`.

Execution command, after sourcing `/home/linjiw/lucid/env/lucid_env.sh` with `LUCID_REPO=/home/linjiw/lucid-quality-frontier`:

```bash
python scripts/practice_utility/run_quality_frontier.py \
  --execute-plan /home/linjiw/lucid-sonic/experiments/quality_frontier_smoke_20260905_a/plan.json \
  --plan-sha256 20ac3da1c0ceed6b0744c5da6c22a37219789c138a2bd5371c2572042a03e21c
```

The plan runs frozen-origin clean/Push-3.5× evaluations, followed by three 16-iteration training arms and their clean/Push-3.5× evaluations. Training uses 1,024 environments; evaluation uses 512 matched replicates. Seed 8600 is development. Thresholds are global 600 mm/local 50 mm engineering screens and carry no hardware-safety claim.

Attempt A **failed** during the first frozen-origin clean evaluation's metric export. All 512 motions had executed, but the qualification callback requested the wrong upstream completion key. Its failed receipt and log are preserved. No training arm ran in attempt A, and its incomplete export is not an accepted measurement result.

## GPU integration attempt B and conditional pilot

Attempt B uses corrected commit `35f19a2` and a fresh immutable directory:

- Plan: `/home/linjiw/lucid-sonic/experiments/quality_frontier_smoke_20260905_b/plan.json`.
- SHA-256: `91dac75733137dfa6f0143a152db90cbca82372409fdfdfaed91d57b193c0383`.
- Driver PID at launch: `847668`; managed session `38728`.
- At this status update, the first evaluation is waiting at the 11,000 MiB free-memory gate behind other shared-GPU workloads. A receipt's `running` cell includes time waiting for capacity; it does not by itself establish that simulation has started.

The full development pilot is prepared but has not begun training:

- Plan: `/home/linjiw/lucid-sonic/experiments/quality_frontier_pilot_20260905_a/plan.json`.
- SHA-256: `165e8d126136cd26e688ea4b78b17330e788e10128407ba771601f21b0bc7874`.
- 2,000 iterations × three arms, 1,024 training environments; two frozen-origin evaluations and five evaluations per trained arm, each with 512 replicates.
- Historical estimate: about 4.5 GPU-hours for training, plus evaluation/startup and shared-resource queue time. Contended wall time will not establish a throughput claim.

Detached supervisor PID `862400` waits for the complete B receipt and exact planned cells, verifies finite receipt/dispatch values and all six scalable channels, then executes the frozen pilot. It stops on any smoke failure. It never launches the pilot from a partial smoke. The pilot itself re-verifies code/input/panel hashes before each cell and stops on a failed cell; there are no automatic cell retries.

Supervisor, status, and logs: `/home/linjiw/lucid-sonic/experiments/quality_frontier_campaign_20260905/`. `status.json` and each experiment's `receipt.json` are authoritative for current execution status. The supervisor waits at most 12 hours for the smoke; the already-started B driver retains its existing 30-minute per-cell GPU capacity timeout. The pilot permits up to 12 hours of capacity waiting per cell. Other jobs are not terminated or reconfigured.

No superiority, tracking-retention, or sim-to-real result is claimed from these starts. Quality veto, recovery instrumentation, and learned dynamics feedback remain subsequent measurement-gated stages.
