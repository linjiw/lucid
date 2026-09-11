# LUCID research status — September 11, 2026

## Outcome and current gate

**BLOCKED:** new simulator work has no explicit current compute/time allowance. The user requests local inspection/tests followed by one bounded pilot budget when limits are missing. No new simulator or training process was launched. **NOT DEMONSTRATED:** durable unchanged-trajectory recovery, usable feedback benefit, multi-motion retention, the proposed retention-budget learner, and hardware transfer. This is not a negative feedback pilot.

Current gate: Phase 1 / D1, real recording-to-score validation. Do not repeat the historical audit on resume unless inputs change. Do not implement the utility estimator/residual allocator or jump to Phase 3. Full-method primary-literature review and confirmation remain downstream work, not completed by the existing prospectus.

## Completed this turn

- Read the August 20 handoff, current D1 implementation/recording notes, experiment design, scorer, adapter, aggregator, reporter, collector and selected native command/recorder code. Used the installed Xiao writing skill's reference copy because the workspace skill copy lacks its referenced files.
- Verified the executable component definitions: planar root distance (m), absolute height error (m), wrapped projected-heading error (rad), direct bounded-joint RMS (rad), and gravity-vector root tilt angle (rad). The adapter never recenters or retimes. Legacy temporary dwell success remains distinct from durable-v2. Source inspection is not live frame/clock validation.
- Reused the existing adapter/aggregator. Fixed numeric-overflow recording corruption aborting the entire report; it now remains an unresolved scheduled attempt. Invalid out-of-window/Boolean terminal ticks cannot fabricate known failure through the bad-file fallback. Independently evidenced valid failures remain F. Invalid frozen protocols fail before trial reporting. Added five regression cases.
- Fresh historical audit rehashed 135 metric panels and reaggregated 69,120 episode records. R1 nominal global drift is +4.33%/+6.46%; hard qualification gains +5.18/+7.71 pp. These are two continuation seeds from one origin and one recording, not recovery evidence. Generated the new evidence note from the audit output.
- Prepared a new nominal instrumentation plan without overwriting September 10 evidence. All 19 declared input/source bindings matched. The raw capture is still not ready-to-score truth until fixed registration, reference clock, motion joint permutation, terminal timing and disturbance readback are verified live.
- Corrected the prospectus title and durable endpoint wording. Preserved the deadline diagnostic manuscript separately. Verified official ICRA 2027 rules, including substantive AI disclosure; existing diagnostic disclosure identifies Codex GPT-6 and its drafting/code scope. No publication/submission performed.

## Commands and validation

The original `/data/robotixx/.../lucid_env.sh` is absent on this host; the handoff's host-independent script works:

```bash
source /home/linjiw/lucid/env/lucid_env.sh
python -m pytest tests/practice_utility/ -q
python -m pytest tests/practice_utility/test_task_recovery_metrics.py tests/practice_utility/test_task_trace_accounting.py -q
python -m isort --check-only scripts/practice_utility/report_task_recovery.py tests/practice_utility/test_task_trace_accounting.py
python -m black --check scripts/practice_utility/report_task_recovery.py tests/practice_utility/test_task_trace_accounting.py
python -m ruff check scripts/practice_utility/report_task_recovery.py tests/practice_utility/test_task_trace_accounting.py
python -m pytest /home/linjiw/lucid/tests/test_diagnostic_data.py -q
```

Full CPU suite: 1,915 passed, four existing warnings, 35.14 s after the logic change (baseline was 1,910 passed, 39.06 s). Focused measurement suite: 36 passed. Diagnostic-data suite: six passed. Import-only cleanup followed the full run; targeted checks were repeated. Default isort and Ruff disagree on interleaved `from dataclasses` imports; using an explicit module import satisfies both without changing repository configuration. Repository-wide whitespace check flags pre-existing generated SVG whitespace; those figures were not edited in this turn. No clean repository-wide formatting claim is made.

From `/home/linjiw/lucid`:

```bash
python3 tools/audit_task_preserving_evidence.py \
  --private-root /home/linjiw/lucid-sonic \
  --output /home/linjiw/lucid-sonic/outputs/research_resume_20260911_a/historical_audit.json
```

Initial shell attempts using unactivated `python` failed (not found); an initial test-log redirect also failed because the output directory did not yet exist. Corrected commands above completed; no experiment attempts were involved.

## Evidence locations and provenance

- Private audit and CPU log: `/home/linjiw/lucid-sonic/outputs/research_resume_20260911_a/{historical_audit.json,collection_preflight.json,cpu_tests.log}`.
- Prepared plan: `/home/linjiw/lucid-sonic/experiments/task_truth_collection_d1_20260911_a/collection_plan.json`; SHA256 `a868fd6cec33da94bda1265dd714902933094f982a09e2c84c97d649b0341da7`.
- SONIC HEAD: `22457bd14a6ee67543c998109dbf8d2691b7e7f2`, with pre-existing dirty/untracked research files and this turn's reporter/test edits. No commit created. Plan hashes bind the collector extensions; HEAD alone does not identify the dirty source.
- New generated evidence note: `paper/task-preserving-recovery/evidence-continuation-2026-09-11.md`.
- Updated prospectus: `paper/task-preserving-recovery/manuscript-skeleton.md`.
- Official rules check: `paper/icra-rules-check-2026-09-11.md`.
- Existing September 10 trace inventory is reported prior evidence, not re-scanned this turn: 39 traces/1,864,448 rows lacking the new raw schema. No complete real recovery recording is certified.

## Remaining budget, blocker and exact next action

Authorized new experiment budget: unspecified; used this turn: **0 GPU experiment-hours**. Request one capped development campaign: **4 cumulative GPU process-hours / 8 elapsed hours**, with staged gates and finite invocation/iteration limits in `paper/task-preserving-recovery/pilot-budget-2026-09-11.md`. This is a request, not approval. The smallest user action is to authorize that budget or supply a smaller explicit cap.

After approval: recheck GPU free memory (9,208 MiB observed, below the inherited 11,000 MiB gate), verify the prepared plan bindings, and execute the exact 15-minute-capped collection command in the budget note. Do not kill unrelated GPU processes. If unavailable, wait only within the elapsed cap and report resource-blocked. Account for interrupted attempts and preserve their files. Verify online W&B in `16726/lucid-sonic`; the prepared nominal callback uses the explicitly noted September 10 instrumentation group. No new online run exists yet.

Then validate native raw truth against the actual motion-library joint permutation and unchanged reference clock/world offset, finish the thin source-to-score conversion for this real capture, and collect the bounded scheduled nonzero event. Freeze development protocol/competence before Z/O/N training. Stop infrastructure work once those gates pass. If competence or instrumentation fails, report that bounded failure rather than training from an incapable origin. If the matched pilot reaches its cap without resolving feedback benefit, report NOT DEMONSTRATED with the attempted-run ledger and keep the diagnostic paper scope.
