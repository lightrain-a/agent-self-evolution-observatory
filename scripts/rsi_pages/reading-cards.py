"""Data-driven RSI paper-reading cards.

Append a reviewed entry to rsi/reading-cards.json and rebuild; this renderer,
navigation, and search index automatically include each new paper.
"""
from __future__ import annotations
import html
import json
import re
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "rsi" / "reading-cards.json"
DATA = json.loads(SOURCE.read_text(encoding="utf-8"))
PAPERS = DATA["papers"]
assert DATA["schema_version"] == 1
assert len({p["id"] for p in PAPERS}) == len(PAPERS), "Duplicate paper ID"


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def make_list(items, kind="ul") -> str:
    return f"<{kind}>" + "".join(f"<li>{esc(item)}</li>" for item in items) + f"</{kind}>"


def reading_card(p: dict) -> str:
    required = (
        "id", "short_title", "title", "authors", "arxiv", "first_posted",
        "version", "read_on", "reading_level", "tags", "one_sentence",
        "problem", "setup", "key_ideas", "evidence", "boundaries",
        "our_relevance", "next_test", "links",
    )
    assert all(k in p for k in required), f"Incomplete reading card: {p.get('id')}"
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", p["id"])
    assert re.fullmatch(r"\d{4}\.\d{4,5}", p["arxiv"])
    assert p["links"]["html"].startswith(f"https://arxiv.org/html/{p['arxiv']}")
    assert all(url.startswith("https://") for url in p["links"].values())
    tags = "".join(f'<span class="reading-tag">{esc(tag)}</span>' for tag in p["tags"])
    mechanisms = "".join(
        f'<li><b>{esc(m["name"])}</b><p>{esc(m["summary"])}</p>'
        f'<code class="reading-formula">{esc(m["formula"])}</code></li>'
        for m in p["key_ideas"]
    )
    external_links = "".join(
        f'<a class="link-btn" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{label}</a>'
        for key, label in (("html", "论文 HTML"), ("pdf", "PDF"), ("code", "GitHub 代码"))
        if (url := p["links"].get(key))
    )
    return f'''<article class="reading-card" id="{esc(p['id'])}" data-paper-tags="{esc('|'.join(p['tags']))}">
  <div class="reading-card-head">
    <div class="reading-metadata"><span class="reading-paper-id">{esc(p['short_title'])}</span><span>arXiv:{esc(p['arxiv'])}</span><span>精读 {esc(p['read_on'])}</span></div>
    <h3>{esc(p['short_title'])}</h3>
    <p class="reading-full-title">{esc(p['title'])}</p>
    <div class="reading-tags">{tags}</div>
  </div>
  <p class="reading-one-sentence">{esc(p['one_sentence'])}</p>
  <dl class="reading-overview">
    <div><dt>它解决什么问题</dt><dd>{esc(p['problem'])}</dd></div>
    <div><dt>它怎么做</dt><dd>{esc(p['setup'])}</dd></div>
    {f'<div><dt>到底更新了什么</dt><dd>{esc(p["updates"])}</dd></div>' if p.get("updates") else ""}
    <div><dt>和我们有什么关系</dt><dd>{esc(p['our_relevance'][0])}</dd></div>
  </dl>
  <details class="reading-expand">
    <summary>展开公式、实验证据与可迁移机制</summary>
    <div class="reading-expanded-content">
      <div class="reading-source-line"><b>作者</b> {esc(p['authors'])} · <b>首发</b> {esc(p['first_posted'])} · <b>版本</b> {esc(p['version'])} · <b>阅读范围</b> {esc(p['reading_level'])}</div>
      <h4>核心机制 · 记住这几个公式</h4><ol class="reading-mechanisms">{mechanisms}</ol>
      <h4>实验证据（作者报告，未复现）</h4>{make_list(p['evidence'])}
      <h4>限制与易错理解</h4>{make_list(p['boundaries'])}
      <h4>对我们 RSI / I5 的启发</h4>{make_list(p['our_relevance'])}
      <div class="reading-next"><b>下一步最值得做的辨别实验</b><p>{esc(p['next_test'])}</p></div>
    </div>
  </details>
  <div class="links reading-links"><a class="link-btn" href="#{esc(p['id'])}" aria-label="复制或保存此卡片的锚点链接">卡片定位</a>{external_links}</div>
</article>'''


for p in PAPERS:
    assert p["key_ideas"] and p["evidence"] and p["tags"], f"Empty card content: {p['id']}"
cards = "\n".join(reading_card(p) for p in PAPERS)
updated = max([p["read_on"] for p in PAPERS], default=DATA["updated"])
PAGE = {
    "slug": "reading-cards",
    "title": "论文精读卡片",
    "en": "Paper reading cards · remember the mechanism, not the abstract",
    "lead": f"目前收录 {len(PAPERS)} 篇精读论文。每张卡片只留下研究问题、核心机制、关键证据、局限与对 RSI 的可迁移启发；支持继续追加论文。",
    "updated": updated,
    "sections": [
        ("guide", "阅读卡片：看完论文以后应该记住什么",
         '<p>这是长期积累的<strong>论文阅读卡库</strong>，和覆盖面广的文献综述分开。每篇用一句话抓住核心问题，再看机制、关键公式、证据和可以迁移的实验；“作者报告”不代表我们已经复现。</p>'
         '<div class="status-strip"><span>精读记录与后续设想分开</span><span>优先保留机制而不是堆摘要</span><span>有新论文直接追加结构化记录</span></div>'),
        ("library", f"论文卡片库 · {len(PAPERS)} 篇",
         '<div class="reading-tools"><label for="reading-card-filter">搜索卡片（标题、方法、机制、标签）</label>'
         '<input type="search" id="reading-card-filter" placeholder="例如：R²Orch、撤回、Curriculum、I5" autocomplete="off">'
         '<span id="reading-card-count" aria-live="polite"></span></div>'
         f'<div class="reading-grid">{cards}</div>'
         '<p class="reading-empty" id="reading-empty" hidden>没有匹配的论文；清空搜索可以查看全部。</p>'
         '<div class="links"><a class="link-btn" href="reading-cards.json" download>下载阅读卡片 JSON（可复用）</a></div>'),
        ("protocol", "下一篇论文如何进入卡片库",
         '<p>在 <code>rsi/reading-cards.json</code> 的 <code>papers</code> 数组中追加新条目，保持唯一的 <code>id</code>、原文链接、阅读版本与日期，并分别填写<strong>问题—机制—证据—局限—我们的启发</strong>。运行 <code>python3 scripts/build_rsi_research.py</code> 即可刷新卡片页、左侧目录和站内搜索索引。</p>'
         '<p>避免把阅读后的研究想法写成原论文已证实的结论；对照实验、随机化假设与复现状态必须可追溯。</p>'),
    ],
    "search_records": [
        {
            "title": f"精读卡片 · {p['short_title']}: {p['title']}",
            "url": f"reading-cards.html#{p['id']}",
            "text": " ".join(
                [p["one_sentence"], p["problem"], p["setup"], p.get("updates", "")]
                + p["tags"]
                + [m["name"] + " " + m["summary"] for m in p["key_ideas"]]
                + p["evidence"] + p["boundaries"] + p["our_relevance"]
            )
        }
        for p in PAPERS
    ],
}
