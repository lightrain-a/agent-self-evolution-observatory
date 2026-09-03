from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "experiments" / "relational_topology_3d" / "RELATIONAL-TOPOLOGY-STAGE-3D-20260831-oracle-pivot-v20"


def load(name: str):
    return json.loads((ART / name).read_text())


class RelationalTopologyOraclePivotV20Test(unittest.TestCase):
    def test_review_receipt_is_real_independent_browser_review(self):
        x = load("oracle_review_receipt.json")
        self.assertEqual(x["verdict"], "PIVOT")
        self.assertEqual(x["oracle"]["version"], "0.18.0")
        self.assertEqual(x["oracle"]["model_dom_verified"], "GPT-5.6 Sol")
        self.assertTrue(x["oracle"]["model_dom_aria_checked"])
        self.assertEqual(x["oracle"]["thinking_dom_verified"], "Extra High, 4 of 5")
        self.assertTrue(x["oracle"]["prompt_submitted"])
        self.assertEqual(x["oracle"]["status"], "completed")
        self.assertEqual(x["scientific_outcomes_read"], 0)
        self.assertFalse(x["p1_opened"])

    def test_pure_support_claim_is_rejected_by_input_dose(self):
        x = load("training_exposure_dose_audit.json")
        self.assertEqual(x["corpora"]["SGP-12"]["rows"], 12240)
        self.assertEqual(x["corpora"]["SGP-14"]["rows"], 12240)
        self.assertEqual(x["corpora"]["SGP-12"]["total_relation_edges"], 18360)
        self.assertEqual(x["corpora"]["SGP-14"]["total_relation_edges"], 30600)
        self.assertAlmostEqual(x["derived_differences"]["relation_edge_dose_ratio_SGP14_over_SGP12"], 5 / 3)
        self.assertFalse(x["adjudication"]["SGP12_vs_SGP14_identifies_training_support_alone"])
        self.assertEqual(x["adjudication"]["allowed_label"], "MATCHED_TRAINING_EXPOSURE_REGIMES")
        self.assertFalse(x["adjudication"]["restart_required_for_topology_first_paper"])

    def test_primary_story_is_topology_first_and_sgp14(self):
        x = load("paper_story.json")
        self.assertEqual(x["primary_scientific_object"]["model"], "SGP-14_PLUS_SHARED_SG2SC")
        self.assertEqual(x["primary_scientific_object"]["relation_counts"], [3, 4])
        self.assertEqual(x["primary_scientific_object"]["topology_contrast"], ["CHAIN", "HUB"])
        self.assertEqual(x["secondary_context"]["SGP-12_vs_SGP-14"], "MATCHED_TRAINING_EXPOSURE_REGIME_MODIFIER_ONLY")
        self.assertEqual(x["scientific_outcomes_read"], 0)
        self.assertFalse(x["p1_opened"])

    def test_development_uses_val_and_confirmation_uses_test(self):
        x = load("p1_protocol.json")
        self.assertEqual(x["split_roles"]["val"], "ONE_SEED_DEVELOPMENTAL_P1_SCREEN_AFTER_SEPARATE_AUTHORITY")
        self.assertEqual(x["split_roles"]["test"], "UNTOUCHED_CONFIRMATORY_MULTI_SEED_LOCKBOX")
        self.assertEqual(x["developmental_panel"]["split"], "val")
        self.assertEqual(x["confirmation_if_go"]["split"], "test")
        self.assertFalse(x["authority_boundary"]["p1_authorized"])
        self.assertEqual(x["authority_boundary"]["scientific_outcomes"], 0)

    def test_primary_topology_panel_excludes_invalid_count2_and_bridge(self):
        x = load("p1_protocol.json")
        self.assertEqual(x["primary_relation_counts"], [3, 4])
        self.assertEqual(x["primary_topologies"], ["CHAIN", "HUB"])
        self.assertIn("P3_EQUALS_K1_2", x["excluded_primary_cells"]["count_2_CHAIN_vs_HUB"])
        self.assertIn("NO_FROZEN_NON_ISOMORPHIC_DEFINITION", x["excluded_primary_cells"]["COMPONENT_BRIDGE_OPTIONAL"])
        self.assertEqual(x["topology_templates"]["count_3"]["active_nodes_each"], 4)
        self.assertEqual(x["topology_templates"]["count_4"]["active_nodes_each"], 5)

    def test_panel_size_and_pair_contract_are_frozen(self):
        x = load("p1_protocol.json")
        p = x["developmental_panel"]
        self.assertEqual(p["counts"]["3"]["matched_tuples"], 40)
        self.assertEqual(p["counts"]["4"]["matched_tuples"], 40)
        self.assertEqual(p["total_matched_tuples"], 80)
        self.assertEqual(p["total_instructions"], 160)
        exact = set(x["matched_tuple_contract"]["exact_within_pair"])
        for key in {
            "base_scene_id", "active_object_ids", "active_object_feature_ids",
            "relation_count", "predicate_multiset", "direction_multiset",
            "exact_clip_token_count", "decoder_checkpoint", "decoder_random_or_noise_seed",
        }:
            self.assertIn(key, exact)
        self.assertIn("SGP output", x["matched_tuple_contract"]["forbidden_filters"])
        self.assertIn("SG2SC output", x["matched_tuple_contract"]["forbidden_filters"])

    def test_oracle_identity_is_never_a_silent_filter(self):
        x = load("p1_protocol.json")
        pol = x["predicted_oracle_protocol"]["identity_failure_policy"]
        self.assertIn("Every materialized instruction remains", pol["primary_population"])
        self.assertEqual(pol["diagnostic"], "exact_identity_eligible is recorded for every instruction.")
        self.assertEqual(pol["repair"], "FORBIDDEN")
        self.assertIn("block", pol["localization_block"].lower())
        self.assertIn("decoder sampling seed", x["predicted_oracle_protocol"]["paired_downstream_state"])
        self.assertIn("decoder noise/randomness", x["predicted_oracle_protocol"]["paired_downstream_state"])

    def test_go_rule_is_fully_frozen(self):
        x = load("p1_protocol.json")
        gates = x["go_stop_rule"]["gates"]
        self.assertEqual(set(gates), {
            "meaningful_topology_residual",
            "cross_count_consistency",
            "upstream_correspondence",
            "selective_oracle_recovery",
            "oracle_identification",
        })
        self.assertIn("0.10", gates["meaningful_topology_residual"]["requirement"])
        self.assertIn("0.05", gates["cross_count_consistency"]["requirement"])
        self.assertIn("0.50", gates["selective_oracle_recovery"]["requirement"])
        self.assertIn("0.95", gates["oracle_identification"]["requirement"])
        self.assertIn("0.05", gates["oracle_identification"]["requirement"])
        self.assertIn("DO_NOT_RESCUE_POST_HOC", x["go_stop_rule"]["action_if_any_fail"])

    def test_minimal_primary_analysis_is_paired_not_four_way(self):
        x = load("p1_protocol.json")
        self.assertEqual(x["analysis"]["primary_method"], "PAIRED_BASE_SCENE_CLUSTER_BOOTSTRAP")
        self.assertEqual(x["analysis"]["bootstrap_replicates"], 10000)
        self.assertEqual(x["analysis"]["bootstrap_seed"], 20260903)
        self.assertFalse(x["analysis"]["four_way_mixed_model_primary"])
        self.assertFalse(x["analysis"]["seed_random_effect_in_one_seed_development"])

    def test_confirmation_requires_three_total_sgp14_seeds(self):
        x = load("p1_protocol.json")
        c = x["confirmation_if_go"]
        self.assertEqual(c["minimum_total_SGP14_training_seeds"], 3)
        self.assertEqual(c["new_independent_SGP14_seeds_required_after_development"], 2)
        self.assertEqual(c["panel_compiler"], "SAME_FROZEN_V20_COMPILER_AND_RULES_APPLIED_TO_TEST")


if __name__ == "__main__":
    unittest.main()
