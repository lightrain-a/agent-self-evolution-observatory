#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
R2 = HERE / "stage-transport-bottleneck-analysis-20260825.json"
OUT = HERE / "stage-evidence-ladder-analysis-20260825.json"
R2_SHA256 = "10a85adf4181c0b9f97691602eee28b59b918853d36a5735a9ea4fe864bef105"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise RuntimeError(msg)


def main() -> None:
    require(R2.is_file(), "missing R2 bottleneck analysis")
    require(sha(R2) == R2_SHA256, "R2 bottleneck analysis SHA drift")
    r2: dict[str, Any] = json.loads(R2.read_text(encoding="utf-8"))
    pattern = r2["observed_pattern"]

    write = pattern["write"]
    forced = pattern["forced_capacity_control"]
    exposure = pattern["native_exposure"]
    uptake = pattern["native_first_action"]
    shopping = pattern["native_terminal_shopping"]
    reddit = pattern["native_terminal_reddit"]

    require(write["shopping_diverged"] == "20/20", "write breadth drift")
    require(abs(float(write["same_mode_excess"]) - 0.105) < 1e-12, "same-mode excess drift")
    require(float(write["same_mode_exact_p"]) < 0.05, "same-mode control no longer passes")
    require(abs(float(forced["terminal_abs_delta"]) - 0.15625) < 1e-12, "forced capacity drift")
    require(float(forced["permutation_p"]) < 0.05, "forced capacity significance drift")
    require(int(exposure["retrieval_hits"]) == 125 and int(exposure["retrieval_opportunities"]) == 172, "native exposure drift")
    require(float(uptake["p"]) >= 0.05 and uptake["modal_changes"] == "0/36", "first-action evidence state drift")
    require(float(shopping["p"]) >= 0.05 and shopping["zero_cells"] == "34/36", "Shopping terminal evidence state drift")
    require(float(reddit["p"]) >= 0.05 and reddit["zero_cells"] == "6/8" and reddit["nonzero_signs"] == "opposite", "Reddit boundary drift")

    ladder = [
        {
            "stage": "persistent_write",
            "evidence_state": "SUPPORTED",
            "evidence_type": "controlled branch-state contrast plus stronger same-mode prompt control",
            "criterion": "all 20 Shopping pairs diverge and the preregistered same-mode excess gate passes",
            "observation": "20/20 Shopping write divergence; same-mode excess=0.105, exact p=0.0078",
            "claim_allowed": "reward-conditioned writer mode reliably changes durable persistent state under the frozen writer protocol",
        },
        {
            "stage": "forced_capacity_side_control",
            "evidence_state": "SUPPORTED_SIDE_CONTROL",
            "evidence_type": "forced fixed-evidence terminal experiment",
            "criterion": "frozen 0.15 practical floor and p<0.05",
            "observation": "terminal |Delta|=0.15625, p=0.00074",
            "claim_allowed": "the downstream system has measurable leverage when branch-specific memory is mechanically supplied",
        },
        {
            "stage": "native_retrieval_exposure",
            "evidence_state": "DIRECTLY_OBSERVED",
            "evidence_type": "native retrieval event count",
            "criterion": "descriptive observation, not a pass/fail inferential gate",
            "observation": "125/172 held-out retrieval opportunities expose branch-specific source memory (rate=0.727)",
            "claim_allowed": "retrieval absence alone is insufficient to explain the weak native endpoint",
        },
        {
            "stage": "native_first_action_uptake",
            "evidence_state": "NOT_SUPPORTED_AT_FROZEN_PRIMARY_TEST",
            "evidence_type": "matched first-action distributional contrast",
            "criterion": "frozen primary statistical test",
            "observation": "TV=0.06944, p=0.5801, 0/36 modal action changes",
            "claim_allowed": "stable first-action branch uptake is not supported on the frozen Shopping states",
        },
        {
            "stage": "native_terminal_outcome",
            "evidence_state": "SPARSE_HETEROGENEOUS_NOT_UNIVERSALLY_SUPPORTED",
            "evidence_type": "native terminal branch contrasts across Shopping and Reddit",
            "criterion": "domain-specific frozen terminal tests plus cell-level sparsity/sign audit",
            "observation": "Shopping |Delta|=0.02083, p=0.4289, 34/36 zero; Reddit |Delta|=0.125, p=0.2253, 6/8 zero, opposite signs",
            "claim_allowed": "a universal directional reward-memory-to-outcome transport effect is not supported",
        },
    ]

    # The boundary rule is deliberately ordinal rather than metric. We never divide
    # memory distance, retrieval rate, action TV, or endpoint effect sizes.
    native_order = ["persistent_write", "native_retrieval_exposure", "native_first_action_uptake", "native_terminal_outcome"]
    state_by_stage = {row["stage"]: row["evidence_state"] for row in ladder}
    positive_prerequisite_states = {"SUPPORTED", "DIRECTLY_OBSERVED"}
    boundary = None
    previous_positive = True
    for stage in native_order:
        state = state_by_stage[stage]
        if previous_positive and state not in positive_prerequisite_states:
            boundary = stage
            break
        previous_positive = previous_positive and state in positive_prerequisite_states
    require(boundary == "native_first_action_uptake", "ordinal localization boundary drift")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "c1-stage-evidence-ladder-analysis",
        "analysis_id": "C1-STAGE-EVIDENCE-LADDER-R3-20260825",
        "paper_id": r2["paper_id"],
        "status": "SUPPORTED_ORDINAL_POST_EXPOSURE_PRE_UPTAKE_LOCALIZATION",
        "source_binding": {"path": str(R2.relative_to(HERE.parents[1])), "sha256": R2_SHA256},
        "scientific_object": {
            "name": "stage evidence ladder for persistent-memory transport",
            "native_order": native_order,
            "side_control": "forced_capacity_side_control",
            "localization_rule": "Among ordered native stages, locate the first stage whose branch-transport evidence is not supported after all preceding prerequisites are supported or directly observed.",
            "ordinal_not_scalar": True,
            "cross_stage_ratio_forbidden": True,
            "causal_mediation_claim_forbidden": True,
        },
        "evidence_ladder": ladder,
        "localization": {
            "first_unsupported_native_stage": boundary,
            "boundary_phrase": "after native retrieval exposure and before stable first-action uptake",
            "why_not_write": "persistent write is supported",
            "why_not_retrieval_absence": "native branch-specific retrieval is directly observed in 125/172 opportunities",
            "why_not_global_insensitivity": "forced capacity side control passes its frozen practical/statistical gate",
            "why_not_terminal_only": "first-action uptake already fails to obtain support before the terminal stage",
            "strength": "OPERATIONAL_ORDINAL_LOCALIZATION_NOT_CAUSAL_MEDIATION",
        },
        "claim_hierarchy": [
            "intervention establishment: reward-conditioned writer mode changes persistent state",
            "capacity control: mechanically supplied branch memory can affect downstream behavior",
            "transport localization: native exposure is observed but stable first-action uptake is not supported",
            "boundary/generalization: native terminal effects are sparse and sign-heterogeneous",
        ],
        "does_not_imply": [
            "all retrieved memory was read or causally used by the policy",
            "a numerical transport efficiency can be computed across heterogeneous stage metrics",
            "the first-action boundary is a causal mediator",
            "the CBRG method has a measured positive or negative behavioral effect",
            "the same boundary necessarily holds for other writers, backbones, domains, or memory architectures",
        ],
        "execution": {"new_scientific_provider_calls": 0, "new_gpu_runs": 0, "new_scientific_experiments": 0},
        "authority": {"scientific": False, "experiment": False, "provider": False, "gpu": False, "claim_expansion": False, "submission": False},
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "boundary": boundary, "stages": len(ladder), "provider_calls": 0, "gpu_runs": 0}, indent=2))


if __name__ == "__main__":
    main()
