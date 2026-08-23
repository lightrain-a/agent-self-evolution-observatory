from __future__ import annotations

import hashlib
import json
import os
import re
import zipfile
from pathlib import Path
from typing import Any, Mapping

from .paper_anonymity_audit import audit_double_blind_bundle, validate_anonymity_audit_receipt

SCHEMA_VERSION = "1.0"
STATUS = "PASS_VENUE_COMPLIANCE_SOURCE_PROJECTION_REQUIRES_REFREEZE"
AI_SECTION_RE = re.compile(
    r"\\(?:sub)*section\*?\s*\{\s*(?:AI\s*[- ]?Use(?:\s+Statement|\s+Disclosure)?|Artificial\s+Intelligence\s+Use(?:\s+Statement|\s+Disclosure)?)\s*\}",
    flags=re.I,
)


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def projection_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: receipt.get(key) for key in (
        "paper_id",
        "source_filename",
        "source_sha256",
        "projected_filename",
        "projected_sha256",
        "main_tex_entry",
        "statement_entry",
        "statement_sha256",
        "changed_entries",
        "anonymity_audit_sha256",
        "status",
    )}


def add_ai_use_statement_projection(
    *,
    paper_id: str,
    source_zip: Path,
    output_zip: Path,
    statement_text: str,
    main_tex_entry: str = "main.tex",
    statement_entry: str = "sections/08_ai_use_statement.tex",
) -> dict[str, Any]:
    source_zip = Path(source_zip).resolve()
    output_zip = Path(output_zip).resolve()
    if not paper_id.strip():
        raise RuntimeError("paper id required")
    if not source_zip.is_file() or not zipfile.is_zipfile(source_zip):
        raise RuntimeError("source submission artifact must be a valid ZIP")
    if output_zip == source_zip:
        raise RuntimeError("venue compliance projection must not overwrite the sealed source ZIP")
    statement = statement_text.strip()
    if not statement or not AI_SECTION_RE.search(statement):
        raise RuntimeError("statement text must contain an explicit AI Use section heading")
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    temp_zip = output_zip.with_name(output_zip.name + ".tmp")
    if temp_zip.exists():
        temp_zip.unlink()
    with zipfile.ZipFile(source_zip, "r") as src:
        infos = [info for info in src.infolist() if not info.is_dir()]
        names = {info.filename for info in infos}
        if main_tex_entry not in names:
            raise RuntimeError(f"main TeX entry missing: {main_tex_entry}")
        if statement_entry in names:
            raise RuntimeError(f"statement entry already exists: {statement_entry}")
        source_rows = {info.filename: src.read(info) for info in infos}
        text_rows = [data.decode("utf-8", errors="ignore") for name, data in source_rows.items() if name.lower().endswith(".tex")]
        if any(AI_SECTION_RE.search(text) for text in text_rows):
            raise RuntimeError("source already contains an AI Use section; refusing duplicate projection")
        main_data = source_rows[main_tex_entry]
        main_text = main_data.decode("utf-8", errors="strict")
        matches = list(re.finditer(r"(?m)^\\bibliography\s*\{", main_text))
        if len(matches) != 1:
            raise RuntimeError("main TeX must contain exactly one line-leading \\bibliography marker")
        insert = f"\\input{{{Path(statement_entry).with_suffix('').as_posix()}}}\n"
        projected_main = (main_text[:matches[0].start()] + insert + main_text[matches[0].start():]).encode("utf-8")
        projected_statement = (statement + "\n").encode("utf-8")
        changed_entries = [
            {
                "entry": main_tex_entry,
                "change": "INSERT_AI_USE_INPUT_BEFORE_BIBLIOGRAPHY",
                "original_sha256": _sha_bytes(main_data),
                "projected_sha256": _sha_bytes(projected_main),
            },
            {
                "entry": statement_entry,
                "change": "ADD_AI_USE_STATEMENT",
                "original_sha256": "",
                "projected_sha256": _sha_bytes(projected_statement),
            },
        ]
        projection_manifest = {
            "schema_version": SCHEMA_VERSION,
            "projection_type": "VENUE_COMPLIANCE_AI_USE_STATEMENT_PROJECTION",
            "paper_id": paper_id,
            "source_filename": source_zip.name,
            "source_sha256": _sha_file(source_zip),
            "main_tex_entry": main_tex_entry,
            "statement_entry": statement_entry,
            "statement_sha256": _sha_bytes(projected_statement),
            "changed_entries": changed_entries,
            "canonical_scientific_artifacts_unchanged": True,
            "scientific_claims_unchanged": True,
            "experiment_evidence_unchanged": True,
            "requires_new_submission_freeze": True,
            "automatic_refreeze_forbidden": True,
        }
        projection_manifest["manifest_sha256"] = _digest(projection_manifest)
        try:
            with zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as dst:
                for info in sorted(infos, key=lambda row: row.filename):
                    data = projected_main if info.filename == main_tex_entry else source_rows[info.filename]
                    zi = zipfile.ZipInfo(info.filename, date_time=(1980, 1, 1, 0, 0, 0))
                    zi.compress_type = zipfile.ZIP_DEFLATED
                    zi.external_attr = info.external_attr
                    dst.writestr(zi, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
                zi = zipfile.ZipInfo(statement_entry, date_time=(1980, 1, 1, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED
                zi.external_attr = 0o100644 << 16
                dst.writestr(zi, projected_statement, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
                zi = zipfile.ZipInfo("venue-compliance-projection.json", date_time=(1980, 1, 1, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED
                zi.external_attr = 0o100644 << 16
                dst.writestr(zi, json.dumps(projection_manifest, ensure_ascii=False, indent=2) + "\n", compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            os.replace(temp_zip, output_zip)
        except Exception:
            if temp_zip.exists():
                temp_zip.unlink()
            raise
    audit = audit_double_blind_bundle(artifacts=[{"label": "projected_source_zip", "path": str(output_zip)}])
    if not validate_anonymity_audit_receipt(audit):
        raise RuntimeError("venue compliance projection anonymity audit receipt invalid")
    if audit.get("pass") is not True:
        raise RuntimeError(f"venue compliance projection remains anonymity-blocked: {audit.get('blocking_finding_codes')}")
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "venue-compliance-source-projection",
        "paper_id": paper_id,
        "source_filename": source_zip.name,
        "source_sha256": _sha_file(source_zip),
        "projected_filename": output_zip.name,
        "projected_sha256": _sha_file(output_zip),
        "main_tex_entry": main_tex_entry,
        "statement_entry": statement_entry,
        "statement_sha256": _sha_bytes(projected_statement),
        "changed_entries": changed_entries,
        "anonymity_audit_sha256": str(audit.get("anonymity_audit_sha256") or ""),
        "anonymity_audit_status": str(audit.get("status") or ""),
        "status": STATUS,
        "canonical_scientific_artifacts_unchanged": True,
        "scientific_claims_unchanged": True,
        "experiment_evidence_unchanged": True,
        "old_submission_freeze_remains_historical": True,
        "requires_new_submission_freeze": True,
        "automatic_refreeze_forbidden": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["projection_sha256"] = _digest(projection_identity(receipt))
    return receipt


def validate_projection_receipt(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("schema_version") != SCHEMA_VERSION or receipt.get("receipt_type") != "venue-compliance-source-projection":
        return False
    if receipt.get("status") != STATUS:
        return False
    for key in (
        "canonical_scientific_artifacts_unchanged",
        "scientific_claims_unchanged",
        "experiment_evidence_unchanged",
        "old_submission_freeze_remains_historical",
        "requires_new_submission_freeze",
        "automatic_refreeze_forbidden",
    ):
        if receipt.get(key) is not True:
            return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("projection_sha256") or "") == _digest(projection_identity(receipt))
