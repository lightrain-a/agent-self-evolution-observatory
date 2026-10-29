#!/usr/bin/env python3
"""Browser geometry regression for the shared RSI layout, at three real viewports.

Requires generated _site/rsi, Firefox and geckodriver. Source registries are read
only. Screenshots and measured geometry go to tmp/rsi-compact-layout-qa/.
"""
from __future__ import annotations
import base64
import json
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tmp'/'rsi-compact-layout-qa'
REPRESENTATIVES={'index','timeline','ideas','reading-cards','reading-notes','literature','learning-rule-evolution','generalization-learnability'}

def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));return sock.getsockname()[1]

def main():
    if not shutil.which('firefox') or not shutil.which('geckodriver'):
        raise SystemExit('Firefox and geckodriver are required for layout verification')
    pages=sorted(p.stem for p in (ROOT/'_site/rsi').glob('*.html'))
    if not pages:raise SystemExit('Build the RSI site first')
    OUT.mkdir(parents=True,exist_ok=True)
    hp,gp=free_port(),free_port()
    while hp==gp:gp=free_port()
    session='';procs=[];measured=[];shots=[];log=(OUT/'webdriver.log').open('w')
    def req(method,path,data=None):
        request=urllib.request.Request(f'http://127.0.0.1:{gp}'+path,
            data=json.dumps(data).encode() if data is not None else None,
            method=method,headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(request,timeout=65) as response:return json.load(response)['value']
        except urllib.error.HTTPError as exc:
            raise AssertionError(exc.read().decode(errors='replace')[:1600]) from exc
    def js(code):return req('POST',f'/session/{session}/execute/sync',{'script':code,'args':[]})
    def check(test,msg):
        if not test:raise AssertionError(msg)
    def nav(path):
        req('POST',f'/session/{session}/url',{'url':f'http://127.0.0.1:{hp}/rsi/'+path+'.html'})
        time.sleep(.22)
    def shot(name):
        (OUT/name).write_bytes(base64.b64decode(req('GET',f'/session/{session}/screenshot')))
        shots.append(name)
    try:
        procs.append(subprocess.Popen([sys.executable,'-m','http.server',str(hp),'--bind','127.0.0.1'],cwd=ROOT/'_site',stdout=log,stderr=log))
        procs.append(subprocess.Popen(['geckodriver','--port',str(gp)],stdout=log,stderr=log))
        for _ in range(40):
            try:req('GET','/status');break
            except Exception:time.sleep(.2)
        session=req('POST','/session',{'capabilities':{'alwaysMatch':{'acceptInsecureCerts':True,'moz:firefoxOptions':{'args':['-headless']}}}})['sessionId']
        for width,height in [(1440,1050),(1920,1080),(390,844)]:
            req('POST',f'/session/{session}/window/rect',{'width':width,'height':height})
            for slug in pages:
                nav(slug)
                m=js('''const content=document.querySelector('.content'),hero=document.querySelector('.research-hero'),h1=document.querySelector('h1'),section=document.querySelector('.research-section'),bar=document.querySelector('.topbar'),c=getComputedStyle(content),r=h1.getBoundingClientRect();return {
                    page:document.body.dataset.rsiPage,h1Count:document.querySelectorAll('h1').length,
                    overflow:document.documentElement.scrollWidth>innerWidth+1,
                    contentTop:parseFloat(c.paddingTop),gutter:parseFloat(c.paddingLeft),
                    headingSize:parseFloat(getComputedStyle(h1).fontSize),headingWithinViewport:r.left>=-1&&r.right<=innerWidth+1,
                    heroHeight:Math.round(hero.getBoundingClientRect().height),heroTop:Math.round(hero.getBoundingClientRect().top),
                    firstSectionTop:Math.round(section.getBoundingClientRect().top),barHeight:Math.round(bar.getBoundingClientRect().height),
                    bodyTextSize:parseFloat(getComputedStyle(document.querySelector('.section-body')).fontSize),
                    sharedStyle:[...document.querySelectorAll('link[rel=stylesheet]')].at(-1)?.getAttribute('href').split('?')[0],
                    sidebarWidth:Math.round(document.querySelector('.sidebar').getBoundingClientRect().width)
                }''')
                m['viewport']=width;measured.append(m)
                check(m['h1Count']==1,f'{slug}/{width}: title count')
                check(not m['overflow'],f'{slug}/{width}: horizontal document overflow')
                check(m['headingWithinViewport'],f'{slug}/{width}: clipped page title')
                check(m['sharedStyle']=='compact.css',f'{slug}/{width}: shared density stylesheet not last')
                check(m['gutter']==(13 if width==390 else 22),f'{slug}/{width}: inconsistent gutter {m}')
                check(m['contentTop']==(14 if width==390 else 18),f'{slug}/{width}: inconsistent top padding')
                check(m['barHeight']<=65,f'{slug}/{width}: oversized topbar')
                check(m['headingSize']>=24,f'{slug}/{width}: title was reduced too far')
                check(m['bodyTextSize']>=14,f'{slug}/{width}: body prose lost readable size')
                check(m['heroHeight']<=(430 if width==390 else 245),f'{slug}/{width}: title region remains oversized: {m["heroHeight"]}')
                if width!=390:check(m['sidebarWidth']==276,f'{slug}/{width}: inconsistent sidebar')
                if slug in REPRESENTATIVES:shot(f'{slug}-{width}.png')
            nav('timeline')
            check(js("return document.querySelector('#rsi-tl-calendar-grid').dataset.calendarView==='activity'"),'Timeline should start in activity-interval calendar mode')
            before=js("return document.querySelector('[data-calendar-month=\"2026-10\"]').querySelectorAll('.rsi-tl-cal-day').length")
            js("document.querySelector('#rsi-tl-calendar-mode').click()")
            after=js("return document.querySelector('[data-calendar-month=\"2026-10\"]').querySelectorAll('.rsi-tl-cal-day').length")
            check(after==31 and after>=before,'Full October calendar toggle is incomplete')
            js("document.querySelector('#rsi-tl-calendar-mode').click()")
            js("document.querySelector('[data-calendar-day=\"2026-10-27\"]').click()")
            time.sleep(.7)
            check(js("return document.querySelector('[data-day=\"2026-10-27\"]').getAttribute('aria-expanded')==='true'"),'Calendar did not open date-table row')
            check(js("return !document.querySelector('[data-day-detail=\"2026-10-27\"]').hidden"),'Selected date details remain hidden')
            check(not js('return document.documentElement.scrollWidth>innerWidth+1'),'Expanded daily content overflows')
            shot(f'timeline-expanded-{width}.png')
            js("document.querySelector('.rsi-tl-item:not([hidden])').open=true")
            check(not js('return document.documentElement.scrollWidth>innerWidth+1'),'Expanded event content overflows')
        check((ROOT/'rsi/timeline-reference.css').read_bytes()==(ROOT/'research-timeline.css').read_bytes(),'Reference template stylesheet was silently forked')
        result={'status':'PASS','pages':len(pages),'viewports':[1440,1920,390],'page_viewports_tested':len(measured),'screenshots':len(shots),'measurements':measured}
        (OUT/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in result.items() if k!='measurements'},ensure_ascii=False))
        for m in measured:
            if m['viewport']==1440 and m['page'] in REPRESENTATIVES:print(json.dumps(m,ensure_ascii=False))
    finally:
        if session:
            try:req('DELETE',f'/session/{session}')
            except Exception:pass
        for proc in procs:
            proc.terminate()
            try:proc.wait(timeout=6)
            except subprocess.TimeoutExpired:proc.kill()
        log.close()

if __name__=='__main__':main()
