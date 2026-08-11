from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings, resolve_experiment_data_root
from .p0_offline_evidence import alfworld, a1, a2, a3_panel, a67_dataset, memory, memory_full, substrate_readiness, e1
from .p0_realizability_suite import build_p0_realizability_suite
from .p0_b10_cpu import run_b10_cpu_p0
from .p0_a6_cpu import run_a6_cpu_p0

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

def _e2_artifact() -> dict[str, Any]:
    path=PROJECT_ROOT/"generated"/"p0-e2-workflow-cpu.json"
    try:return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):return {}


def _e3_artifact() -> dict[str, Any]:
    path=PROJECT_ROOT/"generated"/"p0-e3-real-api.json"
    try:return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):return {}

def _e3_stateful_artifact() -> dict[str, Any]:
    path=PROJECT_ROOT/"generated"/"p0-e3-stateful.json"
    try:return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):return {}

def _e4_artifact() -> dict[str, Any]:
    path=PROJECT_ROOT/"generated"/"p0-e4-permission-cpu.json"
    try:return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):return {}

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

def _apply_a6_stop(card: dict[str, Any], result: dict[str, Any]) -> None:
    if card["idea_id"]!="active-causal-minimal-rollback" or result.get("decision")!="STOP_MATCHED_GROUP_TESTING_EQUIVALENT": return
    m=result.get("matched_simplification") or {}; s=result.get("summary") or {}
    card["checks"]["baseline_disagreement"]=_ck("fail",f"Non-learning binary group testing exactly reproduces active-causal recovery and per-case intervention counts: mean tests {s.get('active-causal',{}).get('mean_tests',0):.3f} vs {s.get('binary-group-testing',{}).get('mean_tests',0):.3f}; per-case identical={m.get('per_case_test_counts_identical')}.","generated/p0-a6-cpu.json","cpu-p0-falsifier")
    card["gpu0"]={"status":"stop-matched-group-testing-equivalent","evidence":"CPU P0 shows the active query policy is exactly a non-learning binary group-testing simplification under the same sparse-fault prior.","source":"generated/p0-a6-cpu.json","evidence_kind":"cpu-p0-falsifier","next":result.get("next_action")}


def _apply_b10(card: dict[str, Any], result: dict[str, Any]) -> None:
    if card["idea_id"]!="constraint-complete-typed-memory-order-logic": return
    if result.get("decision")!="STOP_MATCHED_NARY_EQUIVALENT": return
    m=result.get("metrics") or {}
    card["checks"]["target_variation"]=_ck("pass","32 binding held-out type combinations contain legal and violating orderings under exhaustive programmatic truth.","generated/p0-b10-cpu.json","cpu-p0-falsifier")
    card["checks"]["baseline_disagreement"]=_ck("fail",f"Matched typed n-ary factor ties symbolic exact ({m.get('factor_exact_accuracy',0):.3f} vs {m.get('symbolic_exact_accuracy',0):.3f}) and compiled accuracy at the same active-edge budget ({m.get('factor_budgeted_compiled_accuracy',0):.3f} vs {m.get('symbolic_compiled_accuracy',0):.3f}).","generated/p0-b10-cpu.json","cpu-p0-falsifier")
    card["gpu0"]={"status":"stop-matched-nary-equivalent","evidence":"CPU P0 fired the preregistered matched-simplification stop; no GPU or real-agent expansion is warranted for standalone B-10.","source":"generated/p0-b10-cpu.json","evidence_kind":"cpu-p0-falsifier","next":result.get("next_action")}


def _apply_exact_data_holds(card: dict[str, Any], a67: dict[str, Any], memfull: dict[str, Any]) -> None:
    idea=card["idea_id"]
    if idea=="lineage-aware-rollback" and int(a67.get("max_rounds_per_sequence") or 0)<30:
        card["gpu0"]={"status":"hold-history-too-short","evidence":f"Existing frozen sequences contain at most {int(a67.get('max_rounds_per_sequence') or 0)} sequential update rounds; the P0 contract requires 30-50 updates plus 12 rollback queries.","source":a67.get("source"),"evidence_kind":"real-reused","next":NEXT_ACTION[idea]}
    elif idea=="counterfactual-evolution-decision-controller" and int(a67.get("a7_same_state_four_action_rows") or 0)==0:
        card["gpu0"]={"status":"hold-four-action-counterfactuals-missing","evidence":"The existing 9-sequence artifact has 0 same-state continue/commit/rollback/stop counterfactual rows; optimal-round variation alone cannot train the frozen four-action controller.","source":a67.get("source"),"evidence_kind":"real-reused","next":NEXT_ACTION[idea]}
    elif idea=="contradiction-preserving-consolidation" and int(memfull.get("controlled_nonzero") or 0)<30:
        card["gpu0"]={"status":"hold-support-cardinality-insufficient","evidence":f"The completed shared Memory table contains only {int(memfull.get('controlled_nonzero') or 0)} controlled-nonzero unit effects. These are not automatically conclusion-change cases and cannot satisfy the dedicated >=30 reproducible conclusion-change gate.","source":memfull.get("source"),"evidence_kind":"real-reused","next":NEXT_ACTION[idea]}
    elif idea=="retrieval-interference-auditor" and int(memfull.get("co_retrieval_pair_arms") or 0)==0:
        card["gpu0"]={"status":"hold-co-retrieval-arms-missing","evidence":"The completed shared Memory table contains no randomized co-retrieval pair arm, so an interaction-pathway claim is not identifiable from it.","source":memfull.get("source"),"evidence_kind":"real-reused","next":NEXT_ACTION[idea]}
    elif idea=="memory-half-life" and int(memfull.get("longitudinal_reuse_sequences") or 0)==0:
        card["gpu0"]={"status":"hold-longitudinal-reuse-missing","evidence":"The completed shared Memory table is a treatment table, not a longitudinal reuse stream; it contains 0 repeated reuse sequences for utility-hazard learning.","source":memfull.get("source"),"evidence_kind":"real-reused","next":NEXT_ACTION[idea]}


def _apply_e2_stop(card: dict[str, Any], result: dict[str, Any]) -> None:
    if card["idea_id"]!="workflow-branch-credit" or result.get("decision")!="STOP_MATCHED_E1_DIRECT_EDIT_EQUIVALENT": return
    m=result.get("metrics") or {}
    card["checks"]["target_variation"]=_ck("pass","Four recurring typed failure motifs are verified across 16 source workflows and held out across API/identity-disjoint hidden workflows.","generated/p0-e2-workflow-cpu.json","cpu-workflow-p0")
    card["checks"]["baseline_disagreement"]=_ck("fail",f"Causal grammar and matched E-1-style direct edit policy tie at hidden success {m.get('grammar_hidden_success',0):.3f} vs {m.get('direct_edit_hidden_success',0):.3f}, with rewrite agreement {m.get('hidden_rewrite_agreement',0):.3f} and equal source calls {m.get('grammar_source_calls',0)}.","generated/p0-e2-workflow-cpu.json","cpu-workflow-p0")
    card["checks"]["tiny_overfit"]=_ck("pass","Hidden workflow API/object identities are disjoint and both rules are frozen before hidden truth is opened.","generated/p0-e2-workflow-cpu.json","cpu-workflow-p0")
    card["checks"]["effect_variation"]=_ck("pass","The sandbox contains four distinct local failure causes and four distinct corrective rewrites under programmatic task truth.","generated/p0-e2-workflow-cpu.json","cpu-workflow-p0")
    card["updater_competence"]={"status":"pass","passed":True,"evidence_kind":"cpu-workflow-p0","reason":"Each source motif has repeatable causal and noncausal group intervention outcomes."}
    card["gpu0"]={"status":"stop-matched-e1-direct-edit-equivalent","evidence":"The intervention-confirmed grammar produces exactly the same hidden rewrites as a matched E-1-style paired edit-effect lookup with identical source calls and zero hidden search.","source":"generated/p0-e2-workflow-cpu.json","evidence_kind":"cpu-workflow-p0","next":result.get("next_action")}


def _apply_e3_reality(card: dict[str, Any], result: dict[str, Any]) -> None:
    if card["idea_id"]!="bounded-probe-api-transition-operator" or result.get("decision")!="READ_ONLY_SUBSTRATE_REDUCIBLE": return
    m=result.get("metrics") or {}; fam=m.get("family_accuracy") or {}
    card["checks"]["target_variation"]=_ck("pass","Two heterogeneous live target API families expose distinct endpoint/response/error semantics under the frozen N=6 probe budget.","generated/p0-e3-real-api.json","real-public-api-p0")
    card["checks"]["baseline_disagreement"]=_ck("fail",f"On the read-only public-API substrate, isomorphic deterministic P/E/X reaches hidden semantic accuracy {m.get('hidden_semantic_accuracy',0):.3f}; GitLab={fam.get('gitlab',0):.3f}, Codeberg={fam.get('codeberg',0):.3f}. There is no learned-arm headroom on this substrate.","generated/p0-e3-real-api.json","real-public-api-p0")
    card["checks"]["effect_variation"]=_ck("pass","Frozen probes cover success, missing-resource/reference, and auth-required outcomes; hidden branches cover unseen normal, missing-resource, and authentication recovery.","generated/p0-e3-real-api.json","real-public-api-p0")
    card["gpu0"]={"status":"hold-read-only-substrate-reducible","evidence":"The real read-only API substrate is reducible to deterministic P/E/X, but state-changing E semantics were not tested; this blocks the learned arm here without stopping full E-3.","source":"generated/p0-e3-real-api.json","evidence_kind":"real-public-api-p0","next":result.get("next_action")}


def _apply_e3_stateful_stop(card: dict[str, Any], result: dict[str, Any]) -> None:
    if card["idea_id"]!="bounded-probe-api-transition-operator" or result.get("decision")!="STOP_STATEFUL_DETERMINISTIC_PEX_CEILING": return
    m=result.get("metrics") or {}; fam=m.get("family_accuracy") or {}
    card["checks"]["baseline_disagreement"]=_ck("fail",f"Stateful deterministic P/E/X also reaches exact hidden transition/recovery accuracy {m.get('stateful_semantic_accuracy',0):.3f}; ledger={fam.get('ledger',0):.3f}, vault={fam.get('vault',0):.3f} under the same six-probe budget.","generated/p0-e3-stateful.json","executable-stateful-p0")
    card["checks"]["effect_variation"]=_ck("pass","Stateful hidden cases cover create/update/delete effects plus duplicate, stale-version refresh-retry, and missing-resource abort semantics across two different status-code families.","generated/p0-e3-stateful.json","executable-stateful-p0")
    card["gpu0"]={"status":"stop-stateful-deterministic-pex-ceiling","evidence":"The read-only ceiling persists after adding state-changing E semantics and recovery. Isomorphic deterministic P/E/X exactly matches all hidden final states; no learned-arm headroom remains for standalone E-3.","source":"generated/p0-e3-stateful.json","evidence_kind":"executable-stateful-p0","next":result.get("next_action")}


def _apply_e4_result(card: dict[str, Any], result: dict[str, Any]) -> None:
    verdict=result.get("decision")
    if card["idea_id"]!="interventional-permission-triage-under-ceiling" or verdict not in {"P0_SIGNAL_CONTINUE","STOP_MATCHED_BOOLEAN_RULE_EQUIVALENT"}: return
    m=result.get("metrics") or {}; d=result.get("design") or {}; stop=verdict=="STOP_MATCHED_BOOLEAN_RULE_EQUIVALENT"
    card["checks"]["target_variation"]=_ck("pass",f"Executable permission sandbox has both risky and safe outcomes across {d.get('unseen_test_operators',0)} unseen mutation operators.","generated/p0-e4-permission-cpu.json","cpu-permission-p0")
    card["checks"]["baseline_disagreement"]=_ck("fail" if stop else "pass",f"Zero-miss reauthorizations: learned={m.get('learned_reauthorizations',0)}, envelope={m.get('deterministic_envelope_reauthorizations',0)}, matched Boolean rule={m.get('matched_rule_reauthorizations',0)}.","generated/p0-e4-permission-cpu.json","cpu-permission-p0")
    card["checks"]["tiny_overfit"]=_ck("pass","Linear q is trained on feature combinations disjoint from all test combinations; threshold freezes on calibration.","generated/p0-e4-permission-cpu.json","cpu-permission-p0")
    card["checks"]["competence_window"]=_ck("pass","Held-out permission labels contain both risky and safe outcomes under the immutable ceiling.","generated/p0-e4-permission-cpu.json","cpu-permission-p0")
    card["checks"]["effect_variation"]=_ck("pass","Unseen mutations induce permission-specific effects while many conservative envelope flags are harmless.","generated/p0-e4-permission-cpu.json","cpu-permission-p0")
    card["updater_competence"]={"status":"pass","passed":True,"evidence_kind":"cpu-permission-p0","reason":"Randomized permission canaries provide positive and negative induced-risk labels."}
    card["gpu0"]={"status":"stop-matched-boolean-rule-equivalent" if stop else "p0-signal-continue","evidence":"Matched monotone-DNF rule is equally safe and uses no more reauthorizations than learned q." if stop else "Interventional q safely reduces reauthorization workload versus deterministic envelope.","source":"generated/p0-e4-permission-cpu.json","evidence_kind":"cpu-permission-p0","next":result.get("next_action")}


def _apply_missing_substrates(card: dict[str, Any], ready: dict[str, Any]) -> None:
    idea=card["idea_id"]
    if idea=="compositional-update-compatibility" and int(ready.get("a4_composition_pair_order_rows") or 0)==0:
        card["gpu0"]={"status":"hold-composition-matrix-missing","evidence":"Registered updater artifacts contain 0 pair/order/rollback composition rows for held-out update-identity evaluation.","source":"runs/round1-20260810/a12-v4/evaluations.jsonl","evidence_kind":"registered-artifact-audit","next":NEXT_ACTION[idea]}
    elif idea=="local-counterexample-memory-repair" and not ready.get("b5_boundary_counterexample_artifacts"):
        card["gpu0"]={"status":"hold-boundary-dataset-missing","evidence":"No registered real skill/predicate boundary-counterexample artifact exists for the frozen external applicability-gate P0.","source":"registered experiment artifact inventory","evidence_kind":"registered-artifact-audit","next":NEXT_ACTION[idea]}
    elif idea=="evaluator-coadaptation-guard" and not ready.get("c2_cross_version_matrix_artifacts"):
        card["gpu0"]={"status":"hold-cross-version-matrix-missing","evidence":"No registered 3x3 actor/evaluator cross-version score matrix with frozen external anchors exists yet.","source":"registered experiment artifact inventory","evidence_kind":"registered-artifact-audit","next":NEXT_ACTION[idea]}
    elif idea=="workflow-branch-credit" and not ready.get("e2_group_intervention_artifacts"):
        card["gpu0"]={"status":"hold-group-interventions-missing","evidence":"No registered identity/API-disjoint group-intervention artifact exists for causal motif validation.","source":"registered experiment artifact inventory","evidence_kind":"registered-artifact-audit","next":NEXT_ACTION[idea]}
    elif idea=="bounded-probe-api-transition-operator" and not ready.get("e3_api_transition_artifacts"):
        card["gpu0"]={"status":"hold-real-api-substrate-missing","evidence":"No registered executable multi-family API transition/recovery substrate exists; unrelated local services are not accepted as a transfer benchmark.","source":"registered experiment artifact inventory","evidence_kind":"registered-artifact-audit","next":NEXT_ACTION[idea]}
    elif idea=="interventional-permission-triage-under-ceiling" and not ready.get("e4_permission_canary_artifacts"):
        card["gpu0"]={"status":"hold-permission-sandbox-missing","evidence":"No registered permission-ceiling mutation/canary sandbox with independent external-effect logs exists yet.","source":"registered experiment artifact inventory","evidence_kind":"registered-artifact-audit","next":NEXT_ACTION[idea]}


def _apply_d1(card: dict[str, Any], aw: dict[str, Any]) -> None:
    if card["idea_id"]!="counterexample-generating-curriculum" or not aw["passed"]: return
    card["checks"]["target_variation"]=_ck("pass",f"Base OOD set contains both successes ({aw['successes']}) and failures ({aw['total']-aw['successes']}); boundary candidates can exist.",aw["source"])
    card["gpu0"]={"status":"hold-minimality-unmeasured","evidence":"Task failures are real, but the current artifacts contain 0 verifier-confirmed 1-minimal boundary counterexamples; task failure prevalence is not the curriculum mechanism.","source":aw["source"],"evidence_kind":"real-reused","next":NEXT_ACTION[card['idea_id']]}

def build_p0_offline_qualification_state() -> dict[str, Any]:
    root=resolve_experiment_data_root(StorageSettings.from_env())
    aw,aa1,aa2,a3p,a67,mem,memfull,ready,we1=alfworld(root),a1(root),a2(root),a3_panel(root),a67_dataset(root),memory(root),memory_full(root),substrate_readiness(root),e1(root)
    up_a1=_updater_config("p0_a1_screening_config.json"); up_a2=_updater_config("p0_a2_screening_config.json")
    realizability=build_p0_realizability_suite(); realizability_by_id={row["idea_id"]:row for row in realizability.get("rows") or []}
    b10=run_b10_cpu_p0(); a6cpu=run_a6_cpu_p0(); e2cpu=_e2_artifact(); e3real=_e3_artifact(); e3stateful=_e3_stateful_artifact(); e4cpu=_e4_artifact()
    cards=[]
    for idea in NEW_IDS:
        card=_base_card(idea,aw)
        card["updater_competence"]={"status":"pending","passed":False,"evidence_kind":"pending","reason":"mechanism-specific updater/action-stream competence has not been qualified"}
        if idea=="regression-gated-self-evolution": card["updater_competence"]={**up_a1,"evidence_kind":"real-reused"}
        elif idea in {"lineage-aware-rollback","active-causal-minimal-rollback","counterfactual-evolution-decision-controller"}: card["updater_competence"]={**up_a2,"evidence_kind":"real-reused"}
        _apply_a1(card,aa1); _apply_a2(card,aa2); _apply_memory(card,mem); _apply_e1(card,we1); _apply_a6_stop(card,a6cpu); _apply_b10(card,b10); _apply_d1(card,aw); _apply_exact_data_holds(card,a67,memfull); _apply_missing_substrates(card,ready); _apply_e2_stop(card,e2cpu); _apply_e3_reality(card,e3real); _apply_e3_stateful_stop(card,e3stateful); _apply_e4_result(card,e4cpu)
        synthetic=realizability_by_id.get(idea)
        if synthetic and synthetic.get("representability_pass") and card["checks"]["representability"]["status"]=="pending":
            card["checks"]["representability"]=_ck("synthetic-pass","Synthetic mechanism harness passed; this clears representability only and has no reality/method authority.","generated/p0-realizability-suite.json","synthetic-realizability-only")
        card["gpu0"].setdefault("next", NEXT_ACTION[idea])
        cards.append(card)
    summary={
        "ideas":len(cards),
        "checks_passed":sum(v["status"]=="pass" for c in cards for v in c["checks"].values()),
        "checks_failed":sum(v["status"]=="fail" for c in cards for v in c["checks"].values()),
        "checks_pending":sum(v["status"]=="pending" for c in cards for v in c["checks"].values()),
        "checks_synthetic_pass":sum(v["status"]=="synthetic-pass" for c in cards for v in c["checks"].values()),
        "gpu0_hold_or_conditional":sum(str(c["gpu0"]["status"]).startswith("hold") or c["gpu0"]["status"] in {"conditional","partial-pass"} for c in cards),
        "gpu0_stop":sum(str(c["gpu0"]["status"]).startswith("stop") for c in cards),
    }
    return {"schema_version":"1.0","generated_at":_now(),"experiment_root":"profile-resolved-machine-local",
        "policy":{"real_reused_may_unblock":True,"synthetic_harness_may_not_unblock_reality":True,"same_batch_self_authorization_forbidden":True,"method_result_from_offline_qualification_forbidden":True},
        "shared_evidence":{"alfworld":aw,"a1":aa1,"a2":aa2,"a3_mastered_panel":a3p,"a6_a7_dataset":a67,"updater_competence":{"a1":up_a1,"a2":up_a2},"memory":mem,"memory_full":memfull,"substrate_readiness":ready,"e1":we1,"a6_cpu":{"decision":a6cpu.get("decision"),"summary":a6cpu.get("summary"),"matched_simplification":a6cpu.get("matched_simplification")},"b10":{"decision":b10.get("decision"),"metrics":b10.get("metrics"),"gates":b10.get("gates")},"e2_workflow_cpu":{"decision":e2cpu.get("decision"),"metrics":e2cpu.get("metrics"),"freeze_sha256":e2cpu.get("freeze_sha256_before_hidden")},"e3_real_api":{"decision":e3real.get("decision"),"metrics":e3real.get("metrics"),"prediction_sha256":e3real.get("prediction_sha256_before_hidden")},"e3_stateful":{"decision":e3stateful.get("decision"),"metrics":e3stateful.get("metrics"),"prediction_sha256":e3stateful.get("prediction_sha256_before_hidden")},"e4_permission_cpu":{"decision":e4cpu.get("decision"),"metrics":e4cpu.get("metrics"),"threshold":e4cpu.get("threshold")},"realizability_summary":realizability.get("summary") or {}},"summary":summary,"cards":cards}

def write_p0_offline_qualification_state(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=build_p0_offline_qualification_state(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_OFFLINE_QUALIFICATION = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state

if __name__=="__main__": print(json.dumps(write_p0_offline_qualification_state(),ensure_ascii=False))
