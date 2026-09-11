# Implementation progress: offline recovery contract

Implemented the first part of D1 in the SONIC research namespace:
`gear_sonic/research/practice_utility/task_recovery_metrics.py`, with matching CPU tests.
This is an offline scorer, not a new recovery policy, estimator or simulator evaluation.

The scorer requires explicit five-component bands, integer event ticks, horizon,
dwell, sample interval and normalized error cap. It counts maintained and regained
trials, requires inclusive contiguous dwell, exposes later relapse, invalidates
success after a later physical failure/intervention/reset/reference alteration,
and conservatively pads fixed-horizon errors. Pre-event policy failure stays in
the denominator; missing live truth and undelivered disturbances are instrument
errors. Zero-disturbance controls have distinct output labels and must not be
pooled into disturbed success by a downstream aggregator.

The first concrete pre-event rule requires every recorded pre-event tick to be
in band. The reporting error cost equally weights the five components; it is not
the proposed complete training objective. No default robot tolerances were added.
Synthetic test bands have no experimental interpretation.

Fourteen synthetic contract cases initially passed. Changed files pass Black,
isort and Ruff. The complete `pytest tests/practice_utility/ -q` suite passed: **1,893 tests**, four existing deprecation warnings, 38.69 seconds. The workspace environment script selected the pinned Isaac Python and SONIC directory. No simulator job was launched.

Remaining D1 prerequisites: derive components from independently aligned poses
and joint traces; validate immutable recording/frame/clock identities; distinguish
terminal-pre-reset samples in a recorder adapter; build an all-scheduled-trial
aggregator that separates controls and invalid instruments. Caller-provided
failure and delivery fields are contracts, not proof that instrumentation works.
No historical scalar MPJPE panel can be converted into recovery using this scorer.

Simpler baseline: keep this offline scorer and reuse the existing recorder;
build a live evaluator only if recorded fields cannot meet the contract.
Falsification: a scorer that permits reset-spanning dwell, drops failed trials,
or rewards early termination cannot support the planned research claim.

No experiment, hardware action, publication or constrained optimization was launched.
