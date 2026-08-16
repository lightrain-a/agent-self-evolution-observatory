from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Iterable

from .config import PROJECT_ROOT

DEFAULT_CONTRACT = PROJECT_ROOT / "generated" / "asset-first-stri-qwen3-solver-consequence-p0c-contract-20260816.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "generated" / "asset-first-stri-p0c-feedback-selection-retrospective-20260817.json"
DEFAULT_AUTHOR_REPO = Path("/data/wyt/skill-self-play-agent3-20260816")
DEFAULT_EXECUTION_AUDIT = PROJECT_ROOT / "generated" / "asset-first-stri-p0c-execution-audit-20260817.json"
FIRST_PARTY_LIBRARY_SHA256 = "8441de35078fc4c70880204c46a06856e99cdde7700ff859097032065e2756e0"
FIRST_PARTY_UPLOAD_SHA256 = "239b958fa539e7fca0b26b475b619c0181f2f4d279e69e9ec053bb3b503b5ba9"

# These are the real defaults in question_evaluate/upload.py at the pinned author commit.
FIRST_PARTY_MIN_SCORE = 0.30
FIRST_PARTY_MAX_SCORE = 0.70
FIRST_PARTY_PRUNE = {
    "min_attempts": 8,
    "avg_p_hat_threshold": 0.75,
    "too_easy_rate_threshold": 0.60,
    "preserve_initial_skills": True,
}
SOURCE_FIELDS = (
    "source_skill_id",
    "source_index",
    "p_hat",
    "consistency",
    "candidate_count",
    "correct_count",
)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head(repo: Path) -> str:
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(tmp.read_text(encoding="utf-8"))
    tmp.replace(path)


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    if isinstance(value, str) and value.strip().lower() in {"0", "1", "false", "true"}:
        return value.strip().lower() in {"1", "true"}
    raise ValueError(f"invalid consistency value: {value!r}")


def load_solver_rows(path: Path, *, source_ids: Iterable[str], samples_per_task: int) -> list[dict[str, Any]]:
    allowed = set(source_ids)
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        raw = json.loads(line)
        missing = [key for key in SOURCE_FIELDS if key not in raw]
        if missing:
            raise ValueError(f"solver row line {line_no} missing fields {missing}")
        source = str(raw["source_skill_id"]).strip()
        index = int(raw["source_index"])
        key = (source, index)
        if source not in allowed:
            raise ValueError(f"solver row line {line_no} has unexpected source {source}")
        if key in seen:
            raise ValueError(f"duplicate solver unit {key}")
        seen.add(key)
        p_hat = float(raw["p_hat"])
        consistency = _as_bool(raw["consistency"])
        candidate_count = int(raw["candidate_count"])
        correct_count = int(raw["correct_count"])
        if not math.isfinite(p_hat) or not 0.0 <= p_hat <= 1.0:
            raise ValueError(f"solver row line {line_no} p_hat outside [0,1]")
        if candidate_count < 0 or candidate_count > samples_per_task:
            raise ValueError(f"solver row line {line_no} invalid candidate_count")
        if correct_count < 0 or correct_count > samples_per_task:
            raise ValueError(f"solver row line {line_no} invalid correct_count")
        expected = correct_count / samples_per_task
        if abs(p_hat - expected) > 1e-9:
            raise ValueError(f"solver row line {line_no} p_hat/correct_count mismatch")
        rows.append(
            {
                "source_skill_id": source,
                "source_index": index,
                "p_hat": p_hat,
                "consistency": consistency,
                "candidate_count": candidate_count,
                "correct_count": correct_count,
            }
        )
    if not rows:
        raise ValueError("solver-results.jsonl contains no rows")
    return rows


def first_party_accepted(row: dict[str, Any]) -> bool:
    # evaluate.py emits score=p_hat. upload.py defaults to score filtering [0.3,0.7],
    # does not require consistency/unique-majority, and has validators disabled.
    # candidate_count>0 is the auditable proxy that the author grader produced a
    # non-empty majority answer; P0-C intentionally did not archive majority_answer.
    return bool(
        FIRST_PARTY_MIN_SCORE <= float(row["p_hat"]) <= FIRST_PARTY_MAX_SCORE
        and int(row["candidate_count"]) > 0
    )


def _apply_stats_update(
    skills: list[dict[str, Any]],
    rows: Iterable[dict[str, Any]],
    *,
    normalize_stats: Callable[[Any], dict[str, Any]],
    iteration: int = 1,
) -> list[dict[str, Any]]:
    """Pure in-memory replay of the pinned update_skill_stats_from_records body.

    The author implementation mutates a library on disk. This equivalent replay keeps
    the frozen first-party package library read-only; sampling itself is delegated to
    the author's exact sampling_weights function.
    """
    out = copy.deepcopy(skills)
    by_id = {str(skill["id"]): skill for skill in out}
    for row in rows:
        skill = by_id.get(str(row["source_skill_id"]))
        if skill is None:
            continue
        p_hat = float(row["p_hat"])
        consistency = bool(row["consistency"])
        is_boundary = FIRST_PARTY_MIN_SCORE <= p_hat <= FIRST_PARTY_MAX_SCORE
        stats = normalize_stats(skill.get("stats", {}))
        previous_attempts = int(stats["attempts"])
        new_attempts = previous_attempts + 1
        stats["avg_p_hat"] = ((float(stats["avg_p_hat"]) * previous_attempts) + p_hat) / new_attempts
        stats["attempts"] = new_attempts
        stats["consistent"] += int(consistency)
        stats["boundary"] += int(is_boundary)
        stats["verified"] += int(consistency and is_boundary)
        stats["too_easy"] += int(p_hat > FIRST_PARTY_MAX_SCORE)
        stats["too_hard"] += int(p_hat < FIRST_PARTY_MIN_SCORE)
        stats["inconsistent"] += int(not consistency)
        stats["last_updated_iteration"] = int(iteration)
        skill["stats"] = stats
    return out


def _pruned(skill: dict[str, Any], normalize_stats: Callable[[Any], dict[str, Any]]) -> bool:
    stats = normalize_stats(skill.get("stats", {}))
    attempts = int(stats["attempts"])
    if FIRST_PARTY_PRUNE["preserve_initial_skills"] and int(skill.get("added_iteration", -1)) == 0:
        return False
    if attempts < int(FIRST_PARTY_PRUNE["min_attempts"]):
        return False
    too_easy_rate = float(stats["too_easy"]) / attempts if attempts else 0.0
    return bool(
        float(stats["avg_p_hat"]) >= float(FIRST_PARTY_PRUNE["avg_p_hat_threshold"])
        or too_easy_rate >= float(FIRST_PARTY_PRUNE["too_easy_rate_threshold"])
    )


def _snapshot(
    skills: list[dict[str, Any]],
    *,
    source_ids: list[str],
    sampling_weights: Callable[..., list[float]],
    normalize_stats: Callable[[Any], dict[str, Any]],
) -> dict[str, Any]:
    weights = [float(value) for value in sampling_weights(
        skills,
        current_iteration=1,
        tau=1.0,
        use_quality=True,
        use_exploration=True,
        use_decay=False,
    )]
    total = sum(weights)
    by_id: dict[str, dict[str, Any]] = {}
    for skill, weight in zip(skills, weights, strict=True):
        sid = str(skill["id"])
        if sid not in source_ids:
            continue
        by_id[sid] = {
            "weight": weight,
            "probability": weight / total,
            "stats": normalize_stats(skill.get("stats", {})),
            "pruned_by_default_policy": _pruned(skill, normalize_stats),
            "added_iteration": int(skill.get("added_iteration", -1)),
        }
    ranking = sorted(source_ids, key=lambda sid: (-by_id[sid]["weight"], sid))
    return {"source": by_id, "source_ranking": ranking, "all_skill_weight_sum": total, "active_skill_count": len(skills)}


def _sign(value: float, tolerance: float = 1e-12) -> int:
    return 1 if value > tolerance else -1 if value < -tolerance else 0


def decision_reversals(a: dict[str, Any], b: dict[str, Any], source_ids: list[str]) -> dict[str, Any]:
    ranking_reversals = []
    probability_reversals = []
    for i, left in enumerate(source_ids):
        for right in source_ids[i + 1 :]:
            aw = float(a["source"][left]["weight"]) - float(a["source"][right]["weight"])
            bw = float(b["source"][left]["weight"]) - float(b["source"][right]["weight"])
            ap = float(a["source"][left]["probability"]) - float(a["source"][right]["probability"])
            bp = float(b["source"][left]["probability"]) - float(b["source"][right]["probability"])
            if _sign(aw) * _sign(bw) == -1:
                ranking_reversals.append({"left": left, "right": right, "accepted_only_delta": aw, "exposure_aware_delta": bw})
            if _sign(ap) * _sign(bp) == -1:
                probability_reversals.append({"left": left, "right": right, "accepted_only_delta": ap, "exposure_aware_delta": bp})
    prune_reversals = []
    for sid in source_ids:
        av = bool(a["source"][sid]["pruned_by_default_policy"])
        bv = bool(b["source"][sid]["pruned_by_default_policy"])
        if av != bv:
            prune_reversals.append({"skill_id": sid, "accepted_only_pruned": av, "exposure_aware_pruned": bv})
    return {
        "strict_pairwise_sampling_ranking_reversals": ranking_reversals,
        "strict_pairwise_sampling_probability_reversals": probability_reversals,
        "prune_decision_reversals": prune_reversals,
        "any_real_decision_reversal": bool(ranking_reversals or probability_reversals or prune_reversals),
        "tie_to_nontie_is_not_counted_as_reversal": True,
    }


def _load_author(author_repo: Path, contract: dict[str, Any]) -> tuple[list[dict[str, Any]], Callable[..., list[float]], Callable[[Any], dict[str, Any]], dict[str, Any]]:
    if not author_repo.is_dir():
        raise ValueError(f"author repo not found: {author_repo}")
    head = _git_head(author_repo)
    expected_head = str((contract.get("author_asset") or {}).get("repo_commit") or "")
    if head != expected_head:
        raise ValueError(f"author repo commit mismatch expected={expected_head} actual={head}")
    for name, expected in {
        "question_evaluate/evaluate.py": (contract.get("author_asset") or {}).get("evaluate_py_sha256"),
        "tool_call/grading.py": (contract.get("author_asset") or {}).get("grading_py_sha256"),
        "skill_library/library.py": FIRST_PARTY_LIBRARY_SHA256,
        "question_evaluate/upload.py": FIRST_PARTY_UPLOAD_SHA256,
    }.items():
        actual = _sha256(author_repo / name)
        if expected and actual != expected:
            raise ValueError(f"author file hash mismatch: {name}")
    if str(author_repo) not in sys.path:
        sys.path.insert(0, str(author_repo))
    from skill_library.library import normalize_skill_stats, sampling_weights  # type: ignore
    from skill_library.package_library import load_package_library  # type: ignore

    package_root = author_repo / "tool_call" / "packages"
    skills = load_package_library(str(package_root), load_level="metadata")
    if not skills:
        raise ValueError("author package library is empty")
    receipts = {
        "repo_commit": head,
        "evaluate_py_sha256": _sha256(author_repo / "question_evaluate" / "evaluate.py"),
        "grading_py_sha256": _sha256(author_repo / "tool_call" / "grading.py"),
        "library_py_sha256": _sha256(author_repo / "skill_library" / "library.py"),
        "upload_py_sha256": _sha256(author_repo / "question_evaluate" / "upload.py"),
        "package_skill_count": len(skills),
        "author_repo_read_only": True,
    }
    return skills, sampling_weights, normalize_skill_stats, receipts


def analyze(
    rows: list[dict[str, Any]],
    *,
    skills: list[dict[str, Any]],
    source_ids: list[str],
    sampling_weights: Callable[..., list[float]],
    normalize_stats: Callable[[Any], dict[str, Any]],
) -> dict[str, Any]:
    accepted = [row for row in rows if first_party_accepted(row)]
    accepted_skills = _apply_stats_update(skills, accepted, normalize_stats=normalize_stats)
    exposed_skills = _apply_stats_update(skills, rows, normalize_stats=normalize_stats)
    accepted_snapshot = _snapshot(accepted_skills, source_ids=source_ids, sampling_weights=sampling_weights, normalize_stats=normalize_stats)
    exposed_snapshot = _snapshot(exposed_skills, source_ids=source_ids, sampling_weights=sampling_weights, normalize_stats=normalize_stats)
    reversals = decision_reversals(accepted_snapshot, exposed_snapshot, source_ids)
    source_counts = {}
    for sid in source_ids:
        source_rows = [row for row in rows if row["source_skill_id"] == sid]
        accepted_rows = [row for row in accepted if row["source_skill_id"] == sid]
        source_counts[sid] = {"exposed": len(source_rows), "accepted_only": len(accepted_rows), "censored": len(source_rows) - len(accepted_rows)}
    return {
        "decision": "BASELINE_REQUIRED_AFTER_FIRST_PARTY_DECISION_REVERSAL" if reversals["any_real_decision_reversal"] else "STOP_NO_FIRST_PARTY_DECISION_REVERSAL",
        "source_counts": source_counts,
        "accepted_only": accepted_snapshot,
        "exposure_aware": exposed_snapshot,
        "decision_reversal": reversals,
        "baseline_authorized": bool(reversals["any_real_decision_reversal"]),
        "baseline_next": "censored-feedback/selective-sampling same-information baseline" if reversals["any_real_decision_reversal"] else "NONE_STOP_BEFORE_BASELINE",
    }


def run(
    *,
    contract_path: Path,
    p0c_result_path: Path | None,
    solver_results_path: Path | None,
    author_repo: Path,
    output_path: Path,
    execution_audit_path: Path | None = DEFAULT_EXECUTION_AUDIT,
) -> dict[str, Any]:
    contract = _json(contract_path)
    source_ids = [str(value) for value in ((contract.get("units") or {}).get("source_skill_ids") or [])]
    samples_per_task = int((contract.get("solver") or {}).get("samples_per_task") or 0)
    base = {
        "schema_version": "1.0",
        "stage": "P0C_FIRST_PARTY_FEEDBACK_SELECTION_RETROSPECTIVE",
        "candidate_id": contract.get("candidate_id"),
        "experiment_id": contract.get("experiment_id"),
        "zero_gpu": True,
        "provider_calls": 0,
        "training_steps": 0,
        "scientific_authority": False,
        "policy": {
            "requires_auditable_p0c_result_and_exact_solver_raw_sha": True,
            "accepted_only_uses_first_party_upload_defaults": True,
            "exposure_aware_changes_stats_visibility_only_not_solver_outputs": True,
            "sampling_uses_first_party_quality_times_exploration_no_decay": True,
            "strict_pairwise_preference_flip_or_prune_flip_required": True,
            "ordinary_censoring_baseline_forbidden_until_real_reversal": True,
            "missing_input_is_not_empirical_no_reversal": True,
        },
        "field_provenance": {
            "candidate_count": "ToolCallStats.valid_answer_count",
            "correct_count": "round(ToolCallStats.p_hat * ToolCallStats.total_samples)",
            "consistency": "ToolCallStats.consistency",
            "p_hat": "ToolCallStats.p_hat",
        },
        "first_party_defaults": {
            "upload_min_score": FIRST_PARTY_MIN_SCORE,
            "upload_max_score": FIRST_PARTY_MAX_SCORE,
            "require_consistency": False,
            "require_unique_majority": False,
            "reject_perfect_majority": False,
            "validators_enabled": False,
            "sampling_quality": True,
            "sampling_exploration": True,
            "sampling_decay": False,
            "prune": FIRST_PARTY_PRUNE,
        },
    }
    if p0c_result_path is None or solver_results_path is None or not p0c_result_path.is_file() or not solver_results_path.is_file():
        out = {
            **base,
            "decision": "STOP_MISSING_AUDITABLE_P0C_RESULTS",
            "scientific_result_available": False,
            "empirical_no_reversal_established": False,
            "decision_reversal_evaluated": False,
            "baseline_authorized": False,
            "baseline_next": "NONE_MISSING_AUDITABLE_INPUT",
            "input_receipt": {
                "p0c_result_present": bool(p0c_result_path and p0c_result_path.is_file()),
                "solver_results_present": bool(solver_results_path and solver_results_path.is_file()),
                "execution_audit_present": bool(execution_audit_path and execution_audit_path.is_file()),
                "execution_audit_sha256": _sha256(execution_audit_path) if execution_audit_path and execution_audit_path.is_file() else None,
                "execution_audit_status": _json(execution_audit_path).get("status") if execution_audit_path and execution_audit_path.is_file() else None,
            },
        }
        _atomic_json(output_path, out)
        return out

    p0c_result = _json(p0c_result_path)
    solver_sha = _sha256(solver_results_path)
    errors = []
    if str(p0c_result.get("experiment_id") or "") != str(contract.get("experiment_id") or ""):
        errors.append("p0c-experiment-id-mismatch")
    if p0c_result.get("scientific_result_available") is not True:
        errors.append("p0c-scientific-result-not-available")
    if p0c_result.get("protocol_valid_for_scientific_update") is not True:
        errors.append("p0c-protocol-not-valid")
    if str(p0c_result.get("solver_result_sha256") or "") != solver_sha:
        errors.append("solver-result-sha-mismatch")
    if errors:
        out = {
            **base,
            "decision": "STOP_INVALID_P0C_RESULT_BINDING",
            "scientific_result_available": False,
            "empirical_no_reversal_established": False,
            "decision_reversal_evaluated": False,
            "baseline_authorized": False,
            "baseline_next": "NONE_INVALID_INPUT_BINDING",
            "input_binding_errors": errors,
            "input_receipt": {"p0c_result_sha256": _sha256(p0c_result_path), "solver_results_sha256": solver_sha},
        }
        _atomic_json(output_path, out)
        return out

    skills, sampling_weights, normalize_stats, author_receipts = _load_author(author_repo, contract)
    missing_sources = [sid for sid in source_ids if sid not in {str(skill.get("id")) for skill in skills}]
    if missing_sources:
        raise ValueError(f"source skills missing from author package library: {missing_sources}")
    rows = load_solver_rows(solver_results_path, source_ids=source_ids, samples_per_task=samples_per_task)
    analysis = analyze(
        rows,
        skills=skills,
        source_ids=source_ids,
        sampling_weights=sampling_weights,
        normalize_stats=normalize_stats,
    )
    out = {
        **base,
        **analysis,
        "scientific_result_available": True,
        "empirical_no_reversal_established": analysis["decision"] == "STOP_NO_FIRST_PARTY_DECISION_REVERSAL",
        "decision_reversal_evaluated": True,
        "input_receipt": {
            "p0c_result_sha256": _sha256(p0c_result_path),
            "solver_results_sha256": solver_sha,
            "solver_rows": len(rows),
            "samples_per_task": samples_per_task,
        },
        "author_receipt": author_receipts,
    }
    _atomic_json(output_path, out)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p0c-result", type=Path)
    parser.add_argument("--solver-results", type=Path)
    parser.add_argument("--author-repo", type=Path, default=DEFAULT_AUTHOR_REPO)
    parser.add_argument("--execution-audit", type=Path, default=DEFAULT_EXECUTION_AUDIT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    out = run(
        contract_path=args.contract,
        p0c_result_path=args.p0c_result,
        solver_results_path=args.solver_results,
        author_repo=args.author_repo,
        output_path=args.output,
        execution_audit_path=args.execution_audit,
    )
    print(json.dumps({"decision": out["decision"], "baseline_authorized": out.get("baseline_authorized"), "decision_reversal_evaluated": out.get("decision_reversal_evaluated")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
