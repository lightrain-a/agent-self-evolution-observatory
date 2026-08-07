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
          advisorCards: document.querySelectorAll('.system-advisor-grid article').length,
          advisor: window.ADVISOR_PRIORITY_IDEAS || {},
          text: document.body.textContent || '',
          graphLabel: [...document.querySelectorAll('.system-components-panel tbody tr')].map(x=>x.textContent).find(x=>x.includes('引文与证据图谱')||x.includes('Citation and evidence graph')) || '',
          portfolio: window.DISCUSSION_READY_IDEAS || {},
          stateSummary: window.RESEARCH_SYSTEM_STATE?.summary || {}
        };""")
        require(system["components"] == 10, f"expected ten backend components, got {system['components']}")
        require(system["progressItems"] == 5, f"expected five strict-progress cells, got {system['progressItems']}")
        require(system["advisorCards"] == 8 and len(system["advisor"].get("primary_shortlist", [])) == 8, "system overview must show the eight-direction advisor shortlist")
        require((system["portfolio"].get("count"), system["portfolio"].get("target"), system["portfolio"].get("ready")) == (22, 20, True), f"wrong discussion portfolio: {system['portfolio']}")
        require("22/20" in system["text"], "22/20 progress is not visible")
        require(system["stateSummary"].get("v53_external_pass") == 3, "system state does not expose three v5.3 PASS ideas")
        execute(session_id, "document.querySelector('.language-toggle')?.click();")
        time.sleep(1)
        zh = execute(session_id, "return {graph:[...document.querySelectorAll('.system-components-panel tbody tr')].map(x=>x.textContent).find(x=>x.includes('引文与证据图谱'))||'', text:document.body.textContent||''};")
        require("引文与证据图谱" in zh["graph"], "citation/evidence component is not localized")
        require("22/20" in zh["text"], "Chinese system page lost the strict target")

        navigate("/paper-ideas.html", 6)
        ideas = execute(session_id, """return {
          advisorPanel: document.querySelectorAll('.advisor-priority-panel').length,
          advisorCards: document.querySelectorAll('.advisor-priority-card').length,
          advisorRows: document.querySelectorAll('.advisor-ranking tbody tr').length,
          advisor: window.ADVISOR_PRIORITY_IDEAS || {},
          v5Main: document.querySelectorAll('.v5-panel > .v4-group .v4-idea-card').length,
          v51: document.querySelectorAll('.v51-round .v4-idea-card').length,
          v52: document.querySelectorAll('.v52-round .v4-idea-card').length,
          v53: document.querySelectorAll('.v53-round .v4-idea-card').length,
          v53Pass: document.querySelectorAll('.v53-round .v4-idea-card.verdict-pass').length,
          portfolio: window.DISCUSSION_READY_IDEAS || {},
          v5: window.IDEA_DISCOVERY_V5?.summary || {},
          v51s: window.IDEA_DISCOVERY_V51?.summary || {},
          v52s: window.IDEA_DISCOVERY_V52?.summary || {},
          v53s: window.IDEA_DISCOVERY_V53?.summary || {},
          text: document.body.textContent || ''
        };""")
        require((ideas["advisorPanel"], ideas["advisorCards"], ideas["advisorRows"]) == (1, 8, 22), f"advisor panel counts are wrong: {ideas['advisorPanel']}/{ideas['advisorCards']}/{ideas['advisorRows']}")
        require(ideas["advisor"].get("meta_review_status", {}).get("complete") is True, "advisor comparative meta-review is incomplete")
        require(ideas["v5Main"] == 36, f"expected 36 v5 candidates, got {ideas['v5Main']}")
        require((ideas["v51"], ideas["v52"], ideas["v53"]) == (19, 12, 4), f"repair round counts are wrong: {ideas['v51']}/{ideas['v52']}/{ideas['v53']}")
        require(ideas["v53Pass"] == 3, f"expected three v5.3 PASS cards, got {ideas['v53Pass']}")
        require((ideas["v5"].get("external_pass"), ideas["v51s"].get("pass"), ideas["v52s"].get("pass"), ideas["v53s"].get("pass")) == (6, 3, 1, 3), "v5/v5.x verdict totals are inconsistent")
        require((ideas["portfolio"].get("count"), ideas["portfolio"].get("ready")) == (22, True), "idea page portfolio is stale")
        require("v5.3" in ideas["text"] and "22/20" in ideas["text"], "v5.3 or 22/20 is not visible on idea page")
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
