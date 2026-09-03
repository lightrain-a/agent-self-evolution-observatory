#!/usr/bin/env python3
"""R55: fresh 8-cluster utilization qualification for the R53 full350 lineage."""
from __future__ import annotations

import argparse, hashlib, json, os, pathlib, sys
from datetime import datetime, timezone
from typing import Any

try:
    from . import failure_memory_memrl_utilization_r47 as r47
except ImportError:
    import failure_memory_memrl_utilization_r47 as r47  # type: ignore

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
MANIFEST_STATUS = "R55_FULL350_FRESH_UTILIZATION_MANIFEST_FROZEN_PRE_OUTCOME"
AUTH_STATUS = "R55_FULL350_FRESH_UTILIZATION_EXECUTION_AUTHORITY_FROZEN_PRE_OUTCOME"
R54_PASS = "FRESH_SUPPORT_QUALIFICATION_PASS_VALIDATION_STILL_SEALED"
ARMS = list(r47.ARMS)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load(p: pathlib.Path) -> dict[str, Any]:
    v = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(v, dict): raise RuntimeError(f"not-object:{p}")
    return v


def valid(v: dict[str, Any]) -> bool:
    x = v.get("receipt_sha256")
    return isinstance(x, str) and x == r47.digest({k: z for k, z in v.items() if k != "receipt_sha256"})


def ids_hash(ids: list[str]) -> str:
    return hashlib.sha256("\n".join(ids).encode()).hexdigest()


def preflight(manifest_path: pathlib.Path, authority_path: pathlib.Path, r54_path: pathlib.Path,
              selection_path: pathlib.Path, frozen_path: pathlib.Path, source_receipt_path: pathlib.Path):
    m, a, q, s, f, src = map(load, [manifest_path, authority_path, r54_path, selection_path, frozen_path, source_receipt_path])
    if any(x.get("paper_id") != PAPER_ID for x in [m, a, q, s, f, src]): raise RuntimeError("R55-paper-id-drift")
    if m.get("status") != MANIFEST_STATUS or a.get("status") != AUTH_STATUS or q.get("status") != R54_PASS: raise RuntimeError("R55-status-drift")
    if not all(valid(x) for x in [m, a, q, s, f, src]): raise RuntimeError("R55-receipt-hash-drift")
    b = a.get("bindings") or {}
    checks = {
        "manifest_file_sha256": r47.sha(manifest_path),
        "r54v2_receipt_file_sha256": r47.sha(r54_path),
        "selection_file_sha256": r47.sha(selection_path),
        "frozen_retrieval_file_sha256": r47.sha(frozen_path),
        "source_receipt_file_sha256": r47.sha(source_receipt_path),
        "runner_sha256": r47.sha(pathlib.Path(__file__).resolve()),
    }
    for k, observed in checks.items():
        if b.get(k) != observed: raise RuntimeError(f"R55-binding-drift:{k}")
    if int(q.get("validation_treatment_outcomes_observed") or 0) != 0: raise RuntimeError("R55-validation-already-opened")
    if src.get("status") != "SOURCE_BUILD_COMPLETE" or int(src.get("completed_count") or 0) != 350: raise RuntimeError("R55-source-not-full350")
    e = m.get("execution_manifest") or {}; u = e.get("utilization_qualification") or {}; c = e.get("confirmatory_units") or {}
    ids = [str(x) for x in u.get("representative_ids") or []]; primary_ids = [str(x) for x in c.get("representative_ids") or []]
    if len(ids) != 8 or ids_hash(ids) != u.get("representative_ids_sha256") or list(u.get("arms") or []) != ARMS: raise RuntimeError("R55-utilization-id-or-arm-drift")
    if len(primary_ids) != 32 or ids_hash(primary_ids) != c.get("representative_ids_sha256") or set(ids) & set(primary_ids): raise RuntimeError("R55-primary-id-drift")
    if ids != [str(x) for x in s.get("utilization_representative_ids") or []] or primary_ids != [str(x) for x in s.get("primary_representative_ids") or []]: raise RuntimeError("R55-selection-id-drift")
    records = list(s.get("utilization_records") or []); by = {str(x.get("validation_task_id")): x for x in records}
    if set(by) != set(ids) or len(records) != 8: raise RuntimeError("R55-utilization-record-drift")
    for tid in ids:
        selected = list(by[tid].get("selected") or [])
        if not selected or any(x.get("eligible") is not True for x in selected): raise RuntimeError(f"R55-selected-retrieval-ineligible:{tid}")
        if any(type(x.get("source_outcome_success")) is not bool or not x.get("content") for x in selected): raise RuntimeError(f"R55-selected-retrieval-field-invalid:{tid}")
    # Verify host/runtime/image/model route using the inherited R47 checks that do not depend on old IDs.
    h=e["host"]; source=e["source"]
    import socket, subprocess, urllib.request
    if socket.gethostname()!=h["logical_name"] or pathlib.Path(sys.executable).resolve()!=pathlib.Path(h["python"]).resolve() or os.environ.get("PYTHONDONTWRITEBYTECODE")!="1": raise RuntimeError("R55-host-python-drift")
    root=pathlib.Path(source["checkout"]); head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip(); dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if head!=source["revision"] or dirty: raise RuntimeError("R55-source-checkout-drift")
    split=root/c["split"]
    if r47.sha(split)!=c["split_sha256"]: raise RuntimeError("R55-validation-split-drift")
    image=subprocess.check_output(["docker","image","inspect",e["runtime_image"]["execution_tag"],"--format","{{.Id}}"],text=True).strip()
    if image!=e["runtime_image"]["id"]: raise RuntimeError("R55-image-drift")
    base=e["external_runtime_adapter"]["loopback_base_url"].rstrip("/")
    with urllib.request.urlopen(base+"/models",timeout=5) as rr: models={str(x.get("id")) for x in json.loads(rr.read().decode()).get("data") or []}
    if {e["external_runtime_adapter"]["llm_model_id"],e["external_runtime_adapter"]["embedding_model_id"]}-models: raise RuntimeError("R55-loopback-route-drift")
    return m, a, q, s, f, src, by


def build_plan(m: dict[str, Any], by: dict[str, dict[str, Any]]) -> dict[str, Any]:
    e=m["execution_manifest"]; u=e["utilization_qualification"]; ids=[str(x) for x in u["representative_ids"]]; seed=int(e["randomization"]["seed"])
    donors=r47.u4_map(seed,by,ids); schedule=[]; ordinal=0
    for tid in ids:
        for arm in r47.arm_order(seed,tid):
            schedule.append({"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"u4_donor_task_id":donors[tid]}); ordinal+=1
    p={"schema_version":"1.0","paper_id":PAPER_ID,"role":"R55_FRESH_UTILIZATION_SCHEDULE_FROZEN_PRE_TREATMENT","randomization_seed":seed,
       "utilization_ids":ids,"arms":ARMS,"schedule":schedule,"promotion_endpoint":u["promotion_endpoint"],"pass_rule":u["pass_rule"],
       "terminal_success_is_diagnostic_only":True,"utilization_outcomes_observed_when_plan_created":0,"primary_A_B_outcomes_observed":0,"scientific_authority":False}
    p["plan_sha256"]=r47.digest(p); return p


def resume_guard(out: pathlib.Path, schedule: list[tuple[int,str,str,str]], resume: bool) -> tuple[list[dict[str,Any]],list[dict[str,Any]]]:
    started=r47.rows(out/"started-utilization-arms.jsonl"); complete=r47.rows(out/"completed-utilization-arms.jsonl")
    sk=[(int(x["schedule_ordinal"]),str(x["task_id"]),str(x["arm"]),str(x["u4_donor_task_id"])) for x in started]
    ck=[(int(x["schedule_ordinal"]),str(x["task_id"]),str(x["arm"]),str(x["u4_donor_task_id"])) for x in complete]
    if sk!=schedule[:len(sk)] or ck!=schedule[:len(ck)]: raise RuntimeError("R55-ledger-not-schedule-prefix")
    if len(started)!=len(complete): raise RuntimeError("R55_EXPOSED_INCOMPLETE_ARM_NO_RETRY")
    if complete and len(complete)<len(schedule) and not resume: raise RuntimeError("R55-partial-requires-explicit-resume")
    return started,complete


def main() -> None:
    p=argparse.ArgumentParser()
    for x in ["manifest","authorization","r54v2-qualification","selection","frozen-retrieval","source-receipt","output-dir"]: p.add_argument("--"+x,type=pathlib.Path,required=True)
    p.add_argument("--resume",action="store_true"); a=p.parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    m,auth,q,sel,frozen,src,by=preflight(a.manifest.resolve(),a.authorization.resolve(),a.r54v2_qualification.resolve(),a.selection.resolve(),a.frozen_retrieval.resolve(),a.source_receipt.resolve())
    pp=out/"frozen-utilization-plan.json"; plan=load(pp) if pp.exists() else build_plan(m,by)
    if not pp.exists(): pp.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if plan.get("plan_sha256")!=r47.digest({k:v for k,v in plan.items() if k!="plan_sha256"}): raise RuntimeError("R55-plan-hash-drift")
    schedule=[(int(z["schedule_ordinal"]),str(z["task_id"]),str(z["arm"]),str(z["u4_donor_task_id"])) for z in plan["schedule"]]
    started,complete=resume_guard(out,schedule,a.resume)
    if len(complete)<len(schedule):
        root=pathlib.Path(m["execution_manifest"]["source"]["checkout"])
        if str(root) not in sys.path: sys.path.insert(0,str(root))
        from memrl.lifelongbench_eval.memory_context import format_llb_memory_context
        adapter=r47.build_adapter(m)
        for ordinal,tid,arm,donor in schedule[len(complete):]:
            ctx,meta=r47.memctx(format_llb_memory_context,by[tid],arm,by[donor]); ad=out/"arms"/f"{ordinal:02d}-{tid}-{arm}"; ad.mkdir(parents=True,exist_ok=False)
            started_row={"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"u4_donor_task_id":donor,"status":"STARTED","started_at":now(),
                         "memory_context_sha256":hashlib.sha256(ctx.encode()).hexdigest(),"no_retry_if_incomplete":True}
            r47.append(out/"started-utilization-arms.jsonl",started_row)
            try:
                tr=r47.run_arm(m,adapter,tid,arm,ctx); tp=ad/"trace.json"; tp.write_text(json.dumps(tr,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
                row={"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"u4_donor_task_id":donor,"status":"COMPLETE","completed_at":now(),
                     "first_executable_action":tr["first_executable_action"],"first_executable_action_sha256":hashlib.sha256(str(tr["first_executable_action"] or "<NONE>").encode()).hexdigest(),
                     "terminal_success_diagnostic":tr["terminal_success_diagnostic"],"steps":tr["steps"],"memory_meta":meta,
                     "memory_context_sha256":hashlib.sha256(ctx.encode()).hexdigest(),"trace_file":str(tp),"trace_file_sha256":r47.sha(tp),"external_provider_calls":0}
                r47.append(out/"completed-utilization-arms.jsonl",row)
                print(json.dumps({"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"completed":True},sort_keys=True),flush=True)
            except Exception as ex:
                fail={"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"u4_donor_task_id":donor,"status":"EXECUTION_FAILURE_EXPOSED_NO_RETRY","failed_at":now(),"error_type":type(ex).__name__,"error":str(ex),"scientific_update_allowed":False}
                (ad/"failure.json").write_text(json.dumps(fail,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); raise
    complete=r47.rows(out/"completed-utilization-arms.jsonl")
    result=r47.analyze(plan,complete); result.update({"role":"R55_FRESH_UTILIZATION_QUALIFICATION_ADJUDICATION","manifest_receipt_sha256":m["receipt_sha256"],
        "authorization_receipt_sha256":auth["receipt_sha256"],"r54v2_qualification_receipt_sha256":q["receipt_sha256"],"selection_receipt_sha256":sel["receipt_sha256"],
        "completed_arm_runs":len(complete),"external_provider_calls":0,"primary_confirmatory_outcomes_observed":0})
    result["receipt_sha256"]=r47.digest({k:v for k,v in result.items() if k!="receipt_sha256"})
    (out/"utilization-qualification-receipt.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"pass":result["pass"],"complete_units":result["complete_units"],"u1_specific_first_action_units":result["u1_specific_first_action_units"],"u2_vs_u0_divergence_units":result["u2_vs_u0_divergence_units"],"primary_confirmatory_outcomes_observed":0,"receipt_sha256":result["receipt_sha256"]},sort_keys=True))


if __name__=="__main__": main()
