from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

from research_pipeline.ark_provider import ArkResponsesClient, extract_json_object


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=pathlib.Path, default=pathlib.Path("."))
    ap.add_argument("--model", default="minimax-m3")
    ap.add_argument("--advocate", type=pathlib.Path, required=True)
    ap.add_argument("--statistical-audit", type=pathlib.Path, required=True)
    ap.add_argument("--output", type=pathlib.Path, required=True)
    ap.add_argument("--raw", type=pathlib.Path, required=True)
    a = ap.parse_args()
    root = a.project / "generated/research-data/runs/stri-skillrl-final-policy-p0e-postnegative-20260817"
    paths = {
        "diagnosis": a.project / "generated/asset-first-stri-skillrl-final-policy-p0e-qualified-stop-diagnosis-20260817.json",
        "screen": a.project / "generated/asset-first-stri-skillrl-final-policy-p0e-same-information-screen-20260817.json",
        "design_critic": root / "doubao-v2.review.json",
        "principle_falsifier": root / "deepseek-v2.review.json",
        "operationalization_critic": root / "web-current-source.review.json",
        "principle_advocate": a.advocate,
        "statistical_audit": a.statistical_audit,
    }
    payloads = {k: load(v) for k, v in paths.items()}
    diagnosis_sha = sha(paths["diagnosis"])
    for role in ("design_critic", "principle_falsifier"):
        if payloads[role].get("reviewed_diagnosis_sha256") != diagnosis_sha:
            raise ValueError(f"stale-{role}")
    if payloads["principle_advocate"].get("reviewed_diagnosis_sha256") != diagnosis_sha:
        raise ValueError("stale-principle-advocate")
    if payloads["principle_advocate"].get("reviewed_same_information_screen_sha256") != sha(paths["screen"]):
        raise ValueError("stale-advocate-screen")

    compact = {
        "diagnosis": {k: payloads["diagnosis"].get(k) for k in ["disposition", "belief_update_scope", "diagnosis_layers", "stage2_confirmation_locked"]},
        "endpoint_result": payloads["diagnosis"].get("endpoint_result"),
        "same_information_screen": {"verdict": payloads["screen"].get("verdict"), "any_B_dominance": payloads["screen"].get("any_simple_B_over_C_dominance_supported"), "metrics": payloads["screen"].get("metrics")},
        "statistical_audit": {k: payloads["statistical_audit"].get(k) for k in ["experimental_stop_rule_valid", "persistent_principle_dead_end_statistically_certified", "registered_go_effect_floor", "two_sided_exact_mcnemar_p_at_effect_floor_if_all_flips_one_direction", "minimum_unidirectional_discordances_for_two_sided_mcnemar_p_lt_0_05", "corresponding_minimum_detectable_signed_rate_difference_under_best_case_directionality", "zero_discordance_upper_bounds", "recommended_principle_layer_disposition", "reopen_condition"]},
        "design_critic": {k: payloads["design_critic"].get(k) for k in ["verdict", "confidence", "primary_failure_layer", "new_problem_verdict", "strongest_reduction_of_candidate"]},
        "principle_falsifier": {k: payloads["principle_falsifier"].get(k) for k in ["verdict", "confidence", "primary_failure_layer", "new_problem_verdict", "strongest_reduction_of_candidate"]},
        "operationalization_critic": {k: payloads["operationalization_critic"].get(k) for k in ["verdict", "confidence", "primary_failure_layer", "new_problem_verdict", "required_revision_to_diagnosis"]},
        "principle_advocate": {k: payloads["principle_advocate"].get(k) for k in ["verdict", "confidence", "strongest_case_against_dead_end", "is_that_case_supported_by_current_evidence", "specific_missing_precondition_if_any", "does_same_information_placebo_absorb_semantic_specificity", "does_zero_endpoint_disagreement_validly_reject_registered_endpoint_transport", "is_any_allowed_non_rescue_explanation_sufficient_to_keep_the_scoped_prediction_unresolved"]},
    }
    prompt = f"""You are the META-ADJUDICATOR for a negative-result principle review. No GPU/method/paper-claim authority. Distinguish a valid preregistered experimental STOP from a stronger persistent population-level principle dead end. Broader STRI N1/N2/N3 are out of scope.

Return ONLY compact JSON:
{{"verdict":"CERTIFY_SCOPED_DEAD_END"|"REGISTERED_PREDICTION_REJECTED_ONLY"|"KEEP_SCOPED_PRINCIPLE_UNRESOLVED","confidence":"high"|"medium"|"low","checks":{{"experimental_stop_valid":true|false,"persistent_dead_end_statistical_resolution_sufficient":true|false,"same_information_trajectory_reduction_supported":true|false,"principle_advocate_objection_resolved":true|false,"current_paper_scope_protected":true|false,"stage2_locked":true|false,"new_problem_requires_no_gpu":true|false}},"dead_end_scope":"...","counter_explanation_type":"SAME_INFORMATION_REDUCTION"|"NONE","reason":"...","reopen_condition":"...","current_paper_effect":"...","new_problem_disposition":"NO_NEW_PROBLEM"|"NOVELTY_SCREEN_ONLY"|"NEW_PROBLEM_WORTH_LOCAL_FALSIFIER","required_revision":""}}

Rules:
- The frozen P0-E STOP can remain valid even if persistent principle-dead-end certification is too strong.
- Persistent dead-end requires both an affirmative counter-explanation and adequate statistical resolution for the population-level claim. A preregistered STOP rule is not automatically an equivalence test.
- Do not authorize post-hoc more seeds, another model/task, threshold relaxation, Stage-2, or trajectory divergence as rescue.
- If the advocate identifies a valid statistical-resolution precondition that is not met, choose KEEP_SCOPED_PRINCIPLE_UNRESOLVED (or REGISTERED_PREDICTION_REJECTED_ONLY if you distinguish the registered sample-level prediction), not CERTIFY_SCOPED_DEAD_END.
- The same-information screen may still close the trajectory-only 'new idea' even while the endpoint principle remains unresolved.

PANEL SUMMARY:
{json.dumps(compact,ensure_ascii=False,separators=(',',':'))}
"""
    client = ArkResponsesClient()
    res = client.respond(prompt, model=a.model, max_output_tokens=1800, temperature=0.0, thinking="disabled" if a.model.startswith("deepseek") else None)
    text = str(res.get("text") or "")
    a.raw.parent.mkdir(parents=True, exist_ok=True)
    a.raw.write_text(text + "\n", encoding="utf-8")
    answer = extract_json_object(text)
    compiled = {
        "schema_version": "1.0",
        "artifact_kind": "negative-result-meta-adjudication-review",
        "input_receipts": {k: {"path": str(v), "sha256": sha(v)} for k, v in paths.items()},
        **answer,
        "reviewer_requested_model": a.model,
        "reviewer_model": str(res.get("resolved_model") or a.model),
        "raw_path": str(a.raw),
        "raw_sha256": sha(a.raw),
        "scientific_authority": False,
        "authority": {"paper_claim_expansion": False, "method": False, "full_experiment": False, "gpu": False},
    }
    tmp = a.output.with_suffix(a.output.suffix + ".tmp")
    tmp.write_text(json.dumps(compiled, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(a.output)
    print(json.dumps(compiled, ensure_ascii=False))


if __name__ == "__main__":
    main()
