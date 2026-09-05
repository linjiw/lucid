# LUCID quality-frontier execution status

Date: 2026-09-05. Companion [design](lucid-quality-frontier-design-2026-09-05.md) and [research plan](lucid-quality-frontier-research-plan-2026-09-05.md).

**Completed pilot:** all 20 cells and automatic analysis finished on September 5. [Results and research decision](lucid-quality-frontier-pilot-results-2026-09-05.md). Gate gains are +1.17 points over static and +3.32 over replay, but all arms substantially degrade clean tracking relative to the starting policy. Original inter-arm retention passes must not be read as preservation of that starting policy.

**Active diagnostic:** [initial-distribution campaign status](/home/linjiw/lucid-sonic/experiments/initial_hold_campaign_20260905/status.json), updated every minute. The previous [pilot monitor](/home/linjiw/lucid-sonic/experiments/quality_frontier_campaign_20260905/monitor_a/live.md) is complete and no longer polling. The narrative below preserves historical launch details.

**23:09 UTC update:** all six initial-hold smoke cells and their analysis completed; the long diagnostic is at 95/2,000 iterations with no monitor warnings. Intermediate snapshots will be evaluated after training. The frozen runtime passed 1,908 CPU tests. A separate [checkpoint contract audit](lucid-continuation-contract-audit-2026-09-05.md), with five passing focused tests, confirms exact policy/value smoke parity and identifies fresh optimizer history as a shared restart property. Its causal role in tracking drift is unresolved. No online quality veto or learned feedback signal has been activated.

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
- **Attempt B completed all 11 cells at 2026-09-05 16:14:31 UTC.** All three 16-iteration training arms and all eight evaluations passed. Cells can wait at the 11,000 MiB free-memory gate behind other shared-GPU workloads; a receipt's `running` cell includes that waiting time.

Accepted frozen-origin instrument results (512 matched replicates, one development origin):

| Condition | Completion | Tracking-qualified success |
| --- | --- | --- |
| Clean `phys_000` | 512/512 = 100% | 512/512 = 100% |
| Push 3.5× `ch_push_350` | 332/512 = 64.84% | 251/512 = 49.02% |

At Push 3.5×, 81 completed episodes failed at least one tracking threshold: 63 failed global, 49 failed local, and 31 failed both. This demonstrates a distinction between the frozen screening definitions, not a curriculum benefit or a calibrated hardware tolerance. All episodes had valid pre-step first-episode observations, and completion reconciled exactly with the unchanged upstream metric.

Static smoke checkpoint SHA-256: `8a0104ee6a1856df12d9b04fb8d3952afd684d2132533cdc38598e8c27632895`. Its own resolved config SHA-256 is `dd64060931a4d60cd38fe3e683b1e348d4bfa0e79bf4732a7379787eac8c736a`. Replay/gate policy and value tensors match exactly over their common initial schedule. Complete audited smoke outcomes and the next probe-resolution experiment are in [measurement readiness and probe resolution](lucid-quality-probe-resolution-2026-09-05.md).

The full development pilot ran from 2026-09-05 16:14:53 to 21:37:46 UTC and completed all three arms:

- Plan: `/home/linjiw/lucid-sonic/experiments/quality_frontier_pilot_20260905_a/plan.json`.
- SHA-256: `165e8d126136cd26e688ea4b78b17330e788e10128407ba771601f21b0bc7874`.
- 2,000 iterations × three arms, 1,024 training environments; two frozen-origin evaluations and five evaluations per trained arm, each with 512 replicates.
- Historical estimate was about 4.5 GPU-hours for training. Current shared-GPU iterations take roughly 6–7 seconds, implying approximately 10–12 hours of training wall time if sustained, plus evaluation/startup and queueing. Contended wall time will not establish an uncontended throughput claim.

Detached supervisor PID `862400` waits for the complete B receipt and exact planned cells, verifies finite receipt/dispatch values and all six scalable channels, then executes the frozen pilot. It stops on any smoke failure. It never launches the pilot from a partial smoke. The pilot itself re-verifies code/input/panel hashes before each cell and stops on a failed cell; there are no automatic cell retries.

Supervisor, status, and logs: `/home/linjiw/lucid-sonic/experiments/quality_frontier_campaign_20260905/`. `status.json` and each experiment's `receipt.json` are authoritative for current execution status. The supervisor waits at most 12 hours for the smoke; the already-started B driver retains its existing 30-minute per-cell GPU capacity timeout. The pilot permits up to 12 hours of capacity waiting per cell. Other jobs are not terminated or reconfigured.

No superiority, tracking-retention, or sim-to-real result is claimed from these starts. Quality veto, recovery instrumentation, and learned dynamics feedback remain subsequent measurement-gated stages.

## Analysis continuation

Commit `074046e` in `/home/linjiw/lucid-quality-feedback` adds the receipt-verified all-cell analyzer, finite-panel clean-probe resolution study, and completion-only report watcher. Full CPU suite: **1,893 passed**; Black/Ruff pass for the six additions. Analysis watcher PID `906291` completed its report and exited normally. See the [probe-resolution memo](lucid-quality-probe-resolution-2026-09-05.md) for its earlier development analysis. The completed GPU pilot retains its original frozen commit `35f19a2`.

## Scheduled health and completion monitoring

The user explicitly requested scheduling, monitoring, and post-completion analysis. A detached health monitor started at **2026-09-05 16:46:19 UTC**, PID `917843`, checking every **60 seconds for up to 24 hours**. Its first snapshot reported static training at 406/2,000 iterations, both origin evaluations complete, and no health warnings. The frozen schedule remains static training → five evaluations → replay training → five evaluations → gate training → five evaluations. No duplicate GPU campaign was launched.

The monitor runs from `/home/linjiw/lucid-campaign-monitor`, branch `research/campaign-monitor`, commit `b60eef6`. Nine focused tests passed; Black, Ruff, and `git diff --check` passed. The training and analysis checkouts retain their frozen source.

Monitoring records planned-cell status, training iteration counts, process identity including Linux start time, GPU-capacity waiting, stale logs, experiment/analysis failures, and analysis source drift. It never restarts or modifies an experimental cell. Its immutable configuration SHA-256 is `3b3bf282773d2fffa2183aeceebf5028a80fd53e3f8ee2fc7f5962f6a5e5febe`.

When the full pilot finishes, the existing analysis watcher verifies the artifacts and writes the complete comparison. The health monitor then verifies the analysis output hashes and writes a final development-results summary that preserves both gains and failed retention checks. It cannot label an incomplete primary grid or changed artifacts as a completed result.

Local outputs under `/home/linjiw/lucid-sonic/experiments/quality_frontier_campaign_20260905/monitor_a/`:

- `live.md` and `status.json`: current schedule and health.
- `history.jsonl`: one-minute progress history.
- `results.md`: generated only after successful verification of the completed pilot analysis.
- `monitor_error.json`: written if the monitor itself fails or its time budget expires.

The full analysis destination is `/home/linjiw/lucid-sonic/analysis/quality_frontier_pilot_20260905_a/`. These are local background jobs and local reports; no external message or publication is scheduled. Source receipts remain authoritative if monitoring expires before the campaign completes.
