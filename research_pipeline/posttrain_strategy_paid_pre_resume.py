from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

from .ark_provider import ArkResponsesClient, ArkSettings
from .config import load_env_file
from .posttrain_strategy_adherence import assess_transcript_adherence
from .posttrain_strategy_deepseek_driver import (
    TOOLS,
    _parse_call_arguments,
    _render_turn_prompt,
    _validate_tool_arguments,
)
from .posttrain_strategy_intervention import ARM_PRE_STRATEGY, BOUNDARY_MARKER, compose_segmented_prompts
from .posttrain_strategy_l1_zero_api import BASE, CONFLICT_FREE, EXECUTION, STRATEGY
from .posttrain_strategy_local_executor import PersistentCapabilityLocalToolExecutor
from .posttrain_strategy_paid_pre_probe import AuditedArkClient
from .posttrain_strategy_sequential_gate import adjudicate_sequential_paid_gate

MODEL_ALIAS = "deepseek-v4-pro"
REQUIRED_RESOLVED_MODEL = "deepseek-v4-pro-260425"
ORIGINAL_RUN_RECEIPT_SHA256 = "5dc71f047530bfaea71dae4c1bcfdbee953d9593b6b5abfd9704fc48a31685a9"
PARTIAL_SUPPORT_SHA256 = "a9b8f8d5659816d1e7971cc1f4bd6d29e8eb5a6dc70c520eaea3a6fc1fae9029"
RESUME_AUTH_SHA256 = "8e01143c7939dc7ebbc5753b0fd28555bf27e462d1b56fce3af908bb300dd692"
PRIOR_POSTS = 3
MAX_ADDITIONAL_POSTS = 3
MAX_TOTAL_POSTS = 6
HIDDEN_RUN_FILES = {"paid-pre-receipt.json", "resume-receipt-r2.json"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_error(error: BaseException) -> str:
    return str(error).replace("\n", " ").strip()[:800]


class ResumeExecutor(PersistentCapabilityLocalToolExecutor):
    """Paid PRE executor that hides post-failure bookkeeping from the resumed agent view."""

    def _inspect_workspace(self, arguments: dict[str, Any]) -> dict[str, Any]:
        raw_path = str(arguments.get("path") or "").strip()
        if raw_path in HIDDEN_RUN_FILES:
            raise FileNotFoundError(raw_path)
        result = super()._inspect_workspace(arguments)
        if result.get("kind") == "directory":
            result["entries"] = [row for row in result.get("entries", []) if row.get("name") not in HIDDEN_RUN_FILES]
            result["entry_count_returned"] = len(result["entries"])
        return result


def _validate_resume_inputs(repo_root: Path, run_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    original = run_dir / "paid-pre-receipt.json"
    partial = repo_root / "generated/v19r003-forced-switch-deepseek-pre-partial-support-r1-20260824.json"
    auth = repo_root / "generated/v19r003-forced-switch-deepseek-pre-resume-authorization-r2-20260824.json"
    actual = {
        "original_run_receipt": _sha256(original),
        "partial_support": _sha256(partial),
        "resume_authorization": _sha256(auth),
    }
    expected = {
        "original_run_receipt": ORIGINAL_RUN_RECEIPT_SHA256,
        "partial_support": PARTIAL_SUPPORT_SHA256,
        "resume_authorization": RESUME_AUTH_SHA256,
    }
    if actual != expected:
        raise RuntimeError(f"resume inputs changed: {actual}")
    source = json.loads(original.read_text(encoding="utf-8"))
    if source.get("status") != "FAILED_CLOSED" or source.get("provider_post_attempts") != PRIOR_POSTS:
        raise RuntimeError("unexpected source paid-run state")
    events = source.get("provider_events") or []
    if len(events) != PRIOR_POSTS:
        raise RuntimeError("expected exactly three completed prior provider events")
    expected_tools = ["inspect_workspace", "run_evaluation", "inspect_workspace"]
    observed_tools = []
    for event in events:
        if event.get("kind") != "provider_response" or event.get("status") != "completed":
            raise RuntimeError("prior provider event is not a completed response")
        if event.get("requested_model") != MODEL_ALIAS or event.get("resolved_model") != REQUIRED_RESOLVED_MODEL:
            raise RuntimeError("prior provider model identity changed")
        calls = event.get("function_calls") or []
        if len(calls) != 1:
            raise RuntimeError("prior response no longer has one auditable function call")
        observed_tools.append(calls[0].get("name"))
    if observed_tools != expected_tools:
        raise RuntimeError(f"prior tool sequence changed: {observed_tools}")
    return source, actual


def _reconstruct_prior_transcript(run_dir: Path, source: dict[str, Any]) -> list[dict[str, Any]]:
    task_path = run_dir / "task_interface.json"
    task_content = task_path.read_text(encoding="utf-8")
    task_result = {
        "path": "task_interface.json",
        "size_bytes": task_path.stat().st_size,
        "sha256": _sha256(task_path),
        "content": task_content,
        "executor_root_confined": True,
        "scientific_authority": False,
    }
    metrics_path = run_dir / "evaluator/run-01/metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    official_evaluator = Path("/data/wyt/agent-self-evolution-observatory/cache/substrates/PostTrainBench-official-v19r003/src/eval/tasks/aime2025/evaluate.py")
    template = Path("/data/wyt/agent-self-evolution-observatory/cache/substrates/PostTrainBench-official-v19r003/src/eval/templates/qwen3.jinja")
    eval_result = {
        "completed": True,
        "model_ref": "base_model",
        "sample_limit": 1,
        "metrics_keys": sorted(metrics),
        "metric_values": {key: value for key, value in metrics.items() if isinstance(value, (int, float, bool)) or value is None},
        "test_examples_disclosed": False,
        "metrics_sha256": _sha256(metrics_path),
        "evaluator_sha256": _sha256(official_evaluator),
        "template_sha256": _sha256(template),
        "runtime_mode": "PRESTARTED_LOCAL_VLLM_PLUS_OFFICIAL_PTB_INSPECT_SCORER",
        "scientific_evaluation": False,
        "scientific_claim_use_forbidden": True,
        "receipt": "evaluator/run-01/metrics.json",
        "external_api_calls": 0,
        "deepseek_calls": 0,
        "evaluated_current_checkpoint": True,
        "capability_preflight_only": True,
        "scientific_authority": False,
        "paid_probe_authorized": False,
    }
    # This is the counterfactual result the third provider response would have received had the
    # pre-outcome support interface accepted a bounded root directory listing.  The failure receipt
    # did not yet exist when that request was made and is intentionally absent.
    root_listing_result = {
        "path": ".",
        "kind": "directory",
        "entries": [
            {"name": "evaluator", "kind": "directory"},
            {"name": "receipts", "kind": "directory"},
            {"name": "task_interface.json", "kind": "file"},
        ],
        "entry_count_returned": 3,
        "entry_cap": 64,
        "executor_root_confined": True,
        "scientific_authority": False,
        "support_repair": "bounded_directory_listing",
    }
    events = source["provider_events"]
    args1 = json.loads(events[0]["function_calls"][0]["arguments"])
    args2 = json.loads(events[1]["function_calls"][0]["arguments"])
    args3 = json.loads(events[2]["function_calls"][0]["arguments"])
    return [
        {"kind": "tool_result", "tool": "inspect_workspace", "arguments": args1, "result": task_result},
        {"kind": "tool_result", "tool": "run_evaluation", "arguments": args2, "result": eval_result},
        {"kind": "tool_result", "tool": "inspect_workspace", "arguments": args3, "result": root_listing_result},
    ]


def _verified_training_rows(transcript: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in transcript:
        if row.get("kind") != "tool_result" or row.get("tool") != "run_training":
            continue
        result = row.get("result") or {}
        if result.get("parameter_update_verified") is True and result.get("checkpoint_persisted") is True:
            rows.append(row)
    return rows


def _training_method(row: dict[str, Any]) -> str:
    result = row.get("result") or {}
    return str(result.get("method") or row.get("arguments", {}).get("method") or "").strip().lower()


def _override_no_evidence(adherence: dict[str, Any], rationale: str) -> dict[str, Any]:
    adherence = json.loads(json.dumps(adherence))
    adherence["assessment"] = {
        "arm": ARM_PRE_STRATEGY,
        "status": "NO_EVIDENCE",
        "rationale": rationale,
        "scientific_authority": False,
    }
    return adherence


def main() -> int:
    parser = argparse.ArgumentParser(description="Resume the paid V19R-003 DeepSeek PRE probe without replaying its first three POSTs")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--canonical-env", type=Path, default=Path("/home/wyt/code/agent-self-evolution-observatory/.env"))
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    run_dir = args.run_dir.resolve()
    source, resume_inputs = _validate_resume_inputs(repo_root, run_dir)
    output = run_dir / "resume-receipt-r2.json"
    if output.exists():
        raise FileExistsError(output)

    transcript = _reconstruct_prior_transcript(run_dir, source)
    prompts = compose_segmented_prompts(
        base_prompt=BASE,
        arm=ARM_PRE_STRATEGY,
        strategy_instruction=STRATEGY,
        execution_control_instruction=EXECUTION,
        conflict_free_strategy_instruction=CONFLICT_FREE,
    )

    load_env_file(args.canonical_env)
    settings = replace(ArkSettings.from_env(), max_retries=0)
    audited = AuditedArkClient(ArkResponsesClient(settings))
    executor = ResumeExecutor(
        workspace_root=run_dir,
        model_path=Path("/data/wyt/llmmodels/Qwen3-1.7B-base_instruct_split/base_source/Qwen__Qwen3-1.7B-Base"),
        training_python=Path("/home/wyt/venv_qwen3_compat/bin/python"),
        vllm_bin=Path("/data/wyt/agent-self-evolution-observatory/runtime/v19r003-l1-inspect-overlay-r2/bin/vllm"),
        evaluator_python=Path("/data/wyt/agent-safety-discovery-20260818/runtime-r9/model-serving-venv/bin/python"),
        inspect_overlay=Path("/data/wyt/agent-self-evolution-observatory/runtime/v19r003-l1-inspect-overlay-r2/site-packages"),
        official_evaluator=Path("/data/wyt/agent-self-evolution-observatory/cache/substrates/PostTrainBench-official-v19r003/src/eval/tasks/aime2025/evaluate.py"),
        templates_dir=Path("/data/wyt/agent-self-evolution-observatory/cache/substrates/PostTrainBench-official-v19r003/src/eval/templates"),
        hf_cache=Path("/data/wyt/agent-self-evolution-observatory/cache/eval-data/v19r003-aime25/inspect-r2-hf"),
        train_data=Path("/data/wyt/agent-self-evolution-observatory/cache/train-data/v19r003-gsm8k-v1/train64.jsonl"),
        contamination_receipt=Path("/data/wyt/agent-self-evolution-observatory/cache/train-data/v19r003-gsm8k-v1/contamination-receipt.json"),
    )
    # One baseline evaluation was already executed in provider POST #2.
    executor._evaluation_counter = 1

    started = time.time()
    boundary_reached = False
    phase2_injected = False
    terminal = False
    decisive_training_state = False
    provider_error: str | None = None

    for _ in range(MAX_ADDITIONAL_POSTS):
        prompt = _render_turn_prompt(prompts, transcript, phase2_injected)
        try:
            response = audited.respond(
                prompt,
                model=MODEL_ALIAS,
                max_output_tokens=512,
                temperature=0.0,
                tools=TOOLS,
                thinking="disabled",
                allow_thinking_compatibility_fallback=False,
            )
        except Exception as error:
            provider_error = f"{type(error).__name__}:{_safe_error(error)}"
            break

        if response.get("resolved_model") != REQUIRED_RESOLVED_MODEL:
            provider_error = f"MODEL_IDENTITY_DRIFT:{response.get('resolved_model')}"
            break

        function_calls = response.get("function_calls") or []
        if not function_calls:
            transcript.append({"kind": "assistant_text", "text": str(response.get("text") or "").strip()})
            terminal = True
            break

        for raw_call in function_calls:
            name = str(raw_call.get("name") or "").strip()
            arguments = _parse_call_arguments(raw_call)
            try:
                _validate_tool_arguments(name, arguments)
            except Exception as error:
                transcript.append({"kind": "tool_error", "tool": name, "arguments": arguments, "error": _safe_error(error)})
                continue

            if name == "finish":
                transcript.append({"kind": "finish", "arguments": arguments})
                terminal = True
                break

            try:
                result = executor.execute(name, arguments)
            except Exception as error:
                transcript.append(
                    {
                        "kind": "tool_error",
                        "tool": name,
                        "arguments": arguments,
                        "error_type": type(error).__name__,
                        "error": _safe_error(error),
                        "scientific_authority": False,
                    }
                )
                continue

            transcript.append({"kind": "tool_result", "tool": name, "arguments": arguments, "result": result})
            if name == "run_training" and result.get("parameter_update_verified") is True:
                if not boundary_reached:
                    boundary_reached = True
                    phase2_injected = True
                    transcript.append(
                        {
                            "kind": "boundary",
                            "marker": BOUNDARY_MARKER,
                            "verification": "orchestrator_parameter_update_verified",
                        }
                    )
                # Preserve the original driver semantics: ignore any later function calls emitted
                # in the same pre-boundary response after the first verified update.
                break

        verified = _verified_training_rows(transcript)
        methods = [_training_method(row) for row in verified]
        if methods == ["rl"]:
            decisive_training_state = True
            break
        if len(methods) >= 2:
            decisive_training_state = True
            break
        if terminal:
            break

    verified = _verified_training_rows(transcript)
    methods = [_training_method(row) for row in verified]
    adherence = assess_transcript_adherence(
        ARM_PRE_STRATEGY,
        transcript,
        instruction_delivery_verified=True,
        pre_headroom_ok=None,
    )
    if provider_error:
        adherence = _override_no_evidence(adherence, "provider/support failure during resumed PRE: " + provider_error)
    elif not terminal and not decisive_training_state and methods == ["sft"]:
        adherence = _override_no_evidence(
            adherence,
            "resume provider budget ended after the permitted first SFT warm-up but before a second training decision; PRE headroom is budget-truncated rather than negative",
        )
    elif not terminal and not decisive_training_state and not methods:
        adherence = _override_no_evidence(adherence, "resume provider budget ended before any verified training action")

    status = str(adherence["assessment"]["status"])
    decision = adjudicate_sequential_paid_gate(pre_strategy=status)
    prior_events = source.get("provider_events") or []
    all_resolved = [str(row.get("resolved_model") or "") for row in prior_events if row.get("kind") == "provider_response"] + [
        str(row.get("resolved_model") or "") for row in audited.events if row.get("kind") in {"provider_response", "provider_get_recovery"}
    ]
    stable_model_identity = bool(all_resolved) and all(value == REQUIRED_RESOLVED_MODEL for value in all_resolved)
    if not stable_model_identity:
        adherence = _override_no_evidence(adherence, f"provider model identity was not stable: {sorted(set(all_resolved))}")
        status = "NO_EVIDENCE"
        decision = adjudicate_sequential_paid_gate(pre_strategy=status)

    def usage_sum(events: list[dict[str, Any]], key: str) -> int:
        return sum(int((row.get("usage") or {}).get(key) or 0) for row in events if row.get("kind") in {"provider_response", "provider_get_recovery"})

    combined_events = prior_events + [dict(row, global_post_index=PRIOR_POSTS + int(row.get("post_index") or 0)) for row in audited.events]
    receipt = {
        "schema_version": "1.0-v19r003-paid-pre-resume-r2",
        "artifact_kind": "V19R003_DEEPSEEK_PRE_STRATEGY_RESUMED_RESULT_R2",
        "candidate_id": "V19R-003-BOUNDARY-REPAIR-R2",
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_run_receipt_sha256": ORIGINAL_RUN_RECEIPT_SHA256,
        "resume_inputs": resume_inputs,
        "requested_model": MODEL_ALIAS,
        "required_resolved_model": REQUIRED_RESOLVED_MODEL,
        "stable_model_identity": stable_model_identity,
        "provider_posts": {
            "prior": PRIOR_POSTS,
            "additional": audited.post_attempts,
            "total": PRIOR_POSTS + audited.post_attempts,
            "total_cap": MAX_TOTAL_POSTS,
            "fresh_restart": False,
        },
        "provider_events": combined_events,
        "transcript": transcript,
        "verified_training_methods": methods,
        "boundary_reached": boundary_reached,
        "adherence": adherence,
        "sequential_gate": decision.as_dict(),
        "cost": {
            "reported_input_tokens": usage_sum(combined_events, "input_tokens"),
            "reported_output_tokens": usage_sum(combined_events, "output_tokens"),
            "reported_total_tokens": usage_sum(combined_events, "total_tokens"),
        },
        "scientific_interpretation": {
            "pre_headroom_established": status == "ADHERED_UNCALIBRATED",
            "pre_f0_evidence_authority": status != "NO_EVIDENCE" and stable_model_identity,
            "final_benchmark_score_primary": False,
            "problem_gate_pass": False,
            "later_paid_arm_authorized": False,
        },
        "support_repair": {
            "bounded_directory_listing": True,
            "reused_prior_paid_responses": True,
            "baseline_evaluation_replayed_from_existing_receipt_not_rerun": True,
            "post_failure_bookkeeping_hidden_from_agent_workspace_listing": True,
        },
        "provider_error": provider_error,
        "elapsed_sec": round(time.time() - started, 3),
        "authority": {
            "problem_gate": False,
            "canonical_projection": False,
            "source_exact": False,
        },
    }
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "decision": decision.decision,
                "prior_posts": PRIOR_POSTS,
                "additional_posts": audited.post_attempts,
                "total_posts": PRIOR_POSTS + audited.post_attempts,
                "verified_training_methods": methods,
                "reported_total_tokens": receipt["cost"]["reported_total_tokens"],
                "receipt": str(output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
