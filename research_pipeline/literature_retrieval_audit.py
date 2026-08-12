from __future__ import annotations

from typing import Any


POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "deep_and_wide_retrieval_are_distinct_capabilities": True,
    "relation_aware_retrieval_is_separate_from_content_similarity": True,
    "search_evidence_gathering_and_synthesis_are_separate_stages": True,
    "claim_evidence_chain_required_for_public_claims": True,
    "citation_verifier_must_be_named_versioned_and_calibrated": True,
    "retrieval_quality_must_be_measured_under_cost_budget": True,
    "domain_mismatched_reranker_requires_empirical_qualification": True,
    "pseudo_relevance_labels_cannot_support_benchmark_claims": True,
}

REFERENCES = [
    {"system": "AutoResearchBench", "adopted": "evaluate target-paper Deep Research and open-ended Wide Research as separate literature capabilities"},
    {"system": "SciNetBench", "adopted": "evaluate ego-, pair-, and path-level scientific relations rather than only content similarity"},
    {"system": "PaperQA2", "adopted": "separate paper search, evidence gathering, and answer generation with citation/metadata provenance"},
    {"system": "SciRet", "adopted": "measure retrieval/reranking under corpus-scale and compute constraints; empirically qualify domain-mismatched rerankers"},
    {"system": "Citation Faithfulness Audit", "adopted": "validate and calibrate the citation verifier itself against human gold before trusting citation-failure rates"},
    {"system": "ScientistOne", "adopted": "route numerical, citation, and method claims back to evaluator logs, primary literature, and implementation artifacts"},
]

CLAIM_EVIDENCE_ROUTES = {
    "numerical": "evaluator/result logs and immutable metric tables",
    "citation": "versioned primary literature or official project source",
    "method": "frozen code/config/protocol artifact",
    "system-state": "generated state with provenance and source authority",
}

RETRIEVAL_MODES = (
    {
        "id": "deep-target",
        "question": "Can the system recover a specific target paper from partial scientific clues through multi-step search?",
        "metrics": ["target_recall", "queries_to_target", "source_quality", "cost"],
    },
    {
        "id": "wide-coverage",
        "question": "Can the system comprehensively collect papers satisfying frozen inclusion/exclusion criteria?",
        "metrics": ["set_recall", "set_precision", "IoU", "coverage_gaps", "cost"],
    },
    {
        "id": "relation-aware",
        "question": "Can the system recover supporting, conflicting, derivative, and lineage relations among papers?",
        "metrics": ["ego_relation_accuracy", "pair_relation_accuracy", "path_reconstruction", "review_quality_gain"],
    },
    {
        "id": "claim-grounding",
        "question": "Can every public claim be traced to the correct evidence type without unsupported extrapolation?",
        "metrics": ["citation_support", "claim_evidence_match", "method_code_alignment", "numeric_log_match"],
    },
)


def build_literature_retrieval_audit(evidence_graph: dict[str, Any], corpus: dict[str, Any] | None = None) -> dict[str, Any]:
    graph_summary = evidence_graph.get("summary") or {}
    corpus_stats = (corpus or {}).get("statistics") or {}
    return {
        "schema_version": "1.0",
        "policy": POLICY,
        "references": REFERENCES,
        "summary": {
            "retrieval_modes": len(RETRIEVAL_MODES),
            "claim_evidence_routes": len(CLAIM_EVIDENCE_ROUTES),
            "benchmark_status": "spec-ready-not-yet-scored",
            "current_evidence_nodes": int(graph_summary.get("nodes") or 0),
            "current_evidence_edges": int(graph_summary.get("edges") or 0),
            "current_corpus_papers": int(corpus_stats.get("paper_count") or 0),
        },
        "retrieval_modes": list(RETRIEVAL_MODES),
        "claim_evidence_routes": CLAIM_EVIDENCE_ROUTES,
        "citation_verifier_contract": {
            "required": ["verifier identity", "version", "human-gold calibration set", "false-positive/false-negative profile", "cost"],
            "rule": "Citation support statistics are incomparable across runs when verifier identity/protocol changes without recalibration.",
        },
        "retrieval_qualification": {
            "rule": "A more complex retriever or reranker is admitted only after it beats the matched simpler retriever on the target scientific domain under a matched compute budget.",
            "benchmark_claim_authority": False,
        },
    }
