from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from .ark_provider import ArkResponsesClient, ArkSettings
from .d2_proxy_reward_memory_f1 import _cached_call, _load_raw
from .discovery_engine_terminal_replication import _jsha, _write_json


DEFAULT_PARQUET = Path("generated/research-data/paper-yield-d5-c01/parquet-cache/wa_awm_shuffle1-shopping_run1.parquet")
DEFAULT_VENDOR = Path("generated/research-data/paper-yield-d5-c01/vendor")
DEFAULT_TASK_CONFIG = Path("generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/benchmarks/wa/test_configs/test.raw.json")
DEFAULT_EVALUATOR_SOURCE = Path("generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/browser_use/custom/evaluators/wa/wa_evaluators.py")
DEFAULT_F0 = Path("generated/d2-proxy-reward-memory-f0.json")
DEFAULT_F0_RAW_ROOT = Path("generated/research-data/d2-proxy-reward-memory-f0")
DEFAULT_SUPPORT = Path("generated/d2-proxy-reward-terminal-fixed-evidence-support.json")
DEFAULT_CONTRACT = Path("generated/d2-proxy-reward-terminal-fixed-evidence-contract.json")
DEFAULT_OUTPUT = Path("generated/d2-proxy-reward-terminal-fixed-evidence.json")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _import_parquet(vendor: Path):
    sys.path.insert(0, str(vendor))
    import pyarrow.parquet as pq
    return pq


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


def _clean_answer(answer: str | None) -> str:
    """WebArena StringEvaluator.clean_answer for the selected multi-reference tasks."""
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
    """Exact selected-task behavior: multi-reference must_include, so tokenize=False."""
    clean_pred = _clean_answer(pred)
    checks: list[dict[str, Any]] = []
    score = 1.0
    for ref in references:
        clean_ref = _clean_answer(ref)
        cur = float(clean_ref in clean_pred)
        score *= cur
        checks.append({"ref": ref, "score": cur})
    return score, checks


def build_support(
    *,
    parquet_path: Path = DEFAULT_PARQUET,
    task_config_path: Path = DEFAULT_TASK_CONFIG,
    evaluator_source: Path = DEFAULT_EVALUATOR_SOURCE,
    future_task_ids: tuple[str, ...] = ("164", "385", "387", "388"),
) -> dict[str, Any]:
    pq = _import_parquet(DEFAULT_VENDOR)
    released = {str(row["task_id"]): row for row in pq.read_table(parquet_path, columns=["task_id", "task_prompt", "trajectory_json", "is_successful"]).to_pylist()}
    configs = {str(row["task_id"]): row for row in json.loads(task_config_path.read_text(encoding="utf-8"))}
    rows: list[dict[str, Any]] = []
    for task_id in future_task_ids:
        source = released[task_id]
        config = configs[task_id]
        eval_block = config.get("eval") or {}
        refs = (eval_block.get("reference_answers") or {}).get("must_include") or []
        evidence, state_hashes = _current_state_evidence(str(source["trajectory_json"]))
        ref_checks = []
        for ref in refs:
            ref_checks.append({"ref": ref, "visible": _clean_answer(ref) in _clean_answer(evidence)})
        blockers: list[str] = []
        if eval_block.get("eval_types") != ["string_match"]:
            blockers.append("not-pure-string-match")
        if not refs:
            blockers.append("missing-must-include-reference")
        if len(refs) < 2:
            blockers.append("selected-task-would-enter-tokenize-branch")
        if any("|OR|" in str(ref) for ref in refs):
            blockers.append("ambiguous-or-reference-semantics")
        if not evidence:
            blockers.append("released-browser-evidence-missing")
        if not all(row["visible"] for row in ref_checks):
            blockers.append("released-browser-evidence-does-not-cover-all-references")
        evidence_sha = hashlib.sha256(evidence.encode("utf-8")).hexdigest()
        rows.append({
            "task_id": task_id,
            "task_prompt": str(source["task_prompt"]),
            "intent_template_id": config.get("intent_template_id"),
            "released_original_success": bool(source.get("is_successful")),
            "reference_answers": list(refs),
            "reference_visibility": ref_checks,
            "released_state_count": len(state_hashes),
            "released_state_sha256": state_hashes,
            "evidence_sha256": evidence_sha,
            "evidence_chars": len(evidence),
            "qualified": not blockers,
            "blockers": blockers,
        })
    return {
        "schema_version": "1.0",
        "support_id": "D2-PROXY-REWARD-FIXED-EVIDENCE-TERMINAL-SUPPORT",
        "status": "SUPPORT_QUALIFIED" if all(row["qualified"] for row in rows) else "SUPPORT_INCOMPLETE",
        "selection_policy": {
            "future_task_ids_frozen_before_policy_calls": list(future_task_ids),
            "all_tasks_fresh_to_f0_f0c_f1": True,
            "review_or_opinion_semantic_family_only": True,
            "pure_deterministic_must_include_only": True,
            "all_reference_strings_must_be_visible_in_released_browser_evidence": True,
            "historical_agent_outputs_excluded_from_evidence": True,
            "historical_agent_memory_excluded_from_evidence": True,
        },
        "source_artifacts": {
            "parquet": str(parquet_path),
            "parquet_sha256": _sha(parquet_path),
            "task_config": str(task_config_path),
            "task_config_sha256": _sha(task_config_path),
            "evaluator_source": str(evaluator_source),
            "evaluator_source_sha256": _sha(evaluator_source),
        },
        "tasks": rows,
        "scientific_authority": False,
        "experiment_authority": False,
    }


def _evidence_by_task(parquet_path: Path, task_ids: list[str]) -> dict[str, str]:
    pq = _import_parquet(DEFAULT_VENDOR)
    released = {str(row["task_id"]): row for row in pq.read_table(parquet_path, columns=["task_id", "trajectory_json"]).to_pylist()}
    return {task_id: _current_state_evidence(str(released[task_id]["trajectory_json"]))[0] for task_id in task_ids}


def _answer_prompt(task: str, evidence: str, memory: str) -> str:
    return f"""You are answering a WebArena read-only benchmark task from a frozen released evidence packet.

RULES:
- Use only the RELEASED BROWSER EVIDENCE below as factual evidence.
- REUSABLE MEMORY is procedural guidance. It may influence how you interpret or organize the evidence, but it is not task-specific ground truth.
- Do not invent reviewer names, ratings, product facts, or quotes that are absent from the released evidence.
- Return only the final answer to the benchmark task. Do not return JSON, browser actions, analysis, or commentary.

REUSABLE MEMORY:
{memory.strip() if memory.strip() else 'No reusable memory is supplied.'}

BENCHMARK TASK:
{task}

RELEASED BROWSER EVIDENCE:
{evidence}

FINAL ANSWER:"""


def _cell_stat(rows: list[dict[str, Any]], cells: list[tuple[str, str]]) -> tuple[float, list[dict[str, Any]]]:
    details = []
    values = []
    for source_id, future_id in cells:
        success = [float(row["benchmark_score"]) for row in rows if row["source_memory_task"] == source_id and row["future_task"] == future_id and row["condition"] == "success_label_memory"]
        failure = [float(row["benchmark_score"]) for row in rows if row["source_memory_task"] == source_id and row["future_task"] == future_id and row["condition"] == "failure_label_memory"]
        if not success or not failure:
            continue
        s_rate = sum(success) / len(success)
        f_rate = sum(failure) / len(failure)
        tv = abs(s_rate - f_rate)
        values.append(tv)
        details.append({"source_memory_task": source_id, "future_task": future_id, "success_memory_rate": round(s_rate, 6), "failure_memory_rate": round(f_rate, 6), "absolute_rate_difference": round(tv, 6), "signed_failure_minus_success": round(f_rate - s_rate, 6)})
    return (sum(values) / len(values) if values else 0.0), details


def _permutation_p(rows: list[dict[str, Any]], cells: list[tuple[str, str]], *, repetitions: int, seed: int, observed: float) -> float:
    rng = random.Random(seed)
    pools: list[tuple[list[float], int]] = []
    for source_id, future_id in cells:
        left = [float(row["benchmark_score"]) for row in rows if row["source_memory_task"] == source_id and row["future_task"] == future_id and row["condition"] == "success_label_memory"]
        right = [float(row["benchmark_score"]) for row in rows if row["source_memory_task"] == source_id and row["future_task"] == future_id and row["condition"] == "failure_label_memory"]
        pools.append((left + right, len(left)))
    ge = 0
    for _ in range(repetitions):
        tvs = []
        for pool, n_left in pools:
            shuffled = list(pool)
            rng.shuffle(shuffled)
            a = shuffled[:n_left]
            b = shuffled[n_left:]
            tvs.append(abs(sum(a) / len(a) - sum(b) / len(b)))
        stat = sum(tvs) / len(tvs)
        if stat >= observed - 1e-12:
            ge += 1
    return (ge + 1) / (repetitions + 1)


def run(contract: dict[str, Any], *, output: Path, private_root: Path) -> dict[str, Any]:
    if contract.get("status") != "FROZEN_BEFORE_PROVIDER_CALLS":
        raise ValueError("terminal-fixed-evidence-contract-not-frozen")
    support_path = Path(contract["source_artifacts"]["support"])
    support = json.loads(support_path.read_text(encoding="utf-8"))
    if _sha(support_path) != contract["source_artifacts"]["support_sha256"]:
        raise ValueError("support-sha-drift")
    if support.get("status") != "SUPPORT_QUALIFIED":
        raise ValueError("support-not-qualified")
    task_rows = {str(row["task_id"]): row for row in support["tasks"]}
    future_ids = [str(x) for x in contract["future_tasks"]]
    if any(not task_rows[task_id]["qualified"] for task_id in future_ids):
        raise ValueError("future-task-not-qualified")

    f0_path = Path(contract["source_artifacts"]["f0"])
    f0 = json.loads(f0_path.read_text(encoding="utf-8"))
    if _sha(f0_path) != contract["source_artifacts"]["f0_sha256"]:
        raise ValueError("f0-sha-drift")
    pairs = {str(row["task_id"]): row for row in f0.get("pairs") or [] if row.get("success_memory_sha256") and row.get("failure_memory_sha256")}
    source_ids = [str(x) for x in contract["source_memory_tasks"]]
    if set(source_ids) != set(pairs):
        raise ValueError("source-memory-set-drift")

    evidence = _evidence_by_task(Path(contract["source_artifacts"]["parquet"]), future_ids)
    for task_id in future_ids:
        digest = hashlib.sha256(evidence[task_id].encode("utf-8")).hexdigest()
        if digest != task_rows[task_id]["evidence_sha256"]:
            raise ValueError(f"evidence-sha-drift:{task_id}")

    model_cfg = contract["model"]
    thinking = model_cfg.get("thinking")
    base = ArkSettings.from_env()
    client = ArkResponsesClient(ArkSettings(api_key=base.api_key, base_url=base.base_url, default_model=base.default_model, timeout_seconds=180.0, max_retries=0))

    def responder(**kw: Any) -> dict[str, Any]:
        return client.respond(
            kw["prompt"],
            model=kw["model"],
            max_output_tokens=kw["max_output_tokens"],
            temperature=kw["temperature"],
            thinking=thinking,
            store=True,
            allow_thinking_compatibility_fallback=bool(model_cfg.get("allow_thinking_compatibility_fallback", False)),
        )

    result_rows: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    experiment_id = str(contract["experiment_id"])
    repetitions = int(contract["rollouts_per_cell"])
    cells = [(source_id, future_id) for source_id in source_ids for future_id in future_ids]

    for source_id, future_id in cells:
        pair = pairs[source_id]
        memories = {
            "success_label_memory": _load_raw(DEFAULT_F0_RAW_ROOT, pair["success_memory_sha256"]),
            "failure_label_memory": _load_raw(DEFAULT_F0_RAW_ROOT, pair["failure_memory_sha256"]),
        }
        for condition, memory in memories.items():
            for rollout in range(1, repetitions + 1):
                prompt = _answer_prompt(task_rows[future_id]["task_prompt"], evidence[future_id], memory)
                stage = f"terminal-{future_id}-source-{source_id}-{condition}-r{rollout}"
                response, receipt = _cached_call(
                    responder=responder,
                    root=private_root,
                    experiment_id=experiment_id,
                    stage=stage,
                    engine_id=f"source-{source_id}",
                    prompt=prompt,
                    model=str(model_cfg["requested"]),
                    tokens=int(model_cfg["max_output_tokens"]),
                    temp=float(model_cfg["temperature"]),
                    thinking=thinking,
                )
                receipts.append(receipt)
                if response is None or not str(response.get("text") or "").strip():
                    failures.append({"source_memory_task": source_id, "future_task": future_id, "condition": condition, "rollout": rollout, **receipt})
                    continue
                answer = str(response.get("text") or "").strip()
                score, checks = _must_include_score(answer, list(task_rows[future_id]["reference_answers"]))
                result_rows.append({"source_memory_task": source_id, "future_task": future_id, "condition": condition, "rollout": rollout, "answer_sha256": hashlib.sha256(answer.encode("utf-8")).hexdigest(), "benchmark_score": score, "evaluator_checks": checks, "raw_sha256": receipt.get("raw_sha256"), "scientific_authority": False})

    calibration_rows: list[dict[str, Any]] = []
    calibration_reps = int(contract.get("no_memory_rollouts_per_task") or 0)
    for future_id in future_ids:
        for rollout in range(1, calibration_reps + 1):
            prompt = _answer_prompt(task_rows[future_id]["task_prompt"], evidence[future_id], "")
            stage = f"terminal-{future_id}-no-memory-r{rollout}"
            response, receipt = _cached_call(
                responder=responder,
                root=private_root,
                experiment_id=experiment_id,
                stage=stage,
                engine_id="no-memory",
                prompt=prompt,
                model=str(model_cfg["requested"]),
                tokens=int(model_cfg["max_output_tokens"]),
                temp=float(model_cfg["temperature"]),
                thinking=thinking,
            )
            receipts.append(receipt)
            if response is None or not str(response.get("text") or "").strip():
                failures.append({"source_memory_task": "", "future_task": future_id, "condition": "no_memory", "rollout": rollout, **receipt})
                continue
            answer = str(response.get("text") or "").strip()
            score, checks = _must_include_score(answer, list(task_rows[future_id]["reference_answers"]))
            calibration_rows.append({"future_task": future_id, "condition": "no_memory", "rollout": rollout, "answer_sha256": hashlib.sha256(answer.encode("utf-8")).hexdigest(), "benchmark_score": score, "evaluator_checks": checks, "raw_sha256": receipt.get("raw_sha256"), "scientific_authority": False})

    expected_primary = len(cells) * 2 * repetitions
    expected_calibration = len(future_ids) * calibration_reps
    complete = len(result_rows) == expected_primary and len(calibration_rows) == expected_calibration
    observed, cell_details = _cell_stat(result_rows, cells) if len(result_rows) == expected_primary else (None, [])
    gate = contract["terminal_gate"]
    p_value = None
    gate_pass = False
    if observed is not None:
        p_value = _permutation_p(result_rows, cells, repetitions=int(gate["permutation_repetitions"]), seed=int(gate["permutation_seed"]), observed=float(observed))
        gate_pass = bool(p_value < float(gate["alpha"]) and float(observed) >= float(gate["min_mean_absolute_success_rate_difference"]))
    signed = sum(row["signed_failure_minus_success"] for row in cell_details) / len(cell_details) if cell_details else None
    no_memory_by_task = {}
    for future_id in future_ids:
        vals = [float(row["benchmark_score"]) for row in calibration_rows if row["future_task"] == future_id]
        no_memory_by_task[future_id] = round(sum(vals) / len(vals), 6) if vals else None
    decision = "SUPPORT_FIXED_EVIDENCE_TERMINAL_CORRECTNESS_SHIFT" if gate_pass else ("INCONCLUSIVE_NO_NEGATIVE_AUTHORITY" if complete else "SUPPORT_INCOMPLETE_NO_SCIENTIFIC_AUTHORITY")
    report = {
        "schema_version": "1.0",
        "experiment_id": experiment_id,
        "status": "TERMINAL_FIXED_EVIDENCE_COMPLETE" if complete else "TERMINAL_FIXED_EVIDENCE_SUPPORT_INCOMPLETE",
        "contract_sha256": _jsha(contract),
        "summary": {
            "source_memory_pairs": len(source_ids),
            "future_tasks": len(future_ids),
            "source_future_cells": len(cells),
            "requested_primary_calls": expected_primary,
            "complete_primary_calls": len(result_rows),
            "requested_no_memory_calls": expected_calibration,
            "complete_no_memory_calls": len(calibration_rows),
            "provider_failures": len(failures),
            "observed_mean_absolute_success_rate_difference": round(float(observed), 6) if observed is not None else None,
            "mean_signed_failure_minus_success": round(float(signed), 6) if signed is not None else None,
            "permutation_p_ge_observed": round(float(p_value), 6) if p_value is not None else None,
            "gate_pass": gate_pass,
            "no_memory_success_rate_by_task": no_memory_by_task,
        },
        "cell_results": cell_details,
        "rollouts": result_rows,
        "no_memory_calibration": calibration_rows,
        "provider_receipts": receipts,
        "failures": failures,
        "decision": decision,
        "scope": "Terminal benchmark answer correctness under fixed released browser evidence; does not claim live browser-navigation transport.",
        "scientific_authority": False,
        "experiment_authority": False,
    }
    _write_json(output, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-support", action="store_true")
    parser.add_argument("--support", type=Path, default=DEFAULT_SUPPORT)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--private-root", type=Path, default=Path("generated/research-data/d2-proxy-reward-terminal-fixed-evidence"))
    args = parser.parse_args()
    if args.prepare_support:
        payload = build_support()
        _write_json(args.support, payload)
        print(json.dumps({"status": payload["status"], "tasks": [{"task_id": row["task_id"], "qualified": row["qualified"], "evidence_sha256": row["evidence_sha256"]} for row in payload["tasks"]]}, ensure_ascii=False, indent=2))
        return
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    args.private_root.mkdir(parents=True, exist_ok=True)
    lock_path = args.private_root / "transaction.lock"
    with lock_path.open("a+", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps({"status": "TRANSACTION_ALREADY_RUNNING", "experiment_id": contract.get("experiment_id")}, ensure_ascii=False))
            return
        if args.output.exists():
            existing = json.loads(args.output.read_text(encoding="utf-8"))
            if existing.get("status") == "TERMINAL_FIXED_EVIDENCE_COMPLETE" and existing.get("contract_sha256") == _jsha(contract):
                print(json.dumps({"status": "REPLAY_COMPLETED_PUBLIC_STATE", "summary": existing.get("summary"), "decision": existing.get("decision")}, ensure_ascii=False, indent=2))
                return
        report = run(contract, output=args.output, private_root=args.private_root)
        print(json.dumps({"status": report["status"], "summary": report["summary"], "decision": report["decision"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
