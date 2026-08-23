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
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _free_local_port() -> int:
    # Fixed 8123/4444 ports leak across interrupted MCP/browser sessions and
    # collide with parallel agents. Reserve an ephemeral loopback port instead.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


HTTP_PORT = _free_local_port()
WEBDRIVER_PORT = _free_local_port()


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
    expected_headline=json.loads((ROOT/"generated/current-research-status.json").read_text(encoding="utf-8"))["headline"]
    expected_research_summary=json.loads((ROOT/"generated/research-items.json").read_text(encoding="utf-8"))["summary"]
    expected_dashboard_summary=json.loads((ROOT/"generated/research-dashboard.json").read_text(encoding="utf-8"))["summary"]
    expected_paper_registry=json.loads((ROOT/"generated/paper-registry.json").read_text(encoding="utf-8"))
    expected_registry_summary=expected_paper_registry.get("summary") or {}
    expected_registry_stages={row.get("paper_id"):row.get("paper_stage") for row in (expected_paper_registry.get("papers") or [])}
    expected_registry_titles={row.get("paper_id"):row.get("title") for row in (expected_paper_registry.get("papers") or [])}
    firefox = shutil.which("firefox")
    geckodriver = shutil.which("geckodriver")
    # On the 69 host, the Snap wrapper can fail before WebDriver startup when
    # the user document-portal FUSE mount is stale. Prefer the actual binaries
    # when present; this does not alter browser semantics and avoids wrapper-only
    # namespace failures.
    snap_firefox = Path("/snap/firefox/current/usr/lib/firefox/firefox")
    snap_geckodriver = Path("/snap/firefox/current/usr/lib/firefox/geckodriver")
    if snap_firefox.is_file() and snap_geckodriver.is_file():
        firefox = str(snap_firefox)
        geckodriver = str(snap_geckodriver)
    if firefox and geckodriver:
        driver_command = [geckodriver, "--port", str(WEBDRIVER_PORT)]
        capabilities = {
            "capabilities": {
                "alwaysMatch": {
                    "acceptInsecureCerts": True,
                    "moz:firefoxOptions": {"binary": firefox, "args": ["-headless"]},
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
            wait_cap = float(os.getenv("BROWSER_SMOKE_WAIT_CAP", "0") or 0)
            time.sleep(min(wait, wait_cap) if wait_cap > 0 else wait)

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

        def ensure_language(target: str) -> None:
            toggle = str(execute(session_id, "return document.querySelector('.language-toggle')?.textContent||'';") or "")
            should_click = (target == "zh" and "中文" in toggle) or (target == "en" and "English" in toggle)
            if should_click:
                execute(session_id, "document.querySelector('.language-toggle')?.click();")
                time.sleep(0.7)

        navigate("/index.html", 2)
        require(wait_until("return Number(document.querySelector('.stat b')?.textContent || 0) >= 100 && document.querySelectorAll('.citation-missing').length === 0;"), "curated catalog did not finish loading on home")
        home = execute(
            session_id,
            """return {
              nav: document.querySelectorAll('.nav-level2').length,
              stats: document.querySelectorAll('.stat').length,
              routeCards: document.querySelectorAll('.page-chapter .framework-card').length,
              hero: document.querySelectorAll('.home-hero').length,
              heroActions: document.querySelectorAll('.home-hero-actions a').length,
              ruleSteps: document.querySelectorAll('.home-rule-flow > div').length,
              routeGroups: document.querySelectorAll('.home-route-section').length,
              legacyFramework: document.querySelectorAll('.page-architecture,.project-status-strip').length,
              figure: !!document.querySelector('.overview-figure img'),
              distribution: document.querySelectorAll('.distribution-row').length,
              missing: document.querySelectorAll('.citation-missing').length,
              corpus: Number(document.querySelector('.stat b')?.textContent || 0),
              researchConsole: document.querySelectorAll('.home-research-console').length,
              consoleKpis: document.querySelectorAll('.home-console-kpis > span').length,
              attentionCodes: [...document.querySelectorAll('.home-research-console [data-dashboard-research]')].map(x=>x.dataset.dashboardResearch||''),
              holdRows: document.querySelectorAll('.home-attention-row').length,
              primaryPaper: document.querySelector('.home-primary-paper')?.dataset?.dashboardResearch || '',
              weekHighlights: document.querySelectorAll('.home-week-highlight').length,
              dashboardSummary: window.RESEARCH_DASHBOARD?.summary || {},
              consoleLinks: [...document.querySelectorAll('.home-research-console a')].map(x=>x.getAttribute('href')||'')
            };""",
        )
        require(home["nav"] == 10, f"expected 10 primary navigation targets after consolidating the field atlas, got {home['nav']}")
        require(home["stats"] == 4 and home["routeCards"] == 9 and home["hero"] == 1 and home["heroActions"] == 4 and home["ruleSteps"] == 4 and home["routeGroups"] == 3 and home["legacyFramework"] == 0, f"home compact portal layout is incomplete or duplicated: {home}")
        require(not home["figure"] and home["distribution"] == 0, "home should route readers instead of duplicating the field-history figure or literature distribution")
        require(home["missing"] == 0, "home contains unresolved citations")
        require(home["corpus"] >= 100, "curated literature snapshot did not load")
        require(home["researchConsole"] == 1 and home["consoleKpis"] == 4 and home["primaryPaper"] == "E-7" and home["holdRows"] == 5 and set(home["attentionCodes"]) == {"E-7","G-1","A-3","B-2","B-3","E-1"}, f"home current-research console must expose the six visibility-tracked ResearchItems without treating them as active: {home}")
        require(all(home["dashboardSummary"].get(key) == expected_dashboard_summary.get(key) for key in ("portfolio_objects","research_items","active_research_items","current_attention","paper_ready","holds","launchable_formal_experiments","papers","submission_ready")), f"home dashboard summary must match canonical generated dashboard: rendered={home['dashboardSummary']} expected={expected_dashboard_summary}")
        require(home["dashboardSummary"].get("active_research_items") == 0, f"home must render zero active ResearchItems without synthetic backfill: {home}")
        require(home["weekHighlights"] >= 3 and "research-timeline.html?research=A-3" in home["consoleLinks"] and "selected-paper.html?paper=STRI" in home["consoleLinks"], f"home console must expose weekly provenance plus direct A-3/STRI navigation: {home}")

        navigate("/system-overview.html", 5)
        system_overview = execute(
            session_id,
            """return {
              chapters: document.querySelectorAll('.page-chapter').length,
              toc2: document.querySelectorAll('.toc-level-2').length,
              toc3: document.querySelectorAll('.toc-level-3').length,
              toc4: document.querySelectorAll('.toc-level-4').length,
              stats: document.querySelectorAll('.system-stat').length,
              mapMetrics: document.querySelectorAll('.system-map-metrics > div').length,
              readerChapters: document.querySelectorAll('.reader-roadmap-card').length,
              readerPhases: document.querySelectorAll('.reader-phase').length,
              deepDives: document.querySelectorAll('.system-deep-dive').length,
              authorityCards: document.querySelectorAll('.reader-authority-grid article').length,
              responsibilityLayers: document.querySelectorAll('.system-layer-list article').length,
              componentLayerHeaders: document.querySelectorAll('.system-component-layer').length,
              methodologyControls: document.querySelectorAll('.methodology-control-card').length,
              architectureSummary: window.RESEARCH_SYSTEM_STATE?.system_architecture?.summary || {},
              memorySummary: window.RESEARCH_SYSTEM_STATE?.research_memory_wiki?.summary || {},
              memoryLint: window.RESEARCH_SYSTEM_STATE?.research_memory_wiki?.lint?.summary || {},
              searchClosureSummary: window.RESEARCH_SYSTEM_STATE?.paper_first_search_portfolio_design_adjudication?.summary || {},
              aiCheckpoints: document.querySelectorAll('.system-checkpoint-strip > div').length,
              artifacts: document.querySelectorAll('.system-artifact-table tbody tr').length,
              boundaries: document.querySelectorAll('.system-boundary-card').length,
              boundaryRules: document.querySelectorAll('.system-boundary-card li').length,
              components: document.querySelectorAll('.system-components-panel tbody tr').length,
              lifecycleSteps: document.querySelectorAll('.system-lifecycle-step').length,
              governanceStages: document.querySelectorAll('.governance-stage-card').length,
              outerGates: document.querySelectorAll('.preflight-outer-gate').length,
              preflightGates: document.querySelectorAll('.preflight-gate[data-preflight-key]').length,
              quantWorksheets: document.querySelectorAll('.preflight-quant-grid article').length,
              lessons: document.querySelectorAll('.system-lesson').length,
              failureLayers: document.querySelectorAll('.system-failure-layer').length,
              repairLoops: document.querySelectorAll('.system-repair-loop').length,
              ideaPanels: document.querySelectorAll('.system-idea-card,.system-decision-summary,.system-v5-summary,.system-v4-summary,.system-inspired-summary').length,
              preSummary: window.RESEARCH_SYSTEM_STATE?.pre_p0_identifiability?.summary || {},
              iterationSummary: window.RESEARCH_SYSTEM_STATE?.experiment_iteration?.summary || {},
              v5SummaryPanel: document.querySelectorAll('.system-v5-summary').length,
              v5ProgressItems: document.querySelectorAll('.system-v5-progress span').length,
              v4SummaryPanel: document.querySelectorAll('.system-v4-summary').length,
              v4SummaryCounts: document.querySelectorAll('.system-v4-counts span').length,
              statusGuides: document.querySelectorAll('.system-status-grid article').length,
              evidenceExplorer: document.querySelectorAll('.system-evidence-explorer').length,
              evidenceOptions: document.querySelectorAll('#system-evidence-idea option').length,
              evidenceNodes: document.querySelectorAll('#system-evidence-svg .system-evidence-node').length,
              evidenceLines: document.querySelectorAll('#system-evidence-svg .system-evidence-lines line').length,
              sourceRoutes: document.querySelectorAll('.system-route-grid > div').length,
              mainIdeas: document.querySelectorAll('.system-decision-summary .system-idea-card').length,
              inspiredIdeas: document.querySelectorAll('.system-inspired-summary .system-idea-card').length,
              passIdeas: document.querySelectorAll('.system-decision-summary .verdict-pass').length,
              reviseIdeas: document.querySelectorAll('.system-decision-summary .verdict-revise').length,
              advisorText: /师兄汇报|希望师兄|advisor brief|advisor judgment/i.test(document.body.textContent || ''),
              minVisibleFont: (()=>{const xs=[...document.querySelectorAll('#dynamic-page *')].filter(e=>{const r=e.getBoundingClientRect();return (e.textContent||'').trim()&&r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden'&&e.children.length===0}).map(e=>parseFloat(getComputedStyle(e).fontSize)).filter(Number.isFinite);return xs.length?Math.min(...xs):0})(),
              minVisibleProseFont: (()=>{const xs=[...document.querySelectorAll('#dynamic-page p,#dynamic-page li,#dynamic-page dt,#dynamic-page dd,#dynamic-page td,#dynamic-page th')].filter(e=>{const r=e.getBoundingClientRect();return (e.textContent||'').trim()&&r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden'}).map(e=>parseFloat(getComputedStyle(e).fontSize)).filter(Number.isFinite);return xs.length?Math.min(...xs):0})(),
              links: [...document.querySelectorAll('a')].map(x=>x.getAttribute('href')||''),
              text: document.body.textContent || ''
            };""",
        )
        require(system_overview["chapters"] == 10 and system_overview["readerChapters"] == 0 and system_overview["readerPhases"] == 9 and system_overview["deepDives"] == 4 and system_overview["authorityCards"] == 3, f"system overview reading framework is incomplete after the roadmap was consolidated into the two-row page framework: chapters={system_overview['chapters']} legacy-roadmap={system_overview['readerChapters']} phases={system_overview['readerPhases']} deep={system_overview['deepDives']} authority={system_overview['authorityCards']}")
        require(system_overview["toc2"] == 11 and system_overview["toc3"] >= 10 and system_overview["toc4"] == 0, f"system overview TOC must expose chapter + section hierarchy without machine-level h4 noise: {system_overview['toc2']}/{system_overview['toc3']}/{system_overview['toc4']}")
        require(system_overview["minVisibleFont"] >= 11.5 and system_overview["minVisibleProseFont"] >= 12, f"system overview readability floor regressed: visible={system_overview['minVisibleFont']} prose={system_overview['minVisibleProseFont']}")
        require(system_overview["stats"] == 6, f"research-system hero statistics are incomplete: {system_overview['stats']}")
        require(system_overview["chapters"] == 10 and system_overview["responsibilityLayers"] == 6 and system_overview["lifecycleSteps"] == 21 and system_overview["componentLayerHeaders"] == 6, f"canonical architecture is incomplete: chapters={system_overview['chapters']} layers={system_overview['responsibilityLayers']} stages={system_overview['lifecycleSteps']} component-groups={system_overview['componentLayerHeaders']}")
        require((system_overview["architectureSummary"].get("temporal_stages"),system_overview["architectureSummary"].get("reader_chapters"),system_overview["architectureSummary"].get("reader_stage_coverage"),system_overview["architectureSummary"].get("reader_stage_missing"),system_overview["architectureSummary"].get("reader_stage_duplicates"),system_overview["architectureSummary"].get("reader_stage_extra"),system_overview["architectureSummary"].get("functional_layers"),system_overview["architectureSummary"].get("assigned_components"),system_overview["architectureSummary"].get("unassigned_components"),system_overview["architectureSummary"].get("cross_cutting_controls"),system_overview["architectureSummary"].get("orphan_cross_cutting_controls")) == (21,10,21,0,0,0,6,32,0,3,0), f"backend architecture manifest is stale in browser state: {system_overview['architectureSummary']}")
        require(system_overview["methodologyControls"] == 3 and "Are candidate problems too similar?" in system_overview["text"] and "Freeze the setup before results and check leakage" in system_overview["text"] and "Can another person rerun the key result from scratch?" in system_overview["text"], f"plain-language methodology controls are missing: {system_overview['methodologyControls']}")
        require(system_overview["memorySummary"].get("entries") >= 50 and int(system_overview["memorySummary"].get("scientific_closures") or 0) == int(system_overview["searchClosureSummary"].get("core_principle_dead_ends") or 0) and int(system_overview["memorySummary"].get("search_closures") or 0) + int(system_overview["memorySummary"].get("scientific_closures") or 0) == int(system_overview["searchClosureSummary"].get("shadow_closed_basins") or 0) and system_overview["memorySummary"].get("failure_assets") >= 3 and system_overview["memorySummary"].get("success_assets") >= 3 and system_overview["memoryLint"].get("errors") == 0, f"Research Memory Wiki state is missing or inconsistent with canonical typed closures: summary={system_overview['memorySummary']} canonical={system_overview['searchClosureSummary']} lint={system_overview['memoryLint']}")
        require(("失败 Wiki 已经进入下一轮搜索和实验设计" in system_overview["text"] or "failure wiki is now consumed by the next search and experiment design" in system_overview["text"]) and ("一次运行故障不会污染长期科研记忆" in system_overview["text"] or "One operational glitch cannot poison long-term research memory" in system_overview["text"]), "Research Memory Wiki explanation is missing from System Overview")
        require(system_overview["aiCheckpoints"] == 5, f"AI consultation checkpoint strip is incomplete: {system_overview['aiCheckpoints']}")
        require(system_overview["governanceStages"] == 7, f"P0-System v2 must expose seven scientific stages, got {system_overview['governanceStages']}")
        require(system_overview["outerGates"] == 8 and system_overview["preflightGates"] == 10 and system_overview["quantWorksheets"] == 2, f"Pre-Experiment/identifiability compiler is incomplete: {system_overview['outerGates']}/{system_overview['preflightGates']}/{system_overview['quantWorksheets']}")
        require(system_overview["lessons"] == 6 and system_overview["failureLayers"] == 7 and system_overview["repairLoops"] == 1, f"system learning/diagnosis visualization is incomplete: {system_overview['lessons']}/{system_overview['failureLayers']}/{system_overview['repairLoops']}")
        require(system_overview["artifacts"] >= 14 and system_overview["boundaries"] == 3, f"artifact or automation-boundary documentation is incomplete: {system_overview['artifacts']}/{system_overview['boundaries']}")
        require(system_overview["components"] >= 15, f"backend component table is incomplete: {system_overview['components']}")
        require(system_overview["ideaPanels"] == 0, f"current idea/status panels leaked back into the research-system page: {system_overview['ideaPanels']}")
        require((system_overview["preSummary"].get("audited"), system_overview["preSummary"].get("execution_ready"), system_overview["preSummary"].get("blocked")) == (4,0,4), f"Pre-P0 retrospective state is wrong: {system_overview['preSummary']}")
        iteration = system_overview["iterationSummary"]
        infra_only = iteration.get("diagnosis_counts") == {"infrastructure-error": 4}
        require(iteration.get("scale_up_allowed") == 0 and (iteration.get("belief_updates_allowed") == 1 or (iteration.get("belief_updates_allowed") == 0 and infra_only)), f"experiment diagnosis state is wrong: {iteration}")
        require("Main ICLR idea bank" not in system_overview["text"] and "Final advisor gate" not in system_overview["text"] and "主 ICLR Idea Bank" not in system_overview["text"] and "最终师兄讨论门槛" not in system_overview["text"], "current idea portfolio remains on the research-system page")
        require(("8 / 8" in system_overview["text"] or "8/8" in system_overview["text"]) and ("10 / 10" in system_overview["text"] or "10/10" in system_overview["text"]), "eight-gate Pre-Experiment compiler or ten-check identifiability sub-audit is not visible")
        require("SUPPORT_INSUFFICIENT" in system_overview["text"] and "P0-S" in system_overview["text"] and "P0-M" in system_overview["text"], "P0-System v2 support/method separation is not visible")
        deep_font_floor = execute(session_id, """document.querySelectorAll('.system-deep-dive').forEach(x=>x.open=true); const xs=[...document.querySelectorAll('#dynamic-page *')].filter(e=>{const r=e.getBoundingClientRect();return (e.textContent||'').trim()&&r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden'&&e.children.length===0}).map(e=>parseFloat(getComputedStyle(e).fontSize)).filter(Number.isFinite); return xs.length?Math.min(...xs):0;""")
        require(deep_font_floor >= 11.5, f"expanded machine-detail readability floor regressed: {deep_font_floor}")
        execute(session_id, "document.querySelectorAll('.system-deep-dive').forEach(x=>x.open=false)")
        execute(session_id, "document.querySelector('.language-toggle')?.click();")
        time.sleep(1)
        zh_system = execute(session_id, """return {
          readerText: [...document.querySelectorAll('.reader-roadmap,.reader-phase,.reader-authority')].map(x=>x.textContent||'').join(' '),
          bodyText: document.querySelector('#dynamic-page')?.textContent || '',
          toc2: document.querySelectorAll('.toc-level-2').length,
          toc3: document.querySelectorAll('.toc-level-3').length,
          toc4: document.querySelectorAll('.toc-level-4').length,
          automationText: document.querySelector('.system-automation-panel')?.textContent || '',
          preflightText: [...document.querySelectorAll('.preflight-compiler')].find(x=>x.querySelector('.preflight-gate[data-preflight-key]'))?.textContent || '',
          semanticsText: document.querySelector('.system-semantics')?.textContent || '',
          componentText: document.querySelector('.system-components-panel')?.textContent || '',
          cards: [...document.querySelectorAll('.system-boundary-card,.preflight-gate,.system-failure-layer')].map(x=>({client:x.clientWidth,scroll:x.scrollWidth,text:x.textContent})),
          minVisibleFont: (()=>{const xs=[...document.querySelectorAll('#dynamic-page *')].filter(e=>{const r=e.getBoundingClientRect();return (e.textContent||'').trim()&&r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden'&&e.children.length===0}).map(e=>parseFloat(getComputedStyle(e).fontSize)).filter(Number.isFinite);return xs.length?Math.min(...xs):0})(),
          pageOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2
        };""")
        require((zh_system["toc2"], zh_system["toc4"]) == (11,0) and zh_system["toc3"] >= 10, f"Chinese system TOC must expose second/third-level headings: {zh_system['toc2']}/{zh_system['toc3']}/{zh_system['toc4']}")
        require(zh_system["minVisibleFont"] >= 11.5, f"Chinese system overview readability floor regressed: {zh_system['minVisibleFont']}")
        require(all(marker in zh_system["readerText"] for marker in ("输入","核心判断","阶段产出","先确认异常现象真实存在","最后才做正式科学筛选","这个最小实验无论成功或失败，都会改变下一步吗","方法稳定后冻结版本","论文每条主张是否都有直接证据","自动重放旧案例","谁能提建议、谁能启动实验、谁能改论文结论")), "Chinese reader flow is missing the plain-language research decisions")
        require("自动执行" in zh_system["automationText"] and "条件自动" in zh_system["automationText"] and "人工控制" in zh_system["automationText"], "Chinese automation boundary headings are incomplete")
        require("主张与训练目标对齐" in zh_system["preflightText"] and "方法与最强简化会做出不同决策" in zh_system["preflightText"] and "小样本可拟合性" in zh_system["preflightText"], "Chinese Pre-P0 hard gates are incomplete")
        system_ui_leaks = (
            "CURRENT RESEARCH OS", "EVIDENCE → HYPOTHESIS", "GPU-0 · SURVIVOR GATE",
            "PAPER-FIRST · BEFORE IMPLEMENTATION", "PRINCIPLE · BEFORE EXPERIMENT DESIGN",
            "PROTOCOL VALIDITY · BEFORE SCIENTIFIC INTERPRETATION", "PRE-EXPERIMENT COMPILER · GATE 1–8",
            "DECISION → LEARN → PUBLISH", "SELF-EVOLVING RESEARCH OS",
            "after-evidence-before-hypothesis-freeze", "attack the scientific formulation before implementation begins",
        )
        require(not any(marker in zh_system["bodyText"] for marker in system_ui_leaks), f"Chinese system overview still leaks English flow/UI labels: {[m for m in system_ui_leaks if m in zh_system['bodyText']]}")
        system_ui_zh = ("AI 的任务是指出具体漏洞，不是投票决定通过","代码实现前先写清论文证据结构","先写清为什么应该有效","最后八项启动检查","同一个方向只显示一个当前结论","让系统记住为什么成功、为什么失败","长实验怎样安全启动、断线后怎样继续")
        require(all(marker in zh_system["bodyText"] for marker in system_ui_zh), f"Chinese system overview plain-language labels are incomplete: {[m for m in system_ui_zh if m not in zh_system['bodyText']]}")
        require("先定位失败发生在哪一层" in zh_system["semanticsText"] and "核心原理层" in zh_system["semanticsText"], "Chinese failure-layer semantics are incomplete")
        require("引文与证据图谱" in zh_system["componentText"] and "Citation and evidence graph" not in zh_system["componentText"], "backend component name did not switch to Chinese")
        require(all(card["scroll"] <= card["client"] + 2 for card in zh_system["cards"]), "Chinese system cards overflow horizontally")
        require(not zh_system["pageOverflow"], "Chinese system overview causes page-level horizontal overflow")
        execute(session_id, "document.querySelector('.language-toggle')?.click();")
        time.sleep(1)
        if os.getenv("SYSTEM_OVERVIEW_ONLY") == "1":
            print("SYSTEM_OVERVIEW_SMOKE_OK")
            return

        navigate("/bibliography.html", 16)
        bibliography = execute(
            session_id,
            """return {
              chapters: [...document.querySelectorAll('.page-chapter')].map(x=>x.dataset.chapter||''),
              trustCards: document.querySelectorAll('.bibliography-trust-grid article').length,
              refreshLogs: document.querySelectorAll('.bibliography-refresh-log').length,
              refreshMethods: document.querySelectorAll('.bibliography-refresh-methods article').length,
              refreshChips: document.querySelectorAll('.bibliography-refresh-chips span').length,
              refreshText: document.querySelector('.bibliography-refresh-log')?.textContent || '',
              statusStrips: document.querySelectorAll('.project-status-strip,.field-current-status-strip').length,
              pageOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
              denseReadingLayout: document.querySelectorAll('.bibliography-reading-analysis-grid').length,
              publishedQuestionCards: document.querySelectorAll('.published-question-card').length,
              publishedStories: document.querySelectorAll('.published-direction-story').length,
              publishedComparisonSections: document.querySelectorAll('.published-comparison-section').length,
              publishedQuickReads: document.querySelectorAll('.published-paper-quickread').length,
              publishedQuickFields: document.querySelectorAll('.published-paper-quickread-grid > div').length,
              publishedAudit: window.publishedLiteratureAudit?.() || {published:0,byTier:{},byDirection:{},missingQuick:['audit missing'],missingMustReadEvidence:['audit missing']},
              publishedEvidenceSources: document.querySelectorAll('.published-evidence-source').length,
              publishedIntro: document.querySelector('.published-spine-intro')?.textContent || '',
              ideaMiningDirections: document.querySelectorAll('.idea-mining-direction').length,
              ideaMiningSections: document.querySelectorAll('.idea-mining-body > section').length,
              ideaMiningInternal: document.querySelectorAll('.idea-mining-internal').length,
              ideaMiningInternalLinks: document.querySelectorAll('.idea-mining-internal a').length,
              ideaMiningIntersections: document.querySelectorAll('.idea-intersection-card').length,
              ideaMiningContract: document.querySelectorAll('.idea-candidate-contract article').length,
              ideaMiningPriority: document.querySelectorAll('.idea-mining-priority-strip > a').length,
              ideaMiningAudit: window.literatureIdeaMiningAudit?.() || {directions:0,intersections:0,contract:0,missing:['audit missing'],high:[],crowded:[]},
              ideaMiningText: document.querySelector('[data-chapter="idea-mining"]')?.textContent || '',
              mapGuideCards: document.querySelectorAll('.bibliography-map-guide-grid article').length,
              readingPathCards: document.querySelectorAll('.bibliography-reading-path-grid article').length,
              metaStats: document.querySelectorAll('.bibliography-meta-strip span').length,
              cards: document.querySelectorAll('.reference-card').length,
              loadMore: !!document.querySelector('#load-more-papers'),
              methodMap: !!document.querySelector('#method-time-map'),
              publicationMap: !!document.querySelector('#publication-status-map'),
              signalMap: !!document.querySelector('#surface-signal-map'),
              exports: document.querySelectorAll('.export-btn').length,
              filters: document.querySelectorAll('.bibliography-controls select').length,
              analyses: document.querySelectorAll('.paper-analysis').length,
              analysisFields: document.querySelectorAll('.paper-analysis-grid > div').length,
              designBreakdowns: document.querySelectorAll('.paper-design-breakdown').length,
              designFields: document.querySelectorAll('.paper-design-grid > div').length,
              catalogDesignAudit: window.paperConcreteDesignAudit?.() || {total:0,missing:0,s2SignalLeak:0,samples:{}},
              concreteSamples: window.paperConcreteDesignAudit?.().samples || {},
              analysisGuide: !!document.querySelector('#paper-reading-schema'),
              rankingGuide: !!document.querySelector('#literature-ranking'),
              sortSelect: document.querySelector('#bibliography-sort')?.value || '',
              rankingStatus: document.querySelector('#citation-ranking-status')?.textContent || '',
              priorityRanks: document.querySelectorAll('.reference-card[data-priority-rank]').length,
              roleGroups: document.querySelectorAll('.reference-role-group').length,
              roleBadges: document.querySelectorAll('.reference-card .reading-role').length,
              tierBadges: document.querySelectorAll('.reference-card .ranking-tier').length,
              citationBadges: document.querySelectorAll('.reference-card .citation-count').length,
              mustReadBadges: document.querySelectorAll('.reference-card .badge.must-read').length,
              mustReadNotes: document.querySelectorAll('.reference-card .must-read-note').length,
              mustReadTeamNotes: document.querySelectorAll('.reference-card .must-read-note small').length,
              knownCitations: document.querySelectorAll('.reference-card .citation-count:not(.citation-pending)').length,
              openAnalyses: document.querySelectorAll('.paper-analysis[open]').length,
              analysisLabels: [...document.querySelectorAll('.paper-analysis-grid b')].slice(0,6).map(x=>x.textContent.trim()),
              orderedCards: [...document.querySelectorAll('.reference-card')].map(x=>({role:x.dataset.readingRole,roleRank:Number(x.dataset.roleRank),mustReadRank:Number(x.dataset.mustReadRank||0),tier:Number(x.dataset.tier),citations:Number(x.dataset.citations),year:Number(x.dataset.year),title:x.querySelector('h3')?.textContent||''})),
              missing: document.querySelectorAll('.citation-missing').length
            };""",
        )
        require(bibliography["chapters"] == ["published-spine","published-comparison","idea-mining","field-maps","search-corpus","coverage-protocol"], f"bibliography reading order is wrong: {bibliography['chapters']}")
        require((bibliography["trustCards"],bibliography["refreshLogs"],bibliography["refreshMethods"],bibliography["refreshChips"],bibliography["mapGuideCards"],bibliography["metaStats"]) == (4,1,2,7,3,4), f"bibliography maps or refresh provenance are incomplete: {bibliography}")
        require(all(marker in bibliography["refreshText"] for marker in ("2026-08-22","+33 papers","Semantic Scholar + arXiv","RoMeRL","HarnessBank")), f"bibliography incremental API refresh provenance is incomplete: {bibliography['refreshText']}")
        require(bibliography["statusStrips"] == 0, "bibliography must not show current research-state status strips")
        require(not bibliography["pageOverflow"], "bibliography published-first layout overflows horizontally")
        require((bibliography["publishedQuestionCards"],bibliography["publishedStories"],bibliography["publishedComparisonSections"]) == (4,10,10), f"published literature spine is incomplete: {bibliography}")
        published_audit=bibliography["publishedAudit"]
        require(published_audit["published"] >= 60 and not published_audit["missingQuick"] and published_audit["byTier"].get("A",0) >= 15, f"published literature audit failed: {published_audit}")
        require(published_audit["mustRead"] == 22 and published_audit["paperSpecificEvidence"] == 22 and not published_audit["missingMustReadEvidence"] and published_audit["numericEvidence"] >= 15, f"A-tier paper-specific evidence is incomplete: {published_audit}")
        require(bibliography["publishedQuickReads"] > 0 and bibliography["publishedQuickFields"] == bibliography["publishedQuickReads"] * 8, "published paper 30-second readouts are incomplete")
        require(bibliography["publishedEvidenceSources"] > 0, "visible A-tier paper cards must expose the source-grounded evidence note")
        require("published" in bibliography["publishedIntro"].lower() and str(published_audit["published"]) in bibliography["publishedIntro"], "published spine summary is missing its audited count")
        idea_audit=bibliography["ideaMiningAudit"]
        require((bibliography["ideaMiningDirections"],bibliography["ideaMiningSections"],bibliography["ideaMiningInternal"],bibliography["ideaMiningIntersections"],bibliography["ideaMiningContract"],bibliography["ideaMiningPriority"]) == (10,70,10,8,7,10), f"literature idea-mining UI is incomplete: {bibliography}")
        require(bibliography["ideaMiningInternalLinks"] >= 8, "idea-mining directions must expose current in-house ResearchItem collision links")
        require(idea_audit["directions"] == 10 and idea_audit["intersections"] == 8 and idea_audit["contract"] == 7 and not idea_audit["missing"], f"literature idea-mining audit failed: {idea_audit}")
        require(idea_audit["researchItems"] >= 80 and idea_audit["activeCollisionRefs"] >= 8 and len(idea_audit["uniqueActiveResearchItems"]) >= 4 and idea_audit["terminalCollisionRefs"] >= 50, f"literature gap registry is not colliding against the canonical ResearchItem ledger: {idea_audit}")
        require(set(idea_audit["high"]) == {"D1","D7","D8"} and idea_audit["crowded"] == ["D4"], f"idea opportunity prioritization drifted: {idea_audit}")
        require(all(marker in bibliography["ideaMiningText"] for marker in ("High-collision exclusion","Repeated failure","Surviving opening","Questions to seed later API collisions")), "idea-mining search-space fields are not visible")
        require(bibliography["cards"] == 80, "bibliography initial pagination is not 80")
        require(bibliography["loadMore"], "bibliography load-more control is missing")
        require(bibliography["methodMap"] and bibliography["publicationMap"] and bibliography["signalMap"], "one or more bibliography maps are missing")
        require(bibliography["exports"] == 3, "bibliography exports are incomplete")
        require(bibliography["filters"] == 3, "bibliography select filters are incomplete")
        require(bibliography["analyses"] == 80 and bibliography["analysisFields"] == 480, "paper analyses are incomplete on the initial bibliography page")
        require(bibliography["openAnalyses"] == 0, "bibliography paper details must stay collapsed by default")
        require(bibliography["designBreakdowns"] == 80 and bibliography["designFields"] == 400, "concrete paper-design breakdown is incomplete on the initial bibliography page")
        design_audit=bibliography["catalogDesignAudit"]
        require(design_audit["total"] >= 400 and design_audit["missing"] == 0 and design_audit["s2SignalLeak"] == 0, f"full currently loaded catalog concrete-design audit failed: {design_audit}")
        samples=bibliography["concreteSamples"]
        require("hypergraph" in samples["hyper"].lower() and "recombine" in samples["harness"].lower() and "validity/quality gates" in samples["harness"].lower() and "faulty skill rule" in samples["skill"].lower(), f"paper-specific implementation flows are still too generic: {samples}")
        require(bibliography["analysisGuide"], "paper analysis reading guide is missing")
        require(bibliography["rankingGuide"] and bibliography["sortSelect"] == "priority", "literature ranking controls are incomplete")
        require(bibliography["rankingStatus"], "citation ranking status is missing")
        require(bibliography["priorityRanks"] == 80 and bibliography["roleBadges"] == 80 and bibliography["tierBadges"] == 80 and bibliography["citationBadges"] == 80, "ranking metadata is incomplete on bibliography cards")
        require(bibliography["mustReadBadges"] == 10 and bibliography["mustReadNotes"] == 10 and bibliography["mustReadTeamNotes"] >= 3, f"must-read anchor explanations are incomplete: {bibliography}")
        require(bibliography["roleGroups"] >= 2, "recommended reading groups are missing")
        require(bibliography["knownCitations"] >= 3, f"deployment citation snapshot is not visible: {bibliography['rankingStatus']}")
        ordered = bibliography["orderedCards"]
        require(all(a["roleRank"] <= b["roleRank"] for a, b in zip(ordered, ordered[1:])), "default bibliography order violates reading roles")
        require(len(ordered) >= 10 and all(item["role"] == "must-read" and item["mustReadRank"] == index + 1 for index,item in enumerate(ordered[:10])), f"first ten papers must be the explicit must-read anchors, not a wall of surveys: {ordered[:12]}")
        require(not any(item["role"] == "field-overview" for item in ordered[:10]), "surveys leaked back into the first ten must-read papers")
        require(not any(item["role"] in {"agent-foundation", "model-foundation"} for item in ordered[:20]), "old foundations still dominate the recommended top twenty")
        for a, b in zip(ordered, ordered[1:]):
            if a["role"] != b["role"]:
                continue
            if a["role"] == "must-read":
                require(a["mustReadRank"] <= b["mustReadRank"], "must-read anchors are not following the curated anchor order")
                continue
            if a["role"] in {"agent-foundation", "model-foundation"}:
                require(a["year"] <= b["year"], "foundation papers are not presented chronologically")
                continue
            if a["role"] == "field-overview":
                require(a["year"] >= b["year"], "field overviews are not ordered by recency")
                continue
            require(a["tier"] <= b["tier"], "publication tier is not respected inside a reading role")
            if a["tier"] == b["tier"]:
                require(a["year"] >= b["year"], "papers are not ordered by recency inside a reading role and venue tier")
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
        require(specific_analysis["found"] and not specific_analysis["open"], "requested paper should be located without auto-expanding its analysis")
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
            "/selected-paper.html": {"groups": None, "sections": None},
        }
        for page, expected in expected_hubs.items():
            navigate(page, 7)
            result = execute(
                session_id,
                """return {
                  heading: document.querySelector('h1')?.textContent || '',
                  groups: document.querySelectorAll('.merged-group').length,
                  sections: document.querySelectorAll('.topic-section').length,
                  historySrc: document.querySelector('.overview-figure img')?.getAttribute('src') || '',
                  missing: document.querySelectorAll('.citation-missing').length,
                  pageOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
                  text: document.body.textContent || ''
                };""",
            )
            require(result["heading"], f"{page} has no heading")
            if expected["groups"] is not None:
                require(result["groups"] == expected["groups"], f"{page} group count mismatch")
            if expected["sections"] is not None:
                require(result["sections"] >= expected["sections"], f"{page} has too few sections")
            require(result["missing"] == 0, f"{page} contains unresolved citations")
            require(not result["pageOverflow"], f"{page} causes page-level horizontal overflow")
            if page == "/foundations.html":
                require(not result["historySrc"], "foundations should stay focused on definition/taxonomy instead of duplicating the field-history figure")
            if page == "/selected-paper.html":
                require("PaperRegistry" in result["text"] and "SUBMISSION_READY" in result["text"] and "AGENT-SAFETY-R9" in result["text"] and "STRI" in result["text"] and all(title in result["text"] for title in expected_registry_titles.values()) and all(stage in result["text"] for stage in set(expected_registry_stages.values())), "canonical five-paper PaperRegistry is missing or incomplete")

        navigate("/mechanisms.html", 7)
        field_matrix = execute(session_id, """return {
          bridge:document.querySelectorAll('.field-atlas-bridge a').length,
          chapters:document.querySelectorAll('.field-matrix-chapter').length,
          crossRows:document.querySelectorAll('.field-cross-matrix tbody tr').length,
          denseDetails:document.querySelectorAll('.field-dense-detail').length,
          openDetails:document.querySelectorAll('.field-dense-detail[open]').length,
          evidenceSteps:document.querySelectorAll('.field-evidence-stack>div').length,
          evidenceResources:document.querySelectorAll('.field-evidence-resource').length,
          resourceCards:document.querySelectorAll('.reference-card').length,
          sourceSections:document.querySelectorAll('.field-source-section').length,
          overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2,
          text:document.body.textContent||''
        };""")
        require(field_matrix["bridge"] == 3 and field_matrix["chapters"] == 3 and field_matrix["crossRows"] == 5, f"unified field matrix shell is incomplete: {field_matrix}")
        require(field_matrix["denseDetails"] == 8 and field_matrix["openDetails"] == 0 and field_matrix["evidenceSteps"] == 7 and field_matrix["evidenceResources"] == 3, f"mechanism/domain/evidence detail inventory is incomplete: {field_matrix}")
        require(field_matrix["resourceCards"] == 0 and field_matrix["sourceSections"] >= 50 and not field_matrix["overflow"], f"field atlas must retain detailed source notes without duplicating bibliography resource cards: {field_matrix}")
        require(all(marker in field_matrix["text"] for marker in ("Model parameters","GUI / Web","Embodied / robotics","Future gain","Rollback & recovery","Filter in bibliography")), "unified field matrix is missing one or more mechanism/domain/evidence anchors")

        navigate("/research-directions.html", 7)
        ensure_language("en")
        direction_map = execute(session_id, """return {
          bridge:document.querySelectorAll('.field-atlas-bridge a').length,
          chapters:document.querySelectorAll('.page-chapter').length,
          macroCards:document.querySelectorAll('.direction-macro-card').length,
          historySpine:document.querySelectorAll('.field-history-stage').length,
          historyAudit:document.querySelectorAll('.field-history-audit').length,
          historyAuditOpen:document.querySelectorAll('.field-history-audit[open]').length,
          atlasRows:document.querySelectorAll('.direction-atlas-table tbody tr').length,
          details:document.querySelectorAll('.direction-atlas-detail').length,
          openDetails:document.querySelectorAll('.direction-atlas-detail[open]').length,
          chips:document.querySelectorAll('.idea-chip').length,
          evidenceSections:document.querySelectorAll('.direction-literature').length,
          evidencePapers:document.querySelectorAll('.direction-paper-evidence').length,
          migrationRows:document.querySelectorAll('.historical-taxonomy-migration tbody tr').length,
          agendaOpen:document.querySelectorAll('.historical-agenda-fold[open]').length,
          missing:document.querySelectorAll('.citation-missing').length,
          overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2,
          text:document.body.textContent||''
        };""")
        require(direction_map["bridge"] == 3 and direction_map["chapters"] == 3 and direction_map["historySpine"] == 6 and direction_map["macroCards"] == 4, f"compact field-landscape spine is incomplete: {direction_map}")
        require(direction_map["atlasRows"] == 10 and direction_map["details"] == 10 and direction_map["openDetails"] == 0, f"D1-D10 must render as one table plus ten collapsed details: {direction_map}")
        require(direction_map["chips"] == 34 and direction_map["evidenceSections"] == 10 and direction_map["evidencePapers"] >= 30, f"collapsed direction dossiers lost literature or historical lineage: {direction_map}")
        require(direction_map["historyAudit"] == 1 and direction_map["historyAuditOpen"] == 0 and direction_map["migrationRows"] == 10 and direction_map["agendaOpen"] == 0, f"history/migration audit layers are incomplete or too expanded: {direction_map}")
        require(direction_map["missing"] == 0 and not direction_map["overflow"], f"field landscape has unresolved citations or horizontal overflow: {direction_map}")
        require(all(marker in direction_map["text"] for marker in ("Field matrix","Compare all ten problems first","Representative papers","Current canonical ResearchItem landing")), "English compact field landscape is missing key comparison layers")
        ensure_language("zh")
        zh_state = execute(session_id, """return {text:document.body.textContent||'',brand:[document.querySelector('.brand strong')?.textContent||'',document.querySelector('.brand span')?.textContent||''],nav:[...document.querySelectorAll('.nav-level1 span:first-child,.nav-level2')].map(x=>x.textContent.trim()),placeholder:document.querySelector('#site-search')?.getAttribute('placeholder')||''};""")
        require(all(marker in zh_state["text"] for marker in ("领域矩阵 · 机制 × 场景 × 评测","先横向比较十个问题","代表论文","今天落到哪些","当前 A 类")), "Chinese compact field landscape did not switch")
        require(zh_state["brand"] == ["Agent 自进化","科研观测站"] and "开始阅读" in zh_state["nav"] and "领域图谱" in zh_state["nav"] and "当前科研" in zh_state["nav"] and "文献" in zh_state["nav"] and "Start Here" not in zh_state["nav"] and zh_state["placeholder"] == "搜索研究站内容…", f"shared shell did not fully switch to Chinese: {zh_state}")

        navigate("/domains.html#group-gui-web", 3)
        redirected_domain = execute(session_id, """return {href:location.pathname+location.hash,open:!!document.getElementById('field-gui-web')?.open};""")
        require(redirected_domain["href"].endswith("/mechanisms.html#field-gui-web") and redirected_domain["open"], f"legacy domain deep link did not map/open precisely: {redirected_domain}")
        navigate("/evaluation.html#group-repositories", 3)
        redirected_eval = execute(session_id, """return {href:location.pathname+location.hash,open:!!document.getElementById('field-repositories')?.open};""")
        require(redirected_eval["href"].endswith("/mechanisms.html#field-repositories") and redirected_eval["open"], f"legacy evaluation deep link did not map/open precisely: {redirected_eval}")

        navigate("/research-map.html", 7)
        ensure_language("zh")
        research_map = execute(session_id, """return {
          chapters:document.querySelectorAll('.page-chapter').length,
          toc2:document.querySelectorAll('.toc-level-2').length,
          bridgeLinks:document.querySelectorAll('.rpm-bridge-grid a').length,
          categories:document.querySelectorAll('.rpm-category').length,
          overviewCards:document.querySelectorAll('.rpm-overview-card').length,
          externalDensityRows:document.querySelectorAll('.rpm-external-density').length,
          frontierBoundaries:document.querySelectorAll('.rpm-frontier-boundary').length,
          graphAppendix:document.querySelectorAll('.rpm-graph-schema').length,
          controlBoard:document.querySelectorAll('.rpm-control-board').length,
          controlCodes:[...document.querySelectorAll('.rpm-control-board [data-dashboard-research]')].map(x=>x.dataset.dashboardResearch||''),
          controlRows:document.querySelectorAll('.rpm-control-row').length,
          controlHighlights:document.querySelectorAll('.rpm-control-highlight').length,
          controlLinks:[...document.querySelectorAll('.rpm-control-board a')].map(x=>x.getAttribute('href')||''),
          dashboardSummary:window.RESEARCH_DASHBOARD?.summary||{},
          pageOverflow:document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
          text:document.body.textContent||''
        };""")
        require((research_map["chapters"],research_map["toc2"],research_map["bridgeLinks"],research_map["categories"],research_map["overviewCards"],research_map["externalDensityRows"],research_map["frontierBoundaries"],research_map["graphAppendix"]) == (4,5,3,7,7,6,7,1), f"current research map hierarchy/coverage-density/latest-literature layers are incomplete: {research_map}")
        require(all(marker in research_map["text"] for marker in ("最新文献把边界推到哪里","HarnessBank","RoMeRL","Who Grades the Grader?","EmbodiSkill","Robo-Cortex","SpaceMind","不自动改变 ResearchItem")), f"authenticated S2 boundary interpretation is missing from the current research map: {research_map}")
        require(research_map["controlBoard"] == 1 and research_map["controlRows"] == 5 and set(research_map["controlCodes"]) == {"E-7","G-1","A-3","B-2","B-3","E-1"} and research_map["controlHighlights"] >= 3, f"current research map must begin with the same six-object action queue as home: {research_map}")
        require(research_map["dashboardSummary"].get("launchable_formal_experiments") == 0 and "research-timeline.html?research=A-3" in research_map["controlLinks"] and "selected-paper.html?paper=STRI" in research_map["controlLinks"], f"research-map control board must preserve zero experiment authority and direct provenance links: {research_map}")
        require(not research_map["pageOverflow"], "current research map causes page-level horizontal overflow")
        require("当前控制面 · 跟踪不等于 active" in research_map["text"] and "active ResearchItem=0" in research_map["text"] and "另有 6 个可见跟踪对象" in research_map["text"] and "machine-actionable=0" in research_map["text"] and "本页：当前全景" in research_map["text"] and "研究组合：完整证据" in research_map["text"] and "A–G 快速总览" in research_map["text"] and "把“我们做得多不多”和“外部已经拥不拥挤”分开看" in research_map["text"] and "外部文献更密集" in research_map["text"] and "完整知识图谱技术结构" in research_map["text"], "current research map reading chain/control-board/coverage-density summary is incomplete")

        navigate("/paper-ideas.html", 7)
        ensure_language("zh")
        idea_portfolio = execute(
            session_id,
            """return {
              chapters: document.querySelectorAll('.page-chapter').length,
              decisionConsole: document.querySelectorAll('#portfolio-current').length,
              currentAttentionCards: document.querySelectorAll('.portfolio-attention-card').length,
              categoryIndexLinks: document.querySelectorAll('.canonical-category-nav a').length,
              concludedOpen: document.querySelectorAll('.lane-concluded[open]').length,
              assetsOpen: document.querySelectorAll('.lane-assets[open]').length,
              mementoDefaultOpen: document.querySelector('#live-memento-paper-design')?.open === true,
              safetyDefaultOpen: document.querySelector('.agent-safety-program-fold')?.open === true,
              auditDefaultOpen: document.querySelector('#portfolio-audit')?.open === true,
              portfolioToc: [...document.querySelectorAll('#page-toc a')].map(a=>a.textContent.trim()),
              pageHeight: document.documentElement.scrollHeight,
              pageOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
              categoryGroups: document.querySelectorAll('.canonical-idea-group').length,
              categoryLanes: document.querySelectorAll('.research-category-lane').length,
              evidenceTracks: document.querySelectorAll('.human-review-idea-card .research-item-evidence-track').length,
              paperHandoffs: document.querySelectorAll('.paper-handoff-research-item').length,
              paperHandoffEvidence: document.querySelectorAll('.paper-handoff-evidence-step').length,
              parentCards: document.querySelectorAll('.human-review-idea-card').length,
              standaloneCards: document.querySelectorAll('.supplemental-idea-card').length,
              incubationCards: document.querySelectorAll('.paper-incubation-card').length,
              incubationP0: document.querySelectorAll('.paper-incubation-card.incubation-p0').length,
              incubationSummary: window.PAPER_FIRST_IDEA_INCUBATION?.summary || {},
              terminalGroups: document.querySelectorAll('.human-status-block').length,
              terminalStats: document.querySelectorAll('.human-review-stats .human-stat').length,
              legacyPreGpuBoards: document.querySelectorAll('.pre-gpu-candidate-board').length,
              legacyP0Entry: document.querySelectorAll('.p0-entry-panel').length,
              currentLedger: document.querySelectorAll('#current-research-portfolio').length,
              currentInventoryTotal: Number(document.querySelector('[data-research-inventory-total]')?.getAttribute('data-research-inventory-total') || 0),
              legacyCurrentRows: document.querySelectorAll('#current-research-portfolio .current-research-table tbody tr').length,
              leadingPaperTracks: document.querySelectorAll('#current-research-portfolio .current-paper-track-card').length,
              currentStatus: window.CURRENT_RESEARCH_STATUS?.headline || {},
              canonicalResearchSummary: window.RESEARCH_ITEM_STATE?.summary || {},
              canonicalResearchItems: Object.fromEntries((window.RESEARCH_ITEM_STATE?.research_items || []).map(x=>[x.code,x.scientific_state])),
              paperRegistry: window.PAPER_REGISTRY || {},
              striP0E: window.CURRENT_RESEARCH_STATUS?.stri_dynamic_evidence?.skillrl_p0e || {},
              legacyFinalPass: Number(window.RESEARCH_SYSTEM_STATE?.summary?.final_pass || 0),
              experimentStops: Number(window.RESEARCH_SYSTEM_STATE?.p0_decision_ledger?.summary?.experiment_stopped || 0),
              text: document.body.textContent || ''
            };""",
        )
        require(idea_portfolio["chapters"] == 0 and idea_portfolio["categoryGroups"] == 7 and idea_portfolio["categoryLanes"] == 21 and idea_portfolio["evidenceTracks"] == 26 and idea_portfolio["paperHandoffs"] == 1 and idea_portfolio["paperHandoffEvidence"] == 3, f"Research Portfolio must preserve seven A-G groups, three reading lanes per group, one integrated evidence trail per parent ResearchItem, and one STRI PaperState handoff: {idea_portfolio}")
        expected_portfolio_toc=["当前需要看什么","A–G 研究组合","更新可靠性与回归控制","记忆、经验与持久知识","评价器、奖励与自纠正","任务生成与课程","工作流与结构演化","世界模型与具身适应","Agent 自进化安全与未来风险","审计与历史"]
        require(idea_portfolio["decisionConsole"] == 1 and idea_portfolio["currentAttentionCards"] == 6 and idea_portfolio["categoryIndexLinks"] == 7 and idea_portfolio["concludedOpen"] == 0 and idea_portfolio["assetsOpen"] == 0 and not idea_portfolio["mementoDefaultOpen"] and not idea_portfolio["safetyDefaultOpen"] and not idea_portfolio["auditDefaultOpen"] and idea_portfolio["portfolioToc"] == expected_portfolio_toc and idea_portfolio["pageHeight"] < 7500 and not idea_portfolio["pageOverflow"], f"Research Portfolio must be decision-first with current attention visible and audit/history collapsed by default: {idea_portfolio}")
        require(idea_portfolio["parentCards"] == 26, f"expected all 26 human-parent histories, got {idea_portfolio['parentCards']}")
        require(idea_portfolio["standaloneCards"] == 7, f"expected only the seven validated standalone methods after paper-first authority quarantine, got {idea_portfolio['standaloneCards']}")
        require((idea_portfolio["incubationCards"],idea_portfolio["incubationP0"],idea_portfolio["incubationSummary"].get("p0_authorized"),idea_portfolio["incubationSummary"].get("gpu_authorized")) == (9,0,0,0), f"paper-first queue must remain nine design candidates with zero validated P0/GPU authority: {idea_portfolio}")
        require("STOP_MATCHED_POST_ONLY_EQUIVALENT" in idea_portfolio["text"] and "STOP_MATCHED_SOFT_SCALAR_EQUIVALENT" in idea_portfolio["text"] and "DIAGNOSTIC ONLY" in idea_portfolio["text"], "completed premature Method diagnostics are not visible on Paper Ideas")
        require(idea_portfolio["terminalGroups"] == 0 and idea_portfolio["terminalStats"] == 0, f"legacy terminal-status grouping must not compete with the A-G ResearchItem lanes: {idea_portfolio['terminalGroups']}/{idea_portfolio['terminalStats']}")
        require(idea_portfolio["legacyPreGpuBoards"] == 0 and idea_portfolio["legacyP0Entry"] == 0, "legacy Pre-GPU/P0-entry boards leaked back into canonical Paper Ideas")
        require(idea_portfolio["currentLedger"] == 1 and idea_portfolio["currentInventoryTotal"] == int(expected_research_summary.get("portfolio_objects") or 0) and idea_portfolio["legacyCurrentRows"] == 0 and idea_portfolio["leadingPaperTracks"] == 1, f"complete ResearchItem accounting or PaperState handoff is incomplete, or the legacy current-status row table leaked back in: {idea_portfolio}")
        crs=idea_portfolio["canonicalResearchSummary"]
        require((crs.get("research_items"),crs.get("experiment_records"),crs.get("portfolio_experiment_contexts"),crs.get("evidence_contexts"),crs.get("portfolio_objects")) == (expected_research_summary.get("research_items"),expected_research_summary.get("experiment_records"),expected_research_summary.get("portfolio_experiment_contexts"),expected_research_summary.get("evidence_contexts"),expected_research_summary.get("portfolio_objects")) and crs.get("parent_scientific_states") == {"HOLD":4,"MERGED":6,"STOPPED":16}, f"canonical ResearchItem projection is missing or inconsistent: {crs}")
        require(all(idea_portfolio["canonicalResearchItems"].get(code)=="HOLD" for code in ("A-3","B-2","B-3","E-1")) and idea_portfolio["canonicalResearchItems"].get("E-7")=="PAPER_READY" and idea_portfolio["canonicalResearchItems"].get("G-1")=="HOLD", f"canonical ResearchItem state authority drifted: {idea_portfolio['canonicalResearchItems']}")
        registry_summary=idea_portfolio["paperRegistry"].get("summary") or {}
        registry_papers={row.get("paper_id"):row for row in (idea_portfolio["paperRegistry"].get("papers") or [])}
        require(registry_summary == expected_registry_summary and {pid:row.get("paper_stage") for pid,row in registry_papers.items()} == expected_registry_stages and registry_summary.get("scientific_holds") == 0 and registry_papers.get("STRI",{}).get("source_research_item") == "E-7" and registry_papers.get("STRI",{}).get("paper_stage") == "SUBMISSION_READY" and registry_papers.get("STRI",{}).get("submission_ready") is True and registry_papers.get("AGENT-SAFETY-R9",{}).get("source_research_item") == "G-1" and registry_papers.get("AGENT-SAFETY-R9",{}).get("paper_stage") == "SUBMISSION_READY" and registry_papers.get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",{}).get("paper_stage") == "SUBMISSION_READY" and registry_papers.get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",{}).get("source_research_item") is None and registry_papers.get("D2-PAPER-FAILURE-MEMORY-PROVENANCE",{}).get("source_kind") == "paper-first-discovery-candidate", f"Research Portfolio must match the current PaperRegistry projection while preserving D2 paper-first provenance and G-1 broader HOLD: {idea_portfolio['paperRegistry']}")
        temporal_registry=registry_papers.get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",{})
        failure_registry=registry_papers.get("D2-PAPER-FAILURE-MEMORY-PROVENANCE",{})
        temporal_evidence=temporal_registry.get("source_native_evidence") or {}
        temporal_review=(temporal_registry.get("latest_mock_review") or {}).get("summary") or {}
        temporal_prep=temporal_registry.get("latest_paper_preparation") or {}
        temporal_clean=temporal_prep.get("pass") is True
        temporal_action="NO_INTERNAL_ACTION" if temporal_clean else "PAPER_REPAIR_REQUIRED"
        require(registry_summary == expected_registry_summary and temporal_registry.get("gate_clean_submission_ready") is temporal_clean and temporal_registry.get("immediate_submission_hold") is (not temporal_clean) and (temporal_registry.get("primary_next_action") or {}).get("action_class") == temporal_action and int(temporal_prep.get("required_gates") or 0) == 8 and (temporal_clean or bool(temporal_prep.get("blockers"))) and (temporal_evidence.get("runtime_valid_rows"),temporal_evidence.get("distinct_endpoints"),temporal_evidence.get("institutional_systems")) == (1326,35,3) and temporal_review.get("scores") == [8,8,7] and failure_registry.get("paper_stage") == "SUBMISSION_READY" and failure_registry.get("gate_clean_submission_ready") is True and failure_registry.get("active_unrefuted_claims") == 2, f"Research Portfolio must follow the latest Temporal paper-quality receipt while preserving source-native evidence: {idea_portfolio['paperRegistry']}")
        p0e=idea_portfolio["striP0E"]
        require(p0e.get("status") == "STOP_FIXED_POLICY_DYNAMIC_BRIDGE" and p0e.get("principle_disposition") == "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED" and p0e.get("persistent_principle_dead_end_certified") is False and p0e.get("stage2_locked") is True and p0e.get("new_gpu_authorized") is False, f"qualified STRI P0-E machine boundary is stale: {p0e}")
        require("E-7c" in idea_portfolio["text"] and idea_portfolio["paperHandoffEvidence"] == 3 and p0e.get("stage2_locked") is True and p0e.get("new_gpu_authorized") is False, "STRI P0-E must stay a nested zero-authority E-7c evidence record rather than a peer Idea")
        cs=idea_portfolio["currentStatus"]
        require((cs.get("paper_ready"),cs.get("paper_quality_hold"),cs.get("paper_quality_evidence_debt"),cs.get("canonical_live_ideas"),cs.get("launchable_formal_experiments"),cs.get("legacy_p0_lifecycle")) == (1,0,0,0,0,27) and cs.get("shadow_qualification_ready") == expected_headline.get("shadow_qualification_ready") and int(cs.get("shadow_dead_ends") or 0) >= 0 and int(cs.get("shadow_holds") or 0) >= 0, f"current status invariants are wrong: rendered={cs} expected={expected_headline}")
        require(idea_portfolio["legacyFinalPass"] == 20 and idea_portfolio["experimentStops"] >= 16, f"historical lineage state is unexpectedly missing: {idea_portfolio}")
        require("Historical ICLR Paper Workspace" not in idea_portfolio["text"] and "Selected ICLR Paper Workspace" not in idea_portfolio["text"], "historical paper workspace content leaked into Paper Ideas")
        require("20 个当前 FINAL-PASS" not in idea_portfolio["text"] and all(marker in idea_portfolio["text"] for marker in ("先看 6 个当前需要关注对象","A–G 研究组合","当前关注","审计与历史","SUBMISSION_READY")), "Research Portfolio decision-first current-state framing is incomplete or stale FINAL-PASS framing leaked into the current view")

        navigate("/selected-paper.html", 4)
        ensure_language("zh")
        selected = execute(session_id, """return {
          chapters: document.querySelectorAll('.page-chapter').length,
          currentSTRI: document.querySelectorAll('#selected-stri-current').length,
          currentAgentSafety: document.querySelectorAll('#paper-agent-safety').length,
          paperTocRoots: [...document.querySelectorAll('#page-toc .paper-toc-root > a')].map(a=>a.textContent.trim()),
          paperTocChildCounts: [...document.querySelectorAll('#page-toc .paper-toc-root')].map(li=>li.querySelectorAll(':scope > ul > li').length),
          archive: document.querySelectorAll('#historical-paper-archive').length,
          archiveOpen: document.querySelector('#historical-paper-archive')?.open === true,
          currentStatus: window.CURRENT_RESEARCH_STATUS?.headline || {},
          currentPaper: (window.PAPER_REGISTRY?.papers || []).find(x=>x.paper_id==='STRI') || {},
          agentSafetyPaper: (window.PAPER_REGISTRY?.papers || []).find(x=>x.paper_id==='AGENT-SAFETY-R9') || {},
          paperRegistrySummary: window.PAPER_REGISTRY?.summary || {},
          paperRegistryPanel: document.querySelectorAll('#paper-registry-overview').length,
          paperRegistryCards: document.querySelectorAll('.paper-registry-card').length,
          paperRegistryIds: [...document.querySelectorAll('.paper-registry-card')].map(x=>x.dataset.paperId||''),
          paperRegistryStages: Object.fromEntries([...document.querySelectorAll('.paper-registry-card')].map(x=>[x.dataset.paperId||'',x.dataset.paperStage||''])),
          paperRegistryGateClean: Object.fromEntries([...document.querySelectorAll('.paper-registry-card')].map(x=>[x.dataset.paperId||'',x.dataset.gateClean||''])),
          paperRegistryNextActions: Object.fromEntries([...document.querySelectorAll('.paper-registry-card')].map(x=>[x.dataset.paperId||'',x.dataset.nextAction||''])),
          noveltyPortfolio: document.querySelectorAll('#paper-novelty-portfolio').length,
          noveltyDetails: document.querySelectorAll('.paper-novelty-detail').length,
          noveltyDims: document.querySelectorAll('.paper-novelty-dim-grid article').length,
          noveltyNearest: document.querySelectorAll('.paper-novelty-nearest article').length,
          noveltyAdvisorQuestions: document.querySelectorAll('.paper-novelty-advisor-grid .advisor-question').length,
          noveltyIds: [...document.querySelectorAll('.paper-novelty-detail')].map(x=>x.dataset.paperNovelty||''),
          noveltyText: [...document.querySelectorAll('#paper-novelty-portfolio,.paper-novelty-detail')].map(x=>x.textContent||'').join(' '),
          externalReviewPortfolio: document.querySelectorAll('#paper-external-review-portfolio').length,
          externalReviewDetails: document.querySelectorAll('.paper-external-review-detail').length,
          externalRepairCards: document.querySelectorAll('.paper-external-review-detail .external-repair-card').length,
          externalReviewIds: [...document.querySelectorAll('.paper-external-review-detail')].map(x=>x.dataset.paperExternalReview||''),
          externalReviewScores: Object.fromEntries([...document.querySelectorAll('.paper-external-review-detail')].map(x=>[x.dataset.paperExternalReview||'',(x.querySelector('.paper-external-review-scorebox strong')?.textContent||'').trim()])),
          externalReviewText: [...document.querySelectorAll('#paper-external-review-portfolio,.paper-external-review-detail')].map(x=>x.textContent||'').join(' '),
          objectionMatrixPortfolio: document.querySelectorAll('#stanford-r2-objection-matrix').length,
          objectionDetails: document.querySelectorAll('.reviewer-objection-detail').length,
          objectionRows: document.querySelectorAll('[data-review-objection]').length,
          objectionDispositionCounts: [...document.querySelectorAll('[data-review-objection]')].reduce((acc,x)=>{const d=x.dataset.reviewDisposition||'';acc[d]=(acc[d]||0)+1;return acc;},{}),
          objectionText: [...document.querySelectorAll('#stanford-r2-objection-matrix,.reviewer-objection-detail')].map(x=>x.textContent||'').join(' '),
          temporalPaper: (window.PAPER_REGISTRY?.papers || []).find(x=>x.paper_id==='D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK') || {},
          failureMemoryPaper: (window.PAPER_REGISTRY?.papers || []).find(x=>x.paper_id==='D2-PAPER-FAILURE-MEMORY-PROVENANCE') || {},
          currentDynamic: window.CURRENT_RESEARCH_STATUS?.stri_dynamic_evidence || {},
          paperAcceptance: (window.RESEARCH_SYSTEM_STATE?.paper_acceptance?.ledger_index?.entries || []).find(row=>row.paper_id==='STRI-ICLR2027') || {},
          agentSafetyAcceptance: (window.RESEARCH_SYSTEM_STATE?.paper_acceptance?.ledger_index?.entries || []).find(row=>row.paper_id==='AGENT-SAFETY-R9') || {},
          paperAcceptanceSummary: window.RESEARCH_SYSTEM_STATE?.paper_acceptance?.summary || {},
          acceptancePanels: document.querySelectorAll('.paper-acceptance-workflow').length,
          acceptanceStages: document.querySelectorAll('.paper-acceptance-stage').length,
          submissionDownloads: [...document.querySelectorAll('#selected-stri-current .current-status-downloads a')].map(a=>a.getAttribute('href')||''),
          agentSafetyDownloads: [...document.querySelectorAll('.paper-registry-card[data-paper-id="AGENT-SAFETY-R9"] .current-status-downloads a')].map(a=>a.getAttribute('href')||''),
          title: document.title,
          text: document.querySelector('.layout')?.textContent || ''
        };""")
        require(selected["currentSTRI"] == 1 and selected["currentAgentSafety"] == 1 and selected["archive"] == 1 and not selected["archiveOpen"] and selected["acceptancePanels"] == 5 and selected["acceptanceStages"] == 60, f"Papers must render five current paper details, five independent 12-stage canonical acceptance workflows, and the collapsed historical archive: {selected}")
        require(len(selected["paperTocRoots"]) == 5 and "STRI" in selected["paperTocRoots"][0] and "R9" in selected["paperTocRoots"][1] and any("Temporal Skill" in x for x in selected["paperTocRoots"]) and all(count >= 3 for count in selected["paperTocChildCounts"]), f"selected-paper left hierarchy must expose all five canonical papers with their own second-level sections: {selected['paperTocRoots']}/{selected['paperTocChildCounts']}")
        expected_registry_ids={"STRI","AGENT-SAFETY-R9","D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE","D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK","D2-PAPER-FAILURE-MEMORY-PROVENANCE"}
        require(selected["paperRegistrySummary"] == expected_registry_summary and selected["paperRegistrySummary"].get("scientific_holds") == 0 and selected["paperRegistryPanel"] == 1 and selected["paperRegistryCards"] == len(expected_registry_ids) and set(selected["paperRegistryIds"]) == expected_registry_ids and selected["paperRegistryStages"] == expected_registry_stages, f"PaperRegistry summary/UI is missing or stale relative to the current generated projection: {selected}")
        require(selected["noveltyPortfolio"] == 1 and selected["noveltyDetails"] == 5 and selected["noveltyDims"] == 25 and selected["noveltyNearest"] == 17 and selected["noveltyAdvisorQuestions"] == 5 and set(selected["noveltyIds"]) == expected_registry_ids, f"advisor novelty audit must cover all five PaperStates with five-dimensional comparisons and nearest work: {selected}")
        require(all(marker in selected["noveltyText"] for marker in ("4.5/5","Memory Reward Inflation","Remembering More, Risking More","Not All Skills Help","Memory Provenance Laundering","需要判断","建议下一步","只读文献 overlay")), f"paper novelty audit is missing decision-critical nearest-work or action markers: {selected['noveltyText'][:1800]}")
        require(selected["externalReviewPortfolio"] == 1 and selected["externalReviewDetails"] == 5 and selected["externalRepairCards"] == 15 and set(selected["externalReviewIds"]) == expected_registry_ids, f"Stanford external review overlay must cover all five PaperStates with three repair classes each: {selected}")
        require(selected["externalReviewScores"] == {"STRI":"6.1","AGENT-SAFETY-R9":"6.3","D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE":"6.3","D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK":"5.4","D2-PAPER-FAILURE-MEMORY-PROVENANCE":"5.4"}, f"Stanford Round-2 external review scores drifted: {selected['externalReviewScores']}")
        require(all(marker in selected["externalReviewText"] for marker in ("Round 2","Accept","Weak Accept","Weak Reject","Borderline-leaning Reject","非官方 ICLR 分数","文稿与定位","现有数据可补分析","需要新增证据 / 实验","5.8 → 5.4")), f"Round-2 external review/repair layer is missing reviewer recommendations or repair-plan markers: {selected['externalReviewText'][:2600]}")
        require(selected["objectionMatrixPortfolio"] == 1 and selected["objectionDetails"] == 5 and selected["objectionRows"] == 33 and selected["objectionDispositionCounts"] == {"RESOLVED":9,"EXISTING_EVIDENCE_ACTIONABLE":7,"REQUIRES_SCIENTIFIC_REOPEN":9,"PERMANENT_CLAIM_BOUNDARY":8}, f"Stanford Round-2 objection matrix must render 33 objections across the four legal dispositions: {selected}")
        require(all(marker in selected["objectionText"] for marker in ("33 条 objection","9 已解决","7 现有证据可补","9 需 scientific reopen","8 永久边界","0 AUTO ACTION","SAFETY-O3","SAFETY-O4","SAFETY-O5","TEMP-O2","TEMP-O5","PROXY-O5","FAILURE-O5")), f"Reviewer Objection Matrix is missing decision-critical disposition markers: {selected['objectionText'][:3200]}")
        require("598666122" not in selected["text"] and "rrPkIBax5D" not in selected["text"] and "QUnnU4wFKS" not in selected["text"], "public PaperRegistry must not expose Stanford review email or access tokens")
        temporal_selected=selected["temporalPaper"]
        temporal_selected_prep=temporal_selected.get("latest_paper_preparation") or {}
        temporal_selected_clean=temporal_selected_prep.get("pass") is True
        temporal_selected_action="NO_INTERNAL_ACTION" if temporal_selected_clean else "PAPER_REPAIR_REQUIRED"
        require(selected["paperRegistrySummary"] == expected_registry_summary and selected["paperRegistryGateClean"].get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK") == ("true" if temporal_selected_clean else "false") and selected["paperRegistryGateClean"].get("D2-PAPER-FAILURE-MEMORY-PROVENANCE") == "true" and selected["paperRegistryNextActions"].get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK") == temporal_selected_action and selected["paperRegistryNextActions"].get("D2-PAPER-FAILURE-MEMORY-PROVENANCE") == "NO_INTERNAL_ACTION" and int(temporal_selected_prep.get("required_gates") or 0) == 8 and (temporal_selected_clean or bool(temporal_selected_prep.get("blockers"))) and ((temporal_selected.get("latest_mock_review") or {}).get("summary") or {}).get("scores") == [8,8,7] and ((temporal_selected.get("source_native_evidence") or {}).get("runtime_valid_rows"),(temporal_selected.get("source_native_evidence") or {}).get("distinct_endpoints"),(temporal_selected.get("source_native_evidence") or {}).get("institutional_systems")) == (1326,35,3) and selected["failureMemoryPaper"].get("active_unrefuted_claims") == 2, f"PaperRegistry effective readiness must track latest receipts without losing Temporal evidence: {selected}")
        require(selected["currentPaper"].get("paper_id") == "STRI" and selected["currentPaper"].get("source_research_item") == "E-7" and selected["currentPaper"].get("paper_stage") == "SUBMISSION_READY" and selected["currentPaper"].get("scientific_status") == "READY" and selected["currentPaper"].get("submission_ready") is True and selected["currentPaper"].get("paper_quality_v2_passed") is True and selected["currentPaper"].get("paper_quality_content_addressed_completion") is True and selected["currentPaper"].get("paper_quality_content_addressed_files") == 29 and selected["currentPaper"].get("paper_quality_evidence_debt") == 0 and (selected["currentPaper"].get("qa_passed"),selected["currentPaper"].get("qa_total")) == (60,60) and (selected["currentPaper"].get("official_qa_passed"),selected["currentPaper"].get("official_qa_total")) == (60,60) and selected["currentPaper"].get("paper_quality_schema_version") == "2.1" and selected["currentPaper"].get("paper_quality_main_visualizations") == 4 and selected["currentPaper"].get("paper_visual_figure_qa") == "PASS" and selected["currentPaper"].get("supplement_unit_tests") == "29/29 PASS" and selected["currentPaper"].get("official_source_conflict") is False and selected["currentPaper"].get("deadline_status") == "AUTHOR_SUBMISSION_SOURCES_ALIGNED" and (selected["currentPaper"].get("latest_story_search") or {}).get("pass") is True and bool((selected["currentPaper"].get("mock_pc_modes") or {}).get("BLIND_MANUSCRIPT")) and bool((selected["currentPaper"].get("mock_pc_modes") or {}).get("ARTIFACT_AWARE")) and (selected["currentPaper"].get("latest_claim_audit") or {}).get("pass") is True and (selected["currentPaper"].get("latest_manuscript_ci") or {}).get("pass") is True and ((selected["currentPaper"].get("latest_manuscript_ci") or {}).get("passed"),(selected["currentPaper"].get("latest_manuscript_ci") or {}).get("required")) == (9,9) and (selected["currentPaper"].get("latest_prebuttal") or {}).get("pass") is True and int((selected["currentPaper"].get("latest_prebuttal") or {}).get("unresolved_decision_critical") or 0) == 0 and (selected["currentPaper"].get("latest_submission_readiness") or {}).get("submission_ready") is True and (selected["currentPaper"].get("latest_transition") or {}).get("from") == "PREBUTTAL" and (selected["currentPaper"].get("latest_transition") or {}).get("to") == "SUBMISSION_READY" and (selected["currentPaper"].get("authority") or {}).get("submission") is False and selected["currentStatus"].get("paper_ready") == 1, f"selected-paper current STRI projection is stale: {selected}")
        safety_paper=selected["agentSafetyPaper"]
        require(safety_paper.get("source_research_item") == "G-1" and safety_paper.get("paper_stage") == "SUBMISSION_READY" and safety_paper.get("scientific_status") == "READY" and safety_paper.get("submission_ready") is True and (safety_paper.get("latest_story_search") or {}).get("selected_story_id") == "S1-TEMPORAL-CERTIFICATE-CONTROL" and all((safety_paper.get("mock_pc_modes") or {}).get(mode) for mode in ("BLIND_MANUSCRIPT","ARTIFACT_AWARE")) and (safety_paper.get("latest_claim_audit") or {}).get("pass") is True and ((safety_paper.get("latest_manuscript_ci") or {}).get("passed"),(safety_paper.get("latest_manuscript_ci") or {}).get("required")) == (9,9) and (safety_paper.get("latest_prebuttal") or {}).get("decision_critical") == 9 and (safety_paper.get("latest_submission_readiness") or {}).get("submission_ready") is True and (safety_paper.get("authority") or {}).get("submission") is False, f"Agent Safety bounded R9 PaperState projection is stale: {safety_paper}")
        safety_acceptance=selected["agentSafetyAcceptance"]
        require(safety_acceptance.get("current_state") == "SUBMISSION_READY" and safety_acceptance.get("scientific_status") == "READY" and (safety_acceptance.get("latest_story_search") or {}).get("selected_story_id") == "S1-TEMPORAL-CERTIFICATE-CONTROL" and (safety_acceptance.get("latest_claim_audit") or {}).get("pass") is True and ((safety_acceptance.get("latest_manuscript_ci") or {}).get("passed"),(safety_acceptance.get("latest_manuscript_ci") or {}).get("required")) == (9,9) and (safety_acceptance.get("latest_prebuttal") or {}).get("decision_critical") == 9 and (safety_acceptance.get("latest_submission_readiness") or {}).get("submission_ready") is True and safety_acceptance.get("authority") == {"scientific":False,"experiment":False,"gpu":False,"submission":False}, f"canonical Agent Safety Paper Acceptance projection is stale or unsafe: {selected}")
        acceptance=selected["paperAcceptance"]
        require(acceptance.get("current_state") == "SUBMISSION_READY" and acceptance.get("scientific_status") == "READY" and (acceptance.get("latest_story_search") or {}).get("pass") is True and (acceptance.get("latest_story_search") or {}).get("selected_story_id") == "S1-INVARIANCE-BOUNDARY" and all((acceptance.get("mock_pc_modes") or {}).get(mode) for mode in ("BLIND_MANUSCRIPT","ARTIFACT_AWARE")) and (acceptance.get("latest_claim_audit") or {}).get("pass") is True and (acceptance.get("latest_manuscript_ci") or {}).get("pass") is True and ((acceptance.get("latest_manuscript_ci") or {}).get("passed"),(acceptance.get("latest_manuscript_ci") or {}).get("required")) == (9,9) and (acceptance.get("latest_prebuttal") or {}).get("pass") is True and int((acceptance.get("latest_prebuttal") or {}).get("unresolved_decision_critical") or 0) == 0 and (acceptance.get("latest_submission_readiness") or {}).get("submission_ready") is True and acceptance.get("authority") == {"scientific":False,"experiment":False,"gpu":False,"submission":False} and selected["paperAcceptanceSummary"].get("invalid_ledgers") == 0 and selected["paperAcceptanceSummary"].get("scientific_holds") == 0 and selected["paperAcceptanceSummary"].get("registered_papers") == expected_registry_summary.get("papers") and selected["paperAcceptanceSummary"].get("ledger_submission_ready_papers") == expected_registry_summary.get("submission_ready") and selected["paperAcceptanceSummary"].get("gate_clean_submission_ready_papers") == expected_registry_summary.get("gate_clean_submission_ready") and selected["paperAcceptanceSummary"].get("internal_action_required_papers") == expected_registry_summary.get("internal_action_required") and selected["paperAcceptanceSummary"].get("no_internal_action_papers") == expected_registry_summary.get("no_internal_action"), f"canonical STRI Paper Acceptance projection is stale or unsafe: {selected}")
        p0e = selected["currentDynamic"].get("skillrl_p0e") or {}
        require(p0e.get("status") == "STOP_FIXED_POLICY_DYNAMIC_BRIDGE" and p0e.get("persistent_principle_dead_end_certified") is False and p0e.get("principle_disposition") == "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED" and p0e.get("stage2_locked") is True and p0e.get("new_gpu_authorized") is False and (p0e.get("calibration") or {}).get("calibration_pristine_success") == 18 and (p0e.get("calibration") or {}).get("paired_units") == 24, f"selected-paper P0-E boundary is stale: {selected}")
        autoskill = selected["currentDynamic"].get("autoskill_p19") or {}
        groups = autoskill.get("groups") or {}
        mediator = autoskill.get("mediator_isolation") or {}
        mgroups = mediator.get("groups") or {}
        review = selected["currentPaper"].get("post_isolation_review") or {}
        require(autoskill.get("status") == "GO_STAGE3_DYNAMIC_BEHAVIORAL_PROPAGATION" and groups.get("A_original",{}).get("destructive_signature_positive") == 6 and groups.get("B_split4",{}).get("destructive_signature_positive") == 0 and groups.get("C_id_placebo",{}).get("destructive_signature_positive") == 3 and groups.get("D_quotient_control",{}).get("destructive_signature_positive") == 3 and abs(float(autoskill.get("fisher_exact_p") or 1.0) - 0.0010822510822510823) < 1e-12 and autoskill.get("judge_calls") == 0 and autoskill.get("fresh_container_per_run") is True and mediator.get("status") == "GO_MEDIATOR_ISOLATION_P19" and mgroups.get("E_post_addback",{}).get("positive") == 3 and mgroups.get("F_cleanup_control",{}).get("positive") == 0 and (mediator.get("statistics") or {}).get("exact_fraction") == "1/20" and (mediator.get("measurement_repair") or {}).get("stage3_replay_agreement") == "18/18" and review.get("deepseek_pre_score") == 4 and review.get("deepseek_post_score") == 6 and review.get("decision") == "FREEZE_NARROW_SUBMISSION_NO_FURTHER_EXPERIMENT_SCORE_CHASING", f"selected-paper AutoSkill P19 dynamic/mediator/review evidence is stale: {selected}")
        require("PaperRegistry" in selected["title"] and "PaperRegistry" in selected["text"] and "SUBMISSION_READY" in selected["text"] and "AGENT-SAFETY-R9" in selected["text"] and "关键因果对照" in selected["text"] and "4 update-only / 0 control-only" in selected["text"] and "2026-09-18" in selected["text"] and "2026-09-25" in selected["text"] and ("Former Regression-Gated Self-Evolution workspace" in selected["text"] or "旧 Regression-Gated Self-Evolution 工作区" in selected["text"]), f"selected-paper PaperRegistry/current/historical hierarchy is wrong: {selected}")
        require("only permits a new shadow qualification" not in selected["text"] and "Historical ICLR Paper Workspace" not in selected["title"] and "[object Object]" not in selected["text"], f"selected-paper leaked stale shadow, nested-boundary rendering, or historical-primary framing: {selected}")
        selected_markers = ("30 秒总览","快速阅读顺序：先回答 5 个大问题","PaperRegistry · 系统审计总账","ledger SUBMISSION_READY=5","最新有效投稿门禁",expected_registry_titles["D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK"],expected_registry_titles["D2-PAPER-FAILURE-MEMORY-PROVENANCE"],"中央机制证据","1,326 rows","35 endpoints","Mock-PC=8/8/7","TimeSage-EV 精确复现","关键因果对照","4 update-only / 0 control-only","论文硬门","CANONICAL PAPER LEDGER · 投稿闭环真值","S1-INVARIANCE-BOUNDARY","Blind Manuscript","Artifact-aware","Claim Audit","Manuscript CI=9/9 PASS","Prebuttal=PASS","Submission Ready receipt=","0 AUTO AUTHORITY","科学主张","N1 · AutoSkill P19 动态机制证据","6/6","0/6","post-checkout 加回=3/3","匹配清理对照=0/3","精确 p=1/20","Stage-3 复放=18/18","独立审稿后决策","4/10","6/10","哪些动态实验进入了主张，哪些没有","论文证据是否齐全且能追到固定文件","ICLR 投稿包","可视化证据","Paper Acceptance 当前阶段","Story Search=PASS","已发布控制平面上的表示敏感性","是否声称求解算法本身是新贡献")
        missing_selected_markers = [marker for marker in selected_markers if marker not in selected["text"]]
        require(not missing_selected_markers, f"selected-paper Chinese-first current-paper UI is incomplete; missing={missing_selected_markers}")
        require(set(selected["submissionDownloads"]) == set((selected["currentPaper"].get("downloads") or {}).values()), f"selected-paper STRI downloads must match current PaperRegistry.downloads: {selected['submissionDownloads']} vs {selected['currentPaper'].get('downloads')}")
        require(set(selected["agentSafetyDownloads"]) == set((selected["agentSafetyPaper"].get("downloads") or {}).values()), f"selected-paper Agent Safety downloads must match current PaperRegistry.downloads: {selected['agentSafetyDownloads']} vs {selected['agentSafetyPaper'].get('downloads')}")
        require("Paper Acceptance Ledger 的 scientific / experiment / GPU / submission 自动权限全部为 0" in selected["text"] and "论文侧闭环已经完成" in selected["text"] and "真正提交仍需要外部人工投稿权限" in selected["text"] and "Human authors review and accept responsibility" not in selected["text"], "PaperRegistry must show the submission-ready human-authority boundary without leaking the stale raw legacy handoff")

        navigate("/experiments.html", 4)
        ensure_language("zh")
        experiments_zh = execute(session_id, "return document.body.textContent || ''")
        experiment_markers = ("先看当前实验结论","N1 动态机制证据：表示→检索→被挤出的技能→执行行为","6/6","0/6","post-checkout 加回=3/3","匹配清理对照=0/3","精确 Fisher=1/20","Stage-3 复放=18/18","额外检查 A：提案器是否具备继续实验的基本能力","额外检查 E：更完整策略是否真的会改变最终结果","以前的记忆效应 · 为什么不继续","0 个正式实验可启动")
        missing_experiment_markers = [marker for marker in experiment_markers if marker not in experiments_zh]
        if missing_experiment_markers:
            anchor = experiments_zh.find("N1 动态机制证据")
            snippet = experiments_zh[max(0, anchor-120):anchor+1200] if anchor >= 0 else experiments_zh[:1200]
            raise AssertionError(f"Experiments Chinese-first current-evidence UI is incomplete; missing={missing_experiment_markers}; snippet={snippet}")
        experiment_disposition_leaks = (
            "Use frozen existing P0 evidence; do not rerun identical compute.",
            "Merge branch soft-audit into research-system scheduling; stop standalone A-1 repair and do not spend GPU unless a materially new observable/substrate is proposed.",
            "Merge evidence-depth scheduling into A-1/system soft audit; stop standalone A-2 repair and do not launch controller GPU training.",
        )
        require(not any(marker in experiments_zh for marker in experiment_disposition_leaks), f"Experiments Chinese view still leaks historical English dispositions: {[m for m in experiment_disposition_leaks if m in experiments_zh]}")

        navigate("/bibliography.html", 8)
        bibliography_zh = execute(session_id, "return document.body.textContent || ''")
        require(all(marker in bibliography_zh for marker in ("正式发表","预印本","代码仓库","博客/报告","Agent 组件","模型参数","工具/技能","工作流/脚手架","批评/评测","环境交互","最近增量核验","+33 篇","key 不进入网页")), "Bibliography filters/maps/cards or incremental refresh provenance are not localized to Chinese display labels")

        navigate("/mechanisms.html#field-evaluation-safety", 4)
        evaluation_zh = execute(session_id, "return document.body.textContent || ''")
        require(all(marker in evaluation_zh for marker in ("初始化","提出更新","部署使用","运行脚手架（Harness）基线","谱系组合遗憾（regret）")), "Consolidated field-matrix evaluation terminology is not Chinese-first")

        # Site-wide navigation/readability contract: every canonical page must use the same
        # global language state and the exact same left navigation labels. Literature stays
        # expanded everywhere so readers can jump to the bibliography without another click.
        canonical_frontend_pages = (
            "/index.html", "/foundations.html", "/mechanisms.html",
            "/system-overview.html", "/research-map.html", "/research-timeline.html", "/research-directions.html",
            "/paper-ideas.html", "/experiments.html", "/selected-paper.html", "/bibliography.html",
        )
        execute(session_id, "localStorage.setItem('agent-evolution-language','zh');")
        request("POST", f"/session/{session_id}/window/rect", {"width": 1440, "height": 1000, "x": 0, "y": 0})
        sidebar_signature = None
        for frontend_page in canonical_frontend_pages:
            navigate(frontend_page, 2)
            nav_contract = execute(session_id, """const groups=[...document.querySelectorAll('.sidebar .nav > details.nav-group')].map(d=>({
                title:(d.querySelector('summary span')?.textContent||'').trim(),
                open:d.open,
                links:[...d.querySelectorAll('a.nav-level2')].map(a=>[(a.textContent||'').trim(),a.getAttribute('href')||''])
              }));
              const literature=groups.find(g=>g.links.some(x=>x[1]==='bibliography.html'))||null;
              return {lang:document.documentElement.lang,groups,literatureOpen:!!literature?.open,roleTerm:(document.body.textContent||'').includes('师兄')};""")
            require(nav_contract["lang"] == "zh-CN", f"{frontend_page} did not honor the shared Chinese sidebar language state: {nav_contract}")
            require(nav_contract["literatureOpen"], f"{frontend_page} must keep the Literature navigation group expanded")
            require(not nav_contract["roleTerm"], f"{frontend_page} still renders a role-specific decision label")
            require([group["title"] for group in nav_contract["groups"]] == ["开始阅读","领域图谱","当前科研","文献"], f"{frontend_page} sidebar group names drifted: {nav_contract['groups']}")
            current_signature = [(group["title"], tuple(tuple(link) for link in group["links"])) for group in nav_contract["groups"]]
            if sidebar_signature is None:
                sidebar_signature = current_signature
            else:
                require(current_signature == sidebar_signature, f"{frontend_page} sidebar labels/targets differ from the canonical navigation: {current_signature}")
            site_readability = execute(session_id, """document.querySelectorAll('#dynamic-page details').forEach(x=>x.open=true);
              const visible=e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&Number(s.opacity)>0&&r.width>0&&r.height>0};
              const own=e=>[...e.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent.trim()).filter(Boolean).join(' ');
              const rows=[...document.querySelectorAll('.layout *')].filter(visible).map(e=>({e,t:own(e)})).filter(x=>x.t);
              const withoutMachineIds=t=>t
                .replace(/\\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\\b/g,'')
                .replace(/\\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\\b/g,'')
                .replace(/\\b[a-z0-9]+(?:-[a-z0-9]+){2,}\\b/g,'')
                .replace(/\\b[a-f0-9]{12,64}\\b/g,'');
              const mixed=rows.filter(x=>{const t=withoutMachineIds(x.t);return /[\\u3400-\\u9fff]/.test(t)&&/\\b(?:Idea|Fresh|Shadow|Paper-first|Paper Design|Method Design|Memory|Workflow|Baseline|Pilot|standalone|thesis|support-pass|support-hold|scientific authority|qualification|provider|operator|formulation|matched baseline|dead-end|Evaluation and Benchmarks|Paper \\/ technical report)\\b/i.test(t)}).map(x=>x.t);
              const tiny=rows.map(x=>({tag:x.e.tagName,px:parseFloat(getComputedStyle(x.e).fontSize)||99,t:x.t})).filter(x=>x.px<11.49);
              const prose=rows.map(x=>({tag:x.e.tagName,px:parseFloat(getComputedStyle(x.e).fontSize)||99,t:x.t})).filter(x=>['P','LI','TD','DD'].includes(x.tag)&&x.px<11.99);
              return {lang:document.documentElement.lang,mixed,tiny,prose,toc4:document.querySelectorAll('#page-toc .toc-level-4').length};""")
            require(site_readability["lang"] == "zh-CN", f"{frontend_page} did not remain in Chinese mode: {site_readability}")
            require(not site_readability["mixed"], f"{frontend_page} regressed to mixed English explanatory prose: {site_readability['mixed'][:4]}")
            require(not site_readability["tiny"] and not site_readability["prose"], f"{frontend_page} violates the site-wide font floor: tiny={site_readability['tiny'][:3]} prose={site_readability['prose'][:3]}")
            require(site_readability["toc4"] == 0, f"{frontend_page} sidebar TOC must stop at H3, got H4 entries")

        request("POST", f"/session/{session_id}/window/rect", {"width": 500, "height": 844, "x": 0, "y": 0})
        for frontend_page in canonical_frontend_pages:
            navigate(frontend_page, 1)
            mobile_width = execute(session_id, """const inner=window.innerWidth,scroll=document.documentElement.scrollWidth; const offenders=[...document.querySelectorAll('body *')].map(e=>{const r=e.getBoundingClientRect();return {tag:e.tagName,cls:e.className||'',left:Math.round(r.left),right:Math.round(r.right),width:Math.round(r.width),scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,text:(e.textContent||'').trim().slice(0,180)}}).filter(x=>x.right>inner+2||x.left<-2).sort((a,b)=>b.right-a.right).slice(0,8); return {inner,scroll,offenders};""")
            require(mobile_width["scroll"] <= mobile_width["inner"] + 2, f"{frontend_page} has page-level horizontal overflow on mobile-width viewport: {mobile_width}")

        redirect_checks = {
            "/memory-evolution.html": "mechanisms.html#field-memory",
            "/domains.html": "mechanisms.html#chapter-domain-axis",
            "/evaluation.html": "mechanisms.html#chapter-evidence-axis",
            "/direction-board.html": "paper-ideas.html#discussed-ideas",
            "/paper-roadmap.html": "selected-paper.html#group-paper-roadmap",
        }
        for old_path, expected_suffix in redirect_checks.items():
            navigate(old_path, 2)
            redirected = execute(session_id, "return location.href")
            require(redirected.endswith(expected_suffix), f"{old_path} did not redirect to {expected_suffix}")

        request("POST", f"/session/{session_id}/window/rect", {"width": 390, "height": 844, "x": 0, "y": 0})
        navigate("/system-overview.html", 4)
        mobile_system = execute(session_id, """const xs=[...document.querySelectorAll('#dynamic-page *')].filter(e=>{const r=e.getBoundingClientRect();return (e.textContent||'').trim()&&r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden'&&e.children.length===0}).map(e=>parseFloat(getComputedStyle(e).fontSize)).filter(Number.isFinite); return {minFont:xs.length?Math.min(...xs):0,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2};""")
        require(mobile_system["minFont"] >= 11.5 and not mobile_system["overflow"], f"mobile system overview readability/overflow regression: {mobile_system}")
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
