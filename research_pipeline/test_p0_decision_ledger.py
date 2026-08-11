from __future__ import annotations
import unittest
from .human_terminal_state import build_human_terminal_state
from .p0_admission import build_p0_admission_state
from .p0_decision_ledger import build_p0_decision_ledger
from .p0_offline_qualification import build_p0_offline_qualification_state

class P0DecisionLedgerTest(unittest.TestCase):
 def test_ledger_collapses_plans_to_current_decisions(self):
  state=build_p0_decision_ledger(build_p0_admission_state(),build_p0_offline_qualification_state(),build_human_terminal_state())
  self.assertEqual(state['summary']['active_p0'],20)
  self.assertEqual(state['summary']['launchable'],0)
  self.assertGreaterEqual(state['summary']['experiment_stopped'],16)
  by={r['idea_id']:r for r in state['rows']}
  self.assertEqual(by['active-causal-minimal-rollback']['current_state'],'experiment-stop-await-human-review')
  self.assertEqual(by['active-causal-minimal-rollback']['economy_stop_class'],'matched-simplification')
  self.assertEqual(by['regression-gated-self-evolution']['economy_stop_class'],'substrate')
  for row in state['rows']:
   if row['p0_decision'] or row['economy_stop_class']:
    self.assertEqual(row['current_state'],'experiment-stop-await-human-review')
  self.assertTrue(state['policy']['economy_stop_overrides_planned_registry_display'])

if __name__=='__main__': unittest.main()
