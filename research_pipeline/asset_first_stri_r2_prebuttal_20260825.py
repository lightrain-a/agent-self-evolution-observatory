from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated/asset-first-stri-r2-prebuttal-20260825.json"
OUT_MD = ROOT / "paper_drafts/stri-r2-mechanism-20260825/PREBUTTAL.md"

P0 = ROOT / "generated/asset-first-stri-r2-credit-fragmentation-result-20260825.json"
P1 = ROOT / "generated/asset-first-stri-r2-credit-fragmentation-phase-result-20260825.json"
P2 = ROOT / "generated/asset-first-stri-r2-selection-credit-decomposition-result-20260825.json"
P3 = ROOT / "generated/asset-first-stri-r2-partition-geometry-result-20260825.json"
PREV = ROOT / "generated/asset-first-stri-r2-natural-prevalence-qualification-20260825.json"
SECOND = ROOT / "generated/asset-first-stri-r2-second-system-credit-partition-20260825.json"
NOVELTY = ROOT / "generated/asset-first-stri-r2-credit-fragmentation-novelty-reduction-20260825.json"
R19_STOP = ROOT / "generated/asset-first-stri-autoskill-multitask-pilot-stage1-20260824.json"
GATE = ROOT / "generated/asset-first-stri-r2-manuscript-gate-20260825.json"
INTEGRITY = ROOT / "generated/asset-first-stri-r2-manuscript-integrity-receipt-20260825.json"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def evidence_ref(path: Path) -> dict[str, str]:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha_file(path)}


def build() -> dict[str, Any]:
    p0, p1, p2, p3 = load(P0), load(P1), load(P2), load(P3)
    prev, second, novelty, stop = load(PREV), load(SECOND), load(NOVELTY), load(R19_STOP)
    gate, integrity = load(GATE), load(INTEGRITY)

    required = {
        "p0": p0.get("decision") == "PASS_RELEASED_CREDIT_FRAGMENTATION_MECHANISM",
        "p1": p1.get("decision") == "PASS_CREDIT_FRAGMENTATION_PHASE_DIAGRAM" and p1.get("headline", {}).get("analytic_mismatches") == 0,
        "p2": p2.get("decision") == "PASS_TWO_CHANNEL_SELECTION_CREDIT_DECOMPOSITION",
        "p3": p3.get("decision") == "PASS_ARBITRARY_PARTITION_GEOMETRY" and p3.get("headline", {}).get("formula_mismatches") == 0,
        "novelty": novelty.get("status") == "SURVIVES_NARROWLY_AS_STAGE_LOCAL_CREDIT_FRAGMENTATION",
        "prevalence_hold": prev.get("decision") == "HOLD_NATURAL_PREVALENCE_UNRESOLVED_RUNTIME_OUTPUT_NOT_RELEASED" and prev.get("natural_prevalence_established") is False,
        "second_system_scoped": second.get("decision") == "QUALIFY_SKILLSVOTE_REQUEST_PARTITION_ANALOGUE_ONLY" and second.get("second_exact_phase_law_replication") is False,
        "r19_stop": stop.get("decision") == "STOP_EXPANSION_STAGE1_GATE_NOT_MET",
        "manuscript_gate": gate.get("decision") == "PASS_R2_MECHANISM_SPINE_DRAFT_KEEP_R19_CANONICAL" and gate.get("pass") is True,
        "integrity": ((integrity.get("audit") or {}).get("status") == "PASS_POST_DRAFT_INTEGRITY" and (integrity.get("audit") or {}).get("pass") is True),
    }
    if not all(required.values()):
        raise RuntimeError("R2 prebuttal evidence not ready: " + ", ".join(k for k, v in required.items() if not v))

    sources = {
        "identity_fragmentation": {
            "title": "Frontiers: The Identity Fragmentation Bias",
            "authors": "Tesary Lin; Sanjog Misra",
            "venue": "Marketing Science 41(3), 2022",
            "url": "https://pubsonline.informs.org/doi/10.1287/mksc.2022.1360",
            "absorbed_claim": "Splitting observations from one underlying entity across identifiers can bias inference; generic identity fragmentation is not novel.",
        },
        "strategic_replication": {
            "title": "Multi-armed Bandit Algorithm against Strategic Replication",
            "authors": "Suho Shin; Seungjoon Lee; Jungseul Ok",
            "venue": "AISTATS 2022",
            "url": "https://proceedings.mlr.press/v151/shin22a.html",
            "absorbed_claim": "Duplicate arms can manipulate selection opportunity; selection duplication is inherited rather than R2 novelty.",
        },
        "action_redundancy": {
            "title": "Action Redundancy in Reinforcement Learning",
            "authors": "Nir Baram; Guy Tennenholtz; Shie Mannor",
            "venue": "UAI 2021",
            "url": "https://proceedings.mlr.press/v161/baram21a.html",
            "absorbed_claim": "Equivalent actions can make action-space multiplicity a poor proxy for transition diversity.",
        },
        "rethinkskill": {
            "title": "Rethinking Self-Evolving Agent Skills: Feedback Dynamics over Multiple Rounds",
            "authors": "Yuxuan Liu et al.",
            "venue": "arXiv:2608.02636, 2026",
            "url": "https://arxiv.org/abs/2608.02636",
            "absorbed_claim": "Feedback composition and validation-filtered multi-round skill revision are already directly studied.",
        },
        "skillsvote": {
            "title": "SkillsVote: Lifecycle Governance of Agent Skills from Collection, Recommendation to Evolution",
            "authors": "Hongyi Liu et al.",
            "venue": "arXiv:2605.18401, 2026",
            "url": "https://arxiv.org/abs/2605.18401",
            "absorbed_claim": "Skill-linked attribution and evidence-gated updates are already lifecycle mechanisms; R2 cannot claim those components as new.",
        },
        "skillsp": {
            "title": "Skill Self-Play: Pushing the Frontier of LLM Capability with Co-Evolving Skills",
            "authors": "Siyuan Huang et al.",
            "venue": "arXiv:2607.22529, 2026",
            "url": "https://arxiv.org/abs/2607.22529",
            "role": "First-party released mechanism realization audited by R2.",
        },
    }

    objections = [
        {
            "id": "PB-O1-GENERIC-IDENTITY-FRAGMENTATION",
            "severity": "MAJOR_NOVELTY",
            "reviewer_attack": "This is known identity-fragmentation bias applied to a skill library; the threshold math is elementary.",
            "concede": [
                "Generic identifier fragmentation is known and is explicitly not claimed as new.",
                "The abstract quotient/commutation criterion and threshold algebra are elementary and are not solver/theorem novelty by themselves.",
            ],
            "residual_response": "R2 localizes a released closed-loop control mechanism after selection: the same skill identity is a persistent sufficient-statistic container and lifecycle unit; holding semantic feedback fixed, exact refinement changes future active action availability because identity-local evidence is partitioned before a nonlinear gate. P0 removes the known selection channel, P1/P3 make an ex-ante boundary prediction, and P2 intervenes on selection and credit independently.",
            "decisive_evidence": [evidence_ref(P0), evidence_ref(P1), evidence_ref(P2), evidence_ref(P3), evidence_ref(NOVELTY)],
            "what_would_defeat_r2": "A closest work that studies exact-semantic identity refinement under fixed post-selection feedback and identifies/repairs the same persistent lifecycle noncommutativity, or a failure of P0/P3 under the pinned release.",
            "needs_new_outcome_experiment": False,
            "disposition": "SURVIVES_NARROWLY_STAGE_LOCAL_RESIDUAL",
        },
        {
            "id": "PB-O2-THRESHOLD-TOY",
            "severity": "MAJOR_MECHANISM_DEPTH",
            "reviewer_attack": "The 8 versus 4+4 example is a hand-picked threshold toy; balanced cloning manufactures the phase law.",
            "concede": ["Skill-SP's released retirement rule contains a discrete threshold, so the concrete P1 realization is threshold-gated."],
            "residual_response": "P3 removes the balanced-allocation dependence. For any weak k-way partition with total retirement-eligible evidence N, every partition fragments throughout M<=N<kM. For N>=kM, fragmentation becomes partition-dependent with an exact stars-and-bars fraction. Dynamic-programming counts match the closed form in all 205 audited (k,N) cells. Balanced allocation is the best-case earliest recovery, not the special case that creates the defect.",
            "decisive_evidence": [evidence_ref(P3)],
            "headline": {
                "cells": p3["grid"]["cells"],
                "formula_mismatches": p3["headline"]["formula_mismatches"],
                "guaranteed_region_failures": p3["headline"]["guaranteed_region_failures"],
                "fragmentation_fraction_at_k2_kM": p3["headline"]["by_clone_multiplicity"]["2"]["fragmentation_fraction_at_kM"],
                "fragmentation_fraction_at_k4_kM": p3["headline"]["by_clone_multiplicity"]["4"]["fragmentation_fraction_at_kM"],
            },
            "what_would_defeat_r2": "Any partition in M<=N<kM for which native and aggregate class lifecycle agree, or any mismatch between exact DP counting and the frozen closed-form expression.",
            "needs_new_outcome_experiment": False,
            "disposition": "CLOSED_BY_ARBITRARY_PARTITION_GEOMETRY",
        },
        {
            "id": "PB-O3-RSTAR-GRAFT",
            "severity": "MODERATE_STORY_COHESION",
            "reviewer_attack": "The paper splices an old support-cone routing paper onto a new lifecycle-fragmentation paper; R* and credit fragmentation are unrelated contributions.",
            "concede": ["R* is not the R2 novelty and should not dominate the paper.", "Most old weighting baselines and robustness inventories belong in the supplement."],
            "residual_response": "The 2x2 intervention defines the common causal object: identity is consumed at two different stages. R* is the partial-overlap generalization of the pre-action selection surface; credit fragmentation is the post-feedback persistent-state surface. Quotient selection alone repairs only selection, quotient credit alone repairs only lifecycle, and both together restore both canonical semantic endpoints.",
            "decisive_evidence": [evidence_ref(P2)],
            "what_would_defeat_r2": "If the 2x2 cells failed to separate the surfaces, or if repairing one surface automatically repaired the other, the unified two-surface story would collapse.",
            "needs_new_outcome_experiment": False,
            "disposition": "CLOSED_BY_ORTHOGONAL_STAGE_DECOMPOSITION",
        },
        {
            "id": "PB-O4-SKILLSVOTE-ONLY-CODE-ISOMORPHISM",
            "severity": "MODERATE_GENERALITY",
            "reviewer_attack": "SkillsVote only gives a code-shape analogy; no second-system lifecycle effect is demonstrated.",
            "concede": ["Correct: SkillsVote is not a second phase-law or outcome replication.", "No updater model is executed in this audit."],
            "residual_response": "The purpose of SkillsVote is narrower: an independent released system also partitions semantically identical evidence by skill identity before an updater. Its first-party transformation maps one 8-record context to two 4-record edit requests under exact identity relabeling and back to one 8-record request under semantic quotienting. This corroborates the architectural precondition while preserving the effect-generalization boundary.",
            "decisive_evidence": [evidence_ref(SECOND)],
            "what_would_defeat_r2": "If the first-party feedback-to-update transformation did not key edit contexts by skill identity, or quotient relabeling failed to restore the canonical request topology.",
            "needs_new_outcome_experiment": False,
            "disposition": "SCOPED_STRUCTURAL_CORROBORATION_ONLY",
        },
        {
            "id": "PB-O5-NATURAL-PREVALENCE",
            "severity": "MAJOR_EXTERNAL_VALIDITY",
            "reviewer_attack": "The mechanism may exist in code but almost never occur during endogenous Skill-SP evolution.",
            "concede": ["This remains unresolved.", "The public release and three pinned mirrors do not preserve evolved skills.json or retired ledgers, so empirical entry frequency into the fragmentation region cannot be estimated."],
            "residual_response": "R2 therefore claims mechanism existence, exact counterfactual behavior, and trigger-opportunity plausibility only. The first-party loop updates identity-local statistics before pruning, uses M=8, and carries the active library across rounds, but no prevalence claim is made.",
            "decisive_evidence": [evidence_ref(PREV)],
            "what_would_close_fully": "A content-addressed evolved runtime library/retired ledger or a separately preregistered faithful run exposing endogenous per-skill evidence partitions without outcome-driven selection.",
            "needs_new_outcome_experiment": True,
            "disposition": "OPEN_HOLD_BLOCKS_PREVALENCE_NOT_MECHANISM_EXISTENCE",
        },
        {
            "id": "PB-O6-REPAIR-WITHOUT-UTILITY",
            "severity": "MODERATE_CLOSURE",
            "reviewer_attack": "Quotienting restores internal controller endpoints but is not shown to improve task performance.",
            "concede": ["No downstream utility improvement is claimed."],
            "residual_response": "The scientific estimand is representation invariance. P2 is a mechanism intervention: it changes the diagnosed variables and restores the frozen semantic endpoints. The analysis-only contribution is complete if framed as a mechanism/certificate paper, not a new utility-maximizing method.",
            "decisive_evidence": [evidence_ref(P2), evidence_ref(GATE), evidence_ref(INTEGRITY)],
            "what_would_defeat_r2": "If the paper claimed downstream utility or a deployable performance method without evidence, that claim should be rejected; the current draft explicitly does not make it.",
            "needs_new_outcome_experiment": False,
            "disposition": "ANALYSIS_ONLY_EXCEPTION_KEEP_SCOPE_NARROW",
        },
    ]

    result = {
        "schema_version": "1.0",
        "paper_id": "E1.STRI",
        "stage": "R2_PREBUTTAL_AND_CLOSEST_WORK_COLLISION",
        "decision": "READY_FOR_INDEPENDENT_REVIEW_WITH_ONE_OPEN_EXTERNAL_VALIDITY_HOLD",
        "evidence_checks": required,
        "primary_closest_work": sources,
        "objections": objections,
        "summary": {
            "decision_critical_objections": len(objections),
            "paper_only_closed_or_scoped": sum(not row["needs_new_outcome_experiment"] for row in objections),
            "requires_new_outcome_or_runtime_evidence": sum(row["needs_new_outcome_experiment"] for row in objections),
            "open_major_hold_ids": [row["id"] for row in objections if row["needs_new_outcome_experiment"]],
            "canonical_r19_replacement_authorized": False,
            "independent_model_review_still_required_for_promotion": True,
        },
        "claim_boundary": "This packet prepares rebuttal and paper-only repairs. It does not authorize a prevalence claim, downstream utility claim, second-system lifecycle-effect claim, task-general behavior claim, experiment, GPU run, canonical promotion, or submission.",
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    result["result_canonical_sha256"] = canonical_sha(result)
    return result


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# STRI-R2 Prebuttal Packet",
        "",
        f"Decision: **{result['decision']}**",
        "",
        "This is a draft-only reviewer attack map. It does not replace canonical R19.",
        "",
        "## Closest-work collision table",
        "",
        "| Neighbor | What is absorbed | R2 residual |",
        "|---|---|---|",
    ]
    residual_by_source = {
        "identity_fragmentation": "Persistent post-selection credit/lifecycle partition changes future active skill state under fixed semantic feedback.",
        "strategic_replication": "Selection is removed in P0; lifecycle still diverges under identical feedback.",
        "action_redundancy": "The audited endpoint is persistent evidence/lifecycle state after action, not redundant transition choice.",
        "rethinkskill": "Feedback content is fixed; only exact identity partition varies.",
        "skillsvote": "Independent first-party partition-before-updater topology; explicitly not outcome replication.",
        "skillsp": "First-party mechanism realization used for P0/P1/P2/P3.",
    }
    for key, src in result["primary_closest_work"].items():
        lines.append(f"| {src['title']} | {src.get('absorbed_claim', src.get('role',''))} | {residual_by_source[key]} |")
    lines += ["", "## Decision-critical objections", ""]
    for row in result["objections"]:
        lines += [
            f"### {row['id']} — {row['severity']}",
            "",
            f"**Attack.** {row['reviewer_attack']}",
            "",
            "**Concede.** " + " ".join(row["concede"]),
            "",
            f"**Response.** {row['residual_response']}",
            "",
            f"**Disposition.** `{row['disposition']}`",
            "",
        ]
    lines += [
        "## Promotion rule",
        "",
        "Canonical R19 remains authoritative. R2 can be promoted only after independent draft review; natural-prevalence claims additionally require new content-addressed runtime/outcome evidence under a separate frozen contract.",
        "",
    ]
    return "\n".join(lines)


def write() -> dict[str, Any]:
    result = build()
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(result), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(write(), ensure_ascii=False, indent=2))
