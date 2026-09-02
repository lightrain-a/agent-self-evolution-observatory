#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import run_e2_r17_actor_pool_repair2_continuation_v2 as base

AUTH_STATUS = "AUTHORIZED_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO_MEASUREMENT"


def validate_authority(
    *,
    mode: str,
    authorization: Path | None,
    task_ids: list[str],
    split: dict[str, Any],
    k: int,
) -> tuple[dict[str, Any] | None, str | None]:
    if authorization is None:
        raise RuntimeError("constrained-state actor requires --authorization")
    payload = base.json.loads(authorization.read_text(encoding="utf-8"))
    contract_path = Path(str(payload.get("contract_path") or ""))
    if not contract_path.is_file() or base.sha256(contract_path) != payload.get("contract_sha256"):
        raise RuntimeError("constrained-state authorization/contract binding drift")
    if payload.get("status") != AUTH_STATUS:
        raise RuntimeError("authorization is not constrained-state measurement authority")
    authority = payload.get("authority") or {}
    if authority.get("scientific_experiment") is not True or authority.get("measurement_only") is not True:
        raise RuntimeError("constrained-state measurement authority absent")
    for forbidden in (
        "updater",
        "analyzer",
        "second_backbone",
        "public_benchmark",
        "e3_confirmation",
        "paper_promotion",
        "submission",
    ):
        if authority.get(forbidden) is not False:
            raise RuntimeError(f"constrained-state authorization must forbid {forbidden}")
    scope = payload.get("execution_scope") or {}
    if scope.get("measurement_child") != "E2-R17-SINGLE-CASE-CONSTRAINED-STATE-MICRO":
        raise RuntimeError("constrained-state child identity drift")
    if scope.get("allowed_modes") != ["e1"] or mode != "e1":
        raise RuntimeError("constrained-state actor permits exact mode=e1 only")
    allowed_tasks = [str(value) for value in scope.get("allowed_task_ids") or []]
    if len(allowed_tasks) != 18 or len(task_ids) != 1 or task_ids[0] not in allowed_tasks:
        raise RuntimeError("constrained-state actor invocation must select exactly one frozen heldout task")
    if int(scope.get("exact_k", -1)) != int(k) or int(k) != 1:
        raise RuntimeError("constrained-state authorization requires exact K=1")
    if scope.get("allow_noninitial_skill") is not True:
        raise RuntimeError("constrained-state authorization must allow bound deterministic skills")
    return payload, base.sha256(authorization)


base.validate_authority = validate_authority

if __name__ == "__main__":
    raise SystemExit(base.main())
