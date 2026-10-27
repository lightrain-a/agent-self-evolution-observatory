/* RSI timeline: read-only progressive enhancement; no external requests. */
(() => {
  'use strict';
  if (document.body.dataset.rsiPage !== 'timeline') return;

  const $ = (selector) => document.querySelector(selector);
  const items = Array.from(document.querySelectorAll('.rsi-tl-item'));
  const months = Array.from(document.querySelectorAll('.rsi-tl-month'));
  const kind = $('#rsi-tl-kind');
  const timeRange = $('#rsi-tl-time');
  const query = $('#rsi-tl-query');
  const counter = $('#rsi-tl-count');
  const empty = $('#rsi-tl-empty');
  const reset = $('#rsi-tl-reset');
  if (!kind || !timeRange || !query || !counter || !empty || !reset) return;

  // AoE is UTC-12. Each official timestamp has an explicit -12:00 offset.
  const isUpcoming = (row, now) => {
    const official = row.dataset.dueAt;
    if (official) return Date.parse(official) > now;
    // Reading notes and research records are documented events, not future plans.
    return false;
  };

  function refresh() {
    const selected = kind.value;
    const scope = timeRange.value;
    const terms = query.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const now = Date.now();
    let count = 0;
    items.forEach((row) => {
      const future = isUpcoming(row, now);
      const matchesKind = selected === 'all' || row.dataset.kind === selected;
      const matchesTime = scope === 'all' || (scope === 'upcoming' ? future : !future);
      const searchable = row.textContent.toLocaleLowerCase();
      const matchesText = terms.every((term) => searchable.includes(term));
      const visible = matchesKind && matchesTime && matchesText;
      row.hidden = !visible;
      count += Number(visible);
    });
    months.forEach((month) => {
      const rows = Array.from(month.querySelectorAll('.rsi-tl-item:not([hidden])'));
      month.hidden = rows.length === 0;
      const countLabel = month.querySelector('.rsi-tl-month-head span');
      if (countLabel) countLabel.textContent = rows.length + ' 条记录';
    });
    empty.hidden = count !== 0;
    counter.textContent = '显示 ' + count + ' / ' + items.length + ' 条';
  }

  // Unknown official dates have no data-countdown element and no false timer.
  function updateCountdowns() {
    const now = Date.now();
    document.querySelectorAll('[data-countdown]').forEach((element) => {
      const timestamp = element.dataset.countdown;
      const due = Date.parse(timestamp);
      if (!timestamp || !Number.isFinite(due)) {
        element.textContent = '时间待核验';
        return;
      }
      const diff = due - now;
      element.classList.toggle('is-passed', diff <= 0);
      if (diff <= 0) {
        element.textContent = '已截止 · 官方日期';
      } else {
        const days = Math.floor(diff / 86400000);
        const hours = Math.floor(diff % 86400000 / 3600000);
        const minutes = Math.floor(diff % 3600000 / 60000);
        element.textContent = days > 0
          ? '距截止 ' + days + ' 天 ' + hours + ' 小时'
          : '距截止 ' + hours + ' 小时 ' + minutes + ' 分';
      }
      element.setAttribute('title', '正式截止：' + timestamp + ' (AoE/UTC−12)');
    });
  }

  for (const control of [kind, timeRange, query]) {
    control.addEventListener(control === query ? 'input' : 'change', refresh);
  }
  reset.addEventListener('click', () => {
    kind.value = 'all';
    timeRange.value = 'all';
    query.value = '';
    refresh();
    query.focus();
  });
  updateCountdowns();
  refresh();
  window.setInterval(() => {
    updateCountdowns();
    if (timeRange.value !== 'all') refresh();
  }, 60000);
})();
