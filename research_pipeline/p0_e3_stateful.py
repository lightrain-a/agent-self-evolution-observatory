from __future__ import annotations

import copy, hashlib, json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .config import PROJECT_ROOT

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-e3-stateful.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-e3-stateful.js"

def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

FAMILIES={
 "ledger":{"create_ok":201,"update_ok":200,"delete_ok":204,"duplicate":409,"stale":409,"missing":404},
 "vault":{"create_ok":202,"update_ok":201,"delete_ok":200,"duplicate":422,"stale":412,"missing":410},
}
RECOVERY={"duplicate":"adopt-existing","stale":"refresh-retry","missing":"abort-not-found"}

@dataclass
class Store:
    family:str
    items:dict[str,dict[str,Any]]
    def snapshot(self): return copy.deepcopy(self.items)
    def create(self,key:str,value:str):
        cfg=FAMILIES[self.family]
        if key in self.items:return {"status":cfg["duplicate"],"error":"duplicate"}
        self.items[key]={"value":value,"version":1}; return {"status":cfg["create_ok"],"error":None}
    def update(self,key:str,value:str,version:int):
        cfg=FAMILIES[self.family]
        if key not in self.items:return {"status":cfg["missing"],"error":"missing"}
        if self.items[key]["version"]!=version:return {"status":cfg["stale"],"error":"stale"}
        self.items[key]={"value":value,"version":version+1}; return {"status":cfg["update_ok"],"error":None}
    def delete(self,key:str,version:int|None=None):
        cfg=FAMILIES[self.family]
        if key not in self.items:return {"status":cfg["missing"],"error":"missing"}
        if version is not None and self.items[key]["version"]!=version:return {"status":cfg["stale"],"error":"stale"}
        del self.items[key]; return {"status":cfg["delete_ok"],"error":None}

def _run_case(family:str,case:dict[str,Any])->dict[str,Any]:
    store=Store(family,copy.deepcopy(case.get("initial") or {})); before=store.snapshot()
    op=case["op"]
    if op=="create": response=store.create(case["key"],case["value"])
    elif op=="update": response=store.update(case["key"],case["value"],case["version"])
    elif op=="delete": response=store.delete(case["key"],case.get("version"))
    else: raise KeyError(op)
    first_status=response["status"]; recovery="none"
    if response["error"]:
        recovery=RECOVERY[response["error"]]
        if recovery=="refresh-retry":
            current=store.items.get(case["key"])
            if current and op=="update": response=store.update(case["key"],case["value"],current["version"])
            elif current and op=="delete": response=store.delete(case["key"],current["version"])
        elif recovery=="adopt-existing": pass
    return {"first_status":first_status,"recovery":recovery,"final":store.snapshot(),"before":before}

PROBES=[
 {"name":"create-ok","op":"create","key":"p-create","value":"v1","initial":{}},
 {"name":"update-ok","op":"update","key":"p-update","value":"v2","version":1,"initial":{"p-update":{"value":"v1","version":1}}},
 {"name":"delete-ok","op":"delete","key":"p-delete","version":1,"initial":{"p-delete":{"value":"v1","version":1}}},
 {"name":"duplicate","op":"create","key":"p-dup","value":"new","initial":{"p-dup":{"value":"old","version":3}}},
 {"name":"stale","op":"update","key":"p-stale","value":"new","version":1,"initial":{"p-stale":{"value":"old","version":4}}},
 {"name":"missing","op":"delete","key":"p-missing","version":1,"initial":{}},
]
HIDDEN=[
 {"name":"h-create","op":"create","key":"h1","value":"x","initial":{}},
 {"name":"h-update","op":"update","key":"h2","value":"x2","version":2,"initial":{"h2":{"value":"x","version":2}}},
 {"name":"h-delete","op":"delete","key":"h3","version":5,"initial":{"h3":{"value":"x","version":5}}},
 {"name":"h-duplicate","op":"create","key":"h4","value":"new","initial":{"h4":{"value":"old","version":2}}},
 {"name":"h-stale-delete","op":"delete","key":"h5","version":1,"initial":{"h5":{"value":"old","version":7}}},
 {"name":"h-missing-update","op":"update","key":"h6","value":"new","version":1,"initial":{}},
]

def _learn(probes:list[dict[str,Any]])->dict[str,Any]:
    by={row['name']:row['observation'] for row in probes}
    return {
      'success_status':{'create':by['create-ok']['first_status'],'update':by['update-ok']['first_status'],'delete':by['delete-ok']['first_status']},
      'error_status':{'duplicate':by['duplicate']['first_status'],'stale':by['stale']['first_status'],'missing':by['missing']['first_status']},
      'recovery':{'duplicate':by['duplicate']['recovery'],'stale':by['stale']['recovery'],'missing':by['missing']['recovery']},
      'create_version':1,'update_version_delta':1,
    }

def _predict(case:dict[str,Any],model:dict[str,Any])->dict[str,Any]:
    initial=copy.deepcopy(case.get('initial') or {}); key=case['key']; op=case['op']; error=None
    current=initial.get(key)
    if op=='create' and current is not None:error='duplicate'
    elif op in {'update','delete'} and current is None:error='missing'
    elif op in {'update','delete'} and case.get('version')!=current['version']:error='stale'
    first_status=model['error_status'][error] if error else model['success_status'][op]
    recovery=model['recovery'][error] if error else 'none'; final=copy.deepcopy(initial)
    if error in {'duplicate','missing'}: pass
    elif op=='create': final[key]={'value':case['value'],'version':model['create_version']}
    elif op=='update':
        version=current['version'] if error=='stale' else case['version']
        final[key]={'value':case['value'],'version':version+model['update_version_delta']}
    elif op=='delete': final.pop(key,None)
    return {'name':case['name'],'first_status':first_status,'recovery':recovery,'final':final}

def _hash(x:Any)->str:
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def run_stateful()->dict[str,Any]:
    probes={}; models={}; predictions={}
    for family in FAMILIES:
        rows=[{'name':case['name'],'observation':_run_case(family,case)} for case in PROBES]
        probes[family]=rows; models[family]=_learn(rows)
        predictions[family]=[_predict(case,models[family]) for case in HIDDEN]
    prediction_sha=_hash(predictions)
    hidden={}; scores={}; total=0; correct=0
    for family in FAMILIES:
        rows=[]; fam_correct=0; by={x['name']:x for x in predictions[family]}
        for case in HIDDEN:
            truth=_run_case(family,case); pred=by[case['name']]
            ok=(pred['first_status']==truth['first_status'] and pred['recovery']==truth['recovery'] and pred['final']==truth['final'])
            rows.append({'name':case['name'],'prediction':pred,'truth':truth,'pass':ok})
            total+=1; correct+=int(ok); fam_correct+=int(ok)
        hidden[family]=rows; scores[family]=fam_correct/len(rows)
    ceiling=(total==12 and correct==12 and all(v==1.0 for v in scores.values()))
    return {'schema_version':'1.0','generated_at':_now(),'idea_id':'bounded-probe-api-transition-operator','code':'E-3',
      'design':{'families':list(FAMILIES),'probes_per_family':6,'hidden_cases_per_family':6,'stateful':True,'independent_truth':'executable state snapshots','prediction_frozen_before_hidden':True,'same_pex_representation':True,'cross_operation_hidden_recovery':True},
      'baseline_fairness':{'same_target_probe_budget':True,'same_typed_pex_representation':True,'same_hidden_cases':True,'deterministic_baseline_has_no_source_training_advantage':True,'hidden_truth_used_before_prediction':False,'family_status_semantics_differ':True},
      'probe_rows':probes,'learned_target_semantics':models,'predictions':predictions,'prediction_sha256_before_hidden':prediction_sha,'hidden_rows':hidden,
      'metrics':{'total_hidden':total,'correct_hidden':correct,'stateful_semantic_accuracy':correct/total if total else 0.0,'family_accuracy':scores},
      'deterministic_baseline_ceiling':ceiling,'learned_arm_run':False,'standalone_claim_stop_authorized':ceiling,
      'decision':'STOP_STATEFUL_DETERMINISTIC_PEX_CEILING' if ceiling else 'OPEN_STATEFUL_LEARNED_ARM'}

def write_stateful(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=run_stateful()
    state['next_action']='Return E-3 to human DROP/merge review; deterministic isomorphic P/E/X matches hidden state-changing effects and recovery under the same six-probe budget.' if state['standalone_claim_stop_authorized'] else 'Run the cross-source learned P/E/X arm under exactly the same probes, states, and hidden cases.'
    json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    js_path.write_text('window.P0_E3_STATEFUL = '+json.dumps(state,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    return state

if __name__=='__main__': print(json.dumps(write_stateful(),ensure_ascii=False,indent=2))
