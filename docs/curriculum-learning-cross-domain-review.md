# 跨领域文献综述：智能体的课程学习（Curriculum Learning）——为何"由易到难"常常打不过"混合难度"，以及如何真正评估能力

(Saved 2026-08-27 from user-provided document. English gist and SONIC mapping in
`~/lucid/fable.md` §B.)

## TL;DR（三条核心结论）
- **由易到难课程打不过混合训练，是可预期的常态而非异常**：只有当奖励稀疏、存在探索瓶颈、目标任务在均匀采样下几乎学不动时，课程才有稳定优势；当奖励密集、目标分布本身可学时，均匀/混合采样通常与课程持平甚至更好（Narvekar et al. 2020, JMLR；Klink et al. 自步 RL；LLM 侧 "Rethinking Easy-to-Hard" 2026 的负结果）。你的 PPO 机器人实验落在"密集奖励、目标可学"象限，因此混合训练不落下风完全合理。
- **真正有效的课程共有一组跨领域一致的设计原则**：扩张分布而非替换分布（OpenAI ADR、Rudin terrain "通关回环"）、按学习进度/后悔值采样而非按难度采样（PLR、ACCEL、ALP-GMM、AdaRFT）、回放已掌握任务防遗忘、任务/难度条件化、在完整目标混合上收尾、蒸馏做知识巩固、逐任务奖励归一化（PopArt），以及缓解可塑性丧失（continual backprop、reset）。
- **"能力"必须用分层留出评估来衡量**：按难度分箱的留出（held-out）成功率、最差箱（worst-bin）与 IQM 聚合＋自助法置信区间、≥5 个种子、对齐环境步数预算、训练过程中的保持率曲线（retention curve）、超出训练最大难度的 OOD 外推箱；LLM 侧还须报告 pass@k（大 k）与去污染留出基准。

---

## Key Findings（关键发现）

1. **课程 vs. 均匀采样的条件性**：Kanitscheider et al. 2021（Minecraft 多任务课程）给出了最清晰的理论直觉——课程只在"任务链互相依赖、掌握 T_i 才能学 T_{i+1}、且均匀采样下可学任务占比只有 1/N"时才有数量级的样本效率优势；否则均匀采样并不吃亏。
2. **on-policy（PPO）确实会遗忘，但相对 SFT 遗忘更少**："RL's Razor"（2025）与"Retaining by Doing"（2025）表明遗忘量由"新任务上相对基线策略的 KL 位移"决定，on-policy 天然偏向 KL 最小解，因此比 SFT 遗忘少；但"RL Forgets!"（2026，MRCL 基准）反证连续 RL 后训练仍会严重遗忘。
3. **顶级机器人工作从不"替换"分布，而是始终在并行环境中保留全部难度**：Rudin et al. 2022 的 terrain 课程通过晋级/降级并把"通关最高级的机器人随机回环到任意难度"来显式避免灾难性遗忘；OpenAI ADR 是"扩张随机化区间"；Lee et al. 2020 用粒子滤波维持"可通过但有挑战"的地形分布。
4. **LLM 推理 RL 的课程多为负结果或仅提效**：多项研究发现由易到难排序对最终能力"无稳定收益"；Yue et al. 2025（NeurIPS'25，Best Paper Runner-Up）用 pass@k 证明 RLVR 主要是"提高采样效率"而非扩展基座模型的推理边界，且在大 k 时基座反而超越 RL 模型。
5. **评估协议是本问题的核心**：Agarwal et al. 2021（rliable）与 Kirk et al. 2023（ZSG 综述）共同确立了"留出关卡/种子 + IQM + 自助置信区间 + 性能剖面"的评估范式。

---

## Details（分领域详述）

### A. 深度强化学习 / ML 理论与实践

#### A.1 课程何时有用、何时有害

- **Bengio, Louradour, Collobert, Weston 2009（ICML，"Curriculum Learning"）** 是课程学习的奠基论文，把课程视为一种延续法（continuation method），主张从平滑/简单样本开始有助于找到更好的盆地。但它同时指出课程的收益高度依赖任务与难度度量的选择。
- **Narvekar, Peng, Leonetti, Sinapov, Taylor, Stone 2020（JMLR 21(181):1–50）** 是 RL 课程的权威综述，提出统一框架（task generation / sequencing / transfer），并明确列出开放问题：大多数课程是手工设计、难度度量难定义、以及"课程能否真正超过直接训练"缺乏系统证据。
- **Portelas, Colas, Weng, Hofmann, Oudeyer 2020/2021（ACL 短综述，IJCAI）** 把自动课程学习归纳为按"学习进度"驱动的任务采样，核心是采样"处于最近发展区（ZPD）"的任务。
- **关键的条件性证据**：Kanitscheider et al. 2021 给出了课程优于均匀采样的精确条件——任务链互相依赖且均匀采样下只有 1/N 的 rollout 落在可学任务上。PPAAS（2025）也明确指出："采用密集奖励时，分配困难目标不会像稀疏奖励场景那样严重损害学习。"
- **负结果**："Rethinking Easy-to-Hard: Limits of Curriculum Learning in Post-Training for Deductive Reasoning"（2026）在多个数据集、模型族、SFT 与 RL(GRPO) 上均"未发现课程相对随机采样的稳定优势"。

#### A.2 自动课程 / 无监督环境设计（UED）及其如何处理遗忘

| 方法 | 采样/生成机制 | 如何处理遗忘/保持 | 评估协议 |
|---|---|---|---|
| ALP-GMM（Portelas 2019, CoRL） | 按绝对学习进度拟合 GMM 采样任务 | 持续在整个参数空间采样 | TeachMyAgent |
| Goal GAN（Florensa 2018, ICML） | GAN 生成中等难度目标 | 易漂移 | 目标覆盖率 |
| Teacher-Student CL（Matiisen 2019, TNNLS） | 教师按进度斜率选任务 | 显式回采停滞子任务 | 各子任务成功率 |
| 自步 RL / SPRL（Klink 2020 NeurIPS；JMLR 2021） | 初始分布到目标分布的 KL 约束插值 | 最终匹配目标分布——在目标分布收尾 | 稀疏目标到达 |
| CURROT（Klink 2022 ICML；TPAMI 2024） | 约束最优传输插值 | 平滑逼近目标分布，保留支撑 | 与 9 方法对比 |
| PAIRED（Dennis 2020, NeurIPS） | minimax regret 对抗生成 | 不回放 | 零样本迁移 |
| PLR / Robust PLR（Jiang 2021） | 回放缓冲，按 L1 值损失＋陈旧度采样 | **回放缓冲＋陈旧度纠偏** | Procgen 留出关卡 |
| ACCEL（Parker-Holder 2022, ICML） | 高后悔关卡小步编辑 | 回放缓冲保留旧关卡 | 零样本迁移 |
| POET（Wang 2019/2020） | 环境-智能体协同进化 | 种群保留多样环境 | 跨环境迁移 |
| ADR（OpenAI 2019） | 达阈值即**扩张**随机化区间 | **扩张而非替换** | sim2real |
| SAMPLR（Jiang 2022） | 纠正课程引入的 aleatoric 偏差 | 保证对目标分布无偏 | CarRacing |

统一规律：**有效的自动课程都是"按学习进度/后悔值采样"＋"保留分布支撑"**，而不是把训练分布从简单"平移"到困难。

#### A.3 on-policy RL（PPO）中的灾难性遗忘与对策

- DisCoRL（2019）演示 PPO 顺序微调时灾难性遗忘。
- on-policy vs off-policy 遗忘："RL's Razor"/"Retaining by Doing"（2025）论证 on-policy 因 KL 最小性遗忘更少（LLM 结论）；"RL Forgets!"（2026）反证连续 RL 仍严重遗忘。
- 技术族：策略蒸馏 / Distral（Rusu 2016；Teh 2017）；Progress & Compress（Schwarz 2018）＋ EWC（Kirkpatrick 2017）；KL-to-old-policy 正则；**PopArt**（Hessel 2019, AAAI）：Atari-57 median human-normalized 110%（IMPALA 59.7%）。
- **可塑性丧失**：Dohare et al. 2024（Nature 632:768–774）——ImageNet 二分类在第 2000 个任务时从 89% 跌到 77%；continual backpropagation 与 L2＋权重扰动缓解。primacy bias / 网络重置（Nikishin 2022；D'Oro 2022）；dormant neuron（Sokar 2023）；capacity loss（Lyle 2022）。**对策不同于遗忘**（reset/CBP/L2 vs 回放/蒸馏/KL）。

#### A.4 泛化与评估协议

- Cobbe et al. 2019/2020（CoinRun / Procgen）：训练关卡 vs 留出关卡。
- Kirk et al. 2023（JAIR 76:201–264，ZSG 综述）。
- Agarwal et al. 2021（NeurIPS oral）：IQM ＋ 分层自助置信区间（2000 次）＋ 性能剖面；`rliable`。

### B. 机器人学

#### B.1 Rudin et al. 2022 的地形课程如何显式防遗忘

（CoRL 2021 / PMLR v164，arXiv:2109.11978，§3.1）
- 晋级："If a robot manages to walk past the borders of its terrain, its level is increased…"
- 降级："…if at the end of an episode it moved by less than half of the distance required by its target velocity, its level is reduced again."
- 防遗忘："**Robots solving the highest level are looped back to a randomly selected level to increase the diversity and avoid catastrophic forgetting.**"
- 全难度分布："With thousands of robots we can directly use their current progress in the curriculum as the distribution of the policy's performance."
- 实现（§2.1）：所有地形类型×难度平铺成一整张网格，物理移动机器人切换难度。
- 五种地形；台阶 5→20 cm，坡 0→25°。评估（§4.2, Fig. 5）：0.75 m/s 固定速度穿越成功率。
- **重要澄清**：该论文**没有**"直接在硬地形训练会失败"的对照消融；§4.1 移除课程时同时简化了任务。

**启示**：Rudin 课程不遗忘是因为（1）并行环境始终横跨所有难度；（2）通关随机回环＝旧任务回放；（3）按个体表现调度。

#### B.2 教师-学生 / 特权信息蒸馏与自适应课程

- Lee et al. 2020（Science Robotics 5(47)）：特权教师→本体感觉学生；粒子滤波维持"可通过但有挑战"地形分布。
- Kumar et al. 2021（RSS, RMA）。
- OpenAI 2019（ADR，arXiv:1910.07113）：26 步扰动 20% 成功，15 步 60%。
- Extreme Parkour、ANYmal Parkour、Walk These Ways 延续同一范式。

#### B.3 机器人领域 curriculum vs. no-curriculum 的直接比较

- W&B legged-gym 复现：terrain 课程加速训练，command 课程无用甚至有害。
- 机器人文献很少给出干净的"课程 vs. 混合"对照消融。

### C. LLM 与 LLM 智能体

#### C.1 数据课程 / 数据配比
- DoReMi（Xie 2023, NeurIPS）：下游 +6.5 pts，2.6× 更少步数——**重配比而非排序**。
- Skill-it（Chen 2023）。
- 结论：混合配比重加权稳定优于顺序课程。

#### C.2 面向推理的 RLVR 难度课程
- DeepSeek-R1（2025）：多阶段；KL-to-reference（0.001）；末阶段全场景 RL。
- AdaRFT（Shi 2025, arXiv:2504.05520）：目标难度随奖励移动；训练步数最多减少 2×。
- 过滤 pass 率 0/1 的题（RORL 等）。
- SEC、E2H、CurES、Absolute Zero。

#### C.3 pass@1 vs pass@k
- Yue et al. 2025（NeurIPS'25，arXiv:2504.13837）：随 k 增大基座反超 RL 模型；RLVR 收窄推理范围；蒸馏能引入新知识。
- 启示：区分"拟合当前分布"与"扩大可解任务集"。

#### C.4 LLM 智能体环境课程
- Voyager（Wang 2023，arXiv:2305.16291）：自动课程＋技能库（外部记忆防遗忘）。

### D. 跨领域综合——八条原则

1. **扩张分布，而非替换分布**（ADR、Rudin 回环、SPRL/CURROT）。
2. **按学习进度/后悔值采样，而非按难度硬调度**（PLR、ACCEL、ALP-GMM、AdaRFT）。
3. **回放已掌握任务**（PLR 缓冲、Rudin 回环、Voyager 技能库）。
4. **任务/难度条件化**。
5. **在完整目标混合上收尾**（SPRL/CURROT、DeepSeek-R1）。
6. **蒸馏做知识巩固**（Distral、Progress & Compress、Lee 2020）。
7. **逐任务/逐难度奖励归一化**（PopArt）。
8. **缓解可塑性丧失**（CBP、L2＋扰动、reset）。

**课程预期会输给混合训练的情形**：奖励密集；目标分布在均匀采样下可学；难度维度无探索瓶颈；顺序排序 vs 重配比（DoReMi）。

---

## Recommendations（可落地的分阶段建议）

### 阶段 0：先把评估做对
1. 分层留出评估（含训练范围内与范围外 bin）。
2. worst-bin 与 IQM（rliable，≥2000 次重采样）＋性能剖面。
3. ≥5 个训练种子、对齐环境步数预算。
4. 保持率曲线（retention curve）。
5. OOD 外推箱。
6. 匹配对照：curriculum vs 混合(uniform) vs 混合(重配比)。

### 阶段 1：把朴素课程改造成"扩张＋回放＋进度"式
1. 改"平移"为"扩张"：任意时刻并行环境按比例保留简单配置（Rudin 回环）。
2. 加难度条件化。
3. 按学习进度采样（或 PLR 式回放缓冲）。
4. PopArt 或逐难度奖励归一化。

### 阶段 2：若仍不及混合，排查第二类失败模式
1. 测可塑性丧失（dormant neuron、特征秩、权重范数）→ L2/CBP/reset。
2. 防遗忘正则（KL-to-old、EWC）。
3. 蒸馏巩固。
4. 末阶段回到完整混合。

### 判据
- 保持率曲线简单 bin 下降 >5–10% → 遗忘主因 → 回放/扩张、KL/蒸馏。
- 简单 bin 不降但学不动新难度且 dormant neuron 升高 → 可塑性丧失 → reset/CBP/L2。
- 混合训练 worst-bin 与 OOD 已达标 → 放弃课程，用混合（可加 DoReMi 式重配比）。
- 奖励稀疏、硬任务 pass≈0 → 课程才有本质收益（PLR/ACCEL/ALP-GMM）。

---

## Caveats
- on-policy vs off-policy 遗忘速度无定论。
- 机器人领域缺乏干净的 curriculum vs mixed 消融；Rudin 2022 没有"直接训硬地形失败"的对照图。
- 课程负结果多来自 LLM/推理领域，迁移到连续控制需谨慎。
- 难度度量是开放问题。
- pass@k 类比在连续控制里的对应物尚不成熟；"OOD 箱＋worst-bin"是当前最实用近似。
- 部分二手来源（DeepSeek-R1 冷启动数据、POET/Voyager/Skill-it 细节）需回到一手论文核实。
