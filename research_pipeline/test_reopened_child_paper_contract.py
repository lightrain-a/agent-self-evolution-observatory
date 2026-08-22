from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .reopened_child_claim_audit import build_child_claim_audit
from .reopened_child_paper_contract import (
    STATUS,
    build_child_paper_contract,
    load_child_paper_contract,
    public_child_paper_contract,
    publish_child_paper_contract,
    validate_child_paper_contract,
)
from .test_reopened_child_claim_audit import ReopenedChildClaimAuditTest


class ReopenedChildPaperContractTest(unittest.TestCase):
    def fixture(self, root: Path, *, include_new: bool = False):
        helper = ReopenedChildClaimAuditTest(methodName="test_existing_and_boundary_claims_pass_to_contract_revision_not_claim_update")
        if include_new:
            from .test_reopened_scientific_evidence_paper_handoff import ReopenedScientificEvidencePaperHandoffTest
            source = ReopenedScientificEvidencePaperHandoffTest(methodName="test_method_pass_creates_child_revision_handoff_but_not_claim_or_preparation_authority")
            spec = source.revision_spec()
            spec["candidate_claims"].append({
                "claim_id": "C-NEW-CHILD",
                "claim_text": "A new broader child claim.",
                "evidence_role": "SUPPORTING",
                "claim_relation": "NEW_CHILD_CLAIM",
            })
            handoff = helper.handoff(root, spec=spec)
        else:
            handoff = helper.handoff(root)
        audit = build_child_claim_audit(handoff=handoff, audit_packet=helper.packet(handoff))
        return handoff, audit

    def spec(self, audit: dict) -> dict:
        wording = {
            claim_id: (
                "The reopened method produces the preregistered effect on fresh held-out confirmatory units within the child scientific contract."
                if claim_id == "C-REOPEN-METHOD"
                else "The reopened evidence supports only the frozen child-contract and same-information comparison boundary."
            )
            for claim_id in audit["supported_claim_ids"]
        }
        return {
            "claim_wording": wording,
            "manuscript_scope": "Only the reopened child scientific contract and fresh confirmatory P0 evidence are used for this revision.",
            "limitations_boundary": "Claims remain bounded to the fresh held-out confirmatory split, same-information baselines, and audited method-realization scope.",
            "parent_submitted_bytes_immutable": True,
            "preserve_parent_claims_not_listed": True,
        }

    def test_contract_freezes_supported_claim_delta_without_parent_update_or_preparation_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff, audit = self.fixture(root)
            contract = build_child_paper_contract(handoff=handoff, claim_audit=audit, revision_spec=self.spec(audit))
            self.assertTrue(validate_child_paper_contract(contract))
            self.assertEqual(contract["status"], STATUS)
            self.assertEqual(len(contract["supported_claims"]), 2)
            self.assertTrue(contract["child_claim_revision_frozen"])
            self.assertTrue(contract["paper_preparation_review_eligible"])
            self.assertFalse(contract["paper_preparation_authorized"])
            self.assertFalse(contract["submission_eligible"])
            self.assertFalse(contract["parent_claim_update_authorized"])
            self.assertFalse(contract["new_claim_expansion_authorized"])
            self.assertTrue(contract["parent_submitted_bytes_immutable"])
            self.assertTrue(contract["method_pass_not_principle_proof"])

    def test_held_new_claims_are_excluded_from_child_contract(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff, audit = self.fixture(root, include_new=True)
            self.assertEqual(audit["held_new_claim_ids"], ["C-NEW-CHILD"])
            contract = build_child_paper_contract(handoff=handoff, claim_audit=audit, revision_spec=self.spec(audit))
            self.assertEqual(contract["held_new_claim_ids"], ["C-NEW-CHILD"])
            self.assertNotIn("C-NEW-CHILD", [row["claim_id"] for row in contract["supported_claims"]])
            self.assertTrue(contract["held_new_claims_excluded_from_contract"])
            self.assertFalse(contract["new_claim_expansion_authorized"])

    def test_wording_must_cover_exact_audit_supported_claims(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff, audit = self.fixture(root); spec = self.spec(audit)
            spec["claim_wording"].pop("C-REOPEN-BOUNDARY")
            with self.assertRaisesRegex(RuntimeError, "cover exactly"):
                build_child_paper_contract(handoff=handoff, claim_audit=audit, revision_spec=spec)
            spec = self.spec(audit); spec["claim_wording"]["C-EXTRA"] = "extra"
            with self.assertRaisesRegex(RuntimeError, "cover exactly"):
                build_child_paper_contract(handoff=handoff, claim_audit=audit, revision_spec=spec)

    def test_parent_submission_and_untouched_claim_preservation_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff, audit = self.fixture(root)
            for key in ("parent_submitted_bytes_immutable", "preserve_parent_claims_not_listed"):
                spec = self.spec(audit); spec[key] = False
                with self.assertRaisesRegex(RuntimeError, "preserve parent"):
                    build_child_paper_contract(handoff=handoff, claim_audit=audit, revision_spec=spec)

    def test_contract_is_immutable_per_attempt_and_public_projection_is_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff, audit = self.fixture(root); contract = build_child_paper_contract(handoff=handoff, claim_audit=audit, revision_spec=self.spec(audit))
            first = publish_child_paper_contract(root, contract); second = publish_child_paper_contract(root, contract)
            self.assertEqual(first["child_paper_contract_sha256"], second["child_paper_contract_sha256"])
            loaded = load_child_paper_contract(root, handoff["attempt_sha256"])
            self.assertEqual(loaded["child_paper_contract_sha256"], contract["child_paper_contract_sha256"])
            public = public_child_paper_contract(root, handoff["attempt_sha256"])
            self.assertEqual(public["status"], STATUS)
            self.assertEqual(public["supported_claims"], 2)
            self.assertFalse(public["paper_preparation_authorized"])
            self.assertFalse(public["submission_eligible"])
            raw = json.dumps(public)
            self.assertNotIn("claim_text", raw)
            different = copy.deepcopy(contract); different["manuscript_scope"] += " changed"; different["child_paper_contract_sha256"] = "0" * 64
            with self.assertRaisesRegex(RuntimeError, "invalid child paper contract"):
                publish_child_paper_contract(root, different)

    def test_tamper_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff, audit = self.fixture(root); contract = build_child_paper_contract(handoff=handoff, claim_audit=audit, revision_spec=self.spec(audit))
            bad = copy.deepcopy(contract); bad["paper_preparation_authorized"] = True
            self.assertFalse(validate_child_paper_contract(bad))
            bad2 = copy.deepcopy(contract); bad2["supported_claims"][0]["claim_text"] = "tampered"
            self.assertFalse(validate_child_paper_contract(bad2))


if __name__ == "__main__":
    unittest.main()
