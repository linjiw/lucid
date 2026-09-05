# LUCID: measurement readiness and clean-probe resolution

Date: 2026-09-05. This advances the [quality-frontier research plan](lucid-quality-frontier-research-plan-2026-09-05.md). It reports integration and a secondary development analysis, not curriculum efficacy or a validated online veto.

## Completed integration

Smoke attempt B completed all 11 planned cells at `2026-09-05T16:14:31Z`: two frozen-origin evaluations, three 16-iteration training arms, and two evaluations per trained arm. Every evaluation scored the full 512-alias panel, reconciled episode completion, and had valid first-episode pose samples. Training passed the iteration, stratum, channel, actuator, and checkpoint/config contracts.

Replay and the survival-only gate produced exactly equal tensors for all 55 policy and 17 value state-dict entries at the end of the smoke. This is expected because their short initial schedules coincide. It is a useful runtime parity check, not evidence that adaptive timing is unnecessary over 2,000 iterations.

The fixed hard allocation differs during that initial period. Its clean global legacy error is 137.82 mm versus the origin's 128.57 mm. Every clean trial still completes and passes the deliberately permissive tracking thresholds. This illustrates why an online retention observer needs continuous error measurements alongside binary qualification.

Audited results, per-cell CSV, figure/PDF, and source/output hashes: `/home/linjiw/lucid-sonic/analysis/quality_frontier_smoke_20260905_b/`. The complete artifact is `receipt.json`. Its Markdown report preserves all eight evaluated cells. The smoke omits standard DR and the push–friction composition, so the analyzer leaves the full primary contrast and combined retention decision unavailable rather than substituting the observed subset.

## What was implemented next

Separate checkout `/home/linjiw/lucid-quality-feedback`, branch `research/quality-feedback`, commit `074046e`:

- `frontier_analysis.py` verifies episode identities, thresholds, finite observations, qualification, and aggregate denominators. It reports the frozen two-cell held-out endpoint alongside clean/standard completion and clean legacy pose retention.
- `quality_probe_resolution.py` measures how masked clean tracking errors vary across matched subsets of an already-observed evaluation panel.
- `analyze_quality_frontier.py` verifies plan, metric, checkpoint, and config hashes; exports all-cell JSON/CSV/Markdown/PNG/PDF; and can wait for a complete experiment receipt. Failed or partial runs cannot silently become completed comparisons.

Final CPU suite: **1,893 passed**, four warnings, 38.01 seconds. Log: `/home/linjiw/lucid-sonic/outputs/quality_feedback_cpu_final_20260905.log`. Black and Ruff pass on all six added files. Keep this analysis checkout frozen while its detached watcher is active; future method edits should use another branch/worktree.

## Secondary CPU experiment: probe resolution

For each trained smoke policy, compare its clean masked episode-mean global/local errors with the frozen origin on the same alias identities. Use 1,000 deterministic random subsets of each size, without replacement within a draw, seed 20260905. The ratio is `mean(target error) / mean(origin error) - 1`, separately for global and local errors. A strict increase above 10% crosses the screening margin, with numerical tolerance at the boundary.

This is a secondary development analysis using masked errors. It does not replace the pilot's frozen legacy-error retention endpoint. A clean completion failure or mismatched observation horizon makes the subset quality comparison ineligible; a short failure prefix cannot make retention appear better.

For the static smoke policy, the full-panel masked global increase is **7.19%**, below the 10% screening margin:

| Episodes per policy | 5th–95th percentile of subset global increases | Subsets crossing 10% |
| ---: | ---: | ---: |
| 32 | −1.54% to +15.94% | 28.9% |
| 64 | +1.67% to +13.16% | 24.3% |
| 128 | +3.62% to +10.64% | 10.4% |
| 256 | +5.12% to +9.36% | 2.3% |
| 512 | +7.19% to +7.19% | 0% |

The static local increase is only 0.99%; none of these subsets crosses its 10% margin. Replay and gate have full-panel masked global/local changes of −3.08%/−2.02% relative to origin.

These ranges are **finite-panel subset percentiles, not confidence intervals**. Reusing the same 512 episodes does not create 1,000 new independent experiments. The zero width at 512 is inevitable because every draw contains the whole finite panel; it does not mean that a fresh 512-episode experiment has zero uncertainty. Matched alias/seed identity also does not guarantee identical stochastic trajectories across policies.

The present static example lies below the veto margin. It tests stability near that margin, not sensitivity to a true above-margin degradation. A reliable online decision requires independent probe repetitions on additional policy states and conditions, including both sides of the threshold, with a prespecified sequential procedure.

## Consequences for the next method stage

1. Keep completion, global tracking, and local articulation as separate feedback components. A clean 100% qualification rate can coexist with measurable error growth.
2. Do not use a 32-episode point estimate to fire the quality veto. In this observed example it crosses the margin on more than a quarter of the available subsets.
3. Treat 256 episodes as a candidate probe size for independent calibration, not an established requirement or sufficient sample size. Compare its uncertainty and cost with 512 and longer fixed decision blocks.
4. Measure actual probe cost. Reducing the selected episode count in this CPU study does not measure savings in simulator starts, wall time, or GPU memory. A smaller parallel panel can retain much of Isaac's fixed startup cost.
5. Freeze probe times, references, missing-data handling, candidate competence threshold, confidence procedure, consolidation blocks, and total cost before an online-veto comparison. Missing evidence must hold expansion. Every comparator must pay the same probe cost.
6. Use dedicated intermediate snapshots in that next study. The current E0 pilot saves final capsules only; it can characterize endpoint tradeoffs, but cannot reconstruct when an early quality veto would have fired. Its running protocol is unchanged.

The utility estimator and residual allocator remain gated. History-derived dynamics feedback remains a later prediction/ablation stage. This study neither adds those components nor establishes sim-to-real transfer.

## Running full pilot and automatic analysis

The three-arm 2,000-iteration pilot began at `2026-09-05T16:14:53Z`, after the smoke gate passed. At this update its static arm is training, with replay and gate queued serially. Current shared-GPU iterations take roughly 6–7 seconds; if sustained, this implies around 10–12 hours for all three training arms, plus starts, evaluations, and queueing. This extrapolation is not a promised finish time or an uncontended throughput measurement. The environment-step budget remains unchanged.

The existing campaign supervisor PID is `862400`. Analysis watcher PID `906291` waits up to 24 hours for a complete pilot receipt, then generates `/home/linjiw/lucid-sonic/analysis/quality_frontier_pilot_20260905_a/`. It stops on a failed campaign or changed plan. Its current status is `/home/linjiw/lucid-sonic/analysis/quality_frontier_pilot_20260905_a.watch.json`; its log is in the campaign directory. It does not launch another simulator or modify the pilot.

The authoritative run receipt remains `/home/linjiw/lucid-sonic/experiments/quality_frontier_pilot_20260905_a/receipt.json`. No long-pilot performance conclusion is available yet.
