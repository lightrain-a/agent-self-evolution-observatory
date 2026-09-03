#!/usr/bin/env python3
"""R47 utilization qualification adapter for the R45-M1 replacement lineage.

The 8 units, five arms, deterministic schedule, first-action promotion endpoint,
and pass rule are inherited unchanged from frozen R47/R43.  This adapter only
updates the expected replacement manifest/authority statuses and verifies that
the V2 authority is bound to the V2 manifest before any validation treatment.
"""
from __future__ import annotations

try:
    from . import failure_memory_memrl_utilization_r47 as base
except ImportError:
    import failure_memory_memrl_utilization_r47 as base  # type: ignore

REPLACEMENT_MANIFEST_STATUS = "MEMRL_R45M1_INFRASTRUCTURE_ONLY_REPLACEMENT_MANIFEST_FROZEN_ZERO_CONFIRMATORY_OUTCOMES"
REPLACEMENT_AUTHORITY_STATUS = "HUMAN_BOUNDED_R45M1_REPLACEMENT_EXECUTION_AUTHORITY_RECORDED"
EXPECTED_LOOPBACK_SERVER_SHA256 = "f2b4b49b179856cdd02d244fba81ab7c558e747954170285da0eef6119336d92"

base.G8 = REPLACEMENT_MANIFEST_STATUS
base.AUTH = REPLACEMENT_AUTHORITY_STATUS
_original_preflight = base.preflight


def preflight(manifest, auth, qual, frozen, source_receipt):
    _original_preflight(manifest, auth, qual, frozen, source_receipt)
    if not base.valid_receipt(source_receipt):
        raise RuntimeError("source-receipt-hash-drift")
    binding = (auth.get("bindings") or {}).get("migration_manifest") or {}
    if binding.get("receipt_sha256") != manifest.get("receipt_sha256"):
        raise RuntimeError("authority-manifest-receipt-binding-drift")
    adapter = (manifest.get("execution_manifest") or {}).get("external_runtime_adapter") or {}
    if adapter.get("loopback_server_sha256") != EXPECTED_LOOPBACK_SERVER_SHA256:
        raise RuntimeError("replacement-loopback-binding-drift")


base.preflight = preflight

# Re-export scientific helpers unchanged for tests/audit.
ARMS = base.ARMS
arm_order = base.arm_order
u4_map = base.u4_map
plan = base.plan
reverse_blocks = base.reverse_blocks
memctx = base.memctx
analyze = base.analyze


def main() -> None:
    base.main()


if __name__ == "__main__":
    main()
