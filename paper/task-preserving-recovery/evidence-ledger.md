# Strength assessment and claim–evidence ledger

## Assessment

The strongest current finding is that all continuation endpoints have 100% nominal completion while their global motion errors differ substantially. R1 limits that drift under an explicit empirical gate on both continuation seeds. R1 is a feasible tradeoff, not dominance: unanchored R0 and lower-learning-rate R2 can obtain greater hard qualification while violating retention. This motivates budgeted adaptation without establishing a new optimization method.

The experimental unit for the continuation claim is a post-training run nested within **one trained origin and one short walking motion**. There are two continuation seeds, not independent origins. The 512 aliases per cell are repeated-motion rollouts. The manuscript, webpage, review, prior audit and rendered PDF describe these same runs.

Evidence labels below: **V** = newly checked code, binding or raw-record aggregation; **A** = newly recomputed from an existing aggregate rather than trajectories; **R** = reported in an inspected document/receipt, not independently reproduced in this pass; **P** = proposed/unmeasured. A V label on arithmetic does not validate the simulator or all physical instrumentation.

## Exact historical ledger

| ID and claim | Provenance and check | Result / unit | Scope, simpler alternative and falsifier |
|---|---|---|---|
| D1: completion conceals tracking drift | **V**: both frozen `pilot/plan.json` bindings; 135 `metrics_eval.json` hashes; `eval/qualified/episodes`, 512 unique aliases per cell; recompute episode means, completion and qualification | R0 nominal global +76.5599094232% (8600), +60.5816724142% (8601), with 100% nominal completion | One origin/M1. Not a unique cause. Falsifier: incorrect hash/mask, failure exclusion, or corrected raw errors eliminating the discrepancy. Simpler measurement: completion plus continuous errors. |
| D2: R1 passes empirical retention | **V**: evaluate both `phys_000` and `phys_100`, global/local error increases ≤10%, completion loss ≤2 percentage points, every sampled checkpoint 250/500/1000/1500/2000 | R1 passes 5/5 checks on each seed; R0 0/5 on both; R2 0/5 on seed 8600. Endpoint nominal R1 +4.3337288932% / +6.4628182166% | Gate is not a simultaneous confidence bound or optimizer constraint. Fixed anchor coefficient, cached states. Falsifier of empirical claim: any constituent fails; falsifier of broad preservation: failures on independent origins/motions. |
| D3: R1 improves hard qualification over origin | **V**: average two hard cells' episode qualification, requiring completion and inclusive 600/50 mm global/local means | Gain +5.17578125 and +7.71484375 percentage points; origin 42.7734375%, R1 endpoints 47.94921875% / 50.48828125% | Broad development thresholds; not recovery. R0 gains +6.25/+5.859375; R2 +10.64453125. Simpler alternative: accept a different tradeoff. Falsifier of useful method: tuned simpler protected policy matches or exceeds frontier. |
| D4: R1 margin can be small | **V**: worst over sampled protected condition/error components | Largest increase 7.3487883963% / 9.6682399615%; latter slack 0.3317600385 percentage points | A small positive empirical margin is not statistical certification. Falsifier of reliable budget attainment: repeated budget violations on new policies. |
| D5: shared origin, same anchor | **V**: both plans identify the same origin path and buffer SHA `3517adde…`; recorded origin identity `e7fe72a0…` | 83 first-campaign cells including R2; 57 second-campaign cells without R2; 135 total evaluation panels, 69,120 saved episodes | Model bytes not all rehashed here. R0 seed 8601 is reused from predecessor `_b`; follow each plan's `output`, not inferred `_c` paths. These are independent continuation random seeds conditional on a shared origin, not independent pretraining. |
| D6: no never-shrink superiority | **A**: `ratchet_confirmation_20260831/lucid_ratchet_confirmation_analysis.json`, `ratchet_vs_fixed.success_rate.frontier_auc.per_seed`; aggregate SHA rechecked | Paired differences −0.1627604167, +3.125, −1.171875 pp; mean +0.5967881944, sample SD 2.2468798946; one-sided t lower bound −3.1911242989 pp | Three training seeds. No superiority or statistical noninferiority. Fixed DR is the simpler comparator. Raw trajectories were not re-evaluated. A new matched study, not rhetoric, must establish any broader claim. |
| D7: return–robustness inversion / collapse | **R**: manuscript §3 and `receipts/analysis/lucid_return_inversion_20260901.json` | Reports 2/6 near-collapsed adaptive runs and Spearman −0.73 across 12 policies | This pass prioritizes retention reaggregation. Correlation does not identify policy versus distribution effects. Falsifier of proposed causal explanation: crossed fixed-policy/distribution evaluation fails to support it. |
| D8: constant anchoring is implemented, constrained optimization is not | **V**: `reference_anchor_trainer.py:58–83` adds `beta * penalty` to upstream loss; `qualified_pose.py` implements masked episode metrics | Static auxiliary action penalty; retention gate evaluated outside optimizer | Fixed-weight regularization is the actual current method. No cost advantages, protected rollout dual update or retention guarantee is established by these files. |
| D9: historical local MPJPE is not isolated articulation | **V**: `qualified_pose.py:54–59` subtracts each body's own root but does not yaw-align | Local error retains heading effects; global−local norms do not equal root displacement | Future component metrics need poses/heading or joint traces. Falsifier of a root-drift attribution: observed drift primarily articulation/phase after decomposition. |
| D10: tested actor cannot see isolated horizontal translation | **R**: observability note/receipt reports 6,144 translations. **V**: added `heading_path_error` uses synchronized oracle reference and robot root positions | Existing two-coordinate repair scales by 0.3 m; no estimator, age or validity input | Observation sensitivity is not closed-loop recovery evidence. Proprioceptive histories may still carry disturbance cues. Falsifier of information mechanism: oracle feedback adds no recovery under matched conditions. |
| D11: common-input pilot and delivered events | **R**: path audit receipt reports 2,047 pushes and preserved old columns. **V**: `path_practice_callback.py` logs velocity before/write argument after, reference step and motion ID; native recorder labels resets | Pilot has one released origin; its four-motion nominal analysis reports improvements, but does not establish complete nominal-and-original-envelope retention. Same-state parity passes are reported separately from two failed cross-process gates | Logging a write argument is not proof of realized post-physics impulse or hardware force. No frozen recovery protocol. A matched zero-feedback post-training arm could explain the apparent benefit. |
| D12: three-motion DR A/B | **R in this pass**: September 10 audit previously checked 196 final Isaac cell exits/files and MuJoCo summaries | Separate from continuation; one training seed; 3 training clips and 102 development motions | No multi-motion R1 replication. No online W&B run-name match was found in previous audit; logging remains unverified. A nominal-capable fixed-DR baseline may make a new curriculum unnecessary. |
| D13: recovery, multi-motion retention, hardware benefit | **P**: no completed calibrated claim-bearing evidence supplied | Unmeasured | Not inferred from final height, no-op parity, exports, or external papers. Falsifiers are defined in the experiment plan. |

## Audit boundaries and correction

Raw-record verification reads two campaign roots under `/home/linjiw/lucid-sonic/experiments/`: `retention_screen_campaign_20260906_c/pilot` and `retention_second_seed_20260907_c/pilot`. It follows the frozen plan's per-cell output paths, checks the receipt's metric SHA, then reconstructs completion, qualification, global/local means and all sampled retention gates. It verifies 512 identities, positive valid-sample counts and agreement with the stored qualification flags. It does **not** reconstruct the underlying body trajectories from those already-computed episode scalars, or establish paired physics streams after resets.

Reproduce with:

```bash
python3 tools/audit_task_preserving_evidence.py \
  --private-root /home/linjiw/lucid-sonic \
  --output /home/linjiw/lucid-sonic/outputs/methods_development_20260910/evidence-audit.json
```

**Rounding correction:** the second-seed hard gain is 7.71484375 pp, which rounds to **7.71 pp**. The earlier 7.72 pp equals subtraction of already-rounded percentages (50.49−42.77). Preserve the qualitative finding and correct future manuscript calculations from unrounded values. This is not new evidence of a different effect.

The raw error-time decomposition is unavailable in the inspected historical episode-record schema. Inspect any additional retained trajectories before declaring it impossible to recover elsewhere. New replay would be a new evaluation requiring its own protocol and authorization.

## Candidate claims and explicit falsifiers

| Candidate claim | Necessary result | Falsifier / simpler explanation |
|---|---|---|
| H1: useful estimated task feedback enables recovery | Estimated-feedback arm improves maintained-or-regained success over zero-feedback under equal protection and fixed DR | Only oracle helps; estimated-input gain vanishes with realistic age/bias/dropout; a simple outer loop matches it |
| H2: rollout constraints improve budget-controlled adaptation | Better held-out recovery at the same valid retention budgets, or fewer budget violations at comparable recovery and equal tuning cost | Fixed anchoring sweep, ordinary fine-tuning or established adapter reaches the same or better frontier |
| H3: benefit transfers across capable origins and recordings | Individual-origin effects and uncertainty support the prespecified meaningful gain on disjoint recordings | Gain depends on one origin, repeated source recording, permissive aggregate budget or selection leakage |
| H4: benefit survives uncertainty | Improvement on held-out sensing faults and dynamics combinations with unchanged reference | Improvement requires corrupted-oracle artifacts or disappears under realized estimator errors |
| H5: system improves physical task recovery | Declared hardware protocol with independent measurement and all interventions counted | Effect disappears with matched actuator limits, localization ground truth, or all-trial denominator |

Absence of precision is an inconclusive result, not evidence of equivalence. Failure to find superiority does not prove methods identical. A predeclared practical-equivalence margin and adequate precision would be needed for that stronger statement.
