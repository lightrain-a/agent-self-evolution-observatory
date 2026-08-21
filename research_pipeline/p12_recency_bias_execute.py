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
from .p12_recency_bias_harness import (
    CANDIDATE_ID,
    CONTRACT_SHA256,
    EXECUTOR_MODEL,
    PROVIDER_CALL_CAP,
    adjudicate_rollouts,
    answer_tool,
    canonical_json,
    difficulty_calibration_pairs,
    difficulty_prompt,
    difficulty_summary,
    difficulty_tool,
    rank_skills,
    retrieval_pairing_checks,
    retrieval_text,
    rollout_prompt,
    rollout_units,
    sha_json,
    sha_text,
    skill_calibration_bundles,
    skill_compilation_prompt,
    skill_tool,
    validate_frozen_skills,
)
from .p12_recency_bias_protocol import (
    authorization_ok,
    client,
    load_json,
    lock_output,
    parse_difficulty_answers,
    parse_single_integer,
    parse_skills,
    provider_archive_payload,
    write_json,
)


def _prefix(run_root: Path) -> str:
    _,manifest=authorization_ok(run_root)
    return f"p12-recency-{manifest['harness_manifest_sha256'][:10]}-"


def _current_call_cap(run_root: Path) -> tuple[int,int]:
    plan,_=authorization_ok(run_root);row=next(x for x in plan["entries"] if x.get("candidate_id")==CANDIDATE_ID)
    repair=row.get("harness_runtime_repair") or {}
    if repair:
        return int(repair["replacement_provider_call_cap"]),int(repair["provider_calls_already_charged"])
    return PROVIDER_CALL_CAP,0


def _recorded_calls(persistent_root: Path,prefix: str) -> tuple[int,set[str]]:
    db=database_path(root=persistent_root)
    if not db.is_file(): return 0,set()
    with connect(db) as connection:
        rows=connection.execute("SELECT run_id,provider_calls_executed FROM api_calls WHERE run_id LIKE ?",(prefix+"%",)).fetchall()
    return sum(int(row["provider_calls_executed"] or 0) for row in rows),{str(row["run_id"]) for row in rows}


def _call_once(*,persistent_root: Path,run_id: str,stage: str,prompt: str,tools: list[dict[str,Any]],max_output_tokens: int) -> tuple[dict[str,Any] | None,dict[str,Any]]:
    provider_root=persistent_root/"runs"/run_id;provider_root.mkdir(parents=True,exist_ok=True);psha=sha_text(prompt)
    try:
        response=client().respond(prompt,model=EXECUTOR_MODEL,max_output_tokens=max_output_tokens,temperature=0.0,tools=tools,thinking="disabled",store=True)
    except Exception as error:
        fp=sha_json({"stage":stage,"run_id":run_id,"error":str(error)[:500],"prompt_sha256":psha});receipt=record_provider_failure(run_root=provider_root,stage=stage,payload={"status":"PROVIDER_ERROR_ZERO_AUTHORITY","requested_model":EXECUTOR_MODEL,"error_fingerprint":fp,"prompt_sha256":psha},root=persistent_root)
        return None,{"status":"PROVIDER_FAILURE","error":f"{type(error).__name__}:{str(error)[:1000]}","provider_failure":receipt,"scientific_authority":False,"belief_authority":False}
    archive=provider_archive_payload(response);raw_file=provider_root/"raw-response.json";raw_file.write_text(canonical_json(archive),encoding="utf-8");arch=record_raw_api_output(run_root=provider_root,stage=stage,raw_path=raw_file,requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],request_fingerprint=sha_json({"stage":stage,"run_id":run_id,"prompt_sha256":psha}),prompt_sha256=psha,root=persistent_root)
    archive["raw_sha256"]=arch["raw_sha256"];archive["prompt_sha256"]=psha;archive["provider_run_id"]=run_id
    return archive,{"status":"RAW_ARCHIVED","raw_sha256":arch["raw_sha256"]}


def _close_parse_failure(*,persistent_root: Path,archive: dict[str,Any],stage: str,error: Exception) -> None:
    record_archived_api_parse_failure(run_root=persistent_root/"runs"/archive["provider_run_id"],stage=stage,raw_sha256=archive["raw_sha256"],error=f"{type(error).__name__}:{error}",requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],root=persistent_root)


def execute_difficulty_pair(*,run_root: Path,persistent_root: Path,pair_id: str) -> dict[str,Any]:
    authorization_ok(run_root);pairs={row["pair_id"]:row for row in difficulty_calibration_pairs()}
    if pair_id not in pairs: raise ValueError(pair_id)
    output=run_root/"difficulty"/f"{pair_id}.json";lock=lock_output(output,{"stage":"difficulty","pair_id":pair_id})
    prefix=_prefix(run_root);run_id=prefix+"difficulty-"+pair_id.lower()
    try:
        used,run_ids=_recorded_calls(persistent_root,prefix)
        if run_id in run_ids: raise RuntimeError(f"provider call already recorded:{run_id}")
        current_cap,_=_current_call_cap(run_root)
        if used>=current_cap: raise RuntimeError("P12 provider-call cap exhausted")
        pair=pairs[pair_id];prompt=difficulty_prompt(pair);archive,failure=_call_once(persistent_root=persistent_root,run_id=run_id,stage="p12-difficulty-calibration",prompt=prompt,tools=difficulty_tool(),max_output_tokens=600)
        if archive is None: result={"schema_version":"1.0","status":"DIFFICULTY_PROVIDER_FAILURE","pair_id":pair_id,**failure};write_json(output,result);return result
        try: answers,source=parse_difficulty_answers(archive)
        except Exception as error:
            _close_parse_failure(persistent_root=persistent_root,archive=archive,stage="p12-difficulty-calibration",error=error);result={"schema_version":"1.0","status":"DIFFICULTY_PROTOCOL_FAILURE","pair_id":pair_id,"raw_sha256":archive["raw_sha256"],"error":f"{type(error).__name__}:{error}","scientific_authority":False,"belief_authority":False};write_json(output,result);return result
        result={"schema_version":"1.0","status":"DIFFICULTY_COMPLETE","pair_id":pair_id,"family":pair["family"],"raw_sha256":archive["raw_sha256"],"resolved_model":archive["resolved_model"],"answer_source":source,"backward_answer":answers["backward_answer"],"forward_answer":answers["forward_answer"],"backward_truth":pair["backward"]["answer"],"forward_truth":pair["forward"]["answer"],"backward_success":answers["backward_answer"]==pair["backward"]["answer"],"forward_success":answers["forward_answer"]==pair["forward"]["answer"],"usage":archive["usage"],"scientific_authority":False,"belief_authority":False};result["receipt_sha256"]=sha_json(result);record_parsed_api_output(run_root=persistent_root/"runs"/run_id,stage="p12-difficulty-calibration",raw_sha256=archive["raw_sha256"],structured_payload=result,requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],research_objects=[],root=persistent_root);write_json(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def execute_skill_bundle(*,run_root: Path,persistent_root: Path,bundle_id: str) -> dict[str,Any]:
    authorization_ok(run_root);bundles={row["bundle_id"]:row for row in skill_calibration_bundles()}
    if bundle_id not in bundles: raise ValueError(bundle_id)
    output=run_root/"skill-compilation"/f"{bundle_id}.json";lock=lock_output(output,{"stage":"skill-compilation","bundle_id":bundle_id});prefix=_prefix(run_root);run_id=prefix+"skill-"+bundle_id.lower()
    try:
        used,run_ids=_recorded_calls(persistent_root,prefix)
        if run_id in run_ids: raise RuntimeError(f"provider call already recorded:{run_id}")
        current_cap,_=_current_call_cap(run_root)
        if used>=current_cap: raise RuntimeError("P12 provider-call cap exhausted")
        bundle=bundles[bundle_id];prompt=skill_compilation_prompt(bundle);archive,failure=_call_once(persistent_root=persistent_root,run_id=run_id,stage="p12-skill-compilation",prompt=prompt,tools=skill_tool(),max_output_tokens=1000)
        if archive is None: result={"schema_version":"1.0","status":"SKILL_PROVIDER_FAILURE","bundle_id":bundle_id,**failure};write_json(output,result);return result
        try: texts,source=parse_skills(archive)
        except Exception as error:
            _close_parse_failure(persistent_root=persistent_root,archive=archive,stage="p12-skill-compilation",error=error);result={"schema_version":"1.0","status":"SKILL_PROTOCOL_FAILURE","bundle_id":bundle_id,"raw_sha256":archive["raw_sha256"],"error":f"{type(error).__name__}:{error}","scientific_authority":False,"belief_authority":False};write_json(output,result);return result
        skills=[{"skill_id":bundle["older_skill_id"],"family":bundle["family"],"timestamp":bundle["older_timestamp"],"text":texts["older_skill_text"],"retrieval_text":retrieval_text(bundle["family"]),"origin":"DISJOINT_SKILL_CALIBRATION","source_bundle_id":bundle_id,"scientific_authority":False},{"skill_id":bundle["newer_skill_id"],"family":bundle["family"],"timestamp":bundle["newer_timestamp"],"text":texts["newer_skill_text"],"retrieval_text":retrieval_text(bundle["family"]),"origin":"DISJOINT_SKILL_CALIBRATION","source_bundle_id":bundle_id,"scientific_authority":False}]
        result={"schema_version":"1.0","status":"SKILL_COMPILATION_COMPLETE","bundle_id":bundle_id,"family":bundle["family"],"raw_sha256":archive["raw_sha256"],"resolved_model":archive["resolved_model"],"skill_source":source,"skills":skills,"usage":archive["usage"],"scientific_authority":False,"belief_authority":False};result["receipt_sha256"]=sha_json(result);record_parsed_api_output(run_root=persistent_root/"runs"/run_id,stage="p12-skill-compilation",raw_sha256=archive["raw_sha256"],structured_payload=result,requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],research_objects=[],root=persistent_root);write_json(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def _difficulty_receipt_path(run_root: Path,pair_id: str) -> Path:
    repaired=run_root/"difficulty-repair-v2"/f"{pair_id}.json"
    if repaired.is_file(): return repaired
    return run_root/"difficulty"/f"{pair_id}.json"


def _all_difficulty_complete(run_root: Path) -> bool:
    for row in difficulty_calibration_pairs():
        path=_difficulty_receipt_path(run_root,row["pair_id"])
        if not path.is_file() or load_json(path).get("status")!="DIFFICULTY_COMPLETE": return False
    return True


def pending_calibration(run_root: Path) -> dict[str,list[str]]:
    diff=[]
    for row in difficulty_calibration_pairs():
        path=_difficulty_receipt_path(run_root,row["pair_id"])
        if not path.is_file() or load_json(path).get("status")!="DIFFICULTY_COMPLETE": diff.append(row["pair_id"])
    skills=[row["bundle_id"] for row in skill_calibration_bundles() if not (run_root/"skill-compilation"/f"{row['bundle_id']}.json").is_file()]
    return {"difficulty":diff,"skills":skills}


def run_calibration(*,run_root: Path,persistent_root: Path) -> dict[str,Any]:
    authorization_ok(run_root);completed=[]
    for pid in pending_calibration(run_root)["difficulty"]:
        # A recorded failed difficulty call must be repaired through the explicit
        # runtime-repair route; never silently POST it again here.
        old=run_root/"difficulty"/f"{pid}.json"
        if old.is_file() and load_json(old).get("status")!="DIFFICULTY_COMPLETE": break
        result=execute_difficulty_pair(run_root=run_root,persistent_root=persistent_root,pair_id=pid);completed.append({"kind":"difficulty","id":pid,"status":result.get("status")})
        if result.get("status")!="DIFFICULTY_COMPLETE": break
    if _all_difficulty_complete(run_root):
        for bid in pending_calibration(run_root)["skills"]:
            result=execute_skill_bundle(run_root=run_root,persistent_root=persistent_root,bundle_id=bid);completed.append({"kind":"skill","id":bid,"status":result.get("status")})
            if result.get("status")!="SKILL_COMPILATION_COMPLETE": break
    return {"schema_version":"1.0","status":"P12_CALIBRATION_PROGRESS","difficulty_complete":_all_difficulty_complete(run_root),"completed":completed,"pending":pending_calibration(run_root),"scientific_authority":False,"belief_authority":False}


def freeze_calibration(run_root: Path) -> dict[str,Any]:
    output=run_root/"pre-evaluation-lock.json";lock=lock_output(output,{"stage":"freeze-calibration"})
    try:
        diff=[]
        for row in difficulty_calibration_pairs():
            p=_difficulty_receipt_path(run_root,row["pair_id"])
            if not p.is_file(): raise RuntimeError(f"missing difficulty receipt:{row['pair_id']}")
            receipt=load_json(p)
            if receipt.get("status")!="DIFFICULTY_COMPLETE": raise RuntimeError(f"difficulty calibration not complete:{row['pair_id']}:{receipt.get('status')}")
            diff.append(receipt)
        skills=[]
        for row in skill_calibration_bundles():
            p=run_root/"skill-compilation"/f"{row['bundle_id']}.json"
            if not p.is_file(): raise RuntimeError(f"missing skill receipt:{row['bundle_id']}")
            value=load_json(p)
            if value.get("status")!="SKILL_COMPILATION_COMPLETE": raise RuntimeError(f"skill calibration failed:{row['bundle_id']}")
            skills.extend(value["skills"])
        dsum=difficulty_summary(diff);skill_errors=validate_frozen_skills(skills);pairing=retrieval_pairing_checks(skills)
        library={"schema_version":"1.0","status":"P12_FROZEN_SKILL_LIBRARY","skills":sorted(skills,key=lambda x:x["timestamp"]),"skill_errors":skill_errors,"scientific_authority":False,"belief_authority":False};library["library_sha256"]=sha_json(library);write_json(run_root/"frozen-skill-library.json",library)
        units=rollout_units(skills) if not skill_errors else []
        manifest={"schema_version":"1.0","status":"P12_FROZEN_ROLLOUT_MANIFEST","library_sha256":library["library_sha256"],"unit_count":len(units),"units":units,"scientific_authority":False,"belief_authority":False};manifest["rollout_manifest_sha256"]=sha_json(manifest);write_json(run_root/"rollout-manifest.json",manifest)
        passed=dsum.get("passed") is True and not skill_errors and pairing.get("passed") is True and len(units)==96
        result={"schema_version":"1.0","status":"P12_PRE_EVALUATION_LOCK_PASS" if passed else "P12_PRE_EVALUATION_LOCK_INCONCLUSIVE","difficulty_summary":dsum,"skill_library_sha256":library["library_sha256"],"rollout_manifest_sha256":manifest["rollout_manifest_sha256"],"retrieval_pairing":pairing,"skill_errors":skill_errors,"evaluation_authorized_by_lock":passed,"scientific_authority":False,"belief_authority":False};result["lock_sha256"]=sha_json(result);write_json(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def execute_rollout_unit(*,run_root: Path,persistent_root: Path,unit_id: str) -> dict[str,Any]:
    authorization_ok(run_root);lock_state=load_json(run_root/"pre-evaluation-lock.json")
    if lock_state.get("status")!="P12_PRE_EVALUATION_LOCK_PASS" or lock_state.get("evaluation_authorized_by_lock") is not True: raise RuntimeError("P12 pre-evaluation lock not PASS")
    manifest=load_json(run_root/"rollout-manifest.json");units={row["unit_id"]:row for row in manifest["units"]}
    if unit_id not in units: raise ValueError(unit_id)
    output=run_root/"units"/f"{unit_id}.json";lock=lock_output(output,{"stage":"rollout","unit_id":unit_id});prefix=_prefix(run_root);run_id=prefix+"unit-"+unit_id.lower()
    try:
        used,run_ids=_recorded_calls(persistent_root,prefix)
        if run_id in run_ids: raise RuntimeError(f"provider call already recorded:{run_id}")
        current_cap,_=_current_call_cap(run_root)
        if used>=current_cap: raise RuntimeError("P12 provider-call cap exhausted")
        unit=units[unit_id];prompt=rollout_prompt(unit);archive,failure=_call_once(persistent_root=persistent_root,run_id=run_id,stage="p12-evaluation-unit",prompt=prompt,tools=answer_tool(),max_output_tokens=500)
        if archive is None: result={"schema_version":"1.0","status":"UNIT_PROVIDER_FAILURE","unit_id":unit_id,**failure};write_json(output,result);return result
        try: answer,source=parse_single_integer(archive)
        except Exception as error:
            _close_parse_failure(persistent_root=persistent_root,archive=archive,stage="p12-evaluation-unit",error=error);result={"schema_version":"1.0","status":"UNIT_PROTOCOL_FAILURE","unit_id":unit_id,"raw_sha256":archive["raw_sha256"],"error":f"{type(error).__name__}:{error}","scientific_authority":False,"belief_authority":False};write_json(output,result);return result
        result={"schema_version":"1.0","status":"UNIT_COMPLETE","unit_id":unit_id,"task_id":unit["task_id"],"scenario_id":unit["scenario_id"],"family":unit["family"],"phase":unit["phase"],"library_stage":unit["library_stage"],"recency_policy":unit["recency_policy"],"retrieval_query_sha256":unit["retrieval_query_sha256"],"selected_skill_ids":unit["selected_skill_ids"],"selected_static_similarities":unit["selected_static_similarities"],"answer":answer,"truth":unit["answer"],"task_success":answer==unit["answer"],"answer_source":source,"raw_sha256":archive["raw_sha256"],"resolved_model":archive["resolved_model"],"usage":archive["usage"],"valid_execution":True,"scientific_authority":False,"belief_authority":False};result["unit_receipt_sha256"]=sha_json(result);record_parsed_api_output(run_root=persistent_root/"runs"/run_id,stage="p12-evaluation-unit",raw_sha256=archive["raw_sha256"],structured_payload=result,requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],research_objects=[],root=persistent_root);write_json(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def pending_units(run_root: Path) -> list[str]:
    if not (run_root/"rollout-manifest.json").is_file(): return []
    manifest=load_json(run_root/"rollout-manifest.json")
    return [row["unit_id"] for row in manifest["units"] if not (run_root/"units"/f"{row['unit_id']}.json").is_file()]


def run_batch(*,run_root: Path,persistent_root: Path,limit: int=12) -> dict[str,Any]:
    completed=[]
    for uid in pending_units(run_root)[:max(0,int(limit))]:
        result=execute_rollout_unit(run_root=run_root,persistent_root=persistent_root,unit_id=uid);completed.append({"unit_id":uid,"status":result.get("status"),"task_success":result.get("task_success")})
        if result.get("status")!="UNIT_COMPLETE": break
    after=pending_units(run_root)
    return {"schema_version":"1.0","status":"P12_ROLLOUT_PROGRESS","completed":completed,"pending_count":len(after),"next_units":after[:12],"scientific_authority":False,"belief_authority":False}


def finalize(run_root: Path) -> dict[str,Any]:
    output=run_root/"adjudication.json";lock=lock_output(output,{"stage":"p12-finalize"})
    try:
        lock_state=load_json(run_root/"pre-evaluation-lock.json")
        if lock_state.get("status")!="P12_PRE_EVALUATION_LOCK_PASS": result={"schema_version":"1.0","status":"P12_EVIDENCE_ADJUDICATED","outcome":"INCONCLUSIVE","reason":"pre-evaluation difficulty/retrieval/skill gate failed","pre_evaluation_lock":lock_state,"scientific_authority":False,"belief_authority":False};write_json(output,result);return result
        receipts=[]
        for uid in [row["unit_id"] for row in load_json(run_root/"rollout-manifest.json")["units"]]:
            p=run_root/"units"/f"{uid}.json"
            if p.is_file(): receipts.append(load_json(p))
        result=adjudicate_rollouts(receipts,lock_state["difficulty_summary"]);result["skill_library_sha256"]=lock_state["skill_library_sha256"];result["rollout_manifest_sha256"]=lock_state["rollout_manifest_sha256"];result["protocol_call_cap"]=PROVIDER_CALL_CAP;result["adjudication_sha256"]=sha_json({k:v for k,v in result.items() if k!="adjudication_sha256"});write_json(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def main() -> None:
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="cmd",required=True)
    c=sub.add_parser("calibrate");c.add_argument("--run-root",type=Path,required=True);c.add_argument("--persistent-root",type=Path,required=True)
    f=sub.add_parser("freeze");f.add_argument("--run-root",type=Path,required=True)
    u=sub.add_parser("unit");u.add_argument("--run-root",type=Path,required=True);u.add_argument("--persistent-root",type=Path,required=True);u.add_argument("--unit-id",required=True)
    b=sub.add_parser("batch");b.add_argument("--run-root",type=Path,required=True);b.add_argument("--persistent-root",type=Path,required=True);b.add_argument("--limit",type=int,default=12)
    a=sub.add_parser("finalize");a.add_argument("--run-root",type=Path,required=True)
    args=p.parse_args()
    if args.cmd=="calibrate": out=run_calibration(run_root=args.run_root,persistent_root=args.persistent_root)
    elif args.cmd=="freeze": out=freeze_calibration(args.run_root)
    elif args.cmd=="unit": out=execute_rollout_unit(run_root=args.run_root,persistent_root=args.persistent_root,unit_id=args.unit_id)
    elif args.cmd=="batch": out=run_batch(run_root=args.run_root,persistent_root=args.persistent_root,limit=args.limit)
    else: out=finalize(args.run_root)
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=="__main__": main()
