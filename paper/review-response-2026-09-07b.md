# Response to the independent adversarial review — September 7

An eight-agent independent audit (three reviewer lenses, three citation groups, a figure audit and a
related-work gap search) was run against the built PDF and the receipts. It returned 7 blockers,
50 majors, 23 minors, 6 citation identity errors and 6 citation claim errors. Verdicts were
weak-accept (claims), borderline (statistics), borderline/weak-accept (novelty), weak-accept (figures),
borderline (related work).

Every fix below was applied only after the underlying fact was independently verified against a
primary source or a receipt. Nothing was taken on the auditor's word.

## Corrections that changed a claim

1. **Section 9 contradicted its own Table 6.** The text said "The ordering is what transfers," but at
   λ = 1 the collapsed policy is the strongest seed-8601 arm in both columns (56% all channels,
   84% physics only). The claim held in one of six cells. Rewritten to "the ordering transfers only
   beyond the training envelope," and the λ = 1 inversion is now reported as *evidence for* the paper's
   own thesis: a narrowed policy looks best exactly where it is scored. No number changed.

2. **Automatic Domain Randomization was mis-described, against our own interest.** Verified from
   Algorithm 1 of arXiv:1910.07113: ADR increases a boundary when performance exceeds a high threshold
   and *decreases* it below a low threshold. Section 2 previously implied ADR only expands, and then
   called never-shrink "close to" it. Never-shrink is that boundary rule **with the contraction branch
   removed**, which is a difference on exactly the axis Contribution 2 is about. Corrected; the
   contribution is stronger for it.

3. **Table 2 is a near-tautology by construction, and now says so.** The controller is bounded at
   λ ∈ [0, 1], so the projection cannot expand past the envelope and reduces to clamping after warm-up.
   Verified from `lucid_realized_exposure_20260903.json`: never-shrink puts 99.2% of environment-iterations
   at the envelope against 100% for fixed, with nothing above it. A new paragraph before Table 2 states
   that the table bounds seed and stream variation between near-identical procedures, and that the
   informative comparator for the projection is the unconstrained controller that collapses.
   The redundant "Realized exposure" paragraph was removed.

4. **The generality of Contribution 1 is now defended from our own data.** The obvious attack is that
   collapse was shown only on our controller, whose signal Table 3 itself rejects. Answer added in
   Section 6: the two signals that *do* track competence at pinned difficulty, mean return (+0.973) and
   time-out survival (+0.987), are also the two that improve when ranges shrink. The pressure to contract
   is a property of scoring a curriculum on the distribution it controls, not of the rejected signal.

5. **Both collapses are cross-variant and cross-seed.** Verified from `lucid_return_inversion_20260901.json`:
   the twelve runs are a crossed design of four arms by seeds 8600/8601/8602, and the two collapses are
   `lucid_rg@s8601` (λ 0.062) and `lucid_s4_rg@s8600` (λ 0.012) — different variants, different seeds.
   Stated in Section 4.2. The ten range-holding runs are four adaptive, three never-shrink and three
   fixed, so that grouping is now described as range preservation rather than a method.

## Citation corrections (all verified against primary sources)

| Ref | Was | Now |
|---|---|---|
| [13] | "T. E. Truong et al., BeyondMimic" | **Wrong first author.** Verified author order is Q. Liao, T. E. Truong, X. Huang, Y. Gao, G. Tevet, K. Sreenath, C. K. Liu |
| [8] | Klink, CoRL 2020 | CoRL **2019**, PMLR 100:513–529 (PMLR v100 is CoRL 2019; v100 was published in 2020) |
| [9] | Portelas, CoRL 2020 | CoRL **2019**, PMLR 100:835–853 |
| [1] | grouped under "physical parameters" | Tobin et al. randomize **rendering**, not physics. Sentence now reads "visual [1] or physical [2–4]" |
| [16] | cited for "report success rather than reward" | Agarwal et al. is about reliable evaluation from few runs; now cited for paired per-seed reporting at three seeds |
| [12] | "arXiv:2511.07820v1" | version pin dropped |

A reported Science Robotics 2026 publication for [12] and [13] was **not** added: arXiv shows no journal
reference for either, so the claim could not be confirmed and was left out.

## Citations added (each verified before use)

- **[18] Mozifian et al., LSDR, IROS 2020.** The closest prior art and previously uncited. It regularizes a
  learned randomization distribution toward a broad prior specifically so it does not concentrate on easy
  environments. The manuscript now says plainly: prior work anticipated this failure and designed it away;
  we permit the reduction and price it.
- **[19] Rudin et al., CoRL 2021, PMLR 164:91–100.** The standard legged-locomotion curriculum, and it
  demotes: verified text, "if at the end of an episode it moved by less than half of the distance required
  by its target velocity, its level is reduced again." Levels are per-robot, so demoting one robot does not
  remove hard conditions from the batch. This correctly scopes our mechanism claim to a single global
  difficulty scalar driven by a batch-aggregate score.
- **[20] Wołczyk et al., ICML 2024.** Section 8 previously cited nothing for what is a forgetting result.
  Forgetting during RL fine-tuning and its mitigation by retention terms are established; what is new here
  is that fidelity is lost while completion stays at 100%.

## Figure repairs

- **The MuJoCo figure silently dropped an arm.** It plotted four of Table 6's five, omitting Fixed (seed 8600),
  which is the row the adjacent seed-effect sentence depends on. Restored from the raw draws (93.75 / 56.25 /
  31.25%, all 32 files present per scale).
- **Grayscale.** Series were distinguished by hue alone. The MuJoCo and retention figures now vary marker
  shape and line style as well as colour.
- **Unlabelled reference lines.** The retention figure's 10% budget line and origin marker were unlabelled;
  both are now annotated.
- **No cross-references.** The body never referred to a figure. Figures 1–5 are now called out in the text.
- **Captions.** The MuJoCo caption now states that all five arms appear and that the two fixed seeds differ
  by as much as the methods; the signal-audit caption now discloses that it plots three of the five audited
  signals.

## Other repairs

- Frontier AUC is now defined precisely enough to interpret the 2-point margin: a trapezoidal area over the
  four beyond-envelope cells, normalized to a mean success rate in points.
- The continuation origin is identified as the fixed-randomization seed-8600 checkpoint of Section 5,
  which connects the two halves of the paper.
- R1's binding checkpoint is now reported (largest sampled increase 7.35% at 500 iterations), not only its
  4.33% endpoint.
- The Push 3.5× qualification figure of 49.02% in Section 8.1 is now marked as belonging to the legacy panel,
  because it collides numerically with an unrelated Table 5 quantity.

## Not adopted, and why

- The auditors proposed a new λ-trajectory figure. The data exists, but the paper is at the eight-page limit
  and the existing five figures each carry a distinct claim. Deferred.
- Several suggestions asked for uncertainty intervals on single-seed channel-sweep cells and on the 32-draw
  MuJoCo proportions. The denominators are already stated in the captions; adding intervals to descriptive
  development measurements would imply an inferential status these do not have.

## State after the response

Eight US-letter pages in the official ieeeconf class, at the limit but legal, with roughly 1.2 columns free
on the reference page for the pending second-seed result. No overfull boxes, no missing glyphs. No author,
affiliation, repository, W&B or filesystem string appears in the source, the extracted text or the metadata.

---

# Response to the evidence-ledger audit — September 7 (second workflow)

A separate 14-agent audit re-derived every paper-usable number from the receipts and then had
skeptics try to refute the extractions. It returned 104 problems and 36 refuted facts, of which
3 were marked blockers. Each was checked by hand before any action.

## The one that changed the paper

**Two "separate" controls in Section 8.2 were the same run.** The no-expansion continuation and the
"fresh" branch of the fresh-versus-restored optimizer comparison have identical training
configurations: same origin checkpoint, seed 8600, 2,000 iterations, `mode=box`, `initial_lambda=0.0`,
`fixed_lambda=1.0`, with the only difference an `optimizer_history.mode` flag that defaults to fresh.
I verified their evaluations directly: across all nine shared cells the metric values agree, and in the
nominal cell the only differences are the branch label and a contact-impulse value at the 11th decimal
(2795.5576487512953 against 2795.5576487676685), which is the contact non-repeatability already
documented in this project.

The draft said "Drift persists when the initial hard-practice mixture is held fixed. A separate
fresh-versus-restored optimizer-history experiment also finds degradation in both branches." That
presents one control as two. Section 8.2 now states the numbers and the relationship: the fixed-mixture
continuation ends at 164.83 mm against the origin's 128.57 mm on the legacy panel (+28.20%), the
restored-optimizer branch at 164.24 mm (+27.75%), and the fixed-mixture run and the fresh branch are
one control measured twice. Both endpoint numbers were absent from the draft and are now in it.

The same audit surfaced a limitation of the restore arm that is now stated: the historical optimizer
metadata were unavailable, so its parameter binding is a reconstruction, recorded in the receipt with
`policy_parameter_binding_verified = false` and `simulator_run = false`.

## Blockers I checked and did not act on

- **"The ladders span four evaluator git trees, so the 14.19-point headline pairs incomparable scores."**
  Not correct. The Phase-0 receipt records `evaluator_pin` as a content hash
  (`308e2415…`) with the note "the build that produced every historically scored arm"; `ca057e65` is the
  *worktree* commit, which can differ between campaigns while the evaluator file itself stays pinned. The
  auditor conflated the two. The manuscript makes no claim about evaluator commits either way, so nothing
  changed.
- **"Keep the word episodes at line 162."** That paragraph had already been removed earlier in the session
  and replaced with environment-iterations, which is the correct unit. The advice pointed at the wrong half
  of a hygiene rule.
- **"Present R2 and the optimizer 'fresh' arm as the same continuation."** R2 is the lower-learning-rate arm
  of the retention screen in a different campaign, ending at +27.83% on a different panel. Following that
  instruction would have merged two distinct runs and put a false statement in the paper. Declined.

## Further precision fixes adopted

- **The friction clamp binds earlier than stated.** With a static-friction range of [0.3, 1.6] about a
  nominal 0.95, the low bound is 0.95 − 0.65λ and reaches the 0.05 floor at λ = 0.9/0.65 ≈ 1.385, not 1.5.
  Section 3 now says it begins to bind at λ ≈ 1.385 and that λ = 1.5 is the first ladder cell affected.
- **The seed effect was understated.** The draft said between-seed offsets "reach 7.8 points"; that figure
  is a mean of two paired 8600-to-8602 differences. The largest same-arm spread visible in the paper's own
  Table 2 is 9.3 points (never-shrink, 82.03 to 91.31). Section 5 now quotes 9.3 and points at Table 2 so a
  reader can check it.
- **The anchor cost is a lower bound.** 207.37 seconds is time measured inside the student forwards, not the
  anchor's total compute. Section 8.3 now says so.

## Checked and already correct in the draft

R2 is disclosed as a schedule change and not a pure learning-rate ablation. The 99.2% exposure figure
matches the receipt's own presentation. The MuJoCo-versus-Isaac λ asymmetry is covered by the existing
"labelled approximation" hedge. The 600/50 mm thresholds are already described as broad development
thresholds rather than robot tolerances.
