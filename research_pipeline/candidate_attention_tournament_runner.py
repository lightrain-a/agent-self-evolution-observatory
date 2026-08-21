from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import replace
from pathlib import Path
from typing import Any

from .api_research_memory import (
    record_archived_api_parse_failure,
    record_parsed_api_output,
    record_provider_failure,
    record_raw_api_output,
)
from .ark_provider import ArkResponsesClient, ArkSettings, extract_json_object
from .candidate_attention_tournament import (
    AUTHORITY,
    DIMENSIONS,
    compile_review_batch,
    finalize_attention_tournament,
    prepare_attention_tournament,
)

REVIEWERS = {
    "deepseek": "deepseek-v4-pro",
    "minimax": "minimax-m3",
}
BATCH_SIZE = 6


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


def _client() -> ArkResponsesClient:
    base = ArkSettings.from_env()
    return ArkResponsesClient(replace(base, max_retries=0, timeout_seconds=max(240.0, base.timeout_seconds)))


def prepare(*, machine_path: Path, study: Path, comparisons_per_candidate: int = 3, proximity_threshold: float = 0.25) -> dict[str, Any]:
    output = study / "plan.json"
    lock = _lock(output, {"stage": "prepare", "machine_path": str(machine_path)})
    try:
        machine = _load(machine_path)
        plan = prepare_attention_tournament(
            machine,
            comparisons_per_candidate=comparisons_per_candidate,
            proximity_threshold=proximity_threshold,
        )
        plan["source_machine_sha256"] = _sha(machine_path.read_bytes())
        plan["source_machine_path_hint"] = machine_path.name
        plan["pair_orientation_policy"] = "reviewer-specific-deterministic-swap-normalized-back-to-candidate-id"
        plan["tournament_plan_sha256"] = _sha({k: v for k, v in plan.items() if k != "tournament_plan_sha256"})
        _write(output, plan)
        return plan
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def _swap_for(reviewer_label: str, pair_id: str) -> bool:
    digest = hashlib.sha256(f"attention-orientation:{reviewer_label}:{pair_id}".encode()).hexdigest()
    return int(digest[-1], 16) % 2 == 1


def _oriented_prompt(plan: dict[str, Any], pair_ids: list[str], reviewer_label: str) -> tuple[str, dict[str, bool]]:
    packets = {p["candidate_id"]: p for p in plan.get("candidate_packets") or []}
    pairs = {p["pair_id"]: p for p in plan.get("pair_schedule") or []}
    selected = []
    orientation: dict[str, bool] = {}
    for pid in pair_ids:
        pair = pairs.get(pid)
        if not pair:
            raise ValueError(f"unknown pair: {pid}")
        swap = _swap_for(reviewer_label, pid)
        orientation[pid] = swap
        a_id, b_id = (pair["b"], pair["a"]) if swap else (pair["a"], pair["b"])
        selected.append({"pair_id": pid, "A": packets[a_id], "B": packets[b_id]})
    prompt = f'''You are an advisory candidate-attention tournament reviewer. Rank which frozen candidate deserves scarce research attention first. You may NOT pass, fail, close, eliminate, authorize, or mutate scientific state.

For each pair and each dimension choose A, B, or TIE:
{json.dumps(list(DIMENSIONS),ensure_ascii=False)}
Definitions:
- problem_importance: importance if the exact prediction is true.
- agent_specificity: dependence on persistent agent state/history/memory/self-evolution.
- reduction_resistance: clarity of a residual beyond the stated strongest same-information baseline.
- independent_truth_quality: quality of an externally grounded truth signal.
- falsifier_decisiveness: cheapness and discriminatory power of the bounded falsifier.
- substrate_feasibility: likelihood the frozen falsifier is executable without changing the scientific object.
- paper_contribution: potential paper contribution if the frozen prediction survives.
Overall attention_winner is A/B/TIE. This is scheduling advice only. Do not infer hidden outcomes or invent evidence.

Return JSON only with exactly {len(selected)} reviews:
{{"reviews":[{{"pair_id":"PAIR-...","dimension_winners":{{{','.join(json.dumps(d)+':"A|B|TIE"' for d in DIMENSIONS)}}},"attention_winner":"A|B|TIE","confidence":"HIGH|MEDIUM|LOW","reason":"<=55 words"}}, ...]}}
PAIRS={json.dumps(selected,ensure_ascii=False,separators=(",",":"))}'''
    return prompt, orientation


def _flip(value: str) -> str:
    return "B" if value == "A" else "A" if value == "B" else value


def _normalize_orientation(payload: dict[str, Any], orientation: dict[str, bool]) -> dict[str, Any]:
    rows = []
    for raw in payload.get("reviews") or []:
        row = dict(raw)
        pid = str(row.get("pair_id") or "")
        if orientation.get(pid):
            dims = dict(row.get("dimension_winners") or {})
            row["dimension_winners"] = {key: _flip(str(value)) for key, value in dims.items()}
            row["attention_winner"] = _flip(str(row.get("attention_winner") or ""))
        rows.append(row)
    return {"reviews": rows}


def review(*, study: Path, persistent_root: Path, reviewer_label: str, part: int, batch_size: int = BATCH_SIZE) -> dict[str, Any]:
    if reviewer_label not in REVIEWERS:
        raise ValueError(f"unknown reviewer label: {reviewer_label}")
    plan = _load(study / "plan.json")
    pair_ids = [row["pair_id"] for row in plan.get("pair_schedule") or []]
    start = (int(part) - 1) * int(batch_size)
    selected_ids = pair_ids[start:start + int(batch_size)]
    if not selected_ids:
        raise ValueError(f"empty review batch: reviewer={reviewer_label} part={part}")
    output = study / f"review-{reviewer_label}-p{part}.json"
    run_id = f"candidate-attention-{plan['tournament_plan_sha256'][:12]}-{reviewer_label}-p{part}"
    lock = _lock(output, {"stage": "attention-review", "reviewer": reviewer_label, "part": part, "run_id": run_id})
    model = REVIEWERS[reviewer_label]
    try:
        prompt, orientation = _oriented_prompt(plan, selected_ids, reviewer_label)
        run_root = persistent_root / "runs" / run_id
        run_root.mkdir(parents=True, exist_ok=True)
        prompt_sha = _sha(prompt)
        try:
            response = _client().respond(prompt, model=model, max_output_tokens=5000, temperature=0.0, thinking="disabled", store=True)
        except Exception as error:
            fingerprint = _sha({"stage": "candidate-attention-review", "reviewer": reviewer_label, "part": part, "model": model, "prompt_sha256": prompt_sha, "error": str(error)[:500]})
            receipt = record_provider_failure(
                run_root=run_root,
                stage=f"candidate-attention-{reviewer_label}-p{part}",
                payload={"status": "PROVIDER_ERROR_ZERO_AUTHORITY", "requested_model": model, "error_fingerprint": fingerprint, "prompt_sha256": prompt_sha},
                root=persistent_root,
            )
            failed = {"schema_version": "1.0", "status": "PROVIDER_FAILURE", "run_id": run_id, "reviewer_label": reviewer_label, "part": part, "error_type": type(error).__name__, "error": str(error)[:1400], "provider_failure": receipt, "scientific_authority": False}
            _write(output, failed)
            return failed

        raw = str(response.get("text") or "")
        raw_file = run_root / "raw-review.txt"
        raw_file.write_text(raw, encoding="utf-8")
        request_fp = _sha({"stage": "candidate-attention-review", "reviewer": reviewer_label, "part": part, "model": model, "prompt_sha256": prompt_sha, "pair_ids": selected_ids})
        archived = record_raw_api_output(
            run_root=run_root,
            stage=f"candidate-attention-{reviewer_label}-p{part}",
            raw_path=raw_file,
            requested_model=model,
            resolved_model=str(response.get("resolved_model") or model),
            request_fingerprint=request_fp,
            prompt_sha256=prompt_sha,
            root=persistent_root,
        )
        try:
            parsed = extract_json_object(raw)
            normalized = _normalize_orientation(parsed, orientation)
            compiled = compile_review_batch(
                plan,
                normalized,
                reviewer_label=reviewer_label,
                resolved_model=str(response.get("resolved_model") or model),
                pair_ids=selected_ids,
            )
        except Exception as error:
            record_archived_api_parse_failure(
                run_root=run_root,
                stage=f"candidate-attention-{reviewer_label}-p{part}",
                raw_sha256=archived["raw_sha256"],
                error=f"{type(error).__name__}: {str(error)}",
                requested_model=model,
                resolved_model=str(response.get("resolved_model") or model),
                root=persistent_root,
            )
            failed = {"schema_version": "1.0", "status": "PARSE_OR_PROTOCOL_FAILURE", "run_id": run_id, "reviewer_label": reviewer_label, "part": part, "raw_sha256": archived["raw_sha256"], "error_type": type(error).__name__, "error": str(error)[:1400], "scientific_authority": False}
            _write(output, failed)
            return failed

        structured = {
            "schema_version": "1.0",
            "study": "CANDIDATE_ATTENTION_TOURNAMENT",
            "tournament_plan_sha256": plan["tournament_plan_sha256"],
            "reviewer_label": reviewer_label,
            "part": part,
            "pair_ids": selected_ids,
            "orientation_swapped": orientation,
            "usage": response.get("usage") or {},
            "compiled": compiled,
            "scientific_authority": False,
        }
        record_parsed_api_output(
            run_root=run_root,
            stage=f"candidate-attention-{reviewer_label}-p{part}",
            raw_sha256=archived["raw_sha256"],
            structured_payload=structured,
            requested_model=model,
            resolved_model=str(response.get("resolved_model") or model),
            research_objects=[],
            root=persistent_root,
        )
        out = {**compiled, "run_id": run_id, "part": part, "raw_sha256": archived["raw_sha256"], "prompt_sha256": prompt_sha, "usage": response.get("usage") or {}, "orientation_swapped": orientation}
        _write(output, out)
        return out
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def finalize(*, study: Path, active_slots: int = 4) -> dict[str, Any]:
    output = study / "result.json"
    lock = _lock(output, {"stage": "attention-finalize"})
    try:
        plan = _load(study / "plan.json")
        batches = []
        for label in REVIEWERS:
            files = sorted(study.glob(f"review-{label}-p*.json"))
            if not files:
                raise RuntimeError(f"missing reviewer batches: {label}")
            for path in files:
                payload = _load(path)
                if payload.get("status") != "ATTENTION_REVIEW_BATCH_COMPILED":
                    raise RuntimeError(f"review batch not complete: {path.name}:{payload.get('status')}")
                batches.append(payload)
        result = finalize_attention_tournament(plan, batches, active_slots=active_slots)
        result["review_batch_files"] = sorted(path.name for label in REVIEWERS for path in study.glob(f"review-{label}-p*.json"))
        result["scientific_authority"] = False
        result["authority"] = dict(AUTHORITY)
        result["tournament_result_sha256"] = _sha({k: v for k, v in result.items() if k != "tournament_result_sha256"})
        _write(output, result)
        return result
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--machine", type=Path, required=True); p.add_argument("--study", type=Path, required=True)
    p.add_argument("--comparisons-per-candidate", type=int, default=3); p.add_argument("--proximity-threshold", type=float, default=0.25)
    r = sub.add_parser("review")
    r.add_argument("--study", type=Path, required=True); r.add_argument("--persistent-root", type=Path, required=True)
    r.add_argument("--reviewer", choices=sorted(REVIEWERS), required=True); r.add_argument("--part", type=int, required=True); r.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    f = sub.add_parser("finalize"); f.add_argument("--study", type=Path, required=True); f.add_argument("--active-slots", type=int, default=4)
    args = parser.parse_args()
    if args.cmd == "prepare": out = prepare(machine_path=args.machine, study=args.study, comparisons_per_candidate=args.comparisons_per_candidate, proximity_threshold=args.proximity_threshold)
    elif args.cmd == "review": out = review(study=args.study, persistent_root=args.persistent_root, reviewer_label=args.reviewer, part=args.part, batch_size=args.batch_size)
    else: out = finalize(study=args.study, active_slots=args.active_slots)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
