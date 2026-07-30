#!/usr/bin/env python3
"""Static integrity checks for the consolidated Agent Self-Evolution Observatory."""
from __future__ import annotations

import re
import subprocess
import xml.etree.ElementTree as ET
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
    "agent-self-evolution-history-en.svg", "agent-self-evolution-history-zh.svg",
    "portfolio-data.js", "direction-guide-data.js", "direction-literature-data.js", "page-architecture-data.js", "idea-explanations.js", "idea-comparisons.js",
    "paper-analysis-data.js", "top-paper-analysis-data.js", "citation-ranking-data.js",
    "history-figure-data.js", "catalog_audit.py", "build_citation_cache.py",
    "browser_smoke_test.py", "hierarchy_smoke_test.py", "CHANGELOG.md",
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
        if "page-architecture-data.js" not in scripts:
            fail(f"{filename} must load page-architecture-data.js")
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
    architecture_text = (ROOT / "page-architecture-data.js").read_text(encoding="utf-8")
    expected_chapter_ids = {
        "home": ["understand-field", "select-research", "execute-audit"],
        "foundations": ["boundary-history", "taxonomy-evidence"],
        "mechanisms": ["model-internal", "externalized-experience", "system-level"],
        "domains": ["multimodal-reasoning", "digital-interaction", "physical-world"],
        "evaluation": ["validity-safety", "tasks-benchmarks", "reproducibility"],
        "research-directions": ["orientation", "landscape", "direction-clusters", "long-term-agenda"],
        "paper-ideas": ["iclr-pipeline", "iclr-decision", "historical-dossiers", "cvpr-followup"],
        "selected-paper": ["problem-scope", "evidence-experiments", "narrative-execution", "review-gates"],
        "bibliography": ["coverage-protocol", "ranking-reading", "field-maps", "search-corpus"],
    }
    for page_id, chapter_ids in expected_chapter_ids.items():
        for chapter_id in chapter_ids:
            if architecture_text.count(f'id:"{chapter_id}"') != 1:
                fail(f"page architecture {page_id} is missing unique chapter {chapter_id}")
    app_text = (ROOT / "app.js").read_text(encoding="utf-8")
    for marker in ["renderArchitectureOverview", "renderCustomChapter", "#dynamic-page h4", "toc-level-${node.level}"]:
        if marker not in app_text:
            fail(f"hierarchical renderer is missing {marker}")
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

    direction_guide_text = (ROOT / "direction-guide-data.js").read_text(encoding="utf-8")
    if len(re.findall(r'id:"(?:learn|commit|adapt|govern)"', direction_guide_text)) != 4:
        fail("direction guide must contain four macro questions")
    for direction_id in direction_ids:
        marker = f'"{direction_id}":{{'
        if marker not in direction_guide_text:
            fail(f"direction guide is missing {direction_id}")
        block = direction_guide_text.split(marker, 1)[1].split("\n    }", 1)[0]
        for field in ("plain", "object", "example", "distinction"):
            match = re.search(rf'{field}:\{{en:"([^"]+)",zh:"([^"]+)"\}}', block)
            if not match or not match.group(1).strip() or not match.group(2).strip():
                fail(f"direction {direction_id} is missing bilingual {field}")

    direction_literature_text = (ROOT / "direction-literature-data.js").read_text(encoding="utf-8")
    literature_direction_ids = re.findall(r'^  "([a-z0-9-]+)": \[', direction_literature_text, re.MULTILINE)
    if sorted(literature_direction_ids) != sorted(direction_ids) or len(literature_direction_ids) != 10:
        fail("direction literature must cover all ten research directions exactly once")
    literature_titles = re.findall(r'^      title:"([^"]+)"', direction_literature_text, re.MULTILINE)
    if len(literature_titles) != 30:
        fail("direction literature must contain exactly thirty representative paper records")
    if len(re.findall(r'method:\{en:"[^"]+",zh:"[^"]+"\}', direction_literature_text)) != 30:
        fail("every representative paper must have a bilingual one-line method")
    if len(re.findall(r'fit:\{en:"[^"]+",zh:"[^"]+"\}', direction_literature_text)) != 30:
        fail("every representative paper must explain its bilingual direction fit")
    curated_text = (ROOT / "data.js").read_text(encoding="utf-8")
    missing_direction_papers = [title for title in literature_titles if title not in curated_text]
    if missing_direction_papers:
        fail(f"direction literature papers missing from curated bibliography: {missing_direction_papers}")
    direction_page = (ROOT / "research-directions.html").read_text(encoding="utf-8")
    script_order = [direction_page.find('src="direction-guide-data.js"'), direction_page.find('src="direction-literature-data.js"'), direction_page.find('src="app.js"')]
    if any(position < 0 for position in script_order) or script_order != sorted(script_order):
        fail("research directions page must load direction literature before app.js")

    for figure_name in ("agent-self-evolution-directions-en.svg", "agent-self-evolution-directions-zh.svg"):
        try:
            figure_root = ET.parse(ROOT / figure_name).getroot()
        except ET.ParseError as error:
            fail(f"invalid SVG {figure_name}: {error}")
        if len(figure_root.findall('.//*[@data-paper]')) != 20:
            fail(f"{figure_name} must cite two representative papers for each of ten directions")

    explanations_text = (ROOT / "idea-explanations.js").read_text(encoding="utf-8")
    explanation_blocks = re.findall(r'^  "([^"]+)": \{\n(.*?)(?=^  "[^"]+": \{|^\};)', explanations_text, re.MULTILINE | re.DOTALL)
    explanation_names = [name for name, _ in explanation_blocks]
    if sorted(explanation_names) != sorted(names) or len(explanation_names) != len(set(explanation_names)):
        fail("each paper idea must have exactly one explanation block")
    required_fields = ("purpose", "core", "rationale", "logic")
    for name, block in explanation_blocks:
        for field in required_fields:
            match = re.search(rf'{field}:\{{en:"([^"]+)",zh:"([^"]+)"\}}', block)
            if not match or not match.group(1).strip() or not match.group(2).strip():
                fail(f"idea {name} is missing bilingual {field}")

    comparisons_text = (ROOT / "idea-comparisons.js").read_text(encoding="utf-8")
    comparison_blocks = re.findall(r'^  "([^"]+)": \{\n(.*?)(?=^  "[^"]+": \{|^\};)', comparisons_text, re.MULTILINE | re.DOTALL)
    comparison_names = [name for name, _ in comparison_blocks]
    if sorted(comparison_names) != sorted(names) or len(comparison_names) != len(set(comparison_names)):
        fail("each paper idea must have exactly one importance/advantage block")
    for name, block in comparison_blocks:
        for field in ("importance", "advantage"):
            match = re.search(rf'{field}:\{{en:"([^"]+)",zh:"([^"]+)"\}}', block)
            if not match or not match.group(1).strip() or not match.group(2).strip():
                fail(f"idea {name} is missing bilingual {field}")

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
    for figure_name, method_label in [("agent-self-evolution-history-en.svg", "Update:"), ("agent-self-evolution-history-zh.svg", "更新：")]:
        figure_path = ROOT / figure_name
        try:
            root = ET.parse(figure_path).getroot()
        except ET.ParseError as error:
            fail(f"invalid SVG {figure_name}: {error}")
        milestone_nodes = root.findall(".//*[@data-milestone]")
        figure_text = figure_path.read_text(encoding="utf-8")
        if len(milestone_nodes) != 23:
            fail(f"{figure_name} must contain 23 milestone method cards")
        if figure_text.count(method_label) < 23:
            fail(f"{figure_name} must describe the update target for every milestone")

    paper_analysis_text = (ROOT / "paper-analysis-data.js").read_text(encoding="utf-8")
    method_note_titles = re.findall(r'^  "([^"]+)": \{', paper_analysis_text, re.MULTILINE)
    if len(method_note_titles) < 23 or len(method_note_titles) != len(set(method_note_titles)):
        fail("paper analysis data must contain at least 23 unique paper-specific method notes")
    missing_method_notes = [title for title in method_note_titles if title not in data_text]
    if missing_method_notes:
        fail(f"paper-specific method notes missing from curated bibliography: {missing_method_notes}")

    top_analysis_text = (ROOT / "top-paper-analysis-data.js").read_text(encoding="utf-8")
    top_blocks = re.findall(r'^  "([^"]+)": \{\n(.*?)(?=^  "[^"]+": \{|^\};)', top_analysis_text, re.MULTILINE | re.DOTALL)
    if len(top_blocks) != 24 or len({title for title, _ in top_blocks}) != 24:
        fail("top-paper analysis must contain exactly 24 unique paper analyses")
    for title, block in top_blocks:
        if title not in data_text:
            fail(f"top-paper analysis missing from curated bibliography: {title}")
        for field in ("problem", "advantage", "intuition", "rationale", "flow", "validation"):
            match = re.search(rf'{field}:\{{en:"([^"]+)",zh:"([^"]+)"\}}', block)
            if not match or not match.group(1).strip() or not match.group(2).strip():
                fail(f"top paper {title} is missing bilingual {field}")

    ranking_text = (ROOT / "citation-ranking-data.js").read_text(encoding="utf-8")
    for sort_id in ("priority", "citations", "venue", "recent"):
        if f'id:"{sort_id}"' not in ranking_text:
            fail(f"citation ranking config is missing sort mode {sort_id}")
    if len(re.findall(r'label:"[^"]+",pattern:', ranking_text)) < 15:
        fail("citation ranking config must define at least 15 top-venue patterns")
    role_ids = re.findall(r'\{id:"([a-z-]+)",rank:\d+,title:', ranking_text)
    expected_roles = ["field-overview", "core-evolution", "evaluation-governance", "enabling-mechanism", "agent-foundation", "model-foundation", "adjacent"]
    if role_ids != expected_roles:
        fail(f"reading-role order is incomplete or unstable: {role_ids}")
    if ranking_text.count("citationCount:") < 20 or "snapshotUpdatedAt:" not in ranking_text:
        fail("citation ranking config must contain a dated deployment snapshot for at least 20 core papers")
    bibliography_html = (ROOT / "bibliography.html").read_text(encoding="utf-8")
    required_bibliography_scripts = ["citation-ranking-data.js", "paper-analysis-data.js", "top-paper-analysis-data.js", "app.js"]
    script_positions = [bibliography_html.find(f'src="{name}"') for name in required_bibliography_scripts]
    if any(position < 0 for position in script_positions) or script_positions != sorted(script_positions):
        fail("bibliography must load ranking and analysis scripts before app.js")
    for filename in CANONICAL_PAGES:
        html = (ROOT / filename).read_text(encoding="utf-8")
        if html.find('src="citation-ranking-data.js"') < 0 or html.find('src="citation-ranking-data.js"') > html.find('src="app.js"'):
            fail(f"{filename} must load citation-ranking-data.js before app.js for stable reference numbering")

    app_text = (ROOT / "app.js").read_text(encoding="utf-8")
    for marker in ["Problem motivation", "Comparative advantage", "Core intuition", "Why it should work", "Method flow", "Experimental validation"]:
        if marker not in app_text:
            fail(f"paper-card analysis renderer is missing {marker}")
    for marker in ["sortBibliographyRecords", "publicationTier", "readingRoleInfo", "renderRecommendedPaperGroups", "bibliography-sort", "citation-ranking-status", "citationCount"]:
        if marker not in app_text:
            fail(f"literature ranking implementation is missing {marker}")

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
