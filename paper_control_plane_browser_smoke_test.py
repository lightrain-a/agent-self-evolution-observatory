#!/usr/bin/env python3
"""Real-browser audit for the current PaperRegistry / nine-paper reader control plane."""
from __future__ import annotations

import json
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


def set_zh(session_id: str) -> None:
    execute(session_id, "localStorage.setItem('agent-evolution-language','zh');return true;")
    execute(session_id, "location.reload();return true;")
    time.sleep(0.7)


def execute_args(session_id: str, script: str, args: list):
    return request("POST", f"/session/{session_id}/execute/sync", {"script": script, "args": args})["value"]


def main() -> None:
    expected = json.loads((ROOT / "generated/paper-registry.json").read_text(encoding="utf-8"))
    expected_rows = {row["paper_id"]: row for row in expected.get("papers", [])}
    driver_command, capabilities = browser_runtime()
    server = subprocess.Popen([sys.executable, "-m", "http.server", str(HTTP_PORT), "--bind", "127.0.0.1"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    driver = subprocess.Popen(driver_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    session_id = ""
    try:
        last_error: Exception | None = None
        for attempt in range(3):
            time.sleep(1 + attempt)
            try:
                session_id = request("POST", "/session", capabilities)["value"]["sessionId"]
                break
            except Exception as error:
                last_error = error
                if driver.poll() is not None:
                    driver = subprocess.Popen(driver_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        require(bool(session_id), f"unable to create browser session: {last_error}")

        navigate(session_id, "/selected-paper.html")
        set_zh(session_id)
        selected = execute(session_id, """
          const rows=window.PAPER_REGISTRY?.papers||[];
          return {
            collection:document.querySelectorAll('.cpp-collection-card').length,
            formal:document.querySelectorAll('#formal-paper-collection .cpp-collection-card').length,
            working:document.querySelectorAll('#working-paper-collection .cpp-collection-card').length,
            legacyRegistryCards:document.querySelectorAll('.paper-registry-card').length,
            detail:document.querySelectorAll('.paper-detail-section,.paper-acceptance-workflow').length,
            labels:[...document.querySelectorAll('.cpp-collection-card header>span')].map(x=>(x.textContent||'').trim()),
            summary:window.PAPER_REGISTRY?.summary||{},
            rows,
            overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2
          };""")
        require((selected["collection"], selected["formal"], selected["working"]) == (9, 5, 4), f"nine-paper collection contract drifted: {selected}")
        require(selected["legacyRegistryCards"] == 0 and selected["detail"] == 0, "collection page must route to readers rather than duplicate legacy PaperRegistry detail cards")
        require(not selected["overflow"], "selected-paper collection overflows horizontally")
        require(selected["summary"] == expected.get("summary", {}), f"browser PaperRegistry summary differs from generated canonical projection: {selected['summary']}")
        browser_rows = {row.get("paper_id"): row for row in selected["rows"]}
        require(set(browser_rows) == set(expected_rows) and len(browser_rows) == 5, f"formal PaperState inventory drifted: {sorted(browser_rows)}")
        require([browser_rows[k].get("publication_identity", {}).get("code") for k in expected_rows] == [expected_rows[k].get("publication_identity", {}).get("code") for k in expected_rows], "publication identity projection drifted")
        for paper_id, row in browser_rows.items():
            authority = row.get("authority") or {}
            require(not any(authority.get(k) for k in ("scientific", "experiment", "gpu", "submission")), f"PaperRegistry must never grant authority: {paper_id} {authority}")

        b1 = browser_rows["D2-PAPER-FAILURE-MEMORY-PROVENANCE"]
        require(b1.get("title") == "Does Memory Provenance Matter? Provenance Shifts Agent Behavior but Adds Little Terminal Value Beyond Memory Content", f"B1 canonical title drifted: {b1.get('title')}")
        require(b1.get("paper_stage") == "SUBMISSION_READY" and b1.get("gate_clean_submission_ready") is True, f"B1 readiness drifted: {b1}")
        require(b1.get("supported_claims") == 6 and b1.get("active_unrefuted_claims") == 0, f"B1 R64 claim closure drifted: {b1}")
        require((b1.get("primary_next_action") or {}).get("action_class") == "NO_INTERNAL_ACTION", f"B1 must remain internally closed: {b1}")

        g1 = browser_rows["AGENT-SAFETY-R9"]
        require(g1.get("paper_stage") == "PREBUTTAL" and g1.get("gate_clean_submission_ready") is False and g1.get("immediate_submission_hold") is True, f"G1 reopened hold drifted: {g1}")
        require((g1.get("primary_next_action") or {}).get("action_class") == "EXTERNAL_EVIDENCE_REQUIRED", f"G1 external-evidence blocker drifted: {g1}")

        formal_pages = {
            "/paper-e1.html": "STRI",
            "/paper-g1.html": "AGENT-SAFETY-R9",
            "/paper-c1.html": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
            "/paper-e2.html": "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",
            "/paper-b1.html": "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
        }
        for path, paper_id in formal_pages.items():
            navigate(session_id, path)
            set_zh(session_id)
            view = execute_args(session_id, """const row=(window.PAPER_REGISTRY?.papers||[]).find(x=>x.paper_id===arguments[0])||{};return {registry:document.querySelectorAll('#paper-state').length,download:document.querySelector('.cpp-hero .cpp-download-primary')?.getAttribute('href')||'',h1:(document.querySelector('h1')?.textContent||'').trim(),row,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2};""", [paper_id])
            require(view["registry"] == 1 and not view["overflow"], f"formal reader lost PaperRegistry binding: {path} {view}")
            require(view["row"].get("paper_id") == paper_id and view["row"].get("title") == expected_rows[paper_id].get("title"), f"formal reader loaded wrong PaperState: {path}")
            require(view["download"] == (expected_rows[paper_id].get("downloads") or {}).get("pdf", ""), f"formal reader PDF projection drifted: {path} {view['download']}")
        navigate(session_id, "/paper-b1.html")
        set_zh(session_id)
        b1_view = execute(session_id, """const t=document.body.textContent||'';return {title:document.title,h1:(document.querySelector('h1')?.textContent||'').trim(),full350:t.includes('350 / 350')||t.includes('350/350'),qwen:t.includes('+3.125 pp')||t.includes('+3.125pp'),llama:t.includes('0.0 pp')||t.includes('0pp'),old:t.includes('causal sign unresolved')||t.includes('因果方向未识别'),fffd:(t.match(/\uFFFD/g)||[]).length};""")
        require(b1_view["full350"] and b1_view["qwen"] and b1_view["llama"] and not b1_view["old"] and b1_view["fffd"] == 0, f"B1 R65 public projection drifted: {b1_view}")
        require(b1_view["h1"] in b1_view["title"], f"B1 browser title and H1 diverged: {b1_view}")

        for path in ("/paper-a.html", "/paper-b.html", "/paper-agent-constraint.html", "/paper-3d.html"):
            navigate(session_id, path)
            view = execute(session_id, "return {registry:document.querySelectorAll('#paper-state').length,download:document.querySelectorAll('.cpp-hero .cpp-download-primary').length};")
            require(view == {"registry": 0, "download": 0}, f"working/scientific-object page fabricated formal PaperState or download: {path} {view}")

        print("PASS current PaperRegistry control plane: 5 formal PaperStates + 9-paper collection + B1 R65 reader binding")
    finally:
        if session_id:
            try:
                request("DELETE", f"/session/{session_id}")
            except Exception:
                pass
        driver.terminate(); server.terminate()
        try:
            driver.wait(timeout=3); server.wait(timeout=3)
        except Exception:
            pass


if __name__ == "__main__":
    main()
