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
    for s in d["sections"]:
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", s["id"])
        assert s["title"] and s["blocks"], f"Empty section: {p['id']} / {s['id']}"
        for b in s["blocks"]:
            assert b["type"] in TYPES, f"Bad content block: {p['id']} / {b.get('type')}"


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
    shortcuts = "".join(
        f'<a href="#{e(base)}--{e(section["id"])}">{e(section["title"])}</a>'
        for section in d["sections"]
    )
    sections = "".join(
        f'<section class="deep-chapter" id="{e(base)}--{e(section["id"])}">'
        f'<h3>{e(section["title"])}</h3>'
        + "".join(render_block(block) for block in section["blocks"])
        + '</section>'
        for section in d["sections"]
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
        '<p class="deep-author-note">此页是本站研读记录。论文报告结果、教学示例、研究推断分开标注；未独立复现。</p>'
        '<div class="deep-summary"><h4>三句话记住</h4><ol>'
        + "".join(f'<li>{e(item)}</li>' for item in d["summary"])
        + '</ol></div>'
        f'<nav class="deep-shortcuts" aria-label="{e(p["short_title"])} 精读章节">{shortcuts}</nav>'
        + sections
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
    "lead": f"已整理 {len(DEEP)} 篇完整精读。先在卡片库建立印象，再按机制公式、受控实验、证据边界与下一步辨别实验深读。",
    "updated": max((p["read_on"] for p in DEEP), default="2026-10-27"),
    "sections": [
        ("how-to-read", "如何使用完整精读",
         '<p>这里是<strong>可长期复用的精读正文</strong>，与简短卡片分离。'
         '每一节依次讲“为什么需要、论文怎样做、哪些结果支持、留下什么缺口”。'
         '所有教学算例均与论文实验数字明确区分。'
         '每篇均能从卡片库直接跳到对应精读。</p>'
         '<div class="links"><a class="link-btn" href="reading-cards.html">回到论文卡片库</a></div>'),
    ] + [
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
