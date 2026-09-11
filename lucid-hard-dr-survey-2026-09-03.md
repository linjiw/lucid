<!-- Produced 2026-09-03 by a 45-agent survey+screen of every DR / sim2real knob
     reachable in IsaacLab 2.3.2 / IsaacSim 5.1.0 / SONIC for the G1 tracking task.
     7 survey lenses -> triage (98 candidates -> 14) -> 36 adversarial screens
     (implementable / barrier / real-world) -> synthesis. Not yet reviewed by a human. -->

# Hard DR terms for G1 whole-body tracking: what is left, what is real, and what to run

**Bottom line up front.** Twelve candidates were screened by three independent lenses. All twelve passed implementability. Ten of twelve passed real-hardware grounding. **None passed the barrier lens.** That result is not a survey failure — it is the finding, and it has a specific cause: the defusing property is not *which parameter* we randomize, it is *the shape of the draw*, and no candidate as proposed changes that shape.

Three measurement defects, verified in source today, mean several of this project's own nulls are uninformative and can be fixed for minutes of GPU:

| # | Defect | Consequence | File |
|---|---|---|---|
| **D1** | `randomize_rigid_body_material` draws **one bucket per collision shape**, not per body | Each foot has 7 collision capsules, so foot-effective μ is the mean of 7 i.i.d. draws: SD 0.1418, not 0.3753. μ=0.30 at the foot is **4.58σ**. No run in this project has ever delivered a low-μ foot. | `IsaacLab/.../envs/mdp/events.py:262` |
| **D2** | `randomize_action_delay` calls `buffer.reset(env_ids)` after `set_time_lag` | Correct at an episode boundary; in **interval mode** it zeroes `_num_pushes`, so `__getitem__`'s `torch.minimum(key, _num_pushes-1)` collapses the realized lag to **zero** and ramps back. 12–30% of episode wall-time runs below the commanded lag. Every jitter/burst cell is confounded *easy*. | `gear_sonic/research/practice_utility/events_reset_safe.py:~417`; `IsaacLab/.../utils/buffers/circular_buffer.py:96-110,168` |
| **D3** | Actuator draws are **per joint**, not per env | `step = torch.rand(base.shape)` with `base.shape = (n_envs, n_joints)`. So `act_effort_150` = per-joint U[0.25, 1.0]: E[min over 10 leg joints] = **0.318**, and P(no leg joint below 0.40) = **0.107**. Every actuator "range" result describes a robot with 2–3 weak joints, not a uniformly weak robot. | `gear_sonic/research/practice_utility/actuator_dr.py:255-259` |

The single recommendation: **effort limit as a POINT on all 29 joints, from scratch, at a severity located first by a frozen-policy point screen that costs 15 minutes.** No point-valued DR target has ever been trained in this project, and the point is the only form that expresses simultaneous derating — which the ankle CoP arithmetic in §5 turns into a computable barrier/unlearnable boundary rather than a guess.

---

## 1. What we already schedule, and why it is soft

Preset `gear_sonic/config/manager_env/events/tracking/lucid_curriculum.yaml` (six channels) and `.../lucid_actuator.yaml` (those six plus four).

| Channel | Term | λ=1 range | Draw granularity | Mode | Term file |
|---|---|---|---|---|---|
| Rigid-body mass | `randomize_rigid_body_mass` | ×[0.8, 1.5] on `.*wrist_yaw.*\|torso_link` (3 of 30 bodies) | per env × per body | reset | `terms/randomize_rigid_body_mass.yaml` + preset override |
| Torso CoM | `base_com` | x ±0.025, y/z ±0.05 m on `torso_link` | per env (one xyz, broadcast) | reset | `terms/base_com.yaml` |
| Ground physics material | `physics_material` | static [0.3, 1.6], dyn [0.3, 1.2], rest [0.0, 0.5], `num_buckets: 64`, bodies `.*` | per env × **per collision shape** | reset | `terms/physics_material.yaml` |
| Joint default offset | `add_joint_default_pos` | +[−0.01, 0.01] rad, all 29 joints | per env × per joint | reset | `terms/add_joint_default_pos.yaml` |
| Base velocity push | `push_robot` | x/y ±0.5 m/s, z ±0.2, roll/pitch ±0.52 rad/s, yaw ±0.78; every 1–3 s | per env × per component | interval | `terms/push_robot.yaml` |
| Actuation latency | `randomize_action_delay` | [0, 8] physics steps = 0–40 ms | per env × **per actuator group** (5 groups) | reset | `terms/randomize_action_delay.yaml` |
| Joint effort limit | `randomize_joint_effort_limit` | ×[0.5, 1.0] of peak (139/88/50/25/5 N·m) | per env × per joint | reset | `terms/randomize_joint_effort_limit.yaml` |
| Joint Coulomb friction | `randomize_joint_friction` | +[0, 0.05] × each joint's own rating | per env × per joint | reset | `terms/randomize_joint_friction.yaml` |
| Joint armature | `randomize_joint_armature` | ×[0.7, 1.6] | per env × per joint | reset | `terms/randomize_joint_armature.yaml` |
| Joint velocity limit | `randomize_joint_velocity_limit` | ×[0.6, 1.0] | per env × per joint | reset | `terms/randomize_joint_velocity_limit.yaml` |

### The structural property

`dr_scaling.scale_range` (`gear_sonic/research/practice_utility/dr_scaling.py:100-131`) is affine about a nominal declared in `RANGE_NOMINALS` (`:48-69`): `[c − λ(c−lo), c + λ(hi−c)]`. Every term is mode `reset` or `interval`. This much is already recorded ("nested supports + per-episode redraws"). The sharpening this survey adds is the second axis: **the draw is independent per *dimension*, not just per environment.** Three consequences, all verified today:

1. **Nesting, per parameter.** Supports at intensity *s* sit strictly inside the support at 1. This rules out the "fixed DR withheld a value the curriculum introduces" explanation. It does not, on its own, explain the nulls.

2. **Per-dimension independence concentrates episode difficulty by CLT.** The typical "full intensity" robot is not a uniformly hard robot; it is a near-nominal robot with two or three outlying joints. Widening a range fattens the tails without moving the median episode. This is why every channel behaves like a dose-response cost rather than a threshold.

3. **In two channels the independence destroys the quantity the channel claims to control.** Friction: 7 collision capsules per `ankle_roll_link` (`main.urdf`, lengths 0.05/0.167/0.182/0.186/0.182/0.167/0.05, radii 0.008–0.010, y at 0, ±0.010, ±0.018, ±0.026, all z = −0.025), each drawing its own bucket, so the foot's tangential capacity is ≈ N·mean(μᵢ) with SD/√7 (**D1**). Effort: `act_effort_150`'s "[0.25, 1.0]" is 29 independent draws (**D3**). The channel sweep and the actuator screen both measured a marginal distribution the robot never actually experienced as a coherent plant.

**A fourth, separate correctness item:** the restitution third of the material channel is inert. `modular_tracking_env_cfg.py:322-330` sets terrain `restitution_combine_mode="multiply"` with restitution at `RigidBodyMaterialCfg`'s default 0.0, so *e*_eff = 0 regardless of the [0.0, 0.5] draw. One third of one scheduled channel's parameters has never affected the simulation.

The escape these three imply is not a bigger range. It is a **point with a shared draw** — which is exactly the project's own recorded prediction ("a curriculum needs a CONCENTRATED target"), and which has never been trained.

---

## 2. The knobs we are NOT using

Ordered by the survey ranking. Every row cites a path read in this session or by a screener.

| # | Knob | Category | API / file | Runtime-writable? | Current value | Proposed hard setting | Mechanism of hardness | Real-hardware anchor | Barrier vs unlearnable |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Foot-only friction as a POINT**, `num_buckets: 1` | Tier A | `randomize_rigid_body_material`, `IsaacLab/.../envs/mdp/events.py:155,243,283`; per-body branch `:205-224`; write via `set_material_properties` (`omni/physics/tensors/impl/api.py:2779`) | **Yes**, per env, reset or interval | bodies `.*`, [0.3,1.6]/[0.3,1.2], 64 buckets → foot-effective μ ≈ 0.95 ± 0.14 | `body_names=[".*_ankle_roll_link"]`, static=dyn=μ, `num_buckets: 1`; μ ladder 0.50/0.40/0.30/0.20 | Coulomb cone is non-differentiable; stick→slip changes the contact Jacobian. `num_buckets: 1` removes the √7 averaging | Wet lobby tile / dusty polished concrete μ≈0.2–0.3; ANSI A326.3 requires wet DCOF ≥ 0.42 *(external)* | **Barrier** above μ_req; **unlearnable** below. μ_req from CoM accel is a *lower* bound — single support passes all horizontal force + yaw moment through one foot |
| 2 | **PD stiffness & damping, scaled independently** | Tier A/B | `randomize_actuator_gains`, `events.py:541,587`; writes `write_joint_stiffness_to_sim` (`articulation.py:652`), `write_joint_damping_to_sim` (`:681`) | **Yes**, per env × per joint, reset | **Not randomized at all** — derived once: K = J·ω², D = 2ζJω, ω = 2π·10, ζ = 2.0 (`robots/g1.py:15-26`). Knee K=99.10, ankle K=28.50 | One **correlated scalar per env**; damping pinned at 0.30× nominal; ankle+knee only | ζ_eff crosses a threshold in *pole location* | Sibling stack runs hip (1.51×K, 0.32×D) — inside the proposed box (`gear_sonic/utils/mujoco_sim/wbc_configs/g1_29dof_sonic_model12.yaml:85-91`) | **Barrier**, low probability. Unlearnable only if the delayed closed loop limit-cycles at contact |
| 3 | **Latency process**: common-mode + concentrated + observation staleness | Tier C/D | `DelayedImplicitActuator` (`gear_sonic/envs/manager_env/mdp/actuators.py:11-91`); obs side needs `ModifierBase` (`IsaacLab/.../utils/modifiers/modifier_base.py:46`) | Actuation **yes** (5 ms grain); obs side **needs ~60 lines**, 20 ms grain | [0, 8] steps, `coupling: independent`, actuation only. `grep obs_delay` → nothing | `delay_range: [8.0, 10.0]`, `coupling: "common"`, + 1 policy step common obs staleness. See §4 | Removes the easy sub-population from the *support*; one shared bus | One DDS `LowCmd` carries all 29 motors with one CRC; all attitude obs come from one `imu_state().quaternion()` (`g1_deploy_onnx_ref.cpp:2666-2678, 2895`) | **Barrier**, ~2 rungs of headroom. Sustained 60 ms is a measured 0.000 floor |
| 4 | **Joint stiction, μ_s > μ_d** (breakaway ratio) | Tier A | `write_joint_friction_coefficient_to_sim(..., joint_dynamic_friction_coeff=, ...)` at `articulation.py:871`; docstring `:888-892` | **Yes**, per env × per joint, reset | μ_s = μ_d always (`actuator_dr.py:139-152` `also_write`); URDF declares zero `<dynamics>` (`grep -c` = 0) | μ_d ∈ [0.005, 0.02] of rating; μ_s = ratio·μ_d, ratio ∈ [1.0, 2.0] | Hysteresis: same command, different response depending on motion history | Unitree's own MJCF declares `frictionloss="0.2"` N·m (`motionbricks/assets/skeletons/g1/g1_29dof.xml:5-19`) — 0.14% of the knee rating | **Barrier**, low probability. Unlearnable if μ_s exceeds gravity-load PD authority |
| 5 | **Command dropout**, hold-last-target | Tier C/D | New `JointPositionAction` subclass; seam is `ActionManager.process_action` (`action_manager.py:372-393`), the only 50 Hz boundary | **Yes**, per env, reset | Nothing models a lost command | Whole-body drop of **whole control ticks** (20 ms), p ≤ 0.02, bursts 1–2 ticks | Applied ≠ sent; the drop is hidden from obs *and* from `action_rate_l2` | `LowCommandWriter` republishes the latest `MotorCommand` at 500 Hz — a missed 50 Hz deadline *is* hold-last (`g1_deploy_onnx_ref.cpp:2661-2683`) | **Barrier** by construction — plant unchanged, so it can never be unlearnable |
| 6 | **Persistent sensor bias**: encoder zero + coherent IMU rotation | Tier C/D | `NoiseModelWithAdditiveBiasCfg` (`utils/noise/noise_cfg.py:97-113`), reset per env at `observation_manager.py:301-312`, applied **before** the history append (`:392-424`) | **Yes** per env, but **outside `dr_scaling`** (it walks the event manager only) | All noise zero-mean, i.i.d. per step, under a 10-frame stack: `gravity_dir` ±0.05, `joint_pos` ±0.01 rad | `joint_pos` bias ±0.02–0.035 rad, `operation="abs"`; IMU as **one** rotation applied to every attitude-derived term | A constant offset survives every filter; encoder zero is not compensated by the action offset | Deploy subtracts hard-coded `default_angles` (`g1_deploy_onnx_ref.cpp:2830-2831`); readapt triggers at 0.10 rad mean lower-body error | **Barrier**, low probability. Best *sim2real* item in the survey |
| 7 | **Terrain amplitude + per-env levels** | Tier E | `TerrainImporter.update_env_origins(env_ids, move_up, move_down)` (`terrain_importer.py:314-329`) — the only per-env discrete monotone index in the API | Level assignment **yes** (GPU tensor); the **mesh is startup-only** | `terrain_type: trimesh` (not a plane); boxes ±1–5 mm, `random_rough` = **{0, 20 mm}** (see below), `max_init_terrain_level: 10` already set | Only worth it as **pyramid_stairs**, currently commented out at `terrain.py:21-36` | Contact timing is discontinuous in height; exposure is **endogenous** | Door sills ≤19 mm, cable covers/mat edges to ~25 mm *(ANSI/accessibility code, external)* | **Barrier** for stairs; **unlearnable** above ~8–10 cm (flat-ground clip) |
| 8 | **Effort limit as a POINT** on all 29 joints | Tier B/D | `write_joint_effort_limit_to_sim` (`articulation.py:805`); arms coded at `run_curriculum_comparison.py:474-527` | **Yes**, per env × per joint, reset. Registered in `RANGE_NOMINALS` (nominal 1.0) | ×[0.5, 1.0], **per joint** | `[0.40, 0.40]` all joints, every env, every reset. Ladder 0.50/0.40/0.30 | Simultaneous derating removes the per-joint averaging; binds at the **ankle** | Air-cooled servos sustain ~25–30% of peak continuously *(external)*; deploy sends `tau_ff = 0` so the driver's clip is invisible to the policy | **Barrier** at 0.40–0.50; **unlearnable** below ~0.30 (ankle CoP, §5) |
| 9 | **Initial-state desync** (joint velocity ON, wider pose) | Tier D | `TrackingCommandCfg.pose_range/velocity_range/joint_position_range/joint_velocity_range` (`commands.py:4149-4153`), consumed `:2996-3068` | Per env **yes** — but on the **command manager**, invisible to `dr_scaling` **and to evaluation** | `joint_velocity_range: [-0, 0]` ("turned off"); `joint_position_range` ±0.1 rad | Lower-body only: joint vel ±2.0 rad/s; better, a **phase offset** of *k* reference frames | Recovery is a different behaviour, not a perturbation of the tracking law | Deploy replans and sets `current_frame_ = 0` every 0.1–1.0 s with the robot mid-motion (`g1_deploy_onnx_ref.cpp:3210-3214`); measured pose mismatch 0.26–0.34 rad/joint | **Barrier**, low probability. Structurally **unmeasurable** today — see §6 |
| 10 | **Thermal derating** (endogenous torque budget) | Tier B/D | Built, **wired to nothing**: `gear_sonic/research/practice_utility/thermal.py`, `thermal_actuator.py` (+ 27 CPU tests) | Per-step write **yes**; but `ThermalState.lam` is a **scalar**, so it cannot join the strata dispatchers | Never run | Do not run as configured — see §6 | Endogenous, history-dependent, escapable only by a global change | Two temperatures/motor at 500 Hz; 90/85 °C hysteresis, TTS alert, CSV log; `elbowCrawling` documented as "more likely to overheat" (`docs/source/references/planner_onnx.md:123`) | **Barrier** in principle; **inverted** as configured |
| 11 | **Torque-speed derating** (DC-motor curve) | Tier B | `DCMotor._clip_effort` (`actuator_pd.py:295-308`); or per-step effort write | Startup swap (a) or per-step write (b). (b) can only impose a **symmetric** cap | Flat effort limit *and* a separate flat velocity limit; `articulation.py:776-786` confirms the velocity limit only **brakes** | Do not run — see §6 | Authority falls with speed | Back-EMF is real on every brushless joint | **Barrier** in principle; **inert** at every physically defensible setting |
| 12 | **Disturbance shape**: persistent wrench / push cadence | Tier D | `apply_external_force_torque` → `permanent_wrench_composer` (`events.py:1010-1043`); `WrenchComposer.set_forces_and_torques` (`utils/wrench_composer.py:221`) | Wrench **yes** per env (mode `reset` only — it is cleared on every reset at `articulation.py:215-216`). Cadence **no** | Instantaneous velocity push only | Do not treat as new — see §6 | A held bias has no nominal to return to | Documented deploy target is "G1 + Thor backpack"; no backpack link in `main.urdf` | **Neither (smooth)** for magnitude |

---

## 3. The hardness ladder

Grouped by *why* a thing would be hard, because the mechanism is what distinguishes the tiers — and because the barrier lens killed each tier for a *different* reason.

### Tier A — nonsmooth / discontinuous (stiction, backlash, contact-mode change)
**Members:** foot-friction point (#1), joint stiction ratio (#4), the terrain contact-mode component of (#7).

**What would count as evidence.** A **knee** in the return-vs-intensity curve — a discontinuity in dJ/d(intensity), not merely a steepening slope. Concretely: `success(intensity)` measured on a frozen policy at ≥4 rungs shows a step, and from-scratch `time_out` stays flat at the rung past the step while a staged arm's climbs.

**What falsifies it.** A smooth convex J. This tier has already been falsified once with real numbers: `act_friction` gives 0.0 / −0.78 / −2.73 / −12.30 across 0.5/1/2/3, convex, no knee, and ρ = +0.90 with the existing scalar ladder — i.e. it restates general robustness. The general principle: **a nonsmooth plant does not imply a nonsmooth objective.** A contact-level discontinuity integrated over 50 Hz control, a dense per-link reward, and 1024 environments produces an analytic return. It also falsifies if the conservative stationary policy (never demand more tangential force than the worst μ) is feasible and learnable — which for a walk clip it is.

**The one live question in this tier** is not the mechanism but the measurement: because of **D1**, no friction result in this project was measured on a foot that ever saw low μ. That is worth 12 minutes of GPU to settle (§5, Phase 1b), and nothing more until it reports.

### Tier B — capability removal (torque, speed, thermal budget)
**Members:** effort-limit point (#8), torque-speed (#11), thermal (#10), the existing velocity-limit channel.

**What would count as evidence.** The escape requires a **strategy change**, not an amplitude reduction — visible as a measurable gait statistic moving: double-support fraction, CoP excursion, step length, ankle-vs-hip torque share. Plus C1 ∧ C2: from-scratch fails at the severity, a staged arm reaching the same severity succeeds.

**What falsifies it.** Two ways. (i) A smooth monotone dose-response with the same gait — a weaker robot, not a different problem. (ii) The offline feasibility check showing the reference demands more than the setting supplies → **unlearnable**, and it must be reported that way. This tier carries the sharpest unlearnable risk *and* the sharpest computable boundary: capability removal contracts the feasible set without adding deception, so it can cross from "already solved" to "physically impossible" with no hard-but-learnable band in between. The instrument that locates the band is arithmetic, not GPU (§5).

**Why this tier is still the recommendation** despite failing the barrier lens: it is the only tier where the severity has already been measured live on frozen policies (−18.95 success points at `act_effort_150`, ρ = +0.50 with the existing ladder, i.e. a partly *new* axis), the arms are already coded, and the decision rules are already frozen.

### Tier C — partial observability & information delay
**Members:** observation staleness (#3), sensor bias (#6), command dropout (#5), single-joint encoder dropout.

**What would count as evidence.** The **conservative stationary policy must be infeasible.** Partial observability buys a barrier only when hedging does not work — when the agent must actually identify the latent to act at all.

**What falsifies it, and this tier is thinner than it looks.** Three independent leaks, all verified:
- The actor carries 200 ms of proprioception *and* its own action history (`actor_prop_history_length: 10` on `gravity_dir`, `base_ang_vel`, `joint_pos`, `joint_vel`, `actions`).
- The actor **also** receives `motion_anchor_ori_b` and `motion_anchor_ori_b_mf_nonflat` through the tokenizer group (`observations/tokenizer/unitoken_all_noz.yaml:7,12`) — a clean 6D attitude error computed from the *true* pelvis quaternion. A `gravity_dir`-only bias is therefore observable-around, not hidden. This is the decisive falsification of the tilt-bias arm as proposed, and it prescribes the fix: apply **one** rotation to every attitude-derived term.
- Hedging is usually feasible. A drop is a 20 ms window in which an ImplicitActuator PD keeps running inside PhysX against live joint state at 200 Hz — the robot is never open-loop.

The item in this tier that survives all three leaks is the **encoder-zero bias**, because it is a lie about a quantity nothing else measures, and because `add_joint_default_pos` — the term that looks like its twin — is self-consistent (it updates the action-manager offset, `mdp/events.py:44-46`) and is therefore nearly a re-parameterization in the policy's frame. That is why "joint defaults are free" and "encoder zero is free" are different claims and only the first has been tested.

### Tier D — persistent-within-episode or correlated draws
**Members:** the point form of #1, #4 and #8; a shared scalar in #2; concentrated latency in #3; #5, #9, #10, #12.

**This tier matters more than any single new parameter, and here is the precise reason.** §1 identified two separable defusing mechanisms: *nesting across episodes* and *per-dimension independence within an episode*. Every proposal in this survey attacks at most one. Persistence within an episode does **not** remove nesting across episodes — a held draw from a wide uniform is still a wide uniform. Removing the easy region from the **support** does. And a **shared** (single-scalar-per-env) draw removes the CLT concentration. Those are two distinct edits and both are needed:

```
range,  per-dimension  →  nested AND concentrated on easy      (all 10 current channels)
point,  per-dimension  →  simultaneous, but still per-dimension identical → effectively shared
range,  shared scalar  →  still nested; median episode is mid-support
point,  shared         →  neither nested nor CLT-concentrated  ← never run in this project
```

**What would count as evidence.** `fixed-at-a-POINT` fails from scratch while `fixed-at-a-RANGE` with a matched **mean** succeeds, at the same budget. That is the only experiment that isolates *shape* from *parameter*, and it is the direct test of this project's own leading explanation for every prior null.

**What falsifies it.** Point and range performing identically (→ shape is not the variable; look elsewhere), or the point failing because it is infeasible (→ unlearnable, C1 without C2). Note the trap the current code sets: `run_curriculum_comparison.py:521` builds `act_range` as `[min(nominal, target), max(nominal, target)]` = [0.40, 1.0], **mean 0.70** against the point's 0.40. As coded the contrast confounds shape with mean and cannot support the conclusion. Fix it with a third arm (§5).

### Tier E — task / terrain difficulty
**Members:** terrain amplitude (#7), reference perturbation, slopes.

**What would count as evidence.** A **spatially coherent, monotone** obstacle where partial success is impossible — a stair riser — combined with **endogenous exposure** (the policy's own foot placement selects severity, so a low-clearance policy stubs, terminates early, and never accumulates the trajectories that would teach clearance). That early-termination signal-truncation loop is a genuinely new mechanism and is the one thing in this survey that no other tier offers.

**What falsifies it, and does.** (i) **Spatial mixing.** Cell heights are drawn i.i.d. per 0.30–0.45 m cell (`mesh_terrains.py:307-308`), so the lip between adjacent cells is triangular on [−2h, 2h] **with its mode at zero**: E|lip| = 2h/3, ~25% of lips under 0.29h. Every episode delivers the full difficulty distribution several times per second per foot — spatial redraws at a *higher* frequency than per-episode ones. The truncation loop never closes. (ii) **The reference-clip floor.** The clip is flat-ground, so on uneven ground tracking error acquires an irreducible floor growing with amplitude — and a curriculum *cannot* remove an irreducible floor, since staged and fixed both terminate at the same terrain. Any degradation is confounded between "learning failed" and "the target is geometrically inconsistent with the ground." (iii) `random_uniform_terrain` **ignores difficulty** by its own docstring (`hf_terrains.py:29-30`), so ~1 column in 7 is level-invariant under `curriculum=True`.

The version with teeth — `pyramid_stairs`, `step_height_range=(0.05, 0.23)` — is the one every proposal excludes, and it is sitting commented out at `terrain.py:21-36`.

---

## 4. The single hardest thing we could do to latency

### 4.1 What our latency model does today

`DelayedImplicitActuator` (`gear_sonic/envs/manager_env/mdp/actuators.py:11-91`) holds three `DelayBuffer`s (positions, velocities, efforts) sized at `cfg.max_delay`; `compute()` pushes the setpoint and returns the lagged one, then delegates to `ImplicitActuator.compute`.

- **Granularity: 1 physics step = 5 ms.** `compute` runs inside the decimation loop at 200 Hz. Lags are **integers only** (`_time_lags` is `torch.int`, `delay_buffer.py:54`).
- **Per environment and per *actuator group* — never per joint.** `_time_lags` has shape `(num_envs,)`, and the G1 declares five `ImplicitActuatorCfg` groups (`robots/g1.py:239,277,285,293,301`), each becoming its own `DelayedImplicitActuator`. *(The brief's "per-joint independent" is incorrect; within a group every joint of a given env shares one lag.)*
- **Config:** `terms/randomize_action_delay.yaml` — `mode: reset`, `delay_range: [0.0, 8.0]` (0–40 ms), `distribution: uniform`, `coupling: independent`.
- **`max_delay` is a construction-time ceiling.** IsaacLab's `set_time_lag` would raise past capacity; **LUCID silently clamps instead** (`events_reset_safe.py:373, 385-386`: `group_high = min(high, capacity)`), so a mis-provisioned run trains a quietly smaller envelope with no error.
- **Actuation only.** `grep` for `obs_delay|observation_delay|obs_latency|sensor_delay|state_delay` across the repo returns **nothing**.
- **Jitter exists only as an *evaluation* preset** (`tracking/lucid_eval_latency_jitter.yaml`, `mode: interval`, `interval_range_s: [0.20, 0.50]`, `is_global_time: false`, `coupling: common`). Never trained on.

**And it is broken in interval mode (D2, verified in source today).** `randomize_action_delay` calls `buffer.reset(env_ids)` immediately after `set_time_lag`, justified in-code by "the buffer still holds targets built from the previous episode's joint-default offset" — an *episode-reset* argument. `CircularBuffer.reset` zeroes `_num_pushes`; `__getitem__` clamps `valid_keys = torch.minimum(key, self._num_pushes - 1)`; and `append` refills the whole ring on the first push. So **every mid-episode resample collapses the realized lag to zero and ramps it back over `lag` physics steps.** At `[0.20, 0.50]` s (40–100 physics steps) with lags ≤ 12, roughly **12–30% of episode wall-time runs below the commanded lag.** The existing "jitter process" implements a sawtooth, and every jitter/burst cell measured is confounded in the **easy** direction. Fix first; it is ~5 lines (`reset_buffers: bool = True`, passed `false` from interval terms).

### 4.2 How a real G1's latency actually behaves

Read from the shipped deploy source, not inferred:

- **Four unsynchronised, unpinned threads.** Input 100 Hz, Control 50 Hz, Planner 10 Hz, Command writer 500 Hz (`g1_deploy_onnx_ref.cpp:2164-2167`), created with `UT_CPU_ID_NONE` (`:2580-2588`); `SetThreadPriority()` applies `SCHED_FIFO`/CPU-0 to the **main** thread only, *after* the workers spawn. The 50 Hz loop runs SCHED_OTHER on a Jetson sharing the CPU with TensorRT inference.
- **Deterministic asynchrony is tiny.** The 50 Hz tick reads whatever the 500 Hz `LowState` buffer holds; the 500 Hz writer republishes whatever control left. That is ±2 ms — **below our 5 ms physics granularity, and not representable at all.** The real large jitter comes from scheduler stalls and dropped/CRC-rejected DDS packets. **The realistic process is a small baseline plus rare multi-tick spikes**, not a large uniform baseline.
- **Common-mode, twice over.** One `LowCmd` DDS message carries all 29 motor commands under one CRC (`:2666-2678`) — a lost or late command loses every joint together, so independent per-group lag is a hardware fiction. And the policy's `gravity_dir`, `base_ang_vel`, `joint_pos`, `joint_vel` all arrive in one `LowState` packet, attitude derived from a single `imu_state().quaternion()` (`:2895`) — so **independent IMU-bus and joint-bus lags are also invented.** (The separate torso IMU at `:2899-2901` is logged only; it never reaches the observation vector.)
- **20 ms zero-order hold is already modelled** by `decimation=4`.
- **Thresholds are alarm and abort, not tolerance.** `LOW_STATE_LATE_THRESHOLD{50}` (`:295`) drives an audible operator alert and nothing else (`:2989-2996`); `LOW_STATE_ABSENT_THRESHOLD{500}` (`:296`) makes `CheckSafety()` return false and **aborts control** (`:2764-2779`). The stack *alarms* at 50 ms and *quits* at 500 ms. Nothing says 100 ms is nominal.
- **No measured end-to-end latency figure exists anywhere in this workspace.** `GetAgeMs` measures age-since-DDS-receipt only, excluding on-robot sensing, motor bus and transport. The only statistically monitored latency is `streaming_data_delay` — the VR/teleop *reference* path (threshold 150 ms), which is command-input lag, not plant dead time, and must not be borrowed.

### 4.3 What is already closed

Three results, all from receipts, that remove the obvious moves:

1. **The 0–60 ms amplitude has been trained blind and it won.** `fixed_150` trained with `max_delay_steps: 12` (= `delay_range [0,12]` = 0–60 ms) in `manifests/expansion_prototype_20260902_072758/`, and scored p100 **0.992** / PRIM **0.935** against `gate_150` 0.932 and `ramp_150` 0.921.
2. **Fixed DR saturates the clean ladder past its own support.** `capability_benchmark_analysis_20260830.json`, arm `fixed`: lat_10/20/30/40/**50** ms = 1.0, 1.0, 1.0, 1.0, **1.0**. A policy trained on i.i.d. per-episode 0–40 ms *independent* lag scores 100% at a sustained 50 ms *common* lag.
3. **60 ms is a documented floor.** `latency_60ms` reads 0.000 for every policy ever measured, including the untrained origin, and is banned by name in `learnability_gate.BANNED_RANKING_PRESETS`.

**So the clean latency axis runs from "fixed already scores 1.000" at 50 ms to a measured floor at 60 ms: two rungs at 5 ms granularity, with no measured middle.** Say that plainly in any writeup.

### 4.4 The hard configuration

```yaml
# NEW: gear_sonic/config/manager_env/events/terms/randomize_action_delay_concentrated.yaml
#
# CONCENTRATED, COMMON-MODE actuation latency. Every latency cell ever run in
# this project used a nominal-anchored [0, high] support, so a fraction 1/(high+1)
# of environments drew zero lag every episode. That easy sub-population is the
# nesting mechanism, and it is the only thing a curriculum could have staged past.
# This term removes it from the SUPPORT while keeping lambda=0 a bit-identical
# no-op: RANGE_NOMINALS["delay_range"] = 0.0, so scale_range returns
# [8*lambda, 10*lambda] -- a point-anchored-at-zero ladder with no zero draws at
# lambda = 1.
randomize_action_delay:
  _target_: isaaclab.managers.EventTermCfg
  func: gear_sonic.research.practice_utility.events_reset_safe:randomize_action_delay
  mode: "reset"
  params:
    asset_cfg:
      _target_: isaaclab.managers.SceneEntityCfg
      name: "robot"
    delay_range: [8.0, 10.0]      # 40-50 ms, NO zero draws
    distribution: "uniform"
    # One DDS LowCmd carries all 29 motor commands under one CRC
    # (g1_deploy_onnx_ref.cpp:2666-2678). Independent per-actuator-group lag is a
    # hardware fiction and partially cancels across the body. This is a FIDELITY
    # CORRECTION, not a severity knob.
    coupling: "common"
```

Requires `--max-delay 10` or higher, or LUCID's own clamp silently trains a smaller envelope.

**Observation side** (~60 lines, no upstream edit): a `ModifierBase` subclass in `gear_sonic/research/practice_utility/obs_delay.py` holding a `DelayBuffer(max_steps, data_dim[0], device)`, `reset(env_ids)` → `set_time_lag` + `buffer.reset`, `__call__(data)` → `buffer.compute(data)`. Attach it via `ObservationTermCfg.modifiers` on `gravity_dir`, `base_ang_vel`, `joint_pos`, `joint_vel` in a **new** policy-group yaml. Set **one shared lag of 1 policy step (20 ms)** across all four — that is the hardware-faithful coupling. Two mechanics to record: `ModifierBase` receives no `env` handle, so the modifier must self-register in a module-level registry keyed by a `bus` name that a companion event term looks up (do not reach into the private `_group_obs_class_instances`); and modifiers run once per `observation_manager.compute`, so obs staleness is quantized to **20 ms** while actuation lag stays 5 ms-resolved.

**Enforce a total-loop budget as a hard constraint, not a footnote.** 40–50 ms actuation + 20 ms observation + the 20 ms ZOH already in `decimation=4` is 80–90 ms of loop dead time against a documented 0.000 floor at a *sustained* 60 ms on top of the full envelope. Do not exceed 60 ms on the **sum** of the two new terms.

### 4.5 Why each choice is harder in a way i.i.d. redrawing does not defuse

| Choice | Why it survives per-episode redrawing |
|---|---|
| `delay_range: [8.0, 10.0]` (min > 0) | This is the **only** one that does. Nesting requires the easy region to be *inside the support*; removing it is the sole edit that per-episode redrawing cannot undo. It is the project's own "concentrated target" rule applied to latency, and it has never been run — every measured latency cell used `[0, high]`. |
| `coupling: "common"` | With independent per-group lags the five groups' phase errors partially cancel at the CoM, so the same nominal 40 ms is strictly milder. **Evidence is thin:** the only measurement is one frozen-policy panel (common 0.50/0.61/0.56 vs independent 0.67/0.50/0.78) that is sign-inconsistent across arms. Justify this as a **fidelity correction**, not as severity. |
| Observation staleness | A different quantity from command lag: it removes the ability to *react*, not just to *act*, so it is not simply additive dead time. **Caveat that weakens it:** noise is applied *after* modifiers (`observation_manager.py:392-424`), so a held sample receives an independent noise draw on each repeated step and the 10-frame history can partially de-noise it. |
| Fixed `reset_buffers` | Without it a jitter arm measures a sawtooth that is *easier* than its matched static arm. This is a correctness prerequisite for any within-episode latency claim. |

**Honest expectation: still a tie on the training question.** The amplitude axis is closed, the jitter axis is confounded but points at "free," and the concentrated form has ~two rungs of headroom. The real value of this work is that `coupling: common` and the observation-side term are *fidelity* corrections closing a gap that is currently exactly zero.

---

## 5. Recommended next experiment

**Question:** does training a single motion under FIXED DR at a concentrated hard setting train at all?

**Channel:** joint effort limit as a POINT on all 29 joints. Chosen because it is the only channel whose severity is already measured live (−18.95 pts at `act_effort_150`, ρ = +0.50 with the existing ladder), it is fully built and preregistered, it is the direct test of the concentrated-target hypothesis, and — critically — its barrier/unlearnable boundary is *computable offline*.

**Motion:** `walk_hands_on_back_loop_002__A066_M`, 4.03 s, pool `$LUCID_ROOT/pools/subsets/m1_hob002/robot_filtered`. Arms held still (the wrist half of `ee_body_pos` measures 0.000 on this clip), so **foot placement is the single axis of difficulty** — which is exactly what an ankle-authority channel attacks.

### 5.1 The binding joint, and the boundary — arithmetic, not GPU

A uniform effort scale hits every joint, but it binds at the **ankle**, not the hip or knee. From `main.urdf`: total mass 34.394 kg (51 links) → *mg* = 337.4 N; the sole spans **+0.132 m forward** and −0.054 m back of the `ankle_roll` frame. The ankle group carries `effort_limit_sim = 50.0` with **doubled** gains (`2.0 × STIFFNESS_5020` = 28.50 N·m/rad, `g1.py:277-284`).

Full-CoP ankle torque = *mg* × 0.132 = **44.5 N·m** in single support, **22.3 N·m** per ankle in double support.

| Effort scale | Ankle τ | CoP reach, single support | CoP reach, double support | Knee τ |
|---|---|---|---|---|
| 0.50 | 25.0 N·m | 74 mm (**56%** of forward foot) | 148 mm (100%) | 69.5 N·m |
| **0.40** | **20.0 N·m** | **59 mm (45%)** | 119 mm (90%) | 55.6 N·m |
| 0.30 | 15.0 N·m | 44 mm (34%) | 89 mm (67%) | 41.7 N·m |
| 0.25 | 12.5 N·m | 37 mm (28%) | 74 mm (56%) | 34.8 N·m |

At 0.40 the robot loses roughly **half its single-support CoP authority** and must substitute stepping for ankle regulation — a strategy change, which is the shape a barrier has. The knee at 0.40 keeps 55.6 N·m, comfortably above level-walking demand, so this is not a whole-body weakening. **0.25 is exactly the `PHYSICAL_LIMITS` floor** (`dr_scaling.py:255`); 0.20 would be silently clamped.

### 5.2 Screening sequence — least GPU before the decisive test

**Phase 0 — zero GPU, 36 s.** `pytest tests/practice_utility` (1,812 tests). Catches wiring before anything launches.

**Phase 1a — the frozen-policy POINT screen. ~15 min GPU. This has never been run.** Every actuator cell to date is a per-joint *range* (**D3**); the point's severity is unmeasured.

Build it with the **existing vendor pattern**, which already proves the trick works — three small files, no new machinery:

```bash
# 1. Copy the vendor point term, widen to all joints, put the point at the clamp.
sed -e 's/\[".*_hip_pitch_joint"\]/[".*"]/' \
    -e 's/\[0.633, 0.633\]/[0.25, 0.25]/' \
  gear_sonic/config/manager_env/events/terms/randomize_joint_effort_limit_pitch.yaml \
  > gear_sonic/config/manager_env/events/terms/randomize_joint_effort_limit_point.yaml
# 2. Copy lucid_actuator.yaml -> lucid_actuator_point.yaml, composing that term.
# 3. Add PRESET entries act_point_XXX at channel scale s.
```

The scale→severity map is free: `scale_range([t,t], λ, nominal=1.0)` returns the point `1 − λ(1−t)`, so with *t* = 0.25 one term gives a **continuous** ladder — s = 0.333 → 0.75, 0.667 → 0.50, **0.80 → 0.40**, 0.933 → 0.30, 1.0 → 0.25.

```bash
source /home/linjiw/lucid/env/lucid_env.sh
export LUCID_GPU_WAIT_SECONDS=7200
cd "$LUCID_REPO"
STAMP=$(date +%Y%m%d_%H%M%S)
python scripts/practice_utility/run_curriculum_robustness_eval.py \
  --training-receipt "$LUCID_ROOT/manifests/lucid_channel_sweep_index_20260902.json" \
  --training-config "/home/linjiw/lucid/GR00T-WholeBodyControl/logs_rl/lucid-campaign/manager/universal_token/all_modes/sonic_release_test-20260829_000251/config.yaml" \
  --num-envs 512 --seeds 8600 \
  --modes fixed off lucid_rg lucid_s4_rg \
  --presets act_off act_point_075 act_point_050 act_point_040 act_point_030 act_point_025 \
  --eval-seed-base 8700 --max-delay 12 \
  --panel-receipt "$LUCID_ROOT/manifests/replicate_panel_panel_hob002_k512.json" \
  --artifact-root "$LUCID_ROOT/artifacts/effort_point_screen_$STAMP" \
  --log-dir       "$LUCID_ROOT/outputs/effort_point_screen_$STAMP" \
  --receipt-dir   "$LUCID_ROOT/manifests/effort_point_screen_$STAMP" \
  --min-free-mib 5800 --execute
# lucid_ratchet_rg resolves a different training config; run it as a second
# invocation, exactly as tools/run_actuator_screen.sh already does.
```
25 cells × 35 s ≈ **15 min**.

**Phase 1b — settle the friction nulls. ~12 min GPU.** Because of **D1**, the frozen screen at `num_buckets: 1` on the feet is the cheapest way to find out whether every friction result in this project means anything. Four new term yamls (`body_names: [".*_ankle_roll_link"]`, static = dyn = μ ∈ {0.5, 0.4, 0.3, 0.2}, `num_buckets: 1`) + four presets. Two mechanics to respect: `num_buckets` must never be raised later (`torch.randint` indexes a table sized at `__init__` → IndexError), and a **feet-only regex enters `events.py:205-224` for the first time anywhere** — it raises `ValueError` at `__init__` if the shape-count parse disagrees with `max_shapes`, so smoke-test env construction first. 20 cells ≈ **12 min**.

> *Note the asymmetry:* a friction point is fine for a **screen**, but it cannot be a **curriculum channel** without new code — `RANGE_NOMINALS["static_friction_range"] = None` means the nominal is the *midpoint*, so `scale_range` returns `[μ, μ]` at every λ. The effort channel has a numeric nominal (1.0) and scales correctly, which is why it is the recommendation.

**Phase 1 gate.** Pick the severity where `fixed` first drops below ~0.90 while staying above ~0.40. **If `fixed` stays above 0.95 at 0.25 — the clamp — the channel has no window and you stop here for ~0.5 GPU-h.**

**Phase 2 — one from-scratch arm with a tripwire. 5.5 GPU-h, or ~1.0 if it aborts.**

```bash
python scripts/practice_utility/run_curriculum_comparison.py \
  --from-scratch --num-envs 1024 --iterations 8000 --warmup-iterations 10 \
  --seeds 8600 --modes act_point \
  --actuator-channel effort_limit --actuator-target 0.40 \
  --max-delay 12 --termination-thresholds default \
  --horizons 500 1000 2000 4000 6000 \
  --motion-file "$LUCID_ROOT/pools/subsets/m1_hob002/robot_filtered" --smpl-motion-file dummy \
  --wandb-project lucid-campaign --min-free-mib 8000 --execute
```
**Run one arm per invocation.** The driver writes a single receipt after *all* arms, which is the shape it handles worst in a hunt where arms are expected to fail.

Tripwire, every 10 min while it runs (there is **no instability detector** anywhere in this codebase — nothing will stop a doomed run):
```python
import sys; sys.path.insert(0, '/home/linjiw/lucid/GR00T-WholeBodyControl')
from gear_sonic.research.practice_utility.run_log import parse_run_log
s = parse_run_log('<the arm log>').series('Env/Episode_Termination/time_out')
if s and max(s) >= 1500 and s[max(k for k in s if k <= 1500)] < 0.30:
    print('ABORT: no takeoff by 1500; the no-DR control is ~0.75 there')
```

**Phase 3 — the decisive contrast, 3 arms × 5.5 = 16.5 GPU-h.** `act_off`, `act_point`, and a **mean-matched** range arm. As coded, `act_range` = [0.40, 1.0] (mean 0.70) against the point's 0.40 — that confounds shape with mean. Add `act_range_matched` at `[0.25, 0.55]` (mean 0.40, inside the clamp) and report both.

**Phase 4 — staged arms, only if `act_point` failed.** `act_ramp` + `act_gate` from scratch to the *same* point severity, 11 GPU-h. Set `ARM_RETURN_DROP = 0.99` for any gate arm — the survival gate's `_best_return_mean` is a never-rebaselined running maximum, which tripped `gate_300` on 1,465 of 2,000 iterations.

**Phase 5 — three seeds on whatever contrast survives.** The between-seed effect on absolute capability is **7.8 points**, larger than the 5-point decision margins, so one seed forbids superiority language (rule C7).

### 5.3 Primary metric and decision rule

**Primary:** held-out success on the frozen band, `act_point` minus `act_off`.
**Training-side liveness:** `Env/Episode_Termination/time_out`, against the measured from-scratch no-DR reference on this exact motion, pool and env count: 0.024@664 → **0.707@1327** → 0.860@1990 → 0.953@3316; `Mean length` 23.0 → 49.5@664 → 150.3@1327 → 185@4000.

| Verdict | Rule |
|---|---|
| **NO-EFFECT** | `time_out` ≥ 0.70 by iteration 1,500 **and** final held-out within 5 pts of `act_off`. Report as a severity where a curriculum is unnecessary (rule C5) — this is a map entry, not a failure. |
| **CANDIDATE BARRIER (C1)** | `time_out` < 0.30 at iteration 1,500 **and** final held-out ≥ 10 pts below `act_off`. |
| **BARRIER (C1 ∧ C2)** | C1 **and** a staged arm ending at the *same* point severity reaches within 5 pts of `act_off`. |
| **UNLEARNABLE (C1 without C2)** | C1, no staged arm reaches it, **and** the offline feasibility check is positive. Report as unlearnable. Never as a barrier. |

**Offline feasibility check — run it before booking Phase 2, it costs no training.** Roll out the frozen `fixed@s8600` policy on the clip, record per-joint (|q̇|, |τ|) from `data.applied_torque`, and confirm the clip's peak ankle torque stays below 50·*s*. Corroborate against the CoP table in §5.1. A positive violation converts a Phase-2 failure from "candidate barrier" to "unlearnable" without a second run.

### 5.4 Mandatory guards, declared before launch

1. **From scratch, 8,000 iterations.** Every elevated-intensity training result in this project (1.375 through 3.0) is a 1,500–2,000-iteration warm start from a checkpoint that had already solved λ=1, which makes "direct training fails" literally unaskable. From scratch, this project has only ever trained at λ = 0 and λ = 1.
2. **PhysX read-back must report `matched`** for `randomize_joint_effort_limit` before any "inert" conclusion — the articulation writes its own Python mirror unconditionally, so counting writers called proves nothing. The `physx_getter` (`get_dof_max_forces`) exists on this channel. **Do not use `joint_friction` as the barrier channel until its read-back is fixed** — it is the one actuator channel with no `physx_getter` (`actuator_dr.py:139-152`), so `physx_readback` always returns `unavailable`. The fix is ~10 lines: `get_dof_friction_properties()` exists and returns `(N, dofs, 3)`; it needs a column selector.
3. **Record the draw shape in the receipt.** `act_range` is per-joint independent; `act_point` is per-joint identical. Confusing them is how the survey mis-ranked this candidate in the first place.
4. **λ=0 must be bit-identical**, pinned by a test, or the baseline arm is a subtly different robot.

### 5.5 GPU cost

| Phase | Cost | Cumulative |
|---|---|---|
| 0 — CPU tests | 36 s, 0 GPU | 0 |
| 1a+1b — frozen point screens (45 cells @ 35 s) | **0.45 GPU-h** | 0.45 |
| 2 — one from-scratch arm (tripwire-abortable) | 5.5 GPU-h (~1.0 if aborted) | ~6 |
| 3 — decisive contrast, 3 arms, 1 seed | 16.5 GPU-h | ~17 |
| 4 — staged arms, only on C1 | 11.0 GPU-h | ~28 |
| 5 — 3 seeds on the surviving contrast | +33 to +55 GPU-h | 61–83 |

Measured constants: 35.1 s median per 512-episode eval cell; 1.50 GPU-h median per warm-start 2k cell; **5.5 GPU-h** per from-scratch 8k cell (19,952 s and 20,088 s observed) at 1024 envs / ~10,500 env-steps/s. **The GPU is idle now** (716 / 16,303 MiB, no compute apps). Contention risk is the user's unrelated `scene2motion`/exp028 loop — keep `--min-free-mib` honest and `LUCID_GPU_WAIT_SECONDS` large so a driver queues rather than dies.

---

## 6. What I would not do

### Numerically dangerous — would fabricate a result

1. **`NoiseModelWithAdditiveBiasCfg` without `operation="abs"`.** `NoiseModelWithAdditiveBias.reset` does `_bias[env_ids] = bias_noise_cfg.func(_bias[env_ids], cfg)` (`noise_model.py:174`), and `NoiseCfg.operation` defaults to `"add"` (`noise_cfg.py:29-30`), so the bias performs an unbounded **random walk across episodes** — measured drift to |bias| = 0.294 after 6 resets against an intended 0.09 cap. IsaacLab's only in-tree user sets `"abs"` (`shadow_hand_env_cfg.py:279-286`). As written, the proposed tilt-bias configs would walk past the termination shell and manufacture a "barrier" out of bookkeeping.
2. **`apply_external_force_torque` with the default `SceneEntityCfg("robot")`.** `num_bodies` falls back to `asset.num_bodies` when `body_ids` is not an explicit list (`events.py:1027-1033`), so a ±90 N range is applied **independently to ~30 bodies** — up to ~2,700 N, ≈ 8 g. `body_ids=["torso_link"]` is mandatory. Note also that the stock term samples x, y and z identically, so ±90 N includes a held **vertical** component of ±27% body weight, which models a bodyweight-support gantry, not a tether.
3. **Scheduling `num_buckets` at runtime.** `torch.randint(0, num_buckets, ...)` indexes `material_buckets` sized at `__init__`; `resample_material_buckets` deliberately preserves the count. Set it once; raising it in `params` later is an IndexError.
4. **Wide `joint_velocity_range` on the initial state.** `commands.py:3049-3052` clips joint *position* to `soft_joint_pos_limits` but **never clips joint velocity** to `soft_joint_vel_limits` — so it writes initial speeds above `velocity_limit_sim` into PhysX. Upstream's own `reset_joints_by_offset` clamps velocity (`events.py:1311-1313`); this path does not.
5. **`platform_width=0.0` on `MeshRandomGridTerrainCfg`.** `trimesh.creation.box` with zero extents is degenerate, and the sub-terrain origin is at `+grid_height` while cell tops are distributed about 0 — a systematic spawn drop of *h* plus ±*h*, i.e. up to 90 mm at *h* = 45 mm against a 150 mm shell.
6. **Damping scale below ~0.15× with latency at full.** `randomize_actuator_gains` validates *stiffness* scale ranges with `allow_zero=False` (`events.py:576-580`) but not damping, so 0.25 and even 0.0 are accepted silently. The cap must be enforced by project code.

### Would produce an unlearnable task

7. **μ ≤ 0.15 at the foot on *this* clip.** The clip is hands-on-back, so arm and trunk counter-rotation — the dominant slip-recovery mechanism — is actively penalised by the upper-body tracking term. A failure there is a reward conflict or infeasibility, not a barrier. Report lower-body and upper-body tracking error separately at every rung, and replicate any decisive rung on a free-arm walk clip.
8. **Effort scale below ~0.25.** The ankle drops under 12.5 N·m = 28% of forward CoP in single support, and 0.20 is silently clamped to 0.25 by `PHYSICAL_LIMITS` anyway.
9. **Joint position-limit randomization.** `write_joint_position_limit_to_sim` silently **clamps `default_joint_pos`** (`articulation.py:740-748`), which is the action offset — it moves the controller's zero while the receipt reports only a limit change.
10. **Static 60 ms latency.** Reads 0.000 for every policy ever measured including the untrained origin; banned by name in `learnability_gate.BANNED_RANKING_PRESETS` (both `latency_60ms` and `lat_60ms`).
11. **Stacking 0–60 ms actuation on 20–60 ms observation staleness.** Up to ~140 ms of loop dead time, roughly 6× any plausible onboard G1 figure, and past the point where staging can create phase margin.

### Survived screening, but do not pursue

12. **The mid-stance friction STEP.** Unbuildable as specified: `events.py:262` draws one bucket per collision shape, so per-env randomness and per-shape consistency are **mutually exclusive**. `num_buckets: 1` gives a deterministic global value (no randomization); `num_buckets > 1` re-averages the step across 7 capsules to ~range/√7 — small and smooth, exactly what it was meant to avoid. A real per-foot step needs a bespoke materials writer, contradicting "zero new physics." Separately, the interval form pays a **full `(num_envs, max_shapes, 3)` CPU round-trip** with 1024 staggered envs firing on essentially every 50 Hz step.
13. **Wider uniform latency.** Trained blind at 0–60 ms and it *won* (§4.3).
14. **Per-joint independent PD gain randomization** at log-uniform [0.6, 2.0] / [0.25, 1.0]. The median of log-U[0.6, 2.0] is 1.095, so at maximum intensity the **median joint is nominal** — the support is *centred on the easy case*. If run at all: one correlated scalar per env, a point-form damping, ankle+knee only, and expect a tie. Two corrections worth banking: the "blocking confound" does not exist (`JointAction` materialises its scale once in `__init__`, `joint_actions.py:85-90`, and never re-reads stiffness), and the proposed safety screen is vacuous (`ImplicitActuator` integrates PD implicitly and is unconditionally stable, so "open-loop stability at zero action" passes for every K > 0). Also, upstream's own docstring warns against using `randomize_actuator_gains` in reset mode at all: 5 actuator groups × 2 gains = **10 full-tensor CPU round-trips per reset**.
15. **Joint stiction at 0.08–0.12 of rating.** Two independent objections converge: the deadband is **6.4° (knee) / 8.0° (ankle)** at 0.08 — a third of the action range; and 0.08 of rating is **20–55×** the `frictionloss="0.2"` N·m that Unitree's own MJCF declares (`motionbricks/assets/skeletons/g1/g1_29dof.xml:5-19`; the G1 leg is a 14:1/22:1 backdrivable planetary QDD, not a strain-wave drive). The honest band is ~1–2% of rating. Meanwhile at `act_friction_300` (range [0, 0.15], per joint) the fixed policy already scores **0.873 zero-shot**, so 0.08 sits inside a survived band. The **point** form is a one-line yaml change and is worth running as a *shape* test, at 1–2% — not as a barrier bid at 8%.
16. **Thermal derating as configured — it runs backwards.** At the survey's own plausible duty of 0.19, steady state = duty²·λ·`cool_multiple` = **0.217 < onset 0.35**, while `initial_temperature_max` draws U[0, 0.5λ]. Simulated over a 4.04 s episode the mean available torque **rises**: 0.983 → 0.990 at λ=1, 0.831 → 0.851 at λ=2. Temperature is set exogenously at *t* = 0 and decays (`cool_τ` = 24 s). All three claimed properties — endogenous, history-dependent, arrives late — are absent, and the channel degenerates to a per-episode uniform draw on a static torque scale that *eases off*. The survey's own remedy (λ ≈ onset/(duty²·`cool_multiple`) = 1.6) sets the steady state *exactly at* onset, i.e. time-to-onset = ∞; and `heat_seconds` does not appear in the steady state at all. Making it bite needs `heat_seconds` ≈ 0.25 s, at which point the thermal name is unearned. Two further blockers: `depth` is capped at 1 − 0.5 = 0.5, so it can never go below 0.5× peak — *half as deep* as `effort_limit`'s 0.25 floor; and `ThermalState.lam` is a Python float, so it cannot join the per-cohort strata dispatchers. It is `effort_limit` with an integrator that does not integrate.
17. **The DC-motor curve fitted through (20, 139) and (32, 88).** Those are two **reducer variants of one motor**, not two points on one joint's curve — armature ratio 0.025101925/0.010177520 = 2.4664 against (22/14)² = 2.4694, and τ·ω = 2,780 vs 2,816 W. The fitted line's corner velocity is exactly **20.0 rad/s = the joint's own speed limit**, so torque is clipped flat at 139 across the entire reachable range: a bit-exact no-op. And the vendor-faithful config (saturation = 139 peak, effort_limit ≈ 70 continuous) has its corner at 9.93 rad/s, *above* the clip's measured 7.31 rad/s peak, so it degenerates to the flat effort channel at 0.5× — already measured. Two further mechanics: implementation (b) can only impose a **symmetric** magnitude cap (PhysX DOF max force has no sign), so it removes the braking torque a real motor *keeps* — strictly harsher than the physics it cites, in the recovery quadrant; and it goes blind in telemetry, since `data.applied_torque` is clipped against the **unchanged** `actuator.effort_limit` and feeds the live `energy_consumption` reward (`rewards.py:261`).
18. **Anything motivated by "our sim over-torques the hip by 58%."** RETRACTED (workspace commit `e4daca4`): 88 N·m @ 14.3:1 and 139 N·m @ 22.5:1 are both official Unitree variants, and the derating cells were **measured inert** (`vend_off` 0.9902 vs `vend_hips_100` 0.9922 — inside single-cell noise). Note that the thermal and torque-speed real-world arguments each re-import this claim in a different dress ("the deploy MJCF says 88"); strip it. The deploy folder does ship an asset for the *older* variant while pinning `MODE_MACHINE: 5` (the newer one) — that is an asset-version inconsistency worth a bug report, not evidence about torque.
19. **Gravity.** `randomize_physics_scene_gravity` is global-only by its own docstring (`events.py:515-521`), and in *this* codebase a tilt is **invisible**: `commands.py:161-165` hardcodes `down_dir = (0, 0, -1)`, and `GRAVITY_VEC_W` is captured once at init (`articulation_data.py:57-64`) and never refreshed after `set_gravity`. So a "slope" here is an unobserved IMU bias, not a slope. Never randomize gravity **magnitude**.
20. **Push cadence as a curriculum variable.** `interval_range_s` is a top-level `EventTermCfg` attribute, not a `params` key, and both `capture_baseline` and `apply_lambda` walk `cfg.params` exclusively — it is *structurally invisible* to the scaler. `EventManager` also samples per-env intervals from one global range, so no per-env arm can express it. And 0.2 s is below the natural step period, which the proposal's own guard forbids.
21. **Persistent wrench as a NEW shape.** `ForceTrackingCommandCfg` already ships it (`commands.py:4225-4243`: `max_force = 20.0`, `force_update_frequency = 100` = a 2.0 s hold at 50 Hz) and it is SONIC's own robustness design. Scaling to 50–90 N is a *magnitude* increase on a shape already proven fixed-trainable. Also: `is_global=True` does not do what was claimed — the kernel converts world→link **once at set time** and stores it in the link frame, so a set-once wrench thereafter **rotates with the torso**, and the "world-fixed tether / floor slope" reading is false. And the permanent wrench is **cleared on every env reset** (`articulation.py:215-216`), which makes `mode: interval` a silent per-env intensity leak — use `mode: reset` only.
22. **Terrain via i.i.d. relief.** Defused by spatial mixing (§3, Tier E). Two corrections to carry: the current baseline is *not* "1–5 mm of dither" — `random_rough`'s `noise_step` (0.02) **overruns** its `noise_range` (0.001–0.005), so `np.arange(0, 1+4, 4)` = [0, 4] quanta of 5 mm = **{0, 20 mm}** on ~14% of tiles; and `max_init_terrain_level: 10` is already set at `modular_tracking_env_cfg.py:340`, so `terrain_levels` already varies per env today. If terrain is pursued, do it as `pyramid_stairs` — spatially coherent, monotone, partial success impossible — and fix the origin-height offset first.
23. **Termination-threshold tightening, and degrading the critic.** Neither is DR. The first is the fastest way to manufacture a fake barrier: under the strict preset, 93% of from-scratch episodes die on tracking error within 0.25 s and 0.07% reach time-out, which is why `run_single_motion_baseline.sh` deliberately uses the default thresholds. The second is a training-algorithm knob for a network discarded at deployment.
24. **Any observation- or command-manager channel as a curriculum-vs-fixed test, until evaluation can see it.** `dr_scaling._iter_terms` walks the **event manager only**, and `TrackingCommand`'s initial-state randomization is gated by `if not self.is_evaluating` with every scoring path setting it `True` (`eval_agent_trl.py:589`; `im_eval_callback.py:249`; `ppo_trainer.py:1985, 1994, 2005, 2255`). A curriculum-vs-fixed comparison on initial-state desync therefore returns a **tie by construction, before physics gets a vote.** Fixing that means editing the evaluation protocol, which puts the comparison outside the existing receipt and frontier machinery.

---

## Where the evidence is thin — stated, not smoothed

- **`coupling: "common"` is asserted, not measured.** The only data is one frozen-policy panel (common 0.50/0.61/0.56 vs independent 0.67/0.50/0.78 at the 8-step support) — within noise and sign-inconsistent across arms. Justify it as a fidelity correction.
- **D1 is verified in source and arithmetic, not by a runtime read-back.** Confirm with `robot.root_physx_view.get_material_properties()` after a reset before publishing anything about it.
- **Whether PhysX's DOF friction produces genuine stick-slip under an `ImplicitActuator` solved inside PhysX at dt = 0.005 is not decidable from the Python bindings** — the model lives in the C++ solver. Bench it on a single joint before committing GPU hours.
- **No measured G1 hardware figure exists anywhere in this workspace** for loop latency, joint friction, IMU bias, motor continuous rating, or floor friction. `hardware/` contains one camera-mount STEP file. Every hardware magnitude in this report that is not a config value is an external prior and is labelled as such. The instruments to measure two of them exist and have never been run: the deploy stack prints `LowState age / IMU age` every second (`:4049-4056`), and it logs `tau_est` (`state_logger.cpp:54`). Five minutes on hardware would replace two assumptions with numbers.
- **The barrier lens's claim that "four of the six channels are already mode `startup` and tied" cites `level0_4.yaml`.** Under `lucid_curriculum.yaml` — the preset every landed LUCID result used — those terms are mode `reset`. I did not resolve which preset the cited comparison ran under. Treat "persistent per-env draws are already known inert here" as **unverified**.
- **Validity control for any positive result** in low friction, high stiffness, compliant contact or rough terrain: the robot asks for 8 position / 4 velocity solver iterations (`g1.py:216-217`) against PhysX schema defaults of 32/1, and `friction_correlation_distance` is 0.025 m against an 8–10 mm capsule spacing across a 52 mm sole — PhysX merges the sole into roughly two friction anchors. Replicate at 32/8 iterations and `sim_dt = 0.0025` before writing it down. A barrier that evaporates under solver refinement was never physics.