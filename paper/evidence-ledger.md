# Internal evidence ledger — not submission material

## Appendix B. Evidence ledger (remove before submission)

| Section | Receipt |
|---|---|
| 4 | `receipts/analysis/lucid_return_inversion_20260901.json`, `lucid_p3_readout_20260901.json` |
| 5 | `receipts/analysis/lucid_phase0_analysis_20260901.json` (H_R2 decision), ratchet guard logs |
| 6 | `receipts/analysis/lucid_signal_audit_20260901.json`, `lucid_physical_signal_audit_20260902.json` |
| 7 | `receipts/analysis/lucid_channel_attribution_20260902.json` |
| 8 | `receipts/analysis/mujoco_sim2sim_20260902/`, `lucid_heldout_motion_20260901.json` |
| all | `receipts/analysis/lucid_draft_number_verification_20260902.json` — every number above re-checked against its receipt or the raw training trace |
| 9 | `receipts/analysis/lucid_why_no_curriculum_wins_20260903.json`, `lucid_nesting_calculus_20260903.json`, `lucid_actuator_screen_readout.json` |
| 10 | `receipts/analysis/lucid_progress_signal_audit_20260902.json` and `..._warmstart_20260902.json`; preregistration `lucid_practice_allocation_screen_preregistration_20260902.json`; training trace `artifacts/.../curriculum_comparison_ne1024_20260901_232720/seed_8600/gate_150/curriculum_*.jsonl` (the gate run itself; `lucid_gate_feasibility_20260901.json` is a replay proxy, not this run), preregistration `lucid_support_expansion_screen_preregistration_20260901.json` |


## September 7 additions and claim boundaries

- Continuation drift: `lucid-quality-frontier-pilot-results-2026-09-05.md`. Its legacy panel reports 128.57 → 324.50 mm, not the later retention panel's 127.93 mm origin. Do not combine denominators across protocols.
- R0/R1/R2: `/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_c/analysis/analysis.json` and `receipt.json`; first-episode metrics, 83 completed cells. Endpoint R1 +4.33%; all five checkpoint gates pass, not +4.33% at every checkpoint.
- Optimizer control: `lucid-optimizer-history-results-2026-09-06.md`. Drift in both branches rejects optimizer restoration as a sufficient explanation; it does not prove a PPO-gradient mechanism.
- Second continuation seed: `/home/linjiw/lucid-sonic/experiments/retention_second_seed_20260907_b/pilot/plan.json`, SHA256 `f2ca969140d232579c70c8127df2c6ee775cf00917f3667ce976d9a17afd3f86`. Pending. Same origin, fixed evaluation seed, 57 cells; never label independent origins.
- Path-input pilot: complete training and 16 evaluations, archived future work; sideways push endpoint fails 2/128. No calibrated recovery endpoint, no main-paper claim.

## Prohibited in the submission

No equivalence/noninferiority inference from a passed empirical tolerance rule. No unconditional curriculum superiority. No claim that nesting explains all null results, or that an instantaneous survival signal certifies fidelity. No multi-motion, recovery-observer, hardware, or new-R1 MuJoCo result. No separate supplementary PDF or identifying artifact paths in the anonymous manuscript.
