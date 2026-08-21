from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .paper_first_evidence_acquisition import (
    build_substrate_preflight_request,
    compile_evidence_designs,
    compile_evidence_reviews,
    evidence_design_prompt,
    evidence_review_prompt,
    validate_evidence_plan,
)
from .premium_model_policy import preferred_model
from .problem_search_stage_runner import (
    _ark_with_provider_receipt,
    _evidence_memory_pack,
    _parse_archived_evidence_design_json,
    _record_memory_receipt,
)


def _canon(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(value: Any) -> str:
    if isinstance(value, bytes):
        return hashlib.sha256(value).hexdigest()
    if isinstance(value, str):
        return hashlib.sha256(value.encode()).hexdigest()
    return hashlib.sha256(_canon(value).encode()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _lock(output: Path, payload: dict[str, Any]) -> Path:
    if output.exists():
        raise RuntimeError(f"OUTPUT_ALREADY_EXISTS:{output}")
    lock = Path(str(output) + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise RuntimeError(f"STAGE_ALREADY_RUNNING_OR_STALE_LOCK:{lock}") from error
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        handle.flush(); os.fsync(handle.fileno())
    return lock


def prepare(*, source_plan: Path, study: Path) -> dict[str, Any]:
    output = study / "evidence-plan.json"
    lock = _lock(output, {"stage": "prepare", "source_plan": str(source_plan)})
    try:
        plan = _load(source_plan)
        errors = validate_evidence_plan(plan)
        if errors:
            raise ValueError(f"source evidence plan invalid: {errors}")
        plan = dict(plan)
        plan["attention_evidence_source_sha256"] = _sha(source_plan.read_bytes())
        plan["attention_evidence_study"] = study.name
        _write(output, plan)
        return {"status": "ATTENTION_EVIDENCE_PREPARED", "source_sha256": plan["attention_evidence_source_sha256"], "summary": plan.get("summary") or {}, "scientific_authority": False}
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def design(*, study: Path, persistent_root: Path, part: int, batch_size: int = 2) -> dict[str, Any]:
    plan_path = study / "evidence-plan.json"
    plan = _load(plan_path)
    pending = [
        str(row.get("candidate_id") or "")
        for row in plan.get("entries") or []
        if isinstance(row, dict)
        and row.get("design_selected") is True
        and row.get("status") in {"NEEDS_BOUNDED_EVIDENCE_DESIGN", "BRANCH_REPAIR_READY"}
    ][:batch_size]
    if not pending:
        raise ValueError(f"no evidence-design candidates pending for part={part}")
    output = study / f"design-p{part}.json"
    lock = _lock(output, {"stage": "design", "part": part, "candidate_ids": pending})
    try:
        memory_pack = _evidence_memory_pack(plan, candidate_ids=pending)
        prompt, candidate_ids = evidence_design_prompt(
            plan,
            part=part,
            batch_size=batch_size,
            research_memory_query_pack=memory_pack,
        )
        if candidate_ids != pending:
            raise ValueError("attention evidence-design candidate drift")
        requested_model = preferred_model("evidence_design", "premium-auto")
        run_id = f"attention-evidence-{_sha({'study':study.name,'part':part,'candidates':pending})[:12]}-design"
        run_root = persistent_root / "runs" / run_id
        run_root.mkdir(parents=True, exist_ok=True)
        response = _ark_with_provider_receipt(
            run_root=run_root,
            stem=f"attention-evidence-design-p{part}",
            requested_model=requested_model,
            context={"part": part, "candidate_ids": candidate_ids},
            prompt=prompt,
            max_output_tokens=5200,
            temperature=0.0,
        )
        raw = str(response.get("text") or "")
        resolved = str(response.get("resolved_model") or requested_model)
        payload, raw_sha = _parse_archived_evidence_design_json(
            run_root,
            f"attention-evidence-design-p{part}",
            raw,
            resolved,
            provider_response=response,
            requested_model=requested_model,
        )
        state = compile_evidence_designs(plan, payload, part=part, design_model=resolved)
        _record_memory_receipt(state, stage="attention-evidence-design", part=part, pack=memory_pack)
        errors = validate_evidence_plan(state)
        if errors:
            raise ValueError(f"compiled evidence plan invalid: {errors}")
        _write(plan_path, state)
        out = {
            "schema_version": "1.0",
            "status": "ATTENTION_EVIDENCE_DESIGN_COMPILED",
            "part": part,
            "run_id": run_id,
            "candidate_ids": candidate_ids,
            "requested_model": requested_model,
            "resolved_model": resolved,
            "raw_sha256": raw_sha,
            "memory_query_pack_sha256": memory_pack.get("query_pack_sha256"),
            "memory_selected_ids": memory_pack.get("selected_memory_ids") or [],
            "summary": state.get("summary") or {},
            "scientific_authority": False,
        }
        out["stage_sha256"] = _sha(out)
        _write(output, out)
        return out
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def review(*, study: Path, persistent_root: Path, part: int, batch_size: int = 2) -> dict[str, Any]:
    plan_path = study / "evidence-plan.json"
    plan = _load(plan_path)
    pending = [str(row.get("candidate_id") or "") for row in plan.get("entries") or [] if isinstance(row, dict) and row.get("status") == "NEEDS_INDEPENDENT_EVIDENCE_REVIEW"][:batch_size]
    if not pending:
        raise ValueError(f"no evidence-review candidates pending for part={part}")
    output = study / f"review-p{part}.json"
    lock = _lock(output, {"stage": "review", "part": part, "candidate_ids": pending})
    try:
        prompt, candidate_ids = evidence_review_prompt(plan, part=part, batch_size=batch_size)
        if candidate_ids != pending:
            raise ValueError("attention evidence-review candidate drift")
        requested_model = preferred_model("evidence_review", "premium-auto")
        run_id = f"attention-evidence-{_sha({'study':study.name,'part':part,'candidates':pending})[:12]}-review"
        run_root = persistent_root / "runs" / run_id
        run_root.mkdir(parents=True, exist_ok=True)
        response = _ark_with_provider_receipt(
            run_root=run_root,
            stem=f"attention-evidence-review-p{part}",
            requested_model=requested_model,
            context={"part": part, "candidate_ids": candidate_ids},
            prompt=prompt,
            max_output_tokens=4800,
            temperature=0.0,
        )
        raw = str(response.get("text") or "")
        resolved = str(response.get("resolved_model") or requested_model)
        payload, raw_sha = _parse_archived_evidence_design_json(
            run_root,
            f"attention-evidence-review-p{part}",
            raw,
            resolved,
            provider_response=response,
            requested_model=requested_model,
        )
        state = compile_evidence_reviews(plan, payload, part=part, reviewer_model=resolved)
        errors = validate_evidence_plan(state)
        if errors:
            raise ValueError(f"compiled evidence plan invalid: {errors}")
        _write(plan_path, state)
        out = {
            "schema_version": "1.0",
            "status": "ATTENTION_EVIDENCE_REVIEW_COMPILED",
            "part": part,
            "run_id": run_id,
            "candidate_ids": candidate_ids,
            "requested_model": requested_model,
            "resolved_model": resolved,
            "raw_sha256": raw_sha,
            "summary": state.get("summary") or {},
            "scientific_authority": False,
        }
        out["stage_sha256"] = _sha(out)
        _write(output, out)
        return out
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def substrate_request(*, study: Path) -> dict[str, Any]:
    output = study / "substrate-request.json"
    lock = _lock(output, {"stage": "substrate-request"})
    try:
        plan = _load(study / "evidence-plan.json")
        request = build_substrate_preflight_request(plan)
        _write(output, request)
        return request
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare"); p.add_argument("--source-plan", type=Path, required=True); p.add_argument("--study", type=Path, required=True)
    d = sub.add_parser("design"); d.add_argument("--study", type=Path, required=True); d.add_argument("--persistent-root", type=Path, required=True); d.add_argument("--part", type=int, required=True); d.add_argument("--batch-size", type=int, default=2)
    r = sub.add_parser("review"); r.add_argument("--study", type=Path, required=True); r.add_argument("--persistent-root", type=Path, required=True); r.add_argument("--part", type=int, required=True); r.add_argument("--batch-size", type=int, default=2)
    s = sub.add_parser("substrate-request"); s.add_argument("--study", type=Path, required=True)
    args = parser.parse_args()
    if args.cmd == "prepare": out = prepare(source_plan=args.source_plan, study=args.study)
    elif args.cmd == "design": out = design(study=args.study, persistent_root=args.persistent_root, part=args.part, batch_size=args.batch_size)
    elif args.cmd == "review": out = review(study=args.study, persistent_root=args.persistent_root, part=args.part, batch_size=args.batch_size)
    else: out = substrate_request(study=args.study)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
