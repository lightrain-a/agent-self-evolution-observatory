"""Compact, source-anchored RSI research timeline.

Presentation follows the Agent Observatory's proven hierarchy:
briefing strip -> folding conference details -> paired month calendars ->
collapsible month/day/event histories. Source ownership remains independent.
"""
from __future__ import annotations

import html
import json
import re
from collections import Counter
from datetime import date, datetime
from itertools import groupby
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = json.loads((ROOT / "rsi" / "timeline-data.json").read_text(encoding="utf-8"))
PAPERS = json.loads((ROOT / "rsi" / "reading-cards.json").read_text(encoding="utf-8"))["papers"]
assert DATA["schema_version"] == "1.0"
date.fromisoformat(DATA["verified_at"])
KIND_LABELS = {"deadline": "会议 DDL", "reading": "论文精读", "research": "研究记录"}
KIND_ORDER = {"research": 0, "reading": 1, "deadline": 2}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def safe_url(value: str) -> str:
    if not value or not (value.startswith("https://") or re.fullmatch(
        r"[a-z0-9-]+\.html(?:#[a-z0-9-]+)?", value
    )):
        raise ValueError("Timeline source must be HTTPS or a same-site HTML page: " + value)
    return esc(value)


def check_date(value: str) -> None:
    date.fromisoformat(value)


def month_label(value: str) -> str:
    year, month = value.split("-")
    return f"{year} 年 {int(month)} 月"


def bar(rows: list[dict]) -> str:
    counts = Counter(row["kind"] for row in rows)
    total = max(1, len(rows))
    return ('<span class="rsi-rt-workload" aria-hidden="true">'
            + "".join(f'<i class="rsi-rt-workload--{kind}" style="width:{counts[kind]/total*100:.2f}%"></i>'
                      for kind in KIND_LABELS if counts[kind])
            + "</span>")


def event_card(event: dict) -> str:
    kind = event["kind"]
    due = event.get("due_at") or ""
    tags = event.get("tags", [])
    attrs = ' target="_blank" rel="noopener noreferrer"' if event["source_url"].startswith("https://") else ""
    tag_buttons = "".join(
        f'<button type="button" class="rsi-tl-tag" data-filter-tag="{esc(tag)}" title="筛选 {esc(tag)}">{esc(tag)}</button>'
        for tag in tags[:4]
    )
    if len(tags) > 4:
        tag_buttons += f'<span class="rsi-tl-tag-more">+{len(tags)-4}</span>'
    summary_tags = ''.join(f'<span>{esc(tag)}</span>' for tag in tags[:3])
    publication = (f'<span class="rsi-tl-publication">{esc(event["publication"].split("·")[0].strip())}</span>'
                   if kind == "reading" else "")
    preview = ""
    if kind == "reading":
        story = event["story"]
        parts = "".join(
            f'<div><dt>{label}</dt><dd>{esc(story[key])}</dd></div>'
            for key, label in (("challenge", "问题"), ("insight", "洞察"),
                               ("design", "方法"), ("result", "作者结果"))
        )
        preview = (f'<details class="rsi-tl-paper-preview"><summary>展开论文机制 · Challenge / Insight / Design / Result</summary>'
                   f'<dl>{parts}</dl></details>')
    return f'''<details class="rsi-tl-item rt-event rsi-tl-item--{kind}" id="{esc(event["id"])}"
      data-kind="{kind}" data-date="{esc(event["date"])}" data-due-at="{esc(due)}"
      data-tags="{esc("|".join(tags))}">
      <summary class="rsi-tl-event-summary">
        <span class="rsi-rt-event-dot rsi-rt-event-dot--{kind}" aria-hidden="true"></span>
        <span class="rsi-tl-event-copy">
          <span class="rsi-tl-event-meta"><b>{KIND_LABELS[kind]}</b>{publication}</span>
          <strong>{esc(event["title"])}</strong>
          <span class="rsi-tl-event-abstract">{esc(event["description"])}</span>
          <span class="rsi-summary-tags">{summary_tags}</span>
        </span><span class="rsi-rt-fold-icon" aria-hidden="true"></span>
      </summary>
      <div class="rsi-tl-event-extra">
        <div class="rsi-tl-tags" aria-label="论文与研究主题">{tag_buttons}</div>
        {preview}<div class="rsi-tl-item-footer">
          <a href="{safe_url(event["source_url"])}"{attrs}>{esc(event["source_label"])} ↗</a>{f'<span class="rsi-tl-live" data-countdown="{esc(due)}" aria-live="off">AoE 正式截止</span>' if due else ""}
        </div>
      </div>
    </details>'''


venue_ids, event_ids = set(), set()
events: list[dict] = []
known = 0
official_targets = []
for venue in DATA["venues"]:
    assert venue["id"] not in venue_ids
    venue_ids.add(venue["id"])
    assert venue["year"] == 2027
    safe_url(venue["source_url"])
    for milestone in venue["deadlines"]:
        assert milestone["id"] not in event_ids
        event_ids.add(milestone["id"])
        if milestone["status"] == "official":
            check_date(milestone["date"])
            instant = datetime.fromisoformat(milestone["due_at"])
            assert instant.utcoffset().total_seconds() == -12 * 3600
            assert instant.date().isoformat() == milestone["date"]
            known += 1
            official_targets.append((milestone["due_at"], venue["short"], milestone["label"],
                                     milestone["date"], venue["source_url"]))
            events.append(dict(
                id=milestone["id"], kind="deadline", date=milestone["date"],
                due_at=milestone["due_at"],
                title=f'{venue["short"]} 2027 · {milestone["label"]}',
                description=f'{milestone["note"]}。来源：{venue["full_name"]} 官方日程。',
                source_url=venue["source_url"], source_label="会议官方日期",
                tags=[venue["short"], "2027", "投稿节点"],
            ))
        else:
            assert milestone["status"] == "pending"
            assert milestone["date"] is None and milestone["due_at"] is None

for event in DATA["research_events"]:
    check_date(event["date"])
    assert event["id"] not in event_ids
    event_ids.add(event["id"])
    safe_url(event["source_url"])
    events.append(dict(
        id=event["id"], kind="research", date=event["date"],
        title=event["title"], description=event["description"],
        source_url=event["source_url"], source_label=event["source_label"],
        tags=event.get("tags", ["RSI 研究"]),
    ))

for paper in PAPERS:
    check_date(paper["read_on"])
    eid = "reading-" + paper["id"]
    assert eid not in event_ids
    event_ids.add(eid)
    events.append(dict(
        id=eid, kind="reading", date=paper["read_on"],
        title=f'精读：{paper["short_title"]}',
        description=paper["one_sentence"], tags=paper["tags"],
        story=paper["story"], publication=paper["publication"],
        source_url="reading-cards.html#" + paper["id"],
        source_label="打开完整论文卡片",
    ))

events.sort(key=lambda e: (e["date"], KIND_ORDER[e["kind"]], e["id"]))
tag_counts = Counter(tag for event in events for tag in event.get("tags", []))
featured = sorted(
    (tag for tag, count in tag_counts.items()
     if count >= 2 or re.fullmatch(r"I(?:[1-9]|1[0-4])", tag)),
    key=lambda tag: (-tag_counts[tag], tag.casefold()),
)[:28]
tag_options = "".join(f'<option value="{esc(tag)}">{esc(tag)} · {tag_counts[tag]}</option>'
                      for tag in featured)

weekday = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")


def day_group(day: str, rows: list[dict], *, open_initial: bool = False) -> str:
    """Use the reference timeline's real summary-row / detail-row table layout."""
    counts = Counter(row["kind"] for row in rows)
    headline = next((r["title"] for r in rows if r["kind"] == "research"), rows[0]["title"])
    day_obj = date.fromisoformat(day)
    tags = list(dict.fromkeys(tag for row in rows for tag in row.get("tags", [])
                             if re.fullmatch(r"I[0-9]+", tag)))[:5]
    labels = ''.join(f'<span>{esc(tag)}</span>' for tag in tags)
    return (
        f'<tr class="rsi-rt-day rt-day-row" id="day-{esc(day)}" data-day="{esc(day)}" '
        f'tabindex="0" aria-expanded="false" aria-controls="day-detail-{esc(day)}">'
        f'<td class="rt-table-date"><div class="rt-table-date-inner">'
        f'<button type="button" class="rt-day-toggle" data-toggle-day="{esc(day)}" '
        f'aria-label="展开 {esc(day)} 的研究记录" aria-expanded="false">＋</button>'
        f'<div><b>{int(day[5:7])}月{int(day[8:])}日 · {weekday[day_obj.weekday()]}</b><small>{esc(day)}</small></div></div></td>'
        f'<td class="rt-num rt-activity-count" data-day-total><b>{len(rows)}</b><span>条记录</span></td>'
        f'<td class="rt-num" data-day-kind="reading"><b>{counts["reading"]}</b></td>'
        f'<td class="rt-num" data-day-kind="research"><b>{counts["research"]}</b></td>'
        f'<td class="rt-num" data-day-kind="deadline"><b>{counts["deadline"]}</b></td>'
        f'<td class="rt-table-thread"><p class="rsi-rt-day-headline">{esc(headline)}</p>'
        f'<div class="rt-day-tags">{labels}</div>{bar(rows)}</td></tr>'
        f'<tr class="rt-day-detail-row" id="day-detail-{esc(day)}" data-day-detail="{esc(day)}" hidden>'
        f'<td colspan="6"><div class="rt-day-expanded"><div class="rt-day-events">'
        f'{"".join(event_card(row) for row in rows)}</div></div></td></tr>'
    )


def week_summary(days: list[str], rows: list[dict]) -> str:
    counts = Counter(row["kind"] for row in rows)
    label = f"{days[-1][5:]} — {days[0][5:]}"
    return (
        f'<tr class="rt-week-summary-row" data-week-dates="{esc("|".join(days))}"><td colspan="6">'
        f'<div class="rt-week-inline"><header><div><b>本周记录</b><span>{label}</span></div>'
        f'<div><strong data-week-total>{len(rows)}</strong><span>条活动</span></div></header>'
        f'<div class="rt-week-inline-workload"><span data-week-description>论文精读 {counts["reading"]} · '
        f'研究节点 {counts["research"]} · 会议 DDL {counts["deadline"]}</span>{bar(rows)}</div></div></td></tr>'
    )


all_months = sorted({event["date"][:7] for event in events})
months_markup = []
for month in all_months:
    rows = [event for event in events if event["date"].startswith(month)]
    days = sorted({event["date"] for event in rows}, reverse=True)
    blocks = []
    week_days = []
    for i, day in enumerate(days):
        blocks.append(day_group(day, [e for e in rows if e["date"] == day]))
        week_days.append(day)
        week = date.fromisoformat(day).isocalendar()[:2]
        next_week = date.fromisoformat(days[i+1]).isocalendar()[:2] if i+1 < len(days) else None
        if week != next_week:
            blocks.append(week_summary(week_days, [e for e in rows if e["date"] in week_days]))
            week_days = []
    months_markup.append(
        f'<details class="rsi-tl-month rt-month" data-month="{esc(month)}"'
        f'{" open" if month == all_months[0] else ""}>'
        f'<summary class="rsi-tl-month-head rt-month-header"><div><b>{month_label(month)}</b>'
        f'<span>{month}</span></div><div><b class="rsi-tl-month-days">{len(days)}</b><span>个研究日</span>'
        f'<b class="rsi-tl-month-count">{len(rows)}</b><span>条记录</span>'
        f'<span class="rsi-rt-fold-icon" aria-hidden="true"></span></div></summary>'
        f'<div class="rt-month-table-wrap"><table class="rt-month-table rsi-month-table">'
        f'<thead><tr><th scope="col">日期</th><th scope="col">活动</th><th scope="col">论文精读</th>'
        f'<th scope="col">研究节点</th><th scope="col">会议 DDL</th><th scope="col">当日脉络 / 研究主题</th></tr></thead>'
        f'<tbody>{"".join(blocks)}</tbody></table></div></details>'
    )

status_labels = {"official": "日期已确认", "official_partial": "部分确认", "pending": "日期待公布"}
venue_cards = []
for venue in DATA["venues"]:
    lines = []
    for deadline in venue["deadlines"]:
        official = deadline["status"] == "official"
        stamp = f'{esc(deadline["date"])} <small>23:59 AoE</small>' if official else "待公布"
        timer = (
            f'<span class="rsi-tl-countdown" data-countdown="{esc(deadline["due_at"])}" aria-live="off">正式截止时间</span>'
            f'<span class="rsi-tl-beijing" data-beijing="{esc(deadline["due_at"])}">北京时间换算</span>'
            if official else '<span class="rsi-tl-pending">尚无官方倒计时</span>'
        )
        pending_id = f' id="{esc(deadline["id"])}"' if not official else ""
        lines.append(
            f'<li class="rsi-tl-ddl"{pending_id} data-status="{esc(deadline["status"])}">'
            f'<span class="rsi-tl-ddl-name">{esc(deadline["label"])}</span>'
            f'<span class="rsi-tl-ddl-date">{stamp}</span>{timer}</li>'
        )
    venue_cards.append(
        f'<article class="rsi-tl-venue rsi-tl-venue--{esc(venue["status"])}" id="{esc(venue["id"])}">'
        f'<div class="rsi-tl-venue-top"><strong class="rsi-tl-venue-serial">{esc(venue["short"])} <small>2027</small></strong>'
        f'<span class="rsi-tl-status rsi-tl-status--{esc(venue["status"])}">{status_labels[venue["status"]]}</span></div>'
        f'<h3>{esc(venue["full_name"])}</h3>'
        f'<ul class="rsi-tl-deadlines">{"".join(lines)}</ul>'
        f'<p class="rsi-tl-venue-context">{esc(venue["context"])}</p>'
        f'<a class="rsi-tl-source-link" href="{safe_url(venue["source_url"])}" target="_blank" rel="noopener noreferrer">官方来源 ↗</a>'
        f'</article>'
    )

targets_json = json.dumps(
    [dict(iso=t[0], venue=t[1], label=t[2], date=t[3], url=t[4])
     for t in sorted(official_targets)], ensure_ascii=False, separators=(",", ":")
)
queue = "".join(
    f'<span class="rsi-rt-queue-chip">{esc(t[1])} <b>{esc(t[3][5:])}</b></span>'
    for t in sorted(official_targets)
)

updated = max(DATA["verified_at"], *(p["read_on"] for p in PAPERS))
research_day_count = len({e["date"] for e in events if e["kind"] != "deadline"})
header_html = f'''<header class="research-hero rt-hero rsi-timeline-hero">
  <div class="rt-hero-main"><div class="rt-hero-title"><span>RSI OBSERVATORY</span><h1>研究时间轴</h1></div>
    <p>用月历回看论文与研究进展，在日期表中展开当天记录；论文内容、研究方案和投稿节点分层浏览。</p>
    <div class="rt-hero-kpis"><span><b>{len(events)}</b>条活动</span><span><b>{research_day_count}</b>个研究日</span>
      <span><b>{len(PAPERS)}</b>篇论文精读</span><span><b>{len(DATA["research_events"])}</b>项研究节点</span>
      <span><b>{known}</b>个确认 DDL</span></div></div>
  <aside class="rt-hero-side"><div class="rt-hero-time"><b>更新 {updated}</b><span>提案尚待实验</span></div>
    <div class="rt-legend"><span class="rt-legend-item rt-legend-paper"><i></i>论文精读</span>
      <span class="rt-legend-item rt-legend-experiment"><i></i>研究节点</span>
      <span class="rt-legend-item rt-legend-idea"><i></i>会议 DDL</span></div>
    <div class="rsi-tl-header-links"><a href="reading-cards.html">论文卡片 ↗</a><a href="ideas.html">研究方向 ↗</a></div></aside>
</header>'''

overview = f'''<div class="rsi-rt-briefing rt-iclr-deadlines" data-official-deadlines="{esc(targets_json)}">
  <div class="rsi-rt-next"><span class="rsi-rt-small-label">NEXT DEADLINE · OFFICIAL / AoE</span>
    <div class="rsi-rt-next-title"><b id="rsi-rt-next-label">下一官方投稿节点</b><time id="rsi-rt-next-date"></time></div>
    <div class="rsi-rt-next-foot"><span id="rsi-rt-next-beijing">北京时间自动换算</span>
      <a id="rsi-rt-next-source" href="https://cvpr.thecvf.com/Conferences/2027/Dates" target="_blank" rel="noopener noreferrer">官方来源 ↗</a></div></div>
  <strong class="rt-ddl-countdown" id="rsi-rt-next-countdown" aria-live="off">读取已确认时间…</strong>
  <div class="rsi-rt-queue"><span>投稿窗口</span>{queue}</div>
</div>'''

deadlines = (
    '<details class="rsi-rt-venue-toggle" id="rsi-rt-venue-toggle">'
    '<summary><span><b>会议日程</b><small>CVPR · ICML · ACL 2027 / 查看注册、全文、补充材料与待公布节点</small></span>'
    '<span class="rsi-rt-venue-status">3 个会议 · 展开全部时间</span><span class="rsi-rt-fold-icon" aria-hidden="true"></span></summary>'
    '<div class="rsi-rt-venue-content"><div class="rsi-tl-venue-grid">'
    + "".join(venue_cards) + '</div>'
    f'<p class="rsi-tl-validation">官方核验日期：{esc(DATA["verified_at"])}。'
    'ICML 2027 及 ACL Commitment 尚待公布；未确认时不显示预测日期。</p></div></details>'
)

activity = (
    '<div class="rsi-tl-calendar-panel rt-heatmap-panel" id="rsi-tl-calendar-panel">'
    '<div class="rsi-tl-calendar-head rt-heatmap-heading"><div><span class="rsi-rt-small-label">RESEARCH ACTIVITY</span>'
    '<h3>研究月历</h3><p>默认显示有记录的日期区间；点击日期展开当天，也可切换完整月历。</p></div>'
    '<div class="rsi-tl-calendar-legend" aria-label="活动分类">'
    '<span><i class="rsi-tl-dot rsi-tl-dot--deadline"></i>会议 DDL</span>'
    '<span><i class="rsi-tl-dot rsi-tl-dot--reading"></i>论文精读</span>'
    '<span><i class="rsi-tl-dot rsi-tl-dot--research"></i>研究记录</span>'
    '<button type="button" id="rsi-tl-calendar-mode" aria-pressed="false">完整月历</button></div></div>'
    '<div class="rsi-tl-calendar-grid rt-heat-months" id="rsi-tl-calendar-grid" aria-label="可折叠研究月历"></div>'
    '<div class="rsi-tl-date-selection" id="rsi-tl-date-selection" hidden>'
    '<span id="rsi-tl-selected-label"></span><button id="rsi-tl-clear-day" type="button">清除日期筛选</button></div></div>'
    '<div class="rsi-tl-toolbar" aria-label="研究记录筛选">'
    '<label for="rsi-tl-kind">类型<select id="rsi-tl-kind">'
    '<option value="all">全部事件</option><option value="deadline">会议 DDL</option>'
    '<option value="reading">论文精读</option><option value="research">研究记录</option></select></label>'
    '<label for="rsi-tl-time">时间<select id="rsi-tl-time">'
    '<option value="all">全部时间</option><option value="upcoming">尚未截止</option>'
    '<option value="past">已发生／已结束</option></select></label>'
    '<label for="rsi-tl-topic">研究主题<select id="rsi-tl-topic">'
    '<option value="all">全部标签</option>' + tag_options + '</select></label>'
    '<label class="rsi-tl-search" for="rsi-tl-query">搜索'
    '<input type="search" id="rsi-tl-query" placeholder="论文名、I14、课程、CVPR…"></label>'
    '<button type="button" id="rsi-tl-reset">重置</button>'
    '<output id="rsi-tl-count" aria-live="polite">显示全部</output>'
    '</div>'
    '<div class="rsi-rt-list-heading"><div><b>按月 / 按日查看</b><span>先看当天研究概览，再展开论文内容与来源</span></div>'
    '<div><button type="button" id="rsi-tl-expand-all">展开全部研究日</button>'
    '<button type="button" id="rsi-tl-collapse-all">全部收起</button></div></div>'
    '<div class="rsi-tl-months rt-feed" id="rsi-tl-months">' + "".join(months_markup) + "</div>"
    '<p class="rsi-tl-no-results" id="rsi-tl-empty" hidden>没有符合条件的记录，请调整筛选或日期。</p>'
)

provenance = (
    '<details class="rsi-rt-provenance"><summary>来源与时间口径 · 展开核验说明</summary>'
    f'<p>会议日期核验日期：{esc(DATA["verified_at"])}。CVPR 2027 与 ACL 2027 ARR '
    '只有官方明确公布的日期进入倒计时；其他节点保留“待公布”。时刻按 23:59 AoE（UTC−12）解释。</p>'
    '<p>研究活动和论文阅读日期分别来自 <code>timeline-data.json</code> 与 '
    '<code>reading-cards.json</code>。论文研究内容来自精读卡片的原始结构化笔记；'
    '本站研究设想与作者已报告结果不混为一谈，也不代表本项目已完成实验。</p>'
    '<div class="links"><a class="link-btn" href="timeline-data.json" download>时间轴数据</a>'
    '<a class="link-btn" href="reading-cards.html">论文精读卡片</a></div></details>'
)

PAGE = {
    "slug": "timeline",
    "title": "RSI 研究时间轴",
    "en": "Research Timeline · Live submission deadlines, calendar & paper reading",
    "lead": "研究月历、论文精读与投稿节点一页查看；每层都可折叠，官方日期与研究提案分开记录。",
    "updated": max(DATA["verified_at"], *(p["read_on"] for p in PAPERS)),
    "styles": ["timeline-reference.css", "timeline.css"],
    "header_html": header_html,
    "scripts": ["timeline-view.js"],
    "sections": [
        ("overview", "研究与投稿速览", overview),
        ("deadlines", "CVPR · ICML · ACL 2027", deadlines),
        ("activity", f"研究月历与完整记录 · {len(events)} 条", activity),
        ("provenance", "来源与核验口径", provenance),
    ],
    "search_records": [
        {
            "title": f"RSI 时间轴 · {e['title']}",
            "url": f"timeline.html#{e['id']}",
            "text": e["date"] + " " + e["description"] + " " + e["title"] + " " + " ".join(e.get("tags", [])),
        }
        for e in events
    ] + [
        {
            "title": f"投稿 DDL · {v['short']} 2027",
            "url": f"timeline.html#{v['id']}",
            "text": v["context"] + " " + " ".join(d["label"] + " " + (d["date"] or "待公布")
                                                for d in v["deadlines"]),
        }
        for v in DATA["venues"]
    ],
}
