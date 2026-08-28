# Source this before any SONIC run in the LUCID practice-utility program.
#
#   source /path/to/lucid/env/lucid_env.sh
#
# Host-independent: every path is derived from this file's own location or from
# a variable you may pre-set. Two Python stacks are supported and auto-detected
# (both are IsaacLab 2.3.2 / IsaacSim 5.1.0 / torch 2.7.0+cu128, python 3.11):
#   * conda env `sonic`              -- the original robotixx host
#   * uv venv `env_isaaclab`         -- the linjiw RTX 5080 workstation
# Pre-set LUCID_PY_ENV to force one.

_lucid_env_file="${BASH_SOURCE[0]:-$0}"
export LUCID_WORKSPACE="$(cd "$(dirname "$_lucid_env_file")/.." && pwd)"
export LUCID_REPO="${LUCID_REPO:-$LUCID_WORKSPACE/GR00T-WholeBodyControl}"

# --- data root (never in git; ~tens of GB) ---------------------------------
# Defaults to the original host's path when it exists, else a home-dir root.
if [ -z "${LUCID_ROOT:-}" ]; then
  if [ -d /data/robotixx/lucid-sonic ]; then
    export LUCID_ROOT=/data/robotixx/lucid-sonic
  else
    export LUCID_ROOT="$HOME/lucid-sonic"
  fi
fi

# --- python stack ----------------------------------------------------------
_lucid_venv=/home/linjiw/isaaclab-install/env_isaaclab
_lucid_conda=/home/robotixx/miniconda3/etc/profile.d/conda.sh
case "${LUCID_PY_ENV:-auto}" in
  conda) _lucid_pick=conda ;;
  venv)  _lucid_pick=venv ;;
  *)     if [ -f "$_lucid_conda" ]; then _lucid_pick=conda
         elif [ -f "$_lucid_venv/bin/activate" ]; then _lucid_pick=venv
         else _lucid_pick=none; fi ;;
esac
case "$_lucid_pick" in
  conda) source "$_lucid_conda"; conda activate sonic ;;
  venv)  export PATH="$HOME/.local/bin:$PATH"
         source "$_lucid_venv/bin/activate"
         export ISAACLAB_PATH=/home/linjiw/isaaclab-install/IsaacLab
         # setuptools>=81 dropped pkg_resources, which flatdict's sdist needs.
         export UV_BUILD_CONSTRAINT=/home/linjiw/isaaclab-install/build-constraints.txt
         # Isaac Sim pins numpy 1.26.0; gear_sonic asks for 1.26.4. Override
         # rather than editing the tracked pyproject (which conflicts on pull).
         export UV_OVERRIDE="$LUCID_WORKSPACE/env/uv-overrides.txt" ;;
  none)  echo "lucid_env: no python stack found; set LUCID_PY_ENV" >&2 ;;
esac

# --- non-negotiable gotchas (never bypass this script) ---------------------
# /tmp/isaaclab may be owned by another user -> keep temp under the data root.
export TMPDIR="$LUCID_ROOT/tmp"
# ROS Humble injects a python3.10 site-packages into PYTHONPATH which breaks
# pytest collection (its `launch` plugin) inside our python3.11 env.
unset PYTHONPATH
# Omniverse EULA accepted by the machine owner.
export OMNI_KIT_ACCEPT_EULA=YES
# Leave headroom for Isaac Sim's own threads; torch grabbing every core thrashes.
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-8}
export MKL_NUM_THREADS=${MKL_NUM_THREADS:-8}
export TRL_EXPERIMENTAL_SILENCE=1
export WANDB_MODE=offline

mkdir -p "$LUCID_ROOT"/{tmp,manifests,artifacts,outputs,pools}
cd "$LUCID_REPO"
unset _lucid_env_file _lucid_venv _lucid_conda _lucid_pick
