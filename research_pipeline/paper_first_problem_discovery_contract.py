from __future__ import annotations

from typing import Any

from .paper_first_fresh_saturation import REDUCTION_PATTERNS


DISCOVERY_LANES: tuple[str, ...] = (
    "CONTRADICTION",
    "CONVERGENT_FAILURE",
    "ASSUMPTION_BREAK",
    "UNEXPLAINED_BOUNDARY",
)

FORBIDDEN_DISCOVERY_LANES: tuple[str, ...] = (
    "MISSING_CELL",
    "SHARED_LIMITATION",
    "PURE_TOPIC_BRAINSTORM",
)

SOURCE_EVIDENCE_ROLES: tuple[str, ...] = (
    "EMPIRICAL_FACT",
    "OPERATIONAL_ASSUMPTION",
)

LANE_SOURCE_ROLES: dict[str, tuple[str, str]] = {
    "CONTRADICTION": ("EMPIRICAL_FACT", "EMPIRICAL_FACT"),
    "CONVERGENT_FAILURE": ("EMPIRICAL_FACT", "EMPIRICAL_FACT"),
    "ASSUMPTION_BREAK": ("OPERATIONAL_ASSUMPTION", "EMPIRICAL_FACT"),
    "UNEXPLAINED_BOUNDARY": ("EMPIRICAL_FACT", "EMPIRICAL_FACT"),
}

LANE_EVIDENCE_REQUIRED: dict[str, tuple[str, ...]] = {
    "CONTRADICTION": (
        "shared_operationalization",
        "incompatibility",
    ),
    "CONVERGENT_FAILURE": (
        "shared_condition",
        "method_a",
        "method_b",
        "failure_a",
        "failure_b",
        "independence_basis",
    ),
    "ASSUMPTION_BREAK": (
        "assumption",
        "violation",
        "scope_link",
    ),
    "UNEXPLAINED_BOUNDARY": (
        "shared_measurement",
        "boundary_observation",
        "adjacent_regime",
        "unexplained_transition",
    ),
}

LANE_MACHINE_CONTRACTS: dict[str, str] = {
    "CONTRADICTION": "Two independently grounded empirical facts are incompatible under an explicitly shared operationalization.",
    "CONVERGENT_FAILURE": "Two independent method families show quantitative failure under the same bounded operational condition; the candidate names a common failure object rather than a better-method claim.",
    "ASSUMPTION_BREAK": "Source A contains an explicit operational assumption and independent source B contains empirical evidence that violates it in a scope-linked setting.",
    "UNEXPLAINED_BOUNDARY": "Primary evidence quantitatively establishes an anomalous boundary/regime and an adjacent expected regime for the same measured phenomenon; the candidate targets the unexplained transition.",
}

POLICY: dict[str, Any] = {
    "schema_version": "2.0",
    "multi_lane_discovery_required": True,
    "contradiction_first_required": False,
    "contradiction_lane_retained": True,
    "allowed_discovery_lanes": list(DISCOVERY_LANES),
    "forbidden_discovery_lanes": list(FORBIDDEN_DISCOVERY_LANES),
    "lane_specific_machine_evidence_contract_required": True,
    "two_primary_source_evidence_items_required": True,
    "shared_limitation_without_empirical_failure_forbidden": True,
    "pure_topic_brainstorm_forbidden": True,
    "open_world_missing_cell_claim_forbidden": True,
    "two_mature_theory_baselines_required": True,
    "same_information_nonreducibility_required": True,
    "domain_transfer_veto_required": True,
    "saturation_map_check_required": True,
    "problem_falsifier_required_before_method_design": True,
    "endpoint_headroom_required_before_terminal_interpretation": True,
    "independent_reviewer_must_verify_lane_contract": True,
    "no_lane_specific_downstream_relaxation": True,
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
    "discovery_lane",
    "empirical_evidence",
    "lane_evidence",
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
        "required": ["ref", "title", "claim", "evidence_role", "primary_source", "primary_url", "source_sha256"],
        "evidence_roles": list(SOURCE_EVIDENCE_ROLES),
        "primary_source_must_be_true": True,
        "source_sha256_must_match_primary_evidence_registry": True,
        "claim_must_be_primary_evidence_not_future_work": True,
    }


def candidate_schema() -> dict[str, Any]:
    return {
        "schema_version": "2.0",
        "required": list(REQUIRED_FIELDS),
        "discovery_lane": {
            "allowed": list(DISCOVERY_LANES),
            "forbidden": list(FORBIDDEN_DISCOVERY_LANES),
        },
        "empirical_evidence": {
            "required": ["source_a", "source_b", "relation"],
            "source_schema": source_schema(),
        },
        "lane_evidence": {
            "required_by_lane": {key: list(value) for key, value in LANE_EVIDENCE_REQUIRED.items()},
            "machine_contracts": dict(LANE_MACHINE_CONTRACTS),
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
            "matched_patterns_must_be_exact_known_keys_and_empty": True,
            "rejected_patterns_are_advisory_and_independently_reviewed": True,
            "invalid_entries_must_be_empty": True,
        },
        "semantic_reduction_review": {
            "required": [
                "reviewed",
                "block_only",
                "verdict",
                "reviewer_model",
                "raw_sha256",
                "source_claims_grounded",
                "source_claim_grounding",
                "lane_contract_verified",
            ],
            "verdict_must_be_clear": True,
            "reviewer_can_block_but_never_authorize": True,
            "both_source_claims_require_exact_primary_evidence_grounding": True,
            "lane_contract_must_be_independently_verified": True,
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


def _lane_contract_blockers(candidate: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    lane = str(candidate.get("discovery_lane") or "").strip().upper()
    if lane in FORBIDDEN_DISCOVERY_LANES:
        return [f"forbidden-discovery-lane:{lane}"]
    if lane not in DISCOVERY_LANES:
        return [f"unknown-discovery-lane:{lane or 'EMPTY'}"]

    evidence = candidate.get("empirical_evidence") or {}
    source_a = evidence.get("source_a") or {}
    source_b = evidence.get("source_b") or {}
    expected_roles = LANE_SOURCE_ROLES[lane]
    actual_roles = (
        str(source_a.get("evidence_role") or "").strip().upper(),
        str(source_b.get("evidence_role") or "").strip().upper(),
    )
    if actual_roles != expected_roles:
        blockers.append(
            "lane-source-role-mismatch:"
            + lane
            + ":expected="
            + "/".join(expected_roles)
            + ":actual="
            + "/".join(actual_roles)
        )

    lane_evidence = candidate.get("lane_evidence") or {}
    if not isinstance(lane_evidence, dict):
        blockers.append("lane-evidence-must-be-object")
        return blockers
    for key in LANE_EVIDENCE_REQUIRED[lane]:
        if not _nonempty(lane_evidence.get(key)):
            blockers.append(f"lane-evidence-missing:{lane}:{key}")

    # These are structural anti-shortcut checks. Independent semantic review still
    # decides whether the grounded source claims really support the relation.
    if lane == "CONVERGENT_FAILURE":
        if _normalized_evidence_text(lane_evidence.get("method_a")) == _normalized_evidence_text(lane_evidence.get("method_b")):
            blockers.append("convergent-failure-requires-distinct-methods")
    if lane == "ASSUMPTION_BREAK":
        if len(str(lane_evidence.get("assumption") or "").split()) < 4:
            blockers.append("assumption-break-requires-explicit-operational-assumption")
    return blockers


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

    lane = str(candidate.get("discovery_lane") or "").strip().upper()
    lane_blockers = _lane_contract_blockers(candidate)
    blockers.extend(lane_blockers)
    checks.append({"key": "discovery-lane-contract", "pass": not lane_blockers, "lane": lane})

    evidence = candidate.get("empirical_evidence") or {}
    sources = [evidence.get("source_a") or {}, evidence.get("source_b") or {}]
    source_refs: set[str] = set()
    registry = primary_evidence_by_ref or {}
    for idx, source in enumerate(sources, start=1):
        role = str(source.get("evidence_role") or "").strip().upper()
        passed = (
            all(_nonempty(source.get(key)) for key in ("ref", "title", "claim", "evidence_role", "primary_url", "source_sha256"))
            and role in SOURCE_EVIDENCE_ROLES
            and source.get("primary_source") is True
        )
        checks.append({"key": f"primary-source-{idx}", "pass": passed, "role": role})
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
        blockers.append("discovery-lane-requires-two-distinct-primary-sources")
    if not _nonempty(evidence.get("relation")):
        blockers.append("empirical-evidence-relation-missing")

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
    rejected = list(saturation.get("rejected_patterns") or []) if isinstance(saturation, dict) else []
    invalid_entries = list(saturation.get("invalid_entries") or []) if isinstance(saturation, dict) else []
    known = {row["key"] for row in REDUCTION_PATTERNS}
    unknown_matches = sorted(set(str(x) for x in matched) - known)
    if not isinstance(saturation, dict) or saturation.get("checked") is not True:
        blockers.append("saturation-scan-not-run")
    if matched:
        blockers.append("saturation-pattern-match:" + ",".join(sorted(str(x) for x in matched)))
    if unknown_matches:
        blockers.append("unknown-saturation-pattern:" + ",".join(unknown_matches))
    for row in rejected:
        if not isinstance(row,dict) or str(row.get("key") or "").strip() not in known or not _nonempty(row.get("reason")):
            blockers.append("invalid-rejected-saturation-pattern")
    if invalid_entries:
        blockers.append("invalid-saturation-scan-entry:" + ",".join(sorted(str(x) for x in invalid_entries)))

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
            if semantic_review.get("lane_contract_verified") is not True:
                blockers.append("lane-contract-independent-review-failed")
            if semantic_review.get("source_claims_grounded") is not True:
                blockers.append("source-claim-grounding-failed")
            grounding = semantic_review.get("source_claim_grounding") or {}
            if not isinstance(grounding, dict) or any((grounding.get(key) or {}).get("grounded") is not True for key in ("source_a", "source_b")):
                blockers.append("source-claim-grounding-incomplete")
            if require_primary_registry and isinstance(grounding, dict):
                for source_key in ("source_a", "source_b"):
                    source = evidence.get(source_key) or {}
                    ref = str(source.get("ref") or "").strip()
                    record = registry.get(ref) or {}
                    grounded = grounding.get(source_key) or {}
                    excerpt = str(grounded.get("evidence_excerpt") or "").strip()
                    words = excerpt.split()
                    abstract = _normalized_evidence_text(record.get("abstract") or "")
                    facts = [_normalized_evidence_text(str(fact.get("text") or "")) for fact in (record.get("empirical_facts") or []) if isinstance(fact, dict)]
                    typed = record.get("typed_evidence") or {}
                    assumptions = [_normalized_evidence_text(str(fact.get("text") or "")) for fact in typed.get("operational_assumptions") or [] if isinstance(fact, dict)]
                    failures = [_normalized_evidence_text(str(fact.get("text") or "")) for fact in typed.get("measured_failures") or [] if isinstance(fact, dict)]
                    boundaries = [_normalized_evidence_text(str(fact.get("text") or "")) for fact in typed.get("boundary_observations") or [] if isinstance(fact, dict)]
                    excerpt_norm = _normalized_evidence_text(excerpt)
                    evidence_source = str(grounded.get("evidence_source") or "").strip().lower()
                    role = str(source.get("evidence_role") or "").strip().upper()
                    abstract_match = bool(excerpt_norm and excerpt_norm in abstract)
                    fact_match = bool(excerpt_norm and any(excerpt_norm in fact for fact in facts))
                    assumption_match = bool(excerpt_norm and any(excerpt_norm in fact for fact in assumptions))
                    failure_match = bool(excerpt_norm and any(excerpt_norm in fact for fact in failures))
                    boundary_match = bool(excerpt_norm and any(excerpt_norm in fact for fact in boundaries))
                    fulltext_match = fact_match or assumption_match or failure_match or boundary_match
                    source_match = abstract_match if evidence_source == "abstract" else (fulltext_match if evidence_source == "fulltext" else (abstract_match or fulltext_match))
                    role_match = (role == "OPERATIONAL_ASSUMPTION" and assumption_match) or (role == "EMPIRICAL_FACT" and (abstract_match or fact_match or failure_match or boundary_match))
                    if not (4 <= len(words) <= 30 and source_match and role_match):
                        blockers.append(f"source-claim-evidence-excerpt-mismatch:{source_key}")
            if not _nonempty(semantic_review.get("reviewer_model")) or not _nonempty(semantic_review.get("raw_sha256")):
                blockers.append("semantic-reduction-review-provenance-missing")

    authority = candidate.get("authority") or {}
    for key in ("method_design", "experiment_blueprint", "local_validation", "p0", "gpu", "full_experiment"):
        if authority.get(key) is not False:
            blockers.append(f"authority-must-be-false:{key}")

    blockers = sorted(set(blockers))
    return {
        "schema_version": "2.0",
        "candidate_id": str(candidate.get("candidate_id") or ""),
        "discovery_lane": lane,
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
        "schema_version": "2.0",
        "policy": POLICY,
        "candidate_schema": candidate_schema(),
        "summary": {
            "required_top_level_fields": len(REQUIRED_FIELDS),
            "allowed_discovery_lanes": len(DISCOVERY_LANES),
            "forbidden_discovery_lanes": len(FORBIDDEN_DISCOVERY_LANES),
            "saturation_patterns": len(REDUCTION_PATTERNS),
            "minimum_primary_sources": 2,
            "minimum_mature_theory_baselines": 2,
            "automatic_method_authority": 0,
            "automatic_experiment_authority": 0,
        },
        "lane_contracts": [
            {
                "lane": lane,
                "source_roles": list(LANE_SOURCE_ROLES[lane]),
                "required_lane_evidence": list(LANE_EVIDENCE_REQUIRED[lane]),
                "machine_contract": LANE_MACHINE_CONTRACTS[lane],
            }
            for lane in DISCOVERY_LANES
        ],
        "generator_order": [
            "select one allowed discovery lane from grounded primary evidence",
            "satisfy the lane-specific machine evidence contract before naming a new object",
            "name two strongest mature theories before naming a new object",
            "project identical observable information into each mature theory",
            "state one exact prediction neither theory can express",
            "run saturation/domain-transfer veto",
            "freeze cheapest problem falsifier and endpoint headroom",
            "require independent lane-contract + exact source grounding review",
            "audit problem candidate",
            "human paper-design review only if problem gate passes",
        ],
    }
