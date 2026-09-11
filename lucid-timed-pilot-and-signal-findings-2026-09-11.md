# Timed replay pilot and execution-feedback findings

September 11, 2026. SONIC only; one motion, one continuation seed. This follows
[the eight-update integration study](lucid-explainable-timed-curriculum-2026-09-11.md).

## Question and frozen experiment

Does prioritizing fixed timed-disturbance conditions improve robustness beyond
uniform practice when both policies retain nominal rehearsal and reference
anchoring? Separately, does the existing frozen latent discrepancy carry more
useful execution information than causal filtering?

Both arms start from the original competent checkpoint and the same validated
anchor buffer. They train for 64 PPO updates, 256 environments, 24 steps per
rollout: **393,216 transitions per arm**. Sixty-four environments remain nominal;
192 sample the same 64-tape bank used in the smoke. Teacher behavior, actor,
reward, optimizer recipe and anchoring remain as documented previously. The
new collector reads 16 fixed environments: eight nominal and eight practice.
It supplies no inputs to either policy or teacher.

The frozen validation protocol uses seed 9130, 128 aliases per condition, and
origin/final-uniform/final-PLR policies under nominal, full-physics with zero
actuator delay, and timed 1.5 m/s planar velocity increment plus a 60 ms shared
burst. Retention uses the existing two-percentage-point completion-drop margin
and 10% global/local error margins in nominal and full-physics conditions.
Checkpoints are saved at 32 and 64; the final checkpoint is selected by budget,
not validation performance. The 32-update snapshot is archival in this panel.
These are development conditions. Untouched final testing remains closed.

Training source: clean frozen worktree `/home/linjiw/lucid-timed-pilot-20260911`,
commit `8590cb6`. Plan and receipts:
`/home/linjiw/lucid-sonic/experiments/timed_replay_pilot_20260911_a`.
Evaluation source uses the previously validated snapshot
`/home/linjiw/lucid-ued-eval-20260911b`; the standalone launcher is frozen at
`/home/linjiw/lucid-sonic/manifests/eval_timed_replay_pilot_20260911.py`.
Exact commands and hashes are in the respective plans.

Both training arms completed:
[uniform](https://wandb.ai/16726/lucid-sonic/runs/timed-a516c8961d3f8c67),
[PLR](https://wandb.ai/16726/lucid-sonic/runs/timed-a02bc4efbeae5688).
Each writes 64 execution-trace chunks containing 24,576 environment/time samples.
The native decision audit validates selections and policy-version bookkeeping.

## What is in the execution signal

Each trace sample records issued physical joint targets, the transport's applied
targets, measured joint positions/velocities, root orientation/velocity, native
reference joints/frame, episode identity, condition identity and physics time.
It is captured **before** the next action is applied. Command targets therefore
refer to the most recent physical write; measured state is current at the
control boundary. Reset samples are marked invalid, not filled with invented
measurements. Subsequent reward and termination are separate labels.

This distinction permits separate transport and execution diagnostics:
`issued - measured = (issued - applied) + (applied - measured)` in joint space.
Nonlinear latent distances do not have that additive identity. Temporal features
must be calibrated against phase and loading; ordinary PD effort can produce a
legitimate command-position gap.

The initial collector records `done` but not the timeout subtype. Consequently
these data **cannot** independently identify imminent physical failure. Native
reference frame is logged and advances as expected between ordinary steps, but
the reference-versus-physics timing convention still needs explicit validation
before treating joint error as an independent recovery measure. The next-source
collector now also records native timeout masks; it is CPU tested and was not
silently substituted into this frozen campaign.

## First signal finding: ordinary filtering remains a strong control

The frozen encoder is `lucid_encoder_debug512.pt`; the analysis records its
fingerprint and uses deterministic posterior means. Live joint columns are explicitly reordered to the encoder’s motion-file order. Initial unmapped analyses A–C are superseded for latent comparisons. It compares cosine latent
discrepancy with raw joint RMS, an episode-reset causal EMA (alpha 0.25), and
issued-to-applied target RMS. All features use identical valid causal windows.
Windows crossing episode resets or the held-out stage boundary are excluded.
Phase-wise median/MAD calibration uses only nominal samples from policy versions
0–31. Descriptive associations are measured on practice samples from versions
32–63. Phase calibration pools nominal windows; it is not equal-episode weighting.

| Phase-normalized Spearman association with current joint tracking error | Uniform traces | PLR traces |
|---|---:|---:|
| Raw command–execution RMS | 0.255 | 0.188 |
| Causal EMA of RMS | **0.311** | **0.286** |
| Frozen latent cosine discrepancy, corrected joint order | 0.236 | 0.247 |
| Issued–applied transport RMS | 0.083 | −0.041 |

There are 21,723 and 21,536 valid causal windows, including 5,367 and 5,264 held-out
practice windows, respectively. Overlapping windows are dependent; these counts
are not independent trials or evidence of statistical precision. The result
concerns association with current joint error, not future falls, causal training
utility, or whole-body recovery. It does **not** show the latent representation
is useless. It does show that this first diagnostic provides no reason to prefer
it over ordinary smoothing.

[Signal-analysis receipt](/home/linjiw/lucid-sonic/experiments/execution_signals_20260911_d/analysis.json),
[verified online analysis](https://wandb.ai/16726/lucid-sonic/runs/signals-f8e759dbf070de57).

## A better-defined curriculum hypothesis: separate severity from randomness

A relevant result in *Grounding Aleatoric Uncertainty for Unsupervised Environment
Design* is that curricula can change the distribution of hidden stochastic
parameters and thereby alter the objective for which the policy is optimal.
The paper formalizes curriculum-induced covariate shift and proposes SAMPLR to
address it under its assumptions. [NeurIPS 2022 paper](https://proceedings.neurips.cc/paper_files/paper/2022/file/d3e2d61af1e9612ddecd099144e50404-Paper-Conference.pdf).

Our inference is narrower: selecting one of only four fixed timing/direction
realizations per severity may favor specific event patterns, even when the goal
is tolerance of unpredictable disturbances. This is a hypothesis about the
current design, not an established explanation of the pilot result.

The next process comparison should factor the task into:

1. **Selected severity:** perturbation family, amplitude and latency magnitude.
2. **Fresh event realization:** onset, direction and burst duration, drawn from
   a fixed declared reference law independently of the selected severity ID.
3. **Observed evidence:** delivered dose, pre-event competence, observed task
   degradation, recovery and retained nominal/full-physics performance.

The new `factorized_conditions.py` adapter implements the first two identities:
severity never enters the key that draws event timing/direction. Equal
seed/environment/episode keys produce matched underlying draws despite different
severity choices. Calls for other environments do not advance this key's RNG.
Fresh episode IDs generate new realizations. These contracts have CPU tests;
this adapter is **not yet trained in SONIC** and is not an implementation of
SAMPLR. Its timing law is a chosen simulation reference, not measured deployment
truth. Different policies can have different reset histories, so matching keys
does not imply identical realized exposure counts.

The controlled comparison is exact-tape uniform/PLR versus severity-conditioned
uniform/PLR with fresh realizations. Compare the effect of factorization before
adding latent feedback. Estimate per-severity priorities from repeated fresh
realizations, report score age/count/dispersion, and preserve rare-condition
coverage. High critic error alone does not distinguish learnable weakness from
irreducible randomness. Latent versus filtered versus dense-task feedback should
then use the same process and calibration budget.

PLR also has important algorithmic variants. *Replay-Guided Adversarial Environment
Design* introduces a version that withholds policy updates on uncurated levels;
our current implementation learns from all native rollout transitions. Thus the
current negative/positive outcomes must not be generalized to all PLR variants.
[NeurIPS 2021 paper](https://arxiv.org/abs/2110.02439).

## Evidence still needed

Use independently defined non-timeout termination and recovery labels, with
future labels isolated from the online teacher features. Compare matched
false-alarm rates and lead time across held-out checkpoints; include motion
phase/loading controls. Validate qualified tracking rather than calling every
surviving episode successful imitation. Test duration, jitter and combined
perturbations on fixed validation panels, and only then confirm across training
seeds and unopened event/process tests. Reference anchoring and a fixed nominal
cohort are empirical protection mechanisms, not guarantees against forgetting.
The utility estimator and residual allocator remain gated.

## Completed validation

All nine cells completed (1,152 episode aliases), with online run verification.
The timed delivery audits pass; the full-physics cells verify zero actuator delay.

| Policy | Nominal completion | Full-physics completion | Timed combined-stress completion |
|---|---:|---:|---:|
| Origin | 128/128 | 128/128 | 89/128 (69.53%) |
| Uniform, +64 updates | 128/128 | 128/128 | 90/128 (70.31%) |
| PLR, +64 updates | 128/128 | 127/128 | 91/128 (71.09%) |

| Policy | Nominal global/local MPJPE (mm) | Full-physics global/local MPJPE (mm) |
|---|---:|---:|
| Origin | 118.14 / 28.31 | 198.06 / 32.35 |
| Uniform | 117.37 / 28.76 | 197.45 / 32.96 |
| PLR | 117.75 / 28.39 | 198.22 / 32.30 |

Both arms pass all six predefined completion/global/local retention checks.
Stress completion differs by only one episode between uniform and PLR; no
superiority claim follows. This seed is different from the eight-update smoke's
evaluation seed, so changes between those tables are not a learning curve.
64 updates do not establish convergence or a performance plateau.

The teacher plot shows substantial exposure reallocation: PLR assigns about
21.6% of practice episodes to 1.5 m/s pushes without delay and 23.3% to 1.5 m/s
plus 60 ms, versus roughly 5.3% and 7.0% under uniform sampling. Assignment
concentration therefore is not evidence of corresponding capability gains.
[Selection figure](/home/linjiw/lucid-sonic/experiments/timed_replay_pilot_analysis_20260911_a/condition_choices.png),
[full analysis](https://wandb.ai/16726/lucid-sonic/runs/timedanalysis-daefcacc7510).

Read-only collection has a useful live parity result: the first eight updates'
records match the previous smoke exactly after removing the new trace records—
2,474 records for uniform and 2,472 for PLR. This includes teacher states, event
records and scores, not merely rounded rewards. It supports the collector's
noninterference for that audited prefix, not a simulator-resume guarantee.

## Joint-order defect: discovery, correction and claim boundary

The first reconstruction diagnostic exposed an input-contract mismatch.
`pretrain_encoder.py` trains directly on each motion pickle's `dof` columns.
SONIC's native motion library then reorders those columns using
`mujoco_to_isaaclab_dof`. Robot buffers and the old observer provide Isaac-order
columns, which the old observer passed directly to the motion-file-trained
encoder. Sharing the same 29-dimensional shape is insufficient.

This is verified both from source and the collected reference trajectory:
reference-versus-linearly-resampled raw-motion RMS is 0.7997 rad without the
permutation and 0.000151 rad after the inverse permutation. The small residual
reflects the independently approximated resampling; it is not asserted bitwise
identity. A unit test round-trips all 29 joint impulse columns through the actual
upstream inverse mappings. Another verifies that the corrected observer reorders
both issued and measured streams.

Analyses A–C are retained and marked superseded for latent/reconstruction
comparisons locally and online. B was an identical diagnostic replay, not new
independent evidence. Analysis D performs the explicit conversion and records
the mapping/source hash. Raw RMS and EMA are invariant to a common permutation;
the corrected latent correlations in the table above are 0.236 and 0.247.

After correction, median reconstruction RMSE on nominal calibration windows is
approximately 0.409 rad for issued targets versus 0.087 rad for measured joints
(uniform); PLR gives 0.408 versus 0.086 rad. Before correction, measured-joint
reconstruction error was about 0.46 rad. This supports two distinct issues:
column-order mismatch corrupted the measurement, and PD targets remain less
well represented than measured motion even after that bug is corrected. High
reconstruction error alone is not a calibrated out-of-distribution test or a
proof that a latent feedback signal cannot work.

[Joint-order audit](/home/linjiw/lucid-sonic/experiments/execution_signals_20260911_d/joint_order_audit.json),
[corrected signal analysis](https://wandb.ai/16726/lucid-sonic/runs/signals-f8e759dbf070de57).

The observer now offers `encoder_input_order=g1_motion_file`, records its mapping,
and rejects incomplete permutations. The legacy default remains explicitly
labeled `legacy_unmapped` for reproduction; **new G1 latent-feedback experiments
must select the corrected mode and recalibrate thresholds**. The old latent
setpoint is not automatically valid after a coordinate correction. This path is
CPU-tested; corrected offline inference uses real captured trajectories. No
corrected latent-controlled robot-training result is claimed yet.

The uniform/PLR pilot does not use latent feedback and disables the observer;
its policy training, retention and robustness measurements are unaffected by this
encoder bug. Historical latent-based conclusions require a separate audit and
cannot be salvaged merely by correcting prose.

## Decision

Keep uniform as the matched control. The next discriminating framework test is
severity selection with fresh reference-law event realizations versus exact-tape
replay, with the same rehearsal/anchoring and fixed validation budget. For the
latent track, fix joint-order contracts first, test corrected latent versus EMA
and dense task feedback, and investigate conditional expected execution rather
than assuming PD targets occupy the reference-motion representation. Do not
scale to multiple motions or claim final-test robustness from this pilot.
