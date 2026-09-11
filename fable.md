# Fable's Guidance — LUCID → ICRA 2027

**Status: the September 7 plan is executed. The paper is assembled, audited and complete as a
simulation-only diagnostic contribution.** This document was originally written on 2026-09-07 as a plan.
It is now the record of what was done, what I got wrong, what remains before submission, and where the
work goes next. The August 26 to September 2 log is preserved as `fable-archive-2026-09-02.md`.

**Deadline:** ICRA 2027, Tuesday 2026-09-15, 23:59 Pacific. Eight pages including references,
double-anonymous.

---

## 0. Where the work stands

| Item | State |
|---|---|
| Manuscript | 8 pages in the official `ieeeconf` class, at the limit, no overfull boxes |
| Anonymity | No author, affiliation, repository, W&B or filesystem string in source, text or metadata |
| Figures | 5, all generated from receipts with input-hash assertions, grayscale-safe, all cross-referenced |
| Tables | 7, numbered in reading order, each with denominators in its caption |
| References | 20, every identity and every citing claim verified against a primary source |
| Video | 6.84 MB, 75.7 s, 1080p, 25 fps, progressive H.264. Passes all six ICRA limits |
| Second-seed replication | **Complete.** All 57 cells. R1 passes, R0 fails, on both seeds |
| Independent verification | 37 claims recomputed from raw data, not from summaries |

The four contributions, all measured, all receipted:

1. **Range collapse.** An adaptive curriculum allowed to narrow its own ranges does so in all six runs
   and nearly collapses in two. Terminal return and independently measured robustness are inversely
   ranked, Spearman −0.73 over twelve runs. A collapse costs 14.19 success-AUC points against fixed
   randomization on the same seed.
2. **Never-shrink.** The projection blocks all 2,033 requested reductions across three seeds and passes
   a preregistered tolerance rule. Not equivalence: the one-sided 95% lower bound is −3.19 points.
3. **Survival and fidelity decouple.** Continuation holds 100% nominal completion while global error
   rises 127.93 to 225.87 mm. A fixed practice mixture does not prevent it (+28.20%), nor does restoring
   optimizer state (+27.75%).
4. **Reference anchoring, replicated.** R1 holds the endpoint increase to +4.33% and passes retention at
   all five checkpoints, gaining +5.18 points of hard-condition qualification. A preregistered second
   continuation seed reproduces it: +6.46% and +7.72 points, passing all five again, while the unanchored
   control fails at every checkpoint on both seeds.

Plus the explanation that makes the negatives cohere: fixed randomization already nests every curriculum
stage's marginal parameter values, so a curriculum needs a concentrated target to help. That is the
paper's most valuable idea and it is also the bridge to deployment, because a real robot *is* a
concentrated target.

---

## 1. What I got wrong in the original plan

Recording these because the corrections matter more than the plan did.

- **I said seven pages with room to spare.** It is eight, which is the legal limit. The extra page went
  to verified corrections, not padding.
- **I proposed a supplementary PDF.** ICRA does not support one. The evidence ledger lives in the repo
  instead.
- **I conflated two evaluation panels.** I wrote "128 → 324 mm" and "127.93 mm" as if they shared a
  denominator. They do not: 128.57 mm is the legacy quality-frontier panel and 127.93 mm is the masked
  first-episode retention panel. A parallel agent caught this before I did.
- **I assumed the plan was unexecuted.** Most of section 3 had already been carried out by a parallel
  agent before this session began. The useful work turned out to be verification, not authorship.
- **I described never-shrink as close to Automatic Domain Randomization.** ADR's boundary rule is
  bidirectional: it contracts below a low threshold. Never-shrink is that rule with the contraction
  branch removed, which is a difference on exactly the axis contribution 2 is about.

---

## 2. What the audits found, and what I did about it

Two adversarial workflows ran, 8 agents and 14 agents. They returned 10 blockers, 50 majors and
140 problems between them. Every finding was checked against a primary source before I acted on it.

The three that changed a claim:

- **Section 9 contradicted its own table.** The text asserted an ordering that holds in one of six cells.
  At λ = 1 the collapsed policy is the strongest arm in both columns. Rewritten to claim the ordering only
  beyond the envelope, and the inversion is now reported as evidence for the paper's own thesis: a
  narrowed policy looks best exactly where it is scored.
- **Two "separate" controls were one run.** The no-expansion continuation and the fresh branch of the
  optimizer comparison share every training setting; their evaluations differ only by a label and an
  11th-decimal contact value. Section 8.2 now says so and reports both endpoints, which were missing.
- **Table 2 is near-tautological by construction.** The controller is capped at λ = 1, so the projection
  reduces to clamping, and 99.2% of never-shrink environment-iterations sit at the envelope against 100%
  for fixed. The paper now states this before the table.

Three findings I checked and **rejected**: a claim that the evaluator was unpinned across campaigns (it is
pinned by content hash; the auditor conflated it with the worktree commit), an instruction that would have
merged two genuinely distinct runs, and reported journal publications that arXiv does not show. Acting on
any would have put a false statement in the paper. Adversarial output is a lead, not a verdict.

Full record: `paper/review-response-2026-09-07b.md`.

---

## 3. What remains before submission

Small, and none of it is research.

1. Final read of the assembled PDF end to end, for typography and float placement only.
2. Decide the public-repository question. The site is public and names the author while the paper is under
   double-blind review. This is a judgement call for the author, not a defect.
3. Submit before September 15, not on it. Video upload windows close September 9 and reopen September 17,
   so the video must go up before September 9 if it is to accompany the initial submission.

Do not add experiments. The evidence is closed and the page budget is spent.

---

## 4. Where the work goes next: real-world deployment

The paper is honest that it has no hardware result. The deployment roadmap is a separate document,
`lucid-deployment-roadmap-2026-09-07.md`, published on the project page. Its spine:

- **Tier 0, controller prerequisites.** The deployed actor cannot see its own horizontal path error. In
  6,144 paired-state comparisons a ±0.25 m translation changed the critic's displacement input and every
  yaw control while leaving raw actor terms, assembled proprioception, encoder outputs and action means
  exactly unchanged. A two-column path-error input was built and shadow-gated at max action difference
  0.0, and a 128-iteration pilot ran. It also needs a multi-motion origin: the local origin qualifies on
  none of three longer motions while the released controller qualifies on all four.
- **Tier 1, trustworthy measurement.** No recovery bands, dwell or horizon are frozen, so no
  recovery-qualified endpoint exists. The development clip yields 191 events, all of zero magnitude, and
  only 31 have two uninterrupted seconds.
- **Tier 2, does feedback earn its cost.** Protected fixed practice against a frozen schedule against
  recovery feedback, one budget, same retention mechanism.
- **Tier 3, independent origins and a validated export.** Two continuation seeds from one origin are not
  two origins.
- **Tier 4, hardware.** Instrumented pushes in physical units, external position truth, safety and stop
  rules. A simulator velocity increment is not a calibrated impulse in newton-seconds.

**The single hardest obstacle** is that the exact simulator position used to fix the path-error input is
privileged information. On a real robot it must come from a state estimator or external tracking, and the
error of that source enters the control loop. That is a deployment research problem, not an engineering
detail, and it should be named as such rather than deferred.

---

## 5. Rules that stayed in force, and earned their keep

- Every number points to a receipt. This is what caught the duplicated control and the mis-numbered tables.
- Verify adversarial findings before acting. Three of ten blockers were wrong.
- A tolerance pass is a decision, not equivalence. Print the bound next to every tie.
- Never select a checkpoint after seeing its trajectory. R1's best checkpoint is not its endpoint on
  either seed, and the endpoint is what is reported both times.
- Completion is reported beside tracking error in every table that has either. That is the paper's point.
