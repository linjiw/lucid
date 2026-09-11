# Anchor startup repair and immediate campaign restart

Campaign `_b` stopped at 15:09 UTC after eight completed cells: three origin evaluations, native and R0 16-iteration training, and three R0 evaluations. R1 rejected its student-origin digest before its first optimizer update. This was an instrumentation failure, not a measured failure of retention repair. Its receipt and W&B runs remain preserved.

The GPU check on the user's return found 12,892 MiB free, exceeding the unchanged 11,000 MiB launch gate. The stopped process, rather than capacity, was then preventing progress.

The R1 optimizer-history receipt confirms exact loaded policy/value identity before rollout. Native `Actor.get_std` clamps the policy's saved `std` parameter in place: the checkpoint maximum is 0.5000085830688477 and the configured maximum is 0.5. The anchor's old full-state digest check ran at first loss computation, after this native mutation. The exact loaded-origin check now runs at trainer entry, before any rollout. Native noise behavior, optimizer recipe, beta, action targets, batching, and all matched scientific budgets remain unchanged. Beta-zero train dispatch is tested as an exact no-op.

- Repair source: `/home/linjiw/lucid-anchor-start-repair`, commit `2d4aa0a`.
- Validation: **2,022 CPU tests passed**, 5 warnings, 39.82 seconds; changed-file Black/Ruff pass.
- CPU log: `/home/linjiw/lucid-sonic/outputs/anchor_start_repair_cpu_20260906_a.log`.
- Native clamp reproduction: `/home/linjiw/lucid-sonic/analysis/anchor_start_repair_20260906_a/native_std_clamp.json`.
- Fresh campaign: `/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_c`.
- Frozen campaign SHA256: `973d303542f2d10ceb0ca00bed9ca71963c7c80a343535927962f966fdf7f4d2`.
- Launched at **15:30:16 UTC**; supervisor PID `2139830`; initial smoke driver PID `2140468`.
- Online W&B monitor PID `2139831`, 15-second polling, separate named cell runs.
- [Campaign dashboard](https://wandb.ai/16726/lucid-sonic/runs/ret-46911b8054776113fe91).

The launch command, source binding, predecessor, and monitor command are in `launch.json`. The independent native-precision buffer check passed again before the smoke driver started. The supervisor executes the entire matched smoke, checks native/R0 parity, then automatically executes three 2,000-iteration training arms and the frozen evaluation grid. No long-arm result is claimed before those jobs complete. Monitoring does not bypass a failed implementation or scientific gate.

## Live verification at approximately 15:47 UTC

The restarted native and R0 branches completed all 16 iterations. An early independent checkpoint comparison found exact native/R0 equality for all 55 policy tensors and 17 value tensors; the supervisor will also run the formal whole-smoke gate. All three origin controls and all three R0 evaluations completed. R1 then passed the former failure point and reached iteration 5 / 100 optimizer updates, with 25,600 anchor sample presentations and 200 physical forwards. The logged nonzero anchor loss after learning is expected; this is a functioning-objective check, not efficacy evidence. GPU utilization at that snapshot was 99%.

Live run verification is recorded in `/home/linjiw/lucid-sonic/monitoring/retention_screen_campaign_20260906_c/R1_online_verification.json`. The full 2,000-iteration arms remain automatically gated on completion of the remaining smoke checks; they are not yet reported as started at this snapshot.

R1 subsequently **completed and passed validation for all 16 smoke iterations**: 320 PPO updates, 81,920 anchor sample presentations, and 640 physical anchor forwards. Its first anchor loss was exactly zero at the origin; later losses became nonzero after learning. The driver has advanced to `eval_R1_16_phys_000`. [R1 W&B run](https://wandb.ai/16726/lucid-sonic/runs/ret-37d12b1491d3576eaf3a). The remaining R1 evaluations and R2 smoke precede the automatic long screen.
