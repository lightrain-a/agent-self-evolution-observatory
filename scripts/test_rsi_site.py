#!/usr/bin/env python3
"""Dependency-free integrity checks for the separately scoped RSI dossier."""
from __future__ import annotations
import json
import re
import subprocess
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['index','timeline','literature','reading-cards','reading-notes','cross-domain','learning-science','ideas','idea-i6','teaching','experiments','references']

class Parsed(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.links=[]; self.h1=0
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if 'id' in d: self.ids.append(d['id'])
        if tag=='h1': self.h1+=1
        for attr in ['href','src']:
            if attr in d: self.links.append(d[attr])

def parse(path):
    p=Parsed(); p.feed(path.read_text(encoding='utf-8')); return p

def check(condition, message):
    if not condition: raise AssertionError(message)

def main():
    source=json.loads((ROOT/'rsi/sources.json').read_text(encoding='utf-8'))
    refs={r['id'] for r in source['sources']}
    card_data=json.loads((ROOT/'rsi/reading-cards.json').read_text(encoding='utf-8'))
    cards=card_data['papers']
    check(card_data['schema_version']==2 and len(cards)>0,'Invalid reading card registry')
    questions=card_data['research_questions']
    question_ids={q['id'] for q in questions}
    check(question_ids=={'signal','novelty','reach','retention','safety'} and len(questions)==5,'Invalid RSI five-question taxonomy')
    check(len({p['id'] for p in cards})==len(cards),'Duplicate reading card ID')
    for card in cards:
        check(card['lead_institution'] in card['institutions'],'Leading author institution not in institution list: '+card['id'])
        check(card['institution_source'] and card['publication'],'Missing institution provenance: '+card['id'])
        check(set(card['research_coverage'])==question_ids,'Paper missing RSI coverage axes: '+card['id'])
        for axis in card['research_coverage'].values():
            check(axis['level'] in {'core','partial','not_addressed'},'Invalid RSI coverage status: '+card['id'])
            check(axis['contribution'] and axis['open_question'],'Missing RSI coverage evidence/gap: '+card['id'])
    check(len(refs)==66 and all(f'S{i}' in refs for i in range(26,40)) and 'E11' in refs,'Expected the audited I1–I6 source manifest')
    check(source['review_date']=='2026-10-27','Review date drift')
    timeline=json.loads((ROOT/'rsi/timeline-data.json').read_text(encoding='utf-8'))
    check(timeline['schema_version']=='1.0','Timeline schema incompatible')
    date.fromisoformat(timeline['verified_at'])
    venues={v['id']:v for v in timeline['venues']}
    check(set(venues)=={'cvpr-2027','icml-2027','acl-2027'},'Expected three 2027 target conferences')
    exact={
        'cvpr-2027':{'cvpr-2027-registration':'2026-11-10',
                     'cvpr-2027-paper':'2026-11-16',
                     'cvpr-2027-supplementary':'2026-11-23'},
        'acl-2027':{'acl-2027-arr':'2027-01-04'},
        'icml-2027':{},
    }
    all_deadlines={}
    for venue_id,venue in venues.items():
        check(venue['source_url'].startswith('https://'),'Conference missing official source')
        for ddl in venue['deadlines']:
            check(ddl['id'] not in all_deadlines,'Duplicate conference deadline id')
            all_deadlines[ddl['id']]=ddl
            if ddl['status']=='official':
                check(ddl['date']==exact[venue_id][ddl['id']],f'Unverified official DDL drift: {ddl["id"]}')
                parsed_due=datetime.fromisoformat(ddl['due_at'])
                check(parsed_due.date()==date.fromisoformat(ddl['date']) and
                      parsed_due.utcoffset()==timedelta(hours=-12) and
                      parsed_due.hour==23 and parsed_due.minute==59,
                      f'Official AoE instant is wrong: {ddl["id"]}')
            else:
                check(ddl['status']=='pending' and ddl['date'] is None and ddl['due_at'] is None,
                      f'Unpublished deadline given a guessed date: {ddl["id"]}')
    check(len(all_deadlines)==7 and len(exact['cvpr-2027'])+len(exact['acl-2027'])==4,
          'Timeline DDL snapshot mismatch')
    timeline_html=(ROOT/'rsi/timeline.html').read_text(encoding='utf-8')
    for identifier in all_deadlines:
        check(f'id="{identifier}"' in timeline_html,
              'Deadline missing from timeline page: '+identifier)
    for card in cards:
        check(f'id="reading-{card["id"]}"' in timeline_html,
              'New reading card not automatically included in timeline: '+card['id'])
    check('timeline.css' in timeline_html and 'timeline-view.js' in timeline_html,
          'Timeline runtime assets missing')
    for id in ['rsi-tl-kind','rsi-tl-time','rsi-tl-query','rsi-tl-count']:
        check(f'id="{id}"' in timeline_html,f'Timeline filter missing: {id}')
    # Primary groups and second-level pages share one ordered schema, and every
    # page must have exactly one active parent in the no-JavaScript fallback.
    nav_text=(ROOT/'rsi/site-nav.js').read_text(encoding='utf-8')
    check(nav_text.startswith('window.NAV_GROUPS = '),'Invalid standalone RSI navigation module')
    groups=json.loads(nav_text[len('window.NAV_GROUPS = '):].strip().removesuffix(';'))
    expected_groups={
        'overview':['index','timeline'],
        'literature':['literature','reading-cards','reading-notes','references'],
        'methods':['cross-domain','learning-science'],
        'research':['ideas','idea-i6','teaching','experiments'],
    }
    check([g['id'] for g in groups]==list(expected_groups),'Incorrect first-level RSI menu order')
    grouped_slugs=[]
    for group in groups:
        slugs=[href.removesuffix('.html') for href,_ in group['pages']]
        check(slugs==expected_groups[group['id']],f'Incorrect child menu: {group["id"]}')
        check(group['title']['zh'] and group['title']['en'],f'Missing bilingual parent title: {group["id"]}')
        grouped_slugs.extend(slugs)
    check(len(grouped_slugs)==len(set(grouped_slugs)) and set(grouped_slugs)==set(PAGES),
          'RSI page missing or duplicated across primary menus')
    page_parent={slug:g['id'] for g in groups for slug in expected_groups[g['id']]}
    parsed={}
    site_asset_sources={'site-base.css':ROOT/'style.css', 'site-switch.css':ROOT/'site-switch.css', 'favicon.svg':ROOT/'favicon.svg'}
    for slug in PAGES:
        path=ROOT/'rsi'/f'{slug}.html'; p=parse(path); parsed[path]=p
        check(p.h1==1,f'{slug}: expected one h1')
        check(len(set(p.ids))==len(p.ids),f'{slug}: duplicate IDs')
        text=path.read_text(encoding='utf-8')
        check('[[' not in text,f'{slug}: unexpanded source token')
        check('提案尚待实验' in text,f'{slug}: missing hypothesis status')
        check('lang="zh-CN"' in text,f'{slug}: wrong content language')
        check('class="site-switcher"' in text and 'href="/rsi/"' in text and 'href="/"' in text,f'{slug}: missing two-site switch')
        check('src="site-nav.js"' in text and 'src="../data.js"' not in text,f'{slug}: navigation depends on Agent')
        fallback_groups=re.findall(r'<details class="nav-group([^"]*)" data-nav-group="([^"]+)"([^>]*)>',text)
        check(len(fallback_groups)==len(groups),f'{slug}: fallback navigation lacks primary levels')
        check([name for _,name,_ in fallback_groups]==list(expected_groups),f'{slug}: fallback group order differs')
        active_parents=[name for classes,name,_ in fallback_groups if 'active-group' in classes]
        open_parents=[name for _,name,attrs in fallback_groups if ' open' in attrs]
        check(active_parents==[page_parent[slug]] and open_parents==[page_parent[slug]],
              f'{slug}: current page parent must be active and expanded')
        check(text.count('class="nav-level2 active"')==1,f'{slug}: only one current submenu link is expected')
    for path,p in parsed.items():
        for href in p.links:
            u=urlsplit(href)
            if u.scheme or u.netloc: continue
            if u.path.startswith('/'):
                check(u.path in ('/', '/rsi/'),f'Unexpected absolute path in RSI: {href}')
                continue
            target=(path.parent/unquote(u.path)).resolve() if u.path else path
            check(target.is_relative_to(ROOT),f'Escaping link: {href}')
            if target.name in site_asset_sources and target.parent==ROOT/'rsi':
                check(site_asset_sources[target.name].is_file(),f'Missing shared source for {href}')
                continue
            check(target.is_file(),f'Missing file: {path.name} -> {href}')
            if u.fragment and target.suffix=='.html':
                target_parsed=parsed.get(target) or parse(target)
                check(unquote(u.fragment) in target_parsed.ids,f'Missing anchor: {path.name} -> {href}')
    card_ids=set(parsed[ROOT/'rsi/reading-cards.html'].ids)
    check(all(p['id'] in card_ids for p in cards),'Paper not rendered from JSON')
    card_html=(ROOT/'rsi/reading-cards.html').read_text(encoding='utf-8')
    check(card_html.count('class="reading-card"')==len(cards),'Wrong number of rendered paper cards')
    check('id="reading-question-filter"' in card_html and 'id="reading-coverage-filter"' in card_html,'Missing five-question filters')
    for card in cards:
        check(card['lead_institution'] in card_html,'Missing author institution in HTML: '+card['id'])
        coverage='|'.join(f'{q["id"]}:{card["research_coverage"][q["id"]]["level"]}' for q in questions)
        check(coverage in card_html,'Missing exact five-question coverage status: '+card['id'])
    deep_notes=[p for p in cards if p.get('deep_read')]
    notes_html=(ROOT/'rsi/reading-notes.html').read_text(encoding='utf-8')
    for paper in deep_notes:
        pid=paper['id']
        check(f'href="reading-notes.html#deep-{pid}"' in card_html,
              'Deep-read link missing from compact card: '+pid)
        check(f'id="deep-{pid}"' in notes_html,
              'Deep-read article missing: '+pid)
        section_ids=[s['id'] for s in paper['deep_read']['sections']]
        check(len(section_ids)==len(set(section_ids)) and section_ids,
              'Deep-read sections missing or duplicated: '+pid)
        for section in section_ids:
            check(f'id="deep-{pid}--{section}"' in notes_html,
                  'Deep-read section missing: '+pid+'/'+section)
    check('教学示例' in notes_html and '非论文' in notes_html,
          'Deep-read evidence provenance caveat missing')
    check(all(p['links']['html'].startswith('https://arxiv.org/') for p in cards),'Paper lacks a verified original link')
    ideas=parsed[ROOT/'rsi/ideas.html']
    check(all(f'idea-{i}' in ideas.ids for i in range(1,6)),'I1–I5 anchors missing from research board')
    ideas_text=(ROOT/'rsi/ideas.html').read_text(encoding='utf-8')
    for name in ['R²Orch','PATS','RSIFlow','HCL','SkillBoost','Trace2Skill','PopuLoRA','OPCoD','MACE']:
        check(name in ideas_text,f'Missing nearest-work comparison: {name}')
    check('交流结束后' in ideas_text and '不需要外部教师告诉标准答案' in ideas_text,'I5/I4 hypothesis drift')
    i6_text=(ROOT/'rsi/idea-i6.html').read_text(encoding='utf-8')
    check('href="idea-i6.html"' in ideas_text,'I6 missing from I1–I6 idea board')
    check(all(k in i6_text for k in ('知识不足','搜索不足','选择不足','吸收不足','I2 · 因材施教','From Rollouts to Recipes')),'I6 four probes, orthogonality, or closest-work missing')
    check(all(f'id="{x}"' in i6_text for x in ('question','challenge','insight','design','orthogonality','related','experiments','safety')),'I6 required sections missing')
    ref_ids=set(parsed[ROOT/'rsi/references.html'].ids)
    check(refs<=ref_ids,'Some source cards have no anchors')
    agent_nav=(ROOT/'data.js').read_text(encoding='utf-8')
    check('"rsi/index.html"' not in agent_nav,'Agent navigation still includes RSI pages')
    nav=nav_text
    for slug in PAGES:
        check(f'"{slug}.html"' in nav,f'Missing RSI-only navigation: {slug}')
    records=json.loads((ROOT/'rsi/search-index.json').read_text(encoding='utf-8'))
    for card in cards:
        indexed=[r for r in records if r['url']==f"reading-cards.html#{card['id']}"]
        check(len(indexed)==1,'Paper missing or duplicated in global search')
        check(card['lead_institution'] in indexed[0]['text'],'Author institution missing from search: '+card['id'])
        check(all(q['label'] in indexed[0]['text'] for q in questions),'Five-question labels missing from search: '+card['id'])
    for r in records:
        u=urlsplit(r['url']); p=ROOT/'rsi'/u.path
        check(p in parsed and u.fragment in parsed[p].ids,'Search result target missing: '+r['url'])
    subprocess.run(['node','--check',str(ROOT/'rsi/research.js')],check=True)
    subprocess.run(['node','--check',str(ROOT/'rsi/timeline-view.js')],check=True)
    public=ROOT/'_site'
    if public.exists():
        for slug in PAGES:
            check((public/'rsi'/f'{slug}.html').is_file(),f'Not exported: {slug}')
        for filename in ['timeline-data.json','timeline-view.js','timeline.css']:
            check((public/'rsi'/filename).is_file(),f'RSI timeline asset not exported: {filename}')
            check((public/'rsi'/filename).read_bytes()==(ROOT/'rsi'/filename).read_bytes(),
                  f'RSI timeline export differs from source: {filename}')
        for name,src in site_asset_sources.items():
            check((public/'rsi'/name).is_file(),f'RSI standalone asset missing: {name}')
            check((public/'rsi'/name).read_bytes()==src.read_bytes(),f'RSI standalone asset drift: {name}')
        check((public/'rsi/site-nav.js').read_bytes()==(ROOT/'rsi/site-nav.js').read_bytes(),'RSI nav export drift')
        check(not list(public.rglob('*.py')),'Python leaked into public output')
        check((public/'rsi/sources.json').read_bytes()==(ROOT/'rsi/sources.json').read_bytes(),'Exported source manifest differs')
    print(f'PASS: {len(PAGES)} RSI pages, {len(refs)} sources, {len(records)} search records, local links/anchors, nav and public export.')

if __name__=='__main__': main()
