from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .config import StorageSettings
from .paper_first_primary_evidence import (
    _default_requester,
    _meta_content,
    extract_empirical_fact_candidates,
    extract_typed_evidence_candidates,
    parse_arxiv_page,
)
from .paper_first_problem_generator import load_problem_generator_state
from .paper_first_relation_coverage import portable_review_receipts, relation_universe_digest
from .paper_first_scientific_object_ontology import reviewed_primary_cache_records

DEFAULT_MAX_PRIMARY_PER_RUN = 32
DEFAULT_MAX_FULLTEXT_PER_RUN = 4
DEFAULT_FAILURE_COOLDOWN_HOURS = 24.0
DEFAULT_MIN_INTERVAL_SECONDS = 0.5
DEFAULT_REPLAY_GUARD_MINUTES = 15.0
Requester = Callable[..., Any]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _parse_time(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
    except ValueError:
        return None
    return (parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)


def _root(storage: StorageSettings) -> Path:
    return storage.data_root / "paper-first-problem-discovery"


def _state_path(storage: StorageSettings) -> Path:
    return _root(storage) / "relation-cache-backfill-state.json"


def _cache_dir(storage: StorageSettings) -> Path:
    return _root(storage) / "primary-sources"


def _load_state(storage: StorageSettings) -> dict[str, Any]:
    path = _state_path(storage)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_state(storage: StorageSettings, state: dict[str, Any]) -> None:
    path = _state_path(storage)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _recent_same_universe_attempt(previous: dict[str, Any], *, digest: str, now: datetime, guard_minutes: float) -> bool:
    if guard_minutes <= 0 or str(previous.get("relation_universe_digest") or "") != digest:
        return False
    started = _parse_time(previous.get("run_started_at"))
    if started is None:
        return False
    return 0 <= (now - started).total_seconds() <= guard_minutes * 60


def _refs_from_files(cache_dir: Path, *, fulltext: bool) -> set[str]:
    pattern = "arxiv-full-*.html" if fulltext else "arxiv-*.html"
    prefix = "arxiv-full-" if fulltext else "arxiv-"
    refs: set[str] = set()
    for path in cache_dir.glob(pattern):
        if not fulltext and path.name.startswith("arxiv-full-"):
            continue
        match = re.match(rf"{re.escape(prefix)}(\d{{4}}\.\d+)-", path.name)
        if match:
            refs.add(f"arXiv:{match.group(1)}")
    return refs


def _target_refs(generator_state: dict[str, Any]) -> set[str]:
    return {ref for row in portable_review_receipts(generator_state) for ref in row.get("source_refs") or []}


def _recent_failures(previous: dict[str, Any], *, now: datetime, cooldown_hours: float) -> set[str]:
    result: set[str] = set()
    for row in previous.get("primary_failures") or []:
        if not isinstance(row, dict):
            continue
        when = _parse_time(row.get("failed_at"))
        ref = str(row.get("ref") or "")
        if when is not None and ref and (now - when).total_seconds() <= cooldown_hours * 3600:
            result.add(ref)
    return result


def _throttle(last_fetch: float | None, min_interval_seconds: float) -> float:
    if last_fetch is not None and min_interval_seconds > 0:
        wait = min_interval_seconds - (time.monotonic() - last_fetch)
        if wait > 0:
            time.sleep(wait)
    return time.monotonic()


def _arxiv_id(ref: str) -> str:
    if not ref.startswith("arXiv:"):
        raise ValueError("relation-cache-ref-not-arxiv")
    value = ref.split(":", 1)[1]
    if not re.fullmatch(r"\d{4}\.\d+", value):
        raise ValueError("relation-cache-arxiv-id-invalid")
    return value


def _policy(*, max_primary_per_run: int, max_fulltext_per_run: int, failure_cooldown_hours: float, replay_guard_minutes: float) -> dict[str, Any]:
    return {
        "private_cache_only": True,
        "public_primary_sources_are_refetched_locally": True,
        "fulltext_enrichment_is_optional": True,
        "primary_success_survives_fulltext_failure": True,
        "bounded_primary_attempts_per_run": int(max_primary_per_run),
        "bounded_fulltext_attempts_per_run": int(max_fulltext_per_run),
        "failure_cooldown_hours": float(failure_cooldown_hours),
        "same_universe_replay_guard_minutes": float(replay_guard_minutes),
        "transport_replay_cannot_multiply_network_budget": True,
        "relation_cache_backfill_has_zero_scientific_authority": True,
        "automatic_problem_gate_authority": False,
        "automatic_method_authority": False,
        "automatic_experiment_authority": False,
        "automatic_p0_authority": False,
    }


def backfill_relation_cache(
    *,
    storage: StorageSettings | None = None,
    generator_state: dict[str, Any] | None = None,
    requester: Requester | None = None,
    max_primary_per_run: int = DEFAULT_MAX_PRIMARY_PER_RUN,
    max_fulltext_per_run: int = DEFAULT_MAX_FULLTEXT_PER_RUN,
    failure_cooldown_hours: float = DEFAULT_FAILURE_COOLDOWN_HOURS,
    min_interval_seconds: float = DEFAULT_MIN_INTERVAL_SECONDS,
    replay_guard_minutes: float = DEFAULT_REPLAY_GUARD_MINUTES,
    now: datetime | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    generator_state = generator_state or load_problem_generator_state()
    fetch = requester or _default_requester
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    cache_dir = _cache_dir(storage)
    cache_dir.mkdir(parents=True, exist_ok=True)
    previous = _load_state(storage)
    receipts = portable_review_receipts(generator_state)
    universe_digest = relation_universe_digest(receipts)
    target = _target_refs(generator_state)
    primary_before = _refs_from_files(cache_dir, fulltext=False)
    fulltext_before = _refs_from_files(cache_dir, fulltext=True)
    if _recent_same_universe_attempt(previous, digest=universe_digest, now=current, guard_minutes=replay_guard_minutes):
        usable_refs = {str(row.get("ref") or "") for row in reviewed_primary_cache_records(storage, reviewed_refs=target)}
        return {
            "schema_version": "1.1",
            "generated_at": current.replace(microsecond=0).isoformat(),
            "run_started_at": previous.get("run_started_at"),
            "status": "SKIPPED_RECENT_BACKFILL_ATTEMPT",
            "previous_status": previous.get("status"),
            "relation_universe_digest": universe_digest,
            "policy": _policy(max_primary_per_run=max_primary_per_run,max_fulltext_per_run=max_fulltext_per_run,failure_cooldown_hours=failure_cooldown_hours,replay_guard_minutes=replay_guard_minutes),
            "summary": {"target_refs":len(target),"primary_cached_before":len(target & primary_before),"primary_attempted":0,"primary_succeeded":0,"primary_failed":0,"primary_cached_after":len(target & primary_before),"primary_missing_after":len(target-primary_before),"fulltext_cached_before":len(target & fulltext_before),"fulltext_attempted":0,"fulltext_succeeded":0,"fulltext_failed":0,"fulltext_cached_after":len(target & fulltext_before),"usable_reviewed_cache_records_after":len(target & usable_refs),"cooldown_skipped":0,"scientifically_authorized":0},
            "scientific_authority": False,
        }
    recent_failed = _recent_failures(previous, now=current, cooldown_hours=failure_cooldown_hours)
    missing = sorted(target - primary_before)
    selected = [ref for ref in missing if ref not in recent_failed][: max(0, int(max_primary_per_run))]
    started_at = current.replace(microsecond=0).isoformat()
    _write_state(storage,{"schema_version":"1.1","generated_at":started_at,"run_started_at":started_at,"status":"BACKFILL_RUNNING","relation_universe_digest":universe_digest,"policy":_policy(max_primary_per_run=max_primary_per_run,max_fulltext_per_run=max_fulltext_per_run,failure_cooldown_hours=failure_cooldown_hours,replay_guard_minutes=replay_guard_minutes),"summary":{"target_refs":len(target),"primary_cached_before":len(target & primary_before),"planned_primary_attempts":len(selected),"fulltext_cached_before":len(target & fulltext_before),"scientifically_authorized":0},"primary_failures":[row for row in previous.get("primary_failures") or [] if isinstance(row,dict)][-256:],"scientific_authority":False})

    primary_successes: list[str] = []
    primary_failures: list[dict[str, Any]] = []
    fulltext_successes: list[str] = []
    fulltext_failures: list[dict[str, Any]] = []
    last_fetch_started: float | None = None

    for ref in selected:
        arxiv_id = _arxiv_id(ref)
        try:
            last_fetch_started = _throttle(last_fetch_started, min_interval_seconds)
            response = fetch(
                f"https://arxiv.org/abs/{arxiv_id}",
                timeout=20.0,
                headers={"User-Agent": "Agent-Self-Evolution-Observatory/relation-cache-backfill"},
            )
            status = int(getattr(response, "status_code", 200))
            if status >= 400:
                raise RuntimeError(f"HTTP {status}")
            raw_text = str(getattr(response, "text", "") or "")
            parsed = parse_arxiv_page(raw_text)
            if not raw_text or not parsed.get("title") or not parsed.get("abstract"):
                raise RuntimeError("primary-page-missing-title-or-abstract")
            declared = _meta_content(raw_text, "citation_arxiv_id")
            if declared and declared.split("v", 1)[0] != arxiv_id:
                raise RuntimeError("primary-page-arxiv-id-mismatch")
            raw_bytes = raw_text.encode("utf-8")
            source_sha = hashlib.sha256(raw_bytes).hexdigest()
            target_path = cache_dir / f"arxiv-{arxiv_id}-{source_sha[:12]}.html"
            if not target_path.exists():
                target_path.write_bytes(raw_bytes)
            primary_successes.append(ref)
        except Exception as error:
            primary_failures.append({"ref": ref, "failed_at": current.replace(microsecond=0).isoformat(), "error": f"{type(error).__name__}:{str(error)[:240]}"})

    primary_after_fetch = _refs_from_files(cache_dir, fulltext=False)
    fulltext_candidates = sorted((target & primary_after_fetch) - fulltext_before)[: max(0, int(max_fulltext_per_run))]
    for ref in fulltext_candidates:
        arxiv_id = _arxiv_id(ref)
        try:
            last_fetch_started = _throttle(last_fetch_started, min_interval_seconds)
            response = fetch(
                f"https://arxiv.org/html/{arxiv_id}",
                timeout=20.0,
                headers={"User-Agent": "Agent-Self-Evolution-Observatory/relation-fulltext-backfill"},
            )
            status = int(getattr(response, "status_code", 200))
            if status >= 400:
                raise RuntimeError(f"HTTP {status}")
            raw_text = str(getattr(response, "text", "") or "")
            if not raw_text or "<section" not in raw_text.lower():
                raise RuntimeError("fulltext-page-missing-sections")
            # Parse now so malformed HTML never enters the evidence cache as a
            # successful enrichment. Zero extracted facts remain valid.
            extract_empirical_fact_candidates(raw_text, max_facts=4)
            extract_typed_evidence_candidates(raw_text, max_per_type=2)
            raw_bytes = raw_text.encode("utf-8")
            source_sha = hashlib.sha256(raw_bytes).hexdigest()
            target_path = cache_dir / f"arxiv-full-{arxiv_id}-{source_sha[:12]}.html"
            if not target_path.exists():
                target_path.write_bytes(raw_bytes)
            fulltext_successes.append(ref)
        except Exception as error:
            fulltext_failures.append({"ref": ref, "failed_at": current.replace(microsecond=0).isoformat(), "error": f"{type(error).__name__}:{str(error)[:240]}"})

    primary_after = _refs_from_files(cache_dir, fulltext=False)
    fulltext_after = _refs_from_files(cache_dir, fulltext=True)
    usable_records = reviewed_primary_cache_records(storage, reviewed_refs=target)
    usable_refs = {str(row.get("ref") or "") for row in usable_records}
    # Preserve still-recent failures that were not retried this cycle, then add
    # this cycle's failures. Success removes a prior failure from the ledger.
    success_set = set(primary_successes)
    retained_failures = [
        row for row in previous.get("primary_failures") or []
        if isinstance(row, dict)
        and str(row.get("ref") or "") not in success_set
        and str(row.get("ref") or "") in recent_failed
    ]
    state = {
        "schema_version": "1.1",
        "generated_at": current.replace(microsecond=0).isoformat(),
        "run_started_at": started_at,
        "status": "COMPLETE" if target.issubset(primary_after) else "BACKFILL_IN_PROGRESS",
        "relation_universe_digest": universe_digest,
        "policy": _policy(max_primary_per_run=max_primary_per_run,max_fulltext_per_run=max_fulltext_per_run,failure_cooldown_hours=failure_cooldown_hours,replay_guard_minutes=replay_guard_minutes),
        "summary": {
            "target_refs": len(target),
            "primary_cached_before": len(target & primary_before),
            "primary_attempted": len(selected),
            "primary_succeeded": len(primary_successes),
            "primary_failed": len(primary_failures),
            "primary_cached_after": len(target & primary_after),
            "primary_missing_after": len(target - primary_after),
            "fulltext_cached_before": len(target & fulltext_before),
            "fulltext_attempted": len(fulltext_candidates),
            "fulltext_succeeded": len(fulltext_successes),
            "fulltext_failed": len(fulltext_failures),
            "fulltext_cached_after": len(target & fulltext_after),
            "usable_reviewed_cache_records_after": len(target & usable_refs),
            "cooldown_skipped": len(set(missing) & recent_failed),
            "scientifically_authorized": 0,
        },
        "primary_failures": (retained_failures + primary_failures)[-256:],
        "fulltext_failures": fulltext_failures[-128:],
        "scientific_authority": False,
    }
    _write_state(storage,state)
    return state


if __name__ == "__main__":
    print(json.dumps(backfill_relation_cache(), ensure_ascii=False, indent=2))
