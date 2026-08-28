# SONIC LUCID Restart and Curriculum Debug

Objective: resolve the failed SONIC/LUCID training restart gate, then run a
bounded corrected comparison of LUCID, fixed domain randomization, and no DR.

Primary metrics are restart identity, realized actuator-delay dose, final-four
iteration reward/episode length, latent gap, torque saturation, energy, foot
slip, and curriculum lambda. The seamless continuation result is retained as a
negative finding; the actionable gate tests two symmetric branches restored
from the same capsule because that is the causal experiment's actual boundary.

Every simulator run must source `/data/robotixx/lucid-sonic/lucid_env.sh` and
write a JSON receipt under `/data/robotixx/lucid-sonic/manifests/`.
