# Research-director guidance for the next LUCID experiments

Continue autonomously from the current LUCID research state. Do not ask me questions. First inspect the live unattended campaign and latest receipts/transcript. Do not interrupt, duplicate, or invalidate any running Stage 7/8 evaluation. Finish and audit in-flight preregistered work before launching new arms. Treat the following as hypotheses and experimental-design constraints, not as an assumption that curriculum must win.

## Core scientific premise

With PPO, “easy to hard” losing to direct mixed training is normal. Curriculum is only justified when the hard task cannot be learned from scratch or from the mixed distribution because reward is sparse or exploration stalls. If direct mixed training already learns the hardest non-saturated bin, curriculum may be solving a nonexistent problem while adding forgetting. A clean negative result is acceptable.

The first decision gate must therefore be: **How well does equal-budget direct mixed training perform in the hardest informative bin?** Do not use the saturated 60 ms endpoint as the only hardest bin; the current evidence says it is a floor for all policies. Use the planned 10/20/30/40/60 ms ladder and the existing DR profile to identify the hardest *non-saturated, rankable* bin outcome-blindly or from a frozen pilot rule.

## Immediate order of operations

1. Let the current Stage 7 and Stage 8 frozen-policy evaluations finish. Validate completeness, exit status, unique cells, checkpoint hashes, manifest lineage, and aggregation. Report origin/off/channel-specific/fixed/LUCID arms per preset and per seed before interpreting means.
2. Complete the 256-environment batch-size control and the latency ladder before designing a confirmatory curriculum comparison. These distinguish destructive small-batch PPO fine-tuning from harmful DR and locate a non-saturated latency regime.
3. Build a preregistered diagnostic comparing the settled origin, no-DR continuation, and **direct full mixed training** at equal total environment steps. Measure whether direct mixed reaches the hardest informative bin. If it does, explicitly downgrade or reject the need-for-curriculum hypothesis rather than tuning until curriculum wins.
4. Only if the gate supports curriculum, compare the designs below with identical origin, environment-step budget, optimizer budget, evaluation cadence, and seed set.

## Curriculum arms to test fairly

- **Direct mixed baseline:** sample the complete target training distribution from step 0.
- **Expanding-support curriculum:** sample uniformly over difficulty `[0, d_max]`; advance only `d_max`. Never discard easy bins.
- **Error-weighted expanding curriculum:** weight bins using frozen, lagged per-bin failure/error statistics while enforcing a **10–20% minimum aggregate probability for easy bins** so they cannot be sampled away. Freeze update cadence and smoothing before viewing outcomes.
- **Final-mixture consolidation:** reserve **30–50% of the total training budget** for the complete target mixed distribution. Curriculum starts the policy; it must not define the finish distribution.
- **Per-channel/latency-specific arm:** because current evidence points to latency as the destructive channel, test a gentle latency-only or per-channel schedule rather than forcing all DR dimensions through one scalar λ.

Do not add every arm at full scale immediately. Use a preregistered screening stage, then confirm only surviving hypotheses with adequate seeds. Preserve negative arms and receipts.

## Policy observability caveat

Test feeding a normalized difficulty/DR descriptor into the policy observation only if those variables are legitimately available or estimable at deployment. If exact simulator randomization parameters are privileged and unavailable on the real robot, label that arm privileged/oracle and do not use it for the main deployment claim. A deployable alternative may use observable history or an inferred context latent. Include a no-descriptor baseline.

## PPO controls

- Mixed difficulty creates different return scales. Prevent global advantage/value normalization from being dominated by hard bins. Implement and ablate per-bin reward/value scaling or PopArt-style normalization, with numerical and identity tests.
- Ensure each PPO batch contains enough samples from every active difficulty stratum. Use the 256-env control and log per-bin sample counts/effective sample size per update; fail closed if required bins are absent.
- At support-expansion transitions, lower learning rate according to a frozen schedule and preserve a nonzero entropy floor; compare against a matched no-transition baseline so this is not an extra-budget advantage.
- Keep all comparisons equal in total environment steps, number of PPO updates, rollout size, and evaluation calls. If rollout size necessarily differs, report both environment-step and optimizer-step axes.
- Plot and retain the entire learning curve, not only endpoints.

## Evaluation protocol

- Use a fixed held-out evaluation seed panel, stratified by difficulty. Report success for every bin, success-vs-difficulty curves, macro average, profile AUC, and worst-bin success. Do not collapse to one mean.
- Use **at least five training seeds for confirmatory claims**, with confidence intervals. A three-seed screen is allowed only if clearly labeled screening and followed by five-seed confirmation.
- Evaluate all difficulty bins periodically throughout training to produce retention/forgetting curves and expose the exact stage where easy-bin competence is lost.
- Add frozen OOD bins beyond the maximum training difficulty. This separates distribution fitting from genuine capability extension. Avoid physically meaningless or fully saturated OOD points.
- Keep the 102 in-pool motion panel labeled fresh-physics robustness, not motion generalization. Add held-out motion families/splits before claiming motion generalization.
- Replace or supplement `latency_60ms` with rankable ladder metrics; retain 60 ms as a failure-bound endpoint rather than a ranking endpoint.
- Use hierarchical uncertainty where appropriate (training seed, evaluation seed, motion family/context), not pseudo-replication over individual frames.

## Required experiment matrix and decision gates

Construct a compact, preregistered matrix containing at minimum:

1. settled origin (no fine-tuning),
2. no-DR continuation,
3. direct mixed,
4. expanding support,
5. expanding support plus final mixed consolidation,
6. error-weighted expansion plus easy-bin floor,
7. latency-specific/per-channel LUCID arm,
8. descriptor-conditioned oracle/deployable variants only if scientifically valid.

Use staged gates to control compute:

- **Gate A — learnability:** direct mixed must fail or materially underperform on the hardest informative bin for curriculum necessity to remain plausible.
- **Gate B — retention:** curriculum must not lose meaningful easy-bin/clean capability versus direct mixed and origin after consolidation.
- **Gate C — robustness:** improvement must appear in stratified held-out bins and worst-bin/profile metrics with uncertainty, not only training reward.
- **Gate D — capability extension:** confirmatory arm should improve at least one preregistered non-saturated OOD bin without unacceptable clean regression.

Freeze thresholds from the noise floor/pilot before confirmatory outcomes. Do not move gates post hoc. If a gate fails, record the negative conclusion and stop escalating that branch.

## Research integrity and execution

- Preserve current receipts, hashes, branch lineage, clean commits, and outcome-blind preregistration discipline.
- Add focused tests for samplers, easy-bin probability floors, bin coverage, normalization, transition schedules, resume determinism, receipt schemas, and aggregation.
- Never infer final results from training reward or incomplete cells.
- Do not claim real deployment from simulation. Explicitly separate fresh-physics robustness, held-out motion generalization, OOD physics extrapolation, and real-robot evidence.
- Monitor host RAM/swap. The ARDY CPU encoder currently consumes substantial memory; do not launch a high-host-memory LUCID stage if that creates OOM or timing-validity risk.
- Update the canonical LUCID research log with decisions, preregistrations, receipts, failures, and measured results. Commit coherent code/docs changes, but do not push unless already authorized by the existing session instructions.

Proceed now: audit the in-flight campaign, finish the current evaluations, implement only the next justified prerequisite, and continue the research according to these gates. At each stage, clearly distinguish measured evidence, preregistered decisions, and interpretation.