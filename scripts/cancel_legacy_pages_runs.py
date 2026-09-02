#!/usr/bin/env python3
"""Cancel GitHub's generated Pages workflow before direct frontend deployment.

The repository has a branch-based Pages workflow named ``pages build and
 deployment``. When that generated workflow gets stuck in queued or reporting
states, it retains the ``github-pages`` environment and prevents a recovery
workflow from starting. This helper runs in a job without an environment,
cancels every active generated Pages run, and waits until the runs are final.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

API = "https://api.github.com"
API_VERSION = "2026-03-10"
ACTIVE_STATES = {"queued", "in_progress", "pending", "waiting", "requested"}
LEGACY_WORKFLOW_NAME = "pages build and deployment"


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def request(token: str, method: str, path: str) -> tuple[int, bytes]:
    req = urllib.request.Request(
        API + path,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "agent-evolution-pages-canceller",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def json_body(body: bytes) -> dict[str, Any]:
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def list_active_runs(token: str, repository: str) -> list[dict[str, Any]]:
    status, body = request(token, "GET", f"/repos/{repository}/actions/runs?per_page=100")
    if status != 200:
        raise RuntimeError(f"Unable to list Actions runs: HTTP {status}")
    return [
        run
        for run in json_body(body).get("workflow_runs", [])
        if run.get("name") == LEGACY_WORKFLOW_NAME and run.get("status") in ACTIVE_STATES
    ]


def cancel_active_runs(token: str, repository: str) -> None:
    # Repeat because the generated branch workflow may appear a few seconds after
    # the direct workflow starts.
    observed: set[str] = set()
    consecutive_empty = 0
    for _ in range(18):
        active = list_active_runs(token, repository)
        if not active:
            consecutive_empty += 1
            # Allow enough time for the generated branch workflow to appear,
            # but do not add a fixed ninety-second delay when it is absent.
            if consecutive_empty >= 4:
                break
        else:
            consecutive_empty = 0
        for run in active:
            run_id = str(run.get("id") or "")
            if not run_id or run_id in observed:
                continue
            status, body = request(token, "POST", f"/repos/{repository}/actions/runs/{run_id}/cancel")
            message = json_body(body).get("message", "")
            if status in {202, 409}:
                print(f"Legacy Pages run {run_id}: cancel HTTP {status} {message}".strip())
                observed.add(run_id)
            else:
                raise RuntimeError(f"Unable to cancel legacy Pages run {run_id}: HTTP {status} {message}")
        time.sleep(5)

    for attempt in range(1, 61):
        active = list_active_runs(token, repository)
        if not active:
            print(f"No active generated Pages runs remain after {attempt} status checks.")
            return
        print(
            "Waiting for generated Pages runs to finish: "
            + ", ".join(f"{run.get('id')}={run.get('status')}" for run in active)
        )
        time.sleep(5)
    raise RuntimeError("Generated Pages workflow did not release after cancellation")


def main() -> int:
    # This helper is only a preflight optimization. The deploy job has its own
    # stale-deployment recovery and lock-conflict retries, so a transient REST
    # failure here must never prevent the frontend artifact from being built.
    try:
        cancel_active_runs(required("GH_TOKEN"), required("GITHUB_REPOSITORY"))
    except Exception as error:
        print(
            f"::warning::Generated Pages cancellation was best-effort and failed: {error}. "
            "Continuing to build; deployment recovery will handle remaining locks.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"::error::{error}", file=sys.stderr)
        raise
