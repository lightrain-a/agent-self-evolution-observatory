#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "generated"
PDF_DIR = ROOT / "downloads" / "advisor-20260906"
ORDER = ["E1", "B1", "C1", "G1", "E2", "PAPER_A", "CONSTRAINT_EXTERNALITY", "PAPER_B", "3D"]
ROUTES = {"FREEZE_SUBMIT", "EXECUTE_FROZEN", "QUALIFY_FIRST", "FORMALIZE_FIRST"}
RESOURCE_DIMENSIONS = ["api_cash", "local_gpu_occupancy", "post_meeting_execution_human_hours", "provider_credential_dependency", "calendar_latency"]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(paths: list[Path]) -> tuple[str, list[dict]]:
    rows = []
    for p in sorted(paths, key=lambda x: str(x.relative_to(ROOT))):
        rows.append({"path": str(p.relative_to(ROOT)), "sha256": sha(p)})
    payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest(), rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate/freeze the advisor meeting candidate")
    parser.add_argument("--check", action="store_true", help="Fail if the committed freeze receipt does not match the current sources; do not rewrite it")
    args = parser.parse_args()
    errors: list[str] = []
    manifest = load(G / "advisor-paper-pack-manifest.json")
    reality = load(G / "advisor-reality-support.json")
    resources = load(G / "advisor-resource-ledger.json")
    overlay = load(G / "advisor-reality-cost-independent-review-20260905.json")
    overlay_fix = load(G / "advisor-reality-cost-fix-closure-20260905.json")
    final_attempt = load(G / "advisor-final-decision-sufficiency-review-attempt-20260905.json")
    final_review = load(G / "advisor-final-decision-sufficiency-review-20260906.json")
    agenda = load(G / "advisor-meeting-agenda-20260906.json")
    final_fix = load(G / "advisor-final-decision-sufficiency-fix-closure-20260906.json")

    cards = {}
    card_paths = []
    for p in sorted((G / "advisor-decision-cards").glob("*.json")):
        d = load(p)
        cards[d["paper_id"]] = d
        card_paths.append(p)

    manifest_ids = [p["paper_id"] for p in manifest.get("papers", [])]
    if manifest_ids != ORDER:
        errors.append(f"paper manifest order mismatch: {manifest_ids}")
    if sorted(cards) != sorted(ORDER):
        errors.append(f"decision-card ids mismatch: {sorted(cards)}")
    if sorted((reality.get("papers") or {}).keys()) != sorted(ORDER):
        errors.append("reality-support ids mismatch")
    if sorted((resources.get("papers") or {}).keys()) != sorted(ORDER):
        errors.append("resource-ledger ids mismatch")

    review_paths = []
    for pid in ORDER:
        rp = G / f"stanford-{pid.lower()}-review.json"
        review_paths.append(rp)
        if not rp.exists():
            errors.append(f"missing Stanford review: {pid}")
            continue
        r = load(rp)
        if r.get("status") != "READY":
            errors.append(f"Stanford review not READY: {pid}")
        if not (r.get("authority") or {}).get("external_review_advisory_only"):
            errors.append(f"Stanford advisory authority missing: {pid}")
        if r.get("score_is_official_venue_score") is not False:
            errors.append(f"Stanford score incorrectly marked official: {pid}")

    for p in manifest.get("papers", []):
        pid = p["paper_id"]
        pdf = PDF_DIR / p["filename"]
        if not pdf.exists():
            errors.append(f"missing PDF: {pid}")
        elif sha(pdf) != p["pdf_sha256"]:
            errors.append(f"PDF SHA mismatch: {pid}")

        c = cards.get(pid, {})
        if c.get("route") not in ROUTES:
            errors.append(f"invalid route {pid}: {c.get('route')}")
        for field in ["best_case", "story", "premise", "risk", "strongest_simplification", "evidence_state", "next_closure", "default_action", "override_trigger", "cross_paper_leverage", "advisor_question"]:
            if not str(c.get(field) or "").strip():
                errors.append(f"missing card field {pid}.{field}")

        rr = (resources.get("papers") or {}).get(pid, {})
        auth = rr.get("authorized_now") or {}
        dims = rr.get("resource_dimensions") or {}
        if list(dims.keys()) != RESOURCE_DIMENSIONS:
            errors.append(f"resource dimension order mismatch: {pid}: {list(dims.keys())}")
        if c.get("route") in {"FREEZE_SUBMIT", "FORMALIZE_FIRST"}:
            if str(auth.get("gpu")) != "0" or auth.get("api_units") not in (0, "0"):
                errors.append(f"{pid} route {c.get('route')} has nonzero current compute commitment")
        if c.get("route") == "EXECUTE_FROZEN":
            if str(auth.get("gpu")) == "0" and auth.get("api_units") in (0, "0"):
                errors.append(f"{pid} EXECUTE_FROZEN has no current execution resource")
        if c.get("route") == "QUALIFY_FIRST" and auth.get("api_units") in (0, "0"):
            action = str(c.get("default_action") or "")
            if action.startswith("RUN_"):
                errors.append(f"{pid} default action implies immediate provider execution without current authority: {action}")
        if pid == "G1":
            if auth.get("api_units") not in (0, "0"):
                errors.append("G1 must have zero committed provider calls before explicit Q0 authority")
            if "AUTHORITY" not in str(c.get("default_action") or ""):
                errors.append("G1 default action must explicitly bind Q0 authority")
            if not any("authority" in str(x).lower() for x in c.get("dependencies") or []):
                errors.append("G1 dependencies must include explicit Q0 authority")
        if pid == "CONSTRAINT_EXTERNALITY":
            if auth.get("api_units") not in (0, "0"):
                errors.append("Constraint must have zero committed provider calls after consumed readiness authority")
        if pid in {"B1", "3D"}:
            if not rr.get("operational_snapshot"):
                errors.append(f"{pid} running route missing operational snapshot")
            action = str(c.get("default_action") or "")
            if "NO_INTERIM" not in action and "NO_OUTCOME" not in action:
                errors.append(f"{pid} running default action does not explicitly block interim outcome inspection")

    if overlay.get("response", {}).get("final_verdict") != "REVISE_REALITY_COST_OVERLAY":
        errors.append("unexpected reality/cost independent-review verdict")
    if overlay_fix.get("status") != "FIXES_APPLIED_DETERMINISTIC_PASS":
        errors.append("reality/cost fix closure is not PASS")
    if final_attempt.get("valid_review_count") != 0 or final_attempt.get("valid_review") is not False:
        errors.append("invalid final decision-sufficiency attempt must remain 0 valid reviews")

    reviewer = final_review.get("reviewer") or {}
    if final_review.get("status") != "VALID_INDEPENDENT_REVIEW" or reviewer.get("valid_review_count") != 1 or reviewer.get("assistant_complete") is not True:
        errors.append("final decision-sufficiency review is not one complete valid independent review")
    if final_review.get("verdict") != "REVISE_ADVISOR_MEETING_DECISION_SUFFICIENCY" or final_review.get("freeze_decision") != "REVISE_AND_REFREEZE":
        errors.append("unexpected final decision-sufficiency reviewer verdict/freeze decision")
    if final_fix.get("status") != "FIXES_APPLIED_DETERMINISTIC_PASS":
        errors.append("final decision-sufficiency fix closure is not PASS")

    # The reviewer-required single-decision asks are bound exactly.
    requested_asks = {pid: row.get("question") for pid, row in (final_review.get("per_paper_ask") or {}).items() if row.get("action") == "REPLACE"}
    for pid, expected in requested_asks.items():
        if cards.get(pid, {}).get("advisor_question") != expected:
            errors.append(f"final reviewer replacement ask not bound: {pid}")

    ownership = agenda.get("claim_ownership_map") or {}
    expected_owners = {
        "B1": "provenance-field incremental decision value",
        "PAPER_A": "source-faithful causal transport from source outcome to later policy use",
        "PAPER_B": "longitudinal committed-update causal lifecycle across episodes",
    }
    for pid, expected in expected_owners.items():
        if (ownership.get(pid) or {}).get("primary_claim_owner") != expected:
            errors.append(f"memory claim ownership not frozen: {pid}")
    if len(agenda.get("shared_risk_reopen_rules") or []) < 3 or any(not str(x.get("reopen_threshold") or "").strip() for x in agenda.get("shared_risk_reopen_rules") or []):
        errors.append("shared-risk reopen table is incomplete")
    if len(agenda.get("meeting_outputs") or []) != 5:
        errors.append("meeting outputs must contain exactly five locked outputs")
    if len(agenda.get("do_not_spend_advisor_time_on") or []) > 6:
        errors.append("do-not-spend-advisor-time list exceeds reviewer cap")

    # Meeting schedule must remain exactly three hours while moving time from E1/cost into memory ownership.
    def minutes(hm: str) -> int:
        h, m = map(int, hm.split(":")); return h * 60 + m
    schedule = agenda.get("schedule") or []
    total_minutes = sum(minutes(x["end"]) - minutes(x["start"]) for x in schedule)
    if total_minutes != 180 or not schedule or schedule[0].get("start") != "14:00" or schedule[-1].get("end") != "17:00":
        errors.append(f"advisor schedule must cover exactly 14:00-17:00 / 180 minutes, got {total_minutes}")
    e1_minutes = sum(minutes(x["end"]) - minutes(x["start"]) for x in schedule if str(x.get("label")).startswith("E1"))
    memory_minutes = sum(minutes(x["end"]) - minutes(x["start"]) for x in schedule if str(x.get("label")).startswith("Memory"))
    cost_minutes = sum(minutes(x["end"]) - minutes(x["start"]) for x in schedule if "resource" in str(x.get("label")).lower())
    if e1_minutes > 15 or memory_minutes < 60 or cost_minutes > 12:
        errors.append(f"reviewer time reallocation not closed: E1={e1_minutes}, memory={memory_minutes}, resource={cost_minutes}")
    if not any("Unresolved exceptions" in str(x.get("label")) for x in schedule):
        errors.append("generic nine-paper closure sweep was not replaced by unresolved-exception sweep")

    for pid in ORDER:
        rr = (resources.get("papers") or {}).get(pid, {})
        if not str(rr.get("current_decision_cost") or "").strip():
            errors.append(f"missing current_decision_cost: {pid}")
        if not str(rr.get("cost_to_stop") or "").strip():
            errors.append(f"missing cost_to_stop: {pid}")
    for pid in ["PAPER_A", "PAPER_B"]:
        rr = (resources.get("papers") or {}).get(pid, {})
        if "not current commitment" not in str(rr.get("conditional_envelope_label") or "").lower():
            errors.append(f"future VLA envelope not visually separated from current commitment: {pid}")

    sources = [
        G / "advisor-paper-pack-manifest.json",
        G / "advisor-reality-support.json",
        G / "advisor-resource-ledger.json",
        G / "advisor-reality-cost-independent-review-20260905.json",
        G / "advisor-reality-cost-fix-closure-20260905.json",
        G / "advisor-final-decision-sufficiency-review-attempt-20260905.json",
        G / "advisor-final-decision-sufficiency-review-20260906.json",
        G / "advisor-final-decision-sufficiency-fix-closure-20260906.json",
        G / "advisor-meeting-agenda-20260906.json",
        *card_paths,
        *review_paths,
    ]
    freeze_hash, source_hashes = canonical_hash(sources)

    receipt = {
        "schema_version": "1.0",
        "meeting_id": "2026-09-06-advisor",
        "status": "MEETING_CANDIDATE_FROZEN" if not errors else "MEETING_CANDIDATE_BLOCKED",
        "meeting_candidate_hash": freeze_hash,
        "paper_count": len(ORDER),
        "paper_order": ORDER,
        "route_summary": {route: sum(cards.get(pid, {}).get("route") == route for pid in ORDER) for route in sorted(ROUTES)},
        "checks": {
            "paper_pack_9_of_9": len(manifest.get("papers", [])) == 9,
            "decision_cards_9_of_9": len(cards) == 9,
            "reality_support_9_of_9": len((reality.get("papers") or {})) == 9,
            "resource_ledger_9_of_9": len((resources.get("papers") or {})) == 9,
            "stanford_reviews_9_of_9_ready": all((G / f"stanford-{pid.lower()}-review.json").exists() and load(G / f"stanford-{pid.lower()}-review.json").get("status") == "READY" for pid in ORDER),
            "pdf_sha_binding_9_of_9": all((PDF_DIR / p["filename"]).exists() and sha(PDF_DIR / p["filename"]) == p["pdf_sha256"] for p in manifest.get("papers", [])),
            "route_authority_cost_consistency": not any("route" in e.lower() or "authority" in e.lower() or "committed" in e.lower() for e in errors),
            "prior_independent_reality_cost_review_valid": overlay.get("browser_evidence", {}).get("assistant_complete") is True,
            "prior_reality_cost_fixes_closed": overlay_fix.get("status") == "FIXES_APPLIED_DETERMINISTIC_PASS",
            "final_decision_sufficiency_attempt_fail_closed": final_attempt.get("valid_review_count") == 0,
            "final_decision_sufficiency_review_valid": final_review.get("status") == "VALID_INDEPENDENT_REVIEW" and reviewer.get("valid_review_count") == 1,
            "final_decision_sufficiency_fixes_closed": final_fix.get("status") == "FIXES_APPLIED_DETERMINISTIC_PASS",
            "memory_claim_ownership_frozen": all((ownership.get(pid) or {}).get("primary_claim_owner") == expected for pid, expected in expected_owners.items()),
            "shared_risk_reopen_table_frozen": len(agenda.get("shared_risk_reopen_rules") or []) >= 3,
            "advisor_schedule_reallocated": e1_minutes <= 15 and memory_minutes >= 60 and cost_minutes <= 12,
            "cost_to_stop_9_of_9": all(str((resources.get("papers") or {}).get(pid, {}).get("cost_to_stop") or "").strip() for pid in ORDER),
        },
        "errors": errors,
        "source_hashes": source_hashes,
        "authority": {"scientific": False, "experiment": False, "submission": False, "advisor_meeting_projection_only": True},
        "freeze_rule": "Any later substantive change to a decision card, reality support, resource ledger, frozen PDF, or Stanford review overlay changes the meeting_candidate_hash and requires an explicit new meeting candidate. Operational-only B1/3D ETA refresh may be shown as a separately timestamped overlay without changing scientific decisions.",
    }
    out = G / "advisor-meeting-freeze-20260906.json"
    if args.check:
        if not out.exists():
            errors.append("missing committed advisor-meeting-freeze-20260906.json")
        else:
            committed = load(out)
            if committed.get("meeting_candidate_hash") != freeze_hash:
                errors.append(f"meeting candidate hash drift: committed={committed.get('meeting_candidate_hash')} recomputed={freeze_hash}")
            if committed.get("status") != "MEETING_CANDIDATE_FROZEN":
                errors.append(f"committed freeze status is not frozen: {committed.get('status')}")
            if committed.get("errors"):
                errors.append(f"committed freeze receipt contains errors: {committed.get('errors')}")
    else:
        out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    status = "MEETING_CANDIDATE_FROZEN" if not errors else "MEETING_CANDIDATE_BLOCKED"
    print(json.dumps({"status": status, "meeting_candidate_hash": freeze_hash, "errors": errors, "route_summary": receipt["route_summary"], "mode": "check" if args.check else "write"}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
