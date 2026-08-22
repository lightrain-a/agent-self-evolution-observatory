from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .paper_acceptance import (
    MANDATORY_MANUSCRIPT_CI_CHECKS,
    MockReviewMode,
    ObjectionEvidenceState,
    PaperContract,
    PaperState,
    PrebuttalResolution,
    ReviewerObjection,
    ScientificPaperStatus,
    StoryCandidate,
    evaluate_manuscript_ci,
    evaluate_submission_ready,
    paper_contract_digest,
    paper_contract_payload,
)
from .paper_acceptance_ledger import (
    advance_paper_ledger,
    initialize_paper_ledger,
    record_claim_audit,
    record_manuscript_ci,
    record_mock_review,
    record_paper_preparation,
    record_frozen_contract_paper_preparation,
    record_prebuttal,
    record_story_search,
    record_submission_readiness,
    validate_paper_ledger,
)
from .paper_preparation_protocol import (
    PAPER_PREPARATION_GATE_KEYS,
    PAPER_PREPARATION_PROTOCOL_VERSION,
    REQUIRED_AGENT_NATIVE_LAYERS,
    REQUIRED_READER_MODES,
    REQUIRED_RUBRIC_DIMENSIONS,
    build_paper_preparation_receipt,
    build_paper_preparation_system_state,
    evaluate_paper_preparation,
    validate_paper_preparation_receipt,
)


def passing_packet() -> dict:
    dimensions = {
        name: {"pass": True, "evidence_refs": [f"artifact:{name}"]}
        for name in REQUIRED_RUBRIC_DIMENSIONS
    }
    layers = {
        name: {"complete": True, "artifact_refs": [f"artifact:{name}"]}
        for name in REQUIRED_AGENT_NATIVE_LAYERS
    }
    modes = {
        name: {"completed": True, "unresolved_decision_critical": 0}
        for name in REQUIRED_READER_MODES
    }
    return {
        "protocol_version": PAPER_PREPARATION_PROTOCOL_VERSION,
        "claim_expansion_authorized": False,
        "new_experiment_authorized": False,
        "gates": {
            "hierarchical-rubric": {
                "hierarchical_decomposition": True,
                "single_overall_score_is_non_authoritative": True,
                "plan_execution_parity_pass": True,
                "fabricated_result_scan_pass": True,
                "evidence_sufficiency_review_pass": True,
                "dimensions": dimensions,
            },
            "verification-refinement": {
                "verifier_separate_from_refiner": True,
                "verification_against_frozen_contract": True,
                "issues": [
                    {"issue_id": "P1", "decision_critical": True},
                    {"issue_id": "P2", "decision_critical": False},
                ],
                "resolved_issue_ids": ["P1"],
                "revision_deltas": [{"issue_id": "P1", "artifact_ref": "artifact:revision"}],
                "non_improving_revision_reverted": True,
            },
            "citation-integrity": {
                "citations_total": 12,
                "citations_verified": 12,
                "claim_citations_total": 5,
                "claim_citations_primary_source_verified": 5,
                "duplicate_citations_absent": True,
                "orphan_bib_entries_absent": True,
                "citation_placement_review_pass": True,
                "citation_claim_entailment_review_pass": True,
                "hallucinated_citations": 0,
            },
            "visual-story": {
                "main_visuals": 3,
                "each_core_claim_has_main_visual": True,
                "figure_caption_reference_review_pass": True,
                "figure_text_callout_consistency_pass": True,
                "quantitative_visual_source_binding_pass": True,
                "negative_or_boundary_evidence_visible": True,
                "labels_legible_at_final_pdf_scale": True,
                "persistent_visual_contract_present": True,
                "registered_visuals_match_sections": True,
            },
            "reproducibility-bundle": {
                "self_contained_source_bundle": True,
                "clean_environment_compile_pass": True,
                "reproduction_entrypoint_present": True,
                "dependency_environment_manifest_present": True,
                "data_model_provenance_present": True,
                "random_seed_and_nondeterminism_documented": True,
                "evaluation_code_and_protocol_bound": True,
                "artifact_hash_manifest_present": True,
                "numeric_claim_recompute_pass": True,
                "independent_reproduction_check_pass": True,
                "secret_scan_pass": True,
            },
            "agent-native-artifact": {
                "layers": layers,
                "failed_and_rejected_branches_preserved": True,
                "claim_to_raw_output_roundtrip_pass": True,
            },
            "reader-simulation": {
                "modes": modes,
                "paper_side_findings_resolved_or_explicitly_accepted": True,
                "review_score_is_not_a_hard_gate": True,
            },
            "submission-package": {
                "venue": "ICLR 2027",
                "venue_template_and_page_rules_pass": True,
                "anonymous_source_and_pdf_pass": True,
                "metadata_matches_manuscript": True,
                "supplement_and_main_artifact_consistency_pass": True,
                "fresh_directory_source_compile_pass": True,
                "file_size_and_upload_constraints_pass": True,
                "ai_use_disclosure_decision_recorded": True,
                "authorship_and_conflict_checklist_recorded": True,
                "venue_policy_snapshot_current": True,
                "human_only_requirements_recorded": True,
                "external_human_submit_required": True,
            },
        },
    }


class PaperPreparationProtocolTest(unittest.TestCase):
    def contract(self, *, prep: bool = False) -> PaperContract:
        return PaperContract(
            paper_id="PREP-PAPER",
            title="Preparation protocol test paper",
            central_question="Does the protocol fail closed?",
            supported_claims={"C1": "A supported result."},
            evidence_refs=("artifact:evidence",),
            scientific_status=ScientificPaperStatus.READY,
            paper_preparation_protocol_version=PAPER_PREPARATION_PROTOCOL_VERSION if prep else "",
            paper_preparation_requirements=PAPER_PREPARATION_GATE_KEYS if prep else (),
        )

    def test_full_protocol_passes_all_eight_gates(self) -> None:
        result = evaluate_paper_preparation(passing_packet())
        self.assertTrue(result["pass"])
        self.assertEqual(result["summary"]["required_gates"], 8)
        self.assertEqual(result["summary"]["passed_gates"], 8)
        self.assertEqual(result["blockers"], [])

    def test_citation_and_agent_native_gaps_fail_closed(self) -> None:
        packet = passing_packet()
        packet["gates"]["citation-integrity"]["citations_verified"] = 11
        packet["gates"]["agent-native-artifact"]["layers"]["exploration-graph"]["complete"] = False
        result = evaluate_paper_preparation(packet)
        self.assertFalse(result["pass"])
        self.assertIn("citation-existence-or-metadata-unverified", result["blockers"])
        self.assertIn("agent-native-layer-incomplete:exploration-graph", result["blockers"])

    def test_reader_simulation_requires_resolution_not_score(self) -> None:
        packet = passing_packet()
        packet["gates"]["reader-simulation"]["modes"]["figure-first-skimmer"]["unresolved_decision_critical"] = 1
        result = evaluate_paper_preparation(packet)
        self.assertFalse(result["pass"])
        self.assertTrue(any(item.startswith("reader-mode-unresolved-critical:figure-first-skimmer") for item in result["blockers"]))

    def test_receipt_is_content_addressed_and_tamper_evident(self) -> None:
        contract = self.contract(prep=True)
        receipt = build_paper_preparation_receipt(
            paper_id=contract.paper_id,
            contract_sha256=paper_contract_digest(contract),
            packet=passing_packet(),
        )
        self.assertTrue(receipt["pass"])
        self.assertTrue(validate_paper_preparation_receipt(receipt))
        receipt["gate_pass"]["citation-integrity"] = False
        self.assertFalse(validate_paper_preparation_receipt(receipt))

    def test_legacy_contract_payload_and_digest_are_unchanged_by_default(self) -> None:
        contract = self.contract(prep=False)
        payload = paper_contract_payload(contract)
        self.assertNotIn("paper_preparation_protocol_version", payload)
        old_shape = {
            "paper_id": contract.paper_id,
            "title": contract.title,
            "central_question": contract.central_question,
            "supported_claims": dict(contract.supported_claims),
            "active_unrefuted_claims": {},
            "active_claim_experiment_debt": {},
            "unsupported_claims": {},
            "limitations": [],
            "reopen_conditions": [],
            "evidence_refs": list(contract.evidence_refs),
            "scientific_status": "READY",
            "scientific_authority": False,
            "experiment_authority": False,
            "gpu_authority": False,
        }
        expected = hashlib.sha256(json.dumps(old_shape, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(paper_contract_digest(contract), expected)

    def test_frozen_legacy_contract_can_append_preparation_without_reserialization(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paper_id = "LEGACY-PREP"
            legacy_contract = {
                "paper_id": paper_id,
                "title": "Legacy preparation paper",
                "central_question": "Can frozen legacy identity be preserved?",
                "supported_claims": {"C1": "Supported."},
                "unsupported_claims": {},
                "limitations": [],
                "reopen_conditions": [],
                "evidence_refs": ["artifact:evidence"],
                "scientific_status": "READY",
                "scientific_authority": False,
                "experiment_authority": False,
                "gpu_authority": False,
            }
            digest = hashlib.sha256(json.dumps(legacy_contract, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            directory = root / "paper-acceptance"
            directory.mkdir(parents=True)
            (directory / f"{paper_id}.json").write_text(json.dumps({
                "schema_version": "1.0",
                "paper_id": paper_id,
                "contract_sha256": digest,
                "contract": legacy_contract,
                "current_state": "PAPER_EVIDENCE",
                "scientific_status": "READY",
                "events": [],
                "authority": {"scientific": False, "experiment": False, "gpu": False, "submission": False},
            }))
            row = record_frozen_contract_paper_preparation(root, paper_id, passing_packet())
            receipt = row["events"][-1]["receipt"]
            self.assertEqual(receipt["contract_sha256"], digest)
            self.assertTrue(receipt["pass"])
            self.assertEqual(row["contract"], legacy_contract)
            self.assertEqual(validate_paper_ledger(row), [])

    def test_opt_in_submission_ready_requires_preparation(self) -> None:
        contract = self.contract(prep=True)
        ci = evaluate_manuscript_ci({name: True for name in MANDATORY_MANUSCRIPT_CI_CHECKS})
        blocked = evaluate_submission_ready(contract, ci, {"pass": True})
        self.assertFalse(blocked["submission_ready"])
        self.assertIn("paper-preparation-not-pass", blocked["blockers"])
        receipt = build_paper_preparation_receipt(
            paper_id=contract.paper_id,
            contract_sha256=paper_contract_digest(contract),
            packet=passing_packet(),
        )
        ready = evaluate_submission_ready(contract, ci, {"pass": True}, receipt)
        self.assertTrue(ready["submission_ready"])
        self.assertTrue(ready["paper_preparation_pass"])

    def test_opt_in_ledger_blocks_until_preparation_receipt_exists(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract = self.contract(prep=True)
            initialize_paper_ledger(root, contract)
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.PAPER_DESIGN)["receipt"]["allowed"])
            record_story_search(root, contract, [StoryCandidate("S1", "Story", "Framing", ("C1",), ("C1",))])
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.MANUSCRIPT)["receipt"]["allowed"])
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.MOCK_PC)["receipt"]["allowed"])
            objection = ReviewerObjection("R1", "clarity", "Clarify.", True, ObjectionEvidenceState.EXISTING_EVIDENCE, ("C1",))
            record_mock_review(root, contract, MockReviewMode.BLIND_MANUSCRIPT, [objection])
            record_mock_review(root, contract, MockReviewMode.ARTIFACT_AWARE, [objection])
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.TARGETED_REPAIR)["receipt"]["allowed"])
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.CLAIM_AUDIT)["receipt"]["allowed"])
            record_claim_audit(root, contract, manuscript_ref="artifact:paper", claimed_ids=("C1",), evidence_bound_claim_ids=("C1",), limitations_preserved=True)
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.PDF_QA)["receipt"]["allowed"])
            record_manuscript_ci(root, contract, {name: True for name in MANDATORY_MANUSCRIPT_CI_CHECKS})
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.PREBUTTAL)["receipt"]["allowed"])
            record_prebuttal(root, contract, [objection], [PrebuttalResolution("R1", True, ("artifact:evidence",))])

            blocked_readiness = record_submission_readiness(root, contract)
            self.assertFalse(blocked_readiness["events"][-1]["receipt"]["submission_ready"])
            blocked_transition = advance_paper_ledger(root, contract, PaperState.SUBMISSION_READY)
            self.assertFalse(blocked_transition["receipt"]["allowed"])
            self.assertIn("paper-preparation-pass-receipt-required", blocked_transition["receipt"]["blockers"])

            row = record_paper_preparation(root, contract, passing_packet())
            self.assertTrue(row["events"][-1]["receipt"]["pass"])
            row = record_submission_readiness(root, contract)
            self.assertTrue(row["events"][-1]["receipt"]["submission_ready"])
            transition = advance_paper_ledger(root, contract, PaperState.SUBMISSION_READY)
            self.assertTrue(transition["receipt"]["allowed"])
            self.assertTrue(transition["receipt"]["gate_receipts"]["paper_preparation_receipt_sha256"])
            self.assertEqual(validate_paper_ledger(transition["ledger"]), [])
            self.assertEqual(transition["ledger"]["summary"]["paper_preparation_receipts"], 1)

    def test_system_state_documents_external_inspirations_without_authority(self) -> None:
        state = build_paper_preparation_system_state()
        self.assertEqual(state["summary"]["required_gates"], 8)
        self.assertGreaterEqual(len(state["inspirations"]), 5)
        self.assertEqual(state["summary"]["automatic_submission_authority"], 0)
        self.assertFalse(state["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
