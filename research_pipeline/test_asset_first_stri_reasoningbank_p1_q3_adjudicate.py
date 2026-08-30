from __future__ import annotations

import copy
import unittest

from research_pipeline.asset_first_stri_reasoningbank_p1_core import BASE_URL, MODEL
from research_pipeline.asset_first_stri_reasoningbank_p1_q3_adjudicate import (
    paired_invariants,
    summarize_run,
)


def synthetic_run(*, resolved: bool, content: str = "task") -> dict:
    return {
        "run_id": "q3-example-A",
        "instance_id": "example",
        "failure": None,
        "R1_model_visible_requests": [{
            "model": MODEL,
            "input": [
                {"role": "system", "content": "system"},
                {"role": "user", "content": content},
            ],
            "temperature": 0.0,
            "store": True,
        }],
        "model_responses": [{"resolved_model": MODEL}],
        "provider": {
            "model": MODEL,
            "base_url": BASE_URL,
            "temperature": 0.0,
            "max_output_tokens": "omitted",
            "seed": "omitted",
            "top_p": "omitted",
        },
        "runtime": {
            "pid_namespace": "host",
            "platform": "linux/amd64",
            "receipt": {"base_commit_receipt": {"returncode": 0}},
        },
        "R4_terminal_outcome": {"valid": True, "resolved": resolved},
        "scientific_boundary": {
            "gold_patch_model_visible": False,
            "test_patch_model_visible": False,
            "evaluator_script_model_visible": False,
        },
        "selected_memory": "memory",
    }


def receipt() -> dict:
    return {
        "ordinal": 1,
        "selection_rank": 5,
        "instance_id": "example",
        "arm": "A",
        "run_id": "q3-example-A",
        "file_sha256": "0" * 64,
    }


class ReasoningBankP1Q3AdjudicationTest(unittest.TestCase):
    def test_negative_task_outcome_does_not_fail_implementation(self) -> None:
        summary = summarize_run(receipt(), synthetic_run(resolved=False))
        self.assertTrue(summary["implementation_pass"])
        self.assertFalse(summary["resolved"])
        self.assertFalse(summary["task_outcome_affects_implementation_qualification"])

    def test_blank_model_visible_content_fails_implementation(self) -> None:
        summary = summarize_run(receipt(), synthetic_run(resolved=True, content=""))
        self.assertFalse(summary["implementation_pass"])
        self.assertFalse(summary["checks"]["no_blank_model_visible_request_content"])

    def test_pair_invariants_require_equal_memory_and_first_request(self) -> None:
        base = summarize_run(receipt(), synthetic_run(resolved=False))
        rows = []
        for arm in ("A", "B", "C", "D", "E"):
            row = copy.deepcopy(base)
            row["arm"] = arm
            row["run_id"] = f"q3-example-{arm}"
            rows.append(row)
        checks = paired_invariants(rows)["example"]
        self.assertTrue(all(checks.values()))
        rows[-1]["selected_memory"] = "changed"
        self.assertFalse(paired_invariants(rows)["example"]["B_E_selected_memory_equal"])


if __name__ == "__main__":
    unittest.main()
