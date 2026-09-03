from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.agent_constraint_externality_sq0_v2r1_build import load_cases

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
RESULT = GENERATED / "agent-constraint-externality-sq0-v2r1-mimo25pro-result-20260903.json"
RUNTIME = ROOT / "runtimes/agent-constraint-externality-sq0-v2r1-mimo25pro-20260903"
LEDGER = RUNTIME / "ledger.jsonl"
CLOSEOUT = GENERATED / "agent-constraint-externality-sq0-v2r1-closeout-20260903.json"
DIAGNOSTIC = GENERATED / "agent-constraint-externality-sq0-v2r1-root-cause-20260903.json"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verified(path: Path, expected: str | None = None) -> dict[str, Any]:
    payload = _read(path)
    if payload.get("object_id") != OBJECT_ID:
        raise RuntimeError(f"Object mismatch: {path}")
    if expected is not None and payload.get("status") != expected:
        raise RuntimeError(f"Status mismatch: {path}: {payload.get('status')}")
    claimed = payload.get("content_sha256")
    if claimed is not None:
        unsigned = dict(payload); unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise RuntimeError(f"Content hash mismatch: {path}")
    return payload


def _ledger_rows() -> list[dict[str, Any]]:
    return [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]


def _actual_tnf_output(case: dict[str, Any]) -> str | None:
    db = RUNTIME / "episodes" / case["case_id"].lower() / "measurement-full-dbs" / "file_system.db"
    if not db.is_file():
        raise RuntimeError(f"Missing measurement DB for {case['case_id']}")
    con = sqlite3.connect(db)
    try:
        row = con.execute("SELECT content FROM files WHERE tilde_path = ?", (case["expected"]["output_path"],)).fetchone()
        return None if row is None else str(row[0])
    finally:
        con.close()


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    result = _verified(RESULT, "SQ0_V2R1_TARGET_CHALLENGE_TOO_EASY_STOP")
    rows = _ledger_rows()
    dispatch = [r for r in rows if r.get("event") == "DISPATCH"]
    completion = [r for r in rows if r.get("event") == "COMPLETION"]
    if len(dispatch) != 12 or len(completion) != 12:
        raise RuntimeError("V2R1 ledger is not exactly 12 DISPATCH + 12 COMPLETION.")
    if any(r.get("non_semantic_failure") or not r.get("tool_loop_completed") for r in completion):
        raise RuntimeError("V2R1 closeout expects no non-semantic/interface failures.")
    cases = {c["case_id"]: c for c in load_cases()}
    raw_failed = [r for r in completion if r.get("usable_target_failure")]
    if len(raw_failed) != 4:
        raise RuntimeError("Frozen V2R1 raw failure count drifted.")
    pseudo: list[dict[str, Any]] = []
    substantive: list[str] = []
    for row in raw_failed:
        case = cases[row["case_id"]]
        if not case["kind"].startswith("TNF_"):
            substantive.append(row["case_id"])
            continue
        expected = str(case["expected"]["output_content"])
        actual = _actual_tnf_output(case)
        terminal_newline_only = actual is not None and actual.rstrip("\n") == expected.rstrip("\n") and actual != expected
        if terminal_newline_only:
            pseudo.append({
                "case_id": row["case_id"],
                "classification": "TERMINAL_NEWLINE_ONLY",
                "expected_sha256": hashlib.sha256(expected.encode()).hexdigest(),
                "actual_sha256": hashlib.sha256(actual.encode()).hexdigest(),
                "normalized_equal": True,
            })
        else:
            substantive.append(row["case_id"])
    if len(pseudo) != 4 or substantive:
        raise RuntimeError("V2R1 post-aggregate failure diagnosis drifted.")
    rounds = sum(int(r["model_round_count"]) for r in completion)
    local_window_delta = 0
    reset_crossings: list[str] = []
    for r in completion:
        b, a = r["codingplan_window_before"], r["codingplan_window_after"]
        if b.get("next_reset_at") != a.get("next_reset_at"):
            reset_crossings.append(r["case_id"])
        else:
            local_window_delta += int(a["used"]) - int(b["used"])
    first, last = dispatch[0]["codingplan_window_before"], completion[-1]["codingplan_window_after"]
    first_last_delta = None
    if first.get("next_reset_at") == last.get("next_reset_at"):
        first_last_delta = int(last["used"]) - int(first["used"])
    diagnostic: dict[str, Any] = {
        "schema_version": "ace-sq0-v2r1-root-cause-v1",
        "object_id": OBJECT_ID,
        "status": "SQ0_V2R1_RAW_FAILURES_ARE_FORMATTING_PSEUDO_FAILURES",
        "raw_usable_failure_count": 4,
        "raw_usable_failure_rate": 4 / 12,
        "semantic_failure_count_after_terminal_newline_normalization": 0,
        "semantic_failure_rate_after_terminal_newline_normalization": 0.0,
        "pseudo_failure_cases": pseudo,
        "substantive_failure_cases": substantive,
        "by_kind": {
            "FG_JOIN_V2R1": {"case_count": 6, "raw_failure_count": 0},
            "TNF_JOIN_V2R1": {"case_count": 6, "raw_failure_count": 4, "formatting_pseudo_failure_count": 4},
        },
        "root_causes": [
            "FG_JOIN_V2R1 target challenge was solved substantively in all six fresh cases.",
            "TNF_JOIN_V2R1 joins/arithmetic/path were also solved in all six cases; four raw failures differed only by a terminal newline.",
            "The V2R1 evaluator therefore over-counted exact-format noise as target-learning opportunity.",
        ],
        "prospective_repairs_required": [
            "Normalize only terminal newline equivalence for prospective SQ0 file-content evaluation; preserve all internal bytes/fields/path checks.",
            "Increase target-local multi-source decision composition rather than adding distractor count alone.",
            "Use fresh V3 cases; never reclassify V2R1 as a pass and never reuse V2R1 cases for confirmatory F0-R1.",
        ],
        "provider_requests_added": 0,
        "scientific_effects_observed": 0,
        "authority": {"sq0_v3_design": True, "sq0_v3_execution": False, "f0_r1": False, "probe": False, "p1": False, "paper_claim": False},
    }
    diagnostic["content_sha256"] = sha256_value(diagnostic)
    closeout: dict[str, Any] = {
        "schema_version": "ace-sq0-v2r1-closeout-v1",
        "object_id": OBJECT_ID,
        "status": "SQ0_V2R1_TOO_EASY_CLOSEOUT",
        "verdict": result["status"],
        "result_artifact": str(RESULT.relative_to(ROOT)),
        "result_file_sha256": sha256_file(RESULT),
        "result_content_sha256": result["content_sha256"],
        "ledger_sha256": sha256_file(LEDGER),
        "raw_gate": {"usable_target_failure_count": 4, "usable_target_failure_rate": 4 / 12, "non_semantic_failure_units": []},
        "post_aggregate_semantic_diagnostic": {
            "semantic_failure_count": 0,
            "semantic_failure_rate": 0.0,
            "diagnostic_status": diagnostic["status"],
            "diagnostic_content_sha256": diagnostic["content_sha256"],
        },
        "accounting": {
            "scientific_model_round_count": rounds,
            "appworld_tool_call_total": sum(int(r["appworld_tool_call_count"]) for r in completion),
            "prompt_tokens_total": sum(int(r["prompt_tokens_total"]) for r in completion),
            "completion_tokens_total": sum(int(r["completion_tokens_total"]) for r in completion),
            "sum_case_local_account_window_delta": local_window_delta,
            "first_to_last_account_window_delta": first_last_delta,
            "account_level_requests_not_attributable_to_scientific_model_rounds": None if first_last_delta is None else first_last_delta - rounds,
            "reset_crossing_cases": reset_crossings,
            "accounting_domain_note": "CodingPlan window counts are account-wide and may include concurrent non-SQ0 requests; scientific model rounds come from live per-turn token events.",
        },
        "development_only": True,
        "confirmatory_reuse": False,
        "scientific_effects_observed": 0,
        "authority": {"current_sq0_v2r1": False, "sq0_v3_design": True, "sq0_v3_execution": False, "f0_r1": False, "probe": False, "p1": False, "paper_claim": False},
    }
    closeout["content_sha256"] = sha256_value(closeout)
    return closeout, diagnostic


def main() -> None:
    closeout, diagnostic = build()
    CLOSEOUT.write_text(json.dumps(closeout, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    DIAGNOSTIC.write_text(json.dumps(diagnostic, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": closeout["status"],
        "raw_failure_rate": closeout["raw_gate"]["usable_target_failure_rate"],
        "semantic_failure_rate": closeout["post_aggregate_semantic_diagnostic"]["semantic_failure_rate"],
        "scientific_model_rounds": closeout["accounting"]["scientific_model_round_count"],
        "sq0_v3_execution_authorized": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
