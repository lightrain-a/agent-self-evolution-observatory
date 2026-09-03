"""Build and validate the R45-M1 infrastructure-only child of frozen R43."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .failure_memory_memrl_old_r45_abandonment_r45m1 import (
    OUT as ABANDONMENT,
    validate as validate_abandonment,
    verify_frozen_evidence,
)

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
R43 = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r43-memrl-g8-execution-manifest.json"
OUT = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r45m1-host-migration-execution-manifest.json"
DIFF_OUT = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r45m1-old-r43-vs-replacement-manifest-diff.json"

EXPECTED_INFRA_STATUS = "R45M1_INFRASTRUCTURE_QUALIFIED_ZERO_OUTCOME"
STATUS = "MEMRL_R45M1_INFRASTRUCTURE_ONLY_REPLACEMENT_MANIFEST_FROZEN_ZERO_CONFIRMATORY_OUTCOMES"

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
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object:{path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _receipt_valid(value: dict[str, Any]) -> bool:
    observed = value.get("receipt_sha256")
    return isinstance(observed, str) and observed == _digest(
        {key: row for key, row in value.items() if key != "receipt_sha256"}
    )


def _set_path(value: dict[str, Any], dotted: str, new: Any) -> None:
    parts = dotted.split(".")
    current: dict[str, Any] = value
    for part in parts[:-1]:
        child = current.get(part)
        if not isinstance(child, dict):
            raise ValueError(f"missing manifest path:{dotted}")
        current = child
    if parts[-1] not in current:
        raise ValueError(f"missing manifest path:{dotted}")
    current[parts[-1]] = new


def diff_leaves(old: Any, new: Any, prefix: str = "") -> list[dict[str, Any]]:
    if isinstance(old, dict) and isinstance(new, dict):
        rows: list[dict[str, Any]] = []
        for key in sorted(set(old) | set(new)):
            path = f"{prefix}.{key}" if prefix else str(key)
            if key not in old:
                rows.append({"path": path, "old": None, "new": new[key]})
            elif key not in new:
                rows.append({"path": path, "old": old[key], "new": None})
            else:
                rows.extend(diff_leaves(old[key], new[key], path))
        return rows
    if old != new:
        return [{"path": prefix, "old": old, "new": new}]
    return []


def _scientific_projection(value: Any, prefix: str = "") -> Any:
    if prefix in ALLOWED_INFRASTRUCTURE_PATHS:
        return "__INFRASTRUCTURE_FIELD__"
    if isinstance(value, dict):
        return {
            key: _scientific_projection(row, f"{prefix}.{key}" if prefix else str(key))
            for key, row in sorted(value.items())
        }
    return value


def apply_infrastructure(r43_execution: dict[str, Any], infrastructure: dict[str, Any]) -> dict[str, Any]:
    execution = copy.deepcopy(r43_execution)
    host = infrastructure.get("host") or {}
    runtime = infrastructure.get("python_runtime") or {}
    models = infrastructure.get("models") or {}
    image = infrastructure.get("docker") or {}
    source = infrastructure.get("source") or {}
    replacements = {
        "host.logical_name": host.get("logical_name"),
        "host.ssh_identity": host.get("ssh_identity"),
        "host.gpu_assignment.llm": (host.get("gpu_assignment") or {}).get("llm"),
        "host.gpu_assignment.embedding": (host.get("gpu_assignment") or {}).get("embedding"),
        "host.gpu_assignment.environment": (host.get("gpu_assignment") or {}).get("environment"),
        "host.python": runtime.get("python"),
        "host.pythonpath": runtime.get("pythonpath"),
        "host.runtime_tree_sha256": runtime.get("tree_sha256"),
        "host.runtime_manifest_sha256": runtime.get("manifest_sha256"),
        "host.runtime_manifest_file_sha256": runtime.get("manifest_file_sha256"),
        "source.checkout": source.get("checkout"),
        "models.llm.root": (models.get("llm") or {}).get("root"),
        "models.llm.device": (models.get("llm") or {}).get("device"),
        "models.embedding.root": (models.get("embedding") or {}).get("root"),
        "models.embedding.device": (models.get("embedding") or {}).get("device"),
        "runtime_image.qualified_tag": image.get("qualified_tag"),
        "runtime_image.execution_tag": image.get("execution_tag"),
        "runtime_image.id": image.get("id"),
        "runtime_image.execution_tag_same_content_identity": image.get("same_content_identity"),
    }
    missing = sorted(path for path, value in replacements.items() if value is None)
    if missing:
        raise ValueError("infrastructure-evidence-missing:" + ",".join(missing))
    for path, value in replacements.items():
        _set_path(execution, path, value)
    return execution


def audit(r43_execution: dict[str, Any], replacement: dict[str, Any]) -> dict[str, Any]:
    differences = diff_leaves(r43_execution, replacement)
    non_whitelisted = [
        row for row in differences if row["path"] not in ALLOWED_INFRASTRUCTURE_PATHS
    ]
    old_projection = _scientific_projection(r43_execution)
    new_projection = _scientific_projection(replacement)
    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R45M1-OLD-R43-VS-REPLACEMENT-MANIFEST-DIFF",
        "recorded_date": "2026-09-01",
        "status": "PASS" if not non_whitelisted else "STOP_SCIENTIFIC_PROTOCOL_DRIFT",
        "allowed_infrastructure_paths": sorted(ALLOWED_INFRASTRUCTURE_PATHS),
        "differences": differences,
        "non_whitelisted_scientific_differences": non_whitelisted,
        "non_whitelisted_scientific_difference_count": len(non_whitelisted),
        "old_scientific_projection_sha256": _digest(old_projection),
        "replacement_scientific_projection_sha256": _digest(new_projection),
        "scientific_projection_byte_identical": old_projection == new_projection,
        "confirmatory_outcomes_observed": 0,
    }


def build(infrastructure: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    frozen = verify_frozen_evidence()
    r43 = frozen["r43"]
    abandonment = _load(ABANDONMENT)
    if validate_abandonment(abandonment) or not _receipt_valid(abandonment):
        raise ValueError("old-r45-abandonment-invalid")
    if infrastructure.get("status") != EXPECTED_INFRA_STATUS or not _receipt_valid(infrastructure):
        raise ValueError("replacement-infrastructure-not-qualified")
    if int(infrastructure.get("confirmatory_outcomes_observed") or 0) != 0:
        raise ValueError("pre-manifest-confirmatory-outcome-leak")

    original = r43.get("execution_manifest") or {}
    replacement = apply_infrastructure(original, infrastructure)
    diff = audit(original, replacement)
    if (
        diff["non_whitelisted_scientific_difference_count"] != 0
        or diff["scientific_projection_byte_identical"] is not True
    ):
        raise ValueError("STOP_SCIENTIFIC_PROTOCOL_DRIFT")
    diff["receipt_sha256"] = _digest(diff)

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R45M1-HOST-MIGRATION-EXECUTION-MANIFEST",
        "recorded_date": "2026-09-01",
        "role": "INFRASTRUCTURE_ONLY_CHILD_OF_R43",
        "status": STATUS,
        "lineage": {
            "old_r45": "PERMANENTLY_QUARANTINED_UNKNOWN_REMOTE_STATE",
            "replacement": "R45-M1",
            "resume_of_old_r45": False,
            "attempt_count": 1,
        },
        "parent_bindings": {
            "r43": {
                "path": str(R43.relative_to(PROJECT_ROOT)),
                "sha256": _sha(R43),
                "receipt_sha256": r43.get("receipt_sha256"),
            },
            "old_r45_abandonment": {
                "path": str(ABANDONMENT.relative_to(PROJECT_ROOT)),
                "sha256": _sha(ABANDONMENT),
                "receipt_sha256": abandonment.get("receipt_sha256"),
            },
            "infrastructure_qualification": {
                "receipt_sha256": infrastructure.get("receipt_sha256"),
                "bindings": infrastructure.get("bindings"),
            },
            "diff_audit": {
                "path": str(DIFF_OUT.relative_to(PROJECT_ROOT)),
                "receipt_sha256": diff.get("receipt_sha256"),
            },
        },
        "execution_manifest": replacement,
        "replacement_infrastructure": {
            "output_paths": infrastructure.get("output_paths"),
            "gpu_uuid": (infrastructure.get("host") or {}).get("gpu_uuid"),
            "source_archive_sha256": (infrastructure.get("source") or {}).get("archive_sha256"),
            "zero_outcome_equivalence_receipt_sha256": (
                (infrastructure.get("cross_host_equivalence") or {}).get("receipt_sha256")
            ),
        },
        "scientific_inheritance": {
            "parent": "R43",
            "all_non_infrastructure_fields_byte_identical": True,
            "non_whitelisted_scientific_differences": 0,
            "scientific_projection_sha256": diff["replacement_scientific_projection_sha256"],
        },
        "confirmatory_outcomes_observed": 0,
        "authority": {
            "execution": False,
            "scientific_claim_change": False,
            "external_provider_spend": False,
        },
    }
    payload["receipt_sha256"] = _digest(payload)
    return payload, diff


def validate(payload: dict[str, Any], diff: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("status") != STATUS:
        errors.append("status")
    lineage = payload.get("lineage") or {}
    if lineage.get("replacement") != "R45-M1" or lineage.get("resume_of_old_r45") is not False:
        errors.append("lineage")
    inherited = payload.get("scientific_inheritance") or {}
    if inherited.get("all_non_infrastructure_fields_byte_identical") is not True:
        errors.append("scientific-inheritance")
    if int(inherited.get("non_whitelisted_scientific_differences") or 0) != 0:
        errors.append("scientific-diff")
    if diff.get("status") != "PASS" or int(diff.get("non_whitelisted_scientific_difference_count") or 0) != 0:
        errors.append("diff-audit")
    if diff.get("scientific_projection_byte_identical") is not True:
        errors.append("scientific-projection")
    if not _receipt_valid(diff):
        errors.append("diff-receipt-hash")
    if not _receipt_valid(payload):
        errors.append("manifest-receipt-hash")
    return errors


def write(infrastructure_path: Path, manifest_path: Path = OUT, diff_path: Path = DIFF_OUT) -> dict[str, Any]:
    infrastructure = _load(infrastructure_path)
    payload, diff = build(infrastructure)
    diff_path.write_text(json.dumps(diff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    errors = validate(payload, diff)
    if errors:
        raise ValueError("invalid R45-M1 migration manifest:" + ";".join(errors))
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--infrastructure", type=Path, required=True)
    args = parser.parse_args()
    row = write(args.infrastructure.resolve())
    print(json.dumps({
        "status": row["status"],
        "receipt_sha256": row["receipt_sha256"],
        "non_whitelisted_scientific_differences": row["scientific_inheritance"]["non_whitelisted_scientific_differences"],
        "confirmatory_outcomes_observed": row["confirmatory_outcomes_observed"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
