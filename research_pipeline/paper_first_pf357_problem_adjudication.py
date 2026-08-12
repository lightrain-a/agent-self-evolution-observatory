from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_idea_incubation import build_paper_first_idea_incubation

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-pf357-problem-adjudication.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-pf357-problem-adjudication.js"

REVIEWS = {
    "initial_deepseek": {"model":"deepseek-v4-pro-260425","raw_sha256":"b9fc4f0329f587281049beeb067b60da0853e06466908677174d22931b08bc9e","path":"/data/wyt/agent-evolution-paper-first-reviews/pf357-final-20260813/deepseek-initial.json","authority":"advisory-only"},
    "initial_glm": {"model":"glm-5-2-260617","raw_sha256":"00528d4b54b0d204f5273a84dcac28550cd32faf4116a35e32b4f219946e4d94","path":"/data/wyt/agent-evolution-paper-first-reviews/pf357-final-20260813/glm-initial.json","authority":"advisory-only"},
    "pf3_final_deepseek": {"model":"deepseek-v4-pro-260425","verdict":"STOP_STANDALONE_PROBLEM","confidence":0.94,"raw_sha256":"b0df58ccc093e654bf826b6243ff0db49e0ed4641ea7206ce4969da7877d8f03","path":"/data/wyt/agent-evolution-paper-first-reviews/pf357-final-20260813/pf3-deepseek-final.json","authority":"advisory-only"},
    "pf3_final_glm": {"model":"glm-5-2-260617","verdict":"STOP_STANDALONE_PROBLEM","confidence":"high","raw_sha256":"f16ed3c6b77d5d3ab4ad128bf6966a7f1bd34eaae5fc14caa64b2c8b772ac340","path":"/data/wyt/agent-evolution-paper-first-reviews/pf357-final-20260813/pf3-glm-final.json","authority":"advisory-only"},
}

ROWS = (
    {
        "id":"PF-3",
        "decision":"STOP_PF3_STANDALONE_MERGE_COMPRESSION_LIFECYCLE_CONTROL",
        "paper_problem_status":"TERMINATED_AFTER_RATE_DISTORTION_COLLISION",
        "strongest_collisions":[
            "Experience Compression Spectrum (arXiv:2604.15877) already defines memory/skill/rule levels and explicitly names adaptive cross-level compression as the missing diagonal.",
            "DeMem / Remember the Decision, Not the Description (arXiv:2605.10870) gives a decision-centric rate-distortion frontier, exact forgetting boundary, and certified online splitting only when data show decision conflict.",
            "Skill-to-LoRA, Skill-SD, Metric-Freedom adaptive distillation, MemSkill, and ReuseRL cover internalization, selective distillation, evolving memory skills, and compression/generalization tradeoffs.",
        ],
        "why_stop":"The proposed reversibility option value / rare-case retention gate is expressible as adaptive compression, rate-distortion/value-of-information, or model-selection/optimal-stopping over the already named compression spectrum. Multi-level irreversibility adds constraints but no irreducible scientific object.",
        "surviving_system_role":"compression-lifecycle-control: keep reversible representations until decision-relevant distinctions are certified safe to compress; use as systems policy, not a standalone paper claim.",
        "prohibited_rescues":["new compression metric","new level in the hierarchy","different adapter type","more rare-case probes","renaming rate-distortion as reversibility option value"],
    },
    {
        "id":"PF-5",
        "decision":"STOP_PF5_STANDALONE_MERGE_DIFFERENTIAL_VERIFICATION_COMPONENT",
        "paper_problem_status":"TERMINATED_AS_AGENT_DOMAIN_TRANSFER_OF_DIFFERENTIAL_TESTING",
        "strongest_collisions":[
            "DiffTestGen (arXiv:2607.16024) is change-directed LLM test generation specifically to expose behavioral differences between old/new program versions and feed them to regression detection.",
            "DiffSpec and Mokav already target behavior-differentiating tests; Self-Harness, SEAL, and TDAD provide held-out/sealed/mutation-based agent verification.",
        ],
        "why_stop":"Incumbent-versus-candidate state-action divergence is the closed-loop-agent instantiation of differential behavioral testing. A dynamic state frontier changes the domain geometry, not the underlying problem class.",
        "surviving_system_role":"differential-verification: use update-induced behavior divergence to prioritize verification budget when useful, but treat it as an engineering component subordinate to independent truth and endpoint-headroom rules.",
        "prohibited_rescues":["agent-specific test generator","state-action divergence metric","different environment","more adversarial sampling","calling differential tests verification obligations"],
    },
    {
        "id":"PF-7",
        "decision":"STOP_PF7_STANDALONE_MERGE_EVIDENCE_IMPACT_REVALIDATION_COMPONENT",
        "paper_problem_status":"TERMINATED_AS_CHANGE_IMPACT_AND_REGRESSION_SELECTION_TRANSFER",
        "strongest_collisions":[
            "Safe regression-test selection/change-impact analysis already selects affected tests after changes using dependency information.",
            "NameRTS (arXiv:2605.25356) formulates fine-grained dependency analysis as graph reachability and achieves near-safe affected-test selection for Python changes.",
            "AHE, MOSS, Self-Harness, and SEAL already bind edits to verification/replay/external audit in agent systems.",
        ],
        "why_stop":"Typing graph nodes as claims, traces, assumptions, evaluator contracts, environment facts, and artifacts does not change the underlying dependency-reachability/selective-revalidation problem. A semantic evidence graph is still change-impact analysis unless it introduces a new non-graph validity semantics.",
        "surviving_system_role":"evidence-impact-revalidation: maintain dependency scope and selectively invalidate/revalidate affected evidence as a runtime/governance optimization, not a standalone paper thesis.",
        "prohibited_rescues":["more evidence node types","semantic embeddings on graph edges","LLM-generated dependencies","different graph-cut heuristic","agent provenance terminology"],
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_pf357_problem_adjudication() -> dict[str, Any]:
    incubation=build_paper_first_idea_incubation(); existing={r["id"] for r in incubation.get("candidates") or []}
    if not {"PF-3","PF-5","PF-7"}.issubset(existing): raise ValueError("PF-3/PF-5/PF-7 missing from incubation")
    rows=[]
    for template in ROWS:
        row=dict(template)
        row["authority"]={"paper_problem_active":False,"paper_design_authorized":False,"method_design_authorized":False,"experiment_blueprint_authorized":False,"local_validation_authorized":False,"p0_authorized":False,"gpu_authorized":False,"full_experiment_authorized":False,"premature_pf_f0_used":False,"automatic_replacement_problem_authorized":False}
        rows.append(row)
    return {
        "schema_version":"1.0","generated_at":_now(),"review_id":"paper-first-pf357-final-20260813",
        "policy":{"domain_transfer_is_not_novelty":True,"survey_open_problem_does_not_imply_method_novelty":True,"same_information_baseline_precedes_experiment":True,"ai_is_advisory_only":True,"local_validation_authorized":False},
        "reviews":REVIEWS,
        "summary":{"reviewed":3,"stopped_standalone":3,"paper_design_authorized":0,"local_validation_authorized":0,"p0_authorized":0},
        "rows":rows,
        "portfolio_decision":"STOP PF-3/PF-5/PF-7 as standalone paper problems; merge their useful mechanisms into compression lifecycle, differential verification, and evidence-impact revalidation system controls.",
        "next_action":"The nine-item Paper-first incubation batch is now fully adjudicated. Do not create experiments from this batch. Return to fresh problem discovery using the strengthened collision/same-information rules and reuse these three merged controls in the research system.",
    }


def validate_pf357_problem_adjudication(state:dict[str,Any])->list[str]:
    errors=[]; rows=state.get("rows") or []
    if len(rows)!=3: errors.append("expected three final rows")
    if any(not str(r.get("decision") or "").startswith("STOP_PF") for r in rows): errors.append("all PF-3/5/7 must be standalone STOP")
    if (state.get("summary") or {}).get("stopped_standalone")!=3: errors.append("summary stop count mismatch")
    if (state.get("policy") or {}).get("local_validation_authorized") is not False: errors.append("local validation must remain locked")
    for r in rows:
        if any(v is not False for v in (r.get("authority") or {}).values()): errors.append(f"{r.get('id')} downstream authority must remain false")
    if any(v.get("authority")!="advisory-only" for v in (state.get("reviews") or {}).values()): errors.append("AI reviews must remain advisory")
    return errors


def write_pf357_problem_adjudication(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=build_pf357_problem_adjudication(); errors=validate_pf357_problem_adjudication(state)
    if errors: raise ValueError("Invalid PF357 adjudication:\n- "+"\n- ".join(errors))
    json_path.parent.mkdir(parents=True,exist_ok=True); json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); js_path.write_text("window.PAPER_FIRST_PF357_PROBLEM_ADJUDICATION = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8"); return state

if __name__=="__main__": print(json.dumps(write_pf357_problem_adjudication(),ensure_ascii=False))
