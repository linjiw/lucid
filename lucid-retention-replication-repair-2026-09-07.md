# Replication execution repair and submission progress

September 7: R0 completed all 2,000 iterations, exited zero and passed the complete training validator. The original executor then failed while sending a nested integer-key dictionary to W&B. This was an orchestration/logging failure, not a failed training outcome. The original `_b` plan and failed receipt are unchanged.

The repair uses a new checkout `/home/linjiw/lucid-retention-logging-repair`, commit `a42dd61`. W&B summaries now normalize JSON object keys before publication. Only the already validated R0 logging-failure case can be reused, and its checkpoint, four snapshot checkpoints/capsules, configuration and recorded training artifacts are hash-checked. No R0 retraining, seed substitution, threshold change or extra method arm was introduced.

- R0 final checkpoint SHA256: `852c704d5c4ad189f3326fb53003e60caec2e50b43b569480782e6c8b2a849fb`.
- Continuation plan: `/home/linjiw/lucid-sonic/experiments/retention_second_seed_20260907_c/pilot/plan.json`.
- Plan SHA256: `57fbff80fbcd47f740f0e7bff9f7f84e7bef7892a92b50fd61396cb4ce7827cd`.
- [R1 W&B](https://wandb.ai/16726/lucid-sonic/runs/p4rvttfe), started September 7 11:08 UTC.
- Existing suite: 2,028 passed, five warnings. Focused replication suite including two new serialization regressions: eight passed. Ruff passed for the changed source/tests.
- The results watcher now targets `_c`; the full report remains pending until all 55 evaluation cells complete. The two completed training seeds remain continuations from one origin, not independently trained origins.

## Submission artifacts prepared while training runs

The reference identity audit covers the seventeen retained citations using primary landing pages/proceedings records. It corrects incomplete titles, distinguishes publication and preprint dates, removes an unused entry and closes numbering gaps. It is not a new full-text literature review.

An anonymous simulation video draft is prepared from existing replay footage and the paper figures: 75.72 seconds, 6,788,757 bytes, 1920×1080, 25 fps, no audio. It shows every original tile for eight displayed draws per condition, one policy panel at a time, without new simulator runs. The screen explicitly distinguishes these illustrations from the 32-draw quantitative panel and the historical policies from R0/R1/R2. The video receipt and source/output hashes live in `/home/linjiw/lucid-sonic/outputs/submission_video_20260907/receipt.json`.

The public PDF and video remain working drafts. Final results integration, full package review and submission are outstanding. No recovery-aware, multi-motion, observer or hardware experiment was added.
