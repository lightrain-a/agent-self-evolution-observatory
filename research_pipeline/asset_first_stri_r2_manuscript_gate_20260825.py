from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "paper_drafts/stri-r2-mechanism-20260825"
MAIN = DRAFT / "main.tex"
BODY = DRAFT / "body.tex"
BIB = DRAFT / "references.bib"
PDF = DRAFT / "main.pdf"
FIG = DRAFT / "figures/stri-r2-mechanism-closure.pdf"
SYNTHESIS = ROOT / "generated/asset-first-stri-r2-paper-design-synthesis-20260825.json"
P0 = ROOT / "generated/asset-first-stri-r2-credit-fragmentation-result-20260825.json"
P1 = ROOT / "generated/asset-first-stri-r2-credit-fragmentation-phase-result-20260825.json"
P2 = ROOT / "generated/asset-first-stri-r2-selection-credit-decomposition-result-20260825.json"
P3 = ROOT / "generated/asset-first-stri-r2-partition-geometry-result-20260825.json"
NOVELTY = ROOT / "generated/asset-first-stri-r2-credit-fragmentation-novelty-reduction-20260825.json"
PREVALENCE = ROOT / "generated/asset-first-stri-r2-natural-prevalence-qualification-20260825.json"
SECOND = ROOT / "generated/asset-first-stri-r2-second-system-credit-partition-20260825.json"
R19_STOP = ROOT / "generated/asset-first-stri-autoskill-multitask-pilot-stage1-20260824.json"
OUTPUT = ROOT / "generated/asset-first-stri-r2-manuscript-gate-20260825.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def page_counts() -> tuple[int, int]:
    info = subprocess.check_output(["pdfinfo", str(PDF)], text=True)
    total = int(re.search(r"^Pages:\s+(\d+)$", info, re.M).group(1))
    # Do not depend on transient LaTeX .aux files. The first post-main section is
    # the AI use statement, so locate that section in the rendered PDF page-by-page.
    post_main_page = None
    for page in range(1, total + 1):
        text = subprocess.check_output(["pdftotext", "-f", str(page), "-l", str(page), str(PDF), "-"], text=True)
        if "AI USE STATEMENT" in text.upper():
            post_main_page = page
            break
    if post_main_page is None:
        raise RuntimeError("could not locate rendered AI use statement")
    return post_main_page - 1, total


def citation_keys(body: str) -> set[str]:
    out: set[str] = set()
    for group in re.findall(r"\\cite[pt]?\{([^}]+)\}", body):
        out.update(x.strip() for x in group.split(",") if x.strip())
    return out


def build() -> dict[str, Any]:
    required = [MAIN, BODY, BIB, PDF, FIG, SYNTHESIS, P0, P1, P2, P3, NOVELTY, PREVALENCE, SECOND, R19_STOP]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    if missing:
        raise RuntimeError("missing R2 draft inputs: " + ", ".join(missing))

    main = MAIN.read_text(encoding="utf-8")
    body = BODY.read_text(encoding="utf-8")
    bib = BIB.read_text(encoding="utf-8")
    p0, p1, p2, p3 = load(P0), load(P1), load(P2), load(P3)
    novelty, prevalence, second, stop = load(NOVELTY), load(PREVALENCE), load(SECOND), load(R19_STOP)
    synthesis = load(SYNTHESIS)
    main_pages, total_pages = page_counts()
    cites = citation_keys(body)
    bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib))

    closure = {
        "phenomenon": all(x in body for x in ("selection duplication", "credit fragmentation", "exact-content copies")),
        "strongest_reduction": all(x in body.lower() for x in ("strategic replication", "action-redundancy", "identity fragmentation", "homomorphism")),
        "stage_local_hidden_state": all(x in body for x in ("persistent sufficient state", "attempt count", "prune\\_easy\\_skills")),
        "mechanism_bottleneck": "partition" in body and "nonlinear lifecycle gate" in body,
        "actionable_variables": all(x in body for x in ("Quotient selection", "Quotient credit")),
        "orthogonal_intervention": "$2\\times2$" in body and "fixing either alone leaves the other" in body,
        "phase_prediction": all(x in body for x in ("M\\le N<kM", "$(k-1)M$", "882", "205 cells", "Partition-dependent tail")),
        "same_information_control": all(x in body for x in ("same eight semantic feedback records", "execute no task selection or retrieval", "semantic feedback hash is identical")),
        "cross_system_boundary": all(x in body for x in ("SkillsVote", "request", "does not replicate Skill-SP's lifecycle phase law")),
        "natural_prevalence_hold": all(x in body for x in ("Natural prevalence remains unresolved", "no evolved library or retired ledger")),
        "behavior_stop": all(x in body for x in ("9/9 units", "8/8 valid", "No repeat-2", "not sufficient for task-general behavioral propagation")),
        "engineering_decision": "every persistent control surface that consumes identity should be audited for quotient consistency" in body,
    }

    evidence = {
        "p0": p0.get("decision") == "PASS_RELEASED_CREDIT_FRAGMENTATION_MECHANISM" and p0.get("pass_gate") is True,
        "p1": p1.get("decision") == "PASS_CREDIT_FRAGMENTATION_PHASE_DIAGRAM" and p1.get("headline", {}).get("analytic_mismatches") == 0 and p1.get("grid", {}).get("cells") == 882,
        "p2": p2.get("decision") == "PASS_TWO_CHANNEL_SELECTION_CREDIT_DECOMPOSITION" and p2.get("pass_gate") is True,
        "p3_partition_geometry": p3.get("decision") == "PASS_ARBITRARY_PARTITION_GEOMETRY" and p3.get("pass_gate") is True and p3.get("headline", {}).get("formula_mismatches") == 0 and p3.get("headline", {}).get("guaranteed_region_failures") == 0,
        "novelty": novelty.get("status") == "SURVIVES_NARROWLY_AS_STAGE_LOCAL_CREDIT_FRAGMENTATION",
        "prevalence_fail_closed": prevalence.get("natural_prevalence_established") is False and prevalence.get("decision") == "HOLD_NATURAL_PREVALENCE_UNRESOLVED_RUNTIME_OUTPUT_NOT_RELEASED",
        "second_system_scoped": second.get("decision") == "QUALIFY_SKILLSVOTE_REQUEST_PARTITION_ANALOGUE_ONLY" and second.get("second_exact_phase_law_replication") is False,
        "r19_behavior_stop": stop.get("decision") == "STOP_EXPANSION_STAGE1_GATE_NOT_MET" and stop.get("stage2_repeat_runs_authorized") is False,
    }

    forbidden_claim_hits = []
    forbidden_patterns = {
        "natural_prevalence_established": r"(common|frequent|prevalent)\s+(in|under)\s+Skill-SP",
        "utility_improvement": r"quotient(?:ing)?[^.]{0,80}(improves?|increases?)\s+(task|downstream)\s+(utility|performance)",
        "task_general_behavior": r"task-general behavioral (effect|propagation) (is|was) (established|shown|demonstrated)",
        "second_phase_law": r"SkillsVote[^.]{0,100}(same|exact|replicates?)\s+(phase law|fragmentation window)",
        "generic_quotient_novelty": r"(new|novel)\s+(quotient|homomorphism|lumpability)\s+(theorem|theory|criterion)",
    }
    for name, pat in forbidden_patterns.items():
        if re.search(pat, body, flags=re.I | re.S):
            forbidden_claim_hits.append(name)

    manuscript = {
        "title_correct": "Representation-Invariant Skill Evolution" in main and "Selection Geometry and Credit Fragmentation" in main,
        "main_pages": main_pages,
        "main_pages_le_9": main_pages <= 9,
        "total_pages": total_pages,
        "figure_present": FIG.is_file(),
        "figure_sha256": sha(FIG),
        "citation_keys": sorted(cites),
        "citation_count": len(cites),
        "all_citations_in_bib": cites.issubset(bib_keys),
        "uncited_new_mechanism_sources_present": all(k in bib_keys for k in ("liu2026rethinkskill", "shin2022replication", "baram2021redundancy", "lin2022identityfragmentation", "ravindran2004approximate")),
        "forbidden_claim_hits": forbidden_claim_hits,
        "r19_canonical_overwritten": False,
    }

    pass_gate = all(closure.values()) and all(evidence.values()) and manuscript["title_correct"] and manuscript["main_pages_le_9"] and manuscript["all_citations_in_bib"] and not forbidden_claim_hits
    result = {
        "schema_version": "1.0",
        "paper_id": "E1.STRI",
        "stage": "R2_PAPER_ONLY_MECHANISM_MANUSCRIPT_GATE",
        "decision": "PASS_R2_MECHANISM_SPINE_DRAFT_KEEP_R19_CANONICAL" if pass_gate else "HOLD_R2_MECHANISM_DRAFT",
        "pass": pass_gate,
        "closure_gate": closure,
        "evidence_binding": evidence,
        "manuscript": manuscript,
        "source_binding": {
            "main_sha256": sha(MAIN),
            "body_sha256": sha(BODY),
            "references_sha256": sha(BIB),
            "pdf_sha256": sha(PDF),
            "storyboard_sha256": sha(DRAFT / "STORYBOARD.md"),
            "synthesis_sha256": sha(SYNTHESIS),
        },
        "paper_design_interpretation": "The R2 draft now closes phenomenon -> reduction -> stage-local mechanism -> exact phase prediction -> orthogonal intervention -> cross-system structural corroboration -> explicit prevalence/behavior boundaries. Complexity is tied to distinct estimands and interventions rather than decorative modules.",
        "promotion_status": "DRAFT_ONLY_DO_NOT_REPLACE_R19",
        "next_gate": "Independent reviewer adjudication plus claim-level post-draft integrity on the R2 draft. Natural prevalence or new outcome-bearing execution remains unauthorized.",
        "claim_expansion": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    canon = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    result["result_canonical_sha256"] = hashlib.sha256(canon).hexdigest()
    return result


def write() -> dict[str, Any]:
    result = build()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(write(), ensure_ascii=False, indent=2))
