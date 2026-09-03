#!/usr/bin/env bash
# Practice-allocation screen: where is extra training productive?
#
# Preregistered: receipts/manifests/lucid_practice_allocation_screen_preregistration_20260902.json
#
# Every curriculum result in this programme so far answers whether the training
# ranges move, not whether moving them helps. This screen asks the question that
# comes first. Five branches leave the same competent origin with the same
# architecture, reward, motion, environment count, iteration budget and seed.
# The only difference is what a fixed 25% share of the same 1,024 environments
# practises -- and that share is TAKEN OUT of the lambda = 1 cohort, so a
# targeted branch trains on fewer standard-mixture episodes, never on more.
#
#   fixed          one stratum, everything at lambda 1 (how much is just more training)
#   prac_null      768 / 256 both at lambda 1 (the matched control: dispatcher on, content same)
#   prac_easy      256 practise mass 3x, CoM 3x, joint 3x   (already manageable: 0.949 / 0.988 / 0.990)
#   prac_push      256 practise push 3x                     (the bottleneck: 0.746)
#   prac_fric      256 practise friction 1.5x                (cheap alone: 0.973)
#   prac_pushfric  256 practise BOTH, at the same levels      (so the 2x2 interaction is estimable)
#
# The levels are read off the measured single-channel sweep, so "difficult"
# means a measured success level rather than an intuition.
#
# Scoring is a separate step (run_practice_allocation_scoring.sh) on a frozen
# 13-cell suite that includes ordinary conditions, the practised cells, and two
# cells ABOVE every level any branch practises. The origin is scored too, so
# improvement is measured against the starting point as well as the control.
#
# Cost: 6 x ~1.0 GPU-h serial, then ~0.7 GPU-h scoring. Single seed: this ranks
# designs, it does not decide.
#
# usage: run_practice_allocation_screen.sh [--execute] [--arms a b ...] [--seed N]

set -euo pipefail

readonly DEV_REPO="/home/linjiw/lucid/GR00T-WholeBodyControl"
readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly PY="/home/linjiw/isaaclab-install/env_isaaclab/bin/python"
readonly ORIGIN="${LUCID_ROOT}/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260829_000249/seed_8600/fixed/final_checkpoint.pt"
readonly STAMP="$(date +%Y%m%d_%H%M%S)"
readonly EXPERIMENT="lucid_practice_allocation_ne1024_${STAMP}"
readonly RECEIPT_DIR="${LUCID_ROOT}/manifests/practice_allocation_${STAMP}"
readonly NUM_ENVS=1024
readonly ITERATIONS=1500
readonly MAX_DELAY=12
readonly MOTION="${LUCID_ROOT}/pools/subsets/m1_hob002/robot_filtered"
readonly ENCODER="${LUCID_ROOT}/artifacts/lucid_encoder_debug512.pt"
readonly PREREG="/home/linjiw/lucid/receipts/manifests/lucid_practice_allocation_screen_preregistration_20260902.json"

EXECUTE=0
SEED=8600
ARMS=(prac_null prac_push prac_fric prac_pushfric prac_easy fixed)
while [[ $# -gt 0 ]]; do
    case "$1" in
        --execute) EXECUTE=1; shift ;;
        --seed) SEED="$2"; shift 2 ;;
        --arms) shift; ARMS=(); while [[ $# -gt 0 && "$1" != --* ]]; do ARMS+=("$1"); shift; done ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

log() { printf '[%s] %s\n' "$(date '+%F %H:%M:%S')" "$*"; }
die() { echo "REFUSED: $*" >&2; exit 1; }

log "practice-allocation screen ${EXPERIMENT}: ${ARMS[*]} (seed ${SEED})"
[[ -f "${PREREG}" ]] || die "preregistration missing: ${PREREG}"
[[ -f "${ORIGIN}" ]] || die "origin checkpoint missing: ${ORIGIN}"
origin_sha="$(sha256sum "${ORIGIN}" | cut -d' ' -f1)"
log "origin fixed@s8600 final, sha256 ${origin_sha:0:12}"
log "preregistration sha256 $(sha256sum "${PREREG}" | cut -d' ' -f1 | cut -c1-12)"

export LUCID_ROOT
# shellcheck disable=SC1091
source /home/linjiw/lucid/env/lucid_env.sh
export LUCID_GPU_WAIT_SECONDS=43200
cd "${DEV_REPO}"
log "SONIC $(git rev-parse --short HEAD) on $(git branch --show-current)"

MIN_FREE_MIB=10000
if (( EXECUTE )); then
    # A SIGSTOPped trainer keeps its memory but issues no kernels; a RUNNING one
    # must finish first. This screen never pauses or kills another session's work.
    live="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d' || true)"
    if [[ -n "${live}" ]]; then
        running=""
        for pid in ${live}; do
            state="$(awk '{print $3}' /proc/"${pid}"/stat 2>/dev/null || echo "?")"
            [[ "${state}" == "T" ]] || running+="${pid} "
        done
        [[ -z "${running}" ]] || die "GPU is busy (running pids: ${running}); wait for it to free"
        log "paused compute process(es) present (${live//$'\n'/,}); their memory stays allocated"
        MIN_FREE_MIB=8000
    fi
    [[ ! -d "${RECEIPT_DIR}" ]] || die "receipt directory already exists: ${RECEIPT_DIR}"
    mkdir -p "${RECEIPT_DIR}" "${LUCID_ROOT}/outputs/${EXPERIMENT}"
    cp "${PREREG}" "${RECEIPT_DIR}/preregistration.json"
fi

args=(
    "${PY}" scripts/practice_utility/run_curriculum_comparison.py
    --checkpoint "${ORIGIN}"
    --num-envs "${NUM_ENVS}"
    --iterations "${ITERATIONS}"
    --warmup-iterations 10
    --horizons 500 1000
    --seeds "${SEED}"
    --modes "${ARMS[@]}"
    --max-delay "${MAX_DELAY}"
    --termination-thresholds default
    --motion-file "${MOTION}"
    --smpl-motion-file dummy
    --encoder "${ENCODER}"
    --wandb-project lucid-campaign
    --receipt-dir "${RECEIPT_DIR}"
    --log-dir "${LUCID_ROOT}/outputs/${EXPERIMENT}"
    --min-free-mib "${MIN_FREE_MIB}"
)
if (( EXECUTE )); then
    args+=(--execute)
    log "launching ${#ARMS[@]} arms serially; receipts -> ${RECEIPT_DIR}"
    "${args[@]}"
    log "practice-allocation training complete; score with tools/run_practice_allocation_scoring.sh ${RECEIPT_DIR}"
else
    "${args[@]}" | grep -E "^\[|num_runs|dry run|practice" | head -30
fi
