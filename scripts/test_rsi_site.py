#!/usr/bin/env python3
"""Dependency-free integrity checks for the separately scoped RSI dossier."""
from __future__ import annotations
import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['index','literature','reading-cards','cross-domain','learning-science','ideas','teaching','experiments','references']

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
    check(len(refs)==51,'Expected the audited 51-record source snapshot')
    check(source['review_date']=='2026-10-21','Review date drift')
    parsed={}
    for slug in PAGES:
        path=ROOT/'rsi'/f'{slug}.html'; p=parse(path); parsed[path]=p
        check(p.h1==1,f'{slug}: expected one h1')
        check(len(set(p.ids))==len(p.ids),f'{slug}: duplicate IDs')
        text=path.read_text(encoding='utf-8')
        check('[[' not in text,f'{slug}: unexpanded source token')
        check('提案尚待实验' in text,f'{slug}: missing hypothesis status')
        check('lang="zh-CN"' in text,f'{slug}: wrong content language')
    for path,p in parsed.items():
        for href in p.links:
            u=urlsplit(href)
            if u.scheme or u.netloc: continue
            target=(path.parent/unquote(u.path)).resolve() if u.path else path
            check(target.is_relative_to(ROOT),f'Escaping link: {href}')
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
    check(all(p['links']['html'].startswith('https://arxiv.org/') for p in cards),'Paper lacks a verified original link')
    ref_ids=set(parsed[ROOT/'rsi/references.html'].ids)
    check(refs<=ref_ids,'Some source cards have no anchors')
    nav=(ROOT/'data.js').read_text(encoding='utf-8')
    for slug in PAGES:
        check(f'"rsi/{slug}.html"' in nav,f'Missing root navigation: {slug}')
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
    public=ROOT/'_site'
    if public.exists():
        for slug in PAGES:
            check((public/'rsi'/f'{slug}.html').is_file(),f'Not exported: {slug}')
        check(not list(public.rglob('*.py')),'Python leaked into public output')
        check((public/'rsi/sources.json').read_bytes()==(ROOT/'rsi/sources.json').read_bytes(),'Exported source manifest differs')
    print(f'PASS: {len(PAGES)} RSI pages, {len(refs)} sources, {len(records)} search records, local links/anchors, nav and public export.')

if __name__=='__main__': main()
