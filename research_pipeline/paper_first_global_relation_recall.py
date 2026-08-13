from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .ark_provider import ArkResponsesClient, ArkSettings, extract_json_object
from .config import PROJECT_ROOT, StorageSettings
from .paper_first_fresh_saturation import REDUCTION_PATTERNS
from .paper_first_primary_evidence import load_primary_evidence_state
from .paper_first_problem_discovery_contract import (
    DISCOVERY_LANES,
    LANE_DISTINCT_SOURCE_MINIMUM,
    LANE_EVIDENCE_REQUIRED,
    LANE_MACHINE_CONTRACTS,
    LANE_SOURCE_ROLES,
)
from .paper_first_problem_generator import load_problem_generator_state
from .paper_first_relation_coverage import coobserved_pairs, portable_review_receipts, source_pair_coverage
from .paper_first_scientific_object_ontology import current_lane_axes, reviewed_primary_cache_records
from .public_state_redaction import redact_private_paths

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-global-relation-recall.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-global-relation-recall.js"
RELATION_MODEL = "ark-code-latest"
LANE_REVIEW_MODEL = "glm-5.2"
REDUCTION_MODEL = "deepseek-v4-flash"
PAIR_RELATION_BUDGETS = {
    "CONTRADICTION": 5,
    "CONVERGENT_FAILURE": 5,
    "ASSUMPTION_BREAK": 5,
    "UNEXPLAINED_BOUNDARY": 5,
    "IDENTIFIABILITY_GAP": 2,
    "MISSING_DECISION_OBJECT": 2,
    "COMPOSITION_INTERACTION": 2,
    "CROSS_DOMAIN_STRUCTURAL_ANALOGY": 2,
    "NEW_CAPABILITY_QUESTION": 2,
    "LONGITUDINAL_EMERGENCE": 2,
}
MAX_TOTAL_PROPOSALS = sum(PAIR_RELATION_BUDGETS.values())
Responder = Callable[..., dict[str, Any]]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _root(storage: StorageSettings) -> Path:
    return storage.data_root / "paper-first-problem-discovery" / "global-relation-recall"


def _ark(*, prompt: str, model: str, max_output_tokens: int) -> dict[str, Any]:
    settings = ArkSettings.from_env(required=False)
    if not settings.api_key:
        raise RuntimeError("ARK_API_KEY_NOT_CONFIGURED")
    settings = ArkSettings(api_key=settings.api_key, base_url=settings.base_url, default_model=settings.default_model, timeout_seconds=min(max(settings.timeout_seconds, 90.0), 180.0), max_retries=0)
    return ArkResponsesClient(settings).respond(prompt, model=model, max_output_tokens=max_output_tokens, temperature=0.0, thinking="disabled")


def _write_raw(storage: StorageSettings, run_id: str, role: str, model: str, text: str) -> dict[str, Any]:
    root = _root(storage) / "raw"; root.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest(); path = root / f"{run_id}-{role}-{model.replace('/', '-')}-{digest[:12]}.txt"
    path.write_text(text, encoding="utf-8")
    return {"path": str(path), "sha256": digest, "requested_model": model}


def _receipts(generator: dict[str, Any]) -> list[dict[str, Any]]:
    return portable_review_receipts(generator)


def _target_refs(receipts: list[dict[str, Any]]) -> set[str]:
    return {str(ref) for row in receipts for ref in row.get("source_refs") or [] if str(ref).startswith("arXiv:")}


def _coobserved(receipts: list[dict[str, Any]]) -> set[tuple[str,str]]:
    return coobserved_pairs(receipts)


def _card(record: dict[str, Any]) -> dict[str, Any]:
    typed=record.get("typed_evidence") or {};axes=current_lane_axes(record.get("lane_keys") or [])
    return {"ref":record.get("ref"),"title":record.get("title"),"object":axes.get("object") or [],"context":axes.get("context") or [],"property":axes.get("property") or [],"empirical":[str(x.get("text") or "")[:320] for x in (record.get("empirical_facts") or [])[:2] if isinstance(x,dict)],"assumption":[str(x.get("text") or "")[:320] for x in (typed.get("operational_assumptions") or [])[:1] if isinstance(x,dict)],"failure":[str(x.get("text") or "")[:320] for x in (typed.get("measured_failures") or [])[:1] if isinstance(x,dict)],"boundary":[str(x.get("text") or "")[:320] for x in (typed.get("boundary_observations") or [])[:1] if isinstance(x,dict)]}


def _lane_contracts() -> list[dict[str, Any]]:
    return [
        {
            "lane": lane,
            "pair_budget": PAIR_RELATION_BUDGETS[lane],
            "source_roles": list(LANE_SOURCE_ROLES[lane]),
            "minimum_distinct_primary_sources": int(LANE_DISTINCT_SOURCE_MINIMUM[lane]),
            "required_lane_evidence": list(LANE_EVIDENCE_REQUIRED[lane]),
            "machine_contract": LANE_MACHINE_CONTRACTS[lane],
        }
        for lane in DISCOVERY_LANES
    ]


def relation_prompt(cards: list[dict[str, Any]]) -> str:
    shape = {
        "lanes": {
            lane: [{"source_a":"arXiv:...","source_b":"arXiv:...","relation":"...","why_lane":"...","missing_piece":""}]
            for lane in DISCOVERY_LANES
        },
        "diagnosis":"...",
    }
    return (
        "ZERO-AUTHORITY GLOBAL CROSS-SOURCE RELATION RECALL for an ICLR paper-problem search portfolio. "
        "Never propose a method, paper idea, novelty verdict, Problem-Gate verdict, or downstream action. "
        "The ordinary Search Portfolio already handles single-source phenomena; this pass exists only to recover cross-source pairs that may never have co-occurred in one tranche. "
        "Search ALL supplied primary-evidence cards. A pair may cross scientific-object/context tags; tags are ranking context, never a hard veto. "
        "For each lane return at most its pair_budget proposals, fewer or zero is valid. Do not invent shared measurements, conditions, assumptions, or failures. "
        "Use two DISTINCT primary refs for every proposal even when the lane's ordinary minimum is one, because this layer is specifically a cross-source recall supplement. "
        "LANE CONTRACTS="+json.dumps(_lane_contracts(),ensure_ascii=False,separators=(",",":"))+
        " RETURN JSON ONLY="+json.dumps(shape,ensure_ascii=False,separators=(",",":"))+
        " CARDS="+json.dumps(cards,ensure_ascii=False,separators=(",",":"))
    )


def lane_prompt(proposals: list[dict[str, Any]], cards: list[dict[str, Any]]) -> str:
    return (
        "Independent STRICT lane-contract reviewer; zero scientific authority. Do not judge novelty or mature-theory reduction. "
        "Review every cross-source proposal exactly once against the frozen lane contract. A PASS requires the supplied primary evidence to instantiate the machine contract; thematic similarity is insufficient. "
        "For lanes whose ordinary minimum is one source, this cross-source proposal may still PASS only if the TWO supplied sources jointly support the stated relation; do not reward it merely because a single-source version could exist. "
        "Return JSON only {\"reviews\":[{\"proposal_id\":\"REL-...\",\"verdict\":\"PASS|FAIL\",\"reason\":\"...\",\"missing\":\"\"}],\"diagnosis\":\"...\"}. "
        "LANE CONTRACTS="+json.dumps(_lane_contracts(),ensure_ascii=False,separators=(",",":"))+
        " PROPOSALS="+json.dumps(proposals,ensure_ascii=False,separators=(",",":"))+
        " CARDS="+json.dumps(cards,ensure_ascii=False,separators=(",",":"))
    )


def reduction_prompt(proposals: list[dict[str, Any]], cards: list[dict[str, Any]]) -> str:
    ledger=[{"key":x["key"],"mature_theories":x["mature_theories"],"veto":x["veto"]} for x in REDUCTION_PATTERNS]
    return "Independent STRICT same-information reduction reviewer; zero authority. These pairs already passed lane review. Infer the narrowest falsifiable prediction and test whether the exact same information is already expressible by the supplied negative-space ledger or mature theory. Domain transfer/renaming or ordinary mature objects are REDUCIBLE. NOT_REDUCED requires a concrete residual prediction. Review every proposal once. matched_patterns may use exact ledger keys only. Return JSON only {\"reviews\":[{\"proposal_id\":\"REL-...\",\"verdict\":\"REDUCIBLE|NOT_REDUCED\",\"exact_prediction\":\"...\",\"matched_patterns\":[],\"strongest_reduction\":\"...\",\"residual_prediction\":\"\"}],\"diagnosis\":\"...\"}. PROPOSALS="+json.dumps(proposals,ensure_ascii=False,separators=(",",":"))+" CARDS="+json.dumps(cards,ensure_ascii=False,separators=(",",":"))+" LEDGER="+json.dumps(ledger,ensure_ascii=False,separators=(",",":"))


def _normalize_proposals(payload: dict[str, Any], registry: dict[str, dict[str, Any]], coobserved: set[tuple[str,str]]) -> list[dict[str, Any]]:
    lanes=payload.get("lanes") or {};out=[];seen=set()
    for lane in DISCOVERY_LANES:
        rows=lanes.get(lane) or []
        if not isinstance(rows,list) or len(rows)>PAIR_RELATION_BUDGETS[lane]: raise ValueError(f"relation-proposals-invalid:{lane}")
        idx=0
        for raw in rows:
            if not isinstance(raw,dict): raise ValueError("relation-proposal-entry-invalid")
            a=str(raw.get("source_a") or "").strip();b=str(raw.get("source_b") or "").strip()
            if not a or not b or a not in registry or b not in registry: raise ValueError("relation-proposal-source-invalid")
            if a==b: continue
            pair=tuple(sorted((a,b)));sig=(lane,*pair)
            if sig in seen: continue
            relation=" ".join(str(raw.get("relation") or "").split())[:800];why=" ".join(str(raw.get("why_lane") or "").split())[:800]
            if not relation or not why: raise ValueError("relation-proposal-rationale-missing")
            idx+=1;seen.add(sig)
            out.append({"proposal_id":f"REL-{lane}-{idx}","lane":lane,"source_a":a,"source_b":b,"source_refs":[a,b],"relation":relation,"why_lane":why,"missing_piece":" ".join(str(raw.get("missing_piece") or "").split())[:500],"previously_coobserved":pair in coobserved,"scientific_authority":False})
    return out


def _normalize_lane_reviews(payload: dict[str, Any], proposals: list[dict[str, Any]]) -> dict[str,dict[str,Any]]:
    expected={x["proposal_id"] for x in proposals};out={}
    for raw in payload.get("reviews") or []:
        if not isinstance(raw,dict): continue
        pid=str(raw.get("proposal_id") or "");verdict=str(raw.get("verdict") or "").upper()
        if pid not in expected or pid in out or verdict not in {"PASS","FAIL"}: continue
        out[pid]={"verdict":verdict,"reason":" ".join(str(raw.get("reason") or "").split())[:1000],"missing":" ".join(str(raw.get("missing") or "").split())[:500],"scientific_authority":False}
    if set(out)!=expected: raise ValueError("lane-review-incomplete")
    return out


def _normalize_reductions(payload: dict[str, Any], proposals: list[dict[str, Any]]) -> dict[str,dict[str,Any]]:
    expected={x["proposal_id"] for x in proposals};known={x["key"] for x in REDUCTION_PATTERNS};out={}
    for raw in payload.get("reviews") or []:
        if not isinstance(raw,dict): continue
        pid=str(raw.get("proposal_id") or "");verdict=str(raw.get("verdict") or "").upper()
        if pid not in expected or pid in out or verdict not in {"REDUCIBLE","NOT_REDUCED"}: continue
        residual=" ".join(str(raw.get("residual_prediction") or "").split())[:1000]
        if verdict=="NOT_REDUCED" and not residual: verdict="REDUCIBLE"
        out[pid]={"verdict":verdict,"exact_prediction":" ".join(str(raw.get("exact_prediction") or "").split())[:1200],"matched_patterns":sorted({str(k) for k in raw.get("matched_patterns") or [] if str(k) in known}),"strongest_reduction":" ".join(str(raw.get("strongest_reduction") or "").split())[:1200],"residual_prediction":residual,"scientific_authority":False}
    if set(out)!=expected: raise ValueError("reduction-review-incomplete")
    return out


def _summary(coverage: dict[str,Any], target: set[str], cached: set[str], proposals: list[dict[str,Any]]) -> dict[str,Any]:
    passed=[x for x in proposals if (x.get("lane_review") or {}).get("verdict")=="PASS"]
    reducible=[x for x in passed if (x.get("reduction_review") or {}).get("verdict")=="REDUCIBLE"]
    residual=[x for x in passed if (x.get("reduction_review") or {}).get("verdict")=="NOT_REDUCED"]
    return {"reviewed_receipt_sources":int(coverage.get("reviewed_receipt_sources") or len(target)),"cached_reviewed_sources":len(cached & target),"cache_completeness_fraction":round(len(cached & target)/len(target),4) if target else 0.0,"possible_source_pairs":int(coverage.get("possible_source_pairs") or 0),"coobserved_source_pairs":int(coverage.get("coobserved_source_pairs") or 0),"pair_coverage_fraction":float(coverage.get("pair_coverage_fraction") or 0.0),"relation_blind_spot_detected":bool(coverage.get("relation_blind_spot_detected")),"relation_universe_digest":str(coverage.get("relation_universe_digest") or ""),"relation_proposals":len(proposals),"unseen_relation_proposals":sum(x.get("previously_coobserved") is False for x in proposals),"lane_pass":len(passed),"unseen_lane_pass":sum(x.get("previously_coobserved") is False for x in passed),"reduction_reviewed":sum(bool(x.get("reduction_review")) for x in passed),"reducible":len(reducible),"not_reduced":len(residual),"focused_problem_generator_reopen_required":bool(residual),"scientifically_authorized":0}


def run_global_relation_recall(*,storage:StorageSettings|None=None,primary_state:dict[str,Any]|None=None,generator_state:dict[str,Any]|None=None,cache_records:list[dict[str,Any]]|None=None,previous_state:dict[str,Any]|None=None,relation_responder:Responder|None=None,lane_responder:Responder|None=None,reduction_responder:Responder|None=None,now:datetime|None=None)->dict[str,Any]:
    storage=storage or StorageSettings.from_env();primary_state=primary_state or load_primary_evidence_state();generator_state=generator_state or load_problem_generator_state();run_id=(now or datetime.now(timezone.utc)).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    receipts=_receipts(generator_state);coverage=source_pair_coverage(receipts);target=_target_refs(receipts);cache_rows=cache_records if cache_records is not None else reviewed_primary_cache_records(storage);registry={str(x.get("ref")):x for x in cache_rows if x.get("ref")};cached=set(registry);previous_state=previous_state or load_global_relation_recall_state()
    state={"schema_version":"1.1","generated_at":_now(),"run_id":run_id,"status":"NOT_RUN","policy":{"scientific_authority":False,"source_coverage_exhaustion_is_not_relation_exhaustion":True,"full_reviewed_receipt_cache_required_before_global_scan":True,"relation_miner_is_search_control_only":True,"cross_source_recall_supplements_but_does_not_replace_search_portfolio":True,"single_source_lane_search_remains_search_portfolio_responsibility":True,"independent_lane_reviewer_required":True,"independent_reduction_reviewer_required":True,"all_lane_pass_proposals_require_reduction_review":True,"relation_universe_digest_prevents_repeat_model_calls":True,"same_relation_universe_reuses_portable_completed_scan":True,"pair_relation_budgets":dict(PAIR_RELATION_BUDGETS),"max_total_relation_proposals":MAX_TOTAL_PROPOSALS,"zero_proposals_is_valid":True,"not_reduced_only_reopens_focused_problem_generator":True,"automatic_problem_gate_authority":False,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},"models":{"relation":RELATION_MODEL,"lane_review":LANE_REVIEW_MODEL,"reduction":REDUCTION_MODEL},"relation_coverage":coverage,"raw_artifacts":{},"proposals":[],"last_completed_scan":{}}
    prior_scan=(previous_state.get("last_completed_scan") or {}) if isinstance(previous_state,dict) else {}
    prior_digest=str(prior_scan.get("relation_universe_digest") or "")
    if prior_digest and prior_digest==str(coverage.get("relation_universe_digest") or ""):
        prior_summary=dict(previous_state.get("summary") or {});prior_summary.update({"reviewed_receipt_sources":int(coverage.get("reviewed_receipt_sources") or len(target)),"cached_reviewed_sources":len(cached & target),"cache_completeness_fraction":round(len(cached & target)/len(target),4) if target else 0.0,"possible_source_pairs":int(coverage.get("possible_source_pairs") or 0),"coobserved_source_pairs":int(coverage.get("coobserved_source_pairs") or 0),"pair_coverage_fraction":float(coverage.get("pair_coverage_fraction") or 0.0)})
        state.update({"status":"SKIPPED_RELATION_UNIVERSE_UNCHANGED","summary":prior_summary,"proposals":[dict(row) for row in previous_state.get("proposals") or [] if isinstance(row,dict)],"last_completed_scan":dict(prior_scan)})
        return state
    ps=primary_state.get("summary") or {}
    if ps.get("source_coverage_exhausted") is not True:
        state["status"]="SKIPPED_SOURCE_COVERAGE_OPEN";state["summary"]=_summary(coverage,target,cached,[]);return state
    if not coverage.get("relation_blind_spot_detected"):
        state["status"]="SKIPPED_PAIR_COVERAGE_COMPLETE";state["summary"]=_summary(coverage,target,cached,[]);return state
    missing=sorted(target-cached)
    if missing:
        state["status"]="HOLD_RELATION_CACHE_INCOMPLETE";state["cache_missing_count"]=len(missing);state["cache_missing_ref_digest"]=hashlib.sha256("\n".join(missing).encode()).hexdigest();state["summary"]=_summary(coverage,target,cached,[]);return state
    cards=[_card(registry[ref]) for ref in sorted(target)]
    call=relation_responder or _ark
    try:
        response=call(prompt=relation_prompt(cards),model=RELATION_MODEL,max_output_tokens=5200);raw=str(response.get("text") or "");artifact=_write_raw(storage,run_id,"relation",RELATION_MODEL,raw);artifact["resolved_model"]=str(response.get("resolved_model") or RELATION_MODEL);state["raw_artifacts"]["relation"]=artifact;proposals=_normalize_proposals(extract_json_object(raw),registry,_coobserved(receipts))
    except Exception as error:
        state["status"]="RELATION_PROVIDER_ERROR_ZERO_AUTHORITY";state["error"]=f"{type(error).__name__}:{str(error)[:500]}";state["summary"]=_summary(coverage,target,cached,[]);return state
    if proposals:
        refs=sorted({ref for x in proposals for ref in x["source_refs"]});cards2=[_card(registry[ref]) for ref in refs];call=lane_responder or _ark
        try:
            response=call(prompt=lane_prompt(proposals,cards2),model=LANE_REVIEW_MODEL,max_output_tokens=6500);raw=str(response.get("text") or "");artifact=_write_raw(storage,run_id,"lane-review",LANE_REVIEW_MODEL,raw);artifact["resolved_model"]=str(response.get("resolved_model") or LANE_REVIEW_MODEL);state["raw_artifacts"]["lane_review"]=artifact
            if artifact["resolved_model"]==str((state["raw_artifacts"].get("relation") or {}).get("resolved_model") or ""): raise RuntimeError("relation-lane-reviewer-not-independent")
            reviews=_normalize_lane_reviews(extract_json_object(raw),proposals)
            for x in proposals:x["lane_review"]=reviews[x["proposal_id"]]
        except Exception as error:
            state["status"]="LANE_REVIEW_ERROR_ZERO_AUTHORITY";state["error"]=f"{type(error).__name__}:{str(error)[:500]}";state["proposals"]=proposals;state["summary"]=_summary(coverage,target,cached,proposals);return state
    passed=[x for x in proposals if (x.get("lane_review") or {}).get("verdict")=="PASS"]
    if passed:
        refs=sorted({ref for x in passed for ref in x["source_refs"]});cards3=[_card(registry[ref]) for ref in refs];call=reduction_responder or _ark
        try:
            response=call(prompt=reduction_prompt(passed,cards3),model=REDUCTION_MODEL,max_output_tokens=6000);raw=str(response.get("text") or "");artifact=_write_raw(storage,run_id,"reduction-review",REDUCTION_MODEL,raw);artifact["resolved_model"]=str(response.get("resolved_model") or REDUCTION_MODEL);state["raw_artifacts"]["reduction_review"]=artifact
            if artifact["resolved_model"]==str((state["raw_artifacts"].get("lane_review") or {}).get("resolved_model") or ""): raise RuntimeError("lane-reduction-reviewer-not-independent")
            reviews=_normalize_reductions(extract_json_object(raw),passed)
            for x in passed:x["reduction_review"]=reviews[x["proposal_id"]]
        except Exception as error:
            state["status"]="REDUCTION_REVIEW_ERROR_ZERO_AUTHORITY";state["error"]=f"{type(error).__name__}:{str(error)[:500]}";state["proposals"]=proposals;state["summary"]=_summary(coverage,target,cached,proposals);return state
    state["proposals"]=proposals;state["summary"]=_summary(coverage,target,cached,proposals);state["status"]="GLOBAL_RELATION_RECALL_COMPLETE"
    state["last_completed_scan"]={"run_id":run_id,"relation_universe_digest":str(coverage.get("relation_universe_digest") or ""),"relation_coverage":{"reviewed_receipt_sources":coverage.get("reviewed_receipt_sources",0),"possible_source_pairs":coverage.get("possible_source_pairs",0),"coobserved_source_pairs":coverage.get("coobserved_source_pairs",0),"pair_coverage_fraction":coverage.get("pair_coverage_fraction",0.0)},"summary":dict(state["summary"]),"models":dict(state["models"]),"scientific_authority":False}
    return state


def public_relation_recall_state(state:dict[str,Any],storage:StorageSettings|None=None)->dict[str,Any]:
    public=json.loads(json.dumps(state,ensure_ascii=False))
    for artifact in (public.get("raw_artifacts") or {}).values():
        if isinstance(artifact,dict):artifact.pop("path",None)
    compact=[]
    for row in public.get("proposals") or []:
        compact.append({"proposal_id":row.get("proposal_id"),"lane":row.get("lane"),"source_refs":row.get("source_refs") or [],"previously_coobserved":row.get("previously_coobserved") is True,"lane_verdict":(row.get("lane_review") or {}).get("verdict",""),"reduction_verdict":(row.get("reduction_review") or {}).get("verdict",""),"matched_patterns":(row.get("reduction_review") or {}).get("matched_patterns") or [],"focused_problem_generator_reopen_required":(row.get("reduction_review") or {}).get("verdict")=="NOT_REDUCED","scientific_authority":False})
    public["proposals"]=compact;public["scientific_authority"]=False
    return redact_private_paths(public,storage=storage or StorageSettings.from_env())


def write_global_relation_recall_state(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS,*,storage:StorageSettings|None=None,**kwargs:Any)->dict[str,Any]:
    storage=storage or StorageSettings.from_env();state=run_global_relation_recall(storage=storage,**kwargs)
    private=_root(storage);private.mkdir(parents=True,exist_ok=True);(private/"latest.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    public=public_relation_recall_state(state,storage);json_path.parent.mkdir(parents=True,exist_ok=True);json_path.write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");js_path.write_text("window.PAPER_FIRST_GLOBAL_RELATION_RECALL = "+json.dumps(public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state


def load_global_relation_recall_state(path:Path=DEFAULT_JSON)->dict[str,Any]:
    empty={"schema_version":"1.1","status":"NOT_RUN","policy":{"scientific_authority":False},"summary":{},"relation_coverage":{},"proposals":[],"last_completed_scan":{},"scientific_authority":False}
    if not path.exists():return empty
    try:payload=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):return {**empty,"status":"STATE_UNREADABLE"}
    return payload if isinstance(payload,dict) else {**empty,"status":"STATE_INVALID"}


if __name__=="__main__":print(json.dumps(write_global_relation_recall_state(),ensure_ascii=False,indent=2))
