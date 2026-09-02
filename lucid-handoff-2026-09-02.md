# LUCID handoff — 2026-09-02 (per-channel expansion direction)

Companion to `lucid-research-plan-2026-09-01.md` (section 8 is today's
addendum), `lucid-handoff-2026-09-01-phase2.md` (Phase 2 operations) and the
paper draft `site/lucid-paper.html`.

## 0. Update 07:45 EDT — gate arm complete, queue script ready but NOT launched

- **gate_150 finished** (final checkpoint exported 05:56): four expansions
  from scratch, frontier at the 1.5 ceiling, zero guard trips, zero applied
  decreases. The from-scratch probe-gated mechanism works.
- **ramp_150 is training** (started ~06:00, the Phase 2 driver untouched).
- The user asked whether to stop Phase 2 for the prototype loop. The
  answer implemented: **pause, don't kill.** `tools/run_queue_20260902.sh`
  SIGSTOPs the ramp trainer (+ wandb children), runs the prototype loop in two
  scored batches (box_150/gate_150/box_asym/ramp_asym/fixed_150, then
  ramp_150/fixed/fixed_asym), and SIGCONTs the trainer under an EXIT trap.
  Phase 2 amendment A9 and prototype amendment A5 record it. The agent's
  launch was blocked by the permission classifier (it signals another
  process), so it must be started by hand:

      nohup bash tools/run_queue_20260902.sh --execute > $LUCID_ROOT/outputs/queue_20260902.nohup 2>&1 &

  Progress: `tail -f $LUCID_ROOT/outputs/queue_20260902.log`. If it is ever
  killed, `kill -CONT $(cat $LUCID_ROOT/outputs/queue_20260902.paused_pids)`
  resumes Phase 2 by hand. Expected: batch 1 scored ~15:30, batch 2 ~21:00,
  Phase 2 resumes after and finishes ~2026-09-03 afternoon.

## 1. Live state at hand-off (written 01:30 EDT)

- **Phase 2 screen is training**, experiment
  `curriculum_comparison_ne1024_20260901_232720`, worktree `~/lucid-phase2`
  at SONIC `8fa9732`, arm order gate_150 → ramp_150 → fixed_150 → fixed_u150 →
  fixed. At 00:20 EDT the gate arm was at iteration ~1,000, population
  survival 0.05, probe survival 0.03 at λ=1.125, no expansion yet (expected:
  fixed DR only reaches ~0.95 survival by iteration 5–6k). It ran at ~3.2 s/it
  while the evaluation sweep shared the card; ~2.4 s/it alone. Expect the five
  arms to finish 2026-09-03 morning. **Do not edit `~/lucid-phase2`.**
- **Single-channel attribution sweep** ran beside it
  (`tools/run_channel_sweep.sh`, ~55 s per 512-episode cell under contention,
  ~4.5 GiB beside the trainer's ~7.4 GiB). Receipts under
  `$LUCID_ROOT/manifests/channel_sweep_20260902_001226/`. A first launch died
  at the Omniverse EULA prompt because the driver did not source
  `env/lucid_env.sh` under nohup; it is voided in place
  (`void_channel_sweep_20260902_001037` in manifests/artifacts/outputs).
  Readout: `python tools/analyze_channel_sweep.py`.

## 2. What was built today (all committed, all tested)

SONIC `research/practice-utility`:

| Commit | What |
|---|---|
| `58812d7` | Evaluator: `channel_dr_scales` on the eval callback and eleven `ch_<term>_<level>` presets (one term widened, the other four at λ=1, latency pinned to zero). Scalar path byte-identical. |
| `eac9455` | `box_gate.py` (vector frontier, one probe in rotation), curriculum mode `box`, driver arm `box_150`, `SurvivalGateController.clear_window`. 20 new tests; suite 1,671 passed. |
| `c4d922a` | `box_lambda_max` per-channel ceilings; asymmetric arms `box_asym` / `ramp_asym` / `fixed_asym` (mass/CoM/joint 2.0; push, friction, latency 1.5) from the sweep; delay-buffer check sized from the latency ceiling. Suite 1,677 passed. |

lucid repo: `tools/physical_signal_audit.py` (+ receipt
`receipts/analysis/lucid_physical_signal_audit_20260902.json`),
`tools/run_channel_sweep.sh`, `tools/analyze_channel_sweep.py`,
`tools/run_expansion_prototype.sh`, `tools/run_expansion_prototype_scoring.sh`,
`receipts/manifests/lucid_expansion_prototype_preregistration_20260902.json`
(sha256 prefix `7d8f9bb6851d7ec2`), plan addendum §8, paper section 02 rows.

## 3. Findings today

### 3.1 Body-grounded signals (zero GPU)

Anchoring at fixed λ=1 (five runs, Spearman vs iteration, sign = improving
direction), authority in the two collapses (Pearson r of applied λ vs signal
over the descent), and difficulty response on fourteen frozen-policy ladders:

| signal | anchoring ρ (mean) | reversals | late-quarter range | r(λ) rg8601 / s4rg8600 | ρ vs λ_eval (14 ladders) |
|---|---|---|---|---|---|
| time-out rate | +0.99 | 4.6 | 2% | −0.62 / −0.80 | (saturated in-envelope) |
| mean return | +0.97 | 3.2 | 8% | −0.73 / −0.94 | — |
| latent gap p90 | −0.04 | 19.2 | 32% | −0.03 / +0.04 | — |
| **foot slip / step** | −0.53 | 17.0 | 6% | **+0.75 / +0.71** | **+1.00 on 14/14** |
| contact impulse | −0.74 | 16.0 | 10% | +0.06 / +0.33 | — |
| torque saturation | −0.31 | 7.2 | 27% | −0.42 / +0.66 (sign flips) | sign flips across arms |
| energy (work) | **+0.65** (rises with competence) | 15.6 | 6% | +0.76 / +0.97 | +1.00 |
| action rate | +0.71 (rises) | 6.8 | 2% | +0.47 / +0.88 | — |

Reading: foot slip is the only body signal with authority and a consistent
difficulty response, but it is weakly anchored, saturates, and improves when λ
is cut (relief +34% / +11%) — i.e. it rewards evacuation like return. Energy
and action rate rise with competence, so an "actuator margin" built on them
would call the best policy the most exhausted. Nothing beats time-out on
anchoring. Conclusion unchanged: survival at the probe under a monotone
actuator. Caveat: evaluator batch diagnostics include auto-reset envs after
termination (contamination the receipts already flag).

### 3.2 Single-channel attribution (eval-only, in flight at hand-off)

Complete at 00:59 EDT: 55 cells, receipt
`receipts/analysis/lucid_channel_attribution_20260902.json` (source receipts
`$LUCID_ROOT/manifests/channel_sweep_20260902_001226/`). Success on the
scalar ladder (all channels together) next to the single-channel marginals
(one term widened from the λ=1 envelope, the other four at λ=1, latency 0):

| arm (seed 8600) | phys_100 | phys_150 | phys_200 | fric 1.5 | mass 2× | mass 3× | CoM 2× | CoM 3× | joint 3× | **push 2×** | **push 3×** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fixed | 0.994 | 0.924 | 0.820 | 0.973 | 0.992 | 0.949 | 0.988 | 0.988 | 0.990 | **0.912** | **0.746** |
| ratchet | 0.990 | 0.908 | 0.842 | 0.957 | 0.990 | 0.938 | 0.992 | 0.982 | 0.986 | **0.928** | **0.770** |
| lucid_rg (held) | 0.994 | 0.932 | 0.795 | 0.949 | 0.980 | 0.951 | 0.986 | 0.975 | 0.980 | **0.910** | **0.705** |
| s4_rg (collapsed) | 0.969 | 0.732 | 0.518 | 0.855 | 0.873 | 0.682 | 0.928 | 0.818 | 0.955 | 0.811 | 0.570 |
| off | 0.910 | 0.564 | 0.334 | 0.775 | 0.795 | 0.643 | **0.654** | **0.393** | 0.891 | 0.736 | 0.443 |

Reading, for the three healthy DR-trained finals:

- **The failure surface is anisotropic, and the axis is push.** At twice the
  range, push costs 6–8 points; friction 2–4; mass, CoM and joint offsets
  under 1.5 points each. At three times the range mass/CoM/joint are still
  ≥0.938 while push is 0.705–0.770.
- **Friction is not the driver the scalar ladder made it look like.** The
  friction floor clamps at 0.05 from λ≈1.385, and friction alone at 1.5 costs
  only 2.7 points (fixed) — the paper's "the biggest drop lands at phys_150"
  is a statement about the joint cell, not about slip.
- **The scalar drop is super-additive.** For fixed at 2.0 the marginals sum to
  0.111 of loss; the joint cell loses 0.174. About six points is interaction
  — no axis-aligned probe sees it, which is an argument for keeping a joint
  corner in the probe set even in a per-channel design.
- The ratchet's channel profile is fixed's profile (distributionally identical
  arms), as expected.

For the weak policies the picture is different: `off` breaks on CoM alone
(0.654 at 2×, 0.393 at 3×) and the collapsed arm on push and mass. Anisotropy
is a property of the policy, not of the physics, which is the case for
measuring it online rather than hard-coding it.

What it implies for the box: with every ceiling at 1.5 the box will widen
friction, mass, CoM and joint offsets almost immediately (their probes pass)
and spend its evidence on push — i.e. it should reach fixed_150's support on
four channels within a few hundred iterations and differ from gate_150 mainly
in *when* push widens. The more interesting arm is `box_asym`: cheap channels
allowed past 1.5 (they have headroom to 3×), push and latency held at 1.5,
against an open-loop `ramp_asym` with the same per-channel ceilings (M5).
Both need per-channel ceilings in the driver; see plan §8.4.

Single seed, one clip, 512 episodes per cell (paired noise ≈2–3 points on one
cell); the ordering of channels is far outside that noise, the exact sizes
are not.

## 4. How to run the next thing

1. When Phase 2 releases the GPU:
   `nohup bash tools/run_expansion_prototype.sh --execute > $LUCID_ROOT/outputs/expansion_prototype_driver.log 2>&1 &`
   (eight arms × 2,000 iterations from the fixed@s8600 final, ~10.7 GPU-h;
   `--modes` trims; the driver refuses while a trainer holds the card). The
   preregistration plus amendment
   (`receipts/manifests/lucid_expansion_prototype_amendment_20260902.json`)
   fix the endpoints: the five 1.5 arms on {phys_175, phys_200}; the three
   asymmetric arms on the per-channel 3× panel {mass, CoM, joint} with push
   at 2×/3× reported, and the scalar band labelled in-support for them.
2. Then `bash tools/run_expansion_prototype_scoring.sh <training receipt> --execute`
   (15 cells × 5 arms, ~45 min).
3. Decide with the preregistered rules R1–R5; the box's mechanism is read from
   its `curriculum_*.jsonl` (`frontier_vector`, `active_channel`, `fired`,
   `withheld`, `channel_expansions`) — a stalled box is a result, not a loss.
4. Phase 2 readout as documented in `lucid-handoff-2026-09-01-phase2.md`
   (score with the CURRENT evaluator; `analyze_support_screen.py`; gate vs ramp
   is the decisive contrast).

## 5. Gotchas added today

- Any nohup driver must `source env/lucid_env.sh` (EULA, TMPDIR, venv,
  PYTHONPATH). `LUCID_GPU_WAIT_SECONDS` defaults to 1,800 s in `run_arm`.
- `pkill -f <driver name>` from an agent shell kills the agent's own shell
  (its command line contains the pattern); use `pgrep -f "name.s[h]"`.
- Evaluation beside a trainer is fine for metrics (frozen policy, seeded) but
  not for wall-clock; keep evals away from Phase 2 arm boundaries, where the
  launcher's 6,000 MiB free-memory gate runs.
