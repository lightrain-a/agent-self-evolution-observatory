from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_confirmatory_preexec import sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "generated/agent-constraint-externality-confirmatory-preexec-freeze-20260904.json"
AUDIT = ROOT / "generated/agent-constraint-externality-confirmatory-preexec-audit-20260904.json"
PROPOSAL = ROOT / "generated/agent-constraint-externality-confirmatory-execution-proposal-20260904.json"
OUTPUT = ROOT / "generated/agent-constraint-externality-confirmatory-preexec-closeout-20260904.json"


class CloseoutError(RuntimeError):
    pass


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise CloseoutError(f"missing closeout input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict[str, Any]:
    freeze = load(FREEZE)
    audit = load(AUDIT)
    proposal = load(PROPOSAL)
    if freeze.get("status") != "ZERO_PROVIDER_PREEXEC_FREEZE_COMPLETE_EXECUTION_AUTHORITY_CLOSED":
        raise CloseoutError("preexec freeze status is not closed/pass-ready")
    if audit.get("status") != "PASS_PREEXEC_CONSISTENCY_EXECUTION_AUTHORITY_CLOSED" or audit.get("failed_checks") != []:
        raise CloseoutError("preexec audit did not pass")
    if any(bool(v) for v in proposal.get("authority", {}).values()):
        raise CloseoutError("execution proposal unexpectedly has authority")
    if any(bool(v) for v in freeze.get("authority", {}).values()) or any(bool(v) for v in audit.get("authority", {}).values()):
        raise CloseoutError("preexec objects unexpectedly have authority")
    payload = {
        "schema_version": 1,
        "object_id": "AGENT-CONSTRAINT-EXTERNALITY-CONFIRMATORY-PREEXEC-CLOSEOUT-20260904",
        "recorded_date": "2026-09-04",
        "status": "PREEXEC_DESIGN_DETAILS_FROZEN_PROVIDER_AND_EXECUTION_AUTHORITY_CLOSED",
        "scientific_object": "AGENT-CONSTRAINT-EXTERNALITY-20260831",
        "closed_questions": [
            "exact topology-neutral TARGET_ONLY_VERIFICATION eligibility surface",
            "exact pre-topology target-uptake threshold (+0.50)",
            "exact development repeat-stability rule for R*=2 versus R*=3",
            "hard stochasticity stop with R>3 forbidden",
            "effect-direction-blind N* precision selection over {12,16,20,24}",
            "stable-hash reserve selection with no post-topology backfill",
            "post-treatment target outcomes retained rather than used for family deletion",
        ],
        "still_closed": [
            "provider credit/readiness execution check",
            "Gate 0 direct actor execution",
            "Gate 1 Direct-SFQ-A0 execution",
            "development repeat qualification execution",
            "TARGET_ONLY_VERIFICATION execution",
            "RQ1/RQ2 confirmatory execution",
            "RQ3 held-out execution",
            "RQ4 GTCC execution",
            "secondary actor/external updater",
            "paper claim expansion",
        ],
        "provenance": {
            "freeze_file_sha256": sha256_file(FREEZE),
            "freeze_content_sha256": freeze.get("content_sha256"),
            "audit_file_sha256": sha256_file(AUDIT),
            "audit_content_sha256": audit.get("content_sha256"),
            "execution_proposal_file_sha256": sha256_file(PROPOSAL),
        },
        "authority": {
            "provider_execution": False,
            "gate0": False,
            "gate1": False,
            "development_repeat_qualification": False,
            "target_only_verification": False,
            "rq1_rq2": False,
            "rq3": False,
            "rq4": False,
            "secondary_actor": False,
            "external_updater": False,
            "paper_claim": False,
        },
        "scientific_provider_calls_created": 0,
        "scientific_outcomes_created": 0,
        "next_legal_action": "PROVIDER_READINESS_CHECK_THEN_SEPARATE_HUMAN_EXECUTION_AUTHORITY; DO_NOT DISPATCH SCIENTIFIC UNITS YET",
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    payload = build()
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "content_sha256": payload["content_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
