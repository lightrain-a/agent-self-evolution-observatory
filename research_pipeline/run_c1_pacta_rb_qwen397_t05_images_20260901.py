#!/usr/bin/env python3
"""T0.5 exact-image acquisition for the frozen C1 PACTA Qwen397 source pool.

This is infrastructure-only. It cannot call a language model, writer, binder,
shadow policy, PACTA gate, future task, or evaluator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

MIRROR = "https://docker.1ms.run"
DOCKER_HOST = "unix:///run/user/1006/e1-reasoningbank-docker.sock"
CACHE = Path("/data/wyt/e1-stri-reasoningbank-runtime/oci-blob-cache/sha256")
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t05-images-20260901-v1")
ACCEPT_INDEX = "application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json"
ACCEPT_MANIFEST = "application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json"

SPECS = (
    ("pydata__xarray-4966", "71780cdb18ee29fba095dff8090508a77cba28826c80f2bb19ac2425acd95cbf", "445adac04fe8ac03a165c2e91adc1cfb3f41c20bdfa977ca195698c23d1876e5"),
    ("scikit-learn__scikit-learn-14496", "9fb17db38a54b0ddc8663bea55f1dab894491ebc6d75e4899a1ba76662d0c51b", "a1d4ade93c453ff019f6007d735ed1a8e02fdff7495cabe8cbdd87b83c910779"),
    ("psf__requests-1766", "0618949b48408350dfae74d27e47ff9df8192fbf03248aa4f10650e0a36f52eb", "3a56b7500100dfd495ff45d09196597fad0a4f8937d0ab7430c648c5002545df"),
    ("matplotlib__matplotlib-24627", "476e2188798df71e5e904360d15fe2c6fe23c7f215eb3dafd3001688cbc40adc", "526b4c5c1b786ecf4dbfecb7c3ef847a0749d2de721932871abb46d8ca3dd6d8"),
    ("sphinx-doc__sphinx-8593", "815b32905af211560f2ccece18e672fb3660569d3f00b3b6c663fe55efe8e6a8", "bf09a4f64ca8a2dd3c9e2d252d640ed0239e6b2927fa524e40b6cde7aa0fafc0"),
    ("mwaskom__seaborn-3187", "aea7e43b20703256f5cb807b54cd78a12601f21086d3a62a41de18c254771f4e", "6c0cd3296b90a84889796531ab87a0ed8779015b2bbd2e8d99adbdef95397b03"),
    ("sympy__sympy-15599", "b7e6e69c4defe6eb7fe5c57ff3c946d94f7a2048523de41516d209a9b9d00016", "068c2c597f9dffc4344f276d9a9d1e0557b9e32b15b8ff4c4ffba76995ce6853"),
    ("astropy__astropy-7166", "4b46c92697326df9440868e8990289755954dd739a1ff27a4ad1371da6a63ce2", "cef0666d736b54a87c99d615690d343a381ca0cddc5d10d62811b82427ee98b4"),
    ("django__django-13449", "91f82064e9031f4fb86afddbe286409946109544df3b2b272f4ee6b6a7d7567c", "37219d2a63db909b824e1ff8c742283b5ea30047293a47098fe9249cfbc7b316"),
    ("pylint-dev__pylint-7080", "3389f0d1319ca611d04a209fc30990c131e0bae9acfeb2163938c75ad23479fe", "d81b3855816c07747fbfd694352ce24fb8152cec70d136b292de55ff6afe2db6"),
    ("pytest-dev__pytest-5840", "21a4deef9114348ab02986927e057d6bc0caf46fceca06414493f91ce4c64283", "f2e8a2039f31a889902cb311f03b58fb85c1840b51172d1e7ff30727eb3945d8"),
)

def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()

def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def atomic_bytes(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)
    dir_fd = os.open(path.parent, os.O_DIRECTORY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)
    return sha_bytes(data)

def atomic_json(path: Path, value: Any) -> str:
    return atomic_bytes(path, canonical(value))

def image_repo(instance: str) -> str:
    return "swebench/sweb.eval.x86_64." + instance.replace("__", "_1776_").lower()

def image_ref(instance: str) -> str:
    return image_repo(instance) + ":latest"

def token_for(repo: str, session: requests.Session) -> str:
    probe = session.get(f"{MIRROR}/v2/{repo}/manifests/latest", timeout=30)
    if probe.status_code != 401:
        probe.raise_for_status()
    fields = dict(re.findall(r'(\w+)="([^"]+)"', probe.headers.get("www-authenticate", "")))
    response = session.get(fields["realm"], params={"service": fields["service"], "scope": f"repository:{repo}:pull"}, timeout=30)
    response.raise_for_status()
    payload = response.json()
    return payload.get("token") or payload["access_token"]

def get_raw(repo: str, reference: str, accept: str, session: requests.Session) -> tuple[bytes, dict[str, str]]:
    token = token_for(repo, session)
    response = session.get(
        f"{MIRROR}/v2/{repo}/manifests/{reference}",
        headers={"Authorization": f"Bearer {token}", "Accept": accept},
        timeout=60,
    )
    response.raise_for_status()
    return response.content, {k.lower(): v for k, v in response.headers.items()}

def unique_amd64(index: dict[str, Any]) -> dict[str, Any]:
    rows = [
        row for row in index.get("manifests", [])
        if row.get("platform", {}).get("os") == "linux"
        and row.get("platform", {}).get("architecture") == "amd64"
        and not row.get("platform", {}).get("variant")
    ]
    if len(rows) != 1:
        raise RuntimeError(f"expected exactly one linux/amd64 child, got {len(rows)}")
    return rows[0]

def resolve_once(root: Path, pass_no: int, instance: str, expected_index: str, expected_amd64: str) -> dict[str, Any]:
    repo = image_repo(instance)
    session = requests.Session()
    raw_index, index_headers = get_raw(repo, "latest", ACCEPT_INDEX, session)
    index_path = root / "raw-manifests" / f"pass{pass_no}" / f"{instance}__index.json"
    index_sha = atomic_bytes(index_path, raw_index)
    index_header_digest = index_headers.get("docker-content-digest", "")
    if index_header_digest != f"sha256:{index_sha}":
        raise RuntimeError(f"index header/content digest mismatch for {instance}")
    index = json.loads(raw_index)
    child = unique_amd64(index)
    amd64_digest = child["digest"]
    raw_child, child_headers = get_raw(repo, amd64_digest, ACCEPT_MANIFEST, session)
    child_path = root / "raw-manifests" / f"pass{pass_no}" / f"{instance}__amd64.json"
    child_sha = atomic_bytes(child_path, raw_child)
    child_header_digest = child_headers.get("docker-content-digest", "")
    if child_header_digest != f"sha256:{child_sha}" or amd64_digest != f"sha256:{child_sha}":
        raise RuntimeError(f"child header/index/content digest mismatch for {instance}")
    return {
        "instance_id": instance,
        "image_reference": image_ref(instance),
        "repository": repo,
        "pass": pass_no,
        "index_path": str(index_path),
        "index_sha256": index_sha,
        "index_docker_content_digest": index_header_digest,
        "amd64_path": str(child_path),
        "amd64_sha256": child_sha,
        "amd64_docker_content_digest": child_header_digest,
        "expected_index_sha256": expected_index,
        "expected_amd64_sha256": expected_amd64,
        "observation_match": index_sha == expected_index and child_sha == expected_amd64,
        "resolved_at_utc": now(),
    }

def resolve(root: Path) -> dict[str, Any]:
    if (root / "manifest-resolution.json").exists():
        raise RuntimeError("manifest resolution already finalized; no overwrite")
    root.mkdir(parents=True, exist_ok=True)
    rows = []
    for pass_no in (1, 2):
        for spec in SPECS:
            row = resolve_once(root, pass_no, *spec)
            rows.append(row)
            print(json.dumps({"instance_id": row["instance_id"], "pass": pass_no, "index": row["index_sha256"], "amd64": row["amd64_sha256"]}), flush=True)
    by: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by.setdefault(row["instance_id"], []).append(row)
    stable = all(
        len(items) == 2
        and items[0]["index_sha256"] == items[1]["index_sha256"]
        and items[0]["amd64_sha256"] == items[1]["amd64_sha256"]
        for items in by.values()
    )
    observations = all(row["observation_match"] for row in rows)
    decision = "MANIFESTS_STABLE_AND_OBSERVATIONS_MATCH" if stable and observations else (
        "IMAGE_DIGEST_CHANGED_SINCE_PREFLIGHT_OBSERVATION" if stable else "IMAGE_TAG_RESOLUTION_UNSTABLE"
    )
    result = {"schema_version": 1, "created_at_utc": now(), "mirror": MIRROR, "rows": rows, "stable_twice": stable, "supplied_observations_match": observations, "decision": decision, "provider_calls": 0, "scientific_calls": 0}
    atomic_json(root / "manifest-resolution.json", result)
    if decision != "MANIFESTS_STABLE_AND_OBSERVATIONS_MATCH":
        raise RuntimeError(decision)
    inventory: dict[str, dict[str, Any]] = {}
    images = []
    for instance, expected_index, expected_amd64 in SPECS:
        manifest_path = root / "raw-manifests" / "pass2" / f"{instance}__amd64.json"
        manifest = json.loads(manifest_path.read_bytes())
        descriptors = [manifest["config"], *manifest["layers"]]
        for item in descriptors:
            digest = item["digest"]
            current = inventory.setdefault(digest, {"digest": digest, "size": int(item["size"]), "repositories": []})
            if current["size"] != int(item["size"]):
                raise RuntimeError("shared blob size mismatch")
            current["repositories"].append(image_repo(instance))
        images.append({"instance_id": instance, "image_reference": image_ref(instance), "index_digest": f"sha256:{expected_index}", "amd64_digest": f"sha256:{expected_amd64}", "manifest_path": str(manifest_path), "config_digest": manifest["config"]["digest"], "layer_count": len(manifest["layers"])})
    cache_rows = []
    for digest, item in sorted(inventory.items()):
        path = CACHE / digest[7:]
        exists = path.is_file()
        size_ok = exists and path.stat().st_size == item["size"]
        sha_ok = size_ok and sha_file(path) == digest[7:]
        cache_rows.append({**item, "cache_path": str(path), "exists": exists, "size_ok": size_ok, "sha256_ok": sha_ok, "reusable": sha_ok})
    plan = {
        "schema_version": 1, "created_at_utc": now(), "cache": str(CACHE), "images": images,
        "unique_blob_count": len(cache_rows), "unique_blob_bytes": sum(row["size"] for row in cache_rows),
        "reusable_blob_count": sum(row["reusable"] for row in cache_rows),
        "reusable_blob_bytes": sum(row["size"] for row in cache_rows if row["reusable"]),
        "missing_blob_count": sum(not row["reusable"] for row in cache_rows),
        "missing_blob_bytes": sum(row["size"] for row in cache_rows if not row["reusable"]),
        "rows": cache_rows, "scientific_calls": 0,
    }
    atomic_json(root / "blob-plan.json", plan)
    return result

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--phase", choices=("resolve",), required=True)
    args = parser.parse_args()
    if args.phase == "resolve":
        result = resolve(args.root)
        print(json.dumps({"decision": result["decision"], "image_count": len(SPECS)}))

if __name__ == "__main__":
    main()
