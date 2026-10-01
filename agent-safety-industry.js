/* Read-only official problem leads; no approval or experiment actions. */
(() => {
 'use strict';
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const $=id=>document.getElementById(id);
 let data,sources;
 const statuses={ADDRESSED_WITH_SCOPE:'已有解法，检查适用边界',DOCUMENTED_LIMITATION:'官方明确使用限制',REPORTED_TRADEOFF:'公开的工程权衡',ONGOING_IN_SOURCE:'原文明确的持续挑战'};
 function render(){
  const company=$('industry-company').value;
  const rows=data.industry.signals.filter(s=>!company||s.company===company);
  $('industry-count').textContent=`${rows.length}条问题线索 / ${data.industry_counts.companies}家机构；资料核对${data.industry.checked_on}。官方已处理的部分和我们的追问分开。`;
  $('industry-grid').innerHTML=rows.map(s=>`<article class="industry-card" data-industry-id="${esc(s.id)}"><div class="card-top"><span class="pid">${esc(s.company)}</span><span class="badge">${esc(statuses[s.status])}</span></div><h3>${esc(s.title)}</h3><div class="example"><small>先看一个例子 · 解释，不是新漏洞</small>${esc(s.example)}</div><div class="industry-fact"><b>官方公开的问题</b><p>${esc(s.public_problem)}</p></div><div class="industry-fact"><b>已经做了什么</b><p>${esc(s.already_addressed)}</p></div><details><summary>看适用边界、待核对问题与原文</summary><div class="industry-boundary"><b>不能直接外推什么</b><p>${esc(s.boundary)}</p><b>我们可以继续核对的问题 · 不是已确认idea</b><p>${esc(s.research_question)}</p><small>${esc(s.claim_type)} · ${esc(s.directness)}</small></div>${s.source_refs.map(id=>{const p=sources[id];return `<div class="industry-source"><a href="${esc(p.url)}" target="_blank" rel="noopener noreferrer"><b>${esc(p.label)}</b> ${esc(p.title)} ↗</a><p>${esc(p.locator)}</p><small>${esc(p.statement)}</small></div>`;}).join('')}</details><div class="source-problems">回到相关难点：${s.problem_ids.map(id=>`<button type="button" data-industry-problem="${esc(id)}">${esc(id)}</button>`).join('')}</div></article>`).join('');
 }
 document.addEventListener('flow-idea-atlas-ready',event=>{
  data=event.detail;if(!data.industry)return;
  sources=Object.fromEntries(data.industry.sources.map(s=>[s.id,s]));
  const companies=[...new Set(data.industry.signals.map(s=>s.company))];
  $('industry-company').innerHTML='<option value="">全部机构</option>'+companies.map(c=>`<option>${esc(c)}</option>`).join('');
  $('industry-disambiguation').innerHTML=`<b>“DeepSeek组件耦合”先查清指什么</b><p>${esc(data.industry.disambiguation.explanation)}</p><a href="${esc(sources['IND-S01'].url)}" target="_blank" rel="noopener noreferrer">查看最贴近的原始论文：${esc(sources['IND-S01'].label)} ↗</a>`;
  render();
 });
 $('industry-company').addEventListener('change',()=>{if(data)render();});
 $('industry-grid').addEventListener('click',event=>{
  const b=event.target.closest('[data-industry-problem]');if(b)document.dispatchEvent(new CustomEvent('flow-idea-open-problem',{detail:b.dataset.industryProblem}));
 });
})();
