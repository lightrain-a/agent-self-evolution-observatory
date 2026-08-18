from __future__ import annotations

import unittest

from .dead_end_failure_layers import (
    ASSUMPTION_SCOPE,
    PRINCIPLE,
    METHOD_FORMULATION,
    OPERATIONALIZATION_IDENTIFIABILITY,
    PROBLEM_NOVELTY,
    classify_readjudication,
    problem_novelty_classification,
)


class DeadEndFailureLayerTest(unittest.TestCase):
    def payload(self, counter_type: str = "SAME_INFORMATION_REDUCTION") -> dict:
        return {
            "principle_dead_end_certified": True,
            "principle_diagnosis": {
                "counter_explanation": {"type": counter_type},
            },
            "authority": {"experiment_alone_authorizes_dead_end": False},
        }

    def test_explicit_broader_falsification_is_principle_layer(self) -> None:
        p = self.payload()
        p["broader_core_principle_falsified"] = True
        row = classify_readjudication(p, "anything-principle-readjudication.json")
        self.assertEqual(row["failure_layer"], PRINCIPLE)
        self.assertEqual(row["memory_class"], "PRINCIPLE_STOP")
        self.assertTrue(row["principle_layer_closed"])
        self.assertTrue(row["broader_core_principle_falsified"])

    def test_explicit_principle_stop_can_be_scoped_without_benchmark_death(self) -> None:
        p = self.payload()
        p["stop_class"] = "PRINCIPLE_STOP"
        p["benchmark_level_dead_end_certified"] = False
        row = classify_readjudication(p, "pace-bench-mechanism-redesign-principle-readjudication-20260818.json")
        self.assertEqual(row["failure_layer"], PRINCIPLE)
        self.assertEqual(row["memory_class"], "PRINCIPLE_STOP")
        self.assertTrue(row["principle_layer_closed"])
        self.assertFalse(row["broader_core_principle_falsified"])
        self.assertEqual(row["source_stop_class"], "PRINCIPLE_STOP")

    def test_same_information_scoped_closure_defaults_to_method_formulation(self) -> None:
        p = self.payload()
        p["broader_prompt_repetition_effect_falsified"] = False
        p["experiment_run_for_this_readjudication"] = True
        row = classify_readjudication(p, "evidence-echo-generic-repetition-principle-readjudication-20260817.json")
        self.assertEqual(row["failure_layer"], METHOD_FORMULATION)
        self.assertEqual(row["memory_class"], "METHOD_FORMULATION_STOP")
        self.assertFalse(row["broader_core_principle_falsified"])
        self.assertTrue(row["experiment_run_for_this_readjudication"])
        self.assertFalse(row["experiment_alone_authorizes_closure"])

    def test_known_measurement_bridge_failure_is_operationalization(self) -> None:
        row = classify_readjudication(
            self.payload("IMPOSSIBILITY_OR_INVARIANCE"),
            "p06-coverage-starvation-principle-readjudication-20260816.json",
        )
        self.assertEqual(row["failure_layer"], OPERATIONALIZATION_IDENTIFIABILITY)
        self.assertEqual(row["memory_class"], "OPERATIONALIZATION_IDENTIFIABILITY_STOP")

    def test_treatment_alignment_assumption_failure_is_scope(self) -> None:
        row = classify_readjudication(
            self.payload("NECESSARY_ASSUMPTION_REFUTED"),
            "static-procedural-prior-cross-regime-contradiction-principle-readjudication-20260817.json",
        )
        self.assertEqual(row["failure_layer"], ASSUMPTION_SCOPE)
        self.assertEqual(row["memory_class"], "ASSUMPTION_SCOPE_STOP")

    def test_upstream_collision_is_problem_novelty_stop(self) -> None:
        row = problem_novelty_classification(basis="unit-test")
        self.assertEqual(row["failure_layer"], PROBLEM_NOVELTY)
        self.assertEqual(row["memory_class"], "PROBLEM_NOVELTY_STOP")
        self.assertFalse(row["broader_core_principle_falsified"])
        self.assertFalse(row["experiment_run_for_this_readjudication"])


if __name__ == "__main__":
    unittest.main()
