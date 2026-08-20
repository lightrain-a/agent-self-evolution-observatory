from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

SCHEMA_VERSION = "1.0"
POLICY = {
    "schema_version": SCHEMA_VERSION,
    "integration_lint_has_zero_scientific_authority": True,
    "declared_writer_requires_machine_verifiable_consumer": True,
    "passing_lint_is_not_scientific_acquittal": True,
    "source_wiring_and_receipt_fields_are_checked": True,
    "required_orphan_writer_is_release_blocker": True,
    "integration_lint_cannot_authorize_provider_or_scientific_actions": True,
}

CONTRACTS: tuple[dict[str, Any], ...] = (
    {"key":"research-memory-to-idea-search","producer":"research_pipeline/research_memory_wiki.py","consumer":"research_pipeline/paper_first_problem_generator.py","producer_anchors":("compile_research_memory_query_pack","query_pack_sha256"),"consumer_anchors":("compile_research_memory_query_pack",'purpose="IDEA_SEARCH"',"research_memory_query_receipt")},
    {"key":"research-memory-to-experiment-design","producer":"research_pipeline/research_memory_wiki.py","consumer":"research_pipeline/problem_search_stage_runner.py","producer_anchors":("compile_research_memory_query_pack","selected_memory_ids"),"consumer_anchors":('purpose="EXPERIMENT_DESIGN"',"query_pack_sha256","research_memory_selected_ids")},
    {"key":"failure-assets-to-research-memory","producer":"research_pipeline/failure_asset_library.py","consumer":"research_pipeline/research_memory_wiki.py","producer_anchors":("reusable_prechecks","reuse_effectiveness"),"consumer_anchors":("failure_asset_library","_failures(failure_asset_library)")},
    {"key":"typed-memory-graph-to-research-system","producer":"research_pipeline/scientific_research_graph.py","consumer":"research_pipeline/research_system.py","producer_anchors":("closure_propagation_requires_same_scientific_object_mechanism_and_claim_type","lint_scientific_research_graph","claim_conflicts"),"consumer_anchors":("research_memory_wiki=research_memory_wiki","claim_ledger=claim_ledger","scientific_research_graph")},
    {"key":"aris-governance-to-memory-graph","producer":"research_pipeline/research_governance_layer.py","consumer":"research_pipeline/scientific_research_graph.py","producer_anchors":("build_aris_governance_layer","governance_may_block_or_require_review_but_cannot_self_authorize","experiment_authorizations","candidate_lineage"),"consumer_anchors":("governance_layer: dict","governance_bindings","belief_authority","authorization_id","lineage_id")},
    {"key":"harness-assurance-to-research-system","producer":"research_pipeline/research_harness_assurance.py","consumer":"research_pipeline/research_system.py","producer_anchors":("build_research_harness_assurance","PASS_HARNESS_ASSURANCE"),"consumer_anchors":("build_research_harness_assurance",'"research_harness_assurance"')},
    {"key":"stall-pivot-to-automation-heartbeat","producer":"research_pipeline/research_stall_pivot_controller.py","consumer":"research_pipeline/automation_cycle.py","producer_anchors":("observe_research_stall","FORCE_STRUCTURAL_PIVOT","ESCALATE_HUMAN_REPLAN"),"consumer_anchors":("load_research_stall_state","observe_research_stall","research-stall-pivot")},
    {"key":"meta-optimization-proposer-to-landing-gate","producer":"research_pipeline/research_harness_meta_optimization.py","consumer":"research_pipeline/research_harness_meta_optimization.py","producer_anchors":("build_research_harness_meta_optimization","PROPOSED_NOT_APPLIED"),"consumer_anchors":("validate_meta_change_landing","explicit_human_approval","independent_reviewer_model_family")},
    {"key":"generic-evidence-receipt-compiler-to-agent-safety-adapter","producer":"research_pipeline/evidence_receipt_current_state.py","consumer":"research_pipeline/paper_first_agent_safety_current_projection.py","producer_anchors":("compile_evidence_receipt_projection","projection_payload_sha256","automatic_stage_transition"),"consumer_anchors":("GENERIC_PROJECTION_SPEC","compile_evidence_receipt_projection","receipt_compiler_projection")},
    {"key":"agent-safety-evidence-to-current-projection","producer":"research_pipeline/paper_first_agent_safety_r9_future_evidence.py","consumer":"research_pipeline/paper_first_agent_safety_current_projection.py","producer_anchors":('"paper_evidence_ready": True','"failure_classification"','"additional_behavior_execution_authorized": False'),"consumer_anchors":("project_agent_safety_current_state","FAILURE_LAYERS","receipt_path")},
    {"key":"agent-safety-reopen-control-to-current-projection","producer":"research_pipeline/paper_first_agent_safety_r9_reopen_control.py","consumer":"research_pipeline/paper_first_agent_safety_current_projection.py","producer_anchors":("DESIGN_COMPILED_GATES_UNSATISFIED","EXACT-HELDOUT-SCHEDULE-MANIFEST-MATERIALIZED","execution_authorized"),"consumer_anchors":("reopen_control_design","control_design_sha256","requirements_on_hold")},
    {"key":"agent-safety-claim-table-to-current-projection","producer":"research_pipeline/paper_first_agent_safety_r9_memory_graph.py","consumer":"research_pipeline/paper_first_agent_safety_current_projection.py","producer_anchors":("build_paper_claim_table","table_sha256","HOLD_METHOD_IDENTIFICATION"),"consumer_anchors":("paper_claim_table_sha256","paper_claim_boundary","HOLD_METHOD_IDENTIFICATION")},
    {"key":"agent-safety-claim-traceability-to-memory-graph","producer":"research_pipeline/claim_evidence_traceability.py","consumer":"research_pipeline/scientific_research_graph.py","producer_anchors":("build_claim_evidence_traceability","limits_claim","challenges_claim","tests_identification_for"),"consumer_anchors":("claim_evidence_traceability","claim_evidence_bindings","control_design","authorization_gate")},
    {"key":"agent-safety-current-projection-to-research-system","producer":"research_pipeline/paper_first_agent_safety_current_projection.py","consumer":"research_pipeline/research_system.py","producer_anchors":("load_current_agent_safety_program_state","projection_consistency","CURRENT_STAGE"),"consumer_anchors":("load_current_agent_safety_program_state","agent_safety_current_state","Agent Safety current-state receipt")},
    {"key":"agent-safety-control-traceability-to-research-system","producer":"research_pipeline/claim_evidence_traceability.py","consumer":"research_pipeline/research_system.py","producer_anchors":("CLAIM_EVIDENCE_TRACEABILITY_COMPILED","authorization_gates_bound","scientific_authority"),"consumer_anchors":("agent_safety_claim_evidence_traceability","agent_safety_reopen_control_design","claim_evidence_traceability=agent_safety_claim_evidence_traceability")},
    {"key":"agent-safety-current-projection-to-frontend","producer":"research_pipeline/paper_first_agent_safety_current_projection.py","consumer":"agent-safety-program-view.js","producer_anchors":('"future_evidence"',"PAPER_EVIDENCE_READY_CAUSAL_ATTRIBUTION_HOLD","paper_claim_boundary"),"consumer_anchors":("future_evidence","SUPPORTED_NARROWLY","HOLD_METHOD_IDENTIFICATION")},
)


def _read(root: Path, relative: str) -> str:
    try:
        return (root / relative).read_text(encoding="utf-8")
    except OSError:
        return ""


def build_research_integration_lint(root: Path = PROJECT_ROOT) -> dict[str, Any]:
    rows=[]; errors=[]
    for spec in CONTRACTS:
        producer_text=_read(root,str(spec["producer"])); consumer_text=_read(root,str(spec["consumer"]))
        producer_missing=[a for a in spec["producer_anchors"] if a not in producer_text]
        consumer_missing=[a for a in spec["consumer_anchors"] if a not in consumer_text]
        passed=bool(producer_text and consumer_text and not producer_missing and not consumer_missing)
        rows.append({"key":spec["key"],"producer":spec["producer"],"consumer":spec["consumer"],"producer_exists":bool(producer_text),"consumer_exists":bool(consumer_text),"missing_producer_anchors":producer_missing,"missing_consumer_anchors":consumer_missing,"pass":passed,"scientific_authority":False})
        if not passed:
            errors.append({"code":"required-integration-contract-unwired","contract":spec["key"],"missing_producer_anchors":producer_missing,"missing_consumer_anchors":consumer_missing})
    passed_count=sum(row["pass"] for row in rows)
    return {"schema_version":SCHEMA_VERSION,"status":"PASS_INTEGRATION_LINT" if passed_count==len(rows) else "HOLD_INTEGRATION_LINT","policy":dict(POLICY),"contracts":rows,"errors":errors,"summary":{"contracts":len(rows),"passed":passed_count,"failed":len(rows)-passed_count,"orphan_required_integrations":len(errors)},"scientific_authority":False,"authority":{"provider_calls":False,"problem_gate":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
