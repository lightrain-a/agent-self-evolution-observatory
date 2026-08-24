from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
SOURCE_ZIP = Path("downloads/D2-PAPER-FAILURE-MEMORY-PROVENANCE-source.zip")
EXPECTED_SOURCE_SHA = "932fadfe648aa5d440a54b74e69b72f5359773e31fbce888763f97bb28cce92c"
R19_CONTRACT = Path("generated/d2-failure-memory-provenance-l2b-r19-contract.json")
R19_READINESS = Path("generated/d2-failure-memory-provenance-l2b-r19-readiness.json")
R18C = Path("generated/d2-failure-memory-provenance-l2b-r18c-post-exposure-adjudication.json")

SECTIONS = [
    "source/sections/00_abstract.tex",
    "source/sections/01_intro.tex",
    "source/sections/04_intervention.tex",
    "source/sections/06_limitations_conclusion.tex",
    "source/sections/07_appendix.tex",
]


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def zip_member_bytes(zip_path: Path, member: str) -> bytes:
    p = subprocess.run(["unzip", "-p", str(zip_path), member], check=True, capture_output=True)
    return p.stdout


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict[str, Any]:
    if sha_file(SOURCE_ZIP) != EXPECTED_SOURCE_SHA:
        raise RuntimeError("B1 source ZIP drift")
    r19 = load(R19_CONTRACT)
    ready = load(R19_READINESS)
    r18c = load(R18C)
    if r19["status"] != "R19_PREOUTCOME_CONTRACT_FROZEN_NEW_AUTHORITY_AND_SYNTHETIC_SMOKES_REQUIRED":
        raise RuntimeError("R19 contract drift")
    if ready["status"] != "READY_FOR_NEW_R19_AUTHORITY_NOT_READY_FOR_EXECUTION":
        raise RuntimeError("R19 readiness drift")
    if r18c["scientific_verdict"] != "NO_VERDICT_POST_EXPOSURE_SUPPORT_FAILURE":
        raise RuntimeError("R18c verdict drift")
    if r19["execution_gate"]["execution_permitted"] is not False:
        raise RuntimeError("R19 unexpectedly executable")

    section_hashes = {m: hashlib.sha256(zip_member_bytes(SOURCE_ZIP, m)).hexdigest() for m in SECTIONS}
    analysis = r19["primary_analysis"]
    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "policy_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-POSTOUTCOME-CLAIM-POLICY",
        "recorded_date": "2026-08-24",
        "status": "R19_POSTOUTCOME_INTERPRETATION_AND_MANUSCRIPT_TRANSITIONS_FROZEN_PREOUTCOME",
        "role": "PREOUTCOME_CLAIM_INTERPRETATION_POLICY_NO_EXECUTION_AUTHORITY",
        "bindings": {
            "source_zip_sha256": EXPECTED_SOURCE_SHA,
            "source_section_sha256": section_hashes,
            "r19_contract_sha256": sha_file(R19_CONTRACT),
            "r19_readiness_sha256": sha_file(R19_READINESS),
            "r18c_adjudication_sha256": sha_file(R18C),
        },
        "primary_gate": {
            "independent_unit": "task",
            "independent_n": 35,
            "required_terminal_episodes": 140,
            "estimand": analysis["estimand"],
            "test": analysis["primary_test"],
            "alpha": analysis["alpha"],
            "practical_effect_floor_abs_delta": analysis["practical_effect_floor_abs_delta"],
            "support_if": analysis["support_if"],
            "otherwise": analysis["otherwise"],
            "equivalence_margin": None,
            "no_effect_claim_authorized": False,
        },
        "outcome_branches": {
            "A_SUPPORT_GATE_PASS": {
                "condition": "all 140 valid terminal episodes complete AND abs(mean_delta)>=0.15 AND p_two_sided<0.05",
                "scientific_status": "SUPPORTED_NARROWLY_ON_R19_COMPATIBILITY_SUBSTRATE",
                "allowed": [
                    "State that visible source-outcome provenance metadata causally changes terminal WebArena performance on the frozen R19 ReasoningBank/Shopping compatibility substrate when source record and actionable memory bytes are held fixed.",
                    "Report the observed R19 mean delta, two-sided p-value, task-level interval, and observed sign.",
                    "Upgrade L2 from design/support debt to an executed narrow metadata-only causal result on R19.",
                ],
                "forbidden": [
                    "failure-derived memories are generally harmful or generally helpful",
                    "endpoint-invariant provenance sign",
                    "first-party default Gemini policy replication",
                    "exact Python>=3.13 ReasoningBank runtime replication",
                    "financial AgentDojo L3 transport",
                    "cross-model, cross-runtime, or population prevalence generalization",
                    "pooling R4/R5/R6/bridge/R18/R19 into one effect estimate",
                ],
            },
            "B_FULL_EXECUTION_GATE_NOT_PASS": {
                "condition": "all 140 valid terminal episodes complete but support gate is not satisfied for any reason",
                "scientific_status": "INCONCLUSIVE_NO_NO_EFFECT_AUTHORITY",
                "allowed": [
                    "Report the complete R19 estimate, interval, and two-sided p-value.",
                    "State that the preregistered metadata-only test did not meet the joint practical-effect and significance support gate.",
                    "State that L2 was executed but remains unresolved under the frozen criterion.",
                ],
                "forbidden": [
                    "no effect",
                    "equivalence",
                    "provenance does not matter",
                    "using a directional p-value to rescue a failed two-sided primary",
                    "changing the 0.15 effect floor or alpha after outcome exposure",
                ],
            },
            "C_POST_EXPOSURE_SUPPORT_FAILURE": {
                "condition": "any unresolved support failure after an R19 model completion, browser action, or evaluator call",
                "scientific_status": "NO_VERDICT_SUPPORT_FAILURE",
                "allowed": [
                    "Report the support failure class and the exact exposure boundary.",
                    "Preserve all pre-outcome contracts and support receipts.",
                ],
                "forbidden": [
                    "retrying the affected episode under the same confirmatory attempt",
                    "treating partial cum_reward or incomplete evaluator state as a terminal score",
                    "continuing an invalid incomplete confirmatory schedule for a primary verdict",
                    "scientific positive or negative interpretation of the support failure",
                ],
            },
            "D_PRE_EXPOSURE_SUPPORT_FAILURE": {
                "condition": "support failure before the first R19 model completion, browser action, or evaluator call",
                "scientific_status": "NO_VERDICT_PREOUTCOME_SUPPORT_FAILURE",
                "allowed": [
                    "Use only the exact pre-exposure retry allowed by the newly authorized R19 contract, if that authority exists.",
                    "If the allowed retry cannot close support, stop before opening benchmark outcomes.",
                ],
                "forbidden": [
                    "task/model/memory/threshold substitution",
                    "opening outcomes on a partially repaired contract",
                ],
            },
        },
        "manuscript_transition_map": {
            "source/sections/00_abstract.tex": {
                "A_SUPPORT_GATE_PASS": "Replace the sentence that L2 stops before calls with one narrow executed R19 result sentence; retain L1 mixed-sign and L3-debt boundaries.",
                "B_FULL_EXECUTION_GATE_NOT_PASS": "Replace the R5-only L2 sentence with a complete-R19-but-inconclusive sentence; do not say no effect.",
                "C_OR_D_SUPPORT_FAILURE": "Do not promote R19 into the abstract as an effect result; at most retain L2 as unresolved and move support details to appendix/supplement.",
            },
            "source/sections/01_intro.tex": {
                "A_SUPPORT_GATE_PASS": "Update the ladder-population paragraph so L2 is populated by R19 and distinguish its compatibility-substrate scope from L3.",
                "B_FULL_EXECUTION_GATE_NOT_PASS": "State that a 35-task metadata-only R19 execution leaves L2 unresolved under the joint gate.",
                "C_OR_D_SUPPORT_FAILURE": "Keep the main contribution claim methodological; mention no causal sign upgrade.",
            },
            "source/sections/04_intervention.tex": {
                "A_SUPPORT_GATE_PASS": "Add a dedicated Exact-information metadata intervention subsection with R19 cohort, exact-byte hold-fixed contract, 140-episode schedule, task-level inference, and result.",
                "B_FULL_EXECUTION_GATE_NOT_PASS": "Add the same subsection but adjudicate it as inconclusive; report all primary statistics.",
                "C_OR_D_SUPPORT_FAILURE": "Add only a bounded execution-status paragraph if useful; no effect table using incomplete scores.",
            },
            "source/sections/06_limitations_conclusion.tex": {
                "A_SUPPORT_GATE_PASS": "Retire only the claim that L2 has never executed; retain compatibility-runtime, single-substrate, no-default-Gemini, and L3 limitations.",
                "B_FULL_EXECUTION_GATE_NOT_PASS": "Replace R5-only support-stop wording with executed-but-inconclusive R19 wording and retain no-effect prohibition.",
                "C_OR_D_SUPPORT_FAILURE": "Record R18/R19 support boundary without converting it into a scientific negative.",
            },
            "source/sections/07_appendix.tex": {
                "ALL_BRANCHES": "Add full R19 preregistration hashes, cohort construction, evaluator/alias preflights, budgets, retry policy, and branch-specific adjudication receipt.",
            },
        },
        "anti_story_shopping": {
            "outcome_branch_selected_by_rules_not_author": True,
            "R18_artifacts_cannot_select_R19_story": True,
            "R4_R6_directional_signs_cannot_override_R19_primary": True,
            "R19_secondary_or_early_action_endpoint_cannot_replace_terminal_primary": True,
            "posthoc_subgroup_or_task_removal_for_primary_claim": False,
        },
        "authority": {
            "scientific": False,
            "experiment": False,
            "model_completions": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "submission": False,
        },
        "verdict": "NO_VERDICT_PREOUTCOME_INTERPRETATION_POLICY_ONLY",
    }


def main() -> None:
    out = Path("generated/d2-failure-memory-provenance-l2b-r19-claim-impact-policy.json")
    payload = build()
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "branches": len(payload["outcome_branches"]), "execution_authority": payload["authority"]["experiment"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
