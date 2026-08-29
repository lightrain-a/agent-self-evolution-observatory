You are an independent adversarial reviewer for a post-run mechanical adjudicator repair in E2-R17 E1-A. You are blind to the other reviewer. You must NOT infer or request any mixed-pool/support result; those statistics have not been exposed to the operator before this repair. This review has zero E1-B, paper, frontend, or submission authority.

Reviewer endpoint: deepseek-v4-pro
Exact repair artifact SHA-256: e632988b3ebf39588caaaa7b9b425b869e6d06656353506ef0c8782b5ca33d50

The frozen E1-A run has completed its predeclared 12 streams / 768 rollout refs with zero technical failures. The first invocation of the independently bound support adjudicator stopped before support computation because its precondition used `int(summary.get('updater_calls') or -1) == 0`. In Python, legitimate integer 0 is falsy, so this maps 0 to -1 and rejects a valid zero-updater summary. No mixed/exposed/family support value was read before deciding the repair.

A new versioned adjudicator is proposed. Its diff against the original must be exactly one semantic line: explicit `is not None` plus `int(summary['updater_calls']) == 0`. The original file remains untouched. Audit the bound repair JSON and both source files.

Questions:
1. Is the diagnosed Python falsy-zero bug real and sufficient to explain the precondition failure without consulting support outcomes?
2. Is the repaired file's only difference the zero-updater parsing line? Confirm that mixed-pool recomputation, per-stream exposure, family support, thresholds, trajectory SHA validation, PASS/STOP status, and authority logic are byte/semantically unchanged otherwise.
3. Because this repair occurs after pool generation, is it acceptably outcome-independent given that no support values were inspected and the repair cannot change any support statistic or threshold? Flag any plausible p-hacking path.
4. Does accepting explicit zero while rejecting missing/nonzero updater_calls preserve the intended E1-A no-updater invariant?
5. May this repaired adjudicator be run once on the already-frozen E1-A summary/pools solely to produce the predeclared support PASS/STOP decision? Even on PASS, E1-B must remain HOLD pending a separate immutable contract/review.

Return exactly one JSON object and no markdown using this schema:
{
  "repair_sha256_acknowledged": "",
  "verdict": "PASS_TO_REPAIRED_SUPPORT_ADJUDICATION|REVISE_REPAIR|STOP",
  "zero_parse_bug_assessment": "",
  "delta_scope_assessment": "",
  "post_outcome_selection_risk_assessment": "",
  "support_logic_unchanged_assessment": "",
  "authority_boundary_assessment": "",
  "remaining_blockers": [
    {
      "priority": "P0|P1",
      "issue": "",
      "why_blocking": "",
      "exact_repair": ""
    }
  ],
  "nonblocking_notes": [
    ""
  ],
  "mechanical_pilot_recommendation": "HOLD|STOP",
  "provider_runtime_pilot_recommendation": "HOLD|STOP",
  "e1_a_recommendation": "ALLOW_REPAIRED_SUPPORT_ADJUDICATION_ONLY|HOLD|STOP",
  "e1_b_recommendation": "HOLD|STOP",
  "paper_claim_authority": false,
  "single_sentence_verdict": ""
}

Set `repair_sha256_acknowledged` exactly to the SHA above. PASS only if there is no P0/P1 blocker. Use verdict `PASS_TO_REPAIRED_SUPPORT_ADJUDICATION` and e1_a_recommendation `ALLOW_REPAIRED_SUPPORT_ADJUDICATION_ONLY` for a PASS. Keep e1_b_recommendation=HOLD and paper_claim_authority=false.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START

===== BOUND ARTIFACT: repair_artifact | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-support-adjudicator-zero-parse-repair-20260828.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-e1-a-support-adjudicator-mechanical-repair",
  "date": "2026-08-28",
  "status": "REPAIR_PENDING_INDEPENDENT_PRE_ADJUDICATION_REVIEW",
  "trigger": {
    "failed_command_stage": "support adjudicator precondition validation",
    "error": "E1-A must contain zero updater calls",
    "diagnosis": "The original expression int(summary.get('updater_calls') or -1) maps the legitimate integer 0 to -1 because 0 is falsy in Python.",
    "support_statistics_exposed_to_operator_before_repair": false,
    "mixed_or_exposed_counts_read_before_repair": false,
    "thresholds_changed": false,
    "task_set_changed": false,
    "pool_set_changed": false
  },
  "frozen_run": {
    "contract_path": "generated/e2-r17-e1-a-pool-support-v2-1-contract-20260828.json",
    "contract_sha256": "f2919d201f03a0166d6255240378efd14d45bc7f8a3269bff5b78fcccb6d1d21",
    "authorization_path": "generated/e2-r17-e1-a-pool-support-v2-1-authorization-20260828.json",
    "authorization_sha256": "743836932a1aa08391ec7699f925097a17c01e94a0ad7d0470f25a367247d8dd",
    "run_root": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-1-20260828",
    "completed_streams": 12,
    "completed_rollout_refs": 768,
    "technical_failures": 0
  },
  "code_delta": {
    "original_path": "scripts/adjudicate_e2_r17_e1_a_pool_support.py",
    "original_sha256": "9972296dfc140a3cbd29bc6f475dddb46822353a1f9ae56b5f5b243c13b722ea",
    "repaired_path": "scripts/adjudicate_e2_r17_e1_a_pool_support_v2.py",
    "repaired_sha256": "cc5d43828179bbdcc932a3194140cb798ccfb9b6d60bda6a44090ae4983601a6",
    "only_change": "Replace `int(summary.get(\"updater_calls\") or -1) == 0` with an explicit non-None check followed by `int(summary[\"updater_calls\"]) == 0`.",
    "support_computation_logic_changed": false,
    "support_threshold_logic_changed": false,
    "pool_or_trajectory_validation_changed": false,
    "authority_logic_changed": false
  },
  "zero_outcome_tests": {
    "zero_value_accepted": true,
    "one_value_rejected": true,
    "missing_value_rejected": true,
    "module_import_help": "PASS"
  },
  "rule": "The repaired adjudicator may be used only after independent reviewers confirm that the one-line change is mechanical and cannot alter any support statistic or gate. No support value may be inspected before that review.",
  "authority": {
    "run_repaired_support_adjudicator": false,
    "execute_e1_b": false,
    "paper_promotion": false,
    "submission": false
  }
}


===== BOUND ARTIFACT: original_adjudicator | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/adjudicate_e2_r17_e1_a_pool_support.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    contract = load_json(args.contract)
    authorization = load_json(args.authorization)
    summary = load_json(args.summary)
    contract_sha = sha_file(args.contract)
    authorization_sha = sha_file(args.authorization)

    require(contract.get("status") == "FROZEN_E1_A_POOL_SUPPORT", "E1-A contract status invalid")
    require(authorization.get("status") == "AUTHORIZED_E1", "E1-A authorization status invalid")
    require(authorization.get("contract_sha256") == contract_sha, "authorization does not bind exact E1-A contract")
    require(summary.get("status") == "COMPLETED_ALL_96_POOLS_PENDING_SEPARATE_SUPPORT_ADJUDICATION", "E1-A pool freeze incomplete")
    require(summary.get("contract_sha256") == contract_sha, "summary contract SHA mismatch")
    require(summary.get("authorization_sha256") == authorization_sha, "summary authorization SHA mismatch")
    require(int(summary.get("streams") or 0) == 12, "E1-A stream cardinality invalid")
    require(int(summary.get("tasks") or 0) == 96, "E1-A task cardinality invalid")
    require(int(summary.get("actor_rollouts") or 0) == 768, "E1-A rollout cardinality invalid")
    require(int(summary.get("updater_calls") or -1) == 0, "E1-A must contain zero updater calls")
    require(summary.get("e1_b_authority") is False, "E1-A summary cannot inherit E1-B authority")

    support = summary.get("support") or {}
    stream_rows = support.get("stream_rows") or []
    require(len(stream_rows) == 12, "support summary must include 12 stream rows")
    mixed = int(support.get("mixed_pool_count") or 0)
    exposed = int(support.get("exposed_stream_count") or 0)
    supported_families = int(support.get("supported_families") or 0)
    thresholds = contract["support_gate"]
    min_mixed = int(thresholds["mixed_pool_count_minimum"])
    min_exposed = int(thresholds["exposed_stream_minimum"])
    min_per_stream = int(thresholds["mixed_pools_per_exposed_stream_minimum"])
    min_families = int(thresholds["supported_families_minimum"])

    run_root = Path(contract["run_root"])
    split = load_json(Path(contract["suite"]["root"]) / "r17_split_manifest.json")
    frozen_streams = list(contract["streams"])
    require(list(split["e1_update_streams"].keys()) == frozen_streams, "stream manifest drift")
    expected_tasks = [str(task) for stream_id in frozen_streams for task in split["e1_update_streams"][stream_id]]
    require(len(expected_tasks) == 96 and len(set(expected_tasks)) == 96, "frozen update set must contain 96 unique tasks")
    task_to_stream = {
        str(task): stream_id
        for stream_id in frozen_streams
        for task in split["e1_update_streams"][stream_id]
    }
    metadata_rows = load_json(Path(contract["suite"]["root"]) / "r17_controlled_metadata.json")
    metadata = {str(row["id"]): row for row in metadata_rows}

    pool_sha: dict[str, str] = {}
    mixed_recomputed = 0
    per_stream_mixed = {stream_id: 0 for stream_id in frozen_streams}
    per_family_mixed: dict[str, int] = {}
    for task_id in expected_tasks:
        pool_path = run_root / "cases" / task_id / "pool_k8.json"
        require(pool_path.exists(), f"missing frozen K8 pool: {task_id}")
        pool = load_json(pool_path)
        require(pool.get("task_id") == task_id and int(pool.get("k") or 0) == 8, f"invalid K8 pool identity: {task_id}")
        trajectories = pool.get("trajectories") or []
        require(len(trajectories) == 8, f"K8 pool missing trajectory refs: {task_id}")
        scores = [float(row["score"]) for row in trajectories]
        is_mixed = int(min(scores) < 1.0 and max(scores) >= 1.0)
        mixed_recomputed += is_mixed
        per_stream_mixed[task_to_stream[task_id]] += is_mixed
        family = str(metadata[task_id]["primary_failure_family"])
        per_family_mixed[family] = per_family_mixed.get(family, 0) + is_mixed
        for row in trajectories:
            trajectory = Path(row["trajectory_path"])
            require(trajectory.exists() and sha_file(trajectory) == row["trajectory_sha256"], f"trajectory SHA drift: {task_id}/{row['rollout_index']}")
        pool_sha[task_id] = sha_file(pool_path)
    require(mixed_recomputed == mixed, "mixed-pool total does not recompute from exact frozen pools")
    exposed_recomputed = sum(int(value >= min_per_stream) for value in per_stream_mixed.values())
    require(exposed_recomputed == exposed, "exposed-stream count does not recompute directly from exact frozen pools")
    supported_families_recomputed = sum(int(value > 0) for value in per_family_mixed.values())
    require(supported_families_recomputed == supported_families, "supported-family count does not recompute directly from exact frozen pools")
    summary_stream_map = {str(row["stream_id"]): int(row["mixed_pools"]) for row in stream_rows}
    require(summary_stream_map == per_stream_mixed, "summary per-stream mixed counts drift from exact frozen pools")
    require(dict(sorted((support.get("family_mixed_counts") or {}).items())) == dict(sorted(per_family_mixed.items())), "summary family mixed counts drift from exact frozen pools")
    require(bool(support.get("primary_hard_gate_pass")) == (mixed >= min_mixed and exposed >= min_exposed), "hard-gate flag is inconsistent")
    require(bool(support.get("family_generalization_gate_pass")) == (supported_families >= min_families), "family gate flag is inconsistent")

    hard_pass = mixed >= min_mixed and exposed >= min_exposed
    family_pass = supported_families >= min_families
    status = "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT" if hard_pass else "STOP_E1_SUPPORT_INSUFFICIENT"
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-e1-a-pool-support-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "summary_path": str(args.summary),
        "summary_sha256": sha_file(args.summary),
        "integrity": {
            "streams": 12,
            "tasks": 96,
            "actor_rollouts": 768,
            "frozen_k8_pools": 96,
            "all_trajectory_shas_revalidated": True,
            "task_replacement_after_support_observation": False,
            "waiver_or_rounding": False,
            "updater_calls": 0,
        },
        "primary_support": {
            "mixed_pools": mixed,
            "required_mixed_pools": min_mixed,
            "exposed_streams": exposed,
            "required_exposed_streams": min_exposed,
            "mixed_per_exposed_stream": min_per_stream,
            "per_stream_mixed_recomputed": per_stream_mixed,
            "pass": hard_pass,
        },
        "family_generalization": {
            "supported_families": supported_families,
            "required_supported_families": min_families,
            "pass": family_pass,
            "per_family_mixed_recomputed": dict(sorted(per_family_mixed.items())),
            "controls_primary_e1_b_authorization": False,
            "claim_if_failed": "Block family-generalization and prospective family-ranking claims; pooled E1-B may still be contracted only if primary support passes."
        },
        "pool_sha256": pool_sha,
        "interpretation": (
            "This adjudication evaluates only pre-treatment mixed-pool support and protocol integrity. "
            "It does not evaluate MRW, WIN, RB-AGG, future skill utility, or paper effectiveness."
        ),
        "authority": {
            "prepare_e1_b_contract": hard_pass,
            "execute_e1_b": False,
            "provider_runtime_pilot": False,
            "paper_promotion": False,
            "submission": False,
        },
        "next_gate": (
            "SEPARATE_IMMUTABLE_E1_B_CONTRACT_WITH_FRESH_UPDATER_IDENTITY_AND_NEGATIVE_CONTROL_FIRST"
            if hard_pass
            else "STOP_CENTRAL_R17_ON_CURRENT_CONTROLLED_SUBSTRATE_SUPPORT"
        ),
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if hard_pass else 3


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: repaired_adjudicator | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/adjudicate_e2_r17_e1_a_pool_support_v2.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    contract = load_json(args.contract)
    authorization = load_json(args.authorization)
    summary = load_json(args.summary)
    contract_sha = sha_file(args.contract)
    authorization_sha = sha_file(args.authorization)

    require(contract.get("status") == "FROZEN_E1_A_POOL_SUPPORT", "E1-A contract status invalid")
    require(authorization.get("status") == "AUTHORIZED_E1", "E1-A authorization status invalid")
    require(authorization.get("contract_sha256") == contract_sha, "authorization does not bind exact E1-A contract")
    require(summary.get("status") == "COMPLETED_ALL_96_POOLS_PENDING_SEPARATE_SUPPORT_ADJUDICATION", "E1-A pool freeze incomplete")
    require(summary.get("contract_sha256") == contract_sha, "summary contract SHA mismatch")
    require(summary.get("authorization_sha256") == authorization_sha, "summary authorization SHA mismatch")
    require(int(summary.get("streams") or 0) == 12, "E1-A stream cardinality invalid")
    require(int(summary.get("tasks") or 0) == 96, "E1-A task cardinality invalid")
    require(int(summary.get("actor_rollouts") or 0) == 768, "E1-A rollout cardinality invalid")
    require(summary.get("updater_calls") is not None and int(summary["updater_calls"]) == 0, "E1-A must contain zero updater calls")
    require(summary.get("e1_b_authority") is False, "E1-A summary cannot inherit E1-B authority")

    support = summary.get("support") or {}
    stream_rows = support.get("stream_rows") or []
    require(len(stream_rows) == 12, "support summary must include 12 stream rows")
    mixed = int(support.get("mixed_pool_count") or 0)
    exposed = int(support.get("exposed_stream_count") or 0)
    supported_families = int(support.get("supported_families") or 0)
    thresholds = contract["support_gate"]
    min_mixed = int(thresholds["mixed_pool_count_minimum"])
    min_exposed = int(thresholds["exposed_stream_minimum"])
    min_per_stream = int(thresholds["mixed_pools_per_exposed_stream_minimum"])
    min_families = int(thresholds["supported_families_minimum"])

    run_root = Path(contract["run_root"])
    split = load_json(Path(contract["suite"]["root"]) / "r17_split_manifest.json")
    frozen_streams = list(contract["streams"])
    require(list(split["e1_update_streams"].keys()) == frozen_streams, "stream manifest drift")
    expected_tasks = [str(task) for stream_id in frozen_streams for task in split["e1_update_streams"][stream_id]]
    require(len(expected_tasks) == 96 and len(set(expected_tasks)) == 96, "frozen update set must contain 96 unique tasks")
    task_to_stream = {
        str(task): stream_id
        for stream_id in frozen_streams
        for task in split["e1_update_streams"][stream_id]
    }
    metadata_rows = load_json(Path(contract["suite"]["root"]) / "r17_controlled_metadata.json")
    metadata = {str(row["id"]): row for row in metadata_rows}

    pool_sha: dict[str, str] = {}
    mixed_recomputed = 0
    per_stream_mixed = {stream_id: 0 for stream_id in frozen_streams}
    per_family_mixed: dict[str, int] = {}
    for task_id in expected_tasks:
        pool_path = run_root / "cases" / task_id / "pool_k8.json"
        require(pool_path.exists(), f"missing frozen K8 pool: {task_id}")
        pool = load_json(pool_path)
        require(pool.get("task_id") == task_id and int(pool.get("k") or 0) == 8, f"invalid K8 pool identity: {task_id}")
        trajectories = pool.get("trajectories") or []
        require(len(trajectories) == 8, f"K8 pool missing trajectory refs: {task_id}")
        scores = [float(row["score"]) for row in trajectories]
        is_mixed = int(min(scores) < 1.0 and max(scores) >= 1.0)
        mixed_recomputed += is_mixed
        per_stream_mixed[task_to_stream[task_id]] += is_mixed
        family = str(metadata[task_id]["primary_failure_family"])
        per_family_mixed[family] = per_family_mixed.get(family, 0) + is_mixed
        for row in trajectories:
            trajectory = Path(row["trajectory_path"])
            require(trajectory.exists() and sha_file(trajectory) == row["trajectory_sha256"], f"trajectory SHA drift: {task_id}/{row['rollout_index']}")
        pool_sha[task_id] = sha_file(pool_path)
    require(mixed_recomputed == mixed, "mixed-pool total does not recompute from exact frozen pools")
    exposed_recomputed = sum(int(value >= min_per_stream) for value in per_stream_mixed.values())
    require(exposed_recomputed == exposed, "exposed-stream count does not recompute directly from exact frozen pools")
    supported_families_recomputed = sum(int(value > 0) for value in per_family_mixed.values())
    require(supported_families_recomputed == supported_families, "supported-family count does not recompute directly from exact frozen pools")
    summary_stream_map = {str(row["stream_id"]): int(row["mixed_pools"]) for row in stream_rows}
    require(summary_stream_map == per_stream_mixed, "summary per-stream mixed counts drift from exact frozen pools")
    require(dict(sorted((support.get("family_mixed_counts") or {}).items())) == dict(sorted(per_family_mixed.items())), "summary family mixed counts drift from exact frozen pools")
    require(bool(support.get("primary_hard_gate_pass")) == (mixed >= min_mixed and exposed >= min_exposed), "hard-gate flag is inconsistent")
    require(bool(support.get("family_generalization_gate_pass")) == (supported_families >= min_families), "family gate flag is inconsistent")

    hard_pass = mixed >= min_mixed and exposed >= min_exposed
    family_pass = supported_families >= min_families
    status = "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT" if hard_pass else "STOP_E1_SUPPORT_INSUFFICIENT"
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-e1-a-pool-support-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "summary_path": str(args.summary),
        "summary_sha256": sha_file(args.summary),
        "integrity": {
            "streams": 12,
            "tasks": 96,
            "actor_rollouts": 768,
            "frozen_k8_pools": 96,
            "all_trajectory_shas_revalidated": True,
            "task_replacement_after_support_observation": False,
            "waiver_or_rounding": False,
            "updater_calls": 0,
        },
        "primary_support": {
            "mixed_pools": mixed,
            "required_mixed_pools": min_mixed,
            "exposed_streams": exposed,
            "required_exposed_streams": min_exposed,
            "mixed_per_exposed_stream": min_per_stream,
            "per_stream_mixed_recomputed": per_stream_mixed,
            "pass": hard_pass,
        },
        "family_generalization": {
            "supported_families": supported_families,
            "required_supported_families": min_families,
            "pass": family_pass,
            "per_family_mixed_recomputed": dict(sorted(per_family_mixed.items())),
            "controls_primary_e1_b_authorization": False,
            "claim_if_failed": "Block family-generalization and prospective family-ranking claims; pooled E1-B may still be contracted only if primary support passes."
        },
        "pool_sha256": pool_sha,
        "interpretation": (
            "This adjudication evaluates only pre-treatment mixed-pool support and protocol integrity. "
            "It does not evaluate MRW, WIN, RB-AGG, future skill utility, or paper effectiveness."
        ),
        "authority": {
            "prepare_e1_b_contract": hard_pass,
            "execute_e1_b": False,
            "provider_runtime_pilot": False,
            "paper_promotion": False,
            "submission": False,
        },
        "next_gate": (
            "SEPARATE_IMMUTABLE_E1_B_CONTRACT_WITH_FRESH_UPDATER_IDENTITY_AND_NEGATIVE_CONTROL_FIRST"
            if hard_pass
            else "STOP_CENTRAL_R17_ON_CURRENT_CONTROLLED_SUBSTRATE_SUPPORT"
        ),
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if hard_pass else 3


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: frozen_contract | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-pool-support-v2-1-contract-20260828.json =====
{
  "actor": {
    "concurrency": 4,
    "max_output_tokens": 4096,
    "max_turns": 10,
    "provider_retry_limit": 0,
    "requested_model": "deepseek-v4-pro",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "search_topology": "parallel_best_of_k",
    "temperature": 0,
    "thinking": "disabled"
  },
  "artifact_type": "e2-r17-e1-a-pool-support-contract",
  "authority": {
    "execute_e1_a": false,
    "execute_e1_b": false,
    "independent_preexecution_review": true,
    "paper_promotion": false,
    "provider_runtime_updater_pilot": false,
    "submission": false
  },
  "authorization_scope_required": {
    "allow_noninitial_skill": false,
    "allowed_modes": [
      "e1"
    ],
    "allowed_task_ids": "exact 96 task IDs from the bound e1_update_streams split",
    "authority.e1_a": true,
    "authority.e1_b": false,
    "authority.scientific_experiment": true,
    "exact_k": 8,
    "identity_artifact_sha256": "7fb73c09bc96288438989f4b773abbe3bcb37c43d150b78a9c66da80d1b66ae4",
    "max_output_tokens": 4096,
    "max_turns": 10,
    "provider_budget": {
      "claim_before_provider_io": true,
      "claims_never_released": true,
      "ledger_relative_path": "checkpoints/provider_budget.sqlite3",
      "per_unit_limit": 10,
      "required": true,
      "total_limit": 7680
    },
    "required_resolved_model": "deepseek-v4-pro-ga-260813",
    "required_skill_pre_sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb",
    "runtime_freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "runtime_python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "runtime_qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "status": "AUTHORIZED_E1",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4"
  },
  "bound_code": {
    "actor_pool": {
      "path": "research_pipeline/e2_r17_actor_pool.py",
      "sha256": "ade5f605f32056b7797dbcbcb7b3e839b9c18dce1c0f287f609d86cee3463ef4"
    },
    "actor_runner": {
      "path": "scripts/run_e2_r17_actor_pool.py",
      "sha256": "20a81fbe06f3839cd17babfdb021407368493da61610bca33aae33df8d31ec14"
    },
    "ark_plan_react": {
      "path": "research_pipeline/e2_r17_ark_plan_react.py",
      "sha256": "7a7a9c40774429ac3c9a7c8c003bbc46628a6ef574bd481e628668894e803fba"
    },
    "authority_scope_test": {
      "path": "research_pipeline/test_e2_r17_actor_authority_scope.py",
      "sha256": "4c383aed93bb4d20d0726bc02c3fbba72baead62cc55838850b4f12061b2a1a0"
    },
    "e1_a_orchestrator": {
      "path": "scripts/run_e2_r17_e1_a_pool_support.py",
      "sha256": "24ea070b08399d48af99294615a508874f851af941f5bb0efabe341b0854617d"
    },
    "provider_budget_ledger": {
      "path": "research_pipeline/e2_r17_provider_budget.py",
      "sha256": "df819b30a31e62e007e3f85ae76aa8d06faefaa56e9acefe71ceadb9f8fce444"
    },
    "provider_budget_tests": {
      "path": "research_pipeline/test_e2_r17_provider_budget.py",
      "sha256": "443b0377941a4fbba1a6eaf7fa5af8e33615511b43890bd73da19a8ec94b61eb"
    },
    "search_projection_runner": {
      "path": "research_pipeline/e2_r17_search_projection_runner.py",
      "sha256": "91f5545fe6def937ddee231e71295cc2539bfbb6ea1cf8292f8daef81b4272bc"
    },
    "support_adjudicator": {
      "path": "scripts/adjudicate_e2_r17_e1_a_pool_support.py",
      "sha256": "9972296dfc140a3cbd29bc6f475dddb46822353a1f9ae56b5f5b243c13b722ea"
    }
  },
  "budget": {
    "actor_rollouts_exact": 768,
    "claim_semantics": "transactional claim before provider generation I/O; claims are never released after error/crash",
    "duplicate_completed_rollout_calls": 0,
    "fail_closed_pre_io": true,
    "ledger_relative_path": "checkpoints/provider_budget.sqlite3",
    "max_output_tokens_per_provider_call": 4096,
    "max_provider_calls": 7680,
    "provider_retry_limit": 0,
    "theoretical_max_output_tokens": 31457280,
    "updater_calls": 0
  },
  "checkpoint": {
    "blind_relaunch_after_timeout_or_502": false,
    "exclusive_lock": ".exclusive.lock",
    "leave_lock_on_failure_for_manual_inspection": true,
    "resume_missing_only": true,
    "revalidate_completed_stream_and_rollout_sha_before_resume": true,
    "stream_manifest": "checkpoints/completed_streams.jsonl",
    "stream_summary": "summary/streams/<stream>.json",
    "unit_level_pool_freeze": "cases/<task>/pool_k{1,2,4,8}.json",
    "unit_level_rollout_refs": "cases/<task>/rollout_<i>/r17_trajectory_ref.json"
  },
  "date": "2026-08-28",
  "forbidden_during_e1_a": [
    "updater calls",
    "MRW/WIN/RB-AGG skill updates",
    "held-out future-skill evaluation",
    "method-effectiveness selection",
    "task replacement or dropping after mixed-pool support is observed",
    "changing K/model/skill/prompt/verifier after launch",
    "paper promotion",
    "automatic E1-B authority inheritance"
  ],
  "freeze_rule": "No scientific/support/runtime semantics changed from reviewed V2.1 draft; only freeze/review metadata added.",
  "frozen_at_utc": "2026-08-28T14:23:17+00:00",
  "mindmemos": {
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "initial_skill_sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb",
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817",
    "skill_mutation_allowed": false
  },
  "model_identity": {
    "path": "generated/e2-r17-e1-a-v2-1-model-identity-adjudication-20260828.json",
    "qualification_path": "generated/e2-r17-e1-a-v2-1-model-identity-qualification-20260828.json",
    "qualification_sha256": "08982d439f46bea48b73d1dc09d7af1504eda5ba725738bcf4d785a2fa32fa54",
    "sha256": "7fb73c09bc96288438989f4b773abbe3bcb37c43d150b78a9c66da80d1b66ae4",
    "status": "PASS_CURRENT_REVIEW_TRANCHE"
  },
  "parent_review_summary": {
    "decision": "REVISE_ONE_P0_PROVIDER_BUDGET_GUARD",
    "path": "generated/e2-r17-e1-a-preexecution-review-20260828/summary.json",
    "sha256": "5bc47a53a56fa2a11d0e715c9d1c7131aacb045084266a259ff55090eb52071c"
  },
  "parent_runtime_failure": {
    "path": "generated/e2-r17-e1-a-v2-runtime-failure-adjudication-20260828.json",
    "sha256": "3ad8b73ce13f8b5bc0e51f109a8e910e0894656d3bdd94f10290126a3388a399",
    "status": "TECHNICAL_FAILURE_ZERO_PROVIDER_ZERO_SCIENTIFIC_OUTCOME"
  },
  "parents": {
    "v3_1_mechanical_adjudication": {
      "path": "generated/e2-r17-v3-1-mechanical-pilot-adjudication-20260828.json",
      "sha256": "9b02d870f808c5f61e42b87b9bf09c8028192207267ef56bf65f40fa988b3a10",
      "status": "PASS_MECHANICAL_ONLY_NO_E1_AUTHORITY"
    },
    "v3_plan": {
      "path": "generated/e2-r17-experiment-plan-v3-20260828.json",
      "sha256": "b1a0224117f161ead9fccefa2c22a0f01dfa1d9e72ca1e98107418f21e3e04c5"
    }
  },
  "post_run": {
    "adjudicator": "scripts/adjudicate_e2_r17_e1_a_pool_support.py",
    "if_primary_support_fail": "STOP_E1_BEFORE_UPDATER",
    "if_primary_support_pass": "may prepare a separate immutable E1-B contract; E1-B remains unauthorized until separately reviewed",
    "primary_support_pass": "mixed>=24/96 AND exposed_streams>=8/12 where each exposed stream has >=2 mixed pools",
    "runner_status": "COMPLETED_ALL_96_POOLS_PENDING_SEPARATE_SUPPORT_ADJUDICATION"
  },
  "preexecution_review": {
    "all_allow_separate_e1_a_authorization": true,
    "path": "generated/e2-r17-e1-a-runtime-repair-review-v21-20260828/summary.json",
    "sha256": "00b4f63ad34c729be2b60ca216d59cbe57b0ec98b2a0117dc59151bfa40f1ddc"
  },
  "repair_tests": {
    "command": "python3 -m unittest research_pipeline.test_e2_r17_provider_budget research_pipeline.test_e2_r17_ark_plan_react research_pipeline.test_e2_r17_search_projection_runner research_pipeline.test_e2_r17_actor_authority_scope",
    "eleventh_call_pre_io_blocked": true,
    "global_7681st_call_pre_io_blocked": true,
    "provider_io_used": false,
    "status": "PASS_21_TESTS"
  },
  "reviewed_draft": {
    "path": "generated/e2-r17-e1-a-pool-support-v2-1-draft-contract-20260828.json",
    "sha256": "34bb95012dac2c7efc186d0ab9a4839efeddd21b2179b086fb38c49e48dd9fec"
  },
  "revision": "V2_1_EXPLICIT_FROZEN_RUNTIME_BINDING",
  "run_root": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-1-20260828",
  "runtime": {
    "ambient_sys_executable_for_actor_forbidden": true,
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt",
    "freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "qualification_path": "generated/e2-r17-runtime-dependency-qualification-r2-20260828.json",
    "qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "required_imports": [
      "pydantic",
      "openpyxl==3.1.5",
      "mindmemos_eval.skills.agents.ReactAgentFactory",
      "mindmemos_eval.skills.envs.spreadsheetbench.env.SpreadsheetBenchEnv"
    ],
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv"
  },
  "schema_version": "1.0",
  "scientific_role": "PRE_TREATMENT_SUPPORT_AND_POOL_FREEZE_ONLY",
  "scientific_units": {
    "actor_rollouts": 768,
    "heldout_future_skill_evaluations": 0,
    "nested_prefixes": [
      1,
      2,
      4,
      8
    ],
    "search_k": 8,
    "streams": 12,
    "tasks_per_stream": 8,
    "unique_update_tasks": 96,
    "updater_calls": 0
  },
  "status": "FROZEN_E1_A_POOL_SUPPORT",
  "streams": [
    "e1-agj-00",
    "e1-agj-01",
    "e1-fmv-00",
    "e1-fmv-01",
    "e1-ioc-00",
    "e1-ioc-01",
    "e1-msp-00",
    "e1-msp-01",
    "e1-ska-00",
    "e1-ska-01",
    "e1-tsr-00",
    "e1-tsr-01"
  ],
  "suite": {
    "metadata_sha256": "12d6eb876e2a230e7990be3e61fed108d45f6ddec00bac5c9b88585a04111b04",
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2",
    "split_is_outcome_blind": true,
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4",
    "task_replacement_after_support_observation": false
  },
  "support_gate": {
    "borderline_is_failure": true,
    "evaluate_only_after_all_96_k8_pools_are_frozen": true,
    "exposed_stream_minimum": 8,
    "family_gate_controls_primary_e1_b": false,
    "hard_gate_failure": "STOP_E1_BEFORE_ANY_UPDATER_CALL",
    "mixed_pool_count_minimum": 24,
    "mixed_pool_total": 96,
    "mixed_pools_per_exposed_stream_minimum": 2,
    "replace_or_drop_tasks_after_support_observation": false,
    "rounding_or_waiver": false,
    "stream_total": 12,
    "supported_families_minimum": 4
  },
  "technical_repair_gate": {
    "VIRTUAL_ENV_and_PATH_must_bind_contract_venv": true,
    "actor_must_spawn_with_contract_runtime_python": true,
    "failed_v2_provider_budget_claims": 0,
    "failed_v2_root_must_remain_untouched": true,
    "failed_v2_stale_lock_must_remain": true,
    "fresh_run_root_required": true,
    "runtime_import_smoke_before_actor_spawn": true
  }
}


===== BOUND ARTIFACT: frozen_authorization | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-pool-support-v2-1-authorization-20260828.json =====
{
  "allow_task_replacement": false,
  "artifact_type": "e2-r17-e1-a-exact-authorization",
  "authority": {
    "e1_a": true,
    "e1_b": false,
    "front_end_claim": false,
    "gpu": false,
    "paper_promotion": false,
    "provider_runtime_pilot": false,
    "scientific_experiment": true,
    "submission": false
  },
  "contract_path": "generated/e2-r17-e1-a-pool-support-v2-1-contract-20260828.json",
  "contract_sha256": "f2919d201f03a0166d6255240378efd14d45bc7f8a3269bff5b78fcccb6d1d21",
  "created_at_utc": "2026-08-28T14:23:17+00:00",
  "execution_scope": {
    "allow_noninitial_skill": false,
    "allowed_modes": [
      "e1"
    ],
    "allowed_task_ids": [
      "r17-b2-agj-p2",
      "r17-b2-agj-p5",
      "r17-b2-agj-p7",
      "r17-b3-agj-p0",
      "r17-b2-agj-p3",
      "r17-b3-agj-p3",
      "r17-b2-agj-p8",
      "r17-b3-agj-p8",
      "r17-b2-agj-p0",
      "r17-b3-agj-p6",
      "r17-b3-agj-p2",
      "r17-b3-agj-p5",
      "r17-b2-agj-p6",
      "r17-b3-agj-p7",
      "r17-b3-agj-p1",
      "r17-b2-agj-p4",
      "r17-b3-fmv-p4",
      "r17-b2-fmv-p8",
      "r17-b2-fmv-p1",
      "r17-b2-fmv-p0",
      "r17-b3-fmv-p5",
      "r17-b2-fmv-p5",
      "r17-b3-fmv-p7",
      "r17-b2-fmv-p6",
      "r17-b3-fmv-p0",
      "r17-b2-fmv-p7",
      "r17-b2-fmv-p2",
      "r17-b3-fmv-p2",
      "r17-b3-fmv-p1",
      "r17-b3-fmv-p8",
      "r17-b3-fmv-p3",
      "r17-b2-fmv-p3",
      "r17-b3-ioc-p3",
      "r17-b2-ioc-p2",
      "r17-b2-ioc-p5",
      "r17-b2-ioc-p8",
      "r17-b2-ioc-p0",
      "r17-b3-ioc-p6",
      "r17-b3-ioc-p7",
      "r17-b2-ioc-p3",
      "r17-b3-ioc-p0",
      "r17-b3-ioc-p5",
      "r17-b2-ioc-p6",
      "r17-b2-ioc-p7",
      "r17-b3-ioc-p4",
      "r17-b2-ioc-p1",
      "r17-b3-ioc-p1",
      "r17-b3-ioc-p8",
      "r17-b2-msp-p4",
      "r17-b3-msp-p4",
      "r17-b2-msp-p8",
      "r17-b3-msp-p3",
      "r17-b3-msp-p2",
      "r17-b2-msp-p6",
      "r17-b3-msp-p0",
      "r17-b3-msp-p8",
      "r17-b3-msp-p5",
      "r17-b2-msp-p1",
      "r17-b3-msp-p1",
      "r17-b2-msp-p2",
      "r17-b2-msp-p7",
      "r17-b3-msp-p7",
      "r17-b2-msp-p5",
      "r17-b3-msp-p6",
      "r17-b2-ska-p3",
      "r17-b2-ska-p1",
      "r17-b2-ska-p4",
      "r17-b3-ska-p8",
      "r17-b3-ska-p2",
      "r17-b3-ska-p6",
      "r17-b2-ska-p6",
      "r17-b2-ska-p7",
      "r17-b2-ska-p8",
      "r17-b3-ska-p1",
      "r17-b3-ska-p7",
      "r17-b3-ska-p0",
      "r17-b2-ska-p5",
      "r17-b3-ska-p5",
      "r17-b3-ska-p3",
      "r17-b2-ska-p0",
      "r17-b3-tsr-p7",
      "r17-b3-tsr-p0",
      "r17-b2-tsr-p3",
      "r17-b2-tsr-p8",
      "r17-b2-tsr-p2",
      "r17-b2-tsr-p5",
      "r17-b2-tsr-p4",
      "r17-b3-tsr-p8",
      "r17-b2-tsr-p0",
      "r17-b2-tsr-p6",
      "r17-b2-tsr-p1",
      "r17-b3-tsr-p3",
      "r17-b3-tsr-p1",
      "r17-b3-tsr-p4",
      "r17-b3-tsr-p6",
      "r17-b3-tsr-p5"
    ],
    "authority.e1_a": true,
    "authority.e1_b": false,
    "authority.scientific_experiment": true,
    "exact_k": 8,
    "identity_artifact_sha256": "7fb73c09bc96288438989f4b773abbe3bcb37c43d150b78a9c66da80d1b66ae4",
    "max_output_tokens": 4096,
    "max_turns": 10,
    "provider_budget": {
      "claim_before_provider_io": true,
      "claims_never_released": true,
      "ledger_relative_path": "checkpoints/provider_budget.sqlite3",
      "per_unit_limit": 10,
      "required": true,
      "total_limit": 7680
    },
    "required_resolved_model": "deepseek-v4-pro-ga-260813",
    "required_skill_pre_sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb",
    "runtime_freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "runtime_python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "runtime_qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "status": "AUTHORIZED_E1",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4"
  },
  "identity_path": "generated/e2-r17-e1-a-v2-1-model-identity-adjudication-20260828.json",
  "identity_sha256": "7fb73c09bc96288438989f4b773abbe3bcb37c43d150b78a9c66da80d1b66ae4",
  "k": 8,
  "max_output_tokens": 4096,
  "max_turns": 10,
  "mindmemos_commit": "90491828726e1540442b17cd445d0308d0b8093c",
  "mindmemos_root": "/data/wyt/evidence-substrates/MindMemOS-20260817",
  "parent_failed_v2_adjudication_path": "generated/e2-r17-e1-a-v2-runtime-failure-adjudication-20260828.json",
  "parent_failed_v2_adjudication_sha256": "3ad8b73ce13f8b5bc0e51f109a8e910e0894656d3bdd94f10290126a3388a399",
  "preexecution_review_path": "generated/e2-r17-e1-a-runtime-repair-review-v21-20260828/summary.json",
  "preexecution_review_sha256": "00b4f63ad34c729be2b60ca216d59cbe57b0ec98b2a0117dc59151bfa40f1ddc",
  "prefix_ks": [
    1,
    2,
    4,
    8
  ],
  "private_credentials_included": false,
  "provider_retry_limit": 0,
  "raw_response_ids_included": false,
  "requested_model": "deepseek-v4-pro",
  "resolved_model": "deepseek-v4-pro-ga-260813",
  "resume_missing_units_only": true,
  "run_root": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-1-20260828",
  "runtime": {
    "ambient_sys_executable_for_actor_forbidden": true,
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt",
    "freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "qualification_path": "generated/e2-r17-runtime-dependency-qualification-r2-20260828.json",
    "qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "required_imports": [
      "pydantic",
      "openpyxl==3.1.5",
      "mindmemos_eval.skills.agents.ReactAgentFactory",
      "mindmemos_eval.skills.envs.spreadsheetbench.env.SpreadsheetBenchEnv"
    ],
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv"
  },
  "schema_version": "1.0",
  "status": "AUTHORIZED_E1",
  "stop_on_any_protocol_failure": true,
  "thinking": "disabled"
}


===== BOUND ARTIFACT: prior_runtime_repair_review | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-runtime-repair-review-v21-20260828/summary.json =====
{
  "all_allow_separate_e1_a_authorization": true,
  "all_completed": true,
  "artifact_type": "e2-r17-e1-a-dual-preexecution-review-summary",
  "created_at_utc": "2026-08-28T14:22:18+00:00",
  "draft_contract_sha256": "34bb95012dac2c7efc186d0ab9a4839efeddd21b2179b086fb38c49e48dd9fec",
  "e1_a_recommendations": {
    "deepseek-v4-pro": "ALLOW_SEPARATE_FROZEN_E1_A_AUTHORIZATION",
    "kimi-k3": "ALLOW_SEPARATE_FROZEN_E1_A_AUTHORIZATION"
  },
  "e1_b_recommendations": {
    "deepseek-v4-pro": "HOLD",
    "kimi-k3": "HOLD"
  },
  "exposed_to_other_review": false,
  "independent": true,
  "paper_claim_authority": false,
  "resolved_models": {
    "deepseek-v4-pro": "deepseek-v4-pro-ga-260813",
    "kimi-k3": "kimi-k3"
  },
  "schema_version": "1.0",
  "scientific_authority": false,
  "statuses": {
    "deepseek-v4-pro": "COMPLETED",
    "kimi-k3": "COMPLETED"
  },
  "verdicts": {
    "deepseek-v4-pro": "PASS_TO_SEPARATELY_BOUND_E1_A_AUTHORIZATION",
    "kimi-k3": "PASS_TO_SEPARATELY_BOUND_E1_A_AUTHORIZATION"
  }
}


===== BOUND ARTIFACT: review_identity | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-v2-1-model-identity-qualification-20260828.json =====
{
  "artifact_type": "e2-r17-current-ark-plan-model-identity-qualification",
  "authority": {
    "gpu": false,
    "paper_promotion": false,
    "preexecution_consultation": true,
    "scientific_experiment": false,
    "submission": false
  },
  "checks": {
    "all_protocol_calls_pass": true,
    "provider_retry_zero": true,
    "resolved_identities_distinct": true,
    "route_is_ark_plan": true
  },
  "compatibility_parent": null,
  "created_at_utc": "2026-08-28T14:19:07+00:00",
  "default_model": "ark-code-latest",
  "models": [
    {
      "benchmark_data_accessed": false,
      "checks": {
        "resolved_model_matches_requested_family": true,
        "resolved_model_present": true,
        "text_exact": true
      },
      "get_poll_recovery": false,
      "hidden_provider_retry_used": false,
      "max_output_tokens": 256,
      "poll_count": 0,
      "prompt_sha256": "7bfaf5897d7bbd7f972a67554ee32acc828cd8309e40822dfc05217e987776bf",
      "provider_generation_attempts": 1,
      "provider_retry_limit": 0,
      "provider_status": "completed",
      "raw_text": "PLAN_OK",
      "raw_text_sha256": "aa6b4c1b97751f326153c1927c1106bf5a927ec506a8066dfe0dded595992d7c",
      "requested_model": "deepseek-v4-pro",
      "resolved_model": "deepseek-v4-pro-ga-260813",
      "response_id_sha256": "e9a99ca16f994e16908f91a7dd0f9f4fe48ac7bcc08271f81cc6098c62c8c49a",
      "scientific_outcome": false,
      "status": "PASS",
      "thinking_requested": "disabled",
      "usage": {
        "input_tokens": 27,
        "input_tokens_details": {
          "cached_tokens": 0
        },
        "output_tokens": 3,
        "output_tokens_details": {
          "reasoning_tokens": 0
        },
        "total_tokens": 30
      }
    },
    {
      "benchmark_data_accessed": false,
      "checks": {
        "resolved_model_matches_requested_family": true,
        "resolved_model_present": true,
        "text_exact": true
      },
      "get_poll_recovery": false,
      "hidden_provider_retry_used": false,
      "max_output_tokens": 256,
      "poll_count": 0,
      "prompt_sha256": "7bfaf5897d7bbd7f972a67554ee32acc828cd8309e40822dfc05217e987776bf",
      "provider_generation_attempts": 1,
      "provider_retry_limit": 0,
      "provider_status": "completed",
      "raw_text": "PLAN_OK",
      "raw_text_sha256": "aa6b4c1b97751f326153c1927c1106bf5a927ec506a8066dfe0dded595992d7c",
      "requested_model": "kimi-k3",
      "resolved_model": "kimi-k3",
      "response_id_sha256": "ab55e1b1cff02303d5f4d36fa532a36e341267c2cb5fd0f78a6b624a9c0c892d",
      "scientific_outcome": false,
      "status": "PASS",
      "thinking_requested": "disabled",
      "usage": {
        "input_tokens": 41,
        "input_tokens_details": {
          "cached_tokens": 0
        },
        "output_tokens": 13,
        "output_tokens_details": {
          "reasoning_tokens": 0
        },
        "total_tokens": 54
      }
    }
  ],
  "private_credentials_included": false,
  "raw_response_ids_included": false,
  "release_drift_policy": "Observed resolved identities are frozen for this review tranche. Historical exact suffixes are not reused as authority. Any later execution tranche must requalify and bind its own observed identities.",
  "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
  "schema_version": "1.0",
  "status": "PASS"
}


BOUND DOSSIER END
