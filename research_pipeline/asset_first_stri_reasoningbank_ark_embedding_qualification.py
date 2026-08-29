#!/usr/bin/env python3
"""Live semantic qualification for the Ark embedding retrieval adapter."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_ark_embedding import (
    ArkEmbeddingClient,
    ArkEmbeddingError,
    ArkEmbeddingSettings,
)
from research_pipeline.asset_first_stri_reasoningbank_ark_provider import (
    CANONICAL_SECRET_FILE,
)


EXPERIMENT_ID = "E1-STRI-REASONINGBANK-ARK-EMBED-Q1-20260829"
DEFAULT_OUTPUT = Path(
    "generated/asset-first-stri-reasoningbank-ark-embedding-qualification-result-20260829.json"
)
TEXT_A = "Inspect the repository state before editing and run the narrow regression test."
TEXT_B = "Verify assumptions, implement the smallest change, and test the focused behavior."


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def vector_receipt(vector: list[float]) -> dict[str, Any]:
    serialized = json.dumps(vector, separators=(",", ":"))
    norm = math.sqrt(sum(value * value for value in vector))
    return {
        "dimension": len(vector),
        "sha256": sha(serialized),
        "l2_norm": norm,
        "all_finite": all(math.isfinite(value) for value in vector),
    }


def cosine(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    return numerator / (left_norm * right_norm)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, default=CANONICAL_SECRET_FILE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    settings = ArkEmbeddingSettings.from_env_file(args.env_file)
    client = ArkEmbeddingClient(settings)
    calls: list[dict[str, Any]] = []
    live: list[dict[str, Any]] = []
    for label, inputs in (
        ("batch_a_a_b", [TEXT_A, TEXT_A, TEXT_B]),
        ("repeat_a", [TEXT_A]),
    ):
        try:
            result = client.embed(inputs)
            live.append(result)
            calls.append(
                {
                    "label": label,
                    "ok": True,
                    "requested_model": result["requested_model"],
                    "resolved_model": result["resolved_model"],
                    "input_sha256": [sha(value) for value in inputs],
                    "vectors": [vector_receipt(vector) for vector in result["vectors"]],
                    "usage": result["usage"],
                    "credential_material_present": False,
                }
            )
        except ArkEmbeddingError as error:
            calls.append({"label": label, "ok": False, **error.safe_receipt()})

    vectors = live[0]["vectors"] if live else []
    repeat = live[1]["vectors"][0] if len(live) > 1 else []
    resolved = sorted(
        {
            str(call.get("resolved_model") or "")
            for call in calls
            if call.get("ok")
        }
    )
    dimensions = {
        vector["dimension"]
        for call in calls
        if call.get("ok")
        for vector in call["vectors"]
    }
    checks = {
        "all_requests_succeeded": all(call.get("ok") for call in calls),
        "requested_model_exact": all(
            call.get("requested_model") == settings.model
            for call in calls
            if call.get("ok")
        ),
        "stable_nonempty_resolved_model": len(resolved) == 1 and bool(resolved[0]),
        "one_stable_dimension": len(dimensions) == 1 and next(iter(dimensions), 0) > 0,
        "all_vectors_finite": all(
            vector["all_finite"]
            for call in calls
            if call.get("ok")
            for vector in call["vectors"]
        ),
        "same_input_same_batch_exact": bool(vectors) and vectors[0] == vectors[1],
        "same_input_repeat_exact": bool(vectors) and vectors[0] == repeat,
        "distinct_text_not_exact": bool(vectors) and vectors[0] != vectors[2],
        "self_cosine_one": bool(vectors)
        and abs(cosine(vectors[0], vectors[1]) - 1.0) < 1e-12,
        "usage_present": all(bool(call.get("usage")) for call in calls if call.get("ok")),
    }
    decision = (
        "ARK_EMBEDDING_BACKEND_QUALIFIED"
        if all(checks.values())
        else "ARK_EMBEDDING_BACKEND_NOT_QUALIFIED"
    )
    output = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "experiment_id": EXPERIMENT_ID,
        "contract": (
            "generated/asset-first-stri-reasoningbank-ark-embedding-qualification-"
            "contract-20260829.json"
        ),
        "settings": settings.safe_summary(),
        "calls": calls,
        "resolved_models": resolved,
        "dimensions": sorted(dimensions),
        "checks": checks,
        "decision": decision,
        "scientific_boundary": {
            "provider_semantics_only": True,
            "retrieval_rank_observed": False,
            "p1_task_outcome_observed": False,
            "memory_induction_executed": False,
            "behavioral_claim_authorized": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"decision": decision, "resolved_models": resolved}, sort_keys=True))


if __name__ == "__main__":
    main()
