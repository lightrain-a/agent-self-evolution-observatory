from __future__ import annotations

import unittest

from research_pipeline.asset_first_stri_reasoningbank_p1_q4_prepare import (
    CONTRACT,
    EXPECTED_IDENTITIES,
    validate_existing,
    verify_preoutcome_inputs,
)


class ReasoningBankP1Q4PrepareTest(unittest.TestCase):
    def test_q3_runtime_hold_is_bound_without_task_outcome(self) -> None:
        checks = verify_preoutcome_inputs()
        self.assertTrue(all(row["pass"] for row in checks.values()))
        self.assertEqual(
            checks["same_unrun_q3_identities"]["actual"],
            EXPECTED_IDENTITIES,
        )
        self.assertTrue(checks["q3_runtime_hold_was_outcome_blind"]["pass"])
        self.assertTrue(checks["no_q3_model_execution_artifacts"]["pass"])

    def test_existing_contract_is_preoutcome_and_exact(self) -> None:
        self.assertTrue(CONTRACT.exists())
        self.assertEqual(validate_existing(), [])


if __name__ == "__main__":
    unittest.main()
