"""Current RSI paper portfolio; historical I links remain readable and stable."""
from __future__ import annotations

import html
import re
from rsi_taxonomy import FUNCTIONS, IDEAS, PAPER_IDEAS, PAPER_SECTION_SLUGS, PAPER_PORTFOLIO

DATE = '2026-10-30'
STYLE = 'paper-ideas.css'
FUNCTION_BY_ID = {f['id']: f for f in FUNCTIONS}
STATUS = {'mainline': '论文主线 · 待验证', 'reserve': '探索方向 · 先验证现象'}
PRIORITY = {'first': '优先预实验', 'normal': '推进主线', 'explore': '探索保留'}


def merge_portfolio_sources(sources):
    by_id = {s['id']: s for s in sources}
    for record in PAPER_PORTFOLIO['source_records']:
        fields = {k: record[k] for k in ('id', 'group', 'title', 'date', 'url', 'level', 'note', 'code')}
        if record['id'] in by_id:
            by_id[record['id']].update(fields)
        else:
            sources.append(fields)
    return sources


def esc(value):
    return html.escape(str(value), quote=True)


def ordered(items):
    return '<ol class="pi-steps">' + ''.join('<li>' + esc(s) + '</li>' for s in items) + '</ol>'


def link(item, label=None):
    return '<a href="' + esc(item['href']) + '">' + esc(label or item['id'] + ' · ' + item['title']) + '</a>'


def items_for(key):
    return [p for p in PAPER_IDEAS.values() if p['primary'] == key]


def originals(item):
    parts = []
    for origin in item['origins']:
        if origin in IDEAS:
            parts.append('<a href="' + esc(IDEAS[origin]['href']) + '">' + esc(origin) + '</a>')
        else:
            parts.append(esc(origin))
    return ' / '.join(parts)


def cards(items, compact=False):
    out = []
    for item in items:
        status = STATUS[item['status']]
        out.append('<a class="pi-card" data-function="' + item['primary'] + '" href="' + esc(item['href']) + '">'
                   '<span class="pi-card-meta"><b>' + esc(item['id']) + '</b><span>' + esc(status) + '</span></span>'
                   '<strong>' + esc(item['title']) + '</strong><p>' + esc(item['lead']) + '</p>'
                   + ('' if compact else '<small>继承到下一轮：' + esc(item['inheritance']) + '</small>') + '</a>')
    return '<div class="pi-grid">' + ''.join(out) + '</div>'


RELATIONSHIPS = {
    'experience': '四条主线分别改变“修哪种错误、获得什么反证、做什么诊断试验、保留哪些学习经历”。A1+A4 用固定纠错测错误的后续价值；A2 改变证据内容；A3 识别自修改的具体后果；A5 改变经历的领域覆盖。它们可以共用失败轨迹，但不能都把“选到更有用的数据”作为唯一贡献。',
    'signal': 'B1 学会根据真实学习反应教学生；B2 用学生的独立应用反过来纠正教师知识；B4 让评价能力跟上求解能力。三者分别改变教学表达、教师知识、反馈辨别力。B3 只检验语气是否通过持久学习状态影响后续行为，暂列探索。',
    'capability': 'C1 改变知识载体；C2 保留可供未来重新解释的证据；C3 绑定规则与适用条件；C4 建立解锁后续学习的前置知识；C5 改变参数更新规则。它们都研究持久能力，但可操纵对象与核心因果对照不同。',
    'regulation': 'D1+D2 决定学习顺序；D3 决定谁先教谁；D4 决定何时暂停和重访；D5 决定下一次优先检查什么。D6 研究寻找更新规则的程序本身，依赖 C5 的有效规则空间，暂列探索。各项分别固定其他调控动作，避免变成同一个万能调度器。',
}


def idea_body(item):
    refs = ''.join('<article class="pi-related"><a href="' + esc(r['url']) + '" target="_blank" rel="noopener noreferrer">'
                   + esc(r['title']) + ' ↗</a><p><b>原文已经做到：</b>' + esc(r['finding']) + '</p><p><b>本方案进一步检验：</b>'
                   + esc(r['gap']) + '</p></article>' for r in item['related_work'])
    return ('<article class="pi-idea" data-paper-id="' + esc(item['id']) + '">'
            '<div class="pi-meta"><span>' + esc(STATUS[item['status']]) + '</span><span>来源：' + originals(item) + '</span></div>'
            '<p class="pi-claim"><b>核心假设</b> ' + esc(item['lead']) + '</p>'
            '<div class="pi-pair"><div><h3>RSI Challenge · 问题怎样跨轮累积？</h3><p>' + esc(item['challenge']) + '</p></div>'
            '<div><h3>Insight · 为什么可能解决？</h3><p>' + esc(item['insight']) + '</p></div></div>'
            '<h3>Design · 系统具体怎样改变？</h3>' + ordered(item['design'])
            + '<div class="pi-inheritance"><b>传给下一轮的东西</b><p>' + esc(item['inheritance']) + '</p></div>'
            '<details class="pi-depth"><summary>实验设计 · 怎样识别真正的递归贡献？</summary>' + ordered(item['experiment'])
            + '<p><b>第一项预实验：</b>' + esc(item['pilot']) + '</p><p><b>会改变主张的结果：</b>' + esc(item['falsifier']) + '</p></details>'
            '<details class="pi-depth"><summary>最近工作 · 已有贡献与本方案区别</summary>' + refs + '</details>'
            '<p class="pi-boundary"><b>与其他主线的关联和区分：</b>' + esc(item['separation']) + '</p></article>')


def section_pages():
    pages = []
    for f in FUNCTIONS:
        items = items_for(f['id'])
        main = sum(p['status'] == 'mainline' for p in items)
        reserve = len(items) - main
        sections = [('current-lines', '本板块的独立问题', '<p class="pi-claim">' + esc(RELATIONSHIPS[f['id']]) + '</p>'
                     + '<p>' + str(main) + ' 条论文主线' + ('，' + str(reserve) + ' 条探索方向' if reserve else '')
                     + '。以下是待验证的 insight、方法与实验设计；相关论文的已有证据单列说明。</p>' + cards(items, True))]
        sections += [(p['slug'], p['id'] + ' · ' + p['title'], idea_body(p)) for p in items]
        sections.append(('shared-preliminary', '共用预实验与论文边界', '<p>' + esc(RELATIONSHIPS[f['id']]) + '</p>'
                         '<div class="links"><a class="link-btn" href="ideas.html#shared-pre-experiments">共用前置预实验</a>'
                         '<a class="link-btn" href="ideas.html#orthogonality-current">正交分解与合并依据</a>'
                         '<a class="link-btn" href="idea-prioritization.html#current-priority">推进顺序</a></div>'))
        pages.append({'slug': PAPER_SECTION_SLUGS[f['id']], 'title': f['title'] + ' · RSI 论文主线',
                      'en': f['en'] + ' · Current Paper Ideas', 'lead': f['question'] + ' 每项方案明确继承对象、下一轮用途与决定性实验。',
                      'chapter': f['chapter'], 'primary_function': f['id'], 'styles': [STYLE], 'updated': DATE, 'sections': sections})
    return pages


def shared_pre_experiments():
    groups = [
        ('规则与错误的可验证环境', 'A1+A4 · A2 · C3 · C4',
         '准备规则明确、可自动验真的任务族，系统性改变前置缺口、错误条件和捷径。保存相同起点、失败过程及固定纠错接口。隐藏规则只用于环境判定，不能直接交给发现方法。',
         '分别检验纠错的未来材料价值、反证的信息增量、条件绑定、前置知识解锁；共享数据不共享论文的中心结论。'),
        ('教师—学生的真实学习反应', 'B1 · B2 · B4 · D3',
         '固定学生初始状态、知识材料、短课程与撤去辅助后的后测；记录反馈内容、实际更新和新增学习收益。D3 先用三个模型确认 A→B→C 的传递，再扩展十模型舞伴。',
         '分别改变教法、教师知识、评价器或配对顺序；各论文的主实验只操纵其中一个对象。'),
        ('共同起点与后续学习课程', 'A5 · C1 · C2 · C5 · D1+D2',
         '从共同祖先随机分配准备历史，记录实际保存的参数、记忆、Skill 与优化器状态。提供一套公共后续课程和一套由系统自己生成的后续课程，报告完整成本与学习曲线。',
         '公共课程识别当前学习状态的作用；自产课程再检验状态改变后如何影响下一轮材料。C2 另控制总记忆容量及重新解释成本。'),
        ('自修改与延迟后果', 'A3 · D4 · D5',
         '保存候选修改、旧新组件、当前失败、能力变化与延迟执行后果。固定编辑器、任务池和判定标准，提供受控回滚、辨别试验与重访机会。',
         'A3 选择区分因果解释的试验；D4 分配暂停、重访与训练时间；D5 学习风险检查的分配。三者共享版本记录，各自有独立干预。'),
    ]
    return '<div class="pi-grid">' + ''.join('<article class="pi-pretest"><small>' + esc(ids) + '</small><h3>' + esc(title)
            + '</h3><p>' + esc(setup) + '</p><p><b>分开成论文的依据：</b>' + esc(boundary) + '</p></article>'
            for title, ids, setup, boundary in groups) + '</div>'


def causal_standard():
    return '''<p class="pi-claim">递归证据要回答：这一轮留下的改变，是否让下一轮更容易获得有效经验、可信反馈、可用能力或更好的改进决策？</p>
    <p>教师—学生和十模型群体以联合学习系统为研究边界。固定的外部环境与验证器可以提供真实反馈；递归贡献来自系统实际继承并再次使用的改变，既可以在权重中，也可以在可调用的记忆、Skill 或程序中。</p>
    <ol class="pi-steps"><li><b>先写实际继承对象。</b>参数、记忆、Skill、教师策略、评价器、调度策略或更新规则都可以；研究者看到规律不代表系统已继承它。</li>
    <li><b>分开当前能力与未来贡献。</b>可替换组件用旧版与新版作用于同一起点；分布式参数用共同祖先、随机准备历史和相同后续课程。记录起点、增量、终点及完整曲线。</li>
    <li><b>单独检验闭环路径。</b>先做可控机制实验，再让更新后的组件实际生成下一轮材料或决策。若研究对象正是材料分布的变化，闭环阶段允许材料随系统变化。</li>
    <li><b>使用相同信息和完整预算。</b>生成、诊断、搜索、元训练、教师训练和重访都计成本；记忆在学习时使用与在最终评测时检索分别控制。</li>
    <li><b>后测不能参与选择。</b>独立保留后测任务族，多次重跑完整学习链；不挑选恰好同分的检查点，也不由有限轮收益推出无限或超线性加速。</li></ol>
    <p>参考：<a href="https://arxiv.org/html/2609.26457" target="_blank" rel="noopener noreferrer">AIDE² 的同起点 ignition test</a>比较旧新改进器，作者同时指出噪声与成本限制；<a href="https://arxiv.org/html/2510.21614v3" target="_blank" rel="noopener noreferrer">HGM</a>已区分当前表现和后代改进潜力。这里据此细化各论文的可辨别实验。</p>'''


def lineage_table():
    rows = []
    for iid, origin in IDEAS.items():
        matches = [p for p in PAPER_IDEAS.values() if iid in p['origins']]
        rows.append('<tr><td><a href="' + esc(origin['href']) + '">' + esc(iid) + '</a></td><td>'
                    + '；'.join(link(p) for p in matches) + '</td><td>'
                    + '、'.join(dict.fromkeys(FUNCTION_BY_ID[p['primary']]['title'] for p in matches)) + '</td></tr>')
    return '<p>A/B/C/D 是本轮论文问题的标识；I1–I14 保留为原始思路索引。新增 A5、B4、C2 来自领域覆盖、信号平台期和记忆专题。</p>' \
        + '<div class="table-wrap"><table><thead><tr><th>原始编号</th><th>本轮主线或探索方向</th><th>四板块归属</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'


def current_overview():
    intro = '''<p class="pi-claim">本轮最核心的问题：系统学会一件事后，留下了什么，使它下一轮更会学习和改进？</p>
    <p>原始 14 个 idea 与三个专题经过拆分、合并和 RSI 机制补充，形成 <b>16 条候选论文主线＋2 条探索方向</b>。A1 与 A4 合并，D1 与 D2 合并；B3、D6 先验证关键现象。每条同时包含 insight、方法 design 与实验设计，当前均为待验证方案。</p>
    <div class="links"><a class="link-btn" href="#paper-experience">A · 经验获取</a><a class="link-btn" href="#paper-signal">B · 学习信号</a><a class="link-btn" href="#paper-capability">C · 能力形成</a><a class="link-btn" href="#paper-regulation">D · 学习调控</a><a class="link-btn" href="idea-prioritization.html#current-priority">优先预实验</a></div>'''
    sections = [('current-portfolio', '16 条主线＋2 条探索 · RSI 问题与设计', intro)]
    for f in FUNCTIONS:
        items = items_for(f['id'])
        sections.append(('paper-' + f['id'], f['title'], '<p>' + esc(RELATIONSHIPS[f['id']]) + '</p>' + cards(items)
                         + '<p><a href="' + PAPER_SECTION_SLUGS[f['id']] + '.html">逐项阅读 Challenge → Insight → Design → 实验 → 最近工作 →</a></p>'))
    sections += [
        ('orthogonality-current', '正交分解：哪些合并，哪些独立成文？', '''<p>独立论文需要独立的现象解释、可操纵对象和决定性对照。换任务、数据集、指标或模型数量，不足以形成新主线。</p>
        <div class="pi-pair"><article><h3>A1+A4：先研究一个纠错价值问题</h3><p>错误是否可修复、修复能覆盖多少规则，以及它对以后自产材料的影响，先放进同一条机制链。只有出现两套独立机制与证据时，再考虑拆文。</p></article>
        <article><h3>D1+D2：先统一学习顺序与切换</h3><p>先尝试或先看示范、集中或交错学习，都改变历史留下的状态与后续学习路径。共用同材料多重集的顺序干预，避免仅按课程粒度拆文。</p></article></div>
        <p><b>最容易重叠的边界：</b>B1 改教法、B2 改教师知识、D3 改伙伴关系；C1 改载体、C2 改证据保留与重解释、C3 改条件绑定；C5 改更新规则 η、D6 改寻找规则的程序 π；A3 改诊断试验、D4 改预算和重访、D5 改风险检查。</p>'''),
        ('shared-pre-experiments', '四组可共享的前置预实验', shared_pre_experiments()),
        ('recursive-evidence', '所有主线共用的 RSI 证据要求', causal_standard()),
        ('lineage-current', '原始 I1–I14 → 当前论文主线', lineage_table()),
    ]
    return sections


def historical_sections(sections, scope='原始方案'):
    return [(sid, scope + ' · ' + title, '<details class="pi-depth pi-history"><summary>展开前期记录：' + esc(title)
             + '</summary><p class="pi-archive-note">本段保留早期推导、文献与实验细节；当前主张、归属与推进顺序以上方 2026-10-30 方案为准。</p>' + body + '</details>')
            for sid, title, body in sections]


def apply_portfolio(pages):
    page_map = {p['slug']: p for p in pages}
    overview = page_map['ideas']
    old = overview['sections']
    # Link each historical I anchor to its current paper(s) without changing the anchor.
    replacements = {}
    for iid in IDEAS:
        matches = [p for p in PAPER_IDEAS.values() if iid in p['origins']]
        replacements['idea-' + iid[1:]] = '<p class="pi-archive-note"><b>当前方案：</b>' + '；'.join(link(p) for p in matches) + '</p>'
    linked_old = []
    for sid, title, body in old:
        for anchor, notice in replacements.items():
            pattern = r'(<details\b[^>]*\bid="' + re.escape(anchor) + r'"[^>]*>\s*<summary>.*?</summary>)'
            body = re.sub(pattern, lambda m: m.group(1) + notice, body, count=1, flags=re.S)
        linked_old.append((sid, title, body))
    overview.update(title='RSI 研究方向 · 16 条论文主线＋2 条探索', en='RSI Paper Portfolio · 16 Mainlines and 2 Explorations',
                    lead='逐项说明 RSI 挑战、可验证的 insight、可继承的设计和下一轮学习实验；按综述四项功能归类。',
                    updated=DATE, styles=list(dict.fromkeys(overview.get('styles', []) + [STYLE])),
                    sections=current_overview() + historical_sections(linked_old))
    rank = page_map['idea-prioritization']
    first = [p for p in PAPER_IDEAS.values() if p['priority'] == 'first']
    normal = [p for p in PAPER_IDEAS.values() if p['priority'] == 'normal']
    explore = [p for p in PAPER_IDEAS.values() if p['status'] == 'reserve']
    rank.update(title='RSI 主线优先级与共用预实验', en='RSI Research Priorities and Shared Preliminary Experiments',
                lead='先验证六条直接对应 RSI 瓶颈的主线，其余按机制与基础设施推进；两条探索先确认关键现象。', updated=DATE,
                styles=list(dict.fromkeys(rank.get('styles', []) + [STYLE])))
    first_body = '<p>优先级是结合本轮文献和设计成熟度的研究判断；独立成文仍取决于实际证据。优先推进 A2、B4、C2、C4、D3、D5。</p>' + cards(first, True)
    first_body += '<div class="pi-grid">' + ''.join('<article class="pi-pretest"><h3>' + link(p) + '</h3><p><b>先做：</b>' + esc(p['pilot']) + '</p><p><b>判断依据：</b>' + esc(p['falsifier']) + '</p></article>' for p in first) + '</div>'
    rank['sections'] = [('current-priority', '第一批：六条直接对应 RSI 挑战的主线', first_body),
                        ('current-next', '第二批：继续推进的十条主线', cards(normal, True)),
                        ('current-explorations', '探索保留：B3 与 D6', cards(explore, True)),
                        ('current-shared', '共用前置实验，分别建立论文证据', shared_pre_experiments())] + historical_sections(rank['sections'], '历史评估')
    banner = '<p class="pi-claim">当前研究计划：<b>16 条候选论文主线＋2 条探索方向</b>。每项都写明上一轮的继承对象、下一轮的用途和可区分实验。</p><div class="links"><a class="link-btn" href="ideas.html#current-portfolio">查看完整主线</a><a class="link-btn" href="idea-prioritization.html#current-priority">先做哪些预实验</a></div>'
    for slug in ('index', 'agenda', 'experiments'):
        p = page_map[slug]
        p['sections'].insert(0, ('current-paper-plan', '当前论文计划 · 2026-10-30', banner))
        p['styles'] = list(dict.fromkeys(p.get('styles', []) + [STYLE]))
        p['updated'] = DATE
    topic_mapping = {
        'memory-research-map': ['C2'], 'experience-consolidation': ['C1', 'C2'],
        'learning-signal-bottlenecks': ['B4'], 'generalization-learnability': ['A5', 'C4', 'C5', 'D1+D2'],
    }
    for iid, origin in IDEAS.items():
        slug = origin['href'].split('#')[0].removesuffix('.html')
        if slug == 'ideas':
            continue
        topic_mapping.setdefault(slug, [])
        topic_mapping[slug] += [p['id'] for p in PAPER_IDEAS.values() if iid in p['origins']]
    for slug, ids in topic_mapping.items():
        p = page_map[slug]
        matches = [PAPER_IDEAS[i] for i in dict.fromkeys(ids)]
        body = '<p>本页的原始思路与文献推导已纳入以下当前主线。完整的 RSI challenge、insight、design、关键实验和最近工作比较，集中在新主线详情中。</p>' + cards(matches, True)
        body += '<p class="pi-archive-note">下文保留前期研究记录和技术细节；当前论文边界与优先级以本轮主线为准。</p>'
        position = 1 if slug == 'generalization-learnability' else 0
        p['sections'].insert(position, ('current-paper-links', '本轮对应主线 · 2026-10-30', body))
        p['styles'] = list(dict.fromkeys(p.get('styles', []) + [STYLE]))
        p['updated'] = DATE
    pages.extend(section_pages())
