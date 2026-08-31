#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from research_pipeline.agent_safety_r8_human_semantic import (
    HumanLabelValidationError,
    compare_raters,
    finalize_blinded_human_labels,
    make_adjudication_template,
    validate_adjudication,
    validate_rater_response,
    write_private_json,
)


def _emit(payload: dict, output: str | None) -> None:
    if output:
        write_private_json(output, payload)
        print(json.dumps({"status": "PASS", "output": str(Path(output)), "mode": "0600"}, indent=2))
    else:
        print(json.dumps(payload, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and freeze the AGENT-SAFETY-R9 24-item independent human semantic-label workflow."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-rater", help="Validate one completed first-pass human response.")
    validate.add_argument("response")

    compare = sub.add_parser("compare-raters", help="Validate A/B responses and compute pre-key agreement/conflicts.")
    compare.add_argument("rater_a")
    compare.add_argument("rater_b")
    compare.add_argument("--output")

    make_adj = sub.add_parser("make-adjudication-template", help="Create a 0600 template containing only A/B primary-label conflicts.")
    make_adj.add_argument("rater_a")
    make_adj.add_argument("rater_b")
    make_adj.add_argument("--output", required=True)

    validate_adj = sub.add_parser("validate-adjudication", help="Validate the completed third-adjudicator response.")
    validate_adj.add_argument("adjudication")
    validate_adj.add_argument("rater_a")
    validate_adj.add_argument("rater_b")

    finalize = sub.add_parser(
        "finalize-blind",
        help="Freeze the human-only result before the private experimental key is opened.",
    )
    finalize.add_argument("rater_a")
    finalize.add_argument("rater_b")
    finalize.add_argument("--adjudication")
    finalize.add_argument("--output", required=True)

    args = parser.parse_args()
    try:
        if args.command == "validate-rater":
            obj = validate_rater_response(args.response)
            print(
                json.dumps(
                    {
                        "status": "PASS",
                        "response_role": obj["response_role"],
                        "rater_id": obj["rater_id"],
                        "labels": len(obj["labels"]),
                        "key_unblinding_allowed": False,
                    },
                    indent=2,
                )
            )
        elif args.command == "compare-raters":
            _emit(compare_raters(args.rater_a, args.rater_b), args.output)
        elif args.command == "make-adjudication-template":
            _emit(make_adjudication_template(args.rater_a, args.rater_b), args.output)
        elif args.command == "validate-adjudication":
            obj = validate_adjudication(args.adjudication, args.rater_a, args.rater_b)
            print(json.dumps({"status": "PASS", "adjudication_rows": len(obj["labels"])}, indent=2))
        elif args.command == "finalize-blind":
            _emit(
                finalize_blinded_human_labels(
                    args.rater_a,
                    args.rater_b,
                    adjudication_path=args.adjudication,
                ),
                args.output,
            )
        else:
            parser.error(f"unsupported command: {args.command}")
    except HumanLabelValidationError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
