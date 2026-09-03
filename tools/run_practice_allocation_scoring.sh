#!/usr/bin/env bash
# Score the practice-allocation screen on the frozen 13-cell suite.
#
# The suite is identical for every arm and was frozen before any arm trained
# (see the preregistration). It contains ordinary conditions the policy already
# handles, the practised cells, and two cells ABOVE every level any arm
# practises -- the only cells from which an arm may claim generalization. The
# ORIGIN checkpoint is scored on the same suite, so improvement is measured
# against the starting point as well as against the matched control.
#
# usage: run_practice_allocation_scoring.sh <training-receipt-dir> [--execute]

set -euo pipefail
readonly DEV_REPO="/home/linjiw/lucid/GR00T-WholeBodyControl"
readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly PY="/home/linjiw/isaaclab-install/env_isaaclab/bin/python"
# The origin of every branch is the seed-8600 fixed final, which is ALREADY
# scored on phys_* and the channel cells in the campaign receipts. The two new
# cells (ch_push_350 and the pair cells) do not exist for it yet, so the origin
# is scored on those separately below and the results are merged at analysis
# time. Improvement is then readable against the starting point as well as
# against the matched control.
readonly PANEL="${LUCID_ROOT}/manifests/replicate_panel_panel_hob002_k512.json"
readonly ORIGIN_INDEX="${LUCID_ROOT}/manifests/lucid_channel_sweep_index_20260902.json"
readonly ORIGIN_CAMPAIGN="${LUCID_ROOT}/logs_rl/lucid-campaign/manager/universal_token/all_modes/sonic_release_test-20260829_000251/config.yaml"
readonly NEW_CELLS="ch_push_350 ch_push_fric_300_150 ch_push_fric_350_150"

# Ordinary (already learned) | scalar ladder | practised or adjacent | above every
# practised level | untouched channel.
readonly PRESETS="phys_000 phys_100 phys_150 phys_200 ch_push_200 ch_push_300 ch_mass_300 ch_com_300 ch_joint_300 ch_fric_150 ch_push_fric_300_150 ch_push_350 ch_push_fric_350_150"

TRAIN_DIR="${1:?pass the training receipt directory}"; shift || true
# The evaluator wants the training RECEIPT, not the directory holding it.
TRAIN_RECEIPT="$(ls -t "${TRAIN_DIR}"/curriculum_comparison_*.json 2>/dev/null | head -1)"
EXECUTE=0
[[ "${1:-}" == "--execute" ]] && EXECUTE=1
log() { printf '[%s] %s\n' "$(date '+%F %H:%M:%S')" "$*"; }

export LUCID_ROOT
# shellcheck disable=SC1091
source /home/linjiw/lucid/env/lucid_env.sh
cd "${DEV_REPO}"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT="${LUCID_ROOT}/manifests/practice_allocation_scoring_${STAMP}"
log "scoring ${TRAIN_DIR} on ${PRESETS}"

CFG="$(grep -haoE "logs_rl/[^\"]*sonic_release_test-[0-9_]+" "${TRAIN_DIR}"/*.json 2>/dev/null | head -1)"
[[ -n "${CFG}" ]] || { echo "REFUSED: no campaign config found under ${TRAIN_DIR}" >&2; exit 1; }
[[ -n "${TRAIN_RECEIPT}" ]] || { echo "REFUSED: no training receipt under ${TRAIN_DIR}" >&2; exit 1; }
for path in "${PANEL}" "${ORIGIN_INDEX}"; do
    [[ -f "${path}" ]] || { echo "REFUSED: missing required input ${path}" >&2; exit 1; }
done

# Flags mirror run_channel_sweep.sh, which is the invocation known to work. An
# earlier version of this file invented --campaign-config and --episodes, neither
# of which the evaluator accepts, so it would have died the moment the queue
# reached it.
args=(
    "${PY}" scripts/practice_utility/run_curriculum_robustness_eval.py
    --training-receipt "${TRAIN_RECEIPT}"
    --training-config "${LUCID_ROOT}/${CFG}/config.yaml"
    --num-envs 512
    --seeds 8600
    --modes prac_null prac_push prac_fric prac_pushfric prac_easy fixed
    --presets ${PRESETS}
    --eval-seed-base 8700
    --max-delay 12
    --panel-receipt "${PANEL}"
    --artifact-root "${LUCID_ROOT}/artifacts/practice_allocation_scoring_${STAMP}"
    --log-dir "${LUCID_ROOT}/outputs/practice_allocation_scoring_${STAMP}"
    --receipt-dir "${OUT}"
    --min-free-mib 5800
)
if (( EXECUTE )); then
    args+=(--execute)
    log "scoring 7 policies x 13 cells; receipts -> ${OUT}"
fi
"${args[@]}"

# The origin on the three cells that did not exist when it was first scored.
origin_args=(
    "${PY}" scripts/practice_utility/run_curriculum_robustness_eval.py
    --training-receipt "${ORIGIN_INDEX}"
    --training-config "${ORIGIN_CAMPAIGN}"
    --num-envs 512
    --seeds 8600
    --modes fixed off lucid_rg lucid_s4_rg
    --presets ${NEW_CELLS}
    --eval-seed-base 8700
    --max-delay 12
    --panel-receipt "${PANEL}"
    --artifact-root "${LUCID_ROOT}/artifacts/practice_allocation_origin_${STAMP}"
    --log-dir "${LUCID_ROOT}/outputs/practice_allocation_origin_${STAMP}"
    --receipt-dir "${OUT}_origin"
    --min-free-mib 5800
)
if (( EXECUTE )); then origin_args+=(--execute); fi
log "scoring the origin and the campaign arms on the new cells: ${NEW_CELLS}"
"${origin_args[@]}"
log "done; read out with tools/analyze_practice_allocation.py ${OUT} ${OUT}_origin"
