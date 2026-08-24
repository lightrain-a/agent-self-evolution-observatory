from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    qa = json.loads((HERE / "manuscript-qa.json").read_text(encoding="utf-8"))
    contract = json.loads((HERE / "daytime-story-optimization-contract.json").read_text(encoding="utf-8"))
    if qa["status"] != "PASS" or qa["revision"] != "STANFORD-R3-DAYTIME-STORY-OPTIMIZATION-20260824":
        raise RuntimeError("daytime manuscript QA is not current PASS")
    if contract["status"] != "FROZEN_PAPER_ONLY_OPTIMIZATION":
        raise RuntimeError("daytime optimization contract is not frozen")
    if any((qa["new_provider_calls_exact"], qa["new_provider_calls_observable_lower_bound"], qa["new_scientifically_usable_provider_calls"], qa["new_terminal_rollouts"])):
        raise RuntimeError("daytime revision unexpectedly consumed scientific provider calls")
    if contract["new_scientific_provider_calls"] != 0 or contract["new_rollouts"] != 0 or contract["claim_expansion"] is not False:
        raise RuntimeError("daytime optimization contract expanded scientific scope")

    receipt = {
        "schema_version": "1.0",
        "artifact_type": "daytime-paper-story-revision-receipt",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "status": "PAPER_ONLY_STORY_OPTIMIZATION_COMPLETE",
        "revision": qa["revision"],
        "previous_candidate_pdf_sha256": "24a220df1000771998cc55249588065a98c372ea7286a92dbba098e94cf099f9",
        "current_candidate_pdf_sha256": sha(HERE / "paper.pdf"),
        "title_before": "Reward Errors Become Persistent State: A Controlled Write-Time Memory Intervention in Self-Improving Agents",
        "title_after": "Reward Errors Become Persistent State: A Controlled Intervention in Reward-Conditioned Agent Memory",
        "optimization_contract_sha256": sha(HERE / "daytime-story-optimization-contract.json"),
        "manuscript_qa_sha256": sha(HERE / "manuscript-qa.json"),
        "paper_story_v3_sha256": sha(REPO / "paper-story-reward-memory.js"),
        "paper_reader_data_sha256": sha(REPO / "paper-reader-data.js"),
        "paper_story_v3_contract_pass": True,
        "manuscript_qa_status": qa["status"],
        "manuscript_qa_checks_passed": sum(bool(v) for v in qa["checks"].values()),
        "manuscript_qa_checks_total": len(qa["checks"]),
        "abstract_words_approx": qa["abstract_words_approx"],
        "main_text_pages": qa["main_text_pages"],
        "pdf_pages_total": qa["pdf_pages_total"],
        "changes": [
            {"id": "story", "result": "One causal chain now organizes the paper: fixed-trajectory write intervention -> stronger wording reduction -> matched downstream propagation -> bounded interpretation/generalization."},
            {"id": "scope", "result": "Title/abstract scope is narrowed from generic self-improving agents to reward-conditioned agent memory; broader writer/domain/live claims remain disallowed."},
            {"id": "novelty", "result": "Introduction and Related Work explicitly surrender judge unreliability, feedback-driven memory construction, memory-reward amplification, and general variance novelty."},
            {"id": "missingness", "result": "Paired provider completion is part of the Experimental Setup estimand; downstream source support is explicitly conditional on four complete pairs."},
            {"id": "boundary", "result": "No-memory and GLM results are presented as branch-location and cross-writer boundaries rather than extra contributions."},
            {"id": "simplification", "result": "Released top-1 retrieval reduction is integrated as a matched scientific stop for multi-bit full-bank interaction, not as omitted experimentation."},
            {"id": "presentation", "result": "Research OS stage labels and reviewer-response language are removed from main scientific headings/prose; detailed execution accounting is moved to the appendix."},
            {"id": "chronology", "result": "Conclusion describes the terminal confirmation as a same-support uniform replication after an initial non-pass, with unchanged support and dual gate."},
            {"id": "variance", "result": "Plug-in corruption variance is demoted to bounded consequence analysis and removed from the top-level conclusion contribution summary."},
            {"id": "system_projection", "result": "PaperStory V3 and the reader-facing C1 summary reflect fresh no-memory evidence, the GLM cross-writer boundary, and the top-1 retrieval reduction."},
        ],
        "scientific_values_changed": False,
        "scientific_claims_expanded": False,
        "new_scientific_provider_calls": 0,
        "new_rollouts": 0,
        "external_review_calls": 0,
        "external_review_deferred_to_evening": True,
        "cumulative_r3_repair_provider_calls_exact": qa["cumulative_r3_repair_provider_calls_exact"],
        "cumulative_r3_repair_provider_calls_observable_lower_bound": qa["cumulative_r3_repair_provider_calls_observable_lower_bound"],
        "cumulative_r3_repair_scientifically_usable_provider_calls": qa["cumulative_r3_repair_scientifically_usable_provider_calls"],
        "cumulative_r3_repair_terminal_rollouts": qa["cumulative_r3_repair_terminal_rollouts"],
        "canonical_stable_registry_overwritten": False,
        "canonical_note": "The stable PaperRegistry/acceptance ledger is intentionally not overwritten by this daytime candidate before the next single external review.",
        "scientific_authority": False,
        "experiment_authority": False,
        "submission_authority": False,
    }
    target = HERE / "daytime-story-revision-receipt.json"
    target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "pdf_sha256": receipt["current_candidate_pdf_sha256"],
        "qa_sha256": receipt["manuscript_qa_sha256"],
        "new_scientific_provider_calls": receipt["new_scientific_provider_calls"],
        "cumulative_r3_repair_provider_calls_observable_lower_bound": receipt["cumulative_r3_repair_provider_calls_observable_lower_bound"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
