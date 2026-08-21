from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .api_memory_ablation import build_basin_aware_api_memory_ablation_plan
from .api_memory_search_smoke import _canonical, _sha_text, _usage, _validate_ideas, generation_prompt
from .api_memory_search_smoke_staged import _client, _load, _lock, _write, context
from .api_research_memory import compile_api_memory_query_pack, record_provider_failure, record_raw_api_output
from .ark_provider import extract_json_object

ARMS = ("portfolio", "relevant", "random")
GENERATOR_MODEL = "kimi-k3"


def prepare(*, root: Path, study: Path, prefix: str) -> dict[str, Any]:
    output = study / "state-prepared.json"
    lock = _lock(output, {"stage": "prepare", "prefix": prefix})
    try:
        ctx = context()
        plan = build_basin_aware_api_memory_ablation_plan(
            context=ctx,
            run_id_prefix=prefix,
            stage="memory-portfolio-smoke",
            max_items=4,
            max_chars=8000,
            max_item_chars=600,
            root=root,
        )
        if plan["status"] != "BASIN_AWARE_API_MEMORY_ABLATION_READY":
            raise RuntimeError(str(plan["invariants"]))
        packs: dict[str, dict[str, Any]] = {}
        for arm in ARMS:
            pack = compile_api_memory_query_pack(
                purpose="IDEA_DISCOVERY",
                context=ctx,
                run_id=f"{prefix}-{arm}",
                stage="memory-portfolio-smoke",
                variant=arm,
                max_items=4,
                max_chars=8000,
                max_item_chars=600,
                required=True,
                record_query=True,
                root=root,
            )
            expected = plan["arms"][arm]
            if list(pack.get("selected_memory_ids") or []) != list(expected["selected_memory_ids"]):
                raise RuntimeError(f"pack drift:{arm}")
            if int((pack.get("summary") or {}).get("characters") or 0) != 2406:
                raise RuntimeError(f"memory character mismatch:{arm}:{pack.get('summary')}")
            packs[arm] = pack
        state = {
            "schema_version": "2.3",
            "status": "PREPARED",
            "prefix": prefix,
            "context": ctx,
            "plan": plan,
            "packs": packs,
            "scientific_authority": False,
            "belief_authority": False,
        }
        state["state_sha256"] = _sha_text(_canonical(state))
        _write(output, state)
        return state
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def generate_arm(*, root: Path, study: Path, arm: str) -> dict[str, Any]:
    if arm not in ARMS:
        raise ValueError(arm)
    prep = _load(study / "state-prepared.json")
    prefix = str(prep["prefix"])
    output = study / f"generation-{arm}.json"
    lock = _lock(output, {"stage": "generate", "arm": arm, "prefix": prefix})
    try:
        pack = prep["packs"][arm]
        prompt = generation_prompt(prep["context"], pack)
        if arm == "portfolio":
            prompt += (
                "\n\nPORTFOLIO_RULE: Treat NEAREST_CLOSED_BASIN as an explicit escape boundary. "
                "Do not rescue, rename, or lightly rephrase that basin. Borrow only contract structure "
                "from surviving/distant memories, and use the unresolved boundary to seek a genuinely different scientific object."
            )
        run_root = root / "runs" / f"{prefix}-{arm}"
        run_root.mkdir(parents=True, exist_ok=True)
        try:
            response = _client().respond(
                prompt,
                model=GENERATOR_MODEL,
                max_output_tokens=6000,
                temperature=0.0,
                thinking="disabled",
                store=True,
            )
        except Exception as error:
            psha = _sha_text(prompt)
            fp = _sha_text(_canonical({
                "stage": "memory-portfolio-smoke",
                "arm": arm,
                "model": GENERATOR_MODEL,
                "prompt_sha256": psha,
                "error_type": type(error).__name__,
                "error": str(error)[:500],
            }))
            receipt = record_provider_failure(
                run_root=run_root,
                stage="memory-portfolio-smoke",
                payload={
                    "status": "PROVIDER_ERROR_ZERO_AUTHORITY",
                    "requested_model": GENERATOR_MODEL,
                    "error_fingerprint": fp,
                    "prompt_sha256": psha,
                },
                root=root,
            )
            failed = {
                "schema_version": "1.0",
                "status": "PROVIDER_FAILURE",
                "arm": arm,
                "error_type": type(error).__name__,
                "error": str(error)[:1200],
                "provider_failure": receipt,
                "scientific_authority": False,
                "belief_authority": False,
            }
            _write(output, failed)
            return failed
        raw = str(response.get("text") or "")
        raw_file = run_root / "raw-generation.txt"
        raw_file.write_text(raw, encoding="utf-8")
        psha = _sha_text(prompt)
        fingerprint = _sha_text(_canonical({
            "stage": "memory-portfolio-smoke",
            "arm": arm,
            "model": GENERATOR_MODEL,
            "prompt_sha256": psha,
            "pack_sha256": pack["query_pack_sha256"],
        }))
        archived = record_raw_api_output(
            run_root=run_root,
            stage="memory-portfolio-smoke",
            raw_path=raw_file,
            requested_model=GENERATOR_MODEL,
            resolved_model=str(response.get("resolved_model") or GENERATOR_MODEL),
            request_fingerprint=fingerprint,
            prompt_sha256=psha,
            root=root,
        )
        ideas = _validate_ideas(extract_json_object(raw))
        result = {
            "schema_version": "2.3",
            "status": "GENERATION_COMPLETE_UNCOMMITTED",
            "arm": arm,
            "run_id": f"{prefix}-{arm}",
            "raw_sha256": archived["raw_sha256"],
            "prompt_sha256": psha,
            "resolved_model": str(response.get("resolved_model") or ""),
            "usage": _usage(response),
            "query_pack_sha256": pack["query_pack_sha256"],
            "selected_memory_ids": pack["selected_memory_ids"],
            "selected_memory_roles": pack.get("selected_memory_roles") or [],
            "ideas": ideas,
            "scientific_authority": False,
            "belief_authority": False,
        }
        result["stage_sha256"] = _sha_text(_canonical(result))
        _write(output, result)
        return result
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def prepare_review(*, root: Path, study: Path) -> dict[str, Any]:
    prep = _load(study / "state-prepared.json")
    prefix = str(prep["prefix"])
    output = study / "review-prepared.json"
    lock = _lock(output, {"stage": "prepare-review", "prefix": prefix})
    try:
        rows = []
        for arm in ARMS:
            gen = _load(study / f"generation-{arm}.json")
            if gen.get("status") != "GENERATION_COMPLETE_UNCOMMITTED":
                raise RuntimeError(f"arm not complete:{arm}:{gen.get('status')}")
            for idea in gen["ideas"]:
                seed = _sha_text(f"memory-portfolio-smoke-v23:{arm}:{idea['id']}:{idea['scientific_object']}")
                rows.append({
                    "blind_id": "B" + seed[:12],
                    **{key: value for key, value in idea.items() if key != "id"},
                    "_arm": arm,
                    "_idea_id": idea["id"],
                })
        ordered = sorted(rows, key=lambda row: _sha_text("blind-order-v23:" + row["blind_id"]))
        public = [{key: value for key, value in row.items() if not key.startswith("_")} for row in ordered]
        review_context = {"generated_ideas": public, "purpose": "hard blind history review for portfolio memory smoke"}
        run_id = f"{prefix}-hard-review"
        history_pack = compile_api_memory_query_pack(
            purpose="SEMANTIC_REVIEW",
            context=review_context,
            run_id=run_id,
            stage="memory-portfolio-hard-review",
            variant="relevant",
            max_items=24,
            max_chars=18000,
            required=True,
            record_query=True,
            root=root,
        )
        result = {
            "schema_version": "2.3",
            "status": "REVIEW_PREPARED",
            "hard_review_run_id": run_id,
            "history_pack": history_pack,
            "blinded": public,
            "mapping": [
                {"blind_id": row["blind_id"], "arm": row["_arm"], "idea_id": row["_idea_id"]}
                for row in ordered
            ],
            "scientific_authority": False,
            "belief_authority": False,
        }
        result["stage_sha256"] = _sha_text(_canonical(result))
        _write(output, result)
        return result
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    for cmd in ("prepare", "prepare-review"):
        p = sub.add_parser(cmd)
        p.add_argument("--persistent-root", type=Path, required=True)
        p.add_argument("--study", type=Path, required=True)
        p.add_argument("--prefix", default="api-memory-portfolio-smoke-v23-r1")
    p = sub.add_parser("generate")
    p.add_argument("--persistent-root", type=Path, required=True)
    p.add_argument("--study", type=Path, required=True)
    p.add_argument("--arm", choices=ARMS, required=True)
    args = parser.parse_args()
    if args.cmd == "prepare":
        result = prepare(root=args.persistent_root, study=args.study, prefix=args.prefix)
    elif args.cmd == "generate":
        result = generate_arm(root=args.persistent_root, study=args.study, arm=args.arm)
    else:
        result = prepare_review(root=args.persistent_root, study=args.study)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
