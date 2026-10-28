/* Curated research figure references: source-grounded and never experimental results. */
(() => {
  'use strict';
  const data = window.FIGURE_CURATED;
  const el = id => document.getElementById(id);
  if (!data) { el('curated-grid').textContent = '精选目录未加载，请刷新。'; return; }
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
    '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
  }[char]));
  const allowedHosts = new Set(['github.com', 'raw.githubusercontent.com', 'proceedings.iclr.cc']);
  const localFigureAsset = url => /^figure-reference-assets\/[a-z0-9-]+\.(?:svg|json)$/.test(String(url || ''));
  const safe = url => {
    if (localFigureAsset(url)) return String(url);
    try { const u = new URL(url); return u.protocol === 'https:' && allowedHosts.has(u.hostname) ? u.href : ''; }
    catch (_) { return ''; }
  };
  const safeImage = url => {
    if (localFigureAsset(url) && String(url).endsWith('.svg')) return url;
    try { const u = new URL(url); return u.protocol === 'https:' && u.hostname === 'raw.githubusercontent.com' ? u.href : ''; }
    catch (_) { return ''; }
  };
  const records = new Map(data.entries.map(e => [e.id, e]));
  let lang = 'zh', selected = new Set(), visible = [];
  const pick = (zh, en) => lang === 'zh' ? zh : en;
  const storageKey = 'publication-figure-shortlist-v2';
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || 'null');
    if (saved?.catalog_version === data.catalog_version && Array.isArray(saved.ids))
      selected = new Set(saved.ids.filter(id => records.has(id)).slice(0, 2));
  } catch (_) {}
  function status(message) { el('selection-status').textContent = message; }
  function save() {
    try { localStorage.setItem(storageKey, JSON.stringify({catalog_version:data.catalog_version,ids:[...selected]})); }
    catch (_) { status(pick('浏览器存储不可用；仍可导出。', 'Browser storage unavailable; export is still available.')); }
  }
  function bindImages(root) {
    root.querySelectorAll('img[data-reference]').forEach(img => img.addEventListener('error', () => {
      img.hidden = true;
      const note = img.parentElement.querySelector('.preview-note');
      if (note) note.hidden = false;
    }, {once:true}));
  }
  function sourceLabel(entry) { return entry.source_name === 'Figures4Papers' ? 'FIGURES4PAPERS' : 'ICLR 2026 · FIGURE 1'; }
  function referenceLabel(entry) {
    return entry.preview_origin ? pick('概念重绘 · 点击查看要求', 'Independent diagram · input requirements') :
      pick('参考原图 · 点击放大', 'Original reference · enlarge');
  }
  function codeLabel(entry) {
    return entry.code_role === 'EXPERIMENT_CODE_NOT_FIGURE_SOURCE' ?
      pick('论文实验代码', 'Paper experiment code') : pick('对应脚本', 'Source script');
  }
  function render() {
    const q = el('curated-search').value.toLowerCase().trim();
    const group = el('curated-group').value;
    visible = data.entries.filter(entry =>
      (!group || entry.group === group) &&
      (!q || [entry.title,entry.title_en,entry.question,entry.question_en,entry.learn,entry.learn_en,
        entry.chart,entry.source_name].join(' ').toLowerCase().includes(q)));
    el('curated-grid').innerHTML = visible.map(entry => `<article id="ref-${esc(entry.id)}" class="reference-card${selected.has(entry.id) ? ' selected' : ''}" data-id="${esc(entry.id)}">
      <button class="preview" data-open="${esc(entry.id)}" aria-label="${esc(pick(entry.title,entry.title_en))}">
        <img src="${esc(safeImage(entry.preview_url))}" alt="${esc(entry.title_en)} — ${esc(entry.preview_origin ? 'independent explanatory redraw' : 'original reference')}" loading="lazy" decoding="async" referrerpolicy="no-referrer" data-reference="${esc(entry.id)}">
        <span class="preview-note" hidden>${pick('预览暂不可用，可在详情页打开论文原图。','Preview unavailable; open original source in details.')}</span>
        <span class="preview-label">${referenceLabel(entry)}</span>
      </button>
      <div class="card-body">
        <div class="card-meta">${esc(sourceLabel(entry))} / ${esc(entry.chart.replaceAll('_',' '))}</div>
        <h3>${esc(pick(entry.title,entry.title_en))}</h3>
        <p class="card-question">${esc(pick(entry.question,entry.question_en))}</p>
        <p class="card-learn">${esc(pick(entry.learn,entry.learn_en))}</p>
        <div class="card-fields">${pick('所需输入','Required inputs')}: ${esc(entry.required_fields.join(' · '))}</div>
        ${entry.numeric_data_required === false ? `<p class="figure-schema-note">${pick('示意图：不需要准确率或训练日志；点开可查看数据格式。','Conceptual: no accuracy data needed. Open for a schema.')}</p>` : ''}
        <div class="card-footer"><span>
          <a href="${esc(safe(entry.source_url))}" target="_blank" rel="noopener noreferrer">${pick('论文原图','Original source')}</a> ·
          <a href="${esc(safe(entry.code_url))}" target="_blank" rel="noopener noreferrer">${codeLabel(entry)}</a>
        </span><button data-select="${esc(entry.id)}" aria-pressed="${selected.has(entry.id)}">${selected.has(entry.id) ? pick('✓ 已选','✓ Selected') : pick('选作参考','Select reference')}</button></div>
      </div>
    </article>`).join('') || '<p>' + pick('没有符合条件的精选项。', 'No matching curated reference.') + '</p>';
    el('result-count').textContent = pick(`${visible.length} 个精选参考 · 六张定量图与一张两阶段方法图`,
      `${visible.length} curated references · quantitative plots and a method schematic`);
    el('selection-count').textContent = pick(`已选 ${selected.size} / 2 个参考`, `${selected.size} / 2 references selected`);
    bindImages(el('curated-grid'));
  }
  function labels() {
    document.documentElement.lang = lang;
    el('language-toggle').textContent = pick('English','中文');
    el('gallery-title').innerHTML = pick('少量好图，<br>让比较关系更清楚。','Fewer references.<br>Clearer scientific narratives.');
    el('gallery-intro').textContent = pick(
      '从完整目录中挑选有明确用途的科研图：定量比较、实验趋势，以及 ICLR 2026 的两阶段方法总图。先明确要讲的科学问题，再看需要什么数据。',
      'A compact gallery of quantitative plots and a two-stage ICLR 2026 method schematic. Start with the question and the data needed.');
    el('references-title').textContent = pick('论文里真正用得上的结构','Structures that serve a paper');
    el('selection-heading').textContent = pick('这张图要回答什么？','What should this figure answer?');
    el('selection-help').textContent = pick('例如：如何展示“先记忆、后学习语义”，再到三种泛化？','How to show memorization, semantic alignment, and three probes?');
    el('question-label').textContent = pick('读者问题','Reader question');
    el('reader-question').placeholder = pick('用一句话写下问题；不是图型名称','One scientific question, not a chart name');
    el('export-brief').textContent = pick('导出给 Agent','Export for agent');
    el('curated-metrics').innerHTML = [[data.summary.active_examples,pick('精选图例','curated references')],
      [2,pick('每次最多引用','references per task')],[0,pick('默认加载归档','archive entries loaded')]]
      .map(([value,label]) => `<span><b>${value}</b>${label}</span>`).join('');
    el('audit-counts').innerHTML = '<table>' + Object.entries(data.exclusion_counts)
      .map(([reason,value]) => `<tr><td>${esc(reason)}</td><td>${value}</td></tr>`).join('') + '</table>';
  }
  function contractHTML(entry) {
    if (!Array.isArray(entry.input_contract)) return '';
    const rows = entry.input_contract.map(s => `<tr><td><b>${esc(s.name)}</b><br><code>${esc(s.fields.join(', '))}</code></td><td>${esc(s.reason)}</td></tr>`).join('');
    const measured = Object.entries(entry.optional_measured_fields || {})
      .map(([category,fields]) => `<li><b>${esc(category)}</b>: <code>${esc(fields.join(', '))}</code></li>`).join('');
    return `<section class="figure-contract">
      <h3>${pick('画出这类 F1，需要哪些数据？','What input data is needed to draw this F1-like diagram?')}</h3>
      <p class="figure-schema-note">${pick('不需要实验准确率：这是机制说明图。画图只需两阶段的结构化例子与三种评价提问；示意答案不是模型实测输出。','No measured accuracy is needed. Provide structured examples for the two phases and three test prompts; the shown answers are illustrative.')}</p>
      <table class="schema-table"><thead><tr><th>${pick('数据组及字段','Data and fields')}</th><th>${pick('用来画什么','Purpose')}</th></tr></thead><tbody>${rows}</tbody></table>
      <p><a href="${esc(safe(entry.input_contract_url))}" download>${pick('下载可直接改写的数据格式样例 JSON','Download editable JSON input example')}</a></p>
      <details><summary>${pick('若要把“泛化有效”画成实验结果，还要增加哪些实测数据？','Additional measured fields needed to claim generalization results')}</summary>
        <ul>${measured}</ul><p>${pick('必须标记 Phase 1 已见、Phase 2 未见的事实；独立验证的模型输出不能用示意答案代替。','Record Phase-1 exposure and Phase-2 holdout; do not replace actual model predictions with illustrative answers.')}</p>
      </details>
    </section>`;
  }
  function detail(id) {
    const entry = records.get(id); if (!entry) return;
    const isRedraw = Boolean(entry.preview_origin);
    const sourceNote = isRedraw ?
      pick('本卡预览是依据论文思想独立绘制的解释图，并非作者原 Figure 1 的截图。点击“原始 Figure 1”查看 ICLR 官方 PDF 第 2 页。',
           'The preview is a separate explanatory redraw, not the authors’ Figure 1. Open the official PDF (page 2) for the original.') :
      pick('这是上游设计参考，不是本项目的实验结果；不可照抄坐标、误差条或数值。',
           'This is a design reference, not project evidence; do not copy axes, uncertainties or values.');
    el('figure-detail').innerHTML = `<h2>${esc(pick(entry.title,entry.title_en))}</h2>
      <p>${esc(pick(entry.question,entry.question_en))}</p>
      <div><img class="detail-image" data-reference="${esc(entry.id)}" src="${esc(safeImage(entry.preview_url))}" alt="${esc(entry.title_en)}" referrerpolicy="no-referrer">
      <p class="preview-note" hidden>${pick('预览不可用，请打开原图。','Preview unavailable; open the source.')}</p></div>
      ${contractHTML(entry)}
      <div class="detail-notes"><p>${esc(pick(entry.learn,entry.learn_en))}</p><p>${sourceNote}</p>
        <p>${pick('来源','Source')}: ${esc(entry.source_name)}<br>${esc(entry.license)}</p>
        <a href="${esc(safe(entry.source_url))}" target="_blank" rel="noopener noreferrer">${pick('原始 Figure / 原图','Official original figure')}</a> ·
        <a href="${esc(safe(entry.code_url))}" target="_blank" rel="noopener noreferrer">${codeLabel(entry)}</a> ·
        <a href="${esc(safe(entry.license_url))}" target="_blank" rel="noopener noreferrer">${pick('论文来源及权限','Source and rights')}</a>
      </div>`;
    bindImages(el('figure-detail'));
    el('figure-dialog').showModal();
  }
  function toggle(id) {
    if (!records.has(id)) return;
    if (selected.has(id)) selected.delete(id);
    else if (selected.size >= 2) {
      status(pick('每次最多选 2 个参考；先取消一个。','Select at most two references; remove one first.')); return;
    } else selected.add(id);
    save(); render();
  }
  function exportBrief() {
    const question = el('reader-question').value.trim();
    if (!question || selected.size === 0) {
      status(pick('先写下读者问题，并选择 1–2 个参考。','Enter a question and select 1–2 references.')); return null;
    }
    const entries = [...selected].map(id => {
      const e = records.get(id);
      return {entry_id:e.id,content_version:e.content_version,title:e.title,chart:e.chart,
        required_fields:e.required_fields,source_url:e.source_url,code_url:e.code_url,
        commit:e.commit,preview_origin:e.preview_origin || 'UPSTREAM_SOURCE_IMAGE',
        input_contract_url:e.input_contract_url || null,
        input_contract:e.input_contract || null,
        numeric_data_required:e.numeric_data_required !== false,
        reference_only:true};
    });
    const brief = {schema_version:'2.1',origin:'BROWSER_DRAFT_NOT_SERVER_APPROVAL',
      catalog_version:data.catalog_version,reader_question:question,reference_limit:2,
      reference_scope:'curated_only',entries,
      requires_project_evidence:true,
      requires_numeric_results:entries.some(e => e.numeric_data_required),
      curated_only_external_paper_figures_require_separate_validation:true,
      visual_review:'NOT_RUN',scientific_authority:false};
    const link = document.createElement('a');
    const url = URL.createObjectURL(new Blob([JSON.stringify(brief,null,2)],{type:'application/json'}));
    link.href = url; link.download = 'curated-figure-brief.json'; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 500);
    status(pick('已导出结构参考与数据需求；还须核对项目真实数据和原图版权。',
      'Exported a design brief and input needs; validate project evidence and source rights.'));
    return brief;
  }
  document.addEventListener('click', event => {
    const open = event.target.closest('[data-open]'); if (open) { detail(open.dataset.open); return; }
    const choice = event.target.closest('[data-select]'); if (choice) toggle(choice.dataset.select);
  });
  el('curated-search').addEventListener('input',render);
  el('curated-group').addEventListener('change',render);
  el('language-toggle').onclick = () => { lang = lang === 'zh' ? 'en' : 'zh'; labels(); render(); };
  el('close-dialog').onclick = () => el('figure-dialog').close();
  el('export-brief').onclick = exportBrief;
  labels(); render();
  window.curatedFigureUI = {getVisible:() => visible.map(e=>e.id),getSelected:() => [...selected],toggle,exportBrief,detail};
})();
