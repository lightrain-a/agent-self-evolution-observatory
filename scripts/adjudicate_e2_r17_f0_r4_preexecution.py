#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "generated/e2-r17-f0-r4-frozen-candidate-contract-20260828.json"
PILOT = ROOT / "generated/e2-r17-e0-pilot-manifest-20260828.json"
IDENTITY = ROOT / "generated/e2-r17-current-plan-model-identity-adjudication-20260828.json"
SUITE_QUAL = ROOT / "generated/e2-r17-controlled-suite-v2-mindmemos-qualification-20260827.json"
UPDATER_QUAL = ROOT / "generated/e2-r17-cloned-state-first-party-updater-qualification-20260828.json"
ACTOR_SMOKE = ROOT / "generated/e2-r17-actor-protocol-smoke-20260828.json"
ROUND_ROOT = ROOT / "generated/e2-r17-f0-r4-preexecution-review-20260828"
RUNTIME_RECEIPT = ROOT / "generated/e2-r17-runtime-dependency-qualification-20260828.json"
ADDENDUM = ROOT / "generated/e2-r17-f0-r4-execution-policy-addendum-20260828.json"
ADJUDICATION = ROOT / "generated/e2-r17-f0-r4-preexecution-adjudication-20260828.json"
AUTHORIZATION = ROOT / "generated/e2-r17-e0-pilot-authorization-20260828.json"
REQUESTED_MODELS = ("deepseek-v4-pro", "kimi-k3")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def reviews() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    round1: list[dict[str, Any]] = []
    round2: list[dict[str, Any]] = []
    for model in REQUESTED_MODELS:
        round1.append(load(ROUND_ROOT / "round1" / f"{model}.json"))
        round2.append(load(ROUND_ROOT / "round2" / f"{model}.json"))
    return round1, round2


def validate_inputs() -> dict[str, Any]:
    contract = load(CONTRACT)
    pilot = load(PILOT)
    identity = load(IDENTITY)
    suite = load(SUITE_QUAL)
    updater = load(UPDATER_QUAL)
    smoke = load(ACTOR_SMOKE)
    runtime = load(RUNTIME_RECEIPT)
    round1, round2 = reviews()
    contract_sha = sha256(CONTRACT)

    require(contract.get("status") == "CANDIDATE_REQUIRES_DUAL_PREEXECUTION_REVIEW", "candidate contract status drift")
    require(identity.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "model identity is not qualified")
    require(suite.get("status") == "PASS_ZERO_PROVIDER", "controlled suite is not qualified")
    require(updater.get("status") == "PASS_ZERO_PROVIDER", "updater is not qualified")
    require(smoke.get("status") == "COMPLETED", "actor protocol smoke is not completed")
    require(smoke.get("mode") == "protocol_smoke", "actor smoke mode drift")
    require(smoke.get("scientific_outcome") is False, "actor smoke was mislabeled as scientific outcome")
    require(smoke.get("k") == 1 and smoke.get("prefix_ks") == [1], "actor smoke K/prefix drift")
    require(len(smoke.get("tasks") or []) == 1, "actor smoke must contain exactly one development task")
    require(smoke.get("provider_retry_limit") == 0, "actor smoke provider retry drift")
    require(smoke.get("thinking") == "disabled", "actor smoke thinking drift")
    require(runtime.get("status") == "PASS_ZERO_PROVIDER", "runtime dependency qualification is not passing")
    require(pilot.get("status") == "FROZEN_PRE_OUTCOME", "pilot manifest is not frozen pre-outcome")
    task_ids = [str(value) for value in pilot.get("pilot_task_ids") or []]
    require(len(task_ids) == 12 and len(set(task_ids)) == 12, "pilot manifest must contain 12 unique tasks")
    require(task_ids == [str(value) for value in contract["data"]["e0_pilot"]], "contract and pilot task order differ")
    require(pilot.get("model_outcomes_accessed") is False, "pilot selection accessed model outcomes")
    require(pilot.get("selection_is_outcome_blind") is True, "pilot selection is not outcome blind")

    expected_resolved = {
        model: str(identity["requested_and_resolved"][model]["resolved"])
        for model in REQUESTED_MODELS
    }
    require(len(set(expected_resolved.values())) == 2, "reviewer identities are not distinct")
    for round_number, rows in ((1, round1), (2, round2)):
        require(len(rows) == 2, f"round {round_number} is incomplete")
        for row in rows:
            model = str(row.get("requested_model") or "")
            require(model in expected_resolved, f"unknown reviewer model in round {round_number}")
            require(row.get("status") == "COMPLETED", f"round {round_number} review incomplete for {model}")
            require(row.get("parse_valid") is True, f"round {round_number} review schema invalid for {model}")
            require(row.get("provider_retry_limit") == 0, f"round {round_number} provider retry drift")
            require(row.get("hidden_provider_retry_used") is False, f"round {round_number} hidden retry")
            require(row.get("resolved_model") == expected_resolved[model], f"round {round_number} resolved identity drift")
            require(row.get("contract_sha256") == contract_sha, f"round {round_number} contract hash drift")
            require((row.get("review") or {}).get("contract_sha256_acknowledged") == contract_sha, "review did not acknowledge exact contract")
    require(all((row.get("review") or {}).get("verdict") == "GO" for row in round1), "blind reviews did not both return GO")
    require(all((row.get("review") or {}).get("e0_pilot_recommendation") == "GO" for row in round1), "blind reviews did not both recommend E0 GO")
    require(all((row.get("review") or {}).get("final_verdict") == "GO" for row in round2), "cross reviews did not both return GO")
    require(all((row.get("review") or {}).get("e0_pilot_authorization_recommendation") == "GO" for row in round2), "cross reviews did not both recommend E0 GO")
    require(all((row.get("review") or {}).get("e1_authorization_recommendation") == "HOLD_UNTIL_E0" for row in round2), "E1 is not held until E0")
    require(all((row.get("review") or {}).get("paper_claim_authority") is False for row in round2), "review accidentally grants paper claim authority")

    return {
        "contract": contract,
        "contract_sha": contract_sha,
        "pilot": pilot,
        "pilot_task_ids": task_ids,
        "identity": identity,
        "suite": suite,
        "updater": updater,
        "smoke": smoke,
        "runtime": runtime,
        "round1": round1,
        "round2": round2,
        "expected_resolved": expected_resolved,
    }


def write_addendum(state: dict[str, Any]) -> None:
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-f0-r4-execution-policy-addendum",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "FROZEN_NONSCIENTIFIC_EXECUTION_POLICY",
        "contract_path": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": state["contract_sha"],
        "role": "Clarifies runtime accounting and launch scope without changing the scientific object, estimand, task split, arms, hypotheses, or decision thresholds in the reviewed contract.",
        "scientific_contract_mutated": False,
        "review_sources": [
            {
                "path": str((ROUND_ROOT / f"round{round_number}" / f"{model}.json").relative_to(ROOT)),
                "sha256": sha256(ROUND_ROOT / f"round{round_number}" / f"{model}.json"),
                "round": round_number,
                "requested_model": model,
            }
            for round_number in (1, 2)
            for model in REQUESTED_MODELS
        ],
        "e0_protocol_failure_definition": [
            "any task outside the exact 12-task authorization allowlist or any outcome-driven replacement",
            "suite, split, initial-skill, MindMemOS, identity, authorization, or authorized-code hash drift",
            "non-Plan route, provider retry above zero, thinking not disabled, temperature drift, or resolved-model drift",
            "missing, duplicated, technically incomplete, or non-content-addressed rollout among indices 0..7",
            "case setup, tool execution, evaluator, workbook, provider-response, or trajectory serialization exception",
            "within-pool mismatch in task, input, prompt, initial skill, verifier, requested model, or resolved model",
            "failure to derive K=1/2/4/8 from exact prefixes of the one generated K=8 pool",
            "missing provider receipt, unhashed raw provider response identifier, or credential material in a public artifact",
            "summary task order, K, prefix, contract, authorization, or model identity mismatch",
        ],
        "e0_rescue_definition": "At K=8, rollout-0 has deterministic verifier score 0 and at least one rollout in the same exact pool has score 1; equivalently precommitted_success=0 and acting_success=1.",
        "e0_stop_and_extension": {
            "stop": "STOP the tranche on any protocol failure or zero K=8 rescue events across all 12 pilot tasks.",
            "extension": "Only when the 12-task pilot completes with at least one rescue event may the predeclared remaining 42 E0-calibration tasks be considered; a separate post-pilot adjudication is required before E0-full.",
            "no_task_replacement": True,
            "resume": "Resume only missing rollout units whose content-addressed receipt is absent; never rerun a completed unit for a better outcome.",
        },
        "random_nonwinner_semantics": {
            "candidate_set": "all trajectories in the exact pool except the acting winner, regardless of whether a nonwinner has score 0 or a tied score 1",
            "selection": "index SHA256(randomization_salt|pool_id) modulo candidate count",
            "salt": "e2-r17-r4-random-nonwinner-v1",
            "interpretation": "generic within-pool diversity control, not a rejected-failure control",
            "implementation_path": "research_pipeline/e2_r17_search_projection_runner.py",
            "implementation_sha256": sha256(ROOT / "research_pipeline/e2_r17_search_projection_runner.py"),
        },
        "future_e1_accounting_frozen_before_e0_outcomes": {
            "empty_or_unchanged_skill": "A completed first-party updater call that mints the required version but leaves SKILL.md content unchanged is a valid zero-effect scientific outcome, not a protocol failure.",
            "no_version_or_incomplete_batch": "Failure to mint exactly one version from exactly eight consumed task packets is a protocol failure and cannot be reclassified as a null scientific result.",
            "parser_or_validation_events": "Every parse error, corrective attempt, validation rejection, truncation, failed packet rendering, and updater call is logged in the arm receipt; retry remains zero at the provider layer.",
            "pairwise_reporting": [
                "Rejected-Witness minus Winner-only",
                "Rejected-Witness minus Duplicated-Winner",
                "Rejected-Witness minus Random-Nonwinner",
                "SkillCAT-style contrast minus Winner-only",
                "Precommitted rollout-0 minus Winner-only",
                "all remaining preregistered arm pairs as descriptive estimates",
            ],
        },
        "authority": {
            "scientific_experiment": False,
            "gpu": False,
            "e0_pilot": False,
            "e0_full": False,
            "e1": False,
            "public_externality": False,
            "paper_promotion": False,
            "front_end_claim": False,
            "submission": False,
        },
        "private_credentials_included": False,
        "raw_response_ids_included": False,
    }
    atomic_json(ADDENDUM, payload)


def review_ledger(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for round_number, reviews_for_round in ((1, state["round1"]), (2, state["round2"])):
        for row in reviews_for_round:
            model = str(row["requested_model"])
            path = ROUND_ROOT / f"round{round_number}" / f"{model}.json"
            rows.append(
                {
                    "round": round_number,
                    "requested_model": model,
                    "resolved_model": row["resolved_model"],
                    "status": row["status"],
                    "verdict": (row["review"] or {}).get("verdict" if round_number == 1 else "final_verdict"),
                    "prompt_sha256": row["prompt_sha256"],
                    "response_sha256": row["raw_text_sha256"],
                    "artifact_path": str(path.relative_to(ROOT)),
                    "artifact_sha256": sha256(path),
                    "input_tokens": int((row.get("usage") or {}).get("input_tokens") or 0),
                    "output_tokens": int((row.get("usage") or {}).get("output_tokens") or 0),
                    "total_tokens": int((row.get("usage") or {}).get("total_tokens") or 0),
                    "independent": bool(row.get("independent")),
                    "exposed_to_other_review": bool(row.get("exposed_to_other_review")),
                    "provider_retry_limit": row.get("provider_retry_limit"),
                    "hidden_provider_retry_used": row.get("hidden_provider_retry_used"),
                }
            )
    return rows


def write_adjudication(state: dict[str, Any]) -> None:
    ledger = review_ledger(state)
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-f0-r4-dual-preexecution-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "DUAL_REVIEW_PASS_E0_ONLY",
        "branch": git("branch", "--show-current"),
        "head_before_adjudication": git("rev-parse", "HEAD"),
        "contract_path": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": state["contract_sha"],
        "pilot_manifest_path": str(PILOT.relative_to(ROOT)),
        "pilot_manifest_sha256": sha256(PILOT),
        "execution_addendum_path": str(ADDENDUM.relative_to(ROOT)),
        "execution_addendum_sha256": sha256(ADDENDUM),
        "review_ledger": ledger,
        "token_ledger": {
            "calls": len(ledger),
            "input_tokens": sum(row["input_tokens"] for row in ledger),
            "output_tokens": sum(row["output_tokens"] for row in ledger),
            "total_tokens": sum(row["total_tokens"] for row in ledger),
        },
        "checks": {
            "round1_blind_two_of_two_go": True,
            "round2_cross_exposed_two_of_two_go": True,
            "exact_contract_acknowledged": True,
            "distinct_resolved_reviewer_identities": True,
            "route_is_ark_plan": True,
            "provider_retry_zero": True,
            "no_hidden_retry": True,
            "experiment_identifiable": True,
            "main_claim_falsifiable": True,
            "strongest_simpler_explanations_controlled": True,
            "blocking_collision_present": False,
            "pilot_manifest_pre_outcome": True,
            "controlled_suite_qualified": True,
            "actor_smoke_pass": True,
            "updater_zero_provider_qualification_pass": True,
            "runtime_dependency_qualification_pass": True,
        },
        "decision": {
            "e0_pilot": "GO_TO_EXACT_AUTHORIZATION",
            "e0_full": "HOLD_UNTIL_PILOT_ANALYSIS",
            "e1": "HOLD_UNTIL_E0_SUPPORT_AND_INTEGRITY",
            "public_datasets": "HOLD_UNTIL_IDENTIFICATION_AND_PREDICTION",
            "paper_claim": "HOLD",
            "front_end_claim": "HOLD",
            "submission": "HOLD",
        },
        "authority": {
            "write_exact_e0_authorization": True,
            "scientific_experiment": False,
            "gpu": False,
            "e0_pilot": False,
            "e0_full": False,
            "e1": False,
            "public_externality": False,
            "paper_promotion": False,
            "front_end_claim": False,
            "submission": False,
        },
        "private_credentials_included": False,
        "raw_response_ids_included": False,
    }
    atomic_json(ADJUDICATION, payload)


def code_hashes() -> dict[str, str]:
    paths = (
        "research_pipeline/e2_r17_actor_pool.py",
        "research_pipeline/e2_r17_ark_plan_react.py",
        "research_pipeline/e2_r17_search_projection_runner.py",
        "scripts/run_e2_r17_actor_pool.py",
        "scripts/launch_e2_r17_e0_pilot.py",
    )
    return {rel: sha256(ROOT / rel) for rel in paths}


def write_authorization(state: dict[str, Any]) -> None:
    require(ADJUDICATION.exists() and ADDENDUM.exists(), "adjudication/addendum missing")
    adjudication = load(ADJUDICATION)
    require(adjudication.get("status") == "DUAL_REVIEW_PASS_E0_ONLY", "adjudication does not permit authorization")
    require(not git("status", "--porcelain"), "authorization must be generated from a clean committed worktree")
    commit = git("rev-parse", "HEAD")
    identity = state["identity"]
    deepseek = identity["requested_and_resolved"]["deepseek-v4-pro"]
    suite_root = Path(state["contract"]["data"]["suite_root"])
    run_root = Path("/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-20260828")
    summary_path = run_root / "e0_pilot_summary.json"
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-e0-pilot-exact-authorization",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "AUTHORIZED_E0",
        "authorized_mode": "e0",
        "contract_path": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": state["contract_sha"],
        "preexecution_adjudication_path": str(ADJUDICATION.relative_to(ROOT)),
        "preexecution_adjudication_sha256": sha256(ADJUDICATION),
        "execution_addendum_path": str(ADDENDUM.relative_to(ROOT)),
        "execution_addendum_sha256": sha256(ADDENDUM),
        "pilot_manifest_path": str(PILOT.relative_to(ROOT)),
        "pilot_manifest_sha256": sha256(PILOT),
        "research_git_commit": commit,
        "research_branch": git("branch", "--show-current"),
        "code_sha256": code_hashes(),
        "suite_root": str(suite_root),
        "suite_manifest_sha256": sha256(suite_root / "suite_manifest.json"),
        "split_manifest_sha256": sha256(suite_root / "r17_split_manifest.json"),
        "mindmemos_root": state["contract"]["substrate"]["root"],
        "mindmemos_commit": state["contract"]["substrate"]["commit"],
        "skill_source": str(Path(state["contract"]["substrate"]["initial_skill"]["path"]).parent),
        "skill_pre_sha256": state["contract"]["substrate"]["initial_skill"]["sha256"],
        "identity_path": str(IDENTITY),
        "identity_sha256": sha256(IDENTITY),
        "requested_model": str(deepseek["requested"]),
        "resolved_model": str(deepseek["resolved"]),
        "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
        "provider_retry_limit": 0,
        "thinking": "disabled",
        "temperature": 0,
        "authorized_task_ids": state["pilot_task_ids"],
        "k": 8,
        "prefix_ks": [1, 2, 4, 8],
        "max_turns": 10,
        "max_output_tokens": 4096,
        "concurrency": 4,
        "run_root": str(run_root),
        "summary_path": str(summary_path),
        "runtime_pydeps": state["runtime"]["runtime_pydeps"],
        "runtime_receipt_path": str(RUNTIME_RECEIPT.relative_to(ROOT)),
        "runtime_receipt_sha256": sha256(RUNTIME_RECEIPT),
        "resume_missing_units_only": True,
        "stop_on_any_protocol_failure": True,
        "stop_on_zero_rescue_events": True,
        "allow_task_replacement": False,
        "allow_e0_full_extension": False,
        "allow_e1": False,
        "allow_public_dataset": False,
        "authority": {
            "scientific_experiment": True,
            "gpu": False,
            "e0_pilot": True,
            "e0_full": False,
            "e1": False,
            "public_externality": False,
            "paper_promotion": False,
            "front_end_claim": False,
            "submission": False,
        },
        "private_credentials_included": False,
        "raw_response_ids_included": False,
    }
    payload["body_sha256"] = canonical_sha(payload)
    atomic_json(AUTHORIZATION, payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorize", action="store_true")
    args = parser.parse_args()
    state = validate_inputs()
    if args.authorize:
        # Authorization must be emitted from the already reviewed, committed,
        # clean preexecution state. Rewriting timestamped adjudication assets
        # here would self-contaminate that clean-state check.
        require(ADDENDUM.exists(), "committed execution addendum is missing")
        require(ADJUDICATION.exists(), "committed preexecution adjudication is missing")
        require(load(ADDENDUM).get("status") == "FROZEN_NONSCIENTIFIC_EXECUTION_POLICY", "execution addendum status drift")
        require(load(ADJUDICATION).get("status") == "DUAL_REVIEW_PASS_E0_ONLY", "preexecution adjudication status drift")
        write_authorization(state)
    else:
        write_addendum(state)
        write_adjudication(state)
    print(
        json.dumps(
            {
                "status": "AUTHORIZED_E0" if args.authorize else "DUAL_REVIEW_PASS_E0_ONLY",
                "contract_sha256": state["contract_sha"],
                "addendum_sha256": sha256(ADDENDUM),
                "adjudication_sha256": sha256(ADJUDICATION),
                "authorization_sha256": sha256(AUTHORIZATION) if args.authorize else None,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
