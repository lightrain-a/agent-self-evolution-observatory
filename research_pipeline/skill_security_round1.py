"""Read-only Skill-security discovery lane: evidence, collision and private proposals.

This module does not fetch/install/run Skills, invoke providers, change existing
research decisions, or promote a proposal to a vulnerability. Public projection
contains literature and attack surfaces, never unpublished candidate details.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from .skill_security_round1_sources import SOURCES,NATIVE_OBSERVATIONS,CUTOFF

ROOT=Path(__file__).resolve().parents[1]
SCOPE_FILE=ROOT/'research_pipeline'/'skill_security_round1_scope.json'
PRIORITY='PRIORITY_NATIVE_QUALIFICATION'
STATUSES={PRIORITY,'RESERVE_HIGH_COLLISION','COLLIDES_AS_STATED','KNOWN_OR_DOCUMENTED_NOT_NEW','INTERNAL_COLLISION_REVIEW','ROUND2_DEFERRED'}


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def load(path:Path):
    value=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value,dict):raise ValueError('JSON object required')
    return value


def unique(rows,key,label):
    ids=[r.get(key) for r in rows]
    if any(not isinstance(v,str) or not v for v in ids) or len(set(ids))!=len(ids):raise ValueError('missing-or-duplicate-'+label)
    return set(ids)


def validate_sources(sources=SOURCES):
    ids=unique(sources,'id','source-id')
    for source in sources:
        for field in ('title','kind','read_level','supports','does_not_establish'):
            if not source.get(field):raise ValueError('source-missing-'+field+':'+source['id'])
        if urlparse(source['url']).scheme!='https':raise ValueError('primary-source-https-required')
        if source.get('primary_source') is not True:raise ValueError('non-primary-source-in-core-corpus')
        if date.fromisoformat(source['checked_on'])>date.fromisoformat(CUTOFF):raise ValueError('future-evidence-date')
        if source.get('reproduced_by_us') is not False:raise ValueError('survey-cannot-self-certify-reproduction')
    return ids


def validate_program(program:dict):
    ids=validate_sources();surfaces=unique(program['surfaces'],'id','surface-id');ideas=program.get('ideas',[])
    unique(ideas,'id','candidate-id')
    if program['scope']['round']!=1 or program['scope']['round2']!='DEFERRED_DEFENSE_DESIGN':raise ValueError('round-boundary-changed')
    if any(program['scope']['authority'].values()):raise ValueError('discovery-cannot-authorize-execution')
    if program.get('research_executions',0)!=0 or program.get('provider_calls',0)!=0:raise ValueError('survey-counters-cannot-contain-unbound-results')
    for s in program['surfaces']:
        if not set(s['sources']).issubset(ids):raise ValueError('unknown-surface-source')
    for idea in ideas:
        if idea['status'] not in STATUSES:raise ValueError('unrecognized-candidate-status')
        if not set(idea['source_ids']).issubset(ids) or not set(idea['surfaces']).issubset(surfaces):raise ValueError('orphan-candidate-reference')
        if idea['native_reproduction']!='NOT_RUN' or idea['novelty']!='UNCONFIRMED':raise ValueError('proposal-promoted-without-evidence')
        if not idea.get('nearest_collision') or not idea.get('conditional_difference'):raise ValueError('collision-analysis-required')
        if idea['status']==PRIORITY:
            for field in ('attacker','example','hypotheses','p0','next_action','paper_boundary'):
                if not idea.get(field):raise ValueError('priority-missing-'+field)
            hypotheses=idea['hypotheses']
            if len(hypotheses)<2 or len({h['prediction'] for h in hypotheses})<2:raise ValueError('competing-distinct-predictions-required')
            p0=idea['p0']
            if not p0.get('controls') or not p0.get('measure') or not p0.get('stop'):raise ValueError('incomplete-native-test-plan')
            if p0['budget'].get('no_automatic_launch') is not True:raise ValueError('no-automatic-launch-required')
    return {'status':'PLAN_AND_REFERENCES_VALIDATED_NOT_SCIENTIFIC_PASS','sources':len(ids),'surfaces':len(surfaces),
            'ideas':len(ideas),'status_counts':dict(Counter(i['status'] for i in ideas)),
            'experiment_authority':False,'novelty_confirmed':0,'reproduced_vulnerabilities':0}


def public_state():
    spec=load(SCOPE_FILE);validate_sources()
    for s in spec['surfaces']:
        if not set(s['sources']).issubset({x['id'] for x in SOURCES}):raise ValueError('unknown-source')
    state={'schema_version':'1.0','checked_on':CUTOFF,'scope':spec['scope'],'sources':SOURCES,
           'surfaces':spec['surfaces'],'evidence_ladder':spec['evidence_ladder'],'measurement_rules':spec['measurement_rules'],
           'native_observations':NATIVE_OBSERVATIONS,'summary':{'sources':len(SOURCES),'papers':sum(s['kind']=='PAPER' for s in SOURCES),'surfaces':len(spec['surfaces']),
           'source_kinds':dict(Counter(s['kind'] for s in SOURCES)),'native_observations':len(NATIVE_OBSERVATIONS),'reproduced_vulnerabilities':0,'scientific_executions':0,'provider_calls':0},
           'private_candidates':{'published':False,'location':'Private Obsidian / explicitly supplied backend manifest','auto_import_into_canonical_idea_queue':False},
           'status':'ROUND1_SURVEY_SOURCE_AUDITED_IDEAS_PRIVATE','scientific_authority':False}
    state['snapshot_sha256']=digest(state);return state


def literature_markdown(state):
    lines=['# Skill安全第一轮：攻击面调研知识库','',f"调研截止：{CUTOFF}。本轮是资料与问题发现，不是已验证漏洞集。防御开发留到第二轮。",'',
           '## 范围与状态','',state['scope']['scientific_object'],'',
           '公开页面只有来源、攻击面与已知边界；未发表候选及验证细节保留在私有库。不是自动转载payload，也不安装攻击性Skill。','',
           '## 攻击面地图','', '| 环节 | 可信边界 | 问题 | 来源 |','|---|---|---|---|']
    for r in state['surfaces']:lines.append('| '+r['name']+' | '+r['boundary']+' | '+r['risks']+' | '+', '.join(r['sources'])+' |')
    lines+=['','## 阅读等级与证据边界','',
            'ABSTRACT_REVIEWED仅代表看过原论文摘要，不冒充逐段复核。原生文档行为不是漏洞；issue不是维护者确认；作者的扫描率不等于在野利用率。',
            '多数2026工作仍按预印本对待，只有明确核对的venue另记；本轮不比较来自不同数据/分母的ASR或F1大小。','',
            '## 文献、官方文档、实现与公告','']
    for s in state['sources']:
        lines += [f"### {s['id']} · {s['title']}",f"来源：{s['url']}",f"类型：{s['kind']}；阅读：{s['read_level']}；角色：{s.get('role','SOURCE_OR_CONTEXT')}。",
                  f"支持：{s['supports']}",f"不支持：{s['does_not_establish']}"]
        if s.get('verified_venue'):lines.append('出版状态核对：'+s['verified_venue'])
        if s.get('author_measurement'):lines.append('作者报告（未复现）：`'+json.dumps(s['author_measurement'],ensure_ascii=False)+'`')
        if s.get('commit'):lines.append('固定代码版本：`'+s['commit']+'`；内容SHA256：`'+s['content_sha256']+'`。')
        lines.append('')
    lines+=['## 原生源码/文档检查改变了什么','']
    for row in state['native_observations']:lines += [f"- {row['id']} [{', '.join(row['sources'])}] {row['observation']} 状态：{row['status']}。"]
    lines+=['','## 评测规则','']+[f"- {r}" for r in state['measurement_rules']]
    lines+=['','## 本轮局限','',
     '这是按Skill生命周期和最近邻扩展的第一轮范围调研，不宣称系统性综述已达到文献穷尽。少数工作仅摘要筛查、部分实现尚未核验发布包；这些不能被记成全文或代码复现。',
     '没有运行未知Skill、真实外传、公共目标探测、GPU训练或付费provider。当前仍为0条本轮复现漏洞；真实候选须经过原生支持资格、最小无害反例和来源查重。',
     '原生文档会变；源码仅对记录的commit成立，下一轮实验必须再次冻结实际版本。','']
    return '\n'.join(lines)


def private_markdown(program):
    audit=validate_program(program)
    lines=['# Skill安全 · 第一阶段候选与最小验证','',f"截至{CUTOFF}；仅私有研究计划，不是新漏洞通告。",'',
           '三条优先方向目前只值得做原生支持资格；可靠性来自可反驳设计，而不是先宣布新颖性。18条种子保留全部淘汰理由，不能反复改名复活。','',
           '## 汇总','',json.dumps(audit,ensure_ascii=False),'',
           '| ID | 候选 | 当前状态 |','|---|---|---|']
    lines += [f"| {r['id']} | {r['title']} | {r['status']} |" for r in program['ideas']]
    for r in program['ideas']:
        lines += ['',f"## {r['id']} · {r['title']}",f"问题：{r['question']}",f"状态：{r['status']}；新颖性UNCONFIRMED；原生复现NOT_RUN。",
                  f"最近邻：{', '.join(r['source_ids'])}。{r['nearest_collision']}",f"仅在以下差异成立时保留：{r['conditional_difference']}"]
        for key,label in [('example','例子'),('attacker','攻击者控制'),('next_action','下一项核对'),('paper_boundary','论文范围')]:
            if r.get(key):lines.append(label+'：'+r[key])
        for h in r.get('hypotheses',[]):lines.append(f"- {h['id']}：{h['claim']} 预测：{h['prediction']}")
        if r.get('p0'):
            p=r['p0'];lines += ['最小验证：'+p['units'],'预算（计划未执行）：`'+json.dumps(p['budget'],ensure_ascii=False)+'`',
                               '对照：'+'；'.join(p['controls']),'观测：'+'；'.join(p['measure']),'停止/降级：'+p['stop']]
    lines+=['','## 下一步的唯一科学推进顺序','',
     '优先SS-R1-01的原生合同/版本矩阵；SS-R1-02/03先核查真实事件schema，若实际同一根因则合并。不要同时启动18个实验。',
     'Q0：零provider读取和本地环境资格 → P0：无害原生反例与matched controls → 冻结主要端点/数据身份 → 独立任务与宿主确认。',
     '第一轮不为了论文形式加入新防御；只保留现成防御或简单规则作为鉴别根因的对照。第二轮基于实际漏洞类别再设计机制。',
     '内部查重：既有表示/检索线、persistent agent safety线和embodied authorization线保持原身份。本次不修改它们的裁决或把通用借鉴算新论文。','']
    return '\n'.join(lines)


def candidate_packet(program,idea_id):
    validate_program(program);r=next((i for i in program['ideas'] if i['id']==idea_id),None)
    if not r:raise ValueError('unknown-candidate')
    if r['status']!=PRIORITY:raise ValueError('candidate-not-prioritized-for-native-qualification')
    from .discovery_method_formation import formation_shape,normalize_formation
    shape=formation_shape();shape.update(intuition=r['conditional_difference'],example=r['example'],
        observation={'claim':'已核对的是文档/源码所描述的边界差异；不是已观测攻击成功。','scope':r['paper_boundary'],'evidence_refs':r['source_ids']},
        system={'object':'Skill包、宿主授权记录与实际副作用','update':'原生导入/激活或版本化载入，不修改模型','feedback':'官方语义、原生事件和独立策略真值','selection':'对照冻结的无害fixture，避免模型随机路由混淆','deployment_shift':'宿主/调用阶段/观测接口的显式差分','budget':r['p0']['units']},
        analogies=[],no_analogy_reason='访问控制域、混淆代理和可观测性为成熟原语；没有证据把跨域改名当新机制。',
        hypotheses=[{'id':h['id'],'kind':'MECHANISM' if n==0 else 'ALTERNATIVE','claim':h['claim'],'scope':r['paper_boundary'],'prediction':h['prediction'],'falsifier':r['p0']['stop'],'evidence_refs':r['source_ids']} for n,h in enumerate(r['hypotheses'])],
        claim_boundary=r['paper_boundary'],prospective_requirement='原生资格和最小反例后再冻结宿主版本、任务/来源身份与统计端点；未通过不得进入确认性科学实验。')
    shape['p0']={'mode':'NEW_EXECUTIONS','intervention':r['question'],'controls':r['p0']['controls'],
      'comparator':'同任务无Skill、显式授权相同动作、完整来源/事件对照及当前修复版本','observable':'; '.join(r['p0']['measure']),
      'hypothesis_predictions':{h['id']:h['prediction'] for h in r['hypotheses']},'data_source':'PENDING_NATIVE_FIXTURE_MANIFEST',
      'budget':{'candidates':None,'tasks':None,'repeats':None,'provider_calls_per_evaluation':None,'retry_call_allowance':0,'max_new_calls':0,'estimated_wall_seconds':None,'estimate_basis':'原生fixture预算另列；新增模型调用须独立授权，不编造时长。'},
      'decision_rule':'真实原生入口和政策真值匹配后检查边界差分；不能从文档直接宣告成功。',
      'inconclusive_rule':'缺原生入口/未触发/日志不完整分别SUPPORT_HOLD；不是科学失败或安全结论。',
      'integrity_checks':program['native_gate'],'stop_rule':r['p0']['stop']}
    packet={'candidate_id':r['id'],'lane':program['scope']['id'],'status':'DISCOVERY_ONLY_NATIVE_QUALIFICATION_PENDING',
            'method_formation':normalize_formation(shape),'native_plan':r['p0'],'nearest_work':r['nearest_collision'],
            'core_source_ids':r['source_ids'],'source_records':[s for s in SOURCES if s['id'] in r['source_ids']],
            'automatic_promotion':False,'scientific_authority':False,'provider_authority':False}
    packet['packet_sha256']=digest(packet);return packet


def write_public(root=ROOT):
    state=public_state();(root/'generated').mkdir(parents=True,exist_ok=True);(root/'docs').mkdir(parents=True,exist_ok=True)
    (root/'generated'/'skill-security-round1.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (root/'generated'/'skill-security-round1.js').write_text('window.SKILL_SECURITY_ROUND1='+json.dumps(state,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    (root/'docs'/'skill-security-round1-survey.md').write_text(literature_markdown(state),encoding='utf-8')
    return state


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--private-program',type=Path);p.add_argument('--output',type=Path);p.add_argument('--candidate');p.add_argument('--public',action='store_true');a=p.parse_args()
    if a.public or not a.private_program:
        result=write_public();print(json.dumps(result['summary'],ensure_ascii=False));return
    program=load(a.private_program);audit=validate_program(program)
    if not a.output:p.error('--private-program requires --output outside public source tree')
    dest=a.output.resolve()
    if dest.is_relative_to(ROOT.resolve()):raise ValueError('private-export-cannot-enter-public-repository')
    dest.mkdir(parents=True,exist_ok=True)
    if a.candidate:
        value=candidate_packet(program,a.candidate);(dest/(a.candidate+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:
        (dest/'00-source-survey.md').write_text(literature_markdown(public_state()),encoding='utf-8')
        (dest/'01-private-ideas.md').write_text(private_markdown(program),encoding='utf-8')
        (dest/'research-program.json').write_text(json.dumps(program,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (dest/'validation-receipt.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=False))

if __name__=='__main__':main()
