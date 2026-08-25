#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from research_pipeline.paper_acceptance import PaperContract, ScientificPaperStatus, paper_contract_digest
from research_pipeline.paper_acceptance_ledger import load_paper_ledger, reopen_ready_paper_contract

PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
EXPECTED_PREVIOUS_CONTRACT_SHA256 = "ff6edaa9d93fe289bb84e74937cece3176329925435de8b0c03649f239623ccb"
REINTERPRETATION_SHA256 = "02e39f14e99eca61bc687890c1bb501e540d87395c6887f39b125538cae570be"
RESULT_ANALYSIS_SHA256 = "aa106470adbe11707ad62d13e698cbe252bf7c7989450d94106c2df086f66c7a"
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory")

OLD_REFS = (
    "artifact:sha256:bdf8eb46bbf708cbdcfe72f69d98a3b6a501618409b543c2b44bc085646040d9",
    "artifact:sha256:31e98c5fb917942d077abb788338f4781cb07f07347e139efa5a266e00d93d50",
    "artifact:sha256:39d0f2182d26f37fcad3fa20afea3fa1324b6b2683506a60da745e88ab290457",
    "artifact:sha256:f2e4f3424faf1e3a9ec7aba7958e538eac457e89308552ef7a9c3d69c6a914f9",
)
NEW_REFS = (
    f"artifact:sha256:{REINTERPRETATION_SHA256}",
    f"artifact:sha256:{RESULT_ANALYSIS_SHA256}",
)


def contract() -> PaperContract:
    return PaperContract(
        paper_id=PAPER_ID,
        title="Memory Divergence Is Not Behavioral Divergence: Stage-Resolved Transport in Self-Improving Agent Memory",
        central_question=(
            "When a reward-conditioned writer changes durable memory on an otherwise identical trajectory, "
            "how far does that state difference survive native retrieval exposure, policy uptake, and terminal outcome?"
        ),
        supported_claims={
            "C1": "The released ReasoningBank implementation routes score one to a success-reflection writer and score zero to a failure-reflection writer for persistent memory construction.",
            "C2": "Under an identical released trajectory, flipping the reward-conditioned memory-writing mode changes persistent memory content in every complete F0 pair.",
            "C3": "The four complete paired memories have mean token-set Jaccard distance 0.734789, with observed range 0.691489 to 0.769953.",
            "C5": "Reward-conditioned persistent-state divergence is not sufficient evidence of behavioral divergence; write, retrieval exposure, policy uptake, and terminal outcome must be evaluated as distinct stages.",
            "C6": "In the frozen Shopping breadth evidence, all 20 complete success/failure writer pairs produce different persistent memories, with pooled token-set Jaccard distance 0.673; on the stronger same-mode wording control, reward-mode distance 0.700 exceeds wording distance 0.595 by 0.105 (exact p=0.0078).",
            "C7": "Under forced fixed-evidence memory exposure, the frozen 4-by-4 source-memory by future-task matrix has mean absolute terminal success difference 0.15625 (100,000-draw permutation p=0.00074); this estimates latent behavioral leverage conditional on supplied exposure, not native end-to-end transport.",
            "C8": "Under native Shopping reuse, branch-specific source memory is retrieved in 125 of 172 held-out retrieval opportunities, while first-action total variation is 0.06944 (p=0.5801; 0/36 modal action changes) and mean absolute terminal success difference is 0.02083 (p=0.4289; 34/36 cells zero).",
            "C9": "In the Reddit replication, 4/4 complete reward-conditioned writes diverge, while native terminal transport is sparse and sign-heterogeneous: mean absolute difference 0.125 (p=0.2253), 6/8 cells zero, and the two nonzero cells have opposite signs.",
        },
        unsupported_claims={
            "U1": "Persistent-memory divergence by itself proves downstream behavioral propagation.",
            "U2": "The forced fixed-evidence terminal effect is an estimate of native end-to-end memory transport.",
            "U3": "Reward-conditioned memory produces a universal directional harm or a universal attenuation constant across tasks, domains, writers, or agents.",
            "U4": "The current evidence certifies atom-level causal semantics for every branch-specific memory sentence.",
            "U5": "The stopped CBRG extension has demonstrated a positive or negative behavioral method effect.",
        },
        limitations=(
            "The paired writer intervention identifies an operational success-versus-failure branch contrast. The frozen pool lacks explicit decoding-seed binding and same-condition same-trajectory noise-floor replication for atom-level causal-purity claims.",
            "Forced fixed-evidence injection mechanically supplies memory exposure and therefore measures latent leverage rather than native end-to-end transport.",
            "Native Shopping branch-specific first-action and terminal contrasts are sparse and do not pass their primary statistical gates; the result localizes attenuation rather than a universal directional effect.",
            "Reddit provides a second-domain write/transport replication but remains small and sign-heterogeneous; cross-writer, cross-model, and broader task-family generalization remain open.",
            "Source-faithful live WebArena browser navigation is unavailable in the released environment; native measurements use the frozen supported pathway rather than a newly reconstructed live endpoint.",
            "The CBRG method extension stopped at method realization because no independently qualified outcome-independent semantic-validity adjudicator was available. No behavioral CBRG method-effect experiment was authorized.",
            "The two initial failure-label provider responses that terminated before assistant text remain excluded from paired text estimands and preserved as support debt rather than negative examples.",
        ),
        reopen_conditions=(
            "A method-extension reopen requires a new content-addressed outcome-independent validity adjudicator, an independent task-specific pre-outcome qualification receipt, same-information non-reducibility, and fresh collision clearance.",
            "A broader behavioral-generalization claim requires new frozen cross-writer or cross-domain native transport evidence with the same stage-resolved estimands.",
        ),
        evidence_refs=OLD_REFS + NEW_REFS,
        scientific_status=ScientificPaperStatus.READY,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    row = load_paper_ledger(args.root, PAPER_ID)
    if not row:
        raise SystemExit("canonical C1 paper ledger is missing")
    current_sha = str(row.get("contract_sha256") or "")
    current_state = str(row.get("current_state") or "")
    current_status = str(row.get("scientific_status") or "")

    revised = contract()
    revised_sha = paper_contract_digest(revised)
    if current_sha == revised_sha:
        print(json.dumps({"status": "ALREADY_REOPENED", "contract_sha256": revised_sha, "current_state": current_state}, indent=2))
        return
    if current_sha != EXPECTED_PREVIOUS_CONTRACT_SHA256:
        raise SystemExit(f"unexpected current contract digest: {current_sha}")
    if current_state != "SUBMISSION_READY" or current_status != "READY":
        raise SystemExit(f"unexpected current paper state/status: {current_state}/{current_status}")

    previous = row.get("contract") or {}
    previous_refs = tuple(str(x) for x in previous.get("evidence_refs") or [])
    if previous_refs != OLD_REFS:
        raise SystemExit("previous evidence reference set/order drift")
    previous_claims = previous.get("supported_claims") or {}
    if str(previous_claims.get("C5") or "") != "Reward reliability is a state-consistency requirement for agents that write persistent memory from terminal outcomes.":
        raise SystemExit("previous C5 drift")

    preview = {
        "status": "READY_TO_APPLY_SCIENTIFIC_REOPEN" if not args.apply else "APPLYING_SCIENTIFIC_REOPEN",
        "paper_id": PAPER_ID,
        "previous_contract_sha256": current_sha,
        "revised_contract_sha256": revised_sha,
        "previous_state": current_state,
        "state_after_apply": "PAPER_EVIDENCE",
        "superseded_claims": ["C5"],
        "new_evidence_refs": list(NEW_REFS),
    }
    print(json.dumps(preview, indent=2))
    if not args.apply:
        return

    updated = reopen_ready_paper_contract(
        args.root,
        revised,
        reopen_evidence_refs=NEW_REFS,
        superseded_claims={
            "C5": (
                "Later frozen native Shopping/Reddit evidence shows that durable branch-specific state can be robustly written and even have forced leverage while native first-action and terminal transport remain sparse and unresolved. The previous state-consistency requirement conflated persistent-state divergence with behavioral authority and is superseded by the stage-resolved evaluation claim."
            )
        },
        reason=(
            "Reopen C1 after terminal-result analysis separated forced fixed-evidence leverage from native memory transport. "
            "The new frozen evidence narrows the paper from a variance-amplification/propagation story to stage-resolved identification and measurement."
        ),
        actor="c1-stage-resolved-evidence-reinterpretation-20260825",
    )
    print(json.dumps({
        "status": "SCIENTIFIC_REOPEN_APPLIED",
        "paper_id": PAPER_ID,
        "contract_sha256": updated.get("contract_sha256"),
        "current_state": updated.get("current_state"),
        "scientific_status": updated.get("scientific_status"),
        "events": len(updated.get("events") or []),
        "latest_event": (updated.get("events") or [])[-1].get("event_type"),
    }, indent=2))


if __name__ == "__main__":
    main()
