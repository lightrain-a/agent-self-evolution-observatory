from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings, extract_json_object
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
from .paper_first_relation_coverage import coobserved_pairs, portable_review_receipts, relation_universe_digest, source_pair_coverage
from .paper_first_scientific_object_ontology import current_lane_axes, reviewed_primary_cache_records
from .public_state_redaction import redact_private_paths
from .premium_model_policy import preferred_model
from .relation_scan_boundary_manifest import boundary_receipts, load_relation_scan_boundary_manifest

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-global-relation-recall.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-global-relation-recall.js"
RELATION_MODEL = preferred_model("relation_mining")
LANE_REVIEW_MODEL = preferred_model("relation_lane_review")
REDUCTION_MODEL = preferred_model("relation_reduction_review")
LANE_REVIEW_EXECUTION_CONTRACT_VERSION = "relation-lane-review-sharded-glm-compatible-v3"
LANE_REVIEW_BATCH_SIZE = 6
LANE_REVIEW_MAX_OUTPUT_TOKENS = 15000
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
    settings = ArkSettings(api_key=settings.api_key, base_url=settings.base_url, default_model=settings.default_model, timeout_seconds=min(max(settings.timeout_seconds,90.0),180.0), max_retries=0)
    # GLM's Responses endpoint is provider-compatible only when the thinking profile
    # is left at provider default; forcing thinking=disabled can consume the whole
    # output budget without an auditable assistant message. Other premium families
    # keep deterministic disabled thinking for this reviewer pipeline.
    thinking=None if str(model).lower().startswith("glm") else "disabled"
    return ArkResponsesClient(settings).respond(prompt,model=model,max_output_tokens=max_output_tokens,temperature=0.0,thinking=thinking,allow_thinking_compatibility_fallback=True)


def _write_raw(storage: StorageSettings, run_id: str, role: str, model: str, text: str) -> dict[str, Any]:
    root = _root(storage) / "raw"; root.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest(); path = root / f"{run_id}-{role}-{model.replace('/', '-')}-{digest[:12]}.txt"
    path.write_text(text, encoding="utf-8")
    return {"path": str(path), "sha256": digest, "requested_model": model}


def _provider_error_text(error: Exception) -> str:
    """Return a bounded public-safe provider error without response identifiers."""
    if isinstance(error, ArkResponseStateError):
        return (
            "ArkResponseStateError:incomplete-before-assistant-output;"
            f"reason={error.incomplete_reason or 'unknown'};"
            f"requested_model={error.requested_model};resolved_model={error.resolved_model}"
        )[:500]
    text=f"{type(error).__name__}:{str(error)[:500]}"
    return re.sub(r"response_id=[^;\s]+[;\s]*", "", text)[:500]


def _repair_trailing_relation_root_closure(raw: str) -> tuple[dict[str, Any] | None, str]:
    """Repair only one missing final root-object brace without editing prior bytes."""
    text=str(raw or "")
    if not text or text[-1] != "}":
        return None, ""
    stack:list[str]=[];in_string=False;escaped=False
    for char in text:
        if in_string:
            if escaped:escaped=False
            elif char=="\\":escaped=True
            elif char=='"':in_string=False
            continue
        if char=='"':in_string=True;continue
        if char in "[{":stack.append(char);continue
        if char in "]}":
            expected="[" if char=="]" else "{"
            if not stack or stack[-1]!=expected:return None,""
            stack.pop()
    if in_string or stack!=["{"]:
        return None,""
    repaired=text+"}"
    try:
        payload=extract_json_object(repaired)
    except Exception:
        return None,""
    lanes=payload.get("lanes") if isinstance(payload,dict) else None
    if not isinstance(lanes,dict):
        return None,""
    if any(str(key) not in set(DISCOVERY_LANES)|{"diagnosis"} for key in lanes):
        return None,""
    return payload,repaired


def _parse_relation_payload_with_bounded_repair(
    *,storage:StorageSettings,run_id:str,raw:str,raw_sha256:str,resolved_model:str,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    try:
        return extract_json_object(raw),None
    except Exception:
        payload,repaired=_repair_trailing_relation_root_closure(raw)
        if payload is None:
            raise
    repaired_sha=hashlib.sha256(repaired.encode("utf-8")).hexdigest()
    receipt={
        "schema_version":"1.0",
        "run_id":run_id,
        "status":"PARSE_REPAIRED_TRAILING_ROOT_CLOSURE_ZERO_AUTHORITY",
        "resolved_model":resolved_model,
        "raw_sha256":raw_sha256,
        "repaired_sha256":repaired_sha,
        "repair_type":"APPEND_ONE_ROOT_OBJECT_CLOSING_BRACE_AT_EOF",
        "inserted_closing_brace_count":1,
        "insertion_offset":len(raw),
        "original_bytes_mutated":False,
        "string_content_mutated":False,
        "provider_calls_executed":0,
        "scientific_authority":False,
        "authority":{"problem_gate":False,"method":False,"experiment":False,"p0":False,"gpu":False},
    }
    repair_root=_root(storage)/"repairs";repair_root.mkdir(parents=True,exist_ok=True)
    receipt_path=repair_root/f"{run_id}-relation-{raw_sha256[:12]}-trailing-root-closure.json"
    receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return payload,receipt


def _receipts(generator: dict[str, Any]) -> list[dict[str, Any]]:
    return portable_review_receipts(generator)


def _target_refs(receipts: list[dict[str, Any]]) -> set[str]:
    return {str(ref) for row in receipts for ref in row.get("source_refs") or [] if str(ref).startswith("arXiv:")}


def _coobserved(receipts: list[dict[str, Any]]) -> set[tuple[str,str]]:
    return coobserved_pairs(receipts)


def _card(record: dict[str, Any]) -> dict[str, Any]:
    typed=record.get("typed_evidence") or {};axes=current_lane_axes(record.get("lane_keys") or [])
    return {"ref":record.get("ref"),"title":record.get("title"),"abstract":str(record.get("abstract") or "")[:1200],"object":axes.get("object") or [],"context":axes.get("context") or [],"property":axes.get("property") or [],"empirical":[str(x.get("text") or "")[:320] for x in (record.get("empirical_facts") or [])[:2] if isinstance(x,dict)],"assumption":[str(x.get("text") or "")[:320] for x in (typed.get("operational_assumptions") or [])[:1] if isinstance(x,dict)],"failure":[str(x.get("text") or "")[:320] for x in (typed.get("measured_failures") or [])[:1] if isinstance(x,dict)],"boundary":[str(x.get("text") or "")[:320] for x in (typed.get("boundary_observations") or [])[:1] if isinstance(x,dict)]}


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


def _delta_scan_required_refs(
    receipts: list[dict[str, Any]],
    prior_scan: dict[str, Any],
    *,
    relation_state: dict[str, Any] | None = None,
    boundary_manifest: dict[str, Any] | None = None,
) -> tuple[set[str], bool]:
    """Recover the prior relation boundary without trusting scheduler order alone.

    The historical run-id cutoff remains the first choice. Portable review receipts
    are scheduler metadata, however, so later migrations may reorder their run IDs.
    When the cutoff no longer reproduces the exact prior relation-universe digest,
    fall back only to a validated content-addressed boundary manifest bound to this
    exact last_completed_scan. Missing or mismatched provenance remains fail-closed.
    """
    prior_digest=str(prior_scan.get("relation_universe_digest") or "")
    cutoff=str(prior_scan.get("run_id") or "")
    if not prior_digest or not cutoff:
        return set(), False
    old_receipts=[row for row in receipts if str(row.get("run_id") or "")<=cutoff]
    if relation_universe_digest(old_receipts)!=prior_digest:
        manifest=boundary_manifest if boundary_manifest is not None else load_relation_scan_boundary_manifest()
        binding_state=relation_state if isinstance(relation_state,dict) else {"last_completed_scan":dict(prior_scan)}
        archived=boundary_receipts(manifest,binding_state)
        if not archived or relation_universe_digest(archived)!=prior_digest:
            return set(), False
        old_receipts=archived
    old_refs={str(ref) for row in old_receipts for ref in row.get("source_refs") or []}
    current_refs={str(ref) for row in receipts for ref in row.get("source_refs") or []}
    return current_refs-old_refs, True


def relation_prompt(cards: list[dict[str, Any]], required_touch_refs: set[str] | None = None) -> str:
    shape = {
        "lanes": {
            lane: [{"source_a":"arXiv:...","source_b":"arXiv:...","relation":"...","why_lane":"...","missing_piece":""}]
            for lane in DISCOVERY_LANES
        },
        "diagnosis":"...",
    }
    delta_constraint=(
        "DELTA-ONLY CONSTRAINT: every proposed pair MUST include at least one ref from REQUIRED_NEW_ENDPOINTS; old-old pairs are forbidden because the prior bounded scan already covered that relation universe. REQUIRED_NEW_ENDPOINTS="+json.dumps(sorted(required_touch_refs),ensure_ascii=False,separators=(",",":"))+" "
        if required_touch_refs else ""
    )
    return (
        "ZERO-AUTHORITY GLOBAL CROSS-SOURCE RELATION RECALL for an ICLR paper-problem search portfolio. "
        "Never propose a method, paper idea, novelty verdict, Problem-Gate verdict, or downstream action. "
        "The ordinary Search Portfolio already handles single-source phenomena; this pass exists only to recover cross-source pairs that may never have co-occurred in one tranche. "
        "Search ALL supplied primary-evidence cards. A pair may cross scientific-object/context tags; tags are ranking context, never a hard veto. "
        "For each lane return at most its pair_budget proposals, fewer or zero is valid. Do not invent shared measurements, conditions, assumptions, or failures. "
        "Use two DISTINCT primary refs for every proposal even when the lane's ordinary minimum is one, because this layer is specifically a cross-source recall supplement. "+
        delta_constraint+
        "LANE CONTRACTS="+json.dumps(_lane_contracts(),ensure_ascii=False,separators=(",",":"))+
        " RETURN JSON ONLY="+json.dumps(shape,ensure_ascii=False,separators=(",",":"))+
        " CARDS="+json.dumps(cards,ensure_ascii=False,separators=(",",":"))
    )


def lane_review_execution_contract_sha256() -> str:
    material={
        "version":LANE_REVIEW_EXECUTION_CONTRACT_VERSION,
        "model":LANE_REVIEW_MODEL,
        "max_output_tokens":LANE_REVIEW_MAX_OUTPUT_TOKENS,
        "thinking":"provider-default" if str(LANE_REVIEW_MODEL).lower().startswith("glm") else "disabled",
        "temperature":0.0,
        "batch_size":LANE_REVIEW_BATCH_SIZE,
        "cards_scoped_to_batch_source_refs":True,
        "partial_batch_reviews_have_zero_lane_authority":True,
        "review_contract":"all proposals exactly once; PASS only on supplied primary evidence and frozen lane contract",
    }
    return hashlib.sha256(json.dumps(material,sort_keys=True,separators=(",",":")).encode()).hexdigest()


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


def _lane_review_batches(proposals: list[dict[str, Any]], batch_size: int = LANE_REVIEW_BATCH_SIZE) -> list[list[dict[str, Any]]]:
    size=max(1,int(batch_size))
    return [proposals[start:start+size] for start in range(0,len(proposals),size)]


def _lane_review_resolved_models(state: dict[str, Any]) -> set[str]:
    summary=((state.get("raw_artifacts") or {}).get("lane_review") or {})
    values=summary.get("resolved_models") or []
    return {str(value).strip() for value in values if str(value).strip()}


def _review_lane_proposals(
    *,
    proposals: list[dict[str, Any]],
    registry: dict[str, dict[str, Any]],
    storage: StorageSettings,
    run_id: str,
    relation_resolved_model: str,
    state: dict[str, Any],
    responder: Responder | None = None,
) -> dict[str, dict[str, Any]]:
    """Review lane contracts in bounded batches without partial scientific credit.

    Each batch sees only the primary cards referenced by that batch. Raw responses
    are persisted batch-by-batch for execution recovery, but proposal lane_review
    fields are assigned only after every batch returns a complete normalized review.
    """
    batches=_lane_review_batches(proposals)
    call=responder or _ark
    combined:dict[str,dict[str,Any]]={}
    resolved_models:set[str]=set()
    state["lane_review_execution"]={
        "version":LANE_REVIEW_EXECUTION_CONTRACT_VERSION,
        "execution_contract_sha256":lane_review_execution_contract_sha256(),
        "batch_size":LANE_REVIEW_BATCH_SIZE,
        "batches_total":len(batches),
        "batches_completed":0,
        "partial_batch_reviews_have_zero_lane_authority":True,
        "cards_scoped_to_batch_source_refs":True,
        "scientific_authority":False,
    }
    for index,batch in enumerate(batches,1):
        refs=sorted({ref for proposal in batch for ref in proposal.get("source_refs") or []})
        cards=[_card(registry[ref]) for ref in refs]
        response=call(prompt=lane_prompt(batch,cards),model=LANE_REVIEW_MODEL,max_output_tokens=LANE_REVIEW_MAX_OUTPUT_TOKENS)
        raw=str(response.get("text") or "")
        artifact=_write_raw(storage,run_id,f"lane-review-p{index}",LANE_REVIEW_MODEL,raw)
        artifact.update({
            "resolved_model":str(response.get("resolved_model") or LANE_REVIEW_MODEL),
            "batch_index":index,
            "proposal_ids":[str(proposal.get("proposal_id") or "") for proposal in batch],
            "execution_contract_sha256":lane_review_execution_contract_sha256(),
        })
        state["raw_artifacts"][f"lane_review_p{index}"]=artifact
        resolved_models.add(artifact["resolved_model"])
        if artifact["resolved_model"]==str(relation_resolved_model or ""):
            raise RuntimeError("relation-lane-reviewer-not-independent")
        batch_reviews=_normalize_lane_reviews(extract_json_object(raw),batch)
        combined.update(batch_reviews)
        state["lane_review_execution"]["batches_completed"]=index
    expected={str(proposal.get("proposal_id") or "") for proposal in proposals}
    if set(combined)!=expected:
        raise ValueError("lane-review-batch-aggregation-incomplete")
    state["raw_artifacts"]["lane_review"]={
        "requested_model":LANE_REVIEW_MODEL,
        "resolved_models":sorted(resolved_models),
        "resolved_model":"|".join(sorted(resolved_models)),
        "provider_calls_executed":len(batches),
        "batches":len(batches),
        "batch_size":LANE_REVIEW_BATCH_SIZE,
        "execution_contract_sha256":lane_review_execution_contract_sha256(),
        "scientific_authority":False,
    }
    return combined


def reduction_prompt(proposals: list[dict[str, Any]], cards: list[dict[str, Any]]) -> str:
    ledger=[{"key":x["key"],"mature_theories":x["mature_theories"],"veto":x["veto"]} for x in REDUCTION_PATTERNS]
    return "Independent STRICT same-information reduction reviewer; zero authority. These pairs already passed lane review. Infer the narrowest falsifiable prediction and test whether the exact same information is already expressible by the supplied negative-space ledger or mature theory. Domain transfer/renaming or ordinary mature objects are REDUCIBLE. NOT_REDUCED requires a concrete residual prediction. Review every proposal once. matched_patterns may use exact ledger keys only. Return JSON only {\"reviews\":[{\"proposal_id\":\"REL-...\",\"verdict\":\"REDUCIBLE|NOT_REDUCED\",\"exact_prediction\":\"...\",\"matched_patterns\":[],\"strongest_reduction\":\"...\",\"residual_prediction\":\"\"}],\"diagnosis\":\"...\"}. PROPOSALS="+json.dumps(proposals,ensure_ascii=False,separators=(",",":"))+" CARDS="+json.dumps(cards,ensure_ascii=False,separators=(",",":"))+" LEDGER="+json.dumps(ledger,ensure_ascii=False,separators=(",",":"))


def _normalize_proposals(payload: dict[str, Any], registry: dict[str, dict[str, Any]], coobserved: set[tuple[str,str]], *, required_touch_refs: set[str] | None = None) -> list[dict[str, Any]]:
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
            if required_touch_refs and a not in required_touch_refs and b not in required_touch_refs:
                raise ValueError("relation-proposal-misses-required-delta-endpoint")
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
    storage=storage or StorageSettings.from_env();primary_state=primary_state if primary_state is not None else load_primary_evidence_state();generator_state=generator_state if generator_state is not None else load_problem_generator_state();run_id=(now or datetime.now(timezone.utc)).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    receipts=_receipts(generator_state);coverage=source_pair_coverage(receipts);target=_target_refs(receipts);cache_rows=cache_records if cache_records is not None else reviewed_primary_cache_records(storage,reviewed_refs=target);registry={str(x.get("ref")):x for x in cache_rows if x.get("ref")};cached=set(registry);previous_state=previous_state if previous_state is not None else load_global_relation_recall_state()
    state={"schema_version":"1.2","generated_at":_now(),"run_id":run_id,"status":"NOT_RUN","scientific_authority":False,"policy":{"scientific_authority":False,"source_coverage_exhaustion_is_not_relation_exhaustion":True,"full_reviewed_receipt_cache_required_before_global_scan":True,"relation_miner_is_search_control_only":True,"cross_source_recall_supplements_but_does_not_replace_search_portfolio":True,"single_source_lane_search_remains_search_portfolio_responsibility":True,"independent_lane_reviewer_required":True,"independent_reduction_reviewer_required":True,"all_lane_pass_proposals_require_reduction_review":True,"relation_universe_digest_prevents_repeat_model_calls":True,"same_relation_universe_reuses_portable_completed_scan":True,"stale_completed_scan_uses_delta_only_new_endpoint_pairs":True,"delta_only_scan_forbids_old_old_pairs":True,"pair_relation_budgets":dict(PAIR_RELATION_BUDGETS),"max_total_relation_proposals":MAX_TOTAL_PROPOSALS,"zero_proposals_is_valid":True,"not_reduced_only_reopens_focused_problem_generator":True,"automatic_problem_gate_authority":False,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},"models":{"relation":RELATION_MODEL,"lane_review":LANE_REVIEW_MODEL,"reduction":REDUCTION_MODEL},"relation_coverage":coverage,"delta_scan":{"enabled":False,"required_new_endpoint_count":0,"required_new_endpoint_digest":"","scientific_authority":False},"raw_artifacts":{},"proposals":[],"last_completed_scan":{}}
    prior_scan=(previous_state.get("last_completed_scan") or {}) if isinstance(previous_state,dict) else {}
    # Transient provider/reviewer failures are attempt state, not durable scan history.
    # Preserve the last completed relation boundary until a new complete scan replaces it.
    state["last_completed_scan"]=dict(prior_scan)
    prior_digest=str(prior_scan.get("relation_universe_digest") or "")
    if prior_digest and prior_digest==str(coverage.get("relation_universe_digest") or ""):
        prior_summary=dict(previous_state.get("summary") or {});prior_summary.update({"reviewed_receipt_sources":int(coverage.get("reviewed_receipt_sources") or len(target)),"cached_reviewed_sources":len(cached & target),"cache_completeness_fraction":round(len(cached & target)/len(target),4) if target else 0.0,"possible_source_pairs":int(coverage.get("possible_source_pairs") or 0),"coobserved_source_pairs":int(coverage.get("coobserved_source_pairs") or 0),"pair_coverage_fraction":float(coverage.get("pair_coverage_fraction") or 0.0)})
        state.update({"status":"SKIPPED_RELATION_UNIVERSE_UNCHANGED","summary":prior_summary,"proposals":[dict(row) for row in previous_state.get("proposals") or [] if isinstance(row,dict)],"last_completed_scan":dict(prior_scan)})
        return state
    required_touch_refs:set[str]=set()
    if prior_digest:
        required_touch_refs,reconstructable=_delta_scan_required_refs(receipts,prior_scan,relation_state=previous_state)
        if not reconstructable:
            state["status"]="HOLD_RELATION_DELTA_BOUNDARY_UNRECONSTRUCTABLE";state["summary"]=_summary(coverage,target,cached,[]);return state
        if not required_touch_refs:
            state["status"]="SKIPPED_RELATION_NO_NEW_SOURCE_ENDPOINTS";state["summary"]=_summary(coverage,target,cached,[]);state["last_completed_scan"]=dict(prior_scan);return state
        digest=hashlib.sha256("\n".join(sorted(required_touch_refs)).encode()).hexdigest()
        state["delta_scan"]={"enabled":True,"required_new_endpoint_count":len(required_touch_refs),"required_new_endpoint_digest":digest,"prior_scan_run_id":str(prior_scan.get("run_id") or ""),"scientific_authority":False}
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
        response=call(prompt=relation_prompt(cards,required_touch_refs=required_touch_refs),model=RELATION_MODEL,max_output_tokens=5200);raw=str(response.get("text") or "");artifact=_write_raw(storage,run_id,"relation",RELATION_MODEL,raw);artifact["resolved_model"]=str(response.get("resolved_model") or RELATION_MODEL);state["raw_artifacts"]["relation"]=artifact
        relation_payload,repair_receipt=_parse_relation_payload_with_bounded_repair(storage=storage,run_id=run_id,raw=raw,raw_sha256=str(artifact.get("sha256") or ""),resolved_model=str(artifact.get("resolved_model") or ""))
        if repair_receipt is not None:state["raw_artifacts"]["relation_repair"]=repair_receipt
        proposals=_normalize_proposals(relation_payload,registry,_coobserved(receipts),required_touch_refs=required_touch_refs)
    except Exception as error:
        state["status"]="RELATION_PROVIDER_ERROR_ZERO_AUTHORITY";state["error"]=_provider_error_text(error);state["summary"]=_summary(coverage,target,cached,[]);return state
    if proposals:
        try:
            relation_resolved=str((state["raw_artifacts"].get("relation") or {}).get("resolved_model") or "")
            reviews=_review_lane_proposals(proposals=proposals,registry=registry,storage=storage,run_id=run_id,relation_resolved_model=relation_resolved,state=state,responder=lane_responder)
            for x in proposals:x["lane_review"]=reviews[x["proposal_id"]]
        except Exception as error:
            state["status"]="LANE_REVIEW_ERROR_ZERO_AUTHORITY";state["error"]=_provider_error_text(error);state["proposals"]=proposals;state["summary"]=_summary(coverage,target,cached,proposals);return state
    passed=[x for x in proposals if (x.get("lane_review") or {}).get("verdict")=="PASS"]
    if passed:
        refs=sorted({ref for x in passed for ref in x["source_refs"]});cards3=[_card(registry[ref]) for ref in refs];call=reduction_responder or _ark
        try:
            response=call(prompt=reduction_prompt(passed,cards3),model=REDUCTION_MODEL,max_output_tokens=6000);raw=str(response.get("text") or "");artifact=_write_raw(storage,run_id,"reduction-review",REDUCTION_MODEL,raw);artifact["resolved_model"]=str(response.get("resolved_model") or REDUCTION_MODEL);state["raw_artifacts"]["reduction_review"]=artifact
            if artifact["resolved_model"] in _lane_review_resolved_models(state): raise RuntimeError("lane-reduction-reviewer-not-independent")
            reviews=_normalize_reductions(extract_json_object(raw),passed)
            for x in passed:x["reduction_review"]=reviews[x["proposal_id"]]
        except Exception as error:
            state["status"]="REDUCTION_REVIEW_ERROR_ZERO_AUTHORITY";state["error"]=_provider_error_text(error);state["proposals"]=proposals;state["summary"]=_summary(coverage,target,cached,proposals);return state
    state["proposals"]=proposals;state["summary"]=_summary(coverage,target,cached,proposals);state["status"]="GLOBAL_RELATION_RECALL_COMPLETE"
    state["last_completed_scan"]={"run_id":run_id,"mode":"delta_only_new_endpoint" if required_touch_refs else "full_relation_universe","prior_scan_run_id":str(prior_scan.get("run_id") or "") if required_touch_refs else "","required_new_endpoint_count":len(required_touch_refs),"relation_universe_digest":str(coverage.get("relation_universe_digest") or ""),"relation_coverage":{"reviewed_receipt_sources":coverage.get("reviewed_receipt_sources",0),"possible_source_pairs":coverage.get("possible_source_pairs",0),"coobserved_source_pairs":coverage.get("coobserved_source_pairs",0),"pair_coverage_fraction":coverage.get("pair_coverage_fraction",0.0)},"summary":dict(state["summary"]),"models":dict(state["models"]),"scientific_authority":False}
    return state


def resume_global_relation_recall_from_relation_raw(
    *,
    raw_input: Path,
    expected_raw_sha256: str,
    relation_requested_model: str = RELATION_MODEL,
    relation_resolved_model: str = RELATION_MODEL,
    raw_origin_run_id: str = "",
    storage: StorageSettings | None = None,
    primary_state: dict[str, Any] | None = None,
    generator_state: dict[str, Any] | None = None,
    cache_records: list[dict[str, Any]] | None = None,
    previous_state: dict[str, Any] | None = None,
    lane_responder: Responder | None = None,
    reduction_responder: Responder | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Resume lane/reduction review from an exact archived relation-miner response.

    This path never calls the relation miner.  It revalidates the current source
    universe, the prior completed-scan boundary, cache completeness, and every
    delta-only proposal before spending one lane-review call.  A failed lane or
    reduction review preserves the prior completed scan exactly.
    """
    storage=storage or StorageSettings.from_env()
    primary_state=primary_state if primary_state is not None else load_primary_evidence_state()
    generator_state=generator_state if generator_state is not None else load_problem_generator_state()
    previous_state=previous_state if previous_state is not None else load_global_relation_recall_state()
    if not raw_input.is_file():
        raise ValueError(f"relation replay input unavailable: {raw_input}")
    expected=str(expected_raw_sha256 or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}",expected):
        raise ValueError("relation replay requires exact 64-hex raw sha256")
    raw=raw_input.read_text(encoding="utf-8")
    actual=hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if actual!=expected:
        raise ValueError(f"relation replay digest mismatch expected={expected} actual={actual}")
    requested=str(relation_requested_model or "").strip();resolved=str(relation_resolved_model or "").strip()
    if not requested or not resolved:
        raise ValueError("relation replay requires requested and resolved model identities")

    run_id=(now or datetime.now(timezone.utc)).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    receipts=_receipts(generator_state);coverage=source_pair_coverage(receipts);target=_target_refs(receipts)
    cache_rows=cache_records if cache_records is not None else reviewed_primary_cache_records(storage,reviewed_refs=target)
    registry={str(x.get("ref")):x for x in cache_rows if x.get("ref")};cached=set(registry)
    state={
        "schema_version":"1.3",
        "generated_at":_now(),
        "run_id":run_id,
        "status":"NOT_RUN",
        "scientific_authority":False,
        "policy":{
            "scientific_authority":False,
            "source_coverage_exhaustion_is_not_relation_exhaustion":True,
            "full_reviewed_receipt_cache_required_before_global_scan":True,
            "relation_miner_is_search_control_only":True,
            "cross_source_recall_supplements_but_does_not_replace_search_portfolio":True,
            "single_source_lane_search_remains_search_portfolio_responsibility":True,
            "independent_lane_reviewer_required":True,
            "independent_reduction_reviewer_required":True,
            "all_lane_pass_proposals_require_reduction_review":True,
            "relation_universe_digest_prevents_repeat_model_calls":True,
            "same_relation_universe_reuses_portable_completed_scan":True,
            "stale_completed_scan_uses_delta_only_new_endpoint_pairs":True,
            "delta_only_scan_forbids_old_old_pairs":True,
            "relation_raw_replay_requires_exact_sha256":True,
            "relation_raw_replay_executes_zero_relation_miner_calls":True,
            "relation_raw_replay_revalidates_delta_boundary":True,
            "pair_relation_budgets":dict(PAIR_RELATION_BUDGETS),
            "max_total_relation_proposals":MAX_TOTAL_PROPOSALS,
            "zero_proposals_is_valid":True,
            "not_reduced_only_reopens_focused_problem_generator":True,
            "automatic_problem_gate_authority":False,
            "automatic_method_authority":False,
            "automatic_experiment_authority":False,
            "automatic_p0_authority":False,
        },
        "models":{"relation":requested,"lane_review":LANE_REVIEW_MODEL,"reduction":REDUCTION_MODEL},
        "relation_coverage":coverage,
        "delta_scan":{"enabled":False,"required_new_endpoint_count":0,"required_new_endpoint_digest":"","scientific_authority":False},
        "raw_artifacts":{},
        "proposals":[],
        "last_completed_scan":{},
    }
    prior_scan=(previous_state.get("last_completed_scan") or {}) if isinstance(previous_state,dict) else {}
    state["last_completed_scan"]=dict(prior_scan)
    prior_digest=str(prior_scan.get("relation_universe_digest") or "")
    current_digest=str(coverage.get("relation_universe_digest") or "")
    if prior_digest and prior_digest==current_digest:
        prior_summary=dict(previous_state.get("summary") or {});prior_summary.update({"reviewed_receipt_sources":int(coverage.get("reviewed_receipt_sources") or len(target)),"cached_reviewed_sources":len(cached & target),"cache_completeness_fraction":round(len(cached & target)/len(target),4) if target else 0.0,"possible_source_pairs":int(coverage.get("possible_source_pairs") or 0),"coobserved_source_pairs":int(coverage.get("coobserved_source_pairs") or 0),"pair_coverage_fraction":float(coverage.get("pair_coverage_fraction") or 0.0)})
        state.update({"status":"SKIPPED_RELATION_UNIVERSE_UNCHANGED","summary":prior_summary,"proposals":[dict(row) for row in previous_state.get("proposals") or [] if isinstance(row,dict)],"last_completed_scan":dict(prior_scan)})
        return state
    required_touch_refs:set[str]=set()
    if prior_digest:
        required_touch_refs,reconstructable=_delta_scan_required_refs(receipts,prior_scan,relation_state=previous_state)
        if not reconstructable:
            state["status"]="HOLD_RELATION_DELTA_BOUNDARY_UNRECONSTRUCTABLE";state["summary"]=_summary(coverage,target,cached,[]);return state
        if not required_touch_refs:
            state["status"]="SKIPPED_RELATION_NO_NEW_SOURCE_ENDPOINTS";state["summary"]=_summary(coverage,target,cached,[]);return state
        digest=hashlib.sha256("\n".join(sorted(required_touch_refs)).encode()).hexdigest()
        state["delta_scan"]={"enabled":True,"required_new_endpoint_count":len(required_touch_refs),"required_new_endpoint_digest":digest,"prior_scan_run_id":str(prior_scan.get("run_id") or ""),"scientific_authority":False}
    ps=primary_state.get("summary") or {}
    if ps.get("source_coverage_exhausted") is not True:
        state["status"]="SKIPPED_SOURCE_COVERAGE_OPEN";state["summary"]=_summary(coverage,target,cached,[]);return state
    if not coverage.get("relation_blind_spot_detected"):
        state["status"]="SKIPPED_PAIR_COVERAGE_COMPLETE";state["summary"]=_summary(coverage,target,cached,[]);return state
    missing=sorted(target-cached)
    if missing:
        state["status"]="HOLD_RELATION_CACHE_INCOMPLETE";state["cache_missing_count"]=len(missing);state["cache_missing_ref_digest"]=hashlib.sha256("\n".join(missing).encode()).hexdigest();state["summary"]=_summary(coverage,target,cached,[]);return state

    artifact=_write_raw(storage,run_id,"relation-replay",requested,raw)
    artifact.update({"resolved_model":resolved,"raw_replayed_without_provider":True,"provider_calls_executed":0,"origin_run_id":str(raw_origin_run_id or ""),"origin_raw_sha256":expected})
    state["raw_artifacts"]["relation"]=artifact
    try:
        relation_payload,repair_receipt=_parse_relation_payload_with_bounded_repair(storage=storage,run_id=run_id,raw=raw,raw_sha256=expected,resolved_model=resolved)
        if repair_receipt is not None:state["raw_artifacts"]["relation_repair"]=repair_receipt
        proposals=_normalize_proposals(relation_payload,registry,_coobserved(receipts),required_touch_refs=required_touch_refs)
    except Exception as error:
        state["status"]="RELATION_REPLAY_PARSE_ERROR_ZERO_AUTHORITY";state["error"]=_provider_error_text(error);state["summary"]=_summary(coverage,target,cached,[]);return state

    if proposals:
        try:
            reviews=_review_lane_proposals(proposals=proposals,registry=registry,storage=storage,run_id=run_id,relation_resolved_model=resolved,state=state,responder=lane_responder)
            for x in proposals:x["lane_review"]=reviews[x["proposal_id"]]
        except Exception as error:
            state["status"]="LANE_REVIEW_ERROR_ZERO_AUTHORITY";state["error"]=_provider_error_text(error);state["proposals"]=proposals;state["summary"]=_summary(coverage,target,cached,proposals);return state
    passed=[x for x in proposals if (x.get("lane_review") or {}).get("verdict")=="PASS"]
    if passed:
        refs=sorted({ref for x in passed for ref in x["source_refs"]});cards3=[_card(registry[ref]) for ref in refs];call=reduction_responder or _ark
        try:
            response=call(prompt=reduction_prompt(passed,cards3),model=REDUCTION_MODEL,max_output_tokens=6000);reduction_raw=str(response.get("text") or "");red_artifact=_write_raw(storage,run_id,"reduction-review",REDUCTION_MODEL,reduction_raw);red_artifact["resolved_model"]=str(response.get("resolved_model") or REDUCTION_MODEL);state["raw_artifacts"]["reduction_review"]=red_artifact
            if red_artifact["resolved_model"] in _lane_review_resolved_models(state): raise RuntimeError("lane-reduction-reviewer-not-independent")
            reviews=_normalize_reductions(extract_json_object(reduction_raw),passed)
            for x in passed:x["reduction_review"]=reviews[x["proposal_id"]]
        except Exception as error:
            state["status"]="REDUCTION_REVIEW_ERROR_ZERO_AUTHORITY";state["error"]=_provider_error_text(error);state["proposals"]=proposals;state["summary"]=_summary(coverage,target,cached,proposals);return state
    state["proposals"]=proposals;state["summary"]=_summary(coverage,target,cached,proposals);state["status"]="GLOBAL_RELATION_RECALL_COMPLETE"
    state["last_completed_scan"]={"run_id":run_id,"mode":"delta_only_new_endpoint" if required_touch_refs else "full_relation_universe","prior_scan_run_id":str(prior_scan.get("run_id") or "") if required_touch_refs else "","required_new_endpoint_count":len(required_touch_refs),"relation_universe_digest":current_digest,"relation_coverage":{"reviewed_receipt_sources":coverage.get("reviewed_receipt_sources",0),"possible_source_pairs":coverage.get("possible_source_pairs",0),"coobserved_source_pairs":coverage.get("coobserved_source_pairs",0),"pair_coverage_fraction":coverage.get("pair_coverage_fraction",0.0)},"summary":dict(state["summary"]),"models":dict(state["models"]),"scientific_authority":False}
    return state


def write_resumed_global_relation_recall_state(
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
    *,
    storage: StorageSettings | None = None,
    raw_input: Path,
    expected_raw_sha256: str,
    relation_requested_model: str = RELATION_MODEL,
    relation_resolved_model: str = RELATION_MODEL,
    raw_origin_run_id: str = "",
    explicit_manual_scan_intent: bool = False,
    admission_builder: Callable[...,dict[str,Any]] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Explicit-manual writer for a zero-relation-call resume transaction."""
    storage=storage or StorageSettings.from_env()
    if explicit_manual_scan_intent is not True:
        raise RuntimeError("global relation resume writer requires explicit manual scan intent")
    if admission_builder is None:
        from .paper_first_global_relation_scan_admission import build_global_relation_scan_admission
        admission_builder=build_global_relation_scan_admission
    from .paper_first_relation_delta_preflight import load_private_relation_delta_preflight
    primary_state=kwargs.get("primary_state") if "primary_state" in kwargs else load_primary_evidence_state()
    generator_state=kwargs.get("generator_state") if "generator_state" in kwargs else load_problem_generator_state()
    previous_state=kwargs.get("previous_state") if "previous_state" in kwargs else load_global_relation_recall_state()
    admission=admission_builder(primary_state=primary_state,generator_state=generator_state,relation_state=previous_state,delta_state=load_private_relation_delta_preflight(storage=storage))
    if (admission.get("summary") or {}).get("manual_scan_eligible") is not True:
        raise RuntimeError("global relation resume admission blocked: "+",".join(str(x) for x in admission.get("failed_checks") or []))
    call_kwargs=dict(kwargs);call_kwargs.update({"storage":storage,"primary_state":primary_state,"generator_state":generator_state,"previous_state":previous_state})
    state=resume_global_relation_recall_from_relation_raw(raw_input=raw_input,expected_raw_sha256=expected_raw_sha256,relation_requested_model=relation_requested_model,relation_resolved_model=relation_resolved_model,raw_origin_run_id=raw_origin_run_id,**call_kwargs)
    from .paper_first_global_relation_scan_admission import public_global_relation_scan_admission_summary
    state["writer_admission"]=public_global_relation_scan_admission_summary(admission)
    state.setdefault("policy",{})["explicit_manual_writer_admission_required"]=True
    private=_root(storage);private.mkdir(parents=True,exist_ok=True);(private/"latest.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    public=public_relation_recall_state(state,storage);json_path.parent.mkdir(parents=True,exist_ok=True);json_path.write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");js_path.write_text("window.PAPER_FIRST_GLOBAL_RELATION_RECALL = "+json.dumps(public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state


def mark_lane_review_retry_exhausted(state:dict[str,Any], *, attempt_run_ids:list[str], exact_retry_limit:int=1)->dict[str,Any]:
    """Mark a same-universe lane-review execution path terminal after its exact retry."""
    out=json.loads(json.dumps(state,ensure_ascii=False))
    if out.get("status")!="LANE_REVIEW_ERROR_ZERO_AUTHORITY":raise ValueError("lane retry exhaustion requires LANE_REVIEW_ERROR_ZERO_AUTHORITY")
    relation_artifact=(out.get("raw_artifacts") or {}).get("relation") or {};raw_sha=str(relation_artifact.get("sha256") or "")
    if not re.fullmatch(r"[0-9a-f]{64}",raw_sha):raise ValueError("lane retry exhaustion requires exact archived relation raw")
    attempts=[str(value).strip() for value in attempt_run_ids if str(value).strip()]
    expected_attempts=max(1,int(exact_retry_limit)+1)
    if len(attempts)!=expected_attempts or len(set(attempts))!=len(attempts):raise ValueError("lane retry exhaustion attempt accounting invalid")
    delta=out.get("delta_scan") or {};relation_digest=str((out.get("summary") or {}).get("relation_universe_digest") or "")
    if not re.fullmatch(r"[0-9a-f]{64}",relation_digest):raise ValueError("lane retry exhaustion requires current relation universe digest")
    out.setdefault("policy",{}).update({"same_relation_universe_lane_review_retry_budget_bounded":True,"lane_review_retry_exhaustion_is_execution_control_not_scientific_negative":True,"lane_review_retry_reopens_only_on_new_relation_universe_or_execution_contract":True})
    out["execution_control"]={"status":"LANE_REVIEW_EXACT_RETRY_EXHAUSTED","stage":"lane_review","relation_universe_digest":relation_digest,"required_new_endpoint_digest":str(delta.get("required_new_endpoint_digest") or ""),"relation_raw_sha256":raw_sha,"lane_review_model":LANE_REVIEW_MODEL,"lane_review_execution_contract_version":LANE_REVIEW_EXECUTION_CONTRACT_VERSION,"lane_review_batch_size":LANE_REVIEW_BATCH_SIZE,"lane_review_execution_contract_sha256":lane_review_execution_contract_sha256(),"attempt_run_ids":attempts,"provider_attempts":len(attempts),"exact_retry_limit":int(exact_retry_limit),"retry_budget_exhausted":True,"scientific_authority":False,"reopen_only_if":f"A new relation source universe is frozen, or the versioned lane-review execution contract changes before a new explicit-manual attempt. Do not retry the same universe under {LANE_REVIEW_EXECUTION_CONTRACT_VERSION} (batch_size={LANE_REVIEW_BATCH_SIZE}) after this receipt."}
    return out


def public_relation_recall_state(state:dict[str,Any],storage:StorageSettings|None=None)->dict[str,Any]:
    public=json.loads(json.dumps(state,ensure_ascii=False))
    for artifact in (public.get("raw_artifacts") or {}).values():
        if isinstance(artifact,dict):artifact.pop("path",None)
    compact=[]
    for row in public.get("proposals") or []:
        compact.append({"proposal_id":row.get("proposal_id"),"lane":row.get("lane"),"source_refs":row.get("source_refs") or [],"previously_coobserved":row.get("previously_coobserved") is True,"lane_verdict":(row.get("lane_review") or {}).get("verdict",""),"reduction_verdict":(row.get("reduction_review") or {}).get("verdict",""),"matched_patterns":(row.get("reduction_review") or {}).get("matched_patterns") or [],"focused_problem_generator_reopen_required":(row.get("reduction_review") or {}).get("verdict")=="NOT_REDUCED","scientific_authority":False})
    public["proposals"]=compact;public["scientific_authority"]=False
    return redact_private_paths(public,storage=storage or StorageSettings.from_env())


def write_global_relation_recall_state(
    json_path:Path=DEFAULT_JSON,
    js_path:Path=DEFAULT_JS,
    *,
    storage:StorageSettings|None=None,
    explicit_manual_scan_intent:bool=False,
    admission_builder:Callable[...,dict[str,Any]]|None=None,
    **kwargs:Any,
)->dict[str,Any]:
    storage=storage or StorageSettings.from_env()
    if explicit_manual_scan_intent is not True:
        raise RuntimeError("global relation writer requires explicit manual scan intent")
    if admission_builder is None:
        from .paper_first_global_relation_scan_admission import build_global_relation_scan_admission
        admission_builder=build_global_relation_scan_admission
    admission_kwargs:dict[str,Any]={}
    if "primary_state" in kwargs: admission_kwargs["primary_state"]=kwargs["primary_state"]
    if "generator_state" in kwargs: admission_kwargs["generator_state"]=kwargs["generator_state"]
    if "previous_state" in kwargs: admission_kwargs["relation_state"]=kwargs["previous_state"]
    admission=admission_builder(**admission_kwargs)
    if (admission.get("summary") or {}).get("manual_scan_eligible") is not True:
        raise RuntimeError("global relation writer admission blocked: "+",".join(str(x) for x in admission.get("failed_checks") or []))
    state=run_global_relation_recall(storage=storage,**kwargs)
    from .paper_first_global_relation_scan_admission import public_global_relation_scan_admission_summary
    state["writer_admission"]=public_global_relation_scan_admission_summary(admission)
    state.setdefault("policy",{})["explicit_manual_writer_admission_required"]=True
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
