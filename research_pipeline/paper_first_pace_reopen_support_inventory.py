from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PRIMARY_REF = "arXiv:2608.14441"
SCHEMA_VERSION = "1.0"
CANDIDATE_ID = "AUTO-1-PACE-ONLY-REOPEN-SUPPORT"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _attempt_view(row: dict[str, Any]) -> dict[str, Any]:
    """Keep only information observable after one verified attempt.

    Timestamps and wall-clock verification latency are deliberately excluded: they are
    execution metadata, not part of the scientific repair state.
    """
    return {
        "attempt": int(row.get("attempt") or 0),
        "phase": str(row.get("phase") or ""),
        "code_sha256": str(row.get("code_sha256") or ""),
        "score": row.get("score"),
        "success": row.get("success") is True,
        "constraints": row.get("constraints") or {},
        "outcome": row.get("outcome") or {},
        "physics": row.get("physics") or {},
        "step_count": row.get("step_count"),
    }


def _generator_capability(payload: dict[str, Any]) -> dict[str, Any]:
    config = payload.get("config") or {}
    calls = ((payload.get("metadata") or {}).get("strategy_runtime") or {}).get("candidate_calls") or []
    resolved = sorted({str(row.get("model") or "") for row in calls if isinstance(row, dict) and str(row.get("model") or "")})
    return {
        "requested_model": str(payload.get("model") or ""),
        "resolved_candidate_models": resolved,
        "provider": str(payload.get("provider") or ""),
        "max_tokens": config.get("max_tokens"),
        "temperature": config.get("temperature"),
        "top_p": config.get("top_p"),
        "seed": config.get("seed"),
    }


def _states_for_file(path: Path, relative_path: str) -> list[dict[str, Any]]:
    payload = _load(path)
    attempts = [row for row in payload.get("attempts") or [] if isinstance(row, dict)]
    budget = int(payload.get("attempt_budget") or 0)
    capability = _generator_capability(payload)
    states: list[dict[str, Any]] = []
    history: list[dict[str, Any]] = []
    for index, attempt in enumerate(attempts):
        history.append(_attempt_view(attempt))
        attempt_no = int(attempt.get("attempt") if attempt.get("attempt") is not None else index)
        state = {
            "source_result": relative_path,
            "task_path": str(payload.get("task_path") or ""),
            "target_environment": str(payload.get("target_environment") or ""),
            "strategy": str(payload.get("strategy") or ""),
            "attempt": attempt_no,
            "remaining_budget": max(0, budget - attempt_no),
            "current_code_sha256": str(attempt.get("code_sha256") or ""),
            "current_score": attempt.get("score"),
            "target_specification": {
                "task_path": str(payload.get("task_path") or ""),
                "source_environment": str(payload.get("source_environment") or ""),
                "target_environment": str(payload.get("target_environment") or ""),
                "environment_pair": str(payload.get("environment_pair") or ""),
            },
            "generator_capability": capability,
            "verified_history": list(history),
        }
        # Same-information contract from the scoped PACE principle closure. Search strategy
        # is intentionally excluded: it is the controller being compared, not extra evidence.
        state["same_information_fingerprint"] = _stable_sha({
            "target_specification": state["target_specification"],
            "current_code_sha256": state["current_code_sha256"],
            "verified_history": state["verified_history"],
            "generator_capability": capability,
            "remaining_budget": state["remaining_budget"],
        })
        states.append(state)
    return states


def build_inventory(results_root: Path, source_audit_path: Path) -> dict[str, Any]:
    audit = _load(source_audit_path)
    if audit.get("primary_ref") != PRIMARY_REF:
        raise ValueError("PACE source audit primary ref mismatch")
    source_audit_sha = _sha(source_audit_path)
    listed = ((audit.get("real_trajectory_audit") or {}).get("result_file_hashes") or [])
    if len(listed) != 24:
        raise ValueError(f"expected 24 source-audited PACE result files, found {len(listed)}")

    states: list[dict[str, Any]] = []
    result_hashes: list[dict[str, str]] = []
    for item in listed:
        rel = str((item or {}).get("relative_path") or "")
        expected = str((item or {}).get("sha256") or "")
        path = results_root / rel
        if not path.exists():
            raise FileNotFoundError(path)
        actual = _sha(path)
        if actual != expected:
            raise ValueError(f"PACE result digest mismatch:{rel}")
        result_hashes.append({"relative_path": rel, "sha256": actual})
        states.extend(_states_for_file(path, rel))

    by_same: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for state in states:
        by_same[state["same_information_fingerprint"]].append(state)
    duplicate_groups = [rows for rows in by_same.values() if len(rows) > 1]
    duplicate_sizes = Counter(len(rows) for rows in duplicate_groups)

    # A valid reopen contrast needs the entire pre-outcome repair state to match while
    # some preregistered physics/program structural variable differs. The released
    # trajectories expose no such variable among same-information duplicates: every
    # duplicate is the identical initial program under the same task/target, evaluated by
    # CodeEvolve versus Tree-of-Thoughts before either controller has made a revision.
    eligible_structural_groups = []
    same_info_strategy_pairs = []
    for rows in duplicate_groups:
        strategies = sorted({row["strategy"] for row in rows})
        targets = sorted({json.dumps(row["target_specification"], sort_keys=True) for row in rows})
        codes = sorted({row["current_code_sha256"] for row in rows})
        histories = sorted({_stable_sha(row["verified_history"]) for row in rows})
        if len(strategies) > 1:
            same_info_strategy_pairs.append(rows)
        if len(targets) == 1 and len(codes) > 1 and len(histories) == 1:
            eligible_structural_groups.append(rows)

    initial_by_task_code: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for state in states:
        if state["attempt"] == 0:
            initial_by_task_code[(state["task_path"], state["current_code_sha256"])].append(state)
    cross_target_initial_groups = [
        rows for rows in initial_by_task_code.values()
        if len({row["target_environment"] for row in rows}) > 1
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": CANDIDATE_ID,
        "primary_ref": PRIMARY_REF,
        "source_audit": {
            "artifact": str(source_audit_path),
            "sha256": source_audit_sha,
            "result_file_hashes": result_hashes,
        },
        "reopen_contract": {
            "same_known_repair_surface": True,
            "same_target_specification": True,
            "same_complete_pre_outcome_verifier_transcript": True,
            "same_candidate_program_and_refinement_history": True,
            "same_generator_capability": True,
            "same_remaining_budget": True,
            "required_new_variable": "a preregistered physics/program structural variable that changes an ex-ante next-repair or success/reachability prediction beyond generic CEGIS/version-space, REx-style search allocation, and standard program repair",
        },
        "summary": {
            "result_files": len(result_hashes),
            "attempt_states": len(states),
            "same_information_duplicate_groups": len(duplicate_groups),
            "duplicate_group_sizes": {str(key): value for key, value in sorted(duplicate_sizes.items())},
            "same_information_cross_strategy_groups": len(same_info_strategy_pairs),
            "eligible_physics_program_structural_contrast_groups": len(eligible_structural_groups),
            "same_initial_program_cross_target_groups": len(cross_target_initial_groups),
        },
        "support_diagnosis": {
            "status": "INSUFFICIENT_FOR_PACE_REOPEN_CONTRACT",
            "stop_class": "SUPPORT_STOP",
            "failure_layer": "experiment_identifiability",
            "failure_subtype": "NO_SAME_INFORMATION_STRUCTURAL_CONTRAST",
            "reason": "The 24 released/collected PACE trajectories contain complete candidate code, verifier outcomes, lineage metadata, and remaining-budget information, but no matched state satisfying the scoped reopen contract while varying a preregistered physics/program structural variable. The only same-information duplicates are the identical attempt-0 program under the same target before CodeEvolve and Tree-of-Thoughts diverge. Cross-Stage initial-program matches change the target specification and therefore are not valid same-information contrasts.",
            "principle_dead_end_certified": False,
            "principle_update_allowed": False,
            "benchmark_level_dead_end_certified": False,
            "next_action": "Keep PACE as an evidence asset. Reopen only after first-party or independently verified matched states expose the same surface/specification/transcript/history/generator/budget with a preregistered physics/program structural variable that forces a different ex-ante repair or reachability prediction.",
        },
        "authority": {
            "paper": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
        },
        "scientific_authority": False,
    }


def validate_inventory(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = state.get("summary") or {}
    diagnosis = state.get("support_diagnosis") or {}
    if state.get("primary_ref") != PRIMARY_REF:
        errors.append("wrong PACE ref")
    if summary.get("result_files") != 24:
        errors.append("PACE reopen inventory must bind 24 result files")
    if summary.get("attempt_states") != 162:
        errors.append("PACE reopen inventory attempt-state count drift")
    if summary.get("same_information_duplicate_groups") != 12 or summary.get("duplicate_group_sizes") != {"2": 12}:
        errors.append("PACE same-information duplicate structure drift")
    if summary.get("same_information_cross_strategy_groups") != 12:
        errors.append("PACE same-information cross-strategy group count drift")
    if summary.get("eligible_physics_program_structural_contrast_groups") != 0:
        errors.append("PACE current assets unexpectedly satisfy the structural reopen contrast")
    if summary.get("same_initial_program_cross_target_groups") != 6:
        errors.append("PACE cross-target initial-program group count drift")
    if diagnosis.get("status") != "INSUFFICIENT_FOR_PACE_REOPEN_CONTRACT" or diagnosis.get("stop_class") != "SUPPORT_STOP":
        errors.append("PACE reopen support must remain a support hold")
    if diagnosis.get("failure_layer") != "experiment_identifiability":
        errors.append("PACE reopen support must map to experiment_identifiability")
    if diagnosis.get("principle_dead_end_certified") is not False or diagnosis.get("principle_update_allowed") is not False:
        errors.append("PACE reopen support insufficiency cannot update the principle")
    if state.get("scientific_authority") is not False or any((state.get("authority") or {}).values()):
        errors.append("PACE reopen inventory must have zero downstream authority")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory PACE trajectory support for the scoped same-information reopen contract.")
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--source-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    state = build_inventory(args.results_root, args.source_audit)
    errors = validate_inventory(state)
    if errors:
        raise SystemExit("invalid PACE reopen support inventory: " + "; ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), **state["summary"], "status": state["support_diagnosis"]["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
