from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_codingplan_f0_source import (
    CONTRACT,
    F0_FAMILIES,
    MODEL_ID,
    MODEL_PROFILE,
    PROVIDER,
    REPAIRS_MANIFEST,
    SOURCE_LEDGER,
)
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OUTPUT = GENERATED / "agent-constraint-externality-f0-source-closeout-mimo25pro-20260903.json"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verified(path: Path, expected_status: str | None = None) -> dict[str, Any]:
    payload = _read(path)
    if payload.get("object_id") != OBJECT_ID:
        raise RuntimeError(f"object mismatch: {path}")
    if expected_status and payload.get("status") != expected_status:
        raise RuntimeError(f"status mismatch: {path}: {payload.get('status')}")
    claimed = payload.get("content_sha256") or payload.get("manifest_content_sha256")
    if claimed:
        unsigned = dict(payload)
        unsigned.pop("content_sha256", None)
        unsigned.pop("manifest_content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise RuntimeError(f"content hash mismatch: {path}")
    return payload


def build() -> dict[str, Any]:
    contract = _verified(CONTRACT, "F0_CODINGPLAN_MIMO25PRO_SOURCE_AUTHORIZED")
    repairs = _verified(REPAIRS_MANIFEST, "F0_UPDATE_UPTAKE_INSUFFICIENT_STOP")
    if repairs.get("eligible_families") != [] or repairs.get("updater_model_request_count") != 0:
        raise RuntimeError("source uptake disposition drifted")
    rows = [json.loads(line) for line in SOURCE_LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
    dispatch = [row for row in rows if row["event"] == "DISPATCH"]
    complete = [row for row in rows if row["event"] == "COMPLETION"]
    failures = [row for row in rows if row["event"] == "FAILURE"]
    if len(dispatch) != 8 or len(complete) != 8 or failures:
        raise RuntimeError("F0 source ledger is not exactly 8 dispatch + 8 completion")
    if {row["unit_id"] for row in dispatch} != {row["unit_id"] for row in complete}:
        raise RuntimeError("source dispatch/completion identity drifted")
    target_successes = sum(bool(row["result"]["evaluation"]["target_success"]) for row in complete)
    if target_successes != 8:
        raise RuntimeError("expected frozen source result 8/8 target success")
    resets: list[dict[str, Any]] = []
    for row in complete:
        result = row["result"]
        before = result["codingplan_window_before"]
        after = result["codingplan_window_after"]
        if before.get("next_reset_at") != after.get("next_reset_at") or int(after["used"]) < int(before["used"]):
            resets.append({
                "unit_id": row["unit_id"],
                "before": before,
                "after": after,
            })
    payload: dict[str, Any] = {
        "schema_version": "ace-f0-source-closeout-v1",
        "object_id": OBJECT_ID,
        "status": "F0_UPDATE_UPTAKE_FAIL_SOURCE_CLOSEOUT",
        "verdict": "F0_UPDATE_UPTAKE_FAIL",
        "mandatory_stop": True,
        "selected_backbone": {
            "provider": PROVIDER,
            "model_profile": MODEL_PROFILE,
            "model_id": MODEL_ID,
            "harness": "ATOMCODE_CODINGPLAN_MCP_V1",
        },
        "source_family_ids": list(F0_FAMILIES),
        "source_episode_count": 8,
        "source_target_success_count": target_successes,
        "source_target_failure_count": 8 - target_successes,
        "eligible_repair_family_count": len(repairs["eligible_families"]),
        "eligible_repair_families": repairs["eligible_families"],
        "updater_model_request_count": repairs["updater_model_request_count"],
        "probe_episode_count": 0,
        "scientific_effects_observed": 0,
        "scientific_model_round_count": sum(int(row["result"]["model_round_count"]) for row in complete),
        "appworld_tool_call_total": sum(int(row["result"]["appworld_tool_call_count"]) for row in complete),
        "prompt_tokens_total": sum(int(row["result"]["prompt_tokens_total"]) for row in complete),
        "completion_tokens_total": sum(int(row["result"]["completion_tokens_total"]) for row in complete),
        "codingplan_account_window_reset_crossings": resets,
        "codingplan_account_window_delta_exactly_identifiable": len(resets) == 0,
        "source_ledger_artifact": str(SOURCE_LEDGER.relative_to(ROOT)),
        "source_ledger_sha256": sha256_file(SOURCE_LEDGER),
        "repairs_manifest_artifact": str(REPAIRS_MANIFEST.relative_to(ROOT)),
        "repairs_manifest_file_sha256": sha256_file(REPAIRS_MANIFEST),
        "repairs_manifest_content_sha256": repairs["manifest_content_sha256"],
        "source_contract_content_sha256": contract["content_sha256"],
        "stop_reason": "ZERO_TARGET_FAILURES_SO_NO_PERSISTENT_REPAIR_COULD_BE_GENERATED",
        "interpretation_boundary": (
            "This is an update-uptake/source-failure-substrate failure, not evidence for or against the coupling externality mechanism. "
            "No probe outcome or update-attributable externality was observed."
        ),
        "authority": {
            "f0": False,
            "probe": False,
            "p1": False,
            "toolsandbox": False,
            "appworld_ul": False,
            "paper_claim": False,
        },
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    payload = build()
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "verdict": payload["verdict"],
        "source_target_success_count": payload["source_target_success_count"],
        "eligible_repair_family_count": payload["eligible_repair_family_count"],
        "scientific_model_round_count": payload["scientific_model_round_count"],
        "probe_episode_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
