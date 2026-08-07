from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "idea-discovery-v5.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "idea-discovery-v5.js"
DEFAULT_EXTERNAL_JSON = PROJECT_ROOT / "generated" / "idea-discovery-v5-external-reviews.json"


def bi(zh: str, en: str) -> dict[str, str]:
    return {"zh": zh.strip(), "en": en.strip()}


REPOSITORY_PATTERNS = (
    ("HypoGeniC / HypoRefine", "https://github.com/ChicagoHAI/hypothesis-generation", "data-literature-union", "联合真实数据失败模式与文献假设，而不是只从论文空白生成问题。", "Union empirical failure evidence with literature hypotheses rather than relying on literature gaps alone."),
    ("IdeaForge", "https://github.com/makemebitter/ideaforge", "adversarial-proposer-critic-judge", "让 Proposer、Critic 与 Judge 对抗，主动寻找可被标准方法替代的弱方案。", "Use proposer-critic-judge adversarial debate to expose ideas reducible to standard methods."),
    ("ScholarEval", "https://github.com/skai-research/ScholarEval", "literature-grounded-rubric", "用可操作性、证据深度和文献支撑等多维 rubric 审查 Idea。", "Review ideas with literature-grounded rubrics for actionability, depth, and evidential support."),
    ("InnoEval", "https://github.com/zjunlp/InnoEval", "knowledge-grounded-multiperspective", "把 Idea 评价建模为知识约束、多视角推理，而不是单一新颖性分数。", "Treat idea evaluation as knowledge-grounded multi-perspective reasoning rather than one novelty score."),
    ("SciAtlas", "https://github.com/zjunlp/SciAtlas", "scientific-kg-neighborhood", "从科学知识图谱的邻域和桥接关系检索机制，不只做标题相似度搜索。", "Retrieve mechanism neighborhoods and bridge relations from a scientific knowledge graph."),
    ("InternAgent", "https://github.com/InternScience/InternAgent", "long-horizon-algorithm-discovery", "把长程记忆、算法发现和复现实验纳入持续研究循环。", "Integrate long-horizon memory, algorithm discovery, and reproduction into the research loop."),
    ("AutoScientists", "https://github.com/mims-harvard/AutoScientists", "self-organizing-research-teams", "让不同研究角色自组织并长期运行，避免单一 Agent 的搜索偏置。", "Use self-organizing research teams to reduce single-agent search bias over long runs."),
    ("AutoResearchClaw", "https://github.com/aiming-lab/AutoResearchClaw", "collider-pivot-state-reuse", "保留失败实验状态，继续 collider 或显式 pivot，而不是每轮从零生成 Idea。", "Reuse failed experiment state through collider continuation or explicit pivot instead of restarting ideation."),
    ("autoresearch", "https://github.com/karpathy/autoresearch", "microexperiment-keep-revert", "固定小实验预算，改动后只根据独立指标 keep/revert。", "Use fixed-budget micro-experiments and keep/revert decisions under an independent metric."),
    ("Virtual Scientists", "https://github.com/open-sciencelab/Virtual-Scientists", "team-diversity-topology", "利用新鲜团队、跨团队讨论和不同角色拓扑扩大 Idea 多样性。", "Increase idea diversity through fresh teams, inter-team discussion, and role topology."),
    ("ResearchAgent", "https://github.com/JinheonBaek/ResearchAgent", "low-score-dimension-repair", "只修 Reviewer 低分维度并保留历史。", "Repair low-scoring reviewer dimensions while preserving history."),
    ("AI Scientist-v2", "https://github.com/SakanaAI/AI-Scientist-v2", "agentic-tree-search", "保留多个方法与实验分支，用实验经理做渐进式树搜索。", "Preserve multiple method and experiment branches with progressive agentic tree search."),
    ("ResearchHarness", "https://github.com/InternScience/ResearchHarness", "frozen-harness-comparison", "冻结评测 Harness 和预算，避免 Idea 通过改变测试方式获得优势。", "Freeze the evaluation harness and budget so ideas cannot win by changing evaluation."),
)

WORKFLOW_STAGES = (
    ("E", "经验与文献三角化", "Evidence triangulation", "失败日志、实验结果、论文局限和 Reviewer objection 被归一为同一个 problem capsule。", "Normalize failure logs, experiment outcomes, paper limitations, and reviewer objections into one problem capsule."),
    ("M", "机制邻域扩展", "Mechanism-neighborhood expansion", "从文献图谱、跨领域方法和已有代码中检索可迁移机制。", "Retrieve transportable mechanisms from literature graphs, adjacent domains, and existing code."),
    ("T", "多团队分支生成", "Multi-team branch generation", "独立 proposer 团队分别生成机制、监督、更新表面和实验分支。", "Independent proposer teams generate mechanism, supervision, update-surface, and experiment branches."),
    ("A", "对抗式简化挑战", "Adversarial simplification challenge", "Critic 必须提出更简单的容量匹配替代方案；若能复现则候选降级。", "Critics must propose simpler capacity-matched alternatives; reproducible ideas are demoted."),
    ("C", "组合必要性判定", "Combination necessity", "允许合理组合，但要求每个组件对应独立失败路径且删除后性能下降。", "Allow combinations only when each component closes a distinct failure path and deletion degrades performance."),
    ("R", "复活与合并", "Revival and merge", "旧 REVISE/BLOCK 在关键假设、学习对象或监督闭环变化后重新进入。", "Revive prior REVISE/BLOCK branches after material changes to assumptions, learned objects, or supervision."),
    ("X", "微实验 keep/revert", "Micro-experiment keep/revert", "优先设计 1–6 小时现象实验，结果可直接改变 Idea 排名与分支。", "Use 1–6 hour phenomenon tests whose results directly change ranking and branching."),
    ("J", "知识约束多视角审查", "Knowledge-grounded multi-perspective review", "分别审查真实问题、机制必要性、独立监督、泛化、成本和论文叙事。", "Separately review problem reality, mechanism necessity, independent supervision, transfer, cost, and thesis clarity."),
    ("F", "失败反馈再组合", "Failure-feedback recombination", "REVISE 生成定向 child；BLOCK 保留为组件或复活源，不永久删除。", "Generate targeted children from REVISE; retain BLOCK as components or revival sources rather than deleting them."),
)


def candidate(
    id: str, zh: str, en: str, status: str, problem: tuple[str,str], mechanism: tuple[str,str], surface: str,
    signal: tuple[str,str], truth: tuple[str,str], baseline: tuple[str,str], pilot: tuple[str,str], stop: tuple[str,str],
    parents: tuple[str, ...], components: tuple[str, ...], necessity: tuple[str,str],
    sources: tuple[str, ...], score: tuple[int, int, int, int, int, int], revival: tuple[str,str] | None = None,
) -> dict[str, Any]:
    keys = ("problem_reality", "mechanism_strength", "identifiability", "transfer", "feasibility", "discussion_value")
    return {
        "id": id, "title": bi(zh, en), "internal_status": status,
        "problem": bi(problem[0], problem[1]), "exact_mechanism": bi(mechanism[0], mechanism[1]),
        "update_surface": surface, "learning_signal": bi(signal[0], signal[1]), "independent_ground_truth": bi(truth[0], truth[1]),
        "strongest_baseline": bi(baseline[0], baseline[1]), "decisive_pilot": bi(pilot[0], pilot[1]), "stop_condition": bi(stop[0], stop[1]),
        "parent_ids": list(parents), "components": list(components), "necessity_logic": bi(necessity[0], necessity[1]),
        "repository_patterns": list(sources), "revival_condition": bi(revival[0], revival[1]) if revival else None,
        "scores": dict(zip(keys, score, strict=True)), "mean_score": round(sum(score) / len(score), 3),
        "external_review_status": "pending", "external_verdict": "pending",
    }


CANDIDATES: list[dict[str, Any]] = []

CANDIDATES += [
    candidate("effect-bifurcation-memory-learner","经验效应分叉学习","Experience-Effect Bifurcation Learner","finalist",
      ("同一经验对不同任务子群可能产生相反的未来效应，统一保留或删除都会出错。","One experience can have opposite future effects across task subpopulations, so global keep/delete decisions are unsafe."),
      ("用随机化重放估计异质处理效应；出现多峰或符号冲突时，把经验分裂成带不同适用条件的子经验并冻结分裂规则。","Estimate heterogeneous treatment effects with randomized replay; split a memory into applicability-bounded descendants when effects are multimodal or sign-conflicted, then freeze the split rules."),
      "versioned experience memory with descendant lineage",
      ("经验写入/不写入的随机化未来效应。","Randomized future effects of writing versus withholding the experience."),
      ("时间留出任务中的子经验帮助/伤害效应。","Benefit/harm effects of descendants on chronologically held-out tasks."),
      ("统一经验、语义聚类分裂、上下文门控、A-MAC 类准入。","Unspecialized memory, semantic-cluster splitting, contextual gating, and A-MAC-style admission."),
      ("两个任务域中构造效应符号异质经验，比较未来负迁移、正收益和分裂复杂度。","Create sign-heterogeneous experiences in two domains and compare future negative transfer, positive gain, and split complexity."),
      ("未见任务子群上不能降低负迁移，或语义聚类同样有效则停止。","Stop if negative transfer does not fall on unseen subgroups or semantic clustering is equally effective."),
      ("contradiction-preserving-memory-consolidation",),("randomized-effect-estimation","applicability-specialization"),
      ("异质效应决定何时分叉，适用条件学习决定如何分叉；两者缺一不可。","Effect heterogeneity decides when to split and applicability learning decides how; neither alone closes the failure loop."),
      ("data-literature-union","adversarial-proposer-critic-judge"),(5,5,5,4,4,5)),
    candidate("effect-equivalence-memory-compactor","效应等价记忆压缩器","Effect-Equivalence Memory Compactor","finalist",
      ("长期自进化会积累语义不同但行为作用等价的经验，造成上下文膨胀和冲突。","Long-running evolution accumulates semantically different memories with behaviorally equivalent effects, causing context bloat and conflicts."),
      ("用跨任务干预效应签名而非文本相似度判断可合并性，只合并效应向量和适用边界等价的经验，并保留可逆来源映射。","Use cross-task intervention-effect signatures instead of text similarity; merge only memories equivalent in effect and applicability while preserving reversible provenance."),
      "effect-equivalence memory DAG",
      ("条目级跨任务干预效应向量和容量压力。","Entry-level cross-task intervention-effect vectors and memory-capacity pressure."),
      ("冻结后的任务成功、回归和检索成本。","Frozen downstream success, regression, and retrieval cost."),
      ("语义去重、摘要压缩、LRU、全部保留。","Semantic deduplication, summary compression, LRU eviction, and keep-all."),
      ("持续任务流中匹配存储预算，比较压缩率、未来性能和错误合并回归。","Match memory budgets on continual task streams and compare compression, future performance, and regressions from false merges."),
      ("相同压缩率下不优于语义去重，或错误合并率过高则停止。","Stop if it does not beat semantic deduplication at the same compression rate or false merges are excessive."),
      ("contradiction-preserving-memory-consolidation",),("causal-effect-signatures","reversible-merge-compiler"),
      ("效应签名提供功能等价标准，合并编译器提供持久压缩。","Effect signatures define functional equivalence and the merge compiler provides persistent compression."),
      ("scientific-kg-neighborhood","microexperiment-keep-revert"),(5,5,5,4,4,5)),
    candidate("retrieval-order-clause-learner","检索顺序子句学习","Retrieval-Order Clause Learner","finalist",
      ("多条记忆各自有用，但检索顺序改变会导致规划冲突或错误覆盖。","Several memories may each be useful while retrieval order changes planning and causes destructive override."),
      ("随机化共同检索集合的排列，学习类型化 precedence/commutativity 子句，并在推理前约束排序。","Randomize permutations within co-retrieved sets, learn typed precedence/commutativity clauses, and constrain ordering before inference."),
      "memory-order constraint registry",
      ("同一记忆集合不同排列的环境结果。","Environment outcomes under different permutations of the same memory set."),
      ("未见记忆身份和高阶组合上的顺序效应。","Order effects on unseen memory identities and higher-order combinations."),
      ("时间顺序、相关度排序、Memory Interaction Clause Learner、随机顺序。","Chronological order, relevance sorting, Memory Interaction Clause Learner, and random order."),
      ("二元/三元组合训练，完整留出记忆身份测试排序泛化。","Train on pair/triple sets and hold out memory identities completely to test ordering transfer."),
      ("子句不能跨身份泛化，或简单相关度排序同样有效则停止。","Stop if clauses do not generalize across identities or simple relevance sorting is equally effective."),
      ("memory-interaction-clause-learner",),("co-retrieval-interventions","precedence-clause-induction"),
      ("干预识别顺序效应，子句学习把它变成未来可执行约束。","Interventions identify order effects and clause induction turns them into executable future constraints."),
      ("scientific-kg-neighborhood","low-score-dimension-repair"),(5,5,5,4,4,5)),
    candidate("cross-surface-update-transpiler","跨更新表面转译器","Cross-Surface Update Transpiler","finalist",
      ("同一修复可写入 Prompt、记忆、技能或工作流，但部署环境常只允许部分表面。","The same repair may live in prompt, memory, skill, or workflow, but deployments often permit only a subset of surfaces."),
      ("从行为等价的跨表面修复对学习类型化转译规则，把源表面更新转换为目标表面更新，并用冻结行为契约校验。","Learn typed translation rules from behavior-equivalent cross-surface repair pairs, transpile source updates into target surfaces, and validate with frozen behavioral contracts."),
      "versioned cross-surface update compiler",
      ("源/目标表面修复对、行为契约和失败签名。","Source/target repair pairs, behavioral contracts, and failure signatures."),
      ("未见故障和未见表面组合上的行为等价与回归。","Behavioral equivalence and regression on unseen failures and unseen surface pairs."),
      ("目标表面从零重写、Update-Surface Router、人工模板、直接复制文本。","Target-surface rewrite-from-scratch, Update-Surface Router, manual templates, and direct text copy."),
      ("冻结源修复后转译到两个目标表面，匹配模型调用比较修复成功和圈外回归。","Freeze source repairs and transpile them to two target surfaces under matched model calls; compare repair success and out-of-loop regression."),
      ("不优于目标表面从零重写，或跨模型失效则停止。","Stop if it does not beat target-surface rewrite-from-scratch or fails across models."),
      ("update-surface-router",),("behavioral-effect-matching","typed-surface-translation"),
      ("效应匹配提供跨表面监督，转译器产生可部署目标资产；路由本身不能解决表面不可用。","Effect matching supplies cross-surface supervision and the transpiler creates deployable target assets; routing alone cannot handle an unavailable surface."),
      ("long-horizon-algorithm-discovery","frozen-harness-comparison"),(5,5,5,5,3,5)),
]
CANDIDATES += [
    candidate("update-history-semantic-compactor","更新历史语义压缩器","Update-History Semantic Compactor","finalist",
      ("多轮 Prompt/记忆/工作流更新形成长版本链，重复约束和被覆盖规则增加冲突与维护成本。","Long prompt/memory/workflow version chains accumulate redundant and shadowed rules, increasing conflict and maintenance cost."),
      ("把版本链转成类型化行为约束图，用反事实重放识别被覆盖与等价更新，再编译为更短规范状态并保留回滚映射。","Convert version history into a typed behavioral-constraint graph, identify shadowed/equivalent updates with counterfactual replay, and compile a shorter canonical state with rollback mapping."),
      "canonicalized persistent update state",
      ("版本链、更新依赖和反事实重放结果。","Version history, update dependencies, and counterfactual replay outcomes."),
      ("规范化后冻结任务上的行为等价、回归和上下文成本。","Behavioral equivalence, regression, and context cost after canonicalization."),
      ("保留全部、文本摘要、最后版本、语义去重。","Keep-all, text summarization, last-version-only, and semantic deduplication."),
      ("构造 10–30 轮更新链，压缩到固定预算，测试圈外任务与回滚恢复。","Construct 10–30 round update histories, compress to a fixed budget, and test out-of-loop tasks plus rollback recovery."),
      ("显著压缩下不能保持行为，或回滚映射不可靠则停止。","Stop if behavior cannot be preserved under meaningful compression or rollback mapping is unreliable."),
      ("compositional-update-compatibility",),("version-effect-graph","canonical-compiler"),
      ("版本效应图识别可消去更新，规范编译器保证压缩后仍是可部署状态。","The version-effect graph identifies removable updates and the canonical compiler guarantees a deployable compressed state."),
      ("collider-pivot-state-reuse","microexperiment-keep-revert"),(5,5,5,4,4,5)),
    candidate("causal-update-garbage-collector","因果更新垃圾回收器","Causal Update Garbage Collector","finalist",
      ("旧更新可能已被后续更新完全覆盖，但系统仍长期携带它们并承担交互风险。","Old updates may be fully shadowed by later updates yet remain deployed and continue to create interaction risk."),
      ("周期性做预算受限的禁用干预，识别对留出能力无边际贡献的更新，并在安全证书通过后回收。","Perform budgeted disable interventions, identify updates with no marginal contribution to held-out capabilities, and garbage-collect them after a safety certificate passes."),
      "versioned update registry with tombstones",
      ("更新禁用干预、留出能力结果和依赖图。","Update-disable interventions, held-out capability outcomes, and dependency graph."),
      ("删除后的跨域能力保持和未来交互回归。","Cross-domain capability preservation and future interaction regression after deletion."),
      ("按年龄删除、最后使用时间、语义冗余、全部保留。","Age-based deletion, last-use, semantic redundancy, and keep-all."),
      ("在 12+ 轮版本链上固定干预预算，比较删除率、性能保持和未来冲突。","Use 12+ round version chains under a fixed intervention budget and compare deletion rate, performance preservation, and future conflicts."),
      ("删除率很低或跨模型出现不可接受回归则停止。","Stop if deletion rate is negligible or cross-model regressions are unacceptable."),
      ("memory-half-life","lineage-aware-rollback"),("causal-disable-testing","safe-deletion-certificate"),
      ("禁用干预给出边际贡献证据，删除证书避免把一次审计直接当动作。","Disable interventions provide marginal-contribution evidence and the deletion certificate prevents one audit from directly becoming an action."),
      ("microexperiment-keep-revert","frozen-harness-comparison"),(5,5,5,4,5,5)),
    candidate("residual-patch-transfer-operator","残差补丁迁移算子","Residual Patch Transfer Operator","finalist",
      ("逐实例最小补丁可修复当前更新，但无法复用于新的版本提交。","Per-instance minimal patches can fix the current update but do not transfer to new commits."),
      ("从失败更新及成功二次补丁中学习条件残差算子，根据更新描述符和失败签名直接生成最小补丁，并冻结到未见提交。","Learn a conditional residual operator from failed updates and successful second patches; generate minimal patches from update descriptors and failure signatures and freeze it on unseen commits."),
      "learned residual patch operator",
      ("失败更新→最小稳定补丁训练对和独立回归结果。","Failed-update to minimal-stabilizing-patch pairs with independent regression outcomes."),
      ("未见更新提交上的修复成功、补丁大小和圈外回归。","Repair success, patch size, and out-of-loop regression on unseen update commits."),
      ("联合重优化、HarnessFix、每次重新搜索、最近补丁检索。","Joint re-optimization, HarnessFix, per-instance search, and nearest-patch retrieval."),
      ("按提交级拆分训练/测试，冻结算子后对未见 Prompt/记忆更新生成残差补丁。","Split by update commit, freeze the operator, and generate residual patches for unseen prompt/memory updates."),
      ("不能超过容量匹配联合重优化或最近补丁检索则停止。","Stop if it does not beat capacity-matched joint re-optimization or nearest-patch retrieval."),
      ("minimal-stabilizing-patch-search",),("patch-pair-induction","frozen-residual-operator"),
      ("补丁对暴露跨提交规律，冻结残差算子提供真正迁移；逐实例搜索不能替代。","Patch pairs expose cross-commit structure and the frozen residual operator provides true transfer; per-instance search cannot replace it."),
      ("low-score-dimension-repair","microexperiment-keep-revert"),(5,5,5,5,4,5)),
    candidate("rollback-conditioned-update-inverter","回滚条件更新逆算子","Rollback-Conditioned Update Inverter","finalist",
      ("回滚通常只能撤销整个更新，无法保留更新中有益部分。","Rollback usually removes an entire update even when only part of it caused regression."),
      ("从部分回滚干预学习条件逆算子，将失败更新分解为可逆原子并生成仅抵消有害效应的 inverse patch。","Learn a conditional inverse operator from partial rollback interventions, decompose failed updates into reversible atoms, and generate an inverse patch that cancels only harmful effects."),
      "typed inverse-update operator",
      ("更新原子启用/禁用结果和回归恢复程度。","Enable/disable outcomes of update atoms and degree of regression recovery."),
      ("未见更新上的效用保留率、回归恢复率和 inverse patch 大小。","Utility retention, regression recovery, and inverse-patch size on unseen updates."),
      ("完整回滚、最小稳定补丁、联合重优化、Delta Debugging。","Full rollback, minimal stabilizing patch, joint re-optimization, and delta debugging."),
      ("在混合有益/有害更新中预注册可逆原子，训练后冻结到未见更新。","Pre-register reversible atoms in mixed-benefit/harm updates and freeze the learned inverter on unseen updates."),
      ("无法比完整回滚保留更多效用，或原子分解不稳定则停止。","Stop if it does not retain more utility than full rollback or atom decomposition is unstable."),
      ("active-causal-minimal-rollback",),("partial-rollback-interventions","inverse-operator-learning"),
      ("干预识别需抵消部分，逆算子把证据泛化为未来修复；只做定位仍会全量回滚。","Interventions identify what to cancel and the inverse operator generalizes that evidence into future repair; localization alone still implies whole rollback."),
      ("agentic-tree-search","frozen-harness-comparison"),(5,5,5,5,3,5)),
]
CANDIDATES += [
    candidate("tool-contract-effect-learner","工具契约效应学习","Tool Contract Effect Learner","finalist",
      ("工具 schema 只描述参数，很少显式表示调用前置条件、状态效应和可恢复错误。","Tool schemas describe arguments but rarely encode operational preconditions, state effects, and recoverable errors."),
      ("从成功/失败调用对和环境差分中归纳可执行工具契约，学习 precondition/effect/error-transition，并在规划前约束调用。","Induce executable tool contracts from success/failure calls and environment diffs, learning preconditions, effects, and error transitions that constrain planning before calls."),
      "versioned executable tool-contract library",
      ("调用轨迹、状态差分、错误码和环境验证。","Tool traces, state diffs, error codes, and environment validation."),
      ("未见任务和 API 版本上的非法调用率与任务成功。","Invalid-call rate and task success on unseen tasks and API versions."),
      ("原始 schema、自然语言工具说明、经验记忆、手写规则。","Raw schemas, natural-language tool descriptions, experience memory, and handwritten rules."),
      ("两个可验证状态的工具环境中学习契约，完整留出工具和 API 版本。","Learn contracts in two verifiable tool environments and hold out tools and API versions completely."),
      ("契约不能跨版本迁移，或原始 schema+反思同样有效则停止。","Stop if contracts do not transfer across versions or raw schema plus reflection is equally effective."),
      ("workflow-generalization-certificate",),("transition-induction","contract-enforcement"),
      ("状态差分归纳真实工具语义，契约执行把语义变成持久规划约束。","State-difference induction learns actual tool semantics and contract enforcement turns them into persistent planning constraints."),
      ("long-horizon-algorithm-discovery","data-literature-union"),(5,5,5,5,4,5)),
    candidate("api-error-semantic-adapter","API 错误语义适配器","API Error-Semantics Adapter","finalist",
      ("同一工具能力在不同 API 中返回不同错误语义，迁移后旧恢复策略会静默失效。","Equivalent tool capabilities expose different error semantics across APIs, silently breaking recovery policies after migration."),
      ("学习跨 API 的错误语义中间表示，将 provider-specific 错误映射为规范恢复状态，并编译目标 API 修复动作。","Learn an API-invariant error-semantics representation, map provider-specific failures into canonical recovery states, and compile target-API repair actions."),
      "persistent error-semantics adapter",
      ("等价工具的错误轨迹、恢复动作和最终环境结果。","Error traces, recovery actions, and final outcomes for semantically equivalent tools."),
      ("未见 API 家族上的恢复成功率和错误分类一致性。","Recovery success and error-class consistency on an unseen API family."),
      ("直接 LLM 重写、API-Semantic Workflow Compiler、错误文本检索、人工映射。","Direct LLM rewrite, API-Semantic Workflow Compiler, error-text retrieval, and manual mapping."),
      ("完整留出一个 API 家族，冻结语义表示后迁移恢复策略。","Hold out an entire API family and freeze the semantic representation before transferring recovery policies."),
      ("不能跨 API 家族迁移，或错误文本最近邻同样有效则停止。","Stop if it cannot transfer across API families or nearest error-text retrieval is equally effective."),
      ("api-semantic-workflow-compiler",),("error-state-induction","repair-compilation"),
      ("错误状态归一化解决迁移语义差异，修复编译把规范状态转成目标动作。","Error-state normalization resolves semantic drift and repair compilation converts canonical states to target actions."),
      ("data-literature-union","scientific-kg-neighborhood"),(5,5,5,5,4,5)),
    candidate("workflow-repair-grammar-v5","工作流修复语法 v5","Workflow Repair Grammar v5","finalist",
      ("重复工作流结构故障每次重新搜索补丁，无法跨 API 或图结构复用。","Recurring structural workflow failures are patched from scratch and do not transfer across APIs or graph motifs."),
      ("在冻结的结构重写语言中从失败/修复图差分归纳产生式，学习触发条件和局部重写，禁止测试时重新搜索。","Induce productions from failure/repair graph diffs in a frozen structural rewrite language, learn triggers and local rewrites, and prohibit test-time search."),
      "persistent workflow-repair grammar",
      ("工作流图差分、失败 motif 和独立验证的修复成功结果。","Workflow graph diffs, failure motifs, and independently verified post-repair success."),
      ("API-disjoint 与 motif-disjoint 工作流上的冻结重写成功。","Frozen rewrite success on API-disjoint and motif-disjoint workflows."),
      ("Failure-Driven Workflow Refinement、HarnessFix、图差分检索、测试时搜索。","Failure-Driven Workflow Refinement, HarnessFix, graph-diff retrieval, and test-time search."),
      ("训练/测试按 API 和 motif 双重留出，禁止测试时生成新规则。","Use double holdout by API and motif and forbid new rule generation at test time."),
      ("产生式不能组合泛化，或最近图差分检索同样有效则停止。","Stop if productions do not compositionally generalize or nearest graph-diff retrieval is equally effective."),
      ("workflow-failure-motif-rewriter",),("graph-diff-abstraction","grammar-induction"),
      ("图差分抽象提炼局部结构变化，语法归纳使变化可在未见结构上组合复用。","Graph-diff abstraction isolates structural changes and grammar induction enables compositional reuse on unseen structures."),
      ("collider-pivot-state-reuse","adversarial-proposer-critic-judge"),(5,5,5,5,4,5)),
    candidate("workflow-counterexample-template-miner","工作流反例模板挖掘器","Workflow Counterexample Template Miner","finalist",
      ("工作流修复常只看到失败实例，缺少能区分正确和错误结构的最小反例模板。","Workflow repair sees failure instances but lacks minimal counterexample templates that separate valid from invalid structures."),
      ("通过结构删除/替换寻找最小故障保持子图，聚合为类型化反例模板，并用模板指导未来修复与测试生成。","Find minimal failure-preserving subgraphs via structural deletion/substitution, aggregate them into typed counterexample templates, and use them to guide future repair and test generation."),
      "counterexample-template library",
      ("最小故障子图、匹配正例和修复后结果。","Minimal failure subgraphs, matched positives, and post-repair outcomes."),
      ("未见工作流上的故障召回、修复效率和误报率。","Failure recall, repair efficiency, and false-positive rate on unseen workflows."),
      ("失败日志聚类、图异常检测、最近故障检索、手写 motif。","Failure-log clustering, graph anomaly detection, nearest-failure retrieval, and handwritten motifs."),
      ("两个工作流环境中学习模板，按 motif 和 API 双重留出测试。","Learn templates in two workflow environments and evaluate with motif/API double holdout."),
      ("模板不比日志聚类提高圈外修复效率，或误报高则停止。","Stop if templates do not improve out-of-loop repair efficiency over log clustering or false positives are high."),
      ("failure-localization-before-reflection",),("minimal-counterexample-extraction","template-reuse"),
      ("最小反例提取给出结构因果边界，模板复用使其成为未来持久知识。","Minimal counterexample extraction identifies structural causal boundaries and template reuse turns them into persistent future knowledge."),
      ("data-literature-union","team-diversity-topology"),(5,4,5,5,4,5)),
]
# __V5_BATCH_A__
CANDIDATES += [
    candidate("evaluator-longitudinal-drift-corrector","纵向评价器漂移修正器","Evaluator Longitudinal Drift Corrector","finalist",
      ("Actor 与 evaluator 共同更新后，静态校准器无法识别仅在特定版本配对中出现的评分偏差。","When actor and evaluator co-evolve, static calibration cannot identify biases specific to version pairings."),
      ("构建 actor-version × evaluator-version 交叉评分矩阵，学习时间残差与交互项，并用独立锚点任务训练可冻结的偏差修正头。","Build a crossed actor-version by evaluator-version score matrix, learn temporal residuals and interactions, and train a frozen bias-correction head from independent anchor tasks."),
      "versioned evaluator correction head",
      ("跨版本评分矩阵、锚点任务和外部真值。","Cross-version score matrices, anchor tasks, and external ground truth."),
      ("未来未见 evaluator 版本上的真实排序和下游策略选择质量。","True ranking and downstream policy-selection quality on unseen future evaluator versions."),
      ("Bridge/SAJA 式静态校准、冻结 evaluator、Evaluator Ensemble。","Bridge/SAJA-style static calibration, frozen evaluator, and evaluator ensembles."),
      ("至少 6 轮 actor/evaluator 历史，按未来版本留出，比较偏差预测和策略选择。","Use at least six actor/evaluator rounds with future-version holdout and compare bias prediction plus policy selection."),
      ("不能显著超过静态校准器预测未来偏差则停止。","Stop if it does not significantly beat static calibration on future-version bias."),
      ("evaluator-anchor-residual-corrector",),("cross-version-residual-model","anchor-calibration"),
      ("纵向交互模型捕获共同进化偏差，独立锚点把残差约束到真实能力。","The longitudinal interaction model captures co-evolution bias while independent anchors tie residuals to real capability."),
      ("knowledge-grounded-multiperspective","data-literature-union"),(5,5,5,4,4,5)),
    candidate("rubric-intervention-sparse-solver","Rubric 干预稀疏求解器","Rubric Intervention Sparse Solver","finalist",
      ("评价 rubric 的少数原子可能造成系统性偏差，但整体重写会破坏中性维度。","A few rubric atoms can cause systematic bias while whole-rubric rewriting damages neutral dimensions."),
      ("从因果/中性干预构建 rubric-atom 效应矩阵，用约束稀疏求解器最小增删/重加权，并显式保持中性维度。","Build a rubric-atom effect matrix from causal/neutral interventions and solve a constrained sparse add/drop/reweight edit while explicitly preserving neutral dimensions."),
      "versioned executable rubric",
      ("rubric 原子干预、排序变化和中性保持标签。","Rubric-atom interventions, ranking changes, and neutral-preservation labels."),
      ("冻结独立任务上的偏差降低、真实排序和中性维度保持。","Bias reduction, true ranking, and neutral-dimension preservation on frozen independent tasks."),
      ("RRD、PReMISE、CROME 数据上的普通重写、Reward 微调。","RRD, PReMISE, generic rewriting on CROME interventions, and reward fine-tuning."),
      ("预注册 rubric 原子与因果/中性干预，匹配调用预算比较稀疏编辑与强基线。","Pre-register rubric atoms and causal/neutral interventions and compare sparse editing with strong baselines under matched calls."),
      ("不能保持中性维度，或普通重写同样有效则停止。","Stop if neutral dimensions are not preserved or generic rewriting is equally effective."),
      ("counterfactual-rubric-rewrite",),("intervention-effect-matrix","constrained-sparse-editor"),
      ("效应矩阵定位偏差原子，稀疏求解器在保持约束下执行最小持久修复。","The effect matrix localizes biased atoms and the sparse solver performs minimal persistent repair under preservation constraints."),
      ("literature-grounded-rubric","adversarial-proposer-critic-judge"),(5,5,5,4,4,5)),
    candidate("reward-anchor-counterexample-trainer","Reward 锚点反例训练","Reward Anchor-Counterexample Trainer","finalist",
      ("Reward 模型会在策略进化后出现新 shortcut，但只做不变性审计不能修复评价器。","Reward models develop new shortcuts after policy evolution, while invariance audits alone cannot repair the evaluator."),
      ("独立生成 evaluator 与环境真值分歧的锚点反例，训练小型修正头使因果方向一致、中性变换不变，并用留出策略冻结验证。","Generate independent anchor counterexamples where evaluator and environment disagree; train a small correction head for causal-direction agreement and neutral invariance, then freeze on held-out policies."),
      "small versioned reward-correction head",
      ("锚点反例、环境真值和 evaluator 分数。","Anchor counterexamples, environment truth, and evaluator scores."),
      ("未见策略版本上的真实候选选择与 shortcut 鲁棒性。","True candidate selection and shortcut robustness on unseen policy versions."),
      ("冻结 Reward、PRISM/CROME 式审计、普通 Pairwise Fine-tuning。","Frozen reward, PRISM/CROME-style audits, and ordinary pairwise fine-tuning."),
      ("两个策略版本训练，一个未来策略版本冻结测试，严格分离反例生成器和最终评测。","Train on two policy versions and freeze-test on a future version, separating counterexample generation from final evaluation."),
      ("只改善锚点集而不改善未来策略选择则停止。","Stop if it improves only anchor sets without improving future policy selection."),
      ("reward-invariance-audit",),("independent-anchor-generation","correction-head-training"),
      ("独立锚点暴露新 shortcut，修正头把审计证据内化为持久评价器更新。","Independent anchors expose new shortcuts and the correction head internalizes audit evidence into persistent evaluator updates."),
      ("literature-grounded-rubric","frozen-harness-comparison"),(5,5,5,4,4,5)),
    candidate("checkpoint-training-curriculum-selector","Checkpoint 判别训练课程","Checkpoint-Discriminative Training Curriculum","finalist",
      ("能区分相邻 checkpoint 的任务常被用作评测，但没有反过来用于选择下一轮真正有学习价值的训练任务。","Tasks that discriminate adjacent checkpoints are used for evaluation but rarely drive selection of training tasks that causally improve the next checkpoint."),
      ("学习任务的 checkpoint 判别力与时间效用，把它作为训练样本价值先验；冻结选择器后分配下一 checkpoint 的训练预算。","Learn checkpoint discrimination and temporal utility as a prior for training-sample value, then freeze the selector to allocate the next checkpoint's training budget."),
      "persistent curriculum registry",
      ("相邻 checkpoint 的 paired outcomes、训练后增益和任务特征。","Paired adjacent-checkpoint outcomes, post-training gains, and task features."),
      ("后续 checkpoint 在留出任务上的因果提升。","Causal improvement of later checkpoints on held-out tasks."),
      ("paired IRT、学习进度、失败率课程、随机课程。","Paired IRT, learning-progress curricula, failure-rate curricula, and random curricula."),
      ("两条独立版本流，固定训练样本数，比较下一 checkpoint 的圈外提升。","Use two independent version streams with fixed training-sample counts and compare out-of-loop improvement of the next checkpoint."),
      ("只能提高评测判别而不能提高训练后表现则停止。","Stop if it improves evaluation discrimination but not post-training performance."),
      ("checkpoint-discriminative-curriculum-learner",),("discrimination-estimator","training-budget-allocator"),
      ("判别估计器发现正在变化的能力边界，训练分配器把边界信息转化为真正模型更新。","The discrimination estimator locates changing capability boundaries and the allocator turns that information into actual learning updates."),
      ("microexperiment-keep-revert","frozen-harness-comparison"),(5,5,5,4,4,5)),
]
CANDIDATES += [
    candidate("failure-frontier-training-generator","失败前沿训练生成器","Failure-Frontier Training Generator","finalist",
      ("自进化系统经常重复训练明显失败样本，而不是学习当前能力边界附近最有价值的反例。","Self-evolving systems often retrain on obvious failures rather than counterexamples near the current capability boundary."),
      ("从最近版本的成功/失败对学习边界表示，生成最小扰动的近边界任务，并只保留独立验证器确认能区分当前/上一版本的样本进入训练。","Learn a boundary representation from recent success/failure pairs, generate minimally perturbed near-boundary tasks, and admit only independently verified samples that distinguish current from previous versions."),
      "versioned training curriculum",
      ("版本差异、生成任务和独立可解性/正确性验证。","Version differences, generated tasks, and independent solvability/correctness verification."),
      ("下一版本在留出分布上的提升与遗忘。","Next-version improvement and forgetting on held-out distributions."),
      ("失败重放、难度课程、随机增强、Counterexample-Generating Curriculum。","Failure replay, difficulty curricula, random augmentation, and Counterexample-Generating Curriculum."),
      ("固定生成和训练预算，两个模型三 seed，比较圈外增益与遗忘。","Fix generation and training budgets, use two models and three seeds, and compare out-of-loop gain and forgetting."),
      ("边界生成不优于失败重放，或只提升生成器同分布任务则停止。","Stop if boundary generation does not beat failure replay or improves only generator-matched tasks."),
      ("counterexample-generating-curriculum",),("boundary-model","verified-task-generator"),
      ("边界模型决定生成位置，独立验证器确保样本不是无效难题；两者共同把失败前沿变成训练信号。","The boundary model chooses where to generate and the independent verifier prevents invalid hard examples; together they turn the failure frontier into training signal."),
      ("data-literature-union","microexperiment-keep-revert"),(5,5,5,4,4,5)),
    candidate("update-aware-challenge-generator","更新感知挑战生成器","Update-Aware Challenge Generator","finalist",
      ("一次 Prompt/记忆/技能更新可能引入特定新脆弱性，但固定回归集通常覆盖不到更新语义附近的风险。","A prompt/memory/skill update can introduce update-specific vulnerabilities that a fixed regression suite misses."),
      ("解析更新 diff 与被改变的行为契约，生成针对潜在副作用的挑战任务；失败挑战经独立判定后回流为训练或修复数据。","Parse update diffs and changed behavioral contracts, generate challenges targeting plausible side effects, and feed independently verified failures back as training or repair data."),
      "persistent update-conditioned challenge curriculum",
      ("更新 diff、行为契约、挑战结果和独立评分。","Update diffs, behavioral contracts, challenge outcomes, and independent scores."),
      ("未见更新类型上的回归发现率与修复后泛化。","Regression discovery and post-repair generalization on unseen update types."),
      ("固定回归集、随机任务生成、Change-Triggered Regression Exams、红队 Prompt。","Fixed regression suites, random task generation, Change-Triggered Regression Exams, and generic red-team prompts."),
      ("三类更新训练、一类更新留出；匹配测试/生成预算并评测发现后修复收益。","Train on three update types and hold out a fourth under matched testing/generation budgets; measure downstream repair gains."),
      ("只提高发现率但不能带来修复收益，或固定回归同样有效则停止。","Stop if it improves discovery but not repair, or fixed regression testing is equally effective."),
      ("change-triggered-regression-exams",),("diff-conditioned-generator","failure-feedback-loop"),
      ("diff 条件生成把测试聚焦到真实改变表面，失败回流使挑战真正影响持久更新而非只做评测。","Diff conditioning focuses tests on the changed surface and feedback turns discovered failures into persistent updates rather than evaluation only."),
      ("collider-pivot-state-reuse","literature-grounded-rubric"),(5,5,4,5,4,5)),
    candidate("multi-agent-message-graph-evolver","多 Agent 消息图进化","Multi-Agent Message-Graph Evolver","finalist",
      ("多 Agent 系统通常固定通信拓扑，即使某些消息边在不同任务上持续造成干扰或冗余。","Multi-agent systems usually freeze communication topology even when some message edges consistently cause interference or redundancy."),
      ("对消息边进行受控遮蔽/替换，学习任务 motif 条件下的边际贡献与交互，周期性增删/定向通信边并冻结到未见任务。","Intervene on message edges with masking/replacement, learn motif-conditioned marginal and interaction effects, and persistently add/remove/redirect edges before freezing on unseen tasks."),
      "versioned multi-agent communication graph",
      ("消息边干预、团队结果、token 成本和任务 motif。","Message-edge interventions, team outcomes, token cost, and task motifs."),
      ("未见任务上的团队成功率、通信成本和单点故障鲁棒性。","Team success, communication cost, and single-point-failure robustness on unseen tasks."),
      ("固定全连接、层级通信、随机稀疏、AFlow/工作流搜索。","Fixed full connectivity, hierarchical communication, random sparsity, and AFlow/workflow search."),
      ("两个多 Agent benchmark 上做 4–6 轮拓扑更新，匹配 token 和调用预算，冻结后跨任务。","Run 4–6 topology-update rounds on two multi-agent benchmarks under matched token/call budgets and freeze across tasks."),
      ("收益可由简单稀疏化复现，或跨任务拓扑不稳定则停止。","Stop if simple sparsification reproduces gains or topology is unstable across tasks."),
      ("workflow-generalization-certificate",),("edge-intervention-credit","persistent-topology-edit"),
      ("边干预提供通信信用，拓扑编辑把信用变成可部署结构；只做 workflow search 无法解释边级必要性。","Edge interventions provide communication credit and topology edits turn it into deployable structure; generic workflow search lacks edge-level necessity."),
      ("self-organizing-research-teams","team-diversity-topology"),(5,5,5,5,4,5)),
    candidate("role-specialization-compiler","多 Agent 角色专化编译器","Role Specialization Compiler","finalist",
      ("通用子 Agent 长期处理重复任务 motif 时，固定角色 Prompt 会产生上下文浪费和能力冲突。","General subagents repeatedly handling the same motifs waste context and create capability conflicts under fixed role prompts."),
      ("从跨任务轨迹中聚类稳定职责与成功修复模式，编译为带输入契约、工具权限和退出条件的专化角色，并学习路由。","Cluster stable responsibilities and successful repair patterns across tasks, compile them into specialized roles with input contracts, tool permissions, and exit conditions, and learn routing."),
      "versioned role library and router",
      ("任务 motif、子 Agent 贡献、工具调用和团队结果。","Task motifs, subagent contribution, tool calls, and team outcomes."),
      ("未见任务上的团队成功、角色复用率和成本。","Team success, role reuse rate, and cost on unseen tasks."),
      ("固定角色、动态 prompt 角色、Skill library、router-only。","Fixed roles, dynamically prompted roles, skill libraries, and router-only systems."),
      ("按任务族留出训练/测试，冻结角色库，允许路由但禁止测试时生成新角色。","Hold out task families, freeze the role library, allow routing but no test-time role generation."),
      ("角色无法跨任务复用，或动态 prompt 角色同样有效则停止。","Stop if roles do not reuse across tasks or dynamic role prompting is equally effective."),
      ("multi-agent-message-graph-evolver",),("role-induction","contracted-role-compilation"),
      ("角色归纳找稳定职责，编译把职责变成可执行持久角色；仅路由不能创造专化能力。","Role induction finds stable responsibilities and compilation turns them into executable persistent roles; routing alone cannot create specialization."),
      ("self-organizing-research-teams","team-diversity-topology"),(5,5,4,5,4,5)),
]
CANDIDATES += [
    candidate("collaboration-topology-regression-guard","协作拓扑回归门控","Collaboration-Topology Regression Guard","finalist",
      ("多 Agent 通信图进化后，局部性能提升可能牺牲旧任务中的信息路径和容错。","Evolving a multi-agent communication graph can improve local performance while breaking information paths and fault tolerance on mastered tasks."),
      ("对候选拓扑编辑执行边级归因重放和留出任务连通性测试，学习允许的拓扑变更信赖域并将失败编辑写入禁配约束。","Run edge-attribution replay and held-out connectivity tests for candidate topology edits, learn a trust region over allowable graph changes, and persist failed edits as incompatibility constraints."),
      "versioned communication-graph trust region",
      ("候选图编辑、边级贡献、留出任务和故障注入结果。","Candidate graph edits, edge contributions, held-out tasks, and failure-injection outcomes."),
      ("未来任务上的成功率、通信成本和故障恢复。","Future-task success, communication cost, and fault recovery."),
      ("无门控拓扑搜索、固定图、普通 Regression-Gated、随机回滚。","Ungated topology search, fixed graphs, generic Regression-Gated, and random rollback."),
      ("4 轮拓扑进化，匹配调用预算，测试新任务与旧任务双向回归。","Run four topology-evolution rounds under matched call budgets and test both new-task gain and old-task regression."),
      ("不能减少拓扑更新后的旧任务回归，或限制过强导致无改进则停止。","Stop if it does not reduce old-task regression after topology updates or blocks nearly all useful changes."),
      ("regression-gated-self-evolution","multi-agent-message-graph-evolver"),("edge-credit-replay","graph-trust-region"),
      ("边信用定义哪些路径不可破坏，信赖域约束实际拓扑更新；普通门控没有结构级约束。","Edge credit identifies paths that must be preserved and the trust region constrains actual topology updates; generic gating lacks graph-structural constraints."),
      ("self-organizing-research-teams","frozen-harness-comparison"),(5,5,5,4,4,5)),
    candidate("structured-memory-model-swap-translator","结构化记忆模型迁移器","Structured-Memory Model-Swap Translator","finalist",
      ("自然语言记忆在模型替换后会因检索习惯、工具约束和程序格式差异失效，普通 Prompt 转移不足以处理结构化资产。","Structured agent memories can fail after a model swap because retrieval conventions, tool constraints, and program formats change; prompt transfer is insufficient."),
      ("将记忆拆成前置条件、动作程序、检索链接和约束，学习源模型到目标模型的组件级映射与重组，并在未见模型家族冻结。","Decompose memories into preconditions, action programs, retrieval links, and constraints; learn component-level mappings and recomposition from source to target models and freeze on an unseen model family."),
      "translated structured-memory asset",
      ("跨模型结构化记忆对、执行轨迹和行为锚点。","Cross-model structured-memory pairs, execution traces, and behavioral anchors."),
      ("未见模型家族上的记忆可用率、任务成功和回归。","Memory usability, task success, and regression on an unseen model family."),
      ("PromptBridge、MASA、目标模型从零重写、自然语言翻译。","PromptBridge, MASA, target-model rewrite-from-scratch, and natural-language translation."),
      ("三个开放模型家族，训练两家留一，冻结翻译器测试两任务域。","Use three open model families, train on two and hold out one, then freeze the translator across two task domains."),
      ("不能超过目标模型从零重写或 PromptBridge 类映射则停止。","Stop if it does not beat target-model rewriting or PromptBridge-style mapping."),
      ("asset-level-model-swap-certificate",),("structured-asset-decomposition","component-translation"),
      ("结构分解把普通文本迁移变成资产语义迁移，组件翻译才能保留程序与约束关系。","Structured decomposition turns text transfer into asset-semantic transfer, and component translation preserves program/constraint relations."),
      ("long-horizon-algorithm-discovery","scientific-kg-neighborhood"),(5,5,4,5,3,5)),
    candidate("cross-surface-model-swap-rewriter","跨表面模型替换重写器","Cross-Surface Model-Swap Rewriter","finalist",
      ("换 backbone 后，原更新表面可能不再适合：旧模型需要 Prompt 修复，新模型可能更适合记忆或工具约束。","After a backbone swap, the previously effective update surface may become inappropriate: a prompt fix may need to become memory or a tool constraint."),
      ("联合学习模型差分与跨表面行为等价映射，选择并转译到目标模型最稳定的更新表面，而不是只改写原资产。","Jointly learn model-difference features and cross-surface behavioral equivalence, choosing and transpiling to the most stable update surface for the target model instead of merely rewriting the original asset."),
      "target-model update-surface asset",
      ("源/目标模型行为差分、跨表面修复对和迁移结果。","Source/target behavioral differences, cross-surface repair pairs, and migration outcomes."),
      ("未见模型家族上的迁移成功、回归和资产复杂度。","Migration success, regression, and asset complexity on an unseen model family."),
      ("MASA、PromptBridge、固定表面重写、Cross-Surface Update Transpiler。","MASA, PromptBridge, fixed-surface rewriting, and Cross-Surface Update Transpiler."),
      ("三个模型家族×三更新表面，双重留出模型家族和修复类型。","Use three model families by three update surfaces with double holdout over model family and repair type."),
      ("表面选择不能泛化到未见模型，或固定表面同样稳定则停止。","Stop if surface choice does not generalize to unseen models or a fixed surface is equally stable."),
      ("model-swap-compatibility-certificate","cross-surface-update-transpiler"),("model-difference-encoder","surface-transpilation"),
      ("模型差分决定哪类表面稳定，跨表面转译产生实际迁移资产；只做其中之一无法完成 model-swap repair。","Model differences determine the stable surface and transpilation creates the migrated asset; either alone cannot complete model-swap repair."),
      ("scientific-kg-neighborhood","agentic-tree-search"),(5,5,4,5,3,5)),
    candidate("skill-interface-contract-compiler","技能接口契约编译器","Skill Interface Contract Compiler","finalist",
      ("技能在单任务中有效，但组合或跨工具时常因输入/状态假设不一致而失败。","Skills can work alone but fail in composition or across tools because their input and state assumptions mismatch."),
      ("从技能执行轨迹归纳类型化输入契约、状态后置条件和错误出口，编译兼容检查与必要的接口适配器后再允许组合。","Induce typed input contracts, state postconditions, and error exits from skill traces, then compile compatibility checks and minimal interface adapters before composition."),
      "versioned skill-contract registry",
      ("技能轨迹、状态差分、组合成功/失败和工具 schema。","Skill traces, state diffs, composition success/failure, and tool schemas."),
      ("未见技能组合和未见工具上的组合成功率。","Composition success on unseen skill combinations and unseen tools."),
      ("SkillCAT、SkCC、schema 匹配、测试时 LLM 修复。","SkillCAT, SkCC, schema matching, and test-time LLM repair."),
      ("完整留出技能对和工具，禁止测试时新写契约，比较组合成功与适配成本。","Hold out skill pairs and tools completely, forbid test-time contract generation, and compare composition success plus adaptation cost."),
      ("契约不能预测并修复未见组合，或 schema 匹配同样有效则停止。","Stop if contracts cannot predict and repair unseen compositions or schema matching is equally effective."),
      ("compositional-update-compatibility",),("contract-induction","adapter-compilation"),
      ("契约归纳识别接口不匹配，适配器编译把不匹配转换为可执行桥接；仅检测不解决组合失败。","Contract induction identifies interface mismatch and adapter compilation turns mismatch into executable bridges; detection alone does not repair composition."),
      ("long-horizon-algorithm-discovery","frozen-harness-comparison"),(5,5,5,5,4,5)),
]
# __V5_BATCH_B__
CANDIDATES += [
    candidate("typed-correction-skill-grammar-v5","类型化纠错技能语法 v5","Typed Correction Skill Grammar v5","revival",
      ("纠错技能若只是按失败轨迹存储，很难在未见失败组合上重组。","Correction skills stored per failure trace do not systematically recombine on unseen failure compositions."),
      ("自动归纳感知/规划/工具/执行失败槽，把必要纠错动作编译为产生式；冻结语法后在未见失败组合、工具域和模型上组合调用。","Automatically induce perception/planning/tool/execution failure slots and compile necessary correction actions into productions; freeze the grammar and compose it on unseen failure combinations, tool domains, and models."),
      "persistent correction-skill grammar",
      ("模块替换干预、必要纠错动作和自动失败槽。","Module-replacement interventions, necessary correction actions, and automatically induced failure slots."),
      ("未见失败组合上的修复成功和产生式复用率。","Repair success and production reuse on unseen failure compositions."),
      ("ASI、NSI、扁平技能库、最近修复检索、Correction-Action Causal Compiler。","ASI, NSI, flat skill libraries, nearest-repair retrieval, and Correction-Action Causal Compiler."),
      ("按失败组合和工具域双重留出，禁止测试时新增产生式。","Use double holdout over failure composition and tool domain and forbid new productions at test time."),
      ("失败槽需要人工标签，或最近修复检索同样有效则停止。","Stop if failure slots require manual labels or nearest-repair retrieval is equally effective."),
      ("typed-correction-skill-grammar","correction-action-causal-compiler"),("automatic-failure-slot-induction","grammar-composition"),
      ("自动失败槽去掉人工标签依赖，语法组合检验是否真的超越平面技能检索。","Automatic failure slots remove manual labels and grammar composition tests whether the method truly exceeds flat repair retrieval."),
      ("adversarial-proposer-critic-judge","microexperiment-keep-revert"),(5,5,5,5,4,5),
      ("只有同时满足自动失败槽与未见组合上的系统性重组，才复活为独立方法。","Revive only if failure slots are automatic and productions systematically recombine on unseen compositions.")),
    candidate("retrieval-mediated-harm-factorial-repair-v5","检索介导伤害析因修复 v5","Retrieval-Mediated Harm Factorial Repair v5","revival",
      ("记忆伤害可能来自内容、位置、共同检索或检索本身，单一暴露随机化无法区分。","Memory harm can arise from content, position, co-retrieval, or retrieval itself, which single exposure randomization cannot separate."),
      ("预注册析因干预分别操纵是否纳入、内容替换、排序位置和共同检索，估计路径效应后学习对应的重写/排序/互斥修复策略。","Pre-register factorial interventions over inclusion, content substitution, rank position, and co-retrieval; estimate pathway effects and learn pathway-specific rewrite/order/exclusion repairs."),
      "pathway-specific memory repair policy",
      ("析因干预结果、环境奖励和未来重用结果。","Factorial-intervention outcomes, environment rewards, and future reuse outcomes."),
      ("未见记忆身份上的路径识别准确度和修复收益。","Pathway-identification accuracy and repair gain on unseen memory identities."),
      ("Causal Memory Intervention、MemAudit、上下文 Bandit 直接学修复动作。","Causal Memory Intervention, MemAudit, and contextual-bandit direct repair learning."),
      ("相同干预数据下比较路径分解+修复与直接多臂老虎机，匹配调用和存储预算。","Compare pathway decomposition plus repair against direct contextual-bandit repair on identical intervention data and matched call/storage budgets."),
      ("路径分解不能提高圈外修复，或直接 Bandit 同样有效则停止。","Stop if pathway decomposition does not improve out-of-loop repair or direct bandit learning is equally effective."),
      ("retrieval-mediated-memory-harm-decomposer",),("factorial-mediation-estimation","pathway-specific-repair"),
      ("析因干预使伤害路径可识别，路径特定修复检验这种识别是否有独立价值。","Factorial interventions make harm pathways identifiable and pathway-specific repair tests whether that identification adds independent value."),
      ("data-literature-union","frozen-harness-comparison"),(5,5,5,4,4,5),
      ("只有相对直接修复学习器存在稳定增益时才复活。","Revive only if pathway identification adds stable value over direct repair learning.")),
    candidate("evaluator-residual-policy-corrector-v5","评价器残差策略修正 v5","Evaluator Residual Policy Corrector v5","revival",
      ("静态评价器校准无法处理 actor 与 evaluator 版本共同变化造成的未来评分偏差。","Static evaluator calibration cannot handle future bias caused by joint actor/evaluator version drift."),
      ("用完整 actor-version×evaluator-version 交叉历史学习低秩时间交互残差，并将残差修正头用于未来版本的候选策略排序与选择。","Learn low-rank temporal interaction residuals from a fully crossed actor-version by evaluator-version history and use a residual correction head for future-version policy ranking and selection."),
      "longitudinal evaluator correction head",
      ("交叉版本评分、独立锚点和真实下游任务结果。","Crossed version scores, independent anchors, and true downstream task outcomes."),
      ("未来 evaluator 版本上的策略选择 regret 和真实能力排序。","Policy-selection regret and true capability ranking on future evaluator versions."),
      ("Bridge、SAJA、冻结 evaluator、Evaluator Ensemble。","Bridge, SAJA, frozen evaluators, and evaluator ensembles."),
      ("至少 6 轮交叉历史，未来两个版本完全留出，比较静态与纵向校准。","Use at least six crossed rounds and hold out two future versions completely to compare static and longitudinal calibration."),
      ("纵向交互不提高未来策略选择则停止。","Stop if longitudinal interactions do not improve future policy selection."),
      ("evaluator-anchor-residual-corrector","evaluator-longitudinal-drift-corrector"),("crossed-longitudinal-model","policy-selection-correction"),
      ("交叉历史提供静态校准缺失的信息，最终以策略选择而不是偏差预测作为持久效果。","Crossed history provides information absent from static calibration and policy selection, not bias prediction alone, is the persistent effect."),
      ("literature-grounded-rubric","knowledge-grounded-multiperspective"),(5,5,5,4,4,5),
      ("只有在未来版本策略选择上超过静态校准才复活。","Revive only if future-version policy selection beats static calibration.")),
    candidate("api-semantic-workflow-ir-v5","API 语义工作流 IR v5","API-Semantic Workflow IR v5","revival",
      ("工作流跨 API 迁移时，函数名和 schema 相似并不保证前置条件、效应与错误恢复语义相同。","Across API migrations, similar names and schemas do not guarantee equivalent preconditions, effects, or recovery semantics."),
      ("从执行差分学习跨 API 不变的 precondition/effect/error 语义 IR，并将源工作流编译到目标 API，保持恢复分支。","Learn an API-invariant semantic IR for preconditions, effects, and errors from execution differences, then compile source workflows to target APIs while preserving recovery branches."),
      "portable workflow semantic IR",
      ("跨 API 等价任务、执行状态差分和错误恢复结果。","Cross-API equivalent tasks, execution-state differences, and recovery outcomes."),
      ("完全未见 API 家族上的行为等价、恢复成功和成本。","Behavioral equivalence, recovery success, and cost on a completely unseen API family."),
      ("直接 LLM 重写、SkCC、手写中间表示、执行修复循环。","Direct LLM rewrite, SkCC, handwritten IRs, and execution-repair loops."),
      ("三 API 家族训练两家留一家，冻结 IR 后编译，禁止测试时重新学习语义。","Train on two of three API families, freeze the IR, and compile to the held-out family without test-time semantic learning."),
      ("冻结 IR 不能跨家族保持恢复语义，或直接执行修复同样有效则停止。","Stop if the frozen IR does not preserve recovery semantics across families or direct execution repair is equally effective."),
      ("api-semantic-workflow-compiler","api-error-semantic-adapter"),("semantic-ir-induction","workflow-compilation"),
      ("IR 归纳负责可迁移语义，编译器负责实际目标工作流；必须共同超过直接重写。","IR induction supplies transferable semantics and the compiler creates the target workflow; together they must beat direct rewriting."),
      ("scientific-kg-neighborhood","long-horizon-algorithm-discovery"),(5,5,5,5,3,5),
      ("只有明确学习算子并在 API 家族留出上超过直接重写才复活。","Revive only with an explicit learned semantic operator that beats direct rewriting on held-out API families.")),
]
CANDIDATES += [
    candidate("permission-diff-causal-reauthorizer","更新差分因果重授权器","Update-Diff Causal Reauthorizer","revival",
      ("Agent 更新后继续沿用旧权限会引入新越权，而统一降权又损害效用。","Reusing old permissions after an agent update can create new overreach, while uniform downgrade harms utility."),
      ("对 Prompt/记忆/技能/工作流 diff 做干预式表示学习，预测哪些权限因本次更新新增风险，只运行针对这些权限的独立 canary，再更新租约。","Learn intervention-grounded representations of prompt/memory/skill/workflow diffs, predict which permissions become newly risky, run independent canaries only for those permissions, and update the lease."),
      "versioned permission lease state",
      ("更新 diff、权限干预、canary 结果、越权和任务效用。","Update diffs, permission interventions, canary outcomes, overreach, and task utility."),
      ("未见更新算子上的安全-效用 Pareto 与权限恢复正确率。","Safety-utility Pareto and permission-restoration accuracy on unseen update operators."),
      ("Progent 式动态策略、静态最小权限、统一降权、完整重认证。","Progent-style dynamic policy, static least privilege, uniform downgrade, and full reauthorization."),
      ("三类更新训练、一类更新留出；canary 生成与评分独立于风险模型。","Train on three update types and hold out a fourth; canary generation and scoring remain independent of the risk model."),
      ("未见更新算子上不优于动态策略或完整重认证则停止。","Stop if it does not beat dynamic policy or full reauthorization on unseen update operators."),
      ("update-conditioned-permission-lease",),("causal-diff-risk-model","targeted-reauthorization"),
      ("diff 风险模型缩小需要重认证的权限集合，独立 canary 决定实际权限更新；两者共同避免循环自评。","The diff-risk model narrows permissions needing reauthorization and independent canaries decide actual updates, avoiding circular self-evaluation."),
      ("data-literature-union","frozen-harness-comparison"),(5,5,5,4,4,5),
      ("只有在未见更新算子上稳定降低重认证成本且不牺牲安全时复活。","Revive only if it reduces reauthorization cost on unseen update operators without sacrificing safety.")),
    candidate("curriculum-drift-training-controller","课程漂移训练控制器","Curriculum-Drift Training Controller","revival",
      ("多轮自进化后，旧课程可能继续强化已掌握能力，同时忽略新出现的失败边界。","After multiple evolution rounds, stale curricula can oversample mastered capabilities while ignoring newly emerging failure boundaries."),
      ("学习任务族的训练边际收益与版本漂移，周期性重分配训练预算到效用上升或新失败边界，并保留稳定任务作为回归锚点。","Learn task-family marginal training gain and version drift, reallocating training budget toward rising utility or new failure boundaries while preserving stable tasks as regression anchors."),
      "versioned training curriculum controller",
      ("历史训练分配、checkpoint 变化、任务族效应和回归锚点。","Historical training allocation, checkpoint changes, task-family effects, and regression anchors."),
      ("后续 checkpoint 的圈外提升、遗忘和预算效率。","Out-of-loop improvement, forgetting, and budget efficiency of later checkpoints."),
      ("固定课程、学习进度、失败率课程、Checkpoint-Discriminative Training Curriculum。","Fixed curricula, learning progress, failure-rate curricula, and Checkpoint-Discriminative Training Curriculum."),
      ("两条真实版本流、固定训练预算、至少 4 轮重新分配，评测未见任务族。","Use two real version streams, fixed training budgets, at least four reallocations, and evaluate unseen task families."),
      ("不能提高后续 checkpoint 或遗忘恶化则停止。","Stop if later checkpoints do not improve or forgetting worsens."),
      ("curriculum-drift-controller","checkpoint-training-curriculum-selector"),("drift-estimation","budget-reallocation"),
      ("漂移估计判断课程何时过期，预算重分配真正改变训练数据；仅审计课程不构成学习机制。","Drift estimation identifies stale curricula and budget reallocation actually changes training data; audit alone is not a learning mechanism."),
      ("microexperiment-keep-revert","collider-pivot-state-reuse"),(5,5,5,4,4,5),
      ("只有闭合训练环且在后续 checkpoint 有因果收益时复活。","Revive only when the training loop closes and causes gains in later checkpoints.")),
    candidate("restoration-clause-induction-v5","恢复子句归纳 v5","Restoration-Clause Induction v5","revival",
      ("回滚定位可以找出故障更新，但若证据不能转成未来更新组合规则，同类回退仍会重复。","Rollback localization can identify faulty updates, but without reusable composition rules the same regressions recur."),
      ("在冻结的类型化更新描述符语言中，从随机回滚干预归纳带置信度的 no-good、compatibility 与 precedence 子句，并显式控制误阻断。","In a frozen typed update-descriptor language, induce confidence-bearing no-good, compatibility, and precedence clauses from randomized rollback interventions with explicit false-block control."),
      "persistent update-composition clause library",
      ("回滚干预、更新描述符、恢复结果和误阻断标签。","Rollback interventions, update descriptors, restoration outcomes, and false-block labels."),
      ("未见更新组合上的回归预防率、误阻断率和效用保留。","Regression prevention, false-block rate, and utility retention on unseen update compositions."),
      ("ANNEAL、PMA/ProbDD 后验风险门控、Update-Composition Repair Compiler。","ANNEAL, PMA/ProbDD posterior risk gating, and Update-Composition Repair Compiler."),
      ("完整留出组合模板，比较子句库与相同干预历史训练的直接风险 gate。","Hold out composition templates completely and compare the clause library with a direct risk gate trained on identical intervention history."),
      ("不能超越直接风险 gate 或误阻断过高则停止。","Stop if it does not beat direct risk gating or false blocking is excessive."),
      ("restoration-clause-learning","update-composition-repair-compiler"),("probabilistic-clause-induction","false-block-control"),
      ("子句归纳产生可复用结构知识，误阻断控制保证它不是简单保守 gate。","Clause induction creates reusable structural knowledge and false-block control prevents collapse into a conservative gate."),
      ("adversarial-proposer-critic-judge","knowledge-grounded-multiperspective"),(5,5,5,5,4,5),
      ("只有类型语言、概率语义和误阻断控制均明确时复活。","Revive only when the typed language, probabilistic semantics, and false-block control are all explicit.")),
    candidate("effect-transport-lesson-specializer-v5","效应迁移经验专化 v5","Effect-Transport Lesson Specializer v5","revival",
      ("一条经验在源任务有效，却可能在目标任务族产生负迁移；只输出迁移证书仍不改变持久知识。","A lesson may help its source task but harm a target family; a transport certificate alone does not change persistent knowledge."),
      ("用多任务随机化效应和支持重叠学习可迁移区域；对不可全局迁移的经验自动分裂为任务族条件子经验，并对未知区域弃权。","Learn transportable regions from randomized multi-task effects and support overlap; automatically split non-global lessons into task-family-conditioned descendants and abstain outside support."),
      "transport-specialized lesson lineage",
      ("跨任务族随机化经验效应、支持描述和模型家族信息。","Randomized lesson effects across task families, support descriptors, and model-family information."),
      ("完全未见任务族上的效应符号、负迁移率和覆盖率。","Effect sign, negative-transfer rate, and coverage on fully unseen task families."),
      ("Conformal/R-learner 迁移 gate、语义相似度、Effect-Bifurcation Memory Learner。","Conformal/R-learner transport gates, semantic similarity, and Effect-Bifurcation Memory Learner."),
      ("至少 10 个任务族用于校准/留出，冻结后不得用目标标签，比较 gate-only 与自动专化。","Use at least ten task families for calibration/holdout, forbid target labels after freezing, and compare gate-only versus automatic specialization."),
      ("校准无效、覆盖过低或专化不优于 gate-only 则停止。","Stop if calibration is invalid, coverage too low, or specialization does not beat gate-only."),
      ("conformal-effect-transport-gate","cross-task-effect-transport-certificate"),("transport-risk-estimation","lesson-specialization"),
      ("迁移风险估计确定适用区域，经验专化实际改变持久知识；只输出证书不能解决负迁移。","Transport-risk estimation determines support and lesson specialization actually changes persistent knowledge; a certificate alone cannot repair negative transfer."),
      ("scientific-kg-neighborhood","frozen-harness-comparison"),(5,5,4,5,3,5),
      ("只有具备足够任务族和有效支持假设时复活。","Revive only with enough task families and valid support assumptions.")),
]
CANDIDATES += [
    candidate("strategy-diversity-consolidator","策略多样性整合器","Strategy-Diversity Consolidator","repair",
      ("自进化不断保留最优经验会把策略库收缩到单一模式，环境变化后缺少替代路径。","Repeatedly retaining only the best experience can collapse the strategy library to one mode, leaving no alternatives after environment shifts."),
      ("按行为轨迹与反事实成功条件学习策略模式，在固定容量下保留效用互补的代表策略，并对新经验执行多样性保持整合。","Learn strategy modes from behavior trajectories and counterfactual success conditions, preserve utility-complementary representatives under a fixed capacity, and consolidate new experiences with diversity constraints."),
      "versioned strategy portfolio memory",
      ("轨迹模式、环境条件、策略效用与切换结果。","Trajectory modes, environment conditions, strategy utility, and switching outcomes."),
      ("环境漂移后的恢复速度、策略覆盖和平均任务成功。","Recovery speed, strategy coverage, and average task success after environment shift."),
      ("top-k 成功经验、语义聚类、多样性检索、Skill library。","Top-k successful experiences, semantic clustering, diverse retrieval, and skill libraries."),
      ("先做两种环境漂移的现象实验，确认多策略库确有恢复优势再推进完整学习器。","First run two environment-shift phenomenon tests and advance only if a multi-strategy library shows a recovery advantage."),
      ("不存在稳定策略塌缩现象，或简单语义聚类已足够则停止。","Stop if strategy collapse is not stable or simple semantic clustering is sufficient."),
      ("contradiction-preserving-memory-consolidation",),("behavior-mode-clustering","capacity-constrained-diversity"),
      ("先验证策略塌缩是真实问题；否则组合机制没有必要。","First verify that strategy collapse is real; otherwise the combined mechanism is unnecessary."),
      ("data-literature-union","microexperiment-keep-revert"),(4,4,4,4,4,4)),
    candidate("multi-surface-repair-program-synthesizer","多更新表面修复程序合成","Multi-Surface Repair Program Synthesizer","repair",
      ("同一复杂失败可能需要 Prompt、记忆和工作流共同修复，单表面路由无法覆盖。","A complex failure may require coordinated prompt, memory, and workflow changes, beyond single-surface routing."),
      ("把各表面修复视为类型化原子，通过小规模干预学习必要组合，再合成有顺序和前置条件的最小跨表面修复程序。","Treat per-surface repairs as typed atoms, learn necessary combinations with small interventions, and synthesize a minimal ordered cross-surface repair program with preconditions."),
      "cross-surface repair program",
      ("表面原子干预、组合效果和回归结果。","Surface-atom interventions, composition effects, and regression outcomes."),
      ("未见复合故障上的修复成功、程序长度和旧能力保持。","Repair success, program length, and retention of mastered capabilities on unseen compound failures."),
      ("Update-Surface Router、逐表面贪心、联合 LLM 重写、Update-Composition Repair Compiler。","Update-Surface Router, per-surface greedy repair, joint LLM rewrite, and Update-Composition Repair Compiler."),
      ("先在可控双表面故障上 P0，若必要组合稳定再扩展到三表面。","Start with controlled two-surface faults and expand to three surfaces only if necessary combinations are stable."),
      ("双表面就不存在组合必要性，或联合重写同样有效则停止。","Stop if two-surface combination necessity is absent or joint rewriting is equally effective."),
      ("update-surface-router","update-composition-repair-compiler"),("cross-surface-interventions","repair-program-synthesis"),
      ("必须先证明多表面组合是必要的，再谈程序合成；否则降级为组件。","Combination necessity must be demonstrated before program synthesis; otherwise this is only a component."),
      ("agentic-tree-search","adversarial-proposer-critic-judge"),(4,5,4,3,4,4)),
    candidate("contradiction-lineage-splitter","矛盾谱系分裂器","Contradiction-Lineage Splitter","component",
      ("记忆矛盾通常被压平为多数结论，丢失适用上下文。","Memory contradictions are often flattened into a majority conclusion, losing applicability context."),
      ("检测反复改变决策的矛盾对，建立共同祖先并分裂成上下文专化后代，保留冲突谱系。","Detect contradiction pairs that repeatedly flip decisions, create a common ancestor, and split them into context-specialized descendants while preserving conflict lineage."),
      "contradiction-aware memory lineage",
      ("矛盾重放结果与上下文差分。","Contradiction replay outcomes and contextual differences."),
      ("未来任务中选择正确分支的比例和信息保留。","Correct-branch selection and information retention on future tasks."),
      ("Contradiction-Preserving Memory Consolidation、简单保留两条记忆。","Contradiction-Preserving Memory Consolidation and simply keeping both memories."),
      ("作为 Effect-Bifurcation Memory Learner 的消融组件验证，不单独进入二审。","Evaluate as an ablation/component of Effect-Bifurcation Memory Learner rather than standalone R2."),
      ("不能给主方法带来额外收益则保持组件状态。","Remain a component if it adds no value to the parent method."),
      ("contradiction-preserving-memory-consolidation","effect-bifurcation-memory-learner"),("contradiction-detection","lineage-splitting"),
      ("主要作为效应分叉的结构实现，不足以单独主张。","Primarily a structural implementation for effect bifurcation, not yet a standalone thesis."),
      ("scientific-kg-neighborhood",),(4,4,4,4,5,3)),
    candidate("surface-effect-translation-graph","更新表面效应转译图","Surface-Effect Translation Graph","component",
      ("跨表面修复缺少统一描述不同更新如何产生等价行为效应的中间结构。","Cross-surface repair lacks an intermediate structure describing when different update surfaces produce equivalent behavioral effects."),
      ("建立更新表面×失败类型的效应图，边表示行为等价、可转译或互补关系，为转译器和修复程序提供先验。","Build an update-surface by failure-type effect graph whose edges encode behavioral equivalence, translatability, or complementarity, supplying priors to transpilers and repair programs."),
      "surface-effect knowledge graph",
      ("跨表面修复对与行为效应。","Cross-surface repair pairs and behavioral effects."),
      ("对下游转译/修复搜索的样本效率提升。","Sample-efficiency improvement for downstream transpilation and repair search."),
      ("无图先验、语义相似图、随机图。","No graph prior, semantic-similarity graphs, and random graphs."),
      ("作为 Cross-Surface Update Transpiler 与 Multi-Surface Repair Program 的共享组件测试。","Test as a shared component for Cross-Surface Update Transpiler and Multi-Surface Repair Program."),
      ("对下游无稳定增益则保持组件状态。","Remain a component if downstream gains are not stable."),
      ("cross-surface-update-transpiler","multi-surface-repair-program-synthesizer"),("effect-graph-construction",),
      ("图本身不作为论文主张，只用于提高跨表面方法的数据效率。","The graph is not a standalone paper claim; it is an efficiency component for cross-surface methods."),
      ("scientific-kg-neighborhood",),(4,3,4,4,5,3)),
]
# __V5_BATCH_C__


def _load_reviews() -> dict[str, list[dict[str, Any]]]:
    if not DEFAULT_EXTERNAL_JSON.exists():
        return {}
    try:
        payload = json.loads(DEFAULT_EXTERNAL_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    reviews = payload.get("reviews", {})
    return reviews if isinstance(reviews, dict) else {}


def _pareto(rows: list[dict[str, Any]]) -> list[str]:
    keys = ("problem_reality", "mechanism_strength", "identifiability", "transfer", "feasibility", "discussion_value")
    front: list[str] = []
    for row in rows:
        if any(other is not row and all(other["scores"][k] >= row["scores"][k] for k in keys) and any(other["scores"][k] > row["scores"][k] for k in keys) for other in rows):
            continue
        front.append(row["id"])
    return front


def build_idea_discovery_v5() -> dict[str, Any]:
    reviews = _load_reviews()
    rows: list[dict[str, Any]] = []
    status_order = {"finalist": 0, "revival": 1, "repair": 2, "component": 3}
    for row0 in CANDIDATES:
        row = dict(row0)
        ext = reviews.get(row["id"], [])
        latest = ext[-1] if ext else {}
        row["external_reviews"] = ext
        row["external_review_status"] = "reviewed" if ext else "pending"
        row["external_verdict"] = latest.get("verdict", "pending")
        row["external_confidence"] = latest.get("confidence", "")
        row["external_finding"] = latest.get("finding", "")
        row["external_finding_zh"] = latest.get("finding_zh", "")
        row["external_required_action"] = latest.get("required_action", "")
        row["external_required_action_zh"] = latest.get("required_action_zh", "")
        row["combination_audit"] = latest.get("combination_audit", {})
        rows.append(row)
    rows.sort(key=lambda x: (status_order[x["internal_status"]], -x["mean_score"], x["id"]))
    for rank, row in enumerate(rows, 1):
        row["internal_rank"] = rank
    finalist_pool = [x for x in rows if x["internal_status"] in {"finalist", "revival"}]
    finalist_pool.sort(key=lambda x: ({"pass":0,"revise":1,"pending":2,"block":3}.get(x["external_verdict"],2), -x["mean_score"], x["internal_rank"]))
    for rank, row in enumerate(finalist_pool, 1): row["external_rank"] = rank
    latest = [x["external_verdict"] for x in finalist_pool if x["external_review_status"] == "reviewed"]
    discussion_ready = [x for x in finalist_pool if x["external_verdict"] == "pass"]
    return {
        "schema_version": "1.0", "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "target_venue": "ICLR", "status": "external-reviewed" if len(latest) == len(finalist_pool) else "internal-screen",
        "policy": {
            "target_discussion_ready_total": 20, "do_not_lower_review_bar": True, "combination_allowed": True,
            "blocked_is_revivable": True, "microexperiment_before_full_pilot": True,
            "discussion_ready_definition": "external PASS under official-source review; prior main-bank and v4 PASS remain counted separately",
        },
        "summary": {
            "repository_patterns": len(REPOSITORY_PATTERNS), "workflow_stages": len(WORKFLOW_STAGES), "raw_candidates": len(rows),
            "finalist": sum(x["internal_status"] == "finalist" for x in rows), "revival": sum(x["internal_status"] == "revival" for x in rows),
            "repair": sum(x["internal_status"] == "repair" for x in rows), "component": sum(x["internal_status"] == "component" for x in rows),
            "external_reviewed": len(latest), "external_pending": len(finalist_pool) - len(latest),
            "external_pass": latest.count("pass"), "external_revise": latest.count("revise"), "external_block": latest.count("block"),
            "discussion_ready": len(discussion_ready),
        },
        "repository_patterns": [{"system": s, "official_repo": u, "adopted_as": a, "pattern": bi(z, e)} for s,u,a,z,e in REPOSITORY_PATTERNS],
        "workflow_stages": [{"id": i, "name": bi(z,e), "output": bi(oz,oe)} for i,z,e,oz,oe in WORKFLOW_STAGES],
        "pareto_front_ids": _pareto(rows), "discussion_ready": discussion_ready,
        "finalists": finalist_pool, "all_candidates": rows,
    }


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rows = payload.get("all_candidates", [])
    if len(rows) != 36: errors.append(f"expected 36 candidates, got {len(rows)}")
    if len({x.get('id') for x in rows}) != len(rows): errors.append("duplicate ids")
    if len(payload.get("finalists", [])) < 28: errors.append("expected at least 28 finalists/revivals")
    for row in rows:
        for field in ("title","problem","exact_mechanism","learning_signal","independent_ground_truth","strongest_baseline","decisive_pilot","stop_condition","necessity_logic"):
            value = row.get(field)
            if not isinstance(value, dict) or not value.get("zh") or not value.get("en"):
                errors.append(f"missing bilingual {field}: {row.get('id')}")
        if len(row.get("components", [])) > 3: errors.append(f"too many components: {row.get('id')}")
        if row.get("internal_status") == "revival" and not (row.get("revival_condition") or {}).get("en"):
            errors.append(f"revival missing condition: {row.get('id')}")
    return errors


def write_idea_discovery_v5(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    payload = build_idea_discovery_v5(); errors = validate(payload)
    if errors: raise ValueError("Invalid Idea Discovery v5:\n- " + "\n- ".join(errors))
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.IDEA_DISCOVERY_V5 = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(write_idea_discovery_v5()["summary"], ensure_ascii=False))
