from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings
from .evidence_graph import build_evidence_graph
from .iclr_idea_factory import build_iclr_idea_bank
from .idea_discovery_v3 import build_idea_discovery_v3
from .idea_discovery_v31 import build_idea_discovery_v31
from .idea_discovery_v4 import build_idea_discovery_v4
from .idea_collision import analyze_collisions
from .idea_lineage import build_lineage
from .live_pipeline import load_live_corpus
from .pilot_registry import build_pilot_registry
from .review_repair import build_repair_queue

DEFAULT_JSON = PROJECT_ROOT / "generated" / "research-system-state.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "research-system-state.js"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _component_manifest(state: dict[str, Any]) -> list[dict[str, Any]]:
    graph = state["evidence_graph"]["summary"]
    collisions = state["collision_engine"]["summary"]
    lineage = state["lineage"]["summary"]
    pilots = state["pilot_registry"]["summary"]
    repairs = state["repair_queue"]["summary"]
    discovery = state["idea_discovery_v3"]["summary"]
    repaired = state["idea_discovery_v31"]["summary"]
    v4 = state["idea_discovery_v4"]["summary"]
    return [
        {"source":"ResearchAgent", "component":{"en":"Citation and evidence graph","zh":"引文与证据图谱"}, "status":"running", "evidence":{"en":f"{graph['nodes']} nodes / {graph['edges']} edges","zh":f"{graph['nodes']} 个节点 / {graph['edges']} 条边"}},
        {"source":"AI-Researcher", "component":{"en":"Hybrid semantic deduplication and collision filtering","zh":"混合语义去重与碰撞过滤"}, "status":"running", "evidence":{"en":f"{collisions['pairwise_comparisons']} pair comparisons / {collisions['flagged_pairs']} flagged","zh":f"{collisions['pairwise_comparisons']} 组两两比较 / {collisions['flagged_pairs']} 个标记"}},
        {"source":"MOOSE-Chem / Deep-Ideation", "component":{"en":"Idea lineage and branch preservation","zh":"Idea 谱系与分支保留"}, "status":"running", "evidence":{"en":f"{lineage['idea_nodes']} ideas / {lineage['edges']} lineage edges","zh":f"{lineage['idea_nodes']} 个 Idea / {lineage['edges']} 条谱系边"}},
        {"source":"CycleResearcher", "component":{"en":"Role-separated review repair queue","zh":"角色分离的审查修订队列"}, "status":"running", "evidence":{"en":f"{repairs['queued_ideas']} repair candidates","zh":f"{repairs['queued_ideas']} 个修订候选"}},
        {"source":"ResearchAgent / MOOSE-Chem / SciAgents / AI-Scientist-v2 / RD-Agent", "component":{"en":"Solution-first branch search","zh":"解决方案优先的分支搜索"}, "status":"running", "evidence":{"en":f"{discovery['raw_children']} v3 children / {discovery['external_revise']} R2 revise / {repaired['children']} v3.1 repairs","zh":f"{discovery['raw_children']} 个 v3 子节点 / {discovery['external_revise']} 个 R2 REVISE / {repaired['children']} 个 v3.1 修订"}},
        {"source":"ResearchAgent / MOOSE-Chem / Co-Scientist / HypoRefine / Virtual Scientists / autoresearch", "component":{"en":"Constrained composition and conditional revival","zh":"受约束组合与条件复活"}, "status":"running", "evidence":{"en":f"{v4['raw_candidates']} v4 candidates / {v4['tournament_finalists']} finalists / {v4['external_reviewed']} reviewed","zh":f"{v4['raw_candidates']} 个 v4 候选 / {v4['tournament_finalists']} 个 finalists / {v4['external_reviewed']} 个已复核"}},
        {"source":"AI-Scientist-v2", "component":{"en":"Pilot registry and result feedback","zh":"Pilot 注册表与结果回流"}, "status":"running", "evidence":{"en":f"{pilots['phases']} phases / {pilots['valid_result_files']} executed results","zh":f"{pilots['phases']} 个阶段 / {pilots['valid_result_files']} 个已执行结果"}},
        {"source":"AI-Scientist-v2", "component":{"en":"Unrestricted autonomous code execution tree","zh":"不受限制的自主代码执行树"}, "status":"intentionally-disabled", "evidence":{"en":"Only sandboxed/manual experiment execution is allowed; results can still flow back automatically.","zh":"只允许沙箱或人工确认后的实验执行；合法结果仍可自动回流。"}},
    ]


def _load_corpus_with_site_fallback() -> dict[str, Any]:
    corpus = load_live_corpus()
    if corpus:
        return corpus
    site_js = PROJECT_ROOT / "generated" / "s2-literature.js"
    if not site_js.exists():
        return {"papers": [], "queries": [], "statistics": {}}
    lines = site_js.read_text(encoding="utf-8").splitlines()
    meta_prefix = "window.S2_LITERATURE_META = "
    paper_prefix = "window.S2_LIVE_PAPERS = "
    meta_line = next((line for line in lines if line.startswith(meta_prefix)), "")
    paper_line = next((line for line in lines if line.startswith(paper_prefix)), "")
    try:
        meta = json.loads(meta_line[len(meta_prefix):].removesuffix(";"))
        records = json.loads(paper_line[len(paper_prefix):].removesuffix(";"))
    except (ValueError, json.JSONDecodeError):
        return {"papers": [], "queries": [], "statistics": {}}
    papers=[]
    for record in records:
        papers.append({
            "paper_id":str(record.get("paperId") or record.get("paper_id") or ""),
            "title":record.get("title"), "year":record.get("year"), "venue":record.get("venue"),
            "abstract":record.get("abstract"), "url":record.get("url"),
            "metadata":{
                "citationCount":record.get("citationCount"),
                "isOpenAccess":record.get("isOpenAccess"),
                "matches":record.get("matches") or [],
                "reconstructedFromSiteRecord":True,
            },
        })
    return {
        "schema_version":meta.get("schema_version", "1.0"),
        "retrieved_at":meta.get("retrieved_at"),
        "provider":meta.get("provider"),
        "statistics":meta.get("statistics") or {"paper_count":len(papers), "query_count":0},
        "seed_expansion":meta.get("seed_expansion"),
        "queries":[], "papers":papers,
        "reconstructed_from_site_snapshot":True,
    }


def build_research_system_state() -> dict[str, Any]:
    storage = StorageSettings.from_env()
    corpus = _load_corpus_with_site_fallback()
    idea_bank = build_iclr_idea_bank()
    evidence_graph = build_evidence_graph(corpus, idea_bank)
    collision_engine = analyze_collisions(idea_bank)
    lineage = build_lineage(idea_bank, collision_engine)
    pilot_registry = build_pilot_registry(idea_bank)
    repair_queue = build_repair_queue(idea_bank, collision_engine, pilot_registry)
    idea_discovery_v3 = build_idea_discovery_v3()
    idea_discovery_v31 = build_idea_discovery_v31()
    idea_discovery_v4 = build_idea_discovery_v4()
    latest_report_path = storage.run_dir / "automation" / "latest.json"
    latest_report = None
    if latest_report_path.exists():
        try:
            latest_report = json.loads(latest_report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            latest_report = {"status":"invalid", "path":str(latest_report_path)}
    state = {
        "schema_version":"1.0",
        "generated_at":_now(),
        "target_venue":"ICLR",
        "storage":{"data_root":str(storage.data_root), "run_dir":str(storage.run_dir)},
        "automation":{
            "daily":{"schedule":"02:15 server local time", "mode":"deterministic-offline"},
            "weekly":{"schedule":"Monday 03:15 server local time", "mode":"literature-sync-plus-two-bounded-web-reviews"},
            "fail_safe":"Exclusive locks; partial failure preserves the previous valid deployment artifact.",
            "latest_report":latest_report,
        },
        "summary":{
            "papers":(corpus.get("statistics") or {}).get("paper_count", len(corpus.get("papers") or [])),
            "queries":(corpus.get("statistics") or {}).get("query_count", len(corpus.get("queries") or [])),
            "ideas":idea_bank["summary"]["structured_candidates"],
            "passed_ideas":idea_bank["summary"]["passed"],
            "evidence_nodes":evidence_graph["summary"]["nodes"],
            "evidence_edges":evidence_graph["summary"]["edges"],
            "collision_flags":collision_engine["summary"]["flagged_pairs"],
            "lineage_edges":lineage["summary"]["edges"],
            "pilot_results":pilot_registry["summary"]["valid_result_files"],
            "repair_queue":repair_queue["summary"]["queued_ideas"],
            "solution_children":idea_discovery_v3["summary"]["raw_children"],
            "solution_shortlist":idea_discovery_v3["summary"]["internal_shortlist"],
            "reviewer_repair_children":idea_discovery_v31["summary"]["children"],
            "reviewer_repair_pass":idea_discovery_v31["summary"]["external_pass"],
            "v4_candidates":idea_discovery_v4["summary"]["raw_candidates"],
            "v4_finalists":idea_discovery_v4["summary"]["tournament_finalists"],
            "v4_revivals":idea_discovery_v4["summary"]["revival"],
            "v4_external_pass":idea_discovery_v4["summary"]["external_pass"],
        },
        "evidence_graph":evidence_graph,
        "collision_engine":collision_engine,
        "lineage":lineage,
        "pilot_registry":pilot_registry,
        "repair_queue":repair_queue,
        "idea_discovery_v3":idea_discovery_v3,
        "idea_discovery_v31":idea_discovery_v31,
        "idea_discovery_v4":idea_discovery_v4,
    }
    state["components"] = _component_manifest(state)
    state["health"] = _health(state, corpus)
    return state


def _health(state: dict[str, Any], corpus: dict[str, Any]) -> dict[str, Any]:
    checks = [
        {"key":"corpus", "pass":bool(corpus.get("papers")), "detail":f"{len(corpus.get('papers') or [])} papers"},
        {"key":"evidence-coverage", "pass":state["evidence_graph"]["summary"]["ideas_with_semantic_evidence"] >= 20, "detail":state["evidence_graph"]["summary"]["ideas_with_semantic_evidence"]},
        {"key":"collision-engine", "pass":state["collision_engine"]["summary"]["pairwise_comparisons"] > 0, "detail":state["collision_engine"]["summary"]["pairwise_comparisons"]},
        {"key":"lineage", "pass":state["lineage"]["summary"]["idea_nodes"] >= 24, "detail":state["lineage"]["summary"]["idea_nodes"]},
        {"key":"pilot-schema", "pass":state["pilot_registry"]["summary"]["invalid_result_files"] == 0, "detail":state["pilot_registry"]["summary"]},
    ]
    return {"status":"healthy" if all(item["pass"] for item in checks) else "degraded", "checks":checks}


def validate_state(state: dict[str, Any]) -> list[str]:
    errors=[]
    if state.get("target_venue") != "ICLR": errors.append("target venue mismatch")
    if state["summary"]["papers"] < 100: errors.append("literature corpus too small")
    if state["summary"]["ideas"] < 24: errors.append("idea bank too small")
    if state["evidence_graph"]["summary"]["nodes"] <= state["summary"]["papers"]: errors.append("evidence graph lacks non-paper nodes")
    if state["collision_engine"]["summary"]["pairwise_comparisons"] <= 0: errors.append("collision engine did not run")
    if state["pilot_registry"]["summary"]["phases"] != state["summary"]["passed_ideas"] * 3: errors.append("pilot phase count mismatch")
    return errors


def write_research_system_state(json_path:Path=DEFAULT_JSON, js_path:Path=DEFAULT_JS) -> dict[str, Any]:
    state=build_research_system_state()
    errors=validate_state(state)
    if errors: raise ValueError("Invalid research system state:\n- " + "\n- ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    js_path.write_text("window.RESEARCH_SYSTEM_STATE = "+json.dumps(state, ensure_ascii=False, separators=(",",":"))+";\n", encoding="utf-8")
    return state
