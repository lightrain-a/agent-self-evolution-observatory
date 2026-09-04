#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

LEGACY_COMMIT = "f400a9e218c869a447110f3e3e00de6449550985"
LEGACY_RUNNER_PATH = "paper_drafts/c1-proxy-reward-stanford-r3-20260824/run_b10_native_first_action_transport.py"
EXPECTED_LEGACY_RUNNER_SHA256 = "87214f92c2a11ea9ff139535ca6d7d272680ec5ed7da8b86880475bbb66cb98a"
EXPECTED_CONTRACT_SHA256 = "c2a54c928d74ccb7a153166a02ef0ef7a1504a93b5895952380a95b0277a3436"
EXPECTED_RESULT_SHA256 = "e779c19a6a73bdb4b551f0739453a014fe9fc3cafc17cb4fbaa8b70a5137d8e6"
EXPECTED_CONTRACT_PAYLOAD_SHA256 = "a6983c0fe46c649a187bc60954614dfc489b2de903928a452cf0494034b0b3c5"
EXPECTED_STATES = 36
EXPECTED_N = 4
EXPECTED_CONDITIONS = ["success_memory", "failure_memory", "no_memory"]
EXPECTED_TOTAL = 432
PERMUTATION_SEED = 20260824
PERMUTATION_REPETITIONS = 100000
EXPECTED_TV_FULL = 0.06944444444444445
EXPECTED_P_FULL = 0.5800941990580094


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def extract_json_object(text: str) -> dict[str, Any]:
    # Exact historical helper semantics from research_pipeline/ark_provider.py at LEGACY_COMMIT.
    candidate = text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
    start, end = candidate.find("{"), candidate.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("model output contains no JSON object")
    payload = json.loads(candidate[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("model JSON output is not an object")
    return payload


def action_signature(payload: dict[str, Any]) -> str:
    # Exact historical B10 normalization semantics.
    current = payload.get("current_state") or {}
    actions = payload.get("action") or (current.get("action") if isinstance(current, dict) else None) or []
    if not actions or not isinstance(actions[0], dict):
        return "NO_ACTION"
    action = actions[0]
    name = next(iter(action), "UNKNOWN")
    args = action.get(name) or {}
    if name == "click_element" and isinstance(args, dict):
        return f"click_element:{args.get('index')}"
    return name


def parse_output(text: str) -> tuple[str, str, bool]:
    # Exact historical B10 strict-then-regex recovery semantics.
    try:
        payload = extract_json_object(text)
        sig = action_signature(payload)
        cur = payload.get("current_state") or {}
        goal = str(cur.get("next_goal") or "") if isinstance(cur, dict) else ""
        return sig, goal, False
    except Exception as strict_error:
        match = re.search(r'"action"\s*:\s*\[\s*\{\s*"([^"]+)"\s*:\s*\{(.*?)\}\s*\}\s*\]', text, re.DOTALL)
        if not match:
            raise strict_error
        name = match.group(1)
        body = match.group(2)
        if name == "click_element":
            ix = re.search(r'"index"\s*:\s*(\d+)', body)
            if not ix:
                raise strict_error
            sig = f"click_element:{ix.group(1)}"
        else:
            sig = name
        goal_match = re.search(r'"next_goal"\s*:\s*"((?:\\.|[^"\\])*)"', text, re.DOTALL)
        goal = ""
        if goal_match:
            try:
                goal = json.loads('"' + goal_match.group(1) + '"')
            except Exception:
                goal = goal_match.group(1)
        return sig, goal, True


def tv(a: list[str], b: list[str]) -> float:
    ca, cb = Counter(a), Counter(b)
    keys = set(ca) | set(cb)
    na, nb = max(1, len(a)), max(1, len(b))
    return 0.5 * sum(abs(ca[k] / na - cb[k] / nb) for k in keys)


def mode(values: list[str]) -> str:
    if not values:
        return ""
    counts = Counter(values)
    maximum = max(counts.values())
    return sorted(key for key, count in counts.items() if count == maximum)[0]


def permutation_p(cells: list[dict[str, Any]], observed: float) -> float:
    pools = [cell["success"] + cell["failure"] for cell in cells]
    rng = random.Random(PERMUTATION_SEED)
    greater_equal = 0
    for _ in range(PERMUTATION_REPETITIONS):
        values = []
        for pool in pools:
            shuffled = list(pool)
            rng.shuffle(shuffled)
            values.append(tv(shuffled[:EXPECTED_N], shuffled[EXPECTED_N:]))
        if sum(values) / len(values) >= observed - 1e-12:
            greater_equal += 1
    return (greater_equal + 1) / (PERMUTATION_REPETITIONS + 1)


def git_blob(repo_root: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo_root), "show", f"{commit}:{path}"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Zero-provider raw replay qualification for historical C1 B10 first-action evidence.")
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    run_root = args.run_root.resolve()
    contract_path = run_root / "b10-contract.json"
    result_path = run_root / "b10-result.json"
    private_root = run_root / "private"
    stages_root = private_root / "stages"
    raw_root = private_root / "raw"
    provider_root = private_root / "provider-responses"

    require(contract_path.is_file(), "missing B10 contract")
    require(result_path.is_file(), "missing B10 result")
    require(sha(contract_path) == EXPECTED_CONTRACT_SHA256, "B10 contract SHA drift")
    require(sha(result_path) == EXPECTED_RESULT_SHA256, "B10 result SHA drift")

    historical_runner = git_blob(repo_root, LEGACY_COMMIT, LEGACY_RUNNER_PATH)
    require(sha_bytes(historical_runner) == EXPECTED_LEGACY_RUNNER_SHA256, "historical B10 runner SHA drift")

    contract = load(contract_path)
    result = load(result_path)
    require(contract.get("contract_sha256") == EXPECTED_CONTRACT_PAYLOAD_SHA256, "B10 contract payload SHA drift")
    require(contract.get("future_task_count") == EXPECTED_STATES, "state-count drift")
    require(contract.get("conditions") == EXPECTED_CONDITIONS, "condition drift")
    require(contract.get("rollouts_per_task_per_condition") == EXPECTED_N, "rollout-count drift")
    require(contract.get("expected_provider_calls") == EXPECTED_TOTAL, "provider-call geometry drift")
    require((contract.get("code") or {}).get("runner", {}).get("sha256") == EXPECTED_LEGACY_RUNNER_SHA256, "contract runner binding drift")
    gate = contract.get("primary_gate") or {}
    require(gate.get("permutation_seed") == PERMUTATION_SEED, "permutation seed drift")
    require(gate.get("permutation_repetitions") == PERMUTATION_REPETITIONS, "permutation repetitions drift")
    require(result.get("status") == "B10_EXECUTION_COMPLETE", "historical B10 result incomplete")

    stage_paths = sorted(stages_root.glob("*.json"))
    provider_paths = sorted(provider_root.glob("*.json"))
    raw_paths = sorted(raw_root.glob("*/*.txt"))
    require(len(stage_paths) == EXPECTED_TOTAL, f"expected {EXPECTED_TOTAL} stage records, found {len(stage_paths)}")
    require(len(provider_paths) == EXPECTED_TOTAL, f"expected {EXPECTED_TOTAL} provider-response records, found {len(provider_paths)}")
    require(len(raw_paths) == EXPECTED_TOTAL, f"expected {EXPECTED_TOTAL} raw response objects, found {len(raw_paths)}")

    by_state: dict[int, dict[str, list[tuple[int, str]]]] = defaultdict(lambda: defaultdict(list))
    normalized_mismatches: list[str] = []
    recovered_count = 0
    raw_hash_mismatches: list[str] = []
    stage_ids: set[str] = set()

    for stage_path in stage_paths:
        row = load(stage_path)
        require(row.get("status") == "complete", f"non-complete historical stage: {stage_path.name}")
        stage_id = str(row.get("stage") or "")
        require(stage_id and stage_id not in stage_ids, f"duplicate/missing stage id: {stage_path.name}")
        stage_ids.add(stage_id)
        raw_hash = str(row.get("raw_sha256") or "")
        raw_path = raw_root / raw_hash[:2] / f"{raw_hash}.txt"
        require(raw_path.is_file(), f"missing raw response for {stage_id}")
        raw_bytes = raw_path.read_bytes()
        if sha_bytes(raw_bytes) != raw_hash:
            raw_hash_mismatches.append(stage_id)
            continue
        parsed_sig, _, recovered = parse_output(raw_bytes.decode("utf-8"))
        stored_sig = str(row.get("action_signature") or "")
        if parsed_sig != stored_sig:
            normalized_mismatches.append(stage_id)
        recovered_count += int(recovered)
        state = int(row["future_task"])
        condition = str(row["condition"])
        rollout = int(row["rollout"])
        require(condition in EXPECTED_CONDITIONS, f"unexpected condition: {condition}")
        by_state[state][condition].append((rollout, stored_sig))

    require(not raw_hash_mismatches, f"raw SHA mismatches: {raw_hash_mismatches[:5]}")
    require(not normalized_mismatches, f"raw-to-normalized action mismatches: {normalized_mismatches[:5]}")
    require(len(by_state) == EXPECTED_STATES, f"expected {EXPECTED_STATES} states, found {len(by_state)}")

    cells: list[dict[str, Any]] = []
    for unit in contract.get("task_units") or []:
        state = int(unit["future_task"])
        groups: dict[str, list[str]] = {}
        for condition in EXPECTED_CONDITIONS:
            values = sorted(by_state[state][condition], key=lambda item: item[0])
            require([rollout for rollout, _ in values] == [1, 2, 3, 4], f"rollout geometry drift: {state}/{condition}")
            groups[condition] = [signature for _, signature in values]
        cells.append(
            {
                "future_task": state,
                "success": groups["success_memory"],
                "failure": groups["failure_memory"],
                "no_memory": groups["no_memory"],
            }
        )

    result_cells = {int(cell["future_task"]): cell for cell in result.get("cell_results") or []}
    require(len(result_cells) == EXPECTED_STATES, "result cell geometry drift")
    for cell in cells:
        historical = result_cells[cell["future_task"]]
        require(cell["success"] == historical.get("success"), f"success normalized record drift: {cell['future_task']}")
        require(cell["failure"] == historical.get("failure"), f"failure normalized record drift: {cell['future_task']}")
        require(cell["no_memory"] == historical.get("no_memory"), f"no-memory normalized record drift: {cell['future_task']}")
        require(abs(tv(cell["success"], cell["failure"]) - float(historical["success_failure_tv"])) < 1e-12, f"cell TV drift: {cell['future_task']}")

    observed_tv = sum(tv(cell["success"], cell["failure"]) for cell in cells) / len(cells)
    modal_changes = sum(mode(cell["success"]) != mode(cell["failure"]) for cell in cells)
    p_value = permutation_p(cells, observed_tv)

    require(abs(observed_tv - EXPECTED_TV_FULL) < 1e-15, f"mean TV replay mismatch: {observed_tv}")
    require(abs(p_value - EXPECTED_P_FULL) < 1e-15, f"permutation replay mismatch: {p_value}")
    require(modal_changes == 0, f"modal replay mismatch: {modal_changes}/36")
    summary = result.get("summary") or {}
    require(abs(float(summary["observed_mean_success_failure_tv"]) - round(observed_tv, 6)) < 1e-12, "stored summary TV mismatch")
    require(abs(float(summary["permutation_p_ge_observed"]) - round(p_value, 6)) < 1e-12, "stored summary p mismatch")
    require((result.get("secondary") or {}).get("states_with_modal_success_failure_difference") == 0, "stored modal summary mismatch")

    receipt = {
        "schema_version": "1.0",
        "artifact_type": "c1-b10-first-action-raw-replay-qualification",
        "date": "2026-09-04",
        "status": "PASS_B10_FIRST_ACTION_RAW_REPLAY",
        "paper_id": result.get("paper_id"),
        "experiment_id": result.get("experiment_id"),
        "source_bindings": {
            "b10_contract": {"path": str(contract_path), "sha256": EXPECTED_CONTRACT_SHA256, "payload_sha256": EXPECTED_CONTRACT_PAYLOAD_SHA256},
            "b10_result": {"path": str(result_path), "sha256": EXPECTED_RESULT_SHA256},
            "legacy_runner": {"commit": LEGACY_COMMIT, "path": LEGACY_RUNNER_PATH, "sha256": EXPECTED_LEGACY_RUNNER_SHA256},
        },
        "geometry": {
            "matched_branch_comparison_states": EXPECTED_STATES,
            "conditions": EXPECTED_CONDITIONS,
            "draws_per_state_per_condition": EXPECTED_N,
            "total_provider_records_historical": EXPECTED_TOTAL,
            "success_failure_draws_per_state": "4+4",
            "scientific_unit": "matched frozen Shopping state; repeated calls are nested measurements",
        },
        "raw_provenance_replay": {
            "stage_records_verified": len(stage_paths),
            "provider_response_records_present": len(provider_paths),
            "content_addressed_raw_texts_verified": len(raw_paths),
            "raw_to_historical_action_signature_matches": EXPECTED_TOTAL,
            "strict_parser_fallback_recoveries": recovered_count,
            "normalizer_branch_label_aware": False,
            "normalizer_semantics": contract.get("action_signature"),
        },
        "replayed_historical_primary": {
            "mean_success_failure_tv_full_precision": observed_tv,
            "mean_success_failure_tv_reported": round(observed_tv, 6),
            "permutation_p_full_precision": p_value,
            "permutation_p_reported": round(p_value, 6),
            "modal_success_failure_changes": f"{modal_changes}/{EXPECTED_STATES}",
            "permutation_repetitions": PERMUTATION_REPETITIONS,
            "permutation_seed": PERMUTATION_SEED,
        },
        "design_consequence": {
            "historical_same_condition_repeated_decodes_exist": True,
            "existing_draws_enable_zero_provider_collision_mmd2_diagnostic": True,
            "new_provider_calls_are_not_automatically_required_for_stochasticity_diagnosis": True,
            "prospective_topup_requires_separate_precision_and_verdict_changing_gate": True,
        },
        "execution": {"new_provider_calls": 0, "new_gpu_runs": 0, "historical_records_read": EXPECTED_TOTAL},
        "authority": {"new_scientific_execution": False, "claim_expansion": False, "submission": False},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "replayed": receipt["replayed_historical_primary"], "geometry": receipt["geometry"], "new_provider_calls": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
