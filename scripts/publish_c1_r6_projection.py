#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.paper_acceptance_ledger import build_paper_ledger_index, build_portable_paper_ledger_index, load_paper_ledger
from research_pipeline.research_memory_wiki import (
    _annotate_certainty,
    _review_lessons,
    _sha,
    audit_certainty_typing,
    compile_research_memory_query_pack,
    lint_research_memory_wiki,
    write_research_memory_wiki,
)

PID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
EXPECTED_CONTRACT = "c6cd6e451dd5a7a610ef89f7b2e4ce3e54a70fb568889c6304c33e66dc50bd0e"
EXPECTED_AUDIT = "715721a221a2bfb942fffa43c65aba52f1754ce3d1f99006f13bc32ef4b6e332"
EXPECTED_LESSON_CODES = {
    "bundled-writer-intervention-not-atom-pure",
    "claim-audit-needs-replayable-content-addressed-provenance",
    "measurement-boundary-coarsening-test",
    "method-extension-stop-does-not-negate-measurement-result",
    "operational-localization-not-causal-onset",
    "scope-stage-boundary-to-measured-substrate",
    "stopped-method-no-behavioral-efficacy",
}
GEN = ROOT / "generated"
MEM_DIR = ROOT / "paper_drafts" / "c1-manuscript-strengthening-20260825"
RETRIEVAL = MEM_DIR / "c1-r6-review-memory-retrieval-20260828.json"
RETRIEVAL_SHA = RETRIEVAL.with_suffix(RETRIEVAL.suffix + ".sha256")


def load(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected object: {path}")
    return payload


def write_pair(name: str, variable: str, payload: dict) -> None:
    (GEN / f"{name}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (GEN / f"{name}.js").write_text(f"window.{variable} = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


def stable_bytes(payload: dict) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish only the C1 R6 paper-ledger and Review Lesson projection without sweeping concurrent paper updates")
    parser.add_argument("--data-root", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory"))
    args = parser.parse_args()

    live_index = build_paper_ledger_index(args.data_root)
    if int((live_index.get("summary") or {}).get("invalid_ledgers") or 0) != 0:
        raise RuntimeError("live paper ledger index is invalid")
    live = next((row for row in live_index.get("entries") or [] if row.get("paper_id") == PID), None)
    if not isinstance(live, dict):
        raise RuntimeError("live C1 paper row missing")
    if live.get("contract_sha256") != EXPECTED_CONTRACT:
        raise RuntimeError("live C1 contract drift")
    latest_audit = live.get("latest_claim_audit") or {}
    if latest_audit.get("pass") is not True or latest_audit.get("claim_audit_sha256") != EXPECTED_AUDIT or int(latest_audit.get("passed") or 0) != 35 or int(latest_audit.get("checks") or 0) != 35:
        raise RuntimeError("live C1 claim audit is not the provenance-hardened 35/35 R6 audit")
    learning = live.get("review_learning") or {}
    if set(learning.get("lesson_codes") or []) != EXPECTED_LESSON_CODES or int(learning.get("structured_lesson_receipts") or 0) < 1:
        raise RuntimeError("live C1 structured review lesson is incomplete")

    raw_ledger = load_paper_ledger(args.data_root, PID)
    projected_at = str(raw_ledger.get("updated_at") or "")
    if not projected_at:
        raise RuntimeError("live C1 ledger has no updated_at")

    registry = load(GEN / "paper-registry.json")
    rows = list(registry.get("papers") or [])
    base = next((row for row in rows if row.get("paper_id") == PID), None)
    if not isinstance(base, dict):
        raise RuntimeError("published C1 PaperRegistry row missing")
    candidate = dict(base)
    candidate.update(live)
    candidate["paper_stage"] = str(live.get("current_state") or candidate.get("paper_stage") or "")
    candidate["submission_status"] = candidate["paper_stage"]
    candidate["acceptance_paper_id"] = PID
    rows = [candidate if row.get("paper_id") == PID else row for row in rows]
    registry["papers"] = rows
    registry["generated_at"] = projected_at
    write_pair("paper-registry", "PAPER_REGISTRY", registry)

    portable = build_portable_paper_ledger_index(registry)
    if int((portable.get("summary") or {}).get("invalid_ledgers") or 0) != 0:
        raise RuntimeError("focused PaperRegistry no longer satisfies portable ledger invariants")
    new_lesson = next((row for row in _review_lessons(portable) if row.get("candidate_id") == PID), None)
    if not isinstance(new_lesson, dict):
        raise RuntimeError("C1 Review Lesson did not compile from focused PaperRegistry")
    new_lesson = _annotate_certainty(new_lesson)
    if set((new_lesson.get("review_learning") or {}).get("lesson_codes") or []) != EXPECTED_LESSON_CODES:
        raise RuntimeError("C1 Review Lesson lost structured lesson codes")

    wiki = load(GEN / "research-memory-wiki.json")
    entries = [row for row in wiki.get("entries") or [] if not (isinstance(row, dict) and row.get("kind") == "REVIEW_LESSON" and row.get("candidate_id") == PID)]
    entries.append(new_lesson)
    entries = sorted(entries, key=lambda row: (str(row.get("kind") or ""), str(row.get("memory_id") or "")))
    wiki["entries"] = entries
    wiki["generated_at"] = projected_at
    wiki["wiki_sha256"] = _sha({
        "schema_version": wiki.get("schema_version"),
        "policy": wiki.get("policy"),
        "lesson_templates": wiki.get("lesson_templates"),
        "source_manifest": wiki.get("source_manifest"),
        "entries": entries,
    })
    wiki["lint"] = lint_research_memory_wiki(wiki)
    wiki["certainty_audit"] = audit_certainty_typing(wiki, 30)
    wiki["status"] = "MEMORY_COMPILED" if wiki["lint"]["status"] == "PASS" and wiki["certainty_audit"]["status"] == "PASS" else "MEMORY_INVALID"
    if wiki["status"] != "MEMORY_COMPILED":
        raise RuntimeError(f"focused Research Memory projection invalid: {wiki['lint']}")
    write_research_memory_wiki(wiki)

    system = load(GEN / "research-system-state.json")
    paper_acceptance = system.get("paper_acceptance") or {}
    embedded_index = paper_acceptance.get("ledger_index") or {}
    embedded_rows = list(embedded_index.get("entries") or [])
    portable_c1 = next((row for row in portable.get("entries") or [] if row.get("paper_id") == PID), None)
    if not isinstance(portable_c1, dict):
        raise RuntimeError("focused portable C1 ledger row missing")
    embedded_rows = [portable_c1 if row.get("paper_id") == PID else row for row in embedded_rows]
    embedded_index["entries"] = embedded_rows
    embedded_index["summary"] = portable.get("summary") or embedded_index.get("summary") or {}
    paper_acceptance["ledger_index"] = embedded_index
    paper_acceptance["control_plane_reconciled_at"] = projected_at
    system["paper_acceptance"] = paper_acceptance
    system["research_memory_wiki"] = wiki
    (GEN / "research-system-state.json").write_text(json.dumps(system, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (GEN / "research-system-state.js").write_text("window.RESEARCH_SYSTEM_STATE = " + json.dumps(system, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

    query = compile_research_memory_query_pack(
        wiki,
        purpose="PAPER_DESIGN",
        context=(
            "C1 stage resolved measurement exposure uptake separation load bearing coarsening operational localization causal onset "
            "bundled writer reward semantics Shopping Reddit scope CBRG stopped method behavioral efficacy claim audit replayable content addressed provenance"
        ),
        max_chars=7000,
        max_items=18,
    )
    c1_id = str(new_lesson.get("memory_id") or "")
    if c1_id not in query.get("selected_memory_ids", []):
        raise RuntimeError("C1 Review Lesson was not retrieved by the R6 paper-design query")
    text = str(query.get("text") or "")
    required_phrases = (
        "merging adjacent measurements destroys diagnostic resolution",
        "does not identify why attenuation occurs",
        "content-addressed objects are mechanically verified",
    )
    lesson_text = str(new_lesson.get("summary") or "") + " " + str(new_lesson.get("reusable_precheck") or "")
    full_lesson_phrases = required_phrases + ("reward bit alone",)
    if not all(phrase in lesson_text for phrase in full_lesson_phrases):
        raise RuntimeError("compiled C1 Review Lesson lost one or more load-bearing R6 prechecks")
    if not all(phrase in text for phrase in required_phrases):
        raise RuntimeError("retrieved C1 Review Lesson did not expose the prioritized localization/provenance prechecks within the bounded query pack")

    receipt = {
        "schema_version": "1.0",
        "artifact_type": "c1-r6-research-memory-retrieval-verification",
        "paper_id": PID,
        "contract_sha256": EXPECTED_CONTRACT,
        "claim_audit_sha256": EXPECTED_AUDIT,
        "research_memory_wiki_sha256": wiki["wiki_sha256"],
        "review_lesson_memory_id": c1_id,
        "review_lesson_selected": True,
        "structured_lesson_codes": sorted(EXPECTED_LESSON_CODES),
        "query_pack_sha256": query["query_pack_sha256"],
        "query_selected_memory_ids": query["selected_memory_ids"],
        "required_phrases_verified": list(required_phrases),
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    body = stable_bytes(receipt)
    RETRIEVAL.write_bytes(body)
    digest = hashlib.sha256(body).hexdigest()
    RETRIEVAL_SHA.write_text(f"{digest}  {RETRIEVAL.name}\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "paper_id": PID,
        "paper_registry_claim_audit_sha256": latest_audit.get("claim_audit_sha256"),
        "review_lesson_memory_id": c1_id,
        "review_lesson_codes": sorted(EXPECTED_LESSON_CODES),
        "wiki_sha256": wiki["wiki_sha256"],
        "query_pack_sha256": query["query_pack_sha256"],
        "retrieval_receipt_sha256": digest,
        "scientific_authority": False,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
