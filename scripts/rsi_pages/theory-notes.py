"""Reusable, source-audited RSI theory notebook.

New mechanisms are added to rsi/theory-notes.json. Every theory has a stable,
linkable anchor and a backlink to a source paper's detailed reading chapter.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from rsi_framework import paper_assignment, function_badges

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "rsi" / "theory-notes.json"
PAPER_REGISTRY = ROOT / "rsi" / "reading-cards.json"
THEORY = json.loads(REGISTRY.read_text(encoding="utf-8"))
PAPERS = {p["id"]: p for p in json.loads(PAPER_REGISTRY.read_text(encoding="utf-8"))["papers"]}
LABELS = THEORY["status_legend"]
ENTRIES = THEORY["entries"]


def e(value) -> str:
    return html.escape(str(value), quote=True)


def link_to_deep(entry: dict) -> str:
    return "reading-notes.html#deep-" + entry["source_paper_id"] + "--" + entry["source_anchor"]


def validate() -> None:
    assert THEORY["schema_version"] == 1 and ENTRIES, "Bad theory registry"
    assert len({item["id"] for item in ENTRIES}) == len(ENTRIES), "Duplicate theory IDs"
    assert set(LABELS) == {"paper-mechanism", "teaching-derivation", "rsi-hypothesis"}
    for entry in ENTRIES:
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", entry["id"]), entry["id"]
        assert entry["status"] in LABELS, entry["id"]
        assert all(entry[k] for k in ("title", "question", "insight", "source_locator", "category", "when_to_use", "caution"))
        assert entry["source_paper_id"] in PAPERS, entry["id"]
        paper = PAPERS[entry["source_paper_id"]]
        assert entry["source_anchor"] in {s["id"] for s in paper["deep_read"]["sections"]}, entry["id"]
        assert entry["equations"] and entry["derivation"], entry["id"]
        for eq in entry["equations"]:
            assert all(eq[k] for k in ("name", "expression", "latex", "meaning", "boundary")), entry["id"]
        for step in entry["derivation"]:
            assert all(step[k] for k in ("label", "text")), entry["id"]
        for source in entry.get("additional_sources", []):
            assert source.get("title") and source.get("role") and source.get("url", "").startswith("https://"), entry["id"]


validate()

index = '<p><b>如何使用：</b>每个主题拥有永久链接，可以在其他 Idea、论文和实验方案中直接引用。下方按机制查看公式、推导、适用条件与作者证据边界；新理论只需追加到 <code>theory-notes.json</code>。</p>'
index += '<div class="theory-legend">' + ''.join(
    '<span>' + e(LABELS[k]) + '</span>' for k in LABELS
) + '</div>'
index += '<div class="route-grid theory-directory">' + ''.join(
    '<a href="#' + e(item["id"]) + '"><b>' + e(item["title"]) + '</b><span>' +
    e(item["category"]) + ' · ' + e(item["question"]) + '</span></a>'
    for item in ENTRIES
) + '</div>'
index += '<p class="note"><b>当前主题：</b>DiscoRL的目标生成与元梯度、Hattori 2023的OFC快慢Meta-RL及分阶段干预、Science 2021/2024的非局部信用与记忆标记、ACL 2026的经验跟随和反事实效用、2026年Faulty Memory的抽象保真性。作者机制、本站教学推导及未验证的RSI巩固策略始终分层标注；详见<a href="learning-rule-evolution.html">I14 · 学习规则自进化</a>和<a href="experience-consolidation.html">经验到长期能力候选</a>。</p>'


def render(entry: dict) -> str:
    paper = PAPERS[entry["source_paper_id"]]
    formulas = ''.join(
        '<div class="deep-formula theory-formula"><b>' + e(eq["name"]) + '</b>' +
        '<code>' + e(eq["expression"]) + '</code>' +
        '<p><strong>逐项解释：</strong>' + e(eq["meaning"]) + '</p>' +
        '<p class="deep-caveat"><strong>边界：</strong>' + e(eq["boundary"]) + '</p>' +
        '<details class="theory-latex"><summary>LaTeX 源码（用于论文与笔记引用）</summary><pre><code>' +
        e(eq["latex"]) + '</code></pre></details></div>'
        for eq in entry["equations"]
    )
    steps = '<ol class="research-steps">' + ''.join(
        '<li><b>' + e(step["label"]) + '</b>：' + e(step["text"]) + '</li>'
        for step in entry["derivation"]
    ) + '</ol>'
    cite = ('<div class="links theory-references">'
        '<a class="link-btn" href="' + e(link_to_deep(entry)) + '">返回原论文精读的对应章节</a>'
        '<a class="link-btn" href="reading-cards.html#' + e(entry["source_paper_id"]) + '">论文速览卡片</a>'
        '<a class="link-btn" href="' + e(paper.get("official_url") or paper["links"]["html"]) +
        '" target="_blank" rel="noopener noreferrer">正式论文原文</a></div>')
    extra_sources = '<div class="links theory-references">' + ''.join(
        '<a class="link-btn" target="_blank" rel="noopener noreferrer" href="' +
        e(src["url"]) + '">' + e(src["role"]) + ' · ' + e(src["title"]) + '</a>'
        for src in entry.get("additional_sources", [])
    ) + '</div>' if entry.get("additional_sources") else ''
    return "".join([
        function_badges(paper_assignment(paper)["primary"],paper_assignment(paper)["related"]),
        '<div class="theory-meta"><span>' + e(LABELS[entry["status"]]) + '</span><span>' +
        e(entry["category"]) + '</span></div>',
        '<p class="theory-question"><b>研究问题：</b>' + e(entry["question"]) + '</p>',
        '<p><strong>机制主张：</strong>' + e(entry["insight"]) + '</p>',
        '<h3>关键公式与含义</h3>' + formulas,
        '<h3>推导顺序 / 机制解释</h3>' + steps,
        '<div class="deep-note"><b>后续何时回来看</b><p>' + e(entry["when_to_use"]) + '</p></div>',
        '<div class="deep-note deep-note--boundary"><b>不可越界解释</b><p>' + e(entry["caution"]) + '</p></div>',
        '<p class="theory-source">出处与证据位置：' + e(paper["title"]) + ' · ' + e(entry["source_locator"]) + '</p>',
        cite,
        extra_sources
    ])


PAGE = {
    "slug": "theory-notes",
    "title": "理论工具箱：学习规则、信用分配与元梯度",
    "en": "Reusable Theory Notes · Learning Rules, Nonlocal Credit Assignment and Meta-Gradients",
    "lead": "以后讨论 RSI 的学习规则、半梯度、元梯度与长期可学习性，可直接引用每条固定锚点。论文原机制、教学推导、待验证的机器研究假设严格区分。",
    "updated": THEORY["updated"],
    "styles": ["theory-notes.css"],
    "sections": [("theory-index", "理论目录 · 后续论文可直接引用", index)] + [
        (entry["id"], entry["title"], render(entry)) for entry in ENTRIES
    ],
}
