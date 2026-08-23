from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import zipfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from .presubmission_freeze import validate_freeze, verify_current_frozen_artifacts
from .submission_handoff import validate_handoff_ledger, validate_handoff_receipt

AUDIT_SCHEMA_VERSION = "1.0"
AUDIT_STATUS_PASS = "PASS_VENUE_FORM_CONSISTENCY_AUDIT"
AUDIT_STATUS_FAIL = "FAIL_VENUE_FORM_CONSISTENCY_AUDIT"
AUTHOR_VISIBILITY_ANONYMOUS = "ANONYMOUS_TO_REVIEWERS"
AUTHORITY = {"scientific": False, "experiment": False, "gpu": False, "submission": False}


def _digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _latest(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    for event in reversed(list(row.get("events") or [])):
        if isinstance(event, Mapping) and event.get("event_type") == event_type:
            return dict(event)
    return {}


def _receipt(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    event = _latest(row, event_type)
    value = event.get("receipt") or {}
    return dict(value) if isinstance(value, Mapping) else {}


def _normalize_text(value: Any) -> str:
    text = str(value or "")
    text = text.replace("\\\\", " ")
    text = text.replace("~", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _normalize_keyword(value: Any) -> str:
    return _normalize_text(value).casefold()


def _keywords(value: Any) -> list[str]:
    if isinstance(value, str):
        raw = [item for item in value.split(",")]
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        raw = list(value)
    else:
        raw = []
    return [str(item).strip() for item in raw if str(item).strip()]


def _balanced_braced(text: str, start: int) -> str:
    if start >= len(text) or text[start] != "{":
        return ""
    depth = 0
    chars: list[str] = []
    i = start
    while i < len(text):
        ch = text[i]
        if ch == "{" and (i == 0 or text[i - 1] != "\\"):
            depth += 1
            if depth > 1:
                chars.append(ch)
        elif ch == "}" and (i == 0 or text[i - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return "".join(chars)
            chars.append(ch)
        else:
            chars.append(ch)
        i += 1
    return ""


def _extract_title(tex: str) -> str:
    match = re.search(r"\\title\s*", tex)
    if not match:
        return ""
    brace = tex.find("{", match.end())
    return _balanced_braced(tex, brace) if brace >= 0 else ""


def _extract_abstract(tex: str) -> str:
    match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, flags=re.I | re.S)
    return match.group(1).strip() if match else ""


def _extract_ai_use_statement(tex: str) -> str:
    heading = re.search(
        r"\\(?:sub)*section\*?\s*\{\s*(?:AI\s*[- ]?Use(?:\s+Statement|\s+Disclosure)?|Artificial\s+Intelligence\s+Use(?:\s+Statement|\s+Disclosure)?)\s*\}",
        tex,
        flags=re.I,
    )
    if not heading:
        return ""
    tail = tex[heading.end():]
    boundary = re.search(r"\\(?:sub)*section\*?\s*\{|\\bibliography\b|\\begin\{thebibliography\}|\\end\{document\}", tail, flags=re.I)
    return tail[: boundary.start() if boundary else len(tail)].strip()


def _tex_files_from_artifact(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if not path.exists():
        return rows
    if path.is_dir():
        for item in sorted(path.rglob("*.tex")):
            rows.append((str(item.relative_to(path)), item.read_text(encoding="utf-8", errors="ignore")))
        return rows
    if path.suffix.lower() == ".tex":
        return [(path.name, path.read_text(encoding="utf-8", errors="ignore"))]
    if path.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(path) as archive:
                for name in sorted(archive.namelist()):
                    if name.lower().endswith(".tex") and not name.endswith("/"):
                        rows.append((name, archive.read(name).decode("utf-8", errors="ignore")))
        except zipfile.BadZipFile:
            return []
    return rows


def _source_text_from_freeze(freeze_receipt: Mapping[str, Any]) -> dict[str, Any]:
    tex_rows: list[tuple[str, str]] = []
    source_labels: list[str] = []
    for item in freeze_receipt.get("frozen_artifacts") or []:
        if not isinstance(item, Mapping):
            continue
        label = str(item.get("label") or "")
        path = Path(str(item.get("path") or ""))
        if label in {"source_zip", "submission_bundle", "source_tree"} or path.suffix.lower() in {".zip", ".tex"}:
            rows = _tex_files_from_artifact(path)
            if rows:
                tex_rows.extend(rows)
                source_labels.append(label or path.name)
    if not tex_rows:
        raise RuntimeError("no TeX source found in current frozen artifacts")
    titles = [(name, _extract_title(tex)) for name, tex in tex_rows]
    titles = [(name, value) for name, value in titles if value]
    abstracts = [(name, _extract_abstract(tex)) for name, tex in tex_rows]
    abstracts = [(name, value) for name, value in abstracts if value]
    ai_sections = [(name, _extract_ai_use_statement(tex)) for name, tex in tex_rows]
    ai_sections = [(name, value) for name, value in ai_sections if value]
    if not titles:
        raise RuntimeError("frozen TeX source has no title")
    if not abstracts:
        raise RuntimeError("frozen TeX source has no abstract")
    normalized_titles = {_normalize_text(value) for _, value in titles}
    normalized_abstracts = {_normalize_text(value) for _, value in abstracts}
    if len(normalized_titles) != 1:
        raise RuntimeError(f"multiple inconsistent frozen source titles: {sorted(normalized_titles)}")
    if len(normalized_abstracts) != 1:
        raise RuntimeError("multiple inconsistent frozen source abstracts")
    return {
        "title": next(iter(normalized_titles)),
        "abstract": next(iter(normalized_abstracts)),
        "ai_use_statement": _normalize_text(ai_sections[0][1]) if ai_sections else "",
        "ai_use_statement_source": ai_sections[0][0] if ai_sections else "",
        "source_labels": list(dict.fromkeys(source_labels)),
        "tex_files_scanned": len(tex_rows),
    }


def build_form_contract_template(
    *,
    paper_ledger: Mapping[str, Any],
    freeze_ledger: Mapping[str, Any],
    handoff_ledger: Mapping[str, Any],
    venue_policy: Mapping[str, Any],
) -> dict[str, Any]:
    paper_id = str(paper_ledger.get("paper_id") or "")
    if not paper_id:
        raise RuntimeError("paper id missing")
    freeze_errors = validate_freeze(freeze_ledger)
    if freeze_errors:
        raise RuntimeError(f"freeze ledger invalid: {freeze_errors}")
    drift = verify_current_frozen_artifacts(freeze_ledger)
    if drift:
        raise RuntimeError(f"frozen artifacts are stale: {drift}")
    handoff_errors = validate_handoff_ledger(handoff_ledger)
    if handoff_errors:
        raise RuntimeError(f"handoff ledger invalid: {handoff_errors}")
    freeze = _receipt(freeze_ledger, "pre-submission-freeze")
    handoff = _receipt(handoff_ledger, "machine-submission-handoff")
    if not handoff or not validate_handoff_receipt(handoff):
        raise RuntimeError("current machine handoff invalid")
    if str(freeze_ledger.get("paper_id") or "") != paper_id or str(handoff_ledger.get("paper_id") or "") != paper_id:
        raise RuntimeError("paper/freeze/handoff identity mismatch")
    if str(handoff.get("freeze_sha256") or "") != str(freeze.get("freeze_sha256") or ""):
        raise RuntimeError("handoff is stale relative to current freeze")
    policy_sha = str(venue_policy.get("snapshot_sha256") or "")
    check = dict(venue_policy)
    check.pop("snapshot_sha256", None)
    if not policy_sha or _digest(check) != policy_sha:
        raise RuntimeError("venue policy snapshot digest mismatch")
    if str(handoff.get("venue_policy_snapshot_sha256") or "") != policy_sha:
        raise RuntimeError("handoff/venue policy snapshot mismatch")
    source = _source_text_from_freeze(freeze)
    handoff_title = _normalize_text(handoff.get("title"))
    contract_title = _normalize_text((paper_ledger.get("contract") or {}).get("title"))
    if not handoff_title or handoff_title != contract_title or source["title"] != contract_title:
        raise RuntimeError(
            f"title mismatch across contract/handoff/frozen source: contract={contract_title!r}, handoff={handoff_title!r}, source={source['title']!r}"
        )
    ai_required = bool((venue_policy.get("paper_rules") or {}).get("ai_use_statement_required"))
    if ai_required and not source["ai_use_statement"]:
        raise RuntimeError("venue requires AI-use statement but current frozen source has none")
    supplement_rows = []
    for item in freeze.get("frozen_artifacts") or []:
        if not isinstance(item, Mapping):
            continue
        label = str(item.get("label") or "")
        if label == "paper_pdf":
            continue
        supplement_rows.append({
            "label": label,
            "filename": Path(str(item.get("path") or "artifact")).name,
            "sha256": str(item.get("sha256") or ""),
        })
    template: dict[str, Any] = {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "contract_type": "venue-form-consistency-contract",
        "paper_id": paper_id,
        "venue": str(venue_policy.get("venue") or handoff.get("venue") or ""),
        "binding": {
            "contract_sha256": str(paper_ledger.get("contract_sha256") or ""),
            "freeze_sha256": str(freeze.get("freeze_sha256") or ""),
            "handoff_sha256": str(handoff.get("handoff_sha256") or ""),
            "venue_policy_snapshot_sha256": policy_sha,
        },
        "expected_fields": {
            "title": source["title"],
            "abstract": source["abstract"],
            "keywords": [],
            "author_visibility": AUTHOR_VISIBILITY_ANONYMOUS,
            "ai_use_disclosure": None,
            "supplement_declared": bool(supplement_rows),
            "supplement_artifacts": supplement_rows,
        },
        "source_evidence": {
            "frozen_source_labels": source["source_labels"],
            "tex_files_scanned": source["tex_files_scanned"],
            "ai_use_statement_present": bool(source["ai_use_statement"]),
            "ai_use_statement_sha256": hashlib.sha256(source["ai_use_statement"].encode("utf-8")).hexdigest() if source["ai_use_statement"] else "",
            "ai_use_statement_source": source["ai_use_statement_source"],
        },
        "human_fill_required": ["expected_fields.keywords", "expected_fields.ai_use_disclosure"],
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    return template


def validate_form_contract(contract: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("schema_version") != AUDIT_SCHEMA_VERSION or contract.get("contract_type") != "venue-form-consistency-contract":
        errors.append("venue-form-contract-schema-invalid")
    expected = contract.get("expected_fields") if isinstance(contract.get("expected_fields"), Mapping) else {}
    for key in ("title", "abstract", "author_visibility"):
        if not _normalize_text(expected.get(key)):
            errors.append(f"venue-form-contract-missing:{key}")
    keywords = _keywords(expected.get("keywords"))
    if not keywords:
        errors.append("venue-form-contract-missing:keywords")
    if expected.get("ai_use_disclosure") in (None, "", [], {}):
        errors.append("venue-form-contract-missing:ai_use_disclosure")
    if expected.get("author_visibility") != AUTHOR_VISIBILITY_ANONYMOUS:
        errors.append("venue-form-contract-author-visibility-not-anonymous")
    if any(contract.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        errors.append("venue-form-contract-authority-leak")
    return list(dict.fromkeys(errors))


def _canonical_form_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _canonical_form_value(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_canonical_form_value(item) for item in value]
    if isinstance(value, str):
        return _normalize_text(value)
    return value


def audit_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "freeze_sha256": receipt.get("freeze_sha256"),
        "handoff_sha256": receipt.get("handoff_sha256"),
        "venue_policy_snapshot_sha256": receipt.get("venue_policy_snapshot_sha256"),
        "form_contract_sha256": receipt.get("form_contract_sha256"),
        "form_snapshot_sha256": receipt.get("form_snapshot_sha256"),
        "field_results": receipt.get("field_results") or {},
        "pass": receipt.get("pass"),
        "blockers": receipt.get("blockers") or [],
        "status": receipt.get("status"),
    }


def build_venue_form_audit_receipt(
    *,
    form_contract: Mapping[str, Any],
    form_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    contract_errors = validate_form_contract(form_contract)
    if contract_errors:
        raise RuntimeError(f"venue form contract invalid: {contract_errors}")
    paper_id = str(form_contract.get("paper_id") or "")
    if str(form_snapshot.get("paper_id") or "") != paper_id:
        raise RuntimeError("form snapshot paper id mismatch")
    if str(form_snapshot.get("venue") or "") != str(form_contract.get("venue") or ""):
        raise RuntimeError("form snapshot venue mismatch")
    fields = form_snapshot.get("fields") if isinstance(form_snapshot.get("fields"), Mapping) else {}
    expected = form_contract.get("expected_fields") if isinstance(form_contract.get("expected_fields"), Mapping) else {}
    blockers: list[str] = []
    results: dict[str, Any] = {}

    def result(key: str, ok: bool, expected_value: Any, actual_value: Any) -> None:
        results[key] = {
            "pass": bool(ok),
            "expected_sha256": _digest(_canonical_form_value(expected_value)),
            "actual_sha256": _digest(_canonical_form_value(actual_value)),
        }
        if not ok:
            blockers.append(f"venue-form-field-mismatch:{key}")

    result("title", _normalize_text(fields.get("title")) == _normalize_text(expected.get("title")), expected.get("title"), fields.get("title"))
    result("abstract", _normalize_text(fields.get("abstract")) == _normalize_text(expected.get("abstract")), expected.get("abstract"), fields.get("abstract"))
    exp_keywords = {_normalize_keyword(item) for item in _keywords(expected.get("keywords"))}
    got_keywords = {_normalize_keyword(item) for item in _keywords(fields.get("keywords"))}
    result("keywords", bool(exp_keywords) and got_keywords == exp_keywords, sorted(exp_keywords), sorted(got_keywords))
    result("author_visibility", fields.get("author_visibility") == expected.get("author_visibility"), expected.get("author_visibility"), fields.get("author_visibility"))
    result(
        "ai_use_disclosure",
        _canonical_form_value(fields.get("ai_use_disclosure")) == _canonical_form_value(expected.get("ai_use_disclosure")),
        expected.get("ai_use_disclosure"),
        fields.get("ai_use_disclosure"),
    )
    result(
        "supplement_declared",
        fields.get("supplement_declared") is expected.get("supplement_declared"),
        expected.get("supplement_declared"),
        fields.get("supplement_declared"),
    )
    exp_supp = {str(item.get("label") or ""): str(item.get("sha256") or "") for item in expected.get("supplement_artifacts") or [] if isinstance(item, Mapping)}
    got_supp = {str(item.get("label") or ""): str(item.get("sha256") or "") for item in fields.get("supplement_artifacts") or [] if isinstance(item, Mapping)}
    result("supplement_artifacts", got_supp == exp_supp, exp_supp, got_supp)
    snapshot_capture = str(form_snapshot.get("capture_method") or "").strip()
    captured_at = str(form_snapshot.get("captured_at") or "").strip()
    if not snapshot_capture:
        blockers.append("venue-form-snapshot-capture-method-missing")
    if not captured_at:
        blockers.append("venue-form-snapshot-captured-at-missing")
    binding = form_contract.get("binding") if isinstance(form_contract.get("binding"), Mapping) else {}
    passed = not blockers
    receipt: dict[str, Any] = {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "receipt_type": "venue-form-consistency-audit",
        "paper_id": paper_id,
        "venue": str(form_contract.get("venue") or ""),
        "contract_sha256": str(binding.get("contract_sha256") or ""),
        "freeze_sha256": str(binding.get("freeze_sha256") or ""),
        "handoff_sha256": str(binding.get("handoff_sha256") or ""),
        "venue_policy_snapshot_sha256": str(binding.get("venue_policy_snapshot_sha256") or ""),
        "form_contract_sha256": _digest(form_contract),
        "form_snapshot_sha256": _digest(form_snapshot),
        "field_results": results,
        "pass": passed,
        "blockers": list(dict.fromkeys(blockers)),
        "status": AUDIT_STATUS_PASS if passed else AUDIT_STATUS_FAIL,
        "captured_at": captured_at,
        "capture_method": snapshot_capture,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["venue_form_audit_sha256"] = _digest(audit_identity(receipt))
    return receipt


def validate_venue_form_audit_receipt(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("schema_version") != AUDIT_SCHEMA_VERSION or receipt.get("receipt_type") != "venue-form-consistency-audit":
        return False
    if receipt.get("status") not in {AUDIT_STATUS_PASS, AUDIT_STATUS_FAIL}:
        return False
    if (receipt.get("status") == AUDIT_STATUS_PASS) is not (receipt.get("pass") is True):
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("venue_form_audit_sha256") or "") == _digest(audit_identity(receipt))


def append_venue_form_audit(root: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_venue_form_audit_receipt(receipt):
        raise RuntimeError("invalid venue form audit receipt")
    paper_id = str(receipt.get("paper_id") or "")
    directory = Path(root) / "paper-venue-form-audits"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{paper_id}.json"
    lock = directory / f".{paper_id}.lock"
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        row = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
            "schema_version": AUDIT_SCHEMA_VERSION,
            "paper_id": paper_id,
            "events": [],
            "authority": dict(AUTHORITY),
        }
        prior = _latest(row, "venue-form-consistency-audit")
        prior_receipt = prior.get("receipt") if isinstance(prior.get("receipt"), Mapping) else {}
        if prior_receipt.get("venue_form_audit_sha256") == receipt.get("venue_form_audit_sha256"):
            return row
        event = {
            "event_type": "venue-form-consistency-audit",
            "receipt": dict(receipt),
            "recorded_at": str(receipt.get("captured_at") or ""),
            "scientific_authority": False,
            "experiment_authority": False,
            "gpu_authority": False,
            "submission_authority": False,
        }
        event["event_id"] = _digest([paper_id, len(row.get("events") or []), event])[:24]
        row.setdefault("events", []).append(event)
        row["updated_at"] = event["recorded_at"]
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)
        return row


def validate_venue_form_audit_ledger(row: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if (row.get("authority") or {}) != AUTHORITY:
        errors.append("venue form audit ledger must not grant authority")
    for event in row.get("events") or []:
        if not isinstance(event, Mapping) or event.get("event_type") != "venue-form-consistency-audit":
            errors.append("unknown venue form audit event")
            continue
        receipt = event.get("receipt") or {}
        if not isinstance(receipt, Mapping) or not validate_venue_form_audit_receipt(receipt):
            errors.append("invalid venue form audit receipt")
    return list(dict.fromkeys(errors))


def verify_current_venue_form_audit(
    audit_ledger: Mapping[str, Any],
    handoff_ledger: Mapping[str, Any],
    freeze_ledger: Mapping[str, Any],
) -> list[str]:
    errors = list(validate_venue_form_audit_ledger(audit_ledger))
    audit = _receipt(audit_ledger, "venue-form-consistency-audit")
    handoff = _receipt(handoff_ledger, "machine-submission-handoff")
    freeze = _receipt(freeze_ledger, "pre-submission-freeze")
    if not audit:
        errors.append("venue-form-audit-receipt-missing")
        return list(dict.fromkeys(errors))
    if audit.get("pass") is not True:
        errors.append("venue-form-audit-not-pass")
    if audit.get("handoff_sha256") != handoff.get("handoff_sha256"):
        errors.append("venue-form-audit-handoff-stale")
    if audit.get("freeze_sha256") != freeze.get("freeze_sha256"):
        errors.append("venue-form-audit-freeze-stale")
    errors.extend(verify_current_frozen_artifacts(freeze_ledger))
    return list(dict.fromkeys(errors))
