from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

SCHEMA_VERSION = "1.0-recovered-relation-boundary"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "relation-scan-boundary-manifest.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "relation-scan-boundary-manifest.js"
DEFAULT_RELATION = PROJECT_ROOT / "generated" / "paper-first-global-relation-recall.json"
POLICY = {
    "manifest_is_scheduler_provenance_not_scientific_evidence": True,
    "archived_receipts_only_recover_the_historical_scan_boundary": True,
    "boundary_recovery_cannot_change_historical_relation_results": True,
    "boundary_recovery_cannot_authorize_provider_calls_or_downstream_research": True,
}
AUTHORITY = {
    key: False
    for key in (
        "claim_mutation",
        "scientific_closure",
        "relation_result_mutation",
        "provider_calls",
        "problem_gate",
        "method",
        "experiment",
        "p0",
        "gpu",
    )
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object-required:{path.name}")
    return value


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _content_sha256(value: Any) -> str:
    material = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(material).hexdigest()


def _receipts(generator: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    source = ((generator.get("saturation_memory") or {}).get("portable_review_receipts") or [])
    for row in source:
        if not isinstance(row, dict) or row.get("scientific_authority") is not False:
            continue
        refs = sorted(
            {
                str(ref).strip()
                for ref in row.get("source_refs") or []
                if str(ref).strip().startswith("arXiv:")
            }
        )
        run_id = str(row.get("run_id") or "").strip()
        if run_id and len(refs) >= 2:
            receipt = {
                "run_id": run_id,
                "source_refs": refs,
                "scientific_authority": False,
            }
            receipt["receipt_sha256"] = _content_sha256(receipt)
            result.append(receipt)
    return result


def _source_refs(receipts: list[dict[str, Any]]) -> list[str]:
    return sorted({ref for row in receipts for ref in row.get("source_refs") or []})


def _pairs(receipts: list[dict[str, Any]]) -> set[tuple[str, str]]:
    result: set[tuple[str, str]] = set()
    for row in receipts:
        result.update(combinations(sorted(set(row.get("source_refs") or [])), 2))
    return result


def source_universe_digest(receipts: list[dict[str, Any]]) -> str:
    return hashlib.sha256(
        json.dumps(_source_refs(receipts), ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


def relation_universe_digest(receipts: list[dict[str, Any]]) -> str:
    material = {
        "source_refs": _source_refs(receipts),
        "coobserved_source_pairs": [list(pair) for pair in sorted(_pairs(receipts))],
    }
    return hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_relation_scan_boundary_manifest(
    *,
    archived_generator_path: Path,
    relation_path: Path = DEFAULT_RELATION,
) -> dict[str, Any]:
    generator = _load(archived_generator_path)
    relation = _load(relation_path)
    receipts = _receipts(generator)
    last = relation.get("last_completed_scan") or {}
    coverage = last.get("relation_coverage") or relation.get("relation_coverage") or {}
    relation_digest = relation_universe_digest(receipts)
    expected_digest = str(last.get("relation_universe_digest") or "")
    source_refs = _source_refs(receipts)
    pairs = _pairs(receipts)
    if relation_digest != expected_digest:
        raise ValueError("archived-generator-does-not-replay-relation-boundary")
    if int(coverage.get("reviewed_receipt_sources") or 0) != len(source_refs):
        raise ValueError("archived-source-count-mismatch")
    if int(coverage.get("coobserved_source_pairs") or 0) != len(pairs):
        raise ValueError("archived-pair-count-mismatch")
    state = {
        "schema_version": SCHEMA_VERSION,
        "status": "RELATION_SCAN_BOUNDARY_RECOVERED",
        "policy": dict(POLICY),
        "scan_binding": {
            "scan_run_id": str(last.get("run_id") or ""),
            "relation_universe_digest": relation_digest,
            "source_universe_digest": source_universe_digest(receipts),
            "relation_raw_sha256": str(
                (((relation.get("raw_artifacts") or {}).get("relation") or {}).get("sha256") or "")
            ),
            "receipt_runs": len(receipts),
            "reviewed_sources": len(source_refs),
            "coobserved_source_pairs": len(pairs),
            "archived_generator_state_sha256": _file_sha256(archived_generator_path),
            "relation_state_sha256": _file_sha256(relation_path),
        },
        "portable_review_receipts": receipts,
        "scientific_authority": False,
        "authority": dict(AUTHORITY),
    }
    state["manifest_content_sha256"] = _content_sha256(
        {key: value for key, value in state.items() if key != "manifest_content_sha256"}
    )
    errors = validate_relation_scan_boundary_manifest(state)
    if errors:
        raise ValueError("invalid-relation-boundary-manifest:" + ";".join(errors))
    return state


def validate_relation_scan_boundary_manifest(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    binding = state.get("scan_binding") or {}
    receipts = state.get("portable_review_receipts") or []
    if (
        state.get("status") != "RELATION_SCAN_BOUNDARY_RECOVERED"
        or state.get("scientific_authority") is not False
    ):
        errors.append("status-or-authority")
    if any((state.get("authority") or {}).get(key) is not False for key in AUTHORITY):
        errors.append("authority-leak")
    if any(
        not isinstance(row, dict)
        or row.get("scientific_authority") is not False
        or row.get("source_refs") != sorted(set(row.get("source_refs") or []))
        or any(not str(ref).startswith("arXiv:") for ref in row.get("source_refs") or [])
        for row in receipts
    ):
        errors.append("invalid-receipt")
    if relation_universe_digest(receipts) != binding.get("relation_universe_digest"):
        errors.append("relation-digest-mismatch")
    if source_universe_digest(receipts) != binding.get("source_universe_digest"):
        errors.append("source-digest-mismatch")
    if len(receipts) != int(binding.get("receipt_runs") or 0):
        errors.append("receipt-count-mismatch")
    if len(_source_refs(receipts)) != int(binding.get("reviewed_sources") or 0):
        errors.append("source-count-mismatch")
    if len(_pairs(receipts)) != int(binding.get("coobserved_source_pairs") or 0):
        errors.append("pair-count-mismatch")
    expected = _content_sha256(
        {key: value for key, value in state.items() if key != "manifest_content_sha256"}
    )
    if state.get("manifest_content_sha256") != expected:
        errors.append("content-hash-mismatch")
    return errors


def load_relation_scan_boundary_manifest(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    if not path.is_file():
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "RELATION_SCAN_BOUNDARY_MISSING",
            "policy": dict(POLICY),
            "scientific_authority": False,
            "authority": dict(AUTHORITY),
        }
    try:
        state = _load(path)
    except (OSError, ValueError, json.JSONDecodeError):
        state = {}
    errors = validate_relation_scan_boundary_manifest(state)
    if not errors:
        return state
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "RELATION_SCAN_BOUNDARY_INVALID",
        "errors": errors,
        "policy": dict(POLICY),
        "scientific_authority": False,
        "authority": dict(AUTHORITY),
    }


def boundary_receipts(
    manifest: dict[str, Any],
    relation_state: dict[str, Any],
) -> list[dict[str, Any]]:
    if validate_relation_scan_boundary_manifest(manifest):
        return []
    binding = manifest.get("scan_binding") or {}
    last = relation_state.get("last_completed_scan") or {}
    if (
        binding.get("scan_run_id") != last.get("run_id")
        or binding.get("relation_universe_digest") != last.get("relation_universe_digest")
    ):
        return []
    return list(manifest.get("portable_review_receipts") or [])


def write_relation_scan_boundary_manifest(
    *,
    archived_generator_path: Path,
    relation_path: Path = DEFAULT_RELATION,
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
) -> dict[str, Any]:
    state = build_relation_scan_boundary_manifest(
        archived_generator_path=archived_generator_path,
        relation_path=relation_path,
    )
    json_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    js_path.write_text(
        "window.RELATION_SCAN_BOUNDARY_MANIFEST = "
        + json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    return state


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--archived-generator", type=Path, required=True)
    parser.add_argument("--relation", type=Path, default=DEFAULT_RELATION)
    args = parser.parse_args()
    written = write_relation_scan_boundary_manifest(
        archived_generator_path=args.archived_generator,
        relation_path=args.relation,
    )
    print(json.dumps(written["scan_binding"], ensure_ascii=False, indent=2))
