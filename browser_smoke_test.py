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
        require(home["nav"] == 20, f"expected 20 primary navigation targets after adding the experiment-cost page, got {home['nav']}")
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
              memorySummary: window.RESEARCH_MEMORY_WIKI?.summary || window.RESEARCH_SYSTEM_STATE?.research_memory_wiki?.summary || {},
              memoryLint: window.RESEARCH_MEMORY_WIKI?.lint?.summary || window.RESEARCH_SYSTEM_STATE?.research_memory_wiki?.lint?.summary || {},
              paperDevelopmentGuidance: (window.RESEARCH_MEMORY_WIKI?.entries || []).filter(x=>x.kind==='PAPER_DEVELOPMENT_GUIDANCE').map(x=>x.guidance || {}),
              iclrTemplate: window.ICLR_AGENT_PAPER_TEMPLATE || {},
              iclrTemplatePanels: document.querySelectorAll('.iclr-paper-template').length,
              iclrTemplatePages: document.querySelectorAll('.iclr-template-page').length,
              iclrTemplateLanes: document.querySelectorAll('.iclr-template-lane').length,
              discoveryLessonSection: document.querySelectorAll('[data-discovery-lesson-section]').length,
              discoveryLessonCards: document.querySelectorAll('[data-discovery-lesson]').length,
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
        require((system_overview["architectureSummary"].get("temporal_stages"),system_overview["architectureSummary"].get("reader_chapters"),system_overview["architectureSummary"].get("reader_stage_coverage"),system_overview["architectureSummary"].get("reader_stage_missing"),system_overview["architectureSummary"].get("reader_stage_duplicates"),system_overview["architectureSummary"].get("reader_stage_extra"),system_overview["architectureSummary"].get("functional_layers"),system_overview["architectureSummary"].get("assigned_components"),system_overview["architectureSummary"].get("unassigned_components"),system_overview["architectureSummary"].get("cross_cutting_controls"),system_overview["architectureSummary"].get("orphan_cross_cutting_controls")) == (21,10,21,0,0,0,6,33,0,3,0), f"backend architecture manifest is stale in browser state: {system_overview['architectureSummary']}")
        require(system_overview["methodologyControls"] == 3 and "Are candidate problems too similar?" in system_overview["text"] and "Freeze the setup before results and check leakage" in system_overview["text"] and "Can another person rerun the key result from scratch?" in system_overview["text"], f"plain-language methodology controls are missing: {system_overview['methodologyControls']}")
        discovery_lesson_count = int(system_overview["memorySummary"].get("discovery_lessons") or 0)
        require(system_overview["memorySummary"].get("entries") >= 50 and int(system_overview["memorySummary"].get("scientific_closures") or 0) == int(system_overview["searchClosureSummary"].get("core_principle_dead_ends") or 0) and int(system_overview["memorySummary"].get("search_closures") or 0) + int(system_overview["memorySummary"].get("scientific_closures") or 0) == int(system_overview["searchClosureSummary"].get("shadow_closed_basins") or 0) and system_overview["memorySummary"].get("failure_assets") >= 3 and system_overview["memorySummary"].get("success_assets") >= 3 and discovery_lesson_count >= 19 and system_overview["memorySummary"].get("paper_development_guidance") == 1 and system_overview["memoryLint"].get("errors") == 0, f"Research Memory Wiki state is missing or inconsistent with canonical typed closures/discovery lessons/development guidance: summary={system_overview['memorySummary']} canonical={system_overview['searchClosureSummary']} lint={system_overview['memoryLint']}")
        require(system_overview["discoveryLessonSection"] == 1 and system_overview["discoveryLessonCards"] == discovery_lesson_count and "DISCOVERY_LESSON" in system_overview["text"], f"all canonical Discovery Lessons must be visibly rendered from Research Memory: expected={discovery_lesson_count} section={system_overview['discoveryLessonSection']} cards={system_overview['discoveryLessonCards']}")
        require(len(system_overview["paperDevelopmentGuidance"]) == 1 and len((system_overview["paperDevelopmentGuidance"][0] or {}).get("dimensions") or []) == 4 and len((system_overview["paperDevelopmentGuidance"][0] or {}).get("paper_development_backlog") or []) == 5 and (system_overview["paperDevelopmentGuidance"][0].get("authority") or {}) == {"scientific":False,"method":False,"experiment":False,"gpu":False,"submission":False}, f"senior paper-development guidance is missing or leaked authority: {system_overview['paperDevelopmentGuidance']}")
        tpl=system_overview["iclrTemplate"] or {};tpl_lanes=tpl.get("experiment_lanes") or []
        require(system_overview["iclrTemplatePanels"] == 1 and system_overview["iclrTemplatePages"] == 7 and system_overview["iclrTemplateLanes"] == 7 and len(tpl.get("derived_from") or []) == 8 and sum(row.get("required") is True for row in tpl_lanes) == 6 and abs(sum(float(row.get("pages") or 0) for row in tpl.get("page_budget_main_body") or [])-9.0)<1e-9 and all(value is False for value in (tpl.get("authority") or {}).values()), f"ICLR manuscript template is missing/stale or leaked authority: panel={system_overview['iclrTemplatePanels']} pages={system_overview['iclrTemplatePages']} lanes={system_overview['iclrTemplateLanes']} template={tpl}")
        require(all(marker in system_overview["text"] for marker in ("Scientific closure is not the same as manuscript maturity","Problem necessity, challenge, and related work","Method intuition, design principles, and load-bearing details","A complete experimental program, not a single main table","Plain, direct, reader-comprehensible writing","ICLR PAPER TEMPLATE V1","E1 · Main comparison","E6 · Efficiency / cost / scale","answer → evidence → interpretation → boundary")), "Paper Development Quality / ICLR template is missing from the rendered System Overview")
        require(("失败 Wiki 已经进入下一轮搜索和实验设计" in system_overview["text"] or "failure wiki is now consumed by the next search and experiment design" in system_overview["text"]) and ("一次运行故障不会污染长期科研记忆" in system_overview["text"] or "One operational glitch cannot poison long-term research memory" in system_overview["text"]), "Research Memory Wiki explanation is missing from System Overview")
        require(system_overview["aiCheckpoints"] == 5, f"AI consultation checkpoint strip is incomplete: {system_overview['aiCheckpoints']}")
        require(system_overview["governanceStages"] == 7, f"P0-System v2 must expose seven scientific stages, got {system_overview['governanceStages']}")
        require(system_overview["outerGates"] == 8 and system_overview["preflightGates"] == 10 and system_overview["quantWorksheets"] == 2, f"Pre-Experiment/identifiability compiler is incomplete: {system_overview['outerGates']}/{system_overview['preflightGates']}/{system_overview['quantWorksheets']}")
        require(system_overview["lessons"] == 6 + system_overview["discoveryLessonCards"] and system_overview["failureLayers"] == 7 and system_overview["repairLoops"] == 1, f"system learning/diagnosis visualization is incomplete: {system_overview['lessons']}/{system_overview['failureLayers']}/{system_overview['repairLoops']}")
        require(system_overview["artifacts"] >= 14 and system_overview["boundaries"] == 9, f"artifact or automation-boundary documentation is incomplete: {system_overview['artifacts']}/{system_overview['boundaries']}")
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
        require(all(marker in zh_system["readerText"] for marker in ("输入","核心判断","阶段产出","先确认异常现象真实存在","最后才做正式科学筛选","这个最小实验无论成功或失败，都会改变下一步吗","方法稳定后冻结版本","论文每条主张是否都有直接证据","科学闭环不等于论文已经成熟","问题必要性、Challenge 与 Related Work","方法核心 Intuition、设计理念与全部关键细节","更完整的实验 Program，而不是只有一张主表","讲人话：清晰、直白、易懂的论文写作","自动重放旧案例","谁能提建议、谁能启动实验、谁能改论文结论")), "Chinese reader flow is missing the plain-language research decisions or Paper Development Quality guidance")
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
                require(("论文合集" in result["text"] or "Paper Collection" in result["text"]) and "E1 · STRI" in result["text"] and "Constraint Externality" in result["text"], "selected-paper must remain a compact nine-paper collection rather than a duplicated detail workspace")

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
        require(zh_state["brand"] == ["Agent 自进化","科研观测站"] and "开始阅读" in zh_state["nav"] and "领域图谱" in zh_state["nav"] and "当前科研" in zh_state["nav"] and "参考文献" in zh_state["nav"] and "Start Here" not in zh_state["nav"] and zh_state["placeholder"] == "搜索研究站内容…", f"shared shell did not fully switch to Chinese: {zh_state}")

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
        require(registry_summary == expected_registry_summary and {pid:row.get("paper_stage") for pid,row in registry_papers.items()} == expected_registry_stages and registry_summary.get("scientific_holds") == 0 and registry_papers.get("STRI",{}).get("source_research_item") == "E-7" and registry_papers.get("STRI",{}).get("paper_stage") == "SUBMISSION_READY" and registry_papers.get("STRI",{}).get("submission_ready") is True and registry_papers.get("AGENT-SAFETY-R9",{}).get("source_research_item") == "G-1" and registry_papers.get("AGENT-SAFETY-R9",{}).get("paper_stage") == expected_registry_stages.get("AGENT-SAFETY-R9") and (registry_papers.get("AGENT-SAFETY-R9",{}).get("primary_next_action") or {}).get("action_class") == "EXTERNAL_EVIDENCE_REQUIRED" and (registry_papers.get("AGENT-SAFETY-R9",{}).get("primary_next_action") or {}).get("blocking_on") == "HUMAN_SEMANTIC_LABEL_EVIDENCE_REQUIRED" and registry_papers.get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",{}).get("paper_stage") == "SUBMISSION_READY" and registry_papers.get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",{}).get("source_research_item") is None and registry_papers.get("D2-PAPER-FAILURE-MEMORY-PROVENANCE",{}).get("source_kind") == "paper-first-discovery-candidate", f"Research Portfolio must match the current PaperRegistry projection while preserving D2 paper-first provenance and G-1 broader HOLD: {idea_portfolio['paperRegistry']}")
        temporal_registry=registry_papers.get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",{})
        failure_registry=registry_papers.get("D2-PAPER-FAILURE-MEMORY-PROVENANCE",{})
        temporal_evidence=temporal_registry.get("source_native_evidence") or {}
        temporal_review=(temporal_registry.get("latest_mock_review") or {}).get("summary") or {}
        temporal_prep=temporal_registry.get("latest_paper_preparation") or {}
        temporal_clean=temporal_prep.get("pass") is True
        temporal_action="NO_INTERNAL_ACTION" if temporal_clean else "PAPER_REPAIR_REQUIRED"
        require(registry_summary == expected_registry_summary and temporal_registry.get("paper_stage") == expected_registry_stages.get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK") and temporal_registry.get("gate_clean_submission_ready") is temporal_clean and temporal_registry.get("immediate_submission_hold") is (not temporal_clean) and (temporal_registry.get("primary_next_action") or {}).get("action_class") == temporal_action and int(temporal_prep.get("required_gates") or 0) == 8 and (temporal_clean or bool(temporal_prep.get("blockers"))) and int(temporal_evidence.get("runtime_valid_rows") or 0) > 0 and int(temporal_evidence.get("distinct_endpoints") or 0) > 0 and int(temporal_evidence.get("institutional_systems") or 0) > 0 and bool(temporal_registry.get("latest_mock_review")) and failure_registry.get("paper_stage") == expected_registry_stages.get("D2-PAPER-FAILURE-MEMORY-PROVENANCE") and failure_registry.get("gate_clean_submission_ready") is True and failure_registry.get("supported_claims") == 6 and failure_registry.get("active_unrefuted_claims") == 0, f"Research Portfolio must follow the latest canonical Temporal/Failure paper receipts without pinning an obsolete revision snapshot: {idea_portfolio['paperRegistry']}")
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
          cards: document.querySelectorAll('.cpp-collection-card').length,
          formal: document.querySelectorAll('#formal-paper-collection .cpp-collection-card').length,
          working: document.querySelectorAll('#working-paper-collection .cpp-collection-card').length,
          detailSections: document.querySelectorAll('.paper-detail-section,.cpp-origin,.cpp-resource-columns,.cpp-proof-grid').length,
          labels: [...document.querySelectorAll('.cpp-collection-card header>span')].map(x=>x.textContent.trim()),
          titles: [...document.querySelectorAll('.cpp-collection-card h3')].map(x=>x.textContent.trim()),
          toc: [...document.querySelectorAll('#page-toc a')].map(x=>x.textContent.trim()),
          budgetRows: document.querySelectorAll('#paper-resource-budget .cpp-budget-table tbody tr').length,
          atomgitRows: document.querySelectorAll('#paper-resource-budget .cpp-atomgit-tag').length,
          atomgitSourceLinks: document.querySelectorAll('#atomgit-pro-allocation .cpp-budget-sources a').length,
          paperRegistrySummary: window.PAPER_REGISTRY?.summary || {},
          overflow: document.documentElement.scrollWidth>document.documentElement.clientWidth+2,
          text: document.body.textContent || ''
        };""")
        require(selected["cards"] == 9 and selected["formal"] == 5 and selected["working"] == 4 and selected["detailSections"] == 0 and selected["toc"] == ["实验资源与成本预算","AtomGit Pro 分配","①–⑤ 正式论文","⑥–⑨ 工作论文 / Scientific Object"] and selected["budgetRows"] == 9 and selected["atomgitRows"] == 9 and selected["atomgitSourceLinks"] == 3 and selected["paperRegistrySummary"] == expected_registry_summary and not selected["overflow"], f"selected-paper must remain a nine-paper routing surface with the portfolio resource budget: {selected}")
        require(selected["labels"][:5] == ["① E1 · STRI","② G1 · Temporal Safety","③ C1 · Memory Transport","④ E2 · Search Projection","⑤ B1 · Memory Provenance"] and selected["labels"][7] == "⑧ Constraint Externality" and selected["labels"][8] == "⑨ 3D · Relational Topology", f"paper collection labels/order drifted: {selected['labels']}")
        require("速览版" not in selected["text"] and "完整 PaperState" not in selected["text"] and "Stanford" not in selected["text"], "collection page must not duplicate single-paper detail/review content")

        paper_pages = [
          ("/paper-e1.html", True, ("R*(A)","AutoSkill P19","12 / 32")),
          ("/paper-g1.html", True, ("BrowserART + AWM","HB 0/12","DS 3/12")),
          ("/paper-c1.html", True, ("Shopping","125/172","0.700 vs 0.595")),
          ("/paper-e2.html", True, ("48 matched pairs","17 / 48","R17 · 17/48 · 效果 unopened")),
          ("/paper-b1.html", True, ("350 / 350","+3.125 pp","0.0 pp")),
          ("/paper-a.html", False, ("MemoryVLA","LIBERO-Plus","0.5541")),
          ("/paper-b.html", False, ("MemoryVLA","24 scopes","longitudinal")),
          ("/paper-agent-constraint.html", False, ("AppWorld-derived matched families","Direct-SFQ-A0","24 → TO-V → N*","TARGET_ONLY_VERIFICATION","SHAM_UPDATE","Same-App-k")),
          ("/paper-3d.html", False, ("InstructScene","3D-FRONT / 3D-FUTURE","SceneNAT")),
        ]
        for page, formal_story, markers in paper_pages:
            navigate(page, 4)
            ensure_language("zh")
            paper_view = execute(session_id, """return {
              quick: document.querySelectorAll('#quick-overview').length,
              quickLabel: document.querySelector('#quick-overview .cpp-section-kicker')?.textContent.trim()||'',
              otherPaperCards: document.querySelectorAll('.cpp-collection-card,.cpp-shelf-card').length,
              pager: document.querySelectorAll('.cpp-pager').length,
              modelCards: document.querySelectorAll('#models-data .cpp-resource-columns>section:first-child .cpp-resource-card').length,
              dataCards: document.querySelectorAll('#models-data .cpp-resource-columns>section:last-child .cpp-resource-card').length,
              design: document.querySelectorAll('#experiment-design .cpp-design-lead').length,
              proofCards: document.querySelectorAll('#experiment-results .cpp-proof-grid article').length,
              evolution: document.querySelectorAll('#paper-evolution .cpp-evolution article').length,
              origin: document.querySelectorAll('#problem-origin .cpp-origin-grid article').length,
              registry: document.querySelectorAll('#paper-state').length,
              download: document.querySelector('.cpp-hero .cpp-download-primary')?.getAttribute('href')||'',
              deepDiveClosed: !!document.querySelector('#research-archive:not([open])'),
              back: [...document.querySelectorAll('a')].some(a=>a.getAttribute('href')==='selected-paper.html'),
              overflow: document.documentElement.scrollWidth>document.documentElement.clientWidth+2
            };""")
            expected_quick_label = "0 · 先看懂问题"
            require(paper_view["quick"] == 1 and paper_view["quickLabel"] == expected_quick_label and paper_view["otherPaperCards"] == 0 and paper_view["pager"] == 0 and paper_view["modelCards"] >= 2 and paper_view["dataCards"] >= 2 and paper_view["design"] == 1 and paper_view["proofCards"] >= 3 and paper_view["evolution"] >= 6 and paper_view["origin"] >= 3 and paper_view["back"] and paper_view["deepDiveClosed"] and not paper_view["overflow"], f"beginner-first single-paper reader contract failed for {page}: {paper_view}")
            require((paper_view["registry"] == 1) is formal_story, f"PaperRegistry identity contract failed for {page}: {paper_view}")
            require(bool(paper_view["download"]) is formal_story, f"formal papers must expose the PDF action in the hero and working/scientific-object pages must not invent one: {page} {paper_view}")
            if page == "/paper-e1.html":
                require(paper_view["download"] == "downloads/E1-STRI.pdf", f"E1 PDF target changed unexpectedly: {paper_view}")
            marker_check = execute(session_id, """const compact=s=>String(s).replace(/\\s+/g,'');const t=document.body.textContent||'';const c=compact(t);return {required:arguments[0].map(x=>c.includes(compact(x))),forbidden:c.includes(compact(arguments[1])),fffd:(t.match(/\uFFFD/g)||[]).length};""", [list(markers), "讲给小白听"])
            require(marker_check["fffd"] == 0 and not marker_check["forbidden"] and all(marker_check["required"]), f"single-paper content markers missing/corrupt for {page}: markers={markers} check={marker_check}")

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
            "/system-overview.html", "/experiment-costs.html", "/research-map.html", "/research-timeline.html", "/research-directions.html",
            "/paper-ideas.html", "/experiments.html", "/selected-paper.html",
            "/paper-e1.html", "/paper-g1.html", "/paper-c1.html", "/paper-e2.html", "/paper-b1.html",
            "/paper-a.html", "/paper-b.html", "/paper-agent-constraint.html", "/paper-3d.html",
            "/bibliography.html",
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
              const currentFile=location.pathname.split('/').pop()||'index.html';
              const currentListed=groups.some(g=>g.links.some(x=>x[1]===currentFile));
              return {lang:document.documentElement.lang,groups,allClosed:groups.every(g=>!g.open),activeGroups:document.querySelectorAll('.sidebar .nav > details.nav-group.active-group').length,currentListed,roleTerm:(document.body.textContent||'').includes('师兄')};""")
            require(nav_contract["lang"] == "zh-CN", f"{frontend_page} did not honor the shared Chinese sidebar language state: {nav_contract}")
            require(nav_contract["allClosed"] and nav_contract["activeGroups"] == (1 if nav_contract["currentListed"] else 0), f"{frontend_page} must load with all sidebar groups collapsed and mark the current group only when the page is listed: {nav_contract}")
            require(not nav_contract["roleTerm"], f"{frontend_page} still renders a role-specific decision label")
            require([group["title"] for group in nav_contract["groups"]] == ["开始阅读","领域图谱","当前科研","参考文献"], f"{frontend_page} sidebar group names drifted: {nav_contract['groups']}")
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
            "/paper-roadmap.html": "selected-paper.html",
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
