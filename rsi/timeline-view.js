/* RSI timeline: standalone, source-grounded calendar and live AoE deadlines. */
(() => {
  'use strict';
  if (document.body.dataset.rsiPage !== 'timeline') return;

  const $ = (selector) => document.querySelector(selector);
  const items = Array.from(document.querySelectorAll('.rsi-tl-item'));
  const months = Array.from(document.querySelectorAll('.rsi-tl-month'));
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
  if (!items.length || !kind || !timeRange || !topic || !query || !counter ||
      !empty || !reset || !calendarGrid || !selection || !selectedLabel || !clearDay) return;

  const types = ['deadline', 'reading', 'research'];
  const names = {deadline: '会议 DDL', reading: '论文精读', research: '研究记录'};
  const weekdayNames = ['一', '二', '三', '四', '五', '六', '日'];
  const clockNodes = Array.from(document.querySelectorAll('[data-countdown]'));
  const beijingNodes = Array.from(document.querySelectorAll('[data-beijing]'));
  const formatShanghai = new Intl.DateTimeFormat('zh-CN', {
    timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', hour12: false
  });
  const tagSet = (row) => (row.dataset.tags || '').split('|').filter(Boolean);
  const todayParts = new Intl.DateTimeFormat('en-US', {timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit'})
    .formatToParts(new Date()).reduce((map, part) => {map[part.type] = part.value; return map;}, {});
  const todayShanghai = todayParts.year + '-' + todayParts.month + '-' + todayParts.day;
  const sortedDates = [...new Set(items.map((row) => row.dataset.date))].sort();
  let selectedDay = '';

  function elt(name, className, value) {
    const node = document.createElement(name);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = String(value);
    return node;
  }

  // Every official deadline is a 23:59 AoE timestamp with an explicit -12:00 offset.
  // The browser compares absolute instants; it never guesses dates for pending DDLs.
  function isUpcoming(row, now) {
    return Boolean(row.dataset.dueAt && Date.parse(row.dataset.dueAt) > now);
  }

  function clockText(ms) {
    if (ms <= 0) return '已截止 · 官方日期';
    const s = Math.floor(ms / 1000);
    const days = Math.floor(s / 86400);
    const hours = Math.floor((s % 86400) / 3600);
    const minutes = Math.floor((s % 3600) / 60);
    const seconds = s % 60;
    const pad = (n) => String(n).padStart(2, '0');
    return days + '天 ' + pad(hours) + '时 ' + pad(minutes) + '分 ' + pad(seconds) + '秒';
  }

  function updateCountdowns() {
    const now = Date.now();
    clockNodes.forEach((node) => {
      const iso = node.dataset.countdown;
      const due = Date.parse(iso);
      if (!iso || !Number.isFinite(due)) {
        node.textContent = '时间待核验';
        return;
      }
      node.textContent = clockText(due - now);
      node.classList.toggle('is-passed', due <= now);
      node.classList.toggle('is-urgent', due > now && due - now <= 7 * 86400000);
      node.title = '正式截止：' + iso + '（AoE，UTC−12）';
    });
  }

  beijingNodes.forEach((node) => {
    const due = Date.parse(node.dataset.beijing);
    if (Number.isFinite(due)) {
      node.textContent = '北京时间 ' + formatShanghai.format(new Date(due)).replace(/\//g, '-');
    } else {
      node.textContent = '北京时间待核验';
    }
  });

  function baseMatch(row, now, terms) {
    if (kind.value !== 'all' && row.dataset.kind !== kind.value) return false;
    if (timeRange.value === 'upcoming' && !isUpcoming(row, now)) return false;
    if (timeRange.value === 'past' && isUpcoming(row, now)) return false;
    if (topic.value !== 'all' && !tagSet(row).includes(topic.value)) return false;
    const haystack = (row.textContent + ' ' + row.dataset.tags).toLocaleLowerCase();
    return terms.every((term) => haystack.includes(term));
  }

  // Calendar grid uses UTC only for weekday and month arithmetic; deadline instants
  // are *not* derived from these local calendar dates.
  function monthKeys() {
    const keys = [];
    if (!sortedDates.length) return keys;
    const start = sortedDates[0].slice(0, 7);
    const end = sortedDates[sortedDates.length - 1].slice(0, 7);
    let year = Number(start.slice(0, 4));
    let month = Number(start.slice(5, 7));
    for (let limit = 0; limit < 36; limit += 1) {
      const key = year + '-' + String(month).padStart(2, '0');
      keys.push(key);
      if (key === end) break;
      month += 1;
      if (month === 13) { month = 1; year += 1; }
    }
    return keys;
  }
  const calendarMonths = monthKeys();

  function renderCalendar(rows) {
    const byDay = new Map();
    rows.forEach((row) => {
      const day = row.dataset.date;
      if (!byDay.has(day)) byDay.set(day, []);
      byDay.get(day).push(row);
    });
    const fragment = document.createDocumentFragment();
    calendarMonths.forEach((monthKey) => {
      const year = Number(monthKey.slice(0, 4));
      const monthNum = Number(monthKey.slice(5, 7));
      const lastDay = new Date(Date.UTC(year, monthNum, 0)).getUTCDate();
      const firstWeekday = (new Date(Date.UTC(year, monthNum - 1, 1)).getUTCDay() + 6) % 7;
      const inMonth = rows.filter((row) => row.dataset.date.startsWith(monthKey)).length;
      const panel = elt('section', 'rsi-tl-cal-month');
      panel.dataset.calendarMonth = monthKey;
      const head = elt('header', 'rsi-tl-cal-head');
      head.append(elt('h4', '', year + ' 年 ' + String(monthNum).padStart(2, '0') + ' 月'));
      head.append(elt('span', '', inMonth + ' 条记录'));
      panel.append(head);

      const weekLabels = elt('div', 'rsi-tl-cal-weekdays');
      weekdayNames.forEach((label) => weekLabels.append(elt('span', '', label)));
      panel.append(weekLabels);

      const days = elt('div', 'rsi-tl-cal-days');
      for (let i = 0; i < firstWeekday; i += 1) {
        const blank = elt('span', 'rsi-tl-cal-blank');
        blank.setAttribute('aria-hidden', 'true');
        days.append(blank);
      }
      for (let dayNum = 1; dayNum <= lastDay; dayNum += 1) {
        const iso = monthKey + '-' + String(dayNum).padStart(2, '0');
        const dayRows = byDay.get(iso) || [];
        const count = dayRows.length;
        const day = elt(count ? 'button' : 'span', 'rsi-tl-cal-day', '');
        day.append(elt('span', 'rsi-tl-cal-number', dayNum));
        if (count) {
          day.type = 'button';
          day.dataset.calendarDay = iso;
          day.classList.add('rsi-tl-cal-day--active');
          day.classList.add('rsi-tl-cal-density-' + Math.min(4, Math.ceil(Math.log2(count + 1))));
          day.setAttribute('aria-pressed', String(selectedDay === iso));
          const kinds = new Set(dayRows.map((row) => row.dataset.kind));
          const dots = elt('span', 'rsi-tl-cal-marks');
          types.forEach((type) => {
            if (kinds.has(type)) dots.append(elt('i', 'rsi-tl-dot rsi-tl-dot--' + type));
          });
          day.append(elt('b', 'rsi-tl-cal-count', count));
          day.append(dots);
          const breakdown = types.filter((t) => kinds.has(t)).map((t) =>
            names[t] + ' ' + dayRows.filter((row) => row.dataset.kind === t).length + ' 条'
          ).join('，');
          day.setAttribute('aria-label', iso + '，' + count + ' 条活动：' + breakdown + '。点击筛选日期');
          day.title = iso + ' · ' + breakdown;
        } else {
          day.classList.add('rsi-tl-cal-day--empty');
          day.title = iso + ' · 暂无符合筛选条件的记录';
        }
        if (iso === todayShanghai) {
          day.classList.add('rsi-tl-cal-day--today');
        }
        days.append(day);
      }
      panel.append(days);
      fragment.append(panel);
    });
    calendarGrid.replaceChildren(fragment);
  }

  function refresh() {
    const now = Date.now();
    const terms = query.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const baseRows = items.filter((row) => baseMatch(row, now, terms));
    const selectedRows = selectedDay ? baseRows.filter((row) => row.dataset.date === selectedDay) : baseRows;
    const shown = new Set(selectedRows);
    items.forEach((row) => {
      row.hidden = !shown.has(row);
      row.querySelectorAll('[data-filter-tag]').forEach((tag) => {
        tag.classList.toggle('is-selected', topic.value !== 'all' && tag.dataset.filterTag === topic.value);
        tag.setAttribute('aria-pressed', String(topic.value !== 'all' && tag.dataset.filterTag === topic.value));
      });
    });
    months.forEach((month) => {
      const rows = Array.from(month.querySelectorAll('.rsi-tl-item:not([hidden])'));
      month.hidden = rows.length === 0;
      const countLabel = month.querySelector('.rsi-tl-month-head span');
      if (countLabel) countLabel.textContent = rows.length + ' 条记录';
    });
    renderCalendar(baseRows);
    selection.hidden = !selectedDay;
    if (selectedDay) selectedLabel.textContent = '正在查看 ' + selectedDay + ' · ' + selectedRows.length + ' 条记录';
    empty.hidden = selectedRows.length !== 0;
    counter.textContent = '显示 ' + selectedRows.length + ' / ' + items.length + ' 条';
  }

  function setTag(tag) {
    // A rare card tag still works even if it was not among the 24 common options.
    const oldTransient = topic.querySelector('option[data-transient-tag]');
    if (oldTransient) oldTransient.remove();
    if (tag && !Array.from(topic.options).some((option) => option.value === tag)) {
      const option = elt('option', '', tag);
      option.value = tag;
      option.dataset.transientTag = 'true';
      topic.append(option);
    }
    topic.value = tag || 'all';
    selectedDay = '';
    refresh();
  }

  calendarGrid.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-calendar-day]');
    if (!button) return;
    const day = button.dataset.calendarDay;
    selectedDay = selectedDay === day ? '' : day;
    refresh();
    const first = items.find((row) => !row.hidden);
    if (first && selectedDay) first.scrollIntoView({behavior: 'smooth', block: 'start'});
  });
  document.querySelector('#rsi-tl-months').addEventListener('click', (event) => {
    const button = event.target.closest('button[data-filter-tag]');
    if (!button) return;
    setTag(topic.value === button.dataset.filterTag ? '' : button.dataset.filterTag);
  });
  clearDay.addEventListener('click', () => {
    selectedDay = '';
    refresh();
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

  updateCountdowns();
  refresh();
  window.setInterval(updateCountdowns, 1000);
  window.setInterval(() => {
    if (timeRange.value !== 'all') refresh();
  }, 60000);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      updateCountdowns();
      if (timeRange.value !== 'all') refresh();
    }
  });
})();
