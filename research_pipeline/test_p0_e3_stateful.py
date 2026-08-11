from __future__ import annotations
import json, unittest
from .config import PROJECT_ROOT
from .p0_e3_stateful import _hash

class P0E3StatefulTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state=json.loads((PROJECT_ROOT/'generated'/'p0-e3-stateful.json').read_text(encoding='utf-8'))
    def test_prediction_freeze_and_independent_truth(self):
        self.assertTrue(self.state['design']['prediction_frozen_before_hidden'])
        self.assertTrue(self.state['design']['cross_operation_hidden_recovery'])
        self.assertEqual(_hash(self.state['predictions']),self.state['prediction_sha256_before_hidden'])
        self.assertEqual(self.state['design']['independent_truth'],'executable state snapshots')
        fair=self.state['baseline_fairness']
        self.assertTrue(fair['same_target_probe_budget'] and fair['same_typed_pex_representation'] and fair['same_hidden_cases'])
        self.assertFalse(fair['hidden_truth_used_before_prediction'])
        hidden={row['name'] for rows in self.state['hidden_rows'].values() for row in rows}
        self.assertIn('h-stale-delete',hidden); self.assertIn('h-missing-update',hidden)
    def test_stateful_deterministic_ceiling_fires_stop(self):
        m=self.state['metrics']
        self.assertEqual(m['total_hidden'],12); self.assertEqual(m['correct_hidden'],12)
        self.assertEqual(m['stateful_semantic_accuracy'],1.0)
        self.assertEqual(m['family_accuracy'],{'ledger':1.0,'vault':1.0})
        self.assertEqual(self.state['decision'],'STOP_STATEFUL_DETERMINISTIC_PEX_CEILING')
        self.assertTrue(self.state['standalone_claim_stop_authorized'])
        self.assertFalse(self.state['learned_arm_run'])

if __name__=='__main__': unittest.main()
