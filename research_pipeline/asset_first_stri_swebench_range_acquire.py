#!/usr/bin/env python3
"""Parallel range downloader for remaining verified OCI blobs."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

BASE = "https://docker.1ms.run"
CACHE = Path("/data/wyt/e1-stri-reasoningbank-runtime/oci-blob-cache/sha256")
CHUNK_ROOT = Path("/data/wyt/e1-stri-reasoningbank-runtime/oci-range-chunks")
CHUNK_SIZE = 16 * 1024 * 1024
WORKERS = 24
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


def get_token(repo: str) -> str:
    response = requests.get(
        f"{BASE}/v2/{repo}/blobs/sha256:{'0' * 64}", timeout=20
    )
    fields = dict(
        re.findall(r'(\w+)="([^"]+)"', response.headers["www-authenticate"])
    )
    payload = requests.get(
        fields["realm"],
        params={"service": fields["service"], "scope": f"repository:{repo}:pull"},
        timeout=20,
    ).json()
    return payload.get("token") or payload["access_token"]


def get_url(repo: str, digest: str) -> str:
    response = requests.get(
        f"{BASE}/v2/{repo}/blobs/{digest}",
        headers={"Authorization": f"Bearer {get_token(repo)}"},
        allow_redirects=False,
        timeout=30,
    )
    if response.status_code not in {301, 302, 303, 307, 308}:
        response.raise_for_status()
    return response.headers["location"]


def fetch_chunk(url: str, target: Path, start: int, end: int) -> dict:
    expected = end - start + 1
    if target.exists() and target.stat().st_size == expected:
        return {"status": "existing", "bytes": expected}
    for attempt in range(1, 7):
        try:
            response = requests.get(
                url, headers={"Range": f"bytes={start}-{end}"}, timeout=(20, 60)
            )
            if response.status_code != 206:
                raise RuntimeError(f"range status {response.status_code}")
            if len(response.content) != expected:
                raise RuntimeError(f"range bytes {len(response.content)} != {expected}")
            temporary = target.with_suffix(".tmp")
            temporary.write_bytes(response.content)
            temporary.replace(target)
            return {"status": "downloaded", "bytes": expected, "attempt": attempt}
        except Exception as error:
            if attempt == 6:
                raise
            time.sleep(min(2 ** attempt, 15))
    raise AssertionError("unreachable")


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    CHUNK_ROOT.mkdir(parents=True, exist_ok=True)
    blobs: dict[str, dict] = {}
    for repo, manifest_path in SPECS:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in [manifest["config"], *manifest["layers"]]:
            blobs.setdefault(
                item["digest"], {"repo": repo, "size": int(item["size"])}
            )
    pending = {}
    for digest, item in blobs.items():
        value = digest[7:]
        target = CACHE / value
        if target.exists() and target.stat().st_size == item["size"] and file_digest(target) == value:
            continue
        pending[digest] = item
    print(json.dumps({
        "pending_blobs": len(pending),
        "pending_bytes": sum(item["size"] for item in pending.values()),
        "chunk_size": CHUNK_SIZE,
        "workers": WORKERS,
    }), flush=True)
    jobs = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for digest, item in pending.items():
            url = get_url(item["repo"], digest)
            chunk_dir = CHUNK_ROOT / digest[7:]
            chunk_dir.mkdir(parents=True, exist_ok=True)
            count = math.ceil(item["size"] / CHUNK_SIZE)
            for index in range(count):
                start = index * CHUNK_SIZE
                end = min(item["size"], start + CHUNK_SIZE) - 1
                target = chunk_dir / f"{index:05d}.part"
                future = pool.submit(fetch_chunk, url, target, start, end)
                jobs[future] = (digest, index, count)
        completed = 0
        for future in as_completed(jobs):
            future.result()
            completed += 1
            if completed % 10 == 0 or completed == len(jobs):
                print(json.dumps({"chunks_complete": completed, "chunks_total": len(jobs)}), flush=True)
    rows = []
    for digest, item in pending.items():
        value = digest[7:]
        chunk_dir = CHUNK_ROOT / value
        assembled = CACHE / f"{value}.assembled"
        with assembled.open("wb") as output:
            for part in sorted(chunk_dir.glob("*.part")):
                with part.open("rb") as stream:
                    shutil.copyfileobj(stream, output, length=8 * 1024 * 1024)
        if assembled.stat().st_size != item["size"] or file_digest(assembled) != value:
            raise RuntimeError(f"assembled digest failure: {digest}")
        assembled.replace(CACHE / value)
        partial = CACHE / f"{value}.part"
        if partial.exists():
            partial.unlink()
        rows.append({"digest": digest, "size": item["size"], "verified": True})
    print(json.dumps({
        "decision": "RANGE_DOWNLOAD_VERIFIED",
        "blob_count": len(rows),
        "bytes": sum(row["size"] for row in rows),
        "rows": rows,
    }), flush=True)


if __name__ == "__main__":
    main()
