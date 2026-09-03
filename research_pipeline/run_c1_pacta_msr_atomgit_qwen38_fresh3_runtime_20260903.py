#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline import run_c1_pacta_msr_runtime_20260902 as base
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json, sha256_file

IMAGE_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh3-images-20260903-v2")
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh3-runtime-20260903-v1")
LAYOUT_ROOT = Path("/data/wyt/e1-stri-reasoningbank-runtime/c1-pacta-msr-atomgit-qwen38-fresh3-oci-layouts")
POOL_SHA = "3780fa80ee0bbfce01e3fd4f6bcabe6aaaa21111c0aa910ea7ce1bde302a9257"
MANIFEST_SHA = "c01683a6bb8b42d93634a4bcc0179721f7704d5fa8fe24ba308be699af94a1e8"
BLOB_PLAN_SHA = "a529f4e9dffd27004a7c225d6475d9f0cf951159015a20bb94546545dc403708"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
ROOTFUL_HOST = base.ROOTFUL_HOST


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def bind(blob_receipt_sha: str) -> None:
    if not SHA_RE.fullmatch(blob_receipt_sha):
        raise RuntimeError("STOP_FRESH3_BLOB_RECEIPT_SHA_FORMAT")
    base.IMAGE_ROOT = IMAGE_ROOT
    base.DEFAULT = DEFAULT_ROOT
    base.LAYOUT_ROOT = LAYOUT_ROOT
    base.MANIFEST_SHA = MANIFEST_SHA
    base.BLOB_RECEIPT_SHA = blob_receipt_sha


def audit_inputs(blob_receipt_sha: str) -> dict[str, Any]:
    bind(blob_receipt_sha)
    expected = {
        "manifest-freeze.json": MANIFEST_SHA,
        "blob-plan.json": BLOB_PLAN_SHA,
        "blob-receipt.json": blob_receipt_sha,
    }
    observed: dict[str, str] = {}
    for name, digest in expected.items():
        path = IMAGE_ROOT / name
        if not path.is_file():
            raise RuntimeError(f"STOP_FRESH3_RUNTIME_INPUT_MISSING:{name}")
        actual = sha256_file(path)
        observed[name] = actual
        if actual != digest:
            raise RuntimeError(f"STOP_FRESH3_RUNTIME_INPUT_HASH_DRIFT:{name}:{actual}")
    freeze = load(IMAGE_ROOT / "manifest-freeze.json")
    plan = load(IMAGE_ROOT / "blob-plan.json")
    receipt = load(IMAGE_ROOT / "blob-receipt.json")
    if freeze.get("fresh_pool_sha256") != POOL_SHA or freeze.get("image_count") != 20 or freeze.get("stable_twice") is not True:
        raise RuntimeError("STOP_FRESH3_RUNTIME_MANIFEST_GEOMETRY")
    if plan.get("unique_blob_count") != 88:
        raise RuntimeError("STOP_FRESH3_RUNTIME_BLOB_PLAN_GEOMETRY")
    if receipt.get("all_blobs_verified") is not True or receipt.get("unique_blob_count") != 88:
        raise RuntimeError("STOP_FRESH3_RUNTIME_BLOB_VERIFICATION")
    return {
        "fresh3_pool_sha256": POOL_SHA,
        "image_count": 20,
        "unique_blob_count": 88,
        "input_sha256": observed,
        "provider_calls": 0,
        "scientific_source_tasks_used": 0,
    }


def preflight(root: Path, blob_receipt_sha: str) -> dict[str, Any]:
    audit = audit_inputs(blob_receipt_sha)
    result = base.preflight(root)
    result.update({
        "fresh3_pool_sha256": POOL_SHA,
        "manifest_freeze_sha256": MANIFEST_SHA,
        "blob_plan_sha256": BLOB_PLAN_SHA,
        "blob_receipt_sha256": blob_receipt_sha,
        "scientific_source_tasks_used": 0,
    })
    atomic_json(root / "preflight.json", result)
    return result


def import_all(root: Path, blob_receipt_sha: str) -> dict[str, Any]:
    audit_inputs(blob_receipt_sha)
    pre = load(root / "preflight.json")
    if pre.get("blob_receipt_sha256") != blob_receipt_sha:
        raise RuntimeError("STOP_FRESH3_RUNTIME_PREFLIGHT_RECEIPT_DRIFT")
    return base.import_all(root)


def _run(command: list[str], timeout: int = 180) -> dict[str, Any]:
    env = os.environ.copy(); env["DOCKER_HOST"] = ROOTFUL_HOST
    try:
        p = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, env=env, check=False)
        return {"returncode": p.returncode, "output": p.stdout}
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""; out = out.decode(errors="replace") if isinstance(out, bytes) else out
        return {"returncode": 124, "output": out}


def _exec(cid: str, command: str, timeout: int = 120) -> dict[str, Any]:
    return _run(["docker", "exec", "-w", "/testbed", cid, "bash", "-lc", command], timeout)


def qualify_one(row: dict[str, Any], imported: dict[str, Any]) -> dict[str, Any]:
    keys = ("role", "unit_id", "instance_id", "base_commit", "index_digest", "amd64_digest")
    out = {key: row[key] for key in keys}
    out.update({
        "digest_ref": imported.get("digest_ref", ""),
        "image_id": imported.get("image_id", ""),
        "import_pass": bool(imported.get("import_pass")),
        "digest_inspect_pass": bool(imported.get("digest_inspect_pass")),
    })
    if not out["import_pass"] or not out["digest_inspect_pass"]:
        out.update({"container_start_pass": False, "exact_base_normalization_pass": False, "invalid_reason": "import/digest failure"})
        return out
    env = os.environ.copy(); env["DOCKER_HOST"] = ROOTFUL_HOST
    name = "c1-fresh3-clean-" + os.urandom(6).hex()
    start = subprocess.run(
        ["docker", "run", "-d", "--pull=never", "--name", name, "-w", "/testbed", "--rm", out["digest_ref"], "sleep", "30m"],
        text=True, capture_output=True, timeout=180, env=env, check=False,
    )
    out["container_start_pass"] = start.returncode == 0
    if not out["container_start_pass"]:
        out.update({"exact_base_normalization_pass": False, "invalid_reason": start.stderr[-800:]})
        return out
    cid = start.stdout.strip(); frozen_base = row["base_commit"]
    try:
        head = _exec(cid, "git rev-parse HEAD")
        tracked = _exec(cid, "git diff --quiet && git diff --cached --quiet")
        untracked = _exec(cid, "git ls-files --others --exclude-standard")
        untracked_paths = [line.strip() for line in untracked["output"].splitlines() if line.strip()]
        only_build = all(path == "build" or path.startswith("build/") for path in untracked_paths)
        exists = _exec(cid, f"git cat-file -e {frozen_base}^{{commit}}")
        ancestor = _exec(cid, f"git merge-base --is-ancestor {frozen_base} HEAD")
        tools = _exec(cid, "test -d /testbed && command -v bash && command -v git && command -v python")
        reset = _exec(cid, f"git reset --hard {frozen_base}")
        clean = _exec(cid, "git clean -fd -- build")
        post = _exec(cid, "git rev-parse HEAD")
        status = _exec(cid, "git status --porcelain=v1 --untracked-files=all")
        out.update({
            "observed_initial_head": head["output"].strip(),
            "initial_tracked_tree_clean": tracked["returncode"] == 0,
            "initial_untracked_count": len(untracked_paths),
            "initial_untracked_paths_sha256": hashlib.sha256("\n".join(untracked_paths).encode()).hexdigest(),
            "initial_untracked_only_build": only_build,
            "base_commit_exists": exists["returncode"] == 0,
            "base_is_ancestor": ancestor["returncode"] == 0,
            "runtime_tools_pass": tools["returncode"] == 0,
            "reset_pass": reset["returncode"] == 0,
            "targeted_clean_command": "git clean -fd -- build",
            "targeted_clean_pass": clean["returncode"] == 0,
            "targeted_clean_output": clean["output"],
            "post_reset_head": post["output"].strip(),
            "post_reset_head_exact": post["output"].strip() == frozen_base,
            "post_reset_working_tree_clean": status["returncode"] == 0 and not status["output"].strip(),
        })
        out["exact_base_normalization_pass"] = all([
            out["import_pass"], out["digest_inspect_pass"], out["container_start_pass"],
            out["initial_tracked_tree_clean"], out["initial_untracked_only_build"], out["base_commit_exists"],
            out["base_is_ancestor"], out["runtime_tools_pass"], out["reset_pass"], out["targeted_clean_pass"],
            out["post_reset_head_exact"], out["post_reset_working_tree_clean"],
        ])
        if not out["exact_base_normalization_pass"]:
            out["invalid_reason"] = "targeted build-clean exact-base pre/postcondition failed"
    finally:
        subprocess.run(["docker", "rm", "-f", cid], text=True, capture_output=True, timeout=120, env=env, check=False)
    return out


def qualify(root: Path, blob_receipt_sha: str) -> dict[str, Any]:
    audit_inputs(blob_receipt_sha)
    if (root / "normalization-qualification.json").exists():
        raise RuntimeError("qualification exists; no overwrite")
    imports = {row["instance_id"]: row for row in load(root / "import-receipt.json")["rows"]}
    rows = []; journal = root / "normalization-journal.jsonl"
    for frozen in base.frozen_rows():
        result = qualify_one(frozen, imports[frozen["instance_id"]])
        with journal.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n"); handle.flush(); os.fsync(handle.fileno())
        rows.append(result)
        print(json.dumps({"instance_id": result["instance_id"], "role": result["role"], "pass": result["exact_base_normalization_pass"], "untracked": result.get("initial_untracked_count")}), flush=True)
    qualified = sum(bool(row["exact_base_normalization_pass"]) for row in rows)
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "FRESH3_MSR_20_RUNTIME_READY_AFTER_TARGETED_BUILD_CLEAN" if qualified == 20 else "HOLD_FRESH3_RUNTIME_SUPPORT_INCOMPLETE",
        "qualified": qualified,
        "total": 20,
        "source_qualified": sum(row["role"] == "source" and row["exact_base_normalization_pass"] for row in rows),
        "future_qualified": sum(row["role"] == "future" and row["exact_base_normalization_pass"] for row in rows),
        "blob_receipt_sha256": blob_receipt_sha,
        "manifest_freeze_sha256": MANIFEST_SHA,
        "fresh3_pool_sha256": POOL_SHA,
        "rows": rows,
        "provider_calls": 0,
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
    }
    atomic_json(root / "normalization-qualification.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--phase", choices=("audit", "preflight", "import", "qualify"), required=True)
    parser.add_argument("--blob-receipt-sha", required=True)
    args = parser.parse_args()
    bind(args.blob_receipt_sha)
    if args.phase == "audit": result = audit_inputs(args.blob_receipt_sha)
    elif args.phase == "preflight": result = preflight(args.root, args.blob_receipt_sha)
    elif args.phase == "import": result = import_all(args.root, args.blob_receipt_sha)
    else: result = qualify(args.root, args.blob_receipt_sha)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__": main()
