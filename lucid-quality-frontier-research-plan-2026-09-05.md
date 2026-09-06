# LUCID quality-frontier research and execution plan

Version 1, 2026-09-05. Companion [method design](lucid-quality-frontier-design-2026-09-05.md). The user authorized planning, implementation, and starting experiments. Work proceeds serially on the shared RTX 5080, without disturbing other jobs. This plan begins an investigation; it does not assert the proposed outcomes.

## Questions and evidence ladder

| Question | Hypothesis | Decisive comparison | What a negative result changes |
| --- | --- | --- | --- |
| R0: can quality be measured reliably? | First-episode pose measurement separates failure/reset artifacts from tracking loss | CPU synthetic resets plus matched frozen-policy legacy/new evaluator | Repair the instrument before training claims |
| R1: does online timing earn value? | Candidate feedback improves tracking-qualified robustness or decision cost across origins | Static per-stratum support allocation, frozen development replay, online box gate | Close timing in this setting if it ties at the planned resolution |
| R2: does quality feedback help? | An online quality veto preserves clean tracking while retaining useful expansion | Survival-only versus survival-plus-quality; same final thresholds | Quality is still an outcome, but this veto is not an effective method |
| R3: does dynamics information help? | A history-derived observer distinguishes recoverable difficulty and hidden dynamics | Raw/phase features, simple history, learned observer; later a policy × curriculum factorial | Retain simpler signal or attribute gains to adaptation rather than curriculum |
| R4: do gains transfer? | The surviving change helps unseen motions/processes and physical deployment | Frozen motion/process holdouts, second simulator, hardware | Scope claims to the tier that survives |

## E0: executable development pilot

Purpose: validate runtime replay, new per-episode tracking measurement, and the complete train–freeze–evaluate path. This is not a superiority confirmation. Seed 8600 is development, and all prior outcomes on this seed are known.

Source: frozen 2,000-row `box_fast_300_ng` trace from `curriculum_comparison_ne1024_20260903_024028`. Origin: its seed-8600 solved fixed-DR checkpoint. Preserve reference motion, policy/value initialization, optimizer configuration, 1,024 training environments, 12-step delay-buffer capacity, default termination thresholds, and per-stratum membership seed.

September 5 audit clarification: the original wording “optimizer” was imprecise. The configuration is preserved, while the executed contract starts fresh optimizer/scheduler state from the common policy/value checkpoint. The active loader keys restoration on top-level `resume`, which defaults to false, despite the saved `load_optimizer=True` setting. The [continuation audit](lucid-continuation-contract-audit-2026-09-05.md) documents this shared restart and its unresolved contribution to origin-relative drift. No frozen experiment was changed.

Three pilot arms:

1. `static`: fixed hard allocation at the componentwise maximum of all source per-stratum dispatch vectors. This covers the replay's marginal ranges at the same cohort density and tests whether scheduling is necessary. It may combine marginal extremes absent from the rotating replay; that distribution-shape difference is disclosed.
2. `replay`: canonical full-vector source schedule, without feedback.
3. `gate`: existing `box_fast_300_ng` law and cohort structure, with frontier/probe ceilings capped to the source trace's realized maxima. The adaptive arm cannot obtain larger marginal support than the frozen controls. This is a survival-only control; the quality veto is a later addition.

First run a 16-iteration smoke for all three arms. This only checks the paths, not efficacy. Save each cell's status as it runs; an interrupted cell cannot be silently restarted. Evaluate the frozen origin before launching the long pilot and evaluate every smoke checkpoint with its own resolved config. Keep original checkpoint/config hashes. A valid smoke requires exact iteration/dispatch counts, five delayed actuator groups, six scalable channels, finite outputs, exported checkpoint, and valid tracking records. Replay and static allocation require their intended per-stratum vectors; the gate requires monotone accepted frontiers.

After smoke, launch 2,000 iterations per arm from the same solved origin. This recreates the development contract with the new controls and evaluator. It tests feasibility and descriptive tradeoffs; same-seed replay is primarily a schedule/instrument check. The next cross-origin experiment is needed to establish adaptation of timing.

Evaluation panel: the existing frozen 512-alias hands-on-back replicate panel, evaluation seed 8700, no learning. Five initial cells: `phys_000`, `phys_100`, `ch_push_300`, `ch_push_350`, and `ch_push_fric_350_150`. All inherited event channels not widened in a marginal cell retain that preset's documented baseline; do not describe those cells as isolated clean-plant interventions. Push 3× already exceeds this pilot's realized source push support; Push 3.5× and its composition also exceed the historical 3× design ceiling. Wider uniform physics is secondary in subsequent confirmation.

Initial tracking thresholds: episode-mean global ≤600 mm and local ≤50 mm, frozen engineering screening choices. Failure always fails qualification. Completion, individual errors, and all per-replicate outcomes remain visible. The primary descriptive pilot endpoint is the mean tracking-qualified success over the two above-ceiling push cells. Clean and standard-DR completion retention margin is 2 points. Clean global/local legacy pose retention is ≤10% degradation relative to each compared frozen control. These are practical development rules, not statistical non-inferiority claims or hardware requirements.

Costs: historical 2,000-iteration continuation is roughly 1.5 GPU-hours, so three arms are projected at about 4.5 GPU-hours plus startup and evaluation. This is a projection to replace with the pilot receipt. Smoke and evaluation add costs. No simulator jobs run in parallel. A memory gate queues the process; it does not terminate other jobs.

## E1: prospective cross-origin timing study

After E0, freeze all choices and a new protocol before outcomes. At least three paired solved origins; choose fresh confirmation seeds if old seeds informed tuning. Use the same three arms and identical resources. A source schedule is fixed before the target seeds run. Record realized exposure, including candidate practice; a yoke from seed A is not automatically exposure-identical to adaptive seed B.

Choose one primary endpoint: held-out tracking-qualified gain at a fixed resource budget. A +5-point practical target is the initial planning effect, with final replication sized using E0 paired variation and available resources; three seeds alone do not establish precise population significance. Freeze a seed-level analysis and multiplicity plan. Cost-to-target is secondary unless explicitly selected as the primary before launch.

Add the full broad suite as a secondary endpoint with individual cells displayed. Require both clean completion and clean pose retention. Do not replace a failed macro by a favorable subset. An all-arm quality loss triggers method revision, not selective reporting.

## E2: quality-aware feedback

Build isolated fixed-condition clean probes and the quality-veto state machine only after R0. Account for probe episodes, simulator starts, and wall time identically in every arm. Define candidate evidence windows, quality references, missing-data behavior, sequential confidence/error control, and hold/retry semantics. Pending measurements hold expansion. A veto does not contract accepted support. Compare against E1's survival-only gate, frozen replay, and static allocation.

The cheapest first question is whether quality loss is detectable early enough to change an expansion decision. If affordable windows cannot resolve it, do not build a more complex online score. Consider longer scheduled blocks or a frozen conservative preset and price that alternative.

## E3: recovery and uncertainty

Gather action-aligned histories with motion phase, disturbance timestamps, per-episode identities, and actual dispatch versions. First compare raw pose error and phase/contact-conditioned features for prediction of recovery and future quality failure. Fit simple temporal predictors before a learned latent. Splits exclude held-out motions, origin seeds, policy stages, and temporal DR processes from fitting and tuning. Compare calibration and incremental prediction, not only training loss.

If the observer is useful, test its marginal scheduling value with the policy fixed. Only then consider an architecture factorial: existing/history-conditioned policy × fixed/curriculum training. Privileged dynamics is diagnostic training information. Learned utility selection and residual allocation remain subject to the original gates.

## E4: sim-to-real programme

Select at least three distinct motion families, including free-arm locomotion and a whole-body task, and freeze a family holdout. Acquire or locate synchronized G1 traces to estimate timing, actuator response, and contact priors; label the absence of hardware calibration explicitly. Test equal-marginal different-persistence delays and unseen push–contact compositions. Refine timestep/solver settings and evaluate a second simulator before interpreting a simulator-specific gain as physical robustness.

Physical work needs its own concrete robot/task protocol, calibrated deployment envelope, and trial plan. No hardware run is part of E0. Report independent motion/session conditions, interventions, failures, completion, pose, and available physical measurements. Simulator episode count does not substitute for hardware replication.

## Implementation milestones and stop rules

| Milestone | Deliverable | Exit condition |
| --- | --- | --- |
| P0 | Full design, frozen pilot plan, isolated checkout | Explicit scope, origins, thresholds, resources, and source hashes |
| P1 | Vector replay runtime and tracking instrument | Focused and full CPU suite pass; legacy paths retained |
| P2 | Frozen-origin and three-arm integration smoke | Complete valid receipts, no identity/measurement defects |
| P3 | Development pilot train/evaluation | Every planned cell accounted for, including failures |
| P4 | Cross-origin preregistration | Parameters and seed-level inference frozen before new outcomes |
| P5 | Quality feedback / observer | Each added signal clears its preceding measurement gate |

Any import-path mismatch, schedule mismatch, wrong checkpoint config, invalid denominator, or non-finite observation invalidates the cell. Preserve its receipt and repair under a new cell identity. A negative scientific result does not invalidate the cell. An unexpected quality cost is reported and guides the next stage; it cannot be hidden by renaming the endpoint.

## Execution ledger

September 5 evening decision preparation: the completed E0 pilot fails origin-relative clean tracking retention in all arms, so the fixed-initial-cohort diagnostic precedes E1/E2. Its supplemental report will assess the frozen 2-point completion and 10% global/local pose margins at every saved clean checkpoint. Endpoint recovery cannot erase an earlier sampled breach. Undefined ratios or missing evidence cannot certify retention. This is a development diagnostic, with no statistical non-inferiority claim and no inference about unobserved intervals.

If the initial distribution retains quality throughout the evaluated grid, proceed toward a measured origin-relative expansion veto. If a breach occurs without expansion, isolate the restart/training-retention mechanism before claiming that a richer difficulty signal solves the problem. The [continuation audit](lucid-continuation-contract-audit-2026-09-05.md) specifies the candidate optimizer-history control. No contingent GPU experiment is automatically launched from this classification. Recovery history and dynamics uncertainty remain subsequent prediction-gated signals; original utility-selector gates remain unchanged.

Initial implementation and test results, immutable pilot paths, launch identifiers, and completion status are recorded in `lucid-quality-frontier-status-2026-09-05.md`. Generated experimental material remains outside Git. The original practice-allocation confirmation memo and its frozen decisions remain authoritative for that experiment.
