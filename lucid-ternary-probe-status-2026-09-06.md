# LUCID ternary probe: offline inference and synthetic calibration

September 6, 2026. This advances the supplied ICRA guidance through the
[updated roadmap](lucid-icra-roadmap-2026-09-06.md), while the optimizer comparison
and serial retention screen continue under their frozen contracts. This is a CPU
inference reference; it neither changes the training controller nor demonstrates
robot tracking improvement.

## Implemented and tested

Worktree `/home/linjiw/lucid-ternary-probe`, branch `research/ternary-probe`, commit
`657148c`, based on recovery-measurement commit `e145106`. The worktree is isolated
from all running and queued campaign sources.

[ternary_probe.py](/home/linjiw/lucid-ternary-probe/gear_sonic/research/practice_utility/ternary_probe.py)
implements named mean constraints with explicit units/support/threshold/direction,
a finite look schedule and attempt budget, bounded-outcome Hoeffding intervals,
and Expand / Hold / Unresolved decisions. It has no robot tolerance defaults.

Expand requires every constraint to pass and no missing outcomes. Hold requires
supported failure of at least one constraint, including quality. Otherwise request
the next declared cumulative sample count; at the cap, remain unresolved. Boundary
equality passes, while a supported failure must strictly exclude the boundary.
All endpoint denominators match unique row identities. Missing outcomes retain
their denominator with worst-case support bounds; non-finite or out-of-support
observations invalidate the contract. No implicit clipping, dropped failed rows,
unplanned look or exhausted attempt is accepted.

For M endpoints, L planned looks and K attempts, each two-sided interval spends
`alpha / (K * L * M)`. Its radius is
`(upper_support - lower_support) * sqrt(log(2 / interval_alpha) / (2*n))`.
A union bound gives finite-family error control under independent rows with a
common bounded mean within each frozen-policy attempt. Endpoints within a row and
nested looks need not be independent. Later adaptively selected attempts require
fresh conditionally valid data. The online caller would need a persistent policy,
condition, sample and alpha ledger; this offline component does not supply it.

These assumptions are substantive. Alias uniqueness does not prove simulator
independence, and a maximum observed MPJPE is not an almost-sure population bound.
For origin-relative quality, preserve variation in both policy and origin, e.g.
`student_episode_error - 1.10 * origin_episode_error`, with a justified pairing
and failed-episode contract. No live raw-MPJPE confidence guarantee is established
by this implementation. A tighter valid procedure is still needed if genuine
support bounds make this conservative reference too costly.

## Synthetic experiment and finding

The [validation script](/home/linjiw/lucid-ternary-probe/scripts/practice_utility/validate_ternary_probe.py)
writes its plan before sampling, binds committed source hashes and preserves
non-overwriting outputs. Fixed seed 20260906; 2,000 independent repetitions per
case; looks 128/256/512/1,024; eight reserved attempts; family alpha 0.05; three
endpoints. Synthetic survival threshold is 0.8. The two synthetic quality margins
have support [−1, 1] and threshold zero. These are not robot-selected parameters.

| Synthetic population | Expand / hold / unresolved | Mean hypothetical stopping rows |
| --- | ---: | ---: |
| Clearly feasible: survival 0.98, both quality means −0.4 | 2,000 / 0 / 0 | 221.82 |
| Survival failure: survival 0.55, quality −0.4 | 0 / 2,000 / 0 | 134.98 |
| Quality failure: survival 0.98, quality +0.4 | 0 / 2,000 / 0 | 137.73 |
| Boundary: survival 0.8, quality 0 | 0 / 0 / 2,000 | 1,024.00 |
| Feasible but close: survival 0.86, quality −0.05 | 0 / 0 / 2,000 | 1,024.00 |
| Invalid independence: boundary outcomes repeated in blocks of 128 | 405 / 1,595 / 0 | 128.00 |

No interval miss or incorrect resolved decision was observed in the five valid
cases. Zero observed errors is not zero risk or proof of the analytical bound.
The near-feasible case is decisive for research planning: a formally conservative
rule can exhaust its budget without useful admission. This does not establish
that 128 or 1,024 real episodes are sufficient, nor that every valid procedure
will fail there. The dependence stress case produces 79.75% false holds and
interval miscoverage in all 2,000 repetitions, illustrating an explicit assumption
violation rather than a failure under the promised conditions.

The program generates every full panel and checks every look for calibration.
Stopping rows are simulated decision costs; no GPU time savings were measured.
The whole CPU artifact took 5.89 seconds including plotting. It is not the cost
of simulator probes.

Evidence: [report](/home/linjiw/lucid-sonic/analysis/ternary_probe_synthetic_20260906_a/report.md),
[results](/home/linjiw/lucid-sonic/analysis/ternary_probe_synthetic_20260906_a/results.json),
[PNG](/home/linjiw/lucid-sonic/analysis/ternary_probe_synthetic_20260906_a/calibration.png),
[PDF](/home/linjiw/lucid-sonic/analysis/ternary_probe_synthetic_20260906_a/calibration.pdf),
and [source/output receipt](/home/linjiw/lucid-sonic/analysis/ternary_probe_synthetic_20260906_a/receipt.json).

## Validation and remaining gate

- **35 focused tests passed**, including exact binomial miscoverage enumeration,
  boundary decisions, quality holds, abstention/caps, missing outcomes, invalid
  support, unique identities, immutable configuration, deterministic replay and
  preservation under unit conversion.
- **2,070 full CPU tests passed**, five warnings, 41.63 seconds.
  [CPU log](/home/linjiw/lucid-sonic/outputs/ternary_probe_cpu_20260906_a.log).
- Black and Ruff pass on all three additions; staged whitespace checks pass.
  Repository-wide `make run-checks` still encounters existing isort failures
  beginning in `motionbricks/` and the root isort/Ruff ordering conflict.
  [Check log](/home/linjiw/lucid-sonic/outputs/ternary_probe_run_checks_20260906_a.log).

Reproduce with a new output directory:

```bash
export LUCID_REPO=/home/linjiw/lucid-ternary-probe
source /home/linjiw/lucid/env/lucid_env.sh
python -m pytest tests/practice_utility/
python scripts/practice_utility/validate_ternary_probe.py \
  --output /home/linjiw/lucid-sonic/analysis/ternary_probe_reproduction \
  --repetitions 2000 --seed 20260906
```

At 06:20:13 UTC, fresh-history training was complete and restored history was at
1,087/2,000, with no supervisor warnings. All three supervisors/workers were alive;
collection and the retention screen were waiting for their prerequisites. The
[progress audit](/home/linjiw/lucid-sonic/analysis/icra_progress_audit_20260906_a/audit.json)
records a later timestamped status snapshot and verifies this calibration's hashes.

Next live gate: complete the existing retention experiment, validate component and
event integration, then freeze fresh-draw probe calibration with justified quality
inference and explicit dependence/failure handling. No learned utility estimator,
residual allocator, live adaptive probe or hardware deployment is enabled here.
