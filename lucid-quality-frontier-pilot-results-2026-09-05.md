# LUCID quality-frontier pilot: results and next diagnostic

The pilot completed all 20 planned cells: three 2,000-iteration training arms and 17 frozen-policy evaluations, each with 512 matched replicates. It ran from 2026-09-05 16:14:53 to 21:37:46 UTC, about 5 hours 23 minutes including training and evaluation. Training subprocesses totalled 5.18 hours and evaluation subprocesses 10.61 minutes. The earlier contention-based 10–12-hour extrapolation did not persist.

The gate has a modest descriptive advantage over its trained controls, but the central result is a large loss of clean tracking quality in every arm. This is one development seed, one G1 hands-on-back motion, and simulation only. It does not establish a method-level superiority claim or physical transfer.

## Frozen primary comparison

Tracking-qualified success requires completion plus episode-mean global error ≤600 mm and local error ≤50 mm. The primary endpoint averages Push 3.5× and Push 3.5× + Friction 1.5× equally. These are screening thresholds, not good absolute imitation or hardware tolerances.

| Arm | Held-out tracking-qualified success | Clean completion | Clean global MPJPE | Clean local MPJPE |
| --- | ---: | ---: | ---: | ---: |
| Starting policy | Not evaluated on the full primary grid | 100.00% | 128.57 mm | 28.33 mm |
| Static hard allocation | 39.16% | 99.80% | 357.97 mm | 35.91 mm |
| Frozen replay | 37.01% | 100.00% | 373.92 mm | 35.26 mm |
| Survival feedback gate | 40.33% | 100.00% | 324.50 mm | 34.78 mm |

Gate minus static: **+1.17 points**. Gate minus replay: **+3.32 points**. All three arms ended at the same accepted frontier vector. The static control can combine per-channel marginal extremes absent from the rotating schedule; equal marginal bounds are not identical joint exposure. Same-origin replay is a development comparison, not evidence of adaptation across fresh origins.

## The quality result the inter-arm checks cannot establish

The original automatic report correctly marks the prespecified *inter-arm* retention checks as passing: gate is no worse than static/replay within the margins. Those checks do not establish preservation of the starting policy when all controls degrade together. The updated analyzer now reports origin-relative diagnostics explicitly, without changing the original endpoints or pass/fail rules.

| Arm | Clean global increase versus origin | Clean local increase versus origin | Both within a 10% origin-relative margin? |
| --- | ---: | ---: | --- |
| Static | +178.43% | +26.73% | No |
| Replay | +190.83% | +24.44% | No |
| Gate | +152.39% | +22.75% | No |

At the directly shared Push 3.5× condition, the gate raises completion from **64.84% to 71.09%**, while tracking-qualified success falls from **49.02% to 45.70%**. Thus higher completion does not imply better useful tracking performance. The origin was not evaluated on the composition cell, so no origin-relative two-cell macro is inferred.

The masked first-episode global/local errors also show the large clean degradation in replay and gate. It is not explained away by the known post-reset contamination of older physical telemetry. The static clean panel contains one failed episode, so its paired subset quality-resolution analysis is correctly marked ineligible; its completion and legacy errors remain reported.

## Research decision

Do not promote the survival-only gate into a superiority confirmation on the strength of this pilot. Preserve its modest control-relative result, but resolve the larger retention failure first. The original utility-estimator and residual-allocator gates remain unchanged.

The next feedback design should keep three distinct quantities:

1. Candidate competence: completion and tracking-qualified success at a named DR condition.
2. Retention relative to a frozen starting/reference policy: continuous global and local tracking errors, plus completion, at fixed retained conditions.
3. Recovery/information diagnostics: disturbance-aligned recovery and history-derived response prediction, added only after demonstrating incremental measurement or predictive value.

The initial veto hypothesis is now narrower: hold expansion when an origin-relative quality budget is exhausted. Before implementing that as an online intervention, determine whether holding the initial support can prevent the drift. If it cannot, the method must address training/retention itself; a more elaborate difficulty signal will not repair the demonstrated failure by itself.

## New diagnostic: fixed initial distribution with intermediate snapshots

Implementation checkout `/home/linjiw/lucid-origin-retention`, branch `research/origin-retention`, commit `e5437b8`.

- Adds `allocation=initial`: preserve the source's initial absolute vectors and exact cohort membership throughout the continuation. Resume preserves that initial allocation; the finite horizon and source identity remain enforced.
- Keeps the solved origin, seed 8600, PPO configuration, motion, 1,024 environments, delayed actuator setup, and 2,000-iteration budget.
- Saves verified policy capsules at 250, 500, 1,000, 1,500, and 2,000 iterations. Checks capsule integrity, exact step, branch, horizon label, and each checkpoint's own config before evaluation.
- Evaluates clean tracking at the intermediate checkpoints and the same five endpoint conditions at 2,000 iterations. Probes run after training from frozen snapshots and do not feed back into training.
- Runs a six-cell 16-iteration integration smoke first, including an 8-iteration snapshot, before the 12-cell long diagnostic.

This holds the **E0 initial cohort distribution**, not necessarily the exact distribution on which the origin was originally trained. Its six low strata scale at 1/7 through 6/7, its main frontier is 1.0, and its initial probe already uses 1.125 for joint-default-position offsets. That fixed probe is preserved. Therefore:

- If quality is preserved without expansion, growth of exposure becomes a stronger explanation and an origin-anchored quality veto is worth testing.
- If quality still drifts, expansion is not necessary for the loss. Investigate ordinary continuation under this initial mixture, reference coverage, tracking incentives, and retention practice before attributing the problem to DR growth alone.

Neither outcome by itself proves a physical or representational capacity boundary. The snapshot grid only brackets observed drift between saved policies; it cannot identify an exact first-failure iteration.

Validation: **1,908 CPU tests passed**, five warnings, 52.58 s. Focused callback/driver/analyzer tests passed; Black/Ruff and whitespace checks passed for the changed files. A real prior GPU capsule also passed the integrity loader used for intermediate exports. CPU log: `/home/linjiw/lucid-sonic/outputs/origin_retention_cpu_20260905.log`.

## Receipts and execution

Original complete pilot: `/home/linjiw/lucid-sonic/experiments/quality_frontier_pilot_20260905_a/receipt.json`.
Original automatic report remains preserved at `/home/linjiw/lucid-sonic/analysis/quality_frontier_pilot_20260905_a/`.
The supplemental origin audit, with unchanged primary contrasts and source/output hashes, is `/home/linjiw/lucid-sonic/analysis/quality_frontier_origin_audit_20260905/`.

New immutable plans:

- Smoke: `/home/linjiw/lucid-sonic/experiments/initial_hold_smoke_20260905_a/plan.json`; SHA-256 `6926f0169f09f403e3528b2573ec0ee8523e7ccd8291394fbfc72ffe9cb9cfc2`.
- Long diagnostic: `/home/linjiw/lucid-sonic/experiments/initial_hold_pilot_20260905_a/plan.json`; SHA-256 `8453c7d6296f09b97f8c6cb08b7fa89e201379c8101aa7d49cda17d78ff24417`.

Detached supervisor PID `1172907` started at 2026-09-05 22:44:52 UTC. It runs smoke → verified analysis → long diagnostic → verified analysis serially, monitors progress every minute, and stops on failure. Capacity waits permit up to 12 hours per cell. Initial status and history: `/home/linjiw/lucid-sonic/experiments/initial_hold_campaign_20260905/`. Training, probe, failed-start, and queue costs remain separately identifiable in receipts.

Update at 23:09 UTC: all six smoke cells and analysis completed; the long run reached 95/2,000 iterations. Clean smoke completion and tracking qualification remain 100%, but there is no long-run retention outcome yet. The [continuation contract audit](lucid-continuation-contract-audit-2026-09-05.md) confirms exact policy/value tensor parity with the prior replay smoke and clarifies that all arms use fresh optimizer history. This adds a candidate retention mechanism for a later controlled test; it does not establish the cause of the completed pilot's drift.
