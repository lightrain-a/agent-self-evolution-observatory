from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "cvpr-low-resource-ideas.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "cvpr-low-resource-ideas.js"


def bi(zh: str, en: str | None = None) -> dict[str, str]:
    """The advisor bank is Chinese-first; English titles remain explicit."""

    return {"zh": zh.strip(), "en": (en or zh).strip()}


@dataclass(frozen=True, slots=True)
class Budget:
    max_gpus: int
    gpu_hours: int
    wall_days: int
    training: str


@dataclass(frozen=True, slots=True)
class IdeaSeed:
    id: str
    title: dict[str, str]
    track: str
    problem: str
    core: str
    method: str
    advantage: str
    collision: str
    pilot: str
    metric: str
    stop: str
    nearest: tuple[str, ...]
    datasets: tuple[str, ...]
    budget: Budget
    operator: str
    scores: dict[str, int]


TRACKS: dict[str, dict[str, Any]] = {
    "observation": {
        "label": bi("主动视觉证据与观察", "Active visual evidence and observation"),
        "rationale": "视觉 Agent 的错误经常不是推理器不会推理，而是没有看到、没有复看或没有保存真正支持结论的视觉证据。把观察决策与持久更新绑定，可以用冻结模型直接验证。",
        "importance": "该方向把视觉输入从一次性前处理提升为可审计、可修订的主动证据过程，视觉不可替代性强。",
        "baseline": "固定均匀采样、一次性 crop/search、LensWalk/SenseSearch 式主动观察，以及相同查询预算的随机复看。",
        "models": ("Qwen2.5-VL-7B-Instruct", "InternVL3-8B", "LLaVA-OneVision-7B"),
    },
    "memory": {
        "label": bi("视觉记忆进化与治理", "Visual memory evolution and governance"),
        "rationale": "现有视觉记忆方法证明记忆有用，但很少验证记忆何时失效、何时污染后续任务以及如何只修复局部错误。冻结 Agent 上的记忆写入/检索门控即可形成可证伪实验。",
        "importance": "可靠记忆是跨任务自进化成立的前提；错误记忆会跨任务放大，影响比单轮回答错误更持久。",
        "baseline": "无记忆、文本记忆、视觉 exemplar、AtlasVA/HyMEM 式结构化记忆、相同容量随机删除或 FIFO。",
        "models": ("Qwen2.5-VL-7B-Instruct", "InternVL3-8B", "OpenVLA-7B"),
    },
    "critique": {
        "label": bi("视觉批评与奖励验证", "Visual critique and reward verification"),
        "rationale": "Actor 与 Critic 常共享视觉盲点，语言上合理的 critique 不一定由图像证据支持。通过视图解耦、反事实干预和校准可直接检验 critique 是否真的因果有效。",
        "importance": "自进化依赖反馈；若反馈不可靠，训练越久越可能固化错误。该问题直接服务视觉自改进的可信反馈。",
        "baseline": "自批评、独立 VLM critic、VISCO/Critic-V/Perceval，以及相同调用次数的 majority vote。",
        "models": ("Qwen2.5-VL-7B-Instruct", "InternVL3-8B", "Molmo-7B"),
    },
    "tools": {
        "label": bi("视觉工具与路由进化", "Visual tool and router evolution"),
        "rationale": "现有 agentic VLM 能调用 crop、search、detector 或生成器，但对工具能力边界、版本变化和组合冲突缺少轻量验证。小规模 probe 即可建立可测机制。",
        "importance": "工具路由决定视觉 Agent 的成本、鲁棒性和可扩展性；错误的能力记忆会让系统持续选择错误工具。",
        "baseline": "静态规则、单步分类路由、SenseSearch、CLOVA、OctoT2I，以及相同工具预算的 oracle/随机路由。",
        "models": ("Qwen2.5-VL-7B-Instruct", "InternVL3-8B"),
    },
    "video": {
        "label": bi("视频与时序 Agent", "Video and temporal agents"),
        "rationale": "长视频 Agent 必须在有限帧预算下维护可修订的时序证据；最终答案正确无法说明中间定位、压缩和复看策略可靠。",
        "importance": "时序证据管理是长视频 Agent 从一次性推理走向持续学习的关键视觉问题。",
        "baseline": "均匀采样、固定摘要、LensWalk、VISTA、AgenticVS，以及相同帧预算的随机重采样。",
        "models": ("Qwen2.5-VL-7B-Instruct", "InternVL3-8B", "Video-LLaVA-7B"),
    },
    "embodied": {
        "label": bi("具身视觉与 VLA 过程安全", "Embodied vision and VLA process safety"),
        "rationale": "具身 Agent 可能完成任务但经历不安全、不可恢复或错误归因的中间过程。利用已有轨迹做写入门控与过程审计，无需重新训练大模型。",
        "importance": "真实部署关注的不只是终点成功，还包括过程、恢复和经验是否值得固化，具有明确的视觉闭环贡献。",
        "baseline": "仅按任务成功写入、语言反思、EvoNav/AtlasVA 式经验记忆，以及相同轨迹数的随机写入。",
        "models": ("OpenVLA-7B", "OpenVLA-OFT", "Qwen2.5-VL-7B-Instruct"),
    },
    "generation": {
        "label": bi("生成与编辑 Agent", "Generation and editing agents"),
        "rationale": "自改进生成/编辑循环常由同一评价器反复选择和改写，可能产生偏好漂移、奖励投机与无效编辑。黑盒生成结果和局部重渲染即可验证。",
        "importance": "该方向直接影响图像/视频生成 Agent 的可靠自动优化与推理成本。",
        "baseline": "固定 prompt、VISTA/JarvisEvo/OctoT2I、单评价器迭代与相同生成次数的 best-of-N。",
        "models": ("SDXL", "FLUX.1-schnell", "Qwen2.5-VL-7B-Instruct"),
    },
    "evaluation": {
        "label": bi("视觉自进化评测与诊断", "Evaluation and diagnostics for visual self-evolution"),
        "rationale": "现有工作多报告更新后平均准确率，难以区分真实能力增长、检索捷径、评价器过拟合和跨任务负迁移。可在公开模型与已有日志上构建诊断。",
        "importance": "缺少可证伪评测会让视觉自进化论文无法说明究竟进化了什么；高质量 benchmark 本身适合 CVPR。",
        "baseline": "更新前后平均准确率、常规 continual-learning 指标、随机任务顺序和无审计日志设置。",
        "models": ("Qwen2.5-VL-7B-Instruct", "InternVL3-8B", "OpenVLA-7B"),
    },
}


def S(
    id: str,
    title_en: str,
    title_zh: str,
    track: str,
    problem: str,
    core: str,
    method: str,
    advantage: str,
    collision: str,
    pilot: str,
    metric: str,
    stop: str,
    nearest: tuple[str, ...],
    datasets: tuple[str, ...],
    gpus: int,
    hours: int,
    days: int,
    operator: str,
    scores: tuple[int, int, int, int, int],
) -> IdeaSeed:
    return IdeaSeed(
        id=id,
        title=bi(title_zh, title_en),
        track=track,
        problem=problem,
        core=core,
        method=method,
        advantage=advantage,
        collision=collision,
        pilot=pilot,
        metric=metric,
        stop=stop,
        nearest=nearest,
        datasets=datasets,
        budget=Budget(gpus, hours, days, "冻结主模型；仅允许规则、检索器、小型校准器或 LoRA 级更新。"),
        operator=operator,
        scores=dict(zip(("novelty", "vision", "validity", "evidence", "feasibility"), scores)),
    )


IDEAS: tuple[IdeaSeed, ...] = (
    # A. Active visual evidence and observation (6)
    S("visual-evidence-debt", "Visual Evidence Debt", "视觉证据债务", "observation",
      "Agent 在没有足够视觉支持时仍会提交答案或经验，且后续任务无法知道哪些结论仍欠缺证据。",
      "为每个视觉 claim 维护证据债务；只有债务经主动复看下降到阈值后，答案或经验才能提交。",
      "抽取 claim→定位支持帧/区域→遮挡或重采样验证→累计债务→决定继续观察、弃权或写入。",
      "相比单纯 uncertainty，它明确指出缺哪一段视觉证据，并把观察预算花在未偿还 claim 上。",
      "LensWalk 解决如何主动看；本 Idea 研究何时证据足以支持持久结论，并提供 claim 级债务指标。",
      "在 Video-MME 和 MM-Vet 上给固定帧/crop 预算，比较债务门控与置信度、随机复看。",
      "claim 支持准确率、单位视觉预算准确率、错误经验写入率。",
      "债务分数不能比模型置信度更好地预测错误，或主动复看在等预算下无增益。",
      ("LensWalk", "SenseSearch", "Perceval"), ("Video-MME", "MM-Vet"), 1, 12, 3,
      "metric-replacement", (5, 5, 4, 5, 5)),
    S("counterfactual-observation-admission", "Counterfactual Observation Admission", "反事实观察准入", "observation",
      "一次成功观察容易把偶然背景或无关区域误当成可复用视觉经验。",
      "经验写入前对关键区域做遮挡、替换和邻近 crop；只有结论对因果区域敏感、对无关区域稳定时才准入。",
      "定位候选证据→生成三类局部反事实→重放答案/动作→计算因果选择性→写入或拒绝。",
      "不需要训练新 critic，直接用可解释干预检验经验是否依赖正确视觉因素。",
      "现有自训练通常过滤答案正确性；这里过滤视觉因果依据，避免背景捷径进入记忆。",
      "在 Winoground、MMVP、CV-Bench 上构造正确答案但错误依据的成功样本，测写入后跨样本迁移。",
      "错误依据拒绝率、有效经验保留率、下游负迁移。",
      "反事实选择性与后续迁移无相关性，或拒绝大量有效经验而无净收益。",
      ("VisPlay", "VISCO", "Perceval"), ("Winoground", "MMVP", "CV-Bench"), 1, 18, 4,
      "objective-evaluation-mismatch", (5, 5, 5, 4, 5)),
    S("adaptive-revisit-budget", "Adaptive Revisit Budget", "自适应复看预算", "observation",
      "主动视觉 Agent 往往固定迭代次数，简单样本浪费预算，困难样本又过早停止。",
      "根据相邻观察轮的证据集合稳定性，而非语言置信度，决定继续复看还是停止。",
      "记录每轮支持区域/帧→计算集合变化与答案敏感性→学习无训练阈值或小型校准器→动态停止。",
      "与固定轮数相比，同等准确率下可显著减少视觉调用；与置信度停止相比更贴近视觉证据。",
      "VISTA/LensWalk 使用迭代循环；本 Idea 的新变量是视觉证据稳定性停止规则。",
      "在 LVBench、Video-MME、DocVQA 上绘制准确率—视觉调用 Pareto 曲线。",
      "AUC-Pareto、平均视觉调用次数、困难样本召回。",
      "证据稳定性不能优于置信度或简单轮数规则。",
      ("LensWalk", "VISTA"), ("LVBench", "Video-MME", "DocVQA"), 1, 10, 3,
      "metric-replacement", (4, 5, 4, 5, 5)),
    S("multiview-disagreement-search", "Multi-View Disagreement Search", "多视图分歧搜索", "observation",
      "全图、局部 crop 与不同分辨率视图给出矛盾结论时，现有系统通常直接投票而不是定位分歧来源。",
      "把跨视图分歧转化为下一次观察策略：优先搜索导致结论翻转的空间区域。",
      "并行获取低成本视图→比较 claim/答案→反向定位冲突区域→定向高分辨率观察→更新结论。",
      "比多数投票多提供分歧定位和可解释修复，同时只在冲突样本增加预算。",
      "SenseSearch 协调多工具；本 Idea 专注视图之间的冲突驱动搜索，不需 RL。",
      "在高分辨率细粒度 VQA 与图表问答上比较固定 crop、随机 crop 和分歧驱动 crop。",
      "冲突样本准确率、额外 crop 数、分歧定位 IoU。",
      "分歧无法可靠定位错误区域，或额外观察成本抵消收益。",
      ("SenseSearch", "DeepScan"), ("HR-MMSearch", "ChartQA", "DocVQA"), 1, 14, 3,
      "limitation-inversion", (4, 5, 4, 5, 5)),
    S("observation-provenance-graph", "Observation Provenance Graph", "观察证据溯源图", "observation",
      "视觉 Agent 将结论、工具结果和经验写入文本后，无法追踪其来自哪一帧、哪一 crop、哪个工具版本。",
      "构建 claim—视觉区域—工具调用—经验条目的轻量溯源图，并用图上的断链检测不可信更新。",
      "每次观察保存哈希和坐标→claim 对齐→构图→写入时检查可达证据→下游错误时反向定位污染源。",
      "相比普通日志，它支持跨任务追责与局部回滚，不需要改变基础模型。",
      "EvoGraph-R1 进化知识图；本 Idea 的核心是视觉证据链和更新审计，而非提高 GraphRAG 准确率。",
      "在图表、视频与 GUI 三类任务上注入过期 crop 或错误工具结果，测定位与回滚。",
      "污染源定位率、局部回滚恢复率、存储开销。",
      "溯源图不能比时间戳/平面日志更准确地定位污染。",
      ("EvoGraph-R1", "LensWalk"), ("ChartQA", "Video-MME", "ScreenSpot"), 1, 16, 4,
      "cross-domain-analogy", (5, 5, 4, 4, 5)),
    S("negative-visual-evidence-memory", "Negative Visual Evidence Memory", "负视觉证据记忆", "observation",
      "Agent 会反复搜索已经确认不存在的对象、帧或 UI 控件，造成长期视觉预算浪费。",
      "记忆不仅保存发现了什么，也保存在何种视图和覆盖范围内未发现什么，并随环境变化自动失效。",
      "记录搜索范围与未命中条件→估计覆盖充分度→检索负证据→决定跳过、扩大搜索或重新验证。",
      "比仅存成功 exemplar 更能减少重复无效观察，并能显式控制负证据的适用边界。",
      "现有 visual memory 主要保存正例；本 Idea 研究可验证、可过期的 absence memory。",
      "在 GUI、长视频与导航任务中重复设置缺失目标，比较无记忆、正记忆和负证据记忆。",
      "无效视觉调用下降、漏检率、负证据过期准确率。",
      "节省调用但显著增加漏检，或覆盖充分度无法校准。",
      ("AtlasVA", "HyMEM", "LensWalk"), ("AndroidWorld", "Video-MME", "Habitat"), 1, 10, 3,
      "missing-cell", (5, 5, 4, 4, 5)),

    # B. Visual memory evolution and governance (6)
    S("visual-memory-half-life", "Visual Memory Half-Life", "视觉记忆半衰期", "memory",
      "视觉 exemplar 和空间规则被永久保留，即使场景、界面或具身状态已变化。",
      "根据跨任务重放中的支持率、冲突率和时间漂移估计每条视觉记忆的半衰期，而非统一 FIFO 删除。",
      "周期抽样重放→统计记忆帮助/伤害→拟合生存分数→衰减、复验或删除→记录性能恢复。",
      "比固定容量或时间淘汰能保留长期有效知识，同时更快移除过期视觉经验。",
      "AtlasVA/HyMEM 强调记忆增长；本 Idea 研究可验证的记忆失效与选择性遗忘。",
      "在 AndroidWorld 界面版本变化和 Habitat 场景迁移上模拟漂移。",
      "记忆伤害 AUC、删除后恢复率、有效记忆保留率。",
      "半衰期分数不优于 recency/FIFO，或删除无法改善负迁移。",
      ("AtlasVA", "HyMEM"), ("AndroidWorld", "Habitat"), 1, 12, 4,
      "limitation-inversion", (5, 5, 4, 5, 5)),
    S("retrieval-interference-auditor", "Retrieval Interference Auditor", "检索干扰审计器", "memory",
      "记忆检索提升平均准确率，却可能在少数任务上强烈误导 Agent，而常规 ablation 只比较有/无记忆。",
      "对每次检索做 matched replay：保持其他条件不变，比较有记忆、打乱记忆和无记忆，识别真正的干扰条目。",
      "缓存输入与随机种子→三臂重放→估计条目级处理效应→隔离或降权有害记忆。",
      "直接测量记忆的因果增益/伤害，而非用相似度或最终成功率猜测。",
      "区别于 retrieval quality 工作：目标是验证持久记忆是否造成跨任务负效应。",
      "在 GUI、VQA 和 VLN 上对现有 memory agent 加旁路审计，不重训主模型。",
      "条目级伤害识别 AUC、隔离后净收益、重放成本。",
      "matched replay 不能稳定复现干扰，或干扰条目移除后无改善。",
      ("HyMEM", "AtlasVA"), ("AndroidWorld", "MM-Vet", "R2R"), 1, 18, 4,
      "objective-evaluation-mismatch", (5, 5, 5, 5, 5)),
    S("dual-channel-memory-consistency", "Dual-Channel Memory Consistency", "双通道记忆一致性", "memory",
      "文本总结会丢失几何与外观信息，视觉 exemplar 又缺少抽象适用条件，两者可能互相矛盾。",
      "每条经验同时保存视觉证据与符号规则；检索后先做跨通道一致性检查，再决定采用、修复或弃权。",
      "视觉相似检索+规则检索→交叉验证关键属性→冲突分类→选择视觉重查或文本重写。",
      "相比单通道记忆，既保留视觉细节又显式表达边界，并能检测总结幻觉。",
      "AtlasVA 采用多层记忆；本 Idea 将跨层冲突本身作为门控和可测目标。",
      "在空间推理、GUI 和导航中人工/自动注入摘要错误与 exemplar 错配。",
      "冲突检测率、修复后任务成功率、错误写入率。",
      "冲突分数无法预测失败，或双通道成本无对应收益。",
      ("AtlasVA", "HyMEM"), ("CV-Bench", "AndroidWorld", "R2R"), 1, 20, 4,
      "contradiction-resolution", (4, 5, 5, 4, 5)),
    S("applicability-masked-visual-skills", "Applicability-Masked Visual Skills", "带适用掩码的视觉技能", "memory",
      "从少量成功轨迹总结的技能往往被过度泛化到外观相似但约束不同的场景。",
      "为每个技能学习轻量视觉适用掩码：哪些物体关系、状态和视角满足时才允许调用。",
      "从成功/失败重放提取可见条件→形成原型或小型分类器→调用前验证→越界时退回基础策略。",
      "比纯文本技能描述更能表达空间边界，且只训练很小的适用性头。",
      "现有 skill memory 关注检索与复用；本 Idea把视觉 applicability 作为第一类对象。",
      "在 ALFRED、CALVIN 或 LIBERO 上对已有技能库做跨场景重放。",
      "越界调用下降、技能成功率、基础策略回退成本。",
      "适用掩码无法优于视觉相似度阈值，或过度拒绝有效技能。",
      ("AtlasVA", "EvoNav"), ("ALFRED", "CALVIN", "LIBERO"), 2, 36, 6,
      "assumption-removal", (5, 5, 5, 5, 4)),
    S("local-counterexample-memory-repair", "Local Counterexample Memory Repair", "局部反例记忆修复", "memory",
      "发现一条错误记忆后，常见做法是整条删除或重新总结，可能丢失其中仍有效的部分。",
      "用最小反例定位错误条件，只修改记忆的适用边界或局部节点，并保留原始证据与版本。",
      "生成/检索最近反例→比较成功与失败条件→定位差异属性→打补丁→回归测试旧任务。",
      "比全量重写更低成本、可回滚，并能量化修复是否引入新回归。",
      "EvoGraph-R1 支持图编辑；本 Idea 研究反例驱动的最小视觉记忆补丁。",
      "在 GUI 工作流和对象操作技能中注入单条件错误，比较删除、重写和局部补丁。",
      "修复成功率、旧能力保持率、补丁大小。",
      "局部差异无法识别，或补丁与全量重写相比无保持优势。",
      ("EvoGraph-R1", "HyMEM"), ("AndroidWorld", "ALFRED"), 1, 18, 4,
      "cross-domain-analogy", (5, 5, 5, 5, 5)),
    S("visual-memory-lineage-containment", "Visual Memory Lineage Containment", "视觉记忆谱系隔离", "memory",
      "一条错误视觉经验可派生出多个总结、技能和路由规则，删除源条目仍不能清除后代污染。",
      "记录视觉记忆的派生谱系；源证据被推翻时，自动识别、复验并隔离所有依赖后代。",
      "写入时保存父子边→错误回溯→影响分析→优先复验高使用后代→局部失效与恢复。",
      "相比平面删除，能处理跨代传播并给出明确审计证据。",
      "通用 provenance 研究不等于视觉记忆污染控制；这里要求区域/帧级源证据和后代行为恢复。",
      "在合成的多轮视觉技能进化流中注入一个错误源，测污染传播与清除。",
      "污染后代召回、清除后恢复、误隔离率。",
      "谱系不能显著优于按时间窗口回滚，或维护开销过大。",
      ("EvoGraph-R1", "AtlasVA"), ("ALFRED", "AndroidWorld", "MM-Vet"), 1, 16, 4,
      "cross-domain-analogy", (5, 5, 4, 5, 5)),

    # C. Visual critique and reward verification (5)
    S("decoupled-view-critic", "Decoupled-View Critic", "解耦视图批评器", "critique",
      "Actor 与 Critic 使用同一 resize/crop 时会共享不可见区域和分辨率盲点，导致一致但错误的反馈。",
      "让 Critic 自动选择与 Actor 不同的视图和分辨率，并用视图互补性而非模型数量提升审查。",
      "记录 Actor 视图→生成互补 crop/尺度→Critic claim 检查→分歧定位→仅修复有视觉证据的步骤。",
      "比换一个同输入 critic 更便宜，也能明确证明增益来自视图互补而非模型规模。",
      "Critic-V/VISCO 关注 critic 能力；本 Idea 隔离输入视图共享造成的系统性盲点。",
      "在高分辨率 VQA、图表和 grounding 错误集上做同模型跨视图与跨模型同视图对照。",
      "错误检出率、互补盲点覆盖、每次修复调用数。",
      "跨视图不能优于跨模型同视图，或分歧主要来自随机噪声。",
      ("Critic-V", "VISCO", "Perceval"), ("HR-MMSearch", "ChartQA", "MMVP"), 1, 16, 4,
      "assumption-removal", (5, 5, 5, 5, 5)),
    S("spatial-critique-calibration", "Spatial Critique Calibration", "空间批评校准", "critique",
      "Critic 能输出流畅的错误说明，却没有显示自己是否定位到了真正的视觉错误区域。",
      "要求 critique 同时给出空间证据热图，并用区域定位正确性校准其建议是否可用于自改进。",
      "抽取 critique claim→生成区域热图→与可验证区域/反事实敏感区比较→校准 accept/reject。",
      "把语言 critique 质量转化为视觉可测信号，可阻止无依据建议进入训练或记忆。",
      "Perceval 做 claim 级感知错误；本 Idea 重点是 critique 可靠性校准和更新准入。",
      "在 RefCOCO、MMVP 和视觉编辑错误集上测定位与后续修复。",
      "校准误差、接受后修复成功率、错误 critique 拒绝率。",
      "空间定位不预测修复质量，或热图监督成本过高。",
      ("Perceval", "VISCO"), ("RefCOCO", "MMVP", "MagicBrush"), 1, 20, 4,
      "metric-replacement", (4, 5, 5, 5, 5)),
    S("counterfactual-critique-validation", "Counterfactual Critique Validation", "反事实批评验证", "critique",
      "模型提出的视觉 critique 可能只是事后合理化，按其建议修改图像或观察并不会改变错误结论。",
      "接受 critique 前执行最小反事实：只修正其声称的区域/属性，检查预测是否按方向改变。",
      "解析 critique→生成局部编辑或替代 crop→重跑答案→计算方向一致性→选择用于修复的 critique。",
      "直接检验 critique 的因果有效性，比语言相似度或人工打分更接近自改进目标。",
      "VISCO 测 critique/correction；本 Idea 增加可自动执行的因果准入测试。",
      "在对象属性、计数、空间关系错误上使用现有编辑器或遮挡生成反事实。",
      "方向一致性、有效 critique 精度、修复净增益。",
      "局部反事实质量不足，导致验证噪声高于原 critique 评分。",
      ("VISCO", "Critic-V"), ("MMVP", "CV-Bench", "MagicBrush"), 1, 22, 5,
      "objective-evaluation-mismatch", (5, 5, 5, 5, 5)),
    S("reward-invariance-audit", "Reward Invariance Audit", "奖励不变性审计", "critique",
      "自进化策略可能利用视觉奖励器的背景、边框、水印或压缩偏差，而真实任务质量没有提高；但普通增强敏感性不能直接等同于奖励捷径。",
      "构造三类 matched 干预：经人工/规则验证的语义保持变换、明确改变任务语义的正对照，以及与奖励相关但任务无关的捷径探针；只有三类效应可分离时才判定 shortcut。",
      "先冻结语义判定协议→为同一原图生成三类 matched 干预→比较任务标签、actor 输出和 reward→估计保持/改变效应分离度→定位并屏蔽捷径特征。",
      "相比泛化的增强鲁棒性测试，它用语义改变正对照证明 reward 并非应当对所有视觉变化不敏感，并能在不重训策略时审计 reward hacking。",
      "JarvisEvo/VisPlay 讨论 evaluator/reward；本 Idea 的差异是带语义正负对照的冻结策略因果审计，而不是单纯测试 JPEG 或颜色鲁棒性。",
      "在 MM-Vet、MagicBrush 和 GenEval 上，每类选择至少 100 个经双人或可执行规则确认的 matched triplets。",
      "语义保持违例率、保持/改变干预效应分离度、捷径探针 AUC、审计后选择质量。",
      "三类干预无法形成清晰效应分离，或所谓捷径变化与人类/任务偏好一致。",
      ("JarvisEvo", "VisPlay"), ("MM-Vet", "MagicBrush", "GenEval"), 1, 16, 4,
      "cross-domain-analogy", (5, 5, 5, 5, 5)),
    S("claim-level-visual-repair", "Claim-Level Visual Repair", "Claim 级视觉修复", "critique",
      "整段回答重写会破坏原本正确的视觉事实，也难以判断修复来自哪里。",
      "只重开被 Critic 判定为视觉无依据的 claim，并锁定其余已验证 claim。",
      "分解回答→逐 claim 取证→标记不通过项→定向 crop/search→局部替换→全局一致性检查。",
      "比全回答 self-refine 更稳定、可解释，调用预算集中在真正错误的视觉命题。",
      "Perceval 提供 claim 级错误信号；本 Idea 研究冻结模型下的局部修复与保持性。",
      "在长答案 VQA、图表解释和视频 QA 上比较全量改写、局部改写与不改。",
      "错误 claim 修复率、正确 claim 保持率、调用成本。",
      "局部锁定导致全局不一致，或正确 claim 保持优势不明显。",
      ("Perceval", "VISCO"), ("MM-Vet", "ChartQA", "Video-MME"), 1, 14, 3,
      "limitation-inversion", (4, 5, 5, 5, 5)),

    # D. Tool and router evolution (5)
    S("capability-frontier-probes", "Capability Frontier Probes", "工具能力边界探针", "tools",
      "工具路由器通常只记住平均表现，无法知道 detector、search 或生成器在什么视觉条件下失效。",
      "用小规模对比 probe 主动探索每个工具的能力边界，并把边界作为可更新路由记忆。",
      "从失败邻域生成 probe→估计工具成功边界→路由前检查→新结果增量更新边界。",
      "比大规模重训路由器更省资源，也比单一全局分数更能泛化到组合条件。",
      "OctoT2I 探索工具能力；本 Idea 聚焦可校准边界、最小 probe 和跨版本回归。",
      "在 crop/OCR/search 与多个轻量生成器上用 200–500 个 probe 建立边界。",
      "边界预测 AUC、路由 regret、probe 数量。",
      "边界模型不优于简单历史成功率，或需要过多 probe。",
      ("OctoT2I", "SenseSearch"), ("HR-MMSearch", "DocVQA", "GenEval"), 1, 18, 4,
      "pme-recombination", (4, 5, 5, 5, 5)),
    S("regression-tested-tool-evolution", "Regression-Tested Tool Evolution", "带回归测试的工具进化", "tools",
      "工具 prompt、API 或视觉技能更新后，系统只验证当前失败是否修复，可能破坏过去能力。",
      "每次工具更新自动选择一个最小视觉回归测试集，只有新能力提升且旧边界不退化才提交。",
      "维护版本与失败簇→选择覆盖 probe→候选更新→差分执行→commit/rollback。",
      "把软件 CI 的安全更新机制迁移到视觉工具进化，计算量仅为少量冻结推理。",
      "CLOVA 支持工具更新；本 Idea 的贡献是视觉能力回归选择和可验证提交协议。",
      "对 OCR、grounding、crop 和 GUI click 工具进行 prompt/版本更新实验。",
      "修复率、回归捕获率、每次提交测试成本。",
      "最小回归集不能预测完整测试退化，或成本接近全量测试。",
      ("CLOVA", "SenseSearch"), ("DocVQA", "RefCOCO", "ScreenSpot"), 1, 12, 3,
      "cross-domain-analogy", (5, 3, 5, 5, 5)),
    S("version-aware-visual-routing", "Version-Aware Visual Routing", "版本感知视觉路由", "tools",
      "工具升级或服务变化后，旧能力记忆仍被使用，导致路由器长期选择已改变的工具。",
      "把能力证据绑定到精确工具版本；版本变化时只失效相关边界并触发小规模再探测。",
      "记录 tool manifest 哈希→版本差异检测→影响边界定位→定向 probe→更新路由记忆。",
      "相比周期性全量重测，能局部刷新且避免陈旧能力信息污染。",
      "现有路由通常假设工具静态；本 Idea 把版本漂移作为视觉 Agent 自进化变量。",
      "模拟 OCR、detector 与生成器版本升级，比较无版本、全量重测和局部再探测。",
      "漂移恢复时间、错误路由数、再探测成本。",
      "版本变化与能力变化弱相关，局部影响分析无优势。",
      ("OctoT2I", "CLOVA"), ("DocVQA", "COCO", "GenEval"), 1, 10, 3,
      "assumption-removal", (5, 4, 5, 4, 5)),
    S("tool-composition-conflict-map", "Tool Composition Conflict Map", "工具组合冲突图", "tools",
      "单个工具都有效，不代表串联后有效；resize、crop、OCR、search 的顺序会产生隐藏冲突。",
      "从少量失败轨迹学习工具对/三元组的非交换性与冲突图，路由时避开高风险组合。",
      "收集工具序列→成对顺序交换→测输出变化→构建冲突图→约束组合搜索。",
      "比仅学习单工具分数更能解释组合失败，且只需离线重放。",
      "SenseSearch 学习多工具协调；本 Idea 提供无需 RL 的组合因果诊断与约束。",
      "在高分辨率 VQA 和文档 QA 上枚举小型工具组合。",
      "组合失败预测、序列搜索空间缩减、准确率。",
      "冲突主要由单工具质量解释，组合图无额外信息。",
      ("SenseSearch", "CLOVA"), ("HR-MMSearch", "DocVQA"), 1, 16, 4,
      "contradiction-resolution", (5, 5, 5, 5, 5)),
    S("cost-aware-failure-repair-router", "Cost-Aware Failure Repair Router", "成本感知失败修复路由", "tools",
      "Agent 失败后常从头运行完整工具链，而历史上可能已有更便宜的局部修复路径。",
      "把失败类型映射到最小修复动作，并通过成功/成本双目标持续更新修复路由。",
      "聚类失败证据→记录哪一步修复成功→估计条件成本→优先局部重试→失败再升级。",
      "与整链重跑相比能降低视觉调用和延迟，同时保留明确升级边界。",
      "现有 agentic routing 关注首次求解；本 Idea 研究跨任务积累的 failure-to-repair policy。",
      "在 GUI、文档和长视频任务上注入 OCR、定位和检索失败。",
      "修复成功/成本 Pareto、整链重跑率、错误升级率。",
      "局部修复经常改变全局答案，或节省成本不足。",
      ("SenseSearch", "LensWalk"), ("AndroidWorld", "DocVQA", "Video-MME"), 1, 14, 3,
      "missing-cell", (4, 5, 5, 5, 5)),

    # E. Video and temporal agents (5)
    S("temporal-evidence-ledger", "Temporal Evidence Ledger", "时序证据账本", "video",
      "视频 Agent 的中间结论会在后续帧出现后失效，但摘要通常覆盖旧结论而不保留修订理由。",
      "为每个时序 claim 保存支持区间、反对区间和版本；新证据到来时显式修订而非静默覆盖。",
      "逐轮抽取 claim→绑定帧段→检测支持/冲突→更新账本→答案只引用当前有效 claim。",
      "比纯文本摘要更能处理后出现的反证，并提供可审计的答案来源。",
      "LensWalk 主动取证；本 Idea 研究跨观察轮的时序 claim 生命周期。",
      "在 NExT-QA、Video-MME 和 EgoSchema 上构造早期误导、后期反转样本。",
      "冲突检测、错误结论修订率、引用区间准确率。",
      "账本不优于直接增加帧数或长上下文。",
      ("LensWalk", "AgenticVS"), ("NExT-QA", "Video-MME", "EgoSchema"), 1, 18, 4,
      "limitation-inversion", (5, 5, 5, 5, 5)),
    S("uncertainty-shaped-reobservation", "Uncertainty-Shaped Reobservation", "不确定性形状驱动复看", "video",
      "相同置信度可能来自不同失败：时间边界不确定、对象身份不确定或跨段关系不确定，需要不同复看策略。",
      "将 uncertainty 分解为空间、时间边界和关系三类，并映射到不同重采样动作。",
      "对答案做扰动诊断→识别不确定性形状→选择密采样、跨段对齐或局部放大→重新推理。",
      "比单一置信度阈值更具体，能用相同帧预算选择正确观察操作。",
      "LensWalk 动态选范围/密度；本 Idea 以可诊断 uncertainty type 驱动策略且无需训练。",
      "在时间定位、细粒度动作和多段因果问题上分层评测。",
      "每类错误修复率、帧预算、策略选择准确率。",
      "不确定性类型无法稳定识别或策略差异无增益。",
      ("LensWalk", "EVA"), ("Charades-STA", "Video-MME", "NExT-QA"), 1, 16, 4,
      "pme-recombination", (4, 5, 4, 5, 5)),
    S("event-boundary-counterfactual", "Event-Boundary Counterfactual Test", "事件边界反事实测试", "video",
      "视频答案可能依赖恰好包含目标动作的采样边界，轻微平移窗口就翻转；但如果没有因果帧真值，翻转也可能只是正常的时序分布变化。",
      "为每个问题构造三类窗口：包含标注因果事件的原窗口、只改变无关上下文的边界扰动，以及删除/替换因果帧的正对照；可靠结论应对前者稳定、对后者敏感。",
      "从 Charades-STA 等有时间标注数据取得事件区间→人工抽查因果充分性→生成无关扩张/收缩与因果帧删除→等预算重跑→计算稳定性—敏感性间隔→准入或扩大观察。",
      "它不再把所有边界变化都视为错误，而是用因果帧正对照区分合理敏感性和偶然采样依赖，直接测量时序证据质量。",
      "现有视频 Agent 优化采样；本 Idea 把经标注/验证的因果帧与无关边界分开，并将其稳定性间隔用于经验准入。",
      "先在 Charades-STA 构建 200–300 个预注册因果窗口，再冻结规则迁移到 Video-MME/LVBench 的可定位子集。",
      "无关边界一致率、因果帧干预效应、两者效应间隔、错误经验拒绝率。",
      "因果帧构造的一致性不足，或稳定性—敏感性间隔不能预测跨采样泛化。",
      ("LensWalk", "EvoGround"), ("Charades-STA", "Video-MME", "LVBench"), 1, 16, 4,
      "objective-evaluation-mismatch", (5, 5, 5, 5, 5)),
    S("contradiction-preserving-video-memory", "Contradiction-Preserving Video Memory", "保留矛盾的视频记忆压缩", "video",
      "长视频压缩通常保留共识摘要，却丢掉少数反例和状态变化，后续问答因而产生过度概括。",
      "压缩时强制保留改变结论的反证帧和状态转折，而非只选代表性帧。",
      "生成候选摘要→搜索与摘要冲突的帧→加入最小反证集合→预算内联合存储。",
      "与聚类/均匀关键帧相比，更适合需要否定、例外和状态变化的推理。",
      "普通 video memory 压缩关注覆盖；本 Idea 以结论改变能力定义信息价值。",
      "在长视频异常、状态追踪和多事件问答上比较。",
      "反证保留率、压缩后答案一致性、存储预算。",
      "反证集合难以自动识别，或收益等价于增加更多帧。",
      ("AgenticVS", "LensWalk"), ("Video-MME", "EgoSchema", "NExT-QA"), 1, 14, 4,
      "metric-replacement", (5, 5, 5, 5, 5)),
    S("iterative-video-reasoning-consistency", "Iterative Video Reasoning Consistency", "迭代视频推理过程一致性", "video",
      "视频 Agent 多轮改进后最终答案更好，但中间引用的帧和事件关系可能互相矛盾。",
      "定义跨轮过程一致性：新一轮必须解释为何新增视觉证据推翻或强化旧 claim。",
      "记录每轮 claim/证据→构建转移类型→检测无证据翻转→要求复看或回退。",
      "区别于只比较最终答案，能发现通过猜测获得的偶然改进。",
      "VISTA/AgenticVS 使用 self-reflection；本 Idea 直接评测和约束跨轮视觉证据一致性。",
      "在 Video-MME 与 NExT-QA 上分析多轮 prompt refinement/observation。",
      "无证据翻转率、最终正确但过程不一致率、门控后准确率。",
      "过程一致性与可靠性无关，或门控抑制有效探索。",
      ("VISTA", "AgenticVS"), ("Video-MME", "NExT-QA"), 1, 10, 3,
      "objective-evaluation-mismatch", (5, 5, 4, 5, 5)),

    # F. Embodied vision and VLA process safety (5)
    S("recovery-conditioned-skill-admission", "Recovery-Conditioned Skill Admission", "恢复条件化技能准入", "embodied",
      "具身 Agent 从一次成功轨迹提炼技能，但成功可能依赖异常状态、临时干预或不可复现恢复。",
      "只有轨迹在干预释放后回到稳定可复用状态，经验才可固化为技能。",
      "检测目标事件→释放干预→测几何重合、动作一致与终局残差→按恢复等级准入。",
      "比任务成功门控更严格，能阻止不可恢复过程被当作好经验。",
      "现有经验记忆关注成功/失败；本 Idea 把闭环恢复状态作为写入因果条件。",
      "复用 OpenVLA/OpenVLA-OFT 与现有扰动轨迹，先做离线/小规模闭环 Pilot。",
      "错误技能写入率、跨任务重用成功、恢复等级预测。",
      "恢复等级不能预测技能重用，或所需状态不可观测。",
      ("EvoNav", "AtlasVA"), ("LIBERO", "CALVIN"), 2, 36, 7,
      "objective-evaluation-mismatch", (5, 5, 5, 5, 4)),
    S("unsafe-success-experience-filter", "Unsafe-but-Successful Experience Filter", "成功但不安全的经验过滤", "embodied",
      "任务成功轨迹可能经过禁区、危险接触或不必要绕行，现有自进化仍会把它当正经验。",
      "把过程安全事件与终点成功分开；成功轨迹只有通过过程审计才进入记忆。",
      "定义轻量过程规则/视觉事件检测→审计成功轨迹→标注安全、可修复或拒绝→比较后续学习。",
      "直接解决 success≠safe execution，且可在现有轨迹上完成，无需大规模训练。",
      "具身 benchmark 常以成功率为主；本 Idea 研究成功经验的过程质量与跨任务影响。",
      "在 LIBERO/CALVIN/导航环境选取碰撞、禁区和对象状态事件。",
      "unsafe-success 检出、过滤后成功率、安全事件率。",
      "过程过滤不降低后续风险，或事件规则不具跨场景稳定性。",
      ("EvoNav", "Phoenix"), ("LIBERO", "CALVIN", "Habitat"), 2, 30, 6,
      "metric-replacement", (5, 5, 5, 5, 5)),
    S("action-grounding-commit-gate", "Action-Grounding Commit Gate", "动作视觉依据提交门", "embodied",
      "Agent 能执行正确动作，但理由可能引用错误物体或状态，导致总结出的技能不可迁移。",
      "提交经验前验证动作理由是否能在对应帧中定位到正确对象、关系和状态。",
      "解析 action rationale→ground 到图像→遮挡/替换关键对象→检查动作敏感性→准入。",
      "比只看 action match 更能区分真正视觉策略与偶然正确动作。",
      "VLA 过程分析多比较动作/终点；本 Idea 将视觉因果依据用于经验准入。",
      "在 CALVIN/LIBERO 现有轨迹上离线重放，少量闭环确认。",
      "错误依据拒绝率、经验重用成功、动作保持率。",
      "grounding 不能预测重用，或 rationale 本身不稳定。",
      ("Phoenix", "Perceval"), ("CALVIN", "LIBERO"), 2, 28, 6,
      "objective-evaluation-mismatch", (5, 5, 5, 4, 4)),
    S("minimal-visual-witness", "Minimal Visual Witness for Completion", "任务完成的最小视觉见证", "embodied",
      "具身任务结束时常靠环境 success flag，无法知道哪些最小视觉事实足以证明任务真的完成。",
      "为每类任务提取最小视觉 witness，并用删除测试验证每个 witness 是否必要。",
      "收集成功终点→候选对象/关系事实→逐项删除或遮挡→寻找最小充分集合→运行时验证。",
      "提供可解释、模型无关的完成证据，可发现 success flag 与可见状态不一致。",
      "区别于通用 VQA 验证：目标是闭环任务终止的最小视觉充分条件。",
      "在 ALFRED、CALVIN 或 LIBERO 上从已有终点图像构建。",
      "witness 完成判定、最小性、异常终点检出率。",
      "不同轨迹缺少稳定 witness，或环境 flag 已完全可靠。",
      ("EvoNav", "Phoenix"), ("ALFRED", "CALVIN", "LIBERO"), 1, 20, 5,
      "cross-domain-analogy", (5, 5, 4, 5, 5)),
    S("embodiment-drift-probes", "Embodiment Drift Probe Suite", "具身漂移探针集", "embodied",
      "相机位姿、机械臂标定或对象动力学变化后，Agent 的旧视觉技能会静默失效。",
      "维护覆盖视觉—动作接口的最小 probe 套件，检测 embodiment 变化并只失效受影响技能。",
      "从历史技能提取敏感维度→生成 probe→周期执行→定位漂移类型→选择重标定或回退。",
      "比任务失败后再修复更早发现问题，且无需持续全量评测。",
      "现有自进化假设 embodiment 稳定；本 Idea 把具身漂移检测与技能版本绑定。",
      "在模拟器中改变相机 FOV、位置偏移、动作尺度和摩擦参数。",
      "漂移检测延迟、受影响技能定位、probe 数。",
      "小型 probe 不能预测真实任务退化。",
      ("EvoNav", "AtlasVA"), ("CALVIN", "LIBERO", "Habitat"), 2, 32, 6,
      "assumption-removal", (5, 5, 5, 5, 4)),

    # G. Generation and editing agents (4)
    S("evaluator-preference-drift", "Evaluator Preference Drift Audit", "评价器偏好漂移审计", "generation",
      "生成 Agent 多轮按同一 evaluator 优化后，评价器偏好可能逐渐偏离人类或外部指标。",
      "用冻结的多源 probe 集持续测 evaluator 排序漂移，并在漂移前后比较生成轨迹。",
      "保存初始偏好锚点→每轮抽样 pairwise probe→检测排序翻转→切换 evaluator/停止更新。",
      "比最终一次人评更早定位循环何时开始奖励投机，计算量只增加少量评分。",
      "VISTA/JarvisEvo 使用 evaluator 循环；本 Idea 研究 evaluator 自身随优化过程的有效性边界。",
      "在图像编辑和视频 prompt refinement 中运行 3–5 轮小规模实验。",
      "偏好翻转率、外部指标/人评差距、早停收益。",
      "漂移信号不能早于质量下降，或不同 evaluator 同步漂移。",
      ("VISTA", "JarvisEvo"), ("MagicBrush", "GenEval", "VBench"), 1, 24, 5,
      "objective-evaluation-mismatch", (5, 5, 5, 5, 5)),
    S("edit-causality-check", "Edit Causality Check", "编辑因果性检查", "generation",
      "编辑结果被评价为更好，不代表改进来自指令要求的区域；模型可能同时改变背景或身份。",
      "通过 mask 重渲染和未编辑区域保持测试，验证质量提升是否由目标编辑引起。",
      "定位目标区域→生成完整编辑与仅目标区域合成→比较指令满足和非目标保持→决定接受。",
      "比单一 CLIP/美学分数能区分真正编辑成功与大范围投机。",
      "JarvisEvo 优化编辑器—评价器；本 Idea 提供 intervention-specific attribution gate。",
      "在 MagicBrush、PIE-Bench 或现有编辑集上无需训练。",
      "目标归因率、非目标保持、接受后人评。",
      "局部合成不代表真实生成机制，归因指标与人评不相关。",
      ("JarvisEvo", "VISCO"), ("MagicBrush", "PIE-Bench"), 1, 20, 4,
      "objective-evaluation-mismatch", (5, 5, 5, 5, 5)),
    S("prompt-memory-conflict-resolver", "Prompt Memory Conflict Resolver", "Prompt 记忆冲突消解", "generation",
      "生成 Agent 会积累风格、时序和负面 prompt 经验；不同经验组合后可能互相冲突。",
      "在应用多条 prompt memory 前预测其联合效果，并用最小 A/B 生成识别冲突对。",
      "检索候选记忆→成对组合 probe→测指令满足变化→构建冲突图→选择兼容子集。",
      "比简单拼接经验更稳定，且只对高风险组合增加少量生成。",
      "VISTA 使用多轮 prompt refinement；本 Idea 研究跨任务持久 prompt memory 的组合冲突。",
      "在 T2I-CompBench 和 VBench 小规模子集上测试。",
      "冲突预测、组合 regret、额外生成次数。",
      "冲突图不能泛化到新 prompt，或 best-of-N 已足够。",
      ("VISTA", "OctoT2I"), ("T2I-CompBench", "VBench"), 1, 30, 5,
      "missing-cell", (4, 5, 5, 5, 4)),
    S("budgeted-self-probing-router", "Budgeted Self-Probing Generator Router", "预算化自探测生成器路由", "generation",
      "生成器路由依赖静态 benchmark，无法知道当前 prompt 在不同轻量/重型模型上的真实难度。",
      "先用低分辨率或少步数 probe 估计各生成器对当前 prompt 的能力，再决定是否升级。",
      "各工具运行低成本 probe→VLM 比较关键属性→估计升级价值→选择最终工具/步数。",
      "相比总是调用最强模型，显著节省推理；相比静态分类，利用当前 prompt 的真实视觉结果。",
      "OctoT2I 学习长期工具能力；本 Idea 聚焦每个请求的低成本自探测与升级决策。",
      "用 SDXL/FLUX-schnell 和少步/多步配置在 GenEval/T2I-CompBench 测试。",
      "质量—延迟 Pareto、错误升级率、probe 成本。",
      "probe 排名不能预测完整生成质量。",
      ("OctoT2I", "Self-E"), ("GenEval", "T2I-CompBench"), 2, 36, 6,
      "pme-recombination", (5, 5, 5, 5, 4)),

    # H. Evaluation and diagnostics (6)
    S("visual-agent-regression-bench", "Visual Agent RegressionBench", "视觉 Agent 回归基准", "evaluation",
      "视觉 Agent 更新后只报告新任务收益，缺少覆盖旧视觉能力、工具调用和过程安全的最小回归集。",
      "从真实失败簇中自动选择最小 probe，评测每次 memory/tool/prompt 更新的收益与回归。",
      "汇总公开任务→聚类视觉能力→选择代表 probe→执行版本差分→输出 regression frontier。",
      "可作为多类视觉自进化方法的统一评测协议，不要求训练新模型。",
      "区别于普通 continual benchmark：评测对象包括记忆、工具和工作流更新及其提交门控。",
      "整合 MM-Vet、ScreenSpot、Video-MME、ALFRED 的小型可复现实例。",
      "回归捕获率、probe 压缩比、跨方法一致性。",
      "最小 probe 无法预测完整评测或不同更新类型不可统一。",
      ("SEA-Eval", "VISCO", "LensWalk"), ("MM-Vet", "ScreenSpot", "Video-MME", "ALFRED"), 1, 20, 7,
      "missing-cell", (5, 5, 5, 5, 5)),
    S("compositional-memory-contamination-bench", "Compositional Visual Memory Contamination", "组合式视觉记忆污染基准", "evaluation",
      "单条错误记忆可能无害，但多条看似一致的视觉经验组合后会形成强错误规则。",
      "构建单条、组合和休眠三类视觉记忆污染，测写入过滤、检索组合和激活阶段的盲点。",
      "从公开样本生成可控错误 exemplar/摘要→按组合规则注入→跨任务激活→记录传播。",
      "揭示仅做单条一致性检查无法发现的结构风险，适合 benchmark 贡献。",
      "通用 memory poisoning 不等于视觉证据组合；这里要求图像区域、视角和对象关系触发。",
      "在 VQA、GUI 与导航 memory agent 上做冻结评测。",
      "攻击成功、污染传播深度、检测率、正常效用。",
      "视觉组合触发与文本污染没有显著差异，缺少视觉专属发现。",
      ("AtlasVA", "HyMEM"), ("MM-Vet", "AndroidWorld", "R2R"), 1, 18, 5,
      "cross-domain-analogy", (5, 5, 5, 5, 5)),
    S("self-improvement-transfer-diagnostic", "Self-Improvement Transfer Diagnostic", "自改进迁移诊断", "evaluation",
      "同分布准确率提升无法区分真实视觉技能增长和对更新样本/评价器的记忆。",
      "将每次改进拆为同视觉因素新表面、同表面新关系、无关任务和反事实任务四种迁移。",
      "为更新样本生成受控配对→执行更新→测四象限增益→判定技能、记忆或捷径。",
      "比平均 OOD 测试更能解释究竟学到了哪个视觉变量。",
      "VisPlay 等报告多 benchmark 提升；本 Idea 提供更新级因果迁移诊断。",
      "在视觉属性、空间关系、GUI 操作和视频事件上构造配对。",
      "四象限 transfer profile、shortcut rate、更新收益。",
      "配对生成质量不足或 profile 不能预测真实跨数据集泛化。",
      ("VisPlay", "VISCO"), ("CV-Bench", "MMVP", "ScreenSpot", "NExT-QA"), 1, 24, 6,
      "metric-replacement", (5, 5, 5, 5, 5)),
    S("evolution-audit-log-dataset", "Visual Evolution Audit Logs", "视觉进化审计日志数据集", "evaluation",
      "论文只发布最终模型和汇总结果，缺少更新前证据、候选修改、拒绝原因与回滚记录。",
      "定义统一日志 schema，并从开源视觉 Agent 运行中发布可重放的更新决策轨迹。",
      "采集 observation/claim/update/reviewer/pilot/commit→匿名化→提供重放器与审计任务。",
      "把自进化过程变成可研究数据，支持后续异常检测、归因和 Reviewer 复核。",
      "现有 benchmark 多发布任务轨迹；本 Idea 发布持久更新的决策与证据链。",
      "选 3 类开源 Agent、每类 200–500 次更新事件即可形成首版。",
      "日志覆盖、可重放率、审计任务一致性。",
      "不同系统无法映射到统一 schema，或日志不含足够视觉证据。",
      ("ResearchAgent", "AI-Scientist-v2"), ("MM-Vet", "AndroidWorld", "Video-MME"), 1, 12, 7,
      "missing-cell", (4, 4, 5, 5, 5)),
    S("budgeted-visual-self-evolution-benchmark", "Budgeted Visual Self-Evolution", "预算约束视觉自进化基准", "evaluation",
      "现有自进化比较忽略不同方法使用的模型调用、生成样本、帧数和训练预算。",
      "在固定视觉调用、GPU 小时和持久存储预算下比较更新收益，报告完整 Pareto 前沿。",
      "统一成本记账→设置多档预算→运行 prompt/memory/tool/LoRA 更新→测收益、回归和成本。",
      "能揭示看似更强的方法是否只依赖更多计算，直接服务低资源研究。",
      "区别于普通效率表：预算是实验控制变量，且同时测长期更新收益和回归。",
      "选 2 个 7B VLM、4 个公开任务、4 类更新机制即可。",
      "单位 GPU 小时净增益、Pareto dominance、回归成本。",
      "成本口径无法跨机制公平统一，或排序对预算不敏感。",
      ("VisPlay", "LensWalk", "AtlasVA"), ("MM-Vet", "Video-MME", "ScreenSpot", "CV-Bench"), 2, 48, 10,
      "metric-replacement", (5, 5, 5, 5, 4)),
    S("negative-transfer-map", "Negative Transfer Map for VLM Evolution", "VLM 进化负迁移地图", "evaluation",
      "视觉自改进论文通常只展示平均正增益，无法知道更新在哪些视觉技能之间产生系统性干扰。",
      "构建更新源技能×目标技能矩阵，测每类经验/工具/LoRA 更新的正迁移与负迁移。",
      "定义技能轴→逐类进行小型更新→全矩阵评测→聚类干扰模式→验证可预测边界。",
      "形成直观地图，可直接指导更新顺序和模块隔离，而不是只报告单一 forgetting 数字。",
      "continual learning 有任务遗忘矩阵；本 Idea 针对视觉 Agent 的异构更新对象与技能轴。",
      "利用现有 VLM benchmark 子集和 LoRA/prompt/memory 三类轻量更新。",
      "负迁移矩阵、最坏技能下降、干扰可预测性。",
      "技能划分主观或结果退化为常规 continual-learning 结论。",
      ("VisPlay", "AtlasVA"), ("MM-Vet", "CV-Bench", "ChartQA", "ScreenSpot"), 2, 40, 8,
      "cross-domain-analogy", (5, 5, 5, 5, 4)),
    S("improvement-causality-checklist", "Visual Improvement Causality Suite", "视觉改进因果核验套件", "evaluation",
      "更新后性能提高可能来自更多推理轮数、额外视觉 token、数据泄漏或 evaluator 偏好，而不是提出的机制。",
      "为视觉自进化建立 matched-compute、matched-observation、shuffled-update 和 no-commit 四类强制对照。",
      "包装任意更新方法→自动生成四类 matched control→输出机制专属效应与置信区间。",
      "直接降低审稿中最常见的归因争议，且可作为开源评测工具。",
      "不是提出新自进化算法，而是建立能够推翻虚假机制主张的视觉实验协议。",
      "在 3–4 个现有开源方法上复现实验即可形成首版。",
      "机制专属增益、控制分离、复现一致性。",
      "控制后所有增益消失且无法形成新的领域发现，或覆盖方法太少。",
      ("VisPlay", "VISTA", "AtlasVA", "LensWalk"), ("MM-Vet", "Video-MME", "GenEval", "AndroidWorld"), 2, 36, 8,
      "objective-evaluation-mismatch", (5, 5, 5, 5, 4)),
)


REJECTED: tuple[dict[str, str], ...] = (
    {"title": "从头训练自进化 13B VLM", "reason": "资源需求远超低资源约束，且核心贡献容易退化为规模扩展。"},
    {"title": "在百万无标注图像上复现 VisPlay", "reason": "与已发表工作直接碰撞，训练成本高。"},
    {"title": "通用多 Agent 视觉辩论", "reason": "缺少视觉专属机制，调用成本高，已有工作密集。"},
    {"title": "更大的视觉 Critic", "reason": "仅换更大模型，无法识别机制贡献。"},
    {"title": "完整机器人硬件长期学习平台", "reason": "数据与硬件周期过长，不适合作为当前低资源 Pilot。"},
    {"title": "人工标注十万条视觉反思", "reason": "标注成本高，且不符合自进化问题设定。"},
    {"title": "自进化世界模型从头训练", "reason": "需要大规模视频与训练，主张过宽。"},
    {"title": "所有视觉工具统一强化学习", "reason": "动作空间与训练成本过大，难以归因。"},
    {"title": "通用视觉记忆图", "reason": "与 AtlasVA、HyMEM、EvoGraph-R1 等直接重叠，缺少新的可测变量。"},
    {"title": "仅增加更多 self-reflection 轮数", "reason": "属于计算扩展，不是新机制。"},
    {"title": "新建全尺寸视频自进化 benchmark", "reason": "数据采集与版权成本过高；应先用公开数据构建诊断子集。"},
    {"title": "使用闭源最强模型作为唯一 evaluator", "reason": "不可复现，且评价器偏差无法审计。"},
    {"title": "泛化的视觉 Agent 安全综述", "reason": "不是方法或 benchmark 贡献，难以形成 CVPR 主实验。"},
    {"title": "无实验的视觉自进化理论框架", "reason": "无法在 CVPR 中提供直接视觉证据。"},
    {"title": "只比较最终成功率的经验写入", "reason": "与现有口径相同，不能证明过程或机制贡献。"},
    {"title": "端到端训练全新视频 Agent", "reason": "资源高、开发周期长，已有强工作。"},
    {"title": "生成模型全参数在线自更新", "reason": "训练成本与安全风险高，难做有界 Pilot。"},
    {"title": "视觉 Agent 通用自动论文系统", "reason": "问题过宽，视觉贡献与单篇论文主张不清晰。"},
)


PROJECT_WEB_GPT_REVIEWS: dict[str, dict[str, Any]] = {
    "event-boundary-counterfactual": {
        "reviewer": "agent-project-web-gpt-strict-cvpr-area-chair",
        "verdict": "pass",
        "reviewed_at": "2026-07-30",
        "finding": "The strongest direct visual contribution among the reviewed top three, provided causal frames and irrelevant boundary frames are operationally distinguished.",
        "required_action": "Use annotated/validated causal event windows, irrelevant-context boundary changes, and causal-frame removal or replacement as matched controls.",
        "source_artifact": "/data/wyt/agent-self-evolution-observatory/runs/reviews/top3-cvpr-strict-review.md",
    },
    "reward-invariance-audit": {
        "reviewer": "agent-project-web-gpt-strict-cvpr-area-chair",
        "verdict": "revise",
        "reviewed_at": "2026-07-30",
        "finding": "Potentially useful, but generic transform sensitivity does not establish a reward shortcut because transformations may legitimately alter task evidence.",
        "required_action": "Use human/rule-validated semantics-preserving interventions, semantics-changing positive controls, and nuisance-correlated shortcut probes in matched triplets.",
        "source_artifact": "/data/wyt/agent-self-evolution-observatory/runs/reviews/top3-cvpr-strict-review.md",
    },
    "regression-tested-tool-evolution": {
        "reviewer": "agent-project-web-gpt-strict-cvpr-area-chair",
        "verdict": "block",
        "reviewed_at": "2026-07-30",
        "finding": "The central novelty is software/agent regression governance and transfers almost unchanged to non-visual systems; visual tools alone do not establish a CVPR-specific mechanism.",
        "required_action": "Do not advance as a primary CVPR idea unless a specifically visual failure theory and visual update mechanism are introduced.",
        "source_artifact": "/data/wyt/agent-self-evolution-observatory/runs/reviews/top3-cvpr-strict-review.md",
    },
}


REVIEWERS = (
    ("novelty", "新颖性与最近工作碰撞"),
    ("vision", "CVPR 视觉不可替代性"),
    ("validity", "科学成立性与机制可识别性"),
    ("evidence", "主表与决定性证据"),
    ("feasibility", "低资源可行性"),
)


def _review(seed: IdeaSeed) -> tuple[bool, list[dict[str, Any]], list[str]]:
    blocks: list[str] = []
    if seed.budget.max_gpus > 2:
        blocks.append("GPU 数超过 2。")
    if seed.budget.gpu_hours > 48:
        blocks.append("Pilot GPU 小时超过 48。")
    if not seed.datasets:
        blocks.append("没有公开数据集。")
    if not seed.nearest or not seed.collision.strip():
        blocks.append("缺少最近工作碰撞边界。")
    if min(seed.scores.values()) < 4:
        blocks.append("至少一个 Reviewer 维度低于 4/5。")
    external_review = PROJECT_WEB_GPT_REVIEWS.get(seed.id)
    if external_review and external_review["verdict"] == "block":
        blocks.append(f"项目内网页版 GPT 严格审查阻断：{external_review['finding']}")

    reviews = []
    for key, label in REVIEWERS:
        score = seed.scores[key]
        reviews.append(
            {
                "reviewer": key,
                "label": label,
                "score": score,
                "verdict": "pass" if score >= 4 else "block",
                "finding": {
                    "novelty": seed.collision,
                    "vision": TRACKS[seed.track]["importance"],
                    "validity": TRACKS[seed.track]["rationale"],
                    "evidence": f"决定性指标：{seed.metric}",
                    "feasibility": f"{seed.budget.max_gpus} GPU，约 {seed.budget.gpu_hours} GPU 小时，{seed.budget.wall_days} 天。",
                }[key],
            }
        )
    return not blocks, reviews, blocks


def _experiment_protocol(seed: IdeaSeed) -> dict[str, Any]:
    """Return an executable, low-resource protocol rather than a vague pilot.

    The main claim must be reproducible without a commercial API. A hosted
    frontier model may be added only as a pinned, separately reported ceiling
    or portability check.
    """

    primary_actor = {
        "observation": "Qwen2.5-VL-7B-Instruct (local, frozen)",
        "memory": "Qwen2.5-VL-7B-Instruct (local, frozen)",
        "critique": "Qwen2.5-VL-7B-Instruct actor (local, frozen)",
        "tools": "Qwen2.5-VL-7B-Instruct planner (local, frozen)",
        "video": "Qwen2.5-VL-7B-Instruct (local, frozen, bounded frame input)",
        "embodied": "OpenVLA-7B or OpenVLA-OFT actor (local, frozen)",
        "generation": "SDXL or FLUX.1-schnell generator (local, frozen)",
        "evaluation": "Qwen2.5-VL-7B-Instruct (local, frozen)",
    }[seed.track]
    cross_model = {
        "observation": "InternVL3-8B or LLaVA-OneVision-7B",
        "memory": "InternVL3-8B; OpenVLA-7B for embodied-memory cases",
        "critique": "InternVL3-8B or Molmo-7B as a heterogeneous critic",
        "tools": "InternVL3-8B as a second planner",
        "video": "InternVL3-8B or Video-LLaVA-7B",
        "embodied": "The other OpenVLA checkpoint plus Qwen2.5-VL-7B auditor",
        "generation": "The alternate local generator (SDXL versus FLUX.1-schnell)",
        "evaluation": "InternVL3-8B and the relevant OpenVLA checkpoint",
    }[seed.track]
    critic = {
        "observation": "InternVL3-8B local verifier; deterministic geometric/image tests where possible",
        "memory": "InternVL3-8B local verifier plus matched replay",
        "critique": "InternVL3-8B or Molmo-7B; never reuse the actor alone as the only critic",
        "tools": "Execution success, tool-specific tests, and InternVL3-8B for semantic checks",
        "video": "InternVL3-8B verifier with frame/segment evidence checks",
        "embodied": "Qwen2.5-VL-7B process auditor plus simulator state checks",
        "generation": "Qwen2.5-VL-7B local evaluator plus non-learned perceptual/identity metrics",
        "evaluation": "Independent open-weight judge and task-native executable metrics",
    }[seed.track]
    tools = {
        "observation": "OpenCV/PIL transforms, GroundingDINO or OWL-ViT, SAM2 when localization is needed",
        "memory": "FAISS or exact retrieval, immutable trajectory/image hashes, local metadata store",
        "critique": "OpenCV interventions, local VLM serving, task-native answer checker",
        "tools": "GroundingDINO/OWL-ViT, SAM2, PaddleOCR/Tesseract, Python execution sandbox",
        "video": "ffmpeg/PyAV frame extraction, local temporal sampler, task-native timestamp checker",
        "embodied": "LIBERO/CALVIN/RoboMimic simulator replay and logged robot states",
        "generation": "Diffusers, SDXL/FLUX.1-schnell, open inpainting/editing operators",
        "evaluation": "Local replay harness, checksum/version ledger, task-native scorer",
    }[seed.track]
    unit = {
        "observation": "image/question or video/question pair",
        "memory": "task episode or memory-write event",
        "critique": "reasoning answer with image evidence",
        "tools": "tool-using task episode",
        "video": "video/question episode",
        "embodied": "simulator trajectory",
        "generation": "prompt-generation or prompt-edit episode",
        "evaluation": "evolution episode/update event",
    }[seed.track]
    update_scope = {
        "observation": "Update only the observation policy, evidence ledger, threshold, or a <=50M-parameter calibrator; keep the VLM frozen.",
        "memory": "Update only memory contents, retrieval weights, applicability masks, or a <=50M-parameter gate; keep the actor frozen.",
        "critique": "Primary result uses a frozen heterogeneous critic. Optional LoRA/DPO critic training is a separate ablation, not required for the main claim.",
        "tools": "Update only tool descriptions, capability tests, routing scores, or a small router; freeze the planner and visual tools.",
        "video": "Update only sampling/revisit policy, temporal evidence state, or a small stopping calibrator; freeze the video VLM.",
        "embodied": "Freeze OpenVLA. Update only admission/retrieval/audit modules; no full policy retraining in Phase 0/1.",
        "generation": "Freeze generator and VLM evaluator. Update prompt/tool routing, edit state, or a small calibration layer only.",
        "evaluation": "No foundation-model training is required; construct diagnostics from frozen models, logs, and controlled updates.",
    }[seed.track]
    discovery_count = "100-200"
    calibration_count = "100-200"
    pilot_count = "500-1,000"
    if seed.track in {"embodied", "generation"}:
        pilot_count = "100-300"

    return {
        "execution_mode": "open-weight-primary; commercial API optional",
        "actor": primary_actor,
        "cross_model": cross_model,
        "critic_or_verifier": critic,
        "tool_models": tools,
        "commercial_api_role": bi(
            "非必需。最多选择一个固定版本的商业多模态模型，只用于上界、外部 Judge 或可迁移性测试；主表结论必须在无 API 设置成立。缓存请求，temperature=0，报告模型快照、调用数、token 与费用。",
            "Optional only. At most one pinned commercial multimodal model may be used as a ceiling, external judge, or portability test. The main-table claim must hold without it. Cache requests, use temperature 0, and report model snapshot, calls, tokens, and cost.",
        ),
        "parameter_updates": bi(update_scope),
        "data_protocol": {
            "unit": bi(unit),
            "discovery": bi(
                f"从官方训练划分抽取 {discovery_count} 个 {unit}，只用于确认现象、调试日志和冻结指标定义；不进入最终显著性检验。",
                f"Take {discovery_count} {unit}s from the official training split only for phenomenon confirmation, logging/debugging, and freezing metric definitions; exclude them from final significance tests.",
            ),
            "calibration": bi(
                f"使用与 discovery 不重叠的 {calibration_count} 个样本冻结阈值、停止规则和至多三组超参数；不得查看测试标签。",
                f"Use a disjoint {calibration_count}-sample set to freeze thresholds, stopping rules, and at most three hyperparameter settings; never inspect test labels.",
            ),
            "test": bi(
                f"使用官方测试集或至少 {pilot_count} 个完全隔离的 {unit}。测试期间禁止更新 Prompt、记忆、阈值、路由规则或选择样本。",
                f"Use the official test set or at least {pilot_count} fully held-out {unit}s. During testing, do not update prompts, memory, thresholds, routing rules, or sample selection.",
            ),
        },
        "phases": [
            {
                "id": "P0",
                "title": bi("现象确认", "Phenomenon confirmation"),
                "setup": bi(
                    "在两个开源模型和 100–200 个样本上，不训练任何模块，验证目标失败确实存在，并排除 parser、随机采样、分辨率和预算差异。",
                    "With two open models and 100-200 samples, train nothing; verify the target failure exists and rule out parser, random-sampling, resolution, and budget artifacts.",
                ),
                "gate": bi("若现象在两个模型上均不稳定，停止该 Idea。", "Stop if the phenomenon is unstable on both open models."),
            },
            {
                "id": "P1",
                "title": bi("机制 Pilot", "Mechanism pilot"),
                "setup": bi(
                    f"在主开源模型上运行最强直接 baseline、无更新、随机/等预算对照与本方法；三随机种子，预算不超过 {seed.budget.gpu_hours} GPU 小时。",
                    f"On the primary open model, compare the strongest direct baseline, no-update, random/equal-budget control, and the proposed method; use three seeds within {seed.budget.gpu_hours} GPU-hours.",
                ),
                "gate": bi(seed.stop, seed.stop),
            },
            {
                "id": "P2",
                "title": bi("跨模型与鲁棒性", "Cross-model and robustness"),
                "setup": bi(
                    "冻结 P1 的全部规则，在第二个开源架构、至少一种视觉扰动/场景迁移和可选商业模型上直接复用，不重新选阈值。",
                    "Freeze every P1 choice and transfer it to a second open architecture, at least one visual perturbation/domain shift, and the optional hosted model without retuning thresholds.",
                ),
                "gate": bi("若优势只出现在一个模型或一种预算下，将主张降级为模型特定诊断。", "If gains occur for only one model or one budget, downgrade the claim to a model-specific diagnostic."),
            },
        ],
        "controls": [
            bi("冻结系统／无更新", "Frozen system / no update"),
            bi("随机更新或等调用预算对照", "Random update or equal-call-budget control"),
            bi(TRACKS[seed.track]["baseline"]),
            bi("可执行 oracle 或使用真值证据的上界（仅用于解释差距）", "Executable oracle or ground-truth-evidence ceiling, used only to interpret headroom"),
        ],
        "repetitions": bi(
            "本地随机算法运行 3 个种子并报告逐种子结果；确定性 API 使用 temperature=0，若服务仍非确定，则在 10% 测试子集重复 3 次并报告方差。",
            "Run local stochastic methods with three seeds and report each seed. Use temperature 0 for APIs; if the service remains nondeterministic, repeat three times on 10% of the test set and report variance.",
        ),
        "call_budget": bi(
            "所有方法使用相同基础视觉调用预算；本方法额外观察/批评/工具调用最多为 baseline 的 3 次，并同时报告平均与 P95。可选商业 API 最多 300 次调用。",
            "Give all methods the same base visual-call budget. Extra observation/critique/tool calls are capped at three times the baseline and reported as mean and P95. Optional commercial API use is capped at 300 calls.",
        ),
        "compute_budget": bi(
            f"最多 {seed.budget.max_gpus} 张 RTX 3090，{seed.budget.gpu_hours} GPU 小时，预计 {seed.budget.wall_days} 天；模型、数据和缓存全部位于 /data。",
            f"At most {seed.budget.max_gpus} RTX 3090 GPU(s), {seed.budget.gpu_hours} GPU-hours, and {seed.budget.wall_days} days; models, data, and caches remain on /data.",
        ),
        "main_table": bi(
            f"行：无更新、随机等预算、最强直接 baseline、本方法、oracle。列：{seed.metric}、任务准确率/成功率、错误更新或负迁移、视觉调用数、GPU 小时、API 调用/费用。",
            f"Rows: no update, random equal-budget, strongest direct baseline, proposed method, oracle. Columns: {seed.metric}, task accuracy/success, harmful updates or negative transfer, visual calls, GPU-hours, and API calls/cost.",
        ),
        "ablations": [
            bi("移除核心机制，仅保留相同额外计算", "Remove the core mechanism while keeping the same extra compute"),
            bi("同模型 Critic 与异构 Critic", "Same-model critic versus heterogeneous critic"),
            bi("不更新持久状态，只做当前轮推理", "No persistent-state update; current-episode inference only"),
            bi("阈值、样本量和调用预算敏感性", "Sensitivity to threshold, sample count, and call budget"),
        ],
        "success_gate": bi(
            f"在主开源模型和第二开源架构上，{seed.metric} 均优于最强等预算 baseline；同时任务效用不显著下降，且 95% bootstrap CI 不跨越零。",
            f"On both the primary and second open architectures, {seed.metric} must beat the strongest equal-budget baseline without significant task-utility loss, and the 95% bootstrap CI must exclude zero.",
        ),
        "stop_gate": bi(seed.stop, seed.stop),
        "artifacts_to_log": [
            "model/checkpoint revision and serving configuration",
            "dataset manifest and immutable split IDs",
            "all prompts, memory/tool versions, thresholds, and random seeds",
            "per-example outputs, visual regions/frames, tool traces, and update decisions",
            "GPU wall time, peak memory, local calls, API calls/tokens/cost",
            "failed runs and every excluded sample with a reason",
        ],
    }


def _priority(seed: IdeaSeed) -> float:
    weighted = (
        1.25 * seed.scores["novelty"]
        + 1.25 * seed.scores["vision"]
        + 1.15 * seed.scores["validity"]
        + 1.10 * seed.scores["evidence"]
        + 1.00 * seed.scores["feasibility"]
    )
    resource_bonus = max(0.0, (48 - seed.budget.gpu_hours) / 48)
    return round(weighted + resource_bonus, 3)


def build_cvpr_idea_bank() -> dict[str, Any]:
    passed: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for seed in IDEAS:
        ok, reviews, blocks = _review(seed)
        track = TRACKS[seed.track]
        record = {
            "id": seed.id,
            "title": seed.title,
            "track_id": seed.track,
            "track": track["label"],
            "purpose": bi(seed.problem),
            "core_idea": bi(seed.core),
            "rationale": bi(track["rationale"]),
            "method_logic": bi(seed.method),
            "importance": bi(track["importance"]),
            "comparative_advantage": bi(seed.advantage),
            "collision_boundary": bi(seed.collision),
            "nearest_work": list(seed.nearest),
            "datasets": list(seed.datasets),
            "models": list(track["models"]),
            "strongest_baseline": bi(track["baseline"]),
            "pilot": bi(seed.pilot),
            "decisive_metric": bi(seed.metric),
            "stop_condition": bi(seed.stop),
            "budget": asdict(seed.budget),
            "experiment_protocol": _experiment_protocol(seed),
            "operator": seed.operator,
            "scores": seed.scores,
            "reviews": reviews,
            "external_reviews": [PROJECT_WEB_GPT_REVIEWS[seed.id]] if seed.id in PROJECT_WEB_GPT_REVIEWS else [],
            "priority": _priority(seed),
            "status": "pass" if ok else "block",
            "blocking_reasons": blocks,
        }
        (passed if ok else blocked).append(record)

    passed.sort(key=lambda item: (-item["priority"], item["budget"]["gpu_hours"], item["id"]))
    for rank, item in enumerate(passed, start=1):
        item["rank"] = rank
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "review_mode": "five-role-programmatic-gates-plus-agent-project-web-gpt",
        "policy": {
            "max_gpus": 2,
            "max_gpu_hours": 48,
            "minimum_reviewer_score": 4,
            "required_fields": ["purpose", "core_idea", "rationale", "method_logic", "importance", "comparative_advantage", "collision_boundary", "pilot", "stop_condition", "experiment_protocol"],
        },
        "summary": {
            "raw_candidates": len(IDEAS) + len(REJECTED),
            "structured_candidates": len(IDEAS),
            "passed": len(passed),
            "blocked_after_structured_review": len(blocked),
            "early_rejected": len(REJECTED),
            "tracks": len(TRACKS),
            "project_web_gpt_reviewed": len(PROJECT_WEB_GPT_REVIEWS),
        },
        "tracks": {key: value["label"] for key, value in TRACKS.items()},
        "passed_ideas": passed,
        "blocked_ideas": blocked,
        "early_rejected": list(REJECTED),
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
        if len(idea.get("reviews", [])) != 5 or any(review["verdict"] != "pass" for review in idea["reviews"]):
            errors.append(f"review gate failed: {idea['id']}")
        for field_name in payload["policy"]["required_fields"]:
            value = idea.get(field_name)
            if not value or (isinstance(value, dict) and "zh" in value and not value.get("zh")):
                errors.append(f"missing {field_name}: {idea['id']}")
        protocol = idea.get("experiment_protocol") or {}
        protocol_required = (
            "execution_mode", "actor", "cross_model", "critic_or_verifier",
            "tool_models", "commercial_api_role", "parameter_updates",
            "data_protocol", "phases", "controls", "repetitions",
            "call_budget", "compute_budget", "main_table", "ablations",
            "success_gate", "stop_gate", "artifacts_to_log",
        )
        for key in protocol_required:
            if not protocol.get(key):
                errors.append(f"missing experiment_protocol.{key}: {idea['id']}")
        if "open-weight-primary" not in str(protocol.get("execution_mode", "")):
            errors.append(f"commercial API became primary: {idea['id']}")
        if len(protocol.get("phases") or []) != 3:
            errors.append(f"experiment protocol must have P0/P1/P2: {idea['id']}")
    if len(payload.get("passed_ideas", [])) < 40:
        errors.append("fewer than 40 passed CVPR ideas")
    return errors


def write_cvpr_idea_bank(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    payload = build_cvpr_idea_bank()
    errors = validate_bank(payload)
    if errors:
        raise ValueError("Invalid CVPR idea bank:\n- " + "\n- ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text(
        "window.CVPR_LOW_RESOURCE_IDEAS = "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    return payload
