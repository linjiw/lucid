# Immediate diagnostic revision — separate from the methods programme

The existing title remains **When Training Gets Easier: Range Collapse and Tracking Drift in Humanoid Robustness Training**. The working methods title is a research target, not a replacement claim for the same experiments.

## Corrections supported without new experiments

- The direct 135-panel raw-record audit reproduces the retention result and all five sampled checkpoint decisions for each arm/seed.
- Correct the second-seed hard-qualification gain from 7.72 to **7.71 percentage points** in future builds: 50.48828125−42.7734375=7.71484375. Rounded endpoints explain the earlier discrepancy.
- Keep one origin/one short motion/two continuation seeds explicit. Do not count a second source document or a different DR screen as replication.
- Describe the current loss as constant reference-action anchoring and the retention condition as an empirical selection gate. It is not an implemented constrained optimizer.
- Global/local MPJPE do not isolate translation, heading or articulation. Preserve their actual definitions and prefix masks; do not infer root error from norm subtraction.
- Preserve the exact tested scope of R2: lower, non-adaptive learning rate, one continuation seed. “Early stopping does not help” means none of the five saved checkpoints of these tested arms is feasible.
- The two cross-process path-input gates remain failed. A later same-input action comparison is a different gate; it does not erase them.
- Timed reference playback is available in SONIC in principle. The missing demonstrated hardware capability is localized pose feedback and a validated complete execution path, not the existence of a reference clock.

## Useful new evidence, requiring a separate authorized evaluation

1. Frozen-policy replay with root, heading, articulation and time traces can distinguish the physical source of error. First inventory retained trajectories; the inspected episode scalars cannot supply this decomposition.
2. A crossed matrix of fixed early/late policies evaluated under narrow/wide physical distributions can separate policy change from evaluation-distribution change. Freeze policies, reward/termination/horizon and draws; do not identify causality from correlation alone.
3. A competent independent origin or disjoint additional motions would address breadth more directly than more aliases of the same origin. It cannot be guaranteed to succeed or fit a deadline.

No new result is assumed here. Keep the prospective recovery programme outside the diagnostic Results section. Preserve historical receipts and report negative or inconclusive outcomes. The source manuscript’s one numeric rounding correction is local; public HTML/PDF remain the previously published version until a separately authorized rebuild/publication.
