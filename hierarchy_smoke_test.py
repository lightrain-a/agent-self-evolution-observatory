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
    "mechanisms": (3, 3, 1, 0),
    "system-overview": (10, 11, 18, 0),
    "experiment-costs": (0, 7, 0, 0),
    "research-timeline": (0, 0, 0, 0),
    "research-map": (4, 5, 8, 0),
    "research-directions": (3, 4, 1, 0),
    "paper-ideas": (0, 3, 7, 0),
    "experiments": (3, 4, 3, 0),
    "selected-paper": (0, 2, 0, 0),
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
                actual = tuple(execute(session_id, "return [document.querySelectorAll('.page-chapter').length,document.querySelectorAll('.toc-level-2').length,document.querySelectorAll('.toc-level-3').length,document.querySelectorAll('.toc-level-4').length];"))
                needs_framework = page not in {"index", "mechanisms", "research-directions", "paper-ideas", "selected-paper", "research-timeline", "research-map", "experiment-costs"}
                if actual == expected and (not needs_framework or 'id="page-framework"' in dom):
                    break
                time.sleep(0.5)
            if actual != expected:
                raise AssertionError(f"{page}: expected chapters/toc={expected}, got {actual}")
            nav_contract = execute(session_id, """const groups=[...document.querySelectorAll('.sidebar .nav > details.nav-group')].map(d=>({title:(d.querySelector('summary span')?.textContent||'').trim(),open:d.open,links:[...d.querySelectorAll('a.nav-level2')].map(a=>[(a.textContent||'').trim(),a.getAttribute('href')||''])})); const literature=groups.find(g=>g.links.some(x=>x[1]==='bibliography.html'))||null; return {lang:document.documentElement.lang,groups,literatureOpen:!!literature?.open,roleTerm:(document.body.textContent||'').includes('师兄')};""")
            if nav_contract.get("lang") != "zh-CN":
                raise AssertionError(f"{page}: shared sidebar language state drifted: {nav_contract}")
            if [group.get("title") for group in nav_contract.get("groups", [])] != ["开始阅读", "领域图谱", "当前科研", "参考文献"]:
                raise AssertionError(f"{page}: sidebar group names drifted: {nav_contract}")
            expected_group_links = [
                [("研究站首页", "index.html"), ("研究时间轴", "research-timeline.html"), ("科研系统", "system-overview.html"), ("实验成本", "experiment-costs.html")],
                [("定义与边界 · 什么是 Agent 自进化", "foundations.html"), ("领域全景 · 历史与问题", "research-directions.html"), ("领域矩阵 · 机制 × 场景 × 评测", "mechanisms.html"), ("当前研究组合图谱 · A–G", "research-map.html"), ("研究组合 · ResearchItems", "paper-ideas.html")],
                [("论文合集 · 当前 9 篇", "selected-paper.html"), ("① E1 · STRI", "paper-e1.html"), ("② G1 · 时间安全", "paper-g1.html"), ("③ C1 · 记忆传输", "paper-c1.html"), ("④ E2 · 搜索投影", "paper-e2.html"), ("⑤ B1 · 记忆来源", "paper-b1.html"), ("⑥ Paper A · Influence–Fidelity", "paper-a.html"), ("⑦ Paper B · 具身持久记忆", "paper-b.html"), ("⑧ 约束外部性", "paper-agent-constraint.html"), ("⑨ 3D · 关系拓扑", "paper-3d.html")],
                [("文献库 · 主线与研究空白", "bibliography.html")],
            ]
            actual_group_links = [[tuple(link) for link in group.get("links", [])] for group in nav_contract.get("groups", [])]
            if actual_group_links != expected_group_links:
                raise AssertionError(f"{page}: sidebar group membership/order drifted: {actual_group_links}")
            if any(group.get("open") for group in nav_contract.get("groups", [])):
                raise AssertionError(f"{page}: all four sidebar groups must load collapsed by default: {nav_contract}")
            if nav_contract.get("roleTerm"):
                raise AssertionError(f"{page}: public page still renders the forbidden role-specific label")
            current_sidebar = tuple((group.get("title"), tuple(tuple(link) for link in group.get("links", []))) for group in nav_contract.get("groups", []))
            if sidebar_signature is None:
                sidebar_signature = current_sidebar
            elif current_sidebar != sidebar_signature:
                raise AssertionError(f"{page}: sidebar labels/targets differ from the canonical navigation: {current_sidebar}")
            if page not in {"index", "mechanisms", "research-directions", "paper-ideas", "selected-paper", "research-timeline", "research-map", "experiment-costs"} and 'id="page-framework"' not in dom:
                raise AssertionError(f"{page}: page framework overview is missing")
            if page == "index":
                home = execute(session_id, """return {hero:document.querySelectorAll('.home-hero').length,ruleSteps:document.querySelectorAll('.home-rule-flow>div').length,heroActions:document.querySelectorAll('.home-hero-actions a').length,heroStats:document.querySelectorAll('.home-hero-stats .stat').length,portalGroups:document.querySelectorAll('.home-route-section').length,routeCards:document.querySelectorAll('.home-route-card').length,legacyFramework:document.querySelectorAll('.page-architecture,.project-status-strip').length,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2};""")
                if home != {"hero":1,"ruleSteps":4,"heroActions":4,"heroStats":4,"portalGroups":3,"routeCards":9,"legacyFramework":0,"overflow":False}:
                    raise AssertionError(f"index: compact home portal contract failed: {home}")
            if page == "research-timeline":
                ddl = execute(session_id, """return {panel:document.querySelectorAll('#iclr-2027-deadlines').length,cards:document.querySelectorAll('.rt-ddl-card').length,targets:[...document.querySelectorAll('.rt-ddl-card')].map(x=>x.dataset.target||''),dates:[...document.querySelectorAll('.rt-ddl-card>div')].map(x=>x.textContent||''),official:document.querySelector('.rt-ddl-heading>a')?.href||'',overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2};""")
                if ddl.get("panel") != 1 or ddl.get("cards") != 2 or ddl.get("targets") != ["2026-09-19T11:59:00Z","2026-09-26T11:59:00Z"] or not all("北京时间" in x for x in ddl.get("dates", [])) or "iclr.cc/Conferences/2027/AuthorGuidelines" not in ddl.get("official", "") or ddl.get("overflow"):
                    raise AssertionError(f"research-timeline: ICLR 2027 deadline/countdown contract failed: {ddl}")
            if page == "experiment-costs":
                costs = execute(session_id, """return {sections:document.querySelectorAll('.topic-section').length,tables:document.querySelectorAll('.advisor-table-scroll>.matrix').length,toc:[...document.querySelectorAll('#page-toc a')].map(a=>a.textContent.trim()),status:document.querySelectorAll('.project-status-strip').length,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2};""")
                if costs.get("sections") != 7 or costs.get("tables") != 5 or len(costs.get("toc", [])) != 7 or costs.get("status") != 0 or costs.get("overflow"):
                    raise AssertionError(f"experiment-costs: cost ledger layout contract failed: {costs}")
            if page == "paper-ideas":
                portfolio = execute(session_id, """return {paperShelf:document.querySelectorAll('#current-paper-pages .cpp-shelf-card').length,console:document.querySelectorAll('#portfolio-current').length,currentCards:document.querySelectorAll('.portfolio-attention-card').length,categories:document.querySelectorAll('.canonical-category-nav a').length,currentLanes:document.querySelectorAll('.lane-current').length,concludedOpen:document.querySelectorAll('.lane-concluded[open]').length,assetsOpen:document.querySelectorAll('.lane-assets[open]').length,mementoOpen:document.querySelector('#live-memento-paper-design')?.open===true,safetyOpen:document.querySelector('.agent-safety-program-fold')?.open===true,auditOpen:document.querySelector('#portfolio-audit')?.open===true,toc:[...document.querySelectorAll('#page-toc a')].map(a=>a.textContent.trim()),scrollHeight:document.documentElement.scrollHeight,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2};""")
                expected_toc = ["当前需要看什么","A–G 研究组合","更新可靠性与回归控制","记忆、经验与持久知识","评价器、奖励与自纠正","任务生成与课程","工作流与结构演化","世界模型与具身适应","Agent 自进化安全与未来风险","审计与历史"]
                if portfolio.get("paperShelf") != 0 or portfolio.get("console") != 1 or portfolio.get("currentCards") != 6 or portfolio.get("categories") != 7 or portfolio.get("currentLanes") != 7 or portfolio.get("concludedOpen") != 0 or portfolio.get("assetsOpen") != 0 or portfolio.get("mementoOpen") or portfolio.get("safetyOpen") or portfolio.get("auditOpen") or portfolio.get("toc") != expected_toc or portfolio.get("scrollHeight",99999) > 7500 or portfolio.get("overflow"):
                    raise AssertionError(f"paper-ideas: decision-first portfolio contract failed: {portfolio}")
            if page == "selected-paper":
                collection = execute(session_id, """return {cards:document.querySelectorAll('.cpp-collection-card').length,formal:document.querySelectorAll('#formal-paper-collection .cpp-collection-card').length,working:document.querySelectorAll('#working-paper-collection .cpp-collection-card').length,detailSections:document.querySelectorAll('.paper-detail-section,.cpp-origin,.cpp-resource-columns,.cpp-proof-grid').length,toc:[...document.querySelectorAll('#page-toc a')].map(a=>a.textContent.trim()),paper8:[...document.querySelectorAll('.cpp-collection-card header>span')].find(x=>x.textContent.includes('⑧'))?.textContent.trim()||'',overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2};""")
                if collection != {"cards":9,"formal":5,"working":4,"detailSections":0,"toc":["①–⑤ 正式论文","⑥–⑨ 工作论文 / Scientific Object"],"paper8":"⑧ Constraint Externality","overflow":False}:
                    raise AssertionError(f"selected-paper: collection-only contract failed: {collection}")
            if page == "bibliography":
                paper_details = execute(session_id, """const rows=[...document.querySelectorAll('.reference-card .paper-analysis')]; const first=rows[0]||null; const before=rows.filter(x=>x.open).length; if(first) first.querySelector('summary')?.click(); return {total:rows.length,before,firstOpened:!!first?.open};""")
                if paper_details.get("total") != 80 or paper_details.get("before") != 0 or not paper_details.get("firstOpened"):
                    raise AssertionError(f"bibliography: paper details must all start collapsed and remain manually expandable: {paper_details}")
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
        request("POST", f"/session/{session_id}/window/rect", {"width": 500, "height": 844, "x": 0, "y": 0})
        request("POST", f"/session/{session_id}/url", {"url": f"{base}/index.html?mobile-layout-audit=1"})
        time.sleep(1)
        mobile_home = execute(session_id, """return {heroHeight:Math.round(document.querySelector('.home-hero')?.getBoundingClientRect().height||0),overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2,actions:document.querySelectorAll('.home-hero-actions a').length,routeCards:document.querySelectorAll('.home-route-card').length};""")
        if mobile_home.get("overflow") or mobile_home.get("heroHeight", 9999) > 780 or mobile_home.get("actions") != 4 or mobile_home.get("routeCards") != 9:
            raise AssertionError(f"index: mobile home portal is too tall, overflowing, or incomplete: {mobile_home}")
        print("PASS")
        print("Twelve canonical pages have page-specific hierarchy; the consolidated field atlas and home portal pass compact layout checks")
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
