from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import replace
from pathlib import Path
from typing import Any

from .api_research_memory import (
    record_archived_api_parse_failure,
    record_parsed_api_output,
    record_provider_failure,
    record_raw_api_output,
)
from .ark_provider import ArkResponsesClient, ArkSettings
from .p15_order_effect_harness import (
    CANDIDATE_ID,
    CONTRACT_SHA256,
    EXECUTOR_MODEL,
    HARNESS_PLAN_SHA256,
    all_units,
    evaluate_solution,
    offline_probe,
    sha_json,
    solution_tool,
    validate_solution_ast,
)
from .paper_first_evidence_acquisition import (
    compile_harness_runtime_repair_receipts,
    validate_evidence_plan,
)

PROTOCOL_VERSION = "P15_RUNTIME_PROTOCOL_V2"
REPAIR_PLAN_FILENAME = "runtime-repair-plan-v2.json"
OFFLINE_PROBE_FILENAME = "offline-probe-v2.json"
TRANSPORT_PROBE_FILENAME = "transport-probe-v2.json"
HARNESS_MANIFEST_FILENAME = "harness-manifest-v2.json"
REPAIR_RECEIPT_FILENAME = "runtime-repair-receipt-v2.json"
AUTHORIZATION_FILENAME = "authorization-repaired-plan-v2.json"
OLD_FAILURE_FILENAME = "runtime-failure-manifest-v1.json"
OLD_REVOKED_FILENAME = "authorization-revoked-plan-v1.json"
OLD_HARNESS_FILENAME = "harness-manifest.json"
MAX_REPAIR_PROVIDER_CALLS = 43


def load_json(path: Path) -> dict[str, Any]:
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path,payload: dict[str,Any]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def sha_bytes(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def sha_text(text: str) -> str: return hashlib.sha256(text.encode()).hexdigest()


def lock_output(output: Path,payload: dict[str,Any]) -> Path:
    if output.exists(): raise RuntimeError(f"OUTPUT_ALREADY_EXISTS:{output}")
    lock=Path(str(output)+".lock");lock.parent.mkdir(parents=True,exist_ok=True)
    try: fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError as error: raise RuntimeError(f"STAGE_ALREADY_RUNNING_OR_STALE_LOCK:{lock}") from error
    with os.fdopen(fd,"w",encoding="utf-8") as handle:
        handle.write(json.dumps(payload,ensure_ascii=False,indent=2)+"\n");handle.flush();os.fsync(handle.fileno())
    return lock


def client() -> ArkResponsesClient:
    base=ArkSettings.from_env()
    return ArkResponsesClient(replace(base,max_retries=0,timeout_seconds=max(180.0,base.timeout_seconds)))


def provider_archive_payload(response: dict[str,Any]) -> dict[str,Any]:
    return {
        "protocol_version":PROTOCOL_VERSION,
        "requested_model":str(response.get("requested_model") or EXECUTOR_MODEL),
        "resolved_model":str(response.get("resolved_model") or EXECUTOR_MODEL),
        "response_id":str(response.get("response_id") or ""),
        "status":str(response.get("status") or ""),
        "text":str(response.get("text") or ""),
        "function_calls":list(response.get("function_calls") or []),
        "usage":dict(response.get("usage") or {}),
        "scientific_authority":False,
        "belief_authority":False,
    }


def extract_solution_code(archive: dict[str,Any]) -> tuple[str,str]:
    calls=[row for row in archive.get("function_calls") or [] if isinstance(row,dict) and row.get("name")=="submit_solution"]
    if len(calls)==1:
        args=json.loads(str(calls[0].get("arguments") or "{}"));code=str(args.get("python_code") or "").strip()
        if not code: raise ValueError("submit_solution contains empty python_code")
        return code,"FUNCTION_CALL"
    if len(calls)>1: raise ValueError("multiple submit_solution function calls")
    text=str(archive.get("text") or "").strip()
    if not text: raise ValueError("no submit_solution function call and no assistant text")
    blocks=re.findall(r"```(?:python)?\s*\n?(.*?)```",text,flags=re.I|re.S)
    if blocks:
        if len(blocks)!=1: raise ValueError("text fallback requires exactly one fenced code block")
        rest=re.sub(r"```(?:python)?\s*\n?.*?```","",text,count=1,flags=re.I|re.S).strip()
        if rest: raise ValueError("text fallback forbids prose outside fenced code")
        code=blocks[0].strip()
    else: code=text
    if validate_solution_ast(code).get("valid") is not True: raise ValueError("text fallback is not a valid frozen solve(records) program")
    return code,"TEXT_FALLBACK"


def build_repair_plan(study: Path) -> dict[str,Any]:
    failure=load_json(study/OLD_FAILURE_FILENAME);old_manifest=load_json(study/OLD_HARNESS_FILENAME)
    retry=sorted(str(row.get("unit_id") or "") for row in failure.get("protocol_failures") or [])
    old_units={p.stem for p in (study/"units").glob("*.json")};all_ids=[row["unit_id"] for row in all_units()]
    unstarted=sorted(set(all_ids)-old_units)
    if retry!=["T1-NO-SKILL","T1-PERM-4","T1-PERM-5"]: raise RuntimeError(f"unexpected protocol-failure set:{retry}")
    if len(unstarted)!=40: raise RuntimeError(f"unexpected unstarted-unit count:{len(unstarted)}")
    core={
        "schema_version":"1.0","status":"P15_RUNTIME_REPAIR_PLAN_V2","candidate_id":CANDIDATE_ID,
        "contract_sha256":CONTRACT_SHA256,"scientific_harness_plan_sha256":HARNESS_PLAN_SHA256,
        "failure_manifest_sha256":failure["failure_manifest_sha256"],"replaces_harness_manifest_sha256":old_manifest["harness_manifest_sha256"],
        "protocol_version":PROTOCOL_VERSION,"scientific_object_unchanged":True,"protocol_only_change":True,
        "frozen_executor":{"model":EXECUTOR_MODEL,"temperature":0.0,"prompt":"v1-unchanged","skills":"v1-unchanged","tasks":"v1-unchanged"},
        "archive_before_parse":["text","function_calls","response_id","usage","resolved_model","status"],
        "code_extraction_order":["exactly-one-submit_solution","strict-valid-code-text-fallback"],
        "retry_units":retry,"max_protocol_retries_per_old_failed_unit":1,"unstarted_units":unstarted,
        "replacement_provider_call_cap":len(retry)+len(unstarted),"provider_calls_already_charged":int(failure["provider_calls_charged"]),
        "remaining_model_call_budget_before_repair":int(failure["remaining_model_call_budget"]),
        "no_outcome_conditioning":True,"existing_successful_unit_receipts_are_reused":True,
        "scientific_authority":False,"belief_authority":False,
    }
    if core["replacement_provider_call_cap"]!=MAX_REPAIR_PROVIDER_CALLS: raise RuntimeError("replacement provider-call cap drift")
    core["replacement_harness_plan_sha256"]=sha_json(core);return core


def run_offline_probe(study: Path) -> dict[str,Any]:
    output=study/OFFLINE_PROBE_FILENAME;lock=lock_output(output,{"stage":"offline-probe-v2"})
    try:
        repair=build_repair_plan(study)
        func={"function_calls":[{"name":"submit_solution","arguments":json.dumps({"python_code":"def solve(records):\n    return records\n"})}],"text":""}
        raw={"function_calls":[],"text":"def solve(records):\n    return records\n"}
        fenced={"function_calls":[],"text":"```python\ndef solve(records):\n    return records\n```"}
        checks={"function_call_extract":extract_solution_code(func)[1]=="FUNCTION_CALL","raw_text_fallback":extract_solution_code(raw)[1]=="TEXT_FALLBACK","fenced_text_fallback":extract_solution_code(fenced)[1]=="TEXT_FALLBACK","base_harness_still_passes":offline_probe().get("status")=="P15_OFFLINE_HARNESS_PROBE_PASS","replacement_call_cap_43":repair["replacement_provider_call_cap"]==43}
        try: extract_solution_code({"function_calls":[],"text":"Here is code:\ndef solve(records):\n    return records"});checks["prose_rejected"]=False
        except ValueError: checks["prose_rejected"]=True
        result={"schema_version":"1.0","status":"P15_RUNTIME_REPAIR_OFFLINE_PROBE_PASS" if all(checks.values()) else "P15_RUNTIME_REPAIR_OFFLINE_PROBE_FAIL","replacement_harness_plan_sha256":repair["replacement_harness_plan_sha256"],"checks":checks,"scientific_authority":False,"belief_authority":False}
        result["offline_probe_sha256"]=sha_json(result);write_json(study/REPAIR_PLAN_FILENAME,repair);write_json(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def run_transport_probe(study: Path,persistent_root: Path) -> dict[str,Any]:
    output=study/TRANSPORT_PROBE_FILENAME;lock=lock_output(output,{"stage":"transport-probe-v2"});repair=load_json(study/REPAIR_PLAN_FILENAME)
    run_id=f"p15-order-v2-transport-{repair['replacement_harness_plan_sha256'][:12]}"
    try:
        prompt="Neutral P15 v2 transport probe. Call submit_solution exactly once with python_code='def solve(records):\\n    return records'. No scientific task or candidate evidence is present."
        prompt_sha=sha_text(prompt);run_root=persistent_root/"runs"/run_id;run_root.mkdir(parents=True,exist_ok=True)
        try: response=client().respond(prompt,model=EXECUTOR_MODEL,max_output_tokens=500,temperature=0.0,tools=solution_tool(),thinking="disabled",store=True)
        except Exception as error:
            fp=sha_json({"stage":"p15-v2-transport","error":str(error)[:500],"prompt_sha256":prompt_sha});receipt=record_provider_failure(run_root=run_root,stage="p15-order-v2-transport-probe",payload={"status":"PROVIDER_ERROR_ZERO_AUTHORITY","requested_model":EXECUTOR_MODEL,"error_fingerprint":fp,"prompt_sha256":prompt_sha},root=persistent_root)
            result={"schema_version":"1.0","status":"P15_RUNTIME_REPAIR_TRANSPORT_PROBE_FAIL","provider_failure":receipt,"error":f"{type(error).__name__}:{str(error)[:1000]}","scientific_authority":False,"belief_authority":False};write_json(output,result);return result
        archive=provider_archive_payload(response);raw_file=run_root/"raw-transport-v2.json";raw_file.write_text(json.dumps(archive,ensure_ascii=False,sort_keys=True,separators=(",",":")),encoding="utf-8")
        archived=record_raw_api_output(run_root=run_root,stage="p15-order-v2-transport-probe",raw_path=raw_file,requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],request_fingerprint=sha_json({"stage":"p15-v2-transport","prompt_sha256":prompt_sha}),prompt_sha256=prompt_sha,root=persistent_root)
        try: code,source=extract_solution_code(archive)
        except Exception as error:
            record_archived_api_parse_failure(run_root=run_root,stage="p15-order-v2-transport-probe",raw_sha256=archived["raw_sha256"],error=f"{type(error).__name__}:{error}",requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],root=persistent_root)
            result={"schema_version":"1.0","status":"P15_RUNTIME_REPAIR_TRANSPORT_PROBE_FAIL","raw_sha256":archived["raw_sha256"],"error":f"{type(error).__name__}:{error}","scientific_authority":False,"belief_authority":False};write_json(output,result);return result
        local=evaluate_solution("T1","def solve(records):\n    return records\n")
        result={"schema_version":"1.0","status":"P15_RUNTIME_REPAIR_TRANSPORT_PROBE_PASS","raw_sha256":archived["raw_sha256"],"response_id_archived":bool(archive["response_id"]),"assistant_text_archived":True,"function_calls_archived":True,"usage_archived":bool(archive["usage"]),"code_source":source,"code_received":bool(code),"local_evaluator_callable":local.get("valid_execution") is True,"scientific_authority":False,"belief_authority":False}
        result["transport_probe_sha256"]=sha_json(result);record_parsed_api_output(run_root=run_root,stage="p15-order-v2-transport-probe",raw_sha256=archived["raw_sha256"],structured_payload=result,requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],research_objects=[],root=persistent_root);write_json(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def authorize_repair(study: Path) -> dict[str,Any]:
    output=study/AUTHORIZATION_FILENAME;lock=lock_output(output,{"stage":"authorize-repair-v2"})
    try:
        revoked=load_json(study/OLD_REVOKED_FILENAME);failure=load_json(study/OLD_FAILURE_FILENAME);old=load_json(study/OLD_HARNESS_FILENAME);repair=load_json(study/REPAIR_PLAN_FILENAME);offline=load_json(study/OFFLINE_PROBE_FILENAME);transport=load_json(study/TRANSPORT_PROBE_FILENAME)
        if offline.get("status")!="P15_RUNTIME_REPAIR_OFFLINE_PROBE_PASS" or transport.get("status")!="P15_RUNTIME_REPAIR_TRANSPORT_PROBE_PASS": raise RuntimeError("P15 v2 repair probes not PASS")
        harness_path=Path(__file__).with_name("p15_order_effect_harness.py")
        manifest={"schema_version":"1.0","status":"P15_RUNTIME_REPAIR_HARNESS_PASS","candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"scientific_harness_plan_sha256":HARNESS_PLAN_SHA256,"replacement_harness_plan_sha256":repair["replacement_harness_plan_sha256"],"failure_manifest_sha256":failure["failure_manifest_sha256"],"replaces_harness_manifest_sha256":old["harness_manifest_sha256"],"code_sha256":{"p15_order_effect_harness.py":sha_bytes(harness_path.read_bytes()),"p15_order_effect_protocol_v2.py":sha_bytes(Path(__file__).read_bytes()),"p15_order_effect_execute_v2.py":sha_bytes(Path(__file__).with_name("p15_order_effect_execute_v2.py").read_bytes())},"offline_probe_sha256":offline["offline_probe_sha256"],"transport_probe_sha256":transport["transport_probe_sha256"],"replacement_provider_call_cap":repair["replacement_provider_call_cap"],"sandboxed":True,"probe_passed":True,"budget_feasible":repair["replacement_provider_call_cap"]<=failure["remaining_model_call_budget"],"scientific_object_unchanged":True,"protocol_only_change":True,"scientific_authority":False,"belief_authority":False}
        manifest["harness_manifest_sha256"]=sha_json(manifest);write_json(study/HARNESS_MANIFEST_FILENAME,manifest)
        receipt={"schema_version":"1.0","scientific_authority":False,"receipts":[{"candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"failure_manifest_sha256":failure["failure_manifest_sha256"],"replaces_harness_manifest_sha256":old["harness_manifest_sha256"],"replacement_harness_plan_sha256":repair["replacement_harness_plan_sha256"],"harness_manifest_sha256":manifest["harness_manifest_sha256"],"implementation_summary":"Protocol-only P15 v2: frozen tasks/skills/prompts/model/temperature unchanged; archive assistant text + function calls + response_id + usage before parse; deterministic valid-code text fallback; reuse seven valid v1 receipts; retry only three preregistered v1 protocol failures once; then execute forty never-started units.","sandboxed":True,"probe_passed":True,"budget_feasible":True,"scientific_object_unchanged":True,"protocol_only_change":True,"replacement_provider_call_cap":repair["replacement_provider_call_cap"]}]}
        write_json(study/REPAIR_RECEIPT_FILENAME,receipt);compiled=compile_harness_runtime_repair_receipts(revoked,receipt);errors=validate_evidence_plan(compiled)
        if errors: raise ValueError(f"P15 repaired authorization invalid:{errors}")
        entry=next(row for row in compiled["entries"] if row.get("candidate_id")==CANDIDATE_ID)
        if entry.get("status")!="READY_FOR_BOUNDED_EVIDENCE_ACQUISITION" or entry.get("execution_authorized") is not True: raise RuntimeError("P15 v2 bounded evidence not authorized")
        write_json(output,compiled);return {"status":"P15_RUNTIME_REPAIR_AUTHORIZED","harness_manifest_sha256":manifest["harness_manifest_sha256"],"replacement_harness_plan_sha256":repair["replacement_harness_plan_sha256"],"replacement_provider_call_cap":repair["replacement_provider_call_cap"],"execution_authorized":True,"scientific_authority":False}
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def authorization_ok(study: Path) -> tuple[dict[str,Any],dict[str,Any]]:
    plan=load_json(study/AUTHORIZATION_FILENAME);manifest=load_json(study/HARNESS_MANIFEST_FILENAME);entry=next((row for row in plan.get("entries") or [] if row.get("candidate_id")==CANDIDATE_ID),None)
    if not entry or entry.get("status")!="READY_FOR_BOUNDED_EVIDENCE_ACQUISITION" or entry.get("execution_authorized") is not True: raise RuntimeError("P15 v2 bounded evidence is not authorized")
    if str((entry.get("harness_implementation") or {}).get("harness_manifest_sha256") or "")!=manifest["harness_manifest_sha256"]: raise RuntimeError("P15 v2 repaired harness digest mismatch")
    return plan,manifest
