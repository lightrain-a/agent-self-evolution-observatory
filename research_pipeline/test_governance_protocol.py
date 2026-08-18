from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
from .governance_protocol import STOP_CLASSES,build_governance_state,evaluate_stage_contract,infer_stage,record_repair

class GovernanceProtocolTest(unittest.TestCase):
 def test_stage_mapping_and_support_gate(self):
  self.assertEqual(infer_stage({'phase':'P0-screening'}),'p0-support')
  self.assertEqual(infer_stage({'phase':'P0'}),'p0-method')
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); cfg={'phase':'P0','governance':{'substrate_id':'mem','support_evidence':'support.json'}}
   blocked=evaluate_stage_contract('idea',cfg,root); self.assertFalse(blocked['execution_authorized'])
   (root/'support.json').write_text(json.dumps({'status':'CONSENSUS_SUPPORT_PASS'}))
   passed=evaluate_stage_contract('idea',cfg,root); self.assertTrue(passed['execution_authorized'])
 def test_p0_support_requires_frozen_f0_evidence(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); cfg={'phase':'P0-screening','governance':{'substrate_id':'prompt','f0_evidence':'f0.json'}}
   self.assertFalse(evaluate_stage_contract('idea',cfg,root)['execution_authorized'])
   (root/'f0.json').write_text(json.dumps({'pass':True}))
   self.assertTrue(evaluate_stage_contract('idea',cfg,root)['execution_authorized'])
 def test_repair_budget_stops_third_load_bearing_repair(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); (root/'f0.json').write_text(json.dumps({'pass':True})); cfg={'phase':'P0-screening','governance':{'substrate_id':'prompt','f0_evidence':'f0.json'}}
   record_repair(root,'idea','prompt','representation','r1')
   self.assertTrue(evaluate_stage_contract('idea',cfg,root)['execution_authorized'])
   record_repair(root,'idea','prompt','objective','r2')
   row=evaluate_stage_contract('idea',cfg,root); self.assertFalse(row['execution_authorized']); self.assertTrue(row['repair_budget']['exhausted'])

 def test_stop_taxonomy_only_principle_is_persistent_dead_end(self):
  state=build_governance_state()
  self.assertEqual(set(state["stop_classes"]),{"REALIZATION_STOP","SUPPORT_STOP","PROTOCOL_STOP","PRINCIPLE_STOP"})
  self.assertFalse(STOP_CLASSES["REALIZATION_STOP"]["persistent_dead_end_authority"])
  self.assertFalse(STOP_CLASSES["SUPPORT_STOP"]["persistent_dead_end_authority"])
  self.assertFalse(STOP_CLASSES["PROTOCOL_STOP"]["persistent_dead_end_authority"])
  self.assertTrue(STOP_CLASSES["PRINCIPLE_STOP"]["persistent_dead_end_authority"])
  self.assertTrue(state["policy"]["stop_class_required_for_any_stop"])
  self.assertTrue(state["policy"]["only_principle_stop_may_enter_persistent_dead_end_memory"])

if __name__=='__main__': unittest.main()
