from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.paper_preparation_protocol import build_paper_preparation_system_state


def load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def migration_rows(acceptance_root: Path) -> list[dict]:
    artifact_root = acceptance_root / "paper-acceptance-artifacts"
    rows: list[dict] = []
    if not artifact_root.is_dir():
        return rows
    for directory in sorted(path for path in artifact_root.iterdir() if path.is_dir()):
        receipt_path = directory / "paper-preparation-receipt.json"
        if not receipt_path.is_file():
            continue
        receipt = load_json(receipt_path)
        paper_state = load_json(directory / "paper-state.json")
        rows.append({
            "paper_id": str(receipt.get("paper_id") or directory.name),
            "protocol_version": str(receipt.get("protocol_version") or ""),
            "pass": receipt.get("pass") is True,
            "receipt_sha256": str(receipt.get("receipt_sha256") or ""),
            "gate_pass": dict(receipt.get("gate_pass") or {}),
            "blockers": list(receipt.get("blockers") or []),
            "current_state": str(paper_state.get("canonical_state") or paper_state.get("paper_acceptance_state") or paper_state.get("status") or ""),
            "scientific_authority": False,
        })
    return rows


def build(acceptance_root: Path) -> dict:
    state = build_paper_preparation_system_state()
    migrations = migration_rows(acceptance_root)
    state["migrations"] = migrations
    state["summary"] = {
        **dict(state.get("summary") or {}),
        "migrated_papers": len(migrations),
        "migrated_pass": sum(row.get("pass") is True for row in migrations),
    }
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--acceptance-root", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory"))
    parser.add_argument("--json-output", type=Path, default=ROOT / "generated/paper-preparation-protocol-state.json")
    parser.add_argument("--js-output", type=Path, default=ROOT / "generated/paper-preparation-protocol-state.js")
    args = parser.parse_args()
    payload = build(args.acceptance_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.js_output.write_text("window.PAPER_PREPARATION_PROTOCOL_STATE = " + json.dumps(payload, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "summary": payload["summary"], "json": str(args.json_output), "js": str(args.js_output)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
