from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


PAPER_PREPARATION_PROTOCOL_VERSION = "1.0"

PAPER_PREPARATION_GATE_KEYS: tuple[str, ...] = (
    "hierarchical-rubric",
    "verification-refinement",
    "citation-integrity",
    "visual-story",
    "reproducibility-bundle",
    "agent-native-artifact",
    "reader-simulation",
    "submission-package",
)

REQUIRED_RUBRIC_DIMENSIONS: tuple[str, ...] = (
    "claim-evidence",
    "novelty-positioning",
    "method-experiment",
    "statistics-uncertainty",
    "visual-evidence",
    "limitations-scope",
    "reproducibility",
    "citation-integrity",
    "venue-compliance",
)

REQUIRED_AGENT_NATIVE_LAYERS: tuple[str, ...] = (
    "scientific-logic",
    "executable-specification",
    "exploration-graph",
    "claim-evidence-grounding",
)

REQUIRED_READER_MODES: tuple[str, ...] = (
    "blind-manuscript",
    "artifact-aware",
    "figure-first-skimmer",
    "reproducibility-reviewer",
)

POLICY: dict[str, Any] = {
    "schema_version": PAPER_PREPARATION_PROTOCOL_VERSION,
    "paper_preparation_is_subprotocol_not_new_scientific_authority": True,
    "legacy_paper_contracts_remain_replayable": True,
    "opt_in_contracts_fail_closed_before_submission_ready": True,
    "hierarchical_rubric_precedes_single_score": True,
    "verification_and_refinement_are_separate_roles": True,
    "citation_existence_relevance_and_placement_must_be_verified": True,
    "figure_caption_reference_review_is_independent_from_prose_review": True,
    "reproducibility_requires_clean_environment_smoke": True,
    "agent_native_artifact_preserves_failures_and_claim_grounding": True,
    "reader_simulation_uses_multiple_reading_modes": True,
    "submission_package_is_venue_specific_and_self_contained": True,
    "ai_use_disclosure_decision_is_recorded_but_venue_policy_controls_wording": True,
    "human_submission_authority_remains_external": True,
}

INSPIRATIONS: tuple[dict[str, str], ...] = (
    {
        "system": "The AI Scientist-v2",
        "adopted_principle": "Separate write-up, citation gathering, paper review, plot aggregation, and image/caption/reference review.",
    },
    {
        "system": "Agent Laboratory",
        "adopted_principle": "Treat report writing as a distinct research phase and preserve an explicit human-feedback checkpoint option.",
    },
    {
        "system": "PaperBench",
        "adopted_principle": "Decompose paper completion into hierarchical, individually auditable rubric items instead of relying on one overall score.",
    },
    {
        "system": "Agent-Native Research Artifact (ARA)",
        "adopted_principle": "Package scientific logic, executable specification, exploration/failure history, and claim-to-raw-evidence grounding together.",
    },
    {
        "system": "Collaborative verification/refinement agents",
        "adopted_principle": "Verify each stage against its frozen contract and let a separate refiner repair only identified issues.",
    },
    {
        "system": "ResearchTown / FARS / AutoR",
        "adopted_principle": "Use independent writing/review roles, preserve intermediate artifacts, and require adversarial review findings to be answered before final export.",
    },
    {
        "system": "Story2Proposal",
        "adopted_principle": "Maintain a persistent manuscript/visual contract across architect, writer, refiner, renderer, and evaluation roles.",
    },
    {
        "system": "ResearchArena / ARI",
        "adopted_principle": "Artifact-aware review checks plan/execution parity and result integrity; deterministic gates re-compute numeric claims and independent reproduction verifies the package.",
    },
)


def _digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _texts(value: Any) -> list[str]:
    return [str(item).strip() for item in value if str(item).strip()] if isinstance(value, (list, tuple)) else []


def _gate_result(key: str, blockers: list[str], detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "gate": key,
        "pass": not blockers,
        "blockers": list(dict.fromkeys(blockers)),
        "detail": dict(detail or {}),
        "scientific_authority": False,
    }


def evaluate_hierarchical_rubric(section: Mapping[str, Any]) -> dict[str, Any]:
    row = _mapping(section)
    blockers: list[str] = []
    dimensions = _mapping(row.get("dimensions"))
    for name in REQUIRED_RUBRIC_DIMENSIONS:
        item = _mapping(dimensions.get(name))
        if item.get("pass") is not True:
            blockers.append(f"rubric-dimension-not-pass:{name}")
        if not _texts(item.get("evidence_refs")):
            blockers.append(f"rubric-dimension-missing-evidence:{name}")
    if row.get("hierarchical_decomposition") is not True:
        blockers.append("rubric-not-hierarchically-decomposed")
    if row.get("single_overall_score_is_non_authoritative") is not True:
        blockers.append("rubric-single-score-could-bypass-items")
    for key in ("plan_execution_parity_pass", "fabricated_result_scan_pass", "evidence_sufficiency_review_pass"):
        if row.get(key) is not True:
            blockers.append(f"rubric-integrity-check-failed:{key}")
    return _gate_result("hierarchical-rubric", blockers, {"dimensions": len(dimensions)})


def evaluate_verification_refinement(section: Mapping[str, Any]) -> dict[str, Any]:
    row = _mapping(section)
    blockers: list[str] = []
    issues = [item for item in row.get("issues") or [] if isinstance(item, Mapping)]
    critical = {str(item.get("issue_id") or "") for item in issues if item.get("decision_critical") is True and str(item.get("issue_id") or "")}
    resolved = set(_texts(row.get("resolved_issue_ids")))
    deltas = [item for item in row.get("revision_deltas") or [] if isinstance(item, Mapping)]
    delta_issue_ids = {str(item.get("issue_id") or "") for item in deltas if str(item.get("issue_id") or "")}
    if row.get("verifier_separate_from_refiner") is not True:
        blockers.append("verifier-refiner-role-separation-missing")
    if row.get("verification_against_frozen_contract") is not True:
        blockers.append("verification-not-bound-to-frozen-contract")
    for issue_id in sorted(critical - resolved):
        blockers.append(f"unresolved-critical-verification-issue:{issue_id}")
    for issue_id in sorted(resolved - delta_issue_ids):
        blockers.append(f"resolved-issue-missing-revision-delta:{issue_id}")
    if row.get("non_improving_revision_reverted") is not True:
        blockers.append("non-improving-revision-revert-policy-missing")
    return _gate_result("verification-refinement", blockers, {"issues": len(issues), "critical": len(critical), "resolved": len(resolved)})


def evaluate_citation_integrity(section: Mapping[str, Any]) -> dict[str, Any]:
    row = _mapping(section)
    blockers: list[str] = []
    total = int(row.get("citations_total") or 0)
    verified = int(row.get("citations_verified") or 0)
    primary_claim = int(row.get("claim_citations_primary_source_verified") or 0)
    primary_claim_total = int(row.get("claim_citations_total") or 0)
    if total <= 0:
        blockers.append("citation-set-empty")
    if verified != total:
        blockers.append("citation-existence-or-metadata-unverified")
    if primary_claim_total and primary_claim != primary_claim_total:
        blockers.append("claim-citation-primary-source-unverified")
    for key in (
        "duplicate_citations_absent",
        "orphan_bib_entries_absent",
        "citation_placement_review_pass",
        "citation_claim_entailment_review_pass",
    ):
        if row.get(key) is not True:
            blockers.append(f"citation-check-failed:{key}")
    if row.get("hallucinated_citations") not in (0, None):
        blockers.append("hallucinated-citations-present")
    return _gate_result("citation-integrity", blockers, {"citations_total": total, "citations_verified": verified})


def evaluate_visual_story(section: Mapping[str, Any]) -> dict[str, Any]:
    row = _mapping(section)
    blockers: list[str] = []
    main_visuals = int(row.get("main_visuals") or 0)
    if main_visuals < 1:
        blockers.append("main-visual-missing")
    for key in (
        "each_core_claim_has_main_visual",
        "figure_caption_reference_review_pass",
        "figure_text_callout_consistency_pass",
        "quantitative_visual_source_binding_pass",
        "negative_or_boundary_evidence_visible",
        "labels_legible_at_final_pdf_scale",
        "persistent_visual_contract_present",
        "registered_visuals_match_sections",
    ):
        if row.get(key) is not True:
            blockers.append(f"visual-story-check-failed:{key}")
    return _gate_result("visual-story", blockers, {"main_visuals": main_visuals})


def evaluate_reproducibility_bundle(section: Mapping[str, Any]) -> dict[str, Any]:
    row = _mapping(section)
    blockers: list[str] = []
    for key in (
        "self_contained_source_bundle",
        "clean_environment_compile_pass",
        "reproduction_entrypoint_present",
        "dependency_environment_manifest_present",
        "data_model_provenance_present",
        "random_seed_and_nondeterminism_documented",
        "evaluation_code_and_protocol_bound",
        "artifact_hash_manifest_present",
        "numeric_claim_recompute_pass",
        "independent_reproduction_check_pass",
        "secret_scan_pass",
    ):
        if row.get(key) is not True:
            blockers.append(f"reproducibility-check-failed:{key}")
    return _gate_result("reproducibility-bundle", blockers)


def evaluate_agent_native_artifact(section: Mapping[str, Any]) -> dict[str, Any]:
    row = _mapping(section)
    blockers: list[str] = []
    layers = _mapping(row.get("layers"))
    for layer in REQUIRED_AGENT_NATIVE_LAYERS:
        item = _mapping(layers.get(layer))
        if item.get("complete") is not True:
            blockers.append(f"agent-native-layer-incomplete:{layer}")
        if not _texts(item.get("artifact_refs")):
            blockers.append(f"agent-native-layer-missing-artifact:{layer}")
    if row.get("failed_and_rejected_branches_preserved") is not True:
        blockers.append("exploration-failures-not-preserved")
    if row.get("claim_to_raw_output_roundtrip_pass") is not True:
        blockers.append("claim-raw-output-roundtrip-failed")
    return _gate_result("agent-native-artifact", blockers, {"layers": len(layers)})


def evaluate_reader_simulation(section: Mapping[str, Any]) -> dict[str, Any]:
    row = _mapping(section)
    blockers: list[str] = []
    modes = _mapping(row.get("modes"))
    for mode in REQUIRED_READER_MODES:
        item = _mapping(modes.get(mode))
        if item.get("completed") is not True:
            blockers.append(f"reader-mode-incomplete:{mode}")
        unresolved = int(item.get("unresolved_decision_critical") or 0)
        if unresolved:
            blockers.append(f"reader-mode-unresolved-critical:{mode}:{unresolved}")
    if row.get("paper_side_findings_resolved_or_explicitly_accepted") is not True:
        blockers.append("reader-paper-side-findings-not-closed")
    if row.get("review_score_is_not_a_hard_gate") is not True:
        blockers.append("reader-score-could-substitute-for-objection-resolution")
    return _gate_result("reader-simulation", blockers, {"modes": len(modes)})


def evaluate_submission_package(section: Mapping[str, Any]) -> dict[str, Any]:
    row = _mapping(section)
    blockers: list[str] = []
    if not _text(row.get("venue")):
        blockers.append("submission-venue-missing")
    for key in (
        "venue_template_and_page_rules_pass",
        "anonymous_source_and_pdf_pass",
        "metadata_matches_manuscript",
        "supplement_and_main_artifact_consistency_pass",
        "fresh_directory_source_compile_pass",
        "file_size_and_upload_constraints_pass",
        "ai_use_disclosure_decision_recorded",
        "authorship_and_conflict_checklist_recorded",
        "venue_policy_snapshot_current",
        "human_only_requirements_recorded",
    ):
        if row.get(key) is not True:
            blockers.append(f"submission-package-check-failed:{key}")
    if row.get("external_human_submit_required") is not True:
        blockers.append("external-human-submit-boundary-missing")
    return _gate_result("submission-package", blockers, {"venue": _text(row.get("venue"))})


_GATE_EVALUATORS = {
    "hierarchical-rubric": evaluate_hierarchical_rubric,
    "verification-refinement": evaluate_verification_refinement,
    "citation-integrity": evaluate_citation_integrity,
    "visual-story": evaluate_visual_story,
    "reproducibility-bundle": evaluate_reproducibility_bundle,
    "agent-native-artifact": evaluate_agent_native_artifact,
    "reader-simulation": evaluate_reader_simulation,
    "submission-package": evaluate_submission_package,
}


def evaluate_paper_preparation(packet: Mapping[str, Any] | None) -> dict[str, Any]:
    packet = _mapping(packet)
    blockers: list[str] = []
    if _text(packet.get("protocol_version")) != PAPER_PREPARATION_PROTOCOL_VERSION:
        blockers.append("paper-preparation-protocol-version-missing-or-stale")
    gates = _mapping(packet.get("gates"))
    results: dict[str, Any] = {}
    for key in PAPER_PREPARATION_GATE_KEYS:
        result = _GATE_EVALUATORS[key](_mapping(gates.get(key)))
        results[key] = result
        blockers.extend(result["blockers"])
    if packet.get("claim_expansion_authorized") is not False:
        blockers.append("paper-preparation-must-not-authorize-claim-expansion")
    if packet.get("new_experiment_authorized") is not False:
        blockers.append("paper-preparation-must-not-authorize-new-experiment")
    return {
        "schema_version": PAPER_PREPARATION_PROTOCOL_VERSION,
        "pass": not blockers,
        "blockers": list(dict.fromkeys(blockers)),
        "gates": results,
        "summary": {
            "required_gates": len(PAPER_PREPARATION_GATE_KEYS),
            "passed_gates": sum(result.get("pass") is True for result in results.values()),
        },
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }


def paper_preparation_receipt_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "protocol_version": receipt.get("protocol_version"),
        "packet_sha256": receipt.get("packet_sha256"),
        "pass": receipt.get("pass"),
        "blockers": receipt.get("blockers") or [],
        "gate_pass": receipt.get("gate_pass") or {},
    }


def build_paper_preparation_receipt(
    *,
    paper_id: str,
    contract_sha256: str,
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    result = evaluate_paper_preparation(packet)
    gate_pass = {key: value.get("pass") is True for key, value in result["gates"].items()}
    receipt: dict[str, Any] = {
        "schema_version": "1.0",
        "receipt_type": "paper-preparation",
        "paper_id": paper_id,
        "contract_sha256": contract_sha256,
        "protocol_version": PAPER_PREPARATION_PROTOCOL_VERSION,
        "packet_sha256": _digest(packet),
        "pass": result["pass"],
        "blockers": list(result["blockers"]),
        "gate_pass": gate_pass,
        "summary": dict(result["summary"]),
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["receipt_sha256"] = _digest(paper_preparation_receipt_identity(receipt))
    return receipt


def validate_paper_preparation_receipt(receipt: Mapping[str, Any]) -> bool:
    if str(receipt.get("receipt_type") or "") != "paper-preparation":
        return False
    return str(receipt.get("receipt_sha256") or "") == _digest(paper_preparation_receipt_identity(receipt))


def build_paper_preparation_system_state() -> dict[str, Any]:
    return {
        "schema_version": PAPER_PREPARATION_PROTOCOL_VERSION,
        "policy": dict(POLICY),
        "required_gates": list(PAPER_PREPARATION_GATE_KEYS),
        "required_rubric_dimensions": list(REQUIRED_RUBRIC_DIMENSIONS),
        "required_agent_native_layers": list(REQUIRED_AGENT_NATIVE_LAYERS),
        "required_reader_modes": list(REQUIRED_READER_MODES),
        "inspirations": [dict(row) for row in INSPIRATIONS],
        "summary": {
            "required_gates": len(PAPER_PREPARATION_GATE_KEYS),
            "rubric_dimensions": len(REQUIRED_RUBRIC_DIMENSIONS),
            "agent_native_layers": len(REQUIRED_AGENT_NATIVE_LAYERS),
            "reader_modes": len(REQUIRED_READER_MODES),
            "automatic_scientific_authority": 0,
            "automatic_experiment_authority": 0,
            "automatic_gpu_authority": 0,
            "automatic_submission_authority": 0,
        },
        "scientific_authority": False,
    }
