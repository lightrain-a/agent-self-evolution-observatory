from __future__ import annotations

import copy
import unittest
from pathlib import Path

from .p0_common import load_json
from .principle_adjudication import audit_principle_certificate, adjudicate_experiment_evidence


class PrincipleAdjudicationTest(unittest.TestCase):
    def certificate(self) -> dict:
        config = load_json(Path(__file__).with_name("p0_a1_confirm_config.json"))
        audit = audit_principle_certificate(config)
        self.assertTrue(audit["passed"], audit.get("blockers"))
        return audit

    def test_current_a1_and_a2_configs_have_valid_principle_certificates(self) -> None:
        for name in (
            "p0_a1_screening_config.json", "p0_a1_confirm_config.json",
            "p0_a2_screening_config.json", "p0_a2_confirm_config.json",
        ):
            audit = audit_principle_certificate(load_json(Path(__file__).with_name(name)))
            self.assertTrue(audit["passed"], (name, audit.get("blockers")))
            self.assertFalse(audit["is_formal_gate"], name)

    def test_experiment_design_failure_cannot_falsify_principle(self) -> None:
        verdict = adjudicate_experiment_evidence("no-label-variation", self.certificate())
        self.assertEqual(verdict["verdict"], "EXPERIMENT_DESIGN_REPAIR")
        self.assertFalse(verdict["principle_falsified"])

    def test_representation_failure_updates_operationalization_not_principle(self) -> None:
        verdict = adjudicate_experiment_evidence("representation-signal-mismatch", self.certificate())
        self.assertEqual(verdict["verdict"], "OPERATIONALIZATION_REPAIR")
        self.assertEqual(verdict["scientific_belief_target"], "measurement-bridge")
        self.assertFalse(verdict["principle_falsified"])

    def test_omitted_condition_refines_assumption_before_core_rejection(self) -> None:
        verdict = adjudicate_experiment_evidence(
            "true-negative", self.certificate(), {"omitted_condition_discovered": True}
        )
        self.assertEqual(verdict["verdict"], "ASSUMPTION_OR_SCOPE_REFINEMENT")
        self.assertFalse(verdict["core_mechanism_rejected"])

    def test_true_negative_without_registered_falsifier_does_not_kill_principle(self) -> None:
        verdict = adjudicate_experiment_evidence(
            "true-negative", self.certificate(),
            {"experiment_identifiable": True, "optimization_adequate": True},
        )
        self.assertEqual(verdict["verdict"], "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED")
        self.assertFalse(verdict["principle_falsified"])

    def test_registered_prediction_can_be_falsified_only_with_full_bridge(self) -> None:
        verdict = adjudicate_experiment_evidence(
            "true-negative", self.certificate(), {
                "registered_prediction_id": "A1-P1",
                "assumptions_hold": True,
                "scope_conditions_hold": True,
                "operationalization_valid": True,
                "experiment_identifiable": True,
                "optimization_adequate": True,
                "independent_truth": True,
                "matched_baseline": True,
                "protocol_validity": True,
                "falsifier_triggered": True,
            },
        )
        self.assertEqual(verdict["verdict"], "PRINCIPLE_FALSIFIED")
        self.assertTrue(verdict["principle_falsified"])
        self.assertTrue(verdict["core_mechanism_rejected"])

    def test_missing_failure_update_rule_invalidates_certificate(self) -> None:
        config = load_json(Path(__file__).with_name("p0_a1_confirm_config.json"))
        broken = copy.deepcopy(config)
        del broken["pre_experiment"]["principle_certificate"]["failure_update_rules"]["assumption-violation"]
        audit = audit_principle_certificate(broken)
        self.assertFalse(audit["passed"])
        self.assertIn("principle-failure-update-rule-missing:assumption-violation", audit["blockers"])


if __name__ == "__main__":
    unittest.main()
