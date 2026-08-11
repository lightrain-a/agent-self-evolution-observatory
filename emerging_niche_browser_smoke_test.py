#!/usr/bin/env python3
from __future__ import annotations

import json, shutil, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTTP_PORT, DRIVER_PORT = 8127, 4448


def req(method: str, path: str, data=None):
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(f"http://127.0.0.1:{DRIVER_PORT}{path}", data=body, method=method, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(request, timeout=60) as response: return json.load(response)


def execute(session: str, script: str):
    return req("POST", f"/session/{session}/execute/sync", {"script":script,"args":[]})["value"]


def main() -> None:
    firefox, driver = shutil.which("firefox"), shutil.which("geckodriver")
    if not firefox or not driver: raise SystemExit("SKIP: Firefox/geckodriver unavailable")
    httpd = subprocess.Popen([sys.executable,"-m","http.server",str(HTTP_PORT),"--bind","127.0.0.1"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    webdriver = subprocess.Popen([driver,"--port",str(DRIVER_PORT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    session = ""
    try:
        time.sleep(2)
        caps={"capabilities":{"alwaysMatch":{"acceptInsecureCerts":True,"moz:firefoxOptions":{"args":["-headless"]}}}}
        session=req("POST","/session",caps)["value"]["sessionId"]
        base=f"http://127.0.0.1:{HTTP_PORT}"
        for page in ("system-overview.html","paper-ideas.html"):
            req("POST",f"/session/{session}/url",{"url":f"{base}/{page}"}); time.sleep(5)
            state=execute(session,"""const p=document.getElementById('emerging-niche-score'); return {count:document.querySelectorAll('#emerging-niche-score').length,components:p?p.querySelectorAll('.reviewer-gate-grid article').length:0,text:p?p.textContent:'',lang:document.documentElement.lang,ens:window.EMERGING_NICHE_POLICY?.short_name||'',overrides:window.EMERGING_NICHE_POLICY?.hard_policy?.never_overrides||[]};""")
            assert state["count"] == 1, (page,state)
            assert state["components"] == 5, (page,state)
            assert state["ens"] == "ENS" and "experiment_stop" in state["overrides"], (page,state)
            initial_zh = str(state["lang"]).lower().startswith("zh")
            assert (("新兴小众方向评分" in state["text"]) if initial_zh else ("Emerging-Niche Score" in state["text"])), (page,state)
            execute(session,"document.querySelector('.language-toggle')?.click();"); time.sleep(1)
            flipped=execute(session,"""const p=document.getElementById('emerging-niche-score'); return {count:document.querySelectorAll('#emerging-niche-score').length,text:p?p.textContent:'',lang:document.documentElement.lang};""")
            assert flipped["count"] == 1 and str(flipped["lang"]).lower().startswith("zh") != initial_zh, (page,flipped)
            assert (("新兴小众方向评分" in flipped["text"]) if not initial_zh else ("Emerging-Niche Score" in flipped["text"])), (page,flipped)
        print("PASS\nENS policy rendered on system-overview and paper-ideas in both languages")
    finally:
        if session:
            try: req("DELETE",f"/session/{session}")
            except Exception: pass
        webdriver.terminate(); httpd.terminate()
        try: webdriver.wait(timeout=5)
        except Exception: webdriver.kill()
        try: httpd.wait(timeout=5)
        except Exception: httpd.kill()


if __name__ == "__main__": main()
