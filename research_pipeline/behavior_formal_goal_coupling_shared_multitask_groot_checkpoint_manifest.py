from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
HF_REPO_ID = "kmy17518/gr00t-n1.7-b1k-multitask"
HF_REVISION = "5831e9dc0ec1212e9aaa3d96c8e27d2548718a82"
CHECKPOINT = "checkpoint-238000"
PREREG_SHA256 = "483235155b6fec941969a4a766cbe15e50f2807b06828e625942f3d731d0e231"
SOURCE_QUALIFICATION_SHA256 = "cda384bf9944c4ef6271a31d0d618d22abc27a0dbdbe700266ab656c6b9497e4"
SUBSET_QUALIFICATION_SHA256 = "da1e5abab701e3a5ab150e3abc530043ddf5f01a4b91efd7f094293a27354bf4"
PAYLOAD_MANIFEST_SHA256 = "927e9b648fb46d682450c424dde4afbc815fcda2a17351bd0b22e5f725337979"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def parse_lfs_pointer(content: bytes) -> tuple[str, int] | None:
    if not content.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
        return None
    fields = {}
    for line in content.decode("utf-8").splitlines()[1:]:
        if " " in line:
            key, value = line.split(" ", 1)
            fields[key] = value
    oid_field = fields.get("oid", "")
    size_text = fields.get("size", "")
    if not oid_field.startswith("sha256:") or not size_text.isdigit():
        raise ValueError("malformed Git LFS pointer")
    oid = oid_field.split(":", 1)[1]
    if len(oid) != 64 or any(ch not in "0123456789abcdef" for ch in oid):
        raise ValueError("invalid Git LFS sha256")
    size = int(size_text)
    if size <= 0:
        raise ValueError("invalid Git LFS size")
    return oid, size


def git_blob(repo: Path, ref_path: str) -> tuple[str, bytes]:
    line = subprocess.check_output(
        ["git", "-C", str(repo), "ls-tree", "HEAD", "--", ref_path], text=True
    ).strip()
    if not line:
        raise ValueError(f"missing checkpoint path: {ref_path}")
    left, path = line.split("\t", 1)
    _mode, obj_type, blob_sha = left.split()
    if obj_type != "blob" or path != ref_path:
        raise ValueError(f"unexpected tree entry for {ref_path}")
    env = {**os.environ, "GIT_NO_LAZY_FETCH": "1"}
    content = subprocess.check_output(
        ["git", "-C", str(repo), "cat-file", "blob", blob_sha], env=env
    )
    return blob_sha, content


def compile_manifest(repo: Path, prereg: Path, source_q: Path, subset_q: Path, payload_manifest: Path) -> dict:
    bindings = {
        "preregistration_sha256": sha256_file(prereg),
        "source_qualification_sha256": sha256_file(source_q),
        "subset_qualification_sha256": sha256_file(subset_q),
        "payload_manifest_sha256": sha256_file(payload_manifest),
    }
    expected = {
        "preregistration_sha256": PREREG_SHA256,
        "source_qualification_sha256": SOURCE_QUALIFICATION_SHA256,
        "subset_qualification_sha256": SUBSET_QUALIFICATION_SHA256,
        "payload_manifest_sha256": PAYLOAD_MANIFEST_SHA256,
    }
    if bindings != expected:
        raise ValueError(f"upstream binding drift: {bindings}")
    revision = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    if revision != HF_REVISION:
        raise ValueError(f"HF revision drift: {revision}")
    paths = subprocess.check_output(
        ["git", "-C", str(repo), "ls-tree", "-r", "--name-only", "HEAD", CHECKPOINT], text=True
    ).splitlines()
    if not paths or any(not p.startswith(CHECKPOINT + "/") for p in paths):
        raise ValueError("checkpoint tree missing or malformed")
    rows = []
    weight_bytes = 0
    inline_bytes = 0
    for path in paths:
        blob_sha, content = git_blob(repo, path)
        lfs = parse_lfs_pointer(content)
        if lfs is not None:
            oid, size = lfs
            rows.append({
                "path": path,
                "storage": "git-lfs",
                "git_blob_sha1": blob_sha,
                "lfs_oid_sha256": oid,
                "payload_size_bytes": size,
            })
            weight_bytes += size
        else:
            rows.append({
                "path": path,
                "storage": "inline-git-blob",
                "git_blob_sha1": blob_sha,
                "content_sha256": sha256_bytes(content),
                "content_size_bytes": len(content),
            })
            inline_bytes += len(content)
    readme_blob, readme = git_blob(repo, "README.md")
    if b"final = checkpoint-238000" not in readme:
        raise ValueError("model card no longer identifies checkpoint-238000 as final")
    manifest_text = "\n".join(json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows) + "\n"
    return {
        "schema_version": "behavior-formal-goal-coupling-shared-multitask-groot-checkpoint-manifest-v1",
        "object_id": OBJECT_ID,
        "status": "PUBLIC_GROOT_TERMINAL_CHECKPOINT_CONTENT_ADDRESSED_ZERO_WEIGHT_DOWNLOAD",
        "scientific_authority": False,
        "execution_authority": False,
        "gpu_authority": False,
        "model_load_authorized": False,
        "weight_payload_download_authorized": False,
        "weight_payload_bytes_downloaded": 0,
        "policy_outcomes_read": False,
        "bindings": bindings,
        "source": {
            "repo_id": HF_REPO_ID,
            "revision": HF_REVISION,
            "checkpoint": CHECKPOINT,
            "selection_rule": "terminal/final checkpoint frozen before any local policy outcome; late-snapshot shopping forbidden",
            "readme_git_blob_sha1": readme_blob,
            "readme_sha256": sha256_bytes(readme),
            "model_card_terminal_marker_verified": True,
        },
        "summary": {
            "file_count": len(rows),
            "lfs_file_count": sum(r["storage"] == "git-lfs" for r in rows),
            "inline_file_count": sum(r["storage"] == "inline-git-blob" for r in rows),
            "lfs_payload_bytes": weight_bytes,
            "lfs_payload_gib": weight_bytes / (1024 ** 3),
            "inline_bytes": inline_bytes,
            "checkpoint_manifest_sha256": hashlib.sha256(manifest_text.encode("utf-8")).hexdigest(),
        },
        "files": rows,
        "next_gate": "freeze the pi0.5 shared-subset config patch and zero-update config/data-loader smoke; no model load or optimizer update",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--prereg", type=Path, required=True)
    parser.add_argument("--source-qualification", type=Path, required=True)
    parser.add_argument("--subset-qualification", type=Path, required=True)
    parser.add_argument("--payload-manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = compile_manifest(
        args.repo, args.prereg, args.source_qualification, args.subset_qualification, args.payload_manifest
    )
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], **payload["summary"], "artifact_sha256": sha256_file(args.out)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
