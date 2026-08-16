from __future__ import annotations
import argparse,hashlib,json,os,pathlib,time
from typing import Any
from research_pipeline import asset_first_stri_skillrl_fixed_task_p0d as p0d

EXPERIMENT_ID='STRI-SKILLRL-FINAL-POLICY-COMPETENCY-P0E-20260816'
POLICY_REVISION='2ce16cb90e6357892dde201928279d4513d35c59'
DECODE_SEEDS=(2026081603,2026081604)
GPU_CAP_SECONDS=1350.0
CONTRACT='asset-first-stri-skillrl-final-policy-p0e-contract-20260816.json'
PANEL='asset-first-stri-skillrl-final-policy-p0e-panel-20260816.json'
REVIEW='asset-first-stri-skillrl-final-policy-p0e-review-20260816.json'
MODEL_MANIFEST='asset-first-stri-skillrl-final-policy-p0e-model-manifest-20260816.json'
DEAD_END='asset-first-stri-skillrl-p0d-dead-end-diagnosis-20260816.json'

def sha(p:pathlib.Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(16<<20),b''):h.update(b)
 return h.hexdigest()
def load(p:pathlib.Path)->dict[str,Any]:return json.loads(p.read_text(encoding='utf-8'))
def atomic(path:pathlib.Path,d:dict[str,Any])->None:
 path.parent.mkdir(parents=True,exist_ok=True);t=path.with_suffix(path.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');t.replace(path)
def uid(task:dict[str,Any],seed:int)->str:return f"{task['family']}|{task['selection_sha256'][:12]}|{seed}"

def validate_model(model:pathlib.Path,manifest:dict[str,Any],full_hash:bool=True)->dict[str,Any]:
 if manifest.get('status')!='VALIDATED_PRE_OUTCOME_HF_MODEL':raise ValueError('model-manifest-not-validated')
 if manifest.get('source_revision')!=POLICY_REVISION:raise ValueError('model-revision')
 if pathlib.Path(str(manifest.get('model_dir') or '')).resolve()!=model.resolve():raise ValueError('model-dir')
 checked=[]
 for row in manifest.get('files') or []:
  rel=str(row.get('file') or '');p=model/rel;size=int(row.get('bytes') or -1)
  if not rel or rel.startswith('/') or '..' in pathlib.PurePosixPath(rel).parts:raise ValueError('model-manifest-path')
  if not p.is_file() or p.stat().st_size!=size:raise ValueError(f'model-size:{rel}')
  item={'file':rel,'bytes':size}
  if full_hash:
   got=sha(p)
   if got!=str(row.get('sha256') or ''):raise ValueError(f'model-sha:{rel}')
   item['sha256']=got
  checked.append(item)
 if not checked:raise ValueError('empty-model-manifest')
 return {'ready':True,'architecture':manifest.get('architecture'),'parameters':manifest.get('parameters'),'tensor_bytes':manifest.get('tensor_bytes'),'files':checked}

def validate_controls(project:pathlib.Path,model:pathlib.Path,full_hash:bool=True)->dict[str,Any]:
 g=project/'generated';paths={k:g/n for k,n in {'contract':CONTRACT,'panel':PANEL,'review':REVIEW,'manifest':MODEL_MANIFEST,'dead_end':DEAD_END}.items()}
 for k,p in paths.items():
  if not p.is_file():raise ValueError(f'missing-control:{k}')
 c,panel,review,manifest,dead=(load(paths[x]) for x in ('contract','panel','review','manifest','dead_end'))
 csha,psha,msha=sha(paths['contract']),sha(paths['panel']),sha(paths['manifest'])
 if c.get('experiment_id')!=EXPERIMENT_ID or c.get('status')!='FROZEN_FOR_BOUNDED_EXECUTION_REVIEW':raise ValueError('contract-not-final-frozen')
 if (c.get('task_panel') or {}).get('sha256')!=psha:raise ValueError('panel-sha')
 if panel.get('experiment_id')!=EXPERIMENT_ID or panel.get('disjoint') is not True:raise ValueError('panel-invalid')
 if dead.get('disposition')!='SUBSTRATE_SUPPORT_FAILURE' or dead.get('mechanism_rejected') is not False:raise ValueError('parent-dead-end-invalid')
 link=(c.get('policy') or {}).get('merged_hf_manifest') or {}
 if link.get('path')!=f'generated/{MODEL_MANIFEST}' or link.get('sha256')!=msha:raise ValueError('model-manifest-link')
 if review.get('artifact_kind')!='independent-scientific-contract-review' or review.get('reviewed_contract_sha256')!=csha or review.get('verdict')!='CLEAR_FOR_BOUNDED_EXECUTION':raise ValueError('review-not-clear')
 checks=review.get('checks') or {}
 if not checks or not all(v is True for v in checks.values()):raise ValueError('review-checks')
 return {'contract_sha256':csha,'panel_sha256':psha,'review_sha256':sha(paths['review']),'model_manifest_sha256':msha,'dead_end_sha256':sha(paths['dead_end']),'model':validate_model(model,manifest,full_hash)}

def env_probe(source:pathlib.Path,panel:dict[str,Any],root:pathlib.Path)->dict[str,Any]:
 row=panel['competence_calibration_tasks'][0];game=str(pathlib.Path(os.environ.get('ALFWORLD_DATA','/data/wyt/agent-self-evolution-p0-52-data/alfworld'))/'json_2.1.1/valid_unseen'/row['relative_gamefile']);runner=p0d.load_world(source,root);envs=[];states=[]
 try:
  for _ in range(2):
   e=runner.build_env('eval_out_of_distribution',[game]);envs.append(e);o,i=e.reset();states.append((str(o[0]),p0d.info_commands(i)))
  if states[0]!=states[1]:raise ValueError('env-reset-replay')
  action=next((x for x in states[0][1] if x!='help'),None)
  if not action:raise ValueError('no-admissible-action')
  after=[]
  for e in envs:
   o,r,d,i=e.step([action]);after.append((str(o[0]),float(r[0]),bool(d[0]),p0d.info_won(i),p0d.info_commands(i)))
  if after[0]!=after[1]:raise ValueError('env-step-replay')
  return {'gamefile':game,'action':action,'reset_equal':True,'one_step_equal':True}
 finally:
  for e in envs:
   close=getattr(e,'close',None)
   if callable(close):close()

def preflight(project:pathlib.Path,source:pathlib.Path,model:pathlib.Path,root:pathlib.Path,full_hash:bool=True)->dict[str,Any]:
 ctrl=validate_controls(project,model,full_hash);panel=load(project/'generated'/PANEL);cal=panel.get('competence_calibration_tasks') or [];local=panel.get('local_causal_tasks') or [];conf=panel.get('future_confirmation_tasks') or [];games=[x['relative_gamefile'] for x in cal+local+conf]
 if (len(cal),len(local),len(conf),len(set(games)))!=(12,12,12,36):raise ValueError('panel-cardinality')
 rep=p0d.representation_replay(source,root);env=env_probe(source,panel,root)
 out={'schema_version':'1.0','experiment_id':EXPERIMENT_ID,**ctrl,'representation_replay':rep,'environment_replay':env,'calibration_units':24,'local_causal_units':24,'future_confirmation_units':24,'passed':True,'scientific_authority':False};atomic(root/'preflight.json',out);return out

def run_unit(runner,policy,SkillsOnlyMemory,SimpleMemory,prompts,projection,bank:pathlib.Path,task_row:dict[str,Any],seed:int,deadline:float)->dict[str,Any]:
 game=str(pathlib.Path(os.environ['ALFWORLD_DATA'])/'json_2.1.1/valid_unseen'/task_row['relative_gamefile']);env=runner.build_env('eval_out_of_distribution',[game]);hist=SimpleMemory();hist.reset(1);mem=SkillsOnlyMemory(str(bank),retrieval_mode='template');actions=[];responses=[];prompt_hashes=[];valids=[]
 try:
  o,info=env.reset();obs=str(o[0]);done=False;won=False;task=p0d.extract_task(obs);retrieved=mem.retrieve(task_description=task,top_k=p0d.TOP_K);memory_prompt=mem.format_for_prompt(retrieved);sem=[p0d.semantic_key(x) for x in retrieved['general_skills']];step=1
  while step<=p0d.MAX_STEPS and not done:
   if time.monotonic()>=deadline:return {'status':'BUDGET_EXHAUSTED_MID_UNIT','unit_id':uid(task_row,seed),'steps_completed':step-1}
   cmds=p0d.info_commands(info);prompt=p0d.build_obs(prompts,hist,mem,retrieved,task,obs,cmds,step==1);texts,_=policy.generate([prompt],p0d.step_seed(seed,task_row['selection_sha256'],step));text=texts[0];projected,iv=projection.alfworld_projection([text],[list(cmds)]);action=projected[0];before=obs;o,_,d,i=env.step([action]);hist.store({'text_obs':[before],'action':[action]});obs=str(o[0]);info=i;done=bool(d[0]);won=p0d.info_won(i);actions.append(action);responses.append(text);prompt_hashes.append(p0d.htext(prompt));valids.append(int(iv[0]));step+=1
  row={'unit_id':uid(task_row,seed),'task_family':task_row['family'],'gamefile':task_row['relative_gamefile'],'selection_sha256':task_row['selection_sha256'],'decode_seed':seed,'arm':'A_pristine','won':int(won),'done':done,'steps':len(actions),'projected_actions_sha256':p0d.htext(json.dumps(actions,ensure_ascii=False,separators=(',',':'))),'response_sha256s':[p0d.htext(x) for x in responses],'prompt_sha256s':prompt_hashes,'projection_valids':valids,'invalid_projection_count':sum(1-x for x in valids),'memory_prompt_sha256':p0d.htext(memory_prompt),'general_semantic_set_sha256':p0d.htext(json.dumps(sorted(set(sem)),ensure_ascii=False,separators=(',',':'))),'scientific_authority':False}
  return {'status':'COMPLETE','unit_id':row['unit_id'],'row':row}
 finally:
  close=getattr(env,'close',None)
  if callable(close):close()

def run_shard(project:pathlib.Path,source:pathlib.Path,model:pathlib.Path,root:pathlib.Path,seed_index:int,gpu_cap:float=GPU_CAP_SECONDS)->dict[str,Any]:
 if seed_index not in (0,1):raise ValueError('seed-index')
 ctrl=preflight(project,source,model,root,True);SkillsOnlyMemory,SimpleMemory,prompts,projection=p0d.load_author_modules(source);banks=p0d.materialize_banks(source,root/'banks');tasks=load(project/'generated'/PANEL)['competence_calibration_tasks'];seed=DECODE_SEEDS[seed_index];start=time.monotonic();policy=p0d.VllmPolicy(model);deadline=start+gpu_cap;raw=root/f'calibration-shard-{seed_index}.jsonl';units=[];status='COMPLETE'
 with raw.open('w',encoding='utf-8') as fh:
  for idx,task in enumerate(tasks,1):
   r=run_unit(p0d.load_world(source,root),policy,SkillsOnlyMemory,SimpleMemory,prompts,projection,banks['A_pristine'],task,seed,deadline)
   if r.get('status')!='COMPLETE':status=str(r.get('status'));break
   fh.write(json.dumps(r['row'],ensure_ascii=False)+'\n');fh.flush();units.append(r['unit_id']);print(json.dumps({'stage':'calibration','completed_units':idx,'planned_units':12,'seed_index':seed_index,'gpu_allocation_seconds':round(time.monotonic()-start,2)}),flush=True)
 elapsed=time.monotonic()-start;out={'schema_version':'1.0','experiment_id':EXPERIMENT_ID,'stage':'calibration','contract_sha256':ctrl['contract_sha256'],'seed_index':seed_index,'decode_seed':seed,'status':status,'planned_units':12,'completed_units':len(units),'unit_ids':units,'raw_rows_path':str(raw),'gpu_allocation_seconds':round(elapsed,3),'gpu_hours':round(elapsed/3600,6),'within_budget':elapsed<=gpu_cap and status=='COMPLETE','model_revision':POLICY_REVISION,'scientific_authority':False};atomic(root/f'calibration-shard-{seed_index}.json',out);return out

def aggregate(project:pathlib.Path,shards:list[pathlib.Path],out:pathlib.Path)->dict[str,Any]:
 panel=load(project/'generated'/PANEL);expected={uid(t,s) for t in panel['competence_calibration_tasks'] for s in DECODE_SEEDS};rows=[];seen=set();cost=0.;meta=[]
 for path in shards:
  d=load(path);cost+=float(d.get('gpu_allocation_seconds') or 0);meta.append({'path':str(path),'sha256':sha(path),'status':d.get('status'),'seed_index':d.get('seed_index'),'completed_units':d.get('completed_units')});raw=pathlib.Path(d['raw_rows_path']);rows.extend(json.loads(x) for x in raw.read_text().splitlines() if x.strip());seen.update(d.get('unit_ids') or [])
 raw_out=out.with_suffix('.jsonl');raw_out.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8');status='COMPLETE' if seen==expected and len(rows)==24 and all(x['status']=='COMPLETE' for x in meta) and cost<=2700 else 'INCOMPLETE';payload={'schema_version':'1.0','experiment_id':EXPERIMENT_ID,'stage':'calibration','status':status,'expected_units':24,'completed_units':len(seen),'unit_set_exact':seen==expected,'rows':len(rows),'shards':meta,'gpu_allocation_seconds':round(cost,3),'gpu_hours':round(cost/3600,6),'within_budget':cost<=2700,'raw_rows_path':str(raw_out),'scientific_authority':False};atomic(out,payload);return payload

def analyze(agg_path:pathlib.Path,out:pathlib.Path)->dict[str,Any]:
 agg=load(agg_path);raw=pathlib.Path(agg['raw_rows_path']);rows=[json.loads(x) for x in raw.read_text().splitlines() if x.strip()];errors=[]
 if agg.get('status')!='COMPLETE' or not agg.get('within_budget') or len(rows)!=24:errors.append('calibration-incomplete-or-over-budget')
 if len({r.get('unit_id') for r in rows})!=len(rows):errors.append('duplicate-calibration-unit')
 success=sum(int(r.get('won') or 0) for r in rows);fams=sorted({str(r.get('task_family')) for r in rows if int(r.get('won') or 0)==1});support=4<=success<=20 and len(fams)>=3
 if not 4<=success<=20:errors.append(f'pristine-success-headroom:{success}')
 if len(fams)<3:errors.append(f'pristine-success-family-support:{len(fams)}')
 outcome='INCONCLUSIVE_INFRASTRUCTURE' if agg.get('status')!='COMPLETE' else ('GO_COMPETENT_POLICY_SUPPORT' if support else 'STOP_NO_COMPETENT_POLICY_SUPPORT');material={'aggregate_sha256':sha(agg_path),'raw_sha256':sha(raw),'outcome':outcome,'success':success,'families':fams,'errors':errors};payload={'schema_version':'1.0','experiment_id':EXPERIMENT_ID,'stage':'calibration','outcome':outcome,'qualified_support':bool(support and agg.get('status')=='COMPLETE'),'qualification_errors':errors,'metrics':{'pristine_success_count':success,'pristine_success_rate':success/24 if len(rows)==24 else None,'families_with_success_count':len(fams),'families_with_success':fams},'evidence_manifest_sha256':p0d.htext(json.dumps(material,sort_keys=True,separators=(',',':'))),'claim_boundary':'Calibration only qualifies endpoint support. Failure is not evidence against STRI and forbids policy/task/checkpoint rescue.','scientific_authority':False};atomic(out,payload);return payload

def main()->None:
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=('preflight','run-shard','aggregate','analyze'));ap.add_argument('--project',type=pathlib.Path,default=pathlib.Path('.'));ap.add_argument('--source',type=pathlib.Path);ap.add_argument('--model',type=pathlib.Path);ap.add_argument('--run-root',type=pathlib.Path);ap.add_argument('--seed-index',type=int);ap.add_argument('--gpu-cap-seconds',type=float,default=GPU_CAP_SECONDS);ap.add_argument('--shard-run',type=pathlib.Path,action='append');ap.add_argument('--aggregate',type=pathlib.Path);ap.add_argument('--output',type=pathlib.Path);a=ap.parse_args()
 if a.command=='preflight':
  if not all((a.source,a.model,a.run_root)):raise SystemExit('--source/--model/--run-root required')
  r=preflight(a.project,a.source,a.model,a.run_root,True)
 elif a.command=='run-shard':
  if not all((a.source,a.model,a.run_root)) or a.seed_index is None:raise SystemExit('--source/--model/--run-root/--seed-index required')
  r=run_shard(a.project,a.source,a.model,a.run_root,a.seed_index,a.gpu_cap_seconds)
 elif a.command=='aggregate':
  if not a.shard_run or not a.output:raise SystemExit('--shard-run/--output required')
  r=aggregate(a.project,a.shard_run,a.output)
 else:
  if not a.aggregate or not a.output:raise SystemExit('--aggregate/--output required')
  r=analyze(a.aggregate,a.output)
 print(json.dumps(r,ensure_ascii=False))
if __name__=='__main__':main()
