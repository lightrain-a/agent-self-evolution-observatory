#!/usr/bin/env python3
"""Static integrity checks for the consolidated Agent Self-Evolution Observatory."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CANONICAL_PAGES = {
    "index.html": "home",
    "foundations.html": "foundations",
    "mechanisms.html": "mechanisms",
    "domains.html": "domains",
    "evaluation.html": "evaluation",
    "research-directions.html": "research-directions",
    "paper-ideas.html": "paper-ideas",
    "selected-paper.html": "selected-paper",
    "bibliography.html": "bibliography",
}
REDIRECT_PAGES = {
    "taxonomy.html": "foundations.html#group-taxonomy",
    "model-improvement.html": "mechanisms.html#group-model-improvement",
    "prompt-evolution.html": "mechanisms.html#group-prompt-evolution",
    "memory-evolution.html": "mechanisms.html#group-memory-evolution",
    "tool-evolution.html": "mechanisms.html#group-tool-evolution",
    "workflow-evolution.html": "mechanisms.html#group-workflow-evolution",
    "visual-multimodal.html": "domains.html#group-visual-multimodal",
    "gui-web.html": "domains.html#group-gui-web",
    "embodied-world.html": "domains.html#group-embodied-world",
    "evaluation-safety.html": "evaluation.html#group-evaluation-safety",
    "datasets-benchmarks.html": "evaluation.html#group-datasets-benchmarks",
    "repositories.html": "evaluation.html#group-repositories",
    "coverage-method.html": "bibliography.html#group-coverage-method",
    "research-agenda.html": "research-directions.html#group-research-agenda",
    "direction-board.html": "paper-ideas.html#idea-ranking",
    "paper-problem.html": "selected-paper.html#group-paper-problem",
    "paper-experiments.html": "selected-paper.html#group-paper-experiments",
    "paper-roadmap.html": "selected-paper.html#group-paper-roadmap",
    "review-log.html": "selected-paper.html#group-review-log",
}
REQUIRED_STATIC = [
    "CNAME", ".nojekyll", ".gitignore", "style.css", "app.js", "data.js",
    "content-consolidated.js", "redirect.js", "favicon.svg", "robots.txt",
    "sitemap.xml", "site.webmanifest", "404.html", "knowledge-map.svg",
    "agent-self-evolution-directions-en.svg", "agent-self-evolution-directions-zh.svg",
    "portfolio-data.js", "history-figure-data.js", "catalog_audit.py",
    "browser_smoke_test.py", "CHANGELOG.md",
]
PLACEHOLDERS = ["PAGE_CHUNKS", "<!--NEXT", "<!--PAPERS", "<!--SCRIPT"]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    for name in REQUIRED_STATIC:
        if not (ROOT / name).exists():
            fail(f"missing required file {name}")

    html_files = {path.name for path in ROOT.glob("*.html") if path.name != "404.html"}
    expected = set(CANONICAL_PAGES) | set(REDIRECT_PAGES)
    if html_files != expected:
        fail(f"HTML set mismatch; missing={sorted(expected-html_files)}, extra={sorted(html_files-expected)}")

    referenced_scripts: set[str] = set()
    for filename, page_id in CANONICAL_PAGES.items():
        text = (ROOT / filename).read_text(encoding="utf-8")
        match = re.search(r'<body\s+data-page="([^"]+)"', text)
        if not match or match.group(1) != page_id:
            fail(f"{filename} must use data-page={page_id}")
        if 'class="sidebar"' not in text or 'id="site-search"' not in text or 'id="dynamic-page"' not in text:
            fail(f"{filename} is missing canonical page UI")
        scripts = re.findall(r'<script\s+src="([^"]+)"', text)
        if "data.js" not in scripts or "app.js" not in scripts:
            fail(f"{filename} must load data.js and app.js")
        for script in scripts:
            referenced_scripts.add(script)
            if not (ROOT / script).exists():
                fail(f"{filename} references missing script {script}")

    for filename, target in REDIRECT_PAGES.items():
        text = (ROOT / filename).read_text(encoding="utf-8")
        match = re.search(r'<body\s+data-redirect="([^"]+)"', text)
        if not match or match.group(1) != target:
            fail(f"{filename} must redirect to {target}")
        if 'name="robots" content="noindex"' not in text or 'redirect.js' not in text:
            fail(f"{filename} is not a noindex compatibility redirect")
        target_file = target.split("#", 1)[0]
        if target_file not in CANONICAL_PAGES:
            fail(f"{filename} redirects to non-canonical target {target_file}")

    js_files = sorted(ROOT.glob("*.js"))
    for path in js_files:
        subprocess.run(["node", "--check", str(path)], check=True)

    combined = "\n".join(path.read_text(encoding="utf-8") for path in js_files if path.name != "app.js")
    for page_id in CANONICAL_PAGES.values():
        if page_id != "home" and f'"{page_id}"' not in combined and f'.{page_id}' not in combined:
            fail(f"no content configuration found for canonical page {page_id}")

    portfolio_text = (ROOT / "portfolio-data.js").read_text(encoding="utf-8")
    direction_ids = re.findall(r'^\s*id:"([a-z0-9-]+)",\s*code:"D\d+"', portfolio_text, re.MULTILINE)
    idea_rows = re.findall(r'^  \{name:"([^"]+)",directionId:"([a-z0-9-]+)",rank:(\d+)', portfolio_text, re.MULTILINE)
    if len(direction_ids) != 10 or len(set(direction_ids)) != 10:
        fail("portfolio must contain 10 unique research directions")
    if len(idea_rows) != 34:
        fail("portfolio must contain 34 paper ideas")
    names = [name for name, _, _ in idea_rows]
    ranks = sorted(int(rank) for _, _, rank in idea_rows)
    if len(set(names)) != 34 or ranks != list(range(1, 35)):
        fail("paper ideas must have unique names and ranks 1-34")
    mapped_names: list[str] = []
    for block in re.findall(r'ideaIds:\[([^\]]*)\]', portfolio_text):
        mapped_names.extend(re.findall(r'"([^"]+)"', block))
    if sorted(mapped_names) != sorted(names) or len(mapped_names) != len(set(mapped_names)):
        fail("each paper idea must appear exactly once in the direction mapping")

    history_text = (ROOT / "history-figure-data.js").read_text(encoding="utf-8")
    if len(re.findall(r'^\s*\{?\s*code:"P\d"', history_text, re.MULTILINE)) != 6:
        fail("history figure must contain six stages")
    if len(re.findall(r'^\s*\{name:\{en:', history_text, re.MULTILINE)) != 5:
        fail("history figure must contain five capability rows")
    if len(re.findall(r'^\s*\{code:"D\d+"', history_text, re.MULTILINE)) != 10:
        fail("history figure must contain ten research directions")
    milestones = re.findall(r'\{year:\d{4},short:"[^"]+",title:"([^"]+)"', history_text)
    if len(milestones) != 23 or len(set(milestones)) != 23:
        fail("history figure must contain 23 unique published milestones")
    data_text = (ROOT / "data.js").read_text(encoding="utf-8")
    missing_milestones = [title for title in milestones if title not in data_text]
    if missing_milestones:
        fail(f"history milestones missing from curated bibliography: {missing_milestones}")

    nav_targets = sorted(set(re.findall(r'\["([a-z0-9-]+\.html)"', data_text.split("window.SUPPLEMENTAL_PAPERS", 1)[0])))
    if set(nav_targets) != set(CANONICAL_PAGES):
        fail(f"navigation must contain only canonical pages: {nav_targets}")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for filename in CANONICAL_PAGES:
        url = "https://agent-evolution.lightrain.asia/" if filename == "index.html" else f"https://agent-evolution.lightrain.asia/{filename}"
        if url not in sitemap:
            fail(f"sitemap missing canonical page {filename}")
    for filename in REDIRECT_PAGES:
        if f"https://agent-evolution.lightrain.asia/{filename}" in sitemap:
            fail(f"sitemap must not index redirect page {filename}")

    all_checked = [*(ROOT / name for name in CANONICAL_PAGES), ROOT / "404.html", *js_files, ROOT / "style.css"]
    for path in all_checked:
        text = path.read_text(encoding="utf-8")
        for placeholder in PLACEHOLDERS:
            if placeholder in text:
                fail(f"placeholder {placeholder!r} remains in {path.name}")

    cname = (ROOT / "CNAME").read_text(encoding="utf-8").strip()
    if cname != "agent-evolution.lightrain.asia":
        fail(f"unexpected CNAME: {cname}")

    print("PASS")
    print(f"Canonical pages: {len(CANONICAL_PAGES)}")
    print(f"Compatibility redirects: {len(REDIRECT_PAGES)}")
    print(f"JavaScript files checked: {len(js_files)}")
    print(f"Navigation targets: {len(nav_targets)}")


if __name__ == "__main__":
    main()
