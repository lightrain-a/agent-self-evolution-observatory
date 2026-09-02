#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import run_e2_r17_actor_pool_measurement_compat_v1 as base

AUTH_STATUS = "AUTHORIZED_E2_R17_SINGLE_CASE_FIRST_FAIL_STABILITY_MEASUREMENT"


def validate_authority(
    *,
    mode: str,
    authorization: Path | None,
    task_ids: list[str],
    split: dict[str, Any],
    k: int,
    stop_before_provider_io: bool,
) -> tuple[dict[str, Any], str]:
    if mode != "e1":
        raise RuntimeError("single-case stability actor permits exact mode=e1 only")
    if authorization is None:
        raise RuntimeError("single-case stability actor requires --authorization")
    payload = base.json.loads(authorization.read_text(encoding="utf-8"))
    contract_path = Path(str(payload.get("contract_path") or ""))
    if not contract_path.is_file() or base.sha256(contract_path) != payload.get("contract_sha256"):
        raise RuntimeError("stability authorization/contract binding drift")
    if payload.get("status") != AUTH_STATUS:
        raise RuntimeError("authorization artifact is not a single-case stability authorization")
    authority = payload.get("authority") or {}
    if authority.get("scientific_experiment") is not True or authority.get("measurement_only") is not True:
        raise RuntimeError("stability measurement authority absent")
    for forbidden in ("updater", "analyzer", "second_backbone", "public_benchmark", "e3_confirmation", "paper_promotion", "submission"):
        if authority.get(forbidden) is not False:
            raise RuntimeError(f"stability authorization must forbid {forbidden}")
    scope = payload.get("execution_scope") or {}
    if scope.get("measurement_child") != "E2-R17-SINGLE-CASE-FIRST-FAIL-STABILITY":
        raise RuntimeError("stability child identity drift")
    if scope.get("allowed_modes") != ["e1"]:
        raise RuntimeError("stability authorization must bind exact mode=e1")
    allowed_tasks = [str(value) for value in scope.get("allowed_task_ids") or []]
    if len(allowed_tasks) != 18 or len(task_ids) != 1 or task_ids[0] not in allowed_tasks:
        raise RuntimeError("stability invocation must select exactly one frozen heldout task")
    if int(scope.get("exact_k", -1)) != int(k) or int(k) != 1:
        raise RuntimeError("stability authorization requires exact K=1")
    if scope.get("allow_noninitial_skill") is not True:
        raise RuntimeError("stability authorization must allow exact bound noninitial skills")
    learned = scope.get("learned_states") or []
    if len(learned) != 2 or {str(row.get("arm")) for row in learned} != {"win_c", "first_fail"}:
        raise RuntimeError("stability authorization must bind exactly WIN-C and First-Fail states")
    return payload, base.sha256(authorization)


base.validate_authority = validate_authority

if __name__ == "__main__":
    raise SystemExit(base.main())
