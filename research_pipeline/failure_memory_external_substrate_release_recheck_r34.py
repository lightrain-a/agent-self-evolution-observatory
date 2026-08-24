#!/usr/bin/env python3
"""Record a bounded public release-surface recheck for B1 replacement substrates."""
from __future__ import annotations

import json
from pathlib import Path

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"


def build() -> dict:
    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R34-EXTERNAL-SUBSTRATE-RELEASE-RECHECK",
        "recorded_date": "2026-08-24",
        "status": "NO_EXTERNAL_REPLACEMENT_EXECUTION_SURFACE_UNBLOCKED_SMA_REMAINS_PRIORITY1",
        "role": "BOUNDED_PUBLIC_RELEASE_SURFACE_RECHECK_NO_EXECUTION_AUTHORITY",
        "scientific_relationship": "POST_R19_STOP_SUPPORT_SEARCH_NOT_NEW_IDEA_NOT_R19_RESUME",
        "candidates": [
            {
                "name": "Spatial Memory Agent (SMA)",
                "priority": 1,
                "construct_match": "STRONGEST_EXTERNAL_SOURCE_OUTCOME_PROVENANCE_CANDIDATE",
                "official_project_page": "https://aim-uofa.github.io/SMA/",
                "primary_paper": "https://arxiv.org/abs/2608.12743",
                "bounded_recheck_finding": "Official project page currently exposes Paper/arXiv links and states Code Coming Soon; no first-party GitHub code entry is exposed on that page.",
                "code_release_unblocked": False,
                "schema_runtime_verified": False,
                "exact_information_l2_ready": False,
                "execute_now": False,
                "preferred_next_action": "WAIT_FOR_FIRST_PARTY_CODE_RELEASE_THEN_PIN_COMMIT_AND_INSPECT_MEMORY_CARD_SOURCE_OUTCOME_SCHEMA",
            },
            {
                "name": "Trajectory-Informed Memory Generation for Self-Improving Agent Systems (IBM Research)",
                "priority": 2,
                "construct_match": "STRONG_SOURCE_TRAJECTORY_OUTCOME_BUT_NATIVE_WRITER_CONSOLIDATION_CONFOUNDED",
                "primary_paper": "https://arxiv.org/abs/2603.10600",
                "bounded_recheck_finding": "No author-released executable repository for this memory framework was discovered in the bounded exact-title/arXiv/GitHub recheck. The paper references IBM CUGA as an application platform, which is not treated as a release of the paper-specific memory artifact.",
                "code_release_unblocked": False,
                "schema_runtime_verified": False,
                "exact_information_l2_ready": False,
                "execute_now": False,
                "preferred_next_action": "WAIT_FOR_AUTHOR_CODE_OR_SOURCE_FAITHFUL_ARTIFACT_RELEASE_THEN_INSPECT_PRE_CONSOLIDATION_SCHEMA",
            },
            {
                "name": "MutMem / HOM-AIMOS",
                "priority": None,
                "construct_match": "FAILED_FOR_B1_SOURCE_PROVENANCE",
                "bounded_recheck_finding": "Existing source-level audit identifies the signed valence field as post-use reward feedback rather than memory-generating trajectory outcome provenance.",
                "code_release_unblocked": "IRRELEVANT_TO_CURRENT_STOP",
                "exact_information_l2_ready": False,
                "execute_now": False,
                "preferred_next_action": "KEEP_STOPPED_AS_METADATA_MECHANICS_WITNESS_ONLY",
            },
        ],
        "adjudication": {
            "replacement_execution_ready_now": False,
            "SMA_remains_priority1": True,
            "IBM_remains_priority2": True,
            "MutMem_remains_scientific_stop_for_B1_source_provenance": True,
            "WebArena_support_failure_does_not_relax_construct_match": True,
            "third_party_or_platform_code_does_not_substitute_for_first_party_paper_artifact": True,
            "absence_of_public_release_is_scientific_negative": False,
            "scientific_verdict": "NO_VERDICT_SUPPORT_SEARCH_ONLY",
        },
        "reopen_condition": {
            "preferred_trigger": "SMA_FIRST_PARTY_CODE_RELEASE",
            "after_trigger": [
                "pin immutable commit/content hash",
                "inspect whether source-question outcome is a separate stored field",
                "inspect whether it can be exposed without changing card content/retrieval/TRS/order",
                "enumerate fresh independent exact-information capacity before any treatment outcome",
                "freeze endpoint, schedule, analysis, and support retry policy",
                "obtain new explicit scientific and execution authority",
            ],
            "fallback_trigger": "IBM_FIRST_PARTY_CODE_OR_SOURCE_FAITHFUL_ARTIFACT_RELEASE",
            "same_asset_R33_27_unit_fallback_automatically_authorized": False,
        },
        "authority": {
            "scientific_execution": False,
            "experiment": False,
            "model_calls": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "gpu": False,
            "claim_expansion": False,
            "submission": False,
        },
    }


def main() -> None:
    out = Path("generated/d2-failure-memory-provenance-r34-external-substrate-release-recheck.json")
    payload = build()
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "replacement_ready": False, "priority1": "SMA"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
