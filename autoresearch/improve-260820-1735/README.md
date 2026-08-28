# LUCID Terminal-Consolidation Iteration

Objective: improve deployment-domain robustness without selecting from training
reward. The completed 32-iteration study ended LUCID at mean lambda 0.756;
fixed DR was slightly better under fresh full-envelope DR, while LUCID retained
better clean success. All policies failed the deliberately out-of-range fixed
60 ms test.

Iteration 1 changes one treatment: continue each existing LUCID checkpoint for
an equal 16 PPO iterations at lambda 1 (terminal full-DR consolidation). Matched
fixed-DR checkpoints receive the same 16-iteration compute under lambda 1.
Seeds, 128 environments, debug512 motion pool, six-channel 0--40 ms training
envelope, optimizer state, and evaluation protocol remain fixed. This isolates
late full-DR exposure; latency-range expansion is reserved for the next
iteration if 60 ms robustness remains absent.

Primary decision metric: frozen-policy success under fresh full-envelope DR on
the 102-motion content-dev panel. Keep the schedule if consolidated LUCID
improves at least 2 percentage points over its prior 54.25% success, is no more
than 2 points below the matched continued fixed baseline, and loses less than 3
points from its prior 83.99% clean success. Record 60 ms success/progress as a
deployment stress result, not as a tuning target. Training reward is diagnostic
only. Episode-masked physical-quality claims remain out of scope.

All simulator commands source `/data/robotixx/lucid-sonic/lucid_env.sh`; every
run writes a receipt under `/data/robotixx/lucid-sonic/manifests/`. No final-test
motions, estimator, residual allocator, upstream SONIC edits, or MJLab pivot are
authorized by this iteration.

Iteration 1 was discarded: sixteen abrupt full-DR continuation iterations
reduced LUCID clean success by 7.19 points and full-DR success by 2.29 points;
fixed DR degraded even more. Iteration 2 isolates terminal dose duration by
restarting again from the original step-32 checkpoints and applying exactly
four full-DR continuation iterations. No other training or evaluation setting
changes. The same keep thresholds apply.

Iteration 2 was also discarded. Four abrupt full-DR iterations reduced LUCID
clean success by 4.58 points and full-DR success by 2.94 points. The original
step-32 LUCID checkpoints remain the retained result. Across both variants,
additional full-DR exposure slightly increased 60 ms progress but never yielded
a single success. The next curriculum must integrate a smooth terminal ramp
inside the original equal-compute budget and train latency support through 60
ms; post-hoc hard switching is closed as an improvement path.
