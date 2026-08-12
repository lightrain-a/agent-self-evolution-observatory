from __future__ import annotations

from typing import Any


POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "capabilities_are_declared_not_prompt_inferred": True,
    "least_capable_sufficient_interface_is_preferred": True,
    "typed_scientific_tool_preferred_over_generic_shell": True,
    "dynamic_registration_requires_schema_version_and_smoke": True,
    "unavailable_capability_cannot_be_silently_substituted": True,
    "model_or_tool_routing_cannot_escalate_scientific_authority": True,
    "every_execution_capability_must_emit_auditable_artifacts": True,
    "licenses_and_data_access_constraints_are_part_of_capability_metadata": True,
}

REFERENCES = [
    {"system": "Biomni", "adopted": "declarative tool-description schemas plus a tool registry for dynamic registration and lookup"},
    {"system": "BioMedAgent", "adopted": "learn tool/workflow choice through interactive exploration and reusable memory instead of a fixed hand-written chain"},
    {"system": "PaperQA2", "adopted": "separate scientific search, evidence gathering, and answer synthesis while preserving grounded citations and metadata"},
    {"system": "SAGE", "adopted": "co-design agent subqueries and retriever choice; a stronger retriever is not automatically better when the query generator emits keyword-like queries"},
]

CAPABILITIES: tuple[dict[str, Any], ...] = (
    {
        "id": "literature-deep-search",
        "purpose": "Find a specific target paper or narrow evidence chain through iterative query refinement.",
        "input_contract": ["research question", "target clues", "date/source constraints"],
        "output_contract": ["candidate records", "primary-source refs", "search trace"],
        "authority": "evidence-discovery-only",
        "risk": "low",
        "preferred_interface": "typed literature connector/search API",
        "artifact": "query and candidate provenance",
    },
    {
        "id": "literature-wide-search",
        "purpose": "Collect a broad set of papers satisfying an explicit inclusion contract.",
        "input_contract": ["inclusion/exclusion criteria", "coverage boundary", "cutoff date"],
        "output_contract": ["candidate set", "coverage gaps", "deduplication log"],
        "authority": "evidence-discovery-only",
        "risk": "low",
        "preferred_interface": "multi-query literature retrieval",
        "artifact": "coverage and exclusion ledger",
    },
    {
        "id": "literature-relation-search",
        "purpose": "Recover supporting, conflicting, and lineage relationships rather than only similar papers.",
        "input_contract": ["seed paper or concept", "relation type", "cutoff/field boundary"],
        "output_contract": ["relation candidates", "relation evidence", "path provenance"],
        "authority": "evidence-discovery-only",
        "risk": "low",
        "preferred_interface": "relation-aware literature graph/search",
        "artifact": "pair/path relation ledger",
    },
    {
        "id": "primary-source-fetch",
        "purpose": "Fetch and verify the authoritative paper/project/repository behind a claim.",
        "input_contract": ["paper or project identity"],
        "output_contract": ["versioned primary source", "provenance"],
        "authority": "evidence-verification-only",
        "risk": "low",
        "preferred_interface": "official publisher/repository fetch",
        "artifact": "source identity and version",
    },
    {
        "id": "cpu-falsifier",
        "purpose": "Run the cheapest deterministic or offline test that can change a scientific decision.",
        "input_contract": ["frozen prediction", "candidate evidence", "falsifier contract"],
        "output_contract": ["typed falsifier result", "trace", "cost"],
        "authority": "diagnostic-only",
        "risk": "medium",
        "preferred_interface": "sandboxed deterministic runner",
        "artifact": "versioned result and trace",
    },
    {
        "id": "gpu-experiment",
        "purpose": "Execute an authorized scientific experiment under a frozen protocol.",
        "input_contract": ["execution-authorized card", "resource lease", "frozen config"],
        "output_contract": ["raw trace", "progress", "result artifact", "provenance"],
        "authority": "execution-only",
        "risk": "high",
        "preferred_interface": "experiment orchestrator",
        "artifact": "incremental run bundle",
    },
    {
        "id": "independent-analysis",
        "purpose": "Analyze frozen experiment artifacts without changing the execution protocol.",
        "input_contract": ["immutable evidence bundle", "analysis question"],
        "output_contract": ["analysis result", "assumptions", "uncertainty"],
        "authority": "interpretation-proposal-only",
        "risk": "medium",
        "preferred_interface": "isolated analysis worker",
        "artifact": "analysis provenance",
    },
    {
        "id": "ai-consultation",
        "purpose": "Red-team hypotheses, protocols, and interpretations with independent reviewers.",
        "input_contract": ["frozen dossier", "review rubric"],
        "output_contract": ["findings", "risk level", "machine-check proposals"],
        "authority": "advisory-only",
        "risk": "low",
        "preferred_interface": "blind multi-model review",
        "artifact": "review dossier and disposition",
    },
    {
        "id": "publication",
        "purpose": "Publish validated structured state without mutating scientific history.",
        "input_contract": ["validated generated artifacts", "deployment authority"],
        "output_contract": ["deployment manifest", "public snapshot"],
        "authority": "publication-only",
        "risk": "medium",
        "preferred_interface": "content-addressed deployment pipeline",
        "artifact": "build/deployment SHA",
    },
)


def build_research_capability_registry() -> dict[str, Any]:
    high_risk = [row["id"] for row in CAPABILITIES if row["risk"] == "high"]
    advisory = [row["id"] for row in CAPABILITIES if row["authority"] in {"advisory-only", "interpretation-proposal-only", "diagnostic-only"}]
    return {
        "schema_version": "1.0",
        "policy": POLICY,
        "references": REFERENCES,
        "summary": {
            "capabilities": len(CAPABILITIES),
            "high_risk": len(high_risk),
            "advisory_or_diagnostic": len(advisory),
            "dynamic_registration_policy": "schema+version+smoke required",
        },
        "capabilities": list(CAPABILITIES),
        "routing_contract": {
            "order": ["match typed capability", "check availability/version/smoke", "choose least-privilege sufficient interface", "verify authority and artifact contract", "execute or block"],
            "fallback": "block and surface the missing capability; never silently replace a missing scientific tool with a more permissive generic interface",
        },
        "retrieval_router_contract": {
            "rule": "route query formulation and retriever jointly rather than selecting a retriever in isolation",
            "simple_first": "BM25/lexical retrieval remains a mandatory matched baseline before a reasoning-heavy retriever is promoted",
            "promotion_gate": "a complex retriever must improve the frozen literature benchmark under the same query generator, corpus, cutoff, and budget",
            "domain_mismatch": "if a retriever loses under domain-matched evaluation, retain the simpler retriever and record the mismatch as a failure asset",
        },
    }
