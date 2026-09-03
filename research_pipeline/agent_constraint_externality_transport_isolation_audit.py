from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OUTPUT = GENERATED / "agent-constraint-externality-atomcode-transport-isolation-audit-20260903.json"
ATOMCODE = Path.home() / ".local/bin/atomcode"
SOURCE = Path("/tmp/atomcode-source-inspect")
SOURCE_COMMIT = "287bff70f9400c24f4afd8fcf4762fbab63d8efa"
EXPECTED_BINARY_SHA256 = "ac5ee62fa4c20d70ee4220bdbafa8081051dd717c29a0c0c95de630a989a2113"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_source_identity() -> dict[str, Any]:
    if not SOURCE.is_dir():
        raise RuntimeError("AtomCode source inspection checkout is absent.")
    commit = subprocess.check_output(["git", "-C", str(SOURCE), "rev-parse", "HEAD"], text=True).strip()
    if commit != SOURCE_COMMIT:
        raise RuntimeError(f"AtomCode source commit drifted: {commit}")
    binary_sha = file_sha256(ATOMCODE)
    if binary_sha != EXPECTED_BINARY_SHA256:
        raise RuntimeError("Installed AtomCode binary hash drifted.")
    version = subprocess.check_output([str(ATOMCODE), "--version"], text=True).strip()
    return {
        "source_repository": "https://atomgit.com/atomgit_atomcode/atomcode.git",
        "source_commit": commit,
        "source_describe": subprocess.check_output(
            ["git", "-C", str(SOURCE), "describe", "--always", "--tags"], text=True
        ).strip(),
        "installed_binary": str(ATOMCODE),
        "installed_binary_version": version,
        "installed_binary_sha256": binary_sha,
        "source_files": {
            "crates/atomcode-coding/src/parts.rs": file_sha256(SOURCE / "crates/atomcode-coding/src/parts.rs"),
            "crates/atomcode-daemon/src/kernel_runtime.rs": file_sha256(SOURCE / "crates/atomcode-daemon/src/kernel_runtime.rs"),
            "crates/atomcode-cli/src/main.rs": file_sha256(SOURCE / "crates/atomcode-cli/src/main.rs"),
            "crates/atomcode-auth/src/gateway_crypto.rs": file_sha256(SOURCE / "crates/atomcode-auth/src/gateway_crypto.rs"),
            "crates/atomcode-codingplan-crypto/src/lib.rs": file_sha256(SOURCE / "crates/atomcode-codingplan-crypto/src/lib.rs"),
        },
    }


def build() -> dict[str, Any]:
    identity = checked_source_identity()
    payload: dict[str, Any] = {
        "schema_version": "ace-atomcode-transport-isolation-audit-v1",
        "object_id": OBJECT_ID,
        "status": "OFFICIAL_ATOMCODE_5_0_9_DAEMON_CANNOT_PROVIDE_SIGNED_MCP_ONLY_TOOL_SCHEMA",
        "classification": "TRANSPORT_SCHEMA_ISOLATION_UNAVAILABLE_IN_OFFICIAL_SIGNED_DAEMON",
        "identity": identity,
        "findings": {
            "generic_tools_disabled_config_exists": False,
            "tools_config_scope": "AtomCode 5.0.9 ToolsConfig contains only todo policy; there is no generic disabled-native-tools list.",
            "daemon_prepare_tools": True,
            "daemon_prepare_mcp": "cfg.mcp",
            "daemon_cli_no_tools_flag": False,
            "headless_cli_no_tools_flag": True,
            "headless_no_tools_also_disables_mcp": True,
            "prepare_native_tool_registration": "When PrepareOptions.tools is true, native coding tools and codeintel are registered before MCP tools are appended.",
            "mcp_registration_requires_tools_true": True,
            "permission_guard_removes_schema_before_model_request": False,
            "permission_guard_effect": "Deny can prevent execution only after the model has selected a native tool; it cannot remove that tool from the model-visible request schema.",
            "request_lifecycle_hook_can_mutate_tool_defs": False,
            "request_hook_boundary": "pre_request mutates messages, pre_request_options mutates options, on_request is read-only; provider tool definitions are supplied separately.",
            "open_source_crypto_is_official_signer": False,
            "open_source_crypto_stub": True,
            "self_rebuilt_binary_can_preserve_official_codingplan_signing": False,
        },
        "v5_collision": {
            "v2_native_tool_collision": "read_file",
            "v5_native_tool_collision": "read_file",
            "recurrence_establishes_structural_not_one_off_failure": True,
        },
        "rejected_next_actions": [
            "RUN_SQ0_V6_UNDER_UNMODIFIED_DAEMON",
            "TREAT_PERMISSION_DENY_AS_SCHEMA_ISOLATION",
            "REBUILD_OPEN_SOURCE_BINARY_AND_ASSUME_CODINGPLAN_SIGNING_SURVIVES",
            "REUSE_V5_CASES_AFTER_TRANSPORT_CHANGE",
        ],
        "prospective_transport_candidate": {
            "id": "ATOMCODE_SIGNED_NO_TOOLS_JSON_ACTION_V1",
            "official_binary_unchanged": True,
            "official_signing_path_preserved": True,
            "atomcode_headless_no_tools": True,
            "model_visible_native_function_tools": 0,
            "model_visible_mcp_function_tools": 0,
            "environment_actions": "External controller supplies a content-addressed JSON action schema in text, executes only declared AppWorld actions, and returns observations on the next signed model round.",
            "scientific_harness_changed": True,
            "requires_fresh_harness_and_backbone_qualification": True,
            "may_not_inherit_mimo25pro_b3_capability_pass": True,
        },
        "next_authorized_action": "RUN_NON_SCIENTIFIC_JSON_ACTION_TRANSPORT_Q0_ONLY",
        "scientific_execution_authority": {
            "sq0_v6": False,
            "new_sq0": False,
            "f0_r1": False,
            "p1": False,
            "paper_claim": False,
        },
        "provider_requests_added_by_audit": 0,
        "scientific_outcomes_observed": 0,
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    payload = build()
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "transport_candidate": payload["prospective_transport_candidate"]["id"],
        "next_authorized_action": payload["next_authorized_action"],
        "scientific_execution_authorized": False,
        "content_sha256": payload["content_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
