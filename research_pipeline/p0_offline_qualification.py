from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings, resolve_experiment_data_root
from .p0_offline_evidence import alfworld, a1, a2, a3_panel, a67_dataset, memory, e1
from .p0_realizability_suite import build_p0_realizability_suite

DEFAULT_JSON = PROJECT_ROOT / "generated" / "p0-offline-qualification.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "p0-offline-qualification.js"
EMPIRICAL = ("target_variation","baseline_disagreement","representability","tiny_overfit","competence_window","effect_variation")
NEXT_ACTION = {
    "regression-gated-self-evolution":"Repair updater/action-stream competence, then collect a fresh ALFWorld candidate batch and replay the frozen 6-task mastered panel.",
    "compositional-update-compatibility":"Collect a frozen pair/order/rollback composition matrix with held-out update identities and template×surface splits.",
    "lineage-aware-rollback":"Extend to 30–50 sequential updates and 12 frozen rollback queries; compare matched-storage periodic checkpoints.",
    "contradiction-preserving-consolidation":"Build >=30 reproducible conclusion-change deletion cases and matched NLI/utility selection sets before hidden evaluation.",
    "retrieval-interference-auditor":"Collect candidate co-retrieval pairs and randomized retrieval/content/rank/co-retrieval arms at matched audit cost.",
    "local-counterexample-memory-repair":"Freeze a real skill/predicate vocabulary and collect boundary counterexamples plus old-positive protection cases.",
    "memory-half-life":"Collect repeated real reuse opportunities with matched memory ON/OFF utility labels under the frozen 20% audit budget.",
    "evaluator-coadaptation-guard":"Build a 3×3 actor/evaluator cross-version score matrix with frozen external anchors before any rubric repair.",
    "counterexample-generating-curriculum":"Generate verifier-valid boundary perturbations and measure how often delta debugging reaches 1-minimal counterexamples.",
    "workflow-generalization-certificate":"Rebuild the source paired edit-effect table until within-workflow edit deltas are genuinely non-tied; keep hidden workflows sealed.",
    "workflow-branch-credit":"Collect identity/API-disjoint workflow failures and matched group interventions to test recurring causal motifs.",
    "bounded-probe-api-transition-operator":"Freeze two unseen API families, N=6 target probes/family, deterministic P/E/X rule-quality gate, and hidden recovery harness.",
    "interventional-permission-triage-under-ceiling":"Freeze permission ceiling, mutation-family split, deterministic envelope baseline, canaries, and external-effect oracle.",
    "constraint-complete-typed-memory-order-logic":"Run the CPU 2×2 representation×decoder P0 on >=32 hidden type combinations with exhaustive ordering truth.",
    "active-causal-minimal-rollback":"Collect non-prefix enable/disable interventions and independent minimal-fault truth on 24 frozen 4–8-update sequences.",
    "counterfactual-evolution-decision-controller":"Replay continue/commit/rollback/stop from the same frozen states without regenerating candidates; then fit only if all four actions have support.",
}
NEW_IDS = (
    "regression-gated-self-evolution","compositional-update-compatibility","lineage-aware-rollback",
    "contradiction-preserving-consolidation","retrieval-interference-auditor","local-counterexample-memory-repair",
    "memory-half-life","evaluator-coadaptation-guard","counterexample-generating-curriculum",
    "workflow-generalization-certificate","workflow-branch-credit","bounded-probe-api-transition-operator",
    "interventional-permission-triage-under-ceiling","constraint-complete-typed-memory-order-logic",
    "active-causal-minimal-rollback","counterfactual-evolution-decision-controller",
)

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _ck(status: str, evidence: str, source: str = "", kind: str = "real-reused") -> dict[str, Any]:
    return {"status":status,"evidence":evidence,"source":source,"evidence_kind":kind}

def _pending() -> dict[str, Any]:
    return _ck("pending", "No mechanism-aligned real offline evidence has cleared this check yet.", kind="pending")

def _updater_config(name: str) -> dict[str, Any]:
    path=PROJECT_ROOT/"research_pipeline"/name
    try: d=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): return {"status":"pending","passed":False,"source":f"research_pipeline/{name}","reason":"updater competence config unavailable"}
    u=(d.get("pre_experiment") or {}).get("updater_competence") or {}
    return {"status":str(u.get("status") or "pending"),"passed":bool(u.get("passed")),"decision":u.get("decision"),"evidence":u.get("evidence") or {},"reason":str(u.get("reason") or ""),"source":f"research_pipeline/{name}"}

def _base_card(idea: str, aw: dict[str, Any]) -> dict[str, Any]:
    checks = {key:_pending() for key in EMPIRICAL}
    if idea in {"regression-gated-self-evolution","compositional-update-compatibility","lineage-aware-rollback","contradiction-preserving-consolidation","retrieval-interference-auditor","local-counterexample-memory-repair","memory-half-life","counterexample-generating-curriculum","workflow-generalization-certificate","active-causal-minimal-rollback","counterfactual-evolution-decision-controller"} and aw["passed"]:
        checks["competence_window"] = _ck("pass", f"Qwen2.5-7B OOD qualification: {aw['successes']}/{aw['total']}={aw['success_rate']:.3f}, successes in {aw['task_types_with_success']} task families.", aw["source"])
    return {"idea_id":idea,"gpu0":{"status":"pending","evidence":"Run the frozen mechanism-specific offline/trace phenomenon gate.","evidence_kind":"pending"},"checks":checks}

def _apply_a1(card: dict[str, Any], ev: dict[str, Any]) -> None:
    if card["idea_id"] != "regression-gated-self-evolution": return
    c=card["checks"]
    c["target_variation"]=_ck("pass",f"A-1 screening contains {ev['harmful_candidates']} harmful candidate updates; hidden-regression target is non-constant.",ev["source"])
    c["effect_variation"]=_ck("pass",f"Matched acceptance changed harmful-update count with point reduction {ev['harmful_reduction']:.3f} and target-gain loss {ev['target_gain_loss']:.3f}.",ev["source"])
    c["representability"]=_ck("fail",f"Existing probe panel fidelity failed: LOO AUC={ev['panel_auc']:.3f}, best probe={ev['best_probe_auc']:.3f}, required>={ev['min_auc']:.2f}.",ev["source"])
    card["gpu0"]={"status":"hold","evidence":"Update-harm phenomenon exists, but the current probe representation is not faithful enough for the predictive regression panel.","source":ev["source"],"evidence_kind":"real-reused"}

def _apply_a2(card: dict[str, Any], ev: dict[str, Any]) -> None:
    if card["idea_id"] not in {"lineage-aware-rollback","active-causal-minimal-rollback","counterfactual-evolution-decision-controller"} or ev["sequences"]<9: return
    c=card["checks"]
    c["target_variation"]=_ck("pass",f"9 frozen sequences have optimal-round entropy {ev['entropy_bits']:.3f} bits and {ev['non_early']} non-early optima.",ev["source"])
    c["effect_variation"]=_ck("pass",f"{ev['harm_after_best']}/9 sequences become worse after their best round; {ev['positive_gain_sequences']}/9 contain positive update gain.",ev["source"])
    status={"lineage-aware-rollback":"partial-pass","active-causal-minimal-rollback":"conditional","counterfactual-evolution-decision-controller":"pass-existing-target"}[card["idea_id"]]
    msg={"lineage-aware-rollback":"Sequential rollback need is real, but long-history compaction itself is not yet qualified.","active-causal-minimal-rollback":"Rollback/harm is real, but minimal-fault-set support is not established.","counterfactual-evolution-decision-controller":"Same-sequence decision target is non-degenerate; learner/baseline separation is still unproven."}[card["idea_id"]]
    card["gpu0"]={"status":status,"evidence":msg,"source":ev["source"],"evidence_kind":"real-reused"}

def _apply_memory(card: dict[str, Any], ev: dict[str, Any]) -> None:
    if card["idea_id"] not in {"contradiction-preserving-consolidation","retrieval-interference-auditor","memory-half-life"} or ev["decision"]!="SUPPORT_QUALIFICATION_PASS": return
    c=card["checks"]
    c["target_variation"]=_ck("pass",f"Memory treatment table has {ev['nonzero']}/{ev['units']} controlled nonzero units across {ev['families']} target families.",ev["source"])
    c["effect_variation"]=_ck("pass",f"Controlled effects include both harm ({ev['harm']}) and benefit ({ev['benefit']}).",ev["source"])
    card["gpu0"]={"status":"partial-pass","evidence":"Memory effects are real, but this direction still needs its deletion/co-retrieval/reuse-specific phenomenon gate.","source":ev["source"],"evidence_kind":"real-reused"}

def _apply_e1(card: dict[str, Any], ev: dict[str, Any]) -> None:
    if card["idea_id"]!="workflow-generalization-certificate": return
    c=card["checks"]
    c["target_variation"]=_ck("fail",f"Old edit table is ranking-degenerate: only {ev['effective_workflows']}/{ev['workflows']} workflows have any positive edit and only {ev['uniquely_ranked_workflows']} have non-tied edit deltas.",ev["source"])
    c["effect_variation"]=_ck("fail",f"Effective workflow fraction={ev['effective_fraction']:.3f}; current paired table cannot identify a best-edit ranking policy.",ev["source"])
    card["gpu0"]={"status":"hold","evidence":"Do not open hidden workflows. Rebuild a paired edit-effect table with genuine within-workflow edit variation first.","source":ev["source"],"evidence_kind":"real-reused"}

def _apply_d1(card: dict[str, Any], aw: dict[str, Any]) -> None:
    if card["idea_id"]!="counterexample-generating-curriculum" or not aw["passed"]: return
    card["checks"]["target_variation"]=_ck("pass",f"Base OOD set contains both successes ({aw['successes']}) and failures ({aw['total']-aw['successes']}); boundary candidates can exist.",aw["source"])
    card["gpu0"]={"status":"conditional","evidence":"Task failures are real; 1-minimal boundary-counterexample prevalence is still unmeasured.","source":aw["source"],"evidence_kind":"real-reused"}

def build_p0_offline_qualification_state() -> dict[str, Any]:
    root=resolve_experiment_data_root(StorageSettings.from_env())
    aw,aa1,aa2,a3p,a67,mem,we1=alfworld(root),a1(root),a2(root),a3_panel(root),a67_dataset(root),memory(root),e1(root)
    up_a1=_updater_config("p0_a1_screening_config.json"); up_a2=_updater_config("p0_a2_screening_config.json")
    realizability=build_p0_realizability_suite(); realizability_by_id={row["idea_id"]:row for row in realizability.get("rows") or []}
    cards=[]
    for idea in NEW_IDS:
        card=_base_card(idea,aw)
        card["updater_competence"]={"status":"pending","passed":False,"evidence_kind":"pending","reason":"mechanism-specific updater/action-stream competence has not been qualified"}
        if idea=="regression-gated-self-evolution": card["updater_competence"]={**up_a1,"evidence_kind":"real-reused"}
        elif idea in {"lineage-aware-rollback","active-causal-minimal-rollback","counterfactual-evolution-decision-controller"}: card["updater_competence"]={**up_a2,"evidence_kind":"real-reused"}
        _apply_a1(card,aa1); _apply_a2(card,aa2); _apply_memory(card,mem); _apply_e1(card,we1); _apply_d1(card,aw)
        synthetic=realizability_by_id.get(idea)
        if synthetic and synthetic.get("representability_pass") and card["checks"]["representability"]["status"]=="pending":
            card["checks"]["representability"]=_ck("synthetic-pass","Synthetic mechanism harness passed; this clears representability only and has no reality/method authority.","generated/p0-realizability-suite.json","synthetic-realizability-only")
        card["gpu0"]["next"] = NEXT_ACTION[idea]
        cards.append(card)
    summary={
        "ideas":len(cards),
        "checks_passed":sum(v["status"]=="pass" for c in cards for v in c["checks"].values()),
        "checks_failed":sum(v["status"]=="fail" for c in cards for v in c["checks"].values()),
        "checks_pending":sum(v["status"]=="pending" for c in cards for v in c["checks"].values()),
        "checks_synthetic_pass":sum(v["status"]=="synthetic-pass" for c in cards for v in c["checks"].values()),
        "gpu0_hold_or_conditional":sum(c["gpu0"]["status"] in {"hold","conditional","partial-pass"} for c in cards),
    }
    return {"schema_version":"1.0","generated_at":_now(),"experiment_root":"profile-resolved-machine-local",
        "policy":{"real_reused_may_unblock":True,"synthetic_harness_may_not_unblock_reality":True,"same_batch_self_authorization_forbidden":True,"method_result_from_offline_qualification_forbidden":True},
        "shared_evidence":{"alfworld":aw,"a1":aa1,"a2":aa2,"a3_mastered_panel":a3p,"a6_a7_dataset":a67,"updater_competence":{"a1":up_a1,"a2":up_a2},"memory":mem,"e1":we1,"realizability_summary":realizability.get("summary") or {}},"summary":summary,"cards":cards}

def write_p0_offline_qualification_state(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=build_p0_offline_qualification_state(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_OFFLINE_QUALIFICATION = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state

if __name__=="__main__": print(json.dumps(write_p0_offline_qualification_state(),ensure_ascii=False))
