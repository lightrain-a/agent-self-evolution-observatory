# Agent Constraint Externality — SkillZip / SkillZip Pro informed paper iteration

Date: 2026-09-04
Scientific object: `AGENT-CONSTRAINT-EXTERNALITY-20260831`

This note transfers the reusable lessons from the existing **SkillZip & SkillZip Pro** notes into the current Agent Constraint Externality paper. It changes the paper program and writing architecture only; it grants no experimental authority.

## 1. 科研方法论与后续启发

### 1.1 先验证现象，再解释机制，最后才提出方法

SkillZip/Pro 最重要的可迁移原则不是某个具体算法，而是 **phenomenon first, minimum method second**。当前对象已经有一个很强的 same-update topology identification design，但如果正文一上来就讲 topology mechanism，会像“先有机制、再找现象”。新的论文弧应改成：

1. **Phenomenon**：target-only persistent repair 在改善 target 的同时，是否真的会制造 update-attributable non-target regression？
2. **Mechanism**：如果有 externality，它是否随 outcome-blind resource/prerequisite coupling topology 系统变化？
3. **Prediction**：只用 outcome 前冻结的 topology exposure，能否 prospectively 预测哪些 fresh families 风险更高？
4. **Minimum mitigation**：只有前三步成立，才引入最简单的 topology-aware collateral-check gate；不先做 learned controller。

### 1.2 把 capability、source-failure availability、mechanism 分成三个独立 gate

当前实际执行已经给出一个重要方法论证据：

- `mimo-v2.5-pro` 在 disjoint capability panel 上通过：target success `0.875`、tool-loop completion `0.875`、non-target preservation `1.0`。
- 但旧 F0 source stage 的 8 个 families 全部 target success：`8/8`，因此 `0` target failures、`0` eligible repair families、`0` probe outcomes。
- 这不是 topology mechanism 的负结果，而是 **source-failure substrate unavailable**。

因此以后必须显式区分：

`Capability PASS` ≠ `repairable source failures exist` ≠ `externality exists` ≠ `topology causes externality`。

这比简单“先做 pilot”更严格：每个 gate 都回答不同 identification question，失败时不能越级解释。

### 1.3 失败要按层分类，不能把执行问题写成科学负结果

延续 SkillZip/Pro 的 failure taxonomy：

- implementation/runtime failure
- provider/transport failure
- measurement failure
- protocol failure
- identifiability failure
- source-substrate failure
- scientific mechanism failure

当前历史中，AtomCode native `read_file` contamination 属于 transport/harness invalidity；AA `insufficient_credit` 属于 provider availability；8/8 source success 属于 source-substrate failure。三者都不能写成“constraint coupling 不成立”。

### 1.4 方法必须从结果自然产生，而且保持最小

如果 RQ1–RQ3 最终支持 topology mechanism，优先采用一个无学习器的最小 safeguard：

**Graph-Targeted Collateral Check (GTCC)**

- update 仍由原 target failure 生成；
- 在 commit 前，根据 outcome-blind resource/prerequisite graph 选择离 target 最近或 exposure 最高的 `k` 个 non-target constraints；
- 对这些 constraints 做 matched UPDATE / NO_UPDATE collateral checks；
- 只有 target repair positive 且 sampled collateral checks 无新增 regression 时才 commit。

最强公平 baseline：

- Always Commit
- Target-Only Validation
- Random-k Collateral Check（同 probe budget）
- Full Non-target Check（oracle / upper bound，不作为同成本 baseline）

如果 `Random-k` 已和 GTCC 等价，则不再发展复杂 topology controller；如果简单 nearest-k 已足够，也不引入 learned risk model。

## 2. 实验设计拆解

### Gate 0 — Runtime / protocol qualification（非论文结果）

目标：确认 actor、AppWorld、evaluator、exactly-once ledger、provider transport 都可解释。

当前经验必须继承：checkpoint-first；每次 dispatch、tool loop、world state、evaluation 立即 durable 落盘；missing-unit 只能按冻结 authority resume；unknown-after-dispatch 不自动 replay。

### Gate 1 — Source-Failure Qualification（非机制结果）

目标：证明 selected actor 在 fresh cases 上能产生 **正常终止、语义性的、可完整测量的 target failures**，而不是 tool-cap / harness / provider failures。

当前 prospective object：`DIRECT-SFQ-A0`。

已完成静态资格：

- 12 fresh cases = 6 FG + 6 TNF
- public oracle 12/12 reachable
- max public oracle calls = 48 / 80
- minimum headroom = 32
- vs SQ0 V1–V5 + old F0：case ID / instruction / fixture / target-resource hash overlap 全部 0
- execution remains blocked until a clean direct-provider capability pass and provider credit recovery

### RQ1 — Phenomenon: local repair externality 是否存在？

在 confirmatory matched families 中同时报告：

- Target Repair Gain
- `UE_z = CRR_UPDATE,z - CRR_NO_UPDATE,z`
- pooled update-attributable collateral regression across topology arms

RQ1 先问：**target 真的修好了时，是否有 previously satisfied non-target constraints 因 update 新坏掉？**

不能先用 `UE_HIGH - UE_INDEPENDENT` 代替 phenomenon 本身。

### RQ2 — Mechanism: coupling topology 是否因果调节 externality？

核心 identification 保留现有最强设计：

- exact same repair bytes within family
- same actor / harness / snapshot / constraint count / instruction budget / difficulty / tools / target obligation
- only `INDEPENDENT / LOW / HIGH` outcome-blind coupling changes
- primary contrast: `UE_HIGH - UE_INDEPENDENT`
- ordered secondary prediction: `HIGH >= LOW >= INDEPENDENT`
- graph-distance / shared-resource exposure profile as mechanism localization

### RQ3 — Prospective prediction: outcome-blind topology 能否提前把风险排到前面？

不要给未来留下一个可调权重的“graph risk model”。更干净的是冻结一个 **parameter-free ExposureRank**，并且 RQ3 与后续方法共用同一个排序对象：

1. direct prerequisite / target-write→non-target-read-or-write edge 优先；
2. shared mutable-resource count 降序；
3. shortest prerequisite/resource path distance 升序；
4. stable constraint hash 只做 deterministic tie-break。

`k` 也不根据 outcome 调：只由未来允许的 probe budget 在执行前冻结。

在 **从未用于构造或调参的 fresh held-out families** 上，预注册检验：ExposureRank top-k 中的 update-attributable regressions 是否比同大小 random-k 更富集。若 top-k 没有 prospective enrichment，停止 topology-prediction claim，也不开 GTCC。

### RQ4 — Minimal mitigation: 同一个 ExposureRank 能否以同等 probe budget 降低 collateral regression？

GTCC 不再训练第二个 risk controller，也不根据 RQ3 outcome 重拟 ranking。它直接用 RQ3 冻结的 ExposureRank 选择 top-k non-target constraints，并从同一 pre-update snapshot 做 matched check；只有 target repair positive 且 selected checks 没有新增 update-attributable regression 时才 commit。

主方法实验应放在 public AppWorld confirmatory panel，并使用同成本 baseline：

- Always Commit
- Target-Only Validation
- Random-k Check（与 GTCC 同 probe budget）
- GTCC (frozen ExposureRank top-k)
- Full Non-target Check（oracle / upper bound，不算同成本 baseline）

主结果同时报：

- Average Target Success / Repair Gain
- Collateral Regression Rate
- commit rate
- net task success / utility（若有预冻结定义）
- paired gain + CI
- model/family heterogeneity

### RQ5 — Public benchmark × multi-model × longitudinal（claim expansion）

只有 RQ1–RQ4 通过后才扩：

1. 模型选择参考 AppWorld / tool-agent strongest published baselines，而不是“当前服务器/API 有什么”。
2. 用至少多个能力层级 actor 做 public benchmark main table。
3. 先跑 Pilot，再 Full；不直接铺大矩阵。
4. 如果要讲 persistent self-evolution，而不只是 single-update safety，再加 multi-round accumulation / recovery：连续多次 local repair 后，GTCC 是否仍保持 target gain 且抑制 accumulated collateral regression。

这一层属于 claim expansion，不应成为当前 provider blocker 下的前置工作。

### 2.6 从 SkillZip 的实验规模学习：机制证据与主结果不要混成一张表

现有 SkillZip 笔记里，原版不是只给一个 compression demo：主实验横跨 3 个 agent backbones × 3 个 benchmark，并把 No Skill / Human Skill / Evolved Skill / SkillReducer / SkillZip 放在同一主比较中；随后单独报告 compression overhead、cross-model transfer 和 16-round continual Zip-on-Write。SkillZip Pro 则进一步把问题拆成多个 RQ、held-out 主评估、生命周期/组件消融与 cross-model 检验。

对本项目应迁移的是这个“证据分工”，而不是照搬 benchmark 名称：

- **Controlled mechanism table**：matched AppWorld families，只回答 RQ1/RQ2——externality 是否存在、topology 是否因果调节；这里不追求 benchmark breadth。
- **Prospective prediction table**：untouched held-out families，只回答 RQ3——ExposureRank 是否真的在看 outcome 前把风险排到前面。
- **Public main table**：RQ1–RQ3 通过后再做多个能力层级 actor × mitigation baselines，回答 GTCC 的实际 target/collateral trade-off；这里必须同时报 target success、collateral rate、commit rate、paired gain/CI，而不是只报一个 overall success。
- **Cross-model table**：用不同 actor 检查 topology signal / GTCC 是否依赖单一模型；不把“换模型后仍 positive”当机制识别本身。
- **Longitudinal figure**：只有论文要扩成 persistent self-evolution claim 时才增加，检查 repeated local repairs 下 accumulated collateral regression，而不是把 single-update result 强行叫 long-term evolution。
- **Efficiency table**：把额外 probe 数、LLM requests、wall-clock 与 Full Non-target Check 的 upper bound 分开；Random-k 必须与 GTCC 同 probe budget，避免方法通过多花预算获胜。

这会形成和 SkillZip 类似的清晰分工：**机制实验回答 why，public main table 回答 how much，cross-model 回答 breadth，longitudinal 回答 persistence，efficiency 回答 cost**。

### 2.7 对照 SkillZip Pro / SkillOpt / SkillRevise 后的工作量裁定

不能简单以“模型×benchmark cell 数”判断论文是否够大。三个近邻工作的实验规模对应不同 claim：

- **SkillZip Pro** 是窄而深的 production-object/system paper：核心围绕 production content-moderation skill、industrial multi-round harness、multi-entry bundle、routing fidelity、protected-vs-unprotected failure、Persistent/Transient 与 One-Shot/Continual 生命周期，以及 end-to-end token/cost accounting。它不是靠大量 benchmark cells 证明价值，而是让每个实验直接验证一个 execution contract。
- **SkillRevise** 的 claim 是可泛化 skill revision，所以铺 `3 benchmarks × 5 LLMs`，并做 cross-model transfer。
- **SkillOpt** 的 claim 更宽，是通用 text-space skill optimizer，因此覆盖 `6 benchmarks × 7 target models × 3 harnesses`、共 52 evaluation cells，并与 Human / one-shot / Trace2Skill / TextGrad / GEPA / EvoSkill 等比较。

本项目更接近“机制识别 + system safeguard”，不应照 SkillOpt 堆 52 cells；但目前也不能只靠原来的 8-family F0。当前大量历史执行是 qualification / transport archaeology，不等于 submission-level scientific evidence。

建议的 **minimum sufficient** 主证据不能理解成“必须跑满多少条”，而应理解成**逐层证据上限 + 预冻结 reserve**：

1. **Primary mechanism**：预先生成 `24` 个 fresh candidate families，但不默认全部进入主实验。family eligibility 只由 collateral outcome 前的 valid semantic source failure、repair artifact validity 和 positive target-only repair uptake 决定。再用独立 development-only stability/variance pilot，在任何 confirmatory collateral outcome 前冻结 `N* ∈ {12,16,20,24}` 和 `R* ∈ {2,3}`；按稳定 hash 顺序取前 `N*` 个 eligible families。默认高效目标是 `N*=16,R*=2`（192 probes），绝对上限才是 432 probes。reserve 只能为预声明 eligibility attrition 启用，不能因为效果弱或接近显著性而补样本。
2. **SHAM semantic control**：在主 panel 里事前指定一个 balanced subset（默认 8 families），加入与 real repair 同 persistent surface、近似长度/格式匹配但不含 target-specific action rule 的 `SHAM_UPDATE`。只跑 INDEPENDENT/HIGH 两个 topology extremes。它专门排除“只是多了一段 persistent context/text”这一 strongest alternative；默认 `8×2 topology×2 repeats=32` episodes，比再加一个随意模型的信息密度更高。
3. **Prospective prediction**：预生成 `16` 个 untouched candidates，预冻结 `H*∈{12,16}`；默认 `12×2 branches×R*=2=48` probes，绝对上限 96。Random / Same-App / resource-only / distance-only / ExposureRank 都在同一 held-out outcome 上离线比较，不能为每个 ranking 重跑 Agent。
4. **Mitigation**：只有 RQ1–RQ3 通过才打开。预生成 16 candidates，预冻结 `M*∈{8,12,16}`；默认 `M*=12,R*=2`，即 `12×5 policies×2=120` policy episodes，绝对上限 240。Always / Target-only / Random-k / Same-App-k / GTCC 每个 baseline 必须回答不同替代解释；Full Check 只在约 6 个预冻结 families 作 upper bound。若 GTCC 与 Random-k 在事前 practical margin 内等价，停止方法 claim。
5. **Cross-model**：不再预设“必须 2 个额外模型”。主机制成立后先用 **1 个**额外 capability-qualified actor，在 8-family stratified subset 上复核 RQ1/RQ2；默认约 96 episodes。只有第一次 replication 留下会改变 claim scope 的实质 model-dependence ambiguity，才打开第二个 actor。
6. **Existing-method external validity（高价值可选）**：与其再加第四第五个模型，更值得把一个 AppWorld-compatible 现有 updater（首选 ACE）输出 freeze 后，做约 6–8 fresh families 的 same-update collateral audit。它是 plug-in/generalization，不进入主 causal baseline 表。
7. **Longitudinal（条件性）**：只有要把 claim 扩成 repeated self-evolution 时才增加；它回答 accumulated externality，不是为了让实验表更长。

这里有两个硬规则：

- **重复次数不能机械固定为 3。** 先用完全独立、永不进入 confirmatory 的 development families 做 stability qualification；如果冻结判据显示 2 repeats 已稳定，就不用第 3 次。
- **扩样不能看 treatment direction。** `N* / R* / H* / M*` 的冻结只能依据事前 meaningful-effect / precision 目标、development variance、eligibility attrition、missingness 等 nuisance quantities，不能因为 p-value、effect sign 或“差一点过线”临时增加。

因此当前结论应写成：**实验逻辑已经够，但 submission-ready 有效主科学证据还不够；下一步缺的是高信息密度的 confirmatory outcomes，而不是目标 episode 数。** 每跑一条实验都必须能回答一个预先写清楚的 claim、confound 或 robustness question；否则不跑。

### 2.8 Baseline 不能混淆“因果对照”和“现有方法”

RQ1/RQ2 的最重要 baseline 不是某个 fancy memory algorithm，而是：

- same-snapshot `NO_UPDATE`：证明 regression 可归因于 update；
- exact-same-repair `INDEPENDENT` topology：证明 HIGH-vs-I 是 topology effect；
- LOW：检验 ordered dose-response。

RQ4 才进入方法 baseline：

- Always Commit
- Target-Only Validation
- Random-k Collateral Check（同 probe budget）
- Same-App-k（粗粒度 locality heuristic）
- GTCC
- Full Non-target Check（oracle / upper bound，不算同成本 baseline）

ACE / SkillOpt / SkillRevise / Memory-R1 等会改变 update writer、acceptance policy 或 memory semantics，因此直接放进 RQ2 主表会破坏 exact-same-update identification。最合理的用法是选一个兼容 updater 做 supporting plug-in test，而不是把“不公平方法大乱斗”当 baseline 丰富度。

## 3. 写作架构学习

### 3.1 Working title / 核心矛盾

建议 working title：

**Do Local Repairs Stay Local? Constraint-Coupled Externalities in Self-Evolving Agents**

一句话矛盾：

> A repair can be target-local in intent but non-local in effect because agent tasks share mutable state, APIs, and prerequisites.

不要把“constraint coupling”本身当 novelty，也不要把“memory update 会有副作用”当 novelty。论文守的是 **exact-same-update × matched topology × previously-satisfied non-target regression** 这一 treatment-level identification。

### 3.2 Introduction 的推荐顺序

1. **Agent 当前怎么自我修复**：memory / skill / workflow patch 是低成本 persistent update。
2. **默认评价有什么盲点**：target pass 不代表整个 system state 仍然健康。
3. **关键 mismatch**：local intent ≠ local effect。
4. **为什么现有工作不够**：已有 update regression、memory management、constraint coupling、graph repair，但没有 exact-same-update topology causal test。
5. **我们怎么回答**：先测 phenomenon，再同 update 操纵 topology，再做 prospective prediction。
6. **方法自然产生**：只有机制成立后，用 graph-targeted collateral checks 做最小 safeguard。
7. **贡献只绑定证据**：任何尚未执行的 RQ 用 future/pending 表述，不写成 finding。

### 3.3 正文结构

1. Introduction
2. Background & Problem: Persistent Local Repairs and Hidden Externalities
3. Experimental Object and Failure Qualification
4. RQ1 — Does a Local Repair Create Collateral Regression?
5. RQ2 — Does Constraint Coupling Cause the Externality?
6. RQ3 — Can Topology Predict Risk Prospectively?
7. Graph-Targeted Collateral Check
8. RQ4 — Public AppWorld Main Results
9. Cross-model / Longitudinal Analysis（只有 claim expansion 后）
10. Related Work
11. Limitations & Conclusion

资格化、transport archaeology、provider credit、旧 void runs 不放主故事；它们进 appendix / reproducibility ledger。

### 3.4 图表顺序

- **Figure 1**：一个真实感强的 local-repair → shared state → collateral regression 例子；旁边直接画 same-update INDEPENDENT/LOW/HIGH intervention。
- **Table 1 / Main Table**：public AppWorld × multi-model × mitigation baselines；同时显示 target gain 与 collateral harm，不能只报 overall success。
- **Figure 2**：phenomenon + topology dose response (`UE` by coupling level)。
- **Figure 3**：graph distance / shared-resource exposure vs collateral regression。
- **Table 2**：parameter-free ExposureRank 的 prospective top-k enrichment；同 k random ranking 为对照。
- **Table 3 / Ablation**：Random-k vs GTCC、预冻结 k sensitivity、去掉 topology ranking、source-failure categories。
- **Figure 4（可选）**：multi-round accumulated collateral regression。

### 3.5 Reviewer-facing claim ladder

正文按下面的证据层级写，不跳级：

`valid source failure` → `positive target repair` → `collateral phenomenon` → `topology causal contrast` → `prospective prediction` → `minimal mitigation` → `cross-model / longitudinal generalization`

任何一层失败，都只收窄后续 claim；不靠换 family、改阈值或只挑正例把故事“救回来”。尤其 RQ3 若不通过，就不允许另训一个 risk model 来挽救 GTCC。

## 4. 2026-09-04 最新公开工作 pressure-test

这次重新核对最新公开工作后，必须进一步收窄 novelty：

- **How Memory Management Impacts LLM Agents**（ACL 2026）已经系统报告 experience-following、error propagation 与 misaligned experience replay。因此本项目不能声称首次发现“agent memory 会把错误传播到未来”。
- **Useful Memories Become Faulty When Continuously Updated by LLMs**（arXiv:2605.12978）已经展示 continuous memory consolidation 甚至会让原本有用的经验变坏。因此“持续更新可能退化”也不能作为本项目 novelty。
- SkillZip / SkillZip Pro（arXiv:2608.11079 / 2608.30785）进一步说明 self-evolving skill 的结构契约、rare-route preservation 与最低复杂度方法本身已经成为强设计范式。

所以本项目真正需要守住的是更窄的 residual：

**positive target repair × previously-satisfied non-target regression × exact-same-update matched topology × outcome-blind prospective structural prediction**。

如果最终只能证明 generic memory degradation，而不能证明这组 treatment-level 结构差异，就应该 PIVOT/STOP，而不是把已有现象重新命名。

## 5. 本轮论文对象

已经据此建立 ICLR working draft：

`paper_drafts/agent-constraint-externality-iclr2027/`

核心文件：

- `main.tex`：8 页 working manuscript；所有 externality / topology / GTCC 结果均保持 prospective wording。
- `MAINLINE_BRIEF.md`：一句话对象、claim ladder、当前证据、RQ 与 novelty boundary。
- `references.bib`：AppWorld、ACL 2026 memory management、continuous-memory degradation、SkillZip、SkillZip Pro。
- `main.pdf`：当前可编译快照。

正文当前顺序固定为：**对象错配 → 分层 gate → RQ1 phenomenon → RQ2 mechanism → RQ3 prospective prediction → conditional GTCC → public/multi-model/longitudinal claim expansion**。
