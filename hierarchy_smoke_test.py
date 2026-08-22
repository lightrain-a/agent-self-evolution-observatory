#!/usr/bin/env python3
"""Render every canonical page in a real headless browser and audit H2/H3/H4 hierarchy."""
from __future__ import annotations

import json
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _free_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


HTTP_PORT = _free_local_port()
WEBDRIVER_PORT = _free_local_port()
EXPECTATIONS = {
    "index": (3, 4, 0, 0),
    "foundations": (2, 3, 2, 0),
    "mechanisms": (3, 4, 6, 0),
    "domains": (3, 4, 3, 0),
    "evaluation": (3, 4, 5, 0),
    "system-overview": (10, 11, 17, 0),
    "research-timeline": (0, 0, 0, 0),
    "research-map": (4, 5, 8, 0),
    "research-directions": (4, 6, 8, 0),
    "paper-ideas": (0, 2, 9, 0),
    "experiments": (3, 4, 3, 0),
    "selected-paper": (4, 5, 22, 0),
    "bibliography": (6, 7, 8, 0),
}


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
    return request(
        "POST",
        f"/session/{session_id}/execute/sync",
        {"script": script, "args": []},
    )["value"]


def browser_runtime() -> tuple[list[str], dict]:
    firefox = shutil.which("firefox")
    geckodriver = shutil.which("geckodriver")
    snap_firefox = Path("/snap/firefox/current/usr/lib/firefox/firefox")
    snap_geckodriver = Path("/snap/firefox/current/usr/lib/firefox/geckodriver")
    if snap_firefox.is_file() and snap_geckodriver.is_file():
        firefox = str(snap_firefox)
        geckodriver = str(snap_geckodriver)
    if firefox and geckodriver:
        return (
            [geckodriver, "--port", str(WEBDRIVER_PORT)],
            {
                "capabilities": {
                    "alwaysMatch": {
                        "acceptInsecureCerts": True,
                        "moz:firefoxOptions": {"binary": firefox, "args": ["-headless"]},
                    }
                }
            },
        )

    edge_candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    edge = next((path for path in edge_candidates if path.exists()), None)
    driver_candidates = list(
        (Path.home() / ".cache" / "selenium" / "msedgedriver" / "win64").glob("*/msedgedriver.exe")
    )
    driver_candidates.sort(
        key=lambda path: tuple(int(part) for part in path.parent.name.split(".")),
        reverse=True,
    )
    edgedriver = driver_candidates[0] if driver_candidates else None
    if not edge or not edgedriver:
        raise SystemExit("SKIP: no supported headless browser and driver are available")
    return (
        [str(edgedriver), f"--port={WEBDRIVER_PORT}"],
        {
            "capabilities": {
                "alwaysMatch": {
                    "browserName": "MicrosoftEdge",
                    "acceptInsecureCerts": True,
                    "ms:edgeOptions": {
                        "binary": str(edge),
                        "args": [
                            "--headless=new",
                            "--disable-gpu",
                            "--no-first-run",
                            "--no-default-browser-check",
                        ],
                    },
                }
            }
        },
    )

def count(dom: str, token: str) -> int:
    return dom.count(token)


def main() -> None:
    driver_command, capabilities = browser_runtime()
    server = subprocess.Popen(
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
                    driver = subprocess.Popen(
                        driver_command,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
        if not session_id:
            raise RuntimeError(f"unable to create browser session after retries: {last_session_error}")

        base = f"http://127.0.0.1:{HTTP_PORT}"
        request("POST", f"/session/{session_id}/url", {"url": f"{base}/index.html"})
        time.sleep(0.5)
        execute(session_id, "localStorage.setItem('agent-evolution-language','zh'); return true;")
        sidebar_signature = None
        for page, expected in EXPECTATIONS.items():
            request(
                "POST",
                f"/session/{session_id}/url",
                {"url": f"{base}/{page}.html"},
            )
            deadline = time.time() + 12
            dom = ""
            actual = (0, 0, 0, 0)
            while time.time() < deadline:
                dom = execute(session_id, "return document.documentElement.outerHTML;")
                actual = (
                    count(dom, 'class="page-chapter"'),
                    count(dom, "toc-level-2"),
                    count(dom, "toc-level-3"),
                    count(dom, "toc-level-4"),
                )
                needs_framework = page not in {"paper-ideas", "selected-paper", "research-timeline", "research-map"}
                if actual == expected and (not needs_framework or 'id="page-framework"' in dom):
                    break
                time.sleep(0.5)
            if actual != expected:
                raise AssertionError(f"{page}: expected chapters/toc={expected}, got {actual}")
            nav_contract = execute(session_id, """const groups=[...document.querySelectorAll('.sidebar .nav > details.nav-group')].map(d=>({title:(d.querySelector('summary span')?.textContent||'').trim(),open:d.open,links:[...d.querySelectorAll('a.nav-level2')].map(a=>[(a.textContent||'').trim(),a.getAttribute('href')||''])})); const literature=groups.find(g=>g.links.some(x=>x[1]==='bibliography.html'))||null; return {lang:document.documentElement.lang,groups,literatureOpen:!!literature?.open,roleTerm:(document.body.textContent||'').includes('师兄')};""")
            if nav_contract.get("lang") != "zh-CN":
                raise AssertionError(f"{page}: shared sidebar language state drifted: {nav_contract}")
            if [group.get("title") for group in nav_contract.get("groups", [])] != ["开始阅读", "领域图谱", "当前科研", "文献"]:
                raise AssertionError(f"{page}: sidebar group names drifted: {nav_contract}")
            if not nav_contract.get("literatureOpen"):
                raise AssertionError(f"{page}: Literature navigation group must remain default-open")
            if nav_contract.get("roleTerm"):
                raise AssertionError(f"{page}: public page still renders the forbidden role-specific label")
            current_sidebar = tuple((group.get("title"), tuple(tuple(link) for link in group.get("links", []))) for group in nav_contract.get("groups", []))
            if sidebar_signature is None:
                sidebar_signature = current_sidebar
            elif current_sidebar != sidebar_signature:
                raise AssertionError(f"{page}: sidebar labels/targets differ from the canonical navigation: {current_sidebar}")
            if page not in {"paper-ideas", "selected-paper", "research-timeline", "research-map"} and 'id="page-framework"' not in dom:
                raise AssertionError(f"{page}: page framework overview is missing")
            if page == "research-map":
                expected_toc = [f"#research-map-{letter}-heading" for letter in "abcdefg"] + ["#formal-publication-lineage-heading"]
                actual_toc = execute(session_id, "return [...document.querySelectorAll('#page-toc .toc-level-3 > a')].map(a=>a.getAttribute('href')); ")
                if actual_toc != expected_toc:
                    raise AssertionError(f"research-map: expected A-G then formal-publication secondary TOC, got {actual_toc}")
                body_order = execute(session_id, "return ['a','b','c','d','e','f','g'].map(x=>document.getElementById('research-map-'+x)?.getBoundingClientRect().top + window.scrollY).concat(document.getElementById('formal-publication-lineage')?.getBoundingClientRect().top + window.scrollY); ")
                if any(body_order[index] >= body_order[index + 1] for index in range(len(body_order) - 1)):
                    raise AssertionError(f"research-map: body order must be A-G first and formal-publication lineage last, got {body_order}")
            group_headers = re.findall(r'<header class="merged-group-header".*?</header>', dom, re.DOTALL)
            if any(re.search(r'<h2(?:\s|>)', header) for header in group_headers):
                raise AssertionError(f"{page}: merged group is still rendered as H2")
            print(f"{page}: chapters={actual[0]}, toc={actual[1]}/{actual[2]}/{actual[3]}")
        print("PASS")
        print("Thirteen canonical pages have page-specific hierarchy, with the read-only timeline intentionally using no chapter/TOC headings")
    finally:
        if session_id:
            try:
                request("DELETE", f"/session/{session_id}")
            except Exception:
                pass
        for process in (driver, server):
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
