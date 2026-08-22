#!/usr/bin/env python3
"""Fast real-browser audit for ResearchItem/PaperRegistry public control-plane invariants."""
from __future__ import annotations

import subprocess
import sys
import time

from hierarchy_smoke_test import HTTP_PORT, ROOT, WEBDRIVER_PORT, browser_runtime, execute, request


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def navigate(session_id: str, path: str) -> None:
    request("POST", f"/session/{session_id}/url", {"url": f"http://127.0.0.1:{HTTP_PORT}{path}"})
    deadline = time.time() + 12
    while time.time() < deadline:
        ready = execute(session_id, "return document.readyState === 'complete' && Boolean(document.querySelector('.layout')); ")
        if ready:
            return
        time.sleep(0.25)
    raise AssertionError(f"page did not become ready: {path}")


def main() -> None:
    driver_command, capabilities = browser_runtime()
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(HTTP_PORT), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    driver = subprocess.Popen(driver_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    session_id = ""
    try:
        last_error: Exception | None = None
        for attempt in range(3):
            time.sleep(2 + attempt)
            try:
                session_id = request("POST", "/session", capabilities)["value"]["sessionId"]
                break
            except Exception as error:
                last_error = error
                if driver.poll() is not None:
                    driver = subprocess.Popen(driver_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not session_id:
            raise RuntimeError(f"unable to create browser session: {last_error}")

        navigate(session_id, "/selected-paper.html")
        selected = execute(session_id, """
          const papers = window.PAPER_REGISTRY?.papers || [];
          return {
            summary: window.PAPER_REGISTRY?.summary || {},
            cards: document.querySelectorAll('.paper-registry-card').length,
            actions: Object.fromEntries([...document.querySelectorAll('.paper-registry-card')].map(x => [x.dataset.paperId || '', x.dataset.nextAction || ''])),
            noveltyPortfolio: document.querySelectorAll('#paper-novelty-portfolio').length,
            noveltyDetails: document.querySelectorAll('.paper-novelty-detail').length,
            temporal: papers.find(x => x.paper_id === 'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK') || {},
            failureMemory: papers.find(x => x.paper_id === 'D2-PAPER-FAILURE-MEMORY-PROVENANCE') || {},
            text: document.body.textContent || ''
          };
        """)
        summary = selected["summary"]
        require(selected["cards"] == 5, f"PaperRegistry card count drifted: {selected['cards']}")
        require(summary.get("submission_ready") == 5, f"ledger readiness drifted: {summary}")
        require(summary.get("gate_clean_submission_ready") == 4, f"gate-clean count drifted: {summary}")
        require(summary.get("internal_action_required") == 1 and summary.get("no_internal_action") == 4, f"internal-action split drifted: {summary}")
        require(summary.get("by_internal_action") == {"EXTERNAL_EVIDENCE_REQUIRED": 1, "NO_INTERNAL_ACTION": 4}, f"internal-action classes drifted: {summary}")
        require(selected["noveltyPortfolio"] == 1 and selected["noveltyDetails"] == 5, "advisor novelty audit must remain visible for all five papers")
        require(selected["actions"].get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK") == "EXTERNAL_EVIDENCE_REQUIRED", f"Temporal-Skill action drifted: {selected['actions']}")
        require(selected["actions"].get("D2-PAPER-FAILURE-MEMORY-PROVENANCE") == "NO_INTERNAL_ACTION", f"Failure-Memory action drifted: {selected['actions']}")
        temporal = selected["temporal"]
        require((temporal.get("primary_next_action") or {}).get("blocking_on") == "TIMESAGE_EVALUATED_FIRST_PARTY_ASSETS_NOT_PUBLIC", f"Temporal-Skill blocker drifted: {temporal}")
        require((temporal.get("latest_paper_preparation") or {}).get("pass") is False, "Temporal-Skill latest Paper Preparation must remain failed")
        require(selected["failureMemory"].get("active_unrefuted_claims") == 2, f"Failure-Memory claim boundary drifted: {selected['failureMemory']}")
        has_next_label = "Research OS 下一步" in selected["text"] or "Research OS next action" in selected["text"]
        has_internal_summary = ("内部已闭环=4" in selected["text"] and "仍有内部动作=1" in selected["text"]) or ("internally closed=4" in selected["text"] and "internal action required=1" in selected["text"])
        require(has_next_label and has_internal_summary, "PaperRegistry human-readable internal-action summary is missing")

        navigate(session_id, "/index.html")
        home = execute(session_id, """
          return {
            summary: window.RESEARCH_DASHBOARD?.summary || {},
            text: document.body.textContent || ''
          };
        """)
        home_summary = home["summary"]
        require(home_summary.get("current_attention") == 6 and home_summary.get("research_handoffs") == 1 and home_summary.get("research_waiting_reopen") == 5, f"Home ResearchItem control split drifted: {home_summary}")
        require(home_summary.get("machine_actionable_attention") == 0, f"Home machine-actionable attention must remain zero: {home_summary}")
        require("PAPERSTATE_HANDOFF" in home["text"] and "REOPEN_CONDITION_REQUIRED" in home["text"] and "machine-actionable=0" in home["text"], "Home control plane does not distinguish tracked handoff / waiting HOLD / machine-actionable=0")

        navigate(session_id, "/system-overview.html")
        overview = execute(session_id, """
          return {
            paper: window.RESEARCH_SYSTEM_STATE?.paper_acceptance?.summary || {},
            source: window.RESEARCH_SYSTEM_STATE?.paper_acceptance?.ledger_index_source || '',
            memory: window.RESEARCH_SYSTEM_STATE?.research_memory_wiki?.summary || {},
            text: document.body.textContent || ''
          };
        """)
        paper = overview["paper"]
        memory = overview["memory"]
        require(paper.get("ledger_submission_ready_papers") == 5 and paper.get("gate_clean_submission_ready_papers") == 4, f"ResearchSystem paper summary drifted: {paper}")
        require(paper.get("internal_action_required_papers") == 1 and paper.get("no_internal_action_papers") == 4, f"ResearchSystem internal-action split drifted: {paper}")
        require(memory.get("review_lessons") == 5, f"Research Memory review lessons drifted: {memory}")
        require("论文审查经验 5" in overview["text"] or "5 paper-review lessons" in overview["text"], "System Overview does not expose structured paper-review learning")

        navigate(session_id, "/research-map.html")
        research_map = execute(session_id, """
          const d = window.RESEARCH_DASHBOARD || {};
          return {
            summary: d.summary || {},
            actions: Object.fromEntries((d.attention || []).map(x => [x.code || '', x.next_action_class || ''])),
            text: document.body.textContent || ''
          };
        """)
        research_summary = research_map["summary"]
        require(research_summary.get("research_primary_next_action_counts") == {"MERGED_NO_STANDALONE_ACTION": 10, "NO_INTERNAL_ACTION": 71, "PAPERSTATE_HANDOFF": 1, "REOPEN_CONDITION_REQUIRED": 5}, f"ResearchItem action distribution drifted: {research_summary}")
        require(research_summary.get("machine_actionable_research_items") == 0 and research_summary.get("machine_actionable_attention") == 0, f"ResearchItem machine authority drifted: {research_summary}")
        require(research_summary.get("research_handoffs") == 1 and research_summary.get("research_waiting_reopen") == 5, f"Dashboard ResearchItem control split drifted: {research_summary}")
        require(research_summary.get("paper_internal_action_required") == 1 and research_summary.get("paper_no_internal_action") == 4, f"Dashboard paper action split drifted: {research_summary}")
        require(research_map["actions"].get("E-7") == "PAPERSTATE_HANDOFF" and research_map["actions"].get("G-1") == "REOPEN_CONDITION_REQUIRED", f"Dashboard attention actions drifted: {research_map['actions']}")
        require("PAPERSTATE_HANDOFF" in research_map["text"] and "REOPEN_CONDITION_REQUIRED" in research_map["text"] and "machine-actionable=0" in research_map["text"], "Research Map does not expose tracked/waiting/machine-actionable ResearchItem control classes")

        navigate(session_id, "/paper-ideas.html")
        ideas = execute(session_id, """
          const rows = window.RESEARCH_ITEM_STATE?.research_items || [];
          const e7 = rows.find(x => x.code === 'E-7') || {};
          const stri = (window.PAPER_REGISTRY?.papers || []).find(x => x.paper_id === 'STRI') || {};
          const actionClasses = ['NO_INTERNAL_ACTION','MERGED_NO_STANDALONE_ACTION','REOPEN_CONDITION_REQUIRED','PAPERSTATE_HANDOFF'];
          const parentActionClasses = [...document.querySelectorAll('.canonical-parent-item .canonical-lifecycle-strip')].map(strip => {
            const text = strip.children[1]?.textContent || '';
            return actionClasses.find(name => text.includes(name)) || '';
          });
          return {
            summary: window.RESEARCH_ITEM_STATE?.summary || {},
            e7Action: e7.primary_next_action?.action_class || '',
            paperAction: stri.primary_next_action?.action_class || '',
            parentActionClasses,
            text: document.body.textContent || ''
          };
        """)
        require(ideas["e7Action"] == "PAPERSTATE_HANDOFF" and ideas["paperAction"] == "NO_INTERNAL_ACTION", f"Paper Ideas handoff/internal-closure boundary drifted: {ideas}")
        require("PAPERSTATE_HANDOFF" in ideas["text"] and "NO_INTERNAL_ACTION" in ideas["text"], "Paper Ideas does not expose canonical ResearchItem→PaperState actions")
        require(len(ideas["parentActionClasses"]) == 26 and ideas["parentActionClasses"].count("NO_INTERNAL_ACTION") == 16 and ideas["parentActionClasses"].count("MERGED_NO_STANDALONE_ACTION") == 6 and ideas["parentActionClasses"].count("REOPEN_CONDITION_REQUIRED") == 4, f"Paper Ideas parent cards do not render canonical 16/6/4 actions: {ideas['parentActionClasses']}")
        require("下一步只剩人工作者责任确认" not in ideas["text"] and "only human author responsibility/signoff" not in ideas["text"], "Paper Ideas still frames real submission as an internal Research OS next action")

        print("PASS")
        print("Public control plane verified in a real browser: ResearchItem 71/10/5/1 actions; PaperState 5/4/1; 5 review lessons")
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
