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
                review_status_visible = ("all 26 first-round passes" in result["text"] and "4 PASS" in result["text"] and "12 BLOCK" in result["text"]) or ("26 个首轮通过项均已" in result["text"] and "4 个 PASS" in result["text"] and "12 个 BLOCK" in result["text"])
                require(review_status_visible, "selected-paper external review status is stale or missing")

        navigate("/research-directions.html", 7)
        direction_map = execute(
            session_id,
            """return {
              directions: document.querySelectorAll('.direction-card').length,
              chips: document.querySelectorAll('.idea-chip').length,
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
        require(direction_map["chips"] == 34, f"expected 34 idea mappings, got {direction_map['chips']}")
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
              automationComponents: document.querySelectorAll('.automation-component').length,
              automationStats: document.querySelectorAll('.automation-stats .stat').length,
              automationCollisionRows: document.querySelectorAll('.automation-collision-table tbody tr').length,
              automationRepairRows: document.querySelectorAll('.automation-repair-list li').length,
              automationHealth: document.querySelector('.system-health')?.textContent || '',
              automationStatePapers: Number(window.RESEARCH_SYSTEM_STATE?.summary?.papers || 0),
              automationEvidenceNodes: Number(window.RESEARCH_SYSTEM_STATE?.summary?.evidence_nodes || 0),
              automationPilotPhases: Number(window.RESEARCH_SYSTEM_STATE?.pilot_registry?.summary?.phases || 0),
              iclrAuditRows: document.querySelectorAll('.iclr-audit-panel .published-audit-table tbody tr').length,
              visualAuditRows: document.querySelectorAll('.cvpr-followup-archive .published-audit-table tbody tr').length,
              iclrProtocols: document.querySelectorAll('.iclr-idea-card .cvpr-experiment-protocol').length,
              iclrProtocolPhases: document.querySelectorAll('.iclr-idea-card .protocol-phases article').length,
              iclrProtocolModels: document.querySelectorAll('.iclr-idea-card .protocol-model-grid section').length,
              iclrProjectWebReviews: document.querySelectorAll('.iclr-idea-card .project-web-gpt-review').length,
              iclrExternalProgress: document.querySelector('.external-review-progress')?.textContent || '',
              iclrExternalReviewed: Number(window.ICLR_LOW_RESOURCE_IDEAS?.summary?.project_web_gpt_reviewed || 0),
              iclrExternalPending: Number(window.ICLR_LOW_RESOURCE_IDEAS?.summary?.project_web_gpt_pending || 0),
              iclrExternalPass: Number(window.ICLR_LOW_RESOURCE_IDEAS?.summary?.external_pass || 0),
              iclrExternalRevise: Number(window.ICLR_LOW_RESOURCE_IDEAS?.summary?.external_revise || 0),
              iclrExternalBlock: Number(window.ICLR_LOW_RESOURCE_IDEAS?.summary?.external_block || 0),
              iclrVerdictPassCards: document.querySelectorAll('.iclr-idea-card[data-external-verdict="pass"]').length,
              iclrVerdictReviseCards: document.querySelectorAll('.iclr-idea-card[data-external-verdict="revise"]').length,
              iclrVerdictBlockCards: document.querySelectorAll('.iclr-idea-card[data-external-verdict="block"]').length,
              iclrFirstFourVerdicts: [...document.querySelectorAll('.iclr-idea-card')].slice(0,4).map(x=>x.dataset.externalVerdict),
              iclrStructuredBlocked: document.querySelectorAll('#iclr-low-resource-bank ~ * .structured-blocked, .iclr-bank-panel .structured-blocked').length,
              iclrCards: document.querySelectorAll('.iclr-idea-card').length,
              iclrReviews: document.querySelectorAll('.iclr-idea-card .cvpr-review-pass').length,
              iclrTrackFilters: document.querySelectorAll('.iclr-filter-btn[data-iclr-filter-type="track"]').length,
              iclrBudgetFilters: document.querySelectorAll('.iclr-filter-btn[data-iclr-filter-type="budget"]').length,
              iclrTopRows: document.querySelectorAll('.iclr-top-table tbody tr').length,
              iclrRejected: document.querySelectorAll('.iclr-bank-panel .cvpr-rejected li').length,
              iclrMaxGpus: Math.max(...(window.ICLR_LOW_RESOURCE_IDEAS?.passed_ideas||[]).map(x=>Number(x.budget?.max_gpus||0))),
              iclrMaxHours: Math.max(...(window.ICLR_LOW_RESOURCE_IDEAS?.passed_ideas||[]).map(x=>Number(x.budget?.gpu_hours||0))),
              inspiredPanel: document.querySelectorAll('.machine-school-panel').length,
              inspiredStats: document.querySelectorAll('.machine-school-stats .stat').length,
              inspiredInspirations: document.querySelectorAll('.machine-school-inspirations article').length,
              inspiredGroups: document.querySelectorAll('.machine-school-group').length,
              inspiredCards: document.querySelectorAll('.machine-school-idea').length,
              inspiredExternalReviews: document.querySelectorAll('.machine-school-group.tone-pass .project-web-gpt-review').length,
              inspiredExternalPass: document.querySelectorAll('.machine-school-group.tone-pass .machine-school-idea.verdict-pass').length,
              inspiredExternalRevise: document.querySelectorAll('.machine-school-group.tone-pass .machine-school-idea.verdict-revise').length,
              inspiredExternalBlock: document.querySelectorAll('.machine-school-group.tone-pass .machine-school-idea.verdict-block').length,
              inspiredShortlist: document.querySelectorAll('.machine-shortlist-item').length,
              inspiredSummary: window.MACHINE_SCHOOL_IDEAS?.summary || {},
              inspiredFirstTitle: window.MACHINE_SCHOOL_IDEAS?.passed_ideas?.[0]?.title?.en || '',
              experimentProtocols: document.querySelectorAll('.cvpr-followup-archive .cvpr-experiment-protocol').length,
              protocolPhases: document.querySelectorAll('.cvpr-followup-archive .protocol-phases article').length,
              protocolModels: document.querySelectorAll('.cvpr-followup-archive .protocol-model-grid section').length,
              projectWebReviews: document.querySelectorAll('.cvpr-followup-archive .project-web-gpt-review').length,
              structuredBlocked: document.querySelectorAll('.cvpr-followup-archive .structured-blocked').length,
              backendStages: document.querySelectorAll('.idea-backend-flow article').length,
              funnelStages: document.querySelectorAll('.idea-funnel-stage').length,
              operators: document.querySelectorAll('.idea-operator-grid article').length,
              reviewers: document.querySelectorAll('.reviewer-gate-grid article').length,
              cvprCards: document.querySelectorAll('.cvpr-followup-archive .cvpr-idea-card').length,
              cvprReviews: document.querySelectorAll('.cvpr-followup-archive .cvpr-review-pass').length,
              cvprTrackFilters: document.querySelectorAll('.cvpr-filter-btn[data-cvpr-filter-type="track"]').length,
              cvprBudgetFilters: document.querySelectorAll('.cvpr-filter-btn[data-cvpr-filter-type="budget"]').length,
              cvprTopRows: document.querySelectorAll('.cvpr-followup-archive .cvpr-top-table tbody tr').length,
              cvprRejected: document.querySelectorAll('.cvpr-followup-archive .cvpr-rejected li').length,
              cvprMaxGpus: Math.max(...(window.CVPR_LOW_RESOURCE_IDEAS?.passed_ideas||[]).map(x=>Number(x.budget?.max_gpus||0))),
              cvprMaxHours: Math.max(...(window.CVPR_LOW_RESOURCE_IDEAS?.passed_ideas||[]).map(x=>Number(x.budget?.gpu_hours||0))),
              filters: document.querySelectorAll('.idea-board-filter').length,
              dossiers: document.querySelectorAll('.idea-dossier').length,
              dossierFields: document.querySelectorAll('.idea-dossier-grid section').length,
              evidenceCards: document.querySelectorAll('.idea-evidence-list article').length,
              archiveDirections: document.querySelectorAll('.idea-archive-direction').length,
              archiveIdeas: document.querySelectorAll('.idea-plan-card').length,
              archiveShortlist: document.querySelectorAll('.archive-shortlist-link').length,
              rows: document.querySelectorAll('#idea-ranking tbody tr').length,
              directionCards: document.querySelectorAll('.direction-rank-card').length,
              trackCards: document.querySelectorAll('.track-rank-card').length,
              purpose: document.body.textContent.includes('Purpose / problem') || document.body.textContent.includes('目的／要解决的问题'),
              core: document.body.textContent.includes('Core idea') || document.body.textContent.includes('核心思想'),
              rationale: document.body.textContent.includes('Why it is reasonable') || document.body.textContent.includes('为什么合理'),
              logic: document.body.textContent.includes('Method logic') || document.body.textContent.includes('方法逻辑'),
              importance: document.body.textContent.includes('Research importance') || document.body.textContent.includes('研究重要性'),
              advantage: document.body.textContent.includes('Comparative advantage') || document.body.textContent.includes('相对优势'),
              pilot: document.body.textContent.includes('Decisive pilot') || document.body.textContent.includes('决定性 Pilot'),
              auditActor: document.querySelector('.iclr-audit-panel .published-audit-table tbody tr td:nth-child(2) p')?.textContent || '',
              auditApi: document.querySelector('.iclr-audit-panel .published-audit-table tbody tr td:nth-child(3) p')?.textContent || '',
              auditVerification: document.querySelector('.iclr-audit-panel .published-audit-table tbody tr .verification-badge')?.textContent || '',
              text: document.body.textContent || ''
            };""",
        )
        require(idea_portfolio["automationComponents"] == 6, f"expected six reference-architecture components, got {idea_portfolio['automationComponents']}")
        require(idea_portfolio["automationStats"] == 6, f"expected six automation statistics, got {idea_portfolio['automationStats']}")
        require(idea_portfolio["automationCollisionRows"] > 0 and idea_portfolio["automationRepairRows"] > 0, "automation collision or repair queue did not render")
        require("healthy" in idea_portfolio["automationHealth"].lower(), f"research system health is not visible: {idea_portfolio['automationHealth']}")
        require(idea_portfolio["automationStatePapers"] >= 200 and idea_portfolio["automationEvidenceNodes"] > idea_portfolio["automationStatePapers"], "automation evidence graph is incomplete")
        require(idea_portfolio["automationPilotPhases"] == 78, f"expected 78 registered pilot phases, got {idea_portfolio['automationPilotPhases']}")
        require(idea_portfolio["iclrAuditRows"] == 12, f"expected 12 ICLR experiment-substrate audits, got {idea_portfolio['iclrAuditRows']}")
        require(idea_portfolio["visualAuditRows"] == 12, f"expected 12 preserved visual-paper audits, got {idea_portfolio['visualAuditRows']}")
        require("语言 Agent 与一个可训练 retrospective model 配对" in idea_portfolio["auditActor"], f"ICLR audit actor did not switch to Chinese: {idea_portfolio['auditActor']}")
        require("API 不是" in idea_portfolio["auditApi"], f"ICLR audit API role did not switch to Chinese: {idea_portfolio['auditApi']}")
        require("ICLR 官方摘要" in idea_portfolio["auditVerification"], f"ICLR audit verification label did not switch to Chinese: {idea_portfolio['auditVerification']}")
        require(idea_portfolio["iclrCards"] == 26, f"expected 26 passed ICLR ideas, got {idea_portfolio['iclrCards']}")
        require(idea_portfolio["iclrReviews"] == 182, f"expected 182 seven-dimension ICLR reviews, got {idea_portfolio['iclrReviews']}")
        require(idea_portfolio["iclrProtocols"] == 26, f"expected 26 ICLR experiment protocols, got {idea_portfolio['iclrProtocols']}")
        require(idea_portfolio["iclrProtocolPhases"] == 78, f"expected 78 ICLR P0/P1/P2 phase cards, got {idea_portfolio['iclrProtocolPhases']}")
        require(idea_portfolio["iclrProtocolModels"] == 156, f"expected six model/API fields for each ICLR idea, got {idea_portfolio['iclrProtocolModels']}")
        require(idea_portfolio["iclrProjectWebReviews"] == 26, f"expected 26 rendered ICLR project-web-GPT reviews, got {idea_portfolio['iclrProjectWebReviews']}")
        require(idea_portfolio["iclrExternalReviewed"] == 26 and idea_portfolio["iclrExternalPending"] == 0, f"external ICLR review counts are wrong: {idea_portfolio['iclrExternalReviewed']}/{idea_portfolio['iclrExternalPending']}")
        require((idea_portfolio["iclrExternalPass"], idea_portfolio["iclrExternalRevise"], idea_portfolio["iclrExternalBlock"]) == (4,10,12), f"external verdict distribution is wrong: {idea_portfolio['iclrExternalPass']}/{idea_portfolio['iclrExternalRevise']}/{idea_portfolio['iclrExternalBlock']}")
        require((idea_portfolio["iclrVerdictPassCards"], idea_portfolio["iclrVerdictReviseCards"], idea_portfolio["iclrVerdictBlockCards"]) == (4,10,12), "rendered R2 verdict-card counts are wrong")
        require(idea_portfolio["iclrFirstFourVerdicts"] == ["pass","pass","pass","pass"], f"R2 ranking does not place the four PASS ideas first: {idea_portfolio['iclrFirstFourVerdicts']}")
        require("4 PASS" in idea_portfolio["iclrExternalProgress"] and "12 BLOCK" in idea_portfolio["iclrExternalProgress"], f"external review progress is not rendered: {idea_portfolio['iclrExternalProgress']}")
        require(idea_portfolio["iclrStructuredBlocked"] == 3, f"expected three structured ICLR blocks, got {idea_portfolio['iclrStructuredBlocked']}")
        require(idea_portfolio["iclrTrackFilters"] == 9 and idea_portfolio["iclrBudgetFilters"] == 3, "ICLR track or budget filters are incomplete")
        require(idea_portfolio["iclrTopRows"] == 15 and idea_portfolio["iclrRejected"] == 15, "ICLR comparison table or rejection archive is incomplete")
        require(idea_portfolio["iclrMaxGpus"] <= 2 and idea_portfolio["iclrMaxHours"] <= 48, "ICLR idea bank violates the low-resource policy")
        require(idea_portfolio["inspiredPanel"] == 1 and idea_portfolio["inspiredStats"] == 5, "internet-inspired decision panel or stats did not render")
        require(idea_portfolio["inspiredInspirations"] == 6 and idea_portfolio["inspiredGroups"] == 3, "six inspirations or three screening groups are missing")
        require(idea_portfolio["inspiredCards"] == 24 and idea_portfolio["inspiredExternalReviews"] == 11, f"inspired idea or external-review counts are wrong: {idea_portfolio['inspiredCards']}/{idea_portfolio['inspiredExternalReviews']}")
        require((idea_portfolio["inspiredExternalPass"], idea_portfolio["inspiredExternalRevise"], idea_portfolio["inspiredExternalBlock"]) == (1,7,3), "inspired external verdict-card counts are wrong")
        require(idea_portfolio["inspiredShortlist"] == 8, f"expected eight teacher-discussion candidates, got {idea_portfolio['inspiredShortlist']}")
        require(idea_portfolio["inspiredSummary"].get("raw") == 24 and idea_portfolio["inspiredSummary"].get("external_reviewed") == 11, f"inspired data summary is wrong: {idea_portfolio['inspiredSummary']}")
        require(idea_portfolio["inspiredFirstTitle"] == "Regression-Probe Half-Life", f"wrong top inspired idea: {idea_portfolio['inspiredFirstTitle']}")
        require(idea_portfolio["experimentProtocols"] == 42, f"expected 42 preserved CVPR protocols, got {idea_portfolio['experimentProtocols']}")
        require(idea_portfolio["protocolPhases"] == 126, f"expected 126 preserved CVPR phase cards, got {idea_portfolio['protocolPhases']}")
        require(idea_portfolio["protocolModels"] == 252, f"expected six model/API fields per CVPR idea, got {idea_portfolio['protocolModels']}")
        require(idea_portfolio["projectWebReviews"] == 2, f"expected two preserved CVPR project-web-GPT reviews, got {idea_portfolio['projectWebReviews']}")
        require(idea_portfolio["structuredBlocked"] == 1, f"expected one preserved CVPR structured block, got {idea_portfolio['structuredBlocked']}")
        require(idea_portfolio["backendStages"] == 8, f"expected 8 backend stages, got {idea_portfolio['backendStages']}")
        require(idea_portfolio["funnelStages"] == 0, f"legacy funnel should not lead the ICLR-first page, got {idea_portfolio['funnelStages']}")
        require(idea_portfolio["operators"] == 8 and idea_portfolio["reviewers"] == 7, "ICLR idea generation or reviewer architecture is incomplete")
        require(idea_portfolio["cvprCards"] == 42, f"expected 42 self-reviewed CVPR ideas, got {idea_portfolio['cvprCards']}")
        require(idea_portfolio["cvprReviews"] == 210, "every passed CVPR idea must expose five programmatic review records")
        require(idea_portfolio["cvprTrackFilters"] == 9 and idea_portfolio["cvprBudgetFilters"] == 3, "CVPR track or budget filters are incomplete")
        require(idea_portfolio["cvprTopRows"] == 15 and idea_portfolio["cvprRejected"] == 19, "CVPR comparison table or rejection archive is incomplete")
        require(idea_portfolio["cvprMaxGpus"] <= 2 and idea_portfolio["cvprMaxHours"] <= 48, "CVPR idea bank violates the low-resource policy")
        require(idea_portfolio["filters"] == 5, "advisor filters are incomplete")
        require(idea_portfolio["dossiers"] == 12 and idea_portfolio["dossierFields"] == 72, "advisor shortlist dossiers are incomplete")
        require(idea_portfolio["evidenceCards"] == 36, "shortlist literature neighborhoods are incomplete")
        require(idea_portfolio["archiveDirections"] == 10, "candidate archive does not cover all directions")
        require(idea_portfolio["archiveIdeas"] + idea_portfolio["archiveShortlist"] == 34, "candidate archive does not preserve all 34 ideas")
        require(idea_portfolio["rows"] == 34, f"expected 34 traceable ranked ideas, got {idea_portfolio['rows']}")
        require(idea_portfolio["directionCards"] == 10 and idea_portfolio["trackCards"] == 4, "legacy traceability rankings are incomplete")
        require(idea_portfolio["purpose"] and idea_portfolio["core"] and idea_portfolio["rationale"] and idea_portfolio["logic"], "idea dossiers are missing required reasoning fields")
        require(idea_portfolio["importance"] and idea_portfolio["advantage"] and idea_portfolio["pilot"], "idea dossiers are missing importance, advantage, or pilot evidence")
        require("GroundEvo-Admission" in idea_portfolio["text"] and "PluralLineage-Evo" in idea_portfolio["text"], "idea portfolio is incomplete")
        execute(session_id, "document.querySelector('.language-toggle')?.click();")
        time.sleep(1)
        audit_english = execute(session_id, "return {actor:document.querySelector('.iclr-audit-panel .published-audit-table tbody tr td:nth-child(2) p')?.textContent||'', api:document.querySelector('.iclr-audit-panel .published-audit-table tbody tr td:nth-child(3) p')?.textContent||'', verification:document.querySelector('.iclr-audit-panel .published-audit-table tbody tr .verification-badge')?.textContent||''};")
        require("language agent is paired with a trainable retrospective model" in audit_english["actor"].lower(), f"ICLR audit actor did not switch back to English: {audit_english['actor']}")
        require("api access is not structurally required" in audit_english["api"].lower(), f"ICLR audit API role did not switch back to English: {audit_english['api']}")
        require("official ICLR abstract" in audit_english["verification"], f"ICLR audit verification label did not switch back to English: {audit_english['verification']}")
        iclr_filter = execute(session_id, """const b=[...document.querySelectorAll('.iclr-filter-btn')].find(x=>x.dataset.iclrFilterType==='budget'&&x.dataset.iclrFilterValue==='24'); b?.click(); const expected=(window.ICLR_LOW_RESOURCE_IDEAS?.passed_ideas||[]).filter(x=>Number(x.budget?.gpu_hours||0)<=24).length; const visible=[...document.querySelectorAll('.iclr-filter-target')].filter(x=>!x.closest('[id^=\"iclr-\"]')?.classList.contains('cvpr-filter-hidden')).length; return {expected,visible};""")
        require(iclr_filter["visible"] == iclr_filter["expected"] and iclr_filter["visible"] > 0, f"ICLR budget filter failed: {iclr_filter}")
        iclr_track = execute(session_id, """const b=[...document.querySelectorAll('.iclr-filter-btn')].find(x=>x.dataset.iclrFilterType==='track'&&x.dataset.iclrFilterValue==='memory'); b?.click(); const expected=(window.ICLR_LOW_RESOURCE_IDEAS?.passed_ideas||[]).filter(x=>x.track_id==='memory'&&Number(x.budget?.gpu_hours||0)<=24).length; const visible=[...document.querySelectorAll('.iclr-filter-target')].filter(x=>!x.closest('[id^=\"iclr-\"]')?.classList.contains('cvpr-filter-hidden')).length; return {expected,visible};""")
        require(iclr_track["visible"] == iclr_track["expected"], f"ICLR track filter failed: {iclr_track}")
        cvpr_filter = execute(session_id, """const b=[...document.querySelectorAll('.cvpr-filter-btn')].find(x=>x.dataset.cvprFilterType==='budget'&&x.dataset.cvprFilterValue==='16'); b?.click(); const expected=(window.CVPR_LOW_RESOURCE_IDEAS?.passed_ideas||[]).filter(x=>Number(x.budget?.gpu_hours||0)<=16).length; const visible=[...document.querySelectorAll('.cvpr-filter-target')].filter(x=>!x.closest('[id^=\"cvpr-\"]')?.classList.contains('cvpr-filter-hidden')).length; return {expected,visible};""")
        require(cvpr_filter["visible"] == cvpr_filter["expected"] and cvpr_filter["visible"] > 0, f"CVPR budget filter failed: {cvpr_filter}")
        cvpr_track = execute(session_id, """const b=[...document.querySelectorAll('.cvpr-filter-btn')].find(x=>x.dataset.cvprFilterType==='track'&&x.dataset.cvprFilterValue==='video'); b?.click(); const expected=(window.CVPR_LOW_RESOURCE_IDEAS?.passed_ideas||[]).filter(x=>x.track_id==='video'&&Number(x.budget?.gpu_hours||0)<=16).length; const visible=[...document.querySelectorAll('.cvpr-filter-target')].filter(x=>!x.closest('[id^=\"cvpr-\"]')?.classList.contains('cvpr-filter-hidden')).length; return {expected,visible};""")
        require(cvpr_track["visible"] == cvpr_track["expected"], f"CVPR track filter failed: {cvpr_track}")
        filter_result = execute(session_id, """const b=[...document.querySelectorAll('.idea-board-filter')].find(x=>x.dataset.ideaFilter==='selected'); b?.click(); return {hidden:document.querySelectorAll('.idea-filter-hidden').length, visible:[...document.querySelectorAll('.idea-filter-target')].filter(x=>!x.classList.contains('idea-filter-hidden')).length};""")
        require(filter_result["hidden"] > 0 and filter_result["visible"] == 2, f"advisor filter failed: {filter_result}")

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
