#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q03_output_mcp_20260903 as q03
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json, sha256_file, sha256_text
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime_v7 import parse_action

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-fresh4-q08-transport-stress-contract-20260903.json"
Q08 = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-q08-successor-statistics-contract-20260903.json"
Q08_ADJ = ROOT / "consultations/c1-pacta-msr-fresh3-postgate-gpt56-review-q08-adjudication-20260903.md"
Q03_CLOSURE = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q03-output-mcp-closure-20260903.json"
FRESH4_TRANSPORT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh4-source-transport-amendment-20260903.json"
FRESH4_POOL = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh4-pool-20260903.json"
SOURCE_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh4-source-20260903-v1")
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-fresh4-q08-transport-stress-20260903-v1")
EXPECTED = {
    "q08": "b523187e431ec952d0ba5d3a960ae878a5c8e421d5498c736ff557413184df6d",
    "q08_adjudication": "0189f5828c9b620ce1dfbb74e1d0c21c4310ba955c11d07d5439737ef681a532",
    "q03_closure": "af311a6a2785bff2d06cc12febf5288de5f4759a156d3ca4ac0407cd550837ea",
    "fresh4_transport": "c1229439b0b0aa3e80e7c6e2747d49b5378263d93f5af192597735a5bcaa42da",
    "fresh4_pool": "9582877385413807dea6316c25585d5714662cce17f83fa298934229dc4f0927",
}
LIVE_TIMEOUT_SECONDS = 900
LOGICAL_OUTPUTS = 8
NONFINAL_OUTPUTS = 7
FINAL_OBJECT = {"decision": "finish", "message": "FRESH4_TRANSPORT_FINAL_OK"}
SYSTEM = (
    "This is a synthetic offline MiniSWEAgent transport stress, not a real repository task. "
    "For every NONFINAL turn, return a THOUGHT section followed by exactly one fenced bash command. "
    "The command is only proposed and will not be executed. Do not use any host tool. "
    "When the user explicitly says FINALIZE_JSON, ignore the nonfinal formatting rule and return only one ordinary JSON object "
    "with decision=finish and message=FRESH4_TRANSPORT_FINAL_OK, with no markdown or bash fence."
)
INITIAL_USER = (
    "Synthetic task. We will simulate a long multi-turn debugging conversation using deterministic observations. "
    "This is NONFINAL turn 1. Propose one harmless read-only bash command that would inspect SYNTHETIC_MARKER_01."
)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def verify_inputs() -> dict[str, str]:
    paths = {
        "q08": Q08,
        "q08_adjudication": Q08_ADJ,
        "q03_closure": Q03_CLOSURE,
        "fresh4_transport": FRESH4_TRANSPORT,
        "fresh4_pool": FRESH4_POOL,
    }
    observed: dict[str, str] = {}
    for key, path in paths.items():
        if not path.is_file():
            raise RuntimeError(f"STOP_Q08_STRESS_INPUT_MISSING:{key}")
        digest = sha256_file(path)
        observed[key] = digest
        if digest != EXPECTED[key]:
            raise RuntimeError(f"STOP_Q08_STRESS_INPUT_HASH_DRIFT:{key}:{digest}")
    q08 = json.loads(Q08.read_text())
    q03 = json.loads(Q03_CLOSURE.read_text())
    amendment = json.loads(FRESH4_TRANSPORT.read_text())
    pool = json.loads(FRESH4_POOL.read_text())
    if q08.get("status") != "Q08_SUCCESSOR_STATISTICS_FROZEN_PRE_FRESH4":
        raise RuntimeError("STOP_Q08_STRESS_SUCCESSOR_CONTRACT_INVALID")
    if q03.get("status") != "ATOMGIT_QWEN38_Q03_CONTROLLED_OUTPUT_MCP_PASS":
        raise RuntimeError("STOP_Q08_STRESS_Q03_INVALID")
    channel = amendment.get("source_output_channel") or {}
    if (
        amendment.get("status") != "FROZEN_PRE_SOURCE_OUTCOME"
        or channel.get("allowed_tool") != q03_module_allowed_tool()
        or channel.get("kind") != "text"
        or channel.get("host_native_tools_allowed") is not False
        or channel.get("model_rounds_per_logical_output") != 1
    ):
        raise RuntimeError("STOP_Q08_STRESS_FRESH4_TRANSPORT_INVALID")
    if pool.get("candidate_count") != 10 or pool.get("prior_exclusion_count") != 89:
        raise RuntimeError("STOP_Q08_STRESS_FRESH4_POOL_INVALID")
    return observed


def q03_module_allowed_tool() -> str:
    return q03.ALLOWED_TOOL


def blueprint() -> dict[str, Any]:
    return {
        "system": SYSTEM,
        "initial_user": INITIAL_USER,
        "nonfinal_turns": NONFINAL_OUTPUTS,
        "logical_outputs": LOGICAL_OUTPUTS,
        "observation_template": "SYNTHETIC_OBSERVATION_{turn:02d}: prior proposed command was captured but not executed. Marker SYNTHETIC_MARKER_{next_turn:02d} is now the next synthetic inspection target. This is NONFINAL turn {next_turn}. Return the next THOUGHT plus one fenced bash command.",
        "final_user": "FINALIZE_JSON. The synthetic task is complete. Return only the JSON object {\"decision\":\"finish\",\"message\":\"FRESH4_TRANSPORT_FINAL_OK\"}. No markdown, THOUGHT, or bash fence.",
        "final_object": FINAL_OBJECT,
        "scientific_source_tasks_used": 0,
    }


def prepare(root: Path) -> dict[str, Any]:
    if root.exists():
        raise RuntimeError("Q08 stress root exists; no overwrite")
    if SOURCE_ROOT.exists():
        raise RuntimeError("STOP_Q08_STRESS_FRESH4_SOURCE_ALREADY_STARTED")
    observed = verify_inputs()
    if q03.MAX_OUTPUT_TOKENS != 32768 or q03.MODEL_ID != "qwen3.8-27b" or q03.MODEL_PROFILE != "AtomGit-qwen3.8-27b":
        raise RuntimeError("STOP_Q08_STRESS_PROVIDER_ENVELOPE_DRIFT")
    root.mkdir(parents=True)
    atomic_json(root / "episode-blueprint.json", blueprint())
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "FRESH4_Q08_TRANSPORT_STRESS_PREPARE_PASS",
        "contract_sha256": sha256_file(CONTRACT),
        "input_sha256": observed,
        "blueprint_sha256": sha256_file(root / "episode-blueprint.json"),
        "model_profile": q03.MODEL_PROFILE,
        "model_id": q03.MODEL_ID,
        "allowed_tool": q03.ALLOWED_TOOL,
        "kind": "text",
        "max_tokens": q03.MAX_OUTPUT_TOKENS,
        "live_timeout_seconds": LIVE_TIMEOUT_SECONDS,
        "logical_outputs": LOGICAL_OUTPUTS,
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
        "writer_calls": 0,
        "binder_calls": 0,
        "shadow_calls": 0,
        "final_calls": 0,
    }
    atomic_json(root / "prepare.json", result)
    return result


def run_stress(root: Path) -> dict[str, Any]:
    if SOURCE_ROOT.exists():
        raise RuntimeError("STOP_Q08_STRESS_FRESH4_SOURCE_ALREADY_STARTED")
    if not (root / "prepare.json").is_file():
        raise RuntimeError("prepare first")
    if (root / "stress-result.json").exists() or (root / "fixtures").exists():
        raise RuntimeError("Q08 stress already attempted; no retry/overwrite")
    verify_inputs()
    q03.LIVE_TIMEOUT_SECONDS = LIVE_TIMEOUT_SECONDS
    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": INITIAL_USER},
    ]
    rows: list[dict[str, Any]] = []
    stopped = None
    for turn in range(1, NONFINAL_OUTPUTS + 1):
        fixture = {
            "fixture_id": f"turn-{turn:02d}",
            "kind": "text",
            "exact": False,
            "expected": None,
            "messages": list(messages),
        }
        result = q03.run_live_fixture(root, fixture)
        content = result.get("captured_content")
        parse_pass = False
        action = None
        thought_pass = False
        if isinstance(content, str):
            thought_pass = "THOUGHT:" in content
            try:
                action = parse_action(content)
                parse_pass = True
            except Exception:
                parse_pass = False
        row_pass = (
            result.get("pass") is True
            and result.get("captured_kind") == "text"
            and result.get("tool_names") == [q03.ALLOWED_TOOL]
            and result.get("prohibited_tool") is None
            and result.get("error_message") is None
            and result.get("model_round_count") == 1
            and thought_pass
            and parse_pass
        )
        row = {
            "turn": turn,
            "transport_pass": result.get("pass"),
            "captured_kind": result.get("captured_kind"),
            "tool_names": result.get("tool_names"),
            "prohibited_tool": result.get("prohibited_tool"),
            "error_message": result.get("error_message"),
            "model_round_count": result.get("model_round_count"),
            "prompt_tokens": result.get("prompt_tokens"),
            "completion_tokens": result.get("completion_tokens"),
            "thought_pass": thought_pass,
            "action_parse_pass": parse_pass,
            "action_sha256": sha256_text(action) if action else None,
            "content_sha256": result.get("captured_content_sha256"),
            "pass": row_pass,
        }
        rows.append(row)
        if not row_pass:
            stopped = f"nonfinal_turn_{turn}_failed"
            break
        messages.append({"role": "assistant", "content": str(content)})
        if turn < NONFINAL_OUTPUTS:
            next_turn = turn + 1
            observation = blueprint()["observation_template"].format(turn=turn, next_turn=next_turn)
            messages.append({"role": "user", "content": observation})

    final_row = None
    if stopped is None and len(rows) == NONFINAL_OUTPUTS:
        messages.append({"role": "user", "content": blueprint()["final_user"]})
        fixture = {"fixture_id": "turn-08-final", "kind": "text", "exact": False, "expected": None, "messages": list(messages)}
        result = q03.run_live_fixture(root, fixture)
        content = result.get("captured_content")
        json_pass = False
        parsed = None
        if isinstance(content, str):
            try:
                parsed = json.loads(content.strip())
                json_pass = isinstance(parsed, dict) and set(parsed) == {"decision", "message"} and parsed == FINAL_OBJECT
            except Exception:
                json_pass = False
        final_pass = (
            result.get("pass") is True
            and result.get("captured_kind") == "text"
            and result.get("tool_names") == [q03.ALLOWED_TOOL]
            and result.get("prohibited_tool") is None
            and result.get("error_message") is None
            and result.get("model_round_count") == 1
            and json_pass
        )
        final_row = {
            "turn": 8,
            "transport_pass": result.get("pass"),
            "captured_kind": result.get("captured_kind"),
            "tool_names": result.get("tool_names"),
            "prohibited_tool": result.get("prohibited_tool"),
            "error_message": result.get("error_message"),
            "model_round_count": result.get("model_round_count"),
            "prompt_tokens": result.get("prompt_tokens"),
            "completion_tokens": result.get("completion_tokens"),
            "ordinary_json_finish_pass": json_pass,
            "content_sha256": result.get("captured_content_sha256"),
            "pass": final_pass,
        }
        rows.append(final_row)
        if not final_pass:
            stopped = "final_json_turn_failed"

    passed = len(rows) == LOGICAL_OUTPUTS and all(row.get("pass") for row in rows)
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "FRESH4_Q08_REPEATED_TURN_FINALIZATION_STRESS_PASS" if passed else "HOLD_FRESH4_Q08_TRANSPORT_STRESS",
        "pass": passed,
        "attempted": len(rows),
        "required": LOGICAL_OUTPUTS,
        "nonfinal_passed": sum(bool(row.get("pass")) for row in rows[:NONFINAL_OUTPUTS]),
        "final_json_pass": bool(final_row and final_row.get("pass")),
        "stop_reason": stopped,
        "rows": rows,
        "total_model_rounds": sum(int(row.get("model_round_count") or 0) for row in rows),
        "total_prompt_tokens": sum(int(row.get("prompt_tokens") or 0) for row in rows),
        "total_completion_tokens": sum(int(row.get("completion_tokens") or 0) for row in rows),
        "prohibited_tool_attempts": sum(1 for row in rows if row.get("prohibited_tool")),
        "scientific_source_tasks_used": 0,
        "fresh4_source_authorized": passed,
        "claim_authority": "NO_MSR_METHOD_EFFECT_EVIDENCE",
    }
    atomic_json(root / "stress-result.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--phase", choices=("prepare", "run"), required=True)
    args = parser.parse_args()
    result = prepare(args.root) if args.phase == "prepare" else run_stress(args.root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
