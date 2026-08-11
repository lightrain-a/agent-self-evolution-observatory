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
          chapters: document.querySelectorAll('.page-chapter').length,
          lifecycleSteps: document.querySelectorAll('.system-lifecycle-step').length,
          outerGates: document.querySelectorAll('.preflight-outer-gate').length,
          preflightGates: document.querySelectorAll('.preflight-gate').length,
          quantWorksheets: document.querySelectorAll('.preflight-quant-grid article').length,
          lessons: document.querySelectorAll('.system-lesson').length,
          failureLayers: document.querySelectorAll('.system-failure-layer').length,
          repairLoops: document.querySelectorAll('.system-repair-loop').length,
          components: document.querySelectorAll('.system-components-panel tbody tr').length,
          ideaCards: document.querySelectorAll('.system-idea-card,.system-decision-summary,.system-v5-summary,.system-v4-summary,.system-inspired-summary').length,
          preSummary: window.RESEARCH_SYSTEM_STATE?.pre_p0_identifiability?.summary || {},
          iterationSummary: window.RESEARCH_SYSTEM_STATE?.experiment_iteration?.summary || {},
          text: document.body.textContent || ''
        };""")
        require(system["chapters"] == 4, f"research-system overview must have four chapters, got {system['chapters']}")
        require(system["lifecycleSteps"] == 8, f"research lifecycle must expose eight decision stages, got {system['lifecycleSteps']}")
        require(system["outerGates"] == 8 and system["preflightGates"] == 10 and system["quantWorksheets"] == 2, f"Pre-Experiment/identifiability compiler is incomplete: {system['outerGates']}/{system['preflightGates']}/{system['quantWorksheets']}")
        require(system["lessons"] == 6 and system["failureLayers"] == 5 and system["repairLoops"] == 1, f"learning/diagnosis visualization is incomplete: {system['lessons']}/{system['failureLayers']}/{system['repairLoops']}")
        require(system["components"] == 13, f"expected thirteen backend components including the human terminal controller, got {system['components']}")
        require(system["ideaCards"] == 0, f"system-overview must not render current idea/status panels, got {system['ideaCards']}")
        require((system["preSummary"].get("audited"), system["preSummary"].get("execution_ready"), system["preSummary"].get("blocked")) == (4,0,4), f"Pre-P0 retrospective state is wrong: {system['preSummary']}")
        require(system["iterationSummary"].get("belief_updates_allowed") == 1 and system["iterationSummary"].get("scale_up_allowed") == 0, f"experiment-diagnosis state is wrong: {system['iterationSummary']}")
        require("Main ICLR idea bank" not in system["text"] and "Final advisor gate" not in system["text"] and "主 ICLR Idea Bank" not in system["text"] and "最终师兄讨论门槛" not in system["text"], "current idea portfolio leaked back into the research-system page")
        execute(session_id, "document.querySelector('.language-toggle')?.click();")
        time.sleep(1)
        zh = execute(session_id, "return {text:document.body.textContent||'', outer:document.querySelectorAll('.preflight-outer-gate').length, gates:document.querySelectorAll('.preflight-gate').length, failures:document.querySelectorAll('.system-failure-layer').length};")
        require(zh["outer"] == 8 and zh["gates"] == 10 and zh["failures"] == 5 and "科研系统到底要保证什么" in zh["text"] and "实验启动前编译器与经验沉淀" in zh["text"], "Chinese research-system hierarchy or Pre-Experiment visualization is incomplete")
        request("POST", f"/session/{session_id}/window/rect", {"width": 390, "height": 844})
        time.sleep(1)
        system_mobile = execute(session_id, """const gate=document.querySelector('.preflight-gate-grid'); const failure=document.querySelector('.system-failure-layers'); return {inner:window.innerWidth,scroll:document.documentElement.scrollWidth,gateCols:gate?getComputedStyle(gate).gridTemplateColumns:'',failureCols:failure?getComputedStyle(failure).gridTemplateColumns:'',maxCard:Math.max(0,...[...document.querySelectorAll('.preflight-gate,.system-failure-layer')].map(x=>x.getBoundingClientRect().width))};""")
        require(system_mobile["scroll"] <= system_mobile["inner"] + 2, f"research-system mobile layout has page-level horizontal overflow: {system_mobile}")
        require(" " not in system_mobile["gateCols"].strip() and " " not in system_mobile["failureCols"].strip(), f"Pre-P0/failure grids must collapse to one column on mobile: {system_mobile}")
        require(system_mobile["maxCard"] <= system_mobile["inner"], f"research-system cards exceed mobile viewport: {system_mobile}")
        request("POST", f"/session/{session_id}/window/rect", {"width": 1440, "height": 1000})
        time.sleep(1)

        navigate("/paper-ideas.html", 6)
        ideas = execute(session_id, """return {
          chapters: document.querySelectorAll('.page-chapter').length,
          toc2: document.querySelectorAll('.toc-level-2').length,
          toc3: document.querySelectorAll('.toc-level-3').length,
          toc4: document.querySelectorAll('.toc-level-4').length,
          p0Entry: document.querySelectorAll('.p0-entry-panel').length,
          p0Boards: document.querySelectorAll('.p0-control-board').length,
          experimentLinks: [...document.querySelectorAll('a')].filter(x=>x.getAttribute('href')==='experiments.html').length,
          p0Summary: window.P0_EXPERIMENT_PLAN?.summary || {},
          p0Policy: window.P0_EXPERIMENT_PLAN?.policy || {},
          p0AdmissionSummary: window.RESEARCH_SYSTEM_STATE?.p0_admission?.summary || {},
          p0EntryStats: [...document.querySelectorAll('.p0-entry-stats b')].map(x=>Number((x.textContent||'0').trim())),
          discussedGroups: document.querySelectorAll('.human-science-group').length,
          discussedCards: document.querySelectorAll('.human-review-idea-card').length,
          readyCards: document.querySelectorAll('.human-review-idea-card.human-tone-ready').length,
          mergedCards: document.querySelectorAll('.human-review-idea-card.human-tone-merged').length,
          droppedCards: document.querySelectorAll('.human-review-idea-card.human-tone-dropped').length,
          terminalCounts: [...document.querySelectorAll('.human-review-idea-card')].reduce((a,x)=>{const k=x.dataset.terminalStatus||'';a[k]=(a[k]||0)+1;return a;},{}),
          terminalSummary: window.HUMAN_TERMINAL_IDEA_STATE?.summary || {},
          absorbedChildCount: Object.keys(window.HUMAN_TERMINAL_IDEA_STATE?.absorbed_children || {}).length,
          feedbackSummaries: document.querySelectorAll('.human-review-idea-card .human-idea-summary p').length,
          humanOpinionBoxes: document.querySelectorAll('.human-opinion-box').length,
          iterationBoxes: document.querySelectorAll('.human-iteration-box').length,
          finalRefinementBoxes: document.querySelectorAll('.human-final-refinement').length,
          finalRefinementCounts: [...document.querySelectorAll('.human-final-summary>div>b')].map(x=>Number((x.textContent||'0').trim())),
          methodologyPanels: document.querySelectorAll('.human-review-methodology').length,
          originalEvalGuides: document.querySelectorAll('.human-original-eval-guide').length,
          humanRecommendationStats: [...document.querySelectorAll('.human-recommendation-stat b')].map(x=>Number((x.textContent||'0').trim())),
          canonicalReviewCount: Object.keys(window.HUMAN_REVIEW_CANONICAL_20260810?.ideas || {}).length,
          originalIdeaLabels: [...document.querySelectorAll('.human-idea-title small')].map(x=>(x.textContent||'').trim()),
          concreteExamples: [...document.querySelectorAll('.human-review-idea-card h4')].filter(x=>/举个具体例子|Concrete example/.test(x.textContent||'')).length,
          parentMergeRules: [...document.querySelectorAll('.human-review-idea-card h4')].filter(x=>/必须并回父 Idea|must merge into its parent/.test(x.textContent||'')).length,
          openDiscussedCards: document.querySelectorAll('.human-review-idea-card[open]').length,
          codes: [...document.querySelectorAll('.human-idea-code')].map(x=>(x.textContent||'').trim()),
          newGroups: document.querySelectorAll('.supplemental-group').length,
          newCards: document.querySelectorAll('.supplemental-idea-card').length,
          standaloneCodes: [...document.querySelectorAll('.supplemental-idea-card summary>div>span')].map(x=>(x.textContent||'').trim()),
          openNewCards: document.querySelectorAll('.supplemental-idea-card[open]').length,
          newFinal: [...document.querySelectorAll('.supplemental-idea-card summary small')].filter(x=>/FINAL20|merge audit/.test(x.textContent||'')).length,
          newInspired: [...document.querySelectorAll('.supplemental-idea-card summary small')].filter(x=>/网络灵感|internet-inspired/.test(x.textContent||'')).length,
          mergedMethods: document.querySelectorAll('.human-absorbed-methods').length,
          freshCollisionBlocks: document.querySelectorAll('.human-fresh-collision').length,
          freshCollisionLinks: document.querySelectorAll('.human-fresh-collision nav a').length,
          text: document.body.textContent || ''
        };""")
        require(ideas["chapters"] == 2, f"paper-ideas should have exactly two frontend chapters, got {ideas['chapters']}")
        require(ideas["p0Entry"] == 1 and ideas["p0Boards"] == 0 and ideas["experimentLinks"] >= 1, f"paper-ideas must expose only the compact experiment entry: {ideas['p0Entry']}/{ideas['p0Boards']}/{ideas['experimentLinks']}")
        require(ideas["p0AdmissionSummary"].get("active_p0") == 20 and ideas["p0AdmissionSummary"].get("transitioned_from_p0_ready") == 16 and ideas["p0AdmissionSummary"].get("settings_complete") == 20 and ideas["p0EntryStats"][:4] == [20,16,20,0], f"paper-ideas P0 admission entry is stale: {ideas['p0AdmissionSummary']} / {ideas['p0EntryStats']}")
        require(ideas["p0Summary"].get("ready_now") == 0 and ideas["p0Summary"].get("pre_p0_blocked") == 4 and ideas["p0Summary"].get("gpu_hours_cap_ready_now") == 0 and ideas["p0Summary"].get("p1_authorized") == 0, f"P0 Pre-P0/resource summary is wrong: {ideas['p0Summary']}")
        require(ideas["p0Policy"].get("pre_p0_identifiability_required") is True and ideas["p0Policy"].get("automatic_p0_to_p1_forbidden") is True and ideas["p0Policy"].get("p0_pass_requires_human_approval") is True, f"P0 human/Pre-P0 approval policy is missing: {ideas['p0Policy']}")
        require((ideas["toc2"], ideas["toc3"], ideas["toc4"]) == (3, 9, 0), f"paper-ideas TOC hierarchy is wrong: {ideas['toc2']}/{ideas['toc3']}/{ideas['toc4']}")
        require(ideas["discussedGroups"] == 6 and ideas["discussedCards"] == 26, f"expected six scientific groups and 26 discussed ideas, got {ideas['discussedGroups']}/{ideas['discussedCards']}")
        require((ideas["readyCards"], ideas["mergedCards"], ideas["droppedCards"]) == (13, 6, 7), f"terminal tone counts are wrong: {ideas['readyCards']}/{ideas['mergedCards']}/{ideas['droppedCards']}")
        require(ideas["terminalCounts"].get("p0") == 13 and ideas["terminalCounts"].get("p0-ready",0) == 0 and ideas["terminalCounts"].get("merge") == 6 and ideas["terminalCounts"].get("drop") == 7, f"terminal parent counts are wrong: {ideas['terminalCounts']}")
        require((ideas["terminalSummary"].get("human_parents"), ideas["absorbedChildCount"]) == (26,17), f"terminal ledger or absorbed-child count is wrong: {ideas['terminalSummary']}/{ideas['absorbedChildCount']}")
        require(ideas["feedbackSummaries"] == 26, f"every discussed idea must expose one current summary, got {ideas['feedbackSummaries']}")
        require(ideas["humanOpinionBoxes"] == 26, f"all 26 discussed ideas must preserve the human opinion, got {ideas['humanOpinionBoxes']}")
        require(ideas["iterationBoxes"] == 17 and ideas["finalRefinementBoxes"] == 17, f"all 17 refined methods must show the final iteration and routing: {ideas['iterationBoxes']}/{ideas['finalRefinementBoxes']}")
        require(ideas["finalRefinementCounts"] == [13,0,6,7], f"terminal routing must be 13 P0 / 0 P0-ready / 6 merge / 7 drop, got {ideas['finalRefinementCounts']}")
        require(ideas["methodologyPanels"] == 1 and ideas["originalEvalGuides"] == 1, f"human-opinion audit/original-eval methodology panels are missing: {ideas['methodologyPanels']}/{ideas['originalEvalGuides']}")
        require(ideas["canonicalReviewCount"] == 26, f"canonical human-review map must cover all 26 ideas, got {ideas['canonicalReviewCount']}")
        require(ideas["humanRecommendationStats"] == [4,14,7,1], f"canonical human recommendation counts are wrong: {ideas['humanRecommendationStats']}")
        require(any('Original Idea 4' in label or '原讨论 Idea 4' in label for label in ideas["originalIdeaLabels"]), f"original discussion numbering is not visible: {ideas['originalIdeaLabels'][:5]}")
        require(ideas["concreteExamples"] == 26 and ideas["parentMergeRules"] >= 1, f"intuition/example or parent-merge UI gate is missing: {ideas['concreteExamples']}/{ideas['parentMergeRules']}")
        require(ideas["openDiscussedCards"] == 0 and ideas["openNewCards"] == 0, f"all idea cards must be collapsed by default, got {ideas['openDiscussedCards']}/{ideas['openNewCards']}")
        require(len(ideas["codes"]) == 26 and len(set(ideas["codes"])) == 26, f"group codes are missing or duplicated: {ideas['codes']}")
        require(all(code in ideas["codes"] for code in ("A-1","A-5","B-1","B-7","C-1","D-1","E-1","F-1","F-3")), f"expected stable group codes are missing: {ideas['codes']}")
        require(ideas["newGroups"] == 3 and ideas["newCards"] == 7, f"terminal standalone-method area is incomplete: {ideas['newGroups']}/{ideas['newCards']}")
        require(set(ideas["standaloneCodes"]) == {"A-6","A-7","B-8","B-9","B-10","E-3","E-4"}, f"standalone methods must have stable scientific-group codes: {ideas['standaloneCodes']}")
        require((ideas["newFinal"], ideas["newInspired"]) == (0, 0), f"legacy supplemental candidates must not remain active: {ideas['newFinal']}/{ideas['newInspired']}")
        require(ideas["mergedMethods"] >= 8, f"merged FINAL method provenance is not visible on discussed ideas: {ideas['mergedMethods']}")
        require(ideas["freshCollisionBlocks"] == 17 and ideas["freshCollisionLinks"] >= 40, f"fresh reducibility sources are missing from refined ideas: {ideas['freshCollisionBlocks']}/{ideas['freshCollisionLinks']}")
        require(all(marker in ideas["text"] for marker in ("ChronoMem","DeltaBox","CausalFlow")), "latest load-bearing collision sources are not visible in refined idea cards")
        require("Human terminal ledger" in ideas["text"] and ideas["newCards"] == 7 and ideas["absorbedChildCount"] == 17, "terminal/current idea summary or standalone-method rendering is missing")

        expanded_before_refresh = execute(session_id, """document.documentElement.style.scrollBehavior='auto'; const card=document.getElementById('idea-a-1'); if(!card) return null; card.open=true; card.querySelectorAll('details').forEach(x=>x.open=true); const top=card.getBoundingClientRect().top+window.scrollY; window.scrollTo(0, top+Math.min(900,Math.max(500,card.scrollHeight*.55))); return {y:window.scrollY,open:document.querySelectorAll('#dynamic-page details[open]').length};""")
        time.sleep(1)
        require(expanded_before_refresh and expanded_before_refresh["y"] > 400 and expanded_before_refresh["open"] > 0, f"failed to reproduce an expanded mid-page reading state before refresh: {expanded_before_refresh}")
        request("POST", f"/session/{session_id}/refresh", {})
        time.sleep(6)
        after_refresh = execute(session_id, "return {y:window.scrollY,open:document.querySelectorAll('#dynamic-page details[open]').length,max:document.documentElement.scrollHeight-window.innerHeight};")
        require(after_refresh["y"] <= 4, f"paper-ideas reload must return to the top, got {after_refresh}")
        require(after_refresh["open"] == 0, f"paper-ideas reload must collapse every dynamic details block, got {after_refresh['open']} open blocks")

        request("POST", f"/session/{session_id}/window/rect", {"width": 390, "height": 844})
        time.sleep(1)
        mobile = execute(session_id, """const card=document.querySelector('.human-review-idea-card'); if(card) card.open=true; const history=document.querySelector('.human-review-history'); return {
          innerWidth: window.innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          historyColumns: history ? getComputedStyle(history).gridTemplateColumns : '',
          cardWidth: card ? card.getBoundingClientRect().width : 0,
          bodyWidth: document.body.getBoundingClientRect().width
        };""")
        require(mobile["scrollWidth"] <= mobile["innerWidth"] + 2, f"paper-ideas mobile layout has page-level horizontal overflow: {mobile}")
        require(" " not in mobile["historyColumns"].strip(), f"human review history must collapse to one column on mobile: {mobile['historyColumns']}")
        require(mobile["cardWidth"] <= mobile["innerWidth"], f"idea card exceeds the mobile viewport: {mobile}")
        request("POST", f"/session/{session_id}/window/rect", {"width": 1440, "height": 1000})
        time.sleep(1)

        navigate("/experiments.html", 6)
        experiments = execute(session_id, """return {
          chapters: document.querySelectorAll('.page-chapter').length,
          terminalPortfolio: document.querySelectorAll('#terminal-experiment-portfolio').length,
          terminalRows: document.querySelectorAll('.terminal-experiment-row').length,
          terminalStarted: document.querySelectorAll('.terminal-experiment-row[data-current-p0-started="1"]').length,
          terminalPending: document.querySelectorAll('.terminal-experiment-row[data-current-p0-started="0"]').length,
          terminalP0: document.querySelectorAll('.terminal-experiment-row[data-terminal-lifecycle="p0"]').length,
          terminalP0Ready: document.querySelectorAll('.terminal-experiment-row[data-terminal-lifecycle="p0-ready"]').length,
          auditQueue: document.querySelectorAll('#terminal-unstarted-audit').length,
          auditItems: document.querySelectorAll('.terminal-audit-item').length,
          admissionPanel: document.querySelectorAll('#p0-admission-settings').length,
          admissionRows: document.querySelectorAll('.p0-admission-table tbody tr').length,
          offlinePanel: document.querySelectorAll('#p0-offline-qualification').length,
          offlineSummary: window.P0_OFFLINE_QUALIFICATION?.summary || {},
          realizabilitySummary: window.P0_REALIZABILITY_SUITE?.summary || {},
          b10Decision: window.P0_B10_CPU?.decision || '',
          a6Decision: window.P0_A6_CPU?.decision || '',
          a7Decision: window.P0_A7_COUNTERFACTUAL_CPU?.decision || '',
          b3Decision: window.P0_B3_INTERFERENCE_CPU?.decision || '',
          b3RuntimeDecision: window.P0_B3_INTERFERENCE_CPU?.runtime_preflight_snapshot?.decision || '',
          e2Decision: window.P0_E2_WORKFLOW_CPU?.decision || '',
          e3Decision: window.P0_E3_STATEFUL?.decision || window.P0_E3_REAL_API?.decision || '',
          e4Decision: window.P0_E4_PERMISSION_CPU?.decision || '',
          p0StopRows: document.querySelectorAll('.terminal-exp-p0-stop').length,
          admissionSummary: window.P0_ADMISSION_STATE?.summary || {},
          legacyArchives: document.querySelectorAll('.experiment-legacy-archive').length,
          toc2: document.querySelectorAll('.toc-level-2').length,
          toc3: document.querySelectorAll('.toc-level-3').length,
          toc4: document.querySelectorAll('.toc-level-4').length,
          board: document.querySelectorAll('.p0-control-board').length,
          cards: document.querySelectorAll('.p0-plan-card').length,
          authorized: document.querySelectorAll('.p0-plan-card[data-p0-authorized="1"]').length,
          collision: document.querySelectorAll('.p0-plan-card[data-p0-status="collision-recheck"]').length,
          redesign: document.querySelectorAll('.p0-plan-card[data-p0-status="method-redesign"]').length,
          scenario: document.querySelectorAll('.p0-plan-card[data-p0-status="scenario-check"]').length,
          openCards: document.querySelectorAll('.p0-plan-card[open]').length,
          phaseTracks: document.querySelectorAll('.experiment-phase-track').length,
          phaseCells: document.querySelectorAll('.experiment-phase-cell').length,
          liveResults: document.querySelectorAll('.experiment-live-result').length,
          executedResults: document.querySelectorAll('.experiment-live-result:not(.result-pending)').length,
          ledger: document.querySelectorAll('.experiment-ledger').length,
          ledgerCells: document.querySelectorAll('.experiment-ledger-grid>div').length,
          resultRows: document.querySelectorAll('.experiment-results-table tbody tr').length,
          approvalRows: document.querySelectorAll('.experiment-approval-table tbody tr').length,
          gateCells: document.querySelectorAll('.experiment-gate-summary>span').length,
          preP0Panels: document.querySelectorAll('.pre-p0-panel').length,
          preP0Cards: document.querySelectorAll('.pre-p0-card').length,
          preP0ReadyCards: document.querySelectorAll('.pre-p0-card.ready').length,
          preP0BlockedCards: document.querySelectorAll('.pre-p0-card.blocked').length,
          preP0ReadyState: Number(window.RESEARCH_SYSTEM_STATE?.pre_p0_identifiability?.summary?.execution_ready || 0),
          preP0AuditedState: Number(window.RESEARCH_SYSTEM_STATE?.pre_p0_identifiability?.summary?.audited || 0),
          runtimePanels: document.querySelectorAll('.experiment-runtime-panel').length,
          runtimeCells: document.querySelectorAll('.experiment-runtime-grid>div').length,
          runtimeStages: document.querySelectorAll('.experiment-runtime-stages .runtime-stage').length,
          iterationPanels: document.querySelectorAll('.experiment-iteration-panel').length,
          diagnosisCards: document.querySelectorAll('.experiment-diagnosis-card').length,
          diagnosisTypes: [...document.querySelectorAll('.experiment-diagnosis-card')].map(x=>x.dataset.diagnosis || ''),
          iterationScaleUp: Number(window.RESEARCH_SYSTEM_STATE?.experiment_iteration?.summary?.scale_up_allowed || 0),
          iterationBeliefUpdates: Number(window.RESEARCH_SYSTEM_STATE?.experiment_iteration?.summary?.belief_updates_allowed || 0),
          runtimeReady: Boolean(window.P0_RUNTIME_READINESS?.environment_ready),
          launchReady: Boolean(window.P0_RUNTIME_READINESS?.launch_ready),
          smokeReady: Boolean(window.P0_RUNTIME_READINESS?.smoke_rollout?.ready),
          runtimeBlockers: (window.P0_RUNTIME_READINESS?.blockers || []).length,
          runtimeGpu: (window.P0_RUNTIME_READINESS?.gpus || []).length,
          runtimeModelReady: Boolean(window.P0_RUNTIME_READINESS?.model?.ready),
          runtimeSupported: (window.P0_RUNTIME_READINESS?.supported_p0 || []).length,
          p0AuthorizedState: Number(window.RESEARCH_SYSTEM_STATE?.pilot_registry?.summary?.p0_authorized || 0),
          p1AuthorizedState: Number(window.RESEARCH_SYSTEM_STATE?.pilot_registry?.summary?.p1_authorized || 0),
          validResults: Number(window.RESEARCH_SYSTEM_STATE?.pilot_registry?.summary?.valid_result_files || 0),
          text: document.body.textContent || ''
        };""")
        require(experiments["chapters"] == 3, f"experiments page must have three chapters, got {experiments['chapters']}")
        require((experiments["terminalPortfolio"],experiments["terminalRows"],experiments["terminalP0"],experiments["terminalP0Ready"]) == (1,20,20,0), f"terminal experiment portfolio is not aligned with Paper Ideas: {experiments}")
        require((experiments["terminalStarted"],experiments["terminalPending"],experiments["auditQueue"],experiments["auditItems"]) == (11,9,1,9), f"started/pending audit split is wrong: {experiments}")
        require(experiments["admissionPanel"] == 1 and experiments["admissionRows"] == 16 and experiments["admissionSummary"].get("active_p0") == 20 and experiments["admissionSummary"].get("transitioned_from_p0_ready") == 16 and experiments["admissionSummary"].get("settings_complete") == 20, f"P0 admission/settings panel is incomplete: {experiments}")
        require(experiments["offlinePanel"] == 1 and experiments["offlineSummary"].get("ideas") == 16 and experiments["offlineSummary"].get("checks_failed",0) >= 9 and experiments["offlineSummary"].get("checks_synthetic_pass") == 14 and experiments["offlineSummary"].get("gpu0_stop") == 6, f"offline qualification panel/state is incomplete: {experiments}")
        require(experiments["realizabilitySummary"].get("audited") == 14 and experiments["realizabilitySummary"].get("synthetic_pass") == 14, f"synthetic realizability summary is wrong: {experiments}")
        require(experiments["b10Decision"] == "STOP_MATCHED_NARY_EQUIVALENT" and experiments["a6Decision"] == "STOP_MATCHED_GROUP_TESTING_EQUIVALENT" and experiments["a7Decision"] == "STOP_MATCHED_SHALLOW_RULE_EQUIVALENT" and experiments["b3Decision"] == "SCREENING_SIGNAL_REAL_COINTERACTION_REQUIRED" and experiments["b3RuntimeDecision"] == "HOLD_RUNTIME_ENVIRONMENT_DRIFT" and experiments["e2Decision"] == "STOP_MATCHED_E1_DIRECT_EDIT_EQUIVALENT" and experiments["e3Decision"] == "STOP_STATEFUL_DETERMINISTIC_PEX_CEILING" and experiments["e4Decision"] == "STOP_MATCHED_BOOLEAN_RULE_EQUIVALENT" and experiments["p0StopRows"] == 6, f"A-6/A-7/B-10/E-2/E-3/E-4 STOPs or B-3 screening/runtime HOLD are not visible: {experiments}")
        require(experiments["legacyArchives"] >= 3, f"legacy experiment evidence must be demoted into traceability archives: {experiments['legacyArchives']}")
        require((experiments["toc2"], experiments["toc3"], experiments["toc4"]) == (4, 3, 0), f"experiments TOC hierarchy is wrong: {experiments['toc2']}/{experiments['toc3']}/{experiments['toc4']}")
        require(experiments["board"] == 1 and experiments["cards"] == 5, f"experiment queue is incomplete: {experiments['board']}/{experiments['cards']}")
        require((experiments["authorized"], experiments["collision"], experiments["redesign"], experiments["scenario"], experiments["openCards"]) == (0, 0, 2, 1, 0), f"experiment gate counts are wrong: {experiments['authorized']}/{experiments['collision']}/{experiments['redesign']}/{experiments['scenario']}/{experiments['openCards']}")
        require((experiments["phaseTracks"], experiments["phaseCells"], experiments["liveResults"]) == (5, 20, 5), f"phase/result tracking is incomplete: {experiments['phaseTracks']}/{experiments['phaseCells']}/{experiments['liveResults']}")
        require(experiments["executedResults"] == 0 and experiments["validResults"] == 0, f"unexecuted P0s must not fabricate effects: {experiments['executedResults']}/{experiments['validResults']}")
        require(experiments["ledger"] == 1 and experiments["ledgerCells"] == 6, f"resource ledger is incomplete: {experiments['ledger']}/{experiments['ledgerCells']}")
        require(experiments["resultRows"] == 5 and experiments["approvalRows"] == 5 and experiments["gateCells"] == 4, f"result/approval tables are incomplete: {experiments['resultRows']}/{experiments['approvalRows']}/{experiments['gateCells']}")
        require(experiments["preP0Panels"] == 1 and experiments["preP0Cards"] == 4 and experiments["preP0ReadyCards"] == 0 and experiments["preP0BlockedCards"] == 4 and (experiments["preP0ReadyState"],experiments["preP0AuditedState"]) == (0,4), f"Pre-P0 panel/state is incomplete: {experiments['preP0Panels']}/{experiments['preP0Cards']}/{experiments['preP0ReadyCards']}/{experiments['preP0BlockedCards']} state={experiments['preP0ReadyState']}/{experiments['preP0AuditedState']}")
        require(experiments["runtimePanels"] == 1 and experiments["runtimeCells"] == 7 and experiments["runtimeStages"] == 5, f"runtime readiness panel is incomplete: {experiments['runtimePanels']}/{experiments['runtimeCells']}/{experiments['runtimeStages']}")
        require(experiments["iterationPanels"] == 1 and experiments["diagnosisCards"] == 4, f"experiment diagnosis panel is incomplete: {experiments['iterationPanels']}/{experiments['diagnosisCards']}")
        require(set(experiments["diagnosisTypes"]) == {"representation-signal-mismatch","no-label-variation","matched-simplification-tie","objective-claim-mismatch"}, f"unexpected experiment diagnoses: {experiments['diagnosisTypes']}")
        require(experiments["iterationScaleUp"] == 0 and experiments["iterationBeliefUpdates"] == 1, f"diagnosis policy must permit only the identifiable B-1 belief update and no scale-up: {experiments['iterationScaleUp']}/{experiments['iterationBeliefUpdates']}")
        require(experiments["runtimeGpu"] >= 1 and experiments["runtimeModelReady"] and experiments["runtimeSupported"] == 2, f"runtime preflight lost GPU/model/harness readiness: {experiments}")
        require((experiments["runtimeReady"] and experiments["runtimeBlockers"] == 0) or ((not experiments["runtimeReady"]) and experiments["runtimeBlockers"] >= 1), f"runtime readiness/blocker state is inconsistent: {experiments}")
        require(experiments["launchReady"] == (experiments["runtimeReady"] and experiments["smokeReady"]), f"P0 launch must require both runtime and smoke readiness: {experiments}")
        require((experiments["p0AuthorizedState"], experiments["p1AuthorizedState"]) == (0, 0), f"live authorization state is wrong: {experiments['p0AuthorizedState']}/{experiments['p1AuthorizedState']}")
        require(("结果与效果总表" in experiments["text"] or "Results and effect snapshot" in experiments["text"]) and ("人工审批与下一阶段锁" in experiments["text"] or "Human approvals and next-phase locks" in experiments["text"]), "experiment result/approval sections are not visible")
        require(("Pre-P0" in experiments["text"] and ("实验诊断与原子修复树" in experiments["text"] or "Experiment diagnosis and atomic repair tree" in experiments["text"])), "Pre-P0 or experiment diagnosis/repair section is not visible")
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
