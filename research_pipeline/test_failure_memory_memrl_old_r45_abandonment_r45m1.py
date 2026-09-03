from __future__ import annotations

import copy
import unittest

from .failure_memory_memrl_old_r45_abandonment_r45m1 import (
    build,
    validate,
    verify_frozen_evidence,
)


class OldR45AbandonmentTests(unittest.TestCase):
    def test_frozen_evidence_and_receipt_pass(self) -> None:
        frozen = verify_frozen_evidence()
        self.assertEqual(
            frozen["file_sha256"]["generated/d2-failure-memory-provenance-r43-memrl-g8-execution-manifest.json"],
            "dbd810dce063f5bdaaf7c40038a3329166f8ad11441dd11b49034491bf753de2",
        )
        row = build()
        self.assertEqual(validate(row), [])
        self.assertEqual(row["confirmatory_outcomes_observed_by_this_receipt"], 0)

    def test_unknown_cannot_be_reclassified(self) -> None:
        row = build()
        row["adjudication"]["unknown_reclassified_as_not_started"] = True
        self.assertIn("old-state-overreach", validate(row))

    def test_old_output_cannot_be_admitted(self) -> None:
        row = build()
        row["adjudication"]["old_lineage_admissible_in_new_analysis"] = True
        self.assertIn("old-state-overreach", validate(row))

    def test_receipt_hash_detects_mutation(self) -> None:
        row = build()
        changed = copy.deepcopy(row)
        changed["replacement"]["old_artifact_pooling"] = True
        self.assertIn("receipt-hash", validate(changed))


if __name__ == "__main__":
    unittest.main()
