from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math,os,pathlib,site,sys,tempfile,types,time
from collections import Counter
from typing import Any

CANDIDATE_ID='skill-taxonomy-representation-invariance'
EXPERIMENT_ID='STRI-SKILLRL-FIXED-TASK-DYNAMIC-P0D-20260816'
CONTRACT_SHA='1f40378349825557aa66bdcb01b98542ad396cbea449dd46cf7cfb76e541a718'
REVIEW_SHA='c2e00d9eff984e0405ae41b66994dc233852d121d519789ceebf1124e7d7d121'
PANEL_SHA='e1d6740cea30328c283f3658aa982631d8f2f2207f6806692dd47c2a2a3688b8'
REP_SHA='00bc3acdf79fe59460b1908d455f72cf93394fc975b63d4c5a48d659aa16c076'
AUTHOR_COMMIT='8e66726ed866a4e0a7f053586a41022798192e6c'
MODEL_REVISION='ba9c962eef80a49fc63a94c9728209a36057c671'
ARMS=('A_pristine','B_displacement_clone','C_identity_placebo','D_exact_quotient')
DECODE_SEEDS=(2026081601,2026081602)
TOP_K=6; HISTORY_LENGTH=2; MAX_STEPS=50; MAX_PROMPT_TOKENS=4096; MAX_RESPONSE_TOKENS=512
SOURCE_HASHES={
 'agent_system/memory/base.py':'cdb84ed42fdc426fa7a97d50f812b60eb6fb0e932fa32fdcc55680a321aa5db7',
 'agent_system/memory/memory.py':'d9940bf9d49442f76667b80aff7e80b7c93f37bef015b06641e60229bb3f0d9c',
 'agent_system/memory/skills_only_memory.py':'ba663c6d94fa35ac6ca81cafbd39196c3a29c68254a2e2469122d9ce67d01e64',
 'agent_system/environments/prompts/alfworld.py':'063bd5d629694d459f77c1f5cabec704e62ca1e5c9b58589ccfb5e571e65753e',
 'agent_system/environments/env_package/alfworld/projection.py':'e794d1217d613ef4b550cfe4bfd0b39b4deb10d47493f31f78aef7b5ebf6dd98',
 'agent_system/environments/env_manager.py':'243ef4e511dc797a544646bfef98d384ea6319c263bc4457fd5464578c6a2f86',
 'agent_system/environments/env_package/alfworld/configs/config_tw.yaml':'a33f87ab43253ea602f93c9a0b176771a8ae16a34cd953130e45fc03700f1f49',
 'memory_data/alfworld/claude_style_skills.json':'e8a953beac1809591fadf0d3509db5dea6e66b0fb56ddb573cf30e6d8879e909',
 'memory_data/alfworld/generated_memories_alfworld_total.json':'574738bbf6666182ff7faf5e60f454978f5081fe2e854b4ee41cb780d8e992df',
 'verl/trainer/config/ppo_trainer.yaml':'0f69218f169aed29a827818ca76fb26f7c1c5632bd9cbe318884617d5aa228cc'}

def sha(path:pathlib.Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def htext(x:str)->str:return hashlib.sha256(x.encode()).hexdigest()
def load(path:pathlib.Path):return json.loads(path.read_text(encoding='utf-8'))
def semantic_key(s:dict)->tuple[str,str,str]:return (str(s.get('title','')),str(s.get('principle','')),str(s.get('when_to_apply','')))
def extract_task(text:str)->str:
 marker='Your task is to: ';i=text.find(marker)
 if i<0:raise ValueError('task-description-not-found')
 return text[i+len(marker):].strip()
def mcnemar(left:list[int],right:list[int])->tuple[float,int,int]:
 b=sum(a==0 and c==1 for a,c in zip(left,right));c=sum(a==1 and c==0 for a,c in zip(left,right));n=b+c
 if n==0:return 1.0,b,c
 p=min(1.0,2*sum(math.comb(n,k) for k in range(min(b,c)+1))/(2**n));return p,b,c

def load_author_modules(source_root:pathlib.Path):
 for rel,expected in SOURCE_HASHES.items():
  p=source_root/rel
  if not p.is_file() or sha(p)!=expected:raise ValueError(f'author-source-sha:{rel}')
 memdir=source_root/'agent_system/memory';pkg='_skillrl_p0d_mem';mod=types.ModuleType(pkg);mod.__path__=[str(memdir)];sys.modules[pkg]=mod
 for name in ('base','memory','skills_only_memory'):
  spec=importlib.util.spec_from_file_location(f'{pkg}.{name}',memdir/f'{name}.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 def standalone(name,path):
  spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 prompts=standalone('_skillrl_p0d_prompts',source_root/'agent_system/environments/prompts/alfworld.py')
 projection=standalone('_skillrl_p0d_projection',source_root/'agent_system/environments/env_package/alfworld/projection.py')
 return sys.modules[f'{pkg}.skills_only_memory'].SkillsOnlyMemory,sys.modules[f'{pkg}.memory'].SimpleMemory,prompts,projection

def materialize_banks(source_root:pathlib.Path,out:pathlib.Path)->dict[str,pathlib.Path]:
 bank=load(source_root/'memory_data/alfworld/claude_style_skills.json');out.mkdir(parents=True,exist_ok=True)
 def cloned(target:str,dyn:str):
  b=copy.deepcopy(bank);t=next(s for s in b['general_skills'] if s['skill_id']==target);c=copy.deepcopy(t);c['skill_id']=dyn;b['general_skills'].append(c);return b
 payloads={'A_pristine':bank,'B_displacement_clone':cloned('gen_001','dyn_001'),'C_identity_placebo':cloned('gen_006','dyn_006'),'D_exact_quotient':cloned('gen_001','dyn_001')};paths={}
 for arm,b in payloads.items():
  p=out/f'{arm}.json';p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');paths[arm]=p
 return paths

def quotient_retrieval(mem,task:str)->dict:
 r=dict(mem.retrieve(task_description=task,top_k=TOP_K));chosen=[];seen=set();general=mem.skills.get('general_skills',[]);ordered=[s for s in general if str(s.get('skill_id','')).startswith('dyn_')]+[s for s in general if not str(s.get('skill_id','')).startswith('dyn_')]
 for s in ordered:
  k=semantic_key(s)
  if k in seen:continue
  seen.add(k);chosen.append(s)
  if len(chosen)>=TOP_K:break
 r['general_skills']=chosen;return r

def retrieval_for(arm:str,mem,task:str)->dict:return quotient_retrieval(mem,task) if arm=='D_exact_quotient' else mem.retrieve(task_description=task,top_k=TOP_K)
def build_obs(prompts,mem_history,mem_skill,retrieved:dict,task:str,text_obs:str,commands:list[str],init:bool)->str:
 admissible='\n '.join(f"'{s}'" for s in commands if s!='help')
 if init:return prompts.ALFWORLD_TEMPLATE_NO_HIS.format(current_observation=text_obs,admissible_actions=admissible)
 ctx,lens=mem_history.fetch(HISTORY_LENGTH,obs_key='text_obs',action_key='action');memory_prompt=mem_skill.format_for_prompt(retrieved)
 return prompts.ALFWORLD_TEMPLATE_WITH_MEMORY.format(task_description=task,retrieved_memories=memory_prompt,step_count=len(mem_history[0]),history_length=lens[0],action_history=ctx[0],current_step=len(mem_history[0])+1,current_observation=text_obs,admissible_actions=admissible)

def step_seed(base:int,task_id:str,step:int)->int:return int(hashlib.sha256(f'{base}|{task_id}|{step}'.encode()).hexdigest()[:8],16)

def couple_exact_quotient_response(active:list[str],prompts:list[str],texts:list[str])->list[str]:
 out=list(texts)
 if 'A_pristine' in active and 'D_exact_quotient' in active:
  ia=active.index('A_pristine');id_=active.index('D_exact_quotient')
  if prompts[ia]!=prompts[id_]:raise RuntimeError('A-D-prompt-divergence')
  # A and D are the same represented state by construction. vLLM does not
  # guarantee that two separate sampling requests with the same seed consume
  # the same random stream, so use one realized response for both arms. This
  # couples only the exact-quotient negative control; B/C remain independently
  # sampled and the scientific treatment, tasks, thresholds, and model stay fixed.
  out[id_]=out[ia]
 return out

MODEL_SHARDS={
 'model-00001-of-00009.safetensors':(1886423520,'c2474c3652851fb82b796b5ed8b2c1ac44308fd783ffe418a923d5e1f2ddf36f'),
 'model-00002-of-00009.safetensors':(1864467800,'a3664c32d79e954ba3e53999d932b4e75525e5918ae12b88f01d821180c61a21'),
 'model-00003-of-00009.safetensors':(1864467800,'c03d1ec906536dc0f451c537c65524e1822ccbb406b7957b1ff3b62caa75a605'),
 'model-00004-of-00009.safetensors':(1864467824,'13d6885bcaf3d0b7e2877625d71807222c86975151cd570b11b541c9e74a09a0'),
 'model-00005-of-00009.safetensors':(1864467848,'a518f9e0580dff92b9fb6f939e741319132c1587fc266ff42db017641a489ad4'),
 'model-00006-of-00009.safetensors':(1864467848,'cf05a5bbf89029d1a05e75ccc005445c66e633729fbb235e18835ec14214af6f'),
 'model-00007-of-00009.safetensors':(1864467848,'21cae2d49adbb4971e20ba7b9b6d40b65c5809070e3cc849e65a2e0135e7439c'),
 'model-00008-of-00009.safetensors':(1068046456,'04a9e70ece01bacb30daa7d43b4f3f32eba139ac6fe26f46ed6642af3e0d1ff6'),
 'model-00009-of-00009.safetensors':(1089994880,'06006972c3be88e8a44fe21cfe2b0472b130780c781a741f8f90f1fe5ba3aae2')}

def validate_model(model:pathlib.Path)->dict:
 rows=[]
 for f,(size,expected) in MODEL_SHARDS.items():
  p=model/f
  if not p.is_file() or p.stat().st_size!=size:raise ValueError(f'model-shard-size:{f}')
  got=sha(p)
  if got!=expected:raise ValueError(f'model-shard-sha:{f}')
  rows.append({'file':f,'bytes':size,'sha256':got})
 cfg=load(model/'config.json');idx=load(model/'model.safetensors.index.json')
 if cfg.get('architectures')!=['Qwen2ForCausalLM'] or int((idx.get('metadata') or {}).get('total_size') or 0)!=15231233024:raise ValueError('model-metadata-mismatch')
 return {'revision':MODEL_REVISION,'architecture':'Qwen2ForCausalLM','shards':rows,'total_bytes':sum(r['bytes'] for r in rows)}

def validate_control_files(project:pathlib.Path)->dict:
 files={
  'contract':project/'generated/asset-first-stri-skillrl-fixed-task-p0d-contract-20260816.json',
  'review':project/'generated/asset-first-stri-skillrl-fixed-task-p0d-review-20260816.json',
  'panel':project/'generated/asset-first-stri-skillrl-fixed-task-p0d-panel-20260816.json',
  'representation':project/'generated/asset-first-stri-skillrl-fixed-task-p0d-representation-audit-20260816.json'}
 expected={'contract':CONTRACT_SHA,'review':REVIEW_SHA,'panel':PANEL_SHA,'representation':REP_SHA}
 for k,p in files.items():
  if not p.is_file() or sha(p)!=expected[k]:raise ValueError(f'control-sha:{k}')
 review=load(files['review'])
 if review.get('verdict')!='CLEAR_FOR_BOUNDED_EXECUTION' or not all((review.get('checks') or {}).values()):raise ValueError('independent-review-not-clear')
 return {k:str(p) for k,p in files.items()}

def representation_replay(source:pathlib.Path,run_root:pathlib.Path)->dict:
 SkillsOnlyMemory,_,_,_=load_author_modules(source);paths=materialize_banks(source,run_root/'banks');mem={}
 for arm,p in paths.items():
  mem[arm]=SkillsOnlyMemory(str(p),retrieval_mode='template')
 tasks=[str(x['contextual_description']) for x in load(source/'memory_data/alfworld/generated_memories_alfworld_total.json')]
 counts=Counter()
 for task in tasks:
  ra=mem['A_pristine'].retrieve(task_description=task,top_k=TOP_K);rb=mem['B_displacement_clone'].retrieve(task_description=task,top_k=TOP_K);rc=mem['C_identity_placebo'].retrieve(task_description=task,top_k=TOP_K);rd=quotient_retrieval(mem['D_exact_quotient'],task)
  sa=[semantic_key(x) for x in ra['general_skills']];sb=[semantic_key(x) for x in rb['general_skills']];sc=[semantic_key(x) for x in rc['general_skills']];sd=[semantic_key(x) for x in rd['general_skills']]
  pa=mem['A_pristine'].format_for_prompt(ra);pb=mem['B_displacement_clone'].format_for_prompt(rb);pc=mem['C_identity_placebo'].format_for_prompt(rc);pd=mem['D_exact_quotient'].format_for_prompt(rd)
  counts['treatment_set_changed']+=set(sb)!=set(sa);counts['treatment_prompt_changed']+=pb!=pa;counts['placebo_set_changed']+=set(sc)!=set(sa);counts['placebo_prompt_changed']+=pc!=pa;counts['quotient_set_restored']+=set(sd)==set(sa);counts['quotient_prompt_restored']+=pd==pa
 out={'released_tasks':len(tasks),'counts':dict(counts),'passed':len(tasks)==223 and counts['treatment_set_changed']==223 and counts['placebo_set_changed']==0 and counts['placebo_prompt_changed']==223 and counts['quotient_set_restored']==223 and counts['quotient_prompt_restored']==223,'scientific_authority':False}
 if not out['passed']:raise ValueError('representation-replay-failed')
 return out

def load_world(source:pathlib.Path,run_root:pathlib.Path):
 os.environ.setdefault('ALFWORLD_DATA','/data/wyt/agent-self-evolution-p0-52-data/alfworld');os.environ.setdefault('P0_EXTRA_SITE','/data/wyt/envs/agent_evolution_p0_site_52');site.addsitedir(os.environ['P0_EXTRA_SITE'])
 from research_pipeline.p0_alfworld_adapter import load_config,ALFWorldGameRunner
 cfg=load_config(source/'agent_system/environments/env_package/alfworld/configs/config_tw.yaml');cfg.setdefault('general',{})['save_path']=str(run_root/'alfworld-runtime');return ALFWorldGameRunner(cfg)

def env_replay_probe(source:pathlib.Path,project:pathlib.Path,run_root:pathlib.Path)->dict:
 panel=load(project/'generated/asset-first-stri-skillrl-fixed-task-p0d-panel-20260816.json');rel=panel['local_p0_tasks'][0]['relative_gamefile'];game=str(pathlib.Path(os.environ.get('ALFWORLD_DATA','/data/wyt/agent-self-evolution-p0-52-data/alfworld'))/'json_2.1.1/valid_unseen'/rel);runner=load_world(source,run_root);envs=[];states=[]
 try:
  for _ in range(2):
   e=runner.build_env('eval_out_of_distribution',[game]);envs.append(e);obs,info=e.reset();cmd=list((info.get('admissible_commands') or [[]])[0]);states.append((str(obs[0]),cmd,info))
  if states[0][0]!=states[1][0] or states[0][1]!=states[1][1]:raise ValueError('env-reset-replay-mismatch')
  action=next((x for x in states[0][1] if x!='help'),None)
  if not action:raise ValueError('no-admissible-action')
  after=[]
  for e in envs:
   o,r,d,i=e.step([action]);after.append((str(o[0]),float(r[0]),bool(d[0]),bool((i.get('won') or [False])[0])))
  if after[0]!=after[1]:raise ValueError('env-step-replay-mismatch')
  return {'gamefile':game,'action':action,'reset_equal':True,'one_step_equal':True,'scientific_authority':False}
 finally:
  for e in envs:
   c=getattr(e,'close',None)
   if callable(c):c()

def preflight(project:pathlib.Path,source:pathlib.Path,model:pathlib.Path,run_root:pathlib.Path,require_model:bool=True)->dict:
 controls=validate_control_files(project);rep=representation_replay(source,run_root);env=env_replay_probe(source,project,run_root);panel=load(project/'generated/asset-first-stri-skillrl-fixed-task-p0d-panel-20260816.json')
 local=panel.get('local_p0_tasks') or [];held=panel.get('sealed_confirmation_tasks') or []
 if len(local)!=12 or len(held)!=12 or {x['relative_gamefile'] for x in local}&{x['relative_gamefile'] for x in held}:raise ValueError('task-panel-invalid')
 model_state=validate_model(model) if require_model else {'ready':False}
 out={'schema_version':'1.0','experiment_id':EXPERIMENT_ID,'contract_sha256':CONTRACT_SHA,'control_files':controls,'author_source_root':str(source),'author_commit':AUTHOR_COMMIT,'representation_replay':rep,'environment_replay':env,'history_length':HISTORY_LENGTH,'local_units':24,'sealed_confirmation_units':24,'model':model_state,'passed':True,'scientific_authority':False}
 run_root.mkdir(parents=True,exist_ok=True);(run_root/'preflight.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');return out

class VllmPolicy:
 def __init__(self,model:pathlib.Path,gpu_memory_utilization:float=.90):
  from vllm import LLM,SamplingParams
  self.SamplingParams=SamplingParams;self.llm=LLM(model=str(model),tokenizer=str(model),tensor_parallel_size=1,gpu_memory_utilization=gpu_memory_utilization,max_model_len=MAX_PROMPT_TOKENS+MAX_RESPONSE_TOKENS,trust_remote_code=True,enable_prefix_caching=True);self.tok=self.llm.get_tokenizer()
 def render(self,text:str)->str:return self.tok.apply_chat_template([{'role':'user','content':text}],tokenize=False,add_generation_prompt=True)
 def generate(self,prompts:list[str],seed:int)->tuple[list[str],list[int]]:
  rendered=[self.render(p) for p in prompts];lens=[len(self.tok(x,add_special_tokens=False)['input_ids']) for x in rendered]
  if max(lens)>MAX_PROMPT_TOKENS:raise RuntimeError(f'prompt-token-overflow:{max(lens)}')
  params=[self.SamplingParams(temperature=.4,top_p=.8,top_k=20,repetition_penalty=1.05,max_tokens=MAX_RESPONSE_TOKENS,seed=seed) for _ in rendered]
  outs=self.llm.generate(rendered,params,use_tqdm=False);return [o.outputs[0].text for o in outs],lens

def unit_id(task_row:dict,seed:int)->str:return f"{task_row['family']}|{task_row['selection_sha256'][:12]}|{seed}"
def info_commands(info:dict)->list[str]:return list((info.get('admissible_commands') or [[]])[0])
def info_won(info:dict)->bool:return bool((info.get('won') or [False])[0])

def run_unit(runner,policy:VllmPolicy,SkillsOnlyMemory,SimpleMemory,prompts_mod,projection_mod,bank_paths:dict[str,pathlib.Path],task_row:dict,base_seed:int,deadline:float)->dict:
 game=str(pathlib.Path(os.environ['ALFWORLD_DATA'])/'json_2.1.1/valid_unseen'/task_row['relative_gamefile']);envs={};hist={};mem={};retrieved={};obs={};info={};done={};won={};actions={a:[] for a in ARMS};responses={a:[] for a in ARMS};prompt_hashes={a:[] for a in ARMS};valids={a:[] for a in ARMS}
 try:
  for arm in ARMS:
   envs[arm]=runner.build_env('eval_out_of_distribution',[game]);o,i=envs[arm].reset();obs[arm]=str(o[0]);info[arm]=i;done[arm]=False;won[arm]=False;hist[arm]=SimpleMemory();hist[arm].reset(1);mem[arm]=SkillsOnlyMemory(str(bank_paths[arm]),retrieval_mode='template')
  first_obs=obs['A_pristine'];first_cmds=info_commands(info['A_pristine'])
  if any(obs[a]!=first_obs or info_commands(info[a])!=first_cmds for a in ARMS):raise RuntimeError('four-arm-reset-mismatch')
  task=extract_task(first_obs)
  for arm in ARMS:retrieved[arm]=retrieval_for(arm,mem[arm],task)
  sa={arm:[semantic_key(x) for x in retrieved[arm]['general_skills']] for arm in ARMS};mp={arm:mem[arm].format_for_prompt(retrieved[arm]) for arm in ARMS}
  if set(sa['B_displacement_clone'])==set(sa['A_pristine']):raise RuntimeError('local-treatment-no-displacement')
  if set(sa['C_identity_placebo'])!=set(sa['A_pristine']):raise RuntimeError('local-placebo-semantic-change')
  if set(sa['D_exact_quotient'])!=set(sa['A_pristine']) or mp['D_exact_quotient']!=mp['A_pristine']:raise RuntimeError('local-quotient-not-restored')
  init_prompt=build_obs(prompts_mod,hist['A_pristine'],mem['A_pristine'],retrieved['A_pristine'],task,first_obs,first_cmds,True)
  if time.monotonic()>=deadline:return {'status':'BUDGET_EXHAUSTED_BEFORE_COMMON_PREFIX','unit_id':unit_id(task_row,base_seed)}
  common_text,lens=policy.generate([init_prompt],step_seed(base_seed,task_row['selection_sha256'],1));common=common_text[0];init_hash=htext(init_prompt)
  projected,iv=projection_mod.alfworld_projection([common], [list(first_cmds)]);first_action=projected[0];first_valid=int(iv[0])
  after=[]
  for arm in ARMS:
   before=obs[arm];o,r,d,i=envs[arm].step([first_action]);hist[arm].store({'text_obs':[before],'action':[first_action]});obs[arm]=str(o[0]);info[arm]=i;done[arm]=bool(d[0]);won[arm]=info_won(i);actions[arm].append(first_action);responses[arm].append(common);prompt_hashes[arm].append(init_hash);valids[arm].append(first_valid);after.append((obs[arm],float(r[0]),done[arm],won[arm],info_commands(i)))
  if len({json.dumps(x,sort_keys=True) for x in after})!=1:raise RuntimeError('common-prefix-step-replay-mismatch')
  step=2
  while step<=MAX_STEPS and not all(done.values()):
   if time.monotonic()>=deadline:return {'status':'BUDGET_EXHAUSTED_MID_UNIT','unit_id':unit_id(task_row,base_seed),'steps_completed':step-1}
   if done['A_pristine']!=done['D_exact_quotient'] or won['A_pristine']!=won['D_exact_quotient']:raise RuntimeError('A-D-termination-divergence')
   active=[a for a in ARMS if not done[a]];prompts=[]
   for arm in active:
    prompts.append(build_obs(prompts_mod,hist[arm],mem[arm],retrieved[arm],task,obs[arm],info_commands(info[arm]),False))
   if 'A_pristine' in active and 'D_exact_quotient' in active:
    ia=active.index('A_pristine');id_=active.index('D_exact_quotient')
    if prompts[ia]!=prompts[id_]:raise RuntimeError('A-D-prompt-divergence')
   texts,lens=policy.generate(prompts,step_seed(base_seed,task_row['selection_sha256'],step))
   if len(texts)!=len(active):raise RuntimeError('generation-count-mismatch')
   texts=couple_exact_quotient_response(active,prompts,texts)
   for arm,text,prompt_text in zip(active,texts,prompts):
    cmds=info_commands(info[arm]);projected,iv=projection_mod.alfworld_projection([text],[list(cmds)]);action=projected[0];before=obs[arm];o,r,d,i=envs[arm].step([action]);hist[arm].store({'text_obs':[before],'action':[action]});obs[arm]=str(o[0]);info[arm]=i;done[arm]=bool(d[0]);won[arm]=info_won(i);actions[arm].append(action);responses[arm].append(text);prompt_hashes[arm].append(htext(prompt_text));valids[arm].append(int(iv[0]))
   if actions['A_pristine']!=actions['D_exact_quotient'] or responses['A_pristine']!=responses['D_exact_quotient'] or obs['A_pristine']!=obs['D_exact_quotient']:raise RuntimeError('A-D-trajectory-divergence')
   step+=1
  rows=[]
  for arm in ARMS:
   rows.append({'unit_id':unit_id(task_row,base_seed),'task_family':task_row['family'],'gamefile':task_row['relative_gamefile'],'selection_sha256':task_row['selection_sha256'],'decode_seed':base_seed,'arm':arm,'won':int(won[arm]),'done':bool(done[arm]),'steps':len(actions[arm]),'projected_actions':actions[arm],'projected_actions_sha256':htext(json.dumps(actions[arm],ensure_ascii=False,separators=(',',':'))),'response_sha256s':[htext(x) for x in responses[arm]],'prompt_sha256s':prompt_hashes[arm],'projection_valids':valids[arm],'invalid_projection_count':sum(1-v for v in valids[arm]),'memory_prompt_sha256':htext(mp[arm]),'general_semantic_keys_sha256':htext(json.dumps(sa[arm],ensure_ascii=False,separators=(',',':'))),'general_semantic_set_sha256':htext(json.dumps(sorted(set(sa[arm])),ensure_ascii=False,separators=(',',':'))),'scientific_authority':False})
  return {'status':'COMPLETE','unit_id':unit_id(task_row,base_seed),'rows':rows,'A_D_exact_trajectory':actions['A_pristine']==actions['D_exact_quotient'] and responses['A_pristine']==responses['D_exact_quotient'],'common_prefix_response_sha256':htext(common),'common_prefix_action':first_action,'common_prefix_valid':first_valid}
 finally:
  for e in envs.values():
   c=getattr(e,'close',None)
   if callable(c):c()

def run_shard(project:pathlib.Path,source:pathlib.Path,model:pathlib.Path,run_root:pathlib.Path,seed_index:int,gpu_cap_seconds:float=3600.0)->dict:
 if seed_index not in (0,1):raise ValueError('seed-index')
 preflight(project,source,model,run_root,require_model=True);SkillsOnlyMemory,SimpleMemory,prompts_mod,projection_mod=load_author_modules(source);bank_paths=materialize_banks(source,run_root/'banks');panel=load(project/'generated/asset-first-stri-skillrl-fixed-task-p0d-panel-20260816.json');tasks=panel['local_p0_tasks'];seed=DECODE_SEEDS[seed_index]
 allocation_start=time.monotonic();policy=VllmPolicy(model);deadline=allocation_start+gpu_cap_seconds;raw=run_root/f'shard-{seed_index}.jsonl';result_path=run_root/f'shard-{seed_index}.json';rows=[];units=[];status='COMPLETE'
 with raw.open('w',encoding='utf-8') as fh:
  for idx,task in enumerate(tasks,1):
   u=run_unit(load_world(source,run_root),policy,SkillsOnlyMemory,SimpleMemory,prompts_mod,projection_mod,bank_paths,task,seed,deadline)
   if u.get('status')!='COMPLETE':status=u['status'];break
   for row in u['rows']:fh.write(json.dumps(row,ensure_ascii=False)+'\n');rows.append(row)
   fh.flush();units.append(u['unit_id']);print(json.dumps({'completed_units':idx,'planned_units':len(tasks),'seed_index':seed_index,'gpu_allocation_seconds':round(time.monotonic()-allocation_start,2)},ensure_ascii=False),flush=True)
 allocation=time.monotonic()-allocation_start
 result={'schema_version':'1.0','experiment_id':EXPERIMENT_ID,'contract_sha256':CONTRACT_SHA,'seed_index':seed_index,'decode_seed':seed,'status':status,'planned_units':len(tasks),'completed_units':len(units),'unit_ids':units,'raw_rows_path':str(raw),'gpu_allocation_seconds':round(allocation,3),'gpu_hours':round(allocation/3600,6),'within_budget':allocation<=gpu_cap_seconds and status=='COMPLETE','model_revision':MODEL_REVISION,'scientific_authority':False};result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result

def aggregate(project:pathlib.Path,run_root:pathlib.Path,shards:list[pathlib.Path],out:pathlib.Path)->dict:
 panel=load(project/'generated/asset-first-stri-skillrl-fixed-task-p0d-panel-20260816.json');expected={unit_id(t,s) for t in panel['local_p0_tasks'] for s in DECODE_SEEDS};seen=set();rows=[];cost=0.0;shard_meta=[]
 for p in shards:
  d=load(p);cost+=float(d.get('gpu_allocation_seconds') or 0);shard_meta.append({'path':str(p),'sha256':sha(p),'seed_index':d.get('seed_index'),'status':d.get('status'),'completed_units':d.get('completed_units'),'gpu_allocation_seconds':d.get('gpu_allocation_seconds')})
  rp=pathlib.Path(d['raw_rows_path']);
  for line in rp.read_text(encoding='utf-8').splitlines():
   if line.strip():rows.append(json.loads(line))
  seen.update(d.get('unit_ids') or [])
 raw=out.with_suffix('.jsonl');raw.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
 status='COMPLETE' if seen==expected and len(rows)==len(expected)*4 and all(x['status']=='COMPLETE' for x in shard_meta) and cost<=7200 else 'INCOMPLETE'
 result={'schema_version':'1.0','experiment_id':EXPERIMENT_ID,'contract_sha256':CONTRACT_SHA,'status':status,'expected_units':24,'completed_units':len(seen),'rows':len(rows),'unit_set_exact':seen==expected,'shards':shard_meta,'gpu_allocation_seconds':round(cost,3),'gpu_hours':round(cost/3600,6),'within_budget':cost<=7200,'raw_rows_path':str(raw),'scientific_authority':False};out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result

def analyze(project:pathlib.Path,aggregate_path:pathlib.Path,out:pathlib.Path)->dict:
 agg=load(aggregate_path);raw=pathlib.Path(agg['raw_rows_path']);rows=[json.loads(x) for x in raw.read_text(encoding='utf-8').splitlines() if x.strip()];groups={}
 for r in rows:groups.setdefault(r['unit_id'],{})[r['arm']]=r
 errors=[]
 if agg.get('status')!='COMPLETE' or not agg.get('within_budget') or agg.get('completed_units')!=24:errors.append('aggregate-incomplete-or-over-budget')
 if len(groups)!=24:errors.append('unit-count')
 for uid,g in groups.items():
  if set(g)!=set(ARMS):errors.append(f'arm-set:{uid}');continue
  a,b,c,d=(g[x] for x in ARMS)
  if b['general_semantic_set_sha256']==a['general_semantic_set_sha256']:errors.append(f'treatment-no-semantic-displacement:{uid}')
  if c['general_semantic_set_sha256']!=a['general_semantic_set_sha256']:errors.append(f'placebo-semantic-change:{uid}')
  if c['memory_prompt_sha256']==a['memory_prompt_sha256']:errors.append(f'placebo-prompt-not-changed:{uid}')
  if d['general_semantic_set_sha256']!=a['general_semantic_set_sha256'] or d['memory_prompt_sha256']!=a['memory_prompt_sha256']:errors.append(f'quotient-not-restored:{uid}')
  if d['projected_actions_sha256']!=a['projected_actions_sha256'] or d['response_sha256s']!=a['response_sha256s'] or d['won']!=a['won'] or d['steps']!=a['steps']:errors.append(f'A-D-trajectory-not-identical:{uid}')
 units=sorted(groups);A=[int(groups[u]['A_pristine']['won']) for u in units if set(groups[u])==set(ARMS)];B=[int(groups[u]['B_displacement_clone']['won']) for u in units if set(groups[u])==set(ARMS)];C=[int(groups[u]['C_identity_placebo']['won']) for u in units if set(groups[u])==set(ARMS)];D=[int(groups[u]['D_exact_quotient']['won']) for u in units if set(groups[u])==set(ARMS)]
 pristine=sum(A)
 if len(A)==24 and not 4<=pristine<=20:errors.append(f'pristine-success-headroom:{pristine}')
 qualified=not errors and len(A)==24
 def rate(x):return sum(x)/len(x) if x else float('nan')
 def dis(x,y):return sum(a!=b for a,b in zip(x,y))/len(x) if x else float('nan')
 p,b01,b10=mcnemar(A,B) if len(A)==24 else (1.0,0,0);rA,rB,rC,rD=map(rate,(A,B,C,D));dB,dC,dD=dis(A,B),dis(A,C),dis(A,D)
 fams=set()
 if len(A)==24:
  for u,a,b in zip(units,A,B):
   if a!=b:fams.add(groups[u]['A_pristine']['task_family'])
 metrics={'pristine_success_count':pristine,'success_rate':{'A_pristine':rA,'B_displacement_clone':rB,'C_identity_placebo':rC,'D_exact_quotient':rD},'B_minus_A_success_rate':rB-rA if A else None,'C_minus_A_success_rate':rC-rA if A else None,'D_minus_A_success_rate':rD-rA if A else None,'paired_disagreement':{'B_vs_A':dB,'C_vs_A':dC,'D_vs_A':dD},'B_vs_A_disagreement_minus_C_vs_A':dB-dC if A else None,'B_vs_A_mcnemar_p':p,'discord_A0_B1':b01,'discord_A1_B0':b10,'family_replicated_flip_count':len(fams),'families_with_B_vs_A_flip':sorted(fams)}
 go=bool(qualified and p<.05 and abs(rB-rA)>=.125 and dB-dC>=.125 and dD<=.05 and abs(rD-rA)<=.05 and len(fams)>=2)
 stop=bool(qualified and p>=.05 and dB<=dC+.05 and dD<=.05 and abs(rD-rA)<=.05)
 outcome='GO_C4_FIXED_POLICY_DOWNSTREAM_EVIDENCE' if go else ('STOP_FIXED_POLICY_DYNAMIC_BRIDGE' if stop else 'INCONCLUSIVE')
 material={'contract':CONTRACT_SHA,'aggregate_sha256':sha(aggregate_path),'raw_sha256':sha(raw),'outcome':outcome,'metrics':metrics,'qualification_errors':errors};evidence_sha=htext(json.dumps(material,sort_keys=True,separators=(',',':')))
 result={'schema_version':'1.0','experiment_id':EXPERIMENT_ID,'contract_sha256':CONTRACT_SHA,'outcome':outcome,'qualified':qualified,'qualification_errors':errors,'qualified_units':len(A) if qualified else 0,'metrics':metrics,'aggregate_cost':{'gpu_allocation_seconds':agg.get('gpu_allocation_seconds'),'gpu_hours':agg.get('gpu_hours'),'within_budget':agg.get('within_budget')},'evidence_manifest_sha256':evidence_sha,'claim_if_go':'Supports only C4 fixed-policy downstream representation sensitivity on the SkillRL exact-clone subclass; C2 partial-overlap theorem remains the novelty evidence and C3/SQC superiority stays locked.','claim_if_stop':'Rejects only this SkillRL exact-clone downstream bridge; C1/C2 STRI remain unchanged.','scientific_authority':False};out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result

def main()->None:
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=('preflight','run-shard','aggregate','analyze'));ap.add_argument('--project',type=pathlib.Path,default=pathlib.Path('.'));ap.add_argument('--source',type=pathlib.Path);ap.add_argument('--model',type=pathlib.Path);ap.add_argument('--run-root',type=pathlib.Path);ap.add_argument('--seed-index',type=int);ap.add_argument('--gpu-cap-seconds',type=float,default=3600.0);ap.add_argument('--shard-run',type=pathlib.Path,action='append');ap.add_argument('--aggregate',type=pathlib.Path);ap.add_argument('--output',type=pathlib.Path);a=ap.parse_args()
 if a.command=='preflight':
  if not all((a.source,a.model,a.run_root)):raise SystemExit('--source/--model/--run-root required')
  result=preflight(a.project,a.source,a.model,a.run_root,True)
 elif a.command=='run-shard':
  if not all((a.source,a.model,a.run_root)) or a.seed_index is None:raise SystemExit('--source/--model/--run-root/--seed-index required')
  result=run_shard(a.project,a.source,a.model,a.run_root,a.seed_index,a.gpu_cap_seconds)
 elif a.command=='aggregate':
  if not a.run_root or not a.shard_run or not a.output:raise SystemExit('--run-root/--shard-run/--output required')
  result=aggregate(a.project,a.run_root,a.shard_run,a.output)
 else:
  if not a.aggregate or not a.output:raise SystemExit('--aggregate/--output required')
  result=analyze(a.project,a.aggregate,a.output)
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
