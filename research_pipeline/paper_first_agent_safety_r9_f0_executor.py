from __future__ import annotations

import argparse
import json
from pathlib import Path

from .paper_first_agent_safety_r9_f0_contract import build_plan, validate_bundle, write_zero_model_ledger


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed canonical R9 F0 write-ahead executor preflight")
    parser.add_argument("--config", required=True)
    parser.add_argument("--states-dir", required=True)
    parser.add_argument("--awm-root", required=True)
    parser.add_argument("--browserart-root", required=True)
    parser.add_argument("--evidence-plan", required=True)
    parser.add_argument("--effective-gate", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    bundle = validate_bundle(
        Path(args.config), Path(args.states_dir), Path(args.awm_root), Path(args.browserart_root),
        Path(args.evidence_plan), Path(args.effective_gate),
    )
    plan = build_plan(bundle)
    receipt = write_zero_model_ledger(bundle, plan, Path(args.output_dir))
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
