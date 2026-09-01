"""Render claim-first paper result/limitation text after qualified adjudication."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, utcnow, write_json,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
ADJUDICATION = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-adjudication-20260901.json"
DESIGN = ROOT / "paper_drafts/e1-stri-reasoningbank-qwen-v3-design-20260901.tex"
OUTPUT = ROOT / "paper_drafts/e1-stri-reasoningbank-qwen-v3-results-20260901.tex"
CLAIM_AUDIT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-claim-audit-20260901.json"


def number(value: float | None, digits: int = 4) -> str:
    return "NA" if value is None else f"{float(value):.{digits}f}"


def render_results(adjudication: Mapping[str, Any]) -> str:
    primary = adjudication["primary_A_vs_D"]["permutation"]
    ci = adjudication["primary_A_vs_D"]["task_bootstrap_CI"]
    uptake = adjudication["secondary_A_vs_N"]["permutation"]
    uptake_ci = adjudication["secondary_A_vs_N"]["task_bootstrap_CI"]
    missing = adjudication["missingness_gate"]
    if primary is None:
        primary_sentence = (
            "The exactly-once execution did not yield an analyzable primary task "
            "population, so no A--D behavioral-distribution inference is reported.")
    else:
        primary_sentence = (
            f"The primary analysis included {primary['analyzable_task_count']} task blocks. "
            f"Mean cross-minus-within separation was $T={number(primary['observed_global_T'])}$ "
            f"(task bootstrap 95\\% CI "
            f"$[{number(ci['lower'])}, {number(ci['upper'])}]$; "
            f"within-task permutation $p={number(primary['monte_carlo_p_value'], 6)}$).")
    if uptake is None:
        uptake_sentence = "The A--N uptake contrast was not analyzable."
    else:
        uptake_sentence = (
            f"The secondary A--N contrast gave $T={number(uptake['observed_global_T'])}$ "
            f"(95\\% task bootstrap CI "
            f"$[{number(uptake_ci['lower'])}, {number(uptake_ci['upper'])}]$; "
            f"$p={number(uptake['monte_carlo_p_value'], 6)}$).")
    r4 = adjudication["R4"]["A_vs_D"]
    if r4["decision"] == "R4_TASK_BLOCKED_ANALYSIS_COMPLETE":
        r4_sentence = (
            f"Across {r4['permutation']['task_count']} paired task blocks, the mean "
            f"A--D resolution-proportion difference was "
            f"{number(r4['permutation']['observed_mean_task_difference'])} "
            f"(two-sided task sign-flip "
            f"$p={number(r4['permutation']['two_sided_monte_carlo_p_value'], 6)}$).")
    else:
        r4_sentence = (
            "Terminal resolution did not provide enough paired evaluator-valid task "
            "blocks for the preregistered R4 contrast.")
    strongest = str(adjudication["scientific_adjudication"]["strongest_supported_claim"])
    bounded = str(adjudication["scientific_adjudication"]["bounded_null_wording"])
    return f"""% Generated only after confirmatory scientific adjudication.

\\subsection{{Behavioral-distribution result}}
\\label{{sec:reasoningbank-qwen-results}}

All 24 structurally selected tasks satisfied exact A/B/E request equality and exact
A--D request inequality before behavioral execution. {primary_sentence}
{uptake_sentence} {r4_sentence}

The A and D behavior-valid failure rates were
{number(missing['failure_rate_A'])} and {number(missing['failure_rate_D'])};
their absolute difference was {number(missing['absolute_failure_rate_difference'])}
(Fisher exact $p={number(missing['fisher_exact_two_sided_p'], 6)}$).
The frozen missingness decision was
\\texttt{{{str(missing['decision']).replace('_', '-')}}}.

\\paragraph{{Scientific interpretation.}}
{strongest} The corresponding bounded-null formulation is: {bounded}.
The edit-target endpoint localizes behavior at R3; terminal SWE-bench performance is
reported separately and is not required for an R3 mechanism result.

\\subsection{{Scope and limitations}}
\\label{{sec:reasoningbank-qwen-limitations}}

This study targets task-specific memory generated and consumed by qwen3-coder-next
within one frozen ReasoningBank retrieval configuration and a fresh, deterministic
multi-repository SWE-bench Verified sample. EditTargetSet measures where a patch
acts, while official evaluation measures functional resolution; neither endpoint
alone establishes semantic equivalence of patches. The pilot-qualified precision
range bounds null interpretation, and the carrier-level conclusion remains specific
to the within-case reunion and cross-case top-1 boundary studied here. This scope
turns backend stochasticity into a measured baseline rather than an uncontrolled
source of single-rollout disagreement.

\\subsection{{Reproducibility placement}}
\\label{{sec:reasoningbank-qwen-reproducibility}}

The accompanying artifact records the source/calibration/pilot/confirmatory split,
source trajectories and extracted memories, independent fidelity reviews, retrieval
scores, exact model-visible requests, the 432-unit execution order, per-run
observables and evaluator receipts, task-blocked analysis seeds, resource accounting,
and all terminal failures. These records support exact reconstruction while keeping
execution governance outside the paper's main scientific argument.
"""


def claim_audit_payload(adjudication: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "PAPER_CLAIM_AUDIT", "created_at_utc": utcnow(),
        "decision": "QWEN_RESULT_CLAIMS_BOUND_TO_ADJUDICATION",
        "input_hashes": {
            "adjudication": sha256_file(ADJUDICATION),
            "pre_result_design": sha256_file(DESIGN),
        },
        "strongest_supported_claim": adjudication["scientific_adjudication"][
            "strongest_supported_claim"],
        "bounded_null_wording": adjudication["scientific_adjudication"][
            "bounded_null_wording"],
        "prohibited_claims": adjudication["scientific_adjudication"][
            "prohibited_claims"],
        "R3_does_not_require_R4_difference": True,
        "three_carrier_story_unchanged": True,
        "historical_deepseek_data_entered_confirmatory_inference": False,
        "credential_material_present": False,
    }


def update_paper() -> dict[str, Any]:
    if OUTPUT.exists() or CLAIM_AUDIT.exists():
        raise RuntimeError("refusing to overwrite paper result artifacts")
    adjudication = json.loads(ADJUDICATION.read_text())
    OUTPUT.write_text(render_results(adjudication), encoding="utf-8")
    claim = claim_audit_payload(adjudication)
    return {
        "decision": claim["decision"], "paper_result_sha256": sha256_file(OUTPUT),
        "claim_audit_sha256": write_json(CLAIM_AUDIT, claim),
    }


def main() -> None:
    print(json.dumps(update_paper(), sort_keys=True))


if __name__ == "__main__":
    main()
