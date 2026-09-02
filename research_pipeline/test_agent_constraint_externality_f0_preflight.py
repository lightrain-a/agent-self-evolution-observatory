from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OBJECT_ID = "AGENT-CONSTRAINT-EXTERNALITY-20260831"

PATHS = {
    "capability": GENERATED / "agent-constraint-externality-capability-contract-20260831.json",
    "f0": GENERATED / "agent-constraint-externality-f0-frozen-protocol-20260831.json",
    "readiness": GENERATED / "agent-constraint-externality-f0-readiness-20260831.json",
    "manifest": GENERATED / "agent-constraint-externality-f0-preflight-manifest-20260831.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AppWorldConstraintF0PreflightTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data = {name: load(path) for name, path in PATHS.items()}

    def test_identity_and_zero_outcome_boundary(self) -> None:
        for payload in self.data.values():
            self.assertEqual(payload["object_id"], OBJECT_ID)
        for name in ("capability", "f0", "manifest"):
            self.assertEqual(
                self.data[name]["scientific_outcomes_observed"], 0
            )
            self.assertEqual(self.data[name]["gpu_runs"], 0)
        self.assertEqual(self.data["capability"]["provider_calls"], 0)
        self.assertEqual(self.data["f0"]["provider_calls"], 0)
        readiness = self.data["readiness"]
        self.assertEqual(
            self.data["manifest"]["provider_calls"],
            readiness["capability_provider_request_total"],
        )
        self.assertFalse(readiness["f0_executed"])
        self.assertEqual(readiness["f0_outcomes_observed"], 0)
        self.assertFalse(readiness["p1_authorized"])

    def test_disjoint_outcome_blind_split(self) -> None:
        capability_ids = set(self.data["capability"]["family_ids"])
        f0_ids = set(self.data["f0"]["family_ids"])
        self.assertEqual(len(capability_ids), 4)
        self.assertEqual(len(f0_ids), 8)
        self.assertFalse(capability_ids & f0_ids)
        self.assertEqual(len(capability_ids | f0_ids), 12)
        self.assertTrue(self.data["f0"]["split_is_disjoint_from_capability"])

    def test_model_selection_is_frozen_before_f0(self) -> None:
        capability = self.data["capability"]
        self.assertEqual(
            capability["model_selection_order"],
            ["qwen3.7-flash-2026-07-15"],
        )
        self.assertEqual(capability["maximum_candidate_count"], 1)
        self.assertEqual(capability["maximum_episode_envelope"], 8)
        self.assertEqual(
            capability["selection_rule"],
            "ONLY_QWEN_CANDIDATE_MUST_QUALIFY_OR_STOP",
        )
        self.assertFalse(capability["automatic_fallback"])
        self.assertEqual(capability["execution"]["provider_max_retries"], 0)
        self.assertFalse(capability["execution"]["application_retry"])
        self.assertTrue(capability["execution"]["no_episode_replacement"])

    def test_f0_is_exactly_once_and_within_requested_envelope(self) -> None:
        f0 = self.data["f0"]
        probe = f0["probe_phase"]
        self.assertEqual(probe["arms"], ["INDEPENDENT", "LOW", "HIGH"])
        self.assertEqual(probe["branches"], ["NO_UPDATE", "UPDATE"])
        self.assertEqual(probe["seeds"], [1201, 1202, 1203])
        self.assertEqual(probe["planned_episode_envelope"], 144)
        budgets = f0["budgets"]
        self.assertEqual(budgets["capability_agent_episodes"], 8)
        self.assertEqual(budgets["f0_source_agent_episodes"], 8)
        self.assertEqual(budgets["f0_probe_agent_episode_min"], 108)
        self.assertEqual(budgets["f0_probe_agent_episode_max"], 144)
        self.assertEqual(budgets["agent_episode_total_max"], 160)
        self.assertEqual(budgets["repair_generation_provider_request_cap"], 8)
        exactly_once = f0["exactly_once"]
        self.assertEqual(exactly_once["provider_max_retries"], 0)
        self.assertFalse(exactly_once["application_retry"])
        self.assertTrue(exactly_once["append_only_ledger"])
        self.assertTrue(exactly_once["duplicate_key_is_fatal"])
        self.assertTrue(exactly_once["retry_or_replacement_forbidden"])
        self.assertFalse(probe["partial_effects_readable_during_execution"])

    def test_repair_is_target_only_and_content_addressed(self) -> None:
        source = self.data["f0"]["source_phase"]
        forbidden = set(source["forbidden_updater_input"])
        self.assertIn("NON_TARGET_OUTCOMES", forbidden)
        self.assertIn("TOPOLOGY_LABEL", forbidden)
        self.assertIn("F0_EFFECT", forbidden)
        self.assertFalse(source["human_edit_after_generation"])
        self.assertIn("sha256", source["freeze_fields"])
        self.assertIn("raw_bytes", source["freeze_fields"])
        self.assertIn("normalized_bytes", source["freeze_fields"])
        self.assertIn("word_count", source["freeze_fields"])
        self.assertIn("source_trajectory_sha256", source["freeze_fields"])
        self.assertEqual(source["minimum_eligible_repair_families"], 6)

    def test_post_f0_expansion_remains_closed(self) -> None:
        authority = self.data["f0"]["post_f0_authority"]
        self.assertEqual(authority["toolsandbox_only_after"], "F0_MECHANISM_SUPPORT")
        self.assertEqual(
            authority["appworld_ul_only_after"],
            "F0_AND_TOOLSANDBOX_MECHANISM_SUPPORT",
        )
        self.assertFalse(authority["full_p1"])
        self.assertFalse(authority["workarena"])
        self.assertFalse(authority["multi_backbone"])
        self.assertFalse(authority["paper_claim"])

    def test_provider_summary_has_no_secret_and_readiness_is_honest(self) -> None:
        readiness = self.data["readiness"]
        provider = readiness["provider"]
        self.assertFalse(provider["api_key_in_output"])
        serialized = json.dumps(readiness, sort_keys=True)
        self.assertNotIn("Bearer ", serialized)
        self.assertEqual(readiness["execution_override"]["max_retries"], 0)
        self.assertTrue(readiness["model_prereg_addendum_a0_pass"])
        self.assertTrue(readiness["m1_runner_qualification_pass"])
        if readiness.get("capability_model_selection_state") == "SEARCH_ACTIVE_QWEN_CEILING_DEEPSEEK_FLOOR_GLM52_CEILING_MIMO25_CEILING_MIMO25PRO_NEXT":
            self.assertEqual(
                readiness["status"],
                "CAPABILITY_BACKBONE_SEARCH_CONTINUE_MIMO25PRO_NEXT",
            )
            self.assertEqual(
                readiness["next_authorized_action"],
                "FREEZE_AND_RUN_CODINGPLAN_MIMO25PRO_CAPABILITY_B3",
            )
            self.assertEqual(readiness["mimo25_capability_result_status"], "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP")
            self.assertEqual(readiness["mimo25_scientific_model_round_count"], 69)
            self.assertEqual(readiness["mimo25_account_window_request_delta"], 69)
            self.assertEqual(readiness["mimo25_tool_loop_completion_rate"], 1.0)
            self.assertEqual(readiness["mimo25_target_success_rate"], 1.0)
            self.assertEqual(readiness["backbone_search_b3_remaining_frozen_order"], ["mimo-v2.5-pro"])
            self.assertEqual(
                readiness["backbone_search_b3_next_candidate"],
                {"model_id": "mimo-v2.5-pro", "profile": "AtomGit-mimo-v2.5-pro"},
            )
            self.assertFalse(readiness["eligible_backbone_selected"])
            self.assertFalse(readiness["f0_authorized"])
        elif readiness.get("capability_model_selection_state") == "SEARCH_ACTIVE_QWEN_CEILING_DEEPSEEK_FLOOR_GLM52_CEILING_MIMO25_NEXT":
            self.assertEqual(
                readiness["status"],
                "CAPABILITY_BACKBONE_SEARCH_CONTINUE_MIMO25_NEXT",
            )
            self.assertEqual(
                readiness["next_authorized_action"],
                "FREEZE_AND_RUN_CODINGPLAN_MIMO25_CAPABILITY_B2",
            )
            self.assertEqual(readiness["glm52_capability_result_status"], "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP")
            self.assertEqual(readiness["glm52_scientific_model_round_count"], 77)
            self.assertEqual(readiness["glm52_account_window_request_delta"], 77)
            self.assertEqual(readiness["glm52_tool_loop_completion_rate"], 1.0)
            self.assertEqual(readiness["glm52_target_success_rate"], 1.0)
            self.assertEqual(
                readiness["backbone_search_b2_remaining_frozen_order"],
                ["mimo-v2.5", "mimo-v2.5-pro"],
            )
            self.assertEqual(
                readiness["backbone_search_b2_next_candidate"],
                {"model_id": "mimo-v2.5", "profile": "AtomGit-mimo-v2.5"},
            )
            self.assertFalse(readiness["eligible_backbone_selected"])
            self.assertFalse(readiness["f0_authorized"])
        elif readiness.get("capability_model_selection_state") == "SEARCH_ACTIVE_QWEN_CEILING_DEEPSEEK_FLOOR_GLM52_NEXT":
            self.assertEqual(
                readiness["status"],
                "CAPABILITY_BACKBONE_SEARCH_CONTINUE_GLM52_NEXT",
            )
            self.assertEqual(
                readiness["next_authorized_action"],
                "FREEZE_AND_RUN_CODINGPLAN_GLM52_CAPABILITY_B1",
            )
            self.assertEqual(
                readiness["direct_api_capability_result_status"],
                "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP",
            )
            self.assertEqual(
                readiness["codingplan_capability_result_status"],
                "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP",
            )
            self.assertEqual(
                readiness["deepseek_capability_result_status"],
                "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP",
            )
            self.assertEqual(readiness["deepseek_scientific_model_round_count"], 72)
            self.assertEqual(readiness["deepseek_account_window_request_delta"], 72)
            self.assertEqual(readiness["deepseek_tool_loop_completion_rate"], 0.625)
            self.assertEqual(readiness["deepseek_target_success_rate"], 0.875)
            self.assertEqual(
                readiness["backbone_search_remaining_frozen_order"],
                ["GLM-5.2", "mimo-v2.5", "mimo-v2.5-pro"],
            )
            self.assertEqual(
                readiness["backbone_search_next_candidate"],
                {"model_id": "GLM-5.2", "profile": "AtomGit-GLM-5.2"},
            )
            self.assertFalse(readiness["eligible_backbone_selected"])
            self.assertFalse(readiness["f0_authorized"])
        elif readiness.get("capability_model_selection_state") == "NO_ELIGIBLE_BACKBONE_BOTH_VALID_CANDIDATES_CEILING":
            self.assertEqual(
                readiness["status"],
                "CAPABILITY_MODEL_SELECTION_NO_ELIGIBLE_BACKBONE_ALL_CEILING_STOP",
            )
            self.assertEqual(
                readiness["next_authorized_action"],
                "STOP_AWAIT_HUMAN_BACKBONE_SELECTION",
            )
            self.assertEqual(
                readiness["direct_api_capability_result_status"],
                "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP",
            )
            self.assertEqual(
                readiness["codingplan_capability_result_status"],
                "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP",
            )
            self.assertFalse(readiness["eligible_backbone_selected"])
            self.assertEqual(readiness["codingplan_scientific_model_round_count"], 69)
            self.assertEqual(readiness["codingplan_account_window_request_delta"], 70)
            self.assertEqual(readiness["codingplan_account_level_unattributed_request_count"], 1)
            self.assertFalse(readiness["f0_authorized"])
        elif readiness.get("capability_result_status") == "CAPABILITY_CALIBRATION_PASS":
            self.assertEqual(
                readiness["status"],
                "CAPABILITY_CALIBRATION_PASS_F0_AUTHORIZATION_REQUIRED",
            )
            self.assertEqual(
                readiness["next_authorized_action"],
                "STOP_AWAIT_HUMAN_F0_AUTHORIZATION",
            )
            self.assertFalse(readiness["f0_authorized"])
        elif readiness.get("capability_result_status"):
            self.assertEqual(
                readiness["status"], readiness["capability_result_status"]
            )
            self.assertEqual(
                readiness["next_authorized_action"],
                "STOP_AWAIT_HUMAN_ADJUDICATION",
            )
            self.assertFalse(readiness["f0_authorized"])
        elif readiness.get("capability_r3_partial_void_substrate_filesystem_filename_invalid"):
            self.assertTrue(readiness["capability_prior_results_void_substrate_invalid"])
            self.assertTrue(readiness["capability_substrate_v4_recovery_qualification_pass"])
            self.assertTrue(readiness["capability_r5_partial_authorized"])
            self.assertEqual(readiness["capability_preserved_fg_measurements"], 4)
            self.assertEqual(
                readiness["status"],
                "CAPABILITY_SUBSTRATE_V4_PARTIAL_REQUALIFICATION_READY",
            )
            self.assertEqual(
                readiness["next_authorized_action"],
                "RUN_QWEN37PLUS_CAPABILITY_R5_PARTIAL_TNF_ONLY",
            )
            self.assertEqual(readiness["capability_valid_measurements"], 0)
            self.assertIsNone(readiness["capability_result_artifact"])
            self.assertFalse(readiness["f0_authorized"])
        elif readiness.get("capability_r2_void_substrate_discoverability_invalid"):
            self.assertTrue(readiness["capability_prior_results_void_substrate_invalid"])
            self.assertTrue(readiness["capability_substrate_v2_recovery_qualification_pass"])
            self.assertTrue(readiness["capability_r3_authorized"])
            self.assertTrue(readiness["capability_r3_partial_authorized"])
            self.assertTrue(readiness["capability_r3_full_contract_superseded"])
            self.assertEqual(
                readiness["status"],
                "CAPABILITY_SUBSTRATE_V2_PARTIAL_REQUALIFICATION_READY",
            )
            self.assertEqual(
                readiness["next_authorized_action"],
                "RUN_QWEN37PLUS_CAPABILITY_R3_PARTIAL_TNF_ONLY",
            )
            self.assertFalse(readiness["f0_authorized"])
        elif readiness.get("capability_prior_results_void_substrate_invalid"):
            self.assertTrue(readiness["capability_substrate_recovery_qualification_pass"])
            self.assertTrue(readiness["capability_r2_authorized"])
            self.assertEqual(readiness["status"], "CAPABILITY_SUBSTRATE_REQUALIFICATION_READY")
            self.assertEqual(readiness["next_authorized_action"], "RUN_QWEN37PLUS_CAPABILITY_R2")
            self.assertFalse(readiness["f0_authorized"])
        elif readiness["provider_credential_present"]:
            self.assertEqual(
                readiness["status"], "CAPABILITY_CALIBRATION_READY"
            )
            self.assertEqual(
                readiness["next_authorized_action"],
                "RUN_QWEN_CAPABILITY_CALIBRATION",
            )
        else:
            self.assertEqual(
                readiness["status"], "QWEN_PROVIDER_CONFIGURATION_REQUIRED"
            )
            self.assertEqual(
                readiness["next_authorized_action"],
                "CONFIGURE_QWEN_PROVIDER_CREDENTIAL",
            )

    def test_manifest_hashes_are_self_consistent(self) -> None:
        manifest = self.data["manifest"]
        self.assertFalse(manifest["authority"]["m1_mock_qualification"])
        if self.data["readiness"].get("capability_result_status"):
            self.assertFalse(manifest["authority"]["capability_calibration"])
        else:
            self.assertTrue(manifest["authority"]["capability_calibration"])
        self.assertEqual(
            manifest["authority"]["f0"],
            self.data["readiness"].get("f0_authorized", False),
        )
        self.assertFalse(manifest["authority"]["p1"])
        self.assertEqual(
            manifest["provider_calls"],
            self.data["readiness"]["capability_provider_request_total"],
        )
        self.assertEqual(manifest["provider_calls_accounting_domain"], "DIRECT_API_ONLY")
        self.assertEqual(
            manifest["codingplan_account_window_requests"],
            self.data["readiness"]["codingplan_account_window_request_delta"],
        )
        self.assertIn("DO_NOT_SUM", manifest["codingplan_request_accounting_domain"])
        self.assertEqual(
            manifest["deepseek_codingplan_account_window_requests"],
            self.data["readiness"]["deepseek_account_window_request_delta"],
        )
        self.assertIn(
            "DO_NOT_SUM", manifest["deepseek_codingplan_request_accounting_domain"]
        )
        self.assertEqual(
            manifest["glm52_codingplan_account_window_requests"],
            self.data["readiness"]["glm52_account_window_request_delta"],
        )
        self.assertIn(
            "DO_NOT_SUM", manifest["glm52_codingplan_request_accounting_domain"]
        )
        self.assertEqual(
            manifest["mimo25_codingplan_account_window_requests"],
            self.data["readiness"]["mimo25_account_window_request_delta"],
        )
        self.assertIn(
            "DO_NOT_SUM", manifest["mimo25_codingplan_request_accounting_domain"]
        )
        for relative, metadata in manifest["files"].items():
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(sha256(path), metadata["sha256"])
            self.assertEqual(path.stat().st_size, metadata["bytes"])


if __name__ == "__main__":
    unittest.main()
