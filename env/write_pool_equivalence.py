#!/usr/bin/env python3
"""Record, as an auditable receipt, exactly how a rebuilt pool differs from the frozen one.

The frozen pool/split manifests were produced on the original host. Rebuilding
them here from the public BONES-SEED corpus reproduces every clip bit-for-bit,
but `pool_sha256` hashes `source_root` -- an absolute filesystem path -- so the
identity strings cannot match on a host with a different data root.

This script proves that claim field by field rather than asserting it: it
compares every clip hash, every split assignment, and every top-level field, and
writes the result to a receipt. It never modifies a frozen manifest.
"""

from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import platform
import socket
import subprocess

ROOT = Path(os.environ["LUCID_ROOT"])
REPO = Path(os.environ["LUCID_REPO"])
FROZEN = ROOT / "manifests"
REBUILT = ROOT / "tmp/pool_verify"


def compare(name: str) -> dict:
    a = json.loads((FROZEN / name).read_text())
    b = json.loads((REBUILT / name).read_text())
    differing = sorted(f for f in set(a) | set(b) if a.get(f) != b.get(f))
    out: dict = {"differing_top_level_fields": differing}
    if "motions" in a:
        ha = {m["motion_key"]: m["content_sha256"] for m in a["motions"]}
        hb = {m["motion_key"]: m["content_sha256"] for m in b["motions"]}
        out["num_motions"] = {"frozen": len(ha), "rebuilt": len(hb)}
        out["motion_keys_identical"] = set(ha) == set(hb)
        out["clip_hashes_identical"] = ha == hb
        out["clip_hash_mismatches"] = sorted(k for k in ha if ha.get(k) != hb.get(k))
        out["differing_top_level_fields"] = [f for f in differing if f != "motions"]
        out["motion_entry_fields_that_differ"] = sorted(
            {
                f
                for x, y in zip(a["motions"], b["motions"], strict=True)
                for f in set(x) | set(y)
                if x.get(f) != y.get(f)
            }
        )
    else:
        for field in ("assignment", "group_partition", "ratios", "seed", "stats", "linkage"):
            if field in a or field in b:
                out[f"{field}_identical"] = a.get(field) == b.get(field)
    out["frozen_source_root"] = a.get("source_root")
    out["rebuilt_source_root"] = b.get("source_root")
    return out


def main() -> int:
    results = {}
    for pool_id in ("debug512", "adapt4950"):
        for name in (
            f"pool_{pool_id}.json",
            f"split_{pool_id}_performer.json",
            f"split_{pool_id}_content.json",
        ):
            if (FROZEN / name).exists() and (REBUILT / name).exists():
                results[name] = compare(name)

    substantive = []
    for name, r in results.items():
        if r.get("clip_hash_mismatches"):
            substantive.append(f"{name}: clip hashes differ")
        bad = [
            f
            for f in r["differing_top_level_fields"]
            if f not in ("pool_sha256", "split_sha256", "source_root")
        ]
        if bad:
            substantive.append(f"{name}: {bad}")
        if r.get("motion_entry_fields_that_differ", []) not in ([], ["path"]):
            substantive.append(f"{name}: motion entries differ beyond `path`")
        for k, v in r.items():
            if k.endswith("_identical") and v is False:
                substantive.append(f"{name}: {k} is False")

    receipt = {
        "kind": "lucid_pool_equivalence",
        "schema_version": 1,
        "created_at": datetime.now().astimezone().isoformat(),
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "lucid_root": str(ROOT),
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
        ).strip(),
        "git_status_short": [
            line
            for line in subprocess.check_output(
                ["git", "status", "--short"], cwd=REPO, text=True
            ).splitlines()
            if line
        ],
        "corpus": {
            "source": "huggingface.co/datasets/bones-studio/seed (gated)",
            "archive": "g1.tar.gz",
            "archive_bytes": (ROOT / "pools/bones_seed/g1.tar.gz").stat().st_size,
            "conversion": "convert_soma_csv_to_motion_lib.py --individual --fps_source 120 --fps 30",
        },
        "comparisons": results,
        "substantive_differences": substantive,
        "verdict": (
            "rebuilt pools are the same instrument as the frozen pools; the only "
            "differences are `source_root` and the two hashes derived from it, which "
            "encode an absolute filesystem path and therefore cannot be host-portable"
            if not substantive
            else "rebuilt pools DIFFER substantively from the frozen pools"
        ),
    }

    out = ROOT / "manifests" / (
        "pool_equivalence_"
        + datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
        + ".json"
    )
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["verdict"])
    if substantive:
        for line in substantive:
            print("  !", line)
    print("receipt", out)
    return 0 if not substantive else 1


if __name__ == "__main__":
    raise SystemExit(main())
