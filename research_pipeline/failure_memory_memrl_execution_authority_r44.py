"""Record the user's bounded execution authorization for B1 MemRL R44.

The receipt authorizes exactly the already-frozen R43 transaction. It does not
change scientific belief, expand claims, authorize external provider spend, or
permit outcome-adaptive reruns/selection.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .failure_memory_memrl_g8_manifest_r43 import OUT as G8_PATH, validate as validate_g8

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
SYNTHETIC = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r43-synthetic-stack-smoke.json"
OUT = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r44-human-execution-authorization.json"
EXPECTED_G8_RECEIPT = "ed496819814765359a85f190c71de04f7c19c9788da27784b7c588b1ab5f2fce"
EXPECTED_SYNTHETIC_RECEIPT = "abd02364984657e25430b26fe111225566adc1ae9bfc658f14392f93b092133e"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object:{path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build() -> dict[str, Any]:
    g8 = _load(G8_PATH)
    synthetic = _load(SYNTHETIC)
    errors = validate_g8(g8)
    if errors:
        raise ValueError("g8-invalid:" + ";".join(errors))
    if g8.get("receipt_sha256") != EXPECTED_G8_RECEIPT:
        raise ValueError("g8-receipt-drift")
    if synthetic.get("receipt_sha256") != EXPECTED_SYNTHETIC_RECEIPT:
        raise ValueError("synthetic-stack-receipt-drift")
    if int((synthetic.get("access_accounting") or {}).get("confirmatory_outcomes_observed") or 0) != 0:
        raise ValueError("pre-authorization-outcome-leak")

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R44-HUMAN-EXECUTION-AUTHORIZATION",
        "recorded_date": "2026-08-29",
        "status": "HUMAN_BOUNDED_EXECUTION_AUTHORITY_RECORDED",
        "authorized_by": "explicit user directive in the current conversation to continue B1 experiments; subsequently reaffirmed with '继续'",
        "bindings": {
            "g8_manifest": {"path": str(G8_PATH.relative_to(PROJECT_ROOT)), "sha256": _sha(G8_PATH), "receipt_sha256": g8.get("receipt_sha256")},
            "synthetic_stack": {"path": str(SYNTHETIC.relative_to(PROJECT_ROOT)), "sha256": _sha(SYNTHETIC), "receipt_sha256": synthetic.get("receipt_sha256")},
        },
        "authorized_scope": {
            "source_build": {
                "authorized": True,
                "count": 1,
                "exact_selected_source_tasks": 128,
                "source_selection_sha256": ((g8.get("execution_manifest") or {}).get("source_build") or {}).get("selected_ids_sha256"),
                "external_provider_spend": False,
            },
            "utilization_qualification": {
                "authorized_conditionally_after_source_qualification": True,
                "count": 1,
                "exact_clusters": 8,
                "arms": ["U0_no_memory", "U1_true_memory", "U2_null_memory", "U3_reversed_memory", "U4_shuffled_memory"],
            },
            "primary_confirmatory": {
                "authorized_conditionally_after_source_and_utilization_qualification": True,
                "count": 1,
                "exact_clusters": 32,
                "arms": ["A_content_only", "B_raw_provenance", "C_PSMG", "D_nonprovenance_controller"],
            },
        },
        "hard_limits": {
            "rerun_after_observing_effect": False,
            "outcome_driven_unit_replacement": False,
            "model_or_embedding_change": False,
            "runtime_image_change": False,
            "threshold_or_effect_floor_change": False,
            "arm_semantics_change": False,
            "optional_stopping_on_effect": False,
            "historical_evidence_pooling": False,
            "second_backbone": False,
            "external_provider_calls": False,
        },
        "authority": {
            "execution": True,
            "local_gpu": True,
            "external_provider_spend": False,
            "scientific_belief": False,
            "paper_claim_expansion": False,
            "submission": False,
        },
        "failure_routing": {
            "source_qualification_failure": "SUPPORT_STOP_NO_BEHAVIORAL_VERDICT",
            "utilization_qualification_failure": "OPERATIONALIZATION_STOP_MEMORY_NOT_BEHAVIORALLY_USED",
            "runtime_failure": "EXECUTION_DIAGNOSTIC_ONLY_NO_SCIENTIFIC_UPDATE",
        },
    }
    payload["receipt_sha256"] = _digest({k: v for k, v in payload.items() if k != "receipt_sha256"})
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("status") != "HUMAN_BOUNDED_EXECUTION_AUTHORITY_RECORDED":
        errors.append("status")
    authority = payload.get("authority") or {}
    if authority.get("execution") is not True or authority.get("local_gpu") is not True:
        errors.append("execution-authority")
    if authority.get("external_provider_spend") is not False or authority.get("scientific_belief") is not False or authority.get("paper_claim_expansion") is not False or authority.get("submission") is not False:
        errors.append("authority-leak")
    hard = payload.get("hard_limits") or {}
    if any(value is not False for value in hard.values()):
        errors.append("hard-limit-drift")
    scope = payload.get("authorized_scope") or {}
    if int((scope.get("source_build") or {}).get("count") or 0) != 1 or int((scope.get("source_build") or {}).get("exact_selected_source_tasks") or 0) != 128:
        errors.append("source-scope")
    if int((scope.get("utilization_qualification") or {}).get("exact_clusters") or 0) != 8:
        errors.append("utilization-scope")
    if int((scope.get("primary_confirmatory") or {}).get("exact_clusters") or 0) != 32:
        errors.append("primary-scope")
    expected = _digest({k: v for k, v in payload.items() if k != "receipt_sha256"})
    if payload.get("receipt_sha256") != expected:
        errors.append("receipt-hash")
    return errors


def write(path: Path = OUT) -> dict[str, Any]:
    row = build()
    errors = validate(row)
    if errors:
        raise ValueError("invalid B1 R44 execution authority:" + ";".join(errors))
    path.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return row


if __name__ == "__main__":
    row = write()
    print(json.dumps({"status": row["status"], "receipt_sha256": row["receipt_sha256"], "authorized_scope": row["authorized_scope"], "authority": row["authority"]}, ensure_ascii=False, sort_keys=True))
