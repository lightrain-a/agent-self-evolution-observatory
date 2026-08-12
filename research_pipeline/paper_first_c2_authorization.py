from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_c2_contract import build_c2_contract
from .paper_first_collision_review import build_fresh_collision_review
from .paper_first_stop_triage import build_paper_first_stop_triage
from .paper_first_post_c2_adjudication import build_post_c2_adjudication

STRUCTURAL = PROJECT_ROOT / "generated" / "paper-first-c2-structural-precheck.json"
PROVENANCE = PROJECT_ROOT / "generated" / "paper-first-c2-provenance-authority.json"
REPLAY = PROJECT_ROOT / "generated" / "paper-first-replay-feasibility.json"
SUPPORT = PROJECT_ROOT / "research_pipeline" / "paper_first_c2_support_adjudication_20260812.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-c2-authorization.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-c2-authorization.js"

EXPECTED_STRUCTURAL_SHA256 = "ee3de70cd6296dd83dbed4e1f573c911b72a6219ce2101c9878f1f37e64e6fc3"
EXPECTED_PROVENANCE_SHA256 = "ad283b1098943d725553e38020851f654b5ce8b70a2a362ce5958a56f197ef0e"
EXPECTED_DEEPSEEK_RAW_SHA256 = "a1de0fe3ebb6cd321475aeee2e1cab514e3e969034bdab367c06e6c9439f2017"
EXPECTED_GLM_RAW_SHA256 = "0a32b8c9bf152bbcd1df1ba94c91fe52ad09e3ce07ad94413c46f45959250614"

POLICY = {
    "schema_version": "1.0",
    "authorization_scope": "exact strict-10 C2 local controlled-action falsifier only",
    "ai_is_advisory": True,
    "machine_gates_are_authoritative": True,
    "old_b9_formal_method_is_not_reopened": True,
    "parent_provenance_inconclusive_is_preserved": True,
    "C3_locked": True,
    "full_experiment_authorized": False,
    "second_backbone_authorized": False,
    "threshold_relaxation_authorized": False,
    "unit_replacement_authorized": False,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True).strip()
    except Exception:
        return "unknown"


def evaluate_c2_authorization(
    *,
    collision: dict[str, Any],
    triage: dict[str, Any],
    replay: dict[str, Any],
    support: dict[str, Any],
    structural: dict[str, Any],
    provenance: dict[str, Any],
    contract: dict[str, Any],
    structural_sha256: str,
    provenance_sha256: str,
) -> dict[str, Any]:
    paper_candidates = list(triage.get("paper_candidates") or [])
    candidate = paper_candidates[0] if len(paper_candidates) == 1 else {}
    audit = candidate.get("paper_design_audit") or {}
    reviewers = support.get("reviewers") or {}
    deepseek = reviewers.get("deepseek_v4_pro") or {}
    glm = reviewers.get("glm_5_2") or {}
    synthesis = support.get("synthesis") or {}
    structural_units = structural.get("units") or []
    structural_unique = {str(row.get("unit_id")) for row in structural_units if row.get("unit_id")}
    strict_units = set(str(x) for x in contract.get("strict_units") or [])
    regen = provenance.get("deterministic_nonzero_regeneration") or {}

    checks = [
        {
            "key": "fresh-collision-narrow-pass",
            "pass": str(collision.get("decision") or "").startswith("PASS_NARROW_"),
            "detail": collision.get("decision"),
        },
        {
            "key": "paper-design-audit-pass",
            "pass": bool(audit.get("passed") is True and not audit.get("blockers")),
            "detail": audit.get("summary") or audit.get("blockers"),
        },
        {
            "key": "environment-replay-pass",
            "pass": bool(
                replay.get("decision") == "ENVIRONMENT_REPLAY_FEASIBILITY_PASS"
                and (replay.get("summary") or {}).get("selected_tasks") == 20
                and (replay.get("summary") or {}).get("failed_units") == 0
            ),
            "detail": replay.get("summary"),
        },
        {
            "key": "traceable-reviewer-rule-frozen",
            "pass": bool(
                synthesis.get("decision") == "FREEZE_EXACT_10_UNIT_C2_RULE_PENDING_STRUCTURAL_PRECHECK"
                and int(synthesis.get("valid_units_required") or 0) == 10
                and int(synthesis.get("minimum_nonzero_tau_units") or 0) == 9
                and int(synthesis.get("minimum_parent_sign_concordant_units") or 0) == 9
                and synthesis.get("same_memory_three_context_sign_pattern_required") is True
                and deepseek.get("raw_sha256") == EXPECTED_DEEPSEEK_RAW_SHA256
                and glm.get("raw_sha256") == EXPECTED_GLM_RAW_SHA256
            ),
            "detail": {
                "decision": synthesis.get("decision"),
                "deepseek": deepseek.get("raw_sha256"),
                "glm": glm.get("raw_sha256"),
            },
        },
        {
            "key": "real-structural-precheck-artifact",
            "pass": bool(
                structural_sha256 == EXPECTED_STRUCTURAL_SHA256
                and structural.get("decision") == "C2_STRUCTURAL_PRECHECK_PASS"
                and structural.get("valid_units") == 10
                and structural.get("required_valid_units") == 10
                and structural.get("outcome_opened") is False
                and structural.get("tau_A_computed") is False
                and len(structural_unique) == 10
                and structural_unique == strict_units
                and all(bool(row.get("valid")) for row in structural_units)
            ),
            "detail": {
                "sha256": structural_sha256,
                "decision": structural.get("decision"),
                "valid_units": structural.get("valid_units"),
            },
        },
        {
            "key": "parent-provenance-preserved-not-reinterpreted",
            "pass": bool(
                provenance_sha256 == EXPECTED_PROVENANCE_SHA256
                and provenance.get("decision") == "PROVENANCE_INCONCLUSIVE"
                and provenance.get("paper_level_scientific_authority") is False
                and provenance.get("formal_method_experiment_authorized") is False
                and int(regen.get("nonzero_units") or 0) == 11
                and int(regen.get("controlled_effect_sign_matches") or 0) == 10
                and int(regen.get("controlled_effect_sign_mismatches") or 0) == 1
                and regen.get("gpu_uuid") == contract["runtime"]["gpu_uuid"]
                and regen.get("model_path") == contract["runtime"]["model_path"]
            ),
            "detail": {
                "sha256": provenance_sha256,
                "parent_decision": provenance.get("decision"),
                "sign_matches": regen.get("controlled_effect_sign_matches"),
                "sign_mismatches": regen.get("controlled_effect_sign_mismatches"),
            },
        },
        {
            "key": "c2-contract-exact-scope",
            "pass": bool(
                len(strict_units) == 10
                and contract["frozen_gate"]["go"].get("valid_units") == 10
                and contract["frozen_gate"]["go"].get("minimum_nonzero_tau_units") == 9
                and contract["frozen_gate"]["go"].get("minimum_parent_sign_concordant_units") == 9
                and contract["frozen_gate"]["go"].get("same_memory_cross_context_sign_reversal_required") is True
                and contract["frozen_gate"].get("no_threshold_relaxation") is True
                and contract["frozen_gate"].get("no_unit_rescue") is True
                and contract["post_c2"].get("C3_locked") is True
                and contract["post_c2"].get("full_experiment_authorized") is False
            ),
            "detail": contract.get("frozen_gate"),
        },
    ]
    passed = sum(bool(row["pass"]) for row in checks)
    authorized = passed == len(checks)
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "paper_id": "trajectory-mediated-memory-effect-transport",
        "decision": "C2_LOCAL_VALIDATION_AUTHORIZED" if authorized else "C2_LOCAL_VALIDATION_LOCKED",
        "code_commit": _commit(),
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
        "local_validation_authorized": authorized,
        "authorized_command_scope": "paper_first_c2_local on strict 10 only" if authorized else None,
        "C3_locked": True,
        "full_experiment_authorized": False,
        "old_b9_formal_method_reopened": False,
        "next_action": (
            "run the exact C2 local falsifier on the frozen 60 parent runtime; C3 remains locked"
            if authorized
            else "resolve failed machine authorization checks before any C2 outcome is opened"
        ),
        "policy": POLICY,
    }


def build_c2_authorization() -> dict[str, Any]:
    post_c2 = build_post_c2_adjudication()
    if (post_c2.get("authority") or {}).get("clean_mechanism_stop") is True:
        return {
            "schema_version": "1.0",
            "generated_at": _now(),
            "paper_id": "trajectory-mediated-memory-effect-transport",
            "decision": "C2_LOCAL_VALIDATION_TERMINAL_LOCKED",
            "code_commit": _commit(),
            "checks_passed": 0,
            "checks_total": 0,
            "checks": [],
            "local_validation_authorized": False,
            "authorized_command_scope": None,
            "C3_locked": True,
            "full_experiment_authorized": False,
            "old_b9_formal_method_reopened": False,
            "terminal_post_c2_decision": post_c2.get("decision"),
            "terminal_post_c2_c2_decision_sha256": (post_c2.get("c2_result") or {}).get("decision_sha256"),
            "historical_machine_authorization_recheck_skipped": True,
            "next_action": "C2 has already completed and terminalized the current paper mechanism; archive the formulation and do not rerun C2.",
            "policy": {**POLICY, "post_c2_terminal_lock": True},
        }
    collision = build_fresh_collision_review()
    triage = build_paper_first_stop_triage()
    replay = _load(REPLAY)
    support = _load(SUPPORT)
    structural = _load(STRUCTURAL)
    provenance = _load(PROVENANCE)
    contract = build_c2_contract()
    return evaluate_c2_authorization(
        collision=collision,
        triage=triage,
        replay=replay,
        support=support,
        structural=structural,
        provenance=provenance,
        contract=contract,
        structural_sha256=_sha(STRUCTURAL),
        provenance_sha256=_sha(PROVENANCE),
    )


def write_c2_authorization(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_c2_authorization()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_C2_AUTHORIZATION = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_c2_authorization(), ensure_ascii=False, indent=2))
