"""Data-driven RSI paper-reading cards with comparable five-question coverage.

New papers change only rsi/reading-cards.json. The same taxonomy, institution
fields, evidence limits, filters, and search-index records apply to every card.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "rsi" / "reading-cards.json"
DATA = json.loads(SOURCE.read_text(encoding="utf-8"))
PAPERS = DATA["papers"]
QUESTIONS = DATA["research_questions"]
LEVELS = {"core": "重点研究", "partial": "部分涉及", "not_addressed": "未直接研究"}
assert DATA["schema_version"] == 2
assert [q["id"] for q in QUESTIONS] == ["signal", "novelty", "reach", "retention", "safety"]
assert len({p["id"] for p in PAPERS}) == len(PAPERS), "Duplicate paper ID"


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def make_list(items, kind="ul") -> str:
    return f"<{kind}>" + "".join(f"<li>{esc(item)}</li>" for item in items) + f"</{kind}>"


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
        "id", "short_title", "title", "authors", "arxiv", "first_posted",
        "version", "read_on", "reading_level", "tags", "one_sentence",
        "problem", "setup", "key_ideas", "evidence", "boundaries",
        "our_relevance", "next_test", "links", "lead_institution",
        "institutions", "institution_source", "publication", "research_coverage",
    )
    assert all(k in p for k in required), f"Incomplete reading card: {p.get('id')}"
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", p["id"])
    assert re.fullmatch(r"\d{4}\.\d{4,5}", p["arxiv"])
    assert p["links"]["html"].startswith(f"https://arxiv.org/html/{p['arxiv']}")
    assert all(url.startswith("https://") for url in p["links"].values())
    assert p["lead_institution"] in p["institutions"], f"Leading institution missing: {p['id']}"
    assert len(set(p["institutions"])) == len(p["institutions"])
    assert set(p["research_coverage"]) == {q["id"] for q in QUESTIONS}, f"Missing research axis: {p['id']}"
    assert p["key_ideas"] and p["evidence"] and p["tags"]
    for entry in p["research_coverage"].values():
        assert entry["level"] in LEVELS
        assert entry["contribution"].strip() and entry["open_question"].strip()


def reading_card(p: dict) -> str:
    validate(p)
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
    coverage = "|".join(f'{q["id"]}:{p["research_coverage"][q["id"]]["level"]}' for q in QUESTIONS)
    others = len(p["institutions"]) - 1
    organization_line = esc(p["lead_institution"]) + (f' <span>等 {len(p["institutions"])} 家署名机构</span>' if others else "")
    all_institutions = " · ".join(p["institutions"])
    return f'''<article class="reading-card" id="{esc(p['id'])}" data-paper-tags="{esc('|'.join(p['tags']))}" data-question-coverage="{esc(coverage)}">
  <div class="reading-card-head">
    <div class="reading-metadata"><span class="reading-paper-id">{esc(p['short_title'])}</span><span>arXiv:{esc(p['arxiv'])}</span><span>精读 {esc(p['read_on'])}</span></div>
    <h3>{esc(p['short_title'])}</h3>
    <p class="reading-full-title">{esc(p['title'])}</p>
    <p class="reading-institution"><b>发表单位（作者署名）</b> {organization_line}</p>
    <div class="reading-tags">{tags}</div>
  </div>
  <div class="reading-issues"><p class="reading-issues-title">它研究了自我改进的哪些问题？</p><div class="reading-issue-tags">{issue_badges(p)}</div></div>
  <p class="reading-one-sentence">{esc(p['one_sentence'])}</p>
  <dl class="reading-overview">
    <div><dt>它解决什么问题</dt><dd>{esc(p['problem'])}</dd></div>
    <div><dt>它怎么做</dt><dd>{esc(p['setup'])}</dd></div>
    {f'<div><dt>到底更新了什么</dt><dd>{esc(p["updates"])}</dd></div>' if p.get("updates") else ""}
    <div><dt>和我们有什么关系</dt><dd>{esc(p['our_relevance'][0])}</dd></div>
  </dl>
  <details class="reading-expand">
    <summary>展开五问判断、机制、实验证据与局限</summary>
    <div class="reading-expanded-content">
      <div class="reading-source-line"><b>作者</b> {esc(p['authors'])} · <b>首发</b> {esc(p['first_posted'])} · <b>版本</b> {esc(p['version'])} · <b>阅读范围</b> {esc(p['reading_level'])}</div>
      <p class="reading-institutions-full"><b>全部作者单位：</b>{esc(all_institutions)}<br><b>发表状态：</b>{esc(p['publication'])} · <b>核对位置：</b>{esc(p['institution_source'])}</p>
      <h4>自我改进五问 · 论文做到哪里、还缺什么</h4>
      <p class="reading-taxonomy-caveat">“重点研究”表示直接针对该问题提出机制或证据，不代表问题已被彻底解决。分类属于本站的文献研读判断。</p>
      {issue_details(p)}
      <h4>核心机制 · 记住这几个公式</h4><ol class="reading-mechanisms">{mechanisms}</ol>
      <h4>实验证据（作者报告，未复现）</h4>{make_list(p['evidence'])}
      <h4>限制与易错理解</h4>{make_list(p['boundaries'])}
      <h4>对我们 RSI / I5 的启发</h4>{make_list(p['our_relevance'])}
      <div class="reading-next"><b>下一步最值得做的辨别实验</b><p>{esc(p['next_test'])}</p></div>
    </div>
  </details>
  <div class="links reading-links"><a class="link-btn" href="#{esc(p['id'])}" aria-label="复制或保存此卡片的锚点链接">卡片定位</a>{external_links}</div>
</article>'''


cards = "\n".join(reading_card(p) for p in PAPERS)
updated = max([p["read_on"] for p in PAPERS], default=DATA["updated"])
question_guide = "".join(
    f'<div class="reading-question-guide"><b>{esc(q["label"])}</b><p>{esc(q["definition"])}</p></div>'
    for q in QUESTIONS
)
question_options = "".join(
    f'<option value="{esc(q["id"])}">{esc(q["label"])}</option>'
    for q in QUESTIONS
)
PAGE = {
    "slug": "reading-cards",
    "title": "论文精读卡片",
    "en": "Paper reading cards · remember the mechanism, not the abstract",
    "lead": f"目前收录 {len(PAPERS)} 篇精读论文。统一记录作者单位，并按“信号 / 新信息 / 可采样性 / 内化保留 / 安全”五问标注研究覆盖和仍未解决的问题。",
    "updated": updated,
    "sections": [
        ("guide", "自我改进系统必须回答的四问，外加安全",
         '<p>这五个问题是本站对自我改进研究的<strong>统一比较坐标</strong>，并非作者声称已经全部解决。每篇论文分别标注“重点研究 / 部分涉及 / 未直接研究”，展开后对照<strong>论文做到了什么</strong>与<strong>仍未解决什么</strong>。论文作者单位严格按署名，不能与会议发表状态混为一谈。</p>'
         f'<div class="reading-guide-grid">{question_guide}</div>'
         '<p class="reading-legend"><strong>标注口径：</strong><span class="reading-level reading-level--core">重点研究</span>直接提出机制或证据；<span class="reading-level reading-level--partial">部分涉及</span>只覆盖该问题的一部分；<span class="reading-level reading-level--not_addressed">未直接研究</span>缺乏专门机制或实验。以上表示研究覆盖程度，不表示已经彻底解决。</p>'),
        ("library", f"论文卡片库 · {len(PAPERS)} 篇",
         '<div class="reading-tools"><label for="reading-card-filter">搜索卡片</label>'
         '<input type="search" id="reading-card-filter" placeholder="论文、单位、方法或机制…" autocomplete="off">'
         '<label for="reading-question-filter">对应问题</label>'
         f'<select id="reading-question-filter"><option value="all">全部问题</option>{question_options}</select>'
         '<label for="reading-coverage-filter">涉及程度</label>'
         '<select id="reading-coverage-filter"><option value="addressed">重点或部分涉及</option><option value="core">重点研究</option><option value="partial">部分涉及</option><option value="not_addressed">未直接研究</option><option value="all">全部程度</option></select>'
         '<span id="reading-card-count" aria-live="polite"></span></div>'
         f'<div class="reading-grid">{cards}</div>'
         '<p class="reading-empty" id="reading-empty" hidden>没有匹配的论文；可更换问题、涉及程度或清空搜索。</p>'
         '<div class="links"><a class="link-btn" href="reading-cards.json" download>下载阅读卡片 JSON（可复用）</a></div>'),
        ("protocol", "下一篇论文如何进入卡片库",
         '<p>在 <code>rsi/reading-cards.json</code> 的 <code>papers</code> 数组中追加新条目：包含作者单位、发表状态、原文链接、阅读日期与版本、核心机制及实验证据，并为 <strong>research_coverage</strong> 中的五问逐项填写 <code>level</code>、<code>contribution</code> 和 <code>open_question</code>。运行 <code>python3 scripts/build_rsi_research.py</code> 即可刷新网页、左侧目录和搜索索引。</p>'
         '<p>把作者实际验证的内容与本站的研究判断明确分开；不能用“相关”替代“解决”，也不能把阅读结论写成已经独立复现的结果。</p>'),
    ],
    "search_records": [
        {
            "title": f"精读卡片 · {p['short_title']}: {p['title']}",
            "url": f"reading-cards.html#{p['id']}",
            "text": " ".join(
                [p["one_sentence"], p["problem"], p["setup"], p.get("updates", ""),
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
