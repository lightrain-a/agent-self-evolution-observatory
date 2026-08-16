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


def _terminal_support_holds(design_state: dict[str, Any]) -> list[dict[str, Any]]:
    """Return unresolved terminal support holds across legacy and split memory.

    Support-unavailable rows became reopenable ``hold_objects`` when persistent
    search memory split scientific dead ends from operational holds.  Older
    states may still carry the same rows in ``blocked_objects``.  Read both,
    reject any row certified as a scientific dead end, and deduplicate by its
    provenance-bearing terminal-hold identity rather than candidate id alone
    (shadow candidate ids are reused across runs).
    """
    memory = design_state.get("shadow_dead_end_memory") or {}
    rows = list(memory.get("blocked_objects") or []) + list(memory.get("hold_objects") or [])
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("disposition") or "") != "HOLD_SUPPORT_UNAVAILABLE":
            continue
        basin = str(row.get("basin") or "")
        if not basin.startswith("near-miss-terminal-support-hold-") or row.get("dead_end_certified") is True:
            continue
        key = (str(row.get("source_candidate_id") or ""), str(row.get("source_run_id") or ""), basin)
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(row))
    return out


def _arxiv_ids(row: dict[str, Any]) -> list[str]:
    refs = list(row.get("evidence_basis") or []) + list(row.get("current_source_refs") or [])
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
    for hold in _terminal_support_holds(design_state):
        candidate_id = str(hold.get("source_candidate_id") or "")
        found: list[dict[str, Any]] = []
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
                        "required_unit": _bounded(hold.get("required_unit")),
                        "reopen_only_if": _bounded(hold.get("reopen_only_if")),
                        "scientific_authority": False,
                    })
        dedup: dict[tuple[str, str, str], dict[str, Any]] = {}
        for row in found:
            dedup[(row["candidate_id"], row["source_ref"], row["url"])] = row
        if dedup:
            targets.extend(dedup.values())
        else:
            no_endpoint.append({
                "candidate_id": candidate_id,
                "source_refs": [f"arXiv:{x}" for x in _arxiv_ids(hold)],
                "status": "NO_EXPLICIT_AUTHOR_RELEASE_ENDPOINT",
                "required_unit": _bounded(hold.get("required_unit")),
                "reopen_only_if": _bounded(hold.get("reopen_only_if")),
                "scientific_authority": False,
            })
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
    api = _github_repo_api(url)
    headers = {"User-Agent": "Agent-Self-Evolution-Observatory/release-watch", "Accept": "application/vnd.github+json"}
    if api:
        response = requests.get(api, timeout=20.0, headers=headers)
        status = int(response.status_code)
        if status != 200:
            material = {"status_code": status, "endpoint": url, "fingerprint_version": FINGERPRINT_VERSION}
            return {"status_code": status, "fingerprint": _sha(json.dumps(material, sort_keys=True, separators=(",", ":"))), "surface_nonempty": False, "artifact_file_count": 0, "fingerprint_version": FINGERPRINT_VERSION, "resolved_endpoint": api}
        payload = response.json()
        default_branch = str(payload.get("default_branch") or "main")
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
        material = {"status_code": status, "endpoint": url, "default_branch": default_branch, "artifact_file_count": len(artifacts), "artifact_blob_digest": artifact_digest, "fingerprint_version": FINGERPRINT_VERSION}
        fingerprint = _sha(json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return {"status_code": status, "fingerprint": fingerprint, "surface_nonempty": bool(artifacts), "artifact_file_count": len(artifacts), "artifact_path_digest": _sha("\n".join(path for path, _ in artifacts)), "fingerprint_version": FINGERPRINT_VERSION, "resolved_endpoint": api}
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
    )
    return {
        "schema_version": WATCH_SCHEMA,
        "status": str(state.get("status") or "NOT_RUN"),
        "policy": {
            "scientific_authority": False,
            "primary_declared_release_endpoints_only": True,
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
    fetch = fetcher or _default_fetcher
    rows: list[dict[str, Any]] = []
    checked = skipped = provider_errors = recheck = 0
    for target in targets:
        key = _sha(f"{target['candidate_id']}\n{target['url']}")
        previous = observations.get(key) or {}
        previous_checked = str(previous.get("checked_at") or "")
        cooldown = False
        if previous_checked and str(previous.get("fingerprint_version") or "") == FINGERPRINT_VERSION:
            try:
                cooldown = current - datetime.fromisoformat(previous_checked.replace("Z", "+00:00")) < timedelta(days=max(0.0, cooldown_days))
            except ValueError:
                cooldown = False
        if cooldown:
            skipped += 1
            rows.append({**target, "status": "SKIPPED_COOLDOWN", "previous_status": previous.get("status"), "scientific_authority": False})
            continue
        try:
            result = dict(fetch(target))
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
            if target["declaration_kind"] == "FUTURE_CODE_RELEASE" and 200 <= status_code < 300 and artifact_file_count <= 0:
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
                "fingerprint_version": result_version,
                "checked_at": current.isoformat(),
                "scientific_authority": False,
            }
            observations[key] = {k: row[k] for k in ("candidate_id", "url", "declaration_kind", "status", "http_status", "fingerprint", "fingerprint_version", "checked_at", "scientific_authority")}
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
            "primary_declared_release_endpoints_only": True,
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
            "primary_declaration_refresh_max_per_run": int(max_primary_refreshes),
            "primary_declaration_refresh_cooldown_days": float(primary_refresh_cooldown_days),
            "github_release_fingerprint_ignores_doc_only_churn": True,
            "release_surface_fingerprint_version": FINGERPRINT_VERSION,
            "cooldown_days": float(cooldown_days),
        },
        "summary": {
            "support_holds": len(_terminal_support_holds(design_state)),
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
