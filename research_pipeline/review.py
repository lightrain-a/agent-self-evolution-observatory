from __future__ import annotations

from typing import Any

from .models import BilingualText, ReviewRecord, ScoreDimension, text


REVIEWER_ROLES: tuple[dict[str, Any], ...] = (
    {
        "key": "novelty",
        "name": text("Novelty and collision reviewer", "新颖性与碰撞审查"),
        "question": text("Is the problem–mechanism combination already present in the nearest papers?", "最近邻论文是否已经包含相同的问题—机制组合？"),
        "blocking_evidence": text("Four-way search: same problem, same mechanism, same combination, and same experiment.", "四路检索：相同问题、相同机制、相同组合、相同实验。"),
    },
    {
        "key": "scientific-validity",
        "name": text("Scientific validity reviewer", "科学成立性审查"),
        "question": text("Is there an identifiable observation–failure–mechanism–prediction chain?", "是否存在可识别的观察—失败—机制—预测链？"),
        "blocking_evidence": text("A counterexample or alternative explanation that breaks the causal chain.", "能够打断因果链的反例或替代解释。"),
    },
    {
        "key": "experiment",
        "name": text("Experiment and main-table reviewer", "实验与主表审查"),
        "question": text("Can one normal-setting experiment directly prove the paper's main claim?", "是否有一个正常设置实验能直接证明论文核心主张？"),
        "blocking_evidence": text("Strongest baseline, matched budget, decisive metric, and explicit Go/Stop rule.", "最强基线、匹配预算、决定性指标和明确 Go／Stop。"),
    },
    {
        "key": "feasibility",
        "name": text("Feasibility reviewer", "可行性审查"),
        "question": text("Can the key phenomenon be tested before building the full method?", "能否在完整开发方法前先验证关键现象？"),
        "blocking_evidence": text("Available data, code, model, cost estimate, and a bounded pilot.", "可获得的数据、代码、模型、成本估计和有界 Pilot。"),
    },
    {
        "key": "venue-fit",
        "name": text("CVPR contribution reviewer", "CVPR 贡献审查"),
        "question": text("Is visual information indispensable to the claim rather than a replaceable test domain?", "视觉信息是否是核心主张不可替代的一部分，而非可替换测试领域？"),
        "blocking_evidence": text("A visual-specific failure, mechanism, or evaluation that text-only settings cannot establish.", "文本场景无法建立的视觉特定失败、机制或评测。"),
    },
)


def reviewer_specs() -> list[dict[str, Any]]:
    return list(REVIEWER_ROLES)


def _is_visual(track: BilingualText, direction_id: str) -> bool:
    haystack = f"{track.get('en', '')} {track.get('zh', '')} {direction_id}".lower()
    return any(token in haystack for token in ("visual", "cvpr", "multimodal", "embodied", "视觉", "具身"))


def build_scorecard(*, confidence: str, legacy_rank: int, track: BilingualText, direction_id: str, evidence_count: int) -> list[ScoreDimension]:
    visual = _is_visual(track, direction_id)
    importance = "strong" if legacy_rank <= 12 else "medium" if legacy_rank <= 24 else "weak"
    feasibility = "strong" if confidence == "H" else "medium" if confidence == "M" else "weak"
    evidence = "strong" if evidence_count >= 3 else "medium" if evidence_count else "unknown"
    return [
        ScoreDimension("importance", text("Problem importance", "问题重要性"), importance, text("Priority reflects the size of the failure and its effect on trustworthy persistent learning.", "优先级取决于失败规模及其对可信持久学习的影响。")),
        ScoreDimension("novelty", text("Verified novelty", "已核验新颖性"), "unknown", text("Direction-level neighbors are available, but exact problem–mechanism collision search must be rerun for this formulation.", "已有方向级近邻论文，但仍需针对该具体问题—机制组合重新做碰撞检索。")),
        ScoreDimension("mechanism", text("Mechanism clarity", "机制清晰度"), "strong", text("The candidate states a distinct mechanism and an explicit method flow rather than only a topic.", "候选方案给出了独立机制和明确方法流程，而不只是一个主题。")),
        ScoreDimension("visual", text("Visual necessity", "视觉不可替代性"), "strong" if visual else "weak", text("Strong only when visual evidence, interaction, grounding, view, or state is necessary to the main claim.", "只有当视觉证据、交互、Grounding、视角或状态对核心主张不可替代时才为强。")),
        ScoreDimension("falsifiability", text("Falsifiability", "可证伪性"), "strong", text("Every retained idea has a strongest comparison and explicit Go/Stop result.", "每个保留 Idea 都具有最强对照和明确 Go／Stop 结果。")),
        ScoreDimension("feasibility", text("Pilot feasibility", "Pilot 可行性"), feasibility, text("Confidence estimates whether the phenomenon can be isolated with current models, environments, and bounded compute.", "置信度估计能否使用现有模型、环境和有界算力隔离关键现象。")),
        ScoreDimension("evidence", text("Evidence readiness", "证据完备度"), evidence, text("Counts direct direction-level anchors; idea-level nearest-work differences remain a separate gate.", "统计方向级直接证据；Idea 级最近邻差异仍是独立门槛。")),
    ]


def build_reviews(*, confidence: str, legacy_rank: int, track: BilingualText, direction_id: str, evidence_count: int, selected: bool) -> list[ReviewRecord]:
    visual = _is_visual(track, direction_id)
    return [
        ReviewRecord(
            "novelty",
            "revise",
            text("Does a nearest paper already contain the same problem and mechanism?", "最近邻论文是否已经包含相同问题和机制？"),
            text("The direction has literature anchors, but idea-level four-way collision evidence is not yet frozen.", "该方向已有文献锚点，但 Idea 级四路碰撞证据尚未冻结。"),
            text("Retrieve and compare the nearest papers for problem, mechanism, combination, and experiment before claiming novelty.", "在声称新颖性前，分别检索并比较相同问题、机制、组合和实验的最近论文。"),
        ),
        ReviewRecord(
            "scientific-validity",
            "pass" if confidence in {"H", "M"} else "revise",
            text("Is the proposed mechanism tied to an identifiable failure?", "所提机制是否对应可识别的失败？"),
            text("The candidate provides a problem, rationale, method logic, and a result that could falsify it.", "候选方案给出了问题、合理性、方法逻辑和能够推翻它的结果。"),
            text("During the pilot, test a simpler alternative explanation before adding the complete method.", "Pilot 中应先检验更简单的替代解释，再开发完整方法。"),
        ),
        ReviewRecord(
            "experiment",
            "pass" if legacy_rank <= 20 else "revise",
            text("Can the main result be read from one normal-setting table?", "核心结果能否从一张正常设置主表中直接读出？"),
            text("A minimum experiment, strongest comparison, and Go/Stop boundary are already specified.", "已经指定最小实验、最强对照和 Go／Stop 边界。"),
            text("Freeze the primary metric and main-table columns before implementation.", "实现前冻结主指标与主表列。"),
        ),
        ReviewRecord(
            "feasibility",
            "pass" if confidence == "H" or selected else "revise",
            text("Can the decisive phenomenon be tested with current assets?", "决定性现象能否使用现有资产验证？"),
            text("High-confidence ideas have a bounded setup; medium and low confidence still need an asset and cost audit.", "高置信度 Idea 已具有有界设置；中低置信度仍需资产与成本核查。"),
            text("List exact models, environments, sample count, seeds, expected GPU hours, and failure recovery plan.", "列出确切模型、环境、样本数、随机种子、预计 GPU 小时和失败恢复方案。"),
        ),
        ReviewRecord(
            "venue-fit",
            "pass" if visual else "revise",
            text("Would the contribution remain unchanged if images were replaced by text?", "如果把图像替换为文本，贡献是否基本不变？"),
            text("The visual gate passes only for ideas whose failure or mechanism depends on grounded visual evidence or interaction.", "只有当失败或机制依赖视觉 Grounding 证据或交互时，视觉门槛才通过。"),
            text("For a CVPR target, make the visual-specific variable central to the main claim and main table.", "若目标为 CVPR，应让视觉特定变量成为核心主张和主表中心。"),
        ),
    ]


def classify(*, name: str, confidence: str, legacy_rank: int, track: BilingualText, direction_id: str) -> tuple[str, str]:
    if name == "GroundEvo-Admission":
        return "selected", "advance"
    visual = _is_visual(track, direction_id)
    if visual and confidence == "H" and legacy_rank <= 12:
        return "collision-check", "investigate"
    if confidence in {"H", "M"} and legacy_rank <= 20:
        return "review", "investigate"
    if confidence == "L":
        return "archived", "hold"
    return "review", "hold"
