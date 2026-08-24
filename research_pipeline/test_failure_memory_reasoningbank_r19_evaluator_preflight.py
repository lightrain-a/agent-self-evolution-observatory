from __future__ import annotations

import unittest

from research_pipeline.failure_memory_reasoningbank_r19_evaluator_preflight import normalize_eval, semantic_config_equal


class TestR19EvaluatorPreflight(unittest.TestCase):
    def test_fuzzy_scalar_and_singleton_list_normalize_equal(self):
        a = {"reference_answers": {"fuzzy_match": ["N/A"]}, "string_note": "same"}
        b = {"reference_answers": {"fuzzy_match": "N/A"}, "string_note": "same"}
        self.assertEqual(normalize_eval(a), normalize_eval(b))

    def test_reference_truth_change_does_not_normalize_away(self):
        a = {"reference_answers": {"fuzzy_match": ["N/A"]}}
        b = {"reference_answers": {"fuzzy_match": "different"}}
        self.assertNotEqual(normalize_eval(a), normalize_eval(b))

    def test_semantic_config_requires_task_and_intent_identity(self):
        base = {
            "task_id": 24,
            "intent_template_id": 222,
            "intent": "x",
            "sites": ["shopping"],
            "start_url": "__SHOPPING__",
            "geolocation": None,
            "eval": {"eval_types": ["string_match"], "reference_answers": {"fuzzy_match": "N/A"}},
        }
        other = dict(base)
        other["intent"] = "changed"
        self.assertFalse(semantic_config_equal(base, other))


if __name__ == "__main__":
    unittest.main()
