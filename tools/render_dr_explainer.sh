#!/usr/bin/env bash
# LUCID: render the "why domain randomization matters" explainer footage.
#
# Three frozen policies, all trained on the SAME clip
# (walk_hands_on_back_loop_002__A066_M), played back on that clip under three
# physics presets from the paper's own evaluation ladder:
#
#   off@s8600                no randomization at all      frontier AUC 0.493
#   fixed@s8600              full DR (lambda = 1) throughout  frontier AUC 0.905
#   lucid_ratchet_rg@s8601   best checkpoint we have          frontier AUC 0.913
#
#   phys_000   nominal physics, lambda = 0     (every arm succeeds)
#   phys_150   heavy DR, lambda = 1.5          (half the frontier weight)
#   phys_200   extreme DR, lambda = 2.0        (hardest cell in the frozen grid)
#
# This is NOT a new evaluator. It is the identical per-cell command that
# produced every number in the paper -- same checkpoint, same 512-alias panel,
# same preset callback, same evaluation seed -- with SONIC's built-in
# render recorder switched on and the environment count cut to a few, so the
# footage IS the measurement rather than a re-implementation of it.
#
# Runs from the ca057e6-pinned worktree so the instrument is byte-identical to
# the scored ledger. Refuses while any compute process holds the GPU.
#
# usage: render_dr_explainer.sh [--execute] [--num-envs N] [--width W --height H]

set -euo pipefail

readonly PIN_COMMIT="ca057e658acc59773e798057980b827d65988441"
readonly WORKTREE="/home/linjiw/lucid-phase0-eval"
readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly PANEL="${LUCID_ROOT}/pools/panels/panel_hob002_k512/robot_filtered"
readonly PY="/home/linjiw/isaaclab-install/env_isaaclab/bin/python"
readonly ART="${LUCID_ROOT}/artifacts/curriculum_comparison"
readonly STAMP="$(date +%Y%m%d_%H%M%S)"
readonly OUT="${LUCID_ROOT}/artifacts/dr_explainer_${STAMP}"

EXECUTE=0; NUM_ENVS=4; WIDTH=1280; HEIGHT=720
while [[ $# -gt 0 ]]; do
    case "$1" in
        --execute) EXECUTE=1; shift;;
        --num-envs) NUM_ENVS="$2"; shift 2;;
        --width) WIDTH="$2"; shift 2;;
        --height) HEIGHT="$2"; shift 2;;
        *) echo "unknown arg $1" >&2; exit 2;;
    esac
done

log() { printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }

# arm label -> checkpoint path -> evaluation seed
declare -A CKPT=(
  [off_s8600]="${ART}/curriculum_comparison_ne1024_20260829_000249/seed_8600/off/final_checkpoint.pt"
  [fixed_s8600]="${ART}/curriculum_comparison_ne1024_20260829_000249/seed_8600/fixed/final_checkpoint.pt"
  [ratchet_s8601]="${ART}/curriculum_comparison_ne1024_20260831_144022/seed_8601/lucid_ratchet_rg/final_checkpoint.pt"
)
declare -A EVAL_SEED=( [off_s8600]=8700 [fixed_s8600]=8700 [ratchet_s8601]=8701 )
declare -A SCALE=( [phys_000]=0.0 [phys_150]=1.5 [phys_200]=2.0 )
readonly ARMS=(off_s8600 fixed_s8600 ratchet_s8601)
readonly PRESETS=(phys_000 phys_150 phys_200)

# ------------------------------------------------------------ preconditions --
live="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d' || true)"
if [[ -n "${live}" && "${EXECUTE}" -eq 1 ]]; then
    echo "GPU is busy (pids: ${live//$'\n'/,}); refusing to render beside another job." >&2
    exit 1
fi
[[ "$(git -C "${WORKTREE}" rev-parse HEAD)" == "${PIN_COMMIT}" ]] || { echo "worktree not at pin" >&2; exit 1; }
[[ -z "$(git -C "${WORKTREE}" status --porcelain --untracked-files=all)" ]] || { echo "pinned worktree dirty" >&2; exit 1; }
[[ -d "${PANEL}" ]] || { echo "panel missing: ${PANEL}" >&2; exit 1; }
for arm in "${ARMS[@]}"; do
    ck="${CKPT[$arm]}"
    [[ -f "${ck}" ]] || { echo "checkpoint missing: ${ck}" >&2; exit 1; }
    # The evaluator loads the architecture config from beside the checkpoint.
    # Every arm here was SCORED with the config that sits there now, so the
    # footage and the ledger share one config; refuse rather than guess.
    [[ -f "$(dirname "${ck}")/config.yaml" ]] || { echo "config.yaml missing beside ${ck}" >&2; exit 1; }
done
log "instrument: worktree ${PIN_COMMIT:0:7}, panel k512, ${NUM_ENVS} envs, ${WIDTH}x${HEIGHT}"
mkdir -p "${OUT}"

# ------------------------------------------------------------------ render --
render_cell() {
    local arm="$1" preset="$2"
    local ck="${CKPT[$arm]}" seed="${EVAL_SEED[$arm]}" scale="${SCALE[$preset]}"
    local dir="${OUT}/${arm}/${preset}" branch="dr_explainer_${STAMP}_${arm}_${preset}"
    mkdir -p "${dir}"
    local cmd=(
        "${PY}" "${WORKTREE}/scripts/practice_utility/eval_with_delay.py" --max-delay 12 --
        "checkpoint=${ck}"
        "+num_envs=${NUM_ENVS}" "+headless=true" "+use_wandb=false" "+seed=${seed}"
        "+manager_env/events=tracking/lucid_curriculum" "+use_encoder=g1"
        "+eval_callbacks=[practice_eval]" "+run_eval_loop=false"
        "++manager_env.config.train_only_events=[]"
        "++manager_env.commands.motion.motion_lib_cfg.motion_file=${PANEL}"
        "++manager_env.commands.motion.motion_lib_cfg.smpl_motion_file=dummy"
        "++manager_env.commands.motion.motion_lib_cfg.multi_thread=False"
        "++callbacks.practice_eval._target_=gear_sonic.research.practice_utility.eval_callback.PracticeRobustnessEvalCallback"
        "++callbacks.practice_eval.eval_frequency=1" "++callbacks.practice_eval.eval_only=true"
        "++callbacks.practice_eval.output_dir=${dir}"
        "++callbacks.practice_eval.preset_id=${preset}"
        "++callbacks.practice_eval.branch_id=${branch}"
        "++callbacks.practice_eval.non_latency_dr_scale=${scale}"
        "++callbacks.practice_eval.fixed_latency_steps=0"
        # --- the only additions: SONIC's own render recorder ---
        "++manager_env.config.render_results=True"
        "++manager_env.config.save_rendering_dir=${dir}/render_results"
        "+manager_env/recorders=render"
        "++manager_env.config.env_spacing=10.0"
        "++manager_env.config.render_width=${WIDTH}"
        "++manager_env.config.render_height=${HEIGHT}"
        "++manager_env.config.eval_camera_offset=[2.2,2.2,1.1]"
    )
    log "${arm} @ ${preset} (scale ${scale})"
    if [[ "${EXECUTE}" -eq 1 ]]; then
        ( cd "${WORKTREE}" && "${cmd[@]}" > "${dir}/render.log" 2>&1 ) || {
            echo "render failed for ${arm}@${preset}; see ${dir}/render.log" >&2; exit 1; }
        local n; n="$(ls "${dir}/render_results"/*.mp4 2>/dev/null | wc -l)"
        log "  -> ${n} video(s) in ${dir}/render_results"
        [[ "${n}" -ge 1 ]] || { echo "no video written for ${arm}@${preset}" >&2; exit 1; }
    else
        printf '   %s\n' "${cmd[@]}" | head -3; echo "   ... (+$(( ${#cmd[@]} - 3 )) args)"
    fi
}

for preset in "${PRESETS[@]}"; do
    for arm in "${ARMS[@]}"; do
        render_cell "${arm}" "${preset}"
    done
done

if [[ "${EXECUTE}" -eq 1 ]]; then
    log "raw footage under ${OUT}; stitch with: tools/stitch_dr_explainer.py ${OUT}"
    echo "${OUT}" > "${LUCID_ROOT}/artifacts/dr_explainer_latest.txt"
else
    echo "dry run; pass --execute (GPU must be idle)"
fi
