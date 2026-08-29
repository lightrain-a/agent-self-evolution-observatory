#!/usr/bin/env python3
"""Plan-scoped Ark embedding endpoint qualification after standard endpoint 401."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from research_pipeline.asset_first_stri_reasoningbank_ark_embedding import (
    ArkEmbeddingClient,
    ArkEmbeddingError,
    ArkEmbeddingSettings,
    EMBEDDING_MODEL,
)
from research_pipeline.asset_first_stri_reasoningbank_ark_embedding_qualification import (
    TEXT_A,
    TEXT_B,
    cosine,
    sha,
    vector_receipt,
)
from research_pipeline.asset_first_stri_reasoningbank_ark_provider import (
    ArkReasoningBankSettings,
    CANONICAL_SECRET_FILE,
)


EXPERIMENT_ID = "E1-STRI-REASONINGBANK-ARK-EMBED-Q1B-20260829"
PLAN_EMBEDDING_URL = "https://ark.cn-beijing.volces.com/api/plan/v3/embeddings"
DEFAULT_OUTPUT = Path(
    "generated/asset-first-stri-reasoningbank-ark-plan-embedding-qualification-result-20260829.json"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, default=CANONICAL_SECRET_FILE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    base = ArkReasoningBankSettings.from_env_file(args.env_file)
    settings = ArkEmbeddingSettings(
        api_key=base.api_key,
        url=PLAN_EMBEDDING_URL,
        model=EMBEDDING_MODEL,
        timeout_seconds=base.timeout_seconds,
        max_retries=base.max_retries,
    )
    client = ArkEmbeddingClient(settings)
    calls = []
    live = []
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
        {str(call.get("resolved_model") or "") for call in calls if call.get("ok")}
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
        "ARK_PLAN_EMBEDDING_BACKEND_QUALIFIED"
        if all(checks.values())
        else "ARK_PLAN_EMBEDDING_BACKEND_NOT_QUALIFIED"
    )
    output = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "experiment_id": EXPERIMENT_ID,
        "contract": (
            "generated/asset-first-stri-reasoningbank-ark-plan-embedding-"
            "qualification-contract-20260829.json"
        ),
        "settings": settings.safe_summary(),
        "calls": calls,
        "resolved_models": resolved,
        "dimensions": sorted(dimensions),
        "checks": checks,
        "decision": decision,
        "scientific_boundary": {
            "single_variable_from_q1": "endpoint path",
            "model_unchanged": True,
            "provider_semantics_only": True,
            "retrieval_rank_observed": False,
            "p1_task_outcome_observed": False,
            "memory_induction_executed": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"decision": decision, "resolved_models": resolved}, sort_keys=True))


if __name__ == "__main__":
    main()
