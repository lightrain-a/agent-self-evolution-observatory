from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .reopened_p0_principle_handoff import build_p0_principle_handoff
from .reopened_p0_principle_memory_authorization import (
    AUTH_STATUS,
    HANDOFF_STATUS,
    MEMORY_DESTINATION,
    build_principle_memory_authorization,
    build_principle_memory_handoff,
    public_principle_memory_state,
    publish_principle_memory_receipt,
    validate_principle_memory_authorization,
    validate_principle_memory_handoff,
    validate_principle_memory_ledger,
)
from .test_reopened_p0_principle_handoff import ReopenedP0PrincipleHandoffTest


class ReopenedP0PrincipleMemoryAuthorizationTest(unittest.TestCase):
    def dead_end_handoff(self, root: Path):
        helper = ReopenedP0PrincipleHandoffTest(methodName="test_positive_counter_explanation_only_creates_human_review_dead_end_candidate")
        adjudication = helper.p0_adjudication(root, "METHOD-FAIL")
        return build_p0_principle_handoff(
            p0_adjudication=adjudication,
            principle_certificate=helper.principle_certificate(),
            principle_evidence=helper.true_negative_evidence(with_counter=True),
        )

    def support_handoff(self, root: Path):
        helper = ReopenedP0PrincipleHandoffTest(methodName="test_method_pass_only_supports_principle_without_proof_or_update_authority")
        adjudication = helper.p0_adjudication(root, "METHOD-PASS")
        return build_p0_principle_handoff(
            p0_adjudication=adjudication,
            principle_certificate=helper.principle_certificate(),
        )

    def memory_spec(self, handoff: dict) -> dict:
        return {
            "title": "Scoped dead-end for the reopened method principle",
            "summary": "Within the frozen confirmatory scope, the registered prediction is contradicted and a same-information reduction positively explains the observation.",
            "scope": "Only the child scientific contract and its fresh confirmatory held-out split.",
            "reopen_condition": "Reopen only if a fresh same-information setting produces stable decision disagreement beyond the certified reduction.",
            "opposite_search_seed": "Search for a new observable that survives the same-information reduction.",
            "source_refs": ["sha256:p0-result", "sha256:counter-explanation"],
            "source_principle_evidence_sha256": handoff["principle_evidence_sha256"],
        }

    def test_only_dead_end_candidate_can_receive_human_principle_memory_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(RuntimeError, "dead-end candidate"):
                build_principle_memory_authorization(
                    principle_handoff=self.support_handoff(root),
                    external_authority_ref="pi:approve-dead-end-memory",
                    authorized_at="2027-04-12T12:00:00+00:00",
                )

    def test_human_authorization_is_scoped_and_does_not_write_memory(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff = self.dead_end_handoff(root)
            auth = build_principle_memory_authorization(
                principle_handoff=handoff,
                external_authority_ref="pi:private-principle-memory-approval",
                authorized_at="2027-04-12T12:00:00+00:00",
            )
            self.assertTrue(validate_principle_memory_authorization(auth))
            self.assertEqual(auth["status"], AUTH_STATUS)
            self.assertTrue(auth["principle_memory_update_authorized"])
            self.assertFalse(auth["automatic_memory_write_authorized"])
            self.assertFalse(auth["persistent_memory_write_completed"])
            self.assertFalse(auth["claim_update_authorized"])
            self.assertFalse((root / "research-memory-wiki.json").exists())

    def test_memory_handoff_requires_exact_evidence_sha_scope_reopen_and_sources(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff = self.dead_end_handoff(root)
            auth = build_principle_memory_authorization(principle_handoff=handoff, external_authority_ref="pi:approve", authorized_at="2027-04-12T12:00:00+00:00")
            spec = self.memory_spec(handoff); spec["source_principle_evidence_sha256"] = "0" * 64
            with self.assertRaisesRegex(RuntimeError, "exact principle evidence SHA"):
                build_principle_memory_handoff(principle_handoff=handoff, authorization=auth, memory_spec=spec)
            spec = self.memory_spec(handoff); spec["reopen_condition"] = ""
            with self.assertRaisesRegex(RuntimeError, "reopen_condition"):
                build_principle_memory_handoff(principle_handoff=handoff, authorization=auth, memory_spec=spec)
            spec = self.memory_spec(handoff); spec["source_refs"] = []
            with self.assertRaisesRegex(RuntimeError, "source refs"):
                build_principle_memory_handoff(principle_handoff=handoff, authorization=auth, memory_spec=spec)

    def test_memory_handoff_is_scoped_core_principle_closure_but_not_automatic_write(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff = self.dead_end_handoff(root)
            auth = build_principle_memory_authorization(principle_handoff=handoff, external_authority_ref="pi:approve", authorized_at="2027-04-12T12:00:00+00:00")
            memory = build_principle_memory_handoff(principle_handoff=handoff, authorization=auth, memory_spec=self.memory_spec(handoff))
            self.assertTrue(validate_principle_memory_handoff(memory))
            self.assertEqual(memory["status"], HANDOFF_STATUS)
            self.assertEqual(memory["destination_gate"], MEMORY_DESTINATION)
            self.assertEqual(memory["memory_class"], "PRINCIPLE_DEAD_END")
            self.assertEqual(memory["failure_layer"], "core_principle")
            self.assertTrue(memory["scientific_dead_end_certified"])
            self.assertTrue(memory["principle_update_allowed"])
            self.assertFalse(memory["automatic_memory_write_authorized"])
            self.assertFalse(memory["persistent_memory_write_completed"])
            self.assertFalse(memory["claim_update_authorized"])

    def test_append_only_order_idempotence_and_public_redaction(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff = self.dead_end_handoff(root)
            auth = build_principle_memory_authorization(principle_handoff=handoff, external_authority_ref="pi:private-principle-memory-approval", authorized_at="2027-04-12T12:00:00+00:00")
            memory = build_principle_memory_handoff(principle_handoff=handoff, authorization=auth, memory_spec=self.memory_spec(handoff))
            with self.assertRaisesRegex(RuntimeError, "published human principle authorization"):
                publish_principle_memory_receipt(root, memory, recorded_at="2027-04-12T13:00:00+00:00")
            first = publish_principle_memory_receipt(root, auth, recorded_at="2027-04-12T12:00:00+00:00")
            row = publish_principle_memory_receipt(root, memory, recorded_at="2027-04-12T13:00:00+00:00")
            row2 = publish_principle_memory_receipt(root, memory, recorded_at="2027-04-12T13:00:00+00:00")
            self.assertEqual(len(first["events"]), 1)
            self.assertEqual(len(row["events"]), 2)
            self.assertEqual(len(row2["events"]), 2)
            self.assertEqual(validate_principle_memory_ledger(row2), [])
            public = public_principle_memory_state(root, handoff["contract_id"])
            self.assertEqual(public["status"], HANDOFF_STATUS)
            self.assertTrue(public["principle_update_allowed"])
            self.assertFalse(public["automatic_memory_write_authorized"])
            self.assertFalse(public["persistent_memory_write_completed"])
            text = json.dumps(public)
            self.assertNotIn("pi:private-principle-memory-approval", text)
            self.assertNotIn("external_authority_ref", text)

    def test_tamper_and_global_authority_leak_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff = self.dead_end_handoff(root)
            auth = build_principle_memory_authorization(principle_handoff=handoff, external_authority_ref="pi:approve", authorized_at="2027-04-12T12:00:00+00:00")
            bad = copy.deepcopy(auth); bad["automatic_memory_write_authorized"] = True
            self.assertFalse(validate_principle_memory_authorization(bad))
            publish_principle_memory_receipt(root, auth, recorded_at="2027-04-12T12:00:00+00:00")
            path = root / "scientific-contract-p0-principle-memory" / f"{handoff['contract_id']}.json"
            row = json.loads(path.read_text()); row["authority"]["principle"] = True
            self.assertIn("principle-memory-ledger-global-authority-leak", validate_principle_memory_ledger(row))


if __name__ == "__main__":
    unittest.main()
