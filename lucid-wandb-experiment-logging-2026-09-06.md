# W&B experiment logging — September 6, 2026

User instruction: always log running experiments to W&B and organize their names and metadata.

## Active retention campaign

- Project: https://wandb.ai/16726/lucid-sonic
- Group: `retention_screen_campaign_20260906_b`
- Campaign monitor: https://wandb.ai/16726/lucid-sonic/runs/ret-c67d12b4b05f6edbcddd
- Clean origin: https://wandb.ai/16726/lucid-sonic/runs/ret-fac03c3240827e644116
- Original-envelope origin: https://wandb.ai/16726/lucid-sonic/runs/ret-0e95c1b008884b4f1564
- Push 3.5x origin: https://wandb.ai/16726/lucid-sonic/runs/ret-9ff0d5614b5bb7c4b5c6

At 15:01 UTC, two of 16 smoke cells are complete. Push 3.5x origin is waiting for the existing 11,000 MiB GPU capacity gate. Long training has not started. The existing supervisor automatically executes the smoke, checks native/R0 parity, then launches the frozen 2,000-iteration R0/R1/R2 screen and analyzes its full evaluation grid. It stops on a failed scientific gate.

W&B API verification confirms both completed evaluations are `finished`, their global MPJPE values exactly match local files (128.57060948226064 and 214.03711667030043 mm), and qualified success is 1.0 and 0.98046875. The next evaluation is online with `source_phase=waiting_for_gpu_capacity`. W&B running state describes the logging process; use `source_phase` to distinguish queued simulator work from execution.

## Naming and provenance

Cell names: `retention/<smoke|pilot>/<origin|native|R0|R1|R2>/s<evaluation-or-training-seed>/<cell-id>`.

Each run records both seeds, stage, arm, checkpoint iteration or training horizon, evaluation preset, exact command, source commit, frozen plan and campaign SHA256, anchor buffer SHA256, and optimizer recipe. Training streams scalar console metrics and existing JSONL telemetry, including realized exposure, quality, optimizer rates, and anchor costs. Evaluation runs log available all-motion and success-conditioned MPJPE separately, completion, tracking-qualified success, energy, foot slip, and runtime. Missing signals remain missing. No new metric is inferred from another metric.

The two finished origin evaluations are explicitly marked `backfilled_at_attachment=true`; subsequently attached running cells are false. Stable IDs bind campaign SHA, stage, and cell. Source byte offsets and iteration fields support provenance and deduplication. Resume avoids replaying finished cells; an interruption between W&B enqueue and local cursor persistence may duplicate an event, and local receipts remain authoritative. The monitor disables its own system statistics so its CPU process is not presented as simulator resource consumption.

## Implementation and operation

The frozen simulator commands already disable native W&B. An independent read-only online monitor observes them without changing the experiment. All 1,037 frozen source files and the campaign hash were rechecked after attachment: no mismatches.

- Monitor worktree: `/home/linjiw/lucid-wandb-monitor`
- Commit: `4006975` (`research/practice-utility: stream immutable retention campaigns to W&B`)
- Script: `scripts/practice_utility/monitor_retention_wandb.py`
- Tests: `tests/practice_utility/test_retention_wandb.py` and `test_retention_campaign.py`: **25 passed**.
- Runtime directory: `/home/linjiw/lucid-sonic/monitoring/retention_screen_campaign_20260906_b`
- Monitor PID: `2061148`; interval: 30 seconds.
- Runtime files: `launch.json`, `state.json`, `online_verification.json`, `monitor.log`, and W&B SDK spool.
- Experiment supervisor PID: `2022309`; driver PID: `2022519`.

Exact monitor command (initialize the pinned environment first):

```bash
export LUCID_REPO=/home/linjiw/lucid-wandb-monitor
source /home/linjiw/lucid/env/lucid_env.sh
python -u scripts/practice_utility/monitor_retention_wandb.py \
  --campaign /home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_b \
  --output /home/linjiw/lucid-sonic/monitoring/retention_screen_campaign_20260906_b \
  --entity 16726 --project lucid-sonic --interval 30
```

The active copy is detached via `subprocess.Popen(..., start_new_session=True)`; it does not rely on the chat remaining open. The monitor takes an exclusive lock, retries logging errors without altering simulator execution, follows smoke and pilot stages, and exits at campaign completion/failure. SDK spool files retain local logging data during network interruptions; verify online recovery instead of assuming every queued event reached W&B.

For future campaigns, `AGENTS.md` now requires online W&B and verified run URLs. `env/lucid_env.sh` defaults `WANDB_MODE=online` and `WANDB_PROJECT=lucid-sonic`. New plans must also enable native `use_wandb`; the environment variable alone does not enable the callback. Frozen campaigns use this monitor. Never upload credentials, motion datasets, or large checkpoints as configuration.

## Active campaign superseded at 15:30 UTC

Campaign `_b` later failed at the R1 pre-update identity check after eight completed cells. It is preserved. The corrected campaign is now `_c`, with [new online dashboard](https://wandb.ai/16726/lucid-sonic/runs/ret-46911b8054776113fe91), monitor PID `2139831`, and runtime directory `/home/linjiw/lucid-sonic/monitoring/retention_screen_campaign_20260906_c`. See `lucid-anchor-start-repair-2026-09-06.md` for the diagnosed native std clamp and the repaired check timing. Earlier `_b` links describe historical results, not the current running campaign.
