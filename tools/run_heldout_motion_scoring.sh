#!/usr/bin/env bash
# LUCID Phase-0.5: the first motion-generalization evidence in this programme.
#
# Every robustness number this programme has produced comes from 512 fresh
# physics draws of ONE clip, walk_hands_on_back_loop_002__A066_M -- the clip
# every arm trained on. That measures memorized-motion-under-new-physics, and
# it is the limitation a reviewer will raise first.
#
# Three sibling clips have been sitting unused on disk with committed subset
# receipts since 2026-08-28. This scores five seed-8600 arms on 128-alias
# panels of each of them, at three points of the physics ladder:
#
#   phys_100   the training envelope edge
#   phys_150   inside the frontier band
#   phys_200   the hardest cell in the frozen grid
#
# 5 arms x 3 clips x 3 cells = 45 cells, about 25 minutes.
#
# What this can and cannot show
# -----------------------------
# These clips are all walking motions from the same adaptation partition, so a
# result here is *near*-motion generalization, not the general claim. It also
# cannot separate "the policy generalizes" from "these clips are similar":
# there is no held-out-motion baseline trained on them. What it CAN do is
# falsify the strongest form of the worry -- that the arms differ only in how
# well they memorized one clip -- and it can show whether the ordering by
# frontier exposure survives a change of motion at all.
#
# Panels are k128 rather than k512, so each cell is a mean over 128 episodes
# and is correspondingly noisier than the main ladder. They are NOT
# interchangeable with the k512 numbers and must never be pooled with them.
#
# Runs from the ca057e6-pinned evaluator, the build that produced every
# historically scored arm.
#
# usage: run_heldout_motion_scoring.sh [--execute]

set -euo pipefail

readonly PIN_COMMIT="ca057e658acc59773e798057980b827d65988441"
readonly EXPECTED_EVALUATOR_SHA256="308e24150e4d4f03d0abf0dc6a427063ac662904bb3a7765488a9bff63cd94ca"
readonly DEV_REPO="/home/linjiw/lucid/GR00T-WholeBodyControl"
readonly WORKTREE="/home/linjiw/lucid-phase0-eval"
readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly RECEIPT="${LUCID_ROOT}/manifests/lucid_heldout_motion_index.json"
readonly PY="/home/linjiw/isaaclab-install/env_isaaclab/bin/python"
readonly STAMP="$(date +%Y%m%d_%H%M%S)"

readonly PANELS=(
    "${LUCID_ROOT}/manifests/replicate_panel_panel_m1_hob003_k128.json"
    "${LUCID_ROOT}/manifests/replicate_panel_panel_m1_ffloop_k128.json"
    "${LUCID_ROOT}/manifests/replicate_panel_panel_m1_fwd003_k128.json"
)
readonly PRESETS="phys_100 phys_150 phys_200"

# Config groups. ensure_checkpoint_configs installs ONE config beside every
# checkpoint in an invocation and refuses if a checkpoint already carries a
# different one, so arms are grouped by the config they already hold. The four
# campaign arms share the config that produced their historically scored
# numbers; the ratchet arm, trained later in the confirmation worktree, has its
# own. Grouping this way keeps every cell byte-comparable with the existing
# ledger instead of installing a foreign config beside a frozen checkpoint.
readonly CAMPAIGN_CONFIG="/home/linjiw/lucid/GR00T-WholeBodyControl/logs_rl/lucid-campaign/manager/universal_token/all_modes/sonic_release_test-20260829_000251/config.yaml"
readonly RATCHET_CONFIG="/home/linjiw/lucid-ratchet-confirm/logs_rl/lucid-campaign/manager/universal_token/all_modes/sonic_release_test-20260831_231903/config.yaml"
readonly CAMPAIGN_MODES=(off fixed lucid_rg lucid_s4_rg)
readonly RATCHET_MODES=(lucid_ratchet_rg)

EXECUTE=0
[[ "${1:-}" == "--execute" ]] && EXECUTE=1

log() { printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }

live="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d' || true)"
if [[ -n "${live}" ]]; then
    echo "GPU is busy (pids: ${live//$'\n'/,}); refusing to start." >&2
    exit 1
fi

[[ -f "${RECEIPT}" ]] || { echo "missing checkpoint index: ${RECEIPT}" >&2; exit 1; }
for panel in "${PANELS[@]}"; do
    [[ -f "${panel}" ]] || { echo "missing panel receipt: ${panel}" >&2; exit 1; }
done

if [[ ! -d "${WORKTREE}" ]]; then
    git -C "${DEV_REPO}" worktree add --detach "${WORKTREE}" "${PIN_COMMIT}" >/dev/null
fi
[[ "$(git -C "${WORKTREE}" rev-parse HEAD)" == "${PIN_COMMIT}" ]] || {
    echo "worktree is not at the pinned commit" >&2; exit 1; }
[[ -z "$(git -C "${WORKTREE}" status --porcelain --untracked-files=all)" ]] || {
    echo "pinned worktree is dirty; refusing to score with an unknown instrument" >&2; exit 1; }

evaluator="${WORKTREE}/scripts/practice_utility/run_curriculum_robustness_eval.py"
observed="$(sha256sum "${evaluator}" | cut -d' ' -f1)"
[[ "${observed}" == "${EXPECTED_EVALUATOR_SHA256}" ]] || {
    echo "evaluator SHA ${observed} != pinned" >&2; exit 1; }
log "instrument verified at ${PIN_COMMIT:0:7}"

score_group() {
    local panel="$1" experiment="$2" config="$3"
    shift 3
    local modes=("$@")
    [[ -f "${config}" ]] || { echo "config missing: ${config}" >&2; exit 1; }
    log "  ${#modes[@]} arms with config $(sha256sum "${config}" | cut -c1-12)"
    local args=(
        "${PY}" "${evaluator}"
        --training-receipt "${RECEIPT}"
        --training-config "${config}"
        --num-envs 128
        --seeds 8600
        --modes "${modes[@]}"
        --presets ${PRESETS}
        --eval-seed-base 8700
        --max-delay 12
        --panel-receipt "${panel}"
        --smpl-motion-file dummy
        --artifact-root "${LUCID_ROOT}/artifacts/${experiment}"
        --log-dir "${LUCID_ROOT}/outputs/${experiment}"
        --receipt-dir "${LUCID_ROOT}/manifests"
    )
    [[ "${EXECUTE}" -eq 1 ]] && args+=(--execute)
    ( cd "${WORKTREE}" && "${args[@]}" )
}

for panel in "${PANELS[@]}"; do
    clip="$(basename "${panel}" .json | sed 's/^replicate_panel_panel_//')"
    experiment="heldout_motion_${clip}_${STAMP}"
    mkdir -p "${LUCID_ROOT}/outputs/${experiment}"
    log "clip ${clip}"
    score_group "${panel}" "${experiment}" "${CAMPAIGN_CONFIG}" "${CAMPAIGN_MODES[@]}"
    score_group "${panel}" "${experiment}" "${RATCHET_CONFIG}" "${RATCHET_MODES[@]}"
done

log "held-out motion scoring complete"
