from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-fresh-saturation.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-fresh-saturation.js"

REDUCTION_PATTERNS: tuple[dict[str, Any], ...] = (
    {"key":"update-order-path-dependence","mature_theories":["interaction effects","co-evolutionary dynamics","non-stationary online learning"],"veto":"Do not promote update-order/non-commutativity claims unless a formal object survives those same-information theories."},
    {"key":"snapshot-validity-horizon","mature_theories":["non-stationary model selection","optimal stopping","adaptive validation"],"veto":"A time-varying best checkpoint/half-life is not a new problem by itself."},
    {"key":"feedback-view-intransitivity","mature_theories":["multi-objective optimization","preference cycles","social choice / ranking"],"veto":"Different validation/test/robustness rankings are not novel without a non-reducible decision object."},
    {"key":"operator-closure-reachability","mature_theories":["automata reachability","typed operator algebra","self-modifying program semantics"],"veto":"Versioned agent-resource operator closure is not novel when the protocol already defines the state/operator algebra."},
    {"key":"stream-instability","mature_theories":["dynamical systems","Lyapunov stability","non-stationary learning"],"veto":"Naming a self-evolution stream Lyapunov exponent is domain transfer unless the dynamics add a new structural constraint."},
    {"key":"self-generated-supervision-information-limit","mature_theories":["recursive self-training collapse","closed-loop self-evolution generalization gap","information bottleneck"],"veto":"An information ceiling for self-generated supervision is already occupied unless a distinct information source/constraint changes the theorem."},
    {"key":"validation-filter-information-loss","mature_theories":["Bayesian optimization","information bottleneck","selective sampling"],"veto":"Sparse validation/filtering tradeoffs are not a new scientific object."},
    {"key":"verifier-exogeneity","mature_theories":["adaptive data analysis","conditional independence / d-separation","co-training correlated errors","recursive self-gating collapse"],"veto":"Shared evaluator-policy ancestry is not new unless same-information causal/statistical dependence models cannot express the prediction."},
    {"key":"evolution-induced-task-non-equivalence","mature_theories":["inter-MDP generalized bisimulation","MDP homomorphism","behavioral equivalence"],"veto":"Pre/post scaffold semantics comparability is domain transfer when generalized inter-MDP equivalence solves the same question."},
    {"key":"persistent-update-vs-test-time-compute","mature_theories":["amortized inference","test-time scaling","search-vs-learning evaluation"],"veto":"Persistent update necessity is already an explicit harness/skill evaluation question; require a new structural prediction, not another comparison."},
    {"key":"typed-epistemic-authority","mature_theories":["filtered/source-sensitive belief revision","Bayesian source-reliability networks","dynamic epistemic/justification logic"],"veto":"NO-AUTHORITY evidence transitions are not novel if typed credibility partitions or conditional independence reproduce the same belief update."},
    {"key":"model-scaffold-enactability","mature_theories":["cross-model prompt transfer","instruction following / compliance","model-artifact compatibility"],"veto":"A harness/skill that is valid but not activated or faithfully followed by a target model is not a new object unless it escapes cross-model prompt/artifact compatibility under the same information."},
    {"key":"artifact-uptake-after-retrieval","mature_theories":["retrieval-versus-utilization diagnostics","instruction following","externalized skill execution"],"veto":"Retrieved experience that fails to change behavior is already a utilization/uptake bottleneck; require a new causal object beyond retrieval and instruction-following decomposition."},
    {"key":"environment-mediated-history","mature_theories":["POMDP state sufficiency","causal mediation through physical state","state-conditioned embodied memory"],"veto":"Past actions affecting future behavior through the current world state are not evidence of internal memory; this distinction is mature state/mediation theory unless a new embodied-only prediction survives."},
    {"key":"multimodal-procedural-compression","mature_theories":["multimodal representation","rate-distortion / information preservation","visual grounding and domain adaptation"],"veto":"Visual details that cannot be compressed into text are not a new self-evolution problem when multimodal skills already preserve state cards/keyframes and rate-distortion captures information loss."},
)

DRAFTS: tuple[dict[str, Any], ...] = (
    {"id":"G1","title":"Non-Commutativity of Update Trajectories Under Live Evaluator Drift","decision":"STOP_REDUCTION","reduction":"update-order-path-dependence"},
    {"id":"G2","title":"Temporal Validity Kernel of Intermediate Harness Snapshots","decision":"STOP_REDUCTION","reduction":"snapshot-validity-horizon"},
    {"id":"G3","title":"Topological Torsion in Skill Memory Co-Evolution","decision":"STOP_REDUCTION","reduction":"update-order-path-dependence"},
    {"id":"G4","title":"Information Imbalance Between Step-Level and Multi-Step Optimizer Rankings","decision":"STOP_REDUCTION","reduction":"sequential ranking / credit assignment"},
    {"id":"G5","title":"Intransitivity of Feedback Views Under Scaling","decision":"STOP_REDUCTION","reduction":"feedback-view-intransitivity"},
    {"id":"G6","title":"Algebraic Closure of Versioned Resource Interfaces","decision":"STOP_REDUCTION","reduction":"operator-closure-reachability"},
    {"id":"G7","title":"Lyapunov Instability of Sequential Evolution Streams","decision":"STOP_REDUCTION","reduction":"stream-instability"},
    {"id":"G8","title":"Non-Isomorphic Failure Embeddings Across Memory and Skill Co-Evolution","decision":"STOP_REDUCTION","reduction":"representation/topology relabeling without decision consequence"},
    {"id":"G9","title":"Information Horizon of In-Distribution Process Supervision","decision":"STOP_REDUCTION","reduction":"self-generated-supervision-information-limit"},
    {"id":"G10","title":"Sparse Search Validation Filter Information Loss","decision":"STOP_REDUCTION","reduction":"validation-filter-information-loss"},
    {"id":"X1","title":"Verifier Endogeneity / Exogeneity Budget","decision":"STOP_REDUCTION","reduction":"verifier-exogeneity"},
    {"id":"X2","title":"Evolution-Induced Task Non-Equivalence","decision":"STOP_REDUCTION","reduction":"evolution-induced-task-non-equivalence"},
    {"id":"X3","title":"Persistent-Update Necessity / Compute Substitutability","decision":"STOP_COLLISION","reduction":"persistent-update-vs-test-time-compute"},
    {"id":"X4","title":"Epistemic Authority of Autonomous Experiment Outcomes","decision":"STOP_REDUCTION","reduction":"typed-epistemic-authority"},
    {"id":"X5","title":"Model-Scaffold Enactability Across Policy Models","decision":"STOP_REDUCTION","reduction":"model-scaffold-enactability"},
    {"id":"X6","title":"Persistent Artifact Uptake After Successful Retrieval","decision":"STOP_REDUCTION","reduction":"artifact-uptake-after-retrieval"},
    {"id":"X7","title":"Environment-Mediated History Versus Internal Embodied Memory","decision":"STOP_REDUCTION","reduction":"environment-mediated-history"},
    {"id":"X8","title":"Irreducible Visual Detail in Multimodal Procedural Consolidation","decision":"STOP_REDUCTION","reduction":"multimodal-procedural-compression"},
)

POLICY: dict[str, Any] = {
    "schema_version":"1.0",
    "problem_first_not_method_first":True,
    "mathematical_renaming_is_not_novelty":True,
    "mature_domain_transfer_is_hard_veto":True,
    "same_information_theory_baseline_required":True,
    "latest_primary_source_collision_required":True,
    "endpoint_headroom_required_before_interpreting_terminal_outcomes":True,
    "invalid_or_malformed_ai_generation_has_zero_scientific_authority":True,
    "zero_survivors_is_valid_and_preferred_to_forced_shortlist":True,
    "local_validation_authorized":False,
    "p0_authorized":False,
    "gpu_authorized":False,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_fresh_saturation_state() -> dict[str, Any]:
    return {
        "schema_version":"1.0",
        "generated_at":_now(),
        "review_id":"fresh-problem-saturation-20260813",
        "policy":POLICY,
        "summary":{
            "drafts_reviewed":len(DRAFTS),
            "survivors":0,
            "stopped":len(DRAFTS),
            "reduction_patterns":len(REDUCTION_PATTERNS),
            "local_validation_authorized":0,
            "p0_authorized":0,
        },
        "drafts":[dict(row) for row in DRAFTS],
        "reduction_patterns":[dict(row) for row in REDUCTION_PATTERNS],
        "generator_revision":{
            "old_failure":"Free-form generators produced mathematically named versions of mature problems and malformed long JSON; formatting repair was treated as advisory-only and never as scientific evidence.",
            "new_rule":"Start from a documented contradiction between recent primary-source results; name the two strongest mature theories first; a candidate is generated only if an exact prediction remains that both theories cannot express under the same information.",
            "required_fields":["empirical contradiction","irreducible object","mature-theory non-reducibility","same-information baseline","cheapest problem falsifier","endpoint headroom"],
        },
        "decision":"NO_FRESH_SURVIVOR_CURRENT_SCAN",
        "next_action":"Continue contradiction-first literature discovery in less-saturated subdomains; do not create methods, experiments, P0 entries, or GPU work until a problem survives the mature-theory veto.",
    }


def write_fresh_saturation_state(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state=build_fresh_saturation_state(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_FRESH_SATURATION = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_fresh_saturation_state(),ensure_ascii=False))
