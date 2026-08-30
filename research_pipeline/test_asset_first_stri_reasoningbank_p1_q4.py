from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from research_pipeline.asset_first_stri_reasoningbank_p1_core import DockerRun
from research_pipeline.asset_first_stri_reasoningbank_p1_q4 import (
    ARMS,
    CONTRACT,
    MODEL,
    load_payload,
    planned_cases,
    run_q4,
    verify_q4_inputs,
)


class ReasoningBankP1Q4ExecutionTest(unittest.TestCase):
    def test_preoutcome_inputs_and_contract_verify(self) -> None:
        checks = verify_q4_inputs(require_acquisition=False)
        self.assertTrue(checks["q4_identity_order"]["pass"])
        self.assertTrue(checks["treatment_hashes"]["pass"])
        self.assertTrue(checks["preoutcome_contract"]["pass"])
        self.assertTrue(checks["official_parser_qualification"]["pass"])
        self.assertTrue(checks["q3_runtime_hold_preserved"]["pass"])
        contract = load_payload(CONTRACT)
        self.assertEqual(contract["outcome_discipline"]["q3_model_run_count"], 0)
        self.assertFalse(
            contract["outcome_discipline"]["q3_task_outcome_observed"]
        )
        self.assertEqual(
            contract["runtime_normalization"]["action"],
            "git reset --hard <frozen expected base commit>",
        )

    def test_execution_order_and_model_are_frozen(self) -> None:
        cases = planned_cases()
        self.assertEqual(len(cases), 10)
        self.assertEqual(
            [(row["selection_rank"], row["instance_id"], row["arm"]) for row in cases],
            [
                *[(5, "sphinx-doc__sphinx-9230", arm) for arm in ARMS],
                *[(6, "django__django-11880", arm) for arm in ARMS],
            ],
        )
        self.assertEqual(MODEL, "deepseek-v4-pro-ga-260813")

    @patch("research_pipeline.asset_first_stri_reasoningbank_p1_core.run_host")
    def test_exact_base_normalization_is_scoped_and_receipted(
        self, run_host: Mock,
    ) -> None:
        base = "a" * 40
        run_host.side_effect = [
            {"returncode": 0, "output": '["image@sha256:digest"] amd64'},
            {"returncode": 0, "output": "container-id"},
            {"returncode": 0, "output": "container-name"},
        ]
        container = DockerRun("image@sha256:digest", base, "q4-test", exact_base=True)
        container.exec = Mock(side_effect=[
            {"returncode": 0, "output": "b" * 40},
            {"returncode": 0, "output": f"HEAD is now at {base} frozen"},
            {"returncode": 0, "output": base},
        ])
        receipt = container.start()["base_commit_receipt"]
        self.assertEqual(receipt["rule"], "exact_base_after_preregistered_hard_reset")
        self.assertEqual(receipt["expected_base_commit"], base)
        self.assertEqual(receipt["observed_head"], base)
        self.assertFalse(receipt["git_clean_invoked"])
        self.assertIn(
            f"git reset --hard {base}",
            container.exec.call_args_list[1].args[0],
        )
        container.created = False

    def test_existing_index_forbids_second_invocation_before_any_call(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            index = Path(directory) / "existing.json"
            index.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "second Q4 invocation"):
                run_q4(index_path=index, output_dir=Path(directory) / "runs")


if __name__ == "__main__":
    unittest.main()
