from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
PRIMARY_REF = "arXiv:2608.13040"
PARENT_CLOSURE_ID = "LOPD-LATENT-RETRIEVAL-PLATEAU"
CANDIDATE_ID = "LOPD-FIXED-BUDGET-LATENT-EXPERIENCE-DECOMPOSITION"
EXPECTED_RELEASE_COMMIT = "362d3742fc7b4dbbc0677b219990f2a4b4d0a90f"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object:{path}")
    return payload


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def _remote_head(root: Path) -> str:
    text = subprocess.check_output(["git", "-C", str(root), "ls-remote", "origin", "HEAD"], text=True, timeout=30).strip()
    match = re.match(r"^([0-9a-f]{40})\s+HEAD$", text)
    if not match:
        raise ValueError(f"unexpected LOPD ls-remote output:{text[:160]}")
    return match.group(1)


def _parse_inference_config(text: str) -> dict[str, Any]:
    num_queries_match = re.search(r"(?m)^\s*num_queries:\s*(\d+)\s*$", text)
    checkpoint_match = re.search(r"(?m)^\s*checkpoint:\s*([^#\n]+?)\s*$", text)
    retrieve_match = re.search(r"(?m)^\s*n_retrieve:\s*(\d+)\s*$", text)
    if not num_queries_match or not checkpoint_match or not retrieve_match:
        raise ValueError("LOPD inference config no longer exposes expected qformer/inference fields")
    return {
        "qformer_num_queries": int(num_queries_match.group(1)),
        "compressor_checkpoint": checkpoint_match.group(1).strip(),
        "n_retrieve": int(retrieve_match.group(1)),
    }


def build_hold(
    *,
    repo_root: Path,
    prior_preflight_path: Path,
    parent_closure_path: Path,
    remote_head: str,
) -> dict[str, Any]:
    local_head = _git(repo_root, "rev-parse", "HEAD")
    origin = _git(repo_root, "remote", "get-url", "origin")
    readme_path = repo_root / "README.md"
    config_path = repo_root / "configs/inference/envscaler/envscaler_latent_eval200_qwen3_4b.yaml"
    qformer_path = repo_root / "memory/qformer.py"
    bank_path = repo_root / "memory/bank.py"
    for path in (readme_path, config_path, qformer_path, bank_path):
        if not path.exists():
            raise FileNotFoundError(path)
    readme = readme_path.read_text(encoding="utf-8", errors="replace")
    config_text = config_path.read_text(encoding="utf-8", errors="replace")
    parsed = _parse_inference_config(config_text)
    training_code_pending = bool(re.search(r"Training code coming soon", readme, re.IGNORECASE))
    placeholder_checkpoint = parsed["compressor_checkpoint"] == "YOUR_COMPRESSOR_CHECKPOINT"

    prior = _load(prior_preflight_path)
    receipts = [row for row in prior.get("receipts") or [] if isinstance(row, dict) and row.get("disposition") == "SOURCE_SPECIFIC_REQUIRED"]
    if not receipts:
        raise ValueError("LOPD source-specific preflight receipt missing")
    prior_receipt = receipts[0]

    parent = _load(parent_closure_path)
    parent_counter = ((parent.get("principle_diagnosis") or {}).get("counter_explanation") or {})
    if (
        parent.get("candidate_id") != PARENT_CLOSURE_ID
        or parent.get("principle_dead_end_certified") is not True
        or parent_counter.get("same_information_reduction_verified") is not True
    ):
        raise ValueError("LOPD parent principle closure missing or drifted")

    arms = [
        {"experience_count_J": 1, "latent_tokens_per_experience_K": 64},
        {"experience_count_J": 2, "latent_tokens_per_experience_K": 32},
        {"experience_count_J": 4, "latent_tokens_per_experience_K": 16},
        {"experience_count_J": 8, "latent_tokens_per_experience_K": 8},
    ]
    for arm in arms:
        arm["total_latent_positions_JxK"] = arm["experience_count_J"] * arm["latent_tokens_per_experience_K"]

    release_unchanged = local_head == remote_head == EXPECTED_RELEASE_COMMIT
    source_faithful_execution_available = bool(
        not training_code_pending
        and not placeholder_checkpoint
        and local_head == remote_head
    )
    required_unit = "source-faithful fixed-J*K LOPD training/evaluation arms that independently vary experience count J and latent tokens per experience K while matching total latent positions, retrieval support, compute, and update information"
    reopen = "Reopen when the official/source-specific training pipeline and compatible compressor artifacts become available with enough provenance to train or reproduce all fixed-budget decomposition arms under matched compute/update information, or when an independent review certifies an equivalent operationalization without changing the frozen causal unit, prediction, or strongest same-information baselines."
    hold_signature = hashlib.sha256(json.dumps({
        "candidate_id": CANDIDATE_ID,
        "required_unit": required_unit,
        "source_ref": PRIMARY_REF,
        "release_commit": remote_head,
    }, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]

    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": CANDIDATE_ID,
        "parent_closure_id": PARENT_CLOSURE_ID,
        "primary_ref": PRIMARY_REF,
        "title": "Does latent-experience decomposition matter after fixing the total latent-position budget?",
        "frozen_problem": {
            "causal_unit": "one LOPD task/example under one frozen experience bank and retrieval ranking",
            "intervention": "redistribute a fixed total latent-position budget between number of retrieved experiences J and latent tokens per experience K",
            "total_latent_positions": 64,
            "arms": arms,
            "frozen_controls": [
                "same base/student/self-teacher model identities",
                "same frozen successful-trajectory experience bank",
                "same similarity ranking and retrieval support",
                "same task distribution and evaluation endpoint",
                "same composer family and privileged-margin objective",
                "matched training/update information and compute",
            ],
            "strongest_same_information_baselines": [
                "rate-distortion / representation-capacity model at fixed total latent positions",
                "marginal nonredundant-information model using retrieval rank and experience similarity/correlation",
                "context-budget model using the same total latent positions and training/update compute",
            ],
            "frozen_exact_prediction": "If experience-count versus per-experience-capacity decomposition is a distinct mechanism, then at fixed J*K=64 and matched training/update information, held-out outcomes will differ repeatably across decomposition arms in a way that the same-information rate-distortion, marginal-information/redundancy, retrieval-rank, and context-budget baselines cannot express.",
            "stop_rule": "If decomposition effects are explained by the same-information capacity/redundancy/rank/context baselines, retain the parent LOPD principle closure and do not claim a new mechanism.",
        },
        "release_audit": {
            "official_repository": origin,
            "local_head": local_head,
            "remote_head": remote_head,
            "expected_initial_release_commit": EXPECTED_RELEASE_COMMIT,
            "release_unchanged_since_initial_code_release": release_unchanged,
            "readme_sha256": _sha(readme_path),
            "inference_config_sha256": _sha(config_path),
            "qformer_sha256": _sha(qformer_path),
            "memory_bank_sha256": _sha(bank_path),
            "readme_training_code_coming_soon": training_code_pending,
            "qformer_num_queries": parsed["qformer_num_queries"],
            "compressor_checkpoint_config": parsed["compressor_checkpoint"],
            "compressor_checkpoint_is_placeholder": placeholder_checkpoint,
            "inference_n_retrieve": parsed["n_retrieve"],
            "hf_checkpoint_inventory_status": "UNVERIFIED_NON_LOAD_BEARING",
            "hf_checkpoint_inventory_note": "A Hugging Face file-list probe timed out and is not used as evidence of absence. The current hold is load-bearing on the unchanged official Git release, the explicit 'Training code coming soon' statement, and the source config requiring a compressor checkpoint. Even a K=32 checkpoint alone would not instantiate the K=8/16/64 matched training objects source-faithfully.",
        },
        "prior_source_specific_receipt": {
            "artifact_sha256": _sha(prior_preflight_path),
            "candidate_id": prior_receipt.get("candidate_id"),
            "contract_sha256": prior_receipt.get("contract_sha256"),
            "disposition": prior_receipt.get("disposition"),
            "reason": prior_receipt.get("reason"),
        },
        "support_diagnosis": {
            "status": "WAIT_PRIMARY_ASSET_RELEASE",
            "support_status": "SOURCE_SPECIFIC_PRIMARY_ASSET_UNAVAILABLE",
            "stop_class": "SUPPORT_STOP",
            "failure_layer": "experiment_identifiability",
            "failure_subtype": "SOURCE_SPECIFIC_TRAINING_OBJECT_UNAVAILABLE",
            "source_faithful_execution_available": source_faithful_execution_available,
            "principle_dead_end_certified": False,
            "principle_update_allowed": False,
            "reason": "The fixed-budget child requires source-faithful trained compressor conditions at multiple K values while matching the LOPD training/update object. The official repository remains at its initial release, still states that training code is coming soon, and the released inference configuration fixes qformer.num_queries=32 while requiring a placeholder compressor checkpoint. Changing K locally would therefore change or invent the training object rather than execute the frozen scientific contrast.",
            "reopen_only_if": reopen,
            "next_action": "Keep the fixed-budget decomposition contract as a reopenable source-asset hold. Do not substitute a random, locally invented, differently trained, or outcome-tuned compressor and do not authorize GPU execution until the source-specific dependency is resolved.",
        },
        "memory_projection": {
            "memory_class": "REOPENABLE_HOLD",
            "dead_end_certified": False,
            "hold_origin": "bounded-evidence-acquisition",
            "required_unit": required_unit,
        },
        "persistent_hold": {
            "source_candidate_id": CANDIDATE_ID,
            "basin": f"near-miss-terminal-support-hold-{hold_signature}",
            "title": "Does latent-experience decomposition matter after fixing the total latent-position budget?",
            "disposition": "HOLD_SUPPORT_UNAVAILABLE",
            "support_status": "SOURCE_SPECIFIC_PRIMARY_ASSET_UNAVAILABLE",
            "stop_class": "SUPPORT_STOP",
            "failure_layer": "experiment_identifiability",
            "failure_subtype": "SOURCE_SPECIFIC_TRAINING_OBJECT_UNAVAILABLE",
            "memory_class": "REOPENABLE_HOLD",
            "dead_end_certified": False,
            "required_unit": required_unit,
            "evidence_basis": [PRIMARY_REF],
            "strongest_reduction": "the proposed fixed-budget residual remains unresolved until source-faithful LOPD training/compressor assets can execute the frozen same-information decomposition falsifier",
            "reason": "The official LOPD repository remains at its initial release, still states that training code is coming soon, and exposes qformer.num_queries=32 with a placeholder compressor checkpoint; locally changing K would change or invent the training object.",
            "avoid": [
                "substituting a random, locally invented, differently trained, or outcome-tuned compressor for the source-specific LOPD training object",
                "treating missing released training assets as scientific evidence for or against the fixed-budget residual",
                "reopening from another unbudgeted K or top-n sensitivity sweep",
            ],
            "reopen_only_if": reopen,
            "hold_origin": "bounded-evidence-acquisition",
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_experiment_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
            "scientific_authority": False,
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


def validate_hold(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    frozen = state.get("frozen_problem") or {}
    release = state.get("release_audit") or {}
    support = state.get("support_diagnosis") or {}
    projection = state.get("memory_projection") or {}
    persistent = state.get("persistent_hold") or {}
    arms = frozen.get("arms") or []
    if state.get("primary_ref") != PRIMARY_REF or state.get("parent_closure_id") != PARENT_CLOSURE_ID:
        errors.append("LOPD child identity drift")
    if frozen.get("total_latent_positions") != 64 or len(arms) != 4 or any(int(row.get("total_latent_positions_JxK") or 0) != 64 for row in arms):
        errors.append("LOPD fixed-budget decomposition arms drift")
    if [(row.get("experience_count_J"), row.get("latent_tokens_per_experience_K")) for row in arms] != [(1,64),(2,32),(4,16),(8,8)]:
        errors.append("LOPD decomposition arm identities drift")
    if release.get("local_head") != EXPECTED_RELEASE_COMMIT or release.get("remote_head") != EXPECTED_RELEASE_COMMIT or release.get("release_unchanged_since_initial_code_release") is not True:
        errors.append("LOPD official release head changed; re-audit source assets before keeping the hold")
    if release.get("readme_training_code_coming_soon") is not True or release.get("qformer_num_queries") != 32 or release.get("compressor_checkpoint_is_placeholder") is not True or release.get("inference_n_retrieve") != 1:
        errors.append("LOPD current release no longer matches the source-specific asset hold")
    if support.get("status") != "WAIT_PRIMARY_ASSET_RELEASE" or support.get("support_status") != "SOURCE_SPECIFIC_PRIMARY_ASSET_UNAVAILABLE" or support.get("stop_class") != "SUPPORT_STOP":
        errors.append("LOPD child must remain a source-asset support hold")
    if support.get("failure_layer") != "experiment_identifiability" or support.get("source_faithful_execution_available") is not False:
        errors.append("LOPD child source-faithful execution status drift")
    if support.get("principle_dead_end_certified") is not False or support.get("principle_update_allowed") is not False:
        errors.append("LOPD source-asset hold cannot update the principle")
    if projection.get("memory_class") != "REOPENABLE_HOLD" or projection.get("dead_end_certified") is not False or not str(projection.get("required_unit") or "").strip():
        errors.append("LOPD child memory projection must be a reopenable hold")
    if not str(persistent.get("basin") or "").startswith("near-miss-terminal-support-hold-") or persistent.get("memory_class") != "REOPENABLE_HOLD" or persistent.get("dead_end_certified") is not False or persistent.get("stop_class") != "SUPPORT_STOP" or persistent.get("failure_layer") != "experiment_identifiability" or persistent.get("scientific_authority") is not False:
        errors.append("LOPD persistent source-asset hold is invalid")
    if state.get("scientific_authority") is not False or any((state.get("authority") or {}).values()):
        errors.append("LOPD child hold must have zero downstream authority")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile the LOPD fixed-budget decomposition child and source-specific asset hold.")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--prior-preflight", type=Path, required=True)
    parser.add_argument("--parent-closure", type=Path, required=True)
    parser.add_argument("--remote-head", default="", help="Optional audited official HEAD; otherwise query origin HEAD read-only.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    remote_head = str(args.remote_head or "").strip() or _remote_head(args.repo_root)
    state = build_hold(
        repo_root=args.repo_root,
        prior_preflight_path=args.prior_preflight,
        parent_closure_path=args.parent_closure,
        remote_head=remote_head,
    )
    errors = validate_hold(state)
    if errors:
        raise SystemExit("invalid LOPD fixed-budget asset hold: " + "; ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": state["support_diagnosis"]["status"], "stop_class": state["support_diagnosis"]["stop_class"], "failure_layer": state["support_diagnosis"]["failure_layer"], "remote_head": remote_head}, ensure_ascii=False))


if __name__ == "__main__":
    main()
