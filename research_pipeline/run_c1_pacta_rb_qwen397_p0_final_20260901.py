#!/usr/bin/env python3
"""Final four-arm first-decision measurement and analysis for Qwen397 PACTA P0."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from typing import Any
from research_pipeline.c1_pacta_rb_qwen397 import ARMS,atomic_json,build_final_schedule,sha256_text,tv
from research_pipeline.c1_pacta_rb_qwen397_p0_core import *
from research_pipeline.run_c1_pacta_rb_qwen397_p0_stages_20260901 import binder_rows,jsonl,pilot_units,policy_once,writer_rows

def final(root:Path)->dict[str,Any]:
 shadow=load(root/'shadow-result.json')
 if shadow.get('status')!='SHADOW_GATE_PASS':raise RuntimeError('shadow gate not passed')
 if (root/'final-result.json').exists() or (root/'final'/'outcomes.jsonl').exists():raise RuntimeError('final phase exists; no retry/overwrite')
 pilot=pilot_units(root);by={u['unit_id']:u for u in pilot};mem=writer_rows(root);notes=binder_rows(root);schedule=build_final_schedule(pilot,set(shadow['pacta_open']),set(shadow['random_open']))
 if len(schedule)!=288:raise RuntimeError('final geometry drift')
 inputs=[]
 for c in schedule:
  u=by[c['unit_id']];m=mem[(u['unit_id'],c['branch'])]['memory'];n=notes[(u['unit_id'],c['branch'])]['binding'] if c['uses_scb'] else None
  inputs.append({**c,'prompt_sha256':sha256_text(json.dumps(policy_messages(u,m,n),ensure_ascii=False,sort_keys=True)),'memory_sha256':sha256_text(m),'binding_sha256':'' if n is None else sha256_text(n)})
 jsonl(root/'final-schedule.jsonl',schedule);jsonl(root/'final-inputs.jsonl',inputs)
 b=binding();provider=Provider(require_key(),root,b['requested_model'],b['resolved_model']);out=[]
 for c in schedule:
  u=by[c['unit_id']];m=mem[(u['unit_id'],c['branch'])]['memory'];n=notes[(u['unit_id'],c['branch'])]['binding'] if c['uses_scb'] else None;out.append(policy_once(provider,'final',c,u,m,n))
 jsonl(root/'final'/'outcomes.jsonl',out);per=[]
 pacta_open=set(shadow['pacta_open'])
 for u in pilot:
  r={'unit_id':u['unit_id'],'gate_open':u['unit_id'] in pacta_open}
  for arm in ARMS:
   ss=[x['action_signature'] for x in out if x['unit_id']==u['unit_id'] and x['arm']==arm and x['branch']=='success'];ff=[x['action_signature'] for x in out if x['unit_id']==u['unit_id'] and x['arm']==arm and x['branch']=='failure'];r['U_'+arm]=tv(ss,ff)
  r['D_select']=r['U_A3_PACTA']-r['U_A2_RATE_MATCHED_RANDOM'];r['A3_minus_A1']=r['U_A3_PACTA']-r['U_A1_SCB_ALWAYS'];r['A3_minus_A0']=r['U_A3_PACTA']-r['U_A0_NATIVE'];r['SCB_effect']=r['U_A1_SCB_ALWAYS']-r['U_A0_NATIVE'];per.append(r)
 def mean(k:str)->float:return sum(float(r[k]) for r in per)/len(per)
 d=[r['D_select'] for r in per];pos=sum(x>0 for x in d);neg=sum(x<0 for x in d);zero=sum(x==0 for x in d);md=mean('D_select');a30=mean('A3_minus_A0');a31=mean('A3_minus_A1');oe=[r['SCB_effect'] for r in per if r['gate_open']];ce=[r['SCB_effect'] for r in per if not r['gate_open']];mopen=sum(oe)/len(oe);mclosed=sum(ce)/len(ce);sq=sorted((float(x)**2 for x in d),reverse=True);den=sum(sq);top1=0.0 if den==0 else sq[0]/den;top2=0.0 if den==0 else sum(sq[:2])/den
 checks={'all_288_complete':len(out)==288,'gate_nondegenerate':bool(shadow['geometry_pass']),'mean_D_select_ge_0_05':md>=.05,'positive_gt_negative':pos>neg,'mean_A3_A0_gt_0':a30>0,'mean_A3_A1_ge_0':a31>=0};passed=all(checks.values())
 if passed:status='PACTA_RB_QWEN397_PRELIMINARY_SIGNAL'
 elif md<0:status='PACTA_SELECTION_NEGATIVE_ON_QUALIFIED_RB_QWEN397_PILOT'
 else:status='PACTA_SELECTION_UNSUPPORTED_OR_HETEROGENEOUS_ON_RB_QWEN397_PILOT'
 result={'schema_version':1,'created_at_utc':now(),'status':status,'calls':288,**provider.phase_usage(),'per_unit':per,'means':{arm:mean('U_'+arm) for arm in ARMS},'mean_D_select':md,'D_select_signs':{'positive':pos,'negative':neg,'zero':zero},'mean_A3_minus_A1':a31,'mean_A3_minus_A0':a30,'M_open':mopen,'M_closed':mclosed,'M_open_minus_M_closed':mopen-mclosed,'effect_concentration':{'top1_squared_fraction':top1,'top2_squared_fraction':top2},'pilot_gate':{'checks':checks,'pass':passed},'sealed_provider_calls':0,'terminal_executed':False,'confirmatory_executed':False,'claim_authority':'PRELIMINARY_SINGLE_BACKBONE_P0_ONLY' if passed else 'QUALIFIED_PILOT_NO_POSITIVE_METHOD_AUTHORITY','active_manuscript':'R9','R10_created':False};atomic_json(root/'final-result.json',result);return result

def main()->None:
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=DEFAULT_RUN);a=ap.parse_args();print(json.dumps(final(a.root),ensure_ascii=False,sort_keys=True))
if __name__=='__main__':main()
