from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
CATALOG_B1 = GENERATED / "agent-constraint-externality-codingplan-catalog-b1-20260903.json"
SEARCH_B1 = GENERATED / "agent-constraint-externality-capability-backbone-search-state-b1-20260903.json"
GLM_RESULT = GENERATED / "agent-constraint-externality-codingplan-glm52-capability-b1-result-20260903.json"
GLM_CLOSEOUT = GENERATED / "agent-constraint-externality-codingplan-glm52-capability-b1-closeout-20260903.json"
SEARCH_B2 = GENERATED / "agent-constraint-externality-capability-backbone-search-state-b2-20260903.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verified(path: Path, status: str | None = None) -> dict[str, Any]:
    payload = read_json(path)
    if payload.get("object_id") != OBJECT_ID:
        raise RuntimeError(f"Object mismatch: {path}")
    if status is not None and payload.get("status") != status:
        raise RuntimeError(f"Status mismatch: {path}: {payload.get('status')}")
    claimed = payload.get("content_sha256")
    unsigned = dict(payload)
    unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise RuntimeError(f"Content hash mismatch: {path}")
    return payload


def build_glm_closeout() -> dict[str, Any]:
    result = verified(GLM_RESULT, "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP")
    gate = result["gate"]
    if gate["tool_loop_completion_rate"] != 1.0 or gate["target_success_rate"] != 1.0 or gate["non_target_preservation_rate"] != 1.0:
        raise RuntimeError("GLM aggregate gate drifted.")
    before, after = result["codingplan_window_first_before"], result["codingplan_window_last_after"]
    rounds = int(result["model_round_count"])
    window_delta = int(after["used"]) - int(before["used"])
    if rounds != 77 or window_delta != 77:
        raise RuntimeError("GLM request accounting drifted.")
    payload: dict[str, Any] = {
        "schema_version": "ace-codingplan-glm52-capability-b1-closeout-v1",
        "object_id": OBJECT_ID,
        "status": "CODINGPLAN_GLM52_B1_CEILING_CLOSEOUT",
        "result_artifact": str(GLM_RESULT.relative_to(ROOT)),
        "result_file_sha256": sha256_file(GLM_RESULT),
        "result_content_sha256": result["content_sha256"],
        "verdict": result["status"],
        "gate": gate,
        "tool_loop_completed_measurements": 8,
        "tool_loop_incomplete_measurements": 0,
        "accounting": {
            "scientific_model_round_count": rounds,
            "codingplan_account_window_request_delta": window_delta,
            "account_level_unattributed_request_count": window_delta - rounds,
            "appworld_tool_call_total": int(result["appworld_tool_call_total"]),
            "prompt_tokens_total": int(result["prompt_tokens_total"]),
            "completion_tokens_total": int(result["completion_tokens_total"]),
        },
        "interpretation_boundary": "GLM-5.2 fails only the frozen target-success ceiling; gate, task panel, tool cap, and substrate are unchanged for the next predeclared candidate.",
        "scientific_outcomes_observed": 0,
        "authority": {"f0": False, "p1": False, "toolsandbox": False, "appworld_ul": False, "paper_claim": False},
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def build_search_b2(closeout: dict[str, Any]) -> dict[str, Any]:
    prior = verified(SEARCH_B1, "CAPABILITY_BACKBONE_SEARCH_CONTINUE_GLM52_NEXT")
    catalog = verified(CATALOG_B1, "CODINGPLAN_ACCOUNT_CATALOG_REFRESH_PASS_ZERO_MODEL_REQUESTS")
    models = [row["model_id"] for row in catalog["models"]]
    if models != ["GLM-5.2", "deepseek-v4-flash", "mimo-v2.5", "mimo-v2.5-pro", "qwen3.8-27b"]:
        raise RuntimeError("Frozen CodingPlan catalog order drifted.")
    if prior["remaining_frozen_order"] != ["GLM-5.2", "mimo-v2.5", "mimo-v2.5-pro"]:
        raise RuntimeError("B1 search order drifted.")
    if closeout["verdict"] != "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP":
        raise RuntimeError("GLM is not a ceiling stop, cannot advance by B1 rule.")
    payload: dict[str, Any] = {
        "schema_version": "ace-capability-backbone-search-state-b2-v1",
        "object_id": OBJECT_ID,
        "status": "CAPABILITY_BACKBONE_SEARCH_CONTINUE_MIMO25_NEXT",
        "selection_policy": prior["selection_policy"],
        "catalog_artifact": str(CATALOG_B1.relative_to(ROOT)),
        "catalog_content_sha256": catalog["content_sha256"],
        "prior_search_state_artifact": str(SEARCH_B1.relative_to(ROOT)),
        "prior_search_state_content_sha256": prior["content_sha256"],
        "glm_closeout_artifact": str(GLM_CLOSEOUT.relative_to(ROOT)),
        "glm_closeout_content_sha256": closeout["content_sha256"],
        "remaining_frozen_order": ["mimo-v2.5", "mimo-v2.5-pro"],
        "next_candidate": {"model_id": "mimo-v2.5", "profile": "AtomGit-mimo-v2.5"},
        "stop_rule": prior["stop_rule"],
        "gate_unchanged": prior["gate_unchanged"],
        "advance_reason": "PREDECLARED_PRE_GLM_RULE_APPLIED_AFTER_GLM_CEILING",
        "scientific_outcomes_observed": 0,
        "authority": {"next_capability_candidate": True, "f0": False, "p1": False, "paper_claim": False},
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    closeout = build_glm_closeout(); write_json(GLM_CLOSEOUT, closeout)
    state = build_search_b2(closeout); write_json(SEARCH_B2, state)
    print(json.dumps({"glm_verdict": closeout["verdict"], "glm_rounds": closeout["accounting"]["scientific_model_round_count"], "next_candidate": state["next_candidate"], "remaining_order": state["remaining_frozen_order"], "f0_authorized": False}, sort_keys=True))


if __name__ == "__main__":
    main()
