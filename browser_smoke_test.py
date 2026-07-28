#!/usr/bin/env python3
"""Headless Firefox smoke test for dynamic observatory behavior.

Requires Firefox and geckodriver. The test starts a local static server, executes
real page JavaScript, and checks dynamic catalog loading, maps, filtering,
pagination, linked pages, and mobile navigation.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTTP_PORT = 8123
WEBDRIVER_PORT = 4444


def request(method: str, path: str, data: dict | None = None) -> dict:
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        f"http://127.0.0.1:{WEBDRIVER_PORT}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)


def execute(session_id: str, script: str, args: list | None = None):
    payload = {"script": script, "args": args or []}
    return request("POST", f"/session/{session_id}/execute/sync", payload)["value"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    firefox = shutil.which("firefox")
    geckodriver = shutil.which("geckodriver")
    if not firefox or not geckodriver:
        raise SystemExit("SKIP: Firefox or geckodriver is unavailable")

    httpd = subprocess.Popen(
        ["python3", "-m", "http.server", str(HTTP_PORT), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    driver = subprocess.Popen(
        [geckodriver, "--port", str(WEBDRIVER_PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    session_id = ""
    try:
        time.sleep(2)
        capabilities = {
            "capabilities": {
                "alwaysMatch": {
                    "acceptInsecureCerts": True,
                    "moz:firefoxOptions": {"args": ["-headless"]},
                }
            }
        }
        session_id = request("POST", "/session", capabilities)["value"]["sessionId"]
        base = f"http://127.0.0.1:{HTTP_PORT}"

        def navigate(path: str, wait: float = 5) -> None:
            request("POST", f"/session/{session_id}/url", {"url": base + path})
            time.sleep(wait)

        navigate("/index.html", 8)
        home = execute(
            session_id,
            """return {
              nav: document.querySelectorAll('.nav-level2').length,
              figure: !!document.querySelector('.overview-figure img'),
              distribution: document.querySelectorAll('.distribution-row').length,
              missing: document.querySelectorAll('.citation-missing').length,
              corpus: Number(document.querySelector('.stat b')?.textContent || 0)
            };""",
        )
        require(home["nav"] == 24, f"expected 24 navigation targets, got {home['nav']}")
        require(home["figure"], "knowledge-map figure is missing")
        require(home["distribution"] >= 6, "live update-surface distribution is missing")
        require(home["missing"] == 0, "home contains unresolved citations")
        require(home["corpus"] > 500, "live literature corpus did not load")

        navigate("/bibliography.html", 16)
        bibliography = execute(
            session_id,
            """return {
              cards: document.querySelectorAll('.reference-card').length,
              loadMore: !!document.querySelector('#load-more-papers'),
              methodMap: !!document.querySelector('#method-time-map'),
              publicationMap: !!document.querySelector('#publication-status-map'),
              signalMap: !!document.querySelector('#surface-signal-map'),
              exports: document.querySelectorAll('.export-btn').length,
              filters: document.querySelectorAll('.bibliography-controls select').length,
              missing: document.querySelectorAll('.citation-missing').length
            };""",
        )
        require(bibliography["cards"] == 80, "bibliography initial pagination is not 80")
        require(bibliography["loadMore"], "bibliography load-more control is missing")
        require(bibliography["methodMap"] and bibliography["publicationMap"] and bibliography["signalMap"], "one or more bibliography maps are missing")
        require(bibliography["exports"] == 3, "bibliography exports are incomplete")
        require(bibliography["filters"] == 3, "bibliography select filters are incomplete")
        require(bibliography["missing"] == 0, "bibliography contains unresolved citations")

        clicked = execute(
            session_id,
            """const cell=[...document.querySelectorAll('.timeline-cell:not(.publication-cell)')]
              .find(x=>x.textContent.trim()); if(cell){cell.click(); return true;} return false;""",
        )
        require(clicked, "no non-empty method/year cell was found")
        time.sleep(1)
        filtered_url = execute(session_id, "return location.href")
        require("method=" in filtered_url and "year=" in filtered_url, "filter state was not written to URL")

        execute(session_id, "document.querySelector('#reset-filters')?.click();")
        time.sleep(1)
        before = execute(session_id, "return document.querySelectorAll('.reference-card').length")
        execute(session_id, "document.querySelector('#load-more-papers')?.click();")
        time.sleep(1)
        after = execute(session_id, "return document.querySelectorAll('.reference-card').length")
        require(before == 80 and after == 160, f"pagination failed: {before} -> {after}")

        expected_sections = {
            "/datasets-benchmarks.html": 5,
            "/repositories.html": 4,
            "/research-agenda.html": 6,
            "/visual-multimodal.html": 6,
        }
        for page, minimum in expected_sections.items():
            navigate(page, 7)
            result = execute(
                session_id,
                """return {
                  heading: document.querySelector('h1')?.textContent || '',
                  sections: document.querySelectorAll('.topic-section').length,
                  missing: document.querySelectorAll('.citation-missing').length
                };""",
            )
            require(result["heading"], f"{page} has no heading")
            require(result["sections"] >= minimum, f"{page} has too few sections")
            require(result["missing"] == 0, f"{page} contains unresolved citations")

        navigate("/research-directions.html", 7)
        direction_map = execute(
            session_id,
            """return {
              directions: document.querySelectorAll('.direction-card').length,
              chips: document.querySelectorAll('.idea-chip').length,
              src: document.querySelector('.overview-figure img')?.getAttribute('src') || '',
              text: document.body.textContent || ''
            };""",
        )
        require(direction_map["directions"] == 10, f"expected 10 directions, got {direction_map['directions']}")
        require(direction_map["chips"] == 34, f"expected 34 idea mappings, got {direction_map['chips']}")
        require(direction_map["src"].endswith("agent-self-evolution-directions-en.svg"), "English direction figure is not active")
        execute(session_id, "document.querySelector('.language-toggle')?.click();")
        time.sleep(1)
        zh_src = execute(session_id, "return document.querySelector('.overview-figure img')?.getAttribute('src') || ''")
        require(zh_src.endswith("agent-self-evolution-directions-zh.svg"), "Chinese direction figure did not switch")

        navigate("/paper-ideas.html", 7)
        idea_portfolio = execute(
            session_id,
            """return {
              directions: document.querySelectorAll('.idea-direction-section').length,
              ideas: document.querySelectorAll('.idea-plan-card').length,
              thesis: document.body.textContent.includes('Paper thesis') || document.body.textContent.includes('论文命题')
            };""",
        )
        require(idea_portfolio["directions"] == 10, f"expected 10 idea groups, got {idea_portfolio['directions']}")
        require(idea_portfolio["ideas"] == 34, f"expected 34 concrete ideas, got {idea_portfolio['ideas']}")
        require(idea_portfolio["thesis"], "idea cards are missing paper-plan fields")

        navigate("/direction-board.html", 7)
        ranking = execute(
            session_id,
            """return {
              rows: document.querySelectorAll('#global-idea-ranking + table tbody tr, #global-idea-ranking ~ table tbody tr').length,
              directionCards: document.querySelectorAll('.direction-rank-card').length,
              trackCards: document.querySelectorAll('.track-rank-card').length,
              text: document.body.textContent || ''
            };""",
        )
        require(ranking["rows"] == 34, f"expected 34 ranked ideas, got {ranking['rows']}")
        require(ranking["directionCards"] == 10, f"expected 10 within-direction rankings, got {ranking['directionCards']}")
        require(ranking["trackCards"] == 4, f"expected 4 track rankings, got {ranking['trackCards']}")
        require("GroundEvo-Admission" in ranking["text"] and "PluralLineage-Evo" in ranking["text"], "idea ranking is incomplete")

        request("POST", f"/session/{session_id}/window/rect", {"width": 390, "height": 844, "x": 0, "y": 0})
        navigate("/index.html", 5)
        mobile = execute(
            session_id,
            """const toggle=document.querySelector('.mobile-toggle'); const sidebar=document.querySelector('.sidebar');
              const display=getComputedStyle(toggle).display; toggle.click();
              return {display, open:sidebar.classList.contains('open')};""",
        )
        require(mobile["display"] != "none" and mobile["open"], "mobile navigation did not open")

        print("PASS")
        print("Dynamic corpus, maps, pagination, linked pages, citations, and mobile navigation verified")
    finally:
        if session_id:
            try:
                request("DELETE", f"/session/{session_id}")
            except Exception:
                pass
        for process in (driver, httpd):
            try:
                process.terminate()
                process.wait(timeout=5)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass


if __name__ == "__main__":
    main()
