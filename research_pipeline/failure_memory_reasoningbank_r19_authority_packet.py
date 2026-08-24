from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
CONTRACT = Path("generated/d2-failure-memory-provenance-l2b-r19-contract.json")
READINESS = Path("generated/d2-failure-memory-provenance-l2b-r19-readiness.json")
CLAIM_POLICY = Path("generated/d2-failure-memory-provenance-l2b-r19-claim-impact-policy.json")
R18C = Path("generated/d2-failure-memory-provenance-l2b-r18c-post-exposure-adjudication.json")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict[str, Any]:
    c = load(CONTRACT)
    r = load(READINESS)
    p = load(CLAIM_POLICY)
    r18 = load(R18C)
    if c["execution_gate"]["execution_permitted"] is not False:
        raise RuntimeError("R19 execution already permitted")
    if r["readiness"]["execution_ready_now"] is not False:
        raise RuntimeError("R19 readiness drift")
    if r18["frozen_policy_application"]["single_confirmatory_attempt_consumed"] is not True:
        raise RuntimeError("R18 stop boundary drift")
    if p["authority"]["experiment"] is not False:
        raise RuntimeError("claim policy must be pre-authority")

    exact_scope = {
        "scientific_object": "R19 new 35-template L2B metadata-only experiment; not R18 retry",
        "independent_tasks": 35,
        "terminal_episodes": 140,
        "memory": "reuse R17 exact frozen memory bytes; zero regeneration/editing",
        "treatment": "STATUS_S versus STATUS_F only; selected source record/order and actionable memory bytes identical across arms",
        "executor": "frozen content-addressed local Qwen executor under the R19 alias/transport contract",
        "prebenchmark_support_completions": 2,
        "benchmark_agent_completion_upper_bound": 4200,
        "benchmark_fuzzy_evaluator_completion_upper_bound": 600,
        "maximum_new_local_model_completions": 4802,
        "primary_endpoint": "official terminal WebArena score",
        "primary_analysis": "35 task-level deltas; two-sided sign-flip, 100000 permutations; |mean delta|>=0.15 and p<0.05",
        "full_completion_required": "140/140 valid terminal episodes",
    }

    authorization_text = (
        "Authorize R19 only under the frozen 35-task / 140-episode contract bound by this packet. "
        "Permit the two fixed nonbenchmark local transport smokes and, only if both pass before benchmark exposure, "
        "permit the frozen local model/browser/evaluator execution up to 4802 new local model completions total. "
        "Do not authorize R18 retry, task replacement, memory regeneration/editing, model-manifest/provider switching, "
        "threshold/endpoint/statistical changes, L3 transport, claim expansion, external paid API calls, or post-outcome sample extension. "
        "Scientific support is not granted in advance and must be determined only by the frozen R19 claim-impact policy."
    )

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "packet_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-AUTHORITY-DECISION-PACKET",
        "recorded_date": "2026-08-24",
        "status": "R19_AUTHORITY_DECISION_PACKET_READY_NOT_AUTHORIZED",
        "role": "HUMAN_DECISION_SUPPORT_NOT_AUTHORITY",
        "bindings": {
            "r19_contract_sha256": sha(CONTRACT),
            "r19_readiness_sha256": sha(READINESS),
            "r19_claim_policy_sha256": sha(CLAIM_POLICY),
            "r18c_stop_sha256": sha(R18C),
        },
        "decision_context": {
            "engineering_contract_ready": True,
            "authority_decision_ready": True,
            "execution_ready_without_new_authority": False,
            "R18_attempt_consumed_and_not_retriable": True,
            "R19_is_new_experiment": True,
            "R19_current_scientific_verdict": "NO_VERDICT_PRE_AUTHORITY",
        },
        "exact_scope_if_authorized": exact_scope,
        "mandatory_prebenchmark_sequence_if_authorized": [
            "Re-run zero-call alias/tokenizer registry preflight and live Shopping reset/BrowserGym support preflight.",
            "Run one fixed nonbenchmark synthetic completion through alias gpt-4; inspect only transport success/non-empty response.",
            "Run one fixed nonbenchmark synthetic completion through alias gpt-4-1106-preview; inspect only transport success/non-empty response.",
            "If either synthetic smoke fails, stop before any benchmark episode.",
            "If both pass, execute the frozen 140-episode schedule exactly once under the R19 retry/fail-closed rules.",
            "Apply only the precommitted R19 claim-impact branch after execution.",
        ],
        "authorization_text_for_human_decision": authorization_text,
        "decision_options": {
            "AUTHORIZE_EXACT_R19_SCOPE": "Human explicitly approves the authorization text or an unambiguously equivalent scope.",
            "DO_NOT_AUTHORIZE": "Keep R19 at pre-authority readiness; no benchmark or synthetic model completion is run.",
        },
        "not_authorized_by": [
            "this packet",
            "generic continuation language",
            "paper SUBMISSION_READY state",
            "prior R16 authority",
            "engineering readiness",
            "reviewer demand for O5 evidence",
        ],
        "current_authority": {
            "scientific": False,
            "experiment": False,
            "model_completions": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "gpu": False,
            "submission": False,
        },
        "verdict": "NO_AUTHORITY_DECISION_RECORDED",
    }


def main() -> None:
    out = Path("generated/d2-failure-memory-provenance-l2b-r19-authority-decision-packet.json")
    d = build()
    out.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": d["status"], "execution_ready": False, "authority": d["current_authority"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
