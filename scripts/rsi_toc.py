"""Reader-first RSI page outline: two levels only on genuinely long pages.

A page's public section IDs stay stable. Semantic bands are editorial metadata,
not another taxonomy or a source of duplicate headings in the article body.
"""
from __future__ import annotations

import html
import re

# (first existing section id in each group, short reader-facing group heading).
# Each preset covers the whole document in its original reading order.
TOC_GROUPS = {
    "generalization-learnability": [
        ("tradeoffs", "01 · 现象与问题"),
        ("mechanisms", "02 · 机制、文献与定位"),
        ("metrics", "03 · 测量与任务设计"),
        ("design-lessons", "04 · Method：诊断与干预"),
        ("p0", "05 · P0–P3：公共实验"),
        ("experiment-master", "06 · E0–E5：论文验证"),
    ],
    "reading-notes": [
        ("deep-scienceadv2020-expert-haptic-ceiling-hirano", "01 · 学习行为与记忆"),
        ("deep-memory-management-acl2026-xiong", "02 · 记忆与规则结构"),
        ("deep-nature2024-loss-plasticity-dohare", "03 · 塑性与持续更新"),
        ("deep-inventive-production-pf-2023-kapur", "04 · 教学与经验选择"),
        ("deep-rote-learning-iclr2026-wu", "05 · 规则学习与反馈"),
        ("deep-nature2025-centaur-binz", "06 · 认知模型与规划"),
    ],
    "learning-science": [
        ("framework-position", "01 · 学习科学框架"),
        ("systematic-generalization-mlc", "02 · 规则形成与迁移"),
        ("affective-feedback", "03 · 反馈、自评与纠错"),
        ("schema-reuse-2026", "04 · 图式、课程与探索"),
        ("mosaic-memory", "05 · 记忆与能力形成"),
        ("already", "06 · 迁移验证与局限"),
    ],
    "idea-i9-practice-switching": [
        ("question", "01 · 现象与已有研究"),
        ("challenge", "02 · 科学问题与方法"),
        ("nhb2026-history-state", "03 · 未来可学习性扩展"),
        ("orthogonal", "04 · 与其他 Idea 的边界"),
    ],
    "idea-prioritization": [
        ("decision", "01 · 排序原则与证据"),
        ("idea-1", "02 · I1–I5"),
        ("idea-6", "03 · I6–I10"),
        ("idea-11", "04 · I11–I14"),
        ("execution", "05 · 推进与再评估"),
    ],
    "experiments": [
        ("assets", "01 · 共用实验平台"),
        ("teaching-track", "02 · 教师与伙伴实验"),
        ("i9-practice", "03 · 学习顺序与规则"),
        ("i11-emotional-rsi", "04 · 反馈、先修与排期"),
    ],
    "theory-notes": [
        ("theory-index", "01 · 元学习理论"),
        ("memory-consolidation-fidelity", "02 · 记忆与重放"),
        ("single-edit-gradient-transfer", "03 · 梯度与信用分配"),
        ("dual-timescales", "04 · 元优化与时间尺度"),
    ],
    "i8": [
        ("question", "01 · 错误迁移的科学问题"),
        ("design", "02 · 方法与辨别实验"),
        ("rule-discrimination-npj2026", "03 · 机制与外部证据"),
        ("nonlocal-p0", "04 · 扩展实验与边界"),
    ],
    "idea-i2": [
        ("question", "01 · 师生共进化问题"),
        ("design", "02 · 教学方法与收益"),
        ("learner-response-question", "03 · 学习者响应预测"),
        ("dialogue-p0", "04 · 实验与判别"),
    ],
    "idea-i5": [
        ("scene", "01 · 为什么换伙伴"),
        ("design", "02 · 互教与动态换伴"),
        ("experiments", "03 · 实验和预算"),
        ("papers", "04 · 证据与论文定位"),
    ],
    "idea-i12-prerequisite-bottleneck": [
        ("question", "01 · 先修问题与证据"),
        ("insight", "02 · 先修机制与设计"),
        ("p0", "03 · P0–P2：因果实验"),
        ("metrics", "04 · 验收与边界"),
    ],
    "learning-admission": [
        ("question", "01 · 安全风险与相关工作"),
        ("design", "02 · 接纳方法"),
        ("p0", "03 · P0–P2：受控实验"),
        ("contract", "04 · 验收与论文边界"),
    ],
    "idea-i11-emotional-rsi": [
        ("question", "01 · 反馈效应与机制"),
        ("design", "02 · 设计与最近邻"),
        ("p0", "03 · P0–P2：递归效应"),
        ("metrics", "04 · 衡量与判断"),
    ],
    "idea-i10-learning-novelty": [
        ("question", "01 · 规则与表面新颖"),
        ("related", "02 · 最近邻研究"),
        ("insight", "03 · 方法与关键实验"),
    ],
    "experience-consolidation": [
        ("framework-position", "01 · 概念、证据与机制"),
        ("p0", "02 · P0–P2：巩固实验"),
        ("closest", "03 · 新颖性与决策"),
    ],
    "idea-i6-failure-value": [
        ("question", "01 · 失败为什么值得学"),
        ("stopping", "02 · 停止与重访实验"),
        ("related", "03 · 相关工作与决定"),
    ],
    "teaching": [
        ("position", "01 · 教学问题与反馈"),
        ("contracts", "02 · 教师更新机制"),
        ("algorithm", "03 · 算法与实验方案"),
        ("baselines", "04 · 基线与定位"),
    ],
}

TOC_LABELS = {
    "generalization-learnability": {
        "tradeoffs": "五个关键权衡",
        "tradeoff-solutions": "已有解决思路",
        "question": "同分为何学得不同？",
        "taxonomy": "五层学习指标",
        "states": "掌握 × 未来可学习性",
        "mechanisms": "机制与副作用",
        "history": "问题的发展脉络",
        "evidence": "已有精读证据",
        "new-papers": "最新直接近邻",
        "idea-map": "与 I1–I14 的关系",
        "framework-position": "综述中的位置",
        "metrics": "未来学习怎么测",
        "controls": "C 任务如何构造",
        "design-lessons": "顶刊方法学借鉴",
        "paper-method": "Method · RCP 总览",
        "method-rule-engine": "D1 · 竞争规则图",
        "method-signature": "D2 · 规则状态诊断",
        "method-intervention": "D3 · 针对性补救",
        "method-analysis": "D4 · 竞争机制鉴别",
        "p0": "P0 · 规则辨别",
        "p1": "P1 · 学习历史",
        "p2": "P2 · 前置知识",
        "p3": "P3 · 学习规则进化",
        "experiment-master": "E0–E5 · 实验矩阵",
        "experiment-resources": "模型、数据与资源",
        "experiment-statistics": "统计指标与主终点",
        "experiment-mentor": "师兄评议提纲",
        "figures": "拟图与 Go / Stop",
    },
}


def short_title(title: str) -> str:
    """Avoid unreadable wraparound in a 276px sidebar; retain full title in aria-label."""
    title = html.unescape(re.sub(r"<[^>]+>", "", title)).strip()
    if "｜" in title:
        prefix, suffix = title.split("｜", 1)
        if prefix.strip() in {"Observable Phenomenon", "Challenge", "Insight", "Design", "Why",
                              "Related Work", "Closest Related Work", "Mechanism", "Go / No-Go"}:
            title = prefix.strip() + " · " + suffix.strip()
    return title if len(title) <= 26 else title[:25].rstrip() + "…"


def _link(sid: str, title: str, compact: str | None = None) -> str:
    label = compact or short_title(title)
    return (f'<a class="toc-item" href="#{html.escape(sid, quote=True)}"'
            f' aria-label="{html.escape(title, quote=True)}"'
            f' title="{html.escape(title, quote=True)}">{html.escape(label)}</a>')


def render_page_toc(page: dict) -> str:
    slug = page["slug"]
    sections = page["sections"]
    preset = TOC_GROUPS.get(slug)
    if not preset:
        links = "".join(_link(sid, title) for sid, title, _ in sections)
        return ('<div class="page-toc"><div class="toc-title">本页目录</div>'
                '<nav class="toc-links toc-links--flat" aria-label="本页目录">'
                + links + "</nav></div>")
    starts = {sid: (index, title) for index, (sid, title) in enumerate(preset)}
    ids = [sid for sid, _, _ in sections]
    assert len(set(ids)) == len(ids), (slug, "Duplicate section ID")
    assert set(starts).issubset(ids), (slug, "Invalid outline group", set(starts)-set(ids))
    assert ids[0] == preset[0][0], (slug, "TOC group must start at first section")
    group_html = []
    current = []
    selected_group = None
    labels = TOC_LABELS.get(slug, {})

    def flush() -> None:
        if not current:
            return
        gi, title = selected_group
        first_id = preset[gi][0]
        is_first = gi == 0
        summary = (f'<summary class="toc-group-heading"><span>{html.escape(title)}</span>'
                   '<span class="toc-group-chevron" aria-hidden="true">⌄</span></summary>')
        group_html.append(
            f'<details class="toc-group" data-toc-group="{html.escape(first_id)}"'
            + (' open' if is_first else '') + '>' + summary
            + '<div class="toc-group-items">' + "".join(current) + '</div></details>'
        )
    for sid, title, _ in sections:
        if sid in starts:
            flush()
            current = []
            selected_group = starts[sid]
        current.append(_link(sid, title, labels.get(sid)))
    flush()
    assert len(group_html) == len(preset), (slug, "TOC groups not rendered")
    return ('<div class="page-toc page-toc--grouped">'
            '<div class="toc-title">本页目录 <span class="toc-count">'
            + str(len(sections)) + " 小节</span></div>"
            '<nav class="toc-links toc-links--grouped" aria-label="本页章节导航">'
            + "".join(group_html) + "</nav></div>")
