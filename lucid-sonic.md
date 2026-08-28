# Practice What Transfers

## Counterfactual Practice Utility for SONIC Whole-Body Control

### Detailed Research and Implementation Design Plan

## 0. 一句话研究判断

SONIC 当前依据 motion bin 的失败率分配训练经验；LUCID 当前依据 command–execution mismatch 调整扰动难度。两者都描述了机器人**现在在哪里表现不好**，但它们没有直接测量：

[
\boxed{
\text{在这里多训练一点，是否会使未来部署能力真正变好？}
}
]

本项目将训练分布选择从 current difficulty 重新参数化为 **counterfactual practice utility**：从完全相同的 SONIC policy checkpoint 出发，通过 paired branch-and-continue intervention，直接测量增加某个 motion 或 motion–physics context 的训练剂量后，未来 deployment performance 的变化。

本项目分成三个严格受门控的层级：

1. **Measurement:** SONIC 的 failure、tracking error、latent mismatch 是否能预测长期 practice utility？
2. **Method:** 若不能，用一个受限、可退回原系统的 residual utility sampler 改善训练分配。
3. **Physics extension:** 只有 motion-level 因果关系成立后，才把 context 扩展到 motion × perturbation，并研究 sim-to-real。

这三个层级不能同时开工，也不能把后一个层级的复杂度用于挽救前一个层级尚未成立的假设。

---

# 1. 已验证的研究基座

## 1.1 SONIC 已经提供了我们需要审计的真实 curriculum

SONIC 将大规模 motion tracking 作为统一控制任务，并将模型、数据与计算规模扩展到 42M parameters、100M+ frames 和 21k GPU hours；它使用一个 universal token controller，将 G1 reference、SMPL 和 VR 等不同输入映射到共享 representation。官方模型以 50 Hz 运行，并提供可继续训练的 PyTorch checkpoint。

当前官方配置采用 adaptive motion sampling：

* 默认 `bin_size = 50` frames；
* default target motion frequency 为 50 Hz；
* 每个 bin 的 failure rate 决定后续采样权重；
* failure-rate concentration 由 `adp_samp_failure_rate_max_over_mean = 200` 截断；
* 同时保留 uniform component 与 per-bin/per-motion coverage protection。

因此，在默认配置下，每个 curriculum unit 约是一秒 motion segment。它天然提供了一个可以被质疑和因果审计的假设：

[
\text{failure rate high}
\quad\Rightarrow\quad
\text{should receive more practice}.
]

## 1.2 SONIC 的架构适合 residual research，而不应被重写

官方训练栈由 Hydra configuration、Isaac Lab `ManagerBasedRLEnv`、`ManagerEnvWrapper`、PPO trainer、auxiliary losses、evaluation callback 和 motion-resampling callback 组成。Released `sonic_release` configuration 使用 4096 environments、24 rollout steps、G1/teleop/SMPL encoders、UniversalToken module 和 existing motion resampling。

因此，本项目不更改：

* SONIC actor–critic architecture；
* universal token representation；
* FSQ quantization；
* PPO objective；
* tracking reward；
* auxiliary reconstruction losses；
* PD-controller action semantics。

我们只增加：

1. 可审计的 context sampling interface；
2. 完整 branch state；
3. counterfactual probe runner；
4. 独立 physical-quality evaluation；
5. 最后才增加 bounded residual allocation。

这确保任何结果都能归因于“练什么”，而不是换了一个更大的 policy。

## 1.3 当前 LUCID 结果规定了本项目的纪律

LUCID 原始方法使用 temporal VAE 对 commanded 与 executed joint windows 编码，并以 cosine latent gap 的高分位数控制一个 global DR scale。论文强调 return 和 success 可能延迟，而且 success 可能掩盖 jitter，这个动机仍然成立。

但后续仓库证据已经表明：

* scalar LUCID 不应继续作为当前 paper method；

* matched baseline 解释了早期部分 gain；

* latent gap 可以改善，而 reward 和 episode length 同时恶化；

* raw/latent metrics 可能在 bad-quality rows 上出现假改善；

* mass/COM、friction 和 gain/damping payload 尚未形成对齐的正结果；

* scheduler expressiveness 不是当前主要瓶颈。

因此，本设计采用下面的硬规则：

> **在 oracle measurement 表明 difficulty proxy 与 long-horizon utility 存在系统错位之前，不训练 utility scheduler。**

---

# 2. 研究问题、假设与可证伪边界

## RQ1：Current difficulty 是否预测 future practice value？

给定当前 SONIC policy (\theta_k) 和 motion bin (b)，比较：

[
d_k(b)
======

\text{当前 failure / error / mismatch}
]

与

[
U_H(b\mid\theta_k)
==================

\text{在 }b\text{ 上增加训练剂量后，未来性能的变化}.
]

### Hypothesis H1

Native failure rate、tracking error 和 latent mismatch 能预测 short-horizon utility，但不能稳定预测 long-horizon utility。

### Falsification H1

若 failure rate 或 latent mismatch 对 held-out contexts 的 (U_H)：

* sign accuracy 足够高；
* ranking 稳定；
* calibration 良好；
* 跨 policy stage、motion family 和 perturbation group 不发生明显 reversal；

则不应训练复杂 utility estimator。最好的论文结论将是：

> A simple calibrated difficulty signal is sufficient.

这会强化 SONIC 或 LUCID，而不是削弱项目价值。

---

## RQ2：Counterfactual utility 是否可被可靠测量？

### Hypothesis H2

经过 paired initialization、matched compute、common random numbers 和 exact dose accounting 后，不同 context 的 utility variation 大于 branch stochasticity。

### Falsification H2

如果同一个 context 在 fresh paired seeds 上的 utility variance 与不同 contexts 之间的 variation 同量级，context-level utility 就不可辨识。

此时应当：

* 将 context 合并为 coarser motion families；
* 或将 utility 定义在 perturbation group 层级；
* 或停止 context-level method claim。

不能用更大的 neural estimator 掩盖 noisy labels。

---

## RQ3：Residual utility allocation 是否优于 SONIC 原生 sampler？

### Hypothesis H3

在相同 PPO updates、environment interactions、motion support、optimizer 和 checkpoint-selection rule 下，utility-guided residual sampling：

* 提高 learning-curve AUC；
* 改善 final held-out motion performance；
* 改善 worst-family 或 worst-perturbation performance；
* 不降低 clean tracking quality；
* 不增加 action/contact/actuator damage。

### Falsification H3

如果它只提高早期 AUC，而 sufficiently trained native SONIC 最终追平，则结论只能是：

> practice utility accelerates adaptation,

而不是：

> practice utility produces a better asymptotic controller.

---

# 3. 研究范围：先 motion，后 physics

## 3.1 Core context：SONIC 原生 motion bin

第一阶段定义：

[
x=b,
]

其中 (b) 是 SONIC motion library 中的一个 native 50-frame bin。

这一阶段：

* 保持 SONIC 原生 DR distribution 不变；
* 只改变不同 motion bins 的训练概率；
* 固定 G1-reference encoder；
* 不同时混入 SMPL、teleop encoder sampling；
* 不引入新的 latency 或 actuator model。

这一步直接审计 SONIC 的 failure-based sampling，变量最少，因果解释最清楚。

## 3.2 Extension context：motion × supported physics

Motion-level utility 通过门控后，再定义：

[
x=(b,g,s),
]

其中：

* (b)：motion bin；
* (g)：perturbation group；
* (s)：severity level。

第一批 physics groups 只使用当前 SONIC/Isaac Lab 基础设施已支持且可审计的因素：

1. material：static/dynamic friction 与 restitution；
2. mass/CoM；
3. external push；
4. reference-command perturbation；
5. clean nominal control。

当前 `level0_4` 配置包含 physics material、joint-default offset、base CoM、push 和 rigid-body mass；它并没有原生 LUCID-style actuation delay channel。因此 latency 不进入第一轮 context space。

## 3.3 Latency extension

只有 physics-group experiment 成立后，才实现 explicit FIFO delay：

[
a_t^{exec}=a_{t-d}^{cmd}.
]

SONIC policy rate 是 50 Hz，因此：

* (d=0)：0 ms；
* (d=1)：20 ms；
* (d=2)：40 ms；
* (d=3)：60 ms。

这可以与 LUCID 的 0–40 ms training range 和 60 ms unseen stress setting 对齐，但必须先通过：

[
d=0
\Rightarrow
\text{trajectory-equivalent native SONIC}
]

这一 identity test。LUCID 上传稿件正是以 60 ms 超训练范围 latency 作为 isolated stress evaluation。

---

# 4. Counterfactual Practice Utility 的正式定义

## 4.1 Base distribution

在 policy checkpoint (\theta_k) 时，令 SONIC 原生 sampler 给出的 distribution 为：

[
\rho_k(b).
]

它包含：

* 当前 accumulated failure statistics；
* uniform floor；
* bin weights；
* per-bin/per-motion concentration caps。

我们不重新实现一个“近似 SONIC sampler”。控制分支直接使用当前 sampler state 的 frozen snapshot。

## 4.2 Local intervention kernel

对候选 bin (b)，定义同一 motion clip 内的 local kernel：

[
\kappa_b(j)
\propto
\exp\left(-\frac{|t_j-t_b|}{\sigma_b}\right),
]

并限制在 (b) 及其前后相邻 bins。

不把全部 probability mass 压到单个 bin，原因是：

* 一个 bin 的开始可能缺少进入姿态；
* difficult transition 常跨越 bin boundary；
* 单点 oversampling 容易形成不自然的 phase distribution。

初始 kernel 采用 radius (=1) bin；这意味着训练集中增加的是约三秒局部 motion neighborhood，而不是一个孤立 frame segment。

## 4.3 Equal-compute intervention

定义：

[
\rho_{k,b}^{\epsilon}
=====================

(1-\epsilon)\rho_k+\epsilon\kappa_b.
]

这里不是额外增加 rollout。Intervention branch 与 control branch 的总采样概率仍为 1，总 PPO budget 完全相同。

初始候选：

[
\epsilon=0.10.
]

但在主实验前，用小规模 dose-response pilot 检查：

* (\epsilon) 是否足够产生可测信号；
* 是否过大到改变总体 curriculum support；
* utility 是否在小剂量区间近似平滑。

## 4.4 Paired branch-and-continue

从完全相同的 branch capsule 出发：

[
\theta_{k,H}^{0}
================

\operatorname{Train}_{H}
(\theta_k;\rho_k,\xi),
]

[
\theta_{k,H}^{b}
================

\operatorname{Train}*{H}
(\theta_k;\rho*{k,b}^{\epsilon},\xi).
]

其中 (\xi) 表示所有可匹配的随机性。

Control branch 继续接受正常训练，intervention branch 只重新分配一部分训练经验。

绝不能比较：

[
J(\theta_{k,H}^{b})-J(\theta_k),
]

因为这会把“一般继续训练的收益”误认为 context utility。

真正的 paired effect 是：

[
\Delta J_H(b)
=============

## J(\theta_{k,H}^{b})

J(\theta_{k,H}^{0}).
]

## 4.5 Exact dose normalization

名义上的 (\epsilon H) 不等于实际接受的 context exposure。由于 episode termination、motion length、parallel sampling 和 distributed resampling，必须记录实际剂量：

[
D_H^a(b)
========

\sum_{e,t}
w_b(x_{e,t}^{a}),
\qquad
a\in{0,b},
]

其中 (w_b) 是 kernel membership weight。

额外剂量为：

[
\Delta D_H(b)
=============

D_H^{b}(b)-D_H^{0}(b).
]

最终 utility 定义为：

[
U_H(b\mid\theta_k)
==================

\frac{\Delta J_H(b)}
{\Delta D_H(b)+\varepsilon_D}.
]

每一个 branch report 都必须同时报告：

* nominal intervention；
* intended distribution；
* actual sampled bins；
* actual environment steps；
* actual completed steps；
* early-termination-adjusted dose；
* distribution KL；
* sampling entropy；
* per-motion coverage。

---

# 5. Multi-horizon utility

Practice value可能随时间发生反转。因此每个 branch 在中间 checkpoints 上评估：

[
H\in{H_s,H_m,H_l}.
]

初始候选为：

[
H_s=8,\qquad H_m=32,\qquad H_l=128
]

个 PPO iterations。

这些数字不是未经测量的最终常数。Phase 0 throughput pilot 后，以实际 environment transitions 和 policy-change magnitude 冻结 horizon。选择标准是：

* (H_s)：能看到 immediate optimization response；
* (H_m)：能看到 transfer；
* (H_l)：足以暴露 forgetting 或 negative transfer；
* 同一 intervention branch 可保存三个中间 checkpoint，避免三次独立训练。

Utility label 是一个向量：

[
\mathbf U(b)
============

\left[
U_{H_s}(b),
U_{H_m}(b),
U_{H_l}(b)
\right].
]

特别关注下面三种 context：

### Immediate-only

[
U_{H_s}>0,\qquad U_{H_l}\approx 0.
]

它加速局部收敛，但不改变最终能力。

### Delayed-useful

[
U_{H_s}\leq 0,\qquad U_{H_l}>0.
]

它短期看起来困难，却建立了后续可迁移能力。

### Reversal-harmful

[
U_{H_s}>0,\qquad U_{H_l}<0.
]

它是最重要的 curriculum false positive：短期 proxy 会奖励它，但长期造成 interference 或 forgetting。

---

# 6. Deployment objective 与 physical-quality gate

## 6.1 不再用一个 metric 同时当 teacher 和 judge

LUCID 的 latent gap可以作为 mechanism diagnostic，但不能成为唯一 utility outcome。你们的后续 evidence 已经显示某些 ability metrics 在 action/reward quality 恶化时仍可能改善。

近期 HumanTracker 也指出，常见 kinematic tracking metric 会遗漏 foot skating、support instability 和错误 contact timing，因此本项目的 final outcome 必须与训练 proxy 分离。

## 6.2 Primary efficacy outcome

冻结一个 development deployment suite (\mathcal D_{\mathrm{dev}})，定义：

[
J_{\mathrm{eff}}(\theta)
========================

\operatorname{MacroMean}_{f\in\mathcal F}
\operatorname{QSuccess}_f(\theta),
]

其中 (\mathcal F) 是 motion families 或 perturbation strata。

不使用所有 episode 的 micro average，因为大 family 会淹没小 family。

## 6.3 Quality-qualified success

Episode 只有满足以下条件才记为 quality success：

[
\operatorname{QSuccess}(\tau)
=============================

\mathbf 1
\left[
\begin{array}{l}
\text{motion completion},\
E_{\mathrm{mpjpe}}\leq \tau_p,\
E_{\mathrm{slip}}\leq \tau_s,\
E_{\mathrm{HF-action}}\leq \tau_h,\
E_{\mathrm{contact}}\leq \tau_c,\
E_{\mathrm{sat}}\leq \tau_\tau
\end{array}
\right].
]

Thresholds 在主 branch campaign 前冻结，来源依次为：

1. robot/simulator safety limit；
2. nominal SONIC rollout distribution；
3. hardware-safe pilot；
4. 若硬件 limit 不可获得，使用 baseline distribution 的预注册 quantile。

阈值不能按方法分别调节。

## 6.4 Independent quality outcomes

每次 eval 至少记录：

* success/completion；
* normalized progress；
* MPJPE-L 与 body-part MPJPE；
* reference–execution velocity error；
* reference–execution acceleration error；
* action first difference；
* action second difference；
* high-frequency action spectral energy；
* foot horizontal velocity during contact；
* foot slip distance；
* undesired-contact rate；
* contact impulse；
* joint-limit proximity；
* actuator torque saturation fraction；
* energy proxy；
* episode length；
* termination reason；
* recovery time where applicable。

SONIC 官方 evaluation 已经报告 success、MPJPE-L、velocity distance 和 acceleration distance；官方 reward config也包含 action-rate、joint-limit、undesired-contact、anti-shake 和 feet-acceleration penalties，因此上述物理指标不是另起一套无关的审美，而是将现有训练目标变成可独立审计的 outcome。

## 6.5 Constrained utility label

不把所有指标用任意权重加成一个难以解释的 scalar。

首先计算：

[
U_H^{\mathrm{eff}}(b)
=====================

\frac{
\Delta J_{\mathrm{eff},H}(b)
}{
\Delta D_H(b)+\varepsilon_D
}.
]

再定义 harm vector：

[
\mathbf h_H(b)
==============

[
\Delta J_{\mathrm{clean}},
\Delta E_{\mathrm{action}},
\Delta E_{\mathrm{slip}},
\Delta E_{\mathrm{contact}},
\Delta E_{\mathrm{sat}}
].
]

只有 clean noninferiority 和所有 harm gate 均通过时，context 才可被标为 safe-positive。

因此 utility dataset 中的 target 是：

1. efficacy regression target；
2. harm probability；
3. safe-positive / neutral / harmful 三分类。

这比让一个 scalar gap掩盖 action-quality regression 更稳健。

---

# 7. SONIC 代码集成设计

## 7.1 原则

研究代码放进独立 namespace，并尽量通过 narrow hooks 扩展 upstream SONIC。

建议目录：

```text
gear_sonic/
  research/
    practice_utility/
      __init__.py
      schema.py
      context_registry.py
      sampler_adapter.py
      intervention.py
      dose_accounting.py
      rng_capsule.py
      branch_capsule.py
      quality_metrics.py
      latent_gap_probe.py
      utility_label.py
      proxy_features.py
      estimator.py
      residual_allocator.py
      audit.py
      reports.py

  trl/
    callbacks/
      practice_context_callback.py
      practice_quality_eval_callback.py
      practice_manifest_callback.py

scripts/
  practice_utility/
    build_motion_pool.py
    create_probe_manifest.py
    snapshot_native_sampler.py
    run_branch.py
    evaluate_branch.py
    build_utility_labels.py
    run_proxy_audit.py
    train_utility_estimator.py
    run_residual_curriculum.py
    audit_campaign.py

tests/
  practice_utility/
    test_sampler_identity.py
    test_intervention_distribution.py
    test_exact_dose.py
    test_branch_capsule.py
    test_resume_equivalence.py
    test_distributed_sampling.py
    test_quality_metrics.py
    test_no_test_leakage.py
    test_latency_identity.py
```

## 7.2 Existing file extension map

| Existing component                                 | Minimal modification                                                                                     | Scientific purpose                                 |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| `gear_sonic/utils/motion_lib/motion_lib_base.py`   | Expose native probability snapshot、bin IDs、sampling override 和 exact counters                            | 将 intervention 施加在真实 SONIC sampler，而非旁路复制          |
| `gear_sonic/envs/wrapper/manager_env_wrapper.py`   | 把 context ID、motion/bin ID、actual env action、executed joint state 和 perturbation fingerprint 放入 `extras` | 建立 command–execution、dose 与 quality telemetry      |
| `gear_sonic/trl/callbacks/im_resample_callback.py` | 支持 `native / frozen_pool / residual` 三种模式                                                                | 允许 branch 阶段冻结 motion pool，并在正式训练恢复 native refresh |
| `gear_sonic/trl/callbacks/model_save_callback.py`  | 保存完整 branch capsule                                                                                      | 保证 paired continuation 的初始化可验证                     |
| `gear_sonic/trl/callbacks/im_eval_callback.py`     | 不直接破坏原 callback；派生 quality callback                                                                      | 保留官方指标，同时加入独立物理质量                                  |
| `gear_sonic/trl/trainer/ppo_trainer.py`            | 只加入 state/telemetry hook，不在 trainer 内 fork branches                                                      | 避免 nested training、optimizer 和 GPU state 复杂化       |
| `gear_sonic/config/`                               | 新增 research callback 与 experiment presets                                                                | 所有实验由 frozen Hydra config 驱动                       |
| `gear_sonic/envs/manager_env/mdp/events.py`        | 后期加入 context-conditioned event wrapper                                                                   | physics extension 时使用 deterministic severity cells |

官方代码文档已经把上述训练入口、wrapper、trainer、callbacks、motion library 和 MDP components 分离，因此这些 insertion points 与现有架构一致。

---

# 8. 核心数据结构与接口

## 8.1 ContextKey

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ContextKey:
    motion_key: str
    motion_hash: str
    bin_index: int
    bin_start_frame: int
    bin_end_frame: int
    perturbation_group: str = "native"
    severity_level: int = 0
    encoder_mode: str = "g1"
```

不只使用 integer motion ID，因为不同 loader order 可能改变 ID。Claim-bearing artifacts 必须以 stable motion hash 识别。

## 8.2 BranchCapsule

```python
@dataclass
class BranchCapsule:
    policy_state: dict
    value_state: dict
    optimizer_state: dict
    scheduler_state: dict
    trainer_state: dict
    env_state: dict
    native_sampler_state: dict

    python_rng_state: object
    numpy_rng_state: tuple
    torch_cpu_rng_state: object
    torch_cuda_rng_states: list
    context_rng_state: dict

    resolved_config_hash: str
    motion_pool_manifest_hash: str
    dev_suite_hash: str
    source_commit: str
    checkpoint_sha256: str
```

当前 `ModelSaveCallback` 的 checkpoint dictionary 没有显式 RNG state，因此这是第一项必须增加的基础设施。

## 8.3 SamplerAdapter

```python
class PracticeSamplerAdapter:
    def snapshot_native_distribution(self) -> SamplingSnapshot:
        ...

    def freeze_motion_pool(self, manifest: MotionPoolManifest) -> None:
        ...

    def set_intervention(
        self,
        context: ContextKey,
        epsilon: float,
        kernel_radius: int,
    ) -> None:
        ...

    def set_residual_distribution(
        self,
        probability: torch.Tensor,
        manifest_id: str,
    ) -> None:
        ...

    def clear_override(self) -> None:
        ...

    def get_exact_dose_report(self) -> DoseReport:
        ...
```

当 override 关闭时，所有调用必须落回现有 SONIC path。

## 8.4 UtilityRecord

```python
@dataclass
class UtilityRecord:
    branch_pair_id: str
    context: ContextKey
    policy_stage: str
    seed: int
    horizons: list[int]

    base_distribution_hash: str
    intervention_distribution_hash: str

    actual_control_dose: dict
    actual_intervention_dose: dict

    efficacy_delta: dict
    quality_delta: dict
    safe_positive: dict

    proxy_features: dict
    artifact_hashes: dict
```

所有训练结果必须能从这个 record 追溯到：

* source checkpoint；
* config；
* random streams；
* motion pool；
* exact dose；
* evaluation suite；
* generated reports。

---

# 9. Branch reproducibility 与 common-random-number design

## 9.1 为什么普通 seed 不够

即使 control 与 intervention 都设为 `seed=0`，一旦它们抽到不同 motion bins，后续 global RNG consumption 就会分叉，导致：

* push timing 不同；
* physics parameters 不同；
* policy action sampling 不同；
* minibatch shuffle 不同；
* dropout 或 auxiliary sampling 不同。

此时 branch difference 同时包含 intervention effect 和随机轨迹 divergence。

## 9.2 Counter-based randomness

对非 context-selection 的随机 channel 使用 keyed generator：

[
\xi=
f(
\text{pair_id},
\text{env_id},
\text{episode_index},
\text{channel_name}
).
]

例如：

```text
(pair_003, env_017, episode_009, friction)
(pair_003, env_017, episode_009, push_time)
(pair_003, env_017, episode_009, action_noise)
```

Control 与 intervention 在相同 key 上获得同一随机值；只有 context selector 不同。

完全 bitwise matching 在 GPU physics 中未必能够保证，因此我们要求：

1. deterministic configuration 尽可能开启；
2. RNG receipts 完整保存；
3. (\epsilon=0) branch 做 empirical equivalence；
4. 使用 paired replicates 估计 residual branch noise；
5. 不把 “same seed” 写成 “identical trajectory”。

## 9.3 Frozen motion pool

Oracle branch 中暂时关闭周期性 motion-library reloading：

* 所有 branch 加载同一个 fixed motion pool；
* native sampler 只在固定 pool 内分配 bins；
* control 与 intervention 的 available support 完全相同；
* 不让 global loader selection 成为另一个处理变量。

正式 residual-training 阶段再恢复 SONIC 原生 motion-resample cycle。

---

# 10. 数据与 split 设计

## 10.1 Debug pool

使用公开、处理完成的 BONES-SEED subset：

* 512 distinct motion trajectories；
* 尽量覆盖至少 8 类 motion families；
* 每个 family 至少 40–64 clips；
* 去除 exact duplicates；
* 根据 reference trajectory hash 去除不同文件名但相同 motion；
* 不以视频、camera view 或 render 数量计算多样性。

官方仓库支持从 released checkpoint 在 BONES-SEED 上继续训练，而不是要求从头复现 128-GPU full-scale training。

Debug pool 仅验证：

* code correctness；
* branch variance；
* dose signal；
* runtime；
* no-op parity。

不能用于最终 zero-shot novelty claim。

## 10.2 Claim-bearing split

至少建立：

### Adaptation pool

用于 SONIC continued training 和 utility intervention。

### Development deployment suite

用于 utility label：

[
U_H(x)
======

## J_{\mathcal D_{\mathrm{dev}}}(\theta^x)

J_{\mathcal D_{\mathrm{dev}}}(\theta^0).
]

### Final untouched test suite

只在方法与 hyperparameters 冻结后开启。

Split 必须在以下层级去重：

* source sequence；
* trajectory hash；
* performer/subject where metadata exists；
* motion family；
* near-duplicate trajectory similarity。

SONIC 原论文将 test-content 与 test-repetition 分开：前者是完全未见 motion content，后者是已见类别的新表演。这种区分应继续保留，而不能把两者混成一个 OOD 数字。

## 10.3 Encoder mode isolation

SONIC 的统一 controller 支持 G1、SMPL 和 VR input；不同 encoder 在同一 token space 中共享 decoder。

Core oracle 先固定：

```text
encoder_mode = g1
```

否则一个 context 的训练价值可能同时受：

* motion bin；
* encoder selection；
* tokenizer reconstruction；
* cross-modal latent alignment；

共同影响。

Motion-level result成立后，再评估：

1. G1-bin utility 是否 transfer 到 SMPL encoder；
2. SMPL-context utility 是否改善 VR control；
3. utility ranking 是否跨 interface 稳定。

---

# 11. Proxy instrumentation

每个 candidate context 在 branch 前记录以下 proxy。

## 11.1 Native SONIC proxies

* raw failure count；
* episode count；
* posterior-smoothed failure rate；
* native sampling probability；
* bin weight；
* per-motion total probability；
* staleness；
* recent progress；
* recent MPJPE；
* termination-type distribution。

## 11.2 RL proxies

* mean advantage；
* absolute advantage；
* value loss；
* TD residual；
* policy entropy；
* KL；
* gradient norm；
* PPO clipping fraction；
* actor/critic loss；
* local gradient alignment estimate。

PLR 将 TD error 作为 future learning potential 的 proxy，因此 PLR-style priority 是必须比较的强 baseline，而不是可忽略的 unrelated RL method。

## 11.3 LUCID proxies

从 SONIC 中记录：

* (q_t^{cmd})：送入 actuator/PD 的 target joint position；
* (q_t^{exec})：实际 joint position；
* fixed-length command/execution windows；
* raw mismatch；
* frozen LUCID encoder latent gap；
* median、p90、slope、variance；
* contact-conditioned latent gap。

LUCID gap只作为 predictor 与 mechanism diagnostic，不参与第一阶段 SONIC training。

## 11.4 Motion-structure features

从 reference motion 离线计算：

* root linear/angular speed；
* joint velocity and acceleration；
* vertical COM excursion；
* contact transition count；
* single-support fraction；
* flight-phase fraction；
* hand–foot coordination；
* reference jerk；
* spectral complexity；
* motion duration；
* transition-to-bin difficulty；
* neighboring-bin failure context。

这些 feature 用于判断两个 failure rate 相同的 bins 是否因为 physics structure 不同而具有不同 utility。

---

# 12. Quality evaluator 实现

现有 `ImEvalCallback` 已经保存 termination、progress、MPJPE 和 per-motion outputs，但根据当前代码检查，并未形成完整的 action/contact/torque/slip aggregation；因此新增 subclass，而不是修改官方 callback 的语义。

## 12.1 Action metrics

[
E_{\Delta a}
============

\frac1T
\sum_t
|a_t-a_{t-1}|_2^2
]

[
E_{\Delta^2a}
=============

\frac1T
\sum_t
|a_t-2a_{t-1}+a_{t-2}|_2^2.
]

High-frequency energy：

[
E_{\mathrm{HF}}
===============

\sum_{f\ge f_c}
|\mathcal F(a)_f|^2.
]

报告：

* all joints；
* legs；
* ankles；
* wrists；
* torso；
* maximum-joint tail。

## 12.2 Foot slip

在 foot-contact mask (c_{t,f}=1) 时：

[
E_{\mathrm{slip}}
=================

\sum_{t,f}
c_{t,f}
|
v_{t,f}^{xy}
|
\Delta t.
]

同时报告：

* slip per meter traveled；
* max continuous slip；
* touchdown slip；
* stance-phase slip。

## 12.3 Contact quality

记录：

* non-foot contact rate；
* peak contact impulse；
* impulse integral；
* mistimed contact relative to reference；
* left/right asymmetry；
* contact transition timing error。

## 12.4 Actuator quality

若 simulator 可提供 applied torque 与 actuator limits：

[
r_{\mathrm{sat}}
================

\frac{
#{t,j:|\tau_{t,j}|\ge 0.95\tau_j^{max}}
}{
T|\mathcal J|
}.
]

另记录：

* peak torque ratio；
* RMS torque；
* mechanical-power proxy；
* thermal-risk proxy where justified；
* joint-limit proximity。

不能把 reward term 数值直接当作唯一 physical outcome；reward 可作为辅助 telemetry，但 final evaluator 应从 simulator state/action 重新计算。

---

# 13. Killer Experiment：Difficulty–Utility Phase Portrait

这是整个 proposal 的最高信息量实验。它必须先于 estimator 和 sampler。

## 13.1 Policy stages

从一次 controlled adaptation run 中选择三类 checkpoint：

* **Early:** 刚开始适应 target pool；
* **Middle:** overall performance 明显提升但尚未 plateau；
* **Late:** performance 接近稳定。

不按事后最好看的 iteration 选择。用预先规定的 overall progress thresholds 选取。

Released SONIC checkpoint可作为 adaptation initialization；考虑到官方 full-scale training 推荐 64+ GPUs，本项目不从头训练 SONIC foundation model，而围绕 released checkpoint 做 controlled fine-tuning。

## 13.2 Context selection

每个 stage 选择 24 bins，预先按以下维度分层：

* native failure-rate quartile；
* motion family；
* contact-rich vs contact-light；
* low vs high reference dynamics；
* high vs low current sampling probability；
* no obvious corrupted reference。

不能只挑最困难 bins，因为那会把 proposal 偷偷变成 hard-example study。

## 13.3 Screening campaign

对于每个 stage：

* 1 个 shared control branch / seed；
* 24 intervention branches；
* 2 screening seeds；
* (\epsilon=0.10)；
* nested horizons (H_s,H_m,H_l)；
* common evaluation suite；
* exact dose accounting。

Shared control用于低成本筛查，但不能作为最终 confirmatory evidence。

## 13.4 Confirmation campaign

根据预先定义而非仅看 effect size 的规则，选择：

* 6 个 suspected difficulty–utility reversal contexts；
* 3 个 positive monotonic controls；
* 3 个 negative controls。

使用：

* 4 fresh seeds；
* 每个 intervention 配独立 paired control；
* untouched branch capsules；
* frozen analysis script。

## 13.5 Primary figure

横轴：

[
\text{native SONIC failure rate}
]

纵轴：

[
U_{H_l}^{\mathrm{eff}}.
]

颜色：

[
\text{motion family}.
]

形状：

[
\text{contact regime}.
]

箭头：

[
U_{H_s}
\rightarrow
U_{H_l}.
]

补充 panels：

* latent gap vs (U_{H_l})；
* MPJPE vs (U_{H_l})；
* TD error vs (U_{H_l})；
* learning progress vs (U_{H_l})。

## 13.6 Gate A：Utility identifiability

继续 estimator development 前，需要满足：

1. utility label 的 seed-level reliability 达到预注册标准；
2. between-context variance 明显大于 paired branch noise；
3. actual extra dose 为正且不被 termination 完全吞掉；
4. (\epsilon=0) branch 与 control 在容许范围内等价；
5. 至少一个 horizon 的 signal 可复现。

若不满足，停止 context-level method。

## 13.7 Gate B：Proxy insufficiency

下面任一条件成立，才允许进入 learned estimator：

* native failure 对 long-horizon utility ranking 明显不稳定；
* 在 matched failure quantile 内出现 fresh-seed-confirmed opposite-sign utilities；
* short- and long-horizon utility 存在系统 reversal；
* latent gap、TD error 和 learning progress 均无法达到预注册 calibration；
* multi-feature simple model在 leave-one-family-out 上明显优于最佳单 proxy。

如果 native failure 或 latent gap 已经充分，停止 neural estimator。

---

# 14. Utility estimator

## 14.1 模型顺序

严格按复杂度顺序：

1. constant predictor；
2. native-failure monotonic model；
3. isotonic regression；
4. ridge/elastic-net；
5. gradient-boosted trees；
6. small MLP；
7. 只有在明确发现 temporal representation bottleneck 后，才考虑 sequence model。

不直接使用 Transformer。

## 14.2 输出

Estimator 输出：

[
\hat U_{H_s},\hat U_{H_m},\hat U_{H_l},
]

以及：

[
\hat p_{\mathrm{harm}}.
]

使用 ensemble 或 bootstrap 得到 uncertainty：

[
\sigma_U(x).
]

在线分配使用 conservative score：

[
s(x)
====

## \hat U_{H_l}(x)

\beta\sigma_U(x).
]

若：

[
\hat p_{\mathrm{harm}}(x)>\delta,
]

则该 context 不获得正 residual weight。

## 14.3 Cross-validation

至少执行：

* leave-one-motion-family-out；
* leave-one-policy-stage-out；
* leave-one-source-dataset-out；
* later: leave-one-perturbation-group-out；
* fresh-seed confirmation。

不能随机打散所有 rows 后报告一个容易的 train/test split，因为相邻 bins 和同一 motion clip 高度相关。

## 14.4 Metrics

* Spearman rank correlation；
* pairwise ranking accuracy；
* utility-sign accuracy；
* calibration error；
* negative log likelihood where probabilistic；
* harm AUROC/AUPRC；
* long-horizon regret；
* top-k selected-context true utility；
* family-level worst-case performance。

---

# 15. Identity-Preserving Residual Sampler

## 15.1 Target distribution

保留 SONIC native distribution：

[
\rho_k(b).
]

Utility target：

[
\tilde q_k(b)
=============

\frac{
\rho_k(b)
\exp(s_k(b)/\tau)
}{
Z_k
}.
]

最终 sampler：

[
q_k(b)
======

(1-\alpha_k)\rho_k(b)
+
\alpha_k\tilde q_k(b).
]

## 15.2 Identity point

当：

[
\alpha_k=0,
]

或者所有 utility score 相同，则：

[
q_k=\rho_k.
]

这意味着新方法失败时可以精确退回原 SONIC，而不是要求新 teacher 从零生成整个 curriculum。

## 15.3 Safety and coverage constraints

强制：

[
D_{\mathrm{KL}}(q_k|\rho_k)
\leq
\varepsilon_{\mathrm{KL}}.
]

同时：

* per-bin probability 不超过 native cap 的预注册倍数；
* per-motion aggregate probability 有上限；
* 每个 motion family 保留 minimum coverage；
* unseen/rare families 保留 exploration floor；
* harmful contexts 不被完全删除，而保留小诊断概率；
* residual 不改变 available motion support。

初始 dev grid：

[
\alpha\in{0.10,0.25},
\qquad
\varepsilon_{\mathrm{KL}}\in{0.02,0.05}.
]

主实验前冻结一个 setting。

## 15.4 Refresh cadence

现有 `im_resample` callback 周期性调用 motion resampling。Residual distribution 应在相同 integration point 应用，但 utility estimator 不必每次重新训练。

建议：

* 每次 native resample event：重新计算当前 pool 上的 score 和 constrained distribution；
* 每隔更长周期：更新 estimator checkpoint；
* estimator update 与 policy update 异步记录版本；
* 每个 rollout 都记录使用的 estimator hash 和 distribution hash。

---

# 16. 必须包含的 controls

## 16.1 Native SONIC

原生 failure-based sampler。

## 16.2 Uniform

在相同 frozen motion support 上均匀采样。

## 16.3 Failure-calibrated residual

使用 native failure score，但匹配 utility sampler 的：

* (\alpha)；
* KL；
* entropy；
* coverage floor。

这用于判断 gain 是来自 residual shape，还是 utility information。

## 16.4 Random residual

随机 score，但匹配 distribution shift magnitude。

## 16.5 MPJPE/error sampler

根据 tracking error 重分配。

## 16.6 Absolute learning progress

根据近期 performance difference 分配。

## 16.7 PLR-style sampler

根据 value loss/TD residual 分配。

## 16.8 LUCID mismatch sampler

使用 frozen latent command–execution gap，采用相同 residual shell。

## 16.9 Utility residual

主方法。

## 16.10 Oracle

只在小 context pool 上使用 measured (U_H) 直接分配，作为 upper diagnostic bound，不作为可部署方法。

## 16.11 Yoked schedule

从 seed A 记录 utility residual schedule：

[
q^{A}_1,q^{A}_2,\ldots
]

在 seed B 上 replay，不允许 B 的实时状态影响 schedule。

若 online utility 与 yoked replay 同样好，gain 可能来自 schedule shape 或 dose，而非 policy-specific feedback。这个 control 延续了 LUCID reroute 中已经提出的 cross-seed schedule-swap 逻辑。

---

# 17. Equal-compute full experiment

所有方法共享：

* initialization distribution；
* released checkpoint；
* motion pool；
* policy/value architecture；
* PPO budget；
* environment interactions；
* optimizer settings；
* encoder mode；
* reward；
* termination；
* DR support；
* eval episode seeds；
* final checkpoint-selection rule；
* wall-clock accounting；
* tuning budget。

报告两类结果：

## Learning efficiency

* performance vs environment interactions；
* performance vs PPO updates；
* performance vs GPU hours；
* learning-curve AUC；
* time to threshold。

## Final capability

* sufficiently trained final outcome；
* test-content；
* test-repetition；
* external data source；
* worst motion family；
* held-out contact regime；
* clean performance；
* perturbation severity AUC。

如果 fixed/native method 在充分训练后追平，不能把 AUC gain 写成 better final robustness。

---

# 18. Physics-context extension

Motion-only method通过后，再增加 factorized context。

## 18.1 Context groups

[
g\in
{
\text{material},
\text{mass/CoM},
\text{push},
\text{reference noise},
\text{latency}
}.
]

每个 group 先单独定义四个 severity cells：

[
s\in{0,1,2,3}.
]

不直接构造全部 Cartesian product。

## 18.2 Branch-level first

当前部分 events 是 startup-mode。为避免先修改 per-env physics backend，第一轮 physics oracle 使用 branch-level config：

* control branch 使用 nominal/base distribution；
* intervention branch增加某 group/severity exposure；
* 每个 process 的 physics config固定且可审计。

只有 branch-level effect 成立后，才实现 reset-conditioned per-env context event。

## 18.3 Held-out composition

训练只看到 single groups 与部分 pairs。

Final test 包括未见组合，例如：

* low friction × payload increase；
* CoM shift × push；
* reference jitter × mass variation；
* latency × low friction；
* latency × dynamic single-support motion。

关键结果不是在训练 ranges 内随机再采一批，而是：

[
\text{unseen composition generalization}.
]

## 18.4 Motion–physics interaction

比较：

[
U_H(b,g,s)
]

与 additive approximation：

[
U_H(b)+U_H(g,s).
]

若二者差异明显，说明某些 motion 的 training value 取决于特定 physical mismatch，而不是 motion difficulty 或 physics severity 单独决定。

---

# 19. Sim-to-sim 与 hardware gate

## 19.1 MuJoCo gate

在任何 Unitree G1 hardware experiment 前：

* export frozen policy；
* 使用 repo MuJoCo bridge；
* 验证 observation/action convention；
* 检查 Isaac–MuJoCo clean parity；
* 报告 motion-family macro outcomes；
* 报告 latency、contact、slip 与 torque metrics。

只有：

* clean noninferiority；
* sim-to-sim robustness improvement；
* no action/contact damage；
* no catastrophic family regression；

同时成立，才进入 hardware。

## 19.2 Hardware protocol

不重复原 LUCID 稿件仅 5 motions × 3 trials 的小规模 protocol。该稿件确实以 15 trials 汇报 hardware success，因此新的 claim-bearing study 需要更强的 uncertainty accounting。

建议：

* 20–30 motions；
* 至少 5 repetitions / motion where safe；
* 分层覆盖 locomotion、squat/kneel、upper-body dynamic、contact-rich 与 transition motions；
* method order randomized；
* battery/temperature/robot state 记录；
* safety stop 作为 failure；
* motion 为 statistical cluster，而非把 trial 当完全独立样本；
* Wilson interval 与 hierarchical bootstrap；
* paired motion-level comparison。

Hardware 不用于 utility estimator training，只用于最终外部验证。

---

# 20. Statistical analysis

## 20.1 Oracle utility

对每个 context 使用 paired effect：

[
\Delta J_{b,s}
==============

## J(\theta^{b}_{s})

J(\theta^{0}_{s}).
]

报告：

* paired mean；
* median；
* bootstrap interval；
* sign consistency；
* seed × context variance decomposition；
* intraclass correlation。

## 20.2 Difficulty–utility relation

报告：

* Spearman correlation；
* isotonic calibration；
* pairwise ranking；
* conditional relation within failure quantiles；
* partial relation controlling motion family 和 policy stage；
* reversal count；
* fresh-seed reversal confirmation。

## 20.3 Main method

Primary hypothesis：

[
\Delta
======

## J_{\mathrm{eff}}(\text{utility residual})

J_{\mathrm{eff}}(\text{native SONIC}).
]

Promotion requires：

* positive paired lower 95% interval for primary effect；
* clean noninferiority；
* no catastrophic hard-stratum regression；
* mechanism active；
* fresh-seed confirmation；
* pre-registered multiplicity treatment。

这与当前 LUCID reroute 已经确立的 claim discipline 一致。

## 20.4 Multiple context discovery

Screening contexts 可使用 FDR control，但 final paper claim 不能只基于被选中的 top contexts。

Confirmation 必须使用：

* fresh seeds；
* frozen context set；
* frozen analysis；
* independent control branches。

---

# 21. Test plan

## Unit tests

### Sampler

* probabilities nonnegative；
* sum to one；
* (\epsilon=0) identity；
* constant utility identity；
* exact KL；
* coverage floor；
* per-motion cap；
* deterministic context selection；
* kernel boundary correctness。

### Dose

* intended vs actual dose；
* termination-adjusted dose；
* distributed aggregation；
* no double counting；
* exact motion hash mapping。

### Metrics

* stationary foot yields zero slip；
* known sliding trajectory yields expected slip；
* sinusoidal actions produce known spectral peak；
* torque at limit yields saturation ratio one；
* early termination fills fixed horizon consistently。

## Integration tests

### No-op parity

Run native SONIC and research-enabled SONIC with all interventions disabled：

* same checkpoint；
* same config；
* same motion pool；
* same seeds；
* compare trajectories、rewards、terminations、sampling probabilities。

### Resume equivalence

Compare：

```text
20 iterations uninterrupted
```

against：

```text
10 iterations
save branch capsule
resume
10 iterations
```

报告 policy weights、optimizer state、sampler state、metrics 与 trajectory tolerance。

### Distributed sampler

验证 multi-GPU：

* failure counts sync；
* residual probabilities一致；
* dose reports可重构；
* motion hashes不因 rank 改变；
* global coverage正确。

### Branch identity

Control vs intervention with：

[
\epsilon=0.
]

其 effect distribution 用于估计 branch noise floor。

### Latency identity

FIFO delay (d=0) 与原 action path 等价；(d=1) 必须精确表现为一个 20 ms control-step shift。

### Leakage test

Final test manifest 的 hash 不得出现于：

* utility-label builder；
* estimator training；
* hyperparameter selection；
* development reports。

---

# 22. Config design

建议新增：

```text
gear_sonic/config/
  callbacks/
    practice_context.yaml
    practice_quality_eval.yaml
    practice_manifest.yaml

  research/
    practice_utility/
      base.yaml
      oracle_screen.yaml
      oracle_confirm.yaml
      residual_train.yaml
      physics_extension.yaml

  exp/manager/universal_token/all_modes/
    sonic_practice_audit.yaml
    sonic_practice_residual.yaml
```

示例：

```yaml
practice_utility:
  enabled: true
  mode: oracle_control

  source_commit: c374bae5b9039cd0ee71377e654d11ce1bc69e1d
  encoder_mode: g1

  motion_pool:
    frozen: true
    manifest: manifests/debug_pool_512.json
    disable_periodic_reload: true

  intervention:
    enabled: false
    epsilon: 0.10
    kernel_radius_bins: 1

  branch:
    pair_id: null
    capsule_path: null
    save_rng: true
    counter_rng: true

  dose:
    record_per_bin: true
    record_per_motion: true
    record_completed_steps: true

  quality_eval:
    suite: manifests/dev_suite.json
    fixed_horizon: true
    record_action_spectrum: true
    record_contact_metrics: true
    record_torque_metrics: true

  final_test:
    accessible: false
```

这里的 commit SHA 是本次代码审计所对应的 upstream tree reference；正式开工时应在 fork 中生成 immutable tag，不应长期追随 moving `main`。

---

# 23. Planned command interface

以下是要实现的 research interface，不是当前 upstream 已存在的命令。

## Baseline reproduction

```bash
python gear_sonic/eval_agent_trl.py \
  +checkpoint=sonic_release/last.pt \
  +headless=true \
  +run_once=true
```

## Build fixed pool

```bash
python scripts/practice_utility/build_motion_pool.py \
  --motion-dir data/motion_lib_bones_seed/robot_filtered \
  --num-motions 512 \
  --deduplicate \
  --output manifests/debug_pool_512.json
```

## Create probe campaign

```bash
python scripts/practice_utility/create_probe_manifest.py \
  --checkpoint-manifest manifests/policy_stages.json \
  --motion-pool manifests/debug_pool_512.json \
  --contexts-per-stage 24 \
  --epsilon 0.10 \
  --kernel-radius 1 \
  --horizons 8 32 128 \
  --seeds 0 1 \
  --output manifests/oracle_screen.json
```

## Run one branch

```bash
accelerate launch --num_processes=8 \
  scripts/practice_utility/run_branch.py \
  +exp=manager/universal_token/all_modes/sonic_practice_audit \
  practice_utility.branch_manifest=manifests/oracle_screen.json \
  practice_utility.branch_id=stage_mid_ctx_017_seed_0_intervention
```

## Build labels

```bash
python scripts/practice_utility/build_utility_labels.py \
  --campaign artifacts/oracle_screen \
  --dev-suite manifests/dev_suite.json \
  --output artifacts/utility_labels_v1.parquet
```

## Proxy audit

```bash
python scripts/practice_utility/run_proxy_audit.py \
  --labels artifacts/utility_labels_v1.parquet \
  --group-by motion_family policy_stage \
  --output artifacts/proxy_audit_v1
```

只有 proxy audit 的 Gate A/B 通过后，下面的 estimator 和 residual commands 才获得 training authorization。

---

# 24. Compute plan

## 24.1 不从头重训 foundation model

SONIC 官方 full-scale result依赖 128 GPUs 与大规模训练；当前官方 finetuning guide也明确建议大规模 GPU，虽然提供了 8-process launch example。

本项目采用：

* released checkpoint initialization；
* fixed adaptation pool；
* smaller parallel environment count for instrumentation；
* full environment count only for claim-bearing confirmation；
* shared control branches用于 screening；
* independent paired controls用于 confirmation。

## 24.2 Campaign cost reduction

### Shared control

同一 checkpoint/seed 的 24 个 screening contexts 共用一个 control continuation。

### Nested horizon

一个 branch 在 (H_s,H_m,H_l) 保存 checkpoints，不运行三次。

### Two-stage context count

24-context screening 后，只确认 12 contexts。

### Estimator gate

如果 simple proxy 足够，不运行 full residual campaign。

### Hardware gate

没有 sim-to-sim positive evidence，不消耗 hardware budget。

---

# 25. Milestone plan

## Week 1：Upstream lock 与 baseline

完成：

* fork/tag inspected SONIC commit；
* install/test；
* released checkpoint evaluation；
* frozen config；
* motion-data hashes；
* throughput profile；
* baseline report。

Exit gate：

* baseline可复现；
* no unresolved action/observation mismatch；
* evaluation script稳定；
* exact source receipt存在。

## Week 2：Branch capsule 与 no-op parity

完成：

* full RNG capture；
* sampler state；
* fixed motion pool；
* dose counters；
* resume-equivalence test；
* (\epsilon=0) identity test。

Exit gate：

* research hooks关闭时不改变 SONIC；
* branch variance可估计；
* checkpoint resume可信。

## Week 3：Quality evaluator 与 proxy map

完成：

* action/contact/slip/torque metrics；
* LUCID diagnostic probe；
* 3 policy-stage selection；
* 24-context manifest；
* no-training metric audit。

Exit gate：

* physical metrics可解释；
* bad-quality rows不会因单一 latent improvement被标为 positive；
* final test inaccessible。

## Weeks 4–5：Oracle screening

完成：

* paired branch campaign；
* exact dose audit；
* multi-horizon labels；
* phase portrait；
* label reliability。

Exit gate：

* Gate A: utility identifiable；
* Gate B: simple proxies不充分。

## Week 6：Scientific decision

只能选择以下之一：

### Decision A：Stop at simple signal

Difficulty proxy 已充分。写 calibration/measurement result，不训练 scheduler。

### Decision B：Measurement paper

Utility 可辨识，但预测模型不泛化。完成 benchmark 和 causal analysis。

### Decision C：Residual method authorized

Utility 可辨识，proxy 不充分，estimator 有 held-out predictive value。进入 residual sampler。

## Weeks 7–10：Residual training

* simple estimator；
* uncertainty；
* native/random/failure-calibrated/yoked controls；
* equal-compute comparison；
* final simulation suite。

## Weeks 11–14：Physics extension

* single perturbation groups；
* severity cells；
* unseen compositions；
* optional latency FIFO；
* MuJoCo transfer。

## Final stage：Hardware

只在所有 simulation gate 通过后执行。

---

# 26. Paper claim ladder

## Claim Level 0：Infrastructure

> We built a reproducible counterfactual branch protocol.

这不是主要论文贡献。

## Claim Level 1：Measurement

> Current motion difficulty is not a sufficient predictor of long-horizon practice utility in SONIC.

需要 fresh-seed-confirmed reversals。

## Claim Level 2：Estimator

> Practice utility can be predicted across held-out motion families and policy stages.

需要 leave-one-family/stage evaluation。

## Claim Level 3：Method

> An identity-preserving utility residual improves equal-compute adaptation over SONIC’s native failure sampler.

需要 native、random、difficulty-calibrated、yoked controls。

## Claim Level 4：Generalization

> The improvement transfers to unseen motion content and unseen perturbation compositions.

需要 frozen final test。

## Claim Level 5：Sim-to-real

> Utility-guided practice improves physical G1 execution without sacrificing clean control quality.

需要 MuJoCo gate、hardware confidence intervals 与 independent quality metrics。

不能用 Level 1 证据写 Level 5 abstract。

---

# 27. 可能结果与诚实转向

## Outcome A：Failure is already utility

Native failure sampler充分预测 (U_{H_l})。

结论：

> SONIC’s simple failure-based curriculum is better justified than previously known.

停止 estimator。

## Outcome B：Latent gap比 failure 更好

LUCID gap稳定预测 long-horizon utility。

结论：

> latent command–execution mismatch is valuable as a practice-allocation signal, even if scalar global DR control was too blunt.

这会为 LUCID 找到一个比 global (\lambda) 更合适的作用位置。

## Outcome C：Utility exists but cannot be predicted

Oracle labels稳定，但现有 features 无法跨 family generalize。

结论：

> training value is context-dependent and measurable, but current representations do not capture it.

下一篇转向 clean-feasibility 或 physics-aware representation，而不是硬上 online sampler。

## Outcome D：Acceleration only

Residual sampler提高 AUC，native SONIC 最终追平。

结论限定为 compute efficiency。

## Outcome E：Success提高但 physical quality恶化

结论转为 measurement failure：

> conventional success-based curricula can reward unsafe control artifacts.

这与当前 LUCID bad-quality metric evidence 和新的人类对齐 tracking benchmark相呼应。

## Outcome F：Strong positive

Difficulty 与 utility系统错位；utility estimator可泛化；residual sampler提高 AUC、final OOD、worst-family 与 sim-to-real quality。

此时形成完整方法论文：

> **Practice What Transfers: Counterfactual Utility for Generalist Humanoid Control.**

---

# 28. 第一项必须执行的实验

## Experiment P0 — SONIC Native Difficulty–Utility Audit

### Purpose

只回答一个问题：

[
\boxed{
\text{SONIC failure rate 是否预测 long-horizon practice utility？}
}
]

### Treatment

* released SONIC checkpoint continued on fixed adaptation pool；
* G1 encoder only；
* native DR unchanged；
* 3 policy stages；
* 24 bins/stage；
* stratified by failure quartile、motion family 和 contact structure；
* (\epsilon=0.10) local intervention；
* 2 screening seeds；
* nested short/medium/long horizons；
* quality-qualified dev evaluation；
* exact dose；
* no estimator；
* no residual online scheduler；
* no new physics；
* no hardware。

### Exact claim supported or refuted

> Current failure-based motion difficulty is an insufficient surrogate for the marginal value of practice in generalist humanoid tracking.

如果这个实验没有给出可靠答案，后面任何复杂 method 都不应启动。

---

# 29. 最终 thesis

SONIC 证明了 motion tracking 可以通过数据、模型和计算扩展成 generalist humanoid foundation controller。下一步不应只是继续扩展训练量，还要理解有限训练预算应当放在哪里。

本研究提出：

[
\text{difficulty}
\neq
\text{practice utility}.
]

Difficulty 描述机器人当前在哪里失败；practice utility 描述在某处增加训练经验后，未来部署能力如何改变。

通过 paired counterfactual continuation，我们首先测量两者是否真的不同；只有在证据支持时，才在 SONIC 原生 sampler 周围学习一个受限、可退回、quality-governed 的 residual allocation。

研究最终要回答的不是：

> Which motions are hard?

而是：

> **Which practice experiences make a generalist humanoid controller genuinely better?**
