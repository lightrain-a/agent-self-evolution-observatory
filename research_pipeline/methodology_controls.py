from __future__ import annotations

import json
from pathlib import Path
from typing import Any


C1_PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
C1_GATE_PROFILE = "C1_EXECUTABLE_CLOSURE_V3"
C1_GATE_ID = "C1_EXECUTABLE_CLOSURE_REVIEWER_GATE_V3"
C1_REVISION_PROGRAM = Path(__file__).resolve().parents[1] / "paper_drafts" / "c1-proxy-reward-stanford-r3-20260824" / "mechanism-closure-program-20260824.json"
C1_REQUIRED_BASELINE_IDS = frozenset(
    {
        "neutral-metadata-memory",
        "generic-common-core-residual",
        "semantic-applicability",
        "query-conditioned-reuse",
        "provenance-authorization",
        "success-failure-reflection",
    }
)
C1_ALLOWED_NOVEL_COMPONENT_IDS = frozenset(
    {
        "same-trajectory-counterfactual-branch-residual",
        "evidence-gated-trigger-authority",
    }
)
C1_REQUIRED_VALIDITY_STATES = {"SUPPORTED", "CONTRADICTED", "UNVERIFIABLE"}
C1_D0B_STRUCTURAL_STATUS = "D0B_RECEIPT_STRUCTURE_FEASIBLE_SEMANTIC_VALIDITY_UNADJUDICATED_AUTHORITY_HOLD"
C1_D0B_STRUCTURAL_DECISION = "D0B_STRUCTURAL_GO_SEMANTIC_AUTHORITY_HOLD"
C1_D0B_AUDIT_ARTIFACT = Path(__file__).resolve().parents[1] / "paper_drafts" / "c1-proxy-reward-stanford-r3-20260824" / "cbrg-d0b-receipt-structural-audit-20260824.json"
C1_D0B_CLAIM_BINDING_STATUS = "D0B_RECEIPT_ENVELOPE_COMPLETE_CLAIM_BINDING_HOLD"
C1_D0B_CLAIM_BINDING_DECISION = "D0B_ENVELOPE_GO_CLAIM_BINDING_HOLD"
C1_D0B_CLAIM_BINDING_ARTIFACT = Path(__file__).resolve().parents[1] / "paper_drafts" / "c1-proxy-reward-stanford-r3-20260824" / "cbrg-d0b-claim-binding-audit-v2-20260824.json"
C1_D0B1_IDENTIFIABILITY_STATUS = "D0B1_INTERVENTION_CONTRAST_IDENTIFIABLE_CAUSAL_ATOM_PURITY_HOLD"
C1_D0B1_IDENTIFIABILITY_DECISION = "D0B1_OPERATIONAL_CONTRAST_GO_CAUSAL_ATOM_IDENTITY_HOLD"
C1_D0B1_IDENTIFIABILITY_ARTIFACT = Path(__file__).resolve().parents[1] / "paper_drafts" / "c1-proxy-reward-stanford-r3-20260824" / "cbrg-d0b1-intervention-identifiability-audit-20260824.json"
C1_D0B1C_LOCATOR_STATUS = "D0B1C_OPERATIONAL_CONTRAST_COMPILED_EXACT_LOCATOR_PARTIAL_SEMANTIC_HOLD"
C1_D0B1C_LOCATOR_DECISION = "D0B1C_COMPILER_GO_LOCATOR_PARTIAL_FAIL_CLOSED_D0B2_READY"
C1_D0B1C_LOCATOR_ARTIFACT = Path(__file__).resolve().parents[1] / "paper_drafts" / "c1-proxy-reward-stanford-r3-20260824" / "cbrg-d0b1c-operational-contrast-evidence-locator-20260824.json"
C1_D0B2_READINESS_STATUS = "D0B2_SEMANTIC_ADJUDICATOR_NOT_BOUND_READINESS_HOLD"
C1_D0B2_READINESS_DECISION = "D0B2_READINESS_HOLD_NO_ADMISSIBLE_OUTCOME_INDEPENDENT_VALIDITY_SIGNAL"
C1_D0B2_READINESS_ARTIFACT = Path(__file__).resolve().parents[1] / "paper_drafts" / "c1-proxy-reward-stanford-r3-20260824" / "cbrg-d0b2-semantic-readiness-audit-20260824.json"
C1_D0B2_CLOSURE_STATUS = "D0B2_BOUNDED_ADJUDICATOR_INVENTORY_EXHAUSTED_CURRENT_EXTENSION_STOP_MERGE"
C1_D0B2_CLOSURE_DECISION = "STOP_MERGE_CBRG_EXTENSION_NO_QUALIFIED_OUTCOME_INDEPENDENT_VALIDITY_SIGNAL"
C1_D0B2_CLOSURE_ARTIFACT = Path(__file__).resolve().parents[1] / "paper_drafts" / "c1-proxy-reward-stanford-r3-20260824" / "cbrg-d0b2-adjudicator-inventory-closure-20260825.json"
C1_EXECUTABLE_CLOSURE_REVIEWER_GATE: dict[str, Any] = {
    "gate": C1_GATE_ID,
    "profile": C1_GATE_PROFILE,
    "paper_id": C1_PAPER_ID,
    "status": "REGISTERED_FAIL_CLOSED_ZERO_AUTHORITY",
    "pass_semantics": "D0_DESIGN_ELIGIBLE_ONLY",
    "baseline_only_component_ids": sorted(C1_REQUIRED_BASELINE_IDS),
    "only_admissible_novel_component_ids": sorted(C1_ALLOWED_NOVEL_COMPONENT_IDS),
    "forbidden_shortcuts": [
        "neutral or metadata memory promoted from baseline to novelty",
        "generic common-core/residual factorization promoted from baseline to novelty",
        "semantic applicability or similarity used as evidence authority by itself",
        "reward/success/failure treatment label used to validate its own branch residual",
        "unbound or non-receipted evidence used to grant branch-specific trigger authority",
        "D0 pass used as provider, GPU, experiment, claim-expansion, or submission authority",
    ],
    "authority": {
        "scientific": False,
        "experiment": False,
        "provider": False,
        "gpu": False,
        "claim_expansion": False,
        "submission": False,
    },
}


def _all_authority_false(authority: Any) -> bool:
    return isinstance(authority, dict) and bool(authority) and not any(bool(value) for value in authority.values())


def adjudicate_c1_executable_closure_gate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Fail-closed pre-D0 reviewer gate for the frozen C1 executable-closure residual.

    The gate is deliberately paper-specific. It can grant D0 *design* eligibility only;
    it never grants scientific execution, provider, GPU, claim-expansion, or submission authority.
    """
    errors: list[str] = []
    if candidate.get("paper_id") != C1_PAPER_ID:
        errors.append("paper_id does not match the frozen C1 paper")
    if candidate.get("gate_profile") != C1_GATE_PROFILE:
        errors.append("gate_profile is not C1_EXECUTABLE_CLOSURE_V3")
    if candidate.get("gate_id") != C1_GATE_ID:
        errors.append("gate_id does not match the registered C1 reviewer gate")

    baseline_ids = set(candidate.get("baseline_only_component_ids") or [])
    novel_ids = set(candidate.get("proposed_novel_component_ids") or [])
    missing_baselines = sorted(C1_REQUIRED_BASELINE_IDS - baseline_ids)
    if missing_baselines:
        errors.append("required baseline-only components missing: " + ", ".join(missing_baselines))
    if novel_ids != C1_ALLOWED_NOVEL_COMPONENT_IDS:
        errors.append(
            "C1 novelty set must be exactly same-trajectory counterfactual branch residual + evidence-gated trigger authority"
        )
    if baseline_ids & novel_ids:
        errors.append("baseline-only components re-enter the novelty set")

    residual = candidate.get("scientific_residual") or {}
    if not str(residual.get("statement") or "").strip():
        errors.append("scientific residual is not explicitly stated")
    required_residual_flags = {
        "same_trajectory_counterfactual_pair_required": "same-trajectory counterfactual identity is not required",
        "byte_identical_trajectory_required": "byte-identical trajectory pairing is not required",
        "incremental_over_baselines_required": "incremental information/effect beyond demoted baselines is not required",
        "fresh_collision_clearance_required": "fresh closest-work clearance is not required before ProblemGate",
        "treatment_label_is_not_validity_evidence": "treatment label may incorrectly self-validate its residual",
        "semantic_applicability_alone_is_insufficient": "semantic applicability may incorrectly grant branch authority",
        "outcome_independent_evidence_required": "outcome-independent evidence is not required",
    }
    for key, message in required_residual_flags.items():
        if residual.get(key) is not True:
            errors.append(message)

    trigger = candidate.get("evidence_trigger_contract") or {}
    required_trigger_flags = {
        "claim_bound_source_or_trajectory_evidence_required": "trigger evidence is not bound to exact source/trajectory facts",
        "outcome_independent": "trigger evidence is not outcome-independent",
        "treatment_label_forbidden_as_validity_evidence": "treatment label is not explicitly forbidden as validity evidence",
        "evidence_receipt_required_before_branch_authority": "branch authority can be granted without an evidence receipt",
        "default_withhold_on_contradicted_or_unverifiable": "contradicted/unverifiable evidence does not fail closed",
    }
    for key, message in required_trigger_flags.items():
        if trigger.get(key) is not True:
            errors.append(message)
    if trigger.get("semantic_applicability_role") != "ELIGIBILITY_BASELINE_ONLY":
        errors.append("semantic applicability must remain eligibility/baseline-only")
    validity_states = {str(value) for value in (trigger.get("validity_states") or [])}
    if validity_states != C1_REQUIRED_VALIDITY_STATES:
        errors.append("evidence validity states must be exactly SUPPORTED/CONTRADICTED/UNVERIFIABLE")
    if trigger.get("trigger_authority_status_now") != "CONTRACT_ONLY_NO_BRANCH_AUTHORITY":
        errors.append("current trigger authority must remain contract-only with no branch authority")
    receipt = trigger.get("evidence_receipt_contract") or {}
    required_receipt_flags = {
        "content_addressed": "evidence receipt is not content-addressed",
        "binds_exact_trajectory_sha256": "evidence receipt does not bind the exact trajectory hash",
        "binds_branch_memory_sha256": "evidence receipt does not bind the branch memory hashes",
        "binds_residual_claim_id": "evidence receipt does not bind the residual claim identity",
        "binds_evidence_refs_and_sha256": "evidence receipt does not bind exact evidence refs and hashes",
        "records_validity_state": "evidence receipt does not record the validity state",
        "records_extractor_and_adjudicator_version": "evidence receipt does not record extractor/adjudicator versions",
        "records_authority_decision": "evidence receipt does not record the branch authority decision",
        "receipt_is_required_before_nonzero_branch_authority": "nonzero branch authority does not require a prior receipt",
        "receipt_cannot_grant_provider_or_scientific_authority": "evidence receipt may incorrectly escalate provider/scientific authority",
    }
    for key, message in required_receipt_flags.items():
        if receipt.get(key) is not True:
            errors.append(message)

    collision = candidate.get("collision_audit_contract") or {}
    if collision.get("status") != "COLLISION_AUDITED_CANDIDATE_FRESH_CLEARANCE_REQUIRED_BEFORE_PROBLEMGATE":
        errors.append("collision audit status does not preserve the fresh-clearance boundary")
    if collision.get("exact_residual_claim_status") != "CANDIDATE_ONLY_NOT_NOVELTY_CLAIM":
        errors.append("exact residual is being overclaimed as established novelty")
    if collision.get("fresh_collision_clearance_required_before_problem_gate") is not True:
        errors.append("fresh collision clearance is not required before ProblemGate")
    if not (collision.get("audit_artifact_refs") or []):
        errors.append("collision audit has no versioned artifact reference")

    d0 = candidate.get("d0_contract") or {}
    if d0.get("zero_or_low_cost") is not True:
        errors.append("D0 is not frozen as zero/low-cost design work")
    if d0.get("outcome_independent_support") is not True:
        errors.append("D0 support is not outcome-independent")
    try:
        provider_budget = int(d0.get("provider_call_budget", -1))
    except (TypeError, ValueError):
        provider_budget = -1
    if provider_budget != 0:
        errors.append("D0 scientific provider-call budget is not frozen at zero")
    if d0.get("provider_execution_authority_after_pass") is not False:
        errors.append("D0 may incorrectly auto-authorize provider execution")
    if d0.get("fresh_experiment_authority_after_pass") is not False:
        errors.append("D0 may incorrectly auto-authorize a fresh experiment")

    authority = candidate.get("authority_after_gate") or {}
    if not _all_authority_false(authority):
        errors.append("C1 residual gate must keep all downstream authority false")

    return {
        "gate": C1_GATE_ID,
        "profile": C1_GATE_PROFILE,
        "paper_id": C1_PAPER_ID,
        "eligible_for_d0_design": not errors,
        "errors": errors,
        "authority": dict(C1_EXECUTABLE_CLOSURE_REVIEWER_GATE["authority"]),
    }


def adjudicate_c1_d0b_structural_observation(observation: dict[str, Any]) -> dict[str, Any]:
    """Validate D0-B receipt *structure* without upgrading it to semantic or execution authority."""
    errors: list[str] = []
    if observation.get("status") != C1_D0B_STRUCTURAL_STATUS:
        errors.append("D0-B structural status must preserve semantic-validity HOLD")
    if observation.get("decision") != C1_D0B_STRUCTURAL_DECISION:
        errors.append("D0-B structural decision must remain STRUCTURAL GO / SEMANTIC AUTHORITY HOLD")
    for key in ("provider_calls", "gpu_runs", "semantic_validity_adjudicated_claims", "supported_claims", "contradicted_claims", "unverifiable_claims", "nonzero_branch_authority_receipts"):
        if observation.get(key) != 0:
            errors.append(f"D0-B structural-only field must remain zero: {key}")
    required_counts = {
        "paired_sources_expected": 24,
        "paired_sources_structurally_bound": 24,
        "shopping_pairs_bound": 20,
        "reddit_pairs_bound": 4,
        "pre_writer_trajectory_projections_bound": 24,
        "writer_input_action_summaries_recomputed_and_matched": 24,
        "paired_branch_memories_hash_bound": 24,
        "released_evidence_packets_hash_bound": 24,
        "residual_claim_ids_bound": 423,
    }
    for key, expected in required_counts.items():
        if observation.get(key) != expected:
            errors.append(f"D0-B structural binding count drift: {key}")
    if observation.get("structural_complete") is not True:
        errors.append("D0-B receipt structure is not complete")
    if not _all_authority_false(observation.get("authority")):
        errors.append("D0-B structural observation must keep all downstream authority false")
    audit_ref = str(observation.get("audit_artifact") or "")
    audit_sha = str(observation.get("audit_sha256") or "")
    if not audit_ref or len(audit_sha) != 64:
        errors.append("D0-B structural observation lacks a content-addressed audit artifact")
    else:
        expected_rel = str(C1_D0B_AUDIT_ARTIFACT.relative_to(Path(__file__).resolve().parents[1]))
        if audit_ref != expected_rel:
            errors.append("D0-B structural audit artifact path drift")
        if not C1_D0B_AUDIT_ARTIFACT.is_file():
            errors.append("D0-B structural audit artifact is missing")
        else:
            import hashlib
            actual_sha = hashlib.sha256(C1_D0B_AUDIT_ARTIFACT.read_bytes()).hexdigest()
            if actual_sha != audit_sha:
                errors.append("D0-B structural audit artifact SHA drift")
            else:
                try:
                    audit = json.loads(C1_D0B_AUDIT_ARTIFACT.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    audit = {}
                    errors.append("D0-B structural audit artifact is unreadable")
                summary = audit.get("summary") or {}
                if audit.get("status") != C1_D0B_STRUCTURAL_STATUS:
                    errors.append("D0-B audit artifact status no longer preserves semantic HOLD")
                if audit.get("decision") != C1_D0B_STRUCTURAL_DECISION:
                    errors.append("D0-B audit artifact decision drift")
                if summary.get("semantic_validity_adjudicated_claims") != 0 or summary.get("nonzero_branch_authority_receipts") != 0:
                    errors.append("D0-B audit artifact incorrectly contains semantic or branch authority")
                audit_authority = {k: audit.get(k) for k in ("scientific_authority", "experiment_authority", "provider_call_authority", "gpu_authority", "claim_expansion_authority", "submission_authority")}
                if not _all_authority_false(audit_authority):
                    errors.append("D0-B audit artifact contains nonzero downstream authority")
    return {
        "paper_id": C1_PAPER_ID,
        "status": C1_D0B_STRUCTURAL_STATUS,
        "structurally_feasible": not errors,
        "semantic_authority": False,
        "errors": errors,
        "authority": dict(C1_EXECUTABLE_CLOSURE_REVIEWER_GATE["authority"]),
    }


def adjudicate_c1_d0b_claim_binding_observation(observation: dict[str, Any]) -> dict[str, Any]:
    """Validate the corrected D0-B envelope/claim-binding boundary and preserve the HOLD."""
    errors: list[str] = []
    if observation.get("status") != C1_D0B_CLAIM_BINDING_STATUS:
        errors.append("D0-B claim-binding status must preserve the claim-binding HOLD")
    if observation.get("decision") != C1_D0B_CLAIM_BINDING_DECISION:
        errors.append("D0-B claim-binding decision must remain ENVELOPE GO / CLAIM-BINDING HOLD")
    for key in (
        "provider_calls",
        "gpu_runs",
        "certified_branch_residual_atoms",
        "claim_specific_evidence_refs_bound",
        "claim_level_evidence_receipts",
        "per_claim_validity_adjudicated_atoms",
        "nonzero_branch_authority_receipts",
    ):
        if observation.get(key) != 0:
            errors.append(f"D0-B claim-binding HOLD field must remain zero: {key}")
    required_counts = {
        "receipt_envelopes_expected": 24,
        "receipt_envelopes_packet_bound": 24,
        "candidate_memory_atoms": 423,
        "candidate_memory_atoms_reconstructed": 423,
    }
    for key, expected in required_counts.items():
        if observation.get(key) != expected:
            errors.append(f"D0-B claim-binding audit count drift: {key}")
    if observation.get("packet_level_evidence_binding") is not True:
        errors.append("D0-B receipt envelope must retain packet-level evidence binding")
    if observation.get("claim_level_evidence_binding") is not False:
        errors.append("claim-level evidence binding is incorrectly being claimed")
    if observation.get("candidate_memory_atom_is_not_yet_a_certified_residual_claim") is not True:
        errors.append("candidate memory atoms are incorrectly being treated as certified residual claims")
    if observation.get("residual_identity_certified") is not False:
        errors.append("branch-residual identity is incorrectly certified")
    if observation.get("semantic_validity_adjudicated") is not False:
        errors.append("semantic validity is incorrectly adjudicated before claim binding")
    if observation.get("evidence_authority_available") is not False:
        errors.append("evidence authority is incorrectly available before claim binding and validity")
    if observation.get("treatment_label_used_as_evidence") is not False:
        errors.append("treatment label leaked into the claim-binding audit")
    if observation.get("terminal_reward_or_rubric_used_as_evidence") is not False:
        errors.append("terminal outcome leaked into the claim-binding audit")
    if not _all_authority_false(observation.get("authority")):
        errors.append("D0-B claim-binding observation must keep all downstream authority false")

    audit_ref = str(observation.get("audit_artifact") or "")
    audit_sha = str(observation.get("audit_sha256") or "")
    if not audit_ref or len(audit_sha) != 64:
        errors.append("D0-B claim-binding observation lacks a content-addressed audit artifact")
    else:
        expected_rel = str(C1_D0B_CLAIM_BINDING_ARTIFACT.relative_to(Path(__file__).resolve().parents[1]))
        if audit_ref != expected_rel:
            errors.append("D0-B claim-binding audit artifact path drift")
        if not C1_D0B_CLAIM_BINDING_ARTIFACT.is_file():
            errors.append("D0-B claim-binding audit artifact is missing")
        else:
            import hashlib
            actual_sha = hashlib.sha256(C1_D0B_CLAIM_BINDING_ARTIFACT.read_bytes()).hexdigest()
            if actual_sha != audit_sha:
                errors.append("D0-B claim-binding audit artifact SHA drift")
            else:
                try:
                    audit = json.loads(C1_D0B_CLAIM_BINDING_ARTIFACT.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    audit = {}
                    errors.append("D0-B claim-binding audit artifact is unreadable")
                summary = audit.get("summary") or {}
                semantics = audit.get("binding_semantics") or {}
                if audit.get("status") != C1_D0B_CLAIM_BINDING_STATUS:
                    errors.append("D0-B claim-binding audit status drift")
                if audit.get("decision") != C1_D0B_CLAIM_BINDING_DECISION:
                    errors.append("D0-B claim-binding audit decision drift")
                for key, expected in required_counts.items():
                    if summary.get(key) != expected:
                        errors.append(f"D0-B claim-binding artifact count drift: {key}")
                for key in (
                    "certified_branch_residual_atoms",
                    "claim_specific_evidence_refs_bound",
                    "claim_level_evidence_receipts",
                    "per_claim_validity_adjudicated_atoms",
                    "nonzero_branch_authority_receipts",
                ):
                    if summary.get(key) != 0:
                        errors.append(f"D0-B claim-binding artifact incorrectly advances {key}")
                if semantics.get("packet_level_evidence_binding") is not True:
                    errors.append("D0-B artifact lost packet-level evidence binding")
                if semantics.get("claim_level_evidence_binding") is not False:
                    errors.append("D0-B artifact incorrectly claims claim-level evidence binding")
                if semantics.get("residual_identity_certified") is not False:
                    errors.append("D0-B artifact incorrectly certifies residual identity")
                if semantics.get("semantic_validity_adjudicated") is not False:
                    errors.append("D0-B artifact incorrectly adjudicates semantic validity")
                audit_authority = {k: audit.get(k) for k in ("scientific_authority", "experiment_authority", "provider_call_authority", "gpu_authority", "claim_expansion_authority", "submission_authority")}
                if not _all_authority_false(audit_authority):
                    errors.append("D0-B claim-binding artifact contains nonzero downstream authority")

    return {
        "paper_id": C1_PAPER_ID,
        "status": C1_D0B_CLAIM_BINDING_STATUS,
        "envelope_feasible": not errors,
        "claim_binding_ready": False,
        "semantic_authority": False,
        "errors": errors,
        "authority": dict(C1_EXECUTABLE_CLOSURE_REVIEWER_GATE["authority"]),
    }


def adjudicate_c1_d0b1_intervention_identifiability(observation: dict[str, Any]) -> dict[str, Any]:
    """Preserve the distinction between an operational branch contrast and atom-level causal purity."""
    errors: list[str] = []
    if observation.get("status") != C1_D0B1_IDENTIFIABILITY_STATUS:
        errors.append("D0-B1 identifiability status drift")
    if observation.get("decision") != C1_D0B1_IDENTIFIABILITY_DECISION:
        errors.append("D0-B1 decision must remain operational-contrast GO / causal-atom HOLD")
    expected_counts = {
        "pairs": 24,
        "same_pre_writer_trajectory_projection_pairs": 24,
        "same_resolved_writer_model_within_pair": 24,
        "temperature_zero_pairs": 24,
        "branch_memory_content_changed_pairs": 24,
        "explicit_decoding_seed_bound_pairs": 0,
        "same_condition_same_trajectory_replication_bound_pairs": 0,
        "certified_branch_residual_atoms": 0,
        "claim_specific_evidence_refs_bound": 0,
        "provider_calls_added_by_this_audit": 0,
        "gpu_runs_added_by_this_audit": 0,
    }
    for key, expected in expected_counts.items():
        if observation.get(key) != expected:
            errors.append(f"D0-B1 identifiability count drift: {key}")
    if observation.get("operational_branch_contrast_identifiable") is not True:
        errors.append("D0-B1 must preserve operational branch-contrast identifiability")
    if observation.get("atom_level_causal_residual_purity_certified") is not False:
        errors.append("D0-B1 cannot certify atom-level causal residual purity without a noise-floor control")
    if observation.get("f0c_tasks_complete") != 8 or observation.get("f0c_gate_pass") is not True:
        errors.append("D0-B1 must bind the existing eight-task F0C prompt-mode control")
    if not _all_authority_false(observation.get("authority")):
        errors.append("D0-B1 identifiability observation must keep all downstream authority false")

    audit_ref = str(observation.get("audit_artifact") or "")
    audit_sha = str(observation.get("audit_sha256") or "")
    if not audit_ref or len(audit_sha) != 64:
        errors.append("D0-B1 identifiability observation lacks a content-addressed audit artifact")
    else:
        expected_rel = str(C1_D0B1_IDENTIFIABILITY_ARTIFACT.relative_to(Path(__file__).resolve().parents[1]))
        if audit_ref != expected_rel:
            errors.append("D0-B1 identifiability audit artifact path drift")
        if not C1_D0B1_IDENTIFIABILITY_ARTIFACT.is_file():
            errors.append("D0-B1 identifiability audit artifact is missing")
        else:
            import hashlib
            actual_sha = hashlib.sha256(C1_D0B1_IDENTIFIABILITY_ARTIFACT.read_bytes()).hexdigest()
            if actual_sha != audit_sha:
                errors.append("D0-B1 identifiability audit artifact SHA drift")
            else:
                try:
                    audit = json.loads(C1_D0B1_IDENTIFIABILITY_ARTIFACT.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    audit = {}
                    errors.append("D0-B1 identifiability audit artifact is unreadable")
                lineage = audit.get("current_24_pair_intervention_lineage") or {}
                f0c = audit.get("existing_prompt_mode_control") or {}
                gate = audit.get("b1_gate") or {}
                if audit.get("status") != C1_D0B1_IDENTIFIABILITY_STATUS or audit.get("decision") != C1_D0B1_IDENTIFIABILITY_DECISION:
                    errors.append("D0-B1 identifiability artifact status/decision drift")
                for key in (
                    "pairs",
                    "same_pre_writer_trajectory_projection_pairs",
                    "same_resolved_writer_model_within_pair",
                    "temperature_zero_pairs",
                    "branch_memory_content_changed_pairs",
                    "explicit_decoding_seed_bound_pairs",
                    "same_condition_same_trajectory_replication_bound_pairs",
                ):
                    if lineage.get(key) != expected_counts[key]:
                        errors.append(f"D0-B1 artifact lineage drift: {key}")
                if lineage.get("operational_branch_contrast_identifiable") is not True:
                    errors.append("D0-B1 artifact lost operational branch-contrast identity")
                if lineage.get("atom_level_causal_residual_purity_certified") is not False:
                    errors.append("D0-B1 artifact incorrectly certifies atom-level causal purity")
                if f0c.get("tasks_complete") != 8 or f0c.get("same_mode_paraphrase_control_qualified") is not True:
                    errors.append("D0-B1 artifact lost the existing F0C control")
                if gate.get("certified_branch_residual_atoms") != 0 or gate.get("claim_specific_evidence_refs_bound") != 0:
                    errors.append("D0-B1 artifact incorrectly advances residual/evidence authority")
                audit_authority = {k: audit.get(k) for k in ("scientific_authority", "experiment_authority", "provider_call_authority", "gpu_authority", "claim_expansion_authority", "submission_authority")}
                if not _all_authority_false(audit_authority):
                    errors.append("D0-B1 identifiability artifact contains nonzero downstream authority")

    return {
        "paper_id": C1_PAPER_ID,
        "status": C1_D0B1_IDENTIFIABILITY_STATUS,
        "operational_contrast_identifiable": not errors,
        "causal_atom_purity_certified": False,
        "semantic_authority": False,
        "errors": errors,
        "authority": dict(C1_EXECUTABLE_CLOSURE_REVIEWER_GATE["authority"]),
    }


def adjudicate_c1_d0b1c_locator_observation(observation: dict[str, Any]) -> dict[str, Any]:
    """Validate operational contrast compilation while keeping locator/validity fail-closed."""
    errors: list[str] = []
    if observation.get("status") != C1_D0B1C_LOCATOR_STATUS:
        errors.append("D0-B1c locator status drift")
    if observation.get("decision") != C1_D0B1C_LOCATOR_DECISION:
        errors.append("D0-B1c locator decision drift")
    expected = {
        "provider_calls": 0,
        "gpu_runs": 0,
        "paired_sources": 24,
        "directional_branch_contrast_units": 423,
        "same_field_opposite_counterpart_units": 423,
        "units_with_exact_nonzero_lexical_evidence_anchor": 397,
        "units_without_nonzero_lexical_evidence_anchor": 26,
        "semantic_validity_adjudicated_units": 0,
        "supported_units": 0,
        "contradicted_units": 0,
        "unverifiable_units": 0,
        "nonzero_branch_authority_units": 0,
    }
    for key, value in expected.items():
        if observation.get(key) != value:
            errors.append(f"D0-B1c locator count/status drift: {key}")
    coverage = observation.get("locator_coverage")
    if not isinstance(coverage, (int, float)) or abs(float(coverage) - (397 / 423)) > 1e-12:
        errors.append("D0-B1c locator coverage drift")
    if observation.get("exact_locator_is_not_semantic_support") is not True:
        errors.append("exact evidence location is incorrectly being promoted to semantic support")
    if observation.get("unlocated_units_remain_fail_closed") is not True:
        errors.append("unlocated units must remain fail-closed")
    for key in ("treatment_label_used_as_evidence", "terminal_reward_or_rubric_used_as_evidence", "downstream_outcome_used_as_evidence"):
        if observation.get(key) is not False:
            errors.append(f"forbidden outcome/treatment evidence leaked into D0-B1c: {key}")
    if not _all_authority_false(observation.get("authority")):
        errors.append("D0-B1c observation must keep all downstream authority false")

    ref = str(observation.get("audit_artifact") or "")
    digest = str(observation.get("audit_sha256") or "")
    expected_ref = str(C1_D0B1C_LOCATOR_ARTIFACT.relative_to(Path(__file__).resolve().parents[1]))
    if ref != expected_ref or len(digest) != 64 or not C1_D0B1C_LOCATOR_ARTIFACT.is_file():
        errors.append("D0-B1c locator artifact binding is incomplete")
    else:
        import hashlib
        actual = hashlib.sha256(C1_D0B1C_LOCATOR_ARTIFACT.read_bytes()).hexdigest()
        if actual != digest:
            errors.append("D0-B1c locator artifact SHA drift")
        else:
            try:
                artifact = json.loads(C1_D0B1C_LOCATOR_ARTIFACT.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                artifact = {}
                errors.append("D0-B1c locator artifact is unreadable")
            summary = artifact.get("summary") or {}
            contract = artifact.get("evidence_locator_contract") or {}
            if artifact.get("status") != C1_D0B1C_LOCATOR_STATUS or artifact.get("decision") != C1_D0B1C_LOCATOR_DECISION:
                errors.append("D0-B1c artifact status/decision drift")
            for key in ("paired_sources", "directional_branch_contrast_units", "same_field_opposite_counterpart_units", "units_with_exact_nonzero_lexical_evidence_anchor", "units_without_nonzero_lexical_evidence_anchor", "semantic_validity_adjudicated_units", "supported_units", "contradicted_units", "unverifiable_units", "nonzero_branch_authority_units"):
                if summary.get(key) != expected[key]:
                    errors.append(f"D0-B1c artifact summary drift: {key}")
            if contract.get("lexical_similarity_is_locator_only_not_validity") is not True:
                errors.append("D0-B1c artifact lets locator similarity act as validity")
            if contract.get("no_anchor_forces_fail_closed_unlocated_state") is not True:
                errors.append("D0-B1c artifact does not fail closed on unlocated units")
            if any(bool(artifact.get(key)) for key in ("scientific_authority", "experiment_authority", "provider_call_authority", "gpu_authority", "claim_expansion_authority", "submission_authority")):
                errors.append("D0-B1c artifact contains nonzero downstream authority")

    return {
        "paper_id": C1_PAPER_ID,
        "status": C1_D0B1C_LOCATOR_STATUS,
        "compiler_ready": not errors,
        "locator_partial_fail_closed": not errors,
        "semantic_authority": False,
        "errors": errors,
        "authority": dict(C1_EXECUTABLE_CLOSURE_REVIEWER_GATE["authority"]),
    }


def adjudicate_c1_d0b2_semantic_readiness_observation(observation: dict[str, Any]) -> dict[str, Any]:
    """Fail closed when C1 has no independently qualified semantic-validity adjudicator."""
    errors: list[str] = []
    if observation.get("status") != C1_D0B2_READINESS_STATUS:
        errors.append("D0-B2 semantic-readiness status drift")
    if observation.get("decision") != C1_D0B2_READINESS_DECISION:
        errors.append("D0-B2 semantic-readiness decision drift")
    expected_zero = (
        "nli_classifier_configs_with_entailment_and_contradiction_labels",
        "c1_semantic_qualification_receipts",
        "qualified_semantic_adjudicators_bound",
        "semantic_validity_adjudicated_units",
        "supported_units",
        "contradicted_units",
        "unverifiable_units_adjudicated",
        "nonzero_branch_authority_units",
        "provider_calls",
        "gpu_runs",
    )
    for key in expected_zero:
        if observation.get(key) != 0:
            errors.append(f"D0-B2 readiness HOLD field must remain zero: {key}")
    expected_counts = {
        "operational_units_ready": 423,
        "exact_candidate_anchors_ready": 397,
        "future_forced_unverifiable_without_new_locator": 26,
    }
    for key, expected in expected_counts.items():
        if observation.get(key) != expected:
            errors.append(f"D0-B2 readiness count drift: {key}")
    if observation.get("minilm_is_similarity_baseline_only") is not True:
        errors.append("MiniLM must remain a similarity baseline rather than semantic-validity authority")
    if observation.get("lexical_locator_is_not_semantic_validity") is not True:
        errors.append("lexical evidence location must not be promoted to semantic validity")
    if observation.get("generic_nli_existence_without_c1_qualification_is_insufficient") is not True:
        errors.append("generic NLI existence cannot bypass C1-specific qualification")
    for key in (
        "treatment_label_used_as_validity_evidence",
        "terminal_reward_or_rubric_used_as_validity_evidence",
        "downstream_outcome_used_as_validity_evidence",
    ):
        if observation.get(key) is not False:
            errors.append(f"forbidden validity evidence leaked into D0-B2 readiness: {key}")
    if not _all_authority_false(observation.get("authority")):
        errors.append("D0-B2 readiness HOLD must keep all downstream authority false")

    ref = str(observation.get("audit_artifact") or "")
    digest = str(observation.get("audit_sha256") or "")
    expected_ref = str(C1_D0B2_READINESS_ARTIFACT.relative_to(Path(__file__).resolve().parents[1]))
    if ref != expected_ref or len(digest) != 64 or not C1_D0B2_READINESS_ARTIFACT.is_file():
        errors.append("D0-B2 semantic-readiness artifact binding is incomplete")
    else:
        import hashlib
        actual = hashlib.sha256(C1_D0B2_READINESS_ARTIFACT.read_bytes()).hexdigest()
        if actual != digest:
            errors.append("D0-B2 semantic-readiness artifact SHA drift")
        else:
            try:
                artifact = json.loads(C1_D0B2_READINESS_ARTIFACT.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                artifact = {}
                errors.append("D0-B2 semantic-readiness artifact is unreadable")
            local = artifact.get("local_asset_audit") or {}
            ready = artifact.get("readiness_summary") or {}
            baseline = artifact.get("baseline_asset_boundary") or {}
            contract = artifact.get("adjudicator_contract") or {}
            if artifact.get("status") != C1_D0B2_READINESS_STATUS or artifact.get("decision") != C1_D0B2_READINESS_DECISION:
                errors.append("D0-B2 semantic-readiness artifact status/decision drift")
            if local.get("nli_classifier_configs_with_entailment_and_contradiction_labels") != 0:
                errors.append("D0-B2 artifact no longer records a zero local NLI-classifier snapshot")
            if local.get("admissible_qualified_adjudicators") != 0:
                errors.append("D0-B2 artifact unexpectedly contains an admissible qualified adjudicator")
            if local.get("c1_semantic_qualification_receipts") not in ([], None):
                errors.append("D0-B2 artifact unexpectedly contains a C1 semantic qualification receipt")
            for key, expected in expected_counts.items():
                artifact_key = {
                    "operational_units_ready": "operational_units_ready",
                    "exact_candidate_anchors_ready": "exact_candidate_anchors_ready",
                    "future_forced_unverifiable_without_new_locator": "future_forced_unverifiable_without_new_locator",
                }[key]
                if ready.get(artifact_key) != expected:
                    errors.append(f"D0-B2 artifact readiness count drift: {key}")
            for key in (
                "qualified_semantic_adjudicators_bound",
                "semantic_validity_adjudicated_units",
                "supported_units",
                "contradicted_units",
                "unverifiable_units_adjudicated",
                "nonzero_branch_authority_units",
                "provider_calls",
                "gpu_runs",
            ):
                if ready.get(key) != 0:
                    errors.append(f"D0-B2 artifact incorrectly advances {key}")
            if baseline.get("classification") != "EMBEDDING_SIMILARITY_BASELINE_ONLY_NOT_A_VALIDITY_ADJUDICATOR":
                errors.append("D0-B2 artifact incorrectly upgrades MiniLM beyond baseline status")
            required_outputs = set(contract.get("required_output_states") or [])
            if required_outputs != C1_REQUIRED_VALIDITY_STATES:
                errors.append("D0-B2 adjudicator contract must retain SUPPORTED/CONTRADICTED/UNVERIFIABLE outputs")
            if any(bool(artifact.get(key)) for key in ("scientific_authority", "experiment_authority", "provider_call_authority", "gpu_authority", "claim_expansion_authority", "submission_authority")):
                errors.append("D0-B2 semantic-readiness artifact contains nonzero downstream authority")

    return {
        "paper_id": C1_PAPER_ID,
        "status": C1_D0B2_READINESS_STATUS,
        "readiness_hold_valid": not errors,
        "semantic_adjudicator_ready": False,
        "semantic_authority": False,
        "errors": errors,
        "authority": dict(C1_EXECUTABLE_CLOSURE_REVIEWER_GATE["authority"]),
    }


def adjudicate_c1_d0b2_inventory_closure_observation(observation: dict[str, Any]) -> dict[str, Any]:
    """Terminate only the current CBRG extension after bounded zero-call adjudicator exhaustion."""
    errors: list[str] = []
    if observation.get("status") != C1_D0B2_CLOSURE_STATUS:
        errors.append("D0-B2 closure status drift")
    if observation.get("decision") != C1_D0B2_CLOSURE_DECISION:
        errors.append("D0-B2 closure decision drift")
    if observation.get("scope") != "CURRENT_FROZEN_ZERO_CALL_CBRG_EXTENSION_ONLY":
        errors.append("D0-B2 closure scope must remain limited to the current frozen CBRG extension")

    expected_zero = {
        "local_qualified_adjudicators": 0,
        "repository_admissible_adjudicators": 0,
        "external_semantic_qualification_receipts": 0,
        "provider_calls": 0,
        "gpu_runs": 0,
    }
    for key, expected in expected_zero.items():
        if observation.get(key) != expected:
            errors.append(f"D0-B2 closure zero field drift: {key}")

    if observation.get("cbrg_extension_terminal_state") != "STOP_MERGE_CURRENT_EXTENSION":
        errors.append("current CBRG extension must route to STOP/MERGE")
    if observation.get("c1_measurement_paper_state") != "RETAIN_STAGE_RESOLVED_IDENTIFICATION_MEASUREMENT":
        errors.append("C1 measurement paper must be retained when the extension stops")
    if observation.get("existing_measurement_evidence_invalidated") is not False:
        errors.append("method-extension STOP must not invalidate existing C1 measurement evidence")
    if observation.get("scientific_failure_declared") is not False:
        errors.append("bounded adjudicator exhaustion is not a C1 scientific failure")
    if observation.get("automatic_reopen") is not False:
        errors.append("stopped CBRG extension cannot automatically reopen")
    if observation.get("generic_nli_or_renamed_baseline_can_reopen") is not False:
        errors.append("generic NLI or renamed baseline cannot reopen the stopped extension")
    if observation.get("qualified_content_addressed_reopen_evidence_required") is not True:
        errors.append("reopen must require new qualified content-addressed evidence")
    if not _all_authority_false(observation.get("authority")):
        errors.append("D0-B2 terminal closure must keep all downstream authority false")

    ref = str(observation.get("audit_artifact") or "")
    digest = str(observation.get("audit_sha256") or "")
    expected_ref = str(C1_D0B2_CLOSURE_ARTIFACT.relative_to(Path(__file__).resolve().parents[1]))
    if ref != expected_ref or len(digest) != 64 or not C1_D0B2_CLOSURE_ARTIFACT.is_file():
        errors.append("D0-B2 closure artifact binding is incomplete")
    else:
        import hashlib
        actual = hashlib.sha256(C1_D0B2_CLOSURE_ARTIFACT.read_bytes()).hexdigest()
        if actual != digest:
            errors.append("D0-B2 closure artifact SHA drift")
        else:
            try:
                artifact = json.loads(C1_D0B2_CLOSURE_ARTIFACT.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                artifact = {}
                errors.append("D0-B2 closure artifact is unreadable")
            inventory = artifact.get("repository_inventory") or {}
            routing = artifact.get("terminal_routing") or {}
            reopen = artifact.get("reopen_contract") or {}
            if artifact.get("status") != C1_D0B2_CLOSURE_STATUS or artifact.get("decision") != C1_D0B2_CLOSURE_DECISION:
                errors.append("D0-B2 closure artifact status/decision drift")
            if artifact.get("scope") != "CURRENT_FROZEN_ZERO_CALL_CBRG_EXTENSION_ONLY":
                errors.append("D0-B2 closure artifact overstates its scope")
            if inventory.get("external_textual_candidate_count") != 0:
                errors.append("D0-B2 closure artifact contains an external textual adjudicator candidate")
            if inventory.get("external_semantic_qualification_receipt_count") != 0:
                errors.append("D0-B2 closure artifact contains an external qualification receipt")
            if inventory.get("admissible_qualified_repository_adjudicators") != 0:
                errors.append("D0-B2 closure artifact contains an admissible repository adjudicator")
            if routing.get("cbrg_method_extension") != "STOP_MERGE_CURRENT_EXTENSION":
                errors.append("D0-B2 closure artifact does not stop the current CBRG extension")
            if routing.get("c1_stage_resolved_identification_measurement_paper") != "RETAIN":
                errors.append("D0-B2 closure artifact does not retain the C1 measurement paper")
            if routing.get("c1_existing_measurement_evidence_invalidated") is not False or routing.get("scientific_failure_declared") is not False:
                errors.append("D0-B2 closure artifact incorrectly invalidates or scientifically fails C1")
            if reopen.get("automatic_reopen") is not False:
                errors.append("D0-B2 closure artifact permits automatic reopen")
            if reopen.get("generic_nli_model_existence_is_sufficient") is not False or reopen.get("renamed_similarity_or_common_residual_is_sufficient") is not False:
                errors.append("D0-B2 closure artifact lets generic/renamed baselines reopen the extension")
            if len(reopen.get("required_all") or []) != 4 or reopen.get("reopen_authority_granted_by_this_receipt") is not False:
                errors.append("D0-B2 closure artifact reopen contract is incomplete")
            if artifact.get("provider_calls_added") != 0 or artifact.get("gpu_runs_added") != 0:
                errors.append("D0-B2 closure artifact must remain zero-call/zero-GPU")
            if any(bool(artifact.get(key)) for key in ("scientific_authority", "experiment_authority", "provider_call_authority", "gpu_authority", "claim_expansion_authority", "submission_authority")):
                errors.append("D0-B2 closure artifact contains nonzero downstream authority")

    return {
        "paper_id": C1_PAPER_ID,
        "status": C1_D0B2_CLOSURE_STATUS,
        "terminal_closure_valid": not errors,
        "current_cbrg_extension_stopped": not errors,
        "measurement_paper_retained": not errors,
        "scientific_failure": False,
        "automatic_reopen": False,
        "errors": errors,
        "authority": dict(C1_EXECUTABLE_CLOSURE_REVIEWER_GATE["authority"]),
    }


def require_c1_executable_closure_gate(candidate: dict[str, Any]) -> dict[str, Any]:
    result = adjudicate_c1_executable_closure_gate(candidate)
    if result["eligible_for_d0_design"] is not True:
        raise ValueError(C1_GATE_ID + " blocked: " + "; ".join(result["errors"]))
    return result


def _load_c1_revision_program(path: Path = C1_REVISION_PROGRAM) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        program = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return program if isinstance(program, dict) else {}


def load_c1_executable_closure_candidate(path: Path = C1_REVISION_PROGRAM) -> dict[str, Any]:
    program = _load_c1_revision_program(path)
    candidate = program.get("method_novelty_residual_reviewer_gate") or {}
    return candidate if isinstance(candidate, dict) else {}


def load_c1_d0b_structural_observation(path: Path = C1_REVISION_PROGRAM) -> dict[str, Any]:
    program = _load_c1_revision_program(path)
    observation = program.get("zero_call_D0_B_structural_observed") or {}
    return observation if isinstance(observation, dict) else {}


def load_c1_d0b_claim_binding_observation(path: Path = C1_REVISION_PROGRAM) -> dict[str, Any]:
    program = _load_c1_revision_program(path)
    observation = program.get("zero_call_D0_B_claim_binding_observed") or {}
    return observation if isinstance(observation, dict) else {}


def load_c1_d0b1_intervention_identifiability_observation(path: Path = C1_REVISION_PROGRAM) -> dict[str, Any]:
    program = _load_c1_revision_program(path)
    observation = program.get("zero_call_D0_B1_intervention_identifiability_observed") or {}
    return observation if isinstance(observation, dict) else {}


def load_c1_d0b1c_locator_observation(path: Path = C1_REVISION_PROGRAM) -> dict[str, Any]:
    program = _load_c1_revision_program(path)
    observation = program.get("zero_call_D0_B1C_operational_contrast_locator_observed") or {}
    return observation if isinstance(observation, dict) else {}


def load_c1_d0b2_semantic_readiness_observation(path: Path = C1_REVISION_PROGRAM) -> dict[str, Any]:
    program = _load_c1_revision_program(path)
    observation = program.get("zero_call_D0_B2_semantic_readiness_observed") or {}
    return observation if isinstance(observation, dict) else {}


def load_c1_d0b2_inventory_closure_observation(path: Path = C1_REVISION_PROGRAM) -> dict[str, Any]:
    program = _load_c1_revision_program(path)
    observation = program.get("zero_call_D0_B2_adjudicator_inventory_closure_observed") or {}
    return observation if isinstance(observation, dict) else {}


POLICY: dict[str, Any] = {
    "schema_version": "1.1",
    "cross_cutting_controls_do_not_create_a_seventh_functional_layer": True,
    "controls_inherit_authority_from_their_owner_component": True,
    "unmeasured_controls_must_report_spec_status_not_claim_improvement": True,
    "post_outcome_protocol_changes_require_a_new_registered_contract": True,
    "search_or_tool_access_must_not_leak_hidden_evaluation_answers": True,
    "reproducibility_requires_reexecution_not_only_trace_presence": True,
    "baseline_demoted_components_cannot_reenter_method_novelty_without_new_collision_evidence": True,
    "c1_neutral_metadata_and_generic_core_residual_are_baseline_only": True,
    "c1_only_same_trajectory_counterfactual_residual_plus_evidence_trigger_may_enter_d0": True,
    "semantic_applicability_alone_cannot_grant_evidence_authority": True,
    "treatment_label_cannot_serve_as_its_own_validity_evidence": True,
    "c1_d0_design_gate_cannot_authorize_fresh_execution": True,
    "packet_level_evidence_hash_is_not_claim_level_evidence_binding": True,
    "candidate_memory_atom_cannot_be_called_residual_claim_without_branch_residual_identity": True,
    "claim_specific_evidence_refs_required_before_semantic_validity": True,
    "semantic_validity_required_before_nonzero_branch_authority": True,
    "operational_branch_contrast_is_not_atom_level_causal_purity": True,
    "causal_residual_language_requires_seed_or_same_condition_noise_floor_control": True,
    "evidence_locator_similarity_cannot_grant_semantic_support": True,
    "unlocated_claims_cannot_receive_imputed_evidence_authority": True,
    "semantic_validity_requires_a_qualified_content_addressed_adjudicator": True,
    "generic_nli_model_existence_without_task_specific_qualification_is_not_validity_authority": True,
    "absence_of_qualified_semantic_adjudicator_is_readiness_hold_not_scientific_failure": True,
    "c1_current_cbrg_extension_stop_merge_does_not_invalidate_measurement_paper": True,
    "c1_stopped_extension_cannot_reopen_on_renamed_baseline_or_generic_nli": True,
    "c1_extension_reopen_requires_new_qualified_content_addressed_evidence": True,
    "c1_terminal_closure_overrides_historical_d0_design_eligibility": True,
}


def build_methodology_controls_state() -> dict[str, Any]:
    controls = [
        {
            "key": "exploration-frontier",
            "owner_component": "wide-search-ideation",
            "primary_layer": "paper-design",
            "status": "spec-ready-not-yet-scored",
            "purpose": {
                "en": "Detect portfolio collapse toward a small neighborhood of seed literature even when individual ideas appear novel.",
                "zh": "检测 Idea 组合是否虽然单项看似新颖，却整体塌缩在 seed 文献附近的同一小片区域。",
            },
            "measures": [
                "quality-thresholded diversity yield",
                "distance from seed literature",
                "pairwise semantic dispersion",
                "novelty-axis coverage",
                "lineage/branch entropy",
            ],
            "rules": {
                "novelty_prompt_alone_is_not_evidence_of_search_breadth": True,
                "quality_and_diversity_are_joint_objectives": True,
                "portfolio_level_collapse_is_distinct_from_pairwise_collision": True,
                "low_breadth_triggers_search_reallocation_not_paper_rejection": True,
            },
            "design_sources": [
                "AI Research Agents Narrow Scientific Exploration",
                "IDEAgent",
                "Heuresis",
                "SwarmResearch",
            ],
        },
        {
            "key": "experimental-design-integrity",
            "owner_component": "protocol-and-replay",
            "primary_layer": "experiment-design",
            "status": "contract-ready-not-yet-retrospectively-scored",
            "purpose": {
                "en": "Freeze researcher degrees of freedom before outcomes are visible and prevent web/tool access from contaminating hidden evaluation.",
                "zh": "在看到结果前冻结实验者自由度，并防止联网检索或工具访问污染 hidden evaluation。",
            },
            "preregistration_fields": [
                "model/checkpoint and inference settings",
                "prompt/scaffold and tool policy",
                "task/sample split",
                "metric and outcome semantics",
                "analysis plan and statistical test",
                "randomness/replication and stochastic-agent variance plan",
                "stopping/exclusion rules",
                "allowed adaptations and fallback path",
                "for persistent updates: post-update decision-context support and intended-effect realization check",
            ],
            "contamination_classes": [
                "benchmark-metadata leakage",
                "question-context leakage",
                "explicit-answer leakage",
            ],
            "rules": {
                "outcome_contingent_redesign_requires_new_contract": True,
                "search_trajectory_is_part_of_protocol_provenance": True,
                "hidden_evaluation_access_requires_explicit_allowlist": True,
                "contaminated_runs_cannot_support_method_or_principle_claims": True,
                "persistent_update_support_must_be_checked_under_post_update_policy": True,
                "observation_recurrence_is_not_equivalent_to_full_decision_context_recurrence": True,
                "local_supervision_is_not_behaviorally_realized_until_the_updated_policy_revisits_the_full_context_and_executes_the_intended_intervention": True,
                "failed_effect_realization_is_protocol_or_operationalization_evidence_before_it_is_method_failure": True,
                "historical_runs_predating_this_rule_are_not_retroactively_reclassified": True,
            },
            "design_sources": [
                "Preregistration for Experiments with AI Agents",
                "Search-Time Contamination in Deep Research Agents",
                "AstaBench",
                "An Experimental Design Approach to Evaluating Agentic AI's Autonomous Model Discovery",
                "DAgger / induced observation-distribution consistency",
                "HERO / current-decision-context aligned agentic self-distillation",
                "ReOPD / reliability-aware on-policy prefix distribution",
                "SkillEvolver / deployed-skill silent-bypass audit",
            ],
        },
        {
            "key": "reproducibility-readiness",
            "owner_component": "literature-evidence-integrity",
            "primary_layer": "evidence-knowledge",
            "status": "spec-ready-not-yet-independent-reexecuted",
            "purpose": {
                "en": "Require a third party to reconstruct and rerun the result-generating workflow instead of treating logs or citations as sufficient reproducibility evidence.",
                "zh": "要求第三方能够重建并重跑结果生成流程，而不是把“有日志/有引用”误当成已经可复现。",
            },
            "required_graph": [
                "source/data dependencies",
                "preprocessing/transformation steps",
                "method/configuration",
                "execution commands and environment",
                "metrics/analysis",
                "figure/table/claim outputs",
            ],
            "required_artifacts": [
                "dependency-aware workflow graph",
                "versioned environment manifest",
                "re-execution entry point",
                "seed/data split record",
                "failure/recovery notes",
                "independent reproduction report",
            ],
            "rules": {
                "claim_traceability_is_not_equivalent_to_reproducibility": True,
                "reproduction_must_execute_without_copying_checked_in_results": True,
                "environment_or_dependency_failure_is_reported_separately_from_scientific_failure": True,
                "paper_ready_status_requires_independent_reexecution_for_load_bearing_results": True,
            },
            "design_sources": [
                "ARA: Agentic Reproducibility Assessment",
                "Artisan",
                "ArtifactCopilot",
                "Scaling Reproducibility",
            ],
        },
    ]
    c1_candidate = load_c1_executable_closure_candidate()
    c1_adjudication = adjudicate_c1_executable_closure_gate(c1_candidate)
    c1_d0b_observation = load_c1_d0b_structural_observation()
    c1_d0b_adjudication = adjudicate_c1_d0b_structural_observation(c1_d0b_observation)
    c1_d0b_claim_binding_observation = load_c1_d0b_claim_binding_observation()
    c1_d0b_claim_binding_adjudication = adjudicate_c1_d0b_claim_binding_observation(c1_d0b_claim_binding_observation)
    c1_d0b1_identifiability_observation = load_c1_d0b1_intervention_identifiability_observation()
    c1_d0b1_identifiability_adjudication = adjudicate_c1_d0b1_intervention_identifiability(c1_d0b1_identifiability_observation)
    c1_d0b1c_locator_observation = load_c1_d0b1c_locator_observation()
    c1_d0b1c_locator_adjudication = adjudicate_c1_d0b1c_locator_observation(c1_d0b1c_locator_observation)
    c1_d0b2_readiness_observation = load_c1_d0b2_semantic_readiness_observation()
    c1_d0b2_readiness_adjudication = adjudicate_c1_d0b2_semantic_readiness_observation(c1_d0b2_readiness_observation)
    c1_d0b2_closure_observation = load_c1_d0b2_inventory_closure_observation()
    c1_d0b2_closure_adjudication = adjudicate_c1_d0b2_inventory_closure_observation(c1_d0b2_closure_observation)
    c1_reviewer_gate = {
        **C1_EXECUTABLE_CLOSURE_REVIEWER_GATE,
        "candidate_loaded": bool(c1_candidate),
        "candidate_adjudication": c1_adjudication,
    }
    return {
        "schema_version": "1.1",
        "policy": POLICY,
        "controls": controls,
        "reviewer_gates": {
            "c1_executable_closure_v3": c1_reviewer_gate,
            "c1_d0b_receipt_structure": {
                "status": "HISTORICAL_ENVELOPE_AUDIT_ONLY",
                "observation_loaded": bool(c1_d0b_observation),
                "observation_adjudication": c1_d0b_adjudication,
            },
            "c1_d0b_claim_binding_v2": {
                "status": "REGISTERED_CURRENT_FAIL_CLOSED_CLAIM_BINDING_HOLD",
                "observation_loaded": bool(c1_d0b_claim_binding_observation),
                "observation_adjudication": c1_d0b_claim_binding_adjudication,
            },
            "c1_d0b1_intervention_identifiability": {
                "status": "REGISTERED_OPERATIONAL_CONTRAST_GO_CAUSAL_ATOM_HOLD",
                "observation_loaded": bool(c1_d0b1_identifiability_observation),
                "observation_adjudication": c1_d0b1_identifiability_adjudication,
            },
            "c1_d0b1c_operational_contrast_locator": {
                "status": "REGISTERED_COMPILER_GO_LOCATOR_PARTIAL_FAIL_CLOSED",
                "observation_loaded": bool(c1_d0b1c_locator_observation),
                "observation_adjudication": c1_d0b1c_locator_adjudication,
            },
            "c1_d0b2_semantic_readiness": {
                "status": "REGISTERED_READINESS_HOLD_NO_QUALIFIED_VALIDITY_SIGNAL",
                "observation_loaded": bool(c1_d0b2_readiness_observation),
                "observation_adjudication": c1_d0b2_readiness_adjudication,
            },
            "c1_d0b2_adjudicator_inventory_closure": {
                "status": "REGISTERED_CURRENT_EXTENSION_STOP_MERGE_MEASUREMENT_RETAINED",
                "observation_loaded": bool(c1_d0b2_closure_observation),
                "observation_adjudication": c1_d0b2_closure_adjudication,
            },
        },
        "summary": {
            "controls": len(controls),
            "primary_components_added": 0,
            "functional_layers_added": 0,
            "measured_controls": sum(str(row["status"]).startswith("measured") for row in controls),
            "spec_or_contract_ready": sum("ready" in str(row["status"]) for row in controls),
            "registered_reviewer_gates": 7,
            "c1_reviewer_gate_loaded": bool(c1_candidate),
            "c1_reviewer_gate_historical_d0_design_eligible": c1_adjudication["eligible_for_d0_design"],
            "c1_reviewer_gate_d0_design_eligible": c1_adjudication["eligible_for_d0_design"] and not c1_d0b2_closure_adjudication["current_cbrg_extension_stopped"],
            "c1_reviewer_gate_downstream_authority": any(bool(value) for value in c1_adjudication["authority"].values()),
            "c1_d0b_structural_observation_loaded": bool(c1_d0b_observation),
            "c1_d0b_structurally_feasible": c1_d0b_adjudication["structurally_feasible"],
            "c1_d0b_semantic_authority": c1_d0b_adjudication["semantic_authority"],
            "c1_d0b_downstream_authority": any(bool(value) for value in c1_d0b_adjudication["authority"].values()),
            "c1_d0b_claim_binding_observation_loaded": bool(c1_d0b_claim_binding_observation),
            "c1_d0b_claim_binding_envelope_feasible": c1_d0b_claim_binding_adjudication["envelope_feasible"],
            "c1_d0b_claim_binding_ready": c1_d0b_claim_binding_adjudication["claim_binding_ready"],
            "c1_d0b_claim_binding_semantic_authority": c1_d0b_claim_binding_adjudication["semantic_authority"],
            "c1_d0b_claim_binding_downstream_authority": any(bool(value) for value in c1_d0b_claim_binding_adjudication["authority"].values()),
            "c1_d0b1_identifiability_observation_loaded": bool(c1_d0b1_identifiability_observation),
            "c1_d0b1_operational_contrast_identifiable": c1_d0b1_identifiability_adjudication["operational_contrast_identifiable"],
            "c1_d0b1_causal_atom_purity_certified": c1_d0b1_identifiability_adjudication["causal_atom_purity_certified"],
            "c1_d0b1_semantic_authority": c1_d0b1_identifiability_adjudication["semantic_authority"],
            "c1_d0b1_downstream_authority": any(bool(value) for value in c1_d0b1_identifiability_adjudication["authority"].values()),
            "c1_d0b1c_locator_observation_loaded": bool(c1_d0b1c_locator_observation),
            "c1_d0b1c_compiler_ready": c1_d0b1c_locator_adjudication["compiler_ready"],
            "c1_d0b1c_locator_partial_fail_closed": c1_d0b1c_locator_adjudication["locator_partial_fail_closed"],
            "c1_d0b1c_semantic_authority": c1_d0b1c_locator_adjudication["semantic_authority"],
            "c1_d0b1c_downstream_authority": any(bool(value) for value in c1_d0b1c_locator_adjudication["authority"].values()),
            "c1_d0b2_readiness_observation_loaded": bool(c1_d0b2_readiness_observation),
            "c1_d0b2_readiness_hold_valid": c1_d0b2_readiness_adjudication["readiness_hold_valid"],
            "c1_d0b2_semantic_adjudicator_ready": c1_d0b2_readiness_adjudication["semantic_adjudicator_ready"],
            "c1_d0b2_semantic_authority": c1_d0b2_readiness_adjudication["semantic_authority"],
            "c1_d0b2_downstream_authority": any(bool(value) for value in c1_d0b2_readiness_adjudication["authority"].values()),
            "c1_d0b2_closure_observation_loaded": bool(c1_d0b2_closure_observation),
            "c1_d0b2_terminal_closure_valid": c1_d0b2_closure_adjudication["terminal_closure_valid"],
            "c1_d0b2_current_extension_stopped": c1_d0b2_closure_adjudication["current_cbrg_extension_stopped"],
            "c1_d0b2_measurement_paper_retained": c1_d0b2_closure_adjudication["measurement_paper_retained"],
            "c1_d0b2_closure_scientific_failure": c1_d0b2_closure_adjudication["scientific_failure"],
            "c1_d0b2_closure_automatic_reopen": c1_d0b2_closure_adjudication["automatic_reopen"],
            "c1_d0b2_closure_downstream_authority": any(bool(value) for value in c1_d0b2_closure_adjudication["authority"].values()),
        },
        "merge_only_external_designs": [
            {
                "system": "EurekAgent",
                "reason": "permissions/artifact/budget/HITL environment engineering already maps to Runtime & Authority; no duplicate component is required",
            }
        ],
    }
