# LUCID handoff — active H_R2 confirmation and next-tier gate

Snapshot: 2026-09-01 14:45 EDT. Read
`lucid-latest-report.md` for the scientific result and Tier 1–4 ledger. This
file is the operational continuation record.

## Current truth

The selected-seed Tier-1 screen passed, but the three-seed H_R2
stability/noninferiority decision is still running. Ratchet seed 8600 and the
fresh fixed seed-8602 comparator completed and are frozen read-only. Ratchet
seed 8602 is the third and final training cell. No new confirmation capability
cell has been scored, so H_R2 remains undecidable. Do not describe the current
seed-8601 `+3.125` frontier-success point estimate as a confirmed improvement
or a superiority result.

The active claim-bearing worktree is detached and clean at
`/home/linjiw/lucid-ratchet-confirm`, commit
`ca057e658acc59773e798057980b827d65988441`. Do not patch it or replace it
with the newer development branch.

Active ownership:

- serial driver PID: `221231`
- cell launcher PID: `411832`
- Isaac trainer PID: `411845`
- current cell: `lucid_ratchet_rg`, training seed 8602
- experiment: `curriculum_comparison_ne1024_20260901_100208`
- latest audited state: 2,303/8,000 rows, first lambda >= 0.95 at iteration
  65, lambda 1.0, 84 blocked PI decreases, zero guard trips, zero applied
  decreases, and all of the trailing 1,000 available rows at high lambda
- capsules present: H0500, H1000, H2000
- GPU: trainer PID 411845 only; do not launch another GPU process
- current log ETA: about 15:31 EDT for training completion; prior ladder
  timings put the final analysis near 16:05 EDT if no boundary fails

Current curriculum:

`/home/linjiw/lucid-sonic/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260901_100208/seed_8602/lucid_ratchet_rg/curriculum_curriculum_comparison_ne1024_20260901_100208_s8602_lucid_ratchet_rg.jsonl`

Current log:

`/home/linjiw/lucid-sonic/outputs/curriculum_comparison_ne1024_20260901_100208_s8602_lucid_ratchet_rg.log`

## Completed overnight evidence

Ratchet seed 8600 completed all 8,000 iterations in 19,324.6 seconds (5.37 h)
with exit code 0. Its mechanism trajectory independently passes H_R0: first
lambda >= 0.95 at iteration 64, final lambda 1.0, 453 blocked PI decreases,
zero guard trips, zero applied decreases, and 1,000/1,000 terminal iterations
at high lambda. Its frozen checkpoint is read-only, SHA-256
`0a178eff5b746323cb87217b412637b6391d33b5276254edb57786bf5b4b2cc8`.

Fresh fixed seed 8602 completed all 8,000 iterations in 19,238.6 seconds
(5.34 h) with exit code 0 and final lambda 1.0. Its frozen checkpoint is
read-only, SHA-256
`1e230abf2230362e2ad32e798fa85c50bf6130390dfdba4069dc3e0acb33e4e8`.
This is the H_R2 replacement comparator; the original reboot-killed campaign
cell remains absent and must not be described as recovered or resumed.

Five of six claim-bearing checkpoints are now frozen. Every recorded section
of those manifests currently matches its on-disk hash and size. Seed 8601 and
seed 8600 ratchet trajectories pass H_R0; seed 8602 is an interim mechanism
pass only until it reaches iteration 8,000. Training return is reported only
as telemetry and does not rank capability.

Checkpoint files and freeze manifests are mode 0444. Referenced configs,
curricula, and capsules are hash/size pinned and currently match, but remain
mode 0664; do not describe those auxiliary files as permission-immutable.
New evaluation status is 0/4 ladders and 0/56 new cells. The reused seed-8601
receipts contribute 28 cells only after the new ladders are complete.

## Automatic sequence

The running supervisor owns this exact remaining serial order:

1. finish and freeze ratchet seed 8602;
2. only after all six paired checkpoints are frozen, score four new 14-cell
   ladders: ratchet/fixed seed 8600 at eval seed 8700 and ratchet/fixed seed
   8602 at eval seed 8702;
3. reuse the exact ratchet/fixed seed-8601 ladders at eval seed 8701;
4. write the immutable 84-cell H_R2 analysis;
5. re-audit the locked panel tree after all four new ladders and record the
   post-evaluation inventory before making the final report claim.

Canonical root:

`/home/linjiw/lucid-sonic/manifests/ratchet_confirmation_20260831`

Expected final decision receipt:

`/home/linjiw/lucid-sonic/manifests/ratchet_confirmation_20260831/lucid_ratchet_confirmation_analysis.json`

Evaluation artifacts and logs:

- `/home/linjiw/lucid-sonic/artifacts/ratchet_confirmation_eval_20260831`
- `/home/linjiw/lucid-sonic/outputs/ratchet_confirmation_20260831`

## Zero-GPU work completed while the chain trained

Three receipts were committed without touching the confirmation worktree, the
GPU, or any artifact (commits `c9ccedb`, `4c40504`):

- `receipts/manifests/lucid_frontier_exposure_law_preregistration_20260901.json`
- `receipts/manifests/lucid_frontier_grid_v2_preregistration_20260901.json`
- `receipts/manifests/lucid_frontier_preregistration_amendment_20260901.json`

They establish that ratchet and fixed share an identical training distribution
over 98.75% of training, record the 2-of-6 anti-gating frequency and the return
inversion, freeze prediction P3, and fix the Phase-2 endpoint contamination
before any extrapolation cell exists. See `lucid-latest-report.md`.

**Next operational step after the driver completes**, in this exact order:

1. Read out the H_R2 verdict and score P1/P2 against the committed bands.
   A readout script is drafted in the session scratchpad.
2. Build the bridge worktree. No commit on `research/practice-utility`
   satisfies the four-file additive closure from `ca057e6`; a new clean
   detached worktree must be constructed with ONLY
   `analyze_ratchet_historical_bridge.py`, `run_ratchet_historical_bridge.sh`
   and their two tests added, modes 100755/100644, non-symlink, nlink 1.
3. Author and freeze the bridge preregistration. It requires 29 named
   frozen inputs, seven pinned code files, an exact 14-preset list, and its own
   SHA-256 exported as `LUCID_RATCHET_HISTORICAL_BRIDGE_PREREG_SHA256`. Six
   frozen inputs can only be filled after the H_R2 analysis exists. A draft
   with every computable value is in the session scratchpad.
4. Run the 42-cell bridge to score P3. Its activation accepts an H_R2 verdict
   of `pass` OR `fail`; only an H_R0 mechanism failure blocks it.
5. Only after P3: change the evaluator. It is byte-pinned at `308e2415` by the
   bridge and the screen followup.

### P3 input inventory — verified 2026-09-01 15:15, all present

Every pinned input the 42-cell bridge needs for the collapse arm `lucid_rg`
seed 8601 exists and hashes correctly against the driver's hard-coded tables:

| input | path | sha-256 | driver table |
|---|---|---|---|
| checkpoint | `.../ne1024_20260829_000249/seed_8601/lucid_rg/final_checkpoint.pt` | `e8ece9de91b5…d70e` | matches `EXPECTED_LUCID_CHECKPOINT_SHA256[8601]` |
| true config | `GR00T-WholeBodyControl/logs_rl/…/sonic_release_test-20260830_060944/config.yaml` | `9997fe63…3568` | matches `EXPECTED_LUCID_CONFIG_SHA256[8601]` |
| curriculum | `.../seed_8601/lucid_rg/curriculum_*.jsonl` | `3e98983a34b8896f…` | matches `EXPECTED_LUCID_CURRICULUM_SHA256[8601]` |
| environment | `/home/linjiw/lucid/env/lucid_env.sh` | `aa1827d1…d743` | matches the prereg pin |

Two traps worth knowing before staging:

- **The config is NOT adjacent to the checkpoint.** Six of eleven campaign arms
  have no `config.yaml` beside their artifact (`seed_8601/{lucid_rg,lucid_s4_rg,off}`
  and all three `seed_8602` arms); only the seed-8600 arms and `seed_8601/fixed`
  do. The true config lives in the training run's `logs_rl` output. This is
  exactly why the bridge stages a bundle with the config copied adjacent to the
  checkpoint, and why `--training-config` must be passed explicitly.
- **Staging must copy or reflink, never hardlink.** The driver asserts
  `st_nlink == 1` on both staged files and rejects symlinks.

Reading that config is safe for the live run: the confirmation driver pins
`sonic_release_test-20260830_002425` and `-20260831_144024` (plus `-231903` and
`-044119` in freeze manifests). The collapse arm's config is `-20260830_060944`,
a different directory.

Remaining construction, all absent today and all clean to create:
`/home/linjiw/lucid-ratchet-historical-bridge` (detached worktree),
`manifests/ratchet_historical_bridge_20260901`, the preregistration JSON, and
`artifacts/ratchet_historical_bridge_eval_20260901`.

The worktree needs a commit whose diff from `ca057e6` is EXACTLY four additions.
HEAD `1c947d2` differs by ten additions and four modifications, so no existing
commit qualifies. All four bridge blobs are already in the object store with the
required modes (`100755` for the `.sh`, `100644` for the other three), so the
commit can be built deterministically with `read-tree` + `update-index --cacheinfo`
+ `write-tree` + `commit-tree`.

## Decision boundary

H_R2 is a component-wise 2-of-3 noninferiority rule. All three ratchet
trajectories must first pass H_R0. For each of frontier success AUC, frontier
restricted-mean progress AUC, in-envelope success AUC, and in-envelope
restricted-mean progress AUC, ratchet must stay within the frozen margin on at
least two of three paired training seeds. Latency is secondary.

A pass authorizes only: the monotone ratchet is a stable/noninferior safety
constraint against late anti-gating. It does not authorize superiority and
does not rehabilitate latent gap as a valid difficulty signal. A fail leaves
fixed DR as the baseline and blocks Tier 2.

## Recovery rules

The driver is fail-closed. A cell directory containing `.started` without
exactly one complete valid terminal receipt is evidence of interruption.
Preserve it. Do not resume, delete, overwrite, or silently retrain. File a new
deviation before any replacement run.

A completed cell may be reused only after the driver revalidates its exact
hashes, config source, checkpoint identity, seed mapping, and complete run set.
An existing final analysis must reproduce from frozen inputs, ignoring only
its timestamp.

The machine reboot casualty
`sonic_release_test-20260831_114653` remains partial evidence only. Never
resume it.

## Panel preservation disclosure

Before any new H_R2 capability cell, an audit proved the live panel was still
the exact 512-alias tree created on August 28, then found that the frozen
evaluator/analyzer hashed only the panel JSON and did not independently hash
the mutable alias targets.

Two prospective operational receipts were committed before evaluation:

- preservation amendment: root commit `10849b9`, SHA-256
  `9366af3faa0ff6714ddb50368937f88e5b3211dead2a6882427d6c168fe31af9`
- activation: root commit `9726720`, SHA-256
  `8889cd94477a35278776c4481ea12dea9bd3b1ca77b6a9269b9dd82a04ce94e0`

The exact panel receipt, panel root, alias directory, and source inode had
their write bits removed. No bytes, paths, names, targets, hashes, or inodes
changed; active training continued afterward. Keep those objects read-only
through final analysis and compare a post-evaluation inventory.

This is accidental-mutation protection, not WORM storage. Higher ancestors
remain trusted, and the reused seed-8601 panel has forensic continuity rather
than retroactive cryptographic immutability. Preserve that limitation in the
final report.

## Durable code state

Current development-branch SONIC HEAD is `1c947d2`. It is not the active H_R2
worktree. New commits, in order:

- `c33662d` — strict Tier-2 support analyzer
- `bee67e8` — bind historical live panel aliases
- `1290416` — pin the support environment bootstrap
- `c64487a` — dormant historical-bridge supervisor
- `1c947d2` — dormant Tier-2 support supervisor

The historical bridge is descriptive and nonbinding. It requires terminal H_R2
plus all H_R0 gates, a future frozen preregistration, a clean detached
`ca057e6`-based four-file additive worktree, staged non-hardlinked historical
checkpoints with their true adjacent configs, and 42 new exact cells. It cannot
alter H_R2.

The Tier-2 support screen is also dormant. It requires an H_R2 pass, a future
frozen preregistration, three new 1,024-env x 8,000-iteration training cells
(fresh fixed, fixed-150, fixed-u150), four frozen policies including the
historical fixed comparator, and 60 exact raw k512 evaluation cells. It is a
screening preference rule, not a superiority test.

Focused validation on current SONIC HEAD:

- controller/freeze/confirmation/historical/support matrix: 235 passed
- historical driver plus analyzer: 44 passed
- support driver plus analyzer: 52 passed
- Black/Ruff/Bash syntax/py_compile checks: pass for the new files
- repository-wide `make run-checks`: still blocked by unrelated pre-existing
  isort failures

## Tier status and contingent research plan

### Tier 1 — controller safety

**Status:** active confirmation. The selected seed-8601 screen remains a pass
with descriptive ratchet-minus-fixed gains of +3.125 points frontier success
AUC and +1.933 points frontier restricted-mean progress AUC. Seeds 8600 and
8601 now give two complete clean ratchet mechanism passes; seed 8602 is clean
so far. There are no new seed-8600/8602 capability results.

**Next:** finish the automatic H_R2 chain and apply only the frozen 84-cell,
component-wise 2-of-3 rule. If it passes, claim stability/noninferiority of the
ratchet constraint only. If it fails, retain fixed DR, stop the ratchet line,
and diagnose the failed paired components before authorizing another GPU arm.
Raw latent gap remains invalid either way.

### Historical closure — nonbinding

If H_R2 is terminal and all three H_R0 trajectories pass, the cheapest useful
follow-up is the separately preregistered 42-cell historical `lucid_rg` bridge.
It directly describes whether the ratchet recovered the predeclared seed-8601
collapse interaction under the identical instrument. It cannot alter H_R2 and
must use the clean four-file additive `ca057e6` worktree.

### Tier 2 — support expansion

**Status:** code-ready, experimentally unknown, and blocked on H_R2 pass. The
strict one-seed screen compares historical fixed, fresh fixed, pure fixed-150,
and the 75%-frontier `fixed_u150` distribution on 60 raw k512 cells. It needs
three fresh 1,024-env x 8,000-iteration seed-8600 training cells and a new
immutable preregistration; the stale untracked `run_fixed_u150_arm.sh` is not
authorized.

**Next if H_R2 passes:** create a clean detached worktree at current reviewed
code, freeze a new preregistration and comparator lineage, then run
`run_support_screen.sh`. A candidate must gain at least 2 points of frontier
success AUC and 3 points of mean hard-cell success while meeting progress and
in-envelope noninferiority floors. If neither fixed-150 nor fixed-u150 passes,
stop support expansion. If both pass, prefer fixed-u150 only for a >2-point
frontier advantage or >1-point nominal recovery with frontier loss no worse
than 2 points; otherwise prefer pure fixed-150. Any winner remains a one-seed
screen and needs a later multi-seed confirmation.

### Tier 3 — difficulty-aware optimization

**Status:** no performance evidence. Only the consolidation override plumbing
bug is fixed; per-stratum advantage normalization, PopArt-lite, critic DR
context, and phase-change coupling are unrun.

**Next:** authorize per-stratum advantage normalization only if Tier 2 shows
that a support mixture retains frontier exposure but loses through optimizer
interference. If pure fixed-150 wins cleanly, first confirm support extension
across seeds rather than adding optimizer complexity. Critic-only DR context
defines a new campaign generation.

### Tier 4 — evaluation and claim boundaries

**Status:** the locked v1 instrument is valid for this narrow same-motion H_R2
decision and must not change mid-chain. It still measures 512 aliases of the
training clip, not held-out-motion generalization.

**Next:** immediately after H_R2, compare the post-evaluation panel inventory
with the pre-lock receipt and publish survival/restricted-mean failure-time
tables from existing arrays. In a separately preregistered v2, prioritize
first-termination-masked quality and four held-out k128 motion panels; then add
realized-draw/channel attribution, one compositional cell, and capsule
retention curves.

## Read-only monitoring

```bash
ps -o pid,ppid,etimes,stat,cmd -p 221231,411832,411845

jq -sc '{
  rows:length,
  first_high:([.[]|select(.lambda>=0.95)|.global_step]|first),
  final_lambda:.[-1].lambda,
  binds:([.[]|select(.latch_active)]|length),
  guards:([.[]|select(.guard_tripped)]|length),
  decreases:([.[]|select((.lambda_after // .lambda) < ((.lambda_before // .lambda)-1e-12))]|length)
}' /home/linjiw/lucid-sonic/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260901_100208/seed_8602/lucid_ratchet_rg/curriculum_curriculum_comparison_ne1024_20260901_100208_s8602_lucid_ratchet_rg.jsonl
```

Do not stage the unrelated untracked Gate-A/learnability files or the
`GR00T-WholeBodyControl-plr/` worktree. Preserve the modified PLR queue-status
mirror as unrelated append-only state.
