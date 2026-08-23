from __future__ import annotations

import copy
import unittest

from research_pipeline.failure_memory_reasoningbank_status_l2_preflight import build_cohort


def cfg(tid: str, template: str, eval_types: list[str] | None = None) -> dict:
    return {
        "task_id": int(tid),
        "intent_template_id": int(template),
        "eval": {"eval_types": eval_types or []},
    }


def rec(tid: str, prompt: str, success: bool) -> dict:
    return {
        "task_id": tid,
        "task_prompt": prompt,
        "is_successful": success,
        "trajectory_json": '{"steps": {}}',
    }


class TestReasoningBankStatusL2Preflight(unittest.TestCase):
    def test_one_downstream_per_template_and_prior_source_preferred(self) -> None:
        records = [
            rec("1", "source prior", False),
            rec("2", "fresh A", True),
            rec("3", "fresh B", False),
            rec("10", "source other", True),
            rec("11", "fresh C", False),
        ]
        configs = [
            cfg("1", "100", ["string_match"]),
            cfg("2", "100", ["url_match"]),
            cfg("3", "100", ["string_match"]),
            cfg("10", "200", ["string_match"]),
            cfg("11", "200", ["program_html"]),
        ]
        cohort = build_cohort(records, configs, prior_ids=frozenset({"1"}))
        self.assertEqual([x["downstream_task_id"] for x in cohort], ["2", "10"])
        self.assertEqual([x["source_task_id"] for x in cohort], ["1", "11"])
        self.assertTrue(cohort[0]["source_task_was_prior_d2"])
        self.assertFalse(cohort[1]["source_task_was_prior_d2"])

    def test_downstream_outcome_flip_does_not_change_ids(self) -> None:
        records = [
            rec("1", "source", False),
            rec("2", "fresh A", True),
            rec("3", "fresh B", False),
        ]
        configs = [cfg("1", "100", ["string_match"]), cfg("2", "100", ["url_match"]), cfg("3", "100", ["string_match"])]
        a = build_cohort(records, configs, prior_ids=frozenset({"1"}))
        flipped = copy.deepcopy(records)
        for row in flipped:
            row["is_successful"] = not row["is_successful"]
        b = build_cohort(flipped, configs, prior_ids=frozenset({"1"}))
        self.assertEqual(
            [(x["template_id"], x["downstream_task_id"], x["source_task_id"]) for x in a],
            [(x["template_id"], x["downstream_task_id"], x["source_task_id"]) for x in b],
        )

    def test_no_evaluator_or_no_second_task_means_no_unit(self) -> None:
        records = [rec("1", "only task", True), rec("2", "no eval", False), rec("3", "source for no eval", True)]
        configs = [cfg("1", "100", ["string_match"]), cfg("2", "200", []), cfg("3", "200", ["string_match"])]
        cohort = build_cohort(records, configs, prior_ids=frozenset())
        # Template 100 has no distinct source. Template 200 chooses task 3 as
        # downstream but can use task 2 as source even though source eval is empty.
        self.assertEqual(len(cohort), 1)
        self.assertEqual(cohort[0]["downstream_task_id"], "3")
        self.assertEqual(cohort[0]["source_task_id"], "2")

    def test_unparseable_trajectory_is_not_eligible(self) -> None:
        records = [rec("1", "bad", True), rec("2", "good", False), rec("3", "source", True)]
        records[0]["trajectory_json"] = "not-json"
        configs = [cfg("1", "100", ["string_match"]), cfg("2", "100", ["string_match"]), cfg("3", "100", ["string_match"])]
        cohort = build_cohort(records, configs, prior_ids=frozenset())
        self.assertEqual(cohort[0]["downstream_task_id"], "2")
        self.assertEqual(cohort[0]["source_task_id"], "3")


if __name__ == "__main__":
    unittest.main()
