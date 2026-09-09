"""Contracts for the MuJoCo sim2sim sweep driver.

The sim2sim path carried no test of any kind, and its one silent failure mode
is the expensive one: arm keys are stable NAMES, so re-pointing an arm at a
retrained checkpoint and reusing ``--out`` returned the previous policy's
survival numbers without a word. A wrong number that looks right is worse here
than a crash, because the sweep output goes straight into a table.

What these pin:

* a cached rollout is reused only when the ONNX that produced it, and the clip
  it tracked, are provably the same;
* arms can be supplied per campaign rather than edited into the module;
* an unknown arm name fails with a message instead of a bare KeyError;
* the historical five arms and the module constants other tools import are
  unchanged.
"""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

SPEC = importlib.util.spec_from_file_location(
    "mujoco_sweep", Path(__file__).parents[1] / "tools/mujoco_sweep.py"
)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def selector(**overrides):
    base = SimpleNamespace(arms=list(M.ARMS), arms_json=None, arm=None)
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


# ------------------------------------------------------------ arm selection --


def test_the_historical_arms_are_still_the_default():
    """mujoco_story.py imports these; changing the default would rewrite history.

    Pinned to the literal paths rather than compared against M.ARMS, which would
    be a self-comparison that survives repointing every arm at a new campaign.
    """
    resolved = {k: str(v) for k, v in M.resolve_arms(selector()).items()}
    base = "/home/linjiw/lucid-sonic/artifacts/curriculum_comparison"
    old_campaign = f"{base}/curriculum_comparison_ne1024_20260829_000249"
    new_campaign = f"{base}/curriculum_comparison_ne1024_20260831_144022"
    assert resolved == {
        "off_s8600": f"{old_campaign}/seed_8600/off/exported/model_step_008000_g1.onnx",
        "lucid_collapsed_s8601": f"{old_campaign}/seed_8601/lucid_rg/exported/model_step_008000_g1.onnx",
        "fixed_s8600": f"{old_campaign}/seed_8600/fixed/exported/model_step_008000_g1.onnx",
        "ratchet_s8601": f"{new_campaign}/seed_8601/lucid_ratchet_rg/exported/model_step_008000_g1.onnx",
        "fixed_s8601": f"{old_campaign}/seed_8601/fixed/exported/model_step_008000_g1.onnx",
    }
    assert set(M.LABEL) == set(resolved), "every arm needs a caption for the story grid"


def test_a_campaign_supplies_its_own_arms(tmp_path):
    spec = tmp_path / "arms.json"
    spec.write_text(
        json.dumps(
            {"off_s8600_new": "/tmp/a_g1.onnx", "deploy_s8600": "/tmp/b_g1.onnx"}
        )
    )
    resolved = M.resolve_arms(selector(arms_json=str(spec)))
    assert resolved == {
        "off_s8600_new": Path("/tmp/a_g1.onnx"),
        "deploy_s8600": Path("/tmp/b_g1.onnx"),
    }


def test_repeatable_arm_flag_extends_a_json_file(tmp_path):
    spec = tmp_path / "arms.json"
    spec.write_text(json.dumps({"a": "/tmp/a_g1.onnx"}))
    resolved = M.resolve_arms(selector(arms_json=str(spec), arm=["b=/tmp/b_g1.onnx"]))
    assert set(resolved) == {"a", "b"}


def test_an_arm_named_twice_is_an_error_not_last_one_wins(tmp_path):
    """An arm key must mean exactly one checkpoint, or the hash guard is moot."""
    spec = tmp_path / "arms.json"
    spec.write_text(json.dumps({"a": "/tmp/a_g1.onnx"}))
    with pytest.raises(SystemExit, match="given twice"):
        M.resolve_arms(selector(arms_json=str(spec), arm=["a=/tmp/other_g1.onnx"]))


def test_a_malformed_arm_spec_is_refused():
    with pytest.raises(SystemExit, match="NAME=/path"):
        M.resolve_arms(selector(arm=["no_equals_sign"]))


def test_an_unknown_builtin_arm_names_the_known_ones():
    """It used to be a bare KeyError from a dict comprehension."""
    with pytest.raises(SystemExit, match="unknown arm"):
        M.resolve_arms(selector(arms=["not_an_arm"]))


# ------------------------------------------------------------- the cache --


def seeded(tmp_path, result, digest, clip, channels="all", window="scored"):
    """Lay down a cached rollout as a previous sweep would have.

    The stamp carries digest, clip, channel mask AND the rollout window
    (scored vs full-clip); a stamp missing any of them is a pre-guard receipt
    and must not be trusted (digest=None here).
    """
    d = tmp_path / "runs" / "arm" / "lam1"
    d.mkdir(parents=True)
    (d / "seed1.json").write_text(json.dumps({"result": result}))
    if digest is not None:
        (d / "seed1.onnx_sha256").write_text(f"{digest} {clip} {channels} {window}\n")
    return d


def test_a_matching_cache_is_reused_without_running_the_player(tmp_path, monkeypatch):
    cached = {"fell": False, "t_end": 4.02}
    seeded(tmp_path, cached, "abc123", "/clips/x.pkl")
    monkeypatch.setattr(
        M.subprocess,
        "run",
        lambda *a, **k: pytest.fail("player must not run on a cache hit"),
    )
    _, _, _, result = M.one(
        "arm",
        Path("/tmp/x_g1.onnx"),
        1.0,
        1,
        tmp_path,
        clip="/clips/x.pkl",
        digest="abc123",
    )
    assert result == cached


def test_a_different_checkpoint_invalidates_the_cache(tmp_path):
    """The silent failure this guard exists for."""
    d = seeded(tmp_path, {"fell": False, "t_end": 4.02}, "OLDHASH", "/clips/x.pkl")
    ran = {}

    def fake_run(cmd, **kwargs):
        ran["cmd"] = cmd
        ran["unlinked_before_run"] = not (d / "seed1.json").exists()
        (d / "seed1.json").write_text(
            json.dumps({"result": {"fell": True, "t_end": 1.5}})
        )
        return SimpleNamespace(returncode=0)

    M.subprocess.run, original = fake_run, M.subprocess.run
    try:
        _, _, _, result = M.one(
            "arm",
            Path("/tmp/x_g1.onnx"),
            1.0,
            1,
            tmp_path,
            clip="/clips/x.pkl",
            digest="NEWHASH",
        )
    finally:
        M.subprocess.run = original
    assert ran, "the player must be re-run when the checkpoint changed"
    assert result == {"fell": True, "t_end": 1.5}
    assert (d / "seed1.onnx_sha256").read_text().split()[0] == "NEWHASH"
    # The stale receipt must be UNLINKED before the player runs, not merely
    # overwritten: if the re-run dies, a leftover file from the old checkpoint
    # would be served as this checkpoint's result on the next invocation.
    assert ran["unlinked_before_run"], "the stale seed1.json must be removed first"


def test_a_different_clip_invalidates_the_cache(tmp_path):
    """Same policy, different motion, is a different measurement."""
    d = seeded(tmp_path, {"fell": False, "t_end": 4.02}, "abc123", "/clips/old.pkl")

    def fake_run(cmd, **kwargs):
        (d / "seed1.json").write_text(
            json.dumps({"result": {"fell": True, "t_end": 2.0}})
        )
        return SimpleNamespace(returncode=0)

    M.subprocess.run, original = fake_run, M.subprocess.run
    try:
        _, _, _, result = M.one(
            "arm",
            Path("/tmp/x_g1.onnx"),
            1.0,
            1,
            tmp_path,
            clip="/clips/new.pkl",
            digest="abc123",
        )
    finally:
        M.subprocess.run = original
    assert result["fell"] is True


def test_a_pre_guard_receipt_without_a_stamp_is_recomputed(tmp_path):
    """Receipts written before the guard existed carry no hash; trust none of them."""
    d = seeded(tmp_path, {"fell": False, "t_end": 4.02}, None, "/clips/x.pkl")

    def fake_run(cmd, **kwargs):
        (d / "seed1.json").write_text(
            json.dumps({"result": {"fell": True, "t_end": 3.0}})
        )
        return SimpleNamespace(returncode=0)

    M.subprocess.run, original = fake_run, M.subprocess.run
    try:
        _, _, _, result = M.one(
            "arm",
            Path("/tmp/x_g1.onnx"),
            1.0,
            1,
            tmp_path,
            clip="/clips/x.pkl",
            digest="abc123",
        )
    finally:
        M.subprocess.run = original
    assert result["fell"] is True


def test_the_clip_and_interpreter_reach_the_player(tmp_path):
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        (tmp_path / "runs" / "arm" / "lam1").mkdir(parents=True, exist_ok=True)
        (tmp_path / "runs" / "arm" / "lam1" / "seed1.json").write_text(
            json.dumps({"result": {"fell": False, "t_end": 4.0}})
        )
        return SimpleNamespace(returncode=0)

    M.subprocess.run, original = fake_run, M.subprocess.run
    try:
        M.one(
            "arm",
            Path("/tmp/x_g1.onnx"),
            1.0,
            1,
            tmp_path,
            clip="/clips/mine.pkl",
            digest="d",
            py="/usr/bin/python3",
        )
    finally:
        M.subprocess.run = original
    cmd = captured["cmd"]
    assert cmd[0] == "/usr/bin/python3"
    assert cmd[cmd.index("--clip") + 1] == "/clips/mine.pkl"
    assert "--no-video" in cmd


def test_a_failed_rollout_is_not_cached_as_a_result(tmp_path):
    """An error row must not be stamped, or the failure would be reused forever."""

    def fake_run(cmd, **kwargs):
        return SimpleNamespace(returncode=1)

    M.subprocess.run, original = fake_run, M.subprocess.run
    try:
        _, _, _, result = M.one(
            "arm", Path("/tmp/x_g1.onnx"), 1.0, 1, tmp_path, clip="/c.pkl", digest="d"
        )
    finally:
        M.subprocess.run = original
    assert result["error"] is True
    assert not (tmp_path / "runs" / "arm" / "lam1" / "seed1.onnx_sha256").is_file()


# ------------------------------------------------------------ the digest --


def test_sha256_matches_hashlib(tmp_path):
    import hashlib

    f = tmp_path / "x.onnx"
    f.write_bytes(b"weights" * 1000)
    assert M.sha256(f) == hashlib.sha256(b"weights" * 1000).hexdigest()


def test_a_different_channel_mask_invalidates_the_cache(tmp_path):
    """--channels zeroes whole physics channels and appears nowhere in the path.

    Sweeping `--channels fric,mass` and then all six channels into the same
    --out is a different measurement at the same (arm, lambda, seed), so the
    restricted run's numbers must not be served for the full one.
    """
    d = tmp_path / "runs" / "arm" / "lam1"
    d.mkdir(parents=True)
    (d / "seed1.json").write_text(
        json.dumps({"result": {"fell": False, "t_end": 4.02}})
    )
    (d / "seed1.onnx_sha256").write_text("abc123 /clips/x.pkl fric,mass scored\n")

    def fake_run(cmd, **kwargs):
        (d / "seed1.json").write_text(
            json.dumps({"result": {"fell": True, "t_end": 1.1}})
        )
        return SimpleNamespace(returncode=0)

    M.subprocess.run, original = fake_run, M.subprocess.run
    try:
        _, _, _, result = M.one(
            "arm",
            Path("/tmp/x_g1.onnx"),
            1.0,
            1,
            tmp_path,
            channels=None,
            clip="/clips/x.pkl",
            digest="abc123",
        )
    finally:
        M.subprocess.run = original
    assert (
        result["fell"] is True
    ), "the full-channel run must not reuse a restricted result"
    # stamp is "<sha> <clip> <channels> <window>"; check the channel field itself
    assert (d / "seed1.onnx_sha256").read_text().split()[2] == "all"


def test_the_same_channel_mask_still_hits_the_cache(tmp_path):
    """The guard must not defeat itself: an identical mask still reuses."""
    d = tmp_path / "runs" / "arm" / "lam1"
    d.mkdir(parents=True)
    cached = {"fell": False, "t_end": 4.02}
    (d / "seed1.json").write_text(json.dumps({"result": cached}))
    (d / "seed1.onnx_sha256").write_text("abc123 /clips/x.pkl fric,mass scored\n")

    M.subprocess.run, original = (
        lambda *a, **k: pytest.fail("player must not run on a cache hit"),
        M.subprocess.run,
    )
    try:
        _, _, _, result = M.one(
            "arm",
            Path("/tmp/x_g1.onnx"),
            1.0,
            1,
            tmp_path,
            channels="fric,mass",
            clip="/clips/x.pkl",
            digest="abc123",
        )
    finally:
        M.subprocess.run = original
    assert result == cached


def test_a_full_clip_run_does_not_reuse_a_scored_one(tmp_path):
    """Scored stops at the 0.5 m drift threshold; full-clip runs the whole motion.

    They answer different questions -- a rollout cut short at 1.4 s cannot go on
    to topple -- so a cached scored result must never be served for a full-clip
    request.
    """
    d = seeded(
        tmp_path,
        {"fell": False, "t_end": 1.4},
        "abc123",
        "/clips/x.pkl",
        window="scored",
    )

    def fake_run(cmd, **kwargs):
        assert "--full-clip" in cmd, "the full-clip flag must reach the player"
        (d / "seed1.json").write_text(
            json.dumps({"result": {"fell": True, "t_end": 8.6}})
        )
        return SimpleNamespace(returncode=0)

    M.subprocess.run, original = fake_run, M.subprocess.run
    try:
        _, _, _, result = M.one(
            "arm",
            Path("/tmp/x_g1.onnx"),
            1.0,
            1,
            tmp_path,
            clip="/clips/x.pkl",
            digest="abc123",
            full_clip=True,
        )
    finally:
        M.subprocess.run = original
    assert result["t_end"] == 8.6
    assert (d / "seed1.onnx_sha256").read_text().strip().endswith("full")
