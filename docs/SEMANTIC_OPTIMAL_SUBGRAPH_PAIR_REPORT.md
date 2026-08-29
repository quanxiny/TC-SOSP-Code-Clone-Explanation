# 任务条件化对称最优子图对实验报告

状态：validation-only 计算实验已完成；推荐主变体不使用原模型注意力先验。
GCJ/CodeNet 变换真值、自然样本强基线和运行时门槛已通过；真实盲法专家
评分仍待完成。test 继续封存。

## 结论

可以把原算法的注意力系数作为构造候选子图的先验，但本实验不支持它带来特异性贡献。真实注意力相对确定性打乱注意力的 necessity 差值为 -0.009509，problem-pair cluster bootstrap 95% CI `[-0.022602,+0.000917]`；absolute sufficiency-gap improvement 为 -0.000286，CI `[-0.001090,+0.000299]`。两个区间均不支持真实注意力优于保持分布的打乱对照。

有效的部分是任务条件化的双图语义关系和固定预算离散候选搜索。推荐方法暂称 **TC-SOSP**（Task-Conditioned Symmetric Optimal Subgraph Pair）；这里的“optimal”仅指给定有限候选集中的最优，不是全局组合最优。

## 方法与任务相关性

代码克隆是同角色、可交换的图对关系，不适合直接照搬 Feature Envy 中有方向的 Method→Class KEEP/DROP 目标。TC-SOSP 采用：

1. 对无序图对按文件名作规范化排序，并使用 `min(p(G_i,G_j), p(G_j,G_i))` 的对称预测器，保证交换后选择映射完全一致。
2. 每个图固定选择 top- k 语句节点；主实验 k 为图节点数的 20%。
3. 对预测为 clone 的图对构造高相似度“共同语义语句对”；对预测为 non-clone 的图对构造低相似度“对比差异语句对”。
4. 候选包括对称 Grad×Input、梯度—语义混合、语义乘积、双图 paired-relation marginal，以及一步 CFG 邻域扩散。
5. 对每个候选执行冻结模型的 KEEP/REMOVE 干预，最大化：

   `necessity drop - |sufficiency gap|`

6. 原模型 encoder internal node-token attention 只作为可选候选先验，不直接充当解释；同时运行真实、确定性打乱和 uniform 控制。正式 100 对比较保留真实与打乱控制，uniform 已在 smoke 验证实现后为节省计算而停止扩展。

原实现的注意力归一化跨图节点维/词元位置分组，因此这里谨慎称为“节点—词元内部注意力先验”，不把它描述成严格的单节点内部注意力。

## 固定协议

- 数据：与 C0 完全相同的 100 对 GCJ validation manifest，50 clone + 50 non-clone；预测准确率 0.99。
- 主预测器：paper-clean full-data seed 1337 / epoch 13 checkpoint，参数冻结。
- 主节点预算：每图 20%；附加 10% 和 30% 曲线。
- 统计单位：逐对差值，按 GCJ problem pair 聚类 bootstrap 10,000 次。
- 指标：target-class necessity drop 越高越好；absolute sufficiency gap 越低越好；swap Jaccard 越高越好。
- test：未读取、未推理、未统计。

## 主结果

| 方法（20% 节点） | Necessity | Absolute sufficiency gap | Swap Jaccard | 秒/对 |
|---|---:|---:|---:|---:|
| Symmetric Grad×Input | 0.1731 | 0.0376 | **1.0000** | **0.302** |
| Adapted GNNExplainer（三解释器种子均值） | 0.0358 | 0.3301 | 0.9993 | 3.489 |
| Adapted SubgraphX（三解释器种子均值） | 0.2282 | 0.0232 | 0.9956 | 23.805 |
| TC-SOSP（无注意力） | **0.3088** | **0.0069** | **1.0000** | 0.559 |

逐对比较：

- necessity Δ=+0.135632，problem-pair cluster 95% CI `[+0.077576,+0.175689]`；
- absolute sufficiency-gap improvement=+0.030643，CI `[+0.000422,+0.059391]`；
- swap Jaccard Δ=0，因为两者均达到 1；
- 相对 Grad×Input 增加约 0.256 秒/对，但比 adapted GNNExplainer 和
  adapted SubgraphX 分别快约 6.2 倍和 42.6 倍，也比旧 continuous
  keep-remove mask 的约 5.35 秒/对快约 9.6 倍。

对随机基线先在每个图对内平均 explainer seeds 42/123/2024，再以 100 个
图对作 problem-cluster bootstrap 和配对 Wilcoxon。TC-SOSP 相对
GNNExplainer 的 necessity/sufficiency 增益为 +0.2730/+0.3231，相对
SubgraphX 为 +0.0806/+0.0163；四项在 2 基线 × 3 端点 Holm 校正后均
显著，最大的校正 p 值为 `3.01e-7`。相对 Grad×Input 的固定比较在原
9 端点校正下也保持显著。swap 差异不显著，因此不声称交换一致性优于
所有基线。

三个随机种子的每一个都保持 necessity 与 sufficiency 正效应：最差种子
下相对 GNNExplainer 仍为 +0.2661/+0.3156，相对 SubgraphX 为
+0.0764/+0.0103，且各 seed-specific cluster CI 均排除 0。随机基线的
具体节点选择并不稳定：三种子平均 pairwise selection Jaccard 分别为
0.5026 和 0.4654，100 对中没有一对在三个种子下双侧选择完全相同。
因此可以声称结论对解释器随机性稳健，但不能把随机基线的单次节点集合
描述成稳定真值。完整统计见
`artifacts/comparisons/C16_C18_stochastic_explainer_seed_robustness_validation.json`。

排除四个开发 smoke 样本后，剩余 96 对上的 necessity Δ=+0.134359，CI `[+0.079075,+0.173897]`；absolute sufficiency improvement=+0.031200，CI `[+0.000896,+0.061706]`。因此主效应不是由四个开发样本驱动，但这仍不是预注册的独立 confirmatory benchmark：C0 在同一 validation pool 上的结果此前已知。

## 先验与组件消融

### 注意力先验

| 比较：真实注意力 − 打乱注意力 | 均值差 | Problem-pair cluster 95% CI |
|---|---:|---:|
| Necessity | -0.009509 | [-0.022602, +0.000917] |
| Absolute sufficiency improvement | -0.000286 | [-0.001090, +0.000299] |

结论：注意力可以作为技术上的候选先验，但未通过 attention-specific negative control。推荐变体删除该模块，论文中保留为负消融。

### 语义先验

打乱语义关系后，离散多候选搜索相对梯度仍有较小 necessity 增益 +0.032839，CI `[+0.005526,+0.072643]`。真实语义相对打乱语义再增加 +0.102793，CI `[+0.041431,+0.151840]`。这表明：

- 一小部分增益来自离散候选搜索本身；
- 大部分 necessity 增益来自与 clone/non-clone 任务对应的真实跨图语义关系；
- 真实语义相对打乱语义的 absolute sufficiency 改善区间仍跨 0，因此不单独声称其改善 sufficiency。

### 顺序加入候选族

| 候选池 | Necessity | Absolute sufficiency gap |
|---|---:|---:|
| Gradient only | 0.1731 | 0.0376 |
| + semantic re-ranking | 0.2690 | 0.0078 |
| + paired relation | 0.2994 | 0.0057 |
| + one-step CFG diffusion | **0.3088** | 0.0069 |

- semantic re-ranking 是主组件：necessity Δ=+0.095876，cluster CI `[+0.059193,+0.131078]`，absolute sufficiency 改善 +0.029749，CI `[+0.002346,+0.059031]`。
- paired relation 再增加 necessity +0.030390，CI `[+0.003813,+0.053917]`；其 sufficiency 区间跨 0。
- CFG diffusion 增加较小 necessity +0.009366，CI `[+0.000965,+0.024586]`，但 absolute sufficiency 变化 -0.001207，区间接近并跨 0。若需要更简洁的模型，`semantic + paired relation` 是合理精简版；完整版本保留 CFG 只用于追求 necessity。

正式主方法选择的 100 个候选中，paired relation 32、gradient 17、semantic CFG 13、semantic 0.50 12、semantic 0.75 10、semantic product 8、semantic 0.25 8；83% 的样本没有退化为纯梯度选择。

## 稀疏度与检查点稳健性

| 节点预算 | Necessity Δ | Cluster 95% CI | Absolute sufficiency improvement | Cluster 95% CI |
|---|---:|---:|---:|---:|
| 10% | +0.0942 | [+0.0404,+0.1425] | +0.0489 | [+0.0058,+0.0968] |
| 20% | +0.1356 | [+0.0766,+0.1760] | +0.0306 | [+0.0008,+0.0596] |
| 30% | +0.2179 | [+0.1511,+0.2599] | +0.0067 | [-0.0022,+0.0154] |

20% 是 necessity、sufficiency 与稀疏度之间更平衡的主设置；30% 最大化 necessity，但不再可靠改善 sufficiency。

### 目标函数权重敏感性

在固定 20% 节点预算下，对候选选择目标
`necessity - lambda * absolute_sufficiency_gap` 补充了 lambda
`0/0.5/1/2` 的同样本消融：

| lambda | Necessity | Absolute sufficiency gap |
|---:|---:|---:|
| 0 | **0.309148** | 0.008937 |
| 0.5 | 0.308834 | 0.007090 |
| 1 | 0.308765 | 0.006947 |
| 2 | 0.308156 | **0.006545** |

四个点都在经验 Pareto 前沿上，但差异很小。lambda=0 相对 lambda=1
仅增加 0.000383 necessity，同时使 sufficiency gap 恶化 0.001990；
lambda=2 改善 0.000402 sufficiency gap，但降低 0.000609 necessity。
因此不根据此事后消融重选主方法，保留事先固定且尺度对称的 lambda=1。
证据：`artifacts/comparisons/C_tc_sosp_objective_weight_ablation_validation.json`。

三个独立训练 seed 的 10%-training-data predictor checkpoint 上，方法相对梯度的 necessity Δ 分别为 +0.1558、+0.1528、+0.1613；absolute sufficiency improvement 分别为 +0.0249、+0.0310、+0.0451。六个对应的 checkpoint-level cluster interval 均排除 0，三 checkpoint 平均差为 +0.1566 和 +0.0336。full-data seed 1337 的主检查点也同向，但因训练数据规模不同，不与三 seed 合并作四 seed 推断。

### 自然正负样本分层

TC-SOSP 相对 Grad×Input 的 necessity 增益在 50 个 natural non-clone 上为
+0.0753，在 50 个 natural clone 上为 +0.1960；两个 problem-pair cluster
区间均排除 0。对应 sufficiency-gap 改善为 +0.0046 与 +0.0567，其中
clone 分层的 cluster 区间跨 0，因此只把全样本结果作为主推断。相对
SubgraphX，两类样本的 necessity 和 sufficiency 均保持正向 cluster 区间。

### 变换真值与独立数据

GCJ C8 与 CodeNet C10 各使用 30 个可编译程序的 original、alpha-renamed
及 injected-dead-code 版本，均实现 90/90 CFG 成功和可审计节点对应。TC-SOSP
在两套数据上都取得最高的 alpha/dead correspondence 与最低 absolute
sufficiency gap；相对 Grad×Input 的 necessity 增益分别为 +0.0504 和
+0.0854，严格 18 端点 Holm 校正后仍显著。SubgraphX 在正样本上具有更高
necessity，因此论文主张限定为更稳定、充分的语义子图对，而不是所有
faithfulness 指标上普遍占优。

CodeNet C15 又补充了 15 个跨问题 non-clone 图对。所有 original/alpha/dead
预测均保持 non-clone。TC-SOSP 的 necessity=0.3002、absolute sufficiency
gap=0.0189，均为四方法最优；相对 Grad×Input 的 necessity 增益 +0.1927
在 18 端点 Holm 校正后仍显著。Grad×Input 的平均变换 correspondence 更高，
而 TC-SOSP 的离散 dead-node rejection 更好，这一权衡保留为负面边界。

完整协议与结果见 `docs/EXPLANATION_TRUTH_AND_STRONG_BASELINES.md`。

## 可读案例

已从 TinyPDG 的原始 `codeJson` 恢复所选语句，并按确定规则导出四例：每个标签各一个 subgroup median necessity-gain 例和一个 maximum-gain 例。正样本中可以看到输出格式、数组差分和累计量等共同语义语句对；负样本给出低相似的对比语句区域。

这些案例仅用于人工审计。maximum-gain 显然是 best case；median case 用于展示代表性行为。自然 GCJ 没有节点真值，所以 semantic pair quality 仍是模型派生 proxy，不能写成“解释正确率”。机器可读案例见 `artifacts/explanation_cases/C1_semantic_optimal_subgraph_cases.json`。

## 发表判断与下一步

当前状态升级为 **GO-COMPUTATIONAL-PAPER-2 / HUMAN-GATE-PENDING**。
变换 provenance、两个强图解释器、GCJ/CodeNet 独立复核、正负决策、预算/
checkpoint/目标权重消融和运行时扩展均已完成。计算证据已经足以形成完整
EI 稿件，并达到面向 SCI 投稿的主要技术门槛；但若论文声称解释“可理解、
完整或符合专家语义判断”，真实盲法人评仍是不可替代的最终门槛。

保留的边界包括：

1. 候选选择使用 perturbation faithfulness，而自然样本主指标属于同一家族；
   变换 correspondence、dead-node rejection、语义打乱和独立数据缓解但不
   完全消除循环性。
2. GNNExplainer 与 SubgraphX 都因双图预测器和自定义编码器而明确标为
   adapted，不能写成官方实现的逐行复现。
3. 正样本上 SubgraphX 的 necessity 更高；TC-SOSP 的优势是 correspondence、
   sufficiency、离散干扰节点拒绝和效率的组合，不是单指标统治。
4. 三份 C8 变换包和三份 C9 自然图对包均已盲化并冻结，但不得在真实专家
   提交前生成、补齐或推断评分。

下一阶段只保留两个高价值动作：完成至少两位、最好三位独立专家盲评并
报告一致性/评审时间；若瞄准更高分区 SCI，再加入一个参数化 explainer
作为补强，而不是继续为已否定的 attention prior 扫参。

## 证据

- 完整统一汇总：`artifacts/comparisons/C_semantic_optimal_subgraph_study_validation.json`
- 排除 smoke 的 96 对复核：`artifacts/comparisons/C1_semantic_optimal_subgraph_pair_heldout96_validation.json`
- 定性案例：`artifacts/explanation_cases/C1_semantic_optimal_subgraph_cases.json`
- 主实现：`scripts/explanation_runner.py`
- 新方法测试：`tests/test_optimal_subgraph_pair.py`
- 自然强基线统计：`artifacts/comparisons/C9_natural_strong_baseline_paired_statistics_validation.json`
- 运行时扩展：`artifacts/comparisons/C9_explanation_runtime_scaling_validation.json`
- 变换真值汇总：`artifacts/comparisons/C_transformation_truth_paired_statistics.json`
- 随机解释器三种子：`artifacts/comparisons/C16_C18_stochastic_explainer_seed_robustness_validation.json`
