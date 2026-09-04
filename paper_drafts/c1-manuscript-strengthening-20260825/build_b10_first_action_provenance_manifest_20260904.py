#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

LEGACY_COMMIT = "f400a9e218c869a447110f3e3e00de6449550985"
LEGACY_RUNNER_PATH = "paper_drafts/c1-proxy-reward-stanford-r3-20260824/run_b10_native_first_action_transport.py"
EXPECTED_LEGACY_RUNNER_SHA256 = "87214f92c2a11ea9ff139535ca6d7d272680ec5ed7da8b86880475bbb66cb98a"
EXPECTED_CONTRACT_SHA256 = "c2a54c928d74ccb7a153166a02ef0ef7a1504a93b5895952380a95b0277a3436"
EXPECTED_RESULT_SHA256 = "e779c19a6a73bdb4b551f0739453a014fe9fc3cafc17cb4fbaa8b70a5137d8e6"
EXPECTED_REPLAY_RECEIPT_SHA256 = "2bac711b6ebec8b77568bdca3cd0ea47d62d2dde52add8e34f44493703ff88d7"
EXPECTED_RECORDS = 432


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def stable_digest(value: Any) -> str:
    body = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha_bytes(body)


def git_blob(repo_root: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo_root), "show", f"{commit}:{path}"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a content-addressed provenance manifest for the historical C1 B10 first-action run.")
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--replay-receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    run_root = args.run_root.resolve()
    replay_path = args.replay_receipt.resolve()
    contract_path = run_root / "b10-contract.json"
    result_path = run_root / "b10-result.json"
    stages_root = run_root / "private" / "stages"
    raw_root = run_root / "private" / "raw"
    provider_root = run_root / "private" / "provider-responses"

    require(contract_path.is_file() and sha(contract_path) == EXPECTED_CONTRACT_SHA256, "B10 contract SHA drift")
    require(result_path.is_file() and sha(result_path) == EXPECTED_RESULT_SHA256, "B10 result SHA drift")
    require(replay_path.is_file() and sha(replay_path) == EXPECTED_REPLAY_RECEIPT_SHA256, "replay receipt SHA drift")
    replay = load(replay_path)
    require(replay.get("status") == "PASS_B10_FIRST_ACTION_RAW_REPLAY", "raw replay did not pass")

    legacy_runner = git_blob(repo_root, LEGACY_COMMIT, LEGACY_RUNNER_PATH)
    require(sha_bytes(legacy_runner) == EXPECTED_LEGACY_RUNNER_SHA256, "historical normalizer/runner SHA drift")

    stage_paths = sorted(stages_root.glob("*.json"), key=lambda p: p.name)
    provider_paths = sorted(provider_root.glob("*.json"), key=lambda p: p.name)
    raw_paths = sorted(raw_root.glob("*/*.txt"), key=lambda p: str(p.relative_to(run_root)))
    require(len(stage_paths) == EXPECTED_RECORDS, f"stage record count drift: {len(stage_paths)}")
    require(len(provider_paths) == EXPECTED_RECORDS, f"provider record count drift: {len(provider_paths)}")
    require(len(raw_paths) == EXPECTED_RECORDS, f"raw record count drift: {len(raw_paths)}")

    provider_by_name = {p.name: p for p in provider_paths}
    records: list[dict[str, Any]] = []
    seen_raw: set[str] = set()
    seen_stage_ids: set[str] = set()

    for stage_path in stage_paths:
        stage = load(stage_path)
        require(stage.get("status") == "complete", f"non-complete stage: {stage_path.name}")
        stage_id = str(stage.get("stage") or "")
        require(stage_id and stage_id not in seen_stage_ids, f"duplicate/missing stage id: {stage_path.name}")
        seen_stage_ids.add(stage_id)
        raw_hash = str(stage.get("raw_sha256") or "")
        require(len(raw_hash) == 64, f"missing raw SHA: {stage_id}")
        raw_path = raw_root / raw_hash[:2] / f"{raw_hash}.txt"
        require(raw_path.is_file() and sha(raw_path) == raw_hash, f"raw object drift: {stage_id}")
        seen_raw.add(raw_hash)
        provider_path = provider_by_name.get(stage_path.name)
        require(provider_path is not None and provider_path.is_file(), f"provider receipt missing: {stage_id}")
        provider = load(provider_path)
        require(str(provider.get("stage") or "") == stage_id, f"provider/stage identity mismatch: {stage_id}")
        require(str(provider.get("text_sha256") or "") == raw_hash, f"provider text SHA mismatch: {stage_id}")

        records.append(
            {
                "stage": stage_id,
                "future_task": int(stage["future_task"]),
                "selected_source_task": int(stage["selected_source_task"]),
                "condition": str(stage["condition"]),
                "rollout": int(stage["rollout"]),
                "action_signature": str(stage["action_signature"]),
                "parse_recovered": bool(stage.get("parse_recovered")),
                "stage_record": {
                    "path": str(stage_path.relative_to(run_root)),
                    "sha256": sha(stage_path),
                },
                "raw_text": {
                    "path": str(raw_path.relative_to(run_root)),
                    "sha256": raw_hash,
                },
                "provider_response": {
                    "path": str(provider_path.relative_to(run_root)),
                    "sha256": sha(provider_path),
                },
            }
        )

    require(len(records) == EXPECTED_RECORDS, "record manifest geometry drift")
    require(len(seen_raw) == EXPECTED_RECORDS, "raw response hashes are not one-to-one with historical provider records")

    stage_entries = [record["stage_record"] for record in records]
    raw_entries = [record["raw_text"] for record in records]
    provider_entries = [record["provider_response"] for record in records]
    category_roots = {
        "stage_records_sha256": stable_digest(stage_entries),
        "raw_texts_sha256": stable_digest(raw_entries),
        "provider_responses_sha256": stable_digest(provider_entries),
        "normalized_record_index_sha256": stable_digest(
            [
                {
                    "stage": record["stage"],
                    "future_task": record["future_task"],
                    "selected_source_task": record["selected_source_task"],
                    "condition": record["condition"],
                    "rollout": record["rollout"],
                    "action_signature": record["action_signature"],
                    "parse_recovered": record["parse_recovered"],
                }
                for record in records
            ]
        ),
    }
    category_roots["combined_private_evidence_sha256"] = stable_digest(category_roots)

    payload = {
        "schema_version": "1.0",
        "artifact_type": "c1-b10-first-action-private-provenance-manifest",
        "date": "2026-09-04",
        "status": "PASS_CONTENT_ADDRESSED_PRIVATE_FIRST_ACTION_PROVENANCE",
        "run_root": str(run_root),
        "source_bindings": {
            "b10_contract": {"path": str(contract_path), "sha256": EXPECTED_CONTRACT_SHA256},
            "b10_result": {"path": str(result_path), "sha256": EXPECTED_RESULT_SHA256},
            "raw_replay_receipt": {"path": str(replay_path), "sha256": EXPECTED_REPLAY_RECEIPT_SHA256},
            "historical_normalizer_runner": {
                "commit": LEGACY_COMMIT,
                "path": LEGACY_RUNNER_PATH,
                "sha256": EXPECTED_LEGACY_RUNNER_SHA256,
                "normalizer_semantics": "first structured action name; click_element additionally includes the interactive-element index",
            },
        },
        "geometry": {
            "scientific_units": 36,
            "conditions": ["success_memory", "failure_memory", "no_memory"],
            "draws_per_state_per_condition": 4,
            "provider_records": EXPECTED_RECORDS,
            "stage_records": len(stage_paths),
            "raw_text_objects": len(raw_paths),
            "provider_response_receipts": len(provider_paths),
        },
        "category_roots": category_roots,
        "records": records,
        "privacy_boundary": "This manifest publishes only content hashes, relative private-run paths, normalized action signatures, and non-secret execution metadata. It does not copy raw provider text or credentials into the repository.",
        "execution": {"new_provider_calls": 0, "new_gpu_runs": 0},
        "authority": {"claim_expansion": False, "submission": False},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "geometry": payload["geometry"],
                "category_roots": category_roots,
                "new_provider_calls": 0,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
