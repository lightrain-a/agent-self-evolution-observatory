#!/usr/bin/env python3
"""Real-browser QA for the RSI dossier; temporary servers are always cleaned up."""
from __future__ import annotations
import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tmp'/'rsi-qa-20261021'
PAGES=['index','timeline','literature','reading-cards','reading-notes','cross-domain','learning-science','ideas','idea-i5','idea-i6-failure-value','idea-i7-learning-order','i8','teaching','idea-i6','experiments','references']

def port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0)); return sock.getsockname()[1]

def main():
    firefox=shutil.which('firefox'); gecko=shutil.which('geckodriver')
    if not firefox or not gecko: raise SystemExit('SKIP: Firefox and geckodriver required')
    OUT.mkdir(parents=True,exist_ok=True)
    hp,dp=port(),port()
    while dp==hp: dp=port()
    processes=[]; session=''
    log=(OUT/'webdriver.log').open('w')
    def req(method,path,data=None):
        request=urllib.request.Request(f'http://127.0.0.1:{dp}'+path,data=json.dumps(data).encode() if data is not None else None,method=method,headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(request,timeout=65) as response: return json.load(response)['value']
        except urllib.error.HTTPError as exc:
            detail=exc.read().decode('utf-8', errors='replace')[:1200]
            raise AssertionError(f'WebDriver {method} {path} failed: {detail}') from exc
    def js(code): return req('POST',f'/session/{session}/execute/sync',{'script':code,'args':[]})
    def check(value,msg):
        if not value: raise AssertionError(msg)
    def nav(slug):
        req('POST',f'/session/{session}/url',{'url':f'http://127.0.0.1:{hp}/'+slug}); time.sleep(.6)
    def screenshot(name):
        (OUT/name).write_bytes(base64.b64decode(req('GET',f'/session/{session}/screenshot')))
    try:
        processes.append(subprocess.Popen([sys.executable,'-m','http.server',str(hp),'--bind','127.0.0.1'],cwd=ROOT/'_site',stdout=log,stderr=log))
        processes.append(subprocess.Popen([gecko,'--port',str(dp)],stdout=log,stderr=log))
        for _ in range(30):
            try:
                if req('GET','/status'): break
            except Exception: time.sleep(.3)
        session=req('POST','/session',{'capabilities':{'alwaysMatch':{'acceptInsecureCerts':True,'moz:firefoxOptions':{'args':['-headless']}}}})['sessionId']
        req('POST',f'/session/{session}/window/rect',{'width':1440,'height':1050})
        summaries=[]
        for slug in PAGES:
            nav('rsi/'+slug+'.html')
            stats=js("""const groups=[...document.querySelectorAll('#research-nav details.nav-group')];return {title:document.title,h1:document.querySelectorAll('h1').length,active:document.querySelectorAll('#research-nav a[aria-current="page"]').length,nav:document.querySelectorAll('#research-nav .nav-level2').length,groups:groups.length,expanded:groups.filter(g=>g.open).length,activeParents:groups.filter(g=>g.classList.contains('active-group')&&g.open).length,overflow:document.documentElement.scrollWidth>innerWidth+1,cites:document.querySelectorAll('.cite').length,sections:document.querySelectorAll('.research-section').length};""")
            check(stats['h1']==1 and stats['active']==1 and stats['nav']==len(PAGES) and stats['groups']==4 and stats['expanded']==1 and stats['activeParents']==1,slug+': two-level navigation or title integrity '+str(stats))
            check(not stats['overflow'],slug+': desktop page overflow')
            summaries.append({'page':slug,**stats})
        nav('rsi/index.html')
        rsi_switch=js("return [...document.querySelectorAll('.site-switcher__tab')].map(a=>({href:a.getAttribute('href'),active:a.getAttribute('aria-current')==='true'}));")
        check(rsi_switch==[{'href':'/','active':False},{'href':'/rsi/','active':True}],f'RSI switch destinations incorrect: {rsi_switch}')
        check(js("return [...document.querySelectorAll('#research-nav .nav-level2')].every(a=>!a.getAttribute('href').startsWith('../'))"),'RSI navigation not standalone')
        nav('rsi/timeline.html')
        timeline=json.loads((ROOT/'rsi/timeline-data.json').read_text(encoding='utf-8'))
        expected_deadlines=sum(d['status']=='official' for v in timeline['venues'] for d in v['deadlines'])
        pending_deadlines=sum(d['status']=='pending' for v in timeline['venues'] for d in v['deadlines'])
        reading_papers=json.loads((ROOT/'rsi/reading-cards.json').read_text(encoding='utf-8'))['papers']
        all_events=expected_deadlines+len(timeline['research_events'])+len(reading_papers)
        check(js("return document.querySelectorAll('.rsi-tl-venue').length")==3,'Missing target conference cards')
        check(js("return document.querySelectorAll('.rsi-tl-countdown').length")==expected_deadlines,'Wrong number of official countdowns')
        check(js("return document.querySelectorAll('.rsi-tl-pending').length")==pending_deadlines,'Unknown dates incorrectly assigned timers')
        check(js("return document.querySelectorAll('.rsi-tl-item').length")==all_events,'Timeline event count does not match source registry')
        check(js("return [...document.querySelectorAll('.rsi-tl-countdown')].every(e=>e.dataset.countdown.endsWith('-12:00') && Number.isFinite(Date.parse(e.dataset.countdown)))"),'AoE timestamps not parsed consistently')
        js("const k=document.querySelector('#rsi-tl-kind');k.value='deadline';k.dispatchEvent(new Event('change',{bubbles:true}))")
        check(js("return document.querySelectorAll('.rsi-tl-item:not([hidden])').length")==expected_deadlines,'Deadline filter failed')
        js("const k=document.querySelector('#rsi-tl-kind');k.value='reading';k.dispatchEvent(new Event('change',{bubbles:true}))")
        check(js("return document.querySelectorAll('.rsi-tl-item:not([hidden])').length")==len(reading_papers),'Reading filter failed')
        js("const t=document.querySelector('#rsi-tl-time');t.value='upcoming';t.dispatchEvent(new Event('change',{bubbles:true}))")
        check(js("return document.querySelectorAll('.rsi-tl-item:not([hidden])').length")==0,'Completed reading notes must not appear as upcoming')
        js("document.querySelector('#rsi-tl-reset').click()")
        check(js("return document.querySelectorAll('.rsi-tl-item:not([hidden])').length")==all_events,'Timeline reset did not restore all events')
        js("const q=document.querySelector('#rsi-tl-query');q.value='CVPR';q.dispatchEvent(new Event('input',{bubbles:true}))")
        check(js("return document.querySelectorAll('.rsi-tl-item:not([hidden])').length")==3,'Timeline conference search failed')
        js("document.querySelector('#rsi-tl-reset').click()")
        screenshot('timeline-desktop.png')
        nav('rsi/reading-cards.html')
        check(js("return document.querySelectorAll('.reading-card').length>=1"),'Reading-card library is empty')
        js("const q=document.querySelector('#reading-card-filter');q.value='不存在的测试查询';q.dispatchEvent(new Event('input',{bubbles:true}));")
        check(js("return document.querySelectorAll('.reading-card:not([hidden])').length===0"),'Paper-card filtering failed')
        cards=json.loads((ROOT/'rsi/reading-cards.json').read_text(encoding='utf-8'))['papers']
        check(js("return document.querySelectorAll('.reading-card').length")==len(cards),'Rendered card count does not match registry')
        for paper in cards:
            query=json.dumps(paper['short_title'],ensure_ascii=False)
            js(f"const q=document.querySelector('#reading-card-filter');q.value={query};q.dispatchEvent(new Event('input',{{bubbles:true}}));")
            check(js("return document.querySelectorAll('.reading-card:not([hidden])').length===1"),'Card search did not uniquely find '+paper['short_title'])
            check(js("return document.querySelector('.reading-card:not([hidden])').id")==paper['id'],'Card search matched wrong paper: '+paper['id'])
            check(js("return document.querySelector('.reading-card:not([hidden]) .reading-institution').textContent.includes("+json.dumps(paper['lead_institution'],ensure_ascii=False)+")"),'Institution not visible: '+paper['id'])
            check(js("return [...document.querySelectorAll('.reading-card:not([hidden]) .reading-story-step')].map(s=>s.dataset.storyStage).join(',')==='challenge,insight,design,result'"),
                  'First-read C-I-D-R steps missing or out of order: '+paper['id'])
            check(js("return !document.querySelector('.reading-card:not([hidden]) .reading-expand').open"),
                  'Dense paper evidence unexpectedly visible on card: '+paper['id'])
            js("document.querySelector('.reading-card:not([hidden]) .reading-expand').open=true")
            check(js("return document.querySelector('.reading-card:not([hidden]) .reading-question-details').children.length===5"),'Five-question details incomplete: '+paper['id'])
        js("const q=document.querySelector('#reading-card-filter');q.value='';q.dispatchEvent(new Event('input',{bubbles:true}));")
        for question,level in [('signal','core'),('novelty','partial'),('reach','core'),('retention','core'),('safety','addressed'),('safety','not_addressed')]:
            js(f"const q=document.querySelector('#reading-question-filter');q.value={json.dumps(question)};q.dispatchEvent(new Event('change',{{bubbles:true}}));")
            js(f"const q=document.querySelector('#reading-coverage-filter');q.value={json.dumps(level)};q.dispatchEvent(new Event('change',{{bubbles:true}}));")
            expected=sorted(p['id'] for p in cards if (
                p['research_coverage'][question]['level']!='not_addressed' if level=='addressed'
                else p['research_coverage'][question]['level']==level
            ))
            actual=js("return [...document.querySelectorAll('.reading-card:not([hidden])')].map(c=>c.id).sort()")
            check(actual==expected,f'Coverage filter mismatch {question}/{level}: {actual} vs {expected}')
        js("const q=document.querySelector('#reading-question-filter');q.value='all';q.dispatchEvent(new Event('change',{bubbles:true}));")
        js("const q=document.querySelector('#reading-coverage-filter');q.value='addressed';q.dispatchEvent(new Event('change',{bubbles:true}));")
        js("document.querySelectorAll('.reading-expand').forEach(d=>d.open=false)")
        check(js("return document.querySelector('.reading-card').id==='rsi-anything-2610-13912'"),
              'Featured deep-read paper should be the first visible reading card')
        screenshot('reading-cards-desktop.png')
        js("document.querySelector('#rsi-anything-2610-13912').scrollIntoView({block:'start'})")
        time.sleep(.8)
        screenshot('reading-first-card-desktop.png')
        for paper in cards:
            deep=paper.get('deep_read')
            if deep:
                q=json.dumps('#'+paper['id'])
                check(js(f"return document.querySelector({q}+' .reading-deep-link')!==null"),
                      'Deep-read link missing from compact card: '+paper['id'])
        nav('rsi/reading-notes.html')
        deep_cards=[p for p in cards if p.get('deep_read')]
        for paper in deep_cards:
            identifier='deep-'+paper['id']
            check(js("return document.querySelector("+json.dumps('#'+identifier)+")!==null"),
                  'Deep paper missing in browser: '+paper['id'])
            for section in paper['deep_read']['sections']:
                check(js("return document.querySelector("+json.dumps('#'+identifier+'--'+section['id'])+")!==null"),
                      'Deep section missing in browser: '+section['id'])
        check(js("return document.querySelectorAll('.deep-evidence').length>=4"),
              'Evidence matrix did not render')
        check(js("return [...document.querySelectorAll('.deep-stage')].map(s=>s.dataset.storyStage).join(',')==='challenge,insight,design,result,next'"),
              'Long read does not follow C-I-D-R before extensions')
        check(js("return document.querySelectorAll('.deep-chapter[open]').length===0"),
              'Detailed formulas or cases should start collapsed')
        check(js("return document.querySelector('.deep-terms').children.length===3"),
              'Terms are not explained before jargon')
        screenshot('reading-notes-desktop.png')
        js("document.querySelector('#deep-rsi-anything-2610-13912--stage-challenge').scrollIntoView({block:'start'})")
        time.sleep(.8)
        screenshot('reading-notes-story-desktop.png')
        js("document.querySelector('#deep-rsi-anything-2610-13912--example summary').click()")
        check(js("return document.querySelector('#deep-rsi-anything-2610-13912--example').open"),
              'Clicking the example did not expand it')
        check(js("return document.querySelector('.deep-stage[data-story-stage=design] .deep-chapter[open]')!==null"),
              'Design example is not accessible')
        screenshot('reading-notes-example-desktop.png')
        nav('rsi/index.html'); screenshot('overview-desktop.png')
        js("const q=document.querySelector('#research-search');q.value='SOAR';q.dispatchEvent(new Event('input',{bubbles:true}));")
        for _ in range(25):
            if js("return document.querySelectorAll('.search-hit').length>0"): break
            time.sleep(.2)
        check(js("return document.querySelectorAll('.search-hit').length>0"),'Search does not execute')
        js("const q=document.querySelector('#research-search');q.value='';q.dispatchEvent(new Event('input',{bubbles:true}));")
        check(js("return document.querySelector('#search-results').hidden"),'Search does not clear')
        # Primary headings are collapsible and remain expanded/collapsed when
        # switching languages; the second-level active link stays highlighted.
        js("""document.querySelector('#research-nav [data-nav-group="literature"] summary').click()""")
        check(js("""return document.querySelector('#research-nav [data-nav-group="literature"]').open"""),'Could not expand a primary folder')
        js("""document.querySelector('#research-nav [data-nav-group="overview"] summary').click()""")
        check(not js("""return document.querySelector('#research-nav [data-nav-group="overview"]').open"""),'Could not collapse active primary folder')
        before=js("return document.querySelector('#nav-language').textContent")
        js("document.querySelector('#nav-language').click()")
        check(js("return document.querySelector('#nav-language').textContent")!=before,'Navigation language toggle failed')
        check(js("""return document.querySelector('#research-nav [data-nav-group="literature"]').open && !document.querySelector('#research-nav [data-nav-group="overview"]').open"""),'Folder expansion was lost on language toggle')
        check(js("""return document.querySelector('#research-nav [data-nav-group="literature"] summary span').textContent==='Literature & Reading'"""),'English first-level titles are not rendered')
        check(js("""return document.querySelectorAll('#research-nav a[aria-current="page"]').length===1"""),'Current second-level page highlight lost')
        js("document.querySelector('#nav-language').click()")
        check(js("""return document.querySelector('#research-nav [data-nav-group="literature"] summary span').textContent==='文献与论文精读'"""),'Chinese primary heading not restored')
        nav('rsi/ideas.html')
        for idea_number in range(1, 6):
            steps=js(f"return [...document.querySelector('#idea-{idea_number}').querySelectorAll('.idea-step')].map(e=>({{heading:e.querySelector('h3').textContent.trim(),height:e.getBoundingClientRect().height}}));")
            check(len(steps)==5 and all(s['height']>35 for s in steps),f'I{idea_number} five-stage layout collapsed: {steps}')
            check([s['heading'].split(' ')[0] for s in steps]==['Challenge','现有工作','Insight','Design','实验设计'],f'I{idea_number} argument order wrong')
        js("document.querySelector('#idea-1').scrollIntoView()")
        screenshot('idea-framework-desktop.png')
        req('POST',f'/session/{session}/window/rect',{'width':390,'height':844})
        for slug in ['index','timeline','reading-cards','reading-notes','ideas','idea-i6-failure-value','idea-i7-learning-order','i8','idea-i6','teaching','experiments','references']:
            nav('rsi/'+slug+'.html')
            check(not js('return document.documentElement.scrollWidth>innerWidth+1'),slug+': mobile horizontal overflow')
        nav('rsi/ideas.html'); js("document.querySelector('#idea-1').scrollIntoView()")
        screenshot('idea-framework-mobile.png')
        nav('rsi/index.html'); screenshot('overview-mobile.png')
        js("document.querySelector('#menu-toggle').click()")
        check(js("return document.querySelector('#sidebar').classList.contains('open')&&!document.querySelector('#sidebar-overlay').hidden"),'Mobile drawer did not open')
        screenshot('navigation-mobile.png')
        js("""document.querySelector('#research-nav [data-nav-group="methods"] summary').click()""")
        check(js("""return document.querySelector('#research-nav [data-nav-group="methods"]').open && document.querySelector('#sidebar').classList.contains('open')"""),'Mobile expandable primary folder failed')
        js("""document.querySelector('#research-nav [data-nav-group="methods"] summary').click()""")
        check(not js("""return document.querySelector('#research-nav [data-nav-group="methods"]').open"""),'Mobile primary folder did not collapse')
        js("document.querySelector('#sidebar-close').click()")
        check(js("return !document.querySelector('#sidebar').classList.contains('open')&&document.querySelector('#sidebar-overlay').hidden"),'Mobile drawer did not close')
        req('POST',f'/session/{session}/window/rect',{'width':1440,'height':1050})
        nav('index.html')
        agent_switch=js("return [...document.querySelectorAll('.site-switcher__tab')].map(a=>({href:a.getAttribute('href'),active:a.getAttribute('aria-current')==='true'}));")
        check(agent_switch==[{'href':'/','active':True},{'href':'/rsi/','active':False}],f'Agent switch destinations incorrect: {agent_switch}')
        check(js("""return document.querySelectorAll('.sidebar .nav a[href^="rsi/"]').length===0"""),'Agent navigation still mixes RSI pages')
        js("document.querySelector('.site-switcher__tab[href=\"/rsi/\"]').click()")
        for _ in range(35):
            time.sleep(.2)
            if js("return location.pathname==='/rsi/' && document.body.dataset.rsiPage==='index'"): break
        check(js("return location.pathname==='/rsi/' && document.body.dataset.rsiPage==='index'"),'Agent to RSI switch failed')
        js("document.querySelector('.site-switcher__tab[href=\"/\"]').click()")
        for _ in range(35):
            time.sleep(.2)
            if js("return location.pathname==='/' && document.body.dataset.page==='home'"): break
        check(js("return location.pathname==='/' && document.body.dataset.page==='home'"),'RSI to Agent switch failed')
        nav('advisor-review.html')
        check(js("return document.querySelectorAll('.site-switcher__tab').length===2"),'Advisor Agent page lacks site switch')
        check(js("return document.querySelector('.site-switcher__tab[href=\"/rsi/\"]')!==null"),'Advisor page RSI link missing')
        result={'status':'PASS','pages':summaries,'search':'PASS','language':'PASS','mobile':'PASS','cross_site_switch':'PASS','independent_navigation':'PASS','screenshots':11}
        (OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(result,ensure_ascii=False,indent=2))
    finally:
        if session:
            try: req('DELETE',f'/session/{session}')
            except Exception: pass
        for proc in reversed(processes):
            if proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=8)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait(timeout=8)
        log.close()

if __name__=='__main__': main()
