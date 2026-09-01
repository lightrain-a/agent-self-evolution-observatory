#!/usr/bin/env python3
"""Resume remaining OCI blobs with aria2 range connections, then verify SHA-256."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

BASE = "https://docker.1ms.run"
CACHE = Path("/data/wyt/e1-stri-reasoningbank-runtime/oci-blob-cache/sha256")
SPECS = (
    ("swebench/sweb.eval.x86_64.sympy_1776_sympy-13798", Path("/data/wyt/e1-source-platform-manifest-skopeo.json")),
    ("swebench/sweb.eval.x86_64.pytest-dev_1776_pytest-5631", Path("/data/wyt/e1-pytest-platform-manifest-skopeo.json")),
    ("swebench/sweb.eval.x86_64.sympy_1776_sympy-17318", Path("/data/wyt/e1-sympy17318-platform-manifest-skopeo.json")),
)


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def signed_url(repo: str, digest: str) -> str:
    """Resolve an exact blob URL across direct and bearer-auth mirrors."""
    blob_url = f"{BASE}/v2/{repo}/blobs/{digest}"
    response = requests.get(
        blob_url, allow_redirects=False, timeout=30, stream=True
    )
    try:
        if response.status_code == 200:
            return blob_url
        if response.status_code in {301, 302, 303, 307, 308}:
            return response.headers["location"]
        if response.status_code != 401:
            response.raise_for_status()
        challenge = response.headers.get("www-authenticate")
        if not challenge:
            raise RuntimeError("registry 401 response omitted www-authenticate")
        fields = dict(re.findall(r'(\w+)="([^"]+)"', challenge))
    finally:
        response.close()
    token_payload = requests.get(
        fields["realm"],
        params={"service": fields["service"], "scope": f"repository:{repo}:pull"},
        timeout=20,
    ).json()
    token = token_payload.get("token") or token_payload["access_token"]
    response = requests.get(
        blob_url,
        headers={"Authorization": f"Bearer {token}"},
        allow_redirects=False,
        timeout=30,
        stream=True,
    )
    try:
        if response.status_code == 200:
            return blob_url
        if response.status_code not in {301, 302, 303, 307, 308}:
            response.raise_for_status()
        return response.headers["location"]
    finally:
        response.close()


def acquire_one(digest: str, size: int, repo: str) -> dict:
    value = digest[7:]
    target = CACHE / value
    if target.exists() and target.stat().st_size == size and file_digest(target) == value:
        return {"digest": digest, "size": size, "status": "verified-existing"}
    partial = CACHE / f"{value}.part"
    command = [
        "aria2c", "--continue=true", "--allow-overwrite=true",
        "--auto-file-renaming=false", "--file-allocation=none",
        "--max-connection-per-server=8", "--split=8", "--min-split-size=4M",
        "--connect-timeout=10", "--timeout=20", "--max-tries=10",
        "--retry-wait=2", "--console-log-level=warn",
        "--dir", str(CACHE), "--out", partial.name, signed_url(repo, digest),
    ]
    completed = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, timeout=1800, check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"aria2 failed for {digest}: {completed.output[-1200:]}"
        )
    if partial.stat().st_size != size:
        raise RuntimeError(f"size mismatch for {digest}: {partial.stat().st_size} != {size}")
    actual = file_digest(partial)
    if actual != value:
        raise RuntimeError(f"sha256 mismatch for {digest}: {actual}")
    partial.replace(target)
    return {
        "digest": digest, "size": size, "status": "downloaded-and-verified",
        "aria2_log_tail": completed.stdout[-800:],
    }


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    blobs = {}
    for repo, manifest_path in SPECS:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in [manifest["config"], *manifest["layers"]]:
            blobs.setdefault(
                item["digest"], {"size": int(item["size"]), "repo": repo}
            )
    pending = {
        digest: item for digest, item in blobs.items()
        if not (
            (CACHE / digest[7:]).exists()
            and (CACHE / digest[7:]).stat().st_size == item["size"]
            and file_digest(CACHE / digest[7:]) == digest[7:]
        )
    }
    print(json.dumps({
        "pending_blobs": len(pending),
        "pending_bytes": sum(item["size"] for item in pending.values()),
        "blob_workers": 2,
        "connections_per_blob": 8,
    }), flush=True)
    rows = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            pool.submit(acquire_one, digest, item["size"], item["repo"]): digest
            for digest, item in pending.items()
        }
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            print(json.dumps({
                "digest": row["digest"], "size": row["size"],
                "status": row["status"],
            }), flush=True)
    print(json.dumps({
        "decision": "ARIA2_MIRROR_BLOBS_VERIFIED",
        "blob_count": len(rows),
        "bytes": sum(row["size"] for row in rows),
        "rows": rows,
    }), flush=True)


if __name__ == "__main__":
    main()
