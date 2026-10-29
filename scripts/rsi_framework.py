"""Shared four-function classification and chapter rendering for the RSI site."""
from __future__ import annotations
import html, json, re
from pathlib import Path
from rsi_taxonomy import FUNCTIONS, IDEAS, SOURCE_MAP, PAPER_MAP

ROOT = Path(__file__).resolve().parents[1]
FUNCTION_SLUGS = {'experience':'experience','signal':'signals','capability':'capabilities','regulation':'regulation'}
BY_ID = {f['id']:f for f in FUNCTIONS}

def esc(value):
    return html.escape(str(value), quote=True)

def assignment(value):
    value = {'primary':value,'related':[]} if isinstance(value,str) else (value or {})
    primary = value.get('primary')
    related = list(dict.fromkeys(value.get('related',[])))
    assert primary is None or primary in BY_ID, value
    assert all(k in BY_ID and k != primary for k in related), value
    return {**value,'primary':primary,'related':related}

def source_assignment(source):
    sid = source['id'] if isinstance(source,dict) else source
    if sid not in SOURCE_MAP:
        raise ValueError('Source needs a reviewed assignment: '+sid)
    return assignment(SOURCE_MAP[sid])

def paper_assignment(paper):
    pid = paper['id'] if isinstance(paper,dict) else paper
    if pid not in PAPER_MAP:
        raise ValueError('Paper needs a reviewed assignment: '+pid)
    return assignment(PAPER_MAP[pid])

def function_badges(primary=None, related=(), *, label=True):
    bits=[]
    if primary:
        bits.append(f'<a class="function-badge function-badge--{primary}" data-function="{primary}" href="{FUNCTION_SLUGS[primary]}.html">{"主归属 · " if label else ""}{esc(BY_ID[primary]["title"])}</a>')
    for key in related:
        bits.append(f'<a class="function-badge function-badge--related" data-function="{key}" href="{FUNCTION_SLUGS[key]}.html">关联 · {esc(BY_ID[key]["title"])}</a>')
    return '<div class="function-badges">'+''.join(bits)+'</div>' if bits else ''

def enrich_registries(sources):
    for s in sources:
        item=source_assignment(s)
        s.update(primary_function=item['primary'],related_functions=item['related'],
                 classification_reason=item.get('reason',''),source_role=item.get('role','research'),
                 source_domain=s['group'])
    path=ROOT/'rsi/reading-cards.json'
    data=json.loads(path.read_text(encoding='utf-8'))
    data['taxonomy_version']='learning-functions-2026-10-29'
    data['learning_functions']=FUNCTIONS
    data['diagnostic_dimensions_note']='research_questions/research_coverage保留原有诊断记录；唯一主体分类使用primary_function。'
    for p in data['papers']:
        item=paper_assignment(p)
        p.update(primary_function=item['primary'],related_functions=item['related'],
                 classification_reason=item.get('reason',''),source_ids=item.get('source_ids',[]))
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for filename,collection in [('theory-notes.json','entries'),('related-work.json','targets')]:
        p=ROOT/'rsi'/filename
        d=json.loads(p.read_text(encoding='utf-8'));d['taxonomy_version']=data['taxonomy_version']
        for entry in d[collection]:
            item=paper_assignment(entry.get('source_paper_id') or entry.get('paper_id'))
            entry.update(primary_function=item['primary'],related_functions=item['related'])
        p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    protocol_ideas={'i2-learner-response-protocol.json':'I2','i5-method-protocol.json':'I5',
                    'i12-experiment-protocol.json':'I12','teaching-protocol.json':'I5'}
    for filename,iid in protocol_ideas.items():
        path=ROOT/'rsi'/filename
        protocol=json.loads(path.read_text(encoding='utf-8'))
        protocol['primary_function']=IDEAS[iid]['primary']
        protocol['related_functions']=IDEAS[iid].get('related',[])
        protocol['taxonomy_version']=data['taxonomy_version']
        path.write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    path=ROOT/'rsi/generalization-protocol.json'
    protocol=json.loads(path.read_text(encoding='utf-8'))
    protocol.update(page_role='cross-cutting-evidence',chapter=7,learning_functions=list(BY_ID),taxonomy_version=data['taxonomy_version'])
    path.write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    export={'schema_version':1,'version':data['taxonomy_version'],
            'central_question':'系统如何把不断获得的经历，转化为能够迁移、能够保留，并且支持后续学习的能力？',
            'functions':FUNCTIONS,'ideas':IDEAS,'sources':{s['id']:source_assignment(s) for s in sources},'papers':PAPER_MAP,
            'classification_rule':'按主要科学贡献确定唯一主归属；方法、载体、组织方式、评价目标另作描述字段。',
            'cross_cutting':{'generalization':'贯穿四功能，第7章集中评价','memory':'第4章归因、第5章保存与抽象、第6章修订、第7章检验'}}
    (ROOT/'rsi/taxonomy.json').write_text(json.dumps(export,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return data['papers']

SUBSECTIONS={
'experience':[
('识别能力缺口与学习需求','系统首先要判断当前做不对什么，以及哪些缺口有可能被修复。不确定性、失败分布和能力边界提供线索；前置知识准备程度影响同一经历对不同学习者的价值。','什么证据能区分缺少信息、缺少知识准备与缺少有效更新方式？'),
('构造有信息量的任务与交互','自生成任务、探索、自博弈和环境交互都在创造学习机会。比较它们时，重点是新经历是否提供原先缺少的信息，或者能够排除当前混淆的解释。样本的表面变化应与规则变化分开。','哪个例子或反例最能区分真实规则与当前捷径？'),
('从教师、伙伴和工具获得新信息','教师、伙伴和工具是信息来源，也是系统组织方式。需要记录它们提供了什么、与学习者共享哪些盲点，以及所得信息能否改变后续能力。跨轮教法变化和伙伴重组在第6章集中讨论。','伙伴贡献的是新信息、纠错线索，还是已有答案的重复？'),
('选择具有学习价值的经历','难度、新颖性、覆盖度和失败类型描述经验的不同性质。学习价值还取决于当前知识状态与后续更新，应把选择依据与真实学习后的迁移、保持和成本连接起来。','同样的失败，哪些值得学，哪些应该继续尝试或暂缓？')],
'signal':[
('学习信号的来源与可靠性','环境验证、外部评价、自我评价和同伴评价提供不同形式的反馈。可靠性涉及覆盖范围、共同盲点、误差和置信度；被评价对象变化后，原信号是否仍然有效也需要检查。','学习者与评价器一起变化时，反馈能否仍然指向真实改进？'),
('从任务结果到失败诊断','相同错误终点可能来自知识、搜索、选择或执行中的不同问题。过程信息提供诊断线索，诊断的有效性需要与实际干预及其学习后果对应。','同题同错时，失败过程能否指出真正值得修复的部分？'),
('经验、步骤与记忆的贡献归因','一次成功可能同时依赖推理步骤、检索记忆、示范和工具。信用分配关注各因素的贡献，而不只是记录它们是否出现。移除、替换和配对干预可以帮助区分解释。','哪条记忆、哪个示范或哪一步经验实际改变了决策与学习？'),
('从任务评价到学习收益评价','答案正确、反馈准确、学习者能够吸收、更新改善未来表现，是需要分别研究的量。将任务评价转为学习目标时，应明确预测对象、可用信息和反馈何时可得。','能否在更新之前，预测一次纠错对未见同类任务的净收益？')],
'capability':[
('从具体经历形成知识','原始实例、抽象规则、程序和技能保存不同层次的信息。应检查抽象保留与丢失了什么、规则是否记录适用条件，以及所得知识能否在新情境中复用和组合。','系统学到的是某个答案、局部操作，还是可复用的关系？'),
('在外部状态中保存和使用能力','情景记忆、语义记忆、技能库、提示和工具代码可以形成持久系统状态。需要把写入内容、组织方式、调用条件与后续实际行为的变化联系起来。','什么内容值得保存，何时调用，怎样判断调用确实有帮助？'),
('将经验巩固到模型参数中','监督微调、蒸馏和强化学习是不同的能力更新方法。比较时记录学习信号、训练信息、预算和学习者状态，并用未见任务检查形成的能力。','什么条件下，经验能够经由参数更新形成可迁移的能力？'),
('协调外部支持与内部学习','同一经验可以保留为实例、压缩为规则、写入技能或用于参数更新。选择取决于知识准备、任务变化、调用成本和修订需求。移除外部支持的测试帮助定位收益保存在哪里。','哪些经验值得内化，哪些适合继续查询，两种方式何时相互促进？')],
'regulation':[
('新旧知识的兼容、冲突与修订','遗忘、干扰、回放、记忆过时和规则冲突都涉及多次学习的相互作用。除了新知识收益，还要检查旧能力与适用边界，区分知识冲突和使用条件错配。','新旧规则都有用时，怎样修复各自的适用边界？'),
('学习顺序与未来可学习性','先尝试还是先示范、集中还是交错、先补哪项前置能力，形成不同学习历史。当前表现与未来学习过程需要分别测量，后者要控制下一阶段材料、更新器和预算。','当前表现相近的两个系统，过去的学习顺序是否仍改变未来学习速度？'),
('学习动作与资源的动态分配','探索、总结、更新、复习和停止都是学习动作。更新接纳、回退与验证预算也属于调控；比较决策时应计入整个过程的交互、训练、推理和验证成本。','何时值得继续采样、搜索或回放，何时应该更新或停止？'),
('学习机制自身的改进','教师策略、学习控制器、更新规则和多智能体协作机制，都可能从历史学习结果中改变。需要把机制优化与独立效果检验区分，并考察未参与优化的任务和学习者。','系统能否逐渐改善自己获得经历、判断信号和更新能力的方式？')]
}

def representative_table(key,sources):
    from rsi_taxonomy import FEATURED_SOURCE_IDS
    pool={s['id']:s for s in sources}
    selected=[pool[x] for x in FEATURED_SOURCE_IDS.get(key,[]) if x in pool]
    if not selected:
        selected=[s for s in sources if source_assignment(s)['primary']==key][:8]
    rows=''.join(f'<tr><td><a href="references.html#{s["id"]}">{esc(s["title"])}</a> [[{s["id"]}]]</td><td>{esc(source_assignment(s).get("reason",""))}</td><td>{esc(s["note"])}</td></tr>' for s in selected)
    return '<div class="table-wrap"><table><thead><tr><th>代表工作</th><th>主要解决的问题</th><th>已有研读记录与证据范围</th></tr></thead><tbody>'+rows+'</tbody></table></div>'

def idea_links(key):
    return ''.join(f'<a class="framework-idea" href="{esc(v["href"])}"><b>{esc(k)} · {esc(v["title"])}</b><span>主要问题 · {esc(v.get("section",""))}</span></a>' for k,v in IDEAS.items() if v['primary']==key)

def framework_pages(sources):
    pages=[]
    for f in FUNCTIONS:
        key,chapter=f['id'],f['chapter']
        sections=[('question','本章科学问题',f'<div class="framework-question">{esc(f["question"])}</div><p>{esc(f.get("summary",""))}</p><p>按主要科学贡献归档；方法、能力载体和组织方式分别描述，其他功能中的作用通过交叉引用连接。</p>')]
        for n,(title,text,question) in enumerate(SUBSECTIONS[key],1):
            sections.append((f'section-{chapter}-{n}',f'{chapter}.{n} {title}',f'<p>{text}</p><p class="framework-open"><b>要回答的问题：</b>{question}</p>'))
        sections.extend([
            ('representative-work','代表工作 · 机制与证据',representative_table(key,sources)+f'<p><a href="references.html?function={key}#function-{key}">查看全部来源 →</a> · <a href="reading-cards.html?function={key}">筛选本功能精读 →</a></p>'),
            ('research-directions','我们的研究问题与设计','<p>稳定I编号保持不变；按主要问题归属，关联功能不重复计数。</p><div class="framework-ideas">'+idea_links(key)+'</div>'),
            ('evidence-connection','泛化、保持与未来学习','<p>本章机制需要用未见任务、后续更新后的保持、新能力学习过程和长期成本来检验。不同主张对应不同证据。</p><div class="links"><a class="link-btn" href="evidence.html">第7章 · 证据与评价</a><a class="link-btn" href="generalization-learnability.html">泛化与未来可学习性专题</a><a class="link-btn" href="agenda.html">第8章 · 开放问题</a></div>')
        ])
        pages.append({'slug':FUNCTION_SLUGS[key],'title':f['title'],'en':f.get('en',''),'lead':f['question'],'updated':'2026-10-29','chapter':chapter,'primary_function':key,'sections':sections})
    pages.append({'slug':'foundations','title':'范围与统一分析框架','en':'Scope and Foundations','lead':'从当前输出改善、持久系统学习，到学习机制自身的改进，明确研究对象与分类规则。','chapter':2,'sections':[
        ('scope','2.1 自我改进与递归自我改进的范围','<div class="table-wrap"><table><thead><tr><th>观察层次</th><th>发生的变化</th><th>应记录的因素</th></tr></thead><tbody><tr><td>当前输出改善</td><td>反思、搜索或修订使一次任务表现改善。</td><td>推理计算、上下文和外部帮助。</td></tr><tr><td>持久系统学习</td><td>经验进入参数、记忆、技能等持久状态，影响未来任务。</td><td>改变的状态、后续使用条件、收益和保持。</td></tr><tr><td>学习机制改进</td><td>获取经验、评价或更新的机制本身变化。</td><td>新任务和未见学习者上的真实效果。</td></tr></tbody></table></div><p>外部记忆带来的持久系统改进同样属于研究对象。是否更新参数是机制差异；移除外部支持有助于定位收益，完整系统仍须独立评估。</p>'),
        ('framework','2.2 四项学习功能','<div class="framework-function-grid">'+''.join(f'<a class="framework-function" data-function="{f["id"]}" href="{FUNCTION_SLUGS[f["id"]]}.html"><small>第{f["chapter"]}章</small><h3>{esc(f["title"])}</h3><p>{esc(f["question"])}</p></a>' for f in FUNCTIONS)+'</div><p>前三项说明一次改进如何发生，学习调控协调它们在多轮学习中的相互作用。这是带有反馈关系的功能划分，不是严格单向流水线。</p>'),
        ('classification','分类规则与交叉描述','<div class="table-wrap"><table><thead><tr><th>字段</th><th>回答的问题</th><th>示例</th></tr></thead><tbody><tr><td>唯一主分类</td><td>主要解决什么学习问题？</td><td>经验获取、学习信号、能力形成、学习调控。</td></tr><tr><td>方法</td><td>怎样实现改变？</td><td>RL、SFT、蒸馏、元学习。</td></tr><tr><td>载体</td><td>变化保存在哪里？</td><td>参数、记忆、技能、工具代码。</td></tr><tr><td>组织方式</td><td>哪些系统参与？</td><td>教师—学生、多智能体、工具。</td></tr><tr><td>结果与评价</td><td>形成怎样的能力？</td><td>泛化、保持、未来可学习性、成本。</td></tr><tr><td>机制来源</td><td>假设从哪里得到启发？</td><td>机器学习、教育学、认知科学、神经科学。</td></tr></tbody></table></div><p>一项工作在最能体现主要贡献的章节完整介绍，其余章节交叉引用。I1–I14用于稳定管理，分类改变不会改变其编号或原始链接。</p>'),
        ('method','2.3 文献范围与综述方法',f'<p>当前来源库有{len(sources)}项记录。基础研读自2026年10月21日开始，沿已有问题、论文引用链、会议期刊原文与作者官方资源增量补充；本次分类更新截至2026年10月29日。</p><p>现有材料是定向研读形成的证据地图。按与持续学习功能、机制解释和研究设计的相关性纳入，保留每项发表日期、阅读深度和原始链接；预印本与正式发表状态沿用逐篇核验记录。</p><p>跨领域迁移依次说明：原领域现象 → 可能机制 → AI对应条件与差异 → 可检验假设 → 能够区分解释的实验。</p><div class="links"><a class="link-btn" href="references.html#protocol">来源与检索记录</a><a class="link-btn" href="taxonomy.json">分类数据</a><a class="link-btn" href="research-map.html">统一研究地图</a></div>')
    ]})
    pages.append({'slug':'evidence','title':'泛化、保持与持续改进的证据','en':'Evidence and Evaluation','lead':'用与主张对应的独立证据，判断经历是否形成可迁移、可保留并支持后续学习的能力。','chapter':7,'page_role':'evidence','sections':[
        ('attribution','7.1 改进来自哪里','<p>分别检查额外推理计算、上下文支持、持久记忆和参数更新的贡献。同信息、同预算配对比较，记录训练、推理、交互和验证成本。移除支持可以定位收益来源，也应保留完整系统的评价。</p><p class="note">第4章的评价器参与学习，提供诊断与更新信号；第7章独立检查改进主张。两者可以使用相似工具，但承担不同职责。</p>'),
        ('transfer','7.2 能力能否迁移','<p>分别检验未见实例、未见组合、不同任务结构与变化环境。测试应能够区分实例记忆、局部操作和规则复用，明确允许使用哪些持久状态与外部支持。</p><p><a href="generalization-learnability.html">泛化与未来可学习性专题</a>保留已精读文献及I3/I8/I9/I10/I12/I14的具体实验联系。</p>'),
        ('retention','7.3 能力能否保留，并支持继续学习','<div class="card-grid"><article class="research-card"><h3>旧能力保持</h3><p>经过后续学习，原有能力保留多少？检查新旧规则冲突、误用和任务覆盖。</p></article><article class="research-card"><h3>未来可学习性</h3><p>获得新能力是否更容易？控制当前能力和后续训练条件，比较新任务真实学习曲线。</p></article></div><p>两者需要分别测量。当前测试分数相近，不直接意味着未来学习能力相同。</p>'),
        ('cost','7.4 长期收益、成本与副作用','<p>同时报告多轮新增收益、旧能力保持、未来学习与资源使用。安全约束和行为副作用作为结果维度记录；更新接纳策略的设计属于第6.3节，独立效果在本章检验。</p>'),
        ('claims','主张—证据对应表','<div class="table-wrap"><table><thead><tr><th>希望支持的主张</th><th>需要关注的证据</th><th>相关研究</th></tr></thead><tbody><tr><td>获得可复用能力</td><td>未见任务表现；收益依赖哪些持久状态。</td><td><a href="ideas.html#idea-1">I1</a> · <a href="experience-consolidation.html">经验巩固</a></td></tr><tr><td>学到可迁移规则</td><td>区分实例记忆与规则迁移的测试。</td><td><a href="i8.html">I8</a> · <a href="idea-i10-learning-novelty.html">I10</a></td></tr><tr><td>实现累积改进</td><td>多轮新增收益与后续学习后的旧能力保持。</td><td><a href="ideas.html#idea-3">I3</a> · <a href="idea-i5.html">I5</a></td></tr><tr><td>改善未来可学习性</td><td>控制当前能力和后续训练条件后的新任务学习过程。</td><td><a href="idea-i9-practice-switching.html">I9</a> · <a href="idea-i12-prerequisite-bottleneck.html">I12</a></td></tr><tr><td>改进学习机制</td><td>未参与优化的任务或环境中的机制效果。</td><td><a href="idea-i2.html">I2</a> · <a href="learning-rule-evolution.html">I14</a></td></tr></tbody></table></div><p>不同主张需要不同证据，不把所有工作压成单一强弱排名。</p>')
    ]})
    questions=[
        ('value','学习价值能否在更新前被判断？','连接经验选择、学习者状态和收益预测。比较置信度、难度与实际更新后的未见题净收益。',[('I6','idea-i6-failure-value.html'),('I8','i8.html'),('I2','idea-i2.html')]),
        ('representation','什么经验表示兼顾细节、迁移与修订？','连接记忆、抽象、泛化与知识冲突。比较实例、规则和技能，检查适用条件、信息损失与后续修订。',[('I1','ideas.html#idea-1'),('I3','ideas.html#idea-3'),('记忆专题','memory-research-map.html')]),
        ('readiness','目前缺的是信息、知识准备，还是更新方式？','连接失败诊断、教学与能力形成。用相同材料、补前置知识和替换训练信号的干预区分原因。',[('I10','idea-i10-learning-novelty.html'),('I12','idea-i12-prerequisite-bottleneck.html'),('训练信号专题','learning-signal-bottlenecks.html')]),
        ('co-evolution','学习者、教师和评价器一起变化时，如何获得可靠依据？','连接反馈可靠性、共同盲点和跨轮调控。分别检查各方变化、留出任务效果与同预算对照。',[('I2','idea-i2.html'),('I5','idea-i5.html'),('I13','learning-admission.html')]),
        ('future','当前表现与未来学习能力何时一致、何时冲突？','连接学习顺序、可塑性、资源分配和长期评价。匹配当前能力，再比较新任务学习速度、保持和成本。',[('I7','idea-i7-learning-order.html'),('I9','idea-i9-practice-switching.html'),('I14','learning-rule-evolution.html')])]
    sections=[(sid,title,f'<p>{text}</p><div class="links">'+''.join(f'<a class="link-btn" href="{url}">{label}</a>' for label,url in links)+'</div>') for sid,title,text,links in questions]
    sections.append(('reasoning','从文献启发走向可检验研究','<p>每个问题依次组织：科学问题 → 已知现象 → 主要解释 → 现有方法 → 证据范围 → 未解问题。跨领域迁移还需要说明对应条件与差异，再提出辨别机制的实验。</p><p>文献结论、本站综合判断、跨领域假设和待做实验分别标明。I编号用于持续管理，不表示方案已得到实验验证。</p><div class="links"><a class="link-btn" href="ideas.html">完整研究方案</a><a class="link-btn" href="idea-prioritization.html">优先级与决定性实验</a></div>'))
    pages.append({'slug':'agenda','title':'开放问题与研究议程','en':'Open Questions and Research Agenda','lead':'把已知现象、机制解释、跨领域假设和待验证设计连接到横跨四项学习功能的科学问题。','chapter':8,'page_role':'agenda','sections':sections})
    return pages

PAGE_META={
'index':{'chapter':1},
'memory-research-map':{'primary_function':'capability','related_functions':['signal','regulation']},
'experience-consolidation':{'primary_function':'capability','related_functions':['regulation']},
'learning-signal-bottlenecks':{'primary_function':'signal','related_functions':['capability','regulation']},
'generalization-learnability':{'chapter':7,'page_role':'cross-cutting'},
'curriculum-scale-evidence':{'chapter':7,'page_role':'evidence'},
'experiments':{'chapter':7,'page_role':'evidence'},
'idea-i6':{'page_role':'archive'},'teaching':{'page_role':'branch'}}

def apply_page_metadata(pages):
    for p in pages:
        p.update(PAGE_META.get(p['slug'],{}))
        for iid,idea in IDEAS.items():
            if idea['href']==p['slug']+'.html':
                p.update(primary_function=idea['primary'],related_functions=idea.get('related',[]),idea_id=iid)
        if p.get('primary_function'):
            p.setdefault('chapter',BY_ID[p['primary_function']]['chapter'])
        if p['slug']=='idea-prioritization':
            updated=[]
            for sid,title,body in p['sections']:
                m=re.fullmatch(r'idea-(\d+)',sid)
                iid='I'+m[1] if m else None
                if iid in IDEAS:
                    body=function_badges(IDEAS[iid]['primary'],IDEAS[iid].get('related',[]))+body
                updated.append((sid,title,body))
            p['sections']=updated

def organize_ideas(page):
    grouped={k:[] for k in BY_ID};other=[]
    for sid,title,body in page['sections']:
        m=re.fullmatch(r'idea-(\d+)',sid)
        iid='I'+m[1] if m else None
        if iid not in IDEAS:
            other.append((sid,title,body));continue
        idea=IDEAS[iid];badge=function_badges(idea['primary'],idea.get('related',[]))
        grouped[idea['primary']].append(f'<details class="framework-idea-detail" id="{sid}" data-primary-function="{idea["primary"]}"><summary>{esc(title)}</summary><div class="framework-detail-body">{badge}{body}</div></details>')
        page.setdefault('search_records',[]).append({'title':iid+' · '+idea['title'],'url':'ideas.html#'+sid,'text':BY_ID[idea['primary']]['title']+' '+re.sub('<[^>]+>',' ',body),'primary_function':idea['primary']})
    intro='<p>按主要研究问题组织方案，稳定I编号保持不变。一项方案在主归属完整介绍，其他功能通过关联链接连接。泛化贯穿评价，记忆按实际作用归档。</p><div class="framework-function-grid">'
    intro+=''.join(f'<a class="framework-function" data-function="{f["id"]}" href="#ideas-{f["id"]}"><small>第{f["chapter"]}章 · {len(grouped[f["id"]])}项</small><b>{esc(f["title"])}</b><span>{esc(f["question"])}</span></a>' for f in FUNCTIONS)
    page['sections']=[('classification','四项学习功能 · I1–I14',intro+'</div>')]
    page['sections'] += [('ideas-'+f['id'],f['title'],''.join(grouped[f['id']])) for f in FUNCTIONS]
    page['sections'] += other
    page['lead']='用四项学习功能串联现象、已有研究、Insight与实验设计；I1–I14保留原编号与完整内容。'
