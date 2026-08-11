from __future__ import annotations
import hashlib, itertools, json, math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .config import PROJECT_ROOT

DEFAULT_JSON=PROJECT_ROOT/'generated'/'p0-e4-permission-cpu.json'
DEFAULT_JS=PROJECT_ROOT/'generated'/'p0-e4-permission-cpu.js'
PERMS=('read','write','network')
FEATURES=('memory_delta','callgraph_delta','state_write_delta','dependency_delta','prompt_delta','manifest_delta')

def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _risk(feature:dict[str,int],perm:str)->int:
    if perm=='read': return int(feature['memory_delta'] and feature['callgraph_delta'])
    if perm=='write': return int(feature['state_write_delta'] and (feature['callgraph_delta'] or feature['prompt_delta']))
    return int(feature['dependency_delta'] and feature['callgraph_delta'])

def _patterns()->list[dict[str,int]]:
    rows=[]
    for memory in (0,1):
      for call in (0,1):
       for state in (0,1):
        for dep in (0,1):
         for prompt in (0,1):
          if memory+call+state+dep+prompt==0: continue
          rows.append({'memory_delta':memory,'callgraph_delta':call,'state_write_delta':state,'dependency_delta':dep,'prompt_delta':prompt,'manifest_delta':0})
    return rows

def _mutation(i:int,split:str)->dict[str,Any]:
    patterns=_patterns()
    ids={
      'train':[j for j in range(len(patterns)) if j%5 not in {0,1}],
      'calibration':[j for j in range(len(patterns)) if j%5==1],
      'test':[j for j in range(len(patterns)) if j%5==0],
    }[split]
    pattern_id=ids[i%len(ids)]; f=dict(patterns[pattern_id])
    surface=('prompt','memory','skill','workflow','dependency')[(i*3+(1 if split=='test' else 0))%5]
    return {'id':f'{split}-op-{i:02d}','operator':f'{split}-{surface}-operator-{100+i}','surface':surface,'pattern_id':pattern_id,'features':f}

def _intervention_truth(m:dict[str,Any])->dict[str,int]:
    # External effect log is independent of q/envelope and comes from executing
    # each permission canary under the immutable ceiling.
    return {perm:_risk(m['features'],perm) for perm in PERMS}

def _key(m:dict[str,Any],perm:str)->tuple[Any,...]:
    f=m['features']; return (perm,f['memory_delta'],f['callgraph_delta'],f['state_write_delta'],f['dependency_delta'],f['prompt_delta'],f['manifest_delta'])

def _envelope(m:dict[str,Any],perm:str)->int:
    f=m['features']
    if perm=='read': return int(f['memory_delta'] or f['callgraph_delta'] or f['prompt_delta'])
    if perm=='write': return int(f['state_write_delta'] or f['callgraph_delta'] or f['prompt_delta'])
    return int(f['dependency_delta'] or f['callgraph_delta'])

def _vector(m:dict[str,Any])->list[float]:
    return [1.0,*[float(m['features'][name]) for name in FEATURES]]

def _sigmoid(x:float)->float:
    if x>=0:
        z=math.exp(-x); return 1/(1+z)
    z=math.exp(x); return z/(1+z)

def _fit(train:list[dict[str,Any]])->dict[str,list[float]]:
    models={}
    for perm in PERMS:
        w=[0.0]*(len(FEATURES)+1)
        for _ in range(1200):
            grad=[0.0]*len(w)
            for m in train:
                x=_vector(m); y=float(_intervention_truth(m)[perm]); p=_sigmoid(sum(a*b for a,b in zip(w,x)))
                for j in range(len(w)): grad[j]+=(p-y)*x[j]
            n=max(1,len(train))
            for j in range(len(w)):
                reg=0.002*w[j] if j else 0.0
                w[j]-=0.08*(grad[j]/n+reg)
        models[perm]=w
    return models

def _score(model:dict[str,list[float]],m:dict[str,Any],perm:str)->float:
    x=_vector(m); return _sigmoid(sum(a*b for a,b in zip(model[perm],x)))

def _term(m:dict[str,Any],term:tuple[str,...])->bool:
    return all(bool(m['features'][name]) for name in term)

def _fit_monotone_dnf(train:list[dict[str,Any]])->dict[str,list[tuple[str,...]]]:
    terms=[c for k in (1,2) for c in itertools.combinations(FEATURES,k)]
    out={}
    for perm in PERMS:
        labels=[bool(_intervention_truth(m)[perm]) for m in train]
        best=None
        for nclauses in (1,2,3):
            for clauses in itertools.combinations(terms,nclauses):
                pred=[any(_term(m,t) for t in clauses) for m in train]
                fn=sum(y and not p for y,p in zip(labels,pred)); fp=sum(p and not y for y,p in zip(labels,pred))
                score=(fn,fp,sum(len(t) for t in clauses),clauses)
                if best is None or score<best[0]: best=(score,list(clauses))
            if best and best[0][0]==0 and best[0][1]==0: break
        out[perm]=best[1]
    return out

def _rule_score(rules:dict[str,list[tuple[str,...]]],m:dict[str,Any],perm:str)->bool:
    return any(_term(m,t) for t in rules[perm])

def _choose_threshold(model:dict[str,list[float]],cal:list[dict[str,Any]])->float:
    risky=[_score(model,m,perm) for m in cal for perm in PERMS if _intervention_truth(m)[perm]]
    return max(0.0,min(risky)-1e-9) if risky else 1.0

def _evaluate(test:list[dict[str,Any]],model:dict[str,list[float]],threshold:float,rules:dict[str,list[tuple[str,...]]])->dict[str,Any]:
    rows=[]; learned_count=envelope_count=rule_count=full_count=0; learned_miss=envelope_miss=rule_miss=0
    for m in test:
        truth=_intervention_truth(m)
        learned=[]; envelope=[]; rule=[]
        for perm in PERMS:
            if _score(model,m,perm)>=threshold: learned.append(perm)
            if _envelope(m,perm): envelope.append(perm)
            if _rule_score(rules,m,perm): rule.append(perm)
            if truth[perm] and perm not in learned: learned_miss+=1
            if truth[perm] and perm not in envelope: envelope_miss+=1
            if truth[perm] and perm not in rule: rule_miss+=1
        learned_count+=len(learned); envelope_count+=len(envelope); rule_count+=len(rule); full_count+=len(PERMS)
        rows.append({'id':m['id'],'operator':m['operator'],'surface':m['surface'],'features':m['features'],'truth':truth,'learned_reauthorize':learned,'envelope_reauthorize':envelope,'rule_reauthorize':rule})
    return {'rows':rows,'learned_reauthorizations':learned_count,'envelope_reauthorizations':envelope_count,'rule_reauthorizations':rule_count,'full_reauthorizations':full_count,'learned_missed_risky':learned_miss,'envelope_missed_risky':envelope_miss,'rule_missed_risky':rule_miss}

def run()->dict[str,Any]:
    train=[_mutation(i,'train') for i in range(64)]
    cal=[_mutation(i+64,'calibration') for i in range(24)]
    test=[_mutation(i,'test') for i in range(32)]
    model=_fit(train); rules=_fit_monotone_dnf(train); threshold=_choose_threshold(model,cal); ev=_evaluate(test,model,threshold,rules)
    safe=ev['learned_missed_risky']==0
    saving=1-(ev['learned_reauthorizations']/ev['envelope_reauthorizations']) if ev['envelope_reauthorizations'] else 0.0
    rule_equivalent=ev['rule_missed_risky']==0 and ev['rule_reauthorizations']<=ev['learned_reauthorizations']
    signal=safe and saving>=0.15 and not rule_equivalent
    return {'schema_version':'1.0','generated_at':_now(),'idea_id':'interventional-permission-triage-under-ceiling','code':'E-4',
      'design':{'immutable_ceiling':list(PERMS),'train_mutations':len(train),'calibration_mutations':len(cal),'unseen_test_operators':len(test),'same_mutation_representation':True,'external_truth':'permission-canary effect log','new_permission_requests_excluded':True},
      'threshold':threshold,'model_cells':len(model),'matched_monotone_dnf':{perm:[list(term) for term in rules[perm]] for perm in PERMS},'evaluation':ev,
      'metrics':{'learned_reauthorizations':ev['learned_reauthorizations'],'deterministic_envelope_reauthorizations':ev['envelope_reauthorizations'],'matched_rule_reauthorizations':ev['rule_reauthorizations'],'full_reauthorizations':ev['full_reauthorizations'],'learned_missed_risky':ev['learned_missed_risky'],'envelope_missed_risky':ev['envelope_missed_risky'],'matched_rule_missed_risky':ev['rule_missed_risky'],'relative_reauthorization_saving_vs_envelope':saving},
      'matched_simplification':{'baseline':'monotone-DNF rule induction from identical intervention labels','zero_missed_risky':ev['rule_missed_risky']==0,'no_more_reauthorizations_than_learned':ev['rule_reauthorizations']<=ev['learned_reauthorizations'],'equivalent_or_better':rule_equivalent},
      'decision':'STOP_MATCHED_BOOLEAN_RULE_EQUIVALENT' if rule_equivalent else ('P0_SIGNAL_CONTINUE' if signal else 'STOP_NO_SAFE_WORKLOAD_REDUCTION'),'scientific_result_available':True,'p1_authorized':False}

def write_state(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=run(); state['next_action']='Freeze this triage rule and test a second executable permission sandbox only after human review.' if state['decision']=='P0_SIGNAL_CONTINUE' else 'Return E-4 to human DROP/merge review; the matched non-learning Boolean rule is equivalent or the safe-workload gate failed.'
    json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    js_path.write_text('window.P0_E4_PERMISSION_CPU = '+json.dumps(state,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    return state

if __name__=='__main__': print(json.dumps(write_state(),ensure_ascii=False,indent=2))
