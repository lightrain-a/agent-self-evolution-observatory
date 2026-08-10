from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def build(screening_path: Path, fidelity_path: Path) -> dict[str, Any]:
    screening = _load(screening_path)
    fidelity = _load(fidelity_path)
    analysis = screening.get("analysis") or {}
    directional = screening.get("decision") == "screening-signal"
    fidelity_pass = fidelity.get("fidelity_pass") is True
    baseline_mastered = sum(int(row.get("baseline_success") or 0) for row in fidelity.get("probe_rows") or [])
    panel_size = int(fidelity.get("fixed_probe_count") or 0)
    confirmatory_authorized = directional and fidelity_pass and panel_size > 0 and baseline_mastered == panel_size
    blockers: list[str] = []
    if not directional:
        blockers.append("screening-directional-signal-missing")
    if baseline_mastered < panel_size:
        blockers.append(f"probe-baseline-mastery:{baseline_mastered}/{panel_size}")
    if not fidelity_pass:
        blockers.append("probe-fidelity-below-development-threshold")
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "artifact_kind": "A1-screening-review",
        "idea_id": "update-trust-region",
        "phase": "P0-screening",
        "screening_decision": screening.get("decision"),
        "classification": "SCREENING-SIGNAL / CONFIRMATORY-ELIGIBLE" if confirmatory_authorized else ("SCREENING-SIGNAL / CONFIRMATORY-BLOCKED" if directional else "SCREENING-NO-SIGNAL / CONFIRMATORY-BLOCKED"),
        "method_result_available": False,
        "confirmatory_authorized": confirmatory_authorized,
        "blockers": blockers,
        "directional_effect": {
            "harmful_candidate_count": analysis.get("harmful_candidate_count"),
            "matched_acceptance_count": analysis.get("matched_acceptance_count"),
            "harmful_update_reduction": analysis.get("harmful_update_reduction"),
            "target_gain_loss": analysis.get("target_gain_loss"),
            "strongest_simple_baseline": analysis.get("strongest_simple_baseline"),
        },
        "probe_fidelity": {
            "baseline_mastered_probes": baseline_mastered,
            "panel_size": panel_size,
            "aggregate_panel_leave_one_candidate_out_auc": fidelity.get("aggregate_panel_leave_one_candidate_out_auc"),
            "best_single_probe_action_auc": fidelity.get("best_single_probe_action_auc"),
            "minimum_fidelity_auc": fidelity.get("minimum_fidelity_auc"),
            "fidelity_pass": fidelity_pass,
        },
        "next_action": (
            "human-review-before-confirmatory-p0"
            if confirmatory_authorized else
            "construct-mastered-probe-panel; replay frozen development patches; if fidelity improves, freeze selection rule and validate on a fresh candidate batch before recompiling the Pre-Experiment Card"
        ),
        "interpretation": "A directional screening effect does not override a failed probe-identifiability gate. No METHOD-PASS or METHOD-FAIL is allowed from this artifact.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Combine A-1 screening effect and probe-fidelity evidence into one confirmatory authorization decision.")
    parser.add_argument("--screening", type=Path, required=True)
    parser.add_argument("--probe-fidelity", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = build(args.screening, args.probe_fidelity)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
