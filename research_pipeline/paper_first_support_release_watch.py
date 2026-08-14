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

from .config import StorageSettings
from .paper_first_search_portfolio_design_adjudication import build_search_portfolio_design_adjudication

WATCH_SCHEMA = "1.0"
FINGERPRINT_VERSION = "release-surface-v2"
DEFAULT_COOLDOWN_DAYS = 7.0
MAX_PAGE_BYTES = 1_000_000


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
    memory = design_state.get("shadow_dead_end_memory") or {}
    rows = memory.get("blocked_objects") or []
    return [
        dict(row)
        for row in rows
        if isinstance(row, dict)
        and str(row.get("disposition") or "") == "HOLD_SUPPORT_UNAVAILABLE"
        and str(row.get("basin") or "").startswith("near-miss-terminal-support-hold-")
    ]


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
        dedup: dict[tuple[str, str], dict[str, Any]] = {}
        for row in found:
            dedup[(row["candidate_id"], row["url"])] = row
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


def _load_ledger(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": WATCH_SCHEMA, "observations": {}, "scientific_authority": False}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {"schema_version": WATCH_SCHEMA, "observations": {}, "scientific_authority": False}
    except Exception:
        return {"schema_version": WATCH_SCHEMA, "observations": {}, "scientific_authority": False}


def run_support_release_watch(
    *,
    storage: StorageSettings | None = None,
    design_state: dict[str, Any] | None = None,
    fetcher: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    now: datetime | None = None,
    cooldown_days: float = DEFAULT_COOLDOWN_DAYS,
    ledger_path: Path | None = None,
    write_ledger: bool = True,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    design_state = design_state if design_state is not None else build_search_portfolio_design_adjudication()
    current = _now(now)
    ledger_path = ledger_path or (_watch_root(storage) / "latest.json")
    ledger = _load_ledger(ledger_path)
    observations = dict(ledger.get("observations") or {})
    targets, no_endpoint = explicit_release_targets(design_state, storage=storage)
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
        },
        "rows": rows,
        "scientific_authority": False,
    }
    if write_ledger:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        watch_root = _watch_root(storage)
        watch_root.mkdir(parents=True, exist_ok=True)
        ledger_payload = {"schema_version": WATCH_SCHEMA, "updated_at": current.isoformat(), "observations": observations, "scientific_authority": False}
        ledger_path.write_text(json.dumps(ledger_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (watch_root / "last-run.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state
