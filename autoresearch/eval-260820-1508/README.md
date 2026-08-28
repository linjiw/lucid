# Frozen SONIC Curriculum Robustness Evaluation

Objective: compare the nine frozen LUCID, fixed-DR, and no-DR checkpoints under
identical deployment-oriented evaluation distributions. Training rewards are
not the estimand.

Presets are nominal, fresh full-envelope six-channel DR, and latency beyond the
40 ms training ceiling. Every mode uses matched checkpoint seeds, evaluation
seeds, motions, episode counts, and quality telemetry. No gradient updates are
allowed. The 102-motion content-dev panel is physics-heldout, not motion-heldout,
because the retraining run used the complete debug512 pool.

Primary outcomes: success/termination, MPJPE, completion, foot slip, contact
impulse, torque saturation, energy, and latency dose. Simulator jobs must source
`/data/robotixx/lucid-sonic/lucid_env.sh` and write receipts under
`/data/robotixx/lucid-sonic/manifests/`.

The corrected seed-8600 LUCID pilot passed every mechanism audit: clean success
83.33%, full-DR success 55.88%, and 60 ms success 0%. The last condition is an
intentional beyond-range stress, not a deployability pass. The full nine-policy
matrix is required before comparing curricula.
