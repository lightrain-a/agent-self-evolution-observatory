from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-sp15-identifiability-support.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-sp15-identifiability-support.js"

AUDITED_SOURCES: tuple[dict[str, Any], ...] = (
    {
        "ref": "arXiv:2608.08640",
        "title": "SkillReason: Reasoning-Enhanced Agent Skill Retrieval for Implicit User Requests",
        "primary_url": "https://arxiv.org/abs/2608.08640",
        "access": "verified primary abstract plus bounded local full-text facts",
        "phenomenon_support": True,
        "identifiability_unit_support": False,
        "finding": "The source supports concise underspecified queries, an explicit-versus-implicit retrieval boundary, and a gap between top-rank retrieval and complete capability coverage. It does not expose one observable query paired with multiple compatible task semantics requiring incompatible sufficient skill sets.",
    },
    {
        "ref": "arXiv:2606.18051",
        "title": "Compositional Skill Routing for LLM Agents: Decompose, Retrieve, and Compose",
        "primary_url": "https://arxiv.org/abs/2606.18051",
        "access": "primary arXiv HTML",
        "phenomenon_support": True,
        "identifiability_unit_support": False,
        "finding": "CompSkillBench supplies 300 compositional queries with ground-truth skill chains and demonstrates a decomposition bottleneck. The reviewed source does not establish multiple incompatible sufficient chains as equally compatible with the same observable query.",
    },
    {
        "ref": "arXiv:2606.03565",
        "title": "Skill Is Not Document: A Query-Conditional Benchmark and Two-Stage Retriever for LLM Agent Skill Routing",
        "primary_url": "https://arxiv.org/abs/2606.03565",
        "access": "author repository plus released R3-Skill data schema",
        "repository": "https://github.com/Tencent/R3-Skill",
        "repository_commit": "57d9285969cc293832c71ecbe42a75ac416bef93",
        "released_data_audit": {
            "test_queries": 5696,
            "unique_exact_query_strings": 5696,
            "duplicate_exact_query_strings": 0,
            "skill_number_counts": {"1": 5191, "2": 467, "3": 38},
            "unique_ground_truth_skill_sets": 2407,
            "ground_truth_schema": "one skill_ids list per query row",
        },
        "phenomenon_support": True,
        "identifiability_unit_support": False,
        "finding": "The release provides multi-skill labels and query-conditional set supervision, but all 5,696 test query strings are exact-unique and each row supplies one ground-truth skill set. Repeated label sets across distinct queries do not establish one observable query with multiple latent task interpretations.",
    },
    {
        "ref": "arXiv:2606.10388",
        "title": "SkillResolve-Bench: Measuring and Resolving Same-Capability Ambiguity in Agent Skill Retrieval",
        "primary_url": "https://arxiv.org/abs/2606.10388",
        "access": "primary arXiv abstract and HTML",
        "phenomenon_support": True,
        "identifiability_unit_support": False,
        "finding": "The benchmark supplies query-conditioned ambiguity within a capability family and a preferred representative for each query. It does not directly evidence multiple observationally compatible task semantics requiring incompatible sufficient capability sets.",
    },
    {
        "ref": "arXiv:2606.03056",
        "title": "SkillDAG: Self-Evolving Typed Skill Graphs for LLM Skill Selection at Scale",
        "primary_url": "https://arxiv.org/abs/2606.03056",
        "access": "author repository schema",
        "repository": "https://github.com/Ericbai06/SkillDAG",
        "repository_commit": "2bd7baffae58854018f75857e5626a4a28a705ae",
        "phenomenon_support": True,
        "identifiability_unit_support": False,
        "finding": "The release exposes typed inter-skill structure for retrieval. Structural relations can improve set selection but do not by themselves establish non-identifiability from the same observed query.",
    },
)

NEAR_EQUIVALENT_SCAN = {
    "source": "Tencent/R3-Skill data/test.jsonl",
    "purpose": "bounded discovery-only screen for high text-overlap rows with different labels",
    "method": "dependency-free informative-token inverted index and overlap screen",
    "cross_label_pairs_screened": 928355,
    "high_overlap_candidates": 190,
    "qualifying_identifiability_units": 0,
    "reason": "High text overlap mainly reflected shared domain or template language while the requested tasks differed. Text overlap was never treated as proof of information equivalence.",
    "scientific_authority": False,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_sp15_identifiability_support() -> dict[str, Any]:
    units = sum(int(row.get("identifiability_unit_support") is True) for row in AUDITED_SOURCES)
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "support_id": "sp15-query-only-identifiability-support-20260814",
        "paper_problem_id": "SP-15",
        "revised_claim": "Under fixed query-only inference and a fixed skill library, a minimally sufficient skill set may be observationally non-identifiable when multiple task semantics compatible with the same available query require incompatible sufficient sets.",
        "policy": {
            "data_only_no_model_training": True,
            "phenomenon_support_is_not_identifiability_support": True,
            "underspecified_language_is_not_proof_of_nonidentifiability": True,
            "one_ground_truth_set_per_query_is_not_positive_identifiability_evidence": True,
            "near_duplicate_text_is_discovery_only_not_scientific_evidence": True,
            "query_level_matched_unit_required_before_method_design": True,
            "generic_partial_identification_and_clarification_are_required_reduction_baselines": True,
            "automatic_method_authority": False,
            "automatic_experiment_authority": False,
            "automatic_p0_authority": False,
            "gpu_authority": False,
        },
        "summary": {
            "primary_or_author_releases_audited": len(AUDITED_SOURCES),
            "phenomenon_support_sources": sum(bool(row.get("phenomenon_support")) for row in AUDITED_SOURCES),
            "query_level_identifiability_units": units,
            "released_r3_test_queries": 5696,
            "released_r3_exact_duplicate_queries": 0,
            "near_equivalent_candidates": NEAR_EQUIVALENT_SCAN["high_overlap_candidates"],
            "near_equivalent_candidates_promoted": 0,
            "support_status": "INSUFFICIENT_FOR_IDENTIFIABILITY_CLAIM" if units == 0 else "NONZERO_SUPPORT",
            "method_design_authorized": 0,
            "experiment_blueprint_authorized": 0,
            "local_validation_authorized": 0,
            "p0_authorized": 0,
            "gpu_authorized": 0,
        },
        "audited_sources": [dict(row) for row in AUDITED_SOURCES],
        "near_equivalent_scan": dict(NEAR_EQUIVALENT_SCAN),
        "support_diagnosis": {
            "status": "INSUFFICIENT_FOR_IDENTIFIABILITY_CLAIM",
            "stop_class": "SUPPORT_STOP",
            "failure_layer": "experiment_identifiability",
            "failure_subtype": "NO_MATCHED_QUERY_IDENTIFIABILITY_UNIT",
            "principle_dead_end_certified": False,
            "principle_update_allowed": False,
            "core_principle_rejected": False,
            "benchmark_level_dead_end_certified": False,
            "reason": "Five audited first-party or author-released sources support the retrieval/decomposition/coverage phenomenon, but expose zero provenance-audited matched query-level units in which the same observable or information-equivalent query remains compatible with multiple task semantics that require incompatible sufficient skill sets.",
            "reopen_only_if": "A new provenance-audited query-level unit shows that the same observable or information-equivalent query is compatible with multiple task semantics requiring incompatible sufficient skill sets, and a generic partial-identification/clarification baseline using the same information cannot absorb the claim.",
        },
        "decision": "HOLD_SP15_REVISED_PROBLEM_NO_IDENTIFIABILITY_UNIT",
        "interpretation": "Current evidence strongly supports a real retrieval/decomposition/coverage phenomenon, but the revised thesis needs a stronger unit than current audited benchmarks expose. Zero directly supported query-level identifiability units were found. This is a support failure for the revised formulation, not evidence that such ambiguity never exists.",
        "next_action": "Do not design a method. Obtain or construct a provenance-audited matched ambiguity resource with nonzero query-level identifiability units, or return SP-15 to problem search/revision. A future revival must beat generic partial-identification, selective-prediction, and clarification baselines under the same information.",
    }


def validate_sp15_identifiability_support(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = state.get("policy") or {}
    summary = state.get("summary") or {}
    diagnosis = state.get("support_diagnosis") or {}
    if summary.get("query_level_identifiability_units") != 0 or summary.get("support_status") != "INSUFFICIENT_FOR_IDENTIFIABILITY_CLAIM":
        errors.append("current SP-15 support inventory must not fabricate identifiability units")
    if summary.get("released_r3_test_queries") != 5696 or summary.get("released_r3_exact_duplicate_queries") != 0:
        errors.append("R3-Skill released-query inventory is inconsistent")
    if summary.get("near_equivalent_candidates_promoted") != 0 or (state.get("near_equivalent_scan") or {}).get("scientific_authority") is not False:
        errors.append("near-equivalent query scan cannot become scientific evidence")
    if policy.get("phenomenon_support_is_not_identifiability_support") is not True or policy.get("query_level_matched_unit_required_before_method_design") is not True:
        errors.append("SP-15 support gate must separate phenomenon from matched identifiability units")
    if (diagnosis.get("status"), diagnosis.get("stop_class"), diagnosis.get("failure_layer"), diagnosis.get("failure_subtype")) != ("INSUFFICIENT_FOR_IDENTIFIABILITY_CLAIM", "SUPPORT_STOP", "experiment_identifiability", "NO_MATCHED_QUERY_IDENTIFIABILITY_UNIT"):
        errors.append("SP-15 missing matched identifiability support must be typed as experiment-identifiability SUPPORT_STOP")
    if diagnosis.get("principle_dead_end_certified") is not False or diagnosis.get("principle_update_allowed") is not False or diagnosis.get("core_principle_rejected") is not False or diagnosis.get("benchmark_level_dead_end_certified") is not False:
        errors.append("SP-15 support insufficiency cannot certify or update the scientific principle")
    for key in ("method_design_authorized", "experiment_blueprint_authorized", "local_validation_authorized", "p0_authorized", "gpu_authorized"):
        if int(summary.get(key) or 0) != 0:
            errors.append(f"SP-15 support inventory cannot authorize:{key}")
    if state.get("decision") != "HOLD_SP15_REVISED_PROBLEM_NO_IDENTIFIABILITY_UNIT":
        errors.append("SP-15 must remain HOLD without nonzero identifiability support")
    return sorted(set(errors))


def write_sp15_identifiability_support(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_sp15_identifiability_support()
    errors = validate_sp15_identifiability_support(state)
    if errors:
        raise ValueError("Invalid SP-15 identifiability support inventory:\n- " + "\n- ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_SP15_IDENTIFIABILITY_SUPPORT = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_sp15_identifiability_support(), ensure_ascii=False, indent=2))
