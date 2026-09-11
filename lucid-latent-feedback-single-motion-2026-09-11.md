# LUCID: single-motion latent-feedback research restart

Latest execution: [2,000-iteration protected baseline, requested GACL/PAIRED/PLR research, and conditional timed-disturbance evaluation](lucid-ued-methods-and-baseline-2026-09-11.md). Baseline training is running; method superiority remains unmeasured.

Status: development protocol and method hypothesis, September 11, 2026. The user explicitly requests returning to the original latent-feedback DR question and testing one SONIC motion before scaling. This supersedes the old direction preference, but does not erase its negative evidence or reopen the utility-estimator/residual-allocator gates. No new method superiority, recovery, hardware, or unseen-motion result is established here.

Continuation: [method specification and revised manuscript text](lucid-feedback-method-development-2026-09-11.md). The nominal `_c` pipeline diagnostic completed 32 iterations and 98,304 transitions; its [online training run](https://wandb.ai/16726/lucid-sonic/runs/lf-68e8abfb1b028e27) is verified finished. This is not latent-curriculum efficacy evidence. Independent nominal evaluation follows before stronger DR.

## Question and evidence boundary

**Does learned temporal command–execution feedback improve push-and-delay curriculum decisions beyond calibrated causal filtering and task feedback, while preserving motion tracking?**

The August 20 corrected SONIC study found full-range success of 54.25% for scalar LUCID versus 56.54% for fixed DR; the subsequent latency holdout did not replicate superiority. The September 10 review records useful protected-continuation results but no demonstrated latent-signal advantage. These local receipts constrain the new hypothesis. The simulation/hardware numbers transcribed in `lucid-original-paper.md` belong to the historical draft and are not verified results of this SONIC program.

Choose `walk_hands_on_back_loop_002__A066_M` first: it has an existing one-motion subset and previous nominal/retention measurements. This is a feasibility choice informed by prior development results, not a randomly selected representative motion. Aliases provide repeated episodes, never additional motions. Continue from the previously measured fixed checkpoint for a short pipeline diagnostic; the substantive comparison must use one common competent origin and identical optimizer/anchor treatment. From-scratch nominal acquisition and hard-DR adaptation are separate stages and costs.

## What the teacher should observe

Keep a structured feedback vector rather than summing everything into one uncalibrated latent distance.

| Component | Candidate contents and purpose | Confound/control |
|---|---|---|
| Temporal execution deviation | Issued physical PD targets, measured joint position/velocity; frozen temporal features of their causal windows | PD error generates legitimate torque; condition on reference phase/contact and nominal loading |
| Transport discrepancy | Issued versus actually applied target, command age, realized queue delay | Training-only diagnostics where applied targets are unavailable on hardware; do not subtract away the latency effect in the primary signal |
| Whole-body task state | Reference-relative orientation, root/local tracking, contact and foot-slip measurements | Joint agreement alone misses tipping or path drift; global path error may be teacher-only privileged information |
| Persistence and recovery | Recent level, causal slope, time above calibrated band, decay after an event | A brief impact may be harmless; sustained oscillation must not be denoised away |
| Control effort | Torque saturation, command rate and high-frequency power | Prevent low movement or low mismatch from masquerading as successful tracking |
| Measurement reliability | Valid-window mask, phase-bin calibration count, command source, missing channels and encoder support diagnostics | Missing data means unknown, not zero risk; representation support scores are not calibrated failure probabilities |
| Training context | Channel, severity, event timing, exposure count, policy checkpoint and nominal retention | Distinguish difficult but useful practice from irrecoverable overload; present difficulty is not practice utility |

Initial causal windows: compare 0.10, 0.20 and 0.40 seconds on development data, with timestamps in seconds and resolved control/physics steps. Use one fixed normalization learned only from nominal development episodes. For channel j and phase b, use `(x_j - median_nominal[b,j]) / max(1.4826*MAD_nominal[b,j], epsilon_j)`. Set each epsilon in its channel's units during calibration; numerical floors are not scientific noise floors. Sparse bins remain unavailable. Fit on episode-balanced samples so long survivors do not dominate. This phase adjustment is a candidate control for loading, not a proof that load confounding disappears.

The added `feedback_calibration.py` supplies robust phase normalization and an episode-reset causal EMA. It is offline infrastructure, not connected to training decisions. The existing observer's target source and exact post-step/reset ordering still require a value/timestamp audit before using its readings as aligned command–execution evidence.

Implementation audit: the current SONIC `latent_gap_probe.train_encoder` does reconstruct **clean** windows from corrupted inputs and uses a beta-weighted reconstruction/KL loss. This supports describing the current code as denoising, but does not establish the historical manuscript's actual implementation. The current pretraining script randomly partitions overlapping windows into train/holdout; that holdout is not an independent motion/checkpoint generalization test. New representation experiments must split trajectories before window extraction. Cosine latent distance also discards embedding magnitude, so retain norm diagnostics and compare a calibrated Euclidean alternative rather than assuming amplitude distortions survive the representation.

Representation experiment: preserve the old reference-only frozen encoder as a baseline. A proposed improved encoder uses nominal **command and execution** windows, paired under matching phase/contact, to reduce reference-to-command distribution shift. Compare separate command/execution input adapters with a shared temporal representation against the original shared encoder. Do not assume that necessary PD lag should be forced to zero. A denoising loss uses explicitly corrupted input and clean target; nuisance corruptions must exclude the sustained lag, bias and unstable oscillation the signal should detect. Predictive auxiliary heads for short-horizon execution can be tested later. A dynamics innovation can become small under a learned failure mode, so task checks remain separate. No learned utility estimator is authorized by this representation experiment.

## Teacher and randomization design

Use separate push and delay severity coordinates and a small grid of condition cells. An unknown future onset is part of the environment process; event labels and future queue contents never enter the actor or causal feedback. The simulator may log those labels for retrospective scoring.

Proposed transparent teacher: alternate channel probes, use a fixed nominal rehearsal fraction, retain exposure to previously mastered cells, and expand one coordinate only after sufficient episodes pass independent tracking/retention and calibrated signal checks. Use threshold hysteresis and minimum dwell first. A latent veto augments the same outcome/retention rule used by its filtered and task-only controls. Missing feedback holds expansion. A failed retention check reduces the frontier sampling mass and increases nominal rehearsal; it does not silently delete the attained support. Log realized exposure because a nonzero probability alone does not guarantee meaningful rehearsal. No claim that monotone support prevents policy collapse is made.

Development starting mixture: 25% nominal, 50% attained cells, 25% frontier probes; all fractions, dwell, episode count, signal thresholds and severity increments require calibration before comparative training. These are candidate hyperparameters, not a frozen winning recipe. Probe one axis at a time, then introduce compositions only after both isolated axes have a measurable nonzero success regime. Avoid an integral term until threshold scheduling is understood; later compare P and PI with explicit increase veto and saturation-aware integral handling.

| DR term | Training process to implement and audit | Held-out axis |
|---|---|---|
| Action transport delay | Shared FIFO; start with bounded episodic delay, then random within-episode bursts. Record requested/applied targets, age and queue policy. FIFO selection must not apply a future command; specify handling when delay decreases. | New onset seeds; new burst durations/autocorrelation; explicit out-of-range magnitudes |
| Observation latency | Separate timestamped observation buffer, initially disabled to isolate action delay | Later isolated and combined tests; keep reference-clock behavior explicit |
| Push | Initially planar root velocity increment in m/s, with randomized onset and direction; log exact event state change | New phase/direction combinations, paired push+delay, and larger increments |
| Physical force push | Later finite-duration external force with application point, duration and impulse in N·s | Different pulse shapes/durations at comparable impulse |

Do not call the velocity increment an impulse. A force pulse and a velocity jump are separate experiments. Do not infer effective latency from a configuration multiplier: audit live buffer capacity and sample/update rates. Candidate action-delay ladder is 0/10/20/40 ms with 60 ms outside the initial magnitude support; exact reachable steps must be checked on SONIC. Candidate planar push ladder is 0/0.25/0.5/0.75/1.0 m/s, extended only after competence. These pilot choices are not tuned to test results. Fixed 60 ms and episodic uniform 0–60 ms are different processes.

## Experiment sequence and automated research boundaries

1. **Pipeline diagnostic:** CPU contracts, short single-motion nominal continuation with native online W&B, checkpoint export, live command-source/latency audit. This is not an algorithm comparison and its fresh optimizer treatment cannot demonstrate retention.
2. **Measurement gate:** freeze origin; collect nominal and isolated perturbation sweeps containing successes and failures. Verify event onset/application, pre-reset terminal samples and window warmup. Use development episodes to freeze tracking bands, recovery dwell/horizon and feasible severity cells. If nominal competence fails, repair nominal acquisition first.
3. **Signal gate:** compare normalized raw error, causal EMA/robust error, dense tracking feedback, PCA, frozen random temporal features and learned latent discrepancy. Calibrate all on the same data/budget. Predict falls or tracking-band departure strictly before events with checkpoint-disjoint splits; report PR performance, lead time and sensitivity at matched false-alarm rate. Keep post-fall windows out. Stratify by phase, speed and contact/loading. An offline advantage permits testing feedback; it does not establish curriculum utility.
4. **Training pilot:** one development seed for matched fixed DR, open-loop ramp, task-only teacher, filtered-feedback teacher and latent-feedback teacher. Common actor, reward, origin, anchor, update frequency, guard and compute. Freeze each candidate's evaluation panel before training. Evaluate fixed-distribution tracking and recovery across checkpoints, not training return alone. No learned allocator.
5. **Attribution/confirmation:** replay another seed's schedule, guard-only/no-guard and threshold/P/PI controls where justified by the pilot. Replicate selected primary arms on independent training seeds; size confirmation from pilot variation. Count encoder pretraining, teacher probes, calibration and nominal acquisition, alongside PPO transitions and wall time.
6. **Final test:** freeze algorithm, hyperparameters and checkpoint-selection rule; evaluate once on new event seeds and held-out temporal compositions. Report every condition, not only an average. If test results drive changes, retire that test into development and create a new holdout.
7. **Scale gate:** require meaningful improvement against the strongest calibrated baseline on paired held-out perturbations, with uncertainty reported across training seeds and nominal quality within a prespecified retention tolerance. Until then remain on one motion. A tie favors the simpler signal. Multi-motion training then adds equal-motion aggregation and rare-motion worst-case checks; no unseen-motion claim from this pilot.

An automated loop may run only finite, frozen development candidates, stop on failed instrumentation/logging/nominal gates, retain all failures, and write one receipt per attempt. It must not repeatedly optimize the final test, increase budgets indefinitely, or replace independent validation with its own latent score. Current authorization covers simulator research; this plan launches no hardware experiment.

## Evaluation contract

Distinguish nominal, full training-eligible range, held-out temporal composition within magnitude support, and out-of-range magnitude stress. “Unpredictable” means onset/direction/process draws unavailable to the policy beforehand; it does not mean arbitrary unknown physics.

Use paired, pre-generated episode/event tapes indexed by episode identity and local clock. Resets must not consume another environment's RNG stream or shift the other arm's tape. Log events not reached because of early termination; keep those episodes in unconditional completion statistics and report event-reached counts separately. For each event, score return to predeclared task bands for a dwell within a fixed horizon. Falls are failures, horizon ends are right-censored, and an additional event before recovery is explicitly a compound event or censoring case fixed by protocol. Never claim recovery from terminal height alone.

Report completion, tracking-qualified completion, global and root-relative errors, recovery probability/time with censoring, effort/saturation and worst-condition performance. Global path recovery is limited by SONIC actor observability; teacher access to simulator position does not grant that information to the actor. Keep path recovery distinct from local pose/heading recovery. Show observed latent mismatch separately from survival, with valid counts and warmup marked missing. Any padded score is labeled failure-penalized composite.

## Primary-literature positioning (targeted research, not exhaustive novelty audit)

- [ADR](https://arxiv.org/abs/1910.07113) already adapts randomization. Use a faithful boundary implementation for a canonical comparison; label a scalar reward-threshold baseline ADR-inspired.
- [DORAEMON, ICLR 2024](https://arxiv.org/html/2311.01885v2) maximizes distribution entropy subject to success. Our proposed distinction is validating temporal execution feedback under timed disturbances with retained tracking, not constrained DR adaptation itself.
- [Reinforcement Learning with Random Delays](https://arxiv.org/abs/2010.02966) explicitly treats random action/observation delays. This motivates separating temporal processes; it does not validate our scheduler or justify importing an off-policy delay-correction algorithm into PPO.
- [CAPS](https://arxiv.org/abs/2012.06644) directly regularizes action smoothness. Measure action oscillation independently; a smooth embedding trace is not evidence of smooth actuator commands.

Reference audit: the supplied review's proposed BeyondMimic author-order correction does **not** match the [current arXiv v4 record](https://arxiv.org/abs/2508.08241), which lists Qiayuan Liao first, followed by Takara E. Truong, Xiaoyu Huang, Yuman Gao, Guy Tevet, Koushil Sreenath and C. Karen Liu. Preserve version-specific metadata rather than applying that correction blindly. The [VAE reference](https://arxiv.org/abs/1906.02691) confirms Diederik P. Kingma and Max Welling. Bibliographic recommendations in a review also require verification.

## Replacement manuscript opening (proposed-method text)

**LUCID: Latent Command–Execution Feedback for Domain Randomization in Humanoid Motion Tracking**

Domain randomization exposes humanoid policies to dynamics variation, but introducing strong disturbances can impair motion tracking before the policy learns to recover. We investigate whether temporal discrepancies between issued joint targets and measured motion provide useful feedback for scheduling that exposure. Such discrepancies are not intrinsically failures: position-controlled joints require error to generate torque, and contact transitions can produce legitimate transients. LUCID therefore treats learned command–execution discrepancy as an empirical measurement, conditioned on nominal motion phase and accompanied by independent task-retention checks.

Our central hypothesis is that temporal representations distinguish consequential, persistent execution deviations from benign variation more effectively than equally calibrated causal filters. We propose testing this hypothesis in SONIC on one motion under randomly timed pushes and action-delay bursts before expanding to multiple motions. Signal validation compares learned features with filtered joint error and dense tracking feedback; matched curriculum experiments then isolate whether any measurement advantage improves held-out disturbance performance. Improvements in latent score alone do not establish robustness, recovery or transfer.

Results remain to be inserted from the new frozen protocol. The original draft's hardware counts, uncertainty definitions, encoder objective, delay discretization, ADR identity and failure padding require a raw-record audit before reuse. Keep the historical source intact and link this replacement rather than silently rewriting its evidence.
