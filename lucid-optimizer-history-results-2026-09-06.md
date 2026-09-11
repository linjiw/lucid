# Optimizer history control: complete results and continuation decision

September 6, 2026. The full 22-cell comparison completed at 07:21:21 UTC.
Both fresh and restored AdamW arms trained for 2,000 iterations under the same
fixed initial E0 mixture. All saved evaluations and the complete analysis are
available. The 39 analysis input hashes and six output hashes were reverified
before interpreting these results.

**Select fresh history for the retention-repair screen.** Restoring history is not
a quality repair in this setting: every sampled restored checkpoint breaches the
origin-relative global-error margin, and restored history has a lower held-out
tracking-qualified endpoint. This is the existing bounded development rule, not a
new selection criterion fitted after the comparison.

| Checkpoint | Fresh clean global / local mm | Restored clean global / local mm | Fresh / restored clean retained |
| ---: | ---: | ---: | --- |
| Origin | 128.57 / 28.33 | Same origin | Reference |
| 250 | 118.25 / 28.95 | 157.18 / 27.77 | Yes / No |
| 500 | 146.72 / 29.44 | 172.81 / 29.59 | No / No |
| 1,000 | 141.17 / 28.95 | 212.48 / 29.34 | Yes / No |
| 1,500 | 183.99 / 30.27 | 190.55 / 30.52 | No / No |
| 2,000 | 164.83 / 29.59 | 164.24 / 30.50 | No / No |

Retention combines the original two-point completion margin and +10% legacy
global/local error margins. Fresh at 250 has one failed episode (99.80%
completion), which is within the completion margin but remains visible. Restored
clean completion is 100% at every saved stage. Its final qualified success is
99.61%, versus fresh 100%; completion alone conceals both arms' continuous drift.

At the final checkpoint, clean global drift is +28.20% fresh and +27.75% restored;
local drift is +4.42% and +7.65%, respectively. Thus the small restored advantage
in final global error does not establish retention or erase its worse trajectory.
The unweighted means over the five checkpoint-to-origin global ratios are 1.17438
fresh and 1.39576 restored; local ratios are 1.03903 and 1.04277.

| Final condition | Fresh completion / qualified % | Restored completion / qualified % |
| --- | ---: | ---: |
| Clean | 100.00 / 100.00 | 100.00 / 99.61 |
| Original mixed DR | 98.83 / 96.88 | 99.61 / 95.12 |
| Push 3× | 75.59 / 60.35 | 77.93 / 60.74 |
| Push 3.5× | 65.04 / 48.24 | 66.41 / 47.66 |
| Push 3.5× + friction 1.5× | 55.47 / 39.06 | 59.96 / 38.09 |

The equally weighted qualification average over the two held-out hard conditions
is 43.6523% fresh and 42.8711% restored: restored-minus-fresh is −0.78125 points.
Restored improves hard-condition completion while reducing useful tracking on
both held-out conditions, another example of the survival–quality tradeoff.

The generic analysis says the final restored-versus-fresh retention checks pass.
That comparator is the already drifted fresh endpoint. It does **not** mean either
arm retains the original policy's quality. The separate origin-relative trajectory
rule correctly rejects restored history as the repair recipe.

The experiment isolates restored moments and bias-correction counters under the
pinned fresh-reset contract. It does not prove that PPO termination penalties
dominate pose rewards, that optimizer history never matters, or that exposure
expansion caused the earlier larger drift. It concerns one development origin,
one motion, fixed E0 exposure and simulation only; reconstructed historical
optimizer parameter-order provenance remains as documented in the original audit.

Evidence: [complete report](/home/linjiw/lucid-sonic/analysis/optimizer_history_pilot_20260905_a/report.md),
[analysis receipt](/home/linjiw/lucid-sonic/analysis/optimizer_history_pilot_20260905_a/receipt.json),
and [full-grid recipe decision](/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_a/continuation_decision.json).

The subsequent origin collection completed with 2,048 balanced raw histories.
The first repair campaign stopped before smoke at teacher-target validation.
The [precision diagnosis and corrected execution](lucid-anchor-precision-repair-2026-09-06.md)
records that instrumentation failure. It does not invalidate the completed history
comparison or constitute a behavioral retention result.
