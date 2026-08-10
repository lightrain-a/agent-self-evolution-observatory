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
          text: document.body.textContent || '',
          graphLabel: [...document.querySelectorAll('.system-components-panel tbody tr')].map(x=>x.textContent).find(x=>x.includes('引文与证据图谱')||x.includes('Citation and evidence graph')) || '',
          portfolio: window.DISCUSSION_READY_IDEAS || {},
          stateSummary: window.RESEARCH_SYSTEM_STATE?.summary || {}
        };""")
        require(system["components"] == 11, f"expected eleven backend components, got {system['components']}")
        require(system["progressItems"] == 6, f"expected six final-gate progress cells, got {system['progressItems']}")
        require((system["portfolio"].get("count"), system["portfolio"].get("target"), system["portfolio"].get("ready")) == (20, 20, True), f"wrong discussion portfolio: {system['portfolio']}")
        require("20/20" in system["text"] or "20 / 20" in system["text"], "20/20 final-gate progress is not visible")
        require(system["stateSummary"].get("v53_external_pass") == 3, "system state does not expose three v5.3 PASS ideas")
        execute(session_id, "document.querySelector('.language-toggle')?.click();")
        time.sleep(1)
        zh = execute(session_id, "return {graph:[...document.querySelectorAll('.system-components-panel tbody tr')].map(x=>x.textContent).find(x=>x.includes('引文与证据图谱'))||'', text:document.body.textContent||''};")
        require("引文与证据图谱" in zh["graph"], "citation/evidence component is not localized")
        require("20/20" in zh["text"] or "20 / 20" in zh["text"], "Chinese system page lost the final-gate target")

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
          discussedGroups: document.querySelectorAll('.human-science-group').length,
          discussedCards: document.querySelectorAll('.human-review-idea-card').length,
          readyCards: document.querySelectorAll('.human-review-idea-card.human-tone-ready').length,
          redesignCards: document.querySelectorAll('.human-review-idea-card.human-tone-redesign').length,
          pausedCards: document.querySelectorAll('.human-review-idea-card.human-tone-paused').length,
          feedbackSummaries: document.querySelectorAll('.human-review-idea-card .human-idea-summary p').length,
          humanOpinionBoxes: document.querySelectorAll('.human-opinion-box').length,
          iterationBoxes: document.querySelectorAll('.human-iteration-box').length,
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
        require(ideas["p0Summary"].get("ready_now") == 0 and ideas["p0Summary"].get("pre_p0_blocked") == 4 and ideas["p0Summary"].get("gpu_hours_cap_ready_now") == 0 and ideas["p0Summary"].get("p1_authorized") == 0, f"P0 Pre-P0/resource summary is wrong: {ideas['p0Summary']}")
        require(ideas["p0Policy"].get("pre_p0_identifiability_required") is True and ideas["p0Policy"].get("automatic_p0_to_p1_forbidden") is True and ideas["p0Policy"].get("p0_pass_requires_human_approval") is True, f"P0 human/Pre-P0 approval policy is missing: {ideas['p0Policy']}")
        require((ideas["toc2"], ideas["toc3"], ideas["toc4"]) == (3, 11, 0), f"paper-ideas TOC hierarchy is wrong: {ideas['toc2']}/{ideas['toc3']}/{ideas['toc4']}")
        require(ideas["discussedGroups"] == 6 and ideas["discussedCards"] == 26, f"expected six scientific groups and 26 discussed ideas, got {ideas['discussedGroups']}/{ideas['discussedCards']}")
        require((ideas["readyCards"], ideas["redesignCards"], ideas["pausedCards"]) == (2, 17, 7), f"human-review status counts are wrong: {ideas['readyCards']}/{ideas['redesignCards']}/{ideas['pausedCards']}")
        require(ideas["feedbackSummaries"] == 26, f"every discussed idea must expose one current summary, got {ideas['feedbackSummaries']}")
        require(ideas["humanOpinionBoxes"] == 26, f"all 26 discussed ideas must preserve the human opinion, got {ideas['humanOpinionBoxes']}")
        require(ideas["iterationBoxes"] == 17, f"all 17 method-redesign ideas must show the 2026-08-10 iteration, got {ideas['iterationBoxes']}")
        require(ideas["methodologyPanels"] == 1 and ideas["originalEvalGuides"] == 1, f"human-opinion audit/original-eval methodology panels are missing: {ideas['methodologyPanels']}/{ideas['originalEvalGuides']}")
        require(ideas["canonicalReviewCount"] == 26, f"canonical human-review map must cover all 26 ideas, got {ideas['canonicalReviewCount']}")
        require(ideas["humanRecommendationStats"] == [4,14,7,1], f"canonical human recommendation counts are wrong: {ideas['humanRecommendationStats']}")
        require(any('Original Idea 4' in label or '原讨论 Idea 4' in label for label in ideas["originalIdeaLabels"]), f"original discussion numbering is not visible: {ideas['originalIdeaLabels'][:5]}")
        require(ideas["concreteExamples"] == 26 and ideas["parentMergeRules"] >= 1, f"intuition/example or parent-merge UI gate is missing: {ideas['concreteExamples']}/{ideas['parentMergeRules']}")
        require(ideas["openDiscussedCards"] == 0 and ideas["openNewCards"] == 0, f"all idea cards must be collapsed by default, got {ideas['openDiscussedCards']}/{ideas['openNewCards']}")
        require(len(ideas["codes"]) == 26 and len(set(ideas["codes"])) == 26, f"group codes are missing or duplicated: {ideas['codes']}")
        require(all(code in ideas["codes"] for code in ("A-1","A-5","B-1","B-7","C-1","D-1","E-1","F-1","F-3")), f"expected stable group codes are missing: {ideas['codes']}")
        require(ideas["newGroups"] == 5 and ideas["newCards"] == 18, f"new-idea staging area is incomplete after FINAL20 merge audit: {ideas['newGroups']}/{ideas['newCards']}")
        require((ideas["newFinal"], ideas["newInspired"]) == (3, 15), f"supplemental provenance counts are wrong after merge: {ideas['newFinal']}/{ideas['newInspired']}")
        require(ideas["mergedMethods"] >= 8, f"merged FINAL method provenance is not visible on discussed ideas: {ideas['mergedMethods']}")
        require(ideas["freshCollisionBlocks"] == 17 and ideas["freshCollisionLinks"] >= 48, f"fresh reducibility sources are missing from redesign ideas: {ideas['freshCollisionBlocks']}/{ideas['freshCollisionLinks']}")
        require(all(marker in ideas["text"] for marker in ("已讨论 Idea","新增 Idea","预算校准的预测性回归面板","跨过程验证经验蒸馏","成对编辑效应工作流更新策略","决策翻转驱动的转移准入","E-3","E-4","B-8")), "redesigned/current idea titles or standalone FINAL codes are missing")

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
