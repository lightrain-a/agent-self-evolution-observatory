from __future__ import annotations

import argparse, json, math, socket, subprocess, sys, time
from pathlib import Path
from typing import Any, Sequence

from .config import PROJECT_ROOT, StorageSettings
from .iclr_external_review import EXPECTED_HOST, _atomic_json, extract_json
from .idea_discovery_v52 import DEFAULT_EXTERNAL_JSON as PARENT_REVIEWS, DEFAULT_JSON as PARENT_JSON
from .idea_discovery_v53 import DEFAULT_PROPOSALS_JSON, write_idea_discovery_v53

TARGET_PARENT_IDS = {
    "compiler-residual-contract-editor",
    "filtered-chronological-evaluator-state",
    "certified-out-of-span-interaction-inverter",
    "frozen-compositional-role-contract-clauses",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def parents() -> list[dict[str, Any]]:
    bank = _load(PARENT_JSON)
    reviews = _load(PARENT_REVIEWS).get("reviews", {})
    by_id = {x["id"]: x for x in bank.get("children", [])}
    rows: list[dict[str, Any]] = []
    for idea_id in TARGET_PARENT_IDS:
        rs = reviews.get(idea_id, [])
        if rs and rs[-1].get("verdict") == "revise" and idea_id in by_id:
            row = dict(by_id[idea_id])
            row["review"] = rs[-1]
            rows.append(row)
    rows.sort(key=lambda x: (x.get("rank", 999), x["id"]))
    return rows


def packet(row: dict[str, Any]) -> dict[str, Any]:
    review = row["review"]
    return {
        "parent_id": row["id"],
        "title": row.get("title"),
        "current_mechanism": row.get("exact_mechanism"),
        "required_action": review.get("required_action"),
        "required_action_zh": review.get("required_action_zh"),
        "surviving_difference": (review.get("direct_collision") or {}).get("surviving_difference", ""),
        "strongest_baseline": review.get("strongest_baseline", ""),
        "finding": review.get("finding", ""),
    }


def prompt(rows: Sequence[dict[str, Any]], batch_index: int, batch_count: int) -> str:
    schema = {
        "children": [{
            "id": "new-id",
            "parent_id": "exact parent id",
            "repair_source": "v52-final-boundary",
            "title": {"zh": "", "en": ""},
            "changed_assumption": {"zh": "", "en": ""},
            "exact_mechanism": {"zh": "", "en": ""},
            "update_surface": "",
            "learning_signal": {"zh": "", "en": ""},
            "independent_ground_truth": {"zh": "", "en": ""},
            "simplest_baseline": {"zh": "", "en": ""},
            "decisive_pilot": {"zh": "", "en": ""},
            "stop_condition": {"zh": "", "en": ""},
            "material_change": {"zh": "", "en": ""},
        }]
    }
    return f"""# v5.3 final-boundary targeted repair — batch {batch_index}/{batch_count}

Generate exactly one materially repaired child for every supplied v5.2 REVISE. These are the closest-to-PASS children and each has one explicit remaining reviewer boundary. Follow that final vector exactly. Do not rename the method, add generic components, or weaken the baseline. The new child must make the proposed mechanism and the strongest simpler method use identical data, labels, traces, verifier access, model capacity, calls, tokens, and optimization budget wherever the reviewer requested equality. When the reviewer requests a crossed experiment or falsifier, make that crossed experiment part of the method's preregistered identification contract. Require a frozen persistent operator and independent truth. Return bilingual fields and only JSON.

Schema:
```json
{json.dumps(schema, ensure_ascii=False, indent=2)}
```

Parents:
```json
{json.dumps([packet(x) for x in rows], ensure_ascii=False, indent=2)}
```
"""


def store() -> dict[str, Any]:
    payload = _load(DEFAULT_PROPOSALS_JSON)
    return payload if isinstance(payload, dict) else {"children": []}


def save(children: list[dict[str, Any]]) -> None:
    current = store()
    by_id = {x["id"]: x for x in current.get("children", []) if isinstance(x, dict)}
    for child in children:
        by_id[child["id"]] = child
    _atomic_json(DEFAULT_PROPOSALS_JSON, {"schema_version": "1.0", "children": list(by_id.values())})
    write_idea_discovery_v53()


def normalize(payload: dict[str, Any], expected_parents: set[str]) -> list[dict[str, Any]]:
    rows = [x for x in payload.get("children", []) if isinstance(x, dict) and x.get("parent_id") in expected_parents and x.get("id") and x.get("id") != x.get("parent_id")]
    missing = expected_parents - {x["parent_id"] for x in rows}
    if missing:
        raise ValueError("missing parents: " + ",".join(sorted(missing)))
    return rows


def run(batch_size: int, timeout: int) -> dict[str, Any]:
    if socket.gethostname() != EXPECTED_HOST:
        raise RuntimeError(f"requires {EXPECTED_HOST}")
    rows = parents()
    existing = {x.get("parent_id") for x in store().get("children", []) if isinstance(x, dict)}
    rows = [x for x in rows if x["id"] not in existing]
    settings = StorageSettings.from_env(); settings.ensure()
    output_dir = settings.run_dir / "reviews" / "idea-discovery-v53-generation"; output_dir.mkdir(parents=True, exist_ok=True)
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
            command = [sys.executable, str(runner), "Generate the attached v5.3 targeted children. Return only JSON.", "--file", str(prompt_path), "--slug", f"idea-v53-gen-{index+1:02d}-attempt-{attempt}", "--timeout", str(timeout), "--output", str(response_path)]
            completed = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True, check=False, timeout=timeout + 60)
            try:
                if completed.returncode:
                    raise RuntimeError(completed.stderr[-2000:] or completed.stdout[-2000:])
                children = normalize(extract_json(response_path.read_text(encoding="utf-8")), {x["id"] for x in chunk})
                save(children)
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
    pending = sum(x["id"] not in {y.get("parent_id") for y in store().get("children", []) if isinstance(y, dict)} for x in parents())
    if args.run:
        print(json.dumps(run(args.batch_size, args.timeout)["summary"], ensure_ascii=False))
    else:
        print(json.dumps({"eligible_parents": len(parents()), "pending": pending}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
