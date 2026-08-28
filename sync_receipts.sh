#!/usr/bin/env bash
# Mirror the data-root receipts into this repo and commit them (run after any experiment).
set -euo pipefail
cd "$(dirname "$0")"
rsync -a --exclude '*_origin_map.json' /data/robotixx/lucid-sonic/manifests/ receipts/manifests/
cp /data/robotixx/lucid-sonic/lucid_env.sh env/lucid_env.sh
git add receipts env fable.md docs *.md 2>/dev/null || true
git add GR00T-WholeBodyControl   # submodule pointer
git commit -q -m "receipts: sync $(date '+%Y-%m-%d %H:%M')" && git push -q origin main && echo "synced + pushed" || echo "nothing to sync"
