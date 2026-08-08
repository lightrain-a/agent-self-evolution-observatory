#!/usr/bin/env python3
"""Build the public static site without publishing backend code or private artifacts."""
from __future__ import annotations

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
)


def excluded_public_file(name: str) -> bool:
    return name in EXCLUDED_PUBLIC_FILES or any(name.startswith(prefix) for prefix in EXCLUDED_PUBLIC_PREFIXES)


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


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
        OUTPUT / "system-overview.html",
        OUTPUT / "app.js",
        OUTPUT / "system-overview-view.js",
        OUTPUT / "discussion-ready-view.js",
        OUTPUT / "generated" / "iclr-low-resource-ideas.js",
        OUTPUT / "generated" / "discussion-ready-ideas.js",
        OUTPUT / "generated" / "current-final-ideas.js",
        OUTPUT / "generated" / "final-collision-recheck.js",
        OUTPUT / "generated" / "final-advisor-audit.js",
        OUTPUT / "generated" / "idea-discovery-v5.js",
        OUTPUT / "generated" / "idea-discovery-v53.js",
        OUTPUT / "generated" / "research-system-state.js",
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
