from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-ai-premortem.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-ai-premortem.js"

POLICY = {
    "schema_version": "1.0",
    "ai_is_advisory_only": True,
    "missing_reviewer_is_not_pass": True,
    "reviewer_vote_cannot_authorize_scientific_validation": True,
    "review_disagreement_compiles_to_cheapest_machine_gate": True,
    "environment_feasibility_may_run_before_scientific_local_validation": True,
    "full_experiment_requires_later_explicit_authorization": True,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_paper_first_ai_premortem() -> dict[str, Any]:
    reviewers = [
        {
            "reviewer": "web-gpt-current-source-review",
            "status": "missing",
            "error": "browser-upstream-502",
            "verdict": None,
        },
        {
            "reviewer": "deepseek-v4-pro",
            "status": "complete",
            "verdict": "STOP_PAPER_PROBLEM",
            "confidence": "high",
            "finding": (
                "The surviving proposal risks being a direct composition of CMI endpoint memory intervention, "
                "CAR/CausalFlow trajectory intervention, and a context classifier; replay feasibility and causal "
                "transport assumptions are not yet established."
            ),
            "required_checks": [
                "exact prefix replay with raw hashes",
                "mediator action admissibility under the counterfactual branch",
                "memory-free continuation consistency/support",
                "branch-effect variance/power before certificate training",
            ],
        },
        {
            "reviewer": "glm-5.2",
            "status": "complete",
            "verdict": "ADVANCE_TO_ENVIRONMENT_FEASIBILITY",
            "confidence": 0.72,
            "finding": (
                "A narrow transportability/identifiability question may survive, but only after exact replay, "
                "null-policy, admissibility, leakage, same-information-baseline, and power checks."
            ),
            "required_checks": [
                "exact prefix replay >=20 branch points / >=4 families",
                "null same-action zero-contrast sanity check",
                "pre-treatment/context leakage audit",
                "same-information CMI+CAR/CausalFlow baseline feature/budget equality",
                "C2/C3 power and held-out-context audit",
            ],
        },
        {
            "reviewer": "doubao-seed-evolving-tiebreak-diagnostic",
            "status": "missing",
            "error": "connector-upstream-502",
            "verdict": None,
            "role": "extra diagnostic only; does not replace missing Web GPT",
        },
    ]
    synthesis = {
        "decision": "ADVANCE_ENVIRONMENT_FEASIBILITY_ONLY",
        "paper_problem_status": "novelty-survives-narrowly-but-disputed",
        "reason": (
            "Primary-source collision review leaves a narrow mediated-effect transportability axis, while independent "
            "reviewers disagree on whether it is paper-worthy. The cheapest decision-changing action is therefore an "
            "environment-only replay/consistency gate. This gate cannot establish novelty or authorize C2/C3."
        ),
        "required_machine_checks": [
            {
                "key": "prefix-replay-exactness",
                "requirement": ">=20 branch points across >=4 ALFWorld task families; replay the frozen 5-step action prefix twice from fresh reset and require exact equality of observation, reward, done, admissible commands, and available state facts at every step; persist hashes.",
                "failure_action": "REVISE_PAPER_DESIGN_OR_STOP",
            },
            {
                "key": "mediator-admissibility",
                "requirement": "At a candidate branch point, both observed divergent actions must be admissible from the reconstructed common state; otherwise that unit cannot identify the controlled mediator contrast.",
                "failure_action": "EXCLUDE_UNIT_AND_RECHECK_SUPPORT; systematic failure => STOP_CURRENT_MEDIATOR_DEFINITION",
            },
            {
                "key": "null-same-action",
                "requirement": "For the same replayed branch state and same forced action on both arms, the downstream deterministic continuation must yield zero outcome contrast.",
                "failure_action": "STOP_CAUSAL_REPLAY_INSTRUMENT",
            },
            {
                "key": "memory-free-continuation-consistency",
                "requirement": "The frozen memory-free continuation policy must execute both forced-action branches without undefined state/action support or treatment-dependent policy changes.",
                "failure_action": "REVISE_ESTIMAND_BEFORE_C2",
            },
        ],
        "paper_design_revisions_before_c2": [
            "Call the branch estimand a controlled mediator-action contrast, not a natural indirect effect, unless stronger mediation assumptions are proved.",
            "Define context C using pre-treatment or externally frozen variables only; post-treatment context features are forbidden in the transport certificate.",
            "Make CMI+CAR/CausalFlow+context-family+first-divergence the composed strongest baseline with identical replay units, features, and budget.",
            "State explicit overlap/consistency assumptions for the two mediator actions and the memory-free continuation policy.",
            "Pre-register power/minimum-support for C2 and C3 before opening branch-effect outcomes.",
        ],
        "environment_feasibility_authorized": True,
        "local_scientific_validation_authorized": False,
        "certificate_training_authorized": False,
        "full_experiment_authorized": False,
        "next_gate": "run environment-only replay feasibility; then return to paper-design/AI adjudication",
    }
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "paper_id": "trajectory-mediated-memory-effect-transport",
        "policy": POLICY,
        "reviewers": reviewers,
        "summary": {
            "reviewers_requested": len(reviewers),
            "reviewers_complete": sum(r["status"] == "complete" for r in reviewers),
            "reviewers_missing": sum(r["status"] == "missing" for r in reviewers),
            "stop_verdicts": sum(r.get("verdict") == "STOP_PAPER_PROBLEM" for r in reviewers),
            "environment_feasibility_verdicts": sum(r.get("verdict") == "ADVANCE_TO_ENVIRONMENT_FEASIBILITY" for r in reviewers),
            "environment_feasibility_authorized": True,
            "local_scientific_validation_authorized": False,
            "full_experiment_authorized": False,
        },
        "synthesis": synthesis,
    }


def write_paper_first_ai_premortem(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_paper_first_ai_premortem()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_AI_PREMORTEM = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_paper_first_ai_premortem(), ensure_ascii=False, indent=2))
