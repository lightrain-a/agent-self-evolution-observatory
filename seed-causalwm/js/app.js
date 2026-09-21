/* ============================================================
   Seed 2.1 pro — CausalWM: Causal Cascade instrument
   All pixels: official CausalWM first frames + official
   panel_flow_pointmap_rgb.mp4 (flow | pointmap | rgb).
   ============================================================ */

(() => {
"use strict";

const CASES = {
  "0007": {
    name: "Bottle to drawer",
    instruction: "The robotic gripper picks up the blue bottle on the bathroom counter and places it in the open drawer."
  },
  "0090": {
    name: "Close the drawer",
    instruction: "The robotic gripper closes the file cabinet drawer."
  },
  "0099": {
    name: "Retrieve the bottle",
    instruction: "The robotic gripper retrieves the deep red glass bottle from the refrigerator."
  }
};

const PHASE_STAGE = ["obs", "flow", "pointmap", "rgb", "rgb"]; // 4 = end hold
const NODE_FOR_PHASE = [0, 1, 2, 3, 3];
const OBS_HOLD = 1.5;
const END_HOLD = 1.8;

const FACE_TAG = ["OBSERVATION", "OPTICAL FLOW", "POINTMAPS", "FUTURE RGB", "FUTURE RGB"];
const STAGE_CAPTION = [
  "One first frame and one instruction — no depth, no future frames.",
  "Thought 1 · optical flow predicts motion from the observation and the instruction.",
  "Thought 2 · XYZ pointmaps predict geometry, reading the completed flow.",
  "Future RGB · reads the observation and both completed thoughts.",
  "Future RGB · reads the observation and both completed thoughts."
];
const CALLOUT = {
  obs: {
    title: "OBSERVATION — reads only itself",
    body: "The observed frame is a pure encoding of the scene. It cannot see motion, geometry or future frames, which blocks information from leaking backward into the starting image."
  },
  flow: {
    title: "MOTION — reads observation + instruction",
    body: "Optical flow is predicted first, from the observed video and the instruction (or robot actions). It cannot read pointmaps or future RGB: nothing upstream exists yet."
  },
  pointmap: {
    title: "GEOMETRY — reads observation + completed flow",
    body: "Camera-frame XYZ pointmaps are predicted with the finished optical flow held fixed as context. They cannot read the future RGB stage."
  },
  rgb: {
    title: "FUTURE RGB — reads everything upstream",
    body: "The future video reads the observation and both completed “thoughts” — flow and pointmaps — frozen and reused as context. Later-to-earlier paths do not exist."
  }
};
const BEAM_COLOR = { obs: "#9fb0b9", flow: "#38d6cd", pointmap: "#a78bfa" };

/* ---------- DOM ---------- */

const $ = (id) => document.getElementById(id);
const instrument = $("instrument");
const rail = $("rail");
const railPulse = $("railPulse");
const railNodes = [...document.querySelectorAll(".rail-node")];
const callout = $("railCallout");
const faces = [...document.querySelectorAll(".face")];
const videos = {
  flow: $("vid-flow"),
  pointmap: $("vid-pointmap"),
  rgb: $("vid-rgb")
};
const stageEl = $("stage");
const veil = $("conceptualVeil");
const beamSvg = $("beamOverlay");
const dockTiles = {
  obs: document.querySelector('[data-tile="obs"]'),
  flow: document.querySelector('[data-tile="flow"]'),
  pointmap: document.querySelector('[data-tile="pointmap"]')
};
const scrubber = $("scrubber");
const playBtn = $("playBtn");
const replayBtn = $("replayBtn");
const timeReadout = $("timeReadout");
const modeToggle = $("modeToggle");
const viewBtn = $("viewBtn");
const stageCaptionEl = $("stageCaption");
const faceTagEl = $("faceTag");
const instructionText = $("instructionText");
const caseTabs = [...document.querySelectorAll(".case-tab")];
const lightbox = $("lightbox");
const lightboxImg = $("lightboxImg");

/* ---------- State ---------- */

let currentCase = "0007";
let phase = 0;            // 0..4
let playing = true;
let trio = false;
let conceptual = false;
let holdElapsed = 0;      // obs / endhold
let holdTimer = 0;
let mediaReady = false;
let mediaGate = makeGate();

function makeGate() {
  const g = {};
  g.promise = new Promise((res) => { g.resolve = res; });
  return g;
}
let calloutTimer = 0;
let animTokens = [];      // beam pulse animations
let lastFrameTs = 0;

const vidDuration = () => videos.flow.duration && isFinite(videos.flow.duration) ? videos.flow.duration : 7.5625;
const weights = () => [OBS_HOLD, vidDuration(), vidDuration(), vidDuration(), END_HOLD];

/* ---------- Media loading ---------- */

function onceCanPlay(v) {
  return new Promise((resolve) => {
    let settled = false;
    const ok = () => { if (!settled) { settled = true; resolve(true); } };
    const fail = () => { if (!settled) { settled = true; resolve(false); } };
    if (v.readyState >= 3 && isFinite(v.duration)) { ok(); return; }
    v.addEventListener("canplay", ok, { once: true });
    v.addEventListener("loadedmetadata", ok, { once: true });
    v.addEventListener("error", fail);
    setTimeout(fail, 12000);
  });
}

function seekableCovers(v) {
  if (!isFinite(v.duration) || v.seekable.length === 0) return false;
  return v.seekable.end(v.seekable.length - 1) >= v.duration * 0.8;
}

async function repairSeekable(v) {
  // On servers without HTTP range support a progressive load can finish with a
  // collapsed seekable range ([0,0]), sending every later seek back to frame 0.
  // Reloading re-establishes the range. Give a progressive download a moment to
  // expand before concluding it is broken.
  if (seekableCovers(v)) return true;
  await new Promise((r) => setTimeout(r, 250));
  if (seekableCovers(v)) return true;
  v.load();
  await onceCanPlay(v);
  await new Promise((r) => setTimeout(r, 100));
  return seekableCovers(v);
}

async function loadCaseMedia(id, { autoplay = true } = {}) {
  const base = `media/cases/${id}/`;
  mediaGate = makeGate();
  const results = await Promise.all(
    Object.values(videos).map(async (v) => {
      v.pause();
      v.innerHTML = "";
      const webm = document.createElement("source");
      webm.src = base + "panel.webm";
      webm.type = 'video/webm; codecs="vp9"';
      const mp4 = document.createElement("source");
      mp4.src = base + "panel.mp4";
      mp4.type = 'video/mp4; codecs="avc1.640028"';
      v.append(webm, mp4);
      v.load();
      return onceCanPlay(v);
    })
  );
  if (results.every(Boolean)) {
    await Promise.all(Object.values(videos).map(repairSeekable));
    await Promise.all(Object.values(videos).map((v) =>
      v.readyState >= 2 ? true : onceCanPlay(v)));
  }
  mediaReady = results.every(Boolean) && videos.flow.readyState >= 2;
  mediaGate.resolve();
  return mediaReady;
}

/* ---------- Phase control (cascade) ---------- */

function clearHold() {
  if (holdTimer) { clearTimeout(holdTimer); holdTimer = 0; }
}

function startHold(remaining) {
  clearHold();
  holdTimer = setTimeout(() => {
    holdTimer = 0;
    if (phase === 0) goPhase(1);
    else if (phase === 4) loopReset();
  }, Math.max(60, remaining * 1000));
}

function pauseCascade() {
  playing = false;
  clearHold();
  if (phase >= 1 && phase <= 3) {
    const v = videos[PHASE_STAGE[phase]];
    v.pause();
  }
  updatePlayButton();
}

function playCascade() {
  if (conceptual) exitConceptual();
  playing = true;
  if (phase === 0 || phase === 4) {
    startHold((phase === 0 ? OBS_HOLD : END_HOLD) - holdElapsed);
  } else if (phase >= 1 && phase <= 3) {
    const v = videos[PHASE_STAGE[phase]];
    const p = v.play();
    if (p && p.catch) p.catch(() => {});
  }
  updatePlayButton();
}

async function goPhase(next) {
  clearHold();
  const prev = phase;
  phase = next;
  holdElapsed = 0;

  if (next >= 1 && next <= 3) {
    if (!mediaReady) await mediaGate.promise;
    if (phase !== next) return; // stale after reset
    const name = PHASE_STAGE[next];
    // park earlier videos at end, later at start
    for (let i = 1; i <= 3; i++) {
      const vn = videos[PHASE_STAGE[i]];
      if (i < next) { vn.currentTime = vidDuration() - 0.001; vn.pause(); }
      else if (i > next) { vn.currentTime = 0; vn.pause(); }
    }
    const active = videos[name];
    active.currentTime = 0;
    if (playing) {
      const p = active.play();
      if (p && p.catch) p.catch(() => {});
    }
  } else if (next === 4) {
    videos.rgb.currentTime = vidDuration() - 0.001;
    if (playing) startHold(END_HOLD);
  } else if (next === 0 && playing) {
    startHold(OBS_HOLD);
  }

  applyVisuals(prev, next);
}

function loopReset() {
  // hide dock, reset rail, back to observation
  phase = 0;
  holdElapsed = 0;
  clearHold();
  Object.values(videos).forEach((v) => { v.pause(); try { v.currentTime = 0; } catch (e) {} });
  setDock([]);
  applyVisuals(4, 0);
  if (playing) startHold(OBS_HOLD);
}

/* ---------- Visuals ---------- */

function setFaceForPhase(p) {
  const stageName = PHASE_STAGE[p];
  faces.forEach((f) => f.classList.toggle("is-on", f.dataset.face === stageName));
}

function setDock(visible) {
  for (const key of ["obs", "flow", "pointmap"]) {
    dockTiles[key].hidden = !visible.includes(key);
  }
}

function dockForPhase(p) {
  if (p === 0) return [];
  if (p === 1) return ["obs"];
  if (p === 2) return ["obs", "flow"];
  return ["obs", "flow", "pointmap"]; // 3 rgb + 4 endhold
}

function applyVisuals(prev, next) {
  setFaceForPhase(next);

  // rail
  railNodes.forEach((node, i) => {
    const reach = i <= NODE_FOR_PHASE[next];
    node.classList.toggle("is-reachable", reach);
    node.classList.toggle("is-active", i === NODE_FOR_PHASE[next]);
  });
  rail.classList.toggle("severed", false);
  rail.classList.remove("progress-1", "progress-2", "progress-3");
  if (next >= 1) rail.classList.add("progress-1");
  if (next >= 2) rail.classList.add("progress-2");
  if (next >= 3) rail.classList.add("progress-3");

  // pulse position + color
  const positions = ["12.5%", "37.5%", "62.5%", "87.5%"];
  const colors = ["#9fb0b9", "#38d6cd", "#a78bfa", "#34d399"];
  const ni = NODE_FOR_PHASE[next];
  railPulse.style.left = positions[ni];
  railPulse.style.background = colors[ni];
  railPulse.style.boxShadow = `0 0 12px 2px ${colors[ni]}aa`;
  railPulse.classList.add("run");

  // dock + fly
  const dockList = dockForPhase(next);
  if (prev >= 0 && next > prev && next >= 1 && next <= 3) {
    const completedKey = next === 1 ? "obs" : PHASE_STAGE[next - 1];
    flyStageToDock(completedKey);
  }
  setDock(dockList);

  faceTagEl.textContent = FACE_TAG[next];
  stageCaptionEl.innerHTML = STAGE_CAPTION[next];
  rebuildBeams();
}

/* ---------- FLIP fly: stage -> dock ---------- */

function flyStageToDock(key) {
  const stageRect = stageEl.getBoundingClientRect();
  if (stageRect.width === 0) return;
  const tile = dockTiles[key];
  // tile gets unhidden synchronously by setDock after this call; show temporarily:
  const wasHidden = tile.hidden;
  if (wasHidden) tile.hidden = false;
  const tileRect = tile.getBoundingClientRect();
  if (wasHidden) tile.hidden = true;

  document.querySelectorAll(".fly-clone").forEach((c) => c.remove());

  const clone = document.createElement("div");
  clone.className = "fly-clone";
  clone.style.left = stageRect.left + "px";
  clone.style.top = stageRect.top + "px";
  clone.style.width = stageRect.width + "px";
  clone.style.height = stageRect.height + "px";
  const img = document.createElement("img");
  img.style.width = "100%";
  img.style.height = "100%";
  img.style.objectFit = key === "obs" ? "contain" : "fill";
  img.style.background = "#05080a";
  const base = `media/cases/${currentCase}/`;
  img.src = key === "obs" ? base + "input.jpg"
    : key === "flow" ? base + "flow_end.jpg"
    : base + "pointmap_end.jpg";
  clone.appendChild(img);
  document.body.appendChild(clone);

  requestAnimationFrame(() => {
    const dx = tileRect.left - stageRect.left;
    const dy = tileRect.top - stageRect.top;
    const sx = tileRect.width / stageRect.width;
    const sy = tileRect.height / stageRect.height;
    clone.animate(
      [
        { transform: "translate(0,0) scale(1,1)", borderRadius: "8px" },
        { transform: `translate(${dx}px,${dy}px) scale(${sx},${sy})`, borderRadius: "6px" }
      ],
      { duration: 620, easing: "cubic-bezier(.65,0,.25,1)", fill: "forwards" }
    ).onfinish = () => clone.remove();
  });

  // small flash on the destination tile once docked
  setTimeout(() => {
    if (tile.hidden) return;
    const flash = document.createElement("span");
    flash.className = "tile-flash";
    tile.appendChild(flash);
    setTimeout(() => flash.remove(), 850);
  }, 560);
}

/* ---------- Beams ---------- */

function clearBeamAnimations() {
  animTokens.forEach((t) => cancelAnimationFrame(t));
  animTokens = [];
}

function rebuildBeams({ animate = true } = {}) {
  clearBeamAnimations();
  // keep defs, remove the rest
  [...beamSvg.children].forEach((c) => {
    if (c.tagName !== "defs") c.remove();
  });
  if (trio) return;

  const svgRect = beamSvg.getBoundingClientRect();
  const stageRect = stageEl.getBoundingClientRect();
  const dockList = conceptual ? ["obs"] : dockForPhase(phase);
  if (!dockList.length || stageRect.width === 0) return;

  const n = dockList.length;
  const endSpread = Math.min(150, stageRect.width * 0.28);
  const endXs = n === 1 ? [0] : Array.from({ length: n }, (_, i) => -endSpread / 2 + (endSpread * i) / (n - 1));

  dockList.forEach((key, i) => {
    const tileRect = dockTiles[key].getBoundingClientRect();
    const x1 = tileRect.left + tileRect.width / 2 - svgRect.left;
    const y1 = tileRect.top - svgRect.top - 2;
    const x2 = stageRect.left + stageRect.width / 2 - svgRect.left + endXs[i];
    const y2 = stageRect.bottom - svgRect.top + 3;
    const cx = (x1 + x2) / 2;
    const cy = y1 - Math.max(26, (y2 - y1) * 0.16);
    const d = `M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`;

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", d);
    path.setAttribute("pathLength", "1");
    path.setAttribute("class", "beam-path");
    path.setAttribute("stroke", BEAM_COLOR[key]);
    if (conceptual) {
      path.classList.add("is-live");
      path.style.stroke = "var(--amber)";
      path.style.strokeDasharray = "4 5";
      const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
      const tileW = tileRect.width;
      t.setAttribute("x", x1 + tileW / 2 + 9);
      t.setAttribute("y", y1 + tileRect.height / 2 + 3);
      t.setAttribute("text-anchor", "start");
      t.setAttribute("class", "beam-direct is-show");
      t.textContent = "direct route";
      beamSvg.append(path, t);
      startBeamPulse(path, "#e8b96c", 0);
    } else {
      path.classList.add(animate ? "is-live" : "is-dim");
      if (!animate) {
        path.style.opacity = .9;
        path.style.strokeDashoffset = 0;
      }
      beamSvg.appendChild(path);
      startBeamPulse(path, BEAM_COLOR[key], i * 0.7);
    }
  });
}

function startBeamPulse(path, color, delay) {
  const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  dot.setAttribute("r", "2.4");
  dot.setAttribute("fill", color);
  dot.setAttribute("class", "beam-pulse-dot");
  beamSvg.appendChild(dot);

  const period = 2300;
  let start = 0;
  const tick = (ts) => {
    if (!start) start = ts + delay * 900;
    const t = (((ts - start) % period) + period) % period / period;
    if (ts >= start) {
      const pt = path.getPointAtLength(t);
      dot.setAttribute("cx", pt.x);
      dot.setAttribute("cy", pt.y);
      dot.classList.add("is-run");
    }
    animTokens.push(requestAnimationFrame(tick));
  };
  animTokens.push(requestAnimationFrame(tick));
}

/* ---------- Scrubber / progress ---------- */

function cascadeProgress() {
  const w = weights();
  const total = w.reduce((a, b) => a + b, 0);
  let acc = 0;
  for (let i = 0; i < phase; i++) acc += w[i];
  let local;
  if (phase === 0 || phase === 4) local = Math.min(holdElapsed, w[phase]);
  else local = videos[PHASE_STAGE[phase]].currentTime;
  return Math.min(1, (acc + Math.max(0, local)) / total);
}

function trioProgress() {
  return Math.max(0, Math.min(1, videos.flow.currentTime / vidDuration()));
}

function scrubCascade(frac) {
  pauseCascade();
  const w = weights();
  const total = w.reduce((a, b) => a + b, 0);
  const target = frac * total;
  let acc = 0;
  let targetPhase = 0;
  for (let i = 0; i < w.length; i++) {
    if (target <= acc + w[i] || i === w.length - 1) { targetPhase = i; break; }
    acc += w[i];
  }
  const local = Math.max(0, Math.min(w[targetPhase], target - acc));
  phase = targetPhase;
  holdElapsed = local;
  clearHold();

  if (mediaReady) {
    for (let i = 1; i <= 3; i++) {
      const vn = videos[PHASE_STAGE[i]];
      if (i < targetPhase) vn.currentTime = vidDuration() - 0.001;
      else if (i === targetPhase) vn.currentTime = (targetPhase === 4 ? vidDuration() : local) ;
      else vn.currentTime = 0;
      vn.pause();
    }
  }
  applyVisuals(-1, targetPhase);
}

function scrubTrio(frac) {
  pauseTrio();
  const t = frac * vidDuration();
  if (mediaReady) resetTrioStreams(null, t);
}

function setTickPositions() {
  const w = weights();
  const total = w.reduce((a, b) => a + b, 0);
  const bounds = [0, w[0], w[0] + w[1], w[0] + w[1] + w[2]];
  document.querySelectorAll(".scrub-ticks span").forEach((el, i) => {
    el.style.left = (bounds[i] / total * 100) + "%";
  });
}

/* ---------- Trio ---------- */

function resetTrioStreams(cb, target = 0) {
  const vs = Object.values(videos);
  let remaining = vs.length;
  let settled = false;
  function finish() {
    if (settled) return;
    settled = true;
    clearTimeout(timer);
    vs.forEach((v) => v.removeEventListener("seeked", onSeeked));
    if (cb) cb();
  }
  function onSeeked() {
    if (this._seekDone) return;
    this._seekDone = true;
    remaining--;
    if (remaining <= 0) finish();
  }
  vs.forEach((v) => {
    v._seekDone = false;
    v.pause();
    if (v._prevOnSeeked) v.removeEventListener("seeked", v._prevOnSeeked);
    v._prevOnSeeked = onSeeked;
    v.addEventListener("seeked", onSeeked);
    try { v.currentTime = target; } catch (e) {}
    if (Math.abs(v.currentTime - target) < 0.02) {
      // already at target — no seeked event will arrive
      queueMicrotask(() => { if (!v._seekDone) onSeeked.call(v); });
    }
  });
  const timer = setTimeout(finish, 1200);
}

function fitTrio() {
  if (!trio) return;
  const ha = document.querySelector(".hero-area");
  const w = ha.clientWidth;
  const hh = ha.clientHeight;
  const h = Math.max(140, Math.min(hh - 2, (w - 44) / (16 / 3)));
  stageEl.style.height = h + "px";
  stageEl.style.width = "auto";
}

function enterTrio() {
  if (conceptual) exitConceptual();
  trio = true;
  document.body.classList.add("trio-mode");
  viewBtn.setAttribute("aria-pressed", "true");
  const wasPlaying = playing;
  pauseCascade();
  clearHold();
  requestAnimationFrame(fitTrio);
  const afterGate = () => {
    if (!trio) return;
    resetTrioStreams(() => { if (wasPlaying) trioPlay(); });
  };
  if (mediaReady) afterGate();
  else mediaGate.promise.then(afterGate);
  rebuildBeams();
}

function exitTrio() {
  trio = false;
  document.body.classList.remove("trio-mode");
  viewBtn.setAttribute("aria-pressed", "false");
  pauseTrio();
  stageEl.style.height = "";
  stageEl.style.width = "";
  // restart the relay from the observation
  phase = 0;
  holdElapsed = 0;
  setDock([]);
  applyVisuals(-1, 0);
  if (playing) playCascade();
}

function trioPlay() {
  playing = true;
  Object.values(videos).forEach((v) => {
    const p = v.play();
    if (p && p.catch) p.catch(() => {});
  });
  updatePlayButton();
}

function pauseTrio() {
  playing = false;
  Object.values(videos).forEach((v) => v.pause());
  updatePlayButton();
}

/* ---------- Conceptual mode ---------- */

let conceptualSavedPlaying = true;

function enterConceptual() {
  conceptual = true;
  stageEl.classList.add("is-conceptual");
  veil.hidden = false;
  modeToggle.setAttribute("aria-checked", "true");
  if (trio) pauseTrio();
  else pauseCascade();
  rail.classList.add("severed");
  railPulse.classList.remove("run");
  setDock(["obs"]); // F and P are skipped in the paper's without-CoT setting
  rebuildBeams();
}

function exitConceptual() {
  conceptual = false;
  stageEl.classList.remove("is-conceptual");
  veil.hidden = true;
  modeToggle.setAttribute("aria-checked", "false");
  rail.classList.remove("severed");
  setDock(dockForPhase(phase));
  rebuildBeams();
}

/* ---------- UI helpers ---------- */

function updatePlayButton() {
  const pauseIcon = playBtn.querySelector(".ic-pause");
  const playIcon = playBtn.querySelector(".ic-play");
  if (playing) {
    pauseIcon.hidden = false;
    playIcon.hidden = true;
    playBtn.setAttribute("aria-label", "Pause");
  } else {
    pauseIcon.hidden = true;
    playIcon.hidden = false;
    playBtn.setAttribute("aria-label", "Play");
  }
}

function fmtTime(s) {
  s = Math.max(0, Math.floor(s));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

function updateReadout() {
  if (trio) {
    timeReadout.textContent = `F·P·V SYNC  ${fmtTime(videos.flow.currentTime)} / ${fmtTime(vidDuration())}`;
    return;
  }
  if (phase === 0) {
    timeReadout.textContent = `OBSERVE  ${fmtTime(holdElapsed)} / ${fmtTime(OBS_HOLD)}`;
  } else if (phase === 4) {
    timeReadout.textContent = `FUTURE  ${fmtTime(holdElapsed)} / ${fmtTime(END_HOLD)}`;
  } else {
    const v = videos[PHASE_STAGE[phase]];
    const names = ["", "MOTION", "GEOMETRY", "FUTURE"];
    timeReadout.textContent = `${names[phase]}  ${fmtTime(v.currentTime)} / ${fmtTime(vidDuration())}`;
  }
}

/* ---------- Rail callout ---------- */

function showCallout(stageKey) {
  const data = CALLOUT[stageKey];
  $("calloutTitle").textContent = data.title;
  $("calloutBody").textContent = data.body;
  callout.hidden = false;

  railNodes.forEach((node, i) => {
    const idx = ["obs", "flow", "pointmap", "rgb"].indexOf(stageKey);
    node.classList.toggle("is-reachable", i <= idx);
    node.classList.toggle("is-active", i === idx);
  });

  clearTimeout(calloutTimer);
  calloutTimer = setTimeout(hideCallout, 4200);
}

function hideCallout() {
  callout.hidden = true;
  clearTimeout(calloutTimer);
  // restore reachable set from actual phase
  railNodes.forEach((node, i) => {
    node.classList.toggle("is-reachable", i <= NODE_FOR_PHASE[phase]);
    node.classList.toggle("is-active", i === NODE_FOR_PHASE[phase]);
  });
}

/* ---------- Main animation loop ---------- */

function frame(ts) {
  if (!lastFrameTs) lastFrameTs = ts;
  const dt = Math.min(0.1, (ts - lastFrameTs) / 1000);
  lastFrameTs = ts;

  if (!trio) {
    if ((phase === 0 || phase === 4) && playing && !holdTimer && !conceptual) {
      holdElapsed += dt; // fallback if timer was throttled
    }
    // reconcile: playing a video phase
    if (playing && phase >= 1 && phase <= 3 && !conceptual) {
      const v = videos[PHASE_STAGE[phase]];
      if (v.ended || v.currentTime >= vidDuration() - 0.02) {
        if (phase === 3) goPhase(4);
        else goPhase(phase + 1);
      }
    }
  } else if (playing && mediaReady) {
    // trio: resume an unexpectedly paused stream; correct large drift with a cooldown
    const vs = Object.values(videos);
    const dur = vidDuration();
    const leader = Math.max(...vs.map((v) => v.currentTime));
    if (leader < dur - 0.1) {
      vs.forEach((v) => {
        if (v.paused) {
          const p = v.play();
          if (p && p.catch) p.catch(() => {});
        } else if (leader - v.currentTime > 1.0 && ts - (v.__lastFix || 0) > 2000) {
          v.__lastFix = ts;
          try { v.currentTime = leader; } catch (e) {}
        }
      });
    }
  }

  scrubber.value = Math.round((trio ? trioProgress() : cascadeProgress()) * 1000);
  updateReadout();
  requestAnimationFrame(frame);
}

/* ---------- Case switching ---------- */

async function switchCase(id) {
  if (id === currentCase) {
    // a re-click on the active tab restarts it
    if (trio) { const keep = playing; pauseTrio(); await startTrioCase(id, keep); }
    else { const keep = playing; pauseCascade(); await startCascadeCase(id, keep); }
    return;
  }
  currentCase = id;
  caseTabs.forEach((t) => t.classList.toggle("is-active", t.dataset.case === id));
  mediaReady = false;

  const base = `media/cases/${id}/`;
  $("obsImg").src = base + "input.jpg";
  $("tileObsImg").src = base + "input.jpg";
  $("tileFlowImg").src = base + "flow_end.jpg";
  $("tilePointmapImg").src = base + "pointmap_end.jpg";
  instructionText.textContent = CASES[id].instruction;

  if (trio) await startTrioCase(id);
  else await startCascadeCase(id);
}

async function startCascadeCase(id, wantPlay = true) {
  phase = 0;
  holdElapsed = 0;
  clearHold();
  setDock([]);
  applyVisuals(-1, 0);
  playing = true;
  startHold(OBS_HOLD);
  updatePlayButton();
  await loadCaseMedia(id);
  if (currentCase !== id) return;
  if (!wantPlay) pauseCascade();
}

async function startTrioCase(id, wantPlay = true) {
  playing = wantPlay;
  await loadCaseMedia(id);
  if (currentCase !== id || !trio) return;
  requestAnimationFrame(fitTrio);
  resetTrioStreams(() => { if (trio && playing) trioPlay(); });
}

/* ---------- Events ---------- */

playBtn.addEventListener("click", () => {
  if (conceptual) { exitConceptual(); playing = true; if (trio) trioPlay(); else playCascade(); return; }
  if (playing) { if (trio) pauseTrio(); else pauseCascade(); }
  else { if (trio) trioPlay(); else playCascade(); }
});

replayBtn.addEventListener("click", () => {
  if (conceptual) exitConceptual();
  if (trio) {
    const wasPlaying = playing;
    resetTrioStreams(() => { if (wasPlaying) trioPlay(); });
  } else {
    phase = 0; holdElapsed = 0;
    setDock([]);
    applyVisuals(-1, 0);
    playing = true;
    clearHold();
    startHold(OBS_HOLD);
    updatePlayButton();
  }
});

let scrubActive = false;
scrubber.addEventListener("pointerdown", () => { scrubActive = true; });
scrubber.addEventListener("pointerup", () => { scrubActive = false; });
scrubber.addEventListener("input", () => {
  const frac = Number(scrubber.value) / 1000;
  if (trio) scrubTrio(frac);
  else scrubCascade(frac);
});

viewBtn.addEventListener("click", () => {
  if (trio) exitTrio();
  else enterTrio();
});

modeToggle.addEventListener("click", () => {
  if (conceptual) {
    const keep = conceptualSavedPlaying;
    exitConceptual();
    if (keep) {
      playing = true;
      if (trio) trioPlay();
      else playCascade();
    }
  } else {
    conceptualSavedPlaying = playing;
    enterConceptual();
  }
});
modeToggle.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); modeToggle.click(); }
});

railNodes.forEach((node) => {
  node.addEventListener("click", () => {
    if (callout.hidden) showCallout(node.dataset.stage);
    else hideCallout();
  });
});

document.addEventListener("pointerdown", (e) => {
  if (!callout.hidden && !e.target.closest(".rail-wrap")) hideCallout();
});

caseTabs.forEach((tab) => {
  tab.addEventListener("click", () => switchCase(tab.dataset.case));
});

document.addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT") return;
  if (e.code === "Space" || e.key === "k") {
    e.preventDefault();
    playBtn.click();
  } else if (key_isReplay(e.key)) {
    replayBtn.click();
  } else if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
    const dir = e.key === "ArrowLeft" ? -1 : 1;
    const cur = Number(scrubber.value) / 1000;
    const next = Math.max(0, Math.min(1, cur + dir * 0.015));
    scrubber.value = Math.round(next * 1000);
    if (trio) scrubTrio(next); else scrubCascade(next);
  }
});
function key_isReplay(k) { return k === "r" || k === "R"; }

document.addEventListener("visibilitychange", () => {
  if (document.hidden) return;
  if (!playing || conceptual || trio) return;
  if (phase >= 1 && phase <= 3) {
    const v = videos[PHASE_STAGE[phase]];
    if (v.paused) { const p = v.play(); if (p && p.catch) p.catch(() => {}); }
    if (v.ended) { if (phase === 3) goPhase(4); else goPhase(phase + 1); }
  }
});

Object.entries(videos).forEach(([key, v]) => {
  v.addEventListener("ended", () => {
    if (!playing || conceptual || trio) return;
    if (phase >= 1 && phase <= 3 && PHASE_STAGE[phase] === key) {
      goPhase(phase === 3 ? 4 : phase + 1);
    }
  });
});

/* resize */
let resizeTimer = 0;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => { setTickPositions(); fitTrio(); rebuildBeams({ animate: false }); }, 120);
});
new ResizeObserver(() => { fitTrio(); rebuildBeams({ animate: false }); }).observe(instrument);

/* lightbox */
document.querySelectorAll(".fig-link").forEach((b) => {
  b.addEventListener("click", () => {
    lightboxImg.src = b.dataset.fig === "connected"
      ? "media/figures/connected.png"
      : "media/figures/comparison.png";
    lightbox.hidden = false;
  });
});
$("lightboxClose").addEventListener("click", () => { lightbox.hidden = true; });
lightbox.addEventListener("click", (e) => { if (e.target === lightbox) lightbox.hidden = true; });

/* ---------- Init ---------- */

function init() {
  instructionText.textContent = CASES[currentCase].instruction;
  updatePlayButton();
  setTickPositions();
  requestAnimationFrame(frame);
  // observation displays immediately; hold starts before videos finish loading
  playing = true;
  startHold(OBS_HOLD);
  loadCaseMedia(currentCase);
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
else init();

})();
