# LUCID retention screen: executable development campaign

September 6, 2026. This continues the [quality-preserving robustness plan](lucid-retention-repair-plan-2026-09-06.md). The most promising next test remains frozen-origin behavioral anchoring during the known productive Push mixture, compared with ordinary continuation and a conservative update control. No retention improvement or feedback advantage has yet been demonstrated.

**Execution amendment:** the optimizer control and collection completed, selecting fresh history. The original campaign stopped before smoke on a CPU/native-TF32 target mismatch. [Precision repair and restarted execution](lucid-anchor-precision-repair-2026-09-06.md) supersede the CPU-only validation and active campaign paths below; the original frozen attempt is preserved. The new source validates native precision and uses two 128-row anchor forwards per unchanged 256-sample update, counting their cost.

## Frozen implementation and dependencies

Implementation: `/home/linjiw/lucid-retention-screen`, branch `research/retention-screen`, commit `862f380`. It extends the previously tested anchor implementation (`940af95`) in a separate worktree. Both the running optimizer-history source and queued collection source remain unchanged. No upstream SONIC trainer module was edited.

The campaign configuration is [campaign.json](/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_a/campaign.json). The supervisor executes the following sequence serially and stops on any failed contract, without retrying or silently modifying a plan:

1. Require the complete 2,000-iteration fresh/restored-history control, every planned evaluation, and verified analysis outputs. Require the existing dedicated clean/original-envelope collection worker's completed, hash-bound 2,048-record buffer.
2. Select one common continuation recipe using the bounded rule below, then write the full decision and its input hashes.
3. Recompute all collected action targets with the actual frozen-origin actor on CPU. Require checkpoint/config/normalization/history identity and target agreement with declared GPU/CPU tolerances (absolute 1e-4, relative 1e-5). This is numerical interface evidence, not a behavioral result.
4. Freeze and execute a matched 16-iteration smoke: native trainer plus R0, R1 and R2. Require exact native/R0 policy and value checkpoint parity, declared optimizer history, every applied optimizer rate, fixed 768/256 membership and channel vectors including warmup, delayed-actuator dispatch, valid exports, and anchor work counts. No smoke performance threshold selects a method.
5. Only after smoke passes, freeze and execute all three 2,000-iteration repair arms, with every saved checkpoint evaluated at all five conditions. Analyze the complete grid and export CSV, JSON, Markdown and standalone PNG/PDF robustness-retention figures.

A full pilot has 3 training cells and 80 evaluation cells: origin plus five checkpoints per arm, each at clean, original envelope, Push 3×, Push 3.5×, and Push 3.5×/friction 1.5×. The smoke has 4 training and 12 evaluation cells. The two held-out hard conditions never affect training exposure. GPU starts require 11,000 MiB available memory; each simulator process remains separately logged.

## Bounded continuation selection

Restore history only if all five saved clean checkpoints retain both legacy pose errors within +10% of origin and completion within two points; both unweighted checkpoint-grid mean error ratios are no worse than fresh history and at least one is strictly better; the final mean qualified success across the two hard conditions is no worse than fresh; and final original-envelope completion is no more than two points worse than fresh. Otherwise use fresh history. The complete comparison is reported regardless of the choice.

This operationalizes the earlier preference for fresh history unless restoration offers a useful quality advantage. It was specified after fresh history completed and while restoration was still training. It is a one-origin development decision, not a preregistered confirmation test or an explanation of degradation under a different exposure trajectory. No optimizer sweep follows automatically.

## Rate-contract correction

The native PPO code adjusts rates using KL before optimizer steps even when the outer TRL scheduler is configured constant. The latter resets optimizer groups before step-end callbacks and checkpoint export. Both inspected origin and fresh endpoint checkpoints save 2e-5 group rates; those values do not reconstruct the applied update trajectory. [Source and checkpoint audit](/home/linjiw/lucid-sonic/analysis/retention_update_contract_20260906_a/audit.json).

R0 and R1 preserve native `desired_kl=0.01`, initial rate 2e-5, and inner bounds [1e-5, 2e-4]. R2 uses initial and applied fixed rates 1e-5 with `desired_kl=null`. This is a conservative fixed-rate control, not simply a lower-initial-rate control. If restoration is selected, all arms receive the same source moments/counters while R2 retains its declared recipient rates. Each branch records rates immediately before every optimizer step and again after outer scheduler reset. The old running comparison is unchanged, and this code finding does not establish the cause of tracking deterioration.

## Outcomes and resource contract

The development endpoint is useful hard-condition tracking qualification together with retained clean and original-envelope behavior. Retention uses paired episode-mean differences against 1.10 times the origin, separately for global and local errors, plus a two-point completion margin. All sampled earlier breaches remain visible even if an endpoint recovers. The legacy metrics are reported alongside these masked episode metrics. Mean-difference standard errors are descriptive fixed-look episode uncertainty, not sequential confidence bounds. A matching alias and seed do not guarantee identical policy-dependent random trajectories.

All arms share 768 original-envelope environments plus 256 Push 3× environments, seed 8600, the solved origin, existing rewards/observations/actions/terminations and auxiliary losses. R1 uses beta 1, identity action normalization, 256 buffer samples per optimizer update and isolated seed 8610. No beta or rate sweep is silently added.

The full screen allocates 49,152,000 training transitions and 40,000 PPO updates per arm. R1 adds 10,240,000 anchor sample presentations. Full-grid evaluation uses 40,960 scored episodes. Smoke adds 1,572,864 training transitions and 6,144 scored evaluation episodes; its R1 branch adds 81,920 anchor presentations. Dedicated buffer collection, teacher work, actual dispatch counts, actual rates, anchor forwards, full training wall time, and unsuccessful starts remain in separate receipts. Backward work is combined with PPO and priced through wall time; equal transition budgets are not equal computation budgets.

A small action loss alone does not establish a repair. If the conservative control matches the anchor at retained quality, choose the simpler recipe. If anchoring preserves quality without useful adaptation, investigate measured error components before changing the curriculum. This campaign never automatically starts adaptive allocation, a utility estimator, fresh-origin confirmation, or hardware. Recovery-qualified endpoints still require component and event-alignment validation.

## Validation and monitoring

Final CPU suite: **1,996 passed**, four warnings, 39.67 s. [Log](/home/linjiw/lucid-sonic/outputs/retention_screen_cpu_20260906_b.log). Tests cover complete versus partial grids, preservation of sampled breaches, paired episode differences, bounded continuation selection, native parity, warmup telemetry, scaled fresh/restored history, native KL versus fixed rates, and failed or altered prerequisites. Black and Ruff pass on all nine changed files; staged whitespace checks pass. Repository-wide `make run-checks` still fails in existing isort violations beginning in `motionbricks/`; the root isort/Ruff ordering conflict remains. [Check log](/home/linjiw/lucid-sonic/outputs/retention_screen_run_checks_20260906_a.log).

The [predecessor status](/home/linjiw/lucid-sonic/experiments/optimizer_history_campaign_20260905/status.json) showed fresh training and its evaluations complete, restored training at 443/2,000, and no warnings at 05:38 UTC. These are execution observations, not partial efficacy conclusions.

Monitor the [campaign status](/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_a/status.json), [launch receipt](/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_a/launch.json), and [supervisor log](/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_a/supervisor.log). Future `smoke/plan.json` and `pilot/plan.json` are created only after their prerequisites, binding the realized selected recipe, actual buffer and all source/input hashes. Future `analysis/report.md` records the complete development screen.

## W&B attachment — 15:01 UTC

Per the user's instruction, campaign `_b` is now mirrored online to [W&B](https://wandb.ai/16726/lucid-sonic/runs/ret-c67d12b4b05f6edbcddd) with separate named cell runs. Two completed origin evaluations are explicitly backfilled and verified against the API. The active Push 3.5x origin evaluation remains queued behind the GPU capacity gate. Monitor PID `2061148` follows both smoke and pilot automatically; frozen simulator sources and campaign configuration remain hash-identical. See `lucid-wandb-experiment-logging-2026-09-06.md` for logging coverage, links, naming, and the restart command.

## Restart `_c` and live anchored updates

The `_b` attempt failed when its anchor-origin digest was checked after native rollout mutated the exploration-noise parameter. The isolated timing fix (`2d4aa0a`, 2,022 passing CPU tests) binds the exact origin before rollout. Fresh campaign `_c` launched at 15:30 UTC with [online W&B](https://wandb.ai/16726/lucid-sonic/runs/ret-46911b8054776113fe91). Native and R0 smoke training have completed with exact 72-tensor checkpoint parity, and R1 has passed its previous failure point and performed real anchored optimizer updates. See `lucid-anchor-start-repair-2026-09-06.md` for the reproduction, receipts, active PIDs, and current scope.
