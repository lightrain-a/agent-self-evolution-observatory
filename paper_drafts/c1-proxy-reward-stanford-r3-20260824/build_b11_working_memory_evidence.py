#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
B11=HERE/'b11-working-memory-attribution.json'
PRIOR=HERE/'transport-localization-evidence.json'
B11_SHA='c17ed88b2bfa496f91c4753cbae6d3dcaad5e95b45f794679741fd0fdc4de9e2'
PRIOR_SHA='89b17623214d429efdefd791cc119b74b5231784815990f6a70f6c725e6598bc'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def main():
 if sha(B11)!=B11_SHA:raise RuntimeError('B11 SHA drift')
 if sha(PRIOR)!=PRIOR_SHA:raise RuntimeError('prior localization SHA drift')
 b=load(B11);p=load(PRIOR);a=b['branch_attribution'];g=b['common_centroid_uptake'];d=b['branch_direction_uptake']
 if b['status']!='B11_POSTHOC_ZERO_PROVIDER_DIAGNOSTIC_COMPLETE' or b['provider_calls']!=0 or b['confirmatory_gate'] is not None:raise RuntimeError('B11 authority drift')
 out={'schema_version':'1.0','artifact_type':'b11-working-memory-localization-evidence','paper_id':b['paper_id'],'status':'B11_WORKING_MEMORY_LOCALIZATION_COMPLETE_STOP','role':'Append-only post-hoc process localization after B10. No new provider calls and no claim expansion.',
 'source_bindings':{'prior_transport_localization_sha256':PRIOR_SHA,'b11_attribution_sha256':B11_SHA,'b10_result_sha256':b['source_bindings']['b10_result_sha256'],'b4_result_sha256':b['source_bindings']['b4_result_sha256']},
 'working_memory_observable':{'archived_outputs':b['extraction']['archived_outputs'],'complete_fields':b['extraction']['complete_fields'],'strict_json':b['extraction']['strict_json'],'narrow_recovery':b['extraction']['narrow_string_recovery']},
 'branch_specific_uptake':{'mean_pair_relative_shift':a['mean'],'median_shift':a['median'],'positive_tasks':a['positive_tasks'],'negative_tasks':a['negative_tasks'],'paired_dz':a['paired_dz'],'posthoc_permutation_p':a['within_state_label_permutation_p'],'verdict':'NOT_ESTABLISHED_POSTHOC'},
 'generic_common_core_tendency':{'mean_common_centroid_uptake':g['mean'],'paired_dz':g['paired_dz'],'posthoc_signflip_p':g['signflip_p'],'verdict':'SUGGESTIVE_ONLY_NOT_CONFIRMATORY'},
 'transport_linkage':{'pearson_working_memory_shift_vs_first_action_tv':a['pearson_vs_first_action_tv'],'spearman_working_memory_shift_vs_first_action_tv':a['spearman_vs_first_action_tv'],'leave_one_out_pearson_range':[a['leave_one_out_pearson_vs_first_action_tv_min'],a['leave_one_out_pearson_vs_first_action_tv_max']],'pearson_working_memory_shift_vs_terminal_effect':a['pearson_vs_terminal_absolute_effect'],'interpretation':'States with more branch-relative working-memory movement tend descriptively to show more first-action distribution movement, but this does not carry to terminal outcomes.'},
 'simple_similarity_falsifier':{'input_memory_cosine_distance_mean':a['input_memory_cosine_distance_mean'],'range':[a['input_memory_cosine_distance_min'],a['input_memory_cosine_distance_max']],'pearson_distance_vs_working_memory_shift':a['pearson_input_memory_distance_vs_branch_attribution'],'pearson_distance_vs_first_action_tv':a['pearson_input_memory_distance_vs_first_action_tv'],'pearson_distance_vs_terminal_effect':a['pearson_input_memory_distance_vs_terminal_absolute_effect'],'interpretation':'Input-pair semantic distance is not a useful monotonic explanation for branch uptake or downstream magnitude on the frozen support.'},
 'scientific_synthesis':'The dominant attenuation is already visible in the model-emitted working-memory representation before the first structured action: reward-branch-specific information is weakly internalized, while common-memory uptake is at most suggestive. The small descriptive working-memory-to-action association does not reach terminal outcomes.',
 'stop_decision':{'B12_provider_experiment_authorized':False,'reason':'B11 is post-hoc and does not establish a robust branch-specific pre-action uptake signal. Selecting only B10/B11 positive cells would be outcome-driven support selection.','forbidden':['select future tasks by B10 first-action TV','select tasks by B11 attribution shift','lower prior practical floors','model fishing for a positive branch-uptake result'],'reopen_only_if':['a new branch-specific pre-action observable is frozen before new policy outputs and evaluated on outcome-independent support','or a representation-preserving common-core versus branch-residual intervention is preregistered on the full frozen support without positive-cell selection']},
 'provider_calls':0,'new_rollouts':0,'scientific_authority':False,'experiment_authority':True,'claim_expansion_authority':False,'submission_authority':False}
 target=HERE/'b11-working-memory-localization-evidence.json';tmp=target.with_suffix('.json.tmp');tmp.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');os.replace(tmp,target);print(json.dumps({'status':out['status'],'branch':out['branch_specific_uptake'],'generic':out['generic_common_core_tendency'],'linkage':out['transport_linkage'],'B12_provider_experiment_authorized':False},indent=2))
if __name__=='__main__':main()
