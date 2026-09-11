"""Numerical contracts for the portable diagnostic analysis."""

import importlib.util
from pathlib import Path
import pytest

SPEC = importlib.util.spec_from_file_location(
    "diagnostic", Path(__file__).parents[1] / "tools/analyze_diagnostic_data.py"
)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def panel(g=100, l=20, s=1):
    return {"global_mm": g, "local_mm": l, "completion": s}


def test_gate_checks_envelope_local_and_completion_independently():
    origin = {c: panel() for c in M.PROTECTED}
    current = {"phys_000": panel(), "phys_100": panel(l=23)}
    assert M.retention_gate(current, origin)["D_pct"] == pytest.approx(15)
    assert not M.retention_gate(current, origin)["passes"]
    current["phys_100"] = panel(s=0.97)
    assert not M.retention_gate(current, origin)["passes"]


def test_improvements_are_not_clamped_to_zero_and_missing_cells_fail():
    origin = {c: panel(s=0.9) for c in M.PROTECTED}
    current = {c: panel(g=90, l=18, s=1) for c in M.PROTECTED}
    result = M.retention_gate(current, origin)
    assert result["D_pct"] == pytest.approx(-10)
    assert result["L_pp"] == pytest.approx(-10)
    assert result["passes"]
    with pytest.raises(KeyError):
        M.retention_gate({"phys_000": panel()}, origin)


def test_frontier_integral_starts_at_125_and_has_trapezoid_weights():
    cells = {
        f"phys_{r:03d}": {"success_rate": v}
        for r, v in [(100, 100), (125, 1), (150, 0), (175, 0), (200, 0)]
    }
    assert M.auc(cells, "success_rate") == pytest.approx(1 / 6)


def test_qualification_is_inclusive_and_never_discards_failures():
    episodes = [
        {
            "motion_index": i,
            "valid_samples": 200,
            "completed": done,
            "global_mpjpe_mm": g,
            "local_mpjpe_mm": l,
        }
        for i, (done, g, l) in enumerate([(True, 600, 50), (False, 10, 10), (True, 601, 49)])
    ]
    result = M.summarize(episodes)
    assert result["qualification"] == pytest.approx(1 / 3)
    assert result["completion"] == pytest.approx(2 / 3)
    assert result["global_mm"] == pytest.approx(1211 / 3)


def test_missing_poses_and_duplicate_episode_ids_fail():
    row = {
        "motion_index": 0,
        "valid_samples": 0,
        "completed": False,
        "global_mpjpe_mm": 0,
        "local_mpjpe_mm": 0,
    }
    with pytest.raises(ValueError):
        M.summarize([row])
    row["valid_samples"] = 1
    with pytest.raises(ValueError):
        M.summarize([row, row])


def test_exact_budget_boundary_passes_without_changing_the_margin():
    origin = {c: panel() for c in M.PROTECTED}
    current = {c: panel(g=110, l=22, s=0.98) for c in M.PROTECTED}
    result = M.retention_gate(current, origin)
    assert result["D_pct"] == 10
    assert result["L_pp"] == 2
    assert result["passes"]
    current["phys_100"]["local_mm"] += 1e-10
    assert not M.retention_gate(current, origin)["passes"]
