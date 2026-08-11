from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings, resolve_experiment_data_root
from .discussion_portfolio import build_discussion_portfolio
from .evidence_graph import build_evidence_graph
from .experiment_iteration import build_experiment_iteration_state
from .human_terminal_state import build_human_terminal_state, write_human_terminal_state
from .iclr_idea_factory import build_iclr_idea_bank
from .idea_discovery_v3 import build_idea_discovery_v3
from .idea_discovery_v31 import build_idea_discovery_v31
from .idea_discovery_v4 import build_idea_discovery_v4
from .idea_discovery_v5 import build_idea_discovery_v5
from .idea_discovery_v51 import build_idea_discovery_v51
from .idea_discovery_v52 import build_idea_discovery_v52
from .idea_discovery_v53 import build_idea_discovery_v53
from .idea_collision import analyze_collisions
from .idea_lineage import build_lineage
from .live_pipeline import load_live_corpus
from .pilot_registry import build_pilot_registry
from .p0_mem_xfer_offline_analysis import build_mem_xfer_workflow_state
from .p0_admission import build_p0_admission_state, write_p0_admission_state
from .p0_b10_cpu import write_b10_cpu_p0
from .p0_a6_cpu import write_a6_cpu_p0
from .p0_offline_qualification import build_p0_offline_qualification_state, write_p0_offline_qualification_state
from .p0_realizability_suite import build_p0_realizability_suite, write_p0_realizability_suite
from .pre_experiment_compiler import compile_from_path as compile_pre_experiment_from_path
from .pre_experiment_specs import GATES as PRE_EXPERIMENT_GATES, POLICY as PRE_EXPERIMENT_POLICY
from .pre_p0_identifiability import build_pre_p0_identifiability_audit
from .pre_gpu_candidate_gates import build_pre_gpu_candidate_gate_state
from .review_repair import build_repair_queue

DEFAULT_JSON = PROJECT_ROOT / "generated" / "research-system-state.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "research-system-state.js"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


PRE_EXPERIMENT_CONFIGS = (
    Path(__file__).with_name("p0_a1_screening_config.json"),
    Path(__file__).with_name("p0_a1_confirm_config.json"),
    Path(__file__).with_name("p0_a2_screening_config.json"),
    Path(__file__).with_name("p0_a2_confirm_config.json"),
)


def _build_pre_experiment_state(storage: StorageSettings) -> dict[str, Any]:
    experiment_data_root = resolve_experiment_data_root(storage)
    cards: list[dict[str, Any]] = []
    for config_file in PRE_EXPERIMENT_CONFIGS:
        try:
            config = json.loads(config_file.read_text(encoding="utf-8"))
            card = compile_pre_experiment_from_path(str(config["idea_id"]), config_file, experiment_data_root)
            cards.append({**card, "config": config_file.name})
        except Exception as error:
            cards.append({
                "schema_version": "2.0", "config": config_file.name, "status": "compile-error",
                "execution_authorized": False, "passed_gates": 0, "gate_count": len(PRE_EXPERIMENT_GATES),
                "blockers": [f"compile-error:{type(error).__name__}"],
            })
    formal = [row for row in cards if row.get("phase") == "P0"]
    screening = [row for row in cards if row.get("phase") != "P0"]
    gate_failures = {}
    for gate in PRE_EXPERIMENT_GATES:
        key = gate["key"]
        gate_failures[key] = sum(
            any(item.get("key") == key and item.get("pass") is not True for item in row.get("gates") or [])
            for row in cards
        )
    return {
        "schema_version": "2.0",
        "experiment_data_root": str(experiment_data_root),
        "policy": PRE_EXPERIMENT_POLICY,
        "gates": list(PRE_EXPERIMENT_GATES),
        "summary": {
            "compiled_cards": len(cards),
            "execution_ready": sum(bool(row.get("execution_authorized")) for row in cards),
            "blocked": sum(not bool(row.get("execution_authorized")) for row in cards),
            "updater_prerequisite_pass": sum(bool((row.get("updater_competence_prerequisite") or {}).get("passed")) for row in cards),
            "updater_prerequisite_fail": sum(not bool((row.get("updater_competence_prerequisite") or {}).get("passed")) for row in cards),
            "screening_ready": sum(bool(row.get("execution_authorized")) for row in screening),
            "formal_p0_ready": sum(bool(row.get("execution_authorized")) for row in formal),
            "formal_p0_total": len(formal),
            "gate_failures": gate_failures,
        },
        "cards": cards,
    }


def _component_manifest(state: dict[str, Any]) -> list[dict[str, Any]]:
    graph = state["evidence_graph"]["summary"]
    collisions = state["collision_engine"]["summary"]
    lineage = state["lineage"]["summary"]
    pilots = state["pilot_registry"]["summary"]
    pre_p0 = state["pre_p0_identifiability"]["summary"]
    pre_experiment = state["pre_experiment_compiler"]["summary"]
    iteration = state["experiment_iteration"]["summary"]
    repairs = state["repair_queue"]["summary"]
    terminal = state["human_terminal_ideas"]["summary"]
    discovery = state["idea_discovery_v3"]["summary"]
    repaired = state["idea_discovery_v31"]["summary"]
    v4 = state["idea_discovery_v4"]["summary"]
    v5 = state["idea_discovery_v5"]["summary"]
    return [
        {"source":"ResearchAgent", "component":{"en":"Citation and evidence graph","zh":"引文与证据图谱"}, "status":"running", "evidence":{"en":f"{graph['nodes']} nodes / {graph['edges']} edges","zh":f"{graph['nodes']} 个节点 / {graph['edges']} 条边"}},
        {"source":"AI-Researcher", "component":{"en":"Hybrid semantic deduplication and collision filtering","zh":"混合语义去重与碰撞过滤"}, "status":"running", "evidence":{"en":f"{collisions['pairwise_comparisons']} pair comparisons / {collisions['flagged_pairs']} flagged","zh":f"{collisions['pairwise_comparisons']} 组两两比较 / {collisions['flagged_pairs']} 个标记"}},
        {"source":"MOOSE-Chem / Deep-Ideation", "component":{"en":"Idea lineage and branch preservation","zh":"Idea 谱系与分支保留"}, "status":"running", "evidence":{"en":f"{lineage['idea_nodes']} ideas / {lineage['edges']} lineage edges","zh":f"{lineage['idea_nodes']} 个 Idea / {lineage['edges']} 条谱系边"}},
        {"source":"Human terminal ledger", "component":{"en":"Terminalized human-parent lifecycle controller","zh":"人工 Parent 终态生命周期控制器"}, "status":"running", "evidence":{"en":f"26 parents: {terminal['p0']} P0 / {terminal['p0_ready']} P0-ready / {terminal['merge']} merged / {terminal['drop']} dropped","zh":f"26 个 Parent：{terminal['p0']} P0 / {terminal['p0_ready']} P0 Ready / {terminal['merge']} 合并 / {terminal['drop']} 停止"}},
        {"source":"CycleResearcher", "component":{"en":"Role-separated review repair queue","zh":"角色分离的审查修订队列"}, "status":"running", "evidence":{"en":f"{repairs['queued_ideas']} repair candidates after terminal filtering","zh":f"终态过滤后 {repairs['queued_ideas']} 个修订候选"}},
        {"source":"ResearchAgent / MOOSE-Chem / SciAgents / AI-Scientist-v2 / RD-Agent", "component":{"en":"Solution-first branch search","zh":"解决方案优先的分支搜索"}, "status":"running", "evidence":{"en":f"{discovery['raw_children']} v3 children / {discovery['external_revise']} R2 revise / {repaired['children']} v3.1 repairs","zh":f"{discovery['raw_children']} 个 v3 子节点 / {discovery['external_revise']} 个 R2 REVISE / {repaired['children']} 个 v3.1 修订"}},
        {"source":"ResearchAgent / MOOSE-Chem / Co-Scientist / HypoRefine / Virtual Scientists / autoresearch", "component":{"en":"Constrained composition and conditional revival","zh":"受约束组合与条件复活"}, "status":"running", "evidence":{"en":f"{v4['raw_candidates']} v4 candidates / {v4['tournament_finalists']} finalists / {v4['external_reviewed']} reviewed","zh":f"{v4['raw_candidates']} 个 v4 候选 / {v4['tournament_finalists']} 个 finalists / {v4['external_reviewed']} 个已复核"}},
        {"source":"HypoRefine / IdeaForge / ScholarEval / InnoEval / SciAtlas / InternAgent / AutoScientists", "component":{"en":"Wide-search simplification-challenge ideation","zh":"宽搜索与简化挑战式 Idea 发现"}, "status":"running", "evidence":{"en":f"{v5['raw_candidates']} v5 candidates / {v5['external_reviewed']} R2 reviewed / {v5['external_pass']} PASS","zh":f"{v5['raw_candidates']} 个 v5 候选 / {v5['external_reviewed']} 个 R2 已审 / {v5['external_pass']} 个 PASS"}},
        {"source":"AIDE / AI-Scientist-v2 / R&D-Agent", "component":{"en":"Pre-P0 identifiability auditor","zh":"Pre-P0 实验可识别性审计"}, "status":"running", "evidence":{"en":f"{pre_p0['execution_ready']}/{pre_p0['audited']} retrospective contracts execution-ready","zh":f"当前 {pre_p0['execution_ready']}/{pre_p0['audited']} 份 retrospective 合同允许启动"}},
        {"source":"AIDE / AI-Scientist-v2 / R&D-Agent", "component":{"en":"Updater-competence prerequisite + eight-gate Pre-Experiment Compiler","zh":"Updater Competence 前置条件 + 八门实验启动前编译器"}, "status":"running", "evidence":{"en":f"updater prerequisite {pre_experiment['updater_prerequisite_pass']}/{pre_experiment['compiled_cards']} / launch-ready {pre_experiment['execution_ready']}/{pre_experiment['compiled_cards']} / formal P0 {pre_experiment['formal_p0_ready']}/{pre_experiment['formal_p0_total']}","zh":f"Updater prerequisite {pre_experiment['updater_prerequisite_pass']}/{pre_experiment['compiled_cards']} / 可启动 {pre_experiment['execution_ready']}/{pre_experiment['compiled_cards']} / formal P0 {pre_experiment['formal_p0_ready']}/{pre_experiment['formal_p0_total']}"}},
        {"source":"AI-Scientist-v2", "component":{"en":"Pilot registry and result feedback","zh":"Pilot 注册表与结果回流"}, "status":"running", "evidence":{"en":f"{pilots['phases']} phases / {pilots['valid_result_files']} executed results","zh":f"{pilots['phases']} 个阶段 / {pilots['valid_result_files']} 个已执行结果"}},
        {"source":"AI-Scientist-v2 / AIDE / RD-Agent / ML-Master / AIRA / Agent Laboratory", "component":{"en":"Experiment diagnosis and atomic repair tree","zh":"实验诊断与原子修复树"}, "status":"running", "evidence":{"en":f"{iteration['nodes']} pilot nodes / {iteration['repair_children']} atomic repair children / {iteration['scale_up_allowed']} scale-up","zh":f"{iteration['nodes']} 个 Pilot 节点 / {iteration['repair_children']} 个原子修复子节点 / {iteration['scale_up_allowed']} 个可扩大"}},
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
    pre_p0_identifiability = build_pre_p0_identifiability_audit(idea_bank)
    pre_experiment_compiler = _build_pre_experiment_state(storage)
    formal_cards = {
        str(card.get("idea_id")): card
        for card in pre_experiment_compiler.get("cards") or []
        if card.get("phase") == "P0" and card.get("idea_id")
    }
    experiment_data_root = resolve_experiment_data_root(storage)
    mem_xfer_workflow = build_mem_xfer_workflow_state(experiment_data_root)
    pilot_registry = build_pilot_registry(
        idea_bank,
        result_dir=experiment_data_root / "runs" / "pilots" / "results",
        approval_dir=experiment_data_root / "runs" / "pilots" / "approvals",
        pre_p0_audit=pre_p0_identifiability,
        pre_experiment_cards=formal_cards,
    )
    experiment_iteration = build_experiment_iteration_state()
    pre_gpu_candidate_gates = build_pre_gpu_candidate_gate_state()
    human_terminal_ideas = build_human_terminal_state()
    p0_realizability = build_p0_realizability_suite()
    p0_offline_qualification = build_p0_offline_qualification_state()
    p0_admission = build_p0_admission_state()
    p0_admission_public = {"summary": p0_admission["summary"], "policy": p0_admission["policy"]}
    p0_offline_public = {"summary": p0_offline_qualification["summary"], "policy": p0_offline_qualification["policy"]}
    p0_realizability_public = {"summary": p0_realizability["summary"], "policy": p0_realizability["policy"]}
    repair_queue = build_repair_queue(idea_bank, collision_engine, pilot_registry, experiment_iteration)
    idea_discovery_v3 = build_idea_discovery_v3()
    idea_discovery_v31 = build_idea_discovery_v31()
    idea_discovery_v4 = build_idea_discovery_v4()
    idea_discovery_v5 = build_idea_discovery_v5()
    idea_discovery_v51 = build_idea_discovery_v51()
    idea_discovery_v52 = build_idea_discovery_v52()
    idea_discovery_v53 = build_idea_discovery_v53()
    discussion_portfolio = build_discussion_portfolio()
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
            "pre_p0_audited":pre_p0_identifiability["summary"]["audited"],
            "pre_p0_ready":pre_p0_identifiability["summary"]["execution_ready"],
            "pre_experiment_cards":pre_experiment_compiler["summary"]["compiled_cards"],
            "pre_experiment_ready":pre_experiment_compiler["summary"]["execution_ready"],
            "pre_experiment_formal_ready":pre_experiment_compiler["summary"]["formal_p0_ready"],
            "experiment_diagnoses":experiment_iteration["summary"]["nodes"],
            "experiment_repair_children":experiment_iteration["summary"]["repair_children"],
            "experiment_scale_up":experiment_iteration["summary"]["scale_up_allowed"],
            "repair_queue":repair_queue["summary"]["queued_ideas"],
            "human_terminal_parents":human_terminal_ideas["summary"]["human_parents"],
            "human_terminal_p0":human_terminal_ideas["summary"]["p0"],
            "human_terminal_p0_ready":human_terminal_ideas["summary"]["p0_ready"],
            "human_terminal_merge":human_terminal_ideas["summary"]["merge"],
            "human_terminal_drop":human_terminal_ideas["summary"]["drop"],
            "p0_admission_active":p0_admission["summary"]["active_p0"],
            "p0_admission_transitioned":p0_admission["summary"]["transitioned_from_p0_ready"],
            "p0_admission_settings_complete":p0_admission["summary"]["settings_complete"],
            "p0_admission_execution_authorized":p0_admission["summary"]["execution_authorized"],
            "p0_offline_checks_passed":p0_offline_qualification["summary"]["checks_passed"],
            "p0_offline_checks_failed":p0_offline_qualification["summary"]["checks_failed"],
            "p0_offline_checks_pending":p0_offline_qualification["summary"]["checks_pending"],
            "p0_realizability_passed":p0_realizability["summary"]["synthetic_pass"],
            "p0_b10_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("b10",{}).get("decision"),
            "p0_a4_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("a4_composition_cpu",{}).get("decision"),
            "p0_a5_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("a5_history_cpu",{}).get("decision"),
            "p0_a6_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("a6_cpu",{}).get("decision"),
            "p0_a7_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("a7_counterfactual_cpu",{}).get("decision"),
            "p0_b3_screening_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("b3_interference_cpu",{}).get("decision"),
            "p0_c2_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("c2_evaluator_cpu",{}).get("decision"),
            "p0_d1_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("d1_minimal_curriculum_cpu",{}).get("decision"),
            "p0_e2_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("e2_workflow_cpu",{}).get("decision"),
            "p0_e3_decision":((p0_offline_qualification.get("shared_evidence") or {}).get("e3_stateful") or (p0_offline_qualification.get("shared_evidence") or {}).get("e3_real_api") or {}).get("decision"),
            "p0_e4_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("e4_permission_cpu",{}).get("decision"),
            "solution_children":idea_discovery_v3["summary"]["raw_children"],
            "solution_shortlist":idea_discovery_v3["summary"]["internal_shortlist"],
            "pre_gpu_candidates":pre_gpu_candidate_gates["summary"]["total"],
            "true_small_p0":pre_gpu_candidate_gates["summary"]["small_p0"],
            "pre_gpu_hold":pre_gpu_candidate_gates["summary"]["hold"],
            "pre_gpu_stop":pre_gpu_candidate_gates["summary"]["stop"],
            "reviewer_repair_children":idea_discovery_v31["summary"]["children"],
            "reviewer_repair_pass":idea_discovery_v31["summary"]["external_pass"],
            "v4_candidates":idea_discovery_v4["summary"]["raw_candidates"],
            "v4_finalists":idea_discovery_v4["summary"]["tournament_finalists"],
            "v4_revivals":idea_discovery_v4["summary"]["revival"],
            "v4_external_pass":idea_discovery_v4["summary"]["external_pass"],
            "v5_candidates":idea_discovery_v5["summary"]["raw_candidates"],
            "v5_finalists":len(idea_discovery_v5["finalists"]),
            "v5_revivals":idea_discovery_v5["summary"]["revival"],
            "v5_external_pass":idea_discovery_v5["summary"]["external_pass"],
            "v51_external_pass":idea_discovery_v51["summary"]["pass"],
            "v52_external_pass":idea_discovery_v52["summary"]["pass"],
            "v53_external_pass":idea_discovery_v53["summary"]["pass"],
            "discussion_ready":discussion_portfolio["count"],
            "discussion_target":discussion_portfolio["target"],
            "final_pass":discussion_portfolio["final_summary"]["pass"],
            "final_revise":discussion_portfolio["final_summary"]["revise"],
            "final_block":discussion_portfolio["final_summary"]["block"],
            "final_ready":discussion_portfolio["ready"],
            "mem_xfer_full_table_status":mem_xfer_workflow["full_table"]["status"],
            "mem_xfer_offline_analysis_status":mem_xfer_workflow["offline_analysis"]["status"],
            "mem_xfer_support_qualification_status":mem_xfer_workflow["support_qualification"]["status"],
            "mem_xfer_support_full_status":mem_xfer_workflow["full_support"]["status"],
            "mem_xfer_support_analysis_status":mem_xfer_workflow["support_enriched_analysis"]["status"],
            "mem_xfer_second_model_status":mem_xfer_workflow["second_model"]["status"],
        },
        "evidence_graph":evidence_graph,
        "collision_engine":collision_engine,
        "lineage":lineage,
        "pre_p0_identifiability":pre_p0_identifiability,
        "pre_gpu_candidate_gates":pre_gpu_candidate_gates,
        "pre_experiment_compiler":pre_experiment_compiler,
        "pilot_registry":pilot_registry,
        "experiment_iteration":experiment_iteration,
        "human_terminal_ideas":human_terminal_ideas,
        "p0_admission":p0_admission_public,
        "p0_offline_qualification":p0_offline_public,
        "p0_realizability":p0_realizability_public,
        "repair_queue":repair_queue,
        "idea_discovery_v3":idea_discovery_v3,
        "idea_discovery_v31":idea_discovery_v31,
        "idea_discovery_v4":idea_discovery_v4,
        "idea_discovery_v5":idea_discovery_v5,
        "idea_discovery_v51":idea_discovery_v51,
        "idea_discovery_v52":idea_discovery_v52,
        "idea_discovery_v53":idea_discovery_v53,
        "discussion_portfolio":discussion_portfolio,
        "mem_xfer_workflow":mem_xfer_workflow,
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
        {"key":"pre-p0-identifiability", "pass":state["pre_p0_identifiability"]["policy"]["p0_execution_requires_pre_p0_pass"], "detail":state["pre_p0_identifiability"]["summary"]},
        {"key":"pre-gpu-survivor-gate", "pass":state["pre_gpu_candidate_gates"]["summary"]["total"] == 10 and state["pre_gpu_candidate_gates"]["summary"]["small_p0"] == 2 and state["pre_gpu_candidate_gates"]["policy"]["hold_or_inconclusive_is_not_method_failure"], "detail":state["pre_gpu_candidate_gates"]["summary"]},
        {"key":"pre-experiment-compiler", "pass":state["pre_experiment_compiler"]["policy"]["updater_competence_required_before_gate_1"] and state["pre_experiment_compiler"]["policy"]["updater_competence_is_not_a_ninth_gate"] and state["pre_experiment_compiler"]["policy"]["all_eight_gates_required"] and state["pre_experiment_compiler"]["policy"]["automatic_override_forbidden"] and state["pre_experiment_compiler"]["summary"]["compiled_cards"] == 4, "detail":state["pre_experiment_compiler"]["summary"]},
        {"key":"pilot-schema", "pass":state["pilot_registry"]["summary"]["invalid_result_files"] == 0 and state["pilot_registry"]["summary"]["invalid_approval_files"] == 0 and state["pilot_registry"]["policy"]["automatic_p0_to_p1_forbidden"] and state["pilot_registry"]["policy"]["p0_execution_requires_pre_experiment_8_of_8"], "detail":state["pilot_registry"]["summary"]},
        {"key":"experiment-diagnosis", "pass":state["experiment_iteration"]["summary"]["nodes"] == 4 and state["experiment_iteration"]["policy"]["nonidentifiable_pilot_cannot_update_scientific_belief"], "detail":state["experiment_iteration"]["summary"]},
        {"key":"mem-xfer-workflow", "pass":state["mem_xfer_workflow"]["full_table"]["status"] == "full_table_collected" and state["mem_xfer_workflow"]["offline_analysis"]["status"] == "offline_analysis_complete" and state["mem_xfer_workflow"]["support_qualification"]["status"] == "support_qualification_pass" and state["mem_xfer_workflow"]["full_support"]["status"] == "full_support_complete" and state["mem_xfer_workflow"]["support_enriched_analysis"]["status"] == "support_enriched_analysis_complete" and (state["mem_xfer_workflow"]["support_enriched_analysis"].get("decision") or {}).get("method_failure_authorized") is False and state["mem_xfer_workflow"]["second_model"]["status"] == "second_model_hold", "detail":{"old_full":state["mem_xfer_workflow"]["full_table"]["status"],"old_offline":state["mem_xfer_workflow"]["offline_analysis"]["status"],"support_qualification":state["mem_xfer_workflow"]["support_qualification"]["status"],"full_support":state["mem_xfer_workflow"]["full_support"]["status"],"cpu_gate":state["mem_xfer_workflow"]["support_enriched_analysis"]["status"],"second_model":state["mem_xfer_workflow"]["second_model"]["status"]}},
        {"key":"human-terminal-ledger", "pass":state["human_terminal_ideas"]["summary"].get("human_parents") == 26 and (state["human_terminal_ideas"]["summary"].get("p0"),state["human_terminal_ideas"]["summary"].get("p0_ready"),state["human_terminal_ideas"]["summary"].get("merge"),state["human_terminal_ideas"]["summary"].get("drop")) == (13,0,6,7), "detail":state["human_terminal_ideas"]["summary"]},
        {"key":"p0-admission", "pass":state["p0_admission"]["summary"].get("active_p0") == 20 and state["p0_admission"]["summary"].get("admitted") == 20 and state["p0_admission"]["summary"].get("transitioned_from_p0_ready") == 16 and state["p0_admission"]["summary"].get("settings_complete") == 20, "detail":state["p0_admission"]["summary"]},
        {"key":"p0-offline-qualification", "pass":state["p0_offline_qualification"]["summary"].get("ideas") == 16 and state["p0_offline_qualification"]["policy"].get("method_result_from_offline_qualification_forbidden") is True, "detail":state["p0_offline_qualification"]["summary"]},
        {"key":"p0-realizability", "pass":state["p0_realizability"]["summary"].get("audited") == 14 and state["p0_realizability"]["policy"].get("cannot_emit_method_result") is True, "detail":state["p0_realizability"]["summary"]},
        {"key":"final-advisor-gate", "pass":state["summary"]["final_ready"] and state["summary"]["final_pass"] == state["summary"]["discussion_target"] and state["summary"]["final_revise"] == 0 and state["summary"]["final_block"] == 0, "detail":{"pass":state["summary"]["final_pass"],"target":state["summary"]["discussion_target"],"revise":state["summary"]["final_revise"],"block":state["summary"]["final_block"]}},
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
    if not state["pre_p0_identifiability"]["policy"]["p0_execution_requires_pre_p0_pass"]: errors.append("retrospective Pre-P0 audit must remain authoritative evidence")
    if state["pre_gpu_candidate_gates"]["summary"]["total"] != 10: errors.append("pre-GPU survivor gate must cover all ten shortlisted candidates")
    if state["pre_gpu_candidate_gates"]["summary"]["small_p0"] != 2: errors.append("pre-GPU survivor gate must expose exactly the two currently cleared small P0 candidates")
    if not state["pre_gpu_candidate_gates"]["policy"]["hold_or_inconclusive_is_not_method_failure"]: errors.append("HOLD/INCONCLUSIVE must remain scientifically neutral")
    if not state["pre_experiment_compiler"]["policy"]["updater_competence_required_before_gate_1"]: errors.append("Updater competence must be a hard prerequisite before Gate 1")
    if not state["pre_experiment_compiler"]["policy"]["updater_competence_is_not_a_ninth_gate"]: errors.append("Updater competence must not inflate the formal gate count beyond eight")
    if not state["pre_experiment_compiler"]["policy"]["all_eight_gates_required"]: errors.append("Pre-Experiment Compiler must require all eight gates")
    if not state["pre_experiment_compiler"]["policy"]["automatic_override_forbidden"]: errors.append("Pre-Experiment Compiler override must stay forbidden")
    if state["pre_experiment_compiler"]["summary"]["compiled_cards"] != 4: errors.append("expected four frozen pre-experiment cards")
    if not state["pilot_registry"]["policy"]["p0_execution_requires_pre_experiment_8_of_8"]: errors.append("P0 execution must require an 8/8 Pre-Experiment Card")
    if not state["pilot_registry"]["policy"]["automatic_p0_to_p1_forbidden"]: errors.append("automatic P0-to-P1 escalation must stay forbidden")
    if not state["experiment_iteration"]["policy"]["nonidentifiable_pilot_cannot_update_scientific_belief"]: errors.append("non-identifiable pilots must not update scientific belief")
    if state["mem_xfer_workflow"]["full_table"]["status"] != "full_table_collected": errors.append("mem-xfer full table must remain collected immutable evidence")
    if state["mem_xfer_workflow"]["offline_analysis"]["status"] != "offline_analysis_complete": errors.append("mem-xfer offline analysis must automatically follow a complete full table")
    if state["mem_xfer_workflow"]["support_qualification"]["status"] != "support_qualification_pass": errors.append("mem-xfer support qualification must remain PASS before the frozen full-support table")
    if state["mem_xfer_workflow"]["full_support"]["status"] != "full_support_complete": errors.append("mem-xfer frozen 216-execution Qwen full-support table must be complete")
    if state["mem_xfer_workflow"]["support_enriched_analysis"]["status"] != "support_enriched_analysis_complete": errors.append("mem-xfer CPU-only #3/#5 downstream gate must automatically follow the complete full-support table")
    if (state["mem_xfer_workflow"]["support_enriched_analysis"].get("decision") or {}).get("method_failure_authorized") is not False: errors.append("mem-xfer support gate must not authorize method failure from support insufficiency")
    provenance = state["mem_xfer_workflow"]["full_support"].get("provenance_recovery") or {}
    if provenance.get("decision") != "PROVENANCE_INCONCLUSIVE": errors.append("mem-xfer final provenance recovery must record the matched-hardware inconclusive terminal result")
    if state["mem_xfer_workflow"]["full_support"].get("scientific_authority") != "provenance-inconclusive": errors.append("mem-xfer full table must remain diagnostic-only after provenance mismatch")
    if state["mem_xfer_workflow"]["second_model"]["status"] != "second_model_hold": errors.append("mem-xfer second backbone must remain on HOLD unless the CPU-only full-support gate explicitly authorizes it")
    terminal_summary = state["human_terminal_ideas"]["summary"]
    if terminal_summary.get("human_parents") != 26 or (terminal_summary.get("p0"), terminal_summary.get("p0_ready"), terminal_summary.get("merge"), terminal_summary.get("drop")) != (13,0,6,7): errors.append("human terminal ledger mismatch")
    if state["p0_admission"]["summary"].get("active_p0") != 20 or state["p0_admission"]["summary"].get("admitted") != 20 or state["p0_admission"]["summary"].get("transitioned_from_p0_ready") != 16 or state["p0_admission"]["summary"].get("settings_complete") != 20: errors.append("P0 admission ledger mismatch")
    if state["p0_offline_qualification"]["summary"].get("ideas") != 16 or state["p0_offline_qualification"]["policy"].get("method_result_from_offline_qualification_forbidden") is not True: errors.append("P0 offline qualification policy mismatch")
    if state["p0_realizability"]["summary"].get("audited") != 14 or state["p0_realizability"]["policy"].get("cannot_emit_method_result") is not True: errors.append("P0 realizability policy mismatch")
    if state["repair_queue"]["policy"].get("terminal_human_parent_repair_forbidden") is not True or state["repair_queue"]["policy"].get("absorbed_child_repair_forbidden") is not True: errors.append("terminal repair policy missing")
    if state["pilot_registry"]["summary"]["invalid_approval_files"] != 0: errors.append("invalid pilot approval files")
    if not state["summary"]["final_ready"] or state["summary"]["final_pass"] != state["summary"]["discussion_target"]: errors.append("final advisor gate not ready")
    return errors


def write_research_system_state(json_path:Path=DEFAULT_JSON, js_path:Path=DEFAULT_JS) -> dict[str, Any]:
    write_human_terminal_state()
    write_p0_realizability_suite()
    write_b10_cpu_p0()
    write_a6_cpu_p0()
    write_p0_offline_qualification_state()
    write_p0_admission_state()
    state=build_research_system_state()
    errors=validate_state(state)
    if errors: raise ValueError("Invalid research system state:\n- " + "\n- ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    js_path.write_text("window.RESEARCH_SYSTEM_STATE = "+json.dumps(state, ensure_ascii=False, separators=(",",":"))+";\n", encoding="utf-8")
    return state
