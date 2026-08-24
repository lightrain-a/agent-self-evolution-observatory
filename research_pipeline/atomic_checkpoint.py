from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .research_execution_kernel import SCHEMA_VERSION, canonical_sha256, validate_experiment_manifest


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists(): return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict): raise ValueError(f"expected JSON object:{path}")
    return payload


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
    os.replace(tmp, path)


class AtomicCheckpointStore:
    """Append-only atomic receipts plus an atomically replaced derived cursor."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.manifest_path = self.root / "experiment-manifest.json"
        self.units_path = self.root / "atomic-results.jsonl"
        self.progress_path = self.root / "progress.json"

    def initialize(self, manifest: dict[str, Any]) -> dict[str, Any]:
        audit = validate_experiment_manifest(manifest)
        if not audit["passed"]:
            raise ValueError("invalid experiment manifest:" + ",".join(audit["blockers"]))
        self.root.mkdir(parents=True, exist_ok=True)
        existing = _read_json(self.manifest_path)
        if existing:
            for key in ("contract_sha256", "execution_identity_sha256"):
                if existing.get(key) != manifest.get(key): raise ValueError(f"resume identity mismatch:{key}")
        else:
            _atomic_json(self.manifest_path, manifest)
        return self.rebuild_progress()

    def rows(self) -> list[dict[str, Any]]:
        if not self.units_path.exists(): return []
        rows: list[dict[str, Any]] = []
        for index, line in enumerate(self.units_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip(): continue
            payload = json.loads(line)
            if not isinstance(payload, dict): raise ValueError(f"invalid atomic row:{index}")
            rows.append(payload)
        return rows

    def append_unit(self, unit_id: str, result: Any, *, status: str = "complete",
                    artifact_refs: Iterable[str] | None = None) -> dict[str, Any]:
        manifest = _read_json(self.manifest_path)
        if not manifest: raise RuntimeError("checkpoint store must be initialized first")
        unit = str(unit_id)
        if unit not in set(str(v) for v in manifest.get("unit_ids") or []):
            raise ValueError(f"unit not declared in frozen manifest:{unit}")
        semantic = {
            "unit_id": unit, "status": str(status), "result_sha256": canonical_sha256(result),
            "artifact_refs": [str(v) for v in (artifact_refs or [])],
            "execution_identity_sha256": manifest["execution_identity_sha256"], "scientific_authority": False,
        }
        semantic["receipt_sha256"] = canonical_sha256(semantic)
        for existing in self.rows():
            if str(existing.get("unit_id") or "") != unit: continue
            if {key: existing.get(key) for key in semantic} != semantic:
                raise ValueError(f"atomic unit already exists with different result:{unit}")
            self.rebuild_progress(); return existing
        row = {"recorded_at": _now(), **semantic}
        with self.units_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush(); os.fsync(handle.fileno())
        self.rebuild_progress(); return row

    def rebuild_progress(self) -> dict[str, Any]:
        manifest = _read_json(self.manifest_path)
        if not manifest: return {}
        units = [str(v) for v in manifest.get("unit_ids") or []]
        by_unit: dict[str, dict[str, Any]] = {}
        for row in self.rows():
            unit = str(row.get("unit_id") or "")
            if unit in by_unit and by_unit[unit].get("receipt_sha256") != row.get("receipt_sha256"):
                raise ValueError(f"conflicting duplicate atomic receipts:{unit}")
            by_unit[unit] = row
        completed = [unit for unit in units if (by_unit.get(unit) or {}).get("status") == "complete"]
        pending = [unit for unit in units if unit not in completed]
        progress = {
            "schema_version": SCHEMA_VERSION, "experiment_id": manifest.get("experiment_id"),
            "execution_identity_sha256": manifest.get("execution_identity_sha256"),
            "completed": len(completed), "total": len(units), "completed_unit_ids": completed,
            "next_unit_id": pending[0] if pending else "", "remaining_unit_ids": pending,
            "status": "COMPLETE" if not pending else ("CHECKPOINT" if completed else "NOT_STARTED"),
            "resume_allowed": bool(pending), "scientific_authority": False,
        }
        _atomic_json(self.progress_path, progress); return progress

    def resume_cursor(self) -> dict[str, Any]:
        return self.rebuild_progress()
