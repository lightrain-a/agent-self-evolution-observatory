#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "stage-evidence-ladder-analysis-20260825.json"
OUT = ROOT / "evaluation-coarsening-analysis-20260825.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    ladder = {row["stage"]: row for row in source["evidence_ladder"]}
    required = {
        "persistent_write",
        "forced_capacity_side_control",
        "native_retrieval_exposure",
        "native_first_action_uptake",
        "native_terminal_outcome",
    }
    if set(ladder) != required:
        raise RuntimeError(f"stage set drift: {sorted(ladder)}")

    coarsenings: list[dict[str, Any]] = [
        {
            "view": "write_only",
            "observes": ["persistent_write"],
            "naive_conclusion": "The persistent update is strong because reward-conditioned writing reliably changes memory.",
            "what_it_cannot_distinguish": [
                "durable state change that later changes decisions",
                "durable state change that is retrieved but ignored",
                "durable state change that is never exposed natively",
            ],
            "current_evidence": ladder["persistent_write"]["observation"],
            "miscredit_risk": "credits behavioral authority at the state-construction surface",
        },
        {
            "view": "retrieval_only",
            "observes": ["native_retrieval_exposure"],
            "naive_conclusion": "Memory reuse is active because branch-specific memory is frequently retrieved.",
            "what_it_cannot_distinguish": [
                "retrieved content that changes the next action",
                "retrieved content that is present but policy-irrelevant",
            ],
            "current_evidence": ladder["native_retrieval_exposure"]["observation"],
            "miscredit_risk": "equates availability with policy uptake",
        },
        {
            "view": "native_endpoint_only",
            "observes": ["native_terminal_outcome"],
            "naive_conclusion": "Reward-conditioned memory has little or no downstream effect.",
            "what_it_cannot_distinguish": [
                "writer failure",
                "retrieval failure",
                "post-retrieval policy filtering",
                "heterogeneous cancellation or sparse task-local transport",
            ],
            "current_evidence": ladder["native_terminal_outcome"]["observation"],
            "miscredit_risk": "mistakes an end-to-end null/sparse endpoint for a diagnosis of the failed stage",
        },
        {
            "view": "forced_endpoint_only",
            "observes": ["forced_capacity_side_control"],
            "naive_conclusion": "Branch-specific memory has a meaningful downstream behavioral effect.",
            "what_it_cannot_distinguish": [
                "capacity under supplied memory",
                "native retrieval-and-policy transport under the deployed path",
            ],
            "current_evidence": ladder["forced_capacity_side_control"]["observation"],
            "miscredit_risk": "promotes a bypassed capacity surface into a native end-to-end claim",
        },
        {
            "view": "stage_resolved_signature",
            "observes": [
                "persistent_write",
                "forced_capacity_side_control",
                "native_retrieval_exposure",
                "native_first_action_uptake",
                "native_terminal_outcome",
            ],
            "naive_conclusion": "not applicable: the purpose is to preserve apparently conflicting stage evidence rather than collapse it",
            "what_it_distinguishes": [
                "persistent-state intervention is established",
                "downstream capacity exists when memory is supplied",
                "native exposure is substantial",
                "stable first-action uptake is not supported",
                "native terminal transport is sparse and sign-heterogeneous",
            ],
            "current_evidence": "SUPPORTED / SUPPORTED-SIDE-CONTROL / OBSERVED / NOT-SUPPORTED / SPARSE-HETEROGENEOUS",
            "diagnostic_gain": "localizes the strongest operational attenuation boundary after exposure and before stable action uptake while preventing write, retrieval, forced, or endpoint surfaces from standing in for one another",
        },
    ]

    hypotheses = [
        {
            "id": "H_WRITE_INERT",
            "description": "the reward-conditioned writer fails to create a durable branch-specific state contrast",
            "write_only": "testable",
            "retrieval_only": "not identified",
            "native_endpoint_only": "compatible with a weak endpoint",
            "forced_endpoint_only": "not identified",
            "full_signature": "inconsistent with frozen write evidence",
        },
        {
            "id": "H_GLOBAL_MEMORY_INSENSITIVITY",
            "description": "the downstream system is globally insensitive to supplied branch-specific memory content",
            "write_only": "not identified",
            "retrieval_only": "not identified",
            "native_endpoint_only": "compatible with a weak endpoint",
            "forced_endpoint_only": "weakened by positive forced leverage",
            "full_signature": "weakened, not eliminated",
        },
        {
            "id": "H_RETRIEVAL_ABSENCE",
            "description": "native attenuation is primarily because the branch-specific memory never reaches policy context",
            "write_only": "not identified",
            "retrieval_only": "weakened by observed exposure",
            "native_endpoint_only": "compatible with a weak endpoint",
            "forced_endpoint_only": "not identified because retrieval is bypassed",
            "full_signature": "weakened by 125/172 native exposures",
        },
        {
            "id": "H_EXPOSURE_EQUALS_UPTAKE",
            "description": "retrieval success is a valid surrogate for policy use",
            "write_only": "not identified",
            "retrieval_only": "would be incorrectly accepted if exposure were counted as reuse",
            "native_endpoint_only": "not identified",
            "forced_endpoint_only": "not identified",
            "full_signature": "rejected as an evaluation equivalence by observed exposure plus unsupported first-action contrast",
        },
        {
            "id": "H_UNIVERSAL_DIRECTIONAL_TRANSPORT",
            "description": "reward-conditioned branch memory has a stable signed terminal effect across tasks/domains",
            "write_only": "not identified",
            "retrieval_only": "not identified",
            "native_endpoint_only": "testable only if cell/domain structure is retained",
            "forced_endpoint_only": "not identified for native transport",
            "full_signature": "not supported: Shopping/Reddit are sparse and the Reddit nonzero signs oppose",
        },
    ]

    payload = {
        "schema_version": "1.0",
        "analysis_id": "C1-EVALUATION-COARSENING-R4-20260825",
        "artifact_type": "c1-evaluation-coarsening-analysis",
        "paper_id": source["paper_id"],
        "status": "SUPPORTED_DIAGNOSTIC_VALUE_OF_STAGE_RESOLUTION",
        "question": "What scientific ambiguity is introduced when persistent-memory evaluation observes only a coarsened subset of the write/exposure/uptake/outcome chain?",
        "source_binding": {"path": str(SOURCE.relative_to(ROOT.parent.parent)), "sha256": sha(SOURCE)},
        "stage_signature": {
            "ordered_native_stages": ["persistent_write", "native_retrieval_exposure", "native_first_action_uptake", "native_terminal_outcome"],
            "side_control": "forced_capacity_side_control",
            "observed_signature": ["SUPPORTED", "DIRECTLY_OBSERVED", "NOT_SUPPORTED_AT_FROZEN_PRIMARY_TEST", "SPARSE_HETEROGENEOUS_NOT_UNIVERSALLY_SUPPORTED"],
            "forced_capacity_state": "SUPPORTED_SIDE_CONTROL",
            "interpretation": "The signature preserves logically different evidence surfaces that become contradictory or non-diagnostic when individually projected into a one-number evaluation.",
        },
        "coarsened_views": coarsenings,
        "hypothesis_aliasing_matrix": hypotheses,
        "analysis_conclusion": {
            "core": "The contribution of stage resolution is diagnostic disambiguation, not merely finer reporting. Write-only, retrieval-only, native-endpoint-only, and forced-endpoint-only views support mutually different coarse summaries of the same system. The full signature separates state construction, capacity, availability, policy uptake, and native outcome.",
            "main_localization": source["localization"]["boundary_phrase"],
            "strongest_new_paper_role": "Use evaluation coarsening as the motivation for the stage-evidence ladder: the ladder is valuable because it prevents observational aliasing between distinct failure surfaces.",
            "causal_mediation_claim": False,
            "new_method_claim": False,
        },
        "does_not_imply": [
            "that the stage signature identifies a causal mediator coefficient",
            "that the current boundary generalizes to all memory systems",
            "that every coarse evaluation always yields the listed naive conclusion",
            "that forced and native endpoints are commensurate effect estimates",
        ],
        "execution": {"new_scientific_provider_calls": 0, "new_gpu_runs": 0, "new_scientific_experiments": 0},
        "authority": {"scientific": False, "experiment": False, "provider": False, "gpu": False, "claim_expansion": False, "submission": False},
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "coarsened_views": len(coarsenings), "hypotheses": len(hypotheses), "source_sha256": payload["source_binding"]["sha256"]}, indent=2))


if __name__ == "__main__":
    main()
