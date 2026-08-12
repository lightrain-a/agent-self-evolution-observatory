from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_design_adjudication import build_paper_first_design_adjudication

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-pf1-problem-adjudication.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-pf1-problem-adjudication.js"

REVIEWERS = {
    "deepseek_v4_pro": {
        "requested_model": "deepseek-v4-pro",
        "resolved_model": "deepseek-v4-pro-260425",
        "verdict": "STOP_STANDALONE_PROBLEM",
        "confidence": 0.94,
        "raw_backend_path": "/data/wyt/agent-evolution-paper-first-reviews/pf1-final-20260813/deepseek-v4-pro.json",
        "raw_sha256": "4d5d6a1f275a1b9f852d6283fc3d05ed1311004188ec065fdf70feb75e670d52",
        "authority": "advisory-only",
    },
    "glm_5_2": {
        "requested_model": "glm-5.2",
        "resolved_model": "glm-5-2-260617",
        "verdict": "STOP_STANDALONE_PROBLEM",
        "confidence": 0.95,
        "raw_backend_path": "/data/wyt/agent-evolution-paper-first-reviews/pf1-final-20260813/glm-5.2.json",
        "raw_sha256": "89c644d33fca1786008bb3fa96a5e1b96930f911b55f4b062ed57e80b1a8390a",
        "authority": "advisory-only",
    },
}

PRIMARY_COLLISIONS = [
    {"ref": "arXiv:2605.09315", "title": "Do Self-Evolving Agents Forget? Capability Degradation and Preservation in Lifelong LLM Agent Adaptation", "role": "capability erosion/preservation across workflow, skill/tool, model, and memory self-evolution"},
    {"ref": "arXiv:2604.15414", "title": "Beyond Single-Model Optimization: Preserving Plasticity in Continual Reinforcement Learning", "role": "source/retained states can be poor starting points for future adaptation; source-optimal is not necessarily transfer-optimal"},
    {"ref": "arXiv:2602.07755", "title": "Learning to Continually Learn via Meta-learning Agentic Memory Designs", "role": "meta-learns executable agent memory designs so agents become better continual learners"},
    {"ref": "arXiv:2604.20714", "title": "Learning to Evolve: A Self-Improving Framework for Multi-Agent Systems via Textual Parameter Graph Optimization", "role": "meta-optimizer learns from optimization history to become a better future agent optimizer"},
    {"ref": "arXiv:2604.15034", "title": "Autogenesis: A Self-Evolving Agent Protocol", "role": "separates versioned persistent resources from the closed-loop operator that proposes, assesses, and commits evolution"},
    {"ref": "arXiv:2602.00359", "title": "Position: Agentic Evolution is the Path to Evolving LLMs", "role": "autonomous evolver over persistent system state"},
    {"ref": "arXiv:2605.22505", "title": "Towards Direct Evaluation of Harness Optimizers via Priority Ranking", "role": "intermediate optimizer choices can hinder multi-step harness optimization; direct optimizer quality predicts later improvement"},
    {"ref": "arXiv:2005.06224", "title": "Novelty Search makes Evolvability Inevitable", "role": "evolvability is already a property of current representations under evolutionary variation/search"},
    {"ref": "arXiv:2306.09849", "title": "On Evolvability and Behavior Landscapes in Neuroevolutionary Divergent Search", "role": "representation/behavior landscapes and operator-dependent evolvability are already formalized"},
    {"ref": "arXiv:2602.07659", "title": "Continuous Program Search", "role": "program representation/locality and mutation geometry affect search efficiency under a fixed evolutionary optimizer"},
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_pf1_problem_adjudication() -> dict[str, Any]:
    design = build_paper_first_design_adjudication()
    pf1 = next(row for row in design["rows"] if row["id"] == "PF-1")
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "incubation_id": "PF-1",
        "paper_id": "evolvability-debt-under-persistent-agent-updates",
        "prior_design_verdict": pf1["verdict"],
        "decision": "STOP_PF1_STANDALONE_PROBLEM_MERGE_EVOLVABILITY_AUDIT",
        "paper_problem_status": "TERMINATED_AS_STANDALONE_AFTER_FINAL_COLLISION_REVIEW",
        "reason": (
            "After successively narrowing PF-1 from generic future learnability to fixed-evolver state compatibility and finally to discrete artifact reachable-set/search-geometry effects, "
            "the remaining claim is still expressible using established plasticity, meta-learning, evolvability, and representation/search-locality concepts. The only residual distinction is the agent-artifact domain."
        ),
        "failed_novelty_escape_routes": [
            {"route": "future-learnability AUC under fixed update budget", "collision": "continual-learning plasticity / TeLAPA", "status": "closed"},
            {"route": "fixed autonomous evolver E applied to matched R0/R1", "collision": "fixed-rule future plasticity / transfer-optimality", "status": "closed"},
            {"route": "non-weight prompt-memory-workflow-code surfaces", "collision": "domain transfer alone; CPE already spans these persistent agent surfaces", "status": "closed"},
            {"route": "state-operator compatibility / reachable-set contraction", "collision": "general evolvability and representation/search-landscape theory; Continuous Program Search directly studies representation-locality effects under a fixed optimizer", "status": "closed"},
        ],
        "same_information_reduction": {
            "statement": "Given the same current state, frozen future task distribution, frozen adaptation/evolution operator, and future budget, PF-1's proposed outcome is a future-adaptation/evolvability functional already representable by standard plasticity/evolvability baselines.",
            "irreducible_agent_only_variable": None,
            "domain_transfer_is_sufficient_novelty": False,
        },
        "reviewers": REVIEWERS,
        "review_synthesis": {
            "agreement": "Both independent reviewers conclude that no formal object survived once continual-learning plasticity and operator-dependent evolvability/search-locality work were included.",
            "ai_is_authority": False,
        },
        "primary_collisions": PRIMARY_COLLISIONS,
        "what_survives": {
            "scientific_lesson": "Preserving current capability and old-task retention does not imply preserving future update responsiveness; this remains a useful cross-cutting systems audit.",
            "engineering_rule": "For long-horizon self-evolution, optionally report fixed-evolver future-update responsiveness as a diagnostic dimension when the cost is justified, but do not treat it as a standalone novel method/problem.",
            "failure_asset": "An attractive Agent-specific term can still collapse to a mature cross-domain scientific object; require the irreducible formal object before implementation.",
        },
        "what_is_closed": [
            "Future-Learnability Probe Gate as a standalone method",
            "evolvability debt as a renamed generic plasticity metric",
            "non-parametric agent surfaces as novelty by themselves",
            "reachable-set/search-locality formulation under a fixed evolver as a standalone ICLR problem without an additional irreducible object",
            "automatic transition to method design, experiment blueprint, local validation, P0, or GPU",
        ],
        "revival_rule": (
            "PF-1 may only be revived if a new primary-source review identifies a genuinely agent-specific formal object that cannot be expressed as future plasticity, meta-learning initial-state quality, operator-dependent evolvability, representation/search locality, or optimizer quality. "
            "A new metric, surface, model, task domain, or probe budget is insufficient."
        ),
        "authority": {
            "paper_problem_active": False,
            "method_design_authorized": False,
            "experiment_blueprint_authorized": False,
            "local_validation_authorized": False,
            "p0_authorized": False,
            "gpu_authorized": False,
            "full_experiment_authorized": False,
            "premature_pf_f0_used": False,
            "automatic_replacement_problem_authorized": False,
        },
        "next_action": "Archive PF-1 standalone. Continue paper-first review with unresolved PF-3/PF-5/PF-7 rather than attempting another PF-1 terminology or substrate rescue.",
    }


def validate_pf1_problem_adjudication(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("decision") != "STOP_PF1_STANDALONE_PROBLEM_MERGE_EVOLVABILITY_AUDIT": errors.append("PF-1 standalone STOP missing")
    if len(state.get("failed_novelty_escape_routes") or []) < 4: errors.append("PF-1 collision sequence incomplete")
    if (state.get("same_information_reduction") or {}).get("irreducible_agent_only_variable") is not None: errors.append("PF-1 should not claim an irreducible agent-only variable")
    reviewers = state.get("reviewers") or {}
    if set(reviewers) != {"deepseek_v4_pro", "glm_5_2"}: errors.append("PF-1 requires two independent advisory reviews")
    if any(row.get("verdict") != "STOP_STANDALONE_PROBLEM" for row in reviewers.values()): errors.append("PF-1 reviewers did not converge on STOP")
    if any(row.get("authority") != "advisory-only" for row in reviewers.values()): errors.append("AI reviews must remain advisory-only")
    authority = state.get("authority") or {}
    for key in ("paper_problem_active", "method_design_authorized", "experiment_blueprint_authorized", "local_validation_authorized", "p0_authorized", "gpu_authorized", "full_experiment_authorized", "premature_pf_f0_used", "automatic_replacement_problem_authorized"):
        if authority.get(key) is not False: errors.append(f"{key} must remain false")
    return errors


def write_pf1_problem_adjudication(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_pf1_problem_adjudication()
    errors = validate_pf1_problem_adjudication(state)
    if errors:
        raise ValueError("Invalid PF-1 problem adjudication:\n- " + "\n- ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_PF1_PROBLEM_ADJUDICATION = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_pf1_problem_adjudication(), ensure_ascii=False))
