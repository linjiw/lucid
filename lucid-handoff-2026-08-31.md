# LUCID handoff — Tier-1 ratchet confirmation

> Confirmation update (2026-08-31 23:20 EDT): the one-seed screen passed and
> the parent-preregistered H_R2 continuation is now frozen, committed, and
> preflight-verified. This section supersedes the older process snapshot below.

## Active confirmation handoff

The exact claim-bearing SONIC state is commit
`ca057e658acc59773e798057980b827d65988441`
(`research(practice-utility): harden ratchet confirmation`). It is checked out
detached and clean at `/home/linjiw/lucid-ratchet-confirm`. Do not launch the
confirmation from the dirty source worktree.

Binding prospective amendment:

- external: `~/lucid-sonic/manifests/lucid_monotone_ratchet_confirmation_amendment_20260831.json`
- repository mirror: `receipts/manifests/lucid_monotone_ratchet_confirmation_amendment_20260831.json`
- SHA-256: `2064bf7a16ca159092c6ebeabfbf09bc2fe3c1b30ce359a64505503a83786044`
- preflight: passed, including every frozen file hash and the exact old/new
  config provenance contract

The serial driver is
`/home/linjiw/lucid-ratchet-confirm/scripts/practice_utility/run_ratchet_confirmation.sh`.
Its only valid launch environment is:

```bash
LUCID_RATCHET_CONFIRM_PREREG_SHA256=2064bf7a16ca159092c6ebeabfbf09bc2fe3c1b30ce359a64505503a83786044 \
  /home/linjiw/lucid-ratchet-confirm/scripts/practice_utility/run_ratchet_confirmation.sh
```

The driver performs one-cell receipt boundaries in this order:

1. validate the immutable seed-8601 screen and fixed 8600/8601 historical
   bridges;
2. mark reused fixed-8600, fixed-8601, and ratchet-8601 checkpoints read-only;
3. train/freeze ratchet seed 8600 from scratch;
4. train/freeze missing fixed seed 8602 from scratch;
5. train/freeze ratchet seed 8602 from scratch;
6. only after all six checkpoints are frozen, score ratchet/fixed seed 8600
   with eval seed 8700 and ratchet/fixed seed 8602 with eval seed 8702;
7. reuse the exact two seed-8601 eval-seed-8701 receipts and write the strict
   84-cell H_R2 analysis.

Canonical continuation root:
`~/lucid-sonic/manifests/ratchet_confirmation_20260831/`. Training receipts,
evaluation receipts, frozen-checkpoint manifests, and the final
`lucid_ratchet_confirmation_analysis.json` live below it. Logs and bulky eval
artifacts remain under `~/lucid-sonic/outputs/ratchet_confirmation_20260831/`
and `~/lucid-sonic/artifacts/ratchet_confirmation_eval_20260831/`.

Active process snapshot at 23:20 EDT:

- driver PID 221231, started 23:18:41;
- first-cell launcher PID 222084;
- trainer PID 222101;
- experiment `curriculum_comparison_ne1024_20260831_231901`;
- log `~/lucid-sonic/outputs/curriculum_comparison_ne1024_20260831_231901_s8600_lucid_ratchet_rg.log`;
- first observed curriculum state: 13 rows, lambda 0.05835, zero guard trips.

Do not start another GPU job while this tree is alive. Read-only monitoring:

```bash
ps -o pid,ppid,etimes,stat,cmd -p 221231,222084,222101
tail -n 30 ~/lucid-sonic/outputs/curriculum_comparison_ne1024_20260831_231901_s8600_lucid_ratchet_rg.log
jq -sc '{rows:length,last:.[-1],binds:([.[]|select(.latch_active)]|length),guards:([.[]|select(.guard_tripped)]|length)}' \
  ~/lucid-sonic/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260831_231901/seed_8600/lucid_ratchet_rg/curriculum_curriculum_comparison_ne1024_20260831_231901_s8600_lucid_ratchet_rg.jsonl
```

The amendment's embedded `created_at=23:20:00` is a manual timestamp error:
the exact file mtime is 23:16:10, root commit `9b5879f` locked its blob at
23:18:08, and the active driver began at 23:18:41. Do not rewrite the binding
file. The post-launch correction is
`receipts/manifests/ratchet_confirmation_20260831/ratchet_confirmation_launch_provenance_20260831.json`
(SHA-256 `189de9bb43610325cf4ac6931f064efe4372ae88344d8524fa9dd33adbcbed2b`).

Recovery is deliberately fail-closed. A `.started` directory without exactly
one complete receipt means the cell was interrupted: preserve it, do not
resume or auto-retrain, and file a new deviation before any replacement. A
completed receipt may be reused only after the driver revalidates its hashes,
config source, seed map, and full run set. An existing final analysis is
recomputed into a temporary file and must match every scientific field before
reuse.

H_R2 passes only if all three ratchet H_R0 trajectories pass and each of the
four AUC components separately stays within its frozen margin in at least two
of three paired seeds. Latency is secondary. A pass authorizes
stability/noninferiority only; a fail retains fixed DR as the baseline. Tier 2
is outside this driver and requires a separate prospective preregistration
after H_R2 is immutable.

> Completion update (2026-08-31 22:32 EDT): the live chain described below
> finished successfully. The ratchet passed its targeted seed-8601 screen;
> no directional claim is yet authorized. Use `lucid-latest-report.md` as the
> current status, result, Tier 1–4 ledger, and next-action handoff. The process
> IDs and “training now” language below are retained as a historical snapshot.

Snapshot: 2026-08-31 16:27 EDT. This document is intentionally operational: a
later agent should be able to continue without reconstructing the 26-agent
frontier audit or guessing which live process owns the GPU.

## Executive state

The legacy latent-gap curriculum is not being repaired or relaunched. Its
signal is policy effort, not calibrated difficulty, and it anti-gated two of
six completed controller cells. The first post-reboot experiment is therefore
the smallest signal-agnostic Tier-1 constraint that deletes that failure mode:
`lucid_ratchet_rg`, the existing unstratified `lucid_rg` controller with PI-law
difficulty decreases projected away. The relative return guard remains the
only legal downward path.

The targeted seed-8601 screen is training now. It is not a capability result
yet. At this snapshot it was healthy around iteration 2,400/8,000: lambda first
crossed 0.95 at iteration 70, was currently 1.0, had hundreds of blocked PI
decrease requests, zero guard trips, and zero unguarded applied decreases.
Training should finish around 20:40–20:50 EDT; the serial ratchet and fixed
14-cell ladders add about 26 minutes.

## Durable code and evidence

The SONIC implementation is committed in the nested repository:

- repository: `GR00T-WholeBodyControl/`
- branch: `research/practice-utility`
- commit: `3457718f30b74bd6bca9d7dd439be0e53dbbde43`
- subject: `research(practice-utility): add ratchet frontier screen`

That commit contains the ratchet arm, controller/callback state, strict frozen
analyzer, resumable follow-up driver, support-expansion seams, corrected
lambda=1.5 startup/telemetry, consolidation forwarding, and focused tests.

Binding external evidence:

- `~/lucid-sonic/manifests/lucid_monotone_ratchet_preregistration_20260831.json`
- `~/lucid-sonic/manifests/lucid_monotone_ratchet_endpoint_clarification_20260831.json`
- `~/lucid-sonic/manifests/lucid_ratchet_fixed_s8601_baseline.json`
- `~/lucid-sonic/manifests/lucid_ratchet_postlaunch_commit_provenance_20260831.json`

The endpoint clarification was written before any ratchet capability cell was
scored. “RMS-progress” means restricted-mean normalized episode progress—the
existing `progress_rate = mean(per-episode progress)`—not root-mean-square.

## Live process ownership

At the snapshot:

- training launcher PID: `51631`
- Isaac trainer PID: `51656`
- post-training supervisor PID: `61925`
- GPU compute owner: trainer PID `51656` only
- experiment: `curriculum_comparison_ne1024_20260831_144022`
- branch: `curriculum_comparison_ne1024_20260831_144022_s8601_lucid_ratchet_rg`

Do not start another GPU job, evaluator, analyzer, supervisor, old campaign,
PLR queue, margin arm, fixed-150 arm, or fixed-u150 arm while this chain is
alive.

Canonical live paths:

- training log: `~/lucid-sonic/outputs/curriculum_comparison_ne1024_20260831_144022_s8601_lucid_ratchet_rg.log`
- curriculum JSONL: `~/lucid-sonic/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260831_144022/seed_8601/lucid_ratchet_rg/curriculum_curriculum_comparison_ne1024_20260831_144022_s8601_lucid_ratchet_rg.jsonl`
- expected checkpoint: same arm directory, `final_checkpoint.pt`
- expected training receipt: `~/lucid-sonic/manifests/curriculum_comparison_ne1024_20260831_144022.json`
- treatment evaluation directory: `~/lucid-sonic/manifests/ratchet_screen_20260831/treatment/`
- fixed evaluation directory: `~/lucid-sonic/manifests/ratchet_screen_20260831/fixed/`
- final analysis: `~/lucid-sonic/manifests/lucid_ratchet_screen_analysis_s8601_20260831.json`

The supervisor is
`GR00T-WholeBodyControl/scripts/practice_utility/run_ratchet_screen_followup.sh`.
Leave the existing process alone. It waits for the exact complete training
receipt, waits for an idle compute GPU, scores treatment then fixed with eval
seed 8701, requires exactly 14 successful cells per arm plus frozen panel,
evaluator, config, and checkpoint identities, then runs the strict analyzer.
It reuses one verified receipt at a completed boundary and refuses partial,
ambiguous, or existing-analysis overwrites.

Useful read-only monitoring:

```bash
ps -o pid,ppid,etimes,stat,cmd -p 51631,51656,61925
tail -n 20 ~/lucid-sonic/outputs/curriculum_comparison_ne1024_20260831_144022_s8601_lucid_ratchet_rg.log
jq -sc '{rows:length, final:.[-1], binds:([.[]|select(.latch_active)]|length), guards:([.[]|select(.guard_tripped)]|length)}' \
  ~/lucid-sonic/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260831_144022/seed_8601/lucid_ratchet_rg/curriculum_curriculum_comparison_ne1024_20260831_144022_s8601_lucid_ratchet_rg.jsonl
```

## Frozen decision contract

This seed was selected after observing old seed-8601 `lucid_rg` collapse, so it
is a targeted mechanistic screen, not a blinded efficacy seed and not a
directional claim.

- H_R0: lambda reaches at least 0.95 by iteration 500; every non-guard decrease
  is blocked; at least 95% of the final 1,000 iterations are at lambda>=0.95.
- H_R1: ratchet-minus-fixed is at least -0.02 for frontier success AUC and
  frontier progress AUC over phys_125–200, and at least -0.01 for the two
  in-envelope AUCs over phys_000–100.
- `lat_50ms` is secondary and cannot decide H_R1.
- One seed always remains `screening_only`, even if all four margins pass.
- H_R2 later requires each component margin in at least two of three paired
  training seeds. Strict superiority is not preregistered.

Decision actions:

1. `screen_pass`: authorize only new preregistered ratchet seeds 8600/8602 plus
   the missing from-scratch fixed seed 8602. Do not claim superiority.
2. `screen_fail` with H_R0 pass: the ratchet deletes collapse but does not
   preserve capability. Stop scalar-gap scheduling and retain fixed DR.
3. H_R0 failure: capability interpretation is void; report a mechanism or
   implementation failure and preregister any rerun.
4. Confirmatory H_R2 pass: describe ratchet only as a stability/noninferiority
   constraint. H_R2 fail: fixed DR remains the baseline.

## Provenance disclosure caused by the requested live commit

Training launched at 14:40 from HEAD `fb57e86` with a dirty worktree whose
claim-bearing files were SHA-pinned in the preregistration. At 16:25, while the
already-imported trainer continued, those exact bytes were captured in commit
`3457718`; no claim-bearing file changed. Because the launcher resolves
`git_sha` only when it writes its terminal receipt, that receipt will likely
name `3457718`, not the launch-time HEAD. This is a disclosed timing deviation,
not executable-content drift. The authoritative bridge is
`lucid_ratchet_postlaunch_commit_provenance_20260831.json`.

Do not amend the preregistration or rewrite the implementation commit to hide
this timing. Report it.

## Validation completed

- exact legacy controller replay on all six completed latent-controller cells:
  maximum lambda error zero
- counterfactual ratchet replay: final lambda=1 and 1,000/1,000 terminal
  high-frontier iterations in all six cells
- focused ratchet/callback/launcher/evaluator/analyzer suite: 144 passed
- all relevant `tests/practice_utility` tests excluding the separate untracked
  bin-sampler suite: 1,392 passed, four pre-existing warnings
- `git diff --check`: pass
- repository-wide `make run-checks`: still blocked by broad pre-existing
  upstream/nested isort failures; no unrelated formatter was applied

The separate untracked bin-sampler suite previously produced 37 passes and
three failures. Those failures and files are not part of commit `3457718`.

## Tier plan and progress

| Tier | State | Next honest action |
|---|---|---|
| 0 recovery | Legacy reboot casualties preserved; stale “coverage closed” claim corrected; receipts mirrored locally | Do not resume seed-8602/off. Rebuild missing comparators only under a new explicit plan after this screen. |
| 1 signal | Ratchet implemented, preregistered, committed, and training; competence latch remains default-off | Finish the automatic screen. Confirm only if H_R0/H_R1 permit it. Do not rehabilitate raw latent gap. |
| 2 distribution | `fixed_u`/`fixed_u150` 75%-frontier support seams and lambda=1.5 startup/telemetry contracts implemented | Before any run, correct the fixed-u150 prereg timestamp and stale hashes, choose an honest comparator cohort, and file a new immutable launch record. |
| 3 optimization | Consolidation forwarding bug fixed; no optimizer arm run | After Tier-2 evidence, preregister per-stratum advantage normalization as the cleanest mechanism test. Critic DR-context conditioning requires a new campaign generation. |
| 4 evaluation | Ratchet analyzer now fail-closes on the exact 14-cell instrument and unchanged checkpoints | Add survival/restricted-mean tables, first-termination-masked prefix-K quality, realized-draw/channel cells, capsule retention, and held-out motions only in a separately frozen instrument revision. |

The strategic ordering remains: stabilize frontier exposure first (Tier 1),
then test support expansion (Tier 2), then optimizer-side mixture handling
(Tier 3), while upgrading claim boundaries and failure-time instrumentation
(Tier 4). Do not queue all tiers at once.

## Failure and reboot recovery

- Training dies before a verified terminal receipt: preserve partial artifacts,
  do not resume, and do not auto-retrain. Request an explicitly authorized
  from-scratch rerun with a new identity and deviation record.
- Supervisor sees trainer death without a receipt: it exits after five
  one-minute checks.
- Reboot after one complete evaluation: restart the same supervisor; it will
  reuse a verified treatment or fixed receipt.
- Partial/invalid evaluation receipt: fail closed. Do not delete, rename, or
  overwrite it automatically; preserve and adjudicate.
- Existing analysis receipt: do not rerun or overwrite it.

## Intentionally uncommitted work

The nested SONIC worktree still contains unrelated concurrent Gate-A/bin-sampler
files. They were preserved and deliberately excluded from `3457718`:

- `gear_sonic/research/practice_utility/bin_sampler.py`
- `gear_sonic/research/practice_utility/learnability_gate.py`
- `scripts/practice_utility/audit_evaluation_receipt.py`
- `scripts/practice_utility/run_fixed_u150_arm.sh`
- `scripts/practice_utility/run_gate_a.py`
- `tests/practice_utility/test_bin_sampler.py`
- `tests/practice_utility/test_learnability_gate.py`

The root repo also contains the separate untracked `GR00T-WholeBodyControl-plr/`
worktree. Do not fold any of these into a cleanup commit without auditing their
ownership and frozen preregistrations. The mirrored PLR queue-status JSON has a
large append-only polling-history change; it is intentionally not included in
the handoff commit.
