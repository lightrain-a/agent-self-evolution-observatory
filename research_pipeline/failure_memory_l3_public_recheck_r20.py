from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
PRIOR = Path("generated/d2-failure-memory-provenance-l3-support-recheck-r8.json")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict[str, Any]:
    prior = load(PRIOR)
    if prior["status"] != "NO_NEW_FIRST_PARTY_L3_ARTIFACT_DISCOVERED":
        raise RuntimeError("prior L3 support state drift")
    if prior["adjudication"]["l3_support_unblocked"] is not False:
        raise RuntimeError("prior L3 unexpectedly unblocked")

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_type": "source-faithful-l3-public-release-surface-recheck",
        "receipt_id": "D2-C45-L3-PUBLIC-RELEASE-RECHECK-R20",
        "recorded_date": "2026-08-24",
        "status": "NO_FIRST_PARTY_FINANCIAL_L3_RELEASE_SURFACE_DELTA_DISCOVERED",
        "role": "ZERO_SCIENTIFIC_EXECUTION_PUBLIC_SUPPORT_RECHECK",
        "question": "Has the source paper or a discoverable first-party public release exposed the per-query financial ReasoningBank/audit bundle and runtime bindings needed for source-faithful L3 transport?",
        "prior_r8": {
            "path": str(PRIOR),
            "sha256": sha(PRIOR),
            "status": prior["status"],
        },
        "primary_source_snapshot": {
            "arxiv_id": "2608.17684",
            "title": "Auditing Self-Evolution in Financial Agents: Capability Gains, Security Drift, and Execution-Interface Mismatch",
            "authors": ["Jialong Li", "Jialing Zhu"],
            "arxiv_abs": "https://arxiv.org/abs/2608.17684",
            "arxiv_html": "https://arxiv.org/html/2608.17684v1",
            "version_observed": "v1",
            "submitted_date": "2026-08-18",
            "later_arxiv_version_observed": False,
            "release_statement": "Code and audit artifacts will be released upon publication.",
            "release_statement_location": "Conclusion",
            "direct_author_project_repository_link_observed_in_arxiv_metadata": False,
            "generic_arxiv_code_data_media_integrations_are_not_first_party_release_evidence": True,
        },
        "bounded_public_discovery": {
            "queries": [
                "exact paper title + GitHub",
                "arXiv 2608.17684 + GitHub repository",
                "arXiv 2608.17684 + Hugging Face",
                "exact paper title + code data audit ReasoningBank",
                "author names/ORCID + GitHub",
            ],
            "github_first_party_financial_audit_repository_discovered": False,
            "huggingface_first_party_financial_audit_bundle_discovered": False,
            "indexed_third_party_request_code_pages_seen": True,
            "third_party_request_code_page_counts_as_release": False,
            "orcid_pages_required_javascript_and_were_not_used_as_negative_evidence": True,
            "scope_note": "This is a bounded public discovery result as of the recorded date, not proof that no private, unindexed, or future release exists.",
        },
        "required_l3_surface": {
            "per_query_financial_reasoningbank_records_or_equivalent": True,
            "source_trajectory_outcome_provenance_join": True,
            "source_writer_model_prompt_and_checkpoint_binding": True,
            "source_embedding_model_and_retrieval_binding": True,
            "provenance_bearing_memory_interface_runtime_fields": True,
            "source_native_downstream_units_and_schedule": True,
            "content_addressable_artifacts_sufficient_for_same_information_transport": True,
        },
        "availability": {
            "per_query_financial_reasoningbank_bundle_publicly_verified": False,
            "source_writer_checkpoint_and_prompt_binding_publicly_verified": False,
            "source_embedding_binding_publicly_verified": False,
            "source_native_provenance_intervention_surface_publicly_verified": False,
            "all_required_l3_surface_available": False,
        },
        "adjudication": {
            "release_surface_delta_vs_r8": False,
            "l3_support_unblocked": False,
            "l3_execution_authorized": False,
            "webarena_l2b_can_substitute_for_l3": False,
            "generic_reasoningbank_repo_can_substitute_for_financial_bundle": False,
            "absence_of_public_release_is_scientific_negative": False,
            "scientific_verdict": "NO_VERDICT_SUPPORT_FAILURE",
            "o5_r19_state_changed": False,
            "paper_claims_changed": False,
        },
        "reopen_condition": {
            "trigger": "A first-party publication/repository/artifact release or independently verified equivalent exposes the financial per-query provenance-bearing bundle and auditable source runtime bindings.",
            "then_require": [
                "content-address the newly released source artifacts before inspection-driven task selection",
                "freeze source-faithful L3 estimand and independent units pre-outcome",
                "verify writer/model/embedding/memory-interface and downstream schedule bindings",
                "obtain separate explicit L3 scientific and experiment/model-call authority",
            ],
        },
        "authority": {
            "scientific": False,
            "experiment": False,
            "model_calls": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "gpu": False,
            "submission": False,
        },
        "scientific_verdict": "NO_VERDICT_PUBLIC_SUPPORT_RECHECK_ONLY",
    }


def main() -> None:
    out = Path("generated/d2-failure-memory-provenance-l3-public-support-recheck-r20.json")
    d = build()
    out.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": d["status"], "l3_unblocked": d["adjudication"]["l3_support_unblocked"], "authority": d["authority"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
