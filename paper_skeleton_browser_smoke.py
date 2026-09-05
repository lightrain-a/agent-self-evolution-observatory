#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys, time
from paper_pages_browser_smoke import ROOT, HTTP_PORT, browser_runtime, request, execute, require
PAGES=['paper-e1.html','paper-b1.html','paper-c1.html','paper-g1.html','paper-e2.html','paper-a.html','paper-b.html','paper-agent-constraint.html','paper-3d.html']
def main():
    cmd,caps=browser_runtime(); server=subprocess.Popen([sys.executable,'-m','http.server',str(HTTP_PORT),'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); driver=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); sid=''
    try:
        for i in range(3):
            time.sleep(1+i)
            try: sid=request('POST','/session',caps)['value']['sessionId']; break
            except Exception: pass
        require(bool(sid),'unable to create browser session'); base=f'http://127.0.0.1:{HTTP_PORT}'
        for page in PAGES:
            request('POST',f'/session/{sid}/url',{'url':f'{base}/{page}'}); time.sleep(.45)
            v=execute(sid,"""const s=document.querySelector('#paper-skeleton');return {count:document.querySelectorAll('#paper-skeleton').length,core:s?.querySelectorAll('.cpp-skeleton-core article').length||0,figures:s?.querySelectorAll('.cpp-skeleton-figures article').length||0,bottom:s?.querySelectorAll('.cpp-skeleton-bottom article').length||0,title:s?.querySelectorAll('h2').length||0,badge:(s?.querySelector('.cpp-skeleton-head>span')?.textContent||'').trim(),data:Object.keys(window.CURRENT_PAPER_SKELETONS||{}).length,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2};""")
            require(v['count']==1 and v['core']==5 and v['figures']==2 and v['bottom']==3 and v['title']==0 and v['data']==9 and not v['overflow'],f'skeleton contract failed {page}: {v}')
        print('PASS paper skeleton browser smoke: 9/9 pages')
    finally:
        if sid:
            try: request('DELETE',f'/session/{sid}')
            except Exception: pass
        driver.terminate(); server.terminate()
if __name__=='__main__': main()