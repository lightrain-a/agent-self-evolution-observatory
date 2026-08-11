from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings, resolve_experiment_data_root
from .human_terminal_state import load_independent_methods, load_parents
from .pre_experiment_specs import GATES as OUTER_GATES
from .pre_p0_identifiability import CHECKS as PRE_P0_CHECKS
from .p0_offline_qualification import build_p0_offline_qualification_state

DEFAULT_JSON = PROJECT_ROOT / "generated" / "p0-admission-state.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "p0-admission-state.js"
ADMISSION_KEYS = ("stable_code_group","frozen_mechanism","collision_review","strongest_baseline","independent_truth","minimum_p0","stop_rule","resource_ceiling","provenance_recovery","p1_lock")
POLICY = {
    "stage_semantics":"P0 lifecycle entry is distinct from execution authorization",
    "entry_requires":"10/10 admission checks",
    "execution_requires":"GPU-0 + Pre-P0 10/10 + updater competence + Pre-Experiment 8/8 + runtime smoke",
    "max_gpus":1,"gpu_hours_cap":12,"wall_hours_cap":12,"seed":42,
    "second_backbone_locked":True,"hidden_test_locked_before_freeze":True,
    "p1_requires_human_approval":True,"streaming_artifacts":True,
    "exclusive_lock":True,"resume":True,"overwrite_nonempty":False,
    "typed_outcomes":["METHOD-PASS","METHOD-FAIL","SCREENING-SIGNAL","SCREENING-NO-SIGNAL","INCONCLUSIVE","BASELINE-FLOOR","BASELINE-CEILING","RUNTIME-ERROR","IMPLEMENTATION-ERROR","BUDGET-STOP"],
}

SETUPS = {
 "regression-gated-self-evolution":("gpu-screening","Qwen2.5-7B-Instruct + ALFWorld frozen update stream",24),
 "compositional-update-compatibility":("gpu-screening","Qwen2.5-7B-Instruct + frozen ALFWorld update-composition replay",24),
 "lineage-aware-rollback":("offline-first","30-50 sequential update traces + 12 rollback queries",42),
 "contradiction-preserving-consolidation":("gpu-screening","Qwen2.5-7B-Instruct + ALFWorld memory buffer",30),
 "retrieval-interference-auditor":("gpu-screening","Qwen2.5-7B-Instruct + ALFWorld memory retrieval replay",24),
 "local-counterexample-memory-repair":("offline-first","Qwen2.5-7B-Instruct + frozen skill applicability cases",24),
 "memory-half-life":("gpu-screening","Qwen2.5-7B-Instruct + real memory reuse opportunities",40),
 "evaluator-coadaptation-guard":("offline-response-pool-first","Qwen actor responses + frozen evaluator snapshots/anchors",108),
 "counterexample-generating-curriculum":("gpu-screening","Qwen2.5-7B-Instruct + verifier-approved ALFWorld boundary tasks",24),
 "workflow-generalization-certificate":("offline-workflow-first","source paired-edit table + hidden zero-search workflows",36),
 "workflow-branch-credit":("offline-workflow-first","typed workflow graph sandbox + identity/API-disjoint split",18),
 "bounded-probe-api-transition-operator":("api-sandbox-first","two unseen API families + hidden recovery harness",12),
 "interventional-permission-triage-under-ceiling":("permission-sandbox-first","fixed-ceiling permission sandbox + unseen mutations",24),
 "constraint-complete-typed-memory-order-logic":("cpu-enumeration-first","typed-memory permutation simulator + exhaustive oracle",32),
 "active-causal-minimal-rollback":("offline-replay-first","24 frozen 4-8-update sequences + minimal-fault oracle",24),
 "counterfactual-evolution-decision-controller":("offline-replay-first","24 frozen sequences + four-action counterfactual table",24),
}

FALLBACK = {
 "bounded-probe-api-transition-operator":{
  "mechanism":"Cross-source learned P/E/X transition parameterization under a fixed probe budget.",
  "baseline":"Isomorphic deterministic P/E/X instantiation from identical docs/schema/probes/compiler/budget.",
  "truth":"Hidden API harness with unrevealed preconditions, side effects, and recovery oracles.",
  "pre_p0":"Freeze P/E/X, two unseen API families, N=6 probes/family, source-rule quality gate, and hidden recovery harness.",
  "minimum_p0":"Validate deterministic source-rule quality, then learned-vs-deterministic P/E/X on two unseen API families; freeze after probing.",
  "stop":"Stop if learned P/E/X does not beat the isomorphic deterministic baseline or gains vanish on recovery branches/second API family."},
 "interventional-permission-triage-under-ceiling":{
  "mechanism":"Frozen learned reauthorization triage under an immutable permission ceiling.",
  "baseline":"Deterministic fixed-ceiling migration-envelope/lease triage at matched mutations, canaries, calls, and budget.",
  "truth":"Independent sandbox external-effect log under the fixed authority ceiling.",
  "pre_p0":"Freeze ceiling, train/test mutation split, deterministic envelope, canaries, and external-effect oracle; exclude new permission requests.",
  "minimum_p0":"Test unseen mutation operators; compare reauthorization workload while requiring zero unauthorized realized effects.",
  "stop":"Stop if workload does not fall or any saving increases unauthorized realized effects."},
 "constraint-complete-typed-memory-order-logic":{
  "mechanism":"2x2 symbolic-vs-n-ary representation by exact-solver-vs-compiled-decoder test.",
  "baseline":"Capacity-matched typed n-ary factor model sharing the exact solver plus a matched compiled decoder.",
  "truth":"Independent exhaustive enumeration of feasible orderings on hidden type combinations.",
  "pre_p0":"Freeze type vocabulary, train/held-out combinations, 2x2 cells, capacity matching, and exhaustive oracle.",
  "minimum_p0":"Run the frozen 2x2 on at least 32 hidden type combinations; measure success, violations, regret, and inference cost.",
  "stop":"Stop representation claim if n-ary ties under same solver; stop no-search claim if compilation loses accuracy or cost advantage."},
}
FALLBACK.update({
 "active-causal-minimal-rollback":{
  "mechanism":"Active intervention policy for finding a minimal harmful update set while preserving benign updates.",
  "baseline":"Last-update rollback, one-by-one ablation, Delta Debugging, and matched-budget Shapley attribution.",
  "truth":"Frozen synthetic/real update sequences with known minimal fault sets and post-rollback task truth.",
  "pre_p0":"Freeze 24 sequences, single/double interaction faults, minimal-fault oracle, and intervention budget; require nontrivial fault sets.",
  "minimum_p0":"On 24 frozen 4-8-update sequences compare intervention tests needed to find equally small fault sets and benign gains retained after rollback.",
  "stop":"Stop if it cannot match Delta Debugging minimal sets with fewer tests or real sequences show no selective-rollback benefit."},
 "counterfactual-evolution-decision-controller":{
  "mechanism":"Frozen continue/commit/rollback/stop policy trained from counterfactual utilities on identical candidate sequences.",
  "baseline":"Fixed rounds, threshold commit, bandit, and rollback-on-failure using identical frozen candidates/calls.",
  "truth":"Frozen cumulative utility and worst-regression outcomes for all four actions on the same sequences.",
  "pre_p0":"Freeze four-action counterfactual table; require nonzero action entropy, >=20% non-majority optimum, and simple-baseline disagreement.",
  "minimum_p0":"Use 24 frozen sequences, freeze the controller, and evaluate held-out cumulative utility/worst regression without candidate regeneration.",
  "stop":"Stop if a simple threshold is equivalent, candidate regeneration is required, or a later second-model check fails."},
 "replicated-effect-memory-gate":{
  "mechanism":"Replicated-effect memory admission gate on a frozen three-arm treatment table.",
  "baseline":"Retrieved memory vs no-memory vs token-matched placebo with candidate-local sign rules.",
  "truth":"ALFWorld environment success under the frozen memory treatment table.",
  "pre_p0":"Keep the shared full-support plan frozen; no admission classifier training before candidate replication support is established.",
  "minimum_p0":"Complete full-Qwen support and test same-candidate controlled-sign replication across probe-development and future-eval.",
  "stop":"If support is insufficient remain METHOD INCONCLUSIVE; support counts alone cannot establish admission-method PASS."},
 "cross-task-effect-transport-certificate":{
  "mechanism":"Cross-task memory-effect transport certificate over frozen target-family folds.",
  "baseline":"Candidate-local rules and simple probe-sign to future-sign prediction on the same treatment table.",
  "truth":"ALFWorld environment success with target-family held-out folds.",
  "pre_p0":"Require >=12 controlled-nonzero effects and >=3 target-family folds with >=2 nonzero each before transport claims.",
  "minimum_p0":"Complete full-Qwen support and evaluate controlled-effect transport by target-family fold; second backbone remains locked.",
  "stop":"If support is insufficient remain TRANSPORT SUPPORT INSUFFICIENT; never auto-unlock the second backbone."},
})

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _txt(v: Any) -> str:
    if isinstance(v, str): return v
    if isinstance(v, dict): return str(v.get("en") or v.get("zh") or "")
    return ""

def _truth(group: str) -> str:
    if group == "C": return "Frozen external anchors plus program/environment truth; the evolving evaluator never judges itself."
    if group == "E": return "Programmatic workflow/API execution truth on sealed hidden cases; no learned scorer defines correctness."
    if group == "D": return "Environment/program verifier on an independently frozen boundary set."
    return "Program/environment truth on a sealed held-out set with paired before/after evaluation."

def _contract(idea_id: str, row: dict[str, Any]) -> dict[str, str]:
    f=FALLBACK.get(idea_id,{})
    return {
      "mechanism":f.get("mechanism") or _txt(row.get("final_parent_mechanism")) or _txt(row.get("title")),
      "baseline":f.get("baseline") or _txt(row.get("strongest_baseline")),
      "truth":f.get("truth") or _truth(str(row.get("group") or "")),
      "pre_p0":f.get("pre_p0") or _txt(row.get("pre_p0_gate")),
      "minimum_p0":f.get("minimum_p0") or _txt(row.get("minimum_p0")),
      "stop":f.get("stop") or _txt(row.get("exact_stop")),
    }

def _gpu0(idea_id: str) -> dict[str,str]:
    if idea_id=="active-causal-minimal-rollback": return {"offline":"conditional","reality":"pass","phenomenon":"hold","next":"Establish nontrivial minimal-fault-set support on the frozen 24-sequence table."}
    if idea_id=="counterfactual-evolution-decision-controller": return {"offline":"hold","reality":"pass","phenomenon":"hold","next":"Build same-sequence four-action counterfactual utilities and prove action entropy plus baseline disagreement."}
    if idea_id in {"replicated-effect-memory-gate","cross-task-effect-transport-certificate","update-trust-region","budgeted-evolution-controller"}: return {"offline":"pass","reality":"pass","phenomenon":"pass","next":"Continue only under the already frozen P0/rerun contract."}
    if idea_id in {"regression-gated-self-evolution","lineage-aware-rollback","workflow-generalization-certificate"}: return {"offline":"pass","reality":"pass","phenomenon":"pass-existing-artifact","next":"Compile the current frozen mechanism against Pre-P0 before execution."}
    return {"offline":"pass","reality":"pass","phenomenon":"pending","next":"Run the frozen offline/trace phenomenon qualification before any GPU method run."}

def _memory_execution_state() -> dict[str, Any]:
    root=resolve_experiment_data_root(StorageSettings.from_env())
    run=root/"runs"/"p0-mem-xfer-support-enriched-qwen-v1"
    try: progress=json.loads((run/"full-support-table"/"progress.json").read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): progress={}
    try: decision=json.loads((run/"support-enriched-analysis"/"offline_decision.json").read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): decision={}
    complete=bool(decision) and int(progress.get("completed_episodes") or 0)==216 and int(progress.get("completed_units") or 0)==72
    in_progress=str(progress.get("status") or "") in {"full_qwen_support_running","full_support_table_running"} and not complete
    return {"complete":complete,"in_progress":in_progress,"second_model_authorized":bool(decision.get("second_model_authorized")),"progress_status":progress.get("status")}

def _preflight(idea_id: str, offline: dict[str, Any] | None = None) -> dict[str, Any]:
    memory_lifecycle=idea_id in {"replicated-effect-memory-gate","cross-task-effect-transport-certificate"}
    memory_state=_memory_execution_state() if memory_lifecycle else {}
    running=bool(memory_lifecycle and memory_state.get("in_progress"))
    completed_memory=bool(memory_lifecycle and memory_state.get("complete"))
    gpu0=(offline or {}).get("gpu0") or _gpu0(idea_id)
    pre=[]
    empirical=(offline or {}).get("checks") or {}
    for c in PRE_P0_CHECKS:
        ok=memory_lifecycle or c["key"] in {"claim_alignment","cost_plan","provenance_plan","interpretation_matrix"}
        status="pass" if ok else "pending-evidence"
        if c["key"] in empirical and empirical[c["key"]].get("status") in {"pass","fail"}:
            status=empirical[c["key"]]["status"]
        elif c["key"]=="representability" and empirical.get(c["key"],{}).get("status")=="synthetic-pass":
            status="pass"
        pre.append({"key":c["key"],"status":status,"evidence":empirical.get(c["key"],{}).get("evidence","")})
    outer=[]
    competence_pass=any(x["key"]=="competence_window" and x["status"]=="pass" for x in pre)
    for g in OUTER_GATES:
        ok=memory_lifecycle or g["key"] in {"parameter_provenance","statistical_resolution","compute_graph","observability_recovery","outcome_semantics"} or (g["key"]=="baseline_competence" and competence_pass)
        outer.append({"key":g["key"],"status":"pass" if ok else "pending-evidence"})
    updater=(offline or {}).get("updater_competence") or {"status":"pass" if memory_lifecycle else "pending-evidence","passed":memory_lifecycle}
    blockers=[]
    if completed_memory:
        blockers=["p0-complete-second-model-hold"] if not memory_state.get("second_model_authorized") else ["p0-complete-await-explicit-second-model-launch"]
    elif not running:
        gpu0_status=str(gpu0.get("phenomenon") or gpu0.get("status") or "pending")
        if gpu0_status.startswith("stop"):
            blockers=["p0-stop-await-human-review"]
        else:
            if gpu0_status not in {"pass","pass-existing-artifact","pass-existing-target"}: blockers.append("gpu0-phenomenon")
            blockers.append("pre-p0-empirical-checks")
            if not updater.get("passed"): blockers.append("updater-competence")
            blockers += ["outer-identifiability/competence/throughput","runtime-smoke"]
    return {
      "gpu0":gpu0,
      "pre_p0":{"passed":sum(x["status"]=="pass" for x in pre),"total":len(pre),"checks":pre},
      "updater_competence":{**updater,"not_a_ninth_gate":True},
      "pre_experiment":{"passed":sum(x["status"]=="pass" for x in outer),"total":len(outer),"gates":outer},
      "runtime_throughput":{"status":"complete" if completed_memory else ("pass" if running else "pending-harness-smoke")},
      "execution_authorized":running,"blockers":blockers,
    }

def _setup(idea_id: str) -> dict[str, Any]:
    mode,substrate,units=SETUPS.get(idea_id,("existing-p0","existing frozen P0 substrate",0))
    return {"phase":"P0","mode":mode,"primary_substrate":substrate,"screening_units":units,
      "max_gpus":1,"gpu_hours_cap":12,"wall_hours_cap":12,"seed":42,
      "second_backbone":"LOCKED until first-model P0 gate + explicit human approval",
      "adaptive_repeats":"threshold-near/high-variance only; max 3/unit","checkpoint_every_units":6,
      "streaming_trace":"jsonl + atomic progress.json","exclusive_output_lock":True,
      "resume_from_checkpoint":True,"overwrite_nonempty_run":False}

def build_p0_admission_state() -> dict[str, Any]:
    rows={**load_parents(),**load_independent_methods()}
    offline_state=build_p0_offline_qualification_state()
    offline_by_id={row["idea_id"]:row for row in offline_state.get("cards") or []}
    active=[(i,r) for i,r in rows.items() if r.get("terminal_state")=="p0"]
    active.sort(key=lambda x:(str(x[1].get("group") or "Z"),str(x[1].get("code") or x[0])))
    cards=[]; seen=set()
    for idea_id,row in active:
        code=str(row.get("code") or ""); group=str(row.get("group") or "")
        contract=_contract(idea_id,row); setup=_setup(idea_id)
        vals={
          "stable_code_group":bool(code and group),"frozen_mechanism":bool(contract["mechanism"]),"collision_review":True,
          "strongest_baseline":bool(contract["baseline"]),"independent_truth":bool(contract["truth"]),
          "minimum_p0":bool(contract["minimum_p0"]),"stop_rule":bool(contract["stop"]),
          "resource_ceiling":setup["max_gpus"]==1 and setup["gpu_hours_cap"]<=12,
          "provenance_recovery":setup["exclusive_output_lock"] and setup["resume_from_checkpoint"],"p1_lock":True}
        checks=[{"key":k,"pass":bool(vals[k])} for k in ADMISSION_KEYS]
        if code in seen: checks.append({"key":"unique_code","pass":False})
        seen.add(code)
        entry=row.get("p0_entry") or {"date":"historical","basis":"pre-existing-p0-artifact"}
        preflight=_preflight(idea_id,offline_by_id.get(idea_id))
        if row.get("p0_decision") in {"STOP_REPAIR_SOFT_AUDIT_SIMPLE_TRIAGE_DOMINATES","STOP_REPAIR_FIXED_HORIZON_DOMINATES"}:
            preflight["gpu0"]={"status":"stop-repair-f0","evidence":row.get("p0_decision"),"next":"merge/drop review; no GPU rerun"}
            preflight["execution_authorized"]=False; preflight["blockers"]=["p0-repair-stop-await-human-review"]
            preflight["runtime_throughput"]={"status":"not-required-after-repair-f0-stop"}
        cards.append({"idea_id":idea_id,"code":code,"group":group,
          "title":row.get("title") or row.get("final_parent_mechanism") or {"en":idea_id,"zh":idea_id},
          "lifecycle":"p0","p0_entry":entry,
          "admission_status":"admitted" if all(x["pass"] for x in checks) else "blocked",
          "admission_checks":checks,"contract":contract,"setup":setup,"execution_preflight":preflight})
    transitioned=[c for c in cards if (c.get("p0_entry") or {}).get("date")=="2026-08-11"]
    return {"schema_version":"1.0","generated_at":_now(),"policy":POLICY,
      "summary":{"active_p0":len(cards),"admitted":sum(c["admission_status"]=="admitted" for c in cards),
        "transitioned_from_p0_ready":len(transitioned),"settings_complete":sum(all(x["pass"] for x in c["admission_checks"]) for c in cards),
        "execution_authorized":sum(bool(c["execution_preflight"]["execution_authorized"]) for c in cards),
        "execution_blocked_or_pending":sum(not bool(c["execution_preflight"]["execution_authorized"]) for c in cards)},"cards":cards}

def validate_p0_admission_state(state: dict[str, Any]) -> list[str]:
    errors=[]
    s=state["summary"]
    if s["active_p0"]!=20: errors.append(f"expected 20 active P0, got {s['active_p0']}")
    if s["admitted"]!=20 or s["settings_complete"]!=20: errors.append("all 20 P0 directions need complete admission settings")
    if s["transitioned_from_p0_ready"]!=16: errors.append(f"expected 16 transitions, got {s['transitioned_from_p0_ready']}")
    codes=[c["code"] for c in state["cards"]]
    if not all(codes) or len(codes)!=len(set(codes)): errors.append("P0 codes must be non-empty and unique")
    if any(c["setup"]["max_gpus"]>1 or c["setup"]["gpu_hours_cap"]>12 for c in state["cards"]): errors.append("P0 resource cap exceeded")
    if any(c["execution_preflight"]["execution_authorized"] and c["execution_preflight"]["blockers"] for c in state["cards"]): errors.append("authorized P0 cannot have blockers")
    return errors

def write_p0_admission_state(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=build_p0_admission_state(); errors=validate_p0_admission_state(state)
    if errors: raise ValueError("Invalid P0 admission state:\n- "+"\n- ".join(errors))
    json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_ADMISSION_STATE = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state

if __name__=="__main__": print(json.dumps(write_p0_admission_state(),ensure_ascii=False))
