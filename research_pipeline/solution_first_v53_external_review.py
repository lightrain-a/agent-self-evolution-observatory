from __future__ import annotations

import argparse, json, math, socket, subprocess, sys, time
from pathlib import Path
from typing import Any, Sequence

from .config import PROJECT_ROOT, StorageSettings
from .iclr_external_review import EXPECTED_HOST, _atomic_json, extract_json, normalize_response, update_store
from .idea_discovery_v53 import DEFAULT_EXTERNAL_JSON, DEFAULT_JSON, build_idea_discovery_v53, write_idea_discovery_v53

REVIEWER = "agent-project-web-gpt-idea-discovery-v53-area-chair"


def bank() -> dict[str, Any]:
    return json.loads(DEFAULT_JSON.read_text(encoding="utf-8")) if DEFAULT_JSON.exists() else build_idea_discovery_v53()


def prompt(rows: Sequence[dict[str, Any]], batch_index: int, batch_count: int) -> str:
    schema = {
        "reviewer": REVIEWER,
        "review_date": "YYYY-MM-DD",
        "ideas": [{
            "idea_id": "exact id",
            "verdict": "pass|revise|block",
            "confidence": "high|medium|low",
            "finding": "English",
            "finding_zh": "中文",
            "required_action": "English",
            "required_action_zh": "中文",
            "direct_collision": {"status": "none|partial|direct|unknown", "closest_work": [], "surviving_difference": ""},
            "strongest_baseline": "",
            "decisive_pilot": "",
            "stop_rule": "",
            "unknowns": [],
        }],
    }
    return f"""# Independent v5.3 final-boundary repair audit — batch {batch_index}/{batch_count}

Act as a strict ICLR area chair. Each child is the third targeted repair of a previously REVISE idea, selected only because the v5.2 reviewer stated a single surviving boundary. PASS only if the child now satisfies that exact final boundary under an actually capacity/data/budget-matched strongest baseline, freezes a persistent operator, has independent truth, and survives official-source collision search through 2026-08-01. Do not reward accumulated complexity. If the child merely rewrites the experiment without making the mechanism identifiable, REVISE or BLOCK. If the closest simple baseline is now genuinely matched and the claimed operator still survives, PASS is appropriate.

Return exactly one JSON object and no prose outside JSON.

Schema:
```json
{json.dumps(schema, ensure_ascii=False, indent=2)}
```

Children:
```json
{json.dumps(rows, ensure_ascii=False, indent=2)}
```
"""


def store() -> dict[str, Any]:
    if DEFAULT_EXTERNAL_JSON.exists():
        payload = json.loads(DEFAULT_EXTERNAL_JSON.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("reviews"), dict):
            return payload
    return {"schema_version": "1.0", "reviews": {}, "status": {}}


def run(batch_size: int, timeout: int) -> dict[str, Any]:
    if socket.gethostname() != EXPECTED_HOST:
        raise RuntimeError(f"requires {EXPECTED_HOST}")
    payload = bank()
    ids = [x["id"] for x in payload.get("children", [])]
    stored = store()
    rows = [x for x in payload.get("children", []) if not stored.get("reviews", {}).get(x["id"])]
    settings = StorageSettings.from_env(); settings.ensure()
    output_dir = settings.run_dir / "reviews" / "idea-discovery-v53-web-gpt"; output_dir.mkdir(parents=True, exist_ok=True)
    runner = PROJECT_ROOT / "scripts" / "project_web_gpt.py"
    count = math.ceil(len(rows) / batch_size) if rows else 0
    for index in range(count):
        chunk = rows[index * batch_size:(index + 1) * batch_size]
        prompt_path = output_dir / f"batch-{index+1:02d}-of-{count:02d}.md"
        response_path = output_dir / f"batch-{index+1:02d}-of-{count:02d}.response.md"
        prompt_path.write_text(prompt(chunk, index + 1, count), encoding="utf-8")
        last_error = ""
        for attempt in range(1, 4):
            response_path.unlink(missing_ok=True)
            command = [sys.executable, str(runner), "Review the attached v5.3 repaired idea batch. Return only JSON.", "--file", str(prompt_path), "--slug", f"idea-v53-r2-{index+1:02d}-attempt-{attempt}", "--timeout", str(timeout), "--output", str(response_path)]
            completed = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True, check=False, timeout=timeout + 60)
            try:
                if completed.returncode:
                    raise RuntimeError(completed.stderr[-2000:] or completed.stdout[-2000:])
                reviews = normalize_response(extract_json(response_path.read_text(encoding="utf-8")), [x["id"] for x in chunk], source_artifact=str(response_path))
                stored = update_store(stored, reviews, all_ids=ids, attempt_result=f"batch_{index+1}_completed", attempt_host=socket.gethostname())
                _atomic_json(DEFAULT_EXTERNAL_JSON, stored)
                write_idea_discovery_v53()
                break
            except Exception as error:
                last_error = str(error)
                if attempt < 3:
                    time.sleep(45 * attempt)
        else:
            raise RuntimeError(last_error)
    return write_idea_discovery_v53()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--run", action="store_true"); parser.add_argument("--batch-size", type=int, default=4); parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)
    payload = bank(); pending = sum(not store().get("reviews", {}).get(x["id"]) for x in payload.get("children", []))
    if args.run:
        print(json.dumps(run(args.batch_size, args.timeout)["summary"], ensure_ascii=False))
    else:
        print(json.dumps({"children": len(payload.get("children", [])), "pending": pending}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
