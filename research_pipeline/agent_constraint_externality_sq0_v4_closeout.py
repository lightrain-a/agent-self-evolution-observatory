from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.agent_constraint_externality_sq0_v4_build import load_cases

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
RESULT = GENERATED / "agent-constraint-externality-sq0-v4-mimo25pro-result-20260903.json"
RUNTIME = ROOT / "runtimes/agent-constraint-externality-sq0-v4-mimo25pro-20260903"
LEDGER = RUNTIME / "ledger.jsonl"
CLOSEOUT = GENERATED / "agent-constraint-externality-sq0-v4-closeout-20260903.json"
ROOT_CAUSE = GENERATED / "agent-constraint-externality-sq0-v4-root-cause-20260903.json"
SERIALIZATION_ONLY = ("SQ0V4-TNF-01", "SQ0V4-TNF-02", "SQ0V4-TNF-03")
SEMANTIC_SELECTION = ("SQ0V4-TNF-04", "SQ0V4-TNF-05", "SQ0V4-TNF-06")


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verified(path: Path, status: str | None = None) -> dict[str, Any]:
    payload = _read(path)
    if payload.get("object_id") != OBJECT_ID:
        raise RuntimeError(f"Object mismatch: {path}")
    if status is not None and payload.get("status") != status:
        raise RuntimeError(f"Status mismatch: {path}: {payload.get('status')}")
    claimed = payload.get("content_sha256")
    unsigned = dict(payload); unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise RuntimeError(f"Hash mismatch: {path}")
    return payload


def _actual_output(case: dict[str, Any]) -> tuple[str | None, str | None]:
    episode = RUNTIME / "episodes" / case["case_id"].lower()
    db = episode / "measurement-full-dbs/file_system.db"
    con = sqlite3.connect(db); con.row_factory = sqlite3.Row
    try:
        expected_path = case["expected"]["output_path"]
        row = con.execute("select tilde_path,content from files where tilde_path=?", (expected_path,)).fetchone()
        if row is not None:
            return str(row["tilde_path"]), str(row["content"])
        prefix = expected_path.rsplit("/", 1)[0] + "/sq0v4-output-"
        rows = con.execute("select tilde_path,content from files where tilde_path like ? order by id", (prefix + "%",)).fetchall()
        created = [r for r in rows if not str(r["tilde_path"]).endswith(("adjust-01.txt","adjust-02.txt","adjust-03.txt","adjust-04.txt","adjust-05.txt","adjust-06.txt"))]
        if len(created) != 1:
            return None, None
        return str(created[0]["tilde_path"]), str(created[0]["content"])
    finally:
        con.close()


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    result = _verified(RESULT, "SQ0_V4_TARGET_CHALLENGE_TOO_HARD_STOP")
    if result.get("completed_case_count") != 12 or result.get("usable_target_failure_count") != 11 or result.get("target_success_count") != 1:
        raise RuntimeError("V4 aggregate drifted.")
    if result.get("non_semantic_failure_units") != []:
        raise RuntimeError("V4 closeout expects zero non-semantic failures.")
    cases = {c["case_id"]: c for c in load_cases()}
    audits: dict[str, Any] = {}
    for cid in SERIALIZATION_ONLY + SEMANTIC_SELECTION:
        case = cases[cid]
        actual_path, actual_content = _actual_output(case)
        expected_path = case["expected"]["output_path"]
        expected_content = case["expected"]["output_content"]
        audits[cid] = {
            "expected_path_sha256": sha256_value(expected_path),
            "actual_path_sha256": sha256_value(actual_path) if actual_path else None,
            "path_exact": actual_path == expected_path,
            "expected_content_sha256": sha256_value(expected_content.rstrip("\n")),
            "actual_content_sha256": sha256_value((actual_content or "").rstrip("\n")),
            "content_exact_after_terminal_newline_normalization": (actual_content or "").rstrip("\n") == expected_content.rstrip("\n"),
            "expected_total": expected_content.rstrip("\n").splitlines()[-1].removeprefix("TOTAL="),
            "actual_last_field": (actual_content or "").rstrip("\n").splitlines()[-1].removeprefix("TOTAL=") if actual_content else None,
        }
    if not all(audits[cid]["path_exact"] and audits[cid]["expected_total"] == audits[cid]["actual_last_field"] for cid in SERIALIZATION_ONLY):
        raise RuntimeError("Serialization-only audit drifted.")
    if any(audits[cid]["path_exact"] for cid in SEMANTIC_SELECTION):
        raise RuntimeError("Semantic-selection audit drifted.")
    root: dict[str, Any] = {
        "schema_version": "ace-sq0-v4-root-cause-v1",
        "object_id": OBJECT_ID,
        "status": "SQ0_V4_TOO_HARD_WITH_SERIALIZATION_AND_SEMANTIC_FAILURE_MIX",
        "development_iteration": 4,
        "frozen_v4_verdict_unchanged": result["status"],
        "tnf_serialization_schema_failure_units": list(SERIALIZATION_ONLY),
        "tnf_semantic_selection_failure_units": list(SEMANTIC_SELECTION),
        "audits": audits,
        "diagnosis": [
            "TNF-01/02/03 reached the exact expected output path and exact expected total but serialized source resource identities instead of the required policy/token/value fields.",
            "TNF-04/05/06 produced a different output path, proving at least one semantic task/content selection error independent of serialization.",
            "V5 should remove serialization ambiguity prospectively while preserving the V4 semantic decision graph and using entirely fresh cases.",
        ],
        "prospective_v5_constraints": {
            "fresh_cases_only": True,
            "reuse_v4_case_bytes": False,
            "fg_mechanism_change": "NONE; FRESH_PARAMETERIZATION_ONLY",
            "tnf_semantic_decision_graph_change": "NONE",
            "tnf_serialization_change": "EXPLICIT_FIELD_TO_SOURCE_ATTRIBUTE_MAPPING",
            "terminal_newline_only_normalization_retained": True,
            "tool_budget_not_used_as_difficulty_knob": True,
            "v5_is_final_sq0_calibration_iteration": True,
        },
        "provider_requests_added": 0,
        "scientific_effects_observed": 0,
        "authority": {"sq0_v5_design": True, "sq0_v5_execution": False, "f0_r1": False, "probe": False, "p1": False, "paper_claim": False},
    }
    root["content_sha256"] = sha256_value(root)
    rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
    completions = [r for r in rows if r.get("event") == "COMPLETION"]
    by_kind = {}
    for kind in ("FG_SEMANTIC_V4", "TNF_SEMANTIC_V4"):
        subset = [r for r in completions if r.get("kind") == kind]
        by_kind[kind] = {"completed": len(subset), "usable_target_failures": sum(bool(r.get("usable_target_failure")) for r in subset), "target_successes": sum(bool(r.get("target_success")) for r in subset)}
    if by_kind != {"FG_SEMANTIC_V4":{"completed":6,"usable_target_failures":5,"target_successes":1},"TNF_SEMANTIC_V4":{"completed":6,"usable_target_failures":6,"target_successes":0}}:
        raise RuntimeError(f"V4 by-kind aggregate drifted: {by_kind}")
    closeout: dict[str, Any] = {
        "schema_version": "ace-sq0-v4-closeout-v1",
        "object_id": OBJECT_ID,
        "status": "SQ0_V4_TOO_HARD_CLOSEOUT",
        "verdict": result["status"],
        "result_artifact": str(RESULT.relative_to(ROOT)),
        "result_file_sha256": sha256_file(RESULT),
        "result_content_sha256": result["content_sha256"],
        "ledger_sha256": sha256_file(LEDGER),
        "completed_case_count": 12,
        "usable_target_failure_count": 11,
        "target_success_count": 1,
        "usable_target_failure_rate": 11/12,
        "acceptable_failure_count": [9,10],
        "by_kind": by_kind,
        "root_cause_content_sha256": root["content_sha256"],
        "accounting": {"scientific_model_round_count": result["scientific_model_round_count"], "appworld_tool_call_total": result["appworld_tool_call_total"], "prompt_tokens_total": result["prompt_tokens_total"], "completion_tokens_total": result["completion_tokens_total"]},
        "development_only": True,
        "confirmatory_reuse": False,
        "scientific_effects_observed": 0,
        "authority": {"current_sq0_v4": False, "sq0_v5_design": True, "sq0_v5_execution": False, "f0_r1": False, "probe": False, "p1": False, "paper_claim": False},
    }
    closeout["content_sha256"] = sha256_value(closeout)
    return closeout, root


def main() -> None:
    closeout, root = build()
    CLOSEOUT.write_text(json.dumps(closeout, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    ROOT_CAUSE.write_text(json.dumps(root, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps({"status": closeout["status"], "failures": 11, "serialization_only_tnf": 3, "semantic_selection_tnf": 3, "v5_execution_authorized": False}, sort_keys=True))


if __name__ == "__main__":
    main()
