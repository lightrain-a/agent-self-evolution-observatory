#!/usr/bin/env python3
"""Freeze B1 MemRL G5 preregistration and fail closed on runtime support.

R40 is strictly zero-outcome: it does not invoke an LLM, embedder, LLB task,
evaluator, browser, or GPU. It freezes the confirmatory estimands/arms/stopping
rules prospectively and records whether the current host can even satisfy the
container runtime prerequisite. G6 remains false regardless of G5 status.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
R39 = Path("generated/d2-failure-memory-provenance-r39-memrl-substrate-audit.json")
PSMG = Path("generated/d2-failure-memory-provenance-psmg-method-design-r27.json")
OUT = Path("generated/d2-failure-memory-provenance-r40-memrl-g5-preflight.json")
PINNED_MEMRL_SHA = "c1b322ca43de36ddf64c6712f89d0095bfc35ce0"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return p.returncode, p.stdout.strip()


def probe_runtime(memrl_repo: Path) -> dict:
    repo_ok = (memrl_repo / ".git").exists()
    commit = None
    clean = False
    if repo_ok:
        rc, out = _run(["git", "rev-parse", "HEAD"], memrl_repo)
        commit = out if rc == 0 else None
        rc, out = _run(["git", "status", "--porcelain"], memrl_repo)
        clean = rc == 0 and out == ""

    required = [
        "configs/rl_llb_config.yaml",
        "run/run_llb.py",
        "memrl/run/llb_rl_runner.py",
        "data/llb/os_interaction_train.json",
        "data/llb/os_interaction_val.json",
        "data/llb/db_train.json",
        "data/llb/db_val.json",
    ]
    files_present = {x: (memrl_repo / x).is_file() for x in required}
    docker_rc, docker_out = _run(["docker", "version", "--format", "{{.Server.Version}}"])
    docker_server_available = docker_rc == 0 and bool(docker_out)

    return {
        "memrl_repo": str(memrl_repo),
        "repo_present": repo_ok,
        "pinned_commit_expected": PINNED_MEMRL_SHA,
        "commit_observed": commit,
        "commit_matches": commit == PINNED_MEMRL_SHA,
        "checkout_clean": clean,
        "required_files_present": files_present,
        "all_required_files_present": all(files_present.values()),
        "docker_server_available": docker_server_available,
        "docker_probe_exit_code": docker_rc,
        "docker_probe_output": docker_out[:500],
        "model_calls": 0,
        "environment_actions": 0,
        "evaluator_calls": 0,
        "treatment_outcomes_observed": 0,
    }


def build(runtime: dict) -> dict:
    r39 = _load(R39)
    psmg = _load(PSMG)
    if r39["gate_adjudication"]["passed_stages_now"] != [
        "G1_RELEASE", "G2_PROVENANCE_SCHEMA", "G3_EXACT_INFORMATION", "G4_FRESH_CAPACITY"
    ]:
        raise RuntimeError("R39 G1-G4 qualification drift")
    if r39["authority"]["experiment"]:
        raise RuntimeError("R39 unexpectedly grants experiment authority")
    if psmg["method"]["short_name"] != "PSMG" or psmg["authority"]["experiment"]:
        raise RuntimeError("PSMG design/authority drift")

    static_support = bool(
        runtime["repo_present"]
        and runtime["commit_matches"]
        and runtime["checkout_clean"]
        and runtime["all_required_files_present"]
    )
    runtime_support = bool(static_support and runtime["docker_server_available"])

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R40-MEMRL-G5-PREFLIGHT",
        "recorded_date": "2026-08-25",
        "status": (
            "MEMRL_G5_PREREG_FROZEN_RUNTIME_SUPPORT_BLOCKED_NO_EXECUTION_AUTHORITY"
            if not runtime_support
            else "MEMRL_G5_STATIC_RUNTIME_PREREQUISITES_PRESENT_SUPPORT_SMOKE_STILL_REQUIRED_NO_EXECUTION_AUTHORITY"
        ),
        "role": "ZERO_OUTCOME_G5_PREREGISTRATION_AND_RUNTIME_PREFLIGHT",
        "scientific_relationship": "POST_R39_G5_ONLY_NOT_R19_RESUME_NOT_CONFIRMATORY_EVIDENCE",
        "parent_bindings": {
            "memrl_g1_g4": {"path": str(R39), "sha256": _sha(R39)},
            "psmg_design": {"path": str(PSMG), "sha256": _sha(PSMG)},
        },
        "frozen_confirmatory_contract": {
            "substrate": "MemRL pinned at c1b322ca43de36ddf64c6712f89d0095bfc35ce0",
            "primary_surface": "LifelongAgentBench OSInteraction validation split",
            "secondary_surface": "DBBench validation split; replication only, not required to declare the primary endpoint",
            "source_build": {
                "source_split": "pinned public OSInteraction train split",
                "future_split": "pinned public OSInteraction validation split",
                "source_future_overlap_policy": "task IDs and exact/normalized instruction/script collisions must remain zero as frozen in R39",
                "qualification_gate": [
                    "source build must finish without support retries after scientific exposure begins",
                    "both metadata.success polarities must exist among retrievable source memories",
                    "at least 32 prospectively defined validation dependency clusters must retain at least one eligible frozen retrieval",
                    "retrieval for every analyzed unit must be frozen before arm projection",
                    "failure of any qualification item yields SUPPORT_STOP_NO_VERDICT and no treatment outcomes may be interpreted",
                ],
            },
            "arms": {
                "A_content_only": "frozen retrieved actionable content; source-outcome provenance hidden from executor",
                "B_raw_provenance": "identical frozen actionable content plus truthful metadata.success projected only as source_outcome_success",
                "C_PSMG": "provenance available only to a prospectively frozen governance controller; executor receives governance-approved actionable content without raw provenance label",
                "D_nonprovenance_controller": "same pre-outcome content/relevance/verification/utility information as C except the provenance variable under test",
            },
            "identification_estimand": "paired terminal success difference B_raw_provenance - A_content_only conditional on identical frozen retrieval",
            "governance_estimand": "paired terminal success difference C_PSMG - D_nonprovenance_controller under matched pre-outcome information",
            "primary_endpoint": "native LLB terminal task success",
            "secondary_endpoints": ["steps to terminal completion among valid episodes", "support/retrieval coverage diagnostics"],
            "inference_unit": "prospectively frozen exact skill_list-signature dependency cluster within OSInteraction validation",
            "minimum_reference_independent_units": 32,
            "randomization": "within eligible future unit, arm order generated from fixed seed 20260825 after unit eligibility/retrieval freeze and before any treatment outcome",
            "exclusions": [
                "pre-treatment source-build/support qualification failure",
                "missing/non-boolean source provenance on a selected memory",
                "retrieval mismatch across arms",
                "actionable-content byte mismatch across A/B or controller-information mismatch across C/D",
                "environment/evaluator failure before a valid terminal score",
            ],
            "missingness": "no outcome imputation; support failures remain support debt. A post-exposure infrastructure failure stops the affected confirmatory attempt and forbids ad-hoc retry unless a retry class was prospectively enumerated before exposure.",
            "multiplicity": "A-vs-B identification and C-vs-D governance are distinct estimands; no pooling. OSInteraction is primary; DBBench is labeled replication. No endpoint substitution after outcomes.",
            "interval_and_test_rule": "report paired cluster-level effect with 95% interval and a prospectively fixed randomization/permutation test; effect magnitude and interval are primary, p-value cannot upgrade a rung by itself",
            "effect_relevance_floor": 0.15,
            "no_interim_inference": True,
            "no_optional_stopping_on_effect": True,
            "R19_partial_outcomes_used_for_design": False,
            "same_asset_27_used": False,
        },
        "runtime_preflight": runtime,
        "G5_adjudication": {
            "preregistration_contract_frozen": True,
            "static_pinned_source_support": static_support,
            "container_runtime_available_on_current_host": runtime["docker_server_available"],
            "non_outcome_environment_support_smoke_completed": False,
            "passed_now": False,
            "state": (
                "BLOCKED_CURRENT_HOST_DOCKER_DAEMON_UNAVAILABLE"
                if not runtime["docker_server_available"]
                else "PARTIAL_RUNTIME_PREREQUISITES_PRESENT_STILL_NEEDS_ZERO_OUTCOME_ENVIRONMENT_SUPPORT_SMOKE"
            ),
            "why_not_pass": (
                "LifelongAgentBench OS/DB requires containerized environments; current host cannot reach a Docker server."
                if not runtime["docker_server_available"]
                else "A prospectively bounded non-outcome reset/evaluator support smoke has not yet been completed."
            ),
        },
        "gate_adjudication": {
            "G1_RELEASE": True,
            "G2_PROVENANCE_SCHEMA": True,
            "G3_EXACT_INFORMATION": True,
            "G4_FRESH_CAPACITY": True,
            "G5_SUPPORT_AND_PREREGISTRATION": False,
            "G6_AUTHORITY": False,
            "gate_pass_now": False,
            "next_blocking_stage": "G5_RUNTIME_SUPPORT",
            "qualified_for_confirmatory_execution_now": None,
        },
        "candidate_disposition": {
            "MemRL": "KEEP_AS_FIRST_G1_G4_QUALIFIED_CANDIDATE_G5_PREREG_FROZEN_RUNTIME_SUPPORT_BLOCKED",
            "R19": "REMAINS_STOPPED",
            "same_asset_27": "REMAINS_NON_CONFIRMATORY_INVENTORY",
            "RoMeRL": "REMAINS_G4_STOP",
        },
        "claim_policy": {
            "new_scientific_behavioral_result": False,
            "provenance_only_causal_sign_updated": False,
            "PSMG_efficacy_updated": False,
            "paper_claim_expansion_allowed": False,
            "confirmatory_execution_authorized": False,
        },
        "authority": {
            "scientific_execution": False,
            "experiment": False,
            "model_calls": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "gpu": False,
            "claim_expansion": False,
            "submission": False,
        },
        "next_action": "MOVE_ONLY_THE_ZERO_OUTCOME_G5_RUNTIME_SUPPORT_PREFLIGHT_TO_A_DOCKER_CAPABLE_HOST_WITHOUT_CHANGING_THE_FROZEN_CONTRACT",
        "scientific_verdict": "NO_VERDICT_G5_PREREGISTRATION_ADVANCES_BUT_CURRENT_HOST_SUPPORT_DOES_NOT_PASS",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--memrl-repo", type=Path, required=True)
    args = ap.parse_args()
    runtime = probe_runtime(args.memrl_repo.resolve())
    payload = build(runtime)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "G5": payload["G5_adjudication"]["state"],
        "experiment_authority": payload["authority"]["experiment"],
        "model_calls": payload["runtime_preflight"]["model_calls"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
