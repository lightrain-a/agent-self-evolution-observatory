from __future__ import annotations

from typing import Any

from .paper_first_fresh_saturation import REDUCTION_PATTERNS


POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "contradiction_first_required": True,
    "two_primary_source_facts_required": True,
    "two_mature_theory_baselines_required": True,
    "same_information_nonreducibility_required": True,
    "domain_transfer_veto_required": True,
    "saturation_map_check_required": True,
    "problem_falsifier_required_before_method_design": True,
    "endpoint_headroom_required_before_terminal_interpretation": True,
    "ai_generation_is_advisory_only": True,
    "zero_survivors_is_valid": True,
    "method_design_authorized_by_problem_gate": False,
    "local_validation_authorized_by_problem_gate": False,
    "p0_authorized_by_problem_gate": False,
    "gpu_authorized_by_problem_gate": False,
}

REQUIRED_FIELDS = (
    "candidate_id",
    "title",
    "empirical_contradiction",
    "irreducible_object",
    "mature_theory_baselines",
    "same_information_nonreducibility",
    "exact_prediction",
    "strongest_same_information_baseline",
    "domain_transfer_audit",
    "saturation_scan",
    "cheapest_problem_falsifier",
    "endpoint_headroom_requirement",
    "semantic_reduction_review",
    "authority",
)


def source_schema() -> dict[str, Any]:
    return {
        "required": ["ref", "title", "claim", "primary_source", "primary_url", "source_sha256"],
        "primary_source_must_be_true": True,
        "source_sha256_must_match_primary_evidence_registry": True,
        "claim_must_be_observation_not_future_work": True,
    }


def candidate_schema() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "required": list(REQUIRED_FIELDS),
        "empirical_contradiction": {
            "required": ["source_a", "source_b", "tension"],
            "source_schema": source_schema(),
        },
        "mature_theory_baselines": {
            "minimum": 2,
            "each_required": ["name", "same_information_projection", "reduction_test"],
        },
        "same_information_nonreducibility": {
            "required": ["claim", "why_each_baseline_cannot_express_prediction"],
        },
        "domain_transfer_audit": {
            "required": ["mature_source_domain", "mature_object", "why_not_domain_transfer"],
        },
        "saturation_scan": {
            "required": ["checked", "matched_patterns"],
            "known_patterns": [row["key"] for row in REDUCTION_PATTERNS],
            "matched_patterns_must_be_empty": True,
        },
        "semantic_reduction_review": {
            "required": ["reviewed", "block_only", "verdict", "reviewer_model", "raw_sha256", "source_claims_grounded", "source_claim_grounding"],
            "verdict_must_be_clear": True,
            "reviewer_can_block_but_never_authorize": True,
            "both_source_claims_require_exact_primary_abstract_grounding": True,
        },
        "authority": {
            "required_false": ["method_design", "experiment_blueprint", "local_validation", "p0", "gpu", "full_experiment"],
        },
    }


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return value is not None


def _normalized_evidence_text(value: Any) -> str:
    return " ".join(str(value or "").lower().split())


def audit_problem_candidate(
    candidate: dict[str, Any],
    *,
    primary_evidence_by_ref: dict[str, dict[str, Any]] | None = None,
    require_primary_registry: bool = False,
    require_semantic_review: bool = True,
) -> dict[str, Any]:
    blockers: list[str] = []
    checks: list[dict[str, Any]] = []

    for key in REQUIRED_FIELDS:
        passed = key in candidate and _nonempty(candidate.get(key))
        checks.append({"key": f"field:{key}", "pass": passed})
        if not passed:
            blockers.append(f"missing-or-empty:{key}")

    contradiction = candidate.get("empirical_contradiction") or {}
    sources = [contradiction.get("source_a") or {}, contradiction.get("source_b") or {}]
    source_refs: set[str] = set()
    registry = primary_evidence_by_ref or {}
    for idx, source in enumerate(sources, start=1):
        passed = all(_nonempty(source.get(key)) for key in ("ref", "title", "claim", "primary_url", "source_sha256")) and source.get("primary_source") is True
        checks.append({"key": f"primary-source-{idx}", "pass": passed})
        if not passed:
            blockers.append(f"invalid-primary-source:{idx}")
        ref = str(source.get("ref") or "").strip()
        if ref:
            source_refs.add(ref)
        if require_primary_registry:
            record = registry.get(ref)
            if not record:
                blockers.append(f"primary-source-not-in-registry:{idx}")
            else:
                if str(source.get("source_sha256") or "") != str(record.get("source_sha256") or ""):
                    blockers.append(f"primary-source-sha-mismatch:{idx}")
                if str(source.get("primary_url") or "") != str(record.get("primary_url") or ""):
                    blockers.append(f"primary-source-url-mismatch:{idx}")
                if str(source.get("title") or "").strip() != str(record.get("title") or "").strip():
                    blockers.append(f"primary-source-title-mismatch:{idx}")
    if len(source_refs) != 2:
        blockers.append("contradiction-requires-two-distinct-primary-sources")
    if not _nonempty(contradiction.get("tension")):
        blockers.append("empirical-contradiction-tension-missing")

    baselines = candidate.get("mature_theory_baselines") or []
    if not isinstance(baselines, list) or len(baselines) < 2:
        blockers.append("need-at-least-two-mature-theory-baselines")
    else:
        for idx, row in enumerate(baselines, start=1):
            if not isinstance(row, dict) or not all(_nonempty(row.get(key)) for key in ("name", "same_information_projection", "reduction_test")):
                blockers.append(f"invalid-mature-theory-baseline:{idx}")

    nonred = candidate.get("same_information_nonreducibility") or {}
    if not isinstance(nonred, dict) or not _nonempty(nonred.get("claim")) or not _nonempty(nonred.get("why_each_baseline_cannot_express_prediction")):
        blockers.append("same-information-nonreducibility-incomplete")

    domain = candidate.get("domain_transfer_audit") or {}
    if not isinstance(domain, dict) or not all(_nonempty(domain.get(key)) for key in ("mature_source_domain", "mature_object", "why_not_domain_transfer")):
        blockers.append("domain-transfer-audit-incomplete")

    saturation = candidate.get("saturation_scan") or {}
    matched = list(saturation.get("matched_patterns") or []) if isinstance(saturation, dict) else []
    known = {row["key"] for row in REDUCTION_PATTERNS}
    unknown_matches = sorted(set(str(x) for x in matched) - known)
    if not isinstance(saturation, dict) or saturation.get("checked") is not True:
        blockers.append("saturation-scan-not-run")
    if matched:
        blockers.append("saturation-pattern-match:" + ",".join(sorted(str(x) for x in matched)))
    if unknown_matches:
        blockers.append("unknown-saturation-pattern:" + ",".join(unknown_matches))

    if not _nonempty(candidate.get("exact_prediction")):
        blockers.append("exact-prediction-missing")
    if not _nonempty(candidate.get("strongest_same_information_baseline")):
        blockers.append("strongest-same-information-baseline-missing")
    if not _nonempty(candidate.get("cheapest_problem_falsifier")):
        blockers.append("problem-falsifier-missing")
    if not _nonempty(candidate.get("endpoint_headroom_requirement")):
        blockers.append("endpoint-headroom-missing")

    if require_semantic_review:
        semantic_review = candidate.get("semantic_reduction_review") or {}
        if not isinstance(semantic_review, dict) or semantic_review.get("reviewed") is not True or semantic_review.get("block_only") is not True:
            blockers.append("semantic-reduction-review-missing")
        else:
            verdict = str(semantic_review.get("verdict") or "").upper()
            if verdict != "CLEAR":
                blockers.append("semantic-reduction-review-block")
            if semantic_review.get("source_claims_grounded") is not True:
                blockers.append("source-claim-grounding-failed")
            grounding = semantic_review.get("source_claim_grounding") or {}
            if not isinstance(grounding, dict) or any((grounding.get(key) or {}).get("grounded") is not True for key in ("source_a", "source_b")):
                blockers.append("source-claim-grounding-incomplete")
            if require_primary_registry and isinstance(grounding, dict):
                for source_key in ("source_a", "source_b"):
                    source = contradiction.get(source_key) or {}
                    ref = str(source.get("ref") or "").strip()
                    record = registry.get(ref) or {}
                    grounded = grounding.get(source_key) or {}
                    excerpt = str(grounded.get("evidence_excerpt") or "").strip()
                    words = excerpt.split()
                    abstract = _normalized_evidence_text(record.get("abstract") or "")
                    excerpt_norm = _normalized_evidence_text(excerpt)
                    if not (4 <= len(words) <= 30 and excerpt_norm and excerpt_norm in abstract):
                        blockers.append(f"source-claim-evidence-excerpt-mismatch:{source_key}")
            if not _nonempty(semantic_review.get("reviewer_model")) or not _nonempty(semantic_review.get("raw_sha256")):
                blockers.append("semantic-reduction-review-provenance-missing")

    authority = candidate.get("authority") or {}
    for key in ("method_design", "experiment_blueprint", "local_validation", "p0", "gpu", "full_experiment"):
        if authority.get(key) is not False:
            blockers.append(f"authority-must-be-false:{key}")

    blockers = sorted(set(blockers))
    return {
        "schema_version": "1.0",
        "candidate_id": str(candidate.get("candidate_id") or ""),
        "passed": not blockers,
        "status": "PROBLEM_GATE_PASS_AWAIT_HUMAN_PAPER_DESIGN" if not blockers else "PROBLEM_GATE_BLOCKED",
        "blockers": blockers,
        "checks": checks,
        "policy": POLICY,
        "authority": {
            "paper_design_eligible_for_human_review": not blockers,
            "method_design": False,
            "experiment_blueprint": False,
            "local_validation": False,
            "p0": False,
            "gpu": False,
            "full_experiment": False,
        },
    }


def build_problem_discovery_contract_state() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "policy": POLICY,
        "candidate_schema": candidate_schema(),
        "summary": {
            "required_top_level_fields": len(REQUIRED_FIELDS),
            "saturation_patterns": len(REDUCTION_PATTERNS),
            "minimum_primary_sources": 2,
            "minimum_mature_theory_baselines": 2,
            "automatic_method_authority": 0,
            "automatic_experiment_authority": 0,
        },
        "generator_order": [
            "identify empirical contradiction from two primary sources",
            "name two strongest mature theories before naming a new object",
            "project identical observable information into each mature theory",
            "state one exact prediction neither theory can express",
            "run saturation/domain-transfer veto",
            "freeze cheapest problem falsifier and endpoint headroom",
            "audit problem candidate",
            "human paper-design review only if problem gate passes",
        ],
    }
