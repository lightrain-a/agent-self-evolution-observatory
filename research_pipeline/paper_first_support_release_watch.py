from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import requests

from .config import PROJECT_ROOT, StorageSettings
from .paper_first_primary_evidence import (
    DEFAULT_ARXIV_RATE_LIMIT_COOLDOWN_SECONDS,
    _arxiv_retry_after_seconds,
    _load_arxiv_rate_limit_state,
    _write_arxiv_rate_limit_state,
    parse_arxiv_page,
)
from .paper_first_search_portfolio_design_adjudication import build_search_portfolio_design_adjudication

WATCH_SCHEMA = "1.0"
FINGERPRINT_VERSION = "release-surface-v3"
DEFAULT_COOLDOWN_DAYS = 7.0
PRIMARY_DECLARATION_REFRESH_COOLDOWN_DAYS = 7.0
MAX_PRIMARY_DECLARATION_REFRESHES = 2
MAX_PAGE_BYTES = 1_000_000
PORTABLE_TARGETS_SCHEMA = "1.0"
PORTABLE_OBSERVATIONS_SCHEMA = "1.0"
DEFAULT_PORTABLE_TARGETS_JSON = PROJECT_ROOT / "generated" / "paper-first-support-release-targets.json"
DEFAULT_PORTABLE_TARGETS_JS = PROJECT_ROOT / "generated" / "paper-first-support-release-targets.js"


def _now(value: datetime | None = None) -> datetime:
    return (value or datetime.now(timezone.utc)).astimezone(timezone.utc)


def _watch_root(storage: StorageSettings) -> Path:
    return storage.data_root / "paper-first-problem-discovery" / "support-release-watch"


def _primary_root(storage: StorageSettings) -> Path:
    return storage.data_root / "paper-first-problem-discovery" / "primary-sources"


def _sha(value: bytes | str) -> str:
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(raw).hexdigest()


def _bounded(value: Any, limit: int = 1800) -> str:
    return " ".join(str(value or "").split())[:limit]


def release_watch_contract_sha(
    *,
    candidate_id: str,
    candidate_snapshot_sha256: str,
    targets: list[dict[str, Any]],
    required_reopen_components: list[str] | tuple[str, ...],
) -> str:
    normalized_targets = sorted(
        ({
            "source_ref": str(row.get("source_ref") or "").strip(),
            "url": _clean_url(str(row.get("url") or "")),
            "declaration_kind": str(row.get("declaration_kind") or "").strip().upper(),
            "baseline_revision": str(row.get("baseline_revision") or "").strip().lower(),
            "scientific_authority": False,
        } for row in targets if isinstance(row, dict)),
        key=lambda row: (row["source_ref"], row["url"], row["declaration_kind"], row["baseline_revision"]),
    )
    material = {
        "candidate_id": str(candidate_id or "").strip(),
        "candidate_snapshot_sha256": str(candidate_snapshot_sha256 or "").strip().lower(),
        "targets": normalized_targets,
        "required_reopen_components": sorted({str(x).strip() for x in required_reopen_components if str(x).strip()}),
        "scientific_authority": False,
    }
    return _sha(json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def _terminal_support_holds(design_state: dict[str, Any]) -> list[dict[str, Any]]:
    """Return unresolved terminal support holds across legacy and split memory.

    Support-unavailable rows became reopenable ``hold_objects`` when persistent
    search memory split scientific dead ends from operational holds.  Older
    states may still carry the same rows in ``blocked_objects``.  Read both,
    reject any row certified as a scientific dead end, and deduplicate by its
    provenance-bearing terminal-hold identity rather than candidate id alone
    (shadow candidate ids are reused across runs).
    """
    memory = design_state.get("shadow_search_memory") or design_state.get("shadow_dead_end_memory") or {}
    rows = list(memory.get("closed_objects") or memory.get("blocked_objects") or []) + list(memory.get("hold_objects") or [])
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("disposition") or "") != "HOLD_SUPPORT_UNAVAILABLE":
            continue
        basin = str(row.get("basin") or "")
        if not basin.startswith(("near-miss-terminal-support-hold-", "fresh-phenomenon-support-hold-")) or row.get("dead_end_certified") is True:
            continue
        key = (str(row.get("source_candidate_id") or ""), str(row.get("source_run_id") or ""), basin)
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(row))
    return out


def _load_pre_f0_support_preflight(storage: StorageSettings) -> dict[str, Any]:
    path = storage.site_artifact_dir / "paper-first-pre-f0-problem-falsifier-preflight.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_pre_f0_evidence_plan(storage: StorageSettings) -> dict[str, Any]:
    path = storage.site_artifact_dir / "paper-first-pre-f0-evidence-acquisition-plan.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict) or payload.get("scientific_authority") is not False:
        return {}
    return payload


def _pre_f0_support_holds(storage: StorageSettings) -> list[dict[str, Any]]:
    """Expose canonical Pre-F0 release waits, including evidence-review terminal HOLDs.

    A candidate may have entered Pre-F0 with bounded first-party design allowed and
    later become source-specific after independent BLOCK_BAKE_IN review.  The release
    watcher must follow the *effective* evidence state rather than the historical
    design-eligibility bit; otherwise those terminal HOLDs silently fall out of release
    monitoring.  The evidence-plan overlay is accepted only when candidate identity,
    zero authority, and a content-addressed release-watch contract all bind exactly.
    """
    state = _load_pre_f0_support_preflight(storage)
    evidence_plan = _load_pre_f0_evidence_plan(storage)
    evidence_by_id = {
        str(item.get("candidate_id") or ""): item
        for item in evidence_plan.get("entries") or []
        if isinstance(item, dict) and str(item.get("candidate_id") or "")
    }
    if state.get("scientific_authority") is not False:
        return []
    authority = state.get("authority") or {}
    if any(authority.get(key) is not False for key in ("canonical_generator", "canonical_problem_gate", "paper_design", "method", "experiment", "p0", "gpu")):
        return []
    run_id = str(state.get("run_id") or "").strip()
    support_sha = str(state.get("support_inventory_sha256") or "").strip().lower()
    if not run_id or not re.fullmatch(r"[0-9a-f]{64}", support_sha):
        return []
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in state.get("rows") or []:
        if not isinstance(row, dict):
            continue
        candidate_id = str(row.get("candidate_id") or "").strip()
        refs = sorted({str(ref).strip() for ref in row.get("primary_refs") or [] if str(ref).strip().startswith("arXiv:")})
        evidence = evidence_by_id.get(candidate_id) or {}
        watch_contract = evidence.get("release_watch_contract") or {}
        contract_targets = [dict(target) for target in watch_contract.get("targets") or [] if isinstance(target, dict)]
        contract_required = [str(x).strip() for x in watch_contract.get("required_reopen_components") or [] if str(x).strip()]
        contract_digest = release_watch_contract_sha(
            candidate_id=candidate_id,
            candidate_snapshot_sha256=str(evidence.get("candidate_snapshot_sha256") or ""),
            targets=contract_targets,
            required_reopen_components=contract_required,
        ) if evidence and contract_targets else ""
        effective_hold = bool(
            evidence
            and evidence.get("scientific_authority") is False
            and evidence.get("execution_authorized") is False
            and str(evidence.get("status") or "") in {"HOLD_EVIDENCE_REVIEW_BLOCKED", "WAIT_PRIMARY_ASSET_RELEASE"}
            and str(evidence.get("candidate_snapshot_sha256") or "").strip().lower()
                == str(row.get("candidate_snapshot_sha256") or "").strip().lower()
            and watch_contract.get("scientific_authority") is False
            and bool(contract_required)
            and str(watch_contract.get("contract_sha256") or "").strip().lower() == contract_digest
        )
        legacy_release_only = bool(
            row.get("bounded_first_party_evidence_design_allowed") is False
            and str(row.get("next_route") or "") == "WAIT_FIRST_PARTY_RELEASE_CHANGE"
            and str(row.get("support_recheck_mode") or "") == "FIRST_PARTY_RELEASE_CHANGE_ONLY"
        )
        targets = [dict(target) for target in row.get("release_watch_targets") or [] if isinstance(target, dict)]
        audit_sha = str(row.get("support_audit_sha256") or "").strip().lower()
        memory_class = "PRE_F0_RELEASE_CHANGE_ONLY_HOLD"
        if effective_hold:
            overlay_targets = contract_targets
            if overlay_targets:
                targets = overlay_targets
                audit_sha = str(watch_contract.get("contract_sha256") or "").strip().lower()
                memory_class = "PRE_F0_EFFECTIVE_RELEASE_HOLD"
        if (
            not candidate_id
            or candidate_id in seen
            or str(row.get("disposition") or "") != "HOLD_SUPPORT_UNAVAILABLE"
            or row.get("scientific_authority") is not False
            or not (legacy_release_only or effective_hold)
            or not refs
            or not targets
            or not re.fullmatch(r"[0-9a-f]{64}", audit_sha)
        ):
            continue
        seen.add(candidate_id)
        out.append({
            "source_candidate_id": candidate_id,
            "source_run_id": run_id,
            "source_stage_manifest_sha256": support_sha,
            "support_audit_sha256": audit_sha,
            "candidate_snapshot_sha256": str(evidence.get("candidate_snapshot_sha256") or "").strip().lower() if effective_hold else "",
            "basin": "pre-f0-support-hold-" + _sha(f"{candidate_id}\n{run_id}\n{support_sha}")[:16],
            "disposition": "HOLD_SUPPORT_UNAVAILABLE",
            "support_status": "SUPPORT_UNAVAILABLE_FOR_FROZEN_PROBLEM_FALSIFIER",
            "required_unit": _bounded(row.get("required_unit")),
            "reopen_only_if": _bounded(row.get("reopen_only_if")),
            "evidence_basis": refs,
            "current_source_refs": refs,
            "release_watch_targets": targets,
            "memory_class": memory_class,
            "dead_end_certified": False,
            "scientific_authority": False,
        })
    return out


def current_support_holds(design_state: dict[str, Any], *, storage: StorageSettings) -> list[dict[str, Any]]:
    """Return the zero-authority support-HOLD population used by watch and recheck."""
    rows = _terminal_support_holds(design_state) + _pre_f0_support_holds(storage)
    dedup: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (
            str(row.get("source_candidate_id") or ""),
            str(row.get("source_run_id") or ""),
            str(row.get("basin") or ""),
        )
        dedup.setdefault(key, row)
    return list(dedup.values())


def _support_holds(design_state: dict[str, Any], *, storage: StorageSettings) -> list[dict[str, Any]]:
    return current_support_holds(design_state, storage=storage)


def _arxiv_ids(row: dict[str, Any]) -> list[str]:
    refs = list(row.get("evidence_basis") or []) + list(row.get("current_source_refs") or []) + list(row.get("primary_refs") or [])
    out: list[str] = []
    for ref in refs:
        match = re.fullmatch(r"arXiv:(\d{4}\.\d+)", str(ref or "").strip(), flags=re.I)
        if match and match.group(1) not in out:
            out.append(match.group(1))
    return out


def _visible_context(raw: str, start: int, end: int) -> str:
    snippet = raw[max(0, start - 900): min(len(raw), end + 900)]
    snippet = re.sub(r"<[^>]+>", " ", snippet)
    return " ".join(html.unescape(snippet).split())


def _clean_url(url: str) -> str:
    return html.unescape(str(url or "")).rstrip(".,;:)]}")


def _huggingface_dataset_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != "huggingface.co":
        return None
    parts = [x for x in parsed.path.strip("/").split("/") if x]
    if len(parts) != 3 or parts[0].lower() != "datasets":
        return None
    if any(part in {".", ".."} for part in parts[1:]):
        return None
    return f"{parts[1]}/{parts[2]}"


def _acceptable_release_url(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")
    if parsed.scheme not in {"http", "https"}:
        return False
    if host == "github.com":
        parts = [x for x in path.split("/") if x]
        return len(parts) >= 2 and parts[0].lower() not in {"arxiv", "brucemiller"}
    if host.endswith(".github.io") or host == "github.io":
        return bool(path or host != "github.io")
    if _huggingface_dataset_id(url):
        return True
    return False


def _declared_release_links(raw: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for match in re.finditer(r"https?://[^\s\"'<>\\)\]]+", raw, flags=re.I):
        url = _clean_url(match.group(0))
        if not _acceptable_release_url(url):
            continue
        context = _visible_context(raw, match.start(), match.end())
        low = context.lower()
        kind = ""
        if any(phrase in low for phrase in (
            "code will be made publicly available",
            "code will be publicly available",
            "code will be made available",
            "code will be released",
            "will open-source",
            "will open source",
            "will be open-sourced",
            "will be open sourced",
        )):
            kind = "FUTURE_CODE_RELEASE"
        elif "project page" in low:
            kind = "PROJECT_PAGE"
        if kind:
            out.append({"url": url, "declaration_kind": kind, "declaration_context": _bounded(context, 700)})
    dedup: dict[tuple[str, str], dict[str, str]] = {}
    for row in out:
        dedup[(row["url"], row["declaration_kind"])] = row
    return list(dedup.values())


def explicit_release_targets(
    design_state: dict[str, Any],
    *,
    storage: StorageSettings | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    storage = storage or StorageSettings.from_env()
    root = _primary_root(storage)
    targets: list[dict[str, Any]] = []
    no_endpoint: list[dict[str, Any]] = []
    for hold in _support_holds(design_state, storage=storage):
        candidate_id = str(hold.get("source_candidate_id") or "")
        refs = [f"arXiv:{value}" for value in _arxiv_ids(hold)]
        found: list[dict[str, Any]] = []
        for target in hold.get("release_watch_targets") or []:
            if not isinstance(target, dict):
                continue
            source_ref = str(target.get("source_ref") or "").strip()
            url = _clean_url(str(target.get("url") or ""))
            kind = str(target.get("declaration_kind") or "").strip().upper()
            baseline_revision = str(target.get("baseline_revision") or "").strip().lower()
            valid_kind = kind in {"FIRST_PARTY_REPOSITORY", "FIRST_PARTY_DATASET"}
            kind_matches_url = (
                (kind == "FIRST_PARTY_REPOSITORY" and urlparse(url).netloc.lower() == "github.com")
                or (kind == "FIRST_PARTY_DATASET" and _huggingface_dataset_id(url) is not None)
            )
            if (
                source_ref not in refs
                or not _acceptable_release_url(url)
                or not valid_kind
                or not kind_matches_url
                or not re.fullmatch(r"[0-9a-f]{40}", baseline_revision)
                or target.get("scientific_authority") is not False
            ):
                continue
            found.append({
                "candidate_id": candidate_id,
                "source_ref": source_ref,
                "url": url,
                "declaration_kind": kind,
                "declaration_context": (
                    "durable-support-audit-first-party-dataset"
                    if kind == "FIRST_PARTY_DATASET"
                    else "durable-support-audit-first-party-repository"
                ),
                "primary_cache_sha256": "",
                "endpoint_provenance_kind": "SUPPORT_AUDIT",
                "endpoint_provenance_sha256": str(hold.get("support_audit_sha256") or ""),
                "candidate_snapshot_sha256": str(hold.get("candidate_snapshot_sha256") or "").strip().lower(),
                "baseline_revision": baseline_revision,
                "required_unit": _bounded(hold.get("required_unit")),
                "reopen_only_if": _bounded(hold.get("reopen_only_if")),
                "support_audited_target": True,
                "scientific_authority": False,
            })
        for arxiv_id in _arxiv_ids(hold):
            for path in sorted(root.glob(f"arxiv-{arxiv_id}-*.html")) + sorted(root.glob(f"arxiv-full-{arxiv_id}-*.html")):
                raw = path.read_text(encoding="utf-8", errors="replace")
                cache_sha = _sha(raw)
                for link in _declared_release_links(raw):
                    found.append({
                        "candidate_id": candidate_id,
                        "source_ref": f"arXiv:{arxiv_id}",
                        "url": link["url"],
                        "declaration_kind": link["declaration_kind"],
                        "declaration_context": link["declaration_context"],
                        "primary_cache_sha256": cache_sha,
                        "endpoint_provenance_kind": "PRIMARY_CACHE",
                        "endpoint_provenance_sha256": cache_sha,
                        "baseline_revision": "",
                        "required_unit": _bounded(hold.get("required_unit")),
                        "reopen_only_if": _bounded(hold.get("reopen_only_if")),
                        "support_audited_target": False,
                        "scientific_authority": False,
                    })
        dedup: dict[tuple[str, str, str], dict[str, Any]] = {}
        for row in found:
            key = (row["candidate_id"], row["source_ref"], row["url"])
            previous = dedup.get(key)
            if previous is None or row.get("support_audited_target") is True:
                dedup[key] = row
        if dedup:
            targets.extend(dedup.values())
        else:
            no_endpoint.append({
                "candidate_id": candidate_id,
                "source_refs": refs,
                "status": "NO_EXPLICIT_AUTHOR_RELEASE_ENDPOINT",
                "required_unit": _bounded(hold.get("required_unit")),
                "reopen_only_if": _bounded(hold.get("reopen_only_if")),
                "scientific_authority": False,
            })
    targets.sort(key=lambda row: (str(row.get("candidate_id") or ""), str(row.get("source_ref") or ""), str(row.get("url") or "")))
    return targets, no_endpoint


def build_portable_release_target_manifest(
    design_state: dict[str, Any],
    *,
    storage: StorageSettings | None = None,
) -> dict[str, Any]:
    """Export only public release endpoints discovered from the canonical primary cache.

    Required-unit text, reopen conditions, declaration context, and any cached primary
    content stay private. The receiving host must join these endpoint rows back to its
    own zero-authority terminal HOLD memory before using them.
    """
    targets, _ = explicit_release_targets(design_state, storage=storage)
    safe = []
    for row in targets:
        # Portable schema 1.0 carries only endpoints grounded directly in the
        # canonical primary cache. Support-audited Pre-F0 repository targets
        # stay local until the portable contract is explicitly versioned.
        if str(row.get("endpoint_provenance_kind") or "PRIMARY_CACHE") != "PRIMARY_CACHE":
            continue
        if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("primary_cache_sha256") or "")):
            continue
        safe.append({
            "candidate_id": str(row.get("candidate_id") or ""),
            "source_ref": str(row.get("source_ref") or ""),
            "url": str(row.get("url") or ""),
            "declaration_kind": str(row.get("declaration_kind") or ""),
            "primary_cache_sha256": str(row.get("primary_cache_sha256") or ""),
            "scientific_authority": False,
        })
    safe.sort(key=lambda row: (row["candidate_id"], row["url"]))
    material = json.dumps(safe, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": PORTABLE_TARGETS_SCHEMA,
        "status": "PORTABLE_SUPPORT_RELEASE_TARGETS_READY",
        "manifest_sha256": _sha(material),
        "policy": {
            "scientific_authority": False,
            "public_release_endpoints_only": True,
            "support_contract_fields_not_exported": True,
            "primary_text_context_not_exported": True,
            "receiver_must_join_against_current_terminal_support_holds": True,
            "manifest_cannot_qualify_support_or_reopen_scientific_state": True,
        },
        "summary": {
            "support_holds": len(_terminal_support_holds(design_state)),
            "explicit_release_targets": len(safe),
            "candidates_with_targets": len({row["candidate_id"] for row in safe}),
        },
        "targets": safe,
        "scientific_authority": False,
    }


def validate_portable_release_target_manifest(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("scientific_authority") is not False or (state.get("policy") or {}).get("scientific_authority") is not False:
        errors.append("portable release-target manifest cannot carry scientific authority")
    rows = [row for row in state.get("targets") or [] if isinstance(row, dict)]
    material = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if str(state.get("manifest_sha256") or "") != _sha(material):
        errors.append("portable release-target manifest digest mismatch")
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        candidate = str(row.get("candidate_id") or "")
        ref = str(row.get("source_ref") or "")
        url = str(row.get("url") or "")
        kind = str(row.get("declaration_kind") or "")
        cache_sha = str(row.get("primary_cache_sha256") or "")
        key = (candidate, ref, url)
        if not candidate or not re.fullmatch(r"arXiv:\d{4}\.\d+", ref, flags=re.I) or not _acceptable_release_url(url) or kind not in {"FUTURE_CODE_RELEASE", "PROJECT_PAGE"} or not re.fullmatch(r"[0-9a-f]{64}", cache_sha) or row.get("scientific_authority") is not False:
            errors.append("portable release-target row invalid")
        if key in seen:
            errors.append("portable release-target row duplicated")
        seen.add(key)
        if any(key_name in row for key_name in ("required_unit", "reopen_only_if", "declaration_context", "asset_audit", "evidence_excerpt")):
            errors.append("portable release-target row leaks private/support-contract content")
    return sorted(set(errors))


def write_portable_release_target_manifest(
    *,
    design_state: dict[str, Any] | None = None,
    storage: StorageSettings | None = None,
    json_path: Path = DEFAULT_PORTABLE_TARGETS_JSON,
    js_path: Path = DEFAULT_PORTABLE_TARGETS_JS,
) -> dict[str, Any]:
    design_state = design_state if design_state is not None else build_search_portfolio_design_adjudication()
    state = build_portable_release_target_manifest(design_state, storage=storage)
    errors = validate_portable_release_target_manifest(state)
    if errors:
        raise ValueError("Invalid portable support release targets: " + ";".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_SUPPORT_RELEASE_TARGETS = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


def load_portable_release_target_manifest(path: Path = DEFAULT_PORTABLE_TARGETS_JSON) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(state, dict) or validate_portable_release_target_manifest(state):
        return {}
    return state


def _portable_targets_for_holds(
    design_state: dict[str, Any],
    manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    holds = _terminal_support_holds(design_state)
    out: list[dict[str, Any]] = []
    for row in manifest.get("targets") or []:
        if not isinstance(row, dict):
            continue
        candidate = str(row.get("candidate_id") or "")
        source_ref = str(row.get("source_ref") or "")
        matches = [
            hold for hold in holds
            if str(hold.get("source_candidate_id") or "") == candidate
            and source_ref in {f"arXiv:{value}" for value in _arxiv_ids(hold)}
        ]
        # Candidate ids are reused across shadow runs.  Source-ref matching is
        # therefore mandatory, and any remaining ambiguity fails closed.
        if len(matches) != 1:
            continue
        hold = matches[0]
        out.append({
            "candidate_id": candidate,
            "source_ref": str(row.get("source_ref") or ""),
            "url": str(row.get("url") or ""),
            "declaration_kind": str(row.get("declaration_kind") or ""),
            "declaration_context": "portable-canonical-primary-cache-endpoint",
            "primary_cache_sha256": str(row.get("primary_cache_sha256") or ""),
            "required_unit": _bounded(hold.get("required_unit")),
            "reopen_only_if": _bounded(hold.get("reopen_only_if")),
            "portable_target": True,
            "scientific_authority": False,
        })
    return out


def _merge_portable_release_targets(
    design_state: dict[str, Any],
    local_targets: list[dict[str, Any]],
    no_endpoint: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    portable = _portable_targets_for_holds(design_state, manifest)
    merged: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in portable + local_targets:
        merged[(str(row.get("candidate_id") or ""), str(row.get("source_ref") or ""), str(row.get("url") or ""))] = row
    targeted = {candidate for candidate, _, _ in merged}
    remaining = [row for row in no_endpoint if str(row.get("candidate_id") or "") not in targeted]
    return list(merged.values()), remaining, sum(row.get("portable_target") is True for row in merged.values())


def _portable_observation_target_material(target: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": str(target.get("candidate_id") or "").strip(),
        "candidate_snapshot_sha256": str(target.get("candidate_snapshot_sha256") or "").strip().lower(),
        "source_ref": str(target.get("source_ref") or "").strip(),
        "url": _clean_url(str(target.get("url") or "")),
        "declaration_kind": str(target.get("declaration_kind") or "").strip().upper(),
        "baseline_revision": str(target.get("baseline_revision") or "").strip().lower(),
        "endpoint_provenance_kind": str(target.get("endpoint_provenance_kind") or "").strip().upper(),
        "endpoint_provenance_sha256": str(target.get("endpoint_provenance_sha256") or "").strip().lower(),
    }


def portable_release_observation_target_binding_sha(target: dict[str, Any]) -> str:
    material = _portable_observation_target_material(target)
    return _sha(json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def _portable_observation_target_errors(target: dict[str, Any]) -> list[str]:
    material = _portable_observation_target_material(target)
    errors: list[str] = []
    if not material["candidate_id"]:
        errors.append("candidate id missing")
    if not re.fullmatch(r"[0-9a-f]{64}", material["candidate_snapshot_sha256"]):
        errors.append("candidate snapshot invalid")
    if not re.fullmatch(r"arXiv:\d{4}\.\d+", material["source_ref"], flags=re.I):
        errors.append("source ref invalid")
    if not _acceptable_release_url(material["url"]):
        errors.append("release URL invalid")
    kind = material["declaration_kind"]
    if kind not in {"FIRST_PARTY_REPOSITORY", "FIRST_PARTY_DATASET"}:
        errors.append("portable observation requires support-audited first-party target")
    if kind == "FIRST_PARTY_REPOSITORY" and urlparse(material["url"]).netloc.lower() != "github.com":
        errors.append("repository kind/URL mismatch")
    if kind == "FIRST_PARTY_DATASET" and _huggingface_dataset_id(material["url"]) is None:
        errors.append("dataset kind/URL mismatch")
    if not re.fullmatch(r"[0-9a-f]{40}", material["baseline_revision"]):
        errors.append("baseline revision invalid")
    if material["endpoint_provenance_kind"] != "SUPPORT_AUDIT":
        errors.append("portable observation requires support-audit contract provenance")
    if not re.fullmatch(r"[0-9a-f]{64}", material["endpoint_provenance_sha256"]):
        errors.append("release-watch contract provenance invalid")
    return errors


def build_portable_release_observation_receipt(
    *,
    target: dict[str, Any],
    result: dict[str, Any],
    checked_at: datetime | None = None,
) -> dict[str, Any]:
    target_errors = _portable_observation_target_errors(target)
    if target_errors:
        raise ValueError("invalid portable release-observation target: " + ";".join(target_errors))
    status_code = int(result.get("status_code") or 0)
    fingerprint = str(result.get("fingerprint") or "").strip().lower()
    resolved_revision = str(result.get("resolved_revision") or "").strip().lower()
    fingerprint_version = str(result.get("fingerprint_version") or FINGERPRINT_VERSION).strip()
    artifact_count_raw = result.get("artifact_file_count")
    artifact_file_count = int(artifact_count_raw) if artifact_count_raw is not None else None
    artifact_path_digest = str(result.get("artifact_path_digest") or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
        raise ValueError("portable observation fingerprint invalid")
    if fingerprint_version != FINGERPRINT_VERSION:
        raise ValueError("portable observation fingerprint version stale")
    if 200 <= status_code < 300 and not re.fullmatch(r"[0-9a-f]{40}", resolved_revision):
        raise ValueError("portable observation resolved revision missing")
    if artifact_path_digest and not re.fullmatch(r"[0-9a-f]{64}", artifact_path_digest):
        raise ValueError("portable observation artifact path digest invalid")
    if artifact_file_count is not None and artifact_file_count < 0:
        raise ValueError("portable observation artifact count invalid")
    target_material = _portable_observation_target_material(target)
    observation = {
        "status_code": status_code,
        "fingerprint": fingerprint,
        "surface_nonempty": bool(result.get("surface_nonempty")),
        "artifact_file_count": artifact_file_count,
        "artifact_path_digest": artifact_path_digest,
        "resolved_revision": resolved_revision,
        "fingerprint_version": fingerprint_version,
        "checked_at": _now(checked_at).isoformat(),
    }
    authority = {
        "support_qualification": False,
        "generator_reopen": False,
        "problem_gate": False,
        "method": False,
        "experiment": False,
        "p0": False,
        "gpu": False,
        "scientific": False,
    }
    material = {
        "target_binding": target_material,
        "target_binding_sha256": portable_release_observation_target_binding_sha(target),
        "observation": observation,
        "authority": authority,
        "scientific_authority": False,
    }
    receipt_sha256 = _sha(json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return {
        "schema_version": PORTABLE_OBSERVATIONS_SCHEMA,
        "receipt_kind": "PORTABLE_ZERO_AUTHORITY_RELEASE_OBSERVATION",
        **material,
        "receipt_sha256": receipt_sha256,
    }


def validate_portable_release_observation_receipt(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt.get("schema_version") != PORTABLE_OBSERVATIONS_SCHEMA or receipt.get("receipt_kind") != "PORTABLE_ZERO_AUTHORITY_RELEASE_OBSERVATION":
        errors.append("portable release-observation schema/kind invalid")
    if receipt.get("scientific_authority") is not False:
        errors.append("portable release observation cannot carry scientific authority")
    authority = receipt.get("authority") or {}
    if not isinstance(authority, dict) or not authority or any(value is not False for value in authority.values()):
        errors.append("portable release observation carries non-zero authority")
    target = receipt.get("target_binding") or {}
    errors.extend(_portable_observation_target_errors(target))
    expected_binding = portable_release_observation_target_binding_sha(target) if isinstance(target, dict) else ""
    if receipt.get("target_binding_sha256") != expected_binding:
        errors.append("portable release-observation target binding digest mismatch")
    observation = receipt.get("observation") or {}
    if not isinstance(observation, dict):
        errors.append("portable release observation malformed")
        observation = {}
    if not re.fullmatch(r"[0-9a-f]{64}", str(observation.get("fingerprint") or "")):
        errors.append("portable release-observation fingerprint invalid")
    if str(observation.get("fingerprint_version") or "") != FINGERPRINT_VERSION:
        errors.append("portable release-observation fingerprint version invalid")
    try:
        status_code = int(observation.get("status_code") or 0)
    except (TypeError, ValueError):
        status_code = 0
        errors.append("portable release-observation HTTP status invalid")
    resolved = str(observation.get("resolved_revision") or "").strip().lower()
    if 200 <= status_code < 300 and not re.fullmatch(r"[0-9a-f]{40}", resolved):
        errors.append("portable release-observation resolved revision invalid")
    try:
        datetime.fromisoformat(str(observation.get("checked_at") or "").replace("Z", "+00:00"))
    except ValueError:
        errors.append("portable release-observation checked_at invalid")
    material = {
        "target_binding": target,
        "target_binding_sha256": receipt.get("target_binding_sha256"),
        "observation": observation,
        "authority": authority,
        "scientific_authority": False,
    }
    expected_receipt = _sha(json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if receipt.get("receipt_sha256") != expected_receipt:
        errors.append("portable release-observation receipt digest mismatch")
    forbidden = {"required_unit", "reopen_only_if", "evidence_review", "support_qualified", "scientific_release"}
    if any(key in receipt for key in forbidden) or any(key in target for key in forbidden) or any(key in observation for key in forbidden):
        errors.append("portable release-observation leaks or asserts scientific decision fields")
    return sorted(set(errors))


def build_portable_release_observation_manifest(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [dict(row) for row in receipts]
    for row in rows:
        errors = validate_portable_release_observation_receipt(row)
        if errors:
            raise ValueError("invalid portable release observation: " + ";".join(errors))
    rows.sort(key=lambda row: str(row.get("target_binding_sha256") or ""))
    bindings = [str(row.get("target_binding_sha256") or "") for row in rows]
    if len(bindings) != len(set(bindings)):
        raise ValueError("duplicate portable release-observation target binding")
    manifest_sha256 = _sha(json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return {
        "schema_version": PORTABLE_OBSERVATIONS_SCHEMA,
        "status": "PORTABLE_ZERO_AUTHORITY_RELEASE_OBSERVATIONS_READY",
        "manifest_sha256": manifest_sha256,
        "policy": {
            "scientific_authority": False,
            "observations_only_not_support_evidence": True,
            "receiver_must_match_current_content_addressed_target": True,
            "receiver_reuses_local_release_watch_decision_logic": True,
            "receipt_can_only_request_release_recheck": True,
        },
        "summary": {"receipts": len(rows)},
        "receipts": rows,
        "scientific_authority": False,
    }


def validate_portable_release_observation_manifest(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("schema_version") != PORTABLE_OBSERVATIONS_SCHEMA or state.get("scientific_authority") is not False:
        errors.append("portable release-observation manifest authority/schema invalid")
    policy = state.get("policy") or {}
    if policy.get("scientific_authority") is not False:
        errors.append("portable release-observation manifest policy authority invalid")
    rows = [row for row in state.get("receipts") or [] if isinstance(row, dict)]
    if len(rows) != len(state.get("receipts") or []):
        errors.append("portable release-observation manifest contains malformed rows")
    seen: set[str] = set()
    for row in rows:
        errors.extend(validate_portable_release_observation_receipt(row))
        binding = str(row.get("target_binding_sha256") or "")
        if binding in seen:
            errors.append("portable release-observation manifest duplicates target binding")
        seen.add(binding)
    expected_manifest = _sha(json.dumps(sorted(rows, key=lambda row: str(row.get("target_binding_sha256") or "")), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if state.get("manifest_sha256") != expected_manifest:
        errors.append("portable release-observation manifest digest mismatch")
    return sorted(set(errors))


def load_portable_release_observation_manifest(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(state, dict) or validate_portable_release_observation_manifest(state):
        return {}
    return state


def _portable_observations_for_targets(
    targets: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], int]:
    current = {
        portable_release_observation_target_binding_sha(target): target
        for target in targets
        if not _portable_observation_target_errors(target)
    }
    accepted: dict[str, dict[str, Any]] = {}
    rejected = 0
    for receipt in manifest.get("receipts") or []:
        if not isinstance(receipt, dict) or validate_portable_release_observation_receipt(receipt):
            rejected += 1
            continue
        binding = str(receipt.get("target_binding_sha256") or "")
        target = current.get(binding)
        if target is None or _portable_observation_target_material(target) != receipt.get("target_binding"):
            rejected += 1
            continue
        accepted[binding] = receipt
    return accepted, rejected


def collect_portable_release_observation_manifest(
    *,
    design_state: dict[str, Any] | None = None,
    storage: StorageSettings | None = None,
    fetcher: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    design_state = design_state if design_state is not None else build_search_portfolio_design_adjudication()
    targets, _ = explicit_release_targets(design_state, storage=storage)
    fetch = fetcher or _default_fetcher
    receipts: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for target in targets:
        if _portable_observation_target_errors(target):
            continue
        try:
            result = dict(fetch(target))
            receipts.append(build_portable_release_observation_receipt(target=target, result=result, checked_at=now))
        except Exception as error:
            errors.append({
                "target_binding_sha256": portable_release_observation_target_binding_sha(target),
                "error": f"{type(error).__name__}:{str(error)[:300]}",
            })
    state = build_portable_release_observation_manifest(receipts)
    state["summary"]["eligible_targets"] = len(receipts) + len(errors)
    state["summary"]["collection_errors"] = len(errors)
    state["collection_errors"] = errors
    return state


def write_portable_release_observation_manifest(
    path: Path,
    *,
    design_state: dict[str, Any] | None = None,
    storage: StorageSettings | None = None,
    fetcher: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    state = collect_portable_release_observation_manifest(design_state=design_state, storage=storage, fetcher=fetcher, now=now)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
    return state


def _huggingface_dataset_api(url: str) -> str | None:
    repo_id = _huggingface_dataset_id(url)
    if not repo_id:
        return None
    return f"https://huggingface.co/api/datasets/{repo_id}"


def _github_repo_api(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.netloc.lower() != "github.com":
        return None
    parts = [x for x in parsed.path.strip("/").split("/") if x]
    if len(parts) < 2:
        return None
    return f"https://api.github.com/repos/{parts[0]}/{parts[1]}"


def _is_release_artifact_path(path: str) -> bool:
    value = str(path or "").strip("/")
    name = value.rsplit("/", 1)[-1].lower()
    if not value or name in {".gitignore", ".gitattributes", ".github"}:
        return False
    if name.startswith(("readme", "license", "licence", "citation", "code_of_conduct", "contributing")):
        return False
    if name.endswith((".md", ".rst", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")):
        return False
    return True


def _default_fetcher(target: dict[str, Any]) -> dict[str, Any]:
    url = str(target.get("url") or "")
    hf_api = _huggingface_dataset_api(url)
    api = _github_repo_api(url)
    headers = {"User-Agent": "Agent-Self-Evolution-Observatory/release-watch", "Accept": "application/json"}
    if hf_api:
        response = requests.get(hf_api, timeout=20.0, headers=headers, params={"full": "full"})
        status = int(response.status_code)
        if status != 200:
            material = {"status_code": status, "endpoint": url, "fingerprint_version": FINGERPRINT_VERSION}
            return {"status_code": status, "fingerprint": _sha(json.dumps(material, sort_keys=True, separators=(",", ":"))), "surface_nonempty": False, "artifact_file_count": 0, "fingerprint_version": FINGERPRINT_VERSION, "resolved_endpoint": hf_api}
        payload = response.json() or {}
        resolved_revision = str(payload.get("sha") or "").strip().lower()
        if not re.fullmatch(r"[0-9a-f]{40}", resolved_revision):
            raise RuntimeError("huggingface-dataset-revision-invalid")
        artifacts = sorted(
            str(row.get("rfilename") or "").strip()
            for row in payload.get("siblings") or []
            if isinstance(row, dict) and str(row.get("rfilename") or "").strip()
        )
        artifact_digest = _sha("\n".join(artifacts))
        material = {
            "status_code": status,
            "endpoint": url,
            "resolved_revision": resolved_revision,
            "artifact_file_count": len(artifacts),
            "artifact_path_digest": artifact_digest,
            "fingerprint_version": FINGERPRINT_VERSION,
        }
        fingerprint = _sha(json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return {
            "status_code": status,
            "fingerprint": fingerprint,
            "surface_nonempty": bool(artifacts),
            "artifact_file_count": len(artifacts),
            "artifact_path_digest": artifact_digest,
            "fingerprint_version": FINGERPRINT_VERSION,
            "resolved_endpoint": hf_api,
            "resolved_revision": resolved_revision,
        }
    headers["Accept"] = "application/vnd.github+json"
    if api:
        response = requests.get(api, timeout=20.0, headers=headers)
        status = int(response.status_code)
        if status != 200:
            material = {"status_code": status, "endpoint": url, "fingerprint_version": FINGERPRINT_VERSION}
            return {"status_code": status, "fingerprint": _sha(json.dumps(material, sort_keys=True, separators=(",", ":"))), "surface_nonempty": False, "artifact_file_count": 0, "fingerprint_version": FINGERPRINT_VERSION, "resolved_endpoint": api}
        payload = response.json()
        default_branch = str(payload.get("default_branch") or "main")
        commit_url = f"{api}/commits/{default_branch}"
        commit_response = requests.get(commit_url, timeout=20.0, headers=headers)
        if int(commit_response.status_code) != 200:
            raise RuntimeError(f"github-commit-http-{int(commit_response.status_code)}")
        resolved_revision = str((commit_response.json() or {}).get("sha") or "").strip().lower()
        if not re.fullmatch(r"[0-9a-f]{40}", resolved_revision):
            raise RuntimeError("github-default-branch-revision-invalid")
        tree_url = f"{api}/git/trees/{default_branch}?recursive=1"
        tree_response = requests.get(tree_url, timeout=20.0, headers=headers)
        if int(tree_response.status_code) != 200:
            raise RuntimeError(f"github-tree-http-{int(tree_response.status_code)}")
        tree_payload = tree_response.json()
        artifacts = sorted(
            (str(row.get("path") or ""), str(row.get("sha") or ""))
            for row in tree_payload.get("tree") or []
            if row.get("type") == "blob" and _is_release_artifact_path(str(row.get("path") or ""))
        )
        artifact_digest = _sha("\n".join(f"{path}:{blob_sha}" for path, blob_sha in artifacts))
        material = {"status_code": status, "endpoint": url, "default_branch": default_branch, "resolved_revision": resolved_revision, "artifact_file_count": len(artifacts), "artifact_blob_digest": artifact_digest, "fingerprint_version": FINGERPRINT_VERSION}
        fingerprint = _sha(json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return {"status_code": status, "fingerprint": fingerprint, "surface_nonempty": bool(artifacts), "artifact_file_count": len(artifacts), "artifact_path_digest": _sha("\n".join(path for path, _ in artifacts)), "fingerprint_version": FINGERPRINT_VERSION, "resolved_endpoint": api, "resolved_revision": resolved_revision}
    if urlparse(url).netloc.lower().endswith(".github.io"):
        response = requests.head(url, timeout=20.0, headers=headers, allow_redirects=True)
        status = int(response.status_code)
        response_headers = getattr(response, "headers", {}) or {}
        material = {
            "status_code": status,
            "endpoint": url,
            "resolved_endpoint": str(getattr(response, "url", url) or url),
            "etag": str(response_headers.get("ETag") or response_headers.get("etag") or ""),
            "last_modified": str(response_headers.get("Last-Modified") or response_headers.get("last-modified") or ""),
            "content_length": str(response_headers.get("Content-Length") or response_headers.get("content-length") or ""),
            "fingerprint_version": FINGERPRINT_VERSION,
        }
        fingerprint = _sha(json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        surface_nonempty = 200 <= status < 300 and any(material[key] for key in ("etag", "last_modified", "content_length"))
        return {"status_code": status, "fingerprint": fingerprint, "surface_nonempty": surface_nonempty, "artifact_file_count": None, "fingerprint_version": FINGERPRINT_VERSION, "resolved_endpoint": material["resolved_endpoint"]}
    response = requests.get(url, timeout=20.0, headers=headers, stream=True)
    status = int(response.status_code)
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=65536):
        if not chunk:
            continue
        take = chunk[: max(0, MAX_PAGE_BYTES - total)]
        chunks.append(take)
        total += len(take)
        if total >= MAX_PAGE_BYTES:
            break
    body = b"".join(chunks)
    return {"status_code": status, "fingerprint": _sha(body), "surface_nonempty": bool(body.strip()), "artifact_file_count": None, "fingerprint_version": FINGERPRINT_VERSION, "resolved_endpoint": url}


def _refresh_no_endpoint_primary_declarations(
    no_endpoint: list[dict[str, Any]],
    *,
    storage: StorageSettings,
    ledger: dict[str, Any],
    requester: Callable[..., Any] | None,
    now: datetime,
    cooldown_days: float = PRIMARY_DECLARATION_REFRESH_COOLDOWN_DAYS,
    max_refreshes: int = MAX_PRIMARY_DECLARATION_REFRESHES,
    rate_limit_state_path: Path | None = None,
) -> dict[str, Any]:
    fetch = requester or requests.get
    refreshes = dict(ledger.get("primary_declaration_refreshes") or {})
    cache_root = _primary_root(storage)
    cache_root.mkdir(parents=True, exist_ok=True)
    rate_limit_state_path = rate_limit_state_path or (storage.data_root / "paper-first-problem-discovery" / "arxiv-rate-limit-state.json")
    active_rate_limit = _load_arxiv_rate_limit_state(rate_limit_state_path, now=now)
    if active_rate_limit:
        return {
            "checked": 0,
            "changed": 0,
            "skipped_cooldown": 0,
            "rate_limited": len(no_endpoint),
            "errors": 0,
            "refreshed_refs": [],
            "refreshes": refreshes,
            "rate_limit_blocked_until": active_rate_limit.get("blocked_until"),
        }
    checked = changed = skipped = errors = 0
    refreshed_refs: list[str] = []
    budget = max(0, int(max_refreshes))
    for item in no_endpoint:
        if checked >= budget:
            break
        refs = [str(x) for x in item.get("source_refs") or [] if str(x).startswith("arXiv:")]
        if not refs:
            continue
        ref = refs[0]
        arxiv_id = ref.split(":", 1)[1]
        previous = refreshes.get(ref) or {}
        previous_checked = str(previous.get("checked_at") or "")
        if previous_checked:
            try:
                if now - datetime.fromisoformat(previous_checked.replace("Z", "+00:00")) < timedelta(days=max(0.0, cooldown_days)):
                    skipped += 1
                    continue
            except ValueError:
                pass
        response = fetch(
            f"https://arxiv.org/abs/{arxiv_id}",
            timeout=25.0,
            headers={"User-Agent": "Agent-Self-Evolution-Observatory/support-release-primary-refresh"},
        )
        status = int(getattr(response, "status_code", 200))
        checked += 1
        if status == 429:
            rate_state = _write_arxiv_rate_limit_state(
                rate_limit_state_path,
                now=now,
                retry_after_seconds=_arxiv_retry_after_seconds(response, DEFAULT_ARXIV_RATE_LIMIT_COOLDOWN_SECONDS),
            )
            return {
                "checked": checked,
                "changed": changed,
                "skipped_cooldown": skipped,
                "rate_limited": max(1, len(no_endpoint) - checked + 1),
                "errors": errors,
                "refreshed_refs": refreshed_refs,
                "refreshes": refreshes,
                "rate_limit_blocked_until": rate_state.get("blocked_until"),
            }
        if status >= 400:
            errors += 1
            refreshes[ref] = {"checked_at": now.isoformat(), "http_status": status, "scientific_authority": False}
            continue
        raw_text = str(getattr(response, "text", "") or "")
        parsed = parse_arxiv_page(raw_text)
        if not parsed.get("title") or not parsed.get("abstract"):
            errors += 1
            refreshes[ref] = {"checked_at": now.isoformat(), "http_status": status, "error": "primary-page-missing-title-or-abstract", "scientific_authority": False}
            continue
        raw_bytes = raw_text.encode("utf-8")
        source_sha = _sha(raw_bytes)
        safe_id = re.sub(r"[^0-9A-Za-z._-]+", "_", arxiv_id)
        path = cache_root / f"arxiv-{safe_id}-{source_sha[:12]}.html"
        existed = path.exists()
        if not existed:
            path.write_bytes(raw_bytes)
            changed += 1
        refreshed_refs.append(ref)
        refreshes[ref] = {
            "checked_at": now.isoformat(),
            "http_status": status,
            "primary_sha256": source_sha,
            "content_changed": not existed,
            "scientific_authority": False,
        }
    return {
        "checked": checked,
        "changed": changed,
        "skipped_cooldown": skipped,
        "rate_limited": 0,
        "errors": errors,
        "refreshed_refs": refreshed_refs,
        "refreshes": refreshes,
        "rate_limit_blocked_until": None,
    }


def _load_ledger(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": WATCH_SCHEMA, "observations": {}, "scientific_authority": False}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {"schema_version": WATCH_SCHEMA, "observations": {}, "scientific_authority": False}
    except Exception:
        return {"schema_version": WATCH_SCHEMA, "observations": {}, "scientific_authority": False}


def load_private_support_release_watch(
    *,
    storage: StorageSettings | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    path = path or (_watch_root(storage) / "last-run.json")
    if not path.exists():
        return {"schema_version": WATCH_SCHEMA, "status": "NOT_RUN", "policy": {"scientific_authority": False}, "summary": {}, "rows": [], "scientific_authority": False}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {"schema_version": WATCH_SCHEMA, "status": "STATE_INVALID", "policy": {"scientific_authority": False}, "summary": {}, "rows": [], "scientific_authority": False}
    except Exception:
        return {"schema_version": WATCH_SCHEMA, "status": "STATE_UNREADABLE", "policy": {"scientific_authority": False}, "summary": {}, "rows": [], "scientific_authority": False}


def public_support_release_watch_summary(state: dict[str, Any]) -> dict[str, Any]:
    rows = [row for row in state.get("rows") or [] if isinstance(row, dict)]
    status_counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status") or "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1
    summary = state.get("summary") or {}
    safe_summary_keys = (
        "support_holds", "explicit_release_targets", "no_explicit_endpoint", "checked", "skipped_cooldown",
        "provider_errors", "recheck_required", "support_qualified", "generator_reopen_authorized", "problem_gate_authorized",
        "primary_declaration_refresh_checked", "primary_declaration_refresh_changed", "primary_declaration_refresh_skipped_cooldown",
        "primary_declaration_refresh_rate_limited", "primary_declaration_refresh_errors", "portable_release_targets_used",
        "portable_release_observations_used", "portable_release_observations_rejected", "portable_release_observations_stale",
    )
    return {
        "schema_version": WATCH_SCHEMA,
        "status": str(state.get("status") or "NOT_RUN"),
        "policy": {
            "scientific_authority": False,
            "primary_declared_or_support_audited_release_endpoints_only": True,
            "support_audited_pre_f0_repository_targets_allowed": True,
            "support_audited_pre_f0_first_party_dataset_targets_allowed": True,
            "pre_f0_release_change_only_holds_included": True,
            "related_work_repository_links_are_not_watch_targets": True,
            "release_surface_change_only_requests_recheck": True,
            "release_watch_cannot_mark_support_qualified": True,
            "release_watch_cannot_reopen_generator_or_problem_gate": True,
            "release_watch_has_zero_source_exposure_effect": True,
            "network_checks_are_cooldown_bounded": True,
            "no_endpoint_primary_refresh_is_primary_source_only": True,
            "primary_declaration_refresh_has_zero_source_exposure_effect": True,
            "primary_declaration_refresh_cannot_qualify_support": True,
            "portable_release_targets_are_endpoint_handoff_only": True,
            "portable_release_targets_cannot_qualify_support_or_reopen": True,
            "portable_release_observations_are_zero_authority_endpoint_observations_only": True,
            "portable_release_observations_must_match_current_content_addressed_target": True,
            "portable_release_observations_reuse_local_watch_decision_logic": True,
            "public_summary_excludes_urls_refs_required_units_and_private_paths": True,
        },
        "summary": {key: summary[key] for key in safe_summary_keys if key in summary},
        "status_counts": status_counts,
        "scientific_authority": False,
    }


def run_support_release_watch(
    *,
    storage: StorageSettings | None = None,
    design_state: dict[str, Any] | None = None,
    fetcher: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    primary_requester: Callable[..., Any] | None = None,
    now: datetime | None = None,
    cooldown_days: float = DEFAULT_COOLDOWN_DAYS,
    primary_refresh_cooldown_days: float = PRIMARY_DECLARATION_REFRESH_COOLDOWN_DAYS,
    max_primary_refreshes: int = MAX_PRIMARY_DECLARATION_REFRESHES,
    arxiv_rate_limit_state_path: Path | None = None,
    ledger_path: Path | None = None,
    portable_targets_path: Path = DEFAULT_PORTABLE_TARGETS_JSON,
    portable_observations_path: Path | None = None,
    write_ledger: bool = True,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    design_state = design_state if design_state is not None else build_search_portfolio_design_adjudication()
    current = _now(now)
    ledger_path = ledger_path or (_watch_root(storage) / "latest.json")
    ledger = _load_ledger(ledger_path)
    observations = dict(ledger.get("observations") or {})
    targets, no_endpoint = explicit_release_targets(design_state, storage=storage)
    portable_manifest = load_portable_release_target_manifest(portable_targets_path)
    targets, no_endpoint, portable_used = _merge_portable_release_targets(design_state, targets, no_endpoint, portable_manifest)
    portable_observation_manifest = load_portable_release_observation_manifest(portable_observations_path)
    portable_observations, portable_observation_rejected = _portable_observations_for_targets(targets, portable_observation_manifest)
    primary_refresh = _refresh_no_endpoint_primary_declarations(
        no_endpoint,
        storage=storage,
        ledger=ledger,
        requester=primary_requester,
        now=current,
        cooldown_days=primary_refresh_cooldown_days,
        max_refreshes=max_primary_refreshes,
        rate_limit_state_path=arxiv_rate_limit_state_path,
    )
    ledger["primary_declaration_refreshes"] = primary_refresh["refreshes"]
    if primary_refresh["checked"] or primary_refresh["changed"]:
        targets, no_endpoint = explicit_release_targets(design_state, storage=storage)
        targets, no_endpoint, portable_used = _merge_portable_release_targets(design_state, targets, no_endpoint, portable_manifest)
        portable_observations, portable_observation_rejected = _portable_observations_for_targets(targets, portable_observation_manifest)
    fetch = fetcher or _default_fetcher
    rows: list[dict[str, Any]] = []
    checked = skipped = provider_errors = recheck = 0
    portable_observation_used = portable_observation_stale = 0
    for target in targets:
        key = _sha(f"{target['candidate_id']}\n{target['url']}")
        previous = observations.get(key) or {}
        previous_checked = str(previous.get("checked_at") or "")
        target_binding_sha = portable_release_observation_target_binding_sha(target) if not _portable_observation_target_errors(target) else ""
        portable_receipt = portable_observations.get(target_binding_sha) if target_binding_sha else None
        if portable_receipt and previous_checked:
            try:
                receipt_checked = datetime.fromisoformat(str((portable_receipt.get("observation") or {}).get("checked_at") or "").replace("Z", "+00:00"))
                prior_checked = datetime.fromisoformat(previous_checked.replace("Z", "+00:00"))
                if receipt_checked <= prior_checked:
                    portable_receipt = None
                    portable_observation_stale += 1
            except ValueError:
                portable_receipt = None
                portable_observation_stale += 1
        cooldown = False
        if portable_receipt is None and previous_checked and str(previous.get("fingerprint_version") or "") == FINGERPRINT_VERSION:
            try:
                cooldown = current - datetime.fromisoformat(previous_checked.replace("Z", "+00:00")) < timedelta(days=max(0.0, cooldown_days))
            except ValueError:
                cooldown = False
        if cooldown:
            skipped += 1
            rows.append({**target, "status": "SKIPPED_COOLDOWN", "previous_status": previous.get("status"), "scientific_authority": False})
            continue
        try:
            if portable_receipt is not None:
                portable_observation_used += 1
                observation = dict(portable_receipt.get("observation") or {})
                result = {
                    "status_code": observation.get("status_code"),
                    "fingerprint": observation.get("fingerprint"),
                    "surface_nonempty": observation.get("surface_nonempty"),
                    "artifact_file_count": observation.get("artifact_file_count"),
                    "artifact_path_digest": observation.get("artifact_path_digest"),
                    "resolved_revision": observation.get("resolved_revision"),
                    "fingerprint_version": observation.get("fingerprint_version"),
                }
                observation_source = "PORTABLE_ZERO_AUTHORITY_RELEASE_OBSERVATION"
                observation_checked_at = str(observation.get("checked_at") or current.isoformat())
                receipt_sha256 = str(portable_receipt.get("receipt_sha256") or "")
            else:
                result = dict(fetch(target))
                observation_source = "LOCAL_RELEASE_WATCH_FETCH"
                observation_checked_at = current.isoformat()
                receipt_sha256 = ""
            checked += 1
            status_code = int(result.get("status_code") or 0)
            fingerprint = str(result.get("fingerprint") or "")
            if len(fingerprint) != 64:
                raise ValueError("release-surface-fingerprint-invalid")
            previous_version = str(previous.get("fingerprint_version") or "")
            result_version = str(result.get("fingerprint_version") or FINGERPRINT_VERSION)
            prior_fingerprint = str(previous.get("fingerprint") or "") if previous_version == result_version else ""
            surface_nonempty = bool(result.get("surface_nonempty"))
            artifact_count_raw = result.get("artifact_file_count")
            artifact_file_count = int(artifact_count_raw) if artifact_count_raw is not None else (1 if surface_nonempty else 0)
            baseline_revision = str(target.get("baseline_revision") or "").strip().lower()
            resolved_revision = str(result.get("resolved_revision") or "").strip().lower()
            revision_bound = bool(re.fullmatch(r"[0-9a-f]{40}", baseline_revision))
            resolved_revision_valid = bool(re.fullmatch(r"[0-9a-f]{40}", resolved_revision))
            if revision_bound and 200 <= status_code < 300 and not resolved_revision_valid:
                raise ValueError("release-watch-resolved-revision-missing-for-bound-target")
            if revision_bound and 200 <= status_code < 300:
                status = "NO_RELEASE_CHANGE" if resolved_revision == baseline_revision else "RECHECK_REQUIRED_RELEASE_CHANGED"
            elif target["declaration_kind"] == "FUTURE_CODE_RELEASE" and 200 <= status_code < 300 and artifact_file_count <= 0:
                status = "WAITING_RELEASE_ARTIFACTS"
            elif target["declaration_kind"] == "FUTURE_CODE_RELEASE" and not prior_fingerprint and 200 <= status_code < 300:
                status = "RECHECK_REQUIRED_NEW_RELEASE_SURFACE"
            elif prior_fingerprint and fingerprint != prior_fingerprint:
                status = "RECHECK_REQUIRED_RELEASE_CHANGED"
            elif 200 <= status_code < 300:
                status = "BASELINE_CAPTURED" if not prior_fingerprint else "NO_RELEASE_CHANGE"
            else:
                status = "WAITING_RELEASE_ENDPOINT"
            if status.startswith("RECHECK_REQUIRED"):
                recheck += 1
            row = {
                **target,
                "status": status,
                "http_status": status_code,
                "fingerprint": fingerprint,
                "previous_fingerprint": prior_fingerprint,
                "surface_nonempty": surface_nonempty,
                "artifact_file_count": artifact_file_count,
                "baseline_revision": baseline_revision,
                "resolved_revision": resolved_revision,
                "fingerprint_version": result_version,
                "checked_at": observation_checked_at,
                "observation_source": observation_source,
                "portable_observation_receipt_sha256": receipt_sha256,
                "scientific_authority": False,
            }
            observations[key] = {k: row[k] for k in ("candidate_id", "url", "declaration_kind", "status", "http_status", "fingerprint", "baseline_revision", "resolved_revision", "fingerprint_version", "checked_at", "observation_source", "portable_observation_receipt_sha256", "scientific_authority")}
            rows.append(row)
        except Exception as error:
            provider_errors += 1
            rows.append({**target, "status": "RELEASE_WATCH_PROVIDER_ERROR", "error": f"{type(error).__name__}:{str(error)[:300]}", "scientific_authority": False})
    rows.extend(no_endpoint)
    state = {
        "schema_version": WATCH_SCHEMA,
        "generated_at": current.isoformat(),
        "status": "SUPPORT_RELEASE_WATCH_COMPLETE" if provider_errors == 0 else "SUPPORT_RELEASE_WATCH_PARTIAL",
        "policy": {
            "scientific_authority": False,
            "primary_declared_or_support_audited_release_endpoints_only": True,
            "support_audited_pre_f0_repository_targets_allowed": True,
            "support_audited_pre_f0_first_party_dataset_targets_allowed": True,
            "pre_f0_release_change_only_holds_included": True,
            "related_work_repository_links_are_not_watch_targets": True,
            "release_surface_change_only_requests_recheck": True,
            "release_watch_cannot_mark_support_qualified": True,
            "release_watch_cannot_reopen_generator_or_problem_gate": True,
            "release_watch_has_zero_source_exposure_effect": True,
            "network_checks_are_cooldown_bounded": True,
            "no_endpoint_primary_refresh_is_primary_source_only": True,
            "primary_declaration_refresh_has_zero_source_exposure_effect": True,
            "primary_declaration_refresh_cannot_qualify_support": True,
            "portable_release_targets_are_endpoint_handoff_only": True,
            "portable_release_targets_cannot_qualify_support_or_reopen": True,
            "portable_release_observations_are_zero_authority_endpoint_observations_only": True,
            "portable_release_observations_must_match_current_content_addressed_target": True,
            "portable_release_observations_reuse_local_watch_decision_logic": True,
            "primary_declaration_refresh_max_per_run": int(max_primary_refreshes),
            "primary_declaration_refresh_cooldown_days": float(primary_refresh_cooldown_days),
            "github_release_fingerprint_ignores_doc_only_churn": True,
            "huggingface_dataset_targets_use_official_revision_and_file_manifest": True,
            "revision_bound_targets_recheck_on_any_commit_drift": True,
            "release_surface_fingerprint_version": FINGERPRINT_VERSION,
            "cooldown_days": float(cooldown_days),
        },
        "summary": {
            "support_holds": len(_support_holds(design_state, storage=storage)),
            "explicit_release_targets": len(targets),
            "no_explicit_endpoint": len(no_endpoint),
            "checked": checked,
            "skipped_cooldown": skipped,
            "provider_errors": provider_errors,
            "recheck_required": recheck,
            "support_qualified": 0,
            "generator_reopen_authorized": 0,
            "problem_gate_authorized": 0,
            "primary_declaration_refresh_checked": int(primary_refresh["checked"]),
            "primary_declaration_refresh_changed": int(primary_refresh["changed"]),
            "primary_declaration_refresh_skipped_cooldown": int(primary_refresh["skipped_cooldown"]),
            "primary_declaration_refresh_rate_limited": int(primary_refresh["rate_limited"]),
            "primary_declaration_refresh_errors": int(primary_refresh["errors"]),
            "portable_release_targets_used": int(portable_used),
            "portable_release_observations_used": int(portable_observation_used),
            "portable_release_observations_rejected": int(portable_observation_rejected),
            "portable_release_observations_stale": int(portable_observation_stale),
        },
        "rows": rows,
        "scientific_authority": False,
    }
    if write_ledger:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        watch_root = _watch_root(storage)
        watch_root.mkdir(parents=True, exist_ok=True)
        ledger_payload = {"schema_version": WATCH_SCHEMA, "updated_at": current.isoformat(), "observations": observations, "primary_declaration_refreshes": primary_refresh["refreshes"], "scientific_authority": False}
        ledger_path.write_text(json.dumps(ledger_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (watch_root / "last-run.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state
