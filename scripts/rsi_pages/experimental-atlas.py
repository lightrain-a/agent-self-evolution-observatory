"""Reader-first atlas. Data is exported from a pinned manuscript commit."""
import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DATA=json.loads((ROOT/'rsi/experiment-catalog.json').read_text(encoding='utf-8'))
E=lambda x:html.escape(str(x),quote=True)
Q={x['id']:x for x in DATA['questions']}
G={x['id']:x['title'] for x in DATA['groups']}
TYPES={'application':'已报道使用','introduction':'基准提出','protocol':'协议／适配层'}
KINDS={'paper':'论文','metric':'指标','control':'对照','family':'原始资源家族'}

def link(url,label):
    return '<a href="'+E(url)+'" target="_blank" rel="noopener noreferrer">'+E(label)+'</a>' if url.startswith('https://') else E(label)

def search_blob(s):
    s=s.lower()
    aliases={'memory':'记忆','forget':'遗忘','retention':'保持','learn':'学习','teacher':'教师 教学','student':'学生','curricul':'课程','calibr':'校准','cost':'成本','safety':'安全','attack':'攻击','improver':'改进器','plasticity':'可塑性','code':'代码 编程','reasoning':'推理','robot':'机器人 具身','curve':'曲线','transfer':'迁移','reward':'奖励','selection':'选择','confidence':'置信','privacy':'隐私','rollback':'回滚','diversity':'多样性','coverage':'覆盖'}
    return s+' '+' '.join(v for k,v in aliases.items() if k in s)


def dataset_card(d):
    uses=[]
    for u in d['uses']:
        studies=''.join('<button type="button" class="atlas-inline" data-record-target="'+E(s)+'">查看 '+E(s)+' 配置</button>' for s in u['study_ids'])
        uses.append('<li><div class="atlas-use-heading">'+link(u['source']['url'],u['paper'])+' <span class="atlas-role">'+TYPES[u['kind']]+'</span></div><p>'+E(u['role'])+'</p>'+studies+'</li>')
    papers=' · '.join(u['paper'] for u in d['uses'])
    tags=''.join('<span class="atlas-tag">'+E(Q[q]['title'])+'</span>' for q in d['questions'])
    search=' '.join([d['name'],G[d['group']],papers,d['metric'],d['note'],*[u['role'] for u in d['uses']],*[Q[q]['title'] for q in d['questions']]])
    return '<article class="atlas-card" id="dataset-'+E(d['id'])+'" data-atlas-item data-kind="datasets" data-group="'+E(d['group'])+'" data-questions="'+E(' '.join(d['questions']))+'" data-search="'+E(search_blob(search))+'"><div class="atlas-card-top"><span class="atlas-category">'+E(G[d['group']])+'</span><h3>'+E(d['name'])+'</h3></div><p class="atlas-paper-line"><b>对应论文</b> '+E(papers)+'</p><div class="atlas-tags">'+tags+'</div><details><summary>展开用途、评价和比较条件</summary><ul class="atlas-uses">'+''.join(uses)+'</ul><div class="atlas-evidence-grid"><div><b>原生评价</b><p>'+E(d['metric'])+'</p></div><div><b>比较前检查</b><p>'+E(d['note'])+'</p></div></div></details></article>'

def record_card(r):
    datasets=[d for d in DATA['datasets'] if any(r['id'] in u['study_ids'] for u in d['uses'])]
    association=''.join('<button type="button" class="atlas-inline" data-dataset-target="'+E(d['id'])+'">'+E(d['name'])+'</button>' for d in datasets)
    headers={'paper':['模型与可变状态','任务和读数','对照与使用边界'],'family':['可观察结果','版本与解释条件'],'metric':['定义／操作口径','解释边界'],'control':['固定什么、改变什么','能回答什么']}[r['kind']]
    cells=''.join('<div><b>'+E(headers[i] if i<len(headers) else '说明')+'</b><p>'+E(cell)+'</p></div>' for i,cell in enumerate(r['cells'][1:]))
    sources=' · '.join(link(s['url'],s['title']) for s in r['citations'])
    assets=' '.join(link(s['url'],s['label']) for s in r['links'])
    mapping=('<div class="atlas-related"><b>从资源反查</b>'+association+'</div>' if datasets else '<p class="atlas-muted">此条目尚未录入独立的数据集级对应；不据此推断其没有使用数据集。完整配置见下面原始条目。</p>') if r['kind']=='paper' else ''
    latex='<details class="atlas-latex"><summary>查看原表 LaTeX（公式以原文为准）</summary><pre>'+E(r.get('latex',''))+'</pre></details>' if r['kind']=='metric' else ''
    search=' '.join([r['title'],r['id'],*r['cells'],*[s['title'] for s in r['citations']],*[d['name']+' '+G[d['group']] for d in datasets]])
    return '<article class="atlas-card" id="record-'+E(r['id'])+'" data-atlas-item data-kind="'+E(r['kind'])+'" data-search="'+E(search_blob(search))+'"><div class="atlas-card-top"><span class="atlas-category">'+E(KINDS[r['kind']])+' · '+E(r['id'])+'</span><h3>'+E(r['title'])+'</h3></div>'+mapping+'<details><summary>展开原始条目与来源</summary><p class="atlas-muted">'+E(r['cells'][0])+'</p><div class="atlas-record-grid">'+cells+'</div><div class="atlas-sources"><b>逐项来源</b><p>'+sources+'</p>'+assets+'</div>'+latex+'</details></article>'

buttons=''.join('<button type="button" data-atlas-question="'+E(q['id'])+'" aria-pressed="false"><span>'+E(q['title'])+'</span><small>'+E(q['detail'])+'</small></button>' for q in DATA['questions'])
question_details=''.join('<div data-question-note="'+E(q['id'])+'" hidden><b>'+E(q['title'])+'</b><p><strong>对照：</strong>'+E(q['control'])+'</p><p><strong>评价：</strong>'+E(q['metrics'])+'</p></div>' for q in DATA['questions'])
tabs=''.join('<button type="button" data-atlas-view="'+v+'" aria-pressed="'+('true' if v=='datasets' else 'false')+'">'+label+'</button>' for v,label in [('datasets','数据集 → 论文'),('paper','按论文找配置'),('metric','评价指标'),('control','实验对照'),('family','原始资源索引')])
options=''.join('<option value="'+E(g['id'])+'">'+E(g['title'])+'</option>' for g in DATA['groups'])
panels='<div data-atlas-panel="datasets">'+''.join(dataset_card(d) for d in DATA['datasets'])+'</div>'
for kind in ('paper','metric','control','family'):
    panels+='<div data-atlas-panel="'+kind+'" hidden>'+''.join(record_card(r) for r in DATA['records'] if r['kind']==kind)+'</div>'
st=DATA['stats']
intro='''<div class="atlas-intro"><p><b>先问实验要区分什么，再选数据集。</b>实验问题与任务类型是两个维度，同一数据集只保留一个主条目，通过标签关联多个问题。论文名旁写清它在该研究中的用途；“基准提出”和“协议支持”不算作独立的已完成 RSI 应用。</p><div class="atlas-summary"><span>''' + str(st['dataset_entries'])+''' 个资源条目</span><span>'''+str(st['reported_applications'])+''' 条报道使用关系</span><span>60 个论文条目保留</span><span>64 类指标 · 18 类对照</span></div><p class="atlas-muted">部分条目明确归为任务家族，数量不是独立数据集总数。标签是阅读导航，不表示相关问题已在每篇论文中得到验证。原表细节保留英文，研究问题与操作提示用中文。</p></div>'''
body=intro+'<div id="experimental-atlas-app" data-source-commit="'+E(DATA['source_commit'])+'"><div class="atlas-question-grid">'+buttons+'</div><div class="atlas-question-note" aria-live="polite"><p data-question-note="all">选择一个问题收窄资源；再按任务类别或名称检索。也可以切换到逐论文、指标或对照视图。</p>'+question_details+'</div><div class="atlas-toolbar"><div class="atlas-tabs" role="group" aria-label="索引视角">'+tabs+'</div><div class="atlas-filters"><label>搜索当前视图<input type="search" id="atlas-search" placeholder="如 LoCoMo、SOAR、WebShop、遗忘…"></label><label id="atlas-group-label">任务类别<select id="atlas-group"><option value="all">全部任务类别</option>'+options+'</select></label><button type="button" id="atlas-reset">清除筛选</button><output id="atlas-count" aria-live="polite"></output></div></div><p id="atlas-empty" hidden>当前筛选没有匹配条目。清除筛选或换一个关键词；未收录对应关系不等于该研究没有使用该资源。</p><div class="atlas-results">'+panels+'</div></div>'
source='''<p><b>信息来自论文源稿，而非重新手工维护第二套表。</b>数据集—论文关系由 <code>ResourceRow / Use / Origin / Protocol</code> 生成，原有逐论文、指标、对照与资源家族条目同步保留。</p><p>论文快照：'''+link(DATA['source_repo']+'/commit/'+DATA['source_commit'],DATA['source_commit'][:12])+'''。主稿负责比较实验问题；<code>atlas.tex</code> 配套文档负责详细查找。</p><div class="links">'''+link(DATA['source_repo']+'/blob/main/main.tex','论文源稿')+' · '+link(DATA['source_repo']+'/blob/main/atlas.tex','逐论文配套文档')+' · '+link(DATA['source_repo']+'/blob/main/resources/experimental-atlas/reader-design.md','本轮分类与表格依据')+''' · <a href="experiment-catalog.json" download>下载完整索引 JSON</a></div><p>参考综述的 Table 2 用分组表头区分方法与评价；Table 4 区分数据来源与使用论文。我们借鉴这一组织方式，而不缩小字号塞入全部字段。''' +link('https://arxiv.org/abs/2404.16789v3','Shi et al., 2024')+'''。</p><p class="atlas-muted">这是文献索引，不是实验复现。代码入口不保证可运行；未提取的模型版本、预算和硬件下限不补猜。摘要级线索保留其原有边界。</p>'''
PAGE={'slug':'experimental-atlas','title':'从实验问题找到数据集与论文','en':'Experimental resources · questions, datasets, and reported uses','lead':'先从实验目的浏览资源，再查看哪些论文用过、如何使用；逐论文配置与指标字典仍可反向查找。','updated':'2026-10-31','styles':['experimental-atlas.css'],'scripts':['experimental-atlas.js'],'sections':[('browse','实验资源浏览',body),('provenance','来源与阅读分工',source)]}
