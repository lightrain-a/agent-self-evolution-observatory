from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .api_memory_escape_smoke_staged import ARMS, GENERATOR_MODEL
from .api_memory_portfolio_smoke_finalize import _successful_review
from .api_memory_portfolio_smoke_reviewers import AGENT_REVIEWER_MODEL,HARD_REVIEWER_MODEL,REDUCTION_REVIEWER_MODEL
from .api_memory_search_smoke import _canonical,_diversity,_max_cross_similarity,_sha_text
from .api_memory_search_smoke_staged import _load,_lock,_write
from .api_research_memory import record_api_memory_consumption,record_parsed_api_output


def finalize(*, root:Path, study:Path)->dict[str,Any]:
    output=study/"report.json";lock=_lock(output,{"stage":"finalize"})
    try:
        prep=_load(study/"state-prepared.json");rprep=_load(study/"review-prepared.json")
        hard,ha=_successful_review(study,"hard","HARD_REVIEW_COMPLETE");agent,aa=_successful_review(study,"agent","AGENT_REVIEW_COMPLETE");reduction,ra=_successful_review(study,"reduction","REDUCTION_REVIEW_COMPLETE")
        h={r['blind_id']:r for r in hard['reviews']};a={r['blind_id']:r for r in agent['reviews']};d={r['blind_id']:r for r in reduction['reviews']};mapping={r['blind_id']:(r['arm'],r['idea_id']) for r in rprep['mapping']};per={arm:[] for arm in ARMS}
        for bid,(arm,iid) in mapping.items(): per[arm].append({'blind_id':bid,'idea_id':iid,'hard':h[bid],'agent':a[bid],'reduction':d[bid]})
        gens={arm:_load(study/f"generation-{arm}.json") for arm in ARMS}
        for arm in ARMS:
            gen=gens[arm];pack=prep['packs'][arm];structured={'schema_version':'2.4','study':'API_MEMORY_ESCAPE_SMOKE','arm':arm,'query_pack_sha256':pack['query_pack_sha256'],'selected_memory_ids':pack['selected_memory_ids'],'selected_memory_roles':pack.get('selected_memory_roles') or [],'usage':gen['usage'],'ideas':gen['ideas'],'criterion_reviews':sorted(per[arm],key=lambda r:r['idea_id']),'scientific_authority':False,'belief_authority':False}
            record_parsed_api_output(run_root=root/'runs'/gen['run_id'],stage='memory-escape-smoke',raw_sha256=gen['raw_sha256'],structured_payload=structured,requested_model=GENERATOR_MODEL,resolved_model=gen['resolved_model'],research_objects=[],root=root)
            record_api_memory_consumption(run_id=gen['run_id'],stage='memory-escape-smoke',pack=pack,raw_sha256=gen['raw_sha256'],output_object_ids=[f"{arm}:{x['id']}" for x in gen['ideas']],outcome_status='ESCAPE_SMOKE_GENERATED_ZERO_AUTHORITY',root=root)
        metrics={}
        for arm in ARMS:
            rows=per[arm];ideas=gens[arm]['ideas'];clear=sum((not r['hard']['history_near_duplicate']) and r['hard']['cheapest_falsifier_complete'] and r['agent']['agent_specificity']=='AGENT_SPECIFIC' and r['reduction']['reduction_verdict']=='RESIDUAL_PLAUSIBLE' for r in rows);other=gens['relevant_escape' if arm=='relevant_neutral' else 'relevant_neutral']['ideas']
            metrics[arm]={'n':len(rows),'history_pack_duplicate_rate':sum(r['hard']['history_near_duplicate'] for r in rows)/len(rows),'falsifier_complete_rate':sum(r['hard']['cheapest_falsifier_complete'] for r in rows)/len(rows),'agent_specific_rate':sum(r['agent']['agent_specificity']=='AGENT_SPECIFIC' for r in rows)/len(rows),'exact_reduction_rate':sum(r['reduction']['reduction_verdict']=='EXACT_REDUCTION' for r in rows)/len(rows),'residual_plausible_rate':sum(r['reduction']['reduction_verdict']=='RESIDUAL_PLAUSIBLE' for r in rows)/len(rows),'criterion_panel_clear_count':clear,'criterion_panel_clear_rate':clear/len(rows),'within_arm_lexical_diversity':_diversity(ideas),'mean_max_cross_arm_lexical_similarity':_max_cross_similarity(ideas,other),'generation_input_tokens':gens[arm]['usage']['input_tokens'],'generation_output_tokens':gens[arm]['usage']['output_tokens'],'selected_memory_items':prep['packs'][arm]['summary']['selected'],'selected_memory_characters':prep['packs'][arm]['summary']['characters']}
        primary={'escape_vs_neutral_panel_clear_delta':metrics['relevant_escape']['criterion_panel_clear_rate']-metrics['relevant_neutral']['criterion_panel_clear_rate'],'escape_vs_neutral_agent_specific_delta':metrics['relevant_escape']['agent_specific_rate']-metrics['relevant_neutral']['agent_specific_rate'],'escape_vs_neutral_exact_reduction_delta':metrics['relevant_escape']['exact_reduction_rate']-metrics['relevant_neutral']['exact_reduction_rate'],'same_selected_memory_ids':prep['packs']['relevant_neutral']['selected_memory_ids']==prep['packs']['relevant_escape']['selected_memory_ids'],'same_memory_characters':metrics['relevant_neutral']['selected_memory_characters']==metrics['relevant_escape']['selected_memory_characters'],'same_visible_source_sha256':[r.get('visible_source_sha256') for r in prep['packs']['relevant_neutral'].get('selected_memory_roles') or []]==[r.get('visible_source_sha256') for r in prep['packs']['relevant_escape'].get('selected_memory_roles') or []],'interpretation':'framing-only search-policy smoke with matched selected objects, prefix lengths, visible source bytes, and total characters; not Problem Gate, scientific truth, or publication-success evidence'}
        report={'schema_version':'2.4','status':'API_MEMORY_ESCAPE_SMOKE_COMPLETE','study':'API_MEMORY_ESCAPE_SMOKE_V24','memory_instance_id':prep['packs']['relevant_neutral']['memory_instance_id'],'frozen_ablation_plan_sha256':prep['plan']['plan_sha256'],'history_pool_available_objects':prep['packs']['relevant_neutral']['summary']['available'],'generator_model':GENERATOR_MODEL,'reviewers':{'hard':{'requested':HARD_REVIEWER_MODEL,'resolved':hard['resolved_model'],'usage':hard['usage'],'attempts':ha},'agent':{'requested':AGENT_REVIEWER_MODEL,'resolved':agent['resolved_model'],'usage':agent['usage'],'attempts':aa},'reduction':{'requested':REDUCTION_REVIEWER_MODEL,'resolved':reduction['resolved_model'],'usage':reduction['usage'],'attempts':ra}},'metrics':metrics,'primary_comparison':primary,'generated_outputs_promoted_to_research_objects':False,'scientific_authority':False,'belief_authority':False};report['report_sha256']=_sha_text(_canonical(report));_write(output,report);return report
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def main()->None:
    p=argparse.ArgumentParser();p.add_argument('--persistent-root',type=Path,required=True);p.add_argument('--study',type=Path,required=True);a=p.parse_args();print(json.dumps(finalize(root=a.persistent_root,study=a.study),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
