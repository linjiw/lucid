#!/usr/bin/env bash
# P1: can fixed randomization train a good policy at a concentrated target?
#
# Five warm-start arms from one origin, identical budget, environments, mixture
# and seed. The only difference is the SHAPE and SCHEDULE of one actuator
# channel's target distribution.
#
#   act_off     every actuator channel at nominal; what the budget buys with none
#   act_range   the target as a RANGE. Expected to behave like fixed randomization,
#               because a range that contains its own easy end is self-curricularizing:
#               supports are nested and all 1024 envs redraw every episode, so a
#               batch at full intensity already contains near-nominal episodes.
#   act_point   the SAME target as a point, every environment every episode. This is
#               direct training at a concentrated target, where the easy episodes are
#               genuinely absent, and it is the arm the barrier hypothesis needs.
#   act_ramp    an open-loop schedule ending at that point
#   act_gate    the probe-gated curriculum expanding toward that point
#
# act_point against act_range is the decisive contrast and it is a one-line
# configuration difference. act_ramp and act_gate say whether staging reaches a
# point direct training cannot, and whether feedback adds anything over the
# schedule. Beating act_point is the low bar; beating act_ramp is the real one.
#
# The channel and target are ARGUMENTS, not constants: which channel is worth
# training on is decided by the frozen-policy screen, not assumed here.
#
# Preregistered: receipts/manifests/lucid_actuator_barrier_preregistration_20260903.json
# Cost: 5 arms x ~1 GPU-h. Single seed: this screens, it does not decide.
#
# usage: run_actuator_barrier.sh --channel effort_limit --target 0.5 [--execute]
#                                [--arms a b ...] [--seed N]

set -euo pipefail

readonly DEV_REPO="/home/linjiw/lucid/GR00T-WholeBodyControl"
readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly PY="/home/linjiw/isaaclab-install/env_isaaclab/bin/python"
readonly ORIGIN="${LUCID_ROOT}/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260829_000249/seed_8600/fixed/final_checkpoint.pt"
readonly PREREG="/home/linjiw/lucid/receipts/manifests/lucid_actuator_barrier_preregistration_20260903.json"
readonly MOTION="${LUCID_ROOT}/pools/subsets/m1_hob002/robot_filtered"
readonly ENCODER="${LUCID_ROOT}/artifacts/lucid_encoder_debug512.pt"
readonly NUM_ENVS=1024
readonly ITERATIONS=1500
readonly MAX_DELAY=12

CHANNEL=""; TARGET=""; EXECUTE=0; SEED=8600
ARMS=(act_off act_range act_point act_ramp act_gate)
while [[ $# -gt 0 ]]; do
    case "$1" in
        --channel) CHANNEL="$2"; shift 2 ;;
        --target)  TARGET="$2";  shift 2 ;;
        --seed)    SEED="$2";    shift 2 ;;
        --execute) EXECUTE=1;    shift ;;
        --arms) shift; ARMS=(); while [[ $# -gt 0 && "$1" != --* ]]; do ARMS+=("$1"); shift; done ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

log() { printf '[%s] %s\n' "$(date '+%F %H:%M:%S')" "$*"; }
die() { echo "REFUSED: $*" >&2; exit 1; }

# The screen names the channel and the severity. Refusing a default here is the
# point: an arbitrary target would make the result about a number nobody chose.
[[ -n "${CHANNEL}" ]] || die "pass --channel; the frozen-policy screen decides which one"
[[ -n "${TARGET}"  ]] || die "pass --target; the screen decides where the channel bites"
[[ -f "${PREREG}"  ]] || die "preregistration missing: ${PREREG}"
[[ -f "${ORIGIN}"  ]] || die "origin checkpoint missing: ${ORIGIN}"

readonly STAMP="$(date +%Y%m%d_%H%M%S)"
readonly EXPERIMENT="lucid_actuator_barrier_${CHANNEL}_${STAMP}"
readonly RECEIPT_DIR="${LUCID_ROOT}/manifests/actuator_barrier_${STAMP}"

log "${EXPERIMENT}: ${ARMS[*]} at ${CHANNEL}=${TARGET}, seed ${SEED}"
log "origin sha256 $(sha256sum "${ORIGIN}" | cut -c1-12)"
log "preregistration sha256 $(sha256sum "${PREREG}" | cut -c1-12)"

export LUCID_ROOT
# shellcheck disable=SC1091
source /home/linjiw/lucid/env/lucid_env.sh
export LUCID_GPU_WAIT_SECONDS=43200
cd "${DEV_REPO}"
log "SONIC $(git rev-parse --short HEAD) on $(git branch --show-current)"

MIN_FREE_MIB=10000
if (( EXECUTE )); then
    # A SIGSTOPped trainer keeps its memory but issues no kernels; a RUNNING one
    # must finish first. This never pauses or kills another session's work.
    live="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d' || true)"
    if [[ -n "${live}" ]]; then
        running=""
        for pid in ${live}; do
            state="$(awk '{print $3}' /proc/"${pid}"/stat 2>/dev/null || echo "?")"
            [[ "${state}" == "T" ]] || running+="${pid} "
        done
        [[ -z "${running}" ]] || die "GPU is busy (running pids: ${running})"
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
    --actuator-channel "${CHANNEL}"
    --actuator-target "${TARGET}"
    --max-delay "${MAX_DELAY}"
    --termination-thresholds default
    --motion-file "${MOTION}"
    --smpl-motion-file dummy
    --encoder "${ENCODER}"
    --wandb-project lucid-campaign
    --gate-threshold 0.80
    --gate-window 100
    --gate-dwell 50
    --gate-min-episodes 200
    --gate-guard-action freeze
    --ramp-begin-iteration 0
    --ramp-end-iteration 1000
    --receipt-dir "${RECEIPT_DIR}"
    --log-dir "${LUCID_ROOT}/outputs/${EXPERIMENT}"
    --min-free-mib "${MIN_FREE_MIB}"
)
if (( EXECUTE )); then
    args+=(--execute)
    log "launching ${#ARMS[@]} arms serially; receipts -> ${RECEIPT_DIR}"
    "${args[@]}"
    log "training complete; score the arms on the frozen band before reading anything"
else
    "${args[@]}" | grep -E "^\[|num_runs|dry run|act_" | head -20
fi
