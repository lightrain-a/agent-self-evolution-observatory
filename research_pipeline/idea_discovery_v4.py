from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "idea-discovery-v4.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "idea-discovery-v4.js"
DEFAULT_EXTERNAL_JSON = PROJECT_ROOT / "generated" / "idea-discovery-v4-external-reviews.json"


def bi(zh: str, en: str) -> dict[str, str]:
    return {"zh": zh.strip(), "en": en.strip()}


REPOSITORY_PATTERNS: tuple[dict[str, Any], ...] = (
    {"system":"ResearchAgent","official_repo":"https://github.com/JinheonBaek/ResearchAgent","pattern":bi("按 Reviewer 低分维度进行定向修订，而不是整体重写。","Repair only the low-scoring reviewer dimensions instead of rewriting the whole idea."),"adopted_as":"dimension-targeted-repair"},
    {"system":"MOOSE-Chem","official_repo":"https://github.com/ZonglinY/MOOSE-Chem","pattern":bi("问题背景与灵感语料分离，并允许同背景内和跨灵感的假设变异。","Separate problem background from inspiration corpora and mutate within or across inspirations."),"adopted_as":"mechanism-pool + cross-inspiration-mutation"},
    {"system":"HypoGeniC / HypoRefine","official_repo":"https://github.com/ChicagoHAI/hypothesis-generation","pattern":bi("把数据驱动假设、文献驱动假设及两者并集分别生成并比较。","Generate data-driven, literature-driven, and union hypotheses as distinct banks."),"adopted_as":"evidence-source-union"},
    {"system":"Open Co-Scientist","official_repo":"https://github.com/jataware/open-coscientist","pattern":bi("使用生成、反思、排名、锦标赛、进化、邻近去重和 Meta-review 形成多轮假设竞争。","Use generation, reflection, ranking, tournament, evolution, proximity deduplication, and meta-review."),"adopted_as":"tournament-evolution + diversity-control"},
    {"system":"Virtual Scientists","official_repo":"https://github.com/open-sciencelab/Virtual-Scientists","pattern":bi("通过不同角色和团队组合增加科学 Idea 的知识与视角多样性。","Use different scientist roles and team compositions to diversify knowledge and perspectives."),"adopted_as":"team-composition-diversity"},
    {"system":"AI Scientist-v2","official_repo":"https://github.com/SakanaAI/AI-Scientist-v2","pattern":bi("保留多个方法和实验分支，再通过实验管理与树搜索剪枝。","Preserve method and experiment branches and prune them through tree search and experiment management."),"adopted_as":"branch-and-bound-method-search"},
    {"system":"RD-Agent","official_repo":"https://github.com/microsoft/RD-Agent","pattern":bi("Research 与 Development 分离，并把真实执行反馈写回 Idea Pool。","Separate research from development and feed execution results back into the idea pool."),"adopted_as":"execution-feedback-revival"},
    {"system":"autoresearch","official_repo":"https://github.com/karpathy/autoresearch","pattern":bi("每次修改都在固定评测下 keep/revert，失败实验也保留在 Git 历史。","Keep or revert every change under a fixed evaluation while retaining failed experiments in Git history."),"adopted_as":"fixed-eval-keep-revert"},
    {"system":"autoresearch-agents","official_repo":"https://github.com/hwchase17/autoresearch-agents","pattern":bi("允许修改 Prompt、工具和 Agent 架构，但固定评测 Harness 与数据集。","Allow prompt, tool, and architecture edits while freezing the evaluation harness and dataset."),"adopted_as":"frozen-harness-branch-search"},
    {"system":"ScholarEval","official_repo":"https://github.com/skai-research/ScholarEval","pattern":bi("用文献证据评价并修订 Idea，而不是只给一个总体新颖性分数。","Use literature-grounded evidence to evaluate and refine ideas rather than only scoring novelty."),"adopted_as":"literature-grounded-objection-repair"},
    {"system":"data-to-paper","official_repo":"https://github.com/Technion-Kishony-lab/data-to-paper","pattern":bi("从结论反向追踪到数据、分析和假设，使每个研究主张可验证。","Backward-trace claims to data, analysis, and hypotheses for verifiability."),"adopted_as":"backward-traceable-claim-design"},
)


WORKFLOW_STAGES: tuple[dict[str, Any], ...] = (
    {"id":"P","name":bi("真实问题池","Real-problem bank"),"output":bi("从失败案例、Reviewer objections、实验负结果和部署限制中形成问题胶囊。","Problem capsules from failures, reviewer objections, negative results, and deployment constraints.")},
    {"id":"M","name":bi("机制原子池","Mechanism-atom bank"),"output":bi("从同题工作、跨域方法和自动科研仓库抽取可迁移机制。","Transferable mechanism atoms from direct work, cross-domain methods, and automated-research repositories.")},
    {"id":"C","name":bi("结构兼容图","Structural compatibility graph"),"output":bi("只连接具有相同状态、干预、监督或失效结构的问题与机制。","Connect problems and mechanisms only when state, intervention, supervision, or failure structure matches.")},
    {"id":"U","name":bi("受约束组合","Constrained composition"),"output":bi("组合一至三个必要机制，并解释每个组件为何不可移除。","Compose one to three necessary mechanisms and state why each component cannot be removed.")},
    {"id":"V","name":bi("旧 Idea 条件复活","Conditional revival"),"output":bi("改变关键假设、学习对象、独立监督或部署边界后重新生成分支。","Regenerate old ideas after changing the key assumption, learned object, independent supervision, or deployment boundary.")},
    {"id":"T","name":bi("锦标赛与邻近去重","Tournament and proximity control"),"output":bi("按真实问题覆盖、机制必要性、实验可判定性和组合多样性进行成对比较。","Pairwise compare real-problem coverage, mechanism necessity, experimental decisiveness, and diversity.")},
    {"id":"R","name":bi("可归约性挑战","Reduction challenge"),"output":bi("若标准方法在同数据与预算下能复现，则降级为 Baseline 或组件，而不是永久删除。","If a standard method reproduces the result under equal data and budget, demote to baseline/component rather than delete forever.")},
    {"id":"X","name":bi("资源与实验落地","Resource and experiment grounding"),"output":bi("冻结公开资产、最强 Baseline、P0/P1/P2 和 Stop 条件。","Freeze public assets, strongest baseline, P0/P1/P2, and Stop rule.")},
    {"id":"F","name":bi("结果回流与再组合","Feedback and recombination"),"output":bi("失败分支保留为可复用机制原子，允许在新问题上再次组合。","Preserve failed branches as reusable mechanism atoms for recombination with new problems.")},
)


STATUS_ORDER = {"discussion": 0, "revival": 1, "repair": 2, "component": 3}


def candidate(
    id: str,
    title_zh: str,
    title_en: str,
    lineage: str,
    parents: tuple[str, ...],
    status: str,
    problem_zh: str,
    problem_en: str,
    mechanism_atoms: tuple[str, ...],
    composition_zh: str,
    composition_en: str,
    update_surface: str,
    signal_zh: str,
    signal_en: str,
    truth_zh: str,
    truth_en: str,
    baseline_zh: str,
    baseline_en: str,
    pilot_zh: str,
    pilot_en: str,
    stop_zh: str,
    stop_en: str,
    assets: tuple[str, ...],
    scores: tuple[int, int, int, int, int, int],
    revival_condition_zh: str = "",
    revival_condition_en: str = "",
) -> dict[str, Any]:
    keys = ("problem_reality", "mechanism_necessity", "identifiability", "novelty", "feasibility", "transfer")
    return {
        "id": id,
        "title": bi(title_zh, title_en),
        "lineage_type": lineage,
        "parent_ids": list(parents),
        "internal_status": status,
        "real_problem": bi(problem_zh, problem_en),
        "mechanism_atoms": list(mechanism_atoms),
        "composition_logic": bi(composition_zh, composition_en),
        "persistent_update_object": update_surface,
        "learning_signal": bi(signal_zh, signal_en),
        "independent_ground_truth": bi(truth_zh, truth_en),
        "strongest_baseline": bi(baseline_zh, baseline_en),
        "decisive_pilot": bi(pilot_zh, pilot_en),
        "stop_condition": bi(stop_zh, stop_en),
        "public_assets": list(assets),
        "scores": dict(zip(keys, scores, strict=True)),
        "mean_score": round(sum(scores) / len(scores), 3),
        "revival_condition": bi(revival_condition_zh, revival_condition_en) if revival_condition_zh else None,
        "external_reviews": [],
        "external_verdict": "pending",
    }


CANDIDATES: list[dict[str, Any]] = []
CANDIDATES += [
    candidate(
        "retrieval-mediated-memory-harm-decomposer", "检索介导的记忆伤害分解器", "Retrieval-Mediated Memory Harm Decomposer",
        "new-combination", ("retrieval-interference-auditor", "future-reuse-harm-predictor"), "discussion",
        "记忆条目造成的未来失败既可能来自条目内容本身，也可能来自检索频率、位置和与其他记忆的交互。",
        "Future memory failures may come from content, retrieval exposure, position, or interactions with other memories.",
        ("randomized retrieval exposure", "causal mediation", "persistent memory rewrite"),
        "先随机化条目是否被检索，再把总效应分成内容直接效应、检索介导效应和条目交互效应；系统不只决定是否保留，还把主要伤害来源编译成重写、降频或互斥约束。",
        "Randomize retrieval exposure, decompose total effect into direct content, retrieval-mediated, and interaction effects, then compile the dominant harm source into rewrite, down-weighting, or mutual-exclusion constraints.",
        "versioned memory entry plus retrieval policy",
        "条目级随机检索日志、后续任务奖励和共同检索集合。",
        "Entry-level randomized retrieval logs, future-task rewards, and co-retrieval sets.",
        "独立环境奖励下的未来帮助、直接伤害和介导伤害。",
        "Future benefit, direct harm, and mediated harm under independent environment rewards.",
        "标准因果中介分析、A-MAC、写入／删除门控和固定检索降权。",
        "Standard causal mediation, A-MAC, write/delete gating, and fixed retrieval down-weighting.",
        "在 ALFWorld 与 WebArena-Lite 的时间任务流中随机化条目暴露，比较删除、重写、降频和互斥四种持久修复。",
        "Randomize entry exposure in chronological ALFWorld and WebArena-Lite streams and compare deletion, rewriting, down-weighting, and mutual exclusion.",
        "若中介分解不能指导比统一删除更好的修复，或第二模型上效应方向不稳定，则降级为分析工具。",
        "Demote to analysis if decomposition does not guide better repair than uniform deletion or effect signs are unstable on a second model.",
        ("ALFWorld", "WebArena-Lite", "Qwen2.5-7B-Instruct", "Llama-3.1-8B-Instruct"), (5,5,4,4,4,4),
    ),
    candidate(
        "memory-interaction-clause-learner", "记忆交互兼容子句学习", "Memory Interaction Clause Learner",
        "new-combination", ("contradiction-preserving-consolidation", "compositional-update-compatibility"), "discussion",
        "单条记忆各自有益，但共同检索时可能产生冲突、覆盖或错误组合。",
        "Individually useful memories can conflict, overwrite, or compose incorrectly when retrieved together.",
        ("pairwise interaction interventions", "typed compatibility clauses", "retrieval-time enforcement"),
        "通过成对和三元共同检索干预学习带置信度的兼容、互斥和优先级子句；这些子句成为持久检索约束，而不是一次性冲突检测。",
        "Use pairwise and triple co-retrieval interventions to learn confidence-bearing compatibility, exclusion, and precedence clauses that persist as retrieval constraints.",
        "memory compatibility clause registry",
        "共同检索组合、独立任务结果和冲突解释标签。",
        "Co-retrieval combinations, independent task outcomes, and conflict-explanation labels.",
        "未见任务与未见记忆组合上的共同检索成功率。",
        "Co-retrieval success on unseen tasks and unseen memory combinations.",
        "相似度去重、矛盾保留、全部检索、图聚类和直接风险门控。",
        "Similarity deduplication, contradiction preservation, retrieve-all, graph clustering, and direct risk gating.",
        "构造 20–40 条可独立验证记忆，训练在部分组合上，冻结后评测未见二元和三元组合。",
        "Use 20–40 independently verifiable memories, train on a subset of combinations, and freeze for unseen pair and triple compositions.",
        "若兼容子句不能跨组合泛化，或简单相似度／冲突检测同样有效，则作为记忆管理组件保留。",
        "Retain only as a memory-management component if clauses fail to generalize or simple similarity/conflict checks match performance.",
        ("ALFWorld", "AgentBench subset", "memory interaction harness"), (5,5,5,4,4,4),
    ),
    candidate(
        "cross-model-memory-translation-operator", "跨模型记忆翻译算子", "Cross-Model Memory Translation Operator",
        "new-combination", ("model-swap-compatibility-certificate", "asset-level-model-swap-certificate"), "discussion",
        "同一条自然语言经验在不同基础模型上可能触发不同推理模式，兼容性预测只能发现问题，不能修复。",
        "The same natural-language memory can trigger different reasoning across backbones; compatibility prediction detects but does not repair the problem.",
        ("canonical behavior anchors", "asset transformation", "cycle consistency"),
        "把源模型上的经验转换为目标模型专用记忆，同时约束源任务行为锚点、圈外行为锚点和双向翻译一致性；学习对象是记忆变换器而不是兼容性分数。",
        "Transform source-model memories into target-model-specific assets while preserving source-task and out-of-loop behavior anchors plus cycle consistency; the learned object is a translator, not a score.",
        "cross-model memory translator",
        "源／目标模型在锚点任务上的行为差和翻译后效用。",
        "Source/target behavior gaps on anchor tasks and utility after translation.",
        "目标模型上的持久成功、负迁移和锚点保持。",
        "Persistent success, negative transfer, and anchor preservation on target models.",
        "直接复制、目标模型重写、PromptBridge、MASA 和语义改写。",
        "Direct copy, target-model rewriting, PromptBridge, MASA, and semantic rewriting.",
        "三个开放模型家族、两类任务和 60–100 条经验，留出目标模型家族与经验类别。",
        "Use three open model families, two domains, and 60–100 memories with held-out target families and memory categories.",
        "若变换器不能优于目标模型直接重写，或锚点保持以牺牲任务效用为代价，则停止。",
        "Stop if the translator does not beat direct target-model rewriting or preserves anchors only by sacrificing utility.",
        ("Qwen2.5-7B-Instruct", "Llama-3.1-8B-Instruct", "Mistral-7B-Instruct", "ALFWorld"), (5,5,4,4,3,5),
    ),
    candidate(
        "update-composition-repair-compiler", "更新组合修复编译器", "Update-Composition Repair Compiler",
        "new-combination", ("compositional-update-compatibility", "restoration-clause-learning"), "discussion",
        "检测到 Prompt、记忆和工作流更新不兼容后，现有方法通常只拒绝组合或回滚一个更新。",
        "After detecting incompatible prompt, memory, and workflow updates, existing methods usually reject the composition or roll back one update.",
        ("typed update descriptors", "compatibility clause induction", "graph rewrite compiler"),
        "从失败组合与成功邻域中学习兼容子句，再编译最小重排、条件化或桥接补丁，使原更新尽量都被保留。",
        "Learn compatibility clauses from failed compositions and successful neighbors, then compile minimal reordering, conditioning, or bridge patches that preserve as many original updates as possible.",
        "versioned multi-surface update program",
        "更新组合干预、失败模块和独立回归套件结果。",
        "Update-composition interventions, failing modules, and independent regression-suite outcomes.",
        "未见组合上恢复目标能力且不损害已通过能力。",
        "Restoration on unseen compositions without harming mastered capabilities.",
        "直接拒绝、最后更新回滚、Delta Debugging、人工重排和风险门控。",
        "Direct rejection, last-update rollback, delta debugging, manual reordering, and risk gating.",
        "在 4–8 个版本化更新中构造单点、双点和顺序故障，比较保留更新数、恢复率和额外测试成本。",
        "Construct single, pairwise, and order faults over 4–8 versioned updates and compare retained updates, recovery, and testing cost.",
        "若编译器只是在更贵地搜索已有重排，或保留更新数不优于最小回滚，则降级为工具。",
        "Demote to a tool if it only performs costlier search over known reorderings or fails to retain more updates than minimal rollback.",
        ("ALFWorld", "WebArena-Lite", "versioned update harness"), (5,5,5,4,4,4),
    ),
    candidate(
        "minimal-stabilizing-patch-search", "最小稳定化补丁搜索", "Minimal Stabilizing Patch Search",
        "new-combination", ("agent-update-trust-region", "active-causal-minimal-rollback"), "discussion",
        "某个更新修复目标失败却破坏其他能力时，回滚会丢失目标收益，继续提交又会留下回退。",
        "When an update fixes the target but harms other capabilities, rollback loses the gain while commit preserves regression.",
        ("active counterexample search", "small patch grammar", "trust-region acceptance"),
        "固定原更新，仅在小型补丁语法中主动搜索最小稳定化补丁；补丁必须恢复回归套件且不抹掉目标收益。",
        "Freeze the original update and actively search a small patch grammar for the minimal stabilizer that restores regressions without erasing target gains.",
        "stabilizing patch attached to an update commit",
        "回归反例、补丁执行结果和目标能力保持。",
        "Regression counterexamples, patch outcomes, and target-gain retention.",
        "独立目标测试与回归测试上的双重恢复。",
        "Joint restoration on independent target and regression suites.",
        "完整回滚、重新训练原更新、通用 Prompt 修补、信赖域拒绝。",
        "Full rollback, retraining the original update, generic prompt repair, and trust-region rejection.",
        "选择 Prompt 或记忆单一更新表面，限制补丁语法和调用预算，在两个任务域测试。",
        "Use one prompt or memory update surface, bound the patch grammar and call budget, and test in two domains.",
        "若需要与原更新同规模的重写，或补丁不能跨 seed 保持，则停止。",
        "Stop if stabilization requires a rewrite as large as the original update or fails across seeds.",
        ("ALFWorld", "AgentBench subset", "bounded patch grammar"), (5,5,5,4,4,4),
    ),
    candidate(
        "evaluator-anchor-residual-corrector", "评价器锚点残差修正器", "Evaluator Anchor-Residual Corrector",
        "new-combination", ("evaluator-coadaptation-guard", "actor-evaluator-residual-gate"), "discussion",
        "执行者与评价器共同更新时，交互残差能发现偏差，但单纯拒绝提交不会改善评价器。",
        "When actor and evaluator co-evolve, interaction residuals can expose bias, but commit rejection does not improve the evaluator.",
        ("cross-version score factorization", "independent anchor tasks", "residual correction head"),
        "用跨版本评分矩阵分离 actor 能力、任务难度和 evaluator 偏置，再训练小型残差修正头，使锚点任务排序与外部真值一致。",
        "Factor cross-version scores into actor ability, task difficulty, and evaluator bias, then train a small residual corrector aligned to independent anchor-task rankings.",
        "small evaluator correction head",
        "跨版本评分、外部锚点排序和未来轮次偏差。",
        "Cross-version scores, external anchor rankings, and future-round bias.",
        "冻结外部验证器上的真实能力与排序稳定性。",
        "True capability and ranking stability under a frozen external verifier.",
        "冻结评价器、评价器 Ensemble、CREAM 式一致性和普通 Pairwise Fine-tuning。",
        "Frozen evaluator, evaluator ensemble, CREAM-style consistency, and ordinary pairwise fine-tuning.",
        "构造 6–10 轮 actor/evaluator 版本，留出未来版本并匹配评价调用。",
        "Construct 6–10 actor/evaluator rounds, hold out future versions, and match evaluator calls.",
        "若修正头只提高锚点拟合而不提高圈外策略选择，则作为校准组件保留。",
        "Retain only as calibration if it improves anchor fit but not out-of-loop policy selection.",
        ("open-weight actor/evaluator pairs", "independent anchor tasks"), (5,5,4,4,4,4),
    ),
    candidate(
        "counterfactual-rubric-rewrite", "反事实 Rubric 重写", "Counterfactual Rubric Rewrite",
        "new-combination", ("reward-invariance-audit", "evaluator-coadaptation-guard"), "discussion",
        "评价器失败往往来自 Rubric 某个条件缺失或权重错误，整体微调难以解释且可能破坏其他评分维度。",
        "Evaluator failures often come from missing rubric conditions or wrong weights; full fine-tuning is hard to interpret and may damage other criteria.",
        ("rubric atomization", "counterfactual examples", "minimal rubric edit"),
        "把 Rubric 分解为可执行原子，通过独立因果／中性干预定位缺失或过强原子，再学习最小新增、删除或重加权编辑。",
        "Atomize the rubric, use independent causal and neutral interventions to localize missing or over-weighted atoms, then learn minimal add/delete/reweight edits.",
        "versioned evaluator rubric",
        "干预对、Rubric 原子激活和独立任务结果。",
        "Intervention pairs, rubric-atom activation, and independent task outcomes.",
        "未见任务上的排序改进与中性维度保持。",
        "Ranking improvement and neutral-dimension preservation on unseen tasks.",
        "整体 Reward 微调、Prompt 重写、冻结 Rubric、CROME／PRISM。",
        "Full reward fine-tuning, prompt rewriting, frozen rubric, and CROME/PRISM.",
        "在程序可验证任务中构造 3–5 类 Rubric 故障，比较编辑大小、排序正确率和中性保持。",
        "Inject 3–5 rubric fault types in verifier-rich tasks and compare edit size, ranking correctness, and neutral preservation.",
        "若最小编辑不能优于完整微调的圈外表现，或需要同一评价器自证，则停止。",
        "Stop if minimal edits do not beat full fine-tuning out of loop or require evaluator self-validation.",
        ("programmatic verifier", "open-weight reward/evaluator model"), (5,5,5,4,4,4),
    ),
    candidate(
        "simulator-free-risk-program-distillation", "无模拟器部署的风险程序蒸馏", "Simulator-Free Risk Program Distillation",
        "new-combination", ("irreversible-action-counterfactuals", "simulator-distilled-risk-memory"), "discussion",
        "不可逆动作的反事实后果可由模拟器发现，但部署时持续调用模拟器既昂贵又不算持久学习。",
        "Simulators can reveal irreversible consequences, but deployment-time simulator calls are expensive and not persistent learning.",
        ("verified counterfactual generation", "typed risk program synthesis", "simulator-off freeze"),
        "发现阶段用独立转移验证器生成反事实状态替换，把结果编译为带前置条件、例外和弃权的类型化风险程序，冻结后完全关闭模拟器。",
        "Use an independent transition verifier during discovery to generate counterfactual substitutions, compile them into typed risk programs with preconditions, exceptions, and abstention, then disable the simulator entirely.",
        "versioned risk program library",
        "状态替换、动作后果、程序覆盖与冲突。",
        "State substitutions, action consequences, program coverage, and conflicts.",
        "模拟器关闭后未见状态上的不可逆错误与任务成功。",
        "Irreversible errors and task success on unseen states with the simulator disabled.",
        "在线模拟器、自然语言反思、AutoSpec／AgentSpec 类规则、固定安全 Prompt。",
        "Online simulator, verbal reflection, AutoSpec/AgentSpec-style rules, and fixed safety prompts.",
        "选择一个精确转移环境，独立生成／接纳／评测验证器，冻结后迁移到第二转移系统。",
        "Use one exact-transition environment with separate generation/admission/evaluation verifiers, then freeze and transfer to a second transition system.",
        "若不能脱离模拟器保持收益，或可归约为现有规则归纳，则作为安全基准组件保留。",
        "Retain only as a safety benchmark component if gains vanish without the simulator or reduce to existing rule induction.",
        ("PDDL-style verifier", "ALFWorld-like environment", "second transition system"), (5,5,5,4,3,4),
    ),
    candidate(
        "workflow-failure-motif-rewriter", "工作流失败模式重写器", "Workflow Failure-Motif Rewriter",
        "new-combination", ("workflow-generalization-certificate", "workflow-branch-credit"), "discussion",
        "工作流在新 API 或任务图模式上失败时，证书只能拒绝提交，无法学习如何修复控制流。",
        "When workflows fail on new APIs or task motifs, certificates can reject commits but do not learn how to repair control flow.",
        ("failure-motif mining", "graph rewrite templates", "frozen transfer"),
        "从失败轨迹和成功邻域中提取缺失检查、错误分支、工具顺序和恢复节点模式，学习最小图重写模板并冻结到未见 API。",
        "Mine missing checks, wrong branches, tool order, and recovery motifs from failed traces and successful neighbors, then learn minimal graph-rewrite templates frozen to unseen APIs.",
        "workflow rewrite-template library",
        "失败轨迹、图差分、独立任务结果和工具语义。",
        "Failure traces, graph diffs, independent outcomes, and tool semantics.",
        "未见 API 与未见任务图模式上的修复成功率。",
        "Repair success on unseen APIs and unseen task-graph motifs.",
        "AFlow、人工工作流修复、性能预测器、通用代码补丁。",
        "AFlow, manual workflow repair, performance predictors, and generic code repair.",
        "独立生成 200 个小工作流故障，训练部分 motif，留出 API 与 motif 双重迁移。",
        "Generate 200 small workflow faults, train on a subset of motifs, and hold out both APIs and motifs.",
        "若模板只记住 API 名称，或通用图修复同样有效，则降级为工程工具。",
        "Demote to engineering if templates memorize API names or generic graph repair matches performance.",
        ("WebArena-Lite", "ToolBench subset", "workflow graph extractor"), (5,5,4,4,4,4),
    ),
    candidate(
        "api-semantic-workflow-compiler", "API 语义工作流编译器", "API-Semantic Workflow Compiler",
        "new-combination", ("model-swap-compatibility-certificate", "workflow-generalization-certificate"), "discussion",
        "工作流通常绑定具体工具 schema，更换等价 API 后需要人工重写。",
        "Workflows are tied to concrete tool schemas and often need manual rewriting for semantically equivalent APIs.",
        ("canonical tool semantics", "workflow intermediate representation", "target API compilation"),
        "把工作流编译到带前置条件、效果和错误语义的中间表示，再为目标 API 生成调用绑定和恢复分支；训练目标是行为保持而非文本相似。",
        "Compile workflows into an intermediate representation with preconditions, effects, and error semantics, then generate target-API bindings and recovery branches under behavior-preservation objectives.",
        "portable workflow intermediate representation",
        "源／目标 API 执行轨迹、状态效果和失败语义。",
        "Source/target API traces, state effects, and failure semantics.",
        "未见 API 上的行为等价、成功率和恢复能力。",
        "Behavioral equivalence, success, and recovery on unseen APIs.",
        "手工 schema 映射、SkCC、语义相似度和直接 LLM 重写。",
        "Manual schema mapping, SkCC, semantic similarity, and direct LLM rewriting.",
        "使用两组等价工具 API 和留出第三组，冻结 IR 与编译器，匹配调用预算。",
        "Use two equivalent API families and hold out a third while freezing the IR and compiler under matched calls.",
        "若行为等价仅在训练 API 成立，或 IR 无法覆盖错误恢复，则停止。",
        "Stop if equivalence holds only on training APIs or the IR cannot express error recovery.",
        ("ToolBench subset", "three equivalent API families", "execution verifier"), (5,5,4,4,4,4),
    ),
]

CANDIDATES += [
    candidate(
        "update-conditioned-permission-lease", "更新条件化的权限租约", "Update-Conditioned Permission Lease",
        "new-combination", ("update-aware-permission-downgrade", "behavior-triggered-privilege-lease"), "discussion",
        "Agent 更新后沿用旧权限会产生新越权，永久最低权限又损害任务效用。", "Inherited permissions can create new overreach after an agent update, while permanent minimum privilege harms utility.",
        ("update-diff risk model", "task-bounded lease", "independent reauthorization probes"),
        "根据 Prompt、记忆、技能或工作流 diff 预测受影响权限与最小临时权限集，并用独立 Canary 决定逐级续租。", "Predict affected permissions and a minimal temporary set from prompt, memory, skill, or workflow diffs, then renew authority stepwise using independent canaries.",
        "versioned permission lease state",
        "更新 diff、Canary 结果、越权和任务效用。", "Update diffs, canary outcomes, overreach, and task utility.",
        "未见更新算子上的安全—效用结果。", "Safety-utility outcomes on unseen update operators.",
        "静态最小权限、ABAC/MAC、统一降权和完整重认证。", "Static least privilege, ABAC/MAC, uniform downgrade, and full reauthorization.",
        "在 ToolPrivBench/AuthBench 风格任务上训练三种更新类型并留出第四种。", "Train on three update types and hold out a fourth on ToolPrivBench/AuthBench-style tasks.",
        "若收益来自永久禁权，或留出更新类型上无法校准，则降级为治理组件。", "Demote to governance if gains come from permanent denial or calibration fails on held-out update types.",
        ("ToolPrivBench-style tasks", "AuthBench-style tasks", "versioned agent harness"), (5,5,4,4,4,5),
    ),
    candidate(
        "correction-action-causal-compiler", "纠错动作因果编译器", "Correction-Action Causal Compiler",
        "new-combination", ("correction-policy-credit", "failure-localization-before-reflection"), "discussion",
        "整段反思混合观察、规划、工具和执行错误，成功纠正也无法说明哪类动作必要。", "Whole-trajectory reflection mixes observation, planning, tool, and execution errors, so success does not identify necessary correction actions.",
        ("typed correction actions", "leave-one-action-out interventions", "persistent correction program"),
        "把纠错拆成观察、计划、工具和动作替换，通过最小干预估计必要性，再把有效组合编译为带适用条件的纠错程序。", "Decompose correction into observation, plan, tool, and action replacements, estimate necessity via minimal interventions, and compile effective combinations into applicability-bounded programs.",
        "typed correction-program library",
        "模块替换结果、错误类型和独立任务成功。", "Module-replacement outcomes, failure types, and independent task success.",
        "未见失败组合上的成功率、必要性和误用率。", "Success, necessity, and misuse on unseen failure combinations.",
        "整轨迹反思、REFLECT/InT、成功轨迹 SFT 和 leave-one-step-out。", "Whole-trajectory reflection, REFLECT/InT, success-trace SFT, and leave-one-step-out attribution.",
        "在 verifier-rich 工具环境中构造四类错误与组合错误，冻结后迁移到第二域。", "Create four error types and compositions in a verifier-rich tool environment, then freeze and transfer to a second domain.",
        "若类型化程序不能比模块级反思更好迁移，或真值不独立，则停止。", "Stop if typed programs do not transfer better than module-level reflection or ground truth is not independent.",
        ("ALFWorld", "ToolBench subset", "module replacement harness"), (5,5,5,4,4,4),
    ),
    candidate(
        "checkpoint-discriminative-curriculum-learner", "Checkpoint 判别型课程学习", "Checkpoint-Discriminative Curriculum Learner",
        "new-combination", ("failure-frontier-curriculum", "regression-probe-half-life"), "discussion",
        "按难度或失败率选任务，未必能判断相邻版本是否真的变好。", "Difficulty- or failure-based curricula may not reveal whether adjacent versions truly improve.",
        ("adjacent-version paired replay", "task information gain", "probe survival model"),
        "同时估计任务对相邻版本的判别效应和未来有效半衰期，选择能持续区分真实改进而非偶然波动的课程。", "Jointly estimate adjacent-version discrimination and future utility half-life, selecting tasks that distinguish real improvement from noise over time.",
        "versioned curriculum and probe registry",
        "相邻 Checkpoint 配对结果、版本时间和任务覆盖。", "Paired adjacent-checkpoint outcomes, version time, and task coverage.",
        "留出版本上的真实能力趋势与课程收益。", "True capability trends and curriculum gain on held-out versions.",
        "失败率、难度、学习进度、IRT 和随机课程。", "Failure-rate, difficulty, learning-progress, IRT, and random curricula.",
        "至少使用两条真实 5–8 轮版本流，用早期轮次学习并冻结到后续轮次。", "Use at least two real 5–8-round version streams, learn on early rounds, and freeze for later rounds.",
        "若只在合成版本流成立，或不优于 learning-progress，则列为评测方向。", "Keep as evaluation only if it works solely on synthetic streams or fails to beat learning progress.",
        ("multi-round version logs", "ALFWorld", "AgentBench subset"), (5,5,4,4,3,4),
    ),
    candidate(
        "probe-mutation-retirement-policy", "Probe 变异与退役策略", "Probe Mutation and Retirement Policy",
        "new-combination", ("regression-probe-half-life", "change-triggered-regression-exams"), "discussion",
        "旧 Probe 会失去预测价值，但简单退役可能删除仍重要的边界测试。", "Old probes decay, but simple retirement may delete tests that still protect important boundaries.",
        ("probe half-life", "counterexample mutation", "budgeted portfolio policy"),
        "学习 Probe 的未来价值，并在退役前生成保持原失败边界但改变表面形式的变异 Probe；策略在保留、变异、合并和退役之间分配固定预算。", "Learn future probe value and mutate probes before retirement to preserve the original failure boundary under new surface forms, allocating a fixed budget across keep, mutate, merge, and retire.",
        "evolving regression-probe portfolio",
        "历史版本命中、Probe 谱系、变异结果和更新 diff。", "Historical hits, probe lineage, mutation outcomes, and update diffs.",
        "未来版本回退召回、冗余率和测试成本。", "Future-regression recall, redundancy, and testing cost.",
        "全部保留、半衰期退役、IRT、随机变异和固定回归集。", "Keep-all, half-life retirement, IRT, random mutation, and fixed suites.",
        "在两条版本流上固定总 Probe 数，比较未来召回和陈旧测试比例。", "Fix total probe count on two version streams and compare future recall and stale-test share.",
        "若变异只增加难度而不提高召回，或不优于 keep-all 成本前沿，则停止。", "Stop if mutation only raises difficulty without recall or does not beat the keep-all cost frontier.",
        ("multi-round version logs", "probe generator", "independent full suite"), (5,5,4,4,4,5),
    ),
]
CANDIDATES += [
    candidate(
        "restoration-clause-induction", "恢复子句归纳", "Restoration-Clause Induction",
        "revived", ("active-causal-minimal-rollback", "restoration-clause-learning"), "revival",
        "最小回滚只能修复当前版本，未来出现相似更新组合时仍会重复回退。", "Minimal rollback repairs the current version but does not prevent similar future update compositions from regressing again.",
        ("stochastic rollback interventions", "typed descriptor language", "probabilistic clause induction"),
        "在固定类型化更新描述符语言中，从带噪回滚干预归纳 no-good、兼容和前置子句，并给子句附带置信度、过期条件和误阻断预算。", "Induce no-good, compatibility, and prerequisite clauses from noisy rollback interventions in a fixed typed descriptor language, with confidence, expiry, and false-block budgets.",
        "persistent update-compatibility clause grammar",
        "更新组合干预、恢复结果、描述符和误阻断反馈。", "Update-composition interventions, restoration outcomes, descriptors, and false-block feedback.",
        "未见更新组合上的回退预防与误阻断率。", "Regression prevention and false-block rate on unseen update compositions.",
        "ProbDD/PMA、直接风险门控和 ANNEAL/SKILL.nb 类符号补丁。", "ProbDD/PMA, direct risk gating, and ANNEAL/SKILL.nb-style symbolic patches.",
        "冻结描述符语言，在合成与真实版本历史中比较子句泛化、误阻断和保留收益。", "Freeze the descriptor language and compare clause generalization, false blocks, and retained gains on synthetic and real histories.",
        "若子句不能优于同一干预历史训练的直接风险门控，或语言需按任务人工重写，则返回 repair。", "Return to repair if clauses do not beat a direct risk gate trained on the same interventions or require task-specific language redesign.",
        ("versioned update harness", "ALFWorld", "WebArena-Lite"), (5,5,5,4,3,4),
        "必须把学习对象从一次性故障集合改成可泛化的持久兼容子句，并冻结类型语言。", "Revives only by changing the learned object from a one-off fault set to generalizable persistent compatibility clauses in a frozen typed language.",
    ),
    candidate(
        "randomized-retrieval-mediated-memory-policy", "随机检索介导的记忆策略", "Randomized Retrieval-Mediated Memory Policy",
        "revived", ("randomized-memory-action-policy", "future-reuse-harm-predictor"), "revival",
        "记忆动作会经过未来检索暴露和条目间干扰产生延迟影响，标准上下文 Bandit 忽略这一结构。", "Memory actions act through future retrieval exposure and entry interference, which standard contextual bandits ignore.",
        ("entry-action randomization", "retrieval mediation", "interference-aware policy learning"),
        "分别随机化记忆动作与未来检索暴露，显式建模条目干扰和延迟中介，再学习写入、摘要、隔离和删除策略。", "Randomize memory actions and future retrieval exposure separately, model entry interference and delayed mediation, then learn write, summarize, quarantine, and delete policies.",
        "interference-aware memory-action policy",
        "动作随机化、检索随机化、共同检索集合和未来结果。", "Action randomization, retrieval randomization, co-retrieval sets, and future outcomes.",
        "独立环境奖励下的动作特异总效应与介导效应。", "Action-specific total and mediated effects under independent rewards.",
        "标准 Doubly-Robust Bandit、A-MAC 和无干扰记忆控制。", "Standard doubly robust bandits, A-MAC, and no-interference memory control.",
        "在小型记忆池中控制条目数量和共同检索，比较干扰感知策略与标准 Bandit。", "Control pool size and co-retrieval in a small memory bank and compare against standard bandits.",
        "若显式中介与干扰项不能改善圈外决策，或随机化成本过高，则保留为因果分析。", "Retain as causal analysis if mediation/interference does not improve out-of-loop decisions or randomization cost is prohibitive.",
        ("ALFWorld", "WebArena-Lite", "randomized retrieval harness"), (5,5,5,4,3,3),
        "必须引入记忆特有的检索中介与条目干扰，并证明相同日志上的标准 Bandit 不能复现。", "Revives only with memory-specific retrieval mediation and entry interference that standard bandits on the same logs cannot reproduce.",
    ),
    candidate(
        "transport-calibrated-lesson-specializer", "迁移校准的经验专化器", "Transport-Calibrated Lesson Specializer",
        "revived", ("cross-task-effect-transport-certificate", "applicability-bounded-lessons"), "revival",
        "经验在源任务上有效，但在未见任务族中可能只适用于部分状态；单纯证书只能弃权。", "A lesson may help on its source task yet apply only to a subset of states in unseen task families; a certificate can only abstain.",
        ("effect transport", "support-set specialization", "conformal sign-risk control"),
        "学习跨任务稳定支持集合，并在不确定区域自动收缩经验前置条件；输出被专化的持久经验，而不是迁移分数。", "Learn cross-task stable support sets and shrink lesson preconditions in uncertain regions, producing a specialized persistent lesson rather than a transfer score.",
        "specialized lesson with calibrated support set",
        "多任务 matched replay、状态约束特征和任务族级校准残差。", "Multi-task matched replay, state-constraint features, and family-level calibration residuals.",
        "留出任务族上的效应符号、覆盖与错误调用率。", "Effect sign, coverage, and misuse on held-out task families.",
        "Conformal R-learner、语义相似度、源任务准入、SkillCAT 和固定边界。", "Conformal R-learner, semantic similarity, source admission, SkillCAT, and fixed boundaries.",
        "用足够多任务族做分层校准，冻结后在第二模型和新任务族上评测专化经验。", "Use enough task families for hierarchical calibration, then freeze and evaluate specialized lessons on a second model and unseen families.",
        "若只靠覆盖率坍缩降低错误，或不优于带弃权的效应预测器，则返回 component。", "Return to component if error falls only through coverage collapse or it fails to beat an abstaining effect predictor.",
        ("multiple task families", "Qwen/Llama open models", "matched replay harness"), (5,5,4,4,3,5),
        "必须从预测效应升级为真正改变经验适用集合的持久专化算子。", "Revives only by changing from effect prediction to a persistent specialization operator that edits the lesson's applicability set.",
    ),
]
CANDIDATES += [
    candidate(
        "intervention-certified-reward-repair", "干预认证的 Reward 修复", "Intervention-Certified Reward Repair",
        "revived", ("reward-invariance-audit", "counterfactual-rubric-rewrite"), "revival",
        "Reward 审计能发现捷径或漂移，但不会生成更可靠的持久评价器。", "Reward audits reveal shortcuts or drift but do not create a more reliable persistent evaluator.",
        ("independent causal/neutral interventions", "rubric atom repair", "trust-region update"),
        "用独立认证的因果与中性干预定位 Rubric 原子，再训练小型修正头或最小 Rubric 编辑，同时限制中性维度和外部锚点上的变化。", "Use independently certified causal and neutral interventions to localize rubric atoms, then train a small corrector or minimal rubric edit under neutral-dimension and external-anchor constraints.",
        "versioned reward rubric plus correction head",
        "干预对、Rubric 激活、外部锚点和下游候选结果。", "Intervention pairs, rubric activation, external anchors, and downstream candidate outcomes.",
        "冻结下游策略选择与中性维度保持。", "Frozen downstream policy selection and neutral-dimension preservation.",
        "CROME、PRISM、普通 Pairwise Fine-tuning、冻结 Reward 和只做审计。", "CROME, PRISM, ordinary pairwise fine-tuning, frozen reward, and audit-only baselines.",
        "在程序可验证环境中比较修正头、Rubric 编辑和完整微调，匹配数据与计算。", "Compare a corrector, rubric edits, and full fine-tuning in a verifier-rich environment with matched data and compute.",
        "若只提高干预集而不提高冻结下游选择，或同一验证器闭环监督，则返回 repair。", "Return to repair if gains are limited to the intervention set or supervision closes through the same verifier.",
        ("programmatic verifier", "open reward model", "frozen downstream candidates"), (5,5,5,4,3,4),
        "必须从审计转为明确的 Reward/Rubric 持久更新，并用独立下游选择验证。", "Revives only by becoming an explicit persistent reward/rubric update validated through independent downstream selection.",
    ),
    candidate(
        "monotone-applicability-specializer-v4", "单调适用集合专化器 v4", "Monotone Applicability-Set Specializer v4",
        "revived", ("local-counterexample-memory-repair", "monotone-applicability-specializer"), "revival",
        "自由文本反例修复会破坏原本正确的经验区域，直接删除又浪费可迁移部分。", "Free-text counterexample repair damages correct regions, while deletion wastes transferable knowledge.",
        ("executable precondition lattice", "minimal counterexample", "positive-retention constraint"),
        "把经验表示为类型化前置条件格；每个最小反例只允许添加最小约束或例外，更新必须保持未受影响正例。", "Represent lessons as a typed precondition lattice; each minimal counterexample may add only a minimal constraint or exception while retaining unaffected positives.",
        "structured lesson with executable exception lineage",
        "最小反例、未受影响正例和约束删除轨迹。", "Minimal counterexamples, unaffected positives, and constraint-deletion traces.",
        "规则适用真值、正例保持率和未见状态错误调用。", "Applicability ground truth, positive retention, and misuse on unseen states.",
        "SkillTracer、SkillAdaptor、自由文本重写、全部删除和 Assay 类选择。", "SkillTracer, SkillAdaptor, free-text rewriting, full deletion, and Assay-style selection.",
        "在规则可执行工具环境中冻结类型语言，比较最小编辑数、错误调用和正例保持。", "Freeze the typed language in an executable-rule environment and compare edit size, misuse, and positive retention.",
        "若类型语言需按任务人工设计，或与 SkillAdaptor 等价，则作为可解释组件保留。", "Retain as an interpretable component if the type language is task-specific or equivalent to SkillAdaptor.",
        ("executable tool rules", "counterexample replay harness"), (5,5,5,4,4,4),
        "必须冻结可执行类型语言，并证明单调专化比自由修复更好保持正例。", "Revives only with a frozen executable type language and evidence that monotone specialization preserves unaffected positives better than free repair.",
    ),
    candidate(
        "asset-transformation-compiler", "持久资产变换编译器", "Persistent-Asset Transformation Compiler",
        "revived", ("asset-level-model-swap-certificate", "cross-model-memory-translation-operator"), "revival",
        "资产兼容证书只能预测模型替换风险，不能把 Prompt、记忆或工作流变成目标模型可用形式。", "Asset compatibility certificates predict model-swap risk but do not transform prompts, memories, or workflows for the target model.",
        ("asset-specific canonical IR", "behavior anchors", "target compiler"),
        "先选择一种资产类别，学习规范中间表示和目标模型编译器；用源／目标行为锚点约束变换，而不是统一做兼容评分。", "Choose one asset class, learn a canonical intermediate representation and target-model compiler, and constrain transformation with source/target behavior anchors rather than a universal score.",
        "asset-specific transformation compiler",
        "源资产、目标模型行为、锚点任务和编译后效用。", "Source assets, target-model behavior, anchor tasks, and compiled utility.",
        "留出模型家族上的持久任务成功与锚点保持。", "Persistent task success and anchor preservation on held-out model families.",
        "直接复制、目标模型重写、PromptBridge、MASA、SkCC 和语义翻译。", "Direct copy, target rewriting, PromptBridge, MASA, SkCC, and semantic translation.",
        "先做记忆或工作流单一资产类别，三模型家族训练、第四家族留出。", "Start with one memory or workflow asset class, train on three model families, and hold out a fourth.",
        "若不能优于目标模型直接重写，或 IR 无法表达恢复行为，则返回 component。", "Return to component if it does not beat direct target rewriting or the IR cannot express recovery behavior.",
        ("four open model families", "ALFWorld", "behavior-anchor suite"), (5,5,4,4,3,5),
        "必须从兼容性预测改为实际变换一种资产，并冻结到未见模型家族。", "Revives only by replacing prediction with an actual transformation operator for one asset class, frozen to unseen model families.",
    ),
]
# __CANDIDATES_B__
CANDIDATES += [
    candidate(
        "workflow-branch-responsibility-rewriter", "工作流分支责任重写器", "Workflow Branch-Responsibility Rewriter",
        "revived", ("workflow-branch-credit", "workflow-failure-motif-rewriter"), "revival",
        "工作流失败可能由多个分支交互造成，单纯归因或删除分支不能保留有效路径。", "Workflow failures may arise from branch interactions, and attribution or deletion alone cannot preserve useful paths.",
        ("branch intervention credit", "interaction graph", "minimal graph rewrite"),
        "用分支启用／禁用和替换干预估计责任与交互，再学习最小控制流重写，使责任分支被条件化而非直接删除。", "Estimate branch responsibility and interactions with enable/disable and replacement interventions, then learn minimal control-flow rewrites that condition rather than delete responsible branches.",
        "versioned workflow graph",
        "分支干预、交互结果和独立任务成功。", "Branch interventions, interaction outcomes, and independent task success.",
        "未见图模式上的修复成功与有效分支保持。", "Repair success and useful-branch retention on unseen graph motifs.",
        "Shapley 分支信用、直接删除、Delta Debugging、AFlow 和人工图修复。", "Shapley branch credit, direct deletion, delta debugging, AFlow, and manual graph repair.",
        "在带可执行分支的工具环境中注入单点与交互故障，比较保留分支数和圈外成功。", "Inject single and interacting faults in executable workflows and compare retained branches and out-of-loop success.",
        "若重写不能优于最小分支删除，或责任标签依赖同一模型自评，则返回 component。", "Return to component if rewriting does not beat minimal branch deletion or responsibility labels rely on self-evaluation.",
        ("WebArena-Lite", "workflow graph harness"), (5,5,5,4,4,4),
        "必须从归因子系统升级为真实改变控制流的持久重写算子。", "Revives only by becoming a persistent control-flow rewrite operator rather than an attribution subsystem.",
    ),
    candidate(
        "typed-correction-skill-grammar", "类型化纠错技能语法", "Typed Correction Skill Grammar",
        "revived", ("correction-policy-credit", "correction-action-causal-compiler"), "revival",
        "纠错信用只能解释哪一步有用，却不能把重复纠错模式压缩成可迁移技能。", "Correction credit explains useful steps but does not compress recurring correction patterns into transferable skills.",
        ("typed failure slots", "causal action necessity", "skill grammar induction"),
        "把失败定位结果映射到观察、计划、工具和动作槽位，归纳带前置条件和最小动作序列的纠错技能语法。", "Map localized failures to observation, plan, tool, and action slots, then induce correction-skill grammars with preconditions and minimal action sequences.",
        "persistent correction-skill grammar",
        "模块替换干预、动作必要性和未来复用结果。", "Module-replacement interventions, action necessity, and future reuse outcomes.",
        "未见失败组合上的技能调用正确率和任务恢复率。", "Skill-invocation precision and task recovery on unseen failure compositions.",
        "整轨迹反思、技能摘要、成功轨迹 SFT 和模块级反思。", "Whole-trajectory reflection, skill summarization, success-trace SFT, and module-level reflection.",
        "在两类工具任务上训练三种失败组合，留出新的错误组合和第二模型。", "Train on three failure compositions across two tool domains and hold out new combinations and a second model.",
        "若语法不能比自然语言技能更好迁移，或需要人工槽位标签，则返回 repair。", "Return to repair if the grammar does not transfer better than natural-language skills or needs manual slot labels.",
        ("ALFWorld", "ToolBench subset", "failure-localization harness"), (5,5,5,4,4,4),
        "必须把纠错信用转化为可执行、可复用的持久技能语法。", "Revives only by converting correction credit into executable reusable persistent skill grammar.",
    ),
    candidate(
        "curriculum-drift-repair-controller", "课程漂移修复控制器", "Curriculum-Drift Repair Controller",
        "merged", ("curriculum-drift-controller", "checkpoint-discriminative-curriculum-learner"), "repair",
        "课程更新会逐渐偏离核心能力边界，但仅检测漂移不会恢复覆盖。", "Curriculum updates can drift away from core capability boundaries, while detection alone does not restore coverage.",
        ("coverage debt", "checkpoint discrimination", "counterexample regeneration"),
        "维护能力轴覆盖债务；当某轴判别力下降时，从历史边界任务生成新的反例课程，并在固定预算下恢复覆盖。", "Track coverage debt across capability axes; when discrimination decays, regenerate counterexample curricula from historical boundary tasks under a fixed budget.",
        "versioned curriculum registry",
        "能力轴覆盖、相邻版本判别和课程命中历史。", "Capability-axis coverage, adjacent-version discrimination, and curriculum hit history.",
        "留出版本上的边界覆盖和最坏能力回退。", "Boundary coverage and worst capability regression on held-out versions.",
        "固定课程、失败率采样、learning progress 和随机补题。", "Fixed curricula, failure-rate sampling, learning progress, and random replenishment.",
        "先用现有多轮版本日志验证覆盖债务是否预测回退，再决定是否开发控制器。", "First test whether coverage debt predicts regressions on existing multi-round logs before building the controller.",
        "若覆盖债务不能预测回退，或生成任务只重复旧题，则作为评测指标保留。", "Retain as an evaluation metric if coverage debt does not predict regressions or generated tasks only repeat old items.",
        ("multi-round version logs", "counterexample generator"), (4,4,4,3,3,4),
    ),
    candidate(
        "process-sensitive-experience-admission", "过程敏感的经验准入", "Process-Sensitive Experience Admission",
        "merged", ("outcome-equivalent-trajectory-contrast", "causally-verified-experience-admission"), "repair",
        "两个轨迹结果相同但过程风险不同，若只按成功结果写入经验，会把危险或脆弱过程固化。", "Trajectories can share outcomes but differ in process risk; outcome-only admission can persist dangerous or brittle behavior.",
        ("verified process interventions", "trajectory contrast", "persistent admission rule"),
        "对观察、工具或动作进行独立过程干预，学习哪些过程差异会改变未来复用风险，并据此写入、摘要或隔离经验。", "Apply independent process interventions to observations, tools, or actions, learn which process differences change future reuse risk, and use them for write, summarize, or quarantine decisions.",
        "process-aware experience registry",
        "过程干预、相同终点配对和未来复用结果。", "Process interventions, outcome-matched trajectory pairs, and future reuse outcomes.",
        "未来任务上的过程违规、成功和负迁移。", "Process violations, success, and negative transfer on future tasks.",
        "结果准入、轨迹相似度、因果经验准入和过程分类器。", "Outcome admission, trajectory similarity, causal admission, and process classifiers.",
        "在一个 verifier-rich 环境中构造结果相同但过程不同的轨迹，冻结准入器跨任务评测。", "Construct outcome-equivalent but process-distinct trajectories in one verifier-rich environment and freeze the admission model across tasks.",
        "若过程干预不能预测未来复用风险，或只是安全分类器，则降级为评测方向。", "Demote to evaluation if process interventions do not predict future reuse risk or reduce to a safety classifier.",
        ("verifier-rich tool environment", "trajectory intervention harness"), (5,4,5,4,3,4),
    ),
    candidate(
        "diff-conditioned-regression-test-generator", "更新差分条件化的回归测试生成", "Diff-Conditioned Regression Test Generator",
        "merged", ("change-triggered-regression-exams", "probe-mutation-retirement-policy"), "repair",
        "固定回归集与普通自适应选题不能针对本次更新中新引入的语义边界。", "Fixed regression suites and generic adaptive testing do not target semantic boundaries introduced by the current update.",
        ("update-diff parsing", "failure-boundary retrieval", "test mutation"),
        "从 Prompt、记忆、技能或工作流 diff 提取受影响约束，检索历史边界 Probe，并生成语义保持和语义改变的 matched 测试对。", "Parse affected constraints from prompt, memory, skill, or workflow diffs, retrieve historical boundary probes, and generate matched semantics-preserving and semantics-changing test pairs.",
        "versioned regression-probe registry",
        "更新 diff、历史回退、Probe 谱系和独立执行结果。", "Update diffs, historical regressions, probe lineage, and independent execution outcomes.",
        "当前更新导致的回退召回和误报。", "Recall and false positives for regressions caused by the current update.",
        "随机子集、IRT、AutoJudger、固定小回归集和 LLM 直接出题。", "Random subsets, IRT, AutoJudger, fixed suites, and direct LLM test generation.",
        "注入三类更新回退，固定生成与执行预算，比较未见更新类型上的召回。", "Inject three update-regression types under fixed generation and execution budgets and test recall on a held-out update type.",
        "若测试收益仅来自更多题目，或无法在留出更新类型上泛化，则保留为测试工具。", "Retain as a testing tool if gains come only from more items or fail to generalize to held-out update types.",
        ("ALFWorld", "WebArena-Lite", "update diff parser"), (5,4,4,3,4,4),
    ),
    candidate(
        "budgeted-evolution-tournament-controller", "预算化进化锦标赛控制器", "Budgeted Evolution Tournament Controller",
        "merged", ("budgeted-evolution-controller", "open-coscientist-tournament"), "repair",
        "进化系统常在单一候选序列上继续、提交或停止，容易早收敛且无法维持方法多样性。", "Evolution systems often continue, commit, or stop on one candidate sequence, causing premature convergence and poor method diversity.",
        ("Elo tournament", "proximity diversity", "partial-feedback budget allocation"),
        "维护多个持久更新分支，以成对锦标赛和邻近图分配探索预算；决策控制器在继续、提交、合并和停止之间分配固定调用。", "Maintain multiple persistent-update branches, allocate exploration through pairwise tournaments and proximity graphs, and budget continue, commit, merge, or stop decisions.",
        "evolution branch portfolio",
        "成对比较、分支距离、部分实验结果和成本。", "Pairwise comparisons, branch distance, partial experiment results, and cost.",
        "固定总预算下的最终最优分支、覆盖多样性和回退。", "Best final branch, diversity coverage, and regression under a fixed total budget.",
        "单轨 Bandit、固定轮数、标准 Successive Halving 和随机分配。", "Single-track bandits, fixed rounds, standard successive halving, and random allocation.",
        "先在离线可重放候选池中比较预算分配，再考虑在线 Agent 更新。", "First compare budget allocation in an offline replayable candidate pool before online agent updates.",
        "若锦标赛只改善选择效率而不产生更好持久更新，则作为搜索基础设施保留。", "Retain as search infrastructure if tournaments improve selection efficiency but not persistent updates.",
        ("offline candidate replay pool", "fixed evaluation harness"), (4,4,4,3,4,4),
    ),
    candidate(
        "multi-surface-update-program-synthesis", "多更新表面程序合成", "Multi-Surface Update Program Synthesis",
        "merged", ("update-surface-router", "update-composition-repair-compiler"), "component",
        "同一失败可能需要 Prompt、记忆和工作流的组合修复，固定路由一个表面会留下残余错误。", "One failure may require a combination of prompt, memory, and workflow repairs; routing to one surface can leave residual errors.",
        ("surface-specific edit atoms", "typed repair program", "composition verifier"),
        "在受限 DSL 中合成跨表面的最小修复程序，每个编辑原子都必须通过模块级反事实和组合回归验证。", "Synthesize minimal cross-surface repair programs in a bounded DSL, requiring module-level counterfactual and composition regression validation for every edit atom.",
        "typed multi-surface repair program",
        "模块级替换、组合执行和独立回归结果。", "Module replacements, composed execution, and independent regression outcomes.",
        "圈外任务上的完整修复与编辑成本。", "Complete repair and edit cost on out-of-loop tasks.",
        "单表面路由、穷举组合、人工修复和通用程序合成。", "Single-surface routing, exhaustive combinations, manual repair, and generic program synthesis.",
        "先在三个表面、最多两步修复的合成故障上验证，不直接作为主论文。", "First validate on synthetic faults with three surfaces and at most two edits; do not treat as a primary paper yet.",
        "若穷举小组合已经足够，或 DSL 需任务定制，则只作为系统组件。", "Keep only as a system component if small exhaustive search is sufficient or the DSL is task-specific.",
        ("three-surface repair harness",), (4,4,4,3,3,3),
    ),
    candidate(
        "contradiction-triggered-experience-splitter", "矛盾触发的经验分裂器", "Contradiction-Triggered Experience Splitter",
        "merged", ("contradiction-preserving-consolidation", "applicability-bounded-lessons"), "component",
        "压缩记忆中的矛盾如果只被保留为文本，未来检索时仍可能混在一起触发错误。", "Contradictions preserved only as text may still be retrieved together and cause errors.",
        ("contradiction detection", "support-set clustering", "conditional memory split"),
        "检测会改变结论的矛盾后，把一个经验分裂成带不同适用条件的多个子经验，并保存共同父节点与互斥检索约束。", "When a conclusion-changing contradiction appears, split one lesson into condition-specific children with a shared parent and mutually exclusive retrieval constraints.",
        "branched experience lineage",
        "矛盾对、状态条件、未来检索和任务结果。", "Contradiction pairs, state conditions, future retrievals, and task outcomes.",
        "未见状态上的正确分支选择与存储开销。", "Correct branch selection and storage cost on unseen states.",
        "保留全部矛盾、摘要、聚类和简单条件路由。", "Preserve-all contradiction memory, summarization, clustering, and simple conditional routing.",
        "在可验证条件任务中构造结论翻转矛盾，比较分裂、保留和摘要。", "Create conclusion-flipping contradictions in verifiable conditional tasks and compare splitting, preserving, and summarizing.",
        "若分裂只增加存储，或条件路由与简单聚类等价，则作为记忆组件。", "Keep as a memory component if splitting only increases storage or reduces to simple clustering.",
        ("conditional task generator", "bounded memory budget"), (4,4,4,3,4,4),
    ),
]



def _load_external() -> dict[str, list[dict[str, Any]]]:
    if not DEFAULT_EXTERNAL_JSON.exists():
        return {}
    try:
        payload = json.loads(DEFAULT_EXTERNAL_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    reviews = payload.get("reviews", {})
    return reviews if isinstance(reviews, dict) else {}


def _pareto(rows: list[dict[str, Any]]) -> list[str]:
    keys = ("problem_reality", "mechanism_necessity", "identifiability", "novelty", "feasibility", "transfer")
    front: list[str] = []
    for row in rows:
        dominated = any(
            other is not row
            and all(other["scores"][key] >= row["scores"][key] for key in keys)
            and any(other["scores"][key] > row["scores"][key] for key in keys)
            for other in rows
        )
        if not dominated:
            front.append(row["id"])
    return front


def build_idea_discovery_v4() -> dict[str, Any]:
    external = _load_external()
    rows: list[dict[str, Any]] = []
    for item in CANDIDATES:
        row = dict(item)
        reviews = external.get(row["id"], [])
        latest = reviews[-1] if reviews else {}
        row["external_reviews"] = reviews
        row["external_verdict"] = latest.get("verdict", "pending")
        row["external_confidence"] = latest.get("confidence", "")
        row["external_review_status"] = "reviewed" if reviews else "pending"
        rows.append(row)
    rows.sort(key=lambda row: (STATUS_ORDER[row["internal_status"]], -row["mean_score"], row["id"]))
    for rank, row in enumerate(rows, 1):
        row["internal_rank"] = rank
    groups = {key: [row for row in rows if row["internal_status"] == key] for key in STATUS_ORDER}
    reviewed = [row for row in rows if row["external_review_status"] == "reviewed"]
    verdicts = [row["external_verdict"] for row in reviewed]
    finalists = [row for row in rows if row["internal_status"] in {"discussion", "revival"}][:16]
    verdict_order = {"pass": 0, "revise": 1, "pending": 2, "block": 3}
    review_ranked_finalists = sorted(finalists, key=lambda row: (verdict_order.get(row["external_verdict"], 2), -row["mean_score"], row["internal_rank"]))
    for rank, row in enumerate(review_ranked_finalists, 1):
        row["external_rank"] = rank
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "target_venue": "ICLR",
        "status": "external-reviewed" if reviewed and len(reviewed) == len(finalists) else "internal-tournament",
        "policy": {
            "combinations_allowed": True,
            "combination_requirement": "Every atom must address a distinct necessary link in the real failure loop.",
            "blocked_ideas_may_revive": True,
            "revival_requires_material_change": True,
            "main_bank_unchanged_until_external_pass": True,
            "automatic_final_selection_forbidden": True,
        },
        "summary": {
            "repository_patterns": len(REPOSITORY_PATTERNS),
            "workflow_stages": len(WORKFLOW_STAGES),
            "raw_candidates": len(rows),
            "discussion": len(groups["discussion"]),
            "revival": len(groups["revival"]),
            "repair": len(groups["repair"]),
            "component": len(groups["component"]),
            "tournament_finalists": len(finalists),
            "external_reviewed": len(reviewed),
            "external_pending": len(finalists) - len(reviewed),
            "external_pass": verdicts.count("pass"),
            "external_revise": verdicts.count("revise"),
            "external_block": verdicts.count("block"),
        },
        "repository_patterns": list(REPOSITORY_PATTERNS),
        "workflow_stages": list(WORKFLOW_STAGES),
        "pareto_front_ids": _pareto(rows),
        "tournament_finalists": finalists,
        "review_ranked_finalists": review_ranked_finalists,
        "discussion": groups["discussion"],
        "revival": groups["revival"],
        "repair": groups["repair"],
        "component": groups["component"],
        "all_candidates": rows,
    }


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rows = payload.get("all_candidates", [])
    if len(rows) != 28:
        errors.append(f"expected 28 candidates, got {len(rows)}")
    if len({row.get('id') for row in rows}) != len(rows):
        errors.append("candidate ids are not unique")
    if payload.get("summary", {}).get("discussion", 0) < 12:
        errors.append("discussion shortlist is too small")
    if payload.get("summary", {}).get("revival", 0) < 6:
        errors.append("revival pool is too small")
    for row in rows:
        if len(row.get("mechanism_atoms", [])) < 1 or len(row.get("mechanism_atoms", [])) > 3:
            errors.append(f"invalid mechanism composition: {row.get('id')}")
        for field in ("real_problem", "composition_logic", "learning_signal", "independent_ground_truth", "strongest_baseline", "decisive_pilot", "stop_condition"):
            value = row.get(field)
            if not isinstance(value, dict) or not value.get("zh") or not value.get("en"):
                errors.append(f"missing bilingual {field}: {row.get('id')}")
        if row.get("lineage_type") == "revived" and not row.get("revival_condition"):
            errors.append(f"revived idea lacks revival condition: {row.get('id')}")
    return errors


def write_idea_discovery_v4(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    payload = build_idea_discovery_v4()
    errors = validate(payload)
    if errors:
        raise ValueError("Invalid Idea Discovery v4:\n- " + "\n- ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.IDEA_DISCOVERY_V4 = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(write_idea_discovery_v4()["summary"], ensure_ascii=False))
