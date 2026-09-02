#!/usr/bin/env bash
# Single-channel attribution sweep on the five seed-8600 finals.
#
# The scalar ladder widens all five physics channels together, so a drop at
# phys_150 cannot say which physics broke the policy, and past lambda ~1.385
# the friction floor is clamped so the ladder is silently a mass/CoM/push
# ladder. This sweep scores each frozen final on eleven cells that widen ONE
# term while the other four sit at their training envelope (lambda = 1) and
# latency is pinned to zero:
#
#   ch_fric_125/150/200   physics_material   (friction floor 0.1375 / 0.05 / 0.05)
#   ch_mass_200/300       randomize_rigid_body_mass   [0.6,2.0] / [0.4,2.5]
#   ch_com_200/300        base_com
#   ch_joint_200/300      add_joint_default_pos
#   ch_push_200/300       push_robot
#
# Question it answers: is the failure surface anisotropic? If one channel
# carries the whole frontier drop, a scalar lambda is the wrong actuator and a
# per-channel box is worth building; if every channel degrades alike, it is
# not. Read out with tools/analyze_channel_sweep.py.
#
# Runs CONCURRENTLY with the Phase 2 training screen on the shared GPU. The
# training holds ~7.3 GiB; a 512-env evaluation cell peaks ~5.3 GiB. Wall-clock
# is contended, metrics are not (frozen policy, seeded evaluation). The
# min-free gate below is set so an evaluation cell never starts unless it fits
# beside the trainer, and LUCID_GPU_WAIT_SECONDS lets a cell queue rather than
# die if the trainer is momentarily using more.
#
# usage: run_channel_sweep.sh [--execute]

set -euo pipefail

readonly DEV_REPO="/home/linjiw/lucid/GR00T-WholeBodyControl"
readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly INDEX="${LUCID_ROOT}/manifests/lucid_channel_sweep_index_20260902.json"
readonly PANEL="${LUCID_ROOT}/manifests/replicate_panel_panel_hob002_k512.json"
readonly PY="/home/linjiw/isaaclab-install/env_isaaclab/bin/python"
readonly STAMP="$(date +%Y%m%d_%H%M%S)"
readonly EXPERIMENT="channel_sweep_${STAMP}"
readonly PRESETS="ch_fric_125 ch_fric_150 ch_fric_200 ch_mass_200 ch_mass_300 ch_com_200 ch_com_300 ch_joint_200 ch_joint_300 ch_push_200 ch_push_300"

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

log "channel sweep ${EXPERIMENT}; git $(git rev-parse --short HEAD)"

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
log "channel sweep ${EXPERIMENT} done"
