from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .b1_memrl_alfworld_fresh_preflight import render_memory_patch

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
PREFLIGHT_STATUS = "FRESH_SUBSTRATE_G1_G8_PREFLIGHT_PASS"
SOURCE_STATUS = "SOURCE_PROVENANCE_SUPPORT_PASS"
ARMS = (
    "A0_NO_MEMORY",
    "A1_CONTENT_ONLY",
    "A2_TRUTHFUL_VISIBLE_PROVENANCE",
    "A5_FLIPPED_VISIBLE_PROVENANCE",
    "A7_BACKEND_ONLY_LABEL",
)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def content_hash(payload: dict[str, Any], *, exclude: set[str] | None = None) -> str:
    excluded = exclude or set()
    body = {k: v for k, v in payload.items() if k not in excluded}
    return sha_text(json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def valid_source_rows(output_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((output_dir / "source").glob("*.json")):
        row = load(path)
        if row.get("execution_valid") is True:
            rows.append(row)
    return sorted(rows, key=lambda row: int(row.get("source_index") or 0))


def compile_target_execution_plan(
    *, preflight_path: Path, source_support_path: Path, output_dir: Path, generated_at: str | None = None
) -> dict[str, Any]:
    """Freeze source-memory assignment before any target rollout.

    The source support gate may decide when source acquisition stops. Within the acquired
    execution-valid support set, assignment is deterministic and does not read source
    provenance/reward, target outcomes, pilot outcomes, or behavioral effects.
    """
    preflight = load(preflight_path)
    support = load(source_support_path)
    if preflight.get("paper_id") != PAPER_ID or preflight.get("status") != PREFLIGHT_STATUS:
        raise RuntimeError("fresh preflight is not the frozen B1 PASS contract")
    if support.get("status") != SOURCE_STATUS or support.get("pilot_execution_authorized") is not True:
        raise RuntimeError("source provenance support has not passed")
    if support.get("preflight_manifest_sha256") != preflight.get("manifest_sha256"):
        raise RuntimeError("source-support/preflight manifest drift")
    if any((preflight.get("authority") or {}).get(key) is not False for key in ("scientific", "paper", "experiment", "provider", "gpu", "submission")):
        raise RuntimeError("preflight authority boundary drift")

    sources = valid_source_rows(output_dir)
    if len(sources) < 4:
        raise RuntimeError("source support receipt exists without enough execution-valid sources")
    if {str(row.get("true_provenance") or "") for row in sources} != {"success", "failure"}:
        raise RuntimeError("source support lacks both provenance strata")
    for row in sources:
        if row.get("preflight_manifest_sha256") != preflight.get("manifest_sha256"):
            raise RuntimeError(f"source row manifest drift:{row.get('source_index')}")
        body = str(row.get("memory_body") or "")
        if not body or sha_text(body) != row.get("memory_body_sha256"):
            raise RuntimeError(f"source memory-body hash drift:{row.get('source_index')}")

    partition = preflight.get("task_partition") or {}
    phase_targets = {
        "pilot": list(partition.get("pilot_targets") or []),
        "confirmatory": list(partition.get("confirmatory_targets") or []),
    }
    stats = preflight.get("statistics") or {}
    if len(phase_targets["pilot"]) != int(stats.get("pilot_n") or 0):
        raise RuntimeError("pilot target membership drift")
    if len(phase_targets["confirmatory"]) != int(stats.get("confirmatory_n") or 0):
        raise RuntimeError("confirmatory target membership drift")

    assignments: dict[str, list[dict[str, Any]]] = {"pilot": [], "confirmatory": []}
    offset = 0
    for phase in ("pilot", "confirmatory"):
        for local_index, target in enumerate(phase_targets[phase]):
            global_index = offset + local_index
            source = sources[global_index % len(sources)]
            body = str(source["memory_body"])
            provenance = str(source["true_provenance"])
            patch_hashes = {arm: sha_text(render_memory_patch(body, arm, provenance)) for arm in ARMS}
            if patch_hashes["A1_CONTENT_ONLY"] != patch_hashes["A7_BACKEND_ONLY_LABEL"]:
                raise RuntimeError("A1/A7 executor patch bytes are not identical")
            assignments[phase].append({
                "target_index": local_index,
                "global_target_index": global_index,
                "family": target.get("family"),
                "relative_gamefile": target.get("relative_gamefile"),
                "expected_gamefile_sha256": target.get("gamefile_sha256"),
                "source_index": int(source["source_index"]),
                "source_family": source.get("family"),
                "source_memory_body_sha256": source.get("memory_body_sha256"),
                "true_provenance": provenance,
                "arm_patch_sha256": patch_hashes,
            })
        offset += len(phase_targets[phase])

    plan: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "status": "TARGET_EXECUTION_PLAN_FROZEN",
        "generated_at": generated_at or now(),
        "preflight_manifest_sha256": preflight.get("manifest_sha256"),
        "source_support_receipt_sha256": support.get("receipt_sha256"),
        "source_support_summary": support.get("summary") or {},
        "pairing_rule": "sort acquired execution-valid source rows by frozen source_index; concatenate frozen pilot then confirmatory targets; assign global target i to sources[i mod source_count]",
        "pairing_uses_source_provenance": False,
        "pairing_uses_source_reward": False,
        "pairing_uses_target_outcome": False,
        "pairing_uses_pilot_outcome": False,
        "source_indices_available": [int(row["source_index"]) for row in sources],
        "arm_order": list(ARMS),
        "assignments": assignments,
        "target_outcomes_opened": False,
        "authority": {"scientific": False, "paper": False, "experiment": False, "provider": False, "gpu": False, "submission": False},
    }
    plan["plan_sha256"] = content_hash(plan, exclude={"generated_at", "plan_sha256"})
    return plan


def write_target_execution_plan(*, preflight_path: Path, source_support_path: Path, output_dir: Path, plan_path: Path) -> dict[str, Any]:
    plan = compile_target_execution_plan(preflight_path=preflight_path, source_support_path=source_support_path, output_dir=output_dir)
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return plan
