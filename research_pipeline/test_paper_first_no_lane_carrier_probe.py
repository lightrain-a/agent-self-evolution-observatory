from __future__ import annotations

import unittest

from .paper_first_no_lane_carrier_probe import build_carrier_probe_receipt, build_primary_scope_exclusion_receipt, classify_existing_object_carriers, primary_scope_exclusion


class NoLaneCarrierProbeTest(unittest.TestCase):
    def page(self, section: str, paragraph: str) -> str:
        return f"<html><body><h2>{section}</h2><p>{paragraph}</p></body></html>"

    def test_related_work_cannot_supply_carrier(self) -> None:
        html = self.page("2 Related Work", "Prior systems use on-policy distillation after deployment.")
        self.assertEqual(classify_existing_object_carriers(title="Paper", abstract="", fulltext_html=html), [])

    def test_method_section_rescues_parametric_carrier(self) -> None:
        html = self.page("4 Policy Optimization", "Our method uses on-policy distillation to internalize interaction evidence into the deployed policy.")
        rows = classify_existing_object_carriers(title="Method", abstract="", fulltext_html=html)
        self.assertEqual([row["object_lane"] for row in rows], ["parametric_model_state"])
        self.assertTrue(rows[0]["live_rescue_eligible"])
        self.assertFalse(rows[0]["scientific_authority"])

    def test_actor_model_training_rescues_parametric_carrier(self) -> None:
        html = self.page("C.3 Training Hyperparameters", "The actor model is trained with a bounded learning schedule while its parameters and optimizer state are updated from verified rewards.")
        lanes = [row["object_lane"] for row in classify_existing_object_carriers(title="LLM Self-Improvement", abstract="", fulltext_html=html)]
        self.assertEqual(lanes, ["parametric_model_state"])

    def test_explicit_no_parameter_update_blocks_parametric_match(self) -> None:
        html = self.page("4 Self-Evolution Framework", "Our agent optimizes the rule set without any parameter updates; the rule set is refined from validation feedback.")
        lanes = [row["object_lane"] for row in classify_existing_object_carriers(title="Rules", abstract="", fulltext_html=html)]
        self.assertNotIn("parametric_model_state", lanes)
        self.assertIn("skill_harness", lanes)
        skill = next(row for row in classify_existing_object_carriers(title="Rules", abstract="", fulltext_html=html) if row["object_lane"] == "skill_harness")
        self.assertFalse(skill["live_rescue_eligible"])

    def test_strategy_experience_tree_rescues_memory_carrier(self) -> None:
        html = self.page("3.3 Experiment-Guided Strategy Self-Evolution", "Validated outcomes are written back to the hierarchical strategy experience tree, which is refined after each experiment and reused later.")
        lanes = [row["object_lane"] for row in classify_existing_object_carriers(title="Strategy", abstract="", fulltext_html=html)]
        self.assertEqual(lanes, ["memory_continual"])

    def test_world_model_receipt_is_zero_authority(self) -> None:
        html = self.page("3 Method", "We introduce a self-evolving world model whose representation is revised from verified interaction evidence after each round.")
        receipt = build_carrier_probe_receipt(ref="arXiv:test", title="World", primary_sha256="a" * 64, fulltext_sha256="b" * 64, fulltext_html=html)
        self.assertEqual(receipt["matched_existing_object_lanes"], ["world_model"])
        self.assertEqual(receipt["live_rescue_eligible_lanes"], ["world_model"])
        self.assertTrue(receipt["policy"]["new_object_creation_forbidden"])
        self.assertTrue(receipt["policy"]["skill_harness_rescue_is_shadow_only_until_precision_gate_passes"])
        self.assertFalse(receipt["scientific_authority"])

    def test_unrecognized_target_policy_does_not_create_lane(self) -> None:
        html = self.page("3 Method", "The system repeatedly revises a target decision policy from environment feedback and evaluates it on held-out tasks.")
        self.assertEqual(classify_existing_object_carriers(title="Policy", abstract="", fulltext_html=html), [])

    def test_genetic_network_programming_without_language_model_scope_is_excluded_from_carrier_probe(self) -> None:
        abstract = "We propose Human-Inspired Genetic Network Programming (GNP), using adaptive crossover and mutation operators to evolve decision structures for agents."
        exclusion = primary_scope_exclusion(title="Towards Self-Evolving Agents", abstract=abstract)
        self.assertEqual(exclusion["probe_outcome"], "SCOPE_EXCLUDED_BY_PRIMARY")
        self.assertFalse(exclusion["scientific_authority"])
        receipt = build_primary_scope_exclusion_receipt(ref="arXiv:2607.11913", title="Towards Self-Evolving Agents", abstract=abstract, primary_sha256="a" * 64)
        self.assertEqual(receipt["fulltext_sha256"], "")
        self.assertEqual(receipt["matched_existing_object_lanes"], [])
        self.assertEqual(receipt["live_rescue_eligible_lanes"], [])
        self.assertFalse(receipt["policy"]["global_relevance_changed"])

    def test_language_model_genetic_programming_is_not_scope_excluded(self) -> None:
        abstract = "We use Genetic Network Programming to adapt a large language model agent and update its persistent controller."
        self.assertIsNone(primary_scope_exclusion(title="LLM Agent Controller", abstract=abstract))


if __name__ == "__main__":
    unittest.main()
