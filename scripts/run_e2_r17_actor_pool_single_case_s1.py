#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts import run_e2_r17_actor_pool_repair2_continuation_v2 as base

AUTH_STATUS = "AUTHORIZED_E2_R17_SINGLE_CASE_DIAGNOSTIC_WITNESS_S1"


def validate_authority(
    *,
    mode: str,
    authorization: Path | None,
    task_ids: list[str],
    split: dict[str, Any],
    k: int,
) -> tuple[dict[str, Any] | None, str | None]:
    if mode == "protocol_smoke":
        return base.validate_authority(mode=mode, authorization=authorization, task_ids=task_ids, split=split, k=k)
    if authorization is None:
        raise RuntimeError("single-case S1 scientific actor execution requires --authorization")
    payload = base.json.loads(authorization.read_text(encoding="utf-8"))
    if payload.get("status") != AUTH_STATUS:
        raise RuntimeError("authorization artifact is not a single-case S1 authorization")
    authority = payload.get("authority") or {}
    if authority.get("scientific_experiment") is not True or authority.get("single_case_s1") is not True:
        raise RuntimeError("authorization has no single-case S1 scientific authority")
    for forbidden in ("analyzer", "paper_promotion", "submission", "second_backbone", "public_benchmark"):
        if authority.get(forbidden) is not False:
            raise RuntimeError(f"single-case S1 authorization must forbid {forbidden}")
    scope = payload.get("execution_scope")
    if not isinstance(scope, dict) or scope.get("phase") != "single_case_s1":
        raise RuntimeError("single-case S1 execution_scope drift")
    if scope.get("allow_noninitial_skill") is not True:
        raise RuntimeError("single-case S1 must allow only bound learned skills for heldout evaluation")
    allowed_modes = {str(value) for value in scope.get("allowed_modes") or []}
    if mode not in allowed_modes:
        raise RuntimeError(f"single-case S1 authorization does not allow mode={mode}")
    allowed_tasks = {str(value) for value in scope.get("allowed_task_ids") or []}
    if not allowed_tasks or not set(task_ids).issubset(allowed_tasks):
        raise RuntimeError("single-case S1 authorization does not allow requested heldout tasks")
    if int(scope.get("exact_k", -1)) != int(k):
        raise RuntimeError("single-case S1 exact K drift")
    return payload, base.sha256(authorization)


base.validate_authority = validate_authority

if __name__ == "__main__":
    raise SystemExit(base.main())
