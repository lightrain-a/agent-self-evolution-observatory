"""Independent Kimi-K3 source-memory fidelity audit and bank gate."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_ark_provider import (
    ArkCompatibilityError, ArkReasoningBankClient, ArkReasoningBankSettings,
    CANONICAL_SECRET_FILE,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    BASE_URL, ROOT, canonical_json, sha256_file, sha256_text, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_memory import (
    adjudicate_fidelity, audit_sample,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
REVIEWER_MODEL = "kimi-k3"
BANK = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-bank-20260901.json"
SOURCE_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-trajectories-20260901"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-fidelity-audit-contract-20260901.json"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-fidelity-audit-result-20260901.json"
EXPECTED_CONTRACT_SHA256 = "PENDING"
JSON_RE = re.compile(r"\{.*\}", re.DOTALL)
SYSTEM = """You are an independent source-memory fidelity auditor. Judge only the supplied
source task, source trajectory, and extracted memory. Never infer or request downstream
evaluation outcomes. Return one JSON object with exactly these keys:
faithful_to_source_trajectory (boolean), unsupported_facts_absent (boolean),
gold_or_unavailable_test_leak_absent (boolean), plausible_reusable_lesson (boolean),
SEVERE_FIDELITY_FAILURE (boolean), rationale (string).
SEVERE_FIDELITY_FAILURE is true only for a material fidelity, invention, leakage, or
non-lesson failure. Do not propose deleting individual memories."""


def parse_review(text: str) -> dict[str, Any]:
    matches = JSON_RE.findall(text)
    if len(matches) != 1:
        raise ValueError("independent review did not contain one JSON object")
    row = json.loads(matches[0])
    expected = {
        "faithful_to_source_trajectory", "unsupported_facts_absent",
        "gold_or_unavailable_test_leak_absent", "plausible_reusable_lesson",
        "SEVERE_FIDELITY_FAILURE", "rationale",
    }
    if set(row) != expected:
        raise ValueError("independent review schema drift")
    if any(not isinstance(row[key], bool) for key in expected - {"rationale"}):
        raise ValueError("independent review booleans invalid")
    if not isinstance(row["rationale"], str) or not row["rationale"].strip():
        raise ValueError("independent review rationale invalid")
    return row


def source_receipt(task_id: str) -> tuple[Path, dict[str, Any]]:
    matches = sorted(SOURCE_DIR.glob(f"*-{task_id.replace('__', '-')}.json"))
    if len(matches) != 1:
        raise RuntimeError("source receipt missing for fidelity audit")
    return matches[0], json.loads(matches[0].read_text(encoding="utf-8"))


def contract_payload() -> dict[str, Any]:
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    if bank["decision"] != "QWEN_SOURCE_BANK_FROZEN_PENDING_FIDELITY_AUDIT":
        raise RuntimeError("source bank gate closed")
    task_ids = [row["source_task_id"] for row in bank["entries"]]
    selected = audit_sample(task_ids, experiment_id=EXPERIMENT_ID)
    plan = []
    by_task = {row["source_task_id"]: row for row in bank["entries"]}
    for ordinal, task_id in enumerate(selected, start=1):
        path, source = source_receipt(task_id)
        plan.append({
            "ordinal": ordinal, "audit_id": f"QWEN-FIDELITY-{ordinal:02d}",
            "source_task_id": task_id, "source_receipt": str(path.relative_to(ROOT)),
            "source_receipt_sha256": sha256_file(path),
            "memory_record_sha256": sha256_text(canonical_json(by_task[task_id])),
            "attempt_count": 1,
        })
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "INDEPENDENT_SOURCE_MEMORY_FIDELITY_AUDIT",
        "created_at_utc": utcnow(),
        "decision": "KIMI_K3_25_PERCENT_FIDELITY_AUDIT_AUTHORIZED",
        "source_bank_sha256": sha256_file(BANK),
        "source_task_count": len(task_ids), "audit_task_count": len(selected),
        "audit_fraction": .25, "selection_rule": "ascending SHA256(experiment_id||task_id)",
        "reviewer_model": REVIEWER_MODEL, "reviewer_system_sha256": sha256_text(SYSTEM),
        "reviewer_config": {"temperature": 0.0, "max_output_tokens": 4096,
                            "max_retries": 0, "streaming": False},
        "plan": plan, "plan_sha256": sha256_text(canonical_json(plan)),
        "gate": "SOURCE_BANK_FIDELITY_UNQUALIFIED only when severe failures > 25% audited",
        "selective_memory_deletion_forbidden": True,
        "confirmatory_behavioral_outcomes_visible": False,
        "credential_material_present": False,
    }


def freeze_contract(output: Path = CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite fidelity contract")
    payload = contract_payload()
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload),
            "audit_task_count": payload["audit_task_count"]}


def make_reviewer() -> ArkReasoningBankClient:
    base = ArkReasoningBankSettings.from_env_file(CANONICAL_SECRET_FILE)
    return ArkReasoningBankClient(ArkReasoningBankSettings(
        api_key=base.api_key, base_url=BASE_URL, model=REVIEWER_MODEL,
        timeout_seconds=120.0, max_retries=0))


def run(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing duplicate fidelity audit")
    if EXPECTED_CONTRACT_SHA256 == "PENDING":
        raise RuntimeError("fidelity contract SHA not pinned")
    if sha256_file(CONTRACT) != EXPECTED_CONTRACT_SHA256:
        raise RuntimeError("fidelity contract SHA drift")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    if contract["source_bank_sha256"] != sha256_file(BANK):
        raise RuntimeError("fidelity bank binding drift")
    by_task = {row["source_task_id"]: row for row in bank["entries"]}
    client = make_reviewer()
    reviews = []
    implementation_failures = []
    for unit in contract["plan"]:
        path = ROOT / unit["source_receipt"]
        if sha256_file(path) != unit["source_receipt_sha256"]:
            raise RuntimeError("fidelity source receipt drift")
        source = json.loads(path.read_text(encoding="utf-8"))
        memory = by_task[unit["source_task_id"]]
        visible = {
            "source_task_id": unit["source_task_id"],
            "source_task_sha256": memory["task_sha256"],
            "source_trajectory": source["trajectory"].get("messages")
                or source["trajectory"].get("failure"),
            "extracted_memory": memory["parsed_memory_items"],
        }
        try:
            response = client.create_response(
                input_items=canonical_json(visible), instructions=SYSTEM,
                model=REVIEWER_MODEL, temperature=0.0,
                max_output_tokens=4096, store=True)
            if response.get("resolved_model") != REVIEWER_MODEL or response.get("transport_attempts") != 1:
                raise RuntimeError("independent reviewer identity/retry drift")
            parsed = parse_review(str(response.get("raw_text", response.get("text", ""))))
            reviews.append({
                **unit, **parsed,
                "request_sha256": sha256_text(canonical_json(visible)),
                "response_sha256": sha256_text(str(response.get("raw_text", response.get("text", "")))),
                "resolved_model": response.get("resolved_model"),
                "credential_material_present": False,
            })
        except (ArkCompatibilityError, RuntimeError, ValueError) as error:
            implementation_failures.append({
                **unit, "failure_layer": "provider_or_parser",
                "error_type": type(error).__name__,
                "safe_receipt": error.safe_receipt() if isinstance(error, ArkCompatibilityError) else None,
                "credential_material_present": False,
            })
    complete = len(reviews) == len(contract["plan"])
    gate = adjudicate_fidelity(reviews) if complete else {
        "decision": "SOURCE_BANK_FIDELITY_AUDIT_IMPLEMENTATION_HOLD",
        "audited_source_task_count": len(reviews),
    }
    payload = {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "INDEPENDENT_SOURCE_MEMORY_FIDELITY_AUDIT",
        "created_at_utc": utcnow(), "decision": gate["decision"],
        "contract_sha256": sha256_file(CONTRACT), "source_bank_sha256": sha256_file(BANK),
        "reviews": reviews, "implementation_failures": implementation_failures,
        "gate": gate, "all_source_memories_retained": True,
        "selective_memory_deletion_performed": False,
        "confirmatory_behavioral_outcomes_visible": False,
        "credential_material_present": False,
    }
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload),
            "completed_review_count": len(reviews),
            "severe_failure_count": gate.get("severe_fidelity_failure_count")}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-contract", action="store_true")
    args = parser.parse_args()
    print(json.dumps(freeze_contract() if args.freeze_contract else run(), sort_keys=True))


if __name__ == "__main__":
    main()
