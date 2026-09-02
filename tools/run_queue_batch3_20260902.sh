#!/usr/bin/env bash
# Batch 3 of the 2026-09-02 prototype queue: re-run ramp_asym after the cap fix.
#
# ramp_asym failed at construction in batch 1 ("term_lambda_caps
# ['physics_material'] must be in [0, 1], got 1.5"): the per-channel cap
# validation was envelope-bound and ignored the support-extension flag. Fixed
# in SONIC (caps may reach the extrapolation ceiling when allow_extrapolation
# is set); fixed_asym in batch 2 launches with the fixed code. This script
# waits for the main queue to finish, then trains and scores ramp_asym so the
# R6 contrast (box_asym vs ramp_asym) has its control.
#
# usage: run_queue_batch3_20260902.sh --execute

set -uo pipefail

readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly LUCID="/home/linjiw/lucid"
readonly MAIN_LOG="${LUCID_ROOT}/outputs/queue_20260902.log"
readonly LOG="${LUCID_ROOT}/outputs/queue_20260902_batch3.log"

[[ "${1:-}" == "--execute" ]] || { echo "usage: $0 --execute" >&2; exit 2; }
log() { printf '[%s] %s\n' "$(date '+%F %H:%M:%S')" "$*" | tee -a "${LOG}"; }

log "waiting for the main queue to finish (${MAIN_LOG})"
until grep -q "queue done" "${MAIN_LOG}" 2>/dev/null; do
    pgrep -f "run_queue_2026090[2].sh" >/dev/null || { log "main queue process gone without done marker; continuing anyway"; break; }
    sleep 120
done
# Never start beside a running trainer.
until [[ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')" ]]; do
    log "GPU still busy; waiting"
    sleep 120
done

log "batch 3: ramp_asym"
bash "${LUCID}/tools/run_expansion_prototype.sh" --execute --modes ramp_asym >> "${LOG}" 2>&1
code=$?
log "batch 3 training exit=${code}"
(( code == 0 )) || exit "${code}"
receipt="$(ls -t "${LUCID_ROOT}"/manifests/expansion_prototype_*/curriculum_comparison_ne1024_*.json 2>/dev/null | head -1)"
[[ -n "${receipt}" ]] || { log "batch 3: no training receipt found"; exit 1; }
log "batch 3 scoring ${receipt}"
bash "${LUCID}/tools/run_expansion_prototype_scoring.sh" "${receipt}" --execute >> "${LOG}" 2>&1
log "batch 3 scoring exit=$?"
log "batch 3 done"
