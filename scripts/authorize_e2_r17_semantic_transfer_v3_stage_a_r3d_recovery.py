#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_r3d_runtime_replay_attestation import verify_document as verify_runtime_replay_attestation

CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
CONTROL_PLANE_REVISION = "R3D_PINNED_EXTERNAL_SIGNED_SUPPORT_CAPABILITY"
PREFLIGHT_STATUS = "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_R3D_PINNED_SUPPORT_CAPABILITY_PREFLIGHT"
R3D_REVIEW_VERDICT = "PASS_TO_SEPARATE_R3_RECOVERY_AUTHORIZATION"
R3D_EXECUTION_RECOMMENDATION = "ALLOW_SEPARATE_R3D_RECOVERY_AUTHORIZATION_AFTER_RESET_AND_FRESH_IDENTITY"
ADAPTER_REVIEW_VERDICT = "PASS_R3D_RECOVERY_AUTHORIZATION_ADAPTER"
AUTH_STATUS = "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY"
HARD_PROVIDER_NOT_BEFORE = "2026-09-07T00:00:00+08:00"
EXPECTED_CONTRACT_SHA256 = "21f7a50f4e14f48a139ecfa122f7c8a443d4195a1ade0267ccececcb6e424717"
EXPECTED_PREFLIGHT_SHA256 = "8894bf0e76d4f1b0a8f101ca55df0ff8728696bc29bf888e6287ab2046c724fa"
EXPECTED_R3D_REVIEW_SHA256 = "f97071244451d8e0f7ea1d30f31689948e03858665eeed983802670d38a522fb"
EXPECTED_PROVIDER_RUNNER_SHA256 = "491b2ae6e53fcfe732f15ef263cc365ce61846b3219d7a13fe70e3834f6d3c89"
RUNTIME_REPLAY_STATUS = "PASS_R3D_RECOVERY_AUTHORIZATION_ADAPTER_FROZEN_RUNTIME_REPLAY"
ADAPTER_TEST_PATH = ROOT / "research_pipeline/test_e2_r17_semantic_transfer_v3_r3d_recovery_authorization_adapter.py"
RUNTIME_REPLAY_TOOL_PATH = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3d_adapter_runtime_replay.py"
RUNTIME_REPLAY_ATTESTATION_VERIFIER_PATH = ROOT / "research_pipeline/e2_r17_r3d_runtime_replay_attestation.py"
PROVIDER_RUNNER_PATH = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
PRODUCTION_RUNTIME_REPLAY_PUBLIC_KEY_PATH = ROOT / "generated/e2-r17-r3d-host69-runtime-replay-public-key-20260906.pem"
PRODUCTION_RUNTIME_REPLAY_PUBLIC_KEY_SHA256 = "cc454f52d82b28c7eb33e0f938d3328b65427b3192d1a4992e96333298c1f270"
EXPECTED_RUNTIME_REPLAY_HOSTNAME = "ubuntu"
EXPECTED_RUNTIME_REPLAY_IPV4 = "222.20.126.69"
BURNED = "r17-b21-cgwb-p0"
CENSOR = "r17-b21-cgwp-p0"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def bound(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def build_authorization(
    *,
    contract_path: Path,
    preflight_path: Path,
    r3d_review_path: Path,
    adapter_review_path: Path,
    runtime_replay_path: Path,
    fresh_identity_path: Path,
    output_path: Path,
    now: datetime | None = None,
) -> dict[str, Any]:
    req(not output_path.exists(), "R3D recovery authorization already exists")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    hard_gate = _parse_time(HARD_PROVIDER_NOT_BEFORE)
    req(current >= hard_gate, "R3D hard provider reset boundary not reached")

    contract = load(contract_path)
    preflight = load(preflight_path)
    review = load(r3d_review_path)
    adapter_review = load(adapter_review_path)
    runtime_replay_document = load(runtime_replay_path)
    identity = load(fresh_identity_path)
    csha = sha(contract_path)
    psha = sha(preflight_path)
    rsha = sha(r3d_review_path)
    adapter_sha = sha(Path(__file__))
    test_sha = sha(ADAPTER_TEST_PATH)
    runner_sha = sha(PROVIDER_RUNNER_PATH)
    replay_tool_sha = sha(RUNTIME_REPLAY_TOOL_PATH)
    replay_attestation_verifier_sha = sha(RUNTIME_REPLAY_ATTESTATION_VERIFIER_PATH)

    req(csha == EXPECTED_CONTRACT_SHA256, "R3D contract SHA drift")
    req(contract.get("status") == CONTRACT_STATUS, "R3D contract not frozen")
    req(contract.get("control_plane_revision") == CONTROL_PLANE_REVISION, "R3D control-plane revision drift")
    req(psha == EXPECTED_PREFLIGHT_SHA256, "R3D preflight SHA drift")
    req(preflight.get("status") == PREFLIGHT_STATUS and preflight.get("contract_sha256") == csha, "R3D preflight not passing/bound")
    req(preflight.get("provider_calls") == 0 and preflight.get("scientific_execution") is False and preflight.get("support_inspected") is False, "R3D preflight crossed scientific boundary")
    req(preflight.get("stage_b_authority") is False, "R3D preflight grants Stage B")
    for key in (
        "all_bound_code_hashes_match",
        "fresh_r3d_recovery_lineage_absent",
        "point_of_use_production_trust_root_pinned",
        "provider_recovery_runner_and_authorizer_unchanged",
        "signed_capability_absent",
        "substituted_contract_attacker_key_full_chain_negative_test_present",
        "support_control_tests_10_of_10_pass",
    ):
        req((preflight.get("checks") or {}).get(key) is True, f"R3D preflight check missing: {key}")

    req(rsha == EXPECTED_R3D_REVIEW_SHA256, "R3D accepted review receipt SHA drift")
    req(review.get("status", "").startswith("COMPLETED"), "R3D independent review not completed")
    req(review.get("surface") == "ChatGPT web" and review.get("model") == "GPT-5.6 Sol", "R3D independent review provenance drift")
    req(review.get("verdict") == R3D_REVIEW_VERDICT, "R3D independent review did not PASS")
    req(review.get("execution_recommendation") == R3D_EXECUTION_RECOMMENDATION, "R3D review execution recommendation drift")
    req(review.get("contract_sha256_acknowledged") == csha, "R3D review contract SHA drift")
    req(review.get("preflight_sha256_acknowledged") == psha, "R3D review preflight SHA drift")
    req(review.get("remaining_blockers") == [], "R3D review has remaining blockers")
    req(review.get("stage_b_authority") is False and review.get("scientific_authority") is False, "R3D review authority overbroad")

    req(adapter_review.get("status") == "COMPLETED", "R3D authorization-adapter review not completed")
    req(adapter_review.get("surface") == "ChatGPT web" and adapter_review.get("model") == "GPT-5.6 Sol", "R3D adapter review provenance drift")
    req(adapter_review.get("verdict") == ADAPTER_REVIEW_VERDICT, "R3D authorization adapter not independently PASSed")
    req(adapter_review.get("adapter_sha256_acknowledged") == adapter_sha, "R3D adapter review code SHA drift")
    req(adapter_review.get("contract_sha256_acknowledged") == csha, "R3D adapter review contract SHA drift")
    req(adapter_review.get("preflight_sha256_acknowledged") == psha, "R3D adapter review preflight SHA drift")
    req(adapter_review.get("r3d_review_sha256_acknowledged") == rsha, "R3D adapter review upstream review SHA drift")
    req(adapter_review.get("runtime_replay_attestation_verifier_sha256_acknowledged") == replay_attestation_verifier_sha, "R3D adapter review runtime-replay verifier SHA drift")
    req(adapter_review.get("runtime_replay_public_key_sha256_acknowledged") == PRODUCTION_RUNTIME_REPLAY_PUBLIC_KEY_SHA256, "R3D adapter review runtime-replay public-key SHA drift")
    req(adapter_review.get("provider_authority_only") is True, "R3D adapter review does not bound provider-only authority")
    req(adapter_review.get("stage_b_authority") is False and adapter_review.get("scientific_authority") is False, "R3D adapter review authority overbroad")
    req(adapter_review.get("remaining_blockers") == [], "R3D adapter review has remaining blockers")

    req(runner_sha == EXPECTED_PROVIDER_RUNNER_SHA256, "R3D provider runner SHA drift")
    expected_runtime_replay = {
        "status": RUNTIME_REPLAY_STATUS,
        "execution_host_role": "HOST69_FROZEN_RUNTIME",
        "execution_host_origin": "HOST69_LOCAL_ED25519_PRIVATE_KEY",
        "hostname": EXPECTED_RUNTIME_REPLAY_HOSTNAME,
        "execution_host_ipv4": EXPECTED_RUNTIME_REPLAY_IPV4,
        "python_executable": contract["runtime"]["python_executable"],
        "python_freeze_sha256": contract["runtime"]["freeze_sha256"],
        "contract_sha256": csha,
        "preflight_sha256": psha,
        "r3d_review_sha256": rsha,
        "adapter_sha256": adapter_sha,
        "adapter_tests_sha256": test_sha,
        "provider_runner_sha256": runner_sha,
        "runtime_replay_tool_sha256": replay_tool_sha,
        "host69_public_key_sha256": PRODUCTION_RUNTIME_REPLAY_PUBLIC_KEY_SHA256,
        "compile_pass": True,
        "unit_tests_pass": True,
        "unit_tests_failed": 0,
        "provider_calls": 0,
        "scientific_execution": False,
        "support_inspected": False,
        "stage_b_authority": False,
    }
    runtime_replay = verify_runtime_replay_attestation(
        runtime_replay_document,
        public_key_path=PRODUCTION_RUNTIME_REPLAY_PUBLIC_KEY_PATH,
        expected_public_key_sha256=PRODUCTION_RUNTIME_REPLAY_PUBLIC_KEY_SHA256,
        expected_payload_fields=expected_runtime_replay,
    )

    req(identity.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "fresh R3D identity not passing")
    row = (identity.get("requested_and_resolved") or {}).get("deepseek-v4-pro") or {}
    req(row.get("resolved") == "deepseek-v4-pro-ga-260813", "fresh R3D resolved model drift")
    req(row.get("thinking") == "disabled" and int(row.get("provider_retry_limit", -1)) == 0, "fresh R3D identity execution policy drift")
    identity_time = _parse_time(str(identity.get("created_at_utc") or ""))
    req(identity_time >= hard_gate, "fresh R3D identity predates hard provider reset")

    exact = contract["exact_once_acquisition"]
    manifest_path = bound(exact["unit_manifest_path"])
    req(manifest_path.is_file() and sha(manifest_path) == exact["unit_manifest_sha256"], "R3D provider manifest drift")
    tasks = [str(x) for x in load(manifest_path)["ordered_task_ids"]]
    req(len(tasks) == len(set(tasks)) == 158, "R3D provider universe must be 158 unique tasks")
    req(BURNED not in tasks and CENSOR not in tasks, "R3D excluded task leaked into provider universe")
    opportunity_row = contract["recovery_opportunity_manifest"]
    opportunity_path = bound(opportunity_row["path"])
    req(opportunity_path.is_file() and sha(opportunity_path) == opportunity_row["sha256"], "R3D opportunity manifest drift")
    opportunity = load(opportunity_path)
    streams = {str(k): [str(x) for x in v] for k, v in opportunity["provider_task_ids_by_stream"].items()}
    req(len(streams) == 20, "R3D opportunity stream-count drift")
    req(len(streams["stv3-cgwb-00"]) == 7 and len(streams["stv3-cgwp-00"]) == 7, "R3D matched 7/7 geometry drift")
    req(all(len(v) == (7 if k in {"stv3-cgwb-00", "stv3-cgwp-00"} else 8) for k, v in streams.items()), "R3D 7/7/8 geometry drift")
    req(not Path(contract["run_root"]).exists() and not Path(contract["global_lease_path"]).exists(), "R3D recovery lineage already exists")

    authority = {
        "stage_a_provider_execution": True,
        "stage_b_learning_execution": False,
        "updater": False,
        "heldout_evaluation": False,
        "analyzer": False,
        "second_backbone": False,
        "public_benchmark": False,
        "paper_promotion": False,
        "submission": False,
    }
    identity_sha = sha(fresh_identity_path)
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-r3d-recovery-authorization",
        "created_at_utc": current.isoformat(timespec="seconds"),
        "status": AUTH_STATUS,
        "contract_path": str(contract_path),
        "contract_sha256": csha,
        "preflight_path": str(preflight_path),
        "preflight_sha256": psha,
        "r3d_independent_review": {"path": str(r3d_review_path), "sha256": rsha, "verdict": review["verdict"]},
        "authorization_adapter_review": {"path": str(adapter_review_path), "sha256": sha(adapter_review_path), "verdict": adapter_review["verdict"], "adapter_sha256": adapter_sha},
        "frozen_runtime_replay": {"path": str(runtime_replay_path), "sha256": sha(runtime_replay_path), "status": runtime_replay["status"], "execution_host_role": runtime_replay["execution_host_role"], "execution_host_origin": runtime_replay["execution_host_origin"], "hostname": runtime_replay["hostname"], "execution_host_ipv4": runtime_replay["execution_host_ipv4"], "python_executable": runtime_replay["python_executable"], "adapter_sha256": adapter_sha, "adapter_tests_sha256": test_sha, "provider_runner_sha256": runner_sha, "runtime_replay_tool_sha256": replay_tool_sha, "attestation_verifier_sha256": replay_attestation_verifier_sha, "trusted_public_key_sha256": PRODUCTION_RUNTIME_REPLAY_PUBLIC_KEY_SHA256},
        "fresh_model_identity": {"path": str(fresh_identity_path), "sha256": identity_sha, "status": identity["status"], "created_at_utc": identity["created_at_utc"], "requested_model": "deepseek-v4-pro", "resolved_model": row["resolved"]},
        "single_use": True,
        "exactly_once": True,
        "automatic_retry": False,
        "authority": authority,
        "execution_scope": {
            "recovery_mode": "MATCHED_CENSOR_158",
            "allowed_modes": ["e1"],
            "allowed_task_ids": tasks,
            "exact_k": 8,
            "exact_prefix_ks": [1, 2, 4, 8],
            "exact_concurrency": contract["actor"]["concurrency"],
            "required_run_root": contract["run_root"],
            "runner_lease_required": True,
            "allow_noninitial_skill": False,
            "required_skill_pre_sha256": contract["mindmemos"]["initial_skill_sha256"],
            "required_resolved_model": "deepseek-v4-pro-ga-260813",
            "identity_artifact_sha256": identity_sha,
            "suite_manifest_sha256": contract["suite"]["suite_manifest_sha256"],
            "split_manifest_sha256": contract["suite"]["split_manifest_sha256"],
            "max_turns": contract["actor"]["max_turns"],
            "max_output_tokens": contract["actor"]["max_output_tokens"],
            "provider_budget": {"required": True, "total_limit": contract["budget"]["max_provider_calls"], "per_unit_limit": contract["budget"]["provider_calls_per_rollout_limit"]},
            "exact_once_acquisition": {"required": True, "unit_manifest_path": exact["unit_manifest_path"], "unit_manifest_sha256": exact["unit_manifest_sha256"], "unit_count": 158, "required_claim_root": exact["claim_root"], "attempt_before_any_provider_io": True, "replay_allowed": False, "ambiguous_recollection_allowed": False},
            "global_lease_path": contract["global_lease_path"],
            "recovery_exceptions": {"terminal_technical_missing": BURNED, "matched_no_provider_censor": CENSOR, "matched_censor_provider_calls": 0, "replacement_allowed": False, "additional_attempted_but_unsealed_policy": "STOP"},
        },
        "interpretation_boundary": "Single-use authority adapter for the frozen R3D 158-task Stage-A matched-censor recovery only. It grants no support read, updater, heldout, Stage B, public benchmark, analyzer, or paper claim. The adapter changes authorization schema compatibility only; provider runner and scientific geometry remain frozen.",
    }
    return payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--preflight", type=Path, required=True)
    ap.add_argument("--r3d-review", type=Path, required=True)
    ap.add_argument("--adapter-review", type=Path, required=True)
    ap.add_argument("--runtime-replay", type=Path, required=True)
    ap.add_argument("--fresh-identity", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    payload = build_authorization(
        contract_path=args.contract,
        preflight_path=args.preflight,
        r3d_review_path=args.r3d_review,
        adapter_review_path=args.adapter_review,
        runtime_replay_path=args.runtime_replay,
        fresh_identity_path=args.fresh_identity,
        output_path=args.output,
    )
    atomic(args.output, payload)
    print(json.dumps({"status": payload["status"], "allowed_tasks": len(payload["execution_scope"]["allowed_task_ids"]), "authority": payload["authority"], "provider_calls": 0}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
