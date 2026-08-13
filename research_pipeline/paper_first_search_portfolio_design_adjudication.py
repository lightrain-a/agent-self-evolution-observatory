from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-search-portfolio-design-adjudication.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-search-portfolio-design-adjudication.js"
SHADOW_PORTFOLIO_JSON = PROJECT_ROOT / "generated" / "paper-first-problem-search-portfolio-state.json"
SHADOW_QUEUE_JSON = PROJECT_ROOT / "generated" / "paper-first-problem-search-portfolio-queue-shadow.json"

PRIMARY_SOURCES: dict[str, list[dict[str, str]]] = {
    "SP-09": [
        {
            "ref": "arXiv:2602.12430",
            "title": "Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the Path Forward",
            "url": "https://arxiv.org/abs/2602.12430",
            "boundary_role": "Direct governance collision: four-stage verification gates map acquisition provenance to four graduated deployment-permission tiers with runtime trust evolution; deployment governance cannot be claimed as the new object.",
        },
        {
            "ref": "arXiv:2607.01136",
            "title": "Skills Are Not Islands: Measuring Dependency and Risk in Agent Skill Supply Chains",
            "url": "https://arxiv.org/abs/2607.01136",
            "boundary_role": "Dependency- and workflow-level risk is already a first-class skill-supply-chain object; single-skill inspection is explicitly shown insufficient.",
        },
        {
            "ref": "arXiv:2608.09732",
            "title": "ColluSkill: Adversarial Cross-Skill Composition for Evading Agent Skill Scanners",
            "url": "https://arxiv.org/abs/2608.09732",
            "boundary_role": "ChainGuard already analyzes candidate plus installed skills, dependencies, artifact flows, capability composition, and downstream behavior.",
        },
        {
            "ref": "arXiv:2608.09577",
            "title": "ElasticBack: Stealthy Conditional Backdoor in LLM-Agent Skills via Coupled Trigger-Rule Optimization",
            "url": "https://arxiv.org/abs/2608.09577",
            "boundary_role": "Conditional dormant trigger-risk with preserved clean accuracy and cross-model transfer is already directly demonstrated.",
        },
        {
            "ref": "arXiv:2605.30723",
            "title": "Skill is Not One-Size-Fits-All: Model-Aware Skill Alignment for LLM Agents",
            "url": "https://arxiv.org/abs/2605.30723",
            "boundary_role": "Target-backbone dependence of skill benefit/harm and model-conditioned skill adaptation are already occupied.",
        },
        {
            "ref": "arXiv:2608.10538",
            "title": "SKILLER: Language-Level Reinforcement Learning for Reusable Skill Extraction in Small Language Models",
            "url": "https://arxiv.org/abs/2608.10538",
            "boundary_role": "Executor-specific evolved-skill utility is directly optimized and empirically measured.",
        },
    ],
    "SP-15": [
        {
            "ref": "arXiv:2608.08640",
            "title": "SkillReason: Reasoning-Enhanced Agent Skill Retrieval for Implicit User Requests",
            "url": "https://arxiv.org/abs/2608.08640",
            "boundary_role": "Direct collision with concise underspecified implicit requests and query-only inference without autoregressive CoT; also reports a distinction between top-rank retrieval and complete capability coverage.",
        },
        {
            "ref": "arXiv:2606.18051",
            "title": "Compositional Skill Routing for LLM Agents: Decompose, Retrieve, and Compose",
            "url": "https://arxiv.org/abs/2606.18051",
            "boundary_role": "Task decomposition and multi-skill composition are already formalized; decomposition quality is identified as a primary retrieval bottleneck.",
        },
        {
            "ref": "arXiv:2607.06283",
            "title": "Task Decomposition-Guided Reranking for Adaptive Agent Skill Retrieval",
            "url": "https://arxiv.org/abs/2607.06283",
            "boundary_role": "Task/skill decomposition plus structured reranking already targets ambiguous skill selection.",
        },
        {
            "ref": "arXiv:2606.03565",
            "title": "Skill Is Not Document: A Query-Conditional Benchmark and Two-Stage Retriever for LLM Agent Skill Routing",
            "url": "https://arxiv.org/abs/2606.03565",
            "boundary_role": "Query-conditional joint skill-set compatibility is already a supervised retrieval object rather than independent relevance alone.",
        },
        {
            "ref": "arXiv:2606.10388",
            "title": "SkillResolve-Bench: Measuring and Resolving Same-Capability Ambiguity in Agent Skill Retrieval",
            "url": "https://arxiv.org/abs/2606.10388",
            "boundary_role": "Query-specific same-capability ambiguity and procedural execution risk are already measured and resolved.",
        },
        {
            "ref": "arXiv:2606.03056",
            "title": "SkillDAG: Self-Evolving Typed Skill Graphs for LLM Skill Selection at Scale",
            "url": "https://arxiv.org/abs/2606.03056",
            "boundary_role": "Inter-skill dependency/conflict/specialization structure is already exposed as a retrieval-time object.",
        },
        {
            "ref": "arXiv:2605.05726",
            "title": "SkillRet: A Large-Scale Benchmark for Skill Retrieval in LLM Agents",
            "url": "https://arxiv.org/abs/2605.05726",
            "boundary_role": "Large-scale realistic skill retrieval and query-signal limitations are already benchmarked with disjoint skill pools.",
        },
        {
            "ref": "arXiv:2607.19801",
            "title": "CIR at iKAT SCAI 2026: Exploring Clarification Need Prediction in Agentic Conversational Search",
            "url": "https://arxiv.org/abs/2607.19801",
            "boundary_role": "Generic ambiguity handling via clarification-need prediction is a mature same-information baseline for any proposed abstain/clarify policy.",
        },
    ],
}

SHADOW_DEAD_END_MEMORY = {
    "memory_id": "shadow-paper-design-dead-ends-20260814-r1",
    "scientific_authority": False,
    "live_source_coverage_effect": False,
    "cannot_mutate_canonical_generator_or_queue": True,
    "search_escape_required": True,
    "blocked_objects": [
        {
            "source_candidate_id": "SP-09",
            "basin": "skill-deployment-governance-contextual-acceptance",
            "avoid": [
                "trust tiers or graduated deployment permission as the novelty",
                "context-aware scanner followed by install/update/block/escalate policy as the novelty",
                "model-conditioned skill utility or risk as the novelty",
                "generic contextual constrained or risk-sensitive scalar acceptance",
            ],
            "reopen_only_if": "Current primary evidence supports an ex-ante non-separability or impossibility prediction for the same skill under identical model/trigger/workflow/security/utility information that generic contextual governance cannot express.",
        },
        {
            "source_candidate_id": "SP-15",
            "basin": "implicit-query-decomposition-skill-routing",
            "avoid": [
                "implicit queries are harder",
                "task decomposition improves skill retrieval",
                "top-rank relevance differs from complete capability coverage",
                "query-conditional multi-skill compatibility alone",
                "generic abstention, uncertainty, or clarification policy",
            ],
            "reopen_only_if": "A new provenance-audited query-level unit shows that the same observable or information-equivalent query is compatible with multiple task semantics requiring incompatible sufficient skill sets, and a generic partial-identification/clarification baseline using the same information cannot absorb the claim.",
        },
    ],
}

ADVISORY_CONSULTATION = {
    "run_root": "generated/research-data/runs/ai-consultation/cases/sp-paper-design-20260814",
    "checkpoint": "idea_premortem",
    "reviewers": [
        {
            "reviewer": "glm-5.2",
            "SP-09": "missing:model-output-no-json",
            "SP-15": "missing:output-length-ceiling",
        },
        {
            "reviewer": "deepseek-v4-pro",
            "SP-09": "missing:reasoning-output-length-ceiling",
            "SP-15": "missing:reasoning-output-length-ceiling",
        },
    ],
    "failed_or_missing_review_is_not_pass": True,
    "scientific_authority": False,
}

ROWS: tuple[dict[str, Any], ...] = (
    {
        "id": "SP-09",
        "verdict": "STOP_STANDALONE_COLLISION_KEEP_CONTEXT_RISK_AXIS",
        "original_problem": "Model-trigger-skill-context acceptance object with a compositional-risk veto for evolved skill deployment.",
        "collision_status": "DIRECT_PLUS_COMPOSITIONAL",
        "paper_problem_status": "STOP_STANDALONE",
        "collision_reason": "The original novelty bundle is occupied in pieces that together reproduce the claimed paper object: lifecycle governance already maps verification to graduated deployment permissions; dependency/context-aware skill-chain risk is explicit; conditional dormant attacks and model-dependent skill behavior are already empirical first-class objects. A new install/update/block/escalate acceptance object therefore reduces to a contextual security/utility policy unless it proves a stronger impossibility or decision-theoretic phenomenon.",
        "surviving_risk_axis": "Context-dependent admissibility of the same evolved skill across target model × trigger × installed-skill/workflow context remains a useful evaluation axis, but not a standalone paper thesis under the current formulation.",
        "strongest_same_information_baselines": [
            "Skill Trust and Lifecycle Governance gates/tiers with context-aware verification features",
            "ChainGuard-style candidate+installed-skill context analysis followed by graduated permission assignment",
            "generic contextual constrained decision/risk-sensitive policy using identical model/trigger/workflow/security/utility features",
            "MASA-style model-conditioned skill adaptation plus a security gate",
        ],
        "revival_requirements": [
            "State an ex-ante prediction that cannot be expressed by a contextual constrained policy using exactly the same model/trigger/workflow/utility/security evidence.",
            "Show that the same skill's admissibility has a structural non-separability/impossibility property, not merely model dependence or composition dependence.",
            "Beat lifecycle-governance and ChainGuard-derived decision rules under the same information and false-positive/utility budget.",
            "Do not use a new scalar score, trust tier, permission tier, scanner, or hard veto as the novelty claim.",
        ],
        "cheapest_problem_falsifier": "Construct the candidate's intended install/update/block/escalate labels on a small matched table, then fit or hand-compile a generic contextual constrained policy with the identical target-model, trigger, installed-skill/workflow, utility, and security observations. If it reproduces the decisions, the revised object has no irreducible paper novelty.",
        "method_design_authorized": False,
        "experiment_blueprint_authorized": False,
        "local_validation_authorized": False,
        "p0_authorized": False,
        "gpu_authorized": False,
        "next_action": "Stop standalone SP-09. Preserve context-dependent admissibility as a risk/baseline axis for future skill-evolution papers; reopen only with a non-separability/impossibility result beyond contextual governance.",
    },
    {
        "id": "SP-15",
        "verdict": "REVISE_PAPER_PROBLEM_SUPPORT_INVENTORY_REQUIRED",
        "original_problem": "The explicit-procedure boundary of query-only skill retrieval.",
        "collision_status": "DIRECT_ON_IMPLICIT_RETRIEVAL_AND_DECOMPOSITION",
        "paper_problem_status": "REVISE_BEFORE_METHOD_DESIGN",
        "collision_reason": "Implicit query difficulty, reasoning-enhanced query-only retrieval, task decomposition, structured multi-skill routing, query-conditional skill-set compatibility, same-capability ambiguity, and typed structural retrieval are already occupied. The original explicit-versus-implicit procedural boundary is therefore not sufficient novelty.",
        "revised_problem": "Given an observable user query q and a fixed skill library L under query-only inference, is the minimally sufficient capability/skill set point-identifiable from q at all? If multiple task semantics that are observationally compatible with the same q require incompatible sufficient skill sets, retrieval is structurally non-identifiable and a system must abstain or acquire additional information rather than merely rerank more strongly.",
        "irreducible_boundary_required": "The claim must be about observational non-identifiability of the sufficient skill set, not about implicit queries being harder, decomposition improving retrieval, multi-skill compatibility, same-capability representative risk, or a new clarification policy. The paper must separate 'retriever failed to infer latent steps' from 'no query-only retriever can identify one sufficient set from the available information'.",
        "strongest_same_information_baselines": [
            "SkillReason query-only reasoning-enhanced embedding",
            "SkillWeaver / SkillReranker task decomposition and structured reranking",
            "R3-Skill query-conditional set compatibility",
            "SkillResolve same-capability query-conditioned utility/representative selection",
            "SkillDAG structural relation/conflict retrieval",
            "generic selective prediction / calibrated abstention",
            "generic partial identification over latent task interpretations",
            "generic clarification-need prediction / active query refinement",
        ],
        "required_problem_revision": [
            "Define an observational equivalence relation over task semantics that produce the same available query representation and map each semantic state to a sufficient capability/skill set.",
            "Define point-identifiable, set-identifiable, and non-identifiable retrieval cases before introducing any learned method.",
            "Require matched examples where the observable query is held fixed or information-equivalent while compatible latent task semantics require incompatible sufficient skill sets; simple short-vs-long or explicit-vs-implicit pairs are insufficient.",
            "Show that an oracle ranker with the same query information cannot resolve the non-identifiable cases; otherwise the issue is model quality rather than information structure.",
            "Audit against generic selective prediction, partial identification, and clarification policies using exactly the same ambiguity set/evidence.",
            "Do not claim task decomposition, capability reasoning, top-rank-versus-coverage metrics, or abstention itself as novelty.",
        ],
        "cheapest_problem_falsifier": "Before method design, inventory existing SkillReason/SkillRet/CompSkillBench/R3-Skill/SkillResolve-style assets for query-level units where one observable or information-equivalent query admits multiple plausible task semantics with incompatible sufficient skill sets. If no such units exist, or if a generic uncertainty/clarification baseline using the same information resolves them, stop the revised problem.",
        "method_design_authorized": False,
        "experiment_blueprint_authorized": False,
        "local_validation_authorized": False,
        "p0_authorized": False,
        "gpu_authorized": False,
        "next_action": "Run a data-only support inventory for query-level non-identifiability. Advance to method design only if nonzero matched units survive source/provenance and generic partial-identification/clarification reduction checks.",
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def build_search_portfolio_design_adjudication() -> dict[str, Any]:
    portfolio = _load_json(SHADOW_PORTFOLIO_JSON)
    queue_shadow = _load_json(SHADOW_QUEUE_JSON)
    portfolio_policy = portfolio.get("policy") or {}
    queue_policy = queue_shadow.get("policy") or {}
    if portfolio.get("scientific_authority") is not False or portfolio_policy.get("shadow_only") is not True or portfolio_policy.get("canonical_primary_generator_queue_untouched") is not True:
        raise ValueError("Search Portfolio Paper Design audit requires the zero-authority shadow portfolio state")
    if queue_shadow.get("scientific_authority") is not False or queue_policy.get("shadow_only") is not True or queue_policy.get("cannot_mutate_canonical_queue") is not True:
        raise ValueError("Search Portfolio Paper Design audit requires the zero-authority counterfactual queue shadow")
    candidates = {str(row.get("candidate_id")): row for row in portfolio.get("candidates") or [] if isinstance(row, dict) and row.get("historical_counterfactual_problem_gate_pass") is True}
    counterfactual_pass_ids = {str(value) for value in queue_shadow.get("historical_counterfactual_pass_ids") or []}
    reviewed_ids = [str(row["id"]) for row in ROWS]
    missing = sorted(set(reviewed_ids) - set(candidates) | (set(reviewed_ids) - counterfactual_pass_ids))
    if missing:
        raise ValueError("Search Portfolio design audit requires historical shadow counterfactual survivors: " + ",".join(missing))
    rows = []
    for template in ROWS:
        row = dict(template)
        source = candidates[row["id"]]
        row["shadow_candidate_title"] = source.get("title")
        row["shadow_search_primitive"] = source.get("search_primitive")
        row["historical_counterfactual_problem_gate_pass"] = True
        row["live_paper_design_eligible"] = False
        row["primary_sources"] = PRIMARY_SOURCES[row["id"]]
        row["counterfactual_problem_gate_pass_does_not_grant_live_paper_design"] = True
        rows.append(row)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "review_id": "search-portfolio-sp09-sp15-paper-design-20260814",
        "target_venue": "ICLR",
        "component_owner": "paper-design-contract",
        "source_state": "shadow-search-portfolio",
        "policy": {
            "this_is_a_substate_not_a_new_backend_component": True,
            "source_is_shadow_search_portfolio": True,
            "shadow_queue_has_zero_paper_design_authority": True,
            "cannot_grant_or_revoke_live_paper_design_authority": True,
            "counterfactual_problem_gate_pass_only_triggers_retrospective_collision_audit": True,
            "current_primary_source_collision_review_required": True,
            "same_information_reduction_required_before_method_design": True,
            "failed_or_missing_ai_reviewer_is_not_pass": True,
            "paper_problem_support_inventory_precedes_method_design_when_identifiability_is_claimed": True,
            "method_design_authorized": False,
            "experiment_blueprint_authorized": False,
            "local_validation_authorized": False,
            "p0_authorized": False,
            "gpu_authorized": False,
        },
        "advisory_consultation": ADVISORY_CONSULTATION,
        "shadow_dead_end_memory": SHADOW_DEAD_END_MEMORY,
        "shadow_source": {
            "portfolio_status": portfolio.get("status"),
            "portfolio_schema_version": portfolio.get("schema_version"),
            "historical_source_commit": portfolio.get("historical_source_commit"),
            "frozen_pool_sha256": portfolio.get("frozen_pool_sha256"),
            "summary": dict(portfolio.get("summary") or {}),
            "queue_summary": dict(queue_shadow.get("summary") or {}),
            "scientific_authority": False,
        },
        "summary": {
            "reviewed": len(rows),
            "advance_to_method_design": 0,
            "revise_paper_problem": counts.get("REVISE_PAPER_PROBLEM_SUPPORT_INVENTORY_REQUIRED", 0),
            "stop_standalone": counts.get("STOP_STANDALONE_COLLISION_KEEP_CONTEXT_RISK_AXIS", 0),
            "support_inventory_required": counts.get("REVISE_PAPER_PROBLEM_SUPPORT_INVENTORY_REQUIRED", 0),
            "method_design_authorized": 0,
            "experiment_blueprint_authorized": 0,
            "local_validation_authorized": 0,
            "p0_authorized": 0,
            "gpu_authorized": 0,
        },
        "portfolio_priority": ["SP-15", "SP-09"],
        "rows": rows,
        "portfolio_decision": "Retrospective shadow audit only: SP-09 stops standalone after direct governance/context/model-dependence collisions. SP-15 is revised from an explicit-procedure retrieval boundary to query-only sufficient-skill-set identifiability, but remains blocked from Method Design until query-level support inventory establishes nonzero observationally non-identifiable units and generic partial-identification/clarification baselines do not absorb the object. Neither shadow candidate has live Paper Design authority.",
        "next_action": "Use these outcomes only as zero-authority shadow-search feedback. Do not design a method, compile an Experiment Blueprint, mutate the canonical Problem-Gate queue, start P0, or use GPU for either candidate.",
    }


def validate_search_portfolio_design_adjudication(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = state.get("summary") or {}
    policy = state.get("policy") or {}
    rows = state.get("rows") or []
    if len(rows) != 2 or {str(row.get("id")) for row in rows} != {"SP-09", "SP-15"}:
        errors.append("SP design adjudication must review exactly SP-09 and SP-15")
    if (summary.get("reviewed"), summary.get("advance_to_method_design"), summary.get("revise_paper_problem"), summary.get("stop_standalone")) != (2, 0, 1, 1):
        errors.append("SP design routing must be 0 advance / 1 revise / 1 stop")
    if any(int(summary.get(key) or 0) != 0 for key in ("method_design_authorized", "experiment_blueprint_authorized", "local_validation_authorized", "p0_authorized", "gpu_authorized")):
        errors.append("SP design adjudication cannot authorize downstream work")
    if policy.get("this_is_a_substate_not_a_new_backend_component") is not True or policy.get("paper_problem_support_inventory_precedes_method_design_when_identifiability_is_claimed") is not True:
        errors.append("SP design must remain a Paper Design substate and gate identifiability on support inventory")
    if policy.get("source_is_shadow_search_portfolio") is not True or policy.get("shadow_queue_has_zero_paper_design_authority") is not True or policy.get("cannot_grant_or_revoke_live_paper_design_authority") is not True:
        errors.append("SP design audit must remain retrospective shadow feedback with zero live Paper Design authority")
    if (state.get("advisory_consultation") or {}).get("scientific_authority") is not False or (state.get("advisory_consultation") or {}).get("failed_or_missing_review_is_not_pass") is not True:
        errors.append("unavailable AI premortem reviewers must remain zero-authority and cannot count as PASS")
    memory = state.get("shadow_dead_end_memory") or {}
    if memory.get("scientific_authority") is not False or memory.get("live_source_coverage_effect") is not False or memory.get("cannot_mutate_canonical_generator_or_queue") is not True or len(memory.get("blocked_objects") or []) != 2:
        errors.append("Paper Design dead-end memory must remain shadow-only and contain both SP-09/SP-15 basins")
    for row in rows:
        if not row.get("primary_sources") or not row.get("cheapest_problem_falsifier") or row.get("method_design_authorized") is not False or row.get("gpu_authorized") is not False or row.get("live_paper_design_eligible") is not False or row.get("counterfactual_problem_gate_pass_does_not_grant_live_paper_design") is not True:
            errors.append(f"SP design row incomplete or illegally authoritative:{row.get('id')}")
    return sorted(set(errors))


def write_search_portfolio_design_adjudication(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_search_portfolio_design_adjudication()
    errors = validate_search_portfolio_design_adjudication(state)
    if errors:
        raise ValueError("Invalid Search Portfolio Paper Design adjudication:\n- " + "\n- ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_SEARCH_PORTFOLIO_DESIGN_ADJUDICATION = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_search_portfolio_design_adjudication(), ensure_ascii=False, indent=2))
