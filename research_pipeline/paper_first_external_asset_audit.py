from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import requests

from .paper_first_external_paper_identity import validate_external_paper_identity_receipt

SCHEMA_VERSION = "1.1"
_ASSET_HOSTS = {"github.com", "huggingface.co"}


def _now(value: datetime | None = None) -> str:
    return (value or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _sha(value: str | bytes) -> str:
    payload = value if isinstance(value, bytes) else value.encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _default_fetcher(*, url: str, timeout: float, headers: dict[str, str]):
    return requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)


def _hrefs(page: str) -> list[str]:
    values = []
    for match in re.finditer(r'href\s*=\s*["\']([^"\']+)["\']', str(page or ""), flags=re.I):
        url = html.unescape(match.group(1)).strip()
        if url.startswith("https://") or url.startswith("http://"):
            values.append(url)
    return values


def _paper_declaration_surface(page: str) -> str:
    """Return only the paper-authored arXiv metadata/abstract surface.

    arXiv appends Labs and "Code, Data, Media" UI after the paper metadata. Those
    controls contain generic GitHub/Hugging Face links that are platform chrome,
    not declarations by the paper authors.  Missing/changed arXiv markup therefore
    fails closed to an empty declaration surface rather than forwarding UI links.
    """
    text = str(page or "")
    start = re.search(r'<div\b[^>]*\bid=["\']abs["\'][^>]*>', text, flags=re.I)
    if start is None:
        return ""
    end_positions = []
    for marker in ("<!--end leftcolumn-->", '<div class="extra-services"', "<div class='extra-services'"):
        pos = text.find(marker, start.end())
        if pos >= 0:
            end_positions.append(pos)
    end = min(end_positions) if end_positions else len(text)
    return text[start.start():end]


def _asset_kind(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower().split(":", 1)[0]
    if host == "github.com":
        return "GITHUB"
    if host == "huggingface.co":
        return "HUGGING_FACE"
    if host.endswith(".github.io") or host == "github.io":
        return "PROJECT_PAGE"
    return ""


def _normalize_asset_url(url: str) -> str:
    parsed = urlparse(url)
    scheme = "https" if parsed.scheme in {"http", "https"} else parsed.scheme
    host = parsed.netloc.lower().split(":", 1)[0]
    path = re.sub(r"/+", "/", parsed.path or "/")
    if host == "github.com":
        parts = [part for part in path.split("/") if part]
        if len(parts) >= 2:
            path = f"/{parts[0]}/{parts[1]}"
    if host == "huggingface.co":
        parts = [part for part in path.split("/") if part]
        if len(parts) >= 2 and parts[0] not in {"datasets", "spaces"}:
            path = f"/{parts[0]}/{parts[1]}"
        elif len(parts) >= 3:
            path = f"/{parts[0]}/{parts[1]}/{parts[2]}"
    return f"{scheme}://{host}{path.rstrip('/')}"


def build_external_asset_audit(
    *,
    identity_receipt: dict[str, Any],
    fetcher: Callable[..., Any] | None = None,
    now: datetime | None = None,
    timeout: float = 25.0,
) -> dict[str, Any]:
    """Audit first-party asset declarations only after bibliographic identity passes.

    The paper's official arXiv page is the declaration carrier.  Repository/model
    links are candidates for manual/next-stage first-party inspection only when
    they are linked from that verified primary page.  This function never starts
    experiments and never treats absence of a declared endpoint as scientific
    evidence.
    """
    identity_errors = validate_external_paper_identity_receipt(identity_receipt)
    identity_verified = (
        not identity_errors
        and identity_receipt.get("status") == "VERIFIED_BIBLIOGRAPHIC_IDENTITY"
        and identity_receipt.get("asset_audit_authorized") is True
    )
    official = identity_receipt.get("official_identity") or {}
    identity_binding = str((identity_receipt.get("identity_check") or {}).get("identity_binding_sha256") or "")
    state: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now(now),
        "status": "HOLD_BIBLIOGRAPHIC_IDENTITY",
        "source_identity": {
            "status": str(identity_receipt.get("status") or ""),
            "ref": str(official.get("ref") or ""),
            "title": str(official.get("title") or ""),
            "primary_url": str(official.get("primary_url") or ""),
            "identity_binding_sha256": identity_binding,
            "verified": identity_verified,
        },
        "primary_page": {},
        "declared_asset_endpoints": [],
        "summary": {
            "identity_verified": int(identity_verified),
            "primary_page_verified": 0,
            "declared_asset_endpoints": 0,
            "github_endpoints": 0,
            "huggingface_endpoints": 0,
            "project_page_endpoints": 0,
        },
        "next_action": "repair-bibliographic-identity",
        "asset_content_review_authorized": False,
        "provider_calls_authorized": False,
        "method_authorized": False,
        "experiment_authorized": False,
        "p0_authorized": False,
        "gpu_authorized": False,
        "scientific_authority": False,
        "policy": {
            "verified_bibliographic_identity_required_before_network_asset_probe": True,
            "official_primary_page_is_asset_declaration_carrier": True,
            "only_paper_metadata_surface_is_declaration_carrier": True,
            "arxiv_labs_and_platform_chrome_are_not_paper_asset_declarations": True,
            "repository_or_model_url_guess_is_not_first_party_provenance": True,
            "only_primary_declared_asset_endpoints_are_forwarded": True,
            "no_declared_endpoint_is_evidence_absence_not_scientific_negative": True,
            "asset_audit_never_authorizes_experiment_execution": True,
        },
    }
    if not identity_verified:
        if identity_errors:
            state["identity_validation_errors"] = identity_errors
        return state

    primary_url = str(official.get("primary_url") or "")
    if not primary_url.startswith("https://arxiv.org/abs/"):
        state["status"] = "HOLD_PRIMARY_PAGE_IDENTITY_INVALID"
        state["next_action"] = "repair-primary-page-binding"
        return state

    fetcher = fetcher or _default_fetcher
    headers = {"User-Agent": "Agent-Self-Evolution-Observatory/1.0 official-asset-audit"}
    try:
        response = fetcher(url=primary_url, timeout=timeout, headers=headers)
    except Exception as exc:
        state["status"] = "HOLD_PRIMARY_PAGE_FETCH_FAILED"
        state["primary_page"] = {"url": primary_url, "fetch_error": type(exc).__name__}
        state["next_action"] = "retry-official-primary-page-asset-audit"
        return state

    status_code = int(getattr(response, "status_code", 0) or 0)
    page = str(getattr(response, "text", "") or "")
    final_url = str(getattr(response, "url", primary_url) or primary_url)
    state["primary_page"] = {
        "url": primary_url,
        "final_url": final_url,
        "http_status": status_code,
        "content_sha256": _sha(page) if page else "",
    }
    if status_code != 200 or not page:
        state["status"] = "HOLD_PRIMARY_PAGE_FETCH_FAILED"
        state["next_action"] = "retry-official-primary-page-asset-audit"
        return state

    state["summary"]["primary_page_verified"] = 1
    declaration_surface = _paper_declaration_surface(page)
    endpoints: dict[str, dict[str, Any]] = {}
    for raw_url in _hrefs(declaration_surface):
        kind = _asset_kind(raw_url)
        if not kind:
            continue
        normalized = _normalize_asset_url(raw_url)
        if not normalized:
            continue
        endpoints.setdefault(normalized, {
            "url": normalized,
            "kind": kind,
            "declared_by": primary_url,
            "declaration_carrier_sha256": state["primary_page"]["content_sha256"],
            "first_party_declaration_provenance": True,
            "content_reviewed": False,
            "scientific_authority": False,
        })
    rows = sorted(endpoints.values(), key=lambda value: (str(value["kind"]), str(value["url"])))
    state["declared_asset_endpoints"] = rows
    state["summary"].update({
        "declared_asset_endpoints": len(rows),
        "github_endpoints": sum(row["kind"] == "GITHUB" for row in rows),
        "huggingface_endpoints": sum(row["kind"] == "HUGGING_FACE" for row in rows),
        "project_page_endpoints": sum(row["kind"] == "PROJECT_PAGE" for row in rows),
    })
    if rows:
        state["status"] = "READY_FOR_DECLARED_ASSET_CONTENT_REVIEW"
        state["next_action"] = "inspect-primary-declared-assets-read-only"
        state["asset_content_review_authorized"] = True
    else:
        state["status"] = "VERIFIED_IDENTITY_NO_DECLARED_ASSET_ENDPOINTS"
        state["next_action"] = "inspect-official-paper-pdf-or-author-project-surface-manually"
    return state


def validate_external_asset_audit(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    status = str(state.get("status") or "")
    summary = state.get("summary") or {}
    source = state.get("source_identity") or {}
    rows = [row for row in state.get("declared_asset_endpoints") or [] if isinstance(row, dict)]
    ready = status == "READY_FOR_DECLARED_ASSET_CONTENT_REVIEW"

    if state.get("scientific_authority") is not False:
        errors.append("external asset audit cannot carry scientific authority")
    for key in ("provider_calls_authorized", "method_authorized", "experiment_authorized", "p0_authorized", "gpu_authorized"):
        if state.get(key) is not False:
            errors.append(f"external asset audit cannot authorize {key}")
    if state.get("asset_content_review_authorized") is not ready:
        errors.append("asset content review authorization must exactly follow declared endpoint readiness")
    if int(summary.get("declared_asset_endpoints") or 0) != len(rows):
        errors.append("declared asset endpoint summary mismatch")
    if source.get("verified") is not True and (rows or ready or int(summary.get("primary_page_verified") or 0)):
        errors.append("unverified bibliographic identity cannot probe or forward asset endpoints")
    for row in rows:
        if row.get("first_party_declaration_provenance") is not True or row.get("scientific_authority") is not False:
            errors.append("declared asset endpoint provenance invalid")
        if str(row.get("declared_by") or "") != str(source.get("primary_url") or ""):
            errors.append("declared asset endpoint carrier drift")
        if _asset_kind(str(row.get("url") or "")) != str(row.get("kind") or ""):
            errors.append("declared asset endpoint kind invalid")
    return sorted(set(errors))


def write_external_asset_audit(
    *,
    identity_receipt: dict[str, Any],
    path: Path,
    fetcher: Callable[..., Any] | None = None,
    now: datetime | None = None,
    timeout: float = 25.0,
) -> dict[str, Any]:
    state = build_external_asset_audit(identity_receipt=identity_receipt, fetcher=fetcher, now=now, timeout=timeout)
    errors = validate_external_asset_audit(state)
    if errors:
        raise ValueError("Invalid external asset audit: " + ";".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit primary-declared first-party paper assets after identity verification.")
    parser.add_argument("--identity-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    identity = json.loads(args.identity_receipt.read_text(encoding="utf-8"))
    state = write_external_asset_audit(identity_receipt=identity, path=args.output)
    print(json.dumps(state, ensure_ascii=False, indent=2))


__all__ = [
    "SCHEMA_VERSION",
    "build_external_asset_audit",
    "validate_external_asset_audit",
    "write_external_asset_audit",
]


if __name__ == "__main__":
    main()
