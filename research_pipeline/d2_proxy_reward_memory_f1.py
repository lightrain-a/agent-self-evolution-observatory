from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from .ark_provider import ArkResponsesClient, ArkSettings, extract_json_object
from .config import StorageSettings
from .discovery_engine_terminal_replication import _archive, _jsha, _now, _write_json


def _import_parquet(vendor: Path):
    sys.path.insert(0, str(vendor))
    import pyarrow.parquet as pq
    return pq


def _load_raw(root: Path, sha: str) -> str:
    return (root / "raw" / sha[:2] / f"{sha}.txt").read_text(encoding="utf-8")


def _action_signature(payload: dict[str, Any]) -> str:
    current_state = payload.get("current_state") or {}
    actions = payload.get("action") or (current_state.get("action") if isinstance(current_state, dict) else None) or []
    if not actions or not isinstance(actions[0], dict):
        return "NO_ACTION"
    action = actions[0]
    name = next(iter(action), "UNKNOWN")
    args = action.get(name) or {}
    if name == "click_element" and isinstance(args, dict):
        return f"click_element:{args.get('index')}"
    return name


def _parse_policy_output(text: str) -> tuple[str, str, bool]:
    """Return (action signature, next goal, support-recovered).

    The fallback is intentionally narrow: it recovers only a fully emitted action array from
    provider text whose outer JSON object was truncated after the action. It never invents a
    missing action and therefore carries no scientific selection authority.
    """
    try:
        payload = extract_json_object(text)
        signature = _action_signature(payload)
        current = payload.get("current_state") or {}
        next_goal = str(current.get("next_goal") or "") if isinstance(current, dict) else ""
        return signature, next_goal, False
    except Exception as strict_error:
        action_match = re.search(r'"action"\s*:\s*\[\s*\{\s*"([^"]+)"\s*:\s*\{(.*?)\}\s*\}\s*\]', text, re.DOTALL)
        if not action_match:
            raise strict_error
        name = action_match.group(1)
        body = action_match.group(2)
        if name == "click_element":
            index_match = re.search(r'"index"\s*:\s*(\d+)', body)
            if not index_match:
                raise strict_error
            signature = f"click_element:{index_match.group(1)}"
        else:
            signature = name
        goal_match = re.search(r'"next_goal"\s*:\s*"((?:\\.|[^"\\])*)"', text, re.DOTALL)
        next_goal = ""
        if goal_match:
            try:
                next_goal = json.loads('"' + goal_match.group(1) + '"')
            except Exception:
                next_goal = goal_match.group(1)
        return signature, next_goal, True


def _entropy(signatures: list[str]) -> float:
    if not signatures:
        return 0.0
    counts = Counter(signatures)
    total = len(signatures)
    value = 0.0
    for n in counts.values():
        p = n / total
        value -= p * math.log2(p)
    return value


def _mode(signatures: list[str]) -> str:
    if not signatures:
        return ""
    counts = Counter(signatures)
    best = max(counts.values())
    return sorted([k for k, v in counts.items() if v == best])[0]


def _falsifier_result(*, paired_complete: int, paired_divergent: int, required_aligned: int) -> str:
    """Fail closed when provider/parse support is insufficient to evaluate the frozen falsifier."""
    if paired_divergent > 0:
        return "SURVIVES_F1"
    if required_aligned > 0 and paired_complete == required_aligned:
        return "FALSIFIED_F1"
    return "SUPPORT_INCOMPLETE_NO_SCIENTIFIC_AUTHORITY"


def _request_material(*, experiment_id: str, stage: str, engine_id: str, prompt_sha: str, model: str, tokens: int, temp: float, thinking: str | None = None) -> dict[str, Any]:
    return {
        "transaction_id": experiment_id,
        "stage": stage,
        "engine_id": engine_id,
        "prompt_sha256": prompt_sha,
        "requested_model": model,
        "max_output_tokens": int(tokens),
        "temperature": float(temp),
        "store": True,
        "thinking": thinking,
    }


def _request_fingerprint(*, experiment_id: str, stage: str, engine_id: str, prompt_sha: str, model: str, tokens: int, temp: float, thinking: str | None = None) -> str:
    return _jsha(_request_material(experiment_id=experiment_id, stage=stage, engine_id=engine_id, prompt_sha=prompt_sha, model=model, tokens=tokens, temp=temp, thinking=thinking))


def _cached_call(*, responder, root: Path, experiment_id: str, stage: str, engine_id: str, prompt: str, model: str, tokens: int, temp: float, thinking: str | None = None):
    prompt_archive = _archive(root, "prompts", prompt)
    prompt_sha = prompt_archive["sha256"]
    material = _request_material(experiment_id=experiment_id, stage=stage, engine_id=engine_id, prompt_sha=prompt_sha, model=model, tokens=tokens, temp=temp, thinking=thinking)
    fp = _jsha(material)
    receipt_path = root / "provider-receipts" / fp[:2] / f"{fp}.json"
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        response = receipt.get("response") or {}
        sha = str(response.get("raw_sha256") or "")
        if sha:
            text = _load_raw(root, sha)
            return {"text": text, "resolved_model": response.get("resolved_model"), "usage": response.get("usage") or {}, "status": response.get("status"), "response_id": response.get("response_id")}, {
                "stage": stage, "engine_id": engine_id, "requested_model": model, "resolved_model": response.get("resolved_model"), "prompt_sha256": prompt_sha, "raw_sha256": sha, "request_fingerprint": fp, "usage": response.get("usage") or {}, "status": response.get("status"), "provider_response_id_archived_privately": bool(response.get("response_id")), "scientific_authority": False, "replayed": True,
            }
        return None, {"stage": stage, "engine_id": engine_id, "requested_model": model, "prompt_sha256": prompt_sha, "request_fingerprint": fp, "status": "CACHED_PROVIDER_FAILURE", "scientific_authority": False, "replayed": True}
    try:
        result = responder(prompt=prompt, model=model, max_output_tokens=tokens, temperature=temp)
    except Exception as error:
        rid = str(getattr(error, "response_id", "") or "")
        private = {"schema_version": "1.0", "generated_at": _now(), "request": material, "request_fingerprint": fp, "provider_error": {"type": type(error).__name__, "detail_sha256": hashlib.sha256(str(error).encode()).hexdigest(), "response_id": rid, "status": str(getattr(error, "response_status", "") or "")}, "scientific_authority": False}
        _write_json(receipt_path, private)
        return None, {"stage": stage, "engine_id": engine_id, "requested_model": model, "prompt_sha256": prompt_sha, "request_fingerprint": fp, "status": "PROVIDER_FAILURE", "error_type": type(error).__name__, "provider_response_id_archived_privately": bool(rid), "scientific_authority": False}
    raw = str(result.get("text") or "")
    raw_archive = _archive(root, "raw", raw)
    private = {"schema_version": "1.0", "generated_at": _now(), "request": material, "request_fingerprint": fp, "response": {"response_id": str(result.get("response_id") or ""), "status": str(result.get("status") or ""), "resolved_model": str(result.get("resolved_model") or model), "usage": result.get("usage") or {}, "raw_sha256": raw_archive["sha256"]}, "scientific_authority": False}
    _write_json(receipt_path, private)
    public = {"stage": stage, "engine_id": engine_id, "requested_model": model, "resolved_model": str(result.get("resolved_model") or model), "prompt_sha256": prompt_sha, "raw_sha256": raw_archive["sha256"], "request_fingerprint": fp, "usage": result.get("usage") or {}, "status": str(result.get("status") or ""), "provider_response_id_archived_privately": bool(result.get("response_id")), "scientific_authority": False}
    return result, public


def _decision_prompt(system: str, task: str, state: str, memory: str) -> str:
    memory_block = memory.strip() if memory.strip() else "No reusable memory is available for this decision."
    return f"""SYSTEM INSTRUCTION:\n{system}\n\nREUSABLE MEMORY:\n{memory_block}\n\nULTIMATE TASK:\n{task}\n\nCURRENT BROWSER STATE:\n{state}\n\nChoose the next browser-agent action now. Return only the JSON object required by the system instruction."""


def run(contract: dict[str, Any], *, output: Path, private_root: Path) -> dict[str, Any]:
    if contract.get("status") != "FROZEN_BEFORE_PROVIDER_CALLS":
        raise ValueError("f1-contract-not-frozen")
    f0 = json.loads(Path(contract["source_artifacts"]["f0"]).read_text(encoding="utf-8"))
    f0_pairs = {str(row["task_id"]): row for row in f0.get("pairs") or [] if row.get("token_jaccard_distance") is not None}
    raw_root = Path("generated/research-data/d2-proxy-reward-memory-f0")
    pq = _import_parquet(Path("generated/research-data/paper-yield-d5-c01/vendor"))
    parquet = Path(contract["source_artifacts"]["released_parquet"])
    released = {str(row["task_id"]): row for row in pq.read_table(parquet, columns=["task_id", "task_prompt", "trajectory_json"]).to_pylist()}

    model_cfg = contract["model"]
    thinking = model_cfg.get("thinking")
    allow_thinking_fallback = bool(model_cfg.get("allow_thinking_compatibility_fallback", True))
    base = ArkSettings.from_env()
    client = ArkResponsesClient(ArkSettings(api_key=base.api_key, base_url=base.base_url, default_model=base.default_model, timeout_seconds=120.0, max_retries=0))
    def responder(**kw: Any) -> dict[str, Any]:
        return client.respond(kw["prompt"], model=kw["model"], max_output_tokens=kw["max_output_tokens"], temperature=kw["temperature"], thinking=thinking, store=True, allow_thinking_compatibility_fallback=allow_thinking_fallback)

    rows = []
    receipts = []
    failures = []
    for mapping in contract["paired_interventions"]:
        source_id = str(mapping["source_memory_task"])
        future_id = str(mapping["future_task"])
        step_id = str(mapping["future_step"])
        pair = f0_pairs[source_id]
        traj = json.loads(released[future_id]["trajectory_json"])
        step = (traj.get("steps") or {})[step_id]
        messages = ((step.get("input_messages") or {}).get("contents") or [])
        system = str(messages[0].get("content") or "")
        state = str(messages[-1].get("content") or "")
        memories = {
            "success_label_memory": _load_raw(raw_root, pair["success_memory_sha256"]),
            "failure_label_memory": _load_raw(raw_root, pair["failure_memory_sha256"]),
            "no_memory": "",
        }
        for condition, memory in memories.items():
            for rollout in range(1, int(contract["rollouts_per_condition"]) + 1):
                prompt = _decision_prompt(system, released[future_id]["task_prompt"], state, memory)
                stage = f"future-{future_id}-{condition}-r{rollout}"
                result, receipt = _cached_call(responder=responder, root=private_root, experiment_id=str(contract["experiment_id"]), stage=stage, engine_id=f"memory-{source_id}", prompt=prompt, model=str(model_cfg["requested"]), tokens=int(model_cfg["max_output_tokens"]), temp=float(model_cfg["temperature"]), thinking=thinking)
                receipts.append(receipt)
                if result is None:
                    failures.append({"source_memory_task": source_id, "future_task": future_id, "condition": condition, "rollout": rollout, **receipt})
                    continue
                text = str(result.get("text") or "")
                try:
                    signature, next_goal, parse_recovered = _parse_policy_output(text)
                except Exception as error:
                    failures.append({"source_memory_task": source_id, "future_task": future_id, "condition": condition, "rollout": rollout, "status": "PARSE_FAILURE", "raw_sha256": receipt.get("raw_sha256"), "error_type": type(error).__name__, "scientific_authority": False})
                    continue
                rows.append({"source_memory_task": source_id, "future_task": future_id, "future_step": step_id, "condition": condition, "rollout": rollout, "action_signature": signature, "next_goal": next_goal, "parse_recovered": parse_recovered, "raw_sha256": receipt.get("raw_sha256"), "scientific_authority": False})

    by_task = []
    paired_complete = 0
    paired_divergent = 0
    modal_diff = 0
    modal_comparable = 0
    shifted_from_no_memory = 0
    no_memory_comparable = 0
    for mapping in contract["paired_interventions"]:
        future_id = str(mapping["future_task"])
        groups = {cond: [r["action_signature"] for r in rows if r["future_task"] == future_id and r["condition"] == cond] for cond in contract["conditions"]}
        success = groups["success_label_memory"]
        failure = groups["failure_label_memory"]
        aligned = min(len(success), len(failure))
        divergent = sum(success[i] != failure[i] for i in range(aligned))
        paired_complete += aligned
        paired_divergent += divergent
        smode = _mode(success); fmode = _mode(failure); nmode = _mode(groups["no_memory"])
        if smode and fmode:
            modal_comparable += 1
            if smode != fmode:
                modal_diff += 1
        if nmode and (smode or fmode):
            no_memory_comparable += 1
            if (smode and smode != nmode) or (fmode and fmode != nmode):
                shifted_from_no_memory += 1
        by_task.append({"future_task": future_id, "source_memory_task": str(mapping["source_memory_task"]), "signatures": groups, "modal_signatures": {"success_label_memory": smode, "failure_label_memory": fmode, "no_memory": nmode}, "entropy_bits": {k: round(_entropy(v), 6) for k, v in groups.items()}, "aligned_pair_count": aligned, "aligned_divergent_count": divergent, "scientific_authority": False})

    n_tasks = len(contract["paired_interventions"])
    rollouts_per_condition = int(contract["rollouts_per_condition"])
    required_aligned = n_tasks * rollouts_per_condition
    falsifier_result = _falsifier_result(
        paired_complete=paired_complete,
        paired_divergent=paired_divergent,
        required_aligned=required_aligned,
    )
    summary = {
        "requested_policy_calls": n_tasks * len(contract["conditions"]) * rollouts_per_condition,
        "complete_policy_calls": len(rows),
        "provider_or_parse_failures": len(failures),
        "aligned_success_failure_rollouts": paired_complete,
        "required_aligned_success_failure_rollouts": required_aligned,
        "falsifier_evaluable": paired_complete == required_aligned,
        "paired_action_signature_divergence_rate": round(paired_divergent / paired_complete, 6) if paired_complete else None,
        "modal_action_signature_comparable_tasks": modal_comparable,
        "modal_action_signature_difference_rate": round(modal_diff / modal_comparable, 6) if modal_comparable else None,
        "no_memory_comparable_tasks": no_memory_comparable,
        "memory_condition_shift_from_no_memory": round(shifted_from_no_memory / no_memory_comparable, 6) if no_memory_comparable else None,
    }
    report = {"schema_version": "1.0", "experiment_id": contract["experiment_id"], "status": "F1_COMPLETE" if len(rows) == summary["requested_policy_calls"] else "F1_SUPPORT_INCOMPLETE", "contract_sha256": _jsha(contract), "hypothesis": contract["hypothesis"], "summary": summary, "falsifier_result": falsifier_result, "task_results": by_task, "rollouts": rows, "provider_receipts": receipts, "failures": failures, "experiment_debt": contract["experiment_debt_after_f1"], "scientific_authority": False, "authority": {"problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False}}
    _write_json(output, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=Path("generated/d2-proxy-reward-memory-f1-contract.json"))
    parser.add_argument("--output", type=Path, default=Path("generated/d2-proxy-reward-memory-f1.json"))
    parser.add_argument("--private-root", type=Path)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    root = args.private_root or StorageSettings.from_env().data_root / "d2-proxy-reward-memory-f1"
    root.mkdir(parents=True, exist_ok=True)
    lock = (root / "transaction.lock").open("a+")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(json.dumps({"status": "TRANSACTION_ALREADY_RUNNING", "experiment_id": contract["experiment_id"]}))
        return
    if args.output.exists():
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        if existing.get("status") == "F1_COMPLETE" and existing.get("contract_sha256") == _jsha(contract):
            print(json.dumps({"status": "REPLAY_COMPLETED_PUBLIC_STATE", "summary": existing.get("summary"), "falsifier_result": existing.get("falsifier_result")}, ensure_ascii=False, indent=2))
            return
    report = run(contract, output=args.output, private_root=root)
    print(json.dumps({"status": report["status"], "summary": report["summary"], "falsifier_result": report["falsifier_result"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
