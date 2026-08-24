#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math, os, random, re, shutil
from collections import Counter
from pathlib import Path

H={
 'b10c':'c2a54c928d74ccb7a153166a02ef0ef7a1504a93b5895952380a95b0277a3436',
 'b10r':'e779c19a6a73bdb4b551f0739453a014fe9fc3cafc17cb4fbaa8b70a5137d8e6',
 'b4':'fb3fef89a38806e9a3b13efd8413b920f81b132390818403f4d5be957f42feeb',
 'manifest':'2880b83c71745f049039c15edb02f731e4f87a44670977b61627143102bee0d1',
 'config':'953f9c0d463486b10a6871cc2fd59f223b2c70184f49815e7efbcab5d8908b41',
 'tokenizer':'be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037',
 'pool':'4be450dde3b0273bb9787637cfbd28fe04a7ba6ab9d36ac48e92b11e350ffc23',
 'modules':'84e40c8e006c9b1d6c122e02cba9b02458120b5fb0c87b746c41e0207cf642cf',
 'weights':'53aa51172d142c89d9012cce15ae4d6cc0ca6895895114379cacb4fab128d9db'}
MAXLEN=256; REPS=100000; SEED=20260824

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def req(x,m):
 if not x:raise RuntimeError(m)
def writej(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');os.replace(t,p)
def extract(text,field='memory'):
 for x in [text,(re.search(r'\{[\s\S]*',text).group(0) if re.search(r'\{[\s\S]*',text) else '')]:
  try:
   x=x.strip();x=re.sub(r'^```(?:json)?\s*','',x);x=re.sub(r'\s*```\s*$','',x);o=json.loads(x);v=(o.get('current_state') or {}).get(field)
   if isinstance(v,str) and v.strip():return v,'strict_json'
  except Exception:pass
 m=re.search(r'"'+field+r'"\s*:\s*"((?:\\.|[^"\\])*)"',text,re.S)
 if m:
  try:return json.loads('"'+m.group(1)+'"'),'narrow_string_recovery'
  except:return m.group(1),'narrow_string_recovery_raw'
 return None,'missing'
def pear(xs,ys):
 mx=sum(xs)/len(xs);my=sum(ys)/len(ys);vx=sum((x-mx)**2 for x in xs);vy=sum((y-my)**2 for y in ys)
 return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.sqrt(vx*vy) if vx and vy else None
def ranks(v):
 out=[0.0]*len(v);order=sorted(range(len(v)),key=lambda i:v[i]);i=0
 while i<len(order):
  j=i+1
  while j<len(order) and v[order[j]]==v[order[i]]:j+=1
  r=(i+j-1)/2+1
  for k in order[i:j]:out[k]=r
  i=j
 return out
def signflip_p(vals,obs):
 rng=random.Random(SEED);ge=0
 for _ in range(REPS):
  s=sum(v*(1 if rng.random()<.5 else -1) for v in vals)/len(vals)
  if s>=obs-1e-15:ge+=1
 return (ge+1)/(REPS+1)
def label_perm_p(taskvals,obs):
 rng=random.Random(SEED);ge=0
 for _ in range(REPS):
  ss=[]
  for a in taskvals:
   z=a[:];rng.shuffle(z);ss.append(sum(z[:4])/4-sum(z[4:])/4)
  if sum(ss)/len(ss)>=obs-1e-15:ge+=1
 return (ge+1)/(REPS+1)

def main():
 ap=argparse.ArgumentParser();
 for n in ['b10_run','b4_result','snapshot','weights','run_root','output']:ap.add_argument('--'+n.replace('_','-'),required=True,type=Path)
 a=ap.parse_args();cpath=a.b10_run/'b10-contract.json';rpath=a.b10_run/'b10-result.json'
 req(sha(cpath)==H['b10c'],'B10 contract drift');req(sha(rpath)==H['b10r'],'B10 result drift');req(sha(a.b4_result)==H['b4'],'B4 drift')
 c=load(cpath);b10=load(rpath);b4=load(a.b4_result);mp=Path(c['source_bindings']['memory_manifest']['path']);req(sha(mp)==H['manifest'],'manifest drift')
 for p,h in [(a.snapshot/'config.json',H['config']),(a.snapshot/'tokenizer.json',H['tokenizer']),(a.snapshot/'1_Pooling/config.json',H['pool']),(a.snapshot/'modules.json',H['modules']),(a.weights,H['weights'])]:req(sha(p)==h,f'model artifact drift {p.name}')
 req(b10['status']=='B10_EXECUTION_COMPLETE' and b10['summary']['provider_calls_complete']==432,'B10 incomplete')
 rows=[];ext=Counter();rawroot=a.b10_run/'private'/'raw'
 for sp in sorted((a.b10_run/'private'/'stages').glob('*.json')):
  r=load(sp);req(r['status']=='complete','noncomplete B10 stage');sh=r['raw_sha256'];rp=rawroot/sh[:2]/(sh+'.txt');req(sha(rp)==sh,'raw archive drift');wm,how=extract(rp.read_text());req(bool(wm),'working-memory extraction fail');ext[how]+=1
  rows.append({'tid':int(r['future_task']),'src':int(r['selected_source_task']),'cond':r['condition'],'wm':wm})
 req(len(rows)==432,'B10 stage count drift');units={int(u['future_task']):u for u in c['task_units']};req(len(units)==36,'task support drift');tids=sorted(units)
 mem={}
 for t,u in units.items():
  mem[t]={}
  for k in ['success','failure']:
   p=Path(u['memory_wrappers'][k]['path']);req(sha(p)==u['memory_wrappers'][k]['sha256'],'wrapper drift');mem[t][k]=p.read_text()
 md=a.run_root/'exact-minilm-l6-v2';md.mkdir(parents=True,exist_ok=True)
 for n in ['config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','vocab.txt','sentence_bert_config.json']:
  p=a.snapshot/n
  if p.exists():shutil.copy2(p,md/n)
 target=md/'model.safetensors'
 if target.exists() or target.is_symlink():target.unlink()
 target.symlink_to(a.weights);os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['TOKENIZERS_PARALLELISM']='false'
 import torch,torch.nn.functional as F
 from transformers import AutoModel,AutoTokenizer
 tok=AutoTokenizer.from_pretrained(md,local_files_only=True);model=AutoModel.from_pretrained(md,local_files_only=True);model.eval()
 def enc(txt):
  out=[]
  with torch.no_grad():
   for i in range(0,len(txt),64):
    b=tok(txt[i:i+64],padding=True,truncation=True,max_length=MAXLEN,return_tensors='pt');h=model(**b).last_hidden_state;m=b['attention_mask'].unsqueeze(-1).expand(h.size()).float();e=(h*m).sum(1)/m.sum(1).clamp(min=1e-9);out.append(F.normalize(e,p=2,dim=1))
  return torch.cat(out)
 me=enc(sum(([mem[t]['success'],mem[t]['failure']] for t in tids),[]));ye=enc([r['wm'] for r in rows]);em={t:(me[2*i],me[2*i+1]) for i,t in enumerate(tids)}
 for i,r in enumerate(rows):
  s,f=em[r['tid']];cent=F.normalize((s+f).unsqueeze(0),p=2,dim=1)[0];direction=F.normalize((s-f).unsqueeze(0),p=2,dim=1)[0];y=ye[i];r['branch']=float((y*s).sum()-(y*f).sum());r['centroid']=float((y*cent).sum());r['direction']=float((y*direction).sum())
 b10c={int(x['future_task']):x for x in b10['cell_results']};b4c={int(x['future_task']):x for x in b4['cell_results']};cells=[];perm=[]
 for t in tids:
  g={q:[r for r in rows if r['tid']==t and r['cond']==q] for q in ['success_memory','failure_memory','no_memory']};req(all(len(x)==4 for x in g.values()),'condition coverage drift');mean=lambda q,k:sum(x[k] for x in g[q])/4
  branch=mean('success_memory','branch')-mean('failure_memory','branch');generic=(mean('success_memory','centroid')+mean('failure_memory','centroid'))/2-mean('no_memory','centroid');direction=mean('success_memory','direction')-mean('failure_memory','direction')
  ms,mf=em[t];input_distance=1.0-float((ms*mf).sum())
  cells.append({'future_task':t,'selected_source_task':int(units[t]['selected_source_task']),'input_memory_cosine_distance':input_distance,'branch_attribution_shift':branch,'common_centroid_uptake':generic,'branch_direction_uptake':direction,'first_action_tv':float(b10c[t]['success_failure_tv']),'terminal_absolute_effect':float(b4c[t]['absolute_rate_difference'])});perm.append([x['branch'] for x in g['success_memory']+g['failure_memory']])
 br=[x['branch_attribution_shift'] for x in cells];gen=[x['common_centroid_uptake'] for x in cells];dire=[x['branch_direction_uptake'] for x in cells];dist=[x['input_memory_cosine_distance'] for x in cells];act=[x['first_action_tv'] for x in cells];term=[x['terminal_absolute_effect'] for x in cells]
 def summary(v):
  m=sum(v)/len(v);sd=math.sqrt(sum((x-m)**2 for x in v)/(len(v)-1));return {'mean':m,'median':sum(sorted(v)[17:19])/2,'positive_tasks':sum(x>0 for x in v),'negative_tasks':sum(x<0 for x in v),'paired_dz':m/sd if sd else None,'signflip_p':signflip_p(v,m)}
 obs=sum(br)/36;loo=[pear(br[:i]+br[i+1:],act[:i]+act[i+1:]) for i in range(36)]
 payload={'schema_version':'1.0','experiment_id':'D2-PROXY-B11-WORKING-MEMORY-BRANCH-ATTRIBUTION','paper_id':'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE','status':'B11_POSTHOC_ZERO_PROVIDER_DIAGNOSTIC_COMPLETE','role':'Post-hoc mechanism localization introduced after B10. No confirmatory gate, provider call, new rollout, or claim-expansion authority.','observable':'Model-emitted current_state.memory before the first structured action on each frozen B10 state.','extraction':{'archived_outputs':432,'complete_fields':432,'strict_json':ext['strict_json'],'narrow_string_recovery':ext['narrow_string_recovery'],'other':432-ext['strict_json']-ext['narrow_string_recovery']},'encoder':{'model':'exact cached all-MiniLM-L6-v2','pooling':'attention-mask mean + L2 normalize','max_length':256,'weights_sha256':H['weights']},'branch_attribution':{**summary(br),'within_state_label_permutation_p':label_perm_p(perm,obs),'definition':'cos(output,success_input)-cos(output,failure_input), compared between success- and failure-conditioned outputs','pearson_vs_first_action_tv':pear(br,act),'spearman_vs_first_action_tv':pear(ranks(br),ranks(act)),'leave_one_out_pearson_vs_first_action_tv_min':min(loo),'leave_one_out_pearson_vs_first_action_tv_max':max(loo),'pearson_vs_terminal_absolute_effect':pear(br,term),'pearson_input_memory_distance_vs_branch_attribution':pear(dist,br),'pearson_input_memory_distance_vs_first_action_tv':pear(dist,act),'pearson_input_memory_distance_vs_terminal_absolute_effect':pear(dist,term),'input_memory_cosine_distance_mean':sum(dist)/len(dist),'input_memory_cosine_distance_min':min(dist),'input_memory_cosine_distance_max':max(dist)},'common_centroid_uptake':{**summary(gen),'definition':'mean similarity to normalized success/failure memory centroid under memory conditions minus no-memory'},'branch_direction_uptake':{**summary(dire),'definition':'projection on normalized success-minus-failure direction under success condition minus failure condition'},'cell_results':cells,'source_bindings':{'b10_contract_sha256':H['b10c'],'b10_result_sha256':H['b10r'],'b4_result_sha256':H['b4'],'memory_manifest_sha256':H['manifest'],'weights_sha256':H['weights']},'provider_calls':0,'new_rollouts':0,'confirmatory_gate':None,'scientific_authority':False,'experiment_authority':True,'claim_expansion_authority':False}
 writej(a.output,payload);print(json.dumps({'status':payload['status'],'extraction':payload['extraction'],'branch_attribution':payload['branch_attribution'],'common_centroid_uptake':payload['common_centroid_uptake'],'branch_direction_uptake':payload['branch_direction_uptake'],'provider_calls':0},indent=2))
if __name__=='__main__':main()
