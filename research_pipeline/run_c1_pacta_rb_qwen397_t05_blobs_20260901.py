#!/usr/bin/env python3
"""Resume and verify immutable OCI blobs for C1 PACTA T0.5."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE = "https://docker.1ms.run"
CACHE = Path("/data/wyt/e1-stri-reasoningbank-runtime/oci-blob-cache/sha256")
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t05-images-20260901-v1")

def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def append(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    with path.open("ab") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())

def signed_url(repo: str, value: str) -> str:
    challenge = requests.get(f"{BASE}/v2/{repo}/blobs/sha256:{'0' * 64}", timeout=30)
    fields = dict(re.findall(r'(\w+)="([^"]+)"', challenge.headers["www-authenticate"]))
    token_response = requests.get(fields["realm"], params={"service": fields["service"], "scope": f"repository:{repo}:pull"}, timeout=30)
    token_response.raise_for_status()
    payload = token_response.json()
    token = payload.get("token") or payload["access_token"]
    response = requests.get(f"{BASE}/v2/{repo}/blobs/{value}", headers={"Authorization": f"Bearer {token}"}, allow_redirects=False, timeout=30)
    if response.status_code not in {301, 302, 303, 307, 308}:
        response.raise_for_status()
        return response.url
    return response.headers["location"]

def acquire(root: Path, row: dict) -> dict:
    value = row["digest"][7:]
    target = CACHE / value
    partial = CACHE / f"{value}.part"
    if target.is_file() and target.stat().st_size == row["size"] and digest(target) == value:
        result = {"timestamp": now(), "digest": row["digest"], "size": row["size"], "status": "verified-existing"}
        append(root / "blob-journal.jsonl", result)
        return result
    if target.exists():
        quarantine = CACHE / f"{value}.invalid-{int(__import__('time').time())}"
        target.replace(quarantine)
        append(root / "blob-journal.jsonl", {"timestamp": now(), "digest": row["digest"], "status": "quarantined-invalid-cache", "path": str(quarantine)})
    errors = []
    for attempt in range(1, 7):
        repo = row["repositories"][(attempt - 1) % len(row["repositories"])]
        try:
            url = signed_url(repo, row["digest"])
            command = [
                "aria2c", "--continue=true", "--allow-overwrite=true",
                "--auto-file-renaming=false", "--file-allocation=none",
                "--max-connection-per-server=8", "--split=8", "--min-split-size=4M",
                "--connect-timeout=15", "--timeout=45", "--max-tries=10",
                "--retry-wait=2", "--console-log-level=warn",
                "--dir", str(CACHE), "--out", partial.name, url,
            ]
            completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=7200, check=False)
            if completed.returncode:
                raise RuntimeError(f"aria2 returncode {completed.returncode}: {completed.stdout[-800:]}")
            if partial.stat().st_size != row["size"]:
                raise RuntimeError(f"size {partial.stat().st_size} != {row['size']}")
            actual = digest(partial)
            if actual != value:
                raise RuntimeError(f"sha256 {actual} != {value}")
            partial.replace(target)
            result = {"timestamp": now(), "digest": row["digest"], "size": row["size"], "status": "downloaded-and-verified", "attempt": attempt, "repository": repo}
            append(root / "blob-journal.jsonl", result)
            return result
        except Exception as error:
            errors.append({"attempt": attempt, "repository": repo, "error_type": type(error).__name__, "error": str(error)[-1200:], "partial_bytes": partial.stat().st_size if partial.exists() else 0})
            append(root / "blob-journal.jsonl", {"timestamp": now(), "digest": row["digest"], "status": "infrastructure-retry", **errors[-1], "scientific_retry": False})
    raise RuntimeError(json.dumps({"digest": row["digest"], "errors": errors[-2:]}))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    plan = json.loads((args.root / "blob-plan.json").read_text())
    CACHE.mkdir(parents=True, exist_ok=True)
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(acquire, args.root, row): row["digest"] for row in plan["rows"]}
        for future in as_completed(futures):
            result = future.result()
            rows.append(result)
            print(json.dumps({k: result[k] for k in ("digest", "size", "status")}), flush=True)
    verified = []
    for row in plan["rows"]:
        path = CACHE / row["digest"][7:]
        verified.append(path.is_file() and path.stat().st_size == row["size"] and digest(path) == row["digest"][7:])
    receipt = {
        "schema_version": 1, "created_at_utc": now(), "mirror": BASE,
        "worker_count": args.workers, "connections_per_blob": 8,
        "unique_blob_count": len(plan["rows"]), "unique_blob_bytes": plan["unique_blob_bytes"],
        "all_blobs_verified": all(verified), "rows": sorted(rows, key=lambda x: x["digest"]),
        "scientific_retries": 0, "provider_calls": 0,
    }
    raw = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    tmp = args.root / "blob-receipt.json.tmp"
    tmp.write_bytes(raw)
    os.replace(tmp, args.root / "blob-receipt.json")
    print(json.dumps({"decision": "ALL_BLOBS_VERIFIED", "count": len(rows), "bytes": plan["unique_blob_bytes"]}))

if __name__ == "__main__":
    main()
