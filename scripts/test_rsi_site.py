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
PAGES = ['index','timeline','literature','reading-cards','reading-notes','cross-domain','learning-science','ideas','idea-i2','idea-i5','idea-i6-failure-value','idea-i7-learning-order','i8','idea-i9-practice-switching','teaching','idea-i6','experiments','references']

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
    check(len(refs)>=109 and {'S100','S101','S102','S103','S104','M100'}<=refs and {'S200', 'B200', 'S202', 'S201', 'S204', 'S203', 'S205'}<=refs and all(f'S{i}' in refs for i in range(26,50)) and all(f'E{i}' in refs for i in range(11,19)) and {'M10','M11','M12','M13','S90','E19','E20','E21','E22','E23','E24','E25','M15','M16'}<=refs and all(f'E{i}' in refs for i in range(90,98)),'Expected I1–I9 sources, including I9 primary education and LLM curricula')
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
        'methods':['cross-domain.html','learning-science.html'],
        'research':['ideas.html','ideas.html#idea-1','idea-i2.html','ideas.html#idea-3','ideas.html#idea-4',
                    'idea-i5.html','idea-i6-failure-value.html','idea-i7-learning-order.html',
                    'i8.html','idea-i9-practice-switching.html','experiments.html'],
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
    check(numbered==[f'I{i}' for i in range(1,10)],'Research ideas must appear exactly once, ordered I1–I9')
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
    check('E26' in refs and 'SOAR' in (ROOT/'rsi/literature.html').read_text(encoding='utf-8')
          and '50%' in (ROOT/'rsi/literature.html').read_text(encoding='utf-8'),
          'npj 2026 must be linked to SOAR and the difficulty proxy in closest-work discussion')
    check('reading-notes.html#deep-hypothesis-testing-2026-ding' in (ROOT/'rsi/learning-science.html').read_text(encoding='utf-8'),
          'Mechanism transfer not linked from learning-science page')
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
        or (p.get('doi') and p.get('official_url') == p['links']['html']
            and p['official_url'].startswith('https://'))
        for p in cards
    ),'Paper lacks a verified arXiv or publisher original link')
    ideas=parsed[ROOT/'rsi/ideas.html']
    check(all(f'idea-{i}' in ideas.ids for i in range(1,10)),'I1–I9 anchors missing from research board')
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
    for idea_number in range(1, 10):
        section = ideas_text.split(f'id="idea-{idea_number}"', 1)[1].split('</section>', 1)[0]
        locations = [section.find(heading) for heading in ordered_headings]
        check(all(pos >= 0 for pos in locations) and locations == sorted(locations),
              f'I{idea_number}: Challenge -> Related Work -> Insight -> Design -> Experiment order drift')
        check(section.count('class="idea-step"') == 5,
              f'I{idea_number}: expected exactly five argument blocks')
        check(section.count('class="flow"') >= 1, f'I{idea_number}: four-step method flow missing')
    idea_positions = [ideas_text.index(f'id="idea-{i}"') for i in range(1,10)]
    check(idea_positions == sorted(idea_positions),'I1–I9 sections are out of order')
    check(ideas_text.index('id="orthogonal"') > idea_positions[-1],
          'Independent I6-I9 comparison must follow their complete research narratives')
    for i, detail in ((6,'idea-i6-failure-value.html'),(7,'idea-i7-learning-order.html'),(8,'i8.html'),(9,'idea-i9-practice-switching.html')):
        section = ideas_text.split(f'id="idea-{i}"', 1)[1].split('</section>', 1)[0]
        check(f'href="{detail}"' in section, f'I{i}: full scientific detail page must remain linked')
        check('正交边界' in section,'I6-I9 separation lost in I'+str(i))
    check('十模型互教' in ideas_text and '不需要外部教师告诉标准答案' in ideas_text,'I5/I4 hypothesis drift')
    i2_text=(ROOT/'rsi/idea-i2.html').read_text(encoding='utf-8')
    check('href="idea-i2.html"' in ideas_text and 'href="idea-i2.html"' in (ROOT/'rsi/index.html').read_text(encoding='utf-8'),
          'I2 detailed plan must be reachable from both home and ideas')
    check(all(f'id="{sid}"' in i2_text for sid in ('question','evidence','challenge','insight','related','design','objective','experiments','boundaries')),
          'I2 teaching co-evolution evidence and experimental sections missing')
    check(all(f'href="references.html#{ref}"' in i2_text for ref in ('S100','S101','S102','S103','S104','M100','S17','S19','S33')),
          'I2 verified nearest-work references missing')
    check(all(term in i2_text for term in ('冻结学生','TeachingGain','固定教师','独立学习增益','教学 LoRA','任务 Skill','I5','I6','I7','I8')),
          'I2 must separate pedagogical gains, student learning, carriers and other ideas')
    check('id="i2-coevolution"' in (ROOT/'rsi/experiments.html').read_text(encoding='utf-8'),
          'I2 execution entry missing')
    i5_text=(ROOT/'rsi/idea-i5.html').read_text(encoding='utf-8')
    check('href="idea-i5.html"' in ideas_text and 'href="idea-i5.html"' in (ROOT/'rsi/index.html').read_text(encoding='utf-8'),'I5 page not linked from home/ideas')
    check(all(k in i5_text for k in ('十个模型','换舞伴','Bridge ties bind collective memories','PopuLoRA','OPCoD','HACE','I7','未见任务')),'I5 evidence, orthogonal labels or controls missing')
    check(all(f'id="{x}"' in i5_text for x in ('scene','papers','collisions','challenge','insight','design','experiments','teaching-feedback','summary')),'I5 unified sections missing')
    check('href="teaching.html"' in i5_text and '十模型动态互教' in i5_text,
          'Historical teaching-feedback branch must remain accessible under the sole I5 entry')
    i8_html=(ROOT/'rsi/i8.html').read_text(encoding='utf-8')
    for label in ['Observable Phenomenon','Why','Challenge','Insight','Design','决定性实验','Related Work','预注册判断']:
        check(label in i8_html,'I8 research mechanism structure missing: '+label)
    for ref in ['E12','E13','E14','E15','E18','S17','S40','S41','S42','S43','S44','M10','M11','M13']:
        check(f'href="references.html#{ref}"' in i8_html,'I8 reference missing: '+ref)
    check('语义预测误差' in i8_html and '误导性反馈' in i8_html and '可信反馈门槛' in i8_html,'I8 must retain Pine 2018 prediction-error and misinformation boundary')
    check('href="references.html#E18"' in (ROOT/'rsi/learning-science.html').read_text(encoding='utf-8'),'Pine 2018 must be cross-linked from learning science')
    check('id="i8-related-matrix"' in i8_html, 'I8 closest-work comparison table missing')
    for axis in ['研究对象与条件','用什么信号判断','操作与实际评价','与 I8 相同 / 不同之处']:
        check(axis in i8_html,'I8 related-work scientific comparison axis missing: '+axis)
    for close in ['Self-Error-Instruct','LESS','DATAPROPHET','SOAR','RULE-EDIT','Learning Dynamics','LENS / ACE','I8（待验证）']:
        check(close in i8_html,'I8 nearest work missing from comparison matrix: '+close)
    for boundary in ['Same','Different','Why','Evidence','没有结果']:
        check(boundary in i8_html,'I8 missing honest closest-work boundary: '+boundary)
    check('href="i8.html"' in ideas_text,'I8 missing from idea board')
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
    learn_sci=(ROOT/'rsi/learning-science.html').read_text(encoding='utf-8')
    check('id="learning-progress"' in learn_sci and 'href="references.html#E19"' in learn_sci,
          'Learning science must include Ten et al. 2021 with primary citation')
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
    check(all(term in i9_text for term in
              ('Blocked','Interleaved','Random Interleaved','规则形成','规则辨别','LoRA','I7','P0','P1','P2')),
          'I9 nearest-work, state mechanism or controlled experiments missing')
    check('id="interleaving"' in learn_sci and 'href="references.html#E20"' in learn_sci,
          'Learning science must cross-link I9 primary experiment')
    experiments_html=(ROOT/'rsi/experiments.html').read_text(encoding='utf-8')
    check('id="i9-practice"' in experiments_html and 'idea-i9-practice-switching.html#experiments' in experiments_html,
          'I9 independent experimental contract missing')
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
    check('历史版本' in historical_i6 and f'href="idea-i6-failure-value.html"' in historical_i6,
          'Historical bottleneck draft must have a clear link to the current I6')
    check(all(k in historical_i6 for k in ('知识不足','搜索不足','选择不足','吸收不足','I2 · 因材施教','From Rollouts to Recipes')),
          'Preserved bottleneck probes or citations missing')
    check(all(f'id="{x}"' in historical_i6 for x in ('archive','question','challenge','insight','design','orthogonality','related','experiments','safety')),
          'Historical bottleneck sections missing')
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
