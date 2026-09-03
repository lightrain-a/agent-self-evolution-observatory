#!/usr/bin/env python3
"""R64 prospective calibration for hidden-governance PSMG.

Runs exactly two executor surfaces on 24 fresh, previously unexposed clusters:
N=no memory and M=the frozen R54 actionable content with provenance hidden.
Only after all 48 arms complete are memory marginal utilities computed, the
pre-frozen controller fit, and all R65 test decisions frozen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import random
from datetime import datetime, timezone
from typing import Any

try:
    from . import failure_memory_memrl_ab_identification_r48 as r48
    from . import failure_memory_psmg_governance_common_r63 as common
except ImportError:
    import failure_memory_memrl_ab_identification_r48 as r48  # type: ignore
    import failure_memory_psmg_governance_common_r63 as common  # type: ignore

PAPER_ID = common.PAPER_ID
PROGRAM_STATUS = "R63_PSMG_HIDDEN_GOVERNANCE_PROGRAM_FROZEN_PRE_CALIBRATION_OUTCOME"
AUTH_STATUS = "R64_PSMG_CALIBRATION_EXECUTION_AUTHORITY_FROZEN_PRE_CALIBRATION_OUTCOME"
R54_STATUS = "FRESH_SUPPORT_QUALIFICATION_PASS_VALIDATION_STILL_SEALED"
ARMS = ["N_no_memory", "M_content_only"]
ARM_SEED_STRING = "B1-R64-PSMG-POTENTIAL-20260903"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"not-object:{path}")
    return value


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def valid(value: dict[str, Any]) -> bool:
    receipt = value.get("receipt_sha256")
    return isinstance(receipt, str) and receipt == common.digest({k: v for k, v in value.items() if k != "receipt_sha256"})


def append(path: pathlib.Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        f.flush(); os.fsync(f.fileno())


def rows(path: pathlib.Path) -> list[dict[str, Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []


def arm_order(task_id: str) -> list[str]:
    seed = int(hashlib.sha256(f"{ARM_SEED_STRING}|{task_id}".encode()).hexdigest()[:16], 16)
    out = list(ARMS); random.Random(seed).shuffle(out); return out


def retrieval_by_id(frozen: dict[str, Any]) -> dict[str, dict[str, Any]]:
    by = {str(row.get("representative_id")): row for row in (frozen.get("rows") or [])}
    needed = common.CALIBRATION_IDS + common.TEST_IDS + common.RESERVE_IDS
    if any(t not in by for t in needed):
        raise RuntimeError("R64-frozen-retrieval-missing-required-id")
    for tid in needed:
        row = by[tid]
        if row.get("has_eligible_frozen_retrieval") is not True:
            raise RuntimeError(f"R64-ineligible-required-id:{tid}")
    return by


def feature_table(by: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows_out = [common.feature_record(by[t]) for t in common.CALIBRATION_IDS + common.TEST_IDS + common.RESERVE_IDS]
    out = {
        "schema_version":"1.0","paper_id":PAPER_ID,"role":"R63_PSMG_PREOUTCOME_FEATURE_TABLE",
        "calibration_ids":common.CALIBRATION_IDS,"test_ids":common.TEST_IDS,"reserve_ids":common.RESERVE_IDS,
        "Z_feature_names":common.Z_FEATURE_NAMES,"P_feature_names":common.P_FEATURE_NAMES,
        "rows":rows_out,"target_outcomes_observed_when_created":0,"raw_provenance_executor_visible":False,
    }
    out["feature_table_sha256"] = common.digest(out)
    return out


def preflight(runtime_manifest_path: pathlib.Path, program_path: pathlib.Path, authority_path: pathlib.Path,
              r54_path: pathlib.Path, frozen_path: pathlib.Path, source_receipt_path: pathlib.Path) -> tuple[dict[str,Any],dict[str,Any],dict[str,Any],dict[str,Any],dict[str,Any],dict[str,dict[str,Any]]]:
    runtime, program, authority, r54, frozen, source = map(load, [runtime_manifest_path, program_path, authority_path, r54_path, frozen_path, source_receipt_path])
    if any(x.get("paper_id") != PAPER_ID for x in [runtime, program, authority, r54, frozen, source]): raise RuntimeError("R64-paper-id-drift")
    if program.get("status") != PROGRAM_STATUS or authority.get("status") != AUTH_STATUS or r54.get("status") != R54_STATUS: raise RuntimeError("R64-status-drift")
    if not all(valid(x) for x in [runtime, program, authority, r54, source]): raise RuntimeError("R64-receipt-hash-drift")
    b = authority.get("bindings") or {}
    checks = {
        "runtime_manifest_file_sha256":sha(runtime_manifest_path), "program_contract_file_sha256":sha(program_path),
        "r54v2_receipt_file_sha256":sha(r54_path), "frozen_retrieval_file_sha256":sha(frozen_path),
        "source_receipt_file_sha256":sha(source_receipt_path), "common_module_sha256":sha(pathlib.Path(common.__file__).resolve()),
        "runner_sha256":sha(pathlib.Path(__file__).resolve()),
    }
    for k,v in checks.items():
        if b.get(k) != v: raise RuntimeError(f"R64-binding-drift:{k}")
    if source.get("status") != "SOURCE_BUILD_COMPLETE" or int(source.get("completed_count") or 0) != 350: raise RuntimeError("R64-source-not-full350")
    p = program.get("units") or {}
    if list(map(str,p.get("calibration_ids") or [])) != common.CALIBRATION_IDS or p.get("calibration_ids_sha256") != common.CALIBRATION_IDS_SHA256: raise RuntimeError("R64-calibration-unit-drift")
    if list(map(str,p.get("test_ids") or [])) != common.TEST_IDS or p.get("test_ids_sha256") != common.TEST_IDS_SHA256: raise RuntimeError("R64-test-unit-drift")
    if list(map(str,p.get("reserve_ids") or [])) != common.RESERVE_IDS or p.get("reserve_ids_sha256") != common.RESERVE_IDS_SHA256: raise RuntimeError("R64-reserve-unit-drift")
    if (authority.get("authority") or {}).get("calibration_execution") is not True or (authority.get("authority") or {}).get("test_execution") is not False: raise RuntimeError("R64-authority-scope-drift")
    # Reuse the already-qualified Qwen runtime checks without depending on old cohort IDs.
    e = runtime["execution_manifest"]
    import socket, subprocess, urllib.request
    import sys
    h=e["host"]; src=e["source"]
    if socket.gethostname()!=h["logical_name"] or pathlib.Path(sys.executable).resolve()!=pathlib.Path(h["python"]).resolve() or os.environ.get("PYTHONDONTWRITEBYTECODE")!="1": raise RuntimeError("R64-host-python-drift")
    root=pathlib.Path(src["checkout"]); head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip(); dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if head!=src["revision"] or dirty: raise RuntimeError("R64-source-checkout-drift")
    split=root/e["confirmatory_units"]["split"]
    if sha(split)!=e["confirmatory_units"]["split_sha256"]: raise RuntimeError("R64-split-drift")
    image=subprocess.check_output(["docker","image","inspect",e["runtime_image"]["execution_tag"],"--format","{{.Id}}"],text=True).strip()
    if image!=e["runtime_image"]["id"]: raise RuntimeError("R64-image-drift")
    base=e["external_runtime_adapter"]["loopback_base_url"].rstrip("/")
    with urllib.request.urlopen(base+"/models",timeout=5) as rr: models={str(x.get("id")) for x in json.loads(rr.read().decode()).get("data") or []}
    if {e["external_runtime_adapter"]["llm_model_id"],e["external_runtime_adapter"]["embedding_model_id"]}-models: raise RuntimeError("R64-loopback-route-drift")
    return runtime, program, authority, r54, source, retrieval_by_id(frozen)


def build_surfaces(runtime: dict[str,Any], by: dict[str,dict[str,Any]], ids: list[str]) -> tuple[dict[str,dict[str,str]],dict[str,dict[str,str]]]:
    make_prompt = r48.prompt_builder(runtime); surfaces={}; prompt_hashes={}
    no_memory_ctx = ""; no_memory_prompt = make_prompt(no_memory_ctx)
    for tid in ids:
        selected=[x for x in (by[tid].get("selected") or []) if x.get("eligible") is True]
        pair=r48.render_pair(selected,tid); mem_ctx=pair["A_content_only"]
        if "source_outcome_success" in mem_ctx: raise RuntimeError(f"R64-memory-provenance-leak:{tid}")
        if pair["audit"].get("actionable_content_identical") is not True: raise RuntimeError(f"R64-adapter-audit:{tid}")
        surfaces[tid]={"N_no_memory":no_memory_ctx,"M_content_only":mem_ctx}
        prompt_hashes[tid]={
            "N_no_memory":hashlib.sha256(no_memory_prompt.encode()).hexdigest(),
            "M_content_only":hashlib.sha256(make_prompt(mem_ctx).encode()).hexdigest(),
        }
    return surfaces,prompt_hashes


def build_plan(surfaces:dict[str,dict[str,str]], prompt_hashes:dict[str,dict[str,str]]) -> dict[str,Any]:
    schedule=[]; ordinal=0
    for tid in common.CALIBRATION_IDS:
        for arm in arm_order(tid):
            schedule.append({"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,
                "memory_context_sha256":hashlib.sha256(surfaces[tid][arm].encode()).hexdigest(),"system_prompt_sha256":prompt_hashes[tid][arm]}); ordinal+=1
    out={"schema_version":"1.0","paper_id":PAPER_ID,"role":"R64_PSMG_CALIBRATION_PLAN_FROZEN_PRE_OUTCOME",
        "units":common.CALIBRATION_IDS,"arms":ARMS,"arm_seed_string":ARM_SEED_STRING,"schedule":schedule,
        "calibration_outcomes_observed_when_created":0,"test_outcomes_observed_when_created":0,"raw_provenance_executor_visible":False}
    out["plan_sha256"]=common.digest(out); return out


def main() -> None:
    ap=argparse.ArgumentParser()
    for x in ["runtime-manifest","program-contract","authority","r54v2-qualification","frozen-retrieval","source-receipt","output-dir"]: ap.add_argument("--"+x,type=pathlib.Path,required=True)
    ap.add_argument("--resume",action="store_true"); a=ap.parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    runtime,program,auth,r54,source,by=preflight(a.runtime_manifest.resolve(),a.program_contract.resolve(),a.authority.resolve(),a.r54v2_qualification.resolve(),a.frozen_retrieval.resolve(),a.source_receipt.resolve())
    ft=feature_table(by); ftp=out/"frozen-preoutcome-feature-table.json"
    if ftp.exists():
        if load(ftp).get("feature_table_sha256")!=ft["feature_table_sha256"]: raise RuntimeError("R64-feature-table-drift")
    else: ftp.write_text(json.dumps(ft,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    feature_rows={str(x["task_id"]):x for x in ft["rows"]}
    surfaces,prompt_hashes=build_surfaces(runtime,by,common.CALIBRATION_IDS)
    plan=build_plan(surfaces,prompt_hashes); pp=out/"frozen-calibration-plan.json"
    if pp.exists():
        if load(pp).get("plan_sha256")!=plan["plan_sha256"]: raise RuntimeError("R64-plan-drift")
    else: pp.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    schedule=[(int(x["schedule_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in plan["schedule"]]
    started=rows(out/"started-calibration-arms.jsonl"); complete=rows(out/"completed-calibration-arms.jsonl")
    sk=[(int(x["schedule_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in started]; ck=[(int(x["schedule_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in complete]
    if sk!=schedule[:len(sk)] or ck!=schedule[:len(ck)]: raise RuntimeError("R64-ledger-not-schedule-prefix")
    if len(started)!=len(complete): raise RuntimeError("R64_EXPOSED_INCOMPLETE_ARM_NO_RETRY")
    if complete and len(complete)<len(schedule) and not a.resume: raise RuntimeError("R64-partial-requires-explicit-resume")
    if len(complete)<len(schedule):
        adapter=r48.r47base.build_adapter(runtime); make_prompt=r48.prompt_builder(runtime)
        for ordinal,tid,arm in schedule[len(complete):]:
            ctx=surfaces[tid][arm]; prompt=make_prompt(ctx); expected=plan["schedule"][ordinal]
            if hashlib.sha256(ctx.encode()).hexdigest()!=expected["memory_context_sha256"] or hashlib.sha256(prompt.encode()).hexdigest()!=expected["system_prompt_sha256"]: raise RuntimeError("R64-treatment-surface-drift")
            arm_dir=out/"arms"/f"{ordinal:03d}-{tid}-{arm}"; arm_dir.mkdir(parents=True,exist_ok=False)
            append(out/"started-calibration-arms.jsonl",{"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"STARTED","started_at":now(),"memory_context_sha256":expected["memory_context_sha256"],"system_prompt_sha256":expected["system_prompt_sha256"],"no_retry_if_incomplete":True})
            try:
                tr=r48.run_arm_exact(runtime,adapter,tid,arm,prompt); tp=arm_dir/"trace.json"; tp.write_text(json.dumps(tr,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
                row={"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"COMPLETE","completed_at":now(),"terminal_success":tr["terminal_success"],"steps":tr["steps"],
                     "first_executable_action_sha256":hashlib.sha256(str(tr["first_executable_action"] or "<NONE>").encode()).hexdigest(),"trace_file":str(tp),"trace_file_sha256":sha(tp),
                     "memory_context_sha256":expected["memory_context_sha256"],"system_prompt_sha256":expected["system_prompt_sha256"],"external_provider_calls":0}
                append(out/"completed-calibration-arms.jsonl",row); print(json.dumps({"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"completed":True},sort_keys=True),flush=True)
            except Exception as ex:
                fail={"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"EXECUTION_FAILURE_EXPOSED_NO_RETRY","failed_at":now(),"error_type":type(ex).__name__,"error":str(ex),"scientific_update_allowed":False}
                (arm_dir/"failure.json").write_text(json.dumps(fail,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); raise
    complete=rows(out/"completed-calibration-arms.jsonl")
    if len(complete)!=48: raise RuntimeError("R64-calibration-incomplete")
    pair={t:{} for t in common.CALIBRATION_IDS}
    for row in complete: pair[str(row["task_id"])][str(row["arm"])]=row
    utility={}; outcome_rows=[]
    for tid in common.CALIBRATION_IDS:
        if set(pair[tid])!=set(ARMS): raise RuntimeError(f"R64-incomplete-pair:{tid}")
        n=pair[tid]["N_no_memory"]["terminal_success"]; m=pair[tid]["M_content_only"]["terminal_success"]
        if type(n) is not bool or type(m) is not bool: raise RuntimeError(f"R64-invalid-outcome:{tid}")
        utility[tid]=float(int(m)-int(n)); outcome_rows.append({"task_id":tid,"N_no_memory":n,"M_content_only":m,"memory_marginal_utility":utility[tid]})
    model=common.fit_controller([feature_rows[t] for t in common.CALIBRATION_IDS],utility)
    support=model["calibration_support"]
    receipt={"schema_version":"1.0","paper_id":PAPER_ID,"role":"R64_PSMG_CALIBRATION_COMPLETE_ONLY_ADJUDICATION",
        "status":"PSMG_CALIBRATION_ROUTE_SUPPORT_PASS_TEST_DECISIONS_FROZEN" if support["route_support_pass"] else "CALIBRATION_ROUTE_SUPPORT_STOP_NO_TEST",
        "completed_units":24,"completed_arm_runs":48,"outcome_rows":outcome_rows,"calibration_support":support,
        "feature_table_sha256":ft["feature_table_sha256"],"plan_sha256":plan["plan_sha256"],"program_contract_receipt_sha256":program["receipt_sha256"],"authority_receipt_sha256":auth["receipt_sha256"],
        "test_outcomes_observed":0,"raw_provenance_executor_visible":False,"external_provider_calls":0,"scientific_authority":False}
    if support["route_support_pass"]:
        mp=out/"calibrated-controller.json"; mp.write_text(json.dumps(model,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        decisions=common.freeze_test_decisions(model,[feature_rows[t] for t in common.TEST_IDS]); dp=out/"frozen-test-decisions.json"; dp.write_text(json.dumps(decisions,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        receipt.update({"model_file_sha256":sha(mp),"model_sha256":model["model_sha256"],"test_decisions_file_sha256":sha(dp),"test_decision_plan_sha256":decisions["decision_plan_sha256"],"test_execution_conditionally_authorized_next":True})
    else:
        receipt["test_execution_conditionally_authorized_next"]=False
    receipt["receipt_sha256"]=common.digest(receipt); (out/"calibration-receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:receipt[k] for k in ["status","completed_arm_runs","calibration_support","test_execution_conditionally_authorized_next","receipt_sha256"]},sort_keys=True))


if __name__=="__main__": main()
