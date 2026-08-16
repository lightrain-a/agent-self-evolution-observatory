from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any

from research_pipeline.ark_provider import ArkResponsesClient, extract_json_object

EXPERIMENT_ID = "STRI-SKILLRL-FINAL-POLICY-COMPETENCY-P0E-20260816"
CHECKS = (
    "qualified_stop_identifiable",
    "competence_support_valid",
    "treatment_reached_behavior",
    "semantic_specificity_collapse_supported",
    "endpoint_transport_failure_supported",
    "exact_quotient_control_valid",
    "current_N1_N2_N3_scope_unaffected",
    "stage2_must_remain_locked",
    "failed_C4_must_not_be_rescued_by_posthoc_estimand_change",
)


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def prompt(diagnosis: dict[str, Any], narrow: dict[str, Any], final_state: dict[str, Any]) -> str:
    return f"""You are an independent post-negative scientific reviewer. You did not design this experiment.
Your role is diagnostic only. You cannot authorize GPU, METHOD-PASS/FAIL, paper claim expansion, or a new experiment.

A preregistered P0-E experiment has produced a qualified true negative for an optional downstream bridge (C4). Review whether the failure-layer diagnosis is scientifically valid and whether a genuinely NEW scientific problem survives. Do not rescue the failed C4 by swapping endpoints after seeing the result.

Return ONLY one JSON object with exactly these fields:
{{
  "verdict":"CONFIRM_QUALIFIED_STOP"|"REVISE_DIAGNOSIS"|"REJECT_STOP",
  "confidence":"high"|"medium"|"low",
  "checks":{{{','.join(json.dumps(k)+':true|false' for k in CHECKS)}}},
  "primary_failure_layer":"semantic-specificity-collapse"|"endpoint-transport-failure"|"both"|"other",
  "strongest_alternative_explanation":"...",
  "why_more_seeds_or_stage2_are_not_justified":"...",
  "current_paper_scope_effect":"...",
  "new_problem_verdict":"NO_NEW_PROBLEM"|"NOVELTY_SCREEN_ONLY"|"NEW_PROBLEM_WORTH_LOCAL_FALSIFIER",
  "candidate_new_problem":"...",
  "strongest_reduction_of_candidate":"...",
  "why_candidate_is_not_a_C4_rescue":"...",
  "cheapest_decisive_falsifier_if_any":"...",
  "required_revision_to_diagnosis":"..."
}}

Review standards:
- A true negative is valid only if the endpoint has support, controls are valid, treatment manipulation actually reaches behavior, and the negative cannot be explained by execution failure.
- B semantic displacement changes response/action trajectories but never final success; C identity placebo changes action trajectories even more often; D exact quotient fully restores A.
- Distinguish (i) semantic-specificity failure from (ii) terminal endpoint transport failure / outcome-equivalent robust dynamics.
- The current paper is already explicitly narrowed to static N1/N2/N3 and forbids downstream utility harm. C4 was optional and non-rescuing.
- Do not propose more seeds, easier tasks, another model/checkpoint, threshold relaxation, or post-hoc trajectory divergence as evidence that C4 succeeded.
- If you propose a new problem, state its strongest mature reduction. Prefer NO_NEW_PROBLEM or NOVELTY_SCREEN_ONLY unless it has a genuinely distinct estimand and a falsifiable mechanism.
- If all diagnosis checks are true and no concrete correction is required, use CONFIRM_QUALIFIED_STOP and required_revision_to_diagnosis="".

QUALIFIED STOP DIAGNOSIS:
{json.dumps(diagnosis, ensure_ascii=False, indent=2)}

CURRENT NARROW PAPER DESIGN:
{json.dumps(narrow, ensure_ascii=False, indent=2)}

CURRENT FINAL SUBMISSION STATE:
{json.dumps(final_state, ensure_ascii=False, indent=2)}
"""


def run(project: pathlib.Path, model: str, output: pathlib.Path, raw: pathlib.Path) -> dict[str, Any]:
    diagnosis_path = project / "generated/asset-first-stri-skillrl-final-policy-p0e-qualified-stop-diagnosis-20260817.json"
    narrow_path = project / "generated/asset-first-stri-narrow-paper-design-20260816.json"
    final_path = project / "generated/asset-first-stri-iclr2027-final-state-20260816.json"
    diagnosis, narrow, final_state = map(load, (diagnosis_path, narrow_path, final_path))
    client = ArkResponsesClient()
    response = client.respond(
        prompt(diagnosis, narrow, final_state),
        model=model,
        max_output_tokens=5000,
        temperature=0.0,
        thinking=None if model.startswith("glm") else "disabled",
    )
    text = str(response.get("text") or "")
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_text(text + "\n", encoding="utf-8")
    payload = extract_json_object(text)
    checks = payload.get("checks") or {}
    verdict = str(payload.get("verdict") or "")
    revision = str(payload.get("required_revision_to_diagnosis") or "").strip()
    normalized_checks = {k: checks.get(k) is True for k in CHECKS}
    all_checks = all(normalized_checks.values())
    if verdict == "CONFIRM_QUALIFIED_STOP" and all_checks and not revision:
        compiled_verdict = verdict
    elif verdict == "REJECT_STOP":
        compiled_verdict = "REJECT_STOP"
    else:
        compiled_verdict = "REVISE_DIAGNOSIS"
    compiled = {
        "schema_version": "1.0",
        "experiment_id": EXPERIMENT_ID,
        "artifact_kind": "independent-post-negative-differential-diagnosis-review",
        "reviewed_diagnosis_sha256": sha(diagnosis_path),
        "reviewed_narrow_paper_sha256": sha(narrow_path),
        "reviewed_final_state_sha256": sha(final_path),
        "verdict": compiled_verdict,
        "confidence": payload.get("confidence"),
        "checks": normalized_checks,
        "primary_failure_layer": str(payload.get("primary_failure_layer") or ""),
        "strongest_alternative_explanation": str(payload.get("strongest_alternative_explanation") or ""),
        "why_more_seeds_or_stage2_are_not_justified": str(payload.get("why_more_seeds_or_stage2_are_not_justified") or ""),
        "current_paper_scope_effect": str(payload.get("current_paper_scope_effect") or ""),
        "new_problem_verdict": str(payload.get("new_problem_verdict") or ""),
        "candidate_new_problem": str(payload.get("candidate_new_problem") or ""),
        "strongest_reduction_of_candidate": str(payload.get("strongest_reduction_of_candidate") or ""),
        "why_candidate_is_not_a_C4_rescue": str(payload.get("why_candidate_is_not_a_C4_rescue") or ""),
        "cheapest_decisive_falsifier_if_any": str(payload.get("cheapest_decisive_falsifier_if_any") or ""),
        "required_revision_to_diagnosis": revision,
        "reviewer_requested_model": model,
        "reviewer_model": str(response.get("resolved_model") or model),
        "raw_path": str(raw),
        "raw_sha256": sha(raw),
        "scientific_authority": False,
        "authority": {"paper_claim_expansion": False, "method": False, "full_experiment": False, "gpu": False},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + ".tmp")
    tmp.write_text(json.dumps(compiled, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(output)
    return compiled


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=pathlib.Path, default=pathlib.Path("."))
    ap.add_argument("--model", required=True)
    ap.add_argument("--output", type=pathlib.Path, required=True)
    ap.add_argument("--raw", type=pathlib.Path, required=True)
    a = ap.parse_args()
    print(json.dumps(run(a.project, a.model, a.output, a.raw), ensure_ascii=False))


if __name__ == "__main__":
    main()
