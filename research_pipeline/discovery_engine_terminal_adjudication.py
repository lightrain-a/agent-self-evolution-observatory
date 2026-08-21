from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TERMINAL_STATES={"COMPLETE_PAPER","SCIENTIFIC_STOP","DUPLICATE_BASIN"}
INTERMEDIATE_STATES={"ACTIVE_UNREFUTED_HYPOTHESIS"}
CLOSURE_AUTHORITIES={"direct_counterevidence","same_information_reduction","scope_matched_principle_counter_explanation"}


def validate_candidate_adjudication(row:dict[str,Any])->None:
    state=str(row.get("terminal_state") or "")
    if state not in TERMINAL_STATES|INTERMEDIATE_STATES:raise ValueError("invalid-terminal-state")
    authority=str(row.get("closure_authority") or "")
    evidence=[str(x) for x in (row.get("evidence_refs") or []) if str(x)]
    if state=="SCIENTIFIC_STOP":
        if authority not in CLOSURE_AUTHORITIES:raise ValueError("scientific-stop-needs-valid-closure-authority")
        if not evidence:raise ValueError("scientific-stop-needs-evidence")
        if row.get("retain_in_manuscript") is not False:raise ValueError("scientific-stop-cannot-remain-active")
    elif state=="ACTIVE_UNREFUTED_HYPOTHESIS":
        if authority:raise ValueError("active-unrefuted-cannot-have-closure-authority")
        if row.get("retain_in_manuscript") is not True:raise ValueError("active-unrefuted-must-remain-in-manuscript-pipeline")
        if row.get("claim_narrowing_required") is not False:raise ValueError("active-unrefuted-cannot-auto-narrow")
    elif state=="DUPLICATE_BASIN":
        if not str(row.get("duplicate_of_basin") or ""):raise ValueError("duplicate-basin-target-required")
        if row.get("unique_paper_credit") is not False:raise ValueError("duplicate-basin-cannot-get-unique-credit")
    elif state=="COMPLETE_PAPER":
        if row.get("unique_paper_credit") is not True:raise ValueError("complete-paper-needs-unique-credit")
        if not str(row.get("manuscript_artifact") or ""):raise ValueError("complete-paper-needs-manuscript")
        if row.get("paper_qa_pass") is not True:raise ValueError("complete-paper-needs-qa")


def compile_terminal_state(transaction:dict[str,Any],adjudications:list[dict[str,Any]])->dict[str,Any]:
    candidates={str(row.get("candidate_id") or ""):row for row in (transaction.get("candidates") or []) if isinstance(row,dict)}
    by={str(row.get("candidate_id") or ""):row for row in adjudications if isinstance(row,dict)}
    unknown=sorted(set(by)-set(candidates))
    if unknown:raise ValueError(f"unknown-candidate:{unknown}")
    rows=[]
    for cid,candidate in candidates.items():
        adj=by.get(cid)
        if adj is None:
            rows.append({"candidate_id":cid,"engine_id":candidate.get("engine_id"),"terminal_state":"ACTIVE_UNREFUTED_HYPOTHESIS","retain_in_manuscript":True,"claim_narrowing_required":False,"experiment_debt":["terminal adjudication pending"],"closure_authority":"","scientific_authority":False})
            continue
        validate_candidate_adjudication(adj);rows.append({**adj,"engine_id":candidate.get("engine_id"),"scientific_authority":False})
    estate=[]
    all_terminal=True
    for eid in ("D5","D2"):
        rr=[r for r in rows if r.get("engine_id")==eid];terminal=sum(r["terminal_state"] in TERMINAL_STATES for r in rr);all_terminal=all_terminal and terminal==len(rr)
        estate.append({"engine_id":eid,"candidates":len(rr),"complete_unique_papers":sum(r["terminal_state"]=="COMPLETE_PAPER" and r.get("unique_paper_credit") is True for r in rr),"scientific_stops":sum(r["terminal_state"]=="SCIENTIFIC_STOP" for r in rr),"duplicate_basins":sum(r["terminal_state"]=="DUPLICATE_BASIN" for r in rr),"active_unrefuted":sum(r["terminal_state"]=="ACTIVE_UNREFUTED_HYPOTHESIS" for r in rr),"terminal_resolved":terminal,"scientific_authority":False})
    winner=""
    if all_terminal:
        scores={r["engine_id"]:r["complete_unique_papers"] for r in estate};best=max(scores.values()) if scores else 0;tops=[k for k,v in scores.items() if v==best]
        if len(tops)==1:winner=tops[0]
    return {"schema_version":"1.0","transaction_id":transaction.get("transaction_id"),"status":"TERMINAL_COMPLETE" if all_terminal else "TERMINAL_IN_PROGRESS","policy":{"unrefuted_hypothesis_is_not_terminal_stop":True,"missing_evidence_is_experiment_debt":True,"winner_requires_all_candidates_terminal":True,"duplicate_basin_counts_zero_unique_papers":True},"engine_state":estate,"winner":winner,"winner_declared":bool(winner),"candidate_adjudications":rows,"scientific_authority":False}


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--transaction",type=Path,required=True);p.add_argument("--adjudications",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args();tx=json.loads(a.transaction.read_text());ads=json.loads(a.adjudications.read_text());rows=ads.get("adjudications") if isinstance(ads,dict) else ads;out=compile_terminal_state(tx,rows or []);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n");print(json.dumps({"status":out["status"],"engine_state":out["engine_state"],"winner":out["winner"]},ensure_ascii=False,indent=2))

if __name__=="__main__":main()
