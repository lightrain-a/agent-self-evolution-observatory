"""Preregister and execute Qwen backend stochasticity qualification (Q1)."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_qwen_provider import (
    DIANMING_BASE_URL, DIANMING_SECRET_FILE, QwenChatClient, QwenChatSettings,
    QwenProviderError,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    FORMAT_RE, ROOT, canonical_json, sha256_file, sha256_text,
    utcnow, write_json,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
MODEL = "qwen3-coder-next"
BASE_URL = DIANMING_BASE_URL
K_Q1 = 20
Q0_RESULT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q0-result-20260901.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q1-contract-20260901.json"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q1-result-20260901.json"
INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q1-index-20260901.json"
RECEIPT_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q1-receipts-20260901"
EXPECTED_CONTRACT_SHA256 = "PENDING"
FENCE = chr(96) * 3
FIXED_PROMPT = (
    "This is a synthetic non-benchmark parser check. Return exactly one fenced "
    "bash action and no prose. The action must be:\n"
    + FENCE + "bash\nprintf 'Q1_FIXED_ACTION\\n'\n" + FENCE + "\n"
)


def load_q0() -> dict[str, Any]:
    if not Q0_RESULT.is_file():
        raise RuntimeError("Q0 result absent")
    result = json.loads(Q0_RESULT.read_text(encoding="utf-8"))
    if result["decision"] != "Q0_QWEN3_CODER_NEXT_PROVIDER_QUALIFIED":
        raise RuntimeError("Q0 did not authorize Q1")
    return result


def request_body(sampling: dict[str, Any]) -> dict[str, Any]:
    if sampling["max_retries"] != 0:
        raise RuntimeError("Q0 sampling drift: retries enabled")
    body: dict[str, Any] = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Follow the mini-SWE-agent fenced-bash action format exactly."},
            {"role": "user", "content": FIXED_PROMPT},
        ],
        "max_completion_tokens": int(sampling["max_output_tokens"]),
        "temperature": float(sampling["temperature"]),
        "top_p": float(sampling["top_p"]),
        "n": 1,
        "stream": False,
    }
    if isinstance(sampling.get("top_k"), int):
        body["top_k"] = int(sampling["top_k"])
    return body


def contract_payload() -> dict[str, Any]:
    q0 = load_q0()
    request = request_body(dict(q0["recommended_sampling_resolution"]))
    plan = [{"ordinal": i, "trial_id": f"Q1-{i:02d}", "attempt_count": 1}
            for i in range(1, K_Q1 + 1)]
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "Q1_QWEN_BACKEND_STOCHASTICITY_QUALIFICATION",
        "created_at_utc": utcnow(),
        "decision": "Q1_K20_EXACT_REQUEST_EXECUTION_AUTHORIZED",
        "q0_result_path": str(Q0_RESULT.relative_to(ROOT)),
        "q0_result_sha256": sha256_file(Q0_RESULT),
        "requested_model": MODEL, "resolved_model_requirement": MODEL,
        "fixed_nonbenchmark_prompt": True, "benchmark_calls_authorized": False,
        "request": request, "request_sha256": sha256_text(canonical_json(request)),
        "K_Q1": K_Q1, "trial_plan": plan,
        "trial_plan_sha256": sha256_text(canonical_json(plan)),
        "execution_policy": {
            "exactly_once_per_trial": True, "attempt_count": 1,
            "automatic_retry": False, "replacement": False,
            "max_retries": 0, "streaming": False,
        },
        "classification_rule": {
            "DETERMINISTIC": "all 20 response and normalized-action hashes identical",
            "STOCHASTIC": "at least two response or normalized-action hashes",
            "UNQUALIFIED": "fewer than 20 valid exactly-once receipts",
        },
        "scientific_boundary": {
            "source_generation_authorized": False,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }


def freeze_contract(output: Path = CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite immutable Q1 contract")
    payload = contract_payload()
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload),
            "trial_count": len(payload["trial_plan"])}


def normalize_action(text: str) -> dict[str, Any]:
    actions = FORMAT_RE.findall(text)
    valid = len(actions) == 1 and bool(actions[0].strip())
    action = actions[0].strip() if valid else ""
    first = action.splitlines()[0].strip() if action else ""
    if not action:
        kind = "PARSE_INVALID"
    elif first.startswith(("ls ", "find ", "tree ")):
        kind = "LIST"
    elif first.startswith(("rg ", "grep ")):
        kind = "SEARCH"
    elif first.startswith(("cat ", "sed ", "head ", "tail ", "git diff", "git status")):
        kind = "READ"
    elif first.startswith(("pytest", "python -m pytest", "tox", "make test")):
        kind = "TEST"
    else:
        kind = "OTHER"
    signature = {"parse_valid": valid, "action_class": kind,
                 "first_line": first, "normalized_action": action}
    signature["signature_sha256"] = sha256_text(canonical_json(signature))
    return signature


def make_client() -> QwenChatClient:
    base = QwenChatSettings.from_env_file(DIANMING_SECRET_FILE)
    if base.base_url.rstrip("/") != BASE_URL or base.model != MODEL:
        raise RuntimeError("Q1 provider base URL/model drift")
    return QwenChatClient(QwenChatSettings(
        api_key=base.api_key, base_url=BASE_URL, model=MODEL,
        timeout_seconds=120.0, max_retries=0))


def receipt_path(planned: dict[str, Any]) -> Path:
    return RECEIPT_DIR / f"{int(planned['ordinal']):02d}-{planned['trial_id']}.json"


def index_payload(contract: dict[str, Any], receipts: list[dict[str, Any]],
                  inflight: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "Q1_QWEN_BACKEND_STOCHASTICITY_QUALIFICATION",
        "created_at_utc": utcnow(), "contract_sha256": sha256_file(CONTRACT),
        "planned_count": K_Q1, "completed_count": len(receipts),
        "journal_record_count": len(receipts), "inflight": inflight,
        "execution_complete": len(receipts) == K_Q1,
        "journal": [{
            "ordinal": row["ordinal"], "trial_id": row["trial_id"],
            "attempt_count": row["attempt_count"], "status": row["status"],
            "persisted": True, "receipt_sha256": sha256_file(receipt_path(row)),
        } for row in receipts],
        "checks": {"every_attempt_count_one": all(row["attempt_count"] == 1 for row in receipts),
                   "no_retry": True, "no_replacement": True,
                   "frozen_order_prefix": True},
        "credential_material_present": False,
    }


def execute(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing duplicate Q1 execution")
    if EXPECTED_CONTRACT_SHA256 == "PENDING":
        raise RuntimeError("Q1 contract SHA not pinned")
    if sha256_file(CONTRACT) != EXPECTED_CONTRACT_SHA256:
        raise RuntimeError("Q1 contract SHA drift")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract["q0_result_sha256"] != sha256_file(Q0_RESULT):
        raise RuntimeError("Q1 Q0 binding drift")
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    receipts: list[dict[str, Any]] = []
    missing_seen = False
    for planned in contract["trial_plan"]:
        path = receipt_path(planned)
        if not path.exists():
            missing_seen = True
            continue
        if missing_seen:
            raise RuntimeError("Q1 receipts are not a frozen-order prefix")
        row = json.loads(path.read_text(encoding="utf-8"))
        if row["trial_id"] != planned["trial_id"] or row["attempt_count"] != 1:
            raise RuntimeError("Q1 receipt identity/attempt drift")
        receipts.append(row)
    if INDEX.exists():
        prior = json.loads(INDEX.read_text(encoding="utf-8"))
        inflight = prior.get("inflight")
        if inflight:
            planned = contract["trial_plan"][int(inflight["ordinal"]) - 1]
            if not receipt_path(planned).exists():
                raise RuntimeError("Q1_AMBIGUOUS_INFLIGHT_HOLD: refusing duplicate trial")
    write_json(INDEX, index_payload(contract, receipts))
    request, client = dict(contract["request"]), make_client()
    for planned in contract["trial_plan"][len(receipts):]:
        write_json(INDEX, index_payload(contract, receipts, {
            "ordinal": planned["ordinal"], "trial_id": planned["trial_id"],
            "attempt_count": 1, "state": "DISPATCHED_BEFORE_PROVIDER_CALL"}))
        started = time.monotonic()
        try:
            response = client.create_response(
                input_items=request["messages"], model=request["model"],
                max_output_tokens=request["max_completion_tokens"],
                temperature=request["temperature"], top_p=request["top_p"],
                top_k=request.get("top_k"))
            if response.get("actual_request_sha256") != contract["request_sha256"]:
                raise RuntimeError("Q1 actual Chat request hash drift")
            raw = str(response.get("raw_text", response.get("text", "")))
            row = {
                **planned, "status": "SUCCESS",
                "request_sha256": contract["request_sha256"],
                "response_sha256": sha256_text(raw),
                "raw_payload_sha256": response.get("raw_payload_sha256"),
                "normalized_action": normalize_action(raw),
                "requested_model": response.get("requested_model"),
                "resolved_model": response.get("resolved_model"),
                "usage": response.get("usage") or {},
                "safe_rate_quota_headers": response.get("response_headers") or {},
                "transport_attempts": response.get("transport_attempts"),
                "latency_seconds": round(time.monotonic() - started, 6),
                "credential_material_present": False,
            }
        except QwenProviderError as error:
            row = {
                **planned, "status": "FAILED",
                "request_sha256": contract["request_sha256"],
                "failure": error.safe_receipt(), "transport_attempts": 1,
                "latency_seconds": round(time.monotonic() - started, 6),
                "credential_material_present": False,
            }
        target = receipt_path(planned)
        if target.exists():
            raise RuntimeError("refusing to overwrite Q1 receipt")
        write_json(target, row)
        receipts.append(json.loads(target.read_text(encoding="utf-8")))
        write_json(INDEX, index_payload(contract, receipts))
        print(json.dumps({"ordinal": planned["ordinal"], "trial_id": planned["trial_id"],
                          "status": row["status"], "completed": len(receipts)},
                         sort_keys=True), flush=True)
        if row["status"] != "SUCCESS":
            break
    if len(receipts) != K_Q1:
        return {"decision": "Q1_PROVIDER_HOLD_REMAINING_TRIALS_UNTOUCHED",
                "backend_classification": "UNQUALIFIED", "execution_complete": False,
                "completed_count": len(receipts), "index_sha256": sha256_file(INDEX)}
    successful = [r for r in receipts if r["status"] == "SUCCESS"]
    valid = [r for r in successful if r["normalized_action"]["parse_valid"]]
    response_hashes = sorted({r["response_sha256"] for r in successful})
    action_hashes = sorted({r["normalized_action"]["signature_sha256"] for r in valid})
    once = all(r["attempt_count"] == 1 and int(r.get("transport_attempts") or 0) <= 1
               for r in receipts)
    qualified = (len(valid) == K_Q1 and once
                 and all(r.get("resolved_model") == MODEL for r in successful))
    if not qualified:
        backend, decision = "UNQUALIFIED", "Q1_BACKEND_STOCHASTICITY_QUALIFICATION_HOLD"
    elif len(response_hashes) == len(action_hashes) == 1:
        backend, decision = "DETERMINISTIC", "Q1_QWEN_BACKEND_DETERMINISTIC_SOURCE_GATE_OPEN"
    else:
        backend, decision = "STOCHASTIC", "Q1_QWEN_BACKEND_STOCHASTIC_SOURCE_GATE_OPEN"
    payload = {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "Q1_QWEN_BACKEND_STOCHASTICITY_QUALIFICATION",
        "created_at_utc": utcnow(), "decision": decision,
        "contract_path": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": sha256_file(CONTRACT),
        "q0_result_sha256": sha256_file(Q0_RESULT), "index_sha256": sha256_file(INDEX),
        "request_sha256": contract["request_sha256"], "K_Q1": K_Q1,
        "receipt_count": len(receipts), "successful_count": len(successful),
        "parse_valid_count": len(valid),
        "unique_response_hash_count": len(response_hashes),
        "unique_action_signature_count": len(action_hashes),
        "response_hashes": response_hashes, "action_signature_hashes": action_hashes,
        "backend_classification": backend, "exactly_once": once,
        "attempt_counts": [r["attempt_count"] for r in receipts],
        "retry_count": 0, "replacement_count": 0, "receipts": receipts,
        "scientific_boundary": {"benchmark_calls_made": 0,
            "source_generation_authorized": qualified,
            "confirmatory_execution_authorized": False},
        "credential_material_present": False,
    }
    return {"decision": decision, "backend_classification": backend,
            "file_sha256": write_json(output, payload),
            "successful_count": len(successful)}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-contract", action="store_true")
    args = parser.parse_args()
    print(json.dumps(freeze_contract() if args.freeze_contract else execute(), sort_keys=True))


if __name__ == "__main__":
    main()
