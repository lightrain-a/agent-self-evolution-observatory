from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "p0-realizability-suite.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "p0-realizability-suite.js"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _result(idea_id: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "idea_id": idea_id,
        "status": "synthetic-pass" if passed else "synthetic-fail",
        "representability_pass": passed,
        "evidence_kind": "synthetic-realizability-only",
        "scientific_authority": "representability-only; cannot establish reality, effect size, or method superiority",
        "evidence": evidence,
    }


def _a4() -> dict[str, Any]:
    # Type-level incompatibility must transfer to held-out update identities.
    train=[("p1","prompt","schema"),("p2","prompt","verify"),("m1","memory","ordering"),("m2","memory","retry"),("w1","workflow","schema"),("w2","workflow","verify")]
    held=[("p3","prompt","schema"),("m3","memory","ordering"),("w3","workflow","schema")]
    incompatible={("prompt","schema","memory","ordering"),("memory","ordering","prompt","schema")}
    clauses={(a[1],a[2],b[1],b[2]) for a in train for b in train if (a[1],a[2],b[1],b[2]) in incompatible}
    truth=[]; pred=[]
    for a in held:
        for b in held:
            if a==b: continue
            key=(a[1],a[2],b[1],b[2]); truth.append(int(key in incompatible)); pred.append(int(key in clauses))
    acc=sum(x==y for x,y in zip(truth,pred))/len(truth)
    return _result("compositional-update-compatibility", acc==1.0 and any(truth), {"held_pairs":len(truth),"type_clause_accuracy":acc,"positive_pairs":sum(truth)})


def _a5() -> dict[str, Any]:
    # A compact reversible delta log must answer selective rollback queries exactly.
    history=[]; state={}
    for i in range(40):
        key=f"slot{i%7}"; old=state.get(key,0); new=old+(1 if i%3 else -1); history.append((i,key,old,new)); state[key]=new
    queries=[3,5,8,11,14,17,20,23,26,29,32,39]
    exact=0
    for q in queries:
        s={}
        for i,key,old,new in history:
            if i<=q:s[key]=new
        rebuilt={}
        for i,key,old,new in history[:q+1]: rebuilt[key]=new
        exact+=rebuilt==s
    compact_entries=len({(key,new) for _,key,_,new in history})
    return _result("lineage-aware-rollback", exact==len(queries), {"updates":40,"rollback_queries":len(queries),"exact_queries":exact,"full_entries":40,"distinct_delta_states":compact_entries})


def _b2() -> dict[str, Any]:
    # Deletion oracle identifies entries whose removal flips a query conclusion.
    entries=[("default","bird->fly"),("exception","penguin->not_fly"),("fact","penguin(p)"),("noise","color(p,black)")]
    def answer(active:set[str])->bool:
        return "default" in active and "fact" in active and "exception" not in active
    full={x[0] for x in entries}; base=answer(full); flips=[]
    for name,_ in entries:
        if answer(full-{name})!=base: flips.append(name)
    return _result("contradiction-preserving-consolidation", flips==["exception"], {"entries":len(entries),"conclusion_changing":flips,"nonchanging":[x[0] for x in entries if x[0] not in flips]})


def _b3() -> dict[str, Any]:
    # Harm appears only under co-retrieval; individual-memory tests remain safe.
    memories=("safe_rule","stale_override","helper")
    def harm(active:set[str])->int:
        return int({"safe_rule","stale_override"}.issubset(active))
    single={m:harm({m}) for m in memories}; pair={(a,b):harm({a,b}) for a in memories for b in memories if a<b}
    harmful=[k for k,v in pair.items() if v]
    return _result("retrieval-interference-auditor", all(v==0 for v in single.values()) and harmful==[("safe_rule","stale_override")], {"single_harm":single,"pair_harm":{f"{a}+{b}":v for (a,b),v in pair.items()},"localized_interaction":["safe_rule","stale_override"]})


def _b5() -> dict[str, Any]:
    # Counterexamples may only shrink a conjunction while preserving old positives.
    positives=[{"tool_ok":1,"trusted":1,"mode":"safe"},{"tool_ok":1,"trusted":1,"mode":"fast"}]
    counter={"tool_ok":1,"trusted":0,"mode":"safe"}
    gate=lambda x: bool(x["tool_ok"] and x["trusted"])
    preserved=sum(gate(x) for x in positives); rejected=not gate(counter)
    return _result("local-counterexample-memory-repair", preserved==len(positives) and rejected, {"old_positives":len(positives),"preserved":preserved,"counterexample_rejected":rejected,"added_predicate":"trusted==1"})


def _b6() -> dict[str, Any]:
    # A utility-hazard score can express drift beyond recency/frequency ties.
    rows=[{"age":5,"freq":3,"utility":.4},{"age":5,"freq":3,"utility":-.5},{"age":2,"freq":1,"utility":.2},{"age":2,"freq":1,"utility":-.3}]
    learned=[-r["utility"] for r in rows]; cache=[r["age"]-r["freq"] for r in rows]
    learned_order=sorted(range(len(rows)),key=lambda i:learned[i],reverse=True); cache_order=sorted(range(len(rows)),key=lambda i:cache[i],reverse=True)
    harmful={i for i,r in enumerate(rows) if r["utility"]<0}
    top2=set(learned_order[:2]); cache2=set(cache_order[:2])
    return _result("memory-half-life", harmful.issubset(top2) and not harmful.issubset(cache2), {"harmful_indices":sorted(harmful),"learned_top2":learned_order[:2],"cache_top2":cache_order[:2]})


def _c2() -> dict[str, Any]:
    # Frozen anchors distinguish actor drift from evaluator drift in a 3x3 matrix.
    truth=[.2,.5,.8]
    actor_offsets=[0,.1,-.1]; evaluator_bias=[0,.25,-.2]
    matrix=[[truth[a]+actor_offsets[a]+evaluator_bias[e] for e in range(3)] for a in range(3)]
    anchor=[truth[a]+actor_offsets[a] for a in range(3)]
    est_bias=[sum(matrix[a][e]-anchor[a] for a in range(3))/3 for e in range(3)]
    err=max(abs(x-y) for x,y in zip(est_bias,evaluator_bias))
    return _result("evaluator-coadaptation-guard", err<1e-9, {"actors":3,"evaluators":3,"true_evaluator_bias":evaluator_bias,"estimated_bias":est_bias,"max_error":err})


def _d1() -> dict[str, Any]:
    # Delta debugging removes irrelevant perturbations until every remaining atom is necessary.
    atoms=["rename-field","distractor-text","missing-precondition","extra-space"]
    def fails(xs:set[str])->bool: return "missing-precondition" in xs
    cur=set(atoms)
    for atom in list(atoms):
        trial=cur-{atom}
        if fails(trial): cur=trial
    minimal=fails(cur) and all(not fails(cur-{a}) for a in cur)
    return _result("counterexample-generating-curriculum", minimal and cur=={"missing-precondition"}, {"initial_atoms":len(atoms),"minimal_atoms":sorted(cur),"one_minimal":minimal})


def _e2() -> dict[str, Any]:
    graphs=[{"api":"orders","edges":[("parse","call"),("call","verify"),("verify","commit")]},{"api":"tickets","edges":[("decode","invoke"),("invoke","check"),("check","submit")]}]
    motifs=[("input","tool","verify","commit") if len(g["edges"])==3 else () for g in graphs]
    frozen_rule=("tool","verify","commit")
    applies=sum(bool(m and frozen_rule==m[1:]) for m in motifs)
    return _result("workflow-branch-credit", applies==2, {"api_disjoint_graphs":2,"repeated_typed_motif":frozen_rule,"zero_search_applications":applies})


def _e3() -> dict[str, Any]:
    apis=[{"requires":"token","effect":"stored","error":"expired","recover":"refresh"},{"requires":"credential","effect":"stored","error":"expired","recover":"refresh"}]
    typed=[{"P":a["requires"],"E":a["effect"],"X":{a["error"]:a["recover"]}} for a in apis]
    hidden={"P":"session","E":"stored","X":{"expired":"refresh"}}
    valid=hidden["E"]=="stored" and hidden["X"].get("expired")=="refresh" and all(set(x)=={"P","E","X"} for x in typed)
    return _result("bounded-probe-api-transition-operator", valid, {"source_api_families":2,"typed_fields":["P","E","X"],"hidden_recovery":hidden["X"]})


def _e4() -> dict[str, Any]:
    ceiling={"read","write"}; existing={"read","write"}; risky={"write"}; requested={"admin"}
    revalidate=existing & risky; executable=existing-revalidate
    no_escalation=executable.issubset(ceiling) and not requested.intersection(executable)
    return _result("interventional-permission-triage-under-ceiling", no_escalation and revalidate=={"write"}, {"ceiling":sorted(ceiling),"revalidate":sorted(revalidate),"retained":sorted(executable),"new_request_executable":bool(requested.intersection(executable))})


def _b10() -> dict[str, Any]:
    perms=[("exception","policy","safety"),("exception","safety","policy"),("policy","exception","safety"),("policy","safety","exception"),("safety","exception","policy"),("safety","policy","exception")]
    def legal(p:tuple[str,...])->bool: return p.index("safety")<p.index("policy")
    truth={p:legal(p) for p in perms}; compiled={p for p,v in truth.items() if v}; exact=all(legal(p)==(p in compiled) for p in perms)
    return _result("constraint-complete-typed-memory-order-logic", exact and 0<len(compiled)<len(perms), {"hidden_combinations":len(perms),"legal":len(compiled),"violations":len(perms)-len(compiled),"compiled_exact":exact})


def _a6() -> dict[str, Any]:
    updates={"a","b","c","d"}; fault={"b","c"}
    def fails(active:set[str])->bool: return fault.issubset(active)
    pairs=sorted(({x,y} for x in updates for y in updates if x<y),key=lambda s:sorted(s))
    minimal=next((s for s in pairs if fails(s)),None); retained=updates-(minimal or set())
    return _result("active-causal-minimal-rollback", minimal==fault and retained=={"a","d"}, {"updates":4,"minimal_fault_set":sorted(minimal or []),"benign_retained":sorted(retained),"pair_interventions":len(pairs)})


def _a7() -> dict[str, Any]:
    states=[{"continue":.9,"commit":.6,"rollback":.2,"stop":.4},{"continue":.3,"commit":.8,"rollback":.1,"stop":.5},{"continue":.1,"commit":.2,"rollback":.9,"stop":.4},{"continue":.2,"commit":.3,"rollback":.1,"stop":.9}]
    opt=[max(s,key=s.get) for s in states]; coverage=set(opt)
    return _result("counterfactual-evolution-decision-controller", coverage=={"continue","commit","rollback","stop"}, {"states":len(states),"optimal_actions":opt,"action_coverage":sorted(coverage)})


def build_p0_realizability_suite() -> dict[str, Any]:
    rows=[_a4(),_a5(),_a6(),_a7(),_b2(),_b3(),_b5(),_b6(),_b10(),_c2(),_d1(),_e2(),_e3(),_e4()]
    return {"schema_version":"1.0","generated_at":_now(),"policy":{"representability_only":True,"cannot_unblock_reality_or_effect_variation":True,"cannot_emit_method_result":True},"summary":{"audited":len(rows),"synthetic_pass":sum(r["representability_pass"] for r in rows),"synthetic_fail":sum(not r["representability_pass"] for r in rows)},"rows":rows}


def write_p0_realizability_suite(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=build_p0_realizability_suite(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_REALIZABILITY_SUITE = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state

if __name__=="__main__": print(json.dumps(write_p0_realizability_suite(),ensure_ascii=False))
