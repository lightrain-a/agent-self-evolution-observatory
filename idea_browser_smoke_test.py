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

        navigate("/system-overview.html", wait=1)
        require(wait_for("return (document.body.textContent||'').includes('SATURATION / DEAD-END MEMORY') && (document.body.textContent||'').includes('PAPER-FIRST');"), "research-system dynamic sections did not become ready")
        system = execute(session_id, """return {
          chapters: document.querySelectorAll('.page-chapter').length,
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
          globalRelationFreshness: window.RESEARCH_SYSTEM_STATE?.paper_first_global_relation_freshness || {},
          globalRelationDelta: window.RESEARCH_SYSTEM_STATE?.paper_first_global_relation_delta_preflight || {},
          globalRelationAdmission: window.RESEARCH_SYSTEM_STATE?.paper_first_global_relation_scan_admission || {},
          shadowSearchAdmission: window.RESEARCH_SYSTEM_STATE?.paper_first_shadow_search_admission || {},
          supportReleaseWatch: window.RESEARCH_SYSTEM_STATE?.paper_first_support_release_watch || {},
          supportAssetRecheck: window.RESEARCH_SYSTEM_STATE?.paper_first_support_asset_recheck_queue || {},
          text: document.body.textContent || ''
        };""")
        require(system["chapters"] == 6, f"research-system overview must have six chapters, got {system['chapters']}")
        require(system["responsibilityLayers"] == 6 and system["temporalStages"] == 11 and system["componentLayerHeaders"] == 6 and system["aiCheckpoints"] == 5, f"research-system architecture/AI clinic is incomplete: layers={system['responsibilityLayers']} stages={system['temporalStages']} component-groups={system['componentLayerHeaders']} ai={system['aiCheckpoints']}")
        require((system["architectureSummary"].get("temporal_stages"),system["architectureSummary"].get("functional_layers"),system["architectureSummary"].get("assigned_components"),system["architectureSummary"].get("unassigned_components"),system["architectureSummary"].get("cross_cutting_controls"),system["architectureSummary"].get("orphan_cross_cutting_controls")) == (11,6,27,0,3,0), f"backend architecture manifest is stale in browser state: {system['architectureSummary']}")
        require(system["methodologyControls"] == 3 and "Exploration Frontier" in system["text"] and "Reproducibility Readiness" in system["text"], f"cross-cutting methodology controls are missing: {system['methodologyControls']}")
        require(system["outerGates"] == 8 and system["preflightGates"] == 10 and system["quantWorksheets"] == 2, f"Pre-Experiment/identifiability compiler is incomplete: {system['outerGates']}/{system['preflightGates']}/{system['quantWorksheets']}")
        require(system["lessons"] == 6 and system["failureLayers"] == 6 and system["repairLoops"] == 1, f"learning/diagnosis visualization is incomplete: {system['lessons']}/{system['failureLayers']}/{system['repairLoops']}")
        require(system["components"] >= 27, f"expected the current backend responsibility set including Paper-first contract, capability registry, literature audit, Principle, Protocol Validity, Meta-Trace, failure memory, scheduler, replay, Economy, and AI consultation, got {system['components']}")
        require(system["ideaCards"] == 0, f"system-overview must not render current idea/status panels, got {system['ideaCards']}")
        primary = system["primaryEvidence"]
        generator = system["problemGenerator"]
        require(primary.get("status") == "READY" and (primary.get("policy") or {}).get("empirical_fact_extraction_version") == "precision-v2" and (primary.get("policy") or {}).get("empirical_fact_precision_gate") is True, f"browser primary-evidence precision state is stale: {primary}")
        require((primary.get("policy") or {}).get("scientific_object_lanes") == ["skill_harness","memory_continual","world_model","parametric_model_state"] and (primary.get("policy") or {}).get("source_coverage_exploration_prefers_scientific_objects") is True and (primary.get("policy") or {}).get("context_and_property_tags_have_zero_scientific_authority") is True, f"browser scientific-object policy is stale: {primary.get('policy')}")
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
        require(shadow_system_admission.get("status") == "SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL" and shadow_system_summary.get("same_source_transaction") is True and shadow_system_summary.get("qualification_allowed") is False and shadow_system_summary.get("automatic_provider_calls_authorized") == 0 and "SHADOW RUN ADMISSION" in system["text"], f"system overview shadow-run admission must show duplicate-source zero-call skip: {shadow_system_admission}")
        release_watch=system["supportReleaseWatch"] or {};release_summary=release_watch.get("summary") or {};release_policy=release_watch.get("policy") or {}
        if release_watch.get("status") and release_watch.get("status") != "NOT_RUN":
            require(release_watch.get("scientific_authority") is False and release_policy.get("primary_declared_release_endpoints_only") is True and release_policy.get("related_work_repository_links_are_not_watch_targets") is True and release_policy.get("release_watch_cannot_mark_support_qualified") is True and release_policy.get("release_watch_cannot_reopen_generator_or_problem_gate") is True and int(release_summary.get("support_qualified") or 0)==0 and int(release_summary.get("generator_reopen_authorized") or 0)==0 and int(release_summary.get("problem_gate_authorized") or 0)==0, f"support release watch authority boundary is invalid: {release_watch}")
            if "primary_declaration_refresh_checked" in release_summary:
                require(release_policy.get("no_endpoint_primary_refresh_is_primary_source_only") is True and release_policy.get("primary_declaration_refresh_has_zero_source_exposure_effect") is True and release_policy.get("primary_declaration_refresh_cannot_qualify_support") is True and int(release_summary.get("primary_declaration_refresh_changed") or 0) >= 0 and int(release_summary.get("primary_declaration_refresh_rate_limited") or 0) >= 0, f"support release primary-refresh boundary is invalid: {release_watch}")
                require("primary-refresh checked/changed=" in system["text"], "support release primary-refresh counts are not rendered")
            require("SUPPORT RELEASE WATCH" in system["text"] and "support-qualified=0" in system["text"], "support release watch is not rendered as recheck-only zero authority")
        asset_queue=system["supportAssetRecheck"] or {};asset_summary=asset_queue.get("summary") or {};asset_policy=asset_queue.get("policy") or {}
        if asset_queue.get("status") and asset_queue.get("status") != "NOT_RUN":
            require(asset_queue.get("scientific_authority") is False and asset_policy.get("release_change_only_creates_asset_recheck_task") is True and asset_policy.get("queue_is_durable_across_release_watch_cooldown") is True and asset_policy.get("queue_cannot_mark_support_qualified") is True and asset_policy.get("queue_cannot_reopen_generator_or_problem_gate") is True and asset_policy.get("queue_cannot_authorize_method_experiment_p0_gpu") is True and asset_policy.get("explicit_asset_resolution_required_to_clear_entry") is True and asset_policy.get("automatic_provider_calls_authorized") is False and all(int(asset_summary.get(key) or 0)==0 for key in ("support_qualified","generator_reopen_authorized","problem_gate_authorized","method_authorized","experiment_authorized","p0_authorized","gpu_authorized")), f"support asset recheck queue authority boundary is invalid: {asset_queue}")
            require("SUPPORT ASSET RECHECK QUEUE" in system["text"] and "Generator=0" in system["text"] and "Problem-Gate=0" in system["text"], "support asset recheck queue is not rendered as zero-authority durable task accounting")
        relation_freshness=system["globalRelationFreshness"] or {};relation_summary=relation_freshness.get("summary") or {}
        if relation_freshness.get("status") == "STALE_RELATION_UNIVERSE":
            require(relation_freshness.get("scientific_authority") is False and relation_summary.get("universe_stale") is True and relation_summary.get("current_not_reduced_unknown") is True and relation_summary.get("model_scan_deferred") is True and relation_summary.get("focused_problem_generator_reopen_allowed") is False and int(relation_summary.get("current_reviewed_sources") or 0) > int(relation_summary.get("last_scanned_sources") or 0), f"stale relation-universe boundary is invalid: {relation_freshness}")
            require("STALE_RELATION_UNIVERSE" in system["text"] and "current UNKNOWN" in system["text"] and "model-scan=DEFERRED" in system["text"], "stale relation-universe interpretation is not rendered")
        relation_delta=system["globalRelationDelta"] or {};delta_summary=relation_delta.get("summary") or {};delta_policy=relation_delta.get("policy") or {}
        if relation_delta.get("status") == "RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE":
            require(relation_delta.get("scientific_authority") is False and delta_policy.get("deterministic_typed_evidence_delta_only") is True and delta_policy.get("pair_slots_are_not_lane_valid_pairs") is True and delta_policy.get("cannot_reopen_generator") is True and delta_policy.get("cannot_authorize_relation_model_scan") is True and delta_summary.get("model_scan_authorized") is False and delta_summary.get("focused_generator_reopen_authorized") is False, f"relation delta preflight authority boundary is invalid: {relation_delta}")
            require("RELATION DELTA PREFLIGHT" in system["text"] and "combinatorial search upper bounds" in system["text"], "relation delta preflight is not rendered as non-authoritative opportunity accounting")
        relation_admission=system["globalRelationAdmission"] or {};admission_summary=relation_admission.get("summary") or {};admission_policy=relation_admission.get("policy") or {}
        if relation_admission:
            require(relation_admission.get("scientific_authority") is False and admission_policy.get("automatic_model_scan_authority") is False and admission_policy.get("manual_execution_requires_explicit_operator_flag") is True and admission_policy.get("manual_eligibility_is_not_scientific_authority") is True and admission_policy.get("relation_scan_cannot_authorize_problem_gate") is True and admission_policy.get("relation_scan_cannot_authorize_method_experiment_p0_gpu") is True and admission_summary.get("automatic_model_scan_authorized") is False, f"manual relation scan admission authority boundary is invalid: {relation_admission}")
            require("MANUAL RELATION SCAN ADMISSION" in system["text"] and "automatic-model-authority=NO" in system["text"], "manual relation scan admission is not rendered as explicit-manual-only")
        require("NO-LANE CARRIER PROBE" in system["text"] and "SHADOW SEARCH LAB" in system["text"] and "live-lanes=4" in system["text"] and "shadow-primitives=10" in system["text"] and "GLOBAL RELATION RECALL" in system["text"] and "canonical durable backlog" in system["text"].lower() and any(marker in system["text"] for marker in ("v2.9 · MACHINE-ENFORCED","v3.0 · MACHINE-ENFORCED","v3.1 · MACHINE-ENFORCED","v3.2 · MACHINE-ENFORCED","v3.3 · MACHINE-ENFORCED","v3.4 · MACHINE-ENFORCED","v3.5 · MACHINE-ENFORCED","v3.6 · MACHINE-ENFORCED","v3.7 · MACHINE-ENFORCED","v3.8 · MACHINE-ENFORCED","v3.9 · MACHINE-ENFORCED")), "problem-discovery carrier/live/shadow/relation authority boundary is not rendered")
        require((system["preSummary"].get("audited"), system["preSummary"].get("execution_ready"), system["preSummary"].get("blocked")) == (4,0,4), f"Pre-P0 retrospective state is wrong: {system['preSummary']}")
        iteration = system["iterationSummary"]
        infra_only = iteration.get("diagnosis_counts") == {"infrastructure-error": 4}
        require(iteration.get("scale_up_allowed") == 0 and (iteration.get("belief_updates_allowed") == 1 or (iteration.get("belief_updates_allowed") == 0 and infra_only)), f"experiment-diagnosis state is wrong: {iteration}")
        require("Main ICLR idea bank" not in system["text"] and "Final advisor gate" not in system["text"] and "主 ICLR Idea Bank" not in system["text"] and "最终师兄讨论门槛" not in system["text"], "current idea portfolio leaked back into the research-system page")
        execute(session_id, "document.querySelector('.language-toggle')?.click();")
        time.sleep(1)
        zh = execute(session_id, "return {text:document.body.textContent||'', outer:document.querySelectorAll('.preflight-outer-gate').length, gates:document.querySelectorAll('.preflight-gate').length, failures:document.querySelectorAll('.system-failure-layer').length};")
        require(zh["outer"] == 8 and zh["gates"] == 10 and zh["failures"] == 6 and "P0 ECONOMY" in zh["text"] and "PROTOCOL VALIDITY" in zh["text"] and "SCIENTIFIC META-TRACE" in zh["text"] and "PRINCIPLE" in zh["text"], "research-system Economy / Principle / Protocol Validity / learning-loop visualization is incomplete")
        request("POST", f"/session/{session_id}/window/rect", {"width": 390, "height": 844})
        time.sleep(1)
        system_mobile = execute(session_id, """const gate=document.querySelector('.preflight-gate-grid'); const failure=document.querySelector('.system-failure-layers'); return {inner:window.innerWidth,scroll:document.documentElement.scrollWidth,gateCols:gate?getComputedStyle(gate).gridTemplateColumns:'',failureCols:failure?getComputedStyle(failure).gridTemplateColumns:'',maxCard:Math.max(0,...[...document.querySelectorAll('.preflight-gate,.system-failure-layer,.methodology-control-card')].map(x=>x.getBoundingClientRect().width))};""")
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
          incubationCards: document.querySelectorAll('.paper-incubation-card').length,
          incubationAdvance: document.querySelectorAll('.paper-incubation-card.incubation-advance').length,
          incubationP0: document.querySelectorAll('.paper-incubation-card.incubation-p0').length,
          incubationRevise: document.querySelectorAll('.paper-incubation-card.incubation-revise').length,
          incubationBlock: document.querySelectorAll('.paper-incubation-card.incubation-block').length,
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
          shadowSourceSummary: window.PAPER_FIRST_SEARCH_PORTFOLIO_DESIGN_ADJUDICATION?.shadow_source?.summary || {},
          shadowQueueSummary: window.PAPER_FIRST_SEARCH_PORTFOLIO_DESIGN_ADJUDICATION?.shadow_source?.queue_summary || {},
          shadowLatestRun: window.RESEARCH_SYSTEM_STATE?.paper_first_problem_search_portfolio?.latest_run || {},
          shadowLatestSummary: window.RESEARCH_SYSTEM_STATE?.paper_first_problem_search_portfolio?.latest_run?.summary || {},
          shadowLatestPanels: document.querySelectorAll('.paper-first-search-latest').length,
          shadowAdmission: window.RESEARCH_SYSTEM_STATE?.paper_first_shadow_search_admission || {},
          shadowAdmissionPanels: document.querySelectorAll('.paper-first-shadow-admission').length,
          sp15SupportSummary: window.PAPER_FIRST_SP15_IDENTIFIABILITY_SUPPORT?.summary || {},
          prematureMethodSummary: window.PAPER_FIRST_PREMATURE_METHOD_DIAGNOSTICS?.summary || window.RESEARCH_SYSTEM_STATE?.paper_first_premature_method_diagnostics?.summary || {},
          prematureMethodPanels: document.querySelectorAll('.premature-method-diagnostic').length,
          designCards: document.querySelectorAll('.paper-incubation-card small').length,
          text: document.body.textContent || ''
        };""")
        require(ideas["chapters"] == 2, f"paper-ideas should merge standalone methods and Paper-first new problems into Chapter II, got {ideas['chapters']}")
        require(ideas["p0Entry"] == 0 and ideas["p0Boards"] == 0 and ideas["experimentLinks"] >= 1, f"legacy P0-entry/control boards must stay off canonical Paper Ideas: {ideas['p0Entry']}/{ideas['p0Boards']}/{ideas['experimentLinks']}")
        require(ideas["p0AdmissionSummary"].get("active_p0") == 27 and ideas["p0AdmissionSummary"].get("transitioned_from_p0_ready") == 16 and ideas["p0AdmissionSummary"].get("revived_from_drop") == 7 and ideas["p0AdmissionSummary"].get("settings_complete") == 27 and ideas["p0AdmissionSummary"].get("execution_authorized") == 0, f"paper-ideas unified P0 admission state is stale: {ideas['p0AdmissionSummary']}")
        require(ideas["p0Summary"].get("ready_now") == 0 and ideas["p0Summary"].get("pre_p0_blocked") == 4 and ideas["p0Summary"].get("gpu_hours_cap_ready_now") == 0 and ideas["p0Summary"].get("p1_authorized") == 0, f"P0 Pre-P0/resource summary is wrong: {ideas['p0Summary']}")
        require(ideas["p0Policy"].get("pre_p0_identifiability_required") is True and ideas["p0Policy"].get("automatic_p0_to_p1_forbidden") is True and ideas["p0Policy"].get("p0_pass_requires_human_approval") is True, f"P0 human/Pre-P0 approval policy is missing: {ideas['p0Policy']}")
        require(ideas["toc2"] >= 3 and ideas["toc4"] == 0, f"paper-ideas TOC hierarchy is wrong: {ideas['toc2']}/{ideas['toc3']}/{ideas['toc4']}")
        require(ideas["discussedGroups"] == 6 and ideas["discussedCards"] == 26, f"expected six scientific groups and 26 discussed ideas, got {ideas['discussedGroups']}/{ideas['discussedCards']}")
        require((ideas["readyCards"], ideas["mergedCards"], ideas["droppedCards"]) == (20, 6, 0), f"terminal tone counts are wrong: {ideas['readyCards']}/{ideas['mergedCards']}/{ideas['droppedCards']}")
        require(ideas["terminalCounts"].get("p0") == 20 and ideas["terminalCounts"].get("p0-ready",0) == 0 and ideas["terminalCounts"].get("merge") == 6 and ideas["terminalCounts"].get("drop",0) == 0, f"terminal parent counts are wrong: {ideas['terminalCounts']}")
        require((ideas["terminalSummary"].get("human_parents"), ideas["terminalSummary"].get("revived_to_p0"), ideas["absorbedChildCount"]) == (26,7,17), f"terminal ledger or absorbed-child count is wrong: {ideas['terminalSummary']}/{ideas['absorbedChildCount']}")
        require(ideas["feedbackSummaries"] == 26, f"every discussed idea must expose one current summary, got {ideas['feedbackSummaries']}")
        require(ideas["humanOpinionBoxes"] == 26, f"all 26 discussed ideas must preserve the human opinion, got {ideas['humanOpinionBoxes']}")
        require(ideas["iterationBoxes"] == 17 and ideas["finalRefinementBoxes"] == 17, f"all 17 refined methods must show the final iteration and routing: {ideas['iterationBoxes']}/{ideas['finalRefinementBoxes']}")
        require(ideas["finalRefinementCounts"] == [20,0,6,0], f"terminal routing must be 20 P0 / 0 P0-ready / 6 merge / 0 drop, got {ideas['finalRefinementCounts']}")
        require(ideas["methodologyPanels"] == 1 and ideas["originalEvalGuides"] == 1, f"human-opinion audit/original-eval methodology panels are missing: {ideas['methodologyPanels']}/{ideas['originalEvalGuides']}")
        require(ideas["canonicalReviewCount"] == 26, f"canonical human-review map must cover all 26 ideas, got {ideas['canonicalReviewCount']}")
        require(ideas["humanRecommendationStats"] == [4,14,7,1], f"canonical human recommendation counts are wrong: {ideas['humanRecommendationStats']}")
        require(any('Original Idea 4' in label or '原讨论 Idea 4' in label for label in ideas["originalIdeaLabels"]), f"original discussion numbering is not visible: {ideas['originalIdeaLabels'][:5]}")
        require(ideas["concreteExamples"] == 26 and ideas["parentMergeRules"] >= 1, f"intuition/example or parent-merge UI gate is missing: {ideas['concreteExamples']}/{ideas['parentMergeRules']}")
        require(ideas["openDiscussedCards"] == 0 and ideas["openNewCards"] == 0, f"all idea cards must be collapsed by default, got {ideas['openDiscussedCards']}/{ideas['openNewCards']}")
        require(len(ideas["codes"]) == 26 and len(set(ideas["codes"])) == 26, f"group codes are missing or duplicated: {ideas['codes']}")
        require(all(code in ideas["codes"] for code in ("A-1","A-5","B-1","B-7","C-1","D-1","E-1","F-1","F-3")), f"expected stable group codes are missing: {ideas['codes']}")
        require(ideas["newGroups"] == 3 and ideas["newCards"] == 7, f"standalone area must contain only the seven validated standalone P0 methods: {ideas['newGroups']}/{ideas['newCards']}")
        require(set(ideas["standaloneCodes"]) == {"A-6","A-7","B-8","B-9","B-10","E-3","E-4"}, f"standalone methods must have stable scientific-group codes: {ideas['standaloneCodes']}")
        require((ideas["newFinal"], ideas["newInspired"]) == (0, 0), f"legacy supplemental candidates must not remain active: {ideas['newFinal']}/{ideas['newInspired']}")
        require(ideas["mergedMethods"] >= 8, f"merged FINAL method provenance is not visible on discussed ideas: {ideas['mergedMethods']}")
        require(ideas["freshCollisionBlocks"] == 17 and ideas["freshCollisionLinks"] >= 40, f"fresh reducibility sources are missing from refined ideas: {ideas['freshCollisionBlocks']}/{ideas['freshCollisionLinks']}")
        require(all(marker in ideas["text"] for marker in ("ChronoMem","DeltaBox","CausalFlow")), "latest load-bearing collision sources are not visible in refined idea cards")
        require((ideas["incubationCards"],ideas["incubationAdvance"],ideas["incubationRevise"],ideas["incubationBlock"],ideas["incubationOpen"]) == (9,4,3,2,0), f"Paper-first incubation rendering is wrong: {ideas['incubationCards']}/{ideas['incubationAdvance']}/{ideas['incubationRevise']}/{ideas['incubationBlock']}/{ideas['incubationOpen']}")
        require((ideas["incubationSummary"].get("p0_authorized"),ideas["incubationSummary"].get("gpu_authorized")) == (0,0), f"incubation must remain outside P0/GPU authority: {ideas['incubationSummary']}")
        ds=ideas["designSummary"]
        require((ds.get("reviewed"),ds.get("advance_to_method_design"),ds.get("revise_paper_problem"),ds.get("merge_as_cross_cutting_invariant"),ds.get("stop_standalone_merge_risk_axis"),ds.get("local_validation_authorized")) == (4,1,1,1,1,0), f"Paper Design adjudication routing is stale: {ds}")
        require(ideas["designVerdicts"] == {"PF-2":"ADVANCE_TO_METHOD_DESIGN","PF-1":"REVISE_PAPER_PROBLEM","PF-4":"MERGE_AS_CROSS_CUTTING_INVARIANT","PF-6":"STOP_STANDALONE_MERGE_RISK_AXIS"}, f"Paper Design historical verdicts are wrong: {ideas['designVerdicts']}")
        require(ideas["pf1ProblemDecision"] == "STOP_PF1_STANDALONE_PROBLEM_MERGE_EVOLVABILITY_AUDIT" and not ideas["pf1ProblemActive"] and not ideas["pf1MethodAuthorized"], f"PF-1 final problem STOP is not rendered conservatively: {ideas}")
        require(ideas["pf2MethodDecision"] == "STOP_CURRENT_RSIC_METHOD_THESIS_KEEP_PROBLEM_PROTOCOL" and ideas["pf2MethodProblemStatus"] == "SURVIVES_AS_PROBLEM_AND_EVALUATION_PROTOCOL_ONLY" and not ideas["pf2MethodBlueprintAuthorized"] and not ideas["pf2MethodLocalAuthorized"], f"PF-2 method-level STOP is not rendered conservatively: {ideas}")
        require((ideas["pf357Summary"].get("reviewed"),ideas["pf357Summary"].get("stopped_standalone"),ideas["pf357Summary"].get("paper_design_authorized"),ideas["pf357Summary"].get("local_validation_authorized")) == (3,3,0,0), f"PF-3/5/7 final adjudication is stale: {ideas['pf357Summary']}")
        require(set(ideas["pf357Decisions"]) == {"PF-3","PF-5","PF-7"} and all(str(v).startswith("STOP_PF") for v in ideas["pf357Decisions"].values()), f"PF-3/5/7 decisions are wrong: {ideas['pf357Decisions']}")
        require((ideas["freshSummary"].get("drafts_reviewed"),ideas["freshSummary"].get("survivors"),ideas["freshSummary"].get("stopped"),ideas["freshSummary"].get("local_validation_authorized"),ideas["freshSummary"].get("p0_authorized")) == (41,0,41,0,0) and ideas["freshDecision"] == "NO_FRESH_SURVIVOR_CURRENT_SCAN" and ideas["freshZeroSurvivorPolicy"] and ideas["freshPanel"] == 1, f"fresh saturation scan must show 41 reviewed / 0 survivor / 41 stop with zero-survivor policy: {ideas}")
        require((ideas["shadowDesignSummary"].get("reviewed"),ideas["shadowDesignSummary"].get("advance_to_method_design"),ideas["shadowDesignSummary"].get("revise_paper_problem"),ideas["shadowDesignSummary"].get("stop_standalone"),ideas["shadowDesignSummary"].get("current_source_hard_veto_dead_ends"),ideas["shadowDesignSummary"].get("current_source_hard_veto_added_from_latest_run"),ideas["shadowDesignSummary"].get("current_source_hard_veto_inherited"),ideas["shadowDesignSummary"].get("semantic_blocker_dead_ends"),ideas["shadowDesignSummary"].get("near_miss_preflight_dead_ends"),ideas["shadowDesignSummary"].get("near_miss_support_holds"),ideas["shadowDesignSummary"].get("near_miss_terminal_support_holds"),ideas["shadowDesignSummary"].get("near_miss_current_primary_stops"),ideas["shadowDesignSummary"].get("near_miss_mature_theory_stops")) == (2,0,1,1,2,0,2,4,8,1,4,2,1), f"shadow Search Portfolio design/dead-end routing is stale: {ideas['shadowDesignSummary']}")
        require(ideas["shadowDesignPolicy"].get("source_is_shadow_search_portfolio") is True and ideas["shadowDesignPolicy"].get("shadow_queue_has_zero_paper_design_authority") is True and ideas["shadowDesignPolicy"].get("cannot_grant_or_revoke_live_paper_design_authority") is True, f"shadow Paper Design authority boundary is missing: {ideas['shadowDesignPolicy']}")
        require((ideas["shadowQueueSummary"].get("counterfactual_problem_gate_passed"),ideas["shadowQueueSummary"].get("live_paper_design_eligible")) == (2,0), f"shadow queue must expose 2 historical counterfactual passes and 0 live eligibility: {ideas['shadowQueueSummary']}")
        latest=ideas["shadowLatestSummary"]
        require(ideas["shadowLatestRun"].get("run_id") == "shadow-20260814-r5" and (latest.get("requested_raw_seeds"),latest.get("expansion_successful_shards"),latest.get("expansion_execution_failures"),latest.get("raw_seeds"),latest.get("semantic_unique"),latest.get("evolved_branches"),latest.get("formulation_successful_shards"),latest.get("formulation_parse_failures"),latest.get("formulation_successful_branches"),latest.get("formulation_execution_censored_branches"),latest.get("formulated_candidates"),latest.get("formulation_reduction_pending",0),latest.get("machine_reviewable"),latest.get("machine_reduction_pending",0),latest.get("problem_falsifier_eligible"),latest.get("semantic_clear"),latest.get("terminal_shadow_survivors")) == (120,18,2,84,47,36,11,1,22,2,14,0,0,0,0,0,0), f"latest shadow r5 funnel/accounting is stale: {ideas['shadowLatestRun']}")
        require((latest.get("current_source_missing"),latest.get("current_source_reviewed"),latest.get("live_paper_design_eligible"),ideas["shadowLatestPanels"]) == (0,0,0,1), f"latest shadow r5 must be terminal-complete, zero-live-authority, and rendered once: {latest}/{ideas['shadowLatestPanels']}")
        shadow_admission=ideas["shadowAdmission"];shadow_admission_summary=shadow_admission.get("summary") or {}
        require(shadow_admission.get("status") == "SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL" and shadow_admission_summary.get("canonical_transaction_closed") is True and shadow_admission_summary.get("same_source_transaction") is True and shadow_admission_summary.get("qualification_allowed") is False and shadow_admission_summary.get("automatic_provider_calls_authorized") == 0 and ideas["shadowAdmissionPanels"] == 1, f"shadow next-run admission must skip duplicate r6 with zero provider authority: {shadow_admission}/{ideas['shadowAdmissionPanels']}")
        require((ideas["sp15SupportSummary"].get("primary_or_author_releases_audited"),ideas["sp15SupportSummary"].get("query_level_identifiability_units"),ideas["sp15SupportSummary"].get("method_design_authorized")) == (5,0,0), f"SP-15 shadow identifiability support must remain 5 sources / 0 units / 0 method authority: {ideas['sp15SupportSummary']}")
        require("Shadow Search Portfolio · retrospective Paper Design audit" in ideas["text"] and "Shadow Search Portfolio · latest current-source terminal" in ideas["text"] and "Shadow Search · next-run admission" in ideas["text"] and "SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL" in ideas["text"] and "provider-calls=0" in ideas["text"] and "qualifying query-level units=0" in ideas["text"] and "current-source hard-veto memory=2" in ideas["text"] and "semantic reduction/lane memory=4" in ideas["text"] and "near-miss memory=8" in ideas["text"] and "terminal support HOLD=4" in ideas["text"] and "last terminal memory=shadow-20260814-r4b" in ideas["text"] and "mature-theory STOP=1" in ideas["text"] and "control=1.3/unbound" in ideas["text"] and "execution-censored=2" in ideas["text"] and "reduction-pending=0" in ideas["text"] and "machine-pending=0" in ideas["text"] and "problem-falsifier=0" in ideas["text"] and "inventory-request=0" in ideas["text"], "shadow Paper Design/latest terminal/admission/execution/dead-end/SP-15 results are not rendered")
        require(all(marker in ideas["text"] for marker in ("PF-1","PF-2","PF-3","PF-4","PF-5","PF-6","PF-7","STOP_PF1_STANDALONE_PROBLEM_MERGE_EVOLVABILITY_AUDIT","STOP_CURRENT_RSIC_METHOD_THESIS_KEEP_PROBLEM_PROTOCOL","STOP_PF3_STANDALONE_MERGE_COMPRESSION_LIFECYCLE_CONTROL","STOP_PF5_STANDALONE_MERGE_DIFFERENTIAL_VERIFICATION_COMPONENT","STOP_PF7_STANDALONE_MERGE_EVIDENCE_IMPACT_REVALIDATION_COMPONENT")), "Paper-first terminal/fresh-saturation verdicts are not visible")
        pmd=ideas["prematureMethodSummary"]
        require((pmd.get("directions"),pmd.get("completed_diagnostics"),pmd.get("design_holds"),pmd.get("same_information_reducibility_findings"),pmd.get("hidden_executions"),pmd.get("scientifically_authorized")) == (2,2,1,2,0,0) and ideas["prematureMethodPanels"] == 2, f"premature Method diagnostics must be visible as two non-authoritative PF-1/PF-4 archives: {pmd}/{ideas['prematureMethodPanels']}")
        require("STOP_MATCHED_POST_ONLY_EQUIVALENT" in ideas["text"] and "STOP_MATCHED_SOFT_SCALAR_EQUIVALENT" in ideas["text"] and "DIAGNOSTIC ONLY" in ideas["text"], "Paper-first diagnostic archive markers are not visible")
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
          text: document.body.textContent || ''
        };""")
        require(experiments["chapters"] == 3, f"experiments page must have three chapters, got {experiments['chapters']}")
        require((experiments["terminalPortfolio"],experiments["terminalRows"],experiments["terminalP0"],experiments["terminalP0Ready"]) == (1,27,27,0), f"terminal experiment portfolio is not aligned with validated Paper Ideas: {experiments}")
        require((experiments["terminalStarted"],experiments["terminalPending"],experiments["auditQueue"],experiments["auditItems"]) == (27,0,0,0), f"started/pending audit split is wrong: {experiments}")
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
