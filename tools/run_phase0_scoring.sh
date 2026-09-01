#!/usr/bin/env bash
# LUCID Phase-0 scoring: P3 and the three other unscored controller finals.
#
# Scores the four ne1024 controller arms that have a complete lambda history and
# no robustness score of any kind:
#
#   lucid_rg    @ s8601   final lambda 0.062   <- P3, the predeclared collapse
#   lucid_s4_rg @ s8601   transient dip
#   lucid_rg    @ s8602   transient dip
#   lucid_s4_rg @ s8602   transient dip
#
# P3 is the one measurement that discriminates the candidate exposure laws.
# From lucid_frontier_exposure_law_preregistration_20260901.json, frozen while
# the confirmation was still training:
#
#   recency-weighted predicts   0.725   t(5) PI [0.67376, 0.77569]
#   uniform predicts            0.826   t(5) PI [0.76087, 0.89047]
#   "evacuation is free"        ~0.882
#
#   REJECT the exposure hypothesis if P3 >= 0.881836 or P3 < 0.67366.
#   REJECT the recency term specifically if P3 > 0.77571.
#   [0.76086, 0.77571] discriminates nothing; no model selection is authorized.
#
# Instrument discipline
# ---------------------
# Runs from a detached worktree at ca057e6, where the evaluator hashes to
# 308e24150e4d4f03d0abf0dc6a427063ac662904bb3a7765488a9bff63cd94ca -- the build
# that produced all seven historically scored arms. The development branch has
# since changed that file, and a mixed-instrument comparison is exactly the
# error this programme is organised to avoid.
#
# Evaluation seed follows the checkpoint seed, matching the existing ledger:
# 8700 for seed-8600 arms, 8701 for 8601, 8702 for 8602.
#
# Fail-closed: refuses to start while any compute process holds the GPU, and
# stops at the first nonzero cell rather than continuing with a hole.
#
# usage: run_phase0_scoring.sh [--execute]

set -euo pipefail

readonly PIN_COMMIT="ca057e658acc59773e798057980b827d65988441"
readonly EXPECTED_EVALUATOR_SHA256="308e24150e4d4f03d0abf0dc6a427063ac662904bb3a7765488a9bff63cd94ca"
readonly DEV_REPO="/home/linjiw/lucid/GR00T-WholeBodyControl"
readonly WORKTREE="/home/linjiw/lucid-phase0-eval"
readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly RECEIPT="${LUCID_ROOT}/manifests/lucid_campaign_unscored_finals.json"
readonly PANEL="${LUCID_ROOT}/manifests/replicate_panel_panel_hob002_k512.json"
readonly PY="/home/linjiw/isaaclab-install/env_isaaclab/bin/python"
readonly STAMP="$(date +%Y%m%d_%H%M%S)"
readonly EXPERIMENT="phase0_scoring_${STAMP}"

EXECUTE=0
[[ "${1:-}" == "--execute" ]] && EXECUTE=1

log() { printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }

# ------------------------------------------------------------ preconditions --

log "Phase-0 scoring, experiment ${EXPERIMENT}"

for path in "${RECEIPT}" "${PANEL}"; do
    [[ -f "${path}" ]] || { echo "missing required input: ${path}" >&2; exit 1; }
done

live="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d' || true)"
if [[ -n "${live}" ]]; then
    echo "GPU is busy (pids: ${live//$'\n'/,}). The H_R2 confirmation must finish first." >&2
    echo "Re-run when nvidia-smi reports no compute processes." >&2
    exit 1
fi

# --------------------------------------------------------- pinned worktree --

if [[ ! -d "${WORKTREE}" ]]; then
    log "creating pinned worktree at ${PIN_COMMIT:0:7}"
    git -C "${DEV_REPO}" worktree add --detach "${WORKTREE}" "${PIN_COMMIT}" >/dev/null
fi

head_sha="$(git -C "${WORKTREE}" rev-parse HEAD)"
if [[ "${head_sha}" != "${PIN_COMMIT}" ]]; then
    echo "worktree HEAD ${head_sha} != pinned ${PIN_COMMIT}" >&2; exit 1
fi
if [[ -n "$(git -C "${WORKTREE}" status --porcelain --untracked-files=all)" ]]; then
    echo "pinned worktree is not clean; refusing to score with an unknown instrument" >&2
    git -C "${WORKTREE}" status --short >&2
    exit 1
fi

evaluator="${WORKTREE}/scripts/practice_utility/run_curriculum_robustness_eval.py"
observed="$(sha256sum "${evaluator}" | cut -d' ' -f1)"
if [[ "${observed}" != "${EXPECTED_EVALUATOR_SHA256}" ]]; then
    echo "evaluator SHA-256 ${observed} != pinned ${EXPECTED_EVALUATOR_SHA256}" >&2; exit 1
fi
log "instrument verified: evaluator ${observed:0:12} at ${PIN_COMMIT:0:7}"

# ------------------------------------------------------------------- cells --

# The four frontier cells are the endpoint; the five in-envelope cells cost
# about 3 minutes total and complete the ladder, so the collapse arm is
# comparable to every other arm on the full physics profile rather than only at
# the endpoint.
readonly PRESETS="phys_000 phys_025 phys_050 phys_075 phys_100 phys_125 phys_150 phys_175 phys_200"

# Each arm carries its OWN true adjacent config.yaml from its Hydra run
# directory, and they differ between arms. ensure_checkpoint_configs installs a
# single config beside every checkpoint in one invocation, so each arm is scored
# in its own invocation with its own pinned config -- the same discipline the
# historical bridge uses when it stages checkpoints with their true configs.
score_one() {
    local seed="$1" mode="$2" eval_seed="$3"
    local config sha
    config="$("${PY}" -c "
import json,sys
d=json.load(open('${RECEIPT}'))
for a in d['arms'].values():
    if a['seed']==${seed} and a['mode']=='${mode}':
        print(a['training_config']); break
else:
    raise SystemExit('no arm ${mode}@${seed} in receipt')
")"
    [[ -f "${config}" ]] || { echo "training config missing: ${config}" >&2; exit 1; }
    sha="$(sha256sum "${config}" | cut -d' ' -f1)"
    log "${mode}@s${seed} -> eval seed ${eval_seed}, config ${sha:0:12}"
    local args=(
        "${PY}" "${evaluator}"
        --training-receipt "${RECEIPT}"
        --training-config "${config}"
        --num-envs 512
        --seeds "${seed}"
        --modes "${mode}"
        --presets ${PRESETS}
        --eval-seed-base "${eval_seed}"
        --max-delay 12
        --panel-receipt "${PANEL}"
        --smpl-motion-file dummy
        --artifact-root "${LUCID_ROOT}/artifacts/${EXPERIMENT}"
        --log-dir "${LUCID_ROOT}/outputs/${EXPERIMENT}"
        --receipt-dir "${LUCID_ROOT}/manifests"
    )
    if [[ "${EXECUTE}" -eq 1 ]]; then
        args+=(--execute)
    fi
    ( cd "${WORKTREE}" && "${args[@]}" )
}

mkdir -p "${LUCID_ROOT}/outputs/${EXPERIMENT}"

# P3 first: it is the only measurement on this list that can change the
# paper's framing, and if anything goes wrong later it is the one to have.
score_one 8601 lucid_rg     8701
score_one 8601 lucid_s4_rg  8701
score_one 8602 lucid_rg     8702
score_one 8602 lucid_s4_rg  8702

log "Phase-0 scoring complete. Receipts in ${LUCID_ROOT}/manifests"
log "Score P3 with: tools/score_p3.py"
