from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
import urllib.parse
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "behavior-formal-goal-coupling-2026-release-watch-v1.2"
SPACE_ID = "behavior-1k/2026-challenge-leaderboard"
TARGET_FILES = (
    "data/submissions.jsonl",
    "data/results.jsonl",
    "data/per_task_results.jsonl",
)
IGNORED_HISTORY_FILE = "data/2025_results.jsonl"
SCHEMA_FILE = "data/README.md"
HF_DIRECT = "https://huggingface.co"
HF_MIRROR = "https://hf-mirror.com"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
EMPTY_GIT_BLOB_OID = hashlib.sha1(b"blob 0\0").hexdigest()


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _git_blob_oid(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def _curl(args: list[str], *, timeout_seconds: int = 75) -> subprocess.CompletedProcess[bytes]:
    last: subprocess.CompletedProcess[bytes] | None = None
    for attempt in range(3):
        last = subprocess.run(
            [
                "curl", "--noproxy", "*", "-sS", "--fail", "--connect-timeout", "20",
                "--max-time", str(timeout_seconds), "-H", "User-Agent: research-release-watch/1.2", *args,
            ],
            capture_output=True,
            check=False,
        )
        if last.returncode == 0:
            return last
        if attempt < 2:
            time.sleep(attempt + 1)
    assert last is not None
    raise RuntimeError(f"metadata transport failed rc={last.returncode}: {last.stderr.decode('utf-8', 'replace')[:300]}")


def _get_json(url: str) -> Any:
    return json.loads(_curl([url]).stdout)


def _headers(url: str) -> dict[str, str]:
    raw = _curl(["-D", "-", "-o", "/dev/null", url]).stdout.decode("utf-8", "replace")
    headers: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()
    return headers


def _download_bytes(url: str) -> bytes:
    return _curl(["-L", url]).stdout


def _tree_to_files(tree: Any) -> dict[str, dict[str, Any]]:
    by_path = {str(row.get("path")): row for row in tree if isinstance(row, dict)}
    files: dict[str, dict[str, Any]] = {}
    for path in (*TARGET_FILES, IGNORED_HISTORY_FILE, SCHEMA_FILE):
        row = by_path.get(path)
        if not row:
            files[path] = {"exists": False, "oid": "", "size": None}
        else:
            files[path] = {
                "exists": True,
                "oid": str(row.get("oid") or ""),
                "size": int(row.get("size") or 0),
            }
    return files


def _verify_fixed_revision_mirror(revision: str, files: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Verify only non-outcome schema bytes plus currently empty outcome targets.

    Non-empty target files are deliberately not downloaded here: an OID/size
    delta is sufficient to trigger a zero-authority recheck, and downloading
    their bytes would cross the outcome-access firewall before admission.
    """
    verified: dict[str, Any] = {}
    schema = files.get(SCHEMA_FILE) or {}
    if schema.get("exists"):
        data = _download_bytes(
            f"{HF_MIRROR}/spaces/{SPACE_ID}/resolve/{revision}/{SCHEMA_FILE}?download=true"
        )
        oid = _git_blob_oid(data)
        expected_oid = str(schema.get("oid") or "")
        if len(data) != int(schema.get("size") or 0) or oid != expected_oid:
            raise RuntimeError("fixed-revision schema verification mismatch")
        verified[SCHEMA_FILE] = {
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "git_blob_oid": oid,
            "tree_oid_match": True,
            "outcome_values_read": False,
        }

    for path in TARGET_FILES:
        row = files.get(path) or {}
        if not row.get("exists"):
            verified[path] = {"exists": False, "content_downloaded": False, "outcome_values_read": False}
            continue
        size = int(row.get("size") or 0)
        oid = str(row.get("oid") or "")
        if size > 0:
            verified[path] = {
                "bytes": size,
                "tree_oid": oid,
                "content_downloaded": False,
                "verification": "deferred_nonempty_outcome_content_recheck_required",
                "outcome_values_read": False,
            }
            continue
        data = _download_bytes(
            f"{HF_MIRROR}/spaces/{SPACE_ID}/resolve/{revision}/{path}?download=true"
        )
        actual_oid = _git_blob_oid(data)
        if data != b"" or oid != EMPTY_GIT_BLOB_OID or actual_oid != oid:
            raise RuntimeError(f"empty outcome target verification mismatch:{path}")
        verified[path] = {
            "bytes": 0,
            "sha256": EMPTY_SHA256,
            "git_blob_oid": actual_oid,
            "tree_oid_match": True,
            "content_downloaded": True,
            "outcome_values_read": False,
        }
    return verified


def _current_metadata_mirror() -> dict[str, Any]:
    # hf-mirror does not proxy the Space root metadata endpoint as JSON, but
    # resolve/main exposes X-Repo-Commit. Lock that revision before reading the
    # tree so all subsequent verification is content-addressed.
    probe_url = f"{HF_MIRROR}/spaces/{SPACE_ID}/resolve/main/{SCHEMA_FILE}?download=true"
    headers = _headers(probe_url)
    revision = str(headers.get("x-repo-commit") or "").strip()
    if len(revision) != 40:
        raise ValueError("mirror resolve did not return a 40-character X-Repo-Commit")
    encoded_revision = urllib.parse.quote(revision, safe="")
    tree = _get_json(
        f"{HF_MIRROR}/api/spaces/{SPACE_ID}/tree/{encoded_revision}/data?recursive=true&expand=false"
    )
    files = _tree_to_files(tree)
    verification = _verify_fixed_revision_mirror(revision, files)
    return {
        "space_id": SPACE_ID,
        "sha": revision,
        "last_modified": None,
        "runtime_stage": None,
        "data_files": files,
        "transport": {
            "mode": "hf-mirror-fixed-revision",
            "authority": "Hugging Face Space content mirrored transport",
            "revision_source": "X-Repo-Commit from resolve/main",
            "fixed_revision_tree": True,
            "content_verification": verification,
            "nonempty_outcome_content_downloaded": False,
        },
    }


def _current_metadata_direct() -> dict[str, Any]:
    api = _get_json(f"{HF_DIRECT}/api/spaces/{SPACE_ID}")
    revision = str(api.get("sha") or "").strip()
    if len(revision) != 40:
        raise ValueError("Space API did not return a 40-character revision")
    encoded_revision = urllib.parse.quote(revision, safe="")
    tree = _get_json(
        f"{HF_DIRECT}/api/spaces/{SPACE_ID}/tree/{encoded_revision}/data?recursive=true&expand=false"
    )
    return {
        "space_id": SPACE_ID,
        "sha": revision,
        "last_modified": api.get("lastModified"),
        "runtime_stage": (api.get("runtime") or {}).get("stage"),
        "data_files": _tree_to_files(tree),
        "transport": {
            "mode": "huggingface-direct-metadata",
            "authority": "Hugging Face Space API",
            "fixed_revision_tree": True,
            "nonempty_outcome_content_downloaded": False,
        },
    }


def current_metadata() -> dict[str, Any]:
    # Mirror is preferred on the research hosts because it has proven stable;
    # direct HF remains a failover. Both resolve an exact Space revision before
    # comparing the release surface.
    errors: list[str] = []
    try:
        return _current_metadata_mirror()
    except Exception as error:
        errors.append(f"mirror:{type(error).__name__}:{error}")
    try:
        current = _current_metadata_direct()
        current["transport"]["fallback_from"] = errors
        return current
    except Exception as error:
        errors.append(f"direct:{type(error).__name__}:{error}")
    raise RuntimeError("all release-watch transports failed: " + " | ".join(errors))


def evaluate_release_change(baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    base_space = baseline["leaderboard_space"]
    base_files = base_space["data_files"]
    current_files = current["data_files"]
    changed_targets: list[dict[str, Any]] = []
    for path in TARGET_FILES:
        before = base_files[path]
        after = current_files[path]
        if str(before.get("oid") or "") != str(after.get("oid") or "") or int(before.get("size") or 0) != int(after.get("size") or 0):
            changed_targets.append({
                "path": path,
                "before_oid": before.get("oid"),
                "before_size": int(before.get("size") or 0),
                "after_oid": after.get("oid"),
                "after_size": int(after.get("size") or 0),
            })
    history_before = base_files.get(IGNORED_HISTORY_FILE) or {}
    history_after = current_files.get(IGNORED_HISTORY_FILE) or {}
    history_changed = (
        str(history_before.get("oid") or "") != str(history_after.get("oid") or "")
        or int(history_before.get("size") or 0) != int(history_after.get("size") or 0)
    )
    schema_before = base_files.get(SCHEMA_FILE) or {}
    schema_after = current_files.get(SCHEMA_FILE) or {}
    schema_changed = (
        str(schema_before.get("oid") or "") != str(schema_after.get("oid") or "")
        or int(schema_before.get("size") or 0) != int(schema_after.get("size") or 0)
    )
    trigger = bool(changed_targets)
    if trigger:
        status = "RECHECK_REQUIRED_2026_PUBLIC_RESULT_RELEASE_CHANGE"
    elif schema_changed:
        status = "RECHECK_REQUIRED_2026_PUBLIC_SCHEMA_CHANGE"
    else:
        status = "WATCH_STABLE_NO_2026_PUBLIC_RESULT_RELEASE_CHANGE"
    return {
        "schema_version": SCHEMA_VERSION,
        "object_id": baseline["object_id"],
        "status": status,
        "scientific_authority": False,
        "analysis_authority": False,
        "provider_authority": False,
        "gpu_authority": False,
        "policy_outcome_values_read": False,
        "baseline_sha256": baseline["baseline_sha256"],
        "baseline_space_sha": base_space["sha"],
        "current_space_sha": current["sha"],
        "current_last_modified": current.get("last_modified"),
        "transport": current.get("transport") or {},
        "changed_2026_target_files": changed_targets,
        "ignored_2025_results_changed": history_changed,
        "public_schema_changed": schema_changed,
        "triggered": trigger,
        "recheck_required": trigger or schema_changed,
        "trigger_effect": "zero-authority source/preregistration/admission recheck only; this watch never authorizes outcome analysis",
    }


def run_watch(baseline_path: Path, output_path: Path | None = None) -> dict[str, Any]:
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    current = current_metadata()
    result = evaluate_release_change(baseline, current)
    result["receipt_sha256"] = canonical_sha({k: v for k, v in result.items() if k != "receipt_sha256"})
    if output_path is not None:
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Metadata-only watch for BEHAVIOR 2026 public leaderboard result release")
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_watch(args.baseline, args.output)
    print(json.dumps({
        "status": result["status"],
        "receipt_sha256": result["receipt_sha256"],
        "current_space_sha": result["current_space_sha"],
        "transport_mode": (result.get("transport") or {}).get("mode"),
        "changed_2026_target_files": result["changed_2026_target_files"],
        "policy_outcome_values_read": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
