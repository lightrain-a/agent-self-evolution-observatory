#!/usr/bin/env python3
"""Static integrity checks for the Agent Self-Evolution Observatory."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_MAIN_PAGES = 24
REQUIRED_STATIC = [
    "CNAME", ".nojekyll", "style.css", "app.js", "data.js", "favicon.svg",
    "robots.txt", "sitemap.xml", "site.webmanifest", "404.html", "knowledge-map.svg",
    "agent-self-evolution-directions-en.svg", "agent-self-evolution-directions-zh.svg",
    "portfolio-data.js", "history-figure-data.js", "content-research-directions.js", "content-idea-portfolio.js",
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

    portfolio_text = (ROOT / "portfolio-data.js").read_text(encoding="utf-8")
    direction_ids = re.findall(r'^\s*id:"([a-z0-9-]+)",\s*code:"D\d+"', portfolio_text, re.MULTILINE)
    idea_names = re.findall(r'^  \{name:"([^"]+)",directionId:"([a-z0-9-]+)",rank:(\d+)', portfolio_text, re.MULTILINE)
    if len(direction_ids) != 10 or len(set(direction_ids)) != 10:
        fail(f"expected 10 unique research directions, found {len(direction_ids)}")
    if len(idea_names) != 34:
        fail(f"expected 34 paper ideas, found {len(idea_names)}")
    names = [name for name, _, _ in idea_names]
    ranks = sorted(int(rank) for _, _, rank in idea_names)
    if len(set(names)) != 34 or ranks != list(range(1, 35)):
        fail("paper ideas must have unique names and ranks 1-34")
    unknown_directions = sorted({direction for _, direction, _ in idea_names} - set(direction_ids))
    if unknown_directions:
        fail(f"ideas reference unknown directions: {unknown_directions}")
    mapped_names = []
    for block in re.findall(r'ideaIds:\[([^\]]*)\]', portfolio_text):
        mapped_names.extend(re.findall(r'"([^"]+)"', block))
    if sorted(mapped_names) != sorted(names) or len(mapped_names) != len(set(mapped_names)):
        fail("each paper idea must appear exactly once in the direction mapping")
    for figure_name in ["agent-self-evolution-directions-en.svg", "agent-self-evolution-directions-zh.svg"]:
        figure_text = (ROOT / figure_name).read_text(encoding="utf-8")
        missing_ideas = [name for name in names if name not in figure_text]
        if missing_ideas:
            fail(f"{figure_name} is missing ideas: {missing_ideas}")

    history_text = (ROOT / "history-figure-data.js").read_text(encoding="utf-8")
    history_counts = {
        "stages": len(re.findall(r'^\s*code:"P\d"', history_text, re.MULTILINE)),
        "capabilities": len(re.findall(r'^\s*\{name:\{en:', history_text, re.MULTILINE)),
        "directions": len(re.findall(r'^\s*\{code:"D\d+",title:', history_text, re.MULTILINE)),
        "milestones": len(re.findall(r'^\s*\{year:\d{4},short:', history_text, re.MULTILINE)),
        "shifts": len(re.findall(r'^\s*\{from:\{en:', history_text, re.MULTILINE)),
        "enablers": len(re.findall(r'^\s*\{title:\{en:', history_text, re.MULTILINE)),
        "ladder": len(re.findall(r'^\s*\{level:"L\d"', history_text, re.MULTILINE)),
    }
    expected_history = {"stages": 6, "capabilities": 5, "directions": 10, "milestones": 23, "shifts": 7, "ladder": 5}
    for key, expected in expected_history.items():
        if history_counts[key] != expected:
            fail(f"history figure expected {expected} {key}, found {history_counts[key]}")
    foundations_html = (ROOT / "foundations.html").read_text(encoding="utf-8")
    if 'src="history-figure-data.js"' not in foundations_html:
        fail("foundations.html must load history-figure-data.js")
    app_text = (ROOT / "app.js").read_text(encoding="utf-8")
    for marker in ["history-overview-figure", "history-stage-grid", "history-capabilities", "history-milestone-grid"]:
        if marker not in app_text:
            fail(f"history renderer is missing {marker}")

    data_text = (ROOT / "data.js").read_text(encoding="utf-8")
    milestone_titles = re.findall(r'^\s*\{year:\d{4},short:"[^"]+",title:"([^"]+)"', history_text, re.MULTILINE)
    missing_milestones = [title for title in milestone_titles if f'title:"{title}"' not in data_text]
    if missing_milestones:
        fail(f"history milestones are missing from curated bibliography: {missing_milestones}")
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
