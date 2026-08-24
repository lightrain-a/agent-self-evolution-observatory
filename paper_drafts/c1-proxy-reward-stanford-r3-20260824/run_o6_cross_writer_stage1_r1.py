#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

EXPECTED_DESIGN_SHA256 = "19b3ea55704f4774405713f285b29d53f0ece7d78f9299fbb81ae86939f879b8"
EXPECTED_MODEL = "glm-5.3"
EXPECTED_CALLS = 8
EXPECTED_MAX_OUTPUT_TOKENS = 4096
EXPECTED_SOURCE_TASKS = ["21", "22", "23", "25"]
EXPECTED_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def jsha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return obj


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def archive_text(root: Path, text: str) -> str:
    digest = text_sha(text)
    path = root / "raw" / digest[:2] / f"{digest}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(text, encoding="utf-8")
    elif path.read_text(encoding="utf-8") != text:
        raise RuntimeError("content-addressed raw archive collision")
    return digest


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def normalize_text(text: str) -> str:
    return " ".join(str(text or "").split())


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9_'-]+", str(text or "").lower()))


def jaccard_distance(a: str, b: str) -> float:
    aa, bb = tokens(a), tokens(b)
    union = aa | bb
    return 0.0 if not union else 1.0 - len(aa & bb) / len(union)


def titles(text: str) -> list[str]:
    vals = re.findall(r"^##\s*Title:\s*(.+?)\s*$", str(text or ""), flags=re.MULTILINE)
    return [normalize_text(v) for v in vals]


def action_summary(trajectory_json: str) -> str:
    data = json.loads(trajectory_json)
    lines: list[str] = []
    for step_id, step in sorted((data.get("steps") or {}).items(), key=lambda kv: int(kv[0])):
        output = (step or {}).get("output_messages") or {}
        tool_call_message = output.get("tool_call_message") or {}
        calls = tool_call_message.get("tool_calls") or []
        if calls:
            args = calls[0].get("args") or {}
            current = args.get("current_state") or {}
            if current.get("evaluation_previous_goal"):
                lines.append(f"Step {step_id} evaluation: {normalize_text(current['evaluation_previous_goal'])[:500]}")
            if current.get("next_goal"):
                lines.append(f"Step {step_id} next goal: {normalize_text(current['next_goal'])[:500]}")
            for action in args.get("action") or []:
                lines.append(f"Step {step_id} action: {json.dumps(action, ensure_ascii=False, sort_keys=True)[:900]}")
        controller = (step or {}).get("controller_messages") or {}
        for result in controller.get("action_result") or []:
            content = result.get("content") if isinstance(result, dict) else str(result)
            if content:
                lines.append(f"Step {step_id} result: {normalize_text(content)[:900]}")
        if len(lines) >= 36:
            break
    return "\n".join(lines)


def writer_prompt(system_prompt: str, task: str, trajectory: str) -> str:
    return f"""{system_prompt.strip()}\n\nTask: {task}\n\nTrajectory:\n{trajectory}\n\nCreate memory items for the task above. Return only the requested Markdown memory-item format."""


def normalized_model_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())


def validate_contract(contract_path: Path, contract: dict[str, Any]) -> None:
    require(contract.get("status") == "FROZEN_BEFORE_PROVIDER_CALLS", "Stage-1 contract is not frozen")
    require(contract.get("paper_id") == "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE", "paper mismatch")
    require(contract.get("objection_id") == "PROXY-O6", "objection mismatch")
    require((contract.get("design") or {}).get("sha256") == EXPECTED_DESIGN_SHA256, "design SHA mismatch")
    require(contract.get("source_tasks") == EXPECTED_SOURCE_TASKS, "source task support drift")
    require(int(contract.get("expected_provider_calls") or 0) == EXPECTED_CALLS, "Stage-1 call budget drift")
    model = contract.get("writer_model") or {}
    require(model.get("requested") == EXPECTED_MODEL, "writer model drift")
    require(float(model.get("temperature")) == 0.0, "writer temperature drift")
    require(int(model.get("max_output_tokens")) == EXPECTED_MAX_OUTPUT_TOKENS, "writer token budget drift")
    require(model.get("thinking") is None, "writer thinking setting must be omitted")
    require(int(model.get("provider_retries") or 0) == 0, "writer provider retries must remain zero")
    require(model.get("substitution_allowed") is False, "writer model substitution forbidden")
    gate = contract.get("advance_to_stage2_if") or {}
    require(gate == {"all_8_provider_calls_complete": True, "exact_content_changed_pairs_min": 4, "title_set_changed_pairs_min": 3, "token_jaccard_threshold": None}, "Stage-1 gate drift")
    require(contract.get("stage2_preregistered_gate") == {"mean_absolute_success_rate_difference_min": 0.15, "permutation_p_lt": 0.05}, "Stage-2 preregistered gate drift")
    authority = contract.get("authority") or {}
    require(authority.get("scientific_reopen_authority") is True and authority.get("experiment_authority") is True and authority.get("provider_call_authority") is True, "Stage-1 authority missing")
    require(authority.get("claim_expansion_authority") is False and authority.get("submission_authority") is False, "Stage-1 authority scope expanded")
    for key, row in (contract.get("source_artifacts") or {}).items():
        path = Path(row["path"])
        require(path.is_file(), f"missing Stage-1 source artifact: {key}")
        require(sha256(path) == row["sha256"], f"Stage-1 source artifact SHA drift: {key}")
    hp = Path((contract.get("human_authority") or {})["path"])
    require(hp.is_file() and sha256(hp) == contract["human_authority"]["sha256"], "human authority binding drift")
    runner = contract["code"]["runner"]
    require(Path(runner["path"]).resolve() == Path(__file__).resolve(), "Stage-1 runner path mismatch")
    require(sha256(Path(__file__)) == runner["sha256"], "Stage-1 runner SHA drift after freeze")


def import_runtime(contract: dict[str, Any]):
    repo_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo_root))
    sys.path.insert(0, str(Path(contract["vendor_path"])))
    import pyarrow.parquet as pq  # type: ignore
    from research_pipeline.config import load_env_file
    from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings

    load_env_file(Path(contract["provider_env_file"]))
    base = ArkSettings.from_env()
    require(bool(base.api_key), "ARK provider credential unavailable")
    require(base.base_url == EXPECTED_BASE_URL, f"provider base URL drift: {base.base_url}")
    settings = ArkSettings(api_key=base.api_key, base_url=base.base_url, default_model=base.default_model, timeout_seconds=180.0, max_retries=0)
    return pq, ArkResponseStateError, ArkResponsesClient(settings), settings.safe_summary()


def load_source_rows(contract: dict[str, Any], pq) -> dict[str, dict[str, Any]]:
    parquet = Path(contract["source_artifacts"]["parquet"]["path"])
    all_rows = {str(row["task_id"]): row for row in pq.read_table(parquet, columns=["task_id", "task_prompt", "is_successful", "trajectory_json"]).to_pylist()}
    frozen = {str(row["task_id"]): row for row in contract["source_bindings"]}
    out: dict[str, dict[str, Any]] = {}
    original_f0 = load(Path(contract["source_artifacts"]["original_f0"]["path"]))
    old_pairs = {str(row["task_id"]): row for row in original_f0["pairs"]}
    for task in EXPECTED_SOURCE_TASKS:
        require(task in all_rows and task in frozen and task in old_pairs, f"source task missing: {task}")
        summary = action_summary(str(all_rows[task]["trajectory_json"]))
        require(jsha(summary) == frozen[task]["trajectory_summary_sha256"], f"trajectory summary drift: {task}")
        require(str(all_rows[task]["task_prompt"]) == str(old_pairs[task]["task_prompt"]), f"task prompt drift: {task}")
        out[task] = {"task_prompt": str(all_rows[task]["task_prompt"]), "action_summary": summary, "original_is_successful": bool(all_rows[task]["is_successful"])}
    return out


def stage_name(task: str, label: str) -> str:
    return f"writer-{task}-{label}"


def run_one(*, client, error_type, contract: dict[str, Any], task: str, label: str, system_prompt: str, source: dict[str, Any], private_root: Path) -> dict[str, Any]:
    stage = stage_name(task, label)
    stage_path = private_root / "stages" / f"{stage}.json"
    if stage_path.is_file():
        cached = load(stage_path)
        require(cached.get("stage") == stage, f"cached Stage-1 identity mismatch: {stage}")
        return cached
    prompt = writer_prompt(system_prompt, source["task_prompt"], source["action_summary"])
    base = {"stage": stage, "task_id": task, "label": label, "prompt_sha256": text_sha(prompt), "requested_model": EXPECTED_MODEL}
    try:
        response = client.respond(prompt, model=EXPECTED_MODEL, max_output_tokens=EXPECTED_MAX_OUTPUT_TOKENS, temperature=0.0, thinking=None, store=True, allow_thinking_compatibility_fallback=False)
        text = str(response.get("text") or "")
        response_archive = {
            **base,
            "response_id": response.get("response_id"),
            "status": response.get("status"),
            "requested_model_returned": response.get("requested_model"),
            "resolved_model": response.get("resolved_model"),
            "usage": response.get("usage") or {},
            "text": text,
            "text_sha256": text_sha(text) if text else "",
            "thinking_requested": response.get("thinking_requested"),
            "thinking_effective": response.get("thinking_effective"),
            "thinking_compatibility_fallback": response.get("thinking_compatibility_fallback"),
        }
        atomic_json(private_root / "provider-responses" / f"{stage}.json", response_archive)
        require(str(response.get("requested_model")) == EXPECTED_MODEL, "requested writer model drift in response")
        require(normalized_model_name(str(response.get("resolved_model"))).startswith("glm53"), f"resolved writer model family drift: {response.get('resolved_model')}")
        require(bool(text.strip()), "writer returned empty assistant text")
        raw_sha = archive_text(private_root, text)
        row = {
            **base,
            "status": "complete",
            "response_id": response.get("response_id"),
            "resolved_model": response.get("resolved_model"),
            "usage": response.get("usage") or {},
            "raw_sha256": raw_sha,
            "titles": titles(text),
        }
    except error_type as exc:
        row = {**base, "status": "provider_state_failure", "error_type": type(exc).__name__, "provider_receipt": exc.receipt()}
    except Exception as exc:
        row = {**base, "status": "provider_or_runtime_failure", "error_type": type(exc).__name__, "error": str(exc)[:1000]}
    atomic_json(stage_path, row)
    return row


def build_report(contract_path: Path, contract: dict[str, Any], stages: list[dict[str, Any]], private_root: Path, provider_summary: dict[str, Any]) -> dict[str, Any]:
    by = {(row["task_id"], row["label"]): row for row in stages}
    pairs = []
    for task in EXPECTED_SOURCE_TASKS:
        s = by.get((task, "success"), {})
        f = by.get((task, "failure"), {})
        complete = s.get("status") == "complete" and f.get("status") == "complete"
        success_text = (private_root / "raw" / str(s.get("raw_sha256", ""))[:2] / f"{s.get('raw_sha256','')}.txt").read_text(encoding="utf-8") if complete else ""
        failure_text = (private_root / "raw" / str(f.get("raw_sha256", ""))[:2] / f"{f.get('raw_sha256','')}.txt").read_text(encoding="utf-8") if complete else ""
        s_titles, f_titles = titles(success_text), titles(failure_text)
        pairs.append({
            "task_id": task,
            "success_memory_sha256": s.get("raw_sha256", ""),
            "failure_memory_sha256": f.get("raw_sha256", ""),
            "complete_pair": complete,
            "exact_content_changed": bool(complete and normalize_text(success_text) != normalize_text(failure_text)),
            "token_jaccard_distance": round(jaccard_distance(success_text, failure_text), 6) if complete else None,
            "success_titles": s_titles,
            "failure_titles": f_titles,
            "title_set_parseable_both": bool(s_titles and f_titles),
            "title_set_changed": bool(complete and s_titles and f_titles and set(s_titles) != set(f_titles)),
        })
    complete_calls = sum(row.get("status") == "complete" for row in stages)
    exact_changed = sum(row["exact_content_changed"] for row in pairs)
    title_changed = sum(row["title_set_changed"] for row in pairs)
    complete_pairs = sum(row["complete_pair"] for row in pairs)
    mean_j = sum(float(row["token_jaccard_distance"]) for row in pairs if row["token_jaccard_distance"] is not None) / complete_pairs if complete_pairs else None
    gate = bool(complete_calls == 8 and complete_pairs == 4 and exact_changed >= 4 and title_changed >= 3)
    return {
        "schema_version": "1.0",
        "experiment_id": contract["experiment_id"],
        "paper_id": contract["paper_id"],
        "objection_id": contract["objection_id"],
        "status": "O6_STAGE1_COMPLETE" if complete_calls == 8 else "O6_STAGE1_INCOMPLETE",
        "contract_path": str(contract_path.resolve()),
        "contract_sha256": sha256(contract_path),
        "provider": provider_summary,
        "summary": {
            "requested_provider_calls": 8,
            "complete_provider_calls": complete_calls,
            "complete_pairs": complete_pairs,
            "exact_content_changed_pairs": exact_changed,
            "title_set_changed_pairs": title_changed,
            "mean_token_jaccard_distance": None if mean_j is None else round(mean_j, 6),
            "stage1_gate_pass": gate,
        },
        "pairs": pairs,
        "failures": [{k: row.get(k) for k in ("task_id", "label", "stage", "status", "error_type", "provider_receipt")} for row in stages if row.get("status") != "complete"],
        "decision": "ADVANCE_TO_CROSS_WRITER_TERMINAL_STAGE2" if gate else "STOP_CROSS_WRITER_BEFORE_TERMINAL_STAGE2",
        "stage2_provider_calls_authorized_by_this_result": 0,
        "stage2_requires_separate_execution_contract": True,
        "scientific_authority": False,
        "claim_expansion_authority": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the single-repair 4096-token PROXY-O6 GLM-5.3 cross-writer Stage 1 R1.")
    ap.add_argument("--contract", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--private-root", required=True, type=Path)
    args = ap.parse_args()
    contract = load(args.contract)
    validate_contract(args.contract, contract)
    args.private_root.mkdir(parents=True, exist_ok=True)
    lock_path = args.private_root / "transaction.lock"
    lock_fh = lock_path.open("a+")
    try:
        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(json.dumps({"status": "TRANSACTION_ALREADY_RUNNING", "experiment_id": contract["experiment_id"], "provider_calls_executed_by_this_process": 0}), flush=True)
        return 3
    try:
        pq, error_type, client, provider_summary = import_runtime(contract)
        source_rows = load_source_rows(contract, pq)
        success_prompt = Path(contract["source_artifacts"]["success_prompt"]["path"]).read_text(encoding="utf-8")
        failure_prompt = Path(contract["source_artifacts"]["failure_prompt"]["path"]).read_text(encoding="utf-8")
        stages: list[dict[str, Any]] = []
        stop_after_failure = False
        for task in EXPECTED_SOURCE_TASKS:
            if stop_after_failure:
                break
            for label, system_prompt in (("success", success_prompt), ("failure", failure_prompt)):
                row = run_one(client=client, error_type=error_type, contract=contract, task=task, label=label, system_prompt=system_prompt, source=source_rows[task], private_root=args.private_root)
                stages.append(row)
                report = build_report(args.contract, contract, stages, args.private_root, provider_summary)
                atomic_json(args.output, report)
                print(json.dumps({"stage": row["stage"], "status": row["status"], "complete_so_far": sum(x.get('status') == 'complete' for x in stages), "seen_so_far": len(stages)}), flush=True)
                if row.get("status") != "complete":
                    stop_after_failure = True
                    break
        report = build_report(args.contract, contract, stages, args.private_root, provider_summary)
        atomic_json(args.output, report)
        print(json.dumps({"status": report["status"], "summary": report["summary"], "decision": report["decision"]}, indent=2))
        return 0 if report["status"] == "O6_STAGE1_COMPLETE" else 2
    finally:
        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)
        lock_fh.close()


if __name__ == "__main__":
    raise SystemExit(main())
