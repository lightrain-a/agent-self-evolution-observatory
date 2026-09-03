#!/usr/bin/env python3
"""Freeze a pre-outcome paper-design method for B1 without authorizing execution.

R27 is manuscript/method design only. It does not consume R19 outcomes, does not
change the R19 contract, and does not authorize a new treatment. The design is
conditional on the final R19 adjudication and preserves a strong same-information
baseline rather than hard-coding a favorable SUCCESS/FAILURE direction.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
R19_CONTRACT = Path("generated/d2-failure-memory-provenance-l2b-r19-contract.json")
CLAIM_POLICY = Path("generated/d2-failure-memory-provenance-l2b-r19-claim-impact-policy.json")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    contract = json.loads(R19_CONTRACT.read_text(encoding="utf-8"))
    claim = json.loads(CLAIM_POLICY.read_text(encoding="utf-8"))
    if contract["primary_analysis"]["directional_sign_claim_predeclared"] is not False:
        raise RuntimeError("R19 sign must remain non-directional")
    if claim["authority"]["experiment"] is not False:
        raise RuntimeError("R27 must remain pre-execution method design")

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "design_id": "B1-PROVENANCE-SEPARATED-MEMORY-GOVERNANCE-R27",
        "recorded_date": "2026-08-24",
        "status": "PREOUTCOME_METHOD_DESIGN_FROZEN_NO_NEW_EXECUTION_AUTHORITY",
        "role": "PAPER_CLOSURE_METHOD_DESIGN_NOT_EFFECT_EVIDENCE",
        "bindings": {
            "r19_contract_sha256": sha(R19_CONTRACT),
            "r19_claim_policy_sha256": sha(CLAIM_POLICY),
        },
        "problem_to_method_loop": {
            "observed_problem": "Persistent-memory provenance can be associated with later outcomes, but the causal channel is ambiguous: source difficulty, writer mode, content, and explicit provenance metadata can all differ.",
            "identification_step": "The L0-L3 ladder separates observational association, writer-mode bundles, exact-information provenance metadata, and source-faithful transport.",
            "methodic_response": "Keep provenance as auditable control-plane state for the memory manager while projecting only selected actionable content to the executor. Use provenance to calibrate admission/routing/verification, not as an uncalibrated raw prompt token.",
            "paper_story": "phenomenon -> causal identification -> provenance-separated governance -> bounded validation",
        },
        "method": {
            "name": "Provenance-Separated Memory Governance",
            "short_name": "PSMG",
            "one_sentence": "PSMG preserves provenance for memory governance but separates it from executor-visible content, using a calibrated trust controller to decide whether and how a memory is reused.",
            "components": [
                {
                    "name": "Provenance ledger",
                    "input": "content-addressed memory record plus source-outcome and generation provenance",
                    "operation": "store provenance append-only outside the executor-visible memory text",
                    "why": "prevents provenance laundering while preserving an auditable source trail",
                },
                {
                    "name": "Same-information trust controller",
                    "input": "content relevance/utility features plus provenance and verification evidence available before the current downstream outcome",
                    "operation": "estimate expected reuse utility or risk with all comparator information matched",
                    "why": "avoids a hard-coded SUCCESS-good/FAILURE-bad rule and permits failure-derived memories to remain useful when evidence supports them",
                },
                {
                    "name": "Governance action",
                    "input": "controller score and frozen decision rule",
                    "operation": "admit, down-weight, request verification, or withhold a memory before execution",
                    "why": "turns provenance evidence into an operational response rather than stopping at diagnosis",
                },
                {
                    "name": "Executor-blind projection",
                    "input": "governance-approved memory content",
                    "operation": "send actionable content to the executor without the raw provenance label unless an explicitly tested executor-facing channel is required",
                    "why": "separates provenance-as-governance-signal from provenance-as-prompt-cue",
                },
            ],
            "default_rule": "No universal hard blacklist of failure-derived memories. Provenance modifies governance only through a pre-frozen calibrated rule using matched pre-outcome information.",
        },
        "strong_baselines_for_future_test": [
            "Content-only/default retrieval with provenance hidden",
            "Raw provenance-tag exposure with identical memory bytes (R19-type executor cue)",
            "Hard provenance blacklist/down-weight heuristic",
            "Content/relevance/verification-only utility controller without provenance",
            "Strongest same-information expected-utility controller given every pre-outcome feature available to PSMG except the provenance variable under test",
        ],
        "future_decisive_experiment_if_separately_authorized": {
            "fresh_units_required": True,
            "minimum_arms": [
                "content-only baseline",
                "raw provenance-tag exposure",
                "PSMG governance with executor-blind provenance",
            ],
            "preferred_additional_arm": "same-information content/relevance/verification-only controller without provenance",
            "primary_question": "Does provenance-separated governance improve terminal utility or reduce harmful reuse beyond the strongest same-information controller, without relying on raw provenance prompt cues?",
            "must_hold_fixed": [
                "memory content bytes",
                "candidate memory support",
                "executor model/manifest",
                "task distribution",
                "retrieval/content budget",
                "verification information",
                "evaluation endpoint",
                "analysis rule",
            ],
            "execution_authorized_now": False,
        },
        "conditional_manuscript_use": {
            "if_R19_support_gate_passes": "Promote PSMG from design implication to the proposed response mechanism, while still requiring a separately authorized mitigation experiment before claiming utility improvement.",
            "if_R19_complete_but_inconclusive": "Keep PSMG as a motivated design pattern and future experiment; do not claim that provenance-aware governance improves performance.",
            "if_R19_support_failure": "Do not upgrade PSMG from design implication; preserve only the identification framework and reopen condition.",
        },
        "novelty_boundary": {
            "not_claimed": [
                "provenance-aware memory is itself new",
                "trust scoring or routing is itself new",
                "failure-derived memory should always be suppressed",
            ],
            "candidate_novelty": "the separation of provenance as an auditable governance variable from executor-visible actionable content, tied to an explicit identification ladder that distinguishes writer, content, metadata, and transport channels",
            "closest_work_audit_required_before_novelty_claim": True,
        },
        "claim_boundary": {
            "R27_is_not_R19_effect_evidence": True,
            "R27_does_not_change_R19": True,
            "R27_does_not_authorize_new_treatment": True,
            "R27_does_not_authorize_claim_expansion": True,
            "R27_does_not_assume_R19_direction": True,
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
    }


def main() -> None:
    out = Path("generated/d2-failure-memory-provenance-psmg-method-design-r27.json")
    payload = build()
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "method": payload["method"]["short_name"], "execution_authorized": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
