#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPECTED_DESIGN_SHA256 = "4ba22e9dee9a753e6a2cf6e136259c0763f12f9503aef2ccc75285571b2817a9"
EXPECTED_FUTURE_TASKS = ["164", "385", "387", "388"]
EXPECTED_CALLS = 32
EXPECTED_MODEL = "doubao-seed-2.0-mini"
EXPECTED_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return obj


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _clean_answer(answer: str | None) -> str:
    if answer is None:
        return ""
    answer = str(answer).strip()
    if answer.startswith("'") and answer.endswith("'"):
        answer = answer[1:-1]
    elif answer.startswith('"') and answer.endswith('"'):
        answer = answer[1:-1]
    answer = re.sub(r"(\w+)[\u2010-\u2015\u2212-](\w+)", r"\1-\2", answer)
    return answer.lower()


def _must_include_score(pred: str, references: list[str]) -> tuple[float, list[dict[str, Any]]]:
    clean_pred = _clean_answer(pred)
    checks: list[dict[str, Any]] = []
    score = 1.0
    for ref in references:
        clean_ref = _clean_answer(ref)
        cur = float(clean_ref in clean_pred)
        score *= cur
        checks.append({"ref": ref, "score": cur})
    return score, checks


def _current_state_evidence(trajectory_json: str) -> tuple[str, list[str]]:
    trajectory = json.loads(trajectory_json)
    states: list[str] = []
    hashes: list[str] = []
    seen: set[str] = set()
    for step in (trajectory.get("steps") or {}).values():
        contents = ((step.get("input_messages") or {}).get("contents") or [])
        if not contents:
            continue
        text = str(contents[-1].get("content") or "")
        if "[Current state starts here]" not in text:
            continue
        text = text.split("[Current state starts here]", 1)[1].strip()
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        states.append(text)
        hashes.append(digest)
    return "\n\n--- RELEASED BROWSER STATE ---\n\n".join(states), hashes


def _answer_prompt(task: str, evidence: str) -> str:
    return f"""You are answering a WebArena read-only benchmark task from a frozen released evidence packet.

RULES:
- Use only the RELEASED BROWSER EVIDENCE below as factual evidence.
- REUSABLE MEMORY is procedural guidance. It may influence how you interpret or organize the evidence, but it is not task-specific ground truth.
- Do not invent reviewer names, ratings, product facts, or quotes that are absent from the released evidence.
- Return only the final answer to the benchmark task. Do not return JSON, browser actions, analysis, or commentary.

REUSABLE MEMORY:
No reusable memory is supplied.

BENCHMARK TASK:
{task}

RELEASED BROWSER EVIDENCE:
{evidence}

FINAL ANSWER:"""


def _import_runtime(contract: dict[str, Any]):
    repo_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo_root))
    vendor = Path(contract["vendor_path"])
    sys.path.insert(0, str(vendor))
    import pyarrow.parquet as pq  # type: ignore

    env_file = Path(contract["provider_env_file"])
    from research_pipeline.config import load_env_file
    from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings

    load_env_file(env_file)
    base = ArkSettings.from_env()
    require(bool(base.api_key), "ARK provider credential unavailable after approved env load")
    require(base.base_url == EXPECTED_BASE_URL, f"provider base URL drift: {base.base_url}")
    settings = ArkSettings(
        api_key=base.api_key,
        base_url=base.base_url,
        default_model=base.default_model,
        timeout_seconds=180.0,
        max_retries=0,
    )
    return pq, ArkResponseStateError, ArkResponsesClient(settings), settings.safe_summary()


def _validate_contract(contract_path: Path, contract: dict[str, Any]) -> None:
    require(contract.get("status") == "FROZEN_BEFORE_PROVIDER_CALLS", "execution contract is not frozen")
    require(contract.get("paper_id") == "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE", "paper mismatch")
    require(contract.get("objection_id") == "PROXY-O5", "objection mismatch")
    require((contract.get("design") or {}).get("sha256") == EXPECTED_DESIGN_SHA256, "design SHA mismatch")
    require(contract.get("future_tasks") == EXPECTED_FUTURE_TASKS, "future task drift")
    require(contract.get("condition") == "no_memory", "condition must be literal no_memory")
    require(int(contract.get("rollouts_per_future_task") or 0) == 8, "replication depth drift")
    require(int(contract.get("expected_provider_calls") or 0) == EXPECTED_CALLS, "provider call ceiling drift")
    authority = contract.get("authority") or {}
    require(authority.get("scientific_reopen_authority") is True, "scientific reopen not authorized")
    require(authority.get("experiment_authority") is True, "experiment not authorized")
    require(authority.get("provider_call_authority") is True, "provider calls not authorized")
    require(authority.get("claim_expansion_authority") is False, "claim expansion must remain unauthorized")
    require(authority.get("submission_authority") is False, "submission must remain unauthorized")
    model = contract.get("model") or {}
    require(model.get("requested") == EXPECTED_MODEL, "model drift")
    require(float(model.get("temperature")) == 0.2, "temperature drift")
    require(int(model.get("max_output_tokens")) == 900, "token budget drift")
    require(model.get("thinking") == "disabled", "thinking setting drift")
    require(model.get("allow_thinking_compatibility_fallback") is False, "thinking fallback forbidden")
    require(int(model.get("provider_retries") or 0) == 0, "provider retry drift")
    require(model.get("substitution_allowed") is False, "model substitution forbidden")
    for key, row in (contract.get("source_artifacts") or {}).items():
        p = Path(row["path"])
        require(p.is_file(), f"missing source artifact: {key}")
        require(sha256(p) == row["sha256"], f"source artifact SHA drift: {key}")
    human = contract.get("human_authority") or {}
    hp = Path(human["path"])
    require(hp.is_file(), "human authority artifact missing")
    require(sha256(hp) == human["sha256"], "human authority artifact SHA drift")
    code = contract.get("code") or {}
    runner_row = code.get("runner") or {}
    require(Path(runner_row["path"]).resolve() == Path(__file__).resolve(), "runner path mismatch")
    require(sha256(Path(__file__)) == runner_row["sha256"], "runner SHA drift after freeze")
    analysis_row = code.get("analysis") or {}
    require(sha256(Path(analysis_row["path"])) == analysis_row["sha256"], "analysis code SHA drift")


def _load_task_data(contract: dict[str, Any], pq) -> dict[str, dict[str, Any]]:
    support = load(Path(contract["source_artifacts"]["support"]["path"]))
    support_rows = {str(row["task_id"]): row for row in support.get("tasks") or []}
    require(set(EXPECTED_FUTURE_TASKS).issubset(support_rows), "frozen support missing future tasks")

    parquet_path = Path(contract["source_artifacts"]["parquet"]["path"])
    released = {
        str(row["task_id"]): row
        for row in pq.read_table(parquet_path, columns=["task_id", "task_prompt", "trajectory_json"]).to_pylist()
    }
    out: dict[str, dict[str, Any]] = {}
    for task in EXPECTED_FUTURE_TASKS:
        sr = support_rows[task]
        require(sr.get("qualified") is True, f"future task no longer qualified: {task}")
        evidence, hashes = _current_state_evidence(str(released[task]["trajectory_json"]))
        require(hashlib.sha256(evidence.encode("utf-8")).hexdigest() == sr["evidence_sha256"], f"evidence SHA drift: {task}")
        require(hashes == sr["released_state_sha256"], f"released state hash sequence drift: {task}")
        out[task] = {
            "task_prompt": str(sr["task_prompt"]),
            "reference_answers": list(sr["reference_answers"]),
            "evidence": evidence,
        }
    return out


def _stage_name(task: str, rollout: int) -> str:
    return f"terminal-{task}-no-memory-r{rollout}"


def _stage_path(private_root: Path, stage: str) -> Path:
    return private_root / "stages" / f"{stage}.json"


def _run_one(*, client, error_type, model_cfg: dict[str, Any], task: str, rollout: int, data: dict[str, Any], private_root: Path) -> dict[str, Any]:
    stage = _stage_name(task, rollout)
    stage_path = _stage_path(private_root, stage)
    if stage_path.is_file():
        cached = load(stage_path)
        require(cached.get("stage") == stage, f"stage-cache identity mismatch: {stage}")
        return cached

    prompt = _answer_prompt(data["task_prompt"], data["evidence"])
    prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    base = {
        "stage": stage,
        "future_task": task,
        "condition": "no_memory",
        "rollout": rollout,
        "prompt_sha256": prompt_sha,
        "requested_model": model_cfg["requested"],
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    try:
        response = client.respond(
            prompt,
            model=str(model_cfg["requested"]),
            max_output_tokens=int(model_cfg["max_output_tokens"]),
            temperature=float(model_cfg["temperature"]),
            thinking=str(model_cfg["thinking"]),
            store=True,
            allow_thinking_compatibility_fallback=False,
        )
        require(response.get("thinking_compatibility_fallback") is False, "provider silently applied thinking fallback")
        require(str(response.get("requested_model")) == EXPECTED_MODEL, "requested model drift in response")
        require(str(response.get("resolved_model")) == EXPECTED_MODEL, f"resolved model drift: {response.get('resolved_model')}")
        answer = str(response.get("text") or "").strip()
        require(bool(answer), "provider returned empty assistant text")
        score, checks = _must_include_score(answer, list(data["reference_answers"]))
        private_payload = {
            **base,
            "status": "complete",
            "response_id": response.get("response_id"),
            "resolved_model": response.get("resolved_model"),
            "usage": response.get("usage") or {},
            "answer": answer,
            "answer_sha256": hashlib.sha256(answer.encode("utf-8")).hexdigest(),
            "benchmark_score": score,
            "evaluator_checks": checks,
            "thinking_requested": response.get("thinking_requested"),
            "thinking_effective": response.get("thinking_effective"),
            "thinking_compatibility_fallback": response.get("thinking_compatibility_fallback"),
        }
    except error_type as exc:
        private_payload = {**base, "status": "provider_state_failure", "provider_receipt": exc.receipt(), "error_type": type(exc).__name__}
    except Exception as exc:
        private_payload = {**base, "status": "provider_or_runtime_failure", "error_type": type(exc).__name__, "error": str(exc)[:1000]}

    atomic_json(stage_path, private_payload)
    return private_payload


def _public_report(contract_path: Path, contract: dict[str, Any], provider_summary: dict[str, Any], stages: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [row for row in stages if row.get("status") == "complete"]
    failures = [row for row in stages if row.get("status") != "complete"]
    rollouts = [
        {
            "future_task": row["future_task"],
            "condition": "no_memory",
            "rollout": row["rollout"],
            "answer_sha256": row["answer_sha256"],
            "benchmark_score": row["benchmark_score"],
            "evaluator_checks": row["evaluator_checks"],
            "response_id": row.get("response_id"),
            "resolved_model": row.get("resolved_model"),
            "usage": row.get("usage") or {},
            "scientific_authority": False,
        }
        for row in completed
    ]
    by_task: dict[str, Any] = {}
    for task in EXPECTED_FUTURE_TASKS:
        rows = [r for r in rollouts if r["future_task"] == task]
        by_task[task] = {
            "complete": len(rows),
            "successes": int(sum(float(r["benchmark_score"]) for r in rows)),
            "success_rate": (sum(float(r["benchmark_score"]) for r in rows) / len(rows)) if rows else None,
        }
    return {
        "schema_version": "1.0",
        "experiment_id": contract["experiment_id"],
        "paper_id": contract["paper_id"],
        "objection_id": contract["objection_id"],
        "status": "O5_NO_MEMORY_COMPLETE" if len(completed) == EXPECTED_CALLS and not failures else "O5_NO_MEMORY_INCOMPLETE",
        "contract_path": str(contract_path.resolve()),
        "contract_sha256": sha256(contract_path),
        "provider": {k: v for k, v in provider_summary.items() if k != "api_key"},
        "summary": {
            "requested_provider_calls": EXPECTED_CALLS,
            "complete_provider_calls": len(completed),
            "provider_or_runtime_failures": len(failures),
            "old_exploratory_no_memory_calls_reused": 0,
            "future_task_rates": by_task,
        },
        "rollouts": rollouts,
        "failures": [
            {
                "future_task": row["future_task"],
                "rollout": row["rollout"],
                "status": row["status"],
                "error_type": row.get("error_type"),
                "provider_receipt": row.get("provider_receipt"),
            }
            for row in failures
        ],
        "scope": "Fresh source-independent no-memory terminal control on exactly four frozen future tasks; secondary branch-location diagnostic only.",
        "scientific_authority": False,
        "experiment_authority": True,
        "claim_expansion_authority": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Execute the frozen 32-call PROXY-O5 no-memory terminal control.")
    ap.add_argument("--contract", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--private-root", required=True, type=Path)
    args = ap.parse_args()

    contract = load(args.contract)
    _validate_contract(args.contract, contract)
    pq, ArkResponseStateError, client, provider_summary = _import_runtime(contract)
    task_data = _load_task_data(contract, pq)
    args.private_root.mkdir(parents=True, exist_ok=True)

    stages: list[dict[str, Any]] = []
    for task in EXPECTED_FUTURE_TASKS:
        for rollout in range(1, 9):
            row = _run_one(
                client=client,
                error_type=ArkResponseStateError,
                model_cfg=contract["model"],
                task=task,
                rollout=rollout,
                data=task_data[task],
                private_root=args.private_root,
            )
            stages.append(row)
            atomic_json(args.output, _public_report(args.contract, contract, provider_summary, stages))
            print(json.dumps({"stage": row["stage"], "status": row["status"], "completed_so_far": sum(x.get("status") == "complete" for x in stages), "seen_so_far": len(stages)}), flush=True)

    report = _public_report(args.contract, contract, provider_summary, stages)
    atomic_json(args.output, report)
    print(json.dumps(report["summary"], indent=2))
    return 0 if report["status"] == "O5_NO_MEMORY_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
