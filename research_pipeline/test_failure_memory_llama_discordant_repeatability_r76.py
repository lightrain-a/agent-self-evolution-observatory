from __future__ import annotations
import hashlib,json,pathlib,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
P=ROOT/'generated/d2-failure-memory-provenance-r76-llama-discordant-repeatability.json'

def load(): return json.loads(P.read_text(encoding='utf-8'))
def valid(x):
 r=x['receipt_sha256']; y=dict(x); y.pop('receipt_sha256')
 d=hashlib.sha256(json.dumps(y,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 return r==d

class LlamaDiscordantRepeatabilityR76Tests(unittest.TestCase):
 def setUp(self): self.x=load()
 def test_receipt_is_content_addressed(self): self.assertTrue(valid(self.x))
 def test_old_and_new_decoding_are_greedy(self):
  self.assertEqual(self.x['historical_binding']['temperature'],0.0)
  self.assertFalse(self.x['historical_binding']['do_sample'])
 def test_all_four_pair_patterns_reproduce(self):
  rows=self.x['task_results']; self.assertEqual([r['task_id'] for r in rows],['125','136','193','327'])
  self.assertTrue(all(r['pair_pattern_reproduced'] for r in rows))
  self.assertEqual(self.x['aggregate_repeatability']['terminal_arm_outcomes_reproduced'],'8/8')
  self.assertEqual(self.x['aggregate_repeatability']['terminal_pair_patterns_reproduced'],'4/4')
 def test_first_actions_are_fully_reproduced(self):
  self.assertEqual(self.x['aggregate_repeatability']['first_executable_actions_reproduced'],'8/8')
  self.assertTrue(all(all(r['first_action_reproduced_A_B']) for r in self.x['task_results']))
 def test_only_193A_has_full_path_variation(self):
  by={r['task_id']:r for r in self.x['task_results']}
  self.assertEqual(self.x['aggregate_repeatability']['full_normalized_action_sequences_reproduced'],'7/8')
  self.assertEqual(by['193']['full_normalized_action_sequence_reproduced_A_B'],[False,True])
  self.assertEqual(by['193']['A_common_normalized_action_prefix_steps'],6)
  self.assertEqual(by['193']['historical_steps_A_B'],[10,6])
  self.assertEqual(by['193']['rerun_steps_A_B'],[8,6])
 def test_phase2_not_triggered(self):
  self.assertFalse(self.x['phase1_design']['phase2_triggered'])
  self.assertEqual(self.x['aggregate_repeatability']['unstable_task_ids_under_prespecified_terminal_pattern_rule'],[])
  self.assertFalse(self.x['additional_repeatability_expansion_required'])
 def test_diagnostic_does_not_reopen_primary_inference(self):
  self.assertFalse(self.x['changes_R72_R73_primary_inference'])
  self.assertFalse(self.x['changes_R72_R73_execution_schedule'])
  self.assertFalse(self.x['scientific_authority'])
  self.assertFalse(self.x['experiment_authority'])

if __name__=='__main__': unittest.main()
