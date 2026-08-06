from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .machine_school_english import MACHINE_SCHOOL_ENGLISH

DEFAULT_JSON = PROJECT_ROOT / "generated" / "machine-school-inspired-ideas.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "machine-school-inspired-ideas.js"
DEFAULT_EXTERNAL_JSON = PROJECT_ROOT / "generated" / "machine-school-external-reviews.json"


def bi(zh: str, en: str) -> dict[str, str]:
    return {"zh": zh, "en": en}


INSPIRATIONS = (
    ("uneven", "机器偏科", "Uneven capability", "同一语义任务跨分类、生成和执行的能力差异。", "Capability divergence across classification, generation, and execution for the same semantics."),
    ("exam", "机器月考", "Periodic exam", "多轮更新后何时、用哪些 probe 重测回归。", "When and what to retest after multiple persistent updates."),
    ("blame", "机器家长会", "Version blame", "行为变化应归因到哪个更新表面。", "Which update surface caused a behavioral change."),
    ("retry", "机器复读", "Retry dependence", "重试收益是额外搜索还是可持久内化。", "Whether retry gains are extra search or persistent learning."),
    ("swap", "机器转学", "Model transfer", "更换 backbone 后哪些资产失效。", "Which persistent assets fail after a backbone swap."),
    ("permission", "机器留校查看", "Privilege probation", "依据版本行为证据收缩或恢复授权。", "Shrink or restore authority from version-specific behavioral evidence."),
)


def c(id: str, zh: str, en: str, source: str, decision: str, problem: str, mechanism: str, collision: str, nearest: tuple[str, ...], hypothesis: str, baseline: str, pilot: str, stop: str, domains: tuple[str, ...], hours: int) -> dict[str, Any]:
    return {
        "id": id,
        "title": bi(zh, en),
        "inspiration_id": source,
        "internal_decision": decision,
        "purpose": bi(problem, problem),
        "core_idea": bi(mechanism, mechanism),
        "collision_boundary": bi(collision, collision),
        "nearest_work": list(nearest),
        "hypothesis": bi(hypothesis, hypothesis),
        "strongest_baseline": bi(baseline, baseline),
        "pilot": bi(pilot, pilot),
        "stop_condition": bi(stop, stop),
        "domains": list(domains),
        "budget": {"max_gpus": 1 if hours <= 24 else 2, "gpu_hours": hours, "wall_days": 5 if hours <= 24 else 7},
        "external_reviews": [],
    }


CANDIDATES = [
    c("cross-form-capability-transfer-gap", "跨任务形式能力迁移缺口", "Cross-Form Capability Transfer Gap", "uneven", "pass",
      "同一语义任务在选择题、自由生成和工具执行中表现差异很大，平均准确率掩盖缺口。",
      "构造语义保持的多形式任务组，估计形式迁移矩阵，并据缺口选择不更新、Prompt、记忆或小适配器。",
      "细粒度能力 Benchmark 已揭示 profile 差异，但通常不用于选择持久更新表面。",
      ("Uncovering Competency Gaps", "From Atomic to Agentic", "Reflection-Bench"),
      "形式迁移缺口应比整体置信度更好预测最优更新表面。",
      "固定 Prompt、独立 Prompt、置信度路由、统一记忆、Oracle 路由。",
      "将 GSM8K、AgentBench 和工具任务转成分类、生成、执行三种形式；两个开放模型、三 seed、匹配调用。",
      "若缺口签名不能跨模型预测最优表面，或收益只来自更多调用，则停止。", ("reasoning", "tool", "generation"), 20),
    c("cross-form-update-allocator", "跨形式更新分配器", "Cross-Form Update Allocator", "uneven", "revise",
      "不同形式错误来源不同，系统却固定使用一种更新。", "按形式特征在 Prompt、记忆、工具模板和小模块间分配更新。",
      "与 Update-Surface Router 高度相似，除非能获得廉价可识别标签。", ("Update-Surface Router", "Agent0-VL"),
      "形式特征可降低路由 regret。", "规则、随机、固定表面、Oracle。", "三表面合成故障 Pilot。",
      "若标签仍需穷举全部表面，合并到跨形式缺口 Idea。", ("reasoning", "tool"), 18),
    c("living-capability-report-card", "动态能力报告卡", "Living Capability Report Card", "uneven", "reject",
      "总分掩盖能力短板。", "持续维护多维能力图谱。",
      "JudgeAgent、Reflection-Bench 和 competency-gap 工作直接覆盖。", ("JudgeAgent", "Reflection-Bench", "Uncovering Competency Gaps"),
      "能力图谱比总分更有诊断价值。", "标准 Benchmark 报告。", "多模型分析。",
      "作为网页分析模块保留，不作为独立论文。", ("evaluation",), 8),
    c("specialist-spillover-guard", "专项修复外溢防护", "Specialist Spillover Guard", "uneven", "revise",
      "修复弱能力可能损害强能力轴。", "对非目标能力轴设置非回退约束。",
      "与 Regression-Gated、信赖域和选择性遗忘接近。", ("Regression-Gated Self-Evolution", "Agent Update Trust Region", "Exclusive Unlearning"),
      "轴级约束可降低专项修复外溢。", "整体非回退、固定正则、无约束更新。", "两个能力轴上的 Prompt/LoRA Pilot。",
      "若整体门控同样有效，则并入 Regression-Gated。", ("reasoning", "tool"), 28),
    c("change-triggered-regression-exams", "变更触发的回归考试", "Change-Triggered Regression Exams", "exam", "pass",
      "固定回归集昂贵且不针对本次 Prompt、记忆、技能或工作流变更。",
      "从更新 diff、依赖图和历史 flip 选择最相关 probe，并保留随机审计子集。",
      "动态评测通常按表现或难度选题，而不是根据持久更新 diff 预测回归。", ("AutoJudger", "JudgeAgent", "Regression-Gated Self-Evolution"),
      "20% 测试预算应捕获至少 90% 的全量回归。", "固定小集、随机、IRT、自适应全量。",
      "在 ALFWorld/WebArena-Lite 注入 Prompt、记忆和工作流回归；两个模型、三 seed。",
      "若在未见更新类型或第二模型上召回失效，降级为测试工具。", ("tool", "web"), 22),
    c("delayed-regression-exams", "延迟回归考试", "Delayed Regression Exams", "exam", "pass",
      "更新提交时安全，但与后续更新叠加后才出现伤害。",
      "为已提交更新保留延迟 probe，后续轮次按风险重测并估计 time-to-regression。",
      "组合兼容研究顺序效应，提交门控多只测当前轮；延迟出现时间仍是独立变量。", ("Compositional Update Compatibility", "Regression-Gated Self-Evolution", "ContinualSkillBench"),
      "延迟 probe 应降低最坏轮次损失。", "提交时测试、每轮全量、固定周期。",
      "构造 4–6 轮 Prompt/记忆/技能更新序列和延迟触发故障。",
      "若成本—召回 Pareto 不优于固定周期重测，则停止。", ("tool", "continual"), 24),
    c("regression-probe-half-life", "回归 Probe 半衰期", "Regression-Probe Half-Life", "exam", "pass",
      "旧 probe 随 Agent 版本变化可能不再预测真实回退。",
      "估计 probe 对未来回退预测价值的衰减曲线，按半衰期刷新、合并或退役。",
      "OKBench 处理知识新鲜度，AutoJudger 处理效率，但未直接建模 probe 预测价值衰减。", ("OKBench", "AutoJudger", "ContinualSkillBench"),
      "半衰期调度应在同预算下提高未来回退召回。", "全部保留、最近失败、IRT、随机退役。",
      "先在现有 P0/P1/P2 registry 上做无训练的多轮预测实验。",
      "若不能预测圈外版本的 probe 价值，降级为描述性分析。", ("evaluation", "continual"), 12),
    c("adaptive-exam-scheduler", "自适应考试调度器", "Adaptive Exam Scheduler", "exam", "reject",
      "全量 Benchmark 成本高。", "按实时表现和 IRT 选题。", "AutoJudger 与 JudgeAgent 已直接覆盖。",
      ("AutoJudger", "JudgeAgent"), "自适应选择可降成本。", "随机子集、全量测试。", "多 Benchmark 排名恢复。",
      "淘汰，并作为变更触发考试的 baseline。", ("evaluation",), 8),
]

CANDIDATES += [
    c("multi-surface-change-attribution", "多更新表面变化归因", "Multi-Surface Change Attribution", "blame", "reject",
      "行为变化可能同时来自权重、数据、Prompt、记忆和工作流。", "统一归因所有变化来源。",
      "ExPLAIND、TRACE 和现有 lineage 已覆盖统一训练与风险归因。", ("ExPLAIND", "TRACE", "EvoProvenance"),
      "联合归因优于单来源归因。", "逐来源消融。", "多组件合成变化。", "范围过大且直接碰撞。", ("analysis",), 24),
    c("version-differential-failure-localization", "版本差分故障定位", "Version-Differential Failure Localization", "blame", "pass",
      "新版本失败时，完整回滚不能定位是 Prompt、记忆、技能、工作流还是小模块导致。",
      "在相邻版本间执行最小可逆组件替换，以行为差分定位最小故障集合，再只修复对应表面。",
      "软件 issue localization 定位代码，TRACE/ExPLAIND 归因训练因素；Agent 多表面的可执行最小替换仍不同。",
      ("OrcaLoca", "TRACE", "ExPLAIND", "Compositional Update Compatibility"),
      "最小替换应比整版本回滚和日志归因更准确，并降低修复副作用。",
      "完整回滚、日志归因、随机替换、穷举 Oracle。",
      "在 ALFWorld/WebArena-Lite 注入单点和双点更新故障；最多四个表面、两个模型、三 seed。",
      "若不能在双点故障或第二模型上超过日志归因，则并入 Compositional Update Compatibility。", ("tool", "web"), 24),
    c("update-responsibility-graph", "更新责任图", "Update Responsibility Graph", "blame", "revise",
      "多个已通过更新组合后出现回退时，需要追踪责任传播。", "建立更新依赖与交互图，分配组合故障责任。",
      "与 Compositional Update Compatibility 和 lineage-aware rollback 高度重叠。",
      ("Compositional Update Compatibility", "Lineage-Aware Rollback"),
      "责任图可减少回滚范围。", "逐更新回滚、Shapley、依赖日志。", "三更新合成故障。",
      "作为 Compositional Update Compatibility 的后续机制，不单独立项。", ("continual",), 26),
    c("data-policy-drift-decomposition", "数据漂移与策略漂移分解", "Data-versus-Policy Drift Decomposition", "blame", "reject",
      "性能变化可能来自协变量偏移或更新不稳定。", "分解风险变化来源。", "TRACE 直接提出相同目标。",
      ("TRACE",), "风险分解可改善门控。", "整体风险差。", "分布移位实验。", "直接淘汰。", ("analysis",), 10),
    c("retry-to-one-shot-distillation", "重试到单次策略蒸馏", "Retry-to-One-Shot Distillation", "retry", "reject",
      "多轮重试成功但单次执行仍失败。", "把成功重试轨迹蒸馏为单次策略。",
      "SCoRe、RePrompt、Guided Sampling 和多 Agent reflection 已覆盖重试内化。",
      ("SCoRe", "RePrompt", "Guided Sampling", "DPSDP"),
      "蒸馏可减少重试。", "固定两轮纠正、离线 SFT、再次采样。", "推理与工具任务。", "核心机制已拥挤。", ("reasoning",), 32),
    c("retry-signal-distillation-gate", "重试信号蒸馏门控", "Retry-Signal Distillation Gate", "retry", "revise",
      "重试轨迹混合有效修复信号与纯采样幸运。",
      "用 matched retry、步骤置换和无重试对照估计哪些片段值得写入持久记忆或策略。",
      "与 correction credit、intervention-validated self-correction 和因果经验准入重叠。",
      ("Correction Policy Credit Assignment", "Intervention-Validated Self-Correction", "SCoRe"),
      "门控可保留修复收益并降低错误写入。", "全部写入、成功写入、置信度、随机片段。",
      "两模型、三类重试失败、匹配调用。", "若不能形成机制差异，则作为组件不独立推进。", ("reasoning", "tool"), 22),
    c("retry-dependence-index", "重试依赖指数", "Retry Dependence Index", "retry", "revise",
      "最终成功率掩盖系统对多轮 Prompt 和额外采样的依赖。",
      "测量移除重试后的性能下降、重试长度和移除持久状态后的剩余收益。",
      "这是 Reality-of-Evolution 的公共指标，不足以单独构成方法。", ("ContinualSkillBench", "SCoRe", "Reflection-Bench"),
      "指数可识别伪自进化。", "成功率与平均调用数。", "复用现有 P0 结果。", "作为后端指标，不单独投稿。", ("evaluation",), 6),
    c("recurrent-failure-contract-compilation", "重复失败契约编译", "Recurrent-Failure Contract Compilation", "retry", "pass",
      "同类失败反复出现时，系统继续追加自然语言反思，导致规则重叠和调用膨胀。",
      "把多次失败归纳为带适用条件、禁止动作、验证器和过期条件的可执行契约；圈外重放通过后替换原反思。",
      "Prompt 优化与技能编译已存在，但从重复失败到带过期和验证条件的最小契约仍可测试。",
      ("RePrompt", "SkillCompiler", "SkillOpt", "Deep Reflection Hinting"),
      "契约编译应在同 token 预算下减少重复失败和规则冲突，并跨模型迁移。",
      "追加全部反思、摘要反思、技能编译、固定规则模板。",
      "在 ALFWorld 和代码/工具任务构造三类重复失败；冻结 backbone，只更新契约库。",
      "若收益来自更长上下文，或契约不能迁移到第二模型，则停止。", ("tool", "code"), 20),
]

CANDIDATES += [
    c("model-swap-compatibility-certificate", "模型替换兼容性证书", "Model-Swap Compatibility Certificate", "swap", "pass",
      "更换基础模型后，原有 Prompt、记忆、技能和工作流可能静默失效，通常完整迁移后才发现。",
      "迁移前运行小型行为 probe，预测每个持久资产在目标模型上的可移植性、风险和适配量。",
      "SkCC/MASA 做跨框架编译或模型感知技能适配；本方向预测迁移风险并证书化整个 Agent 状态。",
      ("SkCC", "MASA", "ContinualSkillBench", "WorMI"),
      "小型 probe 应预测资产级负迁移并减少实际重写数量。",
      "全量迁移、语义相似、源成功率、MASA/SkCC、随机 probe。",
      "三个开放模型家族，Prompt/记忆/技能/工作流各 20–30 个资产，两个任务域。",
      "若不能跨目标模型预测负迁移，或成本接近全量迁移，则停止。", ("tool", "web", "multimodal"), 26),
    c("cross-model-skill-portability-gate", "跨模型技能可移植门控", "Cross-Model Skill Portability Gate", "swap", "reject",
      "同一技能对不同 backbone 的作用不同。", "按目标模型改写或筛选技能。",
      "MASA 与 SkCC 已直接覆盖模型感知技能适配和跨框架编译。", ("MASA", "SkCC", "SkillCompiler"),
      "模型感知技能优于统一技能。", "统一技能、目标模型重写。", "多模型 SkillBench。",
      "淘汰，并作为兼容证书的最强 baseline。", ("tool",), 24),
    c("provider-migration-adapter", "模型供应商迁移适配器", "Provider Migration Adapter", "swap", "revise",
      "不同 API 的格式、工具协议和拒绝行为导致迁移失败。",
      "学习轻量中间表示，自动重写系统 Prompt、工具 schema 和技能。",
      "SkCC 已提出跨框架 IR；MASA 处理模型感知重写。", ("SkCC", "MASA"),
      "适配器可保持迁移前行为。", "手工重写、SkCC、MASA。", "两家 API 加两个开放模型。",
      "除非提出新的行为保持约束，否则并入兼容证书。", ("tool",), 18),
    c("swap-aware-regression-localization", "模型替换感知回归定位", "Swap-Aware Regression Localization", "swap", "pass",
      "换模型后失败可能来自目标 backbone 能力不足，也可能来自旧 Prompt、记忆、技能或工具假设不兼容。",
      "执行 backbone 与持久资产的因子替换，区分基础能力缺口和资产不兼容，再选择最小修复。",
      "MASA/SkCC 直接适配技能，但没有把迁移失败分解为 backbone 与多类持久资产的可执行定位。",
      ("MASA", "SkCC", "Version-Differential Failure Localization", "WorMI"),
      "定位后的最小修复应优于全量重写，并避免破坏已兼容资产。",
      "全量重写、只改 Prompt、只改技能、语义相似、Oracle。",
      "两类源模型和两类目标模型，四类资产；在 WebArena-Lite/ALFWorld 注入兼容故障。",
      "若定位低于逐资产消融，或修复成本接近全量重写，则停止。", ("web", "tool"), 28),
    c("behavior-triggered-privilege-lease", "行为证据触发的权限租约", "Behavior-Triggered Privilege Lease", "permission", "pass",
      "静态权限忽略 Agent 版本和任务能力变化；一次可靠不等于永久可以持有高权限。",
      "为高风险工具授予任务和时间限定的租约；根据独立成功、越界和回退证据续租、缩减或撤销。",
      "ToolPrivBench/AuthBench/SEAgent 研究最小权限，AAL/ACL 分离能力与授权；版本证据驱动的权限租约仍不同。",
      ("ToolPrivBench", "AuthBench", "SEAgent", "AAL/ACL"),
      "动态租约应在匹配成功率下降低越权和攻击成功。",
      "静态最小权限、ABAC/MAC、固定风险等级、Prompt 安全规则。",
      "在 AuthBench/ToolPrivBench 风格任务上构造三轮 Agent 更新，不训练基础模型。",
      "若不能优于静态最小权限的安全—效用 Pareto，或依赖同模型自评，则停止。", ("security", "tool"), 18),
    c("privilege-recovery-curriculum", "权限恢复课程", "Privilege Recovery Curriculum", "permission", "pass",
      "权限降级后，系统常永久保守或一次性恢复，缺少可验证的逐级恢复。",
      "从失败类型生成最小能力与安全 probe，通过后逐级恢复权限；失败则保持或继续降级。",
      "最小权限工作关注初始授权和越权，AAL/ACL 给出层级；更新后的可学习恢复课程仍较少。",
      ("ToolPrivBench", "AuthBench", "AAL/ACL", "OR-Bench"),
      "逐级恢复应减少永久过度限制，同时不增加越权事件。",
      "永久降级、一次性恢复、固定等待、人工审批。",
      "构造必要、无关和敏感权限三类任务；两模型、三 seed，权限状态为持久更新。",
      "若在第二任务域不能减少过度拒绝，或安全事件增加，则停止。", ("security", "tool"), 20),
    c("update-aware-permission-downgrade", "更新感知的权限降级", "Update-Aware Permission Downgrade", "permission", "pass",
      "Prompt、记忆、技能、工作流或模型更新会改变工具行为，但权限通常沿用旧版本。",
      "每次持久更新后把高风险权限降到最小集合；通过变更相关安全与效用回归后再恢复。",
      "SEAgent 等管理静态权限，Regression-Gated 管理更新提交；更新后的授权重认证尚未直接建立。",
      ("SEAgent", "ToolPrivBench", "Regression-Gated Self-Evolution", "Change-Triggered Regression Exams"),
      "更新感知降级应阻止新越权，同时比永久最低权限保持更高成功率。",
      "权限不变、永久最低、固定完整回归、ABAC/MAC。",
      "在 Prompt、记忆和技能三种更新后运行 ToolPrivBench/AuthBench 风格任务。",
      "若安全收益来自永久禁用高权限，或恢复阶段无法保持成功率，则停止。", ("security", "continual"), 22),
    c("least-privilege-skill-graduation", "最小权限技能晋级", "Least-Privilege Skill Graduation", "permission", "revise",
      "新技能通常一次获得完整工具权限。", "技能通过逐级测试后从只读、沙箱、监督执行晋升到完整权限。",
      "Agent Skills survey 已提出四级生命周期治理，ToolPrivBench/AuthBench 提供最小权限测量。",
      ("Agent Skills survey", "ToolPrivBench", "AuthBench", "SkillSpector"),
      "技能晋级减少高权限暴露。", "固定技能权限、静态四级治理。", "AgentSkills 任务。",
      "除非加入可学习证据更新与跨版本恢复，否则作为权限租约组件。", ("security", "skill"), 18),
]

# __MORE_CANDIDATES__


def _external() -> dict[str, list[dict[str, Any]]]:
    if not DEFAULT_EXTERNAL_JSON.exists():
        return {}
    try:
        payload = json.loads(DEFAULT_EXTERNAL_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    reviews = payload.get("reviews", {})
    return reviews if isinstance(reviews, dict) else {}


DISCUSSION_PRIORITY = (
    "regression-probe-half-life",
    "version-differential-failure-localization",
    "model-swap-compatibility-certificate",
    "update-aware-permission-downgrade",
    "cross-form-capability-transfer-gap",
    "delayed-regression-exams",
    "privilege-recovery-curriculum",
    "behavior-triggered-privilege-lease",
)


def build_machine_school_bank() -> dict[str, Any]:
    ext = _external()
    rows = []
    for raw_rank, item in enumerate(CANDIDATES, 1):
        row = dict(item)
        row["raw_rank"] = raw_rank
        translations = MACHINE_SCHOOL_ENGLISH.get(row["id"], {})
        for field, english in translations.items():
            if field in row and isinstance(row[field], dict):
                row[field] = {"zh": row[field]["zh"], "en": english}
        row["external_reviews"] = ext.get(row["id"], [])
        latest_review = row["external_reviews"][-1] if row["external_reviews"] else {}
        row["external_verdict"] = latest_review.get("verdict", "pending")
        row["external_confidence"] = latest_review.get("confidence", "")
        if row["external_verdict"] == "pass":
            row["final_status"] = "pilot-now"
        elif row["external_verdict"] == "revise":
            row["final_status"] = "repair-then-decide"
        elif row["external_verdict"] == "block":
            row["final_status"] = "stop-or-merge"
        elif row["internal_decision"] == "pass":
            row["final_status"] = "external-review-pending"
        elif row["internal_decision"] == "revise":
            row["final_status"] = "internal-revise"
        else:
            row["final_status"] = "internal-reject"
        rows.append(row)
    order = {"pass": 0, "revise": 1, "reject": 2}
    rows.sort(key=lambda x: (order[x["internal_decision"]], x["budget"]["gpu_hours"], x["raw_rank"]))
    for rank, row in enumerate(rows, 1):
        row["screen_rank"] = rank
    passed = [x for x in rows if x["internal_decision"] == "pass"]
    external_order = {"pass": 0, "revise": 1, "pending": 2, "block": 3}
    priority_index = {idea_id: index for index, idea_id in enumerate(DISCUSSION_PRIORITY)}
    passed.sort(key=lambda x: (external_order.get(x["external_verdict"], 9), priority_index.get(x["id"], 999), x["budget"]["gpu_hours"], x["raw_rank"]))
    for rank, row in enumerate(passed, 1):
        row["external_rank"] = rank
    revise = [x for x in rows if x["internal_decision"] == "revise"]
    rejected = [x for x in rows if x["internal_decision"] == "reject"]
    latest = [x["external_verdict"] for x in passed if x["external_verdict"] != "pending"]
    discussion_shortlist = [x for x in passed if x["id"] in DISCUSSION_PRIORITY and x["external_verdict"] in {"pass", "revise"}]
    discussion_shortlist.sort(key=lambda x: priority_index[x["id"]])
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": bi("用户提供的 AI 学习委员宇宙截图", "User-provided machine-school metaphor screenshot"),
        "target_venue": "ICLR",
        "policy": {"max_gpus": 2, "max_gpu_hours": 32, "gates": ["persistent learning", "identifiable variable", "official-source collision", "independent feedback", "multi-round stability", "out-of-loop transfer", "matched budgets", "falsifiable P0/P1/P2"]},
        "summary": {"raw": len(rows), "internal_pass": len(passed), "internal_revise": len(revise), "internal_reject": len(rejected), "external_reviewed": sum(bool(x.get("external_reviews")) for x in passed), "external_pass": latest.count("pass"), "external_revise": latest.count("revise"), "external_block": latest.count("block")},
        "inspirations": [{"id": i, "meme": bi(zh, en), "research_variable": bi(vzh, ven)} for i, zh, en, vzh, ven in INSPIRATIONS],
        "teacher_shortlist": discussion_shortlist,
        "passed_ideas": passed,
        "revise_ideas": revise,
        "rejected_ideas": rejected,
        "all_candidates": rows,
    }


def validate_bank(payload: dict[str, Any]) -> list[str]:
    errors = []
    rows = payload.get("all_candidates", [])
    if len(rows) != 24 or len({x.get("id") for x in rows}) != 24:
        errors.append("expected 24 unique candidates")
    if payload.get("summary", {}).get("internal_pass") != 11:
        errors.append("expected 11 pass candidates")
    if payload.get("summary", {}).get("internal_revise") != 7:
        errors.append("expected 7 revise candidates")
    if payload.get("summary", {}).get("internal_reject") != 6:
        errors.append("expected 6 rejected candidates")
    for row in rows:
        if row.get("budget", {}).get("max_gpus", 9) > 2 or row.get("budget", {}).get("gpu_hours", 99) > 32:
            errors.append(f"budget violation: {row.get('id')}")
    return errors


def write_machine_school_bank(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    payload = build_machine_school_bank()
    errors = validate_bank(payload)
    if errors:
        raise ValueError("Invalid machine-school bank: " + "; ".join(errors))
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.MACHINE_SCHOOL_IDEAS = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(write_machine_school_bank()["summary"], ensure_ascii=False))
