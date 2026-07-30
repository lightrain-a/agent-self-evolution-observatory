#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API_ROOT = "https://api.github.com"
API_VERSION = "2026-03-10"
DEFAULT_OWNER = "lightrain-a"
DEFAULT_REPO = "agent-self-evolution-observatory"


def credential_fill() -> tuple[str, str]:
    completed = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        text=True,
        capture_output=True,
        check=True,
        timeout=30,
    )
    values: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    username = values.get("username", "")
    token = values.get("password", "")
    if not username or not token:
        raise RuntimeError("Git Credential Manager did not return an authenticated GitHub credential")
    return username, token


def api_request(token: str, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        API_ROOT + path,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "agent-evolution-deploy-key-configurator",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            content = response.read().decode("utf-8")
            return json.loads(content) if content else None
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {path} failed with HTTP {error.code}: {body[:1000]}") from error


def normalize_public_key(value: str) -> str:
    fields = value.strip().split()
    if len(fields) < 2:
        raise ValueError("Invalid SSH public key")
    return " ".join(fields[:2])


def ensure_deploy_key(
    public_key: str,
    *,
    owner: str,
    repo: str,
    title: str,
) -> dict[str, Any]:
    _, token = credential_fill()
    path = f"/repos/{owner}/{repo}/keys"
    normalized = normalize_public_key(public_key)
    existing = api_request(token, "GET", path)
    for key in existing or []:
        if normalize_public_key(str(key.get("key") or "")) != normalized:
            continue
        if key.get("read_only"):
            raise RuntimeError(
                f"The same deploy key already exists as read-only (id={key.get('id')}); "
                "remove it manually before granting write access."
            )
        return {
            "status": "existing",
            "id": key.get("id"),
            "title": key.get("title"),
            "read_only": bool(key.get("read_only")),
            "verified": bool(key.get("verified")),
        }
    created = api_request(
        token,
        "POST",
        path,
        {"title": title, "key": public_key.strip(), "read_only": False},
    )
    return {
        "status": "created",
        "id": created.get("id"),
        "title": created.get("title"),
        "read_only": bool(created.get("read_only")),
        "verified": bool(created.get("verified")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Add a server public key as a write-enabled deploy key without exposing Git credentials.")
    parser.add_argument("--key-file", type=Path, required=True)
    parser.add_argument("--owner", default=DEFAULT_OWNER)
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--title", default="agent-evolution-52-automation")
    args = parser.parse_args()
    public_key = args.key_file.read_text(encoding="utf-8").strip()
    result = ensure_deploy_key(public_key, owner=args.owner, repo=args.repo, title=args.title)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
