#!/usr/bin/env python3
"""Focused real-browser smoke test for the research-system and idea-decision pages."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTTP_PORT = 8124
WEBDRIVER_PORT = 4445


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


def execute(session_id: str, script: str):
    return request("POST", f"/session/{session_id}/execute/sync", {"script": script, "args": []})["value"]


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def main() -> None:
    firefox, geckodriver = shutil.which("firefox"), shutil.which("geckodriver")
    if not firefox or not geckodriver:
        raise SystemExit("SKIP: Firefox/geckodriver unavailable")
    driver_command = [geckodriver, "--port", str(WEBDRIVER_PORT)]
    capabilities = {"capabilities": {"alwaysMatch": {"acceptInsecureCerts": True, "moz:firefoxOptions": {"args": ["-headless"]}}}}
    httpd = subprocess.Popen([sys.executable, "-m", "http.server", str(HTTP_PORT), "--bind", "127.0.0.1"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    driver = subprocess.Popen(driver_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    session_id = ""
    try:
        for attempt in range(3):
            time.sleep(2 + attempt)
            try:
                session_id = request("POST", "/session", capabilities)["value"]["sessionId"]
                break
            except Exception:
                if driver.poll() is not None:
                    driver = subprocess.Popen(driver_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        require(bool(session_id), "unable to create browser session")
        base = f"http://127.0.0.1:{HTTP_PORT}"

        def navigate(path: str, wait: float = 4) -> None:
            request("POST", f"/session/{session_id}/url", {"url": base + path})
            time.sleep(wait)

        navigate("/system-overview.html")
        system = execute(session_id, """return {
          components: document.querySelectorAll('.system-components-panel tbody tr').length,
          progressItems: document.querySelectorAll('.system-v5-progress span').length,
          text: document.body.textContent || '',
          graphLabel: [...document.querySelectorAll('.system-components-panel tbody tr')].map(x=>x.textContent).find(x=>x.includes('引文与证据图谱')||x.includes('Citation and evidence graph')) || '',
          portfolio: window.DISCUSSION_READY_IDEAS || {},
          stateSummary: window.RESEARCH_SYSTEM_STATE?.summary || {}
        };""")
        require(system["components"] == 9, f"expected nine backend components, got {system['components']}")
        require(system["progressItems"] == 6, f"expected six final-gate progress cells, got {system['progressItems']}")
        require((system["portfolio"].get("count"), system["portfolio"].get("target"), system["portfolio"].get("ready")) == (20, 20, True), f"wrong discussion portfolio: {system['portfolio']}")
        require("20/20" in system["text"] or "20 / 20" in system["text"], "20/20 final-gate progress is not visible")
        require(system["stateSummary"].get("v53_external_pass") == 3, "system state does not expose three v5.3 PASS ideas")
        execute(session_id, "document.querySelector('.language-toggle')?.click();")
        time.sleep(1)
        zh = execute(session_id, "return {graph:[...document.querySelectorAll('.system-components-panel tbody tr')].map(x=>x.textContent).find(x=>x.includes('引文与证据图谱'))||'', text:document.body.textContent||''};")
        require("引文与证据图谱" in zh["graph"], "citation/evidence component is not localized")
        require("20/20" in zh["text"] or "20 / 20" in zh["text"], "Chinese system page lost the final-gate target")

        navigate("/paper-ideas.html", 6)
        ideas = execute(session_id, """return {
          chapters: document.querySelectorAll('.page-chapter').length,
          toc2: document.querySelectorAll('.toc-level-2').length,
          toc3: document.querySelectorAll('.toc-level-3').length,
          toc4: document.querySelectorAll('.toc-level-4').length,
          discussedGroups: document.querySelectorAll('.human-science-group').length,
          discussedCards: document.querySelectorAll('.human-review-idea-card').length,
          readyCards: document.querySelectorAll('.human-review-idea-card.human-tone-ready').length,
          redesignCards: document.querySelectorAll('.human-review-idea-card.human-tone-redesign').length,
          pausedCards: document.querySelectorAll('.human-review-idea-card.human-tone-paused').length,
          feedbackBoxes: document.querySelectorAll('.human-review-idea-card .human-feedback-box').length,
          openDiscussedCards: document.querySelectorAll('.human-review-idea-card[open]').length,
          codes: [...document.querySelectorAll('.human-idea-code')].map(x=>(x.textContent||'').trim()),
          newGroups: document.querySelectorAll('.supplemental-group').length,
          newCards: document.querySelectorAll('.supplemental-idea-card').length,
          openNewCards: document.querySelectorAll('.supplemental-idea-card[open]').length,
          newFinal: [...document.querySelectorAll('.supplemental-idea-card summary small')].filter(x=>/FINAL20|merge audit/.test(x.textContent||'')).length,
          newInspired: [...document.querySelectorAll('.supplemental-idea-card summary small')].filter(x=>/网络灵感|internet-inspired/.test(x.textContent||'')).length,
          mergedMethods: document.querySelectorAll('.human-absorbed-methods').length,
          text: document.body.textContent || ''
        };""")
        require(ideas["chapters"] == 2, f"paper-ideas should have exactly two frontend chapters, got {ideas['chapters']}")
        require((ideas["toc2"], ideas["toc3"], ideas["toc4"]) == (3, 11, 0), f"paper-ideas TOC hierarchy is wrong: {ideas['toc2']}/{ideas['toc3']}/{ideas['toc4']}")
        require(ideas["discussedGroups"] == 6 and ideas["discussedCards"] == 26, f"expected six scientific groups and 26 discussed ideas, got {ideas['discussedGroups']}/{ideas['discussedCards']}")
        require((ideas["readyCards"], ideas["redesignCards"], ideas["pausedCards"]) == (5, 14, 7), f"human-review status counts are wrong: {ideas['readyCards']}/{ideas['redesignCards']}/{ideas['pausedCards']}")
        require(ideas["feedbackBoxes"] == 26, f"every discussed idea must expose the current human feedback, got {ideas['feedbackBoxes']}")
        require(ideas["openDiscussedCards"] == 0 and ideas["openNewCards"] == 0, f"all idea cards must be collapsed by default, got {ideas['openDiscussedCards']}/{ideas['openNewCards']}")
        require(len(ideas["codes"]) == 26 and len(set(ideas["codes"])) == 26, f"group codes are missing or duplicated: {ideas['codes']}")
        require(all(code in ideas["codes"] for code in ("A-1","A-5","B-1","B-7","C-1","D-1","E-1","F-1","F-3")), f"expected stable group codes are missing: {ideas['codes']}")
        require(ideas["newGroups"] == 5 and ideas["newCards"] == 18, f"new-idea staging area is incomplete after FINAL20 merge audit: {ideas['newGroups']}/{ideas['newCards']}")
        require((ideas["newFinal"], ideas["newInspired"]) == (3, 15), f"supplemental provenance counts are wrong after merge: {ideas['newFinal']}/{ideas['newInspired']}")
        require(ideas["mergedMethods"] >= 8, f"merged FINAL method provenance is not visible on discussed ideas: {ideas['mergedMethods']}")
        require(all(marker in ideas["text"] for marker in ("已讨论 Idea","新增 Idea","预算校准的预测性回归面板","有害记忆路径识别与最小隔离修复","E-3","E-4","B-8")), "merged/current idea titles or standalone FINAL codes are missing")
        print("PASS")
        print("Focused system/idea pages verified in a real browser")
    finally:
        if session_id:
            try:
                request("DELETE", f"/session/{session_id}")
            except Exception:
                pass
        driver.terminate(); httpd.terminate()
        try: driver.wait(timeout=5)
        except subprocess.TimeoutExpired: driver.kill()
        try: httpd.wait(timeout=5)
        except subprocess.TimeoutExpired: httpd.kill()


if __name__ == "__main__":
    main()
