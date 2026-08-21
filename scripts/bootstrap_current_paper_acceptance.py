from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from research_pipeline.config import StorageSettings, resolve_experiment_data_root
from research_pipeline.paper_acceptance import PaperContract, PaperState, ScientificPaperStatus
from research_pipeline.paper_acceptance_ledger import (
    advance_paper_ledger,
    build_paper_ledger_index,
    initialize_paper_ledger,
    load_paper_ledger,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_ref(path: Path) -> str:
    return f"artifact:sha256:{_sha256(path)}"


def _stri_contract(main_tex: Path, body_tex: Path) -> PaperContract:
    return PaperContract(
        paper_id="STRI-ICLR2027",
        title="Self-Evolution Should Not Depend on How Skills Are Split: An Exact Certificate for Skill-Taxonomy Representation Invariance",
        central_question="Should semantically equivalent skill-package representations change a self-evolution control surface?",
        supported_claims={
            "N1": "Released self-evolving skill-system control surfaces can depend on skill-package representation.",
            "N2": "For a frozen finite context-by-package support matrix, R*(A) exactly characterizes package-only additive exposure equalizability.",
            "N3": "In the audited regimes, the STRI residual tracks non-equalizable support geometry rather than overlap prevalence alone.",
        },
        unsupported_claims={
            "U1": "A positive STRI certificate causes downstream task failure or predicts longitudinal utility.",
            "U2": "STRI-Cert is computationally novel relative to linear programming.",
            "U3": "The unqualified Qwen3 dynamic bank or the qualified SkillRL bridge establishes a general downstream dynamic effect.",
        },
        limitations=(
            "The frozen paper claim is primarily a static representation-invariance certificate rather than a downstream utility theorem.",
            "The Qwen3 dynamic pilot failed its preregistered proposer qualification gate and contributes no dynamic scientific update.",
            "The qualified SkillRL fixed-task bridge cannot be upgraded into a population-level no-effect conclusion because no equivalence margin or task-cluster power analysis was preregistered.",
        ),
        evidence_refs=(_artifact_ref(main_tex), _artifact_ref(body_tex)),
        scientific_status=ScientificPaperStatus.READY,
    )


def _agent_safety_contract(claim_table: Path) -> PaperContract:
    return PaperContract(
        paper_id="AGENT-SAFETY-R9",
        title="Future First-Violation Hazard after Persistent State Evolution",
        central_question="Does passing the frozen current-safety panel guarantee absence of future first-violation events under persistent-state evolution?",
        supported_claims={
            "C1": "Within the frozen R9 BrowserART/HarmBench operationalization, passing the three-probe current-safety panel did not guarantee absence of first-violation events over the three-step persistent-update held-out schedule.",
        },
        unsupported_claims={
            "U1": "Experience evolution alone causally produced the observed violations.",
            "U2": "Static safety evaluation is generally ineffective across agents, models, or benchmarks.",
            "U3": "The observed branch event fraction is a population hazard estimate.",
            "U4": "HarmBench labels are a noiseless safety oracle.",
        },
        limitations=(
            "Persistent update and held-out task schedule change together in the frozen design; causal attribution to the update alone remains on HOLD.",
            "Evidence is limited to four selected states, Qwen3-8B, BrowserART, HarmBench, three branches, and a three-update horizon.",
            "The branch event fraction is descriptive; common-random-number branches and the small frozen support set are not treated as IID population draws.",
            "HarmBench is the frozen benchmark evaluator, not a noiseless safety oracle.",
        ),
        reopen_conditions=("Run a preregistered no-update control on the same held-out schedule to separate persistent-update effect from held-out schedule effect.",),
        evidence_refs=(_artifact_ref(claim_table),),
        scientific_status=ScientificPaperStatus.CAUSAL_HOLD,
    )


def _has_transition(row: dict, target: PaperState, blocker: str = "") -> bool:
    for event in row.get("events") or []:
        if event.get("event_type") != "paper-transition" or event.get("to") != target.value:
            continue
        if not blocker or blocker in (event.get("blockers") or []):
            return True
    return False


def bootstrap(root: Path, main_tex: Path, body_tex: Path, claim_table: Path) -> dict:
    for path in (main_tex, body_tex, claim_table):
        if not path.is_file():
            raise FileNotFoundError(path)

    stri = _stri_contract(main_tex, body_tex)
    safety = _agent_safety_contract(claim_table)

    initialize_paper_ledger(root, stri, actor="paper-acceptance-migration")
    stri_row = load_paper_ledger(root, stri.paper_id)
    if stri_row.get("current_state") == PaperState.PAPER_EVIDENCE.value:
        advance_paper_ledger(root, stri, PaperState.PAPER_DESIGN, actor="paper-acceptance-migration")

    initialize_paper_ledger(root, safety, actor="paper-acceptance-migration")
    safety_row = load_paper_ledger(root, safety.paper_id)
    if not _has_transition(safety_row, PaperState.PAPER_DESIGN, "causal-hold"):
        advance_paper_ledger(root, safety, PaperState.PAPER_DESIGN, actor="paper-acceptance-migration")

    return build_paper_ledger_index(root)


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the current STRI and Agent-Safety paper contracts in the append-only Paper Acceptance ledger.")
    parser.add_argument("--root", type=Path, default=None, help="Research experiment-data root; defaults to the configured canonical root.")
    parser.add_argument("--stri-main", type=Path, required=True)
    parser.add_argument("--stri-body", type=Path, required=True)
    parser.add_argument("--agent-safety-claim-table", type=Path, required=True)
    args = parser.parse_args()
    root = args.root or resolve_experiment_data_root(StorageSettings.from_env())
    state = bootstrap(root, args.stri_main, args.stri_body, args.agent_safety_claim_table)
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
