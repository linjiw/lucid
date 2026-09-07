# Common path-error input: bounded controller repair before LUCID comparisons

September 7, 2026 UTC. Prospective implementation brief following the completed [physical observability experiment](lucid-translation-observability-2026-09-07.md). This is a common-controller change, not a LUCID curriculum contribution. The input and bounded pilot are implemented. Two cross-process rollout gates failed; the documented same-state live gate subsequently passed, and protected PPO has started. See the [current implementation and experiment status](lucid-common-path-input-status-2026-09-07.md).

## Evidence and scope

The released G1 controller performs the four development motions, but in the tested otherwise identical states a ±0.25 m horizontal displacement changes critic/task error while leaving active actor inputs, G1 encoding and action means exactly unchanged. This does not rule out recovery from pushes using other cues or histories. It does show that the current interface cannot condition on horizontal path error independently of those cues.

Keep the stronger return-to-path objective. Do not reinterpret existing local-pose qualification as recovery to the requested trajectory, and do not expect a training-only observer to repair an actor input omission.

## Minimal proposed interface

Provide the instantaneous horizontal reference-minus-robot anchor displacement, rotated into the robot's heading frame. Fix the initial world/reference alignment once. Use explicit metre units and a frozen input scale; record any clipping and its representational limit. Robot root translation and reference translation must use the same timestamp/frame. Heading is already represented in the existing G1 encoder input; this addition addresses horizontal displacement only.

Implement a separate research observation group and append its two values to the decoder's proprioception inputs. Keep the existing 930-dimensional actor observation, its ten-step per-term histories, G1 tokenizer inputs, joint/action ordering and encoder unchanged. A separate group avoids accidentally inserting coordinates into the middle of an existing history layout.

The inspected released decoder has first weight `actor_module.decoders.g1_dyn.module.0.weight`, shape 2048 × 994: 64 token values plus 930 proprioception values. Appending two new inputs makes it 2048 × 996. A migration should preserve every old column and append two zero columns; all other actor parameters, including action-distribution parameters, retain their released values. The kinematic reconstruction decoder does not consume proprioception and should not be expanded.

This construction is intended to preserve the initial policy function while exposing a trainable path-error dependence. Numerical and live no-op checks are required; zero padding alone is not a simulator-parity result. A fresh optimizer is required when training the expanded parameter tensor. Do not reuse incompatible Adam moments or silently load only matching checkpoint keys.

## Gates before the repair becomes the shared origin

1. **CPU migration and data contract.** Strict checkpoint/configuration hashes, exact old-column preservation, zero new columns, reject already-expanded or wrong-shaped inputs, explicit normalization and frame convention. Test zero and nonzero path inputs, no-op forward tolerances on real origin histories, nonzero gradients to the new columns, deterministic serialization/reload, and unchanged encoder outputs. The actor must receive the fresh term rather than stale history.
2. **Native information and no-op tests.** Re-run the physical-state input diagnostic through the augmented observation group; translations must now change the added input. Zero-initialized actions should still match the released policy within predeclared numerical tolerances. Measure ordinary rollout parity separately on all four original candidates with matched execution paths and seeds.
3. **Bounded common-controller learning pilot.** Use a fixed, motion-balanced recipe and nominal protection. Start with the smallest trainable extension justified by the migration, then evaluate actual path correction on dedicated disturbance trials. Freeze trainable parameters, perturbation process, endpoint and resource limit before launch. This pilot tests a controller repair; it contains no learned observer or feedback scheduler.
4. **Requalify the common origin.** Freeze tighter per-motion competence/tail/sustained-error requirements using development data; evaluate fresh episodes. Require the declared longer solved repertoire, retained nominal behavior and observable return-to-task under the chosen event window. If the repair fails, report it and diagnose the controller rather than launching a curriculum sweep.

The released reward configuration already has a `tracking_anchor_pos` term (weight 0.5, Gaussian scale 0.3 m). Its implemented error uses reference-minus-robot anchor position. Preserve that objective for the first input-only repair unless a separately frozen experiment identifies a need to change it; simultaneous input/reward changes would obscure the diagnosis.

## Shared comparison and deployment boundary

After qualification, freeze this same repaired origin for protected fixed practice, frozen schedule, direct-feedback gate and LUCID. Give every arm the same observation source, scale, protection recipe and allowed conditions. Controller-repair data and compute belong in the cost ledger. An improvement caused by access to path error is attributed to that access, not to recovery feedback.

Exact simulator position is an explicitly privileged simulation input until a corresponding deployment measurement is established. Document the real position estimator, reference synchronization and independent evaluation ground truth before claiming deployment compatibility. A recorder alone does not provide the controller input. Keep the independently measured hardware return-to-path question open.
