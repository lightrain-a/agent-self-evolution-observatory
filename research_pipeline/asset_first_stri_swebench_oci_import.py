#!/usr/bin/env python3
"""Assemble verified OCI layouts and import them into the isolated E1 daemon."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

CACHE = Path("/data/wyt/e1-stri-reasoningbank-runtime/oci-blob-cache/sha256")
LAYOUT_ROOT = Path("/data/wyt/e1-stri-reasoningbank-runtime/oci-layouts")
SKOPEO = Path("/data/wyt/e1-stri-reasoningbank-runtime/skopeo-root/usr/bin/skopeo")
POLICY = Path("/data/wyt/e1-stri-reasoningbank-runtime/skopeo-root/etc/containers/policy.json")
DOCKER_HOST = "unix:///run/user/1006/e1-reasoningbank-docker.sock"
SPECS = (
    {
        "label": "source",
        "repo": "docker.1ms.run/swebench/sweb.eval.x86_64.sympy_1776_sympy-13798",
        "tag": "e1fixed-4111da8b",
        "manifest": Path("/data/wyt/e1-source-platform-manifest-skopeo.json"),
        "digest": "4111da8b069bc23cc67ef24f2f433f82601518941052faebd3c4a621d3748cd6",
    },
    {
        "label": "pytest",
        "repo": "docker.1ms.run/swebench/sweb.eval.x86_64.pytest-dev_1776_pytest-5631",
        "tag": "e1fixed-22a1a81b",
        "manifest": Path("/data/wyt/e1-pytest-platform-manifest-skopeo.json"),
        "digest": "22a1a81b8e937a1ff52cef4f38bf59e6a8baa0648ef3b115e6206bfc5c5de68f",
    },
    {
        "label": "sympy17318",
        "repo": "docker.1ms.run/swebench/sweb.eval.x86_64.sympy_1776_sympy-17318",
        "tag": "e1fixed-4d18e6a3",
        "manifest": Path("/data/wyt/e1-sympy17318-platform-manifest-skopeo.json"),
        "digest": "4d18e6a31fb1d68a8232f3c78a5a4c97e9c7a2d001765dcc90f228cef4b4e39f",
    },
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(command: list[str], timeout: int = 1800) -> dict:
    env = os.environ.copy()
    env["DOCKER_HOST"] = DOCKER_HOST
    completed = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, timeout=timeout, env=env, check=False,
    )
    return {"command": command, "returncode": completed.returncode, "output": completed.stdout}


def assemble(spec: dict) -> dict:
    manifest_bytes = spec["manifest"].read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != spec["digest"]:
        raise RuntimeError(f"{spec['label']} manifest digest mismatch")
    manifest = json.loads(manifest_bytes)
    layout = LAYOUT_ROOT / spec["label"]
    blob_dir = layout / "blobs/sha256"
    blob_dir.mkdir(parents=True, exist_ok=True)
    descriptors = [manifest["config"], *manifest["layers"]]
    verified = []
    for item in descriptors:
        value = item["digest"].split(":", 1)[1]
        source = CACHE / value
        if not source.exists() or source.stat().st_size != int(item["size"]):
            raise RuntimeError(f"missing verified blob {value}")
        if digest(source) != value:
            raise RuntimeError(f"blob digest mismatch {value}")
        target = blob_dir / value
        if not target.exists():
            os.link(source, target)
        verified.append({"digest": item["digest"], "size": item["size"]})
    manifest_target = blob_dir / spec["digest"]
    if not manifest_target.exists():
        manifest_target.write_bytes(manifest_bytes)
    (layout / "oci-layout").write_text(
        json.dumps({"imageLayoutVersion": "1.0.0"}) + "\n", encoding="utf-8"
    )
    descriptor = {
        "mediaType": manifest.get(
            "mediaType", "application/vnd.docker.distribution.manifest.v2+json"
        ),
        "digest": f"sha256:{spec['digest']}",
        "size": len(manifest_bytes),
        "annotations": {"org.opencontainers.image.ref.name": spec["tag"]},
        "platform": {"architecture": "amd64", "os": "linux"},
    }
    (layout / "index.json").write_text(
        json.dumps({"schemaVersion": 2, "manifests": [descriptor]}, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"layout": str(layout), "manifest": descriptor, "blobs": verified}


def import_one(spec: dict) -> dict:
    digest_ref = f"{spec['repo']}@sha256:{spec['digest']}"
    inspected = run([
        "docker", "image", "inspect", digest_ref,
        "--format", "{{json .RepoDigests}} {{.Architecture}} {{.Id}}",
    ], timeout=60)
    if inspected["returncode"] == 0 and f"sha256:{spec['digest']}" in inspected["output"]:
        return {
            "label": spec["label"], "digest_ref": digest_ref,
            "status": "verified-existing", "inspect": inspected, "pass": True,
        }
    assembled = assemble(spec)
    source = f"oci:{assembled['layout']}:{spec['tag']}"
    tagged = f"{spec['repo']}:{spec['tag']}"
    archive = LAYOUT_ROOT / f"{spec['label']}.docker-archive.tar"
    archive.unlink(missing_ok=True)
    archived = run([
        str(SKOPEO), "--policy", str(POLICY), "copy",
        "--override-arch", "amd64", source,
        f"docker-archive:{archive}:{tagged}",
    ])
    if archived["returncode"] != 0:
        raise RuntimeError(f"docker archive build failed: {archived['output'][-2000:]}")
    loaded = run(["docker", "load", "-i", str(archive)])
    if loaded["returncode"] != 0:
        raise RuntimeError(f"docker load failed: {loaded['output'][-2000:]}")
    pulled = run(["docker", "pull", digest_ref], timeout=600)
    if pulled["returncode"] != 0:
        raise RuntimeError(f"digest attachment failed: {pulled['output'][-2000:]}")
    inspected = run([
        "docker", "image", "inspect", digest_ref,
        "--format", "{{json .RepoDigests}} {{.Architecture}} {{.Id}}",
    ], timeout=60)
    if inspected["returncode"] != 0 or f"sha256:{spec['digest']}" not in inspected["output"]:
        raise RuntimeError(f"digest inspect failed: {inspected['output'][-2000:]}")
    return {
        "label": spec["label"], "source": source, "tagged": tagged,
        "digest_ref": digest_ref, "assembled": assembled,
        "archive": str(archive), "archive_sha256": digest(archive),
        "archive_build": archived, "docker_load": loaded,
        "digest_pull": pulled, "inspect": inspected,
        "status": "imported-and-verified", "pass": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--receipt", type=Path,
        default=Path("/data/wyt/e1-stri-reasoningbank-runtime/oci-layouts/import-receipt.json"),
    )
    args = parser.parse_args()
    rows = []
    for spec in SPECS:
        row = import_one(spec)
        rows.append(row)
        print(json.dumps({
            "label": row["label"], "digest_ref": row["digest_ref"], "pass": row["pass"]
        }), flush=True)
    receipt = {
        "schema_version": 1, "docker_host": DOCKER_HOST,
        "rows": rows, "all_imported_by_exact_digest": all(row["pass"] for row in rows),
        "credential_material_present": False,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": "ALL_FIXED_DIGEST_IMAGES_IMPORTED", "count": len(rows)}))


if __name__ == "__main__":
    main()
