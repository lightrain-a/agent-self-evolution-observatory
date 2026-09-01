#!/usr/bin/env python3
"""Assemble, import, and runtime-qualify T0.5 exact SWE-bench images."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.run_c1_pacta_rb_qwen397_t05_images_20260901 import (
    CACHE, DOCKER_HOST, SPECS, atomic_json, image_ref, image_repo, sha_file,
)

DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t05-images-20260901-v1")
LAYOUT_ROOT = Path("/data/wyt/e1-stri-reasoningbank-runtime/c1-pacta-qwen397-t05-oci-layouts")
SKOPEO = Path("/data/wyt/e1-stri-reasoningbank-runtime/skopeo-root/usr/bin/skopeo")
POLICY = Path("/data/wyt/e1-stri-reasoningbank-runtime/skopeo-root/etc/containers/policy.json")
POOL = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-p0-20260831-v1/fresh-pool.json")

def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def run(command: list[str], timeout: int = 1800) -> dict[str, Any]:
    env = os.environ.copy()
    env["DOCKER_HOST"] = DOCKER_HOST
    completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout, env=env, check=False)
    return {"command": command, "returncode": completed.returncode, "output": completed.stdout}

def assemble(root: Path, instance: str, amd64: str) -> tuple[Path, str]:
    manifest_path = root / "raw-manifests" / "pass2" / f"{instance}__amd64.json"
    raw = manifest_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != amd64:
        raise RuntimeError(f"manifest digest mismatch for {instance}")
    manifest = json.loads(raw)
    layout = LAYOUT_ROOT / instance
    blob_dir = layout / "blobs" / "sha256"
    blob_dir.mkdir(parents=True, exist_ok=True)
    for item in [manifest["config"], *manifest["layers"]]:
        value = item["digest"][7:]
        source = CACHE / value
        if not source.is_file() or source.stat().st_size != int(item["size"]) or sha_file(source) != value:
            raise RuntimeError(f"missing/unverified blob {value}")
        target = blob_dir / value
        if not target.exists():
            os.link(source, target)
    manifest_target = blob_dir / amd64
    if manifest_target.exists():
        if sha_file(manifest_target) != amd64:
            raise RuntimeError("existing layout manifest corruption")
    else:
        os.link(manifest_path, manifest_target)
    (layout / "oci-layout").write_text('{"imageLayoutVersion":"1.0.0"}\n')
    fixed_tag = f"t05fixed-{amd64[:12]}"
    descriptor = {
        "mediaType": manifest.get("mediaType", "application/vnd.docker.distribution.manifest.v2+json"),
        "digest": f"sha256:{amd64}", "size": len(raw),
        "annotations": {"org.opencontainers.image.ref.name": fixed_tag},
        "platform": {"architecture": "amd64", "os": "linux"},
    }
    (layout / "index.json").write_text(json.dumps({"schemaVersion": 2, "manifests": [descriptor]}, indent=2) + "\n")
    return layout, fixed_tag

def import_one(root: Path, instance: str, amd64: str) -> dict[str, Any]:
    registry_repo = "docker.1ms.run/" + image_repo(instance)
    digest_ref = f"{registry_repo}@sha256:{amd64}"
    inspected = run(["docker", "image", "inspect", digest_ref, "--format", "{{json .RepoDigests}} {{.Architecture}} {{.Id}}"], 60)
    if inspected["returncode"] != 0 or f"sha256:{amd64}" not in inspected["output"]:
        layout, fixed_tag = assemble(root, instance, amd64)
        archive = LAYOUT_ROOT / f"{instance}.docker-archive.tar"
        archive.unlink(missing_ok=True)
        tagged = f"{registry_repo}:{fixed_tag}"
        archived = run([str(SKOPEO), "--policy", str(POLICY), "copy", "--override-arch", "amd64", f"oci:{layout}:{fixed_tag}", f"docker-archive:{archive}:{tagged}"], 3600)
        if archived["returncode"]:
            raise RuntimeError(f"archive build failed {instance}: {archived['output'][-1500:]}")
        loaded = run(["docker", "load", "-i", str(archive)], 3600)
        archive.unlink(missing_ok=True)
        if loaded["returncode"]:
            raise RuntimeError(f"docker load failed {instance}: {loaded['output'][-1500:]}")
        attached = run(["docker", "pull", digest_ref], 1800)
        if attached["returncode"]:
            raise RuntimeError(f"digest attachment failed {instance}: {attached['output'][-1500:]}")
        inspected = run(["docker", "image", "inspect", digest_ref, "--format", "{{json .RepoDigests}} {{.Architecture}} {{.Id}}"], 60)
    exact = inspected["returncode"] == 0 and f"sha256:{amd64}" in inspected["output"] and "amd64" in inspected["output"]
    if not exact:
        raise RuntimeError(f"exact digest inspect failed {instance}: {inspected['output'][-1000:]}")
    canonical = image_ref(instance)
    tagged_result = run(["docker", "tag", digest_ref, canonical], 60)
    if tagged_result["returncode"]:
        raise RuntimeError(f"canonical tag failed {instance}")
    return {"instance_id": instance, "digest_ref": digest_ref, "canonical_reference": canonical, "amd64_digest": f"sha256:{amd64}", "inspect": inspected, "exact_digest_pass": exact}

def docker_metadata() -> dict[str, Any]:
    version = run(["docker", "version", "--format", "{{json .}}"], 60)
    info = run(["docker", "info", "--format", "{{json .}}"], 60)
    if version["returncode"] or info["returncode"]:
        raise RuntimeError("isolated docker unavailable")
    payload = json.loads(info["output"])
    return {"docker_host": DOCKER_HOST, "version": json.loads(version["output"]), "architecture": payload.get("Architecture"), "docker_root_dir": payload.get("DockerRootDir"), "driver": payload.get("Driver")}

def qualify(root: Path) -> dict[str, Any]:
    pool = json.loads(POOL.read_text())
    units = {row["source_task_id"]: row for row in pool["units"]}
    rows = []
    for instance, _index, amd64 in SPECS:
        unit = units[instance]
        digest_ref = f"docker.1ms.run/{image_repo(instance)}@sha256:{amd64}"
        check = run(["docker", "run", "--rm", digest_ref, "sh", "-lc", "cd /testbed && printf 'HEAD=' && git rev-parse HEAD && printf 'DIRTY=' && git status --porcelain | wc -l && printf 'BASH=' && command -v bash && printf 'GIT=' && command -v git && printf 'PYTHON=' && command -v python"], 180)
        values = {}
        for line in check["output"].splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                values[key] = value
        observed = values.get("HEAD", "")
        row = {
            "instance_id": instance, "repository": unit["task_family"], "digest_ref": digest_ref,
            "expected_base_commit": unit["source_base_commit"], "observed_base_commit": observed,
            "container_start_pass": check["returncode"] == 0,
            "base_commit_pass": observed == unit["source_base_commit"],
            "working_tree_equivalent": values.get("DIRTY") == "0",
            "runtime_prerequisites_pass": all(values.get(k) for k in ("BASH", "GIT", "PYTHON")),
            "tests_executed": 0, "evaluator_calls": 0, "future_task_executions": 0, "provider_calls": 0,
            "raw_check_output": check["output"],
        }
        row["runtime_qualified"] = all(row[k] for k in ("container_start_pass", "base_commit_pass", "working_tree_equivalent", "runtime_prerequisites_pass"))
        rows.append(row)
        print(json.dumps({"instance_id": instance, "runtime_qualified": row["runtime_qualified"], "base_commit": observed}), flush=True)
    count = sum(row["runtime_qualified"] for row in rows)
    decision = "T0_5_FIXED_IMAGES_READY" if count == 11 else ("STOP_REDUCED_RESERVE_IMAGE_SUPPORT" if count >= 6 else "HOLD_FRESH_RUNTIME_SUPPORT_INSUFFICIENT")
    result = {"schema_version": 1, "created_at_utc": now(), "docker": docker_metadata(), "qualified_images": count, "total_images": 11, "rows": rows, "decision": decision, "scientific_calls": 0}
    atomic_json(root / "runtime-qualification.json", result)
    return result

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--phase", choices=("import", "qualify"), required=True)
    args = parser.parse_args()
    if args.phase == "import":
        receipt = args.root / "import-receipt.json"
        if receipt.exists():
            raise RuntimeError("import receipt exists; no overwrite")
        journal = args.root / "import-journal.jsonl"
        completed: dict[str, dict[str, Any]] = {}
        if journal.exists():
            for line in journal.read_text().splitlines():
                if line.strip():
                    row = json.loads(line)
                    completed[row["instance_id"]] = row
        rows = []
        for instance, _index, amd64 in SPECS:
            if instance in completed:
                row = completed[instance]
            else:
                try:
                    row = import_one(args.root, instance, amd64)
                except Exception as exc:  # persist the infrastructure differential and continue the fixed list
                    row = {
                        "instance_id": instance,
                        "amd64_digest": f"sha256:{amd64}",
                        "exact_digest_pass": False,
                        "invalid_reason": f"{type(exc).__name__}: {exc}",
                    }
                with journal.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(row, sort_keys=True) + "\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                completed[instance] = row
            rows.append(row)
            print(json.dumps({"instance_id": instance, "exact_digest_pass": row["exact_digest_pass"]}), flush=True)
        imported = sum(bool(row["exact_digest_pass"]) for row in rows)
        result = {
            "schema_version": 1,
            "created_at_utc": now(),
            "docker": docker_metadata(),
            "rows": rows,
            "imported_by_exact_digest": imported,
            "total_images": len(rows),
            "all_imported_by_exact_digest": imported == len(rows),
            "decision": "ALL_FIXED_DIGEST_IMAGES_IMPORTED" if imported == len(rows) else "EXACT_DIGEST_IMPORT_INCOMPLETE",
            "provider_calls": 0,
        }
        atomic_json(receipt, result)
    else:
        if (args.root / "runtime-qualification.json").exists():
            raise RuntimeError("runtime qualification exists; no overwrite")
        print(json.dumps(qualify(args.root), sort_keys=True))

if __name__ == "__main__":
    main()
