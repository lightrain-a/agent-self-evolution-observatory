from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
import urllib.parse
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "behavior-formal-goal-coupling-2026-release-watch-v1.1"
SPACE_ID = "behavior-1k/2026-challenge-leaderboard"
TARGET_FILES = (
    "data/submissions.jsonl",
    "data/results.jsonl",
    "data/per_task_results.jsonl",
)
IGNORED_HISTORY_FILE = "data/2025_results.jsonl"
SCHEMA_FILE = "data/README.md"


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _get_json(url: str) -> Any:
    # Use the server's proven direct curl transport rather than Python's TLS
    # stack. The installed curl is old, so retries are implemented outside
    # curl for version independence. Transport failure remains fail-closed.
    last: subprocess.CompletedProcess[bytes] | None = None
    for attempt in range(3):
        last = subprocess.run(
            [
                "curl", "--noproxy", "*", "-sS", "--fail", "--connect-timeout", "20",
                "--max-time", "60", "-H", "User-Agent: research-release-watch/1.1", url,
            ],
            capture_output=True,
            check=False,
        )
        if last.returncode == 0:
            return json.loads(last.stdout)
        if attempt < 2:
            time.sleep(attempt + 1)
    assert last is not None
    raise RuntimeError(f"metadata transport failed rc={last.returncode}: {last.stderr.decode('utf-8', 'replace')[:300]}")


def current_metadata() -> dict[str, Any]:
    api = _get_json(f"https://huggingface.co/api/spaces/{SPACE_ID}")
    revision = str(api.get("sha") or "").strip()
    if len(revision) != 40:
        raise ValueError("Space API did not return a 40-character revision")
    encoded_revision = urllib.parse.quote(revision, safe="")
    tree = _get_json(
        f"https://huggingface.co/api/spaces/{SPACE_ID}/tree/{encoded_revision}/data?recursive=true&expand=false"
    )
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
    return {
        "space_id": SPACE_ID,
        "sha": revision,
        "last_modified": api.get("lastModified"),
        "runtime_stage": (api.get("runtime") or {}).get("stage"),
        "data_files": files,
    }


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
        "changed_2026_target_files": result["changed_2026_target_files"],
        "policy_outcome_values_read": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
