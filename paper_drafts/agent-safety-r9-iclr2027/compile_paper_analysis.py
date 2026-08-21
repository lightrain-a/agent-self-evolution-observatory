#!/usr/bin/env python3
"""Compile paper-facing R9 analyses from the adjudicated frozen receipt only."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RECEIPT = REPO / "generated" / "agent-safety-r9-future-evidence-adjudication-20260820.json"
OUTPUT = REPO / "generated" / "agent-safety-r9-paper-analysis-suite-20260821.json"
STATE_ORDER = ["map-P2-A", "map-V4-C1", "reddit-A", "reddit-B"]


def main() -> None:
    receipt = json.loads(RECEIPT.read_text())
    future = receipt["future_first_violation"]
    states = future["states"]

    event_steps = [
        step
        for state in STATE_ORDER
        for step in states[state]["first_violation_steps"]
        if step is not None
    ]
    cumulative = []
    previous = 0
    for horizon in (1, 2, 3):
        detected = sum(step <= horizon for step in event_steps)
        cumulative.append(
            {
                "future_horizon": horizon,
                "episodes_observed": 12 * horizon,
                "event_branches_detected": detected,
                "event_branches_total": 12,
                "incremental_event_branches": detected - previous,
                "descriptive_event_fraction": detected / 12,
            }
        )
        previous = detected

    state_rows = []
    for state in STATE_ORDER:
        row = states[state]
        state_rows.append(
            {
                "state_id": state,
                "site_stratum": row["site_stratum"],
                "qualification_violations": 0,
                "qualification_episodes": 3,
                "future_violation_episodes": row["future_violation_episodes"],
                "future_episodes": row["future_episodes"],
                "event_branches": row["branches_with_first_violation"],
                "branches": row["branches"],
                "first_violation_steps": row["first_violation_steps"],
            }
        )

    output = {
        "schema_version": "1.0",
        "status": "READY_R9_PAPER_ANALYSIS_FROM_FROZEN_EVIDENCE",
        "paper_id": "AGENT-SAFETY-R9",
        "source_receipt": str(RECEIPT.relative_to(REPO)),
        "new_behavior_execution": False,
        "analysis_scope": (
            "Descriptive re-expression of the adjudicated 12-episode current panel "
            "and 36-episode future evaluation; no IID or population-hazard inference."
        ),
        "headline": {
            "qualification": "0/12 evaluator-classified violations",
            "future": "11/36 evaluator-classified violations",
            "event_branches": "8/12",
            "states_with_event": "3/4",
            "static_pass_rule_branch_errors": "8/12",
        },
        "temporal_detection_profile": cumulative,
        "event_timing": future["first_violation_step_counts"],
        "state_rows": state_rows,
        "paired_state_summary": future["pairs"],
        "comparison_roles": [
            {
                "id": "STATIC-SNAPSHOT",
                "role": "claim-target baseline",
                "question": "What is observed at the current state?",
                "evidence": "12 current probes, all non-violations",
                "temporal_conclusion": "No future guarantee follows from the observed panel.",
            },
            {
                "id": "ONE-STEP-FUTURE",
                "role": "horizon-depth baseline",
                "question": "How many event branches are visible after one future step?",
                "evidence": "1/12 branches",
                "temporal_conclusion": "A one-step extension detects only one of eight observed event branches.",
            },
            {
                "id": "TWO-STEP-FUTURE",
                "role": "horizon-depth baseline",
                "question": "How many event branches are visible after two future steps?",
                "evidence": "7/12 branches",
                "temporal_conclusion": "Step 2 contributes six additional first events.",
            },
            {
                "id": "THREE-STEP-FIRST-VIOLATION",
                "role": "full frozen evaluation",
                "question": "Which branches experience a first violation within the declared horizon?",
                "evidence": "8/12 branches; four censored after step 3",
                "temporal_conclusion": "The current pass is not a certificate over this evaluated future.",
            },
        ],
        "claim_evidence_map": [
            {
                "claim_id": "R9-C1",
                "claim": receipt["claim_scope"]["supported"],
                "evidence": [
                    "0/12 current-panel violations",
                    "8/12 branches with a first violation by step 3",
                    "11/36 future violation episodes",
                ],
                "status": "SUPPORTED_NARROWLY",
            },
            {
                "claim_id": "R9-C2",
                "claim": "Evaluation depth changes how many future event branches are observed.",
                "evidence": [
                    "1/12 by step 1",
                    "7/12 by step 2",
                    "8/12 by step 3",
                ],
                "status": "SUPPORTED_DESCRIPTIVELY",
            },
            {
                "claim_id": "R9-C3",
                "claim": "Persistent updating alone caused the observed violations.",
                "evidence": ["No same-schedule no-update outcome is available."],
                "status": "HOLD_METHOD_IDENTIFICATION",
            },
        ],
        "scientific_authority": False,
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
