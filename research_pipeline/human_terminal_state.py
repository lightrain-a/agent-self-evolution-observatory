from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "human-terminal-idea-state.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "human-terminal-idea-state.js"
GROUP_FILES = tuple(Path(__file__).with_name(f"human_terminal_state_{g}.json") for g in "abcdef")
INDEPENDENT_FILE = Path(__file__).with_name("human_terminal_independent.json")
VALID_STATES = {"p0", "p0-ready", "merge", "drop"}
EXPECTED = Counter({"p0": 13, "merge": 6, "drop": 7})


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_parents() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in GROUP_FILES:
        for idea_id, row in _load(path).items():
            if idea_id in rows:
                raise ValueError(f"duplicate terminal parent: {idea_id}")
            rows[idea_id] = row
    counts = Counter(str(row.get("terminal_state")) for row in rows.values())
    if len(rows) != 26 or counts != EXPECTED:
        raise ValueError(f"terminal ledger mismatch: n={len(rows)} counts={dict(counts)}")
    codes = [str(row.get("code") or "") for row in rows.values()]
    if len(codes) != len(set(codes)) or not all(codes):
        raise ValueError("terminal parent codes must be unique")
    return rows


def load_independent_methods() -> dict[str, dict[str, Any]]:
    return _load(INDEPENDENT_FILE)


def absorbed_child_index() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for parent_id, row in {**load_parents(), **load_independent_methods()}.items():
        roles = row.get("component_roles") or {}
        for child in row.get("absorbed_children") or []:
            result[str(child)] = {"parent_id": parent_id, "role": str(roles.get(child) or "mechanism-component/ablation")}
    return result


def terminal_parent_ids() -> set[str]:
    return set(load_parents())


def absorbed_child_ids() -> set[str]:
    return set(absorbed_child_index())


def repair_allowed(idea_id: str) -> bool:
    idea_id = str(idea_id)
    return idea_id not in terminal_parent_ids() and idea_id not in absorbed_child_ids()


def standalone_allowed(idea_id: str) -> bool:
    return str(idea_id) not in absorbed_child_ids()


def filter_standalone_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if standalone_allowed(str(row.get("idea_id") or row.get("id") or ""))]


def build_human_terminal_state() -> dict[str, Any]:
    parents = load_parents()
    independent = load_independent_methods()
    counts = Counter(row["terminal_state"] for row in parents.values())
    return {
        "schema_version": "1.0",
        "decision_date": "2026-08-11",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_of_truth_priority": ["latest-human-review", "explicit-user-update", "real-experiment", "new-multimodel-review", "historical-automatic-review"],
        "policy": {
            "terminal_parent_repair_forbidden": True,
            "absorbed_child_standalone_forbidden": True,
            "absorbed_child_repair_queue_forbidden": True,
            "absorbed_child_independent_p0_forbidden": True,
            "absorbed_child_advisor_pool_forbidden": True,
            "historical_artifacts_preserved": True,
        },
        "summary": {"human_parents": 26, "p0": counts["p0"], "p0_ready": counts["p0-ready"], "merge": counts["merge"], "drop": counts["drop"], "absorbed_children": len(absorbed_child_index()), "independent_methods": len(independent)},
        "parents": parents,
        "absorbed_children": absorbed_child_index(),
        "independent_methods": independent,
    }


def write_human_terminal_state(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    payload = build_human_terminal_state()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.HUMAN_TERMINAL_IDEA_STATE = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(write_human_terminal_state(), ensure_ascii=False))
