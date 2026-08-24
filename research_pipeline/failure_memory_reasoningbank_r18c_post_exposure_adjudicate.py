from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_R15_SHA = "707d2f630ef4a6d40f607ff156348223a424e7a76df96c6c6925747fb66b3c59"
EXPECTED_R16_SHA = "f12b18c129c4e65c076b2f811b65a0a505bf618665f63c87fb883c6d4cf72b4b"
EXPECTED_EXECUTOR_MANIFEST = "5bce411d829007ce344871ae10ea7f02f91d86c932617a7f982e2380bbb1c216"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_bound(path: Path, expected: str, label: str) -> dict[str, Any]:
    actual = sha256_file(path)
    if actual != expected:
        raise RuntimeError(f"{label} digest mismatch: {actual} != {expected}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_receipt(
    r15: dict[str, Any],
    r16: dict[str, Any],
    run_root: Path,
    alias_tags: dict[str, str],
) -> dict[str, Any]:
    failure_path = run_root / "failure.json"
    attempts_path = run_root / "attempts.jsonl"
    if not failure_path.is_file() or not attempts_path.is_file():
        raise RuntimeError("R18c failure/attempt ledger missing")
    failure = json.loads(failure_path.read_text(encoding="utf-8"))
    attempts = [json.loads(x) for x in attempts_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(attempts) != 1 or int(attempts[0]["sequence_index"]) != 0:
        raise RuntimeError("R18c must contain exactly the exposed sequence-0 attempt")

    summary_paths = sorted((run_root / "browsergym").glob("*/summary_info.json"))
    if len(summary_paths) != 1:
        raise RuntimeError("Expected exactly one R18c BrowserGym summary")
    summary_path = summary_paths[0]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    err = str(summary.get("err_msg") or "")
    stack = str(summary.get("stack_trace") or "")
    if "gpt-4-1106-preview" not in err or "404" not in err:
        raise RuntimeError("Unexpected R18c failure class")
    if "env.step(action)" not in stack or "self.evaluator(" not in stack:
        raise RuntimeError("R18c stack does not prove post-action evaluator exposure")
    if int(summary.get("n_steps") or 0) < 1:
        raise RuntimeError("R18c does not show a BrowserGym step")
    if failure.get("scientific_outcome_opened") is not True:
        raise RuntimeError("Runner failure receipt did not mark scientific exposure")

    completion_policy = r15["completion_and_retry_policy"]
    if completion_policy["confirmatory_analysis_requires_all_144_terminal_episodes"] is not True:
        raise RuntimeError("R15 completeness policy drift")
    if "no retry" not in completion_policy["after_any_scientific_exposure"].lower():
        raise RuntimeError("R15 post-exposure no-retry rule drift")
    if r16["scope"]["single_confirmatory_attempt"] is not True:
        raise RuntimeError("R16 single-attempt scope drift")

    required_aliases = {
        "b1-qwen25-32b-l2b-executor:latest",
        "gpt-4:latest",
        "gpt-4-1106-preview:latest",
    }
    if set(alias_tags) != required_aliases:
        raise RuntimeError("Future-support alias set incomplete")
    if len(set(alias_tags.values())) != 1 or next(iter(alias_tags.values())) != EXPECTED_EXECUTOR_MANIFEST:
        raise RuntimeError("Future-support alias digest mismatch")

    step_files = sorted((run_root / "browsergym").glob("*/step_*.pkl.gz"))
    step_artifacts = [
        {"path": str(p.relative_to(run_root)), "sha256": sha256_file(p), "size": p.stat().st_size}
        for p in step_files
    ]
    if not step_artifacts:
        raise RuntimeError("R18c step artifacts missing")

    return {
        "schema_version": "1.0",
        "paper_id": "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-R18C-POST-EXPOSURE-ADJUDICATION",
        "recorded_date": "2026-08-24",
        "status": "POST_EXPOSURE_EVALUATOR_SUPPORT_FAILURE_CONFIRMATORY_ATTEMPT_STOPPED",
        "role": "FAIL_CLOSED_POST_EXPOSURE_ADJUDICATION",
        "bindings": {
            "r15_sha256": EXPECTED_R15_SHA,
            "r16_sha256": EXPECTED_R16_SHA,
            "executor_manifest_digest": f"sha256:{EXPECTED_EXECUTOR_MANIFEST}",
            "run_root": str(run_root),
            "attempts_jsonl_sha256": sha256_file(attempts_path),
            "failure_json_sha256": sha256_file(failure_path),
            "summary_info_sha256": sha256_file(summary_path),
            "step_artifacts": step_artifacts,
        },
        "failure": {
            "class": "WEBARENA_LLM_EVALUATOR_MODEL_ALIAS_NOT_FOUND_AFTER_AGENT_ACTION",
            "requested_evaluator_model": "gpt-4-1106-preview",
            "http_status": 404,
            "failure_location": "original WebArena StringEvaluator -> llm_ua_match after BrowserGym env.step(action)",
            "browsergym_n_steps": int(summary.get("n_steps") or 0),
            "terminal_score_valid": False,
            "cum_reward_must_not_enter_analysis": True,
            "executor_completion_or_action_exposure_occurred": True,
            "evaluator_call_attempted": True,
            "scientific_exposure_occurred": True,
            "action_content_opened_by_this_adjudication": False,
        },
        "frozen_policy_application": {
            "R15_after_scientific_exposure": completion_policy["after_any_scientific_exposure"],
            "R15_confirmatory_requires_all_144": True,
            "R16_single_confirmatory_attempt": True,
            "retry_sequence_0_under_R16": False,
            "task_replacement_under_R16": False,
            "endpoint_switch_under_R16": False,
            "remaining_143_episodes_under_current_confirmatory_attempt": False,
            "single_confirmatory_attempt_consumed": True,
            "current_R18_confirmatory_execution_stopped": True,
        },
        "future_support_alias_preflight": {
            "aliases": alias_tags,
            "all_aliases_manifest_identical": True,
            "alias_creation_used_model_inference": False,
            "alias_ready_for_future_reopen_only": True,
            "alias_does_not_reauthorize_current_R18": True,
        },
        "adjudication": {
            "support_failure_is_scientific_negative": False,
            "current_l2b_scientific_verdict": "NO_VERDICT_POST_EXPOSURE_SUPPORT_FAILURE",
            "historical_R5_or_bridge_may_rescue": False,
            "R18c_cum_reward_zero_may_be_treated_as_terminal_score": False,
            "R18c_step_or_action_artifact_may_enter_confirmatory_analysis": False,
            "continue_current_144_episode_schedule": False,
        },
        "reopen_condition": {
            "new_explicit_scientific_authority_required": True,
            "new_pre_outcome_execution_contract_required": True,
            "must_disclose_R18_R18b_R18c_support_failure_chain": True,
            "must_not_use_exposed_sequence0_artifacts_for_selection_or_threshold_changes": True,
            "preferred_new_independent_cohort_if_available": True,
            "same_cohort_restart_is_not_automatically_authorized": True,
            "evaluator_model_aliases_must_be_preflighted_before_any_new_episode": True,
        },
        "scientific_verdict": "NO_VERDICT_POST_EXPOSURE_SUPPORT_FAILURE",
        "scientific_authority": False,
        "submission_authority": False,
        "authority": {
            "current_R18_execution": False,
            "new_experiment": False,
            "claim_expansion": False,
            "l3": False,
            "threshold_change": False,
            "submission": False,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--r15", type=Path, required=True)
    p.add_argument("--r16", type=Path, required=True)
    p.add_argument("--run-root", type=Path, required=True)
    p.add_argument("--alias-tags-json", type=Path, required=True)
    p.add_argument(
        "--output",
        type=Path,
        default=Path("generated/d2-failure-memory-provenance-l2b-r18c-post-exposure-adjudication.json"),
    )
    args = p.parse_args()
    r15 = load_bound(args.r15, EXPECTED_R15_SHA, "R15")
    r16 = load_bound(args.r16, EXPECTED_R16_SHA, "R16")
    aliases = json.loads(args.alias_tags_json.read_text(encoding="utf-8"))
    receipt = build_receipt(r15, r16, args.run_root, aliases)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "scientific_exposure": receipt["failure"]["scientific_exposure_occurred"],
        "retry_current": receipt["frozen_policy_application"]["retry_sequence_0_under_R16"],
        "continue_current": receipt["adjudication"]["continue_current_144_episode_schedule"],
        "verdict": receipt["scientific_verdict"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
