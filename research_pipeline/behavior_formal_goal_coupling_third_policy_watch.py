from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "behavior-formal-goal-coupling-third-policy-watch-v1.1"


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _curl_bytes(url: str) -> bytes:
    last: subprocess.CompletedProcess[bytes] | None = None
    for attempt in range(2):
        last = subprocess.run(
            ["curl", "--noproxy", "*", "-L", "-sS", "--fail", "--connect-timeout", "8", "--max-time", "20", url],
            capture_output=True,
            check=False,
        )
        if last.returncode == 0:
            return last.stdout
        if attempt == 0:
            time.sleep(1)
    assert last is not None
    raise RuntimeError(f"source transport failed rc={last.returncode}: {last.stderr.decode('utf-8', 'replace')[:300]}")


def _github_raw_fallback(url: str) -> str | None:
    prefix = "https://raw.githubusercontent.com/"
    if not url.startswith(prefix):
        return None
    parts = url[len(prefix):].split("/", 3)
    if len(parts) != 4:
        return None
    owner, repo, ref, path = parts
    return f"https://github.com/{owner}/{repo}/raw/refs/heads/{ref}/{path}"


def _fetch_source_bytes(url: str) -> tuple[bytes, str]:
    errors: list[str] = []
    for candidate in (url, _github_raw_fallback(url)):
        if not candidate:
            continue
        try:
            return _curl_bytes(candidate), candidate
        except Exception as error:
            errors.append(f"{candidate}:{type(error).__name__}:{error}")
    raise RuntimeError("all source transports failed: " + " | ".join(errors))


def _curl_json(url: str) -> dict[str, Any]:
    data = _curl_bytes(url)
    payload = json.loads(data)
    if not isinstance(payload, dict):
        raise ValueError("GitHub issue endpoint did not return an object")
    return payload


def current_surfaces(baseline: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, str]]]:
    current: dict[str, Any] = {}
    transport_errors: list[dict[str, str]] = []
    for key in ("behavior_baselines", "openeta_readme", "openral_vla_compatibility"):
        source = baseline["surfaces"][key]
        try:
            data, transport_url = _fetch_source_bytes(str(source["url"]))
            current[key] = {
                "url": source["url"],
                "transport_url": transport_url,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        except Exception as error:
            transport_errors.append({"surface": key, "error": f"{type(error).__name__}:{error}"[:800]})
    issue_source = baseline["surfaces"]["allenai_behavior2026_bridge_issue"]
    try:
        issue = _curl_json(str(issue_source["url"]))
        current["allenai_behavior2026_bridge_issue"] = {
            "url": issue_source["url"],
            "state": issue.get("state"),
            "updated_at": issue.get("updated_at"),
            "closed_at": issue.get("closed_at"),
            "html_url": issue.get("html_url"),
        }
    except Exception as error:
        transport_errors.append({"surface": "allenai_behavior2026_bridge_issue", "error": f"{type(error).__name__}:{error}"[:800]})
    return current, transport_errors


def evaluate_change(
    baseline: dict[str, Any],
    current: dict[str, Any],
    transport_errors: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    transport_errors = list(transport_errors or [])
    changed: list[dict[str, Any]] = []
    for key in ("behavior_baselines", "openeta_readme", "openral_vla_compatibility"):
        if key not in current:
            continue
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
    after_issue = current.get(issue_key)
    issue_changed = bool(after_issue) and any(before_issue.get(k) != after_issue.get(k) for k in ("state", "updated_at", "closed_at"))
    if issue_changed and after_issue is not None:
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
    watch_complete = not transport_errors
    if triggered:
        status = "RECHECK_REQUIRED_THIRD_POLICY_SOURCE_CHANGE"
    elif not watch_complete:
        status = "WATCH_INCOMPLETE_SOURCE_TRANSPORT_HOLD"
    else:
        status = "WATCH_STABLE_NO_THIRD_POLICY_SOURCE_CHANGE"
    result = {
        "schema_version": SCHEMA_VERSION,
        "object_id": baseline["object_id"],
        "status": status,
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
        "watch_complete": watch_complete,
        "transport_errors": transport_errors,
        "current_surfaces": current,
        "trigger_effect": "zero-authority third-family source requalification only; never grants phase2/model/training/rollout/outcome authority",
    }
    result["receipt_sha256"] = canonical_sha({k: v for k, v in result.items() if k != "receipt_sha256"})
    return result


def run_watch(baseline_path: Path, output_path: Path | None = None) -> dict[str, Any]:
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    current, transport_errors = current_surfaces(baseline)
    result = evaluate_change(baseline, current, transport_errors)
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
        "watch_complete": result["watch_complete"],
        "transport_errors": result["transport_errors"],
        "changed_surfaces": result["changed_surfaces"],
        "policy_outcomes_read": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
