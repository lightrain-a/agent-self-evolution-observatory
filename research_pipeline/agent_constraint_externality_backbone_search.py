from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import research_pipeline.agent_constraint_externality_codingplan_qwen38_capability as live
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
READINESS = GENERATED / "agent-constraint-externality-f0-readiness-20260831.json"
DEEPSEEK_RESULT = GENERATED / "agent-constraint-externality-codingplan-deepseek-live-capability-b0-result-20260903.json"
CATALOG_OUTPUT = GENERATED / "agent-constraint-externality-codingplan-catalog-b1-20260903.json"
DEEPSEEK_CLOSEOUT = GENERATED / "agent-constraint-externality-codingplan-deepseek-live-capability-b0-closeout-20260903.json"
SEARCH_STATE_OUTPUT = GENERATED / "agent-constraint-externality-capability-backbone-search-state-b1-20260903.json"

TESTED_IDS = ("qwen3.7-plus", "qwen3.8-27b", "deepseek-v4-flash")
EXPECTED_REMAINING = ("GLM-5.2", "mimo-v2.5", "mimo-v2.5-pro")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verified(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    if payload.get("object_id") != OBJECT_ID:
        raise RuntimeError(f"Object mismatch: {path}")
    claimed = payload.get("content_sha256")
    if claimed is not None:
        unsigned = dict(payload)
        unsigned.pop("content_sha256")
        if claimed != sha256_value(unsigned):
            raise RuntimeError(f"Content hash mismatch: {path}")
    return payload


def refresh_catalog() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="ace-codingplan-catalog-b1-") as directory:
        root = Path(directory)
        atom_home, workdir = root / "atomcode-home", root / "workdir"
        atom_home.mkdir(); workdir.mkdir()
        shutil.copy2(Path.home() / ".atomcode/auth.toml", atom_home / "auth.toml")
        os.chmod(atom_home / "auth.toml", 0o600)
        source_config = Path.home() / ".atomcode/config.toml"
        if source_config.is_file():
            shutil.copy2(source_config, atom_home / "config.toml")
        else:
            (atom_home / "config.toml").write_text("auto_update = false\n", encoding="utf-8")
        process = None
        try:
            process, base, token = live.start_daemon(atom_home=atom_home, workdir=workdir, log_path=root / "daemon.log")
            before = live.codingplan_usage(base, token)
            setup = live.http_json(base, token, "/codingplan/setup", method="POST", body={}, timeout=90)
            after = live.codingplan_usage(base, token)
            models = live.http_json(base, token, "/models")
            delta = int(after["used"]) - int(before["used"])
            if delta != 0:
                raise RuntimeError(f"Catalog refresh consumed CodingPlan model requests: {delta}")
            safe_models = [
                {
                    "profile": row.get("provider"),
                    "model_id": row.get("model"),
                    "provider_type": row.get("provider_type"),
                    "effort_applicable": bool(row.get("effort_applicable")),
                    "effort_levels": row.get("effort_levels") or [],
                }
                for row in models
            ]
            import tomllib
            config = tomllib.loads((atom_home / "config.toml").read_text(encoding="utf-8"))
            config_models = config.get("models", {})
            for row in safe_models:
                entry = config_models.get(row["profile"], {})
                row["context_window"] = entry.get("context_window")
                row["max_tokens"] = entry.get("max_tokens")
                row["reasoning_effort_levels_config"] = entry.get("reasoning_effort_levels") or []
            payload: dict[str, Any] = {
                "schema_version": "ace-codingplan-catalog-b1-v1",
                "object_id": OBJECT_ID,
                "status": "CODINGPLAN_ACCOUNT_CATALOG_REFRESH_PASS_ZERO_MODEL_REQUESTS",
                "setup_returned_success": bool(setup.get("success", setup.get("status", True))),
                "codingplan_window_before": before,
                "codingplan_window_after": after,
                "codingplan_model_request_delta": delta,
                "models": safe_models,
                "scientific_outcomes_observed": 0,
                "authority": {"capability_search": True, "f0": False, "p1": False},
            }
            payload["content_sha256"] = sha256_value(payload)
            return payload
        finally:
            if process is not None:
                live.terminate_process(process)


def deepseek_closeout() -> dict[str, Any]:
    result = verified(DEEPSEEK_RESULT)
    if result.get("status") != "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP":
        raise RuntimeError("DeepSeek B0 is not frozen at floor.")
    gate = result["gate"]
    if float(gate["target_success_rate"]) != 0.875 or float(gate["non_target_preservation_rate"]) != 1.0:
        raise RuntimeError("DeepSeek aggregate gate drifted.")
    if float(gate["tool_loop_completion_rate"]) != 0.625:
        raise RuntimeError("DeepSeek completion-rate evidence drifted.")
    before, after = result["codingplan_window_first_before"], result["codingplan_window_last_after"]
    window_delta = int(after["used"]) - int(before["used"])
    rounds = int(result["model_round_count"])
    if rounds != 72 or window_delta != 72:
        raise RuntimeError("DeepSeek request accounting drifted.")
    payload: dict[str, Any] = {
        "schema_version": "ace-codingplan-deepseek-live-capability-b0-closeout-v1",
        "object_id": OBJECT_ID,
        "status": "CODINGPLAN_DEEPSEEK_LIVE_B0_FLOOR_CLOSEOUT",
        "result_artifact": str(DEEPSEEK_RESULT.relative_to(ROOT)),
        "result_file_sha256": sha256_file(DEEPSEEK_RESULT),
        "result_content_sha256": result["content_sha256"],
        "verdict": result["status"],
        "gate": gate,
        "tool_loop_completed_measurements": 5,
        "tool_loop_incomplete_measurements": 3,
        "accounting": {
            "scientific_model_round_count": rounds,
            "codingplan_account_window_request_delta": window_delta,
            "account_level_unattributed_request_count": window_delta - rounds,
            "appworld_tool_call_total": int(result["appworld_tool_call_total"]),
            "prompt_tokens_total": int(result["prompt_tokens_total"]),
            "completion_tokens_total": int(result["completion_tokens_total"]),
        },
        "interpretation_boundary": "B0 fails the frozen capability gate because tool-loop completion is below 0.75. The 16-tool cap is not relaxed after observing this result.",
        "scientific_outcomes_observed": 0,
        "authority": {"f0": False, "p1": False, "toolsandbox": False, "appworld_ul": False, "paper_claim": False},
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def build_search_state(catalog: dict[str, Any], closeout: dict[str, Any]) -> dict[str, Any]:
    readiness = read_json(READINESS)
    models = [row["model_id"] for row in catalog["models"]]
    remaining = tuple(model for model in models if model not in TESTED_IDS)
    if remaining != EXPECTED_REMAINING:
        raise RuntimeError(f"Unexpected remaining CodingPlan catalog order: {remaining}")
    payload: dict[str, Any] = {
        "schema_version": "ace-capability-backbone-search-state-b1-v1",
        "object_id": OBJECT_ID,
        "status": "CAPABILITY_BACKBONE_SEARCH_CONTINUE_GLM52_NEXT",
        "selection_policy": "FREEZE_CURRENT_ACCOUNT_CATALOG_ORDER_AFTER_EXCLUDING_ALREADY_VALIDLY_TESTED_MODELS; STOP_AT_FIRST_CAPABILITY_PASS",
        "catalog_artifact": str(CATALOG_OUTPUT.relative_to(ROOT)),
        "catalog_content_sha256": catalog["content_sha256"],
        "already_validly_tested": [
            {"model_id": "qwen3.7-plus", "verdict": readiness["direct_api_capability_result_status"]},
            {"model_id": "qwen3.8-27b", "verdict": readiness["codingplan_capability_result_status"]},
            {"model_id": "deepseek-v4-flash", "verdict": closeout["verdict"]},
        ],
        "remaining_frozen_order": list(remaining),
        "next_candidate": {"model_id": "GLM-5.2", "profile": "AtomGit-GLM-5.2"},
        "stop_rule": "STOP_BACKBONE_SEARCH_IMMEDIATELY_AT_FIRST_CAPABILITY_CALIBRATION_PASS; FLOOR_OR_CEILING_ADVANCES_ONLY_TO_NEXT_PREDECLARED_MODEL",
        "gate_unchanged": {"tool_loop_completion_min": 0.75, "target_success_min": 0.50, "target_success_max": 0.875, "non_target_preservation_min": 0.85, "malformed_tool_calls_required": 0},
        "scientific_outcomes_observed": 0,
        "authority": {"next_capability_candidate": True, "f0": False, "p1": False, "paper_claim": False},
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    catalog = refresh_catalog(); write_json(CATALOG_OUTPUT, catalog)
    closeout = deepseek_closeout(); write_json(DEEPSEEK_CLOSEOUT, closeout)
    state = build_search_state(catalog, closeout); write_json(SEARCH_STATE_OUTPUT, state)
    print(json.dumps({
        "catalog_request_delta": catalog["codingplan_model_request_delta"],
        "deepseek_verdict": closeout["verdict"],
        "next_candidate": state["next_candidate"],
        "remaining_order": state["remaining_frozen_order"],
        "f0_authorized": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
