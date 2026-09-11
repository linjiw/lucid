# September 11 evidence continuation

Status: recovery NOT DEMONSTRATED; simulator campaign BLOCKED pending a bounded resource budget.

Fresh read-only recomputation checked 135 metric panels and 69,120 episode records against frozen plan/metric hashes. Episode copies are not independent training seeds. The following table is generated from `historical_audit.json`; these historical qualification outcomes are not recovery measurements.

| Continuation seed | Arm | Nominal global error change (%) | Hard qualification gain (pp) | Historical retention gate |
|---|---|---:|---:|---|
| 8600 | R0 | 76.56 | 6.25 | Fail |
| 8600 | R1 | 4.33 | 5.18 | Pass |
| 8600 | R2 | 27.83 | 10.64 | Fail |
| 8601 | R0 | 60.58 | 5.86 | Fail |
| 8601 | R1 | 6.46 | 7.71 | Pass |

The defensible diagnostic scope is a mismatch between robustness/training indicators and tracking quality, plus measured effects of cached anchoring in a narrow continuation setting. These data do not establish durable task recovery, realistic sensing, multi-motion retention, a constrained-learning contribution, or hardware transfer. They are not a negative feedback pilot.

Source: `/home/linjiw/lucid-sonic/outputs/research_resume_20260911_a/historical_audit.json`.
Reproduction: `python3 tools/audit_task_preserving_evidence.py --private-root /home/linjiw/lucid-sonic --output /path/to/new/historical_audit.json`.
