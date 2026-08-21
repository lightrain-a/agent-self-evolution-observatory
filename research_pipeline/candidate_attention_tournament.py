from __future__ import annotations

import hashlib
import json
import math
import re
from copy import deepcopy
from typing import Any

SCHEMA_VERSION = "1.0"
DIMENSIONS = (
    "problem_importance",
    "agent_specificity",
    "reduction_resistance",
    "independent_truth_quality",
    "falsifier_decisiveness",
    "substrate_feasibility",
    "paper_contribution",
)
DEFAULT_COMPARISONS_PER_CANDIDATE = 3
DEFAULT_PROXIMITY_THRESHOLD = 0.25
DEFAULT_ACTIVE_SLOTS = 4

AUTHORITY = {
    "scientific_claim": False,
    "candidate_elimination": False,
    "problem_gate": False,
    "paper_design": False,
    "method": False,
    "experiment": False,
    "p0": False,
    "gpu": False,
}


def _canon(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(value: Any) -> str:
    return hashlib.sha256(_canon(value).encode()).hexdigest()


def _text(value: Any, limit: int = 2200) -> str:
    if isinstance(value, (dict, list)):
        value = _canon(value)
    return " ".join(str(value or "").split())[:limit]


def _tokens(value: Any) -> set[str]:
    return {x for x in re.findall(r"[\w]+", _text(value, 12000).lower(), flags=re.UNICODE) if len(x) > 1}


def _packet(row: dict[str, Any]) -> dict[str, Any]:
    candidate = row.get("candidate") if isinstance(row.get("candidate"), dict) else {}
    return {
        "candidate_id": str(row.get("candidate_id") or candidate.get("candidate_id") or ""),
        "title": _text(row.get("title") or candidate.get("title"), 500),
        "discovery_lane": str(row.get("discovery_lane") or candidate.get("discovery_lane") or ""),
        "blockers": [str(x) for x in row.get("blockers") or []],
        "irreducible_object": _text(row.get("irreducible_object") or candidate.get("irreducible_object"), 1800),
        "endpoint_headroom_requirement": _text(row.get("endpoint_headroom_requirement") or candidate.get("endpoint_headroom_requirement"), 1200),
        "exact_prediction": _text(row.get("exact_prediction") or candidate.get("exact_prediction"), 1800),
        "strongest_same_information_baseline": _text(row.get("strongest_same_information_baseline") or candidate.get("strongest_same_information_baseline"), 1600),
        "cheapest_problem_falsifier": _text(row.get("cheapest_problem_falsifier") or candidate.get("cheapest_problem_falsifier"), 1800),
        "scientific_authority": False,
    }


def _similarity(a: dict[str, Any], b: dict[str, Any]) -> float:
    fields = ("title", "irreducible_object", "exact_prediction", "strongest_same_information_baseline", "cheapest_problem_falsifier")
    ta = _tokens(" ".join(str(a.get(k) or "") for k in fields)); tb = _tokens(" ".join(str(b.get(k) or "") for k in fields))
    return len(ta & tb) / len(ta | tb) if ta or tb else 0.0


def _proximity_families(packets: list[dict[str, Any]], threshold: float) -> tuple[list[dict[str, Any]], dict[str, str]]:
    parent = {p["candidate_id"]: p["candidate_id"] for p in packets}
    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb: parent[max(ra, rb)] = min(ra, rb)
    edges=[]
    for i,a in enumerate(packets):
        for b in packets[i+1:]:
            sim=_similarity(a,b)
            if sim >= threshold:
                union(a["candidate_id"],b["candidate_id"])
                edges.append({"a":a["candidate_id"],"b":b["candidate_id"],"similarity":round(sim,6)})
    groups: dict[str,list[str]]={}
    for p in packets: groups.setdefault(find(p["candidate_id"]),[]).append(p["candidate_id"])
    mapping={}
    families=[]
    for index, ids in enumerate(sorted((sorted(v) for v in groups.values()), key=lambda x:x[0]),1):
        family_id=f"PF{index:02d}"
        for cid in ids:mapping[cid]=family_id
        families.append({"family_id":family_id,"candidate_ids":ids,"size":len(ids),"scientific_authority":False})
    return [{"threshold":threshold,"edges":edges,"families":families,"scientific_authority":False}],mapping


def _round_robin(ids: list[str], rounds: int) -> list[dict[str, Any]]:
    ordered=sorted(ids,key=lambda x:hashlib.sha256(("attention-seed:"+x).encode()).hexdigest())
    bye=None
    if len(ordered)%2: ordered.append("__BYE__");bye="__BYE__"
    n=len(ordered); rounds=min(max(0,rounds),n-1); schedule=[]; arr=list(ordered)
    for r in range(rounds):
        for i in range(n//2):
            a,b=arr[i],arr[n-1-i]
            if a==bye or b==bye: continue
            aa,bb=sorted((a,b)); pair_id=f"PAIR-{_sha({'a':aa,'b':bb})[:12]}"
            schedule.append({"pair_id":pair_id,"a":aa,"b":bb,"round":r+1})
        arr=[arr[0],arr[-1],*arr[1:-1]]
    return schedule


def prepare_attention_tournament(machine: dict[str, Any], *, comparisons_per_candidate: int = DEFAULT_COMPARISONS_PER_CANDIDATE, proximity_threshold: float = DEFAULT_PROXIMITY_THRESHOLD) -> dict[str, Any]:
    rows=[x for x in machine.get("problem_falsifier_queue") or [] if isinstance(x,dict)]
    packets=[_packet(row) for row in rows]
    ids=[p["candidate_id"] for p in packets]
    if not packets or any(not x for x in ids) or len(ids)!=len(set(ids)): raise ValueError("attention tournament requires unique nonempty candidate ids")
    proximity,mapping=_proximity_families(packets,float(proximity_threshold))
    pairs=_round_robin(ids,int(comparisons_per_candidate))
    degrees={cid:0 for cid in ids}
    for pair in pairs: degrees[pair["a"]]+=1;degrees[pair["b"]]+=1
    core={"schema_version":SCHEMA_VERSION,"status":"ATTENTION_TOURNAMENT_PREPARED","candidate_count":len(packets),"comparisons_per_candidate_requested":int(comparisons_per_candidate),"candidate_packets":packets,"proximity":proximity,"proximity_family_by_candidate":mapping,"pair_schedule":pairs,"pair_degree":degrees,"policy":{"fixed_schedule_before_reviews":True,"pairwise_results_are_attention_signals_not_scientific_verdicts":True,"proximity_families_preserve_diversity_not_eliminate_candidates":True,"automatic_candidate_elimination_forbidden":True,"scientific_thresholds_unchanged":True},"scientific_authority":False,"authority":dict(AUTHORITY)}
    core["tournament_plan_sha256"]=_sha(core);return core


def review_batch_prompt(plan: dict[str, Any], pair_ids: list[str]) -> str:
    packets={p["candidate_id"]:p for p in plan.get("candidate_packets") or []};pairs={p["pair_id"]:p for p in plan.get("pair_schedule") or []}
    selected=[]
    for pid in pair_ids:
        pair=pairs.get(pid)
        if not pair: raise ValueError(f"unknown pair: {pid}")
        selected.append({"pair_id":pid,"A":packets[pair["a"]],"B":packets[pair["b"]]})
    return f'''You are an advisory candidate-attention tournament reviewer. You may rank which candidate deserves scarce research attention first. You may NOT pass, fail, close, eliminate, or authorize any scientific state.

Compare A vs B using only their frozen contracts. For each dimension choose A, B, or TIE:
{json.dumps(list(DIMENSIONS),ensure_ascii=False)}
Definitions: problem_importance=importance if true; agent_specificity=dependence on persistent agent state/history; reduction_resistance=clarity of a residual beyond the stated strongest same-information baseline; independent_truth_quality=quality of externally grounded truth; falsifier_decisiveness=cheapness and discriminatory power; substrate_feasibility=likelihood the bounded falsifier is executable without changing the object; paper_contribution=potential contribution if the frozen prediction survives.
Overall attention_winner is A/B/TIE. This is scheduling advice only. Do not infer hidden outcomes or invent evidence.
Return JSON only with exactly {len(selected)} reviews:
{{"reviews":[{{"pair_id":"PAIR-...","dimension_winners":{{{','.join(json.dumps(d)+':"A|B|TIE"' for d in DIMENSIONS)}}},"attention_winner":"A|B|TIE","confidence":"HIGH|MEDIUM|LOW","reason":"<=55 words"}}, ...]}}
PAIRS={json.dumps(selected,ensure_ascii=False,separators=(",",":"))}'''


def compile_review_batch(plan: dict[str, Any], payload: dict[str, Any], *, reviewer_label: str, resolved_model: str, pair_ids: list[str]) -> dict[str, Any]:
    if plan.get("scientific_authority") is not False: raise ValueError("tournament plan must be zero authority")
    reviews=[x for x in payload.get("reviews") or [] if isinstance(x,dict)]; expected=set(pair_ids)
    if len(reviews)!=len(expected) or {str(x.get("pair_id") or "") for x in reviews}!=expected: raise ValueError("pairwise review ids mismatch")
    out=[]
    for row in reviews:
        dims=row.get("dimension_winners") or {}
        if not isinstance(dims,dict) or set(dims)!=set(DIMENSIONS) or any(dims[d] not in {"A","B","TIE"} for d in DIMENSIONS): raise ValueError("invalid dimension winners")
        winner=str(row.get("attention_winner") or "")
        if winner not in {"A","B","TIE"}: raise ValueError("invalid attention winner")
        confidence=str(row.get("confidence") or "").upper()
        if confidence not in {"HIGH","MEDIUM","LOW"}: raise ValueError("invalid confidence")
        out.append({"pair_id":row["pair_id"],"dimension_winners":dims,"attention_winner":winner,"confidence":confidence,"reason":_text(row.get("reason"),700),"reviewer_label":reviewer_label,"resolved_model":resolved_model,"scientific_authority":False})
    core={"schema_version":SCHEMA_VERSION,"status":"ATTENTION_REVIEW_BATCH_COMPILED","reviewer_label":reviewer_label,"resolved_model":resolved_model,"pair_ids":sorted(expected),"reviews":sorted(out,key=lambda x:x["pair_id"]),"scientific_authority":False,"authority":dict(AUTHORITY)};core["review_batch_sha256"]=_sha(core);return core


def finalize_attention_tournament(plan: dict[str, Any], review_batches: list[dict[str, Any]], *, active_slots: int = DEFAULT_ACTIVE_SLOTS) -> dict[str, Any]:
    pair_map={p["pair_id"]:p for p in plan.get("pair_schedule") or []};ids=[p["candidate_id"] for p in plan.get("candidate_packets") or []]
    reviewers={str(b.get("reviewer_label") or "") for b in review_batches}
    if len(reviewers)<2: raise ValueError("attention tournament requires at least two reviewer labels")
    seen=set();reviews=[]
    for batch in review_batches:
        for row in batch.get("reviews") or []:
            key=(batch.get("reviewer_label"),row.get("pair_id"))
            if key in seen: raise ValueError("duplicate reviewer/pair review")
            seen.add(key);reviews.append(row)
    expected={(label,pid) for label in reviewers for pid in pair_map}
    if seen!=expected: raise ValueError("attention tournament review coverage incomplete")
    points={cid:0.0 for cid in ids};games={cid:0 for cid in ids};dim_points={cid:{d:0.0 for d in DIMENSIONS} for cid in ids};disagreements=0
    by_pair={pid:[] for pid in pair_map}
    for row in reviews: by_pair[row["pair_id"]].append(row)
    for pid,pair in pair_map.items():
        local=by_pair[pid];winners={r["attention_winner"] for r in local};disagreements+=int(len(winners)>1)
        for row in local:
            for side,cid in (("A",pair["a"]),("B",pair["b"])):
                games[cid]+=1;points[cid]+=1.0 if row["attention_winner"]==side else 0.5 if row["attention_winner"]=="TIE" else 0.0
                for d in DIMENSIONS: dim_points[cid][d]+=1.0 if row["dimension_winners"][d]==side else 0.5 if row["dimension_winners"][d]=="TIE" else 0.0
    family=plan.get("proximity_family_by_candidate") or {};ranking=[]
    for cid in ids:
        denom=max(1,games[cid]);ranking.append({"candidate_id":cid,"attention_score":round(points[cid]/denom,6),"games":games[cid],"dimension_scores":{d:round(dim_points[cid][d]/denom,6) for d in DIMENSIONS},"proximity_family":family.get(cid,""),"scientific_authority":False})
    ranking.sort(key=lambda r:(-r["attention_score"],-r["dimension_scores"]["falsifier_decisiveness"],-r["dimension_scores"]["substrate_feasibility"],r["candidate_id"]))
    selected=[];used=set()
    for row in ranking:
        fam=row["proximity_family"]
        if fam and fam in used: continue
        selected.append(row["candidate_id"]);used.add(fam)
        if len(selected)>=active_slots: break
    for row in ranking:
        if len(selected)>=active_slots: break
        if row["candidate_id"] not in selected:selected.append(row["candidate_id"])
    for i,row in enumerate(ranking,1): row["attention_rank"]=i;row["recommended_active_attention"]=row["candidate_id"] in selected
    core={"schema_version":SCHEMA_VERSION,"status":"ATTENTION_TOURNAMENT_COMPLETE","tournament_plan_sha256":plan.get("tournament_plan_sha256"),"reviewer_labels":sorted(reviewers),"pair_count":len(pair_map),"pair_disagreement_rate":disagreements/max(1,len(pair_map)),"ranking":ranking,"recommended_active_attention":selected,"policy":{"ranking_controls_attention_order_only":True,"no_candidate_is_eliminated_or_scientifically_reclassified":True,"formal_gates_remain_authoritative":True},"scientific_authority":False,"authority":dict(AUTHORITY)};core["tournament_result_sha256"]=_sha(core);return core


def reallocate_unstarted_evidence_plan(evidence_plan: dict[str, Any], tournament: dict[str, Any], *, active_slots: int = DEFAULT_ACTIVE_SLOTS) -> dict[str, Any]:
    allowed={"NEEDS_BOUNDED_EVIDENCE_DESIGN","DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET"}
    entries=[deepcopy(x) for x in evidence_plan.get("entries") or [] if isinstance(x,dict)]
    if any(str(e.get("status") or "") not in allowed for e in entries): raise ValueError("attention reallocation is forbidden after evidence design/review/substrate work begins")
    order=[str(x) for x in tournament.get("recommended_active_attention") or []]
    rank={str(r.get("candidate_id")):int(r.get("attention_rank") or 10**9) for r in tournament.get("ranking") or []}
    if set(rank)!= {str(e.get("candidate_id")) for e in entries}: raise ValueError("tournament/evidence candidate set mismatch")
    selected=set(order[:max(0,int(active_slots))])
    for e in entries:
        cid=str(e.get("candidate_id"));e["attention_rank"]=rank[cid];e["attention_tournament_sha256"]=tournament.get("tournament_result_sha256");e["selection_basis"]="PAIRWISE_ATTENTION_TOURNAMENT_ZERO_AUTHORITY";e["design_selected"]=cid in selected;e["status"]="NEEDS_BOUNDED_EVIDENCE_DESIGN" if cid in selected else "DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET";e["execution_authorized"]=False
    entries.sort(key=lambda e:(int(e.get("attention_rank") or 10**9),str(e.get("candidate_id"))))
    out=deepcopy(evidence_plan);out["entries"]=entries;out["portfolio"]={**dict(out.get("portfolio") or {}),"selection":"pairwise-attention-tournament-zero-authority","max_active_candidates":int(active_slots),"active_candidates":len(selected),"tournament_result_sha256":tournament.get("tournament_result_sha256")};out["scientific_authority"]=False;out["authority"]=dict(AUTHORITY);return out
