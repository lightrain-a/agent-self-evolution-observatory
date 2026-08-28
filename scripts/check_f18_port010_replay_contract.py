#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.f18_port010_replay_contract import build_binding, validate_binding, validate_replay_receipt


def main() -> None:
    binding = build_binding()
    binding_errors = validate_binding(binding)
    with tempfile.TemporaryDirectory(prefix="f18-port010-system-gate-") as td:
        root = Path(td)
        payload = b"SYSTEM_GATE_REGRESSION_ONLY\n"
        artifact = root / "exact-f0-replay-sentinel.txt"
        artifact.write_bytes(payload)
        receipt = {
            "receipt_kind": "SYSTEM_GATE_REGRESSION_ONLY",
            "scientific_evidence_created": False,
            "failure_id": "F18",
            "candidate_id": "PORT-010",
            "candidate_snapshot_sha256": binding["research_object"]["candidate_snapshot_sha256"],
            "exact_f0_sha256": binding["exact_f0"]["sha256"],
            "replay_status": "PASS",
            "evidence_review_status": binding["scientific_state"]["evidence_review_verdict"],
            "authority_source": binding["research_object"]["authorization_scope"]["authority_source"],
            "authority": {
                "problem_gate": False,
                "method": False,
                "experiment": False,
                "p0": False,
                "gpu": False,
                "scientific": False,
            },
            "artifacts": [{
                "path": artifact.name,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "provenance": {
                    "frozen_ref": binding["exact_f0"]["sha256"],
                    "generated_by_replay": True,
                },
            }],
        }
        result = validate_replay_receipt(binding, receipt, root)
    output = {
        **result,
        "binding_errors": binding_errors,
        "receipt_kind": "SYSTEM_GATE_REGRESSION_ONLY",
        "scientific_evidence_created": False,
        "offline_replay_tier_authorized": binding["research_object"]["authorization_scope"]["offline_replay_tier_authorized"],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if binding_errors or result["receipt_integrity"] != "PASS" or result["scientific_release"] != "HOLD":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
