from __future__ import annotations
import unittest
from .human_terminal_state import build_human_terminal_state
from .p0_admission import build_p0_admission_state
from .p0_decision_ledger import build_p0_decision_ledger
from .p0_offline_qualification import build_p0_offline_qualification_state
from .p0_four_direction_iteration import build_four_direction_iteration

class P0DecisionLedgerTest(unittest.TestCase):
 def test_ledger_collapses_plans_to_current_decisions(self):
  state=build_p0_decision_ledger(build_p0_admission_state(),build_p0_offline_qualification_state(),build_human_terminal_state())
  self.assertEqual(state['summary']['active_p0'],31)
  self.assertEqual(state['summary']['launchable'],0)
  self.assertGreaterEqual(state['summary']['experiment_stopped'],20)
  self.assertEqual(state['summary']['economy_blocked'],0)
  self.assertEqual(state['summary']['method_admission_blocked'],2)
  self.assertEqual(state['summary']['upstream_hold'],2)
  by={r['idea_id']:r for r in state['rows']}
  self.assertEqual(by['active-causal-minimal-rollback']['current_state'],'experiment-stop-await-human-review')
  self.assertEqual(by['active-causal-minimal-rollback']['economy_stop_class'],'matched-simplification')
  self.assertEqual(by['regression-gated-self-evolution']['economy_stop_class'],'substrate')
  for row in state['rows']:
   if row['p0_decision'] or row['economy_stop_class']=='matched-simplification':
    self.assertEqual(row['current_state'],'experiment-stop-await-human-review')
   elif row['economy_stop_class']=='substrate':
    self.assertEqual(row['current_state'],'upstream-hold')
  self.assertTrue(state['policy']['economy_stop_overrides_planned_registry_display'])
 def test_latest_four_direction_iteration_overrides_experiment_decision_not_lifecycle(self):
  state=build_p0_decision_ledger(build_p0_admission_state(),build_p0_offline_qualification_state(),build_human_terminal_state(),build_four_direction_iteration())
  by={r['idea_id']:r for r in state['rows']}
  self.assertEqual(by['update-trust-region']['current_state'],'experiment-merge')
  self.assertEqual(by['budgeted-evolution-controller']['current_state'],'upstream-hold')
  self.assertEqual(by['replicated-effect-memory-gate']['current_state'],'experiment-merge')
  self.assertEqual(by['cross-task-effect-transport-certificate']['current_state'],'method-development-stop')
  self.assertEqual(by['cross-task-effect-transport-certificate']['lifecycle'],'p0')
  self.assertEqual(state['summary']['latest_iteration_overrides'],4)
  self.assertEqual(state['summary']['upstream_hold'],3)
  self.assertEqual(state['summary']['method_admission_blocked'],2)
  self.assertEqual(state['summary']['launchable'],0)

if __name__=='__main__': unittest.main()
