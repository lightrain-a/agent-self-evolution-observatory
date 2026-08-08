from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .r3_final_audit import build_r3_final_audit

DEFAULT_OUTPUT = PROJECT_ROOT / "generated" / "ark-r31-repair-candidates-merged.json"
INPUTS = [
    PROJECT_ROOT / "generated" / "ark-r31-repair-candidates.json",
    *[PROJECT_ROOT / "generated" / f"ark-r31-group-{letter}.json" for letter in "abcdefg"],
]


def build() -> dict[str, Any]:
    expected = [row["idea_id"] for row in build_r3_final_audit()["ideas"] if row["verdict"] == "revise"]
    by_parent: dict[str, dict[str, Any]] = {}
    provenance: dict[str, list[str]] = {}
    for path in INPUTS:
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for row in payload.get("repairs") or []:
            parent = row.get("parent_id")
            if parent not in expected or row.get("generator_model") != "deepseek-v4-pro":
                continue
            by_parent[parent] = row
            provenance.setdefault(parent, []).append(path.name)
    missing = [parent for parent in expected if parent not in by_parent]
    extras = sorted(set(by_parent) - set(expected))
    duplicates = {parent: files for parent, files in provenance.items() if len(files) > 1}
    rows = [by_parent[parent] for parent in expected if parent in by_parent]
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "generator_model": "deepseek-v4-pro",
        "summary": {"expected": len(expected), "merged": len(rows), "missing": len(missing), "extras": len(extras), "duplicate_sources": len(duplicates)},
        "validation": {"missing": missing, "extras": extras, "duplicate_sources": duplicates, "complete": not missing and not extras and len(rows) == len(expected)},
        "repairs": rows,
    }


def main() -> int:
    payload = build()
    DEFAULT_OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    if not payload["validation"]["complete"]:
        print(json.dumps(payload["validation"], ensure_ascii=False, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
