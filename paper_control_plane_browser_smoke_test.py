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
            gateCleanCount: [...document.querySelectorAll('.paper-registry-card')].filter(x => x.dataset.gateClean === 'true').length,
            noveltyPortfolio: document.querySelectorAll('#paper-novelty-portfolio').length,
            noveltyDetails: document.querySelectorAll('.paper-novelty-detail').length,
            noveltyAttackCards: document.querySelectorAll('[data-reviewer-novelty-attack]').length,
            noveltyAttackText: [...document.querySelectorAll('[data-reviewer-novelty-attack]')].map(x => x.textContent || '').join(' | '),
            readerPortfolio: document.querySelectorAll('#paper-reader-portfolio').length,
            readerBriefs: document.querySelectorAll('.paper-reader-brief').length,
            readerEvidenceCards: document.querySelectorAll('.paper-reader-evidence-card').length,
            readerFigures: document.querySelectorAll('.paper-reader-figure').length,
            readerFigureText: Object.fromEntries([...document.querySelectorAll('.paper-reader-figure')].map(figure => [figure.dataset.paperFigure || '', figure.textContent || ''])),
            readerBriefText: Object.fromEntries([...document.querySelectorAll('.paper-detail-section[data-paper-toc-root]')].map(section => [section.id || '', section.querySelector('.paper-reader-brief')?.textContent || ''])),
            storyBlueprint: document.querySelectorAll('#paper-story-blueprint').length,
            storyPhases: document.querySelectorAll('.paper-story-v3-phase-grid article').length,
            storyBlueprintSteps: document.querySelectorAll('.paper-story-blueprint-chain-v3 article').length,
            openFullStoryContracts: document.querySelectorAll('.paper-story-v3-full-chain[open]').length,
            storyArchetypes: document.querySelectorAll('.paper-story-archetype-guide article').length,
            storyPapers: document.querySelectorAll('[data-paper-story]').length,
            storyDownloadGroups: document.querySelectorAll('.paper-story-downloads').length,
            storyDownloadPdfs: [...document.querySelectorAll('.paper-story-download-pdf')].map(x => x.getAttribute('href') || ''),
            storyDownloadZips: [...document.querySelectorAll('.paper-story-download-zip')].map(x => x.getAttribute('href') || ''),
            storyDownloadSupplements: [...document.querySelectorAll('.paper-story-download-supplement')].map(x => x.getAttribute('href') || ''),
            storyClosestWorkFolds: document.querySelectorAll('.paper-story-closest-work').length,
            openStoryClosestWorkFolds: document.querySelectorAll('.paper-story-closest-work[open]').length,
            storyClosestWorkGroups: document.querySelectorAll('.paper-story-closest-group').length,
            storyClosestWorkCards: document.querySelectorAll('.paper-story-closest-card').length,
            storyClosestWorkLinks: [...document.querySelectorAll('.paper-story-closest-card>header a')].map(x => x.href || ''),
            storyMissingObjects: document.querySelectorAll('.paper-story-object-question article:first-child').length,
            storyGapCards: document.querySelectorAll('.paper-story-gap-grid article').length,
            storyPredictions: document.querySelectorAll('.paper-story-prediction-grid article').length,
            storyAlternatives: document.querySelectorAll('.paper-story-alternative-table tbody tr').length,
            storyContracts: document.querySelectorAll('.paper-story-contract-grid').length,
            storyRQs: document.querySelectorAll('.paper-story-rq-grid article').length,
            storyComponents: document.querySelectorAll('.paper-story-component-table tbody tr').length,
            storyStressTests: document.querySelectorAll('.paper-story-mechanism-test-grid article').length,
            storyMechanisms: document.querySelectorAll('.paper-story-mechanism-table tbody tr').length,
            storyCoE: document.querySelectorAll('.paper-story-coe-table').length,
            storyOutlineRows: document.querySelectorAll('.paper-story-paper-outline li').length,
            auditFolds: document.querySelectorAll('.paper-reader-audit-fold').length,
            openAuditFolds: document.querySelectorAll('.paper-reader-audit-fold[open]').length,
            acceptanceActionTexts: [...document.querySelectorAll('.paper-acceptance-workflow .current-status-rule')].map(x => (x.textContent || '').trim()),
            temporal: papers.find(x => x.paper_id === 'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK') || {},
            failureMemory: papers.find(x => x.paper_id === 'D2-PAPER-FAILURE-MEMORY-PROVENANCE') || {},
            publicationIdentities: Object.fromEntries(papers.map(x => [x.paper_id || '', x.publication_identity || {}])),
            text: document.body.textContent || ''
          };
        """)
        summary = selected["summary"]
        require(selected["cards"] == 5, f"PaperRegistry card count drifted: {selected['cards']}")
        require(summary.get("submission_ready") == 5, f"ledger readiness drifted: {summary}")
        expected_internal = sum(action != "NO_INTERNAL_ACTION" for action in selected["actions"].values())
        require(summary.get("gate_clean_submission_ready") == selected["gateCleanCount"], f"gate-clean count must be derived from current paper rows: {summary}")
        require(summary.get("internal_action_required") == expected_internal and summary.get("no_internal_action") == 5 - expected_internal, f"internal-action split must follow current paper rows: {summary}")
        require(selected["noveltyPortfolio"] == 1 and selected["noveltyDetails"] == 5 and selected["noveltyAttackCards"] == 5, "advisor novelty audit and reviewer-attack layer must cover all five papers")
        require(all(marker in selected["noveltyAttackText"] for marker in ("Mem-α", "AttriMem", "Anything2Skill", "MutMem", "Experiential Reflective Learning", "unresolved")), f"reviewer novelty attack is missing decision-critical pressure works or boundaries: {selected['noveltyAttackText'][:2500]}")
        require(selected["readerPortfolio"] == 1 and selected["readerBriefs"] == 5 and selected["readerFigures"] == 5, f"reader-first paper layer is incomplete: {selected}")
        require(selected["storyBlueprint"] == 1 and selected["storyPhases"] == 5 and selected["storyBlueprintSteps"] == 15 and selected["openFullStoryContracts"] == 0 and selected["storyArchetypes"] == 5 and selected["storyPapers"] == 5 and selected["storyClosestWorkFolds"] == 5 and selected["openStoryClosestWorkFolds"] == 0 and selected["storyClosestWorkGroups"] == 16 and selected["storyClosestWorkCards"] == 42 and len(selected["storyClosestWorkLinks"]) == 42 and all(link.startswith("https://") for link in selected["storyClosestWorkLinks"]) and selected["storyMissingObjects"] == 5 and selected["storyGapCards"] == 15 and selected["storyPredictions"] >= 15 and selected["storyAlternatives"] >= 15 and selected["storyContracts"] == 5 and selected["storyRQs"] >= 16 and selected["storyComponents"] >= 18 and selected["storyStressTests"] >= 15 and selected["storyMechanisms"] >= 14 and selected["storyCoE"] == 5 and selected["storyOutlineRows"] >= 35, f"Paper Story V3 argument-chain / closest-work layer is incomplete: {selected}")
        expected_download_pdfs = {"downloads/E1-STRI.pdf", "downloads/G1-Agent-Safety-R9.pdf", "downloads/C1-Proxy-Reward.pdf", "downloads/E2-Temporal-Skill.pdf", "downloads/B1-Failure-Memory.pdf"}
        expected_download_zips = {"downloads/STRI-ICLR2027-source.zip", "downloads/Agent-Safety-R9-source.zip", "downloads/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-source.zip", "downloads/D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK-source.zip", "downloads/D2-PAPER-FAILURE-MEMORY-PROVENANCE-source.zip"}
        expected_download_supplements = {"downloads/STRI-ICLR2027-supplement.zip", "downloads/Agent-Safety-R9-supplement.zip", "downloads/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-supplement.zip", "downloads/D2-PAPER-FAILURE-MEMORY-PROVENANCE-supplement.zip"}
        require(selected["storyDownloadGroups"] == 5 and set(selected["storyDownloadPdfs"]) == expected_download_pdfs and set(selected["storyDownloadZips"]) == expected_download_zips and set(selected["storyDownloadSupplements"]) == expected_download_supplements, f"Every Paper Story must expose the publication-numbered stable PDF + source ZIP pair, plus supplement when one exists: {selected}")
        publication_identities = selected.get("publicationIdentities") or {}
        require({k: (publication_identities.get(k) or {}).get("code") for k in ("STRI","AGENT-SAFETY-R9","D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE","D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK","D2-PAPER-FAILURE-MEMORY-PROVENANCE")} == {"STRI":"E1","AGENT-SAFETY-R9":"G1","D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE":"C1","D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK":"E2","D2-PAPER-FAILURE-MEMORY-PROVENANCE":"B1"}, f"PaperRegistry publication identities drifted: {publication_identities}")
        require(all((publication_identities.get(k) or {}).get("category_zh") for k in publication_identities), f"Publication category names must be explicit beside letter codes: {publication_identities}")
        figures=selected["readerFigureText"]
        require(all(marker in figures.get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK","") for marker in ("47.5%","70%","100%","cross-domain grounding")), f"Temporal evidence figure lost the three-arm contrast or negative boundary: {figures.get('D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK','')}")
        require(all(marker in figures.get("D2-PAPER-FAILURE-MEMORY-PROVENANCE","") for marker in ("0.931","0.647","p=.0785","p=.0792","opposite sign")), f"Failure-Memory evidence figure must distinguish association from unresolved causal tests: {figures.get('D2-PAPER-FAILURE-MEMORY-PROVENANCE','')}")
        require(all(marker in figures.get("D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE","") for marker in ("0.700","0.595","256 rollouts","p=.00074","p=.311")), f"Reward-Memory figure must show prompt-control, terminal confirmation, and the negative action-distribution result: {figures.get('D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE','')}")
        briefs=selected["readerBriefText"]
        require(all(marker in briefs.get("paper-d2-paper-temporal-skill-causal-bottleneck","") for marker in ("100%","70%","47.5%","p=0.0156","Cross-domain grounding")), f"Temporal story lost its three-arm effect or negative boundary: {briefs.get('paper-d2-paper-temporal-skill-causal-bottleneck','')}")
        require(all(marker in briefs.get("paper-d2-paper-failure-memory-provenance","") for marker in ("0.931 vs 0.647","p=.0785","p=.0792","causal sign")), f"Failure-Memory reader brief must expose association and unresolved causal sign: {briefs.get('paper-d2-paper-failure-memory-provenance','')}")
        require(all(marker in briefs.get("paper-d2-paper-proxy-reward-memory-variance","") for marker in ("byte-identical","0.700","0.595","256","0.15625","p=0.00074","no-memory")), f"Reward-Memory story must explain write-time identification, strongest prompt control, terminal confirmation, and the no-memory boundary: {briefs.get('paper-d2-paper-proxy-reward-memory-variance','')}")
        require(selected["auditFolds"] >= 7 and selected["openAuditFolds"] == 0, f"machine audit layers must be present but collapsed by default: {selected}")
        temporal = selected["temporal"]
        temporal_prep = temporal.get("latest_paper_preparation") or {}
        temporal_clean = temporal_prep.get("pass") is True
        temporal_action = "NO_INTERNAL_ACTION" if temporal_clean else "PAPER_REPAIR_REQUIRED"
        require(len(selected["acceptanceActionTexts"]) == 5 and any(temporal_action in text for text in selected["acceptanceActionTexts"]), f"Paper Acceptance detail panels must render the latest Temporal action: {selected['acceptanceActionTexts']}")
        require(selected["actions"].get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK") == temporal_action, f"Temporal-Skill action must follow latest Paper Preparation: {selected['actions']}")
        require(selected["actions"].get("D2-PAPER-FAILURE-MEMORY-PROVENANCE") == "NO_INTERNAL_ACTION", f"Failure-Memory action drifted: {selected['actions']}")
        require((temporal.get("primary_next_action") or {}).get("blocking_on") == ("" if temporal_clean else "PAPER_PREPARATION_FAILED"), f"Temporal-Skill blocker must follow latest Paper Preparation: {temporal}")
        require(int(temporal_prep.get("required_gates") or 0) == 8 and int(temporal_prep.get("passed_gates") or 0) <= 8 and (temporal_clean or bool(temporal_prep.get("blockers"))), "Temporal-Skill latest Paper Preparation must be internally coherent")
        require((temporal.get("submission_readiness_context") or {}).get("recommended_immediate_submission") == "READY_FOR_HUMAN_SUBMISSION", f"Temporal-Skill readiness action drifted: {temporal}")
        require(((temporal.get("latest_mock_review") or {}).get("summary") or {}).get("scores") == [8,8,7], f"Temporal-Skill final Mock-PC drifted: {temporal}")
        source_native = temporal.get("source_native_evidence") or {}
        require((source_native.get("runtime_valid_rows"),source_native.get("distinct_endpoints"),source_native.get("institutional_systems")) == (1326,35,3), f"Temporal-Skill source-native evidence drifted: {source_native}")
        require(selected["failureMemory"].get("active_unrefuted_claims") == 2, f"Failure-Memory claim boundary drifted: {selected['failureMemory']}")
        has_next_label = "Research OS 下一步" in selected["text"] or "Research OS next action" in selected["text"]
        closed_count = summary.get("no_internal_action")
        action_count = summary.get("internal_action_required")
        has_internal_summary = (f"内部已闭环={closed_count}" in selected["text"] and f"仍有内部动作={action_count}" in selected["text"]) or (f"internally closed={closed_count}" in selected["text"] and f"internal action required={action_count}" in selected["text"])
        require(has_next_label and has_internal_summary, "PaperRegistry human-readable internal-action summary is missing")
        if "--selected-paper-only" in sys.argv:
            execute(session_id, "localStorage.setItem('agent-evolution-language','en'); return true;")
            navigate(session_id, "/selected-paper.html")
            en_text = execute(session_id, "return document.body.textContent || ''")
            en_markers = (
                "Open Closest-Work Argument Map",
                "Representative paper → mechanism → solved problem → overlap → residual object → claim boundary",
                "COMPONENT OVERLAP",
                "RESIDUAL OBJECT GAP",
                "CLAIM BOUNDARY",
                "Demystifying Agent Skills",
                "Remembering More, Risking More",
                "Memory Reward Inflation",
                "Counterfactual Trace Auditing",
                "Memory Provenance Laundering",
                "Evo-Harness",
                "SkillProx",
                "HyperSkill",
                "Download paper PDF",
                "Download source ZIP",
            )
            require(all(marker in en_text for marker in en_markers), f"English closest-work argument map is incomplete: {[m for m in en_markers if m not in en_text]}")
            execute(session_id, "localStorage.setItem('agent-evolution-language','zh'); return true;")
            navigate(session_id, "/selected-paper.html")
            zh_text = execute(session_id, "return document.body.textContent || ''")
            zh_markers = (
                "Paper Story V3 · 页面写作协议",
                "缺失的科学对象",
                "机制预测",
                "评测合同",
                "机制对齐压力测试",
                "先选论文类型",
                "真正缺的不是一个模块，而是一个科学对象",
                "先写设计要求，再介绍方法组件",
                "方法动机必须产生可观察的机制预测",
                "最强替代解释，以及我们怎样挑战它",
                "Evaluation Contract：先冻结怎样才算证明，再看结果",
                "机制对齐 stress test：优势是否在预测的条件里出现",
                "泛化、效率与明确失效边界",
                "最终 Claim Boundary + Chain of Evidence",
                "展开 Closest-Work Argument Map",
                "代表论文",
                "剩余科学对象",
                "已经覆盖我们的什么",
                "相对 Missing Object 还缺什么",
                "因此我们的贡献边界",
                "256 rollout",
                "p=0.00074",
                "no-skill anchor",
                "L0–L3",
                "5/10",
                "0 calls",
                "下载论文 PDF",
                "下载源码 ZIP",
                "E1 技能 · STRI · 技能分类表示不变性",
                "G1 安全 · R9 · 静态安全不等于未来安全",
                "C1 评估 · Proxy Reward · 奖励误差写入长期记忆",
                "E2 技能 · Temporal Skill · 可复用技能的因果瓶颈",
                "B1 记忆 · Provenance Ladder · 失败记忆来源的因果识别",
            )
            require(all(marker in zh_text for marker in zh_markers), f"Chinese paper-story chain is incomplete: {[m for m in zh_markers if m not in zh_text]}")
            print("PASS")
            print("Selected-paper Paper Story V3 verified in EN+ZH: 5 papers / 10 stable PDF+ZIP download buttons / 15-step blueprint / 5 archetypes / 16 approach groups / 42 closest-work comparisons / 5 reviewer novelty attacks / missing-object / mechanism-prediction / evaluation-contract / stress-test / CoE / collapsed audit")
            return

        navigate(session_id, "/index.html")
        home = execute(session_id, """
          return {
            summary: window.RESEARCH_DASHBOARD?.summary || {},
            text: document.body.textContent || ''
          };
        """)
        home_summary = home["summary"]
        require(home_summary.get("active_research_items") == 0 and home_summary.get("current_attention") == 6 and home_summary.get("research_handoffs") == 1 and home_summary.get("research_waiting_reopen") == 5, f"Home ResearchItem activity/visibility split drifted: {home_summary}")
        require(home_summary.get("machine_actionable_attention") == 0, f"Home machine-actionable attention must remain zero: {home_summary}")
        require("PAPERSTATE_HANDOFF" in home["text"] and "REOPEN_CONDITION_REQUIRED" in home["text"] and "machine-actionable" in home["text"], "Home control plane does not expose tracked handoff / waiting HOLD / machine-actionable labels")

        navigate(session_id, "/system-overview.html")
        overview = execute(session_id, """
          return {
            paper: window.RESEARCH_SYSTEM_STATE?.paper_acceptance?.summary || {},
            source: window.RESEARCH_SYSTEM_STATE?.paper_acceptance?.ledger_index_source || '',
            memory: window.RESEARCH_SYSTEM_STATE?.research_memory_wiki?.summary || {},
            backlog: window.RESEARCH_SYSTEM_STATE?.paper_first_paper_design_backlog?.summary || {},
            text: document.body.textContent || ''
          };
        """)
        paper = overview["paper"]
        memory = overview["memory"]
        backlog = overview["backlog"]
        require(paper.get("ledger_submission_ready_papers") == 5 and paper.get("gate_clean_submission_ready_papers") == summary.get("gate_clean_submission_ready"), f"ResearchSystem paper summary drifted: {paper}")
        require(paper.get("internal_action_required_papers") == summary.get("internal_action_required") and paper.get("no_internal_action_papers") == summary.get("no_internal_action"), f"ResearchSystem internal-action split drifted: {paper}")
        require(memory.get("review_lessons") == 5, f"Research Memory review lessons drifted: {memory}")
        require(backlog.get("pending_human_paper_design") == 0 and backlog.get("memory_prechecks") == 0 and backlog.get("review_lessons_selected") == 0, f"Paper Design backlog memory-precheck summary drifted: {backlog}")
        require("论文审查经验 5" in overview["text"] or "5 paper-review lessons" in overview["text"], "System Overview does not expose structured paper-review learning")
        require("PAPER_DESIGN memory precheck=0" in overview["text"] or "PAPER_DESIGN memory prechecks=0" in overview["text"], "System Overview does not expose the Review Memory → Paper Design precheck wiring")

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
        require(research_summary.get("research_primary_next_action_counts") == {"MERGED_NO_STANDALONE_ACTION": 10, "NO_INTERNAL_ACTION": 72, "PAPERSTATE_HANDOFF": 1, "REOPEN_CONDITION_REQUIRED": 5}, f"ResearchItem action distribution drifted: {research_summary}")
        require(research_summary.get("active_research_items") == 0 and research_summary.get("machine_actionable_research_items") == 0 and research_summary.get("machine_actionable_attention") == 0, f"ResearchItem activity/machine authority drifted: {research_summary}")
        require(research_summary.get("research_handoffs") == 1 and research_summary.get("research_waiting_reopen") == 5, f"Dashboard ResearchItem control split drifted: {research_summary}")
        require(research_summary.get("paper_internal_action_required") == summary.get("internal_action_required") and research_summary.get("paper_no_internal_action") == summary.get("no_internal_action"), f"Dashboard paper action split drifted: {research_summary}")
        require(research_map["actions"].get("E-7") == "PAPERSTATE_HANDOFF" and research_map["actions"].get("G-1") == "REOPEN_CONDITION_REQUIRED", f"Dashboard attention actions drifted: {research_map['actions']}")
        zero_active_label = "active ResearchItem=0" in research_map["text"] or "Active ResearchItems=0" in research_map["text"]
        require("PAPERSTATE_HANDOFF" in research_map["text"] and "REOPEN_CONDITION_REQUIRED" in research_map["text"] and zero_active_label and "machine-actionable=0" in research_map["text"], "Research Map does not expose zero-active plus tracked/waiting/machine-actionable ResearchItem control classes")

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
          const pfActionTexts = [...document.querySelectorAll('.paper-incubation-card .briefing-next')].map(x => x.textContent || '');
          const supplementalActionTexts = [...document.querySelectorAll('.supplemental-idea-card .briefing-next')].map(x => x.textContent || '');
          const safetyActionTexts = [...document.querySelectorAll('.agent-safety-briefing .briefing-next, #agent-safety-program .agent-safety-next-gate')].map(x => x.textContent || '');
          return {
            summary: window.RESEARCH_ITEM_STATE?.summary || {},
            e7Action: e7.primary_next_action?.action_class || '',
            paperAction: stri.primary_next_action?.action_class || '',
            parentActionClasses,
            pfActionTexts,
            supplementalActionTexts,
            safetyActionTexts,
            text: document.body.textContent || ''
          };
        """)
        require(ideas["e7Action"] == "PAPERSTATE_HANDOFF" and ideas["paperAction"] == "NO_INTERNAL_ACTION", f"Paper Ideas handoff/internal-closure boundary drifted: {ideas}")
        require(len(ideas["parentActionClasses"]) == 26 and ideas["parentActionClasses"].count("NO_INTERNAL_ACTION") == 16 and ideas["parentActionClasses"].count("MERGED_NO_STANDALONE_ACTION") == 6 and ideas["parentActionClasses"].count("REOPEN_CONDITION_REQUIRED") == 4, f"Paper Ideas parent cards do not render canonical 16/6/4 actions: {ideas['parentActionClasses']}")
        require(len(ideas["pfActionTexts"]) == 9 and sum("NO_INTERNAL_ACTION" in text for text in ideas["pfActionTexts"]) == 5 and sum("MERGED_NO_STANDALONE_ACTION" in text for text in ideas["pfActionTexts"]) == 4, f"PF cards must render canonical 5 stopped / 4 merged actions: {ideas['pfActionTexts']}")
        require(len(ideas["supplementalActionTexts"]) == 7 and all("NO_INTERNAL_ACTION" in text for text in ideas["supplementalActionTexts"]), f"supplemental ResearchItem cards must render canonical NO_INTERNAL_ACTION: {ideas['supplementalActionTexts']}")
        require(len(ideas["safetyActionTexts"]) >= 2 and all("REOPEN_CONDITION_REQUIRED" in text for text in ideas["safetyActionTexts"]), f"Agent Safety current cards must render canonical REOPEN_CONDITION_REQUIRED: {ideas['safetyActionTexts']}")
        require("下一步只剩人工作者责任确认" not in ideas["text"] and "only human author responsibility/signoff" not in ideas["text"], "Paper Ideas still frames real submission as an internal Research OS next action")

        print("PASS")
        print(f"Public control plane verified in a real browser: ResearchItem 72/10/5/1 actions; PaperState ledger=5 gate-clean={summary.get('gate_clean_submission_ready')} internal-actions={summary.get('internal_action_required')}; 5 review lessons")
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
