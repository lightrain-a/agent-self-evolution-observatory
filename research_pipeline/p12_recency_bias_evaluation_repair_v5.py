from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from .api_memory_store import database_path, connect
from .api_research_memory import record_parsed_api_output
from .p12_recency_bias_execute import _call_once, _close_parse_failure
from .p12_recency_bias_harness import CANDIDATE_ID, CONTRACT_SHA256, EXECUTOR_MODEL, adjudicate_rollouts, answer_tool, rollout_prompt, sha_json
from .p12_recency_bias_protocol import authorization_ok, load_json, lock_output, parse_single_integer, sha_bytes, sha_text, write_json
from .paper_first_evidence_acquisition import compile_harness_runtime_repair_receipts, validate_evidence_plan

FAILURE_V4_FILENAME="runtime-failure-manifest-v4.json"
REVOKED_V4_FILENAME="authorization-revoked-plan-v4.json"
OLD_MANIFEST_V4_FILENAME="harness-implementation-manifest-v4.json"
REPAIR_PLAN_V5_FILENAME="runtime-repair-plan-v5.json"
OFFLINE_PROBE_V5_FILENAME="runtime-repair-offline-probe-v5.json"
TRANSPORT_PROBE_V5_FILENAME="runtime-transport-probe-v5.json"
PROTOCOL_REVIEW_V5_FILENAME="runtime-protocol-review-v5.json"
MANIFEST_V5_FILENAME="harness-implementation-manifest-v5.json"
REPAIR_RECEIPT_V5_FILENAME="runtime-repair-receipt-v5.json"
AUTHORIZATION_V5_FILENAME="authorization-repaired-plan-v5.json"
FAILED_UNIT="E-CYCLIC3-2-F-L8-R"
OLD_RETURN_SENTENCE="Return exactly one integer answer through the supplied function."
ANSWER_RE=re.compile(r"^P12_ANSWER=([-+]?\d+)$")
MAX_OUTPUT_TOKENS=500
REPLACEMENT_PROVIDER_CALL_CAP=94
FROZEN_MAX_MODEL_CALLS=192
PROTOCOL_VERSION="P12_EVALUATION_ANSWER_FIRST_V5"


def answer_first_prompt(unit: dict[str,Any]) -> str:
    base=rollout_prompt(unit)
    if not base.endswith(OLD_RETURN_SENTENCE): raise RuntimeError("frozen rollout prompt return sentence drift")
    replacement="Response protocol only: before any reasoning, emit exactly one first line P12_ANSWER=<integer>. The supplied function may also be called and takes priority. Do not change the task interpretation."
    return base[:-len(OLD_RETURN_SENTENCE)]+replacement


def scientific_prompt_body(prompt: str) -> str:
    if OLD_RETURN_SENTENCE in prompt: return prompt.split(OLD_RETURN_SENTENCE,1)[0]
    marker="Response protocol only: before any reasoning"
    if marker in prompt: return prompt.split(marker,1)[0]
    raise ValueError("unrecognized P12 rollout protocol")


def parse_answer_v5(archive: dict[str,Any]) -> tuple[int,str]:
    try: return parse_single_integer(archive)
    except ValueError: pass
    first=next((line.strip() for line in str(archive.get("text") or "").splitlines() if line.strip()),"")
    match=ANSWER_RE.fullmatch(first)
    if not match: raise ValueError("v5 answer-first fallback requires exact first-line P12_ANSWER")
    return int(match.group(1)),"ANSWER_FIRST_TEXT"


def _manifest_units(run_root: Path) -> list[dict[str,Any]]:
    return list(load_json(run_root/"rollout-manifest.json")["units"])


def build_repair_plan(run_root: Path) -> dict[str,Any]:
    failure=load_json(run_root/FAILURE_V4_FILENAME);old=load_json(run_root/OLD_MANIFEST_V4_FILENAME);units=_manifest_units(run_root)
    completed=[];failed=[];unstarted=[]
    for unit in units:
        path=run_root/"units"/f"{unit['unit_id']}.json"
        if not path.is_file(): unstarted.append(unit["unit_id"]);continue
        row=load_json(path)
        if row.get("status")=="UNIT_COMPLETE": completed.append(unit["unit_id"])
        else: failed.append(unit["unit_id"])
    if failed!=[FAILED_UNIT]: raise RuntimeError(f"unexpected failed evaluation set:{failed}")
    if len(completed)!=2 or len(unstarted)!=93: raise RuntimeError(f"unexpected opened evaluation state completed={len(completed)} unstarted={len(unstarted)}")
    failed_index=next(i for i,u in enumerate(units) if u["unit_id"]==FAILED_UNIT)
    if failed_index!=2 or [u["unit_id"] for u in units[:2]]!=completed: raise RuntimeError("frozen rollout prefix drift")
    bindings={}
    for unit in units[2:]:
        base=rollout_prompt(unit);new=answer_first_prompt(unit)
        bindings[unit["unit_id"]]={"old_prompt_sha256":sha_text(base),"new_prompt_sha256":sha_text(new),"scientific_prompt_body_sha256":sha_text(scientific_prompt_body(base)),"scientific_prompt_body_unchanged":scientific_prompt_body(base)==scientific_prompt_body(new)}
    execution_order=[FAILED_UNIT,*unstarted]
    core={"schema_version":"1.0","status":"P12_EVALUATION_RUNTIME_REPAIR_PLAN_V5","candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"failure_manifest_sha256":failure["failure_manifest_sha256"],"replaces_harness_manifest_sha256":old["harness_manifest_sha256"],"protocol_version":PROTOCOL_VERSION,"protocol_only_change":True,"scientific_object_unchanged":True,"reuse_completed_units":completed,"retry_failed_unit":{"unit_id":FAILED_UNIT,"max_attempts":1},"unstarted_units":unstarted,"execution_order":execution_order,"prompt_bindings":bindings,"model_unchanged":True,"temperature_unchanged":True,"tool_schema_unchanged":True,"max_output_tokens_unchanged":True,"frozen_rollout_order_unchanged":True,"analysis_split_thresholds_unchanged":True,"provider_calls_already_charged":int(failure["provider_calls_charged"]),"remaining_model_call_budget_before_repair":int(failure["remaining_model_call_budget"]),"replacement_provider_call_cap":REPLACEMENT_PROVIDER_CALL_CAP,"scientific_authority":False,"belief_authority":False}
    core["replacement_harness_plan_sha256"]=sha_json(core);return core


def run_offline_probe(run_root: Path) -> dict[str,Any]:
    output=run_root/OFFLINE_PROBE_V5_FILENAME;lock=lock_output(output,{"stage":"p12-evaluation-repair-offline-v5"})
    try:
        plan=build_repair_plan(run_root)
        call={"function_calls":[{"name":"submit_p12_answer","arguments":json.dumps({"answer":7})}],"text":"P12_ANSWER=3"};text={"function_calls":[],"text":"P12_ANSWER=-12\nreasoning"}
        checks={"all_remaining_bodies_unchanged":all(x["scientific_prompt_body_unchanged"] for x in plan["prompt_bindings"].values()),"reuse_exact_two_completed":len(plan["reuse_completed_units"])==2,"retry_exact_failed_once":plan["retry_failed_unit"]=={"unit_id":FAILED_UNIT,"max_attempts":1},"unstarted_exact_93":len(plan["unstarted_units"])==93,"execution_order_exact_94":len(plan["execution_order"])==94 and plan["execution_order"][0]==FAILED_UNIT,"function_call_preferred":parse_answer_v5(call)==(7,"FUNCTION_CALL"),"answer_first_fallback":parse_answer_v5(text)==(-12,"ANSWER_FIRST_TEXT"),"total_calls_108_within_192":plan["provider_calls_already_charged"]+plan["replacement_provider_call_cap"]==108<=FROZEN_MAX_MODEL_CALLS}
        result={"schema_version":"1.0","status":"P12_EVALUATION_RUNTIME_REPAIR_OFFLINE_V5_PASS" if all(checks.values()) else "P12_EVALUATION_RUNTIME_REPAIR_OFFLINE_V5_FAIL","checks":checks,"replacement_harness_plan_sha256":plan["replacement_harness_plan_sha256"],"scientific_authority":False,"belief_authority":False};result["offline_probe_sha256"]=sha_json(result);write_json(run_root/REPAIR_PLAN_V5_FILENAME,plan);write_json(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def run_neutral_transport_probe(run_root: Path,persistent_root: Path) -> dict[str,Any]:
    from .p12_recency_bias_protocol import client,provider_archive_payload
    from .api_research_memory import record_raw_api_output
    output=run_root/TRANSPORT_PROBE_V5_FILENAME;lock=lock_output(output,{"stage":"p12-evaluation-transport-v5"})
    try:
        prompt="Neutral response-protocol probe. Before any reasoning, first line must be exactly P12_ANSWER=11. The trivial integer answer is 5+6. No scientific task, skill, retrieval condition, or evaluation data is present."
        provider_root=persistent_root/"runs"/f"p12-neutral-eval-answer-{sha_text(PROTOCOL_VERSION)[:10]}";provider_root.mkdir(parents=True,exist_ok=True)
        response=client().respond(prompt,model=EXECUTOR_MODEL,max_output_tokens=120,temperature=0.0,thinking="disabled",store=True);archive=provider_archive_payload(response);raw=provider_root/"raw-eval-answer-first.json";raw.write_text(json.dumps(archive,ensure_ascii=False,sort_keys=True,separators=(",",":")),encoding="utf-8");psha=sha_text(prompt);arch=record_raw_api_output(run_root=provider_root,stage="p12-eval-answer-transport-v5",raw_path=raw,requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],request_fingerprint=sha_json({"stage":"p12-eval-answer-transport-v5","prompt_sha256":psha}),prompt_sha256=psha,root=persistent_root);answer,source=parse_answer_v5(archive);passed=answer==11 and source=="ANSWER_FIRST_TEXT";result={"schema_version":"1.0","status":"P12_EVALUATION_RUNTIME_TRANSPORT_V5_PASS" if passed else "P12_EVALUATION_RUNTIME_TRANSPORT_V5_FAIL","raw_sha256":arch["raw_sha256"],"response_id_archived":bool(archive.get("response_id")),"answer_source":source,"answer":answer,"scientific_authority":False,"belief_authority":False};result["transport_probe_sha256"]=sha_json(result);record_parsed_api_output(run_root=provider_root,stage="p12-eval-answer-transport-v5",raw_sha256=arch["raw_sha256"],structured_payload=result,requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],research_objects=[],root=persistent_root);write_json(output,result);return result
    finally:
        if output.exists():lock.unlink(missing_ok=True)


def authorize_v5(run_root: Path) -> dict[str,Any]:
    output=run_root/AUTHORIZATION_V5_FILENAME;lock=lock_output(output,{"stage":"p12-evaluation-authorize-v5"})
    try:
        revoked=load_json(run_root/REVOKED_V4_FILENAME);failure=load_json(run_root/FAILURE_V4_FILENAME);old=load_json(run_root/OLD_MANIFEST_V4_FILENAME);plan=load_json(run_root/REPAIR_PLAN_V5_FILENAME);offline=load_json(run_root/OFFLINE_PROBE_V5_FILENAME);transport=load_json(run_root/TRANSPORT_PROBE_V5_FILENAME);review=load_json(run_root/PROTOCOL_REVIEW_V5_FILENAME)
        if offline.get("status")!="P12_EVALUATION_RUNTIME_REPAIR_OFFLINE_V5_PASS" or transport.get("status")!="P12_EVALUATION_RUNTIME_TRANSPORT_V5_PASS": raise RuntimeError("P12 v5 probes not PASS")
        if review.get("verdict")!="CLEAR_PROTOCOL_EQUIVALENCE" or review.get("reviewer_independent") is not True: raise RuntimeError("P12 v5 independent review not CLEAR")
        base=Path(__file__).parent;names=("p12_recency_bias_harness.py","p12_recency_bias_protocol.py","p12_recency_bias_execute.py","p12_recency_bias_evaluation_repair_v5.py")
        manifest={"schema_version":"1.0","status":"P12_EVALUATION_RUNTIME_REPAIR_HARNESS_V5_PASS","candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"failure_manifest_sha256":failure["failure_manifest_sha256"],"replaces_harness_manifest_sha256":old["harness_manifest_sha256"],"replacement_harness_plan_sha256":plan["replacement_harness_plan_sha256"],"offline_probe_sha256":offline["offline_probe_sha256"],"transport_probe_sha256":transport["transport_probe_sha256"],"protocol_review_sha256":review["review_sha256"],"code_sha256":{n:sha_bytes((base/n).read_bytes()) for n in names},"replacement_provider_call_cap":REPLACEMENT_PROVIDER_CALL_CAP,"sandboxed":True,"probe_passed":True,"budget_feasible":True,"scientific_object_unchanged":True,"protocol_only_change":True,"scientific_authority":False,"belief_authority":False};manifest["harness_manifest_sha256"]=sha_json(manifest);write_json(run_root/MANIFEST_V5_FILENAME,manifest)
        receipt={"schema_version":"1.0","scientific_authority":False,"receipts":[{"candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"failure_manifest_sha256":failure["failure_manifest_sha256"],"replaces_harness_manifest_sha256":old["harness_manifest_sha256"],"replacement_harness_plan_sha256":plan["replacement_harness_plan_sha256"],"harness_manifest_sha256":manifest["harness_manifest_sha256"],"implementation_summary":"P12 v5 evaluation response-protocol only: reuse the two valid frozen evaluation receipts; retry the one protocol-failed unit once; execute all 93 never-started units in the original frozen manifest order. Task prompts/skills/retrieval/truth/Kimi/temperature/tool schema/500-token cap/analysis split and thresholds are unchanged; only require P12_ANSWER=<integer> on the first response line before optional reasoning, with function-call priority.","sandboxed":True,"probe_passed":True,"budget_feasible":True,"scientific_object_unchanged":True,"protocol_only_change":True,"replacement_provider_call_cap":REPLACEMENT_PROVIDER_CALL_CAP}]};write_json(run_root/REPAIR_RECEIPT_V5_FILENAME,receipt);repaired=compile_harness_runtime_repair_receipts(revoked,receipt);errors=validate_evidence_plan(repaired)
        if errors: raise ValueError(f"P12 v5 authorization invalid:{errors}")
        write_json(output,repaired);row=next(x for x in repaired["entries"] if x.get("candidate_id")==CANDIDATE_ID);return {"status":"P12_EVALUATION_RUNTIME_REPAIR_V5_AUTHORIZED","execution_authorized":row["execution_authorized"],"harness_manifest_sha256":manifest["harness_manifest_sha256"],"replacement_harness_plan_sha256":plan["replacement_harness_plan_sha256"],"scientific_authority":False}
    finally:
        if output.exists():lock.unlink(missing_ok=True)


def _v5_run_id(run_root: Path,unit_id: str) -> str:
    manifest=load_json(run_root/MANIFEST_V5_FILENAME);return f"p12-recency-{manifest['harness_manifest_sha256'][:10]}-unit-{unit_id.lower()}"


def _v5_calls_used(run_root: Path,persistent_root: Path) -> int:
    manifest=load_json(run_root/MANIFEST_V5_FILENAME);prefix=f"p12-recency-{manifest['harness_manifest_sha256'][:10]}-unit-";db=database_path(root=persistent_root)
    if not db.is_file(): return 0
    with connect(db) as connection: rows=connection.execute("SELECT provider_calls_executed FROM api_calls WHERE run_id LIKE ?",(prefix+"%",)).fetchall()
    return sum(int(r["provider_calls_executed"] or 0) for r in rows)


def execute_unit_v5(run_root: Path,persistent_root: Path,unit_id: str) -> dict[str,Any]:
    authorization_ok(run_root);lock_state=load_json(run_root/"pre-evaluation-lock.json")
    if lock_state.get("status")!="P12_PRE_EVALUATION_LOCK_PASS" or lock_state.get("evaluation_authorized_by_lock") is not True: raise RuntimeError("P12 pre-evaluation lock not PASS")
    plan=load_json(run_root/REPAIR_PLAN_V5_FILENAME);allowed=set(plan["execution_order"])
    if unit_id not in allowed: raise ValueError(f"P12 v5 unit not authorized:{unit_id}")
    output=run_root/"units-v5"/f"{unit_id}.json";lock=lock_output(output,{"stage":"p12-evaluation-v5","unit_id":unit_id})
    try:
        if _v5_calls_used(run_root,persistent_root)>=REPLACEMENT_PROVIDER_CALL_CAP: raise RuntimeError("P12 v5 provider-call cap exhausted")
        unit=next(x for x in _manifest_units(run_root) if x["unit_id"]==unit_id);run_id=_v5_run_id(run_root,unit_id);archive,failure=_call_once(persistent_root=persistent_root,run_id=run_id,stage="p12-evaluation-unit-v5",prompt=answer_first_prompt(unit),tools=answer_tool(),max_output_tokens=MAX_OUTPUT_TOKENS)
        if archive is None: result={"schema_version":"1.0","status":"UNIT_PROVIDER_FAILURE","unit_id":unit_id,**failure};write_json(output,result);return result
        try: answer,source=parse_answer_v5(archive)
        except Exception as error:
            _close_parse_failure(persistent_root=persistent_root,archive=archive,stage="p12-evaluation-unit-v5",error=error);result={"schema_version":"1.0","status":"UNIT_PROTOCOL_FAILURE","unit_id":unit_id,"raw_sha256":archive["raw_sha256"],"error":f"{type(error).__name__}:{error}","scientific_authority":False,"belief_authority":False};write_json(output,result);return result
        result={"schema_version":"1.0","status":"UNIT_COMPLETE","unit_id":unit_id,"task_id":unit["task_id"],"scenario_id":unit["scenario_id"],"family":unit["family"],"phase":unit["phase"],"library_stage":unit["library_stage"],"recency_policy":unit["recency_policy"],"retrieval_query_sha256":unit["retrieval_query_sha256"],"selected_skill_ids":unit["selected_skill_ids"],"selected_static_similarities":unit["selected_static_similarities"],"answer":answer,"truth":unit["answer"],"task_success":answer==unit["answer"],"answer_source":source,"raw_sha256":archive["raw_sha256"],"resolved_model":archive["resolved_model"],"usage":archive["usage"],"valid_execution":True,"runtime_repair_v5":True,"scientific_authority":False,"belief_authority":False};result["unit_receipt_sha256"]=sha_json(result);record_parsed_api_output(run_root=persistent_root/"runs"/run_id,stage="p12-evaluation-unit-v5",raw_sha256=archive["raw_sha256"],structured_payload=result,requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],research_objects=[],root=persistent_root);write_json(output,result);return result
    finally:
        if output.exists():lock.unlink(missing_ok=True)


def pending_units_v5(run_root: Path) -> list[str]:
    plan=load_json(run_root/REPAIR_PLAN_V5_FILENAME);return [uid for uid in plan["execution_order"] if not (run_root/"units-v5"/f"{uid}.json").is_file()]


def run_batch(run_root: Path,persistent_root: Path,limit: int=8) -> dict[str,Any]:
    completed=[]
    for uid in pending_units_v5(run_root)[:max(0,int(limit))]:
        result=execute_unit_v5(run_root,persistent_root,uid);completed.append({"unit_id":uid,"status":result.get("status"),"task_success":result.get("task_success")})
        if result.get("status")!="UNIT_COMPLETE": break
    pending=pending_units_v5(run_root);return {"schema_version":"1.0","status":"P12_V5_ROLLOUT_PROGRESS","completed":completed,"pending_count":len(pending),"next_units":pending[:8],"scientific_authority":False,"belief_authority":False}


def combined_receipts(run_root: Path) -> list[dict[str,Any]]:
    out=[]
    for unit in _manifest_units(run_root):
        v5=run_root/"units-v5"/f"{unit['unit_id']}.json";old=run_root/"units"/f"{unit['unit_id']}.json"
        if v5.is_file() and load_json(v5).get("status")=="UNIT_COMPLETE": out.append(load_json(v5))
        elif old.is_file() and load_json(old).get("status")=="UNIT_COMPLETE": out.append(load_json(old))
    return out


def finalize_v5(run_root: Path) -> dict[str,Any]:
    output=run_root/"adjudication-v5.json";lock=lock_output(output,{"stage":"p12-finalize-v5"})
    try:
        lock_state=load_json(run_root/"pre-evaluation-lock.json");receipts=combined_receipts(run_root);result=adjudicate_rollouts(receipts,lock_state["difficulty_summary"]);result["skill_library_sha256"]=lock_state["skill_library_sha256"];result["rollout_manifest_sha256"]=lock_state["rollout_manifest_sha256"];result["protocol_version"]=PROTOCOL_VERSION;result["original_valid_receipts_reused"]=sum(1 for u in _manifest_units(run_root) if (run_root/"units"/f"{u['unit_id']}.json").is_file() and load_json(run_root/"units"/f"{u['unit_id']}.json").get("status")=="UNIT_COMPLETE");result["v5_valid_receipts"]=sum(1 for u in _manifest_units(run_root) if (run_root/"units-v5"/f"{u['unit_id']}.json").is_file() and load_json(run_root/"units-v5"/f"{u['unit_id']}.json").get("status")=="UNIT_COMPLETE");result["adjudication_sha256"]=sha_json({k:v for k,v in result.items() if k!="adjudication_sha256"});write_json(output,result);return result
    finally:
        if output.exists():lock.unlink(missing_ok=True)


def main() -> None:
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=("offline-probe","transport-probe","authorize","unit","batch","finalize"));p.add_argument("--run-root",type=Path,required=True);p.add_argument("--persistent-root",type=Path);p.add_argument("--unit-id");p.add_argument("--limit",type=int,default=8);a=p.parse_args()
    if a.cmd=="offline-probe":out=run_offline_probe(a.run_root)
    elif a.cmd=="transport-probe":
        if a.persistent_root is None:raise SystemExit('--persistent-root required')
        out=run_neutral_transport_probe(a.run_root,a.persistent_root)
    elif a.cmd=="authorize":out=authorize_v5(a.run_root)
    elif a.cmd=="unit":
        if a.persistent_root is None or not a.unit_id:raise SystemExit('--persistent-root and --unit-id required')
        out=execute_unit_v5(a.run_root,a.persistent_root,a.unit_id)
    elif a.cmd=="batch":
        if a.persistent_root is None:raise SystemExit('--persistent-root required')
        out=run_batch(a.run_root,a.persistent_root,a.limit)
    else:out=finalize_v5(a.run_root)
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=="__main__":main()
