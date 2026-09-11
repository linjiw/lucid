# LUCID feedback design: measurement before curriculum claims

Development specification, September 11, 2026. This extends the [one-motion restart](lucid-latent-feedback-single-motion-2026-09-11.md). All method advantages below are hypotheses. Historical manuscript numbers are not evidence for this implementation.

## Decision and scientific question

Test one motion, `walk_hands_on_back_loop_002__A066_M`, in SONIC. First establish nominal competence and trustworthy measurements; then compare feedback under isolated push and action-delay conditions; finally compare curricula under matched training budgets. Do not expand the motion set because a training curve looks favorable.

The contribution to test is **whether temporal execution information changes useful curriculum decisions beyond equally calibrated task and filtered-joint feedback**. Adaptive DR itself is established: [DORAEMON](https://arxiv.org/html/2311.01885v2) increases distribution entropy under a success constraint. Our proposed change is the measured information used to regulate exposure under transient disturbances. A two-coordinate threshold teacher is an experimental vehicle, not yet a novel or superior algorithm.

## What belongs in the latent signal?

Keep the learned execution representation narrow. Feed it time-aligned physical joint targets and measured joint positions, with velocities as a separately ablated channel. Preserve joint identity, temporal ordering and command amplitude. Use frozen normalization, a validity mask and timestamps. Reference phase and contact context condition calibration; they must not grant access to future perturbations. Compare reference-only pretraining against nominal command/execution pretraining because policy targets need not resemble reference trajectories.

Do not force all teacher information through this embedding. The teacher needs four distinct inputs:

1. **Execution deviation:** calibrated latent discrepancy, its persistence and causal change; filtered physical discrepancy supplies the matched alternative.
2. **Task competence:** completion at intended timing, reference tracking, base orientation and nominal retention. A low discrepancy cannot certify balance or successful motion.
3. **Recovery and effort:** independently measured return to task bands, torque saturation and action oscillation. Legitimate effort can increase PD error; suppressing all high-frequency variation can hide instability.
4. **Evidence quality and exposure:** valid episode counts, missing measurements, phase coverage, realized condition exposure and measurement age. Unknown evidence cannot authorize expansion.

The essential design principle is to separate **what deviation occurred**, **whether it harmed the task**, and **whether the current policy can learn at that exposure**. Present discrepancy does not establish marginal practice utility. This proposal does not implement the gated utility estimator or residual allocator.

### Candidate discrepancy

For a causal window ending at control time t, retain both issued-target/execution and applied-target/execution diagnostics. The first includes transport effects; the second helps diagnose actuator response. Never substitute one for the other without renaming the measurement. A nominal phase-conditioned residual in feature space is a candidate:

\[
r_t = E_c(w^{issued}_t)-E_x(w^{measured}_t),\qquad
d_t = \|S_b^{-1}(r_t-m_b)\|_2 / \sqrt{d_z}.
\]

Here m_b is the nominal median residual vector in phase bin b and S_b is a diagonal robust scale fitted only on nominal development episodes. A nonzero nominal PD residual is retained in m_b rather than declared a failure. Separate adapters E_c and E_x are optional learned variants; the first comparator uses the existing shared frozen encoder. This expression is a proposed alternative to cosine distance, not a calibrated probability or a stability margin. Check feature collapse and norm loss explicitly.

Fit normalization on equal episode contributions. Choose each scale floor in physical or feature units on development data. Sparse phase bins return unavailable measurements. Track the fraction and maximum duration of threshold exceedances as separate summaries; do not hide persistence inside an unexplained weighted scalar. Initial window candidates remain 0.10/0.20/0.40 seconds. Resolve their exact control-step counts before freezing them.

Use paired nuisance and consequence tests: isolated sensor spikes versus sustained phase lag, persistent bias, amplitude distortion and oscillation associated with independently measured tracking loss. A corruption is not harmless merely because it is high frequency. If training supervised failure prediction, distinguish that model from unsupervised discrepancy and provide supervised nonlatent baselines with the same labels.

## A transparent curriculum for timed push and delay

Index conditions by c=(push level, delay level, temporal process). Keep amplitude, event frequency, burst duration and composition separate. Increasing all simultaneously makes attribution impossible. Random onset is present from the first nonzero exposure, so the learner cannot rely on a deterministic countdown. Begin with isolated channels; add joint conditions only after both have a nonzero competence region.

At each fixed teacher interval, gather complete episode statistics per condition and update a small table. Alternate the next candidate axis deterministically to avoid introducing an unvalidated learned allocator. Sample nominal episodes, attained conditions and one adjacent frontier condition using the same mixture in every feedback arm. The initial 25/50/25 mixture is a development candidate and includes probe cost.

For candidate c, define an expansion permission only when:

\[
A_c = V_c \land (L_c^{track}\ge p_{min})
\land (L^{nominal}\ge p_{retain})
\land (U_c^{exceed}\le \rho_{max}).
\]

V_c requires sufficient independent episodes, valid windows and minimum dwell since the last change. L denotes a prespecified lower confidence bound on tracking-qualified completion; U is an upper bound on the episode-level frequency of persistent signal exceedance. Set confidence levels, episode counts, thresholds and dwell using development data before comparative training. These intervals are descriptive decision rules: repeated looks do not create a formal sequential guarantee. For outcome-only control omit the last clause; for filtered and latent controls change only its signal. Both receive identical task checks, tuning budget and causal data.

An allowed update increases only the selected coordinate by one grid step. Otherwise hold. Sustained nominal degradation reduces frontier sampling mass and increases nominal rehearsal according to a frozen rule. Keep replay of previously attained conditions and log actual exposure. Attained support is historical bookkeeping, not proof that the current policy still masters it. This teacher has no integral windup; PI is a later controller ablation.

Two failure cases matter. A low latent score with poor tracking must block expansion. A high latent score with good tracking may indicate either impending degradation or legitimate effort; the second case can make a latent veto harmful. The matched outcome-only arm is necessary to detect this cost. A representation that predicts falls yet consistently delays useful practice has failed the curriculum hypothesis.

## Latency is a process, not just a maximum

[Random-delay RL](https://arxiv.org/abs/2010.02966) and [state augmentation under stochastic delays](https://arxiv.org/abs/2108.07555) motivate specifying the action/observation interface and memory. More recent [model-based work on random observation delay](https://arxiv.org/abs/2509.20869) studies a different algorithmic route. These papers do not establish that a curriculum can overcome missing actor information. If the SONIC observation history is insufficient, a matched history ablation is a separate policy intervention, not evidence for a better teacher.

For action transport, freeze one queue convention: at physics time t apply the newest arrived command; discard stale arrivals rather than applying older commands after newer ones. Record issue, arrival and application times plus dropped command IDs. This is a proposed transport process and must not be silently conflated with selecting an older entry from a delay buffer. The existing actuator-group delay remains a separate legacy baseline until transport semantics are implemented and audited.

Freeze development, validation and test event tapes independently, indexed by episode identity. Tapes specify onset, direction, severity and duration without relying on the number of previous resets. Delay bursts and push events can coincide only in explicitly declared composition cells. Evaluation distinguishes new random draws from new temporal processes and magnitudes beyond training support. Event timestamps are evaluator metadata, never advance notice to the actor.

## Claim–evidence map

| Claim to test | Essential comparator | Measurement and independent unit | Current evidence |
|---|---|---|---|
| Learned representation adds useful information | Causal filtered mismatch, dense tracking; PCA/random features | Pre-failure PR and lead time; checkpoint-disjoint episodes, uncertainty clustered by checkpoint | Not measured under the new protocol |
| Feedback improves adaptation | Same teacher, origin, guard, reward, compute; change signal only | Fixed-panel tracking and recovery; independent training seeds | Not measured |
| Adaptation must respond to the learner | Schedule replay from another seed | Held-out performance with paired event tapes; training seeds | Not measured |
| Stronger DR expands capability without losing motion | Tuned fixed DR and open-loop schedule | Per-condition qualified completion and nominal retention | Not measured |
| Gains extend to unpredictable disturbances | Frozen temporal-process and magnitude holdouts | Unconditional success, event-reached counts, recovery censoring | Not measured |

For signal scoring, split whole trajectories/checkpoints before extracting overlapping windows. Evaluate alarms strictly before failure; report false alarms per episode/time and lead time. Do not use future event labels as inputs. For recovery, predeclare task bands, dwell and horizon; falls count as failures and observation-horizon endings are censored. Padded latent scores remain failure-penalized composites and cannot validate the signal independently.

## Implementation audit and current execution

The existing observer samples one tracked environment, not an equal-environment population. Its p90 is therefore a temporal statistic of that trajectory, not population risk. It reads `joint_pos_target` after the SONIC wrapper step. Applied-versus-issued interpretation still needs a live value audit. Terminal state can already have been reset at that point.

This continuation fixes two concrete defects in the research observer: clear the window on the tracked environment's done flag even on unsampled steps, and clone CPU samples so later in-place writes cannot alter history. Reset steps are omitted from command/execution windows. This avoids cross-episode gaps but does not capture pre-reset terminal state; the separate native task-truth seam remains necessary for terminal analysis. Historical results are not regenerated or repaired retroactively.

Attempt `latent_feedback_smoke_20260911_b` has an unfinished receipt and no live training process at inspection. Its last console block reports 30,720 timesteps, with no final capsule. Preserve it as an interrupted/incomplete attempt. Attempt `_c` restarts the same nominal diagnostic from the common input checkpoint with the observer fix, a fresh output directory, source hashes and native online W&B. This is a pipeline run, not a matched curriculum experiment or nominal-retention proof.

The smoke completed 32 iterations and 98,304 transitions in 74.25 seconds including simulator startup/export. The [online run](https://wandb.ai/16726/lucid-sonic/runs/lf-68e8abfb1b028e27) is verified finished. Checkpoint SHA256 is `71c0b59d634a4bb157f9d57ddef108e2767c0392135e0f4f34a7459e85b2baf8`; exact command, source/input hashes and metrics are under `/home/linjiw/lucid-sonic/experiments/latent_feedback_smoke_20260911_c/receipt.json` and its neighboring plan. The complete CPU suite passes: **1,924 tests**, four warnings. Repository-wide `make run-checks` fails on existing import-format issues across many files, including unchanged imports in the observer; the new regression test passes Black/isort checks. No repository-wide formatting was applied to the research workspace.

Installed-source audit further resolves the command field: Isaac Lab's articulation passes `data.joint_pos_target` into each actuator and writes the returned delayed position into `_joint_pos_target_sim`; the SONIC delayed actuator replaces the action's positions with its delay-buffer output. Thus the observer reads the issued target in this implementation. This is a source-level finding, not yet a live timestamp/value audit across resets and physics substeps.

Remaining executable gates: nominal tracking/retention, live command timestamps and terminal capture, then the isolated perturbation panel. No multi-motion expansion or latent-superiority claim is justified yet.

### Nominal validation result: reject the smoke checkpoint for continuation

The paired development panel uses 128 aliases of the same motion and evaluation seed 8711, with no added physics randomization or delay. Aliases are repeated executions, not distinct motions or independent training seeds. Both frozen checkpoints were evaluated to the panel horizon.

| Checkpoint | Completion | Mean normalized progress | Global MPJPE (mm) | Local MPJPE (mm) |
|---|---:|---:|---:|---:|
| Common origin | 128/128 (100%) | 1.0000 | 120.98 | 28.21 |
| Fresh-optimizer nominal +32 | 90/128 (70.31%) | 0.8755 | 201.10 | 30.94 |

All-execution errors are reported; these are not success-conditioned errors. Completion is the evaluator's termination-based outcome, not a separately calibrated tracking-qualified success measure. The global error worsened by 80.13 mm and completion fell by 29.69 percentage points. This one-seed diagnostic does not isolate optimizer state as the cause, but it rejects using this particular continuation as a retained nominal origin for harder DR. No post-hoc significance or prespecified tolerance is claimed.

Online evaluations: [origin](https://wandb.ai/16726/lucid-sonic/runs/lf-eval-82f7382bf8bd), [nominal +32](https://wandb.ai/16726/lucid-sonic/runs/lf-eval-fe57c5ab99bd). The evaluation entry point directly invokes evaluation callbacks rather than the native training W&B callback, so an online receipt monitor wraps each evaluation and uploads available scalar metrics, hashes and runtime. Exact commands/plans/metrics are under `/home/linjiw/lucid-sonic/experiments/latent_feedback_nominal_eval_20260911_a/`; the consolidated receipt is `/home/linjiw/lucid-sonic/manifests/latent_feedback_nominal_retention_20260911.json`.

**Next experiment changes because of this result:** keep the competent common origin for frozen-policy signal measurements; use the existing protected-continuation/anchor recipe to test nominal retention before spending on feedback-arm training. Do not tune the latent encoder to conceal this failure, train the failed checkpoint harder, or scale to additional motions. The learner-retention and measurement gates precede the proposed teacher comparison.

## Proposed paper text

**LUCID: Latent Command–Execution Feedback for Domain Randomization in Humanoid Motion Tracking**

**Abstract draft without unverified results.** Domain randomization can expose humanoid tracking policies to timing errors and external disturbances, but the appropriate pace of exposure depends on the learner's current capability. We investigate temporal command–execution discrepancy as feedback for that decision. Because position error can generate useful torque and does not certify whole-body balance, we calibrate execution feedback against nominal behavior and retain independent motion-tracking checks. A transparent curriculum regulates push and action-delay exposure separately, rehearses attained conditions, and tests adjacent difficulty levels. Our evaluation is designed to isolate learned temporal features from causal filtering and dense task feedback using matched teacher rules and training budgets. The initial study uses one SONIC motion and separates unseen disturbance timing, unseen temporal composition, and out-of-range severity. [Insert measured signal-validation and curriculum results, uncertainty, and evidence paths after completion.] No transfer or collapse-prevention claim is made from a pipeline diagnostic.

**Introduction transition.** A curriculum teacher needs to distinguish challenging practice from exposure that destroys the task being learned. Episodic outcomes describe whether tracking succeeded, while command and measured-motion histories may reveal how execution deteriorated. Neither information source is sufficient by definition: a large PD discrepancy may reflect useful loading, and small joint error may coexist with loss of balance. We therefore test whether calibrated temporal execution features improve curriculum decisions when task competence and nominal retention are held fixed. The decisive comparison is with equally calibrated filtered joint feedback, since smoothing alone could explain an apparent latent advantage.
