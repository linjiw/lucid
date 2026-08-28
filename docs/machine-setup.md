# Machine setup — porting LUCID to a second host

Written 2026-08-28 while bringing the program up on `linjiw-ubuntu` (RTX 5080).
The original host (`robotixx`, RTX 5090, conda env `sonic`, data root under
`/data/robotixx/`) is unchanged and still works; everything below is additive.

## What is host-specific, and how each piece is resolved

| thing | old host | this host | how it resolves |
|---|---|---|---|
| workspace | `~/lucid` | `/home/linjiw/lucid` | derived from `env/lucid_env.sh`'s own path |
| SONIC repo | `~/lucid/GR00T-WholeBodyControl` | same | `$LUCID_WORKSPACE/GR00T-WholeBodyControl` |
| data root | `/data/robotixx/lucid-sonic` | `/home/linjiw/lucid-sonic` | `$LUCID_ROOT`, auto-detected |
| python | conda env `sonic` | uv venv `env_isaaclab` | auto-detected, override with `$LUCID_PY_ENV` |
| threads | 4 (20 shared cores) | 8 (9950X, 16C/32T) | `OMP/MKL_NUM_THREADS` default |

`env/lucid_env.sh` is the single entry point on both hosts and is now
host-independent — source it and nothing else:

```bash
source /home/linjiw/lucid/env/lucid_env.sh
```

It activates the python stack, exports `LUCID_WORKSPACE` / `LUCID_REPO` /
`LUCID_ROOT`, sets `TMPDIR` under the data root, unsets `PYTHONPATH` (ROS Humble
otherwise breaks pytest collection), creates the data-root subdirectories, and
`cd`s into the SONIC repo.

## The path retarget

Every driver used to hardcode `/data/robotixx/lucid-sonic` (87 occurrences in 28
files). Those literals now go through one module:

    gear_sonic/research/practice_utility/paths.py

`LUCID_ROOT` defaults to the **original host's absolute path**, so the old host
is byte-identical and every existing receipt still resolves there. Set the
`LUCID_ROOT` environment variable to relocate it. The `run_tace_*.sh` drivers
derive the repo from their own location and source the workspace env script, so
they no longer assume `/home/robotixx`.

This is a behaviour-preserving refactor, but it does change launcher bytes:
`launcher_sha256` in receipts written from here will not match pre-2026-08-28
receipts. Old receipts still record their own launcher hashes, so lineage is
intact; new campaigns simply start a new launcher generation.

## Install on this host

Isaac Sim 5.1.0 / Isaac Lab 0.54.2 / torch 2.7.0+cu128 live in a uv venv at
`/home/linjiw/isaaclab-install/env_isaaclab` (built separately). Into it:

```bash
source /home/linjiw/lucid/env/lucid_env.sh
uv pip install --no-deps -e gear_sonic   # editable, pointed at the LUCID fork
```

`--no-deps` is deliberate. Resolving `gear_sonic`'s dependencies would pull
`numpy==1.26.4` over Isaac Sim's pinned `1.26.0`. `env/uv-overrides.txt` pins it
via `UV_OVERRIDE` for any install that does resolve, so the tracked
`gear_sonic/pyproject.toml` needs **no local diff** and will not conflict on pull.
`UV_BUILD_CONSTRAINT` holds `setuptools<81`, which `flatdict`'s sdist needs
because setuptools 81 removed `pkg_resources`.

## Verification on this host (2026-08-28)

```
check_environment.py --training      all checks passed
pytest tests/practice_utility/       1156 passed, 0 skipped
```

Idle-GPU throughput, `run_throughput_probe.py` (receipts `throughput_idle_*_20260828_*.json`).
The `sample_data` rows are a 2-motion pool and exist only to show the loop runs;
the `debug512` rows are the real 512-motion instrument and are the ones to size a
campaign from.

| pool | variant | num_envs | env-steps/s | s/iter | peak VRAM | util |
|---|---|---:|---:|---:|---:|---:|
| sample_data (2) | native | 64 | 1,267 | 1.21 | 4.5 GB | 65% |
| sample_data (2) | native | 256 | 5,116 | 1.20 | 5.0 GB | 71% |
| sample_data (2) | native | 1,024 | 15,734 | 1.56 | 8.0 GB | 100% |
| **debug512** | native | 256 | **605** | 10.16 | 8.0 GB | 100% |
| **debug512** | observer | 256 | **595** | 10.32 | 8.0 GB | 100% |

Two things fall out. **The observer callback costs 1.5%** (605 -> 595 env-steps/s),
so instrumenting a branch is essentially free. **The pool dominates**: the same
256-env config runs 8.5x slower on 512 motions than on 2, so motion-lib sampling,
not policy compute, sets the iteration time. A 128-iteration branch at
`num_envs=256` on `debug512` costs ~0.37 h.

The card saturates at `num_envs=1024` on `sample_data` at 8 GB of its 16 GB; on
`debug512` it is already at 100% util and 8 GB by `num_envs=256`.

## Rebuilding the frozen pools (done, 2026-08-28)

`bones-studio/seed` is a **gated** HF dataset -- accept the terms and `hf auth
login` first. Only the 23.5 GB G1 archive is needed:

```bash
hf download bones-studio/seed g1.tar.gz metadata/seed_metadata_v004.csv \
    --repo-type dataset --local-dir "$LUCID_ROOT/pools/bones_seed"
tar xzf "$LUCID_ROOT/pools/bones_seed/g1.tar.gz" -C "$LUCID_ROOT/pools/bones_seed"
python env/rebuild_pools.py --pools debug512 adapt4950
```

142,220 CSVs, 49 GB extracted. `env/rebuild_pools.py` stages the clips each
frozen manifest names, converts them (`convert_soma_csv_to_motion_lib.py
--individual --fps_source 120 --fps 30`; the 4x ratio is confirmed against the
manifests' own frame counts), hardlinks them flat into
`$LUCID_ROOT/pools/<id>/robot_filtered/`, and **verifies every clip against the
manifest's `content_sha256`**.

Result: **512/512 and 4950/4950 clips hash-identical to the frozen manifests.**

### The one thing that cannot be reproduced: `pool_sha256`

`env/write_pool_equivalence.py` compares the rebuilt manifests to the frozen ones
field by field and writes a `lucid_pool_equivalence` receipt. Across all six
manifests:

* every clip hash identical, every motion key identical, counts identical;
* every split `assignment`, `group_partition`, `ratios`, `seed`, `stats` and
  `linkage` identical;
* the **only** differences are `source_root`, the per-motion `path`, and the two
  hashes derived from them -- `pool_sha256` and `split_sha256`.

`pool_sha256` hashes `source_root`, an absolute filesystem path, so it is
host-bound by construction: byte-identical data in a different directory gets a
different identity. That is why the frozen probe manifests, the passive-dose plan
and the directional-calibration preregistration -- all hash-bound to
`pool_sha256` -- will not validate here, even though the instrument is provably
the same. **This is an open decision, not a settled one** (see below).

Absolute clip paths inside the frozen manifests are handled separately and
safely: `paths.relocate()` re-roots a recorded path onto `$LUCID_ROOT` only when
the original is missing and the re-rooted one exists. No hash covers those paths.

The frozen encoders were regenerated from the rebuilt pools:
`lucid_encoder_debug512.pt` (fingerprint `bdaf342b21b97704`, 36 s) and
`lucid_encoder_adapt4950.pt` (`ce5145020cf8c6e4`, 302 s). The observer records
whatever fingerprint it loads, so these are accepted; they are new instruments,
not the originals.

## Open decision: pool identity

The rebuilt pools are provably the same data, but carry a different
`pool_sha256`. Three ways forward, none of them taken yet:

1. **Re-freeze downstream on this host.** Regenerate splits, probe origins, probe
   screens, dose plan and directional calibration against the local
   `pool_sha256`. Honest and simple, but it discards the Aug-26 outcome-blind
   freeze and requires re-preregistering before looking at anything.
2. **Make `pool_sha256` content-addressed** by dropping `source_root` from it.
   Arguably a bug fix -- a content hash that includes a filesystem path is not a
   content hash -- and it makes pool identity portable forever. It changes the
   hash for everyone; old receipts keep their own recorded values, so history
   stays readable, but no new run will reproduce an old `pool_sha256`.
3. **Accept the equivalence receipt as an auditable exception**, letting the
   frozen Aug-26 artifacts be used here. Preserves the outcome-blind freeze,
   which is the whole point of having frozen it, but requires the hash gates to
   learn about the equivalence record.

## Still missing on this host

1. **The settled origin** `logs_rl/.../sonic_release_test-20260818_141446/model_step_000024.pt`.
   Not transferable; it was produced on the old host. Regenerating it here gives a
   *different* origin, so it starts a new branch lineage -- the TACE drivers pin
   this exact path and will need repointing.
2. **The SMPL pack** (32 GB) is not installed. `smpl_motion_file=dummy` works for
   all G1-encoder work, which is everything the practice-utility program does.
3. **Full-corpus training data.** All 142,220 motions are extracted as CSVs, but
   only the 5,462 clips the frozen manifests name have been converted to
   motion_lib PKLs. Converting the rest is a `rebuild_pools.py`-shaped job on a
   pool manifest that does not exist yet.

## CPU governor

`env/set-cpu-performance.sh` (run as root) pins the governor to `performance` and
persists it via a `cpu-performance.service` systemd unit. Applied 2026-08-28.

Worth recording *why* this is close to cosmetic here: this host uses the
`amd-pstate-epp` driver in **active** mode, where the `powersave` governor is not
the old ACPI powersave -- the hardware honours the EPP hint, and EPP was already
`performance`. Measured before the change, the 9950X was boosting to 5,622 MHz
against a 5,752 MHz ceiling. The change removes clock *variance*, which matters
for reproducible throughput numbers, not clock *ceiling*. Idle cores still drop
to 600 MHz, which is correct and leaves boost headroom intact.
