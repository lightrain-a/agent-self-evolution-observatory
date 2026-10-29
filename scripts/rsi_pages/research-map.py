"""RSI learning-function map: a static, searchable view of the shared taxonomy."""
import csv
import json
from html import escape
from pathlib import Path
from rsi_framework import FUNCTIONS, IDEAS, BY_ID, FUNCTION_SLUGS, source_assignment
from rsi_taxonomy import FEATURED_SOURCE_IDS

def _e(value):
    return escape(str(value or ""), quote=True)

def _root():
    for candidate in [Path.cwd(), *Path(__file__).resolve().parents]:
        if (candidate / "rsi" / "sources.tsv").exists():
            return candidate
    raise FileNotFoundError("Cannot locate rsi/sources.tsv")

ROOT = _root()
with (ROOT / "rsi" / "sources.tsv").open(encoding="utf-8-sig", newline="") as stream:
    SOURCES = list(csv.DictReader(stream, delimiter="\t"))
READINGS = json.loads((ROOT / "rsi" / "reading-cards.json").read_text(encoding="utf-8-sig"))
FUNCS = list(FUNCTIONS.values()) if isinstance(FUNCTIONS, dict) else list(FUNCTIONS)
IDEA_ROWS = list(IDEAS.items()) if isinstance(IDEAS, dict) else [(x.get("id", ""), x) for x in IDEAS]
ALIASES = {"signals": "signal", "capabilities": "capability"}

def _same(a, b):
    return ALIASES.get(str(a), str(a)) == ALIASES.get(str(b), str(b))

def _slug(fid):
    default = {"experience": "experience", "signal": "signals", "capability": "capabilities", "regulation": "regulation"}
    return FUNCTION_SLUGS.get(fid, default.get(fid, fid))

def _assignment(row):
    for value in (row, row.get("id", "")):
        try:
            result = source_assignment(value)
            if isinstance(result, dict):
                return result.get("primary", result.get("function", ""))
            if isinstance(result, str):
                return result
            if isinstance(result, (tuple, list)) and result:
                return result[0]
        except (TypeError, KeyError, AttributeError):
            pass
    return ""

def _flatten(value):
    if isinstance(value, dict):
        return [item for child in value.values() for item in _flatten(child)]
    if isinstance(value, (list, tuple, set)):
        return [item for child in value for item in _flatten(child)]
    return [str(value)]

FEATURED = set(_flatten(FEATURED_SOURCE_IDS))

def _records(value):
    if isinstance(value, dict):
        if value.get("title"):
            yield value
        for child in value.values():
            yield from _records(child)
    elif isinstance(value, list):
        for child in value:
            yield from _records(child)

READING_ROWS = list(_records(READINGS))
READING_TITLES = {str(x.get("title", "")).casefold() for x in READING_ROWS}
ASSIGNED = {str(row.get("id", row.get("title", ""))): _assignment(row) for row in SOURCES}

def _papers(fid):
    rows = [s for s in SOURCES if _same(ASSIGNED[str(s.get("id", s.get("title", "")))], fid)]
    return sorted(rows, key=lambda s: (str(s.get("id", "")) not in FEATURED, str(s.get("title", "")).casefold() not in READING_TITLES, str(s.get("title", ""))))

def _ideas(fid):
    return [(iid, row) for iid, row in IDEA_ROWS if _same(row.get("primary", ""), fid)]

EVIDENCE = {
    "experience": ("经历提供了什么新信息？", "固定经验数量、交互预算与学习者状态，检验所选经历是否提高未见任务的真实学习收益。"),
    "signal": ("好反馈能否变成好学习？", "分开测量答案正确、反馈准确、学习者吸收，以及更新后的跨题净收益。"),
    "capability": ("经验以什么形式成为能力？", "比较完整系统、外部支持与参数更新的贡献，检验未见实例、规则组合与调用条件。"),
    "regulation": ("多轮更新能否相互支持？", "同时追踪新增收益、旧能力保持、未来学习曲线与全程成本；控制当前能力再比较后续学习。"),
}

def _paper_card(row):
    title, note = row.get("title", ""), row.get("note", "")
    meta = " · ".join(str(row.get(k, "")) for k in ("date", "level") if row.get(k))
    return f'<article class="rm-paper rm-searchable" data-search="{_e(title + " " + note + " " + meta)}"><a href="{_e(row.get("url", ""))}" target="_blank" rel="noopener noreferrer">{_e(title)}<span aria-hidden="true"> ↗</span></a><small>{_e(meta)}</small><p>{_e(note)}</p></article>'

def _idea_card(iid, row):
    tags = row.get("tags", [])
    if isinstance(tags, dict):
        tags = _flatten(tags)
    elif isinstance(tags, str):
        tags = [tags]
    title = row.get("title", "")
    return f'<a class="rm-idea rm-searchable" href="{_e(row.get("href", "ideas.html"))}" data-search="{_e(str(iid) + " " + title + " " + " ".join(map(str, tags)))}"><span class="rm-idea-id">{_e(iid)}</span><span><strong>{_e(title)}</strong><small>{_e(row.get("section", ""))}{" · " if tags else ""}{_e(" / ".join(map(str, tags)))}</small></span><span aria-hidden="true">→</span></a>'

def _group(function):
    fid = function["id"]
    papers, ideas = _papers(fid), _ideas(fid)
    title = function.get("title", fid)
    question = function.get("question", "")
    subsections = function.get("subsections", [])
    if isinstance(subsections, dict):
        subsections = list(subsections.items())
    labels = []
    for item in subsections:
        if isinstance(item, dict):
            label = " ".join(str(item.get(k, "")) for k in ("id", "title") if item.get(k))
        elif isinstance(item, (list, tuple)):
            label = " ".join(map(str, item))
        else:
            label = str(item)
        labels.append(f'<li>{_e(label)}</li>')
    proof_title, proof = EVIDENCE.get(ALIASES.get(fid, fid), ("主张需要什么证据？", "检查泛化、保持、未来可学习性与长期成本。"))
    paper_html = "".join(_paper_card(p) for p in papers[:6]) or '<p class="rm-muted">本组文献见参考文献页。</p>'
    idea_html = "".join(_idea_card(iid, row) for iid, row in ideas) or '<p class="rm-muted">该功能的开放问题见研究议程。</p>'
    return f'''<details class="rm-group" id="map-{_e(fid)}" data-function="{_e(fid)}" open>
      <summary><span class="rm-chapter">CH. {_e(function.get("chapter", ""))}</span><span class="rm-group-heading"><strong>{_e(title)}</strong><small>{_e(question)}</small></span><span class="rm-count">{len(papers)} 条来源 · {len(ideas)} 个 Idea</span><span class="rm-chevron" aria-hidden="true">⌄</span></summary>
      <div class="rm-group-content"><section class="rm-block rm-question"><h3>科学问题</h3><p>{_e(function.get("summary", question))}</p><ol>{"".join(labels)}</ol><a class="rm-text-link" href="{_e(_slug(fid))}.html">进入本章 →</a></section>
      <section class="rm-block rm-literature"><h3>代表文献 <span>按主要贡献归属</span></h3>{paper_html}<a class="rm-text-link" href="references.html?function={_e(fid)}">查看本组全部文献 →</a></section>
      <section class="rm-block rm-ideas"><h3>研究想法 <span>I 编号保持不变</span></h3>{idea_html}</section>
      <section class="rm-block rm-evidence"><h3>证据与缺口</h3><strong>{_e(proof_title)}</strong><p>{_e(proof)}</p><a class="rm-text-link" href="evidence.html">对照第 7 章证据框架 →</a></section></div>
    </details>'''

INDEX = "".join(f'<a class="rm-index-item" href="#map-{_e(f["id"])}" data-map-select="{_e(f["id"])}"><span class="rm-index-no">0{i+1}</span><span><strong>{_e(f.get("title", f["id"]))}</strong><small>{_e(f.get("question", ""))}</small></span><b>{len(_papers(f["id"]))}<small>条来源</small></b></a>' for i, f in enumerate(FUNCS))
OPTIONS = "".join(f'<option value="{_e(f["id"])}">{_e(f.get("title", f["id"]))}</option>' for f in FUNCS)
OVERVIEW = f'''<div class="rm-brief"><div><span class="rm-eyebrow">RSI · LEARNING MECHANISMS</span><p class="rm-central-question">经历怎样转化为能够迁移、能够保留，并支持后续学习的能力？</p><p>四项学习功能组织文献与研究想法。泛化贯穿各环节；记忆按保存、归因和修订等实际作用归位。</p></div><div class="rm-stats"><span><b>4</b>学习功能</span><span><b>{len(SOURCES)}</b>来源条目</span><span><b>{len(IDEA_ROWS)}</b>研究想法</span></div></div><nav class="rm-group-index" aria-label="四项学习功能">{INDEX}</nav><p class="rm-boundary"><strong>阅读方式</strong> 每篇工作有一个主要归属，其他功能通过关联链接连接；方法、载体、组织方式与评价结果作为独立描述字段。</p>'''
MAP = f'''<div class="rm-toolbar"><label class="rm-search-label">搜索地图<input id="rm-search" type="search" placeholder="论文、Idea、科学问题…" autocomplete="off"></label><label>学习功能<select id="rm-function"><option value="all">全部四项功能</option>{OPTIONS}</select></label><div class="rm-actions"><button type="button" id="rm-expand">全部展开</button><button type="button" id="rm-collapse">全部收起</button><button type="button" id="rm-reset">重置</button></div></div><p class="rm-result" id="rm-result" role="status" aria-live="polite">显示全部四项学习功能</p><div class="rm-groups">{"".join(_group(f) for f in FUNCS)}</div><div id="rm-empty" class="rm-empty" hidden><strong>没有找到匹配内容</strong><p>试试论文标题、I 编号，或切换到全部学习功能。</p><button type="button" data-map-reset>清除筛选</button></div>'''
OUTLINE = '''<div class="rm-outline"><a href="index.html"><b>01</b><span>引言<small>中心问题与研究动机</small></span></a><a href="foundations.html"><b>02</b><span>范围与基础<small>概念边界与统一框架</small></span></a><a href="#map-explore" data-map-reset><b>03–06</b><span>四项学习功能<small>唯一的主体分类</small></span></a><a href="evidence.html"><b>07</b><span>证据与评价<small>泛化、保持、未来可学习性</small></span></a><a href="agenda.html"><b>08</b><span>开放问题<small>跨环节的研究议程</small></span></a></div>'''

PAGE = {
    "slug": "research-map", "title": "RSI 研究地图", "en": "Learning Mechanisms for Recursive Self-Improvement",
    "lead": "从经验获取到能力积累：沿四项学习功能连接科学问题、文献、研究想法与证据。",
    "styles": ["research-map.css"], "scripts": ["research-map.js"],
    "sections": [("map-overview", "从经历到持续能力", OVERVIEW), ("map-explore", "探索研究地图", MAP), ("map-outline", "综述的八章结构", OUTLINE)],
}
