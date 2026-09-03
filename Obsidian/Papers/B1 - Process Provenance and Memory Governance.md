# B1 - Process Provenance and Memory Governance

## 结论先行

B1 不再把科学问题写成“failure-derived memory 是否更差”。当前最稳的对象是：**在 actionable content 与 target context 已知后，process provenance 是否还包含关于 downstream marginal utility 的额外信息；该信息通过哪个可观察通道进入 executor / governor；只有当它改变最优 memory-governance 决策时，provenance 才具有工程价值。**

现有结果已经把最关键的 L2 blocker 真正关闭，而且完成了第二 executor backbone 复制。L0 仍是观察关联；L1 仍只识别 outcome-conditioned writer-mode bundle；历史 R5/R19 的 L2 support/runner stop 继续保持原边界，不与新实验合并。新的 R53--R57 prospective MemRL/OSInteraction 实验在 350 个 source tasks 上建立独立 memory bank，经 zero-outcome native-support gate 冻结 32 个 fresh primary clusters 与 8 个 utilization clusters；Qwen2.5-7B-Instruct 上 A(content-only)=15/32、B(+ truthful provenance)=16/32，$\Delta=+0.03125$，exact paired sign-flip $p=1.0$，paired bootstrap 95% CI $[0,0.09375]$，未达到 $|\Delta|\ge0.15$ relevance floor。R59--R61 随后在**完全相同的 source bank、retrieval/content/order、32 个 units、A/B renderer、endpoint 和统计规则**上只替换 executor 为 Meta-Llama-3.1-8B-Instruct；Llama 自己先通过 utilization gate（U1-specific 8/8，placebo U2-vs-U0 5/8），再完成 64/64 A/B：$\Delta=0$，B-only/A-only=2/2，exact $p=1.0$，95% CI $[-0.125,0.125]$，同样未达到 15 pp relevance floor。两模型不做统计 pooling。当前最强结论因此是：**在同一 support-qualified MemRL/OSInteraction exact-information surface 上，raw provenance 对局部控制可见，但在 Qwen 与 Llama 两个独立 executor backbone 上都没有表现出预注册意义上的 terminal incremental value；这是 replicated low-terminal-value / qualified content-sufficiency evidence，而不是 universal zero-effect theorem。** L3 source-faithful transport 与 PSMG governor efficacy 仍未完成。

## 一条完整论文线

```text
自进化 Agent 从成功/失败 trajectory 生成持久 memory
        ↓
retrieval 系统往往只保留 content / relevance / observed reward
        ↓
但 source outcome ≠ memory content ≠ downstream marginal utility
        ↓
先用 L0–L3 ladder 分开 provenance 进入系统的通道
        ↓
再估计 provenance 对 marginal utility 的条件信息，而非预设 success-good / failure-bad
        ↓
推导 No-Channel / Content-Sufficiency / Provenance-Information 三条机制律
        ↓
用 utilization first stage + randomized inclusion / fixed-context replay 做因果识别
        ↓
得到 PROVENANCE_INFORMATIVE / CONTENT_SUFFICIENT / CONFOUNDED / MEMORY_UNUSED / UNCERTAIN regime
        ↓
PSMG 根据 posterior utility、downside risk 与 verification cost 做 reuse / verify / escalate / abstain
        ↓
provenance 无增益时安全退化到 content-only
```

## 科学变量

- `T_i`：source trajectory。
- `O_i`：独立 evaluator 给出的 source outcome。
- `C_i`：从 trajectory 抽取的 actionable memory content。
- `P_i`：不可变 process-provenance record。
- `X_j`：target task/context。
- `A_ij`：admit/retrieve/expose 决策。
- `U_ij`：executor 是否实际利用 memory。
- `Y_ij`：target outcome。
- `theta_ij`：memory 对 target 的 marginal utility。
- `G_ij`：governance action。

核心 estimand：

\[
\theta_i(x)=E[Y\mid do(A_i=1),X=x]-E[Y\mid do(A_i=0),X=x].
\]

内容控制后的 provenance gap：

\[
\Delta_P(x,c)=E[\theta\mid P=success,C=c,X=x]-E[\theta\mid P=failure,C=c,X=x].
\]

真正的治理价值是 provenance 的 value of information：

\[
V_P=E[\max_g E[u(g,\theta)\mid C,X,P]-\max_g E[u(g,\theta)\mid C,X]].
\]

## 三条机制律

### 1. No-Channel Law

如果 executor 与 governor 都看不到也不使用 `P`，只改变 backend provenance label 不应该改变行为分布。若出现差异，应优先诊断状态不一致、输入泄漏或其他未控通道，而不是宣布“历史本身产生了因果效应”。因此 hidden metadata relabel 是 **negative control**，不是主效应实验。

### 2. Content-Sufficiency Law

若

\[
\theta \perp P \mid C,X,
\]

则 content/context 已经是充分信息；provenance 对最优决策没有增量价值。此时 PSMG 必须把 provenance 系数 shrink 到零并退化为 content-only governance。稳定 null 因而是有意义的 regime 结论，而不是实验失败。

### 3. Provenance-Information Law

只有当 `P` 改变 `theta` 的后验，并且差异足以改变最优 reuse / verify / raw-trace escalation / abstain 决策时，provenance 才真正有工程价值。

## PSMG：Provenance-Sensitive Memory Governance

PSMG 不是 success 加权、failure 降权，而是五阶段治理器：

1. **Capture**：content 与 lineage 分离存储。保留 raw trajectory hash、evaluator/version/outcome、extractor/version、transformation chain、retrieval/audit history。
2. **Estimate**：估计 `p(theta | C,P,X,D)`；provenance 只是可收缩 feature/prior，不是质量真值。
3. **Decide**：在 `REUSE / REUSE_WITH_CAUTION / VERIFY_THEN_REUSE / ESCALATE_TO_RAW_TRACE / ABSTAIN / CONTENT_ONLY_FALLBACK` 中决策。
4. **Update**：只有 randomized inclusion/withholding、fixed-context replay 或明确建模的 bundle interaction 才能更新 marginal contribution；共同出现在成功 episode 中不等于贡献。
5. **Safe Collapse**：support、label reliability、conditional information gain 或 transport evidence 不足时 provenance influence → 0。

## 实验闭环

### E0 Measurement qualification

- provenance-chain integrity：extraction / merge / split / summary / dedup / retrieval 后 lineage 100% preservation。
- information-equivalence：结构化 action semantics + 可执行 behavioral equivalence + blind adjudication；embedding 只能做描述变量。
- utilization first stage：true / null / reversed / shuffled memory。
- backend-only provenance relabel：必须 equivalence-null，作为 no-channel negative control。

### E1 Association → marginal utility

把 observational utility 与 causal marginal utility 分开：

- success-associated memory 中是否存在 `theta <= 0`；
- failure-derived memory 中是否存在 `theta > 0`；
- observed-return ranking 与 marginal-utility ranking 的相关/校准差距；
- co-retrieval reward 是否产生 attribution trap。

### E2 Channel factorial

| Arm | Memory | Executor 看 provenance | Governor 看 provenance | 识别对象 |
| --- | --- | --- | --- | --- |
| A0 | 无 | 否 | 否 | task baseline |
| A1 | matched content | 否 | 否 | content-only effect |
| A2 | matched content | 是 | 否 | executor trust response |
| A3 | matched content | 否 | 是 | governance information value |
| A4 | matched content | 是 | 是 | full deployment effect |
| A5 | matched content | 随机标签 | 否 | label susceptibility |
| A6 | matched content | 否 | 随机标签 | governor placebo |
| A7 | matched content | 隐藏 relabel | 隐藏 | no-channel control |

### E3 Regime law

预冻结 moderators：source-target similarity、representation、difficulty、evaluator reliability、executor strength、provenance support、interaction density、decision risk。

只允许五类结论：

- `PROVENANCE_INFORMATIVE`
- `CONTENT_SUFFICIENT`
- `PROVENANCE_CONFOUNDED`
- `MEMORY_UNUSED`
- `UNCERTAIN`

### E4 PSMG evaluation

Qualified baselines：contribution-aware content-only、observed-return/Q ranking、success-only admission、provenance-only heuristic、raw-trace verification fallback、PSMG without shrinkage、oracle marginal-utility upper bound。

指标除了 terminal utility，还必须有 policy regret、negative-utility reuse、false promotion of negative-utility success memories、missed useful failure-derived memory、calibration/Brier、risk-coverage、verification/escalation cost、token/latency/call/storage cost。

### E5 Fresh L2 replication（R53--R57，已完成）

历史 R4/R6、R5、R19 与 R51 support stop 只作为冻结上下文，不与 fresh confirmatory analysis 合并。新实验采用独立 prospective lineage：

- **R53 source bank**：冻结 OSInteraction train split 的全部 350 个 source tasks，按 outcome-blind SHA256 顺序逐个执行并写 memory；350/350 完成，source outcome 176 success / 174 failure，外部 API calls 为 0。
- **R54 native support**：在任何 validation environment reset/evaluator 前，仅用 frozen instruction + native MemRL retrieval 检查支持；排除历史 40 个 cluster 后共有 108 个 fresh skill-signature clusters，其中 106/108 有 eligible retrieval；按预冻结 hash rank 取前 32 个为 primary、后 8 个为 utilization。
- **R55 utilization first stage**：8 clusters × U0/U1/U2/U3/U4 共 40/40 arms 完成。U1 true-memory 在 5/8 units 上相对 U0 与 U2 产生 specific first-action divergence；U2-vs-U0 placebo divergence 为 3/8，满足冻结的 `5 >= 3` 且 `5 >= 3+1` promotion rule，因此确认 memory surface 被 Agent 行为性使用。
- **R56 L2 primary**：32 fresh clusters × A/B 两臂，64/64 arms、0 failures。A=`content only`，B=`same retrieval/order/actionable bytes + truthful source_outcome_success`。A=15/32，B=16/32，$\Delta=+3.125$ pp；B-only=1、A-only=0、discordant pairs=1；exact two-sided sign-flip $p=1.0$；预注册 paired bootstrap 95% CI $[0,9.375]$ pp；15 pp practical floor 未达到。
- **complete-only mechanism diagnostic**：A/B 第一条 executable action 在 9/32 clusters 不同，总步数在 7/32 不同，但 terminal outcome 仅 1/32 不同。这支持 `PROVENANCE_BEHAVIORALLY_LEGIBLE_LOW_TERMINAL_CONVERSION`：标签可以扰动局部控制，但几乎没有增加最终任务效用。
- **R57 adjudication**：`L2_PROVENANCE_ONLY_COMPLETE_QUALIFIED_CONTENT_SUFFICIENCY_LOW_TERMINAL_VALUE`。不能写成 provenance 的真实效应“精确为零”，也不能把一个 task 的差异升级为普遍机制。

### E6 Executor-backbone replication（R59--R62，已完成）

- **只换 executor**：source bank、R54 retrieval/content/order、32 个 primary units、8 个 utilization units、A/B renderer、terminal evaluator、随机化与分析规则全部保持冻结；模型从 Qwen2.5-7B-Instruct 换为 Meta-Llama-3.1-8B-Instruct。
- **R59 parser qualification**：3/3 source-side probes 在原生 prompt 下产生可解析非空 executable action；未打开 validation outcome。
- **R60 utilization**：40/40 arms 完成，U1-specific first-action divergence=8/8，U2-vs-U0 placebo divergence=5/8，满足 promotion gate，因此低 terminal effect 不能归因于 memory first stage 失败。
- **R61 primary**：64/64 A/B 完成；$\Delta=B-A=0$，B-only=2、A-only=2、discordant=4，exact two-sided sign-flip $p=1.0$，paired bootstrap 95% CI $[-0.125,0.125]$，15 pp relevance floor 未达到。
- **R62 adjudication**：`CROSS_BACKBONE_L2_REPLICATION_COMPLETE_ROBUST_LOW_TERMINAL_VALUE_NO_POOLING`。Qwen $+3.125$ pp、Llama $0$ pp 分别报告，不做 post-hoc pooling；允许写成同一 substrate 上的 **two-backbone replicated low terminal value**，不能写成跨所有模型/任务的 zero-effect theorem。

## Fresh substrate G1–G8

1. source outcome 来自独立 environment/evaluator，不由研究者后标。
2. content matching/canonicalization 不看 confirmatory target outcome。
3. intervention 只改变声明的 provenance channel；backend-only relabel 仅作 negative control。
4. fresh target 与 R19、历史剩余 27 units 隔离。
5. terminal / decisive-action endpoint 在同一 evaluator 下可 replay。
6. independent task/template/family 才是统计 n；seed/request 是 nested repetition。
7. matching、exclusion、support 决策对 confirmatory outcome blind。
8. manifest、estimand、exclusion、moderator、power/precision、stopping rule 在第一次 fresh outcome 前冻结。

## 相关工作边界

- execution/source provenance 与 lineage 已有系统化工作，所以“memory 应保留 provenance”本身不是 novelty。
- outcome-aware memory governance、signed outcome evidence 与 persistent memory mutation 已有近邻，因此不能把 PSMG 包装成第一个 provenance-aware memory system。
- learning-from-failure / multi-round feedback / reflective memory 表明 `failure-derived ≠ bad`，所以不能预设固定方向。
- content/relevance/Q-value memory ranking 已覆盖“相似性不足以决定 reuse”，B1 的新增对象必须是 **channel-specific causal identification + provenance-conditioned marginal utility + governance value of information**。

Canonical literature anchors already used in the paper story: arXiv:2606.04990, 2607.29167, 2606.31270, 2608.02636, 2608.02843, 2601.03192, 2502.12110.

## 当前冻结边界

- L0：强 association，仅 motivation，不能升级为 causal sign。
- L1：writer-mode endpoints 方向不一致；只识别 writer-mode bundle，不能升级 provenance-only sign。
- 历史 L2：R5 的 5/10 unique-task support stop 与 R19 的 fail-closed incomplete run继续归档，不复活、不 pooling。
- **Fresh L2（R53--R57）**：已完整执行并识别。32 paired clusters 中 A=15/32、B=16/32，$\Delta=+3.125$ pp，exact $p=1.0$，预注册 bootstrap CI $[0,9.375]$ pp，未达到 15 pp relevance floor；31/32 terminal pairs 相同。允许的结论是 **qualified content-sufficiency / low incremental terminal provenance value in this setting**，不是 universal null。
- **Behavioral channel**：R55 utilization PASS；R56 A/B first action 9/32 不同，因此不能解释为“Agent 没看到/没用 memory 或 provenance”。更准确的机制描述是 provenance 可改变局部轨迹，但 terminal conversion 很低。
- L3：source-faithful motivating-runtime transport debt 未关闭。
- **第二 backbone（R59--R62）**：已 prospectively 完整执行。Meta-Llama-3.1-8B-Instruct parser 3/3 PASS、utilization 8/8-specific vs 5/8-placebo PASS；primary 32 pairs 中 $\Delta=0$，B-only/A-only=2/2，exact $p=1.0$，bootstrap CI $[-12.5,12.5]$ pp，仍低于 15 pp relevance floor。与 Qwen 结果只做 descriptive replication，不 pooling。
- PSMG：已形式化为 prospective governance method，但 C/D controller efficacy 仍 `NOT_IDENTIFIED`；R56 A/B 不能被包装成 PSMG performance claim。

## 可复用研究经验

1. **先问因果通道，再问 effect sign。** 一个 metadata 若没有被任何决策组件观察，单独 relabel 不应成为主 causal treatment。
2. **retrieval ≠ utilization ≠ marginal contribution。** 必须用 first-stage intervention 证明 Agent 真正使用了 memory，再谈 provenance downstream effect。
3. **observed reward ≠ marginal utility。** co-retrieval、task baseline 和 selection 都会制造 attribution bias。
4. **failure-derived ≠ bad，success-derived ≠ good。** provenance 应作为条件信息而不是单调质量标签。
5. **null 也必须有机制含义。** 在 qualified design 中，stable null 可以支持 content sufficiency，方法应安全退化而不是继续寻找能过的指标。
6. **实验量不能靠降低门禁获得。** 一个干净 fresh substrate 的价值高于在历史 holdout 上追加大量相关但不可识别的比较。
