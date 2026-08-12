#!/usr/bin/env python3
"""Static integrity checks for the consolidated Agent Self-Evolution Observatory."""
from __future__ import annotations

import json
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
    "system-overview.html": "system-overview",
    "research-directions.html": "research-directions",
    "paper-ideas.html": "paper-ideas",
    "experiments.html": "experiments",
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
    "direction-board.html": "paper-ideas.html#discussed-ideas",
    "paper-problem.html": "selected-paper.html#group-paper-problem",
    "paper-experiments.html": "selected-paper.html#group-paper-experiments",
    "paper-roadmap.html": "selected-paper.html#group-paper-roadmap",
    "review-log.html": "selected-paper.html#group-review-log",
}
REQUIRED_STATIC = [
    "CNAME", "_config.yml", ".gitignore", "style.css", "app.js", "data.js",
    "content-consolidated.js", "redirect.js", "favicon.svg", "robots.txt",
    "sitemap.xml", "site.webmanifest", "404.html", "knowledge-map.svg",
    "agent-self-evolution-directions-en.svg", "agent-self-evolution-directions-zh.svg",
    "agent-self-evolution-history-en.svg", "agent-self-evolution-history-zh.svg",
    "portfolio-data.js", "direction-guide-data.js", "direction-literature-data.js", "page-architecture-data.js", "idea-explanations.js", "idea-comparisons.js",
    "paper-analysis-data.js", "top-paper-analysis-data.js", "citation-ranking-data.js",
    "history-figure-data.js", "catalog_audit.py", "build_citation_cache.py",
    "browser_smoke_test.py", "hierarchy_smoke_test.py", "CHANGELOG.md",
    "content-review-external.js", "generated/iclr-external-reviews.json",
    "machine-school-ideas-view.js", "generated/machine-school-inspired-ideas.json",
    "generated/machine-school-inspired-ideas.js", "generated/machine-school-external-reviews.json",
    "review-localizations.js", "discussion-ready-view.js", "idea-discovery-v5-view.js", "idea-discovery-v4-view.js", "solution-first-ideas-view.js",
    "generated/discussion-ready-ideas.json", "generated/discussion-ready-ideas.js",
    "generated/idea-discovery-v5.json", "generated/idea-discovery-v5.js", "generated/idea-discovery-v5-external-reviews.json",
    "generated/idea-discovery-v51.json", "generated/idea-discovery-v51.js", "generated/idea-discovery-v51-external-reviews.json",
    "generated/idea-discovery-v52.json", "generated/idea-discovery-v52.js", "generated/idea-discovery-v52-external-reviews.json",
    "generated/idea-discovery-v53.json", "generated/idea-discovery-v53.js", "generated/idea-discovery-v53-external-reviews.json",
    "generated/idea-discovery-v4.json", "generated/idea-discovery-v4.js", "generated/idea-discovery-v4-external-reviews.json",
    "generated/idea-discovery-v3.json", "generated/idea-discovery-v3.js", "generated/idea-discovery-v3-external-reviews.json",
    "generated/idea-discovery-v31.json", "generated/idea-discovery-v31.js", "generated/idea-discovery-v31-external-reviews.json",
    "content-system-overview.js", "system-overview-core.js", "system-overview-map.js", "system-overview-layers.js", "system-overview-intake.js", "system-overview-lifecycle.js", "system-overview-preflight.js", "system-overview-operations.js", "system-overview-closure.js", "system-overview-view.js", "system-overview.css", "system-overview-v2.css",
    "idea-lab.css", "emerging-niche-view.js", "generated/emerging-niche-policy.json", "generated/emerging-niche-policy.js",
    "generated/p0-experiment-plan.js", "generated/p0-collision-recheck.js", "generated/p0-runtime-readiness.js",
]
PLACEHOLDERS = ["PAGE_CHUNKS", "<!--NEXT", "<!--PAPERS", "<!--SCRIPT"]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    for name in REQUIRED_STATIC:
        if not (ROOT / name).exists():
            fail(f"missing required file {name}")

    if (ROOT / ".nojekyll").exists():
        fail(".nojekyll must stay absent so the branch-mode Pages fallback honors _config.yml exclusions")
    pages_config = (ROOT / "_config.yml").read_text(encoding="utf-8")
    for marker in (
        "research_pipeline", "scripts", "deploy", "deliveries", "downloads",
        "advisor-priority-view.js", "generated/advisor-priority-ideas.json",
        "browser_smoke_test.py", "emerging_niche_browser_smoke_test.py", "site_smoke_test.py",
    ):
        if marker not in pages_config:
            fail(f"Pages exclusion config is missing {marker}")

    html_files = {path.name for path in ROOT.glob("*.html") if path.name != "404.html"}
    expected = set(CANONICAL_PAGES) | set(REDIRECT_PAGES)
    if html_files != expected:
        fail(f"HTML set mismatch; missing={sorted(expected-html_files)}, extra={sorted(html_files-expected)}")

    referenced_scripts: set[str] = set()
    canonical_scripts: dict[str, list[str]] = {}
    for filename, page_id in CANONICAL_PAGES.items():
        text = (ROOT / filename).read_text(encoding="utf-8")
        match = re.search(r'<body\s+data-page="([^"]+)"', text)
        if not match or match.group(1) != page_id:
            fail(f"{filename} must use data-page={page_id}")
        if 'class="sidebar"' not in text or 'id="site-search"' not in text or 'id="dynamic-page"' not in text:
            fail(f"{filename} is missing canonical page UI")
        scripts = re.findall(r'<script\s+src="([^"]+)"', text)
        canonical_scripts[filename] = scripts
        title = re.search(r'<title>(.*?)</title>', text)
        description = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', text)
        if not title or not title.group(1).strip() or not description or not description.group(1).strip():
            fail(f"{filename} must have a non-empty title and meta description")
        if "data.js" not in scripts or "app.js" not in scripts:
            fail(f"{filename} must load data.js and app.js")
        if "page-architecture-data.js" not in scripts:
            fail(f"{filename} must load page-architecture-data.js")
        for script in scripts:
            referenced_scripts.add(script)
            if not (ROOT / script).exists():
                fail(f"{filename} references missing script {script}")

    current_state_pages = {"index.html", "research-directions.html", "paper-ideas.html", "experiments.html", "selected-paper.html"}
    for filename in current_state_pages:
        if "generated/research-system-state.js" not in canonical_scripts.get(filename, []):
            fail(f"{filename} must load the unified current research-system state")
    stable_reference_pages = {"foundations.html", "mechanisms.html", "domains.html", "evaluation.html", "bibliography.html"}
    for filename in stable_reference_pages:
        if "generated/research-system-state.js" in canonical_scripts.get(filename, []):
            fail(f"{filename} is a stable reference page and must not mix in current P0 state")
    selected_scripts = set(canonical_scripts.get("selected-paper.html", []))
    if {"content-review.js", "content-review-external.js"} & selected_scripts:
        fail("historical selected-paper workspace must not load stale review overrides")
    if "Historical ICLR Paper Workspace" not in (ROOT / "selected-paper.html").read_text(encoding="utf-8"):
        fail("selected-paper must be explicitly labeled as a historical workspace")

    stale_markers = (
        "Selected ICLR Paper Workspace", "选中 ICLR 论文工作区",
        "No executed pilot results yet", "尚无真实 Pilot",
        "minimum pilot evidence remains missing", "仍缺最小 Pilot",
    )
    for filename in CANONICAL_PAGES:
        html = (ROOT / filename).read_text(encoding="utf-8")
        loaded = [html]
        for script in canonical_scripts.get(filename, []):
            path = ROOT / script
            if path.exists() and not script.startswith("generated/"):
                loaded.append(path.read_text(encoding="utf-8", errors="ignore"))
        rendered_source = "\n".join(loaded)
        for marker in stale_markers:
            if marker in rendered_source:
                fail(f"{filename} still exposes stale current-state marker: {marker}")

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
        "paper-ideas": ["discussed-ideas", "new-ideas"],
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

    idea_page = (ROOT / "paper-ideas.html").read_text(encoding="utf-8")
    system_script_order = [
        idea_page.find('src="generated/iclr-low-resource-ideas.js"'),
        idea_page.find('src="generated/machine-school-inspired-ideas.js"'),
        idea_page.find('src="idea-human-review-data.js"'),
        idea_page.find('src="generated/current-final-ideas.js"'),
        idea_page.find('src="content-idea-portfolio.js"'),
        idea_page.find('src="page-architecture-data.js"'),
        idea_page.find('src="app.js"'),
    ]
    if any(position < 0 for position in system_script_order) or system_script_order != sorted(system_script_order):
        fail("paper ideas page must load the human-review idea data and current supplemental candidates before app.js")
    for filename in ("paper-ideas.html", "system-overview.html"):
        page = (ROOT / filename).read_text(encoding="utf-8")
        policy_pos = page.find('src="generated/emerging-niche-policy.js"')
        app_pos = page.find('src="app.js"')
        view_pos = page.find('src="emerging-niche-view.js"')
        if min(policy_pos, app_pos, view_pos) < 0 or not policy_pos < app_pos < view_pos:
            fail(f"{filename} must load ENS policy before app.js and ENS view after app.js")
    niche_policy = json.loads((ROOT / "generated" / "emerging-niche-policy.json").read_text(encoding="utf-8"))
    if niche_policy.get("short_name") != "ENS" or "experiment_stop" not in niche_policy.get("hard_policy", {}).get("never_overrides", []):
        fail("Emerging-Niche policy must remain prioritization-only and subordinate to experiment STOP")
    state_path = ROOT / "generated" / "research-system-state.json"
    if not state_path.exists():
        fail("research-system-state.json is missing")
    research_state = json.loads(state_path.read_text(encoding="utf-8"))
    if research_state.get("health", {}).get("status") != "healthy":
        fail("continuous research system is not healthy")
    summary = research_state.get("summary") or {}
    if summary.get("papers", 0) < 200 or summary.get("evidence_nodes", 0) <= summary.get("papers", 0):
        fail("continuous research evidence graph is incomplete")
    if research_state.get("collision_engine", {}).get("summary", {}).get("pairwise_comparisons") != 406:
        fail("collision engine did not compare all 29 structured ICLR candidates")
    if research_state.get("pilot_registry", {}).get("summary", {}).get("phases") != 78:
        fail("pilot registry must contain P0/P1/P2 for all 26 passed ICLR ideas")
    if (summary.get("solution_children"), summary.get("solution_shortlist"), summary.get("reviewer_repair_children"), summary.get("reviewer_repair_pass")) != (14,10,6,0):
        fail("research-system state must expose both v3 and v3.1 solution-first rounds")
    if (summary.get("v4_candidates"), summary.get("v4_finalists"), summary.get("v4_revivals")) != (28,16,8):
        fail("research-system state must expose the v4 composition and revival round")
    if (summary.get("v5_candidates"), summary.get("v5_finalists"), summary.get("v5_revivals")) != (36,32,8):
        fail("research-system state must expose the v5 wide-search round")
    components = research_state.get("components", [])
    required_component_sources = {"ResearchAgent", "Human terminal ledger", "P0 retrospective economy review", "Unified P0 decision ledger", "Web GPT + domestic-model independent consultation", "Content-addressed AI consultation automation", "FirstResearch / Popper / Co-Scientist / RD-Agent", "Qiushi / Kosmos / MLEvolve", "MLEvolve / InternAgent / AutoResearchClaw", "ResearchClawBench / HackDetect / ScienceAgentBench / AutoLabs", "External-system intake registry", "Biomni / BioMedAgent / PaperQA2", "AutoResearchBench / PaperQA2 / SciNetBench / ScientistOne / verifier calibration", "Advisor paper-first research contract"}
    component_sources = {str(item.get("source") or "") for item in components}
    if len(components) < 27 or not required_component_sources.issubset(component_sources):
        fail(f"research-system state is missing current backend responsibilities: count={len(components)}, missing={sorted(required_component_sources-component_sources)}")
    pre_p0 = research_state.get("pre_p0_identifiability", {})
    if pre_p0.get("summary", {}).get("audited") != 4 or pre_p0.get("summary", {}).get("execution_ready") != 0:
        fail(f"Pre-P0 identifiability state is inconsistent: {pre_p0.get('summary')}")
    if research_state.get("pilot_registry", {}).get("summary", {}).get("p0_authorized") != 0:
        fail("P0 authorization must be zero while all current Pre-P0 contracts are blocked")
    graph_component = next((item for item in components if item.get("source") == "ResearchAgent"), {})
    if graph_component.get("component", {}).get("zh") != "引文与证据图谱":
        fail("citation/evidence component must be bilingual in the backend state")
    external_review_store = json.loads((ROOT / "generated" / "iclr-external-reviews.json").read_text(encoding="utf-8"))
    external_status = external_review_store.get("status", {})
    if external_review_store.get("total_passed_ideas") != 26:
        fail("external review store must track all 26 first-round-passed ICLR ideas")
    if int(external_status.get("reviewed", 0)) != 26 or int(external_status.get("pending", 0)) != 0 or not external_status.get("complete"):
        fail("external review store must report 26 reviewed, zero pending, and complete")
    expected_external_verdicts = {"pass": 4, "revise": 10, "block": 12, "unknown": 0}
    if external_status.get("verdict_counts") != expected_external_verdicts:
        fail(f"unexpected external verdict distribution: {external_status.get('verdict_counts')}")
    iclr_bank = json.loads((ROOT / "generated" / "iclr-low-resource-ideas.json").read_text(encoding="utf-8"))
    iclr_summary = iclr_bank.get("summary", {})
    if (iclr_summary.get("project_web_gpt_reviewed"), iclr_summary.get("project_web_gpt_pending"), iclr_summary.get("project_web_gpt_complete")) != (26, 0, True):
        fail("ICLR bank external-review completion summary is inconsistent")
    if (iclr_summary.get("external_pass"), iclr_summary.get("external_revise"), iclr_summary.get("external_block")) != (4, 10, 12):
        fail("ICLR bank external verdict counts are inconsistent")
    ideas = iclr_bank.get("passed_ideas", [])
    if [idea.get("external_verdict") for idea in ideas[:4]] != ["pass"] * 4:
        fail("R2 ranking must place all four PASS ideas first")
    if sorted(idea.get("programmatic_rank") for idea in ideas) != list(range(1, 27)):
        fail("ICLR bank must preserve all original R1 ranks")

    inspired_bank = json.loads((ROOT / "generated" / "machine-school-inspired-ideas.json").read_text(encoding="utf-8"))
    inspired_summary = inspired_bank.get("summary", {})
    expected_inspired = {
        "raw": 24,
        "internal_pass": 11,
        "internal_revise": 7,
        "internal_reject": 6,
        "external_reviewed": 11,
        "external_pass": 1,
        "external_revise": 7,
        "external_block": 3,
    }
    if any(inspired_summary.get(key) != value for key, value in expected_inspired.items()):
        fail(f"unexpected inspired-bank summary: {inspired_summary}")
    inspired_passed = inspired_bank.get("passed_ideas", [])
    if len(inspired_passed) != 11 or [item.get("external_rank") for item in inspired_passed] != list(range(1, 12)):
        fail("inspired-bank external ranking is incomplete")
    if inspired_passed[0].get("id") != "regression-probe-half-life" or inspired_passed[0].get("final_status") != "pilot-now":
        fail("Regression-Probe Half-Life must be the sole pilot-now inspired idea")
    if len(inspired_bank.get("teacher_shortlist", [])) != 8:
        fail("inspired-bank teacher shortlist must contain eight decision candidates")
    discovery_v4 = json.loads((ROOT / "generated" / "idea-discovery-v4.json").read_text(encoding="utf-8"))
    v4_summary = discovery_v4.get("summary", {})
    if (v4_summary.get("raw_candidates"), v4_summary.get("discussion"), v4_summary.get("revival"), v4_summary.get("repair"), v4_summary.get("component"), v4_summary.get("tournament_finalists")) != (28, 14, 8, 4, 2, 16):
        fail(f"unexpected Idea Discovery v4 structure: {v4_summary}")
    if len(discovery_v4.get("repository_patterns", [])) != 11 or len(discovery_v4.get("workflow_stages", [])) != 9:
        fail("Idea Discovery v4 must expose eleven repository patterns and nine workflow stages")
    if len(discovery_v4.get("all_candidates", [])) != 28 or len(discovery_v4.get("tournament_finalists", [])) != 16:
        fail("Idea Discovery v4 candidate or finalist list is incomplete")
    if any(not item.get("composition_logic", {}).get("zh") or not item.get("mechanism_atoms") for item in discovery_v4.get("all_candidates", [])):
        fail("Idea Discovery v4 contains an unstructured composition")
    if any(not item.get("revival_condition", {}).get("zh") for item in discovery_v4.get("revival", [])):
        fail("Idea Discovery v4 revival branches lack material revival conditions")
    v4_external = json.loads((ROOT / "generated" / "idea-discovery-v4-external-reviews.json").read_text(encoding="utf-8"))
    v4_status = v4_external.get("status", {})
    if (v4_status.get("reviewed"), v4_status.get("pending")) != (v4_summary.get("external_reviewed"), v4_summary.get("external_pending")):
        fail("Idea Discovery v4 review store and public summary disagree")
    expected_v4_verdicts = {"pass": v4_summary.get("external_pass", 0), "revise": v4_summary.get("external_revise", 0), "block": v4_summary.get("external_block", 0), "unknown": v4_summary.get("external_pending", 0)}
    if v4_status.get("verdict_counts") != expected_v4_verdicts:
        fail(f"Idea Discovery v4 external verdict counts are inconsistent: {v4_status.get('verdict_counts')}")

    discovery_v5 = json.loads((ROOT / "generated" / "idea-discovery-v5.json").read_text(encoding="utf-8"))
    v5_summary = discovery_v5.get("summary", {})
    if (v5_summary.get("raw_candidates"), v5_summary.get("finalist"), v5_summary.get("revival"), v5_summary.get("repair"), v5_summary.get("component")) != (36,24,8,2,2):
        fail(f"unexpected Idea Discovery v5 structure: {v5_summary}")
    if len(discovery_v5.get("finalists", [])) != 32 or len(discovery_v5.get("repository_patterns", [])) < 13:
        fail("Idea Discovery v5 finalist pool or repository patterns are incomplete")
    if any(not item.get("necessity_logic", {}).get("zh") or not item.get("strongest_baseline", {}).get("zh") for item in discovery_v5.get("all_candidates", [])):
        fail("Idea Discovery v5 contains a candidate without a simplification/necessity contract")
    v5_external_path = ROOT / "generated" / "idea-discovery-v5-external-reviews.json"
    if v5_external_path.exists():
        v5_external = json.loads(v5_external_path.read_text(encoding="utf-8")); v5_status = v5_external.get("status", {})
        if (v5_status.get("reviewed"), v5_status.get("pending")) != (v5_summary.get("external_reviewed"), v5_summary.get("external_pending")):
            fail("Idea Discovery v5 review store and public summary disagree")
    expected_repair_rounds = {
        "idea-discovery-v51.json": (19, 19, 3),
        "idea-discovery-v52.json": (12, 12, 1),
        "idea-discovery-v53.json": (4, 4, 3),
    }
    for filename, expected in expected_repair_rounds.items():
        payload = json.loads((ROOT / "generated" / filename).read_text(encoding="utf-8"))
        summary = payload.get("summary", {})
        if (summary.get("children"), summary.get("reviewed"), summary.get("pass")) != expected:
            fail(f"unexpected repair-round summary for {filename}: {summary}")
    discussion = json.loads((ROOT / "generated" / "discussion-ready-ideas.json").read_text(encoding="utf-8"))
    if int(discussion.get("count") or 0) < int(discussion.get("target") or 0) or discussion.get("remaining") != 0 or discussion.get("ready") is not True:
        fail(f"strict discussion-ready portfolio has not reached minimum target: {discussion}")

    discovery_v3 = json.loads((ROOT / "generated" / "idea-discovery-v3.json").read_text(encoding="utf-8"))
    v3_summary = discovery_v3.get("summary", {})
    if (v3_summary.get("raw_children"), v3_summary.get("internal_shortlist"), v3_summary.get("repair"), v3_summary.get("external_reviewed"), v3_summary.get("external_revise"), v3_summary.get("external_block"), v3_summary.get("external_pass")) != (14, 10, 4, 10, 6, 4, 0):
        fail(f"unexpected solution-first v3 summary: {v3_summary}")
    if len(discovery_v3.get("repository_patterns", [])) != 7 or len(discovery_v3.get("workflow_stages", [])) != 9 or len(discovery_v3.get("solution_gates", [])) != 5:
        fail("solution-first v3 must preserve seven GitHub patterns, nine workflow stages, and five mechanism gates")
    for item in discovery_v3.get("shortlist", []):
        if not item.get("exact_mechanism", {}).get("zh") or not item.get("independent_ground_truth", {}).get("zh"):
            fail(f"solution-first child is not concretized: {item.get('id')}")

    discovery_v31 = json.loads((ROOT / "generated" / "idea-discovery-v31.json").read_text(encoding="utf-8"))
    v31_summary = discovery_v31.get("summary", {})
    if (v31_summary.get("children"), v31_summary.get("external_reviewed"), v31_summary.get("external_pass"), v31_summary.get("external_revise"), v31_summary.get("external_block")) != (6,6,0,2,4):
        fail(f"unexpected reviewer-repair v3.1 summary: {v31_summary}")
    if any(not item.get("exact_mechanism", {}).get("zh") for item in discovery_v31.get("children", [])):
        fail("v3.1 reviewer-repaired children are not algorithmically specified")

    inspired_external = json.loads((ROOT / "generated" / "machine-school-external-reviews.json").read_text(encoding="utf-8"))
    inspired_status = inspired_external.get("status", {})
    if (inspired_status.get("reviewed"), inspired_status.get("pending"), inspired_status.get("complete")) != (11, 0, True):
        fail("inspired external review must report 11 reviewed and zero pending")
    if inspired_status.get("verdict_counts") != {"pass": 1, "revise": 7, "block": 3, "unknown": 0}:
        fail("inspired external verdict distribution is inconsistent")

    system_page = (ROOT / "system-overview.html").read_text(encoding="utf-8")
    required_system_scripts = [
        "generated/s2-literature.js",
        "generated/research-system-state.js",
        "content-system-overview.js",
        "page-architecture-data.js",
        "system-overview-core.js",
        "system-overview-lifecycle.js",
        "system-overview-preflight.js",
        "system-overview-operations.js",
        "system-overview-view.js",
        "app.js",
    ]
    system_positions = [system_page.find(f'src="{name}"') for name in required_system_scripts]
    if any(position < 0 for position in system_positions) or system_positions != sorted(system_positions):
        fail("system overview must load research-system state and modular renderers before app.js")
    forbidden_system_scripts = ("generated/iclr-low-resource-ideas.js", "generated/machine-school-inspired-ideas.js", "generated/discussion-ready-ideas.js", "generated/idea-discovery-v5.js")
    if any(f'src="{name}"' in system_page for name in forbidden_system_scripts):
        fail("system overview must not load current idea-bank or discussion-pool artifacts")
    system_files = ["system-overview-core.js", "system-overview-map.js", "system-overview-layers.js", "system-overview-intake.js", "system-overview-lifecycle.js", "system-overview-governance-v2.js", "system-overview-preflight.js", "system-overview-operations.js", "system-overview-closure.js", "system-overview-view.js"]
    system_text = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in system_files)
    for marker in ("RESEARCH SYSTEM CONTRACT", "CURRENT SYSTEM MAP", "system-layer-list", "P0 ECONOMY", "PRE-EXPERIMENT COMPILER", "8 / 8", "GATE 3 · IDENTIFIABILITY SUB-AUDIT", "10 / 10", "P0-SYSTEM v2", "system-failure-layer", "MCP-Yu + Experiment Orchestrator", "DECISION → LEARN → PUBLISH"):
        if marker not in system_text:
            fail(f"system overview implementation is missing {marker}")
    system_content = (ROOT / "content-system-overview.js").read_text(encoding="utf-8")
    forbidden_idea_markers = ("主 ICLR Idea Bank", "最终师兄讨论门槛", "Main ICLR idea bank", "Final advisor gate", "paper-ideas.html#discussed-ideas")
    if any(marker in system_text or marker in system_content for marker in forbidden_idea_markers):
        fail("system overview must contain only the research system, not current idea decisions")
    for marker in ("自动执行", "条件自动", "人工控制", "8/8 Pre-Experiment", "10/10 identifiability", "Paper-first 科研生命周期与当前运行状态", "实验蓝图、P0 经济门、协议有效性与编译", "局部验证、方法冻结、全量实验与失败语义", "SCIENTIFIC META-TRACE"):
        if marker not in system_text and marker not in system_content and marker not in (ROOT / "page-architecture-data.js").read_text(encoding="utf-8"):
            fail(f"Chinese research-system documentation is missing {marker}")

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
