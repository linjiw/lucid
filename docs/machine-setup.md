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
pytest tests/practice_utility/       1143 passed, 13 skipped
```

The 13 skips are `test_trained_encoder.py` — they need the frozen encoder and
pool/split manifests, which are not on this host yet (see below).

Idle-GPU throughput, measured with `run_throughput_probe.py --variant native`
(receipts `throughput_idle_native_ne{64,256,1024}_20260828_*.json`):

| num_envs | env-steps/s | s/iter | peak VRAM | GPU util |
|---:|---:|---:|---:|---:|
| 64 | 1,267 | 1.21 | 4.5 GB | 65% |
| 256 | 5,116 | 1.20 | 5.0 GB | 71% |
| 1,024 | 15,734 | 1.56 | 8.0 GB | 100% |

**These numbers are not comparable to the handoff's RTX 5090 figures.** They were
taken on the 2-motion `sample_data` pool, not the 512-motion pool; motion-lib
size changes sampling cost. They do establish that the card saturates around
`num_envs=1024` at ~8 GB of its 16 GB, which is the useful fact for sizing.

## Still missing on this host

1. **BONES-SEED corpus.** `bones-studio/seed` on Hugging Face is a **gated**
   dataset. Accept the terms at <https://huggingface.co/datasets/bones-studio/seed>
   and `hf auth login`, then pull the 23.5 GB G1 archive — the only one the
   pipeline needs:

   ```bash
   hf download bones-studio/seed g1.tar.gz metadata/seed_metadata_v004.csv \
       --repo-type dataset --local-dir "$LUCID_ROOT/pools/bones_seed"
   ```

   Then `gear_sonic/data_process/convert_soma_csv_to_motion_lib.py` (Bones-SEED
   flat-CSV mode) and `filter_and_copy_bones_data.py` rebuild the pools.
2. **Frozen pools** `pools/debug512/` and `pools/adapt4950/`. The manifests are
   present (mirrored into `$LUCID_ROOT/manifests/`) and carry a `content_sha256`
   per motion, so a rebuild can be **verified against them byte-for-byte** rather
   than trusted.
3. **Frozen encoders** `artifacts/lucid_encoder_debug512.pt` and
   `lucid_encoder_adapt4950.pt` — regenerate with `pretrain_encoder.py` once the
   pools verify. The observer fingerprint-checks these at runtime.
4. **The settled origin** `logs_rl/.../sonic_release_test-20260818_141446/model_step_000024.pt`.
   Not transferable; it was produced on the old host. Regenerating it here gives a
   *different* origin, so it starts a new branch lineage — the TACE drivers pin
   this exact path and will need repointing.
5. **CPU governor** is `powersave`. Set it to `performance` before trusting any
   throughput number on the 9950X.
