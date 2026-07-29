#!/usr/bin/env python3
"""Headless browser smoke test for dynamic observatory behavior.

Uses Firefox/geckodriver when available and falls back to Edge/msedgedriver.
The test starts a local static server, executes real page JavaScript, and checks
catalog loading, consolidated hubs, redirects, filtering, and mobile navigation.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
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
    if firefox and geckodriver:
        driver_command = [geckodriver, "--port", str(WEBDRIVER_PORT)]
        capabilities = {
            "capabilities": {
                "alwaysMatch": {
                    "acceptInsecureCerts": True,
                    "moz:firefoxOptions": {"args": ["-headless"]},
                }
            }
        }
    else:
        edge_candidates = [
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        ]
        edge = next((path for path in edge_candidates if path.exists()), None)
        driver_candidates = list((Path.home() / ".cache" / "selenium" / "msedgedriver" / "win64").glob("*/msedgedriver.exe"))
        driver_candidates.sort(key=lambda path: tuple(int(part) for part in path.parent.name.split(".")), reverse=True)
        edgedriver = driver_candidates[0] if driver_candidates else None
        if not edge or not edgedriver:
            raise SystemExit("SKIP: no supported headless browser and driver are available")
        driver_command = [str(edgedriver), f"--port={WEBDRIVER_PORT}"]
        capabilities = {
            "capabilities": {
                "alwaysMatch": {
                    "browserName": "MicrosoftEdge",
                    "acceptInsecureCerts": True,
                    "ms:edgeOptions": {
                        "binary": str(edge),
                        "args": ["--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check"],
                    },
                }
            }
        }

    httpd = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(HTTP_PORT), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    driver = subprocess.Popen(
        driver_command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    session_id = ""
    try:
        last_session_error: Exception | None = None
        for attempt in range(3):
            time.sleep(2 + attempt)
            try:
                session_id = request("POST", "/session", capabilities)["value"]["sessionId"]
                break
            except Exception as error:
                last_session_error = error
                if driver.poll() is not None:
                    driver = subprocess.Popen(driver_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not session_id:
            raise RuntimeError(f"unable to create browser session after retries: {last_session_error}")
        base = f"http://127.0.0.1:{HTTP_PORT}"

        def navigate(path: str, wait: float = 5) -> None:
            request("POST", f"/session/{session_id}/url", {"url": base + path})
            time.sleep(wait)

        def wait_until(script: str, timeout: float = 45, interval: float = 0.5) -> bool:
            deadline = time.time() + timeout
            while time.time() < deadline:
                try:
                    if execute(session_id, script):
                        return True
                except Exception:
                    pass
                time.sleep(interval)
            return False

        navigate("/index.html", 2)
        require(wait_until("return Number(document.querySelector('.stat b')?.textContent || 0) >= 100 && document.querySelectorAll('.citation-missing').length === 0;"), "curated catalog did not finish loading on home")
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
        require(home["nav"] == 9, f"expected 9 canonical navigation targets, got {home['nav']}")
        require(home["figure"], "knowledge-map figure is missing")
        require(home["distribution"] >= 6, "live update-surface distribution is missing")
        require(home["missing"] == 0, "home contains unresolved citations")
        require(home["corpus"] >= 100, "curated literature snapshot did not load")

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
              analyses: document.querySelectorAll('.paper-analysis').length,
              analysisFields: document.querySelectorAll('.paper-analysis-grid > div').length,
              analysisGuide: !!document.querySelector('#paper-reading-schema'),
              rankingGuide: !!document.querySelector('#literature-ranking'),
              sortSelect: document.querySelector('#bibliography-sort')?.value || '',
              rankingStatus: document.querySelector('#citation-ranking-status')?.textContent || '',
              priorityRanks: document.querySelectorAll('.reference-card[data-priority-rank]').length,
              tierBadges: document.querySelectorAll('.reference-card .ranking-tier').length,
              citationBadges: document.querySelectorAll('.reference-card .citation-count').length,
              knownCitations: document.querySelectorAll('.reference-card .citation-count:not(.citation-pending)').length,
              openAnalyses: document.querySelectorAll('.paper-analysis[open]').length,
              analysisLabels: [...document.querySelectorAll('.paper-analysis-grid b')].slice(0,6).map(x=>x.textContent.trim()),
              orderedCards: [...document.querySelectorAll('.reference-card')].map(x=>({tier:Number(x.dataset.tier),citations:Number(x.dataset.citations),year:Number(x.dataset.year)})),
              missing: document.querySelectorAll('.citation-missing').length
            };""",
        )
        require(bibliography["cards"] == 80, "bibliography initial pagination is not 80")
        require(bibliography["loadMore"], "bibliography load-more control is missing")
        require(bibliography["methodMap"] and bibliography["publicationMap"] and bibliography["signalMap"], "one or more bibliography maps are missing")
        require(bibliography["exports"] == 3, "bibliography exports are incomplete")
        require(bibliography["filters"] == 3, "bibliography select filters are incomplete")
        require(bibliography["analyses"] == 80 and bibliography["analysisFields"] == 480, "paper analyses are incomplete on the initial bibliography page")
        require(bibliography["analysisGuide"], "paper analysis reading guide is missing")
        require(bibliography["rankingGuide"] and bibliography["sortSelect"] == "priority", "literature ranking controls are incomplete")
        require(bibliography["rankingStatus"], "citation ranking status is missing")
        require(bibliography["priorityRanks"] == 80 and bibliography["tierBadges"] == 80 and bibliography["citationBadges"] == 80, "ranking metadata is incomplete on bibliography cards")
        require(bibliography["knownCitations"] >= 10, f"deployment citation snapshot is not visible: {bibliography['rankingStatus']}")
        ordered = bibliography["orderedCards"]
        require(all(a["tier"] <= b["tier"] for a, b in zip(ordered, ordered[1:])), "default bibliography order violates publication tiers")
        for a, b in zip(ordered, ordered[1:]):
            if a["tier"] != b["tier"]:
                continue
            require(not (a["citations"] < 0 <= b["citations"]), "known citation count appears after an unmatched paper in the same tier")
            if a["citations"] >= 0 and b["citations"] >= 0:
                require(a["citations"] >= b["citations"], "citation counts are not descending within a publication tier")
            if a["citations"] < 0 and b["citations"] < 0:
                require(a["year"] >= b["year"], "unmatched papers are not sorted by year within a publication tier")
        require(bibliography["analysisLabels"] == ["Problem motivation", "Comparative advantage", "Core intuition", "Why it should work", "Method flow", "Experimental validation"], f"paper analysis order is incorrect: {bibliography['analysisLabels']}")
        require(bibliography["missing"] == 0, "bibliography contains unresolved citations")

        execute(session_id, "const s=document.querySelector('#bibliography-sort'); s.value='citations'; s.dispatchEvent(new Event('change',{bubbles:true}));")
        time.sleep(1)
        citation_sort = execute(session_id, "return {value:document.querySelector('#bibliography-sort')?.value||'', url:location.href, ranks:document.querySelectorAll('.reference-card[data-priority-rank]').length, citations:[...document.querySelectorAll('.reference-card')].map(x=>Number(x.dataset.citations))};")
        require(citation_sort["value"] == "citations" and "sort=citations" in citation_sort["url"] and citation_sort["ranks"] == 80, "citation sort mode did not apply")
        citation_values = citation_sort["citations"]
        seen_unknown = False
        last_known = float("inf")
        for value in citation_values:
            if value < 0:
                seen_unknown = True
            else:
                require(not seen_unknown, "matched citation appears after unmatched record in citation-only mode")
                require(value <= last_known, "citation-only mode is not globally descending")
                last_known = value
        execute(session_id, "const s=document.querySelector('#bibliography-sort'); s.value='priority'; s.dispatchEvent(new Event('change',{bubbles:true}));")
        time.sleep(1)

        navigate("/bibliography.html?paper=visplay-self-evolving-vision-language-models#ref-visplay-self-evolving-vision-language-models", 7)
        specific_analysis = execute(
            session_id,
            """const card=document.querySelector('#ref-visplay-self-evolving-vision-language-models'); return {
              found: !!card,
              open: !!card?.querySelector('.paper-analysis[open]'),
              label: card?.querySelector('.paper-analysis summary small')?.textContent || '',
              fields: card?.querySelectorAll('.paper-analysis-grid > div').length || 0
            };""",
        )
        require(specific_analysis["found"] and specific_analysis["open"], "requested paper analysis did not open")
        require(specific_analysis["fields"] == 6, "requested paper analysis is missing fields")
        require("curated six-part analysis" in specific_analysis["label"] or "人工核验六项分析" in specific_analysis["label"], "paper-specific six-part analysis is not rendered")

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
        require(before == 80 and after > before, f"pagination failed: {before} -> {after}")

        expected_hubs = {
            "/foundations.html": {"groups": 2, "sections": 8},
            "/mechanisms.html": {"groups": 5, "sections": 26},
            "/domains.html": {"groups": 3, "sections": 14},
            "/evaluation.html": {"groups": 3, "sections": 16},
            "/selected-paper.html": {"groups": 4, "sections": 20},
        }
        for page, expected in expected_hubs.items():
            navigate(page, 7)
            result = execute(
                session_id,
                """return {
                  heading: document.querySelector('h1')?.textContent || '',
                  groups: document.querySelectorAll('.merged-group').length,
                  sections: document.querySelectorAll('.topic-section').length,
                  resources: document.querySelectorAll('.live-resource-panel').length,
                  historySrc: document.querySelector('.overview-figure img')?.getAttribute('src') || '',
                  missing: document.querySelectorAll('.citation-missing').length
                };""",
            )
            require(result["heading"], f"{page} has no heading")
            require(result["groups"] == expected["groups"], f"{page} group count mismatch")
            require(result["sections"] >= expected["sections"], f"{page} has too few sections")
            require(result["missing"] == 0, f"{page} contains unresolved citations")
            if page == "/foundations.html":
                require(result["historySrc"].endswith("agent-self-evolution-history-en.svg"), "foundations history SVG is missing")
            if page == "/evaluation.html":
                require(result["resources"] == 2, "evaluation live resource indexes are incomplete")

        navigate("/research-directions.html", 7)
        direction_map = execute(
            session_id,
            """return {
              directions: document.querySelectorAll('.direction-card').length,
              chips: document.querySelectorAll('.idea-chip').length,
              macroCards: document.querySelectorAll('.direction-macro-card').length,
              explanationGrids: document.querySelectorAll('.direction-explanation-grid').length,
              exampleRows: document.querySelectorAll('.direction-running-example tbody tr').length,
              src: document.querySelector('.overview-figure img')?.getAttribute('src') || '',
              text: document.body.textContent || ''
            };""",
        )
        require(direction_map["directions"] == 10, f"expected 10 directions, got {direction_map['directions']}")
        require(direction_map["chips"] == 34, f"expected 34 idea mappings, got {direction_map['chips']}")
        require(direction_map["macroCards"] == 4, "four-question direction primer is incomplete")
        require(direction_map["explanationGrids"] == 10, "plain-language direction explanations are incomplete")
        require(direction_map["exampleRows"] == 10, "running example does not cover all directions")
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
              rows: document.querySelectorAll('#idea-ranking tbody tr').length,
              directionCards: document.querySelectorAll('.direction-rank-card').length,
              trackCards: document.querySelectorAll('.track-rank-card').length,
              arguments: document.querySelectorAll('.idea-argument-grid').length,
              purpose: document.body.textContent.includes('Purpose / problem') || document.body.textContent.includes('目的／要解决的问题'),
              core: document.body.textContent.includes('Core idea') || document.body.textContent.includes('核心思想'),
              rationale: document.body.textContent.includes('Why it is reasonable') || document.body.textContent.includes('合理性'),
              logic: document.body.textContent.includes('Method logic') || document.body.textContent.includes('方法逻辑'),
              importance: document.body.textContent.includes('Why it matters') || document.body.textContent.includes('研究重要性'),
              advantage: document.body.textContent.includes('Comparative advantage') || document.body.textContent.includes('相对优势'),
              thesis: document.body.textContent.includes('One-line thesis') || document.body.textContent.includes('一句话命题'),
              text: document.body.textContent || ''
            };""",
        )
        require(idea_portfolio["directions"] == 10, f"expected 10 idea groups, got {idea_portfolio['directions']}")
        require(idea_portfolio["ideas"] == 34, f"expected 34 concrete ideas, got {idea_portfolio['ideas']}")
        require(idea_portfolio["rows"] == 34, f"expected 34 ranked ideas, got {idea_portfolio['rows']}")
        require(idea_portfolio["directionCards"] == 10, "within-direction rankings are incomplete")
        require(idea_portfolio["trackCards"] == 4, "track rankings are incomplete")
        require(idea_portfolio["arguments"] == 34, "idea reasoning blocks are incomplete")
        require(idea_portfolio["purpose"] and idea_portfolio["core"] and idea_portfolio["rationale"] and idea_portfolio["logic"], "idea cards are missing required reasoning fields")
        require(idea_portfolio["importance"] and idea_portfolio["advantage"], "idea cards are missing importance or comparative advantage")
        require(idea_portfolio["thesis"], "idea cards are missing validation fields")
        require("GroundEvo-Admission" in idea_portfolio["text"] and "PluralLineage-Evo" in idea_portfolio["text"], "idea portfolio is incomplete")

        redirect_checks = {
            "/memory-evolution.html": "mechanisms.html#group-memory-evolution",
            "/direction-board.html": "paper-ideas.html#idea-ranking",
            "/paper-roadmap.html": "selected-paper.html#group-paper-roadmap",
        }
        for old_path, expected_suffix in redirect_checks.items():
            navigate(old_path, 2)
            redirected = execute(session_id, "return location.href")
            require(redirected.endswith(expected_suffix), f"{old_path} did not redirect to {expected_suffix}")

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
