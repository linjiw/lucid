# LUCID research review and next methods paper — September 10, 2026

LUCID asks whether humanoid robustness training improves the motion the robot executes under disturbance, while retaining its original tracking skill. The current paper is a diagnostic study with measured safeguards. A methods and systems paper remains a research objective: recovery, deployable feedback, multi-motion retention, and hardware benefit are not established.

## Current evidence and paper status

| Study | Verified status | Supported interpretation | Remaining boundary |
|---|---|---|---|
| Range collapse | Twelve scored policies; three training seeds per arm | Return can improve while externally measured robustness deteriorates; never-shrink blocks contraction | +0.60 AUC points versus fixed, SD 2.25; no superiority or statistical noninferiority |
| Protected continuation | R1 passes all five sampled retention checks on each of two seeds | Nominal global drift +4.33% / +6.46%; hard qualification gains +5.18 / +7.72 percentage points | One origin, one motion; extra anchor computation; broad development thresholds |
| Translation observability | 6,144 translations across 1,536 base states leave actor inputs and actions unchanged | The tested actor cannot distinguish those horizontal offsets | Does not isolate the cause of every trajectory failure |
| Common path-input pilot | Live same-state parity passed; 128 training iterations and 16 evaluations completed | Engineering feasibility of the simulator input seam | Earlier cross-process gates failed; two sideways-push failures in 128 trials; no calibrated recovery result |
| Three-motion DR A/B | Both 8,000-iteration arms have exported endpoints; 196/196 final Isaac evaluation cells exit zero with metric files | One-seed screening contrast across three training-clip panels and 102 development motions | Uniform motion sampling; one seed; development pool is not a new motion distribution |
| New MuJoCo A/B | Five mixed-physics and six latency cells per arm, 16 rollout seeds per cell | At mixed λ=2, final-height failures are 14/16 without DR and 5/16 with DR | One curved-walk clip; independent simulator implementation; different torque limits; no hardware result |
| Manuscript | Authoritative Markdown, generated HTML/LaTeX and working PDF | Diagnostic paper; future method explicitly marked proposed | Human scientific review and submission approval remain open; any regenerated PDF needs renewed submission checks |

The final Isaac campaign completed September 9 at 12:43:56 local time. The old “still running” text is superseded. This review checks receipt exit codes and metric-file existence; it does not independently revalidate all metric implementations. The original interrupted evaluation attempt is excluded. The compact [audit](site/data/review-2026-09-10.json) records the eleven final receipt hashes and independently aggregates the MuJoCo outcomes.

The Isaac development panel's reported completion is 66.67% without DR versus 60.78% with DR at nominal physics, and 0.98% versus 50.98% at fixed 60 ms delay. These are 102 development motions, one trained policy per arm, and completion is not tracking qualification. Legacy MPJPE summaries need their own masking/denominator audit before being combined with the continuation paper's episode-based errors.

## Corrections to the public demonstration

The MuJoCo `fell` Boolean means that pelvis-to-reference distance exceeded 0.5 m. The displayed `outcome == fell` instead combines that tracking failure with terminal pelvis height at or below 60% of reference height. It is a final-height failure proxy, not detection of every fall during the clip. Videos continue after path departure; scoring retains the first departure time.

The no-DR control has three tracked rollouts at mixed λ=0.5 and four across the latency cells (two at 0–40 ms, one at 0–60 ms, one at 0–120 ms). The DR arm has zero in every cell. Thus “neither ever completes” was false. Neither demonstrates reliable full-clip tracking. Nominal mean time before leaving the 0.5 m band is approximately 5.5 s versus 1.3 s.

MuJoCo λ is its own mixed evaluation scale. It is not the deployment arm's training envelope: that arm uses physics 1×, push 3× and delay 1.5×. Nor is MuJoCo's sampled delay envelope identical to Isaac's fixed-delay ladder. Simulator torque limits and termination definitions differ. A common scalar and threshold cannot establish matched physics or matched success criteria.

## Most promising direction: observable recovery with protected tracking

**Hypothesis:** a controller that receives a realizable estimate of reference-relative displacement and heading can regain the commanded path after disturbance; protecting nominal behavior during adaptation can prevent the gain from being purchased through persistent drift. This is a proposed mechanism, not a demonstrated LUCID result.

The smallest useful next experiment is a matched feedback ablation under fixed DR, before a learned curriculum. Start with a competent shared multi-motion origin. Compare the existing actor, zero-input control, oracle relative feedback, and estimated relative feedback through the same input adapter, backbone, optimizer, training budget and motion mixture. Use origin anchoring in all primary arms. A subsequent feedback-by-anchor factorial measures whether protection changes the recovery/quality tradeoff.

The deployment input should contain body-frame relative path displacement, heading error and validity/uncertainty indicators from a named localization source. Oracle simulator position is only an upper bound. Train and test the estimated-input branch under frozen bias, drift, delay and dropout conditions; specify reference-frame initialization and clock synchronization. Absolute position is not observable from proprioception alone without additional assumptions. When localization is unavailable, evaluate a declared local velocity/heading tracking task instead of claiming global path recovery.

First use constant anchor strength. An error-dependent anchor that relaxes during recovery and restores during nominal tracking is a later ablation, because relaxing preservation may itself explain a quality loss. Likewise, uncertainty should initially define evaluation strata and a declared fallback, not become an unvalidated curriculum score.

## Experiments remaining, in dependency order

| Gate | Decisive experiment / deliverable | Pass evidence and decision |
|---|---|---|
| 1. Competent origin and deployment contract | Validate a released/common origin on adaptation motions and separate development motions; export parity on identical observation traces; align joint order, gains, delays, torque limits, normalization and reset state | Nominal completion **and** continuous global/local errors pass frozen motion-specific tolerances. Do not train recovery from an origin already failing the task. |
| 2. Recovery measurement | Log disturbance time, root displacement, heading, articulation and contact separately; freeze bands, dwell, horizon, phase and censoring before comparisons | Return to all declared bands for the dwell within the horizon, with failures retained. Validate detector against trajectories; terminal height is insufficient. |
| 3. Feedback mechanism | Same-budget absent/zero/oracle/estimated feedback under fixed DR; then feedback × anchoring | Improvement in recovery with retained nominal and original-envelope tracking. If oracle fails, reconsider control/training; if only oracle helps, prioritize localization/actuation. |
| 4. Uncertain and combined disturbances | Hold out push direction/phase, delay, friction, mass/CoM combinations and localization faults; report every condition and worst condition | Freeze selection on development data; evaluate final policies once on held-out conditions/motions. Show recovery probability, recovery time with censoring, error distributions, completion and effort/saturation. |
| 5. Replication and resource controls | Independent origin seeds and continuation seeds, with fixed broad DR and hand-designed curricula; use pilot variance to size confirmation | Report per-origin paired effects and uncertainty. Match simulator transitions and disclose GPU time, teacher queries, anchor forwards and validation cost. No universal seed count guarantees sufficiency. |
| 6. Adaptive allocation, only if warranted | Protected fixed, frozen/yoked schedule and adaptive schedule with identical feedback, retention, support and selection budget | Establish benefit beyond feedback/protection and exposure alone. Utility estimator and residual allocator remain blocked by Gate A/B; no reopening through this roadmap. |
| 7. Sim2sim system | Frozen exports in Isaac and MuJoCo with matched actuator contract and documented residual mismatch; full motion coverage | Tracking and recovery gains survive transfer. Ablate actuator mismatch separately from DR; do not combine new A/B and historical R1 cohorts. |
| 8. Sim2real system | Build/run deployment stack, verify value-level parity, measure latency and estimator error, then a bounded supervised G1 protocol with physical stop/fall-arrest provisions | Report physical disturbances with force/time/contact geometry, all trials and interventions, tracking/recovery and thermal/torque limits. Simulation velocity increments are not measured impulses. |

Future training/evaluation must use online W&B in `16726/lucid-sonic`, one dated campaign group, explicit stage/arm/seed/checkpoint/condition, source and frozen-plan hashes, metric/checkpoint hashes and verified URLs. This review launches no new robot or simulator experiment. A read-only W&B API query on September 10 found no recent run names matching the A/B campaign identifiers or “deploy”; its online coverage is therefore unverified, not declared absent. The query result is retained privately under `outputs/research_review_20260910/wandb_check.json`. Resolve this provenance gap and record verified run URLs before treating the campaign as logging-complete. Environment variables do not establish online logging.

## Paper argument and positioning

Keep the current diagnostic paper's title and measured results. The new methods paper should answer: **Can observable, quality-preserving adaptation improve disturbance recovery under uncertain sensing and dynamics?** Its candidate contributions are the deployable feedback/protection mechanism, a calibrated recovery evaluation, and a measured transfer system. These become contributions only when the corresponding gates pass. A collection of completed engineering tasks is not evidence of method efficacy.

The nearest-work check is targeted, not a systematic novelty review. [ASAP](https://arxiv.org/abs/2502.01143) learns a residual action model from real data to address dynamics mismatch; actuator alignment is therefore an important alternative explanation/control. [BeyondMimic](https://beyondmimic.github.io/) already demonstrates real humanoid tracking and steerable control. Recent [StableMimic](https://arxiv.org/abs/2608.02385) targets structured post-fall behavior, while [What Matters in Humanoid General Motion Tracking?](https://arxiv.org/abs/2607.19903) studies representation and actuation choices. Our proposed distinction is sustained return to a specified path with explicit retention under uncertain estimated feedback, not recovery or regularization in general. Read full methods and align tasks before claiming novelty or choosing a direct baseline.

For a strong systems paper, show the full sensor-to-actuator contract, integration failures, deployment latency, and the supported operating envelope. For a methods claim, isolate the mechanism with the fixed-DR feedback ablation first. Hardware is necessary for a sim2real claim, not for the validity of the existing simulation diagnosis.

## Revision validation

The September 10 manuscript builds to eight pages with Tectonic. All six existing diagnostic-data tests pass; local page asset/link checks pass and the featured video is readable by ffprobe (28.44 s). Publication uses the existing GitHub Pages workflow. No new simulation, training, hardware trial or paper submission was performed. The prior PDF portal check applies only to its prior hash.
