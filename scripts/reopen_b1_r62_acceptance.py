from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from research_pipeline.paper_acceptance import PaperContract, ScientificPaperStatus, paper_contract_digest
from research_pipeline.paper_acceptance_ledger import (
    load_paper_ledger,
    public_paper_ledger_summary,
    reopen_ready_paper_contract,
    validate_paper_ledger,
)

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
EXPECTED_PRE_R62_CONTRACT_SHA256 = "582a203818f9f590d601b5ea9d3a3ecdc08acb3e34d3b1d9f190e17a2d1dcc25"

EVIDENCE_FILES = {
    "qwen_utilization": (
        "generated/d2-failure-memory-provenance-r55-qwen-utilization-result.json",
        "261a99e3830983f1676bda6d8a199dec1b34e24331d0060f94421c93c7059bd0",
    ),
    "qwen_ab": (
        "generated/d2-failure-memory-provenance-r56-qwen-ab-identification-result.json",
        "1b631575d78eeb0beb7c38669ea01611a0ed165e0ea0109e8b0289dbc1ada0f1",
    ),
    "llama_utilization": (
        "generated/d2-failure-memory-provenance-r60-llama-utilization-result.json",
        "0828f39f2491872feaf7e6e905d17cb6f0a015290b9e503421c25416f155690c",
    ),
    "llama_ab": (
        "generated/d2-failure-memory-provenance-r61-llama-ab-identification-result.json",
        "4c22f9ee7e59c5f75b8a4ccb211300719d13e2dc4d1ac52592ab570a273cbbca",
    ),
    "cross_backbone_adjudication": (
        "generated/d2-failure-memory-provenance-r62-cross-backbone-l2-adjudication.json",
        "67c1848831c93839697262c0626ee0c107c4643f7f94d440ad34fa7f41b6c572",
    ),
    "manuscript_release": (
        "generated/d2-failure-memory-provenance-r62-manuscript-release.json",
        "7e2ef5cee2fe9afda8902a59aa87eebd1d293b20cbfa2f032acd1318fbc18216",
    ),
}

OLD_C1 = (
    "Success-derived ReasoningBank retrievals achieve 0.931 accuracy over 101 cases while "
    "failure-derived retrievals achieve 0.647 over 34 cases in the released financial-agent audit."
)
OLD_C2 = "All ten reported ReasoningBank W->W persistent failures lie in the failure-derived retrieval stratum."
OLD_C3 = (
    "ReasoningBank writes successful and failed trajectories through outcome-conditioned reflection modes, "
    "making trajectory provenance an upstream intervention on persistent memory content."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_ref(hex_digest: str) -> str:
    return f"artifact:sha256:{hex_digest}"


def verified_new_refs(project_root: Path) -> tuple[str, ...]:
    refs: list[str] = []
    for name, (relative, expected) in EVIDENCE_FILES.items():
        path = project_root / relative
        if not path.is_file():
            raise RuntimeError(f"missing R62 evidence file:{name}:{path}")
        observed = sha256(path)
        if observed != expected:
            raise RuntimeError(f"R62 evidence hash drift:{name}:{observed}!={expected}")
        refs.append(artifact_ref(observed))
    return tuple(refs)


def revised_contract(previous: dict, new_refs: tuple[str, ...]) -> PaperContract:
    previous_refs = tuple(str(ref) for ref in previous.get("evidence_refs") or [] if str(ref))
    if (previous.get("supported_claims") or {}).get("C1") != OLD_C1:
        raise RuntimeError("pre-R62 C1 drift")
    if (previous.get("supported_claims") or {}).get("C2") != OLD_C2:
        raise RuntimeError("pre-R62 C2 drift")
    if (previous.get("supported_claims") or {}).get("C3") != OLD_C3:
        raise RuntimeError("pre-R62 C3 drift")
    evidence_refs = tuple(dict.fromkeys((*previous_refs, *new_refs)))
    return PaperContract(
        paper_id=PAPER_ID,
        title="Does Memory Provenance Matter? Exact-Information Swaps Show Low Terminal Value Beyond Content",
        central_question=(
            "Conditional on fixed actionable memory content, retrieval support, and target context, does truthful "
            "source-outcome provenance add terminal utility to an executor, and does that incremental value replicate "
            "across executor backbones?"
        ),
        supported_claims={
            "C1": OLD_C1,
            "C2": OLD_C2,
            "C3": (
                "ReasoningBank uses distinct success- and failure-conditioned writer modes; changing those writers is an "
                "L1 writer-mode bundle intervention and cannot by itself identify the L2 incremental value of provenance "
                "information when actionable memory content differs."
            ),
            "C4": (
                "In a prospective support-qualified MemRL/OSInteraction L2 experiment with Qwen2.5-7B-Instruct, "
                "byte-identical actionable content plus truthful provenance changes terminal success by +0.03125 versus "
                "content only (15/32 versus 16/32, exact paired p=1.0, preregistered bootstrap 95% CI [0,0.09375]); "
                "the prespecified |Delta|>=0.15 terminal relevance floor is not met."
            ),
            "C5": (
                "On the exact same frozen source bank, retrieval/content/order, 32 primary clusters, renderer, endpoint, "
                "and analysis, Meta-Llama-3.1-8B-Instruct gives an L2 terminal effect of 0 with two B-only and two A-only "
                "successes (exact paired p=1.0, bootstrap 95% CI [-0.125,0.125]); its independent memory-utilization gate "
                "passes with 8/8 memory-specific versus 5/8 placebo first-action divergences."
            ),
            "C6": (
                "Without pooling model-specific estimates, both Qwen2.5-7B-Instruct and Meta-Llama-3.1-8B-Instruct remain "
                "below the preregistered 0.15 terminal relevance floor on the same exact-information MemRL/OSInteraction "
                "surface, supporting a bounded two-backbone low-terminal-value/content-sufficiency regime rather than a "
                "universal zero-effect conclusion."
            ),
        },
        unsupported_claims={
            "U1": "Failure-derived provenance universally causes future error across agents and domains.",
            "U2": "Provenance-aware governance or PSMG has already been shown to improve downstream performance.",
            "U3": "The fresh Qwen or Llama result proves that provenance has exactly zero effect or never matters.",
            "U4": "The two executor-specific estimates may be pooled post hoc into one cross-model causal estimate.",
            "U5": "Historical L1 writer-mode contrasts identify the L2 provenance-only effect.",
            "U6": "The MemRL/OSInteraction experiments complete source-faithful L3 transport to the motivating financial ReasoningBank runtime.",
        },
        limitations=(
            "The fresh L2 evidence uses one frozen MemRL/OSInteraction source bank and two executor backbones; it is not a population theorem over models, tasks, or memory systems.",
            "The Qwen and Llama confidence intervals are model-specific finite-sample intervals and are not pooled or interpreted as universal effect bounds.",
            "Historical R4/R6 L1 experiments manipulate outcome-conditioned writer modes and therefore remain writer-bundle evidence rather than provenance-only identification.",
            "The motivating financial audit still lacks the per-query artifacts and exact runtime bindings required for source-faithful L3 transport.",
            "PSMG efficacy remains untested because the completed L2 experiments expose provenance to the executor rather than comparing a provenance-sensitive governor with a strongest same-information provenance-free controller.",
        ),
        reopen_conditions=(
            "Reopen L3 transport claims only after a source-faithful financial ReasoningBank runtime and per-query artifacts are content-addressed and prospectively executed.",
            "Reopen PSMG efficacy only after the provenance-sensitive governor, strongest same-information provenance-free comparator, calibration data, thresholds, and action mapping are frozen before target outcomes.",
            "Reopen a broader cross-system generalization claim only with a separately preregistered independent memory substrate rather than additional outcome-driven reruns of the current surface.",
        ),
        evidence_refs=evidence_refs,
        scientific_status=ScientificPaperStatus.READY,
    )


def execute(root: Path, project_root: Path) -> dict:
    current = load_paper_ledger(root, PAPER_ID)
    if not current:
        raise RuntimeError(f"missing canonical paper ledger:{PAPER_ID}")
    new_refs = verified_new_refs(project_root)
    revised = revised_contract(current.get("contract") or {}, new_refs)
    revised_digest = paper_contract_digest(revised)
    if current.get("contract_sha256") == revised_digest:
        errors = validate_paper_ledger(current)
        if errors:
            raise RuntimeError("already-reopened ledger is invalid:" + ";".join(errors))
        return {"already_reopened": True, "row": current, "public": public_paper_ledger_summary(current)}
    if current.get("contract_sha256") != EXPECTED_PRE_R62_CONTRACT_SHA256:
        raise RuntimeError(f"unexpected pre-R62 contract digest:{current.get('contract_sha256')}")
    if current.get("current_state") != "SUBMISSION_READY" or current.get("scientific_status") != "READY":
        raise RuntimeError("R62 reopen requires the expected unsubmitted READY/SUBMISSION_READY pre-R62 state")
    row = reopen_ready_paper_contract(
        root,
        revised,
        reopen_evidence_refs=new_refs,
        superseded_claims={
            "C3": (
                "R62 separates the outcome-conditioned L1 writer intervention from the exact-information L2 provenance-"
                "exposure estimand. The historical writer fact remains relevant, but it no longer supports an undifferentiated "
                "causal provenance-effect interpretation."
            )
        },
        reason=(
            "Prospective full350 exact-information evidence now executes the previously missing L2 object on Qwen and an "
            "executor-only Llama replication. Both model-specific terminal effects remain below the frozen 0.15 relevance "
            "floor, so the former causal-provenance framing must be narrowed and all paper gates re-audited under the R62 contract."
        ),
        actor="b1-r62-scientific-reopen",
    )
    errors = validate_paper_ledger(row)
    if errors:
        raise RuntimeError("R62 reopened ledger validation failed:" + ";".join(errors))
    public = public_paper_ledger_summary(row)
    if public.get("title") != revised.title or public.get("current_state") != "PAPER_EVIDENCE":
        raise RuntimeError("R62 public projection failed to reset title/state")
    if public.get("gate_clean_submission_ready") is not False:
        raise RuntimeError("R62 scientific reopen must invalidate stale submission readiness")
    return {"already_reopened": False, "row": row, "public": public}


def dry_run(canonical_root: Path, project_root: Path) -> dict:
    source = canonical_root / "paper-acceptance" / f"{PAPER_ID}.json"
    if not source.is_file():
        raise FileNotFoundError(source)
    with tempfile.TemporaryDirectory(prefix="b1-r62-ledger-dryrun-") as td:
        root = Path(td)
        target_dir = root / "paper-acceptance"
        target_dir.mkdir(parents=True)
        shutil.copy2(source, target_dir / source.name)
        result = execute(root, project_root)
        public = result["public"]
        return {
            "dry_run": True,
            "already_reopened": result["already_reopened"],
            "contract_sha256": result["row"]["contract_sha256"],
            "current_state": result["row"]["current_state"],
            "scientific_status": result["row"]["scientific_status"],
            "scientific_reopens": (result["row"].get("summary") or {}).get("scientific_reopens"),
            "public_title": public.get("title"),
            "gate_clean_submission_ready": public.get("gate_clean_submission_ready"),
            "primary_next_action": public.get("primary_next_action"),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed B1 R62 scientific reopen of the canonical Paper Acceptance contract.")
    parser.add_argument("--root", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory"))
    parser.add_argument("--project-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = dry_run(args.root, args.project_root) if args.dry_run else execute(args.root, args.project_root)
    if args.dry_run:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    row = result["row"]
    public = result["public"]
    print(json.dumps({
        "paper_id": PAPER_ID,
        "already_reopened": result["already_reopened"],
        "contract_sha256": row["contract_sha256"],
        "current_state": row["current_state"],
        "scientific_status": row["scientific_status"],
        "scientific_reopens": (row.get("summary") or {}).get("scientific_reopens"),
        "public_title": public.get("title"),
        "gate_clean_submission_ready": public.get("gate_clean_submission_ready"),
        "primary_next_action": public.get("primary_next_action"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
