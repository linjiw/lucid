# LUCID handoff — active H_R2 confirmation and next-tier gate

Snapshot: 2026-09-01 00:56 EDT. Read
`lucid-latest-report.md` for the scientific result and Tier 1–4 ledger. This
file is the operational continuation record.

## Current truth

The selected-seed Tier-1 screen passed, but the three-seed H_R2
stability/noninferiority decision is still running. No new confirmation
capability cell has been scored. Do not describe the current seed-8601
`+3.125` frontier-success point estimate as a confirmed improvement or a
superiority result.

The active claim-bearing worktree is detached and clean at
`/home/linjiw/lucid-ratchet-confirm`, commit
`ca057e658acc59773e798057980b827d65988441`. Do not patch it or replace it
with the newer development branch.

Active ownership:

- serial driver PID: `221231`
- cell launcher PID: `222084`
- Isaac trainer PID: `222101`
- current cell: `lucid_ratchet_rg`, training seed 8600
- experiment: `curriculum_comparison_ne1024_20260831_231901`
- latest audited state: 2,282/8,000 rows, first lambda >= 0.95 at iteration
  64, lambda 1.0, 190 blocked PI decreases, zero guard trips, zero applied
  decreases
- capsules present: H0500, H1000, H2000
- GPU: trainer PID 222101 only; do not launch another GPU process

Current curriculum:

`/home/linjiw/lucid-sonic/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260831_231901/seed_8600/lucid_ratchet_rg/curriculum_curriculum_comparison_ne1024_20260831_231901_s8600_lucid_ratchet_rg.jsonl`

Current log:

`/home/linjiw/lucid-sonic/outputs/curriculum_comparison_ne1024_20260831_231901_s8600_lucid_ratchet_rg.log`

## Automatic sequence

The running supervisor owns this exact serial order:

1. finish and freeze ratchet seed 8600;
2. train and freeze fresh fixed seed 8602;
3. train and freeze ratchet seed 8602;
4. only after all six paired checkpoints are frozen, score four new 14-cell
   ladders: ratchet/fixed seed 8600 at eval seed 8700 and ratchet/fixed seed
   8602 at eval seed 8702;
5. reuse the exact ratchet/fixed seed-8601 ladders at eval seed 8701;
6. write the immutable 84-cell H_R2 analysis.

Canonical root:

`/home/linjiw/lucid-sonic/manifests/ratchet_confirmation_20260831`

Expected final decision receipt:

`/home/linjiw/lucid-sonic/manifests/ratchet_confirmation_20260831/lucid_ratchet_confirmation_analysis.json`

Evaluation artifacts and logs:

- `/home/linjiw/lucid-sonic/artifacts/ratchet_confirmation_eval_20260831`
- `/home/linjiw/lucid-sonic/outputs/ratchet_confirmation_20260831`

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

## Tier progression

- Tier 1: wait for immutable H_R2. Do not infer capability from training return.
- Tier 2: launch only if H_R2 passes and only after creating a new immutable
  preregistration and clean detached worktree for `run_support_screen.sh`.
- Tier 3: do not launch. Use Tier-2 evidence to decide whether per-stratum
  advantage normalization is warranted.
- Tier 4: keep the current H_R2 instrument fixed. Termination-safe quality,
  held-out motions, realized draws, channel cells, and retention belong to a
  separately preregistered v2 instrument.

## Read-only monitoring

```bash
ps -o pid,ppid,etimes,stat,cmd -p 221231,222084,222101

jq -sc '{
  rows:length,
  first_high:([.[]|select(.lambda>=0.95)|.global_step]|first),
  final_lambda:.[-1].lambda,
  binds:([.[]|select(.latch_active)]|length),
  guards:([.[]|select(.guard_tripped)]|length),
  decreases:([.[]|select((.lambda_after // .lambda) < ((.lambda_before // .lambda)-1e-12))]|length)
}' /home/linjiw/lucid-sonic/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260831_231901/seed_8600/lucid_ratchet_rg/curriculum_curriculum_comparison_ne1024_20260831_231901_s8600_lucid_ratchet_rg.jsonl
```

Do not stage the unrelated untracked Gate-A/learnability files or the
`GR00T-WholeBodyControl-plr/` worktree. Preserve the modified PLR queue-status
mirror as unrelated append-only state.
