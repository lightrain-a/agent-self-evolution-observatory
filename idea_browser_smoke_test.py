#!/usr/bin/env python3
"""Focused real-browser smoke test for the research-system and idea-decision pages."""
from __future__ import annotations

import json
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
    expected_state = json.loads((ROOT / "generated" / "research-system-state.json").read_text(encoding="utf-8"))
    expected_current_status = json.loads((ROOT / "generated" / "current-research-status.json").read_text(encoding="utf-8"))
    expected_research = json.loads((ROOT / "generated" / "research-items.json").read_text(encoding="utf-8"))
    expected_registry = json.loads((ROOT / "generated" / "paper-registry.json").read_text(encoding="utf-8"))
    expected_registry_summary = expected_registry.get("summary") or {}
    expected_registry_stages = {str(row.get("paper_id") or ""): str(row.get("paper_stage") or "") for row in (expected_registry.get("papers") or [])}
    expected_research_summary = expected_research.get("summary") or {}
    expected_category_totals = [int(((expected_research_summary.get("by_category") or {}).get(code) or {}).get("portfolio_total") or 0) for code in "ABCDEFG"]
    expected_shadow_closed = int((expected_research_summary.get("source_kind_counts") or {}).get("shadow_closed") or 0)
    expected_closed_codes = {str(row.get("code") or "") for row in (expected_research.get("research_items") or []) if row.get("source_kind") == "shadow_closed"}
    expected_one_minute = 26 + 7 + 9 + expected_shadow_closed + 1 + 1  # +1 live MEMENTO Paper Design candidate
    expected_headline = expected_current_status.get("headline") or {}
    expected_shadow_latest = ((expected_state.get("paper_first_problem_search_portfolio") or {}).get("latest_run") or {})
    expected_shadow_summary = expected_shadow_latest.get("summary") or {}
    firefox, geckodriver = shutil.which("firefox"), shutil.which("geckodriver")
    snap_firefox = Path("/snap/firefox/current/usr/lib/firefox/firefox")
    snap_geckodriver = Path("/snap/firefox/current/usr/lib/firefox/geckodriver")
    if snap_firefox.is_file() and snap_geckodriver.is_file():
        firefox, geckodriver = str(snap_firefox), str(snap_geckodriver)
    if not firefox or not geckodriver:
        raise SystemExit("SKIP: Firefox/geckodriver unavailable")
    driver_command = [geckodriver, "--port", str(WEBDRIVER_PORT)]
    capabilities = {"capabilities": {"alwaysMatch": {"acceptInsecureCerts": True, "pageLoadStrategy": "none", "moz:firefoxOptions": {"binary": firefox, "args": ["-headless"]}}}}
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

        def wait_for(script: str, timeout: float = 20.0, interval: float = 0.5) -> bool:
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                try:
                    if execute(session_id, script):
                        return True
                except Exception:
                    pass
                time.sleep(interval)
            return False

        def ensure_language(target: str) -> None:
            desired = "zh-CN" if target == "zh" else "en"
            current = execute(session_id, "return document.documentElement.lang || ''")
            if current != desired:
                execute(session_id, "document.querySelector('.language-toggle')?.click();")
                require(wait_for(f"return document.documentElement.lang === '{desired}';", timeout=8), f"language did not switch to {target}")

        navigate("/system-overview.html", wait=1)
        require(wait_for("return (document.body.textContent||'').includes('SATURATION / DEAD-END MEMORY') && (document.body.textContent||'').includes('PAPER-FIRST');"), "research-system dynamic sections did not become ready")
        system = execute(session_id, """return {
          chapters: document.querySelectorAll('.page-chapter').length,
          readerChapters: document.querySelectorAll('.reader-roadmap-card').length,
          readerPhases: document.querySelectorAll('.reader-phase').length,
          deepDives: document.querySelectorAll('.system-deep-dive').length,
          authorityCards: document.querySelectorAll('.reader-authority-grid article').length,
          terminationAuthorityCards: document.querySelectorAll('.reader-termination-matrix article').length,
          responsibilityLayers: document.querySelectorAll('.system-layer-list article').length,
          temporalStages: document.querySelectorAll('.system-lifecycle-step').length,
          componentLayerHeaders: document.querySelectorAll('.system-component-layer').length,
          methodologyControls: document.querySelectorAll('.methodology-control-card').length,
          architectureSummary: window.RESEARCH_SYSTEM_STATE?.system_architecture?.summary || {},
          aiCheckpoints: document.querySelectorAll('.system-checkpoint-strip > div').length,
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
          primaryEvidence: window.RESEARCH_SYSTEM_STATE?.paper_first_primary_evidence || {},
          problemGenerator: window.RESEARCH_SYSTEM_STATE?.paper_first_problem_generator || {},
          problemQueue: window.RESEARCH_SYSTEM_STATE?.paper_first_problem_gate_queue || {},
          assetFirstSTRI: window.RESEARCH_SYSTEM_STATE?.asset_first_stri_paper_ready || {},
          paperVisualPortfolio: window.RESEARCH_SYSTEM_STATE?.paper_visual_evidence || {},
          striDownloads: [...document.querySelectorAll('a[data-stri-download]')].map(a => a.getAttribute('href')),
          globalRelationFreshness: window.RESEARCH_SYSTEM_STATE?.paper_first_global_relation_freshness || {},
          globalRelationDelta: window.RESEARCH_SYSTEM_STATE?.paper_first_global_relation_delta_preflight || {},
          globalRelationAdmission: window.RESEARCH_SYSTEM_STATE?.paper_first_global_relation_scan_admission || {},
          shadowSearchAdmission: window.RESEARCH_SYSTEM_STATE?.paper_first_shadow_search_admission || {},
          shadowContinuationFrontier: window.RESEARCH_SYSTEM_STATE?.paper_first_shadow_continuation_frontier || {},
          supportReleaseWatch: window.RESEARCH_SYSTEM_STATE?.paper_first_support_release_watch || {},
          supportAssetRecheck: window.RESEARCH_SYSTEM_STATE?.paper_first_support_asset_recheck_queue || {},
          supportAssetHandoff: window.RESEARCH_SYSTEM_STATE?.paper_first_support_asset_recheck_handoff || {},
          discoveryFrontier: window.RESEARCH_SYSTEM_STATE?.paper_first_discovery_frontier || {},
          stopClasses: window.RESEARCH_SYSTEM_STATE?.research_governance_v2?.stop_classes || {},
          agentSafetySummary: document.querySelectorAll('#agent-safety-system-summary').length,
          agentSafetyStage: window.AGENT_SAFETY_PROGRAM_STATE?.current_stage || '',
          agentSafetyRuntimeStatus: window.AGENT_SAFETY_PROGRAM_STATE?.runtime?.status || '',
          agentSafetyBoundedEvidence: window.AGENT_SAFETY_PROGRAM_STATE?.authority?.bounded_evidence_acquisition === true,
          agentSafetyQualification: window.AGENT_SAFETY_PROGRAM_STATE?.authority?.qualification_probe_execution === true,
          agentSafetyOverallExecution: window.AGENT_SAFETY_PROGRAM_STATE?.execution_authorized === true,
          agentSafetyQualificationStatus: window.AGENT_SAFETY_PROGRAM_STATE?.qualification?.status || '',
          agentSafetyQualifiedStates: window.AGENT_SAFETY_PROGRAM_STATE?.qualification?.qualified_state_count,
          agentSafetyPrincipleDeadEnd: window.AGENT_SAFETY_PROGRAM_STATE?.qualification?.principle_dead_end_certified === true,
          agentSafetyHeldoutFuture: window.AGENT_SAFETY_PROGRAM_STATE?.authority?.heldout_future_probe_execution === true,
          agentSafetyP0: window.AGENT_SAFETY_PROGRAM_STATE?.authority?.p0 === true,
          agentSafetyGpu: window.AGENT_SAFETY_PROGRAM_STATE?.authority?.gpu === true,
          agentSafetyMetadata: window.AGENT_SAFETY_PROGRAM_STATE?.runtime?.official_metadata_connectivity || '',
          agentSafetyMetadataTransport: window.AGENT_SAFETY_PROGRAM_STATE?.runtime?.official_metadata_transport || '',
          agentSafetyReceiptClass: window.AGENT_SAFETY_PROGRAM_STATE?.runtime?.provenance_receipt_class || '',
          agentSafetyBudget: window.AGENT_SAFETY_PROGRAM_STATE?.canonical_protocol?.execution_invariants?.budget || {},
          agentSafetySplit: window.AGENT_SAFETY_PROGRAM_STATE?.canonical_protocol?.execution_invariants?.probe_split || {},
          text: document.body.textContent || ''
        };""")
        require(system["chapters"] == 10 and system["readerChapters"] == 0 and system["readerPhases"] == 9 and system["deepDives"] == 4 and system["authorityCards"] == 3 and system["terminationAuthorityCards"] == 4, f"research-system 21-stage chapter framework is incomplete or the retired duplicate roadmap leaked back in: chapters={system['chapters']} roadmap={system['readerChapters']} phases={system['readerPhases']} deep={system['deepDives']} authority={system['authorityCards']} termination-authority={system['terminationAuthorityCards']}")
        require(system["agentSafetySummary"] == 1 and system["agentSafetyStage"] == "CURRENT_SAFETY_SUPPORT_STOP" and system["agentSafetyRuntimeStatus"] == "READY_RUNTIME_MODEL_ASSETS_PINNED" and system["agentSafetyBoundedEvidence"] is False and system["agentSafetyQualification"] is False and system["agentSafetyOverallExecution"] is False and system["agentSafetyQualificationStatus"] == "STOP_SUPPORT_ZERO_CURRENTLY_SAFE_FROZEN_STATES" and system["agentSafetyQualifiedStates"] == 0 and system["agentSafetyPrincipleDeadEnd"] is False and system["agentSafetyHeldoutFuture"] is False and system["agentSafetyP0"] is False and system["agentSafetyGpu"] is False, f"research-system Agent Safety support-stop state drift: {system['agentSafetySummary']}/{system['agentSafetyStage']}/{system['agentSafetyRuntimeStatus']}/{system['agentSafetyBoundedEvidence']}/{system['agentSafetyQualification']}/{system['agentSafetyOverallExecution']}/{system['agentSafetyQualificationStatus']}/{system['agentSafetyQualifiedStates']}/{system['agentSafetyPrincipleDeadEnd']}")
        sab=system["agentSafetyBudget"]; sas=system["agentSafetySplit"]
        require((sab.get("states"),sab.get("history_strata"),sas.get("qualification_count"),sas.get("heldout_count"),sab.get("total_model_evaluations_upper_bound"),sab.get("contract_max_model_calls")) == (4,2,3,8,240,256) and sas.get("disjoint") is True, f"research-system Agent Safety canonical harness-v2 drift: {sab}/{sas}")
        require(system["agentSafetyMetadata"] == "VERIFIED" and system["agentSafetyMetadataTransport"] == "GITHUB_ACTIONS_LITERAL_HF_CAPTURE" and system["agentSafetyReceiptClass"] == "NON_AUTHORITATIVE_CACHE_CONTENT_CHECK" and "SUPPORT STOP" in system["text"].upper() and ("当前实验实现不能支持公平因果比较" in system["text"] or "does not satisfy the prerequisite of reliably producing currently safe states" in system["text"]), f"research-system Agent Safety provenance/support-stop reader boundary drift: {system['agentSafetyMetadata']}/{system['agentSafetyMetadataTransport']}/{system['agentSafetyReceiptClass']}")
        require(system["responsibilityLayers"] == 6 and system["temporalStages"] == 21 and system["componentLayerHeaders"] == 6 and system["aiCheckpoints"] == 5, f"research-system architecture/AI clinic is incomplete: layers={system['responsibilityLayers']} stages={system['temporalStages']} component-groups={system['componentLayerHeaders']} ai={system['aiCheckpoints']}")
        require((system["architectureSummary"].get("temporal_stages"),system["architectureSummary"].get("reader_chapters"),system["architectureSummary"].get("reader_stage_coverage"),system["architectureSummary"].get("reader_stage_missing"),system["architectureSummary"].get("reader_stage_duplicates"),system["architectureSummary"].get("reader_stage_extra"),system["architectureSummary"].get("functional_layers"),system["architectureSummary"].get("assigned_components"),system["architectureSummary"].get("unassigned_components"),system["architectureSummary"].get("cross_cutting_controls"),system["architectureSummary"].get("orphan_cross_cutting_controls")) == (21,10,21,0,0,0,6,32,0,3,0), f"backend architecture manifest is stale in browser state: {system['architectureSummary']}")
        require(system["methodologyControls"] == 3 and "Are candidate problems too similar?" in system["text"] and "Can another person rerun the key result from scratch?" in system["text"], f"cross-cutting methodology controls are missing: {system['methodologyControls']}")
        require(system["outerGates"] == 8 and system["preflightGates"] == 10 and system["quantWorksheets"] == 2, f"Pre-Experiment/identifiability compiler is incomplete: {system['outerGates']}/{system['preflightGates']}/{system['quantWorksheets']}")
        require(system["lessons"] == 6 and system["failureLayers"] == 7 and system["repairLoops"] == 1, f"learning/diagnosis visualization is incomplete: {system['lessons']}/{system['failureLayers']}/{system['repairLoops']}")
        require(system["components"] >= 27, f"expected the current backend responsibility set including Paper-first contract, capability registry, literature audit, Principle, Protocol Validity, Meta-Trace, failure memory, scheduler, replay, Economy, and AI consultation, got {system['components']}")
        require(system["ideaCards"] == 0, f"system-overview must not render current idea/status panels, got {system['ideaCards']}")
        require(set(system["stopClasses"]) == {"REALIZATION_STOP","SUPPORT_STOP","PROTOCOL_STOP","PRINCIPLE_STOP"} and system["stopClasses"]["PRINCIPLE_STOP"].get("persistent_dead_end_authority") is True and all(system["stopClasses"][key].get("persistent_dead_end_authority") is False for key in ("REALIZATION_STOP","SUPPORT_STOP","PROTOCOL_STOP")), f"system-overview STOP taxonomy is stale: {system['stopClasses']}")
        require(all(marker in system["text"] for marker in ("REALIZATION_STOP","SUPPORT_STOP","PROTOCOL_STOP","PRINCIPLE_STOP")), "system-overview must render all four STOP classes explicitly")
        require(all(marker in system["text"] for marker in ("TERMINATION & MEMORY AUTHORITY", "Current canonical state outranks every historical snapshot", "Exact-reduction closure cannot be revived by repeating the same experiment", "Closing one idea never auto-promotes the next idea", "scheduling may inherit priority · scientific PASS never inherits")), "system-overview termination/memory authority lessons are missing")
        ensure_language("zh")
        zh_system_text = execute(session_id, "return document.body.textContent || ''")
        zh_authority_markers = ("终止结论、搜索记忆和历史 快照 必须分层读取", "当前 正式 状态优先于所有历史 快照", "Exact reduction 终止不能靠重复实验复活", "关闭一个 研究方向 不会让下一个 研究方向 自动晋级", "调度可以继承 · 科学 PASS 不能继承")
        missing_zh_authority = [marker for marker in zh_authority_markers if marker not in zh_system_text]
        require(not missing_zh_authority, f"system-overview Chinese termination/memory authority copy is missing: {missing_zh_authority}; lang={execute(session_id, 'return document.documentElement.lang || \'\'')}")
        ensure_language("en")
        stri=system["assetFirstSTRI"] or {};stri_summary=stri.get("summary") or {};stri_authority=stri.get("authority") or {};canonical_queue_summary=(system["problemQueue"] or {}).get("summary") or {}
        require(stri.get("status")=="READY_NARROW_ICLR" and stri.get("submission_status")=="READY_TO_SUBMIT_PENDING_HUMAN_AUTHOR_SIGNOFF_AND_OPENREVIEW" and stri_summary.get("paper_ready")==1 and stri_summary.get("paper_quality_v2_passed")==1 and stri_summary.get("paper_quality_content_addressed_completion")==1 and stri_summary.get("paper_quality_content_addressed_files")==29 and stri_summary.get("paper_quality_evidence_debt")==0 and stri_summary.get("paper_quality_main_visualizations")==4 and "failure" in (stri_summary.get("paper_quality_main_visual_roles") or []) and (stri_summary.get("paper_quality_missing_ids") or [])==[] and (stri_summary.get("claims_supported"),stri_summary.get("claims_total"))==(3,3) and int(stri_summary.get("qa_checks_total") or 0)>0 and stri_summary.get("qa_checks_passed")==stri_summary.get("qa_checks_total") and int(stri_summary.get("official_qa_checks_total") or 0)>0 and stri_summary.get("official_qa_checks_passed")==stri_summary.get("official_qa_checks_total") and (stri_summary.get("main_text_pages"),stri_summary.get("main_text_page_limit"))==(9,9) and stri_summary.get("supplement_ready")==1 and stri_summary.get("supplement_unit_tests")=="29/29 PASS" and stri_summary.get("human_signoff_pending")==1 and int(stri_summary.get("new_gpu_evidence_required") or 0)==0, f"asset-first STRI Paper Quality v2 ready projection is stale: {stri}")
        require(stri.get("scientific_authority") is False and all(value is False for value in stri_authority.values()) and int(stri_summary.get("canonical_problem_gate_pass_added") or 0)==0 and int(stri_summary.get("canonical_generator_candidates_added") or 0)==0 and int(stri_summary.get("canonical_queue_candidates_added") or 0)==0, f"asset-first STRI leaked canonical/execution authority: {stri}")
        visual=system["paperVisualPortfolio"] or {};visual_summary=visual.get("summary") or {}
        require(visual.get("status")=="VISUAL_EVIDENCE_PORTFOLIO_READY" and visual_summary.get("paper_first_designs")==4 and visual_summary.get("planned_main_visualizations")==16 and visual_summary.get("planned_main_visualizations_per_paper_min")==4 and visual_summary.get("stri_completed_main_visualizations")==4 and visual_summary.get("repair_required")==0 and visual.get("scientific_authority") is False and all(value is False for value in (visual.get("authority") or {}).values()), f"Paper Visual Evidence Portfolio is stale: {visual}")
        require(set(system["striDownloads"]) == {"downloads/STRI-ICLR2027.tex", "downloads/STRI-ICLR2027.pdf", "downloads/STRI-ICLR2027-source.zip"}, f"asset-first STRI download links are missing/stale: {system['striDownloads']}")
        stri_content_text=f"content-addressed=PASS ({int(stri_summary.get('paper_quality_content_addressed_files') or 0)} files)"
        stri_qa_text=f"{int(stri_summary.get('qa_checks_passed') or 0)}/{int(stri_summary.get('qa_checks_total') or 0)} PASS"
        stri_official_qa_text=f"{int(stri_summary.get('official_qa_checks_passed') or 0)}/{int(stri_summary.get('official_qa_checks_total') or 0)} PASS"
        require("ASSET-FIRST ICLR 2027 · PAPER QUALITY V2.1" in system["text"] and "Paper Quality v2.1" in system["text"] and stri_content_text in system["text"] and stri_qa_text in system["text"] and stri_official_qa_text in system["text"] and "main=9/9 pages" in system["text"] and f"tests={stri_summary.get('supplement_unit_tests')}" in system["text"] and f"Problem-Gate PASS={int(canonical_queue_summary.get('passed_problem_gate') or 0)}" in system["text"], "asset-first STRI Paper Quality v2/canonical dual-track status is not rendered")
        primary = system["primaryEvidence"]
        generator = system["problemGenerator"]
        require(primary.get("status") == "READY" and (primary.get("policy") or {}).get("empirical_fact_extraction_version") == "precision-v2" and (primary.get("policy") or {}).get("empirical_fact_precision_gate") is True, f"browser primary-evidence precision state is stale: {primary}")
        require((primary.get("policy") or {}).get("scientific_object_lanes") == ["skill_harness","memory_continual","world_model","parametric_model_state"] and (primary.get("policy") or {}).get("source_coverage_exploration_prefers_scientific_objects") is True and (primary.get("policy") or {}).get("new_object_lanes_require_shadow_primary_support_and_collision_gate") is True and (primary.get("policy") or {}).get("context_and_property_tags_have_zero_scientific_authority") is True, f"browser scientific-object policy is stale: {primary.get('policy')}")
        if (primary.get("summary") or {}).get("source_coverage_exhausted") is True: require(int((primary.get("summary") or {}).get("reviewed_object_linked_sources") or 0) == int((primary.get("summary") or {}).get("eligible_object_linked_sources") or 0) and int((primary.get("summary") or {}).get("unreviewed_object_linked_sources") or 0) == 0, f"object coverage is not exhausted consistently: {primary.get('summary')}")
        require(sum(int(v or 0) for v in ((primary.get("summary") or {}).get("empirical_fact_tier_counts") or {}).values()) == int((primary.get("summary") or {}).get("empirical_fact_candidates") or 0), f"browser fact-tier accounting is stale: {primary.get('summary')}")
        if str(primary.get("schema_version") or "0") >= "1.1":
            carrier=primary.get("carrier_probe") or {};policy=primary.get("policy") or {};summary=primary.get("summary") or {};allowed=set(policy.get("scientific_object_lanes") or [])
            require(policy.get("no_lane_carrier_probe_enabled") is True and policy.get("no_lane_carrier_probe_is_existing_object_rescue_only") is True and policy.get("no_lane_carrier_probe_cannot_create_new_object") is True and policy.get("no_lane_carrier_probe_has_zero_scientific_authority") is True and policy.get("no_lane_carrier_probe_failure_prevents_coverage_exhaustion") is True and policy.get("carrier_probe_pending_skips_live_generator_call") is True, f"browser carrier-probe policy is stale: {policy}")
            require(carrier.get("scientific_authority") is False and int(carrier.get("pending") or 0)==int(summary.get("carrier_probe_pending") or 0) and bool(carrier.get("complete"))==bool(summary.get("carrier_probe_complete")), f"browser carrier-probe accounting is stale: {carrier} / {summary}")
            require(not (summary.get("source_coverage_exhausted") is True and int(summary.get("carrier_probe_pending") or 0)>0), f"browser source coverage exhausted with carrier backlog: {summary}")
            require(all(row.get("scientific_authority") is False and len(str(row.get("primary_sha256") or ""))==64 and (((str(row.get("probe_outcome") or "")=="SCOPE_EXCLUDED_BY_PRIMARY") and not str(row.get("fulltext_sha256") or "") and not (row.get("live_rescue_eligible_lanes") or [])) or len(str(row.get("fulltext_sha256") or ""))==64) and all(str(value) in allowed for value in row.get("live_rescue_eligible_lanes") or []) for row in carrier.get("portable_receipts") or []), f"browser carrier receipts are invalid: {carrier.get('portable_receipts')}")
        require((generator.get("policy") or {}).get("zero_candidate_rationale_required") is True and (generator.get("policy") or {}).get("discovery_saturation_memory_has_zero_scientific_authority") is True and (generator.get("saturation_memory") or {}).get("scientific_authority") is False, f"browser saturation-memory authority state is stale: {generator}")
        if generator.get("status") == "GENERATED_ZERO_CANDIDATES": require(bool(str(generator.get("generation_notes") or "").strip()), "zero-candidate rationale missing from browser state")
        if generator.get("status") == "SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE":
            coverage=generator.get("source_coverage") or {};policy=generator.get("policy") or {};summary=generator.get("summary") or {}
            require(policy.get("incomplete_retrieval_without_new_lane_source_skips_model_call") is True and policy.get("retrieval_incomplete_is_compute_control_not_scientific_negative") is True and coverage.get("source_retrieval_complete") is False and coverage.get("coverage_exhausted") is not True and int(coverage.get("unreviewed_lane_linked_sources") or 0)==0, f"browser retrieval-incomplete generator state is invalid: {generator}")
            require(all(int(summary.get(key) or 0)==0 for key in ("generated","written_to_auto_inbox","semantic_clear","semantic_blocked")), f"browser retrieval-incomplete generator contains generated/reviewed candidates: {summary}")
        if generator.get("status") == "SKIPPED_SOURCE_CARRIER_PROBE_PENDING":
            coverage=generator.get("source_coverage") or {};policy=generator.get("policy") or {};summary=generator.get("summary") or {}
            require(policy.get("carrier_probe_pending_skips_model_call") is True and policy.get("carrier_probe_pending_is_compute_control_not_scientific_negative") is True and coverage.get("coverage_exhausted") is not True and coverage.get("carrier_probe_required") is True and int(coverage.get("carrier_probe_pending") or 0)>0 and coverage.get("carrier_probe_complete") is False and int(coverage.get("unreviewed_lane_linked_sources") or 0)==0, f"browser carrier-pending generator state is invalid: {generator}")
            require(all(int(summary.get(key) or 0)==0 for key in ("generated","written_to_auto_inbox","semantic_clear","semantic_blocked")), f"browser carrier-pending generator contains generated/reviewed candidates: {summary}")
        require("SATURATION / DEAD-END MEMORY" in system["text"] and "precision-v2" in system["text"], "problem-discovery precision/saturation controls are not rendered")
        require("SCIENTIFIC OBJECT AXIS" in system["text"] and "world_model" in system["text"] and "parametric_model_state" in system["text"] and "object-grounded reviewed=" in system["text"], "scientific-object discovery axis is not rendered")
        require("OBJECT RETRIEVAL GAP AUDIT" in system["text"] and "activation=0" in system["text"], "scientific-object retrieval-gap shadow audit is not rendered")
        require("OBJECT CANDIDATE PRIMARY VERIFY" in system["text"] and "primary-verified=" in system["text"], "scientific-object candidate primary verification is not rendered")
        shadow_system_admission=system["shadowSearchAdmission"] or {};shadow_system_summary=shadow_system_admission.get("summary") or {}
        expected_shadow_admission=expected_state.get("paper_first_shadow_search_admission") or {};expected_shadow_admission_summary=expected_shadow_admission.get("summary") or {}
        require(shadow_system_admission.get("scientific_authority") is False and int(shadow_system_summary.get("automatic_provider_calls_authorized") or 0)==0 and "SHADOW RUN ADMISSION" in system["text"], f"system overview shadow-run admission authority/accounting is invalid: {shadow_system_admission}")
        require(shadow_system_admission.get("status")==expected_shadow_admission.get("status") and all(shadow_system_summary.get(key)==expected_shadow_admission_summary.get(key) for key in ("canonical_transaction_closed","same_source_transaction","same_discovery_operator_version","operator_upgrade_recompile","qualification_allowed","automatic_provider_calls_authorized")), f"system overview shadow-run admission diverges from generated research-system state: rendered={shadow_system_admission} expected={expected_shadow_admission}")
        if shadow_system_summary.get("qualification_allowed") is True:
            require(str(shadow_system_admission.get("status") or "").startswith("READY_FOR_") and (shadow_system_summary.get("same_source_transaction") is False or shadow_system_summary.get("operator_upgrade_recompile") is True), f"qualification may open only for a new source transaction or operator upgrade: {shadow_system_admission}")
        if shadow_system_admission.get("status") == "SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL":
            require(shadow_system_summary.get("same_source_transaction") is True and shadow_system_summary.get("same_discovery_operator_version") is True and shadow_system_summary.get("qualification_allowed") is False, f"same-source current-operator terminal shadow must zero-call skip: {shadow_system_admission}")
        shadow_frontier=system["shadowContinuationFrontier"] or {};shadow_frontier_summary=shadow_frontier.get("summary") or {};shadow_frontier_policy=shadow_frontier.get("policy") or {}
        if shadow_frontier:
            require(shadow_frontier.get("scientific_authority") is False and shadow_frontier_policy.get("frontier_is_deterministic_control_projection_only") is True and shadow_frontier_policy.get("frontier_cannot_create_shadow_run") is True and shadow_frontier_policy.get("frontier_cannot_call_model_provider") is True and shadow_frontier_policy.get("frontier_cannot_qualify_support") is True and shadow_frontier_policy.get("frontier_cannot_reopen_generator_or_problem_gate") is True and shadow_frontier_policy.get("frontier_cannot_authorize_method_experiment_p0_gpu") is True and int(shadow_frontier_summary.get("active_control_actions") or 0)==int(str(shadow_frontier.get("status") or "").startswith("READY_FOR_")) and int(shadow_frontier_summary.get("automatic_provider_calls_authorized") or 0)==0 and "SHADOW CONTINUATION FRONTIER" in system["text"] and "external-wait=" in system["text"] and "support-handoff=" in system["text"], f"shadow continuation frontier authority/accounting is invalid: {shadow_frontier}")
        release_watch=system["supportReleaseWatch"] or {};release_summary=release_watch.get("summary") or {};release_policy=release_watch.get("policy") or {}
        if release_watch.get("status") and release_watch.get("status") != "NOT_RUN":
            require(release_watch.get("scientific_authority") is False and release_policy.get("primary_declared_or_support_audited_release_endpoints_only") is True and release_policy.get("support_audited_pre_f0_repository_targets_allowed") is True and release_policy.get("pre_f0_release_change_only_holds_included") is True and release_policy.get("related_work_repository_links_are_not_watch_targets") is True and release_policy.get("release_watch_cannot_mark_support_qualified") is True and release_policy.get("release_watch_cannot_reopen_generator_or_problem_gate") is True and int(release_summary.get("support_qualified") or 0)==0 and int(release_summary.get("generator_reopen_authorized") or 0)==0 and int(release_summary.get("problem_gate_authorized") or 0)==0, f"support release watch authority boundary is invalid: {release_watch}")
            if "primary_declaration_refresh_checked" in release_summary:
                require(release_policy.get("no_endpoint_primary_refresh_is_primary_source_only") is True and release_policy.get("primary_declaration_refresh_has_zero_source_exposure_effect") is True and release_policy.get("primary_declaration_refresh_cannot_qualify_support") is True and int(release_summary.get("primary_declaration_refresh_changed") or 0) >= 0 and int(release_summary.get("primary_declaration_refresh_rate_limited") or 0) >= 0, f"support release primary-refresh boundary is invalid: {release_watch}")
                require("primary-refresh checked/changed=" in system["text"], "support release primary-refresh counts are not rendered")
            require("SUPPORT RELEASE WATCH" in system["text"] and "support-qualified=0" in system["text"], "support release watch is not rendered as recheck-only zero authority")
        asset_queue=system["supportAssetRecheck"] or {};asset_summary=asset_queue.get("summary") or {};asset_policy=asset_queue.get("policy") or {}
        asset_handoff=system["supportAssetHandoff"] or {};handoff_summary=asset_handoff.get("summary") or {};handoff_policy=asset_handoff.get("policy") or {}
        if asset_queue.get("status") and asset_queue.get("status") != "NOT_RUN":
            require(asset_queue.get("scientific_authority") is False and asset_policy.get("release_change_only_creates_asset_recheck_task") is True and asset_policy.get("queue_is_durable_across_release_watch_cooldown") is True and asset_policy.get("queue_cannot_mark_support_qualified") is True and asset_policy.get("queue_cannot_reopen_generator_or_problem_gate") is True and asset_policy.get("queue_cannot_authorize_method_experiment_p0_gpu") is True and asset_policy.get("explicit_asset_resolution_required_to_clear_entry") is True and asset_policy.get("automatic_provider_calls_authorized") is False and all(int(asset_summary.get(key) or 0)==0 for key in ("support_qualified","generator_reopen_authorized","problem_gate_authorized","method_authorized","experiment_authorized","p0_authorized","gpu_authorized")), f"support asset recheck queue authority boundary is invalid: {asset_queue}")
            if "resolved" in asset_summary:
                require(asset_policy.get("asset_resolution_must_bind_latest_trigger_digest") is True and asset_policy.get("asset_resolution_cannot_mark_support_qualified_or_reopen") is True and asset_policy.get("support_inventory_recheck_remains_queue_handoff_not_resolution") is True, f"support asset resolution boundary is invalid: {asset_queue}")
                require("resolved=" in system["text"] and "still-unavailable=" in system["text"] and "irrelevant-release=" in system["text"], "support asset resolution counts are not rendered")
            require("SUPPORT ASSET RECHECK QUEUE" in system["text"] and "Generator=0" in system["text"] and "Problem-Gate=0" in system["text"], "support asset recheck queue is not rendered as zero-authority durable task accounting")
        if asset_handoff.get("status") and asset_handoff.get("status") != "NOT_RUN":
            require(asset_handoff.get("scientific_authority") is False and handoff_policy.get("handoff_reuses_existing_problem_falsifier_support_inventory") is True and handoff_policy.get("asset_recheck_cannot_define_a_parallel_support_gate") is True and handoff_policy.get("support_inventory_receipt_required_before_any_support_decision") is True and handoff_policy.get("problem_falsifier_preflight_remains_support_authority_boundary") is True and handoff_policy.get("handoff_cannot_execute_falsifier_automatically") is True and handoff_policy.get("handoff_cannot_reopen_generator_or_problem_gate") is True and handoff_policy.get("automatic_provider_calls_authorized") is False and int(handoff_summary.get("queued_asset_rechecks") or 0)==int(asset_summary.get("queued") or 0) and int(handoff_summary.get("support_inventory_recheck_ready") or 0)+int(handoff_summary.get("provenance_incomplete") or 0)==int(handoff_summary.get("queued_asset_rechecks") or 0), f"support asset handoff boundary is invalid: {asset_handoff}")
            require(all(int(handoff_summary.get(key) or 0)==0 for key in ("automatic_execution_authorized","provider_calls_authorized","support_qualified","falsifier_execution_authorized","generator_reopen_authorized","problem_gate_authorized","method_authorized","experiment_authorized","p0_authorized","gpu_authorized")), f"support asset handoff leaked authority: {asset_handoff}")
            require("SUPPORT INVENTORY HANDOFF" in system["text"] and "provenance-hold=" in system["text"], "support inventory handoff is not rendered as bounded health")
        frontier=system["discoveryFrontier"] or {};frontier_summary=frontier.get("summary") or {};frontier_policy=frontier.get("policy") or {}
        if frontier:
            require(frontier.get("scientific_authority") is False and frontier_policy.get("frontier_is_deterministic_compute_control_only") is True and frontier_policy.get("frontier_does_not_replace_primary_generator_problem_gate_or_relation_controls") is True and frontier_policy.get("frontier_cannot_authorize_model_calls") is True and frontier_policy.get("frontier_cannot_authorize_problem_gate_method_experiment_p0_gpu") is True and frontier_policy.get("wait_external_status_is_not_scientific_exhaustion") is True and frontier_policy.get("trigger_satisfaction_must_reenter_original_control_plane") is True and all(int(frontier_summary.get(key) or 0)==0 for key in ("automatic_model_calls_authorized","automatic_problem_gate_authorized","automatic_method_authorized","automatic_experiment_authorized","automatic_p0_authorized","automatic_gpu_authorized")), f"discovery frontier authority boundary is invalid: {frontier}")
            if frontier.get("status")=="WAIT_EXTERNAL_EVIDENCE_TRIGGERS": require(int(frontier_summary.get("open_internal_frontiers") or 0)==0 and "DISCOVERY FRONTIER" in system["text"] and "WAIT_EXTERNAL_EVIDENCE_TRIGGERS" in system["text"], f"wait-external discovery frontier is not rendered consistently: {frontier}")
        relation_freshness=system["globalRelationFreshness"] or {};relation_summary=relation_freshness.get("summary") or {}
        if relation_freshness.get("status") == "STALE_RELATION_UNIVERSE":
            require(relation_freshness.get("scientific_authority") is False and relation_summary.get("universe_stale") is True and relation_summary.get("current_not_reduced_unknown") is True and relation_summary.get("model_scan_deferred") is True and relation_summary.get("focused_problem_generator_reopen_allowed") is False and str(relation_freshness.get("current_relation_universe_digest") or "") != str(relation_freshness.get("last_scanned_relation_universe_digest") or ""), f"stale relation-universe boundary is invalid: {relation_freshness}")
            require("STALE_RELATION_UNIVERSE" in system["text"] and "current UNKNOWN" in system["text"] and "model-scan=DEFERRED" in system["text"], "stale relation-universe interpretation is not rendered")
        relation_delta=system["globalRelationDelta"] or {};delta_summary=relation_delta.get("summary") or {};delta_policy=relation_delta.get("policy") or {}
        if relation_delta.get("status") == "RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE":
            require(relation_delta.get("scientific_authority") is False and delta_policy.get("deterministic_typed_evidence_delta_only") is True and delta_policy.get("pair_slots_are_not_lane_valid_pairs") is True and delta_policy.get("cannot_reopen_generator") is True and delta_policy.get("cannot_authorize_relation_model_scan") is True and delta_summary.get("model_scan_authorized") is False and delta_summary.get("focused_generator_reopen_authorized") is False, f"relation delta preflight authority boundary is invalid: {relation_delta}")
            require("RELATION DELTA PREFLIGHT" in system["text"] and "combinatorial search upper bounds" in system["text"], "relation delta preflight is not rendered as non-authoritative opportunity accounting")
        relation_admission=system["globalRelationAdmission"] or {};admission_summary=relation_admission.get("summary") or {};admission_policy=relation_admission.get("policy") or {}
        if relation_admission:
            require(relation_admission.get("scientific_authority") is False and admission_policy.get("automatic_model_scan_authority") is False and admission_policy.get("manual_execution_requires_explicit_operator_flag") is True and admission_policy.get("manual_eligibility_is_not_scientific_authority") is True and admission_policy.get("relation_scan_cannot_authorize_problem_gate") is True and admission_policy.get("relation_scan_cannot_authorize_method_experiment_p0_gpu") is True and admission_summary.get("automatic_model_scan_authorized") is False, f"manual relation scan admission authority boundary is invalid: {relation_admission}")
            require("MANUAL RELATION SCAN ADMISSION" in system["text"] and "automatic-model-authority=NO" in system["text"], "manual relation scan admission is not rendered as explicit-manual-only")
        require("NO-LANE CARRIER PROBE" in system["text"] and "SHADOW SEARCH LAB" in system["text"] and "live-lanes=4" in system["text"] and "shadow-primitives=10" in system["text"] and "GLOBAL RELATION RECALL" in system["text"] and "canonical durable backlog" in system["text"].lower() and any(marker in system["text"] for marker in ("v2.9 · MACHINE-ENFORCED","v3.0 · MACHINE-ENFORCED","v3.1 · MACHINE-ENFORCED","v3.2 · MACHINE-ENFORCED","v3.3 · MACHINE-ENFORCED","v3.4 · MACHINE-ENFORCED","v3.5 · MACHINE-ENFORCED","v3.6 · MACHINE-ENFORCED","v3.7 · MACHINE-ENFORCED","v3.8 · MACHINE-ENFORCED","v3.9 · MACHINE-ENFORCED","v4.0 · MACHINE-ENFORCED","v4.1 · MACHINE-ENFORCED","v4.2 · MACHINE-ENFORCED","v4.3 · MACHINE-ENFORCED")), "problem-discovery carrier/live/shadow/relation authority boundary is not rendered")
        require((system["preSummary"].get("audited"), system["preSummary"].get("execution_ready"), system["preSummary"].get("blocked")) == (4,0,4), f"Pre-P0 retrospective state is wrong: {system['preSummary']}")
        iteration = system["iterationSummary"]
        infra_only = iteration.get("diagnosis_counts") == {"infrastructure-error": 4}
        require(iteration.get("scale_up_allowed") == 0 and (iteration.get("belief_updates_allowed") == 1 or (iteration.get("belief_updates_allowed") == 0 and infra_only)), f"experiment-diagnosis state is wrong: {iteration}")
        require("Main ICLR idea bank" not in system["text"] and "Final advisor gate" not in system["text"] and "主 ICLR Idea Bank" not in system["text"] and "最终师兄讨论门槛" not in system["text"], "current idea portfolio leaked back into the research-system page")
        execute(session_id, "document.querySelector('.language-toggle')?.click();")
        time.sleep(1)
        zh = execute(session_id, "return {text:document.body.textContent||'', outer:document.querySelectorAll('.preflight-outer-gate').length, gates:document.querySelectorAll('.preflight-gate').length, failures:document.querySelectorAll('.system-failure-layer').length};")
        require(zh["outer"] == 8 and zh["gates"] == 10 and zh["failures"] == 7 and "先用便宜检查决定值不值得上 GPU" in zh["text"] and "先证明评测协议真的在测我们声称的能力" in zh["text"] and "让系统记住为什么成功、为什么失败" in zh["text"] and "先写清为什么应该有效" in zh["text"], "research-system plain-language Economy / Principle / Protocol / learning-loop explanation is incomplete")
        request("POST", f"/session/{session_id}/window/rect", {"width": 390, "height": 844})
        time.sleep(1)
        system_mobile = execute(session_id, """const gate=document.querySelector('.preflight-gate-grid'); const failure=document.querySelector('.system-failure-layers'); return {inner:window.innerWidth,scroll:document.documentElement.scrollWidth,gateCols:gate?getComputedStyle(gate).gridTemplateColumns:'',failureCols:failure?getComputedStyle(failure).gridTemplateColumns:'',maxCard:Math.max(0,...[...document.querySelectorAll('.preflight-gate,.system-failure-layer,.methodology-control-card')].map(x=>x.getBoundingClientRect().width))};""")
        require(system_mobile["scroll"] <= system_mobile["inner"] + 2, f"research-system mobile layout has page-level horizontal overflow: {system_mobile}")
        require(" " not in system_mobile["gateCols"].strip() and " " not in system_mobile["failureCols"].strip(), f"Pre-P0/failure grids must collapse to one column on mobile: {system_mobile}")
        require(system_mobile["maxCard"] <= system_mobile["inner"], f"research-system cards exceed mobile viewport: {system_mobile}")
        request("POST", f"/session/{session_id}/window/rect", {"width": 1440, "height": 1000})
        time.sleep(1)

        # System Overview is intentionally a very heavy 21-stage audit surface.
        # Start a fresh browser session before the Timeline/Portfolio suite so
        # the second half measures those pages rather than retained system-page
        # DOM/JS pressure inside a single long-lived Firefox content process.
        request("DELETE", f"/session/{session_id}")
        session_id = request("POST", "/session", capabilities)["value"]["sessionId"]
        request("POST", f"/session/{session_id}/window/rect", {"width": 1440, "height": 1000})

        navigate("/research-timeline.html", 3)
        timeline = execute(session_id, """return {
          title: document.querySelector('h1')?.textContent?.trim() || '',
          monthTables: document.querySelectorAll('.rt-month-table').length,
          heatMonths: document.querySelectorAll('.rt-heat-month').length,
          sourceMonths: new Set((window.RESEARCH_TIMELINE?.events || []).map(e => new Intl.DateTimeFormat('en-US',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit'}).format(new Date(e.occurred_at)))).size,
          firstHeatMonth: document.querySelector('.rt-heat-month')?.dataset?.rtHeatMonth || '',
          lastHeatMonth: [...document.querySelectorAll('.rt-heat-month')].at(-1)?.dataset?.rtHeatMonth || '',
          dayGroups: document.querySelectorAll('.rt-day-row').length,
          openDays: document.querySelectorAll('.rt-day-detail-row:not([hidden])').length,
          eventRows: document.querySelectorAll('.rt-event').length,
          visibleCount: Number(document.querySelector('.rt-hero-kpis span:first-child b')?.textContent || 0),
          summary: window.RESEARCH_TIMELINE?.summary || {},
          timezone: window.RESEARCH_TIMELINE?.projection_policy?.display_timezone || '',
          descActive: document.querySelector('[data-rt-order="desc"]')?.classList.contains('active') === true,
          firstMonth: document.querySelector('.rt-month')?.dataset?.rtMonth || '',
          lastMonth: [...document.querySelectorAll('.rt-month')].at(-1)?.dataset?.rtMonth || '',
          firstDay: document.querySelector('.rt-day-row')?.id?.replace('timeline-', '') || '',
          lastDay: [...document.querySelectorAll('.rt-day-row')].at(-1)?.id?.replace('timeline-', '') || '',
          legendItems: document.querySelectorAll('.rt-legend-item[data-rt-legend]').length,
          legendBackgrounds: new Set([...document.querySelectorAll('.rt-legend-item[data-rt-legend]')].map(x => getComputedStyle(x).backgroundColor)).size,
          heroAccent: getComputedStyle(document.querySelector('.rt-hero'),'::before').backgroundImage || '',
          oldTopLayers: document.querySelectorAll('.lead,.callout,.rt-overview,.rt-stats').length,
          heatPairTop: [...document.querySelectorAll('.rt-heat-month')].slice(0,2).map(x=>Math.round(x.getBoundingClientRect().top)),
          monthTops: [...document.querySelectorAll('.rt-month')].slice(0,2).map(x=>Math.round(x.getBoundingClientRect().top)),
          monthLefts: [...document.querySelectorAll('.rt-month')].slice(0,2).map(x=>Math.round(x.getBoundingClientRect().left)),
          heatBottom: Math.round(document.querySelector('#research-timeline-heatmap')?.getBoundingClientRect().bottom || 0),
          controlsTop: Math.round(document.querySelector('#research-timeline-controls')?.getBoundingClientRect().top || 0),
          controlsHeight: Math.round(document.querySelector('.rt-controls')?.getBoundingClientRect().height || 0),
          aug21WeekLabel: document.querySelector('#timeline-2026-08-21 .rt-table-date b')?.textContent?.trim() || '',
          aug21DateLabel: document.querySelector('#timeline-2026-08-21 .rt-table-date small')?.textContent?.trim() || '',
          jul28WeekLabel: document.querySelector('#timeline-2026-07-28 .rt-table-date b')?.textContent?.trim() || '',
          aug21HeatActivity: document.querySelector('.rt-heat-cell[data-rt-day="2026-08-21"] .rt-heat-activity')?.textContent?.replace(/\\s+/g,'').trim() || '',
          heatCellDisplay: getComputedStyle(document.querySelector('.rt-heat-cell[data-rt-day="2026-08-21"]')).display || '',
          visibleTimezoneChrome: [...document.querySelectorAll('.rt-hero,.rt-heat-month-header,.rt-month-header,.sidebar-note,.rt-policy-note,.counter')].map(x=>x.textContent||'').join(' '),
          aug21Thread: document.querySelector('#timeline-2026-08-21 .rt-table-thread p')?.textContent?.trim() || '',
          aug21Workload: document.querySelector('#timeline-2026-08-21 .rt-table-workload')?.textContent?.trim() || '',
          threadClamp: getComputedStyle(document.querySelector('#timeline-2026-08-21 .rt-table-thread p')).webkitLineClamp || '',
          topWeeklyBlock: document.querySelectorAll('#research-timeline-weekly,.rt-weekly').length,
          weekRows: document.querySelectorAll('.rt-week-summary-row').length,
          weekLabels: [...document.querySelectorAll('.rt-week-inline header>div:first-child b')].map(x=>x.textContent.trim()),
          latestWeekSummary: document.querySelector('.rt-week-inline p')?.textContent?.trim() || '',
          week4AfterAug17: document.querySelector('#timeline-2026-08-17')?.nextElementSibling?.nextElementSibling?.dataset?.rtWeekSummary || '',
          nextDayAfterWeek4: document.querySelector('#timeline-2026-08-17')?.nextElementSibling?.nextElementSibling?.nextElementSibling?.id || '',
          week1AfterJul28: document.querySelector('#timeline-2026-07-28')?.nextElementSibling?.nextElementSibling?.dataset?.rtWeekSummary || '',
          ideaLegend: document.querySelector('.rt-legend-idea')?.textContent?.trim() || '',
          searchPlaceholder: document.querySelector('#site-search')?.getAttribute('placeholder') || '',
          zhText: document.body.textContent || ''
        };""")
        require(timeline["title"] == "研究时间轴", f"timeline must default to its Chinese page title: {timeline}")
        require(timeline["monthTables"] == timeline["heatMonths"] == timeline["sourceMonths"] and timeline["monthTables"] >= 2 and timeline["firstHeatMonth"] >= timeline["lastHeatMonth"] and timeline["dayGroups"] >= 20 and timeline["openDays"] == 0, f"timeline must render one workload calendar and one collapsed table per month: {timeline}")
        require(timeline["eventRows"] == 0 and timeline["visibleCount"] == int(timeline["summary"].get("events") or 0) and timeline["visibleCount"] >= 756, f"timeline must account for the full projection while lazily avoiding hundreds of collapsed event cards at first paint: {timeline}")
        require(timeline["timezone"] == "Asia/Shanghai" and timeline["descActive"] and timeline["firstHeatMonth"] == "2026-08" and timeline["lastHeatMonth"] == "2026-07" and timeline["firstMonth"] == "2026-08" and timeline["lastMonth"] == "2026-07" and timeline["firstDay"] >= timeline["lastDay"] and "月度明细表改为单列" in timeline["zhText"] and "本页只是只读历史投影" in timeline["zhText"], f"timeline month-order/newest-first/internal-timezone/authority boundary is incomplete: {timeline}")
        require(timeline["legendItems"] == 7 and timeline["legendBackgrounds"] == 7 and "linear-gradient" in timeline["heroAccent"], f"timeline compact header must reuse all seven semantic colors in its legend and accent: {timeline}")
        require(timeline["oldTopLayers"] == 0 and len(set(timeline["heatPairTop"])) == 1 and timeline["monthTops"][1] > timeline["monthTops"][0] and len(set(timeline["monthLefts"])) == 1 and timeline["controlsTop"] >= timeline["heatBottom"] and timeline["controlsHeight"] <= 64, f"timeline must keep paired calendars but stack monthly detail tables in one column below one-line filters: {timeline}")
        require(timeline["jul28WeekLabel"] == "第1周 · 周二" and timeline["aug21WeekLabel"] == "第4周 · 周五" and timeline["aug21DateLabel"] == "2026-08-21", f"timeline research weeks must run continuously from the first recorded week: {timeline}")
        require("北京时间" not in timeline["visibleTimezoneChrome"] and "UTC+8" not in timeline["visibleTimezoneChrome"] and "Asia/Shanghai" not in timeline["visibleTimezoneChrome"], f"timeline UI must keep timezone handling internal rather than visually emphasizing it: {timeline}")
        require(timeline["aug21HeatActivity"].endswith("次活动") and timeline["heatCellDisplay"] == "grid", f"timeline calendar cells must separate the date from an explicitly labeled activity count: {timeline}")
        aug21_parts = [part.strip() for part in timeline["aug21Thread"].split("→") if part.strip()]
        require(2 <= len(aug21_parts) <= 4 and len(aug21_parts) == len(set(aug21_parts)) and timeline["aug21Workload"] and timeline["threadClamp"] == "3", f"timeline main thread must be slightly richer while staying deduplicated and paired with workload detail: {timeline}")
        require(timeline["topWeeklyBlock"] == 0 and timeline["weekRows"] >= 4 and timeline["weekLabels"][0] == "第4周总结" and timeline["weekLabels"][-1] == "第1周总结" and timeline["week4AfterAug17"] == "4" and timeline["nextDayAfterWeek4"] == "timeline-2026-08-16" and timeline["week1AfterJul28"] == "1", f"timeline weekly summaries must be embedded at week boundaries instead of rendered as a top card grid: {timeline}")
        require(timeline["ideaLegend"] == "研究方向 / 问题发现" and "研究问题" in timeline["searchPlaceholder"] and "Research Memory" not in timeline["latestWeekSummary"], f"timeline Chinese UI should prefer Chinese terminology while preserving technical identifiers only when necessary: {timeline}")
        execute(session_id, "document.querySelector('.rt-day-row')?.click();")
        time.sleep(0.3)
        timeline_expand = execute(session_id, """const row=document.querySelector('.rt-day-row'); const detail=row?.nextElementSibling; return {expanded:row?.getAttribute('aria-expanded')||'',detailVisible:detail?.hidden===false,toggle:row?.querySelector('.rt-day-toggle')?.textContent||'',loaded:detail?.querySelectorAll('.rt-event').length||0,rendered:detail?.querySelector('.rt-day-events')?.dataset?.rendered||''};""")
        require(timeline_expand["expanded"] == "true" and timeline_expand["detailVisible"] is True and timeline_expand["toggle"] == "−" and timeline_expand["loaded"] > 0 and timeline_expand["rendered"] == "1", f"timeline day row must lazily render and expand its chronological detail row: {timeline_expand}")
        request("POST", f"/session/{session_id}/window/rect", {"width": 390, "height": 844})
        time.sleep(0.5)
        timeline_mobile = execute(session_id, """const wrap=document.querySelector('.rt-month-table-wrap'); return {inner:window.innerWidth,scroll:document.documentElement.scrollWidth,wrapClient:wrap?.clientWidth||0,wrapScroll:wrap?.scrollWidth||0};""")
        require(timeline_mobile["scroll"] <= timeline_mobile["inner"] + 2 and timeline_mobile["wrapScroll"] > timeline_mobile["wrapClient"], f"timeline monthly tables must scroll internally without page-level mobile overflow: {timeline_mobile}")
        request("POST", f"/session/{session_id}/window/rect", {"width": 1440, "height": 1000})
        time.sleep(0.5)

        navigate("/research-timeline.html?research=A-3", 2)
        execute(session_id, "document.querySelector('.rt-day-row')?.click();")
        time.sleep(0.2)
        a3_timeline = execute(session_id, """return {
          selected: document.querySelector('#timeline-research')?.value || '',
          events: [...document.querySelectorAll('.rt-event')].map(x=>x.dataset.canonicalResearch||''),
          chips: [...document.querySelectorAll('.rt-canonical-research b')].map(x=>x.textContent.trim()),
          url: location.search,
          visible: Number(document.querySelector('.rt-hero-kpis span:first-child b')?.textContent || 0)
        };""")
        require(a3_timeline["selected"] == "ri:A-3" and a3_timeline["visible"] >= 1 and a3_timeline["events"] and all("A-3" in value.split() for value in a3_timeline["events"]) and "A-3" in a3_timeline["chips"] and "research=A-3" in a3_timeline["url"], f"timeline must provide a shareable canonical A-3 provenance view: {a3_timeline}")
        navigate("/research-timeline.html?paper=STRI", 2)
        execute(session_id, "document.querySelector('.rt-day-row')?.click();")
        time.sleep(0.2)
        stri_timeline = execute(session_id, """return {
          selected: document.querySelector('#timeline-research')?.value || '',
          events: [...document.querySelectorAll('.rt-event')].map(x=>x.dataset.canonicalPaper||''),
          paperChips: [...document.querySelectorAll('.rt-canonical-paper b')].map(x=>x.textContent.trim()),
          visible: Number(document.querySelector('.rt-hero-kpis span:first-child b')?.textContent || 0)
        };""")
        require(stri_timeline["selected"] == "paper:STRI" and stri_timeline["visible"] >= 1 and stri_timeline["events"] and all("STRI" in value.split() for value in stri_timeline["events"]) and "STRI" in stri_timeline["paperChips"], f"timeline must provide a canonical STRI PaperState provenance view: {stri_timeline}")

        navigate("/research-directions.html", 4)
        directions_bridge = execute(session_id, """return {
          directions: document.querySelectorAll('.direction-card').length,
          bridges: document.querySelectorAll('.direction-current-bridge').length,
          currentLinks: document.querySelectorAll('.direction-current-category').length,
          migrationLinks: document.querySelectorAll('.taxonomy-current-link').length,
          canonicalSummary: window.RESEARCH_ITEM_STATE?.summary || {},
          bridgeText: document.querySelector('.historical-taxonomy-migration')?.textContent || '',
          hrefs: [...document.querySelectorAll('.taxonomy-current-link')].map(x=>x.getAttribute('href')||'')
        };""")
        require(directions_bridge["directions"] == 0 and directions_bridge["bridges"] == 10 and directions_bridge["currentLinks"] == directions_bridge["migrationLinks"] == 21, f"the dense Field Atlas must remove legacy direction cards while preserving all 10 D1-D10 bridge rows and 21 many-to-many canonical A-G links: {directions_bridge}")
        require((directions_bridge["canonicalSummary"].get("portfolio_objects"), (directions_bridge["canonicalSummary"].get("by_category") or {}).get("A",{}).get("portfolio_total"), (directions_bridge["canonicalSummary"].get("by_category") or {}).get("B",{}).get("portfolio_total")) == (expected_research_summary.get("portfolio_objects"), expected_category_totals[0], expected_category_totals[1]) and f"{expected_category_totals[0]} 个对象" in directions_bridge["bridgeText"] and f"{expected_category_totals[1]} 个对象" in directions_bridge["bridgeText"] and any("canonical-group-a" in href for href in directions_bridge["hrefs"]), f"Field Atlas must read current counts from canonical ResearchItemState rather than static labels: {directions_bridge}")

        navigate("/paper-ideas.html", 6)
        ensure_language("zh")
        ideas = execute(session_id, """return {
          chapters: document.querySelectorAll('.page-chapter').length,
          toc2: document.querySelectorAll('.toc-level-2').length,
          toc3: document.querySelectorAll('.toc-level-3').length,
          toc4: document.querySelectorAll('.toc-level-4').length,
          p0Entry: document.querySelectorAll('.p0-entry-panel').length,
          p0Boards: document.querySelectorAll('.p0-control-board').length,
          experimentLinks: [...document.querySelectorAll('a')].filter(x=>(x.getAttribute('href')||'').startsWith('experiments.html')).length,
          p0Summary: window.P0_EXPERIMENT_PLAN?.summary || {},
          p0Policy: window.P0_EXPERIMENT_PLAN?.policy || {},
          p0AdmissionSummary: window.RESEARCH_SYSTEM_STATE?.p0_admission?.summary || {},
          agentSafetyProgram: document.querySelectorAll('#agent-safety-program').length,
          agentSafetyStage: window.AGENT_SAFETY_PROGRAM_STATE?.current_stage || '',
          agentSafetyRuntimeStatus: window.AGENT_SAFETY_PROGRAM_STATE?.runtime?.status || '',
          agentSafetyBoundedEvidence: window.AGENT_SAFETY_PROGRAM_STATE?.authority?.bounded_evidence_acquisition === true,
          agentSafetyQualification: window.AGENT_SAFETY_PROGRAM_STATE?.authority?.qualification_probe_execution === true,
          agentSafetyOverallExecution: window.AGENT_SAFETY_PROGRAM_STATE?.execution_authorized === true,
          agentSafetyQualificationStatus: window.AGENT_SAFETY_PROGRAM_STATE?.qualification?.status || '',
          agentSafetyQualifiedStates: window.AGENT_SAFETY_PROGRAM_STATE?.qualification?.qualified_state_count,
          agentSafetyPrincipleDeadEnd: window.AGENT_SAFETY_PROGRAM_STATE?.qualification?.principle_dead_end_certified === true,
          agentSafetyHeldoutFuture: window.AGENT_SAFETY_PROGRAM_STATE?.authority?.heldout_future_probe_execution === true,
          agentSafetyP0: window.AGENT_SAFETY_PROGRAM_STATE?.authority?.p0 === true,
          agentSafetyGpu: window.AGENT_SAFETY_PROGRAM_STATE?.authority?.gpu === true,
          agentSafetyMetadata: window.AGENT_SAFETY_PROGRAM_STATE?.runtime?.official_metadata_connectivity || '',
          agentSafetyMetadataTransport: window.AGENT_SAFETY_PROGRAM_STATE?.runtime?.official_metadata_transport || '',
          agentSafetyReceiptClass: window.AGENT_SAFETY_PROGRAM_STATE?.runtime?.provenance_receipt_class || '',
          agentSafetyBudget: window.AGENT_SAFETY_PROGRAM_STATE?.canonical_protocol?.execution_invariants?.budget || {},
          agentSafetySplit: window.AGENT_SAFETY_PROGRAM_STATE?.canonical_protocol?.execution_invariants?.probe_split || {},
          agentSafetyClosedRows: document.querySelectorAll('#agent-safety-program .current-research-table tbody tr').length,
          agentSafetyClosedSummary: window.AGENT_SAFETY_PROGRAM_STATE?.closed_basin_summary || {},
          discussedGroups: document.querySelectorAll('.canonical-idea-group').length,
          categoryLinks: document.querySelectorAll('.canonical-category-nav a').length,
          objectHierarchyPanels: document.querySelectorAll('.current-object-hierarchy').length,
          briefingHeroes: document.querySelectorAll('.ideas-briefing-hero').length,
          briefingMetrics: document.querySelectorAll('.ideas-briefing-metrics > article').length,
          briefingDecisions: document.querySelectorAll('.ideas-briefing-decisions > article').length,
          briefingGuides: document.querySelectorAll('.research-briefing-guide').length,
          briefingLessons: document.querySelectorAll('.briefing-lessons > article').length,
          briefingTaxonomyCards: document.querySelectorAll('.briefing-taxonomy-card').length,
          briefingModeButtons: document.querySelectorAll('.briefing-mode-btn').length,
          categoryBriefings: document.querySelectorAll('.canonical-category-briefing').length,
          objectLevelCards: document.querySelectorAll('.research-object-levels > article').length,
          inventoryTotals: [...document.querySelectorAll('[data-research-inventory-total]')].map(x=>Number(x.dataset.researchInventoryTotal||0)),
          categoryRecordTotals: [...document.querySelectorAll('.canonical-category-nav a')].map(x=>Number(x.dataset.categoryTotal||0)),
          legacyMixedStatusRows: document.querySelectorAll('.current-object-hierarchy .current-research-table tbody tr').length,
          categorizedContextBanks: document.querySelectorAll('.categorized-context-bank').length,
          openCategorizedContextBanks: document.querySelectorAll('.categorized-context-bank[open]').length,
          categorizedContextCards: document.querySelectorAll('.categorized-context-card').length,
          categorizedContextIds: [...document.querySelectorAll('.categorized-context-card')].map(x=>x.dataset.researchObject||''),
          categorizedContextCodes: [...document.querySelectorAll('.categorized-context-card header > div > span:first-child')].map(x=>(x.textContent||'').trim()),
          paperHandoffs: document.querySelectorAll('.paper-handoff-research-item').length,
          paperHandoffEvidence: document.querySelectorAll('.paper-handoff-evidence-step').length,
          paperHandoffCodes: [...document.querySelectorAll('.paper-handoff-research-item,.paper-handoff-evidence-step')].map(x=>x.dataset.researchCode||''),
          researchCategoryLanes: document.querySelectorAll('.research-category-lane').length,
          researchItemEvidenceTracks: document.querySelectorAll('.human-review-idea-card .research-item-evidence-track').length,
          researchItemFieldLineages: document.querySelectorAll('.human-review-idea-card .research-item-field-lineage').length,
          researchItemTimelineLinks: [...document.querySelectorAll('.human-review-idea-card .research-item-field-lineage a')].filter(x=>(x.getAttribute('href')||'').startsWith('research-timeline.html?research=')).length,
          pfCodes: [...document.querySelectorAll('.paper-incubation-card')].map(x=>x.dataset.pfCode||''),
          safetyCodes: [...document.querySelectorAll('[data-safety-code]')].map(x=>x.dataset.safetyCode||''),
          parentItems: document.querySelectorAll('.canonical-parent-item').length,
          lifecycleStrips: document.querySelectorAll('.canonical-lifecycle-strip').length,
          discussedCards: document.querySelectorAll('.human-review-idea-card').length,
          readyCards: document.querySelectorAll('.human-review-idea-card.human-tone-ready').length,
          pausedCards: document.querySelectorAll('.human-review-idea-card.human-tone-paused').length,
          mergedCards: document.querySelectorAll('.human-review-idea-card.human-tone-merged').length,
          droppedCards: document.querySelectorAll('.human-review-idea-card.human-tone-dropped').length,
          terminalCounts: [...document.querySelectorAll('.human-review-idea-card')].reduce((a,x)=>{const k=x.dataset.terminalStatus||'';a[k]=(a[k]||0)+1;return a;},{}),
          historicalCounts: [...document.querySelectorAll('.human-review-idea-card')].reduce((a,x)=>{const k=x.dataset.historicalStatus||'';a[k]=(a[k]||0)+1;return a;},{}),
          evidenceDispositionCounts: [...document.querySelectorAll('.human-review-idea-card')].reduce((a,x)=>{const k=x.dataset.evidenceDisposition||'';a[k]=(a[k]||0)+1;return a;},{}),
          parentStatusByCode: Object.fromEntries([...document.querySelectorAll('.human-review-idea-card')].map(x=>[x.querySelector('.human-idea-code')?.textContent?.trim()||'',x.dataset.terminalStatus||''])),
          lifecycleCells: document.querySelectorAll('.canonical-lifecycle-strip > span').length,
          parentActionCounts: [...document.querySelectorAll('.canonical-lifecycle-strip > span:nth-child(2)')].reduce((a,x)=>{const t=(x.textContent||'').replace(/唯一内部动作|Primary internal action/g,'').trim();a[t]=(a[t]||0)+1;return a;},{}),
          explicitLegacyP0Badges: [...document.querySelectorAll('.human-status-badge')].filter(x=>(x.textContent||'').trim()==='已进入 P0').length,
          formalAuthorityZero: [...document.querySelectorAll('.canonical-lifecycle-strip > span:last-child')].filter(x=>(x.textContent||'').trim().endsWith('0')).length,
          evidenceDispositionPanels: document.querySelectorAll('.terminal-evidence-disposition').length,
          terminalSummary: window.HUMAN_TERMINAL_IDEA_STATE?.summary || {},
          canonicalResearchSummary: window.RESEARCH_ITEM_STATE?.summary || {},
          canonicalResearchItems: Object.fromEntries((window.RESEARCH_ITEM_STATE?.research_items || []).map(x=>[x.code,x.scientific_state])),
          paperRegistry: window.PAPER_REGISTRY || {},
          absorbedChildCount: Object.keys(window.HUMAN_TERMINAL_IDEA_STATE?.absorbed_children || {}).length,
          feedbackSummaries: document.querySelectorAll('.human-review-idea-card .human-idea-summary p').length,
          parentBriefingSummaries: document.querySelectorAll('.human-review-idea-card .one-minute-briefing').length,
          parentBriefingReasonPills: document.querySelectorAll('.human-review-idea-card .briefing-reason-pill').length,
          parentConcreteComparisons: document.querySelectorAll('.human-review-idea-card .concrete-method-comparison.comparison-parent').length,
          supplementalConcreteComparisons: document.querySelectorAll('.supplemental-idea-card .concrete-method-comparison.comparison-supplemental').length,
          pfConcreteComparisons: document.querySelectorAll('.paper-incubation-card .concrete-method-comparison.comparison-pf').length,
          concreteComparisonTables: document.querySelectorAll('.concrete-method-comparison table').length,
          concreteComparisonRows: document.querySelectorAll('.concrete-method-comparison tbody tr').length,
          simpleMethodGuides: document.querySelectorAll('.concrete-method-comparison .simple-method-guide').length,
          simpleMethodGuideCells: document.querySelectorAll('.concrete-method-comparison .simple-method-guide span').length,
          simpleMethodGuidesComplete: [...document.querySelectorAll('.concrete-method-comparison')].every(panel=>{const guide=panel.querySelector('.simple-method-guide'); return guide && guide.querySelectorAll('span').length===4 && ['输入看什么','具体怎么跑','最后输出什么','相比复杂方法少了什么'].every(marker=>(guide.textContent||'').includes(marker));}),
          simpleMethodGuideText: [...document.querySelectorAll('.concrete-method-comparison .simple-method-guide')].map(x=>(x.textContent||'').replace(/\\s+/g,' ').trim()).join('\\n'),
          concreteComparisonComplete: [...document.querySelectorAll('.concrete-method-comparison')].every(panel=>['我们的方法怎么做','简单方法一句话','简单方法具体怎么做到','怎么保证比较公平','效果差多少','为什么这个结果足以停止'].every(marker=>(panel.textContent||'').includes(marker))),
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
          parentMergeRules: [...document.querySelectorAll('.human-review-idea-card h4')].filter(x=>/必须并回父(?: Idea| 研究方向|级研究方向)|must merge into its parent/.test(x.textContent||'')).length,
          openDiscussedCards: document.querySelectorAll('.human-review-idea-card[open]').length,
          codes: [...document.querySelectorAll('.human-idea-code')].map(x=>(x.textContent||'').trim()),
          newGroups: document.querySelectorAll('.canonical-related-bank').length,
          openRelatedBanks: document.querySelectorAll('.canonical-related-bank[open]').length,
          categoryRelatedBanks: document.querySelectorAll('.canonical-related-bank:not(.categorized-context-bank)').length,
          openCategoryRelatedBanks: document.querySelectorAll('.canonical-related-bank:not(.categorized-context-bank)[open]').length,
          newCards: document.querySelectorAll('.supplemental-idea-card').length,
          supplementalBriefingSummaries: document.querySelectorAll('.supplemental-idea-card .one-minute-briefing').length,
          standaloneCodes: [...document.querySelectorAll('.supplemental-idea-card summary>div>span')].map(x=>(x.textContent||'').trim()),
          openNewCards: document.querySelectorAll('.supplemental-idea-card[open]').length,
          supplementalBlankPrimaryFields: [...document.querySelectorAll('.supplemental-idea-card')].flatMap(card=>[...card.querySelectorAll('.supplemental-human-grid>section>p,.human-evidence-grid>section>p,.human-experiment-grid>section>p')].filter(node=>!String(node.textContent||'').trim()||['—','--','-'].includes(String(node.textContent||'').trim())).map(node=>(card.querySelector('summary>div>span')?.textContent||'').trim())),
          newFinal: [...document.querySelectorAll('.supplemental-idea-card summary small')].filter(x=>/FINAL20|merge audit/.test(x.textContent||'')).length,
          newInspired: [...document.querySelectorAll('.supplemental-idea-card summary small')].filter(x=>/网络灵感|internet-inspired/.test(x.textContent||'')).length,
          mergedMethods: document.querySelectorAll('.human-absorbed-methods').length,
          freshCollisionBlocks: document.querySelectorAll('.human-fresh-collision').length,
          freshCollisionLinks: document.querySelectorAll('.human-fresh-collision nav a').length,
          liveMementoCards: document.querySelectorAll('#live-memento-paper-design').length,
          liveMementoText: document.querySelector('#live-memento-paper-design')?.textContent||'',
          liveMementoState: window.MEMENTO_JOINT_IDENTIFIABILITY_PAPER_DESIGN || {},
          liveMementoSimpleGuideCells: document.querySelectorAll('#live-memento-paper-design .simple-method-guide span').length,
          incubationCards: document.querySelectorAll('.paper-incubation-card').length,
          incubationBriefingSummaries: document.querySelectorAll('.paper-incubation-card .one-minute-briefing').length,
          incubationAdvance: document.querySelectorAll('.paper-incubation-card.incubation-advance').length,
          incubationP0: document.querySelectorAll('.paper-incubation-card.incubation-p0').length,
          incubationRevise: document.querySelectorAll('.paper-incubation-card.incubation-revise').length,
          incubationBlock: document.querySelectorAll('.paper-incubation-card.incubation-block').length,
          incubationStop: document.querySelectorAll('.paper-incubation-card.incubation-stop').length,
          incubationMerge: document.querySelectorAll('.paper-incubation-card.incubation-merge').length,
          incubationOpen: document.querySelectorAll('.paper-incubation-card[open]').length,
          incubationSummary: window.PAPER_FIRST_IDEA_INCUBATION?.summary || {},
          designSummary: window.PAPER_FIRST_DESIGN_ADJUDICATION?.summary || {},
          designVerdicts: Object.fromEntries((window.PAPER_FIRST_DESIGN_ADJUDICATION?.rows || []).map(x=>[x.id,x.verdict])),
          pf1ProblemDecision: window.PAPER_FIRST_PF1_PROBLEM_ADJUDICATION?.decision || '',
          pf1ProblemActive: Boolean(window.PAPER_FIRST_PF1_PROBLEM_ADJUDICATION?.authority?.paper_problem_active),
          pf1MethodAuthorized: Boolean(window.PAPER_FIRST_PF1_PROBLEM_ADJUDICATION?.authority?.method_design_authorized),
          pf2MethodDecision: window.PAPER_FIRST_PF2_METHOD_ADJUDICATION?.decision || '',
          pf2MethodProblemStatus: window.PAPER_FIRST_PF2_METHOD_ADJUDICATION?.paper_problem_status || '',
          pf2MethodBlueprintAuthorized: Boolean(window.PAPER_FIRST_PF2_METHOD_ADJUDICATION?.authority?.experiment_blueprint_authorized),
          pf2MethodLocalAuthorized: Boolean(window.PAPER_FIRST_PF2_METHOD_ADJUDICATION?.authority?.local_validation_authorized),
          pf357Summary: window.PAPER_FIRST_PF357_PROBLEM_ADJUDICATION?.summary || {},
          pf357Decisions: Object.fromEntries((window.PAPER_FIRST_PF357_PROBLEM_ADJUDICATION?.rows || []).map(x=>[x.id,x.decision])),
          freshSummary: window.PAPER_FIRST_FRESH_SATURATION?.summary || {},
          freshDecision: window.PAPER_FIRST_FRESH_SATURATION?.decision || '',
          freshZeroSurvivorPolicy: Boolean(window.PAPER_FIRST_FRESH_SATURATION?.policy?.zero_survivors_is_valid_and_preferred_to_forced_shortlist),
          freshPanel: document.querySelectorAll('.paper-first-fresh-saturation').length,
          shadowDesignSummary: window.PAPER_FIRST_SEARCH_PORTFOLIO_DESIGN_ADJUDICATION?.summary || {},
          shadowDesignPolicy: window.PAPER_FIRST_SEARCH_PORTFOLIO_DESIGN_ADJUDICATION?.policy || {},
          currentShadowSearch: window.CURRENT_RESEARCH_STATUS?.shadow_search || {},
          closedAuditPanels: document.querySelectorAll('.current-closed-basin-audit').length,
          canonicalClosedArchives: document.querySelectorAll('.canonical-closed-archive').length,
          openCanonicalClosedArchives: document.querySelectorAll('.canonical-closed-archive[open]').length,
          closedIdeaBanks: document.querySelectorAll('.canonical-closed-idea-bank').length,
          openClosedIdeaBanks: document.querySelectorAll('.canonical-closed-idea-bank[open]').length,
          closedIdeaBankLabels: [...document.querySelectorAll('.canonical-closed-idea-bank>summary b')].map(x=>(x.textContent||'').trim()),
          closedIdeaCards: document.querySelectorAll('.closed-idea-card').length,
          closedIdeaBriefingSummaries: document.querySelectorAll('.closed-idea-card .one-minute-briefing').length,
          safetyBriefingSummaries: document.querySelectorAll('#agent-safety-program .agent-safety-briefing').length,
          oneMinuteBriefingLabels: [...document.querySelectorAll('.one-minute-briefing>header>b,.agent-safety-briefing>header>b')].map(x=>(x.textContent||'').trim()),
          oneMinuteSixPartCards: [...document.querySelectorAll('.one-minute-briefing')].filter(card=>card.querySelectorAll('[data-briefing-part]').length===6).length,
          oneMinuteReaderText: [...document.querySelectorAll('.one-minute-briefing')].map(card=>(card.textContent||'').replace(/\\s+/g,' ').trim()).join('\\n'),
          oneMinuteTemplateScenes: [...document.querySelectorAll('.one-minute-briefing [data-briefing-part="scene"]')].filter(node=>['这个方向要解决的是','当前页面记录的最小任务/实验场景','这个方向当前主要在回答论文问题'].some(mark=>(node.textContent||'').includes(mark))).length,
          closedGenericScenes: [...document.querySelectorAll('.closed-one-minute-briefing [data-briefing-part="scene"]')].filter(node=>(node.textContent||'').includes('这条卡不是重新训练一个 Agent')).length,
          closedGenericObserved: [...document.querySelectorAll('.closed-one-minute-briefing [data-briefing-part="observed"]')].filter(node=>(node.textContent||'').includes('最关键的已知事实是')).length,
          oneMinuteStandardCards: document.querySelectorAll('#one-minute-writing-standard .one-minute-standard-grid>article').length,
          oneMinuteStandardText: document.querySelector('#one-minute-writing-standard')?.textContent||'',
          oneMinuteReadingPathText: document.querySelector('#one-minute-writing-standard .one-minute-reading-path')?.textContent||'',
          a3OneMinuteText: document.querySelector('#idea-a-3 .one-minute-briefing')?.textContent||'',
          p04OneMinuteText: document.querySelector('.closed-idea-card[data-closed-source="SHADOW-P04-C01"] .one-minute-briefing')?.textContent||'',
          a3BriefingLayout: (()=>{const card=document.querySelector('#idea-a-3 .one-minute-briefing-grid');if(!card)return{};const part=n=>card.querySelector('[data-briefing-part="'+n+'"]')?.getBoundingClientRect();const scene=part('scene'),progress=part('progress'),observed=part('observed'),judgment=part('judgment'),human=part('human'),next=part('next');return{sceneTop:scene?.top||0,progressTop:progress?.top||0,observedTop:observed?.top||0,judgmentTop:judgment?.top||0,humanTop:human?.top||0,nextTop:next?.top||0,sceneWidth:scene?.width||0,progressWidth:progress?.width||0,cardWidth:card.getBoundingClientRect().width,pageOverflow:document.documentElement.scrollWidth>document.documentElement.clientWidth};})(),
          staleThirtySecondCopy: /给师兄的 30 秒结论|30 秒说明|30-second briefing/.test(document.body.textContent||''),
          closedIdeaCodes: [...document.querySelectorAll('.closed-idea-card')].map(x=>x.dataset.closedCode||''),
          closedIdeaSources: [...document.querySelectorAll('.closed-idea-card')].map(x=>x.dataset.closedSource||''),
          allResearchObjectCodes: [
            ...[...document.querySelectorAll('.human-idea-code')].map(x=>(x.textContent||'').trim()),
            ...[...document.querySelectorAll('.supplemental-idea-card summary>div>span')].map(x=>(x.textContent||'').trim()),
            ...[...document.querySelectorAll('.paper-incubation-card')].map(x=>x.dataset.pfCode||''),
            ...[...document.querySelectorAll('.categorized-context-card header>div>span:first-child')].map(x=>(x.textContent||'').trim()),
            ...[...document.querySelectorAll('.paper-handoff-research-item[data-research-code],.paper-handoff-evidence-step[data-research-code]')].map(x=>x.dataset.researchCode||''),
            ...[...document.querySelectorAll('[data-safety-code]')].map(x=>x.dataset.safetyCode||''),
            ...[...document.querySelectorAll('.closed-idea-card')].map(x=>x.dataset.closedCode||''),
          ],
          mergedClosureRows: document.querySelectorAll('[data-closure-merged="true"]').length,
          closedIdeaBlankPrimaryFields: [...document.querySelectorAll('.closed-idea-card')].flatMap(card=>[...card.querySelectorAll('.closed-idea-body section>p')].filter(node=>!String(node.textContent||'').trim()||['—','--','-'].includes(String(node.textContent||'').trim())).map(node=>card.dataset.closedCode||'')),
          closedAuditRows: document.querySelectorAll('.current-closed-basin-audit tbody tr').length,
          closedAuditReasonsAllZh: [...document.querySelectorAll('.closed-idea-stop p')].every(node => /[\u3400-\u9fff]/.test(node.textContent || '')),
          closedAuditReopensAllZh: [...document.querySelectorAll('.closed-one-minute-briefing>div>p:last-child')].every(node => /[\u3400-\u9fff]/.test(node.textContent || '')),
          statusOuterTracks: getComputedStyle(document.querySelector('.project-status-strip.current')).gridTemplateColumns.trim().split(/\\s+/).length,
          statusCopyTracks: getComputedStyle(document.querySelector('.project-status-copy')).gridTemplateColumns.trim().split(/\\s+/).length,
          statusMetricTracks: getComputedStyle(document.querySelector('.project-status-metrics')).gridTemplateColumns.trim().split(/\\s+/).length,
          statusMetricCount: document.querySelectorAll('.project-status-metrics > div').length,
          shadowSourceSummary: window.PAPER_FIRST_SEARCH_PORTFOLIO_DESIGN_ADJUDICATION?.shadow_source?.summary || {},
          shadowQueueSummary: window.PAPER_FIRST_SEARCH_PORTFOLIO_DESIGN_ADJUDICATION?.shadow_source?.queue_summary || {},
          shadowLatestRun: window.RESEARCH_SYSTEM_STATE?.paper_first_problem_search_portfolio?.latest_run || {},
          shadowLatestSummary: window.RESEARCH_SYSTEM_STATE?.paper_first_problem_search_portfolio?.latest_run?.summary || {},
          shadowLatestPanels: document.querySelectorAll('.paper-first-search-latest').length,
          shadowAdmission: window.RESEARCH_SYSTEM_STATE?.paper_first_shadow_search_admission || {},
          shadowAdmissionPanels: document.querySelectorAll('.paper-first-shadow-admission').length,
          sp15SupportSummary: window.PAPER_FIRST_SP15_IDENTIFIABILITY_SUPPORT?.summary || {},
          sp15SupportDiagnosis: window.PAPER_FIRST_SP15_IDENTIFIABILITY_SUPPORT?.support_diagnosis || {},
          prematureMethodSummary: window.PAPER_FIRST_PREMATURE_METHOD_DIAGNOSTICS?.summary || window.RESEARCH_SYSTEM_STATE?.paper_first_premature_method_diagnostics?.summary || {},
          prematureMethodPanels: document.querySelectorAll('.premature-method-diagnostic').length,
          designCards: document.querySelectorAll('.paper-incubation-card small').length,
          text: document.body.textContent || ''
        };""")
        require(ideas["chapters"] == 0, f"paper-ideas must use category-first architecture instead of the old two-chapter split, got {ideas['chapters']} legacy chapters")
        require(ideas["agentSafetyProgram"] == 1 and ideas["agentSafetyStage"] == system["agentSafetyStage"] and ideas["agentSafetyRuntimeStatus"] == system["agentSafetyRuntimeStatus"] and ideas["agentSafetyBoundedEvidence"] is False and ideas["agentSafetyQualification"] is False and ideas["agentSafetyOverallExecution"] is False and ideas["agentSafetyQualificationStatus"] == "STOP_SUPPORT_ZERO_CURRENTLY_SAFE_FROZEN_STATES" and ideas["agentSafetyQualifiedStates"] == 0 and ideas["agentSafetyPrincipleDeadEnd"] is False and ideas["agentSafetyHeldoutFuture"] is False and ideas["agentSafetyP0"] is False and ideas["agentSafetyGpu"] is False, f"Paper Ideas Agent Safety support-stop state drift: {ideas['agentSafetyProgram']}/{ideas['agentSafetyStage']}/{ideas['agentSafetyRuntimeStatus']}/{ideas['agentSafetyBoundedEvidence']}/{ideas['agentSafetyQualification']}/{ideas['agentSafetyOverallExecution']}/{ideas['agentSafetyQualificationStatus']}/{ideas['agentSafetyQualifiedStates']}/{ideas['agentSafetyPrincipleDeadEnd']}")
        iab=ideas["agentSafetyBudget"]; ias=ideas["agentSafetySplit"]
        require((iab.get("states"),iab.get("history_strata"),ias.get("qualification_count"),ias.get("heldout_count"),iab.get("total_model_evaluations_upper_bound"),iab.get("contract_max_model_calls")) == (4,2,3,8,240,256) and ias.get("disjoint") is True, f"Paper Ideas Agent Safety canonical harness-v2 drift: {iab}/{ias}")
        require(ideas["agentSafetyMetadata"] == "VERIFIED" and ideas["agentSafetyMetadataTransport"] == "GITHUB_ACTIONS_LITERAL_HF_CAPTURE" and ideas["agentSafetyReceiptClass"] == "NON_AUTHORITATIVE_CACHE_CONTENT_CHECK" and "240/256" in ideas["text"] and "SUPPORT STOP" in ideas["text"].upper() and "0/4" in ideas["text"], f"Paper Ideas Agent Safety provenance/support-stop display drift: {ideas['agentSafetyMetadata']}/{ideas['agentSafetyMetadataTransport']}/{ideas['agentSafetyReceiptClass']}")
        asc=ideas["agentSafetyClosedSummary"]
        typed_text=ideas["text"]
        typed_markers=(
            ("搜索闭包，不是原理死路" in typed_text or "search closure, not scientific dead-end" in typed_text),
            ("历史搜索闭包" in typed_text or "legacy search closure" in typed_text),
            ("原理级关闭" in typed_text or "scientific dead-end" in typed_text),
            "PORT-010" in typed_text,
        )
        require(ideas["agentSafetyClosedRows"] == int(asc.get("total") or 0) == 4 and (int(asc.get("canonical_typed") or 0),int(asc.get("legacy_untyped") or 0),int(asc.get("core_principle_dead_ends") or 0),int(asc.get("method_realization_closures") or 0)) == (3,1,1,2) and all(typed_markers), f"Paper Ideas Agent Safety typed closure/support-stop display drift: rows={ideas['agentSafetyClosedRows']} summary={asc} markers={typed_markers}")
        require(ideas["p0Entry"] == 0 and ideas["p0Boards"] == 0 and ideas["experimentLinks"] >= 1, f"legacy P0-entry/control boards must stay off canonical Paper Ideas: {ideas['p0Entry']}/{ideas['p0Boards']}/{ideas['experimentLinks']}")
        require(ideas["p0AdmissionSummary"].get("active_p0") == 27 and ideas["p0AdmissionSummary"].get("transitioned_from_p0_ready") == 16 and ideas["p0AdmissionSummary"].get("revived_from_drop") == 7 and ideas["p0AdmissionSummary"].get("settings_complete") == 27 and ideas["p0AdmissionSummary"].get("execution_authorized") == 0, f"paper-ideas unified P0 admission state is stale: {ideas['p0AdmissionSummary']}")
        require(ideas["p0Summary"].get("ready_now") == 0 and ideas["p0Summary"].get("pre_p0_blocked") == 4 and ideas["p0Summary"].get("gpu_hours_cap_ready_now") == 0 and ideas["p0Summary"].get("p1_authorized") == 0, f"P0 Pre-P0/resource summary is wrong: {ideas['p0Summary']}")
        require(ideas["p0Policy"].get("pre_p0_identifiability_required") is True and ideas["p0Policy"].get("automatic_p0_to_p1_forbidden") is True and ideas["p0Policy"].get("p0_pass_requires_human_approval") is True, f"P0 human/Pre-P0 approval policy is missing: {ideas['p0Policy']}")
        require(ideas["toc2"] >= 2 and ideas["toc3"] >= 7 and ideas["toc4"] == 0, f"paper-ideas category-first TOC hierarchy is wrong: {ideas['toc2']}/{ideas['toc3']}/{ideas['toc4']}")
        require((ideas["discussedGroups"],ideas["categoryLinks"],ideas["parentItems"],ideas["lifecycleStrips"],ideas["discussedCards"]) == (7,7,26,26,26), f"category-first ledger must expose seven groups and 26 complete parent cards: {ideas['discussedGroups']}/{ideas['categoryLinks']}/{ideas['parentItems']}/{ideas['lifecycleStrips']}/{ideas['discussedCards']}")
        require((ideas["objectHierarchyPanels"],ideas["objectLevelCards"],ideas["legacyMixedStatusRows"]) == (1,4,0), f"paper-ideas must expose parent, related-direction, numbered-closure, and evidence ledgers separately and remove the old mixed table: {ideas['objectHierarchyPanels']}/{ideas['objectLevelCards']}/{ideas['legacyMixedStatusRows']}")
        expected_portfolio=int(expected_research_summary.get("portfolio_objects") or 0)
        require(ideas["inventoryTotals"] == [expected_portfolio,expected_portfolio] and ideas["categoryRecordTotals"] == expected_category_totals and sum(ideas["categoryRecordTotals"]) == expected_portfolio, f"full A-G research inventory must expose every canonical portfolio object: {ideas['inventoryTotals']}/{ideas['categoryRecordTotals']} expected={expected_portfolio}/{expected_category_totals}")
        crs=ideas["canonicalResearchSummary"]
        require((crs.get("research_items"),crs.get("experiment_records"),crs.get("portfolio_experiment_contexts"),crs.get("evidence_contexts"),crs.get("portfolio_objects")) == (expected_research_summary.get("research_items"),expected_research_summary.get("experiment_records"),expected_research_summary.get("portfolio_experiment_contexts"),expected_research_summary.get("evidence_contexts"),expected_research_summary.get("portfolio_objects")) and crs.get("parent_scientific_states") == {"HOLD":4,"MERGED":6,"STOPPED":16}, f"canonical ResearchItem projection is missing or inconsistent: {crs}")
        require(all(ideas["canonicalResearchItems"].get(code)=="HOLD" for code in ("A-3","B-2","B-3","E-1")) and ideas["canonicalResearchItems"].get("E-7")=="PAPER_READY" and ideas["canonicalResearchItems"].get("G-1")=="HOLD", f"canonical scientific-state authority is wrong: {ideas['canonicalResearchItems']}")
        registry_summary=ideas["paperRegistry"].get("summary") or {}
        registry_papers={row.get("paper_id"):row for row in (ideas["paperRegistry"].get("papers") or [])}
        require(registry_summary == expected_registry_summary and {pid:row.get("paper_stage") for pid,row in registry_papers.items()} == expected_registry_stages and registry_summary.get("scientific_holds") == 0 and registry_papers.get("STRI",{}).get("source_research_item") == "E-7" and registry_papers.get("STRI",{}).get("paper_stage") == "SUBMISSION_READY" and registry_papers.get("AGENT-SAFETY-R9",{}).get("source_research_item") == "G-1" and registry_papers.get("AGENT-SAFETY-R9",{}).get("paper_stage") == "SUBMISSION_READY" and registry_papers.get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",{}).get("paper_stage") == "SUBMISSION_READY" and registry_papers.get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",{}).get("source_research_item") is None, f"Research Portfolio must match the current PaperRegistry projection while preserving D2 paper-first provenance and broader G-1 HOLD: {ideas['paperRegistry']}")
        require(ideas["categorizedContextBanks"] == ideas["openCategorizedContextBanks"] == 1 and ideas["categorizedContextCards"] == 2 and set(ideas["categorizedContextIds"]) == {"MEM-HISTORY","SP-15"}, f"B-category evidence context must stay complete without splitting the STRI paper chain into peer cards: {ideas['categorizedContextBanks']}/{ideas['openCategorizedContextBanks']}/{ideas['categorizedContextCards']}/{ideas['categorizedContextIds']}")
        require(set(ideas["categorizedContextCodes"]) == {"B-12","B-13"} and ideas["paperHandoffs"] == 1 and ideas["paperHandoffEvidence"] == 3 and set(ideas["paperHandoffCodes"]) == {"E-7","E-7a","E-7b","E-7c"}, f"E-7 must render as one ResearchItem→PaperState handoff with three nested evidence records: {ideas['categorizedContextCodes']}/{ideas['paperHandoffs']}/{ideas['paperHandoffEvidence']}/{ideas['paperHandoffCodes']}")
        require(ideas["researchCategoryLanes"] == 21 and ideas["researchItemEvidenceTracks"] == 26 and ideas["researchItemFieldLineages"] == 26 and ideas["researchItemTimelineLinks"] == 26, f"seven A-G categories must expose three lanes, while every parent ResearchItem exposes one evidence trail and one field/timeline lineage bridge: {ideas['researchCategoryLanes']}/{ideas['researchItemEvidenceTracks']}/{ideas['researchItemFieldLineages']}/{ideas['researchItemTimelineLinks']}")
        require(set(ideas["pfCodes"]) == {"A-8","A-9","A-10","A-11","A-12","B-11","C-7","E-5","E-6"}, f"former PF directions are not distributed into A/B/C/E categories without colliding with parent codes: {ideas['pfCodes']}")
        require(set(ideas["safetyCodes"]) == {"G-1","G-2","G-3","G-4","G-5"}, f"safety directions are not normalized to G-1..G-5: {ideas['safetyCodes']}")
        require((ideas["readyCards"], ideas["pausedCards"], ideas["mergedCards"], ideas["droppedCards"]) == (0, 4, 6, 16), f"canonical parent tone counts must be HOLD=4/MERGED=6/STOP=16: {ideas['readyCards']}/{ideas['pausedCards']}/{ideas['mergedCards']}/{ideas['droppedCards']}")
        require((ideas["terminalCounts"].get("hold"),ideas["terminalCounts"].get("stop"),ideas["terminalCounts"].get("merge")) == (4,16,6) and not any(ideas["terminalCounts"].get(k) for k in ("p0","p0-ready","drop")), f"current parent scientific states must be hold=4/stop=16/merge=6: {ideas['terminalCounts']}")
        require(ideas["historicalCounts"].get("p0") == 20 and ideas["historicalCounts"].get("merge") == 6, f"historical P0 lifecycle must remain separately preserved: {ideas['historicalCounts']}")
        require(ideas["evidenceDispositionCounts"] == {"stop":16,"hold":4,"merge":6} and ideas["evidenceDispositionPanels"] == 26, f"latest evidence disposition is missing or collapsed into terminal state: {ideas['evidenceDispositionCounts']}/{ideas['evidenceDispositionPanels']}")
        require((ideas["briefingHeroes"],ideas["briefingMetrics"],ideas["briefingDecisions"],ideas["briefingGuides"],ideas["briefingLessons"],ideas["briefingTaxonomyCards"],ideas["briefingModeButtons"],ideas["categoryBriefings"]) == (1,4,3,1,3,6,2,7), f"briefing-first overview/taxonomy/category summaries are incomplete: {ideas}")
        require((ideas["parentBriefingSummaries"],ideas["parentBriefingReasonPills"],ideas["supplementalBriefingSummaries"],ideas["incubationBriefingSummaries"],ideas["closedIdeaBriefingSummaries"],ideas["safetyBriefingSummaries"]) == (26,26,7,9,expected_shadow_closed,1), f"one-minute idea summaries are incomplete: {ideas}")
        live=ideas["liveMementoState"]
        require(ideas["liveMementoCards"] == 1 and live.get("status") == "PAPER_DESIGN_FROZEN_EXACT_RUNTIME_SUPPORT_HOLD" and (live.get("paper_design_audit") or {}).get("passed") is True and (live.get("source_integrity") or {}).get("passed") is True and ideas["liveMementoSimpleGuideCells"] == 4, f"live MEMENTO Paper Design candidate is missing or unverified: cards={ideas['liveMementoCards']} state={live} guide_cells={ideas['liveMementoSimpleGuideCells']}")
        require(all(marker in ideas["liveMementoText"] for marker in ("36/36", "12", "36", "-0.05", "简单方法具体怎么做到", "任务组合", "当前没有实验执行权限")), f"live MEMENTO card lacks concrete task/control/F0 explanation: {ideas['liveMementoText']}")
        require(len(ideas["oneMinuteBriefingLabels"]) == expected_one_minute and all(label == "【1min结论】" for label in ideas["oneMinuteBriefingLabels"]) and not ideas["staleThirtySecondCopy"], f"all idea-card briefings must use the unified one-minute label with no stale 30-second copy: count={len(ideas['oneMinuteBriefingLabels'])} expected={expected_one_minute} / stale={ideas['staleThirtySecondCopy']}")
        require(ideas["oneMinuteSixPartCards"] == expected_one_minute and ideas["oneMinuteStandardCards"] == 6, f"all one-minute briefings must implement the six-part decision-memory standard: cards={ideas['oneMinuteSixPartCards']} expected={expected_one_minute} standard={ideas['oneMinuteStandardCards']}")
        reader_jargon=("STOP_CURRENT_SUBSTRATE_UPDATER_INCOMPETENT","effective candidate fraction","future_eval","development unit","72-unit","pair-target","n-ary","RSIC","reward invariance","reward-meaning","source workflow","paired-edit","同信息","谱系")
        require(ideas["oneMinuteTemplateScenes"] == 0 and ideas["closedGenericScenes"] == 0 and ideas["closedGenericObserved"] == 0 and not any(token in ideas["oneMinuteReaderText"] for token in reader_jargon), f"one-minute reader layer still contains template prose or backend jargon: templates={ideas['oneMinuteTemplateScenes']} closed_scene={ideas['closedGenericScenes']} closed_observed={ideas['closedGenericObserved']} hits={[token for token in reader_jargon if token in ideas['oneMinuteReaderText']]}")
        require(all(marker in ideas["oneMinuteStandardText"] for marker in ("具体任务场景","生命周期 + 实际动作","实验实际看到了什么","能确定 / 不能确定","希望人工判断什么","下一步方案","没有真实任务/实验就明确说尚未固定或尚未运行")), f"visible one-minute writing standard is incomplete: {ideas['oneMinuteStandardText']}")
        require(all(marker in ideas["oneMinuteReadingPathText"] for marker in ("快速阅读顺序","30 秒回顾","① 具体场景 → ③ 实际现象 → ④ 当前判断","讨论下一步","② 实际进度 → ⑤ 希望人工判断 → ⑥ 下一步方案")), f"one-minute fast reading path is missing or unclear: {ideas['oneMinuteReadingPathText']}")
        layout=ideas["a3BriefingLayout"]
        require(layout and not layout.get("pageOverflow") and abs(layout.get("sceneWidth",0)-layout.get("cardWidth",0)) < 3 and abs(layout.get("progressWidth",0)-layout.get("cardWidth",0)) < 3 and layout.get("sceneTop",0) < layout.get("progressTop",0) < layout.get("observedTop",0) < layout.get("humanTop",0) and abs(layout.get("observedTop",0)-layout.get("judgmentTop",0)) < 3 and abs(layout.get("humanTop",0)-layout.get("nextTop",0)) < 3, f"one-minute visual hierarchy must be scene → compact progress → observed/judgment → human/next with no overflow: {layout}")
        for width in (900,604):
            request("POST", f"/session/{session_id}/window/rect", {"width":width,"height":900})
            time.sleep(0.4)
            responsive=execute(session_id,"""const card=document.querySelector('#idea-a-3 .one-minute-briefing-grid');const names=['scene','progress','observed','judgment','human','next'];const rects=names.map(n=>card?.querySelector('[data-briefing-part="'+n+'"]')?.getBoundingClientRect());return {tops:rects.map(r=>r?.top||0),widths:rects.map(r=>r?.width||0),cardWidth:card?.getBoundingClientRect().width||0,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth};""")
            require(not responsive.get("overflow") and all(abs(w-responsive.get("cardWidth",0)) < 3 for w in responsive.get("widths",[])) and all(a < b for a,b in zip(responsive.get("tops",[])[:-1],responsive.get("tops",[])[1:])), f"one-minute briefing must become a no-overflow single-column 1→6 reading path at {width}px: {responsive}")
        request("POST", f"/session/{session_id}/window/rect", {"width":1366,"height":900})
        time.sleep(0.4)
        require(all(marker in ideas["a3OneMinuteText"] for marker in ("Qwen2.5-7B-Instruct","ALFWorld","苹果","微波炉","垃圾桶","9 步完成","清洗勺子","餐桌","50 步失败","8 个候选","只有 1 个","隐藏旧任务","希望人工","下一步方案")), f"A-3 one-minute card lacks concrete task/update examples or actionable diagnosis: {ideas['a3OneMinuteText']}")
        require("STOP_CURRENT_SUBSTRATE_UPDATER_INCOMPETENT" not in ideas["a3OneMinuteText"] and "effective candidate fraction" not in ideas["a3OneMinuteText"], f"A-3 visible one-minute card leaked backend status jargon: {ideas['a3OneMinuteText']}")
        require(all(marker in ideas["p04OneMinuteText"] for marker in ("技能池","先升后降","污染临界点","删除最初污染源","派生技能","arXiv:2608.05810","最近工作直接覆盖")), f"P04/B-21 must explain the concrete skill-pool contamination scene, observed prior-work collision, and why the frozen problem closes: {ideas['p04OneMinuteText']}")
        require((ideas["parentConcreteComparisons"],ideas["supplementalConcreteComparisons"],ideas["pfConcreteComparisons"],ideas["concreteComparisonTables"]) == (17,5,2,24) and ideas["concreteComparisonRows"] >= 50 and ideas["concreteComparisonComplete"] is True, f"concrete method/baseline/result comparisons are incomplete: {ideas['parentConcreteComparisons']}/{ideas['supplementalConcreteComparisons']}/{ideas['pfConcreteComparisons']}/{ideas['concreteComparisonTables']}/{ideas['concreteComparisonRows']}/{ideas['concreteComparisonComplete']}")
        require(ideas["simpleMethodGuides"] == 24 and ideas["simpleMethodGuideCells"] == 96 and ideas["simpleMethodGuidesComplete"] is True, f"every formal simple baseline must explain input / mechanics / output / omitted complexity: guides={ideas['simpleMethodGuides']} cells={ideas['simpleMethodGuideCells']} complete={ideas['simpleMethodGuidesComplete']}")
        require(all(marker in ideas["simpleMethodGuideText"] for marker in ("CART 决策树每一层选择一个","source_gain>0、probe_harm=0、probe_mean≥0","状态差分法只保存","ILP（整数规划）","二元稀疏组测试","单调 DNF","枚举所有仍与当前证据相容的修复方案","Σ(类别数量×严重度)")), f"opaque simple baselines are still name-only rather than operationally explained: {ideas['simpleMethodGuideText']}")
        require(all(marker in ideas["text"] for marker in ("目标任务族更容易受更新影响","简单方法 +20 个百分点","少 35 个（47.9%）","简单规则少 16","简单方法 +16.67 个百分点","简单方法 +66.67 个百分点","复杂方法未运行","二元稀疏组测试","简单规则少 24 次（45.3%）","无数值差值；方法预演阶段已停止")), "representative concrete baseline designs or exact deltas are missing")
        require(all(marker in ideas["oneMinuteReaderText"] for marker in ("8 个候选 patch 只有 1 个真正让目标任务变好","24/24 个案例中找对最小故障集","97.5% 的准入决策相同","以后学习下一个新任务会变慢","真正的未来对照从未打开","普通重复或提示显著性")), "representative A-3/A-6/C-1/PF-1/G-1/Evidence-Echo one-minute briefing copy is missing")
        require(ideas["lifecycleCells"] == 130 and ideas["explicitLegacyP0Badges"] == 0 and ideas["formalAuthorityZero"] == 26 and ideas["parentActionCounts"] == {"NO_INTERNAL_ACTION":16,"MERGED_NO_STANDALONE_ACTION":6,"REOPEN_CONDITION_REQUIRED":4}, f"lifecycle/current-decision/action/authority separation failed: cells={ideas['lifecycleCells']} actions={ideas['parentActionCounts']} legacyP0={ideas['explicitLegacyP0Badges']} zeroAuthority={ideas['formalAuthorityZero']}")
        expected_parent_states={"A-1":"stop","A-2":"stop","A-3":"hold","A-5":"stop","B-1":"merge","B-2":"hold","B-3":"hold","C-1":"stop","C-4":"stop","D-1":"stop","D-2":"stop","E-1":"hold","E-2":"stop","F-1":"stop","F-3":"stop"}
        require(all(ideas["parentStatusByCode"].get(code)==state for code,state in expected_parent_states.items()), f"representative parent terminal states are wrong: {ideas['parentStatusByCode']}")
        filter_state = execute(session_id, """const visible=()=>[...document.querySelectorAll('.canonical-parent-item')].filter(x=>!x.hidden).length; const click=s=>document.querySelector('.canonical-filter-btn[data-canonical-status="'+s+'"]')?.click(); click('hold'); const hold=visible(); click('stop'); const stop=visible(); click('merge'); const merge=visible(); click('all'); return {hold,stop,merge,all:visible()};""")
        require(filter_state == {"hold":4,"stop":16,"merge":6,"all":26}, f"current parent scientific-state filter counts are wrong: {filter_state}")
        require((ideas["terminalSummary"].get("human_parents"), ideas["terminalSummary"].get("revived_to_p0"), ideas["absorbedChildCount"]) == (26,7,17), f"historical admission ledger or absorbed-child count is wrong: {ideas['terminalSummary']}/{ideas['absorbedChildCount']}")
        require(ideas["feedbackSummaries"] == 26, f"every discussed idea must expose one current summary, got {ideas['feedbackSummaries']}")
        require(ideas["humanOpinionBoxes"] == 26, f"all 26 discussed ideas must preserve the human opinion, got {ideas['humanOpinionBoxes']}")
        require(ideas["iterationBoxes"] == 17 and ideas["finalRefinementBoxes"] == 17, f"all 17 refined methods must show the final iteration and routing: {ideas['iterationBoxes']}/{ideas['finalRefinementBoxes']}")
        require(ideas["finalRefinementCounts"] == [4,16,6,0], f"current parent routing must be 4 HOLD / 16 STOP / 6 MERGED / 0 launchable, got {ideas['finalRefinementCounts']}")
        require(ideas["methodologyPanels"] == 1 and ideas["originalEvalGuides"] == 1, f"human-opinion audit/original-eval methodology panels are missing: {ideas['methodologyPanels']}/{ideas['originalEvalGuides']}")
        require(ideas["canonicalReviewCount"] == 26, f"canonical human-review map must cover all 26 ideas, got {ideas['canonicalReviewCount']}")
        require(ideas["humanRecommendationStats"] == [4,14,7,1], f"canonical human recommendation counts are wrong: {ideas['humanRecommendationStats']}")
        require(any('Original Idea 4' in label or '原讨论 Idea 4' in label or '原讨论 研究方向 4' in label for label in ideas["originalIdeaLabels"]), f"original discussion numbering is not visible: {ideas['originalIdeaLabels'][:5]}")
        require(ideas["concreteExamples"] == 26 and ideas["parentMergeRules"] >= 1, f"intuition/example or parent-merge UI gate is missing: {ideas['concreteExamples']}/{ideas['parentMergeRules']}")
        require(ideas["openDiscussedCards"] == 0 and ideas["openNewCards"] == 0, f"all idea cards must be collapsed by default, got {ideas['openDiscussedCards']}/{ideas['openNewCards']}")
        briefing_mode = execute(session_id, """const audit=document.querySelector('.briefing-mode-btn[data-briefing-mode="audit"]'); const brief=document.querySelector('.briefing-mode-btn[data-briefing-mode="brief"]'); audit?.click(); const opened={parents:document.querySelectorAll('.human-review-idea-card[open]').length,supplemental:document.querySelectorAll('.supplemental-idea-card[open]').length,pf:document.querySelectorAll('.paper-incubation-card[open]').length,closed:document.querySelectorAll('.closed-idea-card[open]').length,auditClass:document.documentElement.classList.contains('idea-audit-mode')}; brief?.click(); return {...opened,resetParents:document.querySelectorAll('.human-review-idea-card[open]').length,resetAuditClass:document.documentElement.classList.contains('idea-audit-mode')};""")
        require(briefing_mode == {"parents":26,"supplemental":7,"pf":9,"closed":expected_shadow_closed,"auditClass":True,"resetParents":0,"resetAuditClass":False}, f"briefing/full-audit switch is incomplete: {briefing_mode}")
        require(len(ideas["codes"]) == 26 and len(set(ideas["codes"])) == 26, f"group codes are missing or duplicated: {ideas['codes']}")
        require(all(code in ideas["codes"] for code in ("A-1","A-5","B-1","B-7","C-1","D-1","E-1","F-1","F-3")), f"expected stable group codes are missing: {ideas['codes']}")
        require(ideas["newGroups"] == ideas["openRelatedBanks"] == 10 and ideas["categoryRelatedBanks"] == ideas["openCategoryRelatedBanks"] == 9 and ideas["newCards"] == 7, f"related-direction, B-context, and numbered-closure banks must be visible by default while the E-7 paper chain renders as one ResearchItem handoff: {ideas['newGroups']}/{ideas['openRelatedBanks']}/{ideas['categoryRelatedBanks']}/{ideas['openCategoryRelatedBanks']}/{ideas['newCards']}")
        require(set(ideas["standaloneCodes"]) == {"A-6","A-7","B-8","B-9","B-10","E-3","E-4"}, f"standalone methods must have stable scientific-group codes: {ideas['standaloneCodes']}")
        require(not ideas["supplementalBlankPrimaryFields"], f"standalone method cards contain blank primary fields: {ideas['supplementalBlankPrimaryFields']}")
        require((ideas["newFinal"], ideas["newInspired"]) == (0, 0), f"legacy supplemental candidates must not remain active: {ideas['newFinal']}/{ideas['newInspired']}")
        require(ideas["mergedMethods"] >= 8, f"merged FINAL method provenance is not visible on discussed ideas: {ideas['mergedMethods']}")
        require(ideas["freshCollisionBlocks"] == 17 and ideas["freshCollisionLinks"] >= 40, f"fresh reducibility sources are missing from refined ideas: {ideas['freshCollisionBlocks']}/{ideas['freshCollisionLinks']}")
        require(all(marker in ideas["text"] for marker in ("ChronoMem","DeltaBox","CausalFlow")), "latest load-bearing collision sources are not visible in refined idea cards")
        require((ideas["incubationCards"],ideas["incubationStop"],ideas["incubationMerge"],ideas["incubationAdvance"],ideas["incubationRevise"],ideas["incubationBlock"],ideas["incubationOpen"]) == (9,5,4,0,0,0,0), f"Paper-first current rendering is wrong: {ideas['incubationCards']}/{ideas['incubationStop']}/{ideas['incubationMerge']}/{ideas['incubationAdvance']}/{ideas['incubationRevise']}/{ideas['incubationBlock']}/{ideas['incubationOpen']}")
        require((ideas["incubationSummary"].get("p0_authorized"),ideas["incubationSummary"].get("gpu_authorized")) == (0,0), f"incubation must remain outside P0/GPU authority: {ideas['incubationSummary']}")
        ds=ideas["designSummary"]
        require((ds.get("reviewed"),ds.get("advance_to_method_design"),ds.get("revise_paper_problem"),ds.get("merge_as_cross_cutting_invariant"),ds.get("stop_standalone_merge_risk_axis"),ds.get("local_validation_authorized")) == (4,1,1,1,1,0), f"Paper Design adjudication routing is stale: {ds}")
        require(ideas["designVerdicts"] == {"PF-2":"ADVANCE_TO_METHOD_DESIGN","PF-1":"REVISE_PAPER_PROBLEM","PF-4":"MERGE_AS_CROSS_CUTTING_INVARIANT","PF-6":"STOP_STANDALONE_MERGE_RISK_AXIS"}, f"Paper Design historical verdicts are wrong: {ideas['designVerdicts']}")
        require(ideas["pf1ProblemDecision"] == "STOP_PF1_STANDALONE_PROBLEM_MERGE_EVOLVABILITY_AUDIT" and not ideas["pf1ProblemActive"] and not ideas["pf1MethodAuthorized"], f"PF-1 final problem STOP is not rendered conservatively: {ideas}")
        require(ideas["pf2MethodDecision"] == "STOP_CURRENT_RSIC_METHOD_THESIS_KEEP_PROBLEM_PROTOCOL" and ideas["pf2MethodProblemStatus"] == "SURVIVES_AS_PROBLEM_AND_EVALUATION_PROTOCOL_ONLY" and not ideas["pf2MethodBlueprintAuthorized"] and not ideas["pf2MethodLocalAuthorized"], f"PF-2 method-level STOP is not rendered conservatively: {ideas}")
        require((ideas["pf357Summary"].get("reviewed"),ideas["pf357Summary"].get("stopped_standalone"),ideas["pf357Summary"].get("paper_design_authorized"),ideas["pf357Summary"].get("local_validation_authorized")) == (3,3,0,0), f"PF-3/5/7 final adjudication is stale: {ideas['pf357Summary']}")
        require(set(ideas["pf357Decisions"]) == {"PF-3","PF-5","PF-7"} and all(str(v).startswith("STOP_PF") for v in ideas["pf357Decisions"].values()), f"PF-3/5/7 decisions are wrong: {ideas['pf357Decisions']}")
        require((ideas["freshSummary"].get("drafts_reviewed"),ideas["freshSummary"].get("survivors"),ideas["freshSummary"].get("stopped"),ideas["freshSummary"].get("local_validation_authorized"),ideas["freshSummary"].get("p0_authorized")) == (41,0,41,0,0) and ideas["freshDecision"] == "NO_FRESH_SURVIVOR_CURRENT_SCAN" and ideas["freshZeroSurvivorPolicy"] and ideas["freshPanel"] == 1, f"fresh saturation scan must show 41 reviewed / 0 survivor / 41 stop with zero-survivor policy: {ideas}")
        sds=ideas["shadowDesignSummary"]
        require((sds.get("reviewed"),sds.get("advance_to_method_design"),sds.get("revise_paper_problem"),sds.get("stop_standalone")) == (2,0,1,1), f"shadow Search Portfolio design routing is stale: {sds}")
        require(int(sds.get("current_source_hard_veto_dead_ends") or 0) == int(sds.get("current_source_hard_veto_added_from_latest_run") or 0)+int(sds.get("current_source_hard_veto_added_from_terminal_run") or 0)+int(sds.get("current_source_hard_veto_inherited") or 0), f"current-source hard-veto memory accounting is inconsistent: {sds}")
        require(int(sds.get("semantic_blocker_dead_ends") or 0) == 0 and int(sds.get("semantic_hold_objects") or 0) == int(sds.get("semantic_hold_added_from_latest_run") or 0)+int(sds.get("semantic_hold_added_from_terminal_run") or 0)+int(sds.get("semantic_hold_inherited") or 0), f"semantic dead-end/HOLD memory accounting is inconsistent: {sds}")
        scientific_layer_total=sum(int(sds.get(key) or 0) for key in ("execution_stops","experiment_identifiability_stops","optimization_stops","operationalization_stops","method_realization_stops","assumption_scope_stops","core_principle_stops"))
        require(int(sds.get("near_miss_preflight_dead_ends") or 0) == int(sds.get("near_miss_current_primary_stops") or 0)+int(sds.get("near_miss_mature_theory_stops") or 0) and int(sds.get("near_miss_holds") or 0) == int(sds.get("near_miss_support_holds") or 0)+int(sds.get("near_miss_terminal_support_holds") or 0) and int(sds.get("shadow_closed_basins") or 0) == int(sds.get("problem_novelty_stops") or 0)+scientific_layer_total and int(sds.get("shadow_dead_end_objects") or 0) == int(sds.get("core_principle_dead_ends") or 0) == int(sds.get("core_principle_stops") or 0) and int(sds.get("broader_core_principle_falsifications") or 0) == 0, f"near-miss/canonical-failure-layer/search-closure/dead-end/HOLD accounting is inconsistent: {sds}")
        closed_rows=(ideas["currentShadowSearch"].get("closed_rows") or [])
        expected_closed=int(sds.get("shadow_closed_basins") or 0)
        require(ideas["closedAuditPanels"] == ideas["canonicalClosedArchives"] == ideas["openCanonicalClosedArchives"] == ideas["closedAuditRows"] == 0, f"legacy closed-candidate archive tables must be removed: panels={ideas['closedAuditPanels']} archives={ideas['canonicalClosedArchives']} rows={ideas['closedAuditRows']}")
        require(ideas["closedIdeaBanks"] == ideas["openClosedIdeaBanks"] == 5 and ideas["closedIdeaCards"] == expected_shadow_closed and ideas["mergedClosureRows"] == 3 and ideas["closedIdeaCards"] + ideas["mergedClosureRows"] == expected_closed == len(closed_rows), f"all closure decisions must be represented as canonical numbered cards plus three merges: banks={ideas['closedIdeaBanks']} cards={ideas['closedIdeaCards']} expected_cards={expected_shadow_closed} merged={ideas['mergedClosureRows']} expected={expected_closed}")
        require(len(ideas["closedIdeaCodes"]) == len(set(ideas["closedIdeaCodes"])) == expected_shadow_closed and set(ideas["closedIdeaCodes"]) == expected_closed_codes and "B-21" in ideas["closedIdeaCodes"] and "SHADOW-P04-C01" in ideas["closedIdeaSources"], f"numbered stopped-idea codes are incomplete, unstable, duplicated, or missing P04/B-21: actual={ideas['closedIdeaCodes']} expected={sorted(expected_closed_codes)}")
        require(len(ideas["allResearchObjectCodes"]) == len(set(ideas["allResearchObjectCodes"])) == expected_portfolio, f"every deduplicated research object must have one unique A-G code: count={len(ideas['allResearchObjectCodes'])} expected={expected_portfolio} codes={ideas['allResearchObjectCodes']}")
        require(not ideas["closedIdeaBlankPrimaryFields"], f"numbered stopped-idea cards contain blank primary fields: {ideas['closedIdeaBlankPrimaryFields']}")
        require(ideas["closedAuditReasonsAllZh"] and ideas["closedAuditReopensAllZh"], "all separately numbered closed-candidate stop reasons and reopen conditions must render in Chinese")
        require((ideas["statusOuterTracks"],ideas["statusCopyTracks"],ideas["statusMetricTracks"],ideas["statusMetricCount"]) == (1,2,5,10), f"current research status must render as title/message row plus full-width five-column metrics row: {ideas['statusOuterTracks']}/{ideas['statusCopyTracks']}/{ideas['statusMetricTracks']}/{ideas['statusMetricCount']}")
        pa01_closed=next((row for row in closed_rows if row.get("candidate_id")=="PA-01-EVIDENCE-ECHO"),{})
        pace_closed=next((row for row in closed_rows if row.get("candidate_id")=="PA-06-PACE-MECHANISM-REDESIGN-IDENTIFIABILITY"),{})
        require(pa01_closed.get("failure_layer")=="method_realization" and pa01_closed.get("experiment_run_for_this_readjudication") is True and pa01_closed.get("experiment_alone_authorizes_closure") is False, f"PA-01 must remain experiment-informed but method-realization scoped, not experiment-failed principle: {pa01_closed}")
        require(pace_closed.get("failure_layer")=="core_principle" and pace_closed.get("principle_update_allowed") is True and pace_closed.get("broader_core_principle_falsified") is False, f"PACE must be a scoped core-principle stop without benchmark-level falsification: {pace_closed}")
        require(len(ideas["closedIdeaBankLabels"]) == 5 and all(label == "已停止的编号研究方向" for label in ideas["closedIdeaBankLabels"]), f"numbered stopped-idea bank labels are missing: {ideas['closedIdeaBankLabels']}")
        require(all(marker in ideas["text"] for marker in ("负实验是否决定关闭","实验前问题/新颖性","实验可辨识性","方法实现/独立机制")), "numbered stopped-idea failure-layer explanations are not visible in the Chinese Paper Ideas view")
        require(ideas["shadowDesignPolicy"].get("source_is_shadow_search_portfolio") is True and ideas["shadowDesignPolicy"].get("shadow_queue_has_zero_paper_design_authority") is True and ideas["shadowDesignPolicy"].get("cannot_grant_or_revoke_live_paper_design_authority") is True, f"shadow Paper Design authority boundary is missing: {ideas['shadowDesignPolicy']}")
        require((ideas["shadowQueueSummary"].get("counterfactual_problem_gate_passed"),ideas["shadowQueueSummary"].get("live_paper_design_eligible")) == (2,0), f"shadow queue must expose 2 historical counterfactual passes and 0 live eligibility: {ideas['shadowQueueSummary']}")
        latest=ideas["shadowLatestSummary"]
        rendered_latest=ideas["shadowLatestRun"] or {}
        require(rendered_latest.get("run_id") == expected_shadow_latest.get("run_id") and latest == expected_shadow_summary, f"latest shadow browser projection diverges from generated state: rendered={rendered_latest} expected={expected_shadow_latest}")
        latest_authority=rendered_latest.get("authority") or {}
        require(rendered_latest.get("status")=="SHADOW_TERMINAL_COMPLETE" and rendered_latest.get("scientific_authority") is False and (latest.get("current_source_missing"),latest.get("live_paper_design_eligible"),latest.get("terminal_shadow_survivors"),ideas["shadowLatestPanels"]) == (0,0,0,1) and all(latest_authority.get(key) is False for key in ("live_problem_gate","paper_design","method","experiment","p0","gpu")), f"latest shadow must be terminal-complete, zero-live-authority, and rendered once: {rendered_latest}/{ideas['shadowLatestPanels']}")
        shadow_admission=ideas["shadowAdmission"];shadow_admission_summary=shadow_admission.get("summary") or {}
        expected_shadow_admission=expected_state.get("paper_first_shadow_search_admission") or {};expected_shadow_admission_summary=expected_shadow_admission.get("summary") or {}
        require(shadow_admission.get("scientific_authority") is False and int(shadow_admission_summary.get("automatic_provider_calls_authorized") or 0)==0 and ideas["shadowAdmissionPanels"] == 1, f"shadow next-run admission authority/accounting is invalid: {shadow_admission}/{ideas['shadowAdmissionPanels']}")
        require(shadow_admission.get("status")==expected_shadow_admission.get("status") and all(shadow_admission_summary.get(key)==expected_shadow_admission_summary.get(key) for key in ("canonical_transaction_closed","same_source_transaction","same_discovery_operator_version","operator_upgrade_recompile","qualification_allowed","automatic_provider_calls_authorized")), f"shadow admission panel diverges from generated research-system state: rendered={shadow_admission} expected={expected_shadow_admission}")
        if shadow_admission_summary.get("qualification_allowed") is True:
            require(str(shadow_admission.get("status") or "").startswith("READY_FOR_") and (shadow_admission_summary.get("same_source_transaction") is False or shadow_admission_summary.get("operator_upgrade_recompile") is True), f"shadow qualification may open only for a new source transaction or operator upgrade: {shadow_admission}")
        if shadow_admission.get("status") == "SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL":
            require(shadow_admission_summary.get("same_source_transaction") is True and shadow_admission_summary.get("same_discovery_operator_version") is True and shadow_admission_summary.get("qualification_allowed") is False, f"same-source current-operator terminal shadow must skip: {shadow_admission}")
        require((ideas["sp15SupportSummary"].get("primary_or_author_releases_audited"),ideas["sp15SupportSummary"].get("query_level_identifiability_units"),ideas["sp15SupportSummary"].get("method_design_authorized")) == (5,0,0), f"SP-15 shadow identifiability support must remain 5 sources / 0 units / 0 method authority: {ideas['sp15SupportSummary']}")
        require((ideas["sp15SupportDiagnosis"].get("stop_class"),ideas["sp15SupportDiagnosis"].get("failure_layer"),ideas["sp15SupportDiagnosis"].get("failure_subtype")) == ("SUPPORT_STOP","experiment_identifiability","NO_MATCHED_QUERY_IDENTIFIABILITY_UNIT") and ideas["sp15SupportDiagnosis"].get("principle_dead_end_certified") is False and ideas["sp15SupportDiagnosis"].get("principle_update_allowed") is False, f"SP-15 missing matched support must stay a reopenable experiment-identifiability SUPPORT_STOP, not a principle dead-end: {ideas['sp15SupportDiagnosis']}")
        shadow_render_markers=(
            "影子搜索组合 · 回溯式论文设计审查",
            "影子搜索组合 · 最新当前来源终态",
            "影子搜索 · 下一轮准入",
            f"运行={expected_shadow_latest.get('run_id')}",
            f"控制快照={expected_shadow_latest.get('stage_runner_required_schema') or 'legacy'}/{str(expected_shadow_latest.get('control_snapshot_sha256') or '')[:12] or 'unbound'}",
            f"执行截断={int(expected_shadow_summary.get('formulation_execution_censored_branches') or 0)}",
            f"待归约={int(expected_shadow_summary.get('formulation_reduction_pending') or 0)}",
            f"问题证伪器资格={int(expected_shadow_summary.get('problem_falsifier_eligible') or 0)}",
            f"证据库存请求={int(expected_shadow_summary.get('problem_falsifier_inventory_requested') or 0)}",
            f"证据合格={int(expected_shadow_summary.get('problem_falsifier_support_qualified') or 0)}",
            f"暂缓={int(expected_shadow_summary.get('problem_falsifier_hold_support_unavailable') or 0)}",
            f"已执行={int(expected_shadow_summary.get('problem_falsifier_executed') or 0)}",
        )
        require(all(marker in ideas["text"] for marker in shadow_render_markers), f"current shadow latest-run Chinese rendering is inconsistent; missing={[m for m in shadow_render_markers if m not in ideas['text']]}")
        chinese_reader_markers=(
            "相同候选更新池",
            "最新可归约性审查",
            "最近工作",
            "正式问题发现 · 当前状态",
            "影子搜索组合 · 回溯式论文设计审查",
            "影子搜索组合 · 最新当前来源终态",
            "影子搜索 · 下一轮准入",
            "SP-15 影子修订 · 可辨识性证据库存",
            "仅诊断（DIAGNOSTIC ONLY）",
            "停止 PF-1 独立论文",
            "通过正式问题检查的新研究问题",
            "当前科研进展 · 1min 结论版",
            "终态子账本",
            "A–G",
            "局部反例记忆修复",
        )
        require(all(marker in ideas["text"] for marker in chinese_reader_markers), f"paper-ideas Chinese reader layer is incomplete; missing={[m for m in chinese_reader_markers if m not in ideas['text']]}")
        english_reader_leaks=(
            "same candidate update pool",
            "same frozen probe suite",
            "Frozen heterogeneous open-weight critic plus environment/tool ground truth",
            "Fresh reducibility",
            "Live canonical problem discovery",
            "Shadow Search Portfolio · retrospective Paper Design audit",
            "Shadow Search Portfolio · latest current-source terminal",
            "Shadow Search · next-run admission",
            "Paper Design 二审",
            "PF-2 Method Design 会诊",
            "历史 Method 诊断归档",
            "本轮历史 Fresh 扫描",
            "standalone STOP",
            "当前方法 thesis 已终止",
            "正式活跃 Idea",
            "Memory 效应现象",
            "Shadow 暂缓",
            "local-counterexample-memory-repair",
            "Revise and re-audit the paper problem",
            "Archive PF-1 standalone",
            "Generate one common candidate-task pool",
            "terminal collision as standalone paper; integrate as protocol-validity control",
        )
        require(not any(marker in ideas["text"] for marker in english_reader_leaks), f"paper-ideas Chinese view regressed to English explanatory prose: {[m for m in english_reader_leaks if m in ideas['text']]}")
        require(all(marker in ideas["text"] for marker in ("PF-1","PF-2","PF-3","PF-4","PF-5","PF-6","PF-7","STOP_PF1_STANDALONE_PROBLEM_MERGE_EVOLVABILITY_AUDIT","STOP_CURRENT_RSIC_METHOD_THESIS_KEEP_PROBLEM_PROTOCOL","STOP_PF3_STANDALONE_MERGE_COMPRESSION_LIFECYCLE_CONTROL","STOP_PF5_STANDALONE_MERGE_DIFFERENTIAL_VERIFICATION_COMPONENT","STOP_PF7_STANDALONE_MERGE_EVIDENCE_IMPACT_REVALIDATION_COMPONENT")), "Paper-first terminal/fresh-saturation verdicts are not visible")
        pmd=ideas["prematureMethodSummary"]
        require((pmd.get("directions"),pmd.get("completed_diagnostics"),pmd.get("design_holds"),pmd.get("same_information_reducibility_findings"),pmd.get("hidden_executions"),pmd.get("scientifically_authorized")) == (2,2,1,2,0,0) and ideas["prematureMethodPanels"] == 2, f"premature Method diagnostics must be visible as two non-authoritative PF-1/PF-4 archives: {pmd}/{ideas['prematureMethodPanels']}")
        require("STOP_MATCHED_POST_ONLY_EQUIVALENT" in ideas["text"] and "STOP_MATCHED_SOFT_SCALAR_EQUIVALENT" in ideas["text"] and "DIAGNOSTIC ONLY" in ideas["text"], "Paper-first diagnostic archive markers are not visible")
        require("历史人工意见与方法迭代" in ideas["text"] and ideas["newCards"] == 7 and ideas["absorbedChildCount"] == 17, "historical-lineage/current idea summary or standalone-method rendering is missing")

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

        navigate("/paper-ideas.html?research=A-3", 3)
        ensure_language("zh")
        a3_focus = execute(session_id, """const card=document.getElementById('idea-a-3'); return {exists:!!card,open:card?.open===true,focused:card?.classList.contains('research-item-url-focus')===true,fieldLinks:card?.querySelectorAll('.research-item-field-lineage a').length||0,timelineHref:[...card?.querySelectorAll('.research-item-field-lineage a')||[]].map(x=>x.getAttribute('href')||'').find(x=>x.includes('research-timeline.html?research=A-3'))||'',text:card?.querySelector('.research-item-field-lineage')?.textContent||''};""")
        require(a3_focus["exists"] and a3_focus["open"] and a3_focus["focused"] and a3_focus["fieldLinks"] >= 3 and a3_focus["timelineHref"].endswith("research-timeline.html?research=A-3") and "D1" in a3_focus["text"] and "D4" in a3_focus["text"], f"Research Portfolio deep link must focus A-3 and expose its historical-field/current-map/timeline bridge: {a3_focus}")

        navigate("/experiments.html", 6)
        experiments = execute(session_id, """return {
          chapters: document.querySelectorAll('.page-chapter').length,
          terminalPortfolio: document.querySelectorAll('#terminal-experiment-portfolio').length,
          currentPaperEvidence: document.querySelectorAll('#current-paper-evidence-status').length,
          currentStatus: window.CURRENT_RESEARCH_STATUS?.headline || {},
          currentPaperTrack: window.CURRENT_RESEARCH_STATUS?.leading_paper_track || {},
          paceStatus: (window.CURRENT_RESEARCH_STATUS?.fresh_phenomenon_portfolio?.rows || []).find(x => x.candidate_id === 'PA-06-PACE-MECHANISM-REDESIGN-IDENTIFIABILITY') || {},
          terminalRows: document.querySelectorAll('.terminal-experiment-row').length,
          terminalStarted: document.querySelectorAll('.terminal-experiment-row[data-current-p0-started="1"]').length,
          terminalPending: document.querySelectorAll('.terminal-experiment-row[data-current-p0-started="0"]').length,
          terminalP0: document.querySelectorAll('.terminal-experiment-row[data-terminal-lifecycle="p0"]').length,
          terminalP0Ready: document.querySelectorAll('.terminal-experiment-row[data-terminal-lifecycle="p0-ready"]').length,
          batchPanel: document.querySelectorAll('.experiment-batch20').length,
          batchSummary: window.P0_REVIVED_BATCH_F0?.summary || {},
          postC2Panel: document.querySelectorAll('.paper-first-c2-terminal').length,
          postC2Decision: window.PAPER_FIRST_POST_C2_ADJUDICATION?.decision || '',
          postC2ScienceWorldDecision: window.PAPER_FIRST_POST_C2_ADJUDICATION?.scienceworld_scope_evidence?.f0_decision || '',
          postC2C3Locked: Boolean(window.PAPER_FIRST_POST_C2_ADJUDICATION?.authority?.C3_locked),
          postC2FullAuthorized: Boolean(window.PAPER_FIRST_POST_C2_ADJUDICATION?.authority?.full_experiment_authorized),
          prematurePfF0Panel: document.querySelectorAll('.paper-first-premature-f0-audit').length,
          prematurePfF0Summary: window.RESEARCH_SYSTEM_STATE?.paper_first_p0_f0?.summary || {},
          prematurePfMethodPanel: document.querySelectorAll('.paper-first-premature-method-audit').length,
          prematurePfMethodSummary: window.PAPER_FIRST_PREMATURE_METHOD_DIAGNOSTICS?.summary || window.RESEARCH_SYSTEM_STATE?.paper_first_premature_method_diagnostics?.summary || {},
          paperFirstP0Authority: window.RESEARCH_SYSTEM_STATE?.paper_first_p0_authority?.summary || {},
          auditQueue: document.querySelectorAll('#terminal-unstarted-audit').length,
          auditItems: document.querySelectorAll('.terminal-audit-item').length,
          admissionPanel: document.querySelectorAll('#p0-admission-settings').length,
          admissionRows: document.querySelectorAll('.p0-admission-table tbody tr').length,
          offlinePanel: document.querySelectorAll('#p0-offline-qualification').length,
          offlineSummary: window.P0_OFFLINE_QUALIFICATION?.summary || {},
          realizabilitySummary: window.P0_REALIZABILITY_SUITE?.summary || {},
          b10Decision: window.P0_B10_CPU?.decision || '',
          a1RepairDecision: window.P0_A1_SOFT_AUDIT_F0?.decision || '',
          a2RepairDecision: window.P0_A2_EVIDENCE_DEPTH_F0?.decision || '',
          a3Decision: window.P0_A3_SUBSTRATE_STOP?.decision || '',
          a4Decision: window.P0_A4_COMPOSITION_CPU?.decision || '',
          a5Decision: window.P0_A5_HISTORY_CPU?.decision || '',
          a6Decision: window.P0_A6_CPU?.decision || '',
          a7Decision: window.P0_A7_COUNTERFACTUAL_CPU?.decision || '',
          b2Decision: window.P0_B2_SUPPORT_STOP?.decision || '',
          b3Decision: window.P0_B3_INTERFERENCE_CPU?.decision || '',
          b3RuntimeDecision: window.P0_B3_INTERFERENCE_CPU?.runtime_preflight_snapshot?.decision || '',
          b3SupportDecision: window.P0_B3_FRESH_SUPPORT_STOP?.decision || '',
          b3RealStatus: window.P0_B3_REAL_CINTERACTION?.status || '',
          b5Decision: window.P0_B5_APPLICABILITY_CPU?.decision || '',
          b6Decision: window.P0_B6_MEMORY_UTILITY_CPU?.decision || '',
          c2Decision: window.P0_C2_EVALUATOR_CPU?.decision || '',
          d1Decision: window.P0_D1_MINIMAL_CURRICULUM_CPU?.decision || '',
          e1Decision: window.P0_E1_EDIT_TABLE_STOP?.decision || '',
          e2Decision: window.P0_E2_WORKFLOW_CPU?.decision || '',
          e3Decision: window.P0_E3_STATEFUL?.decision || window.P0_E3_REAL_API?.decision || '',
          e4Decision: window.P0_E4_PERMISSION_CPU?.decision || '',
          p0StopRows: document.querySelectorAll('.terminal-exp-p0-stop').length,
          decisionLedgerSummary: window.RESEARCH_SYSTEM_STATE?.p0_decision_ledger?.summary || window.P0_DECISION_LEDGER?.summary || {},
          admissionSummary: window.P0_ADMISSION_STATE?.summary || {},
          legacyArchives: document.querySelectorAll('.experiment-legacy-archive').length,
          masterHeaders: document.querySelectorAll('.experiment-master-table thead th').length,
          currentEvidenceHub: document.querySelectorAll('#experiment-current-evidence').length,
          currentEvidenceDisclosures: document.querySelectorAll('#experiment-current-evidence .experiment-evidence-disclosure').length,
          traceabilityHub: document.querySelectorAll('#experiment-traceability-archive').length,
          traceabilityDisclosures: document.querySelectorAll('#experiment-traceability-archive .experiment-legacy-archive').length,
          openEvidenceDisclosures: document.querySelectorAll('#experiment-current-evidence .experiment-evidence-disclosure[open]').length,
          openTraceabilityDisclosures: document.querySelectorAll('#experiment-traceability-archive .experiment-legacy-archive[open]').length,
          chapterDirectPanels: [...document.querySelectorAll('.page-chapter')].map(ch=>ch.querySelectorAll(':scope > .panel').length),
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
          portfolioBackLinks: [...document.querySelectorAll('a')].filter(x=>(x.getAttribute('href')||'')==='paper-ideas.html').length,
          text: document.body.textContent || ''
        };""")
        require(experiments["chapters"] == 3, f"experiments page must have three chapters, got {experiments['chapters']}")
        require((experiments["terminalPortfolio"],experiments["terminalRows"],experiments["terminalP0"],experiments["terminalP0Ready"]) == (1,27,27,0), f"terminal experiment portfolio is not aligned with validated Paper Ideas: {experiments}")
        require(experiments["currentPaperEvidence"] == 1, f"current STRI paper-evidence panel is missing: {experiments}")
        ecs=experiments["currentStatus"]; ep=experiments["currentPaperTrack"]
        current_keys=("paper_ready","paper_quality_hold","paper_quality_evidence_debt","canonical_live_ideas","launchable_formal_experiments","shadow_qualification_ready","fresh_active_f0","fresh_design_ready_f0","fresh_execution_holds","fresh_support_holds","fresh_ready_problem_review","method_authorized","gpu_authorized","shadow_dead_ends","shadow_holds")
        require(all(ecs.get(key) == expected_headline.get(key) for key in current_keys), f"experiments current-status snapshot diverges from generated/current-research-status.json: rendered={ecs} expected={expected_headline}")
        require((ep.get("paper_id"),ep.get("status"),ep.get("submission_status"),ep.get("claims_supported"),ep.get("claims_total"),ep.get("paper_quality_v2_passed"),ep.get("paper_quality_content_addressed_completion"),ep.get("paper_quality_content_addressed_files"),ep.get("paper_quality_evidence_debt"),ep.get("new_gpu_evidence_required")) == ("STRI","READY_NARROW_ICLR","READY_TO_SUBMIT_PENDING_HUMAN_AUTHOR_SIGNOFF_AND_OPENREVIEW",3,3,True,True,29,0,False), f"STRI paper-quality projection is stale: {ep}")
        pace=experiments["paceStatus"]; pace_child=pace.get("historical_child") or {}
        require((pace.get("status"),pace.get("support_status"),pace.get("stop_class"),pace.get("benchmark_level_dead_end_certified"),pace.get("revised_f0_authorized"),pace.get("provider_formulation_review_required")) == ("STOP_REDUCTION","PRINCIPLE_CLOSED_GENERIC_PROGRAM_SYNTHESIS_REDUCTION","PRINCIPLE_STOP",False,False,False), f"PACE current scoped principle status regressed: {pace}")
        require((pace_child.get("status"),pace_child.get("stop_class"),pace_child.get("principle_dead_end_certified")) == ("ARCHIVED_INVALID_OPERATIONALIZATION","PROTOCOL_STOP",False), f"PACE historical rank-reversal child regressed into a scientific negative: {pace_child}")
        require(all(marker in experiments["text"] for marker in ("PACE","为什么旧实验作废","PRINCIPLE_STOP","ARCHIVED_INVALID_OPERATIONALIZATION","PROTOCOL_STOP")), "PACE STOP taxonomy / invalid-operationalization boundary is not visible in the Chinese experiments view")
        require((experiments["terminalStarted"],experiments["terminalPending"],experiments["auditQueue"],experiments["auditItems"]) == (27,0,0,0), f"historical execution-artifact split is wrong: {experiments}")
        require(experiments["batchPanel"] == 1 and (experiments["batchSummary"].get("parent_p0"),experiments["batchSummary"].get("reused_existing_p0"),experiments["batchSummary"].get("fresh_cpu_f0"),experiments["batchSummary"].get("fresh_matched_simplification_stop"),experiments["batchSummary"].get("fresh_upstream_hold"),experiments["batchSummary"].get("gpu_queue_candidates_before_economy")) == (20,13,7,7,0,0), f"20-Idea P0 batch is missing or stale: {experiments['batchSummary']}")
        require(experiments["postC2Panel"] == 1 and experiments["postC2Decision"] == "STOP_CURRENT_CONTROLLED_MEDIATOR_PAPER_MECHANISM" and experiments["postC2ScienceWorldDecision"] == "SYMMETRIC_F0_HOLD" and experiments["postC2C3Locked"] and not experiments["postC2FullAuthorized"], f"paper-first C2 terminal authority is not rendered conservatively: {experiments}")
        require(experiments["prematurePfF0Panel"] == 1 and experiments["prematurePfF0Summary"].get("quarantined") == 4 and experiments["prematurePfF0Summary"].get("scientifically_authorized") == 0 and experiments["paperFirstP0Authority"].get("promoted") == 0, f"premature PF F0 must remain visible but quarantined from P0/scientific authority: {experiments}")
        pmdx=experiments["prematurePfMethodSummary"]
        require(experiments["prematurePfMethodPanel"] == 1 and (pmdx.get("completed_diagnostics"),pmdx.get("same_information_reducibility_findings"),pmdx.get("hidden_executions"),pmdx.get("scientifically_authorized"),pmdx.get("p0_lifecycle_mutations")) == (2,2,0,0,0), f"premature PF Method results must remain visible only as non-authoritative diagnostic evidence: {experiments}")
        require(experiments["admissionPanel"] == 1 and experiments["admissionRows"] >= 16 and experiments["admissionSummary"].get("active_p0") == 27 and experiments["admissionSummary"].get("transitioned_from_p0_ready") == 16 and experiments["admissionSummary"].get("revived_from_drop") == 7 and experiments["admissionSummary"].get("settings_complete") == 27, f"P0 admission/settings panel is incomplete: {experiments}")
        require(experiments["offlinePanel"] == 1 and experiments["offlineSummary"].get("ideas") == 16 and experiments["offlineSummary"].get("checks_failed",0) >= 15 and experiments["offlineSummary"].get("checks_synthetic_pass") == 14 and experiments["offlineSummary"].get("gpu0_stop") == 16 and experiments["offlineSummary"].get("gpu0_hold_or_conditional") == 0, f"offline qualification panel/state is incomplete: {experiments}")
        require(experiments["realizabilitySummary"].get("audited") == 14 and experiments["realizabilitySummary"].get("synthetic_pass") == 14, f"synthetic realizability summary is wrong: {experiments}")
        require(experiments["a1RepairDecision"] == "STOP_REPAIR_SOFT_AUDIT_SIMPLE_TRIAGE_DOMINATES" and experiments["a2RepairDecision"] == "STOP_REPAIR_FIXED_HORIZON_DOMINATES" and experiments["a3Decision"] == "STOP_CURRENT_SUBSTRATE_UPDATER_INCOMPETENT" and experiments["a4Decision"] == "STOP_DIRECT_ORDER_AWARE_RISK_EQUIVALENT" and experiments["a5Decision"] == "STOP_MATCHED_GENERIC_STATE_DIFF_DOMINATES" and experiments["a6Decision"] == "STOP_MATCHED_GROUP_TESTING_EQUIVALENT" and experiments["a7Decision"] == "STOP_MATCHED_SHALLOW_RULE_EQUIVALENT", f"A-family terminal decisions are not visible: {experiments}")
        require(experiments["b2Decision"] == "STOP_CURRENT_SUBSTRATE_CONCLUSION_CHANGE_SUPPORT_INSUFFICIENT" and experiments["b3SupportDecision"] == "STOP_CURRENT_SUBSTRATE_FRESH_CINTERACTION_SUPPORT_INSUFFICIENT" and experiments["b3RealStatus"] in {"invalid-development","missing"} and experiments["b5Decision"] == "STOP_COMPLEXITY_MATCHED_ILP_EQUIVALENT" and experiments["b6Decision"] == "STOP_RECENCY_FREQUENCY_POLICY_DOMINATES" and experiments["b10Decision"] == "STOP_MATCHED_NARY_EQUIVALENT", f"B-family terminal decisions are not visible: {experiments}")
        require(experiments["c2Decision"] == "STOP_SIMPLE_ANCHOR_RESIDUAL_CALIBRATION_EQUIVALENT" and experiments["d1Decision"] == "STOP_MATCHED_INTERSECTION_FILTER_EQUIVALENT" and experiments["e1Decision"] == "STOP_CURRENT_EDIT_TABLE_RANKING_DEGENERATE" and experiments["e2Decision"] == "STOP_MATCHED_E1_DIRECT_EDIT_EQUIVALENT" and experiments["e3Decision"] == "STOP_STATEFUL_DETERMINISTIC_PEX_CEILING" and experiments["e4Decision"] == "STOP_MATCHED_BOOLEAN_RULE_EQUIVALENT", f"C/D/E terminal decisions are not visible: {experiments}")
        require(experiments["decisionLedgerSummary"].get("active_p0") == 27 and experiments["decisionLedgerSummary"].get("experiment_stopped") == 24 and experiments["decisionLedgerSummary"].get("upstream_hold") == 1 and experiments["decisionLedgerSummary"].get("economy_blocked") == 0 and experiments["decisionLedgerSummary"].get("method_admission_blocked") == 0 and experiments["decisionLedgerSummary"].get("launchable") == 0, f"unified Decision Ledger must cover only 27 validated P0 contracts with 0 launchable: {experiments['decisionLedgerSummary']}")
        require(experiments["p0StopRows"] >= 16, f"terminal STOP styling is unexpectedly incomplete after the four-direction iteration overlay: {experiments['p0StopRows']}")
        require(experiments["legacyArchives"] == 3, f"legacy experiment evidence must live in exactly three traceability drawers: {experiments['legacyArchives']}")
        require(experiments["masterHeaders"] == 4, f"the current experiment table must have exactly four non-duplicative columns, got {experiments['masterHeaders']}")
        require((experiments["currentEvidenceHub"],experiments["currentEvidenceDisclosures"],experiments["traceabilityHub"],experiments["traceabilityDisclosures"]) == (1,2,1,3), f"status/evidence/history hierarchy is wrong: {experiments}")
        require((experiments["openEvidenceDisclosures"],experiments["openTraceabilityDisclosures"]) == (0,0), f"evidence/history drawers must be collapsed by default: {experiments}")
        require(experiments["chapterDirectPanels"] == [1,1,1], f"each experiments chapter must expose one primary panel only: {experiments['chapterDirectPanels']}")
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
        diagnosis_set=set(experiments["diagnosisTypes"])
        canonical_diagnoses={"representation-signal-mismatch","no-label-variation","matched-simplification-tie","objective-claim-mismatch"}
        infra_only=diagnosis_set=={"infrastructure-error"}
        require(diagnosis_set == canonical_diagnoses or infra_only, f"unexpected experiment diagnoses: {experiments['diagnosisTypes']}")
        require(experiments["iterationScaleUp"] == 0 and ((not infra_only and experiments["iterationBeliefUpdates"] == 1) or (infra_only and experiments["iterationBeliefUpdates"] == 0)), f"diagnosis policy is inconsistent with available historical evidence: {experiments['iterationScaleUp']}/{experiments['iterationBeliefUpdates']}")
        require(experiments["runtimeGpu"] >= 1 and experiments["runtimeModelReady"] and experiments["runtimeSupported"] == 2, f"runtime preflight lost GPU/model/harness readiness: {experiments}")
        require((experiments["runtimeReady"] and experiments["runtimeBlockers"] == 0) or ((not experiments["runtimeReady"]) and experiments["runtimeBlockers"] >= 1), f"runtime readiness/blocker state is inconsistent: {experiments}")
        require(experiments["launchReady"] == (experiments["runtimeReady"] and experiments["smokeReady"]), f"P0 launch must require both runtime and smoke readiness: {experiments}")
        require((experiments["p0AuthorizedState"], experiments["p1AuthorizedState"]) == (0, 0), f"live authorization state is wrong: {experiments['p0AuthorizedState']}/{experiments['p1AuthorizedState']}")
        require(("结果与效果总表" in experiments["text"] or "Results and effect snapshot" in experiments["text"]) and ("人工审批与下一阶段锁" in experiments["text"] or "Human approvals and next-phase locks" in experiments["text"]), "experiment result/approval sections are not visible")
        require(("Pre-P0" in experiments["text"] and ("实验诊断与原子修复树" in experiments["text"] or "Experiment diagnosis and atomic repair tree" in experiments["text"])), "Pre-P0 or experiment diagnosis/repair section is not visible")
        require("科学结论统一回到 ResearchItem" in experiments["text"] and experiments["portfolioBackLinks"] >= 1, "experiments page must stay a deep technical audit with an explicit route back to the Research Portfolio")

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
          temporalPaper: (window.PAPER_REGISTRY?.papers || []).find(x=>x.paper_id==='D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK') || {},
          paperRegistrySummary: window.PAPER_REGISTRY?.summary || {},
          paperRegistryPanel: document.querySelectorAll('#paper-registry-overview').length,
          paperRegistryCards: document.querySelectorAll('.paper-registry-card').length,
          paperRegistryIds: [...document.querySelectorAll('.paper-registry-card')].map(x=>x.dataset.paperId||''),
          paperRegistryStages: Object.fromEntries([...document.querySelectorAll('.paper-registry-card')].map(x=>[x.dataset.paperId||'',x.dataset.paperStage||''])),
          paperRegistryNextActions: Object.fromEntries([...document.querySelectorAll('.paper-registry-card')].map(x=>[x.dataset.paperId||'',x.dataset.nextAction||''])),
          currentDynamic: window.CURRENT_RESEARCH_STATUS?.stri_dynamic_evidence || {},
          paperAcceptance: (window.RESEARCH_SYSTEM_STATE?.paper_acceptance?.ledger_index?.entries || []).find(row=>row.paper_id==='STRI-ICLR2027') || {},
          agentSafetyAcceptance: (window.RESEARCH_SYSTEM_STATE?.paper_acceptance?.ledger_index?.entries || []).find(row=>row.paper_id==='AGENT-SAFETY-R9') || {},
          paperAcceptanceSummary: window.RESEARCH_SYSTEM_STATE?.paper_acceptance?.summary || {},
          acceptancePanels: document.querySelectorAll('.paper-acceptance-workflow').length,
          acceptanceStages: document.querySelectorAll('.paper-acceptance-stage').length,
          submissionDownloads: [...document.querySelectorAll('#selected-stri-current .current-status-downloads a')].map(a=>a.getAttribute('href')||''),
          agentSafetyDownloads: [...document.querySelectorAll('.paper-registry-card[data-paper-id="AGENT-SAFETY-R9"] .current-status-downloads a')].map(a=>a.getAttribute('href')||''),
          agentSafetyCardText: document.querySelector('.paper-registry-card[data-paper-id="AGENT-SAFETY-R9"]')?.textContent || '',
          title: document.title,
          text: document.body.textContent || ''
        };""")
        require(selected["currentSTRI"] == 1 and selected["currentAgentSafety"] == 1 and selected["archive"] == 1 and not selected["archiveOpen"] and selected["acceptancePanels"] == 5 and selected["acceptanceStages"] == 60, f"PaperRegistry must render five current paper details, five independent 12-stage acceptance workflows, and one collapsed historical archive: {selected}")
        require(len(selected["paperTocRoots"]) == 5 and "STRI" in selected["paperTocRoots"][0] and "Agent Safety R9" in selected["paperTocRoots"][1] and any("Temporal Skills" in x for x in selected["paperTocRoots"]) and all(count >= 3 for count in selected["paperTocChildCounts"]), f"selected-paper left hierarchy must expose all five canonical papers with their own second-level sections: {selected['paperTocRoots']}/{selected['paperTocChildCounts']}")
        expected_registry_ids={"STRI","AGENT-SAFETY-R9","D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE","D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK","D2-PAPER-FAILURE-MEMORY-PROVENANCE"}
        require(selected["paperRegistrySummary"].get("papers") == 5 and selected["paperRegistrySummary"].get("submission_ready") == 5 and selected["paperRegistrySummary"].get("gate_clean_submission_ready") == 5 and selected["paperRegistrySummary"].get("paper_preparation_failed") == 0 and selected["paperRegistrySummary"].get("immediate_submission_holds") == 0 and selected["paperRegistrySummary"].get("internal_action_required") == 0 and selected["paperRegistrySummary"].get("no_internal_action") == 5 and (selected["paperRegistrySummary"].get("by_stage") or {}).get("SUBMISSION_READY") == 5 and selected["paperRegistrySummary"].get("scientific_holds") == 0 and selected["paperRegistryPanel"] == 1 and selected["paperRegistryCards"] == 5 and set(selected["paperRegistryIds"]) == expected_registry_ids and selected["paperRegistryStages"].get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK") == "SUBMISSION_READY" and selected["paperRegistryStages"].get("D2-PAPER-FAILURE-MEMORY-PROVENANCE") == "SUBMISSION_READY" and selected["paperRegistryNextActions"].get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK") == "NO_INTERNAL_ACTION" and selected["paperRegistryNextActions"].get("D2-PAPER-FAILURE-MEMORY-PROVENANCE") == "NO_INTERNAL_ACTION" and selected["temporalPaper"].get("gate_clean_submission_ready") is True and (selected["temporalPaper"].get("latest_paper_preparation") or {}).get("pass") is True and (selected["temporalPaper"].get("submission_readiness_context") or {}).get("recommended_immediate_submission") == "READY_FOR_HUMAN_SUBMISSION" and ((selected["temporalPaper"].get("latest_mock_review") or {}).get("summary") or {}).get("scores") == [8,8,7] and ((selected["temporalPaper"].get("source_native_evidence") or {}).get("runtime_valid_rows"),(selected["temporalPaper"].get("source_native_evidence") or {}).get("distinct_endpoints"),(selected["temporalPaper"].get("source_native_evidence") or {}).get("institutional_systems")) == (1326,35,3), f"PaperRegistry internal next-action overview is missing or stale: {selected}")
        paper=selected["currentPaper"]
        require(paper.get("paper_id") == "STRI" and paper.get("source_research_item") == "E-7" and paper.get("paper_stage") == "SUBMISSION_READY" and paper.get("scientific_status") == "READY" and paper.get("submission_ready") is True and paper.get("paper_quality_v2_passed") is True and paper.get("paper_quality_content_addressed_completion") is True and paper.get("paper_quality_content_addressed_files") == 29 and paper.get("paper_quality_evidence_debt") == 0 and (paper.get("qa_passed"),paper.get("qa_total")) == (60,60) and (paper.get("official_qa_passed"),paper.get("official_qa_total")) == (60,60) and paper.get("paper_quality_schema_version") == "2.1" and paper.get("paper_quality_main_visualizations") == 4 and paper.get("paper_visual_figure_qa") == "PASS" and paper.get("supplement_unit_tests") == "29/29 PASS" and paper.get("official_source_conflict") is False and paper.get("deadline_status") == "AUTHOR_SUBMISSION_SOURCES_ALIGNED" and paper.get("operational_safe_abstract_deadline_aoe") == "2026-09-18" and paper.get("operational_safe_full_paper_deadline_aoe") == "2026-09-25" and paper.get("recorded_author_guide_abstract_deadline_aoe") == "2026-09-18" and paper.get("recorded_author_guide_full_paper_deadline_aoe") == "2026-09-25" and paper.get("author_membership_freezes_at_abstract_deadline") is True and paper.get("title_freezes_at_full_paper_deadline") is True and (paper.get("latest_story_search") or {}).get("pass") is True and bool((paper.get("mock_pc_modes") or {}).get("BLIND_MANUSCRIPT")) and bool((paper.get("mock_pc_modes") or {}).get("ARTIFACT_AWARE")) and (paper.get("latest_claim_audit") or {}).get("pass") is True and (paper.get("latest_manuscript_ci") or {}).get("pass") is True and ((paper.get("latest_manuscript_ci") or {}).get("passed"),(paper.get("latest_manuscript_ci") or {}).get("required")) == (9,9) and (paper.get("latest_prebuttal") or {}).get("pass") is True and (paper.get("latest_prebuttal") or {}).get("decision_critical") == 10 and (paper.get("latest_submission_readiness") or {}).get("submission_ready") is True and (paper.get("latest_transition") or {}).get("from") == "PREBUTTAL" and (paper.get("latest_transition") or {}).get("to") == "SUBMISSION_READY" and (paper.get("latest_transition") or {}).get("allowed") is True and (paper.get("authority") or {}).get("submission") is False and selected["currentStatus"].get("paper_ready") == 1, f"STRI PaperState projection is stale: {paper}")
        safety_paper=selected["agentSafetyPaper"]
        require(safety_paper.get("source_research_item") == "G-1" and safety_paper.get("paper_stage") == "SUBMISSION_READY" and safety_paper.get("scientific_status") == "READY" and safety_paper.get("submission_ready") is True and (safety_paper.get("latest_story_search") or {}).get("selected_story_id") == "S1-TEMPORAL-CERTIFICATE-CONTROL" and all((safety_paper.get("mock_pc_modes") or {}).get(mode) for mode in ("BLIND_MANUSCRIPT","ARTIFACT_AWARE")) and (safety_paper.get("latest_claim_audit") or {}).get("pass") is True and ((safety_paper.get("latest_manuscript_ci") or {}).get("passed"),(safety_paper.get("latest_manuscript_ci") or {}).get("required")) == (9,9) and (safety_paper.get("latest_prebuttal") or {}).get("decision_critical") == 10 and (safety_paper.get("latest_submission_readiness") or {}).get("submission_ready") is True and (safety_paper.get("authority") or {}).get("submission") is False, f"Agent Safety bounded R9 PaperState projection is stale: {safety_paper}")
        safety_acceptance=selected["agentSafetyAcceptance"]
        require(safety_acceptance.get("current_state") == "SUBMISSION_READY" and safety_acceptance.get("scientific_status") == "READY" and (safety_acceptance.get("latest_story_search") or {}).get("selected_story_id") == "S1-TEMPORAL-CERTIFICATE-CONTROL" and (safety_acceptance.get("latest_claim_audit") or {}).get("pass") is True and ((safety_acceptance.get("latest_manuscript_ci") or {}).get("passed"),(safety_acceptance.get("latest_manuscript_ci") or {}).get("required")) == (9,9) and (safety_acceptance.get("latest_prebuttal") or {}).get("decision_critical") == 10 and (safety_acceptance.get("latest_submission_readiness") or {}).get("submission_ready") is True and safety_acceptance.get("authority") == {"scientific":False,"experiment":False,"gpu":False,"submission":False}, f"canonical Agent Safety Paper Acceptance projection is stale or unsafe: {selected}")
        acceptance=selected["paperAcceptance"]
        require(acceptance.get("current_state") == "SUBMISSION_READY" and acceptance.get("scientific_status") == "READY" and (acceptance.get("latest_story_search") or {}).get("pass") is True and (acceptance.get("latest_story_search") or {}).get("selected_story_id") == "S1-INVARIANCE-BOUNDARY" and all((acceptance.get("mock_pc_modes") or {}).get(mode) for mode in ("BLIND_MANUSCRIPT","ARTIFACT_AWARE")) and (acceptance.get("latest_claim_audit") or {}).get("pass") is True and (acceptance.get("latest_manuscript_ci") or {}).get("pass") is True and ((acceptance.get("latest_manuscript_ci") or {}).get("passed"),(acceptance.get("latest_manuscript_ci") or {}).get("required")) == (9,9) and (acceptance.get("latest_prebuttal") or {}).get("pass") is True and (acceptance.get("latest_prebuttal") or {}).get("decision_critical") == 10 and (acceptance.get("latest_submission_readiness") or {}).get("submission_ready") is True and acceptance.get("authority") == {"scientific":False,"experiment":False,"gpu":False,"submission":False} and selected["paperAcceptanceSummary"].get("invalid_ledgers") == 0 and selected["paperAcceptanceSummary"].get("scientific_holds") == 0 and selected["paperAcceptanceSummary"].get("registered_papers") == 5 and selected["paperAcceptanceSummary"].get("ledger_submission_ready_papers") == 5 and selected["paperAcceptanceSummary"].get("submission_ready_papers") == 5 and selected["paperAcceptanceSummary"].get("gate_clean_submission_ready_papers") == 5 and selected["paperAcceptanceSummary"].get("internal_action_required_papers") == 0 and selected["paperAcceptanceSummary"].get("no_internal_action_papers") == 5, f"canonical STRI Paper Acceptance projection is stale or unsafe: {selected}")
        p0e=selected["currentDynamic"].get("skillrl_p0e") or {}
        require(p0e.get("status") == "STOP_FIXED_POLICY_DYNAMIC_BRIDGE" and p0e.get("persistent_principle_dead_end_certified") is False and p0e.get("principle_disposition") == "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED" and p0e.get("stage2_locked") is True and p0e.get("new_gpu_authorized") is False and (p0e.get("calibration") or {}).get("calibration_pristine_success") == 18 and (p0e.get("calibration") or {}).get("paired_units") == 24, f"PaperState P0-E scientific boundary is stale: {p0e}")
        dual_ready_markers=("PaperRegistry","SUBMISSION_READY","AGENT-SAFETY-R9","4 update-only / 0 control-only","非当前 PaperState · 历史归档","内部已闭环=5","仍有内部动作=0","Research OS 下一步","NO_INTERNAL_ACTION","When Reusable Temporal Skills Become Causal Bottlenecks","Failure Memories Are Not Neutral","READY_FOR_HUMAN_SUBMISSION","Paper Preparation=8/8 PASS","中央机制证据","1,326 rows","35 endpoints","Mock-PC=8/8/7","TimeSage-EV 精确复现","Manuscript CI=9/9 PASS","Prebuttal=PASS","论文侧闭环已经完成")
        missing_dual_ready=[marker for marker in dual_ready_markers if marker not in selected["text"]]
        require(not missing_dual_ready, f"PaperRegistry / dual submission-ready boundary or historical archive is missing: {missing_dual_ready}; Agent Safety card={selected['agentSafetyCardText']!r}")
        require(all(marker in selected["agentSafetyCardText"] for marker in ("关键因果对照","8/12","4/12","4 update-only / 0 control-only","CI=9/9","Prebuttal=10/10")), f"Agent Safety PaperRegistry card is missing controlled evidence or hard-gate results: {selected['agentSafetyCardText']!r}")
        require(set(selected["submissionDownloads"]) == {"downloads/STRI-ICLR2027-submission-ready-20260821.pdf","downloads/STRI-ICLR2027-submission-ready-20260821.tex","downloads/STRI-ICLR2027-submission-ready-20260821-source.zip"}, f"STRI PaperState submission-ready download set is stale: {selected['submissionDownloads']}")
        require(set(selected["agentSafetyDownloads"]) == {"downloads/Agent-Safety-R9-submission-ready-20260822.pdf","downloads/Agent-Safety-R9-submission-ready-20260822.tex","downloads/Agent-Safety-R9-submission-ready-20260822-source.zip"}, f"Agent Safety PaperState submission-ready download set is stale: {selected['agentSafetyDownloads']}")

        print("PASS")
        print("Focused timeline / Research Portfolio / experiment audit / PaperState pages verified in a real browser")
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
