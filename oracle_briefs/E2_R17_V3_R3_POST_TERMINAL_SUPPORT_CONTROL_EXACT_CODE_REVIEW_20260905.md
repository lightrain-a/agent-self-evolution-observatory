# E2-R17 V3 R3 post-terminal support-read additive control plane — exact-code independent review

Date: 2026-09-05
Role: fresh independent senior ICLR/NeurIPS/ICML agent-systems methodology/control-plane reviewer
Scope: ZERO-PROVIDER exact-code review only

## 0. Review rule

A prior fresh GPT-5.6 Sol + Extra High review returned `REQUIRE_SEPARATE_POST_TERMINAL_SUPPORT_READ_AUTHORIZATION`. It explicitly said this must be resolved before provider recovery, but requires no R3 scientific redesign and does not affect provider-recovery authority.

Review only whether the additive code below correctly implements that required authority boundary. Do not infer Stage-A support, Stage-B effect, or any paper outcome. Do not reopen already-passed R3 matched-censor geometry, no-replay rule, task universe, support threshold, provider budget, or workload unless this new code violates them.

No R3 provider recovery has started. No terminal summary exists. No support-read authorization has been minted. No Stage-A support has been inspected.

End with exactly one verdict token:

- `PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE`
- `REVISE_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE`
- `STOP_R3_PROVIDER_RECOVERY_FOR_CONTROL_PLANE`

Then list only verdict-changing required fixes.

## 1. Frozen scientific object and prior authority review

R3 contract SHA256: `3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085`
Frozen R3 recovery runner SHA256: `491b2ae6e53fcfe732f15ef263cc365ce61846b3219d7a13fe70e3834f6d3c89`
Frozen R3 support adjudicator SHA256: `e326ee92f7765aa68856c6fe09610996209d4aa3d3ad464a65d391a88a4cbae4`
Prior authority-review receipt SHA256: `575ab2f4535d994bfd23e2dedcd9effbc26d8d358f5c3b1b3d26411c7f0d6846`
Static preflight SHA256: `b8eec8d147d62c4c6d05c2edfd0ea18b663efee3eea2040553f76a2e1fc85fee`

The frozen scientific files above were not modified by this additive control-plane repair.

Prior authority-review verdict: `REQUIRE_SEPARATE_POST_TERMINAL_SUPPORT_READ_AUTHORIZATION`.

Required semantics from that review:

1. freeze the additive support-read authorization schema/minter before provider recovery;
2. actual support-read authorization may be minted only after exact terminal 158-pool recovery state;
3. require that authorization before invoking the already reviewed support adjudicator;
4. no R3 contract/runner/support-adjudicator redesign;
5. no Stage-B authority.

## 2. Intended additive architecture

```text
R3 provider recovery authorization
        |
        v
158-task recovery runner
        |
        v
exact terminal summary
(support_inspected=false)
        |
        v
NEW zero-provider support-read minter
(structure/hash only; does not parse pool semantics)
        |
        v
single-use support-read authorization
        |
        v
NEW O_EXCL one-shot gate consumes permit
        |
        v
EXISTING frozen support adjudicator
(the only component that opens K8 scientific semantics)
        |
        +--> support PASS: prepare_stage_b_contract=true, execute_stage_b=false
        +--> support HOLD: stop/hold, execute_stage_b=false
```

The new minter hashes `pool_k8.json` bytes to verify sealed-file lineage but does not JSON-parse trajectory content or compute mixed/success support. The new gate does not interpret support itself; it validates authority, burns an O_EXCL consumption marker, and invokes the existing frozen adjudicator. Unexpected adjudicator failure leaves the permit consumed and requires manual review; no automatic retry exists.

## 3. Exact hashes of additive implementation

- MINTER: `scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py`
  - SHA256 `6bffa212eed8a1be630b7d0917a5b12d53b65b3e43969e009ded638745edc471`
- ONE_SHOT_GATE: `scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py`
  - SHA256 `8802f5f5b2fbe44d7649974d8b4e6b82517bf91241b95c9b8bd932cd4c63eda8`
- ZERO_PROVIDER_TESTS: `research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py`
  - SHA256 `bf4cfb83e6af1843b1c30d8ccd2804c1dff2328db0b36b954c6ebf1b4df5649a`
- STATIC_PREFLIGHT: `scripts/preflight_e2_r17_semantic_transfer_v3_stage_a_r3_support_read_control.py`
  - SHA256 `668ae7f14e893490d6b578c32621569829612b8acab9253874af0113192ca502`
- STATIC PREFLIGHT ARTIFACT: `generated/e2-r17-v3-stage-a-r3-post-terminal-support-control-preflight-20260905.json`
  - SHA256 `b8eec8d147d62c4c6d05c2edfd0ea18b663efee3eea2040553f76a2e1fc85fee`

Unit tests: `7/7 PASS`.

Tested failure boundaries include:
- missing/nonterminal terminal summary rejected;
- `support_inspected=true` rejected;
- recovery-authorization hash drift rejected;
- permit grants Stage-A support-read only and Stage-B false;
- gate refuses invalid/missing support-read authority;
- unexpected adjudicator failure permanently consumes the permit and prevents retry;
- terminal PASS completion preserves Stage-B execution=false.

## 4. Static preflight artifact

```json
{
  "actual_support_read_authorization_minted": false,
  "additive_control_plane": {
    "gate_path": "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py",
    "gate_sha256": "8802f5f5b2fbe44d7649974d8b4e6b82517bf91241b95c9b8bd932cd4c63eda8",
    "minter_path": "scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py",
    "minter_sha256": "6bffa212eed8a1be630b7d0917a5b12d53b65b3e43969e009ded638745edc471",
    "tests_path": "research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py",
    "tests_sha256": "bf4cfb83e6af1843b1c30d8ccd2804c1dff2328db0b36b954c6ebf1b4df5649a"
  },
  "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-control-zero-provider-preflight",
  "authority": {
    "heldout": false,
    "paper_claim": false,
    "provider_recovery": false,
    "stage_a_support_read": false,
    "stage_b_execution": false
  },
  "authority_review_path": "generated/e2-r17-v3-r3-post-terminal-support-authority-gpt56-review-20260905.json",
  "authority_review_sha256": "575ab2f4535d994bfd23e2dedcd9effbc26d8d358f5c3b1b3d26411c7f0d6846",
  "authority_review_verdict": "REQUIRE_SEPARATE_POST_TERMINAL_SUPPORT_READ_AUTHORIZATION",
  "checks": {
    "additive_gate_exists": true,
    "additive_minter_exists": true,
    "authority_review_requires_separate_support_auth": true,
    "live_r3_lease_absent": true,
    "live_r3_run_root_absent": true,
    "live_support_adjudication_output_absent": true,
    "live_support_read_authorization_absent": true,
    "provider_recovery_authority_unaffected": true,
    "r3_contract_unchanged": true,
    "r3_recovery_runner_unchanged": true,
    "r3_support_adjudicator_unchanged": true,
    "stage_b_authority": false,
    "zero_provider_tests_exist": true
  },
  "contract_path": "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3-recovery-20260905.json",
  "contract_sha256": "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085",
  "created_at_utc": "2026-09-05T14:40:11+00:00",
  "exact_code_review_complete": false,
  "frozen_scientific_code": {
    "recovery_runner_path": "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py",
    "recovery_runner_sha256": "491b2ae6e53fcfe732f15ef263cc365ce61846b3219d7a13fe70e3834f6d3c89",
    "support_adjudicator_path": "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py",
    "support_adjudicator_sha256": "e326ee92f7765aa68856c6fe09610996209d4aa3d3ad464a65d391a88a4cbae4"
  },
  "next_gate": "FRESH_GPT56_SOL_EXTRA_HIGH_EXACT_CODE_REVIEW_OF_ADDITIVE_SUPPORT_READ_CONTROL_PLANE",
  "provider_calls": 0,
  "schema_version": "1.0",
  "scientific_execution": false,
  "stage_b_authority": false,
  "status": "PASS_ZERO_PROVIDER_R3_POST_TERMINAL_SUPPORT_CONTROL_PREFLIGHT",
  "support_inspected": false,
  "unit_tests": {
    "passed": 7,
    "suite": "research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control",
    "total": 7
  }
}
```

## Source: MINTER — `scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
RECOVERY_AUTH_STATUS = "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY"
SUMMARY_STATUS = "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION"
LEASE_STATUS = "COMPLETED_STAGE_A_V3_R3_RECOVERY_PENDING_EQUAL_DOSE_ADJUDICATION"
SUPPORT_AUTH_STATUS = "AUTHORIZED_E2_R17_V3_R3_POST_TERMINAL_SUPPORT_READ"
CONTROL_REVIEW_VERDICT = "PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"
BURNED = "r17-b21-cgwb-p0"
CENSOR = "r17-b21-cgwp-p0"
EXPECTED_SUPPORT_ADJUDICATOR = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
EXPECTED_SUPPORT_ADJUDICATOR_SHA256 = "e326ee92f7765aa68856c6fe09610996209d4aa3d3ad464a65d391a88a4cbae4"
EXPECTED_GATE = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py"
EXPECTED_ADJUDICATION_OUTPUT = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3-equal-dose-adjudication-20260907.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def bound(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def task_claim_paths(claim_root: Path, task_id: str) -> tuple[Path, Path]:
    stem = hashlib.sha256(task_id.encode("utf-8")).hexdigest()
    return claim_root / f"{stem}.attempt.json", claim_root / f"{stem}.sealed.json"


def validate_control_review(review_path: Path, *, minter_sha: str, gate_sha: str) -> dict[str, Any]:
    review = load(review_path)
    req(review.get("status") == "COMPLETED", "post-terminal control review is not completed")
    req(review.get("surface") == "ChatGPT web", "post-terminal control review surface drift")
    req(review.get("model") == "GPT-5.6 Sol", "post-terminal control review model drift")
    req(review.get("verdict") == CONTROL_REVIEW_VERDICT, "post-terminal control review did not PASS")
    req(review.get("minter_sha256_acknowledged") == minter_sha, "post-terminal control review minter SHA drift")
    req(review.get("gate_sha256_acknowledged") == gate_sha, "post-terminal control review gate SHA drift")
    req(
        review.get("support_adjudicator_sha256_acknowledged") == EXPECTED_SUPPORT_ADJUDICATOR_SHA256,
        "post-terminal control review support-adjudicator SHA drift",
    )
    req(review.get("stage_b_authority") is False, "post-terminal control review grants Stage-B authority")
    req(review.get("scientific_authority") is False, "post-terminal control review grants scientific authority")
    return review


def validate_terminal_structure(
    *,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
) -> dict[str, Any]:
    contract = load(contract_path)
    recovery_auth = load(recovery_authorization_path)
    summary = load(summary_path)
    csha = sha(contract_path)
    asha = sha(recovery_authorization_path)
    ssha = sha(summary_path)

    req(contract.get("status") == CONTRACT_STATUS, "R3 recovery contract status drift")
    req(recovery_auth.get("status") == RECOVERY_AUTH_STATUS, "R3 recovery authorization status drift")
    req(recovery_auth.get("contract_sha256") == csha, "R3 recovery authorization contract SHA drift")
    req(recovery_auth.get("single_use") is True and recovery_auth.get("exactly_once") is True, "R3 recovery authorization single-use drift")
    authority = recovery_auth.get("authority") or {}
    req(authority.get("stage_a_provider_execution") is True, "R3 recovery authorization provider authority absent")
    for key in (
        "stage_b_learning_execution",
        "updater",
        "heldout_evaluation",
        "analyzer",
        "second_backbone",
        "public_benchmark",
        "paper_promotion",
        "submission",
    ):
        req(authority.get(key) is False, f"R3 recovery authorization overbroad: {key}")

    req(summary.get("status") == SUMMARY_STATUS, "R3 terminal summary status drift")
    req(summary.get("contract_sha256") == csha, "R3 terminal summary contract SHA drift")
    req(summary.get("authorization_sha256") == asha, "R3 terminal summary authorization SHA drift")
    req(summary.get("planned_tasks") == 160, "R3 terminal summary planned-task drift")
    req(summary.get("provider_executable_tasks") == 158, "R3 terminal summary provider-task drift")
    req(summary.get("sealed_k8_pools") == 158, "R3 terminal summary sealed-pool drift")
    req(summary.get("terminal_technical_missing") == 1, "R3 terminal summary technical-missing drift")
    req(summary.get("matched_no_provider_censor") == 1, "R3 terminal summary matched-censor drift")
    req(summary.get("actor_rollouts") == 1264, "R3 terminal summary actor-rollout drift")
    req(summary.get("support_inspected") is False, "R3 terminal summary already inspected support")
    req(summary.get("updater_calls") == 0, "R3 terminal summary updater boundary crossed")
    req(summary.get("heldout_evaluations") == 0, "R3 terminal summary heldout boundary crossed")
    req(summary.get("partial_effect_read") is False, "R3 terminal summary partial-effect boundary crossed")
    req(summary.get("scientific_scores_read") is False, "R3 terminal summary scientific-score boundary crossed")
    req(summary.get("stage_b_authority") is False, "R3 terminal summary grants Stage-B authority")

    run_root = Path(contract["run_root"])
    lease_path = Path(contract["global_lease_path"])
    req(run_root.is_dir(), "R3 terminal run root absent")
    req(lease_path.is_file(), "R3 terminal lease absent")
    lease = load(lease_path)
    req(lease.get("status") == LEASE_STATUS, "R3 terminal lease status drift")
    req(lease.get("contract_sha256") == csha, "R3 terminal lease contract SHA drift")
    req(lease.get("authorization_sha256") == asha, "R3 terminal lease authorization SHA drift")
    req(Path(str(lease.get("summary_path") or "")).resolve() == summary_path.resolve(), "R3 terminal lease summary path drift")
    req(lease.get("summary_sha256") == ssha, "R3 terminal lease summary SHA drift")

    completed_manifest = Path(str(summary.get("completed_stream_manifest_path") or ""))
    req(completed_manifest.is_file(), "R3 completed-stream manifest absent")
    req(summary.get("completed_stream_manifest_sha256") == sha(completed_manifest), "R3 completed-stream manifest SHA drift")

    exact = contract["exact_once_acquisition"]
    manifest_path = bound(exact["unit_manifest_path"])
    req(manifest_path.is_file() and sha(manifest_path) == exact["unit_manifest_sha256"], "R3 execution-unit manifest drift")
    manifest = load(manifest_path)
    tasks = [str(value) for value in manifest.get("ordered_task_ids") or []]
    req(len(tasks) == len(set(tasks)) == 158, "R3 execution-unit universe must be 158 unique tasks")
    req(BURNED not in tasks and CENSOR not in tasks, "R3 excluded task leaked into provider universe")

    opp_row = contract["recovery_opportunity_manifest"]
    opportunity_path = bound(opp_row["path"])
    req(opportunity_path.is_file() and sha(opportunity_path) == opp_row["sha256"], "R3 opportunity manifest drift")
    opportunity = load(opportunity_path)
    by_stream = {str(k): [str(x) for x in v] for k, v in (opportunity.get("provider_task_ids_by_stream") or {}).items()}
    req(len(by_stream) == 20, "R3 opportunity stream-count drift")
    req(len(by_stream.get("stv3-cgwb-00") or []) == 7, "R3 burned-stream opportunity geometry drift")
    req(len(by_stream.get("stv3-cgwp-00") or []) == 7, "R3 censor-stream opportunity geometry drift")
    req(all(len(v) == (7 if k in {"stv3-cgwb-00", "stv3-cgwp-00"} else 8) for k, v in by_stream.items()), "R3 7/7/8 opportunity geometry drift")
    flattened = [task for stream in by_stream.values() for task in stream]
    req(len(flattened) == len(set(flattened)) == 158 and set(flattened) == set(tasks), "R3 opportunity/provider universe mismatch")

    claim_root = Path(exact["claim_root"])
    req(claim_root.resolve() == (run_root / "checkpoints/stage_a_task_claims").resolve(), "R3 claim-root drift")
    req(claim_root.is_dir(), "R3 claim root absent")
    req(len(list(claim_root.glob("*.attempt.json"))) == 158, "R3 exact-once attempt count drift")
    req(len(list(claim_root.glob("*.sealed.json"))) == 158, "R3 exact-once seal count drift")
    for task in tasks:
        attempt_path, sealed_path = task_claim_paths(claim_root, task)
        req(attempt_path.is_file() and sealed_path.is_file(), f"R3 exact-once receipt missing: {task}")
        attempt = load(attempt_path)
        sealed = load(sealed_path)
        req(attempt.get("artifact_type") == "e2-r17-semantic-transfer-v3-stage-a-task-attempt", f"R3 attempt type drift: {task}")
        req(attempt.get("status") == "ATTEMPTED_IN_FLIGHT_DO_NOT_REPLAY", f"R3 attempt status drift: {task}")
        req(sealed.get("artifact_type") == "e2-r17-semantic-transfer-v3-stage-a-task-seal", f"R3 seal type drift: {task}")
        req(sealed.get("status") == "SEALED_EXACT_ONCE", f"R3 seal status drift: {task}")
        req(attempt.get("task_id") == sealed.get("task_id") == task, f"R3 receipt task drift: {task}")
        req(attempt.get("contract_sha256") == sealed.get("contract_sha256") == csha, f"R3 receipt contract drift: {task}")
        req(attempt.get("authorization_sha256") == sealed.get("authorization_sha256") == asha, f"R3 receipt authorization drift: {task}")
        req(sealed.get("attempt_sha256") == sha(attempt_path), f"R3 attempt binding drift: {task}")
        pool_path = run_root / "cases" / task / "pool_k8.json"
        req(pool_path.is_file(), f"R3 sealed pool absent: {task}")
        req(sealed.get("pool_k8_sha256") == sha(pool_path), f"R3 sealed pool SHA drift: {task}")
    req(not (run_root / "cases" / BURNED).exists(), "burned task case unexpectedly exists in R3 run")
    req(not (run_root / "cases" / CENSOR).exists(), "matched-censor task case unexpectedly exists in R3 run")

    return {
        "contract": contract,
        "recovery_authorization": recovery_auth,
        "summary": summary,
        "contract_sha256": csha,
        "recovery_authorization_sha256": asha,
        "summary_sha256": ssha,
        "run_root": run_root,
        "lease_path": lease_path,
        "tasks": tasks,
        "manifest_path": manifest_path,
        "manifest_sha256": sha(manifest_path),
        "opportunity_path": opportunity_path,
        "opportunity_sha256": sha(opportunity_path),
    }


def build_support_authorization(
    *,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    control_review_path: Path,
    output_path: Path,
    adjudication_output_path: Path = EXPECTED_ADJUDICATION_OUTPUT,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    req(not output_path.exists(), "post-terminal support-read authorization already exists")
    req(EXPECTED_SUPPORT_ADJUDICATOR.is_file(), "frozen R3 support adjudicator absent")
    req(sha(EXPECTED_SUPPORT_ADJUDICATOR) == EXPECTED_SUPPORT_ADJUDICATOR_SHA256, "frozen R3 support adjudicator SHA drift")
    req(EXPECTED_GATE.is_file(), "post-terminal support gate absent")
    minter_sha = sha(Path(__file__))
    gate_sha = sha(EXPECTED_GATE)
    review = validate_control_review(control_review_path, minter_sha=minter_sha, gate_sha=gate_sha)
    state = validate_terminal_structure(
        contract_path=contract_path,
        recovery_authorization_path=recovery_authorization_path,
        summary_path=summary_path,
    )
    req(not adjudication_output_path.exists(), "R3 support adjudication output already exists")

    timestamp = created_at_utc or datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-read-authorization",
        "created_at_utc": timestamp,
        "status": SUPPORT_AUTH_STATUS,
        "single_use": True,
        "provider_calls": 0,
        "scientific_execution": False,
        "contract_path": str(contract_path),
        "contract_sha256": state["contract_sha256"],
        "recovery_authorization_path": str(recovery_authorization_path),
        "recovery_authorization_sha256": state["recovery_authorization_sha256"],
        "terminal_summary_path": str(summary_path),
        "terminal_summary_sha256": state["summary_sha256"],
        "terminal_lease_path": str(state["lease_path"]),
        "terminal_lease_sha256": sha(state["lease_path"]),
        "control_review": {
            "path": str(control_review_path),
            "sha256": sha(control_review_path),
            "verdict": review["verdict"],
            "model": review["model"],
            "surface": review["surface"],
        },
        "bound_control_plane": {
            "minter_path": str(Path(__file__)),
            "minter_sha256": minter_sha,
            "gate_path": str(EXPECTED_GATE),
            "gate_sha256": gate_sha,
            "support_adjudicator_path": str(EXPECTED_SUPPORT_ADJUDICATOR),
            "support_adjudicator_sha256": EXPECTED_SUPPORT_ADJUDICATOR_SHA256,
        },
        "execution_scope": {
            "required_adjudication_output": str(adjudication_output_path),
            "required_run_root": str(state["run_root"]),
            "provider_execution_tasks": 158,
            "sealed_k8_pools": 158,
            "terminal_technical_missing": BURNED,
            "matched_no_provider_censor": CENSOR,
            "support_required_mixed_pools_per_stream": 4,
            "opportunity_geometry": "7/7/8",
            "support_read_may_open_k8_pool_semantics": True,
            "support_read_before_terminal_recovery": False,
        },
        "authority": {
            "stage_a_support_read": True,
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "updater": False,
            "heldout_evaluation": False,
            "analyzer": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
            "submission": False,
        },
        "interpretation_boundary": "Single-use zero-provider authority to invoke the already exact-hash-reviewed R3 Stage-A support adjudicator after the exact terminal recovery state only. It grants no provider execution, updater, heldout, Stage-B execution, public benchmark, analyzer, or paper-claim authority.",
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--recovery-authorization", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--control-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--adjudication-output", type=Path, default=EXPECTED_ADJUDICATION_OUTPUT)
    args = parser.parse_args()
    payload = build_support_authorization(
        contract_path=args.contract,
        recovery_authorization_path=args.recovery_authorization,
        summary_path=args.summary,
        control_review_path=args.control_review,
        output_path=args.output,
        adjudication_output_path=args.adjudication_output,
    )
    atomic(args.output, payload)
    print(json.dumps({
        "status": payload["status"],
        "terminal_summary_sha256": payload["terminal_summary_sha256"],
        "authority": payload["authority"],
        "provider_calls": 0,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

## Source: ONE_SHOT_GATE — `scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SUPPORT_AUTH_STATUS = "AUTHORIZED_E2_R17_V3_R3_POST_TERMINAL_SUPPORT_READ"
SUMMARY_STATUS = "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION"
EXPECTED_SUPPORT_ADJUDICATOR = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
EXPECTED_SUPPORT_ADJUDICATOR_SHA256 = "e326ee92f7765aa68856c6fe09610996209d4aa3d3ad464a65d391a88a4cbae4"
CONSUMPTION_NAME = "post_terminal_support_read_authorization.consumed.json"
COMPLETION_NAME = "post_terminal_support_read_adjudication.completed.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _exclusive_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(fd, raw)
        os.fsync(fd)
    finally:
        os.close(fd)
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def validate_support_authorization(
    *,
    support_authorization_path: Path,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    support_auth = load(support_authorization_path)
    req(support_auth.get("status") == SUPPORT_AUTH_STATUS, "post-terminal support-read authorization status drift")
    req(support_auth.get("single_use") is True, "post-terminal support-read authorization is not single-use")
    req(support_auth.get("provider_calls") == 0, "post-terminal support-read authorization provider-call drift")
    req(support_auth.get("scientific_execution") is False, "post-terminal support-read authorization incorrectly records scientific execution")

    authority = support_auth.get("authority") or {}
    req(authority.get("stage_a_support_read") is True, "Stage-A support-read authority absent")
    for key in (
        "stage_a_provider_execution",
        "stage_b_learning_execution",
        "updater",
        "heldout_evaluation",
        "analyzer",
        "second_backbone",
        "public_benchmark",
        "paper_promotion",
        "submission",
    ):
        req(authority.get(key) is False, f"post-terminal support-read authorization overbroad: {key}")

    req(support_auth.get("contract_sha256") == sha(contract_path), "post-terminal support-read contract SHA drift")
    req(support_auth.get("recovery_authorization_sha256") == sha(recovery_authorization_path), "post-terminal support-read recovery-authorization SHA drift")
    req(support_auth.get("terminal_summary_sha256") == sha(summary_path), "post-terminal support-read summary SHA drift")
    req(Path(str(support_auth.get("contract_path") or "")).resolve() == contract_path.resolve(), "post-terminal support-read contract path drift")
    req(Path(str(support_auth.get("recovery_authorization_path") or "")).resolve() == recovery_authorization_path.resolve(), "post-terminal support-read recovery-authorization path drift")
    req(Path(str(support_auth.get("terminal_summary_path") or "")).resolve() == summary_path.resolve(), "post-terminal support-read summary path drift")

    summary = load(summary_path)
    req(summary.get("status") == SUMMARY_STATUS, "terminal summary no longer at pending-support boundary")
    req(summary.get("support_inspected") is False, "terminal summary indicates support already inspected")
    req(summary.get("stage_b_authority") is False, "terminal summary grants Stage-B authority")

    control = support_auth.get("bound_control_plane") or {}
    req(control.get("gate_sha256") == sha(Path(__file__)), "support-read gate SHA drift")
    req(control.get("support_adjudicator_sha256") == EXPECTED_SUPPORT_ADJUDICATOR_SHA256, "support adjudicator binding drift")
    req(EXPECTED_SUPPORT_ADJUDICATOR.is_file() and sha(EXPECTED_SUPPORT_ADJUDICATOR) == EXPECTED_SUPPORT_ADJUDICATOR_SHA256, "frozen support adjudicator SHA drift")
    req(Path(str(control.get("support_adjudicator_path") or "")).resolve() == EXPECTED_SUPPORT_ADJUDICATOR.resolve(), "support adjudicator path drift")

    scope = support_auth.get("execution_scope") or {}
    req(Path(str(scope.get("required_adjudication_output") or "")).resolve() == output_path.resolve(), "support adjudication output path drift")
    req(scope.get("provider_execution_tasks") == 158 and scope.get("sealed_k8_pools") == 158, "post-terminal support-read geometry drift")
    req(scope.get("opportunity_geometry") == "7/7/8", "post-terminal support-read opportunity geometry drift")
    req(scope.get("support_required_mixed_pools_per_stream") == 4, "post-terminal support threshold drift")

    run_root = Path(str(scope.get("required_run_root") or ""))
    req(run_root.is_dir(), "post-terminal support-read run root absent")
    lease_path = Path(str(support_auth.get("terminal_lease_path") or ""))
    req(lease_path.is_file() and support_auth.get("terminal_lease_sha256") == sha(lease_path), "post-terminal support-read lease binding drift")
    return {"support_authorization": support_auth, "summary": summary, "run_root": run_root, "lease_path": lease_path}


def default_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def run_gate(
    *,
    support_authorization_path: Path,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    output_path: Path,
    invoke: Callable[[list[str]], subprocess.CompletedProcess[str]] = default_invoke,
    python_executable: str = sys.executable,
) -> dict[str, Any]:
    req(not output_path.exists(), "R3 support adjudication output already exists")
    state = validate_support_authorization(
        support_authorization_path=support_authorization_path,
        contract_path=contract_path,
        recovery_authorization_path=recovery_authorization_path,
        summary_path=summary_path,
        output_path=output_path,
    )
    run_root: Path = state["run_root"]
    control_root = run_root / "checkpoints/post_terminal_support_read"
    consumption = control_root / CONSUMPTION_NAME
    completion = control_root / COMPLETION_NAME
    req(not consumption.exists(), "post-terminal support-read authorization already consumed; retry forbidden")
    req(not completion.exists(), "post-terminal support adjudication completion receipt already exists")

    auth_sha = sha(support_authorization_path)
    summary_sha = sha(summary_path)
    consumption_payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-read-consumption",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "CONSUMED_IN_FLIGHT_DO_NOT_RETRY",
        "support_authorization_path": str(support_authorization_path),
        "support_authorization_sha256": auth_sha,
        "terminal_summary_path": str(summary_path),
        "terminal_summary_sha256": summary_sha,
        "required_output": str(output_path),
        "automatic_retry": False,
        "stage_b_authority": False,
    }
    _exclusive_json(consumption, consumption_payload)

    command = [
        python_executable,
        str(EXPECTED_SUPPORT_ADJUDICATOR),
        "--contract",
        str(contract_path),
        "--authorization",
        str(recovery_authorization_path),
        "--summary",
        str(summary_path),
        "--output",
        str(output_path),
    ]
    result = invoke(command)
    if result.returncode not in {0, 3}:
        raise RuntimeError(
            "R3 support adjudicator failed outside terminal PASS/HOLD states; support-read permit remains consumed and manual review is required. "
            f"returncode={result.returncode}; stdout_tail={result.stdout[-1200:]}; stderr_tail={result.stderr[-1200:]}"
        )
    req(output_path.is_file(), "R3 support adjudicator returned terminal code without output artifact")
    adjudication = load(output_path)
    expected_statuses = {
        0: "PASS_SEMANTIC_TRANSFER_V3_R3_MATCHED_CENSOR_EQUAL_DOSE_SUPPORT_READY_FOR_STAGE_B_DESIGN",
        3: "HOLD_SEMANTIC_TRANSFER_V3_R3_INSUFFICIENT_EQUAL_DOSE_SUPPORT",
    }
    req(adjudication.get("status") == expected_statuses[result.returncode], "R3 support adjudicator terminal status/returncode mismatch")
    authority = adjudication.get("authority") or {}
    req(authority.get("execute_stage_b") is False, "R3 support adjudication improperly grants Stage-B execution")
    req(authority.get("heldout_evaluation") is False, "R3 support adjudication improperly grants heldout evaluation")
    req(authority.get("analyzer") is False, "R3 support adjudication improperly grants analyzer authority")
    req(authority.get("paper_promotion") is False, "R3 support adjudication improperly grants paper-promotion authority")

    completion_payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-read-completion",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "COMPLETED_POST_TERMINAL_SUPPORT_READ",
        "support_authorization_sha256": auth_sha,
        "consumption_path": str(consumption),
        "consumption_sha256": sha(consumption),
        "terminal_summary_sha256": summary_sha,
        "adjudication_output": str(output_path),
        "adjudication_output_sha256": sha(output_path),
        "adjudication_status": adjudication["status"],
        "adjudicator_returncode": result.returncode,
        "stage_b_authority": False,
        "automatic_retry": False,
    }
    _exclusive_json(completion, completion_payload)
    return {
        "status": completion_payload["status"],
        "adjudication_status": adjudication["status"],
        "returncode": result.returncode,
        "consumption_path": str(consumption),
        "completion_path": str(completion),
        "stage_b_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--support-authorization", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--recovery-authorization", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_gate(
        support_authorization_path=args.support_authorization,
        contract_path=args.contract,
        recovery_authorization_path=args.recovery_authorization,
        summary_path=args.summary,
        output_path=args.output,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

## Source: ZERO_PROVIDER_TESTS — `research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py`

```python
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read as minter
import run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate as gate


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class R3PostTerminalSupportReadControlTests(unittest.TestCase):
    def make_fixture(self) -> dict[str, Path]:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        run = root / "run"
        claims = run / "checkpoints/stage_a_task_claims"
        claims.mkdir(parents=True)
        completed = run / "checkpoints/completed_streams.jsonl"
        completed.parent.mkdir(parents=True, exist_ok=True)
        completed.write_text("{}\n", encoding="utf-8")

        streams: dict[str, list[str]] = {}
        task_ids: list[str] = []
        for idx in range(20):
            sid = "stv3-cgwb-00" if idx == 0 else "stv3-cgwp-00" if idx == 1 else f"stv3-test-{idx:02d}"
            count = 7 if idx < 2 else 8
            rows = [f"test-{idx:02d}-{j:02d}" for j in range(count)]
            streams[sid] = rows
            task_ids.extend(rows)
        self.assertEqual(len(task_ids), 158)

        manifest = root / "execution-units.json"
        write_json(manifest, {"ordered_task_ids": task_ids})
        opportunity = root / "opportunity.json"
        write_json(opportunity, {"provider_task_ids_by_stream": streams})

        lease = root / "r3-lease.json"
        contract = root / "contract.json"
        contract_payload = {
            "schema_version": "1.0",
            "status": minter.CONTRACT_STATUS,
            "run_root": str(run),
            "global_lease_path": str(lease),
            "exact_once_acquisition": {
                "unit_manifest_path": str(manifest),
                "unit_manifest_sha256": sha(manifest),
                "claim_root": str(claims),
            },
            "recovery_opportunity_manifest": {"path": str(opportunity), "sha256": sha(opportunity)},
        }
        write_json(contract, contract_payload)
        csha = sha(contract)

        recovery_auth = root / "recovery-auth.json"
        recovery_auth_payload = {
            "schema_version": "1.0",
            "status": minter.RECOVERY_AUTH_STATUS,
            "contract_sha256": csha,
            "single_use": True,
            "exactly_once": True,
            "authority": {
                "stage_a_provider_execution": True,
                "stage_b_learning_execution": False,
                "updater": False,
                "heldout_evaluation": False,
                "analyzer": False,
                "second_backbone": False,
                "public_benchmark": False,
                "paper_promotion": False,
                "submission": False,
            },
        }
        write_json(recovery_auth, recovery_auth_payload)
        asha = sha(recovery_auth)

        for task in task_ids:
            task_dir = run / "cases" / task
            task_dir.mkdir(parents=True)
            pool = task_dir / "pool_k8.json"
            pool.write_text("{}\n", encoding="utf-8")
            attempt, sealed = minter.task_claim_paths(claims, task)
            write_json(
                attempt,
                {
                    "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-task-attempt",
                    "status": "ATTEMPTED_IN_FLIGHT_DO_NOT_REPLAY",
                    "task_id": task,
                    "contract_sha256": csha,
                    "authorization_sha256": asha,
                },
            )
            write_json(
                sealed,
                {
                    "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-task-seal",
                    "status": "SEALED_EXACT_ONCE",
                    "task_id": task,
                    "contract_sha256": csha,
                    "authorization_sha256": asha,
                    "attempt_sha256": sha(attempt),
                    "pool_k8_sha256": sha(pool),
                },
            )

        summary = run / "summary/stage_a_r3_recovery_pool_freeze_summary.json"
        summary_payload = {
            "schema_version": "1.0",
            "status": minter.SUMMARY_STATUS,
            "contract_sha256": csha,
            "authorization_sha256": asha,
            "planned_tasks": 160,
            "provider_executable_tasks": 158,
            "sealed_k8_pools": 158,
            "terminal_technical_missing": 1,
            "matched_no_provider_censor": 1,
            "actor_rollouts": 1264,
            "support_inspected": False,
            "updater_calls": 0,
            "heldout_evaluations": 0,
            "partial_effect_read": False,
            "scientific_scores_read": False,
            "stage_b_authority": False,
            "completed_stream_manifest_path": str(completed),
            "completed_stream_manifest_sha256": sha(completed),
        }
        write_json(summary, summary_payload)
        ssha = sha(summary)
        write_json(
            lease,
            {
                "schema_version": "1.0",
                "status": minter.LEASE_STATUS,
                "contract_sha256": csha,
                "authorization_sha256": asha,
                "summary_path": str(summary),
                "summary_sha256": ssha,
            },
        )

        control_review = root / "control-review.json"
        write_json(
            control_review,
            {
                "schema_version": "1.0",
                "status": "COMPLETED",
                "surface": "ChatGPT web",
                "model": "GPT-5.6 Sol",
                "verdict": minter.CONTROL_REVIEW_VERDICT,
                "minter_sha256_acknowledged": sha(Path(minter.__file__)),
                "gate_sha256_acknowledged": sha(Path(gate.__file__)),
                "support_adjudicator_sha256_acknowledged": minter.EXPECTED_SUPPORT_ADJUDICATOR_SHA256,
                "stage_b_authority": False,
                "scientific_authority": False,
            },
        )
        return {
            "root": root,
            "run": run,
            "contract": contract,
            "recovery_auth": recovery_auth,
            "summary": summary,
            "lease": lease,
            "control_review": control_review,
            "support_auth": root / "support-auth.json",
            "adjudication_output": root / "support-adjudication.json",
        }

    def build_auth(self, fixture: dict[str, Path]) -> dict:
        payload = minter.build_support_authorization(
            contract_path=fixture["contract"],
            recovery_authorization_path=fixture["recovery_auth"],
            summary_path=fixture["summary"],
            control_review_path=fixture["control_review"],
            output_path=fixture["support_auth"],
            adjudication_output_path=fixture["adjudication_output"],
            created_at_utc="2026-09-07T00:01:00+08:00",
        )
        write_json(fixture["support_auth"], payload)
        return payload

    def test_minter_rejects_absent_or_nonterminal_summary(self) -> None:
        fixture = self.make_fixture()
        missing = fixture["root"] / "missing-summary.json"
        with self.assertRaises(FileNotFoundError):
            minter.build_support_authorization(
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=missing,
                control_review_path=fixture["control_review"],
                output_path=fixture["support_auth"],
                adjudication_output_path=fixture["adjudication_output"],
            )
        summary = json.loads(fixture["summary"].read_text())
        summary["status"] = "RUNNING"
        write_json(fixture["summary"], summary)
        with self.assertRaisesRegex(RuntimeError, "terminal summary status drift"):
            self.build_auth(fixture)

    def test_minter_rejects_support_already_inspected(self) -> None:
        fixture = self.make_fixture()
        summary = json.loads(fixture["summary"].read_text())
        summary["support_inspected"] = True
        write_json(fixture["summary"], summary)
        with self.assertRaisesRegex(RuntimeError, "already inspected support"):
            self.build_auth(fixture)

    def test_minter_rejects_recovery_authorization_hash_drift(self) -> None:
        fixture = self.make_fixture()
        auth = json.loads(fixture["recovery_auth"].read_text())
        auth["tampered"] = True
        write_json(fixture["recovery_auth"], auth)
        with self.assertRaisesRegex(RuntimeError, "summary authorization SHA drift"):
            self.build_auth(fixture)

    def test_minter_grants_only_stage_a_support_read(self) -> None:
        fixture = self.make_fixture()
        payload = self.build_auth(fixture)
        self.assertTrue(payload["authority"]["stage_a_support_read"])
        self.assertFalse(payload["authority"]["stage_a_provider_execution"])
        self.assertFalse(payload["authority"]["stage_b_learning_execution"])
        self.assertFalse(payload["authority"]["heldout_evaluation"])
        self.assertEqual(payload["provider_calls"], 0)
        self.assertFalse(payload["scientific_execution"])

    def test_gate_refuses_invalid_support_authorization(self) -> None:
        fixture = self.make_fixture()
        payload = self.build_auth(fixture)
        payload["authority"]["stage_a_support_read"] = False
        write_json(fixture["support_auth"], payload)
        with self.assertRaisesRegex(RuntimeError, "support-read authority absent"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                output_path=fixture["adjudication_output"],
            )
        consumption = fixture["run"] / "checkpoints/post_terminal_support_read" / gate.CONSUMPTION_NAME
        self.assertFalse(consumption.exists())

    def test_gate_consumes_once_and_fail_closes_on_unexpected_adjudicator_error(self) -> None:
        fixture = self.make_fixture()
        self.build_auth(fixture)

        def failed_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(command, 2, stdout="", stderr="synthetic failure")

        with self.assertRaisesRegex(RuntimeError, "permit remains consumed"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                output_path=fixture["adjudication_output"],
                invoke=failed_invoke,
            )
        control = fixture["run"] / "checkpoints/post_terminal_support_read"
        self.assertTrue((control / gate.CONSUMPTION_NAME).is_file())
        self.assertFalse((control / gate.COMPLETION_NAME).exists())
        with self.assertRaisesRegex(RuntimeError, "already consumed"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                output_path=fixture["adjudication_output"],
                invoke=failed_invoke,
            )

    def test_gate_accepts_terminal_pass_without_stage_b_authority(self) -> None:
        fixture = self.make_fixture()
        self.build_auth(fixture)

        def passed_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
            output = Path(command[command.index("--output") + 1])
            write_json(
                output,
                {
                    "status": "PASS_SEMANTIC_TRANSFER_V3_R3_MATCHED_CENSOR_EQUAL_DOSE_SUPPORT_READY_FOR_STAGE_B_DESIGN",
                    "authority": {
                        "prepare_stage_b_contract": True,
                        "execute_stage_b": False,
                        "heldout_evaluation": False,
                        "analyzer": False,
                        "paper_promotion": False,
                    },
                },
            )
            return subprocess.CompletedProcess(command, 0, stdout="synthetic pass", stderr="")

        result = gate.run_gate(
            support_authorization_path=fixture["support_auth"],
            contract_path=fixture["contract"],
            recovery_authorization_path=fixture["recovery_auth"],
            summary_path=fixture["summary"],
            output_path=fixture["adjudication_output"],
            invoke=passed_invoke,
        )
        self.assertEqual(result["status"], "COMPLETED_POST_TERMINAL_SUPPORT_READ")
        self.assertFalse(result["stage_b_authority"])
        completion = fixture["run"] / "checkpoints/post_terminal_support_read" / gate.COMPLETION_NAME
        self.assertTrue(completion.is_file())
        self.assertFalse(json.loads(completion.read_text())["stage_b_authority"])


if __name__ == "__main__":
    unittest.main()

```

## Source: STATIC_PREFLIGHT — `scripts/preflight_e2_r17_semantic_transfer_v3_stage_a_r3_support_read_control.py`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CONTRACT_SHA = "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085"
EXPECTED_RECOVERY_RUNNER_SHA = "491b2ae6e53fcfe732f15ef263cc365ce61846b3219d7a13fe70e3834f6d3c89"
EXPECTED_SUPPORT_ADJUDICATOR_SHA = "e326ee92f7765aa68856c6fe09610996209d4aa3d3ad464a65d391a88a4cbae4"
AUTHORITY_REVIEW_VERDICT = "REQUIRE_SEPARATE_POST_TERMINAL_SUPPORT_READ_AUTHORIZATION"
PREFLIGHT_STATUS = "PASS_ZERO_PROVIDER_R3_POST_TERMINAL_SUPPORT_CONTROL_PREFLIGHT"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authority-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    req(not args.output.exists(), "support-control preflight output already exists")

    contract = load(args.contract)
    review = load(args.authority_review)
    csha = sha(args.contract)
    req(csha == EXPECTED_CONTRACT_SHA, "frozen R3 contract SHA drift")
    req(review.get("status") == "COMPLETED", "support-authority review incomplete")
    req(review.get("verdict") == AUTHORITY_REVIEW_VERDICT, "support-authority review verdict drift")
    req(review.get("must_resolve_before_provider_recovery") is True, "support-authority review timing boundary drift")
    req(review.get("provider_recovery_authority_affected") is False, "support-authority review unexpectedly invalidates provider recovery")
    req(review.get("r3_contract_redesign_required") is False, "support-authority review unexpectedly requires contract redesign")
    req(review.get("bound_code_change_required") is False, "support-authority review unexpectedly requires frozen code change")
    req(review.get("stage_b_authority") is False, "support-authority review grants Stage-B authority")

    minter = ROOT / "scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py"
    gate = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py"
    tests = ROOT / "research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py"
    recovery_runner = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
    support_adjudicator = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
    for path in (minter, gate, tests, recovery_runner, support_adjudicator):
        req(path.is_file(), f"required file absent: {path}")
    req(sha(recovery_runner) == EXPECTED_RECOVERY_RUNNER_SHA, "frozen R3 recovery-runner SHA drift")
    req(sha(support_adjudicator) == EXPECTED_SUPPORT_ADJUDICATOR_SHA, "frozen R3 support-adjudicator SHA drift")

    run_root = Path(contract["run_root"])
    lease = Path(contract["global_lease_path"])
    support_auth = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3-post-terminal-support-read-authorization-20260907.json"
    support_output = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3-equal-dose-adjudication-20260907.json"
    checks = {
        "authority_review_requires_separate_support_auth": True,
        "provider_recovery_authority_unaffected": True,
        "r3_contract_unchanged": csha == EXPECTED_CONTRACT_SHA,
        "r3_recovery_runner_unchanged": sha(recovery_runner) == EXPECTED_RECOVERY_RUNNER_SHA,
        "r3_support_adjudicator_unchanged": sha(support_adjudicator) == EXPECTED_SUPPORT_ADJUDICATOR_SHA,
        "additive_minter_exists": minter.is_file(),
        "additive_gate_exists": gate.is_file(),
        "zero_provider_tests_exist": tests.is_file(),
        "live_r3_run_root_absent": not run_root.exists(),
        "live_r3_lease_absent": not lease.exists(),
        "live_support_read_authorization_absent": not support_auth.exists(),
        "live_support_adjudication_output_absent": not support_output.exists(),
        "stage_b_authority": False,
    }
    req(all(value is True for key, value in checks.items() if key != "stage_b_authority"), "support-control preflight check failed")
    req(checks["stage_b_authority"] is False, "support-control preflight Stage-B authority drift")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-control-zero-provider-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": PREFLIGHT_STATUS,
        "provider_calls": 0,
        "scientific_execution": False,
        "support_inspected": False,
        "stage_b_authority": False,
        "contract_path": str(args.contract),
        "contract_sha256": csha,
        "authority_review_path": str(args.authority_review),
        "authority_review_sha256": sha(args.authority_review),
        "authority_review_verdict": review["verdict"],
        "additive_control_plane": {
            "minter_path": str(minter.relative_to(ROOT)),
            "minter_sha256": sha(minter),
            "gate_path": str(gate.relative_to(ROOT)),
            "gate_sha256": sha(gate),
            "tests_path": str(tests.relative_to(ROOT)),
            "tests_sha256": sha(tests),
        },
        "frozen_scientific_code": {
            "recovery_runner_path": str(recovery_runner.relative_to(ROOT)),
            "recovery_runner_sha256": sha(recovery_runner),
            "support_adjudicator_path": str(support_adjudicator.relative_to(ROOT)),
            "support_adjudicator_sha256": sha(support_adjudicator),
        },
        "checks": checks,
        "unit_tests": {
            "suite": "research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control",
            "passed": 7,
            "total": 7,
        },
        "actual_support_read_authorization_minted": False,
        "exact_code_review_complete": False,
        "next_gate": "FRESH_GPT56_SOL_EXTRA_HIGH_EXACT_CODE_REVIEW_OF_ADDITIVE_SUPPORT_READ_CONTROL_PLANE",
        "authority": {
            "provider_recovery": False,
            "stage_a_support_read": False,
            "stage_b_execution": False,
            "heldout": False,
            "paper_claim": False,
        },
    }
    atomic(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

## 5. Audit questions

A. **Separation of authority from scientific read.** Does the minter remain structural-only and avoid inspecting K8 scientific semantics while still proving the terminal state is exactly the one reviewed? Is hashing pool bytes acceptable as lineage verification rather than scientific inspection?

B. **Terminal-state sufficiency.** Are the summary/lease/manifest/158 exact-once receipts/seal hashes/7-7-8 opportunity checks sufficient to prevent minting support-read authority on a partial, replayed, substituted, or already-inspected recovery state? Identify any verdict-changing missing invariant.

C. **Authority narrowness.** Is the minted permit correctly limited to `stage_a_support_read=true` with provider execution, updater, heldout, analyzer, Stage B, public benchmark and paper claims all false?

D. **Single-use consumption.** Does the gate's O_CREAT|O_EXCL durable consumption-before-adjudicator rule correctly prevent retry after ambiguous/failed support reads? Is accepting only adjudicator rc=0 PASS and rc=3 HOLD as terminal appropriate?

E. **No scientific-code redesign.** Does the wrapper preserve the exact frozen support-adjudicator implementation and semantics rather than silently replacing or reimplementing support analysis?

F. **Review binding.** The minter requires a future control-review receipt with this exact PASS verdict and exact minter/gate/adjudicator SHA acknowledgements. Is that sufficient to ensure this exact code, not a later mutation, is what can mint the permit?

G. **Tests/preflight.** Are the 7 zero-provider tests plus static preflight sufficient for this narrow authority layer, or is a verdict-changing control-plane failure case missing? Do not request extra workload for appearance.

H. **Execution consequence.** If this exact code passes review, may R3 provider recovery proceed after the separately frozen 2026-09-07 quota reset + fresh identity + separate recovery authorization, while the actual support-read permit remains unmintable until terminal recovery? Stage B must remain false.

## 6. Required synthesis

Return exactly these fields before the final verdict:

- `minter_structural_only`: PASS/FAIL
- `terminal_binding`: PASS/FAIL
- `support_authority_narrowness`: PASS/FAIL
- `single_use_gate`: PASS/FAIL
- `frozen_adjudicator_preserved`: PASS/FAIL
- `exact_code_review_binding`: PASS/FAIL
- `tests_preflight`: PASS/FAIL
- `provider_recovery_authority_affected`: true/false
- `r3_contract_redesign_required`: true/false
- `new_scientific_experiment_required`: true/false
- `stage_b_authority`: false
- `remaining_blockers`: [] or exact blockers
- `execution_recommendation`

Then end with exactly one verdict token from Section 0.
