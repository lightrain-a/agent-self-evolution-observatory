#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.paper_first_support_release_watch import (
    run_support_release_watch,
    validate_portable_release_observation_manifest,
    write_portable_release_observation_manifest,
)


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Zero-authority bridge for support release observations across network-isolated research hosts."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    collect = sub.add_parser("collect", help="Collect content-addressed endpoint observations on a networked control host.")
    collect.add_argument("--output", type=Path, required=True)

    validate = sub.add_parser("validate", help="Validate a portable observation manifest without changing research state.")
    validate.add_argument("--input", type=Path, required=True)

    consume = sub.add_parser("consume", help="Consume validated observations through the canonical release-watch decision path.")
    consume.add_argument("--input", type=Path, required=True)
    consume.add_argument("--no-write-ledger", action="store_true")

    args = parser.parse_args()
    if args.command == "collect":
        state = write_portable_release_observation_manifest(args.output)
        print(json.dumps(state, ensure_ascii=False, indent=2))
        if int((state.get("summary") or {}).get("collection_errors") or 0):
            raise SystemExit(2)
        return
    if args.command == "validate":
        state = _read(args.input)
        errors = validate_portable_release_observation_manifest(state)
        print(json.dumps({
            "status": "PASS" if not errors else "REJECT",
            "errors": errors,
            "scientific_authority": False,
        }, ensure_ascii=False, indent=2))
        if errors:
            raise SystemExit(1)
        return
    state = run_support_release_watch(
        portable_observations_path=args.input,
        write_ledger=not args.no_write_ledger,
    )
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
