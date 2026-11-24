"""Builds a one-page project website in docs/ from the latest real-data results.

GitHub Pages publishes the docs/ folder. Every number on the page is read from
output/real, so re-running the analysis and then this keeps the site current.
Charts are drawn in the browser from data embedded in the page (no libraries),
so they stay sharp, follow light/dark mode and show values on hover.
"""
from __future__ import annotations

import html
import json
import shutil

import numpy as np
import pandas as pd

from . import config

REPO_URL = "https://github.com/HughFOD/gas-storage-forecast"

# Still copied so the README and older links keep working; the page draws its own charts.
CHARTS = ["forecast_vs_actual.png", "weather_vs_storage.png", "error_by_model.png", "error_over_time.png"]

FONTS = ("https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@500;600;700"
         "&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&display=swap")

CSS = r"""
:root{--paper:#eef1f4;--card:#fbfcfd;--ink:#13202e;--muted:#5d6975;--faint:#8996a3;--line:#e2e6ea;
--flame:#1d5fd1;--flame-soft:#dbe6f8;--heat:#c8541f;--heat-soft:#f6e1d6;--grid:#e9edf0;--link:#3a66a8;
--display:"Barlow Semi Condensed","Arial Narrow",sans-serif;--body:"Source Sans 3",-apple-system,"Segoe UI",sans-serif}
@media (prefers-color-scheme:dark){:root{--paper:#0c131b;--card:#141e28;--ink:#e6ecf2;--muted:#94a2b0;--faint:#6b7987;
--line:#1f2a36;--flame:#4f86e8;--flame-soft:#1d3254;--heat:#e0703a;--heat-soft:#4a2a1b;--grid:#1b2631;--link:#8eb0e6}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 var(--body)}
a{color:var(--link);text-decoration:none;text-underline-offset:3px}a:hover{text-decoration:underline}
a:focus-visible,button:focus-visible{outline:2px solid var(--flame);outline-offset:3px;border-radius:3px}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
.home{padding:16px 0 0;font-size:.85rem}.home a{color:inherit;text-decoration:none;opacity:.7}.home a:hover{opacity:1;text-decoration:underline}
.mast{padding:12px 0 0}
.mast .row{display:flex;justify-content:space-between;align-items:baseline;gap:12px}
.mast .kicker,.mast .brand,.mast a{white-space:nowrap}
@media (max-width:560px){.mast .kicker{font-size:.72rem;letter-spacing:.09em}.mast .brand{font-size:.95rem;letter-spacing:.1em}.mast .wide{display:none}}
.mast .row:first-child{padding-bottom:10px;border-bottom:2px solid var(--ink)}
.mast .row+.row{padding-top:8px;padding-bottom:8px;border-bottom:1px solid var(--line)}
.kicker{font-family:var(--display);font-weight:600;font-size:.82rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.mast .brand{font-family:var(--display);font-weight:700;font-size:1.05rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink)}
.mast .tail{display:flex;gap:22px;align-items:baseline}
h1,h2,h3{font-family:var(--display);font-weight:600;letter-spacing:-.005em}
h1{font-size:clamp(2.1rem,4.6vw,3.3rem);line-height:1.05;margin:40px 0 14px;max-width:15em}
h2{font-size:1.75rem;line-height:1.15;margin:0 0 6px}
h3{font-size:1.2rem;margin:0 0 4px}
.lede{font-size:1.08rem;color:var(--muted);max-width:40em;margin:0 0 30px}
section{padding:80px 0 0}
.sub{color:var(--muted);max-width:44em;margin:0 0 22px;font-size:.97rem}
.num{font-family:var(--display);font-variant-numeric:tabular-nums}

/* the call */
.call{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:26px 30px 24px;
box-shadow:0 1px 0 var(--line),0 18px 40px -28px rgba(20,40,70,.35)}
.call-head{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:6px}
.pill{display:inline-block;font-family:var(--display);font-weight:700;font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;
color:var(--flame);background:var(--flame-soft);padding:4px 10px;border-radius:999px}
.call .when{color:var(--muted);margin:0;font-size:.95rem}
.call .when b{color:var(--ink);font-weight:600}
.call-main{display:grid;grid-template-columns:1fr auto;gap:18px 48px;align-items:end;margin:14px 0 6px}
.figline{display:flex;align-items:baseline;gap:12px}
.call .fig{font-family:var(--display);font-weight:700;font-size:clamp(5.4rem,15vw,9.5rem);line-height:.82;
color:var(--flame);font-variant-numeric:tabular-nums;letter-spacing:-.025em}
.call .fig.out{color:var(--heat)}
.call .unit{font-family:var(--display);font-size:2rem;font-weight:600;color:var(--flame);opacity:.85}
.call .unit.out{color:var(--heat)}
.call .what{font-size:1.1rem;color:var(--ink);margin:12px 0 0}
.side{display:grid;gap:14px;min-width:220px;padding-left:28px;border-left:1px solid var(--line)}
.side .kicker{display:block;margin-bottom:2px}
.side .val{font-family:var(--display);font-weight:600;font-size:1.75rem;line-height:1.1;font-variant-numeric:tabular-nums;white-space:nowrap}
.side .val.avg{color:var(--heat)}
.side .val small{font-size:1rem;font-weight:500;color:var(--muted)}
.scale{margin:22px 0 4px;min-width:0}.scale svg{display:block;overflow:visible;max-width:100%}
.keys{display:flex;flex-wrap:wrap;gap:6px 22px;font-size:.86rem;color:var(--muted);margin:2px 0 0}
.keys span{display:inline-flex;align-items:center;gap:7px}
.keys .k-pred{width:11px;height:11px;border-radius:50%;background:var(--flame);box-shadow:0 0 0 3px var(--flame-soft)}
.keys .k-range{width:22px;height:10px;border-radius:3px;background:var(--flame-soft);border:1px solid var(--flame)}
.keys .k-avg{width:3px;height:14px;border-radius:1px;background:var(--heat)}
.keys .k-zero{width:0;height:14px;border-left:2px solid var(--muted)}
.notes{display:grid;grid-template-columns:1fr 1fr;gap:6px 28px;margin:18px 0 0;padding-top:16px;border-top:1px solid var(--line)}
.notes p{margin:0;color:var(--muted);font-size:.92rem}.notes b{color:var(--ink);font-weight:600}
.next{color:var(--muted);font-size:.92rem;margin:14px 2px 0}
@media (max-width:700px){.call{padding:22px 20px}.call-main{grid-template-columns:1fr}
.side{border-left:0;padding-left:0;border-top:1px solid var(--line);padding-top:14px;grid-template-columns:1fr 1fr}
.notes{grid-template-columns:1fr}.side .val{font-size:1.4rem}}

/* recent calls */
.tablewrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:12px}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums;font-size:.98rem}
th,td{padding:10px 14px;text-align:right;white-space:nowrap;border-bottom:1px solid var(--line)}
tbody tr:last-child td{border-bottom:0}
th{font-weight:600;color:var(--muted);font-size:.9rem;vertical-align:bottom;white-space:normal}
th:first-child,td:first-child{text-align:left}
tr.best td{font-weight:600;background:var(--flame-soft)}
.missbar{display:inline-block;height:8px;border-radius:0 4px 4px 0;background:var(--flame);vertical-align:middle;margin-left:8px}
.missbar.worse{background:var(--heat)}
.win{color:var(--flame);font-weight:600}.lose{color:var(--heat);font-weight:600}

/* scores */
.scores{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:0;background:var(--card);
border:1px solid var(--line);border-radius:12px;margin-bottom:18px}
.score{padding:18px 22px;border-left:1px solid var(--line)}
.score:first-child{border-left:0}
.score .kicker{display:block;margin-bottom:8px}
.score .v{font-family:var(--display);font-weight:700;font-size:2.4rem;line-height:1;font-variant-numeric:tabular-nums}
h3.minor{font-size:1.25rem;margin:34px 0 4px}
section>.kicker{display:block;margin-bottom:6px;color:var(--flame)}
.score .v small{font-size:1.1rem;font-weight:500;color:var(--muted)}
.score .l{color:var(--muted);font-size:.93rem;margin-top:6px}
@media (max-width:700px){.score{border-left:0;border-top:1px solid var(--line)}.score:first-child{border-top:0}}

/* charts */
.chart{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 18px 10px;margin:0 0 18px;position:relative}
.chart h3{margin:0 4px 2px}.chart p{margin:0 4px 8px;color:var(--muted);font-size:.93rem}
.legend{display:flex;flex-wrap:wrap;gap:4px 18px;margin:0 4px 6px;font-size:.88rem;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:7px}
.legend i{display:inline-block;width:18px;height:0;border-top:2px solid}
.legend i.band{height:10px;border:0;border-radius:2px}
.legend i.dot{width:8px;height:8px;border:0;border-radius:50%}
.plot{position:relative}.plot svg{display:block;width:100%;overflow:visible}
.plot text{font:12px var(--body);fill:var(--faint)}
.tip{position:absolute;pointer-events:none;background:var(--ink);color:var(--paper);font-size:.85rem;line-height:1.45;
padding:8px 11px;border-radius:8px;white-space:nowrap;opacity:0;transform:translate(-50%,0);z-index:2;transition:opacity .08s}
.tip b{font-weight:600}.tip .k{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;box-shadow:0 0 0 1.5px var(--paper)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media (max-width:820px){.grid2{grid-template-columns:1fr}}

/* how it works: genuinely a sequence */
.steps{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:26px}
.steps li{counter-increment:s;border-top:2px solid var(--ink);padding-top:12px}
.steps li::before{content:counter(s);font-family:var(--display);font-weight:700;font-size:1.5rem;color:var(--flame);display:block;line-height:1;margin-bottom:8px}
.steps p{margin:4px 0 0;color:var(--muted);font-size:.97rem}
.findings{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px 34px;margin:0}
.findings div{padding:2px 0}.findings p{margin:2px 0 0;color:var(--muted)}
.events{list-style:none;padding:0;margin:0;columns:2 300px;column-gap:34px}
.events li{break-inside:avoid;padding:9px 0;border-bottom:1px solid var(--line)}
.events .d{font-weight:600}
.glossary{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px 30px;margin:0}
.glossary dt{font-family:var(--display);font-weight:600;font-size:1.1rem}.glossary dd{margin:2px 0 0;color:var(--muted);font-size:.95rem}
footer{margin:72px 0 0;padding:20px 0 40px;border-top:1px solid var(--line);color:var(--muted);font-size:.9rem}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

JS = r"""
const D = __DATA__;
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const NS = "http://www.w3.org/2000/svg";
const el = (t, a, p) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); if (p) p.appendChild(e); return e; };
const sgn = v => (v > 0 ? "+" : v < 0 ? "−" : "") + Math.abs(Math.round(v)).toLocaleString();
const fmtD = s => new Date(s + "T12:00:00").toLocaleDateString("en-US", {month: "short", day: "numeric", year: "numeric"});
const MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function nice(lo, hi, n) {
  const span = hi - lo, step0 = span / n, mag = Math.pow(10, Math.floor(Math.log10(step0)));
  const step = [1, 2, 2.5, 5, 10].map(m => m * mag).find(s => s >= step0);
  const out = []; for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(6));
  return out;
}

/* Hero scale: model range, forecast, 5-year average and zero on one number line. */
function drawScale() {
  const host = document.getElementById("scale"); if (!host || !D.now) return;
  const n = D.now, W = Math.max(280, host.clientWidth || 600), H = 96, pad = 18;
  const lo = Math.min(n.lower, n.avg5, n.pred, 0), hi = Math.max(n.upper, n.avg5, n.pred, 0);
  const m = (hi - lo) * 0.12 + 3, a = lo - m, b = hi + m;
  const x = v => pad + (v - a) / (b - a) * (W - 2 * pad);
  const s = el("svg", {viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: "img",
    "aria-label": `Model range ${sgn(n.lower)} to ${sgn(n.upper)} Bcf, forecast ${sgn(n.pred)}, 5-year average ${sgn(n.avg5)}`}, host);
  const y = 44, out = n.pred < 0;
  const flame = css(out ? "--heat" : "--flame"), soft = css(out ? "--heat-soft" : "--flame-soft");
  const txt = (X, Y, t, st, anchor) => { const e = el("text", {x: X, y: Y, "text-anchor": anchor || "middle", style: st}, s); e.textContent = t; return e; };
  // axis
  el("line", {x1: pad, x2: W - pad, y1: y, y2: y, stroke: css("--line"), "stroke-width": 2, "stroke-linecap": "round"}, s);
  // zero reference
  if (a < 0 && b > 0) {
    el("line", {x1: x(0), x2: x(0), y1: y - 20, y2: y + 20, stroke: css("--muted"), "stroke-width": 2}, s);
  }
  // model range
  el("rect", {x: x(n.lower), y: y - 11, width: Math.max(3, x(n.upper) - x(n.lower)), height: 22, rx: 5,
    fill: soft, stroke: flame, "stroke-width": 1.2, "stroke-opacity": .55}, s);
  // 5-year average
  el("line", {x1: x(n.avg5), x2: x(n.avg5), y1: y - 17, y2: y + 17, stroke: css("--heat"), "stroke-width": 3.5, "stroke-linecap": "round"}, s);
  // forecast marker
  el("circle", {cx: x(n.pred), cy: y, r: 13, fill: flame, opacity: .18}, s);
  el("circle", {cx: x(n.pred), cy: y, r: 8, fill: flame, stroke: css("--card"), "stroke-width": 2.5}, s);
  // labels above: forecast and average, nudged apart if close
  let xp = x(n.pred), xa = x(n.avg5); const gap = 46;
  if (Math.abs(xp - xa) < gap) { const mid = (xp + xa) / 2, d = gap / 2 * (xp <= xa ? 1 : -1); xp = mid - d; xa = mid + d; }
  txt(xp, y - 24, sgn(n.pred), "font:700 15px var(--display);fill:" + flame);
  txt(xa, y - 24, sgn(n.avg5), "font:600 14px var(--display);fill:" + css("--heat"));
  // labels below: range endpoints and zero
  const below = "font:600 13px var(--display);fill:" + css("--ink");
  const xl = x(n.lower), xu = x(n.upper);
  txt(xl, y + 34, sgn(n.lower), below); txt(xu, y + 34, sgn(n.upper), below);
  if (a < 0 && b > 0 && Math.abs(x(0) - xl) > 30 && Math.abs(x(0) - xu) > 30)
    txt(x(0), y + 34, "0", "font:600 13px var(--display);fill:" + css("--muted"));
}

/* Generic line chart with hover crosshair. */
function lineChart(id, cfg) {
  const host = document.getElementById(id); if (!host) return;
  const tip = document.createElement("div"); tip.className = "tip";
  function render() {
    host.querySelectorAll("svg").forEach(e => e.remove());
    const W = Math.max(300, host.clientWidth), H = cfg.height || (W < 560 ? 260 : 320);
    const m = {l: 46, r: cfg.right || 14, t: 12, b: 28};
    const X = cfg.x, n = X.length;
    let lo = Infinity, hi = -Infinity;
    for (const s of cfg.series) for (const v of s.values) if (v != null) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
    if (cfg.band) for (let i = 0; i < n; i++) { if (cfg.band.lo[i] != null) lo = Math.min(lo, cfg.band.lo[i]); if (cfg.band.hi[i] != null) hi = Math.max(hi, cfg.band.hi[i]); }
    if (cfg.zero) { lo = Math.min(lo, 0); hi = Math.max(hi, 0); }
    const padY = (hi - lo) * 0.06; lo -= padY; hi += padY;
    const ticks = nice(lo, hi, 5); lo = Math.min(lo, ticks[0]); hi = Math.max(hi, ticks[ticks.length - 1]);
    const xs = i => m.l + i / (n - 1) * (W - m.l - m.r), ys = v => m.t + (hi - v) / (hi - lo) * (H - m.t - m.b);
    const s = el("svg", {viewBox: `0 0 ${W} ${H}`, height: H, role: "img", "aria-label": cfg.label});
    host.insertBefore(s, host.firstChild);
    for (const t of ticks) {
      el("line", {x1: m.l, x2: W - m.r, y1: ys(t), y2: ys(t), stroke: t === 0 && cfg.zero ? css("--faint") : css("--grid"), "stroke-width": 1}, s);
      el("text", {x: m.l - 8, y: ys(t) + 4, "text-anchor": "end"}, s).textContent = cfg.yfmt ? cfg.yfmt(t) : sgn(t);
    }
    // x labels
    const xl = cfg.xticks(X);
    for (const [i, lab] of xl) el("text", {x: xs(i), y: H - 8, "text-anchor": "middle"}, s).textContent = lab;
    if (cfg.marker != null) {
      el("line", {x1: xs(cfg.marker.i), x2: xs(cfg.marker.i), y1: m.t, y2: H - m.b, stroke: css("--faint"), "stroke-dasharray": "3 4"}, s);
      el("text", {x: xs(cfg.marker.i) + 6, y: m.t + 12, "text-anchor": "start"}, s).textContent = cfg.marker.text;
    }
    if (cfg.band) {
      let d = "", seg = [];
      const flush = () => { if (seg.length > 1) d += "M" + seg.map(i => xs(i) + "," + ys(cfg.band.hi[i])).join("L") + "L" + seg.slice().reverse().map(i => xs(i) + "," + ys(cfg.band.lo[i])).join("L") + "Z"; seg = []; };
      for (let i = 0; i < n; i++) { if (cfg.band.lo[i] != null && cfg.band.hi[i] != null) seg.push(i); else flush(); } flush();
      el("path", {d, fill: css(cfg.band.color), opacity: cfg.band.opacity || 1}, s);
    }
    for (const sr of cfg.series) {
      const col = css(sr.color);
      if (sr.dots) {
        for (let i = 0; i < n; i++) if (sr.values[i] != null) el("circle", {cx: xs(i), cy: ys(sr.values[i]), r: W < 560 ? 2.4 : 3, fill: col}, s);
        continue;
      }
      let d = "", pen = false;
      for (let i = 0; i < n; i++) { const v = sr.values[i]; if (v == null) { pen = false; continue; } d += (pen ? "L" : "M") + xs(i).toFixed(1) + "," + ys(v).toFixed(1); pen = true; }
      el("path", {d, fill: "none", stroke: col, "stroke-width": sr.width || 2, "stroke-dasharray": sr.dash || "", "stroke-linejoin": "round", "stroke-linecap": "round"}, s);
      if (sr.end) { // direct label at the last point
        let j = n - 1; while (j > 0 && sr.values[j] == null) j--;
        el("text", {x: xs(j) + 6, y: ys(sr.values[j]) + 4, style: "font:600 12px var(--body);fill:" + css("--muted")}, s).textContent = sr.end;
      }
    }
    // hover
    const cross = el("line", {y1: m.t, y2: H - m.b, stroke: css("--faint"), "stroke-width": 1, opacity: 0}, s);
    const dots = cfg.series.map(sr => el("circle", {r: 4.5, fill: css(sr.color), stroke: css("--card"), "stroke-width": 2, opacity: 0}, s));
    const hit = el("rect", {x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: "transparent"}, s);
    const move = ev => {
      const r = s.getBoundingClientRect(), px = (ev.touches ? ev.touches[0].clientX : ev.clientX) - r.left;
      const i = Math.max(0, Math.min(n - 1, Math.round((px * W / r.width - m.l) / (W - m.l - m.r) * (n - 1))));
      cross.setAttribute("x1", xs(i)); cross.setAttribute("x2", xs(i)); cross.setAttribute("opacity", 1);
      let rows = "";
      cfg.series.forEach((sr, k) => {
        const v = sr.values[i];
        if (v == null) { dots[k].setAttribute("opacity", 0); return; }
        dots[k].setAttribute("cx", xs(i)); dots[k].setAttribute("cy", ys(v)); dots[k].setAttribute("opacity", 1);
        rows += `<br><span class=k style="background:${css(sr.color)}"></span>${sr.name}: <b>${cfg.yfmt ? cfg.yfmt(v) : sgn(v)}</b>`;
      });
      if (cfg.band && cfg.band.lo[i] != null && cfg.band.name) rows += `<br>${cfg.band.name}: ${cfg.yfmt ? cfg.yfmt(cfg.band.lo[i]) : sgn(cfg.band.lo[i])} to ${cfg.yfmt ? cfg.yfmt(cfg.band.hi[i]) : sgn(cfg.band.hi[i])}`;
      tip.innerHTML = `<b>${cfg.xfmt(X[i], i)}</b>` + rows;
      tip.style.left = Math.min(Math.max(xs(i) * r.width / W, 90), r.width - 90) + "px";
      tip.style.top = (m.t * r.height / H + 4) + "px"; tip.style.opacity = 1;
    };
    const leave = () => { cross.setAttribute("opacity", 0); dots.forEach(d => d.setAttribute("opacity", 0)); tip.style.opacity = 0; };
    hit.addEventListener("pointermove", move); hit.addEventListener("pointerleave", leave);
    hit.addEventListener("touchstart", move, {passive: true});
  }
  host.appendChild(tip); render();
  let t; new ResizeObserver(() => { clearTimeout(t); t = setTimeout(render, 80); }).observe(host);
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);
}

const monthTicks = (X, every) => {
  const out = []; let last = "";
  X.forEach((d, i) => { const dt = new Date(d + "T12:00:00"), k = dt.getFullYear() + "-" + dt.getMonth();
    if (k !== last && dt.getDate() <= 7 && dt.getMonth() % every === 0) out.push([i, dt.getMonth() === 0 ? String(dt.getFullYear()) : MON[dt.getMonth()]]); last = k; });
  return out;
};

const redrawScale = () => { const h = document.getElementById("scale"); if (h) { h.innerHTML = ""; drawScale(); } };
drawScale();
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", redrawScale);
if (document.getElementById("scale")) { let st; new ResizeObserver(() => { clearTimeout(st); st = setTimeout(redrawScale, 80); }).observe(document.getElementById("scale")); }
if (document.fonts) document.fonts.ready.then(redrawScale);

lineChart("c-level", {
  label: "Gas in storage this year compared with last year and the 5-year range",
  x: D.level.week, band: {lo: D.level.min, hi: D.level.max, color: "--grid", name: "5-yr range"},
  series: [
    {name: "5-yr average", values: D.level.avg, color: "--faint", dash: "5 4", width: 1.5},
    {name: String(D.level.prev_year), values: D.level.prev, color: "--heat", width: 2},
    {name: String(D.level.year), values: D.level.cur, color: "--flame", width: 2.5}],
  yfmt: v => Math.round(v).toLocaleString(),
  xfmt: (w, i) => "Week " + w + (D.level.dates[i] ? ", " + D.level.dates[i] : ""),
  xticks: X => [[0, "Jan"], [8, "Mar"], [17, "May"], [26, "Jul"], [35, "Sep"], [43, "Nov"]].filter(([i]) => i < X.length),
});

lineChart("c-pred", {
  label: "Model predictions compared with what EIA reported, last two years",
  x: D.pred.week, zero: true,
  band: {lo: D.pred.lower, hi: D.pred.upper, color: "--flame-soft", name: "Model range"},
  series: [
    {name: "5-year average", values: D.pred.avg5, color: "--heat", dash: "4 4", width: 1.5},
    {name: "Model forecast", values: D.pred.pred, color: "--flame", width: 2},
    {name: "EIA reported", values: D.pred.actual, color: "--ink", dots: true}],
  xfmt: d => "Week ending " + fmtD(d), xticks: X => monthTicks(X, 3),
});

lineChart("c-err", {
  label: "Average miss over the previous 26 weeks, model compared with the 5-year average",
  x: D.err.week, height: 260, right: 14,
  series: [
    {name: "5-year average", values: D.err.avg5, color: "--heat", width: 2},
    {name: "Model", values: D.err.model, color: "--flame", width: 2}],
  yfmt: v => Math.round(v) + " Bcf", xfmt: d => "26 weeks to " + fmtD(d),
  xticks: X => monthTicks(X, 12),
  marker: D.err.holdout_i != null ? {i: D.err.holdout_i, text: "Unseen weeks start"} : null,
});

lineChart("c-weather", {
  label: "Heating degree days and storage change by week, last three winters and summers",
  x: D.wx.week, height: 260, zero: true,
  series: [
    {name: "Storage change (Bcf)", values: D.wx.chg, color: "--flame", width: 2},
    {name: "Colder than normal (scaled)", values: D.wx.hdd, color: "--heat", width: 1.5, dash: "4 3"}],
  xfmt: d => "Week ending " + fmtD(d), xticks: X => monthTicks(X, 6),
});
"""


def _fmt(x, d=1):
    return "–" if pd.isna(x) else f"{x:.{d}f}"


def _sgn(v, d=0):
    if pd.isna(v):
        return "–"
    s = f"{abs(v):,.{d}f}"
    return ("+" if v > 0 else "−" if v < 0 and s.strip("0.,") else "") + s


def _clean(a):
    return [None if (v is None or (isinstance(v, float) and np.isnan(v))) else round(float(v), 1) for v in a]


def _level_data(wf: pd.DataFrame) -> dict:
    s = wf.dropna(subset=["storage_bcf"]).copy()
    s["year"] = s["week_ending"].dt.year
    s["wk"] = s["week_ending"].dt.isocalendar().week.clip(upper=52).astype(int)
    s = s.groupby(["year", "wk"], as_index=False).agg(storage=("storage_bcf", "last"), date=("week_ending", "last"))
    year = int(s["year"].max())
    piv = s.pivot(index="wk", columns="year", values="storage").reindex(range(1, 53))
    hist = piv[[y for y in range(year - 5, year) if y in piv]]
    dates = s[s["year"] == year].set_index("wk")["date"].reindex(range(1, 53))
    return {"week": list(range(1, 53)), "year": year, "prev_year": year - 1,
            "cur": _clean(piv.get(year, pd.Series(index=piv.index, dtype=float))),
            "prev": _clean(piv.get(year - 1, pd.Series(index=piv.index, dtype=float))),
            "min": _clean(hist.min(axis=1)), "max": _clean(hist.max(axis=1)), "avg": _clean(hist.mean(axis=1)),
            "dates": [None if pd.isna(d) else f"{d:%b %-d}" for d in dates]}


def build(src=None, dest=None) -> str:
    src = src or config.OUTPUT / "real"
    dest = dest or config.ROOT / "docs"
    (dest / "img").mkdir(parents=True, exist_ok=True)
    info = json.loads((src / "best.json").read_text()) if (src / "best.json").exists() else {}
    hold_file = src / "metrics_holdout.csv"
    m = pd.read_csv(hold_file if hold_file.exists() else src / "metrics.csv")
    pred = pd.read_csv(src / "predictions.csv", parse_dates=["week_ending"])
    q = pd.read_csv(src / "quality.csv", parse_dates=["week_ending"])
    now = pd.read_csv(src / "nowcast.csv", parse_dates=["week_ending"]) if (src / "nowcast.csv").exists() else None
    wf = pd.read_csv(src / "weekly_features.csv", parse_dates=["week_ending"])

    a = m[m["season"] == "all year"].set_index("model")
    from .report import MODEL_NAMES
    best = info.get("best") or a.loc[MODEL_NAMES, "MAE (Bcf)"].idxmin()
    b, avg = a.loc[best], a.loc["5-year average"]
    s = m.set_index(["model", "season"])
    win_b, win_a = s.loc[(best, "withdrawal"), "MAE (Bcf)"], s.loc[("5-year average", "withdrawal"), "MAE (Bcf)"]
    sum_b, sum_a = s.loc[(best, "injection"), "MAE (Bcf)"], s.loc[("5-year average", "injection"), "MAE (Bcf)"]
    last = pred["week_ending"].max()
    lv = wf.dropna(subset=["storage_bcf"])
    level, level_week = lv["storage_bcf"].iloc[-1], lv["week_ending"].iloc[-1]
    hold_from = pd.Timestamp(info.get("holdout_from", config.HOLDOUT_START))
    chosen_on = info.get("chosen_on", f"{pred['week_ending'].min():%Y}-{hold_from.year - 1}")

    for f in CHARTS:
        if (src / f).exists():
            shutil.copy(src / f, dest / "img" / f)

    # ---- data for the charts -------------------------------------------------
    pb = pred[pred["model"] == best].sort_values("week_ending")
    p5 = pred[pred["model"] == "5-year average"].sort_values("week_ending")
    recent = pb[pb["week_ending"] > last - pd.DateOffset(years=2)]
    data = {"level": _level_data(wf),
            "pred": {"week": [f"{d:%Y-%m-%d}" for d in recent["week_ending"]], "pred": _clean(recent["pred"]),
                     "actual": _clean(recent["actual"]), "avg5": _clean(recent["avg5"]),
                     "lower": _clean(recent["lower"]), "upper": _clean(recent["upper"])}}
    eb = (pb.set_index("week_ending")["pred"] - pb.set_index("week_ending")["actual"]).abs().rolling(26).mean()
    ea = (p5.set_index("week_ending")["pred"] - p5.set_index("week_ending")["actual"]).abs().rolling(26).mean()
    err = pd.DataFrame({"model": eb, "avg5": ea}).dropna()
    hi = int(np.searchsorted(err.index.values, np.datetime64(hold_from)))
    data["err"] = {"week": [f"{d:%Y-%m-%d}" for d in err.index], "model": _clean(err["model"]),
                   "avg5": _clean(err["avg5"]), "holdout_i": hi if 0 < hi < len(err) else None}
    wx = wf[wf["week_ending"] > wf["week_ending"].max() - pd.DateOffset(years=3)].dropna(subset=["change_bcf"])
    sc = wx["change_bcf"].abs().max() / max(wx["hdd_dev"].abs().max(), 1)
    data["wx"] = {"week": [f"{d:%Y-%m-%d}" for d in wx["week_ending"]], "chg": _clean(wx["change_bcf"]),
                  "hdd": _clean((-wx["hdd_dev"] * sc).where(wx["week_ending"].dt.month.isin([11, 12, 1, 2, 3])))}

    # ---- the call -------------------------------------------------------------
    call_html, next_html = "<p class=sub>No prediction is waiting for an EIA report right now.</p>", ""
    if now is not None and not now.empty:
        nb = now[now["model"] == best].sort_values("week_ending")
        if not nb.empty:
            r = nb.iloc[0]
            wk = r["week_ending"]
            data["now"] = {k: round(float(r[k]), 1) for k in ["pred", "lower", "upper", "avg5"]}
            out = r["pred"] < 0
            fc = int(r.get("forecast_days", 0) or 0)
            fc_note = (f"{fc} of the 7 days in this forecast still rely on weather projections, slightly increasing uncertainty."
                       if fc else "All 7 days of weather in this forecast are already measured.")
            u = " out" if out else ""
            call_html = f"""<article class=call aria-labelledby=call-h>
<div class=call-head><span class=pill id=call-h>Model forecast</span>
<p class=when>Week ending <b>{wk:%a, %b %-d}</b>. EIA reports <b>{wk + pd.Timedelta(days=6):%A, %b %-d}, 10:30 a.m. ET</b></p></div>
<div class=call-main>
<div><span class=kicker>Weekly estimate</span>
<div class=figline><div class="fig{u}">{_sgn(r['pred'])}</div><div class="unit{u}">Bcf</div></div>
<p class=what>Expected net {'withdrawal from' if out else 'addition to'} natural gas storage</p></div>
<div class=side>
<div><span class=kicker>Model range</span><div class=val>{_sgn(r['lower'])} to {_sgn(r['upper'])} <small>Bcf</small></div></div>
<div><span class=kicker>5-year average</span><div class="val avg">{_sgn(r['avg5'])} <small>Bcf</small></div></div>
</div></div>
<div class=scale id=scale></div>
<div class=keys><span><i class=k-pred></i>Model forecast</span><span><i class=k-range></i>Model range (80%)</span>
<span><i class=k-avg></i>5-year average</span><span><i class=k-zero></i>Zero (no change)</span></div>
<div class=notes>
<p><b>Forecast range: {_sgn(r['lower'])} to {_sgn(r['upper'])} Bcf.</b> Based on the model's past performance, 80% of actual storage reports are expected to fall within this range.</p>
<p><b>The five-year average for this reporting week is {_sgn(r['avg5'])} Bcf.</b> {fc_note}</p>
</div></article>"""
            if len(nb) > 1:
                r2 = nb.iloc[1]
                next_html = (f"<p class=next>Looking a week further, the early estimate for the week ending "
                             f"{r2['week_ending']:%B %-d} is {'about zero' if abs(r2['pred']) < 0.5 else _sgn(r2['pred']) + ' Bcf'}, based mostly on weather forecasts.</p>")

    # ---- recent calls ---------------------------------------------------------
    rc = pb.dropna(subset=["actual"]).tail(8).iloc[::-1]
    maxmiss = max(1.0, float((rc["pred"] - rc["actual"]).abs().max()))
    rec_rows = ""
    for _, r in rc.iterrows():
        miss = abs(r["pred"] - r["actual"])
        miss5 = abs(r["avg5"] - r["actual"])
        better = miss < miss5
        rec_rows += (f"<tr><td>{r['week_ending']:%b %-d, %Y}</td><td>{_sgn(r['pred'])}</td><td><b>{_sgn(r['actual'])}</b></td>"
                     f"<td>{_sgn(r['avg5'])}</td><td>{miss:.0f}<span class='missbar{'' if better else ' worse'}' "
                     f"style='width:{6 + 70 * miss / maxmiss:.0f}px'></span></td>"
                     f"<td class={'win' if better else 'lose'}>{'Model' if better else '5-year average'}</td></tr>")
    hold = pb[(pb["week_ending"] >= hold_from)].dropna(subset=["actual"])
    h_err = (hold["pred"] - hold["actual"]).abs()
    h_err5 = (hold["avg5"] - hold["actual"]).abs()
    med_b, med_a = float(h_err.median()), float(h_err5.median())
    closer = float((h_err < h_err5).mean() * 100)
    wins = int(sum(abs(r['pred'] - r['actual']) < abs(r['avg5'] - r['actual']) for _, r in rc.iterrows()))

    # ---- method table ---------------------------------------------------------
    plain = {"5-year average": "Standard guess (5-year average)",
             "Weather-adjusted 5-yr avg": "5-year average, adjusted for weather",
             "Gradient boosting": "Gradient-boosted trees", "Ridge regression": "Ridge regression",
             "Same week last year": "Same week last year", "Last week's change": "Same as last week"}
    plain[best] = f"This model ({best.lower()})"
    rows = "".join(
        f"<tr{' class=best' if name == best else ''}><td>{html.escape(plain.get(name, name))}</td>"
        f"<td>{_fmt(r['MAE (Bcf)'])}</td><td>{_fmt(r['beats 5-yr avg (% of weeks)'], 0)}%</td>"
        f"<td>{_fmt(r['surprise direction right (%)'], 0)}{'%' if pd.notna(r['surprise direction right (%)']) else ''}</td>"
        f"<td>{_fmt(r['80% range covered (%)'], 0)}%</td></tr>"
        for name, r in pd.concat([a.loc[[best]], a.drop(index=best)]).iterrows())

    flagged = ""
    for _, r in q[q["check"] == "unexplained change"].iterrows():
        try:
            eia = r["detail"].split(" Bcf vs model ")[0].replace("EIA ", "")
            mod = r["detail"].split(" Bcf vs model ")[1].split(" (")[0]
            flagged += (f"<li><span class=d>Week ending {r['week_ending']:%b %-d, %Y}</span><br>"
                        f"EIA reported {eia} Bcf; the model said {mod}.</li>")
        except (IndexError, AttributeError):
            continue
    pct = (1 - b["MAE (Bcf)"] / avg["MAE (Bcf)"]) * 100
    today = pd.Timestamp.now(tz="America/New_York")
    repo = f"<a href='{REPO_URL}'>Code on GitHub</a>" if REPO_URL else ""

    page = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Natural gas storage forecast | Hugh O'Donnell</title>
<meta name=description content="A weather-driven prediction of the weekly EIA natural gas storage report, with its full track record.">
<meta property="og:title" content="Natural gas storage forecast"><meta property="og:description" content="This week: {_sgn(data['now']['pred']) + ' Bcf' if 'now' in data else 'weekly EIA storage predictions'}. Track record since 2018.">
<link rel=preconnect href=https://fonts.googleapis.com><link rel=preconnect href=https://fonts.gstatic.com crossorigin>
<link rel=stylesheet href="{FONTS}">
<link rel=canonical href="https://hughod.com/gas-storage-forecast/">
<link rel=icon href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cpath d='M16 3c3 6 9 9 9 16a9 9 0 0 1-18 0c0-4 2-6 4-8 0 3 1 5 3 5-1-5 0-9 2-13z' fill='%231d5fd1'/%3E%3C/svg%3E">
<style>{CSS}</style></head><body>
<div class=wrap>
<div class=home><a href="https://hughod.com/">Hugh O'Donnell</a></div>
<header class=mast>
<div class=row><span class=brand>Gas Storage Forecast</span><span class="kicker wide">Energy markets</span></div>
<div class=row><span class=kicker>Weekly EIA prediction</span><span class=tail><span class=kicker>{today:%B %-d, %Y}</span><span class=wide>{repo}</span></span></div>
</header>

<h1>What will Thursday's gas storage report show?</h1>
<p class=lede>Each Thursday the US Energy Information Administration reports how much natural gas went into or out of
underground storage the week before, and gas prices move when the number surprises traders. This model forecasts it
from the weather before the report, using only what was known that morning.</p>

{call_html}
{next_html}

<section>
<span class=kicker>Track record</span>
<h2>How the model has performed</h2>
<p class=sub>Scored on {len(hold)} weekly reports from {hold_from:%Y} to {last:%Y}. The model was designed using {chosen_on} only,
so none of these weeks were used to build it, and every forecast used only data from before that week's report.</p>
<div class=scores>
<div class=score><span class=kicker>Average miss</span><div class=v>{b['MAE (Bcf)']:.0f} <small>Bcf</small></div><div class=l>vs {avg['MAE (Bcf)']:.0f} Bcf for the 5-year average, {pct:.0f}% smaller</div></div>
<div class=score><span class=kicker>Median miss</span><div class=v>{med_b:.0f} <small>Bcf</small></div><div class=l>vs {med_a:.0f} Bcf for the 5-year average</div></div>
<div class=score><span class=kicker>Closer than baseline</span><div class=v>{closer:.0f}%</div><div class=l>of weeks the model beat the 5-year average</div></div>
<div class=score><span class=kicker>Direction right</span><div class=v>{b['surprise direction right (%)']:.0f}%</div><div class=l>called whether the report would land above or below the 5-year average</div></div>
</div>
<h3 class=minor>Last eight reports</h3>
<p class=sub>The model was closer than the 5-year average in {wins} of them. Positive numbers mean gas went into storage; negative, out.</p>
<div class=tablewrap><table><thead><tr><th>Week ending</th><th>Model forecast</th><th>EIA reported</th><th>5-year average</th>
<th>Model's miss (Bcf)</th><th>Closer</th></tr></thead><tbody>{rec_rows}</tbody></table></div>
<div class=chart style="margin-top:18px"><h3>Forecast against actual, last two years</h3>
<div class=legend><span><i style="border-color:var(--flame)"></i>Model forecast</span><span><i class=band style="background:var(--flame-soft)"></i>Model range (80%)</span>
<span><i class=dot style="background:var(--ink)"></i>EIA reported</span><span><i style="border-color:var(--heat);border-top-style:dashed"></i>5-year average</span></div>
<div class=plot id=c-pred></div></div>
<div class=chart><h3>Typical miss over time</h3><p>Average miss over the previous 26 weeks. Winters push both lines up; the model rises much less.</p>
<div class=legend><span><i style="border-color:var(--flame)"></i>Model</span><span><i style="border-color:var(--heat)"></i>5-year average</span></div>
<div class=plot id=c-err></div></div>
</section>

<section>
<h2>Where storage stands</h2>
<p class=sub>US underground storage held <b class=num>{level:,.0f} Bcf</b> in the week ending {level_week:%B %-d, %Y}.
It fills from April to October and drains through the winter.</p>
<div class=chart><h3>Gas in storage, {data['level']['year']} against recent years (Bcf)</h3>
<div class=legend><span><i style="border-color:var(--flame);border-top-width:3px"></i>{data['level']['year']}</span>
<span><i style="border-color:var(--heat)"></i>{data['level']['prev_year']}</span>
<span><i class=band style="background:var(--grid)"></i>Range of the previous 5 years</span>
<span><i style="border-color:var(--faint);border-top-style:dashed"></i>5-year average</span></div>
<div class=plot id=c-level></div></div>
</section>

<section>
<h2>How it works</h2>
<p class=sub>Most of the week-to-week swing is weather: cold weeks burn gas for heat, hot weeks burn it in power plants for air conditioning.</p>
<ol class=steps>
<li><h3>Measure the weather</h3><p>Daily temperatures from 17 cities become heating and cooling degree days, weighted toward
the gas-heated North-East and Midwest in winter and Texas, the South and California in summer.</p></li>
<li><h3>Start from the standard guess</h3><p>The average change for the same week over the past five years, the number
every storage report is compared with.</p></li>
<li><h3>Adjust for the weather</h3><p>A ridge regression learns how far colder or hotter than normal weather pushes storage
away from that average, along with last week's surprise.</p></li>
<li><h3>Test it the hard way</h3><p>Every past week is predicted using only earlier weeks, as if it were that Thursday
morning, then scored against what EIA actually reported.</p></li>
</ol>
<div class=chart style="margin-top:26px"><h3>Cold weeks drain storage</h3><p>Last three years. From November to March the dashed line shows how much colder than normal each week was
(scaled to fit, and flipped so colder points down). Storage change follows it closely.</p>
<div class=legend><span><i style="border-color:var(--flame)"></i>Storage change</span><span><i style="border-color:var(--heat);border-top-style:dashed"></i>Colder than normal</span></div>
<div class=plot id=c-weather></div></div>
</section>

<section>
<h2>What I found</h2>
<div class=findings>
<div><h3>Winter is where weather pays off</h3><p>From November to March the model misses by {win_b:.0f} Bcf on average;
the standard guess misses by {win_a:.0f}. Cold snaps cause the big swings, and temperature data catches them.</p></div>
<div><h3>Summer is harder to beat</h3><p>From April to October the model misses by {sum_b:.0f} Bcf against {sum_a:.0f}.
Summer weeks swing less, and they depend on things the model doesn't see yet, like LNG exports and power demand.</p></div>
<div><h3>Simple beat fancy</h3><p>A plain linear model beat gradient-boosted trees on unseen weeks.</p></div>
<div><h3>Big misses point to real events</h3><p>The largest was Winter Storm Uri in February 2021: frozen wells cut supply,
so storage fell further than the cold alone explains.</p></div>
</div>
</section>

<section>
<h2>Every method compared</h2>
<p class=sub>Weeks from {hold_from:%Y} onward. "Beat the standard guess" is the share of weeks a method was closer than the
5-year average. "Above or below right" is how often it called which side of the 5-year average the report would land on.
"Inside model range" should be close to 80%.</p>
<div class=tablewrap><table><thead><tr><th>Method</th><th>Typical miss (Bcf)</th><th>Beat the standard guess</th>
<th>Above or below right</th><th>Inside model range</th></tr></thead><tbody>{rows}</tbody></table></div>
</section>

<section>
<h2>Weeks the weather couldn't explain</h2>
<p class=sub>Weeks where the model missed far more than usual. These usually trace to events temperatures can't show:
frozen wells, pipeline or LNG outages, or EIA reclassifying gas.</p>
<ul class=events>{flagged}</ul>
</section>

<section>
<h2>Terms</h2>
<dl class=glossary>
<div><dt>Bcf</dt><dd>Billion cubic feet of gas. The US uses roughly 90 Bcf a day; one Bcf heats about 15,000 homes for a year.</dd></div>
<div><dt>Injection and withdrawal</dt><dd>Gas added to storage (positive, mostly April to October) or taken out (negative, mostly winter).</dd></div>
<div><dt>5-year average</dt><dd>The average change for the same week over the past five years: the market's standard guess.</dd></div>
<div><dt>Degree days</dt><dd>How far each day's average temperature was below 65°F (heating) or above it (cooling), added up over the week.</dd></div>
</dl>
</section>

<footer>Updated automatically every day after EIA's report; latest report in the data covers the week ending {last:%B %-d, %Y}.
Data from EIA's weekly working gas in storage (Lower 48) and Open-Meteo temperatures. Built with Python, pandas and scikit-learn.
{repo}</footer>
</div>
<script>{JS.replace("__DATA__", json.dumps(data, separators=(",", ":")))}</script>
</body></html>"""
    (dest / "index.html").write_text(page)
    return str(dest / "index.html")
