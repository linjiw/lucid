# D1 recording-to-report audit — September 10, 2026

## Outcome and stopping point

The offline pose adapter, versioned durable-restoration endpoint and schedule-first
aggregator are implemented and analytically tested. Existing scorer outputs are
unchanged. **Actual recording-path validation and calibrated protocol freeze
remain open.** No actual recording can yet support the complete source-to-score
claim: 39 available `recovery/recovery_trace.jsonl` files were read and hashed,
containing 1,864,448 sample rows. None contains the required raw joint/root pose
schema. Counts are recording inventory, not independent experiments or recovery
measurements.

Private evidence: `/home/linjiw/lucid-sonic/outputs/d1_recording_audit_20260910/`
contains `recording_inventory.json`, pinned source hashes, and a clearly labeled
synthetic source-to-report example. The inventory scans this named trace family
under the experiments root; it does not prove no other raw data exists anywhere.

## Exact implemented component contract

The old scorer accepts five nonnegative scalar errors; it did not derive them.
The new `task_trace_adapter.py` makes their definitions executable:

| Component | Definition and units | Required raw fields / frame |
|---|---|---|
| Planar root/path | Euclidean norm of root xy difference, metres | Robot and unchanged reference pelvis position in the same registered Z-up world W |
| Root height | Absolute root z difference, metres | Same positions; no height recentering |
| Heading | Absolute wrapped difference of projected root +X headings, radians | Unit wxyz root quaternions in W; vertical projected axis produces invalid truth, never zero error |
| Articulation | RMS of direct bounded-joint angle differences, radians | Equal ordered joint names and joint position vectors; no joint-angle wrapping for G1 bounded joints |
| Tilt | Angle between world-gravity vectors expressed in robot/reference root frames, radians | Third rows of root rotation matrices; independent of common yaw and translation |

No body MPJPE is substituted for joint RMS. No root translation is inferred by
subtracting global and local MPJPE. Joint correspondence must match the motion
library and robot before collection is certified; identical vector length is
insufficient. Actor estimates are not accepted as the declared evaluation-truth
source. A declared source label and matching metadata are software checks, not
independent proof of sensor calibration.

`task-truth-v1` requires fixed trial/episode, world, clock, reference content and
registration identities; explicit pre-trial registration xyz/yaw; joint names;
quaternion/units convention; time origin and cadence. Positions supplied to the
adapter are **already registered in W**. It never fits or reapplies a transform.
Truth/reference times must equal the scheduled time at each tick. Missing live
truth remains missing. Raw records and uncapped derived components are retained
in the audit; normalized capped/padded cost is separately labeled in the legacy
result.

## Contract reconciliation

- Pre-event grid is exactly integer ticks `[0, onset)`, with `onset > 0`.
  Missing initial or internal ticks cannot establish competence. There is no
  settling exclusion in v1; a later exclusion needs a new frozen contract.
- Legacy `regained` still means first qualifying dwell, possibly followed by
  relapse. `task-restoration-v2` adds durable entry: an admissible entry with at
  least D dwell and all remaining samples in band through the fixed endpoint.
  Temporary attainment followed by ending out of band fails the new primary
  endpoint. A later qualifying durable return can succeed, preserving earlier
  relapse information in the legacy result.
- Leaving during the pulse and returning before its end is regained, not
  maintained. Success is componentwise; low average cost cannot compensate for
  a violated band.
- Explicit invalidation or observed pre-event/endpoint band violation is known
  failure F even when unrelated truth/delivery information is missing. Delivery
  remains a separate field. An absent nonzero disturbance with no independent
  failure is U. Planned zero controls occupy their own cohort.
- Failure padding is a conservative reporting convention. It is neither observed
  post-failure motion nor the proposed future optimizer's cost derivation.

## Runtime and terminal boundary: checked source, not live validation

The pinned `manager_based_rl_env.py` at
`/home/linjiw/isaaclab-install/IsaacLab/source/isaaclab/isaaclab/envs/` performs:
physics/action application and scene updates → counters → termination and reward
→ optional recorder observations → pre-reset hooks and reset → command compute
→ interval events → observation compute with history update → returned data.
Thus a returned observation may already belong to the reset episode.

The inspected `native_recovery_recorder.py` in `lucid-path-pilot-eval` wraps
`_reset_idx` and samples before reset mutation, labels terminal-pre-reset rows,
tracks physical/reference generations, and samples after native command compute
but before interval events. `commands.py::_update_command` increments the
reference cursor and may resample/wrap. Reference time cannot simply be inferred
from an arbitrary returned pose. The new tap records both the native control
step and absolute reference frame; it does not assert they are aligned.

`attach_raw_capture` is an opt-in tap on this existing recorder. It copies root
poses and joint arrays to owned Python values before passing through the legacy
sample call. It calls no step, policy, observation computation or random draw.
A CPU fixture mutates buffers immediately afterward and confirms the snapshot
is unchanged. Its terminal fixture places a perfect reset pose after failure:
that pose remains excluded from the failed trial. This verifies the interface,
not the simulator's live timing or numerical parity.

## Existing recording coverage and blocker

Existing rows provide: control step, time, env/motion/physical-episode/reference-
segment IDs, normalized reference phase, heading error/validity, global/local
body MPJPE, heading-aligned body articulation MPJPE, and **3D** root distance.
They lack saved robot/reference root xyz, root quaternions and joint vectors;
ordered joint names; immutable registration/clock identity; and a raw independent
reference-time binding sufficient for the new contract. The new raw tap records
poses/joints and native cursors, but registration and joint-library correspondence
still need collection-specific validation. The nominal collection below cannot
validate a nonzero disturbance. Existing push logs must be checked against
actual readback and event units before a disturbed trial is called verified.

The reporter trusts supplied delivery and explicit failure evidence as input
contracts; hash binding prevents file substitution but does not certify those
physical assertions. No report from the inspected real traces is presented as
verified recovery. The synthetic example explicitly asserts synthetic delivery
and produces accounting bounds [0.5, 1.0] for two scheduled disturbed IDs, one
complete and one absent. These numbers demonstrate accounting only.

## Complete scheduled accounting

`aggregate_trials` joins attempts onto immutable scheduled IDs with a preselected
primary attempt. Retries remain visible and cannot replace a failed primary.
Identical duplicate files are counted; conflicting duplicate attempts fail.
Missing primary files are U; controls have separate denominators. Reports expose
N = S + F + U, resolved fraction, reasons, all attempts and [S/N, (S+U)/N]. These
are accounting bounds, not confidence intervals. The CLI checks manifest and
recording hashes and retains file failures as unresolved rows unless independent
failure evidence was supplied. A confirmed pre-event failure never vanishes
because its push was not delivered.

## Smallest collection preparation — not launched

A one-environment nominal raw-capture preparation reuses the existing
`phys_000_s8720_on` evaluation command and origin from the source plan. This is a
short-clip instrumentation check, **not** a competent multi-motion origin choice,
recovery horizon test, or feedback experiment. No new bands are needed to collect
raw values. Existing legacy qualification outputs keep their old interpretation.

Prepared plan:
`/home/linjiw/lucid-sonic/experiments/task_truth_collection_d1_20260910_c/collection_plan.json`

Prepare-only command (executed; no simulator or W&B run launched):

```bash
source /home/linjiw/lucid/env/lucid_env.sh
python scripts/practice_utility/collect_native_task_truth.py \
  --source-plan /home/linjiw/lucid-sonic/experiments/recovery_execution_v2_20260907_a/plan.json \
  --cell phys_000_s8720_on \
  --output /home/linjiw/lucid-sonic/experiments/task_truth_collection_d1_20260910_c
```

An explicitly authorized collection adds `--execute-plan-sha256` with the SHA
printed by preparation. The launcher verifies the recomputed plan and source
input hashes, selects the existing worktree, and loads only the opt-in raw
collector extension. Its callback explicitly initializes online W&B under
`16726/lucid-sonic`, logs collection timing/counts and verifies the online run
before writing its URL receipt. This code is prepared, not live-tested; there is
no online URL to report. No resume is supported; use a new approved attempt ID
and output directory after an interruption. Source drift invalidates the prepared
SHA. The `_a` and `_b` preparations are superseded by `_c` after source formatting
and logging-provenance changes; none is an experiment retry or executed run.

After nominal frame/joint/terminal collection is verified, prepare one scheduled
nonzero pulse with before/readback state and unchanged reference. Do not expand
the collection into a large recovery campaign before this passes. A supported
existing recorder plus offline reporting remains the simpler implementation.

## Calibration and pilot freeze

1. Specify the physical path-and-stop task and acceptable position, height,
   heading, articulation and tilt errors from its purpose and measurement
   resolution. Record rationale in physical units; no values are selected here.
2. Characterize timestamp accuracy, registration repeatability, pose/joint
   precision and sample cadence. Choose dwell and horizon compatible with those
   resolutions and a sufficiently long recording; freeze pre-event window and
   terminal rules before comparing adapted policies.
3. Use origin-only calibration data to test feasibility, not to redefine task
   requirements as whatever the origin achieves. Select a capable shared
   multi-motion origin on separate development recordings and explicit nominal/
   original-envelope tracking, completion and effort budgets.
4. Lock thresholds, schedule, primary durable endpoint, aggregation, reporting
   costs and invalid-instrument/rerun rules; seal confirmation recordings and
   disturbances. An infeasible origin or task goes back to competence/task
   selection, not favorable threshold adjustment.

The smallest scientific pilot is Z/O/N: zero, synchronized oracle, and a declared
corrupted-oracle sensor-model branch through the same adapter. E replaces or
supplements N only when a named estimation process actually exists. Use one
competent shared origin, a small fixed recording mixture, identical trainable
capacity, fixed DR, constant anchoring and matched exposure/validation resources.
Independent origins are a later methods-confirmation requirement. Freeze event
schedules independently of resets; failures before events remain scheduled.
Require same-input initial mean/stochastic action parity, canonical std and
normalizers, matched actor information outside the controlled feedback channels,
and a working delivery audit before interpreting training.

Decision: no oracle gain → investigate information use/timing/task/actuation;
only oracle gain → sensing/latency problem; usable-feedback gain with retention
loss → preservation problem; usable-feedback gain within budgets → feedback ×
anchor and equally tuned simple baselines, then consider constrained learning.
No new curriculum, estimator, or constrained optimizer was implemented.

## Validation observed in this pass

The new adapter/accounting test file passes 17 analytical tests; the unchanged
legacy scorer file contributes 14 cases. The complete CPU suite freshly passed
**1,910 tests, four deprecation warnings, in 36.90 seconds**. Commands used the
workspace environment script and `python -m pytest tests/practice_utility/ -q`.
Changed Python files passed Black and Ruff. Collection code preparation and
Python compilation were checked; its live callback and online logging path
remain unexecuted. The prior 1,893-test receipt is not reused as new evidence.

Status: (a) offline contract/adapter/accounting implemented and CPU-tested;
(b) actual recording path not validated; (c) task-specific protocol not frozen.
D1 stays open. Stop infrastructure expansion after a real nominal/terminal and
single-event recording audit plus protocol freeze; proceed to the feedback pilot.
