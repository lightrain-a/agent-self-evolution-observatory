from __future__ import annotations

import json
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_runner_core import sha256_value
from research_pipeline.agent_constraint_externality_sq0_build import (
    CONTRACT_OUTPUT, OUTPUT_BUNDLE, QUAL_OUTPUT, TOOL_CALL_CAP, build_cases, load_cases,
)


class SQ0TargetChallengeBuildTest(unittest.TestCase):
    def test_exactly_twelve_fresh_cases(self) -> None:
        rows = build_cases()
        self.assertEqual(len(rows), 12)
        self.assertEqual(len({r["case_id"] for r in rows}), 12)
        self.assertEqual(sum(r["kind"] == "FG_CHAIN_V1" for r in rows), 6)
        self.assertEqual(sum(r["kind"] == "TNF_CHAIN_V1" for r in rows), 6)
        self.assertTrue(all(r["case_id"].startswith("SQ0-") for r in rows))

    def test_encrypted_bundle_replays_exact_cases(self) -> None:
        self.assertTrue(OUTPUT_BUNDLE.is_file())
        self.assertEqual(sha256_value(load_cases()), sha256_value(build_cases()))

    def test_static_contract_is_development_only(self) -> None:
        c = json.loads(CONTRACT_OUTPUT.read_text())
        q = json.loads(QUAL_OUTPUT.read_text())
        for x in (c, q):
            claimed = x["content_sha256"]; unsigned = dict(x); unsigned.pop("content_sha256")
            self.assertEqual(claimed, sha256_value(unsigned))
            self.assertEqual(x["provider_requests"], 0)
            self.assertFalse(x["authority"]["f0_r1"])
            self.assertFalse(x["authority"]["probe"])
            self.assertFalse(x["authority"]["p1"])
        self.assertFalse(c["confirmatory_reuse"])
        self.assertFalse(c["old_f0_source_cases_reused"])
        self.assertEqual(c["tool_call_cap"], TOOL_CALL_CAP)

    def test_public_oracles_have_real_headroom(self) -> None:
        q = json.loads(QUAL_OUTPUT.read_text())
        self.assertEqual(q["status"], "SQ0_TARGET_CHALLENGE_V1_PUBLIC_REACHABILITY_PASS")
        self.assertEqual(q["case_count"], 12)
        self.assertLessEqual(q["max_public_tool_calls"], 18)
        self.assertGreaterEqual(q["minimum_headroom"], 6)
        self.assertFalse(q["private_fixture_ids_used"])
        self.assertTrue(all(r["target_success"] for r in q["public_oracles"]))

    def test_public_contract_does_not_publish_private_case_plaintext(self) -> None:
        text = CONTRACT_OUTPUT.read_text()
        for secretish in ["Dispatch package", "qualified-content", "RECIPIENT=", "ROUTE_KEY="]:
            self.assertNotIn(secretish, text)


if __name__ == "__main__":
    unittest.main()
