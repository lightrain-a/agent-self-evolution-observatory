"""RSI's independent research timeline with source-verified conference deadlines.

Conference facts live in rsi/timeline-data.json; reading events come automatically
from the versioned reading-card registry, not manually copied summaries.
"""
from __future__ import annotations

import html
import json
import re
from datetime import date, datetime
from itertools import groupby
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "rsi" / "timeline-data.json"
CARDS = ROOT / "rsi" / "reading-cards.json"
DATA = json.loads(REGISTRY.read_text(encoding="utf-8"))
PAPERS = json.loads(CARDS.read_text(encoding="utf-8"))["papers"]
assert DATA["schema_version"] == "1.0"
date.fromisoformat(DATA["verified_at"])


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def safe_url(value: str) -> str:
    if not value or (not value.startswith("https://") and not re.fullmatch(
        r"[a-z0-9-]+\.html(?:#[a-z0-9-]+)?", value
    )):
        raise ValueError("Timeline source must be official HTTPS or local page: " + value)
    return esc(value)


def check_date(value: str) -> None:
    date.fromisoformat(value)


def month_title(day: str) -> str:
    yyyy, mm = day[:7].split("-")
    return f"{yyyy} 年 {int(mm):02d} 月"


def chinese_date(day: str) -> str:
    y, m, d = day.split("-")
    return f"{y}-{m}-{d}"


def kind_name(kind: str) -> str:
    return {"deadline":"会议 DDL", "reading":"论文精读", "research":"研究记录"}[kind]


def event_card(event: dict) -> str:
    kind = event["kind"]
    due = event.get("due_at") or ""
    attrs = ' target="_blank" rel="noopener noreferrer"' if event["source_url"].startswith("https://") else ''
    link = f'<a href="{safe_url(event["source_url"])}"{attrs}>{esc(event["source_label"])} ↗</a>'
    stamp = f'<time datetime="{esc(event["date"])}">{esc(event["date"][5:])}</time>'
    status = ('官方确认 · AoE' if kind == "deadline" else '阅读卡片已归档' if kind == "reading" else '站内研究记录')
    return f'''<article class="rsi-tl-item rsi-tl-item--{kind}" id="{esc(event["id"])}"
      data-kind="{kind}" data-date="{esc(event["date"])}" data-due-at="{esc(due)}">
      <div class="rsi-tl-item-date">{stamp}</div>
      <div class="rsi-tl-item-main">
        <div class="rsi-tl-item-meta"><span class="rsi-tl-kind rsi-tl-kind--{kind}">{kind_name(kind)}</span><span>{esc(status)}</span></div>
        <h3>{esc(event["title"])}</h3>
        <p>{esc(event["description"])}</p>
        <div class="rsi-tl-item-footer">{link}{f'<span class="rsi-tl-live" data-countdown="{esc(due)}">AoE · 23:59</span>' if due else ""}</div>
      </div>
    </article>'''


venue_ids, event_ids = set(), set()
events = []
known = 0
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
            when = datetime.fromisoformat(milestone["due_at"])
            assert when.utcoffset().total_seconds() == -12 * 3600
            assert when.date().isoformat() == milestone["date"]
            known += 1
            events.append(dict(
                id=milestone["id"], kind="deadline", date=milestone["date"],
                due_at=milestone["due_at"],
                title=f'{venue["short"]} 2027 · {milestone["label"]}',
                description=f'{milestone["note"]}。来源：{venue["full_name"]} 官方会议日程。',
                source_url=venue["source_url"], source_label="会议官方日期",
            ))
        else:
            assert milestone["status"] == "pending" and milestone["date"] is None and milestone["due_at"] is None

research_events = DATA["research_events"]
for event in research_events:
    check_date(event["date"])
    assert event["id"] not in event_ids
    event_ids.add(event["id"])
    safe_url(event["source_url"])
    events.append(dict(id=event["id"], kind="research", date=event["date"],
                       title=event["title"], description=event["description"],
                       source_url=event["source_url"], source_label=event["source_label"]))

for card in PAPERS:
    check_date(card["read_on"])
    eid = "reading-" + card["id"]
    assert eid not in event_ids
    event_ids.add(eid)
    events.append(dict(id=eid, kind="reading", date=card["read_on"],
                       title=f'精读：{card["short_title"]}',
                       description=card["one_sentence"],
                       source_url="reading-cards.html#" + card["id"],
                       source_label="打开精读卡片"))

events.sort(key=lambda e: (e["date"], {"research":0,"reading":1,"deadline":2}[e["kind"]], e["id"]))
months = []
for month, items in groupby(events, key=lambda e: e["date"][:7]):
    rows = list(items)
    months.append(
        f'<section class="rsi-tl-month" data-month="{esc(month)}">'
        f'<div class="rsi-tl-month-head"><h3>{month_title(month + "-01")}</h3><span>{len(rows)} 条记录</span></div>'
        f'<div class="rsi-tl-month-body">{"".join(event_card(e) for e in rows)}</div></section>'
    )

venue_cards = []
for venue in DATA["venues"]:
    status_labels = {"official":"官方已确认", "official_partial":"部分确认", "pending":"等待官方"}
    lines = []
    for item in venue["deadlines"]:
        official = item["status"] == "official"
        stamp = f'{item["date"]} <small>AoE 23:59</small>' if official else "待公布"
        countdown = (
            f'<span class="rsi-tl-countdown" data-countdown="{esc(item["due_at"])}">官方日期</span>'
            if official else '<span class="rsi-tl-pending">不显示预测倒计时</span>'
        )
        pending_id = f' id="{esc(item["id"])}"' if not official else ''
        lines.append(
            f'<li class="rsi-tl-ddl"{pending_id} data-status="{esc(item["status"])}"><span class="rsi-tl-ddl-name">{esc(item["label"])}</span>'
            f'<span class="rsi-tl-ddl-date">{stamp}</span>{countdown}</li>'
        )
    venue_cards.append(
        f'''<article class="rsi-tl-venue rsi-tl-venue--{esc(venue["status"])}" id="{esc(venue["id"])}">
        <div class="rsi-tl-venue-top"><span class="rsi-tl-venue-serial">{esc(venue["short"])} <small>{venue["year"]}</small></span>
        <span class="rsi-tl-status rsi-tl-status--{esc(venue["status"])}">{status_labels[venue["status"]]}</span></div>
        <h3>{esc(venue["full_name"])}</h3><p class="rsi-tl-track">{esc(venue["track"])}</p>
        <ul class="rsi-tl-deadlines">{''.join(lines)}</ul>
        <p class="rsi-tl-venue-context">{esc(venue["context"])}</p>
        <a class="rsi-tl-source-link" href="{safe_url(venue["source_url"])}" target="_blank" rel="noopener noreferrer">
          { "查看官方投稿日程" if venue["status"]!="pending" else "查看会议主办方网站" } ↗</a>
        </article>'''
    )

hero = f'''<div class="rsi-tl-intro">
    <div class="rsi-tl-intro-main"><span class="rsi-tl-kicker">RSI / RESEARCH ROADMAP / 2026—2027</span>
    <h3>研究进展与投稿窗口，在同一条时间轴上。</h3>
    <p>将 RSI 论文阅读和资料整理记录，与目标会议正式 DDL 分层展示。所有日期都保留原始来源，<b>未公布的截稿日期不采用猜测值</b>。</p></div>
    <div class="rsi-tl-overview">
      <div><strong>03</strong><span>目标会议</span></div>
      <div><strong>{known:02d}</strong><span>已确认投稿节点</span></div>
      <div><strong>{len(PAPERS):02d}</strong><span>精读论文卡片</span></div>
    </div>
</div>'''

PAGE = {
    "slug": "timeline",
    "title": "RSI 研究时间轴",
    "en": "Research Timeline · RSI learning, reading & submission deadlines",
    "lead": "按真实记录追踪 RSI 研究进展，并集中管理 CVPR、ICML、ACL 三个会议的官方投稿日期。已确认与待公布日期明确区分。",
    "updated": DATA["verified_at"],
    "styles": ["timeline.css"],
    "scripts": ["timeline-view.js"],
    "sections": [
        ("overview", "投稿目标与时间轴概览",
         hero + f'<p class="rsi-tl-validation">信息核验：{esc(DATA["verified_at"])} · {esc(DATA["timezone_note"])}</p>'),
        ("deadlines", "会议 DDL · CVPR / ICML / ACL",
         '<div class="rsi-tl-venue-grid">' + ''.join(venue_cards) + '</div>'
         '<p class="rsi-tl-notice"><b>ICML 2027:</b> 当前仅可确认会议主办方官方渠道，未确认 2027 摘要或全文截稿日。'
         'ACL 2027 的 ARR 截稿与后续 Commitment 不应混为一个节点；日历中仅对有正式日期的节点生成倒计时。</p>'),
        ("activity", f"研究活动与投稿时间轴 · {len(events)} 个已知日期",
         '''<div class="rsi-tl-toolbar"><label for="rsi-tl-kind">事件类型<select id="rsi-tl-kind">
           <option value="all">全部事件</option><option value="deadline">会议 DDL</option>
           <option value="reading">论文精读</option><option value="research">研究记录</option></select></label>
           <label for="rsi-tl-time">时间范围<select id="rsi-tl-time">
           <option value="all">全部时间</option><option value="upcoming">尚未截止</option>
           <option value="past">已结束／已发生</option></select></label>
           <label class="rsi-tl-search" for="rsi-tl-query">检索记录<input type="search" id="rsi-tl-query" placeholder="例如 CVPR、R²Orch、实验、ARR"></label>
           <button type="button" id="rsi-tl-reset">重置</button>
           <output id="rsi-tl-count" aria-live="polite">显示全部</output></div>'''
         '<div class="rsi-tl-months" id="rsi-tl-months">' + ''.join(months) + '</div>'
         '<p class="rsi-tl-no-results" id="rsi-tl-empty" hidden>该筛选条件下没有时间轴记录，请调整类型、时间范围或检索词。</p>'),
        ("provenance", "来源、时间口径与后续扩展",
         f'<p>截至 <strong>{esc(DATA["verified_at"])}</strong>，CVPR 2027 的注册、投稿、补充材料三个日期，以及 ACL 2027 的 ARR 投稿日期已从大会官方页面核实。'
         'ICML 2027 及 ACL 2027 Commitment 尚未核实到正式 DDL，因此只标记“待公布”。会议截稿以官方最新通知为准。</p>'
         '<p>本页面的研究记录来自本站已归档的资料与论文精读卡片，'
         '<strong>不暗示实验已经成功、已经投稿或会议已经接收。</strong>论文卡片日期从 <code>reading-cards.json</code> 自动读取。</p>'
         '<p>扩展方法：向 <code>timeline-data.json</code> 增加正式核对过的会议信息、日期和引用；向 <code>research_events</code> '
         '增加可溯源的 RSI 里程碑；运行站点构建脚本后同步更新本页。未知日期必须保留 <code>null</code>。</p>'
         '<div class="links"><a class="link-btn" href="timeline-data.json" download>下载时间轴结构化数据</a>'
         '<a class="link-btn" href="reading-cards.html">查看论文精读卡片</a></div>'),
    ],
    "search_records": [
        {
            "title": f"RSI 时间轴 · {e['title']}",
            "url": f"timeline.html#{e['id']}",
            "text": e["date"]+" "+e["description"]+" "+e["title"],
        }
        for e in events
    ] + [
        {
            "title": f"投稿 DDL · {v['short']} 2027",
            "url": f"timeline.html#{v['id']}",
            "text": v["context"]+" "+" ".join(d["label"]+" "+(d["date"] or "待公布") for d in v["deadlines"]),
        }
        for v in DATA["venues"]
    ],
}
