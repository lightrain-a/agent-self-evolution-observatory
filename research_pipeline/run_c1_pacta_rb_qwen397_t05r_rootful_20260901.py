#!/usr/bin/env python3
"""T0.5-R: exact-digest import and exact-base normalization on rootful Docker.

Infrastructure only: this module has no provider, writer, binder, shadow, gate,
final-measurement, evaluator, or future-task execution path.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.c1_pacta_rb_qwen397 import atomic_json, sha256_file
from research_pipeline.run_c1_pacta_rb_qwen397_t05_images_20260901 import CACHE, SPECS, image_ref, image_repo

ROOTFUL_HOST = "unix:///var/run/docker.sock"
OLD_T05 = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t05-images-20260901-v1")
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t05r-images-rootful-20260901-v1")
LAYOUT_ROOT = Path("/data/wyt/e1-stri-reasoningbank-runtime/c1-pacta-qwen397-t05-oci-layouts")
SKOPEO = Path("/data/wyt/e1-stri-reasoningbank-runtime/skopeo-root/usr/bin/skopeo")
POLICY = Path("/data/wyt/e1-stri-reasoningbank-runtime/skopeo-root/etc/containers/policy.json")
POOL = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-p0-20260831-v1/fresh-pool.json")
OFFICIAL = Path("/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026")
OFFICIAL_COMMIT = "ed80611788292ea739f1effd31f16c53823b8a0d"
EXPECTED_CARRIER = {
    "config": ("third_party/src/minisweagent/config/extra/swebench.yaml", "d8bcea20ceb4798a99661074535abd7ba7c188bd4cbc7bd2505eb7c48e54ea41"),
    "agent": ("third_party/src/minisweagent/agents/default.py", "428a78335cbfb365ba8e6622effc8959104f08e8f32068727625bcb296da756c"),
    "writer": ("third_party/src/minisweagent/memory/instruction.py", "08e11fbeac1ba9e20d1dafb20728be24194b56bdfea33f05f6a1220ae2cc9bae"),
    "retrieval": ("third_party/src/minisweagent/memory/memory_management.py", "fe71285a878920d501013ab86b58ef12c9c08071ee0e690061774d5ff5588955"),
    "runner": ("third_party/src/minisweagent/run/extra/swebench.py", "8365112cd2dd2f3dbd74eff611b5d166530c6ddac4b09b674ae384da96531951"),
}
EXPECTED_OLD = {
    "manifest-resolution.json": "b8501421c7eda3cbfa3555de2969a7ed3d413b81727a4db67a082ca82c880b8a",
    "blob-plan.json": "7c7e5d3105e34f659fabb477d3e40c33ddff87354183c321de98d047ea5561a0",
    "blob-receipt.json": "18346047eea25fa4549aad255e6bfa900baa5b6ce8d39115afdf3a06b96fd51c",
}

def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n").encode()
    with path.open("ab") as handle:
        handle.write(raw); handle.flush(); os.fsync(handle.fileno())

def run(command: list[str], timeout: int = 1800) -> dict[str, Any]:
    env = os.environ.copy(); env["DOCKER_HOST"] = ROOTFUL_HOST
    try:
        p = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=timeout, env=env, check=False)
        return {"command": command, "returncode": p.returncode, "output": p.stdout}
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""
        if isinstance(out, bytes): out = out.decode(errors="replace")
        return {"command": command, "returncode": 124, "output": out, "timeout_seconds": timeout}

def docker_metadata() -> dict[str, Any]:
    version = run(["docker", "version", "--format", "{{json .}}"], 60)
    info = run(["docker", "info", "--format", "{{json .}}"], 60)
    if version["returncode"] or info["returncode"]:
        raise RuntimeError("STOP_ROOTFUL_DOCKER_UNAVAILABLE")
    payload = json.loads(info["output"])
    result = {
        "docker_host": ROOTFUL_HOST, "version": json.loads(version["output"]),
        "architecture": payload.get("Architecture"), "docker_root_dir": payload.get("DockerRootDir"),
        "driver": payload.get("Driver"), "security_options": payload.get("SecurityOptions") or [],
    }
    if not is_rootful_metadata(result):
        raise RuntimeError("STOP_ROOTFUL_DOCKER_UNAVAILABLE")
    return result

def is_rootful_metadata(meta: dict[str, Any]) -> bool:
    return (
        meta.get("docker_host") == ROOTFUL_HOST
        and meta.get("docker_root_dir") == "/var/lib/docker"
        and not any("rootless" in str(x).lower() for x in meta.get("security_options", []))
        and str(meta.get("architecture", "")).lower() in {"x86_64", "amd64"}
    )

def normalization_pass(row: dict[str, Any]) -> bool:
    return all(bool(row.get(key)) for key in (
        "import_pass", "digest_inspect_pass", "container_start_pass", "testbed_exists",
        "base_commit_exists", "base_is_ancestor", "initial_working_tree_clean",
        "runtime_tools_pass", "reset_pass", "post_reset_head_exact", "post_reset_working_tree_clean",
    ))

def carrier_audit() -> dict[str, Any]:
    head = subprocess.run(["git", "-C", str(OFFICIAL), "rev-parse", "HEAD"], text=True,
                          capture_output=True, check=True).stdout.strip()
    rows = {}
    for name, (relative, expected) in EXPECTED_CARRIER.items():
        path = OFFICIAL / relative; observed = sha256_file(path)
        rows[name] = {"path": str(path), "sha256": observed, "expected_sha256": expected, "pass": observed == expected}
    passed = head == OFFICIAL_COMMIT and all(x["pass"] for x in rows.values())
    return {"official_commit": head, "expected_commit": OFFICIAL_COMMIT, "files": rows, "pass": passed}

def preflight(root: Path) -> dict[str, Any]:
    if root.exists(): raise RuntimeError(f"new T0.5-R root already exists: {root}")
    root.mkdir(parents=True)
    historical = {}
    for name, expected in EXPECTED_OLD.items():
        path = OLD_T05 / name; observed = sha256_file(path) if path.is_file() else ""
        historical[name] = {"path": str(path), "sha256": observed, "expected_sha256": expected, "pass": observed == expected}
    manifest = json.loads((OLD_T05 / "manifest-resolution.json").read_text())
    if not all(x["pass"] for x in historical.values()) or not manifest["stable_twice"]:
        raise RuntimeError("HOLD_MANIFEST_FREEZE_UNREADABLE")
    carrier = carrier_audit()
    if not carrier["pass"]: raise RuntimeError("STOP_CARRIER_DRIFT")
    plan = json.loads((OLD_T05 / "blob-plan.json").read_text())
    blobs = []
    for item in plan["rows"]:
        path = Path(item["cache_path"])
        size_ok = path.is_file() and path.stat().st_size == int(item["size"])
        sha_ok = size_ok and sha256_file(path) == item["digest"][7:]
        blobs.append({"digest": item["digest"], "size": item["size"], "path": str(path),
                      "size_pass": size_ok, "sha256_pass": sha_ok})
    if not all(x["sha256_pass"] for x in blobs):
        raise RuntimeError("HOLD_BLOB_CACHE_CORRUPTION")
    result = {
        "schema_version": 1, "created_at_utc": now(), "decision": "T05R_PREFLIGHT_PASS",
        "docker": docker_metadata(), "historical_freeze": historical, "carrier": carrier,
        "manifest_stable_twice": manifest["stable_twice"], "blob_count": len(blobs),
        "blob_bytes": sum(x["size"] for x in blobs), "blobs": blobs,
        "provider_calls": 0, "source_trajectory_calls": 0, "writer_calls": 0,
        "binder_calls": 0, "shadow_calls": 0, "final_measurement_calls": 0,
    }
    atomic_json(root / "preflight.json", result)
    return result

def assemble(instance: str, amd64: str) -> tuple[Path, str]:
    manifest_path = OLD_T05 / "raw-manifests" / "pass2" / f"{instance}__amd64.json"
    raw = manifest_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != amd64: raise RuntimeError("manifest digest mismatch")
    manifest = json.loads(raw); layout = LAYOUT_ROOT / instance; blobs = layout / "blobs" / "sha256"
    blobs.mkdir(parents=True, exist_ok=True)
    for descriptor in [manifest["config"], *manifest["layers"]]:
        value = descriptor["digest"][7:]; source = CACHE / value; target = blobs / value
        if not source.is_file() or source.stat().st_size != int(descriptor["size"]) or sha256_file(source) != value:
            raise RuntimeError(f"unverified blob {value}")
        if not target.exists(): os.link(source, target)
    target_manifest = blobs / amd64
    if not target_manifest.exists(): os.link(manifest_path, target_manifest)
    elif sha256_file(target_manifest) != amd64: raise RuntimeError("layout manifest corruption")
    (layout / "oci-layout").write_text('{"imageLayoutVersion":"1.0.0"}\n')
    fixed_tag = f"t05r-{amd64[:12]}"
    descriptor = {"mediaType": manifest.get("mediaType", "application/vnd.docker.distribution.manifest.v2+json"),
                  "digest": f"sha256:{amd64}", "size": len(raw),
                  "annotations": {"org.opencontainers.image.ref.name": fixed_tag},
                  "platform": {"architecture": "amd64", "os": "linux"}}
    (layout / "index.json").write_text(json.dumps({"schemaVersion": 2, "manifests": [descriptor]}, indent=2) + "\n")
    return layout, fixed_tag

def import_one(instance: str, amd64: str) -> dict[str, Any]:
    repo = "docker.1ms.run/" + image_repo(instance); digest_ref = f"{repo}@sha256:{amd64}"
    inspect = run(["docker", "image", "inspect", digest_ref, "--format", "{{json .RepoDigests}}|{{.Architecture}}|{{.Id}}"], 60)
    if inspect["returncode"] or f"sha256:{amd64}" not in inspect["output"]:
        layout, fixed_tag = assemble(instance, amd64)
        archive = LAYOUT_ROOT / f"{instance}.t05r.docker-archive.tar"; archive.unlink(missing_ok=True)
        tagged = f"{repo}:{fixed_tag}"
        archived = run([str(SKOPEO), "--policy", str(POLICY), "copy", "--override-arch", "amd64",
                        f"oci:{layout}:{fixed_tag}", f"docker-archive:{archive}:{tagged}"], 3600)
        if archived["returncode"]: raise RuntimeError(f"archive failed: {archived['output'][-1200:]}")
        loaded = run(["docker", "load", "-i", str(archive)], 3600); archive.unlink(missing_ok=True)
        if loaded["returncode"]: raise RuntimeError(f"load failed: {loaded['output'][-1200:]}")
        attached = run(["docker", "pull", digest_ref], 1800)
        if attached["returncode"]: raise RuntimeError(f"digest attachment failed: {attached['output'][-1200:]}")
        inspect = run(["docker", "image", "inspect", digest_ref,
                       "--format", "{{json .RepoDigests}}|{{.Architecture}}|{{.Id}}"], 60)
    passed = not inspect["returncode"] and f"sha256:{amd64}" in inspect["output"] and "amd64" in inspect["output"]
    if not passed: raise RuntimeError(f"exact digest inspect failed: {inspect['output'][-1000:]}")
    image_id = inspect["output"].strip().split("|")[-1]
    tag = run(["docker", "tag", digest_ref, image_ref(instance)], 60)
    if tag["returncode"]: raise RuntimeError("canonical tag failed")
    return {"instance_id": instance, "digest_ref": digest_ref, "amd64_digest": f"sha256:{amd64}",
            "image_id": image_id, "inspect": inspect, "import_pass": True, "digest_inspect_pass": True}

def import_all(root: Path) -> dict[str, Any]:
    if not (root / "preflight.json").is_file(): raise RuntimeError("preflight missing")
    if (root / "import-receipt.json").exists(): raise RuntimeError("import receipt exists")
    journal = root / "import-journal.jsonl"; done = {}
    if journal.exists():
        for line in journal.read_text().splitlines():
            if line.strip():
                row = json.loads(line); done[row["instance_id"]] = row
    rows = []
    for instance, index_digest, amd64 in SPECS:
        if instance in done: row = done[instance]
        else:
            try: row = import_one(instance, amd64)
            except Exception as exc:
                row = {"instance_id": instance, "amd64_digest": f"sha256:{amd64}", "import_pass": False,
                       "digest_inspect_pass": False, "invalid_reason": f"{type(exc).__name__}: {exc}"}
            row["index_digest"] = f"sha256:{index_digest}"; append_jsonl(journal, row); done[instance] = row
        rows.append(row); print(json.dumps({"instance_id": instance, "import_pass": row["import_pass"]}), flush=True)
    count = sum(x["import_pass"] and x["digest_inspect_pass"] for x in rows)
    result = {"schema_version": 1, "created_at_utc": now(), "docker": docker_metadata(),
              "rows": rows, "imported": count, "total": 11,
              "decision": "T05R_IMPORT_PASS" if count == 11 else "T05R_IMPORT_INCOMPLETE",
              "provider_calls": 0, "source_trajectory_calls": 0}
    atomic_json(root / "import-receipt.json", result); return result

def exec_in(cid: str, command: str, timeout: int = 120) -> dict[str, Any]:
    return run(["docker", "exec", "-w", "/testbed", cid, "bash", "-lc", command], timeout)

def qualify_one(instance: str, index_digest: str, amd64: str, base: str, imported: dict[str, Any]) -> dict[str, Any]:
    digest_ref = f"docker.1ms.run/{image_repo(instance)}@sha256:{amd64}"
    row: dict[str, Any] = {"instance_id": instance, "index_digest": f"sha256:{index_digest}",
                          "amd64_digest": f"sha256:{amd64}", "digest_ref": digest_ref,
                          "frozen_base_commit": base, "import_pass": bool(imported.get("import_pass")),
                          "digest_inspect_pass": bool(imported.get("digest_inspect_pass")),
                          "image_id": imported.get("image_id", "")}
    if not row["import_pass"]:
        row.update({"container_start_pass": False, "exact_base_normalization_pass": False,
                    "invalid_reason": imported.get("invalid_reason", "import failed")}); return row
    name = "c1-t05r-" + os.urandom(6).hex()
    started = run(["docker", "run", "-d", "--pull=never", "--name", name, "-w", "/testbed",
                   "--rm", digest_ref, "sleep", "30m"], 180)
    row["container_start_pass"] = started["returncode"] == 0
    if not row["container_start_pass"]:
        row.update({"exact_base_normalization_pass": False, "invalid_reason": started["output"][-1000:]}); return row
    cid = started["output"].strip()
    try:
        observed = exec_in(cid, "git rev-parse HEAD")
        testbed = exec_in(cid, "test -d /testbed")
        initial_status = exec_in(cid, "test -z \"$(git status --porcelain)\"")
        exists = exec_in(cid, f"git cat-file -e {base}^{{commit}}")
        ancestor = exec_in(cid, f"git merge-base --is-ancestor {base} HEAD")
        tools = exec_in(cid, "command -v bash && command -v git && command -v python")
        reset = exec_in(cid, f"git reset --hard {base}")
        post_head = exec_in(cid, "git rev-parse HEAD")
        post_clean = exec_in(cid, "test -z \"$(git status --porcelain)\"")
        row.update({
            "testbed_exists": testbed["returncode"] == 0,
            "observed_initial_head": observed["output"].strip(),
            "initial_working_tree_clean": initial_status["returncode"] == 0,
            "base_commit_exists": exists["returncode"] == 0,
            "base_is_ancestor": ancestor["returncode"] == 0,
            "runtime_tools_pass": tools["returncode"] == 0,
            "runtime_tools_output": tools["output"],
            "reset_command_output": reset["output"], "reset_pass": reset["returncode"] == 0,
            "post_reset_head": post_head["output"].strip(),
            "post_reset_head_exact": post_head["output"].strip() == base,
            "post_reset_working_tree_clean": post_clean["returncode"] == 0,
        })
        row["exact_base_normalization_pass"] = normalization_pass(row)
        if not row["exact_base_normalization_pass"]: row["invalid_reason"] = "exact-base normalization pre/postcondition failed"
    finally:
        run(["docker", "rm", "-f", cid], 120)
    return row

def qualify(root: Path) -> dict[str, Any]:
    if (root / "normalization-qualification.json").exists(): raise RuntimeError("qualification exists")
    imports = {x["instance_id"]: x for x in json.loads((root / "import-receipt.json").read_text())["rows"]}
    pool = json.loads(POOL.read_text()); units = {x["source_task_id"]: x for x in pool["units"]}
    journal = root / "normalization-journal.jsonl"; done = {}
    if journal.exists():
        for line in journal.read_text().splitlines():
            if line.strip():
                row = json.loads(line); done[row["instance_id"]] = row
    rows = []
    for instance, index_digest, amd64 in SPECS:
        if instance in done: row = done[instance]
        else:
            row = qualify_one(instance, index_digest, amd64, units[instance]["source_base_commit"], imports[instance])
            append_jsonl(journal, row); done[instance] = row
        rows.append(row); print(json.dumps({"instance_id": instance, "exact_base": row["exact_base_normalization_pass"]}), flush=True)
    count = sum(x["exact_base_normalization_pass"] for x in rows)
    decision = "T0_5R_ROOTFUL_RUNTIME_READY" if count == 11 else (
        "STOP_REDUCED_RESERVE_RUNTIME_SUPPORT" if count >= 6 else "HOLD_FRESH_RUNTIME_SUPPORT_INSUFFICIENT")
    result = {"schema_version": 1, "created_at_utc": now(), "docker": docker_metadata(), "rows": rows,
              "qualified": count, "total": 11, "decision": decision, "provider_calls": 0,
              "source_trajectory_calls": 0, "writer_calls": 0, "binder_calls": 0,
              "shadow_calls": 0, "final_measurement_calls": 0, "future_task_executions": 0}
    atomic_json(root / "normalization-qualification.json", result); return result

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--phase", choices=("preflight", "import", "qualify"), required=True)
    args = parser.parse_args()
    if args.phase == "preflight": result = preflight(args.root)
    elif args.phase == "import": result = import_all(args.root)
    else: result = qualify(args.root)
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
