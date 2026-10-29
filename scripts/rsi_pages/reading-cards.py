"""Data-driven RSI paper-reading cards with the shared four-function taxonomy.

New papers change only rsi/reading-cards.json. The same taxonomy, institution
fields, evidence limits, filters, and search-index records apply to every card.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from rsi_framework import FUNCTIONS, BY_ID, paper_assignment, function_badges

SOURCE = Path(__file__).resolve().parents[2] / "rsi" / "reading-cards.json"
DATA = json.loads(SOURCE.read_text(encoding="utf-8"))
PAPERS = DATA["papers"]
RELATED_DATA = json.loads((SOURCE.parent / "related-work.json").read_text(encoding="utf-8"))
RELATED_IDS = {r["paper_id"] for r in RELATED_DATA["targets"]}
QUESTIONS = DATA["research_questions"]
LEVELS = {"core": "重点研究", "partial": "部分涉及", "not_addressed": "未直接研究"}
STORY_STAGES = [
    ("challenge", "Challenge", "难在哪里"),
    ("insight", "Insight", "为什么可解"),
    ("design", "Design", "具体怎么做"),
    ("result", "Result", "结果怎么样"),
]
assert DATA["schema_version"] == 3
assert [q["id"] for q in QUESTIONS] == ["signal", "novelty", "reach", "retention", "safety"]
assert len({p["id"] for p in PAPERS}) == len(PAPERS), "Duplicate paper ID"


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def make_list(items, kind="ul") -> str:
    return f"<{kind}>" + "".join(f"<li>{esc(item)}</li>" for item in items) + f"</{kind}>"


def story_view(p: dict) -> str:
    rows = "".join(
        f'<div class="reading-story-step" data-story-stage="{key}">'
        f'<h4><span>{english}</span>{chinese}</h4><p>{esc(p["story"][key])}</p>'
        '</div>'
        for key, english, chinese in STORY_STAGES
    )
    return f'<div class="reading-story" aria-label="Challenge Insight Design Result 四步读懂">{rows}</div>'


def issue_badges(p: dict) -> str:
    return "".join(
        f'<span class="reading-issue reading-issue--{esc(p["research_coverage"][q["id"]]["level"])}" '
        f'title="{esc(q["definition"])}">{esc(q["label"])}'
        f'<small>{LEVELS[p["research_coverage"][q["id"]]["level"]]}</small></span>'
        for q in QUESTIONS
    )


def issue_details(p: dict) -> str:
    lines = []
    for q in QUESTIONS:
        record = p["research_coverage"][q["id"]]
        level = LEVELS[record["level"]]
        lines.append(
            f'<div class="reading-question-detail">'
            f'<dt><span>{esc(q["label"])}</span><span class="reading-level reading-level--{esc(record["level"])}">{level}</span></dt>'
            f'<dd><p><b>论文做到：</b>{esc(record["contribution"])}</p>'
            f'<p><b>仍未解决：</b>{esc(record["open_question"])}</p></dd>'
            f'</div>'
        )
    return '<dl class="reading-question-details">' + "".join(lines) + '</dl>'


def validate(p: dict) -> None:
    required = (
        "id", "short_title", "title", "authors", "first_posted",
        "version", "read_on", "reading_level", "tags", "one_sentence",
        "problem", "setup", "key_ideas", "evidence", "boundaries",
        "our_relevance", "next_test", "links", "lead_institution",
        "institutions", "institution_source", "publication", "research_coverage", "story",
    )
    assert all(k in p for k in required), f"Incomplete reading card: {p.get('id')}"
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", p["id"])
    arxiv = p.get("arxiv")
    doi = p.get("doi")
    assert bool(arxiv) != bool(doi), f"Specify one primary identifier (arXiv or DOI): {p['id']}"
    if arxiv:
        assert re.fullmatch(r"\d{4}\.\d{4,5}", arxiv), p["id"]
        if p.get("conference_official_primary"):
            assert p["publication"].startswith("ICLR 2026") and p["links"]["html"] == p["official_url"], p["id"]
            assert p["official_url"].startswith("https://proceedings.iclr.cc/paper_files/paper/2026/"), p["id"]
        else:
            assert p["links"]["html"].startswith(f"https://arxiv.org/html/{arxiv}"), p["id"]
    else:
        assert re.fullmatch(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", doi), p["id"]
        assert p["links"]["html"] == p["official_url"], f"Published journal URL mismatch: {p['id']}"
    assert p["links"]["html"].startswith("https://")
    assert all(url.startswith("https://") for url in p["links"].values())
    assert p["lead_institution"] in p["institutions"], f"Leading institution missing: {p['id']}"
    assert len(set(p["institutions"])) == len(p["institutions"])
    assert set(p["research_coverage"]) == {q["id"] for q in QUESTIONS}, f"Missing research axis: {p['id']}"
    assert p["key_ideas"] and p["evidence"] and p["tags"]
    assert set(p["story"]) == {k for k, _, _ in STORY_STAGES}, f"Incomplete C-I-D-R: {p['id']}"
    assert len(p["one_sentence"]) <= 100, f"Opening sentence too long: {p['id']}"
    for stage, _, _ in STORY_STAGES:
        sentence = p["story"][stage]
        assert sentence.strip() and len(sentence) <= 130, f"Make {stage} more readable: {p['id']}"
    for entry in p["research_coverage"].values():
        assert entry["level"] in LEVELS
        assert entry["contribution"].strip() and entry["open_question"].strip()


def reading_card(p: dict) -> str:
    validate(p)
    classification = paper_assignment(p)
    tags = "".join(f'<span class="reading-tag">{esc(tag)}</span>' for tag in p["tags"])
    mechanisms = "".join(
        f'<li><b>{esc(m["name"])}</b><p>{esc(m["summary"])}</p>'
        f'<code class="reading-formula">{esc(m["formula"])}</code></li>'
        for m in p["key_ideas"]
    )
    external_links = "".join(
        f'<a class="link-btn" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{label}</a>'
        for key, label in (("html", "论文原文"), ("pdf", "PDF"), ("code", "代码"), ("data", "公开数据"), ("adapter", "模型适配器"), ("full_text", "开放全文"))
        if (url := p["links"].get(key))
    )
    coverage = "|".join(f'{q["id"]}:{p["research_coverage"][q["id"]]["level"]}' for q in QUESTIONS)
    others = len(p["institutions"]) - 1
    organization_line = esc(p["lead_institution"]) + (f' <span>等 {len(p["institutions"])} 家署名机构</span>' if others else "")
    all_institutions = " · ".join(p["institutions"])
    publication_badge = (p['publication'].split('·')[0].strip() if p.get('conference_official_primary')
        else 'arXiv:'+p['arxiv'] if p.get('arxiv') else p['publication'].split('·')[0].strip())
    return f'''<article class="reading-card" id="{esc(p['id'])}" data-paper-tags="{esc('|'.join(p['tags']))}" data-question-coverage="{esc(coverage)}" data-primary-function="{esc(classification['primary'] or 'support')}" data-related-functions="{esc('|'.join(classification['related']))}">
  <div class="reading-card-head">
    <div class="reading-metadata"><span class="reading-paper-id">{esc(p['short_title'])}</span><span>{esc(publication_badge)}</span><span>阅读 {esc(p['read_on'])}</span>{'<span class="reading-deep-available">含完整精读</span>' if p.get("deep_read") else ""}<a class="reading-timeline-link" href="timeline.html#reading-{esc(p['id'])}" title="返回时间轴中的该次论文精读记录">在研究时间轴中查看 ↗</a></div>
    <h3>{esc(p['short_title'])}</h3>
    <p class="reading-full-title">{esc(p['title'])}</p>
    <p class="reading-institution"><b>发表单位（作者署名）</b> {organization_line}</p>
    <div class="reading-tags">{tags}</div>
  </div>
  <p class="reading-one-sentence">{esc(p['one_sentence'])}</p>
  {story_view(p)}
  {function_badges(classification["primary"], classification["related"])}<p class="reading-classification-note">{esc(classification.get("reason",""))}</p>
  <details class="reading-expand">
    <summary>继续看：真实证据、公式和没解决的问题</summary>
    <div class="reading-expanded-content">
      <div class="reading-source-line"><b>作者</b> {esc(p['authors'])} · <b>首发</b> {esc(p['first_posted'])} · <b>版本</b> {esc(p['version'])} · <b>阅读范围</b> {esc(p['reading_level'])}</div>
      <p class="reading-institutions-full"><b>全部作者单位：</b>{esc(all_institutions)}<br><b>发表状态：</b>{esc(p['publication'])} · <b>核对位置：</b>{esc(p['institution_source'])}</p>
      <h4>更新的是哪一部分？</h4><p>{esc(p.get("updates", p["setup"]))}</p>
      <h4>补充诊断维度：信号、信息、探索、保持与安全</h4>
      <p class="reading-taxonomy-caveat">“重点研究”表示直接针对该问题提出机制或证据，不代表问题已被彻底解决。这些维度补充机制与证据记录；主要功能分类以卡片上方的归属为准。</p>
      {issue_details(p)}
      <h4>核心机制 · 记住这几个公式</h4><ol class="reading-mechanisms">{mechanisms}</ol>
      <h4>实验证据（作者报告，未复现）</h4>{make_list(p['evidence'])}
      <h4>限制与易错理解</h4>{make_list(p['boundaries'])}
      <h4>对我们的 RSI 研究有什么启发？</h4>{make_list(p['our_relevance'])}
      <div class="reading-next"><b>下一步最值得做的辨别实验</b><p>{esc(p['next_test'])}</p></div>
    </div>
  </details>
  <div class="links reading-links">{f'<a class="link-btn reading-deep-link" href="reading-notes.html#deep-{esc(p["id"])}">完整精读 · 公式与实验</a>' if p.get("deep_read") else ""}{f'<a class="link-btn reading-related-link" href="reading-notes.html#deep-{esc(p["id"])}--stage-related">Related Work · 与前人的区别</a>' if p["id"] in RELATED_IDS else ""}<a class="link-btn" href="#{esc(p['id'])}" aria-label="复制或保存此卡片的锚点链接">卡片定位</a>{external_links}</div>
</article>'''


# Papers with a completed long-form read appear first; the registry ID remains stable.
DISPLAY_PAPERS = sorted(PAPERS, key=lambda p: (bool(p.get("deep_read")), p["read_on"]), reverse=True)
cards = "\n".join(reading_card(p) for p in DISPLAY_PAPERS)
updated = max([p["read_on"] for p in PAPERS], default=DATA["updated"])
question_guide = "".join(
    f'<div class="reading-question-guide"><b>{esc(q["label"])}</b><p>{esc(q["definition"])}</p></div>'
    for q in QUESTIONS
)
question_options = "".join(
    f'<option value="{esc(q["id"])}">{esc(q["label"])}</option>'
    for q in QUESTIONS
)
function_options = "".join(f'<option value="{f["id"]}">{esc(f["title"])}</option>' for f in FUNCTIONS)
function_guide = "".join(f'<div class="reading-question-guide"><b>第{f["chapter"]}章 · {esc(f["title"])}</b><p>{esc(f["question"])}</p></div>' for f in FUNCTIONS)
PAGE = {
    "slug": "reading-cards",
    "title": "论文精读卡片",
    "en": "Paper reading cards · remember the mechanism, not the abstract",
    "lead": f"目前收录 {len(PAPERS)} 篇。按经验获取、学习信号、能力形成、学习调控检索；每篇保留 Challenge、Insight、Design、Result 和完整精读。",
    "updated": updated,
    "sections": [
        ("library", f"论文卡片库 · {len(PAPERS)} 篇",
         '<div class="reading-tools"><label for="reading-card-filter">搜索卡片</label>'
         '<input type="search" id="reading-card-filter" placeholder="论文、单位、方法或机制…" autocomplete="off">'
         '<label for="reading-function-filter">学习功能</label>'
         f'<select id="reading-function-filter"><option value="all">全部功能</option>{function_options}</select>'
         '<label for="reading-relation-filter">归属关系</label>'
         '<select id="reading-relation-filter"><option value="primary">主要归属</option><option value="related">关联功能</option><option value="all">主要或关联</option></select>'
         '<span id="reading-card-count" aria-live="polite"></span></div>'
         f'<div class="reading-grid">{cards}</div>'
         '<p class="reading-empty" id="reading-empty" hidden>没有匹配的论文；可更换功能、归属关系或清空搜索。</p>'
         '<div class="links"><a class="link-btn" href="reading-cards.json" download>下载阅读卡片 JSON（可复用）</a></div>'),
        ("guide", "如何按学习功能阅读？",
         '<p>每篇论文按主要科学贡献确定一个主归属，其他作用用关联功能表示。方法、载体、组织方式和结果作为独立描述字段。</p>'
         f'<div class="reading-guide-grid">{function_guide}</div>'
         '<p>泛化贯穿四项功能，在第7章集中检验证据；记忆按归因、保存、修订和效果检验归位。</p>'
         '<details class="framework-fold"><summary>已有诊断记录：信号、信息、探索、保持与安全</summary>'
         f'<div class="reading-guide-grid">{question_guide}</div>'
         '<p>这些维度用于细读证据，不构成另一套主体分类。</p></details>'),
    ],
    "search_records": [
        {
            "title": f"精读卡片 · {p['short_title']}: {p['title']}",
            "url": f"reading-cards.html#{p['id']}",
            "primary_function": paper_assignment(p)["primary"],
            "text": " ".join(
                [BY_ID.get(paper_assignment(p)["primary"],{}).get("title",""), p["one_sentence"], *[p["story"][key] for key, _, _ in STORY_STAGES],
                 p["problem"], p["setup"], p.get("updates", ""),
                 p["lead_institution"], p["publication"], *p["institutions"]]
                + p["tags"]
                + [f'{q["label"]} {LEVELS[p["research_coverage"][q["id"]]["level"]]} '
                   f'{p["research_coverage"][q["id"]]["contribution"]} '
                   f'{p["research_coverage"][q["id"]]["open_question"]}' for q in QUESTIONS]
                + [m["name"] + " " + m["summary"] for m in p["key_ideas"]]
                + p["evidence"] + p["boundaries"] + p["our_relevance"]
            )
        }
        for p in PAPERS
    ],
}
