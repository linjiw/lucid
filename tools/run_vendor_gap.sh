#!/usr/bin/env bash
# What do our policies lose if the robot is what its own vendor files say it is?
#
# robots/g1.py trains hip_pitch and hip_roll at 139 N.m. The vendor MJCF shipped
# with the deploy stack rates BOTH at 88, and for hip_pitch the robot's own URDF
# agrees with the vendor. So the real motor delivers 0.633 of the trained torque
# on the two joints that drive the stride and the lateral balance, and every
# policy in this project was trained with that surplus.
#
# This is not a randomization study. The derate is a POINT, applied to those joints
# only, because the question is about one specific robot rather than a distribution.
#
#   vend_off        the trained rating, 139 N.m: the control
#   vend_hips_050   113 N.m, half way to the vendor value
#   vend_hips_100   88 N.m on BOTH hips: the vendor rating
#   vend_hips_150   62 N.m, past the vendor rating, to give the curve a shape
#   vend_pitch_100  88 N.m on hip pitch ALONE, the joint both vendor files agree on
#
# The last cell matters because the two assets disagree about hip roll: the URDF
# says 139 and the vendor MJCF says 88. Isolating pitch keeps the headline number
# free of that disagreement.
#
# Cost: 5 policies x 5 cells, about 15 minutes. No training.
#
# usage: run_vendor_gap.sh [--execute]

set -euo pipefail

readonly DEV_REPO="/home/linjiw/lucid/GR00T-WholeBodyControl"
readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly INDEX="${LUCID_ROOT}/manifests/lucid_channel_sweep_index_20260902.json"
readonly PANEL="${LUCID_ROOT}/manifests/replicate_panel_panel_hob002_k512.json"
readonly PY="/home/linjiw/isaaclab-install/env_isaaclab/bin/python"
readonly STAMP="$(date +%Y%m%d_%H%M%S)"
readonly EXPERIMENT="vendor_gap_${STAMP}"
readonly PRESETS="vend_off vend_hips_050 vend_hips_100 vend_hips_150 vend_pitch_100"

EXECUTE=0
[[ "${1:-}" == "--execute" ]] && EXECUTE=1

log() { printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }

for path in "${INDEX}" "${PANEL}"; do
    [[ -f "${path}" ]] || { echo "missing required input: ${path}" >&2; exit 1; }
done

# The environment file is what every SONIC process needs and nothing else
# provides under nohup: the venv, the Omniverse EULA acceptance, a writable
# TMPDIR under the data root, and a clean PYTHONPATH. The first launch of this
# sweep skipped it and every cell died at the EULA prompt (voided as
# void_channel_sweep_20260902_001037).
export LUCID_ROOT
# shellcheck disable=SC1091
source /home/linjiw/lucid/env/lucid_env.sh
export LUCID_GPU_WAIT_SECONDS=7200
cd "${DEV_REPO}"

log "vendor gap ${EXPERIMENT}; git $(git rev-parse --short HEAD)"

# Group A: the four campaign finals share one resolved training config.
# Group B: the ratchet final was trained from a different worktree/config.
run_group() {
    local label="$1" config="$2"; shift 2
    local modes=("$@")
    local args=(
        scripts/practice_utility/run_curriculum_robustness_eval.py
        --training-receipt "${INDEX}"
        --training-config "${config}"
        --num-envs 512
        --seeds 8600
        --modes "${modes[@]}"
        --presets ${PRESETS}
        --eval-seed-base 8700
        --max-delay 12
        --panel-receipt "${PANEL}"
        --artifact-root "${LUCID_ROOT}/artifacts/${EXPERIMENT}"
        --log-dir "${LUCID_ROOT}/outputs/${EXPERIMENT}"
        --receipt-dir "${LUCID_ROOT}/manifests/${EXPERIMENT}"
        --min-free-mib 5800
    )
    if (( EXECUTE )); then
        log "group ${label}: ${modes[*]}"
        "${PY}" "${args[@]}" --execute
    else
        "${PY}" "${args[@]}" | tail -5
    fi
}

run_group A "/home/linjiw/lucid/GR00T-WholeBodyControl/logs_rl/lucid-campaign/manager/universal_token/all_modes/sonic_release_test-20260829_000251/config.yaml" fixed off lucid_rg lucid_s4_rg
run_group B "/home/linjiw/lucid-ratchet-confirm/logs_rl/lucid-campaign/manager/universal_token/all_modes/sonic_release_test-20260831_231903/config.yaml" lucid_ratchet_rg
log "vendor gap ${EXPERIMENT} done"
