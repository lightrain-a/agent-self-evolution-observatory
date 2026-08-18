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
    "index": (3, 4, 4, 0),
    "foundations": (2, 3, 2, 0),
    "mechanisms": (3, 4, 6, 0),
    "domains": (3, 4, 3, 0),
    "evaluation": (3, 4, 5, 0),
    "system-overview": (7, 8, 15, 0),
    "research-directions": (4, 5, 9, 0),
    "paper-ideas": (2, 3, 11, 0),
    "experiments": (3, 4, 3, 0),
    "selected-paper": (5, 6, 7, 0),
    "bibliography": (4, 5, 8, 0),
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
                if actual == expected and 'id="page-framework"' in dom:
                    break
                time.sleep(0.5)
            if actual != expected:
                raise AssertionError(f"{page}: expected chapters/toc={expected}, got {actual}")
            if 'id="page-framework"' not in dom:
                raise AssertionError(f"{page}: page framework overview is missing")
            group_headers = re.findall(r'<header class="merged-group-header".*?</header>', dom, re.DOTALL)
            if any(re.search(r'<h2(?:\s|>)', header) for header in group_headers):
                raise AssertionError(f"{page}: merged group is still rendered as H2")
            print(f"{page}: chapters={actual[0]}, toc={actual[1]}/{actual[2]}/{actual[3]}")
        print("PASS")
        print("Eleven canonical pages have page-specific chapter/H2/H3 hierarchy with H4 excluded from the sidebar TOC")
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
