/* Focused paper-reading recommendations. Copying a draft never confirms research. */
(() => {
 'use strict';
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const $=id=>document.getElementById(id);
 let review,readings;
 const refs=ids=>ids.map(id=>`<a class="source-chip" href="${esc(readings[id].url)}" target="_blank" rel="noopener noreferrer"><small>${esc(readings[id].label)}</small>${esc(readings[id].title)} ↗</a>`).join('');
 function draft(id){
  const q=review.questions.find(q=>q.id===id && q.selectable);if(!q)return null;
  return `我确认下一步先研究问题 ${q.id}：${q.title}\n问题表述版本：${review.revision}\n对应原地图：${q.problem_ids.join('、')}\n请先比较该问题的已有方案与可行方案，不直接启动预实验。方案仍需我第二次确认。\n（这是网页生成的待发送草稿；只有我在聊天中明确发送此选择，才构成确认。）`;
 }
 function render(){
  $('review-intro').textContent=review.summary;
  $('review-scope').textContent=review.scope;
  $('review-questions').innerHTML=review.questions.map(q=>`<article class="review-question ${q.selectable?'':'review-deferred'}" data-review-id="${esc(q.id)}"><div class="card-top"><span class="pid">${esc(q.id)}</span><span class="review-recommendation">${esc(q.recommendation)}</span></div><h3>${esc(q.title)}</h3><div class="example"><small>解释性例子 · 不是已观察的漏洞</small>${esc(q.example)}</div><p class="review-value"><b>解决后有什么价值</b><br>${esc(q.value)}</p><p class="review-existing"><b>不能忽略的已有工作</b><br>${esc(q.what_already_exists)}</p><details><summary>为什么这样收敛？看依据与反对理由</summary><div class="review-details"><h4>更具体地问</h4><p>${esc(q.sharper_question)}</p><h4>为什么值得考虑</h4><p>${esc(q.positive_basis)}</p><h4>最强的反对理由</h4><p>${esc(q.nearest_challenge)}</p><h4>目前还缺什么证据</h4><p>${esc(q.missing_evidence)}</p><h4>怎样判断是否继续</h4><p>${esc(q.decision_rule)}</p><h4>直接依据</h4>${refs(q.source_refs)}</div></details><div class="review-actions">${q.selectable?`<button type="button" data-review-draft="${esc(q.id)}">复制问题确认草稿</button>`:'<span class="muted">不为宽泛主张单独启动方案或实验。</span>'}<div class="source-problems">原地图：${q.problem_ids.map(id=>`<button data-review-problem="${esc(id)}">${esc(id)}</button>`).join('')}</div></div></article>`).join('');
  $('review-corrections').innerHTML=review.corrections.map(c=>`<article><h4>原先的表述</h4><p>${esc(c.before)}</p><h4>读原文后改成</h4><p>${esc(c.after)}</p><small>${esc(c.scope)}</small>${refs(c.source_refs)}</article>`).join('');
  $('review-reading-list').innerHTML=review.readings.map(r=>`<article class="review-reading"><div><span class="pub-badge">${esc(r.label)}</span><h4><a href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">${esc(r.title)} ↗</a></h4><p class="muted">${esc(r.version_note)} · ${esc(r.read_scope)}</p></div><dl><dt>问题</dt><dd>${esc(r.problem)}</dd><dt>核心机制</dt><dd>${esc(r.mechanism)}</dd><dt>证据是什么</dt><dd>${esc(r.evidence)}</dd><dt>不应外推什么</dt><dd>${esc(r.limitations)}</dd></dl><div class="review-anchor-links">${r.reading_anchors.map(a=>`<a href="${esc(a.url)}" target="_blank" rel="noopener noreferrer">${esc(a.label)} ↗</a>`).join('')}</div><small>阅读归纳，不是我们的实验结果；未重跑作者实验，也未核验全部形式证明。</small></article>`).join('');
 }
 document.addEventListener('flow-idea-atlas-ready',event=>{
  review=event.detail.problem_review;if(!review)return;
  readings=Object.fromEntries(review.readings.map(r=>[r.id,r]));render();
 });
 $('review-questions').addEventListener('click',async event=>{
  const link=event.target.closest('[data-review-problem]');if(link)document.dispatchEvent(new CustomEvent('flow-idea-open-problem',{detail:link.dataset.reviewProblem}));
  const button=event.target.closest('[data-review-draft]');if(!button||!review)return;
  const text=draft(button.dataset.reviewDraft);if(!text)return;
  $('review-draft-text').value=text;$('review-draft-text').hidden=false;
  try{await navigator.clipboard.writeText(text);$('review-feedback').textContent='已复制待发送草稿。请在聊天中核对并明确发送；网页没有记录任何正式确认。';}
  catch(_){$('review-draft-text').select();$('review-feedback').textContent='请复制下面的草稿，在聊天中核对后发送。网页没有提交审批，也未启动任务。';}
 });
})();
