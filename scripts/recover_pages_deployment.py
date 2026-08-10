#!/usr/bin/env python3
"""Deploy the frontend-only GitHub Pages artifact with recovery.

This script runs only in GitHub Actions. It cancels stale internal Pages
deployments extracted from prior workflow logs, creates a fresh deployment,
refreshes the OIDC identity on every retry, and waits up to 30 minutes for
completion.
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from typing import Any

API = "https://api.github.com"
API_VERSION = "2026-03-10"
DEPLOYMENT_RE = re.compile(rb"Created deployment for [0-9a-f]{40}, ID: ([^\s]+)")
FALLBACK_DEPLOYMENT_RE = re.compile(rb"Created fallback Pages deployment ID: ([^\s]+)")
FINAL_FAILURES = {
    "deployment_failed",
    "deployment_content_failed",
    "deployment_cancelled",
    "deployment_lost",
}
STALE_RUN_CONCLUSIONS = {"success", "failure", "cancelled"}
MAX_STALE_RUNS = 12


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def request(
    token: str,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    *,
    absolute: bool = False,
    extra_headers: dict[str, str] | None = None,
) -> tuple[int, bytes]:
    """Call GitHub REST through the runner-native ``gh`` TLS stack.

    Python urllib on the hosted Pages deploy runner can inherit a certificate
    chain that rejects GitHub's connection as self-signed. ``gh api`` uses the
    runner's native trust store and the workflow-provided GH_TOKEN, while this
    wrapper preserves the status/body contract used by the recovery logic.
    """
    if absolute:
        raise RuntimeError("absolute REST URLs are not supported by the gh-api transport")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": "agent-evolution-pages-recovery",
    }
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if extra_headers:
        headers.update(extra_headers)
    command = ["gh", "api", "--include", "--method", method]
    for key, value in headers.items():
        command.extend(["-H", f"{key}: {value}"])
    command.append(path)
    input_bytes = None
    if payload is not None:
        command.extend(["--input", "-"])
        input_bytes = json.dumps(payload).encode("utf-8")
    env = os.environ.copy()
    env["GH_TOKEN"] = token
    completed = subprocess.run(
        command,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        timeout=60,
        check=False,
    )
    raw = completed.stdout
    separator = b"\r\n\r\n" if b"\r\n\r\n" in raw else b"\n\n"
    header, body = raw.split(separator, 1) if separator in raw else (raw, b"")
    matches = re.findall(rb"^HTTP/\S+\s+(\d{3})", header, re.MULTILINE)
    if not matches:
        stderr = completed.stderr.decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"gh api returned no HTTP status (exit {completed.returncode}): {stderr}")
    return int(matches[-1]), body


def json_body(body: bytes) -> dict[str, Any]:
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def stale_pages_run_ids(token: str, repository: str, source_run_id: str) -> list[str]:
    status, body = request(token, "GET", f"/repos/{repository}/actions/runs?per_page=60")
    if status != 200:
        raise RuntimeError(f"Unable to list workflow runs: HTTP {status}")
    runs = json_body(body).get("workflow_runs", [])
    ids: list[str] = []
    if source_run_id:
        ids.append(source_run_id)
    for run in runs:
        name = str(run.get("name") or "")
        if run.get("conclusion") not in STALE_RUN_CONCLUSIONS:
            continue
        if name == "pages build and deployment" or "Pages" in name:
            run_id = str(run.get("id") or "")
            if run_id and run_id not in ids:
                ids.append(run_id)
        if len(ids) >= MAX_STALE_RUNS:
            break
    return ids


def deployment_ids_from_run(token: str, repository: str, run_id: str, retries: int) -> set[str]:
    path = f"/repos/{repository}/actions/runs/{run_id}/logs"
    for attempt in range(1, retries + 1):
        status, body = request(token, "GET", path)
        if status == 200:
            try:
                with zipfile.ZipFile(io.BytesIO(body)) as archive:
                    joined = b"\n".join(archive.read(name) for name in archive.namelist())
            except zipfile.BadZipFile:
                joined = body
            found = {
                match.decode("utf-8", errors="replace")
                for pattern in (DEPLOYMENT_RE, FALLBACK_DEPLOYMENT_RE)
                for match in pattern.findall(joined)
            }
            if found:
                print(f"Found {len(found)} Pages deployment ID(s) in run {run_id}.")
                return found
        if attempt < retries:
            time.sleep(10)
    print(f"No internal Pages deployment ID found in run {run_id}.")
    return set()


def cancel_stale_deployments(token: str, repository: str, source_run_id: str) -> None:
    ids: set[str] = set()
    stale_runs = stale_pages_run_ids(token, repository, source_run_id)
    print(f"Inspecting {len(stale_runs)} recent completed Pages run(s) for stale deployment locks.")
    for run_id in stale_runs:
        ids.update(deployment_ids_from_run(token, repository, run_id, 18 if run_id == source_run_id else 1))
    for deployment_id in sorted(ids):
        status, body = request(
            token,
            "POST",
            f"/repos/{repository}/pages/deployments/{deployment_id}/cancel",
        )
        message = json_body(body).get("message", "")
        if status in {200, 202, 204, 404, 409}:
            print(f"Pages deployment {deployment_id}: cancel HTTP {status} {message}".strip())
        else:
            print(f"Warning: unable to cancel {deployment_id}: HTTP {status} {message}".strip())
    # The deployment creation path below already retries transient lock conflicts.
    # Keep only a short release grace period here so each publish does not inherit
    # minutes of historical recovery latency.
    time.sleep(20)


def current_artifact_id(token: str, repository: str, workflow_run_id: str) -> int:
    status, body = request(
        token,
        "GET",
        f"/repos/{repository}/actions/runs/{workflow_run_id}/artifacts?per_page=100",
    )
    if status != 200:
        raise RuntimeError(f"Unable to list workflow artifacts: HTTP {status}")
    artifacts = [
        item for item in json_body(body).get("artifacts", [])
        if item.get("name") == "github-pages" and not item.get("expired")
    ]
    if not artifacts:
        raise RuntimeError("The github-pages artifact was not found")
    return int(artifacts[-1]["id"])


def oidc_token(repository: str) -> str:
    url = required("ACTIONS_ID_TOKEN_REQUEST_URL")
    separator = "&" if "?" in url else "?"
    owner = repository.split("/", 1)[0]
    audience = f"https://github.com/{owner}"
    url += separator + urllib.parse.urlencode({"audience": audience})
    request_token = required("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"bearer {request_token}"},
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    value = str(payload.get("value") or "")
    if not value:
        raise RuntimeError("Unable to obtain a GitHub Actions OIDC token")
    return value


def public_roots(repository: str, page_url: str) -> list[str]:
    roots: list[str] = []

    def add(value: str) -> None:
        value = value.strip()
        if not value:
            return
        if not value.startswith(("http://", "https://")):
            value = "https://" + value
        value = value.rstrip("/") + "/"
        if value not in roots:
            roots.append(value)

    add(page_url)
    try:
        add(open("CNAME", "r", encoding="utf-8").read().strip())
    except OSError:
        pass
    owner, repo = repository.split("/", 1)
    add(f"https://{owner}.github.io/{repo}/")
    return roots


def live_build_root(repository: str, page_url: str, build_sha: str) -> str:
    for root in public_roots(repository, page_url):
        manifest_url = urllib.parse.urljoin(root, "deployment-manifest.json")
        separator = "&" if "?" in manifest_url else "?"
        manifest_url += separator + urllib.parse.urlencode({"sha": build_sha})
        req = urllib.request.Request(
            manifest_url,
            headers={
                "Accept": "application/json",
                "Cache-Control": "no-cache",
                "User-Agent": "agent-evolution-pages-live-verifier",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if str(payload.get("build_sha") or "") == build_sha:
            return root
    return ""


def deployment_id_of(deployment: dict[str, Any]) -> str:
    direct = str(deployment.get("id") or "").strip()
    if direct:
        return direct
    status_url = str(deployment.get("status_url") or "").strip()
    parts = [part for part in urllib.parse.urlsplit(status_url).path.split("/") if part]
    if parts and parts[-1] == "status":
        parts.pop()
    return parts[-1] if parts else ""


def create_deployment(
    token: str,
    repository: str,
    artifact_id: int,
    build_sha: str,
) -> dict[str, Any]:
    last_message = ""
    for attempt in range(1, 31):
        # A GitHub OIDC key rotation can invalidate a token that was minted only
        # seconds earlier. Refresh the token on every deployment attempt instead
        # of replaying one invalid token for the whole retry window.
        try:
            identity_token = oidc_token(repository)
        except Exception as error:
            last_message = f"OIDC token request failed: {error}"
            print(f"Create attempt {attempt}/30: {last_message}")
            if attempt < 30:
                time.sleep(20)
            continue
        payload = {
            "artifact_id": artifact_id,
            "pages_build_version": build_sha,
            "oidc_token": identity_token,
        }
        status, body = request(token, "POST", f"/repos/{repository}/pages/deployments", payload)
        response = json_body(body)
        if status in {200, 201}:
            deployment_id = deployment_id_of(response)
            print(f"Created fallback Pages deployment on attempt {attempt} (HTTP {status}).")
            if deployment_id:
                print(f"Created fallback Pages deployment ID: {deployment_id} for {build_sha}.")
            return response
        last_message = str(response.get("message") or body[:500])
        print(f"Create attempt {attempt}/30: HTTP {status}: {last_message}")
        if attempt < 30:
            time.sleep(30)
    raise RuntimeError(f"Unable to create Pages deployment: {last_message}")


def monitor_deployment(token: str, repository: str, deployment: dict[str, Any], build_sha: str) -> str:
    deployment_id = deployment_id_of(deployment)
    if not deployment_id:
        raise RuntimeError("Pages deployment response did not contain a deployment ID")
    page_url = str(deployment.get("page_url") or "")
    for attempt in range(1, 181):
        status, body = request(
            token,
            "GET",
            f"/repos/{repository}/pages/deployments/{deployment_id}",
        )
        response = json_body(body)
        state = str(response.get("status") or "")
        print(f"Pages deployment {deployment_id}: {state or f'HTTP {status}'} ({attempt}/180)")
        if state == "succeed":
            return page_url
        live_root = live_build_root(repository, page_url, build_sha)
        if live_root:
            print(f"Verified live Pages build {build_sha} at {live_root} despite deployment state {state or status}.")
            return live_root
        if state in FINAL_FAILURES:
            raise RuntimeError(f"Pages deployment ended with {state}")
        time.sleep(10)
    request(token, "POST", f"/repos/{repository}/pages/deployments/{deployment_id}/cancel")
    raise RuntimeError("Pages deployment did not finish within 30 minutes")


def main() -> int:
    token = required("GH_TOKEN")
    repository = required("GITHUB_REPOSITORY")
    workflow_run_id = required("GITHUB_RUN_ID")
    build_sha = required("BUILD_SHA")
    source_run_id = os.environ.get("SOURCE_RUN_ID", "").strip()

    cancel_stale_deployments(token, repository, source_run_id)
    artifact_id = current_artifact_id(token, repository, workflow_run_id)
    deployment = create_deployment(token, repository, artifact_id, build_sha)
    page_url = monitor_deployment(token, repository, deployment, build_sha)
    output = os.environ.get("GITHUB_OUTPUT", "")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"page_url={page_url}\n")
    print(f"Pages deployment succeeded: {page_url}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"::error::{error}", file=sys.stderr)
        raise
