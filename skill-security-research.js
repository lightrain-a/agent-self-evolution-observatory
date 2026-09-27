(() => {
  'use strict';
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const state=window.SKILL_SECURITY_ROUND1;
  const root=document.getElementById('skill-security-main');
  if(!state){root.textContent='知识库数据暂未加载，请刷新或查阅仓库文档。';return}
  const sources=Object.fromEntries(state.sources.map(s=>[s.id,s]));
  const stageNames={package:'包与来源',discovery:'发现',selection:'检索选择',activation:'激活预处理',authorization:'授权',execution:'执行',secrets:'数据与密钥',delegation:'委托',persistence:'持久化',update:'更新',revocation:'撤销',availability:'资源消耗',audit:'审计评测',governance:'治理',tool_boundary:'工具边界',authoring:'产生与演化',disclosure:'披露'};
  const sourceLinks=ids=>ids.map(id=>`<a href="#source-${esc(id)}">${esc(id)}</a>`).join(' · ');
  root.innerHTML=`<section class="prep-hero"><div class="eyebrow">SKILL SECURITY · ROUND 1 · ${esc(state.checked_on)}</div><h1>先弄清攻击面，再设计防御</h1><p>研究Skill从被获取到产生实际副作用，来源、权限、数据和执行边界如何衔接。第一轮是文献与原生语义调研、Idea发现；第二轮防御机制暂不启动。</p><div class="prep-flow"><span><b>${state.summary.sources}</b>一手来源</span><span><b>${state.summary.papers}</b>论文</span><span><b>${state.summary.surfaces}</b>攻击面类别</span><span><b>0</b>本轮复现漏洞</span><span><b>0</b>模型/GPU实验</span></div></section>
    <section class="notice"><b>资料已核对，不等于新漏洞已证明。</b><p>每个来源标出阅读深度、能支持什么、不能推出什么。官方说明的高权限行为、可疑扫描特征、已修复公告、公开issue和真实边界漏洞分别记录。未发表Idea及验证细节保留在私有Obsidian和后端，不在此公开。</p></section>
    <section><h2>完整攻击面地图</h2><div class="security-surface-grid">${state.surfaces.map(s=>`<article><h3>${esc(s.id)} · ${esc(s.name)}</h3><p><b>边界：</b>${esc(s.boundary)}</p><p>${esc(s.risks)}</p><p><b>核对方式：</b>${esc(s.control)}</p><small>${sourceLinks(s.sources)}</small></article>`).join('')}</div></section>
    <section><h2>原生文档与源码让哪些直觉需要收窄？</h2>${state.native_observations.map(n=>`<article class="security-source"><h3>${esc(n.id)} · ${esc(n.status)}</h3><p>${esc(n.observation)}</p><small>${sourceLinks(n.sources)} · 不是本轮漏洞回执</small></article>`).join('')}</section>
    <section id="bibliography"><h2>文献、实现、标准与公告</h2><p>按标题、机制、来源ID或问题检索。摘要筛查不冒充全文复核；作者报告的统计不冒充我们的复现。多数2026工作仍作为预印本处理，明确核对的出版信息另列。</p><div class="security-controls"><input id="security-query" type="search" placeholder="Skill-Inject / permission / 数据泄露 / P16"><select id="security-stage"><option value="">全部生命周期</option>${Object.entries(stageNames).map(([k,v])=>`<option value="${esc(k)}">${esc(v)}</option>`).join('')}</select><select id="security-kind"><option value="">全部来源类型</option>${[...new Set(state.sources.map(s=>s.kind))].map(k=>`<option>${esc(k)}</option>`).join('')}</select></div><p id="security-count"></p><div id="security-sources">${state.sources.map(s=>`<article class="security-source" id="source-${esc(s.id)}" data-source-id="${esc(s.id)}"><h3><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.id)} · ${esc(s.title)}</a></h3><small>${esc(s.kind)} · ${esc(s.read_level)} · checked ${esc(s.checked_on)}</small><div>${s.stages.map(v=>`<span class="security-stage">${esc(stageNames[v]||v)}</span>`).join('')}</div><p><b>支持：</b>${esc(s.supports)}</p><p><b>不能推出：</b>${esc(s.does_not_establish)}</p>${s.verified_venue?`<p>出版信息：${esc(s.verified_venue)}</p>`:''}${s.author_measurement?`<details><summary>作者报告的样本信息（本轮未复现）</summary><pre>${esc(JSON.stringify(s.author_measurement,null,2))}</pre></details>`:''}${s.commit?`<p>固定版本：<code>${esc(s.commit)}</code></p>`:''}</article>`).join('')}</div></section>
    <section><h2>候选需要走过的证据阶梯</h2><div class="security-surface-grid">${state.evidence_ladder.map(l=>`<article><h3>${esc(l.stage)} · ${esc(l.name)}</h3><p>${esc(l.requires)}</p></article>`).join('')}</div></section>
    <details><summary>实验指标与标签规则</summary>${state.measurement_rules.map(r=>`<p>${esc(r)}</p>`).join('')}<p>第一轮仅允许在授权本地沙箱中以无害标记验证。不会自动安装未知Skill、执行恶意代码、访问真实凭据、向外部接收方发数据或测试公共目标。</p></details>
    <section><h2>完整知识资产</h2><div class="prep-actions"><a href="generated/skill-security-round1.json" download>公开来源与攻击面 JSON</a><a href="https://github.com/lightrain-a/agent-self-evolution-observatory/blob/main/docs/skill-security-round1-survey.md">逐条文献笔记</a><a href="https://github.com/lightrain-a/agent-self-evolution-observatory/blob/main/docs/skill-security-round1.md">接入与使用说明</a></div><p>本轮为按生命周期和最近邻扩展的范围调研，不宣称文献穷尽；没有复现的实现与尚未核验的数据包保留明确状态。候选详细差异、反证条件和私有研究计划不包含在上述公开JSON内。</p></section>`;
  const inputs=['security-query','security-stage','security-kind'].map(id=>document.getElementById(id));
  function filter(){
    const q=inputs[0].value.toLowerCase().trim(),stage=inputs[1].value,kind=inputs[2].value;let count=0;
    document.querySelectorAll('[data-source-id]').forEach(node=>{
      const s=sources[node.dataset.sourceId];const text=[s.id,s.title,s.supports,s.does_not_establish].join(' ').toLowerCase();
      const show=(!q||text.includes(q))&&(!stage||s.stages.includes(stage))&&(!kind||s.kind===kind);node.hidden=!show;if(show)count++;
    });
    document.getElementById('security-count').textContent=`显示 ${count} / ${state.sources.length} 条来源`;
  }
  inputs.forEach(input=>input.addEventListener(input.tagName==='INPUT'?'input':'change',filter));filter();
})();
