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
readonly ORIGIN_CAMPAIGN="${LUCID_ROOT}/logs_rl/lucid-campaign/manager/universal_token/all_modes/sonic_release_test-20260829_000251/config.yaml"
readonly NEW_CELLS="ch_push_350 ch_push_fric_200_150 ch_push_fric_300_150"

# Ordinary (already learned) | scalar ladder | practised or adjacent | above every
# practised level | untouched channel.
readonly PRESETS="phys_000 phys_100 phys_150 phys_200 ch_push_200 ch_push_300 ch_mass_300 ch_com_300 ch_joint_300 ch_push_fric_200_150 ch_push_350 ch_push_fric_300_150 ch_fric_150"

TRAIN_DIR="${1:?pass the training receipt directory}"; shift || true
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

args=(
    "${PY}" scripts/practice_utility/run_curriculum_robustness_eval.py
    --campaign-config "${LUCID_ROOT}/${CFG}/config.yaml"
    --presets ${PRESETS}
    --episodes 512
    --receipt-dir "${OUT}"
    --modes prac_null prac_push prac_easy prac_pushfric fixed
)
if (( EXECUTE )); then
    args+=(--execute)
    log "scoring 6 policies x 13 cells; receipts -> ${OUT}"
fi
"${args[@]}"

# The origin on the three cells that did not exist when it was first scored.
origin_args=(
    "${PY}" scripts/practice_utility/run_curriculum_robustness_eval.py
    --campaign-config "${ORIGIN_CAMPAIGN}"
    --presets ${NEW_CELLS}
    --episodes 512
    --receipt-dir "${OUT}_origin"
    --modes fixed off lucid_rg lucid_s4_rg lucid_ratchet_rg
)
if (( EXECUTE )); then origin_args+=(--execute); fi
log "scoring the origin and the campaign arms on the new cells: ${NEW_CELLS}"
"${origin_args[@]}"
log "done; read out with tools/analyze_practice_allocation.py ${OUT} ${OUT}_origin"
