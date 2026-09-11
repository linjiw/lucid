# LUCID: Task-Preserving Disturbance Recovery for Humanoid Motion Tracking

**Research-development package, September 10, 2026. Target title; proposed method, not a completed methods paper. Local work only.**

The current evidence establishes an important failure of completion-only evaluation and a bounded preservation result. It does not yet establish a distinct, broadly effective recovery algorithm. The central uncertainty is whether rollout-level retention constraints provide useful recovery beyond equally tuned action anchoring and feedback-enabled adaptation.

My recommendation is to pursue that question, conditional on a competent multi-motion origin and a successful realistic-feedback ablation. The immediate algorithmic novelty case is weak: the proposed architecture and optimizer are established ingredients. A defensible methods/system contribution would be a reproducible improvement in the recovery–retention frontier, or more reliable attainment of specified budgets at equal resources, in the unchanged-trajectory task. If tuned fixed anchoring or a simple outer loop matches that frontier, the stronger algorithmic claim should be abandoned.

The public overview, manuscript, September 10 review, rendered HTML and PDF are overlapping accounts. They are not five experimental replications. The DR screen, path-input pilot and historical continuation are separate cohorts.

Read in order:

1. [Strength assessment and claim–evidence ledger](evidence-ledger.md): includes the new raw-record audit and a rounding correction.
2. [Closest-work comparison and novelty boundary](closest-work.md): all ten requested papers, with method/appendix anchors and task compatibility.
3. [Exact task, objectives and proposed algorithm](formulation-and-algorithm.md): fixed reference, sustained recovery, failure-aware costs, consistent policy-gradient and dual updates.
4. [Staged experiments and decisions](experiment-plan.md): falsification, baselines, allocation of validation and computation.
5. [Working paper skeleton](manuscript-skeleton.md): draft abstract/introduction, figure/table plans, explicit unmeasured placeholders.
6. [Implementation dependencies](implementation-plan.md): audited existing seams, fixes, tests and deferred work.

[Immediate diagnostic revision](../diagnostic-revision-plan-2026-09-10.md) stays separate. The narrow existing result does not need a speculative new title to remain valuable.

## Work completed in this development pass

Read the primary methods and relevant appendices of CLOT, Any2Track, BeyondMimic, PPF, ResMimic, ASAP, StableMimic, Stubborn, SONIC and YAHMP. Checked code for anchoring, episode metrics, path inputs and event capture. Recomputed 135 panels containing 69,120 episode records; all associated metric hashes and the two plan bindings pass. This re-analysis does not regenerate trajectories or reproduce external papers.

The read-only auditor is `tools/audit_task_preserving_evidence.py`; its detailed output and downloaded primary sources are private at `/home/linjiw/lucid-sonic/outputs/methods_development_20260910/`. No simulator, training, hardware, publication or submission was launched. No utility estimator, allocator, recovery policy or constrained trainer was implemented. The algorithm below is a specification to test, not a relabeling of existing PPO.

Validation: the read-only auditor completed on the existing records; its Python syntax check passed. The existing diagnostic-data suite passed all six tests. These checks validate accounting and analysis contracts, not recovery performance or the proposed optimizer.

Follow-on implementation: [offline recovery scoring progress](implementation-progress-2026-09-10.md). D1 is partially implemented with synthetic CPU checks; physical measurement and recovery efficacy remain unverified.

Latest: [D1 recording-to-report audit](d1-recording-audit-2026-09-10.md), including durable restoration, scheduled accounting, raw-recording coverage and a prepared collection command. Actual recording validation and protocol calibration remain open.
