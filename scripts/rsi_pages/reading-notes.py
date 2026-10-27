"""Long-form, source-anchored RSI paper notes generated from reading-cards.json.

Only papers with an optional deep_read object appear here. Never hard-code a
paper-specific webpage: append another deep_read to the card registry instead.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "rsi" / "reading-cards.json"
PAPERS = json.loads(SOURCE.read_text(encoding="utf-8"))["papers"]
DEEP = [p for p in PAPERS if p.get("deep_read")]
TYPES = {"prose", "table", "steps", "formula", "callout", "evidence", "bullets", "tests"}
STAGES = [
    ("challenge", "Challenge", "难在哪里"),
    ("insight", "Insight", "为什么可解"),
    ("design", "Design", "具体怎么做"),
    ("result", "Result", "结果怎么样"),
    ("next", "Next", "哪些问题还没解决"),
]


def e(s: str) -> str:
    return html.escape(str(s), quote=True)


def render_block(b: dict) -> str:
    kind = b["type"]
    if kind == "prose":
        return f'<p class="deep-prose">{e(b["text"])}</p>'
    if kind == "bullets":
        return '<ul class="deep-bullets">' + ''.join(f'<li>{e(t)}</li>' for t in b["items"]) + '</ul>'
    if kind == "steps":
        return '<ol class="deep-steps">' + ''.join(
            f'<li><strong>{e(item["title"])}</strong><p>{e(item["text"])}</p></li>'
            for item in b["items"]
        ) + '</ol>'
    if kind == "formula":
        return (
            f'<div class="deep-formula"><b>{e(b["label"])}</b>'
            f'<code>{e(b["expression"])}</code>'
            f'<p><strong>怎么理解：</strong>{e(b["meaning"])}</p>'
            f'<p class="deep-caveat"><strong>边界：</strong>{e(b["boundary"])}</p></div>'
        )
    if kind == "table":
        assert b["headers"] and all(len(row) == len(b["headers"]) for row in b["rows"])
        caption = f'<caption>{e(b["caption"])}</caption>' if b.get("caption") else ""
        head = '<thead><tr>' + ''.join(f'<th scope="col">{e(h)}</th>' for h in b["headers"]) + '</tr></thead>'
        rows = '<tbody>' + ''.join(
            '<tr>' + ''.join(f'<td>{e(v)}</td>' for v in row) + '</tr>'
            for row in b["rows"]
        ) + '</tbody>'
        return f'<div class="deep-table" tabindex="0" role="region" aria-label="精读内容比较表"><table>{caption}{head}{rows}</table></div>'
    if kind == "callout":
        assert b["kind"] in {"paper", "boundary", "example", "insight", "proposal"}
        return (
            f'<aside class="deep-note deep-note--{e(b["kind"])}">'
            f'<b>{e(b["label"])}</b><p>{e(b["text"])}</p></aside>'
        )
    if kind == "evidence":
        return '<div class="deep-evidence-grid">' + ''.join(
            '<article class="deep-evidence">'
            f'<h4>{e(item["domain"])}</h4>'
            f'<p><b>评测设置：</b>{e(item["setup"])}</p>'
            f'<p><b>作者报告：</b>{e(item["result"])}</p>'
            f'<p><b>能够支持：</b>{e(item["supports"])}</p>'
            f'<p class="deep-caveat"><b>尚不能推断：</b>{e(item["not_proven"])}</p>'
            '</article>'
            for item in b["items"]
        ) + '</div>'
    if kind == "tests":
        return '<div class="deep-test-list">' + ''.join(
            f'<article class="deep-test"><h4>{e(item["name"])}</h4>'
            f'<p><b>实验设计：</b>{e(item["design"])}</p>'
            f'<p><b>决定性证据：</b>{e(item["decisive"])}</p></article>'
            for item in b["items"]
        ) + '</div>'
    raise ValueError(f"Unknown deep reading block type: {kind}")


def validate_deep(p: dict) -> None:
    d = p["deep_read"]
    assert d["focus"] and d["summary"] and d["sections"], f"Empty deep reading: {p['id']}"
    ids = [s["id"] for s in d["sections"]]
    assert len(ids) == len(set(ids)), f"Duplicate section anchor: {p['id']}"
    valid_stages = {stage for stage, _, _ in STAGES}
    for s in d["sections"]:
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", s["id"])
        assert s.get("stage") in valid_stages, f"Section lacks C-I-D-R stage: {p['id']} / {s['id']}"
        assert s["title"] and s["blocks"], f"Empty section: {p['id']} / {s['id']}"
        for b in s["blocks"]:
            assert b["type"] in TYPES, f"Bad content block: {p['id']} / {b.get('type')}"
    assert {key for key, _, _ in STAGES[:4]} <= {s["stage"] for s in d["sections"]}, (
        f"Challenge, Insight, Design, Result must all be supported: {p['id']}"
    )


def full_text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(full_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(full_text(item) for item in value.values())
    return ""


def render_paper(p: dict) -> str:
    validate_deep(p)
    d = p["deep_read"]
    base = f"deep-{p['id']}"
    stage_nav = "".join(
        f'<a href="#{e(base)}--stage-{stage}">{e(en)} · {e(zh)}</a>'
        for stage, en, zh in STAGES
        if any(s["stage"] == stage for s in d["sections"])
    )
    terms = "".join(
        f'<div><dt>{e(item["name"])}</dt><dd>{e(item["meaning"])}</dd></div>'
        for item in d.get("terms", [])
    )
    glossary = (
        '<div class="deep-glossary"><p class="deep-glossary-title">先记住三个角色</p>'
        f'<dl class="deep-terms">{terms}</dl></div>'
        if terms else ""
    )

    def chapter(s: dict) -> str:
        return (
            f'<details class="deep-chapter" id="{e(base)}--{e(s["id"])}">'
            f'<summary>{e(s["title"])}<span class="deep-chapter-hint">展开细节</span></summary>'
            '<div class="deep-chapter-body">'
            + "".join(render_block(b) for b in s["blocks"])
            + '</div></details>'
        )

    stage_parts = []
    for index, (stage, english, chinese) in enumerate(STAGES, start=1):
        chapters = [s for s in d["sections"] if s["stage"] == stage]
        if not chapters:
            continue
        chapters.sort(key=lambda s: s.get("order", 100))
        lead = p["story"].get(stage) if stage != "next" else (
            d.get("afterword") or "这些是尚未解决的科学问题，不应当写成原论文已经证明的结论。"
        )
        stage_parts.append(
            f'<section class="deep-stage" id="{e(base)}--stage-{stage}" data-story-stage="{e(stage)}">'
            f'<header class="deep-stage-head"><span>{index:02d} · {e(english)}</span><h4>{e(chinese)}</h4></header>'
            f'<p class="deep-stage-lead">{e(lead)}</p>'
            '<div class="deep-stage-details">'
            + "".join(chapter(s) for s in chapters)
            + '</div></section>'
        )
    links = "".join(
        f'<a class="link-btn" target="_blank" rel="noopener noreferrer" href="{e(p["links"][key])}">{label}</a>'
        for key, label in (("html", "arXiv 原文"), ("pdf", "PDF 原文"), ("code", "作者代码"))
        if p["links"].get(key)
    )
    return (
        f'<div class="deep-paper-head"><p class="deep-meta">{e(p["lead_institution"])} · '
        f'{e(p["publication"])} · arXiv:{e(p["arxiv"])} · {e(p["read_on"])} 精读</p>'
        f'<h3>{e(p["title"])}</h3>'
        f'<p class="deep-focus">{e(d["focus"])}</p>'
        '<p class="deep-author-note">先读四个大标题下的一句话；要看例子、公式或实验细节时再展开。'
        '这份笔记区分作者结果、教学举例和我们的研究想法，尚未独立复现。</p>'
        + glossary
        + f'<nav class="deep-shortcuts" aria-label="{e(p["short_title"])} 四步精读">{stage_nav}</nav>'
        + "".join(stage_parts)
        + '<div class="deep-back"><a href="reading-cards.html#'
        + e(p["id"]) + '">返回论文速览卡片</a></div>'
        + f'<div class="links deep-source-links">{links}</div></div>'
    )


for paper in DEEP:
    validate_deep(paper)

PAGE = {
    "slug": "reading-notes",
    "title": "论文完整精读",
    "en": "Deep reads · mechanisms, equations, evidence and research gaps",
    "lead": f"已整理 {len(DEEP)} 篇完整精读。先读 Challenge（困难）、Insight（关键想法）、Design（方法）、Result（结果），再按需展开公式和实验。",
    "updated": max((p["read_on"] for p in DEEP), default="2026-10-27"),
    "sections": [
        (f'deep-{p["id"]}', f'精读 · {p["short_title"]}', render_paper(p))
        for p in DEEP
    ],
    "search_records": [
        {
            "title": f'精读正文 · {p["short_title"]} · {section["title"]}',
            "url": f'reading-notes.html#deep-{p["id"]}--{section["id"]}',
            "text": full_text(section["blocks"]) + ' ' + p["title"] + ' ' + p["lead_institution"],
        }
        for p in DEEP
        for section in p["deep_read"]["sections"]
    ],
}
