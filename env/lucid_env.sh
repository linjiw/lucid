# Source this before any SONIC run in the LUCID practice-utility program.
source /home/robotixx/miniconda3/etc/profile.d/conda.sh
conda activate sonic
export LUCID_ROOT=/data/robotixx/lucid-sonic
export LUCID_REPO=/home/robotixx/lucid/GR00T-WholeBodyControl
# /tmp/isaaclab is owned by another user on this host; keep all temp under our data root
export TMPDIR="$LUCID_ROOT/tmp"
# ROS Humble injects a python3.10 site-packages into PYTHONPATH which breaks
# pytest collection (its `launch` plugin) inside our python3.11 env.
unset PYTHONPATH
# This host's 20 cores are usually shared with Isaac Sim runs; letting torch
# claim all of them makes CPU work (tests, VAE pretraining) thrash badly.
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-4}
export MKL_NUM_THREADS=${MKL_NUM_THREADS:-4}
export TRL_EXPERIMENTAL_SILENCE=1
export WANDB_MODE=offline
mkdir -p "$TMPDIR"
cd "$LUCID_REPO"
