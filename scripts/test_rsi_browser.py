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
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tmp'/'rsi-qa-20261021'
PAGES=['index','literature','reading-cards','cross-domain','learning-science','ideas','teaching','experiments','references']

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
        with urllib.request.urlopen(request,timeout=65) as response: return json.load(response)['value']
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
            stats=js("""return {title:document.title,h1:document.querySelectorAll('h1').length,active:document.querySelectorAll('#research-nav a[aria-current="page"]').length,nav:document.querySelectorAll('#research-nav a[href*="/rsi/"]').length,overflow:document.documentElement.scrollWidth>innerWidth+1,cites:document.querySelectorAll('.cite').length,sections:document.querySelectorAll('.research-section').length};""")
            check(stats['h1']==1 and stats['active']==1 and stats['nav']==len(PAGES),slug+': nav or title integrity '+str(stats))
            check(not stats['overflow'],slug+': desktop page overflow')
            summaries.append({'page':slug,**stats})
        nav('rsi/reading-cards.html')
        check(js("return document.querySelectorAll('.reading-card').length>=1"),'Reading-card library is empty')
        js("const q=document.querySelector('#reading-card-filter');q.value='不存在的测试查询';q.dispatchEvent(new Event('input',{bubbles:true}));")
        check(js("return document.querySelectorAll('.reading-card:not([hidden])').length===0"),'Paper-card filtering failed')
        js("const q=document.querySelector('#reading-card-filter');q.value='R²Orch';q.dispatchEvent(new Event('input',{bubbles:true}));")
        check(js("return document.querySelectorAll('.reading-card:not([hidden])').length===1"),'Paper-card search did not find R²Orch')
        screenshot('reading-cards-desktop.png')
        nav('rsi/index.html'); screenshot('overview-desktop.png')
        js("const q=document.querySelector('#research-search');q.value='SOAR';q.dispatchEvent(new Event('input',{bubbles:true}));")
        for _ in range(25):
            if js("return document.querySelectorAll('.search-hit').length>0"): break
            time.sleep(.2)
        check(js("return document.querySelectorAll('.search-hit').length>0"),'Search does not execute')
        js("const q=document.querySelector('#research-search');q.value='';q.dispatchEvent(new Event('input',{bubbles:true}));")
        check(js("return document.querySelector('#search-results').hidden"),'Search does not clear')
        before=js("return document.querySelector('#nav-language').textContent")
        js("document.querySelector('#nav-language').click()")
        check(js("return document.querySelector('#nav-language').textContent")!=before,'Navigation language toggle failed')
        nav('rsi/ideas.html'); js("document.querySelector('#idea-1').scrollIntoView()")
        screenshot('idea-framework-desktop.png')
        req('POST',f'/session/{session}/window/rect',{'width':390,'height':844})
        for slug in ['index','reading-cards','ideas','teaching','experiments','references']:
            nav('rsi/'+slug+'.html')
            check(not js('return document.documentElement.scrollWidth>innerWidth+1'),slug+': mobile horizontal overflow')
        nav('rsi/index.html'); screenshot('overview-mobile.png')
        js("document.querySelector('#menu-toggle').click()")
        check(js("return document.querySelector('#sidebar').classList.contains('open')&&!document.querySelector('#sidebar-overlay').hidden"),'Mobile drawer did not open')
        screenshot('navigation-mobile.png')
        js("document.querySelector('#sidebar-close').click()")
        check(js("return !document.querySelector('#sidebar').classList.contains('open')&&document.querySelector('#sidebar-overlay').hidden"),'Mobile drawer did not close')
        req('POST',f'/session/{session}/window/rect',{'width':1440,'height':1050})
        nav('index.html')
        for _ in range(30):
            if js("return document.querySelectorAll('.nav a[href^="+'"rsi/"'+"]').length===9"): break
            time.sleep(.3)
        check(js("return document.querySelectorAll('.nav a[href^="+'"rsi/"'+"]').length===9"),'Root site lacks new sidebar entry')
        result={'status':'PASS','pages':summaries,'search':'PASS','language':'PASS','mobile':'PASS','root_navigation':'PASS','screenshots':5}
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
