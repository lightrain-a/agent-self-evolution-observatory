"""Reproduce B1/R5's zero-call L2 support-capacity gate from frozen assets.

This is an engineering reproducibility repair, not a scientific reopen. It never
reads outcome labels when selecting tasks and grants no experiment/model authority.
"""
from __future__ import annotations

import argparse, hashlib, json, re
from pathlib import Path
from typing import Any, Iterable

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
EXPERIMENT_ID = "D2-C45-R5-EXACT-INFORMATION-PROVENANCE"
RECONSTRUCTION_ID = "D2-C45-R5-L2-SUPPORT-RECONSTRUCTION-R8"
EXPECTED_SOURCE_SHA256 = "fc9b0011d384403f21534529da0397ca2aabf29fcb30c2dbb5a3c01c30b1387e"
EXPECTED_SOURCE_ROWS = 187
TARGET = 10
EXPECTED_ELIGIBLE = ["21", "25", "26", "163", "165"]
EXPECTED_FAMILY = ["21", "22", "23", "24", "25", "26", "163", "164", "165", "166", "167"]
ARCHIVE_COMMIT = "a82901a9c29d59b0e9da2ae680fab30fa5e82d34"
ARCHIVED = {
    "r5_capacity": {"path":"generated/d2-failure-memory-provenance-r5-support-capacity.json","sha256":"1027c72993f7563c0e7494cec5560469d3eba7fa1891d5b5042ad73b7b9584dc"},
    "r4_terminal": {"path":"generated/d2-failure-memory-provenance-r4-controlled-swap.json","sha256":"9a4d7ea1431dfd18951bf0ad4202e1f35795d1ba676089de60956f989e07f4c8","candidate_task_ids":["385","387","167","23","388","164"]},
    "bridge_support": {"path":"generated/d2-failure-memory-provenance-bridge-support.json","sha256":"b7db0c347ad63fd7efc0cb76c26f4014303c0ccef62b2a3303b876c9089dfcb0","candidate_task_ids":["125","360","228","126","362","229"]},
    "r6_crosscheck": {"path":"generated/d2-failure-memory-provenance-r6-early-action.json","sha256":"f3f55f07cad4c762b42727758aaa331848c654de7c32755d7ef563c96bca08e9"},
}
REVIEWER_RE = re.compile(r"^List out reviewers, if exist, who mention about .+$")
CRITICISM = "What are the main criticisms of this product? Please extract the relevant sentences."


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_sha(obj: Any) -> str:
    raw=json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()


def trajectory(value: Any) -> dict[str, Any]:
    obj=json.loads(value) if isinstance(value,str) else value
    if not isinstance(obj,dict): raise ValueError("trajectory_json must decode to object")
    return obj


def family(prompt: str) -> str|None:
    if REVIEWER_RE.fullmatch(prompt): return "REVIEWER_MENTION_QUERY"
    if prompt == CRITICISM: return "CRITICISM_SENTENCE_EXTRACTION"
    return None


def refs(obj: dict[str, Any]) -> list[str]:
    for rubric in obj.get("rubric_results") or []:
        checks=((rubric.get("details") or {}).get("checks") or {}) if isinstance(rubric,dict) else {}
        items=checks.get("must_include")
        if not isinstance(items,list): continue
        out=[]
        for item in items:
            val=(item or {}).get("ref") if isinstance(item,dict) else item
            val=str(val or "").strip()
            if val and val.upper() != "N/A": out.append(val)
        if out: return out
    return []


def prior_ids() -> set[str]:
    # R4 outcome-blind candidates remain "prior" even when excluded pre-outcome.
    # This is what prevents task 164 (literal-reference-leakage exclusion) reuse.
    return set(ARCHIVED["r4_terminal"]["candidate_task_ids"]) | set(ARCHIVED["bridge_support"]["candidate_task_ids"])


def build_manifest(records: Iterable[dict[str,Any]], source_sha: str, source_name: str) -> dict[str,Any]:
    if source_sha != EXPECTED_SOURCE_SHA256: raise ValueError("frozen source digest mismatch")
    rows=[dict(x) for x in records]; seen=set(); manifest=[]; prior=prior_ids()
    for row in rows:
        tid=str(row.get("task_id") or "").strip()
        if not tid or tid in seen: raise ValueError(f"missing/duplicate task_id: {tid!r}")
        seen.add(tid)
        prompt=str(row.get("task_prompt") or ""); fam=family(prompt)
        if not fam: continue
        rr=refs(trajectory(row.get("trajectory_json"))); blockers=[]
        if not rr: blockers.append("REFERENCE_ANSWER_CONTRACT_FAIL")
        if tid in prior: blockers.append("PRIOR_D2_TASK_ID_REUSE_FORBIDDEN")
        manifest.append({
            "task_id":tid,"prompt_family":fam,"task_prompt":prompt,
            "reference_contract":{"pass":bool(rr),"reference_count":len(rr),"reference_fingerprint":stable_sha(rr) if rr else None},
            "prior_d2_task_id":tid in prior,"eligible":not blockers,"blockers":blockers,
        })
    manifest.sort(key=lambda x:int(x["task_id"]))
    eligible=[x["task_id"] for x in manifest if x["eligible"]]
    prior_family=[x["task_id"] for x in manifest if x["prior_d2_task_id"]]
    ref_pass=sum(bool(x["reference_contract"]["pass"]) for x in manifest)
    return {
        "schema_version":"1.0","paper_id":PAPER_ID,"experiment_id":EXPERIMENT_ID,
        "reconstruction_id":RECONSTRUCTION_ID,"status":"RECONSTRUCTED_AND_VERIFIED_SUPPORT_CAPACITY_STOP",
        "reconstruction_role":"ENGINEERING_REPRODUCIBILITY_REPAIR_ONLY",
        "historical_binding":{"archive_commit":ARCHIVE_COMMIT,"archived_receipts":ARCHIVED,"historical_candidate_task_ids":EXPECTED_ELIGIBLE,"historical_maximum_possible_unique_tasks":5,"historical_model_requests_executed":0},
        "source":{"locator":f"content-addressed-cache:{source_name}","sha256":source_sha,"rows":len(rows)},
        "eligibility_contract":{
            "rule_provenance":"reconstructed from the historical R5 candidate set, archived appendix wording, exact released prompt inventory, and prior-D2 receipts; original regex text was not stored verbatim",
            "historical_rule_text_was_not_stored_verbatim":True,
            "selection_uses_outcome_fields":False,"outcome_fields_used":[],
            "prompt_rules":[r"^List out reviewers, if exist, who mention about .+$",CRITICISM],
            "reference_answer_rule":"non-empty non-N/A checks.must_include",
            "prior_d2_reuse_forbidden":True,
            "prior_candidate_semantics":"R4 outcome-blind candidate IDs count as prior even when excluded before downstream outcomes; task 164 is therefore excluded",
            "prior_d2_task_ids":sorted(prior,key=int),"unique_task_ids_only":True,
            "repeated_runs_do_not_increase_capacity":True,"target_unique_tasks":TARGET,
            "post_audit_rule_widening_forbidden":True,"post_audit_target_reduction_forbidden":True,
        },
        "summary":{"source_rows":len(rows),"review_family_rows":len(manifest),"reference_contract_pass_rows":ref_pass,"prior_d2_exclusions_in_review_family":prior_family,"eligible_unique_tasks":len(eligible),"eligible_task_ids":eligible,"target_unique_tasks":TARGET,"support_gate_pass":len(eligible)>=TARGET,"model_requests_executed":0,"scientific_outcomes_opened":False},
        "review_family_manifest":manifest,
        "adjudication":{"scientific_verdict":"NO_VERDICT_SUPPORT_FAILURE","support_failure_is_scientific_failure":False,"scientific_values_changed":False,"historical_5_of_10_value_reproduced":eligible==EXPECTED_ELIGIBLE},
        "authority":{"scientific":False,"experiment":False,"gpu":False,"model_calls":False,"submission":False},
    }


def validate(obj: dict[str,Any]) -> list[str]:
    s=obj.get("summary") or {}; m=obj.get("review_family_manifest") or []; errors=[]
    if (obj.get("source") or {}).get("sha256") != EXPECTED_SOURCE_SHA256: errors.append("source sha drift")
    if s.get("source_rows") != EXPECTED_SOURCE_ROWS: errors.append("row-count drift")
    if [x.get("task_id") for x in m] != EXPECTED_FAMILY: errors.append("review-family drift")
    if s.get("reference_contract_pass_rows") != 8: errors.append("reference-contract drift")
    if s.get("prior_d2_exclusions_in_review_family") != ["23","164","167"]: errors.append("prior-D2 exclusion drift")
    if s.get("eligible_task_ids") != EXPECTED_ELIGIBLE or s.get("eligible_unique_tasks") != 5: errors.append("5/10 result drift")
    if s.get("support_gate_pass") is not False or s.get("target_unique_tasks") != 10: errors.append("support gate must remain stopped")
    if s.get("model_requests_executed") != 0 or s.get("scientific_outcomes_opened") is not False: errors.append("execution occurred")
    if any((obj.get("authority") or {}).values()): errors.append("authority must remain zero")
    return errors


def build_reopen_contract(m: dict[str,Any]) -> dict[str,Any]:
    s=m["summary"]
    return {
        "schema_version":"1.0","paper_id":PAPER_ID,"experiment_id":EXPERIMENT_ID,
        "contract_id":"D2-C45-L2-FROZEN-REOPEN-CONTRACT-R8","status":"IDENTIFICATION_AND_SUPPORT_FROZEN_EXECUTION_BLOCKED",
        "role":"PROSPECTIVE_PRE_OUTCOME_REOPEN_SPEC_NO_EXECUTION_AUTHORITY",
        "identification_target":{"estimand":"Delta_L(m,x') = E[Y | M=m, do(L=F), x', E] - E[Y | M=m, do(L=S), x', E]","actionable_memory":"M=m byte-identical across L_F and L_S","treatment":"visible provenance metadata only","independent_unit":"unique task","held_fixed":["future query x'","future evidence/state E","actionable memory bytes m","all non-provenance paired inputs"]},
        "support_contract":{"manifest_reconstruction_id":m["reconstruction_id"],"source_sha256":m["source"]["sha256"],"target_unique_tasks":TARGET,"current_eligible_unique_tasks":s["eligible_unique_tasks"],"current_eligible_task_ids":s["eligible_task_ids"],"current_support_gate_pass":False},
        "current_execution_gate":{"model_calls_permitted":False,"scientific_outcome_execution_permitted":False,"current_model_call_budget":0,"l3_transition_permitted":False,"blocking_reasons":["frozen support capacity 5 < target 10","no current scientific/model-call authority","archived R5 lacks complete runtime/statistical binding"]},
        "execution_bindings_still_required_before_any_future_call":["exact executor/model identity and version","exact L_F/L_S metadata serialization with no other byte changes","paired seed/repetition schedule and max request budget","terminal scorer/parser","task-level estimator and exact/randomization test","effect/significance decision rule","support-failure and no-post-outcome-replacement rule"],
        "reopen_condition":{"all_required":True,"conditions":["new content-addressed pre-outcome asset gives >=10 unique eligible tasks under same rules","missing runtime/statistical bindings frozen pre-outcome","separate scientific authority reopens L2","separate experiment/model-call authority permits budget"],"forbidden_repairs":["lower target","widen prompt family","relax reference contract","reuse prior D2 task IDs","count repeated runs as independent","use L1/R4/R6 outcomes to select L2 tasks"]},
        "scientific_values_changed":False,"scientific_authority":False,"experiment_authority":False,"gpu_authority":False,
    }


def build_analysis_gate(m: dict[str,Any], c: dict[str,Any]) -> dict[str,Any]:
    s=m["summary"]
    return {
        "schema_version":"1.0","paper_id":PAPER_ID,"gate_id":"D2-C45-L2-ANALYSIS-GATE-R8",
        "status":"STOP_SUPPORT_CAPACITY_NO_EXECUTION","decision":"KEEP_L2_UNEXECUTED_AND_DO_NOT_ADVANCE_TO_L3_EXECUTION",
        "inputs":{"manifest_reconstruction_id":m["reconstruction_id"],"reopen_contract_id":c["contract_id"],"source_sha256":m["source"]["sha256"]},
        "facts":{"target_unique_tasks":TARGET,"eligible_unique_tasks":s["eligible_unique_tasks"],"eligible_task_ids":s["eligible_task_ids"],"support_gate_pass":False,"model_requests_executed":0,"scientific_outcomes_opened":False},
        "interpretation":"The historical 5-of-10 support stop is independently reproducible from the exact released shopping parquet and archived prior-D2 receipts. This repairs evidence provenance only; it does not repair L2 scientifically.",
        "l3_policy":"L3 source-faithful transport execution remains downstream debt and is not opened by an L2 support failure. Offline asset census is support work only.",
        "scientific_verdict":"NO_VERDICT_SUPPORT_FAILURE","scientific_values_changed":False,
        "scientific_authority":False,"experiment_authority":False,"gpu_authority":False,"submission_authority":False,
    }


def load_parquet(path: Path) -> list[dict[str,Any]]:
    try: import pandas as pd  # type: ignore
    except ModuleNotFoundError as e: raise RuntimeError("use an existing pandas+pyarrow environment") from e
    return [dict(x) for x in pd.read_parquet(path).to_dict(orient="records")]


def dump(path: Path, obj: dict[str,Any]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")


def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--source-parquet",type=Path,required=True); p.add_argument("--output-dir",type=Path,default=Path("generated")); a=p.parse_args()
    source_sha=sha256(a.source_parquet)
    m=build_manifest(load_parquet(a.source_parquet),source_sha,a.source_parquet.name)
    errors=validate(m)
    if errors: raise SystemExit("invalid reconstruction: "+"; ".join(errors))
    c=build_reopen_contract(m); g=build_analysis_gate(m,c)
    dump(a.output_dir/"d2-failure-memory-provenance-r5-eligibility-manifest-r8.json",m)
    dump(a.output_dir/"d2-failure-memory-provenance-l2-reopen-contract-r8.json",c)
    dump(a.output_dir/"d2-failure-memory-provenance-l2-analysis-gate-r8.json",g)
    print(json.dumps({"status":g["status"],"source_sha256":source_sha,"eligible_unique_tasks":m["summary"]["eligible_unique_tasks"],"eligible_task_ids":m["summary"]["eligible_task_ids"],"target_unique_tasks":TARGET,"model_requests_executed":0,"scientific_authority":False,"experiment_authority":False},ensure_ascii=False))


if __name__ == "__main__": main()
