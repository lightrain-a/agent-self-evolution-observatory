from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "generated" / "agent-safety-g1-mcta-length-structure-placebo-contract-20260904.json"


class MCTAPlaceboContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_execution_authority_is_closed(self) -> None:
        self.assertTrue(all(value is False for value in self.contract["authority"].values()))

    def test_exact_bytes_and_subset_must_be_frozen_before_p1(self) -> None:
        timing = self.contract["construction_timing"]
        self.assertTrue(timing["exact_placebo_bytes_must_be_frozen_before_first_p1_provider_call"])
        self.assertTrue(timing["subset_manifest_must_be_frozen_before_first_p1_provider_call"])
        self.assertTrue(timing["post_p1_outcome_placebo_construction_forbidden"])

    def test_placebo_matches_token_length_and_awm_structure(self) -> None:
        matching = self.contract["matching_contract"]
        self.assertIn("per-unit tokenizer length", matching["match_updated_arm_on"])
        self.assertIn("AWM wrapper and section boundaries", matching["match_updated_arm_on"])
        self.assertIn("exactly the same token count", matching["token_length_rule"])

    def test_neutral_content_excludes_executable_workflow_semantics(self) -> None:
        neutral = self.contract["neutral_content_contract"]
        forbidden = " ".join(neutral["forbidden_content"]).lower()
        self.assertIn("imperative browser-action sequences", forbidden)
        self.assertIn("urls", forbidden)
        self.assertFalse(neutral["manual_edit_after_p1_outcome"])

    def test_subset_is_hash_selected_before_outcomes(self) -> None:
        subset = self.contract["mechanism_subset"]
        self.assertEqual(subset["unit_count"], 12)
        self.assertIn("sha256", subset["selection"])
        self.assertFalse(subset["replacement_after_outcome"])

    def test_workload_and_trigger(self) -> None:
        execution = self.contract["execution"]
        self.assertEqual(execution["agent_episode_count"], 72)
        self.assertIn("only if", execution["trigger"].lower())
        self.assertFalse(execution["shared_t0_reexecution"])


if __name__ == "__main__":
    unittest.main()
