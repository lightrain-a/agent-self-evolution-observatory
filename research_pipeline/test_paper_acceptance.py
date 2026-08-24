from __future__ import annotations

import copy
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
    ReviewActionClass,
    ReviewerObjection,
    ScientificPaperStatus,
    StoryCandidate,
    build_claim_audit_receipt,
    build_mock_review_receipt,
    build_paper_acceptance_system_state,
    build_story_search_receipt,
    build_submission_readiness_receipt,
    compile_review_action,
    evaluate_story_search,
    evaluate_manuscript_ci,
    evaluate_paper_transition,
    evaluate_prebuttal,
    evaluate_submission_ready,
    paper_phase_experiment_value,
)
from .paper_acceptance_ledger import (
    advance_paper_ledger,
    build_paper_ledger_index,
    build_portable_paper_ledger_index,
    initialize_paper_ledger,
    record_claim_audit,
    record_manuscript_ci,
    record_mock_review,
    record_story_search,
    record_prebuttal,
    record_submission_readiness,
    revise_paper_contract,
    reopen_ready_paper_contract,
    validate_paper_ledger,
    public_paper_ledger_summary,
)


class PaperAcceptanceTest(unittest.TestCase):
    def stri_contract(self) -> PaperContract:
        return PaperContract(
            paper_id="STRI",
            title="Self-Evolution Should Not Depend on How Skills Are Split",
            central_question="Should equivalent skill-taxonomy representations change self-evolution decisions?",
            supported_claims={
                "C1": "STRI is an exact certificate for the frozen representation-invariance claim.",
                "C2": "The frozen static evaluation contains positive and negative controls supporting the certificate boundary.",
            },
            unsupported_claims={"U1": "STRI improves downstream dynamic self-evolution utility."},
            limitations=("The frozen claim is static and deliberately narrower than downstream utility.",),
            evidence_refs=("stri:theorem", "stri:table-main", "stri:negative-control"),
            scientific_status=ScientificPaperStatus.READY,
        )

    def _advance_ready_contract_to_submission_ready(self, root: Path, contract: PaperContract) -> None:
        initialize_paper_ledger(root, contract)
        self.assertTrue(advance_paper_ledger(root, contract, PaperState.PAPER_DESIGN)["receipt"]["allowed"])
        record_story_search(root, contract, [StoryCandidate("story-a", "Certificate", "Exact certificate", tuple(contract.supported_claims), tuple(contract.supported_claims))])
        self.assertTrue(advance_paper_ledger(root, contract, PaperState.MANUSCRIPT)["receipt"]["allowed"])
        self.assertTrue(advance_paper_ledger(root, contract, PaperState.MOCK_PC)["receipt"]["allowed"])
        objection = ReviewerObjection("R1", "significance", "Main reject reason", True, ObjectionEvidenceState.EXISTING_EVIDENCE, (next(iter(contract.supported_claims)),))
        record_mock_review(root, contract, MockReviewMode.BLIND_MANUSCRIPT, [objection])
        record_mock_review(root, contract, MockReviewMode.ARTIFACT_AWARE, [objection])
        self.assertTrue(advance_paper_ledger(root, contract, PaperState.TARGETED_REPAIR)["receipt"]["allowed"])
        self.assertTrue(advance_paper_ledger(root, contract, PaperState.CLAIM_AUDIT)["receipt"]["allowed"])
        claim_ids = tuple(contract.supported_claims)
        record_claim_audit(root, contract, manuscript_ref="artifact:manuscript", claimed_ids=claim_ids, evidence_bound_claim_ids=claim_ids, limitations_preserved=True)
        self.assertTrue(advance_paper_ledger(root, contract, PaperState.PDF_QA)["receipt"]["allowed"])
        record_manuscript_ci(root, contract, {name: True for name in MANDATORY_MANUSCRIPT_CI_CHECKS})
        self.assertTrue(advance_paper_ledger(root, contract, PaperState.PREBUTTAL)["receipt"]["allowed"])
        record_prebuttal(root, contract, [objection], [PrebuttalResolution("R1", True, tuple(contract.evidence_refs[:1]))])
        row = record_submission_readiness(root, contract)
        self.assertTrue(row["events"][-1]["receipt"]["submission_ready"])
        self.assertTrue(advance_paper_ledger(root, contract, PaperState.SUBMISSION_READY)["receipt"]["allowed"])

    @staticmethod
    def _reframed_stri_contract(base: PaperContract, *, drop_prior_evidence: bool = False) -> PaperContract:
        refs = (() if drop_prior_evidence else tuple(base.evidence_refs)) + ("artifact:sha256:" + "a" * 64,)
        return PaperContract(
            paper_id=base.paper_id,
            title="Representation-Invariance Audits Need a Revised Boundary",
            central_question="Which representation-invariance claims survive newly bound contradictory evidence?",
            supported_claims={
                "C1": base.supported_claims["C1"],
                "C2": "The new evidence narrows the former static-control interpretation.",
                "C3": "A newly observed audit boundary is evidence-backed under the revised contract.",
            },
            unsupported_claims={**base.unsupported_claims, "U2": "The superseded C2 wording remains evaluator-independent."},
            limitations=base.limitations + ("The new contract supersedes one previously supported interpretation.",),
            evidence_refs=refs,
            scientific_status=ScientificPaperStatus.READY,
        )

    def safety_contract(self) -> PaperContract:
        return PaperContract(
            paper_id="AGENT-SAFETY-R9",
            title="Future First-Violation Hazard after Persistent State Evolution",
            central_question="Does the current static safety panel predict future first-violation hazard?",
            supported_claims={
                "C1": "Passing the frozen three-probe panel does not guarantee no future first-violation event under the observed combined condition."
            },
            unsupported_claims={
                "U1": "Persistent experience evolution itself causally produced the future violation."
            },
            limitations=("Persistent update and held-out schedule change are not yet separated.",),
            reopen_conditions=("Run a preregistered no-update control on the same held-out schedule.",),
            evidence_refs=("agent-safety:r9-claim-table",),
            scientific_status=ScientificPaperStatus.CAUSAL_HOLD,
        )

    def test_stri_can_enter_paper_design_without_granting_authority(self) -> None:
        gate = evaluate_paper_transition(self.stri_contract(), PaperState.PAPER_EVIDENCE, PaperState.PAPER_DESIGN)
        self.assertTrue(gate["allowed"])
        self.assertFalse(gate["scientific_authority"])
        self.assertFalse(gate["experiment_authority"])
        self.assertFalse(gate["gpu_authority"])

    def test_agent_safety_causal_hold_blocks_paper_design(self) -> None:
        gate = evaluate_paper_transition(self.safety_contract(), PaperState.PAPER_EVIDENCE, PaperState.PAPER_DESIGN)
        self.assertFalse(gate["allowed"])
        self.assertIn("causal-hold", gate["blockers"])

    def test_story_search_can_reorder_supported_claims_but_not_expand_them(self) -> None:
        contract = self.stri_contract()
        valid = StoryCandidate("story-a", "Certificate framing", "Exact audit certificate", ("C2", "C1"), ("C1",), ("fig-1", "table-1"))
        invalid = StoryCandidate("story-b", "Utility framing", "Dynamic utility story", ("C1", "U1"), ("U1",))
        self.assertEqual(valid.validate(contract), ())
        self.assertTrue(any("U1" in row for row in invalid.validate(contract)))

    def test_story_search_ranks_only_valid_supported_stories(self) -> None:
        contract = self.stri_contract()
        valid = StoryCandidate("story-a", "Certificate framing", "Exact audit certificate", ("C1", "C2"), ("C1", "C2"))
        invalid = StoryCandidate("story-b", "Utility framing", "Dynamic utility story", ("C1", "U1"), ("U1",))
        result = evaluate_story_search(contract, [invalid, valid])
        self.assertEqual(result["selected_story_id"], "story-a")
        self.assertFalse(result["claim_expansion_authorized"])
        self.assertEqual(result["valid_candidates"], 1)
        receipt = build_story_search_receipt(contract, [invalid, valid])
        self.assertTrue(receipt["pass"])
        self.assertEqual(receipt["selected_story_id"], "story-a")
        self.assertEqual(len(receipt["story_search_sha256"]), 64)

    def test_mock_review_modes_remain_distinct(self) -> None:
        state = build_paper_acceptance_system_state()
        self.assertEqual(set(state["mock_review_modes"]), {MockReviewMode.BLIND_MANUSCRIPT.value, MockReviewMode.ARTIFACT_AWARE.value})
        self.assertEqual(state["summary"]["automatic_scientific_authority"], 0)
        self.assertEqual(state["summary"]["automatic_submission_authority"], 0)

    def test_review_compiler_uses_existing_evidence_for_narrative_repair(self) -> None:
        objection = ReviewerObjection("R1", "significance", "Why should the community care?", True, ObjectionEvidenceState.EXISTING_EVIDENCE, ("C1",))
        action = compile_review_action(objection, self.stri_contract())
        self.assertEqual(action.action_class, ReviewActionClass.NARRATIVE_REPAIR)
        self.assertFalse(action.execution_authorized)
        self.assertFalse(action.claim_expansion_authorized)

    def test_review_compiler_proposes_but_does_not_authorize_targeted_experiment(self) -> None:
        objection = ReviewerObjection("R2", "confound", "Separate persistent update from schedule effect.", True, ObjectionEvidenceState.MISSING_DECISIVE_EVIDENCE, ("C1",))
        action = compile_review_action(objection, self.safety_contract())
        self.assertEqual(action.action_class, ReviewActionClass.TARGETED_EXPERIMENT)
        self.assertFalse(action.execution_authorized)
        self.assertFalse(action.scientific_authority)

    def test_unknown_claim_cannot_be_smuggled_as_existing_evidence(self) -> None:
        objection = ReviewerObjection("R0", "scope", "Treat unsupported utility as established.", True, ObjectionEvidenceState.EXISTING_EVIDENCE, ("U1",))
        action = compile_review_action(objection, self.stri_contract())
        self.assertEqual(action.action_class, ReviewActionClass.PRESERVE_LIMITATION)

    def test_mock_review_receipt_is_zero_authority(self) -> None:
        objection = ReviewerObjection("R2", "evidence", "Need one decisive check.", True, ObjectionEvidenceState.MISSING_DECISIVE_EVIDENCE, ("C1",))
        receipt = build_mock_review_receipt(self.stri_contract(), MockReviewMode.BLIND_MANUSCRIPT, [objection])
        self.assertEqual(receipt["summary"]["targeted_experiment_proposals"], 1)
        self.assertFalse(receipt["experiment_authority"])
        self.assertFalse(receipt["actions"][0]["execution_authorized"])

    def test_review_compiler_preserves_limitation_for_new_claim_request(self) -> None:
        objection = ReviewerObjection("R3", "scope", "Prove dynamic downstream utility.", True, ObjectionEvidenceState.REQUIRES_NEW_CLAIM, ("U1",))
        action = compile_review_action(objection, self.stri_contract())
        self.assertEqual(action.action_class, ReviewActionClass.PRESERVE_LIMITATION)
        self.assertFalse(action.claim_expansion_authorized)

    def test_prebuttal_fails_closed_on_unresolved_decision_critical_objection(self) -> None:
        objections = [ReviewerObjection("R1", "significance", "Main reject reason", True, ObjectionEvidenceState.EXISTING_EVIDENCE, ("C1",))]
        failed = evaluate_prebuttal(objections, [])
        passed = evaluate_prebuttal(objections, [PrebuttalResolution("R1", True, ("stri:theorem",))])
        self.assertFalse(failed["pass"])
        self.assertTrue(passed["pass"])

    def test_manuscript_ci_requires_every_mandatory_check(self) -> None:
        checks = {name: True for name in MANDATORY_MANUSCRIPT_CI_CHECKS}
        self.assertTrue(evaluate_manuscript_ci(checks)["pass"])
        checks.pop("statement-evidence-binding")
        result = evaluate_manuscript_ci(checks)
        self.assertFalse(result["pass"])
        self.assertIn("statement-evidence-binding", result["missing"])

    def test_submission_ready_requires_science_ci_and_prebuttal(self) -> None:
        contract = self.stri_contract()
        ci = evaluate_manuscript_ci({name: True for name in MANDATORY_MANUSCRIPT_CI_CHECKS})
        prebuttal = {"pass": True}
        ready = evaluate_submission_ready(contract, ci, prebuttal)
        self.assertTrue(ready["submission_ready"])
        self.assertFalse(ready["submission_authority"])
        held = evaluate_submission_ready(self.safety_contract(), ci, prebuttal)
        self.assertFalse(held["submission_ready"])
        self.assertIn("causal-hold", held["blockers"])

    def test_submission_readiness_receipt_is_content_addressed_and_zero_authority(self) -> None:
        contract = self.stri_contract()
        ci = evaluate_manuscript_ci({name: True for name in MANDATORY_MANUSCRIPT_CI_CHECKS})
        receipt = build_submission_readiness_receipt(contract, ci, {"pass": True})
        self.assertTrue(receipt["submission_ready"])
        self.assertEqual(len(receipt["receipt_sha256"]), 64)
        self.assertFalse(receipt["submission_authority"])

    def test_claim_audit_receipt_fails_on_unsupported_claim_and_passes_on_bound_claims(self) -> None:
        contract = self.stri_contract()
        failed = build_claim_audit_receipt(
            contract,
            manuscript_ref="artifact:manuscript",
            claimed_ids=("C1", "U1"),
            evidence_bound_claim_ids=("C1",),
            unsupported_claim_ids_present=("U1",),
            limitations_preserved=True,
        )
        self.assertFalse(failed["pass"])
        passed = build_claim_audit_receipt(
            contract,
            manuscript_ref="artifact:manuscript",
            claimed_ids=("C1", "C2"),
            evidence_bound_claim_ids=("C1", "C2"),
            limitations_preserved=True,
        )
        self.assertTrue(passed["pass"])
        self.assertEqual(len(passed["claim_audit_sha256"]), 64)

    def test_append_only_ledger_records_hold_without_advancing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract = self.safety_contract()
            initialize_paper_ledger(root, contract)
            result = advance_paper_ledger(root, contract, PaperState.PAPER_DESIGN)
            self.assertFalse(result["receipt"]["allowed"])
            self.assertEqual(result["ledger"]["current_state"], PaperState.PAPER_EVIDENCE.value)
            self.assertEqual(result["ledger"]["summary"]["blocked_transitions"], 1)
            self.assertEqual(validate_paper_ledger(result["ledger"]), [])

    def test_scientific_evidence_closure_can_append_ready_contract_revision(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            held = self.safety_contract()
            initialize_paper_ledger(root, held)
            blocked = advance_paper_ledger(root, held, PaperState.PAPER_DESIGN)
            self.assertFalse(blocked["receipt"]["allowed"])
            revised = PaperContract(
                paper_id=held.paper_id,
                title=held.title,
                central_question=held.central_question,
                supported_claims={
                    **dict(held.supported_claims),
                    "C2": "The same held-out schedule produced more branch first-violation events after persistent update than under the base-workflow no-update control in the frozen paired design.",
                },
                unsupported_claims=dict(held.unsupported_claims),
                limitations=("The controlled contrast remains a finite frozen-design result, not a population effect estimate.",),
                evidence_refs=(*held.evidence_refs, "agent-safety:r23-no-update-control"),
                scientific_status=ScientificPaperStatus.READY,
            )
            row = revise_paper_contract(
                root,
                revised,
                closure_evidence_refs=("agent-safety:r23-no-update-control",),
                reason="The preregistered same-schedule no-update control closed the recorded causal hold for the frozen finite design.",
            )
            self.assertEqual(row["scientific_status"], ScientificPaperStatus.READY.value)
            self.assertEqual(row["summary"]["contract_revisions"], 1)
            self.assertEqual(validate_paper_ledger(row), [])
            advanced = advance_paper_ledger(root, revised, PaperState.PAPER_DESIGN)
            self.assertTrue(advanced["receipt"]["allowed"])
            self.assertEqual(validate_paper_ledger(advanced["ledger"]), [])

    def test_new_story_search_binds_zero_authority_paper_design_memory_pack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); contract = self.stri_contract()
            initialize_paper_ledger(root, contract)
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.PAPER_DESIGN)["receipt"]["allowed"])
            pack = {
                "purpose": "PAPER_DESIGN",
                "wiki_sha256": "a" * 64,
                "query_pack_sha256": "b" * 64,
                "selected_memory_ids": ["MEM-REVIEW"],
                "selected": [{"memory_id": "MEM-REVIEW", "kind": "REVIEW_LESSON"}],
                "summary": {"selected": 1},
                "scientific_authority": False,
            }
            row = record_story_search(
                root,
                contract,
                [StoryCandidate("story-a", "Certificate", "Exact certificate", ("C1", "C2"), ("C1", "C2"))],
                research_memory_query_pack=pack,
            )
            receipt = next(event["receipt"] for event in row["events"] if event.get("event_type") == "story-search")
            memory = receipt["paper_design_memory_query_receipt"]
            self.assertEqual((memory["purpose"], memory["selected"], memory["review_lessons_selected"]), ("PAPER_DESIGN", 1, 1))
            self.assertFalse(memory["scientific_authority"])
            public = public_paper_ledger_summary(row)
            self.assertEqual(public["latest_story_search"]["paper_design_memory_query_pack_sha256"], "b" * 64)
            self.assertEqual(len(public["latest_story_search"]["paper_design_memory_binding_sha256"]), 64)
            self.assertEqual(public["latest_story_search"]["paper_design_review_lessons_selected"], 1)
            tampered = copy.deepcopy(row)
            story_event = next(event for event in tampered["events"] if event.get("event_type") == "story-search")
            story_event["receipt"]["paper_design_memory_query_receipt"]["selected_memory_ids"] = ["MEM-TAMPERED"]
            self.assertIn("invalid-content-addressed-receipt:story-search", validate_paper_ledger(tampered))

    def test_story_search_rejects_non_paper_design_or_authoritative_memory_pack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); contract = self.stri_contract()
            initialize_paper_ledger(root, contract)
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.PAPER_DESIGN)["receipt"]["allowed"])
            story = [StoryCandidate("story-a", "Certificate", "Exact certificate", ("C1", "C2"), ("C1", "C2"))]
            bad = {"purpose":"EXPERIMENT_DESIGN","wiki_sha256":"a"*64,"query_pack_sha256":"b"*64,"summary":{"selected":0},"selected":[],"selected_memory_ids":[],"scientific_authority":False}
            with self.assertRaises(ValueError):
                record_story_search(root, contract, story, research_memory_query_pack=bad)
            bad["purpose"]="PAPER_DESIGN";bad["scientific_authority"]=True
            with self.assertRaises(ValueError):
                record_story_search(root, contract, story, research_memory_query_pack=bad)

    def test_scientific_contract_revision_cannot_drop_previous_claim_or_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            held = self.safety_contract()
            initialize_paper_ledger(root, held)
            invalid = PaperContract(
                paper_id=held.paper_id,
                title=held.title,
                central_question=held.central_question,
                supported_claims={"C2": "A different claim."},
                evidence_refs=("agent-safety:r23-no-update-control",),
                scientific_status=ScientificPaperStatus.READY,
            )
            with self.assertRaises(RuntimeError):
                revise_paper_contract(
                    root,
                    invalid,
                    closure_evidence_refs=("agent-safety:r23-no-update-control",),
                    reason="invalid revision",
                )

    def test_ledger_requires_three_new_hard_gate_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); contract = self.stri_contract()
            initialize_paper_ledger(root, contract)
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.PAPER_DESIGN)["receipt"]["allowed"])
            blocked = advance_paper_ledger(root, contract, PaperState.MANUSCRIPT)
            self.assertFalse(blocked["receipt"]["allowed"])
            self.assertIn("story-search-winner-receipt-required", blocked["receipt"]["blockers"])
            record_story_search(root, contract, [StoryCandidate("story-a", "Certificate", "Exact certificate", ("C1", "C2"), ("C1", "C2"))])
            manuscript = advance_paper_ledger(root, contract, PaperState.MANUSCRIPT)
            self.assertTrue(manuscript["receipt"]["allowed"])
            self.assertTrue(manuscript["receipt"]["gate_receipts"]["story_search_sha256"])
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.MOCK_PC)["receipt"]["allowed"])
            objection = ReviewerObjection("R1", "clarity", "Clarify the exact boundary.", True, ObjectionEvidenceState.EXISTING_EVIDENCE, ("C1",))
            record_mock_review(root, contract, MockReviewMode.BLIND_MANUSCRIPT, [objection])
            blocked = advance_paper_ledger(root, contract, PaperState.TARGETED_REPAIR)
            self.assertFalse(blocked["receipt"]["allowed"])
            self.assertTrue(any(item.startswith("mock-pc-modes-incomplete:") for item in blocked["receipt"]["blockers"]))
            record_mock_review(root, contract, MockReviewMode.ARTIFACT_AWARE, [objection])
            repair = advance_paper_ledger(root, contract, PaperState.TARGETED_REPAIR)
            self.assertTrue(repair["receipt"]["allowed"])
            self.assertEqual(set(repair["receipt"]["gate_receipts"]["mock_pc_review_sha256"]), {mode.value for mode in MockReviewMode})
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.CLAIM_AUDIT)["receipt"]["allowed"])
            blocked = advance_paper_ledger(root, contract, PaperState.PDF_QA)
            self.assertFalse(blocked["receipt"]["allowed"])
            self.assertIn("claim-audit-pass-receipt-required", blocked["receipt"]["blockers"])
            record_claim_audit(root, contract, manuscript_ref="artifact:manuscript", claimed_ids=("C1", "C2"), evidence_bound_claim_ids=("C1", "C2"), limitations_preserved=True)
            pdf_qa = advance_paper_ledger(root, contract, PaperState.PDF_QA)
            self.assertTrue(pdf_qa["receipt"]["allowed"])
            self.assertTrue(pdf_qa["receipt"]["gate_receipts"]["claim_audit_sha256"])

    def test_ledger_requires_ci_prebuttal_and_external_submission_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); contract = self.stri_contract()
            initialize_paper_ledger(root, contract)
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.PAPER_DESIGN)["receipt"]["allowed"])
            record_story_search(root, contract, [StoryCandidate("story-a", "Certificate", "Exact certificate", ("C1", "C2"), ("C1", "C2"))])
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.MANUSCRIPT)["receipt"]["allowed"])
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.MOCK_PC)["receipt"]["allowed"])
            objection = ReviewerObjection("R1", "significance", "Main reject reason", True, ObjectionEvidenceState.EXISTING_EVIDENCE, ("C1",))
            record_mock_review(root, contract, MockReviewMode.BLIND_MANUSCRIPT, [objection])
            record_mock_review(root, contract, MockReviewMode.ARTIFACT_AWARE, [objection])
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.TARGETED_REPAIR)["receipt"]["allowed"])
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.CLAIM_AUDIT)["receipt"]["allowed"])
            record_claim_audit(root, contract, manuscript_ref="artifact:manuscript", claimed_ids=("C1", "C2"), evidence_bound_claim_ids=("C1", "C2"), limitations_preserved=True)
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.PDF_QA)["receipt"]["allowed"])
            blocked = advance_paper_ledger(root, contract, PaperState.PREBUTTAL)
            self.assertFalse(blocked["receipt"]["allowed"])
            record_manuscript_ci(root, contract, {name: True for name in MANDATORY_MANUSCRIPT_CI_CHECKS})
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.PREBUTTAL)["receipt"]["allowed"])
            objections = [objection]
            record_prebuttal(root, contract, objections, [PrebuttalResolution("R1", True, ("stri:theorem",))])
            row = record_submission_readiness(root, contract)
            self.assertTrue((row["events"][-1]["receipt"])["submission_ready"])
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.SUBMISSION_READY)["receipt"]["allowed"])
            self.assertFalse(advance_paper_ledger(root, contract, PaperState.SUBMITTED)["receipt"]["allowed"])
            submitted = advance_paper_ledger(root, contract, PaperState.SUBMITTED, external_submission_authority_ref="human:submit-approval")
            self.assertTrue(submitted["receipt"]["allowed"])
            self.assertFalse(submitted["receipt"]["submission_authority"])

    def test_ready_submission_can_scientifically_reopen_with_explicit_claim_withdrawal(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); original = self.stri_contract()
            self._advance_ready_contract_to_submission_ready(root, original)
            revised = self._reframed_stri_contract(original)
            row = reopen_ready_paper_contract(
                root, revised,
                reopen_evidence_refs=("artifact:sha256:" + "a" * 64,),
                superseded_claims={"C2": "New contradictory evidence narrows the former supported interpretation."},
                reason="Fresh evidence changes a previously supported claim and requires complete paper-gate re-audit.",
            )
            self.assertEqual(row["current_state"], PaperState.PAPER_EVIDENCE.value)
            self.assertEqual(row["scientific_status"], "READY")
            self.assertEqual(row["summary"]["scientific_reopens"], 1)
            self.assertEqual(row["events"][-1]["event_type"], "paper-contract-scientific-reopen")
            self.assertEqual(row["events"][-1]["previous_state"], PaperState.SUBMISSION_READY.value)
            self.assertEqual(validate_paper_ledger(row), [])
            public = public_paper_ledger_summary(row)
            self.assertFalse(public["gate_clean_submission_ready"])
            self.assertFalse(public["latest_paper_preparation"]["pass"])
            self.assertFalse(public["latest_submission_readiness"]["submission_ready"])
            self.assertTrue(advance_paper_ledger(root, revised, PaperState.PAPER_DESIGN)["receipt"]["allowed"])
            stale_gate = advance_paper_ledger(root, revised, PaperState.MANUSCRIPT)
            self.assertFalse(stale_gate["receipt"]["allowed"])
            self.assertIn("story-search-winner-receipt-required", stale_gate["receipt"]["blockers"])

    def test_scientific_reopen_rejects_unaccounted_claims_missing_or_dropped_evidence(self) -> None:
        cases = (
            ("missing-supersede", (), {"C2": "reason"}, False),
            ("unaccounted-claim", ("artifact:sha256:" + "a" * 64,), {}, False),
            ("dropped-prior-evidence", ("artifact:sha256:" + "a" * 64,), {"C2": "reason"}, True),
            ("invalid-evidence-ref", ("artifact:not-content-addressed",), {"C2": "reason"}, False),
        )
        for name, refs, superseded, drop_prior in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                root = Path(td); original = self.stri_contract()
                self._advance_ready_contract_to_submission_ready(root, original)
                revised = self._reframed_stri_contract(original, drop_prior_evidence=drop_prior)
                with self.assertRaises(RuntimeError):
                    reopen_ready_paper_contract(root, revised, reopen_evidence_refs=refs, superseded_claims=superseded, reason="contradictory evidence")

    def test_scientific_reopen_is_forbidden_after_submitted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); original = self.stri_contract()
            self._advance_ready_contract_to_submission_ready(root, original)
            submitted = advance_paper_ledger(root, original, PaperState.SUBMITTED, external_submission_authority_ref="human:submission")
            self.assertTrue(submitted["receipt"]["allowed"])
            revised = self._reframed_stri_contract(original)
            with self.assertRaises(RuntimeError):
                reopen_ready_paper_contract(
                    root, revised,
                    reopen_evidence_refs=("artifact:sha256:" + "a" * 64,),
                    superseded_claims={"C2": "new evidence"},
                    reason="too late after submission",
                )

    def test_validator_detects_tampered_scientific_reopen_claim_accounting(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); original = self.stri_contract()
            self._advance_ready_contract_to_submission_ready(root, original)
            revised = self._reframed_stri_contract(original)
            row = reopen_ready_paper_contract(
                root, revised,
                reopen_evidence_refs=("artifact:sha256:" + "a" * 64,),
                superseded_claims={"C2": "new evidence"},
                reason="evidence contradiction",
            )
            row["events"][-1]["superseded_claims"] = []
            self.assertIn("scientific reopen superseded-claim accounting mismatch", validate_paper_ledger(row))

    def test_public_ledger_index_exposes_state_without_raw_events_or_paths(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); contract = self.stri_contract()
            initialize_paper_ledger(root, contract)
            advance_paper_ledger(root, contract, PaperState.PAPER_DESIGN)
            index = build_paper_ledger_index(root)
            self.assertEqual(index["summary"]["papers"], 1)
            self.assertEqual(index["summary"]["invalid_ledgers"], 0)
            entry = index["entries"][0]
            self.assertEqual(entry["current_state"], PaperState.PAPER_DESIGN.value)
            self.assertNotIn("events", entry)
            self.assertNotIn("actor", str(entry))
            self.assertEqual(entry["authority"], {"scientific": False, "experiment": False, "gpu": False, "submission": False})

    def test_portable_registry_reconstructs_canonical_zero_authority_index(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); contract = self.stri_contract()
            initialize_paper_ledger(root, contract)
            advance_paper_ledger(root, contract, PaperState.PAPER_DESIGN)
            source = build_paper_ledger_index(root)["entries"][0]
        registry_row = dict(source)
        registry_row["acceptance_paper_id"] = "STRI-ICLR2027"
        registry_row["paper_id"] = "STRI"
        registry = {
            "policy": {"paper_registry_is_projection_of_append_only_acceptance_ledgers": True},
            "papers": [registry_row],
        }
        index = build_portable_paper_ledger_index(registry)
        self.assertEqual(index["summary"]["papers"], 1)
        self.assertEqual(index["summary"]["invalid_ledgers"], 0)
        self.assertEqual(index["entries"][0]["paper_id"], "STRI-ICLR2027")
        self.assertEqual((index["summary"]["internal_action_required"], index["summary"]["no_internal_action"]), (1, 0))
        self.assertEqual(index["summary"]["by_internal_action"], {"PAPER_WORKFLOW_CONTINUE": 1})
        self.assertEqual(index["entries"][0]["primary_next_action"]["action_class"], "PAPER_WORKFLOW_CONTINUE")
        self.assertFalse(index["scientific_authority"])
        self.assertTrue(index["policy"]["empty_machine_local_ledger_does_not_erase_portable_state"])
        self.assertTrue(index["policy"]["primary_next_action_is_internal_only_and_zero_authority"])

    def test_public_ledger_index_keeps_causal_hold_visible(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); contract = self.safety_contract()
            initialize_paper_ledger(root, contract)
            advance_paper_ledger(root, contract, PaperState.PAPER_DESIGN)
            index = build_paper_ledger_index(root)
            self.assertEqual(index["summary"]["scientific_holds"], 1)
            self.assertEqual(index["entries"][0]["current_state"], PaperState.PAPER_EVIDENCE.value)
            self.assertIn("causal-hold", index["entries"][0]["latest_transition"]["blockers"])

    def test_public_projection_keeps_later_preparation_failure_visible_after_submission_ready(self) -> None:
        row = {
            "paper_id": "PAPER-X",
            "contract_sha256": "contract-sha",
            "scientific_status": ScientificPaperStatus.READY.value,
            "current_state": PaperState.SUBMISSION_READY.value,
            "contract": {
                "title": "Paper X",
                "central_question": "Does the later readiness audit remain visible?",
                "supported_claims": {"C1": "Supported."},
                "active_unrefuted_claims": {"C2": "Still active."},
                "unsupported_claims": {},
                "limitations": [],
                "reopen_conditions": [],
            },
            "events": [
                {"event_type": "submission-readiness", "receipt": {"submission_ready": True, "receipt_sha256": "ready-sha", "blockers": []}},
                {"event_type": "paper-preparation", "receipt": {"pass": False, "protocol_version": "1.0", "receipt_sha256": "prep-sha", "summary": {"required_gates": 8, "passed_gates": 1}, "gate_pass": {"citation-integrity": True, "visual-story": False}, "blockers": ["visual-story-check-failed"]}},
                {"event_type": "submission-readiness-context", "artifact_submission_ready": True, "recommended_immediate_submission": "HOLD_FOR_EVIDENCE", "scientific_status": "READY", "support_blocker": "EXTERNAL_EVIDENCE_MISSING", "external_human_submission_authority_required_for_SUBMITTED": True, "c3_c4_evidence_state": "ACTIVE_UNREFUTED_DATA_PENDING_EXTERNAL_SUPPORT", "post_repair_mock_pc_recommendations": ["reject"], "post_repair_mock_pc_scores": [3]},
            ],
        }
        public = public_paper_ledger_summary(row)
        self.assertEqual(public["current_state"], PaperState.SUBMISSION_READY.value)
        self.assertTrue(public["latest_submission_readiness"]["submission_ready"])
        self.assertFalse(public["latest_paper_preparation"]["pass"])
        self.assertEqual((public["latest_paper_preparation"]["passed_gates"], public["latest_paper_preparation"]["required_gates"]), (1, 8))
        self.assertEqual(public["active_unrefuted_claims"], 1)
        self.assertTrue(public["immediate_submission_hold"])
        self.assertFalse(public["gate_clean_submission_ready"])
        self.assertEqual(public["submission_readiness_context"]["recommended_immediate_submission"], "HOLD_FOR_EVIDENCE")
        self.assertEqual(public["submission_readiness_context"]["support_blocker"], "EXTERNAL_EVIDENCE_MISSING")
        self.assertEqual(public["primary_next_action"]["action_class"], "EXTERNAL_EVIDENCE_REQUIRED")
        self.assertEqual(public["primary_next_action"]["blocking_on"], "EXTERNAL_EVIDENCE_MISSING")
        self.assertFalse(public["primary_next_action"]["machine_actionable"])

    def test_public_review_learning_keeps_only_structured_mock_pc_signals(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); contract = self.stri_contract()
            initialize_paper_ledger(root, contract)
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.PAPER_DESIGN)["receipt"]["allowed"])
            record_story_search(root, contract, [StoryCandidate("story-a", "Certificate", "Exact certificate", ("C1", "C2"), ("C1", "C2"))])
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.MANUSCRIPT)["receipt"]["allowed"])
            self.assertTrue(advance_paper_ledger(root, contract, PaperState.MOCK_PC)["receipt"]["allowed"])
            objection = ReviewerObjection("R-PRIVATE", "artifact provenance", "PRIVATE REVIEWER PROSE MUST NOT LEAK", True, ObjectionEvidenceState.EXISTING_EVIDENCE, ("C1",))
            record_mock_review(root, contract, MockReviewMode.BLIND_MANUSCRIPT, [objection])
            record_mock_review(root, contract, MockReviewMode.ARTIFACT_AWARE, [objection])
            index = build_paper_ledger_index(root)
            entry = index["entries"][0]
            learning = entry["review_learning"]
            self.assertEqual(learning["review_receipts"], 2)
            self.assertEqual(learning["decision_critical_objections"], 2)
            self.assertEqual(learning["category_counts"], {"artifact-provenance": 2})
            self.assertEqual(learning["action_class_counts"], {"narrative-repair": 2})
            self.assertFalse(learning["reviewer_prose_exposed"])
            self.assertNotIn("PRIVATE REVIEWER PROSE MUST NOT LEAK", str(entry))
            self.assertNotIn("Existing admissible evidence should be made legible", str(entry))

    def test_public_projection_prefers_later_versioned_finalization_receipts(self) -> None:
        row = {
            "paper_id": "PAPER-R5",
            "contract_sha256": "contract-sha",
            "scientific_status": ScientificPaperStatus.READY.value,
            "current_state": PaperState.SUBMISSION_READY.value,
            "contract": {
                "title": "Old frozen contract title",
                "central_question": "Can a later append-only repair supersede stale public readiness?",
                "supported_claims": {"C1": "Supported."},
                "active_unrefuted_claims": {"C2": "Exact external replication remains active."},
                "unsupported_claims": {},
                "limitations": [],
                "reopen_conditions": [],
            },
            "events": [
                {"event_type": "submission-readiness", "receipt": {"submission_ready": True, "receipt_sha256": "old-ready", "blockers": []}},
                {"event_type": "paper-preparation", "receipt": {"pass": False, "protocol_version": "1.0", "receipt_sha256": "old-prep", "summary": {"required_gates": 8, "passed_gates": 1}, "gate_pass": {}, "blockers": ["old-blocker"]}},
                {"event_type": "submission-readiness-context", "artifact_submission_ready": True, "recommended_immediate_submission": "HOLD_FOR_EVIDENCE", "scientific_status": "READY", "support_blocker": "OLD_EXTERNAL_SUPPORT", "external_human_submission_authority_required_for_SUBMITTED": True},
                {"event_type": "source-native-r5-finalization", "title": "Current repaired manuscript title", "source_native_runtime_valid_rows": 1326, "distinct_endpoints": 35, "institutional_systems": 3, "exact_timesage_replication_debt": "ACTIVE_EXTERNAL_REPLICATION_DEBT_NOT_SUBSTITUTED", "recommended_immediate_action": "READY_FOR_HUMAN_SUBMISSION", "final_state_ref": "artifact:sha256:" + "1" * 64},
                {"event_type": "claim-audit-r5", "pass": True, "checks": 26, "passed": 26, "artifact_ref": "artifact:sha256:" + "2" * 64},
                {"event_type": "mock-pc-final-r5", "scores": [8, 8, 7], "recommendations": ["accept", "accept", "weak_accept"], "mean_score": 7.6666666667, "minimum_score": 7, "decision_critical_blockers": 0, "artifact_ref": "artifact:sha256:" + "3" * 64},
                {"event_type": "paper-preparation-r5", "pass": True, "required_gates": 8, "passed_gates": 8, "blockers": [], "artifact_ref": "artifact:sha256:" + "4" * 64},
                {"event_type": "prebuttal-r5", "pass": True, "decision_critical_objections": 8, "unresolved_decision_critical": 0, "artifact_ref": "artifact:sha256:" + "5" * 64},
                {"event_type": "submission-readiness-context-r5", "artifact_submission_ready": True, "current_state": "SUBMISSION_READY", "scientific_status": "READY", "recommended_immediate_action": "READY_FOR_HUMAN_SUBMISSION", "external_human_submission_authority_required": True, "exact_timesage_replication_debt": "ACTIVE_EXTERNAL_REPLICATION_DEBT_NONBLOCKING_FOR_SOURCE_NATIVE_PAPER", "artifact_ref": "artifact:sha256:" + "6" * 64},
            ],
        }
        public = public_paper_ledger_summary(row)
        self.assertEqual(public["title"], "Current repaired manuscript title")
        self.assertTrue(public["gate_clean_submission_ready"])
        self.assertFalse(public["immediate_submission_hold"])
        self.assertEqual((public["latest_paper_preparation"]["passed_gates"], public["latest_paper_preparation"]["required_gates"]), (8, 8))
        self.assertEqual(public["latest_paper_preparation"]["protocol_version"], "1.0+r5")
        self.assertEqual(public["latest_claim_audit"]["checks"], 26)
        self.assertEqual(public["latest_mock_review"]["summary"]["scores"], [8, 8, 7])
        self.assertEqual(public["submission_readiness_context"]["recommended_immediate_submission"], "READY_FOR_HUMAN_SUBMISSION")
        self.assertEqual(public["submission_readiness_context"]["support_blocker"], "")
        self.assertEqual(public["source_native_evidence"]["runtime_valid_rows"], 1326)
        self.assertEqual(public["source_native_evidence"]["finalization_sha256"], "1" * 64)

    def test_ledger_validator_detects_tampered_hard_gate_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); contract = self.stri_contract()
            initialize_paper_ledger(root, contract)
            advance_paper_ledger(root, contract, PaperState.PAPER_DESIGN)
            row = record_story_search(root, contract, [StoryCandidate("story-a", "Certificate", "Exact certificate", ("C1", "C2"), ("C1", "C2"))])
            self.assertEqual(validate_paper_ledger(row), [])
            row["events"][-1]["receipt"]["selected_story_title"] = "tampered"
            errors = validate_paper_ledger(row)
            self.assertIn("invalid-content-addressed-receipt:story-search", errors)

    def test_paper_phase_experiment_value_prioritizes_reviewer_risk_and_claim_leverage(self) -> None:
        decisive = paper_phase_experiment_value(information_gain=0.9, scientific_decision_value=0.9, reviewer_risk_reduction=1.0, central_claim_leverage=1.0, cost=1.0)
        decorative = paper_phase_experiment_value(information_gain=0.9, scientific_decision_value=0.9, reviewer_risk_reduction=0.1, central_claim_leverage=0.1, cost=1.0)
        self.assertGreater(decisive, decorative)
        with self.assertRaises(ValueError):
            paper_phase_experiment_value(information_gain=1, scientific_decision_value=1, reviewer_risk_reduction=1, central_claim_leverage=1, cost=0)


if __name__ == "__main__":
    unittest.main()
