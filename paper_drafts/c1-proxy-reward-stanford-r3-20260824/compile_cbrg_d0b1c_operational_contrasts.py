#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re
from collections import Counter
from pathlib import Path
from typing import Any
import pandas as pd

PAPER_ID='D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
STATUS='D0B1C_OPERATIONAL_CONTRAST_COMPILED_EXACT_LOCATOR_PARTIAL_SEMANTIC_HOLD'
DECISION='D0B1C_COMPILER_GO_LOCATOR_PARTIAL_FAIL_CLOSED_D0B2_READY'
HERE=Path(__file__).resolve().parent
V1=HERE/'cbrg-d0b-receipt-structural-audit-20260824.json'
B1=HERE/'cbrg-d0b1-intervention-identifiability-audit-20260824.json'
OUT=HERE/'cbrg-d0b1c-operational-contrast-evidence-locator-20260824.json'
V1_SHA='3f245fb99237c0da8f0ca34cd2c619b2d92bf0dc44245b53319f172e02c921ef'
B1_SHA='6b88cfb1ab9571db8c05714c54e087e77d340576d6df81a6909f4eb7b370eea0'
STOP=set('the a an and or to of in on for with from by is are was were be been being this that these those it its as at if when then than into out over under you your user task agent current page step use using used can could should would will may must do does did not no'.split())

def sha_b(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def sha_p(p:Path)->str:return sha_b(p.read_bytes())
def sha_t(x:str)->str:return sha_b(x.encode())
def jsha(x:Any)->str:return sha_t(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')))
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text(encoding='utf-8'))
def req(x:bool,msg:str):
    if not x: raise RuntimeError(msg)
def norm(x:Any)->str:return ' '.join(str(x or '').split())
def toks(x:str)->set[str]:return {t for t in re.findall(r'[a-z0-9]+',x.lower()) if len(t)>=3 and t not in STOP}
def jac(a:str,b:str)->float:
    A,B=toks(a),toks(b)
    return len(A&B)/len(A|B) if A and B else 0.0

def memtext(p:Path)->str:
    raw=p.read_text(encoding='utf-8')
    if p.suffix=='.json':
        try:
            d=json.loads(raw)
            if isinstance(d,dict) and str(d.get('text') or '').strip(): return str(d['text'])
        except json.JSONDecodeError: pass
    return raw

def atoms(text:str)->list[dict[str,Any]]:
    out=[]
    for line in text.splitlines():
        m=re.match(r'^##\s+(Title|Description|Content):\s*(.+?)\s*$',line.strip())
        if m: out.append({'field':m.group(1).lower(),'text':m.group(2).strip()})
    if not out:
        out=[{'field':'unknown','text':m.group(1).strip()} for m in re.finditer(r'(?:Title|Description|Content):\s*([^\n#]+)',text)]
    req(bool(out),'no memory atoms')
    for i,a in enumerate(out):a.update(index=i,text_sha256=sha_t(a['text']))
    return out

def traj_index(p:Path)->dict[int,str]:
    f=pd.read_parquet(p);out={}
    for _,r in f.iterrows():out[int(r.task_id)]=str(r.trajectory_json)
    return out

def evidence_lines(traj:str)->list[dict[str,Any]]:
    d=json.loads(traj);out=[];seen=set();order=0
    for sid,step in sorted((d.get('steps') or {}).items(),key=lambda kv:int(kv[0])):
        cs=((step or {}).get('input_messages') or {}).get('contents') or []
        if not cs: continue
        x=str(cs[-1].get('content') or '')
        if '[Current state starts here]' not in x: continue
        state=x.split('[Current state starts here]',1)[1].strip();ss=sha_t(state)
        if ss in seen: continue
        seen.add(ss)
        for li,line in enumerate(state.splitlines()):
            z=norm(line)
            if len(z)<4:continue
            ident={'state_sha256':ss,'state_order':order,'source_step_id':int(sid),'line_index':li,'line_sha256':sha_t(z)}
            out.append({**ident,'evidence_ref_id':'C1E-'+jsha(ident)[:24],'text':z})
        order+=1
    req(bool(out),'no outcome-independent evidence lines')
    return out

def main():
    req(sha_p(V1)==V1_SHA,'v1 SHA drift');req(sha_p(B1)==B1_SHA,'B1 SHA drift')
    v1,b1=load(V1),load(B1)
    lin=b1['current_24_pair_intervention_lineage']
    req(lin['operational_branch_contrast_identifiable'] is True,'B1 operational contrast not GO')
    req(lin['atom_level_causal_residual_purity_certified'] is False,'causal purity unexpectedly certified')
    bind=v1['source_bindings']
    traj={'shopping':traj_index(Path(bind['shopping_parquet']['path'])),'reddit':traj_index(Path(bind['reddit_parquet']['path']))}
    units=[];sources=[];located=0;unlocated=0;same_field=0;span_total=0
    for r in v1['receipts']:
        dom,task=str(r['domain']),int(r['source_task']);spans=evidence_lines(traj[dom][task]);span_total+=len(spans)
        by={}
        for cond in ('success','failure'):
            text=memtext(Path(r['branch_memories'][cond]['path']))
            req(sha_t(text)==r['branch_memories'][cond]['sha256'],f'memory SHA drift {dom}/{task}/{cond}')
            aa=atoms(text);old=r['residual_claim_identity']['claims'][cond];req(len(aa)==len(old),'atom count drift')
            for a,o in zip(aa,old):req(a['text_sha256']==o['text_sha256'],'atom SHA drift');a['historical_atom_id']=o['residual_claim_id']
            by[cond]=aa
        src_loc=src_un=0
        for cond,opp in (('success','failure'),('failure','success')):
            for a in by[cond]:
                cand=[b for b in by[opp] if b['field']==a['field']]
                sf=bool(cand);cand=cand or by[opp]
                best=min(cand,key=lambda b:(-jac(a['text'],b['text']),b['index']))
                align=jac(a['text'],best['text']);same_field+=int(sf)
                scored=[(jac(a['text'],s['text']),i,s) for i,s in enumerate(spans)]
                score,_,ev=min(scored,key=lambda x:(-x[0],x[1]))
                if score>0:
                    loc={'status':'EXACT_LEXICAL_ANCHOR','evidence_ref_id':ev['evidence_ref_id'],'state_sha256':ev['state_sha256'],'state_order':ev['state_order'],'source_step_id':ev['source_step_id'],'line_index':ev['line_index'],'line_sha256':ev['line_sha256'],'lexical_jaccard':score};located+=1;src_loc+=1
                else:
                    loc={'status':'NO_NONZERO_LEXICAL_ANCHOR','evidence_ref_id':None,'lexical_jaccard':0.0};unlocated+=1;src_un+=1
                ident={'paper_id':PAPER_ID,'domain':dom,'source_task':task,'trajectory_projection_sha256':r['trajectory_lineage']['pre_writer_trajectory_projection_sha256'],'focal_condition':cond,'focal_field':a['field'],'focal_index':a['index'],'focal_sha256':a['text_sha256'],'opposite_condition':opp,'opposite_field':best['field'],'opposite_index':best['index'],'opposite_sha256':best['text_sha256'],'compiler_version':'C1_D0B1C_OPERATIONAL_CONTRAST_V1'}
                units.append({'branch_contrast_unit_id':'C1BC-'+jsha(ident)[:24],'domain':dom,'source_task':task,'trajectory_projection_sha256':r['trajectory_lineage']['pre_writer_trajectory_projection_sha256'],'focal':{'condition':cond,'field':a['field'],'field_index':a['index'],'text_sha256':a['text_sha256'],'historical_memory_atom_id':a['historical_atom_id']},'opposite_counterpart':{'condition':opp,'field':best['field'],'field_index':best['index'],'text_sha256':best['text_sha256'],'historical_memory_atom_id':best['historical_atom_id'],'same_field_alignment':sf,'lexical_jaccard':align,'operational_residual_weight':1.0-align},'evidence_locator':loc,'causal_purity_certified':False,'semantic_validity':'UNADJUDICATED_LOCATOR_ONLY','authority_decision':'WITHHOLD_ALL_BRANCH_AUTHORITY'})
        sources.append({'domain':dom,'source_task':task,'branch_contrast_units':len(by['success'])+len(by['failure']),'evidence_lines':len(spans),'located_units':src_loc,'unlocated_units':src_un})
    req(len(units)==423,f'unit count {len(units)}');req(same_field==423,f'same-field {same_field}');req(located==397,f'located {located}');req(unlocated==26,f'unlocated {unlocated}')
    req(all(u['causal_purity_certified'] is False and u['semantic_validity']=='UNADJUDICATED_LOCATOR_ONLY' and u['authority_decision']=='WITHHOLD_ALL_BRANCH_AUTHORITY' for u in units),'authority leak')
    weights=[u['opposite_counterpart']['operational_residual_weight'] for u in units];anchors=[u['evidence_locator']['lexical_jaccard'] for u in units]
    out={'schema_version':'1.0','artifact_type':'c1-d0b1c-operational-contrast-evidence-locator','paper_id':PAPER_ID,'status':STATUS,'decision':DECISION,'input_bindings':{'d0b_envelope_v1':{'path':str(V1.relative_to(HERE.parents[1])),'sha256':V1_SHA},'d0b1_identifiability':{'path':str(B1.relative_to(HERE.parents[1])),'sha256':B1_SHA}},'operational_definition':{'equation':'D_tau,r,i = focal atom_i(W_r(tau)) paired with the highest lexical-overlap same-field atom in W_not-r(tau)','paired_difference_is_operational_not_atom_level_causal_purity':True,'alignment_similarity_is_baseline_infrastructure_not_novelty':True,'thresholded_residual_membership':False},'evidence_locator_contract':{'source':'outcome-excluded released pre-writer browser-state lines from the same frozen trajectory','exact_reference_fields':['state_sha256','state_order','source_step_id','line_index','line_sha256'],'nonzero_lexical_overlap_required_for_exact_anchor':True,'no_anchor_forces_fail_closed_unlocated_state':True,'lexical_similarity_is_locator_only_not_validity':True,'treatment_label_used_as_evidence':False,'terminal_reward_or_rubric_used_as_evidence':False,'downstream_outcome_used_as_evidence':False},'summary':{'paired_sources':24,'directional_branch_contrast_units':423,'same_field_opposite_counterpart_units':same_field,'units_with_exact_nonzero_lexical_evidence_anchor':located,'units_without_nonzero_lexical_evidence_anchor':unlocated,'locator_coverage':located/423,'candidate_evidence_lines_scanned':span_total,'semantic_validity_adjudicated_units':0,'supported_units':0,'contradicted_units':0,'unverifiable_units':0,'nonzero_branch_authority_units':0,'mean_operational_residual_weight':sum(weights)/len(weights),'mean_best_lexical_anchor_including_zero':sum(anchors)/len(anchors)},'gate_interpretation':{'B1c_operational_compiler':'GO','B1c_exact_evidence_locator':'PARTIAL_397_OF_423','B1c_unlocated_policy':'26 units remain fail-closed and are candidates for UNVERIFIABLE in B2','B2':'READY_FOR_ZERO_CALL_SEMANTIC_DESIGN_NOT_EXECUTION','meaning':'Operational paired contrast identities are reproducible. Exact lexical evidence anchors exist for 397/423 units; 26 are intentionally left unlocated rather than given similarity-only pseudo-evidence. No semantic support or behavioral authority is granted.'},'next_required_gate':'D0-B2 zero-call semantic adjudication: assign SUPPORTED/CONTRADICTED/UNVERIFIABLE with the 26 unlocated units forced to UNVERIFIABLE; compare any evidence-validity signal against similarity/applicability baselines; keep all branch authority zero during D0.','stop_condition':'STOP/MERGE if B2 reduces to lexical/semantic similarity, cannot distinguish support from contradiction without outcome leakage, or produces a degenerate evidence signal.','source_summaries':sources,'branch_contrast_units':units,'provider_calls':0,'gpu_runs':0,'scientific_authority':False,'experiment_authority':False,'provider_call_authority':False,'gpu_authority':False,'claim_expansion_authority':False,'submission_authority':False}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');print(json.dumps({'status':STATUS,'decision':DECISION,**out['summary']},indent=2,sort_keys=True))
if __name__=='__main__':main()
