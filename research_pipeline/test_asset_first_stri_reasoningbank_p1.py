from __future__ import annotations

import json
import unittest
from pathlib import Path

from research_pipeline.asset_first_stri_reasoningbank_p1 import (
    source_failure_blocks_induction,
    treatment_cases,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    BASE_STATE_RULE,
    FIXTURE_PATH,
    MEMORY_PREFIX,
    PID_NAMESPACE,
    load_agent_default,
    load_config,
    render_messages,
    render_timeout_observation,
    append_nonempty_assistant_message,
    verify_frozen_inputs,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_eval import (
    parse_pytest,
    parse_sympy,
)


class ReasoningBankP1FrozenRuntimeTest(unittest.TestCase):
    def test_frozen_inputs_and_official_runtime_parameters(self) -> None:
        checks = verify_frozen_inputs()
        self.assertTrue(all(row["pass"] for row in checks.values()))
        config = load_config()
        self.assertEqual(config["agent"]["step_limit"], 250)
        self.assertEqual(float(config["agent"]["cost_limit"]), 3.0)
        self.assertEqual(config["environment"]["timeout"], 60)
        self.assertEqual(config["model"]["model_kwargs"]["temperature"], 0.0)
        self.assertEqual(PID_NAMESPACE, "host")
        self.assertEqual(BASE_STATE_RULE, "exact_or_clean_tree_equivalent_descendant")

    def test_empty_provider_output_is_not_replayed_as_illegal_assistant_content(self) -> None:
        messages = [{"role": "user", "content": "continue"}]
        self.assertFalse(append_nonempty_assistant_message(messages, ""))
        self.assertEqual(messages, [{"role": "user", "content": "continue"}])
        self.assertTrue(append_nonempty_assistant_message(messages, "visible"))
        self.assertEqual(messages[-1], {"role": "assistant", "content": "visible"})

    def test_provider_and_implementation_failures_block_source_induction(self) -> None:
        for layer in ("provider", "provider_identity", "implementation"):
            self.assertTrue(source_failure_blocks_induction({"failure": {"failure_layer": layer}}))
        self.assertFalse(source_failure_blocks_induction({"failure": None}))

    def test_timeout_uses_nonempty_frozen_agent_default_when_yaml_omits_it(self) -> None:
        config = load_config()
        self.assertNotIn("timeout_template", config["agent"])
        official = load_agent_default("timeout_template")
        visible = render_timeout_observation(config, "sleep 61", "partial output")
        self.assertEqual(visible, __import__("jinja2").Template(official).render(
            action={"action": "sleep 61"}, output="partial output"
        ))
        self.assertIn("timed out and has been killed", visible)
        self.assertTrue(visible.strip())

    def test_memory_is_appended_to_official_system_message_only(self) -> None:
        without = render_messages("task")
        with_memory = render_messages("task", "piece one\n\npiece two")
        self.assertEqual(without[1], with_memory[1])
        self.assertEqual(
            with_memory[0]["content"],
            without[0]["content"] + MEMORY_PREFIX + "piece one\n\npiece two",
        )

    def test_evaluator_only_fields_never_enter_rendered_request(self) -> None:
        fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["fixtures"]
        for fixture in fixtures:
            serialized = json.dumps(
                render_messages(fixture["model_visible"]["problem_statement"]),
                ensure_ascii=False,
            )
            self.assertNotIn(fixture["evaluator_only"]["test_patch"], serialized)
            self.assertNotIn(fixture["evaluator_only"]["eval_script"], serialized)


class ReasoningBankP1TreatmentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.memory = {
            "case_id": "source-case",
            "raw_input": "source query",
            "semantic_memory_items": ["piece 1", "piece 2", "piece 3"],
        }

    def test_a_b_native_reunion_and_e_placebo_are_model_visible_equal(self) -> None:
        rows = treatment_cases(self.memory)
        self.assertEqual(rows["A"]["selected_memory"], rows["B"]["selected_memory"])
        self.assertEqual(rows["B"]["selected_memory"], rows["E"]["selected_memory"])
        self.assertNotEqual(rows["A"]["cases"][0]["task_id"], rows["E"]["cases"][0]["task_id"])

    def test_c_reverses_and_d_top_one_loses_cross_case_fragments(self) -> None:
        rows = treatment_cases(self.memory)
        self.assertEqual(rows["C"]["selected_memory"], "piece 3\n\npiece 2\n\npiece 1")
        self.assertEqual(rows["D"]["selected_memory"], "piece 1")
        self.assertTrue(rows["D"]["R0"]["retrieval_scores"]["all_eligible_scores_equal"])
        self.assertEqual(rows["D"]["R0"]["selected_case"], "source-case::cross-1")

    def test_treatment_hashes_are_distinct_except_model_visible_equivalences(self) -> None:
        rows = treatment_cases(self.memory)
        hashes = [rows[arm]["treatment_sha256"] for arm in "ABCDE"]
        self.assertEqual(len(set(hashes)), 5)


class ReasoningBankP1ContractTest(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def test_preregistration_is_preoutcome_and_full_p1_closed(self) -> None:
        contract = json.loads(
            (self.ROOT / "generated/asset-first-stri-reasoningbank-p1-minimal-pilot-contract-20260829.json").read_text(encoding="utf-8")
        )
        blinded = contract["selection_and_outcome_blinding"]
        self.assertFalse(blinded["source_induction_executed"])
        self.assertFalse(blinded["pilot_task_outcome_observed"])
        self.assertEqual(contract["minimal_pilot_rule"]["planned_runs"], 10)
        self.assertFalse(contract["authorization"]["full_p1"])

    def test_contract_freezes_disjoint_tasks_and_all_five_arms(self) -> None:
        contract = json.loads(
            (self.ROOT / "generated/asset-first-stri-reasoningbank-p1-minimal-pilot-contract-20260829.json").read_text(encoding="utf-8")
        )
        population = contract["task_population"]
        source = {row["instance_id"] for row in population["source_cases"]}
        evaluation = {
            row["instance_id"] for row in population["minimal_pilot_evaluation_cases"]
        }
        self.assertTrue(source.isdisjoint(evaluation))
        self.assertEqual(set(contract["treatments"]) & set("ABCDE"), set("ABCDE"))


class ReasoningBankP1ParserTest(unittest.TestCase):
    def test_pytest_parser_matches_frozen_cases(self) -> None:
        parsed = parse_pytest(
            "PASSED testing/python/integration.py::ok\n"
            "FAILED testing/python/integration.py::bad - ValueError\n"
            "SKIPPED testing/python/integration.py::skip reason\n"
        )
        self.assertEqual(parsed["testing/python/integration.py::ok"], "PASSED")
        self.assertEqual(parsed["testing/python/integration.py::bad"], "FAILED")
        self.assertEqual(parsed["testing/python/integration.py::skip"], "SKIPPED")

    def test_sympy_parser_matches_official_verbose_output(self) -> None:
        parsed = parse_sympy("test_one ok\ntest_two F\ntest_three E\n")
        self.assertEqual(
            parsed, {"test_one": "PASSED", "test_two": "FAILED", "test_three": "ERROR"}
        )


if __name__ == "__main__":
    unittest.main()
