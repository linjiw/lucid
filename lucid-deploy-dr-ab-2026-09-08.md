# Deployment randomization against none, from scratch — September 8, 2026

One question: **what does our domain randomization buy a policy trained from scratch on three
motions, and what does it cost at nominal physics?**

Two arms, identical in budget, motions, seed, thresholds and launcher. Only the randomization
differs. This is a screening comparison at one training seed, not a superiority test — see
*Claim limits* below.

## The arms

| Channel | `off` | `fixed_deploy` |
|---|---|---|
| `randomize_rigid_body_mass` | nominal | λ 1.0 envelope |
| `base_com` | nominal | λ 1.0 envelope |
| `add_joint_default_pos` | nominal | λ 1.0 envelope |
| `physics_material` | nominal | λ 1.0 envelope |
| `randomize_action_delay` | `[0, 0]` = 0 ms | λ 1.5 → `[0, 12]` steps = **0–60 ms** |
| `push_robot` | `[0, 0]` | λ 3.0 → **±1.5 m/s** planar, ±0.6 m/s vertical, ±1.56 rad/s roll-pitch, ±2.34 rad/s yaw, redrawn every 1–3 s |

`fixed_deploy` is a fixed-mode arm with `fixed_lambda = 3.0` and `ARM_TERM_CAPS` pulling every
channel except `push_robot` back down — four physics channels to 1.0, latency to 1.5. The scalar
ceiling is therefore reached on **push alone**, so a difference between the arms cannot be
attributed to a wider mass, CoM, joint or friction envelope. The channel sweep already found those
three nearly free (origin scores 0.949 / 0.988 / 0.990 at 3×) and friction physically clamped near
λ 1.385; push is the binding channel, scoring 0.746 at 3×.

`off` applies λ = 0, which collapses every range to its nominal. Verified in code rather than
assumed: `dr_curriculum.py` takes an `elif self.mode == "off"` branch calling `_apply(0.0)`, and
`_mode_lambda` returns `0.0`, so the `fixed_lambda = 1.0` still present in its command line is
never read.

Note what "fixed" still means. `dr_scaling.scale_range` nests every range around its nominal and
every term is reset-mode, so a 3.0 push envelope still delivers near-nominal episodes. This arm
**widens support; it does not concentrate it** — the distinction this programme's own
"fixed DR is already a curriculum" finding turns on.

## Two guards that fail closed

**The delay buffer.** `--max-delay 12` is mandatory. The delayed-actuator buffer clamps a drawn
delay to its capacity *without error*, so `--max-delay 8` would have trained 1.0× latency while the
telemetry claimed 1.5×. `build_command` now refuses the launch and names the required value.

**The held-out cells.** `ch_push_350` and `ch_push_fric_350_150` sit above the 3.0 the treated arm
practises, so they remain genuine extrapolation for both arms.

## Motions

`pools/subsets/m3_long8s_a`, built by `make_training_subset.py` from the **adaptation** partition
(receipt `manifests/training_subset_m3_long8s_a.json`, keys sha256 `a686f955…`):

| Clip | Duration | Family | arm std / leg std |
|---|---|---|---|
| `walk_arc_cw_stop_001__A047` | 8.667 s | walk | 0.047 / 0.175 |
| `walk_ff_stop_270_R_very_slow_001__A445_M` | 9.167 s | walk | 0.020 / 0.125 |
| `crouch_idle_004__A246` | 8.133 s | crouch | 0.042 / 0.015 |

Roughly twice the 4.03 s of `walk_hands_on_back_loop_002__A066_M`, the only from-scratch testbed
this programme has demonstrated learnable. All have quiet arms (reference 0.039 for hob002), so the
wrist half of `ee_body_pos` stays near zero and foot placement remains the single axis of
difficulty. Two walk plus one crouch is the maximum family diversity available at ≥ 8 s in
adaptation.

### A rejected selection, recorded

The first plan used the three longer clips of the September 7 long-motion screen —
`walk_arc_cw_loop_R_002__A229` (10.63 s), `walk_sideway_135_loop_003__A037` (11.23 s),
`neutral_stoop_down_R_001__A104` (8.17 s). Both reasons for rejecting them are measurement facts,
not preferences:

1. **They are the evaluation instrument.** All three are assigned `dev` in
   `split_debug512_content.json`. `make_training_subset.py` refuses to build a training subset from
   `dev` or `test` in as many words — *"that partition is the evaluation instrument"*. A subset
   assembled by hand bypasses that guard, and `run_curriculum_comparison.py` applies no partition
   check and no existence check to `--motion-file`, so the dry run exits 0 and the campaign would
   have leaked without a word. The hand-built directory was deleted.
2. **Two exceed the episode cap.** `base_env.yaml:31` sets `episode_length_s: 10.0`; with
   `decimation: 4` and `sim_dt: 0.005` that is 500 policy steps, and clips are resampled to
   `target_fps: 50`, so the cap is exactly 10 s of clip time. No exp config and no script overrides
   it. A 10.63 s clip is truncated mid-clip and the `time_out` termination becomes unreachable from
   frame 0, so time-out rate stops being comparable to the hob002 baseline's 0.987.

The stooping clip additionally carries an arm-DOF std of 0.176, which reintroduces the
manipulation confound the quiet-arm criterion exists to avoid.

## The second curriculum, switched off

`commands/terms/motion.yaml` enables `adaptive_sampling` (Auto PMCP), which reweights motion
sampling toward clips that fail. On a three-clip pool that reweights a three-element simplex, and
the two arms fail on **different** clips — so left on, they would train on materially different
effective clip mixtures, an uncontrolled between-arm difference recorded nowhere in the receipt.

`--adaptive-motion-sampling off` pins uniform exposure. Read back from the running arm's resolved
Hydra config rather than asserted: `adaptive_sampling: {'enable': False, …}`.

Shipping an A/B with a second uncontrolled curriculum running underneath both arms would invite
exactly the objection the diagnostic paper spends its length answering.

## Evaluation

Evaluation is roughly 4% of training cost, so every axis that can rank this pair is scored.

**Why not the stock presets.** Every `dr_*` cell carries the full 0–40 ms latency envelope, so it
moves two factors at once. That was survivable when both arms had been fine-tuned from a policy
trained with latency; the no-DR arm here has never seen latency at all, and a ladder that floors the
control ranks nothing. `latency_60ms` reads 0.00% for every arm ever measured, the untrained origin
included.

- `phys_000 … phys_300` — the five physics channels, **latency pinned to zero**. The axis on which
  a no-DR arm can be scored honestly.
- `lat_10ms … lat_120ms` — latency alone on nominal physics. `lat_60ms` is exactly the treated
  arm's trained ceiling; 80/100/120 ms are held out.
- `ch_push_200/300/350` and the push×friction pairs — the channel the treated arm actually
  practised, with the 350 cells above what it trained on.

**Panels.** The evaluation callback slices success and progress to the first `num_unique_motions`
environments and freezes the rest mid-episode, recording them as `terminated=False` with
`progress < 1` — censored *and* mislabelled, biased toward overstating success. A literal
three-motion panel is therefore three Bernoulli trials. Instead: one k128 alias panel per training
clip (`panel_arcstop047_k128`, `panel_ffslow445_k128`, `panel_crouch246_k128`), plus the frozen
102-clip dev partition.

The k128 panels alias the **training** clips: they are in-distribution difficulty curves, not a
generalization claim. The dev partition is unseen motions from the same 512-clip pool, so it is
fresh-physics robustness on unseen motions — still not a claim about a new distribution.

## Claim limits

**One training seed.** The measured between-seed effect on absolute capability in this programme is
**7.8 points**, larger than any margin this contrast is likely to produce. The comparison is
paired — same initialization, same motions, same budget, only the randomization differs — which
makes it a clean *descriptive* contrast, but it cannot separate the treatment from a seed-specific
interaction. **No superiority language is licensed.** Escalating to seeds 8601 and 8602 would cost
a further ~26 GPU-h and is the prerequisite for a directional claim.

Neither arm has a recovery result: no band, dwell or horizon has been frozen anywhere in this
project, so no policy has passed or failed a recovery test.

The push is a root **velocity increment** in m/s written into simulator state. It names no impulse
in newton-seconds, because the call carries no mass, no duration and no contact point.

## Supporting changes

| Change | Why |
|---|---|
| `_install_run_config` in the driver | `eval_agent_trl` looks for `config.yaml` beside the checkpoint then its parent, and otherwise proceeds on CLI overrides alone, which cannot describe the universal-token architecture. A from-scratch arm could previously be neither ONNX-exported nor evaluated until someone placed the file by hand. Each arm now gets **its own** resolved config, and the path is recorded in the receipt. The evaluator's fallback symlinks one config beside every checkpoint of a campaign, which is how arms have ended up pointing at a run directory from a different day. |
| `fixed_deploy` added to the evaluator's `MODES` | `--modes off fixed_deploy` was an argparse error at scoring time. |
| `export_arm_onnx.sh` | The one GPU step between a checkpoint and both MuJoCo and any future runner. Refuses to export without `config.yaml`; gates the result on input `obs_dict [1, 1570]` and output `action [1, 29]`; records the sha256, because the filename is `global_step`-derived and does not identify the weights. |
| `mujoco_sweep.py --arms-json / --arm / --clip / --py` | The arm table was five hardcoded absolute ONNX paths and the clip was hardcoded to hob002. |
| `mujoco_sweep.py` cache guard | Each rollout now records the sha256 of the ONNX that produced it and the clip it tracked; a cached result whose stamp differs is discarded. Arm keys are stable *names*, so re-pointing one at a retrained checkpoint and reusing `--out` previously returned the previous policy's numbers in silence. |
| `mujoco_story.py` ledger `.get()` | A new arm raised a bare `KeyError`. It now renders without the Isaac cross-reference overlay, which is the honest outcome — inventing a ledger row would caption it with another policy's number. |
| `tests/test_mujoco_sweep.py` | The sim2sim path had no test of any kind. |

## Sim2sim path, validated before the checkpoints exist

The MuJoCo path was exercised end to end on a historical checkpoint
(`fixed`, seed 8600, from the 2026-08-29 campaign) so that a broken pipeline would be found now
rather than after 13 GPU-hours. Two seeds per cell, lambda = 0, all channels — a spot check, not a
measurement.

| Policy | Clip | lambda 0 |
|---|---|---|
| historical `fixed_s8600` | `walk_hands_on_back_loop_002__A066_M` (its own pool) | **2/2 pass** |
| historical `fixed_s8600` | `walk_arc_cw_stop_001__A047` (a new training clip) | **0/2 pass**, falls at 4.4 s |

The control reproduces the historical receipt, which records 32/32 at lambda = 0 for every arm, so
the pipeline, the observation construction, the joint permutation, the gain table and the reset
convention are all intact under the new `--arms-json` / `--clip` flags.

The second row is the informative one: an existing 512-clip policy cannot hold one of the new
clips even at nominal physics. The three chosen motions are therefore genuinely unsolved by what
this project already has, which is the headroom the A/B needs. It is two rollouts, so it bounds
nothing — it rules out "these clips are already trivially solved", not much more.

The cache guard was also demonstrated on real data rather than only in tests: an identical re-run
returned in 0.050 s (cache hit), while pointing the same arm key at a different checkpoint spent
53 s of CPU recomputing and rewrote the stamp from `80ae6c3e…` to `37090c76…`. Before the guard,
that second case returned the first policy's numbers under the second policy's name.

## Defects found and fixed before the result exists

An adversarial review of the campaign machinery raised 50 findings; 10 survived refutation, and
they reduce to four distinct defects. All four are fixed and covered by tests that fail when the
fix is reverted.

**1. Disabling adaptive sampling killed capsule export.** The first launch ran both arms to
iteration 250 — the first `--horizons` capsule — and died there with
`CapsuleIntegrityError: native_sampler_state is missing ['adp_samp_num_episodes',
'adp_samp_num_failures']`. `motion_lib.get_state_dict` returns an empty dict by contract when
adaptive sampling is off, and `save_capsule` treated that absence as corruption. The guard exists
for a real reason — those counters are indexed by global bin id and are silently wrong against a
different pool — but a run that never had them has nothing to reproduce. `save_capsule` now
accepts an empty sampler state and records `adaptive_sampling: False` so a reader never infers
"off" from "empty"; a **partial** counter set still raises, which is the corruption the guard was
written for. Attempt 1 is preserved at
`outputs/deploy_dr_ab_attempt1_capsule_failure.log`.

**2. The evaluator would have aborted on every cell.** `ensure_checkpoint_configs` required every
checkpoint's `config.yaml` to hash-match one `--training-config` source. Once the driver installs
each arm's *own* resolved config, the two arms necessarily differ, so the gate raised before the
first cell. The two changes were individually reasonable and jointly fatal. A config already
installed beside a checkpoint is now treated as that arm's own provenance and recorded per
destination in `installed_sha256`; the single source stays as the fallback for checkpoints that
have none.

**3. The latency ladder could not run at all.** `run_deploy_dr_ab_eval.sh` passed `--max-delay 12`
while `lat_80ms`, `lat_100ms` and `lat_120ms` need 16, 20 and 24 physics steps.
`assert_latency_within_capacity` checks the whole preset list before the first cell launches, so
the entire nine-rung ladder aborted — taking the six in-capacity rungs with it — and the script
runs without `set -e`, so it would have logged `exit=1` and continued, yielding physics and push
curves and **zero latency data**. The latency invocations now pass `--max-delay 24`; physics and
push stay at 12 so their receipts are unchanged.

**4. The MuJoCo cache guard had a hole on another axis.** The stamp recorded the ONNX hash and the
clip but not `--channels`, which zeroes whole physics channels at the same lambda and appears
nowhere in the run path. Two sweeps into the same `--out` differing only in the channel mask would
have collided — the same silent-wrong-number failure the guard was written to close. The mask is
now in the stamp.

Two of the thirteen MuJoCo tests were also tautological under mutation testing: one compared
`resolve_arms(...)` against the dict it reads from, and one passed with `js.unlink()` deleted.
Both are rewritten, and all three mutants are now killed.

## What is still true of sim2real

Unchanged by this campaign, and worth restating because "prepare the sim2real pipeline" is easy to
over-read. The export path exists and has been exercised. Joint order, kp/kd, `default_angles`,
action scale and the 50 Hz control rate all agree exactly between training and the vendored C++
runner. But that runner has **never been built or run** here — no `build/`, no `CMakeCache.txt`, no
logs. There is no ONNX-versus-Isaac value-level parity test. The one shipped observation config
naming the LUCID export lists eight term names absent from the runner's 76-entry registry and would
throw at initialization. And no hardware safety infrastructure exists: the stop path is a software
boolean, with no hardwired e-stop, no fall-arrest rig and no fallback controller.

The deeper obstacle is unchanged: the deployed observation contains **no horizontal position term
at all**, and the proposed repair is a motion-library lookup indexed by the integer simulator clock
minus the simulator's own body position — absolute, drift-free, and unavailable on a real G1.

## Provenance

- SONIC HEAD `22475f355485742fa211db1d1b4c8e5640ec3589`, working tree **dirty**: `fixed_deploy`,
  the driver changes and all three campaign scripts are uncommitted. A `git stash` or fresh clone
  deletes the treated arm.
- Launch receipt: `$LUCID_ROOT/outputs/deploy_dr_ab_launch.json`.
- Subset receipt: `$LUCID_ROOT/manifests/training_subset_m3_long8s_a.json`.
- Panel receipts: `$LUCID_ROOT/manifests/replicate_panel_panel_{arcstop047,ffslow445,crouch246}_k128.json`.
- CPU suite: **1879 passed** in `tests/practice_utility/` (1852 pre-existing plus 27 new), and
  **21 passed** in the root `tests/`. Every fix above is mutation-tested: reverting it fails
  the test that names it.
