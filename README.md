# LUCID — practice utility & target-anchored curricula on SONIC (ICRA 2027 push)

Workspace repo for the LUCID research program. Code lives in two submodules; the
claim-bearing work is in `GR00T-WholeBodyControl` on branch `research/practice-utility`.
Everything needed to *reason about* the results (plans, guidance, receipts) is here;
everything needed to *re-run* them is in the submodule plus the data root described below.

## Layout

| path | what |
|---|---|
| `fable.md` | **Start here.** Fable's guidance + dated execution log (results, decisions, next steps) |
| `lucid-design-implementation-plan.md` | long-form design doc, §0–25 (gates, estimands, results through 2026-08-21) |
| `lucid-handoff-2026-08-20.md` | agent handoff: environment, rules of engagement, measured results ledger |
| `docs/` | TACE design, LUCID-MC/IROS plan, cross-domain curriculum-learning review, **machine setup** |
| `lucid-original-paper.md`, `lucid-proposal.md`, `lucid-sonic.md` | source documents |
| `receipts/manifests/` | **every experiment receipt** (JSON, git SHA + seeds + verified/not-verified split), mirrored from `$LUCID_ROOT/manifests/` |
| `env/lucid_env.sh` | the environment script every run must source (python stack, `LUCID_ROOT`, TMPDIR, PYTHONPATH, threads); host-independent |
| `autoresearch/` | ledgers of the Aug 20 autoresearch iterations |
| `GR00T-WholeBodyControl/` | submodule → `linjiw/GR00T-WholeBodyControl-lucid`, branch `research/practice-utility` (fork of NVlabs; upstream files untouched, all research under `gear_sonic/research/practice_utility/`, `scripts/practice_utility/`, `tests/practice_utility/`) |
| `whole_body_tracking/` | submodule → HybridRobotics upstream @ `cd65172` (BeyondMimic; DR/latency sandbox only, unmodified) |

## Reproducing on another machine

1. `git clone --recurse-submodules git@github.com:linjiw/lucid.git`
2. Environment: IsaacLab 2.3.2 / IsaacSim 5.1.0 / torch 2.7.0+cu128 (sm_120), as either a
   conda env `sonic` or a uv venv. `source env/lucid_env.sh` before any python — it is
   host-independent (derives the workspace from its own path, auto-detects the python stack,
   and picks `LUCID_ROOT`). `docs/machine-setup.md` records what is host-specific and how a
   second host was brought up.
3. Data root (`LUCID_ROOT`, not in git — ~tens of GB): `pools/` (BONES-SEED motion pools + splits),
   `sonic_release/` (SONIC release checkpoint `model_step_041550.pt`), `artifacts/lucid_encoder_debug512.pt`
   / `lucid_encoder_adapt4950.pt` (frozen encoders), and the settled origin checkpoint
   `logs_rl/.../sonic_release_test-20260818_141446/model_step_000024.pt`. Every receipt in
   `receipts/manifests/` records the sha256 of the checkpoints, pools and splits it used, so a
   re-created data root can be verified against them.
4. CPU tests (no GPU): `pytest tests/practice_utility/` inside the submodule (1,143 passed / 13 skipped as of 2026-08-28;
   the skips need the frozen encoder artifacts).
5. Drivers (GPU): `scripts/practice_utility/run_tace_pilot.sh` → `run_tace_yoked_cross.sh` →
   `run_tace_horizon.sh` → `run_tace_off128.sh` chain via markers in `outputs/tace_pilot_driver.log`;
   `analyze_tace_pilot.py` scores the preregistered hypotheses from receipts.

## Rules of engagement (short)

Never edit upstream SONIC files; every run writes a receipt; preregister before looking;
branches start from settled origins with last-4 efficacy; report negative results. Full
version: `lucid-handoff-2026-08-20.md` §6.
