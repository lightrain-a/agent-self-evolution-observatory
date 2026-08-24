#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PATHS={
 'b1':Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b1-exact-retrieval-exposure-20260824/b1-exact-retrieval-exposure.json'),
 'b2':HERE/'b2-breadth-evidence.json',
 'b3':Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b3-expanded-retrieval-exposure-20260824/b3-expanded-retrieval-exposure.json'),
 'b4':Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b4-retrieval-matched-fixed-evidence-20260824/b4-result.json'),
 'b5':Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b5-no-memory-native-support-20260824/b5-result.json'),
 'b6_parent':Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b6-cross-policy-retrieval-matched-20260824/b6-result.json'),
 'b6_r1':Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b6-cross-policy-retrieval-matched-r1-2200-20260824/b6-r1-result.json'),
 'program':HERE/'baseline-aligned-experiment-program.json',
 'cross_policy_program':HERE/'b6-b7-cross-policy-program.json',
 'cross_policy_repair':HERE/'b6-b7-output-cap-repair-addendum.json',
}
EXPECTED={
 'b1':'88ba6ee7e3fae02f4c461d8fa421b67f4211a9259f597cdcc36e927fe9cdde45',
 'b3':'a5e39a817cdadc9b4edae4edba0c9c90068f1cd9d083e4c3a70bdfad32871440',
 'b4':'fb3fef89a38806e9a3b13efd8413b920f81b132390818403f4d5be957f42feeb',
 'b5':'f506ac35aeb5e88f8473c04cec9259bcddcc53cdad5412d1d488f84eec77ebfb',
 'b6_r1':'202caceba85bc1dd98d077f141d8cd7584fcce0fe17c9ea6c32553d599c22085',
}
PREVIOUS_OBSERVABLE_LOWER_BOUND=841

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path):return json.loads(p.read_text(encoding='utf-8'))
def req(x,msg):
 if not x:raise RuntimeError(msg)

def main():
 for key,h in EXPECTED.items():req(PATHS[key].is_file() and sha(PATHS[key])==h,f'{key} SHA drift')
 for p in PATHS.values():req(p.is_file(),f'missing {p}')
 d={k:load(p) for k,p in PATHS.items()}
 b1,b2,b3,b4,b5,b6p,b6r=d['b1'],d['b2'],d['b3'],d['b4'],d['b5'],d['b6_parent'],d['b6_r1']
 req(b1['status']=='COMPLETE_ZERO_PROVIDER_CALLS' and b1['summary']['shopping_threshold_hits']==8,'B1 drift')
 req(b2['status']=='B2_BROAD_WRITE_CHANNEL_SUPPORTED' and b2['combined_complete_pairs']==20,'B2 drift')
 req(b3['status']=='COMPLETE_ZERO_PROVIDER_CALLS' and b3['summary']['offline_eligible_retrieval_matched_tasks']==36,'B3 drift')
 req(b4['status']=='B4_EXECUTION_COMPLETE' and b4['summary']['provider_calls_complete']==288 and b4['summary']['provider_failures']==0,'B4 drift')
 req(b5['status']=='B5_EXECUTION_COMPLETE' and b5['summary']['provider_calls_complete']==144 and b5['summary']['provider_failures']==0,'B5 drift')
 req(b6p['summary']['provider_calls_attempted_total']==1 and b6p['summary']['provider_calls_complete']==0 and b6p['summary']['provider_failures']==1,'B6 parent drift')
 req(b6r['summary']['provider_calls_attempted_total']==1 and b6r['summary']['provider_calls_complete']==0 and b6r['summary']['provider_failures']==1,'B6 R1 drift')
 req(all((x.get('provider_receipt') or {}).get('incomplete_reason')=='length' for x in b6p['failures']+b6r['failures']),'B6 failure not length-only')
 new_posts=64+288+144+1+1
 usable=32+288+144
 payload={
  'schema_version':'1.0','artifact_type':'baseline-aligned-expansion-evidence','paper_id':'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE','status':'BASELINE_ALIGNED_EXPANSION_COMPLETE_WITH_CROSS_POLICY_SUPPORT_STOP',
  'source_bindings':{k:sha(p) for k,p in PATHS.items()},
  'experiments':{
   'B1_original_bank_exact_retrieval':{'provider_calls':0,'shopping_heldout_tasks':b1['summary']['shopping_heldout_tasks'],'threshold_hits':b1['summary']['shopping_threshold_hits'],'hit_rate':b1['summary']['shopping_hit_rate'],'original_frozen_future_hits':b1['summary']['frozen_future_hits'],'interpretation':'Original four-memory bank rarely exposes these memories under the released retriever; the four F2R1 future tasks are all non-hits.'},
   'B2_write_breadth':{'original_complete_pairs':b2['original_complete_pairs'],'new_complete_pairs':b2['new_complete_pairs'],'combined_complete_pairs':b2['combined_complete_pairs'],'combined_exact_content_change_rate':b2['summary']['combined_exact_content_change_rate'],'combined_title_set_change_rate':b2['summary']['combined_title_set_change_rate'],'new_mean_token_jaccard_distance':b2['summary']['new_mean_token_jaccard_distance'],'pooled_20_pair_mean_token_jaccard_distance':b2['summary']['pooled_20_pair_mean_token_jaccard_distance'],'new_distinct_intent_templates':b2['new_distinct_intent_templates'],'provider_posts':b2['execution_accounting']['total_b2_provider_posts'],'scientifically_usable_provider_posts':b2['execution_accounting']['scientifically_usable_r1_provider_posts'],'interpretation':'Upstream reward-conditioned write divergence replicates broadly over 16 additional outcome-balanced sources; parent 2200-token censoring is execution-only and R1 is the scientific breadth result.'},
   'B3_expanded_bank_exact_retrieval':{'provider_calls':0,'source_memory_count':b3['retrieval_contract']['source_task_count'],'shopping_heldout_tasks':b3['summary']['shopping_heldout_tasks'],'threshold_hits':b3['summary']['shopping_threshold_hits'],'hit_rate':b3['summary']['shopping_hit_rate'],'hit_intent_templates':b3['summary']['hit_intent_template_count'],'offline_eligible_tasks':b3['summary']['offline_eligible_retrieval_matched_tasks'],'eligible_intent_templates':b3['summary']['eligible_intent_template_count'],'interpretation':'Expanding the source bank changes exposure support without changing top-1/.3 retrieval mechanics; 36 tasks are pre-outcome eligible for fixed-evidence transport.'},
   'B4_native_retrieval_matched_branch_transport':{'provider_calls':b4['summary']['provider_calls_attempted_total'],'complete_calls':b4['summary']['provider_calls_complete'],'future_tasks':36,'mean_absolute_success_rate_difference':b4['summary']['observed_mean_absolute_success_rate_difference'],'permutation_p':b4['summary']['permutation_p_ge_observed'],'practical_floor':b4['summary']['practical_effect_floor'],'gate_pass':b4['summary']['breadth_gate_pass'],'zero_cells':b4['secondary']['zero_cells'],'positive_signed_cells':b4['secondary']['positive_signed_cells'],'negative_signed_cells':b4['secondary']['negative_signed_cells'],'joint_floor_cells':18,'joint_ceiling_cells':16,'interpretation':'Success-versus-failure branch transport is not established on broad native-retrieval support; the binary endpoint is highly saturated.'},
   'B5_native_support_no_memory':{'provider_calls':b5['summary']['provider_calls_attempted_total'],'complete_calls':b5['summary']['provider_calls_complete'],'future_tasks':36,'mean_absolute_memory_presence_effect':b5['summary']['observed_mean_absolute_memory_presence_effect'],'permutation_p':b5['summary']['omnibus_permutation_p_ge_observed'],'practical_floor':b5['summary']['practical_effect_floor'],'gate_pass':b5['summary']['memory_presence_gate_pass'],'geometry_counts':b5['summary']['geometry_counts'],'interpretation':'A statistically detectable three-arm deviation exists, but the frozen practical-effect floor is missed; broad native memory presence has small terminal magnitude for this policy/support.'},
   'B6_cross_policy_support_stop':{'provider_posts_parent':1,'provider_posts_r1':1,'scientifically_usable_calls':0,'parent_cap':900,'repair_cap':2200,'failure_stage':'first frozen unit','failure_reason':'length/no assistant text','resolved_model':'deepseek-v4-flash-ga-260731','further_cap_repair_allowed':False,'B7_executed':False,'interpretation':'Cross-policy terminal transfer is unresolved because both preregistered DeepSeek request surfaces fail provider output support before any scientific unit; this is not a scientific null.'}
  },
  'scientific_synthesis':{
   'upstream':'Reward-conditioned writing robustly changes persistent memory over 20 complete paired sources total.',
   'forced_intervention':'The original F2R1 forced memory swap remains evidence that paired persistent states can alter terminal outcomes under a controlled intervention.',
   'native_transport':'Broad released-retrieval identity plus the native ReasoningBank wrapper does not reproduce a practically large success-versus-failure terminal contrast under the Doubao policy.',
   'presence_control':'Literal omission similarly shows only a small practical memory-presence effect on the same broad native support.',
   'boundary':'Write-time state corruption and realized behavioral impact are distinct stages; retrieval exposure, interface, endpoint headroom, and policy/support determine whether a written difference becomes an outcome difference.'
  },
  'execution_accounting':{'new_provider_posts':new_posts,'new_scientifically_usable_provider_completions':usable,'new_scientifically_usable_writer_calls':32,'new_scientifically_usable_terminal_rollouts':432,'new_zero_provider_retrieval_audits':2,'cross_policy_support_failure_posts':2,'prior_full_paper_observable_provider_posts_lower_bound':PREVIOUS_OBSERVABLE_LOWER_BOUND,'updated_full_paper_observable_provider_posts_lower_bound':PREVIOUS_OBSERVABLE_LOWER_BOUND+new_posts,'training_runs':0,'gpu_runs':0},
  'claim_boundary':{'write_channel_breadth_supported':True,'forced_swap_terminal_sensitivity_supported':True,'native_retrieval_matched_branch_transport_supported':False,'native_memory_presence_practical_effect_supported':False,'cross_policy_terminal_transfer_supported':None,'cross_policy_terminal_transfer_status':'SUPPORT_STOP_ZERO_SCIENTIFIC_UNITS','live_browser_transport_supported':False,'population_effect_supported':False},
  'scientific_authority':False,'experiment_authority':True,'claim_expansion_authority':False,'submission_authority':False
 }
 out=HERE/'baseline-aligned-expansion-evidence.json';out.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print(json.dumps({'status':payload['status'],'execution_accounting':payload['execution_accounting'],'scientific_synthesis':payload['scientific_synthesis'],'claim_boundary':payload['claim_boundary']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
