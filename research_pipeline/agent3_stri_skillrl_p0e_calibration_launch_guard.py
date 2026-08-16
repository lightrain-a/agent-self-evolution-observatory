from __future__ import annotations
import argparse,json,pathlib,subprocess
from research_pipeline import asset_first_stri_skillrl_final_policy_p0e_calibration as p0e

PROJECT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=pathlib.Path('/data/wyt/evidence-substrates/SkillRL-8e66726-runnable')
MODEL=pathlib.Path('/data/wyt/models/SkillRL-Alfworld-7B-RL-2ce16cb/hf-merged')
PYTHON=pathlib.Path('/data/wyt/envs/stri-vllm311/bin/python')
RUNNER=PROJECT/'research_pipeline/asset_first_stri_skillrl_final_policy_p0e_calibration.py'
BASE=pathlib.Path('/data/wyt/agent-self-evolution-observatory/runs/agent3-stri-skillrl-p0e-calibration-20260816')
GPU_CANDIDATES=tuple(range(8));SESSIONS=('ag3-stri-p0e-cal-s0','ag3-stri-p0e-cal-s1')

def gpu_pids(gpu:int)->list[int]:
 uuid=subprocess.check_output(['nvidia-smi','-i',str(gpu),'--query-gpu=uuid','--format=csv,noheader'],text=True).strip();raw=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader'],text=True);out=[]
 for line in raw.splitlines():
  x=[v.strip() for v in line.split(',')]
  if len(x)==2 and x[0]==uuid:out.append(int(x[1]))
 return out

def tmux(name:str)->bool:return subprocess.run(['tmux','has-session','-t',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0

def state()->dict:
 blockers=[];control={}
 try:control=p0e.validate_controls(PROJECT,MODEL,full_hash=False)
 except Exception as e:blockers.append(f'control:{type(e).__name__}:{e}')
 gpu={str(i):gpu_pids(i) for i in GPU_CANDIDATES};free=[i for i in GPU_CANDIDATES if not gpu[str(i)]];runs={}
 for seed in (0,1):
  root=BASE/f'seed{seed}';runs[str(seed)]={'root':str(root),'result_exists':(root/f'calibration-shard-{seed}.json').exists(),'raw_exists':(root/f'calibration-shard-{seed}.jsonl').exists(),'tmux':tmux(SESSIONS[seed])}
 pending=[s for s in (0,1) if not runs[str(s)]['result_exists'] and not runs[str(s)]['raw_exists'] and not runs[str(s)]['tmux']];partial=[s for s in (0,1) if runs[str(s)]['raw_exists'] and not runs[str(s)]['result_exists']]
 if not free:blockers.append('no-free-gpu')
 if partial:blockers.append(f'partial-seeds:{partial}')
 if not pending:blockers.append('no-pending-seed')
 return {'experiment_id':p0e.EXPERIMENT_ID,'controls':control,'gpu_compute_pids':gpu,'free_gpus':free,'runs':runs,'pending_seeds':pending,'blocked_partial_seeds':partial,'blockers':blockers,'launchable':not blockers,'scientific_authority':False}

def launch()->dict:
 s=state()
 if not s['launchable']:raise SystemExit(json.dumps({'launched':False,'state':s},ensure_ascii=False))
 BASE.mkdir(parents=True,exist_ok=True);launched=[]
 for seed,gpu in zip(s['pending_seeds'][:len(s['free_gpus'])],s['free_gpus']):
  if gpu_pids(gpu):continue
  root=BASE/f'seed{seed}';root.mkdir(parents=True,exist_ok=False);log=root/'run.log';cmd=(f"CUDA_VISIBLE_DEVICES={gpu} ALFWORLD_DATA=/data/wyt/agent-self-evolution-p0-52-data/alfworld P0_EXTRA_SITE=/data/wyt/envs/agent_evolution_p0_site_52 {PYTHON} {RUNNER} run-shard --project {PROJECT} --source {SOURCE} --model {MODEL} --run-root {root} --seed-index {seed} --gpu-cap-seconds 1350 > {log} 2>&1")
  subprocess.check_call(['tmux','new-session','-d','-s',SESSIONS[seed],'bash','-lc',cmd]);launched.append({'seed':seed,'gpu':gpu,'session':SESSIONS[seed],'run_root':str(root),'log':str(log)})
 return {'launched':bool(launched),'runs':launched,'scientific_authority':False}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=('status','launch'));a=ap.parse_args();print(json.dumps(state() if a.command=='status' else launch(),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
