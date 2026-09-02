#!/usr/bin/env bash
# GPU queue for 2026-09-02: pause the Phase 2 arm, run the prototype loop, resume.
#
# Why pause rather than kill: the Phase 2 driver writes its receipt only when
# the whole five-arm queue finishes, so killing the running ramp_150 arm would
# leave gate_150 (complete, 4 expansions, ceiling reached) without the receipt
# its preregistered analysis needs, and would throw away ramp_150's progress.
# A SIGSTOPped trainer keeps its GPU memory (~6.7 GiB) but issues no kernels,
# so the card's compute is free for the prototype loop; SIGCONT resumes the
# same process with the same RNG stream, so training metrics are untouched
# and only ramp_150's wall-clock is stretched (which the receipt records and
# no decision rule reads). Amendment A9 documents it.
#
# Order: the two decisive prototype pairs first (box_150 vs gate_150, box_asym
# vs ramp_asym) with fixed_150 as the width anchor, scored as soon as they are
# in; then the three remaining controls, scored; then Phase 2 resumes.
#
# The EXIT trap ALWAYS resumes the paused processes, so Phase 2 can never be
# left frozen by a failure in this script.
#
# usage: run_queue_20260902.sh --execute

set -uo pipefail

readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly LUCID="/home/linjiw/lucid"
readonly RAMP_BRANCH="curriculum_comparison_ne1024_20260901_232720_s8600_ramp_150"
readonly LOG="${LUCID_ROOT}/outputs/queue_20260902.log"
readonly PAUSED_FILE="${LUCID_ROOT}/outputs/queue_20260902.paused_pids"

[[ "${1:-}" == "--execute" ]] || { echo "usage: $0 --execute" >&2; exit 2; }
log() { printf '[%s] %s\n' "$(date '+%F %H:%M:%S')" "$*" | tee -a "${LOG}"; }

# ---------------------------------------------------------------- pause --
trainer_pid="$(pgrep -f "branch_id=${RAMP_BRANCH}" | head -1 || true)"
[[ -n "${trainer_pid}" ]] || { log "REFUSED: no running trainer for ${RAMP_BRANCH}"; exit 1; }
# The trainer plus every descendant (wandb-core, wandb-xpu), so nothing keeps
# talking to a frozen parent.
mapfile -t pids < <(printf '%s\n' "${trainer_pid}"; pstree -p "${trainer_pid}" | grep -o '([0-9]\+)' | tr -d '()' | grep -v "^${trainer_pid}$")
printf '%s\n' "${pids[@]}" > "${PAUSED_FILE}"

resume() {
    if [[ -f "${PAUSED_FILE}" ]]; then
        while read -r pid; do
            [[ -n "${pid}" ]] && kill -CONT "${pid}" 2>/dev/null || true
        done < "${PAUSED_FILE}"
        rm -f "${PAUSED_FILE}"
        log "resumed Phase 2 trainer ${trainer_pid} and descendants"
    fi
}
trap resume EXIT

log "pausing Phase 2 ramp_150 trainer ${trainer_pid} (+${#pids[@]} descendants): ${pids[*]}"
for pid in "${pids[@]}"; do kill -STOP "${pid}" 2>/dev/null || true; done
sleep 5
state="$(awk '{print $3}' /proc/"${trainer_pid}"/stat)"
[[ "${state}" == "T" ]] || { log "REFUSED: trainer state is ${state}, not T"; exit 1; }
log "trainer paused; GPU: $(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader)"

# ------------------------------------------------------------- prototype --
run_batch() {
    local label="$1"; shift
    log "prototype batch ${label}: $*"
    bash "${LUCID}/tools/run_expansion_prototype.sh" --execute --modes "$@" >> "${LOG}" 2>&1
    local code=$?
    log "batch ${label} training exit=${code}"
    (( code == 0 )) || return "${code}"
    local receipt
    receipt="$(ls -t "${LUCID_ROOT}"/manifests/expansion_prototype_*/curriculum_comparison_ne1024_*.json 2>/dev/null | head -1)"
    [[ -n "${receipt}" ]] || { log "batch ${label}: no training receipt found"; return 1; }
    log "batch ${label} scoring ${receipt}"
    bash "${LUCID}/tools/run_expansion_prototype_scoring.sh" "${receipt}" --execute >> "${LOG}" 2>&1
    log "batch ${label} scoring exit=$?"
}

run_batch 1 box_150 gate_150 box_asym ramp_asym fixed_150
run_batch 2 ramp_150 fixed fixed_asym

# --------------------------------------------------------------- resume --
resume
trap - EXIT
log "queue done; Phase 2 ramp_150 running again"
