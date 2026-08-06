from __future__ import annotations

import argparse
import json
import math
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Sequence

from .config import PROJECT_ROOT, StorageSettings
from .iclr_external_review import EXPECTED_HOST, _atomic_json, extract_json, normalize_response, update_store
from .idea_discovery_v4 import DEFAULT_EXTERNAL_JSON, DEFAULT_JSON, build_idea_discovery_v4, write_idea_discovery_v4

REVIEWER = "agent-project-web-gpt-idea-discovery-v4-area-chair"


def load_bank(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else build_idea_discovery_v4()
    if not isinstance(payload.get("tournament_finalists"), list):
        raise ValueError(f"{path} has no tournament_finalists")
    return payload


def packet(idea: dict[str, Any]) -> dict[str, Any]:
    return {
        "idea_id": idea["id"],
        "lineage_type": idea.get("lineage_type"),
        "parent_ids": idea.get("parent_ids", []),
        "title": idea.get("title", {}).get("en", ""),
        "real_problem": idea.get("real_problem", {}).get("en", ""),
        "mechanism_atoms": idea.get("mechanism_atoms", []),
        "composition_logic": idea.get("composition_logic", {}).get("en", ""),
        "persistent_update_object": idea.get("persistent_update_object", ""),
        "learning_signal": idea.get("learning_signal", {}).get("en", ""),
        "independent_ground_truth": idea.get("independent_ground_truth", {}).get("en", ""),
        "strongest_baseline": idea.get("strongest_baseline", {}).get("en", ""),
        "decisive_pilot": idea.get("decisive_pilot", {}).get("en", ""),
        "stop_condition": idea.get("stop_condition", {}).get("en", ""),
        "revival_condition": (idea.get("revival_condition") or {}).get("en", ""),
        "public_assets": idea.get("public_assets", []),
        "internal_scores": idea.get("scores", {}),
    }


def build_prompt(ideas: Sequence[dict[str, Any]], *, batch_index: int, batch_count: int) -> str:
    schema = {
        "reviewer": REVIEWER,
        "review_date": "YYYY-MM-DD",
        "ideas": [{
            "idea_id": "exact supplied id",
            "verdict": "pass|revise|block",
            "confidence": "high|medium|low",
            "finding": "mechanism-level judgment in English",
            "finding_zh": "same judgment in simplified Chinese",
            "required_action": "single material action in English",
            "required_action_zh": "same action in simplified Chinese",
            "combination_audit": {
                "all_atoms_necessary": "yes|partial|no",
                "removable_atoms": ["atoms whose removal preserves the claimed mechanism"],
                "simplest_equivalent_baseline": "capacity-matched simpler method",
                "closed_failure_loop": "whether sensing, credit, update, and future evaluation form a coherent loop",
            },
            "direct_collision": {
                "status": "none|partial|direct|unknown",
                "closest_work": [{"title":"exact title","venue_year":"venue/year","official_url":"official URL","overlap":"problem|mechanism|combination|experiment"}],
                "surviving_difference": "remaining standalone boundary or empty",
            },
            "revival_assessment": "material-change|cosmetic-change|not-applicable",
            "strongest_baseline": "baseline most likely to erase the claim",
            "decisive_pilot": "one matched-budget test",
            "stop_rule": "specific falsification condition",
            "unknowns": ["facts not verifiable from official sources"],
        }],
    }
    return f"""# Independent ICLR Idea Discovery v4 audit — batch {batch_index}/{batch_count}

Act as a strict ICLR area chair and method-composition auditor. These candidates come from a constrained problem × mechanism workflow. Some combine known components; some revive earlier REVISE/BLOCK ideas after changing the learned object, supervision, or deployment boundary.

Do not block an idea merely because it combines known components. A combination may be a legitimate contribution when it closes a real failure loop and every component is necessary. Test necessity by asking whether a capacity-matched simpler baseline can remove an atom while preserving the claimed learning behavior. Conversely, do not reward complexity, naming, or revival wording.

Use web search and consult only official paper pages/PDFs, OpenReview/proceedings, official project pages, and author-maintained repositories. Check work available through 2026-08-01. Never infer methods from titles.

For each idea independently evaluate:
1. Is the stated problem a real deployment or learning failure rather than an invented benchmark gap?
2. Does the composition close sensing/credit/update/future-evaluation, and is each mechanism atom necessary?
3. Is the persistent update object exact and behavior-changing after freezing?
4. Is the learning signal identifiable and ground truth independent?
5. Does a simpler predictor, gate, bandit, rule learner, graph rewriter, or generic optimizer reproduce the proposal under identical data and budgets?
6. For revived ideas, did the learned object or supervision materially change?
7. Can the decisive low-resource pilot falsify the specific combination rather than just the broad problem?

Verdicts:
- `pass`: standalone method thesis survives; combination is necessary or a materially new persistent operator is identified.
- `revise`: real problem and plausible solution, but a component, objective, supervision path, collision boundary, or pilot must materially change.
- `block`: not suitable as a standalone paper now. Keep it as a component, baseline, or future revival branch; do not treat block as deletion.

Return exactly one JSON object and no prose outside JSON. Preserve all exact idea IDs.

Required schema:
```json
{json.dumps(schema, ensure_ascii=False, indent=2)}
```

Candidates:
```json
{json.dumps([packet(idea) for idea in ideas], ensure_ascii=False, indent=2)}
```
"""


def normalize_v4_response(payload: dict[str, Any], expected_ids: Sequence[str], *, source_artifact: str) -> dict[str, dict[str, Any]]:
    reviews = normalize_response(payload, expected_ids, source_artifact=source_artifact)
    rows = {str(row.get("idea_id")): row for row in payload.get("ideas", []) if isinstance(row, dict)}
    for idea_id, review in reviews.items():
        row = rows.get(idea_id, {})
        review["combination_audit"] = row.get("combination_audit", {})
        review["revival_assessment"] = str(row.get("revival_assessment") or "not-applicable")
    return reviews


def rehydrate_review_details(output_dir: Path, store_path: Path = DEFAULT_EXTERNAL_JSON) -> dict[str, Any]:
    bank = load_bank()
    all_ids = [idea["id"] for idea in bank["tournament_finalists"]]
    store = read_store(store_path)
    for response_path in sorted(output_dir.glob("batch-*.response.md")):
        payload = extract_json(response_path.read_text(encoding="utf-8"))
        expected = [str(row.get("idea_id")) for row in payload.get("ideas", []) if isinstance(row, dict)]
        reviews = normalize_v4_response(payload, expected, source_artifact=str(response_path))
        store = update_store(store, reviews, all_ids=all_ids, attempt_result="rehydrated_v4_details", attempt_host=socket.gethostname())
    _atomic_json(store_path, store)
    write_idea_discovery_v4()
    return store


def read_store(path: Path = DEFAULT_EXTERNAL_JSON) -> dict[str, Any]:
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("reviews"), dict):
            return payload
    return {"schema_version":"1.0","pipeline":"code-oracle -> signed-in ChatGPT web UI -> Agent project","required_host":EXPECTED_HOST,"reviews":{},"status":{"reviewed":0,"pending":16,"complete":False,"failed_batches":0}}


def prepare_batches(bank: dict[str, Any], output_dir: Path, *, batch_size: int = 4, include_reviewed: bool = False, review_store: dict[str, Any] | None = None) -> dict[str, Any]:
    store = review_store or read_store(); completed = store.get("reviews", {})
    ideas = [idea for idea in bank["tournament_finalists"] if include_reviewed or not completed.get(idea["id"])]
    output_dir.mkdir(parents=True, exist_ok=True)
    count = math.ceil(len(ideas) / batch_size) if ideas else 0; batches = []
    for index in range(count):
        chunk = ideas[index * batch_size:(index + 1) * batch_size]
        prompt_path = output_dir / f"batch-{index + 1:02d}-of-{count:02d}.md"
        response_path = output_dir / f"batch-{index + 1:02d}-of-{count:02d}.response.md"
        prompt_path.write_text(build_prompt(chunk, batch_index=index + 1, batch_count=count), encoding="utf-8")
        batches.append({"index":index + 1,"idea_ids":[idea["id"] for idea in chunk],"prompt":str(prompt_path),"response":str(response_path)})
    manifest = {"schema_version":"1.0","total_finalists":len(bank["tournament_finalists"]),"queued_ideas":len(ideas),"batch_size":batch_size,"batches":batches}
    _atomic_json(output_dir / "manifest.json", manifest)
    return manifest


def run_batches(bank: dict[str, Any], manifest: dict[str, Any], *, store_path: Path, timeout: int, max_attempts: int = 3) -> dict[str, Any]:
    host = socket.gethostname(); ids = [idea["id"] for idea in bank["tournament_finalists"]]
    if host != EXPECTED_HOST:
        store = update_store(read_store(store_path), {}, all_ids=ids, attempt_result="blocked_wrong_host", attempt_host=host); _atomic_json(store_path, store)
        raise RuntimeError(f"external review requires {EXPECTED_HOST}; current host is {host}")
    runner = PROJECT_ROOT / "scripts" / "project_web_gpt.py"; store = read_store(store_path)
    for batch in manifest.get("batches", []):
        prompt_path = Path(batch["prompt"]); response_path = Path(batch["response"]); last_error = ""
        for attempt in range(1, max_attempts + 1):
            response_path.unlink(missing_ok=True)
            command = [sys.executable, str(runner), "Review the attached ICLR Idea Discovery v4 batch. Return only the required JSON object.", "--file", str(prompt_path), "--slug", f"idea-discovery-v4-{batch['index']:02d}-attempt-{attempt}", "--timeout", str(timeout), "--output", str(response_path)]
            completed = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True, check=False, timeout=timeout + 60)
            try:
                if completed.returncode != 0:
                    raise RuntimeError(completed.stderr[-3000:] or completed.stdout[-3000:] or "Oracle failed")
                payload = extract_json(response_path.read_text(encoding="utf-8"))
                reviews = normalize_v4_response(payload, batch["idea_ids"], source_artifact=str(response_path))
                store = update_store(store, reviews, all_ids=ids, attempt_result=f"batch_{batch['index']}_completed", attempt_host=host)
                _atomic_json(store_path, store); write_idea_discovery_v4(); break
            except Exception as error:
                last_error = str(error)
                if attempt < max_attempts: time.sleep(45 * attempt)
        else:
            status = store.setdefault("status", {}); status["failed_batches"] = int(status.get("failed_batches", 0)) + 1
            store = update_store(store, {}, all_ids=ids, attempt_result=f"batch_{batch['index']}_failed", attempt_host=host); _atomic_json(store_path, store)
            raise RuntimeError(last_error or f"batch {batch['index']} failed")
    return store


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Externally review Idea Discovery v4 finalists.")
    parser.add_argument("--run", action="store_true"); parser.add_argument("--batch-size", type=int, default=4); parser.add_argument("--timeout", type=int, default=900); parser.add_argument("--output-dir", type=Path); parser.add_argument("--include-reviewed", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv); settings = StorageSettings.from_env(); settings.ensure(); bank = load_bank()
    output_dir = args.output_dir or settings.run_dir / "reviews" / "idea-discovery-v4-web-gpt"; store = read_store()
    manifest = prepare_batches(bank, output_dir, batch_size=args.batch_size, include_reviewed=args.include_reviewed, review_store=store)
    if args.run:
        result = run_batches(bank, manifest, store_path=DEFAULT_EXTERNAL_JSON, timeout=args.timeout); print(json.dumps(result.get("status", {}), ensure_ascii=False))
    else:
        print(json.dumps({"output_dir":str(output_dir),"queued":manifest["queued_ideas"],"batches":len(manifest["batches"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
