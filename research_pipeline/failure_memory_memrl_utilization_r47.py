#!/usr/bin/env python3
"""Frozen B1 MemRL utilization qualification (R47)."""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,random,socket,subprocess,sys,urllib.request
from datetime import datetime,timezone
from types import SimpleNamespace
from typing import Any
PAPER_ID='D2-PAPER-FAILURE-MEMORY-PROVENANCE'; API_KEY='local-b1-r43'
G8='MEMRL_CURRENT_G1_G8_PASS_EXECUTION_MANIFEST_FROZEN_ZERO_CONFIRMATORY_OUTCOMES'; AUTH='HUMAN_BOUNDED_EXECUTION_AUTHORITY_RECORDED'; QUAL='SOURCE_QUALIFICATION_PASS_RETRIEVAL_FROZEN_VALIDATION_STILL_SEALED'
ARMS=['U0_no_memory','U1_true_memory','U2_null_memory','U3_reversed_memory','U4_shuffled_memory']
def now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def load(p):
 v=json.loads(pathlib.Path(p).read_text());
 if not isinstance(v,dict):raise RuntimeError(f'not-object:{p}')
 return v
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def valid_receipt(v):return isinstance(v.get('receipt_sha256'),str) and v['receipt_sha256']==digest({k:x for k,x in v.items() if k!='receipt_sha256'})
def append(path,row):
 with pathlib.Path(path).open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
def rows(path):
 p=pathlib.Path(path);return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []
def arm_order(seed,tid):
 r=random.Random(int(hashlib.sha256(f'B1-R47-ARM|{seed}|{tid}'.encode()).hexdigest()[:16],16));a=list(ARMS);r.shuffle(a);return a
def u4_map(seed,byid,ids):
 eligible=[x for x in ids if byid[x].get('selected')]
 if len(eligible)<2:raise RuntimeError('u4-donor-support')
 r=random.Random(int(hashlib.sha256(f'B1-R47-U4|{seed}'.encode()).hexdigest()[:16],16));d=list(eligible);r.shuffle(d)
 m={x:d[(i+1)%len(d)] for i,x in enumerate(d)}
 for x in ids:
  if x not in m:m[x]=d[0]
 if any(k==v for k,v in m.items()):raise RuntimeError('u4-self-donor')
 return m
def plan(manifest,qual,frozen):
 e=manifest['execution_manifest'];u=e['utilization_qualification'];ids=[str(x) for x in u['representative_ids']];seed=int(e['randomization']['seed'])
 if len(ids)!=8 or list(u['arms'])!=ARMS or qual.get('status')!=QUAL:raise RuntimeError('util-contract-drift')
 fr=[x for x in frozen['rows'] if x.get('cohort')=='utilization'];by={str(x['validation_task_id']):x for x in fr}
 if set(by)!=set(ids):raise RuntimeError('frozen-row-drift')
 mp=u4_map(seed,by,ids);sched=[{'task_id':x,'arm_order':arm_order(seed,x),'u4_donor_task_id':mp[x]} for x in ids]
 out={'schema_version':'1.0','paper_id':PAPER_ID,'role':'R47_FROZEN_UTILIZATION_SCHEDULE_PRE_OUTCOME','randomization_seed':seed,'utilization_ids':ids,'arms':ARMS,'schedule':sched,'promotion_endpoint':u['promotion_endpoint'],'pass_rule':u['pass_rule'],'terminal_success_is_diagnostic_only':True,'primary_confirmatory_units_opened':False,'utilization_outcomes_observed_when_plan_created':0,'scientific_authority':False}
 out['plan_sha256']=digest(out);return out
def reverse_blocks(text):
 ps=[x.strip() for x in str(text or '').replace('\r\n','\n').split('\n\n') if x.strip()]
 if len(ps)>1:return '\n\n'.join(ps[:1]+list(reversed(ps[1:])))
 ls=[x for x in str(text or '').splitlines() if x.strip()];return '\n'.join(reversed(ls))
def memctx(formatter,row,arm,donor):
 if arm=='U0_no_memory':return '',{'memory_surface':'none','source_task_id':None}
 selected=list((donor if arm=='U4_shuffled_memory' else row).get('selected') or []);top=selected[0] if selected else {}
 success=bool(top.get('source_outcome_success')) if top.get('source_outcome_success') is not None else False;orig=str(top.get('content') or '')
 body=orig if arm in {'U1_true_memory','U4_shuffled_memory'} else ('[NO ACTIONABLE MEMORY CONTENT]' if arm=='U2_null_memory' else reverse_blocks(orig))
 bucket='successed' if success else 'failed';meta=SimpleNamespace(type='SUCCESS_PROCEDURE' if success else 'FAILURE_REFLECTION',success=success)
 ctx=formatter({bucket:[{'content':body,'metadata':meta}]},task='os')
 return ctx,{'memory_surface':bucket,'memory_id':top.get('memory_id'),'source_task_id':top.get('source_task_id'),'source_outcome_success':top.get('source_outcome_success'),'content_sha256':hashlib.sha256(body.encode()).hexdigest()}
def norm_action(x):
 if not x:return None
 ls=[z.strip() for z in str(x).replace('\r\n','\n').splitlines() if z.strip() and not z.strip().startswith('#')];return '\n'.join(ls) or None
def chat(session):
 out=[];h=getattr(session,'chat_history',None)
 if not h:return out
 for i in range(int(h.get_value_length())):
  x=h.get_item_deep_copy(i);out.append({'role':str(getattr(x,'role','')),'content':str(getattr(x,'content','') or '')})
 return out
def preflight(manifest,auth,qual,frozen,source_receipt):
 if manifest.get('paper_id')!=PAPER_ID or auth.get('paper_id')!=PAPER_ID or manifest.get('status')!=G8 or auth.get('status')!=AUTH or qual.get('status')!=QUAL:raise RuntimeError('receipt-status-drift')
 if not all(valid_receipt(x) for x in [manifest,auth,qual,frozen]):raise RuntimeError('receipt-hash-drift')
 if qual.get('frozen_retrieval_receipt_sha256')!=frozen.get('receipt_sha256') or qual.get('source_build_receipt_sha256')!=source_receipt.get('receipt_sha256'):raise RuntimeError('qualification-binding-drift')
 scope=auth['authorized_scope']['utilization_qualification']
 if scope.get('authorized_conditionally_after_source_qualification') is not True or int(scope.get('exact_clusters') or 0)!=8 or list(scope.get('arms') or [])!=ARMS:raise RuntimeError('authority-drift')
 e=manifest['execution_manifest'];h=e['host'];s=e['source']
 if socket.gethostname()!=h['logical_name'] or pathlib.Path(sys.executable).resolve()!=pathlib.Path(h['python']).resolve() or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':raise RuntimeError('host-python-drift')
 root=pathlib.Path(s['checkout']);head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip();dirty=subprocess.check_output(['git','-C',str(root),'status','--porcelain'],text=True).strip()
 if head!=s['revision'] or dirty:raise RuntimeError('source-drift')
 split=root/e['confirmatory_units']['split']
 if sha(split)!=e['confirmatory_units']['split_sha256']:raise RuntimeError('split-drift')
 image=subprocess.check_output(['docker','image','inspect',e['runtime_image']['execution_tag'],'--format','{{.Id}}'],text=True).strip()
 if image!=e['runtime_image']['id']:raise RuntimeError('image-drift')
 base=e['external_runtime_adapter']['loopback_base_url'].rstrip('/')
 with urllib.request.urlopen(base+'/models',timeout=5) as r:models={str(x.get('id')) for x in json.loads(r.read().decode()).get('data') or []}
 if {e['external_runtime_adapter']['llm_model_id'],e['external_runtime_adapter']['embedding_model_id']}-models:raise RuntimeError('loopback-route-drift')
def build_adapter(manifest):
 e=manifest['execution_manifest'];root=pathlib.Path(e['source']['checkout']);llb=root/'3rdparty'/'LifelongAgentBench'
 sys.path.insert(0,str(root)) if str(root) not in sys.path else None;sys.path.insert(0,str(llb)) if str(llb) not in sys.path else None
 from memrl.providers.llm import OpenAILLM
 from memrl.lifelongbench_eval.lm_adapter import MempOpenAIAdapter
 a=e['external_runtime_adapter'];llm=OpenAILLM(api_key=API_KEY,base_url=a['loopback_base_url'],model=a['llm_model_id'],default_temperature=0.0,default_max_tokens=int(e['models']['llm']['max_new_tokens']),provider='openai');return MempOpenAIAdapter(llm)
def run_arm(manifest,adapter,tid,arm,ctx):
 e=manifest['execution_manifest'];root=pathlib.Path(e['source']['checkout']);llb=root/'3rdparty'/'LifelongAgentBench';sys.path.insert(0,str(llb)) if str(llb) not in sys.path else None
 from memrl.lifelongbench_eval.prompts import DEFAULT_SYSTEM_PROMPT,build_llb_prompt_with_memory
 from memrl.lifelongbench_eval.task_wrappers import build_task
 from src.agents.instance.language_model_agent import LanguageModelAgent
 from src.tasks.instance.os_interaction.task import OSInteraction
 from src.tasks.task import AgentAction
 from src.typings import Session,SampleStatus,SessionEvaluationOutcome
 prompt=build_llb_prompt_with_memory(task='os',base_prompt=DEFAULT_SYSTEM_PROMPT,memory_context=ctx);agent=LanguageModelAgent(language_model=adapter,system_prompt=prompt)
 task,tname=build_task(task='os',data_file_path=str(root/e['confirmatory_units']['split']),max_round=int(e['source_build']['max_steps']),os_timeout=int(e['source_build']['os_timeout_seconds']));session=Session(task_name=tname,sample_index=tid);actions=[];first=None;steps=0;success=None
 try:
  task.reset(session)
  while session.sample_status==SampleStatus.RUNNING:
   agent.inference(session);resp=str(session.chat_history.get_item_deep_copy(-1).content or '');p=OSInteraction._parse_agent_response(resp);n=norm_action(p.content if p.action==AgentAction.EXECUTE else None);actions.append({'response':resp,'parsed':str(p.action),'content':p.content,'normalized':n});first=first if first is not None else n;task.interact(session);steps+=1
   if steps>int(e['source_build']['max_steps'])*2:raise RuntimeError('step-ceiling')
  task.complete(session);out=getattr(getattr(session,'evaluation_record',None),'outcome',None);success=(out==SessionEvaluationOutcome.CORRECT)
 finally:
  try:task.release()
  except Exception:pass
 return {'task_id':tid,'arm':arm,'full_system_prompt':prompt,'chat_messages':chat(session),'actions':actions,'first_executable_action':first,'terminal_success_diagnostic':success,'steps':steps}
def analyze(pl,rr):
 by={}
 for r in rr:
  if r.get('status')=='COMPLETE':by.setdefault(str(r['task_id']),{})[str(r['arm'])]=r
 units=[];specific=placebo=complete=0
 for tid in pl['utilization_ids']:
  a=by.get(tid,{});ok=all(x in a for x in ARMS)
  if not ok:units.append({'task_id':tid,'complete':False});continue
  complete+=1;a0=a['U0_no_memory'].get('first_executable_action');a1=a['U1_true_memory'].get('first_executable_action');a2=a['U2_null_memory'].get('first_executable_action');sp=a1!=a0 and a1!=a2;pb=a2!=a0;specific+=int(sp);placebo+=int(pb);units.append({'task_id':tid,'complete':True,'u1_specific_first_action':sp,'u2_vs_u0_divergence':pb,'terminal_success_diagnostic':{x:a[x].get('terminal_success_diagnostic') for x in ARMS}})
 passed=complete==8 and specific>=3 and specific>=placebo+1
 return {'schema_version':'1.0','paper_id':PAPER_ID,'role':'R47_UTILIZATION_QUALIFICATION_ADJUDICATION','status':'UTILIZATION_QUALIFICATION_PASS' if passed else ('UTILIZATION_QUALIFICATION_INCOMPLETE' if complete<8 else 'OPERATIONALIZATION_STOP_MEMORY_NOT_BEHAVIORALLY_USED'),'complete_units':complete,'u1_specific_first_action_units':specific,'u2_vs_u0_divergence_units':placebo,'pass':passed,'primary_32_clusters_authorized_next':passed,'terminal_success_used_for_promotion':False,'unit_rows':units,'scientific_authority':False}
def main():
 ap=argparse.ArgumentParser();
 for x in ['manifest','authorization','qualification','frozen-retrieval','source-receipt','output-dir']:ap.add_argument('--'+x,type=pathlib.Path,required=True)
 ap.add_argument('--resume',action='store_true');a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
 m,u,q,f,s=map(load,[a.manifest,a.authorization,a.qualification,a.frozen_retrieval,a.source_receipt]);preflight(m,u,q,f,s);pp=a.output_dir/'frozen-utilization-plan.json';pl=load(pp) if pp.exists() else plan(m,q,f)
 if not pp.exists():pp.write_text(json.dumps(pl,ensure_ascii=False,indent=2)+'\n')
 by={str(x['validation_task_id']):x for x in f['rows'] if x.get('cohort')=='utilization'};schedule=[(z['task_id'],arm,z['u4_donor_task_id']) for z in pl['schedule'] for arm in z['arm_order']];lp=a.output_dir/'completed-utilization-arms.jsonl';done=rows(lp);prefix=[(str(x.get('task_id')),str(x.get('arm')),str(x.get('u4_donor_task_id'))) for x in done]
 if prefix!=schedule[:len(prefix)]:raise RuntimeError('ledger-not-schedule-prefix')
 if done and len(done)<len(schedule) and not a.resume:raise RuntimeError('partial-requires-resume')
 if len(done)<len(schedule):
  root=pathlib.Path(m['execution_manifest']['source']['checkout']);sys.path.insert(0,str(root)) if str(root) not in sys.path else None
  from memrl.lifelongbench_eval.memory_context import format_llb_memory_context
  adapter=build_adapter(m)
  for i,(tid,arm,donor) in enumerate(schedule[len(done):],start=len(done)):
   ctx,meta=memctx(format_llb_memory_context,by[tid],arm,by[donor]);ad=a.output_dir/'arms'/f'{i:02d}-{tid}-{arm}';ad.mkdir(parents=True,exist_ok=False)
   try:
    tr=run_arm(m,adapter,tid,arm,ctx);tp=ad/'trace.json';tp.write_text(json.dumps(tr,ensure_ascii=False,indent=2)+'\n');row={'schedule_ordinal':i,'task_id':tid,'arm':arm,'u4_donor_task_id':donor,'status':'COMPLETE','completed_at':now(),'first_executable_action':tr['first_executable_action'],'first_executable_action_sha256':hashlib.sha256(str(tr['first_executable_action'] or '<NONE>').encode()).hexdigest(),'terminal_success_diagnostic':tr['terminal_success_diagnostic'],'steps':tr['steps'],'memory_meta':meta,'memory_context_sha256':hashlib.sha256(ctx.encode()).hexdigest(),'trace_file':str(tp),'trace_file_sha256':sha(tp),'external_provider_calls':0};append(lp,row);print(json.dumps({k:row[k] for k in ['schedule_ordinal','task_id','arm','first_executable_action_sha256','terminal_success_diagnostic']},sort_keys=True),flush=True)
   except Exception as ex:
    row={'schedule_ordinal':i,'task_id':tid,'arm':arm,'u4_donor_task_id':donor,'status':'EXECUTION_FAILURE_NO_RETRY','failed_at':now(),'error_type':type(ex).__name__,'error':str(ex),'scientific_update_allowed':False};(ad/'failure.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');append(lp,row);raise
 rr=rows(lp);out=analyze(pl,rr);out.update({'plan_sha256':pl['plan_sha256'],'completed_arm_runs':len(rr),'external_provider_calls':0,'primary_confirmatory_outcomes_observed':0});out['receipt_sha256']=digest(out);(a.output_dir/'utilization-qualification-receipt.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,sort_keys=True))
if __name__=='__main__':main()
