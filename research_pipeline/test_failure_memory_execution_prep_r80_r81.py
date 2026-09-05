from __future__ import annotations
import copy, json, pathlib, unittest
from fractions import Fraction
try:
 from . import failure_memory_scale_validation_r80 as r80
 from . import failure_memory_semantic_control_r81_execution_prep as r81
except ImportError:
 import failure_memory_scale_validation_r80 as r80  # type: ignore
 import failure_memory_semantic_control_r81_execution_prep as r81  # type: ignore

ROOT=pathlib.Path(__file__).resolve().parents[1]

def load(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))

class FailureMemoryExecutionPrepR80R81Tests(unittest.TestCase):
 def setUp(self):
  self.panel=load('generated/d2-failure-memory-provenance-r68-semantic-control-panel.json')
  self.protocol=load('generated/d2-failure-memory-provenance-r72-semantic-control-r3-protocol.json')
  self.parent=load('generated/d2-failure-memory-provenance-r53-full350-source-execution-manifest.json')
  self.freeze=load('generated/d2-failure-memory-provenance-r80-strong-scale-outcome-blind-freeze.json')
  self.manifest=load('generated/d2-failure-memory-provenance-r81-qwen-path-equivalent-execution-manifest.json')
  self.authority=load('generated/d2-failure-memory-provenance-r81-qwen-stage-execution-authority.json')
 def test_receipts(self):
  self.assertTrue(r80.valid(self.freeze)); self.assertTrue(r80.valid(self.panel)); self.assertTrue(r80.valid(self.protocol)); self.assertTrue(r81.valid(self.manifest)); self.assertTrue(r81.valid(self.authority))
 def test_strong_model_identity_is_exact_and_outcome_blind(self):
  m=self.freeze['strong_model']; self.assertEqual(m['repository'],'Qwen/Qwen2.5-32B-Instruct'); self.assertEqual(m['revision'],r80.MODEL_REVISION); self.assertEqual(m['decoding'],{'temperature':0.0,'do_sample':False,'max_new_tokens':512}); self.assertEqual(self.freeze['outcomes_observed_during_freeze'],0); self.assertFalse(self.freeze['authority']['strong_model_execution'])
 def test_scale_trigger_and_control_rule(self):
  t=self.freeze['trigger']; self.assertTrue(t['requires_complete_PT_classification_for_all_66_tasks_on_both_executors']); self.assertEqual(t['D_zero_action'],'DO_NOT_RUN_STRONG_SCALE_CHECK'); self.assertEqual(t['technical_missing_action'],'HOLD_STRONG_SCALE_CHECK_NO_AUTOMATIC_PANEL'); self.assertFalse(self.freeze['matching']['manual_override_allowed']); self.assertTrue(self.freeze['matching']['without_replacement']); self.assertEqual(self.freeze['strong_stage']['trajectory_count_formula'],'4D = (D discordant + D matched concordant controls) x 2 arms')
 def test_matching_is_deterministic_without_replacement(self):
  ids=[str(x) for x in self.panel['representative_ids']]; discord=ids[:3]; controls=ids[3:]
  a=r80.select_controls(self.panel,discord,controls); b=r80.select_controls(self.panel,discord,controls)
  self.assertEqual(a,b); self.assertEqual(len({x['matched_control_task_id'] for x in a}),3)
 def test_classification_uses_union_of_executor_discordance(self):
  ids=[str(x) for x in self.panel['representative_ids'][:3]]
  def rows(patterns):
   out=[]
   for tid,(p,t) in zip(ids,patterns):
    out += [{'task_id':tid,'arm':'P_neutral','terminal_success':p},{'task_id':tid,'arm':'T_truthful','terminal_success':t}]
   return out
  q=rows([(True,False),(True,True),(False,False)]); l=rows([(True,True),(False,True),(False,False)])
  d,c=r80.classify(q,l,ids); self.assertEqual(d,ids[:2]); self.assertEqual(c,[ids[2]])
 def test_path_equivalent_manifest_changes_only_checkout_plus_metadata(self):
  p=copy.deepcopy(self.parent); m=copy.deepcopy(self.manifest)
  self.assertEqual(m['execution_manifest']['source']['revision'],p['execution_manifest']['source']['revision'])
  self.assertEqual(m['execution_manifest']['source']['pinned_source_file_sha256'],p['execution_manifest']['source']['pinned_source_file_sha256'])
  self.assertNotEqual(m['execution_manifest']['source']['checkout'],p['execution_manifest']['source']['checkout'])
  for k in ['models','runtime_image','external_runtime_adapter','source_build']:
   self.assertEqual(m['execution_manifest'][k],p['execution_manifest'][k])
 def test_authority_is_qwen_only(self):
  a=self.authority['authority']; self.assertTrue(a['qwen_execution']); self.assertTrue(a['gpu']); self.assertFalse(a['llama_execution']); self.assertFalse(a['analysis']); self.assertFalse(a['PSMG']); self.assertFalse(a['L3']); self.assertFalse(a['paper_claim_change']); self.assertFalse(a['strong_model_execution'])
  self.assertEqual(self.authority['scope']['planned_stage_trajectories'],189); self.assertTrue(self.authority['scope']['Llama_stage_requires_separate_successor_authority'])

if __name__=='__main__': unittest.main()
