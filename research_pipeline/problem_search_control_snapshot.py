from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .config import PROJECT_ROOT
from .paper_first_shadow_search_admission import primary_content_sha256
from .paper_first_problem_discovery_contract import DISCOVERY_OPERATOR_VERSION


QUALIFICATION_FILENAME = "shadow-run-qualification.json"
QUALIFICATION_SCHEMA_VERSION = "1.1"
STAGE_RUNNER_ARTIFACT_SCHEMA = "1.5"
CONTROL_FILES = (
    "research_pipeline/problem_search_control_snapshot.py",
    "research_pipeline/problem_search_shadow_launcher.py",
    "research_pipeline/paper_first_shadow_search_admission.py",
    "research_pipeline/problem_search_stage_runner.py",
    "research_pipeline/paper_first_problem_search_portfolio.py",
    "research_pipeline/paper_first_problem_discovery_contract.py",
    "research_pipeline/paper_first_problem_generator.py",
    "research_pipeline/paper_first_problem_generator_prompts.py",
    "research_pipeline/paper_first_fresh_saturation.py",
    "research_pipeline/paper_first_problem_falsifier_preflight.py",
    "research_pipeline/paper_first_evidence_acquisition.py",
    "research_pipeline/paper_first_legacy_reduction_migration.py",
    "research_pipeline/paper_first_shadow_current_source_gate.py",
    "research_pipeline/ark_provider.py",
    "research_pipeline/premium_model_policy.py",
)
AUTHORITY = {
    "canonical_generator": False,
    "canonical_queue": False,
    "paper_design": False,
    "method": False,
    "experiment": False,
    "p0": False,
    "gpu": False,
}
POLICY = {
    "frozen_pool_is_content_addressed": True,
    "shadow_memory_is_frozen_for_run": True,
    "control_snapshot_is_content_addressed": True,
    "control_snapshot_drift_stops_before_provider_call": True,
    "new_pool_reopens_old_semantic_search_closures": True,
    "canonical_primary_generator_queue_untouched": True,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _memory_payload(path: Path) -> dict[str, Any]:
    payload = _load(path)
    canonical = isinstance(payload.get("shadow_search_memory"), dict)
    memory = (payload.get("shadow_search_memory") or payload.get("shadow_dead_end_memory")) if isinstance(payload, dict) else None
    if not isinstance(memory, dict):
        memory = payload
    canonical = canonical or ("closed_objects" in memory and "blocked_objects" not in memory)
    if memory.get("scientific_authority") is not False or memory.get("live_source_coverage_effect") is not False or memory.get("cannot_mutate_canonical_generator_or_queue") is not True:
        raise ValueError("shadow memory must be zero-authority and unable to mutate canonical discovery")
    if canonical:
        rows = memory.get("closed_objects") or []
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError("canonical shadow_search_memory.closed_objects must be a list of objects")
        if any(row.get("search_closure_certified") is not True for row in rows):
            raise ValueError("canonical closed_objects rows must set search_closure_certified=true")
        if "blocked_objects" in memory:
            raise ValueError("canonical shadow_search_memory must not expose legacy blocked_objects")
    return memory


def memory_sha256(path: Path) -> str:
    memory = _memory_payload(path)
    canonical = json.dumps(memory, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return _sha_bytes(canonical)


def _git_head(project_root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=project_root, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def _control_files_clean(project_root: Path, control_files: Iterable[str]) -> bool:
    files = list(control_files)
    if not files:
        return True
    try:
        subprocess.check_call(["git", "diff", "--quiet", "--", *files], cwd=project_root)
        subprocess.check_call(["git", "diff", "--cached", "--quiet", "--", *files], cwd=project_root)
        tracked = set(subprocess.check_output(["git", "ls-files", "--", *files], cwd=project_root, text=True).splitlines())
    except (OSError, subprocess.CalledProcessError):
        return False
    return all(path in tracked for path in files)


def compute_control_snapshot(*, project_root: Path = PROJECT_ROOT, control_files: Iterable[str] = CONTROL_FILES) -> dict[str, Any]:
    rows = []
    for relative in control_files:
        path = project_root / relative
        if not path.is_file():
            raise ValueError(f"missing shadow control file: {relative}")
        rows.append({"path": relative, "sha256": _sha_file(path)})
    canonical = json.dumps({"stage_runner_artifact_schema": STAGE_RUNNER_ARTIFACT_SCHEMA, "files": rows}, sort_keys=True, separators=(",", ":")).encode()
    return {
        "stage_runner_artifact_schema": STAGE_RUNNER_ARTIFACT_SCHEMA,
        "control_snapshot_sha256": _sha_bytes(canonical),
        "control_files": rows,
    }


def _validate_pool(pool_path: Path) -> dict[str, Any]:
    pool = _load(pool_path)
    frozen_sha = str(pool.get("frozen_pool_sha256") or "").strip().lower()
    records = [row for row in pool.get("records") or [] if isinstance(row, dict)]
    if not re.fullmatch(r"[0-9a-f]{64}", frozen_sha) or not records:
        raise ValueError("frozen primary evidence pool must carry a 64-hex content digest and nonempty records")
    refs = [str(row.get("ref") or "") for row in records]
    if len(refs) != len(set(refs)) or any(not ref.startswith("arXiv:") for ref in refs):
        raise ValueError("frozen primary evidence pool refs must be unique arXiv refs")
    expected_set_sha = hashlib.sha256("\n".join(sorted(refs)).encode()).hexdigest()
    source_set_sha = str(pool.get("source_set_sha256") or "").strip().lower()
    source_content_sha = primary_content_sha256(records)
    source_pool_sha = str(pool.get("source_pool_sha256") or "").strip().lower()
    if source_set_sha != expected_set_sha:
        raise ValueError("frozen primary evidence source-set digest mismatch")
    if not re.fullmatch(r"[0-9a-f]{64}", source_content_sha):
        raise ValueError("frozen primary evidence primary-content digest invalid")
    if not re.fullmatch(r"[0-9a-f]{64}", source_pool_sha):
        raise ValueError("frozen primary evidence source-pool digest invalid")
    return pool


def _existing_stage_artifacts(run_root: Path) -> list[str]:
    names = []
    for pattern in ("expand-*.json", "error-expand-*.json", "evolve-*.json", "error-evolve-*.json", "formulate-p*.json", "error-formulate-*.json", "review-p*.json", "error-review-*.json", "machine-audit.json", "shadow-final-audit.json"):
        names.extend(path.name for path in run_root.glob(pattern))
    return sorted(set(names))


def build_shadow_run_qualification(*, run_root: Path, pool_path: Path, memory_path: Path, project_root: Path = PROJECT_ROOT, require_clean_control: bool = True, control_files: Iterable[str] = CONTROL_FILES) -> dict[str, Any]:
    if _existing_stage_artifacts(run_root):
        raise ValueError("shadow qualification must be frozen before any expansion/evolution/formulation/review artifact exists")
    if require_clean_control and not _control_files_clean(project_root, control_files):
        raise ValueError("shadow control files must be clean and tracked before qualification freeze")
    pool = _validate_pool(pool_path)
    memory = _memory_payload(memory_path)
    control = compute_control_snapshot(project_root=project_root, control_files=control_files)
    closed_rows = [row for row in memory.get("closed_objects") or [] if isinstance(row, dict) and row.get("search_closure_certified") is True]
    dead_end_rows = [row for row in closed_rows if row.get("dead_end_certified") is True]
    semantic_search_closures = sum(str(row.get("basin") or "").startswith(("semantic-exact-reduction-", "semantic-lane-contract-")) for row in closed_rows)
    semantic_dead_ends = sum(str(row.get("basin") or "").startswith(("semantic-exact-reduction-", "semantic-lane-contract-")) for row in dead_end_rows)
    pool_policy = pool.get("policy") or {}
    pool_source_kind = str(pool_policy.get("pool_source_kind") or ("canonical_private_pool" if pool_policy.get("canonical_private_pool_source") is True else ""))
    receipt = {
        "schema_version": QUALIFICATION_SCHEMA_VERSION,
        "generated_at": _now(),
        "status": "READY_FOR_SHADOW_EXPANSION",
        "run_id": run_root.name,
        "main_commit": _git_head(project_root),
        "discovery_operator_version": DISCOVERY_OPERATOR_VERSION,
        "source_generated_at": pool.get("source_generated_at") or pool.get("generated_at"),
        "source_pool_sha256": pool.get("source_pool_sha256"),
        "source_set_sha256": pool.get("source_set_sha256"),
        "source_primary_content_sha256": primary_content_sha256([row for row in pool.get("records") or [] if isinstance(row,dict)]),
        "frozen_pool_sha256": pool.get("frozen_pool_sha256"),
        "pool_source_kind": pool_source_kind,
        "records": len(pool.get("records") or []),
        "memory_sha256": memory_sha256(memory_path),
        "search_closure_objects": len(closed_rows),
        "dead_end_objects": len(dead_end_rows),
        "semantic_search_closures": semantic_search_closures,
        "semantic_dead_ends": semantic_dead_ends,
        "stage_runner_required_schema": STAGE_RUNNER_ARTIFACT_SCHEMA,
        "control_snapshot_sha256": control["control_snapshot_sha256"],
        "control_files": control["control_files"],
        "scientific_authority": False,
        "authority": dict(AUTHORITY),
        "policy": dict(POLICY),
    }
    return receipt


def write_shadow_run_qualification(*, run_root: Path, pool_path: Path, memory_path: Path, project_root: Path = PROJECT_ROOT, require_clean_control: bool = True, control_files: Iterable[str] = CONTROL_FILES) -> dict[str, Any]:
    run_root.mkdir(parents=True, exist_ok=True)
    target = run_root / QUALIFICATION_FILENAME
    if target.exists():
        existing = _load(target)
        current = build_shadow_run_qualification(run_root=run_root, pool_path=pool_path, memory_path=memory_path, project_root=project_root, require_clean_control=require_clean_control, control_files=control_files)
        immutable = ("run_id", "discovery_operator_version", "source_set_sha256", "source_primary_content_sha256", "frozen_pool_sha256", "pool_source_kind", "memory_sha256", "stage_runner_required_schema", "control_snapshot_sha256")
        if all(existing.get(key) == current.get(key) for key in immutable) and existing.get("status") == "READY_FOR_SHADOW_EXPANSION":
            return existing
        raise ValueError("existing shadow qualification receipt does not match the current frozen transaction")
    receipt = build_shadow_run_qualification(run_root=run_root, pool_path=pool_path, memory_path=memory_path, project_root=project_root, require_clean_control=require_clean_control, control_files=control_files)
    target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def validate_shadow_run_control(*, run_root: Path, pool_path: Path | None = None, memory_path: Path | None = None, project_root: Path = PROJECT_ROOT, require_receipt: bool | None = None, control_files: Iterable[str] = CONTROL_FILES) -> dict[str, Any]:
    if require_receipt is None:
        require_receipt = run_root.name.startswith("shadow-")
    receipt_path = run_root / QUALIFICATION_FILENAME
    if not receipt_path.exists():
        if require_receipt:
            raise ValueError("qualified shadow run receipt is required before stage execution")
        return {}
    receipt = _load(receipt_path)
    if receipt.get("status") != "READY_FOR_SHADOW_EXPANSION" or receipt.get("scientific_authority") is not False:
        raise ValueError("shadow run qualification receipt is not a zero-authority READY receipt")
    if str(receipt.get("stage_runner_required_schema") or "") != STAGE_RUNNER_ARTIFACT_SCHEMA:
        raise ValueError(f"shadow stage-runner schema drift: receipt={receipt.get('stage_runner_required_schema')} current={STAGE_RUNNER_ARTIFACT_SCHEMA}")
    current = compute_control_snapshot(project_root=project_root, control_files=control_files)
    if str(receipt.get("control_snapshot_sha256") or "") != current["control_snapshot_sha256"]:
        raise ValueError("shadow control snapshot drift detected before stage execution")
    if pool_path is not None:
        pool = _validate_pool(pool_path)
        pool_content_sha=primary_content_sha256([row for row in pool.get("records") or [] if isinstance(row,dict)])
        source_pairs=(("source_set_sha256",str(pool.get("source_set_sha256") or "")),("source_primary_content_sha256",pool_content_sha),("source_pool_sha256",str(pool.get("source_pool_sha256") or "")))
        for key,value in source_pairs:
            if str(receipt.get(key) or "")!=value:
                raise ValueError(f"shadow source identity drift detected:{key}")
        if str(receipt.get("frozen_pool_sha256") or "") != str(pool.get("frozen_pool_sha256") or ""):
            raise ValueError("shadow frozen-pool digest drift detected")
        pool_policy = pool.get("policy") or {}
        expected_source_kind = str(pool_policy.get("pool_source_kind") or ("canonical_private_pool" if pool_policy.get("canonical_private_pool_source") is True else ""))
        if receipt.get("pool_source_kind") is not None and str(receipt.get("pool_source_kind") or "") != expected_source_kind:
            raise ValueError("shadow frozen-pool provenance-kind drift detected")
    if memory_path is not None:
        if str(receipt.get("memory_sha256") or "") != memory_sha256(memory_path):
            raise ValueError("shadow dead-end memory digest drift detected")
    authority = receipt.get("authority") or {}
    if any(authority.get(key) is not False for key in AUTHORITY):
        raise ValueError("shadow run qualification cannot carry canonical or downstream authority")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    qualify = sub.add_parser("qualify")
    qualify.add_argument("--run-root", type=Path, required=True)
    qualify.add_argument("--pool", type=Path, required=True)
    qualify.add_argument("--memory", type=Path, required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--run-root", type=Path, required=True)
    validate.add_argument("--pool", type=Path)
    validate.add_argument("--memory", type=Path)
    args = parser.parse_args()
    if args.command == "qualify":
        state = write_shadow_run_qualification(run_root=args.run_root, pool_path=args.pool, memory_path=args.memory)
    else:
        state = validate_shadow_run_control(run_root=args.run_root, pool_path=args.pool, memory_path=args.memory)
    print(json.dumps({"run_id": state.get("run_id"), "status": state.get("status"), "stage_runner_required_schema": state.get("stage_runner_required_schema"), "control_snapshot_sha256": state.get("control_snapshot_sha256"), "scientific_authority": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
