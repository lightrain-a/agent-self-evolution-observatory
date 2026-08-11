from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-e3-real-api.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-e3-real-api.js"
UA="agent-evolution-observatory-p0/1.0"

def _now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _shape(value:Any)->str:
    if isinstance(value,list): return "list"
    if isinstance(value,dict): return "object"
    return type(value).__name__

def _get(url:str)->dict[str,Any]:
    started=time.monotonic(); req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=15) as response:
            status=int(response.status); raw=response.read()
    except urllib.error.HTTPError as error:
        status=int(error.code); raw=error.read()
    except Exception as error:
        return {"status":"runtime-error","error_type":type(error).__name__,"message":str(error),"latency_s":time.monotonic()-started}
    try: parsed=json.loads(raw.decode("utf-8"))
    except Exception: parsed=None
    return {"status":status,"shape":_shape(parsed),"semantic_shape":"error" if status>=400 else _shape(parsed),"top_keys":sorted(parsed.keys())[:12] if isinstance(parsed,dict) else [],"bytes":len(raw),"body_sha256":hashlib.sha256(raw).hexdigest(),"latency_s":time.monotonic()-started}

def _recovery(status:int)->str:
    if status==404:return "abort-not-found"
    if status==401:return "authenticate-required"
    if status in {400,422}:return "repair-request"
    return "none"

TARGETS={
 "gitlab":{
  "docs":"https://docs.gitlab.com/api/projects/",
  "probes":[
   ("repo","https://gitlab.com/api/v4/projects/gitlab-org%2Fgitlab","object"),
   ("branches","https://gitlab.com/api/v4/projects/gitlab-org%2Fgitlab/repository/branches?per_page=1","list"),
   ("commits","https://gitlab.com/api/v4/projects/gitlab-org%2Fgitlab/repository/commits?per_page=1","list"),
   ("bad-repo","https://gitlab.com/api/v4/projects/__agent_evolution_missing_20260811__","error"),
   ("bad-ref","https://gitlab.com/api/v4/projects/gitlab-org%2Fgitlab/repository/branches/__agent_evolution_missing__","error"),
   ("auth-user","https://gitlab.com/api/v4/user","error")],
  "hidden":[
   ("tags","https://gitlab.com/api/v4/projects/gitlab-org%2Fgitlab/repository/tags?per_page=1","collection"),
   ("issues","https://gitlab.com/api/v4/projects/gitlab-org%2Fgitlab/issues?per_page=1","collection"),
   ("merge-requests","https://gitlab.com/api/v4/projects/gitlab-org%2Fgitlab/merge_requests?per_page=1","collection"),
   ("bad-tag","https://gitlab.com/api/v4/projects/gitlab-org%2Fgitlab/repository/tags/__agent_evolution_missing__","item"),
   ("bad-commit","https://gitlab.com/api/v4/projects/gitlab-org%2Fgitlab/repository/commits/__agent_evolution_missing__","item"),
   ("auth-user","https://gitlab.com/api/v4/user","auth-required")]},
 "codeberg":{
  "docs":"https://codeberg.org/api/swagger",
  "probes":[
   ("repo","https://codeberg.org/api/v1/repos/forgejo/forgejo","object"),
   ("branches","https://codeberg.org/api/v1/repos/forgejo/forgejo/branches?limit=1","list"),
   ("commits","https://codeberg.org/api/v1/repos/forgejo/forgejo/commits?limit=1","list"),
   ("bad-repo","https://codeberg.org/api/v1/repos/forgejo/__agent_evolution_missing_20260811__","error"),
   ("bad-ref","https://codeberg.org/api/v1/repos/forgejo/forgejo/branches/__agent_evolution_missing__","error"),
   ("auth-user","https://codeberg.org/api/v1/user","error")],
  "hidden":[
   ("tags","https://codeberg.org/api/v1/repos/forgejo/forgejo/tags?limit=1","collection"),
   ("issues","https://codeberg.org/api/v1/repos/forgejo/forgejo/issues?limit=1","collection"),
   ("pulls","https://codeberg.org/api/v1/repos/forgejo/forgejo/pulls?limit=1","collection"),
   ("bad-branch","https://codeberg.org/api/v1/repos/forgejo/forgejo/branches/__agent_evolution_missing__","item"),
   ("bad-commit","https://codeberg.org/api/v1/repos/forgejo/forgejo/git/commits/__agent_evolution_missing__","item"),
   ("auth-user","https://codeberg.org/api/v1/user","auth-required")]}}


def _probe_expected(name:str,shape:str)->tuple[int,str,str]:
    if name in {"repo","branches","commits"}: return 200,shape,"none"
    if name in {"bad-repo","bad-ref"}: return 404,"error","abort-not-found"
    if name=="bad-page": return 400,"error","repair-pagination"
    raise KeyError(name)

def _probe_contract(probe_rows:list[dict[str,Any]])->dict[str,Any]:
    observed={row["name"]:row["observation"] for row in probe_rows}
    if any(not isinstance(row.get("status"),int) for row in observed.values()):
        return {"pass":False,"reason":"runtime-error"}
    positive=[observed[name] for name in ("repo","branches","commits")]
    missing=[observed[name] for name in ("bad-repo","bad-ref")]
    shapes={observed["branches"]["semantic_shape"],observed["commits"]["semantic_shape"]}
    auth_status=int(observed["auth-user"]["status"])
    passed=(all(row["status"]==200 for row in positive) and all(row["status"]==404 for row in missing)
            and auth_status==401 and len(shapes)==1)
    return {"pass":passed,"missing_status":404,"auth_status":auth_status,"collection_shape":next(iter(shapes)) if len(shapes)==1 else None,
            "auth_recovery":_recovery(auth_status)}


def _predict_hidden(target:dict[str,Any],probe_rows:list[dict[str,Any]])->list[dict[str,Any]]:
    # Predictor sees only target probe outcomes plus public endpoint URL/role.
    # Hidden HTTP outcomes are fetched only after this prediction is hashed.
    contract=_probe_contract(probe_rows)
    if not contract["pass"]: raise RuntimeError("target probe contract did not qualify deterministic P/E/X")
    out=[]
    for name,url,endpoint_role in target["hidden"]:
        missing=("__agent_evolution_missing__" in url or "/999999999" in url)
        if endpoint_role=="auth-required":
            status,shape,recovery=int(contract["auth_status"]),"error","authenticate-required"
        elif missing:
            status,shape,recovery=404,"error","abort-not-found"
        else:
            status=200
            shape=contract["collection_shape"] if endpoint_role=="collection" else "object"
            recovery="none"
        out.append({"name":name,"predicted_status":status,"predicted_shape":shape,"predicted_recovery":recovery})
    return out

def _prediction_hash(predictions:dict[str,list[dict[str,Any]]])->str:
    raw=json.dumps(predictions,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


SOURCE_QUALITY=[
 ("repo","https://api.github.com/repos/octocat/Hello-World","object",200,"none"),
 ("branches","https://api.github.com/repos/octocat/Hello-World/branches?per_page=1","list",200,"none"),
 ("commits","https://api.github.com/repos/octocat/Hello-World/commits?per_page=1","list",200,"none"),
 ("bad-repo","https://api.github.com/repos/octocat/__agent_evolution_missing_20260811__","error",404,"abort-not-found"),
 ("bad-ref","https://api.github.com/repos/octocat/Hello-World/branches/__agent_evolution_missing__","error",404,"abort-not-found"),
]

def _source_quality()->dict[str,Any]:
    rows=[]
    for name,url,shape,status,recovery in SOURCE_QUALITY:
        obs=_get(url)
        actual_recovery=_recovery(int(obs["status"])) if isinstance(obs.get("status"),int) else "runtime-error"
        ok=(obs.get("status")==status and obs.get("semantic_shape")==shape and actual_recovery==recovery)
        rows.append({"name":name,"expected":{"status":status,"shape":shape,"recovery":recovery},"observation":obs,"pass":ok})
    return {"family":"github-source-quality","checks":len(rows),"passed":sum(row["pass"] for row in rows),"pass":all(row["pass"] for row in rows),"rows":rows}

def _score_predictions(predictions:list[dict[str,Any]],actual_rows:list[dict[str,Any]])->dict[str,Any]:
    actual={row["name"]:row for row in actual_rows}; correct=0; scored=[]
    for pred in predictions:
        obs=actual[pred["name"]]["observation"]
        truth={"status":obs.get("status"),"shape":obs.get("semantic_shape"),"recovery":_recovery(int(obs["status"])) if isinstance(obs.get("status"),int) else "runtime-error"}
        ok=(pred["predicted_status"]==truth["status"] and pred["predicted_shape"]==truth["shape"] and pred["predicted_recovery"]==truth["recovery"])
        correct+=int(ok); scored.append({"name":pred["name"],"prediction":pred,"truth":truth,"pass":ok})
    return {"total":len(scored),"correct":correct,"accuracy":correct/len(scored) if scored else 0.0,"rows":scored}

def build()->dict[str,Any]:
    source=_source_quality()
    if not source["pass"]:
        return {"schema_version":"1.0","generated_at":_now(),"idea_id":"bounded-probe-api-transition-operator","code":"E-3","decision":"HOLD_SOURCE_RULE_QUALITY","scientific_result_available":False,"source_rule_quality":source,"learned_arm_run":False}
    probes={}; contracts={}; predictions={}
    for family,target in TARGETS.items():
        rows=[{"name":probe[0],"observation":_get(probe[1])} for probe in target["probes"]]
        probes[family]=rows; contracts[family]=_probe_contract(rows)
        if not contracts[family]["pass"]:
            return {"schema_version":"1.0","generated_at":_now(),"idea_id":"bounded-probe-api-transition-operator","code":"E-3","decision":"HOLD_TARGET_PROBE_CONTRACT","scientific_result_available":False,"source_rule_quality":source,"probe_rows":probes,"probe_contracts":contracts,"learned_arm_run":False}
        predictions[family]=_predict_hidden(target,rows)
    frozen_hash=_prediction_hash(predictions)
    hidden={}; scores={}
    for family,target in TARGETS.items():
        rows=[{"name":name,"endpoint_role":role,"observation":_get(url)} for name,url,role in target["hidden"]]
        hidden[family]=rows; scores[family]=_score_predictions(predictions[family],rows)
    total=sum(row["total"] for row in scores.values()); correct=sum(row["correct"] for row in scores.values())
    ceiling=(total==12 and correct==12)
    return {"schema_version":"1.0","generated_at":_now(),"idea_id":"bounded-probe-api-transition-operator","code":"E-3","design":{"source_family":"github","target_families":list(TARGETS),"probes_per_target":6,"hidden_cases_per_target":6,"target_probe_budget":12,"hidden_outcomes_sealed_until_prediction_hash":True,"read_only_public_api_scope":True},"source_rule_quality":source,"probe_rows":probes,"probe_contracts":contracts,"deterministic_pex_predictions":predictions,"prediction_sha256_before_hidden":frozen_hash,"hidden_rows":hidden,"family_scores":scores,"metrics":{"logical_target_probes":12,"total_hidden":total,"correct_hidden":correct,"hidden_semantic_accuracy":correct/total if total else 0.0,"family_accuracy":{k:v["accuracy"] for k,v in scores.items()}},"deterministic_baseline_ceiling":ceiling,"learned_arm_run":False,"decision":"READ_ONLY_SUBSTRATE_REDUCIBLE" if ceiling else "P0_CONTINUE_LEARNED_ARM_REQUIRED","standalone_claim_stop_authorized":False,"scientific_result_available":True}

def write(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS,refresh:bool=False)->dict[str,Any]:
    if not refresh and json_path.exists():
        try: existing=json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError): existing={}
        if existing.get("scientific_result_available") and existing.get("decision") in {"READ_ONLY_SUBSTRATE_REDUCIBLE","P0_CONTINUE_LEARNED_ARM_REQUIRED"}:
            js_path.write_text("window.P0_E3_REAL_API = "+json.dumps(existing,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
            return existing
    state=build()
    if state.get("decision")=="READ_ONLY_SUBSTRATE_REDUCIBLE":
        state["interpretation"]="Deterministic P/E/X reaches a ceiling on two real read-only API families; skip a learned arm here. This does not stop full E-3 because state-changing E semantics remain untested."
        state["next_action"]="Move only to a stateful hidden-side-effect/recovery harness; if the matched deterministic P/E/X baseline also ties there, fire the standalone STOP rule."
    elif state.get("decision")=="P0_CONTINUE_LEARNED_ARM_REQUIRED":
        state["interpretation"]="Deterministic P/E/X is not at ceiling; a matched learned arm remains necessary."
        state["next_action"]="Run the cross-source learned P/E/X arm under the same target probe budget."
    json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_E3_REAL_API = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state

write_state=write


def main()->None:
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path); parser.add_argument("--refresh",action="store_true"); args=parser.parse_args()
    state=write(args.output or DEFAULT_JSON,DEFAULT_JS if args.output is None else args.output.with_suffix(".js"),refresh=args.refresh)
    print(json.dumps(state,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
