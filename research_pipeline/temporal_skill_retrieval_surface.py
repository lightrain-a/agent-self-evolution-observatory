from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

RETRIEVAL_FIELD = "retrieval_operation_output"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def materialize_retrieval_surface(endpoint: dict[str, Any], operation_output: dict[str, Any]) -> dict[str, Any]:
    """Move the same frozen operation output into retrieved context.

    No candidate, span, record, or metadata row is removed or reordered. The
    only change is one added evidence-package field containing the exact same
    operation output that T exposes through the callable-helper surface.
    """
    row = copy.deepcopy(endpoint)
    package = copy.deepcopy(endpoint["package"])
    if RETRIEVAL_FIELD in package:
        raise ValueError(f"frozen package already contains {RETRIEVAL_FIELD}")
    package[RETRIEVAL_FIELD] = copy.deepcopy(operation_output)
    row["package"] = package
    return row


def parity_receipt(endpoint: dict[str, Any], operation_output: dict[str, Any], retrieval_endpoint: dict[str, Any]) -> dict[str, Any]:
    original_package = endpoint["package"]
    retrieval_package = retrieval_endpoint["package"]
    recovered = {k: v for k, v in retrieval_package.items() if k != RETRIEVAL_FIELD}
    materialized = retrieval_package.get(RETRIEVAL_FIELD)
    return {
        "endpoint_id": endpoint["endpoint_id"],
        "failure_family": endpoint["failure_family"],
        "phase": endpoint["phase"],
        "original_package_sha256": canonical_sha(original_package),
        "retrieval_package_without_operation_sha256": canonical_sha(recovered),
        "operation_output_sha256": canonical_sha(operation_output),
        "materialized_operation_output_sha256": canonical_sha(materialized),
        "candidate_evidence_preserved": canonical_sha(original_package) == canonical_sha(recovered),
        "operation_output_content_equal": canonical_sha(operation_output) == canonical_sha(materialized),
        "only_added_field": set(retrieval_package) == (set(original_package) | {RETRIEVAL_FIELD}),
    }
