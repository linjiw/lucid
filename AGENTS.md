# Repository Guidelines

## Project Structure & Module Organization

This workspace contains two nested Git repositories plus project-level research notes. `GR00T-WholeBodyControl/` is the claim-bearing SONIC codebase. LUCID additions belong in `gear_sonic/research/practice_utility/`, executable workflows in `scripts/practice_utility/`, and matching tests in `tests/practice_utility/`. `whole_body_tracking/` is the BeyondMimic sandbox; its package lives under `source/whole_body_tracking/whole_body_tracking/`, with training and replay entry points in `scripts/`. Root `lucid-*.md` files record the proposal, design, and handoff. Keep generated checkpoints, logs, datasets, and manifests outside Git; media and checked-in robot resources remain under each project's existing `media/`, `data/assets/`, or `sim2mujoco/resources/` trees.

## Build, Test, and Development Commands

For SONIC work, initialize the pinned Isaac environment first:

```bash
source /data/robotixx/lucid-sonic/lucid_env.sh
cd GR00T-WholeBodyControl
pytest tests/practice_utility/   # CPU measurement and contract suite
make run-checks                 # isort, Black, and Ruff checks
make format                     # apply isort and Black
```

Install editable packages from their repository roots: `pip install -e "gear_sonic[training]"`, `pip install -e "decoupled_wbc[dev]"`, or, in `whole_body_tracking/`, `python -m pip install -e source/whole_body_tracking`. BeyondMimic training uses `python scripts/rsl_rl/train.py --task=Tracking-Flat-G1-v0 ...`. GPU/Isaac integration runs are environment-dependent; document the exact command and config in the resulting receipt.

## Coding Style & Naming Conventions

Use four-space Python indentation, `snake_case` for modules/functions, `PascalCase` for classes, and explicit type hints for public interfaces. Follow the nearest `pyproject.toml`: SONIC uses Black (100 columns), Ruff (115), and isort; BeyondMimic uses Black/isort at 120 columns, Pyright, and pre-commit. Preserve upstream SONIC semantics by placing research behavior behind flags or runtime seams.

## Testing Guidelines

Name files `test_<feature>.py` and tests `test_<behavior>`. Add unit tests for schema and numerical invariants, plus regression tests for identity, no-op parity, resume behavior, and deterministic receipts. No numeric coverage threshold is configured; changed research logic must have focused tests. Run CPU tests before any expensive simulator job.

## Commit & Pull Request Guidelines

Commit within the affected nested repository. Follow recent scoped subjects: `fix(lucid): ...`, `test(lucid): ...`, or `research(practice-utility): ...`; keep each commit single-purpose and imperative. Pull requests should state the hypothesis or bug, affected configs, validation commands/results, and linked issue. Include receipt or artifact paths for experiments and screenshots only for visual changes. Never commit credentials, W&B tokens, large motion packs, or generated checkpoints.

## Research-Specific Instructions

Read `lucid-handoff-2026-08-20.md` and the relevant design section before changing experiments. Do not build the utility estimator or residual allocator until their documented gates pass, and keep BeyondMimic sandbox results out of claim-bearing SONIC tables.
