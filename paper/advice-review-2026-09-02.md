# Review of the paper-framing advice (2026-09-02)

Verdict: adopt the central question, the problem-first structure, the plain vocabulary, and the
second title. Correct four details before the advice is applied to prose. Applied in
`paper/when-training-gets-easier.md`.

## Adopt

- **"Is the robot getting better, or is its training getting easier?"** is the paper. Every
  measured result answers it: the collapse (Sec. 4), the never-shrink rule (Sec. 5), the
  signal audit (Sec. 6), the per-channel sweep (Sec. 7). None of the pending work is needed
  to make that paper complete.
- **Title.** *When Training Gets Easier: Training-Range Collapse in Humanoid Control* matches
  what is measured. *Expanding Training Ranges for Humanoid Control* is the project title
  and becomes the paper title only after the matched-schedule test (Sec. 9) is run.
- **Vocabulary table.** Applied throughout; Appendix A of the new draft keeps the mapping so
  the codebase names (ratchet, gate, probe) still resolve.
- **Abstract.** The proposed abstract is honest and was kept almost verbatim. Two additions:
  the twelve-run inversion (Spearman −0.73), which is the strongest single figure we own, and
  the MuJoCo replay, which did not exist when the advice was written.

## Correct

1. **"Held-out performance" needs its axis named.** Our frontier ladder is held-out physics
   on the trained motion, plus one untrained clip of the same family at two cells. The new
   draft says exactly that and never says "generalization".
2. **The advice drops two measured results that carry the argument.** The signal audit
   explains *why* the collapsing curriculum collapsed (its signal has no authority), and the
   channel sweep is the only evidence that per-parameter expansion is worth building. Both
   stay in the main text; they are not future work.
3. **Novelty of the never-shrink rule.** It is essentially ADR's boundary rule. The new draft
   says so in Related Work and claims the measurement, not the rule. Reviewers will check.
4. **"Four increases from 1.0 to 1.5"** is correct but the same run also shows the return-guard
   defect (914 freezes after the ceiling). Reporting the defect with the result is what makes
   the prototype credible.

## Do not do

- Do not present the MuJoCo 8-seed grids as evidence that the never-shrink policy beats
  fixed DR. On 32 seeds they tie (38% = 38%); the video header carries the 8-seed count.
- Do not use "Claim A / Claim B" in the paper. The reader should meet the question, not a
  claim taxonomy. The distinction survives as Sections 5 and 9.
- Do not keep MAnD-Ex, the eight cohorts, or the latency-process coordinates in the main
  text. They belong to the project plan until they have a result.
