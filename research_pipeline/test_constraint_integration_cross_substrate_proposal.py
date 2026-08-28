from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "generated" / "constraint-integration-cross-substrate-proposal-20260828.json"
AUDIT = ROOT / "generated" / "lego-bench-outcome-blind-construct-audit-20260828.json"
COLLISION = ROOT / "generated" / "constraint-integration-current-source-collision-review-20260828.json"
PLAN = ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"

EXPECTED_AUDIT_SHA256 = "f8e845bb66d5c3ae897e939bb9877c1ae85e0491955a4d099e45d6f8bd7d868d"
EXPECTED_COLLISION_SHA256 = "05d985e0b526ce36c545e1f6427cb5d3e7646fa3a8d437f5281e632f34aad278"
EXPECTED_METADATA_SHA256 = "c4cab948b923b522b9ba4991e167e1c5c7d503786f2b2e5c11a64dab89113c21"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ConstraintIntegrationCrossSubstrateProposalTest(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = json.loads(PROPOSAL.read_text(encoding="utf-8"))
        self.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        self.collision = json.loads(COLLISION.read_text(encoding="utf-8"))
        self.plan = json.loads(PLAN.read_text(encoding="utf-8"))

    def test_proposal_is_noncanonical_zero_authority(self) -> None:
        self.assertIsNone(self.proposal["canonical_candidate_id"])
        self.assertEqual(self.proposal["generator_admission"], "PENDING")
        self.assertFalse(self.proposal["scientific_authority"])
        self.assertFalse(self.proposal["execution_authority"])
        self.assertEqual(self.proposal["provider_calls_executed"], 0)
        self.assertEqual(self.proposal["gpu_calls_executed"], 0)
        self.assertTrue(self.proposal["authority"])
        self.assertFalse(any(self.proposal["authority"].values()))
        self.assertEqual(self.proposal["candidate_generator_suite"]["execution_status"], "NOT_AUTHORIZED")
        self.assertEqual(self.proposal["method_intervention"]["status"], "DEFERRED_UNTIL_PROBLEM_GATE")

    def test_port010_hold_is_not_replaced_or_reopened(self) -> None:
        relation = self.proposal["relation_to_port010"]
        self.assertEqual(relation["role"], "HYPOTHESIS_SOURCE_ONLY")
        self.assertEqual(relation["port010_effective_status"], "HOLD_EVIDENCE_REVIEW_BLOCKED")
        self.assertEqual(relation["port010_evidence_review"], "BLOCK_BAKE_IN")
        self.assertFalse(relation["port010_reopen_effect"])
        self.assertTrue(relation["benchmark_replacement_cannot_close_or_reopen_port010"])

        rows = [
            row
            for row in self.plan.get("entries") or []
            if row.get("candidate_id") == "PORT-010"
            and row.get("title") == "Complex-description boundary in end-to-end 3D world construction"
        ]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["status"], "HOLD_EVIDENCE_REVIEW_BLOCKED")
        self.assertEqual((row.get("evidence_review") or {}).get("verdict"), "BLOCK_BAKE_IN")
        adjudication = row["release_change_adjudication"]
        self.assertEqual(adjudication["remaining_reopen_components"], ["per_case_outcomes"])
        for key in (
            "offline_replay_tier_authorized",
            "provider_authority",
            "gpu_authority",
            "scientific_execution_authority",
            "scientific_authority",
        ):
            self.assertFalse(adjudication[key])

    def test_construct_audit_is_content_addressed_and_outcome_blind_at_case_level(self) -> None:
        self.assertEqual(sha256_file(AUDIT), EXPECTED_AUDIT_SHA256)
        self.assertEqual(self.proposal["construct_preflight"]["artifact_sha256"], EXPECTED_AUDIT_SHA256)
        self.assertEqual(self.audit["source"]["metadata_sha256"], EXPECTED_METADATA_SHA256)
        self.assertEqual(
            self.proposal["source_provenance"]["lego_bench_dataset"]["metadata_sha256"],
            EXPECTED_METADATA_SHA256,
        )
        exposure = self.proposal["outcome_exposure_control"]
        self.assertFalse(exposure["per_case_generation_outcomes_read"])
        self.assertFalse(exposure["per_case_evaluator_validity_read"])
        self.assertFalse(exposure["per_case_baseline_scores_read"])
        self.assertFalse(exposure["performance_conditioned_pair_selection"])
        self.assertTrue(exposure["published_aggregate_baseline_results_seen_during_source_survey"])
        self.assertFalse(exposure["published_aggregate_results_used_to_choose_construct_or_pairs"])

    def test_current_source_collision_forces_conditional_independence_null(self) -> None:
        self.assertEqual(sha256_file(COLLISION), EXPECTED_COLLISION_SHA256)
        review = self.proposal["current_source_collision_review"]
        self.assertEqual(review["artifact_sha256"], EXPECTED_COLLISION_SHA256)
        self.assertEqual(review["status"], "SURVIVING_GAP_NARROWED")
        roles = {row["role"] for row in self.collision["sources"]}
        self.assertIn("DIRECT_BENCHMARK_COLLISION", roles)
        self.assertIn("CROSS_DOMAIN_STRONG_NULL", roles)
        self.assertIn("GENERIC_METHOD_COLLISION", roles)
        gap = self.collision["surviving_scientific_gap"]
        self.assertEqual(gap["strongest_null"], "conditional independent-failure / multiplicative-accumulation model")
        self.assertIn("moderator", gap["entropy_role"])
        obj = self.proposal["scientific_object"]
        self.assertIn("conditional-independent", obj["strongest_same_information_baseline"])
        self.assertIn("multiplicative", obj["prediction_disagreement"])
        future = self.proposal["future_analysis_contract_if_authorized"]
        self.assertEqual(len(future["measurement_negative_controls"]), 2)
        self.assertFalse(self.collision["scientific_authority"])
        self.assertFalse(any(self.collision["authority"].values()))

    def test_raw_count_is_rejected_and_entropy_construct_only_advances_to_review(self) -> None:
        raw = self.audit["constructs"]["raw_constraint_count"]
        entropy = self.audit["constructs"]["condition_type_entropy"]
        self.assertEqual(raw["disposition"], "REJECT_LENGTH_CONFOUNDED")
        self.assertGreaterEqual(abs(raw["spearman_with_instruction_words"]), raw["reject_threshold_abs_rho"])
        self.assertEqual(entropy["disposition"], "CLEAR_FOR_ZERO_AUTHORITY_GENERATOR_REVIEW")
        self.assertLess(abs(entropy["spearman_with_instruction_words"]), entropy["clear_threshold_abs_rho"])
        self.assertFalse(self.audit["scientific_authority"])
        self.assertFalse(self.audit["execution_authority"])

    def test_strict_f0_panel_is_pre_outcome_and_sufficient_for_bounded_falsifier(self) -> None:
        panel = self.audit["strict_matched_f0_feasibility"]
        self.assertFalse(panel["selection_uses_outcomes"])
        self.assertTrue(panel["same_constraint_count"])
        self.assertTrue(panel["same_analyst_defined_ordinal_metadata_block"])
        self.assertEqual(panel["max_instruction_word_difference"], 10)
        self.assertEqual(panel["min_type_entropy_difference_bits"], 0.35)
        self.assertEqual(panel["selected_disjoint_pairs"], 11)
        self.assertGreaterEqual(panel["selected_disjoint_pairs"], panel["minimum_pairs_required"])
        seen: set[int] = set()
        for pair in panel["pairs"]:
            self.assertGreater(pair["constraint_count"], 0)
            self.assertLessEqual(pair["word_difference"], 10)
            self.assertGreaterEqual(pair["entropy_difference_bits"], 0.35)
            self.assertNotIn(pair["low_entropy_index"], seen)
            self.assertNotIn(pair["high_entropy_index"], seen)
            seen.update({pair["low_entropy_index"], pair["high_entropy_index"]})

    def test_label_binding_uses_condition_idx_not_list_order(self) -> None:
        exposure = self.audit["outcome_exposure"]
        self.assertEqual(exposure["label_order_mismatch_rows"], [121, 127, 129])
        self.assertIn("condition_idx", exposure["label_binding_rule"])
        self.assertEqual(
            exposure["consumed_fields"],
            ["instruction", "constraints", "labels.condition_idx", "labels.condition_type"],
        )


if __name__ == "__main__":
    unittest.main()
