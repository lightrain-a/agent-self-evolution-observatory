from __future__ import annotations

import hashlib, json, math, re
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from typing import Any, Callable

from .ark_provider import extract_json_object
from .paper_first_fresh_saturation import reduction_pattern_audit
from .premium_model_policy import preferred_model
from .paper_first_problem_discovery_contract import (
    DISCOVERY_LANES, SEARCH_PORTFOLIO_PRIMITIVES, LANE_DISTINCT_SOURCE_MINIMUM, LANE_EVIDENCE_REQUIRED, LANE_MACHINE_CONTRACTS, LANE_SOURCE_ROLES,
    PAPERABILITY_AXES, PAPERABILITY_AXIS_STATUSES,
)

PortfolioCaller = Callable[..., dict[str, Any]]
DEFAULT_RAW_SEEDS=120
DEFAULT_ARCHIVE_CAPACITY=48
DEFAULT_EVOLUTION_PARENTS=24
DEFAULT_SECOND_GENERATION=12
DEFAULT_FORMULATION_BUDGET=24
DEFAULT_REPAIR_PARENTS=12
DEFAULT_REPAIR_CHILDREN_PER_PARENT=2
DEFAULT_EXPANSION_SHARD_SIZE=6
DEFAULT_MAX_PARALLEL_CALLS=2
CROSS_DOMAIN_STRUCTURES=(
    "continual learning / stability-plasticity", "online algorithms / regret and switching cost",
    "distributed systems / consistency and partial failure", "fault-tolerant systems / rollback and irreversible effects",
    "software evolution / compatibility and technical debt", "causal discovery / identifiability and interventions",
    "ecology and evolution / diversity, selection, and niche formation", "control theory / observability, stability, and adaptive control",
    "active learning / value of information", "adaptive experimentation / sequential design",
    "program synthesis / version spaces and counterexamples", "organizational learning / distributed knowledge and routines",
    "database systems / consistency and provenance", "mechanism design / incentives and strategic feedback",
    "information theory / sufficiency and information constraints",
)

def _norm(x:Any)->str:return " ".join(re.sub(r"[^a-z0-9]+"," ",str(x or "").lower()).split())
def _tokens(r):
    text=" ".join(str(r.get(k) or "") for k in ("title","problem_seed","scientific_tension","problem_family","agent_specific_constraint","structural_signature"))
    return {t for t in _norm(text).split() if len(t)>=3}
def _jaccard(a,b):
    x,y=_tokens(a),_tokens(b);return len(x&y)/max(1,len(x|y)) if x and y else 0.0
def _score(r):
    s=r.get("scores") or {};return .30*float(s.get("importance",0) or 0)+.25*float(s.get("specificity",0) or 0)+.25*float(s.get("seed_distance",0) or 0)+.20*float(s.get("evidence_grounding",0) or 0)
def _seed_key(r):return hashlib.sha256((_norm(r.get("structural_signature")) or _norm(r.get("problem_seed"))).encode()).hexdigest()
def _source_refs(r):
    e=r.get("empirical_evidence") or {};return [str((e.get(k) or {}).get("ref") or "").strip() for k in ("source_a","source_b")]

def _normalize_seed(raw,lane,index):
    s=raw.get("scores") or {};e=raw.get("empirical_evidence") or {}
    def src(key):
        x=e.get(key) or {};return {"ref":str(x.get("ref") or "").strip(),"claim":str(x.get("claim") or "").strip(),"evidence_role":str(x.get("evidence_role") or "").strip().upper()}
    return {
        "seed_id":str(raw.get("seed_id") or f"{lane}-{index:03d}"),"discovery_lane":lane,
        "title":str(raw.get("title") or "").strip(),"problem_seed":str(raw.get("problem_seed") or "").strip(),
        "scientific_tension":str(raw.get("scientific_tension") or "").strip(),"problem_family":str(raw.get("problem_family") or "unclassified").strip().lower(),
        "structural_signature":str(raw.get("structural_signature") or "").strip(),"agent_specific_constraint":str(raw.get("agent_specific_constraint") or "").strip(),
        "empirical_evidence":{"source_a":src("source_a"),"source_b":src("source_b"),"relation":str(e.get("relation") or "").strip()},
        "lane_evidence":dict(raw.get("lane_evidence") or {}) if isinstance(raw.get("lane_evidence"),dict) else {},
        "cross_domain_origin":str(raw.get("cross_domain_origin") or "").strip(),
        "scores":{k:max(0.,min(100.,float(s.get(k,0) or 0))) for k in ("importance","specificity","seed_distance","evidence_grounding")},
        "branch_depth":int(raw.get("branch_depth") or 0),"parent_id":str(raw.get("parent_id") or ""),"scientific_authority":False,
    }

def _valid_seed(r,reg):
    lane=str(r.get("discovery_lane") or "");refs=_source_refs(r);e=r.get("empirical_evidence") or {};roles=tuple(str((e.get(k) or {}).get("evidence_role") or "") for k in ("source_a","source_b"))
    lane_evidence=r.get("lane_evidence") or {}
    return bool(
        lane in SEARCH_PORTFOLIO_PRIMITIVES and r.get("title") and r.get("problem_seed") and r.get("structural_signature")
        and len(set(refs))>=LANE_DISTINCT_SOURCE_MINIMUM[lane] and all(ref in reg for ref in refs) and roles==LANE_SOURCE_ROLES[lane]
        and all(str(lane_evidence.get(k) or "").strip() for k in LANE_EVIDENCE_REQUIRED[lane])
    )

def _semantic_dedup(rows,threshold=.78,protected_ids=None):
    protected={str(value) for value in (protected_ids or []) if str(value)};kept=[];dropped=[];exact=defaultdict(set)
    ordered=sorted(rows,key=lambda r:(str(r.get("seed_id") or "") in protected,_score(r)),reverse=True)
    for r in ordered:
        lane=r["discovery_lane"];seed_id=str(r.get("seed_id") or "");key=_seed_key(r);is_protected=seed_id in protected
        same=[p for p in kept if p["discovery_lane"]==lane and not (is_protected and str(p.get("seed_id") or "") in protected)];closest=max((_jaccard(r,p) for p in same),default=0.)
        if not is_protected and key in exact[lane]:dropped.append({"seed_id":r["seed_id"],"lane":lane,"reason":"exact-within-lane-duplicate"});continue
        if not is_protected and closest>=threshold:dropped.append({"seed_id":r["seed_id"],"lane":lane,"reason":"semantic-within-lane-near-duplicate","similarity":round(closest,4)});continue
        exact[lane].add(key);kept.append(r)
    return kept,dropped

def _assign_structural_clusters(rows,threshold=.82):
    reps=[]
    for r in sorted(rows,key=_score,reverse=True):
        sims=[_jaccard(r,p) for p in reps];best=max(sims,default=0.0)
        if reps and best>=threshold:cluster=reps[sims.index(best)]["structural_cluster_id"]
        else:cluster=f"PC-{len(reps)+1:03d}";reps.append(r)
        r["structural_cluster_id"]=cluster
    return rows,len(reps)

def _maxmin_select(rows,capacity,required_ids=None):
    if capacity<=0:return []
    required_order=[];seen_required=set()
    for value in required_ids or []:
        seed_id=str(value or "")
        if seed_id and seed_id not in seen_required:
            seen_required.add(seed_id);required_order.append(seed_id)
    by_id={str(r.get("seed_id") or ""):r for r in rows if str(r.get("seed_id") or "")}
    selected=[by_id[seed_id] for seed_id in required_order if seed_id in by_id][:capacity]
    if len(rows)<=capacity:return selected+[r for r in rows if r not in selected]
    by_lane=defaultdict(list)
    for r in rows:by_lane[r["discovery_lane"]].append(r)
    for lane in SEARCH_PORTFOLIO_PRIMITIVES:
        candidates=[r for r in by_lane[lane] if r not in selected]
        if candidates and len(selected)<capacity:selected.append(max(candidates,key=_score))
    remain=[r for r in rows if r not in selected]
    while remain and len(selected)<capacity:
        seen={r.get("structural_cluster_id") for r in selected}
        def utility(r):
            max_sim=max((_jaccard(r,p) for p in selected),default=0.0);new_cluster=int(r.get("structural_cluster_id") not in seen);lane_count=sum(p["discovery_lane"]==r["discovery_lane"] for p in selected)
            return (new_cluster,1.0-max_sim,-lane_count,_score(r))
        chosen=max(remain,key=utility);selected.append(chosen);remain.remove(chosen)
    return selected

def _archives(rows,capacity,required_ids=None):
    breadth=_maxmin_select(rows,capacity,required_ids=required_ids);novelty=sorted(rows,key=lambda r:(float((r.get("scores") or {}).get("seed_distance",0)),_score(r)),reverse=True)[:max(8,capacity//3)]
    anomaly={"CONVERGENT_FAILURE","ASSUMPTION_BREAK","UNEXPLAINED_BOUNDARY","LONGITUDINAL_EMERGENCE"}
    return {
        "breadth":[r["seed_id"] for r in breadth],"novelty":[r["seed_id"] for r in novelty],
        "contradiction":[r["seed_id"] for r in rows if r["discovery_lane"]=="CONTRADICTION"][:max(6,capacity//4)],
        "anomaly":[r["seed_id"] for r in rows if r["discovery_lane"] in anomaly][:max(8,capacity//3)],
        "cross_domain":[r["seed_id"] for r in rows if r["discovery_lane"]=="CROSS_DOMAIN_STRUCTURAL_ANALOGY"][:max(6,capacity//4)],
    }

def _lane_records(lane,records,max_records=20):
    def typed_count(r,key):return len(((r.get("typed_evidence") or {}).get(key) or []))
    scored=[]
    for idx,r in enumerate(records):
        if lane=="ASSUMPTION_BREAK":score=8*typed_count(r,"operational_assumptions")+3*typed_count(r,"measured_failures")
        elif lane=="CONVERGENT_FAILURE":score=6*typed_count(r,"measured_failures")+typed_count(r,"boundary_observations")
        elif lane in {"UNEXPLAINED_BOUNDARY","LONGITUDINAL_EMERGENCE"}:score=6*typed_count(r,"boundary_observations")+2*typed_count(r,"measured_failures")
        else:score=2*len(r.get("empirical_facts") or [])+typed_count(r,"measured_failures")+typed_count(r,"boundary_observations")
        scored.append((score,-idx,r))
    picked=[r for _,_,r in sorted(scored,key=lambda x:(x[0],x[1]),reverse=True)[:max_records]]
    # ASSUMPTION_BREAK must expose at least one grounded assumption even if it is
    # globally low-ranked; append it by replacing the last slot if necessary.
    if lane=="ASSUMPTION_BREAK" and not any(typed_count(r,"operational_assumptions") for r in picked):
        assumption=next((r for r in records if typed_count(r,"operational_assumptions")),None)
        if assumption:picked=(picked[:-1]+[assumption]) if picked else [assumption]
    return picked

def _evidence_payload(records):
    return [{
        "ref":r.get("ref"),"title":r.get("title"),"publication_date":r.get("publication_date"),"abstract":str(r.get("abstract") or "")[:1500],
        "empirical_facts":[str(f.get("text") or "")[:340] for f in (r.get("empirical_facts") or [])[:3] if isinstance(f,dict)],
        "typed_evidence":{k:[str(f.get("text") or "")[:340] for f in ((r.get("typed_evidence") or {}).get(k) or [])[:2] if isinstance(f,dict)] for k in ("operational_assumptions","measured_failures","boundary_observations")},
    } for r in records[:32]]

def _closed_search_rows(search_memory):
    """Return search closures with explicit legacy blocked_objects compatibility.

    Canonical persistence uses ``closed_objects`` + ``search_closure_certified``.
    Historical snapshots/tests may still supply only ``blocked_objects`` where
    ``dead_end_certified`` carried the old overloaded search-closure meaning. That
    legacy fallback is read-only compatibility and is never written back canonically.
    """
    memory=search_memory or {}
    canonical=isinstance(memory.get("closed_objects"),list)
    rows=memory.get("closed_objects") if canonical else (memory.get("blocked_objects") or [])
    return [
        row for row in (rows or [])
        if isinstance(row,dict)
        and (row.get("search_closure_certified") is True or (not canonical and row.get("dead_end_certified") is True))
    ]


def _fresh_phenomenon_closed_keys(dead_end_memory):
    """Return exact (primary ref, evidence-text SHA) pairs already search-closed.

    Closure is intentionally boundary-level rather than source-level: a paper can
    carry several independent anomalies, and closing one exact search object must
    not blacklist the rest of the paper. Scientific dead-end status is irrelevant
    to this deduplication decision.
    """
    closed=set()
    for row in _closed_search_rows(dead_end_memory):
        closure=row.get("fresh_phenomenon_closure") or {}
        if not isinstance(closure,dict) or closure.get("scientific_authority") is not False:continue
        ref=str(closure.get("source_ref") or "").strip()
        if not ref.startswith("arXiv:"):continue
        for value in closure.get("closed_evidence_sha256") or []:
            sha=str(value or "").strip().lower()
            if re.fullmatch(r"[0-9a-f]{64}",sha):closed.add((ref,sha))
    return closed


def _fresh_phenomenon_held_keys(dead_end_memory):
    """Return exact evidence objects paused by provenance-bound support holds.

    Holds are operational only: unlike principle closures they say nothing about
    the mechanism's truth. They merely keep an unreplayable phenomenon from
    consuming fresh-search slots until a separate release re-audit clears the
    hold artifact.
    """
    held=set()
    for row in (dead_end_memory or {}).get("hold_objects") or []:
        if not isinstance(row,dict) or row.get("dead_end_certified") is True:continue
        hold=row.get("fresh_phenomenon_hold") or {}
        if not isinstance(hold,dict) or hold.get("scientific_authority") is not False:continue
        ref=str(hold.get("source_ref") or "").strip();sha=str(hold.get("evidence_sha256") or "").strip().lower()
        if ref.startswith("arXiv:") and re.fullmatch(r"[0-9a-f]{64}",sha):held.add((ref,sha))
    return held


def _fresh_evidence_sha(item):
    text=" ".join(str((item or {}).get("text") or "").split())
    supplied=str((item or {}).get("text_sha256") or "").strip().lower()
    return supplied if re.fullmatch(r"[0-9a-f]{64}",supplied) else hashlib.sha256(text.encode()).hexdigest()


def _fresh_phenomenon_priors(records,limit=32,recent_days=45,dead_end_memory=None):
    """Return recent *evidence-level* quantitative/failure boundaries for search.

    v11 rotated at source granularity, so one already-explained anomaly could keep
    consuming a paper's fresh slot or force us to suppress the whole paper. v12
    assigns one content-addressed phenomenon_id per primary evidence item and drops
    only those exact items carrying a principle-certified closure receipt.
    """
    parsed=[]
    for r in records:
        if not isinstance(r,dict) or not str(r.get("ref") or "").strip():continue
        try: published=date.fromisoformat(str(r.get("publication_date") or ""))
        except ValueError:continue
        parsed.append((published,r))
    if not parsed:return []
    latest=max(day for day,_ in parsed);cutoff=latest-timedelta(days=max(0,int(recent_days)))
    contrast=re.compile(r"\b(?:from|to|vs\.?|versus|while|despite|drop|decreas|increas|improv|worse|better|plateau|reduc|compress|outperform|lower|higher|only)\w*\b",re.I)
    number=re.compile(r"(?:\b\d+(?:\.\d+)?\s*(?:%|points?|x)\b|\b0\.\d+\b)",re.I)
    anomaly_cue=re.compile(
        r"(?:\bplateau\w*\b|\bfluctuat\w*\b|\bnon[- ]?monotonic\w*\b|\bnot\s+monotonic\b|"
        r"\bwithout\s+(?:a\s+)?consistent\s+gain\b|\bsame\s+peak\b|\brevers\w*\b|\binversion\b|"
        r"\bcliff\b|\bthreshold\b|\bceiling\b|\bsaturat\w*\b|\bdespite\b|\bbut\s+additional\b|"
        r"\bunderperform\w*\b|\bcollapse\w*\b|\bnegative\s+transfer\b|\bworse\b)",
        re.I,
    )
    failure_cue=re.compile(
        r"(?:\bfail(?:s|ed|ing)?\s+(?:to|despite)\b|"
        r"\bunderperform\w*\b|"
        r"\b(?:performance|accuracy|reward|success|utility|quality)\s+(?:degrad\w*|declin\w*|drop\w*)\b|"
        r"\bdegrad(?:es|ed|ing)?\b.{0,48}\b(?:performance|accuracy|reward|success|utility|quality)\b|"
        r"\bcollapse\w*\b|\boverly\s+restrict\w*\b|\bnegative\s+transfer\b|\bmislead\w*\b|"
        r"\bcannot\b|\bunable\b|\binstab\w*\b|\bregress\w*\b|\bdrop\w*\b|\bworse\b|"
        r"\blower\s+utility\b|\boverfit\w*\b|\bredundan\w*\b|\bconflict\w*\b|\bpoison\w*\b|"
        r"\battack\s+success(?:\s+rate)?\b.{0,32}\b(?:increas\w*|ris\w*|remain\w*\s+high|worsen\w*)\b)",
        re.I,
    )
    closed=_fresh_phenomenon_closed_keys(dead_end_memory)
    held=_fresh_phenomenon_held_keys(dead_end_memory)
    priors=[]
    kind_priority={"measured_failure":3,"boundary_observation":2,"quantitative_anomaly":1}
    for published,r in parsed:
        if published<cutoff:continue
        ref=str(r.get("ref") or "");typed=r.get("typed_evidence") or {};facts=[x for x in r.get("empirical_facts") or [] if isinstance(x,dict) and str(x.get("text") or "").strip()]
        items=[]
        items.extend(("measured_failure",x) for x in typed.get("measured_failures") or [] if isinstance(x,dict) and str(x.get("text") or "").strip() and failure_cue.search(str(x.get("text") or "")))
        boundary_protocol_only=re.compile(
            r"(?:\bwe\s+(?:set|use)\b.{0,80}\b(?:threshold|temperature)\b|"
            r"\bwe\s+run\b.{0,100}\bon\s+all\s+\d+\b.{0,120}\bthreshold\b|"
            r"\bnot\s+applied\s+to\b.{0,80}\b(?:mini|benchmark|batch)\b|"
            r"\billustrates?\s+(?:one\s+)?representative\s+failure\s+trace\b|"
            r"\bcrosses?\s+the\s+evidence\s+threshold\s+on\s+its\s+second\b)",re.I)
        items.extend(
            ("boundary_observation",x)
            for x in typed.get("boundary_observations") or []
            if isinstance(x,dict)
            and str(x.get("text") or "").strip()
            and not boundary_protocol_only.search(str(x.get("text") or ""))
            and (
                failure_cue.search(str(x.get("text") or ""))
                or (
                    number.search(str(x.get("text") or ""))
                    and contrast.search(str(x.get("text") or ""))
                    and anomaly_cue.search(str(x.get("text") or ""))
                )
            )
        )
        items.extend(
            ("quantitative_anomaly",x)
            for x in facts
            if number.search(str(x.get("text") or ""))
            and contrast.search(str(x.get("text") or ""))
            and (anomaly_cue.search(str(x.get("text") or "")) or failure_cue.search(str(x.get("text") or "")))
        )
        seen=set()
        for kind,item in items:
            text=" ".join(str(item.get("text") or "").split());sha=_fresh_evidence_sha(item)
            if not text or sha in seen:continue
            seen.add(sha)
            if (ref,sha) in closed or (ref,sha) in held:continue
            priors.append({
                "ref":ref,"publication_date":published.isoformat(),"title":str(r.get("title") or ""),
                "phenomenon_id":sha,"phenomenon_kind":kind,"phenomenon_text":text,
                "measured_failures":[text] if kind=="measured_failure" else [],
                "boundary_observations":[text] if kind=="boundary_observation" else [],
                "quantitative_anomalies":[text] if kind=="quantitative_anomaly" else [],
                "empirical_facts":[" ".join(str(x.get("text") or "").split()) for x in facts[:2]],
                "search_instruction":"target this exact measured/quantitative phenomenon; name the strongest mature reduction and cheapest independent-truth substrate before proposing a method",
                "priority":kind_priority[kind],"scientific_authority":False,
            })
    priors.sort(key=lambda row:(row["publication_date"],row["priority"],row["ref"],row["phenomenon_id"]),reverse=True)
    return priors[:limit]


def _fresh_phenomenon_target(records,part,limit=32,dead_end_memory=None):
    priors=_fresh_phenomenon_priors(records,limit=limit,dead_end_memory=dead_end_memory)
    if not priors:return {}
    index=max(0,int(part)-1)%len(priors)
    return priors[index]

def _inversion_asset_records(dead_end_memory):
    records=[];seen=set()
    for row in (dead_end_memory or {}).get("inversion_asset_evidence") or []:
        if not isinstance(row,dict) or row.get("scientific_authority") is not False or row.get("search_active") is False:continue
        ref=str(row.get("asset_ref") or "").strip();sha=str(row.get("source_sha256") or "").strip().lower();url=str(row.get("primary_url") or "").strip();title=str(row.get("title") or "").strip()
        facts=[" ".join(str(value or "").split()) for value in row.get("empirical_facts") or [] if str(value or "").strip()]
        if not ref.startswith("first-party-asset:") or ref in seen or not re.fullmatch(r"[0-9a-f]{64}",sha) or not url.startswith("https://") or not title or not facts:continue
        seen.add(ref);records.append({
            "ref":ref,"title":title,"abstract":" ".join(facts)[:4000],"primary_url":url,"source_sha256":sha,"primary_source_verified":True,
            "empirical_facts":[{"text":fact,"evidence_tier":"first-party-code-structural-witness"} for fact in facts[:8]],
            "typed_evidence":{"operational_assumptions":[],"measured_failures":[],"boundary_observations":[]},
            "source_kind":"principle-readjudication-first-party-asset","scientific_authority":False,
        })
    return records

def _positive_residual_asset_records(dead_end_memory):
    records=[];seen=set()
    for row in (dead_end_memory or {}).get("positive_residual_asset_evidence") or []:
        if not isinstance(row,dict) or row.get("scientific_authority") is not False or row.get("search_active") is not True:continue
        ref=str(row.get("asset_ref") or "").strip();sha=str(row.get("source_sha256") or "").strip().lower();url=str(row.get("primary_url") or "").strip();title=str(row.get("title") or "").strip();contract=row.get("search_contract") or {}
        facts=[" ".join(str(value or "").split()) for value in row.get("empirical_facts") or [] if str(value or "").strip()]
        if not ref.startswith("positive-residual-asset:") or ref in seen or not re.fullmatch(r"[0-9a-f]{64}",sha) or not url.startswith("https://") or not title or len(facts)<2:continue
        if contract.get("prospective_prediction_required") is not True or contract.get("pre_outcome_information_only") is not True:continue
        seen.add(ref);records.append({
            "ref":ref,"title":title,"abstract":" ".join(facts)[:5000],"primary_url":url,"source_sha256":sha,"primary_source_verified":True,
            "empirical_facts":[{"text":fact,"evidence_tier":"provenance-audited-internal-experiment"} for fact in facts[:10]],
            "typed_evidence":{"operational_assumptions":[],"measured_failures":[{"text":fact,"evidence_tier":"provenance-audited-internal-experiment"} for fact in facts[1:]],"boundary_observations":[{"text":facts[0],"evidence_tier":"provenance-audited-internal-experiment"}]},
            "source_kind":"positive-residual-internal-experiment","search_contract":dict(contract),"failed_mechanisms":list(row.get("failed_mechanisms") or []),"scientific_authority":False,
        })
    return records

def _search_asset_records(dead_end_memory):
    return list(_inversion_asset_records(dead_end_memory))+list(_positive_residual_asset_records(dead_end_memory))

def _prompt_dead_end_memory(dead_end_memory):
    """Project persistent memory into a search-safe prompt view.

    Archived search assets remain in the canonical memory for provenance, but their
    direct inversion seeds and asset payloads must not be visible to generators.
    Keep each closed-basin statement/reopen boundary so the model still avoids re-entry.
    Global closure wins over stale per-certificate asset flags.
    """
    memory=json.loads(json.dumps(dead_end_memory or {},ensure_ascii=False))
    globally_inactive={str(row.get("asset_ref") or "") for row in memory.get("inversion_asset_evidence") or [] if isinstance(row,dict) and row.get("search_active") is False}
    memory["inversion_asset_evidence"]=[row for row in memory.get("inversion_asset_evidence") or [] if not isinstance(row,dict) or row.get("search_active") is not False]
    memory["positive_residual_asset_evidence"]=[row for row in memory.get("positive_residual_asset_evidence") or [] if not isinstance(row,dict) or row.get("search_active") is True]
    for row in _closed_search_rows(memory):
        asset=row.get("opposite_search_asset_evidence") or {}
        ref=str(asset.get("asset_ref") or "") if isinstance(asset,dict) else ""
        if not ref or (ref not in globally_inactive and asset.get("search_active") is not False):continue
        row["opposite_search_asset_evidence"]={"search_active":False,"scientific_authority":False}
        if isinstance(row.get("evidence_basis"),list):
            row["evidence_basis"]=[value for value in row["evidence_basis"] if str(value)!=ref]
        counter=row.get("counter_explanation") or {}
        if isinstance(counter,dict):
            counter=dict(counter)
            counter["opposite_search_seed"]="ARCHIVED_INACTIVE_SEARCH_ASSET"
            if isinstance(counter.get("evidence_refs"),list):
                counter["evidence_refs"]=[value for value in counter["evidence_refs"] if str(value)!=ref]
            row["counter_explanation"]=counter
    memory["inversion_asset_evidence_count"]=len(memory["inversion_asset_evidence"])
    memory["positive_residual_asset_evidence_count"]=len(memory["positive_residual_asset_evidence"])
    return memory

def _positive_residual_priors(dead_end_memory,limit=6):
    priors=[]
    for row in (dead_end_memory or {}).get("positive_residual_asset_evidence") or []:
        if not isinstance(row,dict) or row.get("scientific_authority") is not False or row.get("search_active") is not True:continue
        contract=row.get("search_contract") or {}
        priors.append({"asset_ref":str(row.get("asset_ref") or ""),"phenomenon_status":str(row.get("phenomenon_status") or ""),"mechanism_status":str(row.get("mechanism_status") or ""),"failed_mechanisms":list(row.get("failed_mechanisms") or []),"question":str(contract.get("question") or ""),"must_explain":list(contract.get("must_explain") or []),"must_beat_or_condition_on":list(contract.get("must_beat_or_condition_on") or []),"temporal_exposure_standalone_branch_closed":contract.get("temporal_exposure_standalone_branch_closed") is True,"mandatory_reduction_before_treatment_semantics_experiment":list(contract.get("mandatory_reduction_before_treatment_semantics_experiment") or []),"opposite_search_seed":str(contract.get("opposite_search_seed") or ""),"prohibited_rescues":list(contract.get("prohibited_rescues") or []),"prospective_prediction_required":contract.get("prospective_prediction_required") is True,"pre_outcome_information_only":contract.get("pre_outcome_information_only") is True})
        if len(priors)>=limit:break
    return priors

def _opposite_search_priors(dead_end_memory,limit=8):
    priors=[]
    globally_inactive={str(row.get("asset_ref") or "") for row in (dead_end_memory or {}).get("inversion_asset_evidence") or [] if isinstance(row,dict) and row.get("search_active") is False}
    for row in _closed_search_rows(dead_end_memory):
        asset=row.get("opposite_search_asset_evidence") or {}
        ref=str(asset.get("asset_ref") or "") if isinstance(asset,dict) else ""
        if ref in globally_inactive or (isinstance(asset,dict) and asset and asset.get("search_active") is False):continue
        counter=row.get("counter_explanation") or {}
        if not isinstance(counter,dict):continue
        principle=str(counter.get("opposite_principle") or "").strip();seed=str(counter.get("opposite_search_seed") or "").strip()
        if not principle or not seed:continue
        priors.append({
            "source_candidate_id":str(row.get("source_candidate_id") or ""),
            "basin":str(row.get("basin") or ""),
            "counter_explanation_type":str(counter.get("type") or ""),
            "closure_layer":str(row.get("closure_layer") or ""),
            "failure_layer":str(row.get("failure_layer") or ""),
            "memory_class":str(row.get("memory_class") or ""),
            "principle_update_allowed":row.get("principle_update_allowed") is True,
            "broader_core_principle_falsified":row.get("broader_core_principle_falsified") is True,
            "opposite_principle":principle,
            "opposite_search_seed":seed,
            "reopen_condition":str(counter.get("reopen_condition") or row.get("reopen_only_if") or ""),
            "evidence_refs":list(counter.get("evidence_refs") or row.get("current_source_refs") or [])[:6],
            "asset_ref":str((row.get("opposite_search_asset_evidence") or {}).get("asset_ref") or ""),
        })
        if len(priors)>=limit:break
    return priors

def _expansion_prompt(lane,records,count,dead_end_memory=None,fresh_target_ref="",fresh_target_phenomenon_id=""):
    assets=_inversion_asset_records(dead_end_memory);positive_assets=_positive_residual_asset_records(dead_end_memory);asset_refs={str(row.get("ref") or "") for row in assets+positive_assets};paper_records=[row for row in records if str(row.get("ref") or "") not in asset_refs]
    fresh_priors=_fresh_phenomenon_priors(paper_records,dead_end_memory=dead_end_memory)
    target_id=str(fresh_target_phenomenon_id or "").strip().lower()
    fresh_target=next((row for row in fresh_priors if (target_id and str(row.get("phenomenon_id") or "").lower()==target_id) or (not target_id and str(row.get("ref") or "")==str(fresh_target_ref or ""))),{})
    records=(assets+positive_assets+_lane_records(lane,paper_records,max_records=max(1,20-len(assets)-len(positive_assets))))[:20]
    asset_requirement=("ASSET-INVERSION EXECUTION REQUIREMENT: provenance-bound first-party inversion assets are available. Seed 1 MUST directly execute one certified opposite-search prior by citing a FIRST_PARTY_INVERSION_ASSET ref in source_a; because this lane permits a single distinct source, source_b MAY cite the same asset ref for a second independently stated grounded fact. The seed must test the opposite principle/reopen boundary rather than restate the certified search closure. STRUCTURAL-GRAPH RULE: if the first-party implementation directly exposes whether a causal/update edge exists, do NOT formulate identifiability of that edge. Instead target a downstream consequence of that structure and state what ordinary distribution-shift, stale-supervisor, online-adaptation, or alternating-optimization explanation must be beaten. Remaining seeds may explore any grounded anomaly. " if assets and count>0 else "")
    positive_slot=2 if assets else 1
    positive_requirement=(f"POSITIVE-RESIDUAL EXECUTION REQUIREMENT: Seed {positive_slot} MUST cite a POSITIVE_RESIDUAL_ASSET ref in source_a (source_b MAY reuse the same ref because this lane permits one distinct source). It must propose a NEW scientific mechanism/problem that simultaneously explains the surviving phenomenon and the recorded failed/reduced mechanisms. It MUST make a prospective prediction from pre-outcome information, explicitly condition on or beat the recorded same-information baselines, and obey every prohibited_rescue in the asset. If the asset marks temporal_exposure_standalone_branch_closed, DO NOT propose K-step mediation, ON/OFF exposure windows, duration, cumulative dose, or repeated conditioning as the new mechanism. The only permitted next memory seed must change executable treatment semantics/version identity and must name the mandatory nonstationary/versioned-treatment reductions it must beat before any experiment. Do not use full-trajectory distance or endpoint length/success. This asset is search evidence only, never novelty or experiment authority. " if lane=="UNEXPLAINED_BOUNDARY" and positive_assets and count>=positive_slot else "")
    fresh_requirement=(f"FRESH-PHENOMENON BOUNDARY-COVERAGE REQUIREMENT: no active inversion or positive-residual asset exists. For UNEXPLAINED_BOUNDARY, Seed 1 MUST cite the specifically assigned FRESH_PHENOMENON_TARGET ref={fresh_target.get('ref')} AND directly target phenomenon_id={fresh_target.get('phenomenon_id')} with phenomenon_text={json.dumps(fresh_target.get('phenomenon_text'),ensure_ascii=False)}. Do not substitute another anomaly from the same paper or a more salient fresh source. The seed must name in scientific_tension the strongest mature reduction class it expects to face (for example information redundancy, rate-distortion, adaptive validation, distribution shift, or ceiling effects) and in agent_specific_constraint state what released/independent truth could falsify the residual. Missing released substrate is a HOLD, never evidence of novelty or scientific failure. Remaining seeds may explore other grounded phenomena. " if lane=="UNEXPLAINED_BOUNDARY" and not assets and not positive_assets and fresh_target and count>0 else "")
    contract={"source_roles":list(LANE_SOURCE_ROLES[lane]),"minimum_distinct_primary_sources":LANE_DISTINCT_SOURCE_MINIMUM[lane],"required_lane_evidence":list(LANE_EVIDENCE_REQUIRED[lane]),"machine_contract":LANE_MACHINE_CONTRACTS[lane]}
    analogy=list(CROSS_DOMAIN_STRUCTURES) if lane=="CROSS_DOMAIN_STRUCTURAL_ANALOGY" else []
    shape={"seeds":[{
        "seed_id":"TEMP-1","title":"...","problem_seed":"scientific question, not a method","scientific_tension":"...","problem_family":"...","structural_signature":"failure|object|regime|consequence","agent_specific_constraint":"...",
        "empirical_evidence":{"source_a":{"ref":"primary-ref","claim":"grounded claim","evidence_role":contract["source_roles"][0]},"source_b":{"ref":"primary-ref","claim":"grounded claim","evidence_role":contract["source_roles"][1]},"relation":"why the evidence instantiates this lane"},
        "lane_evidence":{key:"..." for key in contract["required_lane_evidence"]},"cross_domain_origin":"optional","scores":{"importance":70,"specificity":70,"seed_distance":70,"evidence_grounding":70}
    }],"notes":"..."}
    return (
        "EXPANSION stage for an ICLR paper-problem Search Portfolio on self-evolving LLM agents. Generate PROBLEM SEEDS, never methods. "
        "This is exploration, not adjudication: DO NOT apply mature-theory, closest-work, domain-transfer, or Negative-Space novelty vetoes here. "
        "Do not invent open-world missing-cell claims. Preserve structurally unusual seeds even if their final novelty is uncertain. "
        "ANOMALY-FIRST SEARCH: actively inspect source-local sign reversals, nonmonotonicity, thresholds, plateaus, history dependence, composition effects, and bounded failure transitions; do not wait for a second paper to have used the same metric when this lane permits one source. When equally grounded seeds compete, prefer an operational core whose decisive comparison could plausibly be materialized on released units, first-party code, or an existing provenance-audited agent substrate. Support feasibility is a search priority only and never novelty evidence. "
        "CLOSED-BASIN INVERSION is a search prior, never authority: a layer-typed scoped closure may contribute its opposite principle/search seed, but only generate an inversion seed when the supplied fresh primary evidence independently grounds it and the seed escapes the recorded basin/reopen condition. Preserve closure_layer/failure_layer exactly. problem_novelty is an upstream literature/theory stop, not an experimental failure layer. Scientific closures use only execution, experiment_identifiability, optimization, operationalization, method_realization, assumption_scope, or core_principle; only core_principle may enter persistent scientific dead-end memory or update the scoped principle, and broader benchmark/phenomenon falsification remains a separate flag. Never turn a closed-basin inversion into an automatic survivor or fabricate support merely to reuse it. "+asset_requirement+positive_requirement+fresh_requirement+
        f"Generate exactly {count} materially distinct grounded seeds for lane {lane}. The lane machine contract is {json.dumps(contract,ensure_ascii=False)}. "
        f"Use two grounded evidence items and at least {LANE_DISTINCT_SOURCE_MINIMUM[lane]} distinct primary source ref(s), following the lane contract; obey evidence roles. Claims must be supported by supplied primary text. "
        "Vary problem families and structural signatures; avoid paraphrase-only variants. "
        "For CROSS_DOMAIN_STRUCTURAL_ANALOGY, the external domain is only an analogy prior and never novelty by itself; state the Agent-specific structural constraint. "
        f"Analogy priors={json.dumps(analogy,ensure_ascii=False)}. FIRST_PARTY_INVERSION_ASSETS={json.dumps(_evidence_payload(assets),ensure_ascii=False,separators=(',',':'))}. POSITIVE_RESIDUAL_ASSETS={json.dumps(_evidence_payload(positive_assets),ensure_ascii=False,separators=(',',':'))}. POSITIVE_RESIDUAL_PRIORS={json.dumps(_positive_residual_priors(dead_end_memory),ensure_ascii=False,separators=(',',':'))}. FRESH_PHENOMENON_TARGET={json.dumps(fresh_target,ensure_ascii=False,separators=(',',':'))}. FRESH_PHENOMENON_PRIORS={json.dumps(fresh_priors,ensure_ascii=False,separators=(',',':'))}. LAYER-TYPED CLOSED-BASIN INVERSION PRIORS={json.dumps(_opposite_search_priors(dead_end_memory),ensure_ascii=False,separators=(',',':'))}. CLOSED-BASIN SEARCH MEMORY (search-control only, never scientific authority)={json.dumps(_prompt_dead_end_memory(dead_end_memory),ensure_ascii=False,separators=(',',':'))}. VERIFIED PRIMARY EVIDENCE={json.dumps(_evidence_payload(records),ensure_ascii=False,separators=(',',':'))}. "
        f"Return JSON only: {json.dumps(shape,ensure_ascii=False,separators=(',',':'))}"
    )

def _evolution_prompt(parents,generation):
    compact=[{k:p.get(k) for k in ("seed_id","discovery_lane","title","problem_seed","scientific_tension","problem_family","structural_signature","agent_specific_constraint","empirical_evidence","lane_evidence","cross_domain_origin","scores")} for p in parents]
    shape={"children":[{"parent_id":"...","title":"...","problem_seed":"...","scientific_tension":"...","problem_family":"...","structural_signature":"...","agent_specific_constraint":"...","changed_assumption":"...","why_deeper":"...","scores":{"importance":75,"specificity":75,"seed_distance":75,"evidence_grounding":75}}]}
    return (
        f"EVOLUTION generation {generation} of a scientific problem Search Portfolio. Give exactly one child per parent. "
        "Change one substantive assumption, moderator, causal/decision object, regime, information constraint, or interaction structure so the question becomes more paper-shaped. "
        "Do not propose a method and still do NOT apply mature-theory novelty vetoes. Do not change the parent's discovery lane, empirical evidence, or lane-evidence contract; those are inherited by code. "
        f"PARENTS={json.dumps(compact,ensure_ascii=False,separators=(',',':'))}. Return JSON only: {json.dumps(shape,ensure_ascii=False,separators=(',',':'))}"
    )


def _normalize_paperability_axes(value):
    value=value if isinstance(value,dict) else {}
    out={}
    allowed=set(PAPERABILITY_AXIS_STATUSES)
    for axis,label in PAPERABILITY_AXES.items():
        item=value.get(axis) or {}
        if isinstance(item,str): item={"status":item}
        if not isinstance(item,dict): item={}
        status=str(item.get("status") or "OPEN").strip().upper()
        if status not in allowed: status="OPEN"
        out[axis]={
            "label":label,
            "status":status,
            "rationale":" ".join(str(item.get("rationale") or "").split())[:700],
        }
    return out


def _paperability_survives(axes):
    return any((axes.get(axis) or {}).get("status") in {"SUPPORTED","PLAUSIBLE"} for axis in PAPERABILITY_AXES)


def _attack_repair_prompt(parents,children_per_parent=DEFAULT_REPAIR_CHILDREN_PER_PARENT):
    compact=[{k:p.get(k) for k in ("seed_id","parent_id","branch_depth","discovery_lane","title","problem_seed","scientific_tension","problem_family","structural_signature","agent_specific_constraint","empirical_evidence","lane_evidence","cross_domain_origin","scores")} for p in parents]
    axes={axis:label for axis,label in PAPERABILITY_AXES.items()}
    shape={"repairs":[{
        "parent_id":"...",
        "attack":"single strongest scientific objection, stated concretely",
        "attack_class":"CLOSEST_WORK|MATURE_REDUCTION|UNDERFORMED|MEASUREMENT|SUPPORT|PROTOCOL|OTHER",
        "children":[{
            "repair_axis":"change exactly one scientific axis",
            "title":"...","problem_seed":"...","scientific_tension":"...","problem_family":"...","structural_signature":"...","agent_specific_constraint":"...",
            "paperability_axes":{axis:{"status":"SUPPORTED|PLAUSIBLE|OPEN|REDUCED|NOT_CLAIMED","rationale":"..."} for axis in PAPERABILITY_AXES},
            "why_attack_no_longer_applies":"...","scores":{"importance":75,"specificity":75,"seed_distance":75,"evidence_grounding":75}
        }]
    }]}
    return (
        "EVOLUTIONARY REVIEW stage for a scientific Idea portfolio. This is NOT the final semantic/reduction reviewer and has zero scientific authority. "
        "For each parent, first ATTACK it with the single strongest concrete objection, then REPAIR/SPLIT it into materially different child problems instead of issuing a terminal rejection. "
        f"Return exactly {children_per_parent} repair children per parent when possible. Each child must change exactly one scientific axis (object, mechanism, decision, measurement, regime, information set, or intervention) while inheriting the parent's grounded evidence and lane contract. "
        "Do not evade an objection by wording changes, a new dataset name, or a generic domain transfer. Do not claim an exact mature reduction is defeated without evidence. A possible principle reduction closes only the P axis; it does NOT by itself close method-boundary, empirical-phenomenon, benchmark/evaluation, theory/guarantee, or system/capability paperability. "
        "This stage cannot certify PRINCIPLE_STOP or persistent dead-end. If the attack looks fatal, produce children that explicitly move to a different paperability axis or return no child only when the object is malformed/provenance-invalid. "
        f"Paperability axes are {json.dumps(axes,ensure_ascii=False,separators=(',',':'))}; they are search coordinates only and grant zero Method/Experiment/P0/GPU authority. "
        f"PARENTS={json.dumps(compact,ensure_ascii=False,separators=(',',':'))}. Return JSON only: {json.dumps(shape,ensure_ascii=False,separators=(',',':'))}"
    )

def _closest_work_candidates(branch,registry,limit=5):
    excluded=set(_source_refs(branch));scored=[]
    for ref,record in registry.items():
        if ref in excluded:continue
        work={"title":record.get("title") or "","problem_seed":record.get("abstract") or "","scientific_tension":" ".join(str(f.get("text") or "") for f in (record.get("empirical_facts") or [])[:3] if isinstance(f,dict)),"problem_family":"","agent_specific_constraint":"","structural_signature":""}
        sim=_jaccard(branch,work);scored.append((sim,ref,record))
    return [{"ref":ref,"title":str(record.get("title") or ""),"primary_url":str(record.get("primary_url") or ""),"source_sha256":str(record.get("source_sha256") or ""),"abstract_excerpt":str(record.get("abstract") or "")[:800],"lexical_structural_similarity":round(sim,4),"distance":round(1.0-sim,4)} for sim,ref,record in sorted(scored,key=lambda x:(x[0],x[1]),reverse=True)[:limit]]

def _formulation_prompt(branches,registry,dead_end_memory=None):
    compact=[]
    for b in branches:
        compact.append({**{k:b.get(k) for k in ("seed_id","parent_id","branch_depth","discovery_lane","title","problem_seed","scientific_tension","problem_family","structural_signature","agent_specific_constraint","empirical_evidence","lane_evidence","cross_domain_origin")},"closest_work_candidates":_closest_work_candidates(b,registry)})
    refs=sorted({ref for b in branches for ref in _source_refs(b) if ref in registry})
    evidence={ref:{"title":registry[ref].get("title"),"abstract":str(registry[ref].get("abstract") or "")[:1600],"facts":[str(f.get("text") or "")[:400] for f in (registry[ref].get("empirical_facts") or [])[:4] if isinstance(f,dict)],"typed_evidence":{k:[str(f.get("text") or "")[:400] for f in ((registry[ref].get("typed_evidence") or {}).get(k) or [])[:2] if isinstance(f,dict)] for k in ("operational_assumptions","measured_failures","boundary_observations")}} for ref in refs}
    shape={"candidates":[{
        "candidate_id":"PORT-1","source_branch_id":"...","title":"...","discovery_lane":"...","empirical_evidence":{"source_a":{"ref":"arXiv:...","claim":"...","evidence_role":"..."},"source_b":{"ref":"arXiv:...","claim":"...","evidence_role":"..."},"relation":"..."},"lane_evidence":{},
        "irreducible_object":"precise scientific problem/object","novelty_category":"problem-formulation|identification|method-boundary|mechanism|failure-regime|protocol|representation|causal-decomposition|phenomenon",
        "paperability_axes":{axis:{"status":"SUPPORTED|PLAUSIBLE|OPEN|REDUCED|NOT_CLAIMED","rationale":"why this exact paper contribution axis survives or does not"} for axis in PAPERABILITY_AXES},
        "paperability_claim":"which surviving axis makes a cheap falsifier worth running; zero downstream authority",
        "closest_work":{"ref":"arXiv:...","title":"...","shared_structure":"...","distinguishing_gap":"...","search_scope":"fresh-verified-primary-pool"},"closest_work_distance":0.0,
        "mature_theory_baselines":[{"name":"...","same_information_projection":"...","ex_ante_prediction":"...","distinguishing_prediction":"...","cannot_express":"...","reduction_class":"SOFT_COLLISION|NEEDS_EXACT_REDUCTION_TEST|TOO_GENERIC_TO_VETO|VALID_HARD_VETO","exact_reduction_test":"..."}],
        "reduction_falsifiability_contract":{"same_observable_information_checked":True,"ex_ante_exact_prediction_checked":True,"distinguishing_prediction_checked":True,"scope_boundary_checked":True,"all_exact_reduction_tests_resolved":True},
        "same_information_nonreducibility":{"claim":"...","why_each_baseline_cannot_express_prediction":"..."},"exact_prediction":"...","strongest_same_information_baseline":"...","domain_transfer_audit":{"mature_source_domain":"...","mature_object":"...","agent_specific_structural_constraint":"...","why_not_domain_transfer":"..."},
        "saturation_scan":{"checked":True,"matched_patterns":[],"pending_patterns":[],"rejected_patterns":[{"key":"known-key","reason":"why broad similarity does not establish exact reduction"}]},"cheapest_problem_falsifier":"...","endpoint_headroom_requirement":"...","importance":"...","likely_iclr_story":"..."
    }],"rejected":[{"source_branch_id":"...","reason":"...","matched_mature_theory":"...","reduction_class":"VALID_HARD_VETO|NEEDS_EXACT_REDUCTION_TEST|CLOSEST_WORK_COLLISION|UNDERFORMED","exact_reduction_test":"..."}],"notes":"..."}
    return (
        "FORMULATION stage after breadth search and evolutionary attack/repair. Convert genuinely promising branches into concrete paper-problem candidates, but do not confuse a provisional pre-F0 route with final scientific clearance. "
        "The ICLR novelty bar is high but does NOT require a new scientific ontology: acceptable novelty includes a genuinely new problem formulation, identification result, method boundary, theoretically grounded mechanism, measurable failure regime, enabling protocol/representation, causal decomposition with nontrivial prediction, or strong empirical phenomenon. "
        "Domain transfer, renaming, metric/benchmark/taxonomy-only novelty, or simple composition of occupied atoms is not novelty. "
        "Assess paperability on six independent axes P/M/E/B/T/S. A mature theory may reduce the P (principle/problem-formulation) axis without automatically erasing a genuinely different Method/Method-boundary, Empirical phenomenon, Benchmark/evaluation, Theory/guarantee, or System/capability contribution. Conversely, a surviving non-P axis must be concrete and testable; it cannot be a relabeling escape. Paperability axes are search/triage coordinates only and grant zero Method/Experiment/P0/GPU authority. "
        "A mature theory can HARD-VETO a claimed axis only under the Reduction Falsifiability Contract: same observable information, an ex-ante exact candidate-level prediction, a testable distinguishing/reduction prediction, and explicit scope boundary. A generic label such as CATE, dynamical systems, transfer, continual learning, nonmonotonicity, or information theory is not itself a veto. "
        "Use matched_patterns ONLY for a proven exact hard reduction. Use pending_patterns only when an exact reduction test is genuinely unresolved AND the branch is otherwise complete enough for a concrete problem-falsifier preflight; never set all_exact_reduction_tests_resolved=true while any pending pattern or NEEDS_EXACT_REDUCTION_TEST baseline remains. Use rejected_patterns when a broad ledger pattern was considered and the supplied frozen evidence is sufficient to show it cannot exactly reduce the candidate. "
        "Do not manufacture a reduction resolution from absence of evidence. If an unresolved exact reduction is the only remaining blocker, OR if P is reduced but at least one distinct non-P paperability axis remains concrete, keep the full problem object, paperability_axes, exact prediction, strongest same-information baseline, and cheapest falsifier concrete. The deterministic compiler may route it to a zero-authority pre-F0 evidence-acquisition hold before final exact reduction. This is not a Problem-Gate pass. If the branch also lacks lane grounding, provenance, a testable surviving axis, domain-transfer separation, or a concrete falsifier, return it in rejected. "
        "Inspect branch-local closest_work_candidates. A duplicate/collision or VALID_HARD_VETO branch must be returned in rejected rather than silently omitted. If a branch follows a certified scoped closed-basin inversion prior, explicitly verify that fresh primary evidence grounds the opposite principle and that the formulation satisfies the recorded reopen condition; otherwise reject or hold it rather than rewarding inversion wording. Preserve closure_layer/failure_layer exactly: problem_novelty is an upstream literature/theory stop, scientific closures use only execution, experiment_identifiability, optimization, operationalization, method_realization, assumption_scope, or core_principle, and only core_principle may enter persistent scientific dead-end memory or update the scoped principle. Broader benchmark/phenomenon falsification remains a separate field. When first-party code directly determines the dependency graph, the graph fact itself is not an identifiability contribution: require a downstream decision/utility/regret consequence and explicitly test generic distribution-shift, stale-supervisor, online-adaptation, or alternating-optimization reductions before keeping the branch. If a branch follows a POSITIVE_RESIDUAL_ASSET, require one prospective pre-outcome prediction that jointly explains the surviving phenomenon and every named failed mechanism; reject endpoint-leaking features, post-hoc full-trajectory geometry, or a renamed K-step mediator unless independent pre-outcome evidence distinguishes it from the failed first-action mechanism. "
        "Prefer a residual whose cheapest falsifier is an actual controlled comparison we can materialize quickly from released units, first-party code, or an existing provenance-audited substrate. Cheap falsification may precede final exact reduction only as zero-authority evidence acquisition; after a positive residual, the exact same-information reduction must be rerun before live Problem Gate/Paper Design eligibility. Do not claim support exists unless the supplied evidence establishes it; missing support is SUPPORT_STOP/HOLD, never a scientific negative. "
        "Preserve the inherited typed evidence/lane contract and source refs. "
        f"BRANCHES={json.dumps(compact,ensure_ascii=False,separators=(',',':'))}. SEARCH_CLOSURE_MEMORY={json.dumps(_prompt_dead_end_memory(dead_end_memory),ensure_ascii=False,separators=(',',':'))}. CLOSED_BASIN_INVERSION_PRIORS={json.dumps(_opposite_search_priors(dead_end_memory),ensure_ascii=False,separators=(',',':'))}. POSITIVE_RESIDUAL_PRIORS={json.dumps(_positive_residual_priors(dead_end_memory),ensure_ascii=False,separators=(',',':'))}. PRIMARY_EVIDENCE={json.dumps(evidence,ensure_ascii=False,separators=(',',':'))}. REDUCTION_LEDGER={json.dumps(reduction_pattern_audit(),ensure_ascii=False,separators=(',',':'))}. "
        f"Return JSON only: {json.dumps(shape,ensure_ascii=False,separators=(',',':'))}"
    )

def run_search_portfolio(*,records:list[dict[str,Any]],call:PortfolioCaller,model:str,target_raw_seeds:int=DEFAULT_RAW_SEEDS,archive_capacity:int=DEFAULT_ARCHIVE_CAPACITY,evolution_parents:int=DEFAULT_EVOLUTION_PARENTS,second_generation:int=DEFAULT_SECOND_GENERATION,repair_parents:int=DEFAULT_REPAIR_PARENTS,repair_children_per_parent:int=DEFAULT_REPAIR_CHILDREN_PER_PARENT,formulation_budget:int=DEFAULT_FORMULATION_BUDGET,max_parallel_calls:int=DEFAULT_MAX_PARALLEL_CALLS,dead_end_memory:dict[str,Any]|None=None)->dict[str,Any]:
    effective_records=list(_search_asset_records(dead_end_memory))+list(records);reg={str(r.get("ref")):r for r in effective_records if isinstance(r,dict) and r.get("ref")};per_lane=max(1,int(math.ceil(target_raw_seeds/max(1,len(SEARCH_PORTFOLIO_PRIMITIVES)))))
    raw=[];errors=[];calls=0
    def expand_one(lane,part,count):
        res=call(role=f"expand-{lane.lower()}-p{part}",prompt=_expansion_prompt(lane,records,count,dead_end_memory),model=preferred_model("portfolio_expand",model),max_output_tokens=5200);payload=extract_json_object(str(res.get("text") or ""));seeds=payload.get("seeds") or []
        if not isinstance(seeds,list):raise ValueError("seeds-must-be-array")
        out=[]
        for i,item in enumerate(seeds[:count],1):
            if not isinstance(item,dict):continue
            row=_normalize_seed(item,lane,i);row["seed_id"]=f"{lane}-P{part}-{i:03d}"
            if _valid_seed(row,reg):out.append(row)
        return out
    expansion_jobs=[]
    for lane in SEARCH_PORTFOLIO_PRIMITIVES:
        remaining=per_lane;part=1
        while remaining>0:
            count=min(DEFAULT_EXPANSION_SHARD_SIZE,remaining);expansion_jobs.append((lane,part,count));remaining-=count;part+=1
    with ThreadPoolExecutor(max_workers=min(max_parallel_calls,len(expansion_jobs))) as ex:
        jobs={ex.submit(expand_one,*job):f"{job[0]}-p{job[1]}" for job in expansion_jobs}
        for fut in as_completed(jobs):
            try:raw.extend(fut.result());calls+=1
            except Exception as exc:errors.append(f"expand:{jobs[fut]}:{type(exc).__name__}:{str(exc)[:180]}")

    unique,dups=_semantic_dedup(raw);unique,cluster_count=_assign_structural_clusters(unique);archives=_archives(unique,archive_capacity);by_id={r["seed_id"]:r for r in unique};breadth=[by_id[x] for x in archives["breadth"] if x in by_id]
    parents=_maxmin_select(breadth,min(evolution_parents,len(breadth)));evolved=[]
    def evolve_one(batch,generation,label):
        res=call(role=label,prompt=_evolution_prompt(batch,generation),model=preferred_model("portfolio_evolve",model),max_output_tokens=6200);children=extract_json_object(str(res.get("text") or "")).get("children") or []
        if not isinstance(children,list):raise ValueError("children-must-be-array")
        pmap={p["seed_id"]:p for p in batch};out=[]
        for i,ch in enumerate(children,1):
            if not isinstance(ch,dict):continue
            parent=pmap.get(str(ch.get("parent_id") or ""))
            if not parent:continue
            merged={**parent,**ch,"empirical_evidence":parent["empirical_evidence"],"lane_evidence":parent["lane_evidence"],"discovery_lane":parent["discovery_lane"],"cross_domain_origin":parent.get("cross_domain_origin","")}
            row=_normalize_seed(merged,parent["discovery_lane"],i);row["seed_id"]=f"{parent['seed_id']}-G{generation}";row["parent_id"]=parent["seed_id"];row["branch_depth"]=generation
            if _valid_seed(row,reg):out.append(row)
        return out
    g1=[(parents[i:i+8],1,f"evolve-g1-{i//8+1}") for i in range(0,len(parents),8) if parents[i:i+8]]
    with ThreadPoolExecutor(max_workers=min(max_parallel_calls,max(1,len(g1)))) as ex:
        jobs={ex.submit(evolve_one,*job):job[2] for job in g1}
        for fut in as_completed(jobs):
            try:evolved.extend(fut.result());calls+=1
            except Exception as exc:errors.append(f"{jobs[fut]}:{type(exc).__name__}:{str(exc)[:180]}")
    g2_parents=_maxmin_select(evolved,min(second_generation,len(evolved)))
    g2=[(g2_parents[i:i+6],2,f"evolve-g2-{i//6+1}") for i in range(0,len(g2_parents),6) if g2_parents[i:i+6]]
    with ThreadPoolExecutor(max_workers=min(max_parallel_calls,max(1,len(g2)))) as ex:
        jobs={ex.submit(evolve_one,*job):job[2] for job in g2}
        for fut in as_completed(jobs):
            try:evolved.extend(fut.result());calls+=1
            except Exception as exc:errors.append(f"{jobs[fut]}:{type(exc).__name__}:{str(exc)[:180]}")

    # Evolutionary reviewer: attack each selected branch, then repair/split it.
    # This stage is deliberately non-terminal and has zero scientific authority.
    repair_parent_rows=_maxmin_select(evolved+parents,min(repair_parents,len(evolved)+len(parents)));repaired=[];repair_attacks=[]
    def repair_one(batch,label):
        res=call(role=label,prompt=_attack_repair_prompt(batch,repair_children_per_parent),model=preferred_model("portfolio_evolve",model),max_output_tokens=7000);payload=extract_json_object(str(res.get("text") or ""));groups=payload.get("repairs") or []
        if not isinstance(groups,list):raise ValueError("repairs-must-be-array")
        pmap={p["seed_id"]:p for p in batch};out=[];attacks=[]
        for group in groups:
            if not isinstance(group,dict):continue
            parent=pmap.get(str(group.get("parent_id") or ""))
            if not parent:continue
            attack=" ".join(str(group.get("attack") or "").split())[:900];attack_class=str(group.get("attack_class") or "OTHER").strip().upper();children=group.get("children") or []
            if not isinstance(children,list):continue
            attacks.append({"parent_id":parent["seed_id"],"attack":attack,"attack_class":attack_class,"scientific_authority":False})
            for child_index,ch in enumerate(children[:repair_children_per_parent],1):
                if not isinstance(ch,dict):continue
                merged={**parent,**ch,"empirical_evidence":parent["empirical_evidence"],"lane_evidence":parent["lane_evidence"],"discovery_lane":parent["discovery_lane"],"cross_domain_origin":parent.get("cross_domain_origin","")}
                row=_normalize_seed(merged,parent["discovery_lane"],child_index);row["seed_id"]=f"{parent['seed_id']}-R{child_index}";row["parent_id"]=parent["seed_id"];row["branch_depth"]=int(parent.get("branch_depth") or 0)+1
                row["reviewer_attack"]=attack;row["reviewer_attack_class"]=attack_class;row["repair_axis"]=" ".join(str(ch.get("repair_axis") or "").split())[:500];row["why_attack_no_longer_applies"]=" ".join(str(ch.get("why_attack_no_longer_applies") or "").split())[:900];row["paperability_axes"]=_normalize_paperability_axes(ch.get("paperability_axes"));row["paperability_survives"]=_paperability_survives(row["paperability_axes"])
                if _valid_seed(row,reg) and row["paperability_survives"]:out.append(row)
        return out,attacks
    r_jobs=[(repair_parent_rows[i:i+4],f"repair-{i//4+1}") for i in range(0,len(repair_parent_rows),4) if repair_parent_rows[i:i+4]]
    with ThreadPoolExecutor(max_workers=min(max_parallel_calls,max(1,len(r_jobs)))) as ex:
        jobs={ex.submit(repair_one,*job):job[1] for job in r_jobs}
        for fut in as_completed(jobs):
            try:
                children,attacks=fut.result();repaired.extend(children);repair_attacks.extend(attacks);calls+=1
            except Exception as exc:errors.append(f"{jobs[fut]}:{type(exc).__name__}:{str(exc)[:180]}")

    formulation_source=repaired+evolved+parents
    formulation_pool=_maxmin_select(formulation_source,min(formulation_budget,len(formulation_source)),required_ids=[row["seed_id"] for row in repaired[:min(len(repaired),formulation_budget)]]);formulated=[];rejected=[]
    def formulate_one(batch,label):
        res=call(role=label,prompt=_formulation_prompt(batch,reg,dead_end_memory),model=preferred_model("portfolio_formulate",model),max_output_tokens=5600);payload=extract_json_object(str(res.get("text") or ""));live=payload.get("candidates") or [];dead=payload.get("rejected") or []
        if not isinstance(live,list) or not isinstance(dead,list):raise ValueError("formulation-arrays-invalid")
        parents={row["seed_id"]:row for row in batch};normalized=[];local_dead=[x for x in dead if isinstance(x,dict)]
        for item in live:
            if not isinstance(item,dict):continue
            parent=parents.get(str(item.get("source_branch_id") or ""))
            if not parent:continue
            row=dict(item);row["source_branch_id"]=parent["seed_id"];row["branch_depth"]=parent.get("branch_depth",0);row["discovery_lane"]=parent["discovery_lane"];row["empirical_evidence"]=parent["empirical_evidence"];row["lane_evidence"]=parent["lane_evidence"]
            row["paperability_axes"]=_normalize_paperability_axes(item.get("paperability_axes") or parent.get("paperability_axes"));row["paperability_survives"]=_paperability_survives(row["paperability_axes"]);row["reviewer_attack"]=parent.get("reviewer_attack") or "";row["reviewer_attack_class"]=parent.get("reviewer_attack_class") or "";row["repair_axis"]=parent.get("repair_axis") or "";row["why_attack_no_longer_applies"]=parent.get("why_attack_no_longer_applies") or ""
            if row["paperability_survives"]:normalized.append(row)
            else:local_dead.append({"source_branch_id":parent["seed_id"],"reason":"no concrete SUPPORTED/PLAUSIBLE paperability axis survived formulation","reduction_class":"UNDERFORMED","scientific_authority":False})
        return normalized,local_dead
    f_jobs=[(formulation_pool[i:i+2],f"formulate-{i//2+1}") for i in range(0,len(formulation_pool),2) if formulation_pool[i:i+2]]
    with ThreadPoolExecutor(max_workers=min(2,max(1,len(f_jobs)))) as ex:
        jobs={ex.submit(formulate_one,*job):job[1] for job in f_jobs}
        for fut in as_completed(jobs):
            try:
                live,dead=fut.result();formulated.extend(live);rejected.extend(dead);calls+=1
            except Exception as exc:errors.append(f"{jobs[fut]}:{type(exc).__name__}:{str(exc)[:180]}")

    for index,row in enumerate(formulated,1):row["candidate_id"]=f"PORT-{index:03d}"
    lane_counts=Counter(r["discovery_lane"] for r in raw);archive_lanes=Counter(by_id[x]["discovery_lane"] for x in archives["breadth"] if x in by_id);family_counts=Counter(r["problem_family"] for r in unique)
    sample=[by_id[x] for x in archives["breadth"] if x in by_id];dist=[1-_jaccard(sample[i],sample[j]) for i in range(len(sample)) for j in range(i+1,len(sample))]
    axis_coverage={axis:sum((row.get("paperability_axes") or {}).get(axis,{}).get("status") in {"SUPPORTED","PLAUSIBLE"} for row in formulated) for axis in PAPERABILITY_AXES}
    return {
        "schema_version":"3.0-double-funnel","policy":{"expansion_precedes_reduction":True,"parallel_breadth_search":True,"max_parallel_calls":max_parallel_calls,"contradiction_is_one_lane_not_required":True,"low_score_high_diversity_branches_can_survive_expansion":True,"attack_repair_split_before_formulation":True,"reviewer_objection_is_evolution_input_not_terminal_stop":True,"paperability_axes":dict(PAPERABILITY_AXES),"principle_reduction_does_not_auto_close_other_paperability_axes":True,"cheap_problem_falsifier_may_precede_final_exact_reduction":True,"pre_f0_route_has_zero_scientific_authority":True,"exact_reduction_still_required_before_final_problem_gate":True,"mature_theory_veto_delayed_until_formulation":True,"cross_domain_analogy_is_search_primitive_not_novelty":True,"scientific_authority":False},
        "config":{"requested_raw_seeds":target_raw_seeds,"per_lane":per_lane,"expansion_shard_size":DEFAULT_EXPANSION_SHARD_SIZE,"archive_capacity":archive_capacity,"evolution_parents":evolution_parents,"second_generation":second_generation,"repair_parents":repair_parents,"repair_children_per_parent":repair_children_per_parent,"formulation_budget":formulation_budget,"max_parallel_calls":max_parallel_calls},
        "summary":{"raw_seeds":len(raw),"semantic_unique":len(unique),"duplicate_or_near_duplicate":len(dups),"structural_clusters":cluster_count,"unique_problem_families":cluster_count,"model_named_problem_families":len(family_counts),"archive_lane_coverage":len(archive_lanes),"breadth_archive":len(archives["breadth"]),"evolved_branches":len(evolved),"max_branch_depth":max([r.get("branch_depth",0) for r in evolved+repaired] or [0]),"reviewer_attacks":len(repair_attacks),"repair_children":len(repaired),"paperability_axis_coverage":axis_coverage,"formulated_candidates":len(formulated),"formulation_rejected":len(rejected),"portfolio_calls":calls,"mean_archive_pairwise_distance":round(sum(dist)/len(dist),4) if dist else 0.0,"errors":len(errors)},
        "lane_counts":dict(sorted(lane_counts.items())),"archive_lane_counts":dict(sorted(archive_lanes.items())),"family_counts":dict(family_counts.most_common()),"archives":archives,"duplicate_log":dups[:200],"errors":errors,"raw_seeds":raw,"unique_seeds":unique,"evolved":evolved,"repair_attacks":repair_attacks,"repaired":repaired,"formulated_candidates":formulated,"formulation_rejections":rejected,"scientific_authority":False,
    }
