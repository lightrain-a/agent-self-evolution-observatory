from __future__ import annotations

import json
import unittest
from pathlib import Path

R34 = Path("generated/d2-failure-memory-provenance-r34-external-substrate-release-recheck.json")


class TestExternalSubstrateReleaseRecheckR34(unittest.TestCase):
    def test_priority_and_execution_boundary(self) -> None:
        d = json.loads(R34.read_text(encoding="utf-8"))
        self.assertEqual(d["status"], "NO_EXTERNAL_REPLACEMENT_EXECUTION_SURFACE_UNBLOCKED_SMA_REMAINS_PRIORITY1")
        self.assertFalse(d["adjudication"]["replacement_execution_ready_now"])
        self.assertTrue(d["adjudication"]["SMA_remains_priority1"])
        self.assertTrue(d["adjudication"]["IBM_remains_priority2"])
        self.assertTrue(d["adjudication"]["MutMem_remains_scientific_stop_for_B1_source_provenance"])
        self.assertTrue(all(v is False for v in d["authority"].values()))

    def test_sma_and_ibm_are_support_blocked_not_scientific_negative(self) -> None:
        d = json.loads(R34.read_text(encoding="utf-8"))
        by_name = {x["name"]: x for x in d["candidates"]}
        sma = by_name["Spatial Memory Agent (SMA)"]
        ibm = by_name["Trajectory-Informed Memory Generation for Self-Improving Agent Systems (IBM Research)"]
        self.assertFalse(sma["code_release_unblocked"])
        self.assertFalse(sma["exact_information_l2_ready"])
        self.assertFalse(ibm["code_release_unblocked"])
        self.assertFalse(ibm["exact_information_l2_ready"])
        self.assertFalse(d["adjudication"]["absence_of_public_release_is_scientific_negative"])

    def test_construct_standard_not_relaxed_after_webarena_failure(self) -> None:
        d = json.loads(R34.read_text(encoding="utf-8"))
        self.assertTrue(d["adjudication"]["WebArena_support_failure_does_not_relax_construct_match"])
        self.assertTrue(d["adjudication"]["third_party_or_platform_code_does_not_substitute_for_first_party_paper_artifact"])
        self.assertEqual(d["reopen_condition"]["preferred_trigger"], "SMA_FIRST_PARTY_CODE_RELEASE")
        self.assertFalse(d["reopen_condition"]["same_asset_R33_27_unit_fallback_automatically_authorized"])

    def test_public_receipt_has_no_private_paths(self) -> None:
        text = R34.read_text(encoding="utf-8")
        for needle in ["/data/", "/home/", "wyt@", "192.168.", "source_message_ref", "source_message_sha256"]:
            self.assertNotIn(needle, text)


if __name__ == "__main__":
    unittest.main()
