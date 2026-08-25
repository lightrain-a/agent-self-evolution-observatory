# E2-R17 文献综合与重大重构：Search-Projection Censoring

日期：2026-08-25

状态：DESIGN-ONLY；不构成实验授权，不改写 R16，不覆盖已冻结 F0-R2 / F0-R3。

候选标题：**When Better Search Teaches Less: Search-Projection Censoring in Self-Evolving Agents**

候选副标题：**Act from the Winner, Learn from the Search Set**

## 0. 本轮结论

原来的“Compute Shielding”直觉仍有价值，但表述过宽，也会被已有反例直接击穿：Expert Iteration、AlphaZero-like distillation、TSR 等工作都说明，更多 search 完全可能产生更好的训练数据并改善后续策略。因此，不能把论文写成：

> more test-time compute improves acting but harms learning.

真正更精确、可守住、也更有机制深度的科学对象是：

> **Test-time search 生成的是一个候选集合或搜索树；系统随后需要分别决定“给用户执行哪条轨迹”和“给 persistent learner 看哪部分搜索证据”。现有 self-evolving skill pipeline 往往把二者隐式绑定为同一个 winner-only projection。这个绑定会在 search 成功救回任务时，系统性删掉暴露 reusable deficiency 的失败分支。**

新的核心不是 compute amount，而是：

```text
search object / rollout pool T_K
          ├── acting projection a(T_K)   -> served winner
          └── learning projection g(T_K) -> updater evidence
```

现有默认：`g = a = winner-only`。

论文要证明：

1. acting-optimal projection 与 learning-optimal projection 一般不相同；
2. winner-only projection 会产生可精确预测的 selection censoring；
3. 当被删掉的失败比 winner 更有 reusable diagnostic value 时，在线 performance 上升但 frozen-skill quality 下降；
4. 通过 act–learn dual projection，可以在不降低 high-compute acting、且不增加 actor rollout 数量的情况下恢复 persistent learning。

一句话主张：

> **Better search does not inherently teach less; learning from only what search serves can.**

## 1. 文献给出的关键约束

### 1.1 Snell et al.：学习“统一科学变量”，不是复制 baseline 列表

`Scaling LLM Test-Time Compute Optimally...` 把 parallel search、sequential revision、verifier search 压进统一的 compute-allocation 问题，并证明最优策略随 prompt difficulty 改变。R17 应学习其方法论：先找到一个统一对象，再让公式、干预、算法和工程决策从该对象自然长出。

R17 的统一对象不再是 `Skill vs. Compute`，而是 `Search-to-Learning Projection`：test-time search 产生的完整搜索对象如何被压缩成 persistent updater 的观测。

### 1.2 Rethinking Self-Evolving Agent Skills：failure feedback 有价值，但尚未问 failure 为什么消失

该工作发现：388 个 candidate 中只有 55 个成为 byte-distinct validation new best；failure-containing 条件的 yield 高于 success-only，且 11 个最终选中 skill 全部来自包含 failure feedback 的条件。它还发现 Parallel Sampling 在 SearchQA 几乎追平 evolved skill，却在 SpreadsheetBench 上仍落后约 30.96pp。

这给 R17 两个直接启发：failure 可能是 skill evolution 的主要学习信号；skill/search 关系存在 substrate-specific regime，不能写成普遍单调规律。R17 的 residual 是继续追问 executor 的 best-of-K search 是否在 updater 之前内生地删掉了这些 failure。

### 1.3 TSR / Expert Iteration / AlphaZero-like distillation：search 本身不必然损害 learning

TSR 把 beam、lookahead、best-of-N 移到 train-time rollout construction，并在适中预算下改善 agent RL；只有 search 太强、search-induced distribution 与 policy 偏离过大时才退化。Expert Iteration 与 AlphaZero-like 系统更直接地把 search 视为 policy-improvement operator，并把 richer search targets（如 visit-count policy、成功路径或 state-action 数据）蒸馏回 policy。

这组文献构成 R17 的 strongest counterexample：如果 learner 看到了 search 产生的丰富对象，更多 search 可以帮助学习。因此，R17 必须把“compute harmful”改成“winner-only search projection can be harmful”。

### 1.4 Search-E1 / CRAFT / SGCD / OVCSD：不能声称“首次利用 sibling contrast”

这些工作已经使用 sibling successful/failed rollouts、privileged context、counterfactual credit、prefix-tree divergence 或 outcome-verified continuation，为 model-weight RL / self-distillation 提供更密集的 credit。

R17 不能把 novelty 写成“首次学习 rejected rollouts”“首次对比 success 与 failure”“首次从 sibling trajectory 提炼经验”。可守住的边界是：

> **我们研究的不是如何给 model weights 做 token-level credit，而是 acting selector 如何改变 external persistent skill updater 的可见经验分布；我们给出一个 order-statistic censoring law、同池 causal projection intervention，以及不增加 actor rollout 的 dual-channel skill update。**

### 1.5 SKILL-KD / SkillOpt：借鉴训练纪律，不重复 scientific object

SKILL-KD 已经把 student failure 与 stronger teacher trajectory 的差异蒸馏成 textual skill patch。SkillOpt 已经把 textual skill 当作外部可训练状态，引入 bounded edits、held-out validation gate、rejected-edit buffer、slow/meta update。

R17 应直接借鉴 bounded add/delete/replace、held-out acceptance gate、rejected patch memory、train/selection/test 隔离。但 R17 的 teacher 不是外部更强模型；证据来自同一 actor 的 search pool，真正问题是 winner-only logging/projection 导致的 selection censoring。

### 1.6 Selective labels / performative prediction / DAgger：理论母体，不是最终 novelty

Selective-label work研究“决策决定哪些 outcomes 可被观察”；performative prediction 研究“部署决策改变未来数据分布”；DAgger 强调 learner 应在其诱导的状态分布上获得监督。

R17 是这一结构在 self-evolving LLM agents 中的具体实例：

```text
search/selection policy
    -> which trajectory becomes observable to updater
    -> which persistent skill is learned
    -> future behavior
```

论文应承认该理论母体，不声称发现普遍意义上的 censoring。

### 1.7 RLVR pass@k inversion：最接近的“方向反转”类比

近期 RLVR 工作发现 pass@1 可以上升而 high-k coverage 下降，尤其发生在 boundary prompts：训练把稀有正确模式从 policy support 中挤掉。

R17 的方向相反但结构同构：RLVR inversion 是 training update 改变 future inference support；R17 是 inference selection 改变 future training support。这提示主结果不能只报平均 accuracy，而必须研究 support/diagnostic coverage 的丢失发生在哪个 regime。

## 2. 新的统一形式化

### 2.1 Search object 与双投影

给定 task `x`、persistent skill state `S_t`、search budget `K`：

\[
\mathcal T_K \sim Q_K(\cdot\mid x,S_t).
\]

`T_K` 可以是 K 个独立 rollout、beam tree、sequential revision trace 或其他 search object。

acting projection：

\[
\tau^+ = a(\mathcal T_K).
\]

learning projection：

\[
E_t = g(\mathcal T_K).
\]

persistent update：

\[
S_{t+1}=U(S_t,E_t).
\]

当前 acting value：

\[
A(a,K)=\mathbb E[R(a(\mathcal T_K))].
\]

统一低 compute、冻结 skill 后的 learning value：

\[
J(S_{t+1})=\mathbb E_{x'\sim D_{test}}[R(\pi_L(x';S_{t+1}))].
\]

核心区别：`A` 主要依赖 acting projection `a`，future skill quality 依赖 learning projection `g`，没有理论理由要求 `a*=g*`。

### 2.2 Winner-only coupling

许多 pipeline 实际使用：

\[
g_{win}(\mathcal T_K)=a(\mathcal T_K)=\tau^+.
\]

这意味着 search pool 中所有 nonserved branches 对 updater 都是 missing-not-at-random；它们是否缺失由 verifier outcome 与 selector 共同决定。

### 2.3 Diagnostic retention

设 `Z` 表示可复用 deficiency family，例如忘记 materialize formula value、修改 input file、漏掉 schema conversion、未做 verification、错误 sheet/range、tool sequence 错误。

理论上可定义：

\[
D_g=I(Z;g(\mathcal T_K)\mid x,S_t),
\]

但真实 benchmark 不应把 mutual information 当装饰性指标。controlled suite 中 Z 由 deterministic validator 精确给出，可估 exact diagnostic coverage/MI；real benchmark 只报告可审计的 failure-family coverage、rescue event 与 patch-rule coverage。

## 3. 核心理论：Rescue–Censoring Identity

### 3.1 Binary verifier 模型

设每条独立 rollout 成功概率为 `p`，K 条 rollout 相互独立。

\[
A_K(p)=1-(1-p)^K
\]

是 best-of-K acting success；winner-only updater 看到 failure 的概率为：

\[
V_K^{win}(p)=(1-p)^K.
\]

预先指定 rollout-0 作为 learning branch，其 failure visibility 不随 K 改变：

\[
V_K^{pre}(p)=1-p.
\]

于是：

\[
\boxed{A_K(p)-A_1(p)=V_K^{pre}(p)-V_K^{win}(p)=\Gamma_K(p)}
\]

其中：

\[
\Gamma_K(p)=(1-p)-(1-p)^K=(1-p)[1-(1-p)^{K-1}].
\]

解释：在该最小模型中，best-of-K 相对 single rollout 获得的每一单位 acting gain，恰好对应一单位从 winner-only learning channel 中消失的 single-rollout failure mass。等价事件是：predesignated rollout fails，且其余 K-1 条中至少一条成功。

### 3.2 Intermediate-difficulty law

`Gamma_K(p)` 在：

\[
\boxed{p^*(K)=1-K^{-1/(K-1)}}
\]

处最大。

| K | p* |
|---:|---:|
| 2 | 0.500 |
| 4 | 0.370 |
| 8 | 0.257 |
| 16 | 0.169 |

因此，shielding 最强的不是极易题，也不是完全不会的题，而是“单次不稳定、search 经常能救回”的 boundary/intermediate regime。可冻结预测：winner-only 与 diagnostic projection 的 frozen-skill gap 应在中等 single-rollout solvability 上最大，并在 floor/ceiling 两端减弱。

### 3.3 Visibility 不等于 learning value

仅证明 failure 被隐藏还不够。成功轨迹也可能比失败更适合学习。设 mixed group 中：

- `ell_F`：从 failure witness 更新后的期望 future gain；
- `ell_S`：从 served success 更新后的期望 future gain；
- `delta = ell_F - ell_S`：diagnostic advantage。

在简化齐次条件下：

\[
\boxed{\Delta_{learn}^{pre-win}(K,p)=\Gamma_K(p)\,\delta.}
\]

真正的 shielding risk 是：

\[
\boxed{\mathcal R_{shield}(K,z)=\Gamma_K(p_z)\,\delta_z.}
\]

三种 regime：

1. `Gamma≈0`：没有 selection censoring；
2. `Gamma>0, delta>0`：失败 witness 更适合形成 reusable correction，winner-only harms learning；
3. `Gamma>0, delta<=0`：success/search trajectory 更有价值，search 可以改善 learning，符合 TSR/Expert Iteration 类型结果。

机制深度由此收敛为：**selection censoring mass × censored evidence 的 reusable value**。

### 3.4 Prospective mechanism prediction

在 calibration split 上估计 `p_z` 与 cloned-state intervention 得到的 `delta_z`，在 longitudinal experiment 前冻结：

\[
\hat{\mathcal R}_{shield,z}=\Gamma_K(\hat p_z)\hat\delta_z.
\]

随后 prospectively 预测 held-out failure families/difficulty cells 的 reversal、方向和 gap 排序。只有能预测 unseen cells，机制才不只是事后解释。

## 4. Search topology × learning projection

原“Compute Shielding”会被 TSR 反例击穿。新版明确区分两个轴。

### Axis A：search topology

- Parallel best-of-K：失败分支彼此独立，winner selection 会整支删除 nonwinner trajectories；
- Sequential refinement：早期错误可能保留在同一 conversation/history 中；
- Beam/tree search：可能保留 partial-state statistics，也可能只输出 final path。

### Axis B：learning projection

- winner/final-only；
- precommitted branch；
- rejected witness；
- full-history/full-tree；
- contrastive packet。

关键预测：shielding 不是由 parallel compute 单独决定，而由 `topology × projection` 的组合决定；parallel + winner-only 应最强，sequential + full-history 应显著减弱。

| | winner/final-only | history/branch-preserving |
|---|---|---|
| Parallel search | 高 censoring 预测 | actor 相同，learning recovery 预测 |
| Sequential refinement | 若只存 final 仍可能 censor | 若保存 correction history，censoring 明显减弱 |

必须 match LLM calls、input/output tokens、tool calls、verifier access；sequential depth 与 parallel width 分开记账。

## 5. 方法闭环：Censor-Aware Dual Projection（CADP，暂名）

### 5.1 原则

不要让 served trajectory 自动成为唯一 training trajectory。

```text
Acting channel:  serve the verifier-selected winner.
Learning channel: preserve evidence that identifies what the base actor still needs to learn.
```

### 5.2 三层实现

#### I. Precommitted Shadow Projection（因果识别器）

从同一个 K-rollout pool 中，在任何 outcome 前指定 rollout-0：

- acting：serve best-of-K；
- learning：feed rollout-0；
- actor compute：与 H/H 完全相同；
- updater evidence volume：仍是一条 trajectory；
- 不需要额外 shadow call。

它不是最终最优方法，而是最干净的 causal intervention：只改变 learning observation kernel。

#### II. Rejected-Witness Projection（strong simple baseline）

在 mixed group 中选择一个非 served failure witness；在 all-fail group 中选择预先冻结规则下的代表 failure；在 all-success group 中用 winner 或 skip。

它检验是否只要利用 high-K pool 中现成 rejected failure 就足够，不需要额外 counterfactual generation。当前 `H_REJECTED_MINE` 应重命名为 `H/Rejected-Witness`；“hardmine”容易误导为跨任务重采样。

#### III. Contrastive Diagnostic Projection（论文方法）

对 mixed group 构造固定 token budget 的 packet：

```text
- task requirement / common pre-state
- served winner 的最小成功摘要
- one precommitted or frozen-rule failure witness
- first outcome-relevant divergence / verifier failure signature
- instruction: propose one reusable correction; forbid task IDs and instance facts
```

然后：

1. updater 产生 bounded add/delete/replace patch；
2. patch 在 held-out selection split 上验证；
3. 只有严格提升才接受；tie/reject 进入 rejected-edit memory；
4. deployed skill 保持 compact、可审计。

该方法的核心不是“contrastive learning 首次出现”，而是：contrast packet 被 search-projection censoring mechanism 精确触发，只用于 mixed groups，并以 external persistent skill patch 为更新对象。

### 5.3 Censor-aware projection rule

\[
g_{CADP}(\mathcal T_K)=
\begin{cases}
\text{winner-only or no-update}, & \text{all success};\\
\text{representative failure}, & \text{all failure};\\
\text{winner--failure contrast packet}, & \text{mixed group}.
\end{cases}
\]

只有 mixed group 同时满足：search 产生 acting rescue、winner-only 删除可见失败、contrast 存在 outcome-grounded anchor。这避免把方法写成泛化的“大模型反思器”。

### 5.4 Fixed-budget controls

必须加入：winner-only；winner + duplicate winner（token matched）；winner + random nonselected success；failure witness only；random pair；full-pool/full-tree upper bound；contrast without validation gate；contrast with validation gate。

这样才能证明 gain 来自 diagnostic contrast，而不是更多文本或更多 updater tokens。

## 6. 实验体系：从 law 到 causality，再到 longitudinal system

### F0 — 当前静态门禁（已完成，保留）

保留 MindMemOS official clean substrate、SpreadsheetBench Verified-400 exact hashes、K=1 vs K=4、per-rollout receipts/CSV/checkpoints、winner-only/precommitted rollout-0/rejected witness semantics、provider 恢复前 0 scientific outcome。

当前 8-train/8-eval 只允许做 pipeline pilot，不能成为论文主证据。

### F1 — Controlled Procedure Suite：验证 regime law

构造 parameterized Spreadsheet Procedure Suite。它不是为了“制造 high compute 有害”，而是为了提供 independently executable latent deficiency labels。

建议 reusable failure families：

1. preserve source file / copy-before-edit；
2. correct sheet/range targeting；
3. formula materialization；
4. multi-sheet join / key alignment；
5. schema/type conversion；
6. output naming/path；
7. final verification / target-cell check。

每个 family 生成 easy/boundary/hard 三个 complexity regimes、train 与 held-out variants、deterministic task validator、deterministic failure-family validator，并严格分离 instance facts 与 skill rule。

预算采用 nested pools：每个 task 一次生成 Kmax=8 个 rollout，即可离线构造 K={1,2,4,8} prefix，避免重复生成。

F1 检验：

1. empirical `A_K` calibration；
2. rescue-censoring event rate 是否匹配 `Gamma_K(p)`；
3. event 是否在 intermediate p 附近峰值；
4. winner-only projection 的 failure-family coverage 是否按 K 收缩；
5. full pool 中 failure 仍存在，证明是 projection loss，不是 generator support 消失。

### F2 — Cloned-State One-Step Causal Intervention

这是最关键的因果实验，优先于 multi-round。

对同一个 pre-update skill state `S`、同一个 task batch、同一个 K-pool：

```text
clone S into several identical updater states
        ├── apply winner-only evidence
        ├── apply precommitted rollout-0 evidence
        ├── apply rejected-witness evidence
        └── apply contrast packet
```

随后全部 freeze skill，使用 common K=1 executor、same held-out probe，且 probe feedback 永不进入 updater。

candidate pool、acting winner、model、verifier、task、initial skill 全部相同，唯一变化是 `g(T_K)`。

主 estimand：

\[
\Delta_{proj}=\mathbb E[J(U(S,g_1(T_K)))-J(U(S,g_0(T_K)))].
\]

F2 还用于估计每个 failure family 的 `delta_z`，并在 F3 前冻结 shielding-risk prediction。

### F3 — Prospective Mechanism Prediction

使用 F1/F2 development cells 估计：

\[
\hat R_{shield,z}=\Gamma_K(\hat p_z)\hat\delta_z.
\]

对从未进入 F1/F2 的 held-out task templates/workbook families，在 outcome 前写下：哪些 cells 应有 reversal、哪些应无 effect、gap 大小排序。

执行后检验 sign accuracy、rank correlation、predicted-vs-observed calibration，以及 zero-risk cells 是否接近零。

### F4 — MindMemOS × SpreadsheetBench Multi-Round Evolution

五个 arm 从 exact same initial skill SHA 出发：

1. L/L；
2. H/H winner-only；
3. H/precommitted；
4. H/rejected-witness；
5. H/CADP contrast。

每 8 个 evolution tasks 形成一次 source-faithful update。正式实验应有 4–5 evolution batches、多个 independent evolution-stream seeds、每轮后 frozen K=1 held-out probe、final group-disjoint test。

同时画：

\[
R_t^{online}\quad\text{and}\quad J(S_t)^{frozen,K=1}.
\]

headline pattern：

\[
R_{online}^{H/H}>R_{online}^{L/L},
\]

但：

\[
J(S_T^{H/H})<J(S_T^{L/L}),
\]

并且：

\[
J(S_T^{H/CADP})>J(S_T^{H/H})
\]

而 high-compute acting 不下降。

F4 同时记录 SKILL.md exact diff、patch rule × failure-family coverage、accepted/rejected edits、updater input token budget、actor call/token/tool budget、mixed-group rate 与 rescue-censoring events。

### F5 — Topology × Projection

在 matched budget 下比较 parallel best-of-K 与 sequential refinement，以及 winner/final-only 与 full-history/branch-preserving。主要检验 interaction：

\[
(topology\times projection)\rightarrow failure\ retention\rightarrow frozen\ skill.
\]

若 sequential full-history 明显避免 reversal，而 sequential final-only 仍发生，说明核心是 observation projection，而不是“parallel search 天生有害”。

### F6 — 第二 substrate / backbone

只有 F1–F5 主机制成立后，再扩展 ALFWorld/WebShop/coding workflow/SkillEvolBench 中的一个，以及一个不同能力等级 backbone。第二 substrate 的职责是证明机制不只存在于 spreadsheet，不负责救主结论。

## 7. 数据分层与统计设计

### 7.1 四个完全分离的角色

1. **Runtime development pool**：只验证工具、checkpoint、provider、scorer；永不进入科学 claim；
2. **Mechanism calibration pool**：估计 `p_z`、`delta_z`；
3. **Evolution train + validation gate**：产生/选择 skill update；
4. **Held-out probe/final test**：从不送入 updater。

尽可能按 workbook/source/template/failure-family group-disjoint，而不是行级随机切分。

### 7.2 Scientific unit

主 scientific unit 是 one independently seeded complete evolution stream / learned skill state，不是 individual rollout、task repeat、LLM call 或 endpoint row。

### 7.3 Pairing

- 同一 task stream；
- 相同 initial skill SHA；
- 相同 candidate seed index；
- H/H 与 H/projection arms 在 one-step experiment 中共享 exact K-pool；
- longitudinal 中记录 skill divergence，不能假装后续 pools 仍完全相同。

### 7.4 Primary estimands

1. Acting gain：
   \[
   \Delta_A=A_H-A_L.
   \]
2. Winner-only shielding reversal：
   \[
   \Delta_S=J(S_L)-J(S_{H/win}).
   \]
3. Projection rescue：
   \[
   \Delta_P=J(S_{H/CADP})-J(S_{H/win}).
   \]
4. Causal one-step projection effect：
   \[
   \Delta_{clone}=J(U(S,g_{CADP}(T)))-J(U(S,g_{win}(T))).
   \]
5. Topology×projection interaction。

### 7.5 Statistical model

对 binary success 使用 paired hierarchical logistic model，random effects 至少覆盖 evolution stream seed、task/template、failure family；扩展阶段再加入 model/backbone。

同时报告 paired bootstrap CI、run-level effect distribution、AULC（frozen learning curve area）、final frozen score、prospective sign/rank prediction accuracy。

不得把 K 个 rollouts 当作 K 个 independent scientific n。

## 8. Validators

1. **Pool Identity Validator**：one-step clone arms 使用 exact same K-pool hashes；
2. **Projection Validator**：updater input 与预注册 `g(T)` 完全一致；
3. **Acting Invariance Validator**：所有 high-K projection arms serve exact same winner；
4. **No-extra-actor-compute Validator**：precommitted/rejected/contrast 只使用已生成 pool；
5. **Evidence-Budget Validator**：对比 packet 与 token-matched controls；
6. **Failure-Family Validator**：controlled suite 使用 deterministic executable labels；
7. **Skill Leakage Validator**：patch 不得含 task id、cell-specific answer、workbook filename 等 instance facts；
8. **Held-Out Gate Validator**：selection/test tasks 永不进入 updater；
9. **Frozen-Eval Validator**：所有 arms 同 backbone、K=1、temperature、tool harness；
10. **Scientific-Unit Validator**：统计 n 为 independent evolution streams；
11. **Checkpoint Validator**：每 rollout、pool selection、projection packet、skill patch、validation decision、final skill hash 均落 CSV/JSONL；
12. **Resume Validator**：只执行 missing units。

## 9. Kill / downgrade rules

### Kill central thesis

- qualified substrate 上 high-K 无 acting gain；
- winner-only 未降低 diagnostic coverage；
- cloned-state projection intervention 对 future skill 无方向性影响；
- multi-round H/H frozen skill 不弱于 L/L，且 planned replication 一致；
- CADP 不恢复，或恢复来自额外 actor/updater budget；
- prospective risk score 不能预测 held-out regime；
- effect 只在 outcome-selected task subset 出现。

### Downgrade stronger claims

- rejected-witness 与 precommitted/CADP 完全相同：保留“winner-only wastes existing pool evidence”，删除“需要 counterfactual low-C branch”；
- random pair 与 contrast packet 相同：删除“outcome-grounded divergence”机制，只保留“more diverse evidence”；
- winner+duplicate 追平 CADP：删除 diagnostic contrast claim，归因为 updater context budget；
- sequential full-history 与 winner-only 无差异：删除 topology×projection claim；
- failure witness 比 winner 的 diagnostic advantage `delta<=0`：该 family 属于 search-improves-learning regime，不为主 thesis 强行解释。

## 10. 论文主线

### Hook

Test-time scaling 让 agent 通过搜索更多候选并部署更好的结果。Self-evolving agents 又把执行轨迹当作未来 skill 的训练数据。这里存在一个被忽略的假设：

> the trajectory worth serving is also the trajectory worth learning from.

### Phenomenon

best-of-K winner selection 提高 online success，但 winner-only learner 只看到最终被服务的成功轨迹。

### Insight

Search 产生一个 richer object，acting 与 learning 是两个不同 projection。把二者绑定造成 outcome-dependent censoring。

### Law

在 binary verifier 下：

\[
\text{online gain}=\text{single-rollout failure visibility loss}=\Gamma_K(p),
\]

且该 loss 在 intermediate difficulty 最大。

### Mechanism

真正的长期 harm 由：

\[
\Gamma_K(p_z)\times\delta_z
\]

决定：censoring mass 与被 censor evidence 的 reusable value 缺一不可。

### Causal test

同一个 K-pool、同一个 acting winner、同一个 initial skill，只改变 learning projection；随后 common K=1 frozen evaluation。

### Solution

CADP：act from winner；在 mixed search groups 中 learn from winner–failure divergence；bounded patch + held-out gate；不增加 actor rollouts。

### Engineering implication

生产 self-evolving agent 不应只持久化“给用户看到的最终成功轨迹”。Search logs 是 learning substrate，serving policy 与 logging/learning policy 必须解耦。

## 11. 推荐主图

1. **Figure 1 — Dual Projection**：同一 search pool 分成 acting winner 与 learning evidence；winner-only 删除失败分支；
2. **Figure 2 — Rescue–Censoring Law**：`Gamma_K(p)` 随 difficulty/K 的曲线和 `p*(K)`；
3. **Figure 3 — Cloned-State Causal Intervention**：exact same pool，不同 `g(T)`，不同 frozen skill；
4. **Figure 4 — Online/Frozen Reversal**：H/H online 高、frozen learning 曲线低，CADP 同时保留两者；
5. **Figure 5 — Mechanism Prediction**：`Gamma×delta` 对 held-out skill deficit 的预测/校准；
6. **Figure 6 — Method Ablation**：winner-only、duplicate、random、witness、contrast、full-pool 在 fixed budget 下比较。

## 12. Contributions（通过全部 gate 后才允许使用）

1. **Search-to-learning projection formulation**：把 test-time search 明确建模为同时服务 acting 与 persistent learning 的数据生成过程；
2. **Rescue–Censoring Identity and regime law**：给出 online gain 与 winner-only failure visibility loss 的精确关系，以及 intermediate-difficulty peak；
3. **Causal projection evidence**：在 exact same search pools 上只改变 learning projection，证明 winner-only selection 可导致更弱的 persistent skill；
4. **Prospective mechanism prediction**：用 censoring mass × diagnostic advantage 预测 unseen regimes；
5. **CADP**：不增加 actor rollout 的 dual-channel projection，通过 bounded validation-gated skill patches 保留 high-compute acting 与 persistent learning。

## 13. 与当前 F0-R2 / R3 的关系

### 保留

- K=1/K=4 best-of-K；
- MindMemOS + SpreadsheetBench；
- winner-only、precommitted rollout-0、rejected branch；
- frozen K=1 evaluation；
- exact checkpoint/receipt；
- 8-train/8-eval 作为 runtime pilot。

### 修改（须在 provider 恢复前另行生成正式 R4 contract；本文不授权）

- scientific object 从 generic Compute Shielding 改为 Search-Projection Censoring；
- `H/L-shadow` 明确为 same-pool precommitted rollout-0，不是额外 independent call；
- `H/H-hardmine` 改名 `H/Rejected-Witness`；
- 增加 controlled procedure suite；
- 增加 cloned-state one-step causal intervention；
- 增加 `Gamma×delta` prospective prediction；
- contrastive CADP 仅在主机制 gate 后执行；
- multi-round 才是最终 paper evidence，single update 不承担 headline claim。

### 不做

- 不把 R17 塞回 R16 appendix；
- 不以“failure feedback 首次有用”为 novelty；
- 不以“首次利用 sibling rollouts”为 novelty；
- 不写 universal `compute hurts learning`；
- 不在 API 恢复前用 outcome 改 task/failure family；
- 不用更多 benchmark 掩盖主机制失败。

## 14. 关键参考文献（内部索引）

- Snell et al., 2024, `Scaling LLM Test-Time Compute Optimally Can Be More Effective than Scaling Model Parameters`, arXiv:2408.03314.
- Liu et al., 2026, `Rethinking Self-Evolving Agent Skills`, arXiv:2608.02636.
- Wang et al., 2026, `Rethinking the Evaluation of Harness Evolution for Agents`, arXiv:2607.12227.
- Djuhera et al., 2026, `TSR: Trajectory-Search Rollouts for Multi-Turn RL of LLM Agents`, arXiv:2602.11767.
- Liang et al., 2026, `Search-E1`, arXiv:2605.22511.
- Meng & Chen, 2026, `CRAFT`, arXiv:2606.29476.
- Ding et al., 2026, `Sibling-Guided Credit Distillation`, arXiv:2606.12634.
- Xia et al., 2026, `Outcome-Verified Comparative Self-Distillation`, arXiv:2607.27937.
- Shi et al., 2026, `SKILL-KD`, arXiv:2607.28048.
- Yang et al., 2026, `SkillOpt`, arXiv:2605.23904.
- Wang et al., 2026, `Do Not Waste Your Rollouts`, arXiv:2601.21684.
- Zhou, 2026, `When RLVR Shrinks the Reasoning Boundary`, arXiv:2607.20543.
- Zhang et al., 2026, `On-Policy Distillation with Best-of-N Teacher Rollout Selection`, arXiv:2605.09725.
- Perdomo et al., 2020, `Performative Prediction`, arXiv:2002.06673.
- Ross et al., 2011, `DAgger`, arXiv:1011.0686.
- De-Arteaga et al., 2018, `Learning under selective labels...`, arXiv:1807.00905.
