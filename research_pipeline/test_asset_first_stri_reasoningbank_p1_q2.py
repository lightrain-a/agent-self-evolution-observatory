from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from research_pipeline.asset_first_stri_reasoningbank_p1_q2 import (
    ARMS,
    CONTRACT,
    MODEL,
    load_payload,
    planned_cases,
    run_q2,
    verify_q2_inputs,
)


class ReasoningBankP1Q2ExecutionTest(unittest.TestCase):
    def test_preoutcome_inputs_and_contract_verify(self) -> None:
        checks = verify_q2_inputs(require_acquisition=False)
        self.assertTrue(checks["q2_identity_order"]["pass"])
        self.assertTrue(checks["treatment_hashes"]["pass"])
        self.assertTrue(checks["preoutcome_contract"]["pass"])
        self.assertFalse(
            load_payload(CONTRACT)["scientific_boundary"]["q2_task_outcome_observed"]
        )

    def test_execution_order_and_model_are_frozen(self) -> None:
        cases = planned_cases()
        self.assertEqual(len(cases), 10)
        self.assertEqual(
            [(row["selection_rank"], row["instance_id"], row["arm"]) for row in cases],
            [
                *[(3, "django__django-16100", arm) for arm in ARMS],
                *[(4, "sympy__sympy-18211", arm) for arm in ARMS],
            ],
        )
        self.assertEqual(MODEL, "deepseek-v4-pro-ga-260813")

    def test_existing_index_forbids_second_invocation_before_any_call(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            index = Path(directory) / "existing.json"
            index.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "second Q2 invocation"):
                run_q2(index_path=index, output_dir=Path(directory) / "runs")


if __name__ == "__main__":
    unittest.main()
