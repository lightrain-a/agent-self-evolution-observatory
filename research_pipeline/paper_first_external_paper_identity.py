from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

import requests

from .paper_first_primary_evidence import _title_similarity, parse_arxiv_atom

SCHEMA_VERSION = "1.0"
TITLE_MATCH_THRESHOLD = 0.72
_ARXIV_ID_RE = re.compile(r"^(?:arXiv:)?(?P<id>\d{4}\.\d{4,5})(?:v\d+)?$", flags=re.I)


def _now(value: datetime | None = None) -> str:
    return (value or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _sha(value: str | bytes) -> str:
    payload = value if isinstance(value, bytes) else value.encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def normalize_arxiv_ref(value: str) -> tuple[str, str]:
    raw = str(value or "").strip()
    match = _ARXIV_ID_RE.fullmatch(raw)
    if not match:
        return "", ""
    arxiv_id = match.group("id")
    return f"arXiv:{arxiv_id}", arxiv_id


def _default_requester(*, arxiv_id: str, timeout: float, headers: dict[str, str]):
    return requests.get(
        "https://export.arxiv.org/api/query",
        params={"id_list": arxiv_id, "max_results": 1},
        timeout=timeout,
        headers=headers,
    )


def _default_title_search_requester(*, title: str, timeout: float, headers: dict[str, str]):
    escaped = str(title or "").replace('"', " ")
    return requests.get(
        "https://export.arxiv.org/api/query",
        params={
            "search_query": f'ti:"{escaped}"',
            "start": 0,
            "max_results": 10,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        },
        timeout=timeout,
        headers=headers,
    )


def _base_receipt(*, claimed_title: str, claimed_ref: str, now: datetime | None) -> dict[str, Any]:
    normalized_ref, arxiv_id = normalize_arxiv_ref(claimed_ref)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now(now),
        "status": "HOLD_PRIMARY_IDENTITY_UNRESOLVED",
        "claimed_identity": {
            "title": " ".join(str(claimed_title or "").split()),
            "ref": str(claimed_ref or "").strip(),
            "normalized_ref": normalized_ref,
            "arxiv_id": arxiv_id,
        },
        "official_identity": {},
        "identity_check": {
            "primary_metadata_source": "https://export.arxiv.org/api/query",
            "title_match_threshold": TITLE_MATCH_THRESHOLD,
            "title_similarity": 0.0,
            "ref_resolves": False,
            "claimed_title_matches_resolved_ref": False,
            "primary_metadata_sha256": "",
            "identity_binding_sha256": "",
        },
        "identity_recovery": {
            "title_search_attempted": False,
            "matching_candidates": [],
            "matching_candidate_count": 0,
            "claimed_title_primary_identity_status": "NOT_SEARCHED",
        },
        "next_action": "recover-primary-paper-identifier",
        "asset_audit_authorized": False,
        "provider_calls_authorized": False,
        "method_authorized": False,
        "experiment_authorized": False,
        "p0_authorized": False,
        "gpu_authorized": False,
        "scientific_authority": False,
        "policy": {
            "asset_audit_requires_verified_bibliographic_identity_receipt": True,
            "title_and_ref_must_resolve_to_the_same_primary_record": True,
            "title_ref_mismatch_is_quarantine_not_scientific_negative": True,
            "unverified_identity_cannot_start_asset_or_experiment_execution": True,
            "bibliographic_verification_grants_read_only_asset_audit_only": True,
            "bibliographic_verification_never_grants_scientific_or_experiment_authority": True,
        },
    }


def build_external_paper_identity_receipt(
    *,
    claimed_title: str,
    claimed_ref: str,
    requester: Callable[..., Any] | None = None,
    title_search_requester: Callable[..., Any] | None = None,
    now: datetime | None = None,
    timeout: float = 25.0,
) -> dict[str, Any]:
    """Resolve a claimed title↔arXiv pair before any first-party asset audit.

    This is an intake/provenance gate, not a scientific review.  A verified receipt
    permits only read-only official asset inspection.  Any mismatch is quarantined
    instead of silently retargeting the paper or proceeding to experiments.
    """
    receipt = _base_receipt(claimed_title=claimed_title, claimed_ref=claimed_ref, now=now)
    claimed = receipt["claimed_identity"]
    claimed_title = str(claimed.get("title") or "")
    arxiv_id = str(claimed.get("arxiv_id") or "")
    if not claimed_title or not arxiv_id:
        receipt["status"] = "HOLD_INVALID_PAPER_IDENTITY_INPUT"
        receipt["next_action"] = "supply-title-and-valid-arxiv-id"
        return receipt

    requester = requester or _default_requester
    headers = {"User-Agent": "Agent-Self-Evolution-Observatory/1.0 bibliographic-identity-intake"}
    try:
        response = requester(arxiv_id=arxiv_id, timeout=timeout, headers=headers)
    except Exception as exc:  # network failures are evidence absence, never a paper decision
        receipt["status"] = "HOLD_PRIMARY_IDENTITY_FETCH_FAILED"
        receipt["identity_check"]["fetch_error"] = type(exc).__name__
        receipt["next_action"] = "retry-primary-identity-resolution"
        return receipt

    status_code = int(getattr(response, "status_code", 0) or 0)
    text = str(getattr(response, "text", "") or "")
    receipt["identity_check"]["http_status"] = status_code
    receipt["identity_check"]["primary_metadata_sha256"] = _sha(text) if text else ""
    if status_code != 200 or not text:
        receipt["status"] = "HOLD_PRIMARY_IDENTITY_FETCH_FAILED"
        receipt["next_action"] = "retry-primary-identity-resolution"
        return receipt

    rows = parse_arxiv_atom(text)
    matching = [
        row for row in rows
        if str((((row.get("metadata") or {}).get("externalIds") or {}).get("ArXiv")) or "") == arxiv_id
    ]
    if len(matching) != 1:
        receipt["status"] = "HOLD_PRIMARY_IDENTITY_UNRESOLVED"
        receipt["identity_check"]["resolved_records"] = len(matching)
        receipt["next_action"] = "recover-primary-paper-identifier"
        return receipt

    row = matching[0]
    official_title = " ".join(str(row.get("title") or "").split())
    publication_date = str(((row.get("metadata") or {}).get("publicationDate") or ""))
    official_ref = f"arXiv:{arxiv_id}"
    primary_url = f"https://arxiv.org/abs/{arxiv_id}"
    similarity = _title_similarity(claimed_title, official_title)
    metadata_sha = str(receipt["identity_check"].get("primary_metadata_sha256") or "")
    binding_sha = _sha("\n".join((official_ref, official_title, publication_date, metadata_sha)))
    receipt["official_identity"] = {
        "ref": official_ref,
        "arxiv_id": arxiv_id,
        "title": official_title,
        "publication_date": publication_date,
        "primary_url": primary_url,
    }
    receipt["identity_check"].update({
        "ref_resolves": True,
        "resolved_records": 1,
        "title_similarity": round(float(similarity), 6),
        "claimed_title_matches_resolved_ref": similarity >= TITLE_MATCH_THRESHOLD,
        "identity_binding_sha256": binding_sha,
    })

    if similarity < TITLE_MATCH_THRESHOLD:
        receipt["status"] = "QUARANTINED_TITLE_ARXIV_MISMATCH"
        recovery = receipt["identity_recovery"]
        recovery["title_search_attempted"] = True
        title_search_requester = title_search_requester or _default_title_search_requester
        try:
            search_response = title_search_requester(title=claimed_title, timeout=timeout, headers=headers)
            search_status = int(getattr(search_response, "status_code", 0) or 0)
            search_text = str(getattr(search_response, "text", "") or "")
            recovery["http_status"] = search_status
            recovery["search_metadata_sha256"] = _sha(search_text) if search_text else ""
            search_rows = parse_arxiv_atom(search_text) if search_status == 200 and search_text else []
            candidates = []
            for candidate in search_rows:
                candidate_title = " ".join(str(candidate.get("title") or "").split())
                candidate_similarity = _title_similarity(claimed_title, candidate_title)
                if candidate_similarity < TITLE_MATCH_THRESHOLD:
                    continue
                candidate_arxiv_id = str((((candidate.get("metadata") or {}).get("externalIds") or {}).get("ArXiv")) or "")
                if not candidate_arxiv_id:
                    continue
                candidates.append({
                    "ref": f"arXiv:{candidate_arxiv_id}",
                    "title": candidate_title,
                    "publication_date": str(((candidate.get("metadata") or {}).get("publicationDate") or "")),
                    "primary_url": f"https://arxiv.org/abs/{candidate_arxiv_id}",
                    "title_similarity": round(float(candidate_similarity), 6),
                })
            candidates.sort(key=lambda value: (-float(value["title_similarity"]), str(value["ref"])))
            recovery["matching_candidates"] = candidates[:10]
            recovery["matching_candidate_count"] = len(candidates)
            if len(candidates) == 1:
                recovery["claimed_title_primary_identity_status"] = "UNIQUE_RECOVERY_CANDIDATE_FOUND"
                receipt["status"] = "QUARANTINED_TITLE_ARXIV_MISMATCH_RECOVERY_CANDIDATE_FOUND"
                receipt["next_action"] = "rebind-to-recovery-candidate-and-reverify"
            elif candidates:
                recovery["claimed_title_primary_identity_status"] = "AMBIGUOUS_RECOVERY_CANDIDATES"
                receipt["next_action"] = "disambiguate-primary-paper-identifier"
            else:
                recovery["claimed_title_primary_identity_status"] = "UNRESOLVED_NO_PRIMARY_TITLE_MATCH"
                receipt["next_action"] = "recover-primary-paper-identifier"
        except Exception as exc:
            recovery["claimed_title_primary_identity_status"] = "RECOVERY_SEARCH_FAILED"
            recovery["search_error"] = type(exc).__name__
            receipt["next_action"] = "retry-primary-title-recovery-search"
        return receipt

    receipt["status"] = "VERIFIED_BIBLIOGRAPHIC_IDENTITY"
    receipt["next_action"] = "official-first-party-asset-audit"
    receipt["asset_audit_authorized"] = True
    return receipt


def validate_external_paper_identity_receipt(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    status = str(state.get("status") or "")
    verified = status == "VERIFIED_BIBLIOGRAPHIC_IDENTITY"
    check = state.get("identity_check") or {}
    official = state.get("official_identity") or {}
    claimed = state.get("claimed_identity") or {}

    if state.get("scientific_authority") is not False:
        errors.append("bibliographic identity receipt cannot carry scientific authority")
    for key in ("provider_calls_authorized", "method_authorized", "experiment_authorized", "p0_authorized", "gpu_authorized"):
        if state.get(key) is not False:
            errors.append(f"bibliographic identity receipt cannot authorize {key}")
    if state.get("asset_audit_authorized") is not verified:
        errors.append("asset audit authorization must exactly follow verified bibliographic identity")
    if verified:
        if check.get("ref_resolves") is not True or check.get("claimed_title_matches_resolved_ref") is not True:
            errors.append("verified bibliographic identity requires resolved ref and matching title")
        if float(check.get("title_similarity") or 0.0) < TITLE_MATCH_THRESHOLD:
            errors.append("verified bibliographic identity title similarity below threshold")
        if not re.fullmatch(r"[0-9a-f]{64}", str(check.get("identity_binding_sha256") or "")):
            errors.append("verified bibliographic identity requires content binding")
        if str(official.get("ref") or "") != str(claimed.get("normalized_ref") or ""):
            errors.append("verified bibliographic identity ref drift")
    else:
        if state.get("asset_audit_authorized") is not False:
            errors.append("unverified bibliographic identity cannot authorize asset audit")
    return sorted(set(errors))


def write_external_paper_identity_receipt(
    *,
    claimed_title: str,
    claimed_ref: str,
    path: Path,
    requester: Callable[..., Any] | None = None,
    title_search_requester: Callable[..., Any] | None = None,
    now: datetime | None = None,
    timeout: float = 25.0,
) -> dict[str, Any]:
    state = build_external_paper_identity_receipt(
        claimed_title=claimed_title,
        claimed_ref=claimed_ref,
        requester=requester,
        title_search_requester=title_search_requester,
        now=now,
        timeout=timeout,
    )
    errors = validate_external_paper_identity_receipt(state)
    if errors:
        raise ValueError("Invalid external paper identity receipt: " + ";".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a claimed paper title↔arXiv identity before asset audit.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--ref", required=True, dest="claimed_ref")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    state = write_external_paper_identity_receipt(
        claimed_title=args.title,
        claimed_ref=args.claimed_ref,
        path=args.output,
    )
    print(json.dumps(state, ensure_ascii=False, indent=2))


__all__ = [
    "SCHEMA_VERSION",
    "TITLE_MATCH_THRESHOLD",
    "normalize_arxiv_ref",
    "build_external_paper_identity_receipt",
    "validate_external_paper_identity_receipt",
    "write_external_paper_identity_receipt",
]


if __name__ == "__main__":
    main()
