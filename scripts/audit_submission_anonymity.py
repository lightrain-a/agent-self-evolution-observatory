#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.paper_anonymity_audit import audit_double_blind_bundle, public_anonymity_audit, validate_anonymity_audit_receipt


def parse_artifact(value: str) -> dict[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("artifact must be LABEL=PATH")
    label, path = value.split("=", 1)
    if not label.strip() or not path.strip():
        raise argparse.ArgumentTypeError("artifact must be LABEL=PATH")
    return {"label": label.strip(), "path": path.strip()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit a double-blind submission bundle for metadata/source/archive identity leakage. Findings are content-addressed and redact raw private identity tokens.")
    parser.add_argument("--artifact", action="append", type=parse_artifact, required=True, help="Repeat LABEL=PATH, e.g. paper_pdf=/tmp/main.pdf")
    parser.add_argument("--private-identity-token", action="append", default=[], help="Optional private email/affiliation/handle/token to scan; only its SHA is stored in the receipt.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = audit_double_blind_bundle(artifacts=args.artifact, private_identity_tokens=args.private_identity_token)
    if not validate_anonymity_audit_receipt(receipt):
        raise RuntimeError("generated anonymity audit receipt failed validation")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS_ANONYMITY_AUDIT_RECORDED", "audit": public_anonymity_audit(receipt)}, ensure_ascii=False, indent=2))
    if receipt.get("pass") is not True:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
