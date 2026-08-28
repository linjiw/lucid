#!/usr/bin/env bash
# Mirror the data-root receipts into this repo and commit them (run after any experiment).
set -euo pipefail
cd "$(dirname "$0")"
# LUCID_ROOT is host-specific and lives outside git; env/lucid_env.sh resolves it.
: "${LUCID_ROOT:=$(source env/lucid_env.sh >/dev/null 2>&1; echo "$LUCID_ROOT")}"
rsync -a --exclude '*_origin_map.json' "$LUCID_ROOT/manifests/" receipts/manifests/
git add receipts env fable.md docs *.md 2>/dev/null || true
git add GR00T-WholeBodyControl   # submodule pointer
git commit -q -m "receipts: sync $(date '+%Y-%m-%d %H:%M')" && git push -q origin main && echo "synced + pushed" || echo "nothing to sync"
