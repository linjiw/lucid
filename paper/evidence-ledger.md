# Evidence ledger — September 8 diagnostic revision

Internal navigation, excluded from the anonymous manuscript. The current scientific source is `when-training-gets-easier.md`; the September 7 manuscript and earlier IROS programme are historical sources, not interchangeable evidence. The portable package's `data/manifest.json` binds compact files to source hashes. Its identifying source map remains private, outside the archive.

## Current claim map

| Claim / location | Experimental unit and denominator | Portable evidence and computation | Limit |
|---|---|---|---|
| Six A/B runs contract; two collapse (III-A, Fig. 1) | Two recorded shrink-permitted modes × seeds 8600–8602; 8,000-iteration endpoints | `data/historical.json`, `data/range_traces.json.gz`, `analysis/historical_census.csv` | Other full-range endpoints can also have poor AUC |
| Twelve-policy return–AUC correlation (abstract, III-A) | A/B/N/F × three training seeds; no no-DR point | `analysis/diagnostic.json:return_auc_spearman`; `auc` integrates `phys_125..200` | Association across studied controllers, not a fixed-policy causal decomposition |
| Never-shrink empirical decision and uncertainty (III-B, Fig. 2) | Three N-minus-F training-seed contrasts, separately four metric/band components | `data/tolerance.json`; `analysis/diagnostic.json:contrasts` | One-sided empirical degradation tolerance passes; statistical noninferiority/equivalence unsupported |
| Complete retention at all sampled checkpoints (IV-B, Fig. 3, Table 3) | One origin, one motion; seed 8600 R0/R1/R2 and seed 8601 R0/R1; five checkpoints and campaign-specific origin | `data/retention_episodes.json.gz` (135 panels × 512 trials), `analysis/retention_summary.csv`, `analysis/retention_constituents.csv` | R1 passes 10/10 sampled checks; R0 fails 10/10, R2 fails 5/5. No guarantee between samples or across origins |
| Sampled early-stopping alternative (IV-C) | The complete frozen checkpoint schedule; both protected conditions | `analysis/diagnostic.json:early_stopping` | No feasible sampled R0/R2 continuation; retrospective R1 maxima are not held-out performance |
| Threshold sensitivity (IV-C, Fig. 4) | Every checkpoint × all 25 threshold pairs; hard conditions equally weighted | `analysis/threshold_sensitivity.csv` (675 rows) | Exploratory reporting grid fixed before this computation; 600/50 mm remains primary; R0's negative cells retained |
| Physical/controller/optimizer/anchor definitions (II, IV-A) | Recorded common config, arm-specific saved state, and native validation receipts | `data/method.json`, `data/historical.json:controller_state`, `data/anchor_validation.json` | Stale adjacent config labels do not define arms; actual optimizer starts take precedence over unused config fields |
| Legacy drift and optimizer-history control (IV-A) | Separate legacy accumulation protocol and pilot checkpoint | `data/secondary_controls.json:legacy_controls` | Restoration is not necessary for drift; reconstructed parameter binding limits attribution; duplicate fresh/hold condition counted once |
| Secondary nominal 8.79% margin (IV-B) | Separate seed-8730, 128-alias panel | `data/secondary_controls.json:secondary_nominal_128` | Different origin-panel denominator; never pool with primary 512-alias result |
| Limited MuJoCo check (V, Fig. 5) | Historical ONNX policies, 32 draws/cell, independently implemented physics | `data/mujoco.json` (960 draw outcomes across five policies, three scales, two push settings) | Ordering reverses at no-push scale 1; not continuation R1 or hardware |
| Additive-loss residual and signal audit (III-A, V) | Historical saved audit panels | `data/channel_sweep.json`, `data/signal_audit.json` | Descriptive residual, not an identified pairwise interaction or unique collapse cause |
| Video illustrations | Four historical policies × two scales × eight recorded draws | `evidence/historical-video-source.json`, video receipt and hashed source footage | All 64 existing tiles; no matched R0/R1 trajectories or world-path error evidence |

## Frozen replication and provenance

Private root: `/home/linjiw/lucid-sonic`.

- First campaign: `experiments/retention_screen_campaign_20260906_c/pilot`; 83 completed cells, 80 evaluation panels. Frozen plan SHA256 `9ddfe9549ea094caebd41e545be88f0d243bd11c87b6e4c44b0914754687c01a`.
- Repetition: `experiments/retention_second_seed_20260907_c/pilot`; 57 completed cells, 55 evaluation panels. Frozen plan SHA256 `57fbff80fbcd47f740f0e7bff9f7f84e7bef7892a92b50fd61396cb4ce7827cd`.
- The September 7 `_b` plan is superseded by the documented orchestration repair. Its failed logging receipt is preserved. Completed R0 training was reused with final checkpoint SHA256 `852c704d5c4ad189f3326fb53003e60caec2e50b43b569480782e6c8b2a849fb`; it was not rerun to choose a favorable result.
- Common origin SHA256 `e7fe72a0a48d6d4d534368ee9870b7a5e382bf2c51bb025d35eadee0818aaa8d`; collected anchor buffer SHA256 `3517adde328c64d14304f9fab2dfd96f4a4c744ebe2213b2cc6971ee295a4b85`.
- Export rechecked every one of the 135 raw metric hashes against the frozen receipts and recomputed 69,120 episode records. Native cached-action equality is taken from the completed CUDA/TF32 validation, not a new GPU replay in this revision.
- W&B online status was checked read-only in entity `16726`, project `lucid-sonic`. The repaired repetition's 57 runs are finished; the historical `_b` logging failure remains visible. Example verified repetition run: https://wandb.ai/16726/lucid-sonic/runs/p4rvttfe . Complete URL/status inventory: `outputs/icra_revision_20260908/wandb_online_check.json` in the private root. W&B groups may include monitor/smoke runs; their run count is not the experimental-cell denominator.

The original historical receipts remain `receipts/analysis/lucid_return_inversion_20260901.json`, `lucid_phase0_analysis_20260901.json`, `lucid_signal_audit_20260901.json`, `lucid_channel_attribution_20260902.json` and `mujoco_sim2sim_20260902/`. The export preserves their hashes; it does not rewrite source evidence.

## Unavailable evidence and release conditions

Central continuation records do not contain saved time-resolved body/reference/heading trajectories. No root-error subtraction or substitute historical video is used. Existing historical robustness cells do not provide the complete early/late × narrow/wide return matrix with the required common scoring contract. The optional new evaluation is not launched; the central interpretation stays observational.

The completed arithmetic, data build and artifact checks do not provide independent human scientific review, establish IROS 1615 eligibility, or constitute author approval. See `submission-review-2026-09-08.md` for the remaining release decisions. BeyondMimic, released-controller/path-input studies, calibrated recovery claims and old hardware/superiority claims remain outside this diagnostic evidence set.
