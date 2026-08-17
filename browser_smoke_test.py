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
        require(home["nav"] == 11, f"expected 11 canonical navigation targets, got {home['nav']}")
        require(home["figure"], "knowledge-map figure is missing")
        require(home["distribution"] >= 6, "live update-surface distribution is missing")
        require(home["missing"] == 0, "home contains unresolved citations")
        require(home["corpus"] >= 100, "curated literature snapshot did not load")

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
              links: [...document.querySelectorAll('a')].map(x=>x.getAttribute('href')||''),
              text: document.body.textContent || ''
            };""",
        )
        require(system_overview["chapters"] == 7 and system_overview["readerChapters"] == 7 and system_overview["readerPhases"] == 6 and system_overview["deepDives"] == 4 and system_overview["authorityCards"] == 3, f"system overview reading framework is incomplete: chapters={system_overview['chapters']} roadmap={system_overview['readerChapters']} phases={system_overview['readerPhases']} deep={system_overview['deepDives']} authority={system_overview['authorityCards']}")
        require(system_overview["toc2"] >= 7 and system_overview["toc4"] == 0, f"system overview hierarchy is wrong: {system_overview['toc2']}/{system_overview['toc3']}/{system_overview['toc4']}")
        require(system_overview["stats"] == 6, f"research-system hero statistics are incomplete: {system_overview['stats']}")
        require(system_overview["readerChapters"] == 7 and system_overview["responsibilityLayers"] == 6 and system_overview["lifecycleSteps"] == 11 and system_overview["componentLayerHeaders"] == 6, f"canonical architecture is incomplete: reader={system_overview['readerChapters']} layers={system_overview['responsibilityLayers']} stages={system_overview['lifecycleSteps']} component-groups={system_overview['componentLayerHeaders']}")
        require((system_overview["architectureSummary"].get("temporal_stages"),system_overview["architectureSummary"].get("reader_chapters"),system_overview["architectureSummary"].get("reader_stage_coverage"),system_overview["architectureSummary"].get("reader_stage_missing"),system_overview["architectureSummary"].get("reader_stage_duplicates"),system_overview["architectureSummary"].get("reader_stage_extra"),system_overview["architectureSummary"].get("functional_layers"),system_overview["architectureSummary"].get("assigned_components"),system_overview["architectureSummary"].get("unassigned_components"),system_overview["architectureSummary"].get("cross_cutting_controls"),system_overview["architectureSummary"].get("orphan_cross_cutting_controls")) == (11,7,11,0,0,0,6,27,0,3,0), f"backend architecture manifest is stale in browser state: {system_overview['architectureSummary']}")
        require(system_overview["methodologyControls"] == 3 and "Exploration Frontier" in system_overview["text"] and "Search-Time Contamination" in system_overview["text"] and "Reproducibility Readiness" in system_overview["text"], f"cross-cutting methodology controls are missing: {system_overview['methodologyControls']}")
        require(system_overview["aiCheckpoints"] == 5, f"AI consultation checkpoint strip is incomplete: {system_overview['aiCheckpoints']}")
        require(system_overview["governanceStages"] == 7, f"P0-System v2 must expose seven scientific stages, got {system_overview['governanceStages']}")
        require(system_overview["outerGates"] == 8 and system_overview["preflightGates"] == 10 and system_overview["quantWorksheets"] == 2, f"Pre-Experiment/identifiability compiler is incomplete: {system_overview['outerGates']}/{system_overview['preflightGates']}/{system_overview['quantWorksheets']}")
        require(system_overview["lessons"] == 6 and system_overview["failureLayers"] == 6 and system_overview["repairLoops"] == 1, f"system learning/diagnosis visualization is incomplete: {system_overview['lessons']}/{system_overview['failureLayers']}/{system_overview['repairLoops']}")
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
        execute(session_id, "document.querySelector('.language-toggle')?.click();")
        time.sleep(1)
        zh_system = execute(session_id, """return {
          automationText: document.querySelector('.system-automation-panel')?.textContent || '',
          preflightText: [...document.querySelectorAll('.preflight-compiler')].find(x=>x.querySelector('.preflight-gate[data-preflight-key]'))?.textContent || '',
          semanticsText: document.querySelector('.system-semantics')?.textContent || '',
          componentText: document.querySelector('.system-components-panel')?.textContent || '',
          cards: [...document.querySelectorAll('.system-boundary-card,.preflight-gate,.system-failure-layer')].map(x=>({client:x.clientWidth,scroll:x.scrollWidth,text:x.textContent})),
          pageOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2
        };""")
        require("自动执行" in zh_system["automationText"] and "条件自动" in zh_system["automationText"] and "人工控制" in zh_system["automationText"], "Chinese automation boundary headings are incomplete")
        require("主张与训练目标对齐" in zh_system["preflightText"] and "方法与最强简化会做出不同决策" in zh_system["preflightText"] and "小样本可拟合性" in zh_system["preflightText"], "Chinese Pre-P0 hard gates are incomplete")
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
              roleGroups: document.querySelectorAll('.reference-role-group').length,
              roleBadges: document.querySelectorAll('.reference-card .reading-role').length,
              tierBadges: document.querySelectorAll('.reference-card .ranking-tier').length,
              citationBadges: document.querySelectorAll('.reference-card .citation-count').length,
              knownCitations: document.querySelectorAll('.reference-card .citation-count:not(.citation-pending)').length,
              openAnalyses: document.querySelectorAll('.paper-analysis[open]').length,
              analysisLabels: [...document.querySelectorAll('.paper-analysis-grid b')].slice(0,6).map(x=>x.textContent.trim()),
              orderedCards: [...document.querySelectorAll('.reference-card')].map(x=>({role:x.dataset.readingRole,roleRank:Number(x.dataset.roleRank),tier:Number(x.dataset.tier),citations:Number(x.dataset.citations),year:Number(x.dataset.year),title:x.querySelector('h3')?.textContent||''})),
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
        require(bibliography["priorityRanks"] == 80 and bibliography["roleBadges"] == 80 and bibliography["tierBadges"] == 80 and bibliography["citationBadges"] == 80, "ranking metadata is incomplete on bibliography cards")
        require(bibliography["roleGroups"] >= 2, "recommended reading groups are missing")
        require(bibliography["knownCitations"] >= 3, f"deployment citation snapshot is not visible: {bibliography['rankingStatus']}")
        ordered = bibliography["orderedCards"]
        require(all(a["roleRank"] <= b["roleRank"] for a, b in zip(ordered, ordered[1:])), "default bibliography order violates reading roles")
        require(not any(item["role"] in {"agent-foundation", "model-foundation"} for item in ordered[:20]), "old foundations still dominate the recommended top twenty")
        for a, b in zip(ordered, ordered[1:]):
            if a["role"] != b["role"]:
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
            "/selected-paper.html": {"groups": 4, "sections": 13},
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
                  missing: document.querySelectorAll('.citation-missing').length,
                  text: document.body.textContent || ''
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
            if page == "/selected-paper.html":
                require("CURRENT SELECTED PAPER" in result["text"] and "Former Regression-Gated Self-Evolution workspace" in result["text"] and "zero launchable directions" in result["text"], "current STRI workspace or historical STOP archive is missing")

        navigate("/research-directions.html", 7)
        direction_map = execute(
            session_id,
            """return {
              directions: document.querySelectorAll('.direction-card').length,
              chips: document.querySelectorAll('.idea-chip').length,
              chipLinks: document.querySelectorAll('a.idea-chip').length,
              macroCards: document.querySelectorAll('.direction-macro-card').length,
              explanationGrids: document.querySelectorAll('.direction-explanation-grid').length,
              exampleRows: document.querySelectorAll('.direction-running-example tbody tr').length,
              evidenceSections: document.querySelectorAll('.direction-literature').length,
              evidencePapers: document.querySelectorAll('.direction-paper-evidence').length,
              evidenceCitations: document.querySelectorAll('.direction-paper-evidence .inline-citations a').length,
              evidenceMethods: document.querySelectorAll('.direction-paper-evidence > p').length,
              evidenceFits: document.querySelectorAll('.direction-paper-evidence > div').length,
              missing: document.querySelectorAll('.citation-missing').length,
              src: document.querySelector('.overview-figure img')?.getAttribute('src') || '',
              text: document.body.textContent || ''
            };""",
        )
        require(direction_map["directions"] == 10, f"expected 10 directions, got {direction_map['directions']}")
        require(direction_map["chips"] == 34 and direction_map["chipLinks"] == 0, f"expected 34 read-only historical idea-lineage chips, got {direction_map['chips']} with {direction_map['chipLinks']} links")
        require(direction_map["macroCards"] == 4, "four-question direction primer is incomplete")
        require(direction_map["explanationGrids"] == 10, "plain-language direction explanations are incomplete")
        require(direction_map["exampleRows"] == 10, "running example does not cover all directions")
        require(direction_map["evidenceSections"] == 10 and direction_map["evidencePapers"] == 30, "representative literature does not cover all directions")
        require(direction_map["evidenceCitations"] == 30 and direction_map["evidenceMethods"] == 30 and direction_map["evidenceFits"] == 30, "direction literature cards are incomplete")
        require(direction_map["missing"] == 0, "direction literature contains unresolved citations")
        require(direction_map["src"].endswith("agent-self-evolution-directions-en.svg"), "English direction figure is not active")
        execute(session_id, "document.querySelector('.language-toggle')?.click();")
        time.sleep(1)
        zh_state = execute(session_id, "return {src:document.querySelector('.overview-figure img')?.getAttribute('src')||'', text:document.querySelector('.direction-literature')?.textContent||''};")
        require(zh_state["src"].endswith("agent-self-evolution-directions-zh.svg"), "Chinese direction figure did not switch")
        require("代表论文" in zh_state["text"] and "方向关联" in zh_state["text"], "Chinese direction literature did not switch")

        navigate("/paper-ideas.html", 7)
        idea_portfolio = execute(
            session_id,
            """return {
              chapters: document.querySelectorAll('.page-chapter').length,
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
              currentRows: document.querySelectorAll('#current-research-portfolio .current-research-table tbody tr').length,
              leadingPaperTracks: document.querySelectorAll('#current-research-portfolio .current-paper-track-card').length,
              currentStatus: window.CURRENT_RESEARCH_STATUS?.headline || {},
              legacyFinalPass: Number(window.RESEARCH_SYSTEM_STATE?.summary?.final_pass || 0),
              experimentStops: Number(window.RESEARCH_SYSTEM_STATE?.p0_decision_ledger?.summary?.experiment_stopped || 0),
              text: document.body.textContent || ''
            };""",
        )
        require(idea_portfolio["chapters"] == 2, f"Paper Ideas must merge standalone methods and paper-first new problems into Chapter II, got {idea_portfolio['chapters']}")
        require(idea_portfolio["parentCards"] == 26, f"expected all 26 human-parent histories, got {idea_portfolio['parentCards']}")
        require(idea_portfolio["standaloneCards"] == 7, f"expected only the seven validated standalone methods after paper-first authority quarantine, got {idea_portfolio['standaloneCards']}")
        require((idea_portfolio["incubationCards"],idea_portfolio["incubationP0"],idea_portfolio["incubationSummary"].get("p0_authorized"),idea_portfolio["incubationSummary"].get("gpu_authorized")) == (9,0,0,0), f"paper-first queue must remain nine design candidates with zero validated P0/GPU authority: {idea_portfolio}")
        require("STOP_MATCHED_POST_ONLY_EQUIVALENT" in idea_portfolio["text"] and "STOP_MATCHED_SOFT_SCALAR_EQUIVALENT" in idea_portfolio["text"] and "DIAGNOSTIC ONLY" in idea_portfolio["text"], "completed premature Method diagnostics are not visible on Paper Ideas")
        require(idea_portfolio["terminalGroups"] >= 3 and idea_portfolio["terminalStats"] == 4, f"terminal routing UI is incomplete: {idea_portfolio['terminalGroups']}/{idea_portfolio['terminalStats']}")
        require(idea_portfolio["legacyPreGpuBoards"] == 0 and idea_portfolio["legacyP0Entry"] == 0, "legacy Pre-GPU/P0-entry boards leaked back into canonical Paper Ideas")
        require(idea_portfolio["currentLedger"] == 1 and idea_portfolio["currentRows"] >= 7 and idea_portfolio["leadingPaperTracks"] == 1, f"unified current idea ledger is incomplete: {idea_portfolio}")
        require("STRI-P0E" in idea_portfolio["text"] and "STOP_FIXED_POLICY_DYNAMIC_BRIDGE" in idea_portfolio["text"] and "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED" in idea_portfolio["text"], "qualified STRI P0-E boundary is missing from the current ledger")
        cs=idea_portfolio["currentStatus"]
        require((cs.get("paper_ready"),cs.get("paper_quality_hold"),cs.get("paper_quality_evidence_debt"),cs.get("canonical_live_ideas"),cs.get("launchable_formal_experiments"),cs.get("shadow_qualification_ready"),cs.get("legacy_p0_lifecycle")) == (1,0,0,0,0,0,27) and int(cs.get("shadow_dead_ends") or 0) >= 0 and int(cs.get("shadow_holds") or 0) >= 0, f"current status invariants are wrong: {cs}")
        require(idea_portfolio["legacyFinalPass"] == 20 and idea_portfolio["experimentStops"] >= 16, f"historical lineage state is unexpectedly missing: {idea_portfolio}")
        require("Historical ICLR Paper Workspace" not in idea_portfolio["text"] and "Selected ICLR Paper Workspace" not in idea_portfolio["text"], "historical paper workspace content leaked into Paper Ideas")
        require((("当前科研状态" in idea_portfolio["text"] and "Positive residual 当前边界" in idea_portfolio["text"]) or ("Current research state" in idea_portfolio["text"] and "Positive-residual boundary" in idea_portfolio["text"])) and "20 个当前 FINAL-PASS" not in idea_portfolio["text"], "Paper Ideas current-state labels are incomplete or stale FINAL-PASS framing leaked into the current view")

        navigate("/selected-paper.html", 4)
        selected = execute(session_id, """return {
          chapters: document.querySelectorAll('.page-chapter').length,
          currentSTRI: document.querySelectorAll('#selected-stri-current').length,
          archive: document.querySelectorAll('#historical-paper-archive').length,
          currentStatus: window.CURRENT_RESEARCH_STATUS?.headline || {},
          currentPaper: window.CURRENT_RESEARCH_STATUS?.leading_paper_track || {},
          currentDynamic: window.CURRENT_RESEARCH_STATUS?.stri_dynamic_evidence || {},
          title: document.title,
          text: document.body.textContent || ''
        };""")
        require(selected["chapters"] == 5 and selected["currentSTRI"] == 1 and selected["archive"] == 1, f"selected-paper must render one current STRI chapter plus four historical archive chapters: {selected}")
        require(selected["currentPaper"].get("paper_id") == "STRI" and selected["currentPaper"].get("paper_quality_v2_passed") is True and selected["currentPaper"].get("paper_quality_content_addressed_completion") is True and selected["currentPaper"].get("paper_quality_content_addressed_files") == 14 and selected["currentPaper"].get("paper_quality_evidence_debt") == 0 and (selected["currentPaper"].get("qa_passed"),selected["currentPaper"].get("qa_total")) == (60,60) and (selected["currentPaper"].get("official_qa_passed"),selected["currentPaper"].get("official_qa_total")) == (52,52) and selected["currentPaper"].get("paper_quality_schema_version") == "2.1" and selected["currentPaper"].get("paper_quality_main_visualizations") == 4 and selected["currentPaper"].get("paper_visual_figure_qa") == "PASS" and selected["currentPaper"].get("supplement_unit_tests") == "13/13 PASS" and selected["currentPaper"].get("official_source_conflict") is True and selected["currentPaper"].get("deadline_status") == "HUMAN_VERIFICATION_REQUIRED" and selected["currentPaper"].get("operational_safe_abstract_deadline_aoe") == "2026-09-11" and selected["currentPaper"].get("operational_safe_full_paper_deadline_aoe") == "2026-09-16" and selected["currentPaper"].get("recorded_author_guide_abstract_deadline_aoe") == "2026-09-18" and selected["currentPaper"].get("recorded_author_guide_full_paper_deadline_aoe") == "2026-09-25" and selected["currentPaper"].get("author_membership_freezes_at_abstract_deadline") is True and selected["currentPaper"].get("title_freezes_at_full_paper_deadline") is True and selected["currentStatus"].get("paper_ready") == 1, f"selected-paper current STRI projection is stale: {selected}")
        p0e = selected["currentDynamic"].get("skillrl_p0e") or {}
        require(p0e.get("status") == "STOP_FIXED_POLICY_DYNAMIC_BRIDGE" and p0e.get("persistent_principle_dead_end_certified") is False and p0e.get("principle_disposition") == "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED" and p0e.get("stage2_locked") is True and p0e.get("new_gpu_authorized") is False and (p0e.get("calibration") or {}).get("calibration_pristine_success") == 18 and (p0e.get("calibration") or {}).get("paired_units") == 24, f"selected-paper P0-E boundary is stale: {selected}")
        require("Self-Evolution Should Not Depend on How Skills Are Split" in selected["title"] and "CURRENT SELECTED PAPER" in selected["text"] and "2026-09-11" in selected["text"] and "2026-09-16" in selected["text"] and "2026-09-18" in selected["text"] and "2026-09-25" in selected["text"] and ("Official ICLR pages currently conflict" in selected["text"] or "官方页面日期目前冲突" in selected["text"]) and ("Former Regression-Gated Self-Evolution workspace" in selected["text"] or "旧 Regression-Gated Self-Evolution 工作区" in selected["text"]), f"selected-paper current/historical hierarchy or deadline handoff is wrong: {selected}")
        require("only permits a new shadow qualification" not in selected["text"] and "Historical ICLR Paper Workspace" not in selected["title"] and "[object Object]" not in selected["text"], f"selected-paper leaked stale shadow, nested-boundary rendering, or historical-primary framing: {selected}")

        redirect_checks = {
            "/memory-evolution.html": "mechanisms.html#group-memory-evolution",
            "/direction-board.html": "paper-ideas.html#discussed-ideas",
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
