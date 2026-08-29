from __future__ import annotations

import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARTIFACT = HERE / 'c1-r9-residual-alignment-preflight-20260829.json'


class C1R9ResidualAlignmentPreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.obj = json.loads(ARTIFACT.read_text(encoding='utf-8'))

    def test_preflight_is_zero_execution_and_hold_only(self) -> None:
        self.assertEqual(self.obj['status'], 'HOLD_REPRESENTATION_NOT_IDENTIFIED')
        self.assertEqual(self.obj['execution']['provider_calls'], 0)
        self.assertEqual(self.obj['execution']['model_actions'], 0)
        self.assertEqual(self.obj['execution']['new_outcomes_read'], 0)
        self.assertFalse(self.obj['execution']['sealed_23_state_holdout_consumed'])
        self.assertFalse(any(self.obj['authority'].values()))

    def test_source_geometry_is_frozen(self) -> None:
        self.assertEqual(self.obj['source_pairs'], 20)
        self.assertEqual(self.obj['parsed_memory_objects'], 40)
        self.assertEqual(self.obj['matched_item_pairs'], 58)
        self.assertEqual(self.obj['structural_asymmetry_pairs'], [118])

    def test_threshold_sweep_exposes_nonrobust_operationalization(self) -> None:
        rows = {round(row['threshold'], 2): row for row in self.obj['threshold_sweep']}
        self.assertEqual(rows[0.15]['source_pairs_fully_aligned'], 14)
        self.assertEqual(rows[0.20]['source_pairs_fully_aligned'], 6)
        self.assertEqual(rows[0.30]['source_pairs_fully_aligned'], 3)
        self.assertEqual(rows[0.35]['source_pairs_fully_aligned'], 0)
        self.assertEqual(rows[0.50]['matched_items_above_threshold'], 0)

    def test_failure_layer_does_not_falsify_c1_principle(self) -> None:
        adj = self.obj['adjudication']
        self.assertEqual(adj['failure_layer'], 'representation_operationalization')
        self.assertEqual(adj['scientific_principle_update'], 'NONE')
        self.assertIn('Do not choose a lexical similarity threshold', adj['forbidden_next_step'])
        self.assertIn('independently justified and frozen residual representation', adj['reopen_condition'])


if __name__ == '__main__':
    unittest.main()
