from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .candidate_identity import validate_candidate_identity
from .config import PROJECT_ROOT, StorageSettings, resolve_experiment_data_root
from .asset_first_stri_public_status import build_asset_first_stri_public_status, validate_asset_first_stri_public_status
from .asset_first_stri_paper_quality import write_asset_first_stri_paper_quality
from .ai_consultation_clinic import build_ai_consultation_clinic_state, write_ai_consultation_clinic_state
from .ai_consultation_automation import DEFAULT_JSON as AI_CONSULTATION_AUTOMATION_JSON, PUBLIC_POLICY as AI_AUTOMATION_POLICY
from .discussion_portfolio import build_discussion_portfolio
from .evidence_graph import build_evidence_graph
from .evidence_integrity import build_evidence_integrity_state
from .paper_quality_gate import POLICY as PAPER_QUALITY_POLICY
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
from .paper_visual_evidence import build_paper_visual_evidence_portfolio
from .paper_acceptance import PAPER_ACCEPTANCE_TEMPORAL_KEYS, build_paper_acceptance_system_state
from .paper_acceptance_ledger import build_paper_ledger_index, build_portable_paper_ledger_index
from .paper_first_design_adjudication import build_paper_first_design_adjudication, write_paper_first_design_adjudication
from .paper_first_pf1_problem_adjudication import build_pf1_problem_adjudication, write_pf1_problem_adjudication
from .paper_first_pf2_method_adjudication import build_pf2_method_adjudication, write_pf2_method_adjudication
from .paper_first_pf357_problem_adjudication import build_pf357_problem_adjudication, write_pf357_problem_adjudication
from .paper_first_fresh_saturation import build_fresh_saturation_state, write_fresh_saturation_state
from .paper_first_primary_evidence import SUPPORTED_TYPED_EVIDENCE_SNAPSHOT_VERSIONS, TYPED_EVIDENCE_EXTRACTION_VERSION, load_primary_evidence_state
from .paper_first_scientific_object_candidate_evidence import load_scientific_object_candidate_evidence_ledger, public_scientific_object_candidate_evidence_summary
from .paper_first_scientific_object_retrieval_audit import load_private_shadow_scientific_object_retrieval_audit, public_shadow_scientific_object_retrieval_summary
from .paper_first_support_release_watch import load_private_support_release_watch, public_support_release_watch_summary
from .paper_first_support_asset_recheck import load_private_support_asset_recheck_queue, public_support_asset_recheck_summary
from .paper_first_support_asset_recheck_handoff import load_private_support_asset_recheck_handoff, public_support_asset_recheck_handoff_summary
from .paper_first_discovery_frontier import build_paper_first_discovery_frontier, validate_paper_first_discovery_frontier
from .paper_first_fresh_phenomenon_portfolio import DEFAULT_JSON as FRESH_PHENOMENON_PORTFOLIO_JSON, build_fresh_phenomenon_portfolio, validate_fresh_phenomenon_portfolio, write_fresh_phenomenon_portfolio
from .paper_first_skill_validation_transfer_scout import write_skill_validation_transfer_scout
from .paper_first_legacy_reduction_migration import load_public_migration, validate_public_migration
from .paper_first_problem_discovery_contract import DISCOVERY_LANES, DISCOVERY_OPERATOR_VERSION, SEARCH_PORTFOLIO_PRIMITIVES, FORBIDDEN_DISCOVERY_LANES, build_problem_discovery_contract_state
from .paper_first_problem_generator import installed_problem_generator_policy, load_problem_generator_state
from .paper_first_problem_gate_queue import load_problem_gate_queue_state
from .paper_first_pre_f0_queue import load_pre_f0_queue
from .paper_first_problem_falsifier_preflight import load_pre_f0_problem_falsifier_preflight
from .paper_first_shadow_search_admission import DEFAULT_JSON as SHADOW_SEARCH_ADMISSION_JSON, build_shadow_search_admission, public_shadow_search_admission_summary, validate_shadow_search_admission, write_shadow_search_admission
from .paper_first_shadow_continuation_frontier import build_shadow_continuation_frontier, validate_shadow_continuation_frontier
from .paper_first_search_portfolio_design_adjudication import DEFAULT_JSON as SEARCH_PORTFOLIO_DESIGN_JSON, build_search_portfolio_design_adjudication, validate_search_portfolio_design_adjudication, write_search_portfolio_design_adjudication
from .paper_first_sp15_identifiability_support import build_sp15_identifiability_support, write_sp15_identifiability_support
from .paper_first_global_relation_recall import lane_review_execution_contract_sha256, load_global_relation_recall_state
from .paper_first_global_relation_scan_admission import build_global_relation_scan_admission, public_global_relation_scan_admission_summary
from .paper_first_relation_coverage import relation_recall_freshness
from .paper_first_relation_delta_preflight import load_private_relation_delta_preflight, public_relation_delta_preflight_summary
from .paper_first_paper_design_backlog import load_paper_design_backlog
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
from .research_candidate_portfolio import build_research_candidate_portfolio
from .research_harness_assurance import build_research_harness_assurance
from .research_memory_wiki import build_research_memory_wiki, write_research_memory_wiki
from .search_funnel_telemetry import build_search_funnel_telemetry
from .premium_model_policy import policy_summary as premium_model_policy_summary
from .public_state_redaction import redact_private_paths
from .research_system_replay import build_research_system_replay
from .review_repair import build_repair_queue
from .scientific_meta_trace import build_scientific_meta_trace
from .scientific_research_graph import build_scientific_research_graph
from .system_architecture import READING_GROUPS, TEMPORAL_FLOW, annotate_components, build_system_architecture

DEFAULT_JSON = PROJECT_ROOT / "generated" / "research-system-state.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "research-system-state.js"

_HOST_OR_LOCAL_REPO_PATH = re.compile(
    r"(?P<prefix>(?:host[^:]+:)?)?/(?:[^/\"#\s]+/)*agent-self-evolution-observatory(?:-[^/\"#\s]+)?/"
)


def _registered_private_data_roots() -> tuple[str, ...]:
    roots = {str(resolve_experiment_data_root(StorageSettings.from_env()).resolve()).rstrip("/")}
    profile_path = PROJECT_ROOT / "research_pipeline" / "experiment_orchestrator_profiles.json"
    try:
        payload = json.loads(profile_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        payload = {}
    for row in payload.get("servers") or []:
        if isinstance(row, dict) and str(row.get("data_root") or "").strip():
            roots.add(str(Path(str(row["data_root"])).expanduser().resolve()).rstrip("/"))
    return tuple(sorted((root for root in roots if root), key=len, reverse=True))


def _canonicalize_public_state_locations(value: Any, *, _private_roots: tuple[str, ...] | None = None) -> Any:
    """Normalize private/public path spellings before durable-state comparison.

    Public state intentionally redacts machine-local data/repository roots, while
    durable research receipts may retain their original absolute provenance. The
    validator must compare the same scientific object without requiring public
    artifacts to re-expose those private paths. Registered server roots make this
    comparison independent of which checkout or CI host performs validation.
    """
    private_roots = _private_roots or _registered_private_data_roots()
    if isinstance(value, dict):
        return {str(key): _canonicalize_public_state_locations(item, _private_roots=private_roots) for key, item in value.items()}
    if isinstance(value, list):
        return [_canonicalize_public_state_locations(item, _private_roots=private_roots) for item in value]
    if isinstance(value, tuple):
        return [_canonicalize_public_state_locations(item, _private_roots=private_roots) for item in value]
    if not isinstance(value, str):
        return value
    text = value.replace("private-data://", "<PRIVATE_DATA>/")
    for private_root in private_roots:
        text = text.replace(private_root + "/", "<PRIVATE_DATA>/")
    text = text.replace("repo://", "<REPO>/")
    return _HOST_OR_LOCAL_REPO_PATH.sub(
        lambda match: f"{match.group('prefix') or ''}<REPO>/",
        text,
    )


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
    visual_evidence = state["paper_visual_evidence"]["summary"]
    paper_post_c2 = state["paper_first_post_c2"]
    principle = state["principle_layer"]["summary"]
    meta_trace = state["scientific_meta_trace"]["summary"]
    research_graph = state["scientific_research_graph"]["summary"]
    research_memory = state["research_memory_wiki"]["summary"]
    research_memory_lint = state["research_memory_wiki"]["lint"]["summary"]
    failure_assets = state["failure_asset_library"]["summary"]
    value_scheduler = state["experiment_value_scheduler"]["summary"]
    replay = state["research_system_replay"]["summary"]
    external_learning = state["external_system_learning"]["summary"]
    candidate_portfolio = state["research_candidate_portfolio"]["summary"]
    search_funnel = state["search_funnel_telemetry"]
    harness_assurance = state["research_harness_assurance"]["summary"]
    paper_acceptance = state["paper_acceptance"]["summary"]
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
        {"source":"ARIS + local double-funnel", "component":{"en":"Adversarial fan-out + independent jury harness","zh":"对抗式 Fan-out + 独立 Jury Harness"}, "status":"running", "evidence":{"en":f"{harness_assurance['passed']}/{harness_assurance['checks']} harness invariants pass; resolved-model violations={harness_assurance['resolved_model_independence_violations']}","zh":f"Harness 不变量 {harness_assurance['passed']}/{harness_assurance['checks']} 通过；resolved-model 独立性违规={harness_assurance['resolved_model_independence_violations']}"}},
        {"source":"ARIS portfolio persistence + local scientific gates", "component":{"en":"Persistent multi-candidate research portfolio","zh":"持久化多候选科研组合"}, "status":"running", "evidence":{"en":f"{candidate_portfolio['visible_candidates']} visible / {candidate_portfolio['active_problem_lines']} active / {candidate_portfolio['search_holds']} search holds; capacity targets are advisory only","zh":f"{candidate_portfolio['visible_candidates']} 条可见 / {candidate_portfolio['active_problem_lines']} 条 active / {candidate_portfolio['search_holds']} 条 search hold；容量目标仅用于调度"}},
        {"source":"ARIS meta-optimization pattern + local typed failure semantics", "component":{"en":"Search funnel + bottleneck telemetry","zh":"搜索漏斗 + 瓶颈遥测"}, "status":"running", "evidence":{"en":f"current bottleneck={search_funnel['bottleneck']['key']}; telemetry has zero scientific authority","zh":f"当前瓶颈={search_funnel['bottleneck']['key']}；遥测不拥有科学权限"}},
        {"source":"AIDE / AI-Scientist-v2 / R&D-Agent", "component":{"en":"Pre-P0 identifiability auditor","zh":"Pre-P0 实验可识别性审计"}, "status":"running", "evidence":{"en":f"{pre_p0['execution_ready']}/{pre_p0['audited']} retrospective contracts execution-ready","zh":f"当前 {pre_p0['execution_ready']}/{pre_p0['audited']} 份 retrospective 合同允许启动"}},
        {"source":"Advisor paper-first research contract", "component":{"en":"Paper novelty → method → experiment blueprint contract","zh":"论文 Novelty → 方法 → 实验蓝图合同"}, "status":"running", "evidence":{"en":f"{paper_first['paper_design_passed']}/{paper_first['cards']} live cards satisfy paper-first / visual portfolio {visual_evidence['planned_main_visualizations']} planned across {visual_evidence['paper_first_designs']} paper-first designs + {visual_evidence['stri_completed_main_visualizations']} STRI completed / post-C2: {paper_post_c2['decision']}","zh":f"当前 {paper_first['paper_design_passed']}/{paper_first['cards']} 份 live 卡满足 paper-first / 可视化组合：{visual_evidence['paper_first_designs']} 个 paper-first 设计共规划 {visual_evidence['planned_main_visualizations']} 张主图 + STRI 已完成 {visual_evidence['stri_completed_main_visualizations']} 张 / post-C2：{paper_post_c2['decision']}"}},
        {"source":"FirstResearch / Popper / Co-Scientist / RD-Agent", "component":{"en":"Principle Certificate + epistemic adjudicator","zh":"原理证书 + 认识论裁决器"}, "status":"running", "evidence":{"en":f"{principle['certificates_passed']}/{principle['cards']} principle certificates valid / {principle.get('registered_prediction_rejections_pending_counterexplanation',0)} prediction rejections awaiting counter-explanation / {principle.get('principle_dead_end_certifications',0)} certified principle dead ends","zh":f"{principle['certificates_passed']}/{principle['cards']} 份原理证书有效 / {principle.get('registered_prediction_rejections_pending_counterexplanation',0)} 个预测反证待反机制解释 / {principle.get('principle_dead_end_certifications',0)} 个原理级 Dead-End 已认证"}},
        {"source":"Qiushi / Kosmos / MLEvolve", "component":{"en":"Scientific Meta-Trace + cross-branch world state","zh":"Scientific Meta-Trace + 跨分支科研状态"}, "status":"running", "evidence":{"en":f"{meta_trace['principles']} principles / {meta_trace['unresolved_principles']} unresolved / {meta_trace['cross_branch_reference_edges']} cross-branch links","zh":f"{meta_trace['principles']} 个原理 / {meta_trace['unresolved_principles']} 个未决 / {meta_trace['cross_branch_reference_edges']} 条跨分支引用"}},
        {"source":"ARIS research wiki pattern + local typed closure", "component":{"en":"Typed Scientific Research Graph","zh":"类型化科学研究图谱"}, "status":"running", "evidence":{"en":f"{research_graph['nodes']} graph nodes / {research_graph['edges']} edges; memory wiki {research_memory['entries']} entries / {research_memory['failure_assets']} failure / {research_memory['success_assets']} success / {research_memory.get('review_lessons',0)} paper-review lessons / lint warnings {research_memory_lint['warnings']}","zh":f"研究图谱 {research_graph['nodes']} 个节点 / {research_graph['edges']} 条边；Memory Wiki {research_memory['entries']} 条 / 失败 {research_memory['failure_assets']} / 成功 {research_memory['success_assets']} / 论文审查经验 {research_memory.get('review_lessons',0)} / lint warning {research_memory_lint['warnings']}"}},
        {"source":"MLEvolve / InternAgent / AutoResearchClaw", "component":{"en":"Failure Asset + dead-end memory","zh":"失败资产 + Dead-End 记忆库"}, "status":"running", "evidence":{"en":f"{failure_assets['assets']} failure assets / {failure_assets['unique_signatures']} reusable signatures / {failure_assets.get('experimental_stops_not_dead_ends',0)} experimental stops retained as diagnostics / {failure_assets.get('principle_dead_ends',0)} principle-certified dead ends","zh":f"{failure_assets['assets']} 条失败资产 / {failure_assets['unique_signatures']} 类可复用签名 / {failure_assets.get('experimental_stops_not_dead_ends',0)} 个实验 STOP 仅作诊断 / {failure_assets.get('principle_dead_ends',0)} 个原理认证 Dead-End"}},
        {"source":"Ai2 AutoDiscovery / MLEvolve / AI-Scientist-v2", "component":{"en":"Information-gain experiment portfolio scheduler","zh":"信息增益实验组合调度器"}, "status":"running", "evidence":{"en":f"{value_scheduler['candidates']} candidate tests / {value_scheduler['cross_branch_reference_edges']} cross-branch references / advisory only","zh":f"{value_scheduler['candidates']} 个候选实验 / {value_scheduler['cross_branch_reference_edges']} 条跨分支引用 / 仅建议不授权"}},
        {"source":"ResearchClawBench / HackDetect / ScienceAgentBench / AutoLabs", "component":{"en":"Protocol-validity auditor + research-system replay benchmark","zh":"协议有效性审计 + 科研系统回放基准"}, "status":"running", "evidence":{"en":f"protocol {pre_experiment['protocol_validity_pass']}/{pre_experiment['compiled_cards']} / replay {replay['passed']}/{replay['cases']}","zh":f"Protocol {pre_experiment['protocol_validity_pass']}/{pre_experiment['compiled_cards']} / 回放 {replay['passed']}/{replay['cases']}"}},
        {"source":"External-system intake registry", "component":{"en":"Continuous external research-system learning","zh":"持续外部科研系统学习"}, "status":"running", "evidence":{"en":f"{external_learning['systems_reviewed']} systems / {external_learning['adopted']} adopted / {external_learning['next_backlog']} next backlog","zh":f"已审 {external_learning['systems_reviewed']} 个系统 / {external_learning['adopted']} 个已吸收 / {external_learning['next_backlog']} 个下一批"}},
        {"source":"ARIS / ResearchArena / AI-Scientist-v2 / reviewer-decision workflow", "component":{"en":"Paper acceptance closure and manuscript integrity","zh":"论文验收闭环与成稿完整性"}, "status":"running", "evidence":{"en":f"{paper_acceptance['paper_states']} paper states / {paper_acceptance['registered_papers']} ledgers / {paper_acceptance['ledger_submission_ready_papers']} ledger-ready / {paper_acceptance['gate_clean_submission_ready_papers']} latest gate-clean / {paper_acceptance['internal_action_required_papers']} internal action required / zero automatic authority","zh":f"{paper_acceptance['paper_states']} 个论文状态 / {paper_acceptance['registered_papers']} 个 ledger / {paper_acceptance['ledger_submission_ready_papers']} 个历史 ready / {paper_acceptance['gate_clean_submission_ready_papers']} 个最新门禁 clean / {paper_acceptance['internal_action_required_papers']} 个仍需内部动作 / 自动权限为 0"}},
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


def _load_shadow_search_portfolio_public() -> dict[str, Any]:
    path = PROJECT_ROOT / "generated" / "paper-first-problem-search-portfolio-state.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema_version":"1.0-shadow","status":"NOT_RUN","policy":{"shadow_only":True,"scientific_authority":False},"latest_run":{},"scientific_authority":False}
    return payload if isinstance(payload,dict) else {"schema_version":"1.0-shadow","status":"STATE_INVALID","policy":{"shadow_only":True,"scientific_authority":False},"latest_run":{},"scientific_authority":False}


def _load_or_build_search_portfolio_design_adjudication() -> dict[str, Any]:
    """Use the validated durable adjudication as the projection source.

    The adjudication builder intentionally folds persistent search-memory provenance
    into a new snapshot. Rebuilding it as a side effect of composing ResearchSystem
    can therefore relabel an already-recorded closure as "new" versus "inherited"
    even when the scientific object and decision are unchanged. ResearchSystem is a
    read-only composition layer: prefer the durable zero-authority artifact, and only
    rebuild when that artifact is absent or invalid.
    """
    try:
        payload = json.loads(SEARCH_PORTFOLIO_DESIGN_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        payload = {}
    if isinstance(payload, dict) and payload and not validate_search_portfolio_design_adjudication(payload):
        return payload
    return build_search_portfolio_design_adjudication()


def _load_or_build_fresh_phenomenon_portfolio() -> dict[str, Any]:
    """Project the validated durable fresh-phenomenon ledger without re-adjudicating it."""
    try:
        payload = json.loads(FRESH_PHENOMENON_PORTFOLIO_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        payload = {}
    if isinstance(payload, dict) and payload and not validate_fresh_phenomenon_portfolio(payload):
        return payload
    return build_fresh_phenomenon_portfolio()


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
    paper_first_scientific_object_retrieval = public_shadow_scientific_object_retrieval_summary(load_private_shadow_scientific_object_retrieval_audit(storage=storage))
    paper_first_scientific_object_candidate_evidence = public_scientific_object_candidate_evidence_summary(load_scientific_object_candidate_evidence_ledger(storage=storage))
    paper_first_problem_discovery_contract = build_problem_discovery_contract_state()
    paper_first_problem_generator = load_problem_generator_state()
    paper_first_pre_f0_queue = load_pre_f0_queue()
    paper_first_pre_f0_problem_falsifier_preflight = load_pre_f0_problem_falsifier_preflight()
    paper_first_problem_memory = ((paper_first_problem_generator.get("saturation_memory") or {}).get("blocked_problem_memory") or {})
    paper_first_lane_search = paper_first_problem_generator.get("search_diagnostics") or {}
    paper_first_last_lane_search = paper_first_lane_search.get("last_completed_lane_search") or {}
    paper_first_problem_gate_queue = load_problem_gate_queue_state()
    paper_first_search_portfolio_design = _load_or_build_search_portfolio_design_adjudication()
    paper_first_support_release_watch = public_support_release_watch_summary(load_private_support_release_watch(storage=storage))
    paper_first_support_asset_recheck = public_support_asset_recheck_summary(load_private_support_asset_recheck_queue(storage=storage))
    paper_first_support_asset_recheck_handoff = public_support_asset_recheck_handoff_summary(load_private_support_asset_recheck_handoff(storage=storage))
    paper_first_sp15_support = build_sp15_identifiability_support()
    paper_first_paper_design_backlog = load_paper_design_backlog()
    paper_first_global_relation_recall = load_global_relation_recall_state()
    paper_first_global_relation_freshness = relation_recall_freshness(paper_first_problem_generator, paper_first_global_relation_recall)
    paper_first_global_relation_delta_private = load_private_relation_delta_preflight(storage=storage)
    paper_first_global_relation_delta_preflight = public_relation_delta_preflight_summary(paper_first_global_relation_delta_private)
    paper_first_global_relation_scan_admission = public_global_relation_scan_admission_summary(build_global_relation_scan_admission(primary_state=paper_first_primary_evidence,generator_state=paper_first_problem_generator,queue_state=paper_first_problem_gate_queue,relation_state=paper_first_global_relation_recall,delta_state=paper_first_global_relation_delta_private))
    paper_first_problem_search_portfolio = _load_shadow_search_portfolio_public()
    paper_first_evidence_migration = load_public_migration()
    asset_first_stri_paper_ready = build_asset_first_stri_public_status()
    paper_visual_evidence = build_paper_visual_evidence_portfolio()
    paper_first_shadow_search_admission = public_shadow_search_admission_summary(build_shadow_search_admission(primary_state=paper_first_primary_evidence,generator_state=paper_first_problem_generator,queue_state=paper_first_problem_gate_queue,shadow_state=paper_first_problem_search_portfolio))
    paper_first_shadow_continuation_frontier = build_shadow_continuation_frontier(admission=paper_first_shadow_search_admission,support_watch=paper_first_support_release_watch,asset_queue=paper_first_support_asset_recheck,support_handoff=paper_first_support_asset_recheck_handoff)
    paper_first_discovery_frontier = build_paper_first_discovery_frontier(
        primary_state=paper_first_primary_evidence,
        generator_state=paper_first_problem_generator,
        queue_state=paper_first_problem_gate_queue,
        relation_freshness_state=paper_first_global_relation_freshness,
        relation_admission_state=paper_first_global_relation_scan_admission,
        shadow_admission_state=paper_first_shadow_search_admission,
        object_candidate_state=paper_first_scientific_object_candidate_evidence,
        support_release_watch_state=paper_first_support_release_watch,
        support_asset_recheck_state=paper_first_support_asset_recheck,
        shadow_portfolio_state=paper_first_problem_search_portfolio,
        evidence_migration_state=paper_first_evidence_migration,
    )
    research_candidate_portfolio = build_research_candidate_portfolio(
        generator_state=paper_first_problem_generator,
        pre_f0_state=paper_first_pre_f0_queue,
        problem_gate_state=paper_first_problem_gate_queue,
        paper_design_backlog_state=paper_first_paper_design_backlog,
    )
    search_funnel_telemetry = build_search_funnel_telemetry(
        primary_state=paper_first_primary_evidence,
        generator_state=paper_first_problem_generator,
        pre_f0_state=paper_first_pre_f0_queue,
        pre_f0_support_state=paper_first_pre_f0_problem_falsifier_preflight,
        problem_gate_state=paper_first_problem_gate_queue,
        discovery_frontier_state=paper_first_discovery_frontier,
        candidate_portfolio_state=research_candidate_portfolio,
    )
    paper_first_fresh_phenomenon_portfolio = _load_or_build_fresh_phenomenon_portfolio()
    paper_first_shadow_latest = paper_first_problem_search_portfolio.get("latest_run") or {}
    paper_first_shadow_latest_summary = paper_first_shadow_latest.get("summary") or {}
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
    research_harness_assurance = build_research_harness_assurance(
        discovery_contract_state=paper_first_problem_discovery_contract,
        generator_state=paper_first_problem_generator,
        installed_generator_policy=installed_problem_generator_policy(portfolio=True),
        premium_model_policy=premium_model_policy_summary(),
        governance_state=research_governance_v2,
        paper_quality_policy=PAPER_QUALITY_POLICY,
        candidate_portfolio_state=research_candidate_portfolio,
        search_telemetry_state=search_funnel_telemetry,
    )
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
    failure_asset_library = build_failure_asset_library(experiment_iteration, p0_economy_public, paper_first_post_c2, paper_first_p0_f0, principle_layer)
    live_ledger_index = build_paper_ledger_index(experiment_data_root)
    live_ledger_summary = live_ledger_index.get("summary") or {}
    paper_ledger_index = live_ledger_index
    paper_ledger_source = "canonical-append-only-paper-ledgers"
    # Automation/CI hosts may not mirror the research host's private append-only
    # paper ledgers. An empty local directory is missing substrate, not evidence
    # that a published PaperState disappeared. Invalid live ledgers stay fail-closed.
    if int(live_ledger_summary.get("papers") or 0) == 0 and int(live_ledger_summary.get("invalid_ledgers") or 0) == 0:
        try:
            portable_registry = json.loads((PROJECT_ROOT / "generated" / "paper-registry.json").read_text(encoding="utf-8"))
            portable_index = build_portable_paper_ledger_index(portable_registry)
            portable_summary = portable_index.get("summary") or {}
            if int(portable_summary.get("papers") or 0) > 0 or int(portable_summary.get("invalid_ledgers") or 0) > 0:
                paper_ledger_index = portable_index
                paper_ledger_source = "generated/paper-registry.json"
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    research_memory_wiki = build_research_memory_wiki(
        search_design_state=paper_first_search_portfolio_design,
        failure_asset_library=failure_asset_library,
        scientific_meta_trace=scientific_meta_trace,
        candidate_portfolio=research_candidate_portfolio,
        experiment_iteration=experiment_iteration,
        generator_state=paper_first_problem_generator,
        paper_ledger_index=paper_ledger_index,
    )
    scientific_research_graph = build_scientific_research_graph(
        evidence_graph=evidence_graph,
        candidate_portfolio=research_candidate_portfolio,
        scientific_meta_trace=scientific_meta_trace,
        failure_asset_library=failure_asset_library,
        pilot_registry=pilot_registry,
    )
    experiment_value_scheduler = build_experiment_value_scheduler(experiment_iteration, scientific_meta_trace)
    research_system_replay = build_research_system_replay(pre_experiment_compiler)
    external_system_learning = build_external_system_learning_state()
    paper_acceptance = build_paper_acceptance_system_state()
    paper_acceptance["ledger_index"] = paper_ledger_index
    paper_acceptance["ledger_index_source"] = paper_ledger_source
    paper_summary = paper_ledger_index.get("summary") or {}
    paper_acceptance["summary"].update({
        "registered_papers": int(paper_summary.get("papers") or 0),
        "scientific_holds": int(paper_summary.get("scientific_holds") or 0),
        "ledger_submission_ready_papers": int(paper_summary.get("submission_ready") or 0),
        "submission_ready_papers": int(paper_summary.get("submission_ready") or 0),
        "gate_clean_submission_ready_papers": int(paper_summary.get("gate_clean_submission_ready") or 0),
        "paper_preparation_failed_papers": int(paper_summary.get("paper_preparation_failed") or 0),
        "immediate_submission_holds": int(paper_summary.get("immediate_submission_holds") or 0),
        "internal_action_required_papers": int(paper_summary.get("internal_action_required") or 0),
        "no_internal_action_papers": int(paper_summary.get("no_internal_action") or 0),
        "invalid_ledgers": int(paper_summary.get("invalid_ledgers") or 0),
    })
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
            "paper_visual_evidence_status":paper_visual_evidence.get("status"),
            "paper_visual_evidence_designs":int((paper_visual_evidence.get("summary") or {}).get("paper_first_designs") or 0),
            "paper_visual_evidence_planned_main":int((paper_visual_evidence.get("summary") or {}).get("planned_main_visualizations") or 0),
            "paper_visual_evidence_stri_completed_main":int((paper_visual_evidence.get("summary") or {}).get("stri_completed_main_visualizations") or 0),
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
            "paper_first_primary_carrier_probe_required":bool((paper_first_primary_evidence.get("summary") or {}).get("carrier_probe_required")),
            "paper_first_primary_carrier_probe_attempted":int((paper_first_primary_evidence.get("summary") or {}).get("carrier_probe_attempted") or 0),
            "paper_first_primary_carrier_probe_rescued":int((paper_first_primary_evidence.get("summary") or {}).get("carrier_probe_rescued") or 0),
            "paper_first_primary_carrier_probe_pending":int((paper_first_primary_evidence.get("summary") or {}).get("carrier_probe_pending") or 0),
            "paper_first_primary_carrier_probe_complete":bool((paper_first_primary_evidence.get("summary") or {}).get("carrier_probe_complete",True)),
            "paper_first_primary_generation_ready":bool((paper_first_primary_evidence.get("summary") or {}).get("candidate_generation_ready")),
            "paper_first_object_retrieval_candidates_audited":(paper_first_scientific_object_retrieval.get("summary") or {}).get("candidates_audited",0),
            "paper_first_object_retrieval_recall_gaps":(paper_first_scientific_object_retrieval.get("summary") or {}).get("recall_gap_support_insufficient",0),
            "paper_first_object_retrieval_threshold_candidates":(paper_first_scientific_object_retrieval.get("summary") or {}).get("primary_verification_threshold_candidates",0),
            "paper_first_object_retrieval_no_new_support":(paper_first_scientific_object_retrieval.get("summary") or {}).get("no_new_support_found",0),
            "paper_first_object_retrieval_activation_authorized":(paper_first_scientific_object_retrieval.get("summary") or {}).get("activation_authorized",0),
            "paper_first_object_candidate_primary_verified":(paper_first_scientific_object_candidate_evidence.get("summary") or {}).get("primary_verified",0),
            "paper_first_object_candidate_empirical_supported":(paper_first_scientific_object_candidate_evidence.get("summary") or {}).get("empirical_supported",0),
            "paper_first_object_candidate_failure_supported":(paper_first_scientific_object_candidate_evidence.get("summary") or {}).get("measured_failure_supported",0),
            "paper_first_object_candidate_pending_cache":(paper_first_scientific_object_candidate_evidence.get("summary") or {}).get("pending_cache",0),
            "paper_first_object_candidate_activation_authorized":(paper_first_scientific_object_candidate_evidence.get("summary") or {}).get("activation_authorized",0),
            "paper_first_problem_gate_fields":paper_first_problem_discovery_contract["summary"]["required_top_level_fields"],
            "paper_first_problem_gate_saturation_patterns":paper_first_problem_discovery_contract["summary"]["saturation_patterns"],
            "paper_first_problem_generator_status":paper_first_problem_generator.get("status"),
            "paper_first_problem_generator_generated":(paper_first_problem_generator.get("summary") or {}).get("generated",0),
            "paper_first_problem_generator_raw_seeds":(paper_first_problem_generator.get("summary") or {}).get("raw_seeds",0),
            "paper_first_problem_generator_semantic_unique_seeds":(paper_first_problem_generator.get("summary") or {}).get("semantic_unique_seeds",0),
            "paper_first_problem_generator_evolved_branches":(paper_first_problem_generator.get("summary") or {}).get("evolved_branches",0),
            "paper_first_problem_generator_reviewer_attacks":(paper_first_problem_generator.get("summary") or {}).get("reviewer_attacks",0),
            "paper_first_problem_generator_repair_children":(paper_first_problem_generator.get("summary") or {}).get("repair_children",0),
            "paper_first_problem_generator_pre_f0_eligible":(paper_first_problem_generator.get("summary") or {}).get("pre_f0_eligible",0),
            "paper_first_pre_f0_queue_status":paper_first_pre_f0_queue.get("status"),
            "paper_first_pre_f0_queue_queued":(paper_first_pre_f0_queue.get("summary") or {}).get("queued",0),
            "paper_first_pre_f0_support_status":paper_first_pre_f0_problem_falsifier_preflight.get("status"),
            "paper_first_pre_f0_support_ready":(paper_first_pre_f0_problem_falsifier_preflight.get("summary") or {}).get("support_qualified",0),
            "paper_first_pre_f0_support_holds":(paper_first_pre_f0_problem_falsifier_preflight.get("summary") or {}).get("hold_support_unavailable",0),
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
            "paper_first_problem_last_lane_search_available":bool(paper_first_last_lane_search),
            "paper_first_problem_last_lane_search_run_id":paper_first_last_lane_search.get("run_id",""),
            "paper_first_problem_last_lane_search_candidate_lanes":sum(str(row.get("status") or "") == "CANDIDATE" for row in paper_first_last_lane_search.get("lane_search") or [] if isinstance(row,dict)),
            "paper_first_problem_last_lane_search_reducible_lanes":sum(str(row.get("status") or "") == "REDUCIBLE" for row in paper_first_last_lane_search.get("lane_search") or [] if isinstance(row,dict)),
            "paper_first_problem_last_lane_search_no_pair_lanes":sum(str(row.get("status") or "") == "NO_PAIR" for row in paper_first_last_lane_search.get("lane_search") or [] if isinstance(row,dict)),
            "paper_first_problem_queue_submitted":paper_first_problem_gate_queue["summary"]["submitted"],
            "paper_first_problem_queue_passed":paper_first_problem_gate_queue["summary"]["passed_problem_gate"],
            "paper_first_problem_queue_blocked":paper_first_problem_gate_queue["summary"]["blocked_problem_gate"],
            "paper_first_search_portfolio_design_reviewed":paper_first_search_portfolio_design["summary"]["reviewed"],
            "paper_first_search_portfolio_design_advance_method":paper_first_search_portfolio_design["summary"]["advance_to_method_design"],
            "paper_first_search_portfolio_design_revise":paper_first_search_portfolio_design["summary"]["revise_paper_problem"],
            "paper_first_search_portfolio_design_stop":paper_first_search_portfolio_design["summary"]["stop_standalone"],
            "paper_first_search_portfolio_current_source_hard_veto_dead_ends":paper_first_search_portfolio_design["summary"].get("current_source_hard_veto_dead_ends",0),
            "paper_first_search_portfolio_current_source_hard_veto_added_latest":paper_first_search_portfolio_design["summary"].get("current_source_hard_veto_added_from_latest_run",0),
            "paper_first_search_portfolio_current_source_hard_veto_added_terminal":paper_first_search_portfolio_design["summary"].get("current_source_hard_veto_added_from_terminal_run",0),
            "paper_first_search_portfolio_current_source_hard_veto_inherited":paper_first_search_portfolio_design["summary"].get("current_source_hard_veto_inherited",0),
            "paper_first_search_portfolio_semantic_blocker_dead_ends":paper_first_search_portfolio_design["summary"].get("semantic_blocker_dead_ends",0),
            "paper_first_search_portfolio_semantic_blocker_added_latest":paper_first_search_portfolio_design["summary"].get("semantic_blocker_added_from_latest_run",0),
            "paper_first_search_portfolio_semantic_blocker_inherited":paper_first_search_portfolio_design["summary"].get("semantic_blocker_inherited",0),
            "paper_first_search_portfolio_near_miss_dead_ends":paper_first_search_portfolio_design["summary"].get("near_miss_preflight_dead_ends",0),
            "paper_first_search_portfolio_near_miss_support_holds":paper_first_search_portfolio_design["summary"].get("near_miss_support_holds",0),
            "paper_first_search_portfolio_near_miss_terminal_support_holds":paper_first_search_portfolio_design["summary"].get("near_miss_terminal_support_holds",0),
            "paper_first_search_portfolio_near_miss_current_primary_stops":paper_first_search_portfolio_design["summary"].get("near_miss_current_primary_stops",0),
            "paper_first_search_portfolio_near_miss_mature_theory_stops":paper_first_search_portfolio_design["summary"].get("near_miss_mature_theory_stops",0),
            "paper_first_search_portfolio_memory_last_ingested_run_id":(paper_first_search_portfolio_design.get("shadow_memory_maintenance") or {}).get("last_ingested_run_id",""),
            "paper_first_support_release_watch_status":paper_first_support_release_watch.get("status","NOT_RUN"),
            "paper_first_support_release_holds":int((paper_first_support_release_watch.get("summary") or {}).get("support_holds") or 0),
            "paper_first_support_release_targets":int((paper_first_support_release_watch.get("summary") or {}).get("explicit_release_targets") or 0),
            "paper_first_support_release_no_endpoint":int((paper_first_support_release_watch.get("summary") or {}).get("no_explicit_endpoint") or 0),
            "paper_first_support_release_recheck_required":int((paper_first_support_release_watch.get("summary") or {}).get("recheck_required") or 0),
            "paper_first_support_release_support_qualified":int((paper_first_support_release_watch.get("summary") or {}).get("support_qualified") or 0),
            "paper_first_support_release_generator_reopen":int((paper_first_support_release_watch.get("summary") or {}).get("generator_reopen_authorized") or 0),
            "paper_first_support_release_problem_gate":int((paper_first_support_release_watch.get("summary") or {}).get("problem_gate_authorized") or 0),
            "paper_first_support_asset_recheck_status":paper_first_support_asset_recheck.get("status","NOT_RUN"),
            "paper_first_support_asset_recheck_queued":int((paper_first_support_asset_recheck.get("summary") or {}).get("queued") or 0),
            "paper_first_support_asset_recheck_new_triggers":int((paper_first_support_asset_recheck.get("summary") or {}).get("new_triggers") or 0),
            "paper_first_support_asset_recheck_carried_forward":int((paper_first_support_asset_recheck.get("summary") or {}).get("carried_forward") or 0),
            "paper_first_support_asset_recheck_resolved":int((paper_first_support_asset_recheck.get("summary") or {}).get("resolved") or 0),
            "paper_first_support_asset_recheck_resolution_still_unavailable":int((paper_first_support_asset_recheck.get("summary") or {}).get("resolution_still_unavailable") or 0),
            "paper_first_support_asset_recheck_resolution_irrelevant_release":int((paper_first_support_asset_recheck.get("summary") or {}).get("resolution_irrelevant_release") or 0),
            "paper_first_support_asset_handoff_status":paper_first_support_asset_recheck_handoff.get("status","NOT_RUN"),
            "paper_first_support_asset_handoff_ready":int((paper_first_support_asset_recheck_handoff.get("summary") or {}).get("support_inventory_recheck_ready") or 0),
            "paper_first_support_asset_handoff_provenance_incomplete":int((paper_first_support_asset_recheck_handoff.get("summary") or {}).get("provenance_incomplete") or 0),
            "paper_first_sp15_identifiability_support_status":paper_first_sp15_support["summary"]["support_status"],
            "paper_first_sp15_identifiability_units":paper_first_sp15_support["summary"]["query_level_identifiability_units"],
            "paper_first_search_portfolio_method_design_authorized":paper_first_search_portfolio_design["summary"]["method_design_authorized"],
            "paper_first_paper_design_backlog_pending":(paper_first_paper_design_backlog.get("summary") or {}).get("pending_human_paper_design",0),
            "paper_first_global_relation_status":paper_first_global_relation_recall.get("status","NOT_RUN"),
            "paper_first_global_relation_reviewed_sources":(paper_first_global_relation_recall.get("summary") or {}).get("reviewed_receipt_sources",0),
            "paper_first_global_relation_pair_coverage":(paper_first_global_relation_recall.get("summary") or {}).get("pair_coverage_fraction",0.0),
            "paper_first_global_relation_blind_spot":bool((paper_first_global_relation_recall.get("summary") or {}).get("relation_blind_spot_detected")),
            "paper_first_global_relation_cache_fraction":(paper_first_global_relation_recall.get("summary") or {}).get("cache_completeness_fraction",0.0),
            "paper_first_global_relation_proposals":(paper_first_global_relation_recall.get("summary") or {}).get("relation_proposals",0),
            "paper_first_global_relation_unseen_proposals":(paper_first_global_relation_recall.get("summary") or {}).get("unseen_relation_proposals",0),
            "paper_first_global_relation_lane_pass":(paper_first_global_relation_recall.get("summary") or {}).get("lane_pass",0),
            "paper_first_global_relation_unseen_lane_pass":(paper_first_global_relation_recall.get("summary") or {}).get("unseen_lane_pass",0),
            "paper_first_global_relation_reducible":(paper_first_global_relation_recall.get("summary") or {}).get("reducible",0),
            "paper_first_global_relation_not_reduced":(paper_first_global_relation_recall.get("summary") or {}).get("not_reduced",0),
            "paper_first_global_relation_focused_reopen":bool((paper_first_global_relation_recall.get("summary") or {}).get("focused_problem_generator_reopen_required")),
            "paper_first_global_relation_freshness_status":paper_first_global_relation_freshness.get("status","NO_COMPLETED_RELATION_SCAN"),
            "paper_first_global_relation_current_sources":(paper_first_global_relation_freshness.get("summary") or {}).get("current_reviewed_sources",0),
            "paper_first_global_relation_last_scanned_sources":(paper_first_global_relation_freshness.get("summary") or {}).get("last_scanned_sources",0),
            "paper_first_global_relation_current_pair_coverage":(paper_first_global_relation_freshness.get("summary") or {}).get("current_pair_coverage_fraction",0.0),
            "paper_first_global_relation_universe_stale":bool((paper_first_global_relation_freshness.get("summary") or {}).get("universe_stale")),
            "paper_first_global_relation_current_not_reduced_unknown":bool((paper_first_global_relation_freshness.get("summary") or {}).get("current_not_reduced_unknown")),
            "paper_first_global_relation_model_scan_deferred":bool((paper_first_global_relation_freshness.get("summary") or {}).get("model_scan_deferred")),
            "paper_first_global_relation_focused_reopen_allowed":bool((paper_first_global_relation_freshness.get("summary") or {}).get("focused_problem_generator_reopen_allowed")),
            "paper_first_relation_delta_status":paper_first_global_relation_delta_preflight.get("status","NOT_RUN"),
            "paper_first_relation_delta_new_sources":(paper_first_global_relation_delta_preflight.get("summary") or {}).get("new_reviewed_sources",0),
            "paper_first_relation_delta_new_empirical":(paper_first_global_relation_delta_preflight.get("summary") or {}).get("new_empirical_sources",0),
            "paper_first_relation_delta_new_assumptions":(paper_first_global_relation_delta_preflight.get("summary") or {}).get("new_assumption_sources",0),
            "paper_first_relation_delta_new_failures":(paper_first_global_relation_delta_preflight.get("summary") or {}).get("new_failure_sources",0),
            "paper_first_relation_delta_new_boundaries":(paper_first_global_relation_delta_preflight.get("summary") or {}).get("new_boundary_sources",0),
            "paper_first_relation_delta_model_scan_authorized":bool((paper_first_global_relation_delta_preflight.get("summary") or {}).get("model_scan_authorized")),
            "paper_first_relation_delta_focused_reopen_authorized":bool((paper_first_global_relation_delta_preflight.get("summary") or {}).get("focused_generator_reopen_authorized")),
            "paper_first_relation_scan_admission_status":paper_first_global_relation_scan_admission.get("status","HOLD_MANUAL_RELATION_SCAN"),
            "paper_first_relation_scan_admission_checks":(paper_first_global_relation_scan_admission.get("summary") or {}).get("checks",0),
            "paper_first_relation_scan_admission_passed":(paper_first_global_relation_scan_admission.get("summary") or {}).get("passed",0),
            "paper_first_relation_scan_admission_failed":(paper_first_global_relation_scan_admission.get("summary") or {}).get("failed",0),
            "paper_first_relation_scan_manual_eligible":bool((paper_first_global_relation_scan_admission.get("summary") or {}).get("manual_scan_eligible")),
            "paper_first_relation_scan_automatic_authorized":bool((paper_first_global_relation_scan_admission.get("summary") or {}).get("automatic_model_scan_authorized")),
            "paper_first_shadow_search_admission_status":paper_first_shadow_search_admission.get("status","HOLD_CANONICAL_DISCOVERY_TRANSACTION_OPEN"),
            "paper_first_shadow_search_same_source_transaction":bool((paper_first_shadow_search_admission.get("summary") or {}).get("same_source_transaction")),
            "paper_first_shadow_search_qualification_allowed":bool((paper_first_shadow_search_admission.get("summary") or {}).get("qualification_allowed")),
            "paper_first_shadow_search_automatic_provider_calls":int((paper_first_shadow_search_admission.get("summary") or {}).get("automatic_provider_calls_authorized") or 0),
            "paper_first_shadow_continuation_status":paper_first_shadow_continuation_frontier.get("status","HOLD_SHADOW_CONTINUATION_STATE_INCOMPLETE"),
            "paper_first_shadow_continuation_next_action":paper_first_shadow_continuation_frontier.get("next_control_action","repair-shadow-continuation-state"),
            "paper_first_shadow_continuation_active_actions":int((paper_first_shadow_continuation_frontier.get("summary") or {}).get("active_control_actions") or 0),
            "paper_first_shadow_continuation_external_wait":int((paper_first_shadow_continuation_frontier.get("summary") or {}).get("external_wait") or 0),
            "paper_first_discovery_frontier_status":paper_first_discovery_frontier.get("status","WAIT_EXTERNAL_EVIDENCE_TRIGGERS"),
            "paper_first_discovery_frontier_open_internal":int((paper_first_discovery_frontier.get("summary") or {}).get("open_internal_frontiers") or 0),
            "paper_first_discovery_frontier_external_triggers":int((paper_first_discovery_frontier.get("summary") or {}).get("external_triggers") or 0),
            "paper_first_discovery_frontier_model_calls":int((paper_first_discovery_frontier.get("summary") or {}).get("automatic_model_calls_authorized") or 0),
            "paper_first_discovery_frontier_evidence_open":int((paper_first_discovery_frontier.get("summary") or {}).get("evidence_internal_open") or 0),
            "paper_first_fresh_phenomenon_status":paper_first_fresh_phenomenon_portfolio.get("status","NO_ACTIVE_F0"),
            "paper_first_fresh_phenomenon_candidates":int((paper_first_fresh_phenomenon_portfolio.get("summary") or {}).get("candidates") or 0),
            "paper_first_fresh_phenomenon_active_f0":int((paper_first_fresh_phenomenon_portfolio.get("summary") or {}).get("active_f0") or 0),
            "paper_first_fresh_phenomenon_design_ready_f0":int((paper_first_fresh_phenomenon_portfolio.get("summary") or {}).get("design_ready_f0") or 0),
            "paper_first_fresh_phenomenon_support_holds":int((paper_first_fresh_phenomenon_portfolio.get("summary") or {}).get("hold_support") or 0),
            "paper_first_fresh_phenomenon_execution_holds":int((paper_first_fresh_phenomenon_portfolio.get("summary") or {}).get("hold_execution") or 0),
            "paper_first_fresh_phenomenon_ready_problem_review":int((paper_first_fresh_phenomenon_portfolio.get("summary") or {}).get("ready_for_problem_review") or 0),
            "paper_first_fresh_phenomenon_archived":int((paper_first_fresh_phenomenon_portfolio.get("summary") or {}).get("archived") or 0),
            "paper_first_evidence_migration_status":paper_first_evidence_migration.get("status","NOT_RUN"),
            "asset_first_stri_status":asset_first_stri_paper_ready.get("status","HOLD_ASSET_FIRST_PAPER_NOT_READY"),
            "asset_first_stri_paper_ready":int((asset_first_stri_paper_ready.get("summary") or {}).get("paper_ready") or 0),
            "asset_first_stri_claims_supported":int((asset_first_stri_paper_ready.get("summary") or {}).get("claims_supported") or 0),
            "asset_first_stri_claims_total":int((asset_first_stri_paper_ready.get("summary") or {}).get("claims_total") or 0),
            "asset_first_stri_qa_checks_passed":int((asset_first_stri_paper_ready.get("summary") or {}).get("qa_checks_passed") or 0),
            "asset_first_stri_qa_checks_total":int((asset_first_stri_paper_ready.get("summary") or {}).get("qa_checks_total") or 0),
            "asset_first_stri_submission_status":asset_first_stri_paper_ready.get("submission_status","NOT_READY"),
            "asset_first_stri_official_qa_checks_passed":int((asset_first_stri_paper_ready.get("summary") or {}).get("official_qa_checks_passed") or 0),
            "asset_first_stri_official_qa_checks_total":int((asset_first_stri_paper_ready.get("summary") or {}).get("official_qa_checks_total") or 0),
            "asset_first_stri_main_text_pages":int((asset_first_stri_paper_ready.get("summary") or {}).get("main_text_pages") or 0),
            "asset_first_stri_main_text_page_limit":int((asset_first_stri_paper_ready.get("summary") or {}).get("main_text_page_limit") or 0),
            "asset_first_stri_supplement_ready":int((asset_first_stri_paper_ready.get("summary") or {}).get("supplement_ready") or 0),
            "asset_first_stri_human_signoff_pending":int((asset_first_stri_paper_ready.get("summary") or {}).get("human_signoff_pending") or 0),
            "asset_first_stri_paper_quality_v2_passed":int((asset_first_stri_paper_ready.get("summary") or {}).get("paper_quality_v2_passed") or 0),
            "asset_first_stri_paper_quality_source_binding":int((asset_first_stri_paper_ready.get("summary") or {}).get("paper_quality_source_binding") or 0),
            "asset_first_stri_paper_quality_content_addressed_completion":int((asset_first_stri_paper_ready.get("summary") or {}).get("paper_quality_content_addressed_completion") or 0),
            "asset_first_stri_paper_quality_content_addressed_files":int((asset_first_stri_paper_ready.get("summary") or {}).get("paper_quality_content_addressed_files") or 0),
            "asset_first_stri_paper_quality_evidence_debt":int((asset_first_stri_paper_ready.get("summary") or {}).get("paper_quality_evidence_debt") or 0),
            "asset_first_stri_main_visualizations":int((asset_first_stri_paper_ready.get("summary") or {}).get("paper_quality_main_visualizations") or 0),
            "asset_first_stri_canonical_problem_gate_added":int((asset_first_stri_paper_ready.get("summary") or {}).get("canonical_problem_gate_pass_added") or 0),
            "paper_first_evidence_migration_pending":int((paper_first_evidence_migration.get("summary") or {}).get("current_reduction_pending") or 0),
            "paper_first_evidence_migration_design_pending":int((paper_first_evidence_migration.get("summary") or {}).get("evidence_design_pending") or 0),
            "paper_first_evidence_migration_recompile_pending":int((paper_first_evidence_migration.get("summary") or {}).get("evidence_operationalization_recompile_pending") or 0),
            "paper_first_evidence_migration_recompiled":int((paper_first_evidence_migration.get("summary") or {}).get("evidence_operationalization_recompiled") or 0),
            "paper_first_evidence_migration_review_pending":int((paper_first_evidence_migration.get("summary") or {}).get("evidence_review_pending") or 0),
            "paper_first_evidence_migration_substrate_preflight_pending":int((paper_first_evidence_migration.get("summary") or {}).get("evidence_substrate_preflight_pending") or 0),
            "paper_first_evidence_migration_harness_implementation_pending":int((paper_first_evidence_migration.get("summary") or {}).get("evidence_harness_implementation_pending") or 0),
            "paper_first_evidence_migration_execution_ready":int((paper_first_evidence_migration.get("summary") or {}).get("evidence_execution_ready") or 0),
            "paper_first_shadow_latest_run_id":paper_first_problem_search_portfolio.get("latest_run_id",""),
            "paper_first_shadow_latest_stage_runner_schema":paper_first_shadow_latest.get("stage_runner_required_schema",""),
            "paper_first_shadow_latest_control_snapshot_sha256":paper_first_shadow_latest.get("control_snapshot_sha256",""),
            "paper_first_shadow_latest_expansion_successful_shards":paper_first_shadow_latest_summary.get("expansion_successful_shards",0),
            "paper_first_shadow_latest_expansion_execution_failures":paper_first_shadow_latest_summary.get("expansion_execution_failures",0),
            "paper_first_shadow_latest_expansion_parse_failures":paper_first_shadow_latest_summary.get("expansion_parse_failures",0),
            "paper_first_shadow_latest_expansion_provider_failures":paper_first_shadow_latest_summary.get("expansion_provider_failures",0),
            "paper_first_shadow_latest_raw":paper_first_shadow_latest_summary.get("raw_seeds",0),
            "paper_first_shadow_latest_search_closure_blocks":paper_first_shadow_latest_summary.get("search_closure_blocks",paper_first_shadow_latest_summary.get("semantic_dead_end_blocks",0)),
            "paper_first_shadow_latest_unique":paper_first_shadow_latest_summary.get("semantic_unique",0),
            "paper_first_shadow_latest_evolved":paper_first_shadow_latest_summary.get("evolved_branches",0),
            "paper_first_shadow_latest_evolution_g1_requested":paper_first_shadow_latest_summary.get("evolution_g1_requested",0),
            "paper_first_shadow_latest_evolution_g1_valid":paper_first_shadow_latest_summary.get("evolution_g1_valid",0),
            "paper_first_shadow_latest_evolution_g2_requested":paper_first_shadow_latest_summary.get("evolution_g2_requested",0),
            "paper_first_shadow_latest_evolution_g2_valid":paper_first_shadow_latest_summary.get("evolution_g2_valid",0),
            "paper_first_shadow_latest_formulation_requested_shards":paper_first_shadow_latest_summary.get("formulation_requested_shards",0),
            "paper_first_shadow_latest_formulation_successful_shards":paper_first_shadow_latest_summary.get("formulation_successful_shards",0),
            "paper_first_shadow_latest_formulation_provider_failures":paper_first_shadow_latest_summary.get("formulation_provider_failures",0),
            "paper_first_shadow_latest_formulation_requested_branches":paper_first_shadow_latest_summary.get("formulation_requested_branches",0),
            "paper_first_shadow_latest_formulation_successful_branches":paper_first_shadow_latest_summary.get("formulation_successful_branches",0),
            "paper_first_shadow_latest_formulation_execution_censored_branches":paper_first_shadow_latest_summary.get("formulation_execution_censored_branches",0),
            "paper_first_shadow_latest_formulated":paper_first_shadow_latest_summary.get("formulated_candidates",0),
            "paper_first_shadow_latest_formulation_reduction_pending":paper_first_shadow_latest_summary.get("formulation_reduction_pending",0),
            "paper_first_shadow_latest_machine_reviewable":paper_first_shadow_latest_summary.get("machine_reviewable",0),
            "paper_first_shadow_latest_machine_reduction_pending":paper_first_shadow_latest_summary.get("machine_reduction_pending",0),
            "paper_first_shadow_latest_problem_falsifier_eligible":paper_first_shadow_latest_summary.get("problem_falsifier_eligible",0),
            "paper_first_shadow_latest_problem_falsifier_inventory_requested":paper_first_shadow_latest_summary.get("problem_falsifier_inventory_requested",0),
            "paper_first_shadow_latest_problem_falsifier_support_qualified":paper_first_shadow_latest_summary.get("problem_falsifier_support_qualified",0),
            "paper_first_shadow_latest_provisional_problem_candidates":paper_first_shadow_latest_summary.get("provisional_problem_candidates",0),
            "paper_first_shadow_latest_evidence_design_selected":paper_first_shadow_latest_summary.get("evidence_design_selected",0),
            "paper_first_shadow_latest_evidence_design_pending":paper_first_shadow_latest_summary.get("evidence_design_pending",0),
            "paper_first_shadow_latest_evidence_operationalization_recompile_pending":paper_first_shadow_latest_summary.get("evidence_operationalization_recompile_pending",0),
            "paper_first_shadow_latest_evidence_operationalization_recompiled":paper_first_shadow_latest_summary.get("evidence_operationalization_recompiled",0),
            "paper_first_shadow_latest_evidence_wait_primary_asset":paper_first_shadow_latest_summary.get("evidence_wait_primary_asset",0),
            "paper_first_shadow_latest_evidence_review_pending":paper_first_shadow_latest_summary.get("evidence_review_pending",0),
            "paper_first_shadow_latest_evidence_review_clear":paper_first_shadow_latest_summary.get("evidence_review_clear",0),
            "paper_first_shadow_latest_evidence_review_revise":paper_first_shadow_latest_summary.get("evidence_review_revise",0),
            "paper_first_shadow_latest_evidence_review_blocked":paper_first_shadow_latest_summary.get("evidence_review_blocked",0),
            "paper_first_shadow_latest_evidence_substrate_preflight_pending":paper_first_shadow_latest_summary.get("evidence_substrate_preflight_pending",0),
            "paper_first_shadow_latest_evidence_substrate_ready":paper_first_shadow_latest_summary.get("evidence_substrate_ready",0),
            "paper_first_shadow_latest_evidence_harness_implementation_pending":paper_first_shadow_latest_summary.get("evidence_harness_implementation_pending",0),
            "paper_first_shadow_latest_evidence_substrate_hold":paper_first_shadow_latest_summary.get("evidence_substrate_hold",0),
            "paper_first_shadow_latest_evidence_execution_ready":paper_first_shadow_latest_summary.get("evidence_execution_ready",0),
            "paper_first_shadow_latest_evidence_execution_completed":paper_first_shadow_latest_summary.get("evidence_execution_completed",0),
            "paper_first_shadow_latest_evidence_reduction_supported":paper_first_shadow_latest_summary.get("evidence_reduction_supported",0),
            "paper_first_shadow_latest_evidence_residual_survives":paper_first_shadow_latest_summary.get("evidence_residual_survives",0),
            "paper_first_shadow_latest_evidence_inconclusive":paper_first_shadow_latest_summary.get("evidence_inconclusive",0),
            "paper_first_shadow_latest_evidence_branch_repair_ready":paper_first_shadow_latest_summary.get("evidence_branch_repair_ready",0),
            "paper_first_shadow_latest_problem_falsifier_hold":paper_first_shadow_latest_summary.get("problem_falsifier_hold_support_unavailable",0),
            "paper_first_shadow_latest_problem_falsifier_executed":paper_first_shadow_latest_summary.get("problem_falsifier_executed",0),
            "paper_first_shadow_latest_semantic_clear":paper_first_shadow_latest_summary.get("semantic_clear",0),
            "paper_first_shadow_latest_current_source_blocked":paper_first_shadow_latest_summary.get("current_source_blocked",0),
            "paper_first_shadow_latest_terminal_survivors":paper_first_shadow_latest_summary.get("terminal_shadow_survivors",0),
            "paper_first_shadow_latest_live_paper_design_eligible":paper_first_shadow_latest_summary.get("live_paper_design_eligible",0),
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
            "scientific_research_graph_nodes":scientific_research_graph["summary"]["nodes"],
            "scientific_research_graph_edges":scientific_research_graph["summary"]["edges"],
            "research_memory_entries":research_memory_wiki["summary"]["entries"],
            "research_memory_lint_warnings":research_memory_wiki["lint"]["summary"]["warnings"],
            "failure_assets":failure_asset_library["summary"]["assets"],
            "value_scheduler_candidates":experiment_value_scheduler["summary"]["candidates"],
            "research_replay_passed":research_system_replay["summary"]["passed"],
            "external_systems_reviewed":external_system_learning["summary"]["systems_reviewed"],
            "candidate_portfolio_visible":research_candidate_portfolio["summary"]["visible_candidates"],
            "candidate_portfolio_active":research_candidate_portfolio["summary"]["active_problem_lines"],
            "candidate_portfolio_search_holds":research_candidate_portfolio["summary"]["search_holds"],
            "search_funnel_bottleneck":search_funnel_telemetry["bottleneck"]["key"],
            "research_harness_assurance_passed":research_harness_assurance["summary"]["passed"],
            "research_harness_assurance_checks":research_harness_assurance["summary"]["checks"],
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
            "p0_failure_diagnosis_required":p0_decision_ledger["summary"]["failure_diagnosis_required"],
            "p0_failure_diagnosis_complete":p0_decision_ledger["summary"]["failure_diagnosis_complete"],
            "p0_failure_diagnosis_incomplete":p0_decision_ledger["summary"]["failure_diagnosis_incomplete"],
            "p0_failure_layer_counts":p0_decision_ledger["summary"]["failure_layer_counts"],
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
        "paper_visual_evidence":paper_visual_evidence,
        "paper_first_design_adjudication":paper_first_design,
        "paper_first_pf1_problem_adjudication":paper_first_pf1_problem,
        "paper_first_pf2_method_adjudication":paper_first_pf2_method,
        "paper_first_pf357_problem_adjudication":paper_first_pf357,
        "paper_first_fresh_saturation":paper_first_fresh_saturation,
        "paper_first_primary_evidence":paper_first_primary_evidence,
        "paper_first_scientific_object_retrieval_audit":paper_first_scientific_object_retrieval,
        "paper_first_scientific_object_candidate_evidence":paper_first_scientific_object_candidate_evidence,
        "paper_first_problem_discovery_contract":paper_first_problem_discovery_contract,
        "paper_first_problem_generator":paper_first_problem_generator,
        "paper_first_pre_f0_queue":paper_first_pre_f0_queue,
        "paper_first_pre_f0_problem_falsifier_preflight":paper_first_pre_f0_problem_falsifier_preflight,
        "paper_first_problem_gate_queue":paper_first_problem_gate_queue,
        "paper_first_search_portfolio_design_adjudication":paper_first_search_portfolio_design,
        "paper_first_support_release_watch":paper_first_support_release_watch,
        "paper_first_support_asset_recheck_queue":paper_first_support_asset_recheck,
        "paper_first_support_asset_recheck_handoff":paper_first_support_asset_recheck_handoff,
        "paper_first_discovery_frontier":paper_first_discovery_frontier,
        "paper_first_fresh_phenomenon_portfolio":paper_first_fresh_phenomenon_portfolio,
        "paper_first_evidence_migration":paper_first_evidence_migration,
        "asset_first_stri_paper_ready":asset_first_stri_paper_ready,
        "paper_first_sp15_identifiability_support":paper_first_sp15_support,
        "paper_first_paper_design_backlog":paper_first_paper_design_backlog,
        "paper_first_global_relation_recall":paper_first_global_relation_recall,
        "paper_first_global_relation_freshness":paper_first_global_relation_freshness,
        "paper_first_global_relation_delta_preflight":paper_first_global_relation_delta_preflight,
        "paper_first_global_relation_scan_admission":paper_first_global_relation_scan_admission,
        "paper_first_shadow_search_admission":paper_first_shadow_search_admission,
        "paper_first_shadow_continuation_frontier":paper_first_shadow_continuation_frontier,
        "paper_first_problem_search_portfolio":paper_first_problem_search_portfolio,
        "paper_first_post_c2":paper_first_post_c2,
        "paper_first_premature_method_diagnostics":paper_first_premature_method_diagnostics,
        "pilot_registry":pilot_registry,
        "experiment_iteration":experiment_iteration,
        "principle_layer":principle_layer,
        "scientific_meta_trace":scientific_meta_trace,
        "scientific_research_graph":scientific_research_graph,
        "research_memory_wiki":research_memory_wiki,
        "failure_asset_library":failure_asset_library,
        "experiment_value_scheduler":experiment_value_scheduler,
        "research_system_replay":research_system_replay,
        "external_system_learning":external_system_learning,
        "research_candidate_portfolio":research_candidate_portfolio,
        "search_funnel_telemetry":search_funnel_telemetry,
        "research_harness_assurance":research_harness_assurance,
        "paper_acceptance":paper_acceptance,
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
    state["summary"]["architecture_reader_chapters"] = state["system_architecture"]["summary"]["reader_chapters"]
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
    discovery_policy = (state.get("paper_first_problem_discovery_contract") or {}).get("policy") or {}
    generator_policy = (state.get("paper_first_problem_generator") or {}).get("policy") or {}
    live_contract_boundary_ok = bool(
        # Historical published Search Portfolio artifacts remain shadow-only.
        discovery_policy.get("search_portfolio_is_shadow_only") is True
        and discovery_policy.get("search_portfolio_cannot_publish_canonical_generator_or_queue") is True
        # New canonical discovery reuses the portfolio engine only inside one
        # bounded, atomic double-funnel transaction.
        and discovery_policy.get("canonical_double_funnel_required") is True
        and discovery_policy.get("canonical_double_funnel_reuses_portfolio_engine") is True
        and discovery_policy.get("historical_search_portfolio_remains_shadow_only") is True
        and discovery_policy.get("one_content_addressed_pool_allows_at_most_one_live_generator_call") is False
        and discovery_policy.get("one_content_addressed_pool_allows_at_most_one_discovery_transaction") is True
        and discovery_policy.get("bounded_provider_subcalls_inside_discovery_transaction") is True
        and discovery_policy.get("attack_repair_split_before_terminal_review") is True
        and discovery_policy.get("principle_reduction_does_not_auto_close_other_paperability_axes") is True
        and discovery_policy.get("cheap_problem_falsifier_may_precede_exact_reduction") is True
        and discovery_policy.get("pre_f0_evidence_acquisition_has_zero_scientific_authority") is True
        and discovery_policy.get("exact_reduction_required_before_final_problem_gate") is True
        and discovery_policy.get("source_coverage_saturation_reopens_once_on_operator_change") is True
        and discovery_policy.get("single_source_anomaly_first_search_enabled") is True
        and discovery_policy.get("discovery_operator_version") == DISCOVERY_OPERATOR_VERSION
        and tuple(discovery_policy.get("search_portfolio_primitives") or ()) == SEARCH_PORTFOLIO_PRIMITIVES
    )
    generator_operator_version = str(generator_policy.get("discovery_operator_version") or "").strip()
    generator_status = str((state.get("paper_first_problem_generator") or {}).get("status") or "")
    generator_closed_historical_receipt = bool(
        generator_operator_version
        and generator_operator_version != DISCOVERY_OPERATOR_VERSION
        and generator_status in {
            "GENERATED_ZERO_CANDIDATES",
            "GENERATED_PRE_F0_EVIDENCE_ACQUISITION",
            "GENERATED_AWAIT_PROBLEM_GATE",
            "GENERATED_PRE_F0_EVIDENCE_ACQUISITION",
            "SKIPPED_SOURCE_COVERAGE_SATURATED",
            "SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE",
            "SKIPPED_SOURCE_CARRIER_PROBE_PENDING",
            "SKIPPED_INSUFFICIENT_PRIMARY_EVIDENCE",
            "SKIPPED_STALE_PRIMARY_EVIDENCE",
        }
        and generator_policy.get("source_coverage_saturation_reopens_once_on_operator_change") is True
        and ((generator_policy.get("search_portfolio_enabled") is True and generator_policy.get("one_content_addressed_pool_allows_at_most_one_discovery_transaction") is True) or (generator_policy.get("search_portfolio_enabled") is not True and generator_policy.get("one_content_addressed_pool_allows_at_most_one_live_generator_call_per_discovery_operator") is True))
        and generator_policy.get("source_coverage_saturation_operator_upgrade_recompile_is_explicit_exception") is True
    )
    current_generator_double_funnel = bool(
        generator_operator_version == DISCOVERY_OPERATOR_VERSION
        and generator_policy.get("search_portfolio_enabled") is True
        and generator_policy.get("search_portfolio_is_shadow_only") is False
        and generator_policy.get("legacy_published_search_portfolio_remains_shadow_only") is True
        and generator_policy.get("canonical_transaction_forbids_search_portfolio") is False
        and generator_policy.get("one_generator_call_max") is False
        and generator_policy.get("one_semantic_reviewer_call_max") is False
        and generator_policy.get("one_content_addressed_pool_allows_at_most_one_discovery_transaction") is True
        and generator_policy.get("bounded_provider_subcalls_inside_discovery_transaction") is True
        and int(generator_policy.get("portfolio_generator_subcall_budget") or 0) > 0
        and int(generator_policy.get("portfolio_semantic_reviewer_subcall_budget") or 0) > 0
        and generator_policy.get("attack_repair_split_before_formulation") is True
        and generator_policy.get("principle_reduction_does_not_auto_close_other_paperability_axes") is True
        and generator_policy.get("pre_f0_evidence_acquisition_has_zero_scientific_authority") is True
        and generator_policy.get("exact_reduction_required_before_final_problem_gate") is True
    )
    current_generator_legacy = bool(
        generator_operator_version == DISCOVERY_OPERATOR_VERSION
        and generator_policy.get("search_portfolio_enabled") is not True
        and generator_policy.get("one_generator_call_max",True) is True
        and generator_policy.get("one_semantic_reviewer_call_max",True) is True
        and generator_policy.get("one_content_addressed_pool_allows_at_most_one_live_generator_call_per_discovery_operator",True) is True
    )
    generator_operator_contract_ok = bool(
        not generator_operator_version
        or generator_closed_historical_receipt
        or current_generator_double_funnel
        or current_generator_legacy
    )
    live_generator_boundary_ok = bool(
        generator_operator_contract_ok
        and (
            current_generator_double_funnel
            or generator_closed_historical_receipt
            or current_generator_legacy
            or not generator_operator_version
        )
    )
    shadow_portfolio = state.get("paper_first_problem_search_portfolio") or {}
    shadow_latest = shadow_portfolio.get("latest_run") or {}
    shadow_latest_policy = shadow_latest.get("policy") or {}
    shadow_latest_summary = shadow_latest.get("summary") or {}
    shadow_latest_authority = shadow_latest.get("authority") or {}
    shadow_latest_ok = not shadow_latest or bool(
        shadow_latest.get("scientific_authority") is False
        and shadow_latest_policy.get("shadow_only") is True
        and shadow_latest_policy.get("canonical_primary_generator_queue_untouched") is True
        and shadow_latest_policy.get("live_source_coverage_effect") is False
        and shadow_latest_policy.get("current_source_web_receipt_required_after_semantic_clear") is True
        and shadow_latest_policy.get("missing_or_failed_current_source_reviewer_is_not_pass") is True
        and int(shadow_latest_summary.get("live_paper_design_eligible") or 0) == 0
        and int(shadow_latest_summary.get("terminal_shadow_survivors") or 0) == int(shadow_latest_summary.get("current_source_clear") or 0)
        and (shadow_latest.get("status") != "SHADOW_TERMINAL_COMPLETE" or int(shadow_latest_summary.get("current_source_missing") or 0) == 0)
        and all(shadow_latest_authority.get(key) is False for key in ("live_problem_gate","paper_design","method","experiment","p0","gpu"))
    )
    primary_state=state.get("paper_first_primary_evidence") or {};primary_policy=primary_state.get("policy") or {};primary_summary=primary_state.get("summary") or {};primary_schema=str(primary_state.get("schema_version") or "0")
    carrier_probe=primary_state.get("carrier_probe") or {};carrier_receipts=[row for row in carrier_probe.get("portable_receipts") or [] if isinstance(row,dict)]
    primary_carrier_boundary_ok=True
    if primary_schema >= "1.1":
        allowed_objects=set(str(value) for value in primary_policy.get("scientific_object_lanes") or [])
        primary_carrier_boundary_ok=bool(
            primary_policy.get("no_lane_carrier_probe_enabled") is True
            and primary_policy.get("no_lane_carrier_probe_is_existing_object_rescue_only") is True
            and primary_policy.get("no_lane_carrier_probe_cannot_create_new_object") is True
            and primary_policy.get("no_lane_carrier_probe_has_zero_scientific_authority") is True
            and primary_policy.get("no_lane_carrier_probe_failure_prevents_coverage_exhaustion") is True
            and primary_policy.get("carrier_probe_pending_skips_live_generator_call") is True
            and carrier_probe.get("scientific_authority") is False
            and int(carrier_probe.get("pending") or 0)==int(primary_summary.get("carrier_probe_pending") or 0)
            and bool(carrier_probe.get("complete"))==bool(primary_summary.get("carrier_probe_complete"))
            and not (primary_summary.get("source_coverage_exhausted") is True and int(primary_summary.get("carrier_probe_pending") or 0)>0)
            and all(
                row.get("scientific_authority") is False
                and len(str(row.get("primary_sha256") or ""))==64
                and (((str(row.get("probe_outcome") or "")=="SCOPE_EXCLUDED_BY_PRIMARY") and not str(row.get("fulltext_sha256") or "") and not (row.get("live_rescue_eligible_lanes") or [])) or len(str(row.get("fulltext_sha256") or ""))==64)
                and all(str(value) in allowed_objects for value in row.get("live_rescue_eligible_lanes") or [])
                for row in carrier_receipts
            )
        )
    generator_status=str((state.get("paper_first_problem_generator") or {}).get("status") or "");generator_coverage=(state.get("paper_first_problem_generator") or {}).get("source_coverage") or {}
    retrieval_incomplete_boundary_ok=generator_status!="SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE" or bool(
        generator_policy.get("incomplete_retrieval_without_new_lane_source_skips_model_call") is True
        and generator_policy.get("retrieval_incomplete_is_compute_control_not_scientific_negative") is True
        and generator_coverage.get("source_retrieval_complete") is False
        and generator_coverage.get("coverage_exhausted") is not True
        and int(generator_coverage.get("unreviewed_lane_linked_sources") or 0)==0
    )
    carrier_pending_boundary_ok=generator_status!="SKIPPED_SOURCE_CARRIER_PROBE_PENDING" or bool(
        generator_policy.get("carrier_probe_pending_skips_model_call") is True
        and generator_policy.get("carrier_probe_pending_is_compute_control_not_scientific_negative") is True
        and generator_coverage.get("coverage_exhausted") is not True
        and generator_coverage.get("carrier_probe_required") is True
        and int(generator_coverage.get("carrier_probe_pending") or 0)>0
        and generator_coverage.get("carrier_probe_complete") is False
        and int(generator_coverage.get("unreviewed_lane_linked_sources") or 0)==0
    )
    object_retrieval=state.get("paper_first_scientific_object_retrieval_audit") or {};object_retrieval_policy=object_retrieval.get("policy") or {};object_retrieval_summary=object_retrieval.get("summary") or {}
    object_retrieval_boundary_ok=bool(
        object_retrieval.get("scientific_authority") is False
        and object_retrieval_policy.get("shadow_only") is True
        and object_retrieval_policy.get("live_query_set_changed") is False
        and object_retrieval_policy.get("candidate_metadata_does_not_count_as_verified_primary_support") is True
        and object_retrieval_policy.get("incomplete_query_is_not_negative_evidence") is True
        and object_retrieval_policy.get("primary_verification_required_before_lane_preregistration") is True
        and object_retrieval_policy.get("automatic_lane_activation") is False
        and int(object_retrieval_summary.get("activation_authorized") or 0)==0
        and all((row.get("scientific_authority") is False) for row in (object_retrieval.get("results") or {}).values() if isinstance(row,dict))
    )
    candidate_evidence=state.get("paper_first_scientific_object_candidate_evidence") or {};candidate_evidence_policy=candidate_evidence.get("policy") or {};candidate_evidence_summary=candidate_evidence.get("summary") or {}
    candidate_evidence_boundary_ok=bool(
        candidate_evidence.get("scientific_authority") is False
        and candidate_evidence_policy.get("shadow_only") is True
        and candidate_evidence_policy.get("network_fetch_forbidden") is True
        and candidate_evidence_policy.get("source_exposure_effect") is False
        and candidate_evidence_policy.get("live_query_effect") is False
        and candidate_evidence_policy.get("candidate_primary_verification_does_not_activate_lane") is True
        and candidate_evidence_policy.get("support_purity_and_ownership_gates_still_required") is True
        and int(candidate_evidence_summary.get("activation_authorized") or 0)==0
        and all(row.get("scientific_authority") is False for row in (candidate_evidence.get("results") or {}).values() if isinstance(row,dict))
    )
    support_release_watch=state.get("paper_first_support_release_watch") or {};support_release_policy=support_release_watch.get("policy") or {};support_release_summary=support_release_watch.get("summary") or {};support_release_status=str(support_release_watch.get("status") or "NOT_RUN")
    support_primary_refresh_present="primary_declaration_refresh_checked" in support_release_summary
    support_primary_refresh_boundary_ok=bool(
        not support_primary_refresh_present
        or (
            support_release_policy.get("no_endpoint_primary_refresh_is_primary_source_only") is True
            and support_release_policy.get("primary_declaration_refresh_has_zero_source_exposure_effect") is True
            and support_release_policy.get("primary_declaration_refresh_cannot_qualify_support") is True
        )
    )
    support_release_boundary_ok=bool(
        support_release_watch.get("scientific_authority") is False
        and support_release_policy.get("primary_declared_or_support_audited_release_endpoints_only") is True
        and support_release_policy.get("support_audited_pre_f0_repository_targets_allowed") is True
        and support_release_policy.get("pre_f0_release_change_only_holds_included") is True
        and support_release_policy.get("related_work_repository_links_are_not_watch_targets") is True
        and support_release_policy.get("release_surface_change_only_requests_recheck") is True
        and support_release_policy.get("release_watch_cannot_mark_support_qualified") is True
        and support_release_policy.get("release_watch_cannot_reopen_generator_or_problem_gate") is True
        and support_release_policy.get("release_watch_has_zero_source_exposure_effect") is True
        and support_release_policy.get("network_checks_are_cooldown_bounded") is True
        and support_primary_refresh_boundary_ok
        and support_release_policy.get("public_summary_excludes_urls_refs_required_units_and_private_paths") is True
        and int(support_release_summary.get("support_qualified") or 0)==0
        and int(support_release_summary.get("generator_reopen_authorized") or 0)==0
        and int(support_release_summary.get("problem_gate_authorized") or 0)==0
        and support_release_status in {"NOT_RUN","SUPPORT_RELEASE_WATCH_COMPLETE","SUPPORT_RELEASE_WATCH_PARTIAL","STATE_UNREADABLE","STATE_INVALID"}
    )
    support_asset_recheck=state.get("paper_first_support_asset_recheck_queue") or {};support_asset_policy=support_asset_recheck.get("policy") or {};support_asset_summary=support_asset_recheck.get("summary") or {};support_asset_status=str(support_asset_recheck.get("status") or "NOT_RUN")
    support_asset_resolution_present=("resolved" in support_asset_summary) or support_asset_policy.get("asset_resolution_must_bind_latest_trigger_digest") is True
    support_asset_resolution_boundary_ok=(not support_asset_resolution_present) or (
        support_asset_policy.get("asset_resolution_must_bind_latest_trigger_digest") is True
        and support_asset_policy.get("asset_resolution_cannot_mark_support_qualified_or_reopen") is True
        and support_asset_policy.get("support_inventory_recheck_remains_queue_handoff_not_resolution") is True
    )
    support_asset_recheck_boundary_ok=bool(
        support_asset_recheck.get("scientific_authority") is False
        and support_asset_policy.get("release_change_only_creates_asset_recheck_task") is True
        and support_asset_policy.get("queue_is_durable_across_release_watch_cooldown") is True
        and support_asset_policy.get("queue_only_tracks_current_support_holds") is True
        and support_asset_policy.get("queue_cannot_mark_support_qualified") is True
        and support_asset_policy.get("queue_cannot_reopen_generator_or_problem_gate") is True
        and support_asset_policy.get("queue_cannot_authorize_method_experiment_p0_gpu") is True
        and support_asset_policy.get("explicit_asset_resolution_required_to_clear_entry") is True
        and support_asset_resolution_boundary_ok
        and support_asset_policy.get("automatic_provider_calls_authorized") is False
        and support_asset_policy.get("public_summary_excludes_entries_refs_urls_required_units_and_private_paths") is True
        and support_asset_status in {"NOT_RUN","SUPPORT_ASSET_RECHECK_QUEUE_EMPTY","SUPPORT_ASSET_RECHECK_QUEUE_READY","STATE_UNREADABLE","STATE_INVALID"}
        and all(int(support_asset_summary.get(key) or 0)==0 for key in ("support_qualified","generator_reopen_authorized","problem_gate_authorized","method_authorized","experiment_authorized","p0_authorized","gpu_authorized"))
    )
    support_asset_handoff=state.get("paper_first_support_asset_recheck_handoff") or {};support_handoff_policy=support_asset_handoff.get("policy") or {};support_handoff_summary=support_asset_handoff.get("summary") or {};support_handoff_status=str(support_asset_handoff.get("status") or "NOT_RUN")
    support_asset_handoff_boundary_ok=bool(
        support_asset_handoff.get("scientific_authority") is False
        and support_handoff_policy.get("handoff_reuses_existing_problem_falsifier_support_inventory") is True
        and support_handoff_policy.get("asset_recheck_cannot_define_a_parallel_support_gate") is True
        and support_handoff_policy.get("release_change_is_not_support_qualification") is True
        and support_handoff_policy.get("support_inventory_receipt_required_before_any_support_decision") is True
        and support_handoff_policy.get("problem_falsifier_preflight_remains_support_authority_boundary") is True
        and support_handoff_policy.get("handoff_cannot_execute_falsifier_automatically") is True
        and support_handoff_policy.get("handoff_cannot_reopen_generator_or_problem_gate") is True
        and support_handoff_policy.get("handoff_cannot_authorize_method_experiment_p0_gpu") is True
        and support_handoff_policy.get("automatic_provider_calls_authorized") is False
        and support_handoff_policy.get("public_summary_excludes_entries_refs_urls_required_units_and_private_paths") is True
        and support_handoff_status in {"NOT_RUN","SUPPORT_ASSET_RECHECK_HANDOFF_EMPTY","SUPPORT_ASSET_RECHECK_HANDOFF_READY","SUPPORT_ASSET_RECHECK_HANDOFF_HOLD_PROVENANCE","STATE_UNREADABLE","STATE_INVALID"}
        and int(support_handoff_summary.get("queued_asset_rechecks") or 0)==int(support_asset_summary.get("queued") or 0)
        and int(support_handoff_summary.get("support_inventory_recheck_ready") or 0)+int(support_handoff_summary.get("provenance_incomplete") or 0)==int(support_handoff_summary.get("queued_asset_rechecks") or 0)
        and all(int(support_handoff_summary.get(key) or 0)==0 for key in ("automatic_execution_authorized","provider_calls_authorized","support_qualified","falsifier_execution_authorized","generator_reopen_authorized","problem_gate_authorized","method_authorized","experiment_authorized","p0_authorized","gpu_authorized"))
    )
    shadow_continuation=state.get("paper_first_shadow_continuation_frontier") or {}
    shadow_continuation_boundary_ok=bool(shadow_continuation and not validate_shadow_continuation_frontier(shadow_continuation))
    relation_freshness=state.get("paper_first_global_relation_freshness") or {};relation_freshness_policy=relation_freshness.get("policy") or {};relation_freshness_summary=relation_freshness.get("summary") or {}
    relation_freshness_boundary_ok=bool(
        relation_freshness.get("scientific_authority") is False
        and relation_freshness_policy.get("deterministic_digest_comparison_only") is True
        and relation_freshness_policy.get("stale_scan_is_historical_not_current_negative_evidence") is True
        and relation_freshness_policy.get("stale_scan_cannot_reopen_focused_generator") is True
        and relation_freshness_policy.get("model_scan_deferred_is_not_relation_exhaustion") is True
        and (not bool(relation_freshness_summary.get("universe_stale")) or (bool(relation_freshness_summary.get("current_not_reduced_unknown")) and not bool(relation_freshness_summary.get("focused_problem_generator_reopen_allowed"))))
    )
    relation_delta=state.get("paper_first_global_relation_delta_preflight") or {};relation_delta_policy=relation_delta.get("policy") or {};relation_delta_summary=relation_delta.get("summary") or {};relation_delta_status=str(relation_delta.get("status") or "NOT_RUN")
    relation_delta_boundary_ok=bool(
        relation_delta.get("scientific_authority") is False
        and (
            relation_delta_status=="NOT_RUN"
            or (
                relation_delta_policy.get("deterministic_typed_evidence_delta_only") is True
                and relation_delta_policy.get("pair_slots_are_not_lane_valid_pairs") is True
                and relation_delta_policy.get("cannot_reopen_generator") is True
                and relation_delta_policy.get("cannot_authorize_relation_model_scan") is True
                and relation_delta_policy.get("cannot_authorize_problem_gate") is True
                and relation_delta_summary.get("model_scan_authorized") is not True
                and relation_delta_summary.get("focused_generator_reopen_authorized") is not True
            )
        )
    )
    relation_admission=state.get("paper_first_global_relation_scan_admission") or {};relation_admission_policy=relation_admission.get("policy") or {};relation_admission_summary=relation_admission.get("summary") or {}
    relation_admission_boundary_ok=bool(
        relation_admission.get("scientific_authority") is False
        and relation_admission_policy.get("automatic_model_scan_authority") is False
        and relation_admission_policy.get("manual_execution_requires_explicit_operator_flag") is True
        and relation_admission_policy.get("manual_eligibility_is_not_scientific_authority") is True
        and relation_admission_policy.get("relation_scan_cannot_authorize_problem_gate") is True
        and relation_admission_policy.get("relation_scan_cannot_authorize_method_experiment_p0_gpu") is True
        and relation_admission_policy.get("preconditions_are_deterministic_search_control_only") is True
        and relation_admission_summary.get("automatic_model_scan_authorized") is False
        and ((relation_admission.get("status")=="ELIGIBLE_FOR_EXPLICIT_MANUAL_RELATION_SCAN") == (relation_admission_summary.get("manual_scan_eligible") is True))
    )
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
        {"key":"paper-first-carrier-probe-boundary", "pass":primary_carrier_boundary_ok, "detail":{"schema_version":primary_schema,"required":carrier_probe.get("required",False),"attempted":carrier_probe.get("attempted",0),"rescued":carrier_probe.get("rescued",0),"pending":carrier_probe.get("pending",0),"complete":carrier_probe.get("complete",True)}},
        {"key":"paper-first-primary-evidence", "pass":state["paper_first_primary_evidence"].get("status") in {"NOT_RUN","READY","INSUFFICIENT_PRIMARY_EVIDENCE","STALE_CORPUS_BLOCKED","NO_CORPUS","STATE_UNREADABLE"} and (state["paper_first_primary_evidence"].get("policy") or {}).get("candidate_generation_authority") is False and (state["paper_first_primary_evidence"].get("policy") or {}).get("method_authority") is False and (state["paper_first_primary_evidence"].get("policy") or {}).get("experiment_authority") is False and (state["paper_first_primary_evidence"].get("status") != "READY" or ((state["paper_first_primary_evidence"].get("policy") or {}).get("primary_publication_age_is_bounded") is True and float((state["paper_first_primary_evidence"].get("policy") or {}).get("maximum_publication_age_days") or 9999) <= 60.0 and (state["paper_first_primary_evidence"].get("policy") or {}).get("fresh_s2_is_augmented_by_preregistered_arxiv_lanes") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("arxiv_augmentation_failure_does_not_invalidate_fresh_corpus") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("typed_evidence_candidates_are_not_ground_truth") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("typed_evidence_is_deterministic_and_bounded") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("source_coverage_scheduler_is_discovery_only") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("source_review_exposure_has_zero_scientific_authority") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("portable_source_review_receipts_have_zero_scientific_authority") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("private_saturation_ledger_runs_exported_as_zero_authority_portable_receipts") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("source_exposure_cannot_skip_generation_or_problem_gate") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("source_exposure_does_not_relax_relevance_or_freshness") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("source_coverage_exploration_prefers_preregistered_lanes") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("source_coverage_saturation_is_compute_control_not_scientific_negative") is True and (state["paper_first_primary_evidence"].get("policy") or {}).get("new_lane_grounded_source_reopens_generation") is True and (not bool((state["paper_first_primary_evidence"].get("summary") or {}).get("source_coverage_exhausted")) or len(portable_review_refs) >= int((state["paper_first_primary_evidence"].get("summary") or {}).get("prior_reviewed_sources") or 0)) and int((state["paper_first_primary_evidence"].get("summary") or {}).get("selected_previously_reviewed") or 0) + int((state["paper_first_primary_evidence"].get("summary") or {}).get("selected_unreviewed") or 0) == int((state["paper_first_primary_evidence"].get("summary") or {}).get("selected") or 0) and (state["paper_first_primary_evidence"].get("policy") or {}).get("pre_registered_lane_coverage_floor") is True and int((state["paper_first_primary_evidence"].get("policy") or {}).get("lane_floor") or 0) >= 1 and not list((state["paper_first_primary_evidence"].get("summary") or {}).get("undercovered_lanes") or []))), "detail":{"status":state["paper_first_primary_evidence"].get("status"),"summary":state["paper_first_primary_evidence"].get("summary")}},
        {"key":"paper-first-object-retrieval-shadow", "pass":object_retrieval_boundary_ok, "detail":{"status":object_retrieval.get("status"),"summary":object_retrieval_summary}},
        {"key":"paper-first-object-candidate-evidence-shadow", "pass":candidate_evidence_boundary_ok, "detail":{"status":candidate_evidence.get("status"),"summary":candidate_evidence_summary}},
        {"key":"paper-first-support-release-watch", "pass":support_release_boundary_ok, "detail":{"status":support_release_watch.get("status"),"summary":support_release_summary,"status_counts":support_release_watch.get("status_counts") or {}}},
        {"key":"paper-first-support-asset-recheck-queue", "pass":support_asset_recheck_boundary_ok, "detail":{"status":support_asset_recheck.get("status"),"summary":support_asset_summary}},
        {"key":"paper-first-support-asset-recheck-handoff", "pass":support_asset_handoff_boundary_ok, "detail":{"status":support_asset_handoff.get("status"),"summary":support_handoff_summary}},
        {"key":"paper-first-shadow-continuation-frontier", "pass":shadow_continuation_boundary_ok, "detail":{"status":shadow_continuation.get("status"),"summary":shadow_continuation.get("summary") or {}}},
        {"key":"paper-first-discovery-frontier", "pass":not validate_paper_first_discovery_frontier(state.get("paper_first_discovery_frontier") or {}), "detail":{"status":(state.get("paper_first_discovery_frontier") or {}).get("status"),"summary":(state.get("paper_first_discovery_frontier") or {}).get("summary"),"blockers":(state.get("paper_first_discovery_frontier") or {}).get("blockers") or []}},
        {"key":"paper-first-global-relation-freshness", "pass":relation_freshness_boundary_ok, "detail":{"status":relation_freshness.get("status"),"summary":relation_freshness_summary}},
        {"key":"paper-first-global-relation-delta-preflight", "pass":relation_delta_boundary_ok, "detail":{"status":relation_delta.get("status"),"summary":relation_delta_summary,"pair_slots":relation_delta.get("pair_slots") or {},"interpretation":relation_delta.get("interpretation") or {}}},
        {"key":"paper-first-global-relation-scan-admission", "pass":relation_admission_boundary_ok, "detail":{"status":relation_admission.get("status"),"summary":relation_admission_summary}},
        {"key":"paper-first-problem-discovery-contract", "pass":state["paper_first_problem_discovery_contract"]["policy"]["multi_lane_discovery_required"] is True and state["paper_first_problem_discovery_contract"]["policy"]["contradiction_first_required"] is False and state["paper_first_problem_discovery_contract"]["policy"]["contradiction_lane_retained"] is True and tuple(state["paper_first_problem_discovery_contract"]["policy"]["allowed_discovery_lanes"]) == DISCOVERY_LANES and tuple(state["paper_first_problem_discovery_contract"]["policy"]["forbidden_discovery_lanes"]) == FORBIDDEN_DISCOVERY_LANES and state["paper_first_problem_discovery_contract"]["policy"]["lane_specific_machine_evidence_contract_required"] is True and live_contract_boundary_ok and state["paper_first_problem_discovery_contract"]["policy"]["no_lane_specific_downstream_relaxation"] is True and state["paper_first_problem_discovery_contract"]["policy"]["two_mature_theory_baselines_required"] is True and state["paper_first_problem_discovery_contract"]["policy"]["same_information_nonreducibility_required"] is True and state["paper_first_problem_discovery_contract"]["policy"]["domain_transfer_veto_required"] is True and state["paper_first_problem_discovery_contract"]["summary"]["automatic_method_authority"] == 0 and state["paper_first_problem_discovery_contract"]["summary"]["automatic_experiment_authority"] == 0, "detail":state["paper_first_problem_discovery_contract"]["summary"]},
        {"key":"paper-first-retrieval-incomplete-generator-boundary", "pass":retrieval_incomplete_boundary_ok, "detail":{"status":generator_status,"source_coverage":generator_coverage}},
        {"key":"paper-first-carrier-pending-generator-boundary", "pass":carrier_pending_boundary_ok, "detail":{"status":generator_status,"source_coverage":generator_coverage}},
        {"key":"paper-first-problem-generator", "pass":state["paper_first_problem_generator"].get("status") in {"NOT_RUN","SKIPPED_INSUFFICIENT_PRIMARY_EVIDENCE","SKIPPED_STALE_PRIMARY_EVIDENCE","SKIPPED_SOURCE_COVERAGE_SATURATED","SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE","SKIPPED_SOURCE_CARRIER_PROBE_PENDING","GENERATOR_ERROR_ZERO_AUTHORITY","GENERATED_ZERO_CANDIDATES","GENERATED_PRE_F0_EVIDENCE_ACQUISITION","GENERATED_AWAIT_PROBLEM_GATE","STATE_UNREADABLE"} and (state["paper_first_problem_generator"].get("policy") or {}).get("zero_candidates_is_valid") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("multi_lane_discovery_enabled") is True and tuple((state["paper_first_problem_generator"].get("policy") or {}).get("allowed_discovery_lanes") or []) == DISCOVERY_LANES and tuple((state["paper_first_problem_generator"].get("policy") or {}).get("forbidden_discovery_lanes") or []) == FORBIDDEN_DISCOVERY_LANES and live_generator_boundary_ok and (state["paper_first_problem_generator"].get("policy") or {}).get("semantic_reviewer_is_block_only") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("independent_reviewer_must_verify_lane_contract") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("source_coverage_saturation_skips_model_call") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("source_coverage_saturation_is_compute_control_not_scientific_negative") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("new_lane_grounded_primary_source_reopens_generation") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("portable_review_receipts_are_scheduler_metadata_only") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("portable_review_receipts_have_zero_scientific_authority") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("primary_source_coverage_receipts_are_inherited_transactionally") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("candidate_inbox_has_zero_scientific_authority") is True and (state["paper_first_problem_generator"].get("policy") or {}).get("automatic_method_authority") is False and (state["paper_first_problem_generator"].get("policy") or {}).get("automatic_experiment_authority") is False and (state["paper_first_problem_generator"].get("status") not in {"GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE"} or (state["paper_first_problem_generator"].get("policy") or {}).get("independent_reviewer_must_ground_both_source_claims_to_exact_primary_evidence_excerpts") is True), "detail":{"status":state["paper_first_problem_generator"].get("status"),"summary":state["paper_first_problem_generator"].get("summary")}},
        {"key":"paper-first-pre-f0-queue", "pass":state["paper_first_pre_f0_queue"].get("scientific_authority") is False and int((state["paper_first_pre_f0_queue"].get("summary") or {}).get("queued") or 0)==len(state["paper_first_pre_f0_queue"].get("rows") or []) and (state["paper_first_pre_f0_queue"].get("policy") or {}).get("cheap_falsifier_is_evidence_acquisition_not_problem_gate") is True and (state["paper_first_pre_f0_queue"].get("policy") or {}).get("positive_f0_requires_exact_same_information_reduction_recheck") is True and (state["paper_first_pre_f0_queue"].get("policy") or {}).get("exact_reduction_required_before_problem_gate") is True and all((state["paper_first_pre_f0_queue"].get("authority") or {}).get(key) is False for key in ("problem_gate","paper_design","method","experiment","p0","gpu")), "detail":{"status":state["paper_first_pre_f0_queue"].get("status"),"summary":state["paper_first_pre_f0_queue"].get("summary")}},
        {"key":"paper-first-problem-gate-queue", "pass":state["paper_first_problem_gate_queue"]["summary"]["audited"] == state["paper_first_problem_gate_queue"]["summary"]["submitted"] and state["paper_first_problem_gate_queue"]["summary"]["passed_problem_gate"] + state["paper_first_problem_gate_queue"]["summary"]["blocked_problem_gate"] == state["paper_first_problem_gate_queue"]["summary"]["audited"] and state["paper_first_problem_gate_queue"]["summary"]["inbox_errors"] == 0 and state["paper_first_problem_gate_queue"]["summary"]["method_authorized"] == 0 and state["paper_first_problem_gate_queue"]["summary"]["experiment_authorized"] == 0 and state["paper_first_problem_gate_queue"]["summary"]["p0_authorized"] == 0 and state["paper_first_problem_gate_queue"]["policy"]["verified_primary_evidence_registry_required_for_submitted_candidates"] is True and state["paper_first_problem_gate_queue"]["policy"]["multi_lane_candidate_schema_required"] is True and state["paper_first_problem_gate_queue"]["policy"]["lane_contract_independent_review_required"] is True and state["paper_first_problem_gate_queue"]["policy"]["independent_semantic_reduction_review_required"] is True, "detail":state["paper_first_problem_gate_queue"]["summary"]},
        {"key":"search-portfolio-paper-design", "pass":state["paper_first_search_portfolio_design_adjudication"]["summary"]["reviewed"] == 2 and state["paper_first_search_portfolio_design_adjudication"]["summary"]["advance_to_method_design"] == 0 and state["paper_first_search_portfolio_design_adjudication"]["summary"]["revise_paper_problem"] == 1 and state["paper_first_search_portfolio_design_adjudication"]["summary"]["stop_standalone"] == 1 and state["paper_first_search_portfolio_design_adjudication"]["summary"]["method_design_authorized"] == 0 and state["paper_first_search_portfolio_design_adjudication"]["policy"]["source_is_shadow_search_portfolio"] is True and state["paper_first_search_portfolio_design_adjudication"]["policy"]["shadow_queue_has_zero_paper_design_authority"] is True and state["paper_first_search_portfolio_design_adjudication"]["policy"]["cannot_grant_or_revoke_live_paper_design_authority"] is True, "detail":state["paper_first_search_portfolio_design_adjudication"]["summary"]},
        {"key":"sp15-identifiability-support", "pass":state["paper_first_sp15_identifiability_support"]["summary"]["query_level_identifiability_units"] == 0 and state["paper_first_sp15_identifiability_support"]["summary"]["support_status"] == "INSUFFICIENT_FOR_IDENTIFIABILITY_CLAIM" and state["paper_first_sp15_identifiability_support"]["summary"]["method_design_authorized"] == 0 and state["paper_first_sp15_identifiability_support"]["policy"]["phenomenon_support_is_not_identifiability_support"] is True and (state["paper_first_sp15_identifiability_support"].get("support_diagnosis") or {}).get("stop_class") == "SUPPORT_STOP" and (state["paper_first_sp15_identifiability_support"].get("support_diagnosis") or {}).get("failure_layer") == "experiment_identifiability" and (state["paper_first_sp15_identifiability_support"].get("support_diagnosis") or {}).get("principle_dead_end_certified") is False, "detail":{"summary":state["paper_first_sp15_identifiability_support"]["summary"],"support_diagnosis":state["paper_first_sp15_identifiability_support"].get("support_diagnosis") or {}}},
        {"key":"shadow-search-latest-terminal", "pass":shadow_latest_ok, "detail":{"run_id":shadow_portfolio.get("latest_run_id",""),"status":shadow_latest.get("status","NOT_RUN"),"summary":shadow_latest_summary}},
        {"key":"paper-first-post-c2-terminal", "pass":state["paper_first_post_c2"]["decision"] == "STOP_CURRENT_CONTROLLED_MEDIATOR_PAPER_MECHANISM" and state["paper_first_post_c2"]["authority"]["clean_mechanism_stop"] is True and state["paper_first_post_c2"]["authority"]["C3_locked"] is True and state["paper_first_post_c2"]["authority"]["full_experiment_authorized"] is False and state["paper_first_post_c2"]["authority"]["new_method_auto_authorized"] is False and state["paper_first_post_c2"]["authority"]["new_paper_problem_auto_authorized"] is False, "detail":{"decision":state["paper_first_post_c2"]["decision"],"c2":state["paper_first_post_c2"]["c2_result"],"gate_provenance":state["paper_first_post_c2"]["gate_provenance"]}},
        {"key":"backend-architecture-manifest", "pass":state["system_architecture"]["summary"]["temporal_stages"] == len(TEMPORAL_FLOW) and state["system_architecture"]["summary"]["reader_chapters"] == len(READING_GROUPS) and state["system_architecture"]["summary"]["reader_stage_coverage"] == len(TEMPORAL_FLOW) and state["system_architecture"]["summary"]["reader_stage_missing"] == 0 and state["system_architecture"]["summary"]["reader_stage_duplicates"] == 0 and state["system_architecture"]["summary"]["reader_stage_extra"] == 0 and state["system_architecture"]["summary"]["functional_layers"] == 6 and state["system_architecture"]["summary"]["assigned_components"] == len(state["components"]) and state["system_architecture"]["summary"]["unassigned_components"] == 0 and state["system_architecture"]["summary"]["duplicate_component_keys"] == 0 and state["system_architecture"]["summary"]["cross_cutting_controls"] == 3 and state["system_architecture"]["summary"]["orphan_cross_cutting_controls"] == 0, "detail":state["system_architecture"]["summary"]},
        {"key":"paper-acceptance-closure", "pass":state["paper_acceptance"].get("scientific_authority") is False and tuple(state["paper_acceptance"].get("temporal_keys") or []) == PAPER_ACCEPTANCE_TEMPORAL_KEYS and tuple(row["key"] for row in state["system_architecture"]["temporal_flow"][-len(PAPER_ACCEPTANCE_TEMPORAL_KEYS):]) == PAPER_ACCEPTANCE_TEMPORAL_KEYS and state["paper_acceptance"]["summary"].get("paper_states") == len(PAPER_ACCEPTANCE_TEMPORAL_KEYS) and state["paper_acceptance"]["summary"].get("mandatory_manuscript_ci_checks") == 9 and state["paper_acceptance"]["summary"].get("append_only_ledger") is True and all(state["paper_acceptance"]["summary"].get(key) == 0 for key in ("automatic_scientific_authority","automatic_experiment_authority","automatic_gpu_authority","automatic_submission_authority")) and state["paper_acceptance"]["policy"].get("causal_hold_blocks_post_evidence_advancement") is True and state["paper_acceptance"]["policy"].get("story_search_winner_required_for_manuscript") is True and state["paper_acceptance"]["policy"].get("both_mock_pc_modes_required_for_targeted_repair") is True and state["paper_acceptance"]["policy"].get("claim_audit_pass_required_for_pdf_qa") is True and state["paper_acceptance"]["policy"].get("submitted_state_requires_external_human_submission_authority") is True, "detail":state["paper_acceptance"]["summary"]},
        {"key":"paper-acceptance-ledger-index", "pass":state["paper_acceptance"]["ledger_index"].get("scientific_authority") is False and (state["paper_acceptance"]["ledger_index"].get("summary") or {}).get("invalid_ledgers") == 0 and (state["paper_acceptance"]["ledger_index"].get("policy") or {}).get("source_ledgers_are_append_only") is True and (state["paper_acceptance"]["ledger_index"].get("policy") or {}).get("public_projection_excludes_raw_reviewer_prose") is True and (state["paper_acceptance"]["ledger_index"].get("policy") or {}).get("public_projection_excludes_filesystem_paths_and_actors") is True and (state["paper_acceptance"]["ledger_index"].get("policy") or {}).get("ledger_projection_has_zero_authority") is True, "detail":state["paper_acceptance"]["ledger_index"].get("summary") or {}},
        {"key":"principle-layer", "pass":state["principle_layer"]["policy"]["experiment_is_evidence_about_a_principle_not_a_vote_on_an_idea"] and state["principle_layer"]["policy"]["true_negative_does_not_automatically_falsify_principle"] and state["principle_layer"]["policy"]["negative_adjudication_must_emit_failure_layer"] and len(state["principle_layer"]["policy"].get("failure_layer_schema") or []) == 7 and state["principle_layer"]["policy"]["core_principle_update_requires_dead_end_counter_explanation"] and state["principle_layer"]["summary"]["certificates_passed"] == expected_pre_experiment_cards, "detail":state["principle_layer"]["summary"]},
        {"key":"pre-experiment-compiler", "pass":state["pre_experiment_compiler"]["policy"]["paper_design_contract_required_before_principle_and_implementation"] and state["pre_experiment_compiler"]["policy"]["paper_design_contract_is_not_a_formal_gate"] and state["pre_experiment_compiler"]["policy"]["principle_certificate_required_before_updater_competence"] and state["pre_experiment_compiler"]["policy"]["principle_certificate_is_not_a_formal_gate"] and state["pre_experiment_compiler"]["policy"]["protocol_validity_required_before_updater_competence"] and state["pre_experiment_compiler"]["policy"]["protocol_validity_is_not_a_formal_gate"] and state["pre_experiment_compiler"]["summary"]["protocol_validity_pass"] == expected_pre_experiment_cards and state["pre_experiment_compiler"]["policy"]["research_execution_plan_required_before_launch"] and state["pre_experiment_compiler"]["policy"]["research_execution_plan_is_derived_not_a_formal_gate"] and state["pre_experiment_compiler"]["policy"]["research_execution_plan_cannot_authorize_execution"] and state["pre_experiment_compiler"]["summary"]["research_execution_plans"] == expected_pre_experiment_cards and state["pre_experiment_compiler"]["policy"]["updater_competence_required_before_gate_1"] and state["pre_experiment_compiler"]["policy"]["updater_competence_is_not_a_ninth_gate"] and state["pre_experiment_compiler"]["policy"]["all_eight_gates_required"] and state["pre_experiment_compiler"]["policy"]["automatic_override_forbidden"] and state["pre_experiment_compiler"]["policy"]["terminal_outcome_requires_endpoint_headroom_audit"] and state["pre_experiment_compiler"]["policy"]["execution_cap_censoring_must_be_typed_separately"] and state["pre_experiment_compiler"]["policy"]["cap_censored_branch_cannot_count_as_natural_terminal_failure"] and state["pre_experiment_compiler"]["summary"]["compiled_cards"] == expected_pre_experiment_cards, "detail":state["pre_experiment_compiler"]["summary"]},
        {"key":"paper-first-p0-human-authority", "pass":state["paper_first_p0_authority"]["summary"].get("promoted") == 0 or state["paper_first_p0_authority"]["summary"].get("authority_status") == "EXTERNAL_HUMAN_P0_PROMOTION_AUTHORITY_VALID", "detail":state["paper_first_p0_authority"]},
        {"key":"paper-first-p0-f0", "pass":state["paper_first_p0_f0"]["summary"].get("ideas") == 4 and state["paper_first_p0_f0"]["summary"].get("quarantined") == 4 and state["paper_first_p0_f0"]["summary"].get("scientifically_authorized") == 0 and state["paper_first_p0_f0"]["summary"].get("method_fail_authorized") == 0 and state["paper_first_p0_f0"]["policy"].get("unauthorized_execution_is_preserved_as_diagnostic_not_scientific_authority") is True, "detail":state["paper_first_p0_f0"]["summary"]},
        {"key":"paper-first-premature-method-diagnostics", "pass":state["paper_first_premature_method_diagnostics"]["summary"].get("directions") == 2 and state["paper_first_premature_method_diagnostics"]["summary"].get("completed_diagnostics") == 2 and state["paper_first_premature_method_diagnostics"]["summary"].get("same_information_reducibility_findings") == 2 and state["paper_first_premature_method_diagnostics"]["summary"].get("scientifically_authorized") == 0 and state["paper_first_premature_method_diagnostics"]["summary"].get("p0_lifecycle_mutations") == 0 and state["paper_first_premature_method_diagnostics"]["authority"].get("cannot_retroactively_authorize") is True, "detail":state["paper_first_premature_method_diagnostics"]["summary"]},
        {"key":"research-learning-loop", "pass":state["scientific_meta_trace"]["policy"]["raw_execution_trace_is_not_scientific_state"] and state["scientific_meta_trace"]["policy"]["active_scientific_state_is_separate_from_institutional_memory"] and state["scientific_meta_trace"]["policy"]["active_scientific_state_never_time_decays"] and state["failure_asset_library"]["policy"]["assets_are_retrieved_before_new_experiment_design"] and state["failure_asset_library"]["policy"]["institutional_memory_requires_scope_and_effectiveness_tracking"] and state["experiment_value_scheduler"]["policy"]["scheduler_cannot_authorize_execution"] and state["research_system_replay"]["summary"]["failed"] == 0 and state["external_system_learning"]["policy"]["every_candidate_design_requires_local_gap_test"], "detail":{"meta":state["scientific_meta_trace"]["summary"],"failure_assets":state["failure_asset_library"]["summary"],"scheduler":state["experiment_value_scheduler"]["summary"],"replay":state["research_system_replay"]["summary"],"external":state["external_system_learning"]["summary"]}},
        {"key":"research-memory-wiki", "pass":state["research_memory_wiki"].get("status")=="MEMORY_COMPILED" and state["research_memory_wiki"].get("scientific_authority") is False and int(((state["research_memory_wiki"].get("lint") or {}).get("summary") or {}).get("errors") or 0)==0 and (state["research_memory_wiki"].get("policy") or {}).get("transient_operational_noise_is_not_prompt_eligible") is True and (state["research_memory_wiki"].get("policy") or {}).get("query_pack_never_relaxes_downstream_gates") is True, "detail":{"summary":state["research_memory_wiki"].get("summary"),"lint":(state["research_memory_wiki"].get("lint") or {}).get("summary")}},
        {"key":"aris-harness-alignment", "pass":state["research_harness_assurance"].get("status")=="PASS_HARNESS_ASSURANCE" and int((state["research_harness_assurance"].get("summary") or {}).get("failed") or 0)==0 and state["research_candidate_portfolio"].get("scientific_authority") is False and int((state["research_candidate_portfolio"].get("summary") or {}).get("automatic_promotions") or 0)==0 and state["search_funnel_telemetry"].get("scientific_authority") is False and state["scientific_research_graph"].get("scientific_authority") is False and (state["scientific_research_graph"].get("policy") or {}).get("experiment_failure_edge_cannot_close_core_principle") is True, "detail":{"assurance":state["research_harness_assurance"].get("summary"),"portfolio":state["research_candidate_portfolio"].get("summary"),"funnel":state["search_funnel_telemetry"].get("summary"),"graph":state["scientific_research_graph"].get("summary")}},
        {"key":"pilot-schema", "pass":state["pilot_registry"]["summary"]["invalid_result_files"] == 0 and state["pilot_registry"]["summary"]["invalid_approval_files"] == 0 and state["pilot_registry"]["policy"]["automatic_p0_to_p1_forbidden"] and state["pilot_registry"]["policy"]["p0_execution_requires_pre_experiment_8_of_8"], "detail":state["pilot_registry"]["summary"]},
        {"key":"experiment-diagnosis", "pass":state["experiment_iteration"]["summary"]["nodes"] == 4 and state["experiment_iteration"]["policy"]["nonidentifiable_pilot_cannot_update_scientific_belief"], "detail":state["experiment_iteration"]["summary"]},
        {"key":"mem-xfer-workflow", "pass":not _mem_xfer_semantic_errors(state["mem_xfer_workflow"]), "detail":{"semantic_errors":_mem_xfer_semantic_errors(state["mem_xfer_workflow"]),"support_qualification":state["mem_xfer_workflow"]["support_qualification"]["status"],"full_support":state["mem_xfer_workflow"]["full_support"]["status"],"cpu_gate":state["mem_xfer_workflow"]["support_enriched_analysis"]["status"],"second_model":state["mem_xfer_workflow"]["second_model"]["status"]}},
        {"key":"human-terminal-ledger", "pass":terminal_summary.get("human_parents") == 26 and terminal_summary.get("p0_resolved_lineages") == 26 and terminal_summary.get("drop") == 0 and terminal_summary.get("revived_to_p0") == 7, "detail":terminal_summary},
        {"key":"p0-admission", "pass":state["p0_admission"]["summary"].get("active_p0") == expected_active_p0 and state["p0_admission"]["summary"].get("admitted") == expected_active_p0 and state["p0_admission"]["summary"].get("transitioned_from_p0_ready") == 16 and state["p0_admission"]["summary"].get("revived_from_drop") == 7 and state["p0_admission"]["summary"].get("settings_complete") == expected_active_p0, "detail":state["p0_admission"]["summary"]},
        {"key":"p0-economy-gate", "pass":state["p0_economy_gate"]["summary"].get("ideas") == expected_active_p0 and state["p0_economy_gate"]["summary"].get("economy_ready") == state["p0_admission"]["summary"].get("economy_ready") and state["p0_economy_gate"]["policy"].get("all_five_required_before_execution_compilation") is True, "detail":state["p0_economy_gate"]["summary"]},
        {"key":"ai-consultation-clinic", "pass":state["ai_consultation_clinic"]["summary"].get("checkpoints") == 5 and state["ai_consultation_clinic"]["policy"].get("ai_vote_can_authorize_gpu") is False and state["ai_consultation_clinic"]["policy"].get("high_risk_findings_must_be_compiled_into_machine_checks") is True, "detail":state["ai_consultation_clinic"]["summary"]},
        {"key":"ai-consultation-automation", "pass":state["ai_consultation_automation"]["policy"].get("content_addressed_triggers") is True and state["ai_consultation_automation"]["policy"].get("ai_output_never_authorizes_execution") is True and state["ai_consultation_automation"]["clinic_policy"].get("ai_vote_can_authorize_gpu") is False, "detail":state["ai_consultation_automation"]["summary"]},
        {"key":"p0-decision-ledger", "pass":state["p0_decision_ledger"]["summary"].get("active_p0") == expected_active_p0 and state["p0_decision_ledger"]["summary"].get("launchable") == 0 and state["p0_decision_ledger"]["summary"].get("failure_diagnosis_incomplete") == 0 and state["p0_decision_ledger"]["summary"].get("failure_diagnosis_complete") == state["p0_decision_ledger"]["summary"].get("failure_diagnosis_required") and state["p0_decision_ledger"]["policy"].get("economy_stop_overrides_planned_registry_display") is True and state["p0_decision_ledger"]["policy"].get("failed_or_held_experiment_requires_failure_layer") is True, "detail":state["p0_decision_ledger"]["summary"]},
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
    visual_portfolio=state.get("paper_visual_evidence") or {};visual_policy=visual_portfolio.get("policy") or {};visual_summary=visual_portfolio.get("summary") or {}
    if visual_portfolio.get("scientific_authority") is not False or any((visual_portfolio.get("authority") or {}).values()): errors.append("paper visual evidence portfolio must remain zero-authority")
    if visual_policy.get("main_visuals_are_reviewer_question_driven_not_decorative") is not True or visual_policy.get("visual_completion_requires_data_script_figure_caption_binding") is not True: errors.append("paper visual evidence portfolio policy missing")
    if int(visual_summary.get("paper_first_designs") or 0)!=4 or int(visual_summary.get("planned_main_visualizations") or 0)!=16 or int(visual_summary.get("stri_completed_main_visualizations") or 0)!=4 or int(visual_summary.get("repair_required") or 0)!=0: errors.append("paper visual evidence portfolio accounting mismatch")
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
    primary_evidence = state.get("paper_first_primary_evidence") or {}; primary_policy = primary_evidence.get("policy") or {}; primary_summary = primary_evidence.get("summary") or {}; primary_schema=str(primary_evidence.get("schema_version") or "0")
    if primary_policy.get("candidate_generation_authority") is not False or primary_policy.get("method_authority") is not False or primary_policy.get("experiment_authority") is not False: errors.append("primary evidence refresh can supply provenance but cannot authorize candidate/method/experiment transitions")
    if primary_schema >= "1.1":
        carrier=primary_evidence.get("carrier_probe") or {};allowed_objects=set(str(value) for value in primary_policy.get("scientific_object_lanes") or [])
        if primary_policy.get("no_lane_carrier_probe_enabled") is not True or primary_policy.get("no_lane_carrier_probe_is_existing_object_rescue_only") is not True or primary_policy.get("no_lane_carrier_probe_cannot_create_new_object") is not True or primary_policy.get("no_lane_carrier_probe_has_zero_scientific_authority") is not True or primary_policy.get("no_lane_carrier_probe_failure_prevents_coverage_exhaustion") is not True or primary_policy.get("carrier_probe_pending_skips_live_generator_call") is not True:
            errors.append("Primary 1.1 must enforce bounded zero-authority existing-object carrier rescue")
        if carrier.get("scientific_authority") is not False or int(carrier.get("pending") or 0)!=int(primary_summary.get("carrier_probe_pending") or 0) or bool(carrier.get("complete"))!=bool(primary_summary.get("carrier_probe_complete")):
            errors.append("Primary carrier-probe accounting mismatch")
        if primary_summary.get("source_coverage_exhausted") is True and int(primary_summary.get("carrier_probe_pending") or 0)>0:
            errors.append("source coverage cannot be exhausted while carrier-probe backlog remains")
        for row in carrier.get("portable_receipts") or []:
            if not isinstance(row,dict):
                errors.append("Primary carrier-probe receipts must be content-addressed zero-authority existing-object receipts"); break
            scope_excluded=str(row.get("probe_outcome") or "")=="SCOPE_EXCLUDED_BY_PRIMARY"
            fulltext_ok=(scope_excluded and not str(row.get("fulltext_sha256") or "") and not (row.get("live_rescue_eligible_lanes") or [])) or len(str(row.get("fulltext_sha256") or ""))==64
            if row.get("scientific_authority") is not False or len(str(row.get("primary_sha256") or ""))!=64 or not fulltext_ok or any(str(value) not in allowed_objects for value in row.get("live_rescue_eligible_lanes") or []):
                errors.append("Primary carrier-probe receipts must be content-addressed zero-authority existing-object receipts"); break
    if primary_evidence.get("status") == "READY" and (primary_summary.get("verified") or 0) < 4: errors.append("READY primary evidence pool must contain at least four verified records")
    if primary_evidence.get("status") == "READY" and (primary_policy.get("primary_publication_age_is_bounded") is not True or float(primary_policy.get("maximum_publication_age_days") or 9999) > 60.0): errors.append("READY primary evidence pool must hard-bound publication age to <=60 days")
    if primary_evidence.get("status") == "READY" and (primary_policy.get("fulltext_enrichment_is_optional") is not True or primary_policy.get("fulltext_snippets_remain_private_data_artifacts") is not True or primary_policy.get("empirical_fact_candidates_are_not_ground_truth") is not True or primary_policy.get("typed_evidence_candidates_are_not_ground_truth") is not True or primary_policy.get("typed_evidence_is_deterministic_and_bounded") is not True): errors.append("READY primary evidence must keep fulltext/typed enrichment optional-private, deterministic-bounded, and non-authoritative")
    if primary_evidence.get("status") == "READY" and (primary_policy.get("empirical_fact_precision_gate") is not True or primary_policy.get("empirical_fact_extraction_version") != "precision-v2" or primary_policy.get("derived_empirical_facts_reused_only_when_extractor_version_matches") is not True): errors.append("READY primary evidence must use the versioned empirical-fact precision gate and forbid cross-version derived-fact reuse")
    if primary_evidence.get("status") == "READY" and (primary_policy.get("typed_evidence_extraction_version") not in SUPPORTED_TYPED_EVIDENCE_SNAPSHOT_VERSIONS or primary_policy.get("derived_typed_evidence_reused_only_when_extractor_version_matches") is not True or primary_policy.get("typed_evidence_requires_first_party_ownership_or_nonliterature_attribution") is not True): errors.append("READY primary evidence must use a supported first-party-owned typed-evidence snapshot and forbid cross-version typed-evidence reuse")
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
    object_retrieval = state.get("paper_first_scientific_object_retrieval_audit") or {}
    if object_retrieval:
        object_policy=object_retrieval.get("policy") or {};object_summary=object_retrieval.get("summary") or {};object_results=object_retrieval.get("results") or {}
        if object_retrieval.get("scientific_authority") is not False or object_policy.get("shadow_only") is not True or object_policy.get("live_query_set_changed") is not False or object_policy.get("candidate_metadata_does_not_count_as_verified_primary_support") is not True or object_policy.get("incomplete_query_is_not_negative_evidence") is not True or object_policy.get("primary_verification_required_before_lane_preregistration") is not True or object_policy.get("automatic_lane_activation") is not False or int(object_summary.get("activation_authorized") or 0) != 0:
            errors.append("scientific-object retrieval audit must remain shadow-only metadata recall with zero lane authority")
        if any(not isinstance(row,dict) or row.get("scientific_authority") is not False or "rows" in row or "queries" in row or "ref" in row for row in object_results.values()):
            errors.append("scientific-object retrieval public summary cannot expose private queries, rows, refs, or scientific authority")
    candidate_evidence = state.get("paper_first_scientific_object_candidate_evidence") or {}
    if candidate_evidence:
        evidence_policy=candidate_evidence.get("policy") or {};evidence_summary=candidate_evidence.get("summary") or {};evidence_results=candidate_evidence.get("results") or {}
        if candidate_evidence.get("scientific_authority") is not False or evidence_policy.get("shadow_only") is not True or evidence_policy.get("network_fetch_forbidden") is not True or evidence_policy.get("source_exposure_effect") is not False or evidence_policy.get("live_query_effect") is not False or evidence_policy.get("candidate_primary_verification_does_not_activate_lane") is not True or evidence_policy.get("support_purity_and_ownership_gates_still_required") is not True or int(evidence_summary.get("activation_authorized") or 0)!=0:
            errors.append("scientific-object candidate evidence must remain shadow-only primary verification with zero live exposure or lane authority")
        if any(not isinstance(row,dict) or row.get("scientific_authority") is not False or "ref" in row or "title" in row or "abstract" in row or "records" in row for row in evidence_results.values()):
            errors.append("scientific-object candidate evidence public summary cannot expose private primary records")
    discovery_contract = state.get("paper_first_problem_discovery_contract") or {}; discovery_policy = discovery_contract.get("policy") or {}; discovery_summary = discovery_contract.get("summary") or {}
    if discovery_policy.get("multi_lane_discovery_required") is not True or discovery_policy.get("contradiction_first_required") is not False or discovery_policy.get("contradiction_lane_retained") is not True or tuple(discovery_policy.get("allowed_discovery_lanes") or []) != DISCOVERY_LANES or tuple(discovery_policy.get("forbidden_discovery_lanes") or []) != FORBIDDEN_DISCOVERY_LANES or discovery_policy.get("lane_specific_machine_evidence_contract_required") is not True or discovery_policy.get("no_lane_specific_downstream_relaxation") is not True or discovery_policy.get("two_mature_theory_baselines_required") is not True or discovery_policy.get("same_information_nonreducibility_required") is not True or discovery_policy.get("domain_transfer_veto_required") is not True or discovery_policy.get("single_source_anomaly_first_search_enabled") is not True or discovery_policy.get("primary_anomaly_can_trigger_controlled_residual_search_without_cross_paper_metric_match") is not True or discovery_policy.get("reopenable_support_hold_search_prior_enabled") is not True or discovery_policy.get("support_stop_is_not_search_closure") is not True or discovery_policy.get("support_hold_revisit_requires_reopen_evidence") is not True or discovery_policy.get("support_hold_missing_support_is_not_scientific_negative") is not True or discovery_policy.get("principle_dead_end_inversion_search_enabled") is not True or discovery_policy.get("dead_end_inversion_requires_certified_counter_explanation") is not True or discovery_policy.get("dead_end_inversion_is_search_prior_not_scientific_authority") is not True or discovery_policy.get("dead_end_inversion_requires_fresh_primary_grounding") is not True or discovery_policy.get("dead_end_inversion_must_satisfy_recorded_reopen_condition") is not True or discovery_policy.get("first_party_inversion_asset_grounding_enabled") is not True or discovery_policy.get("first_party_inversion_asset_requires_provenance_manifest") is not True or discovery_policy.get("first_party_inversion_asset_is_zero_authority_search_evidence") is not True or discovery_policy.get("first_party_inversion_asset_requires_one_direct_seed_per_shard") is not True or discovery_policy.get("observed_dependency_graph_is_not_an_identifiability_gap") is not True or discovery_policy.get("reciprocal_coupling_claim_requires_downstream_residual_beyond_distribution_shift") is not True or discovery_policy.get("feedback_mechanism_requires_causal_write_path_before_experiment") is not True or discovery_policy.get("positive_residual_search_enabled") is not True or discovery_policy.get("positive_residual_asset_requires_provenance_manifest") is not True or discovery_policy.get("positive_residual_asset_is_zero_authority_search_evidence") is not True or discovery_policy.get("positive_residual_requires_surviving_phenomenon_and_clean_mechanism_stop") is not True or discovery_policy.get("positive_residual_requires_prospective_pre_outcome_prediction") is not True or discovery_policy.get("positive_residual_outcome_leakage_forbidden") is not True or discovery_policy.get("positive_residual_direct_seed_required_in_unexplained_boundary_shard") is not True or discovery_policy.get("inactive_search_assets_hidden_from_generator") is not True or discovery_policy.get("inactive_search_assets_remain_provenance_archived") is not True or discovery_policy.get("no_active_asset_fallback_requires_latest_primary_quantitative_anomaly") is not True or discovery_policy.get("fresh_phenomenon_seed_must_name_measured_boundary_or_failure") is not True or discovery_policy.get("fresh_phenomenon_asset_readiness_is_priority_not_novelty_authority") is not True or discovery_policy.get("fresh_phenomenon_missing_substrate_is_hold_not_scientific_fail") is not True or discovery_policy.get("fresh_phenomenon_recent_window_source_coverage_required") is not True or discovery_policy.get("fresh_phenomenon_target_is_evidence_level_not_source_level") is not True or discovery_policy.get("fresh_phenomenon_principle_closure_is_exact_evidence_sha_only") is not True or discovery_policy.get("fresh_phenomenon_closure_does_not_blacklist_source") is not True or discovery_policy.get("fresh_phenomenon_measured_failure_requires_failure_cue") is not True or discovery_policy.get("fresh_phenomenon_shard_has_deterministic_target_ref") is not True or discovery_policy.get("fresh_phenomenon_shard_has_deterministic_phenomenon_id") is not True or discovery_policy.get("fresh_phenomenon_seed1_must_match_target_ref") is not True or discovery_policy.get("fresh_phenomenon_seed1_must_match_target_phenomenon") is not True or discovery_policy.get("temporal_exposure_relabeling_after_longitudinal_reduction_forbidden") is not True or discovery_policy.get("treatment_semantics_seed_requires_executable_version_change") is not True or discovery_policy.get("treatment_semantics_seed_requires_versioned_treatment_reduction_first") is not True or discovery_policy.get("source_coverage_saturation_reopens_once_on_operator_change") is not True or discovery_policy.get("canonical_double_funnel_required") is not True or discovery_policy.get("canonical_double_funnel_reuses_portfolio_engine") is not True or discovery_policy.get("historical_search_portfolio_remains_shadow_only") is not True or discovery_policy.get("one_content_addressed_pool_allows_at_most_one_discovery_transaction") is not True or discovery_policy.get("bounded_provider_subcalls_inside_discovery_transaction") is not True or discovery_policy.get("attack_repair_split_before_terminal_review") is not True or discovery_policy.get("principle_reduction_does_not_auto_close_other_paperability_axes") is not True or discovery_policy.get("pre_f0_evidence_acquisition_has_zero_scientific_authority") is not True or discovery_policy.get("exact_reduction_required_before_final_problem_gate") is not True or discovery_policy.get("discovery_operator_version") != DISCOVERY_OPERATOR_VERSION: errors.append("paper-first problem discovery contract must require high-recall double-funnel search, repair-before-terminal-review, zero-authority pre-F0, provenance-bound dead-end inversion, and the same strict final reduction gates")
    if discovery_policy.get("reduction_pending_may_reach_block_only_semantic_review") is not True or discovery_policy.get("reduction_pending_cannot_pass_problem_gate") is not True or discovery_policy.get("contradiction_requires_matched_intervention_semantics") is not True or discovery_policy.get("contradiction_requires_matched_adaptation_stage") is not True:
        errors.append("paper-first v14 must review reduction-pending lane semantics before falsifier design while preserving Problem-Gate block and matched contradiction treatment semantics")
    if discovery_policy.get("search_portfolio_is_shadow_only") is not True or discovery_policy.get("search_portfolio_cannot_publish_canonical_generator_or_queue") is not True or discovery_policy.get("historical_search_portfolio_remains_shadow_only") is not True or discovery_policy.get("one_content_addressed_pool_allows_at_most_one_live_generator_call") is not False or discovery_policy.get("one_content_addressed_pool_allows_at_most_one_discovery_transaction") is not True or tuple(discovery_policy.get("search_portfolio_primitives") or []) != SEARCH_PORTFOLIO_PRIMITIVES: errors.append("historical Search Portfolio must remain shadow-only while canonical discovery reuses its ten-primitive engine only inside one bounded double-funnel transaction")
    if discovery_summary.get("saturation_patterns") != fresh_summary.get("reduction_patterns") or discovery_summary.get("automatic_method_authority") != 0 or discovery_summary.get("automatic_experiment_authority") != 0: errors.append("paper-first problem discovery contract must consume the current saturation map and grant no automatic downstream authority")
    generator = state.get("paper_first_problem_generator") or {}; generator_policy = generator.get("policy") or {}; generator_summary = generator.get("summary") or {}; generator_schema = str(generator.get("schema_version") or "0")
    generator_double_funnel=generator_policy.get("search_portfolio_enabled") is True
    if generator_double_funnel:
        if generator_policy.get("search_portfolio_is_shadow_only") is not False or generator_policy.get("legacy_published_search_portfolio_remains_shadow_only") is not True or generator_policy.get("canonical_transaction_forbids_search_portfolio") is not False: errors.append("canonical double-funnel must not promote the historical shadow Search Portfolio")
        if generator_policy.get("one_generator_call_max") is not False or generator_policy.get("one_semantic_reviewer_call_max") is not False or generator_policy.get("one_content_addressed_pool_allows_at_most_one_discovery_transaction") is not True or generator_policy.get("bounded_provider_subcalls_inside_discovery_transaction") is not True: errors.append("canonical double-funnel must use one bounded discovery transaction rather than a one-provider-call assumption")
        if int(generator_policy.get("portfolio_generator_subcall_budget") or 0)<=0 or int(generator_policy.get("portfolio_semantic_reviewer_subcall_budget") or 0)<=0: errors.append("canonical double-funnel provider subcall budgets must be explicit and positive")
        if generator_policy.get("attack_repair_split_before_formulation") is not True or generator_policy.get("principle_reduction_does_not_auto_close_other_paperability_axes") is not True or generator_policy.get("pre_f0_evidence_acquisition_has_zero_scientific_authority") is not True or generator_policy.get("exact_reduction_required_before_final_problem_gate") is not True: errors.append("canonical double-funnel must preserve repair, paperability, pre-F0, and final exact-reduction boundaries")
    else:
        if "one_generator_call_max" in generator_policy and generator_policy.get("one_generator_call_max") is not True: errors.append("legacy canonical problem generator must allow at most one generator call per content-addressed pool")
        if "one_semantic_reviewer_call_max" in generator_policy and generator_policy.get("one_semantic_reviewer_call_max") is not True: errors.append("legacy canonical problem generator must allow at most one semantic reviewer call per content-addressed pool")
        if "canonical_transaction_forbids_search_portfolio" in generator_policy and generator_policy.get("canonical_transaction_forbids_search_portfolio") is not True: errors.append("legacy canonical generator policy must keep Search Portfolio out of the live transaction")
    generator_operator_version = str(generator_policy.get("discovery_operator_version") or "").strip()
    # The public canonical generator state is a historical transaction receipt, not a
    # mutable declaration of the currently installed discovery operator. When the
    # operator changes, the old closed receipt must remain labeled with its original
    # version; admission logic may then allow one new operator-qualified transaction.
    # Accept that explicit historical state here without relabeling it as current.
    generator_closed_historical_receipt = bool(
        generator_operator_version
        and generator_operator_version != DISCOVERY_OPERATOR_VERSION
        and generator.get("status") in {
            "GENERATED_ZERO_CANDIDATES",
            "GENERATED_PRE_F0_EVIDENCE_ACQUISITION",
            "GENERATED_AWAIT_PROBLEM_GATE",
            "GENERATED_PRE_F0_EVIDENCE_ACQUISITION",
            "SKIPPED_SOURCE_COVERAGE_SATURATED",
            "SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE",
            "SKIPPED_SOURCE_CARRIER_PROBE_PENDING",
            "SKIPPED_INSUFFICIENT_PRIMARY_EVIDENCE",
            "SKIPPED_STALE_PRIMARY_EVIDENCE",
        }
        and generator_policy.get("source_coverage_saturation_reopens_once_on_operator_change") is True
        and ((generator_policy.get("search_portfolio_enabled") is True and generator_policy.get("one_content_addressed_pool_allows_at_most_one_discovery_transaction") is True) or (generator_policy.get("search_portfolio_enabled") is not True and generator_policy.get("one_content_addressed_pool_allows_at_most_one_live_generator_call_per_discovery_operator") is True))
        and generator_policy.get("source_coverage_saturation_operator_upgrade_recompile_is_explicit_exception") is True
    )
    current_double_funnel_operator_ok=bool(
        generator_operator_version==DISCOVERY_OPERATOR_VERSION
        and generator_double_funnel
        and generator_policy.get("source_coverage_saturation_skips_model_call_after_current_operator_receipt") is True
        and generator_policy.get("source_coverage_saturation_operator_upgrade_recompile_is_explicit_exception") is True
        and generator_policy.get("source_coverage_saturation_reopens_once_on_operator_change") is True
        and generator_policy.get("one_content_addressed_pool_allows_at_most_one_discovery_transaction") is True
        and generator_policy.get("single_source_anomaly_first_enabled") is True
    )
    current_legacy_operator_ok=bool(
        generator_operator_version==DISCOVERY_OPERATOR_VERSION
        and not generator_double_funnel
        and generator_policy.get("source_coverage_saturation_skips_model_call_after_current_operator_receipt") is True
        and generator_policy.get("source_coverage_saturation_operator_upgrade_recompile_is_explicit_exception") is True
        and generator_policy.get("source_coverage_saturation_reopens_once_on_operator_change") is True
        and generator_policy.get("one_content_addressed_pool_allows_at_most_one_live_generator_call_per_discovery_operator") is True
        and generator_policy.get("single_source_anomaly_first_enabled") is True
    )
    generator_operator_contract_ok = bool(not generator_operator_version or generator_closed_historical_receipt or current_double_funnel_operator_ok or current_legacy_operator_ok)
    if generator_policy.get("zero_candidates_is_valid") is not True or generator_policy.get("multi_lane_discovery_enabled") is not True or tuple(generator_policy.get("allowed_discovery_lanes") or []) != DISCOVERY_LANES or tuple(generator_policy.get("forbidden_discovery_lanes") or []) != FORBIDDEN_DISCOVERY_LANES or generator_policy.get("semantic_reviewer_is_block_only") is not True or generator_policy.get("independent_reviewer_must_verify_lane_contract") is not True or generator_policy.get("source_coverage_saturation_skips_model_call") is not True or not generator_operator_contract_ok or generator_policy.get("source_coverage_saturation_is_compute_control_not_scientific_negative") is not True or generator_policy.get("new_lane_grounded_primary_source_reopens_generation") is not True or generator_policy.get("portable_review_receipts_are_scheduler_metadata_only") is not True or generator_policy.get("portable_review_receipts_have_zero_scientific_authority") is not True or generator_policy.get("primary_source_coverage_receipts_are_inherited_transactionally") is not True or generator_policy.get("candidate_inbox_has_zero_scientific_authority") is not True: errors.append("problem generator must enforce four-lane review plus versioned zero-authority saturation control")
    if generator.get("status") == "SKIPPED_SOURCE_COVERAGE_SATURATED":
        coverage = generator.get("source_coverage") or {}
        unreviewed = coverage.get("unreviewed_lane_linked_sources")
        if coverage.get("coverage_exhausted") is not True or unreviewed is None or int(unreviewed) != 0:
            errors.append("source-coverage saturation skip requires an exhausted lane-grounded evidence universe")
        if coverage.get("carrier_probe_required") is True and (int(coverage.get("carrier_probe_pending") or 0)>0 or coverage.get("carrier_probe_complete") is not True):
            errors.append("source-coverage saturation skip requires completed carrier probing")
    if generator.get("status") == "SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE":
        coverage=generator.get("source_coverage") or {}
        if generator_policy.get("incomplete_retrieval_without_new_lane_source_skips_model_call") is not True or generator_policy.get("retrieval_incomplete_is_compute_control_not_scientific_negative") is not True:
            errors.append("retrieval-incomplete skip must be explicit zero-authority compute control")
        if coverage.get("source_retrieval_complete") is not False or coverage.get("coverage_exhausted") is True or int(coverage.get("unreviewed_lane_linked_sources") or 0)!=0:
            errors.append("retrieval-incomplete generator state is inconsistent")
        if int(generator_summary.get("generated") or 0)!=0 or int(generator_summary.get("written_to_auto_inbox") or 0)!=0 or int(generator_summary.get("semantic_clear") or 0)!=0 or int(generator_summary.get("semantic_blocked") or 0)!=0:
            errors.append("retrieval-incomplete skip cannot contain generated candidates or reviews")
    if generator.get("status") == "SKIPPED_SOURCE_CARRIER_PROBE_PENDING":
        coverage=generator.get("source_coverage") or {}
        if generator_policy.get("carrier_probe_pending_skips_model_call") is not True or generator_policy.get("carrier_probe_pending_is_compute_control_not_scientific_negative") is not True:
            errors.append("carrier-probe pending skip must be explicit zero-authority compute control")
        if coverage.get("coverage_exhausted") is True or coverage.get("carrier_probe_required") is not True or int(coverage.get("carrier_probe_pending") or 0)<=0 or coverage.get("carrier_probe_complete") is True or int(coverage.get("unreviewed_lane_linked_sources") or 0)!=0:
            errors.append("carrier-probe pending generator state is inconsistent")
        if int(generator_summary.get("generated") or 0)!=0 or int(generator_summary.get("written_to_auto_inbox") or 0)!=0 or int(generator_summary.get("semantic_clear") or 0)!=0 or int(generator_summary.get("semantic_blocked") or 0)!=0:
            errors.append("carrier-probe pending skip cannot contain generated candidates or reviews")
    if generator_policy.get("generation_notes_are_advisory_not_scientific_authority") is not True or generator_policy.get("zero_candidate_rationale_required") is not True or generator_policy.get("discovery_saturation_memory_has_zero_scientific_authority") is not True: errors.append("problem generator must preserve generation rationale and saturation memory without scientific authority")
    if generator_schema >= "2.3" and (generator_policy.get("reviewer_blocked_problem_memory_has_zero_scientific_authority") is not True or generator_policy.get("repeated_reduction_basin_requires_search_escape") is not True or generator_policy.get("portable_blocked_problem_memory_is_search_control_only") is not True): errors.append("problem generator must treat reviewer-blocked problem memory as zero-authority search control")
    if generator_schema >= "2.3" and (generator_policy.get("reviewer_declared_excerpt_source_is_audit_metadata_not_grounding_authority") is not True or generator_policy.get("exact_excerpt_location_is_machine_inferred") is not True): errors.append("problem generator must infer exact excerpt location rather than trust reviewer source labels")
    if generator_schema >= "2.4":
        if generator_double_funnel:
            if generator_policy.get("portfolio_expansion_must_audit_all_discovery_lanes") is not True or generator_policy.get("lane_search_diagnostics_have_zero_scientific_authority") is not True or generator_policy.get("lane_search_never_requires_candidate") is not True: errors.append("double-funnel generator must audit all ten search primitives as zero-authority expansion")
        elif generator_policy.get("one_generator_call_must_audit_all_discovery_lanes") is not True or generator_policy.get("lane_search_diagnostics_have_zero_scientific_authority") is not True or generator_policy.get("historically_underexplored_lanes_are_searched_first") is not True or generator_policy.get("lane_search_never_requires_candidate") is not True: errors.append("legacy problem generator must audit all four discovery lanes in one zero-authority search pass without forcing candidates")
    lane_search = generator.get("search_diagnostics") or {}
    if generator_schema >= "2.4" and lane_search.get("scientific_authority") is not False: errors.append("lane-search diagnostics cannot carry scientific authority")
    expected_search_lanes=SEARCH_PORTFOLIO_PRIMITIVES if generator_double_funnel else DISCOVERY_LANES
    if generator_schema >= "2.4" and set(lane_search.get("lane_search_priority") or []) != set(expected_search_lanes): errors.append("lane-search priority must cover the active discovery search vocabulary")
    pre_f0=state.get("paper_first_pre_f0_queue") or {};pre_f0_policy=pre_f0.get("policy") or {};pre_f0_summary=pre_f0.get("summary") or {};pre_f0_rows=[row for row in pre_f0.get("rows") or [] if isinstance(row,dict)];pre_f0_authority=pre_f0.get("authority") or {}
    if pre_f0:
        if pre_f0.get("scientific_authority") is not False or int(pre_f0_summary.get("queued") or 0)!=len(pre_f0_rows) or any(pre_f0_authority.get(key) is not False for key in ("problem_gate","paper_design","method","experiment","p0","gpu")): errors.append("canonical pre-F0 queue must remain zero-authority with exact row accounting")
        if pre_f0_policy.get("cheap_falsifier_is_evidence_acquisition_not_problem_gate") is not True or pre_f0_policy.get("positive_f0_requires_exact_same_information_reduction_recheck") is not True or pre_f0_policy.get("exact_reduction_required_before_problem_gate") is not True or pre_f0_policy.get("pre_f0_cannot_enter_persistent_dead_end_memory") is not True: errors.append("canonical pre-F0 queue must preserve evidence-acquisition and post-F0 exact-reduction boundaries")
        if pre_f0_policy.get("candidate_id_is_run_local_ordinal") is not True or pre_f0_policy.get("candidate_snapshot_sha256_required") is not True: errors.append("canonical pre-F0 queue must bind run-local candidate ordinals to immutable candidate snapshots")
        pre_f0_snapshots=[]
        for row in pre_f0_rows:
            try: validate_candidate_identity(row)
            except ValueError: errors.append(f"canonical pre-F0 candidate identity is invalid: {row.get('candidate_id')}")
            snapshot=str(row.get("candidate_snapshot_sha256") or "").strip().lower()
            if snapshot: pre_f0_snapshots.append(snapshot)
        if len(pre_f0_snapshots)!=len(pre_f0_rows) or len(set(pre_f0_snapshots))!=len(pre_f0_snapshots): errors.append("canonical pre-F0 candidate snapshots must be present and unique")
        if any(row.get("scientific_authority") is not False or any((row.get("authority") or {}).get(key) is not False for key in ("problem_gate","paper_design","method","experiment","p0","gpu")) or str(row.get("next_if_positive") or "")!="RERUN_EXACT_SAME_INFORMATION_REDUCTION" for row in pre_f0_rows): errors.append("canonical pre-F0 row leaks authority or bypasses exact-reduction recheck")
        if generator_double_funnel and int(generator_summary.get("pre_f0_eligible") or 0)!=int(pre_f0_summary.get("queued") or 0): errors.append("canonical generator and pre-F0 queue accounting must match")
    pre_f0_support=state.get("paper_first_pre_f0_problem_falsifier_preflight") or {};pre_f0_support_summary=pre_f0_support.get("summary") or {};pre_f0_support_authority=pre_f0_support.get("authority") or {}
    if pre_f0_support:
        if pre_f0_support.get("scientific_authority") is not False or any(pre_f0_support_authority.get(key) is not False for key in ("canonical_generator","canonical_problem_gate","paper_design","method","experiment","p0","gpu")): errors.append("canonical Pre-F0 support preflight must remain zero-authority")
        if (pre_f0_support.get("policy") or {}).get("canonical_pre_f0_candidate_snapshot_binding_required") is not True: errors.append("canonical Pre-F0 support preflight must require candidate snapshot binding")
        if pre_f0_support.get("status") == "PROBLEM_FALSIFIER_PREFLIGHT_COMPLETE":
            support_queued=int(pre_f0_support_summary.get("queued") or 0);support_ready=int(pre_f0_support_summary.get("support_qualified") or 0);support_hold=int(pre_f0_support_summary.get("hold_support_unavailable") or 0);executed=int(pre_f0_support_summary.get("falsifier_executed") or 0)
            if support_queued!=int(pre_f0_summary.get("queued") or 0) or support_ready+support_hold!=support_queued or executed!=0: errors.append("canonical Pre-F0 support preflight must cover the queue exactly without executing a falsifier")
            queue_identity={(str(row.get("candidate_id") or ""),str(row.get("candidate_identity_version") or ""),str(row.get("candidate_snapshot_sha256") or "").strip().lower()) for row in pre_f0_rows}
            support_rows=[row for row in pre_f0_support.get("rows") or [] if isinstance(row,dict)]
            support_identity={(str(row.get("candidate_id") or ""),str(row.get("candidate_identity_version") or ""),str(row.get("candidate_snapshot_sha256") or "").strip().lower()) for row in support_rows}
            if len(support_identity)!=len(support_rows) or support_identity!=queue_identity: errors.append("canonical Pre-F0 support preflight candidate snapshots do not exactly match the queue")
    generated_discovery_statuses={"GENERATED_ZERO_CANDIDATES","GENERATED_PRE_F0_EVIDENCE_ACQUISITION","GENERATED_AWAIT_PROBLEM_GATE"}
    expected_lane_statuses={"EXPANDED","EMPTY"} if generator_double_funnel else {"NO_PAIR","REDUCIBLE","CANDIDATE"}
    if generator_schema >= "2.4" and generator.get("status") in generated_discovery_statuses:
        lane_rows=[row for row in lane_search.get("lane_search") or [] if isinstance(row,dict)]
        lane_names=[str(row.get("lane") or "") for row in lane_rows]
        lane_statuses=[str(row.get("status") or "") for row in lane_rows]
        if lane_search.get("lane_search_complete") is not True or len(lane_rows)!=len(expected_search_lanes) or set(lane_names)!=set(expected_search_lanes) or any(status not in expected_lane_statuses for status in lane_statuses): errors.append("generated problem state must preserve one complete machine-audited status for every active discovery search lane")
    if generator_schema >= "2.5":
        last_lane_search=lane_search.get("last_completed_lane_search") or {}
        if generator_policy.get("last_completed_lane_search_is_portable_zero_authority_receipt") is not True or generator_policy.get("terminal_zero_call_skip_preserves_last_completed_lane_search") is not True: errors.append("problem generator must preserve the last completed lane search only as a portable zero-authority receipt")
        if last_lane_search:
            last_rows=[row for row in last_lane_search.get("lane_search") or [] if isinstance(row,dict)];last_priority=[str(x or "") for x in last_lane_search.get("lane_search_priority") or []]
            if last_lane_search.get("scientific_authority") is not False or not str(last_lane_search.get("run_id") or "") or len(last_rows)!=len(expected_search_lanes) or set(last_priority)!=set(expected_search_lanes) or [str(row.get("lane") or "") for row in last_rows]!=last_priority or any(str(row.get("status") or "") not in expected_lane_statuses for row in last_rows): errors.append("last completed lane-search receipt is invalid")
        if generator.get("status") in generated_discovery_statuses and (not last_lane_search or str(last_lane_search.get("run_id") or "")!=str(generator.get("run_id") or "")): errors.append("generated problem state must refresh the last completed lane-search receipt")
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
    if generator.get("status") == "GENERATED_AWAIT_PROBLEM_GATE" and int(generator_summary.get("written_to_auto_inbox") or 0) != int(generator_summary.get("generated") or 0): errors.append("generated candidates must be written completely to the auto inbox before gate audit")
    problem_queue = state.get("paper_first_problem_gate_queue") or {}; problem_queue_summary = problem_queue.get("summary") or {}; problem_queue_policy = problem_queue.get("policy") or {}
    if problem_queue_summary.get("audited") != problem_queue_summary.get("submitted") or int(problem_queue_summary.get("passed_problem_gate") or 0) + int(problem_queue_summary.get("blocked_problem_gate") or 0) != int(problem_queue_summary.get("audited") or 0) or problem_queue_summary.get("inbox_errors") != 0: errors.append("paper-first problem gate queue accounting/inbox error")
    if problem_queue_policy.get("all_candidates_require_problem_gate") is not True or problem_queue_policy.get("problem_gate_pass_only_grants_human_paper_design_eligibility") is not True or problem_queue_policy.get("verified_primary_evidence_registry_required_for_submitted_candidates") is not True or problem_queue_policy.get("multi_lane_candidate_schema_required") is not True or problem_queue_policy.get("lane_contract_independent_review_required") is not True or problem_queue_policy.get("independent_semantic_reduction_review_required") is not True or problem_queue_policy.get("semantic_reviewer_is_block_only") is not True or problem_queue_summary.get("method_authorized") != 0 or problem_queue_summary.get("experiment_authorized") != 0 or problem_queue_summary.get("p0_authorized") != 0: errors.append("paper-first problem queue must require primary provenance + multi-lane contract + block-only semantic review and grant only paper-design eligibility")
    sp_design = state.get("paper_first_search_portfolio_design_adjudication") or {}; sp_design_summary = sp_design.get("summary") or {}; sp_design_policy = sp_design.get("policy") or {}
    if (sp_design_summary.get("reviewed"),sp_design_summary.get("advance_to_method_design"),sp_design_summary.get("revise_paper_problem"),sp_design_summary.get("stop_standalone")) != (2,0,1,1) or any(int(sp_design_summary.get(key) or 0) != 0 for key in ("method_design_authorized","experiment_blueprint_authorized","local_validation_authorized","p0_authorized","gpu_authorized")) or sp_design_policy.get("source_is_shadow_search_portfolio") is not True or sp_design_policy.get("shadow_queue_has_zero_paper_design_authority") is not True or sp_design_policy.get("cannot_grant_or_revoke_live_paper_design_authority") is not True: errors.append("Search Portfolio retrospective design audit must route SP-09/SP-15 as 0 method advance / 1 revise / 1 stop while remaining shadow-only and zero-authority")
    errors.extend(f"Search Portfolio design adjudication: {error}" for error in validate_search_portfolio_design_adjudication(sp_design))
    try:
        persisted_sp_design = json.loads(SEARCH_PORTFOLIO_DESIGN_JSON.read_text(encoding="utf-8"))
    except Exception:
        errors.append("research-system embedded Search Portfolio state cannot verify current durable artifact")
    else:
        sp_compare = _canonicalize_public_state_locations(sp_design)
        persisted_sp_compare = _canonicalize_public_state_locations(persisted_sp_design)
        if (
            sp_compare.get("shadow_search_memory") != persisted_sp_compare.get("shadow_search_memory")
            or sp_compare.get("shadow_dead_end_memory") != persisted_sp_compare.get("shadow_dead_end_memory")
            or (sp_compare.get("summary") or {}) != (persisted_sp_compare.get("summary") or {})
            or sp_compare.get("rows") != persisted_sp_compare.get("rows")
        ):
            errors.append("research-system embedded Search Portfolio state is stale versus current durable artifact")
    sp15_support = state.get("paper_first_sp15_identifiability_support") or {}; sp15_summary = sp15_support.get("summary") or {}; sp15_policy = sp15_support.get("policy") or {}; sp15_diagnosis=sp15_support.get("support_diagnosis") or {}
    if sp15_summary.get("query_level_identifiability_units") != 0 or sp15_summary.get("support_status") != "INSUFFICIENT_FOR_IDENTIFIABILITY_CLAIM" or sp15_support.get("decision") != "HOLD_SP15_REVISED_PROBLEM_NO_IDENTIFIABILITY_UNIT" or sp15_policy.get("phenomenon_support_is_not_identifiability_support") is not True or (sp15_diagnosis.get("stop_class"),sp15_diagnosis.get("failure_layer"),sp15_diagnosis.get("failure_subtype")) != ("SUPPORT_STOP","experiment_identifiability","NO_MATCHED_QUERY_IDENTIFIABILITY_UNIT") or sp15_diagnosis.get("principle_dead_end_certified") is not False or sp15_diagnosis.get("principle_update_allowed") is not False or any(int(sp15_summary.get(key) or 0) != 0 for key in ("method_design_authorized","experiment_blueprint_authorized","local_validation_authorized","p0_authorized","gpu_authorized")): errors.append("SP-15 revised identifiability problem must remain a typed experiment-identifiability SUPPORT_STOP/reopenable hold with zero principle-dead-end or downstream authority until nonzero matched query-level support exists")
    support_release_watch=state.get("paper_first_support_release_watch") or {};support_release_policy=support_release_watch.get("policy") or {};support_release_summary=support_release_watch.get("summary") or {};support_release_status=str(support_release_watch.get("status") or "NOT_RUN")
    if support_release_watch:
        support_primary_refresh_present="primary_declaration_refresh_checked" in support_release_summary
        support_primary_refresh_boundary_ok=(not support_primary_refresh_present) or (support_release_policy.get("no_endpoint_primary_refresh_is_primary_source_only") is True and support_release_policy.get("primary_declaration_refresh_has_zero_source_exposure_effect") is True and support_release_policy.get("primary_declaration_refresh_cannot_qualify_support") is True)
        if support_release_watch.get("scientific_authority") is not False or support_release_policy.get("primary_declared_or_support_audited_release_endpoints_only") is not True or support_release_policy.get("support_audited_pre_f0_repository_targets_allowed") is not True or support_release_policy.get("pre_f0_release_change_only_holds_included") is not True or support_release_policy.get("related_work_repository_links_are_not_watch_targets") is not True or support_release_policy.get("release_surface_change_only_requests_recheck") is not True or support_release_policy.get("release_watch_cannot_mark_support_qualified") is not True or support_release_policy.get("release_watch_cannot_reopen_generator_or_problem_gate") is not True or support_release_policy.get("release_watch_has_zero_source_exposure_effect") is not True or support_release_policy.get("network_checks_are_cooldown_bounded") is not True or support_primary_refresh_boundary_ok is not True or support_release_policy.get("public_summary_excludes_urls_refs_required_units_and_private_paths") is not True:
            errors.append("support release watch public state must remain primary-declared-or-support-audited, bounded, redacted, and zero-authority")
        if support_release_status not in {"NOT_RUN","SUPPORT_RELEASE_WATCH_COMPLETE","SUPPORT_RELEASE_WATCH_PARTIAL","STATE_UNREADABLE","STATE_INVALID"}:
            errors.append("support release watch status invalid")
        if int(support_release_summary.get("support_qualified") or 0)!=0 or int(support_release_summary.get("generator_reopen_authorized") or 0)!=0 or int(support_release_summary.get("problem_gate_authorized") or 0)!=0:
            errors.append("support release watch cannot authorize support, Generator reopen, or Problem Gate")
        if any(key in support_release_watch for key in ("rows","url","source_refs","required_unit","reopen_only_if")):
            errors.append("support release watch public state cannot expose URLs, refs, required units, or private rows")
    support_asset_recheck=state.get("paper_first_support_asset_recheck_queue") or {};support_asset_policy=support_asset_recheck.get("policy") or {};support_asset_summary=support_asset_recheck.get("summary") or {};support_asset_status=str(support_asset_recheck.get("status") or "NOT_RUN")
    if support_asset_recheck:
        resolution_present=("resolved" in support_asset_summary) or support_asset_policy.get("asset_resolution_must_bind_latest_trigger_digest") is True
        resolution_policy_ok=(not resolution_present) or (support_asset_policy.get("asset_resolution_must_bind_latest_trigger_digest") is True and support_asset_policy.get("asset_resolution_cannot_mark_support_qualified_or_reopen") is True and support_asset_policy.get("support_inventory_recheck_remains_queue_handoff_not_resolution") is True)
        if support_asset_recheck.get("scientific_authority") is not False or support_asset_policy.get("release_change_only_creates_asset_recheck_task") is not True or support_asset_policy.get("queue_is_durable_across_release_watch_cooldown") is not True or support_asset_policy.get("queue_only_tracks_current_support_holds") is not True or support_asset_policy.get("queue_cannot_mark_support_qualified") is not True or support_asset_policy.get("queue_cannot_reopen_generator_or_problem_gate") is not True or support_asset_policy.get("queue_cannot_authorize_method_experiment_p0_gpu") is not True or support_asset_policy.get("explicit_asset_resolution_required_to_clear_entry") is not True or resolution_policy_ok is not True or support_asset_policy.get("automatic_provider_calls_authorized") is not False or support_asset_policy.get("public_summary_excludes_entries_refs_urls_required_units_and_private_paths") is not True:
            errors.append("support asset recheck queue must remain durable private-task accounting with zero scientific authority")
        if support_asset_status not in {"NOT_RUN","SUPPORT_ASSET_RECHECK_QUEUE_EMPTY","SUPPORT_ASSET_RECHECK_QUEUE_READY","STATE_UNREADABLE","STATE_INVALID"}:
            errors.append("support asset recheck queue status invalid")
        if any(int(support_asset_summary.get(key) or 0)!=0 for key in ("support_qualified","generator_reopen_authorized","problem_gate_authorized","method_authorized","experiment_authorized","p0_authorized","gpu_authorized")):
            errors.append("support asset recheck queue cannot authorize support, Generator, Problem Gate, or downstream execution")
        if any(key in support_asset_recheck for key in ("entries","candidate_id","source_refs","url","required_unit","reopen_only_if")):
            errors.append("support asset recheck public state cannot expose private queue entries, refs, URLs, or required units")
    support_asset_handoff=state.get("paper_first_support_asset_recheck_handoff") or {};support_handoff_policy=support_asset_handoff.get("policy") or {};support_handoff_summary=support_asset_handoff.get("summary") or {};support_handoff_status=str(support_asset_handoff.get("status") or "NOT_RUN")
    if support_asset_handoff:
        if support_asset_handoff.get("scientific_authority") is not False or support_handoff_policy.get("handoff_reuses_existing_problem_falsifier_support_inventory") is not True or support_handoff_policy.get("asset_recheck_cannot_define_a_parallel_support_gate") is not True or support_handoff_policy.get("release_change_is_not_support_qualification") is not True or support_handoff_policy.get("support_inventory_receipt_required_before_any_support_decision") is not True or support_handoff_policy.get("problem_falsifier_preflight_remains_support_authority_boundary") is not True or support_handoff_policy.get("handoff_cannot_execute_falsifier_automatically") is not True or support_handoff_policy.get("handoff_cannot_reopen_generator_or_problem_gate") is not True or support_handoff_policy.get("handoff_cannot_authorize_method_experiment_p0_gpu") is not True or support_handoff_policy.get("automatic_provider_calls_authorized") is not False or support_handoff_policy.get("public_summary_excludes_entries_refs_urls_required_units_and_private_paths") is not True:
            errors.append("support asset handoff must reuse existing support-inventory/preflight with zero execution authority")
        if support_handoff_status not in {"NOT_RUN","SUPPORT_ASSET_RECHECK_HANDOFF_EMPTY","SUPPORT_ASSET_RECHECK_HANDOFF_READY","SUPPORT_ASSET_RECHECK_HANDOFF_HOLD_PROVENANCE","STATE_UNREADABLE","STATE_INVALID"}:
            errors.append("support asset handoff status invalid")
        queued=int(support_handoff_summary.get("queued_asset_rechecks") or 0);ready=int(support_handoff_summary.get("support_inventory_recheck_ready") or 0);incomplete=int(support_handoff_summary.get("provenance_incomplete") or 0)
        if queued!=int(support_asset_summary.get("queued") or 0) or ready+incomplete!=queued:
            errors.append("support asset handoff accounting must match durable queue and partition ready/provenance-hold entries")
        if any(int(support_handoff_summary.get(key) or 0)!=0 for key in ("automatic_execution_authorized","provider_calls_authorized","support_qualified","falsifier_execution_authorized","generator_reopen_authorized","problem_gate_authorized","method_authorized","experiment_authorized","p0_authorized","gpu_authorized")):
            errors.append("support asset handoff cannot authorize provider, support, falsifier, reopen, or downstream execution")
        if any(key in support_asset_handoff for key in ("entries","candidate_id","queue_id","source_refs","required_unit","reopen_only_if","source_run_id")):
            errors.append("support asset handoff public state cannot expose private queue/provenance/support-contract material")
    shadow_search_admission=state.get("paper_first_shadow_search_admission") or {}
    errors.extend(f"Shadow Search admission: {error}" for error in validate_shadow_search_admission(shadow_search_admission))
    try:
        persisted_shadow_admission = json.loads(SHADOW_SEARCH_ADMISSION_JSON.read_text(encoding="utf-8"))
    except Exception:
        errors.append("research-system embedded Shadow Search admission cannot verify current durable artifact")
    else:
        if any(
            shadow_search_admission.get(key) != persisted_shadow_admission.get(key)
            for key in ("status","reason","policy","summary","source_identity","scientific_authority")
        ):
            errors.append("research-system embedded Shadow Search admission is stale versus current durable artifact")
    shadow_continuation=state.get("paper_first_shadow_continuation_frontier") or {}
    if shadow_continuation:
        errors.extend(f"Shadow continuation frontier: {error}" for error in validate_shadow_continuation_frontier(shadow_continuation))
        expected_frontier=build_shadow_continuation_frontier(admission=shadow_search_admission,support_watch=support_release_watch,asset_queue=support_asset_recheck,support_handoff=support_asset_handoff)
        if shadow_continuation.get("status")!=expected_frontier.get("status") or shadow_continuation.get("next_control_action")!=expected_frontier.get("next_control_action") or (shadow_continuation.get("summary") or {})!=(expected_frontier.get("summary") or {}) or (shadow_continuation.get("source_status") or {})!=(expected_frontier.get("source_status") or {}):
            errors.append("shadow continuation frontier must equal the deterministic projection of current admission/watch/queue/handoff state")
    evidence_migration=state.get("paper_first_evidence_migration") or {}
    if evidence_migration:
        errors.extend(f"Legacy evidence migration: {error}" for error in validate_public_migration(evidence_migration))
        if any(key in evidence_migration for key in ("machine_projection","evidence_plan","source_run_path","private_out")): errors.append("legacy evidence migration public state cannot expose private candidate or path material")
    asset_first_stri=state.get("asset_first_stri_paper_ready") or {}
    errors.extend(f"Asset-first STRI paper-ready: {error}" for error in validate_asset_first_stri_public_status(asset_first_stri))
    if int((asset_first_stri.get("summary") or {}).get("canonical_problem_gate_pass_added") or 0)!=0 or int((asset_first_stri.get("summary") or {}).get("canonical_generator_candidates_added") or 0)!=0 or int((asset_first_stri.get("summary") or {}).get("canonical_queue_candidates_added") or 0)!=0:
        errors.append("asset-first STRI paper-ready track cannot mutate canonical discovery accounting")
    discovery_frontier=state.get("paper_first_discovery_frontier") or {}
    if discovery_frontier:
        errors.extend(f"Paper-first discovery frontier: {error}" for error in validate_paper_first_discovery_frontier(discovery_frontier))
        expected_discovery_frontier=build_paper_first_discovery_frontier(
            primary_state=state.get("paper_first_primary_evidence") or {},
            generator_state=state.get("paper_first_problem_generator") or {},
            queue_state=state.get("paper_first_problem_gate_queue") or {},
            relation_freshness_state=state.get("paper_first_global_relation_freshness") or {},
            relation_admission_state=state.get("paper_first_global_relation_scan_admission") or {},
            shadow_admission_state=state.get("paper_first_shadow_search_admission") or {},
            object_candidate_state=state.get("paper_first_scientific_object_candidate_evidence") or {},
            support_release_watch_state=state.get("paper_first_support_release_watch") or {},
            support_asset_recheck_state=state.get("paper_first_support_asset_recheck_queue") or {},
            shadow_portfolio_state=state.get("paper_first_problem_search_portfolio") or {},
            evidence_migration_state=state.get("paper_first_evidence_migration") or {},
        )
        if any(discovery_frontier.get(key)!=expected_discovery_frontier.get(key) for key in ("status","policy","summary","blockers","triggers")):
            errors.append("paper-first discovery frontier must equal the deterministic projection of embedded control states")
    fresh_phenomenon_portfolio=state.get("paper_first_fresh_phenomenon_portfolio") or {}
    if fresh_phenomenon_portfolio:
        errors.extend(f"Fresh phenomenon portfolio: {error}" for error in validate_fresh_phenomenon_portfolio(fresh_phenomenon_portfolio))
        fresh_summary=fresh_phenomenon_portfolio.get("summary") or {}
        if int(fresh_summary.get("canonical_problem_gate_added") or 0)!=0 or any(int(fresh_summary.get(key) or 0)!=0 for key in ("method_authorized","experiment_authorized","p0_authorized","gpu_authorized")):
            errors.append("fresh phenomenon portfolio cannot mutate canonical or downstream scientific authority")
        try:
            persisted_fresh = json.loads(FRESH_PHENOMENON_PORTFOLIO_JSON.read_text(encoding="utf-8"))
        except Exception:
            errors.append("research-system embedded Fresh Phenomenon Portfolio cannot verify current durable artifact")
        else:
            if any(
                fresh_phenomenon_portfolio.get(key) != persisted_fresh.get(key)
                for key in ("status","policy","summary","candidates","source_bindings","scientific_authority")
            ):
                errors.append("research-system embedded Fresh Phenomenon Portfolio is stale versus current durable artifact")
    shadow_portfolio=state.get("paper_first_problem_search_portfolio") or {};shadow_latest=shadow_portfolio.get("latest_run") or {}
    if shadow_latest:
        latest_policy=shadow_latest.get("policy") or {};latest_summary=shadow_latest.get("summary") or {};latest_authority=shadow_latest.get("authority") or {}
        if shadow_portfolio.get("scientific_authority") is not False or (shadow_portfolio.get("policy") or {}).get("shadow_only") is not True: errors.append("Search Portfolio public state must remain shadow-only and zero-authority")
        if shadow_latest.get("scientific_authority") is not False or latest_policy.get("shadow_only") is not True or latest_policy.get("canonical_primary_generator_queue_untouched") is not True or latest_policy.get("live_source_coverage_effect") is not False: errors.append("latest Search Portfolio run must remain shadow-only without canonical source/queue effects")
        if latest_policy.get("current_source_web_receipt_required_after_semantic_clear") is not True or latest_policy.get("missing_or_failed_current_source_reviewer_is_not_pass") is not True: errors.append("semantic CLEAR in shadow search must require fail-closed current-source review")
        if latest_policy.get("source_identity_is_bounded_timestamp_and_sha_provenance") is True:
            source_set_sha=str(shadow_latest.get("source_set_sha256") or "");source_content_sha=str(shadow_latest.get("source_primary_content_sha256") or "");source_pool_sha=str(shadow_latest.get("source_pool_sha256") or "")
            if not str(shadow_latest.get("source_generated_at") or "") or len(source_set_sha)!=64 or any(ch not in "0123456789abcdef" for ch in source_set_sha) or len(source_content_sha)!=64 or any(ch not in "0123456789abcdef" for ch in source_content_sha) or (source_pool_sha and (len(source_pool_sha)!=64 or any(ch not in "0123456789abcdef" for ch in source_pool_sha))): errors.append("latest shadow source identity provenance invalid")
        if latest_policy.get("control_snapshot_bound_run") is True:
            control_sha=str(shadow_latest.get("control_snapshot_sha256") or "");qualification_commit=str(shadow_latest.get("qualification_main_commit") or "")
            if str(shadow_latest.get("stage_runner_required_schema") or "") not in {"1.4","1.5"} or len(control_sha)!=64 or any(ch not in "0123456789abcdef" for ch in control_sha) or len(qualification_commit)!=40 or any(ch not in "0123456789abcdef" for ch in qualification_commit) or latest_policy.get("control_snapshot_provenance_is_bounded_sha_only") is not True or latest_policy.get("control_snapshot_terminal_provenance_verified") is not True: errors.append("qualified shadow run must expose bounded schema-1.4/1.5 control snapshot provenance through terminal gate")
        if str(shadow_latest.get("schema_version") or "") >= "1.1-shadow-run":
            if latest_policy.get("execution_loss_is_not_scientific_negative") is not True or latest_policy.get("problem_falsifier_hold_is_not_scientific_fail") is not True: errors.append("latest shadow run must distinguish execution loss and falsifier HOLD from scientific negatives")
            if int(latest_summary.get("expansion_successful_shards") or 0)+int(latest_summary.get("expansion_execution_failures") or 0)!=int(latest_summary.get("expansion_requested_shards") or 0): errors.append("shadow expansion execution accounting mismatch")
            if int(latest_summary.get("formulation_successful_shards") or 0)+int(latest_summary.get("formulation_provider_failures") or 0)+int(latest_summary.get("formulation_parse_failures") or 0)!=int(latest_summary.get("formulation_requested_shards") or 0): errors.append("shadow formulation shard accounting mismatch")
            if int(latest_summary.get("formulation_successful_branches") or 0)+int(latest_summary.get("formulation_execution_censored_branches") or 0)>int(latest_summary.get("formulation_requested_branches") or 0): errors.append("shadow formulation branch accounting exceeds requested budget")
            if "formulation_reduction_pending" in latest_summary or "machine_reduction_pending" in latest_summary:
                if latest_policy.get("formulation_reduction_pending_is_not_scientific_block_or_pass") is not True or latest_policy.get("machine_rechecks_reduction_pending_before_problem_falsifier") is not True: errors.append("shadow reduction-pending route must remain zero-authority and independently rechecked")
                if int(latest_summary.get("machine_reduction_pending") or 0)!=int(latest_summary.get("problem_falsifier_eligible") or 0): errors.append("machine reduction-pending and problem-falsifier eligibility must match")
            falsifier_eligible=int(latest_summary.get("problem_falsifier_eligible") or 0);falsifier_resolved=int(latest_summary.get("problem_falsifier_support_qualified") or 0)+int(latest_summary.get("problem_falsifier_hold_support_unavailable") or 0)
            if int(latest_summary.get("problem_falsifier_executed") or 0)>int(latest_summary.get("problem_falsifier_support_qualified") or 0): errors.append("shadow problem-falsifier execution exceeds support-qualified units")
            if latest_policy.get("problem_falsifier_preflight_must_cover_all_eligible_before_terminal_complete") is True:
                if shadow_latest.get("status")=="SHADOW_TERMINAL_COMPLETE" and falsifier_resolved!=falsifier_eligible: errors.append("completed shadow terminal requires complete problem-falsifier preflight coverage")
                if shadow_latest.get("status")=="SHADOW_TERMINAL_INCOMPLETE_PROBLEM_FALSIFIER_PREFLIGHT" and not (0<=falsifier_resolved<falsifier_eligible): errors.append("problem-falsifier-incomplete terminal status requires unresolved eligible queue")
            elif latest_policy.get("support_inventory_is_one_evidence_route_not_global_prerequisite") is not True and falsifier_resolved!=falsifier_eligible: errors.append("shadow problem-falsifier preflight accounting mismatch")
            if "provisional_problem_candidates" in latest_summary:
                evidence_open=sum(int(latest_summary.get(key) or 0) for key in ("evidence_design_pending","evidence_operationalization_recompile_pending","evidence_review_pending","evidence_substrate_preflight_pending","evidence_harness_implementation_pending","evidence_execution_ready","evidence_residual_survives","evidence_branch_repair_ready"))
                if latest_policy.get("reduction_pending_enters_bounded_evidence_acquisition_on_future_control_snapshots") is not True or latest_policy.get("evidence_acquisition_authority_is_not_scientific_claim_authority") is not True or latest_policy.get("evidence_residual_survival_requires_semantic_and_current_source_review") is not True: errors.append("future shadow reduction-pending route must separate bounded evidence acquisition from scientific certification")
                if int(latest_summary.get("provisional_problem_candidates") or 0)!=int(latest_summary.get("problem_falsifier_eligible") or 0): errors.append("provisional evidence portfolio must cover every exact-reduction-pending candidate")
                if int(latest_summary.get("evidence_execution_completed") or 0)<int(latest_summary.get("evidence_reduction_supported") or 0)+int(latest_summary.get("evidence_residual_survives") or 0): errors.append("evidence outcome accounting exceeds completed bounded executions")
                if shadow_latest.get("status")=="SHADOW_EVIDENCE_ACQUISITION_PENDING" and evidence_open<=0: errors.append("evidence-acquisition-pending status requires open bounded evidence work")
                if shadow_latest.get("status")=="SHADOW_TERMINAL_COMPLETE" and evidence_open>0: errors.append("completed shadow terminal cannot retain open bounded evidence work")
                if int(latest_summary.get("evidence_residual_survives") or 0)>0 and shadow_latest.get("status")=="SHADOW_TERMINAL_COMPLETE": errors.append("bounded residual survival must return to semantic/current-source review before terminal completion")
        if int(latest_summary.get("terminal_shadow_survivors") or 0)!=int(latest_summary.get("current_source_clear") or 0) or int(latest_summary.get("live_paper_design_eligible") or 0)!=0: errors.append("shadow terminal survivors must equal current-source CLEAR and never grant live Paper Design eligibility")
        if shadow_latest.get("status")=="SHADOW_TERMINAL_COMPLETE" and int(latest_summary.get("current_source_missing") or 0)!=0: errors.append("completed shadow terminal cannot have missing current-source reviews")
        if any(latest_authority.get(key) is not False for key in ("live_problem_gate","paper_design","method","experiment","p0","gpu")): errors.append("latest shadow run cannot authorize live Problem Gate or downstream execution")
    paper_backlog=state.get("paper_first_paper_design_backlog") or {};backlog_policy=paper_backlog.get("policy") or {};backlog_summary=paper_backlog.get("summary") or {};backlog_entries=[row for row in paper_backlog.get("entries") or [] if isinstance(row,dict)]
    if paper_backlog.get("status")!="NOT_RUN":
        if backlog_policy.get("problem_gate_pass_is_durable_until_human_paper_design_resolution") is not True or backlog_policy.get("volatile_discovery_queue_cannot_erase_backlog") is not True or backlog_policy.get("paper_design_eligibility_is_not_method_authority") is not True: errors.append("Problem-Gate PASS must persist in a durable Paper-Design backlog without downstream authority")
        if any(backlog_policy.get(key) is not False for key in ("automatic_method_authority","automatic_experiment_authority","automatic_p0_authority","automatic_gpu_authority")) or any(int(backlog_summary.get(key) or 0)!=0 for key in ("method_authorized","experiment_authorized","p0_authorized","gpu_authorized")): errors.append("Paper-Design backlog cannot authorize method, experiment, P0, or GPU")
        if int(backlog_summary.get("pending_human_paper_design") or 0)!=sum(row.get("status")=="AWAIT_HUMAN_PAPER_DESIGN_REVIEW" for row in backlog_entries): errors.append("Paper-Design backlog pending accounting mismatch")
        current_pass_ids={str(row.get("candidate_id") or "") for row in problem_queue.get("passed") or [] if isinstance(row,dict)};backlog_candidate_ids={str(row.get("candidate_id") or "") for row in backlog_entries}
        if not current_pass_ids.issubset(backlog_candidate_ids): errors.append("current Problem-Gate PASS candidates must be represented in the durable Paper-Design backlog")
    relation=state.get("paper_first_global_relation_recall") or {};relation_policy=relation.get("policy") or {};relation_summary=relation.get("summary") or {};relation_coverage=relation.get("relation_coverage") or {};relation_status=str(relation.get("status") or "NOT_RUN");relation_schema=str(relation.get("schema_version") or "0")
    allowed_relation_statuses={"NOT_RUN","SKIPPED_SOURCE_COVERAGE_OPEN","SKIPPED_PAIR_COVERAGE_COMPLETE","HOLD_RELATION_CACHE_INCOMPLETE","HOLD_RELATION_DELTA_BOUNDARY_UNRECONSTRUCTABLE","SKIPPED_RELATION_NO_NEW_SOURCE_ENDPOINTS","RELATION_PROVIDER_ERROR_ZERO_AUTHORITY","LANE_REVIEW_ERROR_ZERO_AUTHORITY","REDUCTION_REVIEW_ERROR_ZERO_AUTHORITY","GLOBAL_RELATION_RECALL_COMPLETE","SKIPPED_RELATION_UNIVERSE_UNCHANGED","STATE_UNREADABLE","STATE_INVALID"}
    if relation_status not in allowed_relation_statuses: errors.append("Global Relation Recall status invalid")
    if relation_status not in {"NOT_RUN","STATE_UNREADABLE","STATE_INVALID"}:
        if relation_policy.get("source_coverage_exhaustion_is_not_relation_exhaustion") is not True or relation_policy.get("relation_miner_is_search_control_only") is not True or relation_policy.get("cross_source_recall_supplements_but_does_not_replace_search_portfolio") is not True or relation_policy.get("all_lane_pass_proposals_require_reduction_review") is not True or relation_policy.get("not_reduced_only_reopens_focused_problem_generator") is not True: errors.append("Global Relation Recall must remain a zero-authority cross-source supplement after Search Portfolio")
        if any(relation_policy.get(key) is not False for key in ("automatic_problem_gate_authority","automatic_method_authority","automatic_experiment_authority","automatic_p0_authority")): errors.append("Global Relation Recall cannot authorize Problem Gate, method, experiment, or P0")
        if relation_coverage.get("scientific_authority") is not False or relation.get("scientific_authority") is not False: errors.append("Global relation coverage/recall cannot carry scientific authority")
        execution=relation.get("execution_control") or {}
        if execution:
            if execution.get("scientific_authority") is not False or execution.get("status")!="LANE_REVIEW_EXACT_RETRY_EXHAUSTED" or execution.get("stage")!="lane_review" or execution.get("retry_budget_exhausted") is not True or int(execution.get("provider_attempts") or 0)!=int(execution.get("exact_retry_limit") or 0)+1 or len(str(execution.get("relation_universe_digest") or ""))!=64 or len(str(execution.get("relation_raw_sha256") or ""))!=64:
                errors.append("Global Relation Recall execution-retry exhaustion receipt invalid")
            contract_sha=str(execution.get("lane_review_execution_contract_sha256") or "")
            if len(contract_sha)!=64 or any(ch not in "0123456789abcdef" for ch in contract_sha):
                errors.append("Global Relation Recall exhausted lane-review execution-contract digest invalid")
            # A receipt for an older versioned execution contract remains valid history.
            # Retry exhaustion applies only when admission compares that digest to the
            # current contract; a changed digest neither blocks nor authorizes a scan.
            if relation_status!="LANE_REVIEW_ERROR_ZERO_AUTHORITY":
                errors.append("Global Relation Recall retry exhaustion requires a lane-review execution error state")
        if int(relation_summary.get("reduction_reviewed") or 0)!=int(relation_summary.get("lane_pass") or 0): errors.append("every lane-PASS global relation proposal must receive reduction review")
        if bool(relation_summary.get("focused_problem_generator_reopen_required"))!=(int(relation_summary.get("not_reduced") or 0)>0): errors.append("focused problem-generator reopen must be equivalent to a NOT_REDUCED global relation residual")
        if relation_status in {"GLOBAL_RELATION_RECALL_COMPLETE","SKIPPED_RELATION_UNIVERSE_UNCHANGED"}:
            last_scan=relation.get("last_completed_scan") or {}
            if not str(last_scan.get("run_id") or "") or last_scan.get("scientific_authority") is not False or str(last_scan.get("relation_universe_digest") or "")!=str(relation_summary.get("relation_universe_digest") or ""): errors.append("completed Global Relation Recall must preserve a matching zero-authority portable scan receipt")
        if relation_schema >= "1.2":
            if relation_policy.get("stale_completed_scan_uses_delta_only_new_endpoint_pairs") is not True or relation_policy.get("delta_only_scan_forbids_old_old_pairs") is not True:
                errors.append("Global Relation Recall 1.2 must constrain stale-universe scans to new-endpoint delta pairs")
            if relation_status=="GLOBAL_RELATION_RECALL_COMPLETE":
                writer_admission=relation.get("writer_admission") or {};writer_policy=writer_admission.get("policy") or {};writer_summary=writer_admission.get("summary") or {}
                if relation_policy.get("explicit_manual_writer_admission_required") is not True or writer_admission.get("scientific_authority") is not False or writer_policy.get("automatic_model_scan_authority") is not False or writer_policy.get("manual_execution_requires_explicit_operator_flag") is not True or writer_summary.get("manual_scan_eligible") is not True or writer_summary.get("automatic_model_scan_authorized") is not False:
                    errors.append("Global Relation Recall 1.2 completed scan requires explicit zero-authority manual writer admission")
            delta_scan=relation.get("delta_scan") or {}
            if delta_scan.get("enabled") is True:
                count=int(delta_scan.get("required_new_endpoint_count") or 0);digest=str(delta_scan.get("required_new_endpoint_digest") or "")
                if delta_scan.get("scientific_authority") is not False or count<=0 or len(digest)!=64 or any(ch not in "0123456789abcdef" for ch in digest):
                    errors.append("Global Relation Recall delta scan must expose bounded zero-authority new-endpoint provenance")
                if relation_status=="GLOBAL_RELATION_RECALL_COMPLETE":
                    last_scan=relation.get("last_completed_scan") or {}
                    if last_scan.get("mode")!="delta_only_new_endpoint" or int(last_scan.get("required_new_endpoint_count") or 0)!=count or not str(last_scan.get("prior_scan_run_id") or ""):
                        errors.append("completed delta-only relation scan must preserve prior-scan provenance and endpoint count")
    relation_freshness=state.get("paper_first_global_relation_freshness") or {};fresh_policy=relation_freshness.get("policy") or {};fresh_summary=relation_freshness.get("summary") or {}
    if relation_freshness:
        if relation_freshness.get("scientific_authority") is not False or fresh_policy.get("deterministic_digest_comparison_only") is not True or fresh_policy.get("stale_scan_is_historical_not_current_negative_evidence") is not True or fresh_policy.get("stale_scan_cannot_reopen_focused_generator") is not True or fresh_policy.get("model_scan_deferred_is_not_relation_exhaustion") is not True or fresh_policy.get("portable_review_receipts_are_scheduler_metadata_only") is not True or fresh_policy.get("scheduler_topology_only_drift_does_not_require_model_rescan") is not True or fresh_policy.get("source_set_change_or_unreconstructable_boundary_remains_stale") is not True:
            errors.append("Global Relation Recall freshness must remain deterministic zero-authority compute control and ignore scheduler-only topology drift")
        if bool(fresh_summary.get("universe_stale")) and (fresh_summary.get("current_not_reduced_unknown") is not True or fresh_summary.get("focused_problem_generator_reopen_allowed") is not False):
            errors.append("stale Global Relation Recall cannot support a current negative or focused-generator reopen")
        if str(relation_freshness.get("current_relation_universe_digest") or "") and len(str(relation_freshness.get("current_relation_universe_digest") or "")) != 64:
            errors.append("current relation-universe digest invalid")
        if str(relation_freshness.get("last_scanned_relation_universe_digest") or "") and len(str(relation_freshness.get("last_scanned_relation_universe_digest") or "")) != 64:
            errors.append("last scanned relation-universe digest invalid")
        for key in ("current_source_universe_digest","last_scanned_source_universe_digest"):
            value=str(relation_freshness.get(key) or "")
            if value and len(value)!=64: errors.append(f"{key} invalid")
        if fresh_summary.get("scheduler_topology_only_drift") is True:
            if relation_freshness.get("status")!="CURRENT_RELATION_UNIVERSE" or fresh_summary.get("raw_topology_digest_changed") is not True or fresh_summary.get("source_boundary_reconstructable") is not True or fresh_summary.get("universe_stale") is not False or fresh_summary.get("current_not_reduced_unknown") is not False or fresh_summary.get("model_scan_deferred") is not False or not str(relation_freshness.get("current_source_universe_digest") or "") or relation_freshness.get("current_source_universe_digest")!=relation_freshness.get("last_scanned_source_universe_digest"):
                errors.append("scheduler-only relation topology drift must remain current and zero-provider")
        expected_freshness=relation_recall_freshness(state.get("paper_first_problem_generator") or {}, relation)
        expected_summary=expected_freshness.get("summary") or {}
        freshness_summary_keys=("current_reviewed_sources","last_scanned_sources","current_possible_pairs","current_coobserved_pairs","current_pair_coverage_fraction","last_pair_coverage_fraction","current_relation_blind_spot","raw_topology_digest_changed","source_boundary_reconstructable","scheduler_topology_only_drift","universe_stale","current_not_reduced_unknown","model_scan_deferred","focused_problem_generator_reopen_allowed")
        freshness_matches=(
            relation_freshness.get("status")==expected_freshness.get("status")
            and str(relation_freshness.get("current_relation_universe_digest") or "")==str(expected_freshness.get("current_relation_universe_digest") or "")
            and str(relation_freshness.get("last_scanned_relation_universe_digest") or "")==str(expected_freshness.get("last_scanned_relation_universe_digest") or "")
            and str(relation_freshness.get("current_source_universe_digest") or "")==str(expected_freshness.get("current_source_universe_digest") or "")
            and str(relation_freshness.get("last_scanned_source_universe_digest") or "")==str(expected_freshness.get("last_scanned_source_universe_digest") or "")
            and all(fresh_summary.get(key)==expected_summary.get(key) for key in freshness_summary_keys)
        )
        if not freshness_matches:
            errors.append("Global Relation Recall freshness must match embedded Generator and Relation state")
    relation_delta=state.get("paper_first_global_relation_delta_preflight") or {};delta_policy=relation_delta.get("policy") or {};delta_summary=relation_delta.get("summary") or {};delta_status=str(relation_delta.get("status") or "NOT_RUN")
    if relation_delta and delta_status!="NOT_RUN":
        if relation_delta.get("scientific_authority") is not False or delta_policy.get("deterministic_typed_evidence_delta_only") is not True or delta_policy.get("pair_slots_are_not_lane_valid_pairs") is not True or delta_policy.get("cannot_reopen_generator") is not True or delta_policy.get("cannot_authorize_relation_model_scan") is not True or delta_policy.get("cannot_authorize_problem_gate") is not True:
            errors.append("relation delta preflight must remain deterministic zero-authority search control")
        if delta_summary.get("model_scan_authorized") is True or delta_summary.get("focused_generator_reopen_authorized") is True:
            errors.append("relation delta preflight cannot authorize model scan or focused generator reopen")
    relation_admission=state.get("paper_first_global_relation_scan_admission") or {};admission_policy=relation_admission.get("policy") or {};admission_summary=relation_admission.get("summary") or {};admission_status=str(relation_admission.get("status") or "HOLD_MANUAL_RELATION_SCAN");admission_schema=str(relation_admission.get("schema_version") or "0")
    if relation_admission:
        new_retry_policy_ok=admission_schema<"1.1" or admission_policy.get("same_relation_universe_lane_review_retry_exhaustion_blocks_repeat_scan") is True
        if relation_admission.get("scientific_authority") is not False or admission_policy.get("automatic_model_scan_authority") is not False or admission_policy.get("manual_execution_requires_explicit_operator_flag") is not True or admission_policy.get("manual_eligibility_is_not_scientific_authority") is not True or admission_policy.get("relation_scan_cannot_authorize_problem_gate") is not True or admission_policy.get("relation_scan_cannot_authorize_method_experiment_p0_gpu") is not True or admission_policy.get("preconditions_are_deterministic_search_control_only") is not True or not new_retry_policy_ok:
            errors.append("manual relation-scan admission must remain deterministic zero-authority execution precondition")
        if admission_summary.get("automatic_model_scan_authorized") is not False:
            errors.append("manual relation-scan admission cannot authorize model calls automatically")
        if (admission_status=="ELIGIBLE_FOR_EXPLICIT_MANUAL_RELATION_SCAN") != (admission_summary.get("manual_scan_eligible") is True):
            errors.append("manual relation-scan eligibility status/accounting mismatch")
        if admission_status=="HOLD_RELATION_REVIEW_RETRY_EXHAUSTED" and (admission_summary.get("relation_lane_review_retry_exhausted") is not True or admission_summary.get("manual_scan_eligible") is not False):
            errors.append("exhausted relation lane-review retry must block repeat manual scan")
    if (pf357_summary.get("reviewed"),pf357_summary.get("stopped_standalone"),pf357_summary.get("paper_design_authorized"),pf357_summary.get("local_validation_authorized")) != (3,3,0,0): errors.append("PF-3/PF-5/PF-7 must all terminate standalone before Paper Design/local validation")
    post_c2 = state.get("paper_first_post_c2") or {}; post_c2_auth = post_c2.get("authority") or {}
    if post_c2.get("decision") != "STOP_CURRENT_CONTROLLED_MEDIATOR_PAPER_MECHANISM" or post_c2_auth.get("clean_mechanism_stop") is not True: errors.append("post-C2 paper mechanism terminal adjudication must preserve the clean local falsifier STOP")
    if post_c2_auth.get("C3_locked") is not True or post_c2_auth.get("full_experiment_authorized") is not False: errors.append("post-C2 STOP must keep C3/full experiments locked")
    if post_c2_auth.get("new_method_auto_authorized") is not False or post_c2_auth.get("new_paper_problem_auto_authorized") is not False: errors.append("post-C2 STOP cannot auto-authorize a method or new paper problem")
    if (post_c2.get("gate_provenance") or {}).get("decision_invariant_to_later_gate_tightening") is not True: errors.append("post-C2 terminal state must report gate-version invariance")
    if (post_c2.get("decision_context_validity") or {}).get("pass") is not True: errors.append("post-C2 mechanism negative requires full decision-context validity")
    architecture = state.get("system_architecture") or {}; architecture_summary = architecture.get("summary") or {}
    if architecture_summary.get("temporal_stages") != len(TEMPORAL_FLOW) or architecture_summary.get("functional_layers") != 6: errors.append(f"backend architecture must expose one {len(TEMPORAL_FLOW)}-stage lifecycle and six functional layers")
    if architecture_summary.get("reader_chapters") != len(READING_GROUPS) or architecture_summary.get("reader_stage_coverage") != len(TEMPORAL_FLOW) or architecture_summary.get("reader_stage_missing") != 0 or architecture_summary.get("reader_stage_duplicates") != 0 or architecture_summary.get("reader_stage_extra") != 0: errors.append("system-overview reading groups must cover every canonical temporal stage exactly once")
    if architecture_summary.get("assigned_components") != len(state.get("components") or []) or architecture_summary.get("unassigned_components") != 0: errors.append("every backend component must have exactly one primary architecture layer")
    if architecture_summary.get("duplicate_component_keys") != 0: errors.append("backend component architecture keys must be unique")
    if architecture_summary.get("cross_cutting_controls") != 3 or architecture_summary.get("orphan_cross_cutting_controls") != 0: errors.append("all cross-cutting methodology controls must resolve to an existing owner component")
    paper_acceptance = state.get("paper_acceptance") or {}; pa_policy = paper_acceptance.get("policy") or {}; pa_summary = paper_acceptance.get("summary") or {}
    architecture_suffix = tuple(str(row.get("key") or "") for row in (architecture.get("temporal_flow") or [])[-len(PAPER_ACCEPTANCE_TEMPORAL_KEYS):])
    if tuple(paper_acceptance.get("temporal_keys") or []) != PAPER_ACCEPTANCE_TEMPORAL_KEYS or architecture_suffix != PAPER_ACCEPTANCE_TEMPORAL_KEYS: errors.append("Paper Acceptance flow must exactly match the post-evidence architecture suffix")
    if paper_acceptance.get("scientific_authority") is not False or any(pa_summary.get(key) != 0 for key in ("automatic_scientific_authority","automatic_experiment_authority","automatic_gpu_authority","automatic_submission_authority")): errors.append("Paper Acceptance must have zero automatic scientific, experiment, GPU, and submission authority")
    if pa_summary.get("paper_states") != len(PAPER_ACCEPTANCE_TEMPORAL_KEYS) or pa_summary.get("mandatory_manuscript_ci_checks") != 9 or pa_summary.get("append_only_ledger") is not True: errors.append("Paper Acceptance state/CI/ledger contract mismatch")
    if pa_policy.get("causal_hold_blocks_post_evidence_advancement") is not True or pa_policy.get("evidence_gap_blocks_post_evidence_advancement") is not True: errors.append("scientific evidence/causal holds must block paper optimization")
    if pa_policy.get("story_search_may_reframe_but_not_expand_supported_claims") is not True or pa_policy.get("new_claim_request_preserves_limitation_instead_of_claim_expansion") is not True: errors.append("paper optimization must not expand frozen scientific claims")
    if pa_policy.get("story_search_winner_required_for_manuscript") is not True or pa_policy.get("both_mock_pc_modes_required_for_targeted_repair") is not True or pa_policy.get("claim_audit_pass_required_for_pdf_qa") is not True: errors.append("Paper Acceptance transition receipts must hard-gate manuscript, targeted repair, and PDF QA")
    if pa_policy.get("manuscript_ci_fails_closed") is not True or pa_policy.get("submission_ready_requires_prebuttal_and_manuscript_ci") is not True or pa_policy.get("submitted_state_requires_external_human_submission_authority") is not True: errors.append("submission closure must fail closed behind CI, prebuttal, and external submission authority")
    ledger_index = paper_acceptance.get("ledger_index") or {}; ledger_policy = ledger_index.get("policy") or {}; ledger_summary = ledger_index.get("summary") or {}
    if ledger_index.get("scientific_authority") is not False or ledger_summary.get("invalid_ledgers") != 0: errors.append("Paper Acceptance ledger index must be valid and zero-authority")
    if ledger_policy.get("source_ledgers_are_append_only") is not True or ledger_policy.get("public_projection_excludes_raw_reviewer_prose") is not True or ledger_policy.get("public_projection_excludes_filesystem_paths_and_actors") is not True or ledger_policy.get("ledger_projection_has_zero_authority") is not True: errors.append("Paper Acceptance ledger public projection boundary is incomplete")
    expected_paper_summary = {
        "registered_papers": ledger_summary.get("papers"),
        "scientific_holds": ledger_summary.get("scientific_holds"),
        "ledger_submission_ready_papers": ledger_summary.get("submission_ready"),
        "submission_ready_papers": ledger_summary.get("submission_ready"),
        "gate_clean_submission_ready_papers": ledger_summary.get("gate_clean_submission_ready"),
        "paper_preparation_failed_papers": ledger_summary.get("paper_preparation_failed"),
        "immediate_submission_holds": ledger_summary.get("immediate_submission_holds"),
        "internal_action_required_papers": ledger_summary.get("internal_action_required"),
        "no_internal_action_papers": ledger_summary.get("no_internal_action"),
    }
    if any(pa_summary.get(key) != value for key, value in expected_paper_summary.items()): errors.append("Paper Acceptance ledger summary must match the canonical public index with explicit ledger/effective-readiness semantics")
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
    memory_wiki=state.get("research_memory_wiki") or {};memory_policy=memory_wiki.get("policy") or {};memory_lint=memory_wiki.get("lint") or {};memory_summary=memory_wiki.get("summary") or {}
    if memory_wiki.get("status")!="MEMORY_COMPILED" or memory_wiki.get("scientific_authority") is not False or int((memory_lint.get("summary") or {}).get("errors") or 0)!=0: errors.append("research memory wiki must compile with zero lint errors and zero scientific authority")
    if memory_policy.get("wiki_is_compiled_from_canonical_artifacts_not_a_second_source_of_truth") is not True or memory_policy.get("transient_operational_noise_is_not_prompt_eligible") is not True or memory_policy.get("query_pack_never_relaxes_downstream_gates") is not True: errors.append("research memory wiki must remain a derived zero-authority query-pack layer")
    if int(memory_summary.get("search_closures") or 0)+int(memory_summary.get("scientific_closures") or 0)!=len((((state.get("paper_first_search_portfolio_design_adjudication") or {}).get("shadow_search_memory") or {}).get("closed_objects") or [])): errors.append("research memory closure accounting must match canonical shadow search memory")
    if not state["experiment_value_scheduler"]["policy"]["scheduler_cannot_authorize_execution"]: errors.append("experiment value scheduler must remain advisory")
    if state["research_system_replay"]["summary"].get("failed") != 0: errors.append("research-system replay benchmark has failing epistemic cases")
    if not state["external_system_learning"]["policy"]["every_candidate_design_requires_local_gap_test"]: errors.append("external system designs require a local gap test before adoption")
    harness = state.get("research_harness_assurance") or {}; harness_summary = harness.get("summary") or {}
    portfolio = state.get("research_candidate_portfolio") or {}; portfolio_summary = portfolio.get("summary") or {}; portfolio_policy = portfolio.get("policy") or {}
    funnel = state.get("search_funnel_telemetry") or {}; funnel_policy = funnel.get("policy") or {}
    research_graph = state.get("scientific_research_graph") or {}; research_graph_policy = research_graph.get("policy") or {}; research_graph_summary = research_graph.get("summary") or {}
    if harness.get("status") != "PASS_HARNESS_ASSURANCE" or int(harness_summary.get("failed") or 0) != 0 or int(harness_summary.get("passed") or 0) != int(harness_summary.get("checks") or 0): errors.append("research harness assurance must pass every fan-out/jury/executor/claim/telemetry invariant")
    if portfolio.get("scientific_authority") is not False or portfolio_policy.get("portfolio_cannot_promote_candidate_stage") is not True or portfolio_policy.get("soft_capacity_targets_do_not_relax_scientific_thresholds") is not True or int(portfolio_summary.get("visible_candidates") or 0) != len(portfolio.get("rows") or []) or int(portfolio_summary.get("automatic_promotions") or 0) != 0: errors.append("persistent candidate portfolio must remain zero-authority capacity/persistence control")
    if funnel.get("scientific_authority") is not False or funnel_policy.get("typed_reduction_or_support_holds_must_not_be_reported_as_idea_generation_failure") is not True or funnel_policy.get("telemetry_cannot_authorize_provider_calls_problem_gate_method_experiment_p0_or_gpu") is not True: errors.append("search-funnel telemetry must remain zero-authority and preserve typed bottleneck semantics")
    if research_graph.get("scientific_authority") is not False or research_graph_policy.get("experiment_failure_edge_cannot_close_core_principle") is not True or research_graph_policy.get("only_certified_principle_dead_end_may_emit_principle_closure_edge") is not True or int(research_graph_summary.get("principle_closure_edges") or 0) != int(research_graph_summary.get("scientific_closure_nodes") or 0): errors.append("scientific research graph must preserve typed failure/closure authority boundaries")
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
    if (ledger.get("summary") or {}).get("failure_diagnosis_incomplete") != 0: errors.append("P0 decision ledger cannot publish failed/held rows without a complete failure-layer diagnosis")
    if (ledger.get("summary") or {}).get("failure_diagnosis_complete") != (ledger.get("summary") or {}).get("failure_diagnosis_required"): errors.append("P0 decision ledger failure diagnosis coverage must be complete")
    if (ledger.get("policy") or {}).get("failed_or_held_experiment_requires_failure_layer") is not True: errors.append("P0 decision ledger must require typed failure layers for failed/held experiments")
    if (ledger.get("policy") or {}).get("only_core_principle_layer_may_allow_principle_update") is not True: errors.append("P0 decision ledger must forbid lower failure layers from updating the core principle")
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
    write_asset_first_stri_paper_quality()
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
    write_skill_validation_transfer_scout()
    # Persistent search memory must be rebuilt before the fresh portfolio because
    # the latter content-addresses the former. Reversing this order guarantees a
    # one-generation stale dead-end-memory binding whenever a new principle closure
    # is compiled during the same release.
    write_search_portfolio_design_adjudication()
    write_fresh_phenomenon_portfolio()
    write_shadow_search_admission()
    write_sp15_identifiability_support()
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
    write_research_memory_wiki(redact_private_paths(state["research_memory_wiki"],storage=StorageSettings.from_env()))
    public_state=redact_private_paths(state,storage=StorageSettings.from_env())
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(public_state, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    js_path.write_text("window.RESEARCH_SYSTEM_STATE = "+json.dumps(public_state, ensure_ascii=False, separators=(",",":"))+";\n", encoding="utf-8")
    return state
