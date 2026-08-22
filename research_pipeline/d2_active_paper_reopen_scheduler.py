from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
RANKING = ROOT / "generated/d2-active-paper-mock-pc-ranking-20260821.json"
C02_F0C = ROOT / "generated/d2-proxy-reward-memory-f0c-prompt-control.json"
C02_F1D = ROOT / "generated/d2-proxy-reward-memory-f1d-distributional-audit.json"
C02_F2 = ROOT / "generated/d2-proxy-reward-terminal-fixed-evidence.json"
C02_LIVE_CONTRACT = ROOT / "generated/d2-proxy-reward-live-terminal-contract.json"
C02_LIVE_PREFLIGHT = ROOT / "generated/d2-proxy-reward-live-terminal-environment-preflight.json"
C01_BRIDGE = ROOT / "generated/d2-failure-memory-provenance-bridge.json"
C01_FAITHFUL = ROOT / "generated/d2-failure-memory-provenance-faithful-reconstruction-preflight.json"
C01_R4 = ROOT / "generated/d2-failure-memory-provenance-r4-controlled-swap.json"
C01_POWER = ROOT / "generated/d2-failure-memory-provenance-r4-power-audit.json"
C01_EQ = ROOT / "generated/d2-failure-memory-provenance-equivalence-robustness.json"
C01_ADJ = ROOT / "generated/d2-failure-memory-provenance-targeted-repair-adjudication-20260822.json"
C06_SUPPORT = ROOT / "generated/d2-temporal-skill-bottleneck-support-recheck-20260821.json"


PRIORITY = (
    "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
    "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",
    "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_states(root: Path) -> dict[str, str]:
    states: dict[str, str] = {}
    for paper_id in PRIORITY:
        path = root / f"{paper_id}.json"
        if not path.is_file():
            continue
        try:
            payload = _load(path)
        except (OSError, json.JSONDecodeError):
            continue
        state = str(payload.get("current_state") or "")
        if state:
            states[paper_id] = state
    return states


def _done_entry(*, priority: int, paper_id: str, title: str, paper_state: str) -> dict[str, Any]:
    return {
        "priority": priority,
        "paper_id": paper_id,
        "title": title,
        "paper_state": paper_state,
        "scheduler_state": "DONE_SUBMISSION_READY",
        "why_priority": "Canonical Paper Acceptance has already admitted this paper to Submission Ready. Earlier targeted-repair blockers no longer authorize more experiment spending.",
        "decisive_next_experiment": "",
        "blocking_dependencies": [],
        "reopen_condition": "Only reopen the scientific or experiment contract through a new explicit Research OS authorization if post-ready review discovers a decision-critical defect.",
        "forbid_before_reopen": [
            "Do not resume obsolete targeted-repair experiments from the pre-Submission-Ready scheduler.",
            "Do not spend experiment budget merely because an older support receipt remains unresolved.",
        ],
        "scientific_authority": False,
        "experiment_authority": False,
    }


def build_scheduler(
    *,
    paper_acceptance_states: Mapping[str, str] | None = None,
    paper_acceptance_root: Path | None = None,
) -> dict[str, Any]:
    ranking = _load(RANKING)
    ranking_rows = {row["paper_id"]: row for row in ranking["papers"]}
    ranking_ids = [row["paper_id"] for row in ranking["papers"]]
    if ranking_ids != list(PRIORITY):
        raise ValueError(f"mock-pc-priority-drift:{ranking_ids}")

    if paper_acceptance_states is not None:
        canonical = dict(paper_acceptance_states)
    elif paper_acceptance_root is not None:
        canonical = _canonical_states(paper_acceptance_root)
    else:
        canonical = {}
    for paper_id in PRIORITY:
        canonical.setdefault(paper_id, str(ranking_rows[paper_id].get("current_state") or "TARGETED_REPAIR"))

    c02_f0c = _load(C02_F0C)
    c02_f1d = _load(C02_F1D)
    c02_f2 = _load(C02_F2)
    c02_live_contract = _load(C02_LIVE_CONTRACT)
    c02_live_preflight = _load(C02_LIVE_PREFLIGHT)
    c01_bridge = _load(C01_BRIDGE)
    c01_faithful = _load(C01_FAITHFUL)
    c01_r4 = _load(C01_R4)
    c01_power = _load(C01_POWER)
    c01_eq = _load(C01_EQ)
    c01_adj = _load(C01_ADJ)
    c06_support = _load(C06_SUPPORT)

    entries: list[dict[str, Any]] = []

    c02_id = PRIORITY[0]
    c02_state = canonical[c02_id]
    if c02_state == "SUBMISSION_READY":
        entries.append(_done_entry(priority=1, paper_id=c02_id, title=ranking_rows[c02_id]["title"], paper_state=c02_state))
    else:
        c02_ready = c02_live_preflight.get("status") == "READY_FOR_STATE_FIDELITY_PREFLIGHT"
        entries.append({
            "priority": 1,
            "paper_id": c02_id,
            "title": ranking_rows[c02_id]["title"],
            "paper_state": c02_state,
            "scheduler_state": "REOPEN_NOW" if c02_ready else "HOLD_ENVIRONMENT",
            "why_priority": "Highest initial Mock-PC rank while the paper remains below Submission Ready.",
            "decisive_next_experiment": "Live matched WebArena browser continuation under paired reward-conditioned memories, measuring terminal benchmark success and first divergence with the frozen source environment and evaluator.",
            "frozen_execution_contract": str(C02_LIVE_CONTRACT.relative_to(ROOT)),
            "environment_preflight": str(C02_LIVE_PREFLIGHT.relative_to(ROOT)),
            "current_evidence": {
                "f0_prompt_control_gate_pass": bool(c02_f0c["summary"]["gate_pass"]),
                "fresh_first_action_distribution_decision": c02_f1d["decision"],
                "fixed_evidence_terminal_decision": c02_f2["decision"],
                "fixed_evidence_terminal_mean_absolute_success_rate_difference": c02_f2["summary"]["observed_mean_absolute_success_rate_difference"],
                "fixed_evidence_terminal_permutation_p": c02_f2["summary"]["permutation_p_ge_observed"],
                "live_contract_status": c02_live_contract["status"],
                "live_environment_preflight_status": c02_live_preflight["status"],
            },
            "blocking_dependencies": [] if c02_ready else ["Reachable source-faithful WebArena Shopping and reset services."],
            "reopen_condition": "A source-faithful live Shopping environment and reset path become reachable from an authorized execution host.",
            "forbid_before_reopen": [
                "Do not add more fixed-state first-action rollouts.",
                "Do not add more fixed-evidence terminal-answer surrogate rollouts.",
            ],
            "scientific_authority": False,
            "experiment_authority": False,
        })

    c06_id = PRIORITY[1]
    c06_state = canonical[c06_id]
    if c06_state == "SUBMISSION_READY":
        entries.append(_done_entry(priority=2, paper_id=c06_id, title=ranking_rows[c06_id]["title"], paper_state=c06_state))
    else:
        c06_ready = bool(c06_support["local_conclusion"]["evaluated_snapshot_present"])
        entries.append({
            "priority": 2,
            "paper_id": c06_id,
            "title": ranking_rows[c06_id]["title"],
            "paper_state": c06_state,
            "scheduler_state": "REOPEN_NOW" if c06_ready else "HOLD_SUPPORT",
            "why_priority": "Second initial Mock-PC rank while the paper remains below Submission Ready.",
            "decisive_next_experiment": "Frozen TimeSage-EV targeted temporal/exogenous skill injection versus matched generic-skill and no-skill controls.",
            "current_evidence": {
                "local_code_clone_head": c06_support["local_first_party_clones"]["code"]["head"],
                "local_dataset_clone_head": c06_support["local_first_party_clones"]["dataset"]["head"],
                "local_evaluated_snapshot_present": c06_support["local_conclusion"]["evaluated_snapshot_present"],
                "fresh_remote_recheck_status": c06_support["fresh_remote_recheck"]["status"],
            },
            "blocking_dependencies": [] if c06_ready else ["A hashable first-party evaluated TimeSage-EV snapshot."],
            "reopen_condition": "A hashable first-party evaluated TimeSage-EV snapshot becomes available.",
            "forbid_before_reopen": ["Do not fabricate or substitute a synthetic TimeSage evaluated snapshot."],
            "scientific_authority": False,
            "experiment_authority": False,
        })

    c01_id = PRIORITY[2]
    c01_state = canonical[c01_id]
    if c01_state == "SUBMISSION_READY":
        entries.append(_done_entry(priority=3, paper_id=c01_id, title=ranking_rows[c01_id]["title"], paper_state=c01_state))
    else:
        faithful_ready = c01_faithful["status"] != "SUPPORT_HOLD_EXACT_PROVIDER_AND_EMBEDDING_ACCESS"
        independent_ready = int(c01_adj["independent_confirmation_support"]["fresh_qualified_task_count"]) >= 18
        reopen_now = faithful_ready or independent_ready
        entries.append({
            "priority": 3,
            "paper_id": c01_id,
            "title": ranking_rows[c01_id]["title"],
            "paper_state": c01_state,
            "scheduler_state": "REOPEN_NOW" if reopen_now else "HOLD_SUPPORT_AND_IDENTIFICATION",
            "why_priority": "The only D2 paper still below Submission Ready. R4 produced a directional effect, but both the frozen statistical gate and the post-hoc identification robustness audit remain unresolved.",
            "decisive_next_experiment": "Either a source-faithful financial AgentDojo matched-provenance replication, or an independently frozen confirmation with roughly 18-22 or more eligible pairs under a robust multi-reviewer information-equivalence gate.",
            "current_evidence": {
                "faithful_reconstruction_status": c01_faithful["status"],
                "explicit_provenance_bridge_decision": c01_bridge["decision"],
                "r4_verdict": c01_r4["summary"]["verdict"],
                "r4_mean_success_minus_failure_terminal_rate": c01_r4["summary"]["mean_success_minus_failure_terminal_rate"],
                "r4_permutation_p_success_greater": c01_r4["summary"]["permutation_p_success_greater"],
                "r4_support_gate_pass": c01_r4["summary"]["support_gate_pass"],
                "r4_counterevidence_gate_pass": c01_r4["summary"]["counterevidence_gate_pass"],
                "approx_power_at_four_pairs_range": c01_adj["power_audit"]["approx_power_at_four_pairs_range"],
                "approx_independent_pairs_for_80pct_power_range": c01_adj["power_audit"]["approx_independent_pairs_for_80pct_power_range"],
                "original_verifier_primary_strict_pass": c01_eq["summary"]["original_verifier_primary_strict_pass"],
                "deepseek_primary_strict_pass": c01_eq["summary"]["deepseek_primary_strict_pass"],
                "kimi_primary_strict_pass": c01_eq["summary"]["kimi_primary_strict_pass"],
                "three_reviewer_unanimous_primary_strict_pass": c01_eq["summary"]["three_reviewer_unanimous_primary_strict_pass"],
                "fresh_same_release_confirmation_tasks": c01_adj["independent_confirmation_support"]["fresh_qualified_task_count"],
            },
            "blocking_dependencies": [] if reopen_now else [
                "Source-faithful first-party financial artifacts or auditable exact qwen3.7 executor plus embedding access.",
                "Or a disjoint independently frozen support population large enough for approximately 18-22 eligible pairs under robust multi-reviewer equivalence.",
            ],
            "reopen_condition": "One of the two decisive support paths above becomes available before any new outcome is inspected.",
            "forbid_before_reopen": [
                "Do not add seeds to the same four R4 pairs to rescue p<0.05.",
                "Do not drop or replace R4 pairs after the verifier audit.",
                "Do not relax the 0.15 effect floor, 0.05 p threshold, or structural task qualification.",
                "Do not treat identification failure as scientific counterevidence to C4.",
                "Do not spend more budget on the explicit SUCCESS/FAILURE metadata bridge.",
            ],
            "scientific_authority": False,
            "experiment_authority": False,
        })

    summary = {
        "papers": len(entries),
        "submission_ready": sum(row["scheduler_state"] == "DONE_SUBMISSION_READY" for row in entries),
        "reopen_now": sum(row["scheduler_state"] == "REOPEN_NOW" for row in entries),
        "hold_environment": sum(row["scheduler_state"] == "HOLD_ENVIRONMENT" for row in entries),
        "hold_support": sum(row["scheduler_state"] == "HOLD_SUPPORT" for row in entries),
        "hold_support_and_identification": sum(row["scheduler_state"] == "HOLD_SUPPORT_AND_IDENTIFICATION" for row in entries),
    }
    if summary["submission_ready"] == len(entries):
        status = "ALL_D2_PAPERS_SUBMISSION_READY"
    elif summary["submission_ready"] and summary["reopen_now"] == 0:
        status = "PORTFOLIO_HAS_SUBMISSION_READY_WITH_HELD_TARGETED_REPAIR"
    elif summary["reopen_now"]:
        status = "REOPENABLE_TARGETED_REPAIR_PRESENT"
    else:
        status = "TARGETED_REPAIRS_HELD"

    return {
        "schema_version": "1.1",
        "status": status,
        "policy": {
            "canonical_paper_acceptance_state_overrides_stale_pre_ready_scheduler_state": True,
            "submission_ready_papers_are_removed_from_targeted_repair_spending": True,
            "priority_source": "Initial dual-mode Mock-PC rank is retained only as historical ordering; canonical Paper Acceptance state controls current scheduling.",
            "support_failure_has_no_scientific_authority": True,
            "no_surrogate_expansion_when_decisive_dependency_is_blocked": True,
            "resume_only_at_decisive_experiment": True,
        },
        "canonical_paper_acceptance_states": canonical,
        "entries": entries,
        "summary": summary,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "generated/d2-active-paper-reopen-scheduler.json")
    env_root = os.getenv("D2_PAPER_ACCEPTANCE_ROOT", "").strip()
    parser.add_argument("--paper-acceptance-root", type=Path, default=Path(env_root) if env_root else None)
    args = parser.parse_args()
    payload = build_scheduler(paper_acceptance_root=args.paper_acceptance_root)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
