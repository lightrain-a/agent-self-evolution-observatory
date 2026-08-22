#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.rebuttal_protocol import append_review_set, build_review_set, validate_review_set


def load(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Record real venue reviews against an already receipt-bound SUBMITTED paper. No model calls or experiments are performed.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--reviews", type=Path, required=True, help="JSON array or {reviews:[...]} with review_id/source_ref/received_at/text.")
    args = parser.parse_args()

    paper_path = args.root / "paper-acceptance" / f"{args.paper_id}.json"
    if not paper_path.exists():
        parser.error("canonical paper ledger not found")
    paper = load(paper_path)
    payload = load(args.reviews)
    reviews = payload.get("reviews") if isinstance(payload, dict) else payload
    if not isinstance(reviews, list):
        parser.error("review input must be a JSON array or an object with a reviews array")

    review_set = build_review_set(paper, reviews)
    if not validate_review_set(review_set):
        raise RuntimeError("compiled review set failed validation")
    row = append_review_set(args.root, review_set)
    print(json.dumps({
        "status": "REVIEW_SET_RECORDED",
        "paper_id": args.paper_id,
        "review_count": review_set["review_count"],
        "review_set_sha256": review_set["review_set_sha256"],
        "submission_receipt_sha256": review_set["submission_receipt_sha256"],
        "ledger_events": len(row.get("events") or []),
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
