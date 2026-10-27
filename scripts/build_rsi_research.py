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

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'rsi'
DATE = '2026-10-27'
ORDER = ['index', 'timeline', 'literature', 'reading-cards', 'reading-notes', 'cross-domain', 'learning-science', 'ideas', 'idea-i5', 'idea-i6-failure-value', 'idea-i7-learning-order', 'i8', 'teaching', 'idea-i6', 'experiments']
LABELS = ['专题总览', '研究时间轴 · 会议 DDL', '文献与竞争边界', '论文精读卡片', '论文完整精读', '相邻领域方法', '教育学与学习科学', '研究方向 · I1–I8', 'I5 · 十模型互教与动态换伴', 'I6 · 失败过程的学习价值', 'I7 · 先试还是先学', 'I8 · 错误可学习性与迁移', '教学反馈诊断 · I5 支线', '归档 · 跨轮瓶颈切换', '实验执行方案', '来源与核验记录']
EN_LABELS = ['Overview', 'Research Timeline & DDLs', 'Literature', 'Paper Reading Cards', 'Full Paper Deep Reads', 'Cross-domain Methods', 'Learning Science', 'I1–I8 · Research Ideas', 'I5 · Rotating Learning Partners', 'I6 · Learning Value of Failure Trajectories', 'I7 · Learning Order', 'I8 · Error Learnability & Transfer', 'I5 · Teaching Feedback Branch', 'Archive · Bottleneck Switching', 'Experiments', 'Sources']
# A single, ordered definition of RSI primary and secondary navigation.
# The same hierarchy is rendered server-side (without JS) and client-side.
NAV_SECTIONS = [
    {'id':'overview', 'title':{'zh':'专题入口', 'en':'Start Here'}, 'slugs':['index', 'timeline']},
    {'id':'literature', 'title':{'zh':'文献与论文精读', 'en':'Literature & Reading'}, 'slugs':['literature', 'reading-cards', 'reading-notes', 'references']},
    {'id':'methods', 'title':{'zh':'方法与学习科学', 'en':'Methods & Learning Science'}, 'slugs':['cross-domain', 'learning-science']},
    {'id':'research', 'title':{'zh':'研究方向与实验', 'en':'Ideas & Experiments'}, 'slugs':['ideas', 'idea-i5', 'idea-i6-failure-value', 'idea-i7-learning-order', 'i8', 'teaching', 'idea-i6', 'experiments']},
]


def build_navigation(pages: list[dict]) -> list[dict]:
    labels = {p['slug']: {'zh': LABELS[i], 'en': EN_LABELS[i]} for i, p in enumerate(pages)}
    flattened = [slug for section in NAV_SECTIONS for slug in section['slugs']]
    if len(flattened) != len(set(flattened)) or set(flattened) != set(labels):
        raise ValueError('RSI navigation must cover each page exactly once')
    return [
        {
            'id': section['id'],
            'title': section['title'],
            'open': False,
            'pages': [[slug + '.html', labels[slug]] for slug in section['slugs']],
        }
        for section in NAV_SECTIONS
    ]


def render_navigation(groups: list[dict], current: str) -> str:
    blocks = []
    for group in groups:
        has_active = any(href == current + '.html' for href, _ in group['pages'])
        links = ''.join(
            '<a class="nav-level2' + (' active' if href == current + '.html' else '') +
            '" href="' + html.escape(href, quote=True) + '"' +
            (' aria-current="page"' if href == current + '.html' else '') + '>' +
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
    with (OUT / 'sources.tsv').open(encoding='utf-8', newline='') as stream:
        sources = list(csv.DictReader(stream, delimiter='\t'))
    refmap = {r['id']: r for r in sources}
    assert len(refmap) == len(sources)
    assert all(r['url'].startswith('https://') for r in sources)
    pages = [runpy.run_path(str(ROOT / 'scripts' / 'rsi_pages' / (slug + '.py')))['PAGE'] for slug in ORDER]
    source_sections = [('protocol', '核验口径与检索范围', '''<p>本专题的基础综述始于 2026-10-21；I1–I5 新增最近邻于 2026-10-27 增量核验。定向覆盖 RSI、学习型改进器、课程/元学习、学习科学及实验资源。用论文标题、方法词与引用链交叉检索，优先 arXiv、会议页面、作者机构和官方仓库。</p><p><b>阅读深度不同：</b>“正文方法”表示核对了方法/实验设置，不等于逐条复现全部结果；“摘要”只支持摘要范围的陈述；“官方资源”只确认资产与文档存在。代码入口存在不等于依赖安装、运行、原表重现成功。</p><p><b>原始材料与本次研究：</b>用户分享的推文用于确定入口和问题，不把推文统计或数字自动当作原论文结论。新提案、框架与优先级属于本专题分析，均非文献已经证明的结果。</p><p><b>搜索主题：</b>recursive self-improvement / harness optimization / meta-learning / automated curriculum / learning progress / learner modeling / assistance dilemma / fading / retrieval practice / productive failure / interference replay / skill withdrawal / learning response / selective rehearsal / active failure probing / partner selection / co-distillation。</p><div class="note">这是针对选题的证据地图，不是穷尽全部文献的系统综述。未能核对的作者、发表状态、代码可运行性不补写；预印本标注月份。链接会随论文修订与仓库更新变化，实验须另锁 commit / revision。</div><div class="links"><a class="link-btn" href="sources.json" download>下载来源 JSON</a><a class="link-btn" href="sources.tsv" download>下载来源 TSV</a><a class="link-btn" href="research-notes.md" download>下载整篇研究笔记</a></div>''')]
    for group in dict.fromkeys(s['group'] for s in sources):
        cards = []
        for r in [s for s in sources if s['group'] == group]:
            code = f'<a class="link-btn repo" href="{html.escape(r["code"], quote=True)}" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a>' if r.get('code') else ''
            cards.append(f'''<article class="source-card" id="{r['id']}"><div class="source-meta"><span class="ref-id">{r['id']}</span><span>{html.escape(r['date'])}</span><span class="evidence">{html.escape(r['level'])}</span></div><h3><a href="{html.escape(r['url'], quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(r['title'])}</a></h3><p>{html.escape(r['note'])}</p><div class="links"><a class="link-btn" href="{html.escape(r['url'], quote=True)}" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a>{code}</div></article>''')
        source_sections.append(('group-' + {'RSI':'rsi','相邻领域':'methods','学习科学':'education','实验资源':'assets'}[group], f'{group} · {len(cards)} 项', ''.join(cards)))
    pages.append({'slug':'references','title':'来源与核验记录','en':'Primary sources, explicit reading depth, no implied replication','lead':f'{len(sources)} 条来源：{sum(s["group"] != "实验资源" for s in sources)} 项研究文献 / 学习科学来源，{sum(s["group"] == "实验资源" for s in sources)} 项官方实验资源。逐条保留证据边界。','sections':source_sections})
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
                search.append({'title':p['title'] + ' · ' + title, 'url':slug + '.html#' + sid, 'text':plain(body)})
            notes.append(f'## {p["title"]} / {title}\n\n{body}\n')
        for record in p.get('search_records', []):
            search.append(record)
        for r in sources if slug == 'references' else []:
            search.append({'title':r['id']+' · '+r['title'], 'url':'references.html#'+r['id'], 'text':r['date']+' '+r['group']+' '+r['note']})
        nav = render_navigation(site_nav, slug)
        previous = f'<a href="{pages[idx-1]["slug"]}.html">← {LABELS[idx-1]}</a>' if idx else '<a href="/">← Agent 研究站</a>'
        following = f'<a href="{pages[idx+1]["slug"]}.html">{LABELS[idx+1]} →</a>' if idx < len(pages)-1 else '<a href="ideas.html">回到候选 Idea →</a>'
        title = html.escape(p['title'])
        extra_styles = ''.join(f'<link rel="stylesheet" href="{html.escape(asset, quote=True)}">' for asset in p.get('styles', []))
        extra_scripts = ''.join(f'<script src="{html.escape(asset, quote=True)}"></script>' for asset in p.get('scripts', []))
        assert all(re.fullmatch(r'[a-z0-9-]+\.css', asset) for asset in p.get('styles', []))
        assert all(re.fullmatch(r'[a-z0-9-]+\.js', asset) for asset in p.get('scripts', []))
        doc = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{html.escape(p['lead'], quote=True)}"><meta name="theme-color" content="#101827"><title>{title} | RSI Self-Improvement Observatory</title><link rel="canonical" href="https://agent-evolution.lightrain.asia/rsi/{slug}.html"><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="site-base.css"><link rel="stylesheet" href="research.css"><link rel="stylesheet" href="site-switch.css">{extra_styles}</head>
<body data-rsi-page="{slug}"><a class="skip-link" href="#research-main">跳转到正文</a><div class="layout"><aside class="sidebar" id="sidebar"><button class="sidebar-close" id="sidebar-close" aria-label="关闭目录">×</button><nav class="site-switcher" aria-label="研究网站切换"><span class="site-switcher__caption">研究站点 · SITES</span><div class="site-switcher__tabs"><a class="site-switcher__tab" href="/" title="切换到 Agent 自进化研究站">Agent <span aria-hidden="true">↗</span></a><a class="site-switcher__tab active" href="/rsi/" aria-current="true" title="当前：RSI 自主学习研究站">RSI</a></div></nav><a class="brand" href="index.html"><span class="logo">RSI</span><span><strong>RSI × 自主学习</strong><span>Recursive Self-Improvement</span></span></a><nav class="nav" id="research-nav" aria-label="RSI 专题目录">{nav}</nav><div class="page-toc"><div class="toc-title">本页目录</div><nav class="toc-links">{''.join(toc)}</nav></div><div class="sidebar-note">证据综述与待验证假设分开。<br>核验日期：{DATE}<br>本专题详文为中文，保留英文术语与原始文献标题。</div></aside><button class="sidebar-overlay" id="sidebar-overlay" aria-label="关闭目录遮罩" hidden></button><main class="main" id="research-main"><div class="topbar"><button class="mobile-toggle" id="menu-toggle" aria-label="打开目录" aria-controls="sidebar" aria-expanded="false">☰</button><div class="search"><label class="sr-only" for="research-search">搜索本专题的章节与来源</label><input id="research-search" type="search" placeholder="搜索本专题：课程、帮助、Meta-reset、论文名…" autocomplete="off"></div><button class="language-toggle" id="nav-language" title="只切换目录语言；研究详文为中文">EN navigation</button></div><div class="content"><section class="search-results panel" id="search-results" aria-live="polite" hidden></section><header class="research-hero"><div class="eyebrow">RSI RESEARCH DOSSIER / {idx+1:02d}</div><p class="research-en">{html.escape(p['en'])}</p><h1>{title}</h1><p class="lead">{html.escape(p['lead'])}</p><div class="hero-meta"><span>更新 {page_date}</span><span>来源可追踪</span><span>提案尚待实验</span></div></header>{''.join(body_parts)}<nav class="page-pagination" aria-label="专题翻页">{previous}{following}</nav></div><footer class="footer">RSI × 自主学习研究 · {page_date} · <a href="references.html">来源与核验口径</a> · <a href="research-notes.md" download>研究笔记</a><br>文献结论、研究推断和实验计划分别标注；未运行实验，不展示模拟结果。</footer></main></div><script src="site-nav.js"></script><script src="research.js"></script>{extra_scripts}</body></html>'''
        (OUT / (slug + '.html')).write_text(doc, encoding='utf-8')
    # Save public, portable research records; authoring Python remains outside public output.
    metadata = {'review_date':DATE,'scope':'RSI、学习型改进器、相邻领域与学习科学；定向证据地图，非穷尽性综述。','sources':sources}
    (OUT / 'sources.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (OUT / 'search-index.json').write_text(json.dumps(search, ensure_ascii=False)+'\n', encoding='utf-8')
    notes.append('\n## 原始来源\n\n' + '\n'.join(f'- [{r["id"]}] {r["title"]} · {r["date"]}\n  {r["url"]}' for r in sources))
    (OUT / 'research-notes.md').write_text('\n'.join(line.rstrip() for line in '\n'.join(notes).splitlines()) + '\n', encoding='utf-8')
    print(f'Built {len(pages)} pages; {len(sources)} sources; {len(used)} inline-cited sources; {len(search)} search records.')
    unused = set(refmap)-used
    if unused:
        print('Background / resource records not inline-cited:', ', '.join(sorted(unused)))

if __name__ == '__main__':
    main()
