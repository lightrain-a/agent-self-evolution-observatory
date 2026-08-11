from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-c2-evaluator-cpu.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-c2-evaluator-cpu.js"
ACTORS=("a0","a1","a2")
EVALUATORS=("e0","e1","e2")
ACTOR_ABILITY={"a0":0.35,"a1":0.55,"a2":0.75}
EVAL_BIAS={"e0":0.0,"e1":0.18,"e2":-0.08}
SHORTCUT_WEIGHT={"e0":0.0,"e1":0.0,"e2":0.42}


def _now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _anchors()->list[dict[str,Any]]:
    rows=[]
    difficulties=(-0.20,-0.10,0.0,0.10,0.20,0.30)
    for actor in ACTORS:
        for j,diff in enumerate(difficulties):
            shortcut=float((j+ACTORS.index(actor))%2)
            truth=max(0.0,min(1.0,ACTOR_ABILITY[actor]-diff))
            rows.append({"actor":actor,"task":f"t{j}","shortcut":shortcut,"truth":truth})
    return rows


def _score(row:dict[str,Any],evaluator:str,shortcut_override:float|None=None)->float:
    z=row["shortcut"] if shortcut_override is None else shortcut_override
    return row["truth"]+EVAL_BIAS[evaluator]+SHORTCUT_WEIGHT[evaluator]*z


def _matrix(rows:list[dict[str,Any]])->list[dict[str,Any]]:
    out=[]
    for row in rows:
        for evaluator in EVALUATORS:
            out.append({**row,"evaluator":evaluator,"score":_score(row,evaluator)})
    return out


def _fit_intercept_z(rows:list[dict[str,Any]],evaluator:str)->tuple[float,float]:
    xs=[r for r in rows if r["evaluator"]==evaluator]
    z0=[r["score"]-r["truth"] for r in xs if r["shortcut"]==0]
    z1=[r["score"]-r["truth"] for r in xs if r["shortcut"]==1]
    b=sum(z0)/len(z0); w=sum(z1)/len(z1)-b
    return b,w


def _proposed(rows:list[dict[str,Any]])->dict[str,Any]:
    # Cross-version attribution + causal neutralization. Actor-fixed residuals localize evaluator drift;
    # paired shortcut neutralization estimates the rubric atom effect.
    params={}; intervention_calls=0
    for evaluator in EVALUATORS:
        residuals=[r["score"]-r["truth"] for r in rows if r["evaluator"]==evaluator and r["shortcut"]==0]
        bias=sum(residuals)/len(residuals)
        paired=[]
        for r in [x for x in _anchors() if x["shortcut"]==1]:
            paired.append(_score(r,evaluator,1.0)-_score(r,evaluator,0.0)); intervention_calls+=2
        weight=sum(paired)/len(paired)
        params[evaluator]={"bias":bias,"shortcut_weight":weight}
    return {"params":params,"intervention_calls":intervention_calls}


def _simple(rows:list[dict[str,Any]])->dict[str,Any]:
    # Same external anchors and observed evaluator scores, no cross-version decomposition or causal intervention.
    return {"params":{e:{"bias":_fit_intercept_z(rows,e)[0],"shortcut_weight":_fit_intercept_z(rows,e)[1]} for e in EVALUATORS},"intervention_calls":0}


def _repair_eval(rows:list[dict[str,Any]],params:dict[str,Any])->dict[str,Any]:
    errors=[]; by_eval={e:[] for e in EVALUATORS}
    for row in rows:
        p=params[row["evaluator"]]
        repaired=row["score"]-p["bias"]-p["shortcut_weight"]*row["shortcut"]
        err=abs(repaired-row["truth"]); errors.append(err); by_eval[row["evaluator"]].append(err)
    return {"mae":sum(errors)/len(errors),"max_error":max(errors),"by_evaluator_mae":{e:sum(v)/len(v) for e,v in by_eval.items()}}


def _attribution(rows:list[dict[str,Any]])->dict[str,Any]:
    truth={e:int(abs(EVAL_BIAS[e])>1e-12 or abs(SHORTCUT_WEIGHT[e])>1e-12) for e in EVALUATORS}
    cross={}; simple={}
    for e in EVALUATORS:
        xs=[r for r in rows if r["evaluator"]==e]
        mean_res=sum(r["score"]-r["truth"] for r in xs)/len(xs)
        z0=[r["score"]-r["truth"] for r in xs if r["shortcut"]==0]; z1=[r["score"]-r["truth"] for r in xs if r["shortcut"]==1]
        interaction=sum(z1)/len(z1)-sum(z0)/len(z0)
        cross[e]=int(abs(mean_res)>0.05 or abs(interaction)>0.05)
        simple[e]=int(max(abs(mean_res),abs(interaction))>0.05)
    return {"truth":truth,"cross_version":cross,"simple_anchor_residual":simple,"cross_accuracy":sum(cross[e]==truth[e] for e in EVALUATORS)/3,"simple_accuracy":sum(simple[e]==truth[e] for e in EVALUATORS)/3}


def run_c2_cpu_p0()->dict[str,Any]:
    anchors=_anchors(); matrix=_matrix(anchors); proposed=_proposed(matrix); simple=_simple(matrix)
    pe=_repair_eval(matrix,proposed["params"]); se=_repair_eval(matrix,simple["params"]); attr=_attribution(matrix)
    param_equal=all(abs(proposed["params"][e][k]-simple["params"][e][k])<1e-12 for e in EVALUATORS for k in ("bias","shortcut_weight"))
    repair_tie=(se["mae"]<=pe["mae"]+1e-12 and se["max_error"]<=pe["max_error"]+1e-12 and simple["intervention_calls"]<proposed["intervention_calls"] and param_equal)
    attribution_tie=attr["simple_accuracy"]>=attr["cross_accuracy"]
    stop=repair_tie and attribution_tie
    return {"schema_version":"1.0","generated_at":_now(),"idea_id":"evaluator-coadaptation-guard","code":"C-2",
      "scientific_role":"CPU 3x3 actor/evaluator anchor P0 with independent external truth",
      "design":{"actors":3,"evaluators":3,"anchor_responses":len(anchors),"cross_scores":len(matrix),"shortcut_feature":"binary rubric shortcut atom","actor_frozen_on_repair_batch":True,"independent_truth":"external/program anchor score"},
      "ground_truth":{"evaluator_bias":EVAL_BIAS,"shortcut_weight":SHORTCUT_WEIGHT},"attribution":attr,
      "cross_version_causal_repair":{"params":proposed["params"],"extra_intervention_calls":proposed["intervention_calls"],"evaluation":pe},
      "simple_anchor_residual_repair":{"params":simple["params"],"extra_intervention_calls":simple["intervention_calls"],"evaluation":se},
      "matched_simplification":{"baseline":"per-evaluator anchor residual intercept+shortcut calibration","same_anchor_truth":True,"same_observed_cross_scores":True,"same_parameter_count":True,"parameters_identical":param_equal,"repair_tied_or_better":repair_tie,"attribution_tied_or_better":attribution_tie},
      "decision":"STOP_SIMPLE_ANCHOR_RESIDUAL_CALIBRATION_EQUIVALENT" if stop else "P0_SIGNAL_CONTINUE","standalone_claim_stop_authorized":stop,"p1_authorized":False,
      "next_action":"Keep cross-version matrices only as diagnostics; merge evaluator repair into simple frozen-anchor calibration and do not spend GPU on standalone C-2." if stop else "Validate the surviving component on a second evaluator family after human review."}


def write_c2_cpu_p0(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=run_c2_cpu_p0(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_C2_EVALUATOR_CPU = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state


if __name__=="__main__": print(json.dumps(write_c2_cpu_p0(),ensure_ascii=False,indent=2))
