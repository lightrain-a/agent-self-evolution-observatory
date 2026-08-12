from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_pf2_method_design import build_pf2_method_design

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-pf2-method-adjudication.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-pf2-method-adjudication.js"

REVIEWERS = {
    "deepseek_v4_pro": {
        "requested_model": "deepseek-v4-pro",
        "resolved_model": "deepseek-v4-pro-260425",
        "verdict": "REVISE_METHOD_DESIGN",
        "confidence": 0.92,
        "raw_backend_path": "/data/wyt/agent-evolution-paper-first-reviews/pf2-method-20260813/deepseek-v4-pro.json",
        "raw_sha256": "90ddebf42d044fb7919d9f54d614f81e30bf0c8c6d03edafc3f66c0f1cda060c",
        "authority": "advisory-only",
    },
    "glm_5_2": {
        "requested_model": "glm-5.2",
        "resolved_model": "glm-5-2-260617",
        "verdict": "STOP_METHOD_THESIS",
        "confidence": 0.95,
        "raw_backend_path": "/data/wyt/agent-evolution-paper-first-reviews/pf2-method-20260813/glm-5.2.json",
        "raw_sha256": "b044bc0f8c8c07ae90ff1db9db0721946b96e5706f4e9b0ab48d28519e4fc5d6",
        "authority": "advisory-only",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_pf2_method_adjudication() -> dict[str, Any]:
    method = build_pf2_method_design()
    generic = next(row for row in method["same_information_baselines"] if row["name"] == "generic-partial-identification")
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "paper_id": method["paper_id"],
        "incubation_id": "PF-2",
        "reviewed_method": method["method_name"],
        "decision": "STOP_CURRENT_RSIC_METHOD_THESIS_KEEP_PROBLEM_PROTOCOL",
        "method_status": "TERMINATED_BEFORE_EXPERIMENT_BLUEPRINT",
        "paper_problem_status": "SURVIVES_AS_PROBLEM_AND_EVALUATION_PROTOCOL_ONLY",
        "reason": (
            "RSIC's IDENTIFIED/UNIDENTIFIABLE/PROBE_MORE states are currently in one-to-one correspondence with generic partial identification and set-refinement over the same compatible model set, "
            "repair-surface hypotheses, intervention table, and probe outcomes. The agent-surface semantics do not yet create an irreducible inference object or guarantee."
        ),
        "same_information_stop": {
            "baseline": generic["name"],
            "same_information": generic["access"],
            "equivalence": "same compatible set and minimal-surface functional imply identical unique-certification versus abstention decisions",
            "stop_condition_from_method_design": "STOP standalone method novelty if generic partial-identification under the same formal objects yields the same certificate states and decision guarantees.",
            "triggered": True,
        },
        "reviewers": REVIEWERS,
        "review_synthesis": {
            "deepseek": "No irreducible method novelty survives if C(E) and A*(M) are shared with generic partial identification; revise only if a new structural guarantee changes decisions under the same evidence.",
            "glm": "Current method thesis should stop because RSIC is isomorphic to standard partial identification/set refinement under identical causal variables and probe outcomes.",
            "agreement": "Both reviewers independently identify generic partial-identification equivalence as the load-bearing failure.",
            "ai_is_authority": False,
        },
        "what_survives": {
            "problem": "A failure source/responsibility signal need not identify where a persistent agent should be repaired; repair-surface non-identifiability remains a valid scientific question.",
            "protocol": "A cross-surface intervention table with explicit abstention/partial-identification evaluation remains useful as an evaluation protocol or diagnostic benchmark.",
            "collision_memory": "Diagnosis Is Not Prescription and HarnessFix are mandatory nearest-work baselines for any future revival.",
        },
        "what_is_closed": [
            "RSIC as a standalone method contribution",
            "IDENTIFIED/UNIDENTIFIABLE/PROBE_MORE state naming as method novelty",
            "generic information-gain or set-elimination probing as method novelty",
            "a new direct router, classifier, CATE ranker, or renamed generic partial-identification rescue under the same problem formulation",
        ],
        "revival_requirements": [
            "A future method revival must introduce a repair-surface-specific structural assumption, theorem, or guarantee that changes decisions relative to generic partial identification given the exact same evidence and structural inputs.",
            "The difference cannot be merely a different feature representation, classifier, active-probe heuristic, surface taxonomy, or additional metric.",
            "Any proposed revival must rerun primary-source collision search and a same-information method premortem before an experiment blueprint is written.",
        ],
        "authority": {
            "method_thesis_active": False,
            "experiment_blueprint_authorized": False,
            "local_validation_authorized": False,
            "p0_authorized": False,
            "gpu_authorized": False,
            "full_experiment_authorized": False,
            "premature_pf_f0_used": False,
            "new_method_auto_authorized": False,
        },
        "next_action": "Archive PF-2 current method thesis and move paper-first effort to the next unresolved problem boundary. PF-1 evolvability-debt is next; no PF-2 experiment blueprint or local validation may be compiled.",
    }


def validate_pf2_method_adjudication(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("decision") != "STOP_CURRENT_RSIC_METHOD_THESIS_KEEP_PROBLEM_PROTOCOL": errors.append("PF-2 RSIC stop decision missing")
    if state.get("paper_problem_status") != "SURVIVES_AS_PROBLEM_AND_EVALUATION_PROTOCOL_ONLY": errors.append("PF-2 problem/protocol preservation missing")
    if not (state.get("same_information_stop") or {}).get("triggered"): errors.append("same-information STOP must be triggered")
    reviewers = state.get("reviewers") or {}
    if set(reviewers) != {"deepseek_v4_pro", "glm_5_2"}: errors.append("two independent reviewers required")
    if any(row.get("authority") != "advisory-only" for row in reviewers.values()): errors.append("AI reviews must remain advisory-only")
    authority = state.get("authority") or {}
    for key in ("method_thesis_active", "experiment_blueprint_authorized", "local_validation_authorized", "p0_authorized", "gpu_authorized", "full_experiment_authorized", "premature_pf_f0_used", "new_method_auto_authorized"):
        if authority.get(key) is not False: errors.append(f"{key} must remain false")
    return errors


def write_pf2_method_adjudication(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_pf2_method_adjudication()
    errors = validate_pf2_method_adjudication(state)
    if errors:
        raise ValueError("Invalid PF-2 method adjudication:\n- " + "\n- ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_PF2_METHOD_ADJUDICATION = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_pf2_method_adjudication(), ensure_ascii=False))
