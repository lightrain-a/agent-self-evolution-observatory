from __future__ import annotations

import hashlib
import json
import os
import re
import zipfile
from pathlib import Path
from typing import Any, Mapping

from .paper_anonymity_audit import ABS_PATH_RE, audit_double_blind_bundle, validate_anonymity_audit_receipt

SCHEMA_VERSION = "1.0"
STATUS = "PASS_ANONYMIZED_SUBMISSION_PROJECTION_REQUIRES_REFREEZE"
SAFE_AUTO_REDACT_SUFFIXES = {".json", ".jsonl"}
TEXT_SCAN_SUFFIXES = {".tex", ".bib", ".md", ".txt", ".yaml", ".yml", ".py", ".sh", ".csv", ".tsv"}


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


def _replace_private_paths(text: str) -> tuple[str, int]:
    count = 0
    def repl(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        value = match.group(0)
        return "private-path-ref:sha256:" + hashlib.sha256(value.encode()).hexdigest()
    return ABS_PATH_RE.sub(repl, text), count


def _redact_json_value(value: Any) -> tuple[Any, int]:
    if isinstance(value, dict):
        out: dict[str, Any] = {}; count = 0
        for key, item in value.items():
            redacted, hits = _redact_json_value(item); out[key] = redacted; count += hits
        return out, count
    if isinstance(value, list):
        out = []; count = 0
        for item in value:
            redacted, hits = _redact_json_value(item); out.append(redacted); count += hits
        return out, count
    if isinstance(value, str):
        return _replace_private_paths(value)
    return value, 0


def _sanitize_entry(name: str, data: bytes) -> tuple[bytes, int, str]:
    suffix = Path(name).suffix.lower()
    if suffix == ".json":
        try:
            value = json.loads(data.decode("utf-8"))
        except Exception:
            text = data.decode("utf-8", errors="ignore")
            if ABS_PATH_RE.search(text):
                raise RuntimeError(f"JSON with private path is not parseable and cannot be safely auto-redacted: {name}")
            return data, 0, "UNCHANGED"
        redacted, hits = _redact_json_value(value)
        if not hits: return data, 0, "UNCHANGED"
        return (json.dumps(redacted, ensure_ascii=False, indent=2) + "\n").encode(), hits, "JSON_PATH_REDACTION"
    if suffix == ".jsonl":
        lines = data.decode("utf-8", errors="strict").splitlines(); out = []; hits = 0
        for index, line in enumerate(lines):
            if not line.strip(): out.append(line); continue
            try: value = json.loads(line)
            except Exception as exc:
                if ABS_PATH_RE.search(line): raise RuntimeError(f"JSONL private path cannot be safely parsed at {name}:{index+1}") from exc
                out.append(line); continue
            redacted, n = _redact_json_value(value); hits += n; out.append(json.dumps(redacted, ensure_ascii=False, separators=(",", ":")))
        if not hits: return data, 0, "UNCHANGED"
        return ("\n".join(out) + ("\n" if data.endswith(b"\n") else "")).encode(), hits, "JSONL_PATH_REDACTION"
    if suffix in TEXT_SCAN_SUFFIXES:
        text = data.decode("utf-8", errors="ignore")
        if ABS_PATH_RE.search(text):
            raise RuntimeError(f"private path occurs in non-metadata text and requires manual packaging repair: {name}")
    return data, 0, "UNCHANGED"


def projection_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: receipt.get(key) for key in (
        "source_filename", "source_sha256", "sanitized_filename", "sanitized_sha256",
        "changed_entries", "redaction_count", "anonymity_audit_sha256", "status",
    )}


def sanitize_submission_zip(*, source_zip: Path, output_zip: Path) -> dict[str, Any]:
    source_zip = Path(source_zip).resolve(); output_zip = Path(output_zip).resolve()
    if not source_zip.is_file() or not zipfile.is_zipfile(source_zip): raise RuntimeError("source submission artifact must be a valid ZIP")
    if output_zip == source_zip: raise RuntimeError("sanitized projection must not overwrite the sealed source ZIP")
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    temp_zip = output_zip.with_name(output_zip.name + ".tmp")
    if temp_zip.exists(): temp_zip.unlink()
    changed: list[dict[str, Any]] = []; total = 0
    try:
      with zipfile.ZipFile(source_zip, "r") as src, zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as dst:
        for info in sorted(src.infolist(), key=lambda row: row.filename):
            if info.is_dir(): continue
            data = src.read(info); new_data, hits, mode = _sanitize_entry(info.filename, data)
            zi = zipfile.ZipInfo(info.filename, date_time=(1980, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = info.external_attr
            dst.writestr(zi, new_data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            if hits:
                changed.append({"entry": info.filename, "original_sha256": _sha_bytes(data), "sanitized_sha256": _sha_bytes(new_data), "redaction_count": hits, "mode": mode})
                total += hits
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "projection_type": "ANONYMIZED_SUBMISSION_METADATA_PROJECTION",
            "source_filename": source_zip.name,
            "source_sha256": _sha_file(source_zip),
            "changed_entries": changed,
            "redaction_count": total,
            "canonical_scientific_artifacts_unchanged": True,
            "private_path_values_not_persisted": True,
            "requires_new_submission_freeze": True,
        }
        manifest["manifest_sha256"] = _digest({k: manifest[k] for k in manifest if k != "manifest_sha256"})
        zi = zipfile.ZipInfo("anonymized-submission-projection.json", date_time=(1980, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
        dst.writestr(zi, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
      os.replace(temp_zip, output_zip)
    except Exception:
      if temp_zip.exists(): temp_zip.unlink()
      raise
    audit = audit_double_blind_bundle(artifacts=[{"label": "sanitized_zip", "path": str(output_zip)}])
    if not validate_anonymity_audit_receipt(audit): raise RuntimeError("sanitized projection anonymity audit receipt invalid")
    if audit.get("pass") is not True: raise RuntimeError(f"sanitized projection remains anonymity-blocked: {audit.get('blocking_finding_codes')}")
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "anonymized-submission-projection",
        "source_filename": source_zip.name,
        "source_sha256": _sha_file(source_zip),
        "sanitized_filename": output_zip.name,
        "sanitized_sha256": _sha_file(output_zip),
        "changed_entries": changed,
        "redaction_count": total,
        "anonymity_audit_sha256": audit["anonymity_audit_sha256"],
        "anonymity_audit_status": audit["status"],
        "status": STATUS,
        "canonical_scientific_artifacts_unchanged": True,
        "old_submission_freeze_remains_historical": True,
        "requires_new_submission_freeze": True,
        "automatic_refreeze_forbidden": True,
        "scientific_authority": False,
        "submission_authority": False,
    }
    receipt["projection_sha256"] = _digest(projection_identity(receipt))
    return receipt


def validate_projection_receipt(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "anonymized-submission-projection" or receipt.get("status") != STATUS: return False
    if receipt.get("canonical_scientific_artifacts_unchanged") is not True or receipt.get("old_submission_freeze_remains_historical") is not True: return False
    if receipt.get("requires_new_submission_freeze") is not True or receipt.get("automatic_refreeze_forbidden") is not True: return False
    if receipt.get("scientific_authority") is not False or receipt.get("submission_authority") is not False: return False
    if int(receipt.get("redaction_count") or 0) != sum(int(row.get("redaction_count") or 0) for row in receipt.get("changed_entries") or []): return False
    return str(receipt.get("projection_sha256") or "") == _digest(projection_identity(receipt))
