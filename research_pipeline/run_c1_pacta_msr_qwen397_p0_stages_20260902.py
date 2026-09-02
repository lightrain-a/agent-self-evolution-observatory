#!/usr/bin/env python3
"""Prepare/probe/writer/binder/dual-shadow stages for fresh PACTA-MSR/Qwen397 P0."""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
from typing import Any
import yaml
from research_pipeline.c1_pacta_rb_qwen397 import atomic_bytes,atomic_json,sha256_file
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime_v7 import Container
from research_pipeline.c1_pacta_msr_qwen397_p0_core import (
 ROOT,CONFIG,EXECUTION_CONTRACT,MODEL,Provider,binding_prompt,binding_state,gate,load,load_instructions,memory_valid,now,parse_action,phase_usage,pilot_units,policy_messages,probe_specs,safe_id,sha,writer_prompt
)
DEFAULT=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-qwen397-p0-20260902-v1')
SHADOW_SALT='C1-PACTA-MSR-QWEN397-DUAL-SHADOW-v1'
SELECTORS=('G0_STEP0','GPLUS_MATCHED_REVEAL');BRANCHES=('success','failure')

def require_key()->str:
 k=os.environ.get('AA_API_KEY','')
 if not k:raise RuntimeError('STOP_PROVIDER_CREDENTIAL_NOT_CONFIGURED')
 return k
def append(path:Path,row:dict[str,Any])->None:
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('a',encoding='utf-8') as h:h.write(json.dumps(row,sort_keys=True)+'\n');h.flush();os.fsync(h.fileno())
def phase_clean(root:Path,stage:str)->None:
 d=root/stage
 if d.exists() and any(d.rglob('*')):raise RuntimeError(f'{stage} phase already has artifacts; no scientific resume')
 if (root/f'{stage}-result.json').exists():raise RuntimeError(f'{stage} result exists; no overwrite')
def schedule_shadow(pilot:list[dict[str,Any]])->list[dict[str,Any]]:
 out=[]
 for u in pilot:
  for selector in SELECTORS:
   for br in BRANCHES:
    for block in (1,2):
     for rep in range(1,7):
      case=f"{u['unit_id']}__{selector}__{br}__b{block}__r{rep}";out.append({'case_id':case,'unit_id':u['unit_id'],'selector':selector,'branch':br,'block':block,'replicate':rep,'order_key':sha(SHADOW_SALT+'|'+case)})
 out.sort(key=lambda x:(x['order_key'],x['case_id']))
 if len(out)!=384:raise AssertionError('dual shadow geometry')
 return out
def prepare(root:Path)->dict[str,Any]:
 if root.exists():raise RuntimeError('P0 root exists; no overwrite')
 pilot,sealed,random=pilot_units();specs=probe_specs();root.mkdir(parents=True)
 if any(x['unit_id'] not in specs for x in pilot):raise RuntimeError('probe spec missing')
 shadow=schedule_shadow(pilot)
 contract={'schema_version':1,'created_at_utc':now(),'status':'MSR_P0_PREPARE_PASS','source_support_sha256':sha256_file(Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-qwen397-source-20260902-v1/support-audit.json')),'execution_contract_sha256':sha256_file(EXECUTION_CONTRACT),'pilot':[x['unit_id'] for x in pilot],'sealed':sealed,'random_gate_ranking':random,'probe_specs_sha256':sha256_file(ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-probe-specs-v2-20260902.json'),'writer_calls':0,'binder_calls':0,'probe_provider_calls':0,'shadow_calls':0,'final_calls':0,'sealed_provider_calls':0,'terminal':False,'confirmatory':False}
 atomic_json(root/'contract.json',contract);atomic_bytes(root/'shadow-schedule.jsonl',''.join(json.dumps(x,sort_keys=True)+'\n' for x in shadow).encode());atomic_json(root/'prepare-audit.json',{'schema_version':1,'created_at_utc':now(),'status':'MSR_P0_PREPARE_PASS','contract_sha256':sha256_file(root/'contract.json'),'shadow_schedule_sha256':sha256_file(root/'shadow-schedule.jsonl'),'pilot_count':8,'sealed_count':2,'shadow_calls_planned':384,'provider_calls':0})
 return load(root/'prepare-audit.json')
def probe(root:Path)->dict[str,Any]:
 phase_clean(root,'probe');pilot,sealed,_=pilot_units();specs=probe_specs();rows=[]
 for u in pilot:
  s=specs[u['unit_id']];pr=root/'probe'/safe_id(u['unit_id']);c=None
  try:
   c=Container(s['future_digest_ref'],s['future_base_commit'],pr);obs=c.execute(s['command']);obsp=pr/'observation.json';obssha=atomic_bytes(obsp,(json.dumps(obs,ensure_ascii=False,sort_keys=True)+'\n').encode());head=c._git('rev-parse','HEAD').stdout.strip();clean=c._git('status','--porcelain').stdout==''
   passed=(not obs['timeout'] and obs['returncode']==0 and head==s['future_base_commit'] and clean)
   row={'unit_id':u['unit_id'],'future_task_id':u['future_task_id'],'command':s['command'],'command_sha256':s['command_sha256'],'observation':obs,'observation_path':str(obsp),'observation_sha256':obssha,'post_probe_head':head,'post_probe_head_exact':head==s['future_base_commit'],'post_probe_clean':clean,'pass':passed,'provider_calls':0}
   atomic_json(pr/'probe.json',row);rows.append(row)
   if not passed:raise RuntimeError('HOLD_MSR_PROBE_EXECUTION')
  finally:
   if c is not None:c.cleanup()
 if len(rows)!=8:raise RuntimeError('probe geometry')
 out={'schema_version':1,'created_at_utc':now(),'status':'MSR_PROBE_8_PASS','rows':rows,'provider_calls':0,'sealed_probe_executions':0,'sealed':sealed};atomic_json(root/'probe-result.json',out);return out
def writer(root:Path)->dict[str,Any]:
 phase_clean(root,'writer');pr=load(root/'probe-result.json')
 if pr.get('status')!='MSR_PROBE_8_PASS':raise RuntimeError('probe gate not passed')
 key=require_key();pilot,sealed,_=pilot_units();inst=load_instructions();p=Provider(key,root,'writer');rows=[]
 for u in pilot:
  prompt=writer_prompt(u);trajectory_sha=u['source_run']['writer_input_trajectory_sha256']
  for br,name in (('success','SUCCESSFUL_SI'),('failure','FAILED_SI')):
   label=u['unit_id']+'|'+br;r=p.call([{'role':'system','content':inst[name].strip()},{'role':'user','content':prompt}],label,max_tokens=2048,temperature=0.0);text=r['content'].strip()
   if not memory_valid(text):raise RuntimeError('STOP_MSR_WRITER_FORMAT')
   row={'unit_id':u['unit_id'],'source_task_id':u['source_task_id'],'branch':br,'instruction':name,'trajectory_sha256':trajectory_sha,'prompt_sha256':sha(prompt),'memory':text,'memory_sha256':sha(text),'memory_items':len(__import__('re').findall(r'^# Memory Item\s+\d+',text,__import__('re').M)),'provider':r['receipt']};atomic_json(root/'writer'/f'{safe_id(u["unit_id"])}__{br}.json',row);rows.append(row)
 for u in pilot:
  a=[x for x in rows if x['unit_id']==u['unit_id'] and x['branch']=='success'][0];b=[x for x in rows if x['unit_id']==u['unit_id'] and x['branch']=='failure'][0]
  if a['trajectory_sha256']!=b['trajectory_sha256'] or a['memory_sha256']==b['memory_sha256']:raise RuntimeError('STOP_MSR_WRITER_TWIN_INVALID')
 out={'schema_version':1,'created_at_utc':now(),'status':'MSR_WRITER_TWINS_16_PASS','calls':16,'units':8,'sealed_provider_calls':0,**phase_usage(p)};atomic_json(root/'writer-result.json',out);return out
def load_writers(root:Path)->dict[tuple[str,str],dict[str,Any]]:
 return {(x['unit_id'],x['branch']):x for x in (load(p) for p in (root/'writer').glob('*.json'))}
def load_probes(root:Path)->dict[str,dict[str,Any]]:return {x['unit_id']:x for x in load(root/'probe-result.json')['rows']}
def binder(root:Path)->dict[str,Any]:
 phase_clean(root,'binder');w=load(root/'writer-result.json')
 if w.get('status')!='MSR_WRITER_TWINS_16_PASS':raise RuntimeError('writer gate not passed')
 key=require_key();pilot,sealed,_=pilot_units();writers=load_writers(root);probes=load_probes(root);p=Provider(key,root,'binder');rows=[]
 for u in pilot:
  for selector in SELECTORS:
   state=binding_state(selector,probes[u['unit_id']] if selector=='GPLUS_MATCHED_REVEAL' else None)
   for br in BRANCHES:
    mem=writers[(u['unit_id'],br)]['memory'];prompt=binding_prompt(mem,u['future_task'],state);r=p.call([{'role':'system','content':'Return only the requested concise action implication.'},{'role':'user','content':prompt}],u['unit_id']+'|'+selector+'|'+br,max_tokens=512,temperature=0.0);text=r['content'].strip();wc=len(text.split())
    if not text or wc>60:raise RuntimeError('STOP_MSR_BINDER_FORMAT')
    row={'unit_id':u['unit_id'],'selector':selector,'branch':br,'prompt_sha256':sha(prompt),'memory_sha256':writers[(u['unit_id'],br)]['memory_sha256'],'binding':text,'binding_sha256':sha(text),'word_count':wc,'provider':r['receipt']};atomic_json(root/'binder'/f'{safe_id(u["unit_id"])}__{selector}__{br}.json',row);rows.append(row)
 out={'schema_version':1,'created_at_utc':now(),'status':'MSR_BINDER_32_PASS','calls':32,'sealed_provider_calls':0,'word_count_min':min(x['word_count'] for x in rows),'word_count_max':max(x['word_count'] for x in rows),**phase_usage(p)};atomic_json(root/'binder-result.json',out);return out
def load_binders(root:Path)->dict[tuple[str,str,str],dict[str,Any]]:return {(x['unit_id'],x['selector'],x['branch']):x for x in (load(p) for p in (root/'binder').glob('*.json'))}
def shadow(root:Path)->dict[str,Any]:
 phase_clean(root,'shadow');b=load(root/'binder-result.json')
 if b.get('status')!='MSR_BINDER_32_PASS':raise RuntimeError('binder gate not passed')
 key=require_key();pilot,sealed,_=pilot_units();byu={x['unit_id']:x for x in pilot};writers=load_writers(root);binders=load_binders(root);probes=load_probes(root);config=yaml.safe_load(CONFIG.read_text());schedule=[json.loads(x) for x in (root/'shadow-schedule.jsonl').read_text().splitlines() if x.strip()]
 inputs=[]
 for c in schedule:
  u=byu[c['unit_id']];messages=policy_messages(config,u['future_task'],writers[(u['unit_id'],c['branch'])]['memory'],binders[(u['unit_id'],c['selector'],c['branch'])]['binding'],c['selector'],probes[u['unit_id']] if c['selector']=='GPLUS_MATCHED_REVEAL' else None);inputs.append({**c,'messages':messages,'messages_sha256':sha(json.dumps(messages,sort_keys=True,ensure_ascii=False))})
 atomic_bytes(root/'shadow-inputs.jsonl',''.join(json.dumps(x,sort_keys=True,ensure_ascii=False)+'\n' for x in inputs).encode());p=Provider(key,root,'shadow');outcomes=[]
 for c in inputs:
  r=p.call(c['messages'],c['case_id'],max_tokens=512,temperature=0.2);action=parse_action(r['content']);row={k:v for k,v in c.items() if k!='messages'};row.update({'action_signature':action,'response_sha256':r['receipt']['response_sha256'],'provider':r['receipt']});append(root/'shadow/outcomes.jsonl',row);outcomes.append(row)
 per=[]
 for u in pilot:
  row={'unit_id':u['unit_id']}
  for selector in SELECTORS:
   sm={}
   for key0,br,block in (('S1','success',1),('S2','success',2),('F1','failure',1),('F2','failure',2)):sm[key0]=[x['action_signature'] for x in outcomes if x['unit_id']==u['unit_id'] and x['selector']==selector and x['branch']==br and x['block']==block]
   g=gate(sm)
   for k,v in g.items():row[f'{selector}_{k}']=v
  row['margin_improvement']=row['GPLUS_MATCHED_REVEAL_margin']-row['G0_STEP0_margin'];per.append(row)
 kplus=sum(x['GPLUS_MATCHED_REVEAL_G'] for x in per);mean_imp=sum(x['margin_improvement'] for x in per)/8;positive=sum(x['margin_improvement']>0 for x in per);mechanism=(2<=kplus<=6 and mean_imp>=.05 and positive>=5)
 result={'schema_version':1,'created_at_utc':now(),'status':'MSR_MECHANISM_GATE_PASS' if mechanism else 'HOLD_MSR_MECHANISM_GATE','calls':384,'per_unit':per,'G0_open_count':sum(x['G0_STEP0_G'] for x in per),'Gplus_open_count':kplus,'mean_margin_improvement':mean_imp,'positive_margin_improvement_count':positive,'mechanism_gate_pass':mechanism,'sealed_provider_calls':0,**phase_usage(p)};atomic_json(root/'shadow-result.json',result);return result
def main()->None:
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=DEFAULT);a.add_argument('--phase',choices=('prepare','probe','writer','binder','shadow'),required=True);x=a.parse_args();result={'prepare':prepare,'probe':probe,'writer':writer,'binder':binder,'shadow':shadow}[x.phase](x.root);print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
