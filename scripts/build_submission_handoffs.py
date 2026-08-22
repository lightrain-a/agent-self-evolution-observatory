#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.submission_handoff import (
    HANDOFF_STATUS,
    append_handoff,
    build_handoff_receipt,
    render_handoff_markdown,
    validate_handoff_ledger,
)


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def latest_receipt(row: dict[str, Any]) -> dict[str, Any]:
    for event in reversed(row.get("events") or []):
        if isinstance(event, dict) and event.get("event_type") == "machine-submission-handoff":
            receipt = event.get("receipt") or {}
            return receipt if isinstance(receipt, dict) else {}
    return {}


def build(root: Path, policy_path: Path) -> dict[str, Any]:
    policy = load(policy_path)
    current_dir = root / "paper-submission-handoffs" / "current"
    current_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    eligible = 0
    for paper_path in sorted((root / "paper-acceptance").glob("*.json")):
        paper = load(paper_path)
        paper_id = str(paper.get("paper_id") or paper_path.stem)
        freeze_path = root / "paper-submission-freezes" / f"{paper_id}.json"
        if not freeze_path.exists():
            results.append({"paper_id": paper_id, "status": "SKIPPED_NO_CURRENT_MACHINE_FREEZE"})
            continue
        freeze = load(freeze_path)
        try:
            receipt = build_handoff_receipt(paper_ledger=paper, freeze_ledger=freeze, venue_policy=policy)
        except RuntimeError as exc:
            results.append({"paper_id": paper_id, "status": "SKIPPED_NOT_HANDOFF_ELIGIBLE", "reason": str(exc)})
            continue
        eligible += 1
        row = append_handoff(root, receipt)
        errors = validate_handoff_ledger(row)
        if errors:
            raise RuntimeError(f"handoff ledger invalid for {paper_id}: {errors}")
        current = latest_receipt(row)
        atomic_json(current_dir / f"{paper_id}.json", current)
        atomic_text(current_dir / f"{paper_id}.md", render_handoff_markdown(current))
        results.append({
            "paper_id": paper_id,
            "status": current.get("status"),
            "handoff_sha256": current.get("handoff_sha256"),
            "freeze_sha256": current.get("freeze_sha256"),
            "frozen_artifacts": len(current.get("frozen_artifacts") or []),
            "human_confirmation_status": current.get("human_confirmation_status"),
            "ledger_events": len(row.get("events") or []),
            "ledger_validation_errors": [],
        })
    handoff_times = [
        str(load(path).get("handoff_at") or "")
        for path in sorted(current_dir.glob("*.json"))
        if path.name != "index.json"
    ]
    index: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": max((x for x in handoff_times if x), default="1970-01-01T00:00:00+00:00"),
        "status": "MACHINE_HANDOFF_INDEX_HUMAN_CONFIRMATION_REQUIRED",
        "venue": str(policy.get("venue") or ""),
        "venue_policy_snapshot_sha256": str(policy.get("snapshot_sha256") or ""),
        "summary": {
            "papers_seen": len(results),
            "machine_handoff_ready": eligible,
            "human_confirmed": 0,
            "submitted": 0,
        },
        "papers": results,
        "authority": {"scientific": False, "experiment": False, "gpu": False, "submission": False},
    }
    index["index_sha256"] = digest(index)
    atomic_json(current_dir / "index.json", index)
    return index


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--venue-policy", type=Path)
    args = parser.parse_args()
    policy = args.venue_policy or args.root / "paper-submission-freezes" / "venue-policy-iclr2027-20260822.json"
    index = build(args.root, policy)
    print(json.dumps({"status": "PASS", "summary": index["summary"], "index_sha256": index["index_sha256"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
