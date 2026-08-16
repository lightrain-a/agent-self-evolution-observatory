from __future__ import annotations

import hashlib,json,re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

from .config import PROJECT_ROOT
from .paper_first_problem_discovery_contract import DISCOVERY_LANES, DISCOVERY_OPERATOR_VERSION, SEARCH_PORTFOLIO_PRIMITIVES
from .paper_first_problem_gate_queue import build_problem_gate_queue
from .paper_first_problem_generator import _base_policy,_count_by_lane,_empty_summary,load_problem_generator_state
from .paper_first_shadow_search_admission import primary_content_sha256
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
    for pattern in ('shadow-run-qualification.json','expand-*.json','error-expand-*.json','evolve-*.json','error-evolve-*.json','formulate-p*.json','error-formulate-*.json','review-p*.json','error-review-*.json','machine-audit.json','evidence-acquisition-plan.json','evidence-design-p*.json','evidence-recompile-p*.json','evidence-review-p*.json','evidence-substrate-preflight-request.json','evidence-substrate-preflight.json','evidence-harness-implementation.json','evidence-acquisition-adjudication.json','shadow-final-audit.json','shadow-terminal-current-source-gate.json','post-review-current-source-audit.json','current-source-receipt-*.json','problem-falsifier-support-inventory-request.json','problem-falsifier-support-inventory.json','problem-falsifier-preflight.json','frozen-primary-evidence-pool.json'):
        for path in sorted(root.glob(pattern)): pairs.append((path.name,hashlib.sha256(path.read_bytes()).hexdigest()))
    return hashlib.sha256(json.dumps(pairs,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def _evidence_unresolved_count(summary:dict)->int:
    terminal_keys=(
        'evidence_reduction_supported',
        'evidence_wait_primary_asset',
        'evidence_design_invalid',
        'evidence_review_blocked',
        'evidence_substrate_hold',
        'evidence_inconclusive',
    )
    resolved=sum(int(summary.get(key) or 0) for key in terminal_keys)
    return max(0,int(summary.get('provisional_problem_candidates') or 0)-resolved)

def _latest_shadow_run(root:Path)->dict:
    base=load(root/'base.json'); frozen=load(root/'frozen-primary-evidence-pool.json'); machine=load(root/'machine-audit.json')
    final=load(root/'shadow-final-audit.json'); terminal=load(root/'shadow-terminal-current-source-gate.json');qualification=load(root/'shadow-run-qualification.json') if (root/'shadow-run-qualification.json').exists() else {}
    reviewed=rows(root,'review-p*.json','candidates'); evolved=rows(root,'evolve-*.json','children')
    formulated=reduction_pending=rejected=successful_formulation_branches=0
    formulation_paths=list(root.glob('formulate-p*.json'))
    formulation_error_paths=list(root.glob('error-formulate-*.json'))
    for path in formulation_paths:
        payload=load(path);formulated+=len(payload.get('candidates') or []);reduction_pending+=len(payload.get('reduction_pending') or []);rejected+=len(payload.get('rejected') or []);successful_formulation_branches+=len(payload.get('branch_ids') or [])
    formulation_errors=[load(path) for path in formulation_error_paths]
    formulation_provider_failures=sum(str(row.get('status') or '').startswith('PROVIDER_') for row in formulation_errors)
    formulation_parse_failures=sum(str(row.get('status') or '')=='PARSE_ERROR_ZERO_AUTHORITY' for row in formulation_errors)
    formulation_parts=[]
    for path in formulation_paths+formulation_error_paths:
        match=re.search(r'formulate-p(\d+)',path.name)
        if match:formulation_parts.append(int(match.group(1)))
    formulation_requested_shards=max(formulation_parts or [0])
    formulation_requested_branches=formulation_requested_shards*2
    formulation_censored_branches=max(sum(len(row.get('branch_ids') or []) for row in formulation_errors),formulation_requested_branches-successful_formulation_branches)
    falsifier_request=load(root/'problem-falsifier-support-inventory-request.json') if (root/'problem-falsifier-support-inventory-request.json').exists() else {}
    falsifier_request_summary=falsifier_request.get('summary') or {}
    falsifier_preflight=load(root/'problem-falsifier-preflight.json') if (root/'problem-falsifier-preflight.json').exists() else {}
    falsifier_summary=falsifier_preflight.get('summary') or {}
    falsifier_inventory_path=root/'problem-falsifier-support-inventory.json'
    falsifier_inventory_sha=str(falsifier_preflight.get('support_inventory_sha256') or '').strip().lower()
    if falsifier_inventory_sha:
        if not falsifier_inventory_path.exists():raise ValueError('problem falsifier preflight binds a missing support inventory')
        actual_inventory_sha=hashlib.sha256(falsifier_inventory_path.read_bytes()).hexdigest()
        if actual_inventory_sha!=falsifier_inventory_sha:raise ValueError('problem falsifier support inventory hash mismatch')
    evidence_plan=load(root/'evidence-acquisition-plan.json') if (root/'evidence-acquisition-plan.json').exists() else {}
    evidence_summary=evidence_plan.get('summary') or {}
    bs=base.get('summary') or {};archives=base.get('archives') or {};by_id={r.get('seed_id'):r for r in base.get('unique_seeds') or [] if r.get('seed_id')}
    breadth=[by_id[s] for s in archives.get('breadth') or [] if s in by_id];distances=[1-_jaccard(breadth[i],breadth[j]) for i in range(len(breadth)) for j in range(i+1,len(breadth))]
    semantic_clear=[c for c in reviewed if (c.get('semantic_reduction_review') or {}).get('verdict')=='CLEAR']
    term_rows={str(r.get('candidate_id') or ''):r for r in terminal.get('rows') or [] if isinstance(r,dict)}
    candidate_rows=[]
    for row in final.get('rows') or []:
        if not isinstance(row,dict):continue
        cid=str(row.get('candidate_id') or '');term=term_rows.get(cid) or {};current=term.get('current_source_review') or {};candidate=row.get('candidate') or {};semantic=candidate.get('semantic_reduction_review') or {}
        current_sources=sorted({str(item.get('ref') or '') for item in current.get('sources') or [] if isinstance(item,dict) and str(item.get('ref') or '').startswith('arXiv:')})
        evidence_refs=sorted({str((candidate.get('empirical_evidence') or {}).get(key,{}).get('ref') or '') for key in ('source_a','source_b') if str((candidate.get('empirical_evidence') or {}).get(key,{}).get('ref') or '').startswith('arXiv:')})
        candidate_rows.append({'candidate_id':cid,'title':str(row.get('title') or ''),'search_primitive':str(row.get('search_primitive') or ''),'semantic_shadow_clear':row.get('shadow_clear') is True,'semantic_verdict':str(semantic.get('verdict') or ''),'semantic_reduction_class':str(semantic.get('reduction_class') or ''),'semantic_matched_patterns':sorted({str(value) for value in semantic.get('matched_patterns') or [] if str(value)}),'semantic_strongest_reduction':' '.join(str(semantic.get('strongest_reduction') or '').split())[:800],'semantic_exact_reduction_test':' '.join(str(semantic.get('exact_reduction_test') or '').split())[:1200],'semantic_reason':' '.join(str(semantic.get('reason') or '').split())[:1200],'semantic_lane_contract_verified':semantic.get('lane_contract_verified') is True,'semantic_lane_contract_reason':' '.join(str(semantic.get('lane_contract_reason') or '').split())[:1000],'semantic_source_refs':evidence_refs,'semantic_source_claims':[str(((candidate.get('empirical_evidence') or {}).get(key) or {}).get('claim') or '')[:1200] for key in ('source_a','source_b')],'semantic_problem_text':' '.join(str(candidate.get(key) or '') for key in ('title','irreducible_object','exact_prediction'))[:2400],'current_source_status':str(current.get('status') or ''),'current_source_verdict':str(current.get('verdict') or ''),'current_source_reduction_class':str(current.get('reduction_class') or ''),'current_source_strongest_reduction':' '.join(str(current.get('strongest_reduction') or '').split())[:800],'current_source_reason':' '.join(str(current.get('reason') or '').split())[:1200],'current_source_source_refs':current_sources,'terminal_shadow_clear':term.get('terminal_shadow_clear') is True,'live_problem_gate_compatible':term.get('live_problem_gate_compatible') is True,'paper_design_eligible':False,'scientific_authority':False,'authority':{'method':False,'experiment':False,'p0':False,'gpu':False}})
    t=terminal.get('summary') or {};m=machine.get('summary') or {};run_id=root.name
    expansion_successful=len(list(root.glob('expand-*-p*.json')));expansion_error_rows=[load(path) for path in root.glob('error-expand-*.json')];expansion_errors=len(expansion_error_rows);expansion_requested_shards=expansion_successful+expansion_errors
    expansion_parse_failures=sum(str(row.get('status') or '')=='PARSE_ERROR_ZERO_AUTHORITY' for row in expansion_error_rows)
    expansion_provider_failures=sum(str(row.get('status') or '').startswith('PROVIDER_') for row in expansion_error_rows)
    evolution_paths=list(root.glob('evolve-*.json'));evolution_error_paths=list(root.glob('error-evolve-*.json'))
    evolution_calls=len(evolution_paths)+len(evolution_error_paths)
    evolution_by_generation={1:{'requested':0,'valid':0},2:{'requested':0,'valid':0}}
    for path in evolution_paths:
        payload=load(path);match=re.search(r'evolve-g(\d+)-p\d+',path.name)
        if not match:continue
        generation=int(match.group(1));stats=evolution_by_generation.setdefault(generation,{'requested':0,'valid':0})
        children=[row for row in payload.get('children') or [] if isinstance(row,dict)]
        parent_ids=[value for value in payload.get('parent_ids') or [] if value]
        stats['requested']+=int(payload.get('requested_children') or len(parent_ids) or len(children))
        stats['valid']+=int(payload.get('valid_children') or len(children))
    formulation_calls=len(formulation_paths)+len(formulation_error_paths)
    generator_calls=expansion_successful+expansion_errors+evolution_calls+formulation_calls
    reviewer_calls=len(list(root.glob('review-p*.json')))+len(list(root.glob('error-review-*.json')))
    summary={
        'requested_raw_seeds':120,
        'expansion_requested_shards':expansion_requested_shards,
        'expansion_successful_shards':expansion_successful,
        'expansion_execution_failures':expansion_errors,
        'expansion_parse_failures':expansion_parse_failures,
        'expansion_provider_failures':expansion_provider_failures,
        'raw_seeds':int(bs.get('raw_seeds') or 0),
        'semantic_dead_end_blocks':int(bs.get('semantic_dead_end_blocks') or 0),
        'semantic_unique':int(bs.get('semantic_unique') or 0),
        'duplicate_or_near_duplicate':int(bs.get('semantic_duplicates') or 0),
        'unique_problem_families':int(bs.get('structural_clusters') or 0),
        'breadth_archive':int(bs.get('breadth_archive') or 0),
        'archive_lane_coverage':int(bs.get('archive_lane_coverage') or 0),
        'mean_archive_pairwise_distance':round(sum(distances)/len(distances),4) if distances else 0.0,
        'evolved_branches':len(evolved),
        'evolution_g1_requested':int((evolution_by_generation.get(1) or {}).get('requested') or 0),
        'evolution_g1_valid':int((evolution_by_generation.get(1) or {}).get('valid') or 0),
        'evolution_g2_requested':int((evolution_by_generation.get(2) or {}).get('requested') or 0),
        'evolution_g2_valid':int((evolution_by_generation.get(2) or {}).get('valid') or 0),
        'max_branch_depth':max([int(x.get('branch_depth') or 0) for x in evolved] or [0]),
        'formulation_requested_shards':formulation_requested_shards,
        'formulation_successful_shards':len(formulation_paths),
        'formulation_provider_failures':formulation_provider_failures,
        'formulation_parse_failures':formulation_parse_failures,
        'formulation_requested_branches':formulation_requested_branches,
        'formulation_successful_branches':successful_formulation_branches,
        'formulation_execution_censored_branches':formulation_censored_branches,
        'formulated_candidates':formulated,
        'formulation_reduction_pending':reduction_pending,
        'formulation_rejected':rejected,
        'machine_reviewable':int(m.get('reviewable') or 0),
        'machine_reduction_pending':int(m.get('reduction_pending') or 0),
        'machine_reduction_blocked':int(m.get('blocked') or 0),
        'problem_falsifier_eligible':int(m.get('problem_falsifier_eligible') or 0),
        'problem_falsifier_inventory_requested':int(falsifier_request_summary.get('inventory_requests') or 0),
        'problem_falsifier_support_qualified':int(falsifier_summary.get('support_qualified') or 0),
        'problem_falsifier_hold_support_unavailable':int(falsifier_summary.get('hold_support_unavailable') or 0),
        'problem_falsifier_executed':int(falsifier_summary.get('falsifier_executed') or 0),
        'provisional_problem_candidates':int(evidence_summary.get('provisional_problem_candidates') or 0),
        'evidence_design_selected':int(evidence_summary.get('design_selected') or 0),
        'evidence_design_pending':int(evidence_summary.get('design_pending') or 0),
        'evidence_design_invalid':int(evidence_summary.get('design_invalid') or 0),
        'evidence_wait_primary_asset':int(evidence_summary.get('wait_primary_asset') or 0),
        'evidence_operationalization_recompile_pending':int(evidence_summary.get('operationalization_recompile_pending') or 0),
        'evidence_operationalization_recompiled':int(evidence_summary.get('operationalization_recompiled') or 0),
        'evidence_operationalization_intrinsic_source_specific':int(evidence_summary.get('operationalization_intrinsic_source_specific') or 0),
        'evidence_review_pending':int(evidence_summary.get('review_pending') or 0),
        'evidence_review_clear':int(evidence_summary.get('review_clear') or 0),
        'evidence_review_revise':int(evidence_summary.get('review_revise') or 0),
        'evidence_review_blocked':int(evidence_summary.get('review_blocked') or 0),
        'evidence_substrate_preflight_pending':int(evidence_summary.get('substrate_preflight_pending') or 0),
        'evidence_substrate_ready':int(evidence_summary.get('substrate_ready') or 0),
        'evidence_harness_implementation_pending':int(evidence_summary.get('substrate_implementation_pending') or 0),
        'evidence_substrate_hold':int(evidence_summary.get('substrate_hold') or 0),
        'evidence_execution_ready':int(evidence_summary.get('execution_ready') or 0),
        'evidence_execution_completed':int(evidence_summary.get('execution_completed') or 0),
        'evidence_reduction_supported':int(evidence_summary.get('reduction_supported') or 0),
        'evidence_residual_survives':int(evidence_summary.get('residual_survives') or 0),
        'evidence_inconclusive':int(evidence_summary.get('inconclusive') or 0),
        'evidence_branch_repair_ready':int(evidence_summary.get('branch_repair_ready') or 0),
        'evidence_deferred_by_portfolio_budget':int(evidence_summary.get('deferred_by_portfolio_budget') or 0),
        'semantic_reviewed':len(reviewed),
        'semantic_clear':len(semantic_clear),
        'semantic_blocked':len(reviewed)-len(semantic_clear),
        'current_source_reviewed':int(t.get('current_source_clear') or 0)+int(t.get('current_source_blocked') or 0),
        'current_source_clear':int(t.get('current_source_clear') or 0),
        'current_source_blocked':int(t.get('current_source_blocked') or 0),
        'current_source_missing':int(t.get('current_source_missing') or 0),
        'terminal_shadow_survivors':int(t.get('terminal_shadow_survivors') or 0),
        'live_problem_gate_compatible_survivors':int(t.get('live_problem_gate_compatible_survivors') or 0),
        'live_paper_design_eligible':0,
        'generator_model_calls':generator_calls,
        'reviewer_model_calls':reviewer_calls,
        'current_source_review_receipts':int(t.get('current_source_clear') or 0)+int(t.get('current_source_blocked') or 0),
    }
    falsifier_resolved=int(summary['problem_falsifier_support_qualified'])+int(summary['problem_falsifier_hold_support_unavailable']);falsifier_eligible=int(summary['problem_falsifier_eligible'])
    terminal_status=str(terminal.get('status') or 'SHADOW_TERMINAL_INCOMPLETE_CURRENT_SOURCE_REVIEW')
    evidence_present=bool(evidence_plan)
    evidence_internal_open=sum(int(summary.get(key) or 0) for key in ('evidence_design_pending','evidence_operationalization_recompile_pending','evidence_review_pending','evidence_substrate_preflight_pending','evidence_harness_implementation_pending','evidence_execution_ready','evidence_residual_survives','evidence_branch_repair_ready'))
    # Terminal evidence dispositions must close their provisional slot. A candidate
    # held because the reviewed substrate is unavailable/budget-infeasible, or blocked
    # by independent evidence review, is scientifically unresolved as a broader idea
    # but operationally terminal for this frozen evidence-acquisition transaction.
    # Do not keep the shadow run artificially pending after such a fail-closed hold.
    evidence_unresolved=_evidence_unresolved_count(summary)
    if evidence_present and (evidence_internal_open or evidence_unresolved):terminal_status='SHADOW_EVIDENCE_ACQUISITION_PENDING'
    elif not evidence_present and falsifier_resolved!=falsifier_eligible:terminal_status='SHADOW_TERMINAL_INCOMPLETE_PROBLEM_FALSIFIER_PREFLIGHT'
    stage_runner_schema=str(qualification.get('stage_runner_required_schema') or '');control_snapshot_sha=str(qualification.get('control_snapshot_sha256') or '');control_bound=stage_runner_schema=='1.4' and bool(re.fullmatch(r'[0-9a-f]{64}',control_snapshot_sha));control_terminal_verified=False
    if control_bound:
        for label,payload in (('machine-audit',machine),('shadow-final-audit',final),('shadow-terminal-current-source-gate',terminal)):
            if str(payload.get('control_snapshot_sha256') or '')!=control_snapshot_sha:raise ValueError(f'qualified shadow public projection control mismatch:{label}')
        control_terminal_verified=True
    source_generated_at=str(qualification.get('source_generated_at') or frozen.get('generated_at') or '');source_set_sha=str(qualification.get('source_set_sha256') or frozen.get('source_set_sha256') or '');source_content_sha=str(qualification.get('source_primary_content_sha256') or primary_content_sha256([row for row in frozen.get('records') or [] if isinstance(row,dict)]));source_pool_sha=str(qualification.get('source_pool_sha256') or frozen.get('source_pool_sha256') or '')
    if source_set_sha and not re.fullmatch(r'[0-9a-f]{64}',source_set_sha):raise ValueError('shadow source-set provenance invalid')
    if not re.fullmatch(r'[0-9a-f]{64}',source_content_sha):raise ValueError('shadow primary-content provenance invalid')
    if source_pool_sha and not re.fullmatch(r'[0-9a-f]{64}',source_pool_sha):raise ValueError('shadow source-pool provenance invalid')
    return {'schema_version':'1.2-shadow-run','run_id':run_id,'status':terminal_status,'generated_at':now(),'discovery_operator_version':str(qualification.get('discovery_operator_version') or frozen.get('discovery_operator_version') or DISCOVERY_OPERATOR_VERSION),'source_generated_at':source_generated_at,'source_set_sha256':source_set_sha,'source_primary_content_sha256':source_content_sha,'source_pool_sha256':source_pool_sha,'frozen_pool_sha256':frozen.get('frozen_pool_sha256'),'stage_manifest_sha256':manifest_sha(root),'problem_falsifier_support_inventory_sha256':falsifier_inventory_sha,'stage_runner_required_schema':stage_runner_schema,'control_snapshot_sha256':control_snapshot_sha,'qualification_main_commit':str(qualification.get('main_commit') or ''),'scientific_authority':False,'policy':{'shadow_only':True,'canonical_primary_generator_queue_untouched':True,'live_source_coverage_effect':False,'fresh_primary_evidence_is_candidate_source_only':True,'source_identity_is_bounded_timestamp_and_sha_provenance':True,'execution_loss_is_not_scientific_negative':True,'control_snapshot_bound_run':control_bound,'control_snapshot_terminal_provenance_verified':control_terminal_verified,'control_snapshot_provenance_is_bounded_sha_only':True,'formulation_reduction_pending_is_not_scientific_block_or_pass':True,'machine_rechecks_reduction_pending_before_problem_falsifier':True,'problem_falsifier_preflight_must_cover_all_eligible_before_terminal_complete':not evidence_present,'problem_falsifier_hold_is_not_scientific_fail':True,'problem_falsifier_support_inventory_hash_verified':bool(falsifier_inventory_sha),'support_inventory_is_one_evidence_route_not_global_prerequisite':evidence_present,'reduction_pending_enters_bounded_evidence_acquisition_on_future_control_snapshots':True,'evidence_acquisition_authority_is_not_scientific_claim_authority':True,'evidence_residual_survival_requires_semantic_and_current_source_review':True,'current_source_web_receipt_required_after_semantic_clear':True,'missing_or_failed_current_source_reviewer_is_not_pass':True,'terminal_shadow_survivor_is_not_live_problem_gate_pass':True,'cannot_grant_live_paper_design_eligibility':True,'automatic_method_authority':False,'automatic_experiment_authority':False,'automatic_p0_authority':False,'automatic_gpu_authority':False},'summary':summary,'lane_counts':dict(base.get('lane_counts') or {}),'archive_lane_counts':dict(base.get('archive_lane_counts') or {}),'machine_blocker_counts':dict(Counter(v.split(':',1)[0] for row in machine.get('blocked') or [] for v in row.get('blockers') or [])),'candidates':candidate_rows,'authority':{'live_problem_gate':False,'paper_design':False,'method':False,'experiment':False,'p0':False,'gpu':False}}

def publish_latest_run(root:Path):
    latest=_latest_shadow_run(root)
    if not GEN_JSON.exists() or not QUEUE_JSON.exists():raise ValueError('shadow-history-state-required-before-latest-run-publication')
    state=load(GEN_JSON);queue=load(QUEUE_JSON)
    if state.get('scientific_authority') is not False or (state.get('policy') or {}).get('shadow_only') is not True:raise ValueError('existing-shadow-portfolio-history-invalid')
    if queue.get('scientific_authority') is not False or (queue.get('policy') or {}).get('shadow_only') is not True:raise ValueError('existing-shadow-queue-history-invalid')
    state['generated_at']=now();state['latest_run_id']=latest['run_id'];state['latest_run']=latest;state['scientific_authority']=False
    queue['generated_at']=now();queue['latest_run_id']=latest['run_id'];queue['latest_run']={'run_id':latest['run_id'],'status':latest['status'],'summary':{'semantic_clear_before_current_source':latest['summary']['semantic_clear'],'current_source_clear':latest['summary']['current_source_clear'],'current_source_blocked':latest['summary']['current_source_blocked'],'current_source_missing':latest['summary']['current_source_missing'],'terminal_shadow_survivors':latest['summary']['terminal_shadow_survivors'],'live_problem_gate_compatible_survivors':latest['summary']['live_problem_gate_compatible_survivors'],'live_paper_design_eligible':0},'scientific_authority':False,'authority':{'canonical_queue':False,'paper_design':False,'method':False,'experiment':False,'p0':False,'gpu':False}};queue['scientific_authority']=False
    GEN_JSON.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');GEN_JS.write_text('window.PAPER_FIRST_PROBLEM_SEARCH_PORTFOLIO = '+json.dumps(state,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    QUEUE_JSON.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');QUEUE_JS.write_text('window.PAPER_FIRST_PROBLEM_SEARCH_PORTFOLIO_QUEUE = '+json.dumps(queue,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    return {'latest_run_id':latest['run_id'],'summary':latest['summary'],'scientific_authority':False}

def publish(root:Path):
    if (root/'shadow-terminal-current-source-gate.json').exists():return publish_latest_run(root)
    base=load(root/'base.json'); frozen=load(root/'frozen-primary-evidence-pool.json'); machine=load(root/'machine-audit.json')
    reviewed=rows(root,'review-p*.json','candidates'); evolved=rows(root,'evolve-*.json','children')
    live=pending=dead=0
    for path in root.glob('formulate-p*.json'):
        payload=load(path); live+=len(payload.get('candidates') or []); pending+=len(payload.get('reduction_pending') or []); dead+=len(payload.get('rejected') or [])
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
    portfolio={'schema_version':'1.0','frozen_pool_sha256':frozen.get('frozen_pool_sha256'),'stage_manifest_sha256':manifest_sha(root),'scientific_authority':False,'policy':{'expansion_precedes_reduction':True,'diversity_archive_precedes_quality_selection':True,'qd_parent_selection':True,'lane_specific_source_minimum':True,'mature_theory_veto_delayed_until_formulation':True,'reduction_falsifiability_contract_required':True,'formulation_reduction_pending_is_zero_authority':True,'scheduler_rollover_cannot_change_frozen_transaction':True,'automatic_method_authority':False,'automatic_experiment_authority':False,'automatic_p0_authority':False},'summary':{'requested_raw_seeds':120,'raw_seeds':bs.get('raw_seeds',0),'semantic_unique':bs.get('semantic_unique',0),'duplicate_or_near_duplicate':bs.get('semantic_duplicates',0),'unique_problem_families':bs.get('structural_clusters',0),'breadth_archive':bs.get('breadth_archive',0),'archive_lane_coverage':bs.get('archive_lane_coverage',0),'mean_archive_pairwise_distance':summary['archive_pairwise_distance'],'evolved_branches':len(evolved),'max_branch_depth':summary['max_branch_depth'],'formulated_candidates':live,'formulation_reduction_pending':pending,'formulation_rejected':dead,'machine_reviewable':(machine.get('summary') or {}).get('reviewable',0),'machine_reduction_pending':(machine.get('summary') or {}).get('reduction_pending',0),'machine_reduction_blocked':(machine.get('summary') or {}).get('blocked',0),'semantic_reviewed':len(reviewed),'semantic_clear':len(clear),'semantic_blocked':len(blocked),'counterfactual_problem_gate_passed':queue['summary']['passed_problem_gate'],'live_paper_design_eligible':0,'generator_model_calls':summary['portfolio_calls'],'reviewer_model_calls':len(list(root.glob('review-p*.json')))},'lane_counts':base.get('lane_counts') or {},'archive_lane_counts':base.get('archive_lane_counts') or {},'archive_counts':{k:len(v or []) for k,v in archives.items()},'machine_blocker_counts':dict(blockers),'passed_candidate_ids':[x['candidate_id'] for x in queue.get('passed') or []]}
    previous=load_problem_generator_state(GEN_JSON); run_id='search-portfolio-20260813-r1'; refs=sorted(str(r.get('ref')) for r in frozen.get('records') or [] if r.get('ref')); receipt={'run_id':run_id,'pool_sha256':frozen.get('frozen_pool_sha256'),'source_refs':refs,'status':'SHADOW_PORTFOLIO_COMPLETE','requested_model':'ark-code-latest','resolved_model':'doubao-seed-evolving','raw_sha256':portfolio['stage_manifest_sha256'],'scientific_authority':False,'live_source_coverage_effect':False}
    receipts=[dict(x) for x in ((previous.get('saturation_memory') or {}).get('portable_review_receipts') or []) if isinstance(x,dict) and x.get('scientific_authority') is False]+[receipt]; receipts=list({str(x.get('run_id')):x for x in receipts if x.get('run_id')}.values())[-64:]; passed_ids=set(portfolio['passed_candidate_ids'])
    lane_counts=base.get('lane_counts') or {};lane_rows=[{'search_primitive':lane,'status':'EXPANDED' if int(lane_counts.get(lane) or 0)>0 else 'EMPTY','raw_seed_count':int(lane_counts.get(lane) or 0),'reason':'Shadow Search Portfolio expansion produced grounded seeds.' if int(lane_counts.get(lane) or 0)>0 else 'No machine-valid grounded seed survived shadow expansion.'} for lane in SEARCH_PORTFOLIO_PRIMITIVES];search_diagnostics={'search_primitive_priority':list(SEARCH_PORTFOLIO_PRIMITIVES),'search_primitive_audit_complete':True,'search_primitive_audit':lane_rows,'scientific_authority':False}
    shadow_policy=_base_policy(portfolio=True);shadow_policy.update({'scientific_authority':False,'shadow_only':True,'canonical_primary_generator_queue_untouched':True,'cannot_create_live_portable_review_receipt':True,'cannot_grant_live_paper_design_eligibility':True})
    state={'schema_version':'3.2-shadow','generated_at':now(),'run_id':run_id,'status':'SHADOW_PORTFOLIO_COMPLETE','scientific_authority':False,'generator_model':'ark-code-latest','reviewer_model':'glm-5.2','policy':shadow_policy,'summary':summary,'search_diagnostics':search_diagnostics,'search_portfolio':portfolio,'generation_notes':f"Shadow Search Portfolio: raw={bs.get('raw_seeds',0)}, unique={bs.get('semantic_unique',0)}, evolved={len(evolved)}, formulated={live}, machine-reviewable={(machine.get('summary') or {}).get('reviewable',0)}, counterfactual Problem-Gate PASS={queue['summary']['passed_problem_gate']}. No live Paper/Method/Experiment/P0 authority.",'raw_artifacts':{'generator':{'sha256':portfolio['stage_manifest_sha256'],'requested_model':'ark-code-latest','resolved_model':'doubao-seed-evolving','portfolio':True,'calls':summary['portfolio_calls']},'semantic_reviewer':{'requested_model':'glm-5.2','resolved_model':'glm-5-2-260617','calls':len(list(root.glob('review-p*.json')))}},'shadow_memory':{'live_source_coverage_effect':False,'current_shadow_receipt':receipt,'scientific_authority':False},'candidates':[{'candidate_id':c['candidate_id'],'title':c['title'],'search_primitive':c['discovery_lane'],'semantic_verdict':(c.get('semantic_reduction_review') or {}).get('verdict'),'counterfactual_problem_gate_pass':c['candidate_id'] in passed_ids,'paper_design_eligible':False,'scientific_authority':False,'authority':{'method':False,'experiment':False,'p0':False,'gpu':False}} for c in reviewed]}
    GEN_JSON.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); GEN_JS.write_text('window.PAPER_FIRST_PROBLEM_SEARCH_PORTFOLIO = '+json.dumps(state,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    return {'generator':summary,'portfolio':portfolio['summary'],'problem_gate':queue['summary'],'passed':portfolio['passed_candidate_ids']}

if __name__=='__main__':
    import argparse; p=argparse.ArgumentParser();p.add_argument('run_root',type=Path);a=p.parse_args();print(json.dumps(publish(a.run_root),ensure_ascii=False,indent=2))
