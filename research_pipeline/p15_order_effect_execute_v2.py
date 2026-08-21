from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .api_memory_store import connect, database_path
from .api_research_memory import (
    record_archived_api_parse_failure,
    record_parsed_api_output,
    record_provider_failure,
    record_raw_api_output,
)
from .ark_provider import ArkResponseStateError
from .p15_order_effect_harness import (
    EXECUTOR_MODEL,
    all_units,
    adjudicate,
    evaluate_solution,
    prompt_for_unit,
    sha_json,
    solution_tool,
)
from .p15_order_effect_protocol_v2 import (
    AUTHORIZATION_FILENAME,
    REPAIR_PLAN_FILENAME,
    PROTOCOL_VERSION,
    authorization_ok,
    client,
    extract_solution_code,
    load_json,
    lock_output,
    provider_archive_payload,
    sha_text,
    write_json,
)


def _v1_receipt(study: Path,unit_id: str) -> dict[str,Any] | None:
    path=study/"units"/f"{unit_id}.json"
    return load_json(path) if path.is_file() else None


def _run_prefix(study: Path) -> str:
    repair=load_json(study/REPAIR_PLAN_FILENAME)
    return f"p15-order-v2-{repair['replacement_harness_plan_sha256'][:10]}-"


def _recorded_calls(persistent_root: Path,prefix: str) -> tuple[int,set[str]]:
    db=database_path(root=persistent_root)
    if not db.is_file(): return 0,set()
    with connect(db) as connection:
        rows=connection.execute("SELECT run_id,provider_calls_executed FROM api_calls WHERE run_id LIKE ?",(prefix+"%",)).fetchall()
    return sum(int(row["provider_calls_executed"] or 0) for row in rows),{str(row["run_id"]) for row in rows}


def execute_unit(*,study: Path,persistent_root: Path,unit_id: str) -> dict[str,Any]:
    authorization_ok(study);units={row["unit_id"]:row for row in all_units()}
    if unit_id not in units: raise ValueError(f"unknown P15 unit:{unit_id}")
    repair=load_json(study/REPAIR_PLAN_FILENAME);retry=set(repair["retry_units"]);old=_v1_receipt(study,unit_id)
    if old and old.get("status")!="UNIT_PROTOCOL_FAILURE":
        return {"schema_version":"1.0","status":"V1_RECEIPT_REUSED","unit_id":unit_id,"v1_status":old.get("status"),"provider_call_executed":False,"scientific_authority":False,"belief_authority":False}
    if old and unit_id not in retry: raise RuntimeError(f"P15 v2 retry not authorized for old unit:{unit_id}")
    unit=units[unit_id];output=study/"units-v2"/f"{unit_id}.json";lock=lock_output(output,{"stage":"unit-v2","unit_id":unit_id});prefix=_run_prefix(study);run_id=prefix+unit_id.lower()
    try:
        calls_used,run_ids=_recorded_calls(persistent_root,prefix)
        if run_id in run_ids: raise RuntimeError(f"P15 v2 provider call already recorded for {unit_id}; no repeat POST allowed")
        if calls_used>=int(repair["replacement_provider_call_cap"]): raise RuntimeError("P15 v2 replacement provider-call cap exhausted")
        prompt=prompt_for_unit(unit);prompt_sha=sha_text(prompt);run_root=persistent_root/"runs"/run_id;run_root.mkdir(parents=True,exist_ok=True)
        try:
            response=client().respond(prompt,model=EXECUTOR_MODEL,max_output_tokens=2400,temperature=0.0,tools=solution_tool(),thinking="disabled",store=True)
        except ArkResponseStateError as error:
            fp=sha_json({"stage":"p15-order-unit-v2","unit_id":unit_id,"response_id":error.response_id,"status":error.response_status,"prompt_sha256":prompt_sha});receipt=record_provider_failure(run_root=run_root,stage="p15-order-unit-v2",payload={"status":"PROVIDER_STATE_ERROR_ZERO_AUTHORITY","requested_model":EXECUTOR_MODEL,"error_fingerprint":fp,"prompt_sha256":prompt_sha},root=persistent_root)
            result={"schema_version":"1.0","status":"UNIT_PROVIDER_STATE_FAILURE","unit_id":unit_id,"provider_response_id":error.response_id,"provider_failure":receipt,"valid_execution":False,"task_success":False,"scientific_authority":False,"belief_authority":False};write_json(output,result);return result
        except Exception as error:
            fp=sha_json({"stage":"p15-order-unit-v2","unit_id":unit_id,"error":str(error)[:500],"prompt_sha256":prompt_sha});receipt=record_provider_failure(run_root=run_root,stage="p15-order-unit-v2",payload={"status":"PROVIDER_ERROR_ZERO_AUTHORITY","requested_model":EXECUTOR_MODEL,"error_fingerprint":fp,"prompt_sha256":prompt_sha},root=persistent_root)
            result={"schema_version":"1.0","status":"UNIT_PROVIDER_FAILURE","unit_id":unit_id,"provider_failure":receipt,"valid_execution":False,"task_success":False,"scientific_authority":False,"belief_authority":False};write_json(output,result);return result
        archive=provider_archive_payload(response);raw_file=run_root/"raw-unit-v2.json";raw_file.write_text(json.dumps(archive,ensure_ascii=False,sort_keys=True,separators=(",",":")),encoding="utf-8")
        archived=record_raw_api_output(run_root=run_root,stage="p15-order-unit-v2",raw_path=raw_file,requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],request_fingerprint=sha_json({"stage":"p15-order-unit-v2","unit_id":unit_id,"prompt_sha256":prompt_sha}),prompt_sha256=prompt_sha,root=persistent_root)
        try: code,source=extract_solution_code(archive)
        except Exception as error:
            record_archived_api_parse_failure(run_root=run_root,stage="p15-order-unit-v2",raw_sha256=archived["raw_sha256"],error=f"{type(error).__name__}:{error}",requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],root=persistent_root)
            result={"schema_version":"1.0","status":"UNIT_PROTOCOL_FAILURE_V2","unit_id":unit_id,"task_id":unit["task_id"],"condition_id":unit["condition_id"],"skills":unit["skills"],"raw_sha256":archived["raw_sha256"],"response_id_archived":bool(archive["response_id"]),"valid_execution":False,"task_success":False,"scientific_authority":False,"belief_authority":False};write_json(output,result);return result
        evaluation=evaluate_solution(unit["task_id"],code)
        result={"schema_version":"1.0","status":"UNIT_COMPLETE" if evaluation.get("valid_execution") else "UNIT_INVALID_EXECUTION","unit_id":unit_id,"task_id":unit["task_id"],"condition_id":unit["condition_id"],"condition_kind":unit["kind"],"skills":unit["skills"],"prompt_sha256":prompt_sha,"raw_sha256":archived["raw_sha256"],"resolved_model":archive["resolved_model"],"response_id_archived":bool(archive["response_id"]),"code_source":source,"usage":archive["usage"],"code_sha256":sha_text(code),"valid_execution":bool(evaluation.get("valid_execution")),"task_success":bool(evaluation.get("task_success")),"uptake":evaluation.get("uptake") or {},"ast_audit":evaluation.get("ast_audit") or {},"case_results":evaluation.get("cases") or [],"error":evaluation.get("error", ""),"scientific_authority":False,"belief_authority":False}
        result["unit_receipt_sha256"]=sha_json(result);record_parsed_api_output(run_root=run_root,stage="p15-order-unit-v2",raw_sha256=archived["raw_sha256"],structured_payload=result,requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],research_objects=[],root=persistent_root);write_json(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def pending_units(study: Path) -> list[str]:
    repair=load_json(study/REPAIR_PLAN_FILENAME);retry=set(repair["retry_units"]);pending=[]
    for row in all_units():
        uid=row["unit_id"]
        if (study/"units-v2"/f"{uid}.json").is_file(): continue
        v1=_v1_receipt(study,uid)
        if v1 is None or (v1.get("status")=="UNIT_PROTOCOL_FAILURE" and uid in retry): pending.append(uid)
    return pending


def run_pending(*,study: Path,persistent_root: Path,limit: int=5) -> dict[str,Any]:
    authorization_ok(study);completed=[]
    for uid in pending_units(study)[:max(0,int(limit))]:
        result=execute_unit(study=study,persistent_root=persistent_root,unit_id=uid);completed.append({"unit_id":uid,"status":result.get("status")})
        if result.get("status") in {"UNIT_PROTOCOL_FAILURE_V2","UNIT_PROVIDER_FAILURE","UNIT_PROVIDER_STATE_FAILURE"}: break
    after=pending_units(study)
    return {"schema_version":"1.0","status":"P15_V2_BATCH_PROGRESS","completed":completed,"pending_count":len(after),"next_units":after[:10],"scientific_authority":False,"belief_authority":False}


def combined_receipts(study: Path) -> list[dict[str,Any]]:
    rows=[]
    for unit in all_units():
        uid=unit["unit_id"];v2=study/"units-v2"/f"{uid}.json";v1=study/"units"/f"{uid}.json"
        if v2.is_file(): rows.append(load_json(v2))
        elif v1.is_file(): rows.append(load_json(v1))
    return rows


def finalize(study: Path) -> dict[str,Any]:
    output=study/"adjudication-v2.json";lock=lock_output(output,{"stage":"finalize-v2"})
    try:
        result=adjudicate(combined_receipts(study));repair=load_json(study/REPAIR_PLAN_FILENAME);result["protocol_version"]=PROTOCOL_VERSION;result["replacement_harness_plan_sha256"]=repair["replacement_harness_plan_sha256"];result["v1_receipts_reused"]=sum(1 for row in all_units() if (study/"units"/f"{row['unit_id']}.json").is_file() and not (study/"units-v2"/f"{row['unit_id']}.json").is_file());result["v2_receipts"]=sum(1 for row in all_units() if (study/"units-v2"/f"{row['unit_id']}.json").is_file());result["adjudication_sha256"]=sha_json({k:v for k,v in result.items() if k!="adjudication_sha256"});write_json(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def main() -> None:
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest="cmd",required=True)
    u=sub.add_parser("unit");u.add_argument("--study",type=Path,required=True);u.add_argument("--persistent-root",type=Path,required=True);u.add_argument("--unit-id",required=True)
    b=sub.add_parser("batch");b.add_argument("--study",type=Path,required=True);b.add_argument("--persistent-root",type=Path,required=True);b.add_argument("--limit",type=int,default=5)
    f=sub.add_parser("finalize");f.add_argument("--study",type=Path,required=True)
    args=parser.parse_args()
    if args.cmd=="unit": out=execute_unit(study=args.study,persistent_root=args.persistent_root,unit_id=args.unit_id)
    elif args.cmd=="batch": out=run_pending(study=args.study,persistent_root=args.persistent_root,limit=args.limit)
    else: out=finalize(args.study)
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=="__main__": main()
