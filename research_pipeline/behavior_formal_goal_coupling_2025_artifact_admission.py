from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "behavior-formal-goal-coupling-2025-artifact-admission-v1"
TASK_KEYS = ("task", "task_name", "task_id")
INSTANCE_KEYS = ("instance", "instance_idx", "instance_id", "instance_index")
COUNT_KEYS = ("count", "n", "num_rollouts", "num_episodes", "rollout_count", "episode_count", "denominator")
EXPECTED_INSTANCE_IDS = set(range(10))


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _task_value(node: dict[str, Any], task_ids: set[str]) -> str | None:
    for key in TASK_KEYS:
        value = node.get(key)
        if isinstance(value, str) and value in task_ids:
            return value
    return None


def _instance_value(node: dict[str, Any]) -> int | None:
    for key in INSTANCE_KEYS:
        value = node.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int) and value in EXPECTED_INSTANCE_IDS:
            return value
        if isinstance(value, str) and value.isdigit() and int(value) in EXPECTED_INSTANCE_IDS:
            return int(value)
    return None


def _official_q(node: Any) -> float | None:
    if not isinstance(node, dict):
        return None
    q = node.get("q_score")
    if not isinstance(q, dict):
        return None
    final = q.get("final")
    if isinstance(final, bool) or not isinstance(final, (int, float)):
        return None
    value = float(final)
    if not (0.0 <= value <= 1.0):
        return None
    return value


def _explicit_count(node: dict[str, Any]) -> int | None:
    for key in COUNT_KEYS:
        value = node.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def _schema_paths(node: Any, path: tuple[str, ...] = ()) -> set[str]:
    """Return redacted type/schema paths only; never values."""
    out: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            k = str(key)
            out.add("/".join((*path, k, f"<{type(value).__name__}>")))
            out |= _schema_paths(value, (*path, k))
    elif isinstance(node, list):
        out.add("/".join((*path, "[]", f"<len:{len(node)}>")))
        # schema path inspection is bounded to the first item because admission
        # itself separately checks every candidate record for coverage.
        if node:
            out |= _schema_paths(node[0], (*path, "[]"))
    return out


def _walk_dicts(node: Any):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk_dicts(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_dicts(value)


def _raw_rollout_map(payload: Any, task_ids: set[str]) -> dict[tuple[str, int], float] | None:
    records: dict[tuple[str, int], float] = {}
    duplicate = False
    for node in _walk_dicts(payload):
        task = _task_value(node, task_ids)
        instance = _instance_value(node)
        q = _official_q(node)
        if task is None or instance is None or q is None:
            continue
        key = (task, instance)
        if key in records:
            duplicate = True
            break
        records[key] = q
    if duplicate:
        return None
    expected = {(task, instance) for task in task_ids for instance in EXPECTED_INSTANCE_IDS}
    return records if set(records) == expected else None


def _task_key_rollout_map(payload: Any, task_ids: set[str]) -> dict[tuple[str, int], float] | None:
    """Accept exact task-id keyed 10-item lists/dicts with q_score.final."""
    if not isinstance(payload, dict):
        return None
    records: dict[tuple[str, int], float] = {}
    seen_tasks: set[str] = set()
    # Search any dict layer whose keys include exact task IDs.
    for node in _walk_dicts(payload):
        present = task_ids.intersection(map(str, node.keys()))
        if not present:
            continue
        for task in present:
            value = node.get(task)
            if isinstance(value, list) and len(value) == 10:
                items = list(enumerate(value))
            elif isinstance(value, dict) and set(map(str, value.keys())) == {str(i) for i in range(10)}:
                items = [(i, value.get(str(i), value.get(i))) for i in range(10)]
            else:
                continue
            local: dict[tuple[str, int], float] = {}
            for instance, rec in items:
                q = _official_q(rec)
                if q is None:
                    local = {}
                    break
                local[(task, instance)] = q
            if local:
                if task in seen_tasks:
                    return None
                seen_tasks.add(task)
                records.update(local)
    expected = {(task, instance) for task in task_ids for instance in EXPECTED_INSTANCE_IDS}
    return records if set(records) == expected else None


def _aggregate_map(payload: Any, task_ids: set[str]) -> dict[str, float] | None:
    """Accept exact task aggregates only with explicit denominator/count=10."""
    records: dict[str, float] = {}
    # Explicit task-id fields.
    for node in _walk_dicts(payload):
        task = _task_value(node, task_ids)
        q = _official_q(node)
        count = _explicit_count(node)
        if task is None or q is None or count != 10:
            continue
        if task in records:
            return None
        records[task] = q
    if set(records) == task_ids:
        return records

    # Exact task-id keyed aggregate dicts.
    records = {}
    for node in _walk_dicts(payload):
        present = task_ids.intersection(map(str, node.keys()))
        if not present:
            continue
        for task in present:
            value = node.get(task)
            if not isinstance(value, dict):
                continue
            q = _official_q(value)
            count = _explicit_count(value)
            if q is None or count != 10:
                continue
            if task in records:
                return None
            records[task] = q
    return records if set(records) == task_ids else None


@dataclass(frozen=True)
class AdmissionResult:
    status: str
    format: str
    task_count: int
    rollout_count: int
    reasons: tuple[str, ...]
    schema_paths: tuple[str, ...]
    # q values remain process-local and are intentionally absent from result.


def inspect_candidate(payload: Any, task_ids: list[str]) -> AdmissionResult:
    task_set = set(task_ids)
    if len(task_set) != 50:
        raise ValueError("frozen 2025 task list must contain exactly 50 unique IDs")
    schema = tuple(sorted(_schema_paths(payload)))
    raw = _raw_rollout_map(payload, task_set)
    if raw is None:
        raw = _task_key_rollout_map(payload, task_set)
    if raw is not None:
        return AdmissionResult("ELIGIBLE_FULL_STANDARD_PUBLIC", "FULL_TASK_INSTANCE_ROLLOUT", 50, 500, (), schema)
    aggregate = _aggregate_map(payload, task_set)
    if aggregate is not None:
        return AdmissionResult("ELIGIBLE_FULL_STANDARD_PUBLIC", "FULL_TASK_AGGREGATE_DENOM10", 50, 500, (), schema)

    mentioned: set[str] = set()
    for node in _walk_dicts(payload):
        mentioned.update(task_set.intersection(map(str, node.keys())))
        task = _task_value(node, task_set)
        if task:
            mentioned.add(task)
    reasons = (
        "candidate does not match either frozen full-coverage schema",
        f"recoverable_task_ids={len(mentioned)}/50",
        "manual schema rescue is forbidden",
    )
    return AdmissionResult("INELIGIBLE_SCHEMA_OR_COVERAGE", "NONE", len(mentioned), 0, reasons, schema)


def git_blob(repo: Path, revision: str, path: str) -> bytes:
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{revision}:{path}"], capture_output=True, check=True)
    return proc.stdout


def git_blob_sha(repo: Path, revision: str, path: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), "rev-parse", f"{revision}:{path}"], text=True, capture_output=True, check=True)
    return proc.stdout.strip()


def run_admission(*, repo: Path, prereg: Path, amendment: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise ValueError("admission receipt already exists; one-shot contract forbids overwrite")
    base = json.loads(prereg.read_text(encoding="utf-8"))
    amend = json.loads(amendment.read_text(encoding="utf-8"))
    if base.get("preregistration_sha256") != amend.get("base_preregistration_sha256"):
        raise ValueError("preregistration/amendment digest mismatch")
    if amend.get("one_shot_schema_coverage_admission_authorized") is not True:
        raise ValueError("one-shot admission is not authorized by frozen amendment")
    revision = str(base["candidate_artifact_snapshot"]["repo_revision"])
    task_ids = list(base["artifact_admission"]["exact_task_ids"])
    candidates = list(base["candidate_artifact_snapshot"]["candidates"])
    rows: list[dict[str, Any]] = []
    eligible_paths: list[str] = []
    for candidate in candidates:
        path = str(candidate["path"])
        actual_blob = git_blob_sha(repo, revision, path)
        if actual_blob != candidate["blob_sha"]:
            raise ValueError(f"candidate blob drift:{path}:{actual_blob}!={candidate['blob_sha']}")
        raw = git_blob(repo, revision, path)
        if len(raw) != int(candidate["bytes"]):
            raise ValueError(f"candidate byte-size drift:{path}")
        payload = json.loads(raw)
        result = inspect_candidate(payload, task_ids)
        row = {
            "path": path,
            "blob_sha": actual_blob,
            "bytes": len(raw),
            "json_sha256": hashlib.sha256(raw).hexdigest(),
            "status": result.status,
            "format": result.format,
            "recoverable_task_count": result.task_count,
            "recoverable_rollout_count": result.rollout_count,
            "reasons": list(result.reasons),
            "schema_paths": list(result.schema_paths),
            "outcome_values_logged": False,
        }
        rows.append(row)
        if result.status == "ELIGIBLE_FULL_STANDARD_PUBLIC":
            eligible_paths.append(path)
    minimum = int(base["artifact_admission"]["minimum_independent_full_submissions"])
    admitted = len(eligible_paths) >= minimum
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "object_id": base["object_id"],
        "status": "ARTIFACT_ADMISSION_PASS_AWAITING_EXTRACTION_FREEZE" if admitted else "ARTIFACT_ADMISSION_HOLD_INSUFFICIENT_FULL_PUBLIC_OUTCOMES",
        "scientific_authority": False,
        "scientific_statistics_executed": False,
        "policy_outcome_values_accessed_for_schema_coverage_admission": True,
        "outcome_values_logged": False,
        "base_preregistration_sha256": base["preregistration_sha256"],
        "amendment_sha256": amend["amendment_sha256"],
        "repo_revision": revision,
        "candidate_count": len(candidates),
        "eligible_count": len(eligible_paths),
        "minimum_eligible_required": minimum,
        "eligible_paths": eligible_paths,
        "candidates": rows,
        "manual_schema_rescue_authorized": False,
        "policy_self_run_authorized": False,
        "analysis_authorized": False,
        "next_gate": "freeze exact admitted extraction set/schema before scientific statistics" if admitted else "HOLD; do not analyze partial artifacts and do not self-run policies",
    }
    receipt["receipt_sha256"] = canonical_sha({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="One-shot redacted admission of BEHAVIOR 2025 public standard outcome artifacts")
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--prereg", type=Path, required=True)
    parser.add_argument("--amendment", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = run_admission(repo=args.repo, prereg=args.prereg, amendment=args.amendment, output=args.output)
    print(json.dumps({
        "status": receipt["status"],
        "receipt_sha256": receipt["receipt_sha256"],
        "candidate_count": receipt["candidate_count"],
        "eligible_count": receipt["eligible_count"],
        "scientific_statistics_executed": False,
        "outcome_values_logged": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
