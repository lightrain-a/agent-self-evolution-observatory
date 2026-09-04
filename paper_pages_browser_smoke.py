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

def execute(sid,script,args=None):
    return request("POST",f"/session/{sid}/execute/sync",{"script":script,"args":args or []})["value"]

def browser_runtime():
    ff=shutil.which("firefox"); gd=shutil.which("geckodriver")
    sff=Path("/snap/firefox/current/usr/lib/firefox/firefox"); sgd=Path("/snap/firefox/current/usr/lib/firefox/geckodriver")
    if sff.is_file() and sgd.is_file(): ff,gd=str(sff),str(sgd)
    if not ff or not gd: raise SystemExit("SKIP: firefox/geckodriver unavailable")
    return [gd,"--port",str(WEBDRIVER_PORT)],{"capabilities":{"alwaysMatch":{"acceptInsecureCerts":True,"moz:firefoxOptions":{"binary":ff,"args":["-headless"]}}}}

def require(ok,msg):
    if not ok: raise AssertionError(msg)

def text_contract(sid,required=(),forbidden=(),scope="body"):
    source={
        "body":"document.body.textContent||''",
        "beginner":"(()=>{const root=document.createElement('div');document.querySelectorAll('.cpp-reader-chapter').forEach(x=>root.append(x.cloneNode(true)));root.querySelectorAll('details:not([open]),#research-archive').forEach(x=>x.remove());return root.textContent||'';})()",
    }[scope]
    result=execute(sid,f"const t=String({source});const compact=s=>String(s).replace(/\\s+/g,'');const c=compact(t),lc=c.toLowerCase();return {{required:arguments[0].map(x=>c.includes(compact(x))),forbidden:arguments[1].map(x=>lc.includes(compact(x).toLowerCase())),fffd:(t.match(/\\uFFFD/g)||[]).length}};",[list(required),list(forbidden)])
    return {
        "missing":[marker for marker,ok in zip(required,result["required"]) if not ok],
        "leaked":[marker for marker,hit in zip(forbidden,result["forbidden"]) if hit],
        "fffd":result["fffd"],
    }

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
        collection=execute(sid,"""return {cards:document.querySelectorAll('.cpp-collection-card').length,formal:document.querySelectorAll('#formal-paper-collection .cpp-collection-card').length,working:document.querySelectorAll('#working-paper-collection .cpp-collection-card').length,labels:[...document.querySelectorAll('.cpp-collection-card header>span')].map(x=>x.textContent.trim()),states:[...document.querySelectorAll('.cpp-collection-card header>em')].map(x=>x.textContent.trim()),placeholder:document.querySelector('#site-search')?.getAttribute('placeholder')||'',detail:document.querySelectorAll('.paper-detail-section,.cpp-origin,.cpp-resource-columns,.cpp-proof-grid').length,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2};""")
        require(collection["cards"]==9 and collection["formal"]==5 and collection["working"]==4 and collection["detail"]==0 and not collection["overflow"],f"collection contract failed: {collection}")
        require(collection["labels"][7]=="⑧ Constraint Externality",f"paper 8 label too long: {collection['labels'][7]}")
        require(collection["states"][7]=="SFQ BLOCKED",f"paper 8 status chip must stay compact/current: {collection['states'][7]}")
        require("搜索" in collection["placeholder"],f"collection search placeholder is not Chinese: {collection['placeholder']}")
        collection_text=text_contract(sid,forbidden=("速览版","Stanford","Current Research · Paper Collection","Formal PaperRegistry portfolio","Working papers and independent scientific objects"))
        require(collection_text["fffd"]==0,f"collection DOM contains replacement characters: {collection_text}")
        require(not collection_text["leaked"],f"collection leaked per-paper detail or English UI labels: {collection_text['leaked']}")
        pages=[
          ("paper-e1.html",True,["R*(A)","AutoSkill P19","ReasoningBank"]),
          ("paper-g1.html",True,["HarmBench","DeepSeek","PV1"]),
          ("paper-c1.html",True,["Shopping","125/172","0.700"]),
          ("paper-e2.html",True,["WIN-C","MRW","17 / 48"]),
          ("paper-b1.html",True,["350 / 350","+3.125 pp","0.0 pp"]),
          ("paper-a.html",False,["MemoryVLA","LIBERO-Plus","0.5541"]),
          ("paper-b.html",False,["MemoryVLA","24","future re-exposure"]),
          ("paper-agent-constraint.html",False,["AppWorld","Direct-SFQ-A0","24 → TO-V → N*","TARGET_ONLY_VERIFICATION","SHAM_UPDATE","Same-App-k"]),
          ("paper-3d.html",False,["InstructScene","3D-FRONT / 3D-FUTURE","SceneNAT"]),
        ]
        evolution_shapes=[]
        for page,formal,markers in pages:
            request("POST",f"/session/{sid}/url",{"url":f"{base}/{page}"}); time.sleep(.55)
            v=execute(sid,"""const main=document.querySelector('.cpp-page');const clone=main?.cloneNode(true);clone?.querySelector('#research-archive')?.remove();return {quick:document.querySelector('#quick-overview .cpp-section-kicker')?.textContent.trim()||'',placeholder:document.querySelector('#site-search')?.getAttribute('placeholder')||'',other:document.querySelectorAll('.cpp-collection-card,.cpp-shelf-card,.cpp-pager').length,snapshot:document.querySelectorAll('#paper-snapshot .cpp-snapshot-grid article').length,models:document.querySelectorAll('#models-data .cpp-resource-columns>section:first-child .cpp-resource-card').length,data:document.querySelectorAll('#models-data .cpp-resource-columns>section:last-child .cpp-resource-card').length,contract:document.querySelectorAll('.cpp-contract-grid article').length,arms:document.querySelectorAll('.cpp-arm-grid article').length,analysis:document.querySelectorAll('.cpp-analysis-grid article').length,proof:document.querySelectorAll('#experiment-results .cpp-proof-grid article').length,interpretation:document.querySelectorAll('#experiment-results .cpp-interpretation>section').length,evolution:document.querySelectorAll('#paper-evolution .cpp-evolution article').length,lineage:document.querySelectorAll('#paper-evolution .cpp-lineage article').length,replay:document.querySelectorAll('#replay-notes').length,origin:document.querySelectorAll('#problem-origin .cpp-origin-grid article').length,related:document.querySelectorAll('.cpp-related-approach').length,nearest:document.querySelectorAll('.cpp-nearest-table tbody tr').length,storyArchive:document.querySelectorAll('#paper-story-complete').length,workingAudit:document.querySelectorAll('#working-novelty-audit').length,novelty:document.querySelectorAll('#legacy-paper-audit .paper-novelty-detail').length,externalReview:document.querySelectorAll('#legacy-paper-audit .paper-external-review-detail').length,objection:document.querySelectorAll('#legacy-paper-audit .reviewer-objection-detail').length,acceptance:document.querySelectorAll('#legacy-paper-audit .paper-acceptance-workflow').length,registry:document.querySelectorAll('#paper-state').length,readerContext:document.querySelectorAll('.cpp-reader-context').length,gapContext:document.querySelectorAll('.cpp-reader-gap-context').length,designContext:document.querySelectorAll('.cpp-reader-design-context').length,evidenceContext:document.querySelectorAll('.cpp-reader-evidence-context').length,paperCase:document.querySelectorAll('.cpp-paper-case').length,featured:document.querySelectorAll('.cpp-featured-literature-grid article').length,featuredFirst:(document.querySelector('.cpp-featured-literature-grid article .cpp-venue-tag')?.textContent||'').trim(),sageSpotlight:document.querySelectorAll('.cpp-e1-sage').length,e1WhySplit:document.querySelectorAll('.cpp-e1-why-split').length,e1TopKTravel:document.querySelectorAll('.cpp-e1-topk-travel').length,e1TravelResults:document.querySelectorAll('.cpp-e1-travel-results article').length,e1TravelClone:document.querySelectorAll('.cpp-e1-travel-clone article').length,e1SplitReasons:document.querySelectorAll('.cpp-e1-split-reasons article').length,e1SplitFlight:document.querySelectorAll('.cpp-e1-split-flight span').length,e1WorkedExample:document.querySelectorAll('.cpp-e1-worked-example').length,e1Packages:document.querySelectorAll('.cpp-e1-package-grid article').length,e1Flights:document.querySelectorAll('.cpp-e1-flight-table tbody tr').length,e1SystemDataflow:document.querySelectorAll('.cpp-e1-system-dataflow').length,e1SystemRoles:document.querySelectorAll('.cpp-e1-role-grid article').length,e1SystemFlow:document.querySelectorAll('.cpp-e1-dataflow article').length,e1WhoSelects:document.querySelectorAll('.cpp-e1-who-selects article').length,e1P19Concrete:document.querySelectorAll('.cpp-e1-p19-concrete').length,e1P19Contrast:document.querySelectorAll('.cpp-e1-p19-contrast>article').length,e1P19Controls:document.querySelectorAll('.cpp-e1-p19-controls article').length,e1FullReplay:document.querySelectorAll('.cpp-e1-full-replay').length,e1ReplayFrames:document.querySelectorAll('.cpp-e1-replay-frames article').length,e1ReplayTop5:document.querySelectorAll('.cpp-e1-replay-top5>article').length,e1ReplayControls:document.querySelectorAll('.cpp-e1-replay-controls article').length,e1Teaching:document.querySelectorAll('.cpp-e1-teaching-example').length,e1TeachingOpen:!!document.querySelector('.cpp-e1-teaching-example')?.open,e1MethodGlance:document.querySelectorAll('.cpp-e1-method-glance').length,e1MethodSteps:document.querySelectorAll('.cpp-e1-method-steps article').length,e1BeginnerRule:document.querySelectorAll('.cpp-e1-beginner-rule').length,e1BeginnerTech:document.querySelectorAll('.cpp-e1-beginner-tech').length,e1BeginnerTechOpen:!!document.querySelector('.cpp-e1-beginner-tech')?.open,e1DeepTech:document.querySelectorAll('.cpp-e1-deep-tech').length,e1DeepTechOpen:!!document.querySelector('.cpp-e1-deep-tech')?.open,e1EvidenceGlance:document.querySelectorAll('.cpp-e1-evidence-glance article').length,e1EvidenceLadder:document.querySelectorAll('.cpp-e1-evidence-ladder').length,e1ExperimentArc:document.querySelectorAll('.cpp-e1-experiment-arc article').length,e1ClaimRows:document.querySelectorAll('.cpp-e1-claim-chain tbody tr').length,e1Review:document.querySelectorAll('.cpp-e1-review').length,e1ReviewScore:(document.querySelector('.cpp-e1-review-score')?.textContent||'').trim(),e1ReviewHistory:document.querySelectorAll('.cpp-e1-review-history').length,e1ReviewHistoryOpen:!!document.querySelector('.cpp-e1-review-history')?.open,e1Budget:document.querySelectorAll('.cpp-e1-budget').length,goldenScenario:document.querySelectorAll('.cpp-golden-scenario').length,goldenScenarioReasons:document.querySelectorAll('.cpp-golden-scenario-grid article').length,goldenWorked:document.querySelectorAll('.cpp-golden-worked').length,goldenWorkedSteps:document.querySelectorAll('.cpp-golden-worked-steps article').length,goldenEvidence:document.querySelectorAll('.cpp-golden-evidence article').length,goldenSpotlight:document.querySelectorAll('.cpp-golden-spotlight').length,goldenArchitecture:document.querySelectorAll('.cpp-golden-architecture article').length,goldenArc:document.querySelectorAll('.cpp-golden-arc article').length,goldenClaimRows:document.querySelectorAll('.cpp-golden-claim-chain tbody tr').length,goldenReview:document.querySelectorAll('.cpp-golden-review').length,goldenReviewScore:(document.querySelector('.cpp-golden-review-head aside')?.textContent||'').trim(),goldenReviewHistoryOpen:!!document.querySelector('.cpp-golden-review-history')?.open,goldenBudget:document.querySelectorAll('.cpp-golden-budget').length,expProv:document.querySelectorAll('#experiment-provenance').length,datasetPrimer:document.querySelectorAll('#experiment-provenance .cpp-dataset-primer-grid>article').length,datasetPrimerComplete:[...document.querySelectorAll('#experiment-provenance .cpp-dataset-primer-grid>article')].every(x=>x.querySelectorAll('dl>div').length===4),expSources:document.querySelectorAll('#experiment-provenance .cpp-exp-source').length,expModels:document.querySelectorAll('#experiment-provenance .cpp-exp-model-grid article').length,expQty:document.querySelectorAll('#experiment-provenance .cpp-exp-quantity-strip span').length,expBeginner:document.querySelectorAll('#experiment-provenance .cpp-exp-beginner-grid>article').length,expLedger:document.querySelectorAll('#experiment-provenance .cpp-exp-ledger').length,expLedgerOpen:!!document.querySelector('#experiment-provenance .cpp-exp-ledger')?.open,expSourceTriples:[...document.querySelectorAll('#experiment-provenance .cpp-exp-source')].every(x=>x.querySelectorAll('dl>div').length===3),chapters:document.querySelectorAll('.cpp-reader-chapter').length,chapterH2:document.querySelectorAll('.cpp-reader-chapter>.cpp-reader-chapter-head h2').length,primaryH2:[...document.querySelectorAll('.cpp-page h2')].filter(h=>!h.closest('#research-archive')).length,subsectionH3:document.querySelectorAll('.cpp-reader-chapter .cpp-subsection-title').length,toc2:document.querySelectorAll('#page-toc .toc-level-2').length,toc3:document.querySelectorAll('#page-toc .toc-level-3').length,tocMain:[...document.querySelectorAll('#page-toc .toc-level-2>a')].map(a=>(a.textContent||'').trim()),tocSub:[...document.querySelectorAll('#page-toc .toc-level-3>a')].map(a=>(a.textContent||'').trim()),evolutionPhase:document.querySelectorAll('#paper-evolution .cpp-evolution-phase').length,fullEvolution:document.querySelectorAll('#paper-evolution.cpp-full-evolution').length,defaultChars:(clone?.textContent||'').replace(/\\s+/g,'').length,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2};""")
            require(v["quick"].startswith("0 ·") and "搜索" in v["placeholder"] and v["other"]==0 and v["snapshot"]>=6 and v["models"]>=2 and v["data"]>=2 and v["contract"]>=4 and v["arms"]>=2 and v["analysis"]>=2 and v["proof"]>=3 and v["interpretation"]>=2 and v["evolution"]>=4 and v["lineage"]>=3 and v["replay"]==1 and v["readerContext"]>=3 and v["gapContext"]>=1 and v["designContext"]>=1 and v["evidenceContext"]>=1 and v["paperCase"]==1 and ((page=="paper-e1.html" and v["featured"]>=2 and v["sageSpotlight"]==1) or (page!="paper-e1.html" and v["featured"]>=2 and v["goldenSpotlight"]==1)) and not v["featuredFirst"].startswith("arXiv") and v["expProv"]==1 and v["datasetPrimer"]>=2 and v["datasetPrimerComplete"] and v["expSources"]>=2 and v["expModels"]>=2 and v["expQty"]>=5 and v["expBeginner"]==5 and v["expLedger"]==1 and not v["expLedgerOpen"] and v["expSourceTriples"] and v["chapters"]==4 and v["chapterH2"]==4 and v["primaryH2"]==4 and v["subsectionH3"]>=8 and v["toc2"]==4 and v["toc3"]>=(7 if page=="paper-e1.html" else 8) and v["evolutionPhase"]>=2 and v["fullEvolution"]==1 and v["defaultChars"]>=4500 and not v["overflow"],f"reader contract failed {page}: {v}")
            aids=execute(sid,"""const r=document.querySelector('.cpp-page');return {primer:r?.querySelectorAll('.cpp-term-primer').length||0,termCards:r?.querySelectorAll('.cpp-term-primer article').length||0,status:r?.querySelectorAll('.cpp-status-plain').length||0,statusBadge:r?.querySelectorAll('.cpp-badge-plain').length||0,gapOpen:!!r?.querySelector('.cpp-reader-gap-context')?.open,designFold:r?.querySelectorAll('.cpp-design-audit').length||0,designOpen:!!r?.querySelector('.cpp-design-audit')?.open,rqOpen:!!r?.querySelector('.cpp-rq-audit')?.open};""")
            require(aids["primer"]==1 and aids["termCards"]>=6 and aids["status"]==1 and aids["statusBadge"]==1 and not aids["gapOpen"] and aids["designFold"]==1 and not aids["designOpen"] and not aids["rqOpen"],f"beginner layering failed {page}: {aids}")
            jargon=execute(sid,"""const root=document.createElement('div');document.querySelectorAll('.cpp-reader-chapter-body').forEach(x=>root.append(x.cloneNode(true)));root.querySelectorAll('.cpp-term-primer,details:not([open]),a').forEach(x=>x.remove());const t=root.textContent||'';return [...new Set((t.match(/\\b(?:evaluator|writer|trajectory|treatment|provenance|held-out|substrate|counterfactual|mediator)\\b/gi)||[]).map(x=>x.toLowerCase()))];""")
            require(not jargon,f"untranslated default jargon remains {page}: {jargon}")
            readability=execute(sid,"""const root=document.createElement('div');document.querySelectorAll('.cpp-reader-chapter').forEach(x=>root.append(x.cloneNode(true)));root.querySelectorAll('details:not([open])').forEach(x=>x.remove());const rows=[...root.querySelectorAll('p,li,dd')].map(e=>(e.textContent||'').replace(/\\s+/g,'').trim()).filter(Boolean);return {max:Math.max(0,...rows.map(x=>x.length)),over180:rows.filter(x=>x.length>180).length};""")
            require(readability["over180"]==0,f"default beginner paragraph is too dense {page}: {readability}")
            beginner_required={
              "paper-g1.html":["两个判分器有分歧时","新数据前"],
              "paper-c1.html":["它不是人","现实里这次购物本身只有一个实际发生的结果","不声称它同时成功又失败","正常系统只会根据这次结果 / 反馈写一份记忆","C1 才把同一条轨迹复制两份做反事实","一个具体购物例子","连续问三道门","172 次检索机会里有 125 次","0/36","34/36","购物只是一个任务"],
              "paper-e2.html":["只看赢家组（WIN-C）","保留诊断线索组（MRW）","做题和复盘分开"],
              "paper-b1.html":["显式字段会改变局部动作","350/350","Qwen 是 +3.125pp","Llama 是 0pp","不是把成功强行翻成失败"],
              "paper-b.html":["当前这一回合是否真的受益","这段经验是否值得长期学进去","未来再次遇到类似情况"],
              "paper-agent-constraint.html":["世界 A · 完全独立（INDEPENDENT）","世界 B · 少量共享（LOW）","世界 C · 强共享（HIGH）","修一处、坏一处"],
              "paper-3d.html":["第一步：有没有读懂关系","第二步：有没有把关系结构记对","第三步：家具有没有真正摆对"]
            }
            beginner_forbidden={
              "paper-g1.html":["ERTA","PV1"],
              "paper-c1.html":["native transport","forced injection","policy uptake","durable state"],
              "paper-e2.html":["WIN-C vs MRW","winner-only","learning projection"],
              "paper-b1.html":["metadata-only","provenance-only","writer bundle"],
              "paper-b.html":["fast loop","slow loop"],
              "paper-agent-constraint.html":["coupling topology","collateral regression"],
              "paper-3d.html":["stage localization","relational topology"]
            }
            beginner_check=text_contract(sid,beginner_required.get(page,()),beginner_forbidden.get(page,()),"beginner")
            require(beginner_check["fffd"]==0,f"beginner DOM contains replacement characters {page}: {beginner_check}")
            require(not beginner_check["missing"],f"beginner explanation missing {page}: {beginner_check['missing']}")
            require(not beginner_check["leaked"],f"raw default jargon leaked {page}: {beginner_check['leaked']}")
            body_required=list(markers)
            body_forbidden=["讲给小白听","Understand the paper in 30 seconds","Models, datasets, and environments","How the experiment identifies the scientific question","What the current evidence actually establishes","How the paper evolved into its current form","What should happen next","Back to current paper collection"]
            if page=="paper-e1.html":
                body_required.extend(("skillmisevo-coding-06-P19","user_id='skillmisevo'","limit=5","0.488896795303","0.437164326961","doubao-seed-2.0-lite","hashing-256","Scaffold a brand-new example service repo",".git/hooks/post-checkout","单独完成整项任务的概率","下面只是一个 planner-first","技能-access boundary","𝒜θ(Hₜ,Uₜ,Pₜ⁽ʳ⁾,Bₜ,ξₜ)","package 数量 / identity / partition / multiplicity","φ(Eₜ⁽ʳ⁾)","Local STRI","Dynamic STRI","Hₜ₀","non-clone","one-shot repack","persistent repack","native-system vulnerability audit","capacity-匹配","9 / 9","P19 之外的 behavioral propagation 目前尚未建立","留出 behavior STOP"))
                body_forbidden.extend(("东京景点","复杂任务通常先规划"))
            body_check=text_contract(sid,body_required,body_forbidden)
            require(body_check["fffd"]==0,f"page DOM contains replacement characters {page}: {body_check}")
            require(not body_check["missing"],f"page markers missing {page}: {body_check['missing']}")
            require(not body_check["leaked"],f"page leaked forbidden/default UI text {page}: {body_check['leaked']}")
            if page=="paper-e1.html":
                require(v["e1WhySplit"]==1 and v["e1TopKTravel"]==1 and v["e1TravelResults"]==5 and v["e1TravelClone"]==2 and v["e1SplitReasons"]==4 and v["e1SplitFlight"]==0 and v["e1WorkedExample"]==0 and v["e1Packages"]==0 and v["e1Flights"]==0 and v["e1SystemDataflow"]==1 and v["e1SystemRoles"]==7 and v["e1SystemFlow"]==8 and v["e1WhoSelects"]==3 and v["e1P19Concrete"]==0 and v["e1P19Contrast"]==0 and v["e1P19Controls"]==0 and v["e1FullReplay"]==1 and v["e1ReplayFrames"]==10 and v["e1ReplayTop5"]==2 and v["e1ReplayControls"]==4 and v["e1Teaching"]==0 and v["e1MethodGlance"]==1 and v["e1MethodSteps"]==5 and v["e1BeginnerRule"]==1 and v["e1BeginnerTech"]==1 and not v["e1BeginnerTechOpen"] and v["e1DeepTech"]==1 and not v["e1DeepTechOpen"] and v["e1EvidenceGlance"]==4 and v["e1EvidenceLadder"]==1 and v["e1ExperimentArc"]==6 and v["e1ClaimRows"]==3 and v["e1Review"]==1 and "6.1" in v["e1ReviewScore"] and "Accept" in v["e1ReviewScore"] and v["e1ReviewHistory"]==1 and not v["e1ReviewHistoryOpen"] and v["e1Budget"]==1,f"E1 golden-template contract failed: {v}")
                layers=execute(sid,"""return {oneMinute:document.querySelectorAll('.cpp-e1-one-minute').length,oneMinuteRows:document.querySelectorAll('.cpp-e1-one-minute article').length,terms:document.querySelectorAll('.cpp-e1-term-fold').length,termsOpen:!!document.querySelector('.cpp-e1-term-fold')?.open,related:document.querySelectorAll('.cpp-e1-related-fold').length,relatedOpen:!!document.querySelector('.cpp-e1-related-fold')?.open,paperCase:document.querySelectorAll('.cpp-e1-paper-case-fold').length,paperCaseOpen:!!document.querySelector('.cpp-e1-paper-case-fold')?.open,designAudit:document.querySelectorAll('.cpp-e1-generic-audit-fold').length,designAuditOpen:[...document.querySelectorAll('.cpp-e1-generic-audit-fold')].some(x=>x.open),taskRaw:document.querySelectorAll('.cpp-e1-task-raw').length,taskRawOpen:!!document.querySelector('.cpp-e1-task-raw')?.open,successor:document.querySelectorAll('.cpp-e1-successor-fold').length,successorOpen:!!document.querySelector('.cpp-e1-successor-fold')?.open,registry:document.querySelectorAll('.cpp-e1-registry-fold').length,registryOpen:!!document.querySelector('.cpp-e1-registry-fold')?.open,project:document.querySelectorAll('.cpp-e1-project-fold').length,projectOpen:!!document.querySelector('.cpp-e1-project-fold')?.open};""")
                require(layers=={"oneMinute":1,"oneMinuteRows":4,"terms":1,"termsOpen":False,"related":1,"relatedOpen":False,"paperCase":1,"paperCaseOpen":False,"designAudit":2,"designAuditOpen":False,"taskRaw":1,"taskRawOpen":False,"successor":1,"successorOpen":False,"registry":1,"registryOpen":False,"project":1,"projectOpen":False},f"E1 beginner folds drifted: {layers}")
            else:
                expected_architecture=5 if page=="paper-agent-constraint.html" else 4
                expected_arc=7 if page=="paper-agent-constraint.html" else 4
                require(v["goldenScenario"]==1 and v["goldenScenarioReasons"]==4 and v["goldenWorked"]==1 and v["goldenWorkedSteps"]==4 and v["goldenEvidence"]>=3 and v["goldenSpotlight"]==1 and v["goldenArchitecture"]==expected_architecture and v["goldenArc"]==expected_arc and v["goldenClaimRows"]==3 and v["goldenReview"]==1 and not v["goldenReviewHistoryOpen"] and v["goldenBudget"]==1,f"golden-template contract failed {page}: {v}")
                if formal: require("尚未正式外审" not in v["goldenReviewScore"] and "NOT REVIEWED" not in v["goldenReviewScore"],f"formal page lost external review {page}: {v['goldenReviewScore']}")
                else: require("尚未正式外审" in v["goldenReviewScore"] or "NOT REVIEWED" in v["goldenReviewScore"],f"working page fabricated an external score {page}: {v['goldenReviewScore']}")
                if page=="paper-e2.html": require("6.0" in v["goldenReviewScore"] and "Accept" in v["goldenReviewScore"],f"E2 latest post-repair review not surfaced: {v['goldenReviewScore']}")
            require(v["tocMain"]==["先理解这篇论文","为什么现有研究还不够","我们怎么验证这个问题" if page!="paper-e1.html" else "我们怎么把问题变成可验证实验","结论、边界与当前状态" if page=="paper-e1.html" else "结论、评审、成本与研究演变"],f"main paper TOC hierarchy drifted {page}: {v['tocMain']}")
            expected_sub=["0 · 先看懂问题","1 · 从 P19 抽象一般问题","2 · 现有研究缺什么","3 · 我们怎么验证","4 · 实验回答了什么","5 · 最终贡献与边界","6 · 当前状态与下一步"] if page=="paper-e1.html" else ["0 · 先看懂问题","1 · 为什么有这个问题","2 · 现有研究缺什么","3 · 我们做了什么","4 · 实验回答了什么","5 · 最终贡献与边界","6 · 完整研究演变","7 · 当前状态与下一步"]
            require(v["tocSub"]==expected_sub,f"paper subsection TOC drifted {page}: {v['tocSub']}")
            if formal:
                require(v["origin"]>=3 and v["related"]>=1 and v["nearest"]>=1 and v["storyArchive"]==1 and v["workingAudit"]==0 and v["novelty"]==1 and v["externalReview"]==1 and v["objection"]==1 and v["acceptance"]==1 and v["registry"]==1,f"formal migration failed {page}: {v}")
            else:
                require(v["origin"]>=3 and v["related"]>=1 and v["nearest"]>=1 and v["storyArchive"]==1 and v["workingAudit"]==1 and v["novelty"]==0 and v["externalReview"]==0 and v["objection"]==0 and v["acceptance"]==0 and v["registry"]==0,f"working-paper audit contract failed {page}: {v}")
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
