from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .config import PROJECT_ROOT

CANDIDATE_ID = "PA-03-HARNESS-SELECTION-INVERSION"
SOURCE_REF = "arXiv:2607.13683"
ARXIV_VERSION = "v2"
ARXIV_LAST_REVISED = "2026-07-30"
ARXIV_API = "https://export.arxiv.org/api/query?id_list=2607.13683"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "harnessbank-support-audit-20260817.json"
DEFAULT_HOLD_JSON = PROJECT_ROOT / "generated" / "harnessbank-fresh-phenomenon-support-hold-20260817.json"
PHENOMENON_ID = "03bd345821be718b2b342e2348ab18c44a91146219bdde5db2d909336cb8ce52"
CANDIDATE_REPOSITORY = "https://github.com/GAIR-NLP/HarnessBank"
CANDIDATE_REPOSITORY_API = "https://api.github.com/repos/GAIR-NLP/HarnessBank"
GITHUB_SEARCH_QUERIES = (
    "HarnessBank in:name",
    "HarnessBank GAIR-NLP",
    "2607.13683",
)
REQUIRED_UNIT = (
    "paired per-gene harness evolution histories and downstream outcomes under the frozen verification rule, "
    "with enough lineage to reconstruct selected-versus-rejected verification decisions"
)
REOPEN_ONLY_IF = (
    "A first-party release exposes replayable paired gene histories/outcomes and verification lineage sufficient to "
    "reconstruct the frozen selected-versus-rejected decision unit without substituting synthetic or inferred histories."
)
ALLOWED_STATUSES = {
    "HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT",
    "HOLD_SUPPORT_RELEASE_SURFACE_CHANGED_REVIEW_REQUIRED",
    "HOLD_SUPPORT_PRIMARY_SOURCE_CHANGED_REVIEW_REQUIRED",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _http_bytes(url: str, *, accept: str, timeout: float = 20.0) -> tuple[int, bytes]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": accept,
            "User-Agent": "agent-self-evolution-observatory-release-audit/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status), response.read()
    except urllib.error.HTTPError as error:
        return int(error.code), error.read()
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, b""


def _http_json(url: str, *, timeout: float = 20.0) -> tuple[int, Any]:
    status, body = _http_bytes(url, accept="application/vnd.github+json", timeout=timeout)
    if status == 0:
        return 0, {"probe_error": "network-error"}
    try:
        return status, json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return status, {"non_json_response": True}


def probe_current_primary_source(
    *,
    http_bytes: Callable[[str], tuple[int, bytes]] | None = None,
) -> dict[str, Any]:
    getter = http_bytes or (lambda url: _http_bytes(url, accept="application/atom+xml"))
    status, raw = getter(ARXIV_API)
    row: dict[str, Any] = {
        "checked_at": _now(),
        "arxiv_api_http_status": status,
        "probe_complete": False,
        "arxiv_version": "",
        "last_revised": "",
        "updated_at": "",
        "title": "",
        "code_disclosure": "",
        "code_release_is_future_conditional": False,
        "primary_source_changed": True,
    }
    if status != 200 or not raw:
        return row
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return row
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entry = root.find("a:entry", ns)
    if entry is None:
        return row
    entry_id = str(entry.findtext("a:id", default="", namespaces=ns)).strip()
    updated = str(entry.findtext("a:updated", default="", namespaces=ns)).strip()
    title = " ".join(str(entry.findtext("a:title", default="", namespaces=ns)).split())
    summary = " ".join(str(entry.findtext("a:summary", default="", namespaces=ns)).split())
    version = entry_id.rsplit("v", 1)[-1] if "v" in entry_id else ""
    version = f"v{version}" if version.isdigit() else ""
    disclosure = "Our code will be publicly available upon acceptance."
    future_conditional = disclosure in summary
    last_revised = updated[:10] if len(updated) >= 10 else ""
    row.update(
        {
            "probe_complete": bool(version and updated and title),
            "arxiv_version": version,
            "last_revised": last_revised,
            "updated_at": updated,
            "title": title,
            "code_disclosure": disclosure if future_conditional else "",
            "code_release_is_future_conditional": future_conditional,
            "primary_source_changed": not (
                version == ARXIV_VERSION
                and last_revised == ARXIV_LAST_REVISED
                and future_conditional
            ),
        }
    )
    return row


def probe_current_release_surface(
    *,
    http_json: Callable[[str], tuple[int, Any]] | None = None,
) -> dict[str, Any]:
    """Bounded public-release probe; it never treats a repository name guess as scientific evidence.

    The candidate endpoint was previously surfaced by the local research system, but the arXiv v2 page does not
    establish it as an already public official repository. Therefore an HTTP 200 or a search hit only opens a
    manual first-party asset review; it can never auto-promote PA-03 or assert that the required corpus exists.
    """

    getter = http_json or (lambda url: _http_json(url))
    repo_status, repo_payload = getter(CANDIDATE_REPOSITORY_API)
    searches: list[dict[str, Any]] = []
    for query in GITHUB_SEARCH_QUERIES:
        url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode({"q": query, "per_page": 10})
        status, payload = getter(url)
        total_count = payload.get("total_count") if isinstance(payload, dict) else None
        items = payload.get("items") if isinstance(payload, dict) else []
        searches.append(
            {
                "query": query,
                "http_status": status,
                "total_count": int(total_count) if isinstance(total_count, int) else None,
                "public_matches": [
                    str(row.get("full_name") or "")
                    for row in (items or [])[:10]
                    if isinstance(row, dict) and str(row.get("full_name") or "")
                ],
            }
        )
    probe_complete = repo_status in {200, 404} and all(
        int(row.get("http_status") or 0) == 200 and isinstance(row.get("total_count"), int)
        for row in searches
    )
    search_has_match = any((row.get("total_count") or 0) > 0 for row in searches)
    release_surface_changed = repo_status == 200 or search_has_match
    return {
        "checked_at": _now(),
        "candidate_repository_endpoint": CANDIDATE_REPOSITORY,
        "candidate_repository_endpoint_is_primary_source_established": False,
        "candidate_repository_api_http_status": repo_status,
        "candidate_repository_public": repo_status == 200,
        "github_public_repository_searches": searches,
        "probe_complete": probe_complete,
        "release_surface_changed": release_surface_changed,
        "required_unit_release_confirmed": False,
        "scientific_evidence": False,
        "interpretation": (
            "A public repository/search hit changes only the release-review surface; paired histories/outcomes and "
            "verification lineage must still be inspected before the support gate can reopen."
        ),
    }


def build_harnessbank_support_audit(
    *,
    primary_source_probe: dict[str, Any],
    release_surface: dict[str, Any],
    source_tree_sha256: str,
    paper_pdf_sha256: str,
    paper_text_sha256: str,
) -> dict[str, Any]:
    primary_changed = primary_source_probe.get("primary_source_changed") is True
    release_changed = release_surface.get("release_surface_changed") is True
    status = (
        "HOLD_SUPPORT_PRIMARY_SOURCE_CHANGED_REVIEW_REQUIRED"
        if primary_changed
        else (
            "HOLD_SUPPORT_RELEASE_SURFACE_CHANGED_REVIEW_REQUIRED"
            if release_changed
            else "HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT"
        )
    )
    state: dict[str, Any] = {
        "schema_version": "1.1",
        "candidate_id": CANDIDATE_ID,
        "source_ref": SOURCE_REF,
        "audited_at": _now(),
        "status": status,
        "required_unit": REQUIRED_UNIT,
        "primary_source": {
            **primary_source_probe,
            "source_tree_sha256": source_tree_sha256,
            "paper_pdf_sha256": paper_pdf_sha256,
            "paper_text_sha256": paper_text_sha256,
            "release_interpretation": (
                "The probed current primary source still describes code release as future/conditional rather than "
                "documenting an already public replay substrate."
                if primary_source_probe.get("primary_source_changed") is not True
                else "The primary-source version or code-release disclosure changed; refresh and review first-party source assets before any support decision."
            ),
        },
        "current_release_surface_audit": release_surface,
        "released_required_unit_present": False,
        "why_hold": (
            "The paper-level aggregate result is insufficient for the frozen inversion falsifier. Without auditable "
            "gene-level selection histories and downstream outcomes, selected-harness survivorship cannot be separated "
            "from a genuine verification-selection inversion mechanism."
        ),
        "reopen_only_if": REOPEN_ONLY_IF,
        "authority": {
            "scientific_authority": False,
            "problem_gate_authority": False,
            "paper_design_authority": False,
            "method_authority": False,
            "experiment_authority": False,
            "p0_authority": False,
            "gpu_authority": False,
            "automatic_release_polling_authority": False,
        },
    }
    state["audit_sha256"] = _canonical_sha({k: v for k, v in state.items() if k != "audit_sha256"})
    return state


def validate_harnessbank_support_audit(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not state:
        return ["missing-harnessbank-support-audit"]
    if state.get("schema_version") != "1.1":
        errors.append("harnessbank-support-audit-schema-drift")
    if state.get("candidate_id") != CANDIDATE_ID:
        errors.append("harnessbank-support-audit-candidate-drift")
    if state.get("source_ref") != SOURCE_REF:
        errors.append("harnessbank-support-audit-source-drift")
    if state.get("status") not in ALLOWED_STATUSES:
        errors.append("harnessbank-support-audit-status-drift")
    if state.get("required_unit") != REQUIRED_UNIT:
        errors.append("harnessbank-support-audit-required-unit-drift")
    if state.get("reopen_only_if") != REOPEN_ONLY_IF:
        errors.append("harnessbank-support-audit-reopen-contract-drift")
    primary = state.get("primary_source") or {}
    if primary.get("probe_complete") is not True:
        errors.append("harnessbank-primary-source-probe-incomplete")
    if not str(primary.get("arxiv_version") or "").startswith("v") or not str(primary.get("last_revised") or ""):
        errors.append("harnessbank-primary-source-version-missing")
    primary_changed = primary.get("primary_source_changed") is True
    if not primary_changed and (
        primary.get("arxiv_version") != ARXIV_VERSION
        or primary.get("last_revised") != ARXIV_LAST_REVISED
        or primary.get("code_release_is_future_conditional") is not True
    ):
        errors.append("harnessbank-primary-source/change-flag-drift")
    for key in ("source_tree_sha256", "paper_pdf_sha256", "paper_text_sha256"):
        value = str(primary.get(key) or "")
        if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
            errors.append(f"harnessbank-primary-invalid-sha256:{key}")
    release = state.get("current_release_surface_audit") or {}
    if release.get("probe_complete") is not True:
        errors.append("harnessbank-release-surface-probe-incomplete")
    if release.get("scientific_evidence") is not False:
        errors.append("release-surface-probe-cannot-be-scientific-evidence")
    if release.get("required_unit_release_confirmed") is not False:
        errors.append("release-surface-probe-cannot-auto-confirm-required-unit")
    expected_status = (
        "HOLD_SUPPORT_PRIMARY_SOURCE_CHANGED_REVIEW_REQUIRED"
        if primary_changed
        else (
            "HOLD_SUPPORT_RELEASE_SURFACE_CHANGED_REVIEW_REQUIRED"
            if release.get("release_surface_changed") is True
            else "HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT"
        )
    )
    if state.get("status") != expected_status:
        errors.append("harnessbank-release-surface/status-drift")
    if state.get("released_required_unit_present") is not False:
        errors.append("harnessbank-required-unit-cannot-be-present-without-first-party-asset-review")
    authority = state.get("authority") or {}
    if any(bool(value) for value in authority.values()):
        errors.append("harnessbank-support-audit-cannot-carry-authority")
    expected_sha = _canonical_sha({k: v for k, v in state.items() if k != "audit_sha256"})
    if state.get("audit_sha256") != expected_sha:
        errors.append("harnessbank-support-audit-hash-mismatch")
    return errors


def build_harnessbank_support_hold(*, audit: dict[str, Any], audit_file_sha256: str) -> dict[str, Any]:
    if validate_harnessbank_support_audit(audit):
        raise ValueError("cannot build HarnessBank support hold from invalid audit")
    if len(audit_file_sha256) != 64 or any(ch not in "0123456789abcdef" for ch in audit_file_sha256):
        raise ValueError("invalid HarnessBank audit file sha256")
    hold: dict[str, Any] = {
        "schema_version": "1.1",
        "candidate_id": CANDIDATE_ID,
        "title": "HarnessBank selection-inversion phenomenon support hold",
        "source_ref": SOURCE_REF,
        "phenomenon_id": PHENOMENON_ID,
        "status": "HOLD_SUPPORT",
        "support_status": audit.get("status"),
        "scientific_authority": False,
        "required_unit": REQUIRED_UNIT,
        "reason": (
            "The aggregate train/test result is insufficient to distinguish verification-selection inversion from small-n ranking noise, "
            "winner's curse, survivorship, or ordinary adaptive selection. The bound current-source audit has not confirmed a replayable "
            "first-party corpus exposing paired gene histories, outcomes, and verification lineage."
        ),
        "support_audit_artifact": str(DEFAULT_JSON.relative_to(PROJECT_ROOT)),
        "support_audit_sha256": audit_file_sha256,
        "support_audit_internal_sha256": audit.get("audit_sha256"),
        "reopen_only_if": (
            REOPEN_ONLY_IF
            + " A release-surface or primary-source change requests re-audit only and does not automatically clear this hold or authorize scientific progression."
        ),
        "authority": {
            "dead_end": False,
            "problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
            "automatic_release_reopen": False,
        },
    }
    hold["hold_sha256"] = _canonical_sha({k: v for k, v in hold.items() if k != "hold_sha256"})
    return hold


def validate_harnessbank_support_hold(hold: dict[str, Any], *, audit_path: Path = DEFAULT_JSON) -> list[str]:
    errors: list[str] = []
    if hold.get("schema_version") != "1.1":
        errors.append("harnessbank-support-hold-schema-drift")
    if hold.get("candidate_id") != CANDIDATE_ID or hold.get("source_ref") != SOURCE_REF:
        errors.append("harnessbank-support-hold-source-drift")
    if hold.get("phenomenon_id") != PHENOMENON_ID:
        errors.append("harnessbank-support-hold-phenomenon-drift")
    if hold.get("status") != "HOLD_SUPPORT":
        errors.append("harnessbank-support-hold-must-remain-hold")
    if hold.get("scientific_authority") is not False:
        errors.append("harnessbank-support-hold-cannot-carry-scientific-authority")
    if hold.get("required_unit") != REQUIRED_UNIT:
        errors.append("harnessbank-support-hold-required-unit-drift")
    if hold.get("support_audit_artifact") != str(DEFAULT_JSON.relative_to(PROJECT_ROOT)):
        errors.append("harnessbank-support-hold-audit-path-drift")
    if audit_path.is_file():
        audit_file_sha = hashlib.sha256(audit_path.read_bytes()).hexdigest()
        if hold.get("support_audit_sha256") != audit_file_sha:
            errors.append("harnessbank-support-hold-audit-file-hash-mismatch")
        try:
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            audit = {}
        if validate_harnessbank_support_audit(audit):
            errors.append("harnessbank-support-hold-bound-audit-invalid")
        elif hold.get("support_audit_internal_sha256") != audit.get("audit_sha256"):
            errors.append("harnessbank-support-hold-audit-internal-hash-mismatch")
        elif hold.get("support_status") != audit.get("status"):
            errors.append("harnessbank-support-hold-status-drift")
    else:
        errors.append("harnessbank-support-hold-bound-audit-missing")
    authority = hold.get("authority") or {}
    if any(bool(value) for value in authority.values()):
        errors.append("harnessbank-support-hold-cannot-carry-authority")
    expected_sha = _canonical_sha({k: v for k, v in hold.items() if k != "hold_sha256"})
    if hold.get("hold_sha256") != expected_sha:
        errors.append("harnessbank-support-hold-hash-mismatch")
    return errors


def write_harnessbank_support_audit(
    *,
    json_path: Path = DEFAULT_JSON,
    source_tree_sha256: str,
    paper_pdf_sha256: str,
    paper_text_sha256: str,
) -> dict[str, Any]:
    primary_source_probe = probe_current_primary_source()
    release_surface = probe_current_release_surface()
    state = build_harnessbank_support_audit(
        primary_source_probe=primary_source_probe,
        release_surface=release_surface,
        source_tree_sha256=source_tree_sha256,
        paper_pdf_sha256=paper_pdf_sha256,
        paper_text_sha256=paper_text_sha256,
    )
    errors = validate_harnessbank_support_audit(state)
    if errors:
        raise ValueError("; ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def write_harnessbank_support_bundle(
    *,
    json_path: Path = DEFAULT_JSON,
    hold_path: Path = DEFAULT_HOLD_JSON,
    source_tree_sha256: str,
    paper_pdf_sha256: str,
    paper_text_sha256: str,
) -> dict[str, Any]:
    audit = write_harnessbank_support_audit(
        json_path=json_path,
        source_tree_sha256=source_tree_sha256,
        paper_pdf_sha256=paper_pdf_sha256,
        paper_text_sha256=paper_text_sha256,
    )
    audit_file_sha256 = hashlib.sha256(json_path.read_bytes()).hexdigest()
    hold = build_harnessbank_support_hold(audit=audit, audit_file_sha256=audit_file_sha256)
    errors = validate_harnessbank_support_hold(hold, audit_path=json_path)
    if errors:
        raise ValueError("; ".join(errors))
    hold_path.parent.mkdir(parents=True, exist_ok=True)
    hold_path.write_text(json.dumps(hold, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"audit": audit, "support_hold": hold}


def main() -> None:
    parser = argparse.ArgumentParser(description="Bounded current-release support audit for PA-03 HarnessBank")
    parser.add_argument("--out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--hold-out", type=Path, default=DEFAULT_HOLD_JSON)
    parser.add_argument("--source-tree-sha256", required=True)
    parser.add_argument("--paper-pdf-sha256", required=True)
    parser.add_argument("--paper-text-sha256", required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            write_harnessbank_support_bundle(
                json_path=args.out,
                hold_path=args.hold_out,
                source_tree_sha256=args.source_tree_sha256,
                paper_pdf_sha256=args.paper_pdf_sha256,
                paper_text_sha256=args.paper_text_sha256,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
