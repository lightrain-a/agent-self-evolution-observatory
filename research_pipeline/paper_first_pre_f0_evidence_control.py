from __future__ import annotations

import fcntl
import hashlib
import json
import re
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .config import PROJECT_ROOT, StorageSettings
from .paper_first_evidence_acquisition import (
    build_provisional_evidence_plan_from_pre_f0,
    build_substrate_preflight_request,
    compile_evidence_designs,
    compile_harness_implementation_receipts,
    compile_evidence_reviews,
    compile_operationalization_recompiles,
    compile_substrate_preflight,
    evidence_design_prompt,
    evidence_review_prompt,
    operationalization_recompile_prompt,
    validate_evidence_plan,
)
from .paper_first_pre_f0_queue import load_pre_f0_queue
from .paper_first_problem_falsifier_preflight import load_pre_f0_problem_falsifier_preflight
from .premium_model_policy import PREMIUM_AUTO, independent_priority, preferred_model
from .problem_search_stage_runner import (
    _ark_with_provider_receipt,
    _evidence_memory_pack,
    _parse_archived_evidence_design_json,
    _provider_success_metadata,
    _record_memory_receipt,
)

SCHEMA_VERSION = "1.0"
DEFAULT_PLAN_JSON = PROJECT_ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-state.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-state.js"
DEFAULT_QUEUE_JSON = PROJECT_ROOT / "generated" / "paper-first-pre-f0-queue.json"
DEFAULT_SUPPORT_JSON = PROJECT_ROOT / "generated" / "paper-first-pre-f0-problem-falsifier-preflight.json"
AUTHORITY = {"live_problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False}
POLICY = {
    "scientific_authority": False,
    "canonical_pre_f0_only": True,
    "control_binds_queue_support_plan_and_candidate_snapshots": True,
    "provider_raw_is_private_content_addressed": True,
    "one_design_stage_per_input_control": True,
    "design_model_call_has_zero_scientific_authority": True,
    "design_cannot_authorize_execution": True,
    "independent_review_required_before_substrate_preflight": True,
    "support_hold_is_not_scientific_negative": True,
    "first_party_design_must_preserve_frozen_prediction_baseline_and_falsifier": True,
    "automatic_problem_gate_method_experiment_p0_gpu_authority": False,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_path(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object:{path}")
    return payload


def _candidate_snapshots(plan: dict[str, Any]) -> list[str]:
    values=[]
    for row in plan.get("entries") or []:
        if not isinstance(row,dict):
            continue
        digest=str(row.get("candidate_snapshot_sha256") or "").strip().lower()
        if not re.fullmatch(r"[0-9a-f]{64}",digest):
            raise ValueError("canonical Pre-F0 evidence plan candidate snapshot invalid")
        values.append(digest)
    if len(values)!=len(set(values)):
        raise ValueError("canonical Pre-F0 evidence plan candidate snapshots must be unique")
    return sorted(values)


def _control_material(*,queue_path:Path,support_path:Path,plan_path:Path,plan:dict[str,Any]) -> dict[str,Any]:
    material={
        "schema_version":SCHEMA_VERSION,
        "queue_sha256":_sha_path(queue_path),
        "support_preflight_sha256":_sha_path(support_path),
        "plan_sha256":_sha_path(plan_path),
        "support_inventory_sha256":str(plan.get("support_inventory_sha256") or ""),
        "candidate_snapshot_sha256s":_candidate_snapshots(plan),
    }
    inv=material["support_inventory_sha256"]
    if inv and not re.fullmatch(r"[0-9a-f]{64}",inv):
        raise ValueError("canonical Pre-F0 evidence plan support inventory digest invalid")
    return material


def control_snapshot(*,queue_path:Path=DEFAULT_QUEUE_JSON,support_path:Path=DEFAULT_SUPPORT_JSON,plan_path:Path=DEFAULT_PLAN_JSON) -> dict[str,Any]:
    plan=_load(plan_path)
    errors=validate_evidence_plan(plan)
    if errors:
        raise ValueError("invalid canonical Pre-F0 evidence plan: "+",".join(errors))
    queue=_load(queue_path);support=_load(support_path)
    # Rebuild only the immutable route identity.  generated_at is deliberately ignored;
    # every candidate snapshot and support disposition must still match exactly.
    rebuilt=build_provisional_evidence_plan_from_pre_f0(queue,support,run_id=str(plan.get("run_id") or ""),max_active=max(1,int((plan.get("summary") or {}).get("design_selected") or 1)))
    actual={str(row.get("candidate_id") or ""):(str(row.get("candidate_snapshot_sha256") or ""),str(row.get("frozen_irreducible_object") or ""),str(row.get("frozen_exact_prediction") or ""),str(row.get("frozen_same_information_baseline") or ""),str(row.get("frozen_falsifier_expression") or ""),tuple(row.get("source_refs") or [])) for row in plan.get("entries") or [] if isinstance(row,dict)}
    expected={str(row.get("candidate_id") or ""):(str(row.get("candidate_snapshot_sha256") or ""),str(row.get("frozen_irreducible_object") or ""),str(row.get("frozen_exact_prediction") or ""),str(row.get("frozen_same_information_baseline") or ""),str(row.get("frozen_falsifier_expression") or ""),tuple(row.get("source_refs") or [])) for row in rebuilt.get("entries") or [] if isinstance(row,dict)}
    # Once a design has been compiled, the plan has later-stage fields, but the original
    # route identity above must still be exactly the deterministic adapter projection.
    if actual!=expected:
        raise ValueError("canonical Pre-F0 evidence plan drift versus current queue/support identities")
    material=_control_material(queue_path=queue_path,support_path=support_path,plan_path=plan_path,plan=plan)
    control_sha=_sha_bytes(json.dumps(material,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode())
    return {**material,"control_snapshot_sha256":control_sha,"scientific_authority":False}


def _public_state(*,plan:dict[str,Any],control:dict[str,Any],last_stage:dict[str,Any]|None=None,status:str|None=None) -> dict[str,Any]:
    summary=dict(plan.get("summary") or {})
    stage=last_stage or {}
    return {
        "schema_version":SCHEMA_VERSION,
        "generated_at":_now(),
        "status":status or str(plan.get("status") or "NOT_RUN"),
        "control_snapshot_sha256":str(control.get("control_snapshot_sha256") or ""),
        "queue_sha256":str(control.get("queue_sha256") or ""),
        "support_preflight_sha256":str(control.get("support_preflight_sha256") or ""),
        "support_inventory_sha256":str(control.get("support_inventory_sha256") or ""),
        "plan_sha256":str(control.get("plan_sha256") or ""),
        "candidate_snapshot_sha256s":list(control.get("candidate_snapshot_sha256s") or []),
        "policy":dict(POLICY),
        "summary":summary,
        "last_stage":{
            "stage":str(stage.get("stage") or ""),
            "candidate_ids":list(stage.get("candidate_ids") or []),
            "requested_model":str(stage.get("requested_model") or ""),
            "resolved_model":str(stage.get("resolved_model") or ""),
            "raw_sha256":str(stage.get("raw_sha256") or ""),
            "provider_calls_executed":int(stage.get("provider_calls_executed") or 0),
            "research_memory_query_pack_sha256":str(stage.get("research_memory_query_pack_sha256") or ""),
            "scientific_authority":False,
        },
        "scientific_authority":False,
        "authority":dict(AUTHORITY),
    }


def validate_public_state(state:dict[str,Any]) -> list[str]:
    errors=[];policy=state.get("policy") or {};summary=state.get("summary") or {};last=state.get("last_stage") or {}
    if state.get("scientific_authority") is not False or any((state.get("authority") or {}).get(k) is not False for k in AUTHORITY):errors.append("canonical Pre-F0 evidence control cannot carry downstream authority")
    for key,value in POLICY.items():
        if policy.get(key)!=value:errors.append("canonical Pre-F0 evidence control policy mismatch:"+key)
    for key in ("control_snapshot_sha256","queue_sha256","support_preflight_sha256","plan_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}",str(state.get(key) or "")):errors.append("canonical Pre-F0 evidence control digest invalid:"+key)
    inv=str(state.get("support_inventory_sha256") or "")
    if inv and not re.fullmatch(r"[0-9a-f]{64}",inv):errors.append("canonical Pre-F0 evidence support inventory digest invalid")
    if any(int(summary.get(k) or 0)!=0 for k in ("paper_design_authorized","method_authorized","p0_authorized","full_experiment_authorized")):errors.append("canonical Pre-F0 evidence control summary leaks downstream authority")
    if int(last.get("provider_calls_executed") or 0)<0:errors.append("canonical Pre-F0 evidence provider accounting invalid")
    raw=str(last.get("raw_sha256") or "")
    if raw and not re.fullmatch(r"[0-9a-f]{64}",raw):errors.append("canonical Pre-F0 evidence raw digest invalid")
    snapshots=list(state.get("candidate_snapshot_sha256s") or [])
    if not snapshots or any(not re.fullmatch(r"[0-9a-f]{64}",str(x or "")) for x in snapshots) or len(snapshots)!=len(set(snapshots)):errors.append("canonical Pre-F0 evidence candidate snapshot set invalid")
    return sorted(set(errors))


def _write_public(state:dict[str,Any],json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS) -> None:
    errors=validate_public_state(state)
    if errors:raise ValueError("invalid canonical Pre-F0 evidence public state: "+",".join(errors))
    json_path.parent.mkdir(parents=True,exist_ok=True);json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_PRE_F0_EVIDENCE_ACQUISITION = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")


def prepare(*,queue_path:Path=DEFAULT_QUEUE_JSON,support_path:Path=DEFAULT_SUPPORT_JSON,plan_path:Path=DEFAULT_PLAN_JSON,json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS,max_active:int=1) -> dict[str,Any]:
    queue=_load(queue_path);support=_load(support_path);plan=build_provisional_evidence_plan_from_pre_f0(queue,support,run_id="canonical-pre-f0-"+str(queue.get("source_generator_run_id") or ""),max_active=max_active)
    errors=validate_evidence_plan(plan)
    if errors:raise ValueError("invalid canonical Pre-F0 evidence plan: "+",".join(errors))
    plan_path.parent.mkdir(parents=True,exist_ok=True);plan_path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    control=control_snapshot(queue_path=queue_path,support_path=support_path,plan_path=plan_path);public=_public_state(plan=plan,control=control)
    _write_public(public,json_path,js_path);return public


@contextmanager
def _execution_lock(storage:StorageSettings) -> Iterator[None]:
    root=storage.data_root/"paper-first-pre-f0-evidence";root.mkdir(parents=True,exist_ok=True);path=root/"execution.lock"
    with path.open("a+") as handle:
        try:fcntl.flock(handle.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as error:raise RuntimeError("canonical Pre-F0 evidence control already executing") from error
        try:yield
        finally:fcntl.flock(handle.fileno(),fcntl.LOCK_UN)


def design(*,storage:StorageSettings|None=None,queue_path:Path=DEFAULT_QUEUE_JSON,support_path:Path=DEFAULT_SUPPORT_JSON,plan_path:Path=DEFAULT_PLAN_JSON,json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS,model:str=PREMIUM_AUTO) -> dict[str,Any]:
    storage=storage or StorageSettings.from_env();storage.ensure()
    with _execution_lock(storage):
        plan=_load(plan_path);control=control_snapshot(queue_path=queue_path,support_path=support_path,plan_path=plan_path)
        if str(plan.get("status") or "")!="EVIDENCE_DESIGN_PENDING" or int((plan.get("summary") or {}).get("design_pending") or 0)<=0:raise ValueError("canonical Pre-F0 evidence design has no pending design")
        input_control=str(control["control_snapshot_sha256"]);run_root=storage.data_root/"paper-first-pre-f0-evidence"/input_control
        success_path=run_root/"evidence-design-p1.json"
        if success_path.is_file():raise ValueError("canonical Pre-F0 evidence design already completed for this input control")
        run_root.mkdir(parents=True,exist_ok=True)
        memory_pack=_evidence_memory_pack(plan);memory_path=run_root/"research-memory-query-pack.json";memory_path.write_text(json.dumps(memory_pack,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        prompt,candidate_ids=evidence_design_prompt(plan,part=1,batch_size=1,research_memory_query_pack=memory_pack)
        requested=preferred_model("evidence_design",model)
        res=_ark_with_provider_receipt(run_root=run_root,stem="evidence-design-p1",requested_model=requested,context={"part":1,"candidate_ids":candidate_ids,"control_snapshot_sha256":input_control},prompt=prompt,max_output_tokens=5200,temperature=0.0,stage="evidence_design")
        raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or requested);payload,raw_sha=_parse_archived_evidence_design_json(run_root,"evidence-design-p1",raw,resolved);compiled=compile_evidence_designs(plan,payload,part=1,design_model=resolved);_record_memory_receipt(compiled,stage="evidence-design",part=1,pack=memory_pack)
        errors=validate_evidence_plan(compiled)
        if errors:raise ValueError("compiled canonical Pre-F0 evidence design invalid: "+",".join(errors))
        transport=_provider_success_metadata(run_root=run_root,stem="evidence-design-p1",response=res)
        artifact={"schema_version":SCHEMA_VERSION,"generated_at":_now(),"stage":"evidence-design","input_control_snapshot_sha256":input_control,"input_plan_sha256":str(control.get("plan_sha256") or ""),"candidate_ids":candidate_ids,"candidate_snapshot_sha256s":list(control.get("candidate_snapshot_sha256s") or []),"support_inventory_sha256":str(control.get("support_inventory_sha256") or ""),"research_memory_query_pack_sha256":str(memory_pack.get("query_pack_sha256") or ""),"research_memory_query_pack_file_sha256":_sha_path(memory_path),"requested_model":requested,"resolved_model":resolved,"raw_sha256":raw_sha,"raw_archived_before_parse":True,**transport,"scientific_authority":False,"authority":dict(AUTHORITY)}
        success_path.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        plan_path.write_text(json.dumps(compiled,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        output_control=control_snapshot(queue_path=queue_path,support_path=support_path,plan_path=plan_path)
        public=_public_state(plan=compiled,control=output_control,last_stage=artifact);public["parent_control_snapshot_sha256"]=input_control
        _write_public(public,json_path,js_path)
        return public


def recompile_operationalization(*,storage:StorageSettings|None=None,queue_path:Path=DEFAULT_QUEUE_JSON,support_path:Path=DEFAULT_SUPPORT_JSON,plan_path:Path=DEFAULT_PLAN_JSON,json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS,model:str=PREMIUM_AUTO) -> dict[str,Any]:
    storage=storage or StorageSettings.from_env();storage.ensure()
    with _execution_lock(storage):
        plan=_load(plan_path);control=control_snapshot(queue_path=queue_path,support_path=support_path,plan_path=plan_path)
        if str(plan.get("status") or "")!="EVIDENCE_OPERATIONALIZATION_RECOMPILE_PENDING" or int((plan.get("summary") or {}).get("operationalization_recompile_pending") or 0)<=0:raise ValueError("canonical Pre-F0 evidence control has no operationalization recompile pending")
        input_control=str(control["control_snapshot_sha256"]);run_root=storage.data_root/"paper-first-pre-f0-evidence"/input_control;success_path=run_root/"evidence-recompile-p1.json"
        if success_path.is_file():raise ValueError("canonical Pre-F0 operationalization recompile already completed for this input control")
        run_root.mkdir(parents=True,exist_ok=True);memory_pack=_evidence_memory_pack(plan);memory_path=run_root/"research-memory-query-pack.json";memory_path.write_text(json.dumps(memory_pack,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        prompt,candidate_ids=operationalization_recompile_prompt(plan,part=1,batch_size=1,research_memory_query_pack=memory_pack);requested=preferred_model("evidence_recompile",model)
        res=_ark_with_provider_receipt(run_root=run_root,stem="evidence-recompile-p1",requested_model=requested,context={"part":1,"candidate_ids":candidate_ids,"control_snapshot_sha256":input_control},prompt=prompt,max_output_tokens=5600,temperature=0.0,stage="evidence_recompile")
        raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or requested);payload,raw_sha=_parse_archived_evidence_design_json(run_root,"evidence-recompile-p1",raw,resolved);compiled=compile_operationalization_recompiles(plan,payload,part=1,recompiler_model=resolved);_record_memory_receipt(compiled,stage="evidence-recompile",part=1,pack=memory_pack)
        errors=validate_evidence_plan(compiled)
        if errors:raise ValueError("compiled canonical Pre-F0 operationalization recompile invalid: "+",".join(errors))
        transport=_provider_success_metadata(run_root=run_root,stem="evidence-recompile-p1",response=res);artifact={"schema_version":SCHEMA_VERSION,"generated_at":_now(),"stage":"evidence-recompile","input_control_snapshot_sha256":input_control,"input_plan_sha256":str(control.get("plan_sha256") or ""),"candidate_ids":candidate_ids,"candidate_snapshot_sha256s":list(control.get("candidate_snapshot_sha256s") or []),"support_inventory_sha256":str(control.get("support_inventory_sha256") or ""),"research_memory_query_pack_sha256":str(memory_pack.get("query_pack_sha256") or ""),"research_memory_query_pack_file_sha256":_sha_path(memory_path),"requested_model":requested,"resolved_model":resolved,"raw_sha256":raw_sha,"raw_archived_before_parse":True,**transport,"scientific_authority":False,"authority":dict(AUTHORITY)}
        success_path.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");plan_path.write_text(json.dumps(compiled,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");output_control=control_snapshot(queue_path=queue_path,support_path=support_path,plan_path=plan_path);public=_public_state(plan=compiled,control=output_control,last_stage=artifact);public["parent_control_snapshot_sha256"]=input_control;_write_public(public,json_path,js_path);return public


def review(*,storage:StorageSettings|None=None,queue_path:Path=DEFAULT_QUEUE_JSON,support_path:Path=DEFAULT_SUPPORT_JSON,plan_path:Path=DEFAULT_PLAN_JSON,json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS,model:str=PREMIUM_AUTO) -> dict[str,Any]:
    storage=storage or StorageSettings.from_env();storage.ensure()
    with _execution_lock(storage):
        plan=_load(plan_path);control=control_snapshot(queue_path=queue_path,support_path=support_path,plan_path=plan_path)
        if str(plan.get("status") or "")!="EVIDENCE_REVIEW_PENDING" or int((plan.get("summary") or {}).get("review_pending") or 0)<=0:raise ValueError("canonical Pre-F0 evidence control has no independent review pending")
        pending=[row for row in plan.get("entries") or [] if isinstance(row,dict) and row.get("status")=="NEEDS_INDEPENDENT_EVIDENCE_REVIEW"]
        if len(pending)!=1:raise ValueError("canonical Pre-F0 evidence review currently requires exactly one pending contract")
        design_model=str((pending[0].get("design_provenance") or {}).get("resolved_model") or "").strip()
        if not design_model:raise ValueError("canonical Pre-F0 evidence review requires designer/recompiler resolved-model provenance")
        if str(model or "").strip() in {"",PREMIUM_AUTO}:requested=independent_priority("evidence_review",exclude_resolved=design_model)[0]
        else:
            requested=preferred_model("evidence_review",model)
            if requested==design_model:raise ValueError("canonical Pre-F0 evidence reviewer request must differ from design resolved model")
        input_control=str(control["control_snapshot_sha256"]);run_root=storage.data_root/"paper-first-pre-f0-evidence"/input_control;success_path=run_root/"evidence-review-p1.json"
        if success_path.is_file():raise ValueError("canonical Pre-F0 evidence review already completed for this input control")
        run_root.mkdir(parents=True,exist_ok=True);prompt,candidate_ids=evidence_review_prompt(plan,part=1,batch_size=1)
        res=_ark_with_provider_receipt(run_root=run_root,stem="evidence-review-p1",requested_model=requested,context={"part":1,"candidate_ids":candidate_ids,"control_snapshot_sha256":input_control},prompt=prompt,max_output_tokens=4200,temperature=0.0,stage="evidence_review")
        raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or requested);payload,raw_sha=_parse_archived_evidence_design_json(run_root,"evidence-review-p1",raw,resolved);compiled=compile_evidence_reviews(plan,payload,part=1,reviewer_model=resolved)
        errors=validate_evidence_plan(compiled)
        if errors:raise ValueError("compiled canonical Pre-F0 evidence review invalid: "+",".join(errors))
        transport=_provider_success_metadata(run_root=run_root,stem="evidence-review-p1",response=res);artifact={"schema_version":SCHEMA_VERSION,"generated_at":_now(),"stage":"evidence-review","input_control_snapshot_sha256":input_control,"input_plan_sha256":str(control.get("plan_sha256") or ""),"candidate_ids":candidate_ids,"candidate_snapshot_sha256s":list(control.get("candidate_snapshot_sha256s") or []),"support_inventory_sha256":str(control.get("support_inventory_sha256") or ""),"design_resolved_model":design_model,"requested_model":requested,"resolved_model":resolved,"raw_sha256":raw_sha,"raw_archived_before_parse":True,**transport,"scientific_authority":False,"authority":dict(AUTHORITY)}
        success_path.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");plan_path.write_text(json.dumps(compiled,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");output_control=control_snapshot(queue_path=queue_path,support_path=support_path,plan_path=plan_path);public=_public_state(plan=compiled,control=output_control,last_stage=artifact);public["parent_control_snapshot_sha256"]=input_control;_write_public(public,json_path,js_path);return public



def substrate_preflight(*,receipt_payload:dict[str,Any],storage:StorageSettings|None=None,queue_path:Path=DEFAULT_QUEUE_JSON,support_path:Path=DEFAULT_SUPPORT_JSON,plan_path:Path=DEFAULT_PLAN_JSON,json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS) -> dict[str,Any]:
    """Compile one bounded substrate receipt into the canonical Pre-F0 evidence plan.

    This stage is deliberately provider-free and outcome-free.  It may only
    authorize the already-reviewed minimal-harness implementation or bounded
    evidence-acquisition route encoded by ``compile_substrate_preflight``.
    """
    storage=storage or StorageSettings.from_env();storage.ensure()
    with _execution_lock(storage):
        plan=_load(plan_path);control=control_snapshot(queue_path=queue_path,support_path=support_path,plan_path=plan_path)
        if str(plan.get("status") or "")!="EVIDENCE_SUBSTRATE_PREFLIGHT_PENDING" or int((plan.get("summary") or {}).get("substrate_preflight_pending") or 0)<=0:
            raise ValueError("canonical Pre-F0 evidence control has no substrate preflight pending")
        request=build_substrate_preflight_request(plan);candidate_ids=[str(r.get("candidate_id") or "") for r in request.get("rows") or [] if isinstance(r,dict)]
        if not candidate_ids:raise ValueError("canonical Pre-F0 substrate preflight request is empty")
        input_control=str(control["control_snapshot_sha256"]);run_root=storage.data_root/"paper-first-pre-f0-evidence"/input_control;success_path=run_root/"substrate-preflight.json"
        if success_path.is_file():raise ValueError("canonical Pre-F0 substrate preflight already completed for this input control")
        run_root.mkdir(parents=True,exist_ok=True)
        request_path=run_root/"substrate-preflight-request.json";request_path.write_text(json.dumps(request,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        receipt_path=run_root/"substrate-preflight-receipt.json";receipt_path.write_text(json.dumps(receipt_payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        compiled=compile_substrate_preflight(plan,receipt_payload);errors=validate_evidence_plan(compiled)
        if errors:raise ValueError("compiled canonical Pre-F0 substrate preflight invalid: "+",".join(errors))
        artifact={"schema_version":SCHEMA_VERSION,"generated_at":_now(),"stage":"substrate-preflight","input_control_snapshot_sha256":input_control,"input_plan_sha256":str(control.get("plan_sha256") or ""),"candidate_ids":candidate_ids,"candidate_snapshot_sha256s":list(control.get("candidate_snapshot_sha256s") or []),"support_inventory_sha256":str(control.get("support_inventory_sha256") or ""),"request_sha256":_sha_path(request_path),"receipt_sha256":_sha_path(receipt_path),"provider_calls_executed":0,"gpu_calls_executed":0,"outcome_reads_executed":0,"scientific_authority":False,"authority":dict(AUTHORITY)}
        success_path.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");plan_path.write_text(json.dumps(compiled,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        output_control=control_snapshot(queue_path=queue_path,support_path=support_path,plan_path=plan_path);public=_public_state(plan=compiled,control=output_control,last_stage=artifact);public["parent_control_snapshot_sha256"]=input_control;_write_public(public,json_path,js_path);return public


def harness_implementation(*,receipt_payload:dict[str,Any],storage:StorageSettings|None=None,queue_path:Path=DEFAULT_QUEUE_JSON,support_path:Path=DEFAULT_SUPPORT_JSON,plan_path:Path=DEFAULT_PLAN_JSON,json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS) -> dict[str,Any]:
    """Compile a verified run-local harness implementation receipt.

    Harness implementation is provider-free and result-free.  A passing receipt
    may authorize only bounded evidence acquisition for the already-reviewed
    contract; it never carries scientific, Problem-Gate, P0, or GPU authority.
    """
    storage=storage or StorageSettings.from_env();storage.ensure()
    with _execution_lock(storage):
        plan=_load(plan_path);control=control_snapshot(queue_path=queue_path,support_path=support_path,plan_path=plan_path)
        if str(plan.get("status") or "")!="EVIDENCE_HARNESS_IMPLEMENTATION_PENDING" or int((plan.get("summary") or {}).get("substrate_implementation_pending") or 0)<=0:
            raise ValueError("canonical Pre-F0 evidence control has no minimal harness implementation pending")
        pending=[r for r in plan.get("entries") or [] if isinstance(r,dict) and r.get("status")=="NEEDS_MINIMAL_HARNESS_IMPLEMENTATION"]
        candidate_ids=[str(r.get("candidate_id") or "") for r in pending]
        if not candidate_ids:raise ValueError("canonical Pre-F0 harness implementation request is empty")
        input_control=str(control["control_snapshot_sha256"]);run_root=storage.data_root/"paper-first-pre-f0-evidence"/input_control;success_path=run_root/"harness-implementation.json"
        if success_path.is_file():raise ValueError("canonical Pre-F0 harness implementation already completed for this input control")
        run_root.mkdir(parents=True,exist_ok=True)
        receipt_path=run_root/"harness-implementation-receipt.json";receipt_path.write_text(json.dumps(receipt_payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        compiled=compile_harness_implementation_receipts(plan,receipt_payload);errors=validate_evidence_plan(compiled)
        if errors:raise ValueError("compiled canonical Pre-F0 harness implementation invalid: "+",".join(errors))
        artifact={"schema_version":SCHEMA_VERSION,"generated_at":_now(),"stage":"harness-implementation","input_control_snapshot_sha256":input_control,"input_plan_sha256":str(control.get("plan_sha256") or ""),"candidate_ids":candidate_ids,"candidate_snapshot_sha256s":list(control.get("candidate_snapshot_sha256s") or []),"support_inventory_sha256":str(control.get("support_inventory_sha256") or ""),"receipt_sha256":_sha_path(receipt_path),"provider_calls_executed":0,"gpu_calls_executed":0,"scientific_outcome_calls_executed":0,"scientific_authority":False,"authority":dict(AUTHORITY)}
        success_path.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");plan_path.write_text(json.dumps(compiled,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        output_control=control_snapshot(queue_path=queue_path,support_path=support_path,plan_path=plan_path);public=_public_state(plan=compiled,control=output_control,last_stage=artifact);public["parent_control_snapshot_sha256"]=input_control;_write_public(public,json_path,js_path);return public

def load_public(path:Path=DEFAULT_JSON) -> dict[str,Any]:
    try:return _load(path)
    except (OSError,json.JSONDecodeError,ValueError):return {"schema_version":SCHEMA_VERSION,"status":"NOT_RUN","policy":dict(POLICY),"summary":{},"scientific_authority":False,"authority":dict(AUTHORITY)}
