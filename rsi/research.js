/* Static research content stays readable without JavaScript. */
(() => {
  'use strict';
  const root = document;
  const $ = (s) => root.querySelector(s);
  const sidebar = $('#sidebar');
  const overlay = $('#sidebar-overlay');
  const menu = $('#menu-toggle');
  let navLanguage = 'zh';
  try { navLanguage = localStorage.getItem('agent-evolution-language') || 'zh'; } catch (_) {}
  const text = (value) => typeof value === 'string' ? value : (value[navLanguage] || value.zh || value.en || '');
  function renderNavigation() {
    if (!Array.isArray(window.NAV_GROUPS)) return;
    const nav = $('#research-nav');
    nav.replaceChildren();
    const current = 'rsi/' + (root.body.dataset.rsiPage || 'index') + '.html';
    window.NAV_GROUPS.forEach((group) => {
      const details = root.createElement('details');
      details.className = 'nav-group';
      details.open = group.pages.some(([href]) => href === current) || Boolean(group.open);
      const summary = root.createElement('summary');
      summary.className = 'nav-level1';
      summary.textContent = text(group.title);
      const children = root.createElement('div');
      children.className = 'nav-children';
      group.pages.forEach(([href, label]) => {
        const link = root.createElement('a');
        link.href = '../' + href;
        link.className = 'nav-level2' + (href === current ? ' active' : '');
        if (href === current) link.setAttribute('aria-current', 'page');
        link.textContent = text(label);
        children.append(link);
      });
      details.append(summary, children);
      nav.append(details);
    });
    $('#nav-language').textContent = navLanguage === 'zh' ? 'EN navigation' : '中文目录';
  }
  $('#nav-language').addEventListener('click', () => {
    navLanguage = navLanguage === 'zh' ? 'en' : 'zh';
    try { localStorage.setItem('agent-evolution-language', navLanguage); } catch (_) {}
    renderNavigation();
  });
  renderNavigation();
  function setMenu(open) {
    sidebar.classList.toggle('open', open);
    overlay.hidden = !open;
    menu.setAttribute('aria-expanded', String(open));
    root.body.classList.toggle('rsi-menu-open', open);
    if (open) $('#sidebar-close').focus();
    else menu.focus({preventScroll: true});
  }
  menu.addEventListener('click', () => setMenu(!sidebar.classList.contains('open')));
  $('#sidebar-close').addEventListener('click', () => setMenu(false));
  overlay.addEventListener('click', () => setMenu(false));
  root.addEventListener('keydown', (e) => { if (e.key === 'Escape' && sidebar.classList.contains('open')) setMenu(false); });
  sidebar.addEventListener('click', (e) => {
    if (e.target.closest('a[href^="#"]') && innerWidth <= 820) setMenu(false);
  });
  // A local search corpus; never sends research queries to an external service.
  let indexPromise;
  let sequence = 0;
  const input = $('#research-search');
  const results = $('#search-results');
  input.addEventListener('input', async () => {
    const seq = ++sequence;
    const query = input.value.trim().toLocaleLowerCase();
    if (!query) { results.hidden = true; results.replaceChildren(); return; }
    results.hidden = false;
    results.textContent = '检索中…';
    try {
      indexPromise ||= fetch('search-index.json').then((r) => { if (!r.ok) throw new Error('Search index unavailable'); return r.json(); });
      const records = await indexPromise;
      if (seq !== sequence) return;
      const terms = query.split(/\s+/);
      const hits = records.map((r) => ({...r, score: terms.reduce((score, term) => score + (r.title.toLocaleLowerCase().includes(term) ? 3 : 0) + (r.text.toLocaleLowerCase().includes(term) ? 1 : 0), 0)}))
        .filter((r) => terms.every((term) => (r.title + ' ' + r.text).toLocaleLowerCase().includes(term)))
        .sort((a,b) => b.score-a.score);
      results.replaceChildren();
      const heading = root.createElement('h2');
      heading.textContent = `本专题找到 ${hits.length} 项${hits.length > 16 ? '，显示前 16 项' : ''}`;
      results.append(heading);
      if (!hits.length) { const p = root.createElement('p'); p.textContent = '可尝试“帮助”“curriculum”“干扰”或论文名称；本搜索不覆盖旧站其他专题。'; results.append(p); }
      hits.slice(0,16).forEach((r) => {
        const item = root.createElement('article');
        item.className = 'search-hit';
        const a = root.createElement('a'); a.href = r.url; a.textContent = r.title;
        const p = root.createElement('p');
        const position = Math.max(0, r.text.toLocaleLowerCase().indexOf(terms[0])-40);
        p.textContent = (position ? '…' : '') + r.text.slice(position, position+175) + (r.text.length > position+175 ? '…' : '');
        item.append(a,p); results.append(item);
      });
    } catch (_) {
      if (seq === sequence) results.textContent = '搜索索引暂不可用；正文、左侧目录和来源列表仍可阅读。';
      indexPromise = null;
    }
  });
  // Local, progressive-enhancement filter for the reusable paper reading-card library.
  const readingFilter = $('#reading-card-filter');
  if (readingFilter) {
    const cards = [...root.querySelectorAll('.reading-card')];
    const readingQuestion = $('#reading-question-filter');
    const readingCoverage = $('#reading-coverage-filter');
    const readingCount = $('#reading-card-count');
    const readingEmpty = $('#reading-empty');
    const matchCoverage = (level, expected) =>
      expected === 'all' || (expected === 'addressed' ? level !== 'not_addressed' : level === expected);
    const refreshReadingCards = () => {
      const terms = readingFilter.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      const question = readingQuestion?.value || 'all';
      const expected = readingCoverage?.value || 'addressed';
      let shown = 0;
      cards.forEach((card) => {
        const content = card.textContent.toLocaleLowerCase();
        const covers = (card.dataset.questionCoverage || '').split('|').map((entry) => entry.split(':'));
        const relevant = question === 'all' ? covers : covers.filter(([id]) => id === question);
        const levelMatch = (question === 'all' && expected === 'addressed')
          || relevant.some(([, level]) => matchCoverage(level, expected));
        const visible = terms.every((term) => content.includes(term)) && levelMatch;
        card.hidden = !visible;
        if (visible) shown += 1;
      });
      readingCount.textContent = '显示 ' + shown + ' / ' + cards.length + ' 篇';
      readingEmpty.hidden = shown !== 0;
    };
    readingFilter.addEventListener('input', refreshReadingCards);
    readingQuestion?.addEventListener('change', refreshReadingCards);
    readingCoverage?.addEventListener('change', refreshReadingCards);
    refreshReadingCards();
  }
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      const active = entries.filter((e) => e.isIntersecting).sort((a,b) => a.boundingClientRect.top-b.boundingClientRect.top)[0];
      if (!active) return;
      root.querySelectorAll('.toc-links a').forEach((a) => a.classList.toggle('active', a.getAttribute('href') === '#' + active.target.id));
    }, {rootMargin:'-60px 0px -65% 0px'});
    root.querySelectorAll('.research-section').forEach((s) => observer.observe(s));
  }
})();
