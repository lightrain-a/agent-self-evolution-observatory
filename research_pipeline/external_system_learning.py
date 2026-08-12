from __future__ import annotations

from collections import Counter
from typing import Any


POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "external_design_requires_primary_or_official_source": True,
    "component_name_similarity_is_not_adoption_evidence": True,
    "every_candidate_design_requires_local_gap_test": True,
    "redundant_designs_merge_into_existing_component": True,
    "adoption_requires_named_failure_mode_and_machine_check": True,
    "external_system_never_overrides_local_scientific_authority": True,
}

SYSTEM_DESIGNS = [
    {"system": "Qiushi Discovery Engine", "design": "Meta-Trace + nonlinear research phases", "gap": "long raw traces can outgrow coherent scientific state", "local_mapping": "scientific_meta_trace", "status": "adopted"},
    {"system": "Kosmos", "design": "structured world model shared between literature and analysis agents; statement-level code/literature provenance", "gap": "literature and experiment evidence can fragment into separate contexts", "local_mapping": "scientific_meta_trace + evidence provenance", "status": "adopted"},
    {"system": "MLEvolve", "design": "cross-branch reference edges + retrospective memory + progressive exploration/exploitation", "gap": "branch isolation and greedy local optimization", "local_mapping": "meta-trace + value scheduler + failure assets", "status": "adopted"},
    {"system": "InternAgent-1.5", "design": "generation / verification / evolution subsystems plus reproduction mode", "gap": "new ideas can outrun independent verification", "local_mapping": "principle/evidence gates + replay benchmark", "status": "merged-existing"},
    {"system": "BioMedAgent / Biomni", "design": "declarative tool metadata, tool-aware routing, and reusable workflow memory", "gap": "tool choice can be implicit and hard to audit", "local_mapping": "research capability registry", "status": "adopted"},
    {"system": "AutoResearchClaw", "design": "failure-to-safeguard cross-run learning + verified result registry + targeted HITL", "gap": "failures may be repaired once but not become reusable launch constraints", "local_mapping": "failure assets + protocol validity + AI clinic", "status": "adopted"},
    {"system": "ResearchClawBench", "design": "protocol mismatch / evidence mismatch / missing scientific core as separate error classes", "gap": "method quality can be confounded with invalid research protocol", "local_mapping": "protocol validity + replay benchmark", "status": "adopted"},
    {"system": "HackDetect", "design": "audit benchmark exposure, shortcut use, and score inflation", "gap": "agent may succeed through evaluator leakage or unintended shortcuts", "local_mapping": "protocol validity", "status": "adopted"},
    {"system": "ScienceAgentBench verified split", "design": "verify evaluation artifacts to reduce benchmark false negatives", "gap": "evaluation bugs can masquerade as agent/method failure", "local_mapping": "protocol validity + replay benchmark", "status": "adopted"},
    {"system": "AutoResearchBench", "design": "separate deep target-finding from wide comprehensive literature discovery", "gap": "literature retrieval quality is not one scalar capability", "local_mapping": "literature retrieval audit", "status": "adopted"},
    {"system": "PaperQA2", "design": "separate paper search, evidence gathering, and answer synthesis with grounded citations and redundant metadata", "gap": "retrieval and synthesis can collapse into one opaque step", "local_mapping": "literature retrieval audit + capability registry", "status": "adopted"},
    {"system": "SciNetBench", "design": "ego/pair/path relation-aware scientific retrieval", "gap": "content-similarity retrieval misses support, conflict, and lineage structure", "local_mapping": "literature relation-aware audit", "status": "adopted"},
    {"system": "SciRet", "design": "compute-aware retriever/reranker comparison with domain-mismatch qualification", "gap": "stronger rerankers can be worse on scientific domains", "local_mapping": "retrieval qualification contract", "status": "adopted"},
    {"system": "Citation Faithfulness Audit", "design": "calibrate the citation verifier itself against human gold", "gap": "citation failure rates can move when only the verifier changes", "local_mapping": "citation verifier contract", "status": "adopted"},
    {"system": "ScientistOne", "design": "claim-type-specific Chain-of-Evidence audit for numeric, citation, and method claims", "gap": "professional-looking reports can diverge from logs, sources, or implementation", "local_mapping": "claim-evidence routing", "status": "adopted"},
    {"system": "SAGE", "design": "co-design subqueries and retrievers for reasoning-intensive scientific search", "gap": "keyword-oriented agent subqueries can nullify sophisticated retrievers", "local_mapping": "capability-registry retrieval router + simple-first retriever promotion gate", "status": "adopted"},
    {"system": "ReplicationBench", "design": "paper-scale author-validated replication tasks", "gap": "component-level replay does not yet test full paper replication fidelity", "local_mapping": "research-system replay paper-scale reproduction contract", "status": "adopted"},
    {"system": "SCION", "design": "Research Execution Plan compiles scientific intent into objectives, dependencies, checkpoints, tool requirements, artifacts, and fallbacks", "gap": "a scientifically sound principle can still reach runtime as an underspecified execution request", "local_mapping": "derived Research Execution Plan in Pre-Experiment Compiler", "status": "adopted"},
    {"system": "AutoSci", "design": "separate Active Research Memory from Long-Term Knowledge Memory and version memory/workflow evolution", "gap": "current-project truth and reusable cross-project lessons can otherwise contaminate each other", "local_mapping": "Scientific Meta-Trace memory scopes + institutional Failure Assets", "status": "adopted"},
    {"system": "EvoScientist", "design": "separate ideation and experimentation memory with explicit evolution over repeated research cycles", "gap": "historical lessons need scope and reuse-effectiveness tracking rather than permanent authority", "local_mapping": "institutional memory lifecycle metadata", "status": "merged-existing"},
    {"system": "Agent Operating System (AOS)", "design": "separate Control & Governance Plane from Runtime & Coordination Plane", "gap": "policy and authority decisions should not become implicit side effects of runtime routing", "local_mapping": "existing scientific-control vs research-runtime architecture", "status": "merged-existing"},
    {"system": "Exploration-breadth studies / IDEAgent / Heuresis / SwarmResearch", "design": "measure and actively preserve quality-diversity-novelty breadth across a portfolio rather than optimizing isolated ideas", "gap": "pairwise collision checks do not detect portfolio-wide collapse toward seed literature or one high-level approach", "local_mapping": "cross-cutting exploration-frontier control owned by wide-search ideation", "status": "adopted"},
    {"system": "Agent-experiment preregistration / stochastic experimental design / Search-Time Contamination", "design": "freeze researcher degrees of freedom before outcomes, plan repeated runs for stochastic agents, and audit web/tool access for benchmark metadata, question-context, and answer leakage", "gap": "cheap adaptive iteration and open-web retrieval can silently turn confirmatory experiments into outcome-contingent or contaminated analyses", "local_mapping": "cross-cutting experimental-design-integrity control owned by protocol-and-replay", "status": "adopted"},
    {"system": "ARA / Artisan / ArtifactCopilot", "design": "reconstruct dependency-aware scientific workflows and require independent re-execution rather than treating trace presence as reproducibility", "gap": "claim provenance can be correct while the result-generating workflow remains impossible for a third party to reconstruct and rerun", "local_mapping": "cross-cutting reproducibility-readiness control owned by Evidence Integrity", "status": "adopted"},
    {"system": "EurekAgent", "design": "permissions, artifact, budget, and human-in-the-loop environment engineering", "gap": "agent behavior can be shaped more reliably by environment constraints than by another prompt-level workflow", "local_mapping": "existing Runtime & Authority layer: capability permissions + artifact persistence + budget watchdog + human scientific authority", "status": "merged-existing"},
]


def build_external_system_learning_state() -> dict[str, Any]:
    counts = Counter(str(row["status"]) for row in SYSTEM_DESIGNS)
    return {
        "schema_version": "1.0",
        "policy": POLICY,
        "summary": {
            "systems_reviewed": len(SYSTEM_DESIGNS),
            "adopted": counts.get("adopted", 0),
            "merged_existing": counts.get("merged-existing", 0),
            "next_backlog": counts.get("next", 0),
        },
        "designs": SYSTEM_DESIGNS,
        "next_backlog": [row for row in SYSTEM_DESIGNS if row["status"] == "next"],
    }
