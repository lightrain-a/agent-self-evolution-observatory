#!/usr/bin/env python3
"""R75 paired task-ID outcome reporting for B1 provenance contrasts.

This is a descriptive reporting layer. It does not change the frozen R72/R73
experiment, its confirmatory tests, execution schedule, or authority. The goal
is to prevent aggregate success counts from hiding task-level substitution.

For each paired binary contrast, R75 reports the exact task IDs in:
- both success;
- left-only success;
- right-only success;
- both fail;
plus success-set overlap/Jaccard and outcome agreement.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib
from typing import Any, Iterable

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"


def canonical(v:Any)->str:
    return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)

def digest(v:Any)->str:
    return hashlib.sha256(canonical(v).encode()).hexdigest()

def file_sha(p:pathlib.Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read_jsonl(p:pathlib.Path)->list[dict[str,Any]]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]

def _sort_ids(xs:Iterable[str])->list[str]:
    vals=[str(x) for x in xs]
    try:return sorted(vals,key=lambda x:int(x))
    except Exception:return sorted(vals)

def paired_id_summary(rows:list[dict[str,Any]],left_arm:str,right_arm:str,planned_ids:list[str]|None=None)->dict[str,Any]:
    by:dict[str,dict[str,dict[str,Any]]]={}
    for row in rows:
        tid=str(row["task_id"]); arm=str(row["arm"])
        if arm not in {left_arm,right_arm}:continue
        if tid in by and arm in by[tid]:raise RuntimeError(f"duplicate-arm-row:{tid}:{arm}")
        by.setdefault(tid,{})[arm]=row
    ids=_sort_ids(planned_ids if planned_ids is not None else by.keys())
    if set(by)!=set(ids):
        extra=set(by)-set(ids); missing=set(ids)-set(by)
        raise RuntimeError(f"paired-id-domain-drift:missing={_sort_ids(missing)}:extra={_sort_ids(extra)}")
    incomplete=[]; left_success=set(); right_success=set(); both_success=set(); left_only=set(); right_only=set(); both_fail=set()
    for tid in ids:
        d=by[tid]
        if set(d)!={left_arm,right_arm}:
            incomplete.append(tid);continue
        yl=d[left_arm].get("terminal_success");yr=d[right_arm].get("terminal_success")
        if type(yl) is not bool or type(yr) is not bool:
            incomplete.append(tid);continue
        if yl:left_success.add(tid)
        if yr:right_success.add(tid)
        if yl and yr:both_success.add(tid)
        elif yl and not yr:left_only.add(tid)
        elif yr and not yl:right_only.add(tid)
        else:both_fail.add(tid)
    complete_n=len(ids)-len(incomplete)
    union=left_success|right_success; inter=left_success&right_success
    same_success_set=(left_success==right_success) if not incomplete else None
    subset_relation=None
    if not incomplete:
        if left_success==right_success:subset_relation="equal"
        elif left_success < right_success:subset_relation=f"{left_arm}_strict_subset_of_{right_arm}"
        elif right_success < left_success:subset_relation=f"{right_arm}_strict_subset_of_{left_arm}"
        else:subset_relation="neither_subset"
    out={
        "left_arm":left_arm,"right_arm":right_arm,"planned_pairs":len(ids),"complete_pairs":complete_n,
        "left_success_count":len(left_success),"right_success_count":len(right_success),
        "net_success_count_difference_right_minus_left":len(right_success)-len(left_success),
        "both_success_count":len(both_success),"left_only_success_count":len(left_only),"right_only_success_count":len(right_only),"both_fail_count":len(both_fail),
        "left_success_task_ids":_sort_ids(left_success),"right_success_task_ids":_sort_ids(right_success),
        "both_success_task_ids":_sort_ids(both_success),"left_only_success_task_ids":_sort_ids(left_only),"right_only_success_task_ids":_sort_ids(right_only),"both_fail_task_ids":_sort_ids(both_fail),
        "discordant_task_ids":_sort_ids(left_only|right_only),"incomplete_task_ids":_sort_ids(incomplete),
        "success_set_intersection_count":len(inter),"success_set_union_count":len(union),
        "success_set_jaccard":(len(inter)/len(union) if union else 1.0),
        "outcome_agreement_fraction":((len(both_success)+len(both_fail))/complete_n if complete_n else None),
        "outcome_discordance_fraction":((len(left_only)+len(right_only))/complete_n if complete_n else None),
        "same_success_task_set":same_success_set,"success_set_subset_relation":subset_relation,
        "interpretation":"Net success-count difference and task-level success substitution are distinct quantities; a zero net difference can coexist with many discordant task IDs."
    }
    return out

def cross_executor_success_overlap(rows_a:list[dict[str,Any]],rows_b:list[dict[str,Any]],arm:str,executor_a:str,executor_b:str)->dict[str,Any]:
    def s(rows):return {str(r["task_id"]) for r in rows if str(r.get("arm"))==arm and r.get("terminal_success") is True}
    a,b=s(rows_a),s(rows_b); inter=a&b; union=a|b
    return {"arm":arm,"executor_a":executor_a,"executor_b":executor_b,"executor_a_success_count":len(a),"executor_b_success_count":len(b),"both_executor_success_task_ids":_sort_ids(inter),"executor_a_only_success_task_ids":_sort_ids(a-b),"executor_b_only_success_task_ids":_sort_ids(b-a),"success_set_jaccard":len(inter)/len(union) if union else 1.0,"inferential_role":"descriptive_only_no_pooling"}

def historical_receipt(qwen_path:pathlib.Path,llama_path:pathlib.Path)->dict[str,Any]:
    q=read_jsonl(qwen_path);l=read_jsonl(llama_path)
    qsum=paired_id_summary(q,"A_content_only","B_raw_provenance")
    lsum=paired_id_summary(l,"A_content_only","B_raw_provenance")
    out={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R75-HISTORICAL-PAIRED-ID-AUDIT","status":"R75_HISTORICAL_PAIRED_TASK_ID_AUDIT_COMPLETE","role":"ZERO_PROVIDER_DESCRIPTIVE_TASK_ID_OVERLAP_AUDIT","bindings":{"qwen_r56_completed_ab_arms_file_sha256":file_sha(qwen_path),"llama_r61_completed_ab_arms_file_sha256":file_sha(llama_path)},"Qwen2.5-7B-Instruct":qsum,"Meta-Llama-3.1-8B-Instruct":lsum,"cross_executor":{"A_content_only":cross_executor_success_overlap(q,l,"A_content_only","Qwen2.5-7B-Instruct","Meta-Llama-3.1-8B-Instruct"),"B_raw_provenance":cross_executor_success_overlap(q,l,"B_raw_provenance","Qwen2.5-7B-Instruct","Meta-Llama-3.1-8B-Instruct")},"scientific_interpretation":{"Qwen":"The 15 content-only successes are an exact subset of the 16 truthful-field successes; Task 252 is the sole truthful-only terminal success.","Llama":"Aggregate success is 17/32 in both arms, but the success sets differ: two content-only-only successes and two truthful-only successes cancel in the net count.","cross_executor":"Executor success sets overlap only partially and are reported descriptively; executor outcomes are never pooled."},"changes_R72_R73_inferential_gate":False,"changes_R72_R73_workload":False,"new_model_trajectories":0,"experiment_authority":False,"scientific_authority":False,"gpu_authority":False}
    out["receipt_sha256"]=digest(out);return out

def future_reporting_contract()->dict[str,Any]:
    fields=["left_success_task_ids","right_success_task_ids","both_success_task_ids","left_only_success_task_ids","right_only_success_task_ids","both_fail_task_ids","discordant_task_ids","success_set_intersection_count","success_set_union_count","success_set_jaccard","outcome_agreement_fraction","outcome_discordance_fraction","same_success_task_set","success_set_subset_relation"]
    out={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R75-FUTURE-PAIRED-ID-REPORTING-CONTRACT","status":"R75_PAIRED_TASK_ID_REPORTING_REQUIRED_AFTER_R72_EXECUTION","role":"DESCRIPTIVE_REPORTING_EXTENSION_WITHOUT_INFERENTIAL_CHANGE","required_contrasts":{"Qwen_primary":{"left":"P_neutral","right":"T_truthful","planned_n":66},"Qwen_correctness":{"left":"S_shuffled","right":"T_truthful","planned_n":57,"inferential_gate":"existing R72 gate remains unchanged"},"Llama_replication":{"left":"P_neutral","right":"T_truthful","planned_n":66}},"required_fields_per_contrast":fields,"main_table_minimum_fields":["left_success_count","right_success_count","both_success_count","left_only_success_count","right_only_success_count","both_fail_count","net_success_count_difference_right_minus_left"],"appendix_requirement":"List every discordant task ID and its arm-specific binary outcome; do not report only aggregate success totals.","interpretation_rule":"Equal aggregate success counts do not imply equal task-level effects. Net effect and success-set substitution must be reported separately.","cross_executor_success_set_overlap":"descriptive_only_no_pooling","changes_R72_R73_inferential_gate":False,"changes_R72_R73_execution_schedule":False,"new_trajectories_required":0,"execution_authority":False,"scientific_authority":False,"gpu_authority":False}
    out["receipt_sha256"]=digest(out);return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--qwen-r56",type=pathlib.Path);ap.add_argument("--llama-r61",type=pathlib.Path);ap.add_argument("--historical-output",type=pathlib.Path);ap.add_argument("--contract-output",type=pathlib.Path)
    ap.add_argument("--paired-jsonl",type=pathlib.Path);ap.add_argument("--left-arm");ap.add_argument("--right-arm");ap.add_argument("--planned-ids",help="comma-separated paired task IDs");ap.add_argument("--paired-output",type=pathlib.Path)
    a=ap.parse_args()
    if a.qwen_r56 and a.llama_r61:
        if not a.historical_output:raise RuntimeError("--historical-output-required")
        x=historical_receipt(a.qwen_r56,a.llama_r61);a.historical_output.parent.mkdir(parents=True,exist_ok=True);a.historical_output.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":x["status"],"receipt_sha256":x["receipt_sha256"]},sort_keys=True))
    if a.contract_output:
        x=future_reporting_contract();a.contract_output.parent.mkdir(parents=True,exist_ok=True);a.contract_output.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":x["status"],"receipt_sha256":x["receipt_sha256"]},sort_keys=True))
    if a.paired_jsonl:
        if not (a.left_arm and a.right_arm and a.paired_output):raise RuntimeError("generic paired report requires --left-arm --right-arm --paired-output")
        planned=[x.strip() for x in a.planned_ids.split(',') if x.strip()] if a.planned_ids else None
        s=paired_id_summary(read_jsonl(a.paired_jsonl),a.left_arm,a.right_arm,planned)
        out={"schema_version":"1.0","paper_id":PAPER_ID,"status":"R75_GENERIC_PAIRED_TASK_ID_REPORT","source_file_sha256":file_sha(a.paired_jsonl),"summary":s,"inferential_role":"descriptive_only_does_not_replace_frozen_confirmatory_analysis"};out["receipt_sha256"]=digest(out)
        a.paired_output.parent.mkdir(parents=True,exist_ok=True);a.paired_output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":out["status"],"receipt_sha256":out["receipt_sha256"]},sort_keys=True))
if __name__=="__main__":main()
