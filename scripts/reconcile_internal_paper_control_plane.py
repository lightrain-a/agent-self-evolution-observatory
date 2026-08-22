#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.config import StorageSettings, resolve_experiment_data_root
from research_pipeline.paper_acceptance_ledger import build_paper_ledger_index, build_portable_paper_ledger_index
from research_pipeline.paper_first_fresh_phenomenon_portfolio import DEFAULT_JSON as FRESH_PHENOMENON_JSON, validate_fresh_phenomenon_portfolio
from research_pipeline.paper_first_search_portfolio_design_adjudication import DEFAULT_JSON as SEARCH_DESIGN_JSON, validate_search_portfolio_design_adjudication
from research_pipeline.research_memory_wiki import build_research_memory_wiki, write_research_memory_wiki

GEN = ROOT / "generated"
SYSTEM_JSON = GEN / "research-system-state.json"
SYSTEM_JS = GEN / "research-system-state.js"


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def write_system_pair(state: dict) -> None:
    SYSTEM_JSON.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SYSTEM_JS.write_text(
        "window.RESEARCH_SYSTEM_STATE = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def update_component_evidence(state: dict, *, paper_summary: dict, memory_summary: dict, memory_lint: dict) -> None:
    for component in state.get("components") or []:
        if not isinstance(component, dict):
            continue
        key = str(component.get("key") or "")
        evidence = component.setdefault("evidence", {})
        if key == "paper-acceptance-closure":
            paper_states = int(((state.get("paper_acceptance") or {}).get("summary") or {}).get("paper_states") or 0)
            registered = int(paper_summary.get("papers") or 0)
            holds = int(paper_summary.get("scientific_holds") or 0)
            ledger_ready = int(paper_summary.get("submission_ready") or 0)
            gate_clean = int(paper_summary.get("gate_clean_submission_ready") or 0)
            internal_actions = int(paper_summary.get("internal_action_required") or 0)
            evidence["en"] = f"{paper_states} paper states / {registered} registered ledgers / {holds} scientific holds / {ledger_ready} ledger-ready / {gate_clean} latest gate-clean / {internal_actions} internal action required"
            evidence["zh"] = f"{paper_states} 个论文状态 / {registered} 个已注册 ledger / {holds} 个科学 HOLD / {ledger_ready} 个历史 ready / {gate_clean} 个最新门禁 clean / {internal_actions} 个仍需内部动作"
        elif key == "scientific-research-graph":
            graph = (state.get("scientific_research_graph") or {}).get("summary") or {}
            entries = int(memory_summary.get("entries") or 0)
            failures = int(memory_summary.get("failure_assets") or 0)
            successes = int(memory_summary.get("success_assets") or 0)
            review_lessons = int(memory_summary.get("review_lessons") or 0)
            warnings = int(memory_lint.get("warnings") or 0)
            evidence["en"] = f"{int(graph.get('nodes') or 0)} graph nodes / {int(graph.get('edges') or 0)} edges; memory wiki {entries} entries / {failures} failure / {successes} success / {review_lessons} paper-review lessons / lint warnings {warnings}"
            evidence["zh"] = f"研究图谱 {int(graph.get('nodes') or 0)} 个节点 / {int(graph.get('edges') or 0)} 条边；Memory Wiki {entries} 条 / 失败 {failures} / 成功 {successes} / 论文审查经验 {review_lessons} / lint warning {warnings}"


def main() -> None:
    state = load_json(SYSTEM_JSON)
    search_design = load_json(SEARCH_DESIGN_JSON)
    search_errors = validate_search_portfolio_design_adjudication(search_design)
    if search_errors:
        raise RuntimeError("refusing to embed invalid Search Portfolio projection: " + "; ".join(search_errors))

    fresh_phenomenon = load_json(FRESH_PHENOMENON_JSON)
    fresh_errors = validate_fresh_phenomenon_portfolio(fresh_phenomenon)
    if fresh_errors:
        raise RuntimeError("refusing to embed invalid durable Fresh Phenomenon projection: " + "; ".join(fresh_errors))

    data_root = resolve_experiment_data_root(StorageSettings.from_env())
    live_index = build_paper_ledger_index(data_root)
    live_summary = live_index.get("summary") or {}
    if int(live_summary.get("invalid_ledgers") or 0) != 0:
        raise RuntimeError("refusing to reconcile an invalid live paper ledger index")
    ledger_index = live_index
    ledger_index_source = "canonical-append-only-paper-ledgers"
    if int(live_summary.get("papers") or 0) == 0:
        portable_registry = load_json(GEN / "paper-registry.json")
        portable_index = build_portable_paper_ledger_index(portable_registry)
        portable_summary = portable_index.get("summary") or {}
        if int(portable_summary.get("invalid_ledgers") or 0) != 0:
            raise RuntimeError("refusing to reconcile an invalid portable PaperRegistry fallback")
        if int(portable_summary.get("papers") or 0) > 0:
            ledger_index = portable_index
            ledger_index_source = "generated/paper-registry.json"
    ledger_summary = ledger_index.get("summary") or {}

    memory = build_research_memory_wiki(
        search_design_state=search_design,
        failure_asset_library=state.get("failure_asset_library") or {},
        scientific_meta_trace=state.get("scientific_meta_trace") or {},
        candidate_portfolio=state.get("research_candidate_portfolio") or {},
        experiment_iteration=state.get("experiment_iteration") or {},
        generator_state=state.get("paper_first_problem_generator") or {},
        paper_ledger_index=ledger_index,
    )
    if (memory.get("lint") or {}).get("status") != "PASS":
        raise RuntimeError("refusing to publish invalid Research Memory")
    write_research_memory_wiki(memory)

    paper_acceptance = state.setdefault("paper_acceptance", {})
    paper_acceptance["ledger_index"] = ledger_index
    paper_acceptance["ledger_index_source"] = ledger_index_source
    summary = paper_acceptance.setdefault("summary", {})
    summary.update({
        "registered_papers": int(ledger_summary.get("papers") or 0),
        "scientific_holds": int(ledger_summary.get("scientific_holds") or 0),
        "ledger_submission_ready_papers": int(ledger_summary.get("submission_ready") or 0),
        "submission_ready_papers": int(ledger_summary.get("submission_ready") or 0),
        "gate_clean_submission_ready_papers": int(ledger_summary.get("gate_clean_submission_ready") or 0),
        "paper_preparation_failed_papers": int(ledger_summary.get("paper_preparation_failed") or 0),
        "immediate_submission_holds": int(ledger_summary.get("immediate_submission_holds") or 0),
        "internal_action_required_papers": int(ledger_summary.get("internal_action_required") or 0),
        "no_internal_action_papers": int(ledger_summary.get("no_internal_action") or 0),
        "invalid_ledgers": int(ledger_summary.get("invalid_ledgers") or 0),
    })
    paper_acceptance["control_plane_reconciled_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    paper_acceptance.setdefault("policy", {}).update({
        "submission_ready_papers_is_legacy_alias_for_ledger_submission_ready_papers": True,
        "gate_clean_submission_ready_is_latest_effective_internal_readiness": True,
        "primary_next_action_is_internal_only_and_zero_authority": True,
    })

    state["research_memory_wiki"] = memory
    top_summary = state.setdefault("summary", {})
    top_summary.update({
        "research_memory_entries": int((memory.get("summary") or {}).get("entries") or 0),
        "research_memory_review_lessons": int((memory.get("summary") or {}).get("review_lessons") or 0),
        "research_memory_lint_warnings": int(((memory.get("lint") or {}).get("summary") or {}).get("warnings") or 0),
        "paper_acceptance_registered_papers": int(ledger_summary.get("papers") or 0),
        "paper_acceptance_ledger_submission_ready": int(ledger_summary.get("submission_ready") or 0),
        "paper_acceptance_gate_clean_submission_ready": int(ledger_summary.get("gate_clean_submission_ready") or 0),
        "paper_acceptance_internal_action_required": int(ledger_summary.get("internal_action_required") or 0),
    })
    update_component_evidence(
        state,
        paper_summary=ledger_summary,
        memory_summary=memory.get("summary") or {},
        memory_lint=(memory.get("lint") or {}).get("summary") or {},
    )
    write_system_pair(state)

    print(json.dumps({
        "papers": int(ledger_summary.get("papers") or 0),
        "ledger_submission_ready": int(ledger_summary.get("submission_ready") or 0),
        "gate_clean_submission_ready": int(ledger_summary.get("gate_clean_submission_ready") or 0),
        "internal_action_required": int(ledger_summary.get("internal_action_required") or 0),
        "no_internal_action": int(ledger_summary.get("no_internal_action") or 0),
        "review_lessons": int((memory.get("summary") or {}).get("review_lessons") or 0),
        "memory_entries": int((memory.get("summary") or {}).get("entries") or 0),
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
