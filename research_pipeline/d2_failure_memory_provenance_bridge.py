from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Any

from .ark_provider import ArkResponsesClient, ArkSettings
from .d2_proxy_reward_memory_f1 import _cached_call
from .d2_proxy_reward_terminal_fixed_evidence import _clean_answer, _must_include_score
from .discovery_engine_terminal_replication import _jsha, _write_json

ROOT = Path("generated/research-data/paper-yield-d5-c01")
VENDOR = ROOT / "vendor"
TASK_CONFIG = ROOT / "self-improve-fragility/webarena/src/walt/benchmarks/wa/test_configs/test.raw.json"
EVALUATOR_SOURCE = ROOT / "self-improve-fragility/webarena/src/walt/browser_use/custom/evaluators/wa/wa_evaluators.py"
DEFAULT_SUPPORT = Path("generated/d2-failure-memory-provenance-bridge-support.json")
DEFAULT_CONTRACT = Path("generated/d2-failure-memory-provenance-bridge-contract.json")
DEFAULT_OUTPUT = Path("generated/d2-failure-memory-provenance-bridge.json")
DEFAULT_PRIVATE = Path("generated/research-data/d2-failure-memory-provenance-bridge")
FROZEN_TASKS = ("125", "360", "228", "126", "362", "229")
FROZEN_GUIDANCE = (
    "Use only observed task-relevant evidence. Check every constraint in the task before concluding. "
    "When the answer contains multiple required items or a range, verify every required component. "
    "Report only values supported by the observed evidence."
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _import_parquet():
    sys.path.insert(0, str(VENDOR))
    import pyarrow.parquet as pq
    return pq


def _evidence(trajectory_json: str) -> str:
    trajectory = json.loads(trajectory_json)
    states: list[str] = []
    seen: set[str] = set()
    for step in (trajectory.get("steps") or {}).values():
        contents = ((step.get("input_messages") or {}).get("contents") or [])
        if not contents:
            continue
        text = str(contents[-1].get("content") or "")
        if "[Current state starts here]" in text:
            text = text.split("[Current state starts here]", 1)[1]
        text = text.strip()
        if not text:
            continue
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if digest not in seen:
            seen.add(digest)
            states.append(text)
    return "\n\n--- RELEASED BROWSER STATE ---\n\n".join(states)


def _read_only(prompt: str) -> bool:
    low = prompt.lower()
    mutating = (
        "buy ", "purchase", "add to cart", "place an order", "cancel", "return ", "rate ",
        "write a review", "change ", "update ", "set ", "create ", "delete ", "remove ",
        "checkout", "refund", "transfer ", "send money", "edit ",
    )
    return not any(token in low for token in mutating)


def build_support() -> dict[str, Any]:
    pq = _import_parquet()
    configs = {str(row["task_id"]): row for row in json.loads(TASK_CONFIG.read_text(encoding="utf-8"))}
    parquets = sorted(ROOT.glob("parquet-cache/*.parquet"))
    selected: dict[str, dict[str, Any]] = {}
    for parquet in parquets:
        table = pq.read_table(parquet)
        if "task_id" not in table.column_names or "trajectory_json" not in table.column_names:
            continue
        cols = [name for name in ("task_id", "task_prompt", "trajectory_json", "is_successful") if name in table.column_names]
        for row in table.select(cols).to_pylist():
            task_id = str(row["task_id"])
            if task_id not in FROZEN_TASKS or task_id in selected:
                continue
            config = configs.get(task_id) or {}
            eval_block = config.get("eval") or {}
            refs = (eval_block.get("reference_answers") or {}).get("must_include") or []
            task_prompt = str(row.get("task_prompt") or "")
            evidence = _evidence(str(row["trajectory_json"]))
            blockers: list[str] = []
            if eval_block.get("eval_types") != ["string_match"]:
                blockers.append("not-pure-string-match")
            if len(refs) < 2:
                blockers.append("requires-multi-reference-must-include")
            if any("|OR|" in str(ref) for ref in refs):
                blockers.append("ambiguous-or-reference-semantics")
            if not _read_only(task_prompt):
                blockers.append("task-is-not-read-only")
            if not evidence:
                blockers.append("released-evidence-missing")
            visibility = [{"ref": ref, "visible": _clean_answer(ref) in _clean_answer(evidence)} for ref in refs]
            if not all(item["visible"] for item in visibility):
                blockers.append("released-evidence-does-not-cover-all-references")
            selected[task_id] = {
                "task_id": task_id,
                "task_prompt": task_prompt,
                "intent_template_id": config.get("intent_template_id"),
                "source_parquet": parquet.name,
                "source_parquet_sha256": _sha(parquet),
                "released_original_success": bool(row.get("is_successful")),
                "reference_answers": list(refs),
                "reference_visibility": visibility,
                "evidence_sha256": hashlib.sha256(evidence.encode("utf-8")).hexdigest(),
                "evidence_chars": len(evidence),
                "qualified": not blockers,
                "blockers": blockers,
            }
    rows = [selected.get(task_id, {"task_id": task_id, "qualified": False, "blockers": ["frozen-task-not-found"]}) for task_id in FROZEN_TASKS]
    return {
        "schema_version": "1.0",
        "support_id": "D2-C01-EXPLICIT-PROVENANCE-CUE-BRIDGE-SUPPORT",
        "status": "SUPPORT_QUALIFIED" if all(row.get("qualified") is True for row in rows) else "SUPPORT_INCOMPLETE",
        "scope": "Fresh fixed-evidence WebArena bridge; this is not a reconstruction of the financial AgentDojo audit.",
        "selection_policy": {
            "task_ids_frozen_before_bridge_provider_calls": list(FROZEN_TASKS),
            "fresh_to_c02_f0_f1_f2": True,
            "read_only_only": True,
            "deterministic_multi_reference_must_include_only": True,
            "all_references_visible_in_released_evidence": True,
            "three_templates_round_robin": True,
            "historical_agent_outputs_and_memory_excluded": True,
        },
        "guidance": FROZEN_GUIDANCE,
        "guidance_sha256": hashlib.sha256(FROZEN_GUIDANCE.encode("utf-8")).hexdigest(),
        "task_config_sha256": _sha(TASK_CONFIG),
        "evaluator_source_sha256": _sha(EVALUATOR_SOURCE),
        "tasks": rows,
        "scientific_authority": False,
        "experiment_authority": False,
    }


def _load_evidence(row: dict[str, Any]) -> str:
    pq = _import_parquet()
    parquet = ROOT / "parquet-cache" / str(row["source_parquet"])
    table = pq.read_table(parquet, columns=["task_id", "trajectory_json"])
    source = next(item for item in table.to_pylist() if str(item["task_id"]) == str(row["task_id"]))
    evidence = _evidence(str(source["trajectory_json"]))
    if hashlib.sha256(evidence.encode("utf-8")).hexdigest() != row["evidence_sha256"]:
        raise ValueError(f"evidence-sha-drift:{row['task_id']}")
    return evidence


def _prompt(task: str, evidence: str, provenance: str) -> str:
    if provenance == "SUCCESS":
        metadata = "SOURCE OUTCOME: SUCCESS"
    elif provenance == "FAILURE":
        metadata = "SOURCE OUTCOME: FAILURE"
    elif provenance == "UNSPECIFIED":
        metadata = "SOURCE OUTCOME: UNSPECIFIED"
    else:
        raise ValueError(provenance)
    return f"""You are answering a read-only WebArena benchmark task from a frozen released evidence packet.

REUSABLE MEMORY METADATA:
{metadata}

REUSABLE GUIDANCE:
{FROZEN_GUIDANCE}

RULES:
- The guidance text is identical across provenance conditions. The source-outcome field is metadata only.
- Use only RELEASED BROWSER EVIDENCE as task-specific factual evidence.
- Do not invent values absent from the evidence.
- Return only the final benchmark answer. Do not return analysis, browser actions, JSON, or commentary.

BENCHMARK TASK:
{task}

RELEASED BROWSER EVIDENCE:
{evidence}

FINAL ANSWER:"""


def _rates(rows: list[dict[str, Any]], tasks: list[str]) -> tuple[float, list[dict[str, Any]]]:
    details = []
    diffs = []
    for task_id in tasks:
        success = [float(row["benchmark_score"]) for row in rows if row["task_id"] == task_id and row["provenance"] == "SUCCESS"]
        failure = [float(row["benchmark_score"]) for row in rows if row["task_id"] == task_id and row["provenance"] == "FAILURE"]
        unspecified = [float(row["benchmark_score"]) for row in rows if row["task_id"] == task_id and row["provenance"] == "UNSPECIFIED"]
        if not success or not failure:
            continue
        sr = sum(success) / len(success)
        fr = sum(failure) / len(failure)
        ur = sum(unspecified) / len(unspecified) if unspecified else None
        diff = sr - fr
        diffs.append(diff)
        details.append({
            "task_id": task_id,
            "success_provenance_rate": round(sr, 6),
            "failure_provenance_rate": round(fr, 6),
            "unspecified_provenance_rate": round(ur, 6) if ur is not None else None,
            "success_minus_failure": round(diff, 6),
        })
    return (sum(diffs) / len(diffs) if diffs else 0.0), details


def _permutation(rows: list[dict[str, Any]], tasks: list[str], *, repetitions: int, seed: int, observed: float) -> tuple[float, float]:
    rng = random.Random(seed)
    pools: list[tuple[list[float], int]] = []
    for task_id in tasks:
        s = [float(row["benchmark_score"]) for row in rows if row["task_id"] == task_id and row["provenance"] == "SUCCESS"]
        f = [float(row["benchmark_score"]) for row in rows if row["task_id"] == task_id and row["provenance"] == "FAILURE"]
        pools.append((s + f, len(s)))
    ge = 0
    le = 0
    for _ in range(repetitions):
        diffs = []
        for pool, n_s in pools:
            shuffled = list(pool)
            rng.shuffle(shuffled)
            s = shuffled[:n_s]
            f = shuffled[n_s:]
            diffs.append(sum(s) / len(s) - sum(f) / len(f))
        stat = sum(diffs) / len(diffs)
        if stat >= observed - 1e-12:
            ge += 1
        if stat <= observed + 1e-12:
            le += 1
    denom = repetitions + 1
    return (ge + 1) / denom, (le + 1) / denom


def run(contract: dict[str, Any], *, output: Path, private_root: Path) -> dict[str, Any]:
    if contract.get("status") != "FROZEN_BEFORE_PROVIDER_CALLS":
        raise ValueError("bridge-contract-not-frozen")
    support_path = Path(contract["source_artifacts"]["support"])
    support = json.loads(support_path.read_text(encoding="utf-8"))
    if _sha(support_path) != contract["source_artifacts"]["support_sha256"]:
        raise ValueError("support-sha-drift")
    if support.get("status") != "SUPPORT_QUALIFIED":
        raise ValueError("support-not-qualified")
    if support.get("guidance_sha256") != contract["guidance_sha256"]:
        raise ValueError("guidance-sha-drift")
    task_rows = {str(row["task_id"]): row for row in support["tasks"]}
    task_ids = [str(task_id) for task_id in contract["future_tasks"]]
    if task_ids != list(FROZEN_TASKS):
        raise ValueError("future-task-set-drift")
    evidence = {task_id: _load_evidence(task_rows[task_id]) for task_id in task_ids}

    model = contract["model"]
    thinking = model.get("thinking")
    base = ArkSettings.from_env()
    client = ArkResponsesClient(ArkSettings(api_key=base.api_key, base_url=base.base_url, default_model=base.default_model, timeout_seconds=180.0, max_retries=0))

    def responder(**kw: Any) -> dict[str, Any]:
        return client.respond(
            kw["prompt"], model=kw["model"], max_output_tokens=kw["max_output_tokens"],
            temperature=kw["temperature"], thinking=thinking, store=True,
            allow_thinking_compatibility_fallback=bool(model.get("allow_thinking_compatibility_fallback", False)),
        )

    rows: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    reps = int(contract["rollouts_per_condition"])
    conditions = list(contract["conditions"])
    for task_id in task_ids:
        for provenance in conditions:
            for rollout in range(1, reps + 1):
                prompt = _prompt(task_rows[task_id]["task_prompt"], evidence[task_id], provenance)
                response, receipt = _cached_call(
                    responder=responder, root=private_root, experiment_id=str(contract["experiment_id"]),
                    stage=f"task-{task_id}-{provenance.lower()}-r{rollout}", engine_id=f"task-{task_id}",
                    prompt=prompt, model=str(model["requested"]), tokens=int(model["max_output_tokens"]),
                    temp=float(model["temperature"]), thinking=thinking,
                )
                receipts.append(receipt)
                answer = str((response or {}).get("text") or "").strip()
                if not answer:
                    failures.append({"task_id": task_id, "provenance": provenance, "rollout": rollout, **receipt})
                    continue
                score, checks = _must_include_score(answer, list(task_rows[task_id]["reference_answers"]))
                rows.append({
                    "task_id": task_id, "provenance": provenance, "rollout": rollout,
                    "answer_sha256": hashlib.sha256(answer.encode("utf-8")).hexdigest(),
                    "benchmark_score": score, "evaluator_checks": checks, "raw_sha256": receipt.get("raw_sha256"),
                    "scientific_authority": False,
                })

    expected = len(task_ids) * len(conditions) * reps
    complete = len(rows) == expected
    primary_rows = [row for row in rows if row["provenance"] in {"SUCCESS", "FAILURE"}]
    observed, task_details = _rates(rows, task_ids) if complete else (None, [])
    gate = contract["provenance_gate"]
    p_ge = p_le = None
    if observed is not None:
        p_ge, p_le = _permutation(primary_rows, task_ids, repetitions=int(gate["permutation_repetitions"]), seed=int(gate["permutation_seed"]), observed=float(observed))
    support = bool(observed is not None and observed >= float(gate["min_directional_difference"]) and p_ge is not None and p_ge < float(gate["alpha"]))
    counter = bool(observed is not None and observed <= -float(gate["min_directional_difference"]) and p_le is not None and p_le < float(gate["alpha"]))
    if not complete:
        decision = "SUPPORT_INCOMPLETE_NO_SCIENTIFIC_AUTHORITY"
    elif support:
        decision = "SUPPORT_EXPLICIT_PROVENANCE_CUE_BRIDGE"
    elif counter:
        decision = "COUNTEREVIDENCE_EXPLICIT_PROVENANCE_CUE_BRIDGE"
    else:
        decision = "INCONCLUSIVE_NO_NEGATIVE_AUTHORITY"
    report = {
        "schema_version": "1.0",
        "experiment_id": contract["experiment_id"],
        "status": "BRIDGE_COMPLETE" if complete else "BRIDGE_SUPPORT_INCOMPLETE",
        "contract_sha256": _jsha(contract),
        "scope": "Explicit provenance metadata under byte-identical generic guidance and fixed released WebArena evidence. This does not reconstruct the financial AgentDojo audit or natural ReasoningBank memory generation.",
        "summary": {
            "future_tasks": len(task_ids), "templates": len(set(task_rows[task_id]["intent_template_id"] for task_id in task_ids)),
            "requested_calls": expected, "complete_calls": len(rows), "provider_failures": len(failures),
            "mean_success_minus_failure_terminal_rate": round(float(observed), 6) if observed is not None else None,
            "permutation_p_success_greater": round(float(p_ge), 6) if p_ge is not None else None,
            "permutation_p_failure_greater": round(float(p_le), 6) if p_le is not None else None,
            "support_gate_pass": support, "counterevidence_gate_pass": counter,
        },
        "task_results": task_details,
        "rollouts": rows,
        "provider_receipts": receipts,
        "failures": failures,
        "decision": decision,
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
    parser.add_argument("--private-root", type=Path, default=DEFAULT_PRIVATE)
    args = parser.parse_args()
    if args.prepare_support:
        payload = build_support()
        _write_json(args.support, payload)
        print(json.dumps({"status": payload["status"], "tasks": [{"task_id": row["task_id"], "qualified": row["qualified"], "template": row.get("intent_template_id")} for row in payload["tasks"]]}, ensure_ascii=False, indent=2))
        return
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    args.private_root.mkdir(parents=True, exist_ok=True)
    with (args.private_root / "transaction.lock").open("a+", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps({"status": "TRANSACTION_ALREADY_RUNNING", "experiment_id": contract.get("experiment_id")}, ensure_ascii=False))
            return
        if args.output.exists():
            existing = json.loads(args.output.read_text(encoding="utf-8"))
            if existing.get("status") == "BRIDGE_COMPLETE" and existing.get("contract_sha256") == _jsha(contract):
                print(json.dumps({"status": "REPLAY_COMPLETED_PUBLIC_STATE", "summary": existing.get("summary"), "decision": existing.get("decision")}, ensure_ascii=False, indent=2))
                return
        report = run(contract, output=args.output, private_root=args.private_root)
        print(json.dumps({"status": report["status"], "summary": report["summary"], "decision": report["decision"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
