#!/usr/bin/env python3
"""Guarded four-arm final first-decision measurement for PACTA-MSR."""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
import yaml
from research_pipeline.c1_pacta_rb_qwen397 import atomic_bytes,atomic_json
from research_pipeline.c1_pacta_msr_qwen397_p0_core import CONFIG,Provider,load,now,parse_action,phase_usage,pilot_units,policy_messages,safe_id,sha,tv
from research_pipeline.run_c1_pacta_msr_qwen397_p0_stages_20260902 import load_binders,load_probes,load_writers,phase_clean,require_key
DEFAULT=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-qwen397-p0-20260902-v1')
ARMS=('A0_NATIVE','A1_SCB_ALWAYS','A2_RATE_MATCHED_RANDOM','A3_PACTA_MSR');BRANCHES=('success','failure');SALT='C1-PACTA-MSR-QWEN397-FINAL-v1'

def final(root:Path)->dict:
 phase_clean(root,'final');shadow=load(root/'shadow-result.json')
 if shadow.get('status')!='MSR_MECHANISM_GATE_PASS' or not shadow.get('mechanism_gate_pass'):raise RuntimeError('MSR mechanism gate not passed')
 k=int(shadow['Gplus_open_count']);pilot,sealed,random_ranking=pilot_units();byu={x['unit_id']:x for x in pilot};pacta={x['unit_id'] for x in shadow['per_unit'] if x['GPLUS_MATCHED_REVEAL_G']};random=set(random_ranking[:k])
 if len(pacta)!=k or len(random)!=k:raise RuntimeError('rate-match geometry')
 writers=load_writers(root);binders=load_binders(root);probes=load_probes(root);config=yaml.safe_load(CONFIG.read_text());rows=[]
 for u in pilot:
  for arm in ARMS:
   for br in BRANCHES:
    use=(arm=='A1_SCB_ALWAYS') or (arm=='A2_RATE_MATCHED_RANDOM' and u['unit_id'] in random) or (arm=='A3_PACTA_MSR' and u['unit_id'] in pacta);binding=binders[(u['unit_id'],'GPLUS_MATCHED_REVEAL',br)]['binding'] if use else None;messages=policy_messages(config,u['future_task'],writers[(u['unit_id'],br)]['memory'],binding,'GPLUS_MATCHED_REVEAL',probes[u['unit_id']])
    for rep in range(1,7):
     case=f"{u['unit_id']}__{arm}__{br}__r{rep}";rows.append({'case_id':case,'unit_id':u['unit_id'],'arm':arm,'branch':br,'replicate':rep,'uses_scb':use,'messages':messages,'messages_sha256':sha(json.dumps(messages,sort_keys=True,ensure_ascii=False)),'order_key':sha(SALT+'|'+case)})
 rows.sort(key=lambda x:(x['order_key'],x['case_id']))
 if len(rows)!=384:raise RuntimeError('final geometry')
 atomic_bytes(root/'final-inputs.jsonl',''.join(json.dumps(x,sort_keys=True,ensure_ascii=False)+'\n' for x in rows).encode());key=require_key();p=Provider(key,root,'final');out=[]
 for c in rows:
  r=p.call(c['messages'],c['case_id'],max_tokens=512,temperature=0.2);action=parse_action(r['content']);row={k0:v for k0,v in c.items() if k0!='messages'};row.update({'action_signature':action,'response_sha256':r['receipt']['response_sha256'],'provider':r['receipt']});root.joinpath('final').mkdir(exist_ok=True);with_path=root/'final/outcomes.jsonl'
  with with_path.open('a',encoding='utf-8') as h:h.write(json.dumps(row,sort_keys=True)+'\n');h.flush();os.fsync(h.fileno());out.append(row)
 per=[]
 for u in pilot:
  row={'unit_id':u['unit_id']}
  for arm in ARMS:
   s=[x['action_signature'] for x in out if x['unit_id']==u['unit_id'] and x['arm']==arm and x['branch']=='success'];f=[x['action_signature'] for x in out if x['unit_id']==u['unit_id'] and x['arm']==arm and x['branch']=='failure'];row['U_'+arm]=tv(s,f)
  row['D_select']=row['U_A3_PACTA_MSR']-row['U_A2_RATE_MATCHED_RANDOM'];row['A3_A1']=row['U_A3_PACTA_MSR']-row['U_A1_SCB_ALWAYS'];row['A3_A0']=row['U_A3_PACTA_MSR']-row['U_A0_NATIVE'];per.append(row)
 mean=lambda k0:sum(x[k0] for x in per)/8;pos=sum(x['D_select']>0 for x in per);neg=sum(x['D_select']<0 for x in per);zero=8-pos-neg;passed=(mean('D_select')>=.05 and pos>neg and mean('A3_A0')>0 and mean('A3_A1')>=0)
 result={'schema_version':1,'created_at_utc':now(),'status':'PACTA_MSR_PRELIMINARY_SIGNAL' if passed else 'PACTA_MSR_SELECTION_UNSUPPORTED_OR_NEGATIVE','calls':384,'K':k,'pacta_open':sorted(pacta),'random_open':sorted(random),'per_unit':per,'means':{k0:mean(k0) for k0 in ('U_A0_NATIVE','U_A1_SCB_ALWAYS','U_A2_RATE_MATCHED_RANDOM','U_A3_PACTA_MSR','D_select','A3_A1','A3_A0')},'D_signs':{'positive':pos,'negative':neg,'zero':zero},'pilot_gate_pass':passed,'sealed_provider_calls':0,'terminal_executed':False,**phase_usage(p)};atomic_json(root/'final-result.json',result);return result
def main()->None:
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=DEFAULT);x=a.parse_args();print(json.dumps(final(x.root),sort_keys=True))
if __name__=='__main__':main()
