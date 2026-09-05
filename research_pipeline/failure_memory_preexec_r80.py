#!/usr/bin/env python3
"""R80 pre-execution freeze for B1.

This zero-model builder does two things before any R72/R73 outcome is opened:
1) freezes the future targeted ~30B capability-boundary model and the deterministic
   matched-control rule that may be triggered after the Qwen P/T stage; and
2) emits a narrow execution authority for the already independently reviewed
   321-trajectory R72/R73 experiment.

It does not execute models, inspect task outcomes, authorize analysis, PSMG, L3,
or manuscript claim changes.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib
from datetime import datetime, timezone
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
R72_PROTOCOL_RECEIPT = "acd56a621e20e00aca9a65697b86034356f1083ee54b95419fb10c37c885dd23"
R68_PANEL_RECEIPT = "bdfb80d67e353a755f8df6a43fe4889e81f8ff2b7ea902a2e07934a31b99be20"
R74_R3_RECEIPT = "7aaabc3c854098615ba7aacb11012d4b6feafa503d7c6ae5bf36f9e750aa6b38"
R74_CLOSEOUT_RECEIPT = "bca2052dbdd6b5c8416490c2c7dd65a7c01ebb1eec9b241b667eb048afc2067a"
AUTH_STATUS = "R80_R72_R73_EXECUTION_AUTHORITY_USER_GRANTED_PATH_EQUIVALENT_SOURCE"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def canonical(v: Any) -> str:
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def digest(v: Any) -> str:
    return hashlib.sha256(canonical(v).encode()).hexdigest()


def sha(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def load(p: pathlib.Path) -> dict[str, Any]:
    v = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(v, dict):
        raise RuntimeError(f"not-object:{p}")
    return v


def valid(v: dict[str, Any]) -> bool:
    x = v.get("receipt_sha256")
    return isinstance(x, str) and x == digest({k: z for k, z in v.items() if k != "receipt_sha256"})


def task_covariates(rec: dict[str, Any]) -> dict[str, Any]:
    selected = list(rec.get("selected") or [])
    sc = sum(1 for s in selected if s.get("source_outcome_success") is True)
    fc = sum(1 for s in selected if s.get("source_outcome_success") is False)
    sig = sorted(str(x) for x in rec.get("cluster_signature") or [])
    return {
        "task_id": str(rec["validation_task_id"]),
        "r54_eligible_order_index": int(rec["r54_eligible_order_index"]),
        "selected_count": int(rec["selected_count"]),
        "success_memory_count": sc,
        "failure_memory_count": fc,
        "mixed_provenance": bool(sc and fc),
        "cluster_signature": sig,
        "cluster_signature_size": len(sig),
        "task_instruction_utf8_bytes": len(str(rec["task_instruction"]).encode("utf-8")),
        "task_instruction_utf8_sha256": rec["task_instruction_utf8_sha256"],
    }


def match_tuple(a: dict[str, Any], b: dict[str, Any]) -> list[int]:
    A, B = set(a["cluster_signature"]), set(b["cluster_signature"])
    union = len(A | B)
    inter = len(A & B)
    jaccard_ppm = 0 if union == 0 else round((1.0 - inter / union) * 1_000_000)
    return [
        int(a["selected_count"] != b["selected_count"]),
        abs(a["success_memory_count"] - b["success_memory_count"]),
        jaccard_ppm,
        abs(a["cluster_signature_size"] - b["cluster_signature_size"]),
        abs(a["task_instruction_utf8_bytes"] - b["task_instruction_utf8_bytes"]),
        abs(a["r54_eligible_order_index"] - b["r54_eligible_order_index"]),
        int(b["r54_eligible_order_index"]),
        int(b["task_id"]),
    ]


def select_controls_from_frozen_covariates(matching: dict[str, Any], discordant_ids: list[str], concordant_ids: list[str]) -> list[dict[str, Any]]:
    cov_by = {str(x["task_id"]): x for x in matching.get("task_covariates") or []}
    dset = [str(x) for x in discordant_ids]
    cset = [str(x) for x in concordant_ids]
    if set(dset) & set(cset):
        raise RuntimeError("discordant-concordant-overlap")
    if any(x not in cov_by for x in dset + cset):
        raise RuntimeError("matching-task-outside-frozen-panel")
    if not dset:
        return []
    if len(dset) > len(cset):
        raise RuntimeError("insufficient-concordant-controls-fail-closed")
    ordered_d = sorted(dset, key=lambda x: (cov_by[x]["r54_eligible_order_index"], int(x)))
    unused = set(cset)
    out = []
    for did in ordered_d:
        candidates = sorted(unused, key=lambda cid: tuple(match_tuple(cov_by[did], cov_by[cid])))
        if not candidates:
            raise RuntimeError("control-selection-exhausted")
        cid = candidates[0]
        out.append({"discordant_task_id": did, "matched_control_task_id": cid, "cost": match_tuple(cov_by[did], cov_by[cid])})
        unused.remove(cid)
    return out


def build_matching_freeze(panel: dict[str, Any], protocol: dict[str, Any]) -> dict[str, Any]:
    cov = [task_covariates(r) for r in panel.get("records") or []]
    if len(cov) != 66:
        raise RuntimeError("covariate-panel-not-66")
    ids = [x["task_id"] for x in cov]
    if ids != [str(x) for x in protocol["units"]["representative_ids"]]:
        raise RuntimeError("covariate-order-drift")
    pair_cost_rows = []
    for a in cov:
        for b in cov:
            if a["task_id"] == b["task_id"]:
                continue
            pair_cost_rows.append({"left_task_id": a["task_id"], "right_task_id": b["task_id"], "cost": match_tuple(a, b)})
    out = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R80-MATCHED-CONTROL-RULE",
        "recorded_at": now(),
        "status": "R80_QWEN_OUTCOME_BLIND_MATCHING_RULE_FROZEN_PRE_EXECUTION",
        "role": "FUTURE_TARGETED_SCALE_CONTROL_SELECTION_RULE_ZERO_MODEL",
        "bindings": {
            "r68_panel_receipt_sha256": panel["receipt_sha256"],
            "r72_protocol_receipt_sha256": protocol["receipt_sha256"],
            "r80_preexec_builder_sha256": sha(pathlib.Path(__file__).resolve()),
        },
        "Qwen_poststage_sets": {
            "D_discordant": "Qwen complete P_neutral/T_truthful pairs with unequal terminal_success after the sealed 189-run Qwen stage",
            "C_concordant": "Qwen complete P_neutral/T_truthful pairs with equal terminal_success after the sealed 189-run Qwen stage",
            "technical_missing": "excluded from D and C; separately reported; never replaced",
        },
        "trigger": {
            "D_zero": "do not run the strong-model targeted scale check",
            "one_to_one_possible": "if 1 <= |D| <= |C|, select exactly |D| distinct controls and run P/T on D plus controls: 4|D| strong-model trajectories",
            "insufficient_controls": "if |D| > |C|, fail closed; this R80 matched-control plan does not authorize a scale run",
        },
        "control_selection_algorithm": {
            "discordant_processing_order": "ascending frozen r54_eligible_order_index",
            "greedy_one_to_one": True,
            "candidate_pool": "unused members of C_concordant only",
            "choose": "lexicographically minimal frozen cost tuple",
            "cost_tuple_fields_in_order": [
                "selected_count_mismatch",
                "absolute_success_memory_count_difference",
                "cluster_signature_jaccard_distance_ppm",
                "absolute_cluster_signature_size_difference",
                "absolute_task_instruction_utf8_byte_length_difference",
                "absolute_r54_eligible_order_index_difference",
                "candidate_r54_eligible_order_index_tiebreak",
                "candidate_numeric_task_id_tiebreak",
            ],
            "outcome_fields_forbidden_in_cost": True,
            "post_Qwen_manual_control_choice": False,
            "reference_implementation": "select_controls_from_frozen_covariates() in the content-addressed R80 builder",
        },
        "task_covariates": cov,
        "task_covariates_sha256": digest(cov),
        "pair_cost_matrix_rows": pair_cost_rows,
        "pair_cost_matrix_sha256": digest(pair_cost_rows),
        "future_strong_model_readout": {
            "arms": ["P_neutral", "T_truthful"],
            "no_S_shuffled": True,
            "descriptive_only": True,
            "report": [
                "strong-model P/T outcome for every selected task",
                "same-direction persistence count among Qwen D_discordant",
                "any-direction discordance count among Qwen D_discordant",
                "discordance count among matched C controls",
            ],
            "no_cross_model_pooling": True,
            "no_scalar_model_strength_claim": True,
            "no_population_effect_estimate_from_outcome_selected_D": True,
        },
        "task_outcomes_observed": 0,
        "new_model_trajectories": 0,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }
    out["receipt_sha256"] = digest(out)
    return out


def build_scale_freeze(strong: dict[str, Any], matching: dict[str, Any], protocol: dict[str, Any]) -> dict[str, Any]:
    required = ["family", "root", "host", "file_count", "bytes", "artifact_manifest_sha256", "config_sha256", "tokenizer_config_sha256", "generation_config_sha256"]
    missing = [k for k in required if k not in strong]
    if missing:
        raise RuntimeError(f"strong-model-identity-missing:{missing}")
    if strong["family"] != "Qwen3.5-27B" or int(strong["file_count"]) < 20 or int(strong["bytes"]) < 50_000_000_000:
        raise RuntimeError("strong-model-identity-not-expected-27b")
    out = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R80-STRONG-MODEL-SCALE-FREEZE",
        "recorded_at": now(),
        "status": "R80_TARGETED_SCALE_MODEL_AND_MATCHING_RULE_FROZEN_PRE_QWEN_OUTCOME",
        "role": "PROSPECTIVE_CAPABILITY_BOUNDARY_EXTERNAL_VALIDITY_FREEZE_ZERO_MODEL",
        "bindings": {
            "r72_protocol_receipt_sha256": protocol["receipt_sha256"],
            "matching_rule_receipt_sha256": matching["receipt_sha256"],
        },
        "strong_model": strong,
        "scientific_role": "targeted external-validity/capability-boundary diagnostic only; not a third primary executor",
        "activation": "only after sealed Qwen stage is complete and Qwen P/T discordant set is opened under separate analysis authority",
        "scale_run_formula": "4D trajectories where D is the count of complete Qwen P/T terminal-discordant tasks, provided D <= concordant-control count",
        "pre_scale_parser_qualification": {
            "required": True,
            "scope": "non-scientific native OSInteraction response-format qualification before any selected scale task",
            "terminal_evaluator_calls": 0,
            "must_not_change_selected_task_set": True,
        },
        "no_scale_execution_authority_here": True,
        "task_outcomes_observed": 0,
        "new_model_trajectories": 0,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }
    out["receipt_sha256"] = digest(out)
    return out


def build_authority(protocol: dict[str, Any], r74_review: dict[str, Any], r74_closeout: dict[str, Any], scale: dict[str, Any], runner_sha: str, clean_source: str) -> dict[str, Any]:
    out = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R80-R72-R73-EXECUTION-AUTHORITY",
        "recorded_at": now(),
        "status": AUTH_STATUS,
        "role": "USER_AUTHORIZED_EXECUTION_ONLY_FOR_ALREADY_R3_PASSED_321_TRAJECTORY_PROTOCOL",
        "protocol_receipt_sha256": protocol["receipt_sha256"],
        "bindings": {
            "r74_independent_r3_review_receipt_sha256": r74_review["receipt_sha256"],
            "r74_design_closeout_receipt_sha256": r74_closeout["receipt_sha256"],
            "r80_scale_freeze_receipt_sha256": scale["receipt_sha256"],
            "r80_execute_runner_sha256": runner_sha,
        },
        "user_authorization": "Explicit continuation request after the assistant stated the next action would freeze the strong-model rule and start the R72/R73 321-run experiment.",
        "execution_realization": {
            "clean_source_checkout": clean_source,
            "path_migration_only": True,
            "reason": "historical shared checkout contains unrelated untracked temporary files and is not modified; use a clean worktree at the exact pinned commit",
            "scientific_treatment_change": False,
        },
        "authority": {
            "qwen_execution": True,
            "llama_execution": True,
            "analysis": False,
            "gpu": True,
            "PSMG": False,
            "L3": False,
            "paper_claim_change": False,
        },
        "execution_order": "Qwen 189 sealed first, then Llama 132 sealed; no effect inspection before a separately generated analysis authority",
        "planned_new_model_trajectories": 321,
        "strong_model_scale_execution": False,
        "scientific_authority": True,
        "experiment_authority": True,
        "gpu_authority": True,
    }
    out["receipt_sha256"] = digest(out)
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    for x in ["protocol", "panel", "r74-review", "r74-closeout", "strong-model-identity", "output-dir"]:
        p.add_argument("--" + x, type=pathlib.Path, required=True)
    p.add_argument("--r80-execute-runner-sha", required=True)
    p.add_argument("--clean-source-checkout", required=True)
    a = p.parse_args()
    protocol, panel, r74_review, r74_closeout, strong = map(load, [a.protocol, a.panel, a.r74_review, a.r74_closeout, a.strong_model_identity])
    strong = dict(strong)
    strong["identity_input_file_sha256"] = sha(a.strong_model_identity.resolve())
    if not all(valid(x) for x in [protocol, panel, r74_review, r74_closeout]):
        raise RuntimeError("canonical-receipt-invalid")
    if protocol["receipt_sha256"] != R72_PROTOCOL_RECEIPT or panel["receipt_sha256"] != R68_PANEL_RECEIPT or r74_review["receipt_sha256"] != R74_R3_RECEIPT or r74_closeout["receipt_sha256"] != R74_CLOSEOUT_RECEIPT:
        raise RuntimeError("canonical-binding-drift")
    if r74_review.get("verdict") != "PASS_R72_ZERO_PROVIDER_DESIGN" or int((r74_review.get("findings") or {}).get("frozen_total_trajectories") or 0) != 321:
        raise RuntimeError("r74-r3-pass-not-present")
    if r74_closeout.get("next_gate") != "EXPLICIT_USER_EXECUTION_START_REQUIRED_BEFORE_GENERATING_EXECUTION_AUTHORITY":
        raise RuntimeError("unexpected-r74-next-gate")
    outdir = a.output_dir.resolve(); outdir.mkdir(parents=True, exist_ok=True)
    matching = build_matching_freeze(panel, protocol)
    mp = outdir / "d2-failure-memory-provenance-r80-matched-control-rule.json"
    mp.write_text(json.dumps(matching, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    scale = build_scale_freeze(strong, matching, protocol)
    scale["bindings"]["matching_rule_file_sha256"] = sha(mp)
    scale.pop("receipt_sha256", None); scale["receipt_sha256"] = digest(scale)
    sp = outdir / "d2-failure-memory-provenance-r80-strong-model-scale-freeze.json"
    sp.write_text(json.dumps(scale, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    auth = build_authority(protocol, r74_review, r74_closeout, scale, a.r80_execute_runner_sha, a.clean_source_checkout)
    auth["bindings"]["r80_scale_freeze_file_sha256"] = sha(sp)
    auth.pop("receipt_sha256", None); auth["receipt_sha256"] = digest(auth)
    ap = outdir / "d2-failure-memory-provenance-r80-r72-r73-execution-authority.json"
    ap.write_text(json.dumps(auth, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"matching": str(mp), "scale": str(sp), "authority": str(ap), "authority_receipt_sha256": auth["receipt_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
