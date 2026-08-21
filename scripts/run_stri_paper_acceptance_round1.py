from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from research_pipeline.paper_acceptance import (
    MockReviewMode,
    ObjectionEvidenceState,
    PaperContract,
    PaperState,
    ReviewerObjection,
    ScientificPaperStatus,
    StoryCandidate,
)
from research_pipeline.paper_acceptance_ledger import (
    advance_paper_ledger,
    build_paper_ledger_index,
    load_paper_ledger,
    record_mock_review,
    record_story_search,
    validate_paper_ledger,
)


def _contract_from_ledger(row: dict) -> PaperContract:
    payload = row.get("contract") or {}
    return PaperContract(
        paper_id=str(payload["paper_id"]),
        title=str(payload["title"]),
        central_question=str(payload["central_question"]),
        supported_claims=dict(payload.get("supported_claims") or {}),
        unsupported_claims=dict(payload.get("unsupported_claims") or {}),
        limitations=tuple(payload.get("limitations") or []),
        reopen_conditions=tuple(payload.get("reopen_conditions") or []),
        evidence_refs=tuple(payload.get("evidence_refs") or []),
        scientific_status=ScientificPaperStatus(str(payload["scientific_status"])),
    )


def _story_candidates() -> list[StoryCandidate]:
    return [
        StoryCandidate(
            story_id="S1-INVARIANCE-BOUNDARY",
            title="Representation invariance as the paper question; support geometry as the exact boundary",
            framing=(
                "Lead with the self-evolution design principle: semantically equivalent skill taxonomies should not alter the control surface. "
                "Use released identity sensitivity as the phenomenon, R*(A) as the exact package-only exposure boundary, and the high-overlap equalizable regime as the mechanism falsifier."
            ),
            contribution_order=("N1", "N2", "N3"),
            emphasized_claim_ids=("N1", "N2", "N3"),
            figure_order=("stri-overview", "stri-rstar-boundary", "stri-ablation-robustness"),
        ),
        StoryCandidate(
            story_id="S2-CERTIFICATE-FIRST",
            title="Exact support-geometry certificate first",
            framing=(
                "Lead with R*(A) as an exact diagnostic for package-only additive exposure equalizability, then motivate it using released skill-system representation sensitivity."
            ),
            contribution_order=("N2", "N3", "N1"),
            emphasized_claim_ids=("N2", "N3"),
            figure_order=("stri-rstar-boundary", "stri-overview", "stri-ablation-robustness"),
        ),
        StoryCandidate(
            story_id="S3-RELEASED-PHENOMENON-FIRST",
            title="Released-system representation sensitivity first",
            framing=(
                "Lead with two released systems where package identity changes control exposure or retrieval, then narrow to the support-geometry boundary that is exactly auditable in Skill-SP."
            ),
            contribution_order=("N1", "N3", "N2"),
            emphasized_claim_ids=("N1", "N3"),
            figure_order=("stri-overview", "stri-ablation-robustness", "stri-rstar-boundary"),
        ),
        StoryCandidate(
            story_id="S4-DYNAMIC-UTILITY",
            title="Representation sensitivity causes downstream utility loss",
            framing="Center the paper on downstream dynamic utility degradation caused by STRI violations.",
            contribution_order=("N1", "U1"),
            emphasized_claim_ids=("U1",),
        ),
        StoryCandidate(
            story_id="S5-LP-NOVELTY",
            title="A new optimization algorithm for skill-taxonomy balancing",
            framing="Center the paper on computational novelty of STRI-Cert relative to linear programming.",
            contribution_order=("N2", "U2"),
            emphasized_claim_ids=("U2",),
        ),
    ]


def _blind_objections() -> list[ReviewerObjection]:
    return [
        ReviewerObjection(
            "B1-SIGNIFICANCE",
            "significance",
            "The paper is strongest as a representation-invariance audit, but the current narrative risks making a static exposure certificate sound like downstream self-evolution performance. Why is the static control-surface property itself important?",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("N1", "N2"),
        ),
        ReviewerObjection(
            "B2-DEFINITION-SCOPE",
            "technical-scope",
            "The title says representation invariance while the exact theorem is package-only additive exposure equalizability on a frozen support matrix. The manuscript must make this scope relation explicit early and repeatedly.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("N2",),
        ),
        ReviewerObjection(
            "B3-MECHANISM",
            "mechanism",
            "The most convincing scientific result is not the positive R*=2 alone but the negative high-overlap R*=1 regime. The paper should foreground that this falsifies overlap prevalence as the mechanism.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("N3",),
        ),
        ReviewerObjection(
            "B4-NOVELTY-LP",
            "novelty",
            "A skeptical reviewer may reduce STRI-Cert to a standard LP. The manuscript should claim novelty in the audited self-evolution representation question and exact boundary, not in optimization machinery.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("N2",),
        ),
        ReviewerObjection(
            "B5-DYNAMIC-EVIDENCE",
            "evidence",
            "The failed Qwen3 dynamic pilot does not establish downstream harm. Any attempt to use it to claim dynamic utility or task degradation would exceed the frozen evidence contract.",
            True,
            ObjectionEvidenceState.REQUIRES_NEW_CLAIM,
            ("U1",),
        ),
    ]


def _artifact_aware_objections() -> list[ReviewerObjection]:
    return [
        ReviewerObjection(
            "A1-SUPPORT-PROVENANCE",
            "artifact-provenance",
            "The load-bearing certificate depends on independently defined support truth. The frozen manuscript does identify released validators/compiler contracts and must preserve that provenance rather than presenting support as model-inferred labels.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("N2", "N3"),
        ),
        ReviewerObjection(
            "A2-BASELINE-STRENGTH",
            "artifact-baseline",
            "The strongest same-information baseline is arbitrary nonnegative package mass using the complete frozen support matrix. This must remain the main reduction; weaker dedup/pruning baselines should not be presented as the decisive comparison.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("N2",),
        ),
        ReviewerObjection(
            "A3-NEGATIVE-CONTROLS",
            "artifact-negative-control",
            "Level-3 and the logical compiler domain are essential because they demonstrate that the certificate does not mechanically fire on disjoint support or high overlap. These controls should remain load-bearing rather than supplementary decoration.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("N3",),
        ),
        ReviewerObjection(
            "A4-SKILLRL-BOUNDARY",
            "artifact-scope",
            "SkillRL supports an independent identity-sensitivity phenotype but does not provide independent support truth for R*. The manuscript should keep it as evidence for N1 and avoid retrofitting it into N2/N3.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("N1",),
        ),
        ReviewerObjection(
            "A5-DYNAMIC-QUALIFICATION",
            "artifact-qualification",
            "The Qwen3 dynamic bank failed its frozen proposer qualification gate. It must remain a transparent non-result and cannot be used to rescue a dynamic-harm story.",
            True,
            ObjectionEvidenceState.REQUIRES_NEW_CLAIM,
            ("U1",),
        ),
    ]


def _has_receipt(row: dict, event_type: str, *, mode: str = "") -> bool:
    for event in row.get("events") or []:
        if event.get("event_type") != event_type:
            continue
        receipt = event.get("receipt") or {}
        if mode and receipt.get("mode") != mode:
            continue
        return True
    return False


def run(root: Path) -> dict:
    row = load_paper_ledger(root, "STRI-ICLR2027")
    if not row:
        raise RuntimeError("STRI-ICLR2027 paper ledger is missing")
    errors = validate_paper_ledger(row)
    if errors:
        raise RuntimeError("STRI ledger invalid before round1: " + "; ".join(errors))
    contract = _contract_from_ledger(row)
    if contract.scientific_status != ScientificPaperStatus.READY:
        raise RuntimeError("STRI is not scientifically READY for paper optimization")

    if row.get("current_state") == PaperState.PAPER_DESIGN.value and not _has_receipt(row, "story-search"):
        row = record_story_search(root, contract, _story_candidates(), actor="stri-paper-round1-story-search")

    row = load_paper_ledger(root, contract.paper_id)
    if row.get("current_state") == PaperState.PAPER_DESIGN.value:
        result = advance_paper_ledger(
            root,
            contract,
            PaperState.MANUSCRIPT,
            actor="stri-paper-round1",
            artifact_refs=contract.evidence_refs,
        )
        if not result["receipt"]["allowed"]:
            raise RuntimeError("Story Search did not unlock MANUSCRIPT: " + ",".join(result["receipt"]["blockers"]))

    row = load_paper_ledger(root, contract.paper_id)
    if row.get("current_state") == PaperState.MANUSCRIPT.value:
        result = advance_paper_ledger(
            root,
            contract,
            PaperState.MOCK_PC,
            actor="stri-paper-round1",
            artifact_refs=contract.evidence_refs,
        )
        if not result["receipt"]["allowed"]:
            raise RuntimeError("MANUSCRIPT did not enter MOCK_PC: " + ",".join(result["receipt"]["blockers"]))

    row = load_paper_ledger(root, contract.paper_id)
    if row.get("current_state") == PaperState.MOCK_PC.value:
        if not _has_receipt(row, "mock-pc-review", mode=MockReviewMode.BLIND_MANUSCRIPT.value):
            row = record_mock_review(root, contract, MockReviewMode.BLIND_MANUSCRIPT, _blind_objections(), actor="stri-paper-round1-blind-review")
        if not _has_receipt(row, "mock-pc-review", mode=MockReviewMode.ARTIFACT_AWARE.value):
            row = record_mock_review(root, contract, MockReviewMode.ARTIFACT_AWARE, _artifact_aware_objections(), actor="stri-paper-round1-artifact-review")

    row = load_paper_ledger(root, contract.paper_id)
    if row.get("current_state") == PaperState.MOCK_PC.value:
        result = advance_paper_ledger(root, contract, PaperState.TARGETED_REPAIR, actor="stri-paper-round1")
        if not result["receipt"]["allowed"]:
            raise RuntimeError("Both Mock PC modes did not unlock TARGETED_REPAIR: " + ",".join(result["receipt"]["blockers"]))
        row = result["ledger"]

    errors = validate_paper_ledger(row)
    if errors:
        raise RuntimeError("STRI ledger invalid after round1: " + "; ".join(errors))
    index = build_paper_ledger_index(root)
    entry = next(item for item in index["entries"] if item["paper_id"] == contract.paper_id)
    return {
        "paper_id": contract.paper_id,
        "current_state": row.get("current_state"),
        "summary": row.get("summary") or {},
        "public_entry": entry,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the first real STRI Story Search + dual-mode Mock PC against the canonical frozen paper contract.")
    parser.add_argument("--root", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory"))
    args = parser.parse_args()
    print(json.dumps(run(args.root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
