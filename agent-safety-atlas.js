/* Public reading interface only. No approval or experiment write endpoint. */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let data, sources, problems, view = 'map', selected = new Set(), sourceLimit = 12;
  const storageKey = 'flow-idea-problem-atlas-shortlist-v1';
  const feedback = (message) => { $('selection-feedback').textContent = message; };
  function saveSelection() {
    try { localStorage.setItem(storageKey, JSON.stringify({revision: data.revision, ids: [...selected]})); }
    catch (_) { feedback('浏览器不允许本地保存；这次选择仍可复制，但刷新后可能丢失。'); }
  }
  function choice(p) {
    return `<label class="choose"><input type="checkbox" data-select="${esc(p.id)}" ${selected.has(p.id) ? 'checked' : ''}><span>加入待选</span></label>`;
  }
  const groupOf = (s) => s.kind !== 'paper' ? 'documentation' : (s.publication_status || 'preprint');
  const groupLabel = (s) => ({published_verified:'已核验发表',preprint:'预印本补充',indexed_unverified:'发表待核实',documentation:'官方文档'}[groupOf(s)]);
  function sourceLinks(refs) {
    const make = id => {
      const s=sources[id];
      return `<a class="source-chip pub-${esc(groupOf(s))}" href="${esc(s.url)}" target="_blank" rel="noopener noreferrer"><small>${esc(s.publication || groupLabel(s))}</small>${esc(s.title)} ↗</a>`;
    };
    const first=refs.slice(0,6).map(make).join('');
    return first+(refs.length>6?`<details class="more-references"><summary>展开其余 ${refs.length-6} 项依据</summary>${refs.slice(6).map(make).join('')}</details>`:'');
  }
  function sourceYear(s) { return s.published_year || s.first_posted_year || s.semantic_scholar?.indexed_year || ''; }
  function renderSources() {
    const status=$('source-status').value, year=$('source-year').value, query=$('source-query').value.trim().toLowerCase();
    const matches=data.sources.filter(s=>(status==='all'||groupOf(s)===status)&&(!year||String(sourceYear(s))===year)&&
      (!query||[s.title,s.publication,s.supports,...data.problems.filter(p=>p.source_refs.includes(s.id)).map(p=>p.id+' '+p.title)].join(' ').toLowerCase().includes(query)));
    $('source-results').textContent=`共 ${matches.length} 项，当前展示 ${Math.min(sourceLimit,matches.length)} 项。正式记录按发表年份降序；预印本年份与索引年份单独解释。`;
    $('source-list').innerHTML=matches.slice(0,sourceLimit).map(s=>{
      const proof=s.publication_verification;
      const related=data.problems.filter(p=>p.source_refs.includes(s.id));
      const yearNote=s.published_year&&s.semantic_scholar?.indexed_year&&s.published_year!==s.semantic_scholar.indexed_year ? ` · Scholar索引年份 ${s.semantic_scholar.indexed_year}，正式发表 ${s.published_year}`:'';
      return `<article class="source-entry" id="source-${esc(s.id)}" data-publication-status="${esc(groupOf(s))}" data-publication-year="${esc(s.published_year||'')}"><span class="pid">${esc(s.id)}</span><div><div class="source-heading"><span class="pub-badge pub-${esc(groupOf(s))}">${esc(groupLabel(s))}</span><span class="source-meta">${esc(s.publication)}</span></div><h3><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)} ↗</a></h3><p>${esc(s.supports)}</p><p class="source-meta">${esc(s.read_level)} · 核对 ${esc(s.checked_on)}${esc(yearNote)}</p>${s.relevance_role==='adjacent'?`<p class="adjacent-note">邻近背景：不把该论文当作目标系统的直接安全证明。</p>`:''}<div class="source-evidence-links">${proof?.status==='verified'?`<a href="${esc(proof.primary_url)}" target="_blank" rel="noopener noreferrer">查看正式出处 ↗</a>`:''}${(s.aliases||[]).filter(u=>u!==s.url).slice(0,1).map(u=>`<a href="${esc(u)}" target="_blank" rel="noopener noreferrer">原版本 ↗</a>`).join('')}</div><div class="source-problems">对应难点：${related.map(p=>`<button data-detail="${esc(p.id)}" title="${esc(p.title)}">${esc(p.id)}</button>`).join('')}</div></div></article>`;
    }).join('')||'<p class="empty">当前筛选没有条目，不代表该领域没有已发表研究。</p>';
    $('source-more').hidden=sourceLimit>=matches.length;
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
    $('detail-body').innerHTML = `<span class="pid">${esc(p.id)} · ${esc(p.contexts)}</span><h2 id="detail-title">${esc(p.title)}</h2><div class="example"><small>解释性假设场景，不是本轮复现结果</small>${esc(p.example)}</div><section class="detail-section"><h3>为什么值得关心</h3><p>${esc(p.why_it_matters)}</p></section><section class="detail-section"><h3>难在哪里 · 研究者概括</h3><p>${esc(p.why_hard)}</p></section><section class="detail-section"><h3>已有研究已经做到什么</h3><p>${esc(p.existing_progress)}</p>${sourceLinks(p.source_refs)}<p class="muted">${p.evidence_counts?.published_verified||0}项已核验发表、${p.evidence_counts?.preprint||0}项预印本、${p.evidence_counts?.indexed_unverified||0}项待核实。发表身份与摘要已核对不等于全文精读或复现；每项的详细阅读范围见下方文献主线。</p></section><section class="detail-section"><h3>仍需要问清楚什么 · 待核验，不是已确认创新</h3><p class="inference">${esc(p.open_question)}</p></section><section class="detail-section"><h3>与哪些问题相连</h3>${relations.map(e=>{const other=e.from===id?e.to:e.from;return `<button class="relation-item" data-detail="${esc(other)}">${esc(other)} · ${esc(problems[other].title)}<br><small>${esc(e.label)}</small></button>`;}).join('') || '<p class="muted">暂未整理到直接关联，不代表没有关系。</p>'}<p class="muted">这些连接帮助理解问题，不是经过实验验证的因果图。</p></section><div class="detail-select">${choice(p)}<p class="muted">先确认是否值得研究，再找可能方案。勾选不会启动任务。</p></div>`;
    const d=$('detail-dialog'); if (!d.open) d.showModal();
  }
  function renderCoverage() {
    $('coverage-view').innerHTML = `<div class="scroll-table"><table><thead><tr><th>问题主题</th><th>已核验发表 / 预印本 / 待核实 / 文档</th><th>资料覆盖判断</th><th>还缺什么</th></tr></thead><tbody>${data.themes.map(t=>{
      const ids=new Set(data.problems.filter(p=>p.theme_id===t.id).flatMap(p=>p.source_refs));
      const types=['published_verified','preprint','indexed_unverified','documentation'].map(g=>[...ids].filter(id=>groupOf(sources[id])===g).length);
      return `<tr><th>${esc(t.id)} · ${esc(t.title)}</th><td>${types.join(' / ')}</td><td>${esc(t.coverage)}</td><td>${esc(t.coverage_note)}</td></tr>`;
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
      const counts=data.publication_counts;
      $('hero-stats').innerHTML=`<div><b>${counts.published_verified}</b><small>已核验正式论文</small></div><div><b>${counts.published_2026}</b><small>其中发表于2026</small></div><div><b>${data.problems.length}</b><small>研究难点</small></div>`;
      $('refresh-summary').textContent=`从原来的14篇扩展到${counts.papers}篇论文记录：${counts.published_verified}篇已核验正式发表、${counts.preprint}篇预印本补充、${counts.indexed_unverified}篇发表状态待核实，另有${counts.documentation}份官方文档。1216条API候选只作为筛选池，未直接堆进地图。`;
      const receipt=data.collection_summary;
      $('collection-receipt').innerHTML=`<p>复用旧参考库的${receipt.old_scholar_records}条Scholar记录与${receipt.old_supplemental_records}条补充条目；静态去重后${receipt.old_static_bibliography.title_normalized_unique}项。重新执行${receipt.query_count}组认证查询，${receipt.successful_queries}组返回结果，获得${receipt.unique_candidate_records}个去重候选；实际HTTP尝试${receipt.http_requests}次（含重试）。</p><p>这些是候选，不是全部相关、已发表或已全文读完的论文。再经人工相关性筛选和官方书目核验，才进入当前地图。</p><p>未成功查询：${receipt.failed_queries.map(q=>esc(q.id+' '+q.query+' · HTTP '+q.status)).join('；')}。</p><p>${receipt.coverage_limits.map(esc).join('<br>')}</p>`;

      $('scope').textContent=data.scope+' '+data.coverage_statement;
      $('theme-filter').insertAdjacentHTML('beforeend',data.themes.map(t=>`<option value="${esc(t.id)}">${esc(t.id)} · ${esc(t.title)}</option>`).join(''));
      $('survey-steps').innerHTML=data.survey_method.map(s=>`<article class="survey-step"><h3>${esc(s.step)} <small>${esc(s.state)}</small></h3><p>${esc(s.detail)}</p></article>`).join('');
      $('source-count').textContent=`· ${data.sources.length} 项来源`;
      renderSources();
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
  ['source-query','source-status','source-year'].forEach(id=>$(id).addEventListener(id==='source-query'?'input':'change',()=>{sourceLimit=12;if(data)renderSources();}));
  $('source-more').addEventListener('click',()=>{sourceLimit+=12;renderSources();});
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
