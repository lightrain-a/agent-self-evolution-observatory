from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

from research_pipeline.ark_provider import ArkResponsesClient, extract_json_object


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=pathlib.Path, default=pathlib.Path("."))
    ap.add_argument("--model", default="kimi-k3")
    ap.add_argument("--output", type=pathlib.Path, required=True)
    ap.add_argument("--raw", type=pathlib.Path, required=True)
    a = ap.parse_args()
    diagnosis_path = a.project / "generated/asset-first-stri-skillrl-final-policy-p0e-qualified-stop-diagnosis-20260817.json"
    screen_path = a.project / "generated/asset-first-stri-skillrl-final-policy-p0e-same-information-screen-20260817.json"
    diagnosis = json.loads(diagnosis_path.read_text(encoding="utf-8"))
    screen = json.loads(screen_path.read_text(encoding="utf-8"))
    compact = {
        "diagnosis_sha256": sha(diagnosis_path),
        "disposition": diagnosis.get("disposition"),
        "belief_update_scope": diagnosis.get("belief_update_scope"),
        "qualification": diagnosis.get("qualification"),
        "endpoint_result": diagnosis.get("endpoint_result"),
        "trajectory_B": {k: (diagnosis.get("trajectory_result", {}).get("B_displacement_clone_vs_A") or {}).get(k) for k in ["response_sequence_disagreement", "projected_action_sequence_disagreement", "first_action_divergence_median_step", "endpoint_disagreement"]},
        "trajectory_C": {k: (diagnosis.get("trajectory_result", {}).get("C_identity_placebo_vs_A") or {}).get(k) for k in ["response_sequence_disagreement", "projected_action_sequence_disagreement", "first_action_divergence_median_step", "endpoint_disagreement"]},
        "trajectory_D": {k: (diagnosis.get("trajectory_result", {}).get("D_exact_quotient_vs_A") or {}).get(k) for k in ["response_sequence_disagreement", "projected_action_sequence_disagreement", "endpoint_disagreement"]},
        "interpretation": diagnosis.get("principled_interpretation"),
        "paper_scope_effect": diagnosis.get("paper_scope_effect"),
        "same_information_screen_sha256": sha(screen_path),
        "same_information_screen_verdict": screen.get("verdict"),
        "same_information_metrics": screen.get("metrics"),
    }
    prompt = f"""You are the PRINCIPLE ADVOCATE. Make the strongest legitimate case AGAINST persistent dead-end certification for this narrowly scoped prediction: under the single frozen SkillRL final RL policy and frozen 12-task x 2-seed exact-clone panel, semantic displacement B should change terminal ALFWorld success beyond same-information identity placebo C, while exact quotient D restores A.

Broader STRI N1/N2/N3 are OUT OF SCOPE and remain unchanged. Forbidden rescues: more seeds until significance, post-selected easier tasks, another model/checkpoint, threshold relaxation, Stage-2 after local STOP, or replacing terminal success with trajectory divergence after seeing the negative.

Return ONLY compact JSON:
{{"role":"principle-advocate","verdict":"ADVOCATE_CONCEDES_SCOPED_DEAD_END"|"KEEP_SCOPED_PRINCIPLE_UNRESOLVED"|"REJECT_DEAD_END_CERTIFICATION","confidence":"high"|"medium"|"low","strongest_case_against_dead_end":"...","is_that_case_supported_by_current_evidence":true|false,"specific_missing_precondition_if_any":"...","does_same_information_placebo_absorb_semantic_specificity":true|false,"does_zero_endpoint_disagreement_validly_reject_registered_endpoint_transport":true|false,"is_any_allowed_non_rescue_explanation_sufficient_to_keep_the_scoped_prediction_unresolved":true|false,"reason":"...","reopen_condition_if_dead_end_certified":"..."}}

A mere possibility that another future scope may differ belongs in the reopen condition, not as a reason to keep this frozen scope unresolved. The diagnosis deliberately does NOT claim active recovery as the causal mechanism; it only identifies terminal paired equivalence.

EVIDENCE SUMMARY:
{json.dumps(compact,ensure_ascii=False,separators=(',',':'))}
"""
    client = ArkResponsesClient()
    res = client.respond(prompt, model=a.model, max_output_tokens=2200, temperature=0.0, thinking="disabled" if a.model.startswith("deepseek") else None)
    text = str(res.get("text") or "")
    a.raw.parent.mkdir(parents=True, exist_ok=True)
    a.raw.write_text(text + "\n", encoding="utf-8")
    payload = extract_json_object(text)
    compiled = {
        "schema_version": "1.0",
        "artifact_kind": "principle-advocate-post-negative-review",
        "reviewed_diagnosis_sha256": sha(diagnosis_path),
        "reviewed_same_information_screen_sha256": sha(screen_path),
        **payload,
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
