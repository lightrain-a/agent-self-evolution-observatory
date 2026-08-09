#!/usr/bin/env python3
"""Render every canonical page in an independent Edge process and audit H2/H3/H4 hierarchy."""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORT = 8124
EXPECTATIONS = {
    "index": (3, 4, 4, 0),
    "foundations": (2, 3, 2, 8),
    "mechanisms": (3, 4, 6, 26),
    "domains": (3, 4, 3, 14),
    "evaluation": (3, 4, 5, 16),
    "system-overview": (2, 3, 10, 0),
    "research-directions": (4, 5, 9, 23),
    "paper-ideas": (4, 5, 3, 0),
    "experiments": (3, 4, 3, 0),
    "selected-paper": (4, 5, 5, 20),
    "bibliography": (4, 5, 8, 6),
}


def find_edge() -> Path | None:
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    return next((path for path in candidates if path.exists()), None)


def render(edge: Path, page: str) -> str:
    with tempfile.TemporaryDirectory(prefix="agent-evolution-hierarchy-") as profile:
        result = subprocess.run(
            [
                str(edge), "--headless=new", "--disable-gpu", "--no-first-run",
                "--no-default-browser-check", f"--user-data-dir={profile}",
                "--virtual-time-budget=7000", "--dump-dom",
                f"http://127.0.0.1:{PORT}/{page}.html",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=60,
            check=True,
        )
    return result.stdout.decode("utf-8", errors="ignore")


def count(dom: str, token: str) -> int:
    return dom.count(token)


def main() -> None:
    edge = find_edge()
    if not edge:
        raise SystemExit("SKIP: Microsoft Edge is unavailable")

    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(1)
        for page, expected in EXPECTATIONS.items():
            dom = render(edge, page)
            actual = (
                count(dom, 'class="page-chapter"'),
                count(dom, "toc-level-2"),
                count(dom, "toc-level-3"),
                count(dom, "toc-level-4"),
            )
            if actual != expected:
                raise AssertionError(f"{page}: expected chapters/toc={expected}, got {actual}")
            if 'id="page-framework"' not in dom:
                raise AssertionError(f"{page}: page framework overview is missing")
            group_headers = re.findall(r'<header class="merged-group-header".*?</header>', dom, re.DOTALL)
            if any(re.search(r'<h2(?:\s|>)', header) for header in group_headers):
                raise AssertionError(f"{page}: merged group is still rendered as H2")
            print(f"{page}: chapters={actual[0]}, toc={actual[1]}/{actual[2]}/{actual[3]}")
        print("PASS")
        print("Eleven canonical pages have page-specific H2/H3/H4 hierarchy")
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    main()
