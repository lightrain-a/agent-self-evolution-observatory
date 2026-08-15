from __future__ import annotations
import argparse,fcntl,hashlib,json,os,random,time
from datetime import datetime,timezone
from pathlib import Path
import torch
from research_pipeline.scienceworld_qwen_adapter import ScienceWorldQwenPolicy
from research_pipeline.scienceworld_source_repair_runtime import state_key

C=Path(__file__).with_name('scienceworld_base_headroom_q1_contract.json')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def atom(p,x):p=Path(p);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');os.replace(t,p)
def replay(env,u):
 for attempt in range(1,31):
  env.load(u['task_family'],u['variation'],'',generateGoldPath=False);obs,info=env.reset()
  if state_key(env,obs)==u['initial_state_key']:return obs,info,attempt
 return None,None,30

def rollout(env,policy,obs,info,max_steps=50):
 task=env.taskdescription();hist=[];rows=[];score=int(info.get('score',0) or 0)
 for step in range(max_steps):
  inv=env.inventory();action,raw=policy.choose(task,obs,inv,hist,env.get_possible_actions(),env.get_possible_objects());obs2,reward,done,info=env.step(action);score=int(info.get('score',score) or 0)
  rows.append({'step':step,'observation':obs,'observation_sha256':hashlib.sha256(obs.encode()).hexdigest(),'inventory':inv,'action':action,'raw':raw,'reward':reward,'score':score,'done':bool(done),'next_observation':obs2})
  hist.append((action,obs2));obs=obs2
  if done:break
 return rows,score

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--shard',type=int,required=True);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--gpu-uuid',required=True);ap.add_argument('--model-path',type=Path,default=Path('/home/hdd/qinglinji/models/Qwen2.5-7B-Instruct'));a=ap.parse_args()
 if os.environ.get('CUDA_VISIBLE_DEVICES','')!=a.gpu_uuid:raise RuntimeError('GPU UUID binding mismatch')
 plan=json.loads(a.plan.read_text());units=[u for i,u in enumerate(plan['units']) if i%3==a.shard]
 if a.output_dir.exists() and any(a.output_dir.iterdir()):raise RuntimeError('non-empty output')
 a.output_dir.mkdir(parents=True,exist_ok=True);lk=(a.output_dir.parent/(a.output_dir.name+'.lock')).open('a+');fcntl.flock(lk.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
 random.seed(0);torch.manual_seed(0);torch.cuda.manual_seed_all(0);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.use_deterministic_algorithms(True)
 from scienceworld import ScienceWorldEnv
 policy=ScienceWorldQwenPolicy(a.model_path);env=ScienceWorldEnv('',envStepLimit=50);out=[];start=time.monotonic()
 atom(a.output_dir/'manifest.json',{'experiment_id':'SCIENCEWORLD-BASE-HEADROOM-Q1','contract_sha256':sha(C),'plan_file_sha256':sha(a.plan),'plan_hash':plan['plan_hash'],'runner_sha256':sha(Path(__file__)),'gpu_uuid':a.gpu_uuid,'shard':a.shard,'unit_ids':[u['unit_id'] for u in units],'method_result_authorized':False})
 try:
  for u in units:
   obs,info,attempts=replay(env,u)
   if obs is None:r={'unit':u,'replay_available':False,'replay_attempts':attempts,'final_score':None,'success':None,'positive_progress':False,'trace':[]}
   else:
    tr,score=rollout(env,policy,obs,info,50);r={'unit':u,'replay_available':True,'replay_attempts':attempts,'final_score':score,'success':int(score>=100),'positive_progress':bool(score>0),'steps':len(tr),'trace':tr}
   out.append(r);atom(a.output_dir/'unit-results.json',out);atom(a.output_dir/'progress.json',{'status':'running','completed_units':len(out),'total_units':len(units),'current_unit':u['unit_id'],'updated_at':now()})
 finally:
  policy.close();fcntl.flock(lk.fileno(),fcntl.LOCK_UN);lk.close()
 if len(out)!=len(units):raise RuntimeError('incomplete shard')
 atom(a.output_dir/'progress.json',{'status':'complete','completed_units':len(out),'total_units':len(units),'elapsed_hours':(time.monotonic()-start)/3600,'updated_at':now()})
if __name__=='__main__':main()
