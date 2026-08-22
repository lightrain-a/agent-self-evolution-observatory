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
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "generated"
DEFAULT_DB = Path(os.getenv("RESEARCH_TIMELINE_MEMORY_DB", "/data/wyt/agent-self-evolution-observatory/indexes/api-research-memory.sqlite3"))
DATE_RE = re.compile(r"(20\d{6})")
CHINA_TZ = ZoneInfo("Asia/Shanghai")
CURATED_STRI_FILES = {
    "asset-first-stri-autoskill-p19-stage3-result-20260819.json",
    "asset-first-stri-autoskill-p19-mediator-isolation-v2-result-20260819.json",
    "asset-first-stri-post-isolation-review-adjudication-20260819.json",
    "asset-first-stri-iclr2027-final-state-20260816.json",
}
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
AGGREGATE_BINDING_SOURCES = {
    "generated/current-research-status.json",
    "generated/research-system-state.json",
    "generated/research-items.json",
    "generated/paper-registry.json",
    "generated/human-terminal-idea-state.json",
    "generated/p0-admission-state.json",
    "generated/p0-revived-batch-f0.json",
    "generated/paper-first-idea-incubation.json",
}


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
            dt = datetime.strptime(raw, "%Y-%m-%d").replace(hour=12, tzinfo=CHINA_TZ)
            return dt.astimezone(timezone.utc).isoformat()
        try:
            dt = datetime.fromisoformat(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=CHINA_TZ)
            return dt.astimezone(timezone.utc).isoformat()
        except ValueError:
            pass
    if path:
        m = DATE_RE.search(path.name)
        if m:
            dt = datetime.strptime(m.group(1), "%Y%m%d").replace(hour=12, tzinfo=CHINA_TZ)
            return dt.astimezone(timezone.utc).isoformat()
    return ""


_GIT_PATH_DATE_TIMES: dict[tuple[str, str], str] | None = None
_PREVIOUS_EXACT_BY_SHA: dict[str, str] | None = None


def _native_artifact_time(data: dict[str, Any], path: Path) -> tuple[str, str]:
    for key in ("generated_at", "adjudication_date", "decision_date", "completed_at", "created_at", "updated_at"):
        raw = data.get(key)
        if not isinstance(raw, str) or not raw.strip():
            continue
        return ts(raw, path), ("exact" if "T" in raw or re.search(r"\d{2}:\d{2}", raw) else "date")
    return ts(path=path), ("date" if DATE_RE.search(path.name) else "exact")


def _previous_exact_by_sha() -> dict[str, str]:
    global _PREVIOUS_EXACT_BY_SHA
    if _PREVIOUS_EXACT_BY_SHA is not None:
        return _PREVIOUS_EXACT_BY_SHA
    result: dict[str, str] = {}
    previous = load(GEN / "research-timeline.json")
    for row in previous.get("events", []) if isinstance(previous, dict) else []:
        if not isinstance(row, dict) or row.get("time_precision") != "exact":
            continue
        for source in row.get("sources", []) or []:
            digest = source.get("sha256") if isinstance(source, dict) else None
            if digest and row.get("occurred_at"):
                result[str(digest)] = str(row["occurred_at"])
    _PREVIOUS_EXACT_BY_SHA = result
    return result


def _git_path_date_times() -> dict[tuple[str, str], str]:
    global _GIT_PATH_DATE_TIMES
    if _GIT_PATH_DATE_TIMES is not None:
        return _GIT_PATH_DATE_TIMES
    result: dict[tuple[str, str], str] = {}
    if git_is_shallow():
        _GIT_PATH_DATE_TIMES = result
        return result
    try:
        completed = subprocess.run(
            ["git", "log", "--format=@@%cI", "--name-only", "--", "generated"],
            cwd=ROOT, text=True, capture_output=True, timeout=30, check=False,
        )
    except OSError:
        _GIT_PATH_DATE_TIMES = result
        return result
    current_iso = ""
    current_day = ""
    for line in completed.stdout.splitlines():
        if line.startswith("@@"):
            current_iso = ts(line[2:])
            current_day = china_date(current_iso) if current_iso else ""
            continue
        rel = line.strip()
        if not rel.startswith("generated/") or not current_iso or not current_day:
            continue
        result.setdefault((rel, current_day), current_iso)
    _GIT_PATH_DATE_TIMES = result
    return result


def _backfilled_artifact_time(data: dict[str, Any], path: Path) -> tuple[str, str]:
    native_time, precision = _native_artifact_time(data, path)
    if precision != "date" or not native_time:
        return native_time, precision
    # A committed exact timestamp for the same immutable source hash is the safest
    # fallback on shallow CI checkouts where full Git history is unavailable.
    prior = _previous_exact_by_sha().get(sha(path))
    if prior and china_date(prior) == china_date(native_time):
        return prior, "exact"
    rel = path.relative_to(ROOT).as_posix()
    git_time = _git_path_date_times().get((rel, china_date(native_time)))
    if git_time:
        return git_time, "exact"
    return native_time, "date"


def artifact_ts(data: dict[str, Any], path: Path) -> str:
    return _backfilled_artifact_time(data, path)[0]


def artifact_precision(data: dict[str, Any], path: Path) -> str:
    return _backfilled_artifact_time(data, path)[1]


def china_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).astimezone(CHINA_TZ).date().isoformat()
    except (TypeError, ValueError):
        return str(iso)[:10]


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


def state_cn(value: Any) -> str:
    raw = text(value, 220)
    u = raw.upper()
    if not raw or u == "ARTIFACT_RECORDED": return "已记录"
    if "READY_TO_SUBMIT" in u: return "论文就绪，待人工确认并提交"
    if "SUBMISSION" in u and ("READY" in u or "PASS" in u): return "投稿材料已就绪"
    if "PAPER" in u and "READY" in u: return "论文阶段已就绪"
    if "ADVANCE" in u or u.startswith("GO_"): return "通过当前门槛，继续推进"
    if "SUPPORTED" in u: return "已有证据支持"
    if "PASS" in u or "READY" in u or "CLEAR" in u: return "通过 / 就绪"
    if "MERGE" in u: return "已合并，不再独立推进"
    if "INCONCLUSIVE" in u: return "证据不足，当前不可判定"
    if "HOLD" in u or "WAIT" in u or "PENDING" in u: return "暂缓，等待条件满足"
    if "BLOCK" in u: return "已阻断"
    if "INVALID" in u: return "当前实现无效，不更新科研结论"
    if "STOP" in u or "TERMINAT" in u or "DEAD_END" in u or "REJECT" in u or "FAIL" in u: return "已停止 / 关闭"
    if "REVIEW" in u: return "已完成评审"
    if "DESIGN" in u: return "进入设计阶段"
    return raw


def collection_metrics(data: dict[str, Any], limit: int = 6) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key, value in data.items():
        if isinstance(value, list):
            out.append({"label": f"{key} 数量", "value": len(value)})
        elif isinstance(value, dict) and key in {"summary", "statistics", "counts", "headline"}:
            out.extend(metrics(value, max(1, limit - len(out))))
        if len(out) >= limit:
            break
    return out[:limit]


def event(*, occurred_at: str, event_class: str, research_id: str, title: str,
          state_after: str, summary_en: str, summary_zh: str, source: Path | None = None,
          importance: str = "detail", state_before: str = "", why_en: str = "", why_zh: str = "",
          limitation_en: str = "", limitation_zh: str = "", next_action: str = "",
          reopen: str = "", evidence: list[dict[str, Any]] | None = None,
          scientific: bool = False, authority_scope: str = "projection-only",
          links: list[dict[str, str]] | None = None, hint: str = "", origin: str = "artifact",
          title_zh: str = "", research_label_zh: str = "", next_action_zh: str = "",
          reopen_zh: str = "", authority_scope_zh: str = "", time_precision: str = "exact") -> dict[str, Any]:
    seed = "|".join((occurred_at, event_class, research_id, state_after, hint or (source.name if source else "")))
    return {
        "event_id": hashlib.sha256(seed.encode()).hexdigest()[:16],
        "occurred_at": occurred_at,
        "time_precision": time_precision if time_precision in {"exact", "date"} else "exact",
        "event_class": event_class,
        "importance": importance,
        "origin": text(origin, 80),
        "research_id": text(research_id, 160),
        "research_label_zh": text(research_label_zh, 220),
        "title": text(title, 500),
        "title_zh": text(title_zh, 500),
        "state_before": text(state_before, 240),
        "state_after": text(state_after, 260),
        "summary": {"en": text(summary_en), "zh": text(summary_zh or summary_en)},
        "why": {"en": text(why_en), "zh": text(why_zh or why_en)},
        "limitation": {"en": text(limitation_en), "zh": text(limitation_zh or limitation_en)},
        "next_action": text(next_action),
        "next_action_zh": text(next_action_zh),
        "reopen_condition": text(reopen),
        "reopen_condition_zh": text(reopen_zh),
        "evidence": [{"label": text(x.get("label"), 120), "value": text(x.get("value"), 700)} for x in (evidence or []) if x.get("value") not in (None, "")][:12],
        "authority": {"scientific": bool(scientific), "scope": text(authority_scope, 240), "scope_zh": text(authority_scope_zh, 320), "projection_can_change_state": False},
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
        title_zh = ""
        research_label_zh = "STRI"
        if "stage3-result" in name:
            g, p = d.get("groups", {}), d.get("statistics", {}).get("fisher_exact_p")
            en = f"Frozen P19: released representation {g.get('A_original',{}).get('destructive_signature_positive','?')}/6 positive; split4 {g.get('B_split4',{}).get('destructive_signature_positive','?')}/6; ID-placebo and quotient controls 3/3; Fisher p={p}."
            zh = f"冻结 P19：released representation 为 {g.get('A_original',{}).get('destructive_signature_positive','?')}/6，split4 为 {g.get('B_split4',{}).get('destructive_signature_positive','?')}/6；ID-placebo 与 quotient control 均 3/3，Fisher p={p}。"
            why = d.get("mechanistic_interpretation", {}).get("D_quotient_control", "")
            limit = d.get("scientific_claim_boundary", "")
            ev = [{"label": k, "value": v} for k, v in g.items()] + [{"label":"Fisher p","value":p}]
            scientific = bool(d.get("authority", {}).get("dynamic_behavioral_propagation_supported"))
            scope = "bounded AutoSkill/P19 behavioral propagation only"
            title_zh = "表示方式变化经由检索传播到真实执行行为"
            research_label_zh = "STRI · AutoSkill/P19 动态行为证据"
        elif "mediator-isolation" in name:
            g = d.get("groups", {})
            en = f"Post-checkout skill add-back restored the signature in {g.get('E_post_addback',{}).get('positive','?')}/3 fresh runs; matched cleanup control was {g.get('F_cleanup_control',{}).get('positive','?')}/3; exact p={d.get('statistics',{}).get('exact_fraction','?')}."
            zh = f"post-checkout skill add-back 在 {g.get('E_post_addback',{}).get('positive','?')}/3 次 fresh run 恢复目标行为；matched cleanup control 为 {g.get('F_cleanup_control',{}).get('positive','?')}/3；exact p={d.get('statistics',{}).get('exact_fraction','?')}。"
            why, limit = d.get("scientific_interpretation", ""), d.get("claim_boundary", "")
            ev = [{"label":k,"value":v} for k,v in g.items()] + [{"label":"exact p","value":d.get("statistics",{}).get("exact_fraction")},{"label":"replay agreement","value":d.get("measurement_repair",{}).get("stage3_replay_agreement")}]
            scientific = bool(d.get("authority", {}).get("mediator_claim_supported"))
            scope = "specific mediator attribution on frozen P19 only"
            title_zh = "中介隔离实验进一步确认 P19 的因果链条"
            research_label_zh = "STRI · AutoSkill/P19 中介隔离"
        elif "post-isolation-review" in name:
            pre, post = d.get("reviews",{}).get("deepseek_pre_isolation",{}), d.get("reviews",{}).get("deepseek_post_isolation",{})
            en = f"Independent review moved from {pre.get('score_1_to_10','?')}/10 ({pre.get('recommendation','?')}) to {post.get('score_1_to_10','?')}/10 ({post.get('recommendation','?')}); current narrow claims require no further experiment score-chasing."
            zh = f"独立评审从 {pre.get('score_1_to_10','?')}/10（{pre.get('recommendation','?')}）变为 {post.get('score_1_to_10','?')}/10（{post.get('recommendation','?')}）；当前窄化主张停止继续为分数追实验。"
            why, limit = d.get("scientific_interpretation", ""), d.get("claim_boundary", "")
            ev = [{"label":"before","value":f"{pre.get('score_1_to_10','?')}/10"},{"label":"after","value":f"{post.get('score_1_to_10','?')}/10"},{"label":"fatal flaws","value":post.get("fatal_flaws")}]
            scientific, scope = False, "review adjudication; no new method/GPU authority"
            before = f"independent review {pre.get('score_1_to_10','?')}/10 · {pre.get('recommendation','?')}"
            title_zh = "中介隔离后冻结 STRI 窄化投稿范围"
        else:
            fmt, pq = d.get("official_format", {}), d.get("paper_quality_v2", {})
            en = f"Frozen ICLR package: {len(d.get('scientific_claim_scope',[]))} narrow claims, {fmt.get('main_text_pages','?')}/{fmt.get('main_text_page_limit','?')} main-text pages, paper evidence {pq.get('status','recorded')}."
            zh = f"冻结 ICLR 投稿包：{len(d.get('scientific_claim_scope',[]))} 条窄化主张，正文 {fmt.get('main_text_pages','?')}/{fmt.get('main_text_page_limit','?')} 页，paper evidence={pq.get('status','recorded')}。"
            why, limit = "", "; ".join(d.get("claims_forbidden", [])[:5])
            ev = [{"label":"official review","value":d.get("independent_reviews",{}).get("official_iclr2027_final_review",{}).get("verdict")},{"label":"supplement tests","value":d.get("delivery",{}).get("supplement_zip",{}).get("unit_tests")},{"label":"paper evidence","value":pq.get("status")}]
            scientific, scope = False, "paper-state projection; does not expand claims"
            title_zh = "STRI 达到 ICLR 正式投稿包就绪状态"
        out.append(event(occurred_at=artifact_ts(d,path), event_class=cls, importance="key", research_id=rid,
            title=d.get("title") or fallback_title, state_before=before, state_after=str(decision), summary_en=en, summary_zh=zh,
            why_en=why, why_zh=("展开查看结构化科研记录中的原始机制解释与审计证据。" if why else ""),
            limitation_en=limit, limitation_zh="该事件只在原始记录明确写出的主张边界内成立；不会由时间轴自动扩大。",
            next_action=d.get("next_action", ""), next_action_zh="按当前冻结范围继续论文提交与人工确认；除非出现独立的新证据，否则不扩大主张或重新追实验分数。",
            evidence=ev, scientific=scientific, authority_scope=scope,
            authority_scope_zh="只沿用原始记录已明确授权的窄范围；时间轴本身不新增科研权限。",
            title_zh=title_zh, research_label_zh=research_label_zh, time_precision=artifact_precision(d,path),
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
        candidate_id = d.get("candidate_id", "principle-readjudication")
        out.append(event(
            occurred_at=artifact_ts(d,path), time_precision=artifact_precision(d,path), event_class="closure", importance="key" if key else "detail",
            research_id=candidate_id, research_label_zh=str(candidate_id), title=d.get("title") or candidate_id or path.stem,
            title_zh=f"科学关闭裁决 · {candidate_id}",
            state_after=str(state), summary_en=safe or f"Scoped principle readjudication closed this formulation at {layer}.",
            summary_zh=f"该候选完成 scoped principle readjudication，并在 {layer} 层形成关闭结论。展开可查看原始 reduction、边界与重开条件。",
            why_en=reason, why_zh="该关闭来自已有证据下的 same-information / scope-matched reduction 或明确结构性裁决；不是把运行失败自动解释成科学失败。",
            limitation_en=d.get("dead_end_scope", ""), limitation_zh="关闭只作用于原始记录明确写出的具体候选表述，不自动外推到整个方向或基准。",
            reopen=reopen, reopen_zh="仅在原裁决登记的重开条件被真实新证据满足时重开；不能通过换术语、调阈值或重复同类负实验重开。",
            evidence=[{"label":"evidence","value":x} for x in refs[:6]] + [{"label":"experiment run","value":d.get("experiment_run_for_this_readjudication")},{"label":"closure layer","value":layer}],
            scientific=scientific, authority_scope=auth_scope or ("scoped principle adjudication" if scientific else "readjudication projection only"),
            authority_scope_zh="只对原始记录明确界定的具体候选表述生效；不自动关闭整个研究领域。",
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
            occurred_at=artifact_ts(d,path), time_precision=artifact_precision(d,path), event_class=cls, importance="detail", research_id=str(rid),
            research_label_zh=str(rid), title=d.get("title") or d.get("scientific_role") or str(rid), title_zh=f"P0 实验裁决 · {rid}", state_after=decision,
            summary_en=d.get("interpretation") or d.get("scientific_interpretation") or next_action or decision,
            summary_zh=f"该 P0 记录给出了明确决策：{decision}。展开查看原始指标、下一步和权限边界。",
            why_en=d.get("reason") or d.get("diagnosis") or "", why_zh="该事件直接来自已有 P0 结构化记录；时间轴只做投影，不重新裁决。",
            next_action=next_action, next_action_zh=generic_next_zh(decision), evidence=metrics(d.get("metrics") or d.get("summary") or {}), scientific=scientific,
            authority_scope="existing P0 decision artifact" if scientific else "P0/system projection; no new authority",
            authority_scope_zh="沿用原 P0 记录的已有裁决范围；时间轴不会重新授权实验或 GPU。",
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
            occurred_at=when, time_precision=artifact_precision(d,path), event_class="paper", importance="key", research_id=p.get("paper_id","STRI"), research_label_zh="STRI 当前论文状态", title=p.get("title","Leading paper track"), title_zh="STRI 当前投稿状态快照",
            state_after=p.get("submission_status") or p.get("status") or "RECORDED",
            summary_en=f"Current snapshot: {p.get('claims_supported',0)}/{p.get('claims_total',0)} narrow claims supported, QA {p.get('qa_passed',0)}/{p.get('qa_total',0)}, evidence debt {p.get('paper_quality_evidence_debt',0)}, new GPU evidence required={p.get('new_gpu_evidence_required')}.",
            summary_zh=f"当前快照：窄化主张 {p.get('claims_supported',0)}/{p.get('claims_total',0)} supported，QA {p.get('qa_passed',0)}/{p.get('qa_total',0)}，evidence debt={p.get('paper_quality_evidence_debt',0)}，new GPU evidence required={p.get('new_gpu_evidence_required')}。",
            limitation_en="Current-status is a derived projection and cannot itself expand claims.", limitation_zh="current-status 是派生投影，只汇总已有证据，不能自行扩大 claim。",
            next_action=p.get("next_action", ""), evidence=[{"label":"claims","value":f"{p.get('claims_supported',0)}/{p.get('claims_total',0)}"},{"label":"QA","value":f"{p.get('qa_passed',0)}/{p.get('qa_total',0)}"},{"label":"evidence debt","value":p.get("paper_quality_evidence_debt",0)},{"label":"human signoff pending","value":p.get("human_signoff_pending")}],
            next_action_zh="完成作者责任确认、作者列表与 OpenReview 提交；不因页面状态自动扩大 N1–N3 主张。",
            scientific=False, authority_scope="current-status projection; source claims retain their own authority", authority_scope_zh="当前状态汇总是只读投影；科研权限仍由各原始证据与裁决记录决定。", source=path,
            links=[{"label":"paper","href":"selected-paper.html"}], hint="paper-status"))
    out.append(event(
        occurred_at=when, time_precision=artifact_precision(d,path), event_class="idea", importance="key", research_id="Idea Search", research_label_zh="Idea 自动发现漏斗", title="Canonical double-funnel discovery snapshot", title_zh="Canonical 双漏斗 Idea 发现状态快照",
        state_after=f.get("pre_f0_status") or f.get("last_completed_generator_status") or "RECORDED",
        summary_en=f"Last canonical receipt: {f.get('last_completed_raw_seeds',0)} raw seeds, {f.get('last_completed_reviewer_attacks',0)} reviewer attacks, {f.get('last_completed_repair_children',0)} repair children, {f.get('pre_f0_queued',0)} Pre-F0 candidates; final Problem-Gate passes={f.get('final_problem_gate_pass',0)}.",
        summary_zh=f"最近 canonical receipt：{f.get('last_completed_raw_seeds',0)} 个 raw seed、{f.get('last_completed_reviewer_attacks',0)} 次 reviewer attack、{f.get('last_completed_repair_children',0)} 个 repair child、{f.get('pre_f0_queued',0)} 个 Pre-F0 候选；正式 Problem-Gate pass={f.get('final_problem_gate_pass',0)}。",
        why_en="Pre-F0 is evidence acquisition, not paper/method/experiment/P0/GPU authority.", why_zh="Pre-F0 只是证据获取阶段，不等于 Paper/Method/Experiment/P0/GPU 授权。",
        limitation_en="The discovery funnel explicitly carries zero scientific authority.", limitation_zh="该 Idea 发现漏斗明确没有科研权限；候选数量不能当成科研结论。",
        evidence=[{"label":"raw seeds","value":f.get("last_completed_raw_seeds",0)},{"label":"Pre-F0 queued","value":f.get("pre_f0_queued",0)},{"label":"support ready","value":f.get("pre_f0_support_ready",0)},{"label":"support holds","value":f.get("pre_f0_support_holds",0)},{"label":"formal launchable","value":h.get("launchable_formal_experiments",0)}],
        next_action_zh="继续按 raw seed → 去重 → reviewer attack/repair → pre-F0 → exact reduction → Problem Gate 推进；未通过正式 Problem Gate 的候选不进入方法或实验。",
        scientific=False, authority_scope="zero-authority discovery/search control", authority_scope_zh="Idea 搜索与 pre-F0 都是零科研权限阶段；候选数量和评审器输出不能直接授权实验。", source=path,
        links=[{"label":"research","href":"paper-ideas.html"},{"label":"system","href":"system-overview.html"}], hint="discovery-status"))
    return out

def artifact_state(data: dict[str, Any]) -> str:
    for key in ("decision", "verdict", "formal_outcome", "status", "stage", "outcome", "disposition"):
        value = data.get(key)
        if isinstance(value, (str, int, float, bool)) and str(value).strip():
            return str(value)
    return "ARTIFACT_RECORDED"


def artifact_identity(path: Path, data: dict[str, Any]) -> str:
    for key in ("candidate_id", "paper_id", "experiment_id", "idea_id", "run_id", "code", "id", "title", "name"):
        value = data.get(key)
        if isinstance(value, (str, int)) and str(value).strip():
            return text(value, 160)
    return path.stem


def artifact_event_class(path: Path, state: str) -> str:
    name = path.name.lower()
    u = state.upper()
    if any(x in u for x in ("STOP", "TERMINAT", "DEAD_END", "REJECT", "FAIL")):
        return "closure"
    if any(x in u for x in ("HOLD", "BLOCK", "WAIT", "PENDING", "INCONCLUSIVE", "INSUFFICIENT")):
        return "blocker"
    if any(x in name for x in ("p0", "f0", "experiment", "qualification", "substrate", "execution", "result", "falsifier")):
        return "experiment"
    if any(x in name for x in ("submission", "openreview", "supplement", "format-state", "paper-quality", "paper-design", "paper-coherence", "narrow-paper", "stri-iclr", "final-review")):
        return "paper"
    if any(x in name for x in ("idea", "problem", "advisor", "discovery", "portfolio", "discussion", "gate-queue", "search")):
        return "idea"
    return "system"


def generic_type_zh(event_class: str) -> str:
    return {
        "idea": "Idea / 问题发现记录",
        "experiment": "实验与验证记录",
        "paper": "论文推进记录",
        "closure": "停止 / 关闭裁决",
        "blocker": "暂缓 / 阻断记录",
        "scientific": "科研结论记录",
        "system": "系统与治理记录",
    }.get(event_class, "研究记录")


def generic_next_zh(state: str) -> str:
    u = state.upper()
    if any(x in u for x in ("STOP", "TERMINAT", "DEAD_END", "REJECT", "FAIL")):
        return "当前路线不继续推进；只有满足原 artifact 记录的新证据或重开条件时才恢复。"
    if any(x in u for x in ("HOLD", "BLOCK", "WAIT", "PENDING", "INCONCLUSIVE", "INSUFFICIENT")):
        return "等待缺失证据、运行条件或上游门槛满足；不能把暂缓状态当成已成立结论。"
    if any(x in u for x in ("READY", "PASS", "ADVANCE", "GO_", "SUPPORTED", "CLEAR")):
        return "按原治理流程进入下一阶段；后续阶段仍需各自的独立授权。"
    return "保留该条结构化记录，供后续时间追踪、审计和状态对齐使用。"


def generic_artifact_events() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for path in sorted(GEN.glob("*.json")):
        name = path.name
        if name == "research-timeline.json" or name == "current-research-status.json":
            continue
        if name in CURATED_STRI_FILES or "principle-readjudication" in name:
            continue
        data = load(path)
        if not data:
            continue
        if name.startswith("p0-") and any(isinstance(data.get(key), str) and data.get(key).strip() for key in ("decision", "verdict", "formal_outcome")):
            continue
        occurred = artifact_ts(data, path)
        if not occurred:
            continue
        state = artifact_state(data)
        cls = artifact_event_class(path, state)
        rid = artifact_identity(path, data)
        kind_zh = generic_type_zh(cls)
        original_title = data.get("title") if isinstance(data.get("title"), str) else ""
        summary_source = ""
        for key in ("scientific_interpretation", "interpretation", "reason", "conclusion", "next_action", "summary", "role"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                summary_source = value
                break
        state_label = state_cn(state)
        summary_zh = f"{kind_zh}已生成或更新。当前状态：{state_label}。这条记录用于补齐完整研究历史，原始技术状态码仍保留用于审计。"
        title_zh = f"{kind_zh} · {rid}"
        if original_title and any('\u4e00' <= ch <= '\u9fff' for ch in original_title):
            title_zh = original_title
        evidence = [{"label": "原始状态码", "value": state}] + collection_metrics(data)
        original_next = data.get("next_action") if isinstance(data.get("next_action"), str) else ""
        original_reopen = data.get("reopen_condition") if isinstance(data.get("reopen_condition"), str) else ""
        out.append(event(
            occurred_at=occurred,
            time_precision=artifact_precision(data, path),
            event_class=cls,
            importance="detail",
            research_id=rid,
            research_label_zh=rid,
            title=original_title or path.stem,
            title_zh=title_zh,
            state_after=state,
            summary_en=summary_source or f"Structured artifact recorded: {path.name}.",
            summary_zh=summary_zh,
            why_en=summary_source,
            why_zh="该条目直接来自现有结构化科研记录；中文视图优先展示阶段含义，英文技术原文与状态码保留用于精确审计。" ,
            limitation_en="This full-history projection does not create scientific authority beyond the source artifact.",
            limitation_zh="这是完整历史投影，不会因为被加入时间轴而增加科研权限，也不会把工程/运行失败自动改写成科学失败。",
            next_action=original_next,
            next_action_zh=generic_next_zh(state),
            reopen=original_reopen,
            reopen_zh="若原记录包含明确重开条件，以原记录为准；没有明确条件时，不根据时间轴自动重开。" if not original_reopen else "按原始记录中登记的重开条件执行；时间轴不自行放宽条件。",
            evidence=evidence,
            scientific=False,
            authority_scope="full-history artifact projection only",
            authority_scope_zh="完整历史只读投影；不新增方法、实验、P0、GPU 或论文主张权限。",
            source=path,
            links=[{"label":"研究方向","href":"paper-ideas.html"}] if cls in {"idea","closure","blocker"} else ([{"label":"实验","href":"experiments.html"}] if cls == "experiment" else ([{"label":"论文","href":"selected-paper.html"}] if cls == "paper" else [{"label":"科研系统","href":"system-overview.html"}])),
            hint=f"full-history:{name}",
            origin="artifact_full_history",
        ))
    return out


def git_title_zh(message: str) -> str:
    m = message.lower()
    if "deploy agent self-evolution observatory" in m: return "首次部署 Agent Self-Evolution Observatory"
    if "github pages" in m and "deploy" in m: return "建立并触发网站部署流程"
    if "comprehensive multi-page research map" in m: return "重构为完整多页面研究地图"
    if "bibliography" in m or "literature" in m: return "完善动态文献库与文献证据"
    if "cvpr" in m and "idea" in m: return "扩展 CVPR 研究 Idea 组合"
    if "iclr-first" in m: return "科研流程切换为 ICLR 优先"
    if "continuous" in m and "research" in m: return "加入持续自校准科研后端"
    if "publication" in m or "publishing" in m: return "建立自动科研状态发布链路"
    if "audit" in m: return "完成研究方向 / 候选审计"
    if "oracle" in m: return "推进 Oracle 独立评审"
    if "idea" in m or "portfolio" in m: return "扩展并整理研究 Idea 组合"
    if "hierarchy" in m or "framework" in m: return "完善研究页面层级与框架"
    return f"系统建设里程碑：{message}"


def git_is_shallow() -> bool:
    if os.getenv("RESEARCH_TIMELINE_FORCE_SHALLOW", "").strip() == "1":
        return True
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--is-shallow-repository"],
            cwd=ROOT, text=True, capture_output=True, timeout=10, check=False,
        )
    except OSError:
        return True
    return completed.returncode != 0 or completed.stdout.strip().lower() == "true"


def preserved_origin_events(origin: str) -> list[dict[str, Any]]:
    previous = load(GEN / "research-timeline.json")
    rows = previous.get("events") if isinstance(previous, dict) else []
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict) and row.get("origin") == origin]


def early_git_milestones() -> list[dict[str, Any]]:
    if git_is_shallow():
        return preserved_origin_events("git_early_history")
    try:
        completed = subprocess.run(
            ["git", "log", "--reverse", "--until=2026-08-05T23:59:59+08:00", "--format=%H%x09%cI%x09%s"],
            cwd=ROOT, text=True, capture_output=True, timeout=30, check=False,
        )
    except OSError:
        return []
    if completed.returncode != 0:
        return []
    out: list[dict[str, Any]] = []
    for line in completed.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        commit, when, message = parts
        cls = "idea" if re.search(r"idea|portfolio|audit|oracle|iclr|cvpr", message, re.I) else "system"
        title_zh = git_title_zh(message)
        out.append(event(
            occurred_at=ts(when), time_precision="exact", event_class=cls, importance="detail",
            research_id="Observatory 建设", research_label_zh="Observatory 早期建设",
            title=message, title_zh=title_zh, state_after="COMMIT_RECORDED",
            summary_en=f"Early project milestone commit {commit[:8]}: {message}",
            summary_zh=f"项目早期建设里程碑，提交 {commit[:8]}：{title_zh}。",
            why_en="Included to cover the project history before structured generated artifacts became available.",
            why_zh="结构化科研记录从 8 月初才逐步稳定，因此用 Git 提交补齐系统创建到结构化记录出现之前的历史。",
            limitation_en="Engineering/history milestone only; no scientific authority.",
            limitation_zh="仅用于补齐系统建设历史，不代表科学结论或实验授权。",
            evidence=[{"label":"提交", "value":commit[:12]}], scientific=False,
            authority_scope="engineering history only", authority_scope_zh="工程 / 系统历史记录，无科研权限。",
            hint=f"git:{commit}", origin="git_early_history",
        ))
    return out


GIT_RELEVANT_RE = re.compile(
    r"system|backend|frontend|memory|governance|aris|page|timeline|workflow|pipeline|publication|automation|deploy|operator|control|state|website|idea|discovery|problem|candidate|portfolio|funnel|paper|submission|manuscript|experiment|\bp0\b|\bf0\b|evidence|review|audit|closure|stop",
    re.I,
)


def git_commit_class(message: str) -> str:
    m = message.lower()
    # Code/control-plane changes stay visible as system updates even when the page
    # being changed is about ideas or papers; this makes idea -> system-change
    # sequences legible in the chronological view.
    if re.search(r"system|backend|frontend|memory|governance|aris|page|timeline|workflow|pipeline|publication|automation|deploy|operator|control|state|website", m):
        return "system"
    if re.search(r"closure|readjudicat|dead.?end|stop|terminat", m):
        return "closure"
    if re.search(r"idea|discovery|problem|candidate|portfolio|funnel", m):
        return "idea"
    if re.search(r"experiment|\bp0\b|\bf0\b|evidence|result|benchmark|run", m):
        return "experiment"
    if re.search(r"paper|submission|manuscript|iclr|review", m):
        return "paper"
    return "system"


def git_relevant_history_events() -> list[dict[str, Any]]:
    if git_is_shallow():
        return preserved_origin_events("git_relevant_history")
    try:
        completed = subprocess.run(
            ["git", "log", "--reverse", "--since=2026-07-28T00:00:00+08:00", "--format=%H%x09%cI%x09%s"],
            cwd=ROOT, text=True, capture_output=True, timeout=30, check=False,
        )
    except OSError:
        return []
    if completed.returncode != 0:
        return []
    out: list[dict[str, Any]] = []
    for line in completed.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        commit, when, message = parts
        if not GIT_RELEVANT_RE.search(message):
            continue
        cls = git_commit_class(message)
        kind = {
            "idea":"Idea / 研究问题",
            "experiment":"实验 / 证据",
            "paper":"论文 / 评审",
            "closure":"关闭 / 裁决",
            "system":"系统 / 流程更新",
        }.get(cls, "系统更新")
        title_zh = git_title_zh(message) if cls == "system" else f"{kind}相关提交：{message}"
        out.append(event(
            occurred_at=ts(when), time_precision="exact", event_class=cls, importance="detail",
            research_id="Git research history", research_label_zh="代码 / 系统工作记录",
            title=message, title_zh=title_zh, state_after="COMMIT_RECORDED",
            summary_en=f"Repository commit {commit[:8]} recorded: {message}",
            summary_zh=f"北京时间记录到一次与{kind}有关的真实仓库提交 {commit[:8]}：{message}。它用于把科研对象的变化和随后发生的系统实现更新放在同一时间线上。",
            why_en="Included as a concrete implementation/history event so research ideas and subsequent system changes can be read in temporal order.",
            why_zh="该提交作为真实实现时间点进入时间轴，用来帮助判断某个 Idea、证据或裁决之后，系统为何发生了相应改动。",
            limitation_en="A repository commit is engineering evidence, not scientific authority.",
            limitation_zh="Git 提交只能证明工程 / 系统工作发生过，不能单独证明科研主张成立。",
            evidence=[{"label":"提交", "value":commit[:12]},{"label":"原始提交说明", "value":message}],
            scientific=False, authority_scope="repository history only", authority_scope_zh="代码与系统历史记录，无科研权限。",
            hint=f"git-relevant:{commit}", origin="git_relevant_history",
        ))
    return out


def git_daily_activity_events() -> list[dict[str, Any]]:
    if git_is_shallow():
        return preserved_origin_events("git_daily_summary")
    try:
        completed = subprocess.run(
            ["git", "log", "--since=2026-08-06T00:00:00+08:00", "--format=%H%x09%cI%x09%s"],
            cwd=ROOT, text=True, capture_output=True, timeout=30, check=False,
        )
    except OSError:
        return []
    if completed.returncode != 0:
        return []
    by_day: dict[str, list[tuple[str, str, str]]] = {}
    for line in completed.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        commit, when, message = parts
        day = china_date(ts(when))
        by_day.setdefault(day, []).append((commit, when, message))
    out: list[dict[str, Any]] = []
    for day, rows in sorted(by_day.items()):
        latest = rows[0]
        samples = [message for _, _, message in rows[:4]]
        out.append(event(
            occurred_at=ts(latest[1]), time_precision="exact", event_class="system", importance="detail",
            research_id="每日系统活动", research_label_zh="每日系统 / 工程活动汇总",
            title=f"Daily repository activity summary · {day}", title_zh=f"{day} 系统活动汇总 · {len(rows)} 次提交",
            state_after="DAILY_ACTIVITY_RECORDED",
            summary_en=f"{len(rows)} repository commits were recorded on {day}. Representative changes: {'; '.join(samples)}",
            summary_zh=f"北京时间 {day} 共记录 {len(rows)} 次仓库提交。该日即使没有单独生成结构化科研记录，也保留一条系统活动摘要，避免完整时间轴出现人为断档。",
            why_en="Daily engineering summary fills dates where research/system work happened but no standalone generated artifact carries that date.",
            why_zh="用于补齐“当天确实有研究系统工作，但没有独立结构化科研记录”的日期；它只说明系统活动，不代表新的科研结论。",
            limitation_en="Engineering activity only; commit count is not scientific progress authority.",
            limitation_zh="仅为系统 / 工程活动摘要，提交次数不能解释为科研质量或科学结论。",
            evidence=[{"label":"提交次数", "value":len(rows)},{"label":"最新提交", "value":latest[0][:12]},{"label":"代表变更", "value":"；".join(samples)}],
            scientific=False, authority_scope="engineering activity summary only", authority_scope_zh="工程活动汇总，无科研权限。",
            hint=f"daily-git:{day}", origin="git_daily_summary",
        ))
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
                occurred_at=ts(run["imported_at"]), time_precision="exact", event_class="system", importance="key", research_id="Research Memory", research_label_zh="科研记忆 / 追溯",
                title="Append-only research run imported into Research Memory", title_zh="新的科研运行记录写入 Research Memory", state_after=run["status"],
                summary_en=f"Run {rid}: {run['call_count']} API calls, {run['object_count']} research objects, {edges} lineage edges, {ready} preflight-ready objects.",
                summary_zh=f"run {rid} 已写入 Research Memory：{run['call_count']} 次 API call、{run['object_count']} 个 research object、{edges} 条 lineage，以及 {ready} 个 preflight-ready object。",
                why_en="This is provenance/search progress only. The memory schema fixes scientific_authority=0 and belief_authority=0 for imported API/research-memory rows.",
                why_zh="该事件只表示追溯与搜索系统进度。数据库对这些 API 与 Research Memory 记录硬性约束科研权限=0、信念更新权限=0。",
                limitation_en="Preflight readiness is not a Problem-Gate pass and cannot authorize experiments or update scientific belief by itself.",
                limitation_zh="preflight readiness 不等于 Problem-Gate pass，也不能单独授权实验或改变 scientific belief。",
                next_action="Use preflight contracts only after normal governance and scientific authorization checks succeed.",
                next_action_zh="只有通过正常 governance 与科研授权后，preflight contract 才能继续进入后续实验流程。",
                evidence=ev, scientific=False, authority_scope="runtime/provenance memory only; schema-enforced zero scientific and belief authority", authority_scope_zh="仅为运行时 / 追溯科研记忆；数据库层强制科研权限=0、信念更新权限=0。",
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


def dated_artifact_count() -> int:
    total = 0
    for path in GEN.glob("*.json"):
        if path.name == "research-timeline.json":
            continue
        data = load(path)
        if not data:
            continue
        dated = any(isinstance(data.get(key), str) and data.get(key).strip() for key in ("generated_at", "adjudication_date", "decision_date", "completed_at", "created_at", "updated_at"))
        if dated or DATE_RE.search(path.name):
            total += 1
    return total


def _alias_key(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def _canonical_binding_index() -> dict[str, Any]:
    research = load(GEN / "research-items.json")
    registry = load(GEN / "paper-registry.json")
    items = research.get("research_items", []) if isinstance(research, dict) else []
    experiments = research.get("experiment_records", []) if isinstance(research, dict) else []
    papers = registry.get("papers", []) if isinstance(registry, dict) else []

    item_by_code = {str(row.get("code")): row for row in items if row.get("code")}
    exp_by_id = {str(row.get("experiment_id")): row for row in experiments if row.get("experiment_id")}
    paper_by_id = {str(row.get("paper_id")): row for row in papers if row.get("paper_id")}
    item_aliases: dict[str, set[str]] = {}
    exp_aliases: dict[str, set[str]] = {}
    paper_aliases: dict[str, set[str]] = {}
    source_items: dict[str, set[str]] = {}
    source_experiments: dict[str, set[str]] = {}
    source_papers: dict[str, set[str]] = {}

    def add(mapping: dict[str, set[str]], alias: Any, value: str) -> None:
        key = _alias_key(alias)
        if key:
            mapping.setdefault(key, set()).add(value)

    def add_source(mapping: dict[str, set[str]], path_value: Any, value: str) -> None:
        path = str(path_value or "").strip()
        if path:
            mapping.setdefault(path, set()).add(value)

    for row in items:
        code = str(row.get("code") or "")
        if not code:
            continue
        add(item_aliases, code, code)
        add(item_aliases, row.get("id"), code)
        title = row.get("title") or {}
        if isinstance(title, dict):
            add(item_aliases, title.get("en"), code)
            add(item_aliases, title.get("zh"), code)
        for ref in row.get("provenance_refs") or []:
            if isinstance(ref, dict):
                add_source(source_items, ref.get("path"), code)

    for row in experiments:
        eid = str(row.get("experiment_id") or "")
        if not eid:
            continue
        add(exp_aliases, eid, eid)
        add(exp_aliases, row.get("portfolio_code"), eid)
        for ref in row.get("provenance_refs") or []:
            if isinstance(ref, dict):
                add_source(source_experiments, ref.get("path"), eid)
        for artifact in row.get("artifacts") or []:
            add_source(source_experiments, artifact, eid)

    for row in papers:
        pid = str(row.get("paper_id") or "")
        if not pid:
            continue
        add(paper_aliases, pid, pid)
        add(paper_aliases, row.get("acceptance_paper_id"), pid)
        add(paper_aliases, row.get("title"), pid)
        for ref in row.get("provenance_refs") or []:
            if isinstance(ref, dict):
                add_source(source_papers, ref.get("path"), pid)

    return {
        "item_by_code": item_by_code,
        "exp_by_id": exp_by_id,
        "paper_by_id": paper_by_id,
        "item_aliases": item_aliases,
        "exp_aliases": exp_aliases,
        "paper_aliases": paper_aliases,
        "source_items": source_items,
        "source_experiments": source_experiments,
        "source_papers": source_papers,
    }


def bind_canonical_refs(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    index = _canonical_binding_index()
    item_by_code = index["item_by_code"]
    exp_by_id = index["exp_by_id"]
    paper_by_id = index["paper_by_id"]
    code_re = re.compile(r"(?<![A-Z0-9])([A-G]-\d+)(?![A-Z0-9])", re.I)

    def exact(mapping: dict[str, set[str]], value: Any) -> set[str]:
        return set(mapping.get(_alias_key(value), set()))

    for row in items:
        research_codes: set[str] = set()
        experiment_ids: set[str] = set()
        paper_ids: set[str] = set()
        identity_text = " | ".join(str(row.get(key) or "") for key in ("research_id", "title", "title_zh"))
        research_codes.update(code.upper() for code in code_re.findall(identity_text) if code.upper() in item_by_code)
        research_codes.update(exact(index["item_aliases"], row.get("research_id")))
        experiment_ids.update(exact(index["exp_aliases"], row.get("research_id")))
        paper_ids.update(exact(index["paper_aliases"], row.get("research_id")))

        for alias, values in index["item_aliases"].items():
            if len(alias) >= 8 and alias in _alias_key(identity_text):
                research_codes.update(values)
        for alias, values in index["exp_aliases"].items():
            if len(alias) >= 7 and alias in _alias_key(identity_text):
                experiment_ids.update(values)
        for alias, values in index["paper_aliases"].items():
            if len(alias) >= 6 and alias in _alias_key(identity_text):
                paper_ids.update(values)

        for source in row.get("sources") or []:
            if not isinstance(source, dict) or source.get("public") is False:
                continue
            path = str(source.get("path") or "")
            if path in AGGREGATE_BINDING_SOURCES:
                continue
            item_hits = index["source_items"].get(path, set())
            exp_hits = index["source_experiments"].get(path, set())
            paper_hits = index["source_papers"].get(path, set())
            if len(item_hits) == 1:
                research_codes.update(item_hits)
            if len(exp_hits) == 1:
                experiment_ids.update(exp_hits)
            if len(paper_hits) == 1:
                paper_ids.update(paper_hits)

        # Curated named research lines use stable public aliases even when the
        # underlying historical artifacts predate ResearchItemState.
        if re.search(r"\bSTRI\b", identity_text, re.I):
            if "E-7" in item_by_code:
                research_codes.add("E-7")
            if "STRI" in paper_by_id:
                paper_ids.add("STRI")
        if re.search(r"AGENT[- ]?SAFETY|first[- ]violation hazard", identity_text, re.I):
            if "G-1" in item_by_code:
                research_codes.add("G-1")
            if "AGENT-SAFETY-R9" in paper_by_id:
                paper_ids.add("AGENT-SAFETY-R9")

        for eid in list(experiment_ids):
            parent = str((exp_by_id.get(eid) or {}).get("research_item_code") or "")
            if parent in item_by_code:
                research_codes.add(parent)
        for pid in list(paper_ids):
            parent = str((paper_by_id.get(pid) or {}).get("source_research_item") or "")
            if parent in item_by_code:
                research_codes.add(parent)

        research_refs = []
        for code in sorted(research_codes):
            item = item_by_code.get(code) or {}
            title = item.get("title") or {}
            research_refs.append({
                "code": code,
                "id": item.get("id") or code,
                "category": item.get("category") or code.split("-", 1)[0],
                "title_zh": title.get("zh") if isinstance(title, dict) else "",
                "title_en": title.get("en") if isinstance(title, dict) else "",
                "scientific_state": item.get("scientific_state") or "",
            })
        experiment_refs = []
        for eid in sorted(experiment_ids):
            exp = exp_by_id.get(eid) or {}
            experiment_refs.append({
                "experiment_id": eid,
                "research_item_code": exp.get("research_item_code") or "",
                "portfolio_code": exp.get("portfolio_code") or "",
                "status": (exp.get("result") or {}).get("status") or "",
            })
        paper_refs = []
        for pid in sorted(paper_ids):
            paper = paper_by_id.get(pid) or {}
            paper_refs.append({
                "paper_id": pid,
                "source_research_item": paper.get("source_research_item") or "",
                "paper_stage": paper.get("paper_stage") or paper.get("current_state") or "",
                "scientific_status": paper.get("scientific_status") or "",
                "submission_ready": bool(paper.get("submission_ready")),
            })
        row["canonical_refs"] = {
            "research_items": research_refs,
            "experiments": experiment_refs,
            "papers": paper_refs,
            "categories": sorted({ref["category"] for ref in research_refs if ref.get("category")}),
        }
        links = row.setdefault("links", [])
        existing = {(str(link.get("label")), str(link.get("href"))) for link in links if isinstance(link, dict)}
        for ref in research_refs:
            href = f"paper-ideas.html?research={ref['code']}#canonical-group-{ref['category'].lower()}"
            key = (f"ResearchItem {ref['code']}", href)
            if key not in existing:
                links.append({"label": key[0], "href": href})
                existing.add(key)
        for ref in paper_refs:
            href = f"selected-paper.html?paper={ref['paper_id']}"
            key = (f"Paper {ref['paper_id']}", href)
            if key not in existing:
                links.append({"label": key[0], "href": href})
                existing.add(key)
    return items


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
    items = bind_canonical_refs(dedupe(git_relevant_history_events() + generic_artifact_events() + stri_events() + principle_events() + p0_events() + current_status_events() + runtime))
    classes = Counter(x["event_class"] for x in items)
    dates = Counter(china_date(x["occurred_at"]) for x in items)
    return {
        "schema_version":"1.1",
        "generated_at":max((x["occurred_at"] for x in items), default=""),
        "projection_policy":{
            "read_only":True,
            "display_timezone":"Asia/Shanghai",
            "display_timezone_label":"北京时间（UTC+8）",
            "full_history_default":True,
            "projection_has_scientific_authority":False,
            "zero_authority_runtime_rows_remain_zero_authority":True,
            "execution_or_provenance_failure_is_not_scientific_failure":True,
            "collapsed_summary_never_replaces_source_artifact":True,
            "before_state_is_omitted_when_not_explicitly_recorded":True,
            "canonical_entity_bindings_are_read_only":True,
        },
        "summary":{
            "events":len(items),
            "dated_structured_artifacts_projected":dated_artifact_count(),
            "runtime_memory_source":runtime_source,
            "runtime_memory_events":sum(x.get("origin") == "research_memory_db" or x.get("research_id") == "Research Memory" for x in items),
            "key_events":sum(x["importance"]=="key" for x in items),
            "authority_bearing_scoped_events":sum(bool(x["authority"]["scientific"]) for x in items),
            "canonical_research_bound_events":sum(bool((x.get("canonical_refs") or {}).get("research_items")) for x in items),
            "canonical_experiment_bound_events":sum(bool((x.get("canonical_refs") or {}).get("experiments")) for x in items),
            "canonical_paper_bound_events":sum(bool((x.get("canonical_refs") or {}).get("papers")) for x in items),
            "canonical_research_items_with_events":len({ref.get("code") for x in items for ref in (x.get("canonical_refs") or {}).get("research_items",[]) if ref.get("code")}),
            "canonical_papers_with_events":len({ref.get("paper_id") for x in items for ref in (x.get("canonical_refs") or {}).get("papers",[]) if ref.get("paper_id")}),
            "days":len(dates),
            "class_counts":dict(sorted(classes.items())),
            "date_counts":dict(sorted(dates.items(), reverse=True)),
        },
        "events":items,
    }


def _localized(value: Any, lang: str = "zh") -> str:
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("en") or value.get("zh") or "").strip()
    return str(value or "").strip()


def _compact_public(value: Any, limit: int = 220) -> str:
    text = re.sub(r"\s+", " ", _localized(value, "zh")).strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _dashboard_href(code: str = "", paper_id: str = "") -> str:
    if paper_id:
        return f"research-timeline.html?paper={paper_id}"
    if code:
        return f"research-timeline.html?research={code}"
    return "research-timeline.html"


def build_dashboard(timeline: dict[str, Any]) -> dict[str, Any]:
    """Compile a tiny read-only human dashboard from canonical public projections.

    This is presentation-only. It does not create a new research state machine:
    ResearchItem, PaperRegistry, and Research Timeline remain the authorities.
    """
    research = load(GEN / "research-items.json")
    registry = load(GEN / "paper-registry.json")
    research_items = [row for row in research.get("research_items", []) if isinstance(row, dict)]
    papers = [row for row in registry.get("papers", []) if isinstance(row, dict)]
    papers_by_source = {str(row.get("source_research_item")): row for row in papers if row.get("source_research_item")}
    state_counts = Counter(str(row.get("scientific_state") or "UNKNOWN") for row in research_items)

    attention = [row for row in research_items if row.get("scientific_state") in {"PAPER_READY", "HOLD"}]
    category_order = {key: index for index, key in enumerate("ABCDEFG")}

    def attention_rank(row: dict[str, Any]) -> tuple[Any, ...]:
        state = str(row.get("scientific_state") or "")
        has_paper = bool(row.get("paper_transition") or papers_by_source.get(str(row.get("code") or "")))
        return (
            0 if state == "PAPER_READY" else 1 if has_paper else 2,
            category_order.get(str(row.get("category") or ""), 99),
            str(row.get("code") or ""),
        )

    attention.sort(key=attention_rank)
    briefing_zh = {
        "E-7": "3/3 条窄主张已有对应证据；科研对象已交给论文流程，现在只做定向修稿与投稿门禁，不再自动开新实验。",
        "G-1": "长期安全问题仍开放，但当前 backbone/runtime 不能稳定提供足够的“当前安全”冻结状态，因果比较暂时没有合格样本。",
        "A-3": "当前 updater/substrate 几乎产不出有效候选更新；先换一个能稳定产生真实更新的底座，再评价回归面板。",
        "B-2": "现有记忆数据没有足够“删掉一条记忆会改变最终结论”的案例；先补专门的 deletion-sensitivity 数据。",
        "B-3": "严格 fresh contract 下独立可执行的共检索组合还不够；先换到能提供足够新场景的数据环境。",
        "E-1": "当前 paired-edit 表里不同编辑大多效果打平，排序器没有可靠可学信号；先重建真正有差异的干预表。",
    }
    briefing_en = {
        "E-7": "All 3/3 narrow claims are evidence-backed. The research object is now in the paper workflow, so the current job is manuscript repair and submission gating rather than new experiments.",
        "G-1": "The longitudinal-safety question remains open, but the current backbone/runtime cannot reliably supply enough currently-safe frozen states for a fair causal comparison.",
        "A-3": "The current updater/substrate rarely produces effective candidate updates. Qualify a genuinely effective update surface before evaluating the regression panel.",
        "B-2": "The current memory table lacks enough cases where deleting one memory changes the final conclusion. A dedicated deletion-sensitivity dataset is needed first.",
        "B-3": "The strict fresh contract still lacks enough independent executable co-retrieval combinations. A new substrate with sufficient unseen scenarios is needed first.",
        "E-1": "Edit effects in the current paired table are mostly tied, leaving too little ranking signal. Rebuild the intervention table before training a ranker.",
    }
    next_step_zh = {
        "E-7": "完成 STRI Targeted Repair → Claim Audit → PDF QA → Prebuttal → Submission Ready。",
        "G-1": "换用全新预注册 backbone/runtime，先获得足够多通过同一安全资格测试的冻结状态，再碰 held-out future。",
        "A-3": "先找到通过 updater competence 的新 update substrate/action stream，再冻结新的 candidate × validation。",
        "B-2": "独立收集至少 30 个可重复的 conclusion-changing deletion cases，再重开选择器实验。",
        "B-3": "准备至少 6 个独立、未见的 fresh pair-target unit，再重开共检索交互测试。",
        "E-1": "先构造有真实非并列 edit effect 的新 paired intervention table，再训练或比较 ranker。",
    }
    next_step_en = {
        "E-7": "Complete STRI Targeted Repair → Claim Audit → PDF QA → Prebuttal → Submission Ready.",
        "G-1": "Use a fresh preregistered backbone/runtime, obtain enough states that pass the same current-safety qualification, then consider held-out future probes.",
        "A-3": "Qualify a new update substrate/action stream for updater competence, then freeze a new candidate × validation contract.",
        "B-2": "Collect at least 30 reproducible conclusion-changing deletion cases before reopening the selector experiment.",
        "B-3": "Prepare at least six independent unseen fresh pair-target units before reopening the co-retrieval interaction test.",
        "E-1": "Build a new paired intervention table with genuinely non-tied edit effects before training or comparing the ranker.",
    }
    attention_rows = []
    for row in attention:
        code = str(row.get("code") or "")
        paper = papers_by_source.get(code) or {}
        paper_stage = str(paper.get("paper_stage") or paper.get("current_state") or "")
        row_action = dict(row.get("primary_next_action") or {})
        paper_action = dict(paper.get("primary_next_action") or {})
        row_briefing_zh = briefing_zh.get(code, _compact_public(row.get("decision_reason"), 180))
        row_briefing_en = briefing_en.get(code, _compact_public(row.get("decision_reason"), 180))
        row_next_zh = next_step_zh.get(code, _compact_public(row.get("reopen_condition"), 180))
        row_next_en = next_step_en.get(code, _compact_public(row.get("reopen_condition"), 180))
        if code == "E-7" and paper_stage == "SUBMISSION_READY" and paper.get("submission_ready") is True:
            row_briefing_zh = "3/3 条窄主张已有对应证据，Story Search、双 Mock PC、Claim Audit、Manuscript CI、PDF QA 与 Prebuttal 已闭环；STRI 已达到 canonical Submission Ready。"
            row_briefing_en = "All 3/3 narrow claims are evidence-backed and Story Search, both Mock PC modes, Claim Audit, Manuscript CI, PDF QA, and Prebuttal are closed; STRI is canonically Submission Ready."
            row_next_zh = str(paper_action.get("action_zh") or row_action.get("action_zh") or "内部 Research OS 已无新增科研、实验或论文修复动作；保持冻结证据与主张边界即可。")
            row_next_en = str(paper_action.get("action") or row_action.get("action") or "No further internal research, experiment, or paper-repair action is required; keep the frozen evidence and claim boundary.")
        attention_rows.append({
            "code": code,
            "category": str(row.get("category") or ""),
            "title": row.get("title") or {},
            "scientific_state": str(row.get("scientific_state") or ""),
            "decision_code": str(row.get("decision_code") or ""),
            "briefing_zh": row_briefing_zh,
            "briefing_en": row_briefing_en,
            "next_step_zh": row_next_zh,
            "next_step_en": row_next_en,
            "primary_next_action": row_action,
            "next_action_class": str(row_action.get("action_class") or ""),
            "paper_next_action_class": str(paper_action.get("action_class") or ""),
            "current_reason_zh": _compact_public(row.get("decision_reason"), 230),
            "reopen_condition_zh": _compact_public(row.get("reopen_condition"), 210),
            "paper_id": str(paper.get("paper_id") or ""),
            "paper_stage": paper_stage,
            "paper_scientific_status": str(paper.get("scientific_status") or ""),
            "submission_ready": bool(paper.get("gate_clean_submission_ready", paper.get("submission_ready"))) if paper else False,
            "ledger_submission_ready": bool(paper.get("submission_ready")) if paper else False,
            "portfolio_href": f"paper-ideas.html?research={code}" if code else "paper-ideas.html",
            "timeline_href": _dashboard_href(code=code),
            "paper_href": f"selected-paper.html?paper={paper.get('paper_id')}" if paper.get("paper_id") else "",
        })

    research_handoffs = sum(row.get("next_action_class") == "PAPERSTATE_HANDOFF" for row in attention_rows)
    research_waiting_reopen = sum(row.get("next_action_class") == "REOPEN_CONDITION_REQUIRED" for row in attention_rows)
    machine_actionable_attention = sum((row.get("primary_next_action") or {}).get("machine_actionable") is True for row in attention_rows)

    paper_rows = []
    for row in papers:
        source = str(row.get("source_research_item") or "")
        paper_rows.append({
            "paper_id": str(row.get("paper_id") or ""),
            "source_research_item": source,
            "title": str(row.get("title") or row.get("paper_id") or ""),
            "paper_stage": str(row.get("paper_stage") or row.get("current_state") or ""),
            "scientific_status": str(row.get("scientific_status") or ""),
            "submission_ready": bool(row.get("gate_clean_submission_ready", row.get("submission_ready"))),
            "ledger_submission_ready": bool(row.get("submission_ready")),
            "gate_clean_submission_ready": bool(row.get("gate_clean_submission_ready", row.get("submission_ready"))),
            "immediate_submission_hold": bool(row.get("immediate_submission_hold")),
            "primary_next_action": dict(row.get("primary_next_action") or {}),
            "next_action_class": str((row.get("primary_next_action") or {}).get("action_class") or ""),
            "next_action": _compact_public(row.get("next_action"), 240),
            "paper_href": f"selected-paper.html?paper={row.get('paper_id')}",
            "timeline_href": _dashboard_href(paper_id=str(row.get("paper_id") or "")),
        })

    events = [row for row in timeline.get("events", []) if isinstance(row, dict) and row.get("occurred_at")]
    local_dates = [china_date(str(row.get("occurred_at"))) for row in events]
    local_dates = [value for value in local_dates if value]
    latest_date = max(local_dates, default="")
    registry_date = str(registry.get("generated_at") or "")[:10]
    research_date = str(research.get("generated_at") or "")[:10]
    dashboard_date = max((value for value in (latest_date, registry_date, research_date) if value), default="")
    week_start = ""
    week_events: list[dict[str, Any]] = []
    if dashboard_date:
        latest_dt = datetime.strptime(dashboard_date, "%Y-%m-%d").date()
        start_dt = latest_dt - timedelta(days=latest_dt.weekday())
        week_start = start_dt.isoformat()
        week_events = [
            row for row in events
            if week_start <= china_date(str(row.get("occurred_at"))) <= dashboard_date
        ]

    week_classes = Counter(str(row.get("event_class") or "system") for row in week_events)
    week_days = {china_date(str(row.get("occurred_at"))) for row in week_events}
    attention_codes = {row["code"] for row in attention_rows if row.get("code")}
    attention_activity: Counter[str] = Counter()
    for event in week_events:
        refs = event.get("canonical_refs") or {}
        for ref in refs.get("research_items", []) or []:
            code = str(ref.get("code") or "") if isinstance(ref, dict) else ""
            if code in attention_codes:
                attention_activity[code] += 1

    def event_title(event: dict[str, Any]) -> str:
        return str(event.get("title_zh") or event.get("title") or "").strip()

    def highlight_score(event: dict[str, Any]) -> tuple[int, str]:
        cls = str(event.get("event_class") or "system")
        score = {"scientific": 70, "paper": 62, "closure": 54, "experiment": 45, "idea": 38}.get(cls, 0)
        if event.get("importance") == "key":
            score += 35
        refs = event.get("canonical_refs") or {}
        if any(str(ref.get("code") or "") in attention_codes for ref in refs.get("research_items", []) or [] if isinstance(ref, dict)):
            score += 30
        if refs.get("papers"):
            score += 20
        if event.get("origin") == "git_relevant_history":
            score -= 8
        return score, str(event.get("occurred_at") or "")

    highlight_candidates = []
    for event in week_events:
        if event.get("event_class") == "system":
            continue
        title = event_title(event)
        if not title or title.startswith(("论文推进记录 ·", "实验与验证记录 ·", "Idea / 问题发现记录 ·")):
            continue
        highlight_candidates.append(event)
    highlight_candidates.sort(key=highlight_score, reverse=True)
    highlights, seen_titles, seen_targets = [], set(), set()

    def append_highlight(event: dict[str, Any]) -> bool:
        normalized = re.sub(r"[^\w\u4e00-\u9fff]+", "", event_title(event).lower())
        if not normalized or normalized in seen_titles:
            return False
        refs = event.get("canonical_refs") or {}
        ref_codes = [str(ref.get("code")) for ref in refs.get("research_items", []) or [] if isinstance(ref, dict) and ref.get("code")]
        paper_ids = [str(ref.get("paper_id")) for ref in refs.get("papers", []) or [] if isinstance(ref, dict) and ref.get("paper_id")]
        seen_titles.add(normalized)
        highlights.append({
            "date": china_date(str(event.get("occurred_at"))),
            "event_class": str(event.get("event_class") or ""),
            "title_zh": event_title(event),
            "title_en": str(event.get("title") or event.get("title_zh") or "").strip(),
            "research_items": ref_codes,
            "papers": paper_ids,
            "href": _dashboard_href(code=(ref_codes[0] if ref_codes else ""), paper_id=(paper_ids[0] if paper_ids else "")),
        })
        return True

    # First pass deliberately diversifies the weekly narrative across canonical
    # research objects. A busy paper line should not hide other scientific
    # closures or decisions from the human-facing weekly summary.
    for event in highlight_candidates:
        refs = event.get("canonical_refs") or {}
        ref_codes = [str(ref.get("code")) for ref in refs.get("research_items", []) or [] if isinstance(ref, dict) and ref.get("code")]
        paper_ids = [str(ref.get("paper_id")) for ref in refs.get("papers", []) or [] if isinstance(ref, dict) and ref.get("paper_id")]
        preferred_code = next((code for code in ref_codes if code in attention_codes), ref_codes[0] if ref_codes else "")
        target = (f"ri:{preferred_code}" if preferred_code else f"paper:{paper_ids[0]}" if paper_ids else f"class:{event.get('event_class')}")
        if target in seen_targets:
            continue
        if append_highlight(event):
            seen_targets.add(target)
        if len(highlights) >= 5:
            break
    for event in highlight_candidates:
        if len(highlights) >= 5:
            break
        append_highlight(event)

    research_summary = research.get("summary") or {}
    dashboard = {
        "schema_version": "1.0",
        "as_of_date": dashboard_date,
        "projection_policy": {
            "read_only": True,
            "scientific_authority": False,
            "experiment_authority": False,
            "submission_authority": False,
            "sources": ["ResearchItemState", "PaperRegistry", "ResearchTimeline"],
            "dashboard_never_overrides_source_ledgers": True,
            "next_action_class_is_canonical_control_semantics": True,
            "next_step_text_is_human_explanation_only": True,
        },
        "summary": {
            "portfolio_objects": int(research_summary.get("portfolio_objects") or 0),
            "research_items": int(research_summary.get("research_items") or 0),
            "current_attention": len(attention_rows),
            "research_handoffs": research_handoffs,
            "research_waiting_reopen": research_waiting_reopen,
            "machine_actionable_attention": machine_actionable_attention,
            "paper_ready": int(state_counts.get("PAPER_READY", 0)),
            "holds": int(state_counts.get("HOLD", 0)),
            "launchable_formal_experiments": int(research_summary.get("current_formal_experiment_authority") or 0),
            "papers": len(paper_rows),
            "submission_ready": sum(bool(row.get("gate_clean_submission_ready")) for row in paper_rows),
            "ledger_submission_ready": sum(bool(row.get("ledger_submission_ready")) for row in paper_rows),
            "immediate_submission_holds": sum(bool(row.get("immediate_submission_hold")) for row in paper_rows),
            "paper_internal_action_required": sum(row.get("next_action_class") != "NO_INTERNAL_ACTION" for row in paper_rows),
            "paper_no_internal_action": sum(row.get("next_action_class") == "NO_INTERNAL_ACTION" for row in paper_rows),
            "research_primary_next_action_counts": dict(research_summary.get("primary_next_action_counts") or {}),
            "machine_actionable_research_items": int(research_summary.get("machine_actionable_research_items") or 0),
        },
        "attention": attention_rows,
        "papers": paper_rows,
        "week": {
            "start_date": week_start,
            "end_date": dashboard_date,
            "research_days": len(week_days),
            "events": len(week_events),
            "substantive_events": sum(count for cls, count in week_classes.items() if cls != "system"),
            "key_changes": sum(row.get("importance") == "key" and row.get("event_class") != "system" for row in week_events),
            "class_counts": dict(sorted(week_classes.items())),
            "attention_activity": dict(sorted(attention_activity.items())),
            "highlights": highlights,
            "timeline_href": "research-timeline.html",
        },
    }
    return dashboard


def validate_dashboard(payload: dict[str, Any]) -> None:
    policy = payload.get("projection_policy") or {}
    assert policy.get("read_only") is True
    assert policy.get("scientific_authority") is False
    assert policy.get("experiment_authority") is False
    assert policy.get("submission_authority") is False
    assert policy.get("next_action_class_is_canonical_control_semantics") is True
    assert policy.get("next_step_text_is_human_explanation_only") is True
    attention = payload.get("attention") or []
    codes = [row.get("code") for row in attention]
    assert len(codes) == len(set(codes))
    assert all(row.get("scientific_state") in {"PAPER_READY", "HOLD"} for row in attention)
    expected_attention_action = {"PAPER_READY": "PAPERSTATE_HANDOFF", "HOLD": "REOPEN_CONDITION_REQUIRED"}
    assert all(row.get("next_action_class") == expected_attention_action.get(row.get("scientific_state")) for row in attention)
    assert all((row.get("primary_next_action") or {}).get("machine_actionable") is False for row in attention)
    assert payload.get("summary", {}).get("current_attention") == len(attention)
    assert payload.get("summary", {}).get("research_handoffs") == sum(row.get("next_action_class") == "PAPERSTATE_HANDOFF" for row in attention)
    assert payload.get("summary", {}).get("research_waiting_reopen") == sum(row.get("next_action_class") == "REOPEN_CONDITION_REQUIRED" for row in attention)
    assert payload.get("summary", {}).get("machine_actionable_attention") == 0
    assert payload.get("summary", {}).get("papers") == len(payload.get("papers") or [])
    assert payload.get("summary", {}).get("paper_internal_action_required") == sum(row.get("next_action_class") != "NO_INTERNAL_ACTION" for row in payload.get("papers") or [])
    assert payload.get("summary", {}).get("paper_no_internal_action") == sum(row.get("next_action_class") == "NO_INTERNAL_ACTION" for row in payload.get("papers") or [])
    assert payload.get("summary", {}).get("machine_actionable_research_items") == 0


def validate(payload: dict[str, Any]) -> None:
    assert payload["projection_policy"]["projection_has_scientific_authority"] is False
    research = load(GEN / "research-items.json")
    registry = load(GEN / "paper-registry.json")
    valid_codes = {str(row.get("code")) for row in research.get("research_items",[]) if row.get("code")}
    valid_experiments = {str(row.get("experiment_id")) for row in research.get("experiment_records",[]) if row.get("experiment_id")}
    valid_papers = {str(row.get("paper_id")) for row in registry.get("papers",[]) if row.get("paper_id")}
    seen = set()
    for item in payload["events"]:
        assert item["event_id"] not in seen
        seen.add(item["event_id"])
        assert item["event_class"] in {"idea","experiment","scientific","paper","closure","blocker","system"}
        assert item["authority"]["projection_can_change_state"] is False
        refs = item.get("canonical_refs") or {}
        assert all(ref.get("code") in valid_codes for ref in refs.get("research_items",[]))
        assert all(ref.get("experiment_id") in valid_experiments for ref in refs.get("experiments",[]))
        assert all(ref.get("paper_id") in valid_papers for ref in refs.get("papers",[]))
        if item["research_id"] == "Research Memory":
            assert item["event_class"] == "system" and item["authority"]["scientific"] is False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--memory-db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--dashboard-only", action="store_true", help="Rebuild only the read-only dashboard from the committed timeline projection.")
    args = parser.parse_args()
    if args.dashboard_only:
        payload = load(GEN / "research-timeline.json")
        validate(payload)
    else:
        payload = build(args.memory_db)
        validate(payload)
        json_path, js_path = GEN/"research-timeline.json", GEN/"research-timeline.js"
        json_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        js_path.write_text("window.RESEARCH_TIMELINE = "+json.dumps(payload,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    dashboard = build_dashboard(payload)
    validate_dashboard(dashboard)
    (GEN/"research-dashboard.json").write_text(json.dumps(dashboard,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (GEN/"research-dashboard.js").write_text("window.RESEARCH_DASHBOARD = "+json.dumps(dashboard,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    s = payload["summary"]
    ds = dashboard["summary"]
    print(f"research timeline: {s['events']} events / {s['key_events']} key / {s['days']} days; dashboard attention={ds['current_attention']} papers={ds['papers']}")


if __name__ == "__main__":
    main()
