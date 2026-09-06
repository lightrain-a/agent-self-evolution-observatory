from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline import agent_constraint_externality_atomgit_repeat_common as c
from research_pipeline.agent_constraint_externality_confirmatory_preexec import decide_repeat_count_after_two, decide_N_star
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT=Path(__file__).resolve().parents[1]; G=ROOT/'generated'
RESULT=G/'agent-constraint-externality-atomgit-repeat-r2-result-20260906.json'
MEASUREMENTS=G/'agent-constraint-externality-atomgit-repeat-r2-measurements-20260906.json'
OUTPUT=G/'agent-constraint-externality-atomgit-repeat-r2-adjudication-20260906.json'

class AdjudicationError(RuntimeError): pass

def validate_rows(rows:list[dict[str,Any]])->None:
    if len(rows)!=72: raise AdjudicationError('R2 adjudication requires exactly 72 rows')
    expected={(u['family_id'],u['arm'],u['branch'],u['repeat']) for u in c.units()}; observed={(str(r['family_id']),str(r['arm']),str(r['branch']),int(r['repeat'])) for r in rows}
    if observed!=expected or len(observed)!=72: raise AdjudicationError('R2 measurement matrix drift')
    index={(str(r['family_id']),str(r['arm']),str(r['branch']),int(r['repeat'])):r for r in rows}
    for fid in c.family_index():
        repair=c.repair_record(fid)['repair_sha256']
        for arm in c.ARMS:
            for repeat in c.REPEATS:
                no=index[(fid,arm,'NO_UPDATE',repeat)]; real=index[(fid,arm,'REAL_REPAIR',repeat)]
                if no.get('scientific_state_sha256')!=real.get('scientific_state_sha256') or not no.get('scientific_state_sha256'): raise AdjudicationError(f'paired scientific state mismatch: {fid}/{arm}/{repeat}')
                if no.get('repair_sha256') is not None: raise AdjudicationError('NO_UPDATE repair leakage')
                if real.get('repair_sha256')!=repair: raise AdjudicationError('REAL_REPAIR SHA drift')
                if no.get('valid') is not True or real.get('valid') is not True: raise AdjudicationError('technical invalidity must stop before scientific adjudication')
                for row in (no,real):
                    if not isinstance(row.get('target_success'),bool): raise AdjudicationError('target_success type drift')
                    x=float(row.get('crr'))
                    if not 0.0<=x<=1.0: raise AdjudicationError('CRR range drift')

def adjudicate_rows(rows:list[dict[str,Any]])->dict[str,Any]:
    validate_rows(rows); repeat=decide_repeat_count_after_two(rows)
    if repeat['status']=='REPEAT_QUALIFICATION_PASS_R2':
        precision=decide_N_star(rows,2); status='ATOMGIT_REPEAT_DEV_R2_PASS_PRECISION_FROZEN_CONFIRMATORY_EXECUTION_CLOSED' if precision['status']=='PRECISION_QUALIFICATION_PASS' else 'ATOMGIT_REPEAT_DEV_R2_PASS_PRECISION_STOP_N24_INSUFFICIENT'
        return {'status':status,'R_star':2,'repeat_decision':repeat,'precision_decision':precision,'R3_required':False}
    if repeat['status']=='REPEAT_QUALIFICATION_REQUIRE_R3':
        return {'status':'ATOMGIT_REPEAT_DEV_R3_REQUIRED_AUTHORITY_CLOSED','R_star':None,'repeat_decision':repeat,'precision_decision':None,'R3_required':True}
    return {'status':'ATOMGIT_REPEAT_DEV_STABILITY_STOP_NO_CONFIRMATORY','R_star':None,'repeat_decision':repeat,'precision_decision':None,'R3_required':False}

def build()->dict[str,Any]:
    result=c.readj(RESULT)
    if result.get('object_id')!=OBJECT_ID or result.get('status')!='ATOMGIT_REPEAT_DEV_R2_PANEL_COMPLETE_PENDING_DIRECTION_BLIND_ADJUDICATION': raise AdjudicationError('R2 terminal result not ready')
    h=result.get('content_sha256'); y=dict(result); y.pop('content_sha256',None)
    if h!=sha256_value(y): raise AdjudicationError('R2 result content drift')
    payload=c.readj(MEASUREMENTS); rows=payload.get('rows')
    if not isinstance(rows,list) or payload.get('ledger_sha256')!=result.get('ledger_sha256'): raise AdjudicationError('R2 measurement/ledger binding drift')
    decision=adjudicate_rows(rows)
    out={'schema_version':'ace-repeat-dev-r2-adjudication-v1','object_id':OBJECT_ID,**decision,'r2_result_content_sha256':result['content_sha256'],'r2_result_file_sha256':sha256_file(RESULT),'measurements_file_sha256':sha256_file(MEASUREMENTS),'ledger_sha256':result['ledger_sha256'],'development_effect_mean_emitted':False,'development_effect_sign_emitted':False,'selection_uses_effect_direction':False,'provider_requests_created':0,'scientific_confirmatory_outcomes_created':0,'authority':{'development_repeat_qualification_closed':True,'r3_execution':False,'target_only_verification':False,'confirmatory_source_repair':False,'rq1_rq2':False,'rq3':False,'rq4':False,'paper_claim':False}}
    out['content_sha256']=sha256_value(out); c.writej(OUTPUT,out); return out

def main()->None: print(json.dumps(build(),ensure_ascii=False,sort_keys=True))
if __name__=='__main__': main()
