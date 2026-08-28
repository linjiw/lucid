Continue the LUCID research now with write access, autonomously and without asking questions. Apply the research-director guidance already present in this session and in `/home/linjiw/lucid/lucid_next_experiment_guidance_2026-08-28.md`.

First inspect the current live campaign and all newly landed receipts. Do not stop, duplicate, overwrite, or invalidate any running Stage 7/8/queued evaluation. If GPU work is active, work only on safe CPU-side analysis, tests, preregistration, and implementation until the campaign reaches the appropriate gate.

Your immediate priorities are:

1. Finish and audit the existing Stage 7/8 results before interpreting them. Clearly label all existing three-seed work as screening-grade.
2. Implement a deterministic, receipt-backed Gate-A learnability diagnostic that identifies the hardest non-saturated informative bin and tests whether equal-budget direct mixed training already learns it. Do not use 60 ms latency as a ranking bin.
3. Implement and test the expanding-support sampler safeguards: a preregistered 10–20% easy-bin probability floor, lagged/frozen error weighting, per-bin sample-count and effective-sample-size accounting, fail-closed active-bin coverage checks, deterministic resume, and receipt fields.
4. Implement per-bin reward/value scaling or PopArt-style normalization only behind an ablatable flag, with numerical identity/no-op tests. Do not silently alter existing baselines.
5. Construct and preregister a compute-efficient screening matrix followed by a five-training-seed confirmatory matrix. Include settled origin, no-DR continuation, direct mixed, expanding support, expansion plus 30–50% final mixed consolidation, error-weighted expansion with the easy-bin floor, and latency-specific/per-channel LUCID. Add descriptor-conditioned variants only as clearly labeled oracle/deployable arms when scientifically valid.
6. Preserve equal environment-step, PPO-update, rollout-size, and evaluation budgets across comparisons; record both environment-step and optimizer-step axes where necessary.
7. Add fixed held-out stratified evaluation, per-bin/worst-bin metrics, success-vs-difficulty and retention curves, hierarchical uncertainty, held-out motion families, and non-saturated OOD bins. Keep fresh-physics robustness distinct from motion generalization and deployment evidence.
8. Run focused CPU tests, lint/format checks, update the canonical research log and preregistrations, and commit coherent changes in the correct nested repository. Do not push unless the existing session already has explicit authorization.
9. Launch new GPU experiments only when their prerequisites and gates are frozen, resources are safe, no conflicting campaign is active, and the launch will not create invalid concurrency. Preserve negative results and stop branches whose preregistered gates fail.

Scientific stance: do not optimize for making curriculum win. If direct mixed training solves the hardest informative bin and retains clean performance, record that curriculum is unnecessary. Focus curriculum research on the latency axis only if the ladder provides a non-saturated learnable regime and the evidence supports it.

Proceed through the justified sequence, continuously distinguishing measurements, preregistered decisions, and interpretation. Leave durable receipts and a clear resume point.