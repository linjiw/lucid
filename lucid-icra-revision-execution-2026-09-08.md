# ICRA revision execution — September 8, 2026

The September 8 user-supplied revision brief governs this work. The scientific basis is the current diagnostic manuscript, including the completed September 7 same-origin continuation replication. Existing unpublished workspace changes are preserved; pre-revision copies of the manuscript and builders are outside Git under `outputs/icra_revision_20260908/before` in the private data root.

## Frozen reporting addendum (existing records only)

This addendum is written before computing the new sensitivity and feasible-checkpoint summaries. It authorizes no simulation or training. It is a retrospective analysis plan, not a prospective experiment registration; the primary 600/50 mm outcomes were already known.

- Analyze every saved pilot evaluation from the first continuation campaign (seed 8600, R0/R1/R2) and completed repetition (seed 8601, R0/R1). Retain each campaign's own frozen-origin panel and every sampled iteration 250, 500, 1000, 1500, 2000.
- Protected conditions are `phys_000` and `phys_100`. Compute D as the maximum percentage increase over both global/local episode-mean errors and both conditions; L as the maximum completion loss in percentage points over both conditions. A checkpoint passes iff D <= 10 and L <= 2. Export every constituent measurement. Missing data is an error, never a pass.
- Hard qualification equally weights `ch_push_350` and `ch_push_fric_350_150`. Preserve the fixed 2000-iteration endpoint. Describe feasible earlier checkpoints separately; a maximum selected from this panel is exploratory, with no held-out deployment interpretation. Break exact ties by earliest iteration.
- Sensitivity grid: global thresholds {400, 500, 600, 700, 800} mm crossed with local thresholds {40, 45, 50, 55, 60} mm. Retain completion as a requirement and use the implementation's inclusive thresholds. Report all 25 cells for the origin and every sampled continuation checkpoint, plus continuous errors and completion. Do not select a new primary threshold.
- Treat rollout comparisons as unpaired unless alias-level perturbation draws establish stream identity. A numeric seed alone is insufficient. Pair historical policy differences by training seed only, without treating episodes as trained-policy replicates.
- Inventory existing saved trajectories for root translation, heading, articulation and time traces. Never infer root error by subtracting pose-error norms. A missing trajectory is reported as unavailable.
- The optional fixed-policy distribution decomposition remains unlaunched. First inventory whether saved evaluations contain the required policy/distribution/reward/horizon cells; any new evaluation requires a separate dated resource decision.

## Work and release gates

1. Reconcile arm/configuration census, endpoint precision, metric implementation, checkpoint lineage, and completed replication.
2. Export anonymous compact inputs with hashes; implement full retention, early-stopping and sensitivity analyses; replace machine-specific figure dependencies.
3. Rewrite the authoritative Markdown around two questions and measured controls. Regenerate HTML/TeX and figures through the builders.
4. Run focused numerical/provenance checks, rebuild in an isolated directory, compile and visually inspect every PDF page. Review the existing video and replace stale labels/results as necessary.
5. Reconcile evidence ledger, disclosure, source checks and submission checklist. Obtain actual IROS 1615 disposition, human scientific review, author approval and portal verification. Do not mark these completed without evidence.

## Initial verified status

- Both continuation campaign pilot receipts record completion (83 and 57 cells respectively); fresh episode-level recomputation is in progress.
- Repetition plan SHA256: `57fbff80fbcd47f740f0e7bff9f7f84e7bef7892a92b50fd61396cb4ce7827cd`.
- The collected-anchor validation records exact native CUDA replay of 2048 cached actions with 128-row physical batches. CPU and direct 256-row batch diagnostics differ and must not be represented as exact parity.
- No new experiment, external publication, or conference submission has been made in this revision.

## Completed revision and analysis

The work used existing records only. Source campaign commits are `2d4aa0aef89a078b00cc397b8b13f4809227a5c7` (first screen) and `a42dd61975222ac74eeb17cf3253aeaf8210b2a3` (repetition); the portable campaign metadata records both. The root reporting checkout starts from `ea6d16eac15a7f1145a263c67f175ca927194d4b`, with pre-existing unpublished changes and this uncommitted revision. Current SONIC HEAD is `22475f355485742fa211db1d1b4c8e5640ec3589`; no SONIC experiment implementation was changed or launched in this revision.

All 135 evaluation-panel hashes match their frozen receipts; 69,120 episode records reproduce the results. The complete screen and repetition are 83/57 cells, respectively. Online W&B states and URLs were checked read-only; the full inventory is `outputs/icra_revision_20260908/wandb_online_check.json` under the private root. The repetition's 57 repaired-plan runs are finished. Example verified run: https://wandb.ai/16726/lucid-sonic/runs/p4rvttfe . The old logging-failure run remains labelled failed; monitor/smoke runs are not experimental replicates.

| Continuation seed | Arm | Endpoint D (%) | Endpoint L (pp) | Hard qualification (%) | Sampled retention |
|---|---|---|---|---|---|
| 8600 | R0 | 76.5599 | 0.1953 | 49.0234 | Fail 5/5 |
| 8600 | R1 | 4.3337 | 0 | 47.9492 | Pass 5/5 |
| 8600 | R2 | 27.8330 | 0.5859 | 53.4180 | Fail 5/5 |
| 8601 | R0 | 60.5817 | 0 | 48.6328 | Fail 5/5 |
| 8601 | R1 | 6.4628 | 0 | 50.4883 | Pass 5/5 |

Origin hard qualification is 42.7734%. No sampled R0/R2 continuation is feasible. Retrospective best feasible R1 checkpoints are iteration 500 at seed 8600 (50.0977%) and 1,500 at seed 8601 (51.9531%); endpoint comparisons stay primary. R1 endpoint gains remain positive at all 25 reporting thresholds on both seeds; R0 has five negative cells on each seed. Every constituent condition/error/completion value and all 675 sensitivity rows are exported.

The twelve-policy census is A=`lucid_rg`, B=`lucid_s4_rg`, N=`lucid_ratchet_rg`, F=`fixed`, each seeds 8600–8602 and 8,000 iterations. Saved states establish A's single cohort and B's four intensity strata. Corrected interpretations distinguish the mismatch signal from return, allow positive contraction equilibria, represent ADR faithfully, use exact one-sided empirical tolerances, and limit MuJoCo/optimizer/additive-loss claims.

The 128-alias secondary nominal panel is kept separate (8.79% relative global error increase). No central saved body/reference/heading time trajectories or complete fixed-policy narrow/wide return matrix were found in the relevant existing evaluation records. These limitations are stated in the paper. No optional evaluation resource request is necessary for the narrowed diagnostic claims; no new simulation is authorized by this reporting addendum.

## Artifact validation and handoff

The authoritative Markdown now generates the eight-page anonymous TeX/PDF and HTML, with five figures drawn from the compact anonymous data package. `tools/export_diagnostic_data.py` verifies private sources and writes its identifying source map outside the package. The analyzer, full CSV reporter, numerical tests and package builder are portable. Six numerical contract tests pass. An isolated build in `/tmp/icra-diagnostic-portable-release` needs no author-home data or simulator; figure outputs match the working tree byte for byte.

Every PDF page was visually inspected; plotting-label collisions were fixed and the changed page checked again. The exact candidate also passed the live PaperPlaza ICRA 2027 initial contributed-paper PDF test with no reprocessing: no critical issues or margin problems, eight US Letter pages, searchable text, all fonts embedded, no Type 3 fonts. This was a compliance test, not submission. The receipt binds the tested PDF hash in `paper/evidence/icra-pdf-preflight-2026-09-08.json`.

The revised video uses existing footage only: 83.72 seconds, 1080p/25 fps, progressive MP4, about 7.30 MB. All 2,093 frames decode and are progressive. All 64 tile outcomes reconcile with the manifest whose source video hash matches the footage. The actual fixed/never-shrink/collapsed video policies are seed 8601; no-DR is seed 8600. A default script argument briefly suggested the wrong fixed seed during the audit; exact manifest binding resolved it before handoff. Visual samples span the complete duration, with full-resolution checks of amended labels. Human watch-through remains pending.

Final review materials: `paper/review-response-2026-09-08.md`, `paper/evidence-ledger.md`, `paper/submission-review-2026-09-08.md`. Remaining release requirements are actual IROS 1615 disposition and route, an independent human scientific challenge, all-author verification/approval and final metadata/submission receipts. The user was asked for disposition and the approving collaborator; no answer has arrived. Nothing has been committed, pushed, published or submitted to the conference.

The final review bundle is `outputs/icra_revision_20260908/diagnostic-review-package-2026-09-08.zip` in the private root (16,321,549 bytes, 66 files). SHA256: `da9e1d27f640c075c89f54eb5698243e500662b71cd249e28b23286f1fcb8f79`. It includes all compact inputs, source scripts, figures, scalar reports, the anonymous PDF, the final video and original hashed footage. The identifying source map and raw logs are excluded. Expanded candidate: `outputs/icra_revision_20260908/review-candidate`; execution receipt: `outputs/icra_revision_20260908/revision-receipt.json`.

Reviewed/tested PDF SHA256: `62bba60887efb22c02ab8179701c33956ba041f36761159505dc44d15c9758fd`, copied to `site/working-paper.pdf`. Reviewed video SHA256: `3201e7015221eaae08786762fde41b930ad5dd2b697ca550df361d16ee172555`, copied to `site/videos/diagnostic-video-draft.mp4`. These local copies do not publish the site. Final source/HTML/TeX and packaged file hashes were cross-checked after assembly.

## Goal continuation: live metadata preflight

The preceding goal turn made progress: it completed the existing-data revision, isolated build, visual checks and live PDF compliance test. This continuation rechecked the authoritative working PDF and all packaged hashes; they still match the reviewed candidate. No human disposition/review/approval has been supplied, so the same author-dependent release condition remains unresolved for a second consecutive goal turn. The goal is not complete.

Read-only navigation through the live ICRA 2027 blank contributed-paper form and keyword selector resolved two remaining metadata questions. The unchanged abstract uses 1,462 characters against the actual 2,000-character limit. The call's minimum of three keywords and selector's maximum of three require exactly three. Verified draft priority order: **Humanoid and Bipedal Locomotion**, **Reinforcement Learning**, **Performance Evaluation and Benchmarking** (96 combined characters including separators, below 250). The selector says keywords cannot be changed after submission. No authors were entered, consent checkbox accepted, metadata submitted or paper uploaded through the submission wizard. The earlier PDF upload was solely to the separate compliance-test service.

Anonymous evidence: `paper/evidence/icra-metadata-preflight-2026-09-08.json`; updated metadata: `paper/evidence/submission-metadata-draft-2026-09-08.json`. Raw blank forms stay private because they contain transient session fields. The checklist now records the exact limits and labels; the appropriate submission route still depends on IROS disposition and author approval.

The latest bundle is `outputs/icra_revision_20260908/diagnostic-review-package-2026-09-08-metadata.zip` (16,327,314 bytes, 68 files), SHA256 `04bddd32327956dee40a122f16e8ba9e866ba3185c21fba5f1f53047ed8b7c33`. Expanded directory: `outputs/icra_revision_20260908/review-candidate-metadata`. The original archive is preserved. The paper, video and scientific inputs have exactly the same hashes as the portal-tested/visually checked versions; only metadata, preflight evidence and handoff documentation changed. Archive integrity and anonymity scans pass.

Remaining completion evidence must come from the authors: IROS 1615 status and manuscript relationship, named independent human scientific review, ordered authors/PINs and corresponding author, approval of the exact scientific content and disclosure, and final route/submission authorization. Human verification must precede removal of the pending-review notices and dependent final file checks. Those requirements are explicit in the user's release gate and cannot be replaced by another automated audit or an unrequested experiment.

## Third-turn blocked audit

The previous goal turn was progress: it verified the live metadata constraints and produced the updated anonymous bundle. On this third consecutive goal turn, the current authoritative metadata still has null authors, corresponding author, PINs, IROS disposition and submission route. The execution receipt and release checklist still record pending human scientific review and all-author approval. No new author decision or approval has arrived in the conversation or current review records.

Fresh SHA256 checks confirm that the working PDF, video and latest archive still match the checked candidate. The metadata preflight is complete, and no experiment or build is awaiting a live process. Further finalization depends on the same unresolved author decisions: eligibility/route, human scientific and video review, final author metadata and approval. Repeating automatic checks, removing pending-verification notices without verification, or launching an unrequested experiment cannot fulfill those requirements. The goal is therefore marked **blocked on author input**, not complete. The checked artifacts are preserved for resumption when the required evidence arrives.
