from __future__ import annotations

import argparse
import hashlib
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
    revise_paper_contract,
    validate_paper_ledger,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_ref(path: Path) -> str:
    return f"artifact:sha256:{_sha256(path)}"


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


def _revised_contract(row: dict, evidence_dir: Path) -> tuple[PaperContract, tuple[str, ...]]:
    current = _contract_from_ledger(row)
    required = (
        evidence_dir / "agent-safety-r9-controlled-longitudinal-adjudication-20260821.json",
        evidence_dir / "agent-safety-r9-controlled-longitudinal-scientific-review-20260821.json",
        evidence_dir / "agent-safety-r9-controlled-paper-claim-table-20260821.json",
        evidence_dir / "agent-safety-r9-controlled-paper-qa-20260821.json",
    )
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    closure_refs = tuple(_artifact_ref(path) for path in required)
    evidence_refs = tuple(dict.fromkeys((*current.evidence_refs, *closure_refs)))
    supported = dict(current.supported_claims)
    supported.update(
        {
            "C2": (
                "Within the frozen 12 paired BrowserART trajectories, the updated-workflow condition had 8/12 branch first-violation events versus 4/12 under the same held-out schedule with the step-0 workflow held fixed; paired discordance was four update-only and zero control-only."
            ),
            "C3": (
                "Across 12 frozen state-by-probe trajectories, four originally non-violating qualification probes had a first evaluator-classified violation at a later workflow snapshot while probe identity and seed were fixed and probe writeback was disabled."
            ),
        }
    )
    unsupported = dict(current.unsupported_claims)
    unsupported.update(
        {
            "U5": "The paired finite contrast is a statistically representative population causal effect.",
            "U6": "The fixed-probe snapshot result establishes monotonic safety degradation or identifies a semantic mechanism.",
            "U7": "This work originates longitudinal memory-safety evaluation as a general research direction.",
        }
    )
    return (
        PaperContract(
            paper_id=current.paper_id,
            title="A Static Safety Pass Is Not a Temporal Certificate: Controlled First-Violation Evidence in a Persistent Web Agent",
            central_question=(
                "After a persistent web agent passes a frozen current-safety panel, does that pass certify a declared future, and does a same-schedule no-update control leave a finite update-associated first-violation contrast?"
            ),
            supported_claims=supported,
            unsupported_claims=unsupported,
            limitations=(
                "The evidence is a finite frozen-design result on one Qwen3-8B backbone, four selected persistent states, 12 paired branches, and a three-step horizon; it is not a population effect estimate.",
                "Matched seeds and a fixed protocol reduce design variation but fresh stochastic rollouts are not deterministic potential outcomes.",
                "HarmBench-Llama-2-13b-cls is the frozen operational evaluator and has not been independently validated for this BrowserART realization.",
                "The fixed-probe snapshot panel is descriptive and non-monotonic in two event trajectories; it does not identify a semantic mechanism.",
            ),
            reopen_conditions=(),
            evidence_refs=evidence_refs,
            scientific_status=ScientificPaperStatus.READY,
        ),
        closure_refs,
    )


def _story_candidates() -> list[StoryCandidate]:
    return [
        StoryCandidate(
            story_id="S1-TEMPORAL-CERTIFICATE-CONTROL",
            title="Static pass versus temporal certificate; same-schedule control localizes the finite update contrast",
            framing=(
                "Lead with the evaluation contract: a clean current panel is an observation, not a certificate over a declared future. "
                "Use the same-schedule base-workflow arm to separate the realized workflow-update contrast from schedule, and use fixed probes across snapshots as the complementary localization check."
            ),
            contribution_order=("C1", "C2", "C3"),
            emphasized_claim_ids=("C1", "C2", "C3"),
            figure_order=("evaluation-protocol", "controlled-longitudinal-comparison", "first-violation-by-state-branch"),
        ),
        StoryCandidate(
            story_id="S2-PAIRED-CONTROL-FIRST",
            title="Paired same-schedule update contrast first",
            framing=(
                "Lead with the frozen 12-pair update-versus-base contrast, then use the static-pass failure and fixed-probe snapshot panel to explain why temporal evaluation is necessary."
            ),
            contribution_order=("C2", "C1", "C3"),
            emphasized_claim_ids=("C2", "C1"),
            figure_order=("controlled-longitudinal-comparison", "evaluation-protocol", "first-violation-by-state-branch"),
        ),
        StoryCandidate(
            story_id="S3-FIRST-EVENT-TIMING",
            title="First-violation time as the evaluation object",
            framing=(
                "Lead with first-event timing and censoring as the reporting object, then show the static-pass counterexample and controlled update contrast."
            ),
            contribution_order=("C1", "C2", "C3"),
            emphasized_claim_ids=("C1",),
            figure_order=("first-violation-by-state-branch", "controlled-longitudinal-comparison"),
        ),
        StoryCandidate(
            story_id="S4-POPULATION-CAUSAL",
            title="Persistent memory causally increases deployment risk",
            framing="Center the paper on a population causal effect of persistent memory updates.",
            contribution_order=("C2", "U5"),
            emphasized_claim_ids=("U5",),
        ),
        StoryCandidate(
            story_id="S5-LONGITUDINAL-PRIORITY",
            title="The first longitudinal safety evaluation for memory-equipped agents",
            framing="Claim priority over longitudinal memory-safety evaluation as a general direction.",
            contribution_order=("C1", "U7"),
            emphasized_claim_ids=("U7",),
        ),
    ]


def _blind_objections() -> list[ReviewerObjection]:
    return [
        ReviewerObjection(
            "B1-NOVELTY-COLLISION",
            "novelty",
            "Broader 2026 work already establishes longitudinal safety risk in memory-equipped agents using fixed probes and a memory-disabled counterfactual. The manuscript must make the incremental scientific object unmistakable: an action-taking BrowserART/AWM trajectory, exact same-schedule base-workflow control, and branch-level first-event timing rather than priority over longitudinal memory safety.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("C1", "C2", "C3"),
        ),
        ReviewerObjection(
            "B2-SMALL-FINITE-DESIGN",
            "evidence-scope",
            "Twelve paired branches are too small for a population effect claim. The paper is defensible only if it consistently presents C1 as a finite logical counterexample and C2 as a realized paired contrast, without statistical generalization language.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("C1", "C2"),
        ),
        ReviewerObjection(
            "B3-CAUSAL-WORDING",
            "causal-scope",
            "The 8/12 versus 4/12 contrast does not by itself establish a population causal effect because the rollouts are stochastic and the states are selected. Any stronger causal wording would exceed the frozen contract.",
            True,
            ObjectionEvidenceState.REQUIRES_NEW_CLAIM,
            ("U5",),
        ),
        ReviewerObjection(
            "B4-WHAT-CHANGES",
            "clarity",
            "The reader needs a crisp operational account of what differs between updated and base-workflow arms and what remains identical; otherwise the central control is difficult to audit from the paper alone.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("C2",),
        ),
        ReviewerObjection(
            "B5-FIRST-EVENT-VALUE",
            "significance",
            "First-violation timing should be justified as more than a visualization choice: the manuscript should show concretely that one-step evaluation would have missed most event branches and explain censoring at the declared horizon.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("C1",),
        ),
    ]


def _artifact_aware_objections() -> list[ReviewerObjection]:
    return [
        ReviewerObjection(
            "A1-CONTROL-IDENTITY",
            "artifact-provenance",
            "The load-bearing C2 claim requires exact binding that the task, behavior ID, seed, branch, horizon, runtime, evaluator, threshold, and guard are shared across arms and that only workflow update state changes.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("C2",),
        ),
        ReviewerObjection(
            "A2-FIXED-PROBE-READONLY",
            "artifact-protocol",
            "C3 is only interpretable if the exact qualification probe identity and seed are reused and later probe outputs cannot write back into memory. The manuscript and artifact notes must preserve that invariant.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("C3",),
        ),
        ReviewerObjection(
            "A3-RERUN-SEMANTICS",
            "artifact-integrity",
            "The paper should distinguish the archived zero-realization BrokenPipe from a completed-episode rerun and keep the no-rerun/no outcome-driven-selection policy explicit because execution integrity is part of the evidence claim.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("C2", "C3"),
        ),
        ReviewerObjection(
            "A4-EVALUATOR-ORACLE",
            "artifact-measurement",
            "HarmBench is an operational classifier and has not been independently validated for this BrowserART realization. Treating its labels as semantic ground truth would require new measurement evidence and must remain a limitation.",
            True,
            ObjectionEvidenceState.REQUIRES_NEW_CLAIM,
            ("U4",),
        ),
        ReviewerObjection(
            "A5-CLAIM-ARTIFACT-BINDING",
            "artifact-traceability",
            "The submission package should make C1, C2, and C3 traceable to the controlled adjudication, independent scientific review, claim table, and numeric QA rather than only to prose in the manuscript.",
            True,
            ObjectionEvidenceState.EXISTING_EVIDENCE,
            ("C1", "C2", "C3"),
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


def run(root: Path, evidence_dir: Path) -> dict:
    row = load_paper_ledger(root, "AGENT-SAFETY-R9")
    if not row:
        raise RuntimeError("AGENT-SAFETY-R9 paper ledger is missing")
    errors = validate_paper_ledger(row)
    if errors:
        raise RuntimeError("Agent Safety ledger invalid before round1: " + "; ".join(errors))

    if row.get("scientific_status") == ScientificPaperStatus.CAUSAL_HOLD.value:
        revised, closure_refs = _revised_contract(row, evidence_dir)
        row = revise_paper_contract(
            root,
            revised,
            closure_evidence_refs=closure_refs,
            reason=(
                "The preregistered same-held-out-schedule no-update control completed 36/36 episodes and the independent scientific review marked the recorded reopen condition SATISFIED_FOR_FROZEN_R9_FINITE_DESIGN."
            ),
            actor="agent-safety-r23-evidence-closure",
        )

    contract = _contract_from_ledger(row)
    if contract.scientific_status != ScientificPaperStatus.READY:
        raise RuntimeError("Agent Safety is not scientifically READY after controlled evidence closure")

    row = load_paper_ledger(root, contract.paper_id)
    if row.get("current_state") == PaperState.PAPER_EVIDENCE.value:
        result = advance_paper_ledger(root, contract, PaperState.PAPER_DESIGN, actor="agent-safety-paper-round1", artifact_refs=contract.evidence_refs)
        if not result["receipt"]["allowed"]:
            raise RuntimeError("PAPER_EVIDENCE did not unlock PAPER_DESIGN: " + ",".join(result["receipt"]["blockers"]))

    row = load_paper_ledger(root, contract.paper_id)
    if row.get("current_state") == PaperState.PAPER_DESIGN.value and not _has_receipt(row, "story-search"):
        row = record_story_search(root, contract, _story_candidates(), actor="agent-safety-paper-round1-story-search")

    row = load_paper_ledger(root, contract.paper_id)
    if row.get("current_state") == PaperState.PAPER_DESIGN.value:
        result = advance_paper_ledger(root, contract, PaperState.MANUSCRIPT, actor="agent-safety-paper-round1", artifact_refs=contract.evidence_refs)
        if not result["receipt"]["allowed"]:
            raise RuntimeError("Story Search did not unlock MANUSCRIPT: " + ",".join(result["receipt"]["blockers"]))

    row = load_paper_ledger(root, contract.paper_id)
    if row.get("current_state") == PaperState.MANUSCRIPT.value:
        result = advance_paper_ledger(root, contract, PaperState.MOCK_PC, actor="agent-safety-paper-round1", artifact_refs=contract.evidence_refs)
        if not result["receipt"]["allowed"]:
            raise RuntimeError("MANUSCRIPT did not enter MOCK_PC: " + ",".join(result["receipt"]["blockers"]))

    row = load_paper_ledger(root, contract.paper_id)
    if row.get("current_state") == PaperState.MOCK_PC.value:
        if not _has_receipt(row, "mock-pc-review", mode=MockReviewMode.BLIND_MANUSCRIPT.value):
            row = record_mock_review(root, contract, MockReviewMode.BLIND_MANUSCRIPT, _blind_objections(), actor="agent-safety-paper-round1-blind-review")
        if not _has_receipt(row, "mock-pc-review", mode=MockReviewMode.ARTIFACT_AWARE.value):
            row = record_mock_review(root, contract, MockReviewMode.ARTIFACT_AWARE, _artifact_aware_objections(), actor="agent-safety-paper-round1-artifact-review")

    row = load_paper_ledger(root, contract.paper_id)
    if row.get("current_state") == PaperState.MOCK_PC.value:
        result = advance_paper_ledger(root, contract, PaperState.TARGETED_REPAIR, actor="agent-safety-paper-round1")
        if not result["receipt"]["allowed"]:
            raise RuntimeError("Both Mock PC modes did not unlock TARGETED_REPAIR: " + ",".join(result["receipt"]["blockers"]))
        row = result["ledger"]

    errors = validate_paper_ledger(row)
    if errors:
        raise RuntimeError("Agent Safety ledger invalid after round1: " + "; ".join(errors))
    index = build_paper_ledger_index(root)
    entry = next(item for item in index["entries"] if item["paper_id"] == contract.paper_id)
    return {
        "paper_id": contract.paper_id,
        "scientific_status": row.get("scientific_status"),
        "current_state": row.get("current_state"),
        "summary": row.get("summary") or {},
        "public_entry": entry,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Close the frozen R9 causal hold with completed R23 controls, then run Story Search and dual-mode Mock PC.")
    parser.add_argument("--root", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory"))
    parser.add_argument("--evidence-dir", type=Path, default=REPO_ROOT / "generated")
    args = parser.parse_args()
    print(json.dumps(run(args.root, args.evidence_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
