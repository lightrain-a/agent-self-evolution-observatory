#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
STATUS = "D0B1_INTERVENTION_CONTRAST_IDENTIFIABLE_CAUSAL_ATOM_PURITY_HOLD"
DECISION = "D0B1_OPERATIONAL_CONTRAST_GO_CAUSAL_ATOM_IDENTITY_HOLD"

HERE = Path(__file__).resolve().parent
V1_RECEIPTS = HERE / "cbrg-d0b-receipt-structural-audit-20260824.json"
OUT = HERE / "cbrg-d0b1-intervention-identifiability-audit-20260824.json"
F0_RESULT = Path("/data/wyt/agent-self-evolution-observatory/paper-acceptance-artifacts/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE/f0-write-channel.json")
F0C_RESULT = Path("/data/wyt/agent-self-evolution-observatory/paper-acceptance-artifacts/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE/f0c-prompt-control.json")
B2_CONTRACT = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b2-source-expansion-r1-4096-20260824/b2-source-expansion-r1-contract.json")
B2_PROVIDER_DIR = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b2-source-expansion-r1-4096-20260824/private/provider-responses")
REDDIT_CONTRACT = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b12-crossdomain-qualification-20260824/b12-reddit-r1-contract.json")
REDDIT_WRITER_CSV = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b12-crossdomain-qualification-20260824/b12-r1-writer.csv")

F0_CONTRACT_COMMIT = "ac0f037dc992d873349345d2b5982c484aae703c"
F0_CONTRACT_REPO_PATH = "generated/d2-proxy-reward-memory-f0-contract.json"
F0_CONTRACT_SHA256 = "34986b0ae64c70e314aa84b0ed3d08a8014f2b7fbef36169c81dbfb676f7c035"


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def historical_f0_contract() -> tuple[dict[str, Any], str]:
    raw = subprocess.check_output(["git", "show", f"{F0_CONTRACT_COMMIT}:{F0_CONTRACT_REPO_PATH}"])
    digest = sha_bytes(raw)
    require(digest == F0_CONTRACT_SHA256, f"historical F0 contract SHA drift: {digest}")
    return json.loads(raw), digest


def pair_key(task: Any, condition: str) -> tuple[int, str]:
    return int(task), condition


def main() -> None:
    v1 = load_json(V1_RECEIPTS)
    receipts = v1.get("receipts") or []
    require(len(receipts) == 24, "expected the frozen 24-pair D0-B receipt pool")
    receipt_by_task = {(str(r.get("domain")), int(r.get("source_task"))): r for r in receipts}

    f0_contract, f0_contract_sha = historical_f0_contract()
    f0 = load_json(F0_RESULT)
    f0c = load_json(F0C_RESULT)
    b2 = load_json(B2_CONTRACT)
    reddit = load_json(REDDIT_CONTRACT)

    require(float((f0_contract.get("model") or {}).get("temperature")) == 0.0, "F0 writer temperature is not zero")
    require(float((b2.get("writer_model") or {}).get("temperature")) == 0.0, "B2 writer temperature is not zero")
    reddit_writer_model = ((reddit.get("writer_stage") or {}).get("model") or {})
    require(float(reddit_writer_model.get("temperature")) == 0.0, "Reddit writer temperature is not zero")
    require(bool(((f0c.get("summary") or {}).get("gate_pass"))), "historical F0C prompt control did not pass")

    f0_receipts: dict[tuple[int, str], dict[str, Any]] = {}
    for row in f0.get("provider_receipts") or []:
        stage = str(row.get("stage") or "")
        if stage not in {"memory-success", "memory-failure"} or str(row.get("status") or "") != "completed":
            continue
        condition = stage.split("memory-", 1)[1]
        engine = str(row.get("engine_id") or "")
        require(engine.startswith("task-"), "unexpected F0 engine id")
        f0_receipts[pair_key(engine.split("task-", 1)[1], condition)] = row

    b2_receipts: dict[tuple[int, str], dict[str, Any]] = {}
    for path in sorted(B2_PROVIDER_DIR.glob("writer-*.json")):
        row = load_json(path)
        # The frozen B2 breadth result treats a small number of length-capped
        # provider responses as usable parsed memories when non-empty text is
        # archived. For intervention-lineage purposes we need the resolved model
        # and exact archived text, not a provider-status upgrade.
        if not str(row.get("text") or "").strip():
            continue
        b2_receipts[pair_key(row.get("task_id"), str(row.get("label")))] = row

    reddit_receipts: dict[tuple[int, str], dict[str, Any]] = {}
    with REDDIT_WRITER_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if str(row.get("status") or "") != "complete":
                continue
            reddit_receipts[pair_key(row.get("source_task"), str(row.get("condition")))] = row

    current_rows: list[dict[str, Any]] = []
    for (domain, task), receipt in sorted(receipt_by_task.items()):
        source_kind = receipt.get("source_kind")
        if domain == "shopping" and source_kind == "original_f0":
            cohort = "shopping_original_f0"
            model_cfg = f0_contract.get("model") or {}
            records = f0_receipts
            changed = str((f0_contract.get("intervention") or {}).get("changed") or "")
            seed_bound = "seed" in model_cfg
            max_tokens = model_cfg.get("max_output_tokens")
        elif domain == "shopping" and source_kind == "b2_r1":
            cohort = "shopping_b2_r1"
            model_cfg = b2.get("writer_model") or {}
            records = b2_receipts
            changed = "success versus failure ReasoningBank prompt; all other per-pair writer settings frozen by contract"
            seed_bound = "seed" in model_cfg
            max_tokens = model_cfg.get("max_output_tokens")
        elif domain == "reddit":
            cohort = "reddit_b12_r1"
            model_cfg = reddit_writer_model
            records = reddit_receipts
            changed = "success versus failure ReasoningBank prompt; same source action summary and writer configuration"
            seed_bound = "seed" in model_cfg
            max_tokens = model_cfg.get("max_output_tokens")
        else:
            raise RuntimeError(f"unexpected D0-B cohort: {domain}/{task}/{source_kind}")

        success = records.get((task, "success"))
        failure = records.get((task, "failure"))
        require(success is not None and failure is not None, f"missing complete writer pair: {domain}/{task}")
        success_model = str(success.get("resolved_model") or success.get("requested_model") or "")
        failure_model = str(failure.get("resolved_model") or failure.get("requested_model") or "")
        same_resolved_model = bool(success_model) and success_model == failure_model
        projection_identical = bool(((receipt.get("trajectory_lineage") or {}).get("projection_is_identical_for_success_and_failure_writers")))
        branch_memories_differ = str(((receipt.get("branch_memories") or {}).get("success") or {}).get("sha256")) != str(((receipt.get("branch_memories") or {}).get("failure") or {}).get("sha256"))
        temp_zero = float(model_cfg.get("temperature")) == 0.0

        current_rows.append(
            {
                "domain": domain,
                "source_task": task,
                "cohort": cohort,
                "same_pre_writer_trajectory_projection": projection_identical,
                "same_resolved_writer_model": same_resolved_model,
                "temperature_zero": temp_zero,
                "explicit_seed_bound": bool(seed_bound),
                "same_condition_same_trajectory_replication_bound": False,
                "branch_memories_differ": branch_memories_differ,
                "max_output_tokens": max_tokens,
                "changed_surface": changed,
            }
        )

    cohort_counts = Counter(row["cohort"] for row in current_rows)
    all_lineage = sum(bool(row["same_pre_writer_trajectory_projection"]) for row in current_rows)
    all_models = sum(bool(row["same_resolved_writer_model"]) for row in current_rows)
    temp_zero_pairs = sum(bool(row["temperature_zero"]) for row in current_rows)
    seed_bound_pairs = sum(bool(row["explicit_seed_bound"]) for row in current_rows)
    replicated_pairs = sum(bool(row["same_condition_same_trajectory_replication_bound"]) for row in current_rows)
    differing_pairs = sum(bool(row["branch_memories_differ"]) for row in current_rows)

    require(all_lineage == 24, "not all D0-B pairs share the exact pre-writer projection")
    require(all_models == 24, "not all D0-B pairs use the same resolved writer model within pair")
    require(temp_zero_pairs == 24, "not all D0-B writer pairs use temperature zero")
    require(differing_pairs == 24, "not all D0-B branch-memory pairs differ")
    require(seed_bound_pairs == 0, "unexpected explicit decoding seed discovered; audit contract must be revisited")
    require(replicated_pairs == 0, "unexpected same-condition replication discovered; audit contract must be revisited")

    f0c_summary = f0c.get("summary") or {}
    f0c_qualification = f0c.get("prompt_control_qualification") or {}
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "c1-d0b1-intervention-identifiability-audit",
        "paper_id": PAPER_ID,
        "status": STATUS,
        "decision": DECISION,
        "current_24_pair_intervention_lineage": {
            "pairs": 24,
            "cohorts": dict(sorted(cohort_counts.items())),
            "same_pre_writer_trajectory_projection_pairs": all_lineage,
            "same_resolved_writer_model_within_pair": all_models,
            "temperature_zero_pairs": temp_zero_pairs,
            "branch_memory_content_changed_pairs": differing_pairs,
            "explicit_decoding_seed_bound_pairs": seed_bound_pairs,
            "same_condition_same_trajectory_replication_bound_pairs": replicated_pairs,
            "operational_branch_contrast_identifiable": True,
            "atom_level_causal_residual_purity_certified": False,
        },
        "existing_prompt_mode_control": {
            "artifact": str(F0C_RESULT),
            "sha256": sha_file(F0C_RESULT),
            "tasks_complete": int(f0c_summary.get("tasks_complete") or 0),
            "same_mode_paraphrase_control_qualified": bool(f0c_qualification.get("qualified")),
            "mean_between_reward_mode_distance": float(f0c_summary.get("mean_between_original_distance")),
            "mean_within_mode_paraphrase_distance": float(f0c_summary.get("mean_within_mode_distance")),
            "mean_between_minus_within_delta": float(f0c_summary.get("mean_delta_between_minus_within")),
            "exact_one_sided_sign_flip_p": float(f0c_summary.get("exact_one_sided_sign_flip_p")),
            "decision": str(f0c.get("decision") or ""),
            "interpretation": "Existing fresh control supports an aggregate reward/reflection-mode effect beyond a stronger same-mode wording perturbation. It does not identify which atom in the current 24-pair pool is a causal residual and does not estimate same-condition writer variance on those exact trajectories.",
        },
        "writer_contract_bindings": {
            "historical_f0_contract": {
                "git_commit": F0_CONTRACT_COMMIT,
                "repo_path": F0_CONTRACT_REPO_PATH,
                "sha256": f0_contract_sha,
                "temperature": (f0_contract.get("model") or {}).get("temperature"),
                "max_output_tokens": (f0_contract.get("model") or {}).get("max_output_tokens"),
            },
            "shopping_b2_contract": {
                "path": str(B2_CONTRACT),
                "sha256": sha_file(B2_CONTRACT),
                "temperature": (b2.get("writer_model") or {}).get("temperature"),
                "max_output_tokens": (b2.get("writer_model") or {}).get("max_output_tokens"),
            },
            "reddit_b12_contract": {
                "path": str(REDDIT_CONTRACT),
                "sha256": sha_file(REDDIT_CONTRACT),
                "temperature": reddit_writer_model.get("temperature"),
                "max_output_tokens": reddit_writer_model.get("max_output_tokens"),
            },
        },
        "identifiability_boundary": {
            "what_is_identified_now": "A content-addressed operational counterfactual branch contrast: two writer outputs from the same pre-writer trajectory projection, same resolved writer model, and temperature-zero configuration, differing by success/failure reflection branch.",
            "what_is_not_identified_now": "Atom-level causal residual purity. No explicit decoding seed or same-condition same-trajectory replicate is bound for the current 24 pairs, so an individual textual difference cannot be certified as treatment-only rather than treatment plus residual writer nondeterminism.",
            "terminology_rule": "Until a noise-floor/replication control is bound, call per-atom objects branch-contrast atoms or candidate residuals, not certified causal residual claims.",
            "effect_of_f0c": "The existing F0C control materially strengthens aggregate mode attribution but does not remove the atom-level identifiability gap.",
        },
        "b1_gate": {
            "B1a_intervention_lineage": "GO",
            "B1b_atom_level_residual_identity": "HOLD",
            "B1c_exact_claim_evidence_locator": "LOCKED_BEHIND_B1b_OR_OPERATIONAL_REDEFINITION",
            "certified_branch_residual_atoms": 0,
            "claim_specific_evidence_refs_bound": 0,
        },
        "next_permitted_action": "Zero-call design choice only: either redefine CBRG explicitly around operational branch-contrast atoms, or preserve causal-residual wording and preregister a future same-condition replication/seed/noise-floor control before atom-level residual authority. No semantic adjudicator or provider execution is authorized now.",
        "stop_condition": "If the method requires atom-level causal attribution but cannot obtain a same-condition noise floor without post-outcome selection, STOP/MERGE the method extension rather than treating branch difference as causal residual evidence.",
        "rows": current_rows,
        "provider_calls_added_by_this_audit": 0,
        "gpu_runs_added_by_this_audit": 0,
        "scientific_authority": False,
        "experiment_authority": False,
        "provider_call_authority": False,
        "gpu_authority": False,
        "claim_expansion_authority": False,
        "submission_authority": False,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": STATUS, "decision": DECISION, **payload["current_24_pair_intervention_lineage"], "f0c": payload["existing_prompt_mode_control"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
