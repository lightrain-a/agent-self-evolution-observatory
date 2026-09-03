from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
AUDIT = GENERATED / "agent-constraint-externality-atomcode-transport-isolation-audit-20260903.json"
RUNNER = ROOT / "research_pipeline/agent_constraint_externality_signed_no_tools_q0.py"
OUTPUT = GENERATED / "agent-constraint-externality-signed-no-tools-json-action-q0-failure-20260903.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verified(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    if payload.get("object_id") != OBJECT_ID:
        raise RuntimeError(f"Object mismatch: {path}")
    claimed = payload.get("content_sha256")
    unsigned = dict(payload)
    unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise RuntimeError(f"Content hash mismatch: {path}")
    return payload


def build() -> dict[str, Any]:
    audit = verified(AUDIT)
    if audit.get("next_authorized_action") != "RUN_NON_SCIENTIFIC_JSON_ACTION_TRANSPORT_Q0_ONLY":
        raise RuntimeError("Transport audit did not authorize the consumed Q0.")
    payload: dict[str, Any] = {
        "schema_version": "ace-signed-no-tools-json-action-q0-failure-v1",
        "object_id": OBJECT_ID,
        "status": "SIGNED_NO_TOOLS_JSON_ACTION_Q0_FAIL_CODING_PERSONA_CONTAMINATION",
        "classification": "OFFICIAL_SIGNED_RUNTIME_PERSONA_INCOMPATIBLE_WITH_NEUTRAL_JSON_ACTION_ACTOR",
        "transport_id": "ATOMCODE_SIGNED_NO_TOOLS_JSON_ACTION_V1",
        "transport_audit_content_sha256": audit["content_sha256"],
        "runner_source_sha256": sha256_file(RUNNER),
        "provider": "ATOMGIT_CODINGPLAN_SIGNED_GATEWAY",
        "model_profile": "AtomGit-mimo-v2.5-pro",
        "model_id": "mimo-v2.5-pro",
        "atomcode_no_tools": True,
        "model_visible_function_tool_count": 0,
        "mcp_mounted": False,
        "non_scientific_model_request_count": 1,
        "scientific_case_count": 0,
        "appworld_action_count": 0,
        "sq0_case_count": 0,
        "scientific_outcomes_observed": 0,
        "failure": {
            "stage": "FIRST_SYNTHETIC_JSON_ACTION_ROUND",
            "strict_json_parse": False,
            "response_was_non_json_prose": True,
            "observed_semantics": "The model identified itself as an AI coding assistant using function calls and declined to execute the supplied JSON action protocol, asking for a software-engineering task instead.",
            "coding_persona_present": True,
            "provider_or_transport_error": False,
            "tool_schema_contamination": False,
        },
        "source_audit": {
            "coding_persona_unconditionally_assembled": True,
            "model_config_system_prompt_replaces_coding_persona": False,
            "headless_no_tools_removes_coding_persona": False,
            "supported_cli_persona_override_found": False,
            "supported_config_persona_override_found": False,
            "open_source_rebuild_preserves_official_codingplan_signing": False,
        },
        "disposition": {
            "retry_same_q0": False,
            "prompt_tune_same_q0_after_failure": False,
            "run_scientific_sq0_with_codingplan": False,
            "run_f0_r1_with_codingplan": False,
            "codingplan_may_continue_for_non_scientific_coding_work": True,
            "scientific_actor_next_transport": "DIRECT_PROVIDER_API_WITHOUT_ATOMCODE_CODING_PERSONA",
        },
        "next_authorized_action": "DESIGN_PROSPECTIVE_DIRECT_API_SOURCE_FAILURE_QUALIFICATION_ONLY",
        "authority": {
            "codingplan_scientific_actor": False,
            "new_sq0_execution": False,
            "f0_r1": False,
            "p1": False,
            "paper_claim": False,
            "design_only": True,
        },
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    payload = build()
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "non_scientific_model_request_count": payload["non_scientific_model_request_count"],
        "scientific_outcomes_observed": 0,
        "next_authorized_action": payload["next_authorized_action"],
        "content_sha256": payload["content_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
