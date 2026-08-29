#!/usr/bin/env python3
"""Acquire the three preregistered SWE-Bench images via a registry mirror.

Blobs are downloaded concurrently into a shared cache and verified by their
OCI sha256 digest. This avoids RootlessKit's slow registry data path; import
into the isolated E1 Docker daemon is a separate step.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

BASE = "https://docker.1ms.run"
SPECS = (
    {
        "label": "source",
        "repo": "swebench/sweb.eval.x86_64.sympy_1776_sympy-13798",
        "manifest": "/data/wyt/e1-source-platform-manifest-skopeo.json",
        "manifest_digest": "4111da8b069bc23cc67ef24f2f433f82601518941052faebd3c4a621d3748cd6",
    },
    {
        "label": "pytest",
        "repo": "swebench/sweb.eval.x86_64.pytest-dev_1776_pytest-5631",
        "manifest": "/data/wyt/e1-pytest-platform-manifest-skopeo.json",
        "manifest_digest": "22a1a81b8e937a1ff52cef4f38bf59e6a8baa0648ef3b115e6206bfc5c5de68f",
    },
    {
        "label": "sympy17318",
        "repo": "swebench/sweb.eval.x86_64.sympy_1776_sympy-17318",
        "manifest": "/data/wyt/e1-sympy17318-platform-manifest-skopeo.json",
        "manifest_digest": "4d18e6a31fb1d68a8232f3c78a5a4c97e9c7a2d001765dcc90f228cef4b4e39f",
    },
)


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def token_for(repo: str) -> str:
    challenge = requests.get(f"{BASE}/v2/{repo}/blobs/sha256:{'0' * 64}", timeout=20)
    fields = dict(
        re.findall(r'(\w+)="([^"]+)"', challenge.headers.get("www-authenticate", ""))
    )
    response = requests.get(
        fields["realm"],
        params={"service": fields["service"], "scope": f"repository:{repo}:pull"},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("token") or payload["access_token"]


def signed_url(repo: str, digest: str) -> str:
    response = requests.get(
        f"{BASE}/v2/{repo}/blobs/{digest}",
        headers={"Authorization": f"Bearer {token_for(repo)}"},
        timeout=30,
        allow_redirects=False,
    )
    if response.status_code not in {301, 302, 303, 307, 308}:
        response.raise_for_status()
        return response.url
    return response.headers["location"]


def download_one(cache: Path, digest: str, size: int, repo: str) -> dict:
    target = cache / digest.split(":", 1)[1]
    part = target.with_suffix(".part")
    if target.exists() and target.stat().st_size == size and digest_file(target) == digest[7:]:
        return {"digest": digest, "size": size, "status": "verified-existing"}
    for attempt in range(1, 7):
        try:
            offset = part.stat().st_size if part.exists() else 0
            headers = {"Range": f"bytes={offset}-"} if offset else {}
            with requests.get(
                signed_url(repo, digest), headers=headers, stream=True, timeout=(30, 120)
            ) as response:
                if offset and response.status_code == 206:
                    mode = "ab"
                else:
                    mode = "wb"
                    offset = 0
                response.raise_for_status()
                with part.open(mode) as stream:
                    for chunk in response.iter_content(8 * 1024 * 1024):
                        if chunk:
                            stream.write(chunk)
            if part.stat().st_size != size:
                raise RuntimeError(f"size {part.stat().st_size} != {size}")
            actual = digest_file(part)
            if actual != digest[7:]:
                raise RuntimeError(f"sha256 {actual} != {digest[7:]}")
            part.replace(target)
            return {"digest": digest, "size": size, "status": "downloaded", "attempt": attempt}
        except Exception as error:
            if attempt == 6:
                raise
            print(json.dumps({
                "digest": digest, "attempt": attempt, "retry": type(error).__name__,
                "partial_bytes": part.stat().st_size if part.exists() else 0,
            }), flush=True)
            time.sleep(min(2 ** attempt, 20))
    raise AssertionError("unreachable")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cache",
        type=Path,
        default=Path("/data/wyt/e1-stri-reasoningbank-runtime/oci-blob-cache/sha256"),
    )
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path("/data/wyt/e1-stri-reasoningbank-runtime/oci-blob-cache/receipt.json"),
    )
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    blobs: dict[str, dict] = {}
    manifests = []
    for spec in SPECS:
        path = Path(spec["manifest"])
        if digest_file(path) != spec["manifest_digest"]:
            raise RuntimeError(f"manifest digest mismatch: {path}")
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifests.append({
            "label": spec["label"], "repo": spec["repo"],
            "manifest_digest": f"sha256:{spec['manifest_digest']}",
            "config_digest": manifest["config"]["digest"],
        })
        for item in [manifest["config"], *manifest["layers"]]:
            blobs.setdefault(
                item["digest"],
                {"size": int(item["size"]), "repo": spec["repo"]},
            )
            if blobs[item["digest"]]["size"] != int(item["size"]):
                raise RuntimeError("shared digest size mismatch")
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(download_one, args.cache, digest, item["size"], item["repo"]): digest
            for digest, item in blobs.items()
        }
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            print(json.dumps(row, sort_keys=True), flush=True)
    receipt = {
        "schema_version": 1,
        "mirror": BASE,
        "manifests": manifests,
        "unique_blob_count": len(blobs),
        "unique_blob_bytes": sum(item["size"] for item in blobs.values()),
        "worker_count": args.workers,
        "rows": sorted(rows, key=lambda row: row["digest"]),
        "all_sha256_verified": len(rows) == len(blobs),
        "credential_material_present": False,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "decision": "MIRROR_BLOBS_VERIFIED",
        "unique_blob_count": len(rows),
        "unique_blob_bytes": receipt["unique_blob_bytes"],
    }), flush=True)


if __name__ == "__main__":
    main()
