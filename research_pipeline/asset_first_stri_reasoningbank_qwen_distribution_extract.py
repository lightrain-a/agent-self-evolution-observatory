"""Freeze and execute official Qwen ReasoningBank memory extraction for all sources."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_ark_provider import ArkCompatibilityError
from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    OFFICIAL_COMMIT, INSTRUCTION_PATH, ROOT, canonical_json, load_instructions,
    sha256_file, sha256_text, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_agent import (
    MODEL, make_client, safe_response,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_memory import (
    memory_record,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
SOURCE_INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-index-20260901.json"
SOURCE_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-trajectories-20260901"
Q0 = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q0-result-20260901.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-memory-extraction-contract-20260901.json"
RECEIPT_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-memory-extraction-receipts-20260901"
BANK = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-bank-20260901.json"
INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-memory-extraction-index-20260901.json"
EXPECTED_CONTRACT_SHA256 = "PENDING"


def source_receipts() -> list[tuple[Path, dict[str, Any]]]:
    source_index = json.loads(SOURCE_INDEX.read_text(encoding="utf-8"))
    if source_index["decision"] != "QWEN_SOURCE_TRAJECTORIES_COMPLETE":
        raise RuntimeError("source trajectories incomplete")
    rows = []
    for journal in source_index["journal"]:
        matches = sorted(SOURCE_DIR.glob(f"{journal['ordinal']:02d}-*.json"))
        if len(matches) != 1 or sha256_file(matches[0]) != journal["receipt_sha256"]:
            raise RuntimeError("source trajectory receipt identity drift")
        rows.append((matches[0], json.loads(matches[0].read_text(encoding="utf-8"))))
    return rows


def trajectory_input(receipt: dict[str, Any]) -> str:
    trajectory = receipt["trajectory"]
    messages = trajectory.get("messages") or []
    visible = [str(row.get("content") or "") for row in messages if row.get("role") != "system"]
    if visible:
        return "\n".join(visible)
    failure = trajectory.get("failure") or {}
    return "Source trajectory terminated before model-visible interaction: " + canonical_json(failure)


def extraction_plan() -> list[dict[str, Any]]:
    plan = []
    for ordinal, (path, receipt) in enumerate(source_receipts(), start=1):
        trajectory = receipt["trajectory"]
        evaluator = trajectory.get("R4_terminal_outcome") or {}
        text = trajectory_input(receipt)
        plan.append({
            "ordinal": ordinal, "extraction_id": f"QWEN-MEMORY-{ordinal:02d}",
            "source_task_id": receipt["instance_id"],
            "source_repository": receipt["instance_id"].split("__", 1)[0],
            "source_receipt": str(path.relative_to(ROOT)),
            "source_receipt_sha256": sha256_file(path),
            "source_trajectory_sha256": sha256_text(canonical_json(trajectory)),
            "trajectory_input_sha256": sha256_text(text),
            "source_evaluator_valid": bool(evaluator.get("valid")),
            "source_resolved": bool(evaluator.get("resolved")),
            "instruction_key": "SUCCESSFUL_SI" if evaluator.get("resolved") else "FAILED_SI",
            "attempt_count": 1, "automatic_retry": False, "replacement": False,
        })
    return plan


def contract_payload() -> dict[str, Any]:
    plan = extraction_plan()
    q0 = json.loads(Q0.read_text(encoding="utf-8"))
    if q0["decision"] != "Q0_QWEN3_CODER_NEXT_PROVIDER_QUALIFIED":
        raise RuntimeError("Q0 gate closed")
    sampling = dict(q0["recommended_sampling_resolution"])
    instructions = load_instructions()
    if len(plan) not in {24, 32}:
        raise RuntimeError("source count drift")
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_REASONINGBANK_MEMORY_EXTRACTION",
        "created_at_utc": utcnow(),
        "decision": "QWEN_OFFICIAL_MEMORY_EXTRACTION_EXACTLY_ONCE_AUTHORIZED",
        "source_index_sha256": sha256_file(SOURCE_INDEX),
        "q0_sha256": sha256_file(Q0), "official_commit": OFFICIAL_COMMIT,
        "official_instruction_path": str(INSTRUCTION_PATH),
        "official_instruction_sha256": sha256_file(INSTRUCTION_PATH),
        "instruction_hashes": {key: sha256_text(value.strip())
                               for key, value in instructions.items()},
        "extractor_model": MODEL, "extractor_sampling": sampling,
        "max_memory_item_count_instruction": 3,
        "output_parser": "exact official response.split('\\n\\n') retaining nonempty blocks",
        "item_schema": "official Markdown Memory Item title/description/content",
        "plan": plan, "plan_sha256": sha256_text(canonical_json(plan)),
        "execution_policy": {
            "attempt_count": 1, "automatic_retry": False, "replacement": False,
            "successful_failed_timeout_sources_all_retained": True,
            "selective_memory_deletion": False,
        },
        "scientific_boundary": {
            "confirmatory_outcomes_observed": False,
            "fidelity_audit_authorized_after_bank": True,
            "retrieval_authorized_before_fidelity_pass": False,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }


def freeze_contract(output: Path = CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite memory extraction contract")
    payload = contract_payload()
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload),
            "source_count": len(payload["plan"])}


def receipt_path(unit: dict[str, Any]) -> Path:
    return RECEIPT_DIR / f"{unit['ordinal']:02d}-{unit['source_task_id'].replace('__', '-')}.json"


def run() -> dict[str, Any]:
    if EXPECTED_CONTRACT_SHA256 == "PENDING":
        raise RuntimeError("memory extraction contract SHA not pinned")
    if sha256_file(CONTRACT) != EXPECTED_CONTRACT_SHA256:
        raise RuntimeError("memory extraction contract SHA drift")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract["source_index_sha256"] != sha256_file(SOURCE_INDEX):
        raise RuntimeError("source index binding drift")
    instructions = load_instructions()
    client = make_client()
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    if INDEX.exists():
        prior = json.loads(INDEX.read_text(encoding="utf-8"))
        inflight = prior.get("inflight")
        if inflight:
            unit = contract["plan"][int(inflight["ordinal"]) - 1]
            if not receipt_path(unit).exists():
                raise RuntimeError(
                    "MEMORY_EXTRACTION_AMBIGUOUS_INFLIGHT_HOLD: refusing duplicate generation"
                )
    completed: list[dict[str, Any]] = []
    for unit in contract["plan"]:
        target = receipt_path(unit)
        if target.exists():
            saved = json.loads(target.read_text(encoding="utf-8"))
            if saved["attempt_count"] != 1 or saved["extraction_id"] != unit["extraction_id"]:
                raise RuntimeError("memory receipt identity drift")
            completed.append(saved)
            continue
        if len(completed) != unit["ordinal"] - 1:
            raise RuntimeError("memory receipts are not frozen-order prefix")
        source_path = ROOT / unit["source_receipt"]
        if sha256_file(source_path) != unit["source_receipt_sha256"]:
            raise RuntimeError("source receipt drift")
        source = json.loads(source_path.read_text(encoding="utf-8"))
        text = trajectory_input(source)
        if sha256_text(text) != unit["trajectory_input_sha256"]:
            raise RuntimeError("memory trajectory input drift")
        task = str(source["trajectory"].get("task_sha256") or unit["source_task_id"])
        task_text = str(source["trajectory"].get("problem_statement") or "")
        if not task_text:
            raise RuntimeError("source problem statement absent from trajectory receipt")
        prompt = f"**Query:** {task_text}\n\n**Trajectory:**\n{text}"
        instruction = instructions[unit["instruction_key"]].strip()
        write_json(INDEX, index_payload(contract, completed, inflight={
            "ordinal": unit["ordinal"], "extraction_id": unit["extraction_id"],
            "source_task_id": unit["source_task_id"], "attempt_count": 1,
            "state": "DISPATCHED_BEFORE_PROVIDER_CALL",
        }))
        request = {
            "model": MODEL, "input": prompt, "instructions": instruction,
            "temperature": contract["extractor_sampling"]["temperature"],
            "top_p": contract["extractor_sampling"]["top_p"],
            "max_output_tokens": contract["extractor_sampling"]["max_output_tokens"],
            "store": True,
        }
        if isinstance(contract["extractor_sampling"].get("top_k"), int):
            request["top_k"] = contract["extractor_sampling"]["top_k"]
        try:
            response = client.create_response(
                input_items=prompt, instructions=instruction, model=MODEL,
                temperature=request["temperature"], top_p=request["top_p"],
                top_k=request.get("top_k"),
                max_output_tokens=request["max_output_tokens"], store=True)
            safe = safe_response(response)
            if safe["resolved_model"] != MODEL or safe["transport_attempts"] != 1:
                raise RuntimeError("extractor provider identity/retry drift")
            raw = safe["text"]
            status, failure = "COMPLETED", None
        except (ArkCompatibilityError, RuntimeError) as error:
            raw, safe, status = "", None, "TERMINAL_PROVIDER_OR_IDENTITY_FAILURE"
            failure = {
                "failure_layer": "provider", "error_type": type(error).__name__,
                "message": str(error) if not isinstance(error, ArkCompatibilityError) else None,
                "safe_receipt": error.safe_receipt() if isinstance(error, ArkCompatibilityError) else None,
            }
        record = memory_record(
            source_task_id=unit["source_task_id"],
            source_repository=unit["source_repository"], source_query=task_text,
            task_sha256=task, trajectory_sha256=unit["source_trajectory_sha256"],
            source_resolved=unit["source_resolved"], raw_response=raw,
            policy_model=MODEL, extractor_model=MODEL,
            provider_config_sha256=sha256_text(canonical_json(contract["extractor_sampling"])),
            evaluator_result={"valid": unit["source_evaluator_valid"],
                              "resolved": unit["source_resolved"]})
        receipt = {
            **unit, "created_at_utc": utcnow(), "execution_status": status,
            "request_sha256": sha256_text(canonical_json(request)),
            "response": safe, "failure": failure, "memory": record,
            "credential_material_present": False,
        }
        write_json(target, receipt)
        completed.append(json.loads(target.read_text(encoding="utf-8")))
        write_json(INDEX, index_payload(contract, completed))
        print(json.dumps({"ordinal": unit["ordinal"], "source_task_id": unit["source_task_id"],
                          "execution_status": status, "completed": len(completed)}, sort_keys=True), flush=True)
    bank_entries = [row["memory"] for row in completed]
    bank_payload = {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_REASONINGBANK_SOURCE_BANK",
        "created_at_utc": utcnow(), "decision": "QWEN_SOURCE_BANK_FROZEN_PENDING_FIDELITY_AUDIT",
        "contract_sha256": sha256_file(CONTRACT), "source_index_sha256": sha256_file(SOURCE_INDEX),
        "memory_count": len(bank_entries),
        "memory_with_nonempty_items_count": sum(bool(row["parsed_memory_items"]) for row in bank_entries),
        "entries": bank_entries,
        "entry_set_sha256": sha256_text(canonical_json(bank_entries)),
        "selective_memory_deletion_performed": False,
        "credential_material_present": False,
    }
    if BANK.exists():
        raise RuntimeError("refusing to overwrite source bank")
    bank_sha = write_json(BANK, bank_payload)
    final = index_payload(contract, completed)
    final["source_bank_path"] = str(BANK.relative_to(ROOT))
    final["source_bank_sha256"] = bank_sha
    final["decision"] = "QWEN_MEMORY_EXTRACTION_COMPLETE_SOURCE_BANK_FROZEN"
    return {"decision": final["decision"], "index_sha256": write_json(INDEX, final),
            "source_bank_sha256": bank_sha, "memory_count": len(bank_entries)}


def index_payload(contract: dict[str, Any], completed: list[dict[str, Any]],
                  inflight: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_REASONINGBANK_MEMORY_EXTRACTION",
        "created_at_utc": utcnow(),
        "decision": "QWEN_MEMORY_EXTRACTION_IN_PROGRESS",
        "execution_complete": len(completed) == len(contract["plan"]),
        "planned_count": len(contract["plan"]), "completed_count": len(completed),
        "journal_record_count": len(completed),
        "inflight": inflight,
        "journal": [{
            "ordinal": row["ordinal"], "extraction_id": row["extraction_id"],
            "source_task_id": row["source_task_id"], "attempt_count": row["attempt_count"],
            "execution_status": row["execution_status"], "persisted": True,
            "receipt_sha256": sha256_file(receipt_path(row)),
        } for row in completed],
        "checks": {
            "every_attempt_count_one": all(row["attempt_count"] == 1 for row in completed),
            "no_retry": True, "no_replacement": True,
            "selective_memory_deletion": False,
        },
        "credential_material_present": False,
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-contract", action="store_true")
    args = parser.parse_args()
    print(json.dumps(freeze_contract() if args.freeze_contract else run(), sort_keys=True))


if __name__ == "__main__":
    main()
