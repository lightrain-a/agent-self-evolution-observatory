"""Freeze the 36-source ReasoningBank writer-input contract for B1 L2B.

R13 makes no model calls. It deterministically serializes only the frozen task
instruction and executed tool-action sequence from the released AWM trajectory,
selects the first-party ReasoningBank success/failure system prompt using the
already-frozen native source outcome, and content-addresses every writer input.

The information boundary follows the archived R6 precedent (task instruction +
executed action sequence, terminal-success label removed from the trace), but
this serializer is a new prospectively frozen R13 serializer and is not claimed
to be byte-identical to the historical R6 serializer.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
CONTRACT_ID = "D2-C45-REASONINGBANK-UNIFORM-WRITER-R13"
EXPECTED_PARQUET_SHA256 = "fc9b0011d384403f21534529da0397ca2aabf29fcb30c2dbb5a3c01c30b1387e"
EXPECTED_RB_COMMIT = "ed80611788292ea739f1effd31f16c53823b8a0d"
EXPECTED_PROMPT_FILE_SHA256 = "073d354bc84a24ba8a2c697133b5d832fe89ca67a53705fb0af419528f7b11ee"
EXPECTED_INDUCE_MEMORY_SHA256 = "97d7da3fe5bd3e37d05e4aa07c050b1154334951cc2cad20619774ae77e0912c"
WRITER_MODEL_FAMILY = "Qwen2.5-32B"
WRITER_TEMPERATURE = 0.0


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def extract_constants(path: Path) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            value = node.value
            for target in targets:
                if isinstance(target, ast.Name) and target.id in {"SUCCESSFUL_SI", "FAILED_SI"}:
                    out[target.id] = ast.literal_eval(value)
    if set(out) != {"SUCCESSFUL_SI", "FAILED_SI"}:
        raise ValueError("ReasoningBank success/failure prompts missing")
    return out


def executed_actions(trajectory: dict[str, Any]) -> list[dict[str, Any]]:
    steps = trajectory.get("steps") or {}
    if not isinstance(steps, dict):
        raise ValueError("trajectory.steps must be an object")
    ordered = sorted(steps, key=lambda x: int(x))
    out: list[dict[str, Any]] = []
    for step_id in ordered:
        step = steps[step_id] or {}
        calls = (((step.get("output_messages") or {}).get("tool_call_message") or {}).get("tool_calls") or [])
        actions: list[Any] = []
        for call in calls:
            args = (call or {}).get("args") or {}
            value = args.get("action")
            if isinstance(value, list):
                actions.extend(value)
        if actions:
            out.append({"step": int(step_id), "actions": actions})
    if not out:
        raise ValueError("no executed tool actions found")
    return out


def serialize_trace(task_prompt: str, trajectory: dict[str, Any]) -> str:
    rows = executed_actions(trajectory)
    lines = [f"Query: {task_prompt}", "", "Executed Action Sequence:"]
    for row in rows:
        lines.append(f"Step {row['step']}: {canonical_json(row['actions'])}")
    return "\n".join(lines)


def load_parquet(path: Path) -> list[dict[str, Any]]:
    try:
        import pandas as pd  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("use an existing pandas+pyarrow environment") from exc
    return [dict(x) for x in pd.read_parquet(path).to_dict(orient="records")]


def parse_trajectory(value: Any) -> tuple[dict[str, Any], bytes]:
    if isinstance(value, str):
        raw = value.encode("utf-8")
        obj = json.loads(value)
    elif isinstance(value, dict):
        raw = canonical_json(value).encode("utf-8")
        obj = value
    else:
        raise ValueError("trajectory_json must be string or object")
    if not isinstance(obj, dict):
        raise ValueError("trajectory_json must decode to object")
    return obj, raw


def build(r9: dict[str, Any], rows: list[dict[str, Any]], prompts: dict[str, str], *, parquet_sha: str, rb_root: Path) -> dict[str, Any]:
    if parquet_sha != EXPECTED_PARQUET_SHA256:
        raise ValueError("frozen parquet digest drift")
    import subprocess
    head = subprocess.check_output(["git", "-C", str(rb_root), "rev-parse", "HEAD"], text=True).strip()
    if head != EXPECTED_RB_COMMIT:
        raise ValueError(f"ReasoningBank commit drift: {head}")
    if sha_file(rb_root / "WebArena/prompts/memory_instruction.py") != EXPECTED_PROMPT_FILE_SHA256:
        raise ValueError("ReasoningBank prompt file digest drift")
    if sha_file(rb_root / "WebArena/induce_memory.py") != EXPECTED_INDUCE_MEMORY_SHA256:
        raise ValueError("ReasoningBank induce_memory digest drift")

    by_id = {str(row.get("task_id")): row for row in rows}
    cohort = r9.get("cohort") or []
    if len(cohort) != 36:
        raise ValueError("R9 cohort must contain 36 rows")
    manifest = []
    status_counts = {"success": 0, "fail": 0}
    total_steps = 0
    total_action_objects = 0
    for unit in cohort:
        task_id = str(unit["source_task_id"])
        row = by_id.get(task_id)
        if row is None:
            raise ValueError(f"missing source task {task_id}")
        native = "success" if bool(row.get("is_successful")) else "fail"
        if native != str(unit.get("source_native_status")):
            raise ValueError(f"native status drift for {task_id}")
        task_prompt = str(row.get("task_prompt") or "")
        traj, raw = parse_trajectory(row.get("trajectory_json"))
        if str(traj.get("task_prompt") or "") != task_prompt:
            raise ValueError(f"task prompt mismatch inside trajectory for {task_id}")
        # Terminal labels/rubrics and all observation/input/current_state content are intentionally excluded.
        compact = serialize_trace(task_prompt, traj)
        actions = executed_actions(traj)
        action_objects = sum(len(s["actions"]) for s in actions)
        total_steps += len(actions)
        total_action_objects += action_objects
        prompt_name = "SUCCESSFUL_SI" if native == "success" else "FAILED_SI"
        system_prompt = prompts[prompt_name]
        writer_user_input = compact
        request_fingerprint = sha_bytes((system_prompt + "\n\0\n" + writer_user_input).encode("utf-8"))
        status_counts[native] += 1
        manifest.append({
            "source_task_id": task_id,
            "downstream_task_id": str(unit["downstream_task_id"]),
            "template_id": str(unit["template_id"]),
            "native_source_status": native,
            "task_prompt_sha256": sha_bytes(task_prompt.encode("utf-8")),
            "raw_trajectory_json_sha256": sha_bytes(raw),
            "compact_trace_sha256": sha_bytes(compact.encode("utf-8")),
            "compact_trace_chars": len(compact),
            "executed_steps": len(actions),
            "executed_action_objects": action_objects,
            "system_prompt": prompt_name,
            "system_prompt_sha256": sha_bytes(system_prompt.encode("utf-8")),
            "writer_request_fingerprint": request_fingerprint,
        })

    if status_counts != {"success": 15, "fail": 21}:
        raise ValueError(f"source status distribution drift: {status_counts}")
    ids = [x["source_task_id"] for x in manifest]
    if len(set(ids)) != 36:
        raise ValueError("source-task uniqueness drift")
    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "contract_id": CONTRACT_ID,
        "recorded_date": "2026-08-24",
        "status": "WRITER_INPUTS_AND_INFORMATION_BOUNDARY_FROZEN_MODEL_ARTIFACT_AND_CALL_AUTHORITY_BLOCKED",
        "role": "PROSPECTIVE_ZERO_CALL_SOURCE_MEMORY_REALIZATION_CONTRACT",
        "source_bindings": {
            "parquet_sha256": parquet_sha,
            "reasoningbank_commit": head,
            "memory_instruction_py_sha256": EXPECTED_PROMPT_FILE_SHA256,
            "induce_memory_py_sha256": EXPECTED_INDUCE_MEMORY_SHA256,
        },
        "information_boundary": {
            "serializer_name": "R13_R6_STYLE_ACTION_SEQUENCE_V1",
            "historical_precedent": "Archived R6 preserves task instruction and executed action sequence and removes terminal success labels; R13 freezes a new deterministic serializer under the same information boundary and does not claim byte identity with R6.",
            "included": ["source task instruction", "ordered executed tool action objects"],
            "excluded": ["is_successful field from trace text", "rubric_results", "terminal evaluator results", "input_messages/DOM/observations", "current_state reasoning/memory/next_goal", "tool response content", "timing/token/cost metadata"],
            "native_source_status_used_only_to_choose_first_party_writer_system_prompt": True,
            "selection_or_serialization_uses_downstream_outcome": False,
        },
        "writer_contract": {
            "writer_model_family": WRITER_MODEL_FAMILY,
            "historical_R6_precedent_model": "Qwen2.5-32B",
            "temperature": WRITER_TEMPERATURE,
            "one_realized_memory_record_per_source_task": True,
            "uniform_realization_for_all_36_sources": True,
            "writer_request_count_if_authorized": 36,
            "exact_model_artifact_digest_required_before_calls": True,
            "current_exact_model_artifact_bound": False,
            "automatic_model_substitution_forbidden": True,
            "prompt_or_serializer_change_after_any_writer_output_forbidden": True,
            "output_contract": {
                "preserve_complete_writer_response_utf8": True,
                "derive_memory_items_by": "writer_response.split('\\n\\n')",
                "require_join_roundtrip_equality": True,
                "content_address_response_and_joined_memory_bytes_before_downstream_outcomes": True,
                "at_most_three_memory_items_per_first_party_prompt": True,
            },
            "support_retry_policy": {
                "semantic_retry_or_prompt_change": False,
                "outcome_driven_regeneration": False,
                "exact_same_request_retry_only_for_transport_or_empty_response": True,
                "maximum_exact_retries_per_source": 1,
                "first_complete_parseable_response_is_frozen": True,
            },
        },
        "summary": {
            "source_tasks": 36,
            "native_source_status_counts": status_counts,
            "total_executed_steps_in_compact_inputs": total_steps,
            "total_executed_action_objects": total_action_objects,
            "all_writer_inputs_content_addressed": True,
            "model_calls_executed": 0,
            "exact_memory_bytes_bound": False,
        },
        "writer_input_manifest": manifest,
        "downstream_L2_binding": {
            "after_writer_realization": "Freeze each selected source record ID/order and exact memory_items bytes once; render R9 STATUS_S versus STATUS_F around the same bytes only.",
            "memory_regeneration_between_status_arms_forbidden": True,
            "status_must_not_affect_retrieval_or_source_selection": True,
            "historical_R5_or_bridge_pooling": False,
        },
        "execution_gate": {
            "writer_inputs_frozen": True,
            "writer_model_family_and_temperature_frozen": True,
            "exact_writer_model_artifact_bound": False,
            "writer_calls_permitted": False,
            "exact_memory_bytes_bound": False,
            "downstream_l2_outcomes_permitted": False,
            "scientific_authority": False,
            "experiment_model_call_authority": False,
        },
        "scientific_verdict": "NO_VERDICT_WRITER_INPUT_CONTRACT_ONLY",
        "authority": {"scientific": False, "experiment": False, "model_calls": False, "browser_actions": False, "evaluator_calls": False, "gpu": False, "submission": False},
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--r9", type=Path, required=True)
    p.add_argument("--source-parquet", type=Path, required=True)
    p.add_argument("--reasoningbank-root", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-writer-input-contract-r13.json"))
    a = p.parse_args()
    if sha_file(a.source_parquet) != EXPECTED_PARQUET_SHA256:
        raise SystemExit("frozen parquet digest drift")
    prompt_file = a.reasoningbank_root / "WebArena/prompts/memory_instruction.py"
    prompts = extract_constants(prompt_file)
    payload = build(json.loads(a.r9.read_text(encoding="utf-8")), load_parquet(a.source_parquet), prompts, parquet_sha=EXPECTED_PARQUET_SHA256, rb_root=a.reasoningbank_root)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "sources": payload["summary"]["source_tasks"], "steps": payload["summary"]["total_executed_steps_in_compact_inputs"], "actions": payload["summary"]["total_executed_action_objects"], "writer_calls": payload["summary"]["model_calls_executed"], "calls_permitted": payload["execution_gate"]["writer_calls_permitted"]}))


if __name__ == "__main__":
    main()
