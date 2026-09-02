#!/usr/bin/env bash
# LUCID expansion prototype: five widening policies from one competent origin.
#
# The from-scratch Phase 2 screen answers "does a probe-gated frontier beat an
# open-loop ramp over 8,000 iterations" at ~5.4 GPU-h per arm. That is the
# confirmatory cell; it is too slow to iterate a controller design on. This
# driver is the fast loop: every arm starts from the SAME competent policy --
# the fixed-DR seed-8600 final, which has the lambda = 1 task solved (time-out
# ~0.95) -- and gets 2,000 iterations to widen support, so each arm costs about
# 1.3 GPU-h and the question becomes the one a curriculum actually faces once
# the envelope is mastered: how should support be widened, and along which
# channels?
#
#   fixed       stay at lambda 1.0                    (more-training control)
#   fixed_150   jump to lambda 1.5 at once            (width control)
#   ramp_150    linear 1.0 -> 1.5 over 1,500 iters    (open-loop schedule)
#   gate_150    scalar frontier, probe-gated          (Phase 2 feedback arm)
#   box_150     VECTOR frontier, one probe in rotation (per-channel feedback)
#
# All five share the origin, the budget, the strata, and a 1.5 ceiling on
# every channel, so the held-out band {phys_175, phys_200} and every
# single-channel cell at 2.0/3.0 stay outside every arm's training support.
#
# Prototype knobs (not the Phase 2 values): gate window 100 / dwell 50 /
# min-episodes 200 so a 128-env probe (~6 episodes per iteration) can make a
# decision every ~150 iterations; the box's per-channel probe budget is 300
# iterations so no single channel can hold the probe for the whole run.
#
# Single seed. This is a screen: it ranks designs, it does not decide.
# Non-resume warm start: the trainer restores policy weights only (fresh
# optimizer, fresh LR schedule, iteration counter from 1), identically for
# every arm.
#
# Cost: 5 x ~1.3 GPU-h serial. Refuses to start while the GPU has a trainer on
# it (the Phase 2 screen must finish first).
#
# usage: run_expansion_prototype.sh [--execute] [--modes m1 m2 ...]

set -euo pipefail

readonly DEV_REPO="/home/linjiw/lucid/GR00T-WholeBodyControl"
readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly PY="/home/linjiw/isaaclab-install/env_isaaclab/bin/python"
readonly ORIGIN="${LUCID_ROOT}/artifacts/curriculum_comparison/curriculum_comparison_ne1024_20260829_000249/seed_8600/fixed/final_checkpoint.pt"
readonly ORIGIN_SHA256_EXPECTED="${LUCID_ORIGIN_SHA256:-}"
readonly STAMP="$(date +%Y%m%d_%H%M%S)"
readonly EXPERIMENT="lucid_expansion_prototype_ne1024_${STAMP}"
readonly RECEIPT_DIR="${LUCID_ROOT}/manifests/expansion_prototype_${STAMP}"
readonly SEED=8600
readonly NUM_ENVS=1024
readonly ITERATIONS=2000
readonly MAX_DELAY=12
readonly MOTION="${LUCID_ROOT}/pools/subsets/m1_hob002/robot_filtered"
readonly ENCODER="${LUCID_ROOT}/artifacts/lucid_encoder_debug512.pt"

EXECUTE=0
MODES=(box_150 gate_150 ramp_150 fixed_150 fixed)
while [[ $# -gt 0 ]]; do
    case "$1" in
        --execute) EXECUTE=1; shift ;;
        --modes) shift; MODES=(); while [[ $# -gt 0 && "$1" != --* ]]; do MODES+=("$1"); shift; done ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

log() { printf '[%s] %s\n' "$(date '+%F %H:%M:%S')" "$*"; }
die() { echo "REFUSED: $*" >&2; exit 1; }

log "expansion prototype ${EXPERIMENT}: ${MODES[*]}"
[[ -f "${ORIGIN}" ]] || die "origin checkpoint missing: ${ORIGIN}"
origin_sha="$(sha256sum "${ORIGIN}" | cut -d' ' -f1)"
if [[ -n "${ORIGIN_SHA256_EXPECTED}" && "${origin_sha}" != "${ORIGIN_SHA256_EXPECTED}" ]]; then
    die "origin checkpoint SHA-256 ${origin_sha} != expected ${ORIGIN_SHA256_EXPECTED}"
fi
log "origin fixed@s8600 final, sha256 ${origin_sha:0:12}"

export LUCID_ROOT
# shellcheck disable=SC1091
source /home/linjiw/lucid/env/lucid_env.sh
export LUCID_GPU_WAIT_SECONDS=43200
cd "${DEV_REPO}"
log "SONIC $(git rev-parse --short HEAD) on $(git branch --show-current)"

if (( EXECUTE )); then
    live="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d' || true)"
    [[ -z "${live}" ]] || die "GPU is busy (pids: ${live//$'\n'/,}); the Phase 2 screen must finish first"
    [[ ! -d "${RECEIPT_DIR}" ]] || die "receipt directory already exists: ${RECEIPT_DIR}"
    mkdir -p "${RECEIPT_DIR}" "${LUCID_ROOT}/outputs/${EXPERIMENT}"
fi

args=(
    "${PY}" scripts/practice_utility/run_curriculum_comparison.py
    --checkpoint "${ORIGIN}"
    --num-envs "${NUM_ENVS}"
    --iterations "${ITERATIONS}"
    --warmup-iterations 10
    --horizons 500 1000 1500
    --seeds "${SEED}"
    --modes "${MODES[@]}"
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
    --box-channel-budget 300
    --ramp-begin-iteration 0
    --ramp-end-iteration 1500
    --receipt-dir "${RECEIPT_DIR}"
    --log-dir "${LUCID_ROOT}/outputs/${EXPERIMENT}"
    --min-free-mib 10000
)
if (( EXECUTE )); then
    args+=(--execute)
    log "launching ${#MODES[@]} arms serially; receipts -> ${RECEIPT_DIR}"
    "${args[@]}"
    log "expansion prototype training complete"
else
    "${args[@]}" | grep -E "^\[|num_runs|dry run" | head -20
fi
