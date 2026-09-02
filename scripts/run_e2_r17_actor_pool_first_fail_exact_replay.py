#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from scripts import run_e2_r17_actor_pool_repair2_continuation_v2 as base

AUTH_STATUS="AUTHORIZED_E2_R17_SINGLE_CASE_FIRST_FAIL_EXACT_REPLAY"


def validate_authority(*,mode:str,authorization:Path|None,task_ids:list[str],split:dict[str,Any],k:int)->tuple[dict[str,Any]|None,str|None]:
    if mode=="protocol_smoke": return base.validate_authority(mode=mode,authorization=authorization,task_ids=task_ids,split=split,k=k)
    if authorization is None: raise RuntimeError("exact-replay actor requires --authorization")
    payload=base.json.loads(authorization.read_text(encoding="utf-8"))
    if payload.get("status")!=AUTH_STATUS: raise RuntimeError("authorization is not exact-replay authority")
    au=payload.get("authority") or {}
    if au.get("scientific_experiment") is not True or au.get("exact_replay") is not True: raise RuntimeError("exact-replay authority absent")
    for forbidden in ("analyzer","paper_promotion","submission","second_backbone","public_benchmark","e3_confirmation"):
        if au.get(forbidden) is not False: raise RuntimeError(f"exact-replay authorization must forbid {forbidden}")
    scope=payload.get("execution_scope") or {}
    if scope.get("phase")!="single_case_first_fail_exact_replay": raise RuntimeError("exact-replay phase drift")
    if scope.get("allow_noninitial_skill") is not True: raise RuntimeError("exact-replay learned skill authority absent")
    if mode not in set(map(str,scope.get("allowed_modes") or [])): raise RuntimeError("exact-replay mode not allowed")
    allowed=set(map(str,scope.get("allowed_task_ids") or []))
    if not set(task_ids).issubset(allowed): raise RuntimeError("exact-replay task scope drift")
    if int(scope.get("exact_k",-1))!=int(k): raise RuntimeError("exact-replay K drift")
    return payload,base.sha256(authorization)

base.validate_authority=validate_authority
if __name__=="__main__": raise SystemExit(base.main())
