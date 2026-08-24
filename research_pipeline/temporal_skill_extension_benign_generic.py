from __future__ import annotations

import argparse, hashlib, json, os, sys, time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings
from research_pipeline.experiment_authority import acquire_authority, release_authority
from research_pipeline import temporal_skill_g0_execute as core

PAPER_ID = core.PAPER_ID
DATA_ROOT = core.DATA_ROOT
BASE_PLAN = ROOT / "generated" / "temporal-skill-g0-fresh-factorial-plan-20260824.json"
BASE_STAGE = ROOT / "generated" / "temporal-skill-g0-staged-execution-contract-20260824.json"
PLAN = ROOT / "generated" / "temporal-skill-extension-benign-generic-plan-20260824.json"
STAGE = ROOT / "generated" / "temporal-skill-extension-benign-generic-stage-20260824.json"
AUTH = ROOT / "generated" / "temporal-skill-extension-benign-generic-authorization-20260824.json"
OUT = DATA_ROOT / "paper-acceptance" / "source-native-replay" / PAPER_ID / "20260824-extension-benign-generic-deepseek" / "results.json"
OWNER = PAPER_ID + ":EXTENSION:BENIGN-GENERIC"
MODEL = "deepseek-v4-pro"
RESOLVED = "deepseek-v4-pro-260425"
BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"
ARMS = ("N_FRESH", "B_GENERIC", "T_FROZEN")

BENIGN_SOURCE = '''def skill(package, context):
    """Mechanism-agnostic evidence organizer.

    Preserve candidate order and expose all evidence without temporal filtering,
    release-period inference, or mechanism-specific grounding selection.
    """
    out = {"guidance": "Use all supplied evidence and verify task-specific constraints yourself."}
    if isinstance(package.get("candidate_spans"), list):
        out["evidence_inventory"] = [
            {"span_id": str(x.get("span_id", "")), "text": str(x.get("text", ""))[:180]}
            for x in package.get("candidate_spans", [])
        ]
    elif isinstance(package.get("release_records"), list):
        out["evidence_inventory"] = [
            {
                "evidence_ref": str(x.get("evidence_ref", "")),
                "release_date": str(x.get("release_date", "")),
                "document_spans": [
                    {"span_id": str(s.get("span_id", "")), "text": str(s.get("text", ""))[:160]}
                    for s in x.get("document_spans", [])
                ],
            }
            for x in package.get("release_records", [])
        ]
    elif package.get("document_text") is not None:
        out["document_excerpt"] = str(package.get("document_text", ""))[:1200]
    else:
        out["package_keys"] = sorted(str(k) for k in package.keys())
    return out
'''


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical_sha(v: Any) -> str:
    return sha_bytes(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def benign_output(package: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"guidance": "Use all supplied evidence and verify task-specific constraints yourself."}
    if isinstance(package.get("candidate_spans"), list):
        out["evidence_inventory"] = [
            {"span_id": str(x.get("span_id", "")), "text": str(x.get("text", ""))[:180]}
            for x in package.get("candidate_spans", [])
        ]
    elif isinstance(package.get("release_records"), list):
        out["evidence_inventory"] = [
            {
                "evidence_ref": str(x.get("evidence_ref", "")),
                "release_date": str(x.get("release_date", "")),
                "document_spans": [
                    {"span_id": str(s.get("span_id", "")), "text": str(s.get("text", ""))[:160]}
                    for s in x.get("document_spans", [])
                ],
            }
            for x in package.get("release_records", [])
        ]
    elif package.get("document_text") is not None:
        out["document_excerpt"] = str(package.get("document_text", ""))[:1200]
    else:
        out["package_keys"] = sorted(str(k) for k in package.keys())
    return out


def prepare() -> dict[str, Any]:
    base = read(BASE_PLAN)
    stage0 = read(BASE_STAGE)
    rows = []
    for r in base["rows"]:
        q = dict(r)
        if q["arm"] == "G0_NOOP":
            q["arm"] = "B_GENERIC"; q["condition_id"] = "BGEN"
        rows.append(q)
    body = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "experiment": "E2_EXTENSION_BENIGN_GENERIC",
        "purpose": "Triangulate R15 attribution audit with a benign mechanism-agnostic evidence organizer without changing the current R15 claim.",
        "arms": list(ARMS),
        "rows": rows,
        "model_identity": {"requested_model": MODEL, "required_resolved_model": RESOLVED, "required_plan_base_url": BASE_URL},
        "benign_generic": {
            "source": BENIGN_SOURCE,
            "source_sha256": sha_bytes(BENIGN_SOURCE.encode()),
            "mechanism_forbidden": ["temporal filtering", "release-period inference", "mechanism-specific grounding selection", "candidate reordering"],
            "allowed": ["preserve all evidence", "preserve original order", "copy/organize evidence fields", "generic verification reminder"],
        },
        "summary": {"independent_endpoints": 35, "repeats": 2, "planned_model_calls": len(rows), "calls_by_arm": {a: sum(r["arm"]==a for r in rows) for a in ARMS}},
        "decision_policy": {
            "pilot_promotion": "runtime/protocol/checkpoint integrity only",
            "scientific_interpretation": "B is a distinct future treatment. Compare T-N, T-B, and B-N; do not overwrite R15 current claim from pilot outcomes.",
            "appendix_candidate": "If B does not materially alter the R15 verdict and no new mechanism emerges, treat as appendix/robustness evidence.",
            "new_paper_candidate": "Only if B or later multi-turn work exposes a stable new mechanism not reducible to current surface/output contrasts.",
        },
    }
    body["plan_body_sha256"] = canonical_sha({k:v for k,v in body.items() if k != "plan_body_sha256"})
    pilot_keys = []
    for key in stage0["pilot"]["row_keys"]:
        pilot_keys.append(key.replace("|G0_NOOP", "|B_GENERIC"))
    stage = {
        "schema_version": "1.0", "paper_id": PAPER_ID, "experiment": body["experiment"], "bound_plan_body_sha256": body["plan_body_sha256"],
        "pilot": {"model_calls": len(pilot_keys), "row_keys": pilot_keys, "promotion_gate": "runtime/protocol/checkpoint integrity only", "scientific_outcomes_used_for_promotion": False},
        "full": {"model_calls": len(rows), "requires_pilot_runtime_pass": True},
    }
    stage["stage_contract_sha256"] = canonical_sha({k:v for k,v in stage.items() if k != "stage_contract_sha256"})
    auth = {
        "schema_version": "1.0", "paper_id": PAPER_ID, "experiment": body["experiment"],
        "status": "HUMAN_EXECUTION_AUTHORITY_RECORDED", "authorized_by": "explicit user directive in current conversation",
        "scientific_reopen_authorized": True, "execution_authorized": True, "provider_spend_authorized": True,
        "scope": ["BENIGN_GENERIC_PILOT", "FRESH_N_B_T_SAME_UNITS", "EXTENSION_EVIDENCE_ONLY"],
        "bound_plan_body_sha256": body["plan_body_sha256"], "bound_stage_contract_sha256": stage["stage_contract_sha256"],
        "bounded_budget": {"pilot_model_calls": len(pilot_keys), "full_model_calls_upper_bound": len(rows), "reruns_allowed": False, "resume_missing_only": True},
        "model_identity": body["model_identity"], "outcome_driven_selection_authorized": False,
        "current_r15_contract_may_be_mutated_automatically": False,
    }
    auth["authorization_sha256"] = canonical_sha({k:v for k,v in auth.items() if k != "authorization_sha256"})
    core.atomic_json(PLAN, body); core.atomic_json(STAGE, stage); core.atomic_json(AUTH, auth)
    return {"plan": str(PLAN), "stage": str(STAGE), "auth": str(AUTH), "plan_sha": body["plan_body_sha256"], "pilot_calls": len(pilot_keys), "full_calls": len(rows)}


def helper_output(assets: dict[str, Any], endpoint: dict[str, Any], arm: str):
    if arm == "N_FRESH": return None, None
    if arm == "B_GENERIC": return benign_output(endpoint["package"], endpoint.get("skill_context") or {}), sha_bytes(BENIGN_SOURCE.encode())
    eid=str(endpoint["endpoint_id"]); source=assets["source"][eid]; family=str(endpoint["failure_family"])
    module=assets["targeted_modules"][(source,family)]
    return module.skill(endpoint["package"],endpoint.get("skill_context") or {}), assets["hashes"]["targeted"][f"{source}:{family}"]


def run_one(client, assets, row):
    endpoint=assets["endpoints"][str(row["endpoint_id"])]
    helper,hsha=helper_output(assets,endpoint,row["arm"]); prompt=core.render_prompt(assets,endpoint,helper)
    base={**row,"helper_output":helper,"helper_source_sha256":hsha,"prompt_sha256":sha_bytes(prompt.encode()),"runtime_valid":False,"family_success":False,"generation_post_attempts":1,"get_recovery_attempts":0}
    started=time.time()
    try:
        response=client.respond(prompt,model=row["requested_model"],max_output_tokens=core.MAX_OUTPUT_TOKENS,temperature=0,thinking="disabled",allow_thinking_compatibility_fallback=False); text=str(response.get("text") or ""); recovered=False
    except ArkResponseStateError as exc:
        if not exc.response_id: return {**base,"failure_kind":"provider-response-state-no-id","error":str(exc),"runtime_seconds":round(time.time()-started,3)}
        polled=client.poll_response(exc.response_id,max_polls=core.POLL_MAX,interval_seconds=core.POLL_INTERVAL_SECONDS); text=str(polled.get("text") or ""); recovered=True
        response={"response_id":polled.get("response_id") or exc.response_id,"status":polled.get("status"),"resolved_model":polled.get("resolved_model") or exc.resolved_model,"usage":polled.get("usage") or {}}
        base["get_recovery_attempts"]=int(polled.get("poll_count") or 0)
        if not text: return {**base,"resolved_model":str(response.get("resolved_model") or ""),"failure_kind":"provider-get-recovery-no-text","error":str(exc),"runtime_seconds":round(time.time()-started,3)}
    except Exception as exc:
        return {**base,"failure_kind":"provider-post-failure","error_type":type(exc).__name__,"error":str(exc)[:1200],"runtime_seconds":round(time.time()-started,3)}
    common={**base,"resolved_model":str(response.get("resolved_model") or ""),"provider_response_id_sha256":sha_bytes(str(response.get("response_id") or "").encode()),"provider_status":response.get("status"),"usage":response.get("usage") or {},"raw_text":text,"raw_text_sha256":sha_bytes(text.encode()),"get_recovered":recovered,"runtime_seconds":round(time.time()-started,3)}
    if common["resolved_model"] != row["required_resolved_model"]: return {**common,"failure_kind":"resolved-model-drift"}
    try: pred,score=core.parse_and_score(assets,endpoint,text)
    except Exception as exc: return {**common,"failure_kind":"protocol-parse-or-score-failure","error_type":type(exc).__name__,"error":str(exc)[:1200]}
    return {**common,"prediction":pred,"family_score":score,"family_success":bool(score["success"]),"runtime_valid":True}


def execute(stage_name: str):
    plan=read(PLAN); stage=read(STAGE); auth=read(AUTH)
    if auth.get("bound_plan_body_sha256") != plan.get("plan_body_sha256") or auth.get("bound_stage_contract_sha256") != stage.get("stage_contract_sha256"): raise RuntimeError("authorization binding mismatch")
    assets=core.load_assets(); core.recover_orphan_raw(OUT,plan)
    existing=core.load_csv_rows(OUT.parent/"results.csv")
    bad=[k for k,r in existing.items() if r.get("runtime_valid")!="True"]
    if bad: raise RuntimeError("runtime-invalid checkpoint requires adjudication: "+bad[0])
    target=set(stage["pilot"]["row_keys"]) if stage_name=="pilot" else {core.row_key(r) for r in plan["rows"]}
    if stage_name=="full":
        gp=OUT.parent/"pilot-gate.json"
        if not gp.exists() or not read(gp).get("pass"): raise RuntimeError("pilot runtime gate not passed")
    raw=ArkSettings.from_env(required=True)
    if raw.base_url.rstrip("/") != BASE_URL: raise RuntimeError("refuse non-Plan billing route")
    client=ArkResponsesClient(ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=180,max_retries=0))
    authority=acquire_authority(DATA_ROOT,OWNER,plan["plan_body_sha256"],"temporal-extension-benign-generic",stage_name,"E2-BENIGN-GENERIC-"+stage_name.upper()+"-20260824")
    outcome="runner-exception"
    try:
        core.checkpoint_progress(OUT,plan,stage_name,"running")
        idx={core.row_key(r):i for i,r in enumerate(plan["rows"])}
        for r in plan["rows"]:
            k=core.row_key(r)
            if k not in target or k in core.load_csv_rows(OUT.parent/"results.csv"): continue
            row=run_one(client,assets,r); core.persist_checkpoint(OUT,row,idx[k]); core.checkpoint_progress(OUT,plan,stage_name,"running",f"last={k}")
            if not row.get("runtime_valid"):
                outcome=str(row.get("failure_kind") or "runtime-invalid"); core.checkpoint_progress(OUT,plan,stage_name,"stopped",outcome); return {"status":"stopped","reason":outcome,"unit_key":k}
        if stage_name=="pilot":
            rows=core.load_csv_rows(OUT.parent/"results.csv"); req=stage["pilot"]["row_keys"]
            missing=[k for k in req if k not in rows]; invalid=[k for k in req if k in rows and rows[k].get("runtime_valid")!="True"]; drift=[k for k in req if k in rows and rows[k].get("resolved_model")!=RESOLVED]; raw_missing=[k for k in req if k in rows and not Path(rows[k].get("raw_receipt_path") or "").exists()]
            gate={"schema_version":"1.0","gate":"E2-BENIGN-GENERIC-PILOT-RUNTIME","pass":not(missing or invalid or drift or raw_missing),"pilot_calls":len(req),"missing":missing,"runtime_invalid":invalid,"model_drift":drift,"raw_missing":raw_missing,"scientific_outcomes_inspected_for_promotion":False}
            core.atomic_json(OUT.parent/"pilot-gate.json",gate); outcome="pilot-pass" if gate["pass"] else "pilot-fail"; core.checkpoint_progress(OUT,plan,stage_name,outcome); return {"status":outcome,"pilot_gate":gate}
        final=core.rebuild_results_json(OUT,plan,{"receipt_body_sha256":"extension-benign-generic"},{"authorization_sha256":auth["authorization_sha256"]},assets); outcome="completed" if final["scientific_result_available"] else "partial"; core.checkpoint_progress(OUT,plan,stage_name,outcome); return {"status":outcome,"rows":final["rows_total"]}
    finally:
        release_authority(DATA_ROOT,OWNER,str(authority["authority_id"]),outcome)


def summarize_pilot():
    plan=read(PLAN); rows=core.load_csv_rows(OUT.parent/"results.csv"); req=STAGE and read(STAGE)["pilot"]["row_keys"]
    by={}
    for k in req:
        r=rows[k]; by.setdefault(r["endpoint_id"],{})[r["arm"]]=1.0 if r["family_success"]=="True" else 0.0
    return {"endpoints":by,"contrasts":{e:{"T-N":a["T_FROZEN"]-a["N_FRESH"],"T-B":a["T_FROZEN"]-a["B_GENERIC"],"B-N":a["B_GENERIC"]-a["N_FRESH"]} for e,a in by.items()}}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("cmd",choices=["prepare","pilot","full","summary"]); a=ap.parse_args()
    if a.cmd=="prepare": print(json.dumps(prepare(),indent=2))
    elif a.cmd=="summary": print(json.dumps(summarize_pilot(),indent=2))
    else: print(json.dumps(execute(a.cmd),indent=2))

if __name__=="__main__": main()
