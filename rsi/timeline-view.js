/* RSI research-timeline v3: compact, folding, source-grounded, standalone. */
(() => {
  'use strict';
  if (document.body.dataset.rsiPage !== 'timeline') return;

  const $ = (selector) => document.querySelector(selector);
  const items = [...document.querySelectorAll('.rsi-tl-item')];
  const months = [...document.querySelectorAll('.rsi-tl-month')];
  const days = [...document.querySelectorAll('.rsi-rt-day')];
  const kind = $('#rsi-tl-kind');
  const timeRange = $('#rsi-tl-time');
  const topic = $('#rsi-tl-topic');
  const query = $('#rsi-tl-query');
  const counter = $('#rsi-tl-count');
  const empty = $('#rsi-tl-empty');
  const reset = $('#rsi-tl-reset');
  const calendarGrid = $('#rsi-tl-calendar-grid');
  const selection = $('#rsi-tl-date-selection');
  const selectedLabel = $('#rsi-tl-selected-label');
  const clearDay = $('#rsi-tl-clear-day');
  const expandAll = $('#rsi-tl-expand-all');
  const collapseAll = $('#rsi-tl-collapse-all');
  const venueToggle = $('#rsi-rt-venue-toggle');
  if (!items.length || !kind || !timeRange || !topic || !query || !counter ||
      !empty || !reset || !calendarGrid || !selection || !selectedLabel ||
      !clearDay || !expandAll || !collapseAll) return;

  const types = ['deadline', 'reading', 'research'];
  const names = {deadline: '会议 DDL', reading: '论文精读', research: '研究记录'};
  const weekdays = ['一', '二', '三', '四', '五', '六', '日'];
  const clockNodes = [...document.querySelectorAll('[data-countdown]')];
  const beijingNodes = [...document.querySelectorAll('[data-beijing]')];
  const fmtChina = new Intl.DateTimeFormat('zh-CN', {
    timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', hour12: false
  });
  const dateParts = new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit'
  }).formatToParts(new Date()).reduce((obj, part) => {
    obj[part.type] = part.value;
    return obj;
  }, {});
  const todayChina = [dateParts.year, dateParts.month, dateParts.day].join('-');
  const allDates = [...new Set(items.map((r) => r.dataset.date))].sort();
  const monthDetails = new Map();
  let selectedDay = '';

  const deadlineData = (() => {
    try { return JSON.parse($('.rsi-rt-briefing')?.dataset.officialDeadlines || '[]'); }
    catch (_) { return []; }
  })();

  const create = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = String(text);
    return node;
  };
  const tagsOf = (item) => (item.dataset.tags || '').split('|').filter(Boolean);
  const isUpcoming = (row, now) =>
    Boolean(row.dataset.dueAt && Date.parse(row.dataset.dueAt) > now);
  const pad = (n) => String(n).padStart(2, '0');

  function countdownText(diff) {
    if (diff <= 0) return '已截止 · 官方日期';
    const seconds = Math.floor(diff / 1000);
    const day = Math.floor(seconds / 86400);
    const hour = Math.floor((seconds % 86400) / 3600);
    const minute = Math.floor((seconds % 3600) / 60);
    const second = seconds % 60;
    return day + '天 ' + pad(hour) + '时 ' + pad(minute) + '分 ' + pad(second) + '秒';
  }

  function updateCountdowns() {
    const now = Date.now();
    clockNodes.forEach((node) => {
      const due = Date.parse(node.dataset.countdown);
      if (!Number.isFinite(due)) { node.textContent = '时间待核验'; return; }
      node.textContent = countdownText(due - now);
      node.classList.toggle('is-passed', due <= now);
      node.classList.toggle('is-urgent', due > now && due - now < 7 * 86400000);
      node.title = '正式截止：' + node.dataset.countdown + '（AoE / UTC−12）';
    });
    const next = deadlineData.find((value) => Date.parse(value.iso) > now)
      || deadlineData[deadlineData.length - 1];
    const label = $('#rsi-rt-next-label');
    const date = $('#rsi-rt-next-date');
    const counterNode = $('#rsi-rt-next-countdown');
    const local = $('#rsi-rt-next-beijing');
    const source = $('#rsi-rt-next-source');
    if (next && label && date && counterNode && local && source) {
      const due = Date.parse(next.iso);
      label.textContent = next.venue + ' 2027 · ' + next.label;
      date.textContent = next.date + ' AoE';
      counterNode.textContent = countdownText(due - now);
      counterNode.classList.toggle('is-passed', due <= now);
      counterNode.classList.toggle('is-urgent', due > now && due - now < 7 * 86400000);
      local.textContent = '北京时间 ' + fmtChina.format(new Date(due)).replace(/\//g, '-');
      source.href = next.url;
    }
  }

  beijingNodes.forEach((node) => {
    const stamp = Date.parse(node.dataset.beijing);
    node.textContent = Number.isFinite(stamp)
      ? '北京时间 ' + fmtChina.format(new Date(stamp)).replace(/\//g, '-')
      : '北京时间待核验';
  });

  const calendarMonths = (() => {
    if (!allDates.length) return [];
    const first = allDates[0].slice(0, 7);
    const last = allDates[allDates.length - 1].slice(0, 7);
    let year = Number(first.slice(0, 4));
    let month = Number(first.slice(5, 7));
    const keys = [];
    for (let limit = 0; limit < 36; limit += 1) {
      const key = year + '-' + pad(month);
      keys.push(key);
      if (key === last) break;
      month += 1;
      if (month === 13) { month = 1; year += 1; }
    }
    return keys;
  })();

  function renderCalendar(rows) {
    // Preserve user-opened/closed calendar months when filters change.
    calendarGrid.querySelectorAll('details[data-calendar-month]').forEach((detail) => {
      monthDetails.set(detail.dataset.calendarMonth, detail.open);
    });
    const byDay = new Map();
    rows.forEach((row) => {
      const date = row.dataset.date;
      if (!byDay.has(date)) byDay.set(date, []);
      byDay.get(date).push(row);
    });
    const fragment = document.createDocumentFragment();
    calendarMonths.forEach((key, index) => {
      const year = Number(key.slice(0, 4));
      const month = Number(key.slice(5, 7));
      const firstWeekday = (new Date(Date.UTC(year, month - 1, 1)).getUTCDay() + 6) % 7;
      const lastDay = new Date(Date.UTC(year, month, 0)).getUTCDate();
      const count = rows.filter((r) => r.dataset.date.startsWith(key)).length;

      const panel = create('details', 'rsi-tl-cal-month');
      panel.dataset.calendarMonth = key;
      panel.open = monthDetails.has(key) ? monthDetails.get(key) : index < 2;

      const head = create('summary', 'rsi-tl-cal-head');
      const title = create('span', 'rsi-tl-cal-title');
      title.append(create('b', '', year + ' 年 ' + month + ' 月'));
      title.append(create('small', '', count + ' 条记录'));
      head.append(title, create('span', 'rsi-rt-fold-icon'));
      panel.append(head);
      const inside = create('div', 'rsi-tl-cal-inner');
      const weekdayRow = create('div', 'rsi-tl-cal-weekdays');
      weekdays.forEach((day) => weekdayRow.append(create('span', '', day)));
      inside.append(weekdayRow);
      const grid = create('div', 'rsi-tl-cal-days');
      for (let blank = 0; blank < firstWeekday; blank += 1) {
        const node = create('span', 'rsi-tl-cal-blank');
        node.setAttribute('aria-hidden', 'true');
        grid.append(node);
      }
      for (let n = 1; n <= lastDay; n += 1) {
        const day = key + '-' + pad(n);
        const dayRows = byDay.get(day) || [];
        const countDay = dayRows.length;
        const cell = create(countDay ? 'button' : 'span', 'rsi-tl-cal-day');
        cell.append(create('span', 'rsi-tl-cal-number', n));
        if (day === todayChina) cell.classList.add('is-today');
        if (countDay) {
          cell.type = 'button';
          cell.dataset.calendarDay = day;
          cell.classList.add('has-activity');
          cell.classList.add('rsi-tl-cal-density-' + Math.min(4, Math.ceil(Math.log2(countDay + 1))));
          cell.setAttribute('aria-pressed', String(selectedDay === day));
          cell.append(create('b', 'rsi-tl-cal-count', countDay));
          const dots = create('span', 'rsi-tl-cal-marks');
          const kinds = new Set(dayRows.map((r) => r.dataset.kind));
          types.forEach((type) => {
            if (kinds.has(type)) dots.append(create('i', 'rsi-tl-dot rsi-tl-dot--' + type));
          });
          cell.append(dots);
          const brief = types.filter((type) => kinds.has(type))
            .map((type) => names[type] + ' ' +
              dayRows.filter((row) => row.dataset.kind === type).length + ' 条').join('，');
          cell.setAttribute('aria-label', day + '，' + countDay + ' 条记录：' + brief + '。点击查看');
          cell.title = day + ' · ' + brief;
        } else {
          cell.classList.add('is-empty');
          cell.title = day + ' · 没有符合筛选的记录';
        }
        grid.append(cell);
      }
      inside.append(grid);
      panel.append(inside);
      fragment.append(panel);
    });
    calendarGrid.replaceChildren(fragment);
  }

  function baseMatch(row, now, terms) {
    if (kind.value !== 'all' && row.dataset.kind !== kind.value) return false;
    if (timeRange.value === 'upcoming' && !isUpcoming(row, now)) return false;
    if (timeRange.value === 'past' && isUpcoming(row, now)) return false;
    if (topic.value !== 'all' && !tagsOf(row).includes(topic.value)) return false;
    const words = (row.textContent + ' ' + row.dataset.tags).toLocaleLowerCase();
    return terms.every((word) => words.includes(word));
  }

  function updateWorkload(container, rows) {
    if (!container) return;
    container.replaceChildren();
    for (const type of types) {
      const n = rows.filter((row) => row.dataset.kind === type).length;
      if (!n) continue;
      const band = create('i', 'rsi-rt-workload--' + type);
      band.style.width = (100 * n / rows.length).toFixed(2) + '%';
      container.append(band);
    }
  }

  function refresh() {
    const now = Date.now();
    const terms = query.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const baseRows = items.filter((row) => baseMatch(row, now, terms));
    const visibleRows = selectedDay
      ? baseRows.filter((row) => row.dataset.date === selectedDay)
      : baseRows;
    const visible = new Set(visibleRows);
    items.forEach((row) => {
      row.hidden = !visible.has(row);
      row.querySelectorAll('[data-filter-tag]').forEach((button) => {
        const active = topic.value !== 'all' && button.dataset.filterTag === topic.value;
        button.classList.toggle('is-selected', active);
        button.setAttribute('aria-pressed', String(active));
      });
    });
    days.forEach((day) => {
      const rows = [...day.querySelectorAll('.rsi-tl-item:not([hidden])')];
      day.hidden = rows.length === 0;
      const countNode = day.querySelector('.rsi-rt-day-volume b');
      if (countNode) countNode.textContent = rows.length;
      const kinds = day.querySelector('.rsi-rt-day-kinds');
      if (kinds) {
        kinds.replaceChildren();
        types.forEach((type) => {
          const n = rows.filter((row) => row.dataset.kind === type).length;
          if (n) kinds.append(create('span', 'rsi-rt-kind-count rsi-rt-kind-count--' + type,
                                     names[type] + ' ' + n));
        });
      }
      const headline = day.querySelector('.rsi-rt-day-headline');
      if (headline && rows.length) {
        const primary = rows.find((row) => row.dataset.kind === 'research') || rows[0];
        headline.textContent = primary.querySelector('.rsi-tl-event-copy strong')?.textContent || '';
      }
      updateWorkload(day.querySelector('.rsi-rt-workload'), rows);
    });
    months.forEach((month) => {
      const rows = [...month.querySelectorAll('.rsi-tl-item:not([hidden])')];
      month.hidden = !rows.length;
      const count = month.querySelector('.rsi-tl-month-count');
      if (count) count.textContent = rows.length;
      updateWorkload(month.querySelector(':scope > summary .rsi-rt-workload'), rows);
    });

    renderCalendar(baseRows);
    selection.hidden = !selectedDay;
    if (selectedDay) {
      selectedLabel.textContent = selectedDay + ' · ' + visibleRows.length + ' 条符合条件的记录';
    }
    empty.hidden = visibleRows.length !== 0;
    counter.textContent = visibleRows.length + ' / ' + items.length + ' 条';
  }

  function setTag(tag) {
    const transient = topic.querySelector('option[data-transient-tag]');
    if (transient) transient.remove();
    if (tag && ![...topic.options].some((option) => option.value === tag)) {
      const option = create('option', '', tag);
      option.value = tag;
      option.dataset.transientTag = 'true';
      topic.append(option);
    }
    topic.value = tag || 'all';
    selectedDay = '';
    refresh();
  }

  function openDay(day, scroll = true) {
    const target = document.getElementById('day-' + day);
    if (!target || target.hidden) return;
    const month = target.closest('.rsi-tl-month');
    if (month) month.open = true;
    target.open = true;
    if (scroll) target.scrollIntoView({behavior: 'smooth', block: 'start'});
  }

  calendarGrid.addEventListener('click', (event) => {
    const cell = event.target.closest('button[data-calendar-day]');
    if (!cell) return;
    const clicked = cell.dataset.calendarDay;
    selectedDay = selectedDay === clicked ? '' : clicked;
    refresh();
    if (selectedDay) openDay(selectedDay);
  });

  $('#rsi-tl-months').addEventListener('click', (event) => {
    const button = event.target.closest('button[data-filter-tag]');
    if (button) setTag(topic.value === button.dataset.filterTag ? '' : button.dataset.filterTag);
  });
  clearDay.addEventListener('click', () => { selectedDay = ''; refresh(); });
  expandAll.addEventListener('click', () => {
    months.forEach((month) => { if (!month.hidden) month.open = true; });
    days.forEach((day) => { if (!day.hidden) day.open = true; });
  });
  collapseAll.addEventListener('click', () => {
    days.forEach((day) => { day.open = false; });
    months.forEach((month) => { month.open = false; });
  });

  for (const control of [kind, timeRange, topic, query]) {
    control.addEventListener(control === query ? 'input' : 'change', refresh);
  }
  reset.addEventListener('click', () => {
    kind.value = 'all';
    timeRange.value = 'all';
    query.value = '';
    setTag('');
    query.focus();
  });

  function openHashTarget() {
    let hash = '';
    try { hash = decodeURIComponent(location.hash.slice(1)); }
    catch (_) { return; }
    if (!hash) return;
    const node = document.getElementById(hash);
    if (!node) return;
    if (venueToggle && (node.closest('.rsi-rt-venue-toggle') || node === venueToggle)) {
      venueToggle.open = true;
    }
    const month = node.closest('.rsi-tl-month');
    const day = node.closest('.rsi-rt-day');
    const item = node.closest('.rsi-tl-item');
    if (month) month.open = true;
    if (day) day.open = true;
    if (item) item.open = true;
    if (month || day || item || node.closest('.rsi-rt-venue-toggle')) {
      node.scrollIntoView({block: 'start'});
    }
  }

  updateCountdowns();
  refresh();
  openHashTarget();
  window.addEventListener('hashchange', openHashTarget);
  window.setInterval(updateCountdowns, 1000);
  window.setInterval(() => { if (timeRange.value !== 'all') refresh(); }, 60000);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      updateCountdowns();
      if (timeRange.value !== 'all') refresh();
    }
  });
})();
