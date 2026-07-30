from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "iclr-low-resource-ideas.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "iclr-low-resource-ideas.js"


def bi(zh: str, en: str) -> dict[str, str]:
    return {"zh": zh.strip(), "en": en.strip()}


@dataclass(frozen=True, slots=True)
class Budget:
    max_gpus: int
    gpu_hours: int
    wall_days: int
    training: str = "Freeze the foundation model; update only prompts, memory, workflows, routers, or modules below 50M parameters."


@dataclass(frozen=True, slots=True)
class IdeaSpec:
    id: str
    title: dict[str, str]
    track: str
    problem: dict[str, str]
    mechanism: dict[str, str]
    hypothesis: dict[str, str]
    collision: dict[str, str]
    nearest: tuple[str, ...]
    datasets: tuple[str, ...]
    domains: tuple[str, ...]
    budget: Budget
    operator: str
    scores: tuple[int, int, int, int, int, int, int]


REVIEW_KEYS = ("novelty", "learning_problem", "generality", "attribution", "stability", "feedback", "feasibility")

TRACKS: dict[str, dict[str, Any]] = {
    "constrained": {
        "label": bi("受约束持续进化", "Constrained continual evolution"),
        "rationale": bi("每次更新同时包含收益和回退风险；自进化应被写成带非回退、成本和安全约束的策略改进。", "Every update carries gain and regression risk; self-evolution should be constrained policy improvement."),
        "importance": bi("直接研究 ICLR 关心的学习动力学：哪些更新被接受、为何多轮改进不坍塌、收益能否圈外泛化。", "This directly studies learning dynamics, multi-round stability, and out-of-loop generalization."),
        "baseline": bi("全部接受、仅按当前任务收益接受、置信度门控、固定非回退阈值、等预算随机更新。", "Accept-all, current-task-gain filtering, confidence gates, fixed non-regression thresholds, and equal-budget random updates."),
        "models": ("Qwen2.5-7B-Instruct", "Llama-3.1-8B-Instruct", "Qwen2.5-VL-7B-Instruct"),
    },
    "credit": {
        "label": bi("失败归因与经验准入", "Failure credit and experience admission"),
        "rationale": bi("成功或失败轨迹不能直接说明哪条经验真正导致结果；需要 matched replay 和局部干预。", "Success or failure does not identify the causal lesson; matched replay and local intervention are required."),
        "importance": bi("错误归因会把偶然相关固化为长期规则，是记忆、技能、Prompt 和策略更新的共同上游问题。", "Wrong attribution turns coincidence into persistent rules across memory, skills, prompts, and policies."),
        "baseline": bi("按成功写入、语言 Critic、模型置信度、轨迹级消融、随机拒绝。", "Success-only admission, language critics, confidence, trajectory ablation, and random rejection."),
        "models": ("Qwen2.5-7B-Instruct", "Llama-3.1-8B-Instruct", "Qwen2.5-VL-7B-Instruct"),
    },
    "memory": {
        "label": bi("记忆与技能巩固", "Memory and skill consolidation"),
        "rationale": bi("持久记忆需要识别干扰、保存反例、表达适用边界，并随任务漂移修订。", "Persistent memory must detect interference, retain counterexamples, encode applicability, and adapt under drift."),
        "importance": bi("记忆是最常见的低资源更新表面，也是负迁移最容易被平均准确率掩盖的地方。", "Memory is the most common low-resource update surface and a major hidden source of negative transfer."),
        "baseline": bi("无记忆、FIFO、相似度检索、摘要记忆、固定技能库、随机删除。", "No memory, FIFO, similarity retrieval, summary memory, fixed skill libraries, and random deletion."),
        "models": ("Qwen2.5-7B-Instruct", "Llama-3.1-8B-Instruct", "Qwen2.5-VL-7B-Instruct"),
    },
    "correction": {
        "label": bi("自纠正与策略内化", "Self-correction and policy internalization"),
        "rationale": bi("第二次回答更好不等于学会纠正；必须区分额外采样、外部 Critic 和 on-policy 纠错内化。", "A better second answer is not learned correction; extra sampling, external critics, and on-policy internalization must be separated."),
        "importance": bi("自纠正是低资源自进化的重要路径，但最容易被更多推理计算伪装。", "Self-correction is a key low-resource path but is easily confounded by extra inference."),
        "baseline": bi("再次采样、Self-Refine、独立 Critic、离线 SFT、固定两轮纠正、多数投票。", "Resampling, Self-Refine, independent critics, offline SFT, fixed two-pass correction, and majority vote."),
        "models": ("Qwen2.5-7B-Instruct", "Llama-3.1-8B-Instruct", "InternVL3-8B"),
    },
    "curriculum": {
        "label": bi("课程与任务进化", "Curriculum and task evolution"),
        "rationale": bi("从失败生成新任务可推进能力边界，也会造成重复、难度膨胀、标签污染和策略漂移。", "Failure-generated tasks can move the frontier but also create duplication, difficulty inflation, contamination, and drift."),
        "importance": bi("WebRL 展示了自进化课程的潜力；关键空缺是何时产生真实圈外泛化。", "WebRL shows the potential of evolving curricula; the key question is when they yield out-of-loop generalization."),
        "baseline": bi("静态数据、随机重采样、失败重放、难度课程、WebRL 式生成、等量人工任务。", "Static data, random resampling, failure replay, difficulty curricula, WebRL-style generation, and equal-size human tasks."),
        "models": ("Qwen2.5-7B-Instruct", "Llama-3.1-8B-Instruct", "Qwen2.5-VL-7B-Instruct"),
    },
    "workflow": {
        "label": bi("工作流与更新表面搜索", "Workflow and update-surface search"),
        "rationale": bi("工作流是冻结基础模型时最灵活的学习表面，但搜索结果缺少结构信用、组合稳定性和圈外证据。", "Workflows are flexible update surfaces with frozen backbones but lack structural credit, compositional stability, and out-of-loop evidence."),
        "importance": bi("ICLR 价值在于学习可组合、可泛化且稳定的结构更新规则。", "The ICLR contribution is learning compositional, generalizable, stable structure-update rules."),
        "baseline": bi("固定工作流、Prompt 搜索、AFlow、随机图编辑、贪心修改、等成本 MCTS。", "Fixed workflows, prompt search, AFlow, random graph edits, greedy edits, and equal-cost MCTS."),
        "models": ("Qwen2.5-7B-Instruct", "Llama-3.1-8B-Instruct", "Qwen2.5-VL-7B-Instruct"),
    },
    "evaluator": {
        "label": bi("奖励与评价器进化", "Reward and evaluator evolution"),
        "rationale": bi("Actor 与 Reward/Critic 共进化会形成确认偏差和代理目标过优化；评价器更新必须用独立证据治理。", "Co-evolving actors and evaluators creates confirmation bias and proxy overoptimization; evaluator updates need independent evidence."),
        "importance": bi("反馈完整性决定所有自训练闭环是否可信。", "Feedback integrity determines whether any self-training loop is trustworthy."),
        "baseline": bi("冻结 Reward、同模型自评、独立 Reward、自进化 Reward、人工小样本校准、多 Judge。", "Frozen rewards, same-model self-evaluation, independent rewards, self-evolved rewards, small human calibration, and judge ensembles."),
        "models": ("Qwen2.5-7B-Instruct", "Llama-3.1-8B-Instruct", "Mistral-7B-Instruct-v0.3"),
    },
    "world": {
        "label": bi("世界模型与具身持续适应", "World models and embodied adaptation"),
        "rationale": bi("Agent 需要学习动作后的状态变化、不可逆后果和恢复边界，但更准的模型不一定改善决策。", "Agents need action-conditioned dynamics, irreversible outcomes, and recovery boundaries, yet accuracy may not improve decisions."),
        "importance": bi("世界模型把语言反思推进到可验证环境动态学习，并连接 Web、GUI 与具身场景。", "World models move reflection toward verifiable dynamics learning across web, GUI, and embodied settings."),
        "baseline": bi("无世界模型、语言反思、WMA、一步转移模型、树搜索、随机风险惩罚。", "No world model, verbal reflection, WMA, one-step transitions, tree search, and random risk penalties."),
        "models": ("Qwen2.5-7B-Instruct", "Llama-3.1-8B-Instruct", "OpenVLA-7B"),
    },
}

def I(
    id: str,
    zh: str,
    en: str,
    track: str,
    problem_zh: str,
    problem_en: str,
    mechanism_zh: str,
    mechanism_en: str,
    hypothesis_zh: str,
    hypothesis_en: str,
    collision_zh: str,
    collision_en: str,
    nearest: tuple[str, ...],
    datasets: tuple[str, ...],
    domains: tuple[str, ...],
    hours: int,
    scores: tuple[int, int, int, int, int, int, int],
    operator: str = "limitation-inversion",
    gpus: int = 1,
    days: int = 5,
) -> IdeaSpec:
    return IdeaSpec(
        id=id,
        title=bi(zh, en),
        track=track,
        problem=bi(problem_zh, problem_en),
        mechanism=bi(mechanism_zh, mechanism_en),
        hypothesis=bi(hypothesis_zh, hypothesis_en),
        collision=bi(collision_zh, collision_en),
        nearest=nearest,
        datasets=datasets,
        domains=domains,
        budget=Budget(gpus, hours, days),
        operator=operator,
        scores=scores,
    )


IDEAS: tuple[IdeaSpec, ...] = (
    I(
        "regression-gated-self-evolution", "回归门控自进化", "Regression-Gated Self-Evolution", "constrained",
        "Agent 修复当前失败后常直接提交更新，却不检查旧能力和圈外任务是否退化。",
        "Agents often commit an update after fixing the current failure without checking regressions on mastered and out-of-loop tasks.",
        "把每次更新视为带非回退、成本和安全约束的策略改进；仅在隔离回归集通过后 commit，否则 rollback。",
        "Treat every update as constrained policy improvement; commit only after isolated non-regression, cost, and safety tests, otherwise roll back.",
        "固定预算下，回归门控应提高未来任务收益并显著降低最坏回退率。",
        "Under fixed budgets, regression gating should improve future-task utility and reduce worst-case regression.",
        "AFlow 搜索工作流、WebRL 控制策略漂移，但没有统一的跨更新表面 commit/rollback 规则。",
        "AFlow searches workflows and WebRL controls policy drift, but neither provides a unified cross-surface commit/rollback rule.",
        ("AFlow", "WebRL", "Constrained RLHF"), ("ALFWorld", "WebArena-Lite", "MM-Vet"), ("text/tool", "web", "multimodal"), 36,
        (5,5,5,5,5,5,5), "cross-domain-analogy", 2, 7,
    ),
    I(
        "update-trust-region", "Agent 更新信赖域", "Agent Update Trust Region", "constrained",
        "平均收益相似的更新可能引发完全不同的行为分布漂移。",
        "Updates with similar average gains can induce very different behavioral distribution shifts.",
        "用轨迹 KL、动作编辑距离、工具路由和记忆检索变化定义离散 Agent 更新信赖域。",
        "Define a trust region for discrete agent updates using trajectory KL, action-edit distance, tool routing, and memory-retrieval shift.",
        "行为偏移应比文本编辑距离或当前任务收益更好预测回退。",
        "Behavioral shift should predict regressions better than textual edit distance or current-task gain.",
        "TRPO/PPO 约束参数策略，但 Prompt、记忆和工作流更新缺少对应信赖域。",
        "TRPO/PPO constrain parameter policies, while prompt, memory, and workflow updates lack an analogous trust region.",
        ("Retroformer", "TRPO", "Safe Policy Improvement"), ("ALFWorld", "AgentBench"), ("text/tool", "planning"), 20,
        (4,5,5,4,5,4,5), "pme-recombination",
    ),
    I(
        "budgeted-evolution-controller", "预算感知进化控制器", "Budgeted Evolution Controller", "constrained",
        "固定反思和更新轮数会在简单任务浪费调用，在困难任务过早停止。",
        "Fixed evolution rounds waste calls on easy tasks and stop too early on difficult ones.",
        "学习一个小型元控制器，根据边际收益、分歧、回退和成本选择继续、回滚或停止。",
        "Learn a small meta-controller that chooses continue, roll back, or stop from marginal gain, disagreement, regression, and cost.",
        "控制器应在等效性能下减少至少 30% 调用，并能跨任务族迁移。",
        "The controller should save at least 30% of calls at matched utility and transfer across task families.",
        "现有 Agent 搜索通常固定预算或 patience，停止规则没有被当作学习对象。",
        "Agent search usually fixes budgets or patience; stopping itself is rarely treated as a learning problem.",
        ("AFlow", "WebRL", "Optimal Stopping"), ("ALFWorld", "WebArena-Lite", "AgentBench"), ("text/tool", "web"), 18,
        (4,5,5,4,5,4,5), "missing-cell",
    ),
    I(
        "lineage-aware-rollback", "谱系感知回滚", "Lineage-Aware Rollback", "constrained",
        "多个更新依次提交后，出现回退时难以确定应撤销哪个祖先更新。",
        "After multiple commits, regressions do not reveal which ancestor update should be reverted.",
        "维护更新依赖图，并用分层 disable-replay 估计最小回滚集合。",
        "Maintain an update dependency graph and estimate a minimal rollback set with hierarchical disable-replay.",
        "局部回滚应比恢复最近 checkpoint 保留更多累积收益。",
        "Local rollback should preserve more accumulated gain than reverting to the latest checkpoint.",
        "软件版本控制保存谱系，但 Agent 更新的行为依赖和最小回滚尚未系统学习。",
        "Version control stores lineage, but behavioral dependencies and minimal rollback for agent updates remain underexplored.",
        ("AFlow", "Autogenesis", "Program Repair"), ("ALFWorld", "AgentBench"), ("workflow", "text/tool"), 22,
        (4,5,4,5,5,4,5), "cross-domain-analogy",
    ),

    I(
        "causally-verified-experience-admission", "因果验证经验准入", "Causally Verified Experience Admission", "credit",
        "成功轨迹常产生非因果或不可复用经验，按成功率写入会积累有害规则。",
        "Successful trajectories often yield non-causal or non-reusable lessons, making success-only admission harmful.",
        "候选经验必须在 matched replay 中改变目标失败，并对无关变化保持稳定，才允许持久写入。",
        "A candidate lesson must change the target failure in matched replay and remain stable to irrelevant changes before persistent admission.",
        "因果准入应提高未来任务收益并降低有害 commit。",
        "Causal admission should improve future-task utility and reduce harmful commits.",
        "Retroformer 学习反思、AgentRefine 学习纠错轨迹，但没有控制经验持久化前的因果准入。",
        "Retroformer learns retrospection and AgentRefine learns refinement traces, but neither governs causal admission before persistence.",
        ("Retroformer", "AgentRefine", "Counterfactual Trace Auditing"), ("ALFWorld", "WebArena-Lite", "MM-Vet"), ("text/tool", "web", "multimodal"), 40,
        (5,5,5,5,5,5,4), "objective-evaluation-mismatch", 2, 8,
    ),
    I(
        "outcome-equivalent-trajectory-contrast", "结果等价轨迹对比", "Outcome-Equivalent Trajectory Contrast", "credit",
        "相同终点成功可由可靠过程或偶然捷径产生，结果奖励无法区分两者。",
        "The same successful endpoint can arise from reliable behavior or accidental shortcuts, which outcome rewards cannot distinguish.",
        "对比终点相同但过程不同的轨迹，只保留跨有效过程稳定的经验。",
        "Contrast trajectories with identical outcomes but different processes and retain only lessons stable across valid processes.",
        "跨成功过程稳定的经验应比单轨迹反思具有更强圈外迁移。",
        "Lessons stable across successful processes should transfer better than single-trajectory reflections.",
        "过程奖励通常需要人工标注；结果等价配对可以提供低监督替代。",
        "Process rewards often require labels; outcome-equivalent pairing provides a low-supervision alternative.",
        ("Process Reward Models", "Retroformer", "TPER"), ("ALFWorld", "WebArena-Lite"), ("text/tool", "web"), 24,
        (5,5,5,4,4,4,5), "contradiction-resolution",
    ),
    I(
        "applicability-bounded-lessons", "带适用边界的经验学习", "Applicability-Bounded Lesson Learning", "credit",
        "自然语言经验被过度泛化到表面相似但约束不同的状态。",
        "Natural-language lessons are overgeneralized to superficially similar states with different constraints.",
        "每条经验同时保存支持条件、最小反例和弃权区域。",
        "Store support conditions, minimal counterexamples, and abstention regions with every lesson.",
        "带边界经验应保持正迁移，同时减少跨任务错误调用。",
        "Bounded lessons should preserve positive transfer while reducing erroneous cross-task invocation.",
        "AgentRefine 改善纠错泛化，但不显式维护每条持久经验的适用域。",
        "AgentRefine improves refinement generalization but does not explicitly maintain lesson applicability.",
        ("AgentRefine", "Memory Skill", "Selective Prediction"), ("ALFWorld", "AgentBench", "MM-Vet"), ("text/tool", "multimodal"), 20,
        (4,5,5,4,4,4,5), "assumption-removal",
    ),
    I(
        "failure-localization-before-reflection", "先定位后反思", "Failure Localization Before Reflection", "credit",
        "整条轨迹反思混合感知、规划、工具和执行错误，生成的经验难以验证。",
        "Whole-trajectory reflection mixes perception, planning, tool, and execution errors, making lessons hard to verify.",
        "先用最小观察/计划/工具/动作替换定位失败模块，再只允许对应模块生成更新。",
        "Localize the failing module with minimal observation, plan, tool, or action replacements before generating an update.",
        "模块定位正确时，模块专属更新应优于全局反思。",
        "Correct localization should make module-specific updates outperform global reflection.",
        "Retroformer 生成根因总结，但缺少可执行的模块级干预真值。",
        "Retroformer summarizes root causes but lacks executable module-level intervention ground truth.",
        ("Retroformer", "Causal Tracing", "Program Repair"), ("AgentBench", "WebArena-Lite"), ("text/tool", "web"), 28,
        (5,5,4,5,4,4,4), "limitation-inversion",
    ),

    I(
        "retrieval-interference-auditor", "检索干扰审计器", "Retrieval Interference Auditor", "memory",
        "记忆提高平均性能，却可能在少数未见任务上强烈误导。",
        "Memory can improve averages while strongly harming some unseen tasks.",
        "对每次检索执行有记忆、打乱记忆、无记忆三臂 matched replay，估计条目级帮助与伤害。",
        "Run matched replay with retrieved, shuffled, and no memory to estimate entry-level benefit and harm.",
        "隔离识别出的有害条目后，应恢复圈外任务且保留主要收益。",
        "Quarantining harmful entries should recover out-of-loop tasks without erasing main gains.",
        "现有记忆 Agent 关注相关性，本方法关注持久记忆的因果负效应。",
        "Memory agents focus on relevance; this targets causal harm from persistence.",
        ("Reflexion", "Memory Agents", "Causal Retrieval"), ("ALFWorld", "HotpotQA", "MM-Vet"), ("text/tool", "knowledge", "multimodal"), 24,
        (5,5,5,5,5,5,5), "objective-evaluation-mismatch",
    ),
    I(
        "local-counterexample-memory-repair", "局部反例记忆修复", "Local Counterexample Memory Repair", "memory",
        "一条错误反例会触发整条记忆删除或重写，丢失仍然有效的部分。",
        "A single counterexample often triggers whole-memory deletion or rewrite, destroying still-valid knowledge.",
        "用最小反例只收缩适用边界，并保留原规则、例外和修订谱系。",
        "Use minimal counterexamples to shrink applicability while preserving the original rule, exceptions, and lineage.",
        "局部修复应同时提高反例修复率和旧正例保持率。",
        "Local repair should improve both counterexample repair and old-positive retention.",
        "continual learning 研究参数遗忘；这里研究 Agent 记忆的局部语义修复。",
        "Continual learning studies parameter forgetting; this studies local semantic repair of agent memory.",
        ("Continual Learning", "Program Repair", "Memory Skill"), ("ALFWorld", "AgentBench", "MM-Vet"), ("text/tool", "multimodal"), 22,
        (5,5,5,5,5,4,5), "cross-domain-analogy",
    ),
    I(
        "contradiction-preserving-consolidation", "保留矛盾的记忆巩固", "Contradiction-Preserving Memory Consolidation", "memory",
        "记忆压缩倾向保留共识摘要，丢掉能推翻规则的少数反证。",
        "Memory consolidation preserves consensus summaries and drops rare counterevidence that can overturn a rule.",
        "固定容量下联合优化代表性和反证保留，保存能改变结论的最小反例集。",
        "Under fixed capacity, optimize representativeness and counterevidence retention, preserving a minimal conclusion-changing set.",
        "保留反证应减少过度概括和后续负迁移。",
        "Preserving counterevidence should reduce overgeneralization and later negative transfer.",
        "常规 consolidation 测覆盖率；这里用改变结论的能力定义信息价值。",
        "Standard consolidation measures coverage; this defines value by the ability to change conclusions.",
        ("Memory Consolidation", "EvoGraph-R1", "Contradiction Retrieval"), ("HotpotQA", "ALFWorld", "Video-MME"), ("knowledge", "text/tool", "multimodal"), 20,
        (5,5,5,4,5,4,5), "metric-replacement",
    ),
    I(
        "memory-half-life", "记忆半衰期", "Memory Half-Life", "memory",
        "记忆被永久保留，即使环境、工具或偏好已经变化。",
        "Memories persist even after environments, tools, or preferences change.",
        "根据跨任务帮助率、冲突率和漂移证据估计半衰期，触发复验、衰减或删除。",
        "Estimate half-life from cross-task benefit, conflict, and drift evidence, triggering revalidation, decay, or deletion.",
        "半衰期应比 recency/FIFO 更快删除过期记忆并保留长期有效规则。",
        "Half-life should remove stale memories faster than recency/FIFO while retaining durable rules.",
        "选择性遗忘已有启发式，但帮助/伤害驱动的半衰期仍不足。",
        "Selective forgetting has heuristics, but benefit/harm-driven half-life remains underexplored.",
        ("Selective Forgetting", "Continual Learning", "Memory Agents"), ("AndroidWorld", "ALFWorld", "HotpotQA"), ("web", "text/tool", "knowledge"), 18,
        (4,5,5,4,5,4,5), "limitation-inversion",
    ),

    I(
        "intervention-validated-self-correction", "干预验证自纠正", "Intervention-Validated Self-Correction", "correction",
        "Critique 可能只是事后合理化，修复其声称的变量并不会按预期改变答案。",
        "A critique may be post-hoc rationalization: fixing the claimed variable may not change the answer as predicted.",
        "接受纠正前执行最小步骤/观察/工具干预，验证方向一致的因果效应。",
        "Before accepting a correction, execute a minimal step, observation, or tool intervention and test directional causal consistency.",
        "通过干预验证的纠正应具有更高修复率和迁移性。",
        "Intervention-validated corrections should repair more reliably and transfer better.",
        "SCoRe 学习 on-policy 纠正；本方法治理哪些纠正信号值得持久化。",
        "SCoRe learns on-policy correction; this governs which correction signals deserve persistence.",
        ("SCoRe", "AgentRefine", "VISCO"), ("GSM8K", "ALFWorld", "MM-Vet"), ("reasoning", "text/tool", "multimodal"), 28,
        (5,5,5,5,4,5,4), "objective-evaluation-mismatch",
    ),
    I(
        "correction-policy-credit", "纠正策略信用分配", "Correction Policy Credit Assignment", "correction",
        "多轮纠正中无法判断哪次 critique 或修复动作真正带来提升。",
        "Multi-round correction does not reveal which critique or repair action caused improvement.",
        "对检查、重采样、工具调用和局部重写做局部反事实信用分配。",
        "Assign local counterfactual credit to checking, resampling, tool use, and local rewrite actions.",
        "动作级信用应减少无效纠正调用而保持修复率。",
        "Action-level credit should remove ineffective correction calls while preserving repair.",
        "SCoRe 学习总体纠正策略，但动作级信用与成本控制仍不足。",
        "SCoRe learns an overall correction strategy, but action-level credit and cost control remain open.",
        ("SCoRe", "Process Rewards", "Policy Credit Assignment"), ("HumanEval", "ALFWorld", "MM-Vet"), ("code", "text/tool", "multimodal"), 24,
        (4,5,5,5,4,4,5), "missing-cell",
    ),
    I(
        "heterogeneous-critic-disagreement", "异构 Critic 分歧学习", "Heterogeneous Critic Disagreement Learning", "correction",
        "Actor 与同架构 Critic 容易共享盲点，表面一致不能证明正确。",
        "Actors and same-family critics share blind spots, so agreement is not correctness.",
        "只把可由环境或工具真值裁决的跨架构 Critic 分歧用于更新。",
        "Use cross-architecture critic disagreement for learning only when environment or tool ground truth can resolve it.",
        "可裁决分歧应比全量 critique 具有更高监督精度。",
        "Resolvable disagreements should provide higher supervision precision than all critiques.",
        "Critic-V 使用独立 Critic；跨架构分歧何时成为可靠学习信号仍不明确。",
        "Critic-V uses an independent critic; when cross-family disagreement becomes reliable supervision is still unclear.",
        ("Critic-V", "ChatEval", "SCoRe"), ("GSM8K", "ALFWorld", "MM-Vet"), ("reasoning", "text/tool", "multimodal"), 32,
        (4,5,5,4,4,5,4), "pme-recombination", 2, 6,
    ),
    I(
        "self-correction-collapse-detector", "自纠正坍塌检测", "Self-Correction Collapse Detector", "correction",
        "模型可能学会频繁改答案、偏好格式或迎合 Reward，而不是真正纠错。",
        "A model may learn to change answers, prefer a format, or please a reward without genuinely correcting errors.",
        "用正确答案保持、错误答案修复和反事实敏感性三轴定义纠正坍塌。",
        "Define correction collapse using correct-answer preservation, error repair, and counterfactual sensitivity.",
        "真实纠正应同时提高修复并保持正确答案和无关稳定性。",
        "Real correction should improve repair while preserving correct answers and irrelevant invariance.",
        "SCoRe 分析训练坍塌；本方法提供跨模型、无需训练的统一审计。",
        "SCoRe analyzes training collapse; this provides a cross-model, training-free audit.",
        ("SCoRe", "Self-Refine", "Self-Correction Limits"), ("GSM8K", "HumanEval", "MM-Vet"), ("reasoning", "code", "multimodal"), 18,
        (4,5,5,4,5,5,5), "metric-replacement",
    ),

    I(
        "failure-frontier-curriculum", "失败前沿课程", "Failure-Frontier Curriculum", "curriculum",
        "失败生成课程容易重复旧失败或制造超出当前学习能力的无效难题。",
        "Failure-generated curricula duplicate old failures or create tasks beyond the useful learning frontier.",
        "只保留位于当前成功—失败边界附近且能区分相邻 checkpoint 的任务。",
        "Keep only tasks near the success-failure boundary that discriminate adjacent checkpoints.",
        "前沿任务应以更少样本获得更高圈外提升。",
        "Frontier tasks should yield more out-of-loop gain per sample.",
        "WebRL 从失败生成任务；本方法增加 checkpoint 判别性和圈外验证。",
        "WebRL generates tasks from failures; this adds checkpoint discriminativeness and out-of-loop validation.",
        ("WebRL", "Active Learning", "Curriculum Learning"), ("WebArena-Lite", "ALFWorld"), ("web", "text/tool"), 48,
        (5,5,5,4,5,4,4), "pme-recombination", 2, 8,
    ),
    I(
        "counterexample-generating-curriculum", "反例生成课程", "Counterexample-Generating Curriculum", "curriculum",
        "课程生成模仿失败样本，却不主动寻找能推翻当前策略规则的最小反例。",
        "Curriculum generation imitates failures rather than searching for minimal counterexamples to current policy rules.",
        "从隐含规则生成单约束变化的边界任务，只保留能触发一致性破坏且可自动验证的反例。",
        "Generate single-constraint boundary tasks from implicit rules and retain only automatically verifiable counterexamples.",
        "最小反例应提高规则边界泛化，而不只是近邻任务性能。",
        "Minimal counterexamples should improve boundary generalization rather than nearby-task performance only.",
        "AgentRefine 合成纠错轨迹；本方法显式优化反例价值。",
        "AgentRefine synthesizes refinement traces; this explicitly optimizes counterexample value.",
        ("AgentRefine", "Counterexample-Guided Learning", "WebRL"), ("ALFWorld", "ToolBench", "MM-Vet"), ("text/tool", "multimodal"), 26,
        (5,5,5,4,4,5,5), "cross-domain-analogy",
    ),
    I(
        "curriculum-drift-controller", "课程漂移控制器", "Curriculum Drift Controller", "curriculum",
        "在线课程改变策略分布，旧 Reward 和任务生成器随迭代失配。",
        "Online curricula shift policy distributions, making rewards and task generators stale.",
        "用固定锚点和行为分布距离监测漂移，并触发 replay、减小更新或停止。",
        "Monitor drift with frozen anchors and behavioral distance, triggering replay, smaller updates, or stopping.",
        "漂移信号应在锚点退化前预测回退。",
        "Drift signals should predict regression before anchor degradation.",
        "WebRL 控制训练漂移，但缺少跨方法统一、可审计的课程漂移指标。",
        "WebRL controls training drift but lacks a unified, auditable curriculum-drift metric.",
        ("WebRL", "Continual Learning", "Distribution Shift"), ("WebArena-Lite", "ALFWorld"), ("web", "text/tool"), 22,
        (4,5,5,4,5,4,5), "metric-replacement",
    ),

    I(
        "workflow-branch-credit", "工作流分支信用分配", "Workflow Branch Credit Assignment", "workflow",
        "工作流搜索发现更高分图后，无法知道哪个节点、边或并行结构真正带来改进。",
        "After workflow search finds a better graph, it is unclear which node, edge, or parallel structure caused the gain.",
        "对局部图编辑做 matched ablation，学习节点、边和交互项的结构信用。",
        "Use matched ablations of local graph edits to learn node, edge, and interaction credit.",
        "结构信用应减少达到同等性能所需的搜索评估，并跨任务复用。",
        "Structural credit should reduce search evaluations required for the same performance and transfer across tasks.",
        "AFlow 使用 MCTS 和经验树，但结构级因果信用仍不明确。",
        "AFlow uses MCTS and experience trees, but causal structural credit remains unclear.",
        ("AFlow", "Flow", "WorfBench"), ("HumanEval", "GSM8K", "HotpotQA"), ("code", "reasoning", "knowledge"), 28,
        (5,5,5,5,4,4,5), "missing-cell",
    ),
    I(
        "update-surface-router", "更新表面路由器", "Update-Surface Router", "workflow",
        "同一失败可通过改 Prompt、记忆、工作流或小模块修复，但系统通常固定更新一种表面。",
        "The same failure may be fixed by prompt, memory, workflow, or small-module updates, yet systems hard-code one surface.",
        "根据失败证据学习成本感知路由器，选择最小且最稳定的更新表面。",
        "Learn a cost-aware router that selects the smallest and most stable update surface from failure evidence.",
        "路由器应以明显低于穷举的成本接近 oracle 修复收益。",
        "The router should approach oracle repair at substantially lower cost than exhaustive evaluation.",
        "自进化综述按更新表面分类，但跨表面选择仍少有直接学习方法。",
        "Surveys classify update surfaces, but direct learning of cross-surface selection is rare.",
        ("AFlow", "Retroformer", "LoRA"), ("ALFWorld", "AgentBench", "MM-Vet"), ("text/tool", "multimodal"), 44,
        (5,5,5,4,5,4,4), "missing-cell", 2, 8,
    ),
    I(
        "compositional-update-compatibility", "组合更新兼容性", "Compositional Update Compatibility", "workflow",
        "两个单独有效的更新组合后可能相互干扰，逐项回归无法预测组合效果。",
        "Two individually useful updates can interfere when composed; individual regression tests cannot predict composition.",
        "通过顺序交换和局部组合实验学习更新之间的非交换性与交互图。",
        "Learn non-commutativity and an interaction graph through order swaps and local composition tests.",
        "交互图应预测未见组合回退并找到更优提交顺序。",
        "The interaction graph should predict unseen composition regressions and identify better commit orders.",
        "工作流模块化研究结构依赖，但更新操作之间的语义干扰仍未系统建模。",
        "Workflow modularity studies structural dependencies, but semantic interference among updates remains under-modeled.",
        ("Flow", "AFlow", "Software Merge Testing"), ("AgentBench", "ALFWorld"), ("workflow", "text/tool"), 24,
        (5,5,4,5,5,4,5), "cross-domain-analogy",
    ),
    I(
        "workflow-generalization-certificate", "工作流泛化证书", "Workflow Generalization Certificate", "workflow",
        "开发集最优工作流可能利用任务模板，held-out 分数也难覆盖结构捷径。",
        "Development-optimal workflows may exploit templates, and a single held-out score misses structural shortcuts.",
        "用结构扰动、任务重命名和工具替换构成最小泛化证书，未通过则不提交。",
        "Use structural perturbation, task renaming, and tool substitution as a minimal generalization certificate before commit.",
        "通过证书的工作流应更好迁移到未见工具和任务图。",
        "Certified workflows should transfer better to unseen tools and task graphs.",
        "WorfBench 提供结构评测；本方法把评测转为工作流准入机制。",
        "WorfBench evaluates structure; this converts evaluation into workflow admission.",
        ("WorfBench", "AFlow", "Metamorphic Testing"), ("WorfBench", "HumanEval", "HotpotQA"), ("workflow", "code", "knowledge"), 16,
        (4,5,5,4,5,4,5), "cross-domain-analogy",
    ),

    I(
        "evaluator-coadaptation-guard", "评价器共适应防护", "Evaluator Co-Adaptation Guard", "evaluator",
        "Actor 与评价器同时进化会共同放大捷径，内部 reward 上升但外部质量下降。",
        "Co-evolving actors and evaluators can amplify shared shortcuts while external quality declines.",
        "每轮交叉配对 Actor/Reward 版本，并用冻结锚点和异构 Judge 阻止只对当前 Actor 有利的更新。",
        "Cross-pair actor and reward versions each round and use frozen anchors plus heterogeneous judges to block actor-specific evaluator updates.",
        "跨版本门控应降低外部 Judge 和人工小样本上的 reward hacking。",
        "Cross-version gating should reduce reward hacking under external judges and small human audits.",
        "Self-Evolved Reward Learning 改进 Reward，但缺少严格跨版本共适应审计。",
        "Self-Evolved Reward Learning improves rewards but lacks strict cross-version co-adaptation audits.",
        ("Self-Evolved Reward Learning", "Constrained RLHF", "Red Queen"), ("UltraFeedback", "HH-RLHF"), ("alignment", "reward learning"), 42,
        (5,5,5,5,5,5,4), "contradiction-resolution", 2, 8,
    ),
    I(
        "reward-invariance-audit", "奖励不变性审计", "Reward Invariance Audit", "evaluator",
        "Reward 对语义无关格式、背景或表述敏感时，Agent 会优化捷径。",
        "Agents exploit shortcuts when rewards respond to semantically irrelevant format, background, or phrasing.",
        "用语义保持、语义改变正对照和捷径探针三类 matched interventions 测选择性不变性。",
        "Use matched semantics-preserving, semantics-changing positive controls, and shortcut probes to measure selective invariance.",
        "可靠 Reward 应对无关变化稳定、对语义改变敏感，并预测真实选择错误。",
        "Reliable rewards should be invariant to irrelevant changes, sensitive to semantic changes, and predictive of real selection errors.",
        "Constrained RLHF 研究过优化；本方法提供跨任务域、无需训练的干预诊断。",
        "Constrained RLHF studies overoptimization; this provides cross-domain intervention diagnostics without training.",
        ("Constrained RLHF", "Self-Evolved Reward Learning", "Reward Hacking"), ("GSM8K", "ALFWorld", "MM-Vet"), ("reasoning", "text/tool", "multimodal"), 20,
        (5,5,5,5,5,5,5), "metric-replacement",
    ),
    I(
        "self-label-confidence-flow", "自标注置信传播", "Self-Label Confidence Flow", "evaluator",
        "多轮自标注和再训练会丢失初始不确定性，低质量标签可能跨代放大。",
        "Across self-labeling generations, initial uncertainty is lost and low-quality labels can amplify.",
        "让每个派生标签携带来源、置信度和父标签依赖，并把不确定性传播到训练权重。",
        "Carry provenance, confidence, and parent-label dependencies with each derived label and propagate uncertainty into training weights.",
        "谱系置信应更好预测标签错误并降低噪声放大。",
        "Lineage confidence should better predict label errors and reduce noise amplification.",
        "Self-Evolved Reward Learning 筛选当前轮标签，但跨轮置信传播仍是空缺。",
        "Self-Evolved Reward Learning filters current-round labels, but cross-round confidence propagation remains open.",
        ("Self-Evolved Reward Learning", "Weak-to-Strong", "Data Provenance"), ("UltraFeedback", "HH-RLHF"), ("reward learning", "alignment"), 24,
        (5,5,5,4,5,5,5), "cross-domain-analogy",
    ),

    I(
        "world-model-error-gated-learning", "世界模型误差门控学习", "World-Model Error-Gated Learning", "world",
        "更准的世界模型不一定改变决策，盲目写入所有转移会增加训练噪声。",
        "A more accurate world model may not improve decisions, and learning every transition adds noise.",
        "只学习那些预测误差会改变动作选择、风险或恢复决策的转移。",
        "Learn only transition errors that would change action selection, risk, or recovery decisions.",
        "决策价值门控应以更少更新获得同等或更高任务收益。",
        "Decision-value gating should match or improve utility with fewer updates.",
        "WMA 提升预测并改善策略选择；本方法治理哪些预测误差值得学习。",
        "WMA improves predictions and policy selection; this governs which prediction errors deserve learning.",
        ("Web Agents with World Models", "Model-Based RL", "Value of Information"), ("WebArena-Lite", "AndroidWorld", "LIBERO"), ("web", "GUI", "embodied"), 38,
        (5,5,5,5,5,4,4), "objective-evaluation-mismatch", 2, 8,
    ),
    I(
        "irreversible-action-counterfactuals", "不可逆动作反事实", "Irreversible-Action Counterfactuals", "world",
        "Agent 只从已执行轨迹学习，难以获得未执行但会导致不可逆损失的负经验。",
        "Agents learn only from executed trajectories and miss counterfactual negative experience for irreversible actions.",
        "用世界模型生成受约束的未执行后果，仅在环境规则或模拟器可验证时写入风险记忆。",
        "Generate constrained unexecuted consequences and admit risk memories only when verified by environment rules or simulators.",
        "验证后的反事实记忆应减少不可逆错误且不导致过度保守。",
        "Verified counterfactual memory should reduce irreversible errors without excessive conservatism.",
        "WMA 预测动作后果；本方法专注不可逆风险的可验证反事实经验。",
        "WMA predicts action outcomes; this focuses on verifiable counterfactual experience for irreversible risk.",
        ("Web Agents with World Models", "Safe Exploration", "Counterfactual Planning"), ("WebArena-Lite", "AndroidWorld", "LIBERO"), ("web", "GUI", "embodied"), 32,
        (5,5,5,5,5,5,4), "assumption-removal", 2, 7,
    ),
    I(
        "recovery-conditioned-experience", "恢复条件经验学习", "Recovery-Conditioned Experience Learning", "world",
        "任务成功或重新加入轨迹不等于完整恢复，残余状态可能被写成成功经验。",
        "Task success or trajectory rejoin does not imply full recovery, and residual states can be stored as success lessons.",
        "经验准入同时要求终点成功、持续重合和状态残差通过，并按恢复级别控制写入强度。",
        "Admission requires endpoint success, sustained rejoin, and residual-state checks, with update strength conditioned on recovery level.",
        "完整恢复轨迹应具有更高未来技能复用价值，残差轨迹更易造成负迁移。",
        "Fully recovered trajectories should have higher future reuse value; residual trajectories should cause more negative transfer.",
        "具身 continual learning 常按任务成功更新，过程残差与持久学习的关系仍不足。",
        "Embodied continual learning often updates from task success, leaving process residuals underexplored.",
        ("Online Continual Learning for Agents", "TPER", "OpenVLA"), ("LIBERO", "CALVIN"), ("embodied", "VLA"), 26,
        (5,5,4,5,5,4,5), "pme-recombination",
    ),
)

EARLY_REJECTED: tuple[dict[str, str], ...] = (
    {"title":"更大模型做更多反思", "reason":"只增加推理计算，不能证明持久学习。"},
    {"title":"全参数训练 70B 自进化 Agent", "reason":"超出低资源约束且机制难归因。"},
    {"title":"只在自生成任务上提升", "reason":"缺少圈外泛化。"},
    {"title":"仅商业 API 闭环", "reason":"不可复现且依赖供应商快照。"},
    {"title":"固定多轮 Self-Refine", "reason":"属于更多采样，不是进化机制。"},
    {"title":"同模型 Actor 与 Judge 自我确认", "reason":"反馈完整性无法独立验证。"},
    {"title":"只报告最佳 checkpoint", "reason":"掩盖多轮回退与坍塌。"},
    {"title":"从头训练世界模型和策略", "reason":"资源高且无法分离贡献。"},
    {"title":"单一视觉 benchmark 技巧", "reason":"保留为 CVPR 后续，不作为 ICLR 主候选。"},
    {"title":"只做平均准确率的记忆消融", "reason":"无法识别有害条目和负迁移。"},
    {"title":"无隔离划分的在线适应", "reason":"无法排除测试泄漏。"},
    {"title":"泛化 Agent 自进化综述", "reason":"不是方法或可证伪 benchmark 贡献。"},
)

STRUCTURED_BLOCKS: dict[str, dict[str, str]] = {
    "failure-localization-before-reflection": {
        "finding":"Module-level intervention labels may require expensive environment-specific instrumentation.",
        "required_action":"Demonstrate automatic intervention labels on two domains before advancing.",
    },
    "update-surface-router": {
        "finding":"Oracle labels require executing all update surfaces, making supervision close to exhaustive search.",
        "required_action":"Provide partial-feedback or active-query labels substantially cheaper than enumeration.",
    },
    "heterogeneous-critic-disagreement": {
        "finding":"Cross-family disagreement may reflect formatting and style rather than distinct error mechanisms.",
        "required_action":"Show environment-grounded disagreement precision before using it as supervision.",
    },
}

EXTERNAL_REVIEWS: dict[str, list[dict[str, Any]]] = {
    "regression-gated-self-evolution": [{
        "reviewer":"agent-project-web-gpt-iclr-area-chair",
        "verdict":"pass",
        "finding":"The strongest low-resource ICLR thesis is constrained policy improvement with disjoint regression tests, matched costs, and auditable commit/rollback.",
        "required_action":"Report persistent capability gain and regression after every evolution round under equal interaction, token, model-call, and training budgets.",
        "source_artifact":"/data/wyt/agent-self-evolution-observatory/runs/reviews/iclr-first-research-design.md",
    }],
}


def _review(spec: IdeaSpec) -> tuple[bool, list[dict[str, Any]], list[str]]:
    blocks: list[str] = []
    if spec.budget.max_gpus > 2 or spec.budget.gpu_hours > 48:
        blocks.append("Resource budget exceeds two GPUs or 48 GPU-hours.")
    if len(spec.domains) < 2:
        blocks.append("Fewer than two evaluation domains.")
    if min(spec.scores) < 4:
        blocks.append("At least one ICLR review dimension is below 4/5.")
    if spec.id in STRUCTURED_BLOCKS:
        blocks.append(STRUCTURED_BLOCKS[spec.id]["finding"])
    labels = {
        "novelty":bi("机制新颖性", "Mechanism novelty"),
        "learning_problem":bi("学习问题重要性", "Learning-problem importance"),
        "generality":bi("跨领域一般性", "Cross-domain generality"),
        "attribution":bi("信用分配与可识别性", "Credit assignment and identifiability"),
        "stability":bi("更新稳定性", "Update stability"),
        "feedback":bi("反馈完整性", "Feedback integrity"),
        "feasibility":bi("效率与可复现性", "Efficiency and reproducibility"),
    }
    findings = {
        "novelty":spec.collision,
        "learning_problem":TRACKS[spec.track]["importance"],
        "generality":bi(f"覆盖 {len(spec.domains)} 类任务域。", f"Covers {len(spec.domains)} task domains."),
        "attribution":spec.hypothesis,
        "stability":bi("必须逐轮报告收益、最坏回退和被拒绝更新。", "Must report gain, worst regression, and rejected updates after every round."),
        "feedback":bi("环境真值、工具执行或异构 Critic 必须提供独立证据。", "Environment truth, tool execution, or a heterogeneous critic must provide independent evidence."),
        "feasibility":bi(f"上限 {spec.budget.max_gpus} GPU、{spec.budget.gpu_hours} GPU 小时。", f"Cap: {spec.budget.max_gpus} GPUs and {spec.budget.gpu_hours} GPU-hours."),
    }
    reviews = []
    for key, score in zip(REVIEW_KEYS, spec.scores):
        reviews.append({"reviewer":key, "label":labels[key], "score":score, "verdict":"pass" if score >= 4 else "block", "finding":findings[key]})
    return not blocks, reviews, blocks


def _derived_fields(spec: IdeaSpec) -> dict[str, dict[str, str]]:
    track = TRACKS[spec.track]
    method = bi(
        f"从失败或更新候选中抽取状态，应用“{spec.mechanism['zh']}”，在隔离 calibration 与 regression 集上比较后 commit、局部修复或 rollback。",
        f"Extract states from failures or candidate updates, apply: {spec.mechanism['en']}, compare on isolated calibration and regression sets, then commit, locally repair, or roll back.",
    )
    advantage = bi(
        f"相较于“{track['baseline']['zh']}”，该机制直接检验更新是否产生持久、可归因且稳定的圈外收益。",
        f"Compared with {track['baseline']['en']}, the mechanism directly tests whether updates yield persistent, attributable, stable out-of-loop gains.",
    )
    pilot = bi(
        f"在 {'、'.join(spec.datasets)} 上，以 {spec.budget.max_gpus} GPU、{spec.budget.gpu_hours} GPU 小时完成两个开放模型和至少两个任务域的 P0/P1/P2 验证。",
        f"Run P0/P1/P2 on {', '.join(spec.datasets)} with two open models and at least two domains within {spec.budget.max_gpus} GPUs and {spec.budget.gpu_hours} GPU-hours.",
    )
    metric = bi(
        "Future-task gain、Worst regression、Update-admission precision、Out-of-loop generalization 与单位交互/调用/GPU 收益。",
        "Future-task gain, worst regression, update-admission precision, out-of-loop generalization, and gain per interaction/call/GPU-hour.",
    )
    stop = bi(
        f"若“{spec.hypothesis['zh']}”在第二模型或第二任务域不成立，或收益仅来自更多调用，则停止。",
        f"Stop if the hypothesis—{spec.hypothesis['en']}—fails on the second model/domain or gains come only from extra calls.",
    )
    return {"method_logic":method, "comparative_advantage":advantage, "pilot":pilot, "metric":metric, "stop":stop}


def _protocol(spec: IdeaSpec, fields: dict[str, dict[str, str]]) -> dict[str, Any]:
    models = TRACKS[spec.track]["models"]
    return {
        "execution_mode":bi("ICLR 主结果使用开放权重、冻结基础模型和持久小组件更新；视觉专门版本留给 CVPR。", "ICLR primary results use open weights, frozen backbones, and persistent small-component updates; visual specialization remains for CVPR."),
        "actor":models[0],
        "cross_model":models[1],
        "optional_domain_model":models[2],
        "critic_or_verifier":"Frozen heterogeneous open-weight critic plus environment/tool ground truth whenever available.",
        "commercial_api_role":bi("仅作为固定版本可选上界或最多 200 次审计 Judge；核心结论不得依赖。", "Optional fixed-version ceiling or audited judge for at most 200 calls; never required for the core claim."),
        "parameter_updates":bi("只更新 Prompt、记忆、工作流、路由器、Reward 校准器或 <50M 参数模块。", "Update prompts, memory, workflows, routers, reward calibrators, or modules below 50M parameters."),
        "data_protocol":{
            "discovery":bi("每个主域 100–200 个训练样本，只确认现象。", "Use 100-200 training examples per main domain for phenomenon confirmation only."),
            "calibration":bi("另取不重叠的 100–200 个样本冻结阈值和至多三组超参数。", "Use a disjoint 100-200 examples to freeze thresholds and at most three hyperparameter settings."),
            "test":bi("官方测试集或至少 500 个隔离样本；测试期间禁止修改更新规则。", "Use official tests or at least 500 isolated examples; update rules stay frozen during testing."),
        },
        "phases":[
            {"id":"P0", "title":bi("真实进化检查", "Reality-of-evolution check"), "setup":bi("移除持久状态并匹配推理预算，排除更多采样、检索和重排。", "Remove persistent state and match inference budgets to exclude extra sampling, retrieval, and reranking."), "gate":bi("若移除更新后收益仍在，则不属于持续学习。", "If gains remain after removing the update, the effect is not persistent learning.")},
            {"id":"P1", "title":bi("机制 Pilot", "Mechanism pilot"), "setup":fields["pilot"], "gate":spec.hypothesis},
            {"id":"P2", "title":bi("圈外泛化与稳定性", "Out-of-loop generalization and stability"), "setup":bi("冻结 P1 决定，迁移到第二模型、第二任务域并运行至少三轮。", "Freeze P1 choices, transfer to a second model/domain, and run at least three rounds."), "gate":fields["stop"]},
        ],
        "controls":[
            bi("无持久更新，匹配推理预算。", "No persistent update with matched inference budget."),
            bi("全部接受或仅按当前任务收益接受。", "Accept all updates or filter only by current-task gain."),
            TRACKS[spec.track]["baseline"],
            bi("等预算随机更新／拒绝。", "Equal-budget random update/rejection."),
            bi("隐藏真值 Oracle 上界。", "Hidden-ground-truth oracle ceiling."),
        ],
        "repetitions":bi("三个随机种子；报告均值、标准差和样本级 bootstrap 95% CI。", "Three seeds with mean, standard deviation, and sample-level bootstrap 95% CIs."),
        "call_budget":bi("记录环境交互、模型调用、token、工具调用、候选更新和被拒绝更新。", "Report environment interactions, model calls, tokens, tool calls, candidate updates, and rejected updates."),
        "compute_budget":bi(f"上限 {spec.budget.max_gpus} GPU、{spec.budget.gpu_hours} GPU 小时、{spec.budget.wall_days} 天。", f"Cap: {spec.budget.max_gpus} GPUs, {spec.budget.gpu_hours} GPU-hours, {spec.budget.wall_days} days."),
        "main_table":fields["metric"],
        "ablations":[
            bi("移除归因／回归门控。", "Remove attribution/regression gating."),
            bi("移除圈外测试。", "Remove out-of-loop tests."),
            bi("同架构 Critic 替代异构 Critic。", "Replace heterogeneous critic with actor family."),
            bi("不匹配调用与算力预算。", "Remove call and compute matching."),
        ],
        "success_gate":bi("两个开放模型、至少两个任务域均优于最强等预算 baseline，且最坏回退不增加。", "Both open models and at least two domains beat the strongest equal-budget baseline without increasing worst-case regression."),
        "stop_gate":fields["stop"],
        "artifacts":["config", "seed", "model snapshots", "accepted/rejected update lineage", "per-round metrics", "call/GPU accounting"],
    }


def _priority(spec: IdeaSpec) -> float:
    weights = (1.15, 1.30, 1.20, 1.20, 1.15, 1.05, 1.00)
    external_pass = any(review.get("verdict") == "pass" for review in EXTERNAL_REVIEWS.get(spec.id, []))
    strategic_boost = {
        "regression-gated-self-evolution": 3.0,
        "causally-verified-experience-admission": 1.5,
        "retrieval-interference-auditor": 0.8,
        "local-counterexample-memory-repair": 0.5,
    }.get(spec.id, 0.0)
    return round(
        sum(w*s for w,s in zip(weights, spec.scores))
        + max(0.0, (48-spec.budget.gpu_hours)/48)
        + (1.0 if external_pass else 0.0)
        + strategic_boost,
        3,
    )


def build_iclr_idea_bank() -> dict[str, Any]:
    passed: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for spec in IDEAS:
        ok, reviews, blocks = _review(spec)
        fields = _derived_fields(spec)
        record = {
            "id":spec.id,
            "title":spec.title,
            "track_id":spec.track,
            "track":TRACKS[spec.track]["label"],
            "purpose":spec.problem,
            "core_idea":spec.mechanism,
            "rationale":TRACKS[spec.track]["rationale"],
            "method_logic":fields["method_logic"],
            "importance":TRACKS[spec.track]["importance"],
            "comparative_advantage":fields["comparative_advantage"],
            "collision_boundary":spec.collision,
            "hypothesis":spec.hypothesis,
            "nearest_work":list(spec.nearest),
            "datasets":list(spec.datasets),
            "domains":list(spec.domains),
            "models":list(TRACKS[spec.track]["models"]),
            "strongest_baseline":TRACKS[spec.track]["baseline"],
            "pilot":fields["pilot"],
            "decisive_metric":fields["metric"],
            "stop_condition":fields["stop"],
            "budget":asdict(spec.budget),
            "operator":spec.operator,
            "scores":dict(zip(REVIEW_KEYS, spec.scores)),
            "reviews":reviews,
            "external_reviews":EXTERNAL_REVIEWS.get(spec.id, []),
            "experiment_protocol":_protocol(spec, fields),
            "priority":_priority(spec),
            "status":"pass" if ok else "block",
            "blocking_reasons":blocks,
        }
        if spec.id in STRUCTURED_BLOCKS:
            record["structured_block"] = STRUCTURED_BLOCKS[spec.id]
        (passed if ok else blocked).append(record)
    passed.sort(key=lambda item:(-item["priority"], item["budget"]["gpu_hours"], item["id"]))
    for rank,item in enumerate(passed, start=1):
        item["rank"] = rank
    return {
        "schema_version":"1.0",
        "generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "target_venue":"ICLR",
        "secondary_venue":"CVPR",
        "review_mode":"iclr-seven-dimension-programmatic-plus-project-web-gpt",
        "policy":{
            "max_gpus":2,
            "max_gpu_hours":48,
            "minimum_reviewer_score":4,
            "minimum_domains":2,
            "review_dimensions":list(REVIEW_KEYS),
            "primary_open_weight_required":True,
            "commercial_api_optional_only":True,
        },
        "summary":{
            "raw_candidates":len(IDEAS)+len(EARLY_REJECTED),
            "structured_candidates":len(IDEAS),
            "passed":len(passed),
            "blocked_after_structured_review":len(blocked),
            "early_rejected":len(EARLY_REJECTED),
            "tracks":len(TRACKS),
            "project_web_gpt_reviewed":sum(bool(EXTERNAL_REVIEWS.get(spec.id)) for spec in IDEAS),
        },
        "tracks":{key:value["label"] for key,value in TRACKS.items()},
        "passed_ideas":passed,
        "blocked_ideas":blocked,
        "early_rejected":list(EARLY_REJECTED),
        "iclr_review_dimensions":[
            {"key":"reality", "label":bi("真实持续进化", "Reality of evolution"), "question":bi("是否获得持久能力，而不是更多推理、检索或重排？", "Is capability persistent rather than extra inference, retrieval, or reranking?")},
            {"key":"mechanism", "label":bi("更新机制明确", "Mechanistic specificity"), "question":bi("究竟更新了参数、Prompt、记忆、工作流、Reward 还是世界模型？", "What exactly changes: weights, prompts, memory, workflows, rewards, or world models?")},
            {"key":"credit", "label":bi("信用分配与可识别性", "Credit assignment and identifiability"), "question":bi("更新能否归因到具体失败、状态或反馈？", "Can the update be attributed to a specific failure, state, or feedback signal?")},
            {"key":"stability", "label":bi("更新稳定性", "Update stability"), "question":bi("多轮进化是否避免回退、坍塌与遗忘？", "Does multi-round evolution avoid regression, collapse, and forgetting?")},
            {"key":"generalization", "label":bi("圈外泛化", "Out-of-loop generalization"), "question":bi("收益能否迁移到未见任务、环境、工具和模型族？", "Do gains transfer to unseen tasks, environments, tools, and model families?")},
            {"key":"feedback", "label":bi("反馈完整性", "Feedback integrity"), "question":bi("Reward、Critic 与 Verifier 是否有独立真值和对抗测试？", "Are rewards, critics, and verifiers independently calibrated and stress-tested?")},
            {"key":"efficiency", "label":bi("效率与复现", "Efficiency and reproducibility"), "question":bi("交互、token、调用、训练与墙钟预算是否严格匹配？", "Are interaction, token, call, training, and wall-clock budgets matched?")},
        ],
    }


def validate_bank(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    for idea in payload.get("passed_ideas", []):
        if idea["id"] in ids:
            errors.append(f"duplicate id: {idea['id']}")
        ids.add(idea["id"])
        if idea["budget"]["max_gpus"] > 2 or idea["budget"]["gpu_hours"] > 48:
            errors.append(f"resource gate failed: {idea['id']}")
        if len(idea.get("domains", [])) < 2:
            errors.append(f"generality gate failed: {idea['id']}")
        if len(idea.get("reviews", [])) != 7 or any(review["verdict"] != "pass" for review in idea["reviews"]):
            errors.append(f"review gate failed: {idea['id']}")
        if not idea.get("experiment_protocol"):
            errors.append(f"missing protocol: {idea['id']}")
        for field in ("purpose","core_idea","rationale","method_logic","importance","comparative_advantage","collision_boundary","hypothesis","pilot","decisive_metric","stop_condition"):
            value = idea.get(field)
            if not isinstance(value, dict) or not value.get("zh") or not value.get("en"):
                errors.append(f"missing bilingual {field}: {idea['id']}")
    if len(payload.get("passed_ideas", [])) < 24:
        errors.append("fewer than 24 passed ICLR ideas")
    if payload.get("target_venue") != "ICLR":
        errors.append("target venue is not ICLR")
    return errors


def write_iclr_idea_bank(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    payload = build_iclr_idea_bank()
    errors = validate_bank(payload)
    if errors:
        raise ValueError("Invalid ICLR idea bank:\n- " + "\n- ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.ICLR_LOW_RESOURCE_IDEAS = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return payload
