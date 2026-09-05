from __future__ import annotations
import hashlib,json,pathlib,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
GEN=ROOT/'generated'
FILES={
 'r76':GEN/'d2-failure-memory-provenance-r76-llama-discordant-repeatability.json',
 'm1':GEN/'d2-failure-memory-provenance-r77-m1-divergence-localization.json',
 'states':GEN/'d2-failure-memory-provenance-r77-m2-frozen-probe-states.json',
 'm2a':GEN/'d2-failure-memory-provenance-r77-m2a-exact-greedy-replay.json',
 'm2b':GEN/'d2-failure-memory-provenance-r77-m2b-exact-same-state-logit-probe.json',
 'm3plan':GEN/'d2-failure-memory-provenance-r77-m3-branch-response-mediation-plan.json',
 'm3':GEN/'d2-failure-memory-provenance-r77-m3-branch-response-mediation-result.json',
 'm4':GEN/'d2-failure-memory-provenance-r77-m4-temperature-sensitivity-analytic.json',
 'closeout':GEN/'d2-failure-memory-provenance-r77-mechanism-closeout.json',
}
EXPECTED_FILE_SHA={
 'r76':'6d310cb2f841598a0f38c24b809dac334def69d5f0b8f42edfd32b0c4641f98a',
 'm1':'11b409cf611e3684810a4eb94c59049f365940162ee098f825c100013a8c72ba',
 'states':'f89542dab1ef48f32c548e8a1f3efdbafc339410b56ca36023f943d1e6f61a10',
 'm2a':'37cf5909f97e017835e48cb21a287d0ef8462118b5f11eb415ddafa2325be8f5',
 'm2b':'a319749c5405c9a41c2f581d9e8f9b3bde266902275fb8c496d26341109b17b1',
 'm3plan':'f812a70e6f1d8ebae5f109d088af38922784516396fbef5b42875e08c5a569bc',
 'm3':'168a75fefa1dc47fa1e8d035637480bf42ccfc6070f2f1878c20b6c811c194b8',
 'm4':'aff99a066346f8c9031aa28142d7bae0cc75288a2cc5282cd7ca3b1e1363a607',
}
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def valid(x):
 r=x['receipt_sha256'];y=dict(x);y.pop('receipt_sha256');return r==digest(y)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class FailureMemoryMechanismR77Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x={k:load(v) for k,v in FILES.items()}

 def test_raw_artifact_file_hashes_are_bound(self):
  for k,h in EXPECTED_FILE_SHA.items():self.assertEqual(sha(FILES[k]),h,k)

 def test_receipts_are_content_valid(self):
  for k in ['r76','m1','states','m2a','m2b','m3plan','m3','m4','closeout']:
   self.assertTrue(valid(self.x[k]),k)

 def test_temperature_sampling_is_not_primary_explanation(self):
  r=self.x['r76']
  self.assertEqual(r['status'],'R76_LLAMA_DISCORDANT_EXACT_RERUN_4_OF_4_PAIR_PATTERNS_REPRODUCED')
  self.assertEqual(r['historical_binding']['temperature'],0.0);self.assertFalse(r['historical_binding']['do_sample'])
  self.assertEqual(r['aggregate_repeatability']['terminal_pair_patterns_reproduced'],'4/4')
  self.assertEqual(r['aggregate_repeatability']['terminal_arm_outcomes_reproduced'],'8/8')
  self.assertEqual(r['aggregate_repeatability']['unstable_task_ids_under_prespecified_terminal_pattern_rule'],[])

 def test_m1_divergence_geometry(self):
  by={r['task_id']:r for r in self.x['m1']['rows']}
  self.assertEqual((by['125']['first_normalized_action_divergence_action_index'],by['125']['common_external_transition_prefix_count'],by['125']['history_exactly_shared_at_target']),(5,5,True))
  self.assertEqual((by['193']['first_normalized_action_divergence_action_index'],by['193']['history_exactly_shared_at_target']),(0,True))
  self.assertEqual(by['136']['anchor_names'],['A_history','B_history'])
  self.assertEqual(by['327']['anchor_names'],['A_history','B_history'])

 def test_m2a_exact_runtime_replay_fidelity(self):
  x=self.x['m2a'];self.assertEqual(x['status'],'R77_M2A_EXACT_GREEDY_REPLAY_PASS');self.assertEqual(x['failures'],[]);self.assertEqual(len(x['rows']),8)
  self.assertTrue(all(r['normalized_action_matches_historical'] for r in x['rows']))

 def test_m2b_direct_boundary_flips_only_on_125_193(self):
  rows=self.x['m2b']['rows'];by={}
  for r in rows:by.setdefault(r['task_id'],[]).append(r)
  self.assertTrue(by['125'][0]['prompt_swap_flips_A_vs_B_candidate_token_preference'])
  self.assertLess(by['125'][0]['conditions']['A']['branchpoint_logodds_B_minus_A'],0);self.assertGreater(by['125'][0]['conditions']['B']['branchpoint_logodds_B_minus_A'],0)
  self.assertTrue(by['193'][0]['prompt_swap_flips_A_vs_B_candidate_token_preference'])
  self.assertAlmostEqual(by['193'][0]['treatment_shift_branchpoint_logodds_toward_B'],0.6250000596046448)
  self.assertFalse(any(r['prompt_swap_flips_A_vs_B_candidate_token_preference'] for r in by['136']))
  self.assertFalse(any(r['prompt_swap_flips_A_vs_B_candidate_token_preference'] for r in by['327']))

 def test_m2b_history_anchor_dominates_136_and_327(self):
  by={(r['task_id'],r['anchor']):r for r in self.x['m2b']['rows']}
  for tid in ['136','327']:
   a=by[(tid,'A_history')];b=by[(tid,'B_history')]
   self.assertLess(a['conditions']['A']['branchpoint_logodds_B_minus_A'],0)
   self.assertLess(a['conditions']['B']['branchpoint_logodds_B_minus_A'],0)
   self.assertGreater(b['conditions']['A']['branchpoint_logodds_B_minus_A'],0)
   self.assertGreater(b['conditions']['B']['branchpoint_logodds_B_minus_A'],0)

 def test_m3_branch_response_mediation_is_heterogeneous(self):
  by={r['task_id']:r for r in self.x['m3']['task_rows']}
  self.assertTrue(by['125']['both_cross_forced_terminals_match_opposite_historical_branches'])
  self.assertTrue(by['136']['both_cross_forced_terminals_match_opposite_historical_branches'])
  self.assertFalse(by['193']['both_cross_forced_terminals_match_opposite_historical_branches'])
  self.assertEqual((by['193']['A_prompt_force_B_terminal'],by['193']['B_prompt_force_A_terminal']),(True,True))
  self.assertFalse(by['327']['both_cross_forced_terminals_match_opposite_historical_branches'])
  self.assertEqual((by['327']['A_prompt_force_B_terminal'],by['327']['B_prompt_force_A_terminal']),(True,True))
  self.assertEqual(self.x['m3']['full_bidirectional_terminal_swap_count'],2)

 def test_m4_temperature_separates_fragile_125_from_robust_193(self):
  by={r['task_id']:r for r in self.x['m4']['task_summary']}
  self.assertEqual(by['125']['mechanism_temperature_type'],'DIRECT_PROMPT_BOUNDARY_FLIP_ALL_ANCHORS')
  self.assertEqual(by['193']['mechanism_temperature_type'],'DIRECT_PROMPT_BOUNDARY_FLIP_ALL_ANCHORS')
  self.assertLess(by['125']['temperature_0p2_probability_shifts'][0],0.05)
  self.assertGreater(by['193']['temperature_0p2_probability_shifts'][0],0.50)
  self.assertEqual(by['136']['mechanism_temperature_type'],'HISTORY_ANCHOR_DOMINANT_SIGN_WITHIN_ANCHOR')
  self.assertEqual(by['327']['mechanism_temperature_type'],'HISTORY_ANCHOR_DOMINANT_SIGN_WITHIN_ANCHOR')

 def test_closeout_does_not_upgrade_primary_claim(self):
  c=self.x['closeout']
  self.assertFalse(c['changes_R72_R73_primary_inference']);self.assertFalse(c['changes_R72_R73_execution_schedule'])
  self.assertFalse(c['experiment_authority']);self.assertFalse(c['gpu_authority'])
  self.assertIn('post hoc',c['interpretation_limits'][0].lower())
  self.assertIn('not isolated',c['capability_boundary_hypothesis'])

if __name__=='__main__':unittest.main()
