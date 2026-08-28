#!/usr/bin/env python3
"""Rebuild the frozen LUCID motion pools from the public BONES-SEED G1 corpus.

The frozen manifests in $LUCID_ROOT/manifests/pool_*.json name every motion they
contain and carry a sha256 of each clip's `dof` array. That makes a rebuild
*verifiable*: this script regenerates the clips and checks each hash against the
manifest, so the pools are either provably the same instrument as the original
host's or they are reported as different. It never edits the manifests.

    python env/rebuild_pools.py --pools debug512 adapt4950
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import joblib

ROOT = Path(os.environ["LUCID_ROOT"])
REPO = Path(os.environ["LUCID_REPO"])
CSV_ROOT = ROOT / "pools/bones_seed/g1/csv"
STAGE_CSV = ROOT / "pools/_stage_csv"
STAGE_PKL = ROOT / "pools/_stage_pkl"
CONVERT = REPO / "gear_sonic/data_process/convert_soma_csv_to_motion_lib.py"
SRC_FPS, DST_FPS = 120, 30


def index_csvs() -> dict[str, Path]:
    return {c.stem: c for c in CSV_ROOT.rglob("*.csv")}


def stage(keys: set[str], index: dict[str, Path]) -> tuple[int, list[str]]:
    missing = sorted(k for k in keys if k not in index)
    staged = 0
    for key in sorted(keys - set(missing)):
        src = index[key]
        dst = STAGE_CSV / src.parent.name / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            dst.symlink_to(src)
        staged += 1
    return staged, missing


def convert(workers: int) -> None:
    STAGE_PKL.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(CONVERT),
        "--input", str(STAGE_CSV), "--output", str(STAGE_PKL),
        "--individual", "--fps", str(DST_FPS), "--fps_source", str(SRC_FPS),
        "--num_workers", str(workers),
    ]
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def flatten(pool_id: str, keys: set[str]) -> Path:
    out = ROOT / f"pools/{pool_id}/robot_filtered"
    out.mkdir(parents=True, exist_ok=True)
    by_stem = {p.stem: p for p in STAGE_PKL.rglob("*.pkl")}
    for key in sorted(keys):
        src = by_stem.get(key)
        if src is None:
            continue
        dst = out / f"{key}.pkl"
        if not dst.exists():
            os.link(src, dst)          # hardlink: one copy on disk
    return out


def verify(pool_id: str, manifest: dict, pool_dir: Path) -> dict:
    expected = {m["motion_key"]: m["content_sha256"] for m in manifest["motions"]}
    match = mismatch = absent = 0
    bad: list[str] = []
    for key, want in expected.items():
        path = pool_dir / f"{key}.pkl"
        if not path.exists():
            absent += 1
            continue
        payload = joblib.load(path)
        clip = payload[key] if key in payload else next(iter(payload.values()))
        got = hashlib.sha256(clip["dof"].tobytes()).hexdigest()
        if got == want:
            match += 1
        else:
            mismatch += 1
            if len(bad) < 5:
                bad.append(f"{key}: want {want[:12]} got {got[:12]}")
    return {"match": match, "mismatch": mismatch, "absent": absent, "examples": bad}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pools", nargs="+", default=["debug512", "adapt4950"])
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--skip-convert", action="store_true")
    args = ap.parse_args()

    manifests = {p: json.load(open(ROOT / f"manifests/pool_{p}.json")) for p in args.pools}
    per_pool = {p: {m["motion_key"] for m in d["motions"]} for p, d in manifests.items()}
    union: set[str] = set().union(*per_pool.values())
    print(f"pools: { {p: len(k) for p, k in per_pool.items()} }  union={len(union)}")

    index = index_csvs()
    print(f"extracted CSVs indexed: {len(index)}")
    staged, missing = stage(union, index)
    print(f"staged {staged} CSVs; {len(missing)} not found in the corpus")
    if missing:
        print("  missing sample:", missing[:5])

    if not args.skip_convert:
        convert(args.workers)

    report = {}
    for pool_id, keys in per_pool.items():
        pool_dir = flatten(pool_id, keys)
        result = verify(pool_id, manifests[pool_id], pool_dir)
        report[pool_id] = result
        total = len(keys)
        print(f"\n{pool_id}: {result['match']}/{total} clips hash-identical to the frozen "
              f"manifest; {result['mismatch']} mismatched, {result['absent']} absent")
        for line in result["examples"]:
            print("   ", line)
    ok = all(r["mismatch"] == 0 and r["absent"] == 0 for r in report.values())
    print("\nRESULT:", "pools reproduce the frozen instrument exactly"
          if ok else "pools DIFFER from the frozen instrument -- new lineage required")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
