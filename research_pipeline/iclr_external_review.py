from __future__ import annotations

import argparse
import json
import math
import re
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from .config import PROJECT_ROOT, StorageSettings
from .iclr_idea_factory import DEFAULT_EXTERNAL_REVIEW_JSON, DEFAULT_JSON, load_external_reviews, write_iclr_idea_bank

REVIEWER = "agent-project-web-gpt-iclr-area-chair"
EXPECTED_HOST = "admin01-NF5468M5"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_bank(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload.get("passed_ideas"), list):
        raise ValueError(f"{path} has no passed_ideas list")
    return payload


def idea_packet(idea: dict[str, Any]) -> dict[str, Any]:
    return {
        "idea_id": idea["id"],
        "rank": idea.get("rank"),
        "title": idea.get("title", {}).get("en", ""),
        "track": idea.get("track", {}).get("en", ""),
        "learning_problem": idea.get("purpose", {}).get("en", ""),
        "core_mechanism": idea.get("core_idea", {}).get("en", ""),
        "collision_boundary": idea.get("collision_boundary", {}).get("en", ""),
        "nearest_work": idea.get("nearest_work", []),
        "hypothesis": idea.get("hypothesis", {}).get("en", ""),
        "strongest_baseline": idea.get("strongest_baseline", {}).get("en", ""),
        "pilot": idea.get("pilot", {}).get("en", ""),
        "stop_condition": idea.get("stop_condition", {}).get("en", ""),
        "domains": idea.get("domains", []),
        "budget": idea.get("budget", {}),
    }


def build_prompt(ideas: Sequence[dict[str, Any]], *, batch_index: int, batch_count: int) -> str:
    packets = [idea_packet(idea) for idea in ideas]
    schema = {
        "reviewer": REVIEWER,
        "review_date": "YYYY-MM-DD",
        "ideas": [
            {
                "idea_id": "exact supplied id",
                "verdict": "pass|revise|block",
                "confidence": "high|medium|low",
                "finding": "most important independent judgment",
                "required_action": "single concrete action before advancing",
                "direct_collision": {
                    "status": "none|partial|direct|unknown",
                    "closest_work": [
                        {
                            "title": "exact title",
                            "venue_year": "venue/year or arXiv date",
                            "official_url": "official paper/project/code URL",
                            "overlap": "problem|mechanism|combination|experiment",
                        }
                    ],
                    "surviving_difference": "narrow novelty boundary or empty when blocked",
                },
                "iclr_fit": "strong|conditional|weak",
                "strongest_baseline": "baseline most likely to erase the claim",
                "decisive_pilot": "one normal-setting comparison",
                "stop_rule": "specific falsification condition",
                "unknowns": ["facts not verifiable from official sources"],
            }
        ],
    }
    return f"""# Independent ICLR idea audit — batch {batch_index}/{batch_count}

Act as a strict ICLR area chair and mechanism-level novelty auditor. Review every supplied idea independently. Use web search and consult only official paper pages/PDFs, OpenReview/CVF/ACL/NeurIPS proceedings, official project pages, and author-maintained repositories. Check work available through 2026-08-01. Never infer a method from a title.

For each idea test: persistent learning versus extra inference; exact update surface; identifiable credit; multi-round stability; out-of-loop generalization; independent feedback; matched interaction/token/call/training budgets; direct problem/mechanism/combination/experiment collision; and whether a low-resource P0/P1/P2 pilot can falsify the claim.

Verdicts:
- `pass`: a standalone ICLR thesis survives after explicit narrowing.
- `revise`: useful direction, but the novelty boundary, mechanism, or decisive experiment must change.
- `block`: recent work substantially covers the problem–mechanism pair, or the proposal is not an identifiable learning contribution.

Return exactly one JSON object and no prose outside JSON. Review all {len(packets)} ideas; preserve every exact `idea_id`.

Required schema:
```json
{json.dumps(schema, ensure_ascii=False, indent=2)}
```

Ideas:
```json
{json.dumps(packets, ensure_ascii=False, indent=2)}
```
"""


def extract_json(text: str) -> dict[str, Any]:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    candidate = fenced.group(1) if fenced else text[text.find("{") : text.rfind("}") + 1]
    if not candidate or not candidate.startswith("{"):
        raise ValueError("response does not contain a JSON object")
    payload = json.loads(candidate)
    if not isinstance(payload, dict):
        raise ValueError("response JSON must be an object")
    return payload


def normalize_response(payload: dict[str, Any], expected_ids: Sequence[str], *, source_artifact: str) -> dict[str, dict[str, Any]]:
    rows = payload.get("ideas")
    if not isinstance(rows, list):
        raise ValueError("response has no ideas list")
    expected = list(expected_ids)
    seen: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        idea_id = row.get("idea_id")
        verdict = row.get("verdict")
        if idea_id not in expected or verdict not in {"pass", "revise", "block"}:
            continue
        finding = str(row.get("finding", "")).strip()
        action = str(row.get("required_action", "")).strip()
        if not finding or not action:
            raise ValueError(f"review for {idea_id} lacks finding or required_action")
        seen[idea_id] = {
            "reviewer": str(payload.get("reviewer") or REVIEWER),
            "review_date": str(payload.get("review_date") or utc_now()[:10]),
            "verdict": verdict,
            "confidence": str(row.get("confidence") or "medium"),
            "finding": finding,
            "required_action": action,
            "direct_collision": row.get("direct_collision", {}),
            "iclr_fit": str(row.get("iclr_fit") or "conditional"),
            "strongest_baseline": str(row.get("strongest_baseline") or ""),
            "decisive_pilot": str(row.get("decisive_pilot") or ""),
            "stop_rule": str(row.get("stop_rule") or ""),
            "unknowns": row.get("unknowns", []),
            "source_artifact": source_artifact,
        }
    missing = [idea_id for idea_id in expected if idea_id not in seen]
    if missing:
        raise ValueError("response omitted or malformed ideas: " + ", ".join(missing))
    return seen


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def read_store(path: Path = DEFAULT_EXTERNAL_REVIEW_JSON) -> dict[str, Any]:
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("reviews"), dict):
            return payload
    return {
        "schema_version": "1.0",
        "updated_at": utc_now(),
        "pipeline": "code-oracle -> signed-in ChatGPT web UI -> Agent project",
        "required_host": EXPECTED_HOST,
        "reviews": load_external_reviews(path),
        "status": {},
    }


def update_store(
    store: dict[str, Any],
    new_reviews: dict[str, dict[str, Any]],
    *,
    all_ids: Sequence[str],
    attempt_result: str,
    attempt_host: str,
) -> dict[str, Any]:
    reviews = store.setdefault("reviews", {})
    for idea_id, review in new_reviews.items():
        existing = [item for item in reviews.get(idea_id, []) if item.get("reviewer") != review.get("reviewer")]
        reviews[idea_id] = [*existing, review]
    reviewed = sum(bool(reviews.get(idea_id)) for idea_id in all_ids)
    verdict_counts = {verdict: 0 for verdict in ("pass", "revise", "block", "unknown")}
    for idea_id in all_ids:
        items = reviews.get(idea_id, [])
        verdict = items[-1].get("verdict", "unknown") if items else "unknown"
        verdict_counts[verdict if verdict in verdict_counts else "unknown"] += 1
    store.update({
        "schema_version": "1.0",
        "updated_at": utc_now(),
        "pipeline": "code-oracle -> signed-in ChatGPT web UI -> Agent project",
        "required_host": EXPECTED_HOST,
        "total_passed_ideas": len(all_ids),
    })
    status = store.setdefault("status", {})
    status.update({
        "reviewed": reviewed,
        "pending": len(all_ids) - reviewed,
        "complete": reviewed == len(all_ids),
        "last_attempt": utc_now(),
        "last_attempt_host": attempt_host,
        "last_attempt_result": attempt_result,
        "verdict_counts": verdict_counts,
    })
    return store


def prepare_batches(
    bank: dict[str, Any],
    output_dir: Path,
    *,
    batch_size: int = 5,
    include_reviewed: bool = False,
    review_store: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    store = review_store or read_store()
    completed = store.get("reviews", {})
    ideas = [idea for idea in bank["passed_ideas"] if include_reviewed or not completed.get(idea["id"])]
    output_dir.mkdir(parents=True, exist_ok=True)
    count = math.ceil(len(ideas) / batch_size) if ideas else 0
    batches = []
    for index in range(count):
        chunk = ideas[index * batch_size : (index + 1) * batch_size]
        prompt_path = output_dir / f"batch-{index + 1:02d}-of-{count:02d}.md"
        response_path = output_dir / f"batch-{index + 1:02d}-of-{count:02d}.response.md"
        prompt_path.write_text(build_prompt(chunk, batch_index=index + 1, batch_count=count), encoding="utf-8")
        batches.append({
            "index": index + 1,
            "idea_ids": [idea["id"] for idea in chunk],
            "prompt": str(prompt_path),
            "response": str(response_path),
            "status": "prepared",
        })
    manifest = {
        "schema_version": "1.0",
        "prepared_at": utc_now(),
        "total_passed_ideas": len(bank["passed_ideas"]),
        "already_reviewed": len(bank["passed_ideas"]) - len(ideas) if not include_reviewed else 0,
        "queued_ideas": len(ideas),
        "batch_size": batch_size,
        "batches": batches,
    }
    _atomic_json(output_dir / "manifest.json", manifest)
    return manifest


def run_batches(
    bank: dict[str, Any],
    manifest: dict[str, Any],
    *,
    store_path: Path = DEFAULT_EXTERNAL_REVIEW_JSON,
    timeout: int = 900,
    max_batches: int | None = None,
    max_attempts: int = 3,
) -> dict[str, Any]:
    host = socket.gethostname()
    if host != EXPECTED_HOST:
        store = update_store(read_store(store_path), {}, all_ids=[idea["id"] for idea in bank["passed_ideas"]], attempt_result="blocked_wrong_host", attempt_host=host)
        _atomic_json(store_path, store)
        raise RuntimeError(f"external review requires {EXPECTED_HOST}; current host is {host}")
    runner = PROJECT_ROOT / "scripts" / "project_web_gpt.py"
    store = read_store(store_path)
    batches = manifest.get("batches", [])
    if max_batches is not None:
        batches = batches[:max_batches]
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    for batch in batches:
        prompt_path = Path(batch["prompt"])
        response_path = Path(batch["response"])
        reviews: dict[str, dict[str, Any]] | None = None
        last_error = ""
        for attempt in range(1, max_attempts + 1):
            response_path.unlink(missing_ok=True)
            command = [
                sys.executable,
                str(runner),
                "Review the attached ICLR idea batch. Return only the required JSON object.",
                "--file",
                str(prompt_path),
                "--slug",
                f"iclr-idea-audit-{batch['index']:02d}-attempt-{attempt}",
                "--timeout",
                str(timeout),
                "--output",
                str(response_path),
            ]
            try:
                completed = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True, check=False, timeout=timeout + 60)
                if completed.returncode != 0:
                    raise RuntimeError(completed.stderr[-3000:] or completed.stdout[-3000:] or f"Oracle exited with {completed.returncode}")
                if not response_path.exists():
                    raise RuntimeError("Oracle completed without a response artifact")
                payload = extract_json(response_path.read_text(encoding="utf-8"))
                reviews = normalize_response(payload, batch["idea_ids"], source_artifact=str(response_path))
                break
            except (OSError, RuntimeError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as error:
                last_error = str(error)
                status = store.setdefault("status", {})
                status["failed_batches"] = int(status.get("failed_batches", 0)) + 1
                store = update_store(
                    store,
                    {},
                    all_ids=[idea["id"] for idea in bank["passed_ideas"]],
                    attempt_result=f"batch_{batch['index']}_attempt_{attempt}_failed",
                    attempt_host=host,
                )
                status = store.setdefault("status", {})
                status["last_error"] = last_error[:1000]
                _atomic_json(store_path, store)
                if attempt < max_attempts:
                    time.sleep(min(30, 10 * attempt))
        if reviews is None:
            raise RuntimeError(f"batch {batch['index']} failed after {max_attempts} attempts: {last_error}")
        store = update_store(store, reviews, all_ids=[idea["id"] for idea in bank["passed_ideas"]], attempt_result=f"batch_{batch['index']}_completed", attempt_host=host)
        store.setdefault("status", {}).pop("last_error", None)
        _atomic_json(store_path, store)
        write_iclr_idea_bank()
    return store


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch-review all first-round-passed ICLR ideas with Code Oracle and the signed-in Agent-project ChatGPT.")
    parser.add_argument("--run", action="store_true", help="Execute prepared batches through scripts/project_web_gpt.py")
    parser.add_argument("--include-reviewed", action="store_true", help="Re-review ideas that already have an external result")
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--max-batches", type=int)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--bank", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--store", type=Path, default=DEFAULT_EXTERNAL_REVIEW_JSON)
    parser.add_argument("--output-dir", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    settings = StorageSettings.from_env()
    settings.ensure()
    bank = load_bank(args.bank)
    output_dir = args.output_dir or settings.run_dir / "reviews" / "iclr-project-web-gpt"
    manifest = prepare_batches(bank, output_dir, batch_size=args.batch_size, include_reviewed=args.include_reviewed, review_store=read_store(args.store))
    if args.run:
        store = run_batches(bank, manifest, store_path=args.store, timeout=args.timeout, max_batches=args.max_batches, max_attempts=args.max_attempts)
        print(json.dumps(store.get("status", {}), ensure_ascii=False))
    else:
        print(json.dumps({"output_dir": str(output_dir), **{key: manifest[key] for key in ("total_passed_ideas", "already_reviewed", "queued_ideas", "batch_size")}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
