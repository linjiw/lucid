# LUCID root-position feedback: what the completed data establishes

Date: September 5 EDT / September 6 UTC. This secondary CPU analysis uses completed evaluations and leaves the running optimizer-history experiment unchanged.

## Finding

The earlier replay and survival-gate policies necessarily have larger **mean pelvis translation error** than the solved origin on their complete clean evaluation panels. The minimum increases allowed by the measured pose errors are **180.85 mm for replay** and **132.16 mm for gate**. This narrows the observed failure from an undifferentiated global tracking error to a demonstrable translation-error increase. It does not identify which training intervention caused that increase.

| Policy | Mean pelvis translation-error bounds | Target-minus-origin bounds |
| --- | ---: | ---: |
| Solved origin | 99.74–156.12 mm | Reference |
| Replay | 336.97–407.14 mm | +180.85 to +307.40 mm |
| Survival gate | 288.28–357.49 mm | +132.16 to +257.75 mm |
| Fixed initial DR, 2,000 iterations | 134.57–193.44 mm | −21.55 to +93.71 mm |

The fixed-initial bounds overlap the origin. Its translation change therefore remains unresolved from these aggregate measurements, even though its continuous global-error retention check fails. The intermediate fixed-initial checkpoints also have overlapping intervals. Static and the 250-iteration initial checkpoint each contain a failed clean episode; their full-motion comparisons are marked ineligible rather than computed from a selectively successful subset.

These are **geometric bounds**, not confidence intervals, an additive decomposition of MPJPE, or population estimates. In particular, global MPJPE minus root-relative MPJPE is not a measured pelvis error. The calculation uses the pre-step, first-episode records, whose absolute means differ slightly from the legacy MPJPE values in the frozen primary tables. Those primary tables remain unchanged.

## Derivation and body identity

At one time step let `r` be the executed-minus-reference pelvis position and `d_j` the corresponding body-position error after each pose's pelvis position is subtracted. Then each global body error is `e_j = r + d_j`. If `g` and `l` are the body-averaged norms of `e_j` and `d_j`, the triangle inequalities imply `|g-l| ≤ ||r|| ≤ g+l`. After averaging over the same episode's time samples, its means satisfy `|G-L| ≤ R ≤ G+L`. Averaging these per-episode lower/upper bounds yields bounds on the equally weighted panel mean.

The implemented qualified-pose instrument subtracts body zero without rotating either pose. The audited config lists `pelvis` first in `manager_env.commands.motion.body_names`; the motion command uses `find_bodies(..., preserve_order=True)`. The wrapper exposes those ordered body positions to the instrument. Consequently the bounds concern pelvis **position**, not heading. Root-relative position error still contains heading and articulation effects; it is not a joint-only or orientation-invariant error.

The comparison requires matching episode IDs and observation horizons, completed first episodes, finite nonnegative errors, and positive sample counts. Reversing the reference/executed sign does not change these norm bounds.

## Feedback-design implication

Keep task completion and continuous quality distinct, then split quality into directly measured components before fitting a latent signal:

1. Pelvis translation error, with horizontal and vertical components reported separately.
2. Pelvis heading/orientation error with an explicit quaternion/frame convention.
3. Body-position error after root translation subtraction, plus a separately defined orientation-aligned quantity if needed. The present local metric does not perform orientation alignment.
4. Disturbance-aligned recovery of those components, with episode identity, event time, and the DR assignment version attached. Error size alone does not say whether a condition is recoverable or whether more practice will help.

This is a specification for the next measurement extension, not an installed online controller. Direct measurements must reconcile with the geometric bounds in replayed frozen-policy evaluations before they can guide scheduling. Preserve the old qualification outcomes as a parity check, exclude all reset poses, and report failed episodes separately from full-motion quality means.

For eventual sim-to-real use, the available reference and state-estimation frames, alignment errors, and estimator uncertainty must be explicit. Privileged simulator state is useful for diagnosis but does not by itself provide a deployable feedback signal. A history model must show incremental prediction of component-specific recovery or retention loss beyond raw error, phase, and simple history before its latent enters curriculum decisions. No utility-estimator or residual-allocation gate is changed by this analysis.

## Implementation and validation

Checkout `/home/linjiw/lucid-root-error-bounds`, commit `9e3a63f`, adds `scripts/practice_utility/analyze_root_error_bounds.py` and ten passing focused tests. Tests include exact pure translation, random vector trajectories satisfying the inequalities, global error below local error, overlap that cannot certify an increase, failed episodes, horizon/identity mismatches, and invalid measurements. Black/Ruff and whitespace checks pass. The script verifies completed source-analysis input/output hashes and exports deterministic JSON/Markdown with source receipts and output hashes.

Results: [earlier frontier policies](/home/linjiw/lucid-sonic/analysis/frontier_root_bounds_20260905_a/report.md) and [fixed-initial checkpoints](/home/linjiw/lucid-sonic/analysis/initial_hold_root_bounds_20260905_a/report.md). No simulator job or new measurement was needed for these bounds. The paired optimizer-history GPU run remains under frozen commit `e981e97`.

Reproduction command, using a fresh output directory:

```bash
export LUCID_REPO=/home/linjiw/lucid-root-error-bounds
source /home/linjiw/lucid/env/lucid_env.sh
cd "$LUCID_REPO"
python scripts/practice_utility/analyze_root_error_bounds.py \
  --analysis-dir /home/linjiw/lucid-sonic/analysis/quality_frontier_origin_audit_20260905 \
  --output-dir /home/linjiw/lucid-sonic/analysis/frontier_root_bounds_reproduction
```
