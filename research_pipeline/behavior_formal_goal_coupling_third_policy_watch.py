from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "behavior-formal-goal-coupling-third-policy-watch-v1"


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _curl_bytes(url: str) -> bytes:
    last: subprocess.CompletedProcess[bytes] | None = None
    for attempt in range(3):
        last = subprocess.run(
            ["curl", "--noproxy", "*", "-L", "-sS", "--fail", "--connect-timeout", "15", "--max-time", "45", url],
            capture_output=True,
            check=False,
        )
        if last.returncode == 0:
            return last.stdout
        if attempt < 2:
            time.sleep(attempt + 1)
    assert last is not None
    raise RuntimeError(f"source transport failed rc={last.returncode}: {last.stderr.decode('utf-8', 'replace')[:300]}")


def _curl_json(url: str) -> dict[str, Any]:
    data = _curl_bytes(url)
    payload = json.loads(data)
    if not isinstance(payload, dict):
        raise ValueError("GitHub issue endpoint did not return an object")
    return payload


def current_surfaces(baseline: dict[str, Any]) -> dict[str, Any]:
    current: dict[str, Any] = {}
    for key in ("behavior_baselines", "openeta_readme", "openral_vla_compatibility"):
        source = baseline["surfaces"][key]
        data = _curl_bytes(str(source["url"]))
        current[key] = {
            "url": source["url"],
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    issue_source = baseline["surfaces"]["allenai_behavior2026_bridge_issue"]
    issue = _curl_json(str(issue_source["url"]))
    current["allenai_behavior2026_bridge_issue"] = {
        "url": issue_source["url"],
        "state": issue.get("state"),
        "updated_at": issue.get("updated_at"),
        "closed_at": issue.get("closed_at"),
        "html_url": issue.get("html_url"),
    }
    return current


def evaluate_change(baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    changed: list[dict[str, Any]] = []
    for key in ("behavior_baselines", "openeta_readme", "openral_vla_compatibility"):
        before = baseline["surfaces"][key]
        after = current[key]
        if before.get("sha256") != after.get("sha256") or int(before.get("bytes") or 0) != int(after.get("bytes") or 0):
            changed.append({
                "surface": key,
                "before_sha256": before.get("sha256"),
                "after_sha256": after.get("sha256"),
                "before_bytes": before.get("bytes"),
                "after_bytes": after.get("bytes"),
            })
    issue_key = "allenai_behavior2026_bridge_issue"
    before_issue = baseline["surfaces"][issue_key]
    after_issue = current[issue_key]
    issue_changed = any(before_issue.get(k) != after_issue.get(k) for k in ("state", "updated_at", "closed_at"))
    if issue_changed:
        changed.append({
            "surface": issue_key,
            "before_state": before_issue.get("state"),
            "after_state": after_issue.get("state"),
            "before_updated_at": before_issue.get("updated_at"),
            "after_updated_at": after_issue.get("updated_at"),
            "before_closed_at": before_issue.get("closed_at"),
            "after_closed_at": after_issue.get("closed_at"),
        })
    triggered = bool(changed)
    result = {
        "schema_version": SCHEMA_VERSION,
        "object_id": baseline["object_id"],
        "status": "RECHECK_REQUIRED_THIRD_POLICY_SOURCE_CHANGE" if triggered else "WATCH_STABLE_NO_THIRD_POLICY_SOURCE_CHANGE",
        "scientific_authority": False,
        "execution_authority": False,
        "gpu_authority": False,
        "policy_training_authorized": False,
        "policy_rollouts_authorized": False,
        "policy_outcomes_read": False,
        "baseline_sha256": baseline["baseline_sha256"],
        "changed_surfaces": changed,
        "triggered": triggered,
        "recheck_required": triggered,
        "current_surfaces": current,
        "trigger_effect": "zero-authority third-family source requalification only; never grants phase2/model/training/rollout/outcome authority",
    }
    result["receipt_sha256"] = canonical_sha({k: v for k, v in result.items() if k != "receipt_sha256"})
    return result


def run_watch(baseline_path: Path, output_path: Path | None = None) -> dict[str, Any]:
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    current = current_surfaces(baseline)
    result = evaluate_change(baseline, current)
    if output_path is not None:
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Metadata-only source watch for a third BEHAVIOR 2026 policy family")
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_watch(args.baseline, args.output)
    print(json.dumps({
        "status": result["status"],
        "receipt_sha256": result["receipt_sha256"],
        "triggered": result["triggered"],
        "changed_surfaces": result["changed_surfaces"],
        "policy_outcomes_read": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
