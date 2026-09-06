from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline import agent_constraint_externality_atomgit_repair_common as c
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "generated"
OUTPUT = G / "agent-constraint-externality-atomgit-repeat-dev-repair-closeout-20260906.json"
NOTE = ROOT / "consultations/agent-constraint-externality-atomgit-repeat-dev-repair-closeout-20260906.md"


class CloseoutError(RuntimeError):
    pass


def build() -> dict[str, Any]:
    result = c.verified(c.RESULT, "ATOMGIT_REPEAT_DEV_SIX_REPAIRS_FROZEN_REPEAT_AUTHORITY_CLOSED")
    manifest = c.verified(c.MANIFEST, "ATOMGIT_REPEAT_DEV_SIX_REPAIRS_FROZEN_REPEAT_AUTHORITY_CLOSED")
    projection = c.projection()
    ids = c.selected_ids(projection)
    if result["repair_count"] != 6 or manifest["repair_count"] != 6 or set(manifest["repairs"]) != set(ids):
        raise CloseoutError("six-repair terminal geometry drift")
    if result["manifest_content_sha256"] != manifest["content_sha256"]:
        raise CloseoutError("result/manifest content binding drift")
    if result["ledger_sha256"] != manifest["ledger_sha256"] or result["ledger_sha256"] != sha256_file(c.LEDGER):
        raise CloseoutError("repair ledger binding drift")
    rows = c.ledger_rows()
    dispatch = [row for row in rows if row.get("event") == "DISPATCH"]
    complete = [row for row in rows if row.get("event") == "COMPLETION"]
    failure = [row for row in rows if row.get("event") == "FAILURE"]
    if len(dispatch) != 6 or len(complete) != 6 or failure:
        raise CloseoutError("repair exactly-once terminal geometry drift")
    if {row["unit_id"] for row in dispatch} != {row["unit_id"] for row in complete}:
        raise CloseoutError("repair dispatch/completion set mismatch")

    audit: dict[str, Any] = {}
    for family_id in ids:
        record = manifest["repairs"][family_id]
        repair_path = ROOT / record["repair_path"]
        raw_path = ROOT / record["raw_repair_path"]
        if not repair_path.is_file() or sha256_file(repair_path) != record["repair_sha256"]:
            raise CloseoutError(f"repair bytes drift: {family_id}")
        if not raw_path.is_file() or sha256_file(raw_path) != record["raw_repair_sha256"]:
            raise CloseoutError(f"raw repair bytes drift: {family_id}")
        if record.get("human_edited") is not False:
            raise CloseoutError(f"human edit flag drift: {family_id}")
        family_projection = projection["families"][family_id]
        if record["projected_tool_trajectory_sha256"] != family_projection["projected_tool_trajectory_sha256"]:
            raise CloseoutError(f"projected trajectory binding drift: {family_id}")
        if record["target_failure_slice_sha256"] != family_projection["target_failure_slice_sha256"]:
            raise CloseoutError(f"failure slice binding drift: {family_id}")
        text = repair_path.read_text(encoding="utf-8")
        if any(term in text.lower() for term in c.FORBIDDEN_REPAIR_TERMS):
            raise CloseoutError(f"structural term contamination: {family_id}")
        audit[family_id] = {
            "repair_sha256": record["repair_sha256"],
            "repair_byte_length": int(record["repair_byte_length"]),
            "repair_word_count": len(text.split()),
            "generation_model_round_count": int(record["generation_model_round_count"]),
            "projected_tool_trajectory_sha256": record["projected_tool_trajectory_sha256"],
            "target_failure_slice_sha256": record["target_failure_slice_sha256"],
            "human_edited": False,
        }

    out: dict[str, Any] = {
        "schema_version": "ace-repeat-dev-repair-closeout-v1",
        "object_id": OBJECT_ID,
        "status": "ATOMGIT_REPEAT_DEV_SIX_REPAIRS_FROZEN_READY_FOR_ZERO_PROVIDER_REPEAT_PREP",
        "repair_result_content_sha256": result["content_sha256"],
        "repair_result_file_sha256": sha256_file(c.RESULT),
        "repair_manifest_content_sha256": manifest["content_sha256"],
        "repair_manifest_file_sha256": sha256_file(c.MANIFEST),
        "repair_ledger_sha256": sha256_file(c.LEDGER),
        "projection_content_sha256": projection["content_sha256"],
        "selected_family_ids": projection["selected_family_ids"],
        "repair_integrity": audit,
        "exactly_once": {
            "dispatch_count": 6,
            "completion_count": 6,
            "failure_count": 0,
            "dispatch_completion_unit_sets_equal": True,
            "model_round_count": sum(int(row.get("model_round_count", 0)) for row in complete),
        },
        "post_freeze_manual_inspection": {
            "occurred": True,
            "purpose": "read-only integrity/face-validity inspection after all six repair bytes were already frozen",
            "semantic_concern_observed": True,
            "concern_summary": "At least two FG notes appeared internally questionable or self-contradictory on manual reading.",
            "human_edits": 0,
            "repair_regeneration": 0,
            "family_exclusion": 0,
            "family_replacement": 0,
            "repair_selection_by_apparent_quality": False,
            "effectiveness_manual_adjudication_authority": False,
            "policy": "All six exact frozen repair byte strings remain in the development repeat panel. Their behavioral effect is measured only by the preregistered evaluator; manual plausibility cannot alter the panel.",
        },
        "interpretation": "This closeout establishes only six frozen target-only model-generated repair artifacts with intact provenance. It is not repair-uptake, collateral-externality, topology, or paper-claim evidence.",
        "scientific_externality_outcomes_observed": 0,
        "provider_requests_created_by_closeout": 0,
        "authority": {
            "repair_generation_closed": True,
            "development_repeat_qualification": False,
            "target_only_verification": False,
            "rq1_rq2": False,
            "rq3": False,
            "rq4": False,
            "paper_claim": False,
        },
        "next_legal_action": "Zero-provider R*=2 development repeat-panel implementation, tests, and readiness only. Provider execution requires a separate human authority.",
    }
    out["content_sha256"] = sha256_value(out)
    OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    NOTE.write_text(
        "# Agent Constraint Externality — six-repair closeout\n\n"
        "Date: 2026-09-06\n\n"
        "## Verdict\n\n"
        "`ATOMGIT_REPEAT_DEV_SIX_REPAIRS_FROZEN_READY_FOR_ZERO_PROVIDER_REPEAT_PREP`\n\n"
        "Six development repair artifacts are frozen with 6 DISPATCH / 6 COMPLETION / 0 FAILURE and exactly one MiMo-V2.5-Pro model round per repair. No repeat/topology episode has been authorized or executed by this closeout.\n\n"
        "## Post-freeze manual inspection boundary\n\n"
        "A read-only manual inspection occurred only after all six repair byte strings were frozen. At least two FG notes appeared semantically questionable or self-contradictory. This observation has zero selection authority: no repair was edited, regenerated, dropped, replaced, or preferred based on apparent quality. All six exact repair byte strings remain fixed for the development repeat panel, where the preregistered evaluator—not human plausibility—determines behavioral effect.\n\n"
        "## Authority\n\n"
        "Repair generation is closed. Development repeat qualification, TARGET_ONLY_VERIFICATION, RQ1/RQ2, RQ3, RQ4, and paper claims all remain closed. The next legal action is zero-provider R*=2 runner/readiness preparation only.\n",
        encoding="utf-8",
    )
    return out


def main() -> None:
    print(json.dumps(build(), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
