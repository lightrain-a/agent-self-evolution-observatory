#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, socket, subprocess, sys, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1",0)); return s.getsockname()[1]
HTTP_PORT=free_port(); WEBDRIVER_PORT=free_port()

def request(method,path,data=None):
    body=json.dumps(data).encode() if data is not None else None
    req=urllib.request.Request(f"http://127.0.0.1:{WEBDRIVER_PORT}{path}",data=body,method=method,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)

def execute(sid,script):
    return request("POST",f"/session/{sid}/execute/sync",{"script":script,"args":[]})["value"]

def browser_runtime():
    ff=shutil.which("firefox"); gd=shutil.which("geckodriver")
    sff=Path("/snap/firefox/current/usr/lib/firefox/firefox"); sgd=Path("/snap/firefox/current/usr/lib/firefox/geckodriver")
    if sff.is_file() and sgd.is_file(): ff,gd=str(sff),str(sgd)
    if not ff or not gd: raise SystemExit("SKIP: firefox/geckodriver unavailable")
    return [gd,"--port",str(WEBDRIVER_PORT)],{"capabilities":{"alwaysMatch":{"acceptInsecureCerts":True,"moz:firefoxOptions":{"binary":ff,"args":["-headless"]}}}}

def require(ok,msg):
    if not ok: raise AssertionError(msg)

def main():
    cmd,caps=browser_runtime()
    server=subprocess.Popen([sys.executable,"-m","http.server",str(HTTP_PORT),"--bind","127.0.0.1"],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    driver=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    sid=""
    try:
        for i in range(3):
            time.sleep(1+i)
            try: sid=request("POST","/session",caps)["value"]["sessionId"]; break
            except Exception: pass
        require(bool(sid),"unable to create browser session")
        base=f"http://127.0.0.1:{HTTP_PORT}"
        request("POST",f"/session/{sid}/url",{"url":f"{base}/selected-paper.html"}); time.sleep(.6)
        execute(sid,"localStorage.setItem('agent-evolution-language','zh');location.reload();return true;"); time.sleep(.8)
        collection=execute(sid,"""return {cards:document.querySelectorAll('.cpp-collection-card').length,formal:document.querySelectorAll('#formal-paper-collection .cpp-collection-card').length,working:document.querySelectorAll('#working-paper-collection .cpp-collection-card').length,labels:[...document.querySelectorAll('.cpp-collection-card header>span')].map(x=>x.textContent.trim()),states:[...document.querySelectorAll('.cpp-collection-card header>em')].map(x=>x.textContent.trim()),placeholder:document.querySelector('#site-search')?.getAttribute('placeholder')||'',detail:document.querySelectorAll('.paper-detail-section,.cpp-origin,.cpp-resource-columns,.cpp-proof-grid').length,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2,text:document.body.textContent||''};""")
        require(collection["cards"]==9 and collection["formal"]==5 and collection["working"]==4 and collection["detail"]==0 and not collection["overflow"],f"collection contract failed: {collection}")
        require(collection["labels"][7]=="⑧ Constraint Externality",f"paper 8 label too long: {collection['labels'][7]}")
        require(collection["states"][7]=="PRE-F0.5",f"paper 8 status chip must stay compact: {collection['states'][7]}")
        require("搜索" in collection["placeholder"],f"collection search placeholder is not Chinese: {collection['placeholder']}")
        require("速览版" not in collection["text"] and "Stanford" not in collection["text"],"collection leaked per-paper detail")
        require(not any(x in collection["text"] for x in ("Current Research · Paper Collection","Formal PaperRegistry portfolio","Working papers and independent scientific objects")),"collection leaked English UI labels")
        pages=[
          ("paper-e1.html",True,["R*(A;q)","AutoSkill P19","40 / 40"]),
          ("paper-g1.html",True,["BrowserART + AWM","HB 0/12","DS 3/12"]),
          ("paper-c1.html",True,["Shopping","125/172","0.700 vs 0.595"]),
          ("paper-e2.html",True,["12 streams × 4 paired replicates","17 / 48","Partial effect unopened"]),
          ("paper-b1.html",True,["AgentDojo financial","5/10 eligible","0 calls"]),
          ("paper-a.html",False,["MemoryVLA","LIBERO-Plus",".5541"]),
          ("paper-b.html",False,["MemoryVLA","24 development scopes","Longitudinal confirmatory"]),
          ("paper-agent-constraint.html",False,["AppWorld-derived matched families","PRE-F0.5","ARK_API_KEY"]),
          ("paper-3d.html",False,["InstructScene","3D-FRONT / 3D-FUTURE","SceneNAT"]),
        ]
        for page,formal,markers in pages:
            request("POST",f"/session/{sid}/url",{"url":f"{base}/{page}"}); time.sleep(.55)
            v=execute(sid,"""return {quick:document.querySelector('#quick-overview .cpp-section-kicker')?.textContent.trim()||'',placeholder:document.querySelector('#site-search')?.getAttribute('placeholder')||'',other:document.querySelectorAll('.cpp-collection-card,.cpp-shelf-card,.cpp-pager').length,snapshot:document.querySelectorAll('#paper-snapshot .cpp-snapshot-grid article').length,models:document.querySelectorAll('#models-data .cpp-resource-columns>section:first-child .cpp-resource-card').length,data:document.querySelectorAll('#models-data .cpp-resource-columns>section:last-child .cpp-resource-card').length,contract:document.querySelectorAll('#experiment-contract .cpp-contract-grid article').length,arms:document.querySelectorAll('#experiment-design .cpp-arm-grid article').length,analysis:document.querySelectorAll('#experiment-design .cpp-analysis-grid article').length,design:document.querySelectorAll('#experiment-design .cpp-design-lead').length,proof:document.querySelectorAll('#experiment-results .cpp-proof-grid article').length,interpretation:document.querySelectorAll('#experiment-results .cpp-interpretation>section').length,evolution:document.querySelectorAll('#paper-evolution .cpp-evolution article').length,lineage:document.querySelectorAll('#paper-evolution .cpp-lineage article').length,replay:document.querySelectorAll('#replay-notes').length,origin:document.querySelectorAll('#problem-origin .cpp-origin-grid article').length,registry:document.querySelectorAll('#paper-state').length,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2,text:document.body.textContent||''};""")
            require(v["quick"]=="速览版" and "搜索" in v["placeholder"] and v["other"]==0 and v["snapshot"]>=6 and v["models"]>=2 and v["data"]>=2 and v["contract"]>=4 and v["arms"]>=2 and v["analysis"]>=2 and v["design"]==1 and v["proof"]>=3 and v["interpretation"]>=2 and v["evolution"]>=6 and v["lineage"]>=3 and v["replay"]==1 and not v["overflow"],f"reader contract failed {page}: {v}")
            require((v["origin"]>=3)==formal and (v["registry"]==1)==formal,f"formal migration failed {page}: {v}")
            require("讲给小白听" not in v["text"] and all(m in v["text"] for m in markers),f"markers missing {page}: {markers}")
            require(not any(x in v["text"] for x in ("Understand the paper in 30 seconds","Models, datasets, and environments","How the experiment identifies the scientific question","What the current evidence actually establishes","How the paper evolved into its current form","What should happen next","Back to current paper collection")),f"English UI leaked into Chinese page {page}")
        request("POST",f"/session/{sid}/window/rect",{"width":390,"height":844});
        request("POST",f"/session/{sid}/url",{"url":f"{base}/paper-e2.html"}); time.sleep(.5)
        mobile=execute(sid,"return document.documentElement.scrollWidth>document.documentElement.clientWidth+2")
        require(not mobile,"paper-e2 mobile horizontal overflow")
        print("PASS paper collection + 9 single-paper pages + mobile")
    finally:
        if sid:
            try: request("DELETE",f"/session/{sid}")
            except Exception: pass
        driver.terminate(); server.terminate()
        try: driver.wait(timeout=3); server.wait(timeout=3)
        except Exception: pass
if __name__=="__main__": main()
