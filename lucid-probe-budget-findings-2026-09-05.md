# LUCID clean-probe budget: measured ambiguity and feedback implications

Date: September 5 EDT / September 6 UTC. This CPU analysis uses only the completed fixed-initial-DR diagnostic. It leaves the running optimizer-history experiment, its thresholds, and its frozen endpoints unchanged.

## Empirical finding

Small clean probes distinguish large observed losses more consistently than mild losses near the 10% retention margin. At the 500-iteration policy, full-panel global error is 14.12% above the origin; 70.8% of sampled 32-alias subsets exceed the margin. At 1,000 iterations, full-panel degradation is 9.80%; small subsets frequently exceed the margin anyway.

| Policy iteration | Full-panel global increase | Above-margin subsets at n=32 | At n=64 | At n=128 | At n=256 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 500 | 14.12% | 70.8% | 81.3% | 86.9% | 98.2% |
| 1,000 | 9.80% | 45.5% | 50.2% | 47.7% | 45.8% |
| 1,500 | 43.10% | 100.0% | 100.0% | 100.0% | 100.0% |
| 2,000 | 28.20% | 98.6% | 100.0% | 100.0% | 100.0% |

Each row uses 1,000 matched subset draws without replacement within each draw from the existing 512-alias panel. These fractions describe **observed subset variation**, not independent-rollout detection probabilities, population false-positive rates, or independent training replications. Shared alias IDs do not guarantee identical stochastic trajectories across policies.

At iteration 500, the global subset 5th/95th percentiles are 2.74–26.36% for 32 aliases, narrowing to 11.10–17.37% for 256. At iteration 1,000 even 256 aliases span 6.79–13.08%, straddling the margin. These quantiles are **not confidence intervals**. Using all 512 aliases removes variation from choosing subsets of this panel; it does not eliminate uncertainty about fresh simulator trials or other policies/motions.

The 250-iteration stage remains ineligible because one clean episode failed. Short-prefix means from that failure cannot certify full-motion pose retention. Its completion outcome remains in the source report rather than being dropped or silently converted to a success.

## Consequence for the proposed feedback method

The future quality decision needs a third state, **unresolved**, alongside evidence of retained quality and evidence of loss. Pending or unresolved evidence should not authorize expansion. A 32-episode point estimate cannot be assumed to provide reliable early warning near the demonstrated boundary. Larger probes may resolve some mild losses, but this analysis does not select a statistically calibrated budget or establish an online detector.

The next measurement design should therefore:

1. Freeze policy and retained-condition identity during a probe block. Keep completion and continuous global/local reference-relative error separate; maintain the current pre-reset first-episode accounting.
2. Compare a fixed probe budget with a prespecified staged budget. Treat 32→64→128→256 as candidate engineering budgets to validate on new data, not an already justified sequential rule. Price actual starts, rollouts, and wall time equally across curriculum arms. Offline subset size is not a measured simulator-cost saving, and running fewer environments need not reproduce a subset of a 512-environment evaluation.
3. Calibrate repeated-decision error control using an appropriate prospective protocol before activation. Existing subset quantiles cannot be relabeled as confidence bounds. Preserve indeterminate results and impose a finite probe budget rather than sampling until a favorable outcome appears.
4. Test persistence or hysteresis against the observed non-monotone trajectory. A single sampled recovery at iteration 1,000 does not establish stable recovery; requiring repeated evidence also has delay and cost that must be measured.
5. Address the retention mechanism first. The completed no-expansion run still drifts, so a quality veto alone cannot guarantee preservation. The running fresh/restored-history pair tests one candidate contributor. Recovery and dynamics-history features enter later only if they add predictive value beyond raw error, phase, and simple history.

This analysis prepares the measurement component of a curriculum, not a utility estimator or learned selector. Neither the one-motion dataset nor these uncertainty diagnostics establishes a robot's physical capacity boundary or sim-to-real transfer.

## Implementation and artifacts

Checkout `/home/linjiw/lucid-probe-budget`, commit `eb22174`, adds `scripts/practice_utility/analyze_probe_budget.py` and 11 passing focused tests. Black/Ruff and whitespace checks pass. The script verifies the completed source analysis's input/output hashes, preserves excluded stages, labels the full-panel census separately, and exports all 20 stage/budget rows. The running GPU checkout remains frozen at `e981e97`, whose full CPU suite passed 1,940 tests.

Artifacts: [table and interpretation](/home/linjiw/lucid-sonic/analysis/initial_hold_probe_budget_20260905_a/report.md), [plot PDF](/home/linjiw/lucid-sonic/analysis/initial_hold_probe_budget_20260905_a/probe_budget.pdf), [plot PNG](/home/linjiw/lucid-sonic/analysis/initial_hold_probe_budget_20260905_a/probe_budget.png), and [receipt](/home/linjiw/lucid-sonic/analysis/initial_hold_probe_budget_20260905_a/receipt.json). The plot was visually checked. Source analysis: `/home/linjiw/lucid-sonic/analysis/initial_hold_retention_20260905_a/`.

Reproduction, with a fresh output directory:

```bash
export LUCID_REPO=/home/linjiw/lucid-probe-budget
source /home/linjiw/lucid/env/lucid_env.sh
cd "$LUCID_REPO"
python scripts/practice_utility/analyze_probe_budget.py \
  --analysis-dir /home/linjiw/lucid-sonic/analysis/initial_hold_retention_20260905_a \
  --output-dir /home/linjiw/lucid-sonic/analysis/initial_hold_probe_budget_reproduction
```
