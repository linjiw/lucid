#!/usr/bin/env bash
# P0: do the actuator channels do anything, and where do they start to bite?
#
# No training. Five frozen policies scored on thirteen cells of the actuator event
# preset, which is lucid_curriculum plus four channels Isaac Lab already lets us
# write per environment and that this robot currently holds fixed: peak torque,
# joint friction (which the URDF declares none of), reflected inertia, and the
# joint speed ceiling.
#
# This is the cheapest step that can END the direction. If no defensible severity
# constrains a competent policy, the channel is not a barrier candidate and is
# reported as such rather than retuned until it bites.
#
#   act_off          every actuator channel collapsed to its nominal; the
#                    within-preset reference the other cells are read against
#   act_effort_*     peak torque, the rating a deployed motor does not meet
#   act_friction_*   gearbox friction, the one channel that ADDS absent physics
#   act_armature_*   reflected inertia, expected to behave like the smooth channels
#   act_velocity_*   speed ceiling; read with care, since below what the clip
#                    demands this makes the reference untrackable rather than
#                    hard, which is not a learnability barrier
#
# The six inherited channels sit at their envelope in every cell, exactly as they
# do for the physics cells, so a drop is attributable to the one channel varied.
#
# Deliberately a near-copy of run_channel_sweep.sh, which is known to work: same
# two-group split because the ratchet final was trained from a different worktree
# and resolves a different config, same panel, same 512-episode cells.
#
# Cost: 5 policies x 13 cells, about 0.6 GPU-h. Single seed: range-finding, not a
# decision about any curriculum.
#
# usage: run_actuator_screen.sh [--execute]

set -euo pipefail

readonly DEV_REPO="/home/linjiw/lucid/GR00T-WholeBodyControl"
readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly INDEX="${LUCID_ROOT}/manifests/lucid_channel_sweep_index_20260902.json"
readonly PANEL="${LUCID_ROOT}/manifests/replicate_panel_panel_hob002_k512.json"
readonly PY="/home/linjiw/isaaclab-install/env_isaaclab/bin/python"
readonly STAMP="$(date +%Y%m%d_%H%M%S)"
readonly EXPERIMENT="actuator_screen_${STAMP}"
readonly PRESETS="act_off act_effort_050 act_effort_100 act_effort_150 act_friction_050 act_friction_100 act_friction_200 act_friction_300 act_armature_100 act_armature_200 act_velocity_050 act_velocity_100 act_velocity_150"

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

log "actuator screen ${EXPERIMENT}; git $(git rev-parse --short HEAD)"

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
log "actuator screen ${EXPERIMENT} done"
