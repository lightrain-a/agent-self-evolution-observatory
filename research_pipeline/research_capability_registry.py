from __future__ import annotations

import re
from typing import Any, Iterable


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
    "third_party_skill_requires_admission_certificate_before_routing": True,
    "skill_router_selects_least_privilege_sufficient_skill": True,
    "skill_pack_orchestrator_never_becomes_a_second_research_os": True,
    "skill_capability_never_implies_scientific_experiment_gpu_or_submission_authority": True,
    "unqualified_skill_cannot_be_silently_loaded": True,
}

REFERENCES = [
    {"system": "Biomni", "adopted": "declarative tool-description schemas plus a tool registry for dynamic registration and lookup"},
    {"system": "BioMedAgent", "adopted": "learn tool/workflow choice through interactive exploration and reusable memory instead of a fixed hand-written chain"},
    {"system": "PaperQA2", "adopted": "separate scientific search, evidence gathering, and answer synthesis while preserving grounded citations and metadata"},
    {"system": "SAGE", "adopted": "co-design agent subqueries and retriever choice; a stronger retriever is not automatically better when the query generator emits keyword-like queries"},
]

SKILL_DATA_ACCESS_LEVELS = ("NONE", "VERIFIED_ONLY", "REDACTED", "RAW")
SKILL_EXECUTION_MODES = ("DETERMINISTIC", "AGENTIC", "HYBRID")
SKILL_CAPABILITY_TYPES = (
    "literature", "citation", "statistics", "experiment", "coding", "writing",
    "reviewing", "visualization", "causal-inference", "signal-processing", "ml-research",
)

SKILL_PACK_CATALOG: tuple[dict[str, Any], ...] = (
    {"skill_pack": "Academic Research Skills", "status": "CATALOGUED_NOT_INSTALLED", "capabilities": ["citation", "reviewing", "writing"], "role": "integrity and academic research support"},
    {"skill_pack": "Scientific Agent Skills", "status": "CATALOGUED_NOT_INSTALLED", "capabilities": ["statistics", "experiment", "coding"], "role": "domain scientific execution"},
    {"skill_pack": "nature-skills", "status": "CATALOGUED_NOT_INSTALLED", "capabilities": ["writing", "reviewing", "visualization"], "role": "evidence-first manuscript drafting and polishing"},
    {"skill_pack": "Claude Scholar", "status": "CATALOGUED_NOT_INSTALLED", "capabilities": ["literature", "citation", "reviewing"], "role": "literature management and reference checks"},
    {"skill_pack": "Auto-Empirical Research Skills", "status": "CATALOGUED_NOT_INSTALLED", "capabilities": ["statistics", "causal-inference", "coding"], "role": "social-science empirical methods"},
    {"skill_pack": "AI-Research-SKILLs", "status": "CATALOGUED_NOT_INSTALLED", "capabilities": ["ml-research", "experiment", "coding"], "role": "AI/ML domain execution; orchestration authority explicitly excluded"},
    {"skill_pack": "codex-claude-academic-skills", "status": "CATALOGUED_NOT_INSTALLED", "capabilities": ["signal-processing", "statistics", "coding"], "role": "MATLAB/Python engineering analysis"},
    {"skill_pack": "Research Paper Writing Skills", "status": "CATALOGUED_NOT_INSTALLED", "capabilities": ["writing", "reviewing"], "role": "paper structure and editorial policy"},
)


def _skill_risk_score(manifest: dict[str, Any]) -> int:
    access = str(manifest.get("data_access_level") or "NONE").upper()
    score = {"NONE": 0, "VERIFIED_ONLY": 1, "REDACTED": 2, "RAW": 3}.get(access, 4)
    for key, weight in (
        ("external_network_access", 2), ("filesystem_write_access", 2),
        ("code_execution", 3), ("gpu_access", 4), ("secret_access", 5),
    ):
        score += weight if manifest.get(key) is True else 0
    return score


def build_skill_admission_certificate(manifest: dict[str, Any]) -> dict[str, Any]:
    """Qualify a third-party/local skill as a capability provider, never as a scientific authority."""
    source = str(manifest.get("source_repository") or "").strip()
    revision = str(manifest.get("commit_sha") or manifest.get("revision_sha256") or "").strip().lower()
    capability_types = sorted({str(x).strip().lower() for x in manifest.get("capability_types") or [] if str(x).strip()})
    blockers: list[str] = []
    for key in ("skill_id", "skill_version", "license", "maintainer"):
        if not str(manifest.get(key) or "").strip():
            blockers.append(f"skill-manifest-missing:{key}")
    if not source:
        blockers.append("skill-source-repository-missing")
    if not (re.fullmatch(r"[0-9a-f]{40}", revision) or re.fullmatch(r"[0-9a-f]{64}", revision)):
        blockers.append("skill-source-revision-must-be-content-addressed")
    if not capability_types:
        blockers.append("skill-capability-types-missing")
    invalid_caps = sorted(set(capability_types) - set(SKILL_CAPABILITY_TYPES))
    if invalid_caps:
        blockers.append("skill-capability-types-invalid:" + ",".join(invalid_caps))
    data_access = str(manifest.get("data_access_level") or "").upper()
    if data_access not in SKILL_DATA_ACCESS_LEVELS:
        blockers.append("skill-data-access-level-invalid")
    mode = str(manifest.get("execution_mode") or "").upper()
    if mode not in SKILL_EXECUTION_MODES:
        blockers.append("skill-execution-mode-invalid")
    for key in ("external_network_access", "filesystem_write_access", "code_execution", "gpu_access", "secret_access"):
        if not isinstance(manifest.get(key), bool):
            blockers.append(f"skill-permission-must-be-explicit-bool:{key}")
    artifacts = [str(x).strip() for x in manifest.get("expected_artifacts") or [] if str(x).strip()]
    if not artifacts:
        blockers.append("skill-expected-artifacts-missing")
    smoke = manifest.get("smoke") if isinstance(manifest.get("smoke"), dict) else {}
    if smoke.get("passed") is not True or not str(smoke.get("artifact_ref") or "").strip():
        blockers.append("skill-smoke-not-passed-with-artifact")
    if manifest.get("requests_scientific_authority") is True or manifest.get("requests_experiment_authority") is True:
        blockers.append("skill-cannot-request-scientific-or-experiment-authority")
    risk_score = _skill_risk_score(manifest)
    status = "SKILL_QUALIFIED" if not blockers else "SKILL_ADMISSION_HOLD"
    return {
        "schema_version": "1.0",
        "skill_id": str(manifest.get("skill_id") or ""),
        "skill_version": str(manifest.get("skill_version") or ""),
        "source_repository": source,
        "source_revision": revision,
        "license": str(manifest.get("license") or ""),
        "maintainer": str(manifest.get("maintainer") or ""),
        "capability_types": capability_types,
        "data_access_level": data_access,
        "execution_mode": mode,
        "permissions": {key: manifest.get(key) is True for key in ("external_network_access", "filesystem_write_access", "code_execution", "gpu_access", "secret_access")},
        "expected_artifacts": artifacts,
        "smoke": dict(smoke),
        "risk_score": risk_score,
        "status": status,
        "blockers": sorted(set(blockers)),
        "sandbox_required": risk_score > 0,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }


def route_research_skills(requirements: dict[str, Any], certificates: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Select the least-privilege qualified skill set for declared capability requirements."""
    required = sorted({str(x).strip().lower() for x in requirements.get("capability_types") or [] if str(x).strip()})
    max_access = str(requirements.get("max_data_access_level") or "RAW").upper()
    access_rank = {name: index for index, name in enumerate(SKILL_DATA_ACCESS_LEVELS)}
    blockers: list[str] = []
    if max_access not in access_rank:
        blockers.append("router-max-data-access-invalid")
    invalid = sorted(set(required) - set(SKILL_CAPABILITY_TYPES))
    if invalid:
        blockers.append("router-capability-invalid:" + ",".join(invalid))
    qualified = []
    for cert in certificates:
        if not isinstance(cert, dict) or cert.get("status") != "SKILL_QUALIFIED":
            continue
        if max_access in access_rank and access_rank.get(str(cert.get("data_access_level") or "RAW"), 99) > access_rank[max_access]:
            continue
        qualified.append(cert)
    selected: list[dict[str, Any]] = []
    uncovered = set(required)
    while uncovered:
        candidates = []
        for cert in qualified:
            covers = uncovered.intersection(set(cert.get("capability_types") or []))
            if covers:
                candidates.append((int(cert.get("risk_score") or 0), -len(covers), str(cert.get("skill_id") or ""), cert, covers))
        if not candidates:
            break
        _, _, _, cert, covers = min(candidates)
        selected.append({"skill_id": cert.get("skill_id"), "skill_version": cert.get("skill_version"), "covers": sorted(covers), "risk_score": cert.get("risk_score"), "source_revision": cert.get("source_revision")})
        uncovered -= covers
    if uncovered:
        blockers.append("required-skill-capability-unavailable:" + ",".join(sorted(uncovered)))
    return {
        "schema_version": "1.0",
        "status": "SKILL_ROUTE_READY" if not blockers else "SKILL_ROUTE_HOLD",
        "required_capabilities": required,
        "selected_skills": selected,
        "uncovered_capabilities": sorted(uncovered),
        "blockers": blockers,
        "selection_rule": "least-privilege sufficient qualified set; no silent generic fallback",
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }


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
            "skill_packs_catalogued_not_installed": len(SKILL_PACK_CATALOG),
            "skill_admission_contract_installed": 1,
            "skill_router_contract_installed": 1,
            "automatic_skill_authority": 0,
        },
        "skill_pack_catalog": list(SKILL_PACK_CATALOG),
        "skill_admission_contract": {
            "required_identity": ["skill_id", "skill_version", "source_repository", "content-addressed revision", "license", "maintainer"],
            "required_permissions": ["data_access_level", "external_network_access", "filesystem_write_access", "code_execution", "gpu_access", "secret_access"],
            "required_validation": ["capability_types", "expected_artifacts", "smoke artifact"],
            "authority": {"scientific": False, "experiment": False, "gpu": False, "submission": False},
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
