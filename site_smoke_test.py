#!/usr/bin/env python3
"""Static integrity checks for the Agent Self-Evolution Observatory."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_MAIN_PAGES = 23
REQUIRED_STATIC = [
    "CNAME", ".nojekyll", "style.css", "app.js", "data.js", "favicon.svg",
    "robots.txt", "sitemap.xml", "site.webmanifest", "404.html", "knowledge-map.svg",
    "catalog_audit.py", "browser_smoke_test.py", "CHANGELOG.md",
]
PLACEHOLDERS = ["PAGE_CHUNKS", "<!--NEXT", "<!--PAPERS", "<!--SCRIPT"]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    for name in REQUIRED_STATIC:
        if not (ROOT / name).exists():
            fail(f"missing required file {name}")

    html_files = sorted(path for path in ROOT.glob("*.html") if path.name != "404.html")
    if len(html_files) != EXPECTED_MAIN_PAGES:
        fail(f"expected {EXPECTED_MAIN_PAGES} main HTML pages, found {len(html_files)}")

    page_ids: dict[str, str] = {}
    referenced_scripts: set[str] = set()
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        match = re.search(r'<body\s+data-page="([^"]+)"', text)
        if not match:
            fail(f"{path.name} has no data-page")
        page_id = match.group(1)
        if page_id in page_ids.values():
            fail(f"duplicate data-page {page_id}")
        page_ids[path.name] = page_id
        if 'class="sidebar"' not in text or 'id="site-search"' not in text:
            fail(f"{path.name} is missing sidebar or search UI")
        if 'id="dynamic-page"' not in text:
            fail(f"{path.name} is missing the dynamic content root")
        scripts = re.findall(r'<script\s+src="([^"]+)"', text)
        if "data.js" not in scripts or "app.js" not in scripts:
            fail(f"{path.name} must load data.js and app.js")
        for script in scripts:
            referenced_scripts.add(script)
            if not (ROOT / script).exists():
                fail(f"{path.name} references missing script {script}")

    js_files = sorted(ROOT.glob("*.js"))
    for path in js_files:
        subprocess.run(["node", "--check", str(path)], check=True)

    content_js = [path for path in js_files if path.name != "app.js"]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in content_js)
    for page_id in page_ids.values():
        if f'"{page_id}"' not in combined:
            fail(f"no content configuration found for {page_id}")

    data_text = (ROOT / "data.js").read_text(encoding="utf-8")
    nav_targets = sorted(set(re.findall(r'\["([a-z0-9-]+\.html)"', data_text)))
    missing_nav = [target for target in nav_targets if not (ROOT / target).exists()]
    if missing_nav:
        fail(f"navigation targets missing: {missing_nav}")
    if set(nav_targets) != set(page_ids):
        missing_from_nav = sorted(set(page_ids) - set(nav_targets))
        if missing_from_nav != ["index.html"]:
            fail(f"pages missing from navigation: {missing_from_nav}")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for filename in page_ids:
        url = "https://agent-evolution.lightrain.asia/" if filename == "index.html" else f"https://agent-evolution.lightrain.asia/{filename}"
        if url not in sitemap:
            fail(f"sitemap missing {filename}")

    all_checked = [*html_files, ROOT / "404.html", *js_files, ROOT / "style.css"]
    for path in all_checked:
        text = path.read_text(encoding="utf-8")
        for placeholder in PLACEHOLDERS:
            if placeholder in text:
                fail(f"placeholder {placeholder!r} remains in {path.name}")

    cname = (ROOT / "CNAME").read_text(encoding="utf-8").strip()
    if cname != "agent-evolution.lightrain.asia":
        fail(f"unexpected CNAME: {cname}")

    print("PASS")
    print(f"Main HTML pages: {len(html_files)}")
    print(f"JavaScript files checked: {len(js_files)}")
    print(f"Unique page IDs: {len(set(page_ids.values()))}")
    print(f"Navigation targets: {len(nav_targets)}")


if __name__ == "__main__":
    main()
