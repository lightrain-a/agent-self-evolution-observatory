"""Verified, non-promotional closest-work comparisons for RSI deep reads.

One generic renderer for all paper targets in rsi/related-work.json.
Claim provenance and model-vs-model comparison status are explicit.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = json.loads((ROOT / "rsi" / "related-work.json").read_text(encoding="utf-8"))
assert DATA["schema_version"] == 1
TARGETS = {r["paper_id"]: r for r in DATA["targets"]}
assert len(TARGETS) == len(DATA["targets"])


def e(value) -> str:
    return html.escape(str(value), quote=True)


def validate(target: dict) -> None:
    works = target["works"]
    assert 5 <= len(works) <= 24, "Curated related work requires 5-24 auditable references"
    assert len({r["id"] for r in works}) == len(works), "Duplicate related-work ID"
    assert 3 <= sum(r["distance"] == "closest" for r in works) <= 8, "Keep the closest-work shortlist focused"
    for row in works:
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", row["id"]), row["id"]
        assert row["distance"] in ("closest", "context"), row["id"]
        assert row["primary_url"].startswith("https://"), row["id"]
        assert all(row.get(k) for k in (
            "name", "venue", "family", "cited_at", "source_scope", "problem",
            "update_surface", "supervision", "shared", "difference",
            "why", "evidence", "decisive_test", "verification"
        )), f"Related-work evidence incomplete: {row['id']}"
    assert target.get("evidence_gap") and target.get("one_sentence")


def matrix(rows: list[dict], target_id: str) -> str:
    head = ["工作 / 年份", "原工作解决什么", "更新什么、靠什么反馈", "与本文区别"]
    trs = "".join(
        '<tr>'
        f'<td><a href="#related-{e(target_id)}--{e(r["id"])}">{e(r["name"])}</a>'
        f'<small>{e(r["year"])} · {e(r["venue"])}</small></td>'
        f'<td>{e(r["problem"])}</td>'
        f'<td><b>{e(r["update_surface"])}</b><small>{e(r["supervision"])}</small></td>'
        f'<td>{e(r["difference"])}</td></tr>'
        for r in rows
    )
    return '<div class="deep-related-matrix" role="region" aria-label="相关工作可横向滚动的比较表" tabindex="0"><table>' + (
        "<thead><tr>" + "".join(f'<th scope="col">{e(h)}</th>' for h in head) + "</tr></thead>"
    ) + "<tbody>" + trs + "</tbody></table></div>"


def details(rows: list[dict], target_id: str) -> str:
    return "".join(
        f'<details id="related-{e(target_id)}--{e(r["id"])}" class="deep-related-paper">'
        f'<summary><span>{e(r["name"])} · {e(r["family"])}</span><small>展开核查与区别</small></summary>'
        '<div class="deep-related-paper-body">'
        f'<p class="deep-related-venue"><b>{e(r["full_title"])}</b> · {e(r["venue"])}</p>'
        f'<p><b>RSI-Anything 怎么引用它：</b>{e(r["cited_at"])}；{e(r["relationship"])}</p>'
        f'<p><b>相同点：</b>{e(r["shared"])}</p>'
        f'<p><b>真正不同：</b>{e(r["difference"])}</p>'
        f'<p><b>为什么这个区别重要：</b>{e(r["why"])}</p>'
        f'<p><b>论文实际有的证据：</b>{e(r["evidence"])}</p>'
        f'<p><b>还需要什么决定性对照：</b>{e(r["decisive_test"])}</p>'
        f'<p class="deep-related-source"><a target="_blank" rel="noopener noreferrer" href="{e(r["primary_url"])}">核对原论文 / 官方项目</a> · '
        f'{e(r["source_scope"])} · {e(r["verification"])}</p>'
        '</div></details>'
        for r in rows
    )


def render(target: dict, base: str) -> str:
    validate(target)
    closest = [r for r in target["works"] if r["distance"] == "closest"]
    context = [r for r in target["works"] if r["distance"] == "context"]
    evolution = "".join(
        f'<li><b>{e(item["period"])}</b><span>{e(item["summary"])}</span>'
        + (f'<a href="{e(item["source_url"])}" target="_blank" '
           f'rel="noopener noreferrer">原论文</a>' if item.get("source_url") else "")
        + '</li>'
        for item in target.get("evolution", [])
    )
    companion = (
        f'<ol class="deep-related-evolution">{evolution}</ol>' if evolution else ""
    )
    secondary = (
        '<details class="deep-related-context"><summary>'
        f'其他相关工作 · {len(context)} 篇（课程 / 科研 Agent）'
        '</summary>' + matrix(context, target['paper_id']) + details(context, target['paper_id']) + '</details>'
        if context else ""
    )
    return (
        '<div class="deep-related">'
        f'<p class="deep-related-takeaway">{e(target["reading_takeaway"])}</p>'
        '<h5>这条研究路线怎么发展？</h5>' + companion
        + f'<h5>最相近的 {len(closest)} 篇 · 实际研究边界</h5>'
        '<p class="deep-related-instructions">先扫四列表，再展开具体论文。'
        '这里比较的是研究问题、更新对象和实际验证条件，'
        '不是给本文设计“全部胜出”的勾选表。</p>'
        + matrix(closest, target['paper_id'])
        + details(closest, target['paper_id'])
        + secondary
        + '<p class="deep-related-boundary"><b>读表结论：</b>'
        + e(target["one_sentence"]) + '</p>'
        + '<p class="deep-related-boundary"><b>目前无法下的结论：</b>'
        + e(target["evidence_gap"]) + '</p>'
        + '<p class="deep-related-provenance">核验日期：' + e(DATA["updated"])
        + ' · 根据 RSI-Anything ' + e(target["source_related_sections"])
        + ' 所列文献定位，逐篇对照原论文或作者项目。'
        '“同任务直接对照”和“领域相邻”两种证据不能互相替代。</p>'
        + '</div>'
    )


def search_records(paper_id: str, base: str) -> list[dict]:
    target = TARGETS.get(paper_id)
    if not target:
        return []
    return [
        {
            "title": f'Related Work · {r["name"]} vs RSI-Anything',
            "url": f'reading-notes.html#related-{paper_id}--{r["id"]}',
            "text": " ".join(str(r[k]) for k in (
                "full_title", "venue", "family", "problem", "update_surface",
                "shared", "difference", "why", "evidence", "decisive_test",
            )),
        }
        for r in target["works"]
    ]
