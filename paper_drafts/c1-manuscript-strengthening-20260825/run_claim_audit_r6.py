#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REGISTRY = HERE / "claim-audit-r6-registry-20260828.json"
OUT = HERE / "claim-audit-r6-provenance-seal-20260828.json"
OUT_SHA = HERE / "claim-audit-r6-provenance-seal-20260828.json.sha256"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def resolve(rel: str) -> Path:
    path = HERE / rel
    if not path.is_file():
        raise RuntimeError(f"missing claim-audit input: {rel}")
    return path


def json_get(payload: Any, path: list[Any]) -> Any:
    cur = payload
    for key in path:
        if isinstance(key, int):
            if not isinstance(cur, list):
                raise TypeError(f"expected list before index {key}")
            cur = cur[key]
        else:
            if not isinstance(cur, dict):
                raise TypeError(f"expected object before key {key}")
            cur = cur[key]
    return cur


def evaluate(row: dict[str, Any]) -> dict[str, Any]:
    kind = row["kind"]
    sources = row.get("sources") or ([row["source"]] if row.get("source") else [])
    paths = [resolve(rel) for rel in sources]
    evidence = [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in paths]

    if kind == "text":
        joined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        required = row.get("required", [])
        forbidden = row.get("forbidden", [])
        required_ok = all(token in joined for token in required)
        forbidden_ok = all(token not in joined for token in forbidden)
        passed = required_ok and forbidden_ok
        detail = {
            "required": required,
            "required_present": {token: token in joined for token in required},
            "forbidden": forbidden,
            "forbidden_absent": {token: token not in joined for token in forbidden},
        }
    elif kind == "json_eq":
        if len(paths) != 1:
            raise RuntimeError(f"json_eq requires one source: {row['id']}")
        payload = json.loads(paths[0].read_text(encoding="utf-8"))
        actual = json_get(payload, row["json_path"])
        expected = row["expected"]
        passed = actual == expected
        detail = {"json_path": row["json_path"], "expected": expected, "actual": actual}
    else:
        raise RuntimeError(f"unsupported claim kind: {kind}")

    return {
        "id": row["id"],
        "description": row["description"],
        "pass": passed,
        "evidence": evidence,
        "detail": detail,
    }


def build_payload() -> dict[str, Any]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    claims = registry.get("claims") or []
    ids = [row.get("id") for row in claims]
    expected_ids = [f"C{i:02d}" for i in range(1, 36)]
    if ids != expected_ids:
        raise RuntimeError(f"claim registry must be exactly C01..C35 in order; got {ids}")

    results = [evaluate(row) for row in claims]
    used_paths: dict[str, str] = {}
    for result in results:
        for item in result["evidence"]:
            used_paths[item["path"]] = item["sha256"]

    payload = {
        "schema_version": "1.0",
        "artifact_type": "c1-r5-replayable-claim-audit",
        "paper_id": registry["paper_id"],
        "revision_id": registry["revision_id"],
        "status": "PASS" if all(row["pass"] for row in results) else "FAIL",
        "summary": {
            "claims_total": len(results),
            "claims_passed": sum(row["pass"] for row in results),
            "claims_failed": sum(not row["pass"] for row in results),
        },
        "claims": results,
        "provenance": {
            "registry": {
                "path": str(REGISTRY.relative_to(ROOT)),
                "sha256": sha(REGISTRY),
            },
            "runner": {
                "path": str(Path(__file__).resolve().relative_to(ROOT)),
                "sha256": sha(Path(__file__).resolve()),
            },
            "inputs": [{"path": path, "sha256": used_paths[path]} for path in sorted(used_paths)],
            "serialization": "UTF-8 JSON, sort_keys=True, indent=2, trailing newline; no wall-clock fields",
        },
        "execution": {
            "new_scientific_provider_calls": 0,
            "new_gpu_scientific_runs": 0,
            "new_scientific_experiments": 0,
            "network_required": False,
        },
        "authority": {
            "scientific": False,
            "experiment": False,
            "provider": False,
            "gpu": False,
            "claim_expansion": False,
            "submission": False,
        },
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay the C1 R6 35-claim manuscript audit")
    parser.add_argument("--check", action="store_true", help="verify the checked-in artifact and detached SHA without rewriting them")
    args = parser.parse_args()

    payload = build_payload()
    body = stable_json_bytes(payload)
    digest = hashlib.sha256(body).hexdigest()
    sha_line = f"{digest}  {OUT.name}\n".encode("utf-8")

    if args.check:
        if not OUT.is_file() or not OUT_SHA.is_file():
            raise RuntimeError("missing checked-in claim-audit artifact or detached SHA")
        if OUT.read_bytes() != body:
            raise RuntimeError("claim-audit artifact is not replay-byte-identical")
        if OUT_SHA.read_bytes() != sha_line:
            raise RuntimeError("claim-audit detached SHA is stale")
        if payload["status"] != "PASS":
            raise RuntimeError("replayed claim audit is FAIL")
        print(json.dumps({"status": "REPLAY_PASS", **payload["summary"], "sha256": digest}, sort_keys=True))
        return

    OUT.write_bytes(body)
    OUT_SHA.write_bytes(sha_line)
    print(json.dumps({"status": payload["status"], **payload["summary"], "sha256": digest}, sort_keys=True))
    if payload["status"] != "PASS":
        failed = [row["id"] for row in payload["claims"] if not row["pass"]]
        raise RuntimeError(f"R6 claim audit failed: {failed}")


if __name__ == "__main__":
    main()
