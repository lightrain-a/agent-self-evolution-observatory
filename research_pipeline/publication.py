from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings

DAILY_ARTIFACTS = (
    "generated/human-terminal-idea-state.json",
    "generated/human-terminal-idea-state.js",
    "generated/research-system-state.json",
    "generated/research-system-state.js",
)
WEEKLY_ARTIFACTS = DAILY_ARTIFACTS + (
    "generated/iclr-low-resource-ideas.json",
    "generated/iclr-low-resource-ideas.js",
    "generated/machine-school-inspired-ideas.json",
    "generated/machine-school-inspired-ideas.js",
    "generated/machine-school-external-reviews.json",
    "generated/idea-discovery-v3.json",
    "generated/idea-discovery-v3.js",
    "generated/idea-discovery-v3-external-reviews.json",
    "generated/idea-discovery-v31.json",
    "generated/idea-discovery-v31.js",
    "generated/idea-discovery-v31-external-reviews.json",
    "generated/idea-discovery-v5.json",
    "generated/idea-discovery-v5.js",
    "generated/idea-discovery-v5-external-reviews.json",
    "generated/idea-discovery-v51.json",
    "generated/idea-discovery-v51.js",
    "generated/idea-discovery-v51-external-reviews.json",
    "generated/idea-discovery-v52.json",
    "generated/idea-discovery-v52.js",
    "generated/idea-discovery-v52-external-reviews.json",
    "generated/idea-discovery-v53.json",
    "generated/idea-discovery-v53.js",
    "generated/idea-discovery-v53-external-reviews.json",
    "generated/discussion-ready-ideas.json",
    "generated/discussion-ready-ideas.js",
    "generated/idea-discovery-v4.json",
    "generated/idea-discovery-v4.js",
    "generated/idea-discovery-v4-external-reviews.json",
    "generated/iclr-experiment-audit.json",
    "generated/iclr-experiment-audit.js",
    "generated/cvpr-low-resource-ideas.json",
    "generated/cvpr-low-resource-ideas.js",
    "generated/published-experiment-audit.json",
    "generated/published-experiment-audit.js",
    "generated/s2-literature.js",
)
VOLATILE_KEYS = {
    "created_at", "generated_at", "retrieved_at", "started_at", "completed_at", "updated_at",
}
PUBLICATION_OK_STATES = frozenset({"published", "unchanged", "deferred", "recovered"})


def _run(*args: str, check: bool = True, timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), cwd=PROJECT_ROOT, text=True, capture_output=True, check=check, timeout=timeout,
    )


def _status_paths() -> list[str]:
    completed = _run("git", "status", "--porcelain", check=True)
    paths: list[str] = []
    for line in completed.stdout.splitlines():
        if len(line) >= 4:
            paths.append(line[3:].strip().strip('"'))
    return paths


def _normalize(value: Any, *, root: bool = False) -> Any:
    if isinstance(value, dict):
        normalized = {}
        for key, item in value.items():
            if key in VOLATILE_KEYS:
                continue
            if root and key == "automation":
                automation = dict(item or {})
                automation.pop("latest_report", None)
                normalized[key] = _normalize(automation)
                continue
            if key in {"source_path", "result_dir", "cache_dir"}:
                continue
            normalized[key] = _normalize(item)
        return normalized
    if isinstance(value, list):
        return [_normalize(item, root=root) for item in value]
    return value


def _normalized_payload_digest(payload: Any) -> str:
    normalized = _normalize(payload, root=True)
    encoded = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _normalized_text_digest(relative: str, text: str) -> str:
    if relative.endswith(".json"):
        return _normalized_payload_digest(json.loads(text))
    parsed_payloads: list[Any] = []
    for line in text.splitlines():
        if " = " not in line or not line.rstrip().endswith(";"):
            continue
        _, raw_payload = line.split(" = ", 1)
        try:
            parsed_payloads.append(json.loads(raw_payload.strip().removesuffix(";")))
        except json.JSONDecodeError:
            parsed_payloads = []
            break
    if parsed_payloads:
        return _normalized_payload_digest(parsed_payloads)
    fallback = re.sub(r'"(?:generated_at|retrieved_at|started_at|completed_at|updated_at)":"[^"]*"', '"volatile":""', text)
    fallback = re.sub(r'"cache_dir":"[^"]*"', '"cache_dir":"<cache>"', fallback)
    return hashlib.sha256(fallback.encode("utf-8")).hexdigest()


def _artifact_digest(paths: tuple[str, ...]) -> str:
    digests: list[str] = []
    for relative in paths:
        path = PROJECT_ROOT / relative
        if not path.exists():
            raise FileNotFoundError(path)
        digests.append(_normalized_text_digest(relative, path.read_text(encoding="utf-8")))
    return hashlib.sha256("\n".join(digests).encode("utf-8")).hexdigest()


def _head_artifact_digest(paths: tuple[str, ...]) -> str | None:
    digests: list[str] = []
    for relative in paths:
        completed = _run("git", "show", f"HEAD:{relative}", check=False)
        if completed.returncode != 0:
            return None
        digests.append(_normalized_text_digest(relative, completed.stdout))
    return hashlib.sha256("\n".join(digests).encode("utf-8")).hexdigest()


def _restore(paths: tuple[str, ...]) -> None:
    _run("git", "restore", "--", *paths, check=True)


def _ensure_git_identity() -> dict[str, str]:
    name = _run("git", "config", "--get", "user.name", check=False).stdout.strip()
    email = _run("git", "config", "--get", "user.email", check=False).stdout.strip()
    if not name:
        name = "Agent Evolution Automation"
        _run("git", "config", "--local", "user.name", name, check=True)
    if not email:
        email = "agent-evolution-bot@users.noreply.github.com"
        _run("git", "config", "--local", "user.email", email, check=True)
    return {"name": name, "email": email}


def _push_with_timeout() -> subprocess.CompletedProcess[str]:
    return _run(
        "git", "-c", "http.proxy=", "-c", "https.proxy=", "push", "origin", "main",
        check=True, timeout=float(os.getenv("AUTOMATION_GIT_PUSH_TIMEOUT", "90")),
    )


def _recover_pending_push(local: str, remote: str) -> dict[str, Any] | None:
    counts = _run("git", "rev-list", "--left-right", "--count", "origin/main...HEAD", check=True).stdout.strip().split()
    if len(counts) != 2:
        return {"status": "blocked", "reason": "unable to determine branch divergence", "local": local, "remote": remote}
    remote_only, local_only = (int(counts[0]), int(counts[1]))
    if remote_only == 0 and local_only > 0:
        try:
            push = _push_with_timeout()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            detail = getattr(error, "stderr", "") or str(error)
            return {
                "status": "deferred", "reason": "pending local commit still cannot be pushed",
                "local_ahead": local_only, "commit": _run("git", "rev-parse", "--short", "HEAD").stdout.strip(),
                "detail": str(detail)[-2000:],
            }
        return {
            "status": "recovered", "reason": "previous pending commit pushed",
            "local_ahead": local_only, "commit": _run("git", "rev-parse", "--short", "HEAD").stdout.strip(),
            "push": push.stdout[-1000:] + push.stderr[-1000:],
        }
    if local_only == 0 and remote_only > 0:
        return {
            "status": "deferred", "reason": "origin/main advanced; manual fast-forward required before publication",
            "remote_ahead": remote_only, "local": local, "remote": remote,
        }
    return {
        "status": "blocked", "reason": "local and origin/main have diverged",
        "local_ahead": local_only, "remote_ahead": remote_only, "local": local, "remote": remote,
    }


def publish_generated_state(*, mode: str) -> dict[str, Any]:
    storage = StorageSettings.from_env()
    state_dir = storage.run_dir / "automation"
    state_dir.mkdir(parents=True, exist_ok=True)
    artifacts = WEEKLY_ARTIFACTS if mode == "weekly" else DAILY_ARTIFACTS
    allowed = set(WEEKLY_ARTIFACTS)
    dirty = _status_paths()
    disallowed = [path for path in dirty if path not in allowed]
    if disallowed:
        return {"status": "blocked", "reason": "non-generated working-tree changes", "paths": disallowed}

    try:
        _run(
            "git", "-c", "http.proxy=", "-c", "https.proxy=", "fetch", "origin", "main",
            check=True, timeout=float(os.getenv("AUTOMATION_GIT_FETCH_TIMEOUT", "60")),
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        detail = getattr(error, "stderr", "") or str(error)
        return {"status": "deferred", "reason": "git fetch unavailable", "detail": str(detail)[-2000:]}
    local = _run("git", "rev-parse", "HEAD").stdout.strip()
    remote = _run("git", "rev-parse", "origin/main").stdout.strip()
    recovered: dict[str, Any] | None = None
    if local != remote:
        recovered = _recover_pending_push(local, remote)
        if recovered and recovered.get("status") != "recovered":
            return recovered

    digest = _artifact_digest(artifacts)
    digest_file = state_dir / f"published-{mode}-digest.txt"
    previous = digest_file.read_text(encoding="utf-8").strip() if digest_file.exists() else ""
    head_digest = _head_artifact_digest(artifacts)
    if previous == digest or head_digest == digest:
        _restore(tuple(path for path in artifacts if (PROJECT_ROOT / path).exists()))
        digest_file.write_text(digest + "\n", encoding="utf-8")
        return {
            "status": "unchanged",
            "digest": digest,
            "artifacts": list(artifacts),
            "matched": "stored-digest" if previous == digest else "HEAD",
            "recovered_previous_push": recovered,
        }

    identity = _ensure_git_identity()
    _run("git", "add", "--", *artifacts, check=True)
    staged = _run("git", "diff", "--cached", "--name-only").stdout.splitlines()
    if not staged:
        digest_file.write_text(digest + "\n", encoding="utf-8")
        return {"status": "unchanged", "digest": digest, "artifacts": list(artifacts)}
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    message = f"Automated {mode} research state update {stamp}"
    _run("git", "commit", "-m", message, check=True)
    try:
        push = _push_with_timeout()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        detail = getattr(error, "stderr", "") or str(error)
        return {
            "status": "deferred",
            "reason": "commit created but push is pending",
            "commit": _run("git", "rev-parse", "--short", "HEAD").stdout.strip(),
            "detail": str(detail)[-2000:],
        }
    digest_file.write_text(digest + "\n", encoding="utf-8")
    return {
        "status": "published",
        "digest": digest,
        "artifacts": staged,
        "commit": _run("git", "rev-parse", "--short", "HEAD").stdout.strip(),
        "push": push.stdout[-1000:] + push.stderr[-1000:],
        "identity": identity,
        "recovered_previous_push": recovered,
    }
