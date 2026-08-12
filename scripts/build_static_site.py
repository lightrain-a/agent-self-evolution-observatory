#!/usr/bin/env python3
"""Build the public static site without publishing backend code or private artifacts."""
from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
)
LOCAL_ASSET_RE = re.compile(
    r'(?P<prefix>\b(?:src|href)=["\'])(?P<url>(?!https?://|//|data:|mailto:|#)[^"\']+\.(?:css|js))(?P<suffix>["\'])'
)


def excluded_public_file(name: str) -> bool:
    return name in EXCLUDED_PUBLIC_FILES or any(name.startswith(prefix) for prefix in EXCLUDED_PUBLIC_PREFIXES)


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


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

    required = (
        OUTPUT / "index.html",
        OUTPUT / "paper-ideas.html",
        OUTPUT / "paper-first-incubation-view.js",
        OUTPUT / "experiments.html",
        OUTPUT / "system-overview.html",
        OUTPUT / "app.js",
        OUTPUT / "experiment-terminal-view.js",
        OUTPUT / "experiment-page-view.js",
        OUTPUT / "experiment-four-direction-view.js",
        OUTPUT / "system-overview-view.js",
        OUTPUT / "system-overview-map.js",
        OUTPUT / "system-overview-layers.js",
        OUTPUT / "system-overview-intake.js",
        OUTPUT / "system-overview-closure.js",
        OUTPUT / "system-overview-governance-v2.js",
        OUTPUT / "generated" / "research-governance-v2.js",
        OUTPUT / "generated" / "research-governance-v2.json",
        OUTPUT / "emerging-niche-view.js",
        OUTPUT / "discussion-ready-view.js",
        OUTPUT / "deployment-manifest.json",
        OUTPUT / "generated" / "iclr-low-resource-ideas.js",
        OUTPUT / "generated" / "emerging-niche-policy.js",
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
        OUTPUT / "generated" / "p0-experiment-plan.js",
        OUTPUT / "generated" / "p0-collision-recheck.js",
        OUTPUT / "generated" / "p0-runtime-readiness.js",
    )
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

    print(f"Built {len(copied)} public files in {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    build()
