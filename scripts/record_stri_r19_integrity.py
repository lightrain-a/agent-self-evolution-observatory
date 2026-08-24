#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.config import StorageSettings, resolve_experiment_data_root
from research_pipeline.paper_acceptance_ledger import load_paper_ledger, record_post_draft_integrity, validate_paper_ledger
from scripts.publish_stri_r19_projection import contract_from_ledger, selective_projection

PID = "STRI-ICLR2027"
MANIFEST = ROOT / "generated/asset-first-stri-r19-manuscript-integrity-manifest-20260824.json"
WRAPPED_RECEIPT = ROOT / "generated/asset-first-stri-r19-manuscript-integrity-receipt-20260824.json"
BODY = ROOT / "paper_drafts/stri-20260816-narrow-body.tex"
SOURCE_ZIP = ROOT / "downloads/STRI-ICLR2027-source.zip"
OUTPUT = ROOT / "generated/asset-first-stri-r19-post-draft-integrity-projection-20260824.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object: {path}")
    return value


def row_hashes(path: Path, *, registry: bool) -> dict[str, str]:
    payload = load(path)
    rows = payload.get("papers") or [] if registry else (((payload.get("paper_acceptance") or {}).get("ledger_index") or {}).get("entries") or [])
    out: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        pid = str(row.get("paper_id") or "")
        if not pid or pid in {"STRI", PID}:
            continue
        raw = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        out[pid] = hashlib.sha256(raw).hexdigest()
    return out


def verify_source_binding() -> None:
    if not SOURCE_ZIP.is_file():
        raise RuntimeError("R19 source ZIP missing")
    with zipfile.ZipFile(SOURCE_ZIP) as zf:
        packaged = zf.read(BODY.name)
    if packaged != BODY.read_bytes():
        raise RuntimeError("R19 stable source ZIP manuscript body does not match integrity-audited body")


def main() -> None:
    manifest = load(MANIFEST)
    wrapped = load(WRAPPED_RECEIPT)
    inner = wrapped.get("receipt") or {}
    audit = wrapped.get("audit") or {}
    if wrapped.get("manifest_sha256") != sha(MANIFEST):
        raise RuntimeError("integrity manifest digest drift")
    if audit.get("status") != "PASS_POST_DRAFT_INTEGRITY" or audit.get("pass") is not True:
        raise RuntimeError("STRI post-draft integrity audit is not PASS")
    if any(inner.get(key) is not False for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        raise RuntimeError("integrity receipt authority drift")
    verify_source_binding()

    registry_before = row_hashes(ROOT / "generated/paper-registry.json", registry=True)
    system_before = row_hashes(ROOT / "generated/research-system-state.json", registry=False)
    root = resolve_experiment_data_root(StorageSettings.from_env())
    before = load_paper_ledger(root, PID)
    if before.get("current_state") != "SUBMISSION_READY" or before.get("scientific_status") != "READY":
        raise RuntimeError("R19 live STRI ledger is not SUBMISSION_READY/READY")
    target_sha = str(inner.get("receipt_sha256") or "")
    existing = [
        event for event in (before.get("events") or [])
        if isinstance(event, dict)
        and event.get("event_type") == "post-draft-integrity"
        and str((event.get("receipt") or {}).get("receipt_sha256") or "") == target_sha
    ]
    if existing:
        after = before
        appended = False
    else:
        contract = contract_from_ledger(before)
        after = record_post_draft_integrity(
            root, contract, manifest, project_root=ROOT,
            actor="stri-r19-post-draft-integrity",
        )
        appended = True
    errors = validate_paper_ledger(after)
    if errors:
        raise RuntimeError("R19 ledger invalid after integrity receipt: " + "; ".join(errors))
    latest = [event for event in after.get("events") or [] if isinstance(event, dict) and event.get("event_type") == "post-draft-integrity"][-1]
    if str((latest.get("receipt") or {}).get("receipt_sha256") or "") != target_sha:
        raise RuntimeError("latest integrity receipt is not the audited R19 receipt")

    projection = selective_projection(root)
    registry_after = row_hashes(ROOT / "generated/paper-registry.json", registry=True)
    system_after = row_hashes(ROOT / "generated/research-system-state.json", registry=False)
    if registry_after != registry_before:
        raise RuntimeError("non-STRI PaperRegistry rows changed during integrity projection")
    if system_after != system_before:
        raise RuntimeError("non-STRI PaperAcceptance rows changed during integrity projection")

    receipt = {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "acceptance_paper_id": PID,
        "revision": "R19-post-draft-integrity",
        "status": "PASS_POST_DRAFT_INTEGRITY_RECORDED",
        "audit_scope": manifest.get("audit_scope"),
        "manifest_ref": str(MANIFEST.relative_to(ROOT)),
        "manifest_sha256": sha(MANIFEST),
        "integrity_receipt_ref": str(WRAPPED_RECEIPT.relative_to(ROOT)),
        "integrity_receipt_file_sha256": sha(WRAPPED_RECEIPT),
        "integrity_receipt_sha256": target_sha,
        "ledger_event_appended": appended,
        "post_draft_integrity_receipts": int((after.get("summary") or {}).get("post_draft_integrity_receipts") or 0),
        "ledger_valid": True,
        "source_zip_body_binding": "PASS",
        "public_status": (projection.get("public_status") or {}).get("status"),
        "gate_clean_submission_ready": (projection.get("live") or {}).get("gate_clean_submission_ready"),
        "other_paper_registry_rows_preserved": True,
        "other_paper_acceptance_rows_preserved": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    identity = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    receipt["receipt_sha256"] = hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    OUTPUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
