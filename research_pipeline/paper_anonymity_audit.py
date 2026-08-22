from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Mapping, Sequence

SCHEMA_VERSION = "1.0"
PASS_STATUS = "PASS_DOUBLE_BLIND_LEAKAGE_AUDIT"
WARN_STATUS = "PASS_DOUBLE_BLIND_LEAKAGE_AUDIT_WITH_REVIEW_WARNINGS"
BLOCK_STATUS = "BLOCKED_DOUBLE_BLIND_LEAKAGE_AUDIT"
TEXT_SUFFIXES = {".tex", ".bib", ".md", ".txt", ".json", ".yaml", ".yml", ".py", ".sh", ".csv", ".tsv"}
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
ORCID_RE = re.compile(r"(?i)(?:https?://orcid\.org/)?\b\d{4}-\d{4}-\d{4}-[\dX]{4}\b")
ABS_PATH_RE = re.compile(r"(?i)(?:/(?:home|Users|data|mnt|srv|tmp)/[^\s{}<>\]\[\"']+|[A-Z]:\\Users\\[^\s{}<>\]\[\"']+)")
REPO_RE = re.compile(r"(?i)https?://(?:www\.)?(?:github\.com|gitlab\.com|bitbucket\.org)/[^\s<>{}\]\[\"']+")
ACK_RE = re.compile(r"(?i)(?:\\(?:section|subsection)\*?\{\s*acknowledg(?:e)?ments?\s*\}|(?:^|\n)\s*acknowledg(?:e)?ments?\s*(?:\n|$))")
LATEX_FIELD_RE = re.compile(r"(?is)\\(author|affiliation|institution|email|thanks|orcid|homepage)\s*(?:\[[^\]]*\])?\s*\{([^{}]*)\}")
SUSPICIOUS_ARCHIVE_PARTS = {".git", ".github", ".idea", ".vscode", "__MACOSX", ".DS_Store"}
ANON_OK = {"", "anonymous", "anonymous authors", "anonymous author", "redacted", "none", "unknown"}


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _text(value: Any) -> str:
    return str(value or "").strip()


def _finding(code: str, artifact: str, location: str, severity: str = "BLOCK") -> dict[str, str]:
    return {"code": code, "severity": severity, "artifact": artifact, "location_hash": hashlib.sha256(location.encode()).hexdigest()[:20]}


def _anonymous_latex_value(value: str) -> bool:
    normalized = re.sub(r"\\[A-Za-z@]+|[{}~\\]", " ", value)
    normalized = " ".join(normalized.split()).casefold()
    if normalized in ANON_OK or normalized in {"anonymous institution", "anonymous affiliation", "institution withheld for review"}:
        return True
    tokens = re.findall(r"[a-z]+", normalized)
    allowed = {"anonymous", "authors", "author", "submission", "paper", "under", "double", "blind", "review", "for", "reviewing", "purposes", "only", "iclr"}
    return bool(tokens and tokens[0] == "anonymous" and set(tokens) <= allowed)


def _scan_text(text: str, artifact: str, location: str, private_tokens: Sequence[str], *, latex_structural: bool = True) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if EMAIL_RE.search(text): findings.append(_finding("email-address-present", artifact, location))
    if ORCID_RE.search(text): findings.append(_finding("orcid-present", artifact, location))
    if ABS_PATH_RE.search(text): findings.append(_finding("absolute-private-path-present", artifact, location))
    if ACK_RE.search(text): findings.append(_finding("acknowledgment-section-present", artifact, location))
    if latex_structural:
        for command, value in LATEX_FIELD_RE.findall(text):
            cmd = command.casefold()
            if cmd in {"author", "affiliation", "institution"} and _anonymous_latex_value(value):
                continue
            if value.strip():
                findings.append(_finding("latex-author-affiliation-identity-command-present", artifact, location + "|" + cmd))
                break
    for token in private_tokens:
        if token and token.casefold() in text.casefold():
            findings.append(_finding("private-identity-token-present", artifact, location + "|" + hashlib.sha256(token.encode()).hexdigest()))
            break
    for match in REPO_RE.findall(text):
        if "anonymous" not in match.casefold() and "anonym" not in match.casefold():
            findings.append(_finding("nonanonymous-repository-url-review-required", artifact, location, "WARN"))
            break
    return findings


def _pdf_info(path: Path) -> tuple[dict[str, str], str]:
    proc = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, timeout=30, check=False)
    if proc.returncode != 0:
        raise RuntimeError("pdfinfo failed")
    info: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1); info[key.strip()] = value.strip()
    with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
        proc2 = subprocess.run(["pdftotext", str(path), tmp.name], capture_output=True, text=True, timeout=60, check=False)
        if proc2.returncode != 0:
            raise RuntimeError("pdftotext failed")
        text = Path(tmp.name).read_text(encoding="utf-8", errors="ignore")
    return info, text


def _scan_pdf(path: Path, label: str, private_tokens: Sequence[str]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    try:
        info, text = _pdf_info(path)
    except Exception:
        return [_finding("pdf-inspection-failed", label, path.name)]
    author = _text(info.get("Author"))
    if author.casefold() not in ANON_OK:
        findings.append(_finding("pdf-author-metadata-not-anonymous", label, path.name + "|Author"))
    for key in ("Title", "Subject", "Keywords", "Creator", "Producer"):
        findings.extend(_scan_text(_text(info.get(key)), label, path.name + "|" + key, private_tokens, latex_structural=False))
    findings.extend(_scan_text(text, label, path.name + "|text", private_tokens, latex_structural=False))
    return findings


def _archive_entries(path: Path) -> list[tuple[str, bytes]]:
    rows: list[tuple[str, bytes]] = []
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            name = info.filename
            if info.is_dir():
                rows.append((name, b"")); continue
            data = archive.read(info)
            rows.append((name, data))
    return rows


def _scan_archive(path: Path, label: str, private_tokens: Sequence[str]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    try:
        entries = _archive_entries(path)
    except Exception:
        return [_finding("archive-inspection-failed", label, path.name)]
    for name, data in entries:
        parts = [part for part in name.replace("\\", "/").split("/") if part]
        if name.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", name):
            findings.append(_finding("archive-absolute-path-present", label, name))
        if any(part in SUSPICIOUS_ARCHIVE_PARTS for part in parts):
            findings.append(_finding("archive-hidden-vcs-or-editor-metadata-present", label, name))
        if EMAIL_RE.search(name) or ORCID_RE.search(name):
            findings.append(_finding("archive-filename-identity-present", label, name))
        for token in private_tokens:
            if token and token.casefold() in name.casefold():
                findings.append(_finding("private-identity-token-in-filename", label, name)); break
        suffix = Path(name).suffix.lower()
        if data and suffix in TEXT_SUFFIXES and len(data) <= 8_000_000:
            text = data.decode("utf-8", errors="ignore")
            findings.extend(_scan_text(text, label, name, private_tokens, latex_structural=suffix == ".tex"))
    return findings


def _scan_directory(path: Path, label: str, private_tokens: Sequence[str]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for item in sorted(path.rglob("*")):
        rel = item.relative_to(path).as_posix()
        if any(part in SUSPICIOUS_ARCHIVE_PARTS for part in item.relative_to(path).parts):
            findings.append(_finding("source-hidden-vcs-or-editor-metadata-present", label, rel))
        if not item.is_file(): continue
        if EMAIL_RE.search(rel) or ORCID_RE.search(rel): findings.append(_finding("source-filename-identity-present", label, rel))
        for token in private_tokens:
            if token and token.casefold() in rel.casefold(): findings.append(_finding("private-identity-token-in-filename", label, rel)); break
        if item.suffix.lower() in TEXT_SUFFIXES and item.stat().st_size <= 8_000_000:
            findings.extend(_scan_text(item.read_text(encoding="utf-8", errors="ignore"), label, rel, private_tokens, latex_structural=item.suffix.lower() == ".tex"))
    return findings


def audit_double_blind_bundle(*, artifacts: Sequence[Mapping[str, Any]], private_identity_tokens: Sequence[str] = ()) -> dict[str, Any]:
    tokens = [str(x).strip() for x in private_identity_tokens if str(x).strip()]
    findings: list[dict[str, str]] = []; manifest: list[dict[str, Any]] = []
    for spec in artifacts:
        if not isinstance(spec, Mapping): continue
        label = _text(spec.get("label")) or "artifact"; path = Path(_text(spec.get("path"))).expanduser().resolve()
        if not path.exists():
            findings.append(_finding("artifact-missing", label, path.name)); continue
        if path.is_file():
            manifest.append({"label": label, "filename": path.name, "sha256": _sha(path), "bytes": path.stat().st_size})
            suffix = path.suffix.lower()
            if suffix == ".pdf": findings.extend(_scan_pdf(path, label, tokens))
            elif suffix == ".zip": findings.extend(_scan_archive(path, label, tokens))
            elif suffix in TEXT_SUFFIXES:
                findings.extend(_scan_text(path.read_text(encoding="utf-8", errors="ignore"), label, path.name, tokens, latex_structural=suffix == ".tex"))
        elif path.is_dir():
            manifest.append({"label": label, "filename": path.name, "sha256": _digest(sorted((p.relative_to(path).as_posix(), _sha(p)) for p in path.rglob("*") if p.is_file())), "bytes": sum(p.stat().st_size for p in path.rglob("*") if p.is_file())})
            findings.extend(_scan_directory(path, label, tokens))
    unique = []
    seen = set()
    for item in findings:
        key = (item["code"], item["artifact"], item["location_hash"])
        if key not in seen: seen.add(key); unique.append(item)
    blockers = [item for item in unique if item.get("severity") == "BLOCK"]
    warnings = [item for item in unique if item.get("severity") == "WARN"]
    status = BLOCK_STATUS if blockers else WARN_STATUS if warnings else PASS_STATUS
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "double-blind-leakage-audit",
        "status": status,
        "pass": not blockers,
        "artifact_manifest": manifest,
        "artifact_manifest_sha256": _digest(manifest),
        "private_identity_token_hashes": sorted(hashlib.sha256(token.encode()).hexdigest() for token in tokens),
        "findings": unique,
        "finding_codes": sorted({item["code"] for item in unique}),
        "finding_count": len(unique),
        "blocking_finding_count": len(blockers),
        "warning_count": len(warnings),
        "blocking_finding_codes": sorted({item["code"] for item in blockers}),
        "warning_codes": sorted({item["code"] for item in warnings}),
        "checks": {
            "pdf_metadata_and_text_scanned": any(item["filename"].lower().endswith(".pdf") for item in manifest),
            "source_or_archive_scanned": any(not item["filename"].lower().endswith(".pdf") for item in manifest),
            "private_tokens_stored_as_hash_only": True,
            "receipt_contains_no_raw_private_identity_tokens": True,
        },
        "scientific_authority": False,
        "submission_authority": False,
    }
    receipt["anonymity_audit_sha256"] = _digest({k: receipt[k] for k in receipt if k != "anonymity_audit_sha256"})
    return receipt


def validate_anonymity_audit_receipt(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "double-blind-leakage-audit" or receipt.get("schema_version") != SCHEMA_VERSION: return False
    findings = receipt.get("findings") or []
    if not isinstance(findings, list) or int(receipt.get("finding_count") or 0) != len(findings): return False
    blockers = [item for item in findings if isinstance(item, Mapping) and item.get("severity") == "BLOCK"]
    warnings = [item for item in findings if isinstance(item, Mapping) and item.get("severity") == "WARN"]
    if any(not isinstance(item, Mapping) or item.get("severity") not in {"BLOCK", "WARN"} for item in findings): return False
    expected = BLOCK_STATUS if blockers else WARN_STATUS if warnings else PASS_STATUS
    if receipt.get("status") != expected or receipt.get("pass") is not (not blockers): return False
    if int(receipt.get("blocking_finding_count") or 0) != len(blockers) or int(receipt.get("warning_count") or 0) != len(warnings): return False
    if list(receipt.get("blocking_finding_codes") or []) != sorted({item["code"] for item in blockers}): return False
    if list(receipt.get("warning_codes") or []) != sorted({item["code"] for item in warnings}): return False
    manifest = receipt.get("artifact_manifest") or []
    if not isinstance(manifest, list) or not manifest or _digest(manifest) != _text(receipt.get("artifact_manifest_sha256")): return False
    if any("path" in item for item in manifest if isinstance(item, Mapping)): return False
    if receipt.get("scientific_authority") is not False or receipt.get("submission_authority") is not False: return False
    checks = receipt.get("checks") or {}
    if checks.get("private_tokens_stored_as_hash_only") is not True or checks.get("receipt_contains_no_raw_private_identity_tokens") is not True: return False
    return _text(receipt.get("anonymity_audit_sha256")) == _digest({k: receipt[k] for k in receipt if k != "anonymity_audit_sha256"})


def public_anonymity_audit(receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_anonymity_audit_receipt(receipt):
        return {"status": "DOUBLE_BLIND_AUDIT_INVALID", "pass": False, "finding_count": 0, "finding_codes": [], "anonymity_audit_sha256": ""}
    return {
        "status": receipt.get("status"), "pass": receipt.get("pass") is True,
        "finding_count": int(receipt.get("finding_count") or 0), "finding_codes": list(receipt.get("finding_codes") or []),
        "blocking_finding_count": int(receipt.get("blocking_finding_count") or 0), "warning_count": int(receipt.get("warning_count") or 0),
        "blocking_finding_codes": list(receipt.get("blocking_finding_codes") or []), "warning_codes": list(receipt.get("warning_codes") or []),
        "artifact_count": len(receipt.get("artifact_manifest") or []), "anonymity_audit_sha256": _text(receipt.get("anonymity_audit_sha256")),
        "scientific_authority": False, "submission_authority": False,
    }
