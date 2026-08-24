from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from .research_execution_kernel import SCHEMA_VERSION, canonical_sha256, validate_experiment_manifest


def _overlaps(left: str, right: str) -> bool:
    a = Path(left).as_posix().rstrip("/") or "/"
    b = Path(right).as_posix().rstrip("/") or "/"
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def build_research_sandbox_contract(
    *, readable_paths: Iterable[str], writable_paths: Iterable[str], executable_tools: Iterable[str],
    forbidden_tools: Iterable[str] | None = None, evaluator_paths: Iterable[str] | None = None,
    secret_paths: Iterable[str] | None = None, network_mode: str = "deny",
    network_allowlist: Iterable[str] | None = None, gpu_budget: dict[str, Any] | None = None,
    api_budget: dict[str, Any] | None = None, wallclock_budget: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = {
        "schema_version": SCHEMA_VERSION, "readable_paths": [str(v) for v in readable_paths],
        "writable_paths": [str(v) for v in writable_paths], "executable_tools": [str(v) for v in executable_tools],
        "forbidden_tools": [str(v) for v in (forbidden_tools or [])],
        "evaluator_paths": [str(v) for v in (evaluator_paths or [])], "secret_paths": [str(v) for v in (secret_paths or [])],
        "network_mode": str(network_mode), "network_allowlist": [str(v) for v in (network_allowlist or [])],
        "gpu_budget": dict(gpu_budget or {}), "api_budget": dict(api_budget or {}), "wallclock_budget": dict(wallclock_budget or {}),
        "evaluator_mutation_allowed": False, "secret_mutation_allowed": False,
        "capability_escalation_allowed": False, "scientific_authority": False,
    }
    contract["contract_sha256"] = canonical_sha256(contract)
    contract["validation"] = validate_research_sandbox_contract(contract)
    return contract


def validate_research_sandbox_contract(contract: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    writable = [str(v) for v in contract.get("writable_paths") or []]
    evaluator = [str(v) for v in contract.get("evaluator_paths") or []]
    secrets = [str(v) for v in contract.get("secret_paths") or []]
    if any(_overlaps(w, p) for w in writable for p in evaluator): blockers.append("executor-write-overlaps-evaluator-surface")
    if any(_overlaps(w, p) for w in writable for p in secrets): blockers.append("executor-write-overlaps-secret-surface")
    if str(contract.get("network_mode") or "") not in {"deny", "allowlist"}: blockers.append("network-mode-must-be-deny-or-allowlist")
    if contract.get("network_mode") == "allowlist" and not contract.get("network_allowlist"): blockers.append("network-allowlist-empty")
    if set(contract.get("executable_tools") or []) & set(contract.get("forbidden_tools") or []): blockers.append("tool-listed-as-both-executable-and-forbidden")
    if any(contract.get(key) is not False for key in ("evaluator_mutation_allowed", "secret_mutation_allowed", "capability_escalation_allowed")):
        blockers.append("sandbox-privilege-escalation-forbidden")
    if contract.get("scientific_authority") is not False: blockers.append("sandbox-cannot-grant-scientific-authority")
    raw = {key: value for key, value in contract.items() if key not in {"contract_sha256", "validation"}}
    if str(contract.get("contract_sha256") or "") and contract.get("contract_sha256") != canonical_sha256(raw): blockers.append("sandbox-contract-digest-mismatch")
    return {"status": "PASS" if not blockers else "BLOCK", "passed": not blockers, "blockers": blockers, "scientific_authority": False}


def build_execution_job(manifest: dict[str, Any], *, planner_actor: str, phase: str, authority_ref: str = "") -> dict[str, Any]:
    audit = validate_experiment_manifest(manifest)
    if not audit["passed"]: raise ValueError("invalid experiment manifest:" + ",".join(audit["blockers"]))
    if phase not in {"smoke", "pilot", "full"}: raise ValueError(f"unknown phase:{phase}")
    job = {
        "schema_version": SCHEMA_VERSION, "experiment_id": manifest["experiment_id"],
        "research_item_code": manifest["research_item_code"], "planner_actor": str(planner_actor), "phase": phase,
        "authority_ref": str(authority_ref), "manifest_contract_sha256": manifest["contract_sha256"],
        "execution_identity_sha256": manifest["execution_identity_sha256"],
        "scientific_contract": dict(manifest["scientific_contract"]),
        "scientific_contract_sha256": manifest["scientific_contract_sha256"], "unit_ids": list(manifest["unit_ids"]),
        "executor_may_change_scientific_contract": False, "job_has_scientific_authority": False,
    }
    job["job_sha256"] = canonical_sha256(job); return job


def validate_executor_receipt(job: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    if receipt.get("job_sha256") != job.get("job_sha256"): blockers.append("executor-receipt-job-digest-mismatch")
    if receipt.get("execution_identity_sha256") != job.get("execution_identity_sha256"): blockers.append("executor-receipt-execution-identity-mismatch")
    if receipt.get("scientific_contract_sha256") != job.get("scientific_contract_sha256"): blockers.append("executor-receipt-scientific-contract-mismatch")
    if receipt.get("scientific_contract") is not None and receipt.get("scientific_contract") != job.get("scientific_contract"):
        blockers.append("executor-attempted-scientific-contract-mutation")
    if receipt.get("scientific_validity_pass") is True: blockers.append("executor-cannot-self-acquit-scientific-validity")
    if receipt.get("scientific_authority") not in (None, False): blockers.append("executor-receipt-cannot-grant-scientific-authority")
    return {"status": "PASS" if not blockers else "BLOCK", "passed": not blockers, "blockers": blockers, "scientific_authority": False}
