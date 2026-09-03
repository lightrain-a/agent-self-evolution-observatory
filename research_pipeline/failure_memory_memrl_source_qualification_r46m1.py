#!/usr/bin/env python3
"""R46 replacement-lineage adapter for R45-M1.

Scientific retrieval/support semantics remain exactly those in R46.  The only
adaptation is to bind R46's service construction and receipt helpers to the
R45-M1 source runner rather than the quarantined R45 host-60 wrapper.
"""
from __future__ import annotations

import argparse
import json
import pathlib

try:
    from . import failure_memory_memrl_source_qualification_r46 as base
    from .failure_memory_memrl_source_execute_r45m1 import (
        PAPER_ID,
        _build_service_and_runner,
        _digest,
        _load,
        _sha,
        _verify_receipt_hash,
    )
except ImportError:
    import failure_memory_memrl_source_qualification_r46 as base  # type: ignore
    from failure_memory_memrl_source_execute_r45m1 import (  # type: ignore
        PAPER_ID,
        _build_service_and_runner,
        _digest,
        _load,
        _sha,
        _verify_receipt_hash,
    )

# Rebind only infrastructure/source-lineage helpers used by base.build().
base.PAPER_ID = PAPER_ID
base._build_service_and_runner = _build_service_and_runner
base._digest = _digest
base._load = _load
base._sha = _sha
base._verify_receipt_hash = _verify_receipt_hash

build = base.build
STATUS_PASS = base.STATUS_PASS
STATUS_STOP = base.STATUS_STOP


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=pathlib.Path, required=True)
    parser.add_argument("--source-receipt", type=pathlib.Path, required=True)
    parser.add_argument("--completed-ledger", type=pathlib.Path, required=True)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()
    result = build(
        args.manifest.resolve(),
        args.source_receipt.resolve(),
        args.completed_ledger.resolve(),
        args.output_dir.resolve(),
    )
    print(json.dumps({
        "status": result["status"],
        "eligible_frozen_retrieval_clusters": result["eligible_frozen_retrieval_clusters"],
        "both_source_provenance_polarities_retrievable": result["both_source_provenance_polarities_retrievable"],
        "validation_treatment_outcomes_observed": 0,
        "receipt_sha256": result["receipt_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
