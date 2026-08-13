from __future__ import annotations

import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

from .paper_first_primary_evidence import parse_arxiv_page, extract_empirical_fact_candidates, extract_typed_evidence_candidates


def collect_refs(run_root: Path) -> set[str]:
    refs: set[str] = set()
    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "ref" and isinstance(item, str) and item.startswith("arXiv:"):
                    refs.add(item)
                else:
                    walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
    for pattern in ("expand-*.json", "evolve-*.json", "formulate-*.json"):
        for path in run_root.glob(pattern):
            try:
                walk(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
    return refs


def choose_cached(source_dir: Path, pattern: str, cutoff: float) -> Path | None:
    rows: list[tuple[float, Path]] = []
    for path in source_dir.glob(pattern):
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if mtime <= cutoff:
            rows.append((mtime, path))
    return max(rows, key=lambda row: row[0])[1] if rows else None


def build_frozen_pool(run_root: Path, source_dir: Path, out: Path) -> dict:
    refs = sorted(collect_refs(run_root))
    if not refs:
        raise ValueError("no staged arXiv refs")
    expansion_raw = list((run_root / "raw").glob("expand-*.txt"))
    cutoff = min((path.stat().st_mtime for path in expansion_raw), default=datetime.now(timezone.utc).timestamp())
    records = []
    missing = []
    for ref in refs:
        arxiv_id = ref.removeprefix("arXiv:")
        abs_path = choose_cached(source_dir, f"arxiv-{arxiv_id}-*.html", cutoff)
        full_path = choose_cached(source_dir, f"arxiv-full-{arxiv_id}-*.html", cutoff)
        if abs_path is None:
            missing.append(ref)
            continue
        raw = abs_path.read_bytes()
        page = raw.decode("utf-8", errors="replace")
        parsed = parse_arxiv_page(page)
        title = str(parsed.get("title") or "").strip()
        abstract = str(parsed.get("abstract") or "").strip()
        if not title or not abstract:
            missing.append(ref)
            continue
        facts = []
        typed = {"operational_assumptions": [], "measured_failures": [], "boundary_observations": []}
        full_sha = ""
        if full_path is not None:
            full_raw = full_path.read_bytes()
            full_sha = hashlib.sha256(full_raw).hexdigest()
            full_text = full_raw.decode("utf-8", errors="replace")
            facts = extract_empirical_fact_candidates(full_text, max_facts=4)
            typed = extract_typed_evidence_candidates(full_text, max_per_type=2)
        records.append({
            "ref": ref,
            "title": title,
            "primary_url": f"https://arxiv.org/abs/{arxiv_id}",
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "abstract_sha256": hashlib.sha256(abstract.encode()).hexdigest(),
            "abstract": abstract,
            "fulltext_sha256": full_sha,
            "fulltext_verified": bool(full_sha),
            "empirical_facts": facts,
            "typed_evidence": typed,
            "primary_source_verified": True,
            "recovered_from_content_addressed_primary_cache": True,
        })
    if missing:
        raise ValueError("missing cached primary evidence:" + ",".join(missing))
    payload = {
        "schema_version": "1.0",
        "status": "READY",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "frozen_for_search_portfolio": True,
        "recovered_after_scheduler_rollover": True,
        "recovery_cutoff_epoch": cutoff,
        "summary": {
            "selected": len(records),
            "verified": len(records),
            "fulltext_verified": sum(bool(row["fulltext_verified"]) for row in records),
            "candidate_generation_ready": True,
        },
        "policy": {
            "candidate_generation_authority": False,
            "method_authority": False,
            "experiment_authority": False,
            "p0_authority": False,
            "content_addressed_cache_recovery": True,
            "scheduler_rollover_cannot_change_frozen_transaction": True,
        },
        "records": records,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload["frozen_pool_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"refs": len(refs), "verified": len(records), "fulltext_verified": payload["summary"]["fulltext_verified"], "frozen_pool_sha256": payload["frozen_pool_sha256"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_frozen_pool(args.run_root, args.source_dir, args.out), ensure_ascii=False))


if __name__ == "__main__":
    main()
