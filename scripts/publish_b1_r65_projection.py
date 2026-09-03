#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_pipeline.paper_acceptance_ledger import build_paper_ledger_index
from research_pipeline.research_item_state import build_paper_registry

PID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
TITLE = "Does Memory Provenance Matter? Provenance Shifts Agent Behavior but Adds Little Terminal Value Beyond Memory Content"
PDF_SHA = "5a929a14c7313ebc44aac1fc70d367b0df5226c28b0bb20aa08aaedf9f0f55e5"
SOURCE_SHA = "ac31427db1df904a65f52b73a85e0f8786db5bcb9f3e8ed4da36ece7ed6bcd3f"
SUPPLEMENT_SHA = "f2fcaca296514c508b6557181405f4daf6e7c243d4ec53101098549e2214a9ed"
GEN = ROOT / "generated"
DL = ROOT / "downloads"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def write_pair(name: str, variable: str, payload: dict) -> None:
    (GEN / f"{name}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (GEN / f"{name}.js").write_text(
        f"window.{variable} = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def summary(rows: list[dict], old: dict) -> dict:
    out = dict(old)
    out["papers"] = len(rows)
    out["submission_ready"] = sum(row.get("submission_ready") is True for row in rows)
    out["gate_clean_submission_ready"] = sum(row.get("gate_clean_submission_ready") is True for row in rows)
    out["paper_preparation_failed"] = sum(
        (row.get("latest_paper_preparation") or {}).get("required_gates", 0) > 0
        and (row.get("latest_paper_preparation") or {}).get("pass") is not True
        for row in rows
    )
    out["immediate_submission_holds"] = sum(row.get("immediate_submission_hold") is True for row in rows)
    out["internal_action_required"] = sum(
        (row.get("primary_next_action") or {}).get("action_class") != "NO_INTERNAL_ACTION" for row in rows
    )
    out["no_internal_action"] = len(rows) - out["internal_action_required"]
    out["by_internal_action"] = dict(
        sorted(Counter((row.get("primary_next_action") or {}).get("action_class") or "UNKNOWN" for row in rows).items())
    )
    out["scientific_holds"] = sum(str(row.get("scientific_status")) != "READY" for row in rows)
    out["by_stage"] = dict(
        sorted(Counter(row.get("paper_stage") or row.get("current_state") or "UNKNOWN" for row in rows).items())
    )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory"))
    args = parser.parse_args()

    stable = {
        "pdf": DL / "B1-Failure-Memory.pdf",
        "source_zip": DL / f"{PID}-source.zip",
        "supplement_zip": DL / f"{PID}-supplement.zip",
    }
    expected = {"pdf": PDF_SHA, "source_zip": SOURCE_SHA, "supplement_zip": SUPPLEMENT_SHA}
    for key, path in stable.items():
        observed = sha(path)
        if observed != expected[key]:
            raise RuntimeError(f"B1 stable artifact mismatch:{key}:{observed}")

    old_registry = json.loads((GEN / "paper-registry.json").read_text(encoding="utf-8"))
    old_other = {row["paper_id"]: row for row in old_registry["papers"] if row.get("paper_id") != PID}
    old_state = json.loads((GEN / "research-system-state.json").read_text(encoding="utf-8"))
    old_entries = ((old_state.get("paper_acceptance") or {}).get("ledger_index") or {}).get("entries") or []
    old_state_other = {row["paper_id"]: row for row in old_entries if row.get("paper_id") != PID}

    live_index = build_paper_ledger_index(args.data_root)
    live_row = next(row for row in live_index["entries"] if row["paper_id"] == PID)
    if live_row.get("title") != TITLE:
        raise RuntimeError("live B1 title is not R63 title")
    if live_row.get("current_state") != "SUBMISSION_READY" or live_row.get("scientific_status") != "READY":
        raise RuntimeError("live B1 acceptance is not READY/SUBMISSION_READY")
    if live_row.get("gate_clean_submission_ready") is not True or live_row.get("immediate_submission_hold") is not False:
        raise RuntimeError("live B1 acceptance gate is not clean")

    candidate_full = build_paper_registry()
    candidate = next(row for row in candidate_full["papers"] if row["paper_id"] == PID)
    if candidate.get("title") != TITLE or candidate.get("contract_sha256") != live_row.get("contract_sha256"):
        raise RuntimeError("B1 registry candidate does not match canonical acceptance ledger")

    rows = [candidate if row.get("paper_id") == PID else row for row in old_registry["papers"]]
    if sum(row.get("paper_id") == PID for row in rows) != 1:
        raise RuntimeError("B1 paper-registry cardinality error")
    old_registry["papers"] = rows
    old_registry["generated_at"] = candidate_full.get("generated_at") or datetime.now(timezone.utc).isoformat(timespec="seconds")
    old_registry["source_revision"] = candidate_full.get("source_revision") or old_registry.get("source_revision")
    old_registry["summary"] = summary(rows, old_registry.get("summary") or {})
    write_pair("paper-registry", "PAPER_REGISTRY", old_registry)

    state = old_state
    paper_acceptance = state.get("paper_acceptance") or {}
    ledger_index = paper_acceptance.get("ledger_index") or {}
    entries = [live_row if row.get("paper_id") == PID else row for row in (ledger_index.get("entries") or [])]
    if sum(row.get("paper_id") == PID for row in entries) != 1:
        raise RuntimeError("B1 research-system ledger cardinality error")
    ledger_index["entries"] = entries
    paper_acceptance["ledger_index"] = ledger_index
    state["paper_acceptance"] = paper_acceptance
    (GEN / "research-system-state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (GEN / "research-system-state.js").write_text(
        "window.RESEARCH_SYSTEM_STATE = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )

    new_other = {row["paper_id"]: row for row in old_registry["papers"] if row.get("paper_id") != PID}
    new_state_other = {row["paper_id"]: row for row in entries if row.get("paper_id") != PID}
    if old_other != new_other or old_state_other != new_state_other:
        raise RuntimeError("non-B1 paper projection changed")

    receipt = {
        "schema_version": "1.0",
        "status": "B1_R65_SELECTIVE_PUBLIC_PROJECTION_PUBLISHED",
        "paper_id": PID,
        "title": TITLE,
        "current_revision": "R65",
        "contract_sha256": live_row.get("contract_sha256"),
        "scientific_status": live_row.get("scientific_status"),
        "current_state": live_row.get("current_state"),
        "gate_clean_submission_ready": live_row.get("gate_clean_submission_ready"),
        "stable_hashes": expected,
        "other_paper_rows_preserved": True,
        "other_paper_registry_digest": digest(new_other),
        "other_research_system_paper_digest": digest(new_state_other),
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["receipt_sha256"] = digest(receipt)
    (GEN / "d2-failure-memory-provenance-r65-public-projection.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
