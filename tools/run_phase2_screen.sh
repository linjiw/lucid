#!/usr/bin/env bash
# LUCID Phase-2: the support-expansion screen.
#
# Five arms at seed 8600, 1,024 environments x 8,000 iterations, every arm
# capped at lambda 1.5 so the primary endpoint stays held out for all of them:
#
#   gate_150    probe stratum one step ABOVE the frontier gates expansion
#   ramp_150    same strata, same probe, frontier on a fixed schedule, reads nothing
#   fixed_150   direct mixed training at 1.5, single stratum   (Gate A)
#   fixed_u150  75% frontier + 25% retention tail, no scheduling
#   fixed       fresh comparator at lambda 1.0
#
# The decisive contrast is gate_150 against ramp_150. Those two share stratum
# count, stratum sizes, probe placement and terminal support, so they differ in
# exactly one thing: how the frontier moves. Beating fixed randomization would
# only show that difficulty rose, which is the trap the ratchet result fell
# into -- it was distributionally identical to fixed DR over 98.75% of training.
#
# Decision rules D1-D4 and mechanism gates G1-G4 are frozen in
#   receipts/manifests/lucid_support_expansion_screen_preregistration_20260901.json
# with amendments A1-A6. This driver does NOT evaluate them; it only trains,
# and refuses to start if anything the preregistration pinned has moved.
#
# Cost: 5 cells x ~5.4 GPU-h = ~27 GPU-h, serial, on one RTX 5080.
#
# usage: run_phase2_screen.sh [--execute]

set -euo pipefail

readonly PIN_COMMIT="dd0fd61b6bf6090d9f0f1c430b2ec895f9e9dc1e"
readonly WORKTREE="/home/linjiw/lucid-phase2"
readonly DEV_REPO="/home/linjiw/lucid/GR00T-WholeBodyControl"
readonly LUCID_ROOT="/home/linjiw/lucid-sonic"
readonly RECEIPTS="/home/linjiw/lucid/receipts/manifests"
readonly PREREG="${RECEIPTS}/lucid_support_expansion_screen_preregistration_20260901.json"
readonly AMENDMENT="${RECEIPTS}/lucid_support_expansion_screen_amendment_20260901.json"
readonly PREREG_SHA256="b1346bb60a37f4fc945323ec07a37804d0d61a8fbe8efdf9dc89b1ffbc71184e"
readonly PY="/home/linjiw/isaaclab-install/env_isaaclab/bin/python"
readonly STAMP="$(date +%Y%m%d_%H%M%S)"
readonly EXPERIMENT="lucid_support_expansion_ne1024_${STAMP}"
readonly RECEIPT_DIR="${LUCID_ROOT}/manifests/support_expansion_${STAMP}"

# Frozen design. Changing any of these without amending the preregistration
# first is exactly what the amendment rule forbids.
readonly SEED=8600
readonly NUM_ENVS=1024
readonly ITERATIONS=8000
readonly MAX_DELAY=12
readonly MOTION="${LUCID_ROOT}/pools/subsets/m1_hob002/robot_filtered"
readonly ENCODER="${LUCID_ROOT}/artifacts/lucid_encoder_debug512.pt"
# The feedback arm runs FIRST so its mechanism telemetry is inspected earliest.
# If it stalls or misbehaves the remaining four still answer the width question.
readonly MODES=(gate_150 ramp_150 fixed_150 fixed_u150 fixed)

EXECUTE=0
[[ "${1:-}" == "--execute" ]] && EXECUTE=1

log() { printf '[%s] %s\n' "$(date '+%F %H:%M:%S')" "$*"; }
die() { echo "REFUSED: $*" >&2; exit 1; }

log "Phase-2 support-expansion screen, experiment ${EXPERIMENT}"

# ------------------------------------------------------------ gate: prereg --

[[ -f "${PREREG}" ]] || die "preregistration missing: ${PREREG}"
[[ -f "${AMENDMENT}" ]] || die "amendment missing: ${AMENDMENT}"
observed_prereg="$(sha256sum "${PREREG}" | cut -d' ' -f1)"
[[ "${observed_prereg}" == "${PREREG_SHA256}" ]] || \
    die "preregistration SHA-256 ${observed_prereg} != frozen ${PREREG_SHA256}"
log "gate 1/5 preregistration: frozen blob verified"

# --------------------------------------------------------- gate: worktree --

[[ -d "${WORKTREE}" ]] || die "clean worktree absent: ${WORKTREE}"
head="$(git -C "${WORKTREE}" rev-parse HEAD)"
[[ "${head}" == "${PIN_COMMIT}" ]] || die "worktree HEAD ${head} != pinned ${PIN_COMMIT}"
[[ -z "$(git -C "${WORKTREE}" status --porcelain --untracked-files=all)" ]] || \
    die "worktree is not clean; untracked research files must not enter the import path"
log "gate 2/5 worktree: clean and detached at ${PIN_COMMIT:0:7}"

# ------------------------------------------------------- gate: provenance --

"${PY}" - "${WORKTREE}" "${PREREG}" "${AMENDMENT}" <<'PYEOF' || die "code-state provenance mismatch"
import hashlib, json, sys
from pathlib import Path
root, prereg_path, amendment_path = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
recorded = dict(json.load(open(prereg_path))["code_state"]["file_sha256"])
for correction in json.load(open(amendment_path))["corrections"]:
    target = correction.get("target", "")
    if correction.get("now") and target.startswith("code_state"):
        recorded[target.split("['")[1].split("']")[0]] = correction["now"]
    for key, value in (correction.get("code") or {}).items():
        if key != "commit":
            recorded[key] = value
bad = []
for name, expected in sorted(recorded.items()):
    path = root / name
    if not path.is_file():
        bad.append((name, "MISSING"))
    elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        bad.append((name, "DRIFT"))
for name, why in bad:
    print(f"  {why}: {name}", file=sys.stderr)
sys.exit(1 if bad else 0)
PYEOF
log "gate 3/5 provenance: all preregistration-pinned files match"

# --------------------------------------------------------- gate: resources --

live="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d' || true)"
[[ -z "${live}" ]] || die "GPU is busy (pids: ${live//$'\n'/,})"
free_mib="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)"
(( free_mib >= 10000 )) || die "only ${free_mib} MiB free; a 1024-env cell needs headroom"
free_gib="$(df -BG --output=avail "${LUCID_ROOT}" | tail -1 | tr -dc '0-9')"
# Five cells x (checkpoint ~0.5 GB + capsules) plus logs; 60 GiB is comfortable.
(( free_gib >= 60 )) || die "only ${free_gib} GiB free under ${LUCID_ROOT}"
for path in "${MOTION}" "${ENCODER}"; do
    [[ -e "${path}" ]] || die "training input missing: ${path}"
done
log "gate 4/5 resources: GPU idle, ${free_mib} MiB free, ${free_gib} GiB disk"

# ------------------------------------------------------- gate: fail-closed --

if [[ -d "${RECEIPT_DIR}" ]]; then
    die "receipt directory already exists: ${RECEIPT_DIR}"
fi
# The launcher itself refuses a delay buffer too small for the arms' lambda
# ceiling. Prove that guard is live before committing 27 GPU-hours to it.
if ( cd "${WORKTREE}" && "${PY}" scripts/practice_utility/run_curriculum_comparison.py \
        --from-scratch --num-envs "${NUM_ENVS}" --iterations "${ITERATIONS}" \
        --seeds "${SEED}" --modes gate_150 --max-delay 8 \
        --motion-file "${MOTION}" --smpl-motion-file dummy --encoder "${ENCODER}" \
        >/dev/null 2>&1 ); then
    die "the delay-buffer guard did NOT fire at --max-delay 8; refusing to trust it"
fi
log "gate 5/5 fail-closed: delay-buffer guard verified live"

mkdir -p "${RECEIPT_DIR}" "${LUCID_ROOT}/outputs/${EXPERIMENT}"

# -------------------------------------------------------------------- run --

args=(
    "${PY}" scripts/practice_utility/run_curriculum_comparison.py
    --from-scratch
    --num-envs "${NUM_ENVS}"
    --iterations "${ITERATIONS}"
    --warmup-iterations 10
    --horizons 500 1000 2000 4000 6000
    --seeds "${SEED}"
    --modes "${MODES[@]}"
    --max-delay "${MAX_DELAY}"
    --termination-thresholds default
    --motion-file "${MOTION}"
    --smpl-motion-file dummy
    --encoder "${ENCODER}"
    --wandb-project lucid-campaign
    --receipt-dir "${RECEIPT_DIR}"
    --log-dir "${LUCID_ROOT}/outputs/${EXPERIMENT}"
    --min-free-mib 6000
)
[[ "${EXECUTE}" -eq 1 ]] && args+=(--execute)

log "launching ${#MODES[@]} arms in order: ${MODES[*]}"
log "receipts -> ${RECEIPT_DIR}"
( cd "${WORKTREE}" && "${args[@]}" )
log "Phase-2 training complete"
