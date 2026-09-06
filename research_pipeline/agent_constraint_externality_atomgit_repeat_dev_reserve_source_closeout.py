from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
CONTRACT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-source-execution-contract-20260906.json"
RESULT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-source-result-20260906.json"
OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-source-closeout-20260906.json"
RUN_ROOT = Path("/data/wyt/agent-constraint-externality/runs/atomgit-repeat-dev-reserve-source-20260906-v1")
LEDGER = RUN_ROOT / "source-ledger.jsonl"
DUMMY_MARKERS = ("ACE-DEV-DUMMY", "/spare-")
AUTH_TOOL_SUFFIXES = ("__login", "__show_account_passwords")


class CloseoutError(RuntimeError):
    pass


def readj(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verified(path: Path, status: str) -> dict[str, Any]:
    payload = readj(path)
    if payload.get("object_id") != OBJECT_ID or payload.get("status") != status:
        raise CloseoutError(f"identity/status mismatch: {path}")
    claimed = payload.get("content_sha256")
    unsigned = dict(payload); unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise CloseoutError(f"content hash mismatch: {path}")
    return payload


def ledger_rows() -> list[dict[str, Any]]:
    if not LEDGER.is_file():
        raise CloseoutError("reserve source ledger missing")
    return [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]


def selected_from(completion: list[dict[str, Any]], ranked: dict[str, list[str]]) -> dict[str, list[str]]:
    by_id = {row["family_id"]: row for row in completion}
    selected = {"FG": [], "TNF": []}
    for category in ("FG", "TNF"):
        for family_id in ranked[category]:
            row = by_id.get(family_id)
            if row and row.get("usable_semantic_failure") is True:
                selected[category].append(family_id)
                if len(selected[category]) == 3:
                    break
    return selected


def trajectory_audit(completion: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    per_family: dict[str, Any] = {}
    leakage: dict[str, Any] = {}
    for row in completion:
        family_id = row["family_id"]
        path = RUN_ROOT / family_id.lower() / "trajectory.jsonl"
        if not path.is_file() or sha256_file(path) != row["trajectory_sha256"]:
            raise CloseoutError(f"trajectory hash drift: {family_id}")
        events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        dispatch = [event for event in events if event.get("event") == "TOOL_DISPATCH"]
        complete = [event for event in events if event.get("event") == "TOOL_COMPLETION"]
        rejected = [event for event in events if event.get("event") == "TOOL_REJECTED"]
        if rejected or len(dispatch) != len(complete) != 0:
            raise CloseoutError(f"trajectory rejected/dangling geometry: {family_id}")
        if len(dispatch) != int(row["appworld_tool_call_count"]) or len(complete) != int(row["appworld_tool_call_count"]):
            raise CloseoutError(f"trajectory/tool count drift: {family_id}")
        dispatch_ids = {event["tool_id"] for event in dispatch}
        complete_ids = {event["tool_id"] for event in complete}
        if len(dispatch_ids) != len(dispatch) or len(complete_ids) != len(complete) or dispatch_ids != complete_ids:
            raise CloseoutError(f"trajectory exactly-once drift: {family_id}")
        text = path.read_text(encoding="utf-8")
        dummy_rows = [event for event in events if any(marker.lower() in json.dumps(event, ensure_ascii=False).lower() for marker in DUMMY_MARKERS)]
        auth_rows = [
            event for event in events
            if str(event.get("tool_name", "")).endswith(AUTH_TOOL_SUFFIXES)
            or "access_token" in (event.get("arguments") or {})
            or "password" in (event.get("arguments") or {})
        ]
        per_family[family_id] = {
            "trajectory_sha256": row["trajectory_sha256"],
            "tool_call_count": int(row["appworld_tool_call_count"]),
            "row_count": len(events),
            "dispatch_completion_sets_equal": True,
            "rejected_count": 0,
        }
        leakage[family_id] = {
            "dummy_marker_row_count": len(dummy_rows),
            "auth_transport_row_count": len(auth_rows),
            "raw_trajectory_safe_for_repair_writer": len(dummy_rows) == 0 and len(auth_rows) == 0,
        }
    return per_family, leakage


def build() -> dict[str, Any]:
    contract = verified(CONTRACT, "ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_EXECUTION_AUTHORIZED")
    result = verified(RESULT, "ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_PANEL_PASS_REPAIR_CLOSED")
    rows = ledger_rows()
    dispatch = [row for row in rows if row.get("event") == "DISPATCH"]
    completion = [row for row in rows if row.get("event") == "COMPLETION"]
    failure = [row for row in rows if row.get("event") == "FAILURE"]
    if len(rows) != 20 or len(dispatch) != 10 or len(completion) != 10 or failure:
        raise CloseoutError("reserve source terminal ledger geometry drift")
    if len({row["unit_id"] for row in dispatch}) != 10 or len({row["unit_id"] for row in completion}) != 10:
        raise CloseoutError("reserve source duplicate unit")
    if {row["unit_id"] for row in dispatch} != {row["unit_id"] for row in completion}:
        raise CloseoutError("dispatch/completion unit sets differ")
    ranked = contract["ranked_family_ids"]
    selected = selected_from(completion, ranked)
    if selected != result["selected_family_ids"] or any(len(selected[cat]) != 3 for cat in ("FG", "TNF")):
        raise CloseoutError("frozen first-three selection drift")
    if int(result["semantic_failure_count"]) != 6 or int(result["target_success_count"]) != 4:
        raise CloseoutError("source support result drift")
    if sha256_file(LEDGER) != result["ledger_sha256"]:
        raise CloseoutError("ledger/result hash drift")
    trajectories, leakage = trajectory_audit(completion)
    selected_leakage = {fid: leakage[fid] for fid in selected["FG"] + selected["TNF"]}
    dummy_selected = [fid for fid, audit in selected_leakage.items() if audit["dummy_marker_row_count"] > 0]
    auth_selected = [fid for fid, audit in selected_leakage.items() if audit["auth_transport_row_count"] > 0]
    out: dict[str, Any] = {
        "schema_version": "ace-repeat-dev-reserve-source-closeout-v1",
        "object_id": OBJECT_ID,
        "status": "ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_PANEL_PASS_TARGET_EVIDENCE_PROJECTION_REQUIRED",
        "execution_id": result["execution_id"],
        "execution_contract_content_sha256": contract["content_sha256"],
        "result_content_sha256": result["content_sha256"],
        "result_file_sha256": sha256_file(RESULT),
        "ledger_sha256": result["ledger_sha256"],
        "ledger": {
            "row_count": 20,
            "dispatch_count": 10,
            "completion_count": 10,
            "failure_count": 0,
            "unique_dispatch_units": 10,
            "unique_completion_units": 10,
            "dispatch_completion_unit_sets_equal": True,
        },
        "source_outcomes": {
            "completed_source_count": 10,
            "semantic_failure_count": 6,
            "target_success_count": 4,
            "selected_family_ids": selected,
            "selected_family_count": 6,
            "scientific_model_round_count": int(result["scientific_model_round_count"]),
            "appworld_tool_call_total": int(result["appworld_tool_call_total"]),
        },
        "trajectory_integrity": trajectories,
        "repair_input_audit": {
            "raw_source_trajectory_is_not_direct_repair_input": True,
            "selected_family_audit": selected_leakage,
            "selected_families_with_dummy_observation": dummy_selected,
            "selected_families_with_auth_transport_evidence": auth_selected,
            "reason": "Source eligibility remains valid because selection used only normally completed target outcome before repair/topology. The updater contract is stricter: only target-failure evidence may be visible, so dummy topology-construction resources and authentication transport must be deterministically projected out before any repair-writer provider call.",
            "required_projection": "TARGET_EVIDENCE_PROJECTION_V1",
        },
        "interpretation": "The six-family development source panel is frozen and valid for source-failure eligibility. This is not repair-uptake, collateral-externality, or topology evidence. Repair generation remains closed until a zero-provider target-evidence projection passes anti-leakage tests.",
        "repair_generation_executed": False,
        "topology_execution_executed": False,
        "scientific_externality_outcomes_observed": 0,
        "authority": {
            "reserve_source_execution_closed": True,
            "repair_generation": False,
            "development_repeat_qualification": False,
            "target_only_verification": False,
            "rq1_rq2": False,
            "rq3": False,
            "rq4": False,
            "paper_claim": False,
        },
        "next_legal_action": "Implement and test TARGET_EVIDENCE_PROJECTION_V1 with zero provider calls, then freeze repair-generation readiness; any repair-writer execution requires separate human authority.",
    }
    out["content_sha256"] = sha256_value(out)
    OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def main() -> None:
    print(json.dumps(build(), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
