# MuJoCo sim-to-sim survival experiments (2026-09-02)

Policies exported to ONNX (`scripts/practice_utility/eval_with_delay.py ... +export_onnx_only=true`)
and replayed in MuJoCo by `tools/mujoco_player.py` on the trained clip
`walk_hands_on_back_loop_002__A066_M`, with hand-built approximations of the six Isaac
DR channels scaled by λ. A run passes if the anchor error stays under 0.5 m to the end of
the 4 s clip; otherwise the fall time is recorded. Seeds are shared across arms.

| file | what |
|---|---|
| `sweep_full_channels*` | 5 arms × 6 λ × 32 seeds, all channels (pushes included) |
| `sweep_physics_only*` | 5 arms × λ {1, 1.5, 2} × 32 seeds, friction+mass+com+joint+delay, no pushes |
| `story_full_ladder_manifest.json` | 8-seed grids behind `artifacts/mujoco_story_20260902/story.mp4` |
| `story_frontier_manifest.json` | 8-seed grids behind `artifacts/mujoco_story_frontier_20260902/story.mp4` (physics-only, λ 1.5 / 2) |
| `explainer_captions.json` | first 3-arm explainer, `artifacts/mujoco_dr_explainer_20260902_150259/final/` |

Videos live under `$LUCID_ROOT/artifacts/` (not versioned). MuJoCo survival and Isaac
512-episode ledger numbers are shown side by side in every header and never pooled.

Readout: with pushes, the ordering off < collapsed < {ratchet ≈ paired fixed} < fixed@s8600
holds from λ 1 up. Without pushes, beyond the training envelope (λ 2) ratchet and paired
fixed tie at 38 %, the collapsed controller reaches 16 %, no-DR 3 %. Push is the binding
channel in MuJoCo as in Isaac; the residual MuJoCo-vs-Isaac gap is the sim2sim gap and is
reported, not tuned.
