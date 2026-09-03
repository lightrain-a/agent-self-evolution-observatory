from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
RESULT = GENERATED / "agent-constraint-externality-sq0-v3-mimo25pro-result-20260903.json"
RUNTIME = ROOT / "runtimes/agent-constraint-externality-sq0-v3-mimo25pro-20260903"
LEDGER = RUNTIME / "ledger.jsonl"
CLOSEOUT = GENERATED / "agent-constraint-externality-sq0-v3-closeout-20260903.json"
DIAGNOSTIC = GENERATED / "agent-constraint-externality-sq0-v3-root-cause-20260903.json"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verified(path: Path, status: str | None = None) -> dict[str, Any]:
    payload = _read(path)
    if payload.get("object_id") != OBJECT_ID:
        raise RuntimeError(f"Object mismatch: {path}")
    if status is not None and payload.get("status") != status:
        raise RuntimeError(f"Status mismatch: {path}: {payload.get('status')}")
    claimed = payload.get("content_sha256")
    if claimed is not None:
        unsigned = dict(payload); unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise RuntimeError(f"Content hash mismatch: {path}")
    return payload


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    result = _verified(RESULT, "SQ0_V3_FUTILITY_TOO_EASY_STOP")
    rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
    dispatch = [r for r in rows if r.get("event") == "DISPATCH"]
    completion = [r for r in rows if r.get("event") == "COMPLETION"]
    if len(dispatch) != 9 or len(completion) != 9:
        raise RuntimeError("V3 futility ledger must be exactly 9 DISPATCH + 9 COMPLETION.")
    if any(r.get("non_semantic_failure") or not r.get("tool_loop_completed") for r in completion):
        raise RuntimeError("V3 closeout expects no interface/non-semantic failures.")
    if result.get("usable_target_failure_count") != 5 or result.get("target_success_count") != 4:
        raise RuntimeError("V3 aggregate drifted.")
    if result.get("possible_final_failure_count_interval") != [5, 8] or result.get("acceptable_final_failure_counts") != [9, 10]:
        raise RuntimeError("V3 futility arithmetic drifted.")
    if result.get("remaining_undispatched_case_count") != 3 or result.get("futility_proven") is not True:
        raise RuntimeError("V3 early-stop disposition drifted.")
    by_kind: dict[str, dict[str, int]] = {}
    for kind, token in (("FG_SEMANTIC_V3", "SQ0V3-FG-"), ("TNF_SEMANTIC_V3", "SQ0V3-TNF-")):
        subset = [r for r in completion if token in str(r.get("case_id", r.get("unit_id", "")))]
        by_kind[kind] = {
            "completed": len(subset),
            "usable_target_failures": sum(bool(r.get("usable_target_failure", not r.get("target_success", False))) for r in subset),
            "target_successes": sum(bool(r.get("target_success")) for r in subset),
        }
    if by_kind["FG_SEMANTIC_V3"] != {"completed": 6, "usable_target_failures": 5, "target_successes": 1}:
        raise RuntimeError("V3 FG diagnostic drifted.")
    if by_kind["TNF_SEMANTIC_V3"] != {"completed": 3, "usable_target_failures": 0, "target_successes": 3}:
        raise RuntimeError("V3 TNF diagnostic drifted.")
    diagnostic: dict[str, Any] = {
        "schema_version": "ace-sq0-v3-root-cause-v1",
        "object_id": OBJECT_ID,
        "status": "SQ0_V3_TNF_TOO_EASY_FG_NEAR_TARGET_WINDOW",
        "development_iteration": 3,
        "by_kind": by_kind,
        "root_causes": [
            "Fresh FG semantic-composition cases produced five substantive failures in six completed cases, which is near the desired development failure regime.",
            "The first three fresh TNF semantic-composition cases were all solved, making the final 9-10/12 failure window unreachable after the fourth overall target success.",
            "The next development iteration must preserve the FG mechanism while increasing TNF target-local decision depth; it must not reduce tool budget, hide resource locators, or reuse observed cases.",
        ],
        "prospective_v4_constraints": {
            "fresh_cases_only": True,
            "reuse_v3_case_bytes": False,
            "fg_mechanism_change": "NONE; FRESH_PARAMETERIZATION_ONLY",
            "tnf_change": "ADD_PUBLIC_DYNAMIC_POLICY_SELECTION_AND_SECOND_STAGE_ADJUSTMENT_COMPOSITION",
            "tool_budget_not_used_as_difficulty_knob": True,
            "hidden_fixture_ids_forbidden": True,
            "terminal_newline_only_normalization_retained": True,
        },
        "provider_requests_added": 0,
        "scientific_effects_observed": 0,
        "authority": {"sq0_v4_design": True, "sq0_v4_execution": False, "f0_r1": False, "probe": False, "p1": False, "paper_claim": False},
    }
    diagnostic["content_sha256"] = sha256_value(diagnostic)
    rounds = sum(int(r.get("model_round_count", 0)) for r in completion)
    closeout: dict[str, Any] = {
        "schema_version": "ace-sq0-v3-closeout-v1",
        "object_id": OBJECT_ID,
        "status": "SQ0_V3_TOO_EASY_FUTILITY_CLOSEOUT",
        "verdict": result["status"],
        "result_artifact": str(RESULT.relative_to(ROOT)),
        "result_file_sha256": sha256_file(RESULT),
        "result_content_sha256": result["content_sha256"],
        "ledger_sha256": sha256_file(LEDGER),
        "completed_case_count": 9,
        "planned_case_count": 12,
        "remaining_undispatched_case_count": 3,
        "usable_target_failure_count": 5,
        "target_success_count": 4,
        "observed_failure_rate": 5 / 9,
        "possible_final_failure_count_interval": [5, 8],
        "acceptable_final_failure_counts": [9, 10],
        "futility_proven": True,
        "by_kind": by_kind,
        "root_cause_content_sha256": diagnostic["content_sha256"],
        "accounting": {
            "scientific_model_round_count": rounds,
            "appworld_tool_call_total": sum(int(r.get("appworld_tool_call_count", 0)) for r in completion),
            "prompt_tokens_total": sum(int(r.get("prompt_tokens_total", 0)) for r in completion),
            "completion_tokens_total": sum(int(r.get("completion_tokens_total", 0)) for r in completion),
        },
        "development_only": True,
        "confirmatory_reuse": False,
        "scientific_effects_observed": 0,
        "authority": {"current_sq0_v3": False, "sq0_v4_design": True, "sq0_v4_execution": False, "f0_r1": False, "probe": False, "p1": False, "paper_claim": False},
    }
    closeout["content_sha256"] = sha256_value(closeout)
    return closeout, diagnostic


def main() -> None:
    closeout, diagnostic = build()
    CLOSEOUT.write_text(json.dumps(closeout, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    DIAGNOSTIC.write_text(json.dumps(diagnostic, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": closeout["status"], "completed": 9, "failures": 5, "v4_execution_authorized": False}, sort_keys=True))


if __name__ == "__main__":
    main()
