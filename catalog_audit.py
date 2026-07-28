#!/usr/bin/env python3
"""Audit upstream literature coverage, deduplication, and citation resolution."""
from __future__ import annotations

import base64
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = [
    ("mechanism-survey", "selfimproving-agent/Awesome-Self-Improving-Agents", "survey"),
    ("experience-survey", "FrontisAI/Awesome-Self-Improving-Agents", "frontis"),
]


def normalize(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def fetch_readme(repo: str) -> str:
    sources = [
        (f"https://api.github.com/repos/{repo}/contents/README.md", "api"),
        (f"https://raw.githubusercontent.com/{repo}/main/README.md", "raw"),
        (f"https://cdn.jsdelivr.net/gh/{repo}@main/README.md", "raw"),
    ]
    errors: list[str] = []
    for url, mode in sources:
        request = urllib.request.Request(url, headers={"User-Agent": "agent-evolution-observatory-audit"})
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                if mode == "api":
                    payload = json.load(response)
                    return base64.b64decode(payload["content"]).decode("utf-8")
                return response.read().decode("utf-8")
        except Exception as exc:  # Network and rate-limit fallbacks are intentional here.
            errors.append(f"{url}: {exc}")
    raise RuntimeError(f"Unable to fetch {repo} README via any source: {' | '.join(errors)}")


def parse_survey(markdown: str) -> list[dict[str, object]]:
    rows = []
    pattern = re.compile(
        r"^\s*\|\s*(20\d\d)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*\[paper\]\((.*?)\)",
        re.MULTILINE | re.IGNORECASE,
    )
    for match in pattern.finditer(markdown):
        rows.append({"year": int(match.group(1)), "title": match.group(2).strip(), "venue": match.group(3).strip(), "url": match.group(4).strip()})
    return rows


def parse_frontis(markdown: str) -> list[dict[str, object]]:
    rows = []
    pattern = re.compile(r"^\|\s*(20\d\d)(?:-\d\d)?\s*\|\s*`?[^|`]*`?\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|", re.MULTILINE)
    for match in pattern.finditer(markdown):
        links = re.findall(r"\]\((https?://[^)]+)\)", match.group(3))
        if not links:
            continue
        rows.append({"year": int(match.group(1)), "title": match.group(2).strip(), "venue": "inferred", "url": links[-1]})
    return rows


def curated_records() -> list[dict[str, object]]:
    text = (ROOT / "data.js").read_text(encoding="utf-8").split("window.PAGE_CONTENT", 1)[0]
    records = []
    for match in re.finditer(r"\{year:(\d+),title:\"([^\"]+)\",venue:\"([^\"]*)\",url:\"([^\"]*)\"", text):
        records.append({"year": int(match.group(1)), "title": match.group(2), "venue": match.group(3), "url": match.group(4)})
    return records


def citation_titles() -> set[str]:
    text = (ROOT / "app.js").read_text(encoding="utf-8")
    block = text.split("const PAGE_CITATIONS = {", 1)[1].split("\n};", 1)[0]
    page_ids = set(re.findall(r'^\s*"([a-z0-9-]+)":', block, re.MULTILINE))
    return {value for value in re.findall(r'"([^\"]+)"', block) if value not in page_ids and len(value.split()) >= 3}


def main() -> None:
    source_records: list[dict[str, object]] = []
    for name, repo, parser in SOURCES:
        markdown = fetch_readme(repo)
        rows = parse_frontis(markdown) if parser == "frontis" else parse_survey(markdown)
        source_records.extend({**row, "source": name} for row in rows)
        print(f"{name}: raw={len(rows)}, unique={len({normalize(str(row['title'])) for row in rows})}")

    curated = curated_records()
    merged: dict[str, dict[str, object]] = {}
    for row in [*source_records, *curated]:
        merged[normalize(str(row["title"]))] = row

    source_membership: dict[str, set[str]] = {}
    for row in source_records:
        source_membership.setdefault(normalize(str(row["title"])), set()).add(str(row["source"]))
    overlap = sum(len(sources) > 1 for sources in source_membership.values())

    duplicate_counts = Counter(normalize(str(row["title"])) for row in [*source_records, *curated])
    duplicates = [key for key, count in duplicate_counts.items() if count > 1]
    missing_urls = [row for row in merged.values() if not str(row.get("url", "")).strip()]

    unresolved = []
    keys = set(merged)
    for title in sorted(citation_titles()):
        key = normalize(title)
        if key in keys or any(key in candidate or candidate in key for candidate in keys if len(candidate) > 12):
            continue
        unresolved.append(title)

    print(f"curated: {len(curated)}")
    print(f"cross-source overlap: {overlap}")
    print(f"merged unique titles: {len(merged)}")
    print(f"duplicate normalized titles before merge: {len(duplicates)}")
    print(f"records with missing URL: {len(missing_urls)}")
    print(f"citation titles: {len(citation_titles())}")
    print(f"unresolved citations: {len(unresolved)}")
    for title in unresolved:
        print(f"  - {title}")
    if unresolved:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
