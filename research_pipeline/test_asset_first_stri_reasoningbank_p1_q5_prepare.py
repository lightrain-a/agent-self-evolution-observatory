from __future__ import annotations

import unittest

from research_pipeline.asset_first_stri_reasoningbank_p1_q5_prepare import (
    CANONICAL_LESSON,
    CONTRACT,
    DIFFERENTIAL,
    MANIFEST,
    MEMORY,
    SPHINX_AFTER,
    SPHINX_BEFORE,
    load_payload,
    validate_existing,
    verify_frozen_inputs,
)


class ReasoningBankP1Q5PrepareTest(unittest.TestCase):
    def test_frozen_q4_inputs_verify(self) -> None:
        checks = verify_frozen_inputs()
        self.assertTrue(all(row["pass"] for row in checks.values()))

    def test_q4_manifest_and_failure_differential_are_exact(self) -> None:
        manifest = load_payload(MANIFEST)
        differential = load_payload(DIFFERENTIAL)
        self.assertEqual(manifest["artifact_count"], 14)
        self.assertTrue(manifest["all_artifacts_sha256_verified"])
        self.assertEqual(
            differential["classification"]["primary_failure_layer"], "evaluator"
        )
        self.assertFalse(differential["classification"]["parser"])
        self.assertTrue(differential["classification"]["evaluator"])
        self.assertTrue(
            all(row["official_local_exact"] for row in differential["parser_replay"])
        )
        self.assertTrue(
            all(row["official_status_count"] == 0 for row in differential["parser_replay"])
        )

    def test_scientific_memory_preserves_no_belief_update(self) -> None:
        memory = load_payload(MEMORY)
        self.assertEqual(memory["canonical_lesson"], CANONICAL_LESSON)
        self.assertFalse(memory["scientific_authority"])
        self.assertFalse(memory["experiment_authority"])

    def test_q5_is_single_variable_and_execution_unauthorized(self) -> None:
        contract = load_payload(CONTRACT)
        self.assertEqual(len(contract["frozen_replay_sources"]), 10)
        self.assertEqual(contract["single_variable_repair"]["before"], SPHINX_BEFORE)
        self.assertEqual(contract["single_variable_repair"]["after"], SPHINX_AFTER)
        self.assertEqual(contract["single_variable_repair"]["model_calls"], 0)
        self.assertEqual(contract["single_variable_repair"]["provider_calls"], 0)
        self.assertFalse(
            contract["authorization"]["q5_replay_execution_authorized"]
        )
        self.assertFalse(contract["authorization"]["full_p1_execution_authorized"])
        sphinx = [
            row for row in contract["frozen_replay_sources"]
            if row["instance_id"] == "sphinx-doc__sphinx-9230"
        ]
        django = [
            row for row in contract["frozen_replay_sources"]
            if row["instance_id"] == "django__django-11880"
        ]
        self.assertTrue(all(row["evaluator_script_changed"] for row in sphinx))
        self.assertTrue(all(not row["evaluator_script_changed"] for row in django))
        self.assertEqual(validate_existing(), [])


if __name__ == "__main__":
    unittest.main()
