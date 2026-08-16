from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.paper_first_fresh_f0_authority import (
    AUTHORITY_TYPE,
    CANDIDATE_ID,
    CONTRACT_VERSION,
    EXPECTED_REPAIR_SHA256,
    EXPECTED_RUNTIME_SHA256,
    load_human_authority,
    require_bounded_f0_execution_authority,
)


class FreshF0AuthorityTest(unittest.TestCase):
    def payload(self) -> dict:
        return {
            "authority_type": AUTHORITY_TYPE,
            "decision": "approve",
            "reviewed_by": "human-user",
            "reviewed_at": "2026-08-17T03:36:00+08:00",
            "source_message_ref": "chat-message:test-fresh-f0",
            "source_message_sha256": hashlib.sha256("继续，你把其他的idea继续推进吧".encode("utf-8")).hexdigest(),
            "candidate_id": CANDIDATE_ID,
            "contract_version": CONTRACT_VERSION,
            "runtime_sha256": EXPECTED_RUNTIME_SHA256,
            "operationalization_repair_sha256": EXPECTED_REPAIR_SHA256,
            "bounded_f0_execution_authorized": True,
            "gpu_lease_authorized": True,
            "single_attempt": True,
            "problem_gate_authorized": False,
            "paper_design_authorized": False,
            "method_authorized": False,
            "p0_authorized": False,
            "full_experiment_authorized": False,
        }

    def write_external(self, payload: dict) -> Path:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        path = Path(td.name) / "authority.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def test_missing_authority_fails_closed(self) -> None:
        authority = load_human_authority("")
        self.assertFalse(authority["bounded_f0_execution_authorized"])
        self.assertFalse(authority["gpu_lease_authorized"])
        with self.assertRaisesRegex(RuntimeError, "valid external human execution authority"):
            require_bounded_f0_execution_authority(authority=authority)

    def test_valid_external_permit_authorizes_only_bounded_f0_and_gpu_lease(self) -> None:
        authority = load_human_authority(self.write_external(self.payload()))
        self.assertEqual([], authority["errors"])
        self.assertTrue(authority["bounded_f0_execution_authorized"])
        self.assertTrue(authority["gpu_lease_authorized"])
        self.assertTrue(authority["single_attempt"])
        for key in (
            "problem_gate_authorized",
            "paper_design_authorized",
            "method_authorized",
            "p0_authorized",
            "full_experiment_authorized",
        ):
            self.assertFalse(authority[key])
        self.assertIs(authority, require_bounded_f0_execution_authority(authority=authority))

    def test_runtime_binding_mismatch_fails_closed(self) -> None:
        payload = self.payload()
        payload["runtime_sha256"] = "0" * 64
        authority = load_human_authority(self.write_external(payload))
        self.assertIn("runtime-sha256-mismatch", authority["errors"])
        self.assertFalse(authority["bounded_f0_execution_authorized"])

    def test_downstream_scope_expansion_invalidates_permit(self) -> None:
        payload = self.payload()
        payload["method_authorized"] = True
        authority = load_human_authority(self.write_external(payload))
        self.assertIn("forbidden-downstream-authority:method_authorized", authority["errors"])
        self.assertFalse(authority["bounded_f0_execution_authorized"])

    def test_single_attempt_is_mandatory(self) -> None:
        payload = self.payload()
        payload["single_attempt"] = False
        authority = load_human_authority(self.write_external(payload))
        self.assertIn("single-attempt-required", authority["errors"])
        self.assertFalse(authority["bounded_f0_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
