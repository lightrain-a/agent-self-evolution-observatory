#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, re
from pathlib import Path

ORIGINAL=[21,22,23,25]

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def tsha(s:str)->str:return hashlib.sha256(s.encode()).hexdigest()
def load(p:Path):return json.loads(p.read_text())
def req(x,msg):
 if not x:raise RuntimeError(msg)
def writej(p:Path,d):p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');os.replace(t,p)
def items(text:str):
 blocks=re.split(r'(?m)^# Memory Item \d+\s*$',text)
 out=[]
 for b in blocks:
  if not b.strip():continue
  m1=re.search(r'(?m)^## Title:\s*(.+?)\s*$',b);m2=re.search(r'(?m)^## Description:\s*(.+?)\s*$',b);m3=re.search(r'(?ms)^## Content:\s*(.+?)\s*$',b)
  req(bool(m1 and m2 and m3),'memory item parse failure')
  out.append({'title':m1.group(1).strip(),'description':m2.group(1).strip(),'content':m3.group(1).strip()})
 req(bool(out),'no memory items parsed');return out
def native_wrapper(source_intent:str,text:str)->str:
 pre='\nBelow are some memory items that I accumulated from past interaction from the environment that may be helpful to solve the task. You can use it when you feel it\'s relevant.\n\n'
 s=pre+f'[Retrieved from past task: "{source_intent}"]\n'
 for d in items(text):s+=f"Title: {d['title']}\nDescription: {d['description']}\nContent: {d['content']}\n\n"
 return s

def main():
 ap=argparse.ArgumentParser();
 for n in ['f0','f2_prompt_root','b2','b2_private','task_config','private_root','output']:ap.add_argument('--'+n.replace('_','-'),required=True,type=Path)
 a=ap.parse_args();f0=load(a.f0);b2=load(a.b2);tasks=load(a.task_config);by={int(x['task_id']):x for x in tasks}
 req(f0['summary']['paired_trajectories_complete']==4,'F0 drift');req(b2['status']=='B2_BROAD_WRITE_CHANNEL_SUPPORTED' and b2['new_complete_pairs']==16,'B2 drift')
 manifest=[];a.private_root.mkdir(parents=True,exist_ok=True)
 # Recover original raw memories from historical F2R1 prompts by exact F0 SHA.
 prompts=list(a.f2_prompt_root.rglob('*.txt'))
 f0p={int(x['task_id']):x for x in f0['pairs'] if x.get('success_memory_sha256') and x.get('failure_memory_sha256')}
 for source in ORIGINAL:
  for cond,key in [('success','success_memory_sha256'),('failure','failure_memory_sha256')]:
   target=f0p[source][key];matches=[]
   for p in prompts:
    t=p.read_text()
    if 'REUSABLE MEMORY:\n' not in t or '\n\nBENCHMARK TASK:' not in t:continue
    mem=t.split('REUSABLE MEMORY:\n',1)[1].split('\n\nBENCHMARK TASK:',1)[0]
    if tsha(mem)==target:matches.append(mem)
   req(matches and all(m==matches[0] for m in matches),f'original memory recovery failed {source}/{cond}')
   mem=matches[0];raw=a.private_root/f'{source}-{cond}.md';raw.write_text(mem);wrap=native_wrapper(str(by[source]['intent']),mem);wp=a.private_root/f'{source}-{cond}-native-wrapper.txt';wp.write_text(wrap)
   manifest.append({'source_task':source,'condition':cond,'source_kind':'original_f0','task_description':str(by[source]['intent']),'raw_path':str(raw.resolve()),'raw_sha256':target,'native_wrapper_path':str(wp.resolve()),'native_wrapper_sha256':tsha(wrap),'memory_item_count':len(items(mem))})
 # New B2 memories are already archived content-addressed in R1 private/raw.
 for pair in b2['new_pair_results']:
  source=int(pair['task_id'])
  for cond,key in [('success','success_memory_sha256'),('failure','failure_memory_sha256')]:
   h=pair[key];src=a.b2_private/'raw'/h[:2]/(h+'.txt');req(src.is_file() and sha(src)==h,f'B2 raw drift {source}/{cond}');mem=src.read_text();wrap=native_wrapper(str(by[source]['intent']),mem);wp=a.private_root/f'{source}-{cond}-native-wrapper.txt';wp.write_text(wrap)
   manifest.append({'source_task':source,'condition':cond,'source_kind':'b2_r1','task_description':str(by[source]['intent']),'raw_path':str(src.resolve()),'raw_sha256':h,'native_wrapper_path':str(wp.resolve()),'native_wrapper_sha256':tsha(wrap),'memory_item_count':len(items(mem))})
 req(len(manifest)==40 and len({(x['source_task'],x['condition']) for x in manifest})==40,'manifest size drift')
 payload={'schema_version':'1.0','artifact_type':'b4-native-memory-manifest','paper_id':'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE','status':'B4_MEMORY_MANIFEST_READY','source_task_count':20,'memory_object_count':40,'native_wrapper_contract':{'preamble_exact_from_released_memory_py':True,'rm_meta_instruct':True,'memory_as_human_message':True,'wrapper_fields':['Retrieved from past task','Title','Description','Content']},'objects':manifest,'source_bindings':{'f0_sha256':sha(a.f0),'b2_sha256':sha(a.b2),'task_config_sha256':sha(a.task_config)},'provider_calls':0,'scientific_authority':False,'experiment_authority':True}
 writej(a.output,payload);print(json.dumps({'status':payload['status'],'source_task_count':20,'memory_object_count':40,'item_counts':{str(n):sum(x['memory_item_count']==n for x in manifest) for n in sorted({x['memory_item_count'] for x in manifest})}},indent=2))
if __name__=='__main__':main()
