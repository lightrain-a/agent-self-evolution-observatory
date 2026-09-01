#!/usr/bin/env python3
"""Neutral transport-only qualification for Qwen397 full-source action output budget."""
from __future__ import annotations
import argparse, json, os, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from research_pipeline.c1_pacta_rb_qwen397 import AA_BASE_URL, atomic_bytes, atomic_json, canonical, sha256_file, sha256_text
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime import parse_action

MODEL="qwen3.5-397b-a17b"
SOURCE_OUTPUT_BUDGET=16384
FIRST_DECISION_BUDGET=512
FIXTURE_COUNT=6
PARENT_RESULT=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-source-budget-q0-20260901-v1/qualification-result.json")
PARENT_RESULT_SHA256="73ff4787bb7ece1286cb14bfce2e3380e2b3f5cb454838e46b7b32bfad56eb4e"
DEFAULT_ROOT=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-source-budget-q0-20260901-v2")

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def require_key():
    key=os.environ.get("AA_API_KEY","")
    if not key: raise RuntimeError("STOP_PROVIDER_CREDENTIAL_NOT_CONFIGURED")
    return key

def expected_command(fid:str,n:int)->str:
    payload="\n".join(f"{fid}_LINE_{i:04d}_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" for i in range(1,n+1))
    return f"cat <<'EOF' > /tmp/{fid}.txt\n{payload}\nEOF"

def fixtures()->list[dict[str,Any]]:
    rows=[]
    for h in (0,12,24):
        for n in (160,320):
            fid=f"qwen397_source_budget_v2_h{h}_l{n}"
            action=expected_command(fid,n)
            messages=[{"role":"system","content":"Transport qualification only. Return exactly one fenced bash code block containing the exact command requested by the user. Do not add prose, reasoning, alternatives, compression, loops, or substitutions."}]
            filler="SYNTHETIC_CONTEXT_"+("0123456789abcdef"*64)
            for i in range(h):
                messages.append({"role":"user","content":filler+f"_USER_{i}"})
                messages.append({"role":"assistant","content":f"ACK_{i}"})
            messages.append({"role":"user","content":"Return this command exactly, byte-for-byte inside one ```bash fence:\n\n"+action})
            rows.append({"fixture_id":fid,"history_pairs":h,"line_count":n,"expected_action":action,"expected_action_sha256":sha256_text(action),"messages":messages})
    assert len(rows)==FIXTURE_COUNT
    return rows

def call(key:str,root:Path,index:int,fx:dict[str,Any])->dict[str,Any]:
    packet={"model":MODEL,"messages":fx["messages"],"stream":False,"n":1,"max_completion_tokens":SOURCE_OUTPUT_BUDGET,"temperature":0.0,"enable_thinking":False,"enable_search":False}
    safe={"endpoint":AA_BASE_URL+"/chat/completions","method":"POST","body":packet,"authorization_material_persisted":False,"transport_attempt":1,"provider_retries":0}
    reqp=root/"raw"/f"request-{index:04d}.json";resp=root/"raw"/f"response-{index:04d}.json"
    reqsha=atomic_bytes(reqp,(canonical(safe)+"\n").encode())
    r=urllib.request.Request(AA_BASE_URL+"/chat/completions",data=canonical(packet).encode(),method="POST",headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
    status=None
    try:
        with urllib.request.urlopen(r,timeout=300) as x: status=int(x.status);raw=x.read()
    except urllib.error.HTTPError as e: status=int(e.code);raw=e.read()
    ressha=atomic_bytes(resp,raw)
    base={"fixture_id":fx["fixture_id"],"history_pairs":fx["history_pairs"],"line_count":fx["line_count"],"status_code":status,"request_sha256":reqsha,"response_sha256":ressha,"persisted_before_parse":True,"requested_model":MODEL,"max_completion_tokens":SOURCE_OUTPUT_BUDGET,"provider_retries":0}
    if status is None or not 200<=status<300:
        row={**base,"pass":False,"parse_status":"NOT_PARSED_HTTP_ERROR","failure":f"HTTP_{status}"};atomic_json(root/"calls"/f"{index:04d}.json",row);return row
    try:
        p=json.loads(raw.decode());choice=p["choices"][0];content=str(choice["message"]["content"]);action=parse_action(content);resolved=str(p.get("model") or "");finish=str(choice.get("finish_reason") or "");exact=action==fx["expected_action"]
        row={**base,"pass":resolved==MODEL and finish=="stop" and exact,"parse_status":"PARSED","resolved_model":resolved,"model_drift":resolved!=MODEL,"finish_reason":finish,"exact_action_match":exact,"action_sha256":sha256_text(action),"expected_action_sha256":fx["expected_action_sha256"],"action_chars":len(action),"usage":p.get("usage") if isinstance(p.get("usage"),dict) else {}}
    except Exception as e:
        row={**base,"pass":False,"parse_status":"PARSE_FAILED","failure":f"{type(e).__name__}: {e}"}
    atomic_json(root/"calls"/f"{index:04d}.json",row);return row

def run(root:Path)->dict[str,Any]:
    if root.exists(): raise RuntimeError(f"qualification root exists; no overwrite/retry: {root}")
    if sha256_file(PARENT_RESULT)!=PARENT_RESULT_SHA256: raise RuntimeError("parent Q0-v1 result hash drift")
    root.mkdir(parents=True)
    atomic_json(root/"contract.json",{"schema_version":1,"created_at_utc":now(),"experiment":"C1-PACTA-RB-QWEN397-SOURCE-BUDGET-Q0-v2-20260901","non_scientific":True,"model":MODEL,"source_trajectory_output_budget_candidate":SOURCE_OUTPUT_BUDGET,"pacta_first_decision_budget_unchanged":FIRST_DECISION_BUDGET,"fixture_count":FIXTURE_COUNT,"fixture_grid":{"history_pairs":[0,12,24],"payload_lines":[160,320]},"pass_rule":"6/6 HTTP success, persisted-before-parse, exact model, finish_reason=stop, exactly one fenced bash action, byte-exact expected action","provider_retries":0,"scientific_source_tasks_used":0,"v5_source_task_replayed":False,"writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0})
    key=require_key();rows=[]
    for i,fx in enumerate(fixtures(),1):
        row=call(key,root,i,fx);rows.append(row);print(json.dumps({"fixture":row["fixture_id"],"pass":row["pass"],"status":row["status_code"],"finish":row.get("finish_reason")}),flush=True)
        if i<FIXTURE_COUNT: time.sleep(3)
    passed=all(r.get("pass") for r in rows) and len(rows)==FIXTURE_COUNT
    result={"schema_version":1,"created_at_utc":now(),"decision":"SOURCE_TRAJECTORY_BUDGET_16384_QUALIFIED" if passed else "STOP_SOURCE_TRAJECTORY_BUDGET_16384_UNQUALIFIED","pass":passed,"source_trajectory_output_budget":SOURCE_OUTPUT_BUDGET if passed else None,"pacta_first_decision_budget":FIRST_DECISION_BUDGET,"qualified":sum(bool(r.get("pass")) for r in rows),"total":FIXTURE_COUNT,"provider_calls":len(rows),"prompt_tokens":sum(int((r.get("usage") or {}).get("prompt_tokens") or 0) for r in rows),"completion_tokens":sum(int((r.get("usage") or {}).get("completion_tokens") or 0) for r in rows),"rows":rows,"scientific_source_tasks_used":0,"v5_source_task_replayed":False,"writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0,"claim_authority":"NO_NEW_PACTA_EFFECT_EVIDENCE"}
    atomic_json(root/"qualification-result.json",result);return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=DEFAULT_ROOT);a=ap.parse_args();r=run(a.root);print(json.dumps({"decision":r["decision"],"qualified":r["qualified"],"total":r["total"]},sort_keys=True))
if __name__=="__main__":main()
