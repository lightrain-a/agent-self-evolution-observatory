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
        for name in ("capability", "f0"):
            self.assertEqual(self.data[name]["scientific_outcomes_observed"], 0)
            self.assertEqual(self.data[name]["gpu_runs"], 0)
        readiness = self.data["readiness"]
        self.assertEqual(self.data["manifest"]["scientific_outcomes_observed"], readiness["f0_outcomes_observed"])
        self.assertEqual(self.data["manifest"]["gpu_runs"], 0)
        self.assertEqual(self.data["capability"]["provider_calls"], 0)
        self.assertEqual(self.data["f0"]["provider_calls"], 0)
        self.assertEqual(
            self.data["manifest"]["provider_calls"],
            readiness["capability_provider_request_total"],
        )
        if readiness.get("f0_adjudication_verdict") == "F0_UPDATE_UPTAKE_FAIL":
            self.assertTrue(readiness["f0_executed"])
            self.assertEqual(readiness["f0_source_outcomes_observed"], 8)
            self.assertEqual(readiness["f0_probe_effects_observed"], 0)
            self.assertEqual(readiness["f0_outcomes_observed"], 8)
        else:
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
        if readiness.get("capability_model_selection_state") == "SELECTED_MIMO25PRO_SQ0_V5_FINAL_CALIBRATION_AUTHORIZED_AFTER_V4_TOO_HARD":
            self.assertEqual(readiness["status"], "SQ0_V5_FINAL_TARGET_FAILURE_QUALIFICATION_AUTHORIZED_READY")
            self.assertEqual(readiness["next_authorized_action"], "RUN_SQ0_V5_MIMO25PRO_FINAL_CALIBRATION")
            self.assertTrue(readiness["sq0_v4_closed"])
            self.assertEqual(readiness["sq0_v4_result_status"], "SQ0_V4_TARGET_CHALLENGE_TOO_HARD_STOP")
            self.assertEqual(readiness["sq0_v4_usable_target_failure_count"], 11)
            self.assertEqual(readiness["sq0_v4_target_success_count"], 1)
            self.assertEqual(readiness["sq0_v4_closeout_status"], "SQ0_V4_TOO_HARD_CLOSEOUT")
            self.assertEqual(readiness["sq0_v4_root_cause_status"], "SQ0_V4_TOO_HARD_WITH_SERIALIZATION_AND_SEMANTIC_FAILURE_MIX")
            self.assertEqual(readiness["sq0_v5_static_contract_status"], "SQ0_V5_STATIC_DESIGN_READY_FINAL_CALIBRATION")
            self.assertEqual(readiness["sq0_v5_static_qualification_status"], "SQ0_V5_PUBLIC_REACHABILITY_AND_FRESHNESS_PASS_FINAL_CALIBRATION")
            self.assertTrue(readiness["sq0_v5_final_calibration"])
            self.assertEqual(readiness["sq0_v5_static_max_public_tool_calls"], 48)
            self.assertEqual(readiness["sq0_v5_static_minimum_headroom"], 32)
            for key in ("case_id_overlap_count","instruction_hash_overlap_count","fixture_hash_overlap_count","target_local_resource_hash_overlap_count"):
                self.assertEqual(readiness["sq0_v5_freshness_audit"][key], 0)
            self.assertEqual(readiness["sq0_v5_human_authorization_status"], "USER_AUTHORIZED_SQ0_V5_AFTER_V4_TOO_HARD_CLOSEOUT_AND_STATIC_PASS")
            self.assertEqual(readiness["sq0_v5_mcp_q1_status"], "SQ0_V5_MIMO25PRO_MCP_PREDISPATCH_PASS")
            self.assertEqual(readiness["sq0_v5_mcp_q1_model_requests"], 0)
            self.assertEqual(readiness["sq0_v5_execution_contract_status"], "SQ0_V5_MIMO25PRO_EXECUTION_AUTHORIZED")
            self.assertTrue(readiness["sq0_v5_execution_authorized"])
            self.assertTrue(readiness["f0_r1_sq0_execution_authorized"])
            self.assertFalse(readiness["f0_r1_execution_authorized"])
            self.assertFalse(readiness["f0_authorized"])
            self.assertFalse(readiness["p1_authorized"])
        elif readiness.get("capability_model_selection_state") == "SELECTED_MIMO25PRO_SQ0_V4_AUTHORIZED_AFTER_V3_FUTILITY_CLOSEOUT":
            self.assertEqual(readiness["status"], "SQ0_V4_TARGET_FAILURE_QUALIFICATION_AUTHORIZED_READY")
            self.assertEqual(readiness["next_authorized_action"], "RUN_SQ0_V4_MIMO25PRO")
            self.assertTrue(readiness["sq0_v3_closed"])
            self.assertEqual(readiness["sq0_v3_closeout_status"], "SQ0_V3_TOO_EASY_FUTILITY_CLOSEOUT")
            self.assertEqual(readiness["sq0_v3_root_cause_status"], "SQ0_V3_TNF_TOO_EASY_FG_NEAR_TARGET_WINDOW")
            self.assertEqual(readiness["sq0_v4_static_contract_status"], "SQ0_V4_STATIC_DESIGN_READY")
            self.assertEqual(readiness["sq0_v4_static_qualification_status"], "SQ0_V4_PUBLIC_REACHABILITY_AND_FRESHNESS_PASS")
            self.assertEqual(readiness["sq0_v4_static_max_public_tool_calls"], 48)
            self.assertEqual(readiness["sq0_v4_static_minimum_headroom"], 32)
            self.assertEqual(readiness["sq0_v4_freshness_audit"]["case_id_overlap_count"], 0)
            self.assertEqual(readiness["sq0_v4_freshness_audit"]["instruction_hash_overlap_count"], 0)
            self.assertEqual(readiness["sq0_v4_freshness_audit"]["fixture_hash_overlap_count"], 0)
            self.assertEqual(readiness["sq0_v4_freshness_audit"]["target_local_resource_hash_overlap_count"], 0)
            self.assertEqual(readiness["sq0_v4_human_authorization_status"], "USER_AUTHORIZED_SQ0_V4_AFTER_V3_FUTILITY_CLOSEOUT_AND_STATIC_PASS")
            self.assertEqual(readiness["sq0_v4_mcp_q1_status"], "SQ0_V4_MIMO25PRO_MCP_PREDISPATCH_PASS")
            self.assertEqual(readiness["sq0_v4_mcp_q1_model_requests"], 0)
            self.assertEqual(readiness["sq0_v4_execution_contract_status"], "SQ0_V4_MIMO25PRO_EXECUTION_AUTHORIZED")
            self.assertTrue(readiness["sq0_v4_execution_authorized"])
            self.assertTrue(readiness["f0_r1_sq0_execution_authorized"])
            self.assertFalse(readiness["f0_r1_execution_authorized"])
            self.assertFalse(readiness["f0_authorized"])
            self.assertFalse(readiness["p1_authorized"])
        elif readiness.get("capability_model_selection_state") == "SELECTED_MIMO25PRO_SQ0_V3_AUTHORIZED_AFTER_V2R1_CLOSEOUT":
            self.assertEqual(readiness["status"], "SQ0_V3_TARGET_FAILURE_QUALIFICATION_AUTHORIZED_READY")
            self.assertEqual(readiness["next_authorized_action"], "RUN_SQ0_V3_MIMO25PRO")
            self.assertEqual(readiness["sq0_v3_static_contract_status"], "SQ0_V3_STATIC_DESIGN_READY")
            self.assertEqual(readiness["sq0_v3_static_qualification_status"], "SQ0_V3_PUBLIC_REACHABILITY_PASS")
            self.assertLessEqual(readiness["sq0_v3_static_max_public_tool_calls"], 30)
            self.assertGreaterEqual(readiness["sq0_v3_static_minimum_headroom"], 18)
            self.assertEqual(readiness["sq0_v3_human_authorization_status"], "USER_AUTHORIZED_SQ0_V3_AFTER_TRANSPORT_QUALIFICATION_PASS")
            self.assertEqual(readiness["sq0_v3_mcp_q1_status"], "SQ0_V3_MIMO25PRO_MCP_PREDISPATCH_PASS")
            self.assertEqual(readiness["sq0_v3_mcp_q1_model_requests"], 0)
            self.assertEqual(readiness["sq0_v3_execution_contract_status"], "SQ0_V3_MIMO25PRO_EXECUTION_AUTHORIZED")
            self.assertTrue(readiness["sq0_v3_execution_authorized"])
            self.assertFalse(readiness["f0_r1_execution_authorized"])
            self.assertFalse(readiness["f0_authorized"])
            self.assertFalse(readiness["p1_authorized"])
        elif readiness.get("capability_model_selection_state") == "SELECTED_MIMO25PRO_SQ0_V2R1_TOO_EASY_CLOSED_V3_DESIGN_REQUIRED":
            self.assertEqual(readiness["status"], "SQ0_V2R1_TOO_EASY_CLOSED_V3_DESIGN_REQUIRED")
            self.assertEqual(readiness["next_authorized_action"], "BUILD_FRESH_SQ0_V3_SEMANTIC_CHALLENGE")
            self.assertEqual(readiness["sq0_v2r1_result_status"], "SQ0_V2R1_TARGET_CHALLENGE_TOO_EASY_STOP")
            self.assertEqual(readiness["sq0_v2r1_usable_target_failure_count"], 4)
            self.assertAlmostEqual(readiness["sq0_v2r1_usable_target_failure_rate"], 1.0 / 3.0)
            self.assertEqual(readiness["sq0_v2r1_non_semantic_failure_units"], [])
            self.assertEqual(readiness["sq0_v2r1_scientific_model_round_count"], 180)
            self.assertEqual(readiness["sq0_v2r1_closeout_status"], "SQ0_V2R1_TOO_EASY_CLOSEOUT")
            self.assertEqual(readiness["sq0_v2r1_root_cause_status"], "SQ0_V2R1_RAW_FAILURES_ARE_FORMATTING_PSEUDO_FAILURES")
            self.assertEqual(readiness["sq0_v2r1_semantic_failure_count"], 0)
            self.assertTrue(readiness["sq0_v2r1_closed"])
            self.assertFalse(readiness["sq0_v2r1_execution_authorized"])
            self.assertFalse(readiness["f0_r1_execution_authorized"])
            self.assertFalse(readiness["f0_authorized"])
            self.assertFalse(readiness["p1_authorized"])
        elif readiness.get("capability_model_selection_state") == "SELECTED_MIMO25PRO_SQ0_V2R1_AUTHORIZED_AFTER_TRANSPORT_PASS":
            self.assertEqual(readiness["status"], "SQ0_V2R1_TARGET_FAILURE_QUALIFICATION_AUTHORIZED_READY")
            self.assertEqual(readiness["next_authorized_action"], "RUN_SQ0_V2R1_MIMO25PRO")
            self.assertEqual(readiness["sq0_v2_void_status"], "SQ0_V2_VOID_NATIVE_READ_FILE_SCHEMA_CONTAMINATION")
            self.assertTrue(readiness["sq0_v2_void_active"])
            self.assertEqual(readiness["sq0_v2r1_static_contract_status"], "SQ0_V2R1_STATIC_DESIGN_READY")
            self.assertEqual(readiness["sq0_v2r1_static_qualification_status"], "SQ0_V2R1_PUBLIC_REACHABILITY_PASS")
            self.assertLessEqual(readiness["sq0_v2r1_static_max_public_tool_calls"], 25)
            self.assertGreaterEqual(readiness["sq0_v2r1_static_minimum_headroom"], 15)
            self.assertEqual(readiness["sq0_v2r1_transport_contract_status"], "SQ0_V2R1_TRANSPORT_QUALIFICATION_AUTHORIZED")
            self.assertEqual(readiness["sq0_v2r1_transport_result_status"], "SQ0_V2R1_TRANSPORT_QUALIFICATION_PASS")
            self.assertEqual(readiness["sq0_v2r1_transport_native_tool_attempts"], [])
            self.assertEqual(readiness["sq0_v2r1_human_authorization_status"], "USER_AUTHORIZED_SQ0_V2R1_AFTER_TRANSPORT_QUALIFICATION_PASS")
            self.assertEqual(readiness["sq0_v2r1_mcp_q1_status"], "SQ0_V2R1_MIMO25PRO_MCP_PREDISPATCH_PASS")
            self.assertEqual(readiness["sq0_v2r1_mcp_q1_model_requests"], 0)
            self.assertEqual(readiness["sq0_v2r1_execution_contract_status"], "SQ0_V2R1_MIMO25PRO_EXECUTION_AUTHORIZED")
            self.assertTrue(readiness["sq0_v2r1_execution_authorized"])
            self.assertFalse(readiness["sq0_v2_execution_authorized"])
            self.assertFalse(readiness["f0_r1_execution_authorized"])
            self.assertFalse(readiness["f0_authorized"])
            self.assertFalse(readiness["p1_authorized"])
        elif readiness.get("capability_model_selection_state") == "SELECTED_MIMO25PRO_SQ0_V2R1_TRANSPORT_READY_AFTER_V2_VOID":
            self.assertEqual(readiness["status"], "SQ0_V2R1_TRANSPORT_QUALIFICATION_AUTHORIZED_READY")
            self.assertEqual(readiness["next_authorized_action"], "RUN_SQ0_V2R1_TRANSPORT_QUALIFICATION")
            self.assertEqual(readiness["sq0_v2_void_status"], "SQ0_V2_VOID_NATIVE_READ_FILE_SCHEMA_CONTAMINATION")
            self.assertTrue(readiness["sq0_v2_void_active"])
            self.assertEqual(readiness["sq0_v2r1_static_contract_status"], "SQ0_V2R1_STATIC_DESIGN_READY")
            self.assertEqual(readiness["sq0_v2r1_static_qualification_status"], "SQ0_V2R1_PUBLIC_REACHABILITY_PASS")
            self.assertLessEqual(readiness["sq0_v2r1_static_max_public_tool_calls"], 25)
            self.assertGreaterEqual(readiness["sq0_v2r1_static_minimum_headroom"], 15)
            self.assertEqual(readiness["sq0_v2r1_transport_contract_status"], "SQ0_V2R1_TRANSPORT_QUALIFICATION_AUTHORIZED")
            self.assertIsNone(readiness["sq0_v2r1_transport_result_status"])
            self.assertTrue(readiness["sq0_v2r1_transport_qualification_ready"])
            self.assertFalse(readiness["sq0_v2_execution_authorized"])
            self.assertFalse(readiness["f0_r1_execution_authorized"])
            self.assertFalse(readiness["f0_authorized"])
            self.assertFalse(readiness["p1_authorized"])
        elif readiness.get("capability_model_selection_state") == "SELECTED_MIMO25PRO_SQ0_V2_AUTHORIZED_AFTER_V1_TOO_EASY":
            self.assertEqual(readiness["status"], "SQ0_V2_TARGET_FAILURE_QUALIFICATION_AUTHORIZED_READY")
            self.assertEqual(readiness["next_authorized_action"], "RUN_SQ0_V2_MIMO25PRO")
            self.assertEqual(readiness["sq0_v2_static_contract_status"], "SQ0_V2_TARGET_CHALLENGE_STATIC_DESIGN_READY")
            self.assertEqual(readiness["sq0_v2_static_qualification_status"], "SQ0_V2_PUBLIC_REACHABILITY_PASS")
            self.assertLessEqual(readiness["sq0_v2_static_max_public_tool_calls"], 26)
            self.assertGreaterEqual(readiness["sq0_v2_static_minimum_headroom"], 10)
            self.assertEqual(readiness["sq0_v2_human_authorization_status"], "USER_AUTHORIZED_SQ0_V2_DEVELOPMENT_ITERATION_AFTER_V1_TOO_EASY")
            self.assertEqual(readiness["sq0_v2_mcp_q1_status"], "SQ0_V2_MIMO25PRO_MCP_PREDISPATCH_PASS")
            self.assertEqual(readiness["sq0_v2_mcp_q1_model_requests"], 0)
            self.assertEqual(readiness["sq0_v2_execution_contract_status"], "SQ0_V2_MIMO25PRO_EXECUTION_AUTHORIZED")
            self.assertTrue(readiness["sq0_v2_execution_authorized"])
            self.assertFalse(readiness["f0_r1_execution_authorized"])
            self.assertFalse(readiness["f0_authorized"])
            self.assertFalse(readiness["p1_authorized"])
        elif readiness.get("capability_model_selection_state") == "SELECTED_MIMO25PRO_SQ0_V1_TOO_EASY_STOP":
            self.assertEqual(readiness["status"], "SQ0_TARGET_CHALLENGE_TOO_EASY_STOP")
            self.assertEqual(readiness["next_authorized_action"], "DESIGN_FRESH_SQ0_V2_TARGET_CHALLENGE")
            self.assertEqual(readiness["sq0_v1_result_status"], "SQ0_TARGET_CHALLENGE_TOO_EASY_STOP")
            self.assertEqual(readiness["sq0_v1_closeout_status"], "SQ0_V1_TOO_EASY_CLOSEOUT")
            self.assertEqual(readiness["sq0_v1_usable_target_failure_count"], 0)
            self.assertEqual(readiness["sq0_v1_usable_target_failure_rate"], 0.0)
            self.assertEqual(readiness["sq0_v1_scientific_model_round_count"], 135)
            self.assertEqual(readiness["sq0_v1_appworld_tool_call_total"], 190)
            self.assertFalse(readiness["sq0_execution_authorized"])
            self.assertFalse(readiness["f0_r1_execution_authorized"])
            self.assertFalse(readiness["f0_authorized"])
            self.assertFalse(readiness["p1_authorized"])
        elif readiness.get("capability_model_selection_state") == "SELECTED_MIMO25PRO_SQ0_AUTHORIZED_AFTER_F0_UPTAKE_FAIL":
            self.assertEqual(readiness["status"], "SQ0_TARGET_FAILURE_QUALIFICATION_AUTHORIZED_READY")
            self.assertEqual(readiness["next_authorized_action"], "RUN_SQ0_MIMO25PRO_V1")
            self.assertTrue(readiness["f0_executed"])
            self.assertFalse(readiness["f0_authorized"])
            self.assertFalse(readiness["p1_authorized"])
            self.assertEqual(readiness["f0_adjudication_verdict"], "F0_UPDATE_UPTAKE_FAIL")
            self.assertEqual(readiness["sq0_static_contract_status"], "SQ0_TARGET_CHALLENGE_V1_STATIC_DESIGN_READY")
            self.assertEqual(readiness["sq0_static_qualification_status"], "SQ0_TARGET_CHALLENGE_V1_PUBLIC_REACHABILITY_PASS")
            self.assertLessEqual(readiness["sq0_static_max_public_tool_calls"], 18)
            self.assertGreaterEqual(readiness["sq0_static_minimum_headroom"], 6)
            self.assertEqual(readiness["sq0_human_authorization_status"], "USER_AUTHORIZED_SQ0_TARGET_FAILURE_QUALIFICATION_AFTER_F0_UPTAKE_FAIL")
            self.assertEqual(readiness["sq0_mcp_q1_status"], "SQ0_MIMO25PRO_MCP_PREDISPATCH_PASS")
            self.assertEqual(readiness["sq0_mcp_q1_model_requests"], 0)
            self.assertEqual(readiness["sq0_execution_contract_status"], "SQ0_MIMO25PRO_V1_EXECUTION_AUTHORIZED")
            self.assertTrue(readiness["sq0_execution_authorized"])
            self.assertTrue(readiness["f0_r1_sq0_execution_authorized"])
            self.assertFalse(readiness["f0_r1_execution_authorized"])
        elif readiness.get("capability_model_selection_state") == "SELECTED_MIMO25PRO_F0_UPDATE_UPTAKE_FAIL":
            self.assertEqual(readiness["status"], "F0_UPDATE_UPTAKE_FAIL")
            self.assertEqual(readiness["next_authorized_action"], "STOP_CURRENT_F0_REVIEW_PROSPECTIVE_SOURCE_FAILURE_QUALIFICATION_PROPOSAL")
            self.assertTrue(readiness["f0_executed"])
            self.assertFalse(readiness["f0_authorized"])
            self.assertFalse(readiness["p1_authorized"])
            self.assertEqual(readiness["f0_source_target_success_count"], 8)
            self.assertEqual(readiness["f0_source_target_failure_count"], 0)
            self.assertEqual(readiness["f0_eligible_repair_family_count"], 0)
            self.assertEqual(readiness["f0_source_scientific_model_round_count"], 74)
            self.assertEqual(readiness["f0_source_appworld_tool_call_total"], 87)
            self.assertEqual(readiness["f0_probe_episode_count"], 0)
            self.assertEqual(readiness["f0_adjudication_verdict"], "F0_UPDATE_UPTAKE_FAIL")
            self.assertEqual(
                readiness["f0_uptake_root_cause_status"],
                "CAPABILITY_GATE_DOES_NOT_IDENTIFY_SOURCE_FAILURE_AVAILABILITY",
            )
            self.assertEqual(
                readiness["f0_uptake_root_cause_classification"],
                "SOURCE_FAILURE_OPPORTUNITY_DESIGN_MISMATCH",
            )
            self.assertEqual(
                readiness["f0_r1_proposal_status"],
                "PROSPECTIVE_F0_R1_SOURCE_FAILURE_QUALIFICATION_PROPOSAL_ONLY",
            )
            self.assertFalse(readiness["f0_r1_sq0_execution_authorized"])
            self.assertFalse(readiness["f0_r1_execution_authorized"])
        elif readiness.get("capability_model_selection_state") == "SELECTED_MIMO25PRO_F0_SOURCE_AUTHORIZED":
            self.assertEqual(readiness["status"], "F0_SOURCE_AUTHORIZED_READY")
            self.assertEqual(readiness["next_authorized_action"], "RUN_F0_SOURCE_MIMO25PRO")
            self.assertTrue(readiness["eligible_backbone_selected"])
            self.assertTrue(readiness["f0_authorized"])
            self.assertFalse(readiness["p1_authorized"])
            self.assertFalse(readiness["tool_sandbox_authorized"])
            self.assertFalse(readiness["appworld_ul_authorized"])
            self.assertEqual(
                readiness["f0_human_authorization_status"],
                "USER_AUTHORIZED_F0_AFTER_MIMO25PRO_CAPABILITY_PASS",
            )
            self.assertEqual(
                readiness["f0_transport_addendum_status"],
                "F0_SELECTED_BACKBONE_TRANSPORT_COMPATIBILITY_ADDENDUM_PASS",
            )
            self.assertEqual(
                readiness["f0_mcp_q1_status"],
                "F0_CODINGPLAN_MIMO25PRO_MCP_PREDISPATCH_PASS",
            )
            self.assertEqual(readiness["f0_mcp_q1_model_requests"], 0)
            self.assertEqual(
                readiness["f0_source_contract_status"],
                "F0_CODINGPLAN_MIMO25PRO_SOURCE_AUTHORIZED",
            )
        elif readiness.get("capability_model_selection_state") == "SELECTED_MIMO25PRO_PASS_F0_AUTHORIZATION_REQUIRED":
            self.assertEqual(
                readiness["status"],
                "CAPABILITY_CALIBRATION_PASS_F0_AUTHORIZATION_REQUIRED",
            )
            self.assertEqual(
                readiness["next_authorized_action"],
                "STOP_AWAIT_HUMAN_F0_AUTHORIZATION",
            )
            self.assertTrue(readiness["eligible_backbone_selected"])
            self.assertEqual(readiness["mimo25pro_capability_result_status"], "CAPABILITY_CALIBRATION_PASS")
            self.assertEqual(readiness["mimo25pro_capability_closeout_status"], "CODINGPLAN_MIMO25PRO_B3_PASS_CLOSEOUT")
            self.assertEqual(readiness["mimo25pro_scientific_model_round_count"], 77)
            self.assertEqual(readiness["mimo25pro_account_window_request_delta"], 78)
            self.assertEqual(readiness["mimo25pro_account_level_unattributed_request_count"], 1)
            self.assertEqual(readiness["mimo25pro_tool_loop_completion_rate"], 0.875)
            self.assertEqual(readiness["mimo25pro_target_success_rate"], 0.875)
            self.assertEqual(readiness["selected_backbone_capability_result_status"], "CAPABILITY_CALIBRATION_PASS")
            self.assertEqual(
                readiness["selected_backbone"],
                {
                    "model_id": "mimo-v2.5-pro",
                    "model_profile": "AtomGit-mimo-v2.5-pro",
                    "provider": "ATOMGIT_CODINGPLAN_SIGNED_GATEWAY",
                    "harness": "ATOMCODE_CODINGPLAN_MCP_V1",
                },
            )
            self.assertFalse(readiness["f0_authorized"])
        elif readiness.get("capability_model_selection_state") == "SEARCH_ACTIVE_QWEN_CEILING_DEEPSEEK_FLOOR_GLM52_CEILING_MIMO25_CEILING_MIMO25PRO_NEXT":
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
