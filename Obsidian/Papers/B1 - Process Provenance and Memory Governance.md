# B1 - Process Provenance and Memory Governance

## 结论先行

B1 不再把科学问题写成“failure-derived memory 是否更差”。当前最稳的对象是：**在 actionable content 与 target context 已知后，process provenance 是否还包含关于 downstream marginal utility 的额外信息；该信息通过哪个可观察通道进入 executor / governor；只有当它改变最优 memory-governance 决策时，provenance 才具有工程价值。**

现有结果仍严格保持原边界：L0 是观察关联；L1 是 outcome-conditioned writer-mode bundle；历史 L2 byte-identical 设计只有 5/10 eligible unique tasks、0 calls，因此不是 null；L3 source-faithful transport 仍未完成。不能把当前证据写成固定方向的 provenance-only causal effect。

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

### E5 Fresh replication

历史 R4/R6 与 L2 support stop 只作为冻结上下文，不与 fresh confirmatory analysis 合并。

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

- L0：强 association，仅 motivation。
- L1：writer-mode endpoints 方向不一致，不能升级 provenance-only sign。
- L2：5/10 unique task、0 calls，是 support stop，不是 null。
- L3：source-faithful transport debt 未关闭。
- R19：归档，不复活来补实验量。
- 历史剩余 27：non-confirmatory，不做 outcome mining。
- Fresh confirmatory：只有 G1–G8 全过才允许重新申请执行权限。
- PSMG：已形式化为 prospective method，但没有 performance-improvement claim。

## 可复用研究经验

1. **先问因果通道，再问 effect sign。** 一个 metadata 若没有被任何决策组件观察，单独 relabel 不应成为主 causal treatment。
2. **retrieval ≠ utilization ≠ marginal contribution。** 必须用 first-stage intervention 证明 Agent 真正使用了 memory，再谈 provenance downstream effect。
3. **observed reward ≠ marginal utility。** co-retrieval、task baseline 和 selection 都会制造 attribution bias。
4. **failure-derived ≠ bad，success-derived ≠ good。** provenance 应作为条件信息而不是单调质量标签。
5. **null 也必须有机制含义。** 在 qualified design 中，stable null 可以支持 content sufficiency，方法应安全退化而不是继续寻找能过的指标。
6. **实验量不能靠降低门禁获得。** 一个干净 fresh substrate 的价值高于在历史 holdout 上追加大量相关但不可识别的比较。
