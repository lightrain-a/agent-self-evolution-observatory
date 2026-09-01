from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.relational_topology_real_corpus import (
    audit_pair, compile_pair, jsonl_bytes, load_object_types, sha256_file,
)
from research_pipeline.relational_topology_real_protocol import (
    CLIP_MODEL, CLIP_REVISION, DATASET_REVISION, PROTOCOL_ID, REAL_GLOBAL_SEED,
    REAL_REGIME_SLOT_COUNTS, SHARED_SLOTS,
)
from research_pipeline.relational_topology_training_qualification import (
    LICENSE_RECEIPT, canonical_bytes, require_license,
)

OBJECT_ID = "RELATIONAL-TOPOLOGY-STAGE-3D-20260831"
RUN_ID = f"{OBJECT_ID}-real-corpus-qualification-v3"
INSTRUCTSCENE_SHA = "a9097a62c484c56ac7be5ec2928ef497cbbaaf24"
SCENENAT_SHA = "542b82ff0cda4e0350575ca8f1cd5d147529130c"
SPLIT_SHA = "f8f144f2380668b7db999d1b21b0331ade27b72f7e4892b43da068559ffb6d79"
EXPECTED = {
    "InstructScene.zip": (4968734935, "705c14271c1dcd588d8e6e36970f9a02c5b77902be446d26af73f04b2563272d"),
    "3D-FRONT.zip": (26400916556, "97a3bcaa1cba416f20f5e5aee969b0cffc31e1588b9b780391d318d0e0b97d15"),
    "threedfront_objfeat_vqvae_epoch_01999.pth": (365619721, "e1c577fd55681138c7191394db5113cedcb4da5ffab2eac7272d399c33bb9cb4"),
    "objfeat_bounds.pkl": (159, "e2f290af3fe934443fce03f8d2f34adbffaf7974dcab349d517723205d4d0d30"),
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def verify_repo(path: Path, expected: str) -> None:
    actual = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    if actual != expected:
        raise SystemExit(f"source repo drift: {path}: {actual}")


def verify_sources(dataset_root: Path, instructscene: Path, scenenat: Path) -> dict[str, Any]:
    verify_repo(instructscene, INSTRUCTSCENE_SHA)
    verify_repo(scenenat, SCENENAT_SHA)
    downloads = dataset_root / "downloads"
    assets: dict[str, Any] = {}
    for name, (expected_size, expected_sha) in EXPECTED.items():
        path = downloads / name
        actual_size = path.stat().st_size
        actual_sha = sha256_file(path)
        if actual_size != expected_size or actual_sha != expected_sha:
            raise SystemExit(f"frozen source drift: {name}: size={actual_size} sha={actual_sha}")
        assets[name] = {"bytes": actual_size, "sha256": actual_sha}
    is_split = instructscene / "configs/bedroom_threed_front_splits.csv"
    sn_split = scenenat / "dataset/bedroom_threed_front_splits.csv"
    is_sha, sn_sha = sha256_file(is_split), sha256_file(sn_split)
    if is_sha != SPLIT_SHA or sn_sha != SPLIT_SHA or is_split.read_bytes() != sn_split.read_bytes():
        raise SystemExit("BEDROOM split mismatch")
    return {
        "dataset_revision": DATASET_REVISION,
        "instructscene_repo_sha": INSTRUCTSCENE_SHA,
        "scenenat_repo_sha": SCENENAT_SHA,
        "bedroom_split_sha256": SPLIT_SHA,
        "bedroom_split_byte_identical": True,
        "assets": assets,
    }


def seal_3dfront_extraction(dataset_root: Path) -> dict[str, Any]:
    status = dataset_root / "3dfront_extract.status"
    if not status.exists() or status.read_text().strip() != "PASS":
        raise SystemExit("3D-FRONT extraction is not sealed PASS")
    archive = dataset_root / "downloads/3D-FRONT.zip"
    materialized = dataset_root / "materialized"
    missing: list[str] = []
    size_mismatch: list[dict[str, Any]] = []
    member_count = 0
    total_bytes = 0
    with zipfile.ZipFile(archive) as handle:
        for info in handle.infolist():
            if info.is_dir():
                continue
            member_count += 1
            total_bytes += info.file_size
            target = materialized / info.filename
            if not target.is_file():
                if len(missing) < 20:
                    missing.append(info.filename)
                continue
            actual = target.stat().st_size
            if actual != info.file_size and len(size_mismatch) < 20:
                size_mismatch.append({"member": info.filename, "expected": info.file_size, "actual": actual})
    if missing or size_mismatch:
        raise SystemExit(f"3D-FRONT extraction seal failed: missing={missing} mismatch={size_mismatch}")
    return {
        "status": "PASS",
        "archive_sha256": EXPECTED["3D-FRONT.zip"][1],
        "archive_bytes": EXPECTED["3D-FRONT.zip"][0],
        "file_members": member_count,
        "uncompressed_member_bytes": total_bytes,
        "all_archive_files_present_with_exact_size": True,
    }


def code_sha() -> dict[str, str]:
    paths = [
        ROOT / "research_pipeline/relational_topology_real_protocol.py",
        ROOT / "research_pipeline/relational_topology_real_corpus.py",
        Path(__file__).resolve(),
    ]
    per_file = {str(path.relative_to(ROOT)): sha256_file(path) for path in paths}
    combined = hashlib.sha256(b"".join(path.read_bytes() for path in paths)).hexdigest()
    return {"combined_sha256": combined, **per_file}


def exclusion_digest(excluded: list[dict[str, Any]]) -> str:
    public = [{k: v for k, v in item.items() if k != "detail"} for item in excluded]
    return sha256_value(public)


def run_replay(args: argparse.Namespace, tokenizer: Any, object_types: tuple[str, ...], generator_sha: str, canonical: dict[str, Any]) -> dict[str, Any]:
    variants = {
        "forward_w1": ("forward", 1),
        "reverse_w1": ("reverse", 1),
        "shuffled_w1": ("shuffled", 1),
        "forward_w4": ("forward", 4),
    }
    observed: dict[str, Any] = {}
    for name, (traversal, workers) in variants.items():
        current = canonical if name == "forward_w1" else compile_pair(
            args.bedroom_root, args.split_csv, object_types, tokenizer, generator_sha,
            args.license_receipt, traversal=traversal, workers=workers,
        )
        observed[name] = {
            "corpus_jsonl_sha256": current["jsonl_sha256"],
            "eligible_scene_pool_sha256": sha256_value(current["eligible_scenes"]),
            "excluded_candidate_sha256": exclusion_digest(current["excluded"]),
            "eligible_scene_count": len(current["eligible_scenes"]),
            "excluded_scene_count": len(current["excluded"]),
        }
    corpus_hash_sets = {
        regime: {value["corpus_jsonl_sha256"][regime] for value in observed.values()}
        for regime in REAL_REGIME_SLOT_COUNTS
    }
    replay_pass = (
        all(len(values) == 1 for values in corpus_hash_sets.values())
        and len({value["eligible_scene_pool_sha256"] for value in observed.values()}) == 1
        and len({value["excluded_candidate_sha256"] for value in observed.values()}) == 1
    )
    return {"status": "PASS" if replay_pass else "FAIL", "byte_identical": replay_pass, "variants": observed}


def write_outputs(out: Path, canonical: dict[str, Any], payload: dict[str, Any]) -> None:
    partial = out.with_name(out.name + ".partial")
    if out.exists() or partial.exists():
        raise SystemExit(f"exactly-once output path already exists: {out} or {partial}")
    partial.mkdir(parents=True)
    (partial / "STATUS").write_text("RUNNING\n")
    for regime, rows in canonical["rows"].items():
        (partial / f"{regime}.jsonl").write_bytes(jsonl_bytes(rows))
    (partial / "eligible_scenes.txt").write_text("\n".join(canonical["eligible_scenes"]) + "\n")
    with (partial / "excluded_scenes.jsonl").open("wb") as handle:
        for item in canonical["excluded"]:
            handle.write(canonical_bytes(item))
    (partial / "qualification.json").write_bytes(canonical_bytes(payload))
    hashes = {}
    for path in sorted(partial.iterdir()):
        if path.name in {"STATUS", "ARTIFACT_SHA256SUMS"} or not path.is_file():
            continue
        hashes[path.name] = sha256_file(path)
    (partial / "ARTIFACT_SHA256SUMS").write_text("".join(f"{value}  {name}\n" for name, value in hashes.items()))
    (partial / "STATUS").write_text("PASS\n" if payload["verdict"].startswith("PASS_") else "FAIL\n")
    os.replace(partial, out)


def sanitize_for_git(payload: dict[str, Any]) -> dict[str, Any]:
    audit = payload["corpus_audit"]
    return {
        "object_id": payload["object_id"], "run_id": payload["run_id"],
        "verdict": payload["verdict"], "scientific_outcomes": 0,
        "dataset_revision": DATASET_REVISION, "source_seal": payload["source_seal"],
        "extraction_seal": payload["extraction_seal"], "generator": payload["generator"],
        "protocol": payload["protocol"], "corpus_audit": audit,
        "replay": payload["replay"], "content_addresses": payload["content_addresses"],
        "authority": payload["authority"],
        "licensed_row_content_committed_to_git": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--license-receipt", required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--bedroom-root", type=Path, required=True)
    parser.add_argument("--split-csv", type=Path, required=True)
    parser.add_argument("--instructscene-root", type=Path, required=True)
    parser.add_argument("--scenenat-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--git-artifact-dir", type=Path, required=True)
    args = parser.parse_args()
    require_license(args.license_receipt)

    source_seal = verify_sources(args.dataset_root, args.instructscene_root, args.scenenat_root)
    extraction_seal = seal_3dfront_extraction(args.dataset_root)
    code = code_sha(); generator_sha = code["combined_sha256"]
    object_types = load_object_types(args.bedroom_root / "dataset_stats.txt")

    from transformers import CLIPTokenizerFast
    tokenizer = CLIPTokenizerFast.from_pretrained(
        CLIP_MODEL, revision=CLIP_REVISION, local_files_only=True,
    )
    if tokenizer.model_max_length != 77:
        raise SystemExit(f"CLIP max length drift: {tokenizer.model_max_length}")

    canonical = compile_pair(
        args.bedroom_root, args.split_csv, object_types, tokenizer, generator_sha,
        args.license_receipt, traversal="forward", workers=1,
    )
    audit = audit_pair(canonical)
    replay = run_replay(args, tokenizer, object_types, generator_sha, canonical)
    gates = {
        "source_seal": True, "extraction_seal": True,
        "real_corpus_audit": audit["status"] == "PASS",
        "replay_byte_identical": replay["status"] == "PASS",
    }
    verdict = "PASS_REAL_MATCHED_CORPUS_QUALIFIED_GPU_QUALIFICATION_PROPOSABLE" if all(gates.values()) else "HOLD_REAL_MATCHED_CORPUS_QUALIFICATION"
    payload = {
        "object_id": OBJECT_ID, "run_id": RUN_ID, "verdict": verdict,
        "license_receipt_observed_exactly": args.license_receipt,
        "source_seal": source_seal, "extraction_seal": extraction_seal,
        "generator": code,
        "protocol": {
            "id": PROTOCOL_ID,
            "source_semantics": "SceneNAT-v2 refined text construction",
            "frozen_adapter_changes": [
                "relation count is externally fixed to the preregistered slot schedule",
                "RNG is content-derived per scene_id+sample_slot and never global sequential",
                "relation selection uses one per-slot permutation and count-specific prefixes for nested matching",
            ],
            "global_seed": REAL_GLOBAL_SEED,
            "slot_counts": {key: list(value) for key, value in REAL_REGIME_SLOT_COUNTS.items()},
            "shared_slots": list(SHARED_SLOTS),
            "clip_model": CLIP_MODEL, "clip_revision": CLIP_REVISION, "clip_max_tokens": 77,
        },
        "corpus_audit": audit, "replay": replay, "gates": gates,
        "content_addresses": {
            "corpus_jsonl_sha256": canonical["jsonl_sha256"],
            "eligible_scene_pool_sha256": sha256_value(canonical["eligible_scenes"]),
            "excluded_candidate_sha256": exclusion_digest(canonical["excluded"]),
        },
        "authority": {
            "data_license_confirmed": True, "data_materialization_authority": True,
            "gpu_training_qualification_authority": False, "gpu_authority": False,
            "official_training": False, "p1": False, "scientific_gpu_runs": 0,
            "scientific_outcomes": 0, "provider_calls": 0,
            "port_010": {"status": "HOLD_EVIDENCE_REVIEW_BLOCKED", "evidence_review": "BLOCK_BAKE_IN", "changed": False},
            "next_gate": "PROPOSE_GPU_TRAINING_QUALIFICATION_AUTHORITY" if verdict.startswith("PASS_") else "STOP_HOLD_REAL_CORPUS_QUALIFICATION",
        },
    }
    write_outputs(args.output_dir, canonical, payload)
    if args.git_artifact_dir.exists():
        raise SystemExit(f"git artifact dir already exists: {args.git_artifact_dir}")
    args.git_artifact_dir.mkdir(parents=True)
    sanitized = sanitize_for_git(payload)
    (args.git_artifact_dir / "adjudication.json").write_bytes(canonical_bytes(sanitized))
    (args.git_artifact_dir / "authority.json").write_bytes(canonical_bytes(payload["authority"]))
    (args.git_artifact_dir / "corpus_audit.json").write_bytes(canonical_bytes(audit))
    (args.git_artifact_dir / "replay.json").write_bytes(canonical_bytes(replay))
    artifact_hashes = {path.name: sha256_file(path) for path in sorted(args.git_artifact_dir.iterdir()) if path.is_file()}
    (args.git_artifact_dir / "ARTIFACT_SHA256SUMS").write_text("".join(f"{value}  {name}\n" for name, value in artifact_hashes.items()))
    print(json.dumps({"verdict": verdict, "rows": audit["rows"], "eligible_scenes": audit["eligible_scene_count"], "corpus_sha256": canonical["jsonl_sha256"], "replay": replay["status"]}, sort_keys=True))
    return 0 if verdict.startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
