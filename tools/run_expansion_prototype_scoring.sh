#!/usr/bin/env bash
# Score the expansion-prototype finals on the held-out band and the channel cells.
#
# For every arm in a prototype training receipt, 15 cells at 512 episodes:
#
#   phys_100 phys_125 phys_150          in-support for 1.5 arms (reported, not gated on)
#   phys_175 phys_200                   the held-out band, outside every arm's support
#   ch_fric_150 ch_fric_200             friction marginal (the floor clamps at 0.05)
#   ch_mass_200 ch_mass_300 ch_com_200 ch_com_300 ch_joint_200 ch_joint_300
#   ch_push_200 ch_push_300             single-channel marginals past every ceiling
#
# The channel cells are what the box arm is FOR: if it widened mass and pushes
# while holding friction, its gain should show on ch_mass/ch_push and its cost
# (if any) on ch_fric. A scalar arm cannot produce that signature.
#
# usage: run_expansion_prototype_scoring.sh <training-receipt.json> [--execute]

set -euo pipefail

readonly DEV_REPO="/home/linjiw/lucid/GR00T-WholeBodyControl"
readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly PANEL="${LUCID_ROOT}/manifests/replicate_panel_panel_hob002_k512.json"
readonly PY="/home/linjiw/isaaclab-install/env_isaaclab/bin/python"
readonly PRESETS="phys_100 phys_125 phys_150 phys_175 phys_200 phys_250 phys_300 ch_fric_150 ch_fric_200 ch_mass_200 ch_mass_300 ch_com_200 ch_com_300 ch_joint_200 ch_joint_300 ch_push_200 ch_push_300"

RECEIPT="${1:-}"
[[ -n "${RECEIPT}" && -f "${RECEIPT}" ]] || { echo "usage: $0 <training-receipt.json> [--execute]" >&2; exit 2; }
EXECUTE=0
[[ "${2:-}" == "--execute" ]] && EXECUTE=1

log() { printf '[%s] %s\n' "$(date '+%F %H:%M:%S')" "$*"; }
readonly STAMP="$(date +%Y%m%d_%H%M%S)"
readonly EXPERIMENT="expansion_prototype_scoring_${STAMP}"

export LUCID_ROOT
# shellcheck disable=SC1091
source /home/linjiw/lucid/env/lucid_env.sh
export LUCID_GPU_WAIT_SECONDS=43200
cd "${DEV_REPO}"

# The training config is the one resolved beside the origin checkpoint; the
# comparison driver records it under config.checkpoint, which the evaluator
# reads to install config.yaml beside every scored final.
modes="$("${PY}" -c "import json,sys; r=json.load(open(sys.argv[1])); print(' '.join(dict.fromkeys(a['mode'] for a in r['arms'].values() if a.get('checkpoint_exported'))))" "${RECEIPT}")"
log "scoring ${EXPERIMENT}: modes ${modes} from $(basename "${RECEIPT}")"

args=(
    scripts/practice_utility/run_curriculum_robustness_eval.py
    --training-receipt "${RECEIPT}"
    --num-envs 512
    --seeds 8600
    --modes ${modes}
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
    "${PY}" "${args[@]}" --execute
    log "scoring complete; receipts -> ${LUCID_ROOT}/manifests/${EXPERIMENT}"
else
    "${PY}" "${args[@]}" | tail -4
fi
