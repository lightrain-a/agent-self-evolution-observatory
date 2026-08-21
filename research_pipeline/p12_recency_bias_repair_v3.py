from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .api_research_memory import record_archived_api_parse_failure, record_parsed_api_output, record_raw_api_output
from .p12_recency_bias_execute import _call_once, _close_parse_failure
from .p12_recency_bias_harness import (
    CANDIDATE_ID,
    CONTRACT_SHA256,
    EXECUTOR_MODEL,
    difficulty_calibration_pairs,
    difficulty_prompt,
    difficulty_tool,
    sha_json,
)
from .p12_recency_bias_protocol import (
    REPAIRED_AUTHORIZATION_V3_FILENAME,
    REPAIRED_IMPLEMENTATION_MANIFEST_V3_FILENAME,
    client,
    load_json,
    lock_output,
    parse_difficulty_answers,
    provider_archive_payload,
    sha_bytes,
    sha_text,
    write_json,
)
from .paper_first_evidence_acquisition import compile_harness_runtime_repair_receipts, validate_evidence_plan

FAILED_PAIR = "D-CYCLIC3-1"
FAILURE_V2_FILENAME = "runtime-failure-manifest-v2.json"
REVOKED_V2_FILENAME = "authorization-revoked-plan-v2.json"
OLD_MANIFEST_V2_FILENAME = "harness-implementation-manifest-v2.json"
REPAIR_PLAN_V3_FILENAME = "runtime-repair-plan-v3.json"
OFFLINE_PROBE_V3_FILENAME = "runtime-repair-offline-probe-v3.json"
PROTOCOL_REVIEW_V3_FILENAME = "runtime-protocol-review-v3.json"
TRANSPORT_PROBE_V3_FILENAME = "runtime-transport-probe-v3.json"
REPAIR_RECEIPT_V3_FILENAME = "runtime-repair-receipt-v3.json"
OLD_RETURN_SENTENCE = "Return the two integer answers only through the supplied function."
ANSWER_PREFIX_RE = re.compile(r"^P12_ANSWERS backward=([-+]?\d+) forward=([-+]?\d+)$")
V3_MAX_OUTPUT_TOKENS = 600
FROZEN_MAX_MODEL_CALLS = 192
REPLACEMENT_PROVIDER_CALL_CAP = 101
PROTOCOL_VERSION = "P12_CALIBRATION_ANSWER_FIRST_V3"


def _pair() -> dict[str, Any]:
    return next(row for row in difficulty_calibration_pairs() if row["pair_id"] == FAILED_PAIR)


def answer_first_prompt(pair: dict[str, Any]) -> str:
    base = difficulty_prompt(pair)
    if not base.endswith(OLD_RETURN_SENTENCE):
        raise RuntimeError("frozen difficulty prompt return sentence drift")
    replacement = (
        "Response protocol only: before any reasoning, emit exactly one first line in the form "
        "P12_ANSWERS backward=<integer> forward=<integer>. The supplied function may also be called; "
        "a valid function call takes priority. Do not change the task interpretation."
    )
    return base[: -len(OLD_RETURN_SENTENCE)] + replacement


def scientific_prompt_body(prompt: str) -> str:
    marker = "Return the two integer answers only through the supplied function."
    if marker in prompt:
        return prompt.split(marker, 1)[0]
    marker_v3 = "Response protocol only: before any reasoning"
    if marker_v3 in prompt:
        return prompt.split(marker_v3, 1)[0]
    raise ValueError("unrecognized P12 difficulty prompt protocol")


def parse_v3_difficulty_answers(archive: dict[str, Any]) -> tuple[dict[str, int], str]:
    try:
        return parse_difficulty_answers(archive)
    except ValueError:
        pass
    text = str(archive.get("text") or "")
    first = next((line.strip() for line in text.splitlines() if line.strip()), "")
    match = ANSWER_PREFIX_RE.fullmatch(first)
    if not match:
        raise ValueError("v3 answer-first fallback requires exact first-line P12_ANSWERS prefix")
    return {"backward_answer": int(match.group(1)), "forward_answer": int(match.group(2))}, "ANSWER_FIRST_TEXT"


def build_repair_plan(run_root: Path) -> dict[str, Any]:
    failure = load_json(run_root / FAILURE_V2_FILENAME)
    old_manifest = load_json(run_root / OLD_MANIFEST_V2_FILENAME)
    base = difficulty_prompt(_pair())
    v3 = answer_first_prompt(_pair())
    core = {
        "schema_version": "1.0",
        "status": "P12_RUNTIME_REPAIR_PLAN_V3",
        "candidate_id": CANDIDATE_ID,
        "contract_sha256": CONTRACT_SHA256,
        "failure_manifest_sha256": failure["failure_manifest_sha256"],
        "replaces_harness_manifest_sha256": old_manifest["harness_manifest_sha256"],
        "failed_pair": FAILED_PAIR,
        "protocol_version": PROTOCOL_VERSION,
        "protocol_only_change": True,
        "scientific_object_unchanged": True,
        "old_prompt_sha256": sha_text(base),
        "new_prompt_sha256": sha_text(v3),
        "scientific_prompt_body_sha256": sha_text(scientific_prompt_body(base)),
        "scientific_prompt_body_unchanged": scientific_prompt_body(base) == scientific_prompt_body(v3),
        "retry": {
            "pair_id": FAILED_PAIR,
            "max_attempts": 1,
            "max_output_tokens": V3_MAX_OUTPUT_TOKENS,
            "task_unchanged": True,
            "truth_unchanged": True,
            "model_unchanged": True,
            "temperature_unchanged": True,
            "tool_schema_unchanged": True,
            "only_return_protocol_changes": True,
        },
        "reuse_completed_difficulty": ["D-LINEAR-1", "D-QUADRATIC-1", "D-ALTERNATING2-1"],
        "remaining_scientific_work": {"skill_compilation_calls": 4, "evaluation_calls": 96},
        "provider_calls_already_charged": int(failure["provider_calls_charged"]),
        "remaining_model_call_budget_before_repair": int(failure["remaining_model_call_budget"]),
        "replacement_provider_call_cap": REPLACEMENT_PROVIDER_CALL_CAP,
        "scientific_authority": False,
        "belief_authority": False,
    }
    core["replacement_harness_plan_sha256"] = sha_json(core)
    return core


def run_offline_probe(run_root: Path) -> dict[str, Any]:
    output = run_root / OFFLINE_PROBE_V3_FILENAME
    lock = lock_output(output, {"stage": "p12-runtime-repair-offline-v3"})
    try:
        plan = build_repair_plan(run_root)
        function_archive = {"function_calls": [{"name": "submit_p12_difficulty_answers", "arguments": json.dumps({"backward_answer": 1, "forward_answer": 2})}], "text": ""}
        text_archive = {"function_calls": [], "text": "P12_ANSWERS backward=-3 forward=8\nlong reasoning may follow"}
        checks = {
            "scientific_prompt_body_unchanged": plan["scientific_prompt_body_unchanged"] is True,
            "single_failed_pair_only": plan["retry"]["pair_id"] == FAILED_PAIR and plan["retry"]["max_attempts"] == 1,
            "function_call_still_preferred": parse_v3_difficulty_answers(function_archive)[1] == "FUNCTION_CALL",
            "answer_first_fallback": parse_v3_difficulty_answers(text_archive) == ({"backward_answer": -3, "forward_answer": 8}, "ANSWER_FIRST_TEXT"),
            "total_calls_106_within_192": plan["provider_calls_already_charged"] + plan["replacement_provider_call_cap"] == 106 <= FROZEN_MAX_MODEL_CALLS,
        }
        result = {"schema_version": "1.0", "status": "P12_RUNTIME_REPAIR_OFFLINE_V3_PASS" if all(checks.values()) else "P12_RUNTIME_REPAIR_OFFLINE_V3_FAIL", "checks": checks, "replacement_harness_plan_sha256": plan["replacement_harness_plan_sha256"], "scientific_authority": False, "belief_authority": False}
        result["offline_probe_sha256"] = sha_json(result)
        write_json(run_root / REPAIR_PLAN_V3_FILENAME, plan)
        write_json(output, result)
        return result
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def run_neutral_transport_probe(run_root: Path, persistent_root: Path) -> dict[str, Any]:
    output = run_root / TRANSPORT_PROBE_V3_FILENAME
    lock = lock_output(output, {"stage": "p12-runtime-transport-v3"})
    try:
        prompt = "Neutral response-protocol probe. Before any reasoning, first line must be exactly P12_ANSWERS backward=5 forward=9. The two trivial answers are 2+3 and 4+5. Do not use scientific task data."
        provider_root = persistent_root / "runs" / f"p12-neutral-answer-first-{sha_text(PROTOCOL_VERSION)[:10]}"
        provider_root.mkdir(parents=True, exist_ok=True)
        response = client().respond(prompt, model=EXECUTOR_MODEL, max_output_tokens=120, temperature=0.0, thinking="disabled", store=True)
        archive = provider_archive_payload(response)
        raw_file = provider_root / "raw-answer-first.json"
        raw_file.write_text(json.dumps(archive, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")
        psha = sha_text(prompt)
        archived = record_raw_api_output(run_root=provider_root, stage="p12-answer-first-transport-v3", raw_path=raw_file, requested_model=EXECUTOR_MODEL, resolved_model=archive["resolved_model"], request_fingerprint=sha_json({"stage": "p12-answer-first-transport-v3", "prompt_sha256": psha}), prompt_sha256=psha, root=persistent_root)
        answers, source = parse_v3_difficulty_answers(archive)
        passed = answers == {"backward_answer": 5, "forward_answer": 9} and source == "ANSWER_FIRST_TEXT"
        result = {"schema_version": "1.0", "status": "P12_RUNTIME_TRANSPORT_V3_PASS" if passed else "P12_RUNTIME_TRANSPORT_V3_FAIL", "raw_sha256": archived["raw_sha256"], "response_status": archive.get("status"), "response_id_archived": bool(archive.get("response_id")), "answer_source": source, "answers": answers, "scientific_authority": False, "belief_authority": False}
        result["transport_probe_sha256"] = sha_json(result)
        record_parsed_api_output(run_root=provider_root, stage="p12-answer-first-transport-v3", raw_sha256=archived["raw_sha256"], structured_payload=result, requested_model=EXECUTOR_MODEL, resolved_model=archive["resolved_model"], research_objects=[], root=persistent_root)
        write_json(output, result)
        return result
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def authorize_v3(run_root: Path) -> dict[str, Any]:
    output = run_root / REPAIRED_AUTHORIZATION_V3_FILENAME
    lock = lock_output(output, {"stage": "p12-runtime-authorize-v3"})
    try:
        revoked = load_json(run_root / REVOKED_V2_FILENAME)
        failure = load_json(run_root / FAILURE_V2_FILENAME)
        old_manifest = load_json(run_root / OLD_MANIFEST_V2_FILENAME)
        plan = load_json(run_root / REPAIR_PLAN_V3_FILENAME)
        offline = load_json(run_root / OFFLINE_PROBE_V3_FILENAME)
        transport = load_json(run_root / TRANSPORT_PROBE_V3_FILENAME)
        review = load_json(run_root / PROTOCOL_REVIEW_V3_FILENAME)
        if offline.get("status") != "P12_RUNTIME_REPAIR_OFFLINE_V3_PASS" or transport.get("status") != "P12_RUNTIME_TRANSPORT_V3_PASS":
            raise RuntimeError("P12 v3 repair probes not PASS")
        if review.get("verdict") != "CLEAR_PROTOCOL_EQUIVALENCE" or review.get("reviewer_independent") is not True:
            raise RuntimeError("P12 v3 independent protocol review not CLEAR")
        base = Path(__file__).parent
        names = ("p12_recency_bias_harness.py", "p12_recency_bias_protocol.py", "p12_recency_bias_execute.py", "p12_recency_bias_repair_v3.py")
        manifest = {"schema_version": "1.0", "status": "P12_RUNTIME_REPAIR_HARNESS_V3_PASS", "candidate_id": CANDIDATE_ID, "contract_sha256": CONTRACT_SHA256, "failure_manifest_sha256": failure["failure_manifest_sha256"], "replaces_harness_manifest_sha256": old_manifest["harness_manifest_sha256"], "replacement_harness_plan_sha256": plan["replacement_harness_plan_sha256"], "offline_probe_sha256": offline["offline_probe_sha256"], "transport_probe_sha256": transport["transport_probe_sha256"], "protocol_review_sha256": review["review_sha256"], "code_sha256": {name: sha_bytes((base / name).read_bytes()) for name in names}, "replacement_provider_call_cap": REPLACEMENT_PROVIDER_CALL_CAP, "sandboxed": True, "probe_passed": True, "budget_feasible": True, "scientific_object_unchanged": True, "protocol_only_change": True, "scientific_authority": False, "belief_authority": False}
        manifest["harness_manifest_sha256"] = sha_json(manifest)
        write_json(run_root / REPAIRED_IMPLEMENTATION_MANIFEST_V3_FILENAME, manifest)
        receipt = {"schema_version": "1.0", "scientific_authority": False, "receipts": [{"candidate_id": CANDIDATE_ID, "contract_sha256": CONTRACT_SHA256, "failure_manifest_sha256": failure["failure_manifest_sha256"], "replaces_harness_manifest_sha256": old_manifest["harness_manifest_sha256"], "replacement_harness_plan_sha256": plan["replacement_harness_plan_sha256"], "harness_manifest_sha256": manifest["harness_manifest_sha256"], "implementation_summary": "P12 v3 response-protocol-only repair: frozen D-CYCLIC3 task/truth/model/temperature/tool schema unchanged; only final return protocol requires answers on the first response line before optional reasoning, with function-call priority; reuse three completed difficulty receipts and retry D-CYCLIC3-1 exactly once before unchanged skill/evaluation work.", "sandboxed": True, "probe_passed": True, "budget_feasible": True, "scientific_object_unchanged": True, "protocol_only_change": True, "replacement_provider_call_cap": REPLACEMENT_PROVIDER_CALL_CAP}]}
        write_json(run_root / REPAIR_RECEIPT_V3_FILENAME, receipt)
        repaired = compile_harness_runtime_repair_receipts(revoked, receipt)
        errors = validate_evidence_plan(repaired)
        if errors:
            raise ValueError(f"P12 v3 repaired authorization invalid:{errors}")
        write_json(output, repaired)
        row = next(x for x in repaired["entries"] if x.get("candidate_id") == CANDIDATE_ID)
        return {"status": "P12_RUNTIME_REPAIR_V3_AUTHORIZED", "execution_authorized": row["execution_authorized"], "harness_manifest_sha256": manifest["harness_manifest_sha256"], "replacement_harness_plan_sha256": plan["replacement_harness_plan_sha256"], "scientific_authority": False}
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def retry_failed_difficulty(run_root: Path, persistent_root: Path) -> dict[str, Any]:
    from .p12_recency_bias_protocol import authorization_ok

    authorization_ok(run_root)
    output = run_root / "difficulty-repair-v3" / f"{FAILED_PAIR}.json"
    lock = lock_output(output, {"stage": "p12-difficulty-repair-v3", "pair_id": FAILED_PAIR})
    try:
        pair = _pair()
        manifest = load_json(run_root / REPAIRED_IMPLEMENTATION_MANIFEST_V3_FILENAME)
        run_id = f"p12-recency-{manifest['harness_manifest_sha256'][:10]}-difficulty-repair-{FAILED_PAIR.lower()}"
        archive, failure = _call_once(persistent_root=persistent_root, run_id=run_id, stage="p12-difficulty-calibration-repair-v3", prompt=answer_first_prompt(pair), tools=difficulty_tool(), max_output_tokens=V3_MAX_OUTPUT_TOKENS)
        if archive is None:
            result = {"schema_version": "1.0", "status": "DIFFICULTY_PROVIDER_FAILURE", "pair_id": FAILED_PAIR, **failure}
            write_json(output, result)
            return result
        try:
            answers, source = parse_v3_difficulty_answers(archive)
        except Exception as error:
            _close_parse_failure(persistent_root=persistent_root, archive=archive, stage="p12-difficulty-calibration-repair-v3", error=error)
            result = {"schema_version": "1.0", "status": "DIFFICULTY_PROTOCOL_FAILURE", "pair_id": FAILED_PAIR, "raw_sha256": archive["raw_sha256"], "error": f"{type(error).__name__}:{error}", "scientific_authority": False, "belief_authority": False}
            write_json(output, result)
            return result
        result = {"schema_version": "1.0", "status": "DIFFICULTY_COMPLETE", "pair_id": FAILED_PAIR, "family": pair["family"], "raw_sha256": archive["raw_sha256"], "resolved_model": archive["resolved_model"], "response_status": archive.get("status"), "answer_source": source, "backward_answer": answers["backward_answer"], "forward_answer": answers["forward_answer"], "backward_truth": pair["backward"]["answer"], "forward_truth": pair["forward"]["answer"], "backward_success": answers["backward_answer"] == pair["backward"]["answer"], "forward_success": answers["forward_answer"] == pair["forward"]["answer"], "usage": archive["usage"], "runtime_repair_v3": True, "scientific_authority": False, "belief_authority": False}
        result["receipt_sha256"] = sha_json(result)
        record_parsed_api_output(run_root=persistent_root / "runs" / run_id, stage="p12-difficulty-calibration-repair-v3", raw_sha256=archive["raw_sha256"], structured_payload=result, requested_model=EXECUTOR_MODEL, resolved_model=archive["resolved_model"], research_objects=[], root=persistent_root)
        write_json(output, result)
        return result
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=("offline-probe", "transport-probe", "authorize", "retry"))
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--persistent-root", type=Path)
    args = parser.parse_args()
    if args.cmd == "offline-probe":
        out = run_offline_probe(args.run_root)
    elif args.cmd == "transport-probe":
        if args.persistent_root is None:
            raise SystemExit("--persistent-root required")
        out = run_neutral_transport_probe(args.run_root, args.persistent_root)
    elif args.cmd == "authorize":
        out = authorize_v3(args.run_root)
    else:
        if args.persistent_root is None:
            raise SystemExit("--persistent-root required")
        out = retry_failed_difficulty(args.run_root, args.persistent_root)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
