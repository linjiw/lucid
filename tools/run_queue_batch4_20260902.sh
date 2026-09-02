#!/usr/bin/env bash
# Batch 4 of the 2026-09-02 prototype queue: beyond the safe width.
#
# Waits for batch 3 (ramp_asym) to finish, then trains gate_300 and fixed_300
# with the standard gate cadence, then box_fast_300 with the fast cadence, and
# scores all three on the wide corner. Preregistration:
#   receipts/manifests/lucid_expansion_prototype_batch4_preregistration_20260902.json
#
# usage: run_queue_batch4_20260902.sh --execute

set -uo pipefail

readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly LUCID="/home/linjiw/lucid"
readonly B3_LOG="${LUCID_ROOT}/outputs/queue_20260902_batch3.log"
readonly LOG="${LUCID_ROOT}/outputs/queue_20260902_batch4.log"

[[ "${1:-}" == "--execute" ]] || { echo "usage: $0 --execute" >&2; exit 2; }
log() { printf '[%s] %s\n' "$(date '+%F %H:%M:%S')" "$*" | tee -a "${LOG}"; }

log "waiting for batch 3 to finish (${B3_LOG})"
until grep -q "batch 3 done\|batch 3 training exit=[1-9]" "${B3_LOG}" 2>/dev/null; do
    pgrep -f "run_queue_batch3_2026090[2]" >/dev/null || { log "batch 3 process gone; continuing"; break; }
    sleep 120
done
until [[ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')" ]]; do
    log "GPU still busy; waiting"; sleep 120
done

score_latest() {
    local receipt
    receipt="$(ls -t "${LUCID_ROOT}"/manifests/expansion_prototype_*/curriculum_comparison_ne1024_*.json 2>/dev/null | head -1)"
    [[ -n "${receipt}" ]] || { log "no training receipt found"; return 1; }
    log "scoring ${receipt}"
    bash "${LUCID}/tools/run_expansion_prototype_scoring.sh" "${receipt}" --execute >> "${LOG}" 2>&1
    log "scoring exit=$?"
}

log "batch 4a: gate_300 fixed_300 (window 100 / dwell 50)"
bash "${LUCID}/tools/run_expansion_prototype.sh" --execute --modes gate_300 fixed_300 >> "${LOG}" 2>&1
log "batch 4a training exit=$?"
score_latest

log "batch 4b: box_fast_300 (window 50 / dwell 25 / min 100)"
GATE_WINDOW=50 GATE_DWELL=25 GATE_MIN_EPISODES=100 bash "${LUCID}/tools/run_expansion_prototype.sh" --execute --modes box_fast_300 >> "${LOG}" 2>&1
log "batch 4b training exit=$?"
score_latest
log "batch 4 done"
