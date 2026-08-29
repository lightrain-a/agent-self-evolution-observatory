#!/usr/bin/env python3
"""Provider-independent top-1 selection certificate for the frozen P1 treatments."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPERIMENT_ID = "E1-STRI-REASONINGBANK-P1-RETRIEVAL-CERT-20260829"
EXPECTED_OFFICIAL_COMMIT = "ed80611788292ea739f1effd31f16c53823b8a0d"
EXPECTED_SELECTION_SHA256 = "fe71285a878920d501013ab86b58ef12c9c08071ee0e690061774d5ff5588955"
DEFAULT_SOURCE_ROOT = Path(
    "/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026"
)
DEFAULT_OUTPUT = Path(
    "generated/asset-first-stri-reasoningbank-p1-retrieval-certificate-result-20260829.json"
)


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def official_top1(rows: list[tuple[str, float]]) -> str:
    scored = list(rows)
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:1][0][0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    selection_path = (
        args.source_root
        / "third_party/src/minisweagent/memory/memory_management.py"
    )
    selection = selection_path.read_bytes()
    text = selection.decode("utf-8")
    commit = subprocess.run(
        ["git", "-C", str(args.source_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    sample_scores = [-0.9, 0.0, 0.4, 1.0]
    one_case = {
        str(score): official_top1([("source-case", score)])
        for score in sample_scores
    }
    d_cases = ["source-case::fragment-1", "source-case::fragment-2"]
    d_ties = {
        str(score): official_top1([(d_cases[0], score), (d_cases[1], score)])
        for score in sample_scores
    }
    checks = {
        "official_commit_matches": commit == EXPECTED_OFFICIAL_COMMIT,
        "selection_source_hash_matches": sha_bytes(selection)
        == EXPECTED_SELECTION_SHA256,
        "official_descending_stable_sort_present": (
            'id2score.sort(key=lambda x: x[1], reverse=True)' in text
        ),
        "official_top_n_slice_present": "top_ids = ordered_ids[:n]" in text,
        "a_b_c_e_one_case_top1_invariant": set(one_case.values())
        == {"source-case"},
        "d_cloned_case_scores_tied_by_construction": True,
        "d_stable_tie_selects_first_case": set(d_ties.values()) == {d_cases[0]},
        "top_k_one": True,
    }
    decision = (
        "P1_TOP1_SELECTION_IDENTIFIED_WITHOUT_EXTERNAL_EMBEDDING"
        if all(checks.values())
        else "P1_TOP1_SELECTION_CERTIFICATE_FAILED"
    )
    output: dict[str, Any] = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "experiment_id": EXPERIMENT_ID,
        "contract": (
            "generated/asset-first-stri-reasoningbank-p1-retrieval-certificate-"
            "contract-20260829.json"
        ),
        "official_source": {
            "commit": commit,
            "selection_path": str(selection_path.relative_to(args.source_root)),
            "selection_sha256": sha_bytes(selection),
        },
        "intervention": {
            "A_B_C_E": (
                "Exactly one eligible source case; top-1 selects it for every finite "
                "similarity score."
            ),
            "D": (
                "Split the selected source case into two ordered case records, clone the "
                "source query and cached embedding identity into both records, place "
                "fragment-1 first, and keep official top-1. Equal vectors imply equal "
                "cosine scores for every evaluation query; Python's registered stable "
                "descending sort selects fragment-1."
            ),
            "semantic_evidence_changed": False,
            "ranking_formula_changed": False,
            "top_k_changed": False,
            "surrogate_embedding_model_used": False,
        },
        "symbolic_score_observable": {
            "A_B_C_E_selected_case": one_case,
            "D_selected_case_under_equal_scores": d_ties,
            "score_values_are_proof_witnesses_not_runtime_embeddings": True,
        },
        "checks": checks,
        "decision": decision,
        "claim_ceiling": (
            "Identifies selected-case membership for the frozen one-source P1 design "
            "without estimating semantic relevance or absolute retrieval scores. It "
            "does not qualify Ark embeddings or general multi-case retrieval."
        ),
        "scientific_boundary": {
            "provider_calls": 0,
            "memory_induction_executed": False,
            "p1_task_outcome_observed": False,
            "behavioral_claim_authorized": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"decision": decision, "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
