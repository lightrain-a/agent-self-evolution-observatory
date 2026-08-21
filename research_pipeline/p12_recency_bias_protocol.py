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
from .p12_recency_bias_harness import (
    CANDIDATE_ID,
    CONTRACT_SHA256,
    EXECUTOR_MODEL,
    HARNESS_PLAN_SHA256,
    PROVIDER_CALL_CAP,
    answer_tool,
    canonical_json,
    offline_probe,
    sha_json,
    sha_text,
)
from .paper_first_evidence_acquisition import (
    compile_harness_implementation_receipts,
    validate_evidence_plan,
)

PROTOCOL_VERSION = "P12_RECENCY_RUNTIME_V1"
TRANSPORT_PROBE_FILENAME = "transport-probe.json"
IMPLEMENTATION_MANIFEST_FILENAME = "harness-implementation-manifest.json"
IMPLEMENTATION_RECEIPT_FILENAME = "harness-implementation-receipt.json"
AUTHORIZATION_FILENAME = "authorization-plan.json"
REVOKED_AUTHORIZATION_FILENAME = "authorization-revoked-plan-v1.json"
REPAIRED_AUTHORIZATION_FILENAME = "authorization-repaired-plan-v2.json"
REPAIRED_IMPLEMENTATION_MANIFEST_FILENAME = "harness-implementation-manifest-v2.json"


def load_json(path: Path) -> dict[str, Any]:
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path,payload: dict[str,Any]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def sha_bytes(data: bytes) -> str: return hashlib.sha256(data).hexdigest()


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


def _function_args(archive: dict[str,Any],name: str) -> dict[str,Any] | None:
    calls=[row for row in archive.get("function_calls") or [] if isinstance(row,dict) and row.get("name")==name]
    if len(calls)>1: raise ValueError(f"multiple {name} calls")
    if not calls: return None
    value=json.loads(str(calls[0].get("arguments") or "{}"))
    if not isinstance(value,dict): raise ValueError(f"{name} arguments are not an object")
    return value


def parse_single_integer(archive: dict[str,Any],function_name: str="submit_p12_answer") -> tuple[int,str]:
    args=_function_args(archive,function_name)
    if args is not None:
        value=args.get("answer")
        if not isinstance(value,int): raise ValueError(f"{function_name} answer is not integer")
        return value,"FUNCTION_CALL"
    text=str(archive.get("text") or "").strip()
    if not text: raise ValueError("no answer function call and no assistant text")
    try:
        payload=json.loads(text)
        if isinstance(payload,dict) and isinstance(payload.get("answer"),int): return int(payload["answer"]),"JSON_TEXT_FALLBACK"
    except json.JSONDecodeError: pass
    if re.fullmatch(r"[-+]?\d+",text): return int(text),"INTEGER_TEXT_FALLBACK"
    raise ValueError("answer text fallback must be exact integer or JSON object with integer answer")


def parse_difficulty_answers(archive: dict[str,Any]) -> tuple[dict[str,int],str]:
    args=_function_args(archive,"submit_p12_difficulty_answers")
    if args is not None:
        if not isinstance(args.get("backward_answer"),int) or not isinstance(args.get("forward_answer"),int): raise ValueError("difficulty answers must be integers")
        return {"backward_answer":int(args["backward_answer"]),"forward_answer":int(args["forward_answer"])},"FUNCTION_CALL"
    text=str(archive.get("text") or "").strip()
    try: payload=json.loads(text)
    except json.JSONDecodeError as error: raise ValueError("difficulty fallback requires exact JSON") from error
    if not isinstance(payload,dict) or not isinstance(payload.get("backward_answer"),int) or not isinstance(payload.get("forward_answer"),int): raise ValueError("difficulty fallback JSON invalid")
    return {"backward_answer":int(payload["backward_answer"]),"forward_answer":int(payload["forward_answer"])},"JSON_TEXT_FALLBACK"


def parse_skills(archive: dict[str,Any]) -> tuple[dict[str,str],str]:
    args=_function_args(archive,"submit_p12_skills")
    source="FUNCTION_CALL"
    if args is None:
        text=str(archive.get("text") or "").strip()
        try: args=json.loads(text);source="JSON_TEXT_FALLBACK"
        except json.JSONDecodeError as error: raise ValueError("skill fallback requires exact JSON") from error
    if not isinstance(args,dict): raise ValueError("skill payload invalid")
    older=" ".join(str(args.get("older_skill_text") or "").split());newer=" ".join(str(args.get("newer_skill_text") or "").split())
    if not older or not newer or len(older)>700 or len(newer)>700: raise ValueError("skill text missing or too long")
    if older==newer: raise ValueError("two calibration-derived skills must not be byte-identical")
    return {"older_skill_text":older,"newer_skill_text":newer},source


def run_transport_probe(*,run_root: Path,persistent_root: Path) -> dict[str,Any]:
    output=run_root/TRANSPORT_PROBE_FILENAME;lock=lock_output(output,{"stage":"p12-transport-probe"})
    try:
        prompt="Neutral P12 transport probe. Return integer 7 only through submit_p12_answer. No scientific task, candidate evidence, skill, phase, or retrieval condition is present."
        psha=sha_text(prompt);provider_root=persistent_root/"runs"/f"p12-neutral-transport-{sha_text(PROTOCOL_VERSION)[:10]}";provider_root.mkdir(parents=True,exist_ok=True)
        try: response=client().respond(prompt,model=EXECUTOR_MODEL,max_output_tokens=300,temperature=0.0,tools=answer_tool(),thinking="disabled",store=True)
        except Exception as error:
            fp=sha_json({"stage":"p12-transport","error":str(error)[:500],"prompt_sha256":psha});receipt=record_provider_failure(run_root=provider_root,stage="p12-recency-transport-probe",payload={"status":"PROVIDER_ERROR_ZERO_AUTHORITY","requested_model":EXECUTOR_MODEL,"error_fingerprint":fp,"prompt_sha256":psha},root=persistent_root);result={"status":"P12_TRANSPORT_PROBE_FAIL","provider_failure":receipt,"error":f"{type(error).__name__}:{str(error)[:1000]}","scientific_authority":False,"belief_authority":False};write_json(output,result);return result
        archive=provider_archive_payload(response);raw_file=provider_root/"raw-transport.json";raw_file.write_text(canonical_json(archive),encoding="utf-8");arch=record_raw_api_output(run_root=provider_root,stage="p12-recency-transport-probe",raw_path=raw_file,requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],request_fingerprint=sha_json({"stage":"p12-transport","prompt_sha256":psha}),prompt_sha256=psha,root=persistent_root)
        try: answer,source=parse_single_integer(archive)
        except Exception as error:
            record_archived_api_parse_failure(run_root=provider_root,stage="p12-recency-transport-probe",raw_sha256=arch["raw_sha256"],error=f"{type(error).__name__}:{error}",requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],root=persistent_root);result={"status":"P12_TRANSPORT_PROBE_FAIL","raw_sha256":arch["raw_sha256"],"error":f"{type(error).__name__}:{error}","scientific_authority":False,"belief_authority":False};write_json(output,result);return result
        result={"schema_version":"1.0","status":"P12_TRANSPORT_PROBE_PASS" if answer==7 else "P12_TRANSPORT_PROBE_FAIL","answer":answer,"answer_source":source,"raw_sha256":arch["raw_sha256"],"response_id_archived":bool(archive["response_id"]),"assistant_text_archived":True,"function_calls_archived":True,"usage_archived":bool(archive["usage"]),"scientific_authority":False,"belief_authority":False};result["transport_probe_sha256"]=sha_json(result);record_parsed_api_output(run_root=provider_root,stage="p12-recency-transport-probe",raw_sha256=arch["raw_sha256"],structured_payload=result,requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],research_objects=[],root=persistent_root);write_json(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def authorize_implementation(*,run_root: Path,persistent_root: Path,evidence_plan_path: Path) -> dict[str,Any]:
    output=run_root/AUTHORIZATION_FILENAME;lock=lock_output(output,{"stage":"p12-authorize-implementation"})
    try:
        offline=load_json(run_root/"offline-probe.json");review=load_json(run_root/"analysis-protocol-review.json");transport=load_json(run_root/TRANSPORT_PROBE_FILENAME);plan=load_json(evidence_plan_path)
        if offline.get("status")!="P12_OFFLINE_HARNESS_PROBE_PASS" or review.get("review",{}).get("verdict")!="CLEAR_FOR_HARNESS_IMPLEMENTATION" or transport.get("status")!="P12_TRANSPORT_PROBE_PASS": raise RuntimeError("P12 implementation gates not CLEAR")
        files=("p12_recency_bias_harness.py","p12_recency_bias_protocol.py","p12_recency_bias_execute.py")
        code={name:sha_bytes(Path(__file__).with_name(name).read_bytes()) for name in files}
        manifest={"schema_version":"1.0","status":"P12_HARNESS_IMPLEMENTATION_PROBE_PASS","candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"harness_plan_sha256":HARNESS_PLAN_SHA256,"protocol_version":PROTOCOL_VERSION,"code_sha256":code,"offline_probe_sha256":offline["offline_probe_sha256"],"analysis_protocol_review_sha256":review["review_sha256"],"transport_probe_sha256":transport["transport_probe_sha256"],"provider_call_upper_bound":PROVIDER_CALL_CAP,"sandboxed":True,"probe_passed":True,"budget_feasible":True,"scientific_object_unchanged":True,"scientific_authority":False,"belief_authority":False};manifest["harness_manifest_sha256"]=sha_json(manifest);write_json(run_root/IMPLEMENTATION_MANIFEST_FILENAME,manifest)
        receipt={"schema_version":"1.0","scientific_authority":False,"receipts":[{"candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"harness_manifest_sha256":manifest["harness_manifest_sha256"],"implementation_summary":"First-party P12 temporal sandbox: 4 disjoint no-skill paired difficulty calls, 4 disjoint calibration-to-skill compilation calls, frozen 8-skill 4/8-stage libraries, phase-identical BM25 retrieval query, uniform vs exponential half-life-2 recency ranking, 96 locked Kimi-K3 rollout units, deterministic integer truth, preregistered 8/4 additive-vs-interaction analysis independently reviewed CLEAR.","sandboxed":True,"probe_passed":True,"budget_feasible":True}]};write_json(run_root/IMPLEMENTATION_RECEIPT_FILENAME,receipt)
        compiled=compile_harness_implementation_receipts(plan,receipt);errors=validate_evidence_plan(compiled)
        if errors: raise ValueError(f"P12 authorization invalid:{errors}")
        row=next(x for x in compiled["entries"] if x.get("candidate_id")==CANDIDATE_ID)
        if row.get("status")!="READY_FOR_BOUNDED_EVIDENCE_ACQUISITION" or row.get("execution_authorized") is not True: raise RuntimeError("P12 bounded evidence not authorized")
        write_json(output,compiled);return {"status":"P12_HARNESS_IMPLEMENTATION_AUTHORIZED","harness_manifest_sha256":manifest["harness_manifest_sha256"],"execution_authorized":True,"provider_call_upper_bound":PROVIDER_CALL_CAP,"scientific_authority":False}
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def authorization_ok(run_root: Path) -> tuple[dict[str,Any],dict[str,Any]]:
    repaired=run_root/REPAIRED_AUTHORIZATION_FILENAME
    revoked=run_root/REVOKED_AUTHORIZATION_FILENAME
    if repaired.is_file():
        plan=load_json(repaired);manifest=load_json(run_root/REPAIRED_IMPLEMENTATION_MANIFEST_FILENAME)
    else:
        if revoked.is_file(): raise RuntimeError("P12 v1 authorization was revoked; repaired authorization is required")
        plan=load_json(run_root/AUTHORIZATION_FILENAME);manifest=load_json(run_root/IMPLEMENTATION_MANIFEST_FILENAME)
    row=next((x for x in plan.get("entries") or [] if x.get("candidate_id")==CANDIDATE_ID),None)
    if not row or row.get("status")!="READY_FOR_BOUNDED_EVIDENCE_ACQUISITION" or row.get("execution_authorized") is not True: raise RuntimeError("P12 bounded evidence not authorized")
    if str((row.get("harness_implementation") or {}).get("harness_manifest_sha256") or "")!=manifest["harness_manifest_sha256"]: raise RuntimeError("P12 harness manifest digest mismatch")
    return plan,manifest
