# LUCID — When Training Gets Easier

**[Project page](https://linjiw.github.io/lucid/)** · **[Working manuscript](paper/when-training-gets-easier.md)** · **[September 7 science freeze](lucid-icra-freeze-2026-09-07.md)**

We are preparing a diagnostic ICRA paper on training-range collapse and tracking-quality drift in humanoid robustness training, following `fable.md` and `fable.html`. The completed evidence supports safeguards and bounded development findings, not adaptive-curriculum superiority.

**Current experiment:** second continuation seed of R0 versus reference-anchored R1, from the same local origin. Two 2,000-iteration runs and 55 fixed-policy evaluation cells; online [W&B logging](https://wandb.ai/16726/lucid-sonic/runs/p4rvttfe). R0 training is complete; R1 is running after a logging-only repair with verified R0 reuse. Results are pending. The completed first seed gives R1 +4.33% nominal global error and +5.18 percentage points hard-condition qualification versus origin, within the empirical retention checks.

The recovery-aware multi-motion programme is future work. Its path-input pilot and sixteen evaluations are complete; the sideways push endpoint includes two failures in 128 trials. It does not provide calibrated recovery evidence for this manuscript.

Workspace repo for the LUCID research program. Code lives in two submodules; the
claim-bearing work is in `GR00T-WholeBodyControl` on branch `research/practice-utility`.
Everything needed to *reason about* the results (plans, guidance, receipts) is here;
everything needed to *re-run* them is in the submodule plus the data root described below.

## Layout

| path | what |
|---|---|
| `site/index.html` | **Current public overview:** research objective, completed results, latest experiment and next gates |
| `fable.md` / `fable.html` | **Current guidance (2026-09-07): minimal path to the ICRA 2027 submission** |
| `fable-archive-2026-09-02.md` | Historical guidance and dated execution log (Aug 26 – Sep 2) |
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
