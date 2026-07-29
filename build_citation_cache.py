#!/usr/bin/env python3
"""Build a reviewable OpenAlex citation snapshot for the merged bibliography.

The script prints a JavaScript assignment to stdout and never overwrites project
files. Review the title matches before saving the output as a static seed.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import difflib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from catalog_audit import SOURCES, curated_records, fetch_readme, normalize, parse_frontis, parse_survey

OPENALEX_URL = "https://api.openalex.org/works"
SELECT = "id,display_name,cited_by_count,publication_year,primary_location"
USER_AGENT = "agent-self-evolution-observatory/1.0"
MAILTO = "contact@lightrain.asia"


def merged_records() -> list[dict[str, object]]:
    upstream: list[dict[str, object]] = []
    for _, repo, parser in SOURCES:
        markdown = fetch_readme(repo)
        rows = parse_frontis(markdown) if parser == "frontis" else parse_survey(markdown)
        upstream.extend(rows)
    merged: dict[str, dict[str, object]] = {}
    for row in [*upstream, *curated_records()]:
        key = normalize(str(row["title"]))
        if key:
            merged[key] = {**merged.get(key, {}), **row}
    return sorted(merged.values(), key=lambda row: normalize(str(row["title"])))


def request_json(url: str, retries: int = 4) -> dict[str, object]:
    for attempt in range(retries):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.load(response)
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(min(8.0, 0.8 * (2**attempt)))
    raise RuntimeError("unreachable")


def title_score(query: str, candidate: str, query_year: int | None, candidate_year: int | None) -> float:
    q, c = normalize(query), normalize(candidate)
    if not q or not c:
        return 0.0
    ratio = difflib.SequenceMatcher(None, q, c).ratio()
    q_tokens, c_tokens = set(q.split()), set(c.split())
    overlap = len(q_tokens & c_tokens) / max(1, len(q_tokens | c_tokens))
    score = max(ratio, overlap)
    if q == c:
        score = 1.0
    elif q in c or c in q:
        score = max(score, min(len(q), len(c)) / max(len(q), len(c)))
    if query_year and candidate_year:
        gap = abs(query_year - candidate_year)
        if gap == 0:
            score += 0.04
        elif gap > 2:
            score -= 0.12
    return max(0.0, min(1.0, score))


def lookup(record: dict[str, object]) -> tuple[str, dict[str, object] | None]:
    title = str(record["title"])
    year = int(record.get("year") or 0) or None
    params = urllib.parse.urlencode({"search": title, "per-page": 8, "select": SELECT, "mailto": MAILTO})
    try:
        payload = request_json(f"{OPENALEX_URL}?{params}")
    except Exception as exc:
        return normalize(title), {"error": str(exc)}
    candidates = payload.get("results", []) if isinstance(payload, dict) else []
    scored: list[tuple[float, dict[str, object]]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        score = title_score(title, str(candidate.get("display_name", "")), year, candidate.get("publication_year") if isinstance(candidate.get("publication_year"), int) else None)
        scored.append((score, candidate))
    if not scored:
        return normalize(title), None
    score, candidate = max(scored, key=lambda item: item[0])
    if score < 0.78:
        return normalize(title), None
    source = candidate.get("primary_location") or {}
    source_name = ((source.get("source") or {}).get("display_name") if isinstance(source, dict) else None) or ""
    return normalize(title), {
        "citationCount": int(candidate.get("cited_by_count") or 0),
        "openAlexId": candidate.get("id"),
        "matchedTitle": candidate.get("display_name"),
        "matchedYear": candidate.get("publication_year"),
        "matchedVenue": source_name,
        "matchScore": round(score, 3),
        "fetchedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=0, help="0 means all remaining records")
    parser.add_argument("--chunk-id", default="0")
    args = parser.parse_args()

    all_records = merged_records()
    stop = len(all_records) if args.limit <= 0 else min(len(all_records), args.start + args.limit)
    records = all_records[args.start:stop]
    matched: dict[str, dict[str, object]] = {}
    failures: dict[str, object] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(lookup, record) for record in records]
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            key, result = future.result()
            if result and "citationCount" in result:
                matched[key] = result
            elif result and "error" in result:
                failures[key] = result["error"]
            if index % 50 == 0:
                print(f"// processed {index}/{len(records)}", file=sys.stderr)
    payload = {
        "chunkId": str(args.chunk_id),
        "source": "OpenAlex",
        "updatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "catalogRecordCount": len(all_records),
        "start": args.start,
        "end": stop,
        "matchedCount": len(matched),
        "unmatchedCount": len(records) - len(matched),
        "requestFailureCount": len(failures),
        "records": dict(sorted(matched.items())),
    }
    compact = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    print("window.CITATION_CACHE_CHUNKS=window.CITATION_CACHE_CHUNKS||[];window.CITATION_CACHE_CHUNKS.push(" + compact + ");")


if __name__ == "__main__":
    main()
