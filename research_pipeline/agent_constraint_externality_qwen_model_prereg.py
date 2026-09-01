from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from research_pipeline.config import DEFAULT_ENV_FILE, load_env_file

OBJECT_ID = "AGENT-CONSTRAINT-EXTERNALITY-20260831"
ADDENDUM_ID = "AGENT-CONSTRAINT-EXTERNALITY-QWEN-MODEL-PREREG-ADDENDUM-A0"
GENERATED_AT = "2026-09-01T15:30:00+08:00"
LIVE_PARENT_SHA = "da3ebe8fc66503b28183853e251fa291bfb8d118"
REQUESTED_MODEL = "qwen3.7-flash-2026-07-15"
ALLOWED_ALIAS = "qwen3.7-flash"
PROVIDER_ID = "TYPICAL_TOKEN_OPENAI_RESPONSES_API"
PROVIDER_BASE_URL = "https://api.aa.com.cn/api/v1"
API_KEY_ENV = "AA_API_KEY"
BASE_URL_ENV = "AA_BASE_URL"
ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OUTPUT = (
    GENERATED
    / "agent-constraint-externality-qwen-model-prereg-addendum-a0-20260901.json"
)
MANIFEST = (
    GENERATED
    / "agent-constraint-externality-qwen-model-prereg-addendum-a0-manifest-20260901.json"
)


class ModelPreregError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def safe_provider_summary() -> dict[str, Any]:
    load_env_file(DEFAULT_ENV_FILE)
    api_key = os.getenv(API_KEY_ENV, "").strip()
    base_url = os.getenv(BASE_URL_ENV, PROVIDER_BASE_URL).rstrip("/")
    return {
        "configured": bool(api_key),
        "provider": PROVIDER_ID,
        "base_url": base_url,
        "requested_model": REQUESTED_MODEL,
        "allowed_alias": ALLOWED_ALIAS,
        "api_key_env": API_KEY_ENV,
        "api_key_in_output": False,
    }


def validate_zero_outcome_boundary() -> dict[str, Any]:
    qualification = read_json(
        GENERATED
        / "agent-constraint-externality-appworld-compiler-qualification-20260831.json"
    )
    capability = read_json(
        GENERATED / "agent-constraint-externality-capability-contract-20260831.json"
    )
    readiness = read_json(
        GENERATED / "agent-constraint-externality-f0-readiness-20260831.json"
    )
    if qualification["object_id"] != OBJECT_ID:
        raise ModelPreregError("Compiler object identity mismatch.")
    if qualification["verdict"] != "PRE_F0_5_PASS":
        raise ModelPreregError("Model addendum requires PRE_F0_5_PASS.")
    counters = {
        "compiler_provider_calls": qualification["provider_calls"],
        "compiler_scientific_outcomes": qualification[
            "scientific_outcomes_observed"
        ],
        "prior_capability_provider_calls": capability["provider_calls"],
        "prior_capability_scientific_outcomes": capability[
            "scientific_outcomes_observed"
        ],
        "prior_f0_outcomes": readiness["f0_outcomes_observed"],
    }
    if any(counters.values()) or readiness["f0_executed"]:
        raise ModelPreregError(
            "Model selection cannot change after provider calls or scientific outcomes."
        )
    return counters


def build_addendum() -> dict[str, Any]:
    counters = validate_zero_outcome_boundary()
    return {
        "schema_version": "agent-constraint-externality-model-prereg-addendum-v1",
        "generated_at": GENERATED_AT,
        "object_id": OBJECT_ID,
        "addendum_id": ADDENDUM_ID,
        "live_parent_sha": LIVE_PARENT_SHA,
        "status": "QWEN_MODEL_PREREG_ADDENDUM_A0_PASS",
        "change_boundary": {
            "scientific_outcomes_at_switch": 0,
            "scientific_provider_calls_at_switch": 0,
            "f0_executed_at_switch": False,
            "validated_counters": counters,
            "outcome_driven_change": False,
        },
        "supersedes_candidate_order": [
            "doubao-seed-2.0-lite",
            "deepseek-v4-flash",
            "deepseek-v4-pro",
        ],
        "primary_candidate": {
            "requested_model": REQUESTED_MODEL,
            "allowed_alias": ALLOWED_ALIAS,
            "candidate_count": 1,
            "fallback_candidates": [],
            "snapshot_preferred": True,
            "alias_policy": {
                "allowed_only_if_snapshot_unavailable": True,
                "persist_request_model_id": True,
                "persist_resolved_model_metadata": True,
                "persist_provider_base_url": True,
                "persist_capability_feature_snapshot": True,
                "backend_revision_drift_disposition": "STOP_AND_ADJUDICATE",
            },
        },
        "selection_reasons": [
            "FUNCTION_CALLING_SUPPORT",
            "AGENT_AND_TOOL_USE_SUITABILITY",
            "LOW_INFERENCE_COST",
            "SUITABLE_FIRST_STAGE_NON_FRONTIER_CAPABILITY_TIER",
            "STRONGER_SAME_FAMILY_VALIDATION_CAN_BE_ADDED_LATER",
        ],
        "forbidden_selection_reason": "EXPECTED_TO_PRODUCE_MORE_EXTERNALITY",
        "provider_contract": {
            "provider": PROVIDER_ID,
            "base_url": PROVIDER_BASE_URL,
            "responses_endpoint": PROVIDER_BASE_URL + "/responses",
            "models_endpoint": PROVIDER_BASE_URL + "/models",
            "official_documentation": (
                "https://api-doc.aa.com.cn/zh/docs/api/ai-model/text/"
                "post-api-v1-responses"
            ),
            "response_model_field_is_resolved_identity_source": True,
            "custom_function_tools_supported": True,
            "secrets_in_artifacts": False,
        },
        "capability_dispositions": {
            "pass": "FREEZE_QWEN_BACKBONE_AND_ENTER_F0",
            "floor": "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP",
            "ceiling": "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP",
            "provider_or_tool_incompatibility": (
                "CAPABILITY_CALIBRATION_FAIL_INTERFACE_STOP"
            ),
            "automatic_fallback": False,
        },
        "budget_correction": {
            "capability_agent_episodes": 8,
            "f0_source_agent_episodes": 8,
            "f0_probe_agent_episode_min": 108,
            "f0_probe_agent_episode_max": 144,
            "agent_episode_total_max": 160,
            "repair_generation_provider_request_cap": 8,
            "count_separately": [
                "agent_episode_count",
                "agent_model_request_count",
                "updater_model_request_count",
                "provider_request_total",
            ],
            "probe_144_is_total_f0_cap": False,
        },
        "authority": {
            "m1_mock_qualification": True,
            "real_provider_call": False,
            "capability_calibration": False,
            "f0": False,
            "toolsandbox": False,
            "appworld_ul": False,
            "p1": False,
            "second_model": False,
            "method": False,
            "paper_claim": False,
        },
        "scientific_outcomes_observed": 0,
        "provider_calls": 0,
        "gpu_runs": 0,
    }


def main() -> None:
    addendum = build_addendum()
    write_json(OUTPUT, addendum)
    manifest = {
        "schema_version": (
            "agent-constraint-externality-model-prereg-addendum-manifest-v1"
        ),
        "generated_at": GENERATED_AT,
        "object_id": OBJECT_ID,
        "addendum_id": ADDENDUM_ID,
        "status": addendum["status"],
        "files": {
            str(OUTPUT.relative_to(ROOT)): {
                "sha256": file_sha256(OUTPUT),
                "bytes": OUTPUT.stat().st_size,
            }
        },
        "scientific_outcomes_observed": 0,
        "provider_calls": 0,
        "authority": addendum["authority"],
    }
    write_json(MANIFEST, manifest)
    print(json.dumps({
        "status": addendum["status"],
        "requested_model": REQUESTED_MODEL,
        "candidate_count": 1,
        "capability_agent_episodes": 8,
        "scientific_outcomes_observed": 0,
        "provider_calls": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
