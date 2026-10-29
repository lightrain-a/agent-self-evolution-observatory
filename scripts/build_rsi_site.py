#!/usr/bin/env python3
"""Build the standalone RSI website under _site/rsi (or into a separate output).

This script does not rebuild the Agent site, load its navigation, or require its
runtime assets. GitHub Pages serves the two outputs under / and /rsi/.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

from build_static_site import (
    ROOT,
    assert_no_sensitive_public_text,
    copy_file,
    version_html_assets,
)

SOURCE = ROOT / "rsi"
DEFAULT_OUTPUT = ROOT / "_site" / "rsi"
ALLOWED_FILES = {".html", ".css", ".js", ".json", ".tsv", ".md"}
STANDALONE_ASSETS = {
    "site-base.css": ROOT / "style.css",
    "site-switch.css": ROOT / "site-switch.css",
    "favicon.svg": ROOT / "favicon.svg",
}


def build(output: Path = DEFAULT_OUTPUT) -> Path:
    output = output.resolve()
    if output in {ROOT, ROOT / "_site", SOURCE} or SOURCE in output.parents:
        raise RuntimeError(f"Unsafe RSI output directory: {output}")
    if not (SOURCE / "site-nav.js").is_file():
        raise RuntimeError("Missing generated RSI navigation. Run python3 scripts/build_rsi_research.py")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    copied = []
    for source in sorted(SOURCE.iterdir()):
        if source.is_file() and source.suffix in ALLOWED_FILES:
            target = output / source.name
            copy_file(source, target)
            copied.append(target)

    for name, source in STANDALONE_ASSETS.items():
        target = output / name
        copy_file(source, target)
        copied.append(target)

    build_sha = os.environ.get("GITHUB_SHA", "local").strip() or "local"
    (output / "deployment-manifest.json").write_text(
        json.dumps({
            "schema_version": "1.0",
            "build_sha": build_sha,
            "source": "rsi-standalone-site-build",
        }, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    for html_path in sorted(output.glob("*.html")):
        html_path.write_text(
            version_html_assets(html_path.read_text(encoding="utf-8"), build_sha),
            encoding="utf-8",
        )

    required = (
        "index.html", "timeline.html", "timeline-data.json", "timeline.css", "timeline-view.js",
        "reading-cards.html", "reading-notes.html", "generalization-learnability.html", "generalization-protocol.json", "theory-notes.html", "theory-notes.json", "theory-notes.css", "ideas.html", "curriculum-scale-evidence.html", "idea-prioritization.html", "idea-i5.html", "idea-i6.html", "i8.html", "idea-i9-practice-switching.html", "idea-i10-learning-novelty.html", "idea-i12-prerequisite-bottleneck.html", "i12-experiment-protocol.json", "i2-learner-response-protocol.json", "learning-admission.html", "memory-research-map.html", "learning-signal-bottlenecks.html", "experience-consolidation.html", "learning-rule-evolution.html", "site-nav.js",

        "research.js", "research.css", "compact.css", "timeline-reference.css", "site-base.css", "site-switch.css",
        "favicon.svg", "sources.json", "reading-cards.json", "deployment-manifest.json",
    )
    missing = [name for name in required if not (output / name).is_file()]
    if missing:
        raise RuntimeError("RSI site missing files: " + ", ".join(missing))

    for html_path in sorted(output.glob("*.html")):
        content = html_path.read_text(encoding="utf-8")
        for old_dependency in ('src="../data.js"', 'href="../style.css"', 'href="../favicon.svg"'):
            if old_dependency in content:
                raise RuntimeError(f"RSI page still depends on Agent site: {html_path.name}")
    if any(p.suffix == ".py" for p in output.rglob("*")):
        raise RuntimeError("RSI authoring code leaked into output")
    assert_no_sensitive_public_text(output)
    print(f"Built standalone RSI site: {len(copied)} files in {output}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Standalone destination (default: _site/rsi)")
    args = parser.parse_args()
    build(args.output)
