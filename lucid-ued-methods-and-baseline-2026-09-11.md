# LUCID: protected baseline and environment-design curricula

September 11, 2026. Active execution and implementation note. This continues the [latent-feedback design](lucid-feedback-method-development-2026-09-11.md). The user requests a 2,000-epoch baseline followed by research, implementation and comparison of GACL, PAIRED and PLR ideas. Here an epoch means **one SONIC PPO iteration**, with 24 transitions per environment. Reaching iteration 2,000 is a budget endpoint, not proof of convergence.

> The 2,000-iteration training has finished. Evaluation recovery, timed-event auditing, and subsequent measured results are tracked in [the post-baseline note](lucid-ued-post-baseline-2026-09-11.md). The historical launch specification below remains unchanged.

## Baseline launch specification

Use the validated reference-anchored R1 fixed-practice recipe from the competent one-motion origin, with new continuation seed **8612**. Prior R1 results retained tracking over 2,000 iterations on seeds 8600 and 8601; the unanchored smoke failed retention. This justifies the recipe choice without claiming the new run will succeed.

- One motion: `walk_hands_on_back_loop_002__A066_M`.
- 1,024 environments × 24 steps × 2,000 iterations = **49,152,000 training transitions**.
- Fixed allocation: 768 environments in the original envelope and 256 in the same envelope with push scale 3×. This is protected fixed DR, not nominal-only training. Actuator-group delay remains the historical process; it is not shared transport bursts.
- Retain the original actor/reward/termination contract and the validated anchor buffer, beta 1, 256 anchor samples/update and native-precision forwards in physical batches of 128. Track extra anchor cost separately.
- Save at 250, 500, 1,000, 1,500 and 2,000 iterations. Evaluate the origin and all five snapshots on the five inherited conditions, 512 aliases each: **30 evaluation cells**, 15,360 episode aliases. Aliases are one motion, not extra motions or training seeds.
- [Native online W&B training](https://wandb.ai/16726/lucid-sonic/runs/ued-1fc8d3b06340c154); group `latent_ued_single_motion_20260911`, entity `16726`, project `lucid-sonic`.
- Frozen source worktree `/home/linjiw/lucid-latent-ued`, commit `a42dd61975222ac74eeb17cf3253aeaf8210b2a3`; source/input hashes in the plan. The baseline worktree remains unchanged while new methods are developed in the main SONIC research namespace.
- Plan `/home/linjiw/lucid-sonic/experiments/latent_ued_baseline_20260911_a/plan.json`, SHA256 `eb5148d7a1052cdc1d67140adfcec0c97d3b45718a66f99e54fda5a5b76631bb`. Receipt and `train_R1.log` are neighbors. Launch command is recorded in the neighboring driver launch JSON.

The frozen baseline uses its legacy observer for diagnostics only. Its latent p90 is not used to select practice or validate the new signal, and its historical window behavior is not treated as repaired evidence. The new observer reset fix remains in the main research checkout.

The isolated worktree passes **2,030 CPU tests**. The initial bare `pytest` invocation resolved editable-package imports from the main checkout and failed collection; `python -m pytest` from the isolated worktree resolves the intended modules and passes. No test failure was treated as a simulator result.

## What the requested sources contribute

**GACL.** A pretrained VAE represents tasks, a teacher uses task/performance context, an antagonist supplies regret, and reference sampling maintains domain relevance. The formal description permits history, but the reported experimental state is the most recent task/reward pair. This motivates separate last-pair and recurrent-history controls. Its task latent is not a command–execution discrepancy. The public repository currently exposes a README and figures, not an executable training implementation, so the present adaptation is reconstructed from the paper rather than presented as an upstream reproduction. [Paper, Section III and IV](https://arxiv.org/html/2508.02988v1), [repository](https://github.com/linjiw/GACL).

**PAIRED.** An environment adversary maximizes the antagonist–student return difference. The sampled surrogate uses maximum antagonist return minus mean protagonist return on the same environment. A trained antagonist provides an empirical solvability comparison; a frozen reference cannot silently replace it. Its minimax-regret result depends on equilibrium/best-response assumptions and is not a guarantee for finite SONIC training. [Paper, Section IV](https://arxiv.org/html/2012.02096v2).

**PLR.** Replay selects environments for fresh on-policy rollouts, rather than reusing old PPO transitions. Value-L1 priority is the mean absolute difference between GAE returns and value predictions, combined with staleness and unseen-level sampling. The released sampler includes policies for partial trajectories. Use raw value residuals, not normalized PPO advantages. [Paper](https://arxiv.org/html/2010.03934v3), [released sampler](https://github.com/facebookresearch/level-replay/blob/main/level_replay/level_sampler.py).

Our inference: the promising combination is a structured execution measurement inside a teacher that remembers exposure and competence, with reference rehearsal and a check against unsolvable tasks. These components can also conflict: large value error can reflect unpredictable noise; large latent discrepancy can reflect useful effort; regret can reflect a temporarily weak antagonist. None alone establishes learning potential.

## The proposed LUCID teacher interface

Separate three quantities instead of naming all of them “latent feedback”:

| Quantity | Contents | Role |
|---|---|---|
| Task descriptor | Push magnitude/direction, burst duration, delay process and an opaque event-tape ID | Describes what the teacher assigned; future event timing stays out of the actor and causal execution observer |
| Execution representation | Calibrated issued-command versus measured-motion windows, phase-conditioned discrepancy, persistence and slope | Candidate information about how execution degrades |
| Competence/context | Task completion and tracking, recovery, retained nominal performance, effort, score age, realized exposure, validity counts | Prevents discrepancy from standing in for task success or reliable evidence |

For a low-dimensional push/delay task bank, a task VAE is not needed to encode five or six explicit parameters. First test finite-bank teacher adapters. A learned decoder becomes a separate experiment only if waveform/task complexity makes compression useful. Do not claim that replacing GACL's VAE with a bank reproduces its whole method.

Use task/performance context from the previous completed measurement interval. Last-pair history is the closest initial GACL state adaptation; a recurrent teacher is an additional memory experiment. Feed the same task/competence/context channels to filtered-feedback and latent-feedback teachers, changing only execution features. Fit all calibration on development trajectories and freeze it. Missing latent windows are unavailable evidence, never zero discrepancy.

Keep a reference mixture for domain relevance and an independently specified nominal-retention constraint. Preserve previously attained conditions in replay, but remeasure their competence. Historical exposure does not prove current mastery. Antagonist and student must receive identical actor information and matched event tapes; only the teacher may access task parameters during training.

## Implemented components and their current limits

New modules live in `GR00T-WholeBodyControl/gear_sonic/research/practice_utility/`.

| Component | Implemented | Remaining before a performance claim |
|---|---|---|
| `condition_replay.py` | Value-L1 scoring, rank/staleness mixture, unseen sampling, private RNG/state restoration, signed PAIRED regret surrogate | Connect scores to correctly tagged SONIC episode/rollout segments; matched live replay training |
| `regret_teacher.py` | Stateless adversary, last-pair teacher, recurrent teacher, fixed reference sampling, actor/value loss with source mask | Train antagonist and student on identical tasks; integrate meta-training loop and budget accounting |
| `disturbance_tape.py` | Split-keyed immutable push/delay draws and scalar transport reference | Validate live physics delivery and episode accounting |
| `timed_tape_runtime.py` | Opt-in native physics-step target transport, reset handling, velocity-change pushes, event logs | Live no-op parity, applied-target/velocity readbacks and terminal trace audit |
| `timed_tape_eval_callback.py` | Frozen-policy evaluation using the new event process | Queued live instrumentation/feasibility panel |
| `baseline_retention.py` | All-episode summary and inherited empirical retention rule | Applied automatically after the baseline finishes its panel |

The new code is original implementation from the described algorithms. It does not install Procgen or the old PLR dependency stack into Isaac. The downloaded reference sampler remains outside Git under `/home/linjiw/lucid-sonic/references/level_replay_level_sampler.py`, SHA256 `e5e42e662296a4f093a228979cf5a842dcf9666d2707bb9e6953755fa4b00f75`. A non-tied, all-seen rank/staleness case matches the released sampler to absolute tolerance 1e-15. This checks one formula case, not full algorithm equivalence. Our stable tie order, private RNG and zero-staleness fallback are explicit implementation choices.

**Current validation:** main SONIC suite **1,946 passed**, four warnings. New tests cover exact replay RNG continuation, signed regret, source-masked teacher gradients, recurrent/last-pair information flow, independent event keys, scalar/batched queue agreement, partial reset isolation and zero-delay target/RNG parity in fake environments. The 14 added files pass Ruff and Black checks. These tests do not establish simulator or robot performance.

## Automatic follow-up after the baseline

`continue_ued_after_baseline.py` waits at most six hours, checks the completed receipt and frozen research-source hashes, then recomputes the inherited retention rule directly from per-episode records. Across both nominal and original-envelope conditions at all five snapshots, require global/local error no more than 10% above origin and completion no more than two percentage points below origin. This is an empirical fixed-panel decision, not a sequential confidence guarantee. It keeps every failed episode in the denominator.

If retention fails, save all results and stop escalation. If it passes, invoke `run_timed_tape_gate.py` at the fixed 2,000-iteration endpoint. The follow-up has 11 cells of 128 aliases: native nominal, zero-event runtime, then nine timed push/delay/composition cells. No-op comparison requires exact equality of selected completion, progress, global/local tracking metrics and failed IDs before perturbation cells run. It is metric parity, not a proof of complete trajectory identity.

The timed panel includes velocity increments of 0.5, 1.0 and 1.5 m/s; shared delay bursts of 20, 40 and 60 ms; and combinations. Onsets are keyed random draws between physics ticks 120 and 499; burst duration is 20–99 ticks at 200 Hz. These are development conditions. New draws and changed temporal processes are distinct from out-of-range magnitudes, and final-test seeds remain unchosen. Event logs retain resets and whether the push was reached. Recovery is not inferred from surviving an event.

The transport convention is explicit: reissue the held target every physics tick, apply the newest arrived packet, and discard older late arrivals. During native actuator writes the queued target is supplied temporarily, then the issued target is restored for observers. This convention differs from a control-rate FIFO and from historical independently delayed actuator groups. The callback requires zero background DR and zero legacy delay to isolate it. Live readback validation remains necessary.

The supervisors do not depend on this chat staying open. The baseline launches its complete evaluation grid; the follow-up stops on failed retention or no-op parity. They do **not** automatically start unvalidated learned-teacher comparisons.

Follow-up supervisor is now launched from an isolated source snapshot at `/home/linjiw/lucid-ued-tape-gate`, PID `79446`. Its state is `/home/linjiw/lucid-sonic/experiments/latent_ued_followup_20260911_a/state.json`; exact launch arguments are in the neighboring `_launch.json`. The snapshot freezes 472 Python/YAML/test files and passes the 22 focused new tests. The main checkout can continue evolving without changing this queued experiment. Baseline supervisor PID is `63730`; use current receipt/process state rather than treating these historical PIDs as permanently live.

### Minimal signal experiment

The first teacher observation should concatenate a task descriptor, previous task return/qualified completion, a nominal-calibrated execution discrepancy and exceedance duration, nominal-retention measurements, realized exposure/measurement age, and validity masks. Root/task quality and effort stay separate from the learned execution vector. Add command velocity, contact context, inferred transport age and recurrent history one at a time where measured confounds justify them.

Do not simply give larger replay weight to a larger latent gap. That can concentrate training on legitimate high-torque motion or irrecoverable states. Test two explicit uses instead: (a) a calibrated execution veto on expansion with an otherwise identical task-only teacher, and (b) execution features in a history-conditioned teacher that can learn when a gap was followed by recovery or deterioration. The second is not validated by the first. Keep a filtered-feature teacher identical in every other respect.

For stochastic push and delay, distinguish repeatable failure from irreducible event/action randomness. Use matched task tapes and several rollouts before interpreting antagonist regret; keep antagonist rollout count fixed because a maximum grows with the number of attempts. Report negative regret and both-fail cases. PLR value error is a candidate priority, not a certificate of epistemic uncertainty. A teacher that chooses the highest error can still overpractice noisy conditions.

## Matched method campaign after the delivery and calibration gates

1. Treat the completed baseline as a common frozen origin only after retention validation. Inspect fixed-distribution curves for a plateau; otherwise call it the 2,000-iteration baseline, not a converged policy. Do not pick the best checkpoint after seeing stress results.
2. Collect a new reference-anchor buffer at that origin. The existing anchor explicitly binds the old policy weights and cannot correctly be reused for a new endpoint. Validate native target replay and nominal continuation before comparative adaptation.
3. Freeze a finite training bank of disturbance tapes and disjoint validation/test banks. The replay unit is the complete disturbance process and seed, never only a motion ID. Specify how partial episodes are scored at PPO boundaries.
4. Compare protected uniform replay, PLR-value, finite PAIRED, finite GACL-last, GACL-last plus filtered execution feedback, and the same teacher plus latent execution feedback. Add recurrent history only after the last-pair comparison. Keep actor/reward/anchor, reference mixture, student budget, event support and evaluation panel fixed.
5. Give PAIRED/GACL a trained antagonist with the same actor information. Report student transitions and total student+antagonist+teacher/probe compute. A matching-student-budget comparison does not have matching total cost. Add a total-budget display or control to assess practical value.
6. Use the teacher's regret signal to propose tasks, and independent retention/measurement checks to admit expansion. Record veto frequency; excessive vetoes can reduce learning. Test whether latent information helps beyond value residual, task feedback and causal filtering.
7. Report fixed-panel tracking-qualified completion, observed tracking errors, event-reached counts, effort, realized exposure, worst-condition performance and validated recovery. Compare live feedback to a schedule transferred from another seed. Only then replicate and expand the motion set.

The user's request explicitly authorizes these named curriculum methods. This does not authorize building the separate counterfactual utility estimator or residual allocator behind their still-unmet gates. No method superiority, convergence, multi-motion generalization, sim-to-real transfer or hardware result is established by this continuation yet.
