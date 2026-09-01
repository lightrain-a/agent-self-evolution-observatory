#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_actor_pool import (
    ActorRolloutConfig,
    atomic_json,
    file_sha256,
    run_actor_rollout,
)
from research_pipeline.e2_r17_local_openai_react import LocalOpenAIReactLLM

MODEL_NAME = "qwen3-8b-open-weight-e2-qualification"
MODEL_CONFIG_SHA256 = "f7c4eadfbbf522470667b797a3c89be2524832d2d599797248dc304fff447c30"
TOKENIZER_CONFIG_SHA256 = "d5d09f07b48c3086c508b30d1c9114bd1189145b74e982a265350c923acd8101"
TOKENIZER_JSON_SHA256 = "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
GENERATION_CONFIG_SHA256 = "2325da0f15bb848e018c5ae071b7943332e9f871d6b60e2ed22ca97d4cb993d2"
MODEL_REVISION_RECEIPT_SHA256 = "02d3ae6409a74c6f2d8ac1790fabec536cb4671518b062e279ac0563fb6757d1"
MODEL_VERIFICATION_RECEIPT_SHA256 = "86e5151358a45eb3092b120250b7b5a4af58b185094e870d38046d64d5b059ee"
MODEL_FILES_MANIFEST_SHA256 = "73ea6bb0a38168c9b923bd12fe8c1bfca9a0b8c39ebd5e8fb9d2ef8e97789bac"
MODEL_REVISION = "b968826d9c46dd6066d109eabc6255188de91218"
MINDMEMOS_COMMIT = "90491828726e1540442b17cd445d0308d0b8093c"
SUITE_MANIFEST_SHA256 = "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4"
SPLIT_MANIFEST_SHA256 = "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9"
QUALIFICATION_TASK_IDS = (
    "r17-b0-agj-p4",
    "r17-b0-fmv-p1",
    "r17-b0-ioc-p3",
    "r17-b0-msp-p3",
    "r17-b0-ska-p3",
    "r17-b0-tsr-p3",
)
SIMPLE_PROBE_REPEATS = 3


def canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_mindmemos(root: Path) -> tuple[Any, Any]:
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    source_roots = [root / "src/mindmemos_eval", root / "src/mindmemos_sdk", root / "src/mindmemos"]
    for source in reversed(source_roots):
        if str(source) not in sys.path:
            sys.path.insert(0, str(source))
    from mindmemos_eval.skills.agents import ReactAgentFactory
    from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv

    return ReactAgentFactory, SpreadsheetBenchEnv


async def simple_tool_reproducibility_probe(
    *,
    base_url: str,
    model: str,
    max_output_tokens: int,
    seed: int,
) -> dict[str, Any]:
    messages = [
        {"role": "system", "content": "Call the supplied function exactly once. Do not answer in prose."},
        {"role": "user", "content": "Use add_numbers to calculate 7 + 5."},
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_numbers",
                "description": "Add two integers.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "integer"},
                        "b": {"type": "integer"},
                    },
                    "required": ["a", "b"],
                    "additionalProperties": False,
                },
            },
        }
    ]
    rows: list[dict[str, Any]] = []
    for repeat in range(SIMPLE_PROBE_REPEATS):
        adapter = LocalOpenAIReactLLM(
            base_url=base_url,
            requested_model=model,
            required_resolved_model=model,
            max_output_tokens=max_output_tokens,
            seed=seed,
        )
        message = await adapter(messages, tools)
        rows.append(
            {
                "repeat": repeat,
                "message": message,
                "message_sha256": canonical_sha(message),
                "receipts": adapter.public_receipts(),
            }
        )
    first = rows[0]["message"]
    calls = first.get("tool_calls") or []
    expected_call = False
    if len(calls) == 1 and (calls[0].get("function") or {}).get("name") == "add_numbers":
        try:
            args = json.loads((calls[0].get("function") or {}).get("arguments") or "{}")
        except json.JSONDecodeError:
            args = {}
        expected_call = args == {"a": 7, "b": 5}
    return {
        "repeats": SIMPLE_PROBE_REPEATS,
        "rows": rows,
        "exact_message_reproduction": len({row["message_sha256"] for row in rows}) == 1,
        "expected_tool_call": expected_call,
    }


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    ReactAgentFactory, SpreadsheetBenchEnv = load_mindmemos(args.mindmemos_root)
    mind_head = subprocess.check_output(
        ["git", "-C", str(args.mindmemos_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if mind_head != MINDMEMOS_COMMIT:
        raise RuntimeError("MindMemOS qualification commit drift")
    if subprocess.check_output(
        ["git", "-C", str(args.mindmemos_root), "status", "--short"], text=True
    ).strip():
        raise RuntimeError("MindMemOS qualification tree is dirty")
    split_path = args.suite_root / "r17_split_manifest.json"
    if file_sha256(args.suite_root / "suite_manifest.json") != SUITE_MANIFEST_SHA256:
        raise RuntimeError("controlled suite manifest drift")
    if file_sha256(split_path) != SPLIT_MANIFEST_SHA256:
        raise RuntimeError("controlled split manifest drift")
    split = json.loads(split_path.read_text(encoding="utf-8"))
    development = set(map(str, split["development"]))
    if not set(QUALIFICATION_TASK_IDS).issubset(development):
        raise RuntimeError("qualification task set escaped the development split")

    model_files = {
        "config.json": MODEL_CONFIG_SHA256,
        "tokenizer_config.json": TOKENIZER_CONFIG_SHA256,
        "tokenizer.json": TOKENIZER_JSON_SHA256,
        "generation_config.json": GENERATION_CONFIG_SHA256,
        ".r9-model-revision.json": MODEL_REVISION_RECEIPT_SHA256,
        ".r9-hf-verification.json": MODEL_VERIFICATION_RECEIPT_SHA256,
    }
    for name, expected in model_files.items():
        path = args.model_path / name
        if not path.is_file() or file_sha256(path) != expected:
            raise RuntimeError(f"local model identity drift: {name}")
    verification = json.loads((args.model_path / ".r9-hf-verification.json").read_text(encoding="utf-8"))
    if not verification.get("formal_gate_eligible"):
        raise RuntimeError("local model verification receipt is not formal-gate eligible")
    if verification.get("revision") != MODEL_REVISION:
        raise RuntimeError("local model exact revision drift")
    if verification.get("files_manifest_sha256") != MODEL_FILES_MANIFEST_SHA256:
        raise RuntimeError("local model content-addressed file manifest drift")

    initial_skill = args.mindmemos_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx"
    skill_md = initial_skill / "SKILL.md"
    if not skill_md.is_file():
        raise RuntimeError("frozen initial SpreadsheetBench skill missing")
    skill_sha = file_sha256(skill_md)
    env = SpreadsheetBenchEnv(args.suite_root, args.run_root)
    cases = {case.id: case for case in env.load_cases("all")}
    metadata_rows = json.loads(
        (args.suite_root / "r17_controlled_metadata.json").read_text(encoding="utf-8")
    )
    metadata = {str(row["id"]): row for row in metadata_rows}
    evaluator_sources = [
        args.mindmemos_root / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/evaluator.py",
        args.mindmemos_root / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py",
    ]

    simple_probe = await simple_tool_reproducibility_probe(
        base_url=args.base_url,
        model=args.model,
        max_output_tokens=min(args.max_output_tokens, 256),
        seed=args.seed,
    )
    if not simple_probe["exact_message_reproduction"]:
        raise RuntimeError("simple local tool-call probe was not exactly reproducible")
    if not simple_probe["expected_tool_call"]:
        raise RuntimeError("simple local tool-call probe did not emit the expected call")
    tasks: list[dict[str, Any]] = []
    for task_id in QUALIFICATION_TASK_IDS:
        adapter = LocalOpenAIReactLLM(
            base_url=args.base_url,
            requested_model=args.model,
            required_resolved_model=args.model,
            max_output_tokens=args.max_output_tokens,
            seed=args.seed,
        )
        factory = ReactAgentFactory(
            adapter,
            max_turns=args.max_turns,
            skill_sources=[initial_skill],
            python_path=sys.executable,
        )
        config = ActorRolloutConfig(
            requested_model=args.model,
            required_resolved_model=args.model,
            max_turns=args.max_turns,
            skill_source=str(initial_skill),
            skill_pre_sha256=skill_sha,
            failure_family=str(metadata[task_id]["primary_failure_family"]),
            experiment_mode="local_evaluator_runtime_qualification",
        )
        ref = await run_actor_rollout(
            env=env,
            case=cases[task_id],
            rollout_index=0,
            agent_factory=factory,
            adapter=adapter,
            config=config,
            evaluator_sources=evaluator_sources,
        )
        receipts = adapter.public_receipts()
        if not receipts:
            trajectory = json.loads(Path(ref.trajectory_path).read_text(encoding="utf-8"))
            receipts = list(trajectory.get("adapter_receipts") or [])
        tasks.append(
            {
                "task_id": task_id,
                "failure_family": metadata[task_id]["primary_failure_family"],
                "score": float(ref.score),
                "trajectory_ref_path": str(
                    args.run_root / "cases" / task_id / "rollout_0" / "r17_trajectory_ref.json"
                ),
                "trajectory_ref_sha256": file_sha256(
                    args.run_root / "cases" / task_id / "rollout_0" / "r17_trajectory_ref.json"
                ),
                "provider_calls": len(receipts),
                "finish_reasons": [str(row.get("finish_reason") or "") for row in receipts],
                "receipt_bundle_sha256": canonical_sha(receipts),
            }
        )

    success_count = int(sum(row["score"] for row in tasks))
    no_length_truncation = all(
        finish != "length" for row in tasks for finish in row["finish_reasons"]
    )
    nondegenerate_headroom = 0 < success_count < len(tasks)
    passed = (
        simple_probe["exact_message_reproduction"]
        and simple_probe["expected_tool_call"]
        and no_length_truncation
        and nondegenerate_headroom
    )
    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-local-evaluator-runtime-qualification",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": (
            "PASS_LOCAL_EVALUATOR_RUNTIME_QUALIFICATION"
            if passed
            else "FAIL_LOCAL_EVALUATOR_RUNTIME_QUALIFICATION"
        ),
        "scientific_outcome": False,
        "central_mechanism_adjudicated": False,
        "historical_hold_reinterpreted": False,
        "selection_rule": (
            "Before outcomes, take the first lexicographic development task from each "
            "of the six controlled task families."
        ),
        "qualification_task_ids": list(QUALIFICATION_TASK_IDS),
        "criteria": {
            "simple_tool_call_exact_across_three_repeats": simple_probe[
                "exact_message_reproduction"
            ],
            "simple_tool_call_semantically_correct": simple_probe["expected_tool_call"],
            "no_length_finish_reason": no_length_truncation,
            "development_success_count_strictly_between_zero_and_six": nondegenerate_headroom,
        },
        "simple_probe": simple_probe,
        "development_success_count": success_count,
        "development_task_count": len(tasks),
        "tasks": tasks,
        "model": {
            "served_name": args.model,
            "path": str(args.model_path),
            "file_sha256": model_files,
            "revision": MODEL_REVISION,
            "files_manifest_sha256": MODEL_FILES_MANIFEST_SHA256,
            "seed": args.seed,
            "temperature": 0.0,
            "top_p": 1.0,
            "enable_thinking": False,
            "provider_retry_limit": 0,
        },
        "runtime": {
            "python_executable": sys.executable,
            "python_version": platform.python_version(),
            "mindmemos_root": str(args.mindmemos_root),
            "mindmemos_commit": mind_head,
            "base_url": args.base_url,
            "bound_code": {
                "qualification_runner": {
                    "path": str(Path(__file__).resolve()),
                    "sha256": file_sha256(Path(__file__).resolve()),
                },
                "local_adapter": {
                    "path": str((ROOT / "research_pipeline/e2_r17_local_openai_react.py").resolve()),
                    "sha256": file_sha256(ROOT / "research_pipeline/e2_r17_local_openai_react.py"),
                },
                "actor_rollout": {
                    "path": str((ROOT / "research_pipeline/e2_r17_actor_pool.py").resolve()),
                    "sha256": file_sha256(ROOT / "research_pipeline/e2_r17_actor_pool.py"),
                },
            },
        },
        "suite": {
            "root": str(args.suite_root),
            "suite_manifest_sha256": SUITE_MANIFEST_SHA256,
            "split_manifest_sha256": SPLIT_MANIFEST_SHA256,
        },
        "initial_skill_sha256": skill_sha,
        "authority": {
            "freeze_scientific_protocol": passed,
            "execute_scientific_negative_control": False,
            "execute_mrw": False,
            "paper_promotion": False,
        },
        "private_credentials_included": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite-root", type=Path, required=True)
    parser.add_argument("--mindmemos-root", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:18080")
    parser.add_argument("--model", default=MODEL_NAME)
    parser.add_argument("--seed", type=int, default=1717)
    parser.add_argument("--max-turns", type=int, default=10)
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.model != MODEL_NAME:
        raise SystemExit(f"qualification model must be {MODEL_NAME}")
    if args.seed != 1717:
        raise SystemExit("qualification seed must be 1717")
    try:
        summary = asyncio.run(main_async(args))
    except Exception as exc:  # noqa: BLE001 - qualification failures are terminal evidence
        summary = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-local-evaluator-runtime-qualification",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "FAIL_LOCAL_EVALUATOR_RUNTIME_QUALIFICATION",
            "technical_error": f"{type(exc).__name__}: {exc}"[:2000],
            "scientific_outcome": False,
            "central_mechanism_adjudicated": False,
            "historical_hold_reinterpreted": False,
            "authority": {
                "freeze_scientific_protocol": False,
                "execute_scientific_negative_control": False,
                "execute_mrw": False,
                "paper_promotion": False,
            },
        }
    atomic_json(args.output, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["status"].startswith("PASS_") else 3


if __name__ == "__main__":
    raise SystemExit(main())
