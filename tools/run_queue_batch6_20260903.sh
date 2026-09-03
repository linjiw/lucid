#!/usr/bin/env bash
# Batch 6: the guard-free per-channel box. Waits for batch 5, then trains and
# scores box_fast_300_ng -- the box at a fast cadence and a 3.0 ceiling with
# the relative-return guard inert. The guarded box converged to a nearly
# uniform frontier because the guard froze every channel at once and no
# channel's probe ever fell below threshold; per-channel asymmetry can only
# show where the channels differ, which is near 2.5-3.0.
# usage: run_queue_batch6_20260903.sh --execute
set -uo pipefail
readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly LUCID="/home/linjiw/lucid"
readonly B5_LOG="${LUCID_ROOT}/outputs/queue_20260902_batch5.log"
readonly LOG="${LUCID_ROOT}/outputs/queue_20260903_batch6.log"
[[ "${1:-}" == "--execute" ]] || { echo "usage: $0 --execute" >&2; exit 2; }
log() { printf '[%s] %s\n' "$(date '+%F %H:%M:%S')" "$*" | tee -a "${LOG}"; }
log "waiting for batch 5 to finish (${B5_LOG})"
until grep -q "batch 5 done" "${B5_LOG}" 2>/dev/null; do
    pgrep -f "run_queue_batch5_2026090[2]" >/dev/null || { log "batch 5 process gone; continuing"; break; }
    sleep 120
done
until [[ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')" ]]; do
    log "GPU busy; waiting"; sleep 120
done
log "batch 6: box_fast_300_ng (window 50 / dwell 25 / min 100, guard inert)"
GATE_WINDOW=50 GATE_DWELL=25 GATE_MIN_EPISODES=100 bash "${LUCID}/tools/run_expansion_prototype.sh" --execute --modes box_fast_300_ng >> "${LOG}" 2>&1
log "batch 6 training exit=$?"
receipt="$(ls -t "${LUCID_ROOT}"/manifests/expansion_prototype_*/curriculum_comparison_ne1024_*.json 2>/dev/null | head -1)"
[[ -n "${receipt}" ]] || { log "no receipt"; exit 1; }
log "batch 6 scoring ${receipt}"
bash "${LUCID}/tools/run_expansion_prototype_scoring.sh" "${receipt}" --execute >> "${LOG}" 2>&1
log "batch 6 scoring exit=$?"
log "batch 6 done"
