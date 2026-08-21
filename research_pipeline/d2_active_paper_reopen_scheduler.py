from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
PAPERSTATES = ROOT / "generated/d2-active-paperstates-20260821.json"
RANKING = ROOT / "generated/d2-active-paper-mock-pc-ranking-20260821.json"
C02_F0C = ROOT / "generated/d2-proxy-reward-memory-f0c-prompt-control.json"
C02_F1D = ROOT / "generated/d2-proxy-reward-memory-f1d-distributional-audit.json"
C02_F2 = ROOT / "generated/d2-proxy-reward-terminal-fixed-evidence.json"
C02_LIVE_CONTRACT = ROOT / "generated/d2-proxy-reward-live-terminal-contract.json"
C02_LIVE_PREFLIGHT = ROOT / "generated/d2-proxy-reward-live-terminal-environment-preflight.json"
C01_BRIDGE = ROOT / "generated/d2-failure-memory-provenance-bridge.json"
C01_FAITHFUL = ROOT / "generated/d2-failure-memory-provenance-faithful-reconstruction-preflight.json"
C06_SUPPORT = ROOT / "generated/d2-temporal-skill-bottleneck-support-recheck-20260821.json"


PRIORITY = (
    "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
    "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",
    "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_scheduler() -> dict[str, Any]:
    states = _load(PAPERSTATES)
    ranking = _load(RANKING)
    by_id = {row["paper_id"]: row for row in states["papers"]}
    ranking_ids = [row["paper_id"] for row in ranking["papers"]]
    if ranking_ids != list(PRIORITY):
        raise ValueError(f"mock-pc-priority-drift:{ranking_ids}")

    c02_f0c = _load(C02_F0C)
    c02_f1d = _load(C02_F1D)
    c02_f2 = _load(C02_F2)
    c02_live_contract = _load(C02_LIVE_CONTRACT)
    c02_live_preflight = _load(C02_LIVE_PREFLIGHT)
    c01_bridge = _load(C01_BRIDGE)
    c01_faithful = _load(C01_FAITHFUL)
    c06_support = _load(C06_SUPPORT)

    entries: list[dict[str, Any]] = []

    c02 = by_id[PRIORITY[0]]
    c02_ready = c02_live_preflight.get("status") == "READY_FOR_STATE_FIDELITY_PREFLIGHT"
    entries.append({
        "priority": 1,
        "paper_id": c02["paper_id"],
        "title": c02["title"],
        "paper_state": "TARGETED_REPAIR",
        "scheduler_state": "REOPEN_NOW" if c02_ready else "HOLD_ENVIRONMENT",
        "why_priority": "Highest Mock-PC rank and the only paper with a completed direct write-channel intervention plus a passed same-information prompt control.",
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
            "live_asset_gate_pass": c02_live_preflight["asset_gate"]["pass"],
            "live_shopping_tcp_reachable": c02_live_preflight["network_gate"]["shopping"]["reachable"],
            "live_reset_tcp_reachable": c02_live_preflight["network_gate"]["reset"]["reachable"],
        },
        "blocking_dependencies": [] if c02_ready else [
            "Reachable source-faithful WebArena Shopping service.",
            "Reachable reset service or equivalent reproducible reset mechanism.",
        ],
        "reopen_condition": "A source-faithful live Shopping environment and reset path become reachable from an authorized execution host.",
        "forbid_before_reopen": [
            "Do not add more fixed-state first-action rollouts.",
            "Do not add more fixed-evidence terminal-answer surrogate rollouts.",
            "Do not interpret environment unavailability as scientific counterevidence.",
        ],
        "scientific_authority": False,
        "experiment_authority": False,
    })

    c06 = by_id[PRIORITY[1]]
    c06_ready = bool((c06.get("support_state") or {}).get("local_frozen_evaluated_snapshot_available"))
    entries.append({
        "priority": 2,
        "paper_id": c06["paper_id"],
        "title": c06["title"],
        "paper_state": "TARGETED_REPAIR",
        "scheduler_state": "REOPEN_NOW" if c06_ready else "HOLD_SUPPORT",
        "why_priority": "Second Mock-PC rank; the decisive three-condition intervention is already specified and waits on one first-party evaluated-snapshot dependency.",
        "decisive_next_experiment": "Frozen TimeSage-EV targeted temporal/exogenous skill injection versus matched generic-skill and no-skill controls on preregistered failure families.",
        "current_evidence": {
            "local_code_clone_head": c06_support["local_first_party_clones"]["code"]["head"],
            "local_dataset_clone_head": c06_support["local_first_party_clones"]["dataset"]["head"],
            "local_evaluated_snapshot_present": c06_support["local_conclusion"]["evaluated_snapshot_present"],
            "fresh_remote_recheck_status": c06_support["fresh_remote_recheck"]["status"],
        },
        "blocking_dependencies": [] if c06_ready else [
            "First-party frozen evaluated TimeSage-EV scenario snapshot or equivalent first-party inputs/outcomes/skill-interface artifacts."
        ],
        "reopen_condition": "A hashable first-party evaluated TimeSage-EV snapshot becomes available.",
        "forbid_before_reopen": [
            "Do not fabricate or substitute a synthetic TimeSage evaluated snapshot.",
            "Do not use remote-network failure as evidence that the public release is still empty.",
            "Do not run targeted-skill outcome calls before failure-family labels and controls can be frozen on first-party artifacts.",
        ],
        "scientific_authority": False,
        "experiment_authority": False,
    })

    c01 = by_id[PRIORITY[2]]
    faithful_ready = c01_faithful["status"] != "SUPPORT_HOLD_EXACT_PROVIDER_AND_EMBEDDING_ACCESS"
    entries.append({
        "priority": 3,
        "paper_id": c01["paper_id"],
        "title": c01["title"],
        "paper_state": "TARGETED_REPAIR",
        "scheduler_state": "REOPEN_NOW" if faithful_ready else "HOLD_SUPPORT",
        "why_priority": "Lowest Mock-PC rank and the explicit-provenance bridge has already exhausted its information value; only a source-faithful natural-memory swap can change the central causal claim.",
        "decisive_next_experiment": "Source-faithful matched semantic-memory provenance swap on the financial AgentDojo/ReasoningBank setting, including forward and reverse swaps.",
        "current_evidence": {
            "faithful_reconstruction_status": c01_faithful["status"],
            "explicit_provenance_bridge_decision": c01_bridge["decision"],
            "explicit_provenance_bridge_calls": c01_bridge["summary"]["complete_calls"],
            "explicit_provenance_bridge_success_minus_failure": c01_bridge["summary"]["mean_success_minus_failure_terminal_rate"],
        },
        "blocking_dependencies": [] if faithful_ready else [
            "Auditable access to the exact qwen3.7-flash-2026-07-15 executor snapshot.",
            "Auditable access to qwen3.7-text-embedding for source-faithful top-1 retrieval.",
            "A faithful AgentDojo bridge plus aggregate-fidelity gate, or first-party per-query audit artifacts from the financial study.",
        ],
        "reopen_condition": "Exact executor+embedding access becomes available, or the financial-audit authors release per-query artifacts sufficient for the natural matched provenance swap.",
        "forbid_before_reopen": [
            "Do not add more explicit SUCCESS/FAILURE metadata-tag bridge rollouts.",
            "Do not substitute a different embedding model and call it source-faithful reproduction.",
            "Do not treat the 0.000 bridge difference as equivalence because no equivalence margin was preregistered.",
        ],
        "scientific_authority": False,
        "experiment_authority": False,
    })

    return {
        "schema_version": "1.0",
        "status": "ALL_THREE_TARGETED_REPAIRS_EXTERNALLY_BLOCKED" if all(row["scheduler_state"] != "REOPEN_NOW" for row in entries) else "REOPENABLE_TARGETED_REPAIR_PRESENT",
        "policy": {
            "priority_source": "Initial dual-mode Mock-PC ranking; later experiments may remove reviewer objections but do not silently reorder papers without a new comparable Mock-PC round.",
            "support_failure_has_no_scientific_authority": True,
            "no_surrogate_expansion_when_decisive_dependency_is_blocked": True,
            "resume_only_at_decisive_experiment": True,
        },
        "entries": entries,
        "summary": {
            "papers": len(entries),
            "reopen_now": sum(row["scheduler_state"] == "REOPEN_NOW" for row in entries),
            "hold_environment": sum(row["scheduler_state"] == "HOLD_ENVIRONMENT" for row in entries),
            "hold_support": sum(row["scheduler_state"] == "HOLD_SUPPORT" for row in entries),
        },
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "generated/d2-active-paper-reopen-scheduler.json")
    args = parser.parse_args()
    payload = build_scheduler()
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
