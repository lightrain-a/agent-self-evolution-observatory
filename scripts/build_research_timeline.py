#!/usr/bin/env python3
"""Build the public, read-only Research Timeline projection.

The timeline never grants scientific authority. Runtime/API-memory rows are always
SYSTEM events with authority=false; scientific/closure rows only mirror explicit
existing decisions from structured artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "generated"
DEFAULT_DB = Path(os.getenv("RESEARCH_TIMELINE_MEMORY_DB", "/data/wyt/agent-self-evolution-observatory/indexes/api-research-memory.sqlite3"))
DATE_RE = re.compile(r"(20\d{6})")
NON_PUBLIC_SOURCE_NAMES = {
    "advisor-priority-view.js",
    "advisor-priority-ideas.js",
    "advisor-priority-ideas.json",
    "advisor-priority-meta-review.json",
}
NON_PUBLIC_SOURCE_PREFIXES = (
    "ark-", "r31-", "r32-final-ideas", "r32-targeted-recheck",
    "final-method-refinement-", "asset-first-stri-",
)


def load(path: Path) -> dict[str, Any]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ts(value: Any = None, path: Path | None = None) -> str:
    raw = str(value or "").strip().replace("Z", "+00:00")
    if raw:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
            raw += "T12:00:00+00:00"
        try:
            dt = datetime.fromisoformat(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
        except ValueError:
            pass
    if path:
        m = DATE_RE.search(path.name)
        if m:
            return datetime.strptime(m.group(1), "%Y%m%d").replace(hour=12, tzinfo=timezone.utc).isoformat()
    return ""


def artifact_ts(data: dict[str, Any], path: Path) -> str:
    for key in ("generated_at", "adjudication_date", "decision_date", "completed_at", "created_at", "updated_at"):
        value = ts(data.get(key), path)
        if value:
            return value
    return ts(path=path)


def text(value: Any, limit: int = 1400) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    value = " ".join(str(value).split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def source_is_public(path: Path) -> bool:
    name = path.name
    return name not in NON_PUBLIC_SOURCE_NAMES and not any(name.startswith(prefix) for prefix in NON_PUBLIC_SOURCE_PREFIXES)


def src(path: Path | None) -> list[dict[str, Any]]:
    if not path or not path.exists():
        return []
    public = source_is_public(path)
    return [{
        "path": path.relative_to(ROOT).as_posix() if public else "[non-public-source]",
        "sha256": sha(path),
        "public": public,
    }]


def metrics(mapping: Any, limit: int = 8) -> list[dict[str, str]]:
    if not isinstance(mapping, dict):
        return []
    out = []
    for key, value in mapping.items():
        if isinstance(value, (str, int, float, bool)):
            out.append({"label": text(key, 100), "value": text(value, 500)})
        if len(out) >= limit:
            break
    return out


def event(*, occurred_at: str, event_class: str, research_id: str, title: str,
          state_after: str, summary_en: str, summary_zh: str, source: Path | None = None,
          importance: str = "detail", state_before: str = "", why_en: str = "", why_zh: str = "",
          limitation_en: str = "", limitation_zh: str = "", next_action: str = "",
          reopen: str = "", evidence: list[dict[str, Any]] | None = None,
          scientific: bool = False, authority_scope: str = "projection-only",
          links: list[dict[str, str]] | None = None, hint: str = "", origin: str = "artifact") -> dict[str, Any]:
    seed = "|".join((occurred_at, event_class, research_id, state_after, hint or (source.name if source else "")))
    return {
        "event_id": hashlib.sha256(seed.encode()).hexdigest()[:16],
        "occurred_at": occurred_at,
        "event_class": event_class,
        "importance": importance,
        "origin": text(origin, 80),
        "research_id": text(research_id, 160),
        "title": text(title, 500),
        "state_before": text(state_before, 240),
        "state_after": text(state_after, 260),
        "summary": {"en": text(summary_en), "zh": text(summary_zh or summary_en)},
        "why": {"en": text(why_en), "zh": text(why_zh or why_en)},
        "limitation": {"en": text(limitation_en), "zh": text(limitation_zh or limitation_en)},
        "next_action": text(next_action),
        "reopen_condition": text(reopen),
        "evidence": [{"label": text(x.get("label"), 120), "value": text(x.get("value"), 700)} for x in (evidence or []) if x.get("value") not in (None, "")][:12],
        "authority": {"scientific": bool(scientific), "scope": text(authority_scope, 240), "projection_can_change_state": False},
        "sources": src(source),
        "links": links or [],
    }


def stri_events() -> list[dict[str, Any]]:
    out = []
    specs = [
        ("asset-first-stri-autoskill-p19-stage3-result-20260819.json", "scientific", "STRI · AutoSkill/P19", "Representation change propagated through retrieval to executed behavior"),
        ("asset-first-stri-autoskill-p19-mediator-isolation-v2-result-20260819.json", "scientific", "STRI · AutoSkill/P19", "Mediator isolation strengthened the bounded causal chain"),
        ("asset-first-stri-post-isolation-review-adjudication-20260819.json", "paper", "STRI", "Narrow submission scope frozen after independent review"),
        ("asset-first-stri-iclr2027-final-state-20260816.json", "paper", "STRI", "Official ICLR submission package reached ready state"),
    ]
    for name, cls, rid, fallback_title in specs:
        path = GEN / name
        d = load(path)
        if not d:
            continue
        decision = d.get("decision") or d.get("stage") or d.get("status") or "RECORDED"
        before = ""
        if "stage3-result" in name:
            g, p = d.get("groups", {}), d.get("statistics", {}).get("fisher_exact_p")
            en = f"Frozen P19: released representation {g.get('A_original',{}).get('destructive_signature_positive','?')}/6 positive; split4 {g.get('B_split4',{}).get('destructive_signature_positive','?')}/6; ID-placebo and quotient controls 3/3; Fisher p={p}."
            zh = f"冻结 P19：released representation 为 {g.get('A_original',{}).get('destructive_signature_positive','?')}/6，split4 为 {g.get('B_split4',{}).get('destructive_signature_positive','?')}/6；ID-placebo 与 quotient control 均 3/3，Fisher p={p}。"
            why = d.get("mechanistic_interpretation", {}).get("D_quotient_control", "")
            limit = d.get("scientific_claim_boundary", "")
            ev = [{"label": k, "value": v} for k, v in g.items()] + [{"label":"Fisher p","value":p}]
            scientific = bool(d.get("authority", {}).get("dynamic_behavioral_propagation_supported"))
            scope = "bounded AutoSkill/P19 behavioral propagation only"
        elif "mediator-isolation" in name:
            g = d.get("groups", {})
            en = f"Post-checkout skill add-back restored the signature in {g.get('E_post_addback',{}).get('positive','?')}/3 fresh runs; matched cleanup control was {g.get('F_cleanup_control',{}).get('positive','?')}/3; exact p={d.get('statistics',{}).get('exact_fraction','?')}."
            zh = f"post-checkout skill add-back 在 {g.get('E_post_addback',{}).get('positive','?')}/3 次 fresh run 恢复目标行为；matched cleanup control 为 {g.get('F_cleanup_control',{}).get('positive','?')}/3；exact p={d.get('statistics',{}).get('exact_fraction','?')}。"
            why, limit = d.get("scientific_interpretation", ""), d.get("claim_boundary", "")
            ev = [{"label":k,"value":v} for k,v in g.items()] + [{"label":"exact p","value":d.get("statistics",{}).get("exact_fraction")},{"label":"replay agreement","value":d.get("measurement_repair",{}).get("stage3_replay_agreement")}]
            scientific = bool(d.get("authority", {}).get("mediator_claim_supported"))
            scope = "specific mediator attribution on frozen P19 only"
        elif "post-isolation-review" in name:
            pre, post = d.get("reviews",{}).get("deepseek_pre_isolation",{}), d.get("reviews",{}).get("deepseek_post_isolation",{})
            en = f"Independent review moved from {pre.get('score_1_to_10','?')}/10 ({pre.get('recommendation','?')}) to {post.get('score_1_to_10','?')}/10 ({post.get('recommendation','?')}); current narrow claims require no further experiment score-chasing."
            zh = f"独立评审从 {pre.get('score_1_to_10','?')}/10（{pre.get('recommendation','?')}）变为 {post.get('score_1_to_10','?')}/10（{post.get('recommendation','?')}）；当前窄化主张停止继续为分数追实验。"
            why, limit = d.get("scientific_interpretation", ""), d.get("claim_boundary", "")
            ev = [{"label":"before","value":f"{pre.get('score_1_to_10','?')}/10"},{"label":"after","value":f"{post.get('score_1_to_10','?')}/10"},{"label":"fatal flaws","value":post.get("fatal_flaws")}]
            scientific, scope = False, "review adjudication; no new method/GPU authority"
            before = f"independent review {pre.get('score_1_to_10','?')}/10 · {pre.get('recommendation','?')}"
        else:
            fmt, pq = d.get("official_format", {}), d.get("paper_quality_v2", {})
            en = f"Frozen ICLR package: {len(d.get('scientific_claim_scope',[]))} narrow claims, {fmt.get('main_text_pages','?')}/{fmt.get('main_text_page_limit','?')} main-text pages, paper evidence {pq.get('status','recorded')}."
            zh = f"冻结 ICLR 投稿包：{len(d.get('scientific_claim_scope',[]))} 条窄化主张，正文 {fmt.get('main_text_pages','?')}/{fmt.get('main_text_page_limit','?')} 页，paper evidence={pq.get('status','recorded')}。"
            why, limit = "", "; ".join(d.get("claims_forbidden", [])[:5])
            ev = [{"label":"official review","value":d.get("independent_reviews",{}).get("official_iclr2027_final_review",{}).get("verdict")},{"label":"supplement tests","value":d.get("delivery",{}).get("supplement_zip",{}).get("unit_tests")},{"label":"paper evidence","value":pq.get("status")}]
            scientific, scope = False, "paper-state projection; does not expand claims"
        out.append(event(occurred_at=artifact_ts(d,path), event_class=cls, importance="key", research_id=rid,
            title=d.get("title") or fallback_title, state_before=before, state_after=str(decision), summary_en=en, summary_zh=zh,
            why_en=why, why_zh=("展开查看结构化 artifact 中的原始机制解释与审计证据。" if why else ""),
            limitation_en=limit, limitation_zh="该事件只在 artifact 明确写出的 claim boundary 内成立；不会由时间轴自动扩大。",
            next_action=d.get("next_action", ""), evidence=ev, scientific=scientific, authority_scope=scope,
            source=path, links=[{"label":"paper","href":"selected-paper.html"},{"label":"experiments","href":"experiments.html"}]))
    return out

def principle_events() -> list[dict[str, Any]]:
    out = []
    for path in sorted(GEN.glob("*principle-readjudication-*.json")):
        d = load(path)
        if not d:
            continue
        diagnosis = d.get("principle_diagnosis", {}) if isinstance(d.get("principle_diagnosis"), dict) else {}
        counter = diagnosis.get("counter_explanation", {}) if isinstance(diagnosis.get("counter_explanation"), dict) else {}
        interp = d.get("scientific_interpretation", {}) if isinstance(d.get("scientific_interpretation"), dict) else {}
        authority = d.get("authority", {}) if isinstance(d.get("authority"), dict) else {}
        state = diagnosis.get("status") or ("PRINCIPLE_DEAD_END_CERTIFIED" if d.get("principle_dead_end_certified") else "READJUDICATED")
        layer = d.get("closure_layer") or d.get("failure_layer") or "scoped_principle"
        safe = interp.get("safe_claim") or d.get("reason") or counter.get("statement") or diagnosis.get("statement") or ""
        reason = counter.get("statement") or diagnosis.get("statement") or safe
        reopen = counter.get("reopen_condition") or diagnosis.get("reopen_condition") or d.get("reopen_condition") or d.get("reopen_only_if") or ""
        refs = counter.get("evidence_refs") or diagnosis.get("evidence_refs") or []
        refs = refs if isinstance(refs, list) else []
        auth_scope = str(authority.get("scientific_authority", ""))
        scientific = bool(d.get("principle_dead_end_certified")) and (
            "principle" in auth_scope.lower()
            or bool(authority.get("primary_same_information_counter_explanation_authorizes_scoped_dead_end"))
            or bool(d.get("principle_update_allowed"))
        )
        key = "core_principle" in str(layer).lower() or bool(d.get("experiment_run_for_this_readjudication")) or str(d.get("candidate_id", "")).startswith("PORT-")
        out.append(event(
            occurred_at=artifact_ts(d,path), event_class="closure", importance="key" if key else "detail",
            research_id=d.get("candidate_id", "principle-readjudication"), title=d.get("title") or d.get("candidate_id") or path.stem,
            state_after=str(state), summary_en=safe or f"Scoped principle readjudication closed this formulation at {layer}.",
            summary_zh=f"该候选完成 scoped principle readjudication，并在 {layer} 层形成关闭结论。展开可查看原始 reduction、边界与重开条件。",
            why_en=reason, why_zh="该关闭来自已有证据下的 same-information / scope-matched reduction 或明确结构性裁决；不是把运行失败自动解释成科学失败。",
            limitation_en=d.get("dead_end_scope", ""), limitation_zh="关闭只作用于 artifact 明确写出的 scoped formulation，不自动外推到整个方向或 benchmark。",
            reopen=reopen, evidence=[{"label":"evidence","value":x} for x in refs[:6]] + [{"label":"experiment run","value":d.get("experiment_run_for_this_readjudication")},{"label":"closure layer","value":layer}],
            scientific=scientific, authority_scope=auth_scope or ("scoped principle adjudication" if scientific else "readjudication projection only"),
            source=path, links=[{"label":"research","href":"paper-ideas.html"}]))
    return out


def p0_events() -> list[dict[str, Any]]:
    out = []
    for path in sorted(GEN.glob("p0-*.json")):
        d = load(path)
        if not d:
            continue
        decision = d.get("decision") or d.get("verdict") or d.get("formal_outcome")
        if not isinstance(decision, str) or not decision.strip():
            continue
        upper = decision.upper()
        scientific = bool(d.get("scientific_authority")) or bool(d.get("standalone_claim_stop_authorized")) or bool(d.get("method_fail_authorized"))
        if any(x in upper for x in ("STOP", "FAIL", "MERGE")):
            cls = "closure"
        elif any(x in upper for x in ("HOLD", "BLOCK")):
            cls = "blocker"
        else:
            cls = "scientific" if scientific else "system"
        rid = d.get("code") or d.get("idea_id") or d.get("experiment_id") or path.stem
        next_action = d.get("next_action") or d.get("next") or ""
        out.append(event(
            occurred_at=artifact_ts(d,path), event_class=cls, importance="detail", research_id=str(rid),
            title=d.get("title") or d.get("scientific_role") or str(rid), state_after=decision,
            summary_en=d.get("interpretation") or d.get("scientific_interpretation") or next_action or decision,
            summary_zh=f"该 P0 artifact 记录了明确决策：{decision}。展开查看原始指标、下一步和 authority 边界。",
            why_en=d.get("reason") or d.get("diagnosis") or "", why_zh="该事件直接来自已有 P0 artifact；时间轴只做投影，不重新裁决。",
            next_action=next_action, evidence=metrics(d.get("metrics") or d.get("summary") or {}), scientific=scientific,
            authority_scope="existing P0 decision artifact" if scientific else "P0/system projection; no new authority",
            source=path, links=[{"label":"experiments","href":"experiments.html"}]))
    return out


def current_status_events() -> list[dict[str, Any]]:
    path = GEN / "current-research-status.json"
    d = load(path)
    if not d:
        return []
    when = artifact_ts(d,path)
    h, p, f = d.get("headline", {}), d.get("leading_paper_track", {}), d.get("idea_search_funnel", {})
    out = []
    if p:
        out.append(event(
            occurred_at=when, event_class="paper", importance="key", research_id=p.get("paper_id","STRI"), title=p.get("title","Leading paper track"),
            state_after=p.get("submission_status") or p.get("status") or "RECORDED",
            summary_en=f"Current snapshot: {p.get('claims_supported',0)}/{p.get('claims_total',0)} narrow claims supported, QA {p.get('qa_passed',0)}/{p.get('qa_total',0)}, evidence debt {p.get('paper_quality_evidence_debt',0)}, new GPU evidence required={p.get('new_gpu_evidence_required')}.",
            summary_zh=f"当前快照：窄化主张 {p.get('claims_supported',0)}/{p.get('claims_total',0)} supported，QA {p.get('qa_passed',0)}/{p.get('qa_total',0)}，evidence debt={p.get('paper_quality_evidence_debt',0)}，new GPU evidence required={p.get('new_gpu_evidence_required')}。",
            limitation_en="Current-status is a derived projection and cannot itself expand claims.", limitation_zh="current-status 是派生投影，只汇总已有证据，不能自行扩大 claim。",
            next_action=p.get("next_action", ""), evidence=[{"label":"claims","value":f"{p.get('claims_supported',0)}/{p.get('claims_total',0)}"},{"label":"QA","value":f"{p.get('qa_passed',0)}/{p.get('qa_total',0)}"},{"label":"evidence debt","value":p.get("paper_quality_evidence_debt",0)},{"label":"human signoff pending","value":p.get("human_signoff_pending")}],
            scientific=False, authority_scope="current-status projection; source claims retain their own authority", source=path,
            links=[{"label":"paper","href":"selected-paper.html"}], hint="paper-status"))
    out.append(event(
        occurred_at=when, event_class="system", importance="key", research_id="Idea Search", title="Canonical double-funnel discovery snapshot",
        state_after=f.get("pre_f0_status") or f.get("last_completed_generator_status") or "RECORDED",
        summary_en=f"Last canonical receipt: {f.get('last_completed_raw_seeds',0)} raw seeds, {f.get('last_completed_reviewer_attacks',0)} reviewer attacks, {f.get('last_completed_repair_children',0)} repair children, {f.get('pre_f0_queued',0)} Pre-F0 candidates; final Problem-Gate passes={f.get('final_problem_gate_pass',0)}.",
        summary_zh=f"最近 canonical receipt：{f.get('last_completed_raw_seeds',0)} 个 raw seed、{f.get('last_completed_reviewer_attacks',0)} 次 reviewer attack、{f.get('last_completed_repair_children',0)} 个 repair child、{f.get('pre_f0_queued',0)} 个 Pre-F0 候选；正式 Problem-Gate pass={f.get('final_problem_gate_pass',0)}。",
        why_en="Pre-F0 is evidence acquisition, not paper/method/experiment/P0/GPU authority.", why_zh="Pre-F0 只是证据获取阶段，不等于 Paper/Method/Experiment/P0/GPU 授权。",
        limitation_en="The discovery funnel explicitly carries zero scientific authority.", limitation_zh="该 discovery funnel 明确是 zero scientific authority；候选数量不能当成科研结论。",
        evidence=[{"label":"raw seeds","value":f.get("last_completed_raw_seeds",0)},{"label":"Pre-F0 queued","value":f.get("pre_f0_queued",0)},{"label":"support ready","value":f.get("pre_f0_support_ready",0)},{"label":"support holds","value":f.get("pre_f0_support_holds",0)},{"label":"formal launchable","value":h.get("launchable_formal_experiments",0)}],
        scientific=False, authority_scope="zero-authority discovery/search control", source=path,
        links=[{"label":"research","href":"paper-ideas.html"},{"label":"system","href":"system-overview.html"}], hint="discovery-status"))
    return out

def memory_events(db_path: Path) -> list[dict[str, Any]] | None:
    if not db_path.exists():
        return None
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        runs = conn.execute("SELECT * FROM runs ORDER BY imported_at").fetchall()
    except sqlite3.Error:
        return None
    out = []
    try:
        for run in runs:
            rid = run["run_id"]
            dispositions = Counter(r[0] for r in conn.execute("SELECT disposition FROM research_objects WHERE run_id=?",(rid,)).fetchall())
            edges = conn.execute("SELECT COUNT(*) FROM lineage_edges WHERE run_id=?",(rid,)).fetchone()[0]
            failures = conn.execute("SELECT COUNT(*) FROM api_calls WHERE run_id=? AND failure_class!='NONE'",(rid,)).fetchone()[0]
            ready = dispositions.get("READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT",0)
            ev = [{"label":"API calls","value":run["call_count"]},{"label":"research objects","value":run["object_count"]},{"label":"lineage edges","value":edges},{"label":"preflight-ready objects","value":ready},{"label":"recorded call failures","value":failures}]
            ev += [{"label":f"disposition · {name}","value":count} for name,count in dispositions.most_common(4)]
            out.append(event(
                occurred_at=ts(run["imported_at"]), event_class="system", importance="key", research_id="Research Memory",
                title="Append-only research run imported into Research Memory", state_after=run["status"],
                summary_en=f"Run {rid}: {run['call_count']} API calls, {run['object_count']} research objects, {edges} lineage edges, {ready} preflight-ready objects.",
                summary_zh=f"run {rid} 已写入 Research Memory：{run['call_count']} 次 API call、{run['object_count']} 个 research object、{edges} 条 lineage，以及 {ready} 个 preflight-ready object。",
                why_en="This is provenance/search progress only. The memory schema fixes scientific_authority=0 and belief_authority=0 for imported API/research-memory rows.",
                why_zh="该事件只表示 provenance / 搜索系统进度。数据库对这些 API 与 Research Memory 记录硬性约束 scientific_authority=0、belief_authority=0。",
                limitation_en="Preflight readiness is not a Problem-Gate pass and cannot authorize experiments or update scientific belief by itself.",
                limitation_zh="preflight readiness 不等于 Problem-Gate pass，也不能单独授权实验或改变 scientific belief。",
                next_action="Use preflight contracts only after normal governance and scientific authorization checks succeed.",
                evidence=ev, scientific=False, authority_scope="runtime/provenance memory only; schema-enforced zero scientific and belief authority",
                links=[{"label":"system","href":"system-overview.html"},{"label":"research","href":"paper-ideas.html"}], hint=rid, origin="research_memory_db"))
    except sqlite3.Error:
        return None
    finally:
        conn.close()
    return out


def preserved_memory_events() -> list[dict[str, Any]]:
    previous = load(GEN / "research-timeline.json")
    rows = previous.get("events") if isinstance(previous, dict) else []
    if not isinstance(rows, list):
        return []
    return [
        row for row in rows
        if isinstance(row, dict)
        and (row.get("origin") == "research_memory_db" or row.get("research_id") == "Research Memory")
        and row.get("authority", {}).get("scientific") is False
    ]


def dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen, out = set(), []
    for item in items:
        if item["event_id"] in seen or not item.get("occurred_at"):
            continue
        seen.add(item["event_id"])
        out.append(item)
    out.sort(key=lambda x:(x["occurred_at"],x["importance"]=="key",x["event_id"]), reverse=True)
    return out


def build(db_path: Path) -> dict[str, Any]:
    runtime = memory_events(db_path)
    if runtime is None:
        runtime = preserved_memory_events()
        runtime_source = "preserved_committed_snapshot" if runtime else "unavailable"
    else:
        runtime_source = "live_read_only_db"
    items = dedupe(stri_events() + principle_events() + p0_events() + current_status_events() + runtime)
    classes = Counter(x["event_class"] for x in items)
    dates = Counter(x["occurred_at"][:10] for x in items)
    return {
        "schema_version":"1.0",
        "generated_at":max((x["occurred_at"] for x in items), default=""),
        "projection_policy":{
            "read_only":True,
            "projection_has_scientific_authority":False,
            "zero_authority_runtime_rows_remain_zero_authority":True,
            "execution_or_provenance_failure_is_not_scientific_failure":True,
            "collapsed_summary_never_replaces_source_artifact":True,
            "before_state_is_omitted_when_not_explicitly_recorded":True,
        },
        "summary":{
            "events":len(items),
            "runtime_memory_source":runtime_source,
            "runtime_memory_events":sum(x.get("origin") == "research_memory_db" or x.get("research_id") == "Research Memory" for x in items),
            "key_events":sum(x["importance"]=="key" for x in items),
            "authority_bearing_scoped_events":sum(bool(x["authority"]["scientific"]) for x in items),
            "days":len(dates),
            "class_counts":dict(sorted(classes.items())),
            "date_counts":dict(sorted(dates.items(), reverse=True)),
        },
        "events":items,
    }


def validate(payload: dict[str, Any]) -> None:
    assert payload["projection_policy"]["projection_has_scientific_authority"] is False
    seen = set()
    for item in payload["events"]:
        assert item["event_id"] not in seen
        seen.add(item["event_id"])
        assert item["event_class"] in {"scientific","paper","closure","blocker","system"}
        assert item["authority"]["projection_can_change_state"] is False
        if item["research_id"] == "Research Memory":
            assert item["event_class"] == "system" and item["authority"]["scientific"] is False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--memory-db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    payload = build(args.memory_db)
    validate(payload)
    json_path, js_path = GEN/"research-timeline.json", GEN/"research-timeline.js"
    json_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.RESEARCH_TIMELINE = "+json.dumps(payload,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    s = payload["summary"]
    print(f"research timeline: {s['events']} events / {s['key_events']} key / {s['days']} days")


if __name__ == "__main__":
    main()
