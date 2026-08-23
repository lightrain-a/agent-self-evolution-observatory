from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .config import PROJECT_ROOT
except ImportError:  # direct script execution
    import sys
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from research_pipeline.config import PROJECT_ROOT

SCHEMA_VERSION = "1.0"
SPEC = PROJECT_ROOT / "research_pipeline" / "longitudinal_safety_discovery_lessons_20260823.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "longitudinal-safety-discovery-cycle-20260823.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "longitudinal-safety-discovery-cycle-20260823.js"
ROUNDS = (
    ("v3", "idea-discovery-v3.json", "idea-discovery-v3-external-reviews.json"),
    ("v3.1", "idea-discovery-v31.json", "idea-discovery-v31-external-reviews.json"),
    ("v4", "idea-discovery-v4.json", "idea-discovery-v4-external-reviews.json"),
    ("v5", "idea-discovery-v5.json", "idea-discovery-v5-external-reviews.json"),
    ("v5.1", "idea-discovery-v51.json", "idea-discovery-v51-external-reviews.json"),
    ("v5.2", "idea-discovery-v52.json", "idea-discovery-v52-external-reviews.json"),
    ("v5.3", "idea-discovery-v53.json", "idea-discovery-v53-external-reviews.json"),
)
TERMS = ("persistent", "memory", "skill", "update", "self-evol", "safety", "verification", "verifier", "rollback", "longitudinal", "failure", "drift", "policy", "agent")
MATERIAL_SIGNALS = ("replace the", "change the", "learned object", "persistent object", "pivot", "reframe", "target regime", "make descendants", "interaction-aware", "transition operator", "migration operator", "repair or rollback representation", "residual-corrected", "formal", "causal slot", "version-contrastive", "zero-anchor", "cross-lineage")
BASELINE_ONLY_SIGNALS = ("add a capacity-matched", "add same-information", "compare it", "compare against", "include a", "preregister", "report a", "run a crossed", "run a prequential")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _flatten(value: Any) -> str:
    if isinstance(value, dict): return " ".join(_flatten(v) for v in value.values())
    if isinstance(value, list): return " ".join(_flatten(v) for v in value)
    return str(value or "")


def _rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("all_children", "children", "all_candidates"):
        if isinstance(payload.get(key), list): return [dict(x) for x in payload[key] if isinstance(x, dict)]
    return []


def _reviews(path: Path) -> dict[str, dict[str, Any]]:
    try: raw = json.loads(path.read_text(encoding="utf-8")).get("reviews") or {}
    except (OSError, json.JSONDecodeError): return {}
    out = {}
    if isinstance(raw, dict):
        for cid, value in raw.items():
            if isinstance(value, list) and value and isinstance(value[-1], dict): out[str(cid)] = dict(value[-1])
            elif isinstance(value, dict): out[str(cid)] = dict(value)
    return out


def _title(row: dict[str, Any]) -> str:
    value = row.get("title")
    return str((value.get("en") or value.get("zh") or "") if isinstance(value, dict) else (value or row.get("id") or ""))


def _mutation_class(required_action: str, verdict: str) -> tuple[str, int, int]:
    text = required_action.lower()
    material = sum(sig in text for sig in MATERIAL_SIGNALS)
    baseline = sum(sig in text for sig in BASELINE_ONLY_SIGNALS)
    if verdict == "block" and material > 0:
        return "STRUCTURAL_MUTATION", material, baseline
    if material >= 2 or (material >= 1 and baseline == 0):
        return "STRUCTURAL_MUTATION", material, baseline
    if baseline > 0:
        return "EXPERIMENT_OR_BASELINE_REPAIR", material, baseline
    return "UNCLASSIFIED_REPAIR", material, baseline


def _pairwise_tournament(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    collision_score={"none":3,"partial":2,"unrecorded":1,"direct":0}
    verdict_score={"revise":2,"block":1}
    result=[]
    for left in rows:
        wins=ties=losses=points=0.0
        lv=(int(left.get("material_signal_count") or 0),verdict_score.get(left.get("external_verdict"),0),int(left.get("target_relevance_hits") or 0),collision_score.get(left.get("collision_status"),1),float(left.get("historical_mean_score") or 0),-int(left.get("baseline_only_signal_count") or 0))
        for right in rows:
            if right is left: continue
            rv=(int(right.get("material_signal_count") or 0),verdict_score.get(right.get("external_verdict"),0),int(right.get("target_relevance_hits") or 0),collision_score.get(right.get("collision_status"),1),float(right.get("historical_mean_score") or 0),-int(right.get("baseline_only_signal_count") or 0))
            l=sum(a>b for a,b in zip(lv,rv)); r=sum(a<b for a,b in zip(lv,rv))
            if l>r: wins+=1; points+=1
            elif r>l: losses+=1
            else: ties+=1; points+=0.5
        item=dict(left); item.update({"pairwise_wins":int(wins),"pairwise_ties":int(ties),"pairwise_losses":int(losses),"pairwise_points":points}); result.append(item)
    result.sort(key=lambda x:(-x["pairwise_points"],-x["mutation_score"],x["candidate_id"]))
    for index,row in enumerate(result,1): row["tournament_rank"]=index
    return result


def build_historical_pool_audit() -> dict[str, Any]:
    records, round_counts = [], {}
    for round_id, payload_name, review_name in ROUNDS:
        payload = json.loads((PROJECT_ROOT / "generated" / payload_name).read_text(encoding="utf-8"))
        reviews = _reviews(PROJECT_ROOT / "generated" / review_name)
        candidates = _rows(payload); round_counts[round_id] = len(candidates)
        for row in candidates:
            cid = str(row.get("id") or ""); review = reviews.get(cid) or {}; verdict = str(review.get("verdict") or row.get("external_verdict") or "pending").lower()
            title = _title(row); text = " ".join([title, _flatten(row.get("problem")), _flatten(row.get("real_problem")), _flatten(row.get("exact_mechanism")), _flatten(row.get("persistent_update_object")), _flatten(row.get("update_surface")), _flatten(row.get("learning_signal"))]).lower()
            relevance = sum(term in text for term in TERMS); direct = review.get("direct_collision") or {}; collision = str(direct.get("status") or "unrecorded") if isinstance(direct, dict) else "unrecorded"; action = str(review.get("required_action") or "").strip(); mean = float(row.get("mean_score") or 0)
            mutation_class, material_count, baseline_count = _mutation_class(action, verdict)
            score = {"revise":24,"block":12,"pass":2,"pending":0}.get(verdict,0) + 3*relevance + min(mean,5) + {"partial":4,"none":3,"unrecorded":2,"direct":-4}.get(collision,0) + (4 if action else 0) + 4*material_count - 2*baseline_count
            records.append({"round":round_id,"candidate_id":cid,"title":title,"external_verdict":verdict,"target_relevance_hits":relevance,"historical_mean_score":mean,"collision_status":collision,"review_vector_present":bool(action),"required_action":action[:1200],"mutation_class":mutation_class,"material_signal_count":material_count,"baseline_only_signal_count":baseline_count,"mutation_score":round(score,3),"scientific_authority":False})
    ids = [x["candidate_id"] for x in records]; eligible = [x for x in records if x["external_verdict"] in {"revise","block"} and x["target_relevance_hits"] >= 2 and x["review_vector_present"]]; eligible.sort(key=lambda x:(-x["mutation_score"],x["candidate_id"]))
    structural=[x for x in eligible if x["mutation_class"]=="STRUCTURAL_MUTATION"]; tournament=_pairwise_tournament(structural)
    experiment_only=[x for x in eligible if x["mutation_class"]=="EXPERIMENT_OR_BASELINE_REPAIR"]
    return {"round_counts":round_counts,"generation_records":len(records),"unique_candidate_ids":len(set(ids)),"duplicate_candidate_ids":len(ids)-len(set(ids)),"verdict_counts":dict(sorted(Counter(x["external_verdict"] for x in records).items())),"horse_race":{"mode":"all-vs-all-pairwise-failure-lineage-mutation-tournament","uses_all_historical_generation_records":True,"pairwise_tournament_precedent":"idea-discovery-v4","old_winner_selection_is_forbidden":True,"baseline_only_repairs_do_not_enter_structural_tournament":True,"purpose":"select material mutation parents and reviewer vectors, not promote historical ideas","eligible_failure_lineages":len(eligible),"structural_mutation_lineages":len(structural),"experiment_or_baseline_repair_lineages":len(experiment_only),"pairwise_matches":len(structural)*(len(structural)-1)//2,"tournament_top8":tournament[:8],"top_mutation_parents":tournament[:16],"scientific_authority":False}}


def validate_discovery_cycle(payload: dict[str, Any]) -> list[str]:
    errors = []; audit = payload.get("historical_pool_audit") or {}; summary = payload.get("summary") or {}; debate = payload.get("debate_contract") or {}
    if payload.get("scientific_authority") is not False: errors.append("scientific-authority-leak")
    if (audit.get("generation_records"), audit.get("unique_candidate_ids")) != (119,119): errors.append("historical-pool-not-119-unique")
    if (summary.get("problem_gate_pass"), summary.get("active_research_items_after")) != (0,0): errors.append("illegal-promotion")
    if debate.get("transcript_required_before_problem_gate") is not True or debate.get("single_model_structured_debate_is_not_independent_review") is not True or debate.get("candidate_identity_lock_required") is not True or debate.get("unmapped_candidate_alias_forces_protocol_fail") is not True or debate.get("explicit_parent_child_mapping_required_for_material_mutation") is not True: errors.append("debate-contract-incomplete")
    if (payload.get("policy") or {}).get("canonical_open_transaction_is_not_mutated") is not True: errors.append("canonical-open-transaction-mutation")
    for row in payload.get("lessons") or []:
        if row.get("scientific_authority") is not False or not row.get("lesson_id") or not row.get("reopen_condition") or not row.get("reusable_precheck"): errors.append("invalid-failure-lesson:"+str(row.get("lesson_id") or "missing"))
    return sorted(set(errors))


def build_discovery_cycle(*, generated_at: str | None = None) -> dict[str, Any]:
    spec = json.loads(SPEC.read_text(encoding="utf-8")); lessons = [dict(x, scientific_authority=False) for x in spec.get("lessons") or []]; historical = build_historical_pool_audit()
    payload = {"schema_version":SCHEMA_VERSION,"generated_at":generated_at or _now(),"status":"RECORDED_ZERO_SURVIVOR_FAILURE_MEMORY_AND_NEXT_DISCOVERY_POLICY","strategy_version":spec.get("strategy_version"),"policy":{"canonical_open_transaction_is_not_mutated":True,"historical_horse_race_is_search_control_only":True,"historical_pass_is_not_current_novelty":True,"failure_memory_is_a_mutation_prior_not_a_veto":True,"material_mutation_required_for_revival":True,"debate_cannot_grant_problem_gate":True,"support_failure_is_not_scientific_failure":True,"problem_gate_remains_mandatory":True,"active_researchitem_zero_is_valid":True},"transaction_receipts":spec.get("transaction_receipts") or {},"historical_pool_audit":historical,"lessons":lessons,"debate_contract":{"status":"REQUIRED_FOR_NEXT_MUTATION_ROUND","minimum_rounds":2,"roles":[{"role":"proposer","duty":"material mutation from an explicit failure/reopen condition"},{"role":"reduction_critic","duty":"strongest same-information simplification, mature reduction or collision"},{"role":"substrate_critic","duty":"attack grounding, same-substrate units, truth and observability"},{"role":"proposer_rebuttal","duty":"change a scientific object/assumption/observable/intervention/supervision/deployment boundary; rhetoric is invalid"},{"role":"judge","duty":"STOP, REVISE, HOLD_SUPPORT, or ELIGIBLE_FOR_PROBLEMGATE only"}],"transcript_required_before_problem_gate":True,"candidate_identity_lock_required":True,"unmapped_candidate_alias_forces_protocol_fail":True,"explicit_parent_child_mapping_required_for_material_mutation":True,"single_model_structured_debate_is_not_independent_review":True,"independent_reviewer_still_required_downstream":True,"scientific_authority":False},"failure_directed_mutation_contract":{"parent_sources":["historical REVISE/BLOCK reviewer vectors","current exact reductions","source/lane failures","support-censored resume boundaries"],"allowed_material_changes":["scientific_object","assumption","observable","intervention","supervision","deployment_boundary"],"forbidden_changes":["title-only rename","new seed/model/baseline only","weaker comparator","unsupported cross-source analogy","support failure as scientific evidence"],"each_child_must_name_parent_failure_lesson":True,"each_child_must_name_strongest_reduction_before_generation":True,"each_child_must_define_cheapest_falsifier_before_method_design":True,"scientific_authority":False},"next_cycle":{"canonical_state":"HOLD_CANONICAL_DISCOVERY_TRANSACTION_OPEN","prepared_actions":["race 119 historical lineages for mutation potential","mutate only material reviewer-vector/reopen-condition failures","record proposer-critic-rebuttal-judge debate before ProblemGate","resume only support-censored anchored lanes when provider support exists"],"automatic_provider_calls_authorized":0,"problem_gate_authorized":False,"researchitem_creation_authorized":False,"experiment_authorized":False,"gpu_authorized":False,"scientific_authority":False},"summary":{"historical_generation_records":historical["generation_records"],"historical_unique_candidate_ids":historical["unique_candidate_ids"],"failure_lessons":len(lessons),"independent_transaction_survivors":0,"ouroboros_anchor_survivors":0,"problem_gate_pass":0,"active_research_items_before":0,"active_research_items_after":0},"scientific_authority":False,"authority":{"problem_gate":False,"researchitem":False,"method":False,"experiment":False,"gpu":False}}
    payload["cycle_sha256"] = _sha({k:v for k,v in payload.items() if k != "generated_at"}); errors = validate_discovery_cycle(payload); payload["lint"] = {"status":"PASS" if not errors else "FAIL","errors":errors,"scientific_authority":False}; return payload


def load_discovery_cycle(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    try: payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError: return {}
    except json.JSONDecodeError as exc: raise ValueError(f"invalid longitudinal discovery cycle JSON:{path}") from exc
    errors = validate_discovery_cycle(payload)
    if errors: raise ValueError("invalid longitudinal discovery cycle: "+";".join(errors))
    return payload


def write_discovery_cycle(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    payload = build_discovery_cycle()
    if (payload.get("lint") or {}).get("status") != "PASS": raise ValueError("refusing to persist invalid longitudinal discovery cycle")
    json_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); js_path.write_text("window.LONGITUDINAL_SAFETY_DISCOVERY_CYCLE = "+json.dumps(payload,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8"); return payload


if __name__ == "__main__":
    result=write_discovery_cycle(); print(json.dumps({"status":result["status"],"summary":result["summary"],"cycle_sha256":result["cycle_sha256"]},ensure_ascii=False,sort_keys=True))
