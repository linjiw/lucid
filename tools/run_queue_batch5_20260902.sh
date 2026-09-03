#!/usr/bin/env bash
# Batch 5: the guard-free gate. Waits for batch 4 to finish, then trains and
# scores gate_300_ng (gate_300 with the relative-return guard inert), which
# isolates the survival probe as the stopping rule. Preregistration:
#   receipts/manifests/lucid_expansion_prototype_batch5_preregistration_20260902.json
# usage: run_queue_batch5_20260902.sh --execute
set -uo pipefail
readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly LUCID="/home/linjiw/lucid"
readonly B4_LOG="${LUCID_ROOT}/outputs/queue_20260902_batch4.log"
readonly LOG="${LUCID_ROOT}/outputs/queue_20260902_batch5.log"
[[ "${1:-}" == "--execute" ]] || { echo "usage: $0 --execute" >&2; exit 2; }
log() { printf '[%s] %s\n' "$(date '+%F %H:%M:%S')" "$*" | tee -a "${LOG}"; }
log "waiting for batch 4 to finish (${B4_LOG})"
until grep -q "batch 4 done" "${B4_LOG}" 2>/dev/null; do
    pgrep -f "run_queue_batch4_2026090[2]" >/dev/null || { log "batch 4 process gone; continuing"; break; }
    sleep 120
done
until [[ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')" ]]; do
    log "GPU busy; waiting"; sleep 120
done
log "batch 5: gate_300_ng"
bash "${LUCID}/tools/run_expansion_prototype.sh" --execute --modes gate_300_ng >> "${LOG}" 2>&1
log "batch 5 training exit=$?"
receipt="$(ls -t "${LUCID_ROOT}"/manifests/expansion_prototype_*/curriculum_comparison_ne1024_*.json 2>/dev/null | head -1)"
[[ -n "${receipt}" ]] || { log "no receipt"; exit 1; }
log "batch 5 scoring ${receipt}"
bash "${LUCID}/tools/run_expansion_prototype_scoring.sh" "${receipt}" --execute >> "${LOG}" 2>&1
log "batch 5 scoring exit=$?"
log "batch 5 done"
