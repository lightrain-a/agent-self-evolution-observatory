from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "generated" / "constraint-integration-executability-preflight-20260828.json"
MANIFEST = ROOT / "generated" / "lego-bench-aligned-scene-json-manifest-20260828.json"
PROPOSAL = ROOT / "generated" / "constraint-integration-cross-substrate-proposal-20260828.json"
PLAN = ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"

EXPECTED_PREFLIGHT_SHA256 = "15cf610915f3d3cd1e144f81207ac240517d0e5969418dd8e13e86b719d49f13"
EXPECTED_MANIFEST_SHA256 = "ba12ccc4a4e18520e9aad192c87e47bdc90b2c3bb8ee05a2ddde07de3aa226f0"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ConstraintIntegrationExecutabilityPreflightTest(unittest.TestCase):
    def setUp(self) -> None:
        self.preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.proposal = json.loads(PROPOSAL.read_text(encoding="utf-8"))
        self.plan = json.loads(PLAN.read_text(encoding="utf-8"))

    def test_preflight_and_manifest_are_content_addressed(self) -> None:
        self.assertEqual(sha256_file(PREFLIGHT), EXPECTED_PREFLIGHT_SHA256)
        self.assertEqual(sha256_file(MANIFEST), EXPECTED_MANIFEST_SHA256)
        asset = self.preflight["aligned_scene_asset"]
        self.assertEqual(asset["manifest_sha256"], EXPECTED_MANIFEST_SHA256)
        self.assertEqual(asset["scene_hash_root"], self.manifest["scene_hash_root"])
        self.assertEqual(asset["full_data_sha256"], self.manifest["full_data_sha256"])
        self.assertEqual(asset["scene_json_count"], self.manifest["scene_count"])

    def test_aligned_scene_asset_is_outcome_blind_and_zero_authority(self) -> None:
        self.assertEqual(self.manifest["scene_count"], 130)
        self.assertTrue(self.manifest["all_index_query_pairs_match_full_data"])
        self.assertFalse(self.manifest["outcome_fields_inspected"])
        self.assertFalse(self.manifest["scientific_authority"])
        asset = self.preflight["aligned_scene_asset"]
        self.assertTrue(asset["scene_json_materialized"])
        self.assertFalse(asset["per_case_evaluator_outcomes_read"])
        self.assertFalse(asset["scientific_authority"])

    def test_local_evaluator_is_possible_but_not_runtime_ready(self) -> None:
        evaluator = self.preflight["lego_eval"]
        self.assertTrue(evaluator["zero_external_provider_possible_in_principle"])
        self.assertFalse(evaluator["zero_external_provider_runtime_ready_now"])
        self.assertTrue(evaluator["constraint_evaluation_is_sequential"])
        self.assertTrue(evaluator["previous_constraint_outputs_enter_later_tool_selection"])
        self.assertEqual(evaluator["measurement_coupling_risk"], "REAL_AND_PRE_REGISTERED")
        model = self.preflight["local_open_model_candidate"]
        self.assertTrue(model["materialized"])
        self.assertTrue(model["does_not_authorize_gpu"])
        runtime = self.preflight["runtime_preflight"]
        self.assertEqual(runtime["status"], "NOT_RUNTIME_READY")
        self.assertFalse(runtime["candidate_env_capabilities"]["vllm_available"])
        self.assertFalse(runtime["candidate_env_capabilities"]["ai2thor_available"])
        self.assertFalse(runtime["objathor_holodeck_assets"]["materialized_on_checked_paths"])
        self.assertFalse(runtime["lego_object_images"]["materialized_on_checked_paths"])

    def test_reference_generator_baselines_are_not_zero_provider_source_faithful(self) -> None:
        baselines = self.preflight["published_generator_baselines"]
        self.assertEqual({x["name"] for x in baselines}, {"Holodeck", "LayoutGPT", "I-Design", "LayoutVLM"})
        for row in baselines:
            self.assertEqual(len(row["revision"]), 40)
            self.assertFalse(row["zero_provider_source_faithful_execution"])
            self.assertFalse(row["local_model_substitution_is_same_baseline"])
        released = self.preflight["released_baseline_outcome_status"]
        self.assertFalse(released["per_case_generated_scene_bundle_identified_in_inspected_official_lego_surfaces"])

    def test_execution_ladder_is_fail_closed(self) -> None:
        self.assertEqual(self.preflight["generator_admission"], "PENDING")
        self.assertFalse(self.preflight["scientific_authority"])
        self.assertFalse(self.preflight["execution_authority"])
        self.assertFalse(self.preflight["provider_authority"])
        self.assertFalse(self.preflight["gpu_authority"])
        self.assertTrue(self.preflight["authority"])
        self.assertFalse(any(self.preflight["authority"].values()))
        stages = {row["stage"]: row for row in self.preflight["execution_ladder"]}
        self.assertEqual(stages["A"]["status"], "COMPLETED_ZERO_AUTHORITY")
        self.assertIn("BLOCKED", stages["B"]["status"])
        self.assertEqual(stages["C"]["status"], "NOT_AUTHORIZED")
        self.assertEqual(stages["D"]["status"], "NOT_AUTHORIZED_PROVIDER_BOUND")

    def test_port010_remains_hold_and_proposal_remains_noncanonical(self) -> None:
        self.assertIsNone(self.proposal["canonical_candidate_id"])
        self.assertEqual(self.proposal["generator_admission"], "PENDING")
        rows = [
            row for row in self.plan.get("entries") or []
            if row.get("candidate_id") == "PORT-010"
            and row.get("title") == "Complex-description boundary in end-to-end 3D world construction"
        ]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["status"], "HOLD_EVIDENCE_REVIEW_BLOCKED")
        self.assertEqual((row.get("evidence_review") or {}).get("verdict"), "BLOCK_BAKE_IN")
        adjudication = row["release_change_adjudication"]
        self.assertEqual(adjudication["remaining_reopen_components"], ["per_case_outcomes"])
        self.assertFalse(adjudication["offline_replay_tier_authorized"])
        self.assertFalse(adjudication["provider_authority"])
        self.assertFalse(adjudication["gpu_authority"])
        self.assertFalse(adjudication["scientific_execution_authority"])


if __name__ == "__main__":
    unittest.main()
