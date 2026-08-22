#!/usr/bin/env python3
"""Refresh only the public Paper Acceptance snapshot embedded in Research System state.

The append-only paper ledgers live under the canonical experiment-data root.  The
static-site build already refreshes PaperRegistry from those ledgers, but the much
larger Research System snapshot is intentionally not rebuilt on every frontend
publish.  This focused projection keeps the embedded Paper Acceptance index in
sync without recompiling or mutating any scientific/discovery state.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.config import StorageSettings, resolve_experiment_data_root
from research_pipeline.paper_acceptance_ledger import build_paper_ledger_index, build_portable_paper_ledger_index

GEN = ROOT / "generated"
JSON_PATH = GEN / "research-system-state.json"
JS_PATH = GEN / "research-system-state.js"


def refresh() -> dict:
    state = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    acceptance = state.get("paper_acceptance")
    if not isinstance(acceptance, dict):
        raise RuntimeError("research-system-state.json has no paper_acceptance object")

    data_root = resolve_experiment_data_root(StorageSettings.from_env())
    live_index = build_paper_ledger_index(data_root)
    live_summary = live_index.get("summary") or {}
    ledger_index = live_index
    ledger_source = "canonical-append-only-paper-ledgers"

    if int(live_summary.get("invalid_ledgers") or 0) != 0:
        raise RuntimeError(f"Paper Acceptance live ledger index is invalid: {live_summary}")
    if int(live_summary.get("papers") or 0) == 0:
        registry = json.loads((GEN / "paper-registry.json").read_text(encoding="utf-8"))
        ledger_index = build_portable_paper_ledger_index(registry)
        ledger_source = "generated/paper-registry.json"

    index_summary = ledger_index.get("summary") or {}
    if ledger_index.get("scientific_authority") is not False:
        raise RuntimeError("Paper Acceptance public ledger index must remain zero-authority")
    if int(index_summary.get("invalid_ledgers") or 0) != 0:
        raise RuntimeError(f"Paper Acceptance ledger index is invalid: {index_summary}")
    if int(index_summary.get("papers") or 0) == 0:
        raise RuntimeError("Paper Acceptance projection has no live or portable papers; refusing to erase published state")

    acceptance["ledger_index"] = ledger_index
    acceptance["ledger_index_source"] = ledger_source
    summary = acceptance.setdefault("summary", {})
    summary.update(
        {
            "registered_papers": int(index_summary.get("papers") or 0),
            "scientific_holds": int(index_summary.get("scientific_holds") or 0),
            "submission_ready_papers": int(index_summary.get("submission_ready") or 0),
            "invalid_ledgers": int(index_summary.get("invalid_ledgers") or 0),
            "ledger_submission_ready_papers": int(index_summary.get("submission_ready") or 0),
            "gate_clean_submission_ready_papers": int(index_summary.get("gate_clean_submission_ready") or 0),
            "paper_preparation_failed_papers": int(index_summary.get("paper_preparation_failed") or 0),
            "immediate_submission_holds": int(index_summary.get("immediate_submission_holds") or 0),
            "internal_action_required_papers": int(index_summary.get("internal_action_required") or 0),
            "no_internal_action_papers": int(index_summary.get("no_internal_action") or 0),
        }
    )

    JSON_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    JS_PATH.write_text(
        "window.RESEARCH_SYSTEM_STATE = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    return {
        "papers": int(index_summary.get("papers") or 0),
        "submission_ready": int(index_summary.get("submission_ready") or 0),
        "scientific_holds": int(index_summary.get("scientific_holds") or 0),
        "gate_clean_submission_ready": int(index_summary.get("gate_clean_submission_ready") or 0),
        "immediate_submission_holds": int(index_summary.get("immediate_submission_holds") or 0),
        "internal_action_required": int(index_summary.get("internal_action_required") or 0),
        "no_internal_action": int(index_summary.get("no_internal_action") or 0),
        "invalid_ledgers": int(index_summary.get("invalid_ledgers") or 0),
        "source": ledger_source,
    }


def main() -> None:
    print(json.dumps(refresh(), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
