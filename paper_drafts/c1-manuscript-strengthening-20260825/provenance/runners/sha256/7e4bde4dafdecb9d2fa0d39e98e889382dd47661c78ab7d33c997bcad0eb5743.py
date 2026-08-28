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
CAS_ARTIFACT_ROOT = HERE / "provenance" / "sha256"
CAS_RUNNER_ROOT = HERE / "provenance" / "runners" / "sha256"
CAS_REGISTRY_ROOT = HERE / "provenance" / "registries" / "sha256"

SENSITIVITY = HERE / "stage-evidence-sensitivity-audit-20260826.json"
LADDER = HERE / "stage-evidence-ladder-analysis-20260825.json"
R2 = HERE / "stage-transport-bottleneck-analysis-20260825.json"
STAGE_REINTERPRETATION = HERE / "stage-resolved-evidence-reinterpretation.json"
LINEAGE_RUNNERS = (
    HERE / "analyze_stage_evidence_sensitivity.py",
    HERE / "analyze_stage_evidence_ladder.py",
    HERE / "analyze_stage_transport_bottleneck.py",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def resolve(rel: str) -> Path:
    path = HERE / rel
    if not path.is_file():
        raise RuntimeError(f"missing claim-audit input: {rel}")
    return path


def resolve_root(rel: str) -> Path:
    path = ROOT / rel
    if not path.is_file():
        raise RuntimeError(f"missing lineage input: {rel}")
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


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def normalize_bindings(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list) and all(isinstance(row, dict) for row in value):
        return value
    raise RuntimeError("lineage binding must be an object or list of objects")


def verify_declared_bindings(owner: Path, field: str) -> list[dict[str, str]]:
    payload = load_object(owner)
    rows = normalize_bindings(payload.get(field))
    verified: list[dict[str, str]] = []
    for row in rows:
        rel = str(row.get("path") or "")
        expected = str(row.get("sha256") or "")
        if not rel or len(expected) != 64:
            raise RuntimeError(f"malformed lineage binding in {owner.name}: {row}")
        target = resolve_root(rel)
        actual = sha(target)
        if actual != expected:
            raise RuntimeError(f"lineage SHA drift: {rel}: expected {expected}, got {actual}")
        verified.append(
            {
                "owner": str(owner.relative_to(ROOT)),
                "field": field,
                "path": rel,
                "sha256": actual,
            }
        )
    return verified


def verify_lineage() -> dict[str, Any]:
    expected_chain = {
        str(LADDER.relative_to(ROOT)),
        str(R2.relative_to(ROOT)),
        str(STAGE_REINTERPRETATION.relative_to(ROOT)),
        "research_pipeline/result_analysis_ledger_20260825.json",
        "paper_drafts/c1-proxy-reward-stanford-r3-20260824/cbrg-d0b1c-operational-contrast-evidence-locator-20260824.json",
        "paper_drafts/c1-proxy-reward-stanford-r3-20260824/cbrg-d0b2-adjudicator-inventory-closure-20260825.json",
    }
    verified: list[dict[str, str]] = []
    verified.extend(verify_declared_bindings(SENSITIVITY, "source_binding"))
    verified.extend(verify_declared_bindings(LADDER, "source_binding"))
    verified.extend(verify_declared_bindings(R2, "source_bindings"))
    verified.extend(verify_declared_bindings(STAGE_REINTERPRETATION, "source_bindings"))
    verified_paths = {row["path"] for row in verified}
    missing = sorted(expected_chain - verified_paths)
    if missing:
        raise RuntimeError(f"lineage chain incomplete; missing bound paths: {missing}")

    runner_rows = []
    for path in LINEAGE_RUNNERS:
        if not path.is_file():
            raise RuntimeError(f"missing lineage runner: {path.name}")
        runner_rows.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path)})

    statuses = {
        "stage_reinterpretation": load_object(STAGE_REINTERPRETATION).get("status"),
        "transport_analysis": load_object(R2).get("status"),
        "stage_ladder": load_object(LADDER).get("status"),
        "sensitivity_audit": load_object(SENSITIVITY).get("status"),
    }
    if statuses != {
        "stage_reinterpretation": "NEW_INTERPRETATION_OF_FROZEN_EVIDENCE_REQUIRES_PAPER_CONTRACT_REOPEN",
        "transport_analysis": "SUPPORTED_OPERATIONAL_POST_EXPOSURE_ATTENUATION_LOCALIZATION",
        "stage_ladder": "SUPPORTED_ORDINAL_POST_EXPOSURE_PRE_UPTAKE_LOCALIZATION",
        "sensitivity_audit": "EVIDENCE_LOCALIZATION_SUPPORTED_LATENT_BOTTLENECK_NOT_IDENTIFIED",
    }:
        raise RuntimeError(f"unexpected evidence-lineage status drift: {statuses}")

    return {
        "verified_bindings": sorted(verified, key=lambda row: (row["owner"], row["path"])),
        "lineage_runners": sorted(runner_rows, key=lambda row: row["path"]),
        "statuses": statuses,
        "interpretation": "The claim audit binds the manuscript to a SHA-verified frozen-evidence chain; it does not upgrade operational localization to causal mediation or add scientific authority.",
    }


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
        "schema_version": "1.1",
        "artifact_type": "c1-r6-replayable-claim-audit",
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
            "lineage": verify_lineage(),
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


def cas_locations(audit_digest: str, runner_digest: str, registry_digest: str) -> dict[str, Path]:
    return {
        "artifact": CAS_ARTIFACT_ROOT / f"{audit_digest}.json",
        "runner": CAS_RUNNER_ROOT / f"{runner_digest}.py",
        "registry": CAS_REGISTRY_ROOT / f"{registry_digest}.json",
    }


def seal_or_check_cas(*, body: bytes, digest: str, check: bool) -> dict[str, str]:
    runner_path = Path(__file__).resolve()
    runner_digest = sha(runner_path)
    registry_digest = sha(REGISTRY)
    locations = cas_locations(digest, runner_digest, registry_digest)
    expected_bytes = {
        "artifact": body,
        "runner": runner_path.read_bytes(),
        "registry": REGISTRY.read_bytes(),
    }
    if check:
        for key, path in locations.items():
            if not path.is_file():
                raise RuntimeError(f"missing content-addressed {key}: {path.relative_to(ROOT)}")
            if path.read_bytes() != expected_bytes[key]:
                raise RuntimeError(f"content-addressed {key} bytes drift: {path.relative_to(ROOT)}")
    else:
        for path in locations.values():
            path.parent.mkdir(parents=True, exist_ok=True)
        for key, path in locations.items():
            path.write_bytes(expected_bytes[key])
    return {key: str(path.relative_to(ROOT)) for key, path in locations.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay the C1 R6 35-claim manuscript audit")
    parser.add_argument("--check", action="store_true", help="verify checked-in alias, detached SHA, content-addressed artifact/runner/registry, and evidence lineage without rewriting")
    args = parser.parse_args()

    payload = build_payload()
    body = stable_json_bytes(payload)
    digest = hashlib.sha256(body).hexdigest()
    sha_line = f"{digest}  {OUT.name}\n".encode("utf-8")
    cas = seal_or_check_cas(body=body, digest=digest, check=args.check)

    if args.check:
        if not OUT.is_file() or not OUT_SHA.is_file():
            raise RuntimeError("missing checked-in claim-audit alias or detached SHA")
        if OUT.read_bytes() != body:
            raise RuntimeError("claim-audit alias is not replay-byte-identical")
        if OUT_SHA.read_bytes() != sha_line:
            raise RuntimeError("claim-audit detached SHA is stale")
        if payload["status"] != "PASS":
            raise RuntimeError("replayed claim audit is FAIL")
        print(json.dumps({"status": "REPLAY_PASS", **payload["summary"], "sha256": digest, "cas": cas}, sort_keys=True))
        return

    OUT.write_bytes(body)
    OUT_SHA.write_bytes(sha_line)
    print(json.dumps({"status": payload["status"], **payload["summary"], "sha256": digest, "cas": cas}, sort_keys=True))
    if payload["status"] != "PASS":
        failed = [row["id"] for row in payload["claims"] if not row["pass"]]
        raise RuntimeError(f"R6 claim audit failed: {failed}")


if __name__ == "__main__":
    main()
