# Distributional Latency Evaluation

## Scope

Audit whether the retained step-32 SONIC policies were actually trained with a
curriculum-scaled latency channel, then characterize frozen-policy performance
across preregistered latency distributions. The fixed 60 ms result is retained
only as an endpoint.

## Protocol

- Source training receipt: `curriculum_comparison_ne128_20260820_143058.json`.
- Policies remain frozen; checkpoints are hashed before and after evaluation.
- Discovery and confirmation motion panels are fixed before rollouts by an
  outcome-blind hash split of the 102-motion content-development panel.
- Discovery may locate candidate operating regions. Claims require the disjoint
  confirmation panel and fresh physics seeds; the final test split stays closed.
- Report the complete evaluation surface, including negative cells. Do not
  select only the condition in which LUCID ranks first.
- Primary outcomes: motion success and progress. MPJPE is secondary because
  early termination can make it deceptively small.

## Status

Training audit, discovery, and disjoint confirmation are complete. The audit receipt
`latency_curriculum_audit_20260820_231532.json` verifies all nine original arms.
The 66-run discovery receipt
`latency_distribution_discovery_ne32_20260820_232545.json` passed every live
mechanism and checkpoint-freeze check. Its outcome-blind 18-motion panel selected
one condition for holdout: nominal non-latency physics with a shared per-episode
uniform 0–60 ms delay. Nine confirmation runs completed on a disjoint
84-motion/63-content-group panel, all three checkpoint seeds, and fresh physics
seeds. Mean success/progress were 46.03/56.71% LUCID, 46.43/58.29% fixed, and
44.05/55.27% off. LUCID beat fixed in only one seed, so directional replication
failed. The analysis receipt is
`latency_distribution_analysis_20260821_042612.json`.

The source audit also corrected the method description: historical training
sampled five actuator-group lags independently and held them until each
environment reset. It did not train on a shared transport lag or within-episode
jitter. Aggregate process telemetry and both shared and independent delay models
are now explicit.

## Decision

Reject a broad latency-robustness advantage for the retained LUCID checkpoints.
The evaluation was fair and mechanism-verified; the important correction is a
training-process mismatch, not evidence that SONIC evaluation suppresses LUCID.
Next, preregister equal-compute process-aware training with shared 0–60 ms support
and a curriculum over latency amplitude and resampling cadence.
