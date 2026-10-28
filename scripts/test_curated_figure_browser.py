#!/usr/bin/env python3
"""Smoke-test the curated figure gallery in a real browser (including ICLR Fig.1)."""
from __future__ import annotations
import base64
import json
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '_site'
TMP = ROOT / 'tmp' / 'figure-gallery-qa'

def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]

def main() -> None:
    browser, driver = shutil.which('firefox'), shutil.which('geckodriver')
    if not browser or not driver:
        print('SKIP: Firefox and geckodriver required')
        return
    TMP.mkdir(parents=True, exist_ok=True)
    host_port, driver_port = free_port(), free_port()
    while driver_port == host_port:
        driver_port = free_port()
    processes = []
    session = ''
    log = (TMP / 'webdriver.log').open('w')
    def wd(method: str, route: str, payload: dict | None = None):
        url = f'http://127.0.0.1:{driver_port}{route}'
        request = urllib.request.Request(url,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={'Content-Type':'application/json'}, method=method)
        with urllib.request.urlopen(request, timeout=32) as response:
            obj = json.load(response)
        return obj['value']
    def js(script: str):
        return wd('POST', f'/session/{session}/execute/sync', {'script':script,'args':[]})
    def check(expr, message):
        if not expr: raise AssertionError(message)
    def screen(name: str) -> None:
        (TMP / name).write_bytes(base64.b64decode(wd('GET',f'/session/{session}/screenshot')))
    try:
        processes.append(subprocess.Popen(
            [sys.executable, '-m', 'http.server', str(host_port), '--bind', '127.0.0.1'],
            cwd=OUTPUT, stdout=log, stderr=log))
        processes.append(subprocess.Popen([driver,'--port',str(driver_port)],stdout=log,stderr=log))
        for _ in range(35):
            try:
                wd('GET','/status');break
            except Exception: time.sleep(.25)
        session=wd('POST','/session',{'capabilities':{'alwaysMatch':{
            'acceptInsecureCerts':True,'moz:firefoxOptions':{'args':['-headless']}}}})['sessionId']
        wd('POST',f'/session/{session}/window/rect',{'width':1450,'height':970})
        base=f'http://127.0.0.1:{host_port}'
        wd('POST',f'/session/{session}/url',{'url':base+'/figure-knowledge-base.html'})
        time.sleep(.8)
        check(js("return document.querySelectorAll('.reference-card').length") == 7,'Missing curated reference cards')
        check(js("return document.querySelectorAll('#curated-grid [data-id=iclr26-rote-learning-fig1]').length") == 1,
              'ICLR Figure 1 must be featured in gallery')
        js("document.querySelector('#ref-iclr26-rote-learning-fig1').scrollIntoView({block:'center'})")
        for _ in range(20):
            if js("return (()=>{const e=document.querySelector('#ref-iclr26-rote-learning-fig1 img');return e.complete&&e.naturalWidth>0})()"): break
            time.sleep(.15)
        image_state=js("return (()=>{const e=document.querySelector('#ref-iclr26-rote-learning-fig1 img');return {src:e.src,complete:e.complete,naturalWidth:e.naturalWidth,hidden:e.hidden,loading:e.loading}})()")
        check(image_state['complete'] and image_state['naturalWidth']>0,
              'Locally authored method-figure preview did not load after lazy-load exposure: '+str(image_state))
        check(js("return document.querySelector('#rote-fig1-inputs').textContent.includes('不需要模型准确率')"),
              'Input guide must explain conceptual vs measured inputs')
        check(js("return document.querySelector('#curated-metrics').textContent.includes('7')"),
              'Gallery source count incorrect')
        js("document.querySelector('[data-open=iclr26-rote-learning-fig1]').click()")
        time.sleep(.35)
        check(js("return document.querySelector('#figure-dialog').open"),'Details modal did not open')
        check(js("return document.querySelectorAll('#figure-detail .schema-table tbody tr').length === 5"),
              'Required input schema groups missing')
        check(js("return document.querySelector('#figure-detail').textContent.includes('不需要实验准确率')"),
              'Data contract caveat not visible')
        check(js("return [...document.querySelectorAll('#figure-detail a')].some(a=>a.href.includes('proceedings.iclr.cc') && a.href.includes('page=2'))"),
              'Official Figure 1 link missing from detail')
        check(js("return [...document.querySelectorAll('#figure-detail a')].some(a=>a.href.includes('rote-learning-fig1-inputs.json'))"),
              'Downloadable example JSON missing')
        screen('method-figure-modal-desktop.png')
        js("document.querySelector('#close-dialog').click()")
        check(not js("return document.querySelector('#figure-dialog').open"),'Modal did not close')
        js("const s=document.querySelector('#curated-group');s.value='method';s.dispatchEvent(new Event('change',{bubbles:true}));")
        check(js("return document.querySelectorAll('.reference-card').length===1"),'Method filter did not isolate conceptual figure')
        js("document.querySelector('#language-toggle').click()")
        check(js("return document.documentElement.lang==='en'"),'Bilingual control did not change language')
        wd('POST',f'/session/{session}/window/rect',{'width':390,'height':840})
        time.sleep(.25)
        check(not js("return document.documentElement.scrollWidth>innerWidth+1"),
              'Mobile gallery has horizontal overflow')
        js("document.querySelector('[data-open=iclr26-rote-learning-fig1]').click()")
        time.sleep(.2)
        check(js("return document.querySelector('#figure-dialog').open"),'Mobile Figure 1 modal failed')
        check(not js("return document.documentElement.scrollWidth>innerWidth+1"),'Mobile modal horizontal overflow')
        screen('method-figure-modal-mobile.png')
        wd('GET', '/status')
        with urllib.request.urlopen(base+'/figure-reference-assets/rote-learning-fig1-inputs.json',timeout=8) as r:
            check(json.load(r)['numeric_data_required_for_schematic'] is False,
                  'Public JSON missing source-matched schematic contract')
        print('PASS: ICLR F1 curated figure, source and data contract, local SVG, filters, modal, mobile layout, language')
    finally:
        if session:
            try: wd('DELETE',f'/session/{session}')
            except Exception: pass
        for proc in reversed(processes):
            if proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=4)
                except subprocess.TimeoutExpired: proc.kill()
        log.close()

if __name__ == '__main__':
    main()
