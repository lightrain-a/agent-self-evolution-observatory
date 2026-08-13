from __future__ import annotations

import hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

from .config import PROJECT_ROOT
from .paper_first_problem_discovery_contract import DISCOVERY_LANES, SEARCH_PORTFOLIO_PRIMITIVES
from .paper_first_problem_gate_queue import build_problem_gate_queue
from .paper_first_problem_generator import _base_policy,_count_by_lane,_empty_summary,load_problem_generator_state
from .paper_first_problem_search_portfolio import _jaccard

GEN_JSON=PROJECT_ROOT/'generated'/'paper-first-problem-search-portfolio-state.json'
GEN_JS=PROJECT_ROOT/'generated'/'paper-first-problem-search-portfolio-state.js'
QUEUE_JSON=PROJECT_ROOT/'generated'/'paper-first-problem-search-portfolio-queue-shadow.json'
QUEUE_JS=PROJECT_ROOT/'generated'/'paper-first-problem-search-portfolio-queue-shadow.js'

def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def rows(root,pattern,key):
    out=[]
    for path in sorted(root.glob(pattern)): out.extend([x for x in (load(path).get(key) or []) if isinstance(x,dict)])
    return out

def manifest_sha(root):
    pairs=[]
    for pattern in ('expand-*.json','evolve-*.json','formulate-*.json','review-p*.json','machine-audit.json','problem-gate.json','frozen-primary-evidence-pool.json'):
        for path in sorted(root.glob(pattern)): pairs.append((path.name,hashlib.sha256(path.read_bytes()).hexdigest()))
    return hashlib.sha256(json.dumps(pairs,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def publish(root:Path):
    base=load(root/'base.json'); frozen=load(root/'frozen-primary-evidence-pool.json'); machine=load(root/'machine-audit.json')
    reviewed=rows(root,'review-p*.json','candidates'); evolved=rows(root,'evolve-*.json','children')
    live=dead=0
    for path in root.glob('formulate-p*.json'):
        payload=load(path); live+=len(payload.get('candidates') or []); dead+=len(payload.get('rejected') or [])
    inbox=root/'reviewed-candidate-inbox.json'
    inbox.write_text(json.dumps({'schema_version':'2.0','authority':{'paper':False,'method':False,'experiment':False,'p0':False,'gpu':False},'candidates':reviewed},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    queue=build_problem_gate_queue(root/'missing-manual.json',auto_inbox_path=inbox,primary_pool_path=root/'frozen-primary-evidence-pool.json')
    queue.setdefault('policy',{}).update({'scientific_authority':False,'shadow_only':True,'cannot_grant_live_paper_design_eligibility':True})
    QUEUE_JSON.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); QUEUE_JS.write_text('window.PAPER_FIRST_PROBLEM_SEARCH_PORTFOLIO_QUEUE = '+json.dumps(queue,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    bs=base.get('summary') or {}; archives=base.get('archives') or {}; by_id={r.get('seed_id'):r for r in base.get('unique_seeds') or [] if r.get('seed_id')}
    breadth=[by_id[s] for s in archives.get('breadth') or [] if s in by_id]; distances=[1-_jaccard(breadth[i],breadth[j]) for i in range(len(breadth)) for j in range(i+1,len(breadth))]
    clear=[c for c in reviewed if (c.get('semantic_reduction_review') or {}).get('verdict')=='CLEAR']; blocked=[c for c in reviewed if c not in clear]
    summary=_empty_summary(len(frozen.get('records') or [])); summary.update({'raw_seeds':bs.get('raw_seeds',0),'semantic_unique_seeds':bs.get('semantic_unique',0),'unique_problem_families':bs.get('structural_clusters',0),'breadth_archive':bs.get('breadth_archive',0),'archive_pairwise_distance':round(sum(distances)/len(distances),4) if distances else 0.0,'evolved_branches':len(evolved),'max_branch_depth':max([int(x.get('branch_depth') or 0) for x in evolved] or [0]),'portfolio_calls':len(list(root.glob('expand-*.json')))+len(list(root.glob('evolve-*.json')))+len(list(root.glob('formulate-p*.json'))),'generated':len(reviewed),'structurally_reviewable':len(reviewed),'semantic_clear':len(clear),'semantic_blocked':len(blocked),'written_to_auto_inbox':len(reviewed),'generated_by_lane':_count_by_lane(reviewed),'structurally_reviewable_by_lane':_count_by_lane(reviewed),'semantic_clear_by_lane':_count_by_lane(clear),'semantic_blocked_by_lane':_count_by_lane(blocked)})
    blockers=Counter(v.split(':',1)[0] for row in machine.get('blocked') or [] for v in row.get('blockers') or [])
    portfolio={'schema_version':'1.0','frozen_pool_sha256':frozen.get('frozen_pool_sha256'),'stage_manifest_sha256':manifest_sha(root),'scientific_authority':False,'policy':{'expansion_precedes_reduction':True,'diversity_archive_precedes_quality_selection':True,'qd_parent_selection':True,'lane_specific_source_minimum':True,'mature_theory_veto_delayed_until_formulation':True,'reduction_falsifiability_contract_required':True,'scheduler_rollover_cannot_change_frozen_transaction':True,'automatic_method_authority':False,'automatic_experiment_authority':False,'automatic_p0_authority':False},'summary':{'requested_raw_seeds':120,'raw_seeds':bs.get('raw_seeds',0),'semantic_unique':bs.get('semantic_unique',0),'duplicate_or_near_duplicate':bs.get('semantic_duplicates',0),'unique_problem_families':bs.get('structural_clusters',0),'breadth_archive':bs.get('breadth_archive',0),'archive_lane_coverage':bs.get('archive_lane_coverage',0),'mean_archive_pairwise_distance':summary['archive_pairwise_distance'],'evolved_branches':len(evolved),'max_branch_depth':summary['max_branch_depth'],'formulated_candidates':live,'formulation_rejected':dead,'machine_reviewable':(machine.get('summary') or {}).get('reviewable',0),'machine_reduction_blocked':(machine.get('summary') or {}).get('blocked',0),'semantic_reviewed':len(reviewed),'semantic_clear':len(clear),'semantic_blocked':len(blocked),'counterfactual_problem_gate_passed':queue['summary']['passed_problem_gate'],'live_paper_design_eligible':0,'generator_model_calls':summary['portfolio_calls'],'reviewer_model_calls':len(list(root.glob('review-p*.json')))},'lane_counts':base.get('lane_counts') or {},'archive_lane_counts':base.get('archive_lane_counts') or {},'archive_counts':{k:len(v or []) for k,v in archives.items()},'machine_blocker_counts':dict(blockers),'passed_candidate_ids':[x['candidate_id'] for x in queue.get('passed') or []]}
    previous=load_problem_generator_state(GEN_JSON); run_id='search-portfolio-20260813-r1'; refs=sorted(str(r.get('ref')) for r in frozen.get('records') or [] if r.get('ref')); receipt={'run_id':run_id,'pool_sha256':frozen.get('frozen_pool_sha256'),'source_refs':refs,'status':'SHADOW_PORTFOLIO_COMPLETE','requested_model':'ark-code-latest','resolved_model':'doubao-seed-evolving','raw_sha256':portfolio['stage_manifest_sha256'],'scientific_authority':False,'live_source_coverage_effect':False}
    receipts=[dict(x) for x in ((previous.get('saturation_memory') or {}).get('portable_review_receipts') or []) if isinstance(x,dict) and x.get('scientific_authority') is False]+[receipt]; receipts=list({str(x.get('run_id')):x for x in receipts if x.get('run_id')}.values())[-64:]; passed_ids=set(portfolio['passed_candidate_ids'])
    lane_counts=base.get('lane_counts') or {};lane_rows=[{'search_primitive':lane,'status':'EXPANDED' if int(lane_counts.get(lane) or 0)>0 else 'EMPTY','raw_seed_count':int(lane_counts.get(lane) or 0),'reason':'Shadow Search Portfolio expansion produced grounded seeds.' if int(lane_counts.get(lane) or 0)>0 else 'No machine-valid grounded seed survived shadow expansion.'} for lane in SEARCH_PORTFOLIO_PRIMITIVES];search_diagnostics={'search_primitive_priority':list(SEARCH_PORTFOLIO_PRIMITIVES),'search_primitive_audit_complete':True,'search_primitive_audit':lane_rows,'scientific_authority':False}
    shadow_policy=_base_policy(portfolio=True);shadow_policy.update({'scientific_authority':False,'shadow_only':True,'canonical_primary_generator_queue_untouched':True,'cannot_create_live_portable_review_receipt':True,'cannot_grant_live_paper_design_eligibility':True})
    state={'schema_version':'3.2-shadow','generated_at':now(),'run_id':run_id,'status':'SHADOW_PORTFOLIO_COMPLETE','scientific_authority':False,'generator_model':'ark-code-latest','reviewer_model':'glm-5.2','policy':shadow_policy,'summary':summary,'search_diagnostics':search_diagnostics,'search_portfolio':portfolio,'generation_notes':f"Shadow Search Portfolio: raw={bs.get('raw_seeds',0)}, unique={bs.get('semantic_unique',0)}, evolved={len(evolved)}, formulated={live}, machine-reviewable={(machine.get('summary') or {}).get('reviewable',0)}, counterfactual Problem-Gate PASS={queue['summary']['passed_problem_gate']}. No live Paper/Method/Experiment/P0 authority.",'raw_artifacts':{'generator':{'sha256':portfolio['stage_manifest_sha256'],'requested_model':'ark-code-latest','resolved_model':'doubao-seed-evolving','portfolio':True,'calls':summary['portfolio_calls']},'semantic_reviewer':{'requested_model':'glm-5.2','resolved_model':'glm-5-2-260617','calls':len(list(root.glob('review-p*.json')))}},'shadow_memory':{'live_source_coverage_effect':False,'current_shadow_receipt':receipt,'scientific_authority':False},'candidates':[{'candidate_id':c['candidate_id'],'title':c['title'],'search_primitive':c['discovery_lane'],'semantic_verdict':(c.get('semantic_reduction_review') or {}).get('verdict'),'counterfactual_problem_gate_pass':c['candidate_id'] in passed_ids,'paper_design_eligible':False,'scientific_authority':False,'authority':{'method':False,'experiment':False,'p0':False,'gpu':False}} for c in reviewed]}
    GEN_JSON.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); GEN_JS.write_text('window.PAPER_FIRST_PROBLEM_SEARCH_PORTFOLIO = '+json.dumps(state,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    return {'generator':summary,'portfolio':portfolio['summary'],'problem_gate':queue['summary'],'passed':portfolio['passed_candidate_ids']}

if __name__=='__main__':
    import argparse; p=argparse.ArgumentParser();p.add_argument('run_root',type=Path);a=p.parse_args();print(json.dumps(publish(a.run_root),ensure_ascii=False,indent=2))
