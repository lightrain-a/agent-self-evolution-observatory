/* Reader index: DOM-only search, no external API or background synchronization. */
(() => {
  'use strict';
  function init() {
    const root = document.getElementById('experimental-atlas-app');
    if (!root) return;
    if (root.dataset.atlasReady === 'true') return;
    root.dataset.atlasReady = 'true';
    const search = root.querySelector('#atlas-search');
    const group = root.querySelector('#atlas-group');
    const params = new URL(location.href).searchParams;
    const views = ['datasets', 'paper', 'metric', 'control', 'family'];
    let view = views.includes(params.get('atlas_view')) ? params.get('atlas_view') : 'datasets';
    let question = params.get('atlas_question') || 'all';
    if (!root.querySelector('[data-atlas-question="' + CSS.escape(question) + '"]')) question = 'all';
    search.value = params.get('atlas_search') || '';
    const initialGroup = params.get('atlas_group') || 'all';
    if ([...group.options].some(x => x.value === initialGroup)) group.value = initialGroup;
    const cards = [...root.querySelectorAll('[data-atlas-item]')];
    function save() {
      const url = new URL(location.href);
      for (const [key,value] of Object.entries({atlas_view:view,atlas_question:question,atlas_group:group.value,atlas_search:search.value.trim()})) {
        if (!value || value === 'all' || (key === 'atlas_view' && value === 'datasets')) url.searchParams.delete(key);
        else url.searchParams.set(key,value);
      }
      history.replaceState(history.state, '', url.href);
    }
    function render(updateUrl = true) {
      const terms = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      const total = cards.filter(c => c.dataset.kind === view).length;
      let visible = 0;
      root.querySelectorAll('[data-atlas-panel]').forEach(p => {p.hidden = p.dataset.atlasPanel !== view;});
      root.querySelectorAll('[data-atlas-view]').forEach(b => b.setAttribute('aria-pressed',String(b.dataset.atlasView === view)));
      root.querySelectorAll('[data-atlas-question]').forEach(b => b.setAttribute('aria-pressed',String(view === 'datasets' && b.dataset.atlasQuestion === question)));
      root.querySelectorAll('[data-question-note]').forEach(p => {p.hidden = p.dataset.questionNote !== (view === 'datasets' ? question : 'all');});
      root.querySelector('#atlas-group-label').hidden = view !== 'datasets';
      cards.forEach(c => {
        const match = c.dataset.kind === view && terms.every(t => c.dataset.search.includes(t)) &&
          (view !== 'datasets' || ((group.value === 'all' || c.dataset.group === group.value) &&
          (question === 'all' || c.dataset.questions.split(' ').includes(question))));
        c.hidden = !match;
        if (match) visible += 1;
      });
      root.querySelector('#atlas-count').textContent = '显示 ' + visible + ' / ' + total + ' 个条目';
      root.querySelector('#atlas-empty').hidden = visible > 0;
      if (updateUrl) save();
    }
    function jump(kind, id) {
      view = kind; question = 'all'; group.value = 'all'; search.value = '';
      render();
      const target = document.getElementById((kind === 'datasets' ? 'dataset-' : 'record-') + id);
      if (!target) return;
      const details = target.querySelector('details');
      if (details) details.open = true;
      target.setAttribute('tabindex','-1');
      target.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',block:'start'});
      target.focus({preventScroll:true});
    }
    root.addEventListener('click',event => {
      const button = event.target.closest('button');
      if (!button || !root.contains(button)) return;
      if (button.hasAttribute('data-atlas-view')) {view=button.dataset.atlasView;question='all';search.value='';group.value='all';render();}
      else if (button.hasAttribute('data-atlas-question')) {view='datasets';question=question === button.dataset.atlasQuestion ? 'all' : button.dataset.atlasQuestion;render();}
      else if (button.hasAttribute('data-record-target')) jump('paper',button.dataset.recordTarget);
      else if (button.hasAttribute('data-dataset-target')) jump('datasets',button.dataset.datasetTarget);
      else if (button.id === 'atlas-reset') {question='all';group.value='all';search.value='';render();}
    });
    search.addEventListener('input',() => render());
    group.addEventListener('change',() => render());
    render(false);
  }
  if (!window.__rsiAtlasListener) {
    document.addEventListener('rsi:pagechange',init);
    window.__rsiAtlasListener = true;
  }
  init();
})();
