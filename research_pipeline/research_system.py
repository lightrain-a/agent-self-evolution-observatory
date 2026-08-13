from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings, resolve_experiment_data_root
from .ai_consultation_clinic import build_ai_consultation_clinic_state, write_ai_consultation_clinic_state
from .ai_consultation_automation import DEFAULT_JSON as AI_CONSULTATION_AUTOMATION_JSON, PUBLIC_POLICY as AI_AUTOMATION_POLICY
from .discussion_portfolio import build_discussion_portfolio
from .evidence_graph import build_evidence_graph
from .evidence_integrity import build_evidence_integrity_state
from .experiment_iteration import build_experiment_iteration_state
from .experiment_value_scheduler import build_experiment_value_scheduler
from .external_system_learning import build_external_system_learning_state
from .failure_asset_library import build_failure_asset_library
from .human_terminal_state import build_human_terminal_state, write_human_terminal_state
from .governance_protocol import build_governance_state, write_governance_state
from .resource_lease import list_gpu_leases
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
from .literature_retrieval_audit import build_literature_retrieval_audit
from .methodology_controls import build_methodology_controls_state
from .pilot_registry import build_pilot_registry
from .p0_mem_xfer_offline_analysis import build_mem_xfer_workflow_state
from .paper_design_contract import build_paper_first_workflow_state
from .paper_first_design_adjudication import build_paper_first_design_adjudication, write_paper_first_design_adjudication
from .paper_first_pf1_problem_adjudication import build_pf1_problem_adjudication, write_pf1_problem_adjudication
from .paper_first_pf2_method_adjudication import build_pf2_method_adjudication, write_pf2_method_adjudication
from .paper_first_pf357_problem_adjudication import build_pf357_problem_adjudication, write_pf357_problem_adjudication
from .paper_first_fresh_saturation import build_fresh_saturation_state, write_fresh_saturation_state
from .paper_first_primary_evidence import load_primary_evidence_state
from .paper_first_problem_discovery_contract import DISCOVERY_LANES, FORBIDDEN_DISCOVERY_LANES, build_problem_discovery_contract_state
from .paper_first_problem_generator import load_problem_generator_state
from .paper_first_problem_gate_queue import load_problem_gate_queue_state
from .paper_first_post_c2_adjudication import build_post_c2_adjudication, write_post_c2_adjudication
from .paper_first_premature_method_diagnostics import resolve_premature_method_diagnostics, write_premature_method_diagnostics
from .p0_admission import build_p0_admission_state, write_p0_admission_state
from .p0_b10_cpu import write_b10_cpu_p0
from .p0_a6_cpu import write_a6_cpu_p0
from .p0_offline_qualification import build_p0_offline_qualification_state, write_p0_offline_qualification_state
from .p0_realizability_suite import build_p0_realizability_suite, write_p0_realizability_suite
from .p0_revived_batch_f0 import build_revived_batch_f0, write_revived_batch_f0
from .p0_decision_ledger import build_p0_decision_ledger, write_p0_decision_ledger
from .p0_four_direction_iteration import build_four_direction_iteration, write_four_direction_iteration
from .paper_first_p0_f0 import resolve_paper_first_p0_f0_state, write_paper_first_p0_f0_state
from .paper_first_p0_promotions import AUTHORITY as PAPER_FIRST_P0_AUTHORITY, promotion_summary as paper_first_p0_promotion_summary
from .persistent_updater_program_final import build_persistent_updater_program_final, write_persistent_updater_program_final
from .pre_experiment_compiler import compile_from_path as compile_pre_experiment_from_path
from .pre_experiment_specs import GATES as PRE_EXPERIMENT_GATES, POLICY as PRE_EXPERIMENT_POLICY
from .pre_p0_identifiability import build_pre_p0_identifiability_audit
from .pre_gpu_candidate_gates import build_pre_gpu_candidate_gate_state
from .principle_adjudication import build_principle_layer_state
from .research_capability_registry import build_research_capability_registry
from .public_state_redaction import redact_private_paths
from .research_system_replay import build_research_system_replay
from .review_repair import build_repair_queue
from .scientific_meta_trace import build_scientific_meta_trace
from .system_architecture import annotate_components, build_system_architecture

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

# The four paper-first PF configs are preserved as design/execution provenance, but
# they are not live Pre-Experiment authority until an external human P0-promotion
# artifact exists. Their already-executed local F0 rows are quarantined separately.


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
                "schema_version": "2.3", "config": config_file.name, "status": "compile-error",
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
        "schema_version": "2.3",
        "experiment_data_root": str(experiment_data_root),
        "policy": PRE_EXPERIMENT_POLICY,
        "gates": list(PRE_EXPERIMENT_GATES),
        "summary": {
            "compiled_cards": len(cards),
            "paper_design_pass": sum(bool((row.get("paper_design_prerequisite") or {}).get("passed")) for row in cards),
            "paper_design_blocked": sum(not bool((row.get("paper_design_prerequisite") or {}).get("passed")) for row in cards),
            "execution_ready": sum(bool(row.get("execution_authorized")) for row in cards),
            "blocked": sum(not bool(row.get("execution_authorized")) for row in cards),
            "principle_certificate_pass": sum(bool((row.get("principle_certificate_prerequisite") or {}).get("passed")) for row in cards),
            "principle_certificate_fail": sum(not bool((row.get("principle_certificate_prerequisite") or {}).get("passed")) for row in cards),
            "protocol_validity_pass": sum(bool((row.get("protocol_validity_prerequisite") or {}).get("passed")) for row in cards),
            "protocol_validity_fail": sum(not bool((row.get("protocol_validity_prerequisite") or {}).get("passed")) for row in cards),
            "research_execution_plans": sum(bool(row.get("research_execution_plan")) for row in cards),
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
    capabilities = state["research_capability_registry"]["summary"]
    literature_audit = state["literature_retrieval_audit"]["summary"]
    evidence_integrity = state["evidence_integrity"]["summary"]
    collisions = state["collision_engine"]["summary"]
    lineage = state["lineage"]["summary"]
    pilots = state["pilot_registry"]["summary"]
    pre_p0 = state["pre_p0_identifiability"]["summary"]
    pre_experiment = state["pre_experiment_compiler"]["summary"]
    paper_first = state["paper_first_workflow"]["summary"]
    paper_post_c2 = state["paper_first_post_c2"]
    principle = state["principle_layer"]["summary"]
    meta_trace = state["scientific_meta_trace"]["summary"]
    failure_assets = state["failure_asset_library"]["summary"]
    value_scheduler = state["experiment_value_scheduler"]["summary"]
    replay = state["research_system_replay"]["summary"]
    external_learning = state["external_system_learning"]["summary"]
    economy = state["p0_economy_gate"]["summary"]
    p0_ledger = state["p0_decision_ledger"]["summary"]
    ai_clinic = state["ai_consultation_clinic"]["summary"]
    ai_automation = state["ai_consultation_automation"]["summary"]
    governance = state["research_governance_v2"]
    iteration = state["experiment_iteration"]["summary"]
    repairs = state["repair_queue"]["summary"]
    terminal = state["human_terminal_ideas"]["summary"]
    discovery = state["idea_discovery_v3"]["summary"]
    repaired = state["idea_discovery_v31"]["summary"]
    v4 = state["idea_discovery_v4"]["summary"]
    v5 = state["idea_discovery_v5"]["summary"]
    return [
        {"source":"ResearchAgent", "component":{"en":"Citation and evidence graph","zh":"引文与证据图谱"}, "status":"running", "evidence":{"en":f"{graph['nodes']} nodes / {graph['edges']} edges","zh":f"{graph['nodes']} 个节点 / {graph['edges']} 条边"}},
        {"source":"Biomni / BioMedAgent / PaperQA2", "component":{"en":"Declarative research capability registry","zh":"声明式科研能力注册表"}, "status":"running", "evidence":{"en":f"{capabilities['capabilities']} typed capabilities / {capabilities['high_risk']} high-risk / least-privilege routing","zh":f"{capabilities['capabilities']} 类 typed capability / {capabilities['high_risk']} 类高风险 / 最小权限路由"}},
        {"source":"AutoResearchBench / PaperQA2 / SciNetBench / ScientistOne / verifier calibration", "component":{"en":"Literature retrieval + Evidence Integrity layer","zh":"文献检索 + Evidence Integrity 层"}, "status":"running", "evidence":{"en":f"{literature_audit['retrieval_modes']} retrieval modes / {evidence_integrity['claim_types']} claim types / verifier {evidence_integrity['verifier_calibration_status']}","zh":f"{literature_audit['retrieval_modes']} 类检索模式 / {evidence_integrity['claim_types']} 类 claim / verifier {evidence_integrity['verifier_calibration_status']}"}},
        {"source":"AI-Researcher", "component":{"en":"Hybrid semantic deduplication and collision filtering","zh":"混合语义去重与碰撞过滤"}, "status":"running", "evidence":{"en":f"{collisions['pairwise_comparisons']} pair comparisons / {collisions['flagged_pairs']} flagged","zh":f"{collisions['pairwise_comparisons']} 组两两比较 / {collisions['flagged_pairs']} 个标记"}},
        {"source":"MOOSE-Chem / Deep-Ideation", "component":{"en":"Idea lineage and branch preservation","zh":"Idea 谱系与分支保留"}, "status":"running", "evidence":{"en":f"{lineage['idea_nodes']} ideas / {lineage['edges']} lineage edges","zh":f"{lineage['idea_nodes']} 个 Idea / {lineage['edges']} 条谱系边"}},
        {"source":"Human terminal ledger", "component":{"en":"Terminalized human-parent lifecycle controller","zh":"人工 Parent 终态生命周期控制器"}, "status":"running", "evidence":{"en":f"26 parents: {terminal['p0']} P0 / {terminal['p0_ready']} P0-ready / {terminal['merge']} merged / {terminal['drop']} dropped","zh":f"26 个 Parent：{terminal['p0']} P0 / {terminal['p0_ready']} P0 Ready / {terminal['merge']} 合并 / {terminal['drop']} 停止"}},
        {"source":"CycleResearcher", "component":{"en":"Role-separated review repair queue","zh":"角色分离的审查修订队列"}, "status":"running", "evidence":{"en":f"{repairs['queued_ideas']} repair candidates after terminal filtering","zh":f"终态过滤后 {repairs['queued_ideas']} 个修订候选"}},
        {"source":"ResearchAgent / MOOSE-Chem / SciAgents / AI-Scientist-v2 / RD-Agent", "component":{"en":"Solution-first branch search","zh":"解决方案优先的分支搜索"}, "status":"running", "evidence":{"en":f"{discovery['raw_children']} v3 children / {discovery['external_revise']} R2 revise / {repaired['children']} v3.1 repairs","zh":f"{discovery['raw_children']} 个 v3 子节点 / {discovery['external_revise']} 个 R2 REVISE / {repaired['children']} 个 v3.1 修订"}},
        {"source":"ResearchAgent / MOOSE-Chem / Co-Scientist / HypoRefine / Virtual Scientists / autoresearch", "component":{"en":"Constrained composition and conditional revival","zh":"受约束组合与条件复活"}, "status":"running", "evidence":{"en":f"{v4['raw_candidates']} v4 candidates / {v4['tournament_finalists']} finalists / {v4['external_reviewed']} reviewed","zh":f"{v4['raw_candidates']} 个 v4 候选 / {v4['tournament_finalists']} 个 finalists / {v4['external_reviewed']} 个已复核"}},
        {"source":"HypoRefine / IdeaForge / ScholarEval / InnoEval / SciAtlas / InternAgent / AutoScientists", "component":{"en":"Wide-search simplification-challenge ideation","zh":"宽搜索与简化挑战式 Idea 发现"}, "status":"running", "evidence":{"en":f"{v5['raw_candidates']} v5 candidates / {v5['external_reviewed']} R2 reviewed / {v5['external_pass']} PASS","zh":f"{v5['raw_candidates']} 个 v5 候选 / {v5['external_reviewed']} 个 R2 已审 / {v5['external_pass']} 个 PASS"}},
        {"source":"AIDE / AI-Scientist-v2 / R&D-Agent", "component":{"en":"Pre-P0 identifiability auditor","zh":"Pre-P0 实验可识别性审计"}, "status":"running", "evidence":{"en":f"{pre_p0['execution_ready']}/{pre_p0['audited']} retrospective contracts execution-ready","zh":f"当前 {pre_p0['execution_ready']}/{pre_p0['audited']} 份 retrospective 合同允许启动"}},
        {"source":"Advisor paper-first research contract", "component":{"en":"Paper novelty → method → experiment blueprint contract","zh":"论文 Novelty → 方法 → 实验蓝图合同"}, "status":"running", "evidence":{"en":f"{paper_first['paper_design_passed']}/{paper_first['cards']} current cards satisfy the paper-first contract / post-C2: {paper_post_c2['decision']} / C3 locked={paper_post_c2['authority']['C3_locked']}","zh":f"当前 {paper_first['paper_design_passed']}/{paper_first['cards']} 份卡满足 paper-first 合同 / post-C2：{paper_post_c2['decision']} / C3 锁定={paper_post_c2['authority']['C3_locked']}"}},
        {"source":"FirstResearch / Popper / Co-Scientist / RD-Agent", "component":{"en":"Principle Certificate + epistemic adjudicator","zh":"原理证书 + 认识论裁决器"}, "status":"running", "evidence":{"en":f"{principle['certificates_passed']}/{principle['cards']} principle certificates valid / {principle['principle_falsifications']} principle falsifications","zh":f"{principle['certificates_passed']}/{principle['cards']} 份原理证书有效 / {principle['principle_falsifications']} 个原理级否定"}},
        {"source":"Qiushi / Kosmos / MLEvolve", "component":{"en":"Scientific Meta-Trace + cross-branch world state","zh":"Scientific Meta-Trace + 跨分支科研状态"}, "status":"running", "evidence":{"en":f"{meta_trace['principles']} principles / {meta_trace['unresolved_principles']} unresolved / {meta_trace['cross_branch_reference_edges']} cross-branch links","zh":f"{meta_trace['principles']} 个原理 / {meta_trace['unresolved_principles']} 个未决 / {meta_trace['cross_branch_reference_edges']} 条跨分支引用"}},
        {"source":"MLEvolve / InternAgent / AutoResearchClaw", "component":{"en":"Failure Asset + dead-end memory","zh":"失败资产 + Dead-End 记忆库"}, "status":"running", "evidence":{"en":f"{failure_assets['assets']} failure assets / {failure_assets['unique_signatures']} reusable signatures / {failure_assets['economy_dead_ends']} economy dead ends","zh":f"{failure_assets['assets']} 条失败资产 / {failure_assets['unique_signatures']} 类可复用签名 / {failure_assets['economy_dead_ends']} 个 Economy dead end"}},
        {"source":"Ai2 AutoDiscovery / MLEvolve / AI-Scientist-v2", "component":{"en":"Information-gain experiment portfolio scheduler","zh":"信息增益实验组合调度器"}, "status":"running", "evidence":{"en":f"{value_scheduler['candidates']} candidate tests / {value_scheduler['cross_branch_reference_edges']} cross-branch references / advisory only","zh":f"{value_scheduler['candidates']} 个候选实验 / {value_scheduler['cross_branch_reference_edges']} 条跨分支引用 / 仅建议不授权"}},
        {"source":"ResearchClawBench / HackDetect / ScienceAgentBench / AutoLabs", "component":{"en":"Protocol-validity auditor + research-system replay benchmark","zh":"协议有效性审计 + 科研系统回放基准"}, "status":"running", "evidence":{"en":f"protocol {pre_experiment['protocol_validity_pass']}/{pre_experiment['compiled_cards']} / replay {replay['passed']}/{replay['cases']}","zh":f"Protocol {pre_experiment['protocol_validity_pass']}/{pre_experiment['compiled_cards']} / 回放 {replay['passed']}/{replay['cases']}"}},
        {"source":"External-system intake registry", "component":{"en":"Continuous external research-system learning","zh":"持续外部科研系统学习"}, "status":"running", "evidence":{"en":f"{external_learning['systems_reviewed']} systems / {external_learning['adopted']} adopted / {external_learning['next_backlog']} next backlog","zh":f"已审 {external_learning['systems_reviewed']} 个系统 / {external_learning['adopted']} 个已吸收 / {external_learning['next_backlog']} 个下一批"}},
        {"source":"P0 retrospective economy review", "component":{"en":"Five-gate P0 Economy layer","zh":"P0 五门资源经济层"}, "status":"running", "evidence":{"en":f"{economy['matched_simplification_stops']} matched-simplification stops / {economy['substrate_stops']} substrate stops / {economy['economy_ready']} currently economy-ready","zh":f"{economy['matched_simplification_stops']} 个简化基线 STOP / {economy['substrate_stops']} 个底座 STOP / 当前 {economy['economy_ready']} 个 Economy-ready"}},
        {"source":"Web GPT + domestic-model independent consultation", "component":{"en":"Five-checkpoint AI consultation clinic","zh":"五节点 AI 会诊诊断层"}, "status":"running", "evidence":{"en":f"{ai_clinic['checkpoints']} checkpoints / {ai_clinic['pre_gpu_checkpoints']} before GPU / zero AI-authoritative checkpoints","zh":f"{ai_clinic['checkpoints']} 个会诊节点 / {ai_clinic['pre_gpu_checkpoints']} 个位于 GPU 前 / AI 直接授权节点为 0"}},
        {"source":"Content-addressed AI consultation automation", "component":{"en":"Automatic consultation trigger queue","zh":"AI 会诊自动触发队列"}, "status":"running", "evidence":{"en":f"baseline={ai_automation.get('baseline_initialized')} / {ai_automation.get('cases',0)} cases / {ai_automation.get('pending',0)} pending / {ai_automation.get('unresolved_high_risk',0)} unresolved high-risk","zh":f"baseline={ai_automation.get('baseline_initialized')} / {ai_automation.get('cases',0)} 个 case / {ai_automation.get('pending',0)} 个待执行 / {ai_automation.get('unresolved_high_risk',0)} 个未处置高风险"}},
        {"source":"Unified P0 decision ledger", "component":{"en":"Current experiment-decision ledger","zh":"统一 P0 当前决策账本"}, "status":"running", "evidence":{"en":f"{p0_ledger['active_p0']} active rows / {p0_ledger['experiment_stopped']} stopped awaiting review / {p0_ledger['launchable']} launchable","zh":f"{p0_ledger['active_p0']} 条活跃记录 / {p0_ledger['experiment_stopped']} 条实验 STOP 待人工 / {p0_ledger['launchable']} 条可启动"}},
        {"source":"P0-System v2", "component":{"en":"Stage governance, repair budgets, trace contracts, and resource leases","zh":"阶段治理、修复预算、Trace 合同与资源租约"}, "status":"running", "evidence":{"en":f"{len(governance['stages'])} scientific stages / {len(governance['failure_classes'])} typed failure classes / {governance['runtime']['active_gpu_leases']} active GPU leases","zh":f"{len(governance['stages'])} 个科学阶段 / {len(governance['failure_classes'])} 类失败语义 / {governance['runtime']['active_gpu_leases']} 个活跃 GPU 租约"}},
        {"source":"AIDE / AI-Scientist-v2 / R&D-Agent / SCION", "component":{"en":"Updater prerequisite + derived Research Execution Plan + eight-gate Pre-Experiment Compiler","zh":"Updater 前置 + 派生 Research Execution Plan + 八门实验启动前编译器"}, "status":"running", "evidence":{"en":f"REP {pre_experiment['research_execution_plans']}/{pre_experiment['compiled_cards']} / updater prerequisite {pre_experiment['updater_prerequisite_pass']}/{pre_experiment['compiled_cards']} / launch-ready {pre_experiment['execution_ready']}/{pre_experiment['compiled_cards']}","zh":f"REP {pre_experiment['research_execution_plans']}/{pre_experiment['compiled_cards']} / Updater prerequisite {pre_experiment['updater_prerequisite_pass']}/{pre_experiment['compiled_cards']} / 可启动 {pre_experiment['execution_ready']}/{pre_experiment['compiled_cards']}"}},
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


def _load_ai_consultation_automation_public() -> dict[str, Any]:
    try:
        payload = json.loads(AI_CONSULTATION_AUTOMATION_JSON.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except (OSError, json.JSONDecodeError):
        pass
    return {
        "schema_version": "1.0",
        "generated_at": None,
        "policy": AI_AUTOMATION_POLICY,
        "clinic_policy": {
            "ai_vote_can_authorize_gpu": False,
            "ai_vote_can_authorize_second_backbone": False,
            "ai_vote_can_emit_method_pass_fail": False,
            "high_risk_findings_must_be_compiled_into_machine_checks": True,
        },
        "finding_dispositions": [],
        "summary": {
            "baseline_initialized": False,
            "baseline_subjects": 0,
            "cases": 0,
            "created_this_cycle": 0,
            "executed_this_cycle": 0,
            "pending": 0,
            "partial": 0,
            "complete": 0,
            "reviewer_unavailable": 0,
            "retryable": 0,
            "waived_cases": 0,
            "unresolved_high_risk": 0,
        },
        "recent_cases": [],
    }


def build_research_system_state() -> dict[str, Any]:
    storage = StorageSettings.from_env()
    corpus = _load_corpus_with_site_fallback()
    idea_bank = build_iclr_idea_bank()
    evidence_graph = build_evidence_graph(corpus, idea_bank)
    research_capability_registry = build_research_capability_registry()
    literature_retrieval_audit = build_literature_retrieval_audit(evidence_graph, corpus)
    evidence_integrity = build_evidence_integrity_state()
    methodology_controls = build_methodology_controls_state()
    collision_engine = analyze_collisions(idea_bank)
    lineage = build_lineage(idea_bank, collision_engine)
    pre_p0_identifiability = build_pre_p0_identifiability_audit(idea_bank)
    pre_experiment_compiler = _build_pre_experiment_state(storage)
    paper_first_workflow = build_paper_first_workflow_state(pre_experiment_compiler)
    paper_first_design = build_paper_first_design_adjudication()
    paper_first_pf1_problem = build_pf1_problem_adjudication()
    paper_first_pf2_method = build_pf2_method_adjudication()
    paper_first_pf357 = build_pf357_problem_adjudication()
    paper_first_fresh_saturation = build_fresh_saturation_state()
    paper_first_primary_evidence = load_primary_evidence_state()
    paper_first_problem_discovery_contract = build_problem_discovery_contract_state()
    paper_first_problem_generator = load_problem_generator_state()
    paper_first_problem_memory = ((paper_first_problem_generator.get("saturation_memory") or {}).get("blocked_problem_memory") or {})
    paper_first_lane_search = paper_first_problem_generator.get("search_diagnostics") or {}
    paper_first_problem_gate_queue = load_problem_gate_queue_state()
    paper_first_post_c2 = build_post_c2_adjudication()
    formal_cards = {
        str(card.get("idea_id")): card
        for card in pre_experiment_compiler.get("cards") or []
        if card.get("phase") == "P0" and card.get("idea_id")
    }
    experiment_data_root = resolve_experiment_data_root(storage)
    paper_first_premature_method_diagnostics = resolve_premature_method_diagnostics(experiment_data_root)
    research_governance_v2 = build_governance_state()
    research_governance_v2["runtime"] = {
        "active_gpu_leases": len(list_gpu_leases(experiment_data_root, True)),
        "lease_root": str(experiment_data_root / "resource-leases"),
        "repair_budget_root": str(experiment_data_root / "governance" / "repair-budget"),
    }
    mem_xfer_workflow = build_mem_xfer_workflow_state(experiment_data_root)
    pilot_registry = build_pilot_registry(
        idea_bank,
        result_dir=experiment_data_root / "runs" / "pilots" / "results",
        approval_dir=experiment_data_root / "runs" / "pilots" / "approvals",
        pre_p0_audit=pre_p0_identifiability,
        pre_experiment_cards=formal_cards,
    )
    experiment_iteration = build_experiment_iteration_state()
    principle_layer = build_principle_layer_state(pre_experiment_compiler.get("cards") or [], experiment_iteration.get("nodes") or [])
    pre_gpu_candidate_gates = build_pre_gpu_candidate_gate_state()
    human_terminal_ideas = build_human_terminal_state()
    p0_realizability = build_p0_realizability_suite()
    p0_revived_batch = build_revived_batch_f0()
    paper_first_p0_f0 = resolve_paper_first_p0_f0_state(experiment_data_root)
    paper_first_p0_authority = {"schema_version":"1.0", "authority":PAPER_FIRST_P0_AUTHORITY, "summary":paper_first_p0_promotion_summary()}
    p0_offline_qualification = build_p0_offline_qualification_state()
    p0_admission = build_p0_admission_state()
    four_direction_iteration = build_four_direction_iteration()
    persistent_updater_program_final = build_persistent_updater_program_final()
    ai_consultation_clinic = build_ai_consultation_clinic_state()
    ai_consultation_automation = _load_ai_consultation_automation_public()
    p0_admission_public = {"summary": p0_admission["summary"], "policy": p0_admission["policy"]}
    ai_consultation_public = {"summary": ai_consultation_clinic["summary"], "policy": ai_consultation_clinic["policy"], "panel": ai_consultation_clinic["panel"], "checkpoints": ai_consultation_clinic["checkpoints"], "finding_dispositions": ai_consultation_clinic["finding_dispositions"]}
    ai_consultation_automation_public = {
        "summary": ai_consultation_automation.get("summary") or {},
        "policy": ai_consultation_automation.get("policy") or AI_AUTOMATION_POLICY,
        "clinic_policy": ai_consultation_automation.get("clinic_policy") or {},
        "finding_dispositions": ai_consultation_automation.get("finding_dispositions") or [],
        "recent_cases": ai_consultation_automation.get("recent_cases") or [],
    }
    p0_economy_gate = p0_admission["economy_gate"]
    p0_economy_public = {"summary": p0_economy_gate["summary"], "policy": p0_economy_gate["policy"], "gates": p0_economy_gate["gates"]}
    p0_decision_ledger = build_p0_decision_ledger(p0_admission, p0_offline_qualification, human_terminal_ideas, four_direction_iteration)
    p0_decision_ledger_public = {"summary": p0_decision_ledger["summary"], "policy": p0_decision_ledger["policy"]}
    scientific_meta_trace = build_scientific_meta_trace(pre_experiment_compiler, principle_layer, experiment_iteration, p0_decision_ledger_public)
    failure_asset_library = build_failure_asset_library(experiment_iteration, p0_economy_public, paper_first_post_c2, paper_first_p0_f0)
    experiment_value_scheduler = build_experiment_value_scheduler(experiment_iteration, scientific_meta_trace)
    research_system_replay = build_research_system_replay(pre_experiment_compiler)
    external_system_learning = build_external_system_learning_state()
    p0_offline_public = {"summary": p0_offline_qualification["summary"], "policy": p0_offline_qualification["policy"]}
    p0_realizability_public = {"summary": p0_realizability["summary"], "policy": p0_realizability["policy"]}
    p0_revived_batch_public = {"summary": p0_revived_batch["summary"], "policy": p0_revived_batch["policy"], "parent_batch": p0_revived_batch["parent_batch"]}
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
            "weekly":{"schedule":"Monday 03:15 server local time", "mode":"literature-sync-plus-bounded-idea-and-research-system-reviews"},
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
            "research_capabilities":research_capability_registry["summary"]["capabilities"],
            "literature_retrieval_modes":literature_retrieval_audit["summary"]["retrieval_modes"],
            "literature_benchmark_status":literature_retrieval_audit["summary"]["benchmark_status"],
            "evidence_integrity_claim_types":evidence_integrity["summary"]["claim_types"],
            "evidence_verifier_calibration_status":evidence_integrity["summary"]["verifier_calibration_status"],
            "methodology_cross_cutting_controls":methodology_controls["summary"]["controls"],
            "methodology_primary_components_added":methodology_controls["summary"]["primary_components_added"],
            "collision_flags":collision_engine["summary"]["flagged_pairs"],
            "lineage_edges":lineage["summary"]["edges"],
            "pilot_results":pilot_registry["summary"]["valid_result_files"],
            "pre_p0_audited":pre_p0_identifiability["summary"]["audited"],
            "pre_p0_ready":pre_p0_identifiability["summary"]["execution_ready"],
            "pre_experiment_cards":pre_experiment_compiler["summary"]["compiled_cards"],
            "paper_design_contract_passed":paper_first_workflow["summary"]["paper_design_passed"],
            "paper_design_contract_blocked":paper_first_workflow["summary"]["paper_design_blocked"],
            "paper_first_design_reviewed":paper_first_design["summary"]["reviewed"],
            "paper_first_design_advance_method":paper_first_design["summary"]["advance_to_method_design"],
            "paper_first_design_revise_problem":paper_first_design["summary"]["revise_paper_problem"],
            "paper_first_design_merge_invariant":paper_first_design["summary"]["merge_as_cross_cutting_invariant"],
            "paper_first_design_stop_standalone":paper_first_design["summary"]["stop_standalone_merge_risk_axis"],
            "paper_first_pf1_problem_decision":paper_first_pf1_problem["decision"],
            "paper_first_pf1_problem_active":paper_first_pf1_problem["authority"]["paper_problem_active"],
            "paper_first_pf1_method_design_authorized":paper_first_pf1_problem["authority"]["method_design_authorized"],
            "paper_first_pf2_method_decision":paper_first_pf2_method["decision"],
            "paper_first_pf2_method_active":paper_first_pf2_method["authority"]["method_thesis_active"],
            "paper_first_pf2_experiment_blueprint_authorized":paper_first_pf2_method["authority"]["experiment_blueprint_authorized"],
            "paper_first_pf357_reviewed":paper_first_pf357["summary"]["reviewed"],
            "paper_first_pf357_stopped":paper_first_pf357["summary"]["stopped_standalone"],
            "paper_first_fresh_drafts_reviewed":paper_first_fresh_saturation["summary"]["drafts_reviewed"],
            "paper_first_fresh_survivors":paper_first_fresh_saturation["summary"]["survivors"],
            "paper_first_fresh_stopped":paper_first_fresh_saturation["summary"]["stopped"],
            "paper_first_primary_evidence_status":paper_first_primary_evidence.get("status"),
            "paper_first_primary_evidence_verified":(paper_first_primary_evidence.get("summary") or {}).get("verified",0),
            "paper_first_primary_fact_extraction_version":(paper_first_primary_evidence.get("policy") or {}).get("empirical_fact_extraction_version"),
            "paper_first_primary_typed_extraction_version":(paper_first_primary_evidence.get("policy") or {}).get("typed_evidence_extraction_version"),
            "paper_first_primary_source_scheduler_active":bool((paper_first_primary_evidence.get("summary") or {}).get("source_coverage_scheduler_active")),
            "paper_first_primary_source_scheduler_prior_runs":(paper_first_primary_evidence.get("summary") or {}).get("saturation_ledger_runs",0),
            "paper_first_primary_selected_reviewed":(paper_first_primary_evidence.get("summary") or {}).get("selected_previously_reviewed",0),
            "paper_first_primary_selected_unreviewed":(paper_first_primary_evidence.get("summary") or {}).get("selected_unreviewed",0),
            "paper_first_primary_lane_linked_reviewed":(paper_first_primary_evidence.get("summary") or {}).get("reviewed_lane_linked_sources",0),
            "paper_first_primary_lane_linked_unreviewed":(paper_first_primary_evidence.get("summary") or {}).get("unreviewed_lane_linked_sources",0),
            "paper_first_primary_source_coverage_exhausted":bool((paper_first_primary_evidence.get("summary") or {}).get("source_coverage_exhausted")),
            "paper_first_primary_generation_ready":bool((paper_first_primary_evidence.get("summary") or {}).get("candidate_generation_ready")),
            "paper_first_problem_gate_fields":paper_first_problem_discovery_contract["summary"]["required_top_level_fields"],
            "paper_first_problem_gate_saturation_patterns":paper_first_problem_discovery_contract["summary"]["saturation_patterns"],
            "paper_first_problem_generator_status":paper_first_problem_generator.get("status"),
            "paper_first_problem_generator_generated":(paper_first_problem_generator.get("summary") or {}).get("generated",0),
            "paper_first_problem_generator_semantic_clear":(paper_first_problem_generator.get("summary") or {}).get("semantic_clear",0),
            "paper_first_problem_generator_semantic_blocked":(paper_first_problem_generator.get("summary") or {}).get("semantic_blocked",0),
            "paper_first_problem_generator_saturation_entries":(paper_first_problem_generator.get("saturation_memory") or {}).get("ledger_entries",0),
            "paper_first_problem_generator_prior_identical_zero":(paper_first_problem_generator.get("saturation_memory") or {}).get("prior_identical_zero_runs",0),
            "paper_first_problem_blocked_attempts":paper_first_problem_memory.get("blocked_candidate_attempts",0),
            "paper_first_problem_top_reduction_basin":(paper_first_problem_memory.get("top_reduction_basin") or {}).get("pattern",""),
            "paper_first_problem_top_reduction_count":(paper_first_problem_memory.get("top_reduction_basin") or {}).get("count",0),
            "paper_first_problem_repeated_reduction_basin":bool(paper_first_problem_memory.get("repeated_reduction_basin")),
            "paper_first_problem_search_escape_required":bool(paper_first_problem_memory.get("search_escape_required")),
            "paper_first_problem_lane_search_complete":bool(paper_first_lane_search.get("lane_search_complete")),
            "paper_first_problem_lane_search_candidate_lanes":sum(str(row.get("status") or "") == "CANDIDATE" for row in paper_first_lane_search.get("lane_search") or [] if isinstance(row,dict)),
            "paper_first_problem_lane_search_reducible_lanes":sum(str(row.get("status") or "") == "REDUCIBLE" for row in paper_first_lane_search.get("lane_search") or [] if isinstance(row,dict)),
            "paper_first_problem_lane_search_no_pair_lanes":sum(str(row.get("status") or "") == "NO_PAIR" for row in paper_first_lane_search.get("lane_search") or [] if isinstance(row,dict)),
            "paper_first_problem_lane_search_expanded_lanes":sum(str(row.get("status") or "") == "EXPANDED" for row in paper_first_lane_search.get("lane_search") or [] if isinstance(row,dict)),
            "paper_first_problem_lane_search_empty_lanes":sum(str(row.get("status") or "") == "EMPTY" for row in paper_first_lane_search.get("lane_search") or [] if isinstance(row,dict)),
            "paper_first_problem_queue_submitted":paper_first_problem_gate_queue["summary"]["submitted"],
            "paper_first_problem_queue_passed":paper_first_problem_gate_queue["summary"]["passed_problem_gate"],
            "paper_first_problem_queue_blocked":paper_first_problem_gate_queue["summary"]["blocked_problem_gate"],
            "paper_first_post_c2_decision":paper_first_post_c2["decision"],
            "paper_first_post_c2_current_formulation":paper_first_post_c2["current_paper_formulation_status"],
            "paper_first_post_c2_c3_locked":paper_first_post_c2["authority"]["C3_locked"],
            "paper_first_premature_method_diagnostics":paper_first_premature_method_diagnostics["summary"]["completed_diagnostics"],
            "paper_first_premature_method_reducibility_findings":paper_first_premature_method_diagnostics["summary"]["same_information_reducibility_findings"],
            "paper_first_premature_method_scientific_authority":paper_first_premature_method_diagnostics["summary"]["scientifically_authorized"],
            "pre_experiment_ready":pre_experiment_compiler["summary"]["execution_ready"],
            "pre_experiment_formal_ready":pre_experiment_compiler["summary"]["formal_p0_ready"],
            "research_execution_plans":pre_experiment_compiler["summary"]["research_execution_plans"],
            "experiment_diagnoses":experiment_iteration["summary"]["nodes"],
            "experiment_repair_children":experiment_iteration["summary"]["repair_children"],
            "experiment_scale_up":experiment_iteration["summary"]["scale_up_allowed"],
            "principle_certificates_passed":principle_layer["summary"]["certificates_passed"],
            "principle_falsifications":principle_layer["summary"]["principle_falsifications"],
            "protocol_validity_pass":pre_experiment_compiler["summary"]["protocol_validity_pass"],
            "meta_trace_unresolved":scientific_meta_trace["summary"]["unresolved_principles"],
            "failure_assets":failure_asset_library["summary"]["assets"],
            "value_scheduler_candidates":experiment_value_scheduler["summary"]["candidates"],
            "research_replay_passed":research_system_replay["summary"]["passed"],
            "external_systems_reviewed":external_system_learning["summary"]["systems_reviewed"],
            "repair_queue":repair_queue["summary"]["queued_ideas"],
            "human_terminal_parents":human_terminal_ideas["summary"]["human_parents"],
            "human_terminal_p0":human_terminal_ideas["summary"]["p0"],
            "human_terminal_p0_ready":human_terminal_ideas["summary"]["p0_ready"],
            "human_terminal_merge":human_terminal_ideas["summary"]["merge"],
            "human_terminal_drop":human_terminal_ideas["summary"]["drop"],
            "p0_admission_active":p0_admission["summary"]["active_p0"],
            "p0_admission_transitioned":p0_admission["summary"]["transitioned_from_p0_ready"],
            "p0_admission_settings_complete":p0_admission["summary"]["settings_complete"],
            "p0_admission_economy_ready":p0_admission["summary"]["economy_ready"],
            "p0_admission_execution_authorized":p0_admission["summary"]["execution_authorized"],
            "ai_consultation_checkpoints":ai_consultation_clinic["summary"]["checkpoints"],
            "ai_consultation_pre_gpu_checkpoints":ai_consultation_clinic["summary"]["pre_gpu_checkpoints"],
            "ai_consultation_automation_cases":(ai_consultation_automation.get("summary") or {}).get("cases",0),
            "ai_consultation_pending":(ai_consultation_automation.get("summary") or {}).get("pending",0),
            "ai_consultation_unresolved_high_risk":(ai_consultation_automation.get("summary") or {}).get("unresolved_high_risk",0),
            "p0_economy_matched_simplification_stops":p0_economy_gate["summary"]["matched_simplification_stops"],
            "p0_economy_substrate_stops":p0_economy_gate["summary"]["substrate_stops"],
            "p0_decision_ledger_stopped":p0_decision_ledger["summary"]["experiment_stopped"],
            "p0_decision_ledger_launchable":p0_decision_ledger["summary"]["launchable"],
            "persistent_updater_program_verdict":persistent_updater_program_final["verdict"],
            "persistent_updater_batch_authorized":persistent_updater_program_final["batch_experiment_authorized"],
            "governance_v2_stages":len(research_governance_v2["stages"]),
            "governance_v2_failure_classes":len(research_governance_v2["failure_classes"]),
            "governance_v2_active_gpu_leases":research_governance_v2["runtime"]["active_gpu_leases"],
            "p0_offline_checks_passed":p0_offline_qualification["summary"]["checks_passed"],
            "p0_offline_checks_failed":p0_offline_qualification["summary"]["checks_failed"],
            "p0_offline_checks_pending":p0_offline_qualification["summary"]["checks_pending"],
            "p0_realizability_passed":p0_realizability["summary"]["synthetic_pass"],
            "p0_batch_parent_p0":p0_revived_batch["summary"]["parent_p0"],
            "p0_batch_reused_existing":p0_revived_batch["summary"]["reused_existing_p0"],
            "p0_batch_fresh_cpu_f0":p0_revived_batch["summary"]["fresh_cpu_f0"],
            "p0_batch_matched_stops":p0_revived_batch["summary"]["fresh_matched_simplification_stop"],
            "p0_batch_upstream_holds":p0_revived_batch["summary"]["fresh_upstream_hold"],
            "p0_batch_gpu_candidates":p0_revived_batch["summary"]["gpu_queue_candidates_before_economy"],
            "paper_first_p0_promoted":paper_first_p0_authority["summary"]["promoted"],
            "paper_first_p0_authority_status":paper_first_p0_authority["summary"]["authority_status"],
            "paper_first_p0_f0_quarantined":paper_first_p0_f0["summary"]["quarantined"],
            "paper_first_p0_f0_running":paper_first_p0_f0["summary"]["running"],
            "paper_first_p0_f0_support_pass":paper_first_p0_f0["summary"]["support_pass"],
            "paper_first_p0_f0_support_hold":paper_first_p0_f0["summary"]["support_hold"],
            "paper_first_p0_f0_observed_support_pass":paper_first_p0_f0["summary"]["observed_support_pass"],
            "paper_first_p0_f0_observed_support_hold":paper_first_p0_f0["summary"]["observed_support_hold"],
            "p0_b10_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("b10",{}).get("decision"),
            "p0_a1_repair_decision":(human_terminal_ideas.get("parents") or {}).get("update-trust-region",{}).get("p0_decision"),
            "p0_a2_repair_decision":(human_terminal_ideas.get("parents") or {}).get("budgeted-evolution-controller",{}).get("p0_decision"),
            "p0_a3_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("a3_substrate_stop",{}).get("decision"),
            "p0_a4_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("a4_composition_cpu",{}).get("decision"),
            "p0_a5_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("a5_history_cpu",{}).get("decision"),
            "p0_a6_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("a6_cpu",{}).get("decision"),
            "p0_a7_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("a7_counterfactual_cpu",{}).get("decision"),
            "p0_b2_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("b2_support_stop",{}).get("decision"),
            "p0_b3_screening_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("b3_interference_cpu",{}).get("decision"),
            "p0_b3_support_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("b3_fresh_support_stop",{}).get("decision"),
            "p0_b3_real_decision":((p0_offline_qualification.get("shared_evidence") or {}).get("b3_real_cinteraction",{}).get("decision") or {}).get("decision"),
            "p0_b5_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("b5_applicability_cpu",{}).get("decision"),
            "p0_b6_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("b6_memory_utility_cpu",{}).get("decision"),
            "p0_c2_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("c2_evaluator_cpu",{}).get("decision"),
            "p0_d1_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("d1_minimal_curriculum_cpu",{}).get("decision"),
            "p0_e1_decision":(p0_offline_qualification.get("shared_evidence") or {}).get("e1_edit_table_stop",{}).get("decision"),
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
        "research_capability_registry":research_capability_registry,
        "literature_retrieval_audit":literature_retrieval_audit,
        "evidence_integrity":evidence_integrity,
        "methodology_controls":methodology_controls,
        "collision_engine":collision_engine,
        "lineage":lineage,
        "pre_p0_identifiability":pre_p0_identifiability,
        "pre_gpu_candidate_gates":pre_gpu_candidate_gates,
        "pre_experiment_compiler":pre_experiment_compiler,
        "paper_first_workflow":paper_first_workflow,
        "paper_first_design_adjudication":paper_first_design,
        "paper_first_pf1_problem_adjudication":paper_first_pf1_problem,
        "paper_first_pf2_method_adjudication":paper_first_pf2_method,
        "paper_first_pf357_problem_adjudication":paper_first_pf357,
        "paper_first_fresh_saturation":paper_first_fresh_saturation,
        "paper_first_primary_evidence":paper_first_primary_evidence,
        "paper_first_problem_discovery_contract":paper_first_problem_discovery_contract,
        "paper_first_problem_generator":paper_first_problem_generator,
        "paper_first_problem_gate_queue":paper_first_problem_gate_queue,
        "paper_first_post_c2":paper_first_post_c2,
        "paper_first_premature_method_diagnostics":paper_first_premature_method_diagnostics,
        "pilot_registry":pilot_registry,
        "experiment_iteration":experiment_iteration,
        "principle_layer":principle_layer,
        "scientific_meta_trace":scientific_meta_trace,
        "failure_asset_library":failure_asset_library,
        "experiment_value_scheduler":experiment_value_scheduler,
        "research_system_replay":research_system_replay,
        "external_system_learning":external_system_learning,
        "human_terminal_ideas":human_terminal_ideas,
        "p0_admission":p0_admission_public,
        "ai_consultation_clinic":ai_consultation_public,
        "ai_consultation_automation":ai_consultation_automation_public,
        "p0_economy_gate":p0_economy_public,
        "p0_decision_ledger":p0_decision_ledger_public,
        "p0_four_direction_iteration":{"policy":four_direction_iteration["policy"],"ideas":four_direction_iteration["ideas"],"source_authority_sha256":four_direction_iteration["source_authority_sha256"]},
        "persistent_updater_program_final":persistent_updater_program_final,
        "research_governance_v2":research_governance_v2,
        "p0_offline_qualification":p0_offline_public,
        "p0_realizability":p0_realizability_public,
        "p0_revived_batch_f0":p0_revived_batch_public,
        "paper_first_p0_authority":paper_first_p0_authority,
        "paper_first_p0_f0":paper_first_p0_f0,
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
    state["components"] = annotate_components(_component_manifest(state))
    state["system_architecture"] = build_system_architecture(state["components"], methodology_controls)
    state["summary"]["architecture_temporal_stages"] = state["system_architecture"]["summary"]["temporal_stages"]
    state["summary"]["architecture_functional_layers"] = state["system_architecture"]["summary"]["functional_layers"]
    state["health"] = _health(state, corpus)
    return state


def _mem_xfer_semantic_errors(workflow: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    allowed = set(workflow.get("allowed_statuses") or [])
    for key in ("full_table", "offline_analysis", "support_qualification", "full_support", "support_enriched_analysis", "applicability_falsifier", "mechanism_diagnosis", "second_model"):
        status = str((workflow.get(key) or {}).get("status") or "")
        if status and status not in allowed and status != "collecting": errors.append(f"mem-xfer invalid typed status {key}:{status}")
    support = workflow.get("support_qualification") or {}
    full = workflow.get("full_support") or {}
    analysis = workflow.get("support_enriched_analysis") or {}
    formal = workflow.get("formal_method") or {}
    second = workflow.get("second_model") or {}
    if full.get("authorized") and support.get("status") != "support_qualification_pass": errors.append("mem-xfer full support cannot be authorized before support PASS")
    decision = analysis.get("decision") or {}
    if decision and decision.get("method_failure_authorized") is True and decision.get("formal_method_experiment_authorized") is not True: errors.append("support insufficiency cannot authorize METHOD-FAIL")
    if formal.get("authorized") and analysis.get("status") != "support_enriched_analysis_complete": errors.append("formal method cannot open before completed support analysis")
    if second.get("authorized") and decision.get("second_model_authorized") is not True: errors.append("second backbone requires explicit support-analysis authorization")
    return errors


def _health(state: dict[str, Any], corpus: dict[str, Any]) -> dict[str, Any]:
    terminal_summary = state["human_terminal_ideas"]["summary"]
    expected_active_p0 = int(terminal_summary.get("p0") or 0) + int(terminal_summary.get("independent_methods") or 0)
    expected_pre_experiment_cards = len(PRE_EXPERIMENT_CONFIGS)
    portable_receipts = ((state.get("paper_first_problem_generator") or {}).get("saturation_memory") or {}).get("portable_review_receipts") or []
    portable_review_refs = {str(ref) for row in portable_receipts if isinstance(row,dict) and row.get("scientific_authority") is False for ref in row.get("source_refs") or [] if str(ref).startswith("arXiv:")}
    checks = [
        {"key":"corpus", "pass":bool(corpus.get("papers")), "detail":f"{len(corpus.get('papers') or [])} papers"},
        {"key":"evidence-coverage", "pass":state["evidence_graph"]["summary"]["ideas_with_semantic_evidence"] >= 20, "detail":state["evidence_graph"]["summary"]["ideas_with_semantic_evidence"]},
        {"key":"capability-and-literature-audit", "pass":state["research_capability_registry"]["policy"]["capabilities_are_declared_not_prompt_inferred"] and state["research_capability_registry"]["policy"]["model_or_tool_routing_cannot_escalate_scientific_authority"] and state["research_capability_registry"]["summary"]["capabilities"] >= 9 and state["literature_retrieval_audit"]["policy"]["deep_and_wide_retrieval_are_distinct_capabilities"] and state["literature_retrieval_audit"]["policy"]["citation_verifier_must_be_named_versioned_and_calibrated"] and state["literature_retrieval_audit"]["summary"]["benchmark_status"] == "spec-ready-not-yet-scored" and state["evidence_integrity"]["policy"]["every_publishable_claim_requires_evidence_chain"] and state["evidence_integrity"]["policy"]["uncalibrated_verifier_cannot_be_treated_as_ground_truth"], "detail":{"capabilities":state["research_capability_registry"]["summary"],"literature":state["literature_retrieval_audit"]["summary"],"evidence_integrity":state["evidence_integrity"]["summary"]}},
        {"key":"cross-cutting-methodology-controls", "pass":state["methodology_controls"]["summary"]["controls"] == 3 and state["methodology_controls"]["summary"]["primary_components_added"] == 0 and state["methodology_controls"]["summary"]["functional_layers_added"] == 0 and state["methodology_controls"]["policy"]["post_outcome_protocol_changes_require_a_new_registered_contract"] and state["methodology_controls"]["policy"]["search_or_tool_access_must_not_leak_hidden_evaluation_answers"] and state["methodology_controls"]["policy"]["reproducibility_requires_reexecution_not_only_trace_presence"], "detail":state["methodology_controls"]["summary"]},
        {"key":"collision-engine", "pass":state["collision_engine"]["summary"]["pairwise_comparisons"] > 0, "detail":state["collision_engine"]["summary"]["pairwise_comparisons"]},
        {"key":"lineage", "pass":state["lineage"]["summary"]["idea_nodes"] >= 24, "detail":state["lineage"]["summary"]["idea_nodes"]},
        {"key":"pre-p0-identifiability", "pass":state["pre_p0_identifiability"]["policy"]["p0_execution_requires_pre_p0_pass"], "detail":state["pre_p0_identifiability"]["summary"]},
        {"key":"pre-gpu-survivor-gate", "pass":state["pre_gpu_candidate_gates"]["summary"]["total"] == 10 and state["pre_gpu_candidate_gates"]["summary"]["small_p0"] == 2 and state["pre_gpu_candidate_gates"]["policy"]["hold_or_inconclusive_is_not_method_failure"], "detail":state["pre_gpu_candidate_gates"]["summary"]},
        {"key":"paper-first-research-contract", "pass":state["paper_first_workflow"]["policy"]["paper_novelty_precedes_method_design"] and state["paper_first_workflow"]["policy"]["method_design_precedes_experiment_blueprint"] and state["paper_first_workflow"]["policy"]["local_validation_is_for_falsification_not_method_discovery"] and state["paper_first_workflow"]["policy"]["full_experiment_requires_frozen_method_and_blueprint"], "detail":state["paper_first_workflow"]["summary"]},
        {"key":"paper-first-design-adjudication", "pass":state["paper_first_design_adjudication"]["summary"]["reviewed"] == 4 and state["paper_first_design_adjudication"]["summary"]["advance_to_method_design"] == 1 and state["paper_first_design_adjudication"]["summary"]["local_validation_authorized"] == 0 and state["paper_first_design_adjudication"]["policy"]["premature_f0_cannot_support_problem_or_method_selection"] is True, "detail":state["paper_first_design_adjudication"]["summary"]},
        {"key":"paper-first-pf1-problem-stop", "pass":state["paper_first_pf1_problem_adjudication"]["decision"] == "STOP_PF1_STANDALONE_PROBLEM_MERGE_EVOLVABILITY_AUDIT" and state["paper_first_pf1_problem_adjudication"]["authority"]["paper_problem_active"] is False and state["paper_first_pf1_problem_adjudication"]["authority"]["method_design_authorized"] is False and state["paper_first_pf1_problem_adjudication"]["authority"]["local_validation_authorized"] is False, "detail":{"decision":state["paper_first_pf1_problem_adjudication"]["decision"],"status":state["paper_first_pf1_problem_adjudication"]["paper_problem_status"]}},
        {"key":"paper-first-pf2-method-stop", "pass":state["paper_first_pf2_method_adjudication"]["decision"] == "STOP_CURRENT_RSIC_METHOD_THESIS_KEEP_PROBLEM_PROTOCOL" and state["paper_first_pf2_method_adjudication"]["same_information_stop"]["triggered"] is True and state["paper_first_pf2_method_adjudication"]["authority"]["method_thesis_active"] is False and state["paper_first_pf2_method_adjudication"]["authority"]["experiment_blueprint_authorized"] is False and state["paper_first_pf2_method_adjudication"]["authority"]["local_validation_authorized"] is False, "detail":{"decision":state["paper_first_pf2_method_adjudication"]["decision"],"problem_status":state["paper_first_pf2_method_adjudication"]["paper_problem_status"]}},
        {"key":"paper-first-pf357-stops", "pass":state["paper_first_pf357_problem_adjudication"]["summary"]["reviewed"] == 3 and state["paper_first_pf357_problem_adjudication"]["summary"]["stopped_standalone"] == 3 and state["paper_first_pf357_problem_adjudication"]["summary"]["paper_design_authorized"] == 0 and state["paper_first_pf357_problem_adjudication"]["summary"]["local_validation_authorized"] == 0, "detail":state["paper_first_pf357_problem_adjudication"]["summary"]},
        {"key":"paper-first-fresh-saturation", "pass":state["paper_first_fresh_saturation"]["summary"]["drafts_reviewed"] == state["paper_first_fresh_saturation"]["summary"]["stopped"] and state["paper_first_fresh_saturation"]["summary"]["drafts_reviewed"] == len(state["paper_first_fresh_saturation"]["drafts"]) and state["paper_first_fresh_saturation"]["summary"]["survivors"] == 0 and state["paper_first_fresh_saturation"]["policy"]["zero_survivors_is_valid_and_preferred_to_forced_shortlist"] is True and state["paper_first_fresh_saturation"]["policy"]["local_validation_authorized"] is False, "detail":state["paper_first_fresh_saturation"]["summary"]},
        {"key":"paper-first-primary-evidence", "pass":state["paper_first_primary_evidence"].get("status") in {"NOT_RUN","READY","INSUFFICIENT_PRIMARY_EVIDENCE","STALE_CORPUS_BLOCKED","NO_CORPUS","STATE_UNREADABLE"} and (state["paper_first_primary_evidence"].get("policy") or {}).get("candidate_generation_authority") is False and (state["paper_first_primary_evidence"].get("policy") or {}).get("method_authority") is False and (state["paper_first_primary_evidence"].get("policy") or {}).get("experiment_authority") is False and (state["paper_first_primary_evidence"].get("status") != "READY" or ((state["paper_first_primary_evidence"].get("policy") or {}).get("primary_publication_age_is_bounded") is True and float((state["paper_first_primary_evidence"].get("policy") or {}).get("maximum_publication_age_days") or 9999) <= 60.0 and (state["paper_first_primary_evidence"].get("policy") or {}).get("fresh_s2_is_augmented_by_preregistered_arxiv_lanes") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("arxiv_augmentation_failure_does_not_invalidate_fresh_corpus") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("typed_evidence_candidates_are_not_ground_truth") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("typed_evidence_is_deterministic_and_bounded") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("source_coverage_scheduler_is_discovery_only") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("source_review_exposure_has_zero_scientific_authority") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("portable_source_review_receipts_have_zero_scientific_authority") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("private_saturation_ledger_runs_exported_as_zero_authority_portable_receipts") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("source_exposure_cannot_skip_generation_or_problem_gate") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("source_exposure_does_not_relax_relevance_or_freshness") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("source_coverage_exploration_prefers_preregistered_lanes") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("source_coverage_saturation_is_compute_control_not_scientific_negative") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("new_lane_grounded_source_reopens_generation") is True and (not bool((state["paper_first_primary_evidence"].get("summary") or {}).get("source_coverage_exhausted")) or len(portable_review_refs) >= int((state["paper_first_primary_evidence"].get("summary") or {}).get("prior_reviewed_sources") or 0)) and int((state["paper_first_primary_evidence"].get("summary") or {}).get("selected_previously_reviewed") or 0) + int((state["paper_first_primary_evidence"].get("summary") or {}).get("selected_unreviewed") or 0) == int((state["paper_first_primary_evidence"].get("summary") or {}).get("selected") or 0) and (state["paper_first_primary_evidence"].get("policy") or {}).get("pre_registered_lane_coverage_floor") is True and int((state["paper_first_primary_evidence"].get("policy") or {}).get("lane_floor") or 0) >= 1 and not list((state["paper_first_primary_evidence"].get("summary") or {}).get("undercovered_lanes") or []))), "detail":{"status":state["paper_first_primary_evidence"].get("status"),"summary":state["paper_first_primary_evidence"].get("summary")}},
        {"key":"paper-first-problem-discovery-contract", "pass":state["paper_first_problem_discovery_contract"]["policy"]["multi_lane_discovery_required"] is True and state["paper_first_problem_discovery_contract"]["policy"]["contradiction_first_required"] is False and state["paper_first_problem_discovery_contract"]["policy"]["contradiction_lane_retained"] is True and tuple(state["paper_first_problem_discovery_contract"]["policy"]["allowed_discovery_lanes"]) == DISCOVERY_LANES and tuple(state["paper_first_problem_discovery_contract"]["policy"]["forbidden_discovery_lanes"]) == FORBIDDEN_DISCOVERY_LANES and state["paper_first_problem_discovery_contract"]["policy"]["lane_specific_machine_evidence_contract_required"] is True and state["paper_first_problem_discovery_contract"]["policy"]["expansion_reduction_separated"] is True and state["paper_first_problem_discovery_contract"]["policy"]["mature_theory_veto_delayed_until_formulated_branch"] is True and state["paper_first_problem_discovery_contract"]["policy"]["reduction_falsifiability_contract_required"] is True and state["paper_first_problem_discovery_contract"]["policy"]["generic_theory_label_cannot_veto"] is True and state["paper_first_problem_discovery_contract"]["policy"]["no_lane_specific_downstream_relaxation"] is True and state["paper_first_problem_discovery_contract"]["policy"]["two_mature_theory_baselines_required"] is True and state["paper_first_problem_discovery_contract"]["policy"]["same_information_nonreducibility_required"] is True and state["paper_first_problem_discovery_contract"]["policy"]["domain_transfer_veto_required"] is True and state["paper_first_problem_discovery_contract"]["summary"]["automatic_method_authority"] == 0 and state["paper_first_problem_discovery_contract"]["summary"]["automatic_experiment_authority"] == 0, "detail":state["paper_first_problem_discovery_contract"]["summary"]},
        {"key":"paper-first-problem-generator", "pass":state["paper_first_problem_generator"].get("status") in {"NOT_RUN","SKIPPED_INSUFFICIENT_PRIMARY_EVIDENCE","SKIPPED_STALE_PRIMARY_EVIDENCE","SKIPPED_SOURCE_COVERAGE_SATURATED","GENERATOR_ERROR_ZERO_AUTHORITY","GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE","STATE_UNREADABLE"} and (state["paper_first_problem_generator"].get("policy") or {}).get("zero_candidates_is_valid") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("search_portfolio_enabled") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("expansion_precedes_reduction") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("mature_theory_veto_delayed_until_formulation") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("diversity_archives_required") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("branch_lineage_required") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("reduction_falsifiability_contract_required") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("generic_theory_label_cannot_veto") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("multi_lane_discovery_enabled") is True and tuple((state["paper_first_problem_generator"].get("policy") or {}).get("allowed_discovery_lanes") or []) == DISCOVERY_LANES and tuple((state["paper_first_problem_generator"].get("policy") or {}).get("forbidden_discovery_lanes") or []) == FORBIDDEN_DISCOVERY_LANES and (state["paper_first_problem_generator"].get("policy") or {}).get("semantic_reviewer_is_block_only") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("independent_reviewer_must_verify_lane_contract") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("source_coverage_saturation_skips_model_call") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("source_coverage_saturation_is_compute_control_not_scientific_negative") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("new_lane_grounded_primary_source_reopens_generation") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("portable_review_receipts_are_scheduler_metadata_only") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("portable_review_receipts_have_zero_scientific_authority") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("primary_source_coverage_receipts_are_inherited_transactionally") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("candidate_inbox_has_zero_scientific_authority") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("automatic_method_authority") is False and (state["paper_first_problem_generator"].get("policy") or {}).get("automatic_experiment_authority") is False and (state["paper_first_problem_generator"].get("status") not in {"GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE"} or (state["paper_first_problem_generator"].get("policy") or {}).get("independent_reviewer_must_ground_both_source_claims_to_exact_primary_evidence_excerpts") is True), "detail":{"status":state["paper_first_problem_generator"].get("status"),"summary":state["paper_first_problem_generator"].get("summary")}},
        {"key":"paper-first-problem-gate-queue", "pass":state["paper_first_problem_gate_queue"]["summary"]["audited"] == state["paper_first_problem_gate_queue"]["summary"]["submitted"] and state["paper_first_problem_gate_queue"]["summary"]["passed_problem_gate"] + state["paper_first_problem_gate_queue"]["summary"]["blocked_problem_gate"] == state["paper_first_problem_gate_queue"]["summary"]["audited"] and state["paper_first_problem_gate_queue"]["summary"]["inbox_errors"] == 0 and state["paper_first_problem_gate_queue"]["summary"]["method_authorized"] == 0 and state["paper_first_problem_gate_queue"]["summary"]["experiment_authorized"] == 0 and state["paper_first_problem_gate_queue"]["summary"]["p0_authorized"] == 0 and state["paper_first_problem_gate_queue"]["policy"]["verified_primary_evidence_registry_required_for_submitted_candidates"] is True and state["paper_first_problem_gate_queue"]["policy"]["multi_lane_candidate_schema_required"] is True and state["paper_first_problem_gate_queue"]["policy"]["lane_contract_independent_review_required"] is True and state["paper_first_problem_gate_queue"]["policy"]["independent_semantic_reduction_review_required"] is True, "detail":state["paper_first_problem_gate_queue"]["summary"]},
        {"key":"paper-first-post-c2-terminal", "pass":state["paper_first_post_c2"]["decision"] == "STOP_CURRENT_CONTROLLED_MEDIATOR_PAPER_MECHANISM" and state["paper_first_post_c2"]["authority"]["clean_mechanism_stop"] is True and state["paper_first_post_c2"]["authority"]["C3_locked"] is True and state["paper_first_post_c2"]["authority"]["full_experiment_authorized"] is False and state["paper_first_post_c2"]["authority"]["new_method_auto_authorized"] is False and state["paper_first_post_c2"]["authority"]["new_paper_problem_auto_authorized"] is False, "detail":{"decision":state["paper_first_post_c2"]["decision"],"c2":state["paper_first_post_c2"]["c2_result"],"gate_provenance":state["paper_first_post_c2"]["gate_provenance"]}},
        {"key":"backend-architecture-manifest", "pass":state["system_architecture"]["summary"]["temporal_stages"] == 11 and state["system_architecture"]["summary"]["functional_layers"] == 6 and state["system_architecture"]["summary"]["assigned_components"] == len(state["components"]) and state["system_architecture"]["summary"]["unassigned_components"] == 0 and state["system_architecture"]["summary"]["duplicate_component_keys"] == 0 and state["system_architecture"]["summary"]["cross_cutting_controls"] == 3 and state["system_architecture"]["summary"]["orphan_cross_cutting_controls"] == 0, "detail":state["system_architecture"]["summary"]},
        {"key":"principle-layer", "pass":state["principle_layer"]["policy"]["experiment_is_evidence_about_a_principle_not_a_vote_on_an_idea"] and state["principle_layer"]["policy"]["true_negative_does_not_automatically_falsify_principle"] and state["principle_layer"]["summary"]["certificates_passed"] == expected_pre_experiment_cards, "detail":state["principle_layer"]["summary"]},
        {"key":"pre-experiment-compiler", "pass":state["pre_experiment_compiler"]["policy"]["paper_design_contract_required_before_principle_and_implementation"] and state["pre_experiment_compiler"]["policy"]["paper_design_contract_is_not_a_formal_gate"] and state["pre_experiment_compiler"]["policy"]["principle_certificate_required_before_updater_competence"] and state["pre_experiment_compiler"]["policy"]["principle_certificate_is_not_a_formal_gate"] and state["pre_experiment_compiler"]["policy"]["protocol_validity_required_before_updater_competence"] and state["pre_experiment_compiler"]["policy"]["protocol_validity_is_not_a_formal_gate"] and state["pre_experiment_compiler"]["summary"]["protocol_validity_pass"] == expected_pre_experiment_cards and state["pre_experiment_compiler"]["policy"]["research_execution_plan_required_before_launch"] and state["pre_experiment_compiler"]["policy"]["research_execution_plan_is_derived_not_a_formal_gate"] and state["pre_experiment_compiler"]["policy"]["research_execution_plan_cannot_authorize_execution"] and state["pre_experiment_compiler"]["summary"]["research_execution_plans"] == expected_pre_experiment_cards and state["pre_experiment_compiler"]["policy"]["updater_competence_required_before_gate_1"] and state["pre_experiment_compiler"]["policy"]["updater_competence_is_not_a_ninth_gate"] and state["pre_experiment_compiler"]["policy"]["all_eight_gates_required"] and state["pre_experiment_compiler"]["policy"]["automatic_override_forbidden"] and state["pre_experiment_compiler"]["policy"]["terminal_outcome_requires_endpoint_headroom_audit"] and state["pre_experiment_compiler"]["policy"]["execution_cap_censoring_must_be_typed_separately"] and state["pre_experiment_compiler"]["policy"]["cap_censored_branch_cannot_count_as_natural_terminal_failure"] and state["pre_experiment_compiler"]["summary"]["compiled_cards"] == expected_pre_experiment_cards, "detail":state["pre_experiment_compiler"]["summary"]},
        {"key":"paper-first-p0-human-authority", "pass":state["paper_first_p0_authority"]["summary"].get("promoted") == 0 or state["paper_first_p0_authority"]["summary"].get("authority_status") == "EXTERNAL_HUMAN_P0_PROMOTION_AUTHORITY_VALID", "detail":state["paper_first_p0_authority"]},
        {"key":"paper-first-p0-f0", "pass":state["paper_first_p0_f0"]["summary"].get("ideas") == 4 and state["paper_first_p0_f0"]["summary"].get("quarantined") == 4 and state["paper_first_p0_f0"]["summary"].get("scientifically_authorized") == 0 and state["paper_first_p0_f0"]["summary"].get("method_fail_authorized") == 0 and state["paper_first_p0_f0"]["policy"].get("unauthorized_execution_is_preserved_as_diagnostic_not_scientific_authority") is True, "detail":state["paper_first_p0_f0"]["summary"]},
        {"key":"paper-first-premature-method-diagnostics", "pass":state["paper_first_premature_method_diagnostics"]["summary"].get("directions") == 2 and state["paper_first_premature_method_diagnostics"]["summary"].get("completed_diagnostics") == 2 and state["paper_first_premature_method_diagnostics"]["summary"].get("same_information_reducibility_findings") == 2 and state["paper_first_premature_method_diagnostics"]["summary"].get("scientifically_authorized") == 0 and state["paper_first_premature_method_diagnostics"]["summary"].get("p0_lifecycle_mutations") == 0 and state["paper_first_premature_method_diagnostics"]["authority"].get("cannot_retroactively_authorize") is True, "detail":state["paper_first_premature_method_diagnostics"]["summary"]},
        {"key":"research-learning-loop", "pass":state["scientific_meta_trace"]["policy"]["raw_execution_trace_is_not_scientific_state"] and state["scientific_meta_trace"]["policy"]["active_scientific_state_is_separate_from_institutional_memory"] and state["scientific_meta_trace"]["policy"]["active_scientific_state_never_time_decays"] and state["failure_asset_library"]["policy"]["assets_are_retrieved_before_new_experiment_design"] and state["failure_asset_library"]["policy"]["institutional_memory_requires_scope_and_effectiveness_tracking"] and state["experiment_value_scheduler"]["policy"]["scheduler_cannot_authorize_execution"] and state["research_system_replay"]["summary"]["failed"] == 0 and state["external_system_learning"]["policy"]["every_candidate_design_requires_local_gap_test"], "detail":{"meta":state["scientific_meta_trace"]["summary"],"failure_assets":state["failure_asset_library"]["summary"],"scheduler":state["experiment_value_scheduler"]["summary"],"replay":state["research_system_replay"]["summary"],"external":state["external_system_learning"]["summary"]}},
        {"key":"pilot-schema", "pass":state["pilot_registry"]["summary"]["invalid_result_files"] == 0 and state["pilot_registry"]["summary"]["invalid_approval_files"] == 0 and state["pilot_registry"]["policy"]["automatic_p0_to_p1_forbidden"] and state["pilot_registry"]["policy"]["p0_execution_requires_pre_experiment_8_of_8"], "detail":state["pilot_registry"]["summary"]},
        {"key":"experiment-diagnosis", "pass":state["experiment_iteration"]["summary"]["nodes"] == 4 and state["experiment_iteration"]["policy"]["nonidentifiable_pilot_cannot_update_scientific_belief"], "detail":state["experiment_iteration"]["summary"]},
        {"key":"mem-xfer-workflow", "pass":not _mem_xfer_semantic_errors(state["mem_xfer_workflow"]), "detail":{"semantic_errors":_mem_xfer_semantic_errors(state["mem_xfer_workflow"]),"support_qualification":state["mem_xfer_workflow"]["support_qualification"]["status"],"full_support":state["mem_xfer_workflow"]["full_support"]["status"],"cpu_gate":state["mem_xfer_workflow"]["support_enriched_analysis"]["status"],"second_model":state["mem_xfer_workflow"]["second_model"]["status"]}},
        {"key":"human-terminal-ledger", "pass":terminal_summary.get("human_parents") == 26 and terminal_summary.get("p0_resolved_lineages") == 26 and terminal_summary.get("drop") == 0 and terminal_summary.get("revived_to_p0") == 7, "detail":terminal_summary},
        {"key":"p0-admission", "pass":state["p0_admission"]["summary"].get("active_p0") == expected_active_p0 and state["p0_admission"]["summary"].get("admitted") == expected_active_p0 and state["p0_admission"]["summary"].get("transitioned_from_p0_ready") == 16 and state["p0_admission"]["summary"].get("revived_from_drop") == 7 and state["p0_admission"]["summary"].get("settings_complete") == expected_active_p0, "detail":state["p0_admission"]["summary"]},
        {"key":"p0-economy-gate", "pass":state["p0_economy_gate"]["summary"].get("ideas") == expected_active_p0 and state["p0_economy_gate"]["summary"].get("economy_ready") == state["p0_admission"]["summary"].get("economy_ready") and state["p0_economy_gate"]["policy"].get("all_five_required_before_execution_compilation") is True, "detail":state["p0_economy_gate"]["summary"]},
        {"key":"ai-consultation-clinic", "pass":state["ai_consultation_clinic"]["summary"].get("checkpoints") == 5 and state["ai_consultation_clinic"]["policy"].get("ai_vote_can_authorize_gpu") is False and state["ai_consultation_clinic"]["policy"].get("high_risk_findings_must_be_compiled_into_machine_checks") is True, "detail":state["ai_consultation_clinic"]["summary"]},
        {"key":"ai-consultation-automation", "pass":state["ai_consultation_automation"]["policy"].get("content_addressed_triggers") is True and state["ai_consultation_automation"]["policy"].get("ai_output_never_authorizes_execution") is True and state["ai_consultation_automation"]["clinic_policy"].get("ai_vote_can_authorize_gpu") is False, "detail":state["ai_consultation_automation"]["summary"]},
        {"key":"p0-decision-ledger", "pass":state["p0_decision_ledger"]["summary"].get("active_p0") == expected_active_p0 and state["p0_decision_ledger"]["summary"].get("launchable") == 0 and state["p0_decision_ledger"]["policy"].get("economy_stop_overrides_planned_registry_display") is True, "detail":state["p0_decision_ledger"]["summary"]},
        {"key":"persistent-updater-terminal", "pass":state["persistent_updater_program_final"].get("verdict") == "STOP_CURRENT_PERSISTENT_UPDATER_PROGRAM" and state["persistent_updater_program_final"].get("batch_experiment_authorized") is False and (state["persistent_updater_program_final"].get("states") or {}).get("A2") == "KEEP_PROBLEM_HOLD_NO_QUALIFIED_UPDATER", "detail":{"verdict":state["persistent_updater_program_final"].get("verdict"),"batch":state["persistent_updater_program_final"].get("batch_experiment_authorized"),"A2":(state["persistent_updater_program_final"].get("states") or {}).get("A2")}},
        {"key":"research-governance-v2", "pass":state["research_governance_v2"]["policy"].get("paper_novelty_precedes_method_design") is True and state["research_governance_v2"]["policy"].get("method_design_precedes_experiment_plan") is True and state["research_governance_v2"]["policy"].get("local_validation_precedes_full_experiment") is True and state["research_governance_v2"]["policy"].get("support_and_method_are_distinct") is True and state["research_governance_v2"]["policy"].get("p0_method_requires_frozen_support_pass") is True and state["research_governance_v2"]["policy"].get("raw_trace_is_mandatory_for_gpu_runs") is True and len(state["research_governance_v2"].get("stages") or []) == 7, "detail":state["research_governance_v2"]},
        {"key":"p0-offline-qualification", "pass":state["p0_offline_qualification"]["summary"].get("ideas") == 16 and state["p0_offline_qualification"]["policy"].get("method_result_from_offline_qualification_forbidden") is True, "detail":state["p0_offline_qualification"]["summary"]},
        {"key":"p0-realizability", "pass":state["p0_realizability"]["summary"].get("audited") == 14 and state["p0_realizability"]["policy"].get("cannot_emit_method_result") is True, "detail":state["p0_realizability"]["summary"]},
        {"key":"p0-20idea-batch", "pass":state["p0_revived_batch_f0"]["summary"].get("parent_p0") == 20 and state["p0_revived_batch_f0"]["summary"].get("reused_existing_p0") == 13 and state["p0_revived_batch_f0"]["summary"].get("fresh_cpu_f0") == 7 and sum(int(state["p0_revived_batch_f0"]["summary"].get(key) or 0) for key in ("fresh_matched_simplification_stop","fresh_upstream_hold","fresh_signal_continue")) == 7 and state["p0_revived_batch_f0"]["summary"].get("gpu_queue_candidates_before_economy") == state["p0_revived_batch_f0"]["summary"].get("fresh_signal_continue"), "detail":state["p0_revived_batch_f0"]["summary"]},
        {"key":"final-advisor-gate", "pass":state["summary"]["final_ready"] and state["summary"]["final_pass"] == state["summary"]["discussion_target"] and state["summary"]["final_revise"] == 0 and state["summary"]["final_block"] == 0, "detail":{"pass":state["summary"]["final_pass"],"target":state["summary"]["discussion_target"],"revise":state["summary"]["final_revise"],"block":state["summary"]["final_block"]}},
    ]
    return {"status":"healthy" if all(item["pass"] for item in checks) else "degraded", "checks":checks}


def validate_state(state: dict[str, Any]) -> list[str]:
    errors=[]
    expected_pre_experiment_cards = len(PRE_EXPERIMENT_CONFIGS)
    if state.get("target_venue") != "ICLR": errors.append("target venue mismatch")
    if state["summary"]["papers"] < 100: errors.append("literature corpus too small")
    if state["summary"]["ideas"] < 24: errors.append("idea bank too small")
    if state["evidence_graph"]["summary"]["nodes"] <= state["summary"]["papers"]: errors.append("evidence graph lacks non-paper nodes")
    if not state["research_capability_registry"]["policy"]["capabilities_are_declared_not_prompt_inferred"] or state["research_capability_registry"]["summary"].get("capabilities",0) < 9: errors.append("research capability registry is incomplete")
    if not state["research_capability_registry"]["policy"]["model_or_tool_routing_cannot_escalate_scientific_authority"]: errors.append("capability routing must not escalate scientific authority")
    if not state["literature_retrieval_audit"]["policy"]["deep_and_wide_retrieval_are_distinct_capabilities"]: errors.append("deep and wide literature retrieval must remain distinct")
    if not state["literature_retrieval_audit"]["policy"]["citation_verifier_must_be_named_versioned_and_calibrated"]: errors.append("citation verifier must be versioned and calibrated")
    if state["literature_retrieval_audit"]["summary"].get("benchmark_status") != "spec-ready-not-yet-scored": errors.append("literature retrieval benchmark status mismatch")
    if not state["evidence_integrity"]["policy"]["every_publishable_claim_requires_evidence_chain"]: errors.append("publishable claims must require an evidence chain")
    if not state["evidence_integrity"]["policy"]["uncalibrated_verifier_cannot_be_treated_as_ground_truth"]: errors.append("uncalibrated verifiers must not be treated as ground truth")
    methodology = state.get("methodology_controls") or {}; methodology_summary = methodology.get("summary") or {}; methodology_policy = methodology.get("policy") or {}
    if methodology_summary.get("controls") != 3 or methodology_summary.get("primary_components_added") != 0 or methodology_summary.get("functional_layers_added") != 0: errors.append("cross-cutting methodology controls must add three controls without new primary components or layers")
    if methodology_policy.get("post_outcome_protocol_changes_require_a_new_registered_contract") is not True: errors.append("post-outcome protocol changes must require a new registered contract")
    if methodology_policy.get("search_or_tool_access_must_not_leak_hidden_evaluation_answers") is not True: errors.append("search/tool access must not contaminate hidden evaluation")
    if methodology_policy.get("reproducibility_requires_reexecution_not_only_trace_presence") is not True: errors.append("reproducibility must require re-execution rather than trace presence alone")
    if state["collision_engine"]["summary"]["pairwise_comparisons"] <= 0: errors.append("collision engine did not run")
    if state["pilot_registry"]["summary"]["phases"] != state["summary"]["passed_ideas"] * 3: errors.append("pilot phase count mismatch")
    if not state["pre_p0_identifiability"]["policy"]["p0_execution_requires_pre_p0_pass"]: errors.append("retrospective Pre-P0 audit must remain authoritative evidence")
    if state["pre_gpu_candidate_gates"]["summary"]["total"] != 10: errors.append("pre-GPU survivor gate must cover all ten shortlisted candidates")
    if state["pre_gpu_candidate_gates"]["summary"]["small_p0"] != 2: errors.append("pre-GPU survivor gate must expose exactly the two currently cleared small P0 candidates")
    if not state["pre_gpu_candidate_gates"]["policy"]["hold_or_inconclusive_is_not_method_failure"]: errors.append("HOLD/INCONCLUSIVE must remain scientifically neutral")
    if not state["paper_first_workflow"]["policy"]["paper_novelty_precedes_method_design"]: errors.append("paper novelty must be frozen before method design")
    if not state["paper_first_workflow"]["policy"]["method_design_precedes_experiment_blueprint"]: errors.append("method design must precede experiment blueprint")
    if not state["paper_first_workflow"]["policy"]["local_validation_is_for_falsification_not_method_discovery"]: errors.append("local validation must not discover or redefine the core method")
    if not state["paper_first_workflow"]["policy"]["full_experiment_requires_frozen_method_and_blueprint"]: errors.append("full experiments require frozen method and experiment blueprint")
    design = state.get("paper_first_design_adjudication") or {}; design_summary = design.get("summary") or {}; design_policy = design.get("policy") or {}
    if (design_summary.get("reviewed"), design_summary.get("advance_to_method_design"), design_summary.get("revise_paper_problem"), design_summary.get("merge_as_cross_cutting_invariant"), design_summary.get("stop_standalone_merge_risk_axis")) != (4,1,1,1,1): errors.append("paper-first design adjudication must conservatively route PF-1/PF-2/PF-4/PF-6 as 1 method / 1 revise / 1 merge / 1 stop")
    if design_policy.get("local_validation_authorized") is not False or design_policy.get("p0_authorized") is not False or design_policy.get("premature_f0_cannot_support_problem_or_method_selection") is not True: errors.append("paper-first design adjudication must remain outside P0/local-validation authority and ignore premature F0 as scientific evidence")
    pf1_problem = state.get("paper_first_pf1_problem_adjudication") or {}; pf1_auth = pf1_problem.get("authority") or {}
    if pf1_problem.get("decision") != "STOP_PF1_STANDALONE_PROBLEM_MERGE_EVOLVABILITY_AUDIT": errors.append("PF-1 standalone problem must terminate after final plasticity/evolvability collision review")
    if any(pf1_auth.get(key) is not False for key in ("paper_problem_active","method_design_authorized","experiment_blueprint_authorized","local_validation_authorized","p0_authorized","gpu_authorized","full_experiment_authorized","premature_pf_f0_used","automatic_replacement_problem_authorized")): errors.append("PF-1 problem STOP cannot authorize a method, replacement problem, or experiment")
    pf2_method = state.get("paper_first_pf2_method_adjudication") or {}; pf2_auth = pf2_method.get("authority") or {}
    if pf2_method.get("decision") != "STOP_CURRENT_RSIC_METHOD_THESIS_KEEP_PROBLEM_PROTOCOL" or not (pf2_method.get("same_information_stop") or {}).get("triggered"): errors.append("PF-2 RSIC method thesis must stop on same-information generic partial-identification equivalence")
    if any(pf2_auth.get(key) is not False for key in ("method_thesis_active","experiment_blueprint_authorized","local_validation_authorized","p0_authorized","gpu_authorized","full_experiment_authorized","premature_pf_f0_used","new_method_auto_authorized")): errors.append("PF-2 method STOP cannot authorize a replacement method, blueprint, or experiment")
    pf357 = state.get("paper_first_pf357_problem_adjudication") or {}; pf357_summary = pf357.get("summary") or {}
    fresh_sat = state.get("paper_first_fresh_saturation") or {}; fresh_summary = fresh_sat.get("summary") or {}; fresh_policy = fresh_sat.get("policy") or {}
    if fresh_summary.get("survivors") != 0 or fresh_summary.get("drafts_reviewed") != fresh_summary.get("stopped") or fresh_summary.get("drafts_reviewed") != len(fresh_sat.get("drafts") or []): errors.append("fresh discovery saturation accounting mismatch")
    if fresh_policy.get("zero_survivors_is_valid_and_preferred_to_forced_shortlist") is not True or fresh_policy.get("local_validation_authorized") is not False or fresh_policy.get("p0_authorized") is not False: errors.append("fresh discovery must allow zero survivors and remain outside execution authority")
    primary_evidence = state.get("paper_first_primary_evidence") or {}; primary_policy = primary_evidence.get("policy") or {}; primary_summary = primary_evidence.get("summary") or {}
    if primary_policy.get("candidate_generation_authority") is not False or primary_policy.get("method_authority") is not False or primary_policy.get("experiment_authority") is not False: errors.append("primary evidence refresh can supply provenance but cannot authorize candidate/method/experiment transitions")
    if primary_evidence.get("status") == "READY" and (primary_summary.get("verified") or 0) < 4: errors.append("READY primary evidence pool must contain at least four verified records")
    if primary_evidence.get("status") == "READY" and (primary_policy.get("primary_publication_age_is_bounded") is not True or float(primary_policy.get("maximum_publication_age_days") or 9999) > 60.0): errors.append("READY primary evidence pool must hard-bound publication age to <=60 days")
    if primary_evidence.get("status") == "READY" and (primary_policy.get("fulltext_enrichment_is_optional") is not True or primary_policy.get("fulltext_snippets_remain_private_data_artifacts") is not True or primary_policy.get("empirical_fact_candidates_are_not_ground_truth") is not True or primary_policy.get("typed_evidence_candidates_are_not_ground_truth") is not True or primary_policy.get("typed_evidence_is_deterministic_and_bounded") is not True): errors.append("READY primary evidence must keep fulltext/typed enrichment optional-private, deterministic-bounded, and non-authoritative")
    if primary_evidence.get("status") == "READY" and (primary_policy.get("empirical_fact_precision_gate") is not True or primary_policy.get("empirical_fact_extraction_version") != "precision-v2" or primary_policy.get("derived_empirical_facts_reused_only_when_extractor_version_matches") is not True): errors.append("READY primary evidence must use the versioned empirical-fact precision gate and forbid cross-version derived-fact reuse")
    if primary_evidence.get("status") == "READY" and (primary_policy.get("typed_evidence_extraction_version") != "typed-v1" or primary_policy.get("derived_typed_evidence_reused_only_when_extractor_version_matches") is not True): errors.append("READY primary evidence must version typed evidence and forbid cross-version typed-evidence reuse")
    if primary_evidence.get("status") == "READY" and (primary_policy.get("source_coverage_scheduler_is_discovery_only") is not True or primary_policy.get("source_review_exposure_has_zero_scientific_authority") is not True or primary_policy.get("portable_source_review_receipts_have_zero_scientific_authority") is not True or primary_policy.get("private_saturation_ledger_runs_exported_as_zero_authority_portable_receipts") is not True or primary_policy.get("source_exposure_cannot_skip_generation_or_problem_gate") is not True or primary_policy.get("source_exposure_does_not_relax_relevance_or_freshness") is not True or primary_policy.get("source_coverage_exploration_prefers_preregistered_lanes") is not True or primary_policy.get("source_coverage_saturation_is_compute_control_not_scientific_negative") is not True or primary_policy.get("new_lane_grounded_source_reopens_generation") is not True): errors.append("READY primary evidence must keep source-exposure scheduling retrieval-only, portable, zero-authority, lane-grounded, reopenable, and inside the same freshness/relevance gates")
    if primary_evidence.get("status") == "READY" and int(primary_summary.get("selected_previously_reviewed") or 0) + int(primary_summary.get("selected_unreviewed") or 0) != int(primary_summary.get("selected") or 0): errors.append("source-coverage selected reviewed/unreviewed accounting must equal selected evidence count")
    if primary_evidence.get("status") == "READY" and int(primary_summary.get("saturation_ledger_runs") or 0) > 0 and int(primary_summary.get("selected") or 0) > int(primary_summary.get("coverage_anchor_count") or 0) and primary_summary.get("source_coverage_scheduler_active") is not True: errors.append("available saturation history must activate the zero-authority source-coverage scheduler for the exploration tranche")
    fact_tiers = primary_summary.get("empirical_fact_tier_counts") or {}
    if primary_evidence.get("status") == "READY" and sum(int(value or 0) for value in fact_tiers.values()) != int(primary_summary.get("empirical_fact_candidates") or 0): errors.append("empirical fact tier accounting must equal the published fact-candidate count")
    typed_counts = primary_summary.get("typed_evidence_candidates") or {}
    if primary_evidence.get("status") == "READY" and set(typed_counts) != {"operational_assumptions","measured_failures","boundary_observations"}: errors.append("typed evidence accounting must expose assumption/failure/boundary buckets")
    if primary_evidence.get("status") == "READY" and (primary_policy.get("pre_registered_lane_coverage_floor") is not True or primary_policy.get("lane_coverage_is_discovery_breadth_not_scientific_authority") is not True or int(primary_policy.get("lane_floor") or 0) < 1): errors.append("READY primary evidence must enforce the preregistered lane coverage floor without granting scientific authority")
    if primary_evidence.get("status") == "READY" and (primary_policy.get("fresh_s2_is_augmented_by_preregistered_arxiv_lanes") is not True or primary_policy.get("arxiv_augmentation_failure_does_not_invalidate_fresh_corpus") is not True): errors.append("READY primary evidence must augment fresh corpus discovery with preregistered arXiv lanes while treating augmentation failure as metadata-only")
    if primary_evidence.get("status") == "READY" and list(primary_summary.get("undercovered_lanes") or []): errors.append("READY primary evidence selection must satisfy every eligible preregistered lane floor")
    discovery_contract = state.get("paper_first_problem_discovery_contract") or {}; discovery_policy = discovery_contract.get("policy") or {}; discovery_summary = discovery_contract.get("summary") or {}
    if discovery_policy.get("multi_lane_discovery_required") is not True or discovery_policy.get("contradiction_first_required") is not False or discovery_policy.get("contradiction_lane_retained") is not True or tuple(discovery_policy.get("allowed_discovery_lanes") or []) != DISCOVERY_LANES or tuple(discovery_policy.get("forbidden_discovery_lanes") or []) != FORBIDDEN_DISCOVERY_LANES or discovery_policy.get("lane_specific_machine_evidence_contract_required") is not True or discovery_policy.get("expansion_reduction_separated") is not True or discovery_policy.get("mature_theory_veto_delayed_until_formulated_branch") is not True or discovery_policy.get("reduction_falsifiability_contract_required") is not True or discovery_policy.get("generic_theory_label_cannot_veto") is not True or discovery_policy.get("no_lane_specific_downstream_relaxation") is not True or discovery_policy.get("two_mature_theory_baselines_required") is not True or discovery_policy.get("same_information_nonreducibility_required") is not True or discovery_policy.get("domain_transfer_veto_required") is not True: errors.append("paper-first problem discovery contract must require ten-lane expansion, delayed falsifiable reduction, and shared downstream novelty gates")
    if discovery_summary.get("saturation_patterns") != fresh_summary.get("reduction_patterns") or discovery_summary.get("automatic_method_authority") != 0 or discovery_summary.get("automatic_experiment_authority") != 0: errors.append("paper-first problem discovery contract must consume the current saturation map and grant no automatic downstream authority")
    generator = state.get("paper_first_problem_generator") or {}; generator_policy = generator.get("policy") or {}; generator_summary = generator.get("summary") or {}; generator_schema = str(generator.get("schema_version") or "0")
    if generator_schema >= "3.1" and (generator_policy.get("zero_candidates_is_valid") is not True or generator_policy.get("search_portfolio_enabled") is not True or generator_policy.get("expansion_precedes_reduction") is not True or generator_policy.get("mature_theory_veto_delayed_until_formulation") is not True or generator_policy.get("diversity_archives_required") is not True or generator_policy.get("branch_lineage_required") is not True or generator_policy.get("reduction_falsifiability_contract_required") is not True or generator_policy.get("generic_theory_label_cannot_veto") is not True or generator_policy.get("multi_lane_discovery_enabled") is not True or tuple(generator_policy.get("allowed_discovery_lanes") or []) != DISCOVERY_LANES or tuple(generator_policy.get("forbidden_discovery_lanes") or []) != FORBIDDEN_DISCOVERY_LANES or generator_policy.get("semantic_reviewer_is_block_only") is not True or generator_policy.get("independent_reviewer_must_verify_lane_contract") is not True or generator_policy.get("source_coverage_saturation_skips_model_call") is not True or generator_policy.get("source_coverage_saturation_is_compute_control_not_scientific_negative") is not True or generator_policy.get("new_lane_grounded_primary_source_reopens_generation") is not True or generator_policy.get("portable_review_receipts_are_scheduler_metadata_only") is not True or generator_policy.get("portable_review_receipts_have_zero_scientific_authority") is not True or generator_policy.get("primary_source_coverage_receipts_are_inherited_transactionally") is not True or generator_policy.get("candidate_inbox_has_zero_scientific_authority") is not True): errors.append("problem generator must enforce the ten-lane Search Portfolio plus portable zero-authority source-coverage control")
    if generator.get("status") == "SKIPPED_SOURCE_COVERAGE_SATURATED":
        coverage = generator.get("source_coverage") or {}
        unreviewed = coverage.get("unreviewed_lane_linked_sources")
        if coverage.get("coverage_exhausted") is not True or unreviewed is None or int(unreviewed) != 0:
            errors.append("source-coverage saturation skip requires an exhausted lane-grounded evidence universe")
    if generator_policy.get("generation_notes_are_advisory_not_scientific_authority") is not True or generator_policy.get("zero_candidate_rationale_required") is not True or generator_policy.get("discovery_saturation_memory_has_zero_scientific_authority") is not True: errors.append("problem generator must preserve generation rationale and saturation memory without scientific authority")
    if generator_schema >= "2.3" and (generator_policy.get("reviewer_blocked_problem_memory_has_zero_scientific_authority") is not True or generator_policy.get("repeated_reduction_basin_requires_search_escape") is not True or generator_policy.get("portable_blocked_problem_memory_is_search_control_only") is not True): errors.append("problem generator must treat reviewer-blocked problem memory as zero-authority search control")
    if generator_schema >= "2.3" and (generator_policy.get("reviewer_declared_excerpt_source_is_audit_metadata_not_grounding_authority") is not True or generator_policy.get("exact_excerpt_location_is_machine_inferred") is not True): errors.append("problem generator must infer exact excerpt location rather than trust reviewer source labels")
    if generator_schema >= "2.4" and generator_policy.get("search_portfolio_enabled") is True and (generator_policy.get("portfolio_expansion_must_audit_all_discovery_lanes") is not True or generator_policy.get("lane_search_diagnostics_have_zero_scientific_authority") is not True or generator_policy.get("historically_underexplored_lanes_are_searched_first") is not True or generator_policy.get("lane_search_never_requires_candidate") is not True): errors.append("Search Portfolio must leave a zero-authority expansion audit for every discovery lane without forcing candidates")
    if generator_schema >= "2.4" and generator_policy.get("search_portfolio_enabled") is not True and (generator_policy.get("one_generator_call_must_audit_all_discovery_lanes") is not True or generator_policy.get("lane_search_diagnostics_have_zero_scientific_authority") is not True): errors.append("legacy problem generator must audit every discovery lane in one zero-authority pass")
    lane_search = generator.get("search_diagnostics") or {}
    if generator_schema >= "2.4" and lane_search.get("scientific_authority") is not False: errors.append("lane-search diagnostics cannot carry scientific authority")
    expected_lane_set=set(DISCOVERY_LANES) if generator_schema >= "3.1" else set(generator_policy.get("allowed_discovery_lanes") or DISCOVERY_LANES)
    if generator_schema >= "2.4" and set(lane_search.get("lane_search_priority") or []) != expected_lane_set: errors.append("lane-search priority must cover all discovery lanes")
    if generator_schema >= "2.4" and generator.get("status") in {"GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE"}:
        lane_rows=[row for row in lane_search.get("lane_search") or [] if isinstance(row,dict)]
        lane_names=[str(row.get("lane") or "") for row in lane_rows]
        lane_statuses=[str(row.get("status") or "") for row in lane_rows]
        allowed_lane_statuses={"EXPANDED","EMPTY"} if generator_policy.get("search_portfolio_enabled") is True else {"NO_PAIR","REDUCIBLE","CANDIDATE"}
        if lane_search.get("lane_search_complete") is not True or len(lane_rows)!=len(expected_lane_set) or set(lane_names)!=expected_lane_set or any(status not in allowed_lane_statuses for status in lane_statuses): errors.append("generated problem state must preserve one complete machine-audited status for every discovery lane")
    saturation_memory = generator.get("saturation_memory") or {}
    if saturation_memory.get("scientific_authority") is not False: errors.append("problem-discovery saturation memory cannot carry scientific authority")
    blocked_memory = saturation_memory.get("blocked_problem_memory") or {}
    if generator_schema >= "2.3" and blocked_memory.get("scientific_authority") is not False: errors.append("reviewer-blocked problem memory cannot carry scientific authority")
    if generator_schema >= "2.3" and any(row.get("scientific_authority") is not False for row in blocked_memory.get("portable_blocked_problem_memory") or [] if isinstance(row,dict)): errors.append("portable reviewer-blocked problem memory cannot carry scientific authority")
    top_basin = blocked_memory.get("top_reduction_basin") or {}
    if generator_schema >= "2.3" and blocked_memory.get("repeated_reduction_basin") is True and (blocked_memory.get("search_escape_required") is not True or int(top_basin.get("count") or 0) < 3): errors.append("repeated problem-reduction basin must require search escape with repeated evidence")
    portable_receipts = [row for row in saturation_memory.get("portable_review_receipts") or [] if isinstance(row,dict)]
    if any(row.get("scientific_authority") is not False for row in portable_receipts): errors.append("portable problem-review receipts cannot carry scientific authority")
    portable_review_refs = {str(ref) for row in portable_receipts for ref in row.get("source_refs") or [] if str(ref).startswith("arXiv:")}
    if primary_summary.get("source_coverage_exhausted") is True and len(portable_review_refs) < int(primary_summary.get("prior_reviewed_sources") or 0): errors.append("exhausted source coverage must export portable review receipts for every previously reviewed source")
    if generator.get("status") == "GENERATED_ZERO_CANDIDATES" and not str(generator.get("generation_notes") or "").strip(): errors.append("zero-candidate generator state must preserve an auditable rationale")
    if generator.get("status") in {"GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE"} and (generator_policy.get("independent_reviewer_must_ground_both_source_claims_to_exact_primary_evidence_excerpts") is not True or generator_policy.get("independent_reviewer_must_verify_lane_contract") is not True): errors.append("generated problem candidates require independent exact-primary-evidence grounding plus lane-contract verification")
    if generator_policy.get("automatic_method_authority") is not False or generator_policy.get("automatic_experiment_authority") is not False or generator_policy.get("automatic_p0_authority") is not False: errors.append("problem generator cannot authorize method, experiment, or P0")
    portfolio = generator.get("search_portfolio") or {}; portfolio_summary = portfolio.get("summary") or {}; portfolio_policy = portfolio.get("policy") or {}
    if portfolio:
        if portfolio.get("scientific_authority") is not False or portfolio_policy.get("expansion_precedes_reduction") is not True or portfolio_policy.get("mature_theory_veto_delayed_until_formulation") is not True: errors.append("Search Portfolio must remain zero-authority and separate expansion from reduction")
        if int(portfolio_summary.get("archive_lane_coverage") or 0) != len(DISCOVERY_LANES): errors.append("Search Portfolio breadth archive must preserve all discovery lanes")
    if generator.get("status") == "GENERATED_AWAIT_PROBLEM_GATE" and int(generator_summary.get("written_to_auto_inbox") or 0) != int(generator_summary.get("generated") or 0): errors.append("generated candidates must be written completely to the auto inbox before gate audit")
    problem_queue = state.get("paper_first_problem_gate_queue") or {}; problem_queue_summary = problem_queue.get("summary") or {}; problem_queue_policy = problem_queue.get("policy") or {}
    if problem_queue_summary.get("audited") != problem_queue_summary.get("submitted") or int(problem_queue_summary.get("passed_problem_gate") or 0) + int(problem_queue_summary.get("blocked_problem_gate") or 0) != int(problem_queue_summary.get("audited") or 0) or problem_queue_summary.get("inbox_errors") != 0: errors.append("paper-first problem gate queue accounting/inbox error")
    if problem_queue_policy.get("all_candidates_require_problem_gate") is not True or problem_queue_policy.get("problem_gate_pass_only_grants_human_paper_design_eligibility") is not True or problem_queue_policy.get("verified_primary_evidence_registry_required_for_submitted_candidates") is not True or problem_queue_policy.get("multi_lane_candidate_schema_required") is not True or problem_queue_policy.get("lane_contract_independent_review_required") is not True or problem_queue_policy.get("independent_semantic_reduction_review_required") is not True or problem_queue_policy.get("semantic_reviewer_is_block_only") is not True or problem_queue_summary.get("method_authorized") != 0 or problem_queue_summary.get("experiment_authorized") != 0 or problem_queue_summary.get("p0_authorized") != 0: errors.append("paper-first problem queue must require primary provenance + multi-lane contract + block-only semantic review and grant only paper-design eligibility")
    if (pf357_summary.get("reviewed"),pf357_summary.get("stopped_standalone"),pf357_summary.get("paper_design_authorized"),pf357_summary.get("local_validation_authorized")) != (3,3,0,0): errors.append("PF-3/PF-5/PF-7 must all terminate standalone before Paper Design/local validation")
    post_c2 = state.get("paper_first_post_c2") or {}; post_c2_auth = post_c2.get("authority") or {}
    if post_c2.get("decision") != "STOP_CURRENT_CONTROLLED_MEDIATOR_PAPER_MECHANISM" or post_c2_auth.get("clean_mechanism_stop") is not True: errors.append("post-C2 paper mechanism terminal adjudication must preserve the clean local falsifier STOP")
    if post_c2_auth.get("C3_locked") is not True or post_c2_auth.get("full_experiment_authorized") is not False: errors.append("post-C2 STOP must keep C3/full experiments locked")
    if post_c2_auth.get("new_method_auto_authorized") is not False or post_c2_auth.get("new_paper_problem_auto_authorized") is not False: errors.append("post-C2 STOP cannot auto-authorize a method or new paper problem")
    if (post_c2.get("gate_provenance") or {}).get("decision_invariant_to_later_gate_tightening") is not True: errors.append("post-C2 terminal state must report gate-version invariance")
    if (post_c2.get("decision_context_validity") or {}).get("pass") is not True: errors.append("post-C2 mechanism negative requires full decision-context validity")
    architecture = state.get("system_architecture") or {}; architecture_summary = architecture.get("summary") or {}
    if architecture_summary.get("temporal_stages") != 11 or architecture_summary.get("functional_layers") != 6: errors.append("backend architecture must expose one 11-stage lifecycle and six functional layers")
    if architecture_summary.get("assigned_components") != len(state.get("components") or []) or architecture_summary.get("unassigned_components") != 0: errors.append("every backend component must have exactly one primary architecture layer")
    if architecture_summary.get("duplicate_component_keys") != 0: errors.append("backend component architecture keys must be unique")
    if architecture_summary.get("cross_cutting_controls") != 3 or architecture_summary.get("orphan_cross_cutting_controls") != 0: errors.append("all cross-cutting methodology controls must resolve to an existing owner component")
    if not state["principle_layer"]["policy"]["experiment_is_evidence_about_a_principle_not_a_vote_on_an_idea"]: errors.append("experiments must remain evidence about principles rather than votes on ideas")
    if not state["principle_layer"]["policy"]["true_negative_does_not_automatically_falsify_principle"]: errors.append("true negatives must not automatically falsify principles")
    if state["principle_layer"]["summary"]["certificates_passed"] != expected_pre_experiment_cards: errors.append(f"all {expected_pre_experiment_cards} current pre-experiment cards must have valid principle certificates")
    if not state["pre_experiment_compiler"]["policy"]["paper_design_contract_required_before_principle_and_implementation"]: errors.append("Paper Design Contract must precede implementation and experiment execution")
    if not state["pre_experiment_compiler"]["policy"]["paper_design_contract_is_not_a_formal_gate"]: errors.append("Paper Design Contract must not inflate the formal eight-gate experiment compiler")
    if not state["pre_experiment_compiler"]["policy"]["principle_certificate_required_before_updater_competence"]: errors.append("Principle Certificate must be a hard prerequisite before updater competence")
    if not state["pre_experiment_compiler"]["policy"]["principle_certificate_is_not_a_formal_gate"]: errors.append("Principle Certificate must not inflate the formal gate count beyond eight")
    if not state["pre_experiment_compiler"]["policy"]["protocol_validity_required_before_updater_competence"]: errors.append("Protocol Validity must be a hard prerequisite before updater competence")
    if not state["pre_experiment_compiler"]["policy"]["protocol_validity_is_not_a_formal_gate"]: errors.append("Protocol Validity must not inflate the formal gate count beyond eight")
    if state["pre_experiment_compiler"]["summary"].get("protocol_validity_pass") != expected_pre_experiment_cards: errors.append(f"all {expected_pre_experiment_cards} current pre-experiment cards must pass Protocol Validity")
    if not state["pre_experiment_compiler"]["policy"]["research_execution_plan_required_before_launch"]: errors.append("a derived Research Execution Plan must exist before launch")
    if not state["pre_experiment_compiler"]["policy"]["research_execution_plan_is_derived_not_a_formal_gate"]: errors.append("Research Execution Plan must not inflate the formal gate count")
    if not state["pre_experiment_compiler"]["policy"]["research_execution_plan_cannot_authorize_execution"]: errors.append("Research Execution Plan must never authorize execution")
    if state["pre_experiment_compiler"]["summary"].get("research_execution_plans") != expected_pre_experiment_cards: errors.append(f"all {expected_pre_experiment_cards} current cards must expose a derived Research Execution Plan")
    if not state["pre_experiment_compiler"]["policy"]["updater_competence_required_before_gate_1"]: errors.append("Updater competence must be a hard prerequisite before Gate 1")
    if not state["pre_experiment_compiler"]["policy"]["updater_competence_is_not_a_ninth_gate"]: errors.append("Updater competence must not inflate the formal gate count beyond eight")
    if not state["pre_experiment_compiler"]["policy"]["all_eight_gates_required"]: errors.append("Pre-Experiment Compiler must require all eight gates")
    if not state["pre_experiment_compiler"]["policy"]["automatic_override_forbidden"]: errors.append("Pre-Experiment Compiler override must stay forbidden")
    if not state["pre_experiment_compiler"]["policy"]["terminal_outcome_requires_endpoint_headroom_audit"]: errors.append("terminal-outcome experiments must require endpoint-headroom evidence")
    if not state["pre_experiment_compiler"]["policy"]["execution_cap_censoring_must_be_typed_separately"]: errors.append("execution-cap censoring must have a distinct typed outcome")
    if not state["pre_experiment_compiler"]["policy"]["cap_censored_branch_cannot_count_as_natural_terminal_failure"]: errors.append("cap-censored branches must not be counted as natural terminal failures")
    if state["pre_experiment_compiler"]["summary"]["compiled_cards"] != expected_pre_experiment_cards: errors.append(f"expected {expected_pre_experiment_cards} frozen pre-experiment cards")
    paper_first_authority = state.get("paper_first_p0_authority") or {}; pfa_summary = paper_first_authority.get("summary") or {}
    if int(pfa_summary.get("promoted") or 0) > 0 and pfa_summary.get("authority_status") != "EXTERNAL_HUMAN_P0_PROMOTION_AUTHORITY_VALID": errors.append("paper-first P0 promotion requires a validated external human authority artifact")
    paper_first_f0 = state.get("paper_first_p0_f0") or {}; pf0_summary = paper_first_f0.get("summary") or {}
    if pf0_summary.get("ideas") != 4 or pf0_summary.get("quarantined") != 4 or pf0_summary.get("scientifically_authorized") != 0 or pf0_summary.get("method_fail_authorized") != 0: errors.append("paper-first premature local F0 must remain four diagnostic-only quarantined executions with zero scientific authority")
    if (paper_first_f0.get("policy") or {}).get("unauthorized_execution_is_preserved_as_diagnostic_not_scientific_authority") is not True: errors.append("paper-first premature execution must be preserved without creating scientific authority")
    if (paper_first_f0.get("policy") or {}).get("p0_method_requires_support_pass_and_pre_experiment_authority") is not True: errors.append("paper-first P0 method work must remain locked behind support plus Pre-Experiment authority")
    premature_method = state.get("paper_first_premature_method_diagnostics") or {}; pmd_summary = premature_method.get("summary") or {}; pmd_auth = premature_method.get("authority") or {}
    if (pmd_summary.get("directions"),pmd_summary.get("completed_diagnostics"),pmd_summary.get("design_holds"),pmd_summary.get("same_information_reducibility_findings"),pmd_summary.get("scientifically_authorized"),pmd_summary.get("p0_lifecycle_mutations"),pmd_summary.get("full_experiment_authorized")) != (2,2,1,2,0,0,0): errors.append("premature Paper-first Method diagnostics must remain two completed non-authoritative reducibility records")
    if pmd_auth.get("cannot_retroactively_authorize") is not True or pmd_auth.get("cannot_override_problem_or_design_adjudication") is not True or pmd_auth.get("scientific_authority") is not False: errors.append("premature Method diagnostics must remain subordinate to frozen paper authority")
    if not state["pilot_registry"]["policy"]["p0_execution_requires_pre_experiment_8_of_8"]: errors.append("P0 execution must require an 8/8 Pre-Experiment Card")
    if not state["pilot_registry"]["policy"]["automatic_p0_to_p1_forbidden"]: errors.append("automatic P0-to-P1 escalation must stay forbidden")
    if not state["experiment_iteration"]["policy"]["nonidentifiable_pilot_cannot_update_scientific_belief"]: errors.append("non-identifiable pilots must not update scientific belief")
    if not state["scientific_meta_trace"]["policy"]["raw_execution_trace_is_not_scientific_state"]: errors.append("raw trace must remain separate from compact scientific state")
    if not state["scientific_meta_trace"]["policy"]["active_scientific_state_is_separate_from_institutional_memory"]: errors.append("active scientific state must remain separate from institutional memory")
    if not state["scientific_meta_trace"]["policy"]["active_scientific_state_never_time_decays"]: errors.append("active scientific authority must never decay as memory")
    if not state["failure_asset_library"]["policy"]["assets_are_retrieved_before_new_experiment_design"]: errors.append("failure assets must be retrieved before new experiment design")
    if not state["failure_asset_library"]["policy"]["institutional_memory_requires_scope_and_effectiveness_tracking"]: errors.append("institutional failure memory must track scope and reuse effectiveness")
    if not state["experiment_value_scheduler"]["policy"]["scheduler_cannot_authorize_execution"]: errors.append("experiment value scheduler must remain advisory")
    if state["research_system_replay"]["summary"].get("failed") != 0: errors.append("research-system replay benchmark has failing epistemic cases")
    if not state["external_system_learning"]["policy"]["every_candidate_design_requires_local_gap_test"]: errors.append("external system designs require a local gap test before adoption")
    errors.extend(_mem_xfer_semantic_errors(state["mem_xfer_workflow"]))
    if not state["mem_xfer_workflow"].get("allowed_statuses"): errors.append("mem-xfer workflow must publish typed allowed statuses")
    if not state["mem_xfer_workflow"].get("dependencies"): errors.append("mem-xfer workflow must publish stage dependencies")
    terminal_summary = state["human_terminal_ideas"]["summary"]
    expected_active_p0 = int(terminal_summary.get("p0") or 0) + int(terminal_summary.get("independent_methods") or 0)
    if terminal_summary.get("human_parents") != 26 or terminal_summary.get("p0_resolved_lineages") != 26 or terminal_summary.get("drop") != 0 or terminal_summary.get("revived_to_p0") != 7: errors.append("human terminal ledger mismatch")
    if state["p0_admission"]["summary"].get("active_p0") != expected_active_p0 or state["p0_admission"]["summary"].get("admitted") != expected_active_p0 or state["p0_admission"]["summary"].get("transitioned_from_p0_ready") != 16 or state["p0_admission"]["summary"].get("revived_from_drop") != 7 or state["p0_admission"]["summary"].get("settings_complete") != expected_active_p0: errors.append("P0 admission ledger mismatch")
    economy = state.get("p0_economy_gate") or {}
    economy_summary = economy.get("summary") or {}
    if economy_summary.get("ideas") != expected_active_p0 or economy_summary.get("economy_ready") != state["p0_admission"]["summary"].get("economy_ready"): errors.append("P0 Economy active-card accounting mismatch")
    if (economy.get("policy") or {}).get("all_five_required_before_execution_compilation") is not True: errors.append("P0 Economy 5/5 must precede execution compilation")
    ai_clinic = state.get("ai_consultation_clinic") or {}
    if (ai_clinic.get("summary") or {}).get("checkpoints") != 5: errors.append("AI consultation clinic must expose five checkpoints")
    if (ai_clinic.get("policy") or {}).get("ai_vote_can_authorize_gpu") is not False: errors.append("AI consultation must never authorize GPU execution")
    if (ai_clinic.get("policy") or {}).get("high_risk_findings_must_be_compiled_into_machine_checks") is not True: errors.append("AI consultation findings must compile into machine checks")
    ai_automation = state.get("ai_consultation_automation") or {}
    if (ai_automation.get("policy") or {}).get("content_addressed_triggers") is not True: errors.append("AI consultation automation must use content-addressed triggers")
    if (ai_automation.get("policy") or {}).get("ai_output_never_authorizes_execution") is not True: errors.append("AI consultation automation must never authorize execution")
    if (ai_automation.get("clinic_policy") or {}).get("ai_vote_can_authorize_gpu") is not False: errors.append("AI consultation automation must preserve zero AI GPU authority")
    ledger = state.get("p0_decision_ledger") or {}
    if (ledger.get("summary") or {}).get("active_p0") != expected_active_p0: errors.append(f"P0 decision ledger must cover all {expected_active_p0} active P0 directions")
    if (ledger.get("summary") or {}).get("launchable") != state["p0_admission"]["summary"].get("execution_authorized"): errors.append("P0 decision ledger launchability must match execution authorization")
    if (ledger.get("policy") or {}).get("economy_stop_overrides_planned_registry_display") is not True: errors.append("P0 decision ledger must override stale planned display with terminal Economy evidence")
    updater_final = state.get("persistent_updater_program_final") or {}
    if updater_final.get("verdict") != "STOP_CURRENT_PERSISTENT_UPDATER_PROGRAM" or updater_final.get("batch_experiment_authorized") is not False or updater_final.get("second_backbone_authorized") is not False: errors.append("persistent updater terminal authority must keep batch and second backbone locked")
    if (updater_final.get("states") or {}).get("A2") != "KEEP_PROBLEM_HOLD_NO_QUALIFIED_UPDATER": errors.append("persistent updater terminal authority must keep A2 as upstream HOLD")
    governance = state.get("research_governance_v2") or {}
    if len(governance.get("stages") or []) != 7: errors.append("Research Governance v2 must expose seven ordered scientific stages")
    if (governance.get("policy") or {}).get("paper_novelty_precedes_method_design") is not True or (governance.get("policy") or {}).get("method_design_precedes_experiment_plan") is not True or (governance.get("policy") or {}).get("local_validation_precedes_full_experiment") is not True: errors.append("paper-first macro research ordering is missing")
    if (governance.get("policy") or {}).get("support_and_method_are_distinct") is not True or (governance.get("policy") or {}).get("p0_method_requires_frozen_support_pass") is not True: errors.append("P0 support/method stage separation policy missing")
    if (governance.get("policy") or {}).get("raw_trace_is_mandatory_for_gpu_runs") is not True or (governance.get("policy") or {}).get("pre_model_load_audit_required") is not True: errors.append("GPU trace/pre-model-load governance policy missing")
    if state["p0_offline_qualification"]["summary"].get("ideas") != 16 or state["p0_offline_qualification"]["policy"].get("method_result_from_offline_qualification_forbidden") is not True: errors.append("P0 offline qualification policy mismatch")
    if state["p0_realizability"]["summary"].get("audited") != 14 or state["p0_realizability"]["policy"].get("cannot_emit_method_result") is not True: errors.append("P0 realizability policy mismatch")
    batch = state.get("p0_revived_batch_f0") or {}; bs = batch.get("summary") or {}
    if (bs.get("parent_p0"), bs.get("reused_existing_p0"), bs.get("fresh_cpu_f0")) != (20,13,7): errors.append("20-Idea P0 batch accounting mismatch")
    if sum(int(bs.get(key) or 0) for key in ("fresh_matched_simplification_stop","fresh_upstream_hold","fresh_signal_continue")) != 7 or bs.get("gpu_queue_candidates_before_economy") != bs.get("fresh_signal_continue"): errors.append("20-Idea P0 fresh-routing accounting mismatch")
    if state["repair_queue"]["policy"].get("terminal_human_parent_repair_forbidden") is not False or state["repair_queue"]["policy"].get("stop_automatic_idea_iteration_at_p0") is not True or state["repair_queue"]["policy"].get("absorbed_child_repair_forbidden") is not True: errors.append("terminal repair policy missing")
    if state["pilot_registry"]["summary"]["invalid_approval_files"] != 0: errors.append("invalid pilot approval files")
    if not state["summary"]["final_ready"] or state["summary"]["final_pass"] != state["summary"]["discussion_target"]: errors.append("final advisor gate not ready")
    return errors


def write_research_system_state(json_path:Path=DEFAULT_JSON, js_path:Path=DEFAULT_JS) -> dict[str, Any]:
    write_human_terminal_state()
    write_p0_realizability_suite()
    write_revived_batch_f0()
    write_paper_first_p0_f0_state()
    write_b10_cpu_p0()
    write_a6_cpu_p0()
    write_p0_offline_qualification_state()
    write_p0_admission_state()
    write_four_direction_iteration()
    write_persistent_updater_program_final()
    write_paper_first_design_adjudication()
    write_pf1_problem_adjudication()
    write_pf2_method_adjudication()
    write_pf357_problem_adjudication()
    write_fresh_saturation_state()
    # Problem-gate Queue is a frozen output of the Primary -> Generator -> Queue
    # transaction. Rebuilding it here would couple research-system projection to
    # whichever host-private inbox happens to be mounted on this machine.
    write_post_c2_adjudication()
    write_premature_method_diagnostics()
    write_ai_consultation_clinic_state()
    state=build_research_system_state()
    write_p0_decision_ledger(state["p0_decision_ledger"])
    write_governance_state(PROJECT_ROOT / "generated" / "research-governance-v2.json", PROJECT_ROOT / "generated" / "research-governance-v2.js")
    errors=validate_state(state)
    if errors: raise ValueError("Invalid research system state:\n- " + "\n- ".join(errors))
    public_state=redact_private_paths(state,storage=StorageSettings.from_env())
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(public_state, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    js_path.write_text("window.RESEARCH_SYSTEM_STATE = "+json.dumps(public_state, ensure_ascii=False, separators=(",",":"))+";\n", encoding="utf-8")
    return state
