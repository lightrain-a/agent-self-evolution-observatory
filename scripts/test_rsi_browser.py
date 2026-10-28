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
PAGES=['index','timeline','literature','reading-cards','reading-notes','cross-domain','learning-science','ideas','idea-i2','idea-i5','idea-i6-failure-value','idea-i7-learning-order','i8','idea-i9-practice-switching','teaching','idea-i6','experiments','references']

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
        nav_data=json.loads((ROOT/'rsi/site-nav.js').read_text(encoding='utf-8').split(' = ',1)[1].strip().removesuffix(';'))
        expected_nav_links=sum(len(group['pages']) for group in nav_data)
        summaries=[]
        for slug in PAGES:
            nav('rsi/'+slug+'.html')
            stats=js("""const groups=[...document.querySelectorAll('#research-nav details.nav-group')];return {title:document.title,h1:document.querySelectorAll('h1').length,active:document.querySelectorAll('#research-nav a[aria-current="page"]').length,nav:document.querySelectorAll('#research-nav .nav-level2').length,groups:groups.length,expanded:groups.filter(g=>g.open).length,activeParents:groups.filter(g=>g.classList.contains('active-group')&&g.open).length,overflow:document.documentElement.scrollWidth>innerWidth+1,cites:document.querySelectorAll('.cite').length,sections:document.querySelectorAll('.research-section').length};""")
            check(stats['h1']==1 and stats['active']==1 and stats['nav']==expected_nav_links and stats['groups']==4 and stats['expanded']==1 and stats['activeParents']==1,slug+': two-level navigation or title integrity '+str(stats))
            check(not stats['overflow'],slug+': desktop page overflow')
            summaries.append({'page':slug,**stats})
        nav('rsi/index.html')
        rsi_switch=js("return [...document.querySelectorAll('.site-switcher__tab')].map(a=>({href:a.getAttribute('href'),active:a.getAttribute('aria-current')==='true'}));")
        check(rsi_switch==[{'href':'/','active':False},{'href':'/rsi/','active':True}],f'RSI switch destinations incorrect: {rsi_switch}')
        check(js("return [...document.querySelectorAll('#research-nav .nav-level2')].every(a=>!a.getAttribute('href').startsWith('../'))"),'RSI navigation not standalone')
        nav('rsi/literature.html')
        check(js("return document.querySelectorAll('#rsi-landscape-20261003 table tbody tr').length===5"),
              'Curated overview must present four research questions and safety')
        check(js("return document.querySelectorAll('#rsi-landscape-20261003 .cite').length>=11"),
              'Curated overview needs primary research citations')
        js("document.querySelector('#rsi-landscape-20261003').scrollIntoView({block:'start'})")
        time.sleep(.6)
        screenshot('rsi-panorama-evidence-desktop.png')
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
        expected_first=sorted(cards,key=lambda p:(bool(p.get('deep_read')),p['read_on']),reverse=True)[0]['id']
        check(js("return document.querySelector('.reading-card').id")==expected_first,
              'Reading cards must show latest deep-read papers first')
        check(js("return document.querySelector('#optimal-practice-2020-eglington .reading-metadata').textContent.includes('npj Science of Learning')"),
              'Journal card should display its real venue, not a made-up arXiv ID')
        check(js("return document.querySelector('#acl2026-good-curriculum-jia .reading-metadata').textContent.includes('ACL 2026')"),
              'ACL conference paper should show its actual venue')
        check(js("return document.querySelector('#acl2026-sft-ilp-xue .reading-metadata').textContent.includes('ACL 2026')"),
              'Incomplete Learning paper must have correct ACL 2026 venue')
        check(js("return document.querySelectorAll('#acl2026-sft-ilp-xue .reading-story-step').length===4"),
              'Incomplete Learning paper must have four readable summary stages')
        check(js("return document.querySelector('#acl2026-good-curriculum-jia .reading-story-step').textContent.includes('难在哪里')"),
              'ACL conference reading card missing four-stage readable summary')
        screenshot('reading-cards-desktop.png')
        js("document.querySelector('#acl2026-sft-ilp-xue').scrollIntoView({block:'start'})")
        time.sleep(.6)
        screenshot('reading-ilp-card-desktop.png')
        check(js("return document.querySelector('#acl2026-sft-ilp-xue .reading-related-link')!==null"),
              'ILP card needs direct nearest Related Work jump')
        check(js("return document.querySelector('#rote-learning-iclr2026-wu .reading-metadata').textContent.includes('ICLR 2026')"),
              'Published Rote Learning card must name ICLR rather than looking like an unpublished preprint')
        check(js("return document.querySelector('#rote-learning-iclr2026-wu .reading-story-step[data-story-stage=result]').textContent.includes('36%')"),
              'Rote Learning overview must not hide the two-hop negative result')
        js("document.querySelector('#rote-learning-iclr2026-wu').scrollIntoView({block:'start'})")
        time.sleep(.7)
        screenshot('reading-rote-learning-card-desktop.png')
        js("document.querySelector('#acl2026-good-curriculum-jia').scrollIntoView({block:'start'})")
        time.sleep(.6)
        screenshot('reading-acl2026-card-desktop.png')
        check(js("return document.querySelector('#acl2026-good-curriculum-jia .reading-related-link')!==null"),
              'ACL curriculum card missing its Related Work jump')
        js("document.querySelector('#optimal-practice-2020-eglington').scrollIntoView({block:'start'})")
        time.sleep(.7)
        screenshot('reading-npj-card-desktop.png')
        check(js("return document.querySelector('#optimal-practice-2020-eglington .reading-related-link')!==null"),
              'npj practice scheduling paper lacks related-work comparison')
        check(js("return document.querySelector('#rsi-anything-2610-13912 .reading-related-link')!==null"),
              'RSI-Anything card missing Related Work shortcut')
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
        check(js("return document.querySelectorAll('#deep-hypothesis-testing-2026-ding--figure-four-learner-trajectories .deep-table tbody tr').length===4"),
              'Four grouped Figure 4 learner-profile rows missing')
        js("document.querySelector('#deep-hypothesis-testing-2026-ding--figure-four-learner-trajectories summary').click()")
        check(js("return document.querySelector('#deep-hypothesis-testing-2026-ding--figure-four-learner-trajectories').open"),
              'Figure 4 details cannot expand')
        js("document.querySelector('#deep-hypothesis-testing-2026-ding--figure-four-learner-trajectories').scrollIntoView({block:'start'})")
        time.sleep(.6)
        screenshot('motor-figure4-seven-trajectories-desktop.png')
        js("document.querySelector('#deep-hypothesis-testing-2026-ding--figure-four-learner-trajectories summary').click()")
        check(js("return document.querySelectorAll('.deep-chapter[open]').length===0"),
              'Figure 4 details do not collapse cleanly')
        check(js("return document.querySelectorAll('.deep-evidence').length>=4"),
              'Evidence matrix did not render')
        check(js("return document.querySelectorAll('#deep-acl2026-good-curriculum-jia .deep-metric-item').length===5"),
              'ACL curriculum five metrics should be visible without expanding chapters')
        check(js("return document.querySelectorAll('#deep-acl2026-sft-ilp-xue .deep-metric-item').length===5"),
              'ILP five causes with results should be visible without expanding chapters')
        check(js("return document.querySelector('#deep-acl2026-sft-ilp-xue .deep-metric-overview').textContent.includes('82.1%')"),
              'ILP five-cause summary missing the decisive knowledge-gap result')
        check(js("return document.querySelector('#deep-acl2026-sft-ilp-xue .deep-metric-overview').textContent.includes('0.53')"),
              'ILP five-cause summary missing left-side forgetting effect')
        check(js("return [...document.querySelectorAll('#deep-acl2026-good-curriculum-jia .deep-metric-result')].every((e,i)=>e.textContent.includes('Table '+(i+1)))"),
              'Each visible metric must include the matching table and result')
        related_papers={t['paper_id'] for t in json.loads((ROOT/'rsi/related-work.json').read_text(encoding='utf-8'))['targets']}
        for paper in deep_cards:
            selector=json.dumps('#deep-'+paper['id'])
            actual_stages=js("return [...document.querySelector("+selector+").querySelectorAll('.deep-stage')].map(s=>s.dataset.storyStage).join(',')")
            has_related = (paper['id'] in related_papers or any(s['stage']=='related' for s in paper['deep_read']['sections']))
            expected_stages='challenge,insight,design,result'+(',related' if has_related else '')+',next'
            check(actual_stages==expected_stages,
                  'Paper long read must follow C-I-D-R, optional Related Work, then future questions: '+paper['id'])
        check(js("return document.querySelector('#deep-rote-learning-iclr2026-wu--stage-result').textContent.includes('36%') && document.querySelector('#deep-rote-learning-iclr2026-wu--stage-result').textContent.includes('16%')"),
              'Two-hop reasoning limits absent from the new full reading note')
        check(js("return document.querySelector('#deep-rote-learning-iclr2026-wu--stage-next').textContent.includes('RSI')"),
              'Rote Learning must identify what would need actual RSI experiments')
        check(js("return document.querySelectorAll('#deep-rsi-anything-2610-13912--stage-related > .deep-stage-details > .deep-related > .deep-related-matrix tbody tr').length===7"),
              'RSI-Anything closest-work table should include seven papers')
        check(js("return document.querySelectorAll('#deep-optimal-practice-2020-eglington--stage-related .deep-related-matrix tbody tr').length===4"),
              'npj 2020 must compare four real closest works')
        check(js("return document.querySelector('#deep-optimal-practice-2020-eglington').textContent.includes('p=0.2')"),
              'Original paper versus speculative hard-task wait distinction not present')
        check(js("return document.querySelectorAll('#deep-rsi-anything-2610-13912--stage-related .deep-related-paper').length===9"),
              'Nine source-grounded Related Work comparisons expected')
        check(js("""return document.querySelector('#related-rsi-anything-2610-13912--rlanything a[href^="https"]').getAttribute('href')==='https://proceedings.mlr.press/v306/wang26jf.html'"""),
              'RLAnything source must point to official ICML proceedings')
        check(js("return document.querySelectorAll('.deep-chapter[open]').length===0"),
              'Detailed formulas or cases should start collapsed')
        check(js("return document.querySelector('#deep-hypothesis-testing-2026-ding .deep-terms').children.length===3"),
              'Original motor-learning three-term glossary changed')
        check(js("return document.querySelector('#deep-hgm-2510-21614 .deep-terms').children.length>=5 && document.querySelector('#deep-hgm-2510-21614--stage-insight')!==null"),
              'HGM glossary or full C-I-D-R reading is not rendered')
        screenshot('reading-notes-desktop.png')
        js("document.querySelector('#deep-acl2026-sft-ilp-xue .deep-metric-overview').scrollIntoView({block:'start'})")
        time.sleep(.6)
        screenshot('reading-ilp-five-causes-desktop.png')
        js("document.querySelector('#deep-acl2026-good-curriculum-jia .deep-metric-overview').scrollIntoView({block:'start'})")
        time.sleep(.6)
        screenshot('reading-acl2026-metrics-desktop.png')
        js("document.querySelector('#deep-acl2026-good-curriculum-jia--decision-variability summary').click()")
        check(js("return document.querySelector('#deep-acl2026-good-curriculum-jia--decision-variability').open"),
              'VACC formula and 12/15 caution did not expand')
        js("document.querySelector('#deep-rsi-anything-2610-13912--stage-challenge').scrollIntoView({block:'start'})")
        time.sleep(.8)
        screenshot('reading-notes-story-desktop.png')
        js("document.querySelector('#deep-optimal-practice-2020-eglington--stage-challenge').scrollIntoView({block:'start'})")
        time.sleep(.7)
        screenshot('reading-npj-story-desktop.png')
        js("document.querySelector('#deep-rsi-anything-2610-13912--stage-related').scrollIntoView({block:'start'})")
        time.sleep(.8)
        screenshot('reading-related-work-desktop.png')
        js("document.querySelector('#related-rsi-anything-2610-13912--cure summary').click()")
        check(js("return document.querySelector('#related-rsi-anything-2610-13912--cure').open"),
              'CURE difference and evidence did not expand')
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
        ordered_links=js("return [...document.querySelectorAll('#research-nav [data-nav-group=research] .nav-level2')].map(a=>({label:a.textContent.trim(),href:a.getAttribute('href')}));")
        numbers=[item['label'].split(' ·')[0] for item in ordered_links if item['label'].startswith('I')]
        check(numbers==[f'I{i}' for i in range(1,10)],f'Numbered ideas duplicated or not sorted: {ordered_links}')
        check(not any(item['href'] in ('teaching.html','idea-i6.html') for item in ordered_links),'Historical pages should not compete in the sidebar')
        js("document.querySelector('#research-nav a[href=\"ideas.html#idea-3\"]').click()")
        time.sleep(.3)
        check(js("return location.hash==='#idea-3' && document.querySelector('#research-nav a[aria-current=page]').getAttribute('href')==='ideas.html#idea-3'"),
              'Current idea anchor not highlighted after same-page navigation')
        nav('rsi/ideas.html#idea-2')
        check(js("return document.querySelector('#research-nav a[aria-current=page]').getAttribute('href')==='idea-i2.html'"),
              'Legacy I2 anchor must highlight the dedicated I2 entry')
        js("document.querySelector('#research-nav a[href=\"idea-i2.html\"]').click()")
        time.sleep(.4)
        check(js("return document.body.dataset.rsiPage==='idea-i2' && document.querySelectorAll('#research-nav a[aria-current=page]').length===1"),
              'I2 detailed page navigation failed')
        screenshot('i2-coevolution-desktop.png')
        nav('rsi/teaching.html')
        check(js("return document.querySelector('#research-nav a[aria-current=page]').getAttribute('href')==='idea-i5.html'"),
              'Teaching feedback archive should highlight the sole I5 navigation item')
        nav('rsi/idea-i6.html')
        check(js("return document.querySelector('#research-nav a[aria-current=page]').getAttribute('href')==='ideas.html'"),
              'Historic I6 archive must not compete with current numbered I6')
        nav('rsi/ideas.html')
        for idea_number in range(1, 10):
            steps=js(f"return [...document.querySelector('#idea-{idea_number}').querySelectorAll('.idea-step')].map(e=>({{heading:e.querySelector('h3').textContent.trim(),height:e.getBoundingClientRect().height}}));")
            check(len(steps)==5 and all(s['height']>35 for s in steps),f'I{idea_number} five-stage layout collapsed: {steps}')
            check([s['heading'].split(' ')[0] for s in steps]==['Challenge','现有工作','Insight','Design','实验设计'],f'I{idea_number} argument order wrong')
            check(js(f"return document.querySelectorAll('#idea-{idea_number} .flow>div').length>=4"),
                  f'I{idea_number} missing four-step design diagram')
        for i,detail in ((6,'idea-i6-failure-value.html'),(7,'idea-i7-learning-order.html'),(8,'i8.html'),(9,'idea-i9-practice-switching.html')):
            check(js(f"return document.querySelector('#idea-{i} .idea-side-note a[href=\"{detail}\"]')!==null"),
                  f'I{i} full research page link missing')
        js("document.querySelector('#idea-1').scrollIntoView({block:'start'})")
        time.sleep(.5)
        screenshot('idea-framework-desktop.png')
        js("document.querySelector('#idea-6').scrollIntoView({block:'start'})")
        time.sleep(.5)
        screenshot('idea-i6-five-stage-desktop.png')
        js("document.querySelector('#idea-8').scrollIntoView({block:'start'})")
        time.sleep(.5)
        screenshot('idea-i8-five-stage-desktop.png')
        js("document.querySelector('#idea-9').scrollIntoView({block:'start'})")
        time.sleep(.5)
        screenshot('idea-i9-five-stage-desktop.png')
        req('POST',f'/session/{session}/window/rect',{'width':390,'height':844})
        for slug in ['index','timeline','reading-cards','reading-notes','ideas','idea-i2','idea-i5','idea-i6-failure-value','idea-i7-learning-order','i8','idea-i9-practice-switching','idea-i6','teaching','experiments','references']:
            nav('rsi/'+slug+'.html')
            check(not js('return document.documentElement.scrollWidth>innerWidth+1'),slug+': mobile horizontal overflow')
        nav('rsi/ideas.html'); js("document.querySelector('#idea-1').scrollIntoView({block:'start'})")
        time.sleep(.5)
        screenshot('idea-framework-mobile.png')
        js("document.querySelector('#idea-7').scrollIntoView({block:'start'})")
        time.sleep(.5)
        check(not js('return document.documentElement.scrollWidth>innerWidth+1'),
              'I7 on mobile must not create horizontal page overflow')
        screenshot('idea-i7-five-stage-mobile.png')
        nav('rsi/idea-i9-practice-switching.html')
        check(js("return ['future-question','future-geometry','future-related','future-p0','future-gate'].every(id=>document.getElementById(id)!==null)"),
              'I9 browser does not render A/B-to-C scientific extension')
        check(js("return document.querySelector('#future-geometry').textContent.includes('Lie bracket') && document.querySelector('#future-p0').textContent.includes('AdamW')"),
              'Future learnability geometry or matched optimizer control not visible')
        check(not js('return document.documentElement.scrollWidth>innerWidth+1'), 'I9 detail must fit mobile width')
        screenshot('idea-i9-detail-mobile.png')
        nav('rsi/ideas.html')
        js("document.querySelector('#menu-toggle').click()")
        time.sleep(.45)
        check(js("return (()=>{const r=document.querySelector('#sidebar').getBoundingClientRect();return r.right>10 && r.left<innerWidth-10})()"),
              'Mobile research drawer not visible after transition')
        screenshot('ideas-numbered-navigation-mobile.png')
        js("document.querySelector('#research-nav a[href=\"ideas.html#idea-3\"]').click()")
        time.sleep(.2)
        check(js("return location.hash==='#idea-3' && !document.querySelector('#sidebar').classList.contains('open')"),
              'Mobile numbered anchor did not navigate or close the drawer')
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
        result={'status':'PASS','pages':summaries,'search':'PASS','language':'PASS','mobile':'PASS','cross_site_switch':'PASS','independent_navigation':'PASS','screenshots':23}
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
