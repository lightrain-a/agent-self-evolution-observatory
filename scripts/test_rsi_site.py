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
PAGES = ['index','timeline','literature','reading-cards','reading-notes','cross-domain','theory-notes','learning-science','curriculum-scale-evidence','ideas','idea-prioritization','idea-i2','idea-i5','idea-i6-failure-value','idea-i7-learning-order','i8','idea-i9-practice-switching','idea-i10-learning-novelty','idea-i11-emotional-rsi','idea-i12-prerequisite-bottleneck','learning-admission','experience-consolidation','teaching','idea-i6','experiments','references']


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
    check(card_data['schema_version']==3 and len(cards)>0,'Invalid reading card registry')
    questions=card_data['research_questions']
    question_ids={q['id'] for q in questions}
    check(question_ids=={'signal','novelty','reach','retention','safety'} and len(questions)==5,'Invalid RSI five-question taxonomy')
    check(len({p['id'] for p in cards})==len(cards),'Duplicate reading card ID')
    theory_data=json.loads((ROOT/'rsi/theory-notes.json').read_text(encoding='utf-8'))
    check(theory_data['schema_version']==1 and len(theory_data['entries'])>=7,'Missing reusable theory registry')
    theory_entries=theory_data['entries']
    theory_ids={entry['id'] for entry in theory_entries}
    check(len(theory_ids)==len(theory_entries),'Duplicate theory anchor ID')
    check({'learning-target-generation','semi-gradient-expressivity','meta-gradient-chain',
           'dual-timescales','prediction-bootstrapping','meta-stabilization',
           'rsi-future-learnability-objective'}<=theory_ids,'Missing DiscoRL theory derivation')
    theory_page=(ROOT/'rsi/theory-notes.html').read_text(encoding='utf-8')
    deep_page=(ROOT/'rsi/reading-notes.html').read_text(encoding='utf-8')
    for entry in theory_entries:
        paper=next((p for p in cards if p['id']==entry['source_paper_id']),None)
        check(paper is not None and paper.get('deep_read'), 'Theory without a deep-read source: '+entry['id'])
        check(entry['source_anchor'] in {s['id'] for s in paper['deep_read']['sections']},
              'Broken theory-to-paper chapter: '+entry['id'])
        check('id="'+entry['id']+'"' in theory_page,'Theory stable anchor missing: '+entry['id'])
        check('reading-notes.html#deep-'+paper['id']+'--'+entry['source_anchor'] in theory_page,
              'Theory chapter backlink missing: '+entry['id'])
        check('theory-notes.html#'+entry['id'] in deep_page,
              'Original paper deep-read missing theory shortcut: '+entry['id'])
        check(all(e.get('latex') and e.get('expression') for e in entry['equations']),
              'Theory lacks checked formulas/LaTeX: '+entry['id'])
        check(entry['status'] in theory_data['status_legend'],
              'Theory evidence tier missing: '+entry['id'])
    check({'paper-mechanism','teaching-derivation','rsi-hypothesis'}<=
          {t['status'] for t in theory_entries},'Theory source vs derivation vs hypothesis not distinguished')
    check({'awake-ripple-memory-tagging','experience-tag-vs-consolidation-utility'}<=theory_ids,
          'Science 2024 memory tagging theory missing')
    mouse_paper=next((p for p in cards if p['id']=='sharp-wave-ripples-science2024-yang'),None)
    check(mouse_paper is not None and mouse_paper.get('doi')=='10.1126/science.adk8261'
          and len(mouse_paper.get('deep_read',{}).get('sections',[]))>=10,
          'Science 2024 mouse SPW-R deep read missing')
    check('deep-sharp-wave-ripples-science2024-yang--core-results' in deep_page
          and 'theory-notes.html#awake-ripple-memory-tagging' in deep_page,
          'Science 2024 reading-to-theory jump missing')
    i6_text=(ROOT/'rsi/idea-i6-failure-value.html').read_text(encoding='utf-8')
    check('id="science2024-memory-tagging"' in i6_text
          and 'theory-notes.html#experience-tag-vs-consolidation-utility' in i6_text,
          'I6 science memory-tagging and future-utility theory entry missing')
    check({'nonlocal-credit-assignment','need-gain-prioritized-replay',
           'single-edit-gradient-transfer','nonlocal-net-transfer-i8'}<=theory_ids,
          'Missing reusable Science/LLM nonlocal-learning theory')
    science=next((p for p in cards if p['id']=='nonlocal-replay-science2021-liu'),None)
    check(science is not None and science.get('doi')=='10.1126/science.abf1357'
          and len(science.get('deep_read',{}).get('sections',[]))>=12,
          'Science 2021 nonlocal-learning deep read missing')
    science_related=json.loads((ROOT/'rsi/related-work.json').read_text(encoding='utf-8'))
    nonlocal_related=next((t for t in science_related['targets']
                          if t['paper_id']=='nonlocal-replay-science2021-liu'),None)
    check(nonlocal_related is not None and len(nonlocal_related['works'])>=8
          and {'gradsim','leap','one-shot-rlvr'}<=
          {w['id'] for w in nonlocal_related['works']},
          'Missing audited LLM comparison against Science 2021')
    i8_text=(ROOT/'rsi/i8.html').read_text(encoding='utf-8')
    check('id="science2021-nonlocal"' in i8_text and 'id="nonlocal-p0"' in i8_text
          and 'reading-notes.html#deep-nonlocal-replay-science2021-liu' in i8_text
          and 'theory-notes.html#need-gain-prioritized-replay' in i8_text,
          'I8 nonlocal learning reading/protocol/theory links missing')
    memory_cards={p['id']:p for p in cards if p['id'] in
                  ('memory-management-acl2026-xiong','faulty-memory-arxiv2026-zhang')}
    check(set(memory_cards)=={'memory-management-acl2026-xiong','faulty-memory-arxiv2026-zhang'},
          'Missing two LLM memory deep reads')
    acl=memory_cards['memory-management-acl2026-xiong']
    faulty=memory_cards['faulty-memory-arxiv2026-zhang']
    check(acl['doi']=='10.18653/v1/2026.acl-long.27' and
          len(acl['deep_read']['sections'])>=11 and
          '38.67/42.06' in ' '.join(acl['evidence']),
          'ACL 2026 result / provenance contract drift')
    check(faulty['arxiv']=='2605.12978' and 'v2' in faulty['version'] and
          faulty['links']['html']=='https://arxiv.org/html/2605.12978v2' and
          len(faulty['deep_read']['sections'])>=14 and
          '100%→54%' in ' '.join(faulty['evidence']) and
          '54%' in ' '.join(faulty['boundaries']),
          'Faulty Memory v2 result or abstract/body contradiction missing')
    check({'memory-retrieval-causal-utility','memory-consolidation-fidelity'}<=theory_ids,
          'Experience/memory causal-utility and fidelity theories missing')
    for paper_id,anchor in (('memory-management-acl2026-xiong','table-two'),
                             ('faulty-memory-arxiv2026-zhang','table-five-causal')):
        check('deep-'+paper_id+'--'+anchor in deep_page,
              'Missing primary-paper experiment anchor: '+paper_id)
    candidate=(ROOT/'rsi/experience-consolidation.html').read_text(encoding='utf-8')
    check(all('id="'+x+'"' in candidate for x in
              ('question','evidence','mechanism','formal','p0','p1','p2','closest','research-boundary','decision')),
          'Experience-to-competence candidate missing causal experiment sections')
    check(all(anchor in candidate for anchor in (
              'deep-memory-management-acl2026-xiong',
              'deep-faulty-memory-arxiv2026-zhang',
              'deep-sharp-wave-ripples-science2024-yang',
              'memory-retrieval-causal-utility',
              'memory-consolidation-fidelity')),
          'Experience-to-competence candidate missing source and theory backlinks')
    check('experience-consolidation.html' in
          (ROOT/'rsi/index.html').read_text(encoding='utf-8'),
          'Missing homepage entry to unnumbered experience research')
    for card in cards:
        stages=('challenge','insight','design','result')
        check(tuple(card.get('story',{}))==stages,'Paper lacks ordered C-I-D-R reading contract: '+card['id'])
        check(all(0<len(card['story'][stage])<=130 for stage in stages),'C-I-D-R paragraph too long: '+card['id'])
        check(len(card['one_sentence'])<=100,'Paper opening summary too long: '+card['id'])
        check(card['lead_institution'] in card['institutions'],'Leading author institution not in institution list: '+card['id'])
        check(card['institution_source'] and card['publication'],'Missing institution provenance: '+card['id'])
        check(bool(card.get('arxiv')) != bool(card.get('doi')),
              'Every reading card must be a preprint or verified publication: '+card['id'])
        check(set(card['research_coverage'])==question_ids,'Paper missing RSI coverage axes: '+card['id'])
        for axis in card['research_coverage'].values():
            check(axis['level'] in {'core','partial','not_addressed'},'Invalid RSI coverage status: '+card['id'])
            check(axis['contribution'] and axis['open_question'],'Missing RSI coverage evidence/gap: '+card['id'])
    check(len(refs)>=124 and {'E27','S105','S106','S107'}<=refs and {'S100','S101','S102','S103','S104','M100'}<=refs and {'S200', 'B200', 'S202', 'S201', 'S204', 'S203', 'S205'}<=refs and all(f'S{i}' in refs for i in range(26,50)) and all(f'E{i}' in refs for i in range(11,19)) and {'M10','M11','M12','M13','S90','E19','E20','E21','E22','E23','E24','E25','M15','M16'}<=refs and all(f'E{i}' in refs for i in range(90,98)),'Expected I1–I9 sources, including I9 primary education and LLM curricula')
    check(all(f'R{i:02d}' in refs for i in range(1,12)),
          'Curated RSI panorama lacks one or more verified primary-source links')
    panorama=(ROOT/'rsi/literature.html').read_text(encoding='utf-8')
    check('id="rsi-landscape-20261003"' in panorama
          and '思林广不记' in panorama and '2026-10-03' in panorama,
          'External RSI survey provenance / panorama anchor missing')
    for category in ('信号对不对','有没有新东西','采不采得到','吸收了会不会丢','安全：跨越四问'):
        check(category in panorama,'Panorama failure category missing: '+category)
    for source_id in (f'R{i:02d}' for i in range(1,12)):
        check(f'references.html#{source_id}' in panorama,
              'Primary RSI panorama evidence not cited: '+source_id)
    check('不是已被整个领域统一采纳的唯一定义' in panorama
          and '逐篇核对' in panorama and '一手来源' in panorama,
          'Secondary survey and primary-paper evidence must remain separate')
    check('href="literature.html#rsi-landscape-20261003"'
          in (ROOT/'rsi/index.html').read_text(encoding='utf-8'),
          'RSI homepage lacks a clear entry to curated panorama')
    check(source['review_date']=='2026-10-28','Review date drift')
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
        'overview':['index.html','timeline.html'],
        'literature':['literature.html','reading-cards.html','reading-notes.html','references.html'],
        'methods':['cross-domain.html','theory-notes.html','learning-science.html','curriculum-scale-evidence.html'],
        'research':['ideas.html','idea-prioritization.html','ideas.html#idea-1','idea-i2.html','ideas.html#idea-3','ideas.html#idea-4',
                    'idea-i5.html','idea-i6-failure-value.html','idea-i7-learning-order.html',
                    'i8.html','idea-i9-practice-switching.html','idea-i10-learning-novelty.html','idea-i11-emotional-rsi.html','idea-i12-prerequisite-bottleneck.html','learning-admission.html','experience-consolidation.html','experiments.html'],
    }
    check([g['id'] for g in groups]==list(expected_groups),'Incorrect first-level RSI menu order')
    visible_slugs=[]
    for group in groups:
        hrefs=[href for href,_ in group['pages']]
        check(hrefs==expected_groups[group['id']],f'Incorrect ordered submenu: {group["id"]}')
        check(group['title']['zh'] and group['title']['en'],f'Missing bilingual parent title: {group["id"]}')
        visible_slugs.extend(urlsplit(href).path.removesuffix('.html') for href in hrefs)
    check(set(visible_slugs)==set(PAGES)-{'teaching','idea-i6'},
          'Visible RSI pages must exclude only linked historical research')
    research_links=groups[-1]['pages']
    numbered=[label['zh'].split(' ·')[0] for _,label in research_links if label['zh'].startswith('I')]
    check(numbered==[f'I{i}' for i in range(1,14)],'Research ideas I1–I13 must appear once and in order')
    ranking=(ROOT/'rsi/idea-prioritization.html').read_text(encoding='utf-8')
    check('科学上限' in ranking and '完成把握' in ranking and 'Go' in ranking,
          'Ranking page missing the editorial contract')
    check(all(f'id="idea-{i}"' in ranking for i in range(1,14)),
          'Ranking page missing one or more original Idea anchors')
    check('href="idea-prioritization.html"' in (ROOT/'rsi/index.html').read_text(encoding='utf-8')
          and 'href="idea-prioritization.html"' in (ROOT/'rsi/ideas.html').read_text(encoding='utf-8'),
          'Ranking page not reachable from RSI homepage and ideas overview')
    check(not any(href in ('teaching.html','idea-i6.html') for href,_ in research_links),
          'Archived I5 or I6 content still duplicated in numbered navigation')
    page_parent={slug:g['id'] for g in groups for href,_ in g['pages']
                 for slug in [urlsplit(href).path.removesuffix('.html')]}
    page_parent.update({'teaching':'research','idea-i6':'research'})
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
    check(card_html.count('class="reading-story-step"')==4*len(cards),'Each paper must show four clear C-I-D-R steps')
    check(card_html.count('class="reading-overview"')==0,'Dense old paper overview should not lead the card')
    check('id="reading-question-filter"' in card_html and 'id="reading-coverage-filter"' in card_html,'Missing five-question filters')
    for card in cards:
        check(card['lead_institution'] in card_html,'Missing author institution in HTML: '+card['id'])
        coverage='|'.join(f'{q["id"]}:{card["research_coverage"][q["id"]]["level"]}' for q in questions)
        check(coverage in card_html,'Missing exact five-question coverage status: '+card['id'])
    inventive=next((p for p in cards if p['id']=='inventive-production-pf-2023-kapur'),None)
    check(inventive is not None
          and inventive.get('doi')=='10.1038/s41539-023-00165-y'
          and inventive['official_url']=='https://www.nature.com/articles/s41539-023-00165-y',
          'Inventive Production 2023 source or official journal link missing')
    inventive_text=json.dumps(inventive,ensure_ascii=False)
    check('E98' in refs and len(inventive['deep_read']['sections'])>=7
          and all(term in inventive_text for term in
                  ('112','105','62.589','105.518','因果','成本','平台期','直接纠错','上限')),
          'Inventive Production deep read must retain results and efficiency/ceiling caveats')
    for page in ('learning-science.html','idea-i6-failure-value.html'):
        check('reading-notes.html#deep-inventive-production-pf-2023-kapur'
              in (ROOT/'rsi'/page).read_text(encoding='utf-8'),
              'Missing practical RSI cross-link to Inventive Production note: '+page)
    centaur=next((p for p in cards if p['id']=='nature2025-centaur-binz'),None)
    check(centaur is not None
          and centaur.get('doi')=='10.1038/s41586-025-09215-4'
          and centaur.get('official_url')=='https://www.nature.com/articles/s41586-025-09215-4'
          and 'Helmholtz Munich' in centaur['lead_institution'],
          'Centaur Nature 2025 official DOI or leading affiliation is missing')
    check(all(f'E{i}' in refs for i in (701,702,703,704)),
          'Centaur, StudentSim, ICLR precursor or simulation-validity primary sources missing')
    centaur_text=json.dumps(centaur,ensure_ascii=False)
    check(len(centaur['deep_read']['metric_summary'])==5
          and len(centaur['deep_read']['sections'])>=10
          and all(token in centaur_text for token in
                  ('160','60,092','10,681,650','253,597,411',
                   '0.15%','rank=8','0.44','0.58','0.56',
                   '0.51','0.63','0.42','0.62','1.65','1.92',
                   '54.12','52.78','0.144','0.007','0.045',
                   '181.7','72.5','71.7','StudentSim',
                   '独立','持久','不等于')),
          'Centaur key quantitative evidence and real-update scientific boundary missing')
    check(centaur['links']['data']=='https://huggingface.co/datasets/marcelbinz/Psych-101'
          and centaur['links']['adapter']=='https://huggingface.co/marcelbinz/Llama-3.1-Centaur-70B-adapter',
          'Centaur public data and adapter source links missing')
    for page in ('learning-science.html','idea-i2.html'):
        source_html=(ROOT/'rsi'/page).read_text(encoding='utf-8')
        check('reading-notes.html#deep-nature2025-centaur-binz' in source_html
              and 'href="references.html#E701"' in source_html
              and 'href="references.html#E702"' in source_html,
              'Centaur / StudentSim I2 and learning science cross-links missing on '+page)
    moral=next((p for p in cards if p['id']=='nhb2025-moral-strategy-maier'),None)
    check(moral is not None
          and moral.get('doi')=='10.1038/s41562-025-02271-w'
          and moral['official_url']=='https://www.nature.com/articles/s41562-025-02271-w',
          'NHB 2025 metacognitive moral learning primary source missing')
    check('University College London' in moral['lead_institution']
          and all(f'E{i}' in refs for i in range(311,316)),
          'NHB lead institution or related-work primary source records missing')
    moral_text=json.dumps(moral,ensure_ascii=False)
    check(all(term in moral_text for term in (
        '2,328','2328','13次','387','380','834','727',
        '51.8%','68.2%','55.7%','44.3%',
        '89.4%','27.9%','67.3%',
        '97.70','86.73','0.047','0.064','0.061',
        '121分钟','99分钟','数小时','规则','安全')),
        'Missing experiment-specific values or scientific caveats in moral learning note')
    moral_sections={s['id'] for s in moral['deep_read']['sections']}
    check({'action-or-strategy','learning-models','feedback-manipulation',
           'experiment-one','experiment-two','experiment-three',
           'experiment-four','rsi-research-boundary'}<=moral_sections,
          'Action-vs-strategy design, four experiments or RSI limits missing')
    moral_note=(ROOT/'rsi/reading-notes.html').read_text(encoding='utf-8')
    check('id="deep-nhb2025-moral-strategy-maier--stage-related"' in moral_note
          and all(f'id="deep-nhb2025-moral-strategy-maier--{sid}"' in moral_note
                  for sid in ('experiment-one','experiment-two','experiment-three','experiment-four')),
          'New moral strategy note or related-work section not rendered')
    check('href="reading-notes.html#deep-nhb2025-moral-strategy-maier"'
          in (ROOT/'rsi/reading-cards.html').read_text(encoding='utf-8'),
          'Moral learning card lacks long-form reading link')
    similarity=next((p for p in cards if p['id']=='nc2025-task-similarity-menghi'),None)
    check(similarity is not None
          and similarity.get('doi')=='10.1038/s41467-025-66849-8'
          and similarity['official_url']=='https://www.nature.com/articles/s41467-025-66849-8'
          and similarity['lead_institution']=='Max Planck Institute for Human Cognitive and Brain Sciences',
          'Task similarity NC 2025 source or affiliations missing')
    check(all(f'E{i}' in refs for i in (99,100,101,102,103)),
          'NC 2025 target and four verified background sources missing')
    similarity_text=json.dumps(similarity,ensure_ascii=False)
    check(len(similarity['deep_read']['sections'])>=9
          and all(token in similarity_text for token in
                  ('60.44%','66.61%','6.17','0.005','0.159','0.709',
                   'Figure 6','完全正交','部分重叠','完全相同','50 次')),
          'NC 2025 figure-specific results or non-monotonic input geometry missing')
    check('没有 Blocked/Interleaved 直接随机对照' in similarity_text
          or '没有 Blocked/Interleaved 直接随机对照' in ''.join(similarity['boundaries']),
          'NC 2025 must not be mistaken for a blocked/interleaved study')
    osm=next((p for p in cards if p['id']=='nature2025-orthogonalized-state-machine-sun'),None)
    check(osm is not None and osm.get('doi')=='10.1038/s41586-024-08548-w'
          and osm['official_url']=='https://www.nature.com/articles/s41586-024-08548-w'
          and osm['lead_institution']=='Janelia Research Campus, Howard Hughes Medical Institute',
          'Nature 2025 OSM source citation or institution missing')
    check({'E353','E354','M66','M67','M68'}<=refs,
          'Nature 2025 OSM and strongest CSCG/LLM nearest works missing')
    osmtext=json.dumps(osm,ensure_ascii=False)
    check(len(osm['deep_read']['sections'])>=12
          and all(key in {s['id'] for s in osm['deep_read']['sections']} for key in (
               '2acdc-task','behavior','state-separation','cscg','model-counterexamples',
               'transfer-cues','nearest-work','rsi-p0'))
          and all(t in osmtext for t in (
               '4,682','3,954','p=0.004','State Aliasing','False Split',
               'CSCG','LSTM','Transformer','I8','I9')),
          'OSM Nature findings, counterexamples or falsifiable RSI extension absent')
    osmnote=(ROOT/'rsi/reading-notes.html').read_text(encoding='utf-8')
    check('id="deep-nature2025-orthogonalized-state-machine-sun"' in osmnote
          and 'id="deep-nature2025-orthogonalized-state-machine-sun--rsi-p0"' in osmnote,
          'Nature OSM long read or executable study anchor not generated')
    for page, section in [('learning-science','orthogonalized-state-machine'),
                          ('i8','nature2025-state-machine'),
                          ('idea-i9-practice-switching','nature2025-orthogonalized-state')]:
        ht=(ROOT/'rsi'/f'{page}.html').read_text(encoding='utf-8')
        check(f'id="{section}"' in ht
              and 'reading-notes.html#deep-nature2025-orthogonalized-state-machine-sun' in ht
              and 'href="references.html#E353"' in ht,
              'Nature OSM must link to learning science and both I8/I9 mechanisms: '+page)
    check('reading-notes.html#deep-nature2025-orthogonalized-state-machine-sun'
          in (ROOT/'rsi/index.html').read_text(encoding='utf-8'),
          'Nature OSM long-form reading absent from RSI homepage')
    holton=next((p for p in cards if p['id']=='nhb2025-transfer-interference-holton'),None)
    check(holton is not None and holton['doi']=='10.1038/s41562-025-02318-y'
          and holton['official_url']=='https://www.nature.com/articles/s41562-025-02318-y'
          and holton['links']['code']=='https://github.com/eleanorholton/transfer-interference',
          'NHB transfer/interference primary source, journal identity or author code missing')
    holton_sections={s['id'] for s in holton['deep_read']['sections']}
    check({'challenge-transfer-interference','experiment-aba-protocol','metrics-von-mises',
           'figure-2-network-reuse','figure-3-replication','figure-4-individuals',
           'rich-lazy-experiments','graded-update-vs-swap','closest-work-boundary',
           'rsi-i3-insight','rsi-p0-aba','rsi-p1-p2','cross-idea-and-limits'}
          <=holton_sections,
          'NHB reading missing human protocol, ANN mechanisms, figures or RSI P0/P1/P2')
    holton_text=json.dumps(holton,ensure_ascii=False)
    check('E100' in refs and all(k in holton_text for k in
          ('305','151','154','120','Near','Far','0.006','0.013',
           '0.49°','75.10°','Lumpers','Splitters','Rich','Lazy',
           'Rule-Misuse','I3','I9','I13','人脑','因果')),
          'NHB original sample, transfer metrics, causal limits or idea boundary lost')
    holton_note=(ROOT/'rsi/reading-notes.html').read_text(encoding='utf-8')
    hurl='reading-notes.html#deep-nhb2025-transfer-interference-holton'
    check('id="deep-nhb2025-transfer-interference-holton"' in holton_note
          and 'id="deep-nhb2025-transfer-interference-holton--rsi-p0-aba"' in holton_note
          and 'id="deep-nhb2025-transfer-interference-holton--figure-4-individuals"' in holton_note,
          'NHB complete reading or decisive P0 and figure anchors not built')
    check(all(hurl in (ROOT/'rsi'/f'{p}.html').read_text(encoding='utf-8')
              for p in ('index','ideas','idea-i9-practice-switching',
                        'learning-science','learning-admission')),
          'NHB paper not cross-linked from homepage, I3, I9, I13 or learning science')
    check('href="references.html#E100"' in (ROOT/'rsi/ideas.html').read_text(encoding='utf-8'),
          'NHB primary source registry E100 not cited from I3')
    schema=next((p for p in cards if p['id']=='nc2026-schema-reuse-tian'),None)
    check(schema is not None
          and schema['doi']=='10.1038/s41467-026-68692-x'
          and schema['official_url']=='https://www.nature.com/articles/s41467-026-68692-x',
          'NC 2026 schema reuse official paper identification missing')
    schema_sections={s['id'] for s in schema['deep_read']['sections']}
    check({'core-question','neural-mechanism','protocol-monkeys','numbers-and-limitations',
           'strong-closest-work','rsi-beyond-orthogonality','schema-lifecycle',
           'first-falsifier','recursive-test','research-position'}<=schema_sections,
          'Schema reuse note missing key original evidence or RSI research design')
    check(all(x in json.dumps(schema,ensure_ascii=False)
              for x in ('Reverse-A','81.4','0.47','0.49','因果','元规则')),
          'Schema neural caveats or causal design lost')
    check({'E320','M311','M312','M313','S311','S312','S313','S314'}<=refs,
          'Schema paper/closest-work references missing or overwritten')
    check('reading-notes.html#deep-nc2026-schema-reuse-tian'
          in (ROOT/'rsi/learning-science.html').read_text(encoding='utf-8')
          and 'reading-notes.html#deep-nc2026-schema-reuse-tian'
          in (ROOT/'rsi/ideas.html').read_text(encoding='utf-8'),
          'Schema research is not linked from learning science and I3')
    plasticity=next((p for p in cards if p['id']=='nature2024-loss-plasticity-dohare'),None)
    check(plasticity is not None and plasticity['doi']=='10.1038/s41586-024-07711-7'
          and plasticity['official_url']=='https://www.nature.com/articles/s41586-024-07711-7'
          and plasticity['links']['code']=='https://github.com/shibhansh/loss-of-plasticity',
          'Nature 2024 plasticity paper, DOI or primary code source missing')
    pl_text=json.dumps(plasticity,ensure_ascii=False)
    check('M22' in refs and len(plasticity['deep_read']['sections'])>=9
          and all(t in pl_text for t in ('ImageNet','CIFAR-100','Ant-v3','Permuted MNIST',
                                        '250 epochs','200 epochs','40','5个百分点',
                                        '10^-5','因果','RSI','未来可学习性')),
          'Nature plasticity experiment design or RSI uncertainty missing')
    notes=(ROOT/'rsi/reading-notes.html').read_text(encoding='utf-8')
    check('id="deep-nature2024-loss-plasticity-dohare"' in notes
          and 'id="deep-nature2024-loss-plasticity-dohare--cheap-rsi-test"' in notes,
          'Nature plasticity full reading or P0 falsifier not built')
    admission_text=(ROOT/'rsi/learning-admission.html').read_text(encoding='utf-8')
    i9_plasticity=(ROOT/'rsi/idea-i9-practice-switching.html').read_text(encoding='utf-8')
    check('id="plasticity"' in admission_text
          and 'reading-notes.html#deep-nature2024-loss-plasticity-dohare' in admission_text
          and 'reading-notes.html#deep-nature2024-loss-plasticity-dohare' in i9_plasticity
          and 'learning-admission.html#plasticity' in i9_plasticity,
          'Missing cross-links to the Nature reading, Learning Admission and I9 note')
    misalign=next((p for p in cards if p['id']=='nature2026-narrow-misalignment-betley'),None)
    check(misalign is not None and misalign['doi']=='10.1038/s41586-025-09937-5'
          and misalign['official_url']=='https://www.nature.com/articles/s41586-025-09937-5'
          and misalign['links']['code']=='https://github.com/emergent-misalignment/emergent-misalignment/',
          'Nature 2026 misalignment official DOI, paper or code missing')
    misalign_text=json.dumps(misalign,ensure_ascii=False)
    check({'M450','M451','M452','M453'}<=refs
          and len(misalign['deep_read']['sections'])>=13
          and all(t in misalign_text for t in
                  ('6,000','14,927','GPT-4o','GPT-4.1','Qwen2.5',
                   'JSON','Python','40步','ICML 2025',
                   '单纯','不等于','因果','Learning Admission')),
          'Nature 2026 paper must distinguish original evidence, controls, metrics and RSI transfer')
    misalign_note=(ROOT/'rsi/reading-notes.html').read_text(encoding='utf-8')
    check('id="deep-nature2026-narrow-misalignment-betley"' in misalign_note
          and 'id="deep-nature2026-narrow-misalignment-betley--training-dynamics"' in misalign_note
          and 'id="deep-nature2026-narrow-misalignment-betley--rsi-experiment"' in misalign_note,
          'Misalignment paper reading and P0 experiment are not rendered')
    note_url='reading-notes.html#deep-nature2026-narrow-misalignment-betley'
    check('id="nonlocal-effects"' in admission_text and note_url in admission_text
          and note_url in (ROOT/'rsi/ideas.html').read_text(encoding='utf-8'),
          'Missing Learning Admission / I3 cross-links for non-local behavior drift')
    check(all(f'href="references.html#{s}"' in admission_text
              for s in ('M450','M451','M452','M453')),
          'Learning Admission lacks auditable primary/nearest sources')
    npj=next((p for p in cards if p['id']=='optimal-practice-2020-eglington'),None)
    check(npj is not None and npj.get('doi')=='10.1038/s41539-020-00074-4',
          '2020 npj paper not correctly identified by its real DOI')
    check(npj['links']['html']=='https://www.nature.com/articles/s41539-020-00074-4'
          and npj['links']['code']=='https://osf.io/d9rms/',
          'Publisher original or author-provided simulation materials missing')
    check('等待' in ' '.join(npj['boundaries']) and '前置' in ' '.join(npj['our_relevance']),
          'Forgot the distinction between retrieval decay and learning a new skill')
    motor=next((p for p in cards if p['id']=='hypothesis-testing-2026-ding'),None)
    check(motor is not None and motor.get('doi')=='10.1038/s41539-026-00428-4',
          'The npj 2026 hypothesis testing paper must be source-identified correctly')
    check(motor['links']['html']=='https://www.nature.com/articles/s41539-026-00428-4'
          and motor['links']['code']=='https://osf.io/aknqj/',
          'Motor-learning paper official source or OpenMotor dataset link missing')
    check(all(term in ' '.join(motor['boundaries']) for term in ('0.5','LLM')),
          'Motor learning should not be misrepresented as proof of optimal p=0.5')
    motor_sections={s['id']:s for s in motor['deep_read']['sections']}
    check({'structured-vs-random','figure-four-learner-trajectories',
           'motor-learning-related-work'}<=set(motor_sections),
          'Missing the motor hypothesis-test mechanisms, seven learner clusters or closest-work distinctions')
    trajectory=json.dumps(motor_sections['figure-four-learner-trajectories'],ensure_ascii=False)
    check(all(n in trajectory for n in ('476','560','C1','C2','C3','C4','C5','C6','C7','62.2%','11.3%','6.1%')),
          'Figure 4 learner-cluster evidence lost or denominator changed')
    mechanism=json.dumps(motor_sections['structured-vs-random'],ensure_ascii=False)
    check('0.694' in mechanism and '0.088' in mechanism and 'model-based RL' in mechanism,
          'Experiment 2 nonsignificant JSD and RL distinction must be explicit')
    motor_html=(ROOT/'rsi/reading-notes.html').read_text(encoding='utf-8')
    for sid in ('structured-vs-random','figure-four-learner-trajectories','motor-learning-related-work'):
        check(f'id="deep-hypothesis-testing-2026-ding--{sid}"' in motor_html,
              'Updated motor reading anchor not built: '+sid)
    ideas_html=(ROOT/'rsi/ideas.html').read_text(encoding='utf-8')
    i8_html=(ROOT/'rsi/i8.html').read_text(encoding='utf-8')
    check('reading-notes.html#deep-hypothesis-testing-2026-ding--structured-vs-random' in ideas_html
          and 'reading-notes.html#deep-hypothesis-testing-2026-ding--figure-four-learner-trajectories' in i8_html
          and 'I4' in ''.join(motor['our_relevance']) and 'I8' in ''.join(motor['our_relevance']),
          'I4/I8 did not inherit the new hypothesis-testing evidence')
    check('reading-notes.html#deep-hypothesis-testing-2026-ding'
          in (ROOT/'rsi/idea-i6-failure-value.html').read_text(encoding='utf-8'),
          'I6 must retain its motor-hypothesis-testing evidence link')
    check('E26' in refs and 'SOAR' in (ROOT/'rsi/literature.html').read_text(encoding='utf-8')
          and '50%' in (ROOT/'rsi/literature.html').read_text(encoding='utf-8'),
          'npj 2026 must be linked to SOAR and the difficulty proxy in closest-work discussion')
    check('reading-notes.html#deep-hypothesis-testing-2026-ding' in (ROOT/'rsi/learning-science.html').read_text(encoding='utf-8'),
          'Mechanism transfer not linked from learning-science page')
    curriculum=next((p for p in cards if p['id']=='acl2026-good-curriculum-jia'),None)
    check(curriculum is not None and curriculum.get('doi')=='10.18653/v1/2026.acl-long.1591',
          'ACL 2026 curriculum paper must use the official anthology DOI')
    check(curriculum['links']['html']=='https://aclanthology.org/2026.acl-long.1591/'
          and curriculum['lead_institution']=='Dartmouth College',
          'ACL venue or leading affiliation mismatch')
    dims=curriculum['deep_read']['metric_summary']
    check(len(dims)==5,'Curriculum five-metric-family overview missing')
    check(all('Table '+str(i) in dims[i-1]['result'] for i in range(1,6)),
          'Each curriculum dimension must point to its original main-result table')
    sections=curriculum['deep_read']['sections']
    check(all(any(s['id']==id for s in sections) for id in (
        'problem-difficulty','model-surprisal','confidence-margin',
        'predictive-uncertainty','decision-variability','results-five-families','metric-tiers')),
        'Curriculum must explain all five measurements and their results')
    allblocks=json.dumps(sections,ensure_ascii=False)
    check(all(k in allblocks for k in ('RS','SC','CD','ACC','SLP','TLP','LG','SLE','TLE','VACC')),
          'One or more of the ten concrete metrics missing')
    check(all(k in allblocks for k in ('70.90%','24.02%','69.92%','79.49%','60.16%','12/15')),
          'One or more of five main-table metric result examples missing')
    check('Online P50' in allblocks and '不是' in allblocks,
          'Missing static VACC vs online P50 distinction')
    ilp=next((p for p in cards if p['id']=='acl2026-sft-ilp-xue'),None)
    check(ilp is not None and ilp.get('doi')=='10.18653/v1/2026.acl-long.1393'
          and ilp.get('official_url')=='https://aclanthology.org/2026.acl-long.1393/',
          'ACL 2026 SFT paper source or DOI not verified')
    check(len(ilp['deep_read']['metric_summary'])==5
          and len({s['id'] for s in ilp['deep_read']['sections']})==len(ilp['deep_read']['sections']),
          'Five causes or unique section anchors missing from ILP deep read')
    ilptext=json.dumps(ilp,ensure_ascii=False)
    check(all(token in ilptext for token in (
        '15.3%','18.7%','13.2%','14.1%','17.4%','14.6%',
        '65.3','66.8','82.1','68.1','70.9','82.3','85.1','0.41','0.53',
        '88.2','90.1','78%'
    )), 'Incomplete learning 5-category empirical evidence missing or altered')
    check(all(token in ilptext for token in ('多选题','训练题','迁移','未见','预算','不等于')),
          'ILP causal and training-item versus transfer boundary missing')
    deep_notes=[p for p in cards if p.get('deep_read')]
    notes_html=(ROOT/'rsi/reading-notes.html').read_text(encoding='utf-8')
    katyal=next((p for p in cards if p['id']=='nc2025-metacognition-underconfidence-katyal'),None)
    check(katyal is not None and katyal.get('doi')=='10.1038/s41467-025-57040-0'
          and katyal['official_url']=='https://www.nature.com/articles/s41467-025-57040-0',
          'NC 2025 metacognition original article, DOI or reading card missing')
    katyal_text=json.dumps(katyal,ensure_ascii=False)
    check('E29' in refs and len(katyal['deep_read']['sections'])>=11
          and all(t in katyal_text for t in ('230','278','1.77','0.702','0.005',
                                              'D1','D2','D3','ΔLR_f','ΔLR_c','Beta',
                                              '选择性','真实反馈','I11')),
          'NC 2025 feedback bias, model mechanics or numerical source boundaries missing')
    check('id="deep-nc2025-metacognition-underconfidence-katyal"' in notes_html
          and 'id="deep-nc2025-metacognition-underconfidence-katyal--confidence-model"' in notes_html,
          'NC 2025 complete deep read and Beta equations not visible')
    check('id="metacognitive-confidence"' in (ROOT/'rsi/learning-science.html').read_text(encoding='utf-8')
          and 'href="references.html#E29"' in (ROOT/'rsi/learning-science.html').read_text(encoding='utf-8'),
          'NC 2025 learning-science evidence missing or unreferenced')
    check('reading-notes.html#deep-nc2025-metacognition-underconfidence-katyal' in
          (ROOT/'rsi/idea-i11-emotional-rsi.html').read_text(encoding='utf-8') and
          'href="references.html#E29"' in (ROOT/'rsi/idea-i11-emotional-rsi.html').read_text(encoding='utf-8'),
          'I11 must distinguish feedback selection from emotional tone and cite NC 2025')
    check('reading-notes.html#deep-nc2025-metacognition-underconfidence-katyal' in
          (ROOT/'rsi/index.html').read_text(encoding='utf-8'),
          'NC 2025 full read not discoverable from RSI homepage')
    expected_metric_items=sum(len(p.get('deep_read',{}).get('metric_summary',[])) for p in deep_notes)
    check('id="deep-acl2026-good-curriculum-jia"' in notes_html
          and notes_html.count('class="deep-metric-item"')==expected_metric_items,
          'Five-item overviews must render once for each compatible reading')
    check('id="deep-acl2026-sft-ilp-xue"' in notes_html
          and '五种学不会的原因 · 对应诊断与实验' in notes_html,
          'ILP must show its own five-causes summary before detailed sections')
    for paper in deep_notes:
        pid=paper['id']
        check(f'href="reading-notes.html#deep-{pid}"' in card_html,
              'Deep-read link missing from compact card: '+pid)
        check(f'id="deep-{pid}"' in notes_html,
              'Deep-read article missing: '+pid)
        section_ids=[s['id'] for s in paper['deep_read']['sections']]
        check(len(section_ids)==len(set(section_ids)) and section_ids,
              'Deep-read sections missing or duplicated: '+pid)
        stages={s['stage'] for s in paper['deep_read']['sections']}
        check({'challenge','insight','design','result'}<=stages,'Deep read missing one of four main stages: '+pid)
        for stage in ['challenge','insight','design','result']:
            check(f'id="deep-{pid}--stage-{stage}"' in notes_html,
                  'Visible C-I-D-R heading missing: '+pid+'/'+stage)
        for section in section_ids:
            check(f'id="deep-{pid}--{section}"' in notes_html,
                  'Deep-read section missing: '+pid+'/'+section)
    related_data=json.loads((ROOT/'rsi/related-work.json').read_text(encoding='utf-8'))
    check(related_data['schema_version']==1,'Related-work registry schema changed without migration')
    check(len(related_data['targets'])>=1,'No audited related-work comparisons')
    for target in related_data['targets']:
        pid=target['paper_id']
        check(any(p['id']==pid and p.get('deep_read') for p in cards),
              'Related-work target lacks a source reading card: '+pid)
        closest=[x for x in target['works'] if x['distance']=='closest']
        check(3<=len(closest)<=8,'Closest work table must contain 3-8 true comparators')
        check(f'href="reading-notes.html#deep-{pid}--stage-related"' in card_html,
              'Card lacks Related Work jump link: '+pid)
        check(f'id="deep-{pid}--stage-related"' in notes_html,
              'Related Work stage not rendered: '+pid)
        check(len({x['id'] for x in target['works']})==len(target['works']),
              'Duplicate related work ID: '+pid)
        for work in target['works']:
            check(work['primary_url'].startswith('https://'),'Non-official related source URL: '+work['id'])
            check(all(work.get(key) for key in ['shared','difference','why','evidence','decisive_test','source_scope']),
                  'Unverifiable related work comparison: '+work['id'])
            check(f'id="related-{pid}--{work["id"]}"' in notes_html,
                  'Related-work paper details missing: '+work['id'])
    check('读表结论' in notes_html and '不能' in notes_html,
          'Related-work comparison lacks calibrated conclusion and limitations')
    check('教学示例' in notes_html and '非论文' in notes_html,
          'Deep-read evidence provenance caveat missing')
    check(all(
        (p.get('arxiv') and p['links']['html'].startswith('https://arxiv.org/'))
        or (p.get('arxiv') and p.get('conference_official_primary') is True
            and p.get('official_url') == p['links']['html']
            and p['official_url'].startswith('https://proceedings.iclr.cc/paper_files/paper/2026/'))
        or (p.get('doi') and p.get('official_url') == p['links']['html']
            and p['official_url'].startswith('https://'))
        for p in cards
    ),'Paper lacks a verified arXiv or publisher original link')
    ideas=parsed[ROOT/'rsi/ideas.html']
    check(all(f'idea-{i}' in ideas.ids for i in range(1,13)),'I1–I9 and I11 anchors missing from research board')
    ideas_text=(ROOT/'rsi/ideas.html').read_text(encoding='utf-8')
    for name in ['R²Orch','PATS','RSIFlow','HCL','SkillBoost','Trace2Skill','PopuLoRA','OPCoD','MACE']:
        check(name in ideas_text,f'Missing nearest-work comparison: {name}')
    # All eight independent ideas share one readable argument chain;
    # later ideas must not collapse to short summaries or links to detail pages.
    ordered_headings = (
        '<h3>Challenge <small>（难在哪里）</small></h3>',
        '<h3>现有工作 <small>（别人研究了什么）</small></h3>',
        '<h3>Insight <small>（为何可解）</small></h3>',
        '<h3>Design <small>（如何做）</small></h3>',
        '<h3>实验设计 <small>（怎么验证）</small></h3>',
    )
    for idea_number in range(1,13):
        section = ideas_text.split(f'id="idea-{idea_number}"', 1)[1].split('</section>', 1)[0]
        locations = [section.find(heading) for heading in ordered_headings]
        check(all(pos >= 0 for pos in locations) and locations == sorted(locations),
              f'I{idea_number}: Challenge -> Related Work -> Insight -> Design -> Experiment order drift')
        check(section.count('class="idea-step"') == 5,
              f'I{idea_number}: expected exactly five argument blocks')
        check(section.count('class="flow"') >= 1, f'I{idea_number}: four-step method flow missing')
    idea_positions = [ideas_text.index(f'id="idea-{i}"') for i in list(range(1,10))+[11,12]]
    check(idea_positions == sorted(idea_positions),'Published I1–I9 and I11 sections are out of order')
    check(ideas_text.index('id="orthogonal"') > idea_positions[-1],
          'Independent I6-I9 and I11 comparison must follow full scientific narratives')
    for i, detail in ((6,'idea-i6-failure-value.html'),(7,'idea-i7-learning-order.html'),(8,'i8.html'),(9,'idea-i9-practice-switching.html'),(10,'idea-i10-learning-novelty.html'),(11,'idea-i11-emotional-rsi.html'),(12,'idea-i12-prerequisite-bottleneck.html')):
        section = ideas_text.split(f'id="idea-{i}"', 1)[1].split('</section>', 1)[0]
        check(f'href="{detail}"' in section, f'I{i}: full scientific detail page must remain linked')
        check('正交边界' in section,'I6-I9 separation lost in I'+str(i))
    check('十模型互教' in ideas_text and '不需要外部教师告诉标准答案' in ideas_text,'I5/I4 hypothesis drift')
    i2_text=(ROOT/'rsi/idea-i2.html').read_text(encoding='utf-8')
    check('href="idea-i2.html"' in ideas_text and 'href="idea-i2.html"' in (ROOT/'rsi/index.html').read_text(encoding='utf-8'),
          'I2 detailed plan must be reachable from both home and ideas')
    check(all(f'id="{sid}"' in i2_text for sid in ('question','evidence','dialogue-evidence','challenge','insight','related','design','objective','dialogue-p0','experiments','boundaries')),
          'I2 teaching co-evolution or bidirectional diagnostic sections missing')
    check(all(f'href="references.html#{ref}"' in i2_text for ref in ('S100','S101','S102','S103','S104','M100','S17','S19','S20','S33','E27','S105','S106','S107')),
          'I2 verified closest-work or feedback uptake references missing')
    check(all(term in i2_text for term in ('冻结学生','TeachingGain','固定教师','独立学习增益','教学 LoRA','任务 Skill','I5','I6','I7','I8')),
          'I2 must separate pedagogical gains, student learning, carriers and other ideas')
    check('id="i2-coevolution"' in (ROOT/'rsi/experiments.html').read_text(encoding='utf-8'),
          'I2 execution entry missing')
    # Centaur/StudentSim ground learner-response modeling in actual parameter learning,
    # not next-answer behavior. Keep original I2 interactive-response E0 untouched.
    response_sections=('learner-response-question','learner-response-p0',
                       'learner-response-p1','learner-response-p2')
    check(all(f'id="{sid}"' in i2_text for sid in response_sections),
          'Centaur-inspired I2 LR-P0/P1/P2 study and causal question missing')
    check(all(f'href="references.html#{rid}"' in i2_text
              for rid in ('E701','E702','E703','E704','S47')),
          'Centaur/StudentSim/SOAR nearest sources missing from I2')
    check(all(term in i2_text for term in
              ('120','40','160','状态','交互','StudentSim','contextual bandit',
               '真实 LoRA','更新前','旧能力','6 个','Go / Merge / Stop')),
          'I2 LR-P0/1/2 evidence controls, cost or retention missing')
    response_protocol=json.loads((ROOT/'rsi/i2-learner-response-protocol.json').read_text(encoding='utf-8'))
    check(response_protocol['idea_id']=='I2'
          and response_protocol['status']=='research_design_not_executed'
          and response_protocol['pilot']['total_real_update_branches']==160
          and response_protocol['pilot']['pedagogical_branch_count']==120
          and {'P0','P1','P2'} <= set(response_protocol['evaluation'])
          and len(response_protocol['baselines'])>=7,
          'I2 learning-response machine-readable protocol invalid or claims completed work')
    check('id="i2-learner-response"' in (ROOT/'rsi/experiments.html').read_text(encoding='utf-8')
          and 'href="i2-learner-response-protocol.json"' in i2_text
          and 'idea-i2.html#learner-response-question' in (ROOT/'rsi/index.html').read_text(encoding='utf-8')
          and 'reading-notes.html#deep-nature2025-centaur-binz' in (ROOT/'rsi/index.html').read_text(encoding='utf-8'),
          'I2 learner-response protocol, index entry or Centaur reading note not discoverable')

    for arm in ('A · 单向解释','B · 固定多轮','C · 真实双向','D · 错配回应'):
        check(arm in i2_text,'I2 A/B/C/D response-matching control missing: '+arm)
    check('id="i2-dialogue-four-arms"' in i2_text and 'C−D' in i2_text and '总 Token' in i2_text,
          'I2 response-specific information comparison or feedback quantity control missing')
    check('idea-i2.html#dialogue-p0' in (ROOT/'rsi/experiments.html').read_text(encoding='utf-8'),
          'I2 P0 must be linked from experiment execution page')
    assert all(f'href="references.html#{rid}"' in (ROOT/'rsi/learning-science.html').read_text(encoding='utf-8') for rid in ('E27','S105','S106')), 'Feedback uptake evidence must be primary-sourced'
    check('id="feedback-uptake"' in (ROOT/'rsi/learning-science.html').read_text(encoding='utf-8'),
          'npj 2025 Ignore/Copy/Apply reading missing')
    i5_text=(ROOT/'rsi/idea-i5.html').read_text(encoding='utf-8')
    check('href="idea-i5.html"' in ideas_text and 'href="idea-i5.html"' in (ROOT/'rsi/index.html').read_text(encoding='utf-8'),'I5 page not linked from home/ideas')
    check(all(k in i5_text for k in ('十个模型','换舞伴','Bridge ties bind collective memories','PopuLoRA','OPCoD','HACE','I7','未见任务')),'I5 evidence, orthogonal labels or controls missing')
    check(all(f'id="{x}"' in i5_text for x in ('scene','papers','collisions','challenge','insight','design','experiments','teaching-feedback','summary')),'I5 unified sections missing')
    check('href="idea-i2.html#dialogue-p0"' in i5_text and 'href="references.html#E27"' in i5_text,
          'I5 must fix teaching protocol and link to I2 dialogue information study')
    check('href="teaching.html"' in i5_text and '十模型动态互教' in i5_text,
          'Historical teaching-feedback branch must remain accessible under the sole I5 entry')
    i8_html=(ROOT/'rsi/i8.html').read_text(encoding='utf-8')
    for label in ['Observable Phenomenon','Why','Challenge','Insight','Design','决定性实验','Related Work','预注册判断']:
        check(label in i8_html,'I8 research mechanism structure missing: '+label)
    for ref in ['E12','E13','E14','E15','E18','S17','S40','S41','S42','S43','S44','M10','M11','M13']:
        check(f'href="references.html#{ref}"' in i8_html,'I8 reference missing: '+ref)
    check('语义预测误差' in i8_html and '误导性反馈' in i8_html and '可信反馈门槛' in i8_html,'I8 must retain Pine 2018 prediction-error and misinformation boundary')
    check('href="references.html#E18"' in (ROOT/'rsi/learning-science.html').read_text(encoding='utf-8'),'Pine 2018 must be cross-linked from learning science')
    check('href="references.html#E27"' in i8_html and 'idea-i2.html#dialogue-p0' in i8_html,
          'I8 must distinguish feedback application evidence from I2 interaction mechanism')
    check('id="i8-related-matrix"' in i8_html, 'I8 closest-work comparison table missing')
    check('M27' in refs
          and 'reading-notes.html#deep-acl2026-sft-ilp-xue' in i8_html
          and '训练题' in i8_html and '异结构' in i8_html,
          'I8 must explicitly compare ILP training-example repairs against rule transfer')
    check('reading-notes.html#deep-acl2026-sft-ilp-xue' in ideas_text
          and all(f'idea-{i}' in ideas.ids for i in (3,6,8)),
          'I3, I6 and I8 overview must use ILP primary evidence and keep idea boundaries')
    check('reading-notes.html#deep-acl2026-sft-ilp-xue'
          in (ROOT/'rsi/idea-i6-failure-value.html').read_text(encoding='utf-8'),
          'I6 detail must include ILP as a matching/confounding baseline')
    for axis in ['研究对象与条件','用什么信号判断','操作与实际评价','与 I8 相同 / 不同之处']:
        check(axis in i8_html,'I8 related-work scientific comparison axis missing: '+axis)
    for close in ['Self-Error-Instruct','LESS','DATAPROPHET','SOAR','RULE-EDIT','Learning Dynamics','LENS / ACE','I8（待验证）']:
        check(close in i8_html,'I8 nearest work missing from comparison matrix: '+close)
    for boundary in ['Same','Different','Why','Evidence','没有结果']:
        check(boundary in i8_html,'I8 missing honest closest-work boundary: '+boundary)
    check('href="i8.html"' in ideas_text,'I8 missing from idea board')
    check('reading-notes.html#deep-nc2025-task-similarity-menghi' in ideas_text
          and all(f'href="references.html#E{i}"' in ideas_text for i in (99,100)),
          'I9 and I3 overview must link to NC 2025 and sequential-learning contrast')
    check('href="i8.html"' in (ROOT/'rsi/index.html').read_text(encoding='utf-8'),'I8 missing from homepage')
    i6_text=(ROOT/'rsi/idea-i6-failure-value.html').read_text(encoding='utf-8')
    i7_text=(ROOT/'rsi/idea-i7-learning-order.html').read_text(encoding='utf-8')
    historical_i6=(ROOT/'rsi/idea-i6.html').read_text(encoding='utf-8')
    overview=(ROOT/'rsi/index.html').read_text(encoding='utf-8')
    for href in ['idea-i6-failure-value.html','idea-i7-learning-order.html']:
        check(f'href="{href}"' in ideas_text and f'href="{href}"' in overview,
              'Current I6/I7 page not reachable from board and homepage: '+href)
    check('失败轨迹' in i6_text and '固定教学顺序' in i6_text and 'I8' in i6_text,
          'Current I6 must isolate failed-process effects from learning order and I8')
    check(all(f'id="{x}"' in i6_text for x in ('question','observation','reason','protocol','stopping','stop-experiment','related','gate')),
          'Current I6 must include failure-value-based stopping and revisit protocol')
    check(all(k in i6_text for k in ('继续尝试当前题','纠正已有错误','换其他错题','暂缓并重访','Deferred Failure Queue','E2 · 继续、停止')),
          'I6 action choices or decisive stopping experiment missing')
    check(all(f'href="references.html#{ref}"' in i6_text for ref in ('E16','E17','S45','S46','S47','S48','S49','M12')),
          'I6 stopping references missing')
    check('id="nc2021"' in i6_text and 'href="references.html#E19"' in i6_text and 'Same Plateau' in i6_text,
          'I6 must archive NC 2021 learning-progress evidence and falsifiable deferred revisit test')
    check('绝对值' in ideas_text.split('id="idea-3"',1)[1].split('</section>',1)[0] and '净能力增益' in ideas_text,
          'I3 must separate observed LP change from retained net capability gain')
    check('href="references.html#E19"' in i8_html and 'idea-i6-failure-value.html#nc2021' in i8_html,
          'I8 must distinguish learning-progress task choice from error-specific transfer')
    check('id="nc2025-task-similarity"' in i8_html
          and 'reading-notes.html#deep-nc2025-task-similarity-menghi' in i8_html,
          'I8 must clarify surface feature versus rule structure and transfer')
    learn_sci=(ROOT/'rsi/learning-science.html').read_text(encoding='utf-8')
    check('id="learning-progress"' in learn_sci and 'href="references.html#E19"' in learn_sci,
          'Learning science must include Ten et al. 2021 with primary citation')
    check('id="task-similarity-nc2025"' in learn_sci
          and 'reading-notes.html#deep-nc2025-task-similarity-menghi' in learn_sci
          and '完全正交' in learn_sci and '部分重叠' in learn_sci,
          'NC 2025 learning-science evidence must include three feature overlap conditions')
    check('先独立尝试' in i7_text and '先看示范' in i7_text and 'I6' in i7_text,
          'Current I7 must isolate learning-order effects')
    i9_text=(ROOT/'rsi/idea-i9-practice-switching.html').read_text(encoding='utf-8')
    check('href="idea-i9-practice-switching.html"' in ideas_text and
          'href="idea-i9-practice-switching.html"' in overview,
          'I9 detail page not reachable from home or overview')
    check(all(f'id="{sid}"' in i9_text for sid in
              ('question','evidence','related','challenge','insight','design','experiments','orthogonal','gate')),
          'I9 scientific argument or experimental section missing')
    check(all(f'href="references.html#{ref}"' in i9_text for ref in
              ('E20','E21','E22','E23','E24','E25','M15','M16')),
          'I9 primary reference missing')
    check('deep-optimal-practice-2020-eglington' in i9_text,
          'I9 must distinguish already-studied item-level scheduling from cross-topic sequencing')
    check('id="nc2025-task-similarity"' in i9_text
          and 'reading-notes.html#deep-nc2025-task-similarity-menghi' in i9_text
          and 'Blocked' in i9_text and 'Interleaved' in i9_text
          and '规则关系' in i9_text and '顺序' in i9_text,
          'I9 must preserve similarity x schedule experiment and its evidence limit')
    check(all(term in i9_text for term in
              ('Blocked','Interleaved','Random Interleaved','规则形成','规则辨别','LoRA','I7','P0','P1','P2')),
          'I9 nearest-work, state mechanism or controlled experiments missing')
    check('id="interleaving"' in learn_sci and 'href="references.html#E20"' in learn_sci,
          'Learning science must cross-link I9 primary experiment')
    experiments_html=(ROOT/'rsi/experiments.html').read_text(encoding='utf-8')
    check('id="i9-practice"' in experiments_html and 'idea-i9-practice-switching.html#experiments' in experiments_html,
          'I9 independent experimental contract missing')
    # I9's future-learnability expansion must not replace the blocked/interleaved core.
    check(all(f'id="{sid}"' in i9_text for sid in
              ('future-question','future-geometry','future-related','future-p0','future-gate')),
          'I9 third-task learnability expansion missing or a section anchor was renamed')
    check(all(f'href="references.html#{ref}"' in i9_text for ref in
              ('M18','M19','M20','M21','M22','M23','E26')),
          'I9 future learning and sequential geometry closest work not source-cited')
    check(all(term in i9_text for term in
              ('θ<sub>AB</sub>','θ<sub>BA</sub>','H<sub>tr</sub>','当前能力相近',
               'C 已知','C 未知','重置 AdamW','0/1/5/10/20/40','Go / Merge / Stop')),
          'I9 must retain SGD boundary, future adaptation setup and falsifiable checks')
    check('id="i9-future-c-types"' in i9_text and
          all(k in i9_text for k in ('C₁ · 可组合的共享规则','C₂ · 必须放弃局部捷径','C₃ · 无关规则负对照',
                                    '交叉作用','108 个 C 训练分支')),
          'I9 must separate shared-rule, shortcut-conflict and unrelated C tasks with precommitted scale')
    check(all(k in experiments_html for k in ('C₁','C₂','C₃')) and
          'idea-i9-practice-switching.html#future-p0' in experiments_html,
          'I9 future learnability experiment entry must name C task families and link full design')
    check('idea-i9-practice-switching.html#future-question' in ideas_text and
          'idea-i9-practice-switching.html#future-p0' in experiments_html,
          'I9 A/B-to-C scientific extension not discoverable from overview and experiments')
    check('id="i9-future-learnability"' in experiments_html and
          'href="references.html#M18"' in (ROOT/'rsi/literature.html').read_text(encoding='utf-8'),
          'I9 third-task experiment and ICML 2026 nearest-work index missing')
    check('id="hypothesis-testing"' in learn_sci and
          'idea-i9-practice-switching.html#future-question' in learn_sci,
          'Motor-learning mechanism must link to I9 future learnability')
    # I11: Affective feedback is a persistent-RSI research proposal, not a one-shot EmotionPrompt result.
    i11=(ROOT/'rsi/idea-i11-emotional-rsi.html').read_text(encoding='utf-8')
    check(set(['E28']+[f'M{i}' for i in range(28,37)])<=refs,
          'I11 must retain original emotion and RSI learning-control source records')
    check(all(f'id="{x}"' in i11 for x in (
          'question','evidence','challenge','insight','design','related','p0','p1','p2','metrics','boundaries','gate')),
          'I11 five-stage scientific chain or P0/P1/P2 experiment section missing')
    check('id="i11-related-matrix"' in i11 and
          all(f'href="references.html#M{i}"' in i11 for i in range(28,37)) and
          'href="references.html#E28"' in i11,
          'I11 closest-work differences not source linked')
    check(all(term in i11 for term in (
          '学习控制','继续','核验','停止','写回','校准','LoRA','Skill',
          '净学习','固定重试','独立', 'GO', 'MERGE', 'STOP')),
          'I11 must test learning-control changes, true updates, and falsification')
    check('href="idea-i11-emotional-rsi.html"' in overview and
          'href="idea-i11-emotional-rsi.html"' in ideas_text and
          'id="idea-11"' in ideas_text,
          'I11 entry missing from homepage or research overview')
    check('id="affective-feedback"' in learn_sci and
          'href="references.html#E28"' in learn_sci and
          'href="idea-i11-emotional-rsi.html#p2"' in learn_sci,
          'I11 npj human evidence and RSI boundary absent from learning science')
    check('id="i11-emotional-rsi"' in experiments_html and
          'idea-i11-emotional-rsi.html#p0' in experiments_html,
          'I11 experiment execution entry missing')
    # I12 causal-prerequisite study and A/B/D merges must coexist without renumbering older ideas.
    i12=(ROOT/'rsi/idea-i12-prerequisite-bottleneck.html').read_text(encoding='utf-8')
    required_i12=('question','challenge','evidence','related','insight','definition','design',
                  'orthogonal','p0','p1','p2','metrics','gate')
    check(all(f'id="{sid}"' in i12 for sid in required_i12),
          'I12 causal scientific chain, counterfactual or experiments missing')
    check(all(f'href="references.html#{ref}"' in i12 for ref in
              ('E401','S401','S402','S403','S404','S405','S406','S47','M27','R04')),
          'I12 primary nearest-work sources not auditable')
    check(all(term in i12 for term in ('第二段','高频','非先修','真正依赖','GO','MERGE','STOP',
                                      'SkillDAG','SOAR','可学习性')),
          'I12 causal prerequisite against correlation/retrieval and stop gates missing')
    check('i12-experiment-protocol.json' in i12 and
          'idea-i12-prerequisite-bottleneck.html' in overview and
          'id="i12-prerequisite-unlocking"' in experiments_html,
          'I12 homepage, detail, downloadable protocol or execution index missing')
    protocol=json.loads((ROOT/'rsi/i12-experiment-protocol.json').read_text(encoding='utf-8'))
    check(protocol['idea_id']=='I12' and protocol['status']=='research_design_not_executed'
          and len(protocol['first_stage']['updates'])>=5 and
          all(k in protocol for k in ('main_estimand','data_splits','causal_controls','metrics')),
          'I12 experimental contract must be executable as a design, not reported as measured results')
    check('id="prerequisite-unlocking"' in learn_sci and
          'href="references.html#E401"' in learn_sci and
          'href="idea-i12-prerequisite-bottleneck.html"' in learn_sci,
          'NC 2026 prerequisite-inspired mechanism missing from learning science')
    check('id="idea-a-merged"' in i8_html and
          'id="idea-b-merged"' in i5_text and
          'id="idea-d-diagnostic"' in i2_text,
          'A/B/D research consolidation missing from I8/I5/I2')
    check(all(link in ideas_text for link in (
          'idea-i2.html#idea-d-diagnostic', 'idea-i5.html#idea-b-merged',
          'i8.html#idea-a-merged', 'idea-i12-prerequisite-bottleneck.html')),
          'The A/B/D merges and new I12 must each have a distinct overview entry')
    i10=(ROOT/'rsi/idea-i10-learning-novelty.html').read_text(encoding='utf-8')
    check({'E350','E351','E352'} <= refs and
          all(f'M{i}' in refs for i in range(50,66)),
          'MLC and I10 paper sources missing')
    check('href="idea-i10-learning-novelty.html"' in overview and
          'id="idea-10"' in ideas_text and
          all(x in overview for x in ('I10','I11','I12','I13')),
          'I10 not integrated with numbered RSI research pool')
    check(all(f'id="{x}"' in i10 for x in
          ('question','mosaic','case','mlc-nature2023','insight','design','experiment','go')),
          'I10 rule-learning mechanism or MLC section missing')
    check('reading-notes.html#deep-lake-baroni-mlc-nature2023' in i10 and
          'Table 1' in i10 and 'Table 2' in i10 and '20%' in i10,
          'MLC interpretation needs human/algorithm benchmark distinction')
    mlc=next((p for p in cards if p['id']=='lake-baroni-mlc-nature2023'),None)
    check(mlc is not None and len(mlc['deep_read']['sections'])==10 and
          len(mlc['deep_read']['metric_summary'])==5,
          'MLC Nature complete 10-section deep read missing')
    check('id="deep-lake-baroni-mlc-nature2023"' in notes_html and
          'id="systematic-generalization-mlc"' in learn_sci and
          'id="i10-rule-learning"' in experiments_html,
          'MLC deep-read or related RSI experimentation missing')
    # NHB 2026: paper reading, Figure 4b/c/e design references and larger-model evidence.
    nhb=next((p for p in cards if p['id']=='nhb2025-distribution-curriculum-pesnot-lerousseau'),None)
    check(nhb is not None and nhb.get('doi')=='10.1038/s41562-025-02359-3'
          and len(nhb['deep_read']['sections'])==10
          and len(nhb['deep_read']['metric_summary'])==5,
          'Missing original NHB paper, ten-section deep read or five-metric summary')
    check('E360' in refs and set(f'M{i}' for i in range(500,515))<=refs,
          'Larger-model source map and original NHB source missing')
    nhb_anchor='deep-nhb2025-distribution-curriculum-pesnot-lerousseau'
    survey=(ROOT/'rsi/curriculum-scale-evidence.html').read_text(encoding='utf-8')
    i9=(ROOT/'rsi/idea-i9-practice-switching.html').read_text(encoding='utf-8')
    check(f'id="{nhb_anchor}"' in notes_html and 'id="nhb2026-distribution-curriculum"' in i9
          and 'id="nhb2026-frequency-vs-rule"' in i10
          and 'id="nhb2026-repetition-diversity"' in learn_sci,
          'NHB research mechanism must appear in I9, I10, learning-science and deep read')
    check('id="nhb2026-strategy-retention"' in experiments_html and
          all(f'href="references.html#M{i}"' in survey for i in range(500,515)),
          'LLM/VLM survey or preregistered P0 protocol not source-linked')
    check('curriculum-scale-evidence.html' in overview and
          nhb_anchor in overview and
          'Figure4' in survey,
          'Larger-model study and NHB Figure4 must be findable from homepage')
    nhb_text=notes_html.split('id="'+nhb_anchor+'"',1)[1]
    check(all(z in nhb_text for z in ('31/50','17/50','0.969','Figure 4','C1','C2')),
          'Figure4 paper reading lacks effect strength, sample evidence or curriculum-label warning')
    check((ROOT/'figure-reference-assets/nhb-fig4-bce-inputs.json').is_file(),
          'NHB figure reproduction contract missing')
    rote = next((p for p in cards if p['id']=='rote-learning-iclr2026-wu'), None)
    check(rote is not None and rote.get('arxiv')=='2507.21914' and rote.get('conference_official_primary') is True,
          'ICLR 2026 Rote Learning reading note must link the official published version')
    check(rote['links']['html'].startswith('https://proceedings.iclr.cc/') and
          len(rote.get('deep_read',{}).get('sections',[]))>=12,
          'Rote Learning requires a full source-grounded deep read')
    rote_html=notes_html.split('id="deep-rote-learning-iclr2026-wu"',1)[-1]
    check(all(t in rote_html for t in ('36%', '16%', '95%', '76%', '14%', 'ICL')),
          'Rote Learning must present simple success, two-hop weakness and information-mismatch caution')
    check('id="rote-learning"' in learn_sci and
          all(f'href="references.html#{ref}"' in learn_sci for ref in ('M24','M25','M26')),
          'Rote Learning needs critical source notes and two-hop closest work')
    check('deep-rote-learning-iclr2026-wu' in overview and
          'id="rote-learning-iclr2026-wu"' in card_html,
          'Rote Learning must be reachable from homepage and compact card')
    mosaic = next((p for p in cards if p['id']=='mosaic-memory-2026-shilov'), None)
    check(mosaic is not None and mosaic.get('doi')=='10.1038/s41467-026-68603-0',
          'Mosaic Memory Nature Communications card DOI missing')
    check(len(mosaic['deep_read']['sections'])==10 and {'challenge','insight','design','result','next'}<=
          {s['stage'] for s in mosaic['deep_read']['sections']},
          'Mosaic Memory must preserve source-vs-RSI distinctions and 10-section deep read')
    check('id="mosaic-memory-2026-shilov"' in card_html and
          'id="deep-mosaic-memory-2026-shilov"' in notes_html,
          'Mosaic Memory reading card and full note not both rendered')
    check('id="mosaic-memory"' in learn_sci and 'href="references.html#M17"' in learn_sci,
          'Learning science needs the primary Mosaic Memory source citation')
    check('deep-mosaic-memory-2026-shilov' in overview,
          'New Nature Communications reading note must be discoverable from the homepage')
    onan = next((p for p in cards if p['id']=='onan-self-organized-interleaving-2024'), None)
    check(onan is not None and onan.get('doi')=='10.1038/s41539-024-00245-7'
          and onan['links']['html']=='https://www.nature.com/articles/s41539-024-00245-7',
          'Onan 2024 original npj publication not captured')
    check(len(onan.get('deep_read',{}).get('sections',[]))>=12 and
          len(onan['deep_read']['metric_summary'])==5 and
          {'challenge','insight','design','result','related','next'} <=
          {s['stage'] for s in onan['deep_read']['sections']},
          'Onan 2024 must have full evidence and distinct RQ1/RQ2/RQ3 coverage')
    check('id="onan-self-organized-interleaving-2024"' in card_html
          and 'id="deep-onan-self-organized-interleaving-2024"' in notes_html,
          'Onan 2024 quick card or full reading missing')
    onan_note = notes_html.split('id="deep-onan-self-organized-interleaving-2024"',1)[1].split('<section class="panel research-section" id="deep-',1)[0]
    check(all(s in onan_note for s in ('76%', '55%', '81%', '57%', 'p=0.222',
                                     'p=0.205', '6.56', '3.57', '35', '5–7')),
          'Onan 2024 numbers or null accuracy result missing from deep note')
    check('odds' in onan_note and '不显著' in onan_note
          and '联合干预' in onan_note and 'I9' in onan_note,
          'Onan 2024 must separate behavior change, correlational score and I9 proposal')
    check('E310' in refs
          and 'href="references.html#E310"' in overview
          and 'href="reading-notes.html#deep-onan-self-organized-interleaving-2024"' in overview,
          'Onan source and full read must be discoverable from homepage')
    hgm = next((p for p in cards if p['id']=='hgm-2510-21614'), None)
    check(hgm is not None and hgm['arxiv']=='2510.21614' and
          'ICLR 2026' in hgm['publication'], 'HGM original and venue missing')
    check(len(hgm['deep_read']['sections'])>=11 and
          {'challenge','insight','design','result','related','next'} <=
          {s['stage'] for s in hgm['deep_read']['sections']},
          'HGM must retain full C-I-D-R/Related Work source-grounded reading')
    check('id="hgm-2510-21614"' in card_html and
          'id="deep-hgm-2510-21614"' in notes_html and
          'id="deep-hgm-2510-21614--cmp-estimator"' in notes_html,
          'HGM reading card, full note or CMP formula missing')
    hgm_note = notes_html.split('id="deep-hgm-2510-21614"',1)[1].split('<section class="panel research-section" id="deep-',1)[0]
    check(all(x in hgm_note for x in ('0.778','0.626','56.7%','517','61.4%','47.8%','57.0%')),
          'HGM actual correlations, main metrics or filtered transfer missing')
    check('CMP_hat' in hgm_note and 'Oracle' in hgm_note and
          'CPU-hours' in hgm_note and 'I5' in hgm_note,
          'HGM theoretical vs empirical distinction or RSI boundaries missing')
    check('href="reading-notes.html#deep-hgm-2510-21614"' in overview and
          'href="references.html#S310"' in overview,
          'HGM must be discoverable on homepage with auditable source')
    soar = next((p for p in cards if p['id']=='soar-2601-18778'), None)
    check(soar is not None and soar.get('arxiv')=='2601.18778' and
          'ICML 2026' in soar['publication'], 'SOAR original paper and venue metadata missing')
    check(len(soar['deep_read']['sections'])==14 and
          {'challenge','insight','design','result','next'} <=
          {s['stage'] for s in soar['deep_read']['sections']},
          'SOAR full reading needs the original argument chain and appendices')
    check('id="soar-2601-18778"' in card_html and
          'id="deep-soar-2601-18778"' in notes_html and
          'id="deep-soar-2601-18778--intrinsic"' in notes_html,
          'SOAR reading card, deep read or exact intrinsic formula section missing')
    check('1−sbar_i' in notes_html and '34.91' in notes_html and '10.82' in notes_html,
          'SOAR actual intrinsic reward and diversity collapse evidence must remain')
    check('82' in notes_html and '144' in notes_html and 'fail@128' in notes_html,
          'SOAR incorrect-answer sample-size boundary or hard filtering missing')
    check('id="soar-grounded"' in learn_sci and
          'deep-soar-2601-18778' in learn_sci and
          'deep-soar-2601-18778' in overview,
          'SOAR must be reachable from learning science and home')
    for slug in ('idea-i2','idea-i6-failure-value','i8','idea-i9-practice-switching'):
        page_text=(ROOT/'rsi'/f'{slug}.html').read_text(encoding='utf-8')
        check('reading-notes.html#deep-soar-2601-18778' in page_text,
              'SOAR evidence and related-idea boundaries must crosslink: '+slug)
    check(any(t['paper_id']=='soar-2601-18778' and len(t['works'])==4
              for t in related_data['targets']),
          'SOAR must have a source-verified closest-work comparison')
    check('历史版本' in historical_i6 and f'href="idea-i6-failure-value.html"' in historical_i6,
          'Historical bottleneck draft must have a clear link to the current I6')
    check(all(k in historical_i6 for k in ('知识不足','搜索不足','选择不足','吸收不足','I2 · 因材施教','From Rollouts to Recipes')),
          'Preserved bottleneck probes or citations missing')
    check(all(f'id="{x}"' in historical_i6 for x in ('archive','question','challenge','insight','design','orthogonality','related','experiments','safety')),
          'Historical bottleneck sections missing')
    admission=(ROOT/'rsi/learning-admission.html').read_text(encoding='utf-8')
    check(all(f'id="{part}"' in admission for part in
              ('question','phenomena','work','challenge','insight','design','p0','p1','p2','boundaries')),
          'Learning admission must retain scientific story, evidence layers and decisive tests')
    check(all(word in admission for word in
              ('EAFT','RieSelect','CoPE','RSIFlow','MetaSkill-Evolve','Skill∞',
               'Core-only','System-with-Experts','Meta-Admission Skill','重访','旧规则已失效',
               'Unsafe Admission FNR','Safe Update FRR','独立安全验收')),
          'Admission page lacks fixed-learning versus RSI boundary or long-term evidence')
    check(all(f'href="references.html#{key}"' in admission for key in
              ('M320','M321','M322','M22','M450','M454','S320',
               'S450','S451','S452','S453','S454')),
          'Admission literature has uncited or missing first-party registry entries')
    check('href="learning-admission.html"' in overview and
          'href="learning-admission.html"' in ideas_text,
          'I13 Learning Admission is absent from the research board')
    check('learning-admission.html' in nav_text and 'I13 · 安全更新接纳' in nav_text,
          'Formal I13 title or second-level navigation missing')
    check('I13 · 安全更新接纳' in admission and 'I13 · RSI 安全更新接纳' in overview
          and 'I13 · RSI 安全更新接纳' in ideas_text,
          'I13 homepage, idea board or canonical detail title not promoted')
    check('RSI RESEARCH CANDIDATE · UNNUMBERED' not in admission
          and '独立候选（未编号）' not in overview
          and '新增独立研究候选（未编号）' not in ideas_text,
          'Old unnumbered candidate labels remain after I13 promotion')
    check(all(f'id="{part}"' in admission for part in ('plasticity','nonlocal-effects','contract'))
          and all(t in admission for t in ('M22','M450','p0','p1','p2','硬约束','误拒','后代',
                                         '拒绝本轮候选','实际部署','SafeEvolve','回滚')),
          'I13 safety-first contract or original Learning Admission research boundaries lost')
    check('尚无真实实验或跨代更新结果' in admission,
          'Formal I13 status must not imply that experiments have been completed')
    check('id="idea-3"' in ideas_text and
          '与 I13 的事前接纳分开' in ideas_text.split('id="idea-3"',1)[1].split('</section>',1)[0],
          'I3 post-conflict repair was not separated from pre-update admission')
    ref_ids=set(parsed[ROOT/'rsi/references.html'].ids)
    check(refs<=ref_ids,'Some source cards have no anchors')
    agent_nav=(ROOT/'data.js').read_text(encoding='utf-8')
    check('"rsi/index.html"' not in agent_nav,'Agent navigation still includes RSI pages')
    nav=nav_text
    for slug in set(PAGES)-{'teaching','idea-i6'}:
        check(f'"{slug}.html"' in nav,f'Missing active RSI navigation: {slug}')
    for slug in ('teaching','idea-i6'):
        check(f'"{slug}.html"' not in nav,f'Archived RSI page must not duplicate a numbered nav item: {slug}')
    records=json.loads((ROOT/'rsi/search-index.json').read_text(encoding='utf-8'))
    for target in related_data['targets']:
        for work in target['works']:
            url=f'reading-notes.html#related-{target["paper_id"]}--{work["id"]}'
            check(sum(r['url']==url for r in records)==1,
                  'Related-work source missing or repeated in global search: '+work['id'])
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
        check((public/'rsi/related-work.json').read_bytes()==(ROOT/'rsi/related-work.json').read_bytes(),
              'Published related-work source differs from reviewed registry')
        check(not list(public.rglob('*.py')),'Python leaked into public output')
        check((public/'rsi/sources.json').read_bytes()==(ROOT/'rsi/sources.json').read_bytes(),'Exported source manifest differs')
    print(f'PASS: {len(PAGES)} RSI pages, {len(refs)} sources, {len(records)} search records, local links/anchors, nav and public export.')

if __name__=='__main__': main()
