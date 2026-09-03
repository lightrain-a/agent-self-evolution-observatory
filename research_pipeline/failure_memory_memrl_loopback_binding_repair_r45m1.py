"""Versioned pre-exposure loopback binding repair for B1 R45-M1.

The first replacement manifest accidentally retained the forensic R43 loopback
server path/hash even though host 231 was qualified with the R45-M1 loopback
server that differs only in physical model roots, device placement, and labels.
This module never overwrites the frozen v1 objects.  It creates a v2 execution
closure and authority only if the scientific projection remains byte-identical
and no scientific/validation exposure is recorded by the Q5-v2 gate.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
R43 = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r43-memrl-g8-execution-manifest.json"
V1_MANIFEST = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r45m1-host-migration-execution-manifest.json"
V1_AUTHORITY = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r45m1-replacement-execution-authority.json"
Q5_PASS = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r45m1-q5v2-host-migration-equivalence-pass.json"
TRANSFER_REPAIR = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r45m1-preexposure-runner-transfer-repair-20260901.json"
SERVER = PROJECT_ROOT / "research_pipeline" / "failure_memory_memrl_local_openai_server_r45m1.py"

REPAIR_OUT = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r45m1-loopback-binding-repair-20260901.json"
DIFF_OUT = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r45m1-old-r43-vs-replacement-manifest-v2-diff.json"
MANIFEST_V2_OUT = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r45m1-host-migration-execution-manifest-v2.json"
AUTHORITY_V2_OUT = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r45m1-replacement-execution-authority-v2.json"

EXPECTED_SERVER_SHA256 = "f2b4b49b179856cdd02d244fba81ab7c558e747954170285da0eef6119336d92"
EXPECTED_V1_SERVER_SHA256 = "fd43b687a094de3ca2c5b1bdcabfbc39f7dfba324ccf8f1600615969698b5e8b"
EXPECTED_MANIFEST_STATUS = "MEMRL_R45M1_INFRASTRUCTURE_ONLY_REPLACEMENT_MANIFEST_FROZEN_ZERO_CONFIRMATORY_OUTCOMES"
EXPECTED_AUTHORITY_STATUS = "HUMAN_BOUNDED_R45M1_REPLACEMENT_EXECUTION_AUTHORITY_RECORDED"

ALLOWED_INFRASTRUCTURE_PATHS = {
    "host.logical_name",
    "host.ssh_identity",
    "host.gpu_assignment.llm",
    "host.gpu_assignment.embedding",
    "host.gpu_assignment.environment",
    "host.python",
    "host.pythonpath",
    "host.runtime_tree_sha256",
    "host.runtime_manifest_sha256",
    "host.runtime_manifest_file_sha256",
    "source.checkout",
    "models.llm.root",
    "models.llm.device",
    "models.embedding.root",
    "models.embedding.device",
    "runtime_image.qualified_tag",
    "runtime_image.execution_tag",
    "runtime_image.id",
    "runtime_image.execution_tag_same_content_identity",
    "external_runtime_adapter.loopback_server_path",
    "external_runtime_adapter.loopback_server_sha256",
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object:{path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _valid_receipt(value: dict[str, Any]) -> bool:
    observed = value.get("receipt_sha256")
    return isinstance(observed, str) and observed == _digest(
        {k: v for k, v in value.items() if k != "receipt_sha256"}
    )


def _diff(old: Any, new: Any, prefix: str = "") -> list[dict[str, Any]]:
    if isinstance(old, dict) and isinstance(new, dict):
        rows: list[dict[str, Any]] = []
        for key in sorted(set(old) | set(new)):
            path = f"{prefix}.{key}" if prefix else str(key)
            if key not in old:
                rows.append({"path": path, "old": None, "new": new[key]})
            elif key not in new:
                rows.append({"path": path, "old": old[key], "new": None})
            else:
                rows.extend(_diff(old[key], new[key], path))
        return rows
    return [] if old == new else [{"path": prefix, "old": old, "new": new}]


def _projection(value: Any, prefix: str = "") -> Any:
    if prefix in ALLOWED_INFRASTRUCTURE_PATHS:
        return "__INFRASTRUCTURE_FIELD__"
    if isinstance(value, dict):
        return {
            key: _projection(row, f"{prefix}.{key}" if prefix else str(key))
            for key, row in sorted(value.items())
        }
    return value


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    r43 = _load(R43)
    v1 = _load(V1_MANIFEST)
    auth1 = _load(V1_AUTHORITY)
    q5 = _load(Q5_PASS)
    transfer = _load(TRANSFER_REPAIR)
    if not all(_valid_receipt(row) for row in (r43, v1, auth1, q5, transfer)):
        raise ValueError("parent-receipt-invalid")
    if v1.get("status") != EXPECTED_MANIFEST_STATUS or auth1.get("status") != EXPECTED_AUTHORITY_STATUS:
        raise ValueError("parent-status-drift")
    if q5.get("status") != "HOST_MIGRATION_EQUIVALENCE_PASS" or q5.get("all_q1_q5a_pass") is not True:
        raise ValueError("q5v2-not-pass")
    accounting = q5.get("access_accounting") or {}
    for key in ("scientific_source_units_executed", "validation_units_initialized", "confirmatory_treatment_outcomes_observed"):
        if int(accounting.get(key) or 0) != 0:
            raise ValueError("preexposure-gate-violated:" + key)
    if _sha(SERVER) != EXPECTED_SERVER_SHA256:
        raise ValueError("replacement-loopback-server-drift")

    old_adapter = ((v1.get("execution_manifest") or {}).get("external_runtime_adapter") or {})
    if old_adapter.get("loopback_server_sha256") != EXPECTED_V1_SERVER_SHA256:
        raise ValueError("v1-loopback-binding-not-as-expected")

    repair: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R45M1-LOOPBACK-BINDING-REPAIR-20260901",
        "recorded_date": "2026-09-01",
        "status": "PREEXPOSURE_INFRASTRUCTURE_BINDING_REPAIR_PASS",
        "role": "VERSIONED_INFRASTRUCTURE_ONLY_LOOPBACK_BINDING_CORRECTION",
        "problem": {
            "v1_manifest_bound_loopback_server_path": old_adapter.get("loopback_server_path"),
            "v1_manifest_bound_loopback_server_sha256": old_adapter.get("loopback_server_sha256"),
            "qualified_host_231_loopback_server_path": "research_pipeline/failure_memory_memrl_local_openai_server_r45m1.py",
            "qualified_host_231_loopback_server_sha256": EXPECTED_SERVER_SHA256,
            "classification": "execution-artifact binding mismatch discovered before source exposure",
        },
        "scientific_boundary": {
            "model_ids_changed": False,
            "model_bytes_changed": False,
            "embedding_bytes_changed": False,
            "temperature_changed": False,
            "max_tokens_changed": False,
            "prompt_changed": False,
            "parser_changed": False,
            "retrieval_changed": False,
            "arm_semantics_changed": False,
            "selected_units_changed": False,
        },
        "preexposure_accounting": {
            "scientific_source_units_executed": 0,
            "validation_units_opened": 0,
            "confirmatory_outcomes_observed": 0,
            "partial_effect_inspected": False,
        },
        "parents": {
            "v1_manifest_sha256": _sha(V1_MANIFEST),
            "v1_authority_sha256": _sha(V1_AUTHORITY),
            "q5v2_pass_sha256": _sha(Q5_PASS),
            "transfer_repair_sha256": _sha(TRANSFER_REPAIR),
        },
    }
    repair["receipt_sha256"] = _digest(repair)

    manifest2 = copy.deepcopy(v1)
    manifest2["receipt_id"] = "D2-FAILURE-MEMORY-PROVENANCE-R45M1-HOST-MIGRATION-EXECUTION-MANIFEST-V2"
    manifest2.setdefault("parent_bindings", {})["loopback_binding_repair"] = {
        "path": str(REPAIR_OUT.relative_to(PROJECT_ROOT)),
        "receipt_sha256": repair["receipt_sha256"],
    }
    adapter2 = manifest2["execution_manifest"]["external_runtime_adapter"]
    adapter2["loopback_server_path"] = "research_pipeline/failure_memory_memrl_local_openai_server_r45m1.py"
    adapter2["loopback_server_sha256"] = EXPECTED_SERVER_SHA256
    manifest2["authority"] = {"execution": False, "scientific_claim_change": False, "external_provider_spend": False}
    manifest2.pop("receipt_sha256", None)
    manifest2["receipt_sha256"] = _digest(manifest2)

    original = r43.get("execution_manifest") or {}
    replacement = manifest2.get("execution_manifest") or {}
    differences = _diff(original, replacement)
    non_whitelisted = [row for row in differences if row["path"] not in ALLOWED_INFRASTRUCTURE_PATHS]
    old_proj = _projection(original)
    new_proj = _projection(replacement)
    diff: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R45M1-OLD-R43-VS-REPLACEMENT-MANIFEST-V2-DIFF",
        "recorded_date": "2026-09-01",
        "status": "PASS" if not non_whitelisted and old_proj == new_proj else "STOP_SCIENTIFIC_PROTOCOL_DRIFT",
        "allowed_infrastructure_paths": sorted(ALLOWED_INFRASTRUCTURE_PATHS),
        "differences": differences,
        "non_whitelisted_scientific_differences": non_whitelisted,
        "non_whitelisted_scientific_difference_count": len(non_whitelisted),
        "old_scientific_projection_sha256": _digest(old_proj),
        "replacement_scientific_projection_sha256": _digest(new_proj),
        "scientific_projection_byte_identical": old_proj == new_proj,
        "confirmatory_outcomes_observed": 0,
    }
    diff["receipt_sha256"] = _digest(diff)
    if diff["status"] != "PASS":
        raise ValueError("STOP_SCIENTIFIC_PROTOCOL_DRIFT")

    auth2 = copy.deepcopy(auth1)
    auth2["receipt_id"] = "D2-FAILURE-MEMORY-PROVENANCE-R45M1-REPLACEMENT-EXECUTION-AUTHORITY-V2"
    auth2.setdefault("bindings", {})["parent_authority_v1"] = {
        "path": str(V1_AUTHORITY.relative_to(PROJECT_ROOT)),
        "sha256": _sha(V1_AUTHORITY),
        "receipt_sha256": auth1.get("receipt_sha256"),
    }
    auth2["bindings"]["loopback_binding_repair"] = {
        "path": str(REPAIR_OUT.relative_to(PROJECT_ROOT)),
        "receipt_sha256": repair["receipt_sha256"],
    }
    auth2["bindings"]["migration_manifest"] = {
        "path": str(MANIFEST_V2_OUT.relative_to(PROJECT_ROOT)),
        "sha256": "__FILLED_AFTER_MANIFEST_WRITE__",
        "receipt_sha256": manifest2["receipt_sha256"],
    }
    auth2["pre_authority_accounting"] = {
        "scientific_source_units_executed": 0,
        "validation_units_opened": 0,
        "confirmatory_outcomes_observed": 0,
        "partial_effect_inspected": False,
    }
    auth2.pop("receipt_sha256", None)
    return repair, manifest2, diff, auth2


def write_all() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    repair, manifest2, diff, auth2 = build()
    REPAIR_OUT.write_text(json.dumps(repair, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST_V2_OUT.write_text(json.dumps(manifest2, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DIFF_OUT.write_text(json.dumps(diff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    auth2["bindings"]["migration_manifest"]["sha256"] = _sha(MANIFEST_V2_OUT)
    auth2["receipt_sha256"] = _digest(auth2)
    AUTHORITY_V2_OUT.write_text(json.dumps(auth2, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return repair, manifest2, diff, auth2


def validate_outputs() -> list[str]:
    errors: list[str] = []
    for path in (REPAIR_OUT, MANIFEST_V2_OUT, DIFF_OUT, AUTHORITY_V2_OUT):
        if not path.is_file():
            errors.append("missing:" + path.name)
            continue
        row = _load(path)
        if not _valid_receipt(row):
            errors.append("receipt:" + path.name)
    if errors:
        return errors
    manifest2 = _load(MANIFEST_V2_OUT)
    auth2 = _load(AUTHORITY_V2_OUT)
    diff = _load(DIFF_OUT)
    adapter = manifest2["execution_manifest"]["external_runtime_adapter"]
    if adapter.get("loopback_server_sha256") != EXPECTED_SERVER_SHA256:
        errors.append("loopback-sha")
    if adapter.get("loopback_server_path") != "research_pipeline/failure_memory_memrl_local_openai_server_r45m1.py":
        errors.append("loopback-path")
    if diff.get("status") != "PASS" or diff.get("scientific_projection_byte_identical") is not True:
        errors.append("diff")
    if int(diff.get("non_whitelisted_scientific_difference_count", -1)) != 0:
        errors.append("scientific-diff")
    binding = (auth2.get("bindings") or {}).get("migration_manifest") or {}
    if binding.get("sha256") != _sha(MANIFEST_V2_OUT) or binding.get("receipt_sha256") != manifest2.get("receipt_sha256"):
        errors.append("authority-binding")
    return errors


if __name__ == "__main__":
    repair, manifest2, diff, auth2 = write_all()
    errors = validate_outputs()
    if errors:
        raise SystemExit("invalid loopback binding repair:" + ";".join(errors))
    print(json.dumps({
        "status": repair["status"],
        "manifest_receipt_sha256": manifest2["receipt_sha256"],
        "diff_receipt_sha256": diff["receipt_sha256"],
        "authority_receipt_sha256": auth2["receipt_sha256"],
        "scientific_projection_byte_identical": diff["scientific_projection_byte_identical"],
        "non_whitelisted_scientific_difference_count": diff["non_whitelisted_scientific_difference_count"],
    }, sort_keys=True))
