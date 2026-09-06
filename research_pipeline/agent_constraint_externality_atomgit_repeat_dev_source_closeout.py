from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
CONTRACT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-source-execution-contract-20260906.json"
OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-source-closeout-20260906.json"
LEDGER = Path("/data/wyt/agent-constraint-externality/runs/atomgit-repeat-dev-source-20260906-v1/source-ledger.jsonl")


class CloseoutError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verified(path: Path, status: str) -> dict[str, Any]:
    payload = read_json(path)
    if payload.get("object_id") != OBJECT_ID or payload.get("status") != status:
        raise CloseoutError(f"identity/status mismatch: {path}")
    claimed = payload.get("content_sha256")
    if claimed:
        unsigned = dict(payload); unsigned.pop("content_sha256", None)
        if sha256_value(unsigned) != claimed:
            raise CloseoutError(f"content hash mismatch: {path}")
    return payload


def rows() -> list[dict[str, Any]]:
    if not LEDGER.is_file():
        raise CloseoutError("source ledger missing")
    return [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]


def build() -> dict[str, Any]:
    contract = verified(CONTRACT, "ATOMGIT_REPEAT_DEV_SIX_SOURCE_EXECUTION_AUTHORIZED")
    family_ids = list(contract["panel"]["family_ids"])
    ledger_rows = rows()
    dispatch = [r for r in ledger_rows if r.get("event") == "DISPATCH"]
    completion = [r for r in ledger_rows if r.get("event") == "COMPLETION"]
    failure = [r for r in ledger_rows if r.get("event") == "FAILURE"]
    if failure:
        raise CloseoutError("source closeout expected support stop, not technical failure")
    if [r["family_id"] for r in dispatch] != family_ids[:3]:
        raise CloseoutError("dispatch order drift before support stop")
    if [r["family_id"] for r in completion] != family_ids[:3]:
        raise CloseoutError("completion order drift before support stop")
    if [bool(r.get("target_success")) for r in completion] != [False, False, True]:
        raise CloseoutError("terminal support geometry drift")
    if not all(bool(r.get("tool_loop_completed")) and bool(r.get("all_tool_dispatches_closed")) for r in completion):
        raise CloseoutError("completed source unit lost trajectory/tool closure")
    if set(family_ids[3:]) & {r["family_id"] for r in ledger_rows}:
        raise CloseoutError("post-stop family was dispatched")
    if contract.get("panel", {}).get("family_ids") != family_ids:
        raise CloseoutError("execution-contract family order drift")
    result: dict[str, Any] = {
        "schema_version": "ace-repeat-dev-source-closeout-v1",
        "object_id": OBJECT_ID,
        "status": "ATOMGIT_REPEAT_DEV_FIXED_SIX_SOURCE_SUPPORT_FAIL_STOP_NO_REPAIR",
        "execution_id": contract["execution_id"],
        "execution_contract_content_sha256": contract["content_sha256"],
        "ledger_sha256": sha256_file(LEDGER),
        "planned_family_count": 6,
        "dispatched_family_count": 3,
        "completed_family_count": 3,
        "semantic_target_failure_count": 2,
        "target_success_count": 1,
        "never_dispatched_family_ids": family_ids[3:],
        "support_stop_family_id": completion[-1]["family_id"],
        "support_stop_reason": "Frozen fixed-six contract requires every development family to have a semantic target failure; the third normally completed source succeeded. Replacement/top-up is forbidden.",
        "completed_units": [
            {
                "family_id": row["family_id"],
                "case_id": row["case_id"],
                "target_success": bool(row["target_success"]),
                "usable_semantic_failure": bool(row["usable_semantic_failure"]),
                "model_round_count": int(row["model_round_count"]),
                "appworld_tool_call_count": int(row["appworld_tool_call_count"]),
                "trajectory_sha256": row["trajectory_sha256"],
            }
            for row in completion
        ],
        "scientific_model_round_count": sum(int(r["model_round_count"]) for r in completion),
        "appworld_tool_call_total": sum(int(r["appworld_tool_call_count"]) for r in completion),
        "repair_generation_executed": False,
        "topology_execution_executed": False,
        "scientific_externality_outcomes_observed": 0,
        "interpretation": "Qualification-layer support failure only. It does not test repair uptake, collateral externality, or topology dependence.",
        "current_fixed_six_reusable_for_repeat_panel": False,
        "replacement_or_top_up_allowed_under_consumed_contract": False,
        "authority": {
            "source_execution_consumed": True,
            "repair_generation": False,
            "development_repeat_qualification": False,
            "target_only_verification": False,
            "rq1_rq2": False,
            "rq3": False,
            "rq4": False,
            "paper_claim": False,
        },
        "next_legal_action": "ZERO_PROVIDER development-reserve protocol repair only; any fresh provider dispatch requires a new reviewed contract and separate human execution authority.",
    }
    result["content_sha256"] = sha256_value(result)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    print(json.dumps(build(), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
