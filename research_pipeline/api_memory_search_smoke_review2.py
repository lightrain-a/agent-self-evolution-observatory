from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import replace
from pathlib import Path
from typing import Any

from .api_memory_search_smoke import _canonical, _sha_text, _usage, review_prompt
from .api_research_memory import (
    compile_api_memory_query_pack,
    record_api_memory_consumption,
    record_parsed_api_output,
    record_provider_failure,
    record_raw_api_output,
)
from .ark_provider import ArkResponsesClient, ArkSettings, extract_json_object

REVIEWER_MODEL = "minimax-m3"


def _client() -> ArkResponsesClient:
    base = ArkSettings.from_env()
    return ArkResponsesClient(
        replace(base, max_retries=0, timeout_seconds=max(240.0, base.timeout_seconds))
    )


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _lock(output: Path) -> Path:
    if output.exists():
        raise RuntimeError(f"OUTPUT_ALREADY_EXISTS:{output}")
    lock = Path(str(output) + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise RuntimeError(f"STAGE_ALREADY_RUNNING_OR_STALE_LOCK:{lock}") from error
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps({"stage": "blind-review2", "model": REVIEWER_MODEL}, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return lock


def run(*, root: Path, study: Path) -> dict[str, Any]:
    prepared = _load(study / "review-prepared.json")
    first = _load(study / "review-result.json")
    if first.get("status") != "REVIEW_COMPLETE_UNCOMMITTED":
        raise RuntimeError("first reviewer is not complete")
    output = study / "review2-result.json"
    lock = _lock(output)
    try:
        review_context = {
            "generated_ideas": prepared["blinded"],
            "purpose": "blind search-policy review",
        }
        prefix = str(_load(study / "state-prepared.json")["prefix"])
        run_id = f"{prefix}-blind-review2-r1"
        pack = compile_api_memory_query_pack(
            purpose="SEMANTIC_REVIEW",
            context=review_context,
            run_id=run_id,
            stage="memory-search-smoke-review",
            variant="relevant",
            max_items=24,
            max_chars=18000,
            required=True,
            record_query=True,
            root=root,
        )
        if pack["query_pack_sha256"] != prepared["history_pack"]["query_pack_sha256"]:
            raise RuntimeError("second reviewer history pack drift")
        prompt = review_prompt(pack, prepared["blinded"])
        run_root = root / "runs" / run_id
        run_root.mkdir(parents=True, exist_ok=True)
        try:
            response = _client().respond(
                prompt,
                model=REVIEWER_MODEL,
                max_output_tokens=7500,
                temperature=0.0,
                thinking="disabled",
                store=True,
            )
        except Exception as error:
            psha = _sha_text(prompt)
            fp = _sha_text(
                _canonical(
                    {
                        "stage": "memory-search-smoke-review2",
                        "model": REVIEWER_MODEL,
                        "prompt_sha256": psha,
                        "error_type": type(error).__name__,
                        "error": str(error)[:500],
                    }
                )
            )
            receipt = record_provider_failure(
                run_root=run_root,
                stage="memory-search-smoke-review2",
                payload={
                    "status": "PROVIDER_ERROR_ZERO_AUTHORITY",
                    "requested_model": REVIEWER_MODEL,
                    "error_fingerprint": fp,
                    "prompt_sha256": psha,
                },
                root=root,
            )
            failed = {
                "schema_version": "1.0",
                "status": "PROVIDER_FAILURE",
                "run_id": run_id,
                "error_type": type(error).__name__,
                "error": str(error)[:1200],
                "provider_failure": receipt,
                "scientific_authority": False,
                "belief_authority": False,
            }
            _write(output, failed)
            return failed

        raw = str(response.get("text") or "")
        raw_file = run_root / "raw-review2.txt"
        raw_file.write_text(raw, encoding="utf-8")
        psha = _sha_text(prompt)
        fingerprint = _sha_text(
            _canonical(
                {
                    "stage": "memory-search-smoke-review2",
                    "model": REVIEWER_MODEL,
                    "prompt_sha256": psha,
                    "pack_sha256": pack["query_pack_sha256"],
                }
            )
        )
        archived = record_raw_api_output(
            run_root=run_root,
            stage="memory-search-smoke-review2",
            raw_path=raw_file,
            requested_model=REVIEWER_MODEL,
            resolved_model=str(response.get("resolved_model") or REVIEWER_MODEL),
            request_fingerprint=fingerprint,
            prompt_sha256=psha,
            root=root,
        )
        payload = extract_json_object(raw)
        reviews = payload.get("reviews")
        if not isinstance(reviews, list) or len(reviews) != 18:
            raise ValueError("second reviewer must return 18 reviews")
        expected = {str(row["blind_id"]) for row in prepared["blinded"]}
        observed = {str(row.get("blind_id") or "") for row in reviews if isinstance(row, dict)}
        if observed != expected:
            raise ValueError("second reviewer blind ids mismatch")

        structured = {
            "schema_version": "1.0",
            "study": "API_MEMORY_SEARCH_SMOKE_V22_STAGED_REVIEW2",
            "history_query_pack_sha256": pack["query_pack_sha256"],
            "selected_history_memory_ids": pack["selected_memory_ids"],
            "usage": _usage(response),
            "reviews": reviews,
            "scientific_authority": False,
            "belief_authority": False,
        }
        record_parsed_api_output(
            run_root=run_root,
            stage="memory-search-smoke-review2",
            raw_sha256=archived["raw_sha256"],
            structured_payload=structured,
            requested_model=REVIEWER_MODEL,
            resolved_model=str(response.get("resolved_model") or REVIEWER_MODEL),
            research_objects=[],
            root=root,
        )
        record_api_memory_consumption(
            run_id=run_id,
            stage="memory-search-smoke-review2",
            pack=pack,
            raw_sha256=archived["raw_sha256"],
            output_object_ids=sorted(expected),
            outcome_status="SEARCH_SMOKE_BLIND_REVIEW2_ZERO_AUTHORITY",
            root=root,
        )
        result = {
            "schema_version": "1.0",
            "status": "REVIEW2_COMPLETE",
            "run_id": run_id,
            "raw_sha256": archived["raw_sha256"],
            "prompt_sha256": psha,
            "history_query_pack_sha256": pack["query_pack_sha256"],
            "resolved_model": str(response.get("resolved_model") or ""),
            "usage": _usage(response),
            "reviews": reviews,
            "scientific_authority": False,
            "belief_authority": False,
        }
        result["stage_sha256"] = hashlib.sha256(_canonical(result).encode()).hexdigest()
        _write(output, result)
        return result
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--persistent-root", type=Path, required=True)
    parser.add_argument("--study", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(root=args.persistent_root, study=args.study), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
