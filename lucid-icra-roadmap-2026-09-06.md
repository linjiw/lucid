# LUCID ICRA roadmap: retention first, calibrated feedback second

**Latest analysis, September 7, 01:06 UTC:** R1 remains the selected protected baseline from the completed 83-cell development screen. The four-cell contact diagnostic is complete. The separately preregistered eight-cell execution/retention parity campaign now passes all four pairs, covering 1,024 evaluation aliases and 380 aligned nonzero push events. Contact diagnostics remain unvalidated and the original all-metric gate remains failed. Recovery-band calibration and feedback efficacy are next. See the [research-direction update](lucid-research-direction-update-2026-09-07.md).


September 6, 2026. This incorporates the supplied Gemini guidance after checking the
current research notes and live campaign state. It supplements the
[retention-repair plan](lucid-retention-repair-plan-2026-09-06.md) and its
[execution contract](lucid-retention-screen-execution-2026-09-06.md). Frozen running
endpoints, comparison grids, and recipe-selection rules remain authoritative.

**Ideal-paper extension:** [LUCID: Recovery-Aware Curricula for Quality-Preserving Humanoid Robustness](lucid-ideal-paper-execution-plan-2026-09-06.md) incorporates the user's complete paper vision, adds the recovery-prediction and closed-loop signal-value gates, six-method/five-origin target design, total-cost arithmetic, and a quantitative hardware tier. It is the prospective paper plan; it does not replace frozen running endpoints. As of 17:59 UTC the complete smoke passed and campaign `_c` was training R0 at 1,729/2,000 iterations without warnings. The historical diagnostic framing below remains the evidence-backed fallback if the proposed method comparisons fail.

**Execution update:** the [complete history comparison](lucid-optimizer-history-results-2026-09-06.md) selects fresh history. The [target-precision repair](lucid-anchor-precision-repair-2026-09-06.md) closes the first screen's instrumentation failure and records the restarted smoke-gated campaign. Earlier “still running” entries below describe the roadmap's initial snapshot, not the current control status.

## Scientific framing and corrections to the supplied guidance

The defensible current thesis is that maintaining disturbance support and preserving
tracking competence are distinct requirements in humanoid policy continuation.
The existing evidence diagnoses failures; quality-preserving repair and incremental
feedback value remain hypotheses. A provisional diagnostic title is **Diagnosing
Frontier Drift in Humanoid Whole-Body Tracking**. Add “Quality-Constrained Domain
Randomization” to the method framing only when its behavioral benefit is measured.

| Proposed claim | Audited evidence and scope | Manuscript decision |
| --- | --- | --- |
| Return inversion accompanies curriculum evacuation | The [historical ledger](lucid-latest-report.md) reports 12 arms: Pearson −0.61 overall, −0.60 among controllers, Spearman −0.73. Highest returns belong to the two evacuating arms. | Name the statistic and 12-arm denominator. Do not label −0.73 as Pearson r. Never-shrink prevents support contraction by construction; it does not solve all tracking failure or establish superiority over fixed DR. |
| Completion can conceal tracking loss | The [frontier pilot](lucid-quality-frontier-pilot-results-2026-09-05.md) reports gate clean global error 324.50 versus origin 128.57 mm, with 100% completion; Push 3.5× qualification falls from 49.02% to 45.70%. | Describe survival–quality decoupling. “Cheating” is an interpretation, not a measured internal policy strategy. |
| Expansion is unnecessary for drift | [Fixed-initial continuation](lucid-initial-hold-results-2026-09-05.md) ends at +28.20% clean global error after nonmonotone sampled breaches. | State one origin, one motion, and the exact initial E0 mixture. It is not a reconstruction of the origin's training distribution. |
| Pelvis translation contributes to the failure | [Geometric bounds](lucid-root-feedback-findings-2026-09-05.md) imply gate-minus-origin mean pelvis error increases by at least 132.16 mm on the complete masked panels. | This is a lower bound on an increase, not directly measured absolute translation or a confidence interval. |
| Optimizer comparison identifies the cause | Fresh/restored 2,000-iteration control is still running at this amendment. | Neither outcome uniquely identifies momentum mismatch or proves PPO survival penalties dominate pose gradients. It isolates a moments-and-counters intervention under the pinned restart contract; exposure, coverage, incentives, and interactions remain alternatives. |
| Reference-policy anchoring repairs quality | R1 implementation is queued behind buffer and smoke gates; R0 ordinary and R2 conservative continuation are matched controls. | No repair result yet. The implemented mean-action squared loss is not a measured KL loss; learned variance and the native auxiliary objective matter. Preserve the frozen R1 rather than change it mid-campaign. |
| Push is the binding channel | Existing development ladders and practice studies motivate Push-focused practice. | Limit this to the tested checkpoints, channel definitions, budgets and process shapes. A sampled 3× ladder is not a universal physical tolerance certificate. |
| A brief G1 video establishes the paper | No new physical result was verified here. | A qualitative demonstration supports feasibility; comparative robustness needs a protocol, denominators and measured perturbations. No acceptance guarantee follows. |

For corresponding body positions, the exact vector identity is
`e_j = r + d_j`, where `r` is pelvis translation error and `d_j` is the
translation-only root-relative body error. Norm averages are not additive:
`abs(G - L) <= R <= G + L` on matching time/episode samples. Heading-aligned
articulation adds a distinct coordinate transformation. Retain global MPJPE and
report directly measured pelvis translation, heading, translation-only local error,
and heading-aligned articulation alongside it. The
[recovery measurement implementation](lucid-recovery-measurement-status-2026-09-06.md)
already passes analytical tests; live event timing and no-op parity remain gates.

## Immediate execution and decisions

1. Finish the 22-cell optimizer comparison and verified full-grid analysis. Preserve
   all five sampled clean stages, including earlier breaches. Apply the already
   recorded common-recipe selection rule; no partial-outcome selection or optimizer
   sweep. The current inner PPO KL-driven learning rates differ from checkpoint
   boundary rates. A new warm-down schedule would be a separate intervention;
   it is not implied by choosing fresh AdamW history.
2. Let the existing serial queue collect the origin buffer, verify teacher targets,
   and run native/R0/R1/R2 smoke. Only its passed contracts release the frozen
   three-arm, 2,000-iteration retention screen. Score every saved stage on all five
   conditions. Preserve clean and original-envelope completion and both errors,
   hard-condition qualification, actual rates, anchor work, transitions and wall time.
3. Select a useful repair only if hard-condition adaptation coexists with retained
   tracking. If R2 matches R1 at retained quality, prefer R2. If neither works,
   advance component measurement to diagnose the failure before selecting a new
   intervention. Do not tune a curriculum around a failing retention mechanism.
4. Prepare probe statistics offline now. After a viable repair and measurement
   validation, freeze fresh simulator calibration draws, the finite attempt/look
   budget, all quality conditions, failed-episode treatment and total error spending.
   Do not use existing scoring panels as fresh online evidence.

The new [offline ternary probe work](lucid-ternary-probe-status-2026-09-06.md)
implements a finite-look reference and synthetic calibration. Expand requires every
constraint to pass. Hold includes supported quality failure as well as supported
survival failure. Otherwise remain unresolved and request the next declared sample
increment; at the cap, unresolved remains unresolved. No automatic frontier
contraction follows either hold or unresolved.

The reference uses bounded-outcome Hoeffding intervals with error allocation across
all endpoints, looks and attempts. It exposes a remaining assumption: raw MPJPE
does not acquire a known population bound from observed extrema. Before live use,
justify a genuine support/moment contract or select and validate another inference
procedure. An explicitly bounded alternative changes the estimand and must be
reported beside raw errors; it cannot silently replace the retention endpoint.
Repeated-look coverage and row independence are separate from the choice of three
decision labels. [Howard et al.](https://arxiv.org/abs/1810.08240) provide the
established sequential-inference context; this code is a conservative finite-family
reference, not a new confidence-sequence method.

## Conditional three-week work sequence

These are completion gates and priorities, not a promised calendar or a verified
conference deadline. Re-estimate GPU time from observed current throughput and
complete evaluation/startup costs before each new campaign.

| Stage | Concrete deliverable | Advancement gate |
| --- | --- | --- |
| Week 1: close diagnosis and repair | Complete optimizer comparison; origin buffer; matched smoke; all R0/R1/R2 saved-stage results and retention–robustness plots. Draft the claim–evidence table and diagnostic results. | A common recipe and at least one useful retention-preserving repair; otherwise a documented negative result and a component-driven next hypothesis. |
| Week 2: validate measurement and feedback | Live component/event no-op audit, frozen development recovery bands, fresh-draw probe calibration including false expansion/hold, unresolved rate and measured cost. Freeze adaptive A versus protected fixed F and frozen schedule S. | Reliable measurement and a feasible probe budget. All arms share the same repair and count probe/anchor costs. A primary endpoint cannot be replaced by favorable cost-to-target after failure. |
| Week 3: replication and transfer tier | Complete matched comparison when feasible; independent-origin replication, at least two provenance-checked distinct motion families, final-checkpoint MuJoCo evaluation. Prepare a separate hardware protocol if simulator promotion gates pass. | Promote claims only to the completed tier. Do not compress remaining gates to fit the manuscript schedule. |

Seeds 8600–8602 have already influenced development. Report them as replication
with paired origin-level differences and mean ± sample SD; do not call 8601/8602
untouched final confirmation. Reserve genuinely fresh solved origins for final
confirmation before inspecting their outcomes. Many episode aliases improve
within-policy precision but do not increase the number of learned policies.

For motion transfer, inventory training/adaptation/probe/scoring membership and
file hashes before choosing at least two distinct motion families, such as turning
and squat/step behavior. Verify the frozen origin's ability on those motions first.
Separate zero-shot unseen-motion evaluation from training a new per-motion origin;
the latter tests replication across tasks. An unsolved origin cannot isolate loss
of retained competence. No final clip identities are asserted without that audit.

MuJoCo work must bind the final origin/F/A or repair checkpoints to exports and
validate observations, action scaling, history, delay/event process, solver/timestep
and metric frames. Gemini's “32-draw setup completed” statement is not completion
evidence for these future checkpoints. A draw count alone does not establish
precision. Keep simulator-specific outcomes separate and retain all failed draws.

Hardware is a later, separately reviewed physical protocol: qualified local operator,
deployment parity and timing checks, apparatus/perturbation measurement, retained
tracking criteria, stop conditions, and all attempted trials. A simulator velocity
increment is not automatically a calibrated physical impulse. No robot deployment
or physical push experiment is launched by this roadmap.

## Manuscript structure and strongest necessary comparison

Write the operational failure first: training return and completion can improve
while supported task difficulty or tracking fidelity degrades. Show the failure
taxonomy, evidence lineage and unsuccessful controls before proposing a repair.
Then report R1 against ordinary continuation and conservative R2, followed by A
against the strongest fixed allocation with the same repair. A frozen schedule
separates online feedback value from a useful development-derived schedule.

The minimum figures are the complete return/support diagnostic; time-ordered
retention–robustness trajectories with all sampled stages; direct translation,
heading and articulation measurements after live validation; calibrated probe
decision/error/cost curves; and the matched origin/motion-level result with transfer
tiers clearly marked. Keep historical and new metrics in adjacent labeled columns.

Constrained DR expansion and policy anchoring alone are insufficient novelty:
[DORAEMON](https://proceedings.iclr.cc/paper_files/paper/2024/file/56adf9cb91aedfa41ce24398782a012f-Paper-Conference.pdf)
already optimizes randomization breadth under a success constraint and discusses
policy KL as a possible forgetting remedy. The proposed contribution must therefore
be supported by the measured failure characterization and the incremental value of
retention/recovery feedback at its full cost. A strong diagnostic paper remains
possible if method superiority fails, with the negative comparisons visible.

**G1 implementation update:** [Native recovery event capture and paired audit](lucid-native-recovery-capture-status-2026-09-06.md) now pass 2,094 CPU tests. This advances the measurement gate while the retention campaign trains. It does not establish live recovery prediction or curriculum efficacy.
