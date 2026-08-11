from __future__ import annotations

import itertools
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-a7-counterfactual-cpu.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-a7-counterfactual-cpu.js"
ACTIONS=("continue","commit","rollback","stop")


def _now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _utility(state:dict[str,float],action:str)->float:
    gain=state["gain"]; reg=state["regression"]; budget=state["budget"]; head=state["headroom"]
    if action=="continue": return gain + 1.5*head - 0.8*reg - 0.7*budget
    if action=="commit": return 1.5*gain - 1.8*reg - 0.2*budget
    if action=="rollback": return 1.3*reg - 0.4*max(gain,0) - 0.15
    return 0.05 - 0.15*budget


def _states()->list[dict[str,Any]]:
    rows=[]; idx=0
    for gain,reg,budget,head in itertools.product((-1.0,0.0,1.0),(0.0,1.0),(0.25,0.5,0.75,1.0),(0.0,1.0)):
        state={"gain":gain,"regression":reg,"budget":budget,"headroom":head}
        utilities={a:_utility(state,a) for a in ACTIONS}; optimal=max(ACTIONS,key=lambda a:(utilities[a],-ACTIONS.index(a)))
        split="hidden" if idx%3==2 else "calibration" if idx%3==1 else "train"
        rows.append({"state_id":f"s{idx:03d}","split":split,"features":state,"utilities":utilities,"optimal_action":optimal}); idx+=1
    return rows


def _features(row:dict[str,Any])->list[float]:
    f=row["features"]
    return [1.0,f["gain"],f["regression"],f["budget"],f["headroom"],f["gain"]*f["headroom"],f["regression"]*f["budget"]]


def _fit_linear(train:list[dict[str,Any]],epochs:int=800,lr:float=0.08)->dict[str,list[float]]:
    dims=len(_features(train[0])); w={a:[0.0]*dims for a in ACTIONS}
    for _ in range(epochs):
        grad={a:[0.0]*dims for a in ACTIONS}
        for row in train:
            x=_features(row); scores={a:sum(v*z for v,z in zip(w[a],x)) for a in ACTIONS}; mx=max(scores.values()); ex={a:math.exp(scores[a]-mx) for a in ACTIONS}; den=sum(ex.values()); p={a:ex[a]/den for a in ACTIONS}
            for a in ACTIONS:
                err=p[a]-float(row["optimal_action"]==a)
                for j,val in enumerate(x): grad[a][j]+=err*val
        for a in ACTIONS:
            for j in range(dims): w[a][j]-=lr*grad[a][j]/len(train)
    return w


def _predict_linear(model:dict[str,list[float]],row:dict[str,Any])->str:
    x=_features(row); return max(ACTIONS,key=lambda a:sum(v*z for v,z in zip(model[a],x)))


def _rule(row:dict[str,Any],params:tuple[float,float,float,float])->str:
    reg_cut,budget_stop,gain_continue,budget_continue=params; f=row["features"]
    if f["regression"]>=reg_cut: return "rollback"
    if f["budget"]>=budget_stop and f["gain"]<=0: return "stop"
    if f["headroom"]>=0.5 and f["gain"]>=gain_continue and f["budget"]<=budget_continue: return "continue"
    return "commit"


def _fit_rule(train:list[dict[str,Any]],cal:list[dict[str,Any]])->tuple[float,float,float,float]:
    candidates=list(itertools.product((0.5,1.0),(0.5,0.75,1.0),(-1.0,0.0,1.0),(0.5,0.75,1.0)))
    best=None
    for params in candidates:
        tr=sum(_rule(r,params)==r["optimal_action"] for r in train)/len(train)
        ca=sum(_rule(r,params)==r["optimal_action"] for r in cal)/len(cal)
        score=(ca,tr,-sum(abs(x) for x in params),tuple(-x for x in params))
        if best is None or score>best[0]: best=(score,params)
    return best[1]


def _threshold_baseline(row:dict[str,Any])->str:
    f=row["features"]
    if f["regression"]>=0.5:return "rollback"
    if f["gain"]>0 and f["budget"]<0.75:return "commit"
    return "stop"


def _majority(rows:list[dict[str,Any]])->str:
    return max(ACTIONS,key=lambda a:(sum(r["optimal_action"]==a for r in rows),-ACTIONS.index(a)))


def _fit_tree(rows:list[dict[str,Any]],depth:int)->dict[str,Any]:
    if depth<=0 or len({r["optimal_action"] for r in rows})<=1:
        return {"leaf":_majority(rows)}
    features=("gain","regression","budget","headroom"); best=None
    for key in features:
        vals=sorted({r["features"][key] for r in rows})
        cuts=[(a+b)/2 for a,b in zip(vals,vals[1:])]
        for cut in cuts:
            left=[r for r in rows if r["features"][key]<=cut]; right=[r for r in rows if r["features"][key]>cut]
            if not left or not right: continue
            score=sum(r["optimal_action"]==_majority(left) for r in left)+sum(r["optimal_action"]==_majority(right) for r in right)
            cand=(score,-abs(len(left)-len(right)),key,cut,left,right)
            if best is None or cand[:4]>best[:4]: best=cand
    if best is None:return {"leaf":_majority(rows)}
    _,_,key,cut,left,right=best
    return {"feature":key,"cut":cut,"left":_fit_tree(left,depth-1),"right":_fit_tree(right,depth-1)}


def _predict_tree(tree:dict[str,Any],row:dict[str,Any])->str:
    node=tree
    while "leaf" not in node:
        node=node["left"] if row["features"][node["feature"]]<=node["cut"] else node["right"]
    return node["leaf"]


def _tree_nodes(tree:dict[str,Any])->int:
    return 1 if "leaf" in tree else 1+_tree_nodes(tree["left"])+_tree_nodes(tree["right"])


def _evaluate(rows:list[dict[str,Any]],policy)->dict[str,Any]:
    correct=0; utility=0.0; oracle=0.0; worst_regret=0.0; actions={a:0 for a in ACTIONS}; details=[]
    for row in rows:
        action=policy(row); actions[action]+=1; truth=row["optimal_action"]; u=row["utilities"][action]; o=row["utilities"][truth]; regret=o-u
        correct+=int(action==truth); utility+=u; oracle+=o; worst_regret=max(worst_regret,regret)
        details.append({"state_id":row["state_id"],"action":action,"truth":truth,"utility":u,"oracle_utility":o,"regret":regret})
    return {"n":len(rows),"action_accuracy":correct/len(rows),"mean_utility":utility/len(rows),"oracle_mean_utility":oracle/len(rows),"mean_regret":(oracle-utility)/len(rows),"worst_regret":worst_regret,"action_counts":actions,"rows":details}


def run_a7_cpu_p0()->dict[str,Any]:
    rows=_states(); train=[r for r in rows if r["split"]=="train"]; cal=[r for r in rows if r["split"]=="calibration"]; hidden=[r for r in rows if r["split"]=="hidden"]
    model=_fit_linear(train); params=_fit_rule(train,cal)
    depth_scores=[]
    for depth in range(1,5):
        tree=_fit_tree(train,depth); score=_evaluate(cal,lambda r,t=tree:_predict_tree(t,r)); depth_scores.append((score["action_accuracy"],-score["mean_regret"],-depth,depth))
    best_depth=max(depth_scores)[3]; tree=_fit_tree(train+cal,best_depth)
    linear=_evaluate(hidden,lambda r:_predict_linear(model,r)); rule=_evaluate(hidden,lambda r:_rule(r,params)); tree_eval=_evaluate(hidden,lambda r:_predict_tree(tree,r)); threshold=_evaluate(hidden,_threshold_baseline)
    hidden_truth={a:sum(r["optimal_action"]==a for r in hidden) for a in ACTIONS}; support=all(v>0 for v in hidden_truth.values())
    equivalent=(tree_eval["mean_regret"]<=linear["mean_regret"]+1e-12 and tree_eval["worst_regret"]<=linear["worst_regret"]+1e-12 and tree_eval["action_accuracy"]>=linear["action_accuracy"]-1e-12)
    return {"schema_version":"1.0","generated_at":_now(),"idea_id":"counterfactual-evolution-decision-controller","code":"A-7",
      "scientific_role":"CPU same-state four-action P0 with programmatic counterfactual truth; no candidate regeneration",
      "design":{"states":len(rows),"train":len(train),"calibration":len(cal),"hidden":len(hidden),"actions":list(ACTIONS),"hidden_action_truth":hidden_truth,"all_actions_supported_hidden":support,"candidate_regeneration":False,"independent_truth":"frozen four-action utility table"},
      "linear_controller":{"weights":model,"hidden":linear},"matched_shallow_rule":{"params":{"reg_cut":params[0],"budget_stop":params[1],"gain_continue":params[2],"budget_continue":params[3]},"hidden":rule},"matched_cart":{"selected_depth":best_depth,"nodes":_tree_nodes(tree),"tree":tree,"hidden":tree_eval},"threshold_baseline":{"hidden":threshold},
      "matched_simplification":{"baseline":"calibration-selected shallow CART on identical state features","equivalent_or_better":equivalent},
      "decision":"STOP_MATCHED_SHALLOW_RULE_EQUIVALENT" if support and equivalent else "P0_SIGNAL_CONTINUE" if support and linear["mean_regret"]<threshold["mean_regret"] else "HOLD_ACTION_SUPPORT_OR_SIGNAL",
      "standalone_claim_stop_authorized":bool(support and equivalent),"p1_authorized":False,
      "next_action":"Merge A-7 into A-2 as a simple same-state counterfactual decision rule; do not spend GPU on a standalone learned-controller paper." if support and equivalent else "Build the real same-state four-action replay table only if this CPU P0 retains a nontrivial advantage over simple rules."}


def write_a7_cpu_p0(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=run_a7_cpu_p0(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_A7_COUNTERFACTUAL_CPU = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state


if __name__=="__main__": print(json.dumps(write_a7_cpu_p0(),ensure_ascii=False,indent=2))
