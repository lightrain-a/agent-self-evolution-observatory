from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
V4_BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle"
V4_QUAL = GENERATED / "agent-constraint-externality-capability-substrate-recovery-qualification-r4-20260902.json"
PLUS_R5 = GENERATED / "agent-constraint-externality-qwen37plus-capability-result-r5-partial-20260902.json"
Q0_SOURCE = Path("/tmp/ace-live-q0-result.json")
Q0_OUTPUT = GENERATED / "agent-constraint-externality-codingplan-mcp-q0-qualification-20260902.json"
Q1_OUTPUT = GENERATED / "agent-constraint-externality-codingplan-appworld-mcp-q1-predispatch-20260902.json"
CONTRACT_OUTPUT = GENERATED / "agent-constraint-externality-codingplan-qwen38-capability-a0-contract-20260902.json"
MANIFEST_OUTPUT = GENERATED / "agent-constraint-externality-codingplan-qwen38-capability-a0-manifest-20260902.json"

ATOMCODE_BINARY_SHA256 = "ac5ee62fa4c20d70ee4220bdbafa8081051dd717c29a0c0c95de630a989a2113"
ATOMCODE_VERSION = "5.0.9"
MODEL_PROFILE = "AtomGit-qwen3.8-27b"
MODEL_ID = "qwen3.8-27b"
PROVIDER = "ATOMGIT_CODINGPLAN_SIGNED_GATEWAY"
BASE_URL = "https://llm-api.atomgit.com/v1"
CONTEXT_WINDOW = 262_144
MAX_OUTPUT_TOKENS = 65_536
REASONING_EFFORT = "xhigh"
RETRY_MAX_ATTEMPTS = 1
TOOL_CALL_CAP = 16
MODEL_ROUND_CAP = 20
CAPABILITY_FAMILIES = ["ACE-FG-05", "ACE-FG-06", "ACE-TNF-05", "ACE-TNF-06"]
REPEATS = [1, 2]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verified(path: Path, status: str | None = None) -> dict[str, Any]:
    payload = read_json(path)
    if payload.get("object_id") != OBJECT_ID:
        raise RuntimeError(f"Object mismatch: {path}")
    if status is not None and payload.get("status") != status:
        raise RuntimeError(f"Unexpected status in {path}: {payload.get('status')}")
    claimed = payload.get("content_sha256")
    if claimed is not None:
        unsigned = dict(payload); unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise RuntimeError(f"Content hash mismatch: {path}")
    return payload


def build_q0() -> dict[str, Any]:
    raw = read_json(Q0_SOURCE)
    if raw.get("q0_pass") is not True:
        raise RuntimeError("CodingPlan MCP Q0 did not pass.")
    if raw.get("tool_names") != ["mcp__appworld__set_value"]:
        raise RuntimeError("Q0 did not use exactly the intended synthetic MCP tool.")
    if raw.get("tool_success") != [True]:
        raise RuntimeError("Q0 synthetic MCP tool did not succeed.")
    token_events = raw.get("token_events") or []
    payload: dict[str, Any] = {
        "schema_version": "ace-codingplan-mcp-q0-qualification-v1",
        "object_id": OBJECT_ID,
        "status": "CODINGPLAN_MCP_Q0_PASS",
        "provider": PROVIDER,
        "model_profile": MODEL_PROFILE,
        "model_id": MODEL_ID,
        "atomcode_version": ATOMCODE_VERSION,
        "atomcode_binary_sha256": ATOMCODE_BINARY_SHA256,
        "mcp_tool_names": raw["tool_names"],
        "mcp_tool_success": raw["tool_success"],
        "model_round_count": len(token_events),
        "prompt_tokens_total": sum(int(row.get("prompt", 0)) for row in token_events),
        "completion_tokens_total": sum(int(row.get("completion", 0)) for row in token_events),
        "non_mcp_tool_calls": 0,
        "final_text_sha256": hashlib.sha256(str(raw.get("final_text", "")).encode()).hexdigest(),
        "scientific_appworld_episodes": 0,
        "f0_scientific_outcomes_observed": 0,
        "note": "Synthetic tool-use qualification only; prior failed Q0 plumbing attempts are non-scientific infrastructure history.",
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def build_contract(q0: dict[str, Any]) -> dict[str, Any]:
    verified(V4_QUAL, "CAPABILITY_SUBSTRATE_V4_PUBLIC_REACHABILITY_WITH_HEADROOM_PASS")
    q1 = verified(Q1_OUTPUT, "CODINGPLAN_APPWORLD_MCP_LIVE_PREDISPATCH_PASS")
    if q1.get("scientific_dispatch_sent") is not False or int(q1.get("codingplan_model_requests", -1)) != 0:
        raise RuntimeError("Q1 AppWorld MCP qualification crossed the zero-request predispatch boundary.")
    if q1.get("session_mcp_progress_status") != "TOOLS_LISTED":
        raise RuntimeError("Q1 AppWorld MCP catalog was not listed before model dispatch.")
    if q1.get("model_profile") != MODEL_PROFILE:
        raise RuntimeError("Q1 CodingPlan model profile drifted.")
    plus = verified(PLUS_R5, "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP")
    if float(plus["gate"]["target_success_rate"]) != 1.0:
        raise RuntimeError("Expected sealed Plus ceiling witness before CodingPlan candidate selection.")
    payload: dict[str, Any] = {
        "schema_version": "ace-codingplan-qwen38-capability-a0-contract-v1",
        "object_id": OBJECT_ID,
        "execution_id": "CODINGPLAN-QWEN38-27B-CAPABILITY-A0",
        "status": "CODINGPLAN_QWEN38_CAPABILITY_A0_AUTHORIZED",
        "purpose": "Prospective capability calibration only; F0 remains closed.",
        "selection_context": {
            "prior_direct_harness_candidate": "qwen3.7-plus",
            "prior_direct_harness_disposition": "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP",
            "new_candidate_is_post_ceiling_sequential_selection": True,
            "strict_model_only_comparison_to_prior_harness_claimed": False,
        },
        "provider": {
            "id": PROVIDER,
            "base_url": BASE_URL,
            "request_signing": "OFFICIAL_ATOMCODE_BINARY_CLOSED_CODINGPLAN_SIGNER",
            "oauth_secret_persisted_in_artifact": False,
            "atomcode_version": ATOMCODE_VERSION,
            "atomcode_binary_sha256": ATOMCODE_BINARY_SHA256,
        },
        "model": {
            "profile": MODEL_PROFILE,
            "id": MODEL_ID,
            "context_window": CONTEXT_WINDOW,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "reasoning_effort": REASONING_EFFORT,
            "retry_max_attempts": RETRY_MAX_ATTEMPTS,
            "temperature": "ATOMCODE_PROVIDER_DEFAULT_UNSET",
        },
        "codingplan": {
            "plan": "CodingPlan Pro",
            "quota_metric": "requests",
            "rolling_window_hours": 5,
            "rolling_window_limit": 500,
            "total_token_quota": "UNLIMITED_BY_PLAN",
            "scientific_request_accounting": "COUNT_LIVE_TOKEN_EVENTS_AND_PLAN_WINDOW_DELTA",
        },
        "harness": {
            "id": "ATOMCODE_CODINGPLAN_MCP_V1",
            "distinct_from_direct_openai_function_calling": True,
            "base_task_policy": "Complete the task using only AppWorld MCP tools. Preserve unrelated state. Batch independent AppWorld tool calls in the same model round whenever possible. When finished, return a concise completion message.",
            "atomcode_coding_persona_present": True,
            "project_instruction_restricts_tools_to_appworld_mcp": True,
            "non_appworld_mcp_tool_attempt": "FAIL_INTERFACE_AND_STOP",
            "approval_policy": "ALLOW_APPWORLD_MCP_ONLY_DENY_ALL_OTHER_TOOL_REQUESTS",
            "persist_appworld_state_after_every_tool_call": True,
            "ai_session_naming": False,
            "subagents_enabled": False,
        },
        "substrate": {
            "bundle_path": str(V4_BUNDLE.relative_to(ROOT)),
            "bundle_sha256": sha256_file(V4_BUNDLE),
            "qualification_path": str(V4_QUAL.relative_to(ROOT)),
            "qualification_sha256": sha256_file(V4_QUAL),
            "tool_call_cap": TOOL_CALL_CAP,
        },
        "panel": {
            "family_ids": CAPABILITY_FAMILIES,
            "repeats": REPEATS,
            "episode_count": 8,
            "arm": "LOW",
            "model_round_cap_per_episode": MODEL_ROUND_CAP,
            "replacement": False,
            "application_retry": False,
            "provider_retry": False,
        },
        "frozen_gate": {
            "tool_loop_completion_rate_min": 0.75,
            "target_success_rate_min": 0.50,
            "target_success_rate_max": 0.875,
            "non_target_preservation_rate_min": 0.85,
            "malformed_tool_calls_required": 0,
        },
        "q0_qualification_sha256": q0["content_sha256"],
        "q1_appworld_mcp_predispatch_sha256": q1["content_sha256"],
        "partial_effect_firewall": True,
        "authority": {
            "codingplan_capability_a0": True,
            "f0": False,
            "p1": False,
            "toolsandbox": False,
            "appworld_ul": False,
            "paper_claim": False,
        },
        "f0_scientific_outcomes_observed": 0,
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    q0 = build_q0()
    contract = build_contract(q0)
    write_json(Q0_OUTPUT, q0)
    write_json(CONTRACT_OUTPUT, contract)
    manifest: dict[str, Any] = {
        "schema_version": "ace-codingplan-qwen38-capability-a0-manifest-v1",
        "object_id": OBJECT_ID,
        "status": "CODINGPLAN_QWEN38_CAPABILITY_A0_FROZEN",
        "files": {
            str(Q0_OUTPUT.relative_to(ROOT)): {"sha256": sha256_file(Q0_OUTPUT), "bytes": Q0_OUTPUT.stat().st_size},
            str(Q1_OUTPUT.relative_to(ROOT)): {"sha256": sha256_file(Q1_OUTPUT), "bytes": Q1_OUTPUT.stat().st_size},
            str(CONTRACT_OUTPUT.relative_to(ROOT)): {"sha256": sha256_file(CONTRACT_OUTPUT), "bytes": CONTRACT_OUTPUT.stat().st_size},
            str(V4_BUNDLE.relative_to(ROOT)): {"sha256": sha256_file(V4_BUNDLE), "bytes": V4_BUNDLE.stat().st_size},
        },
        "f0_scientific_outcomes_observed": 0,
        "authority": contract["authority"],
    }
    manifest["content_sha256"] = sha256_value(manifest)
    write_json(MANIFEST_OUTPUT, manifest)
    print(json.dumps({
        "status": manifest["status"],
        "model": MODEL_ID,
        "context_window": CONTEXT_WINDOW,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "reasoning_effort": REASONING_EFFORT,
        "episode_count": 8,
        "tool_call_cap": TOOL_CALL_CAP,
        "model_round_cap": MODEL_ROUND_CAP,
        "f0_authorized": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
