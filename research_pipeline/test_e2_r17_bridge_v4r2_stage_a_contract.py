from __future__ import annotations

import unittest
from pathlib import Path

from scripts.freeze_e2_r17_bridge_v4r2_stage_a_contract import build_contract

ROOT = Path(__file__).resolve().parents[1]


class BridgeV4R2StageAContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_contract()

    def test_contract_is_zero_authority(self) -> None:
        self.assertEqual(self.contract["status"], "FROZEN_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_SUPPORT")
        self.assertFalse(any(self.contract["authority"].values()))

    def test_exact_screen_search_geometry(self) -> None:
        search = self.contract["search"]
        self.assertEqual(len(search["stream_ids"]), 6)
        self.assertEqual(len(search["task_ids"]), 48)
        self.assertEqual(len(search["unit_ids"]), 384)
        self.assertEqual(len(set(search["unit_ids"])), 384)
        self.assertEqual(search["exact_k"], 8)

    def test_stage_a_support_gate_has_no_replacement(self) -> None:
        gate = self.contract["support_gate"]
        self.assertEqual(gate["mixed_pools_per_stream_minimum"], 4)
        self.assertTrue(gate["all_six_streams_must_pass"])
        self.assertFalse(gate["stream_task_or_k_replacement"])
        self.assertTrue(gate["inspection_after_all_384_search_units"])

    def test_stage_a_budget_excludes_updater_and_heldout(self) -> None:
        budget = self.contract["budget"]
        self.assertEqual(budget["search_provider_call_ceiling"], 3840)
        self.assertEqual(budget["per_search_unit_call_ceiling"], 10)
        self.assertEqual(budget["updater_call_ceiling"], 0)
        self.assertEqual(budget["heldout_actor_call_ceiling"], 0)

    def test_runner_source_has_no_state_generation_or_heldout_path(self) -> None:
        source = (ROOT / "research_pipeline/e2_r17_bridge_v4r2_stage_a_runtime.py").read_text(encoding="utf-8")
        self.assertNotIn("run_bridge_free_update", source)
        self.assertNotIn("materialize_actor_visible_state", source)
        self.assertNotIn("stage_heldout", source)
        self.assertIn('"updater_calls":0', source)
        self.assertIn('"heldout_actor_calls":0', source)

    def test_point_of_use_binds_exact_runner_runtime_and_authorization_scope(self) -> None:
        source = (ROOT / "research_pipeline/e2_r17_bridge_v4r2_stage_a_runtime.py").read_text(encoding="utf-8")
        self.assertIn("Path(sys.executable).resolve()==runtime_python.resolve()", source)
        for witness in (
            'scope.get("allowed_task_ids")==c["search"]["task_ids"]',
            'int(scope.get("exact_k",-1))==8',
            'scope.get("identity_artifact_sha256")==c["model_identity"]["sha256"]',
            'scope.get("required_skill_pre_sha256")==c["initial_skill"]["sha256"]',
            'int(scope.get("max_turns",-1))==c["actor"]["max_turns"]',
            'int(scope.get("max_output_tokens",-1))==c["actor"]["max_output_tokens"]',
            'scope.get("automatic_retry") is False',
            'scope.get("run_root")==c["run_root"]',
            'pb.get("required") is True',
        ):
            self.assertIn(witness, source)


if __name__ == "__main__":
    unittest.main()
