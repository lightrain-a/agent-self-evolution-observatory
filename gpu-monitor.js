"use strict";
(function () {
  const API_BASE = String(window.GPU_MONITOR_API_BASE || "").replace(/\/+$/, "");
  const POLL_MS = 5000;
  const NODE_META = {
    "69": { title: "69 服务器", hint: "A100 · 独立节点", order: 0 },
    "42": { title: "42 服务器", hint: "RTX 4090 · 计算节点", order: 1 },
    "52": { title: "52 服务器", hint: "RTX 3090 · 计算节点", order: 2 }
  };
  const container = document.getElementById("server-grid");
  const summaryNode = document.getElementById("cluster-summary");
  const lastUpdated = document.getElementById("last-updated");
  const connection = document.getElementById("connection");
  const connectionLabel = document.getElementById("connection-label");
  const warning = document.getElementById("monitor-warning");
  let mostRecent = null;
  let history = {};
  let isPolling = false;
  let lastSuccessfulFetch = 0;

  function esc(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function num(value) {
    return typeof value === "number" && Number.isFinite(value) ? value : null;
  }
  function percent(value) {
    return Math.max(0, Math.min(100, num(value) == null ? 0 : value));
  }
  function fmt(value, digits) {
    return num(value) == null ? "—" : value.toFixed(digits == null ? 0 : digits);
  }
  function gib(mib) {
    return num(mib) == null ? "—" : (mib / 1024).toFixed(1);
  }
  function nowSeconds() {
    return Date.now() / 1000;
  }
  function setConnection(label, klass) {
    connection.className = "connection" + (klass ? " " + klass : "");
    connectionLabel.textContent = label;
  }
  function chart(series) {
    const finite = (series || []).filter(p => p && num(p.avg_util) !== null).slice(-60);
    if (finite.length < 2) return '<div class="node-spark-label">积累 10 分钟使用率趋势中</div>';
    const coords = finite.map((point, idx) => {
      const x = 3 + (idx * 294 / (finite.length - 1));
      const y = 43 - percent(point.avg_util) * 0.40;
      return x.toFixed(1) + "," + y.toFixed(1);
    }).join(" ");
    return '<svg viewBox="0 0 300 48" role="img" aria-label="最近十分钟平均 GPU 利用率趋势">' +
      '<line x1="0" y1="43" x2="300" y2="43" stroke="#dce7f5" stroke-width="1"/>' +
      '<line x1="0" y1="23" x2="300" y2="23" stroke="#edf2f9" stroke-dasharray="3 4"/>' +
      '<polyline fill="none" stroke="#3472e8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" points="' + coords + '"/>' +
      '</svg><div class="node-spark-label">最近约 10 分钟 · 平均利用率</div>';
  }
  function nodeCard(host) {
    const meta = NODE_META[host.id] || { title: String(host.id), hint: "GPU 服务器" };
    const age = num(host.sampled_at) === null ? null : Math.max(0, nowSeconds() - host.sampled_at);
    const online = Boolean(host.online && age !== null && age <= 35);
    const gpus = Array.isArray(host.gpus) ? host.gpus : [];
    const utils = gpus.map(g => num(g.util)).filter(v => v !== null);
    const average = utils.length ? utils.reduce((a, b) => a + b, 0) / utils.length : null;
    const used = gpus.reduce((sum, g) => sum + (num(g.used_mib) || 0), 0);
    const total = gpus.reduce((sum, g) => sum + (num(g.total_mib) || 0), 0);
    const lastSeen = age == null ? "尚未收到数据" : ("上次采样 " + Math.round(age) + " 秒前");
    const gpuHtml = gpus.map(g => {
      const u = percent(g.util);
      const m = num(g.total_mib) > 0 ? percent(g.used_mib * 100 / g.total_mib) : 0;
      const temp = num(g.temp_c);
      const power = num(g.power_w);
      return '<div class="gpu-tile" aria-label="GPU ' + esc(g.index) + '">' +
        '<div class="gpu-top"><span class="gpu-index">GPU ' + esc(g.index) + '</span><strong class="gpu-util">' + fmt(g.util) + '%</strong></div>' +
        '<div class="gpu-model" title="' + esc(g.model) + '">' + esc(g.model) + '</div>' +
        '<div class="meter" title="GPU 计算利用率"><div class="meter-fill' + (u >= 90 ? ' hot' : '') + '" style="width:' + u + '%"></div></div>' +
        '<div class="memory-head"><span>显存</span><b>' + gib(g.used_mib) + ' / ' + gib(g.total_mib) + ' GiB</b></div>' +
        '<div class="meter memory-meter" title="已分配显存"><div class="meter-fill" style="width:' + m + '%"></div></div>' +
        '<div class="gpu-foot"><span>温度 <strong>' + (temp === null ? '—' : fmt(temp) + '°C') + '</strong></span>' +
        '<span>功耗 <strong>' + (power === null ? '—' : fmt(power) + 'W') + '</strong></span></div>' +
        '</div>';
    }).join("");
    return '<article class="node' + (online ? '' : ' offline') + '">' +
      '<div class="node-header"><div class="node-title"><div class="node-id">' + esc(host.id) + '</div>' +
      '<div><h3>' + esc(meta.title) + '</h3><p>' + esc(meta.hint) + ' · ' + esc(lastSeen) + '</p></div></div>' +
      '<span class="node-state">' + (online ? '● 在线' : '● ' + (gpus.length ? '采集超时' : '等待数据')) + '</span></div>' +
      (gpus.length
        ? '<div class="node-metrics">' +
          '<div class="node-metric"><span>GPU 数量</span><strong>' + gpus.length + '</strong></div>' +
          '<div class="node-metric"><span>平均利用率</span><strong>' + fmt(average) + '%</strong></div>' +
          '<div class="node-metric"><span>已分配 / 总显存</span><strong>' + gib(used) + ' / ' + gib(total) + ' GiB</strong></div>' +
          '<div class="node-spark">' + chart(history[host.id]) + '</div></div>' +
          '<div class="gpu-grid">' + gpuHtml + '</div>'
        : '<div class="offline-empty">此节点尚无有效 GPU 数据。请检查采集进程与中继连接。</div>') +
      '</article>';
  }
  function stat(label, value, unit, note) {
    return '<article class="stat"><span>' + esc(label) + '</span><strong>' +
      esc(value) + (unit ? '<em>' + esc(unit) + '</em>' : '') +
      '</strong><small>' + esc(note) + '</small></article>';
  }
  function render(data) {
    if (!data || !Array.isArray(data.hosts)) return;
    const hosts = data.hosts.slice().sort((a, b) => (NODE_META[a.id]?.order ?? 9) - (NODE_META[b.id]?.order ?? 9));
    const onlineHosts = hosts.filter(h => h.online && num(h.sampled_at) !== null && nowSeconds() - h.sampled_at <= 35);
    const onlineGpus = onlineHosts.flatMap(h => h.gpus || []);
    const allGpus = hosts.flatMap(h => h.gpus || []);
    const validUtils = onlineGpus.map(g => num(g.util)).filter(v => v !== null);
    const avgUtil = validUtils.length ? validUtils.reduce((a, b) => a + b, 0) / validUtils.length : null;
    const usedMib = onlineGpus.reduce((a, g) => a + (num(g.used_mib) || 0), 0);
    const totalMib = onlineGpus.reduce((a, g) => a + (num(g.total_mib) || 0), 0);
    summaryNode.innerHTML = [
      stat("在线服务器", onlineHosts.length + " / " + hosts.length, "", "35 秒无心跳判定超时"),
      stat("可见 GPU 数量", String(allGpus.length), "张", "已发现的 GPU 总数"),
      stat("平均 GPU 利用率", avgUtil === null ? "—" : fmt(avgUtil) + "%", "", "仅统计在线 GPU"),
      stat("已分配显存", gib(usedMib), " / " + gib(totalMib) + " GiB", "在线节点的 GPU 显存")
    ].join("");
    container.innerHTML = hosts.map(nodeCard).join("");
    const clock = new Date((num(data.server_time) || nowSeconds()) * 1000);
    lastUpdated.textContent = "中继更新 " + clock.toLocaleTimeString("zh-CN", { hour12: false });
    setConnection(onlineHosts.length + "/" + hosts.length + " 节点在线", onlineHosts.length ? "connected" : "error");
    if (onlineHosts.length < hosts.length) {
      warning.hidden = false;
      warning.textContent = "存在未上报或采集超时的节点："
        + hosts.filter(h => !onlineHosts.includes(h)).map(h => h.id).join("、")
        + "。离线节点保留最后一次可见值，不应视为当前资源可用性。";
    } else {
      warning.hidden = true;
    }
  }
  async function getJson(path) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch(API_BASE + path + "?t=" + Date.now(), {cache: "no-store", signal: controller.signal});
      if (!response.ok) throw new Error("HTTP " + response.status);
      return await response.json();
    } finally {
      clearTimeout(timeout);
    }
  }
  async function poll() {
    if (isPolling || document.visibilityState === "hidden") return;
    if (!API_BASE) {
      setConnection("尚未配置数据接口", "error");
      warning.hidden = false;
      warning.textContent = "实时中继地址尚未配置，网页已部署但暂时无法显示服务器数据。";
      return;
    }
    isPolling = true;
    try {
      const [data, trends] = await Promise.all([
        getJson("/api/v1/gpus"),
        getJson("/api/v1/history").catch(() => null)
      ]);
      if (trends && trends.hosts) history = trends.hosts;
      mostRecent = data;
      lastSuccessfulFetch = Date.now();
      render(data);
    } catch (err) {
      setConnection("实时接口连接失败", "error");
      warning.hidden = false;
      warning.textContent = "无法获取 GPU 最新数据。可能是网络、采集服务或临时 HTTPS 通道中断；不会把历史值标成当前在线。";
      if (mostRecent) {
        render(mostRecent);
        setConnection("实时接口连接失败", "error");
        warning.hidden = false;
        if (Date.now() - lastSuccessfulFetch > 35000) {
          warning.textContent = "实时接口超过 35 秒不可达，页面显示的是历史快照。请检查数据中继或 HTTPS 通道。";
        }
      }
    } finally {
      isPolling = false;
    }
  }
  poll();
  window.setInterval(poll, POLL_MS);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") poll();
  });
})();
