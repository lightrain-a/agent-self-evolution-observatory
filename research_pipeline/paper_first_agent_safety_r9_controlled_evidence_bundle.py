from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


LAYERS = ("runtime", "protocol", "support", "operationalization", "method", "principle")


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object: {path}")
    return value


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def attach_hash(value: dict[str, Any], key: str) -> dict[str, Any]:
    value[key] = hashlib.sha256(canonical(value)).hexdigest()
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def repo_ref(path: Path) -> str:
    return f"repo://{path.as_posix()}#sha256={sha_file(path)}"


def build(adjudication_path: Path, review_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    adjudication = load(adjudication_path)
    review = load(review_path)
    if adjudication["status"] != "READY_R23_CONTROLLED_LONGITUDINAL_ADJUDICATION":
        raise RuntimeError("controlled adjudication is not ready")
    if review["status"] != "READY_R23_CONTROLLED_LONGITUDINAL_SCIENTIFIC_REVIEW":
        raise RuntimeError("scientific review is not ready")

    source_refs = [repo_ref(adjudication_path), repo_ref(review_path)]
    primary = adjudication["primary_same_schedule_control"]
    fixed = adjudication["secondary_fixed_probe_snapshots"]
    decisions = review["decisions"]
    controlled_supported = decisions["same_schedule_update_contrast"] == "SUPPORTED_FINITE_CONTROLLED_CONTRAST"
    fixed_supported = decisions["fixed_probe_snapshot_panel"] == "SUPPORTED_DESCRIPTIVE_STATE_DEPENDENCE"

    update_supported = (
        "Within the frozen 12 paired BrowserART trajectories, the updated-workflow condition "
        f"had {primary['treatment_branch_events']}/12 branch first-violation events versus "
        f"{primary['control_branch_events']}/12 under the same-schedule base-workflow control "
        f"({primary['paired_discordance']['treatment_only']} update-only, "
        f"{primary['paired_discordance']['control_only']} control-only)."
        if controlled_supported else ""
    )
    fixed_supported_text = (
        f"Across 12 frozen state-by-probe trajectories, {fixed['trajectories_with_first_violation']} "
        "originally non-violating qualification probes had a first evaluator-classified violation "
        "at a later workflow snapshot while probe identity and seed remained fixed."
        if fixed_supported else ""
    )

    rows = [
        {
            "row_id": "R9-CLAIM-01",
            "supported_claim": (
                "Within the frozen R9 BrowserART/HarmBench operationalization, passing the "
                "three-probe current-safety panel did not guarantee absence of first-violation "
                "events over the evaluated three-step future."
            ),
            "not_supported_claim": "Static safety evaluation is generally ineffective across agents, models, or benchmarks.",
            "limitation": "The guarantee result is a finite logical counterexample in four selected states, not a population estimate.",
        },
        {
            "row_id": "R9-CLAIM-02",
            "supported_claim": update_supported,
            "not_supported_claim": (
                "" if controlled_supported else
                "Persistent updating increased branch first-violation events in the frozen paired design."
            ),
            "limitation": (
                "The same-schedule contrast separates workflow-update condition from schedule in this frozen "
                "12-pair design, but one backbone and stochastic rollouts do not support a population causal effect."
            ),
        },
        {
            "row_id": "R9-CLAIM-03",
            "supported_claim": fixed_supported_text,
            "not_supported_claim": (
                "" if fixed_supported else
                "The fixed qualification probes became less safe at later workflow snapshots."
            ),
            "limitation": "The read-only snapshot panel is descriptive, non-monotonic in two event trajectories, and limited to three probes, four states, and three exposure steps.",
        },
        {
            "row_id": "R9-CLAIM-04",
            "supported_claim": "",
            "not_supported_claim": "The observed event fractions are population hazards or prevalence estimates.",
            "limitation": "Branches and probe trajectories are deliberately constructed paired units, not IID deployment samples.",
        },
        {
            "row_id": "R9-CLAIM-05",
            "supported_claim": "",
            "not_supported_claim": "HarmBench labels are a noiseless safety oracle.",
            "limitation": "HarmBench remains the frozen operational evaluator and lacks independent validation for this BrowserART realization.",
        },
    ]
    claim_table = {
        "schema_version": "2.0",
        "status": "READY_AGENT_SAFETY_R9_CONTROLLED_PAPER_CLAIM_TABLE",
        "candidate_id": "SHADOW-P01-C01",
        "evidence_refs": source_refs,
        "columns": ["supported_claim", "not_supported_claim", "limitation"],
        "rows": rows,
        "evidence_summary": {
            "static_qualification": "12/12 completed predictions were non-violations",
            "updated_future_branch_events": f"{primary['treatment_branch_events']}/12",
            "no_update_future_branch_events": f"{primary['control_branch_events']}/12",
            "paired_discordance": primary["paired_discordance"],
            "fixed_probe_event_trajectories": f"{fixed['trajectories_with_first_violation']}/12",
            "fixed_probe_violations_by_exposure_step": fixed["violations_by_exposure_step"],
        },
        "population_hazard_claim": False,
        "scientific_authority": False,
    }
    attach_hash(claim_table, "table_sha256")

    claims = [
        {
            "claim_id": "AGENT-SAFETY-R9-STATIC-PASS-NO-FUTURE-GUARANTEE",
            "claim_text": rows[0]["supported_claim"],
            "claim_type": "predictive_sufficiency",
            "scientific_object": "persistent-state-agent-safety",
            "mechanism": "current-safety-panel-to-future-first-violation",
            "adjudication_status": "SUPPORTED_NARROWLY",
            "evidence_ids": source_refs,
            "scientific_authority": False,
        },
        {
            "claim_id": "AGENT-SAFETY-R9-PERSISTENT-UPDATE-CONTROLLED-CONTRAST",
            "claim_text": update_supported or rows[1]["not_supported_claim"],
            "claim_type": "finite_controlled_contrast",
            "scientific_object": "persistent-state-agent-safety",
            "mechanism": "persistent-update-effect-separated-from-heldout-schedule",
            "adjudication_status": decisions["same_schedule_update_contrast"],
            "evidence_ids": source_refs,
            "scientific_authority": False,
        },
        {
            "claim_id": "AGENT-SAFETY-R9-FIXED-PROBE-SNAPSHOT-TRANSITION",
            "claim_text": fixed_supported_text or rows[2]["not_supported_claim"],
            "claim_type": "descriptive_longitudinal_probe",
            "scientific_object": "persistent-state-agent-safety",
            "mechanism": "fixed-probe-response-across-workflow-snapshots",
            "adjudication_status": decisions["fixed_probe_snapshot_panel"],
            "evidence_ids": source_refs,
            "scientific_authority": False,
        },
    ]
    reopen_status = decisions["reopen_condition_status"]
    graph = {
        "schema_version": "2.1",
        "status": "READY_AGENT_SAFETY_R9_CONTROLLED_MEMORY_GRAPH_2_1_INPUTS",
        "evidence_refs": source_refs,
        "claim_table_sha256": claim_table["table_sha256"],
        "claim_ledger": claims,
        "supplemental_memory_entries": [
            {
                "memory_id": "MEM-RESULT-AGENT-SAFETY-R9-UPDATE-VS-SCHEDULE",
                "kind": "RESULT",
                "title": "R9 same-schedule no-update control executed",
                "summary": update_supported or rows[1]["not_supported_claim"],
                "candidate_id": "AGENT-SAFETY-R9-PERSISTENT-UPDATE-CONTROLLED-CONTRAST",
                "affected_layer": "method",
                "memory_class": "FINITE_CONTROLLED_CONTRAST",
                "durability_class": "scientific",
                "prompt_eligible": True,
                "search_closure_certified": False,
                "scientific_dead_end_certified": False,
                "principle_update_allowed": False,
                "reopen_condition": "separate persistent update effect from held-out schedule effect",
                "reopen_condition_status": reopen_status,
                "source_refs": source_refs,
                "scientific_authority": False,
            }
        ],
        "reopen_condition": {
            "condition_id": "REOPEN-AGENT-SAFETY-R9-SEPARATE-UPDATE-FROM-SCHEDULE",
            "condition": "separate persistent update effect from held-out schedule effect",
            "implementation": "same held-out schedule with the workflow snapshot held at its step-0 base state",
            "status": reopen_status,
            "satisfied_for_population_claim": False,
            "automatic_reopen": False,
            "new_behavior_execution_authorized": False,
            "scientific_authority": False,
        },
        "failure_classification": {
            layer: list(review["failure_classification"].get(layer, [])) for layer in LAYERS
        },
        "summary": {
            "claims": len(claims),
            "supported_narrowly": sum(
                "SUPPORTED" in claim["adjudication_status"] for claim in claims
            ),
            "reopen_conditions": 1,
            "population_claims": 0,
            "principle_updates": 0,
        },
        "scientific_authority": False,
    }
    attach_hash(graph, "bundle_sha256")
    return claim_table, graph


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adjudication", required=True)
    parser.add_argument("--scientific-review", required=True)
    parser.add_argument("--claim-table-output", required=True)
    parser.add_argument("--memory-graph-output", required=True)
    args = parser.parse_args()
    claim_table, graph = build(Path(args.adjudication), Path(args.scientific_review))
    atomic_json(Path(args.claim_table_output), claim_table)
    atomic_json(Path(args.memory_graph_output), graph)
    print(json.dumps({
        "claim_table_sha256": claim_table["table_sha256"],
        "memory_graph_sha256": graph["bundle_sha256"],
        "reopen_condition_status": graph["reopen_condition"]["status"],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
