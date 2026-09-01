from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OBJECT_ID = "AGENT-CONSTRAINT-EXTERNALITY-20260831"
ADDENDUM = (
    GENERATED
    / "agent-constraint-externality-qwen-model-prereg-addendum-a0-20260901.json"
)
MANIFEST = (
    GENERATED
    / "agent-constraint-externality-qwen-model-prereg-addendum-a0-manifest-20260901.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AgentConstraintExternalityQwenModelPreregTest(unittest.TestCase):
    def setUp(self) -> None:
        self.addendum = load(ADDENDUM)
        self.manifest = load(MANIFEST)

    def test_addendum_was_created_at_zero_outcome_boundary(self) -> None:
        self.assertEqual(self.addendum["object_id"], OBJECT_ID)
        self.assertEqual(
            self.addendum["status"], "QWEN_MODEL_PREREG_ADDENDUM_A0_PASS"
        )
        boundary = self.addendum["change_boundary"]
        self.assertEqual(boundary["scientific_outcomes_at_switch"], 0)
        self.assertEqual(boundary["scientific_provider_calls_at_switch"], 0)
        self.assertFalse(boundary["f0_executed_at_switch"])
        self.assertFalse(boundary["outcome_driven_change"])
        self.assertTrue(all(value == 0 for value in boundary["validated_counters"].values()))

    def test_exactly_one_qwen_candidate_is_frozen(self) -> None:
        candidate = self.addendum["primary_candidate"]
        self.assertEqual(candidate["requested_model"], "qwen3.7-flash-2026-07-15")
        self.assertEqual(candidate["allowed_alias"], "qwen3.7-flash")
        self.assertEqual(candidate["candidate_count"], 1)
        self.assertEqual(candidate["fallback_candidates"], [])
        self.assertEqual(
            candidate["alias_policy"]["backend_revision_drift_disposition"],
            "STOP_AND_ADJUDICATE",
        )
        disposition = self.addendum["capability_dispositions"]
        self.assertFalse(disposition["automatic_fallback"])

    def test_switch_reasons_are_not_outcome_driven(self) -> None:
        reasons = set(self.addendum["selection_reasons"])
        self.assertIn("FUNCTION_CALLING_SUPPORT", reasons)
        self.assertIn("LOW_INFERENCE_COST", reasons)
        self.assertIn(
            "SUITABLE_FIRST_STAGE_NON_FRONTIER_CAPABILITY_TIER", reasons
        )
        self.assertEqual(
            self.addendum["forbidden_selection_reason"],
            "EXPECTED_TO_PRODUCE_MORE_EXTERNALITY",
        )

    def test_corrected_budgets_are_separate(self) -> None:
        budget = self.addendum["budget_correction"]
        self.assertEqual(budget["capability_agent_episodes"], 8)
        self.assertEqual(budget["f0_source_agent_episodes"], 8)
        self.assertEqual(budget["f0_probe_agent_episode_min"], 108)
        self.assertEqual(budget["f0_probe_agent_episode_max"], 144)
        self.assertEqual(budget["agent_episode_total_max"], 160)
        self.assertEqual(budget["repair_generation_provider_request_cap"], 8)
        self.assertFalse(budget["probe_144_is_total_f0_cap"])
        self.assertEqual(len(budget["count_separately"]), 4)

    def test_only_m1_mock_authority_is_open(self) -> None:
        authority = self.addendum["authority"]
        self.assertTrue(authority["m1_mock_qualification"])
        for name in (
            "real_provider_call", "capability_calibration", "f0", "toolsandbox",
            "appworld_ul", "p1", "second_model", "method", "paper_claim",
        ):
            self.assertFalse(authority[name], name)

    def test_provider_contract_is_safe(self) -> None:
        provider = self.addendum["provider_contract"]
        self.assertEqual(provider["base_url"], "https://api.aa.com.cn/api/v1")
        self.assertTrue(provider["custom_function_tools_supported"])
        self.assertTrue(provider["response_model_field_is_resolved_identity_source"])
        self.assertFalse(provider["secrets_in_artifacts"])
        serialized = json.dumps(self.addendum, sort_keys=True)
        self.assertNotIn("Bearer ", serialized)
        self.assertNotIn("sk-", serialized)

    def test_manifest_is_content_addressed(self) -> None:
        relative = str(ADDENDUM.relative_to(ROOT))
        metadata = self.manifest["files"][relative]
        self.assertEqual(metadata["sha256"], sha256(ADDENDUM))
        self.assertEqual(metadata["bytes"], ADDENDUM.stat().st_size)
        self.assertEqual(self.manifest["scientific_outcomes_observed"], 0)
        self.assertEqual(self.manifest["provider_calls"], 0)


if __name__ == "__main__":
    unittest.main()
