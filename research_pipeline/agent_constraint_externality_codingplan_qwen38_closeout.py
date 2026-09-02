from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_codingplan_prereg import (
    CONTRACT_OUTPUT,
    MANIFEST_OUTPUT,
    MODEL_ID,
    MODEL_PROFILE,
    PROVIDER,
    Q0_OUTPUT,
    Q1_OUTPUT,
)
from research_pipeline.agent_constraint_externality_codingplan_qwen38_capability import (
    EXECUTION_ID,
    RESULT_OUTPUT,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    OBJECT_ID,
    sha256_file,
    sha256_value,
)

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
LEDGER = (
    ROOT
    / "runtimes/agent-constraint-externality-codingplan-qwen38-capability-a0-r1-20260902/ledger.jsonl"
)
OUTPUT = GENERATED / "agent-constraint-externality-codingplan-qwen38-capability-a0-closeout-20260902.json"
TOOL_CALL_CAP = 16
MODEL_ROUND_CAP = 20


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verified(path: Path, expected_status: str | None = None) -> dict[str, Any]:
    payload = read_json(path)
    claimed = payload.get("content_sha256")
    unsigned = dict(payload)
    unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise RuntimeError(f"Content hash mismatch: {path}")
    if expected_status is not None and payload.get("status") != expected_status:
        raise RuntimeError(f"Unexpected status in {path}: {payload.get('status')}")
    return payload


def ledger_rows() -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise RuntimeError("CodingPlan scientific ledger is empty.")
    return rows


def build() -> dict[str, Any]:
    result = verified(RESULT_OUTPUT, "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP")
    contract = verified(CONTRACT_OUTPUT, "CODINGPLAN_QWEN38_CAPABILITY_A0_AUTHORIZED")
    q0 = verified(Q0_OUTPUT, "CODINGPLAN_MCP_Q0_PASS")
    q1 = verified(Q1_OUTPUT, "CODINGPLAN_APPWORLD_MCP_LIVE_PREDISPATCH_PASS")
    manifest = verified(MANIFEST_OUTPUT, "CODINGPLAN_QWEN38_CAPABILITY_A0_FROZEN")
    rows = ledger_rows()
    dispatches = [row for row in rows if row.get("event") == "DISPATCH"]
    completions = [row for row in rows if row.get("event") == "COMPLETION"]
    failures = [row for row in rows if row.get("event") == "FAILURE"]
    unit_ids = [row["unit_id"] for row in completions]
    if len(dispatches) != 8 or len(completions) != 8 or failures:
        raise RuntimeError("CodingPlan closeout requires 8 DISPATCH + 8 COMPLETION and zero FAILURE.")
    if len(set(unit_ids)) != 8:
        raise RuntimeError("CodingPlan closeout found duplicate completed unit IDs.")
    if sha256_file(LEDGER) != result.get("ledger_sha256"):
        raise RuntimeError("CodingPlan result/ledger hash mismatch.")
    if result.get("valid_capability_measurements") != 8:
        raise RuntimeError("CodingPlan result does not contain eight valid capability measurements.")
    if result.get("model_profile") != MODEL_PROFILE or result.get("model_id") != MODEL_ID:
        raise RuntimeError("CodingPlan model identity drifted.")
    if result.get("provider") != "ATOMGIT_CODINGPLAN_SIGNED_GATEWAY":
        raise RuntimeError("CodingPlan result provider identity drifted.")
    contract_provider = contract.get("provider", {})
    if not isinstance(contract_provider, dict) or contract_provider.get("id") != PROVIDER:
        raise RuntimeError("CodingPlan frozen contract provider drifted.")
    if q1.get("codingplan_model_requests") != 0 or q1.get("scientific_dispatch_sent") is not False:
        raise RuntimeError("Q1 crossed the zero-request predispatch boundary.")

    scientific_rounds = sum(int(row["model_round_count"]) for row in completions)
    appworld_tools = sum(int(row["appworld_tool_call_count"]) for row in completions)
    if scientific_rounds != int(result["model_round_count"]):
        raise RuntimeError("Scientific model round accounting mismatch.")
    if appworld_tools != int(result["appworld_tool_call_total"]):
        raise RuntimeError("AppWorld tool accounting mismatch.")
    if not all(row.get("atomcode_stop_reason") == "stopped" for row in completions):
        raise RuntimeError("A CodingPlan scientific unit did not stop normally.")
    if not all(int(row["model_round_count"]) <= MODEL_ROUND_CAP for row in completions):
        raise RuntimeError("A CodingPlan unit exceeded the frozen model-round cap.")
    if not all(int(row["appworld_tool_call_count"]) <= TOOL_CALL_CAP for row in completions):
        raise RuntimeError("A CodingPlan unit exceeded the frozen AppWorld tool cap.")
    if not all(bool(row.get("target_success")) for row in completions):
        raise RuntimeError("The sealed CodingPlan ceiling result contradicts a failed target unit.")
    if not all(float(row.get("non_target_preservation", -1)) == 1.0 for row in completions):
        raise RuntimeError("The sealed CodingPlan ceiling result contradicts non-target preservation.")

    first_before = int(result["codingplan_window_first_before"]["used"])
    last_after = int(result["codingplan_window_last_after"]["used"])
    account_window_delta = last_after - first_before
    if account_window_delta < scientific_rounds:
        raise RuntimeError("Account-level CodingPlan usage is smaller than scientific model rounds.")
    unattributed = account_window_delta - scientific_rounds

    per_unit: list[dict[str, Any]] = []
    inter_unit_gaps: list[dict[str, Any]] = []
    prior_after: int | None = None
    for row in completions:
        before = int(row["codingplan_window_before"]["used"])
        after = int(row["codingplan_window_after"]["used"])
        rounds = int(row["model_round_count"])
        if after - before != rounds:
            raise RuntimeError(f"Per-unit CodingPlan usage delta differs from live rounds: {row['unit_id']}")
        if prior_after is not None and before != prior_after:
            inter_unit_gaps.append({
                "before_unit_id": row["unit_id"],
                "previous_unit_window_after": prior_after,
                "current_unit_window_before": before,
                "account_window_gap": before - prior_after,
            })
        prior_after = after
        per_unit.append({
            "unit_id": row["unit_id"],
            "model_round_count": rounds,
            "appworld_tool_call_count": int(row["appworld_tool_call_count"]),
            "codingplan_window_used_before": before,
            "codingplan_window_used_after": after,
        })
    if sum(int(gap["account_window_gap"]) for gap in inter_unit_gaps) != unattributed:
        raise RuntimeError("Inter-unit CodingPlan gaps do not reconcile with account-level delta.")

    payload: dict[str, Any] = {
        "schema_version": "ace-codingplan-qwen38-capability-a0-closeout-v1",
        "object_id": OBJECT_ID,
        "execution_id": EXECUTION_ID,
        "status": "CODINGPLAN_QWEN38_CAPABILITY_A0_CLOSEOUT_CEILING_STOP",
        "scientific_verdict": result["status"],
        "gate": result["gate"],
        "provider": result["provider"],
        "model_profile": result["model_profile"],
        "model_id": result["model_id"],
        "harness": result["harness"],
        "strict_direct_api_comparison": False,
        "comparison_note": (
            "AtomCode CodingPlan MCP is a distinct harness from the direct OpenAI-compatible AppWorld runner; "
            "its capability result is valid for backbone qualification but request accounting is kept separate."
        ),
        "scientific_units": {
            "scheduled": 8,
            "dispatched": 8,
            "completed": 8,
            "failures": 0,
            "duplicate_completed_units": 0,
            "retries": 0,
            "replacements": 0,
        },
        "execution_accounting": {
            "scientific_model_round_count": scientific_rounds,
            "appworld_tool_call_total": appworld_tools,
            "prompt_tokens_total": int(result["prompt_tokens_total"]),
            "completion_tokens_total": int(result["completion_tokens_total"]),
            "codingplan_account_window_used_before": first_before,
            "codingplan_account_window_used_after": last_after,
            "codingplan_account_window_request_delta": account_window_delta,
            "scientific_rounds_attributable_to_units": scientific_rounds,
            "account_level_unattributed_request_count": unattributed,
            "unattributed_request_classification": (
                "ACCOUNT_LEVEL_CODINGPLAN_REQUEST_OUTSIDE_SCIENTIFIC_UNIT"
                if unattributed
                else "NONE"
            ),
            "unattributed_request_note": (
                "CodingPlan usage is account-level. No extra scientific session, AppWorld MCP trace, or ledger round "
                "supports assigning the inter-unit request gap to a scientific unit. AI session naming was disabled."
            ),
            "inter_unit_account_window_gaps": inter_unit_gaps,
            "per_unit": per_unit,
        },
        "provenance": {
            "result": {"path": str(RESULT_OUTPUT.relative_to(ROOT)), "sha256": sha256_file(RESULT_OUTPUT), "content_sha256": result["content_sha256"]},
            "ledger": {"path": str(LEDGER.relative_to(ROOT)), "sha256": sha256_file(LEDGER)},
            "contract": {"path": str(CONTRACT_OUTPUT.relative_to(ROOT)), "sha256": sha256_file(CONTRACT_OUTPUT), "content_sha256": contract["content_sha256"]},
            "contract_manifest": {"path": str(MANIFEST_OUTPUT.relative_to(ROOT)), "sha256": sha256_file(MANIFEST_OUTPUT), "content_sha256": manifest["content_sha256"]},
            "q0": {"path": str(Q0_OUTPUT.relative_to(ROOT)), "sha256": sha256_file(Q0_OUTPUT), "content_sha256": q0["content_sha256"]},
            "q1": {"path": str(Q1_OUTPUT.relative_to(ROOT)), "sha256": sha256_file(Q1_OUTPUT), "content_sha256": q1["content_sha256"]},
        },
        "scientific_outcomes_observed": 0,
        "f0_executed": False,
        "authority": {
            "f0": False,
            "p1": False,
            "toolsandbox": False,
            "appworld_ul": False,
            "paper_claim": False,
        },
        "next_legal_action": "STOP_AWAIT_HUMAN_BACKBONE_SELECTION",
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    payload = build()
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": payload["status"],
        "scientific_verdict": payload["scientific_verdict"],
        "scientific_model_rounds": payload["execution_accounting"]["scientific_model_round_count"],
        "codingplan_window_delta": payload["execution_accounting"]["codingplan_account_window_request_delta"],
        "unattributed_requests": payload["execution_accounting"]["account_level_unattributed_request_count"],
        "f0_authorized": payload["authority"]["f0"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
