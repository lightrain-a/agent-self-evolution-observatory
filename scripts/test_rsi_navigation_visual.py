#!/usr/bin/env python3
"""Actual Edge/Chromium checks for three-tier chapter nav and two-tier article outlines.

Starts a temporary local static server and closes the browser and server on exit.
Screenshots are QA-only artifacts in tmp/; never part of the deployed website.
"""
from __future__ import annotations
import contextlib
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
OUT = ROOT / "tmp" / "rsi-navigation-hierarchy"
from playwright.sync_api import sync_playwright


def main() -> None:
    if not EDGE.is_file():
        print("SKIP: Microsoft Edge executable unavailable")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=ROOT / "_site",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}/rsi/"
    with contextlib.ExitStack() as stack:
        stack.callback(server.wait)
        stack.callback(server.kill)
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True, executable_path=str(EDGE),
                args=["--disable-extensions", "--disable-background-networking"],
            )
            desktop = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
            page = desktop.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(base + "generalization-learnability.html", wait_until="domcontentloaded")
            page.locator("#research-nav details.nav-group").first.wait_for()
            assert page.locator("#research-nav details.nav-group").count() == 7
            assert page.locator("#research-nav details.nav-subgroup").count() == 7
            assert page.locator(".toc-group").count() == 6
            assert page.locator(".toc-links a.toc-item").count() == 28
            assert page.locator('#research-nav [data-nav-subgroup="evidence-topics"]').evaluate("(x)=>x.open")
            assert page.locator(".toc-group").first.evaluate("(x)=>x.open")
            assert page.locator(".toc-group").nth(1).evaluate("(x)=>!x.open")
            assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), "desktop overflow"
            nav_positions = page.evaluate("""() => {
                const g=document.querySelector('[data-nav-group="evidence"]>.nav-level1');
                const f=document.querySelector('[data-nav-subgroup="evidence-topics"]>.nav-folder-title');
                const a=document.querySelector('[data-nav-subgroup="evidence-topics"] a.nav-level2');
                return [g,f,a].map(e=>Math.round(e.getBoundingClientRect().left));
            }""")
            assert nav_positions[0] < nav_positions[1] < nav_positions[2], f"indentation {nav_positions}"
            page.screenshot(path=str(OUT / "desktop-navigation.png"))
            page.goto(base + "generalization-learnability.html#method-intervention", wait_until="domcontentloaded")
            assert page.locator('a.toc-item[href="#method-intervention"]').evaluate(
                "(a)=>a.closest('details.toc-group').open && a.classList.contains('active')"
            )
            page.locator("#nav-language").click()
            assert page.locator('#research-nav [data-nav-subgroup="evidence-topics"]').evaluate("(x)=>x.open")
            # Soft page swaps preserve the sidebar, and change only the current outline.
            page.evaluate("window.__qaSidebar = document.getElementById('sidebar')")
            page.locator('a.nav-level2[href="experiments.html"]').click()
            page.wait_for_url("**/experiments.html", timeout=15000)
            page.wait_for_function("document.body.dataset.rsiPage === 'experiments' && document.querySelectorAll('.toc-group').length === 4", timeout=15000)
            assert page.evaluate("document.getElementById('sidebar')===window.__qaSidebar"), "sidebar remounted"
            assert page.locator(".toc-group").count() == 4
            assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), "after route overflow"
            mobile = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1, is_mobile=True,
                                         has_touch=True)
            m = mobile.new_page()
            mobile_errors = []
            m.on("pageerror", lambda e: mobile_errors.append(str(e)))
            m.goto(base + "generalization-learnability.html#method-intervention", wait_until="domcontentloaded")
            m.locator("#menu-toggle").click()
            assert m.locator("#sidebar").evaluate("(x)=>x.classList.contains('open')")
            assert m.locator('a.toc-item[href="#method-intervention"]').is_visible()
            m.screenshot(path=str(OUT / "mobile-open-navigation.png"))
            m.locator('a.toc-item[href="#method-intervention"]').click()
            assert not m.locator("#sidebar").evaluate("(x)=>x.classList.contains('open')")
            assert m.evaluate("location.hash") == "#method-intervention"
            # Navigate to a different subsection from the drawer (not merely the existing hash).
            m.locator("#menu-toggle").click()
            m.locator('[data-toc-group="experiment-master"] > summary').click()
            m.locator('a.toc-item[href="#experiment-master"]').click()
            m.wait_for_function("location.hash === '#experiment-master'")
            assert not m.locator("#sidebar").evaluate("(x)=>x.classList.contains('open')")
            assert m.locator('a.toc-item[href="#experiment-master"]').evaluate(
                "(a)=>a.classList.contains('active') && a.closest('details').open"
            ), "mobile deep-link selection must highlight its new outline stage"
            assert m.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), "mobile overflow"
            assert not errors and not mobile_errors, (errors, mobile_errors)
            print({
                "status": "PASS",
                "desktop": "1440x900",
                "mobile": "390x844",
                "site_chapters": 7,
                "topic_folders": 7,
                "generalization_toc_stages": 6,
                "generalization_toc_sections": 28,
                "sidebar_indentation_px": nav_positions,
                "soft_navigation_shell_preserved": True,
                "deep_link_mobile_close": True,
                "screenshots": str(OUT),
            })
            mobile.close()
            desktop.close()
            browser.close()


if __name__ == "__main__":
    main()
