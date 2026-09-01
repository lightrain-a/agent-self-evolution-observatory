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
          ("paper-e1.html",True,["R*(A;q)","AutoSkill P19","ReasoningBank"]),
          ("paper-g1.html",True,["HarmBench","DeepSeek","PV1"]),
          ("paper-c1.html",True,["Shopping","125/172","0.700"]),
          ("paper-e2.html",True,["WIN-C","MRW","17 / 48"]),
          ("paper-b1.html",True,["AgentDojo","5/10","provenance"]),
          ("paper-a.html",False,["MemoryVLA","LIBERO-Plus","0.5541"]),
          ("paper-b.html",False,["MemoryVLA","24","future re-exposure"]),
          ("paper-agent-constraint.html",False,["AppWorld","PRE-F0.5","0 calls · 0 outcomes"]),
          ("paper-3d.html",False,["InstructScene","3D-FRONT / 3D-FUTURE","SceneNAT"]),
        ]
        evolution_shapes=[]
        for page,formal,markers in pages:
            request("POST",f"/session/{sid}/url",{"url":f"{base}/{page}"}); time.sleep(.55)
            v=execute(sid,"""const main=document.querySelector('.cpp-page');const clone=main?.cloneNode(true);clone?.querySelector('#research-archive')?.remove();return {quick:document.querySelector('#quick-overview .cpp-section-kicker')?.textContent.trim()||'',placeholder:document.querySelector('#site-search')?.getAttribute('placeholder')||'',other:document.querySelectorAll('.cpp-collection-card,.cpp-shelf-card,.cpp-pager').length,snapshot:document.querySelectorAll('#paper-snapshot .cpp-snapshot-grid article').length,models:document.querySelectorAll('#models-data .cpp-resource-columns>section:first-child .cpp-resource-card').length,data:document.querySelectorAll('#models-data .cpp-resource-columns>section:last-child .cpp-resource-card').length,contract:document.querySelectorAll('.cpp-contract-grid article').length,arms:document.querySelectorAll('.cpp-arm-grid article').length,analysis:document.querySelectorAll('.cpp-analysis-grid article').length,proof:document.querySelectorAll('#experiment-results .cpp-proof-grid article').length,interpretation:document.querySelectorAll('#experiment-results .cpp-interpretation>section').length,evolution:document.querySelectorAll('#paper-evolution .cpp-evolution article').length,lineage:document.querySelectorAll('#paper-evolution .cpp-lineage article').length,replay:document.querySelectorAll('#replay-notes').length,origin:document.querySelectorAll('#problem-origin .cpp-origin-grid article').length,related:document.querySelectorAll('.cpp-related-approach').length,nearest:document.querySelectorAll('.cpp-nearest-table tbody tr').length,storyArchive:document.querySelectorAll('#paper-story-complete').length,workingAudit:document.querySelectorAll('#working-novelty-audit').length,novelty:document.querySelectorAll('#legacy-paper-audit .paper-novelty-detail').length,externalReview:document.querySelectorAll('#legacy-paper-audit .paper-external-review-detail').length,objection:document.querySelectorAll('#legacy-paper-audit .reviewer-objection-detail').length,acceptance:document.querySelectorAll('#legacy-paper-audit .paper-acceptance-workflow').length,registry:document.querySelectorAll('#paper-state').length,readerContext:document.querySelectorAll('.cpp-reader-context').length,gapContext:document.querySelectorAll('.cpp-reader-gap-context').length,designContext:document.querySelectorAll('.cpp-reader-design-context').length,evidenceContext:document.querySelectorAll('.cpp-reader-evidence-context').length,evolutionPhase:document.querySelectorAll('#paper-evolution .cpp-evolution-phase').length,fullEvolution:document.querySelectorAll('#paper-evolution.cpp-full-evolution').length,defaultChars:(clone?.textContent||'').replace(/\\s+/g,'').length,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2,text:document.body.textContent||''};""")
            require(v["quick"].startswith("0 ·") and "搜索" in v["placeholder"] and v["other"]==0 and v["snapshot"]>=6 and v["models"]>=2 and v["data"]>=2 and v["contract"]>=4 and v["arms"]>=2 and v["analysis"]>=2 and v["proof"]>=3 and v["interpretation"]>=2 and v["evolution"]>=4 and v["lineage"]>=3 and v["replay"]==1 and v["readerContext"]>=3 and v["gapContext"]>=1 and v["designContext"]>=1 and v["evidenceContext"]>=1 and v["evolutionPhase"]>=1 and v["fullEvolution"]==1 and v["defaultChars"]>=4500 and not v["overflow"],f"reader contract failed {page}: {v}")
            if formal:
                require(v["origin"]>=3 and v["related"]>=1 and v["nearest"]>=1 and v["storyArchive"]==1 and v["workingAudit"]==0 and v["novelty"]==1 and v["externalReview"]==1 and v["objection"]==1 and v["acceptance"]==1 and v["registry"]==1,f"formal migration failed {page}: {v}")
            else:
                require(v["origin"]>=3 and v["related"]>=1 and v["nearest"]>=1 and v["storyArchive"]==1 and v["workingAudit"]==1 and v["novelty"]==0 and v["externalReview"]==0 and v["objection"]==0 and v["acceptance"]==0 and v["registry"]==0,f"working-paper audit contract failed {page}: {v}")
            require("讲给小白听" not in v["text"] and all(m in v["text"] for m in markers),f"markers missing {page}: {markers}")
            require(not any(x in v["text"] for x in ("Understand the paper in 30 seconds","Models, datasets, and environments","How the experiment identifies the scientific question","What the current evidence actually establishes","How the paper evolved into its current form","What should happen next","Back to current paper collection")),f"English UI leaked into Chinese page {page}")
            evolution_shapes.append((page,v["evolution"],v["lineage"],v["defaultChars"]))
        require(len({(e,l) for _,e,l,_ in evolution_shapes})>=4,f"paper evolution regressed to one fixed template: {evolution_shapes}")
        require(max(n for *_,n in evolution_shapes)-min(n for *_,n in evolution_shapes)>=1000,f"default reader depth is suspiciously uniform: {evolution_shapes}")
        print("reader evolution shapes",evolution_shapes)
        request("POST",f"/session/{sid}/window/rect",{"width":390,"height":844});
        for mobile_page in ("paper-e1.html","paper-b1.html","paper-e2.html","paper-a.html","paper-b.html","paper-agent-constraint.html","paper-3d.html"):
            request("POST",f"/session/{sid}/url",{"url":f"{base}/{mobile_page}"}); time.sleep(.5)
            mobile=execute(sid,"return {overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2,tableScroll:[...document.querySelectorAll('#related-work-comparison .advisor-table-scroll')].every(x=>x.scrollWidth>=x.clientWidth)}")
            require(not mobile["overflow"] and mobile["tableScroll"],f"{mobile_page} mobile related-work overflow contract failed: {mobile}")
        print("PASS paper collection + 9 single-paper pages + mobile")
    finally:
        if sid:
            try: request("DELETE",f"/session/{sid}")
            except Exception: pass
        driver.terminate(); server.terminate()
        try: driver.wait(timeout=3); server.wait(timeout=3)
        except Exception: pass
if __name__=="__main__": main()
