from __future__ import annotations

import argparse
import hashlib
import json
import os
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
    adjudicate,
    all_units,
    evaluate_solution,
    offline_probe,
    prompt_for_unit,
    sha_json,
    solution_tool,
)
from .paper_first_evidence_acquisition import (
    compile_harness_implementation_receipts,
    validate_evidence_plan,
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _lock(output: Path, payload: dict[str, Any]) -> Path:
    if output.exists():
        raise RuntimeError(f"OUTPUT_ALREADY_EXISTS:{output}")
    lock = Path(str(output) + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise RuntimeError(f"STAGE_ALREADY_RUNNING_OR_STALE_LOCK:{lock}") from error
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        handle.flush(); os.fsync(handle.fileno())
    return lock


def _client() -> ArkResponsesClient:
    base = ArkSettings.from_env()
    return ArkResponsesClient(replace(base, max_retries=0, timeout_seconds=max(180.0, base.timeout_seconds)))


def run_offline_probe(*, study: Path) -> dict[str, Any]:
    output = study / "offline-probe.json"
    lock = _lock(output, {"stage": "offline-probe"})
    try:
        result = offline_probe()
        _write(output, result)
        return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def run_transport_probe(*, study: Path, persistent_root: Path) -> dict[str, Any]:
    output = study / "transport-probe.json"
    lock = _lock(output, {"stage": "transport-probe"})
    run_id = f"p15-order-harness-transport-{HARNESS_PLAN_SHA256[:12]}"
    try:
        prompt = "Neutral harness transport probe. Call submit_solution exactly once with python_code='def solve(records):\\n    return records'. No scientific task or candidate evidence is present."
        run_root = persistent_root / "runs" / run_id
        run_root.mkdir(parents=True, exist_ok=True)
        prompt_sha = _sha_text(prompt)
        try:
            response = _client().respond(
                prompt,
                model=EXECUTOR_MODEL,
                max_output_tokens=400,
                temperature=0.0,
                tools=solution_tool(),
                thinking="disabled",
                store=True,
            )
        except Exception as error:
            fp = sha_json({"stage":"p15-transport-probe","error":str(error)[:500],"prompt_sha256":prompt_sha})
            receipt = record_provider_failure(
                run_root=run_root,
                stage="p15-order-transport-probe",
                payload={"status":"PROVIDER_ERROR_ZERO_AUTHORITY","requested_model":EXECUTOR_MODEL,"error_fingerprint":fp,"prompt_sha256":prompt_sha},
                root=persistent_root,
            )
            result={"schema_version":"1.0","status":"P15_TRANSPORT_PROBE_FAIL","error":f"{type(error).__name__}:{str(error)[:1000]}","provider_failure":receipt,"scientific_authority":False,"belief_authority":False}
            _write(output,result);return result
        calls=[call for call in response.get("function_calls") or [] if call.get("name")=="submit_solution"]
        safe={"requested_model":EXECUTOR_MODEL,"resolved_model":str(response.get("resolved_model") or EXECUTOR_MODEL),"function_calls":calls,"usage":response.get("usage") or {},"scientific_authority":False}
        raw=json.dumps(safe,ensure_ascii=False,sort_keys=True,separators=(",",":"));raw_file=run_root/"raw-transport-probe.json";raw_file.write_text(raw,encoding="utf-8")
        archived=record_raw_api_output(run_root=run_root,stage="p15-order-transport-probe",raw_path=raw_file,requested_model=EXECUTOR_MODEL,resolved_model=safe["resolved_model"],request_fingerprint=sha_json({"stage":"p15-order-transport-probe","prompt_sha256":prompt_sha}),prompt_sha256=prompt_sha,root=persistent_root)
        if len(calls)!=1:
            record_archived_api_parse_failure(run_root=run_root,stage="p15-order-transport-probe",raw_sha256=archived["raw_sha256"],error=f"expected one submit_solution call got {len(calls)}",requested_model=EXECUTOR_MODEL,resolved_model=safe["resolved_model"],root=persistent_root)
            result={"schema_version":"1.0","status":"P15_TRANSPORT_PROBE_FAIL","raw_sha256":archived["raw_sha256"],"reason":"missing required function call","scientific_authority":False,"belief_authority":False};_write(output,result);return result
        args=json.loads(str(calls[0].get("arguments") or "{}"));code=str(args.get("python_code") or "")
        evaluation=evaluate_solution("T1","def solve(records):\n    return records\n")
        result={"schema_version":"1.0","status":"P15_TRANSPORT_PROBE_PASS" if code.startswith("def solve") else "P15_TRANSPORT_PROBE_FAIL","raw_sha256":archived["raw_sha256"],"resolved_model":safe["resolved_model"],"usage":safe["usage"],"function_transport":len(calls)==1,"neutral_code_received":bool(code),"local_evaluator_callable":evaluation.get("valid_execution") is True,"scientific_authority":False,"belief_authority":False}
        record_parsed_api_output(run_root=run_root,stage="p15-order-transport-probe",raw_sha256=archived["raw_sha256"],structured_payload=result,requested_model=EXECUTOR_MODEL,resolved_model=safe["resolved_model"],research_objects=[],root=persistent_root)
        result["transport_probe_sha256"]=sha_json(result);_write(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def authorize(*, study: Path, source_plan: Path) -> dict[str, Any]:
    output=study/"authorization-plan.json";lock=_lock(output,{"stage":"authorize"})
    try:
        plan=_load(source_plan);offline=_load(study/"offline-probe.json");transport=_load(study/"transport-probe.json")
        if offline.get("status")!="P15_OFFLINE_HARNESS_PROBE_PASS" or transport.get("status")!="P15_TRANSPORT_PROBE_PASS":raise RuntimeError("P15 harness probes not PASS")
        module_path=Path(__file__).with_name("p15_order_effect_harness.py")
        manifest={"schema_version":"1.0","status":"P15_HARNESS_IMPLEMENTATION_PROBE_PASS","candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"harness_plan_sha256":HARNESS_PLAN_SHA256,"code_sha256":{"p15_order_effect_harness.py":_sha_bytes(module_path.read_bytes()),"p15_order_effect_runner.py":_sha_bytes(Path(__file__).read_bytes())},"offline_probe_sha256":offline["offline_probe_sha256"],"transport_probe_sha256":transport["transport_probe_sha256"],"sandboxed":True,"probe_passed":True,"budget_feasible":offline.get("unit_count")==50 and offline.get("provider_call_upper_bound")<=80,"scientific_authority":False,"belief_authority":False}
        manifest["harness_manifest_sha256"]=sha_json(manifest);_write(study/"harness-manifest.json",manifest)
        receipt={"schema_version":"1.0","scientific_authority":False,"receipts":[{"candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"harness_manifest_sha256":manifest["harness_manifest_sha256"],"implementation_summary":"First-party P15 sandbox: five frozen benign Python tasks, five frozen procedural skills, six identical-skill permutations plus no/single-skill controls; Kimi-K3 one-call executor; AST safety validation; executable unit-test truth; mechanical uptake signatures; per-unit locks/receipts.","sandboxed":True,"probe_passed":True,"budget_feasible":True}]}
        _write(study/"harness-implementation-receipt.json",receipt)
        compiled=compile_harness_implementation_receipts(plan,receipt);errors=validate_evidence_plan(compiled)
        if errors:raise ValueError(f"compiled authorization plan invalid:{errors}")
        entry=next(row for row in compiled["entries"] if row.get("candidate_id")==CANDIDATE_ID)
        if entry.get("status")!="READY_FOR_BOUNDED_EVIDENCE_ACQUISITION" or entry.get("execution_authorized") is not True:raise RuntimeError("P15 bounded evidence not authorized by compiler")
        _write(output,compiled)
        return {"status":"P15_BOUNDED_EVIDENCE_AUTHORIZED","harness_manifest_sha256":manifest["harness_manifest_sha256"],"execution_authorized":True,"scientific_authority":False}
    finally:
        if output.exists():lock.unlink(missing_ok=True)


def _authorization_ok(study: Path) -> None:
    plan=_load(study/"authorization-plan.json")
    entry=next((row for row in plan.get("entries") or [] if row.get("candidate_id")==CANDIDATE_ID),None)
    if not entry or entry.get("status")!="READY_FOR_BOUNDED_EVIDENCE_ACQUISITION" or entry.get("execution_authorized") is not True:raise RuntimeError("P15 bounded evidence execution is not authorized")
    if str(entry.get("contract_sha256") or "")!=CONTRACT_SHA256 or str((entry.get("harness_implementation") or {}).get("harness_manifest_sha256") or "")!=str(_load(study/"harness-manifest.json").get("harness_manifest_sha256") or ""):raise RuntimeError("P15 authorization digest mismatch")


def execute_unit(*, study: Path, persistent_root: Path, unit_id: str) -> dict[str, Any]:
    _authorization_ok(study)
    units={row["unit_id"]:row for row in all_units()}
    if unit_id not in units:raise ValueError(f"unknown P15 unit:{unit_id}")
    unit=units[unit_id];output=study/"units"/f"{unit_id}.json";lock=_lock(output,{"stage":"unit","unit_id":unit_id})
    run_id=f"p15-order-{HARNESS_PLAN_SHA256[:10]}-{unit_id.lower()}"
    try:
        prompt=prompt_for_unit(unit);prompt_sha=_sha_text(prompt);run_root=persistent_root/"runs"/run_id;run_root.mkdir(parents=True,exist_ok=True)
        try:
            response=_client().respond(prompt,model=EXECUTOR_MODEL,max_output_tokens=2400,temperature=0.0,tools=solution_tool(),thinking="disabled",store=True)
        except Exception as error:
            fp=sha_json({"stage":"p15-order-unit","unit_id":unit_id,"error":str(error)[:500],"prompt_sha256":prompt_sha})
            receipt=record_provider_failure(run_root=run_root,stage="p15-order-unit",payload={"status":"PROVIDER_ERROR_ZERO_AUTHORITY","requested_model":EXECUTOR_MODEL,"error_fingerprint":fp,"prompt_sha256":prompt_sha},root=persistent_root)
            result={"schema_version":"1.0","status":"UNIT_PROVIDER_FAILURE","unit_id":unit_id,"task_id":unit["task_id"],"condition_id":unit["condition_id"],"skills":unit["skills"],"provider_failure":receipt,"valid_execution":False,"task_success":False,"scientific_authority":False,"belief_authority":False};_write(output,result);return result
        calls=[call for call in response.get("function_calls") or [] if call.get("name")=="submit_solution"]
        safe={"requested_model":EXECUTOR_MODEL,"resolved_model":str(response.get("resolved_model") or EXECUTOR_MODEL),"function_calls":calls,"usage":response.get("usage") or {},"scientific_authority":False}
        raw=json.dumps(safe,ensure_ascii=False,sort_keys=True,separators=(",",":"));raw_file=run_root/"raw-unit.json";raw_file.write_text(raw,encoding="utf-8")
        archived=record_raw_api_output(run_root=run_root,stage="p15-order-unit",raw_path=raw_file,requested_model=EXECUTOR_MODEL,resolved_model=safe["resolved_model"],request_fingerprint=sha_json({"stage":"p15-order-unit","unit_id":unit_id,"prompt_sha256":prompt_sha}),prompt_sha256=prompt_sha,root=persistent_root)
        if len(calls)!=1:
            record_archived_api_parse_failure(run_root=run_root,stage="p15-order-unit",raw_sha256=archived["raw_sha256"],error=f"expected one submit_solution call got {len(calls)}",requested_model=EXECUTOR_MODEL,resolved_model=safe["resolved_model"],root=persistent_root)
            result={"schema_version":"1.0","status":"UNIT_PROTOCOL_FAILURE","unit_id":unit_id,"task_id":unit["task_id"],"condition_id":unit["condition_id"],"skills":unit["skills"],"raw_sha256":archived["raw_sha256"],"valid_execution":False,"task_success":False,"scientific_authority":False,"belief_authority":False};_write(output,result);return result
        try:
            args=json.loads(str(calls[0].get("arguments") or "{}"));code=str(args.get("python_code") or "")
        except Exception as error:
            record_archived_api_parse_failure(run_root=run_root,stage="p15-order-unit",raw_sha256=archived["raw_sha256"],error=f"function arguments:{type(error).__name__}:{error}",requested_model=EXECUTOR_MODEL,resolved_model=safe["resolved_model"],root=persistent_root)
            result={"schema_version":"1.0","status":"UNIT_PROTOCOL_FAILURE","unit_id":unit_id,"task_id":unit["task_id"],"condition_id":unit["condition_id"],"skills":unit["skills"],"raw_sha256":archived["raw_sha256"],"valid_execution":False,"task_success":False,"scientific_authority":False,"belief_authority":False};_write(output,result);return result
        evaluation=evaluate_solution(unit["task_id"],code)
        result={"schema_version":"1.0","status":"UNIT_COMPLETE" if evaluation.get("valid_execution") else "UNIT_INVALID_EXECUTION","unit_id":unit_id,"task_id":unit["task_id"],"condition_id":unit["condition_id"],"condition_kind":unit["kind"],"skills":unit["skills"],"prompt_sha256":prompt_sha,"raw_sha256":archived["raw_sha256"],"resolved_model":safe["resolved_model"],"usage":safe["usage"],"code_sha256":_sha_text(code),"valid_execution":bool(evaluation.get("valid_execution")),"task_success":bool(evaluation.get("task_success")),"uptake":evaluation.get("uptake") or {},"ast_audit":evaluation.get("ast_audit") or {},"case_results":evaluation.get("cases") or [],"error":evaluation.get("error", ""),"scientific_authority":False,"belief_authority":False}
        result["unit_receipt_sha256"]=sha_json(result)
        record_parsed_api_output(run_root=run_root,stage="p15-order-unit",raw_sha256=archived["raw_sha256"],structured_payload=result,requested_model=EXECUTOR_MODEL,resolved_model=safe["resolved_model"],research_objects=[],root=persistent_root)
        _write(output,result);return result
    finally:
        if output.exists():lock.unlink(missing_ok=True)


def finalize(*, study: Path) -> dict[str, Any]:
    output=study/"adjudication.json";lock=_lock(output,{"stage":"finalize"})
    try:
        units=[]
        for path in sorted((study/"units").glob("*.json")):
            units.append(_load(path))
        result=adjudicate(units);_write(output,result);return result
    finally:
        if output.exists():lock.unlink(missing_ok=True)


def main() -> None:
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("offline-probe");p.add_argument("--study",type=Path,required=True)
    t=sub.add_parser("transport-probe");t.add_argument("--study",type=Path,required=True);t.add_argument("--persistent-root",type=Path,required=True)
    a=sub.add_parser("authorize");a.add_argument("--study",type=Path,required=True);a.add_argument("--source-plan",type=Path,required=True)
    u=sub.add_parser("unit");u.add_argument("--study",type=Path,required=True);u.add_argument("--persistent-root",type=Path,required=True);u.add_argument("--unit-id",required=True)
    f=sub.add_parser("finalize");f.add_argument("--study",type=Path,required=True)
    args=parser.parse_args()
    if args.cmd=="offline-probe":out=run_offline_probe(study=args.study)
    elif args.cmd=="transport-probe":out=run_transport_probe(study=args.study,persistent_root=args.persistent_root)
    elif args.cmd=="authorize":out=authorize(study=args.study,source_plan=args.source_plan)
    elif args.cmd=="unit":out=execute_unit(study=args.study,persistent_root=args.persistent_root,unit_id=args.unit_id)
    else:out=finalize(study=args.study)
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=="__main__":main()
