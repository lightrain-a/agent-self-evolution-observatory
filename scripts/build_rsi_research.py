#!/usr/bin/env python3
"""Build the independently scoped RSI research section from reviewed source notes."""
from __future__ import annotations
import csv
import html
import json
import re
import runpy
from collections import Counter
from pathlib import Path
from rsi_framework import (FUNCTIONS, IDEAS, BY_ID, FUNCTION_SLUGS, function_badges, source_assignment,
                           enrich_registries, framework_pages, apply_page_metadata, organize_ideas)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'rsi'
DATE = '2026-10-29'
BASE_ORDER = ['index','research-map','timeline','literature','reading-cards','reading-notes','cross-domain','theory-notes','learning-science','generalization-learnability','curriculum-scale-evidence','ideas','idea-prioritization','idea-i2','idea-i5','idea-i6-failure-value','idea-i7-learning-order','i8','idea-i9-practice-switching','idea-i10-learning-novelty','idea-i11-emotional-rsi','idea-i12-prerequisite-bottleneck','learning-admission','learning-rule-evolution','memory-research-map','learning-signal-bottlenecks','experience-consolidation','teaching','idea-i6','experiments']
CHAPTER_ORDER = ['index','research-map','foundations','experience','signals','capabilities','regulation','evidence','agenda']
NAV_ARCHIVED_PAGES = {'teaching':'idea-i5.html','idea-i6':'ideas.html'}

def page_label(p):
    labels={'index':'第1章 · 研究总览','research-map':'四功能研究地图','foundations':'第2章 · 范围与框架',
            'timeline':'研究时间轴 · 会议 DDL','ideas':'I1–I14 · 研究方向总览',
            'idea-prioritization':'方案优先级与决定性实验','evidence':'第7章 · 证据与评价',
            'agenda':'第8章 · 开放问题与研究议程','experiments':'实验执行方案',
            'learning-admission':'I13 · 安全更新接纳','learning-rule-evolution':'I14 · 学习规则自进化'}
    for iid,idea in IDEAS.items():
        if idea['href']==p['slug']+'.html' and p['slug'] not in labels:
            return iid+' · '+idea['title']
    return labels.get(p['slug'],p['title'])

def build_navigation(pages):
    by_slug={p['slug']:p for p in pages}
    def entry(slug):
        p=by_slug[slug]
        return [slug+'.html',{'zh':page_label(p),'en':p.get('en',p['title'])}]
    groups=[{'id':'overview','title':{'zh':'总览与综述框架','en':'Overview & Review'},'open':False,
             'pages':[entry(s) for s in ('index','research-map','foundations','timeline','ideas','idea-prioritization')]}]
    extras={'experience':[],'signal':['learning-signal-bottlenecks'],
            'capability':['memory-research-map','experience-consolidation'],'regulation':[]}
    for f in FUNCTIONS:
        links=[entry(FUNCTION_SLUGS[f['id']])]
        for iid,idea in IDEAS.items():
            if idea['primary']==f['id']:
                links.append([idea['href'],{'zh':iid+' · '+idea['title'],'en':iid+' · '+idea.get('en',idea['title'])}])
        links += [entry(s) for s in extras[f['id']]]
        groups.append({'id':f['id'],'title':{'zh':f'第{f["chapter"]}章 · '+f['title'],'en':f.get('en',f['title'])},'open':False,'pages':links})
    groups.extend([
        {'id':'evidence','title':{'zh':'证据与研究议程','en':'Evidence & Agenda'},'open':False,
         'pages':[entry(s) for s in ('evidence','generalization-learnability','curriculum-scale-evidence','experiments','agenda')]},
        {'id':'literature','title':{'zh':'文献与机制资料','en':'Literature & Mechanisms'},'open':False,
         'pages':[entry(s) for s in ('literature','reading-cards','reading-notes','cross-domain','theory-notes','learning-science','references')]}
    ])
    covered=[href[:-5] for g in groups for href,_ in g['pages'] if '#' not in href]
    assert len(covered)==len(set(covered)), 'Duplicate navigation page'
    assert set(covered)|set(NAV_ARCHIVED_PAGES)==set(by_slug), ('Uncovered navigation pages',set(by_slug)-set(covered)-set(NAV_ARCHIVED_PAGES))
    return groups

def render_navigation(groups: list[dict], current: str) -> str:
    blocks = []
    selected = NAV_ARCHIVED_PAGES.get(current, current + '.html')
    for group in groups:
        has_active = any(href == selected for href, _ in group['pages'])
        links = ''.join(
            '<a class="nav-level2' + (' active' if href == selected else '') +
            '" href="' + html.escape(href, quote=True) + '"' +
            (' aria-current="page"' if href == selected else '') + '>' +
            html.escape(label['zh']) + '</a>'
            for href, label in group['pages']
        )
        blocks.append(
            '<details class="nav-group' + (' active-group' if has_active else '') +
            '" data-nav-group="' + html.escape(group['id']) + '"' +
            (' open' if has_active else '') +
            '><summary class="nav-level1"><span>' + html.escape(group['title']['zh']) +
            '</span><span class="nav-chevron" aria-hidden="true">⌄</span></summary>' +
            '<div class="nav-children">' + links + '</div></details>'
        )
    return ''.join(blocks)



def plain(text: str) -> str:
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', text))).strip()


def main() -> None:
    (OUT / "timeline-reference.css").write_text(
        (ROOT / "research-timeline.css").read_text(encoding="utf-8"), encoding="utf-8")
    with (OUT / 'sources.tsv').open(encoding='utf-8', newline='') as stream:
        sources = list(csv.DictReader(stream, delimiter='\t'))
    refmap = {r['id']: r for r in sources}
    assert len(refmap) == len(sources)
    assert all(r['url'].startswith('https://') for r in sources)
    reading_papers = enrich_registries(sources)
    pages = [runpy.run_path(str(ROOT / 'scripts' / 'rsi_pages' / (slug + '.py')))['PAGE'] for slug in BASE_ORDER]
    pages.extend(framework_pages(sources))
    organize_ideas(next(p for p in pages if p['slug']=='ideas'))
    source_sections = [('protocol', '核验口径与检索范围', '''<p>本专题的基础综述始于 2026-10-21；I1–I5 新增最近邻于 2026-10-27 增量核验。定向覆盖 RSI、学习型改进器、课程/元学习、学习科学及实验资源。用论文标题、方法词与引用链交叉检索，优先 arXiv、会议页面、作者机构和官方仓库。</p><p><b>阅读深度不同：</b>“正文方法”表示核对了方法/实验设置，不等于逐条复现全部结果；“摘要”只支持摘要范围的陈述；“官方资源”只确认资产与文档存在。代码入口存在不等于依赖安装、运行、原表重现成功。</p><p><b>原始材料与本次研究：</b>用户分享的推文用于确定入口和问题，不把推文统计或数字自动当作原论文结论。新提案、框架与优先级属于本专题分析，均非文献已经证明的结果。</p><p><b>搜索主题：</b>recursive self-improvement / harness optimization / meta-learning / automated curriculum / learning progress / learner modeling / assistance dilemma / fading / retrieval practice / productive failure / interference replay / skill withdrawal / learning response / selective rehearsal / active failure probing / partner selection / co-distillation。</p><div class="note">这是针对选题的证据地图，不是穷尽全部文献的系统综述。未能核对的作者、发表状态、代码可运行性不补写；预印本标注月份。链接会随论文修订与仓库更新变化，实验须另锁 commit / revision。</div><div class="links"><a class="link-btn" href="sources.json" download>下载来源 JSON</a><a class="link-btn" href="sources.tsv" download>下载来源 TSV</a><a class="link-btn" href="research-notes.md" download>下载整篇研究笔记</a></div>''')]
    filter_options = ''.join(f'<option value="{f["id"]}">{html.escape(f["title"])}</option>' for f in FUNCTIONS)
    source_sections[0] = (source_sections[0][0], source_sections[0][1],
        '<span id="group-rsi"></span><span id="group-methods"></span><span id="group-education"></span><span id="group-assets"></span>'
        + '<div class="reference-tools"><label for="reference-query">搜索来源</label><input id="reference-query" type="search" placeholder="标题、机制或来源编号…">'
        + f'<label for="reference-function">主要功能</label><select id="reference-function"><option value="all">全部来源</option>{filter_options}<option value="support">综述、评估与资源</option></select><span id="reference-count" aria-live="polite"></span></div>'
        + '<p>研究文献按主要科学贡献归入四项学习功能；教育学、认知科学和神经科学保留为来源领域。综述、独立评估与实验资源作为支撑材料列出。</p>'
        + '<details class="framework-fold"><summary>检索范围、阅读深度与来源记录</summary>'+source_sections[0][2]+'</details>')
    for key, label in [(f['id'], f['title']) for f in FUNCTIONS] + [(None,'综述、独立评估与实验资源')]:
        records=[s for s in sources if source_assignment(s)['primary']==key]
        cards=[]
        for r in records:
            info=source_assignment(r)
            code=f'<a class="link-btn repo" href="{html.escape(r["code"],quote=True)}" target="_blank" rel="noopener noreferrer">代码 / 官方资源</a>' if r.get('code') else ''
            badges=function_badges(info['primary'],info['related'])
            cards.append(f'''<article class="source-card" id="{r['id']}" data-primary-function="{key or 'support'}" data-related-functions="{'|'.join(info['related'])}"><div class="source-meta"><span class="ref-id">{r['id']}</span><span>{html.escape(r['date'])}</span><span class="evidence">{html.escape(r['level'])}</span><span>{html.escape(r['group'])}</span></div><h3><a href="{html.escape(r['url'],quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(r['title'])}</a></h3>{badges}<p>{html.escape(r['note'])}</p><p class="classification-reason">{html.escape(info.get('reason',''))}</p><div class="links"><a class="link-btn" href="{html.escape(r['url'],quote=True)}" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a>{code}</div></article>''')
        source_sections.append(('function-'+(key or 'support'), f'{label} · {len(cards)} 项',''.join(cards)))
    pages.append({'slug':'references','title':'来源与文献分类','en':'References by Learning Function','lead':f'{len(sources)} 项来源按四项学习功能组织，保留来源领域、阅读深度与原始链接。','sections':source_sections})
    apply_page_metadata(pages)
    order=CHAPTER_ORDER+[s for s in BASE_ORDER if s not in CHAPTER_ORDER]+['references']
    page_map={p['slug']:p for p in pages}
    assert set(order)==set(page_map)
    pages=[page_map[s] for s in order]
    # A self-contained RSI navigation module. Agent's data.js is never loaded.
    site_nav = build_navigation(pages)
    (OUT / 'site-nav.js').write_text('window.NAV_GROUPS = ' + json.dumps(site_nav, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
    used = set()
    def expand(text: str) -> str:
        text = text.replace('[[SOURCE_COUNT]]', str(len(sources)))
        def repl(m: re.Match) -> str:
            key = m.group(1)
            if key not in refmap:
                raise ValueError('Unknown source: ' + key)
            used.add(key)
            return f'<a class="cite" href="references.html#{key}" title="{html.escape(refmap[key]["title"], quote=True)}">[{key}]</a>'
        return re.sub(r'\[\[([A-Z]\d+)\]\]', repl, text)
    search = []
    notes = [f'# RSI × 自主学习研究\n\n核验日期：{DATE}\n\n本文件包含证据综述与待验证提案，不包含本项目实验结果。\n']
    for idx, p in enumerate(pages):
        slug = p['slug']
        page_date = p.get('updated', DATE)
        body_parts = []
        toc = []
        for sid, title, body in p['sections']:
            body = expand(body)
            body_parts.append(f'<section class="panel research-section" id="{sid}"><h2>{html.escape(title)}</h2><div class="section-body">{body}</div></section>')
            toc.append(f'<a href="#{sid}">{html.escape(title)}</a>')
            if slug != 'references':
                search.append({'title':p['title'] + ' · ' + title, 'url':slug + '.html#' + sid, 'text':plain(body)+' '+BY_ID.get(p.get('primary_function'),{}).get('title',''), 'primary_function':p.get('primary_function')})
            notes.append(f'## {p["title"]} / {title}\n\n{body}\n')
        for record in p.get('search_records', []):
            if not record.get('primary_function'):
                for paper in reading_papers:
                    if any(record['url'].startswith(prefix+paper['id']) for prefix in
                           ('reading-cards.html#','reading-notes.html#deep-','reading-notes.html#related-')):
                        record['primary_function']=paper['primary_function']
                        record['text'] += ' '+BY_ID[paper['primary_function']]['title']
                        break
            search.append({**record, 'primary_function':record.get('primary_function',p.get('primary_function'))})
        for r in sources if slug == 'references' else []:
            search.append({'title':r['id']+' · '+r['title'], 'url':'references.html#'+r['id'], 'text':r['date']+' '+r['group']+' '+r['note']+' '+BY_ID.get(r.get('primary_function'),{}).get('title',''), 'primary_function':r.get('primary_function')})
        nav = render_navigation(site_nav, slug)
        previous = f'<a href="{pages[idx-1]["slug"]}.html">← {page_label(pages[idx-1])}</a>' if idx else '<a href="/">← Agent 研究站</a>'
        following = f'<a href="{pages[idx+1]["slug"]}.html">{page_label(pages[idx+1])} →</a>' if idx < len(pages)-1 else '<a href="ideas.html">回到候选 Idea →</a>'
        title = html.escape(p['title'])
        category_badges = function_badges(p.get('primary_function'), p.get('related_functions', []))
        eyebrow = f'CHAPTER {p["chapter"]:02d} · RSI LEARNING MECHANISMS' if p.get('chapter') else 'RSI · LEARNING MECHANISMS'
        page_function = p.get('primary_function','')
        extra_styles = ''.join(f'<link rel="stylesheet" href="{html.escape(asset, quote=True)}">' for asset in p.get('styles', []))
        extra_scripts = ''.join(f'<script src="{html.escape(asset, quote=True)}"></script>' for asset in p.get('scripts', []))
        assert all(re.fullmatch(r'[a-z0-9-]+\.css', asset) for asset in p.get('styles', []))
        assert all(re.fullmatch(r'[a-z0-9-]+\.js', asset) for asset in p.get('scripts', []))
        header_html = p.get('header_html') or f'''<header class="research-hero"><div class="eyebrow">{eyebrow}</div><p class="research-en">{html.escape(p['en'])}</p><h1>{title}</h1>{category_badges}<p class="lead">{html.escape(p['lead'])}</p><div class="hero-meta"><span>更新 {page_date}</span><span>四功能统一分类</span><a href="research-map.html">研究地图 ↗</a></div></header>'''
        doc = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{html.escape(p['lead'], quote=True)}"><meta name="theme-color" content="#101827"><title>{title} | RSI Self-Improvement Observatory</title><link rel="canonical" href="https://agent-evolution.lightrain.asia/rsi/{slug}.html"><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="site-base.css"><link rel="stylesheet" href="research.css"><link rel="stylesheet" href="site-switch.css"><link rel="stylesheet" href="framework.css">{extra_styles}<link rel="stylesheet" href="compact.css"></head>
<body data-rsi-page="{slug}" data-primary-function="{page_function}"><a class="skip-link" href="#research-main">跳转到正文</a><div class="layout"><aside class="sidebar" id="sidebar"><button class="sidebar-close" id="sidebar-close" aria-label="关闭目录">×</button><nav class="site-switcher" aria-label="研究网站切换"><span class="site-switcher__caption">研究站点 · SITES</span><div class="site-switcher__tabs"><a class="site-switcher__tab" href="/" title="切换到 Agent 自进化研究站">Agent <span aria-hidden="true">↗</span></a><a class="site-switcher__tab active" href="/rsi/" aria-current="true" title="当前：RSI 自主学习研究站">RSI</a></div></nav><a class="brand" href="index.html"><span class="logo">RSI</span><span><strong>RSI × 自主学习</strong><span>Recursive Self-Improvement</span></span></a><nav class="nav" id="research-nav" aria-label="RSI 专题目录">{nav}</nav><div class="page-toc"><div class="toc-title">本页目录</div><nav class="toc-links">{''.join(toc)}</nav></div><div class="sidebar-note">证据综述与待验证假设分开。<br>核验日期：{DATE}<br>本专题详文为中文，保留英文术语与原始文献标题。</div></aside><button class="sidebar-overlay" id="sidebar-overlay" aria-label="关闭目录遮罩" hidden></button><main class="main" id="research-main"><div class="topbar"><button class="mobile-toggle" id="menu-toggle" aria-label="打开目录" aria-controls="sidebar" aria-expanded="false">☰</button><div class="search"><label class="sr-only" for="research-search">搜索本专题的章节与来源</label><input id="research-search" type="search" placeholder="搜索功能、研究问题、I 编号或论文…" autocomplete="off"></div><button class="language-toggle" id="nav-language" title="只切换目录语言；研究详文为中文">EN navigation</button></div><div class="content"><section class="search-results panel" id="search-results" aria-live="polite" hidden></section>{header_html}{''.join(body_parts)}<nav class="page-pagination" aria-label="专题翻页">{previous}{following}</nav></div><footer class="footer">RSI × 自主学习研究 · {page_date} · <a href="references.html">来源与核验口径</a> · <a href="research-notes.md" download>研究笔记</a><br>文献结论、研究推断和实验计划分别标注；未运行实验，不展示模拟结果。</footer></main></div><script src="site-nav.js"></script><script src="research.js"></script><script src="framework.js"></script>{extra_scripts}<script src="page-router.js"></script></body></html>'''
        (OUT / (slug + '.html')).write_text(doc, encoding='utf-8')
    # Save public, portable research records; authoring Python remains outside public output.
    metadata = {'taxonomy_version':'learning-functions-2026-10-29','review_date':DATE,'scope':'RSI、学习型改进器、相邻领域与学习科学；定向证据地图，非穷尽性综述。','sources':sources}
    (OUT / 'sources.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (OUT / 'search-index.json').write_text(json.dumps(search, ensure_ascii=False)+'\n', encoding='utf-8')
    notes.append('\n## 原始来源\n\n' + '\n'.join(f'- [{r["id"]}] {r["title"]} · {r["date"]}\n  {r["url"]}' for r in sources))
    (OUT / 'research-notes.md').write_text('\n'.join(line.rstrip() for line in '\n'.join(notes).splitlines()) + '\n', encoding='utf-8')
    fieldnames = list(sources[0])
    with (OUT/'sources.tsv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fieldnames,delimiter='\t')
        writer.writeheader()
        writer.writerows({k:('|'.join(v) if isinstance(v,list) else v) for k,v in r.items()} for r in sources)
    print(f'Built {len(pages)} pages; {len(sources)} sources; {len(used)} inline-cited sources; {len(search)} search records.')
    unused = set(refmap)-used
    if unused:
        print('Background / resource records not inline-cited:', ', '.join(sorted(unused)))

if __name__ == '__main__':
    main()
