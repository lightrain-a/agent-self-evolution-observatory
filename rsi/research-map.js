(() => {
  'use strict';
  window.RSIResearchMapCleanup?.();
  const query = document.getElementById('rm-search');
  const select = document.getElementById('rm-function');
  if (!query || !select) return;
  const groups = [...document.querySelectorAll('.rm-group')];
  const result = document.getElementById('rm-result');
  const empty = document.getElementById('rm-empty');
  const index = [...document.querySelectorAll('[data-map-select]')];
  const aliases = {signals:'signal',capabilities:'capability'};
  const valid = value => [...select.options].some(option => option.value === value);
  let lastOpen = new Map(groups.map(group => [group, group.open]));
  let searching = false;
  const url = new URL(location.href);
  const initial = url.searchParams.get('function') || 'all';
  select.value = valid(initial) ? initial : (valid(aliases[initial]) ? aliases[initial] : 'all');
  query.value = url.searchParams.get('q') || '';
  function apply(syncUrl = true) {
    const terms = query.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const nowSearching = terms.length > 0;
    if (nowSearching && !searching) lastOpen = new Map(groups.map(group => [group, group.open]));
    let shown = 0, matches = 0;
    for (const group of groups) {
      const category = select.value === 'all' || group.dataset.function === select.value;
      const heading = group.querySelector('summary').textContent.toLocaleLowerCase();
      const overview = group.querySelector('.rm-question').textContent.toLocaleLowerCase();
      const groupMatches = terms.every(term => (heading + ' ' + overview).includes(term));
      let rowMatches = 0;
      for (const row of group.querySelectorAll('.rm-searchable')) {
        const text = (row.dataset.search || row.textContent).toLocaleLowerCase();
        const hit = !nowSearching || groupMatches || terms.every(term => text.includes(term));
        row.hidden = !hit;
        if (hit) rowMatches++;
      }
      group.hidden = !category || (nowSearching && !groupMatches && rowMatches === 0);
      if (!group.hidden) { shown++; matches += rowMatches; }
      if (nowSearching && !group.hidden) group.open = true;
      else if (!nowSearching && searching) group.open = lastOpen.get(group) ?? true;
    }
    searching = nowSearching;
    empty.hidden = shown !== 0;
    result.textContent = nowSearching ? `找到 ${shown} 项学习功能，${matches} 条文献或 Idea` : `显示 ${shown} 项学习功能`;
    index.forEach(link => link.setAttribute('aria-current', String(link.dataset.mapSelect === select.value)));
    if (syncUrl) {
      const next = new URL(location.href);
      if (select.value === 'all') next.searchParams.delete('function');
      else next.searchParams.set('function', select.value);
      if (query.value.trim()) next.searchParams.set('q', query.value.trim());
      else next.searchParams.delete('q');
      history.replaceState(null, '', next);
    }
  }
  function reset() { query.value = ''; select.value = 'all'; apply(); }
  query.addEventListener('input', () => apply());
  select.addEventListener('change', () => apply());
  document.getElementById('rm-reset').addEventListener('click', reset);
  document.querySelectorAll('[data-map-reset]').forEach(button => button.addEventListener('click', reset));
  document.getElementById('rm-expand').addEventListener('click', () => groups.filter(group => !group.hidden).forEach(group => { group.open = true; }));
  document.getElementById('rm-collapse').addEventListener('click', () => groups.filter(group => !group.hidden).forEach(group => { group.open = false; }));
  index.forEach(link => link.addEventListener('click', event => {
    event.preventDefault(); query.value = ''; select.value = link.dataset.mapSelect; apply();
    const group = groups.find(item => item.dataset.function === select.value);
    if (group) { group.open = true; group.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',block:'start'}); }
  }));
  const onPopState = () => { const next = new URL(location.href); select.value = valid(next.searchParams.get('function')) ? next.searchParams.get('function') : 'all'; query.value = next.searchParams.get('q') || ''; apply(false); };
  window.addEventListener('popstate', onPopState);
  window.RSIResearchMapCleanup = () => window.removeEventListener('popstate',onPopState);
  apply(false);
})();
