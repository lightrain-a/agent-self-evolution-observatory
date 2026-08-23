#!/usr/bin/env python3
"""Build the public static site without publishing backend code or private artifacts."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.public_projection_invariants import validate_public_control_plane

OUTPUT = ROOT / "_site"

ROOT_PATTERNS = (
    "*.html",
    "*.css",
    "*.js",
    "*.svg",
)
ROOT_FILES = (
    "CNAME",
    "robots.txt",
    "sitemap.xml",
    "site.webmanifest",
)
GENERATED_PATTERNS = ("*.js", "*.json")
TEXT_PUBLIC_SUFFIXES = {"", ".html", ".css", ".js", ".json", ".svg", ".txt", ".tex", ".xml", ".webmanifest"}
PUBLIC_REDACTIONS = (
    (re.compile(r"(?<![\w.])(?:[A-Za-z0-9._-]+@)?(?:222\.20\.126\.\d+|10\.42\.8\.\d+):/[^\s\"'`<>#\\]+"), "[internal-remote-path-redacted]"),
    (re.compile(r"(?<![\w.])host\d+:/[^\s\"'`<>#\\]+", re.IGNORECASE), "[internal-remote-path-redacted]"),
    (re.compile(r"/(?:data/(?:wyt|lry)|home/(?:wyt|lry|hdd))/[^\s\"'`<>#\\]+"), "[internal-path-redacted]"),
    (re.compile(r"\b[A-Za-z0-9._-]+@(?:222\.20\.126\.\d+|10\.42\.8\.\d+)\b"), "[internal-ssh-redacted]"),
    (re.compile(r"\b(?:222\.20\.126\.\d+|10\.42\.8\.\d+)\b"), "[internal-host-redacted]"),
    (re.compile(r"\badmin\d+-NF[A-Za-z0-9_-]+\b", re.IGNORECASE), "[internal-hostname-redacted]"),
    (re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"), "[secret-token-redacted]"),
)
EXCLUDED_PUBLIC_FILES = {
    "advisor-priority-view.js",
    "advisor-priority-ideas.js",
    "advisor-priority-ideas.json",
    "advisor-priority-meta-review.json",
}
EXCLUDED_PUBLIC_PREFIXES = (
    "ark-",
    "r31-",
    "r32-final-ideas",
    "r32-targeted-recheck",
    "final-method-refinement-",
    "asset-first-stri-",
)
LOCAL_ASSET_RE = re.compile(
    r'(?P<prefix>\b(?:src|href)=["\'])(?P<url>(?!https?://|//|data:|mailto:|#)[^"\']+\.(?:css|js))(?P<suffix>["\'])'
)


def excluded_public_file(name: str) -> bool:
    return name in EXCLUDED_PUBLIC_FILES or any(name.startswith(prefix) for prefix in EXCLUDED_PUBLIC_PREFIXES)


def redact_public_text(text: str) -> str:
    for pattern, replacement in PUBLIC_REDACTIONS:
        text = pattern.sub(replacement, text)
    return text


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix.lower() in TEXT_PUBLIC_SUFFIXES:
        try:
            text = source.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(source, destination)
        else:
            destination.write_text(redact_public_text(text), encoding="utf-8")
        return
    shutil.copy2(source, destination)


def assert_no_sensitive_public_text(root: Path) -> None:
    leaks: list[str] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_PUBLIC_SUFFIXES):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern, _ in PUBLIC_REDACTIONS:
            match = pattern.search(text)
            if match:
                leaks.append(f"{path.relative_to(root)}: {match.group(0)[:120]}")
                break
    if leaks:
        raise RuntimeError("Sensitive internal text leaked into the static site: " + "; ".join(leaks[:20]))


def cache_guard_script(build_sha: str) -> str:
    encoded_sha = json.dumps(build_sha)
    return f'''<script>window.__SITE_BUILD_SHA__={encoded_sha};(()=>{{const current=String(window.__SITE_BUILD_SHA__||"").slice(0,12);fetch(`deployment-manifest.json?check=${{Date.now()}}`,{{cache:"no-store"}}).then(r=>r.ok?r.json():null).then(m=>{{const latest=String(m?.build_sha||"").slice(0,12);if(!latest||!current||latest===current)return;const u=new URL(location.href);if(u.searchParams.get("_sitev")===latest)return;u.searchParams.set("_sitev",latest);location.replace(u.toString());}}).catch(()=>{{}});}})();</script>'''


def version_html_assets(html: str, build_sha: str) -> str:
    version = build_sha[:12] or "local"

    def replace(match: re.Match[str]) -> str:
        url = match.group("url")
        separator = "&" if "?" in url else "?"
        return f'{match.group("prefix")}{url}{separator}v={version}{match.group("suffix")}'

    html = LOCAL_ASSET_RE.sub(replace, html)
    guard = cache_guard_script(build_sha)
    if "</head>" in html:
        return html.replace("</head>", guard + "</head>", 1)
    return guard + html


def build() -> Path:
    # Refresh only the embedded Paper Acceptance public projection from the
    # append-only canonical ledgers.  Rebuilding the entire Research System here
    # would also recompile unrelated discovery state, which a frontend publish
    # must never do.
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "refresh_paper_acceptance_projection.py")],
        cwd=ROOT,
        check=True,
    )
    # Enumerate ProblemGate-passed paper-design candidates that are canonical/live but
    # intentionally not yet ResearchItems or PaperStates. This closes the pre-promotion
    # control-plane blind spot without granting any scientific/execution authority.
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_pre_researchitem_candidates.py")],
        cwd=ROOT,
        check=True,
    )
    # Recompute the small public current-state ledger from authoritative generated artifacts
    # immediately before copying the site, so every publish uses the same backend truth.
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_current_research_status.py")],
        cwd=ROOT,
        check=True,
    )
    # Project the many append-only research artifacts into one read-only
    # ResearchItem/PaperState model before the frontend is copied. This layer
    # has no scientific or execution authority; it only resolves current-state
    # presentation and cross-entity references.
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_research_items.py")],
        cwd=ROOT,
        check=True,
    )
    # Join the curated literature-gap registry with the freshly projected
    # ResearchItem ledger. This bundle is read-only input for future idea
    # collision/generation and never promotes a gap or authorizes experiments.
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_literature_idea_mining_input.py")],
        cwd=ROOT,
        check=True,
    )
    # Timeline history is authored by the research host, not reconstructed on
    # a GitHub runner that lacks the server-side Research Memory DB. Rebuild
    # only the current dashboard from the committed read-only timeline.
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_research_timeline.py"), "--dashboard-only"],
        cwd=ROOT,
        check=True,
    )
    # PaperRegistry is reader-facing only when every canonical PaperState has a
    # complete Paper Story V3 argument.  This gate is intentionally zero-authority:
    # it cannot change claims or PaperState, but it fails closed before public copy
    # if a new paper omits the scientific-story contract.
    subprocess.run(
        ["node", str(ROOT / "scripts" / "validate_paper_story_contract.js")],
        cwd=ROOT,
        check=True,
    )
    generated = ROOT / "generated"
    paper_registry = json.loads((generated / "paper-registry.json").read_text(encoding="utf-8"))
    projection_errors = validate_public_control_plane(
        research_state=json.loads((generated / "research-items.json").read_text(encoding="utf-8")),
        paper_registry=paper_registry,
        research_system=json.loads((generated / "research-system-state.json").read_text(encoding="utf-8")),
        research_dashboard=json.loads((generated / "research-dashboard.json").read_text(encoding="utf-8")),
        research_memory=json.loads((generated / "research-memory-wiki.json").read_text(encoding="utf-8")),
    )
    if projection_errors:
        raise RuntimeError("public control-plane projection invariant failure before static-site copy: " + "; ".join(projection_errors))
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    copied: set[Path] = set()
    for pattern in ROOT_PATTERNS:
        for source in sorted(ROOT.glob(pattern)):
            if source.is_file() and not excluded_public_file(source.name):
                destination = OUTPUT / source.name
                copy_file(source, destination)
                copied.add(destination)

    for name in ROOT_FILES:
        source = ROOT / name
        if source.exists():
            destination = OUTPUT / name
            copy_file(source, destination)
            copied.add(destination)

    build_sha = os.environ.get("GITHUB_SHA", "local").strip() or "local"
    manifest = {
        "schema_version": "1.0",
        "build_sha": build_sha,
        "source": "frontend-only-pages-build",
    }
    manifest_path = OUTPUT / "deployment-manifest.json"
    manifest_path.write_text(json.dumps(manifest, separators=(",", ":")) + "\n", encoding="utf-8")
    copied.add(manifest_path)

    for html_path in sorted(OUTPUT.glob("*.html")):
        html = html_path.read_text(encoding="utf-8")
        html_path.write_text(version_html_assets(html, build_sha), encoding="utf-8")

    generated_output = OUTPUT / "generated"
    generated_source = ROOT / "generated"
    for pattern in GENERATED_PATTERNS:
        for source in sorted(generated_source.glob(pattern)):
            if source.is_file() and not excluded_public_file(source.name):
                destination = generated_output / source.name
                copy_file(source, destination)
                copied.add(destination)

    downloads_source = ROOT / "downloads"
    downloads_output = OUTPUT / "downloads"
    declared_download_names: set[str] = set()
    for paper in paper_registry.get("papers") or []:
        for ref in (paper.get("downloads") or {}).values():
            if not ref:
                continue
            candidate = Path(str(ref))
            if candidate.is_absolute() or len(candidate.parts) != 2 or candidate.parts[0] != "downloads" or candidate.name in {"", ".", ".."}:
                raise RuntimeError(f"PaperRegistry contains an invalid public download path: {ref}")
            declared_download_names.add(candidate.name)

    legacy_download_names = (
        "STRI-ICLR2027.tex", "STRI-ICLR2027.pdf", "STRI-ICLR2027-source.zip",
        "STRI-ICLR2027-submission-ready-20260821.tex",
        "STRI-ICLR2027-submission-ready-20260821.pdf",
        "STRI-ICLR2027-submission-ready-20260821-source.zip",
        "Agent-Safety-R9-submission-ready-20260822.tex",
        "Agent-Safety-R9-submission-ready-20260822.pdf",
        "Agent-Safety-R9-submission-ready-20260822-source.zip",
        "Agent-Safety-R9.pdf", "Agent-Safety-R9-source.zip", "Agent-Safety-R9-supplement.zip",
        "Agent-Safety-R9-measurement-r6-20260823.pdf",
        "Agent-Safety-R9-measurement-r6-20260823-source.zip",
        "Agent-Safety-R9-measurement-r6-20260823-supplement.zip",
        "Agent-Safety-R9-stanford-round2-r7-20260823.pdf",
        "Agent-Safety-R9-stanford-round2-r7-20260823-source.zip",
        "Agent-Safety-R9-stanford-round2-r7-20260823-supplement.zip",
        "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE.pdf", "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-source.zip",
        "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK.pdf", "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK-source.zip",
        "D2-PAPER-FAILURE-MEMORY-PROVENANCE.pdf", "D2-PAPER-FAILURE-MEMORY-PROVENANCE-source.zip",
        "Agent-Self-Evolution-Observatory-Five-Papers.zip",
    )
    for name in sorted(set(legacy_download_names) | declared_download_names):
        source = downloads_source / name
        if source.exists():
            destination = downloads_output / name
            copy_file(source, destination)
            copied.add(destination)

    required = (
        OUTPUT / "index.html",
        OUTPUT / "paper-ideas.html",
        OUTPUT / "research-timeline.html",
        OUTPUT / "research-map.html",
        OUTPUT / "research-map.css",
        OUTPUT / "research-map-view.js",
        OUTPUT / "research-landscape-data.js",
        OUTPUT / "generated" / "research-items.js",
        OUTPUT / "generated" / "literature-idea-mining-input.json",
        OUTPUT / "generated" / "literature-idea-mining-collision.js",
        OUTPUT / "generated" / "paper-registry.js",
        OUTPUT / "research-directions.html",
        OUTPUT / "research-timeline.css",
        OUTPUT / "research-timeline-view.js",
        OUTPUT / "generated" / "research-timeline.js",
        OUTPUT / "generated" / "research-timeline.json",
        OUTPUT / "paper-first-incubation-view.js",
        OUTPUT / "current-research-status-view.js",
        OUTPUT / "experiments.html",
        OUTPUT / "system-overview.html",
        OUTPUT / "app.js",
        OUTPUT / "experiment-terminal-view.js",
        OUTPUT / "experiment-page-view.js",
        OUTPUT / "experiment-four-direction-view.js",
        OUTPUT / "system-overview-view.js",
        OUTPUT / "system-overview-reader.js",
        OUTPUT / "system-overview-map.js",
        OUTPUT / "system-overview-layers.js",
        OUTPUT / "system-overview-intake.js",
        OUTPUT / "system-overview-closure.js",
        OUTPUT / "system-overview-governance-v2.js",
        OUTPUT / "generated" / "research-governance-v2.js",
        OUTPUT / "generated" / "research-governance-v2.json",
        OUTPUT / "discussion-ready-view.js",
        OUTPUT / "deployment-manifest.json",
        OUTPUT / "generated" / "iclr-low-resource-ideas.js",
        OUTPUT / "generated" / "human-terminal-idea-state.js",
        OUTPUT / "generated" / "p0-admission-state.js",
        OUTPUT / "generated" / "p0-four-direction-iteration.js",
        OUTPUT / "generated" / "persistent-updater-program-final.js",
        OUTPUT / "generated" / "persistent-updater-program-final.json",
        OUTPUT / "generated" / "p0-decision-ledger.js",
        OUTPUT / "generated" / "p0-offline-qualification.js",
        OUTPUT / "generated" / "p0-realizability-suite.js",
        OUTPUT / "generated" / "p0-revived-batch-f0.js",
        OUTPUT / "generated" / "p0-b10-cpu.js",
        OUTPUT / "generated" / "p0-a1-soft-audit-f0.js",
        OUTPUT / "generated" / "p0-a2-evidence-depth-f0.js",
        OUTPUT / "generated" / "p0-a3-substrate-stop.js",
        OUTPUT / "generated" / "p0-a4-composition-cpu.js",
        OUTPUT / "generated" / "p0-a5-history-cpu.js",
        OUTPUT / "generated" / "p0-a6-cpu.js",
        OUTPUT / "generated" / "p0-a7-counterfactual-cpu.js",
        OUTPUT / "generated" / "p0-b2-support-stop.js",
        OUTPUT / "generated" / "p0-b3-interference-cpu.js",
        OUTPUT / "generated" / "p0-b3-fresh-support-stop.js",
        OUTPUT / "generated" / "p0-b3-real-cinteraction.js",
        OUTPUT / "generated" / "p0-b5-applicability-cpu.js",
        OUTPUT / "generated" / "p0-b6-memory-utility-cpu.js",
        OUTPUT / "generated" / "p0-c2-evaluator-cpu.js",
        OUTPUT / "generated" / "p0-d1-minimal-curriculum-cpu.js",
        OUTPUT / "generated" / "p0-e1-edit-table-stop.js",
        OUTPUT / "generated" / "p0-e2-workflow-cpu.js",
        OUTPUT / "generated" / "p0-e3-real-api.js",
        OUTPUT / "generated" / "p0-e3-stateful.js",
        OUTPUT / "generated" / "p0-e4-permission-cpu.js",
        OUTPUT / "generated" / "discussion-ready-ideas.js",
        OUTPUT / "generated" / "paper-first-idea-incubation.js",
        OUTPUT / "generated" / "current-final-ideas.js",
        OUTPUT / "generated" / "final-collision-recheck.js",
        OUTPUT / "generated" / "final-advisor-audit.js",
        OUTPUT / "generated" / "idea-discovery-v5.js",
        OUTPUT / "generated" / "idea-discovery-v53.js",
        OUTPUT / "generated" / "research-system-state.js",
        OUTPUT / "generated" / "current-research-status.js",
        OUTPUT / "generated" / "current-research-status.json",
        OUTPUT / "generated" / "pre-researchitem-candidates.js",
        OUTPUT / "generated" / "pre-researchitem-candidates.json",
        OUTPUT / "generated" / "research-items.js",
        OUTPUT / "generated" / "research-items.json",
        OUTPUT / "generated" / "paper-registry.js",
        OUTPUT / "generated" / "paper-registry.json",
        OUTPUT / "generated" / "paper-first-p0-f0-state.js",
        OUTPUT / "generated" / "paper-first-p0-f0-state.json",
        OUTPUT / "generated" / "paper-first-premature-method-diagnostics.js",
        OUTPUT / "generated" / "paper-first-premature-method-diagnostics.json",
        OUTPUT / "generated" / "p0-experiment-plan.js",
        OUTPUT / "generated" / "p0-collision-recheck.js",
        OUTPUT / "generated" / "p0-runtime-readiness.js",
        OUTPUT / "downloads" / "STRI-ICLR2027.tex",
        OUTPUT / "downloads" / "STRI-ICLR2027.pdf",
        OUTPUT / "downloads" / "STRI-ICLR2027-source.zip",
        OUTPUT / "downloads" / "STRI-ICLR2027-submission-ready-20260821.tex",
        OUTPUT / "downloads" / "STRI-ICLR2027-submission-ready-20260821.pdf",
        OUTPUT / "downloads" / "STRI-ICLR2027-submission-ready-20260821-source.zip",
        OUTPUT / "downloads" / "Agent-Safety-R9-submission-ready-20260822.tex",
        OUTPUT / "downloads" / "Agent-Safety-R9-submission-ready-20260822.pdf",
        OUTPUT / "downloads" / "Agent-Safety-R9-submission-ready-20260822-source.zip",
        OUTPUT / "downloads" / "Agent-Safety-R9.pdf",
        OUTPUT / "downloads" / "Agent-Safety-R9-source.zip",
        OUTPUT / "downloads" / "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE.pdf",
        OUTPUT / "downloads" / "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-source.zip",
        OUTPUT / "downloads" / "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK.pdf",
        OUTPUT / "downloads" / "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK-source.zip",
        OUTPUT / "downloads" / "D2-PAPER-FAILURE-MEMORY-PROVENANCE.pdf",
        OUTPUT / "downloads" / "D2-PAPER-FAILURE-MEMORY-PROVENANCE-source.zip",
    )
    required = required + tuple(OUTPUT / "downloads" / name for name in sorted(declared_download_names))
    missing = [str(path.relative_to(OUTPUT)) for path in required if not path.exists()]
    if missing:
        raise RuntimeError("Static site is missing required files: " + ", ".join(missing))

    forbidden = (
        OUTPUT / ".env",
        OUTPUT / "research_pipeline",
        OUTPUT / "scripts",
    )
    if any(path.exists() for path in forbidden):
        raise RuntimeError("Backend or private files leaked into the static site")
    if list(OUTPUT.rglob("*.enc")) or list(OUTPUT.rglob("*.py")):
        raise RuntimeError("Encrypted artifacts or Python sources leaked into the static site")
    for path in (OUTPUT, OUTPUT / "generated"):
        for source in path.iterdir() if path.exists() else ():
            if source.is_file() and excluded_public_file(source.name):
                raise RuntimeError(f"Backend/internal artifact leaked into the static site: {source.name}")
    assert_no_sensitive_public_text(OUTPUT)

    print(f"Built {len(copied)} public files in {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    build()
