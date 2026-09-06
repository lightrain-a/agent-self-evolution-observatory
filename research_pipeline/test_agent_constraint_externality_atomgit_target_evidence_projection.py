from __future__ import annotations

import json
import unittest
from pathlib import Path

from research_pipeline import agent_constraint_externality_atomgit_target_evidence_projection as p
from research_pipeline.agent_constraint_externality_runner_core import sha256_file, sha256_value


class TargetEvidenceProjectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.output = p.build()

    def test_selected_geometry_is_exact_six_balanced(self) -> None:
        selected = self.output["selected_family_ids"]
        self.assertEqual(3, len(selected["FG"]))
        self.assertEqual(3, len(selected["TNF"]))
        self.assertEqual(6, len(set(selected["FG"] + selected["TNF"])))
        self.assertEqual(set(selected["FG"] + selected["TNF"]), set(self.output["families"]))

    def test_zero_provider_and_authority_closed(self) -> None:
        self.assertEqual(0, self.output["provider_requests_created"])
        self.assertEqual(0, self.output["repair_writer_requests_created"])
        self.assertFalse(self.output["authority"]["repair_generation"])
        self.assertFalse(self.output["authority"]["development_repeat_qualification"])
        self.assertFalse(self.output["authority"]["rq1_rq2"])

    def test_projection_drops_auth_and_dummy_material(self) -> None:
        text = json.dumps(self.output["families"], ensure_ascii=False, sort_keys=True).lower()
        for marker in p.FORBIDDEN_MARKERS:
            self.assertNotIn(marker.lower(), text)
        for secret in ('"access_token"', '"password"', 'bearer '):
            self.assertNotIn(secret, text)
        self.assertIsNone(p.JWT_RE.search(text))
        counts = self.output["aggregate_projection_counts"]
        self.assertGreater(counts["auth_transport_dropped"], 0)
        self.assertGreater(counts["dummy_or_non_target_dropped"], 0)
        self.assertGreater(counts["kept"], 0)

    def test_every_family_has_nonempty_target_only_trace(self) -> None:
        for family_id, family in self.output["families"].items():
            trace = family["projected_tool_trajectory"]
            self.assertTrue(trace, family_id)
            self.assertEqual(sha256_value(trace), family["projected_tool_trajectory_sha256"])
            for step in trace:
                self.assertFalse(step["tool_name"].startswith("supervisor__"))
                self.assertFalse(step["tool_name"].endswith(p.AUTH_SUFFIXES))
                self.assertFalse(set(map(str.lower, step["arguments"])) & p.SECRET_KEYS)

    def test_failure_slice_is_target_failure_and_content_addressed(self) -> None:
        for family_id, family in self.output["families"].items():
            failure = family["target_failure_slice"]
            self.assertIs(False, failure["target_success"], family_id)
            self.assertIn("expected", failure)
            self.assertEqual(sha256_value(failure), family["target_failure_slice_sha256"])
            if "-FG-" in family_id:
                self.assertIn("observed_target_local_email_candidates", failure)
            else:
                self.assertIn("observed_target_local_output_candidates", failure)

    def test_projection_is_bound_to_source_closeout_and_ledger(self) -> None:
        closeout = p.verified(
            p.SOURCE_CLOSEOUT,
            "ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_PANEL_PASS_TARGET_EVIDENCE_PROJECTION_REQUIRED",
        )
        self.assertEqual(closeout["content_sha256"], self.output["source_closeout_content_sha256"])
        self.assertEqual(closeout["ledger_sha256"], self.output["source_ledger_sha256"])
        self.assertEqual(sha256_file(p.SOURCE_CLOSEOUT), self.output["source_closeout_file_sha256"])

    def test_prune_result_filters_unrelated_records(self) -> None:
        markers = ["dsfqa0-output-01-r115-"]
        value = [
            {"title": "unrelated task", "description": "ordinary"},
            {"title": "dsfqa0-output-01-r115-b", "description": "target"},
        ]
        projected = p.prune_result(value, markers)
        self.assertEqual(1, len(projected))
        self.assertEqual("dsfqa0-output-01-r115-b", projected[0]["title"])

    def test_sanitize_strips_secret_fields_and_jwt(self) -> None:
        value = {
            "access_token": "secret",
            "password": "secret2",
            "TOKEN": "semantic-token",
            "text": "eyJabcdefghijklmnopqrstuvwxyz0123456789.abc.def",
        }
        out = p.sanitize(value)
        self.assertNotIn("access_token", out)
        self.assertNotIn("password", out)
        self.assertEqual("semantic-token", out["TOKEN"])
        self.assertIn("<REDACTED_AUTH_TOKEN>", out["text"])

    def test_readiness_matches_projection_and_keeps_topology_closed(self) -> None:
        readiness = json.loads(p.READINESS.read_text(encoding="utf-8"))
        unsigned = dict(readiness); claimed = unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))
        self.assertEqual(self.output["content_sha256"], readiness["projection_content_sha256"])
        self.assertEqual(6, readiness["repair_writer_request_cap"])
        self.assertFalse(readiness["authority"]["repair_generation"])
        self.assertFalse(readiness["authority"]["development_repeat_qualification"])
        self.assertFalse(readiness["authority"]["rq1_rq2"])


if __name__ == "__main__":
    unittest.main()
