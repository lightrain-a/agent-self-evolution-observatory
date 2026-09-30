/* Public reading interface only. No approval or experiment write endpoint. */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let data, sources, problems, view = 'map', selected = new Set();
  const storageKey = 'flow-idea-problem-atlas-shortlist-v1';
  const feedback = (message) => { $('selection-feedback').textContent = message; };
  function saveSelection() {
    try { localStorage.setItem(storageKey, JSON.stringify({revision: data.revision, ids: [...selected]})); }
    catch (_) { feedback('浏览器不允许本地保存；这次选择仍可复制，但刷新后可能丢失。'); }
  }
  function choice(p) {
    return `<label class="choose"><input type="checkbox" data-select="${esc(p.id)}" ${selected.has(p.id) ? 'checked' : ''}><span>加入待选</span></label>`;
  }
  function sourceLinks(refs) {
    return refs.map(id => `<a class="source-chip" href="${esc(sources[id].url)}" target="_blank" rel="noopener noreferrer">${esc(sources[id].title)} ↗</a>`).join('');
  }
  function filtered() {
    const query = $('query').value.trim().toLowerCase();
    return data.problems.filter(p => (!$('theme-filter').value || p.theme_id === $('theme-filter').value) &&
      (!$('status-filter').value || p.status === $('status-filter').value) && (!query ||
      [p.id,p.title,p.example,p.why_hard,p.contexts,...p.source_refs.map(id=>sources[id].title)].join(' ').toLowerCase().includes(query)));
  }
  function render() {
    const rows = filtered();
    $('count').textContent = `当前显示 ${rows.length} / ${data.problems.length} 个难点 · 资料覆盖不等于风险大小，列表顺序不代表推荐排名。`;
    document.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === view)));
    ['map','list','coverage'].forEach(v => { $(v+'-view').hidden = v !== view; });
    $('map-view').innerHTML = data.themes.filter(t => rows.some(p => p.theme_id === t.id)).map(t => {
      const count = rows.filter(p=>p.theme_id===t.id).length;
      return `<button class="theme-card" data-theme="${esc(t.id)}"><span class="theme-top"><span class="theme-id">${esc(t.id)}</span><span class="theme-stage">${esc(t.stage)}</span></span><h3>${esc(t.title)}</h3><p>${esc(t.subtitle)}</p><span class="theme-bottom"><span>${count} 个难点，进入阅读 →</span><span class="${t.coverage==='待补查'?'coverage-gap':''}">${esc(t.coverage)}</span></span></button>`;
    }).join('') || '<div class="empty">没有匹配项。可以清除筛选，或换一个具体词，例如“记忆”或“权限”。</div>';
    $('list-view').innerHTML = rows.map(p=>`<article class="problem-card"><div class="card-top"><span class="pid">${esc(p.id)} · ${esc(p.contexts)}</span><span class="badge">${esc(p.status)}</span></div><h3>${esc(p.title)}</h3><div class="example"><small>先看一个例子 · 假设场景</small>${esc(p.example)}</div><p class="card-value"><b>为什么值得关心</b>　${esc(p.why_it_matters)}</p><div class="card-bottom"><button class="detail-link" data-detail="${esc(p.id)}">已有研究做到了哪？　↗</button>${choice(p)}</div></article>`).join('') || '<div class="empty">没有匹配项；不代表这一领域没有研究。</div>';
    renderSelection();
  }
  function renderSelection() {
    $('selection-count').textContent = String(selected.size);
    $('compare').disabled = selected.size < 2;
    $('copy-selection').disabled = !selected.size;
    $('download-selection').disabled = !selected.size;
    $('selection-items').innerHTML = [...selected].map(id=>`<div class="selection-row"><b>${esc(id)}</b><button class="detail-link" data-detail="${esc(id)}">${esc(problems[id].title)}</button><button data-remove="${esc(id)}" aria-label="移除${esc(id)}">移除</button></div>`).join('') || '<p class="muted">还没有选择。可以从主题进入，或直接逐项阅读。</p>';
    document.querySelectorAll('[data-select]').forEach(el => { el.checked = selected.has(el.dataset.select); });
  }
  function showProblem(id) {
    const p = problems[id]; if (!p) return;
    const relations = data.relations.filter(e=>e.from===id || e.to===id);
    $('detail-body').innerHTML = `<span class="pid">${esc(p.id)} · ${esc(p.contexts)}</span><h2 id="detail-title">${esc(p.title)}</h2><div class="example"><small>解释性假设场景，不是本轮复现结果</small>${esc(p.example)}</div><section class="detail-section"><h3>为什么值得关心</h3><p>${esc(p.why_it_matters)}</p></section><section class="detail-section"><h3>难在哪里 · 研究者概括</h3><p>${esc(p.why_hard)}</p></section><section class="detail-section"><h3>已有研究已经做到什么</h3><p>${esc(p.existing_progress)}</p>${sourceLinks(p.source_refs)}<p class="muted">${p.source_refs.map(id=>`${esc(sources[id].title)}：${esc(sources[id].read_level)}`).join('；')}。这里没有宣称完成全文复现。</p></section><section class="detail-section"><h3>仍需要问清楚什么 · 待核验，不是已确认创新</h3><p class="inference">${esc(p.open_question)}</p></section><section class="detail-section"><h3>与哪些问题相连</h3>${relations.map(e=>{const other=e.from===id?e.to:e.from;return `<button class="relation-item" data-detail="${esc(other)}">${esc(other)} · ${esc(problems[other].title)}<br><small>${esc(e.label)}</small></button>`;}).join('') || '<p class="muted">暂未整理到直接关联，不代表没有关系。</p>'}<p class="muted">这些连接帮助理解问题，不是经过实验验证的因果图。</p></section><div class="detail-select">${choice(p)}<p class="muted">先确认是否值得研究，再找可能方案。勾选不会启动任务。</p></div>`;
    const d=$('detail-dialog'); if (!d.open) d.showModal();
  }
  function renderCoverage() {
    $('coverage-view').innerHTML = `<div class="scroll-table"><table><thead><tr><th>问题主题</th><th>相关论文 / 文档</th><th>资料覆盖判断</th><th>还缺什么</th></tr></thead><tbody>${data.themes.map(t=>{
      const ids=new Set(data.problems.filter(p=>p.theme_id===t.id).flatMap(p=>p.source_refs));
      const papers=[...ids].filter(id=>sources[id].kind==='paper').length;
      return `<tr><th>${esc(t.id)} · ${esc(t.title)}</th><td>${papers} 篇论文 / ${ids.size-papers} 份文档</td><td>${esc(t.coverage)}</td><td>${esc(t.coverage_note)}</td></tr>`;
    }).join('')}</tbody></table></div><p class="muted">覆盖度是编者对当前材料的判断，不是定量安全评分。同一来源可支持多个主题，不能将各行数量相加当成独立论文数。</p><h3>哪些地方仍需要补查？</h3><div class="coverage-grid">${data.coverage_gaps.map(g=>`<article class="coverage-note"><h3>${esc(g.area)}</h3><p>${esc(g.reason)}</p></article>`).join('')}</div><div class="coverage-note" style="margin-top:18px"><h3>“尽量全面”怎么落实？</h3><p>按工作环节和风险后果交叉检查；相关论文、官方规范与反例互相补充；未覆盖的入口公开标注。第二阶段先补选中问题的关键证据，再比较可能方案，而不是把尚未查到的地方直接叫创新空白。</p></div>`;
  }
  function shortlistText() {
    return `难点地图版本：${data.checked_on} / ${data.revision.slice(0,12)}\n\n我希望先确认以下研究难点：\n${[...selected].map(id=>`${id}：${problems[id].title}`).join('\n')}\n\n请先核对这些难点的已有工作和价值，确认后进入方案调研；不要直接开始预实验。\n（网页待选清单；正式确认以我在聊天中明确给出的指令为准。）`;
  }
  function compare() {
    const items=[...selected].slice(0,4).map(id=>problems[id]);
    const fields=[['先看一个例子','example'],['价值','why_it_matters'],['难在哪里','why_hard'],['已有进展','existing_progress'],['待回答问题','open_question'],['场景','contexts'],['当前性质','status']];
    $('compare-body').innerHTML=`${selected.size>4?'<p class="muted">为保持可读，本次比较清单前4项；可以移除或调整后再比较。</p>':''}<div class="scroll-table"><table><thead><tr><th>比较什么</th>${items.map(p=>`<th>${esc(p.id)}<br>${esc(p.title)}</th>`).join('')}</tr></thead><tbody>${fields.map(([label,key])=>`<tr><th>${label}</th>${items.map(p=>`<td>${esc(p[key])}</td>`).join('')}</tr>`).join('')}<tr><th>一手依据</th>${items.map(p=>`<td>${sourceLinks(p.source_refs)}</td>`).join('')}</tr></tbody></table></div>`;
    $('compare-dialog').showModal();
  }
  async function initialize() {
    try {
      const response=await fetch('generated/agent-safety-atlas.json', {cache:'no-cache'});
      if(!response.ok) throw new Error('Map not available'); data=await response.json();
      if(data.schema_version!==1 || !Array.isArray(data.problems) || !data.revision) throw new Error('Unsupported map');
      sources=Object.fromEntries(data.sources.map(s=>[s.id,s])); problems=Object.fromEntries(data.problems.map(p=>[p.id,p]));
      const papers=data.sources.filter(s=>s.kind==='paper').length;
      $('hero-stats').innerHTML=`<div><b>${data.problems.length}</b><small>研究难点</small></div><div><b>${papers}</b><small>一手论文</small></div><div><b>${data.sources.length-papers}</b><small>官方文档</small></div>`;
      $('scope').textContent=data.scope+' '+data.coverage_statement;
      $('theme-filter').insertAdjacentHTML('beforeend',data.themes.map(t=>`<option value="${esc(t.id)}">${esc(t.id)} · ${esc(t.title)}</option>`).join(''));
      $('survey-steps').innerHTML=data.survey_method.map(s=>`<article class="survey-step"><h3>${esc(s.step)} <small>${esc(s.state)}</small></h3><p>${esc(s.detail)}</p></article>`).join('');
      $('source-count').textContent=`· ${data.sources.length} 项`;
      $('source-list').innerHTML=data.sources.map(s=>`<article class="source-entry" id="source-${esc(s.id)}"><span class="pid">${esc(s.id)}</span><div><h3><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)} ↗</a></h3><span class="source-meta">${esc(s.publication)} · ${esc(s.read_level)} · 核对 ${esc(s.checked_on)}</span><p>${esc(s.supports)}</p><p class="source-meta">${esc(s.limits)}</p></div></article>`).join('');
      $('version-note').textContent=`来源核对：${data.checked_on} · 地图版本 ${data.revision.slice(0,12)} · 暂无已确认难点和方案。不是对全领域的穷尽调查。`;
      try {
        const saved=JSON.parse(localStorage.getItem(storageKey)||'null');
        if(saved?.revision===data.revision && Array.isArray(saved.ids)) selected=new Set(saved.ids.filter(id=>problems[id]));
        else if(saved?.ids?.length) feedback('地图已更新：旧版本清单未被自动沿用，请重新核对后选择。');
      } catch (_) { feedback('本地清单不可用；仍可阅读、比较和复制本次选择。'); }
      renderCoverage(); render();
      const id=location.hash.replace('#problem-',''); if(problems[id]) showProblem(id);
    } catch(error) { $('load-error').hidden=false; $('hero-stats').textContent='资料暂未加载'; }
  }
  document.addEventListener('click',event=>{
    const element=event.target.closest('button'); if(!element || !data) return;
    if(element.dataset.view){view=element.dataset.view;render();}
    if(element.dataset.theme){$('theme-filter').value=element.dataset.theme;view='list';render();}
    if(element.dataset.detail) showProblem(element.dataset.detail);
    if(element.dataset.remove){selected.delete(element.dataset.remove);saveSelection();renderSelection();}
    if(element.classList.contains('dialog-close')) element.closest('dialog').close();
  });
  document.addEventListener('change',event=>{
    const id=event.target.dataset.select;if(!id || !problems[id]) return;
    if(event.target.checked) selected.add(id); else selected.delete(id);
    saveSelection();renderSelection();
  });
  ['query','theme-filter','status-filter'].forEach(id=>$(id).addEventListener(id==='query'?'input':'change',()=>{if(data)render();}));
  $('reset').addEventListener('click',()=>{['query','theme-filter','status-filter'].forEach(id=>$(id).value='');if(data)render();});
  $('clear-selection').addEventListener('click',()=>{selected.clear();saveSelection();renderSelection();feedback('本机清单已清空；没有改动服务器研究状态。');});
  $('compare').addEventListener('click',compare);
  $('copy-selection').addEventListener('click',async()=>{
    const text=shortlistText();try{await navigator.clipboard.writeText(text);feedback('已复制。请粘贴到当前聊天，由你明确确认后再进入方案阶段。');}
    catch(_){$('copy-fallback').hidden=false;$('copy-fallback').value=text;$('copy-fallback').select();feedback('请复制下面文字到当前聊天。没有提交服务器审批。');}
  });
  $('download-selection').addEventListener('click',()=>{
    const value={intent:'REVIEW_DRAFT_NOT_CONFIRMATION',atlas_revision:data.revision,problem_ids:[...selected],items:[...selected].map(id=>({id,title:problems[id].title})),experiment_authority:false};
    const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download='agent-safety-problem-shortlist.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    feedback('已导出待选清单，不是正式确认或实验授权。');
  });
  initialize();
})();
