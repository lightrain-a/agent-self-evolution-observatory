from __future__ import annotations
import copy,hashlib
import torch
from research_pipeline.scienceworld_qwen_adapter import substantive_gold_action

def htxt(x:str)->str:return hashlib.sha256(str(x).encode()).hexdigest()
def unit_seed(unit_id:str)->int:return int(hashlib.sha256(unit_id.encode()).hexdigest()[:8],16)

def build_source_examples(env,policy,u,pair_count=6):
 env.load(u['task_family'],u['source_variation'],'',generateGoldPath=True); obs,info=env.reset(); gold=list(env.get_gold_action_sequence()); hist=[]; out=[]; seen=set(); task=env.taskdescription()
 for gi,a in enumerate(gold):
  key=(htxt(obs),a.strip().lower())
  if substantive_gold_action(a) and key not in seen and len(out)<pair_count:
   seen.add(key); out.append({'gold_index':gi,'task_desc':task,'observation':obs,'observation_sha256':htxt(obs),'inventory':env.inventory(),'history':copy.deepcopy(hist),'templates':list(env.get_possible_actions()),'objects':list(env.get_possible_objects()),'gold_action':a})
  obs2,reward,done,info=env.step(a); hist.append((a,obs2)); obs=obs2
  if done: break
 return out

def encode_example(policy,ex):
 msgs=policy._prompt(ex['task_desc'],ex['observation'],ex['inventory'],ex['history'],ex['templates'],ex['objects']); prompt=policy.tokenizer.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True); p=policy.tokenizer(prompt,return_tensors='pt',add_special_tokens=False)['input_ids'][0]; target='Action: '+ex['gold_action']+(policy.tokenizer.eos_token or ''); t=policy.tokenizer(target,return_tensors='pt',add_special_tokens=False)['input_ids'][0]; ids=torch.cat([p,t]).unsqueeze(0).to(policy.device); att=torch.ones_like(ids); labels=ids.clone(); labels[:,:p.numel()]=-100; return {'input_ids':ids,'attention_mask':att,'labels':labels}

def base_fingerprint(model):
 h=hashlib.sha256(); base=getattr(model,'model',model)
 layers=base.model.layers if hasattr(base,'model') and hasattr(base.model,'layers') else base.layers
 for i in (26,27):
  for n in ('q_proj','v_proj'):
   w=getattr(layers[i].self_attn,n).weight.detach().cpu().contiguous(); h.update(str(tuple(w.shape)).encode()); h.update(w.view(torch.uint16).numpy().tobytes())
 return h.hexdigest()

def attach_lora(policy,c):
 from peft import LoraConfig,get_peft_model
 lc=c['lora']; cfg=LoraConfig(r=lc['r'],lora_alpha=lc['alpha'],lora_dropout=lc['dropout'],bias=lc['bias'],task_type='CAUSAL_LM',target_modules=lc['target_modules'],layers_to_transform=lc['layers'],layers_pattern='layers'); policy.model=get_peft_model(policy.model,cfg); return policy.model

def train_adapter(policy,examples,c):
 seed=unit_seed(c['_unit_id']); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed); model=attach_lora(policy,c); model.train(); model.config.use_cache=False; opt=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=c['training']['learning_rate'],weight_decay=c['training']['weight_decay']); enc=[encode_example(policy,e) for e in examples]; losses=[]
 for step in range(c['training']['steps']):
  batch=enc[step%len(enc)]; opt.zero_grad(set_to_none=True); out=model(**batch); loss=out.loss; loss.backward(); opt.step(); losses.append(float(loss.detach().cpu()))
 model.eval(); model.config.use_cache=True; return {'seed':seed,'loss_first':losses[0],'loss_last':losses[-1],'losses':losses}

def eval_training_pairs(policy,examples):
 rows=[]
 for ex in examples:
  a,raw=policy.choose(ex['task_desc'],ex['observation'],ex['inventory'],ex['history'],ex['templates'],ex['objects']); rows.append({'observation_sha256':ex['observation_sha256'],'gold_action':ex['gold_action'],'pred_action':a,'exact':a.strip().lower()==ex['gold_action'].strip().lower(),'raw':raw})
 return rows
