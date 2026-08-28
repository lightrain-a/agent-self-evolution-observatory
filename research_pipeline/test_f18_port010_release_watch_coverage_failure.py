from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "research_pipeline" / "f18_port010_release_watch_coverage_failure_20260828.json"
PRE = ROOT / "generated" / "port010-vwe-firstparty-preanalysis-proposal.json"
PLAN = ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"


def find_dataset_url(value):
    if isinstance(value, dict):
        if isinstance(value.get("dataset_url"), str):
            return value["dataset_url"]
        for child in value.values():
            found = find_dataset_url(child)
            if found:
                return found
    if isinstance(value, list):
        for child in value:
            found = find_dataset_url(child)
            if found:
                return found
    return ""


class F18Port010ReleaseWatchCoverageFailureTest(unittest.TestCase):
    def test_asset_matches_current_uncovered_first_party_dataset_surface(self) -> None:
        asset = json.loads(ASSET.read_text(encoding="utf-8"))
        pre = json.loads(PRE.read_text(encoding="utf-8"))
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        row = next(
            x for x in plan["entries"]
            if x.get("candidate_id") == "PORT-010"
            and x.get("title") == "Complex-description boundary in end-to-end 3D world construction"
        )
        dataset_url = find_dataset_url(pre)
        watch_urls = [x.get("url") for x in row["release_watch_contract"]["targets"]]
        self.assertTrue(dataset_url)
        self.assertEqual(asset["source_state"]["uncovered_first_party_dataset_url"], dataset_url)
        self.assertNotIn(dataset_url, watch_urls)
        self.assertFalse(asset["observation"]["dataset_endpoint_present_in_release_watch_contract"])
        self.assertFalse(asset["observation"]["immutable_dataset_revision_verified_in_this_audit"])
        self.assertFalse(asset["observation"]["qualifying_per_case_outcome_artifact_verified_in_this_audit"])
        self.assertEqual(row["release_change_adjudication"]["remaining_reopen_components"], ["per_case_outcomes"])
        self.assertFalse(row["release_change_adjudication"]["offline_replay_tier_authorized"])
        self.assertFalse(asset["scientific_authority"])
        self.assertTrue(asset["authority"])
        self.assertFalse(any(asset["authority"].values()))


if __name__ == "__main__":
    unittest.main()
