#!/usr/bin/env python3
"""Static integrity checks for the Agent Self-Evolution Observatory."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_SCRIPTS = [
    "data.js",
    "content-mechanisms-a.js",
    "content-mechanisms-b.js",
    "content-domains-a.js",
    "content-embodied.js",
    "content-evaluation.js",
    "content-coverage.js",
    "content-paper-a.js",
    "content-paper-experiments.js",
    "content-paper-roadmap.js",
    "content-review.js",
    "app.js",
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    html_files = sorted(ROOT.glob("*.html"))
    if len(html_files) != 19:
        fail(f"expected 19 HTML pages, found {len(html_files)}")

    page_ids: dict[str, str] = {}
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        match = re.search(r'<body\s+data-page="([^"]+)"', text)
        if not match:
            fail(f"{path.name} has no data-page")
        page_ids[path.name] = match.group(1)
        for script in EXPECTED_SCRIPTS:
            if f'src="{script}"' not in text:
                fail(f"{path.name} does not load {script}")
        if 'class="sidebar"' not in text or 'id="site-search"' not in text:
            fail(f"{path.name} is missing sidebar or search UI")
        if 'id="dynamic-page"' not in text:
            fail(f"{path.name} is missing the dynamic content root")

    for script in EXPECTED_SCRIPTS:
        path = ROOT / script
        if not path.exists():
            fail(f"missing script {script}")
        subprocess.run(["node", "--check", str(path)], check=True)

    combined = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in EXPECTED_SCRIPTS[:-1])
    for page_id in page_ids.values():
        if f'"{page_id}"' not in combined:
            fail(f"no content configuration found for {page_id}")

    placeholders = ["PAGE_CHUNKS", "<!--NEXT", "<!--PAPERS", "<!--SCRIPT"]
    for path in [*html_files, *(ROOT / name for name in EXPECTED_SCRIPTS)]:
        text = path.read_text(encoding="utf-8")
        for placeholder in placeholders:
            if placeholder in text:
                fail(f"placeholder {placeholder!r} remains in {path.name}")

    cname = (ROOT / "CNAME").read_text(encoding="utf-8").strip()
    if cname != "agent-evolution.lightrain.asia":
        fail(f"unexpected CNAME: {cname}")

    print("PASS")
    print(f"HTML pages: {len(html_files)}")
    print(f"JavaScript files checked: {len(EXPECTED_SCRIPTS)}")
    print(f"Unique page IDs: {len(set(page_ids.values()))}")


if __name__ == "__main__":
    main()
