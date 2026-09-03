from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import (
    OBJECT_ID,
    sha256_file,
    sha256_value,
)

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
RUNTIME_LEDGER = (
    ROOT
    / "runtimes"
    / "agent-constraint-externality-codingplan-mimo25pro-capability-b3-20260903"
    / "ledger.jsonl"
)
SEARCH_B3 = GENERATED / "agent-constraint-externality-capability-backbone-search-state-b3-20260903.json"
CONTRACT = GENERATED / "agent-constraint-externality-codingplan-mimo25pro-capability-b3-contract-20260903.json"
EXECUTION_SEAL = GENERATED / "agent-constraint-externality-codingplan-mimo25pro-b3-execution-seal-20260903.json"
RESULT = GENERATED / "agent-constraint-externality-codingplan-mimo25pro-capability-b3-result-20260903.json"
CLOSEOUT = GENERATED / "agent-constraint-externality-codingplan-mimo25pro-capability-b3-closeout-20260903.json"
FINAL_SELECTION = GENERATED / "agent-constraint-externality-capability-backbone-selection-final-20260903.json"

EXPECTED_MODEL_ID = "mimo-v2.5-pro"
EXPECTED_MODEL_PROFILE = "AtomGit-mimo-v2.5-pro"
EXPECTED_HARNESS = "ATOMCODE_CODINGPLAN_MCP_V1"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


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


def ledger_completion_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in RUNTIME_LEDGER.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("event") == "COMPLETION":
            rows.append(row)
    if len(rows) != 8:
        raise RuntimeError(f"Expected eight completion rows, found {len(rows)}")
    return rows


def build_closeout() -> dict[str, Any]:
    search = verified(SEARCH_B3, "CAPABILITY_BACKBONE_SEARCH_CONTINUE_MIMO25PRO_NEXT")
    contract = verified(CONTRACT, "CODINGPLAN_MIMO25PRO_CAPABILITY_B3_AUTHORIZED")
    seal = verified(EXECUTION_SEAL, "CODINGPLAN_MIMO25PRO_B3_EXECUTION_SEAL_PASS")
    result = verified(RESULT, "CAPABILITY_CALIBRATION_PASS")

    if result.get("model_id") != EXPECTED_MODEL_ID:
        raise RuntimeError("MiMo 2.5 Pro result model id drifted.")
    if result.get("model_profile") != EXPECTED_MODEL_PROFILE:
        raise RuntimeError("MiMo 2.5 Pro result model profile drifted.")
    if result.get("harness") != EXPECTED_HARNESS:
        raise RuntimeError("MiMo 2.5 Pro result harness drifted.")
    if result.get("contract_sha256") != contract.get("content_sha256"):
        raise RuntimeError("MiMo 2.5 Pro result/contract lineage drifted.")
    if result.get("backbone_search_state_sha256") != search.get("content_sha256"):
        raise RuntimeError("MiMo 2.5 Pro result/search lineage drifted.")
    if seal.get("contract_content_sha256") != contract.get("content_sha256"):
        raise RuntimeError("MiMo 2.5 Pro execution seal/contract lineage drifted.")
    if seal.get("backbone_search_state_sha256") != search.get("content_sha256"):
        raise RuntimeError("MiMo 2.5 Pro execution seal/search lineage drifted.")
    if seal.get("ledger_absent_before_execution") is not True or seal.get("scientific_dispatch_count_before_execution") != 0:
        raise RuntimeError("MiMo 2.5 Pro execution seal is not at a clean pre-dispatch boundary.")
    if sha256_file(RUNTIME_LEDGER) != result.get("ledger_sha256"):
        raise RuntimeError("MiMo 2.5 Pro ledger bytes drifted after result.")

    gate = result["gate"]
    expected_gate = {
        "tool_loop_completion_rate": 0.875,
        "target_success_rate": 0.875,
        "non_target_preservation_rate": 1.0,
        "malformed_tool_call_count": 0,
        "verdict": "CAPABILITY_CALIBRATION_PASS",
    }
    for key, value in expected_gate.items():
        if gate.get(key) != value:
            raise RuntimeError(f"MiMo 2.5 Pro gate drifted for {key}: {gate.get(key)}")

    completions = ledger_completion_rows()
    incomplete = [row for row in completions if not bool(row.get("tool_loop_completed"))]
    failed_target = [row for row in completions if not bool(row.get("target_success"))]
    if len(incomplete) != 1 or len(failed_target) != 1:
        raise RuntimeError("MiMo 2.5 Pro PASS boundary no longer has exactly one incomplete/failed unit.")
    if incomplete[0].get("unit_id") != failed_target[0].get("unit_id"):
        raise RuntimeError("MiMo 2.5 Pro incomplete and target-failure units diverged.")

    first_before = result["codingplan_window_first_before"]
    last_after = result["codingplan_window_last_after"]
    rounds = int(result["model_round_count"])
    account_delta = int(last_after["used"]) - int(first_before["used"])
    if rounds != 77 or account_delta != 78:
        raise RuntimeError("MiMo 2.5 Pro request accounting drifted.")

    account_gaps: list[dict[str, Any]] = []
    previous_after: int | None = None
    for row in completions:
        before = int(row["codingplan_window_before"]["used"])
        after = int(row["codingplan_window_after"]["used"])
        row_rounds = int(row["model_round_count"])
        if after - before != row_rounds:
            raise RuntimeError(f"Per-unit request accounting drifted: {row['unit_id']}")
        if previous_after is not None and before != previous_after:
            account_gaps.append(
                {
                    "after_previous_unit": previous_after,
                    "before_unit": before,
                    "gap": before - previous_after,
                    "before_unit_id": row["unit_id"],
                }
            )
        previous_after = after
    if account_gaps != [
        {
            "after_previous_unit": 283,
            "before_unit": 284,
            "gap": 1,
            "before_unit_id": "capability:mimo-v2.5-pro|ACE-TNF-06|2",
        }
    ]:
        raise RuntimeError(f"Unexpected MiMo 2.5 Pro account-level gaps: {account_gaps}")

    payload: dict[str, Any] = {
        "schema_version": "ace-codingplan-mimo25pro-capability-b3-closeout-v1",
        "object_id": OBJECT_ID,
        "status": "CODINGPLAN_MIMO25PRO_B3_PASS_CLOSEOUT",
        "result_artifact": str(RESULT.relative_to(ROOT)),
        "result_file_sha256": sha256_file(RESULT),
        "result_content_sha256": result["content_sha256"],
        "contract_artifact": str(CONTRACT.relative_to(ROOT)),
        "contract_content_sha256": contract["content_sha256"],
        "execution_seal_artifact": str(EXECUTION_SEAL.relative_to(ROOT)),
        "execution_seal_content_sha256": seal["content_sha256"],
        "ledger_artifact": str(RUNTIME_LEDGER.relative_to(ROOT)),
        "ledger_sha256": result["ledger_sha256"],
        "verdict": result["status"],
        "model_id": EXPECTED_MODEL_ID,
        "model_profile": EXPECTED_MODEL_PROFILE,
        "harness": EXPECTED_HARNESS,
        "gate": gate,
        "valid_capability_measurements": 8,
        "tool_loop_completed_measurements": 7,
        "tool_loop_incomplete_measurements": 1,
        "target_success_measurements": 7,
        "target_failure_measurements": 1,
        "single_incomplete_unit_id": incomplete[0]["unit_id"],
        "accounting": {
            "scientific_model_round_count": rounds,
            "codingplan_account_window_request_delta": account_delta,
            "account_level_unattributed_request_count": account_delta - rounds,
            "account_level_gaps": account_gaps,
            "appworld_tool_call_total": int(result["appworld_tool_call_total"]),
            "prompt_tokens_total": int(result["prompt_tokens_total"]),
            "completion_tokens_total": int(result["completion_tokens_total"]),
            "accounting_domain": "CODINGPLAN_ACCOUNT_WINDOW_DO_NOT_SUM_WITH_DIRECT_API_PROVIDER_CALLS",
        },
        "selection_interpretation": (
            "mimo-v2.5-pro is the first candidate in the predeclared backbone ladder to satisfy all frozen "
            "capability thresholds. Its target-success and tool-loop-completion rates are both 7/8, and "
            "target success is exactly at the frozen 0.875 ceiling rather than above it."
        ),
        "scientific_outcomes_observed": 0,
        "authority": {
            "backbone_selection": True,
            "f0": False,
            "f0_reason": "Capability PASS freezes the backbone but never self-authorizes F0.",
            "p1": False,
            "toolsandbox": False,
            "appworld_ul": False,
            "paper_claim": False,
        },
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def build_final_selection(closeout: dict[str, Any]) -> dict[str, Any]:
    search = verified(SEARCH_B3, "CAPABILITY_BACKBONE_SEARCH_CONTINUE_MIMO25PRO_NEXT")
    if search.get("remaining_frozen_order") != [EXPECTED_MODEL_ID]:
        raise RuntimeError("Final backbone search order drifted.")
    if search.get("next_candidate") != {
        "model_id": EXPECTED_MODEL_ID,
        "profile": EXPECTED_MODEL_PROFILE,
    }:
        raise RuntimeError("Final backbone search candidate drifted.")
    if closeout.get("verdict") != "CAPABILITY_CALIBRATION_PASS":
        raise RuntimeError("Cannot freeze backbone from a non-PASS closeout.")

    payload: dict[str, Any] = {
        "schema_version": "ace-capability-backbone-selection-final-v1",
        "object_id": OBJECT_ID,
        "status": "CAPABILITY_BACKBONE_SELECTED_MIMO25PRO_PASS",
        "selection_policy": search["selection_policy"],
        "predeclared_search_state_artifact": str(SEARCH_B3.relative_to(ROOT)),
        "predeclared_search_state_content_sha256": search["content_sha256"],
        "capability_closeout_artifact": str(CLOSEOUT.relative_to(ROOT)),
        "capability_closeout_content_sha256": closeout["content_sha256"],
        "selected_backbone": {
            "model_id": EXPECTED_MODEL_ID,
            "model_profile": EXPECTED_MODEL_PROFILE,
            "provider": "ATOMGIT_CODINGPLAN_SIGNED_GATEWAY",
            "harness": EXPECTED_HARNESS,
        },
        "frozen_gate_result": closeout["gate"],
        "remaining_candidate_order": [],
        "selection_reason": "FIRST_PREDECLARED_CANDIDATE_TO_PASS_ALL_FROZEN_CAPABILITY_THRESHOLDS",
        "selection_is_outcome_bounded_by_preregistered_ladder": True,
        "scientific_outcomes_observed": 0,
        "authority": {
            "backbone_selected": True,
            "f0": False,
            "f0_reason": "Separate human F0 authorization is still required after backbone freeze.",
            "p1": False,
            "toolsandbox": False,
            "appworld_ul": False,
            "paper_claim": False,
        },
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    closeout = build_closeout()
    write_json(CLOSEOUT, closeout)
    selection = build_final_selection(closeout)
    write_json(FINAL_SELECTION, selection)
    print(
        json.dumps(
            {
                "status": closeout["status"],
                "verdict": closeout["verdict"],
                "selected_backbone": selection["selected_backbone"],
                "scientific_model_rounds": closeout["accounting"]["scientific_model_round_count"],
                "codingplan_window_requests": closeout["accounting"]["codingplan_account_window_request_delta"],
                "unattributed_account_requests": closeout["accounting"]["account_level_unattributed_request_count"],
                "f0_authorized": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
