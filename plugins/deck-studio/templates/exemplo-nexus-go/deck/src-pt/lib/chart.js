// Shared chart helpers (docs/DESIGN.md §7): table access, formatting, scales, SVG marks,
// axis, and the frame every chart sits in (subtitle, legend, "Table" toggle, tooltip).
const NS = 'http://www.w3.org/2000/svg';

// ---------- numbers and labels ----------
export const fmt = (x, d = 2) => `${x < 0 ? '−' : ''}${Math.abs(x).toFixed(d).replace('.', ',')}`;
export const sg = (x, d = 2) => `${x < 0 ? '−' : '+'}${Math.abs(x).toFixed(d).replace('.', ',')}`;
export const pp = (x, d = 2) => `${sg(x, d)} p.p.`;
// LaTeX cell text -> plain text
export const plain = (v) => typeof v !== 'string' ? v : v
  .replace(/\\(?:textsc|textit|textbf|texttt|mathrm)\{([^}]*)\}/g, '$1')
  .replace(/\\gamma/g, 'γ').replace(/\\alpha/g, 'α').replace(/\\downarrow/g, '').replace(/\\(max|min)/g, '$1')
  .replace(/--/g, '–').replace(/>=\s*/g, '≥ ').replace(/[{}_^\\]/g, '').trim();

// colours: CSS variables only, so a theme switch needs no redraw
export const C = {
  seq: 'var(--seq)', net: 'var(--net)', fuse: 'var(--fuse)', ink2: 'var(--ink-2)',
  n1: 'var(--muted)', n2: 'color-mix(in srgb, var(--muted) 50%, var(--slide))',
  tint: (c, p) => `color-mix(in srgb, ${c} ${p}%, var(--slide))`,
};

// ---------- data ----------
// rows of a table, header first; an empty first cell repeats the group of the row above
export function rows(data, key) {
  const t = data && data[key];
  if (!t) throw new Error(`thesis_tables.json has no "${key}"`);
  const [head, ...body] = t.rows;
  let g = '';
  return {
    head: head.map(plain), caption: t.caption,
    body: body.map((r) => { g = r[0] === '' ? g : r[0]; return [plain(g), ...r.slice(1).map(plain)]; }),
  };
}
export function pick(body, ...key) {
  const r = body.find((x) => key.every((k, i) => x[i] === k));
  if (!r) throw new Error(`row ${key.join(' / ')} not found`);
  return r;
}
export const col = (t, name) => {
  const i = t.head.indexOf(name);
  if (i < 0) throw new Error(`column ${name} not found`);
  return i;
};

// ---------- scales and SVG ----------
export const lin = (d0, d1, r0, r1) => (v) => r0 + ((v - d0) * (r1 - r0)) / (d1 - d0);
export const range = (a, b, st) => Array.from({ length: Math.round((b - a) / st) + 1 }, (_, i) => +(a + i * st).toFixed(6));
export function s(parent, tag, attrs = {}, text) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v != null) e.setAttribute(k, v);
  if (text != null) e.textContent = text;
  if (parent) parent.append(e);
  return e;
}
// horizontal bar from baseline x0 to data end x1 (either direction): 4 px rounded end, square base
export function hbar(x0, x1, y, h, r = 4) {
  const d = x1 >= x0 ? 1 : -1, w = Math.abs(x1 - x0);
  r = Math.min(r, w, h / 2);
  const xe = x1 - d * r, sw = d > 0 ? 1 : 0;
  return `M${x0},${y}H${xe}A${r},${r} 0 0 ${sw} ${x1},${y + r}V${y + h - r}A${r},${r} 0 0 ${sw} ${xe},${y + h}H${x0}Z`;
}
// vertical gridlines and tick labels under the plot
export function axisX(g, x, ticks, y0, y1, f = String) {
  for (const t of ticks) {
    s(g, 'line', { class: 'grid', x1: x(t), x2: x(t), y1: y0, y2: y1 });
    s(g, 'text', { class: 'tick', x: x(t), y: y1 + 22, 'text-anchor': 'middle' }, f(t));
  }
}
// a hover/focus target: tooltip text in data-tv (value) and data-tl (label); step = reveal step
export function mark(parent, value, label, step) {
  const g = s(parent, 'g', {
    class: step == null ? 'mk' : 'mk o', 'data-s': step, tabindex: 0, 'data-interactive': '', role: 'img', 'aria-label': `${label}: ${value}`,
  });
  g.dataset.tv = value;
  g.dataset.tl = label;
  return g;
}
// show the elements whose data-s <= n
export const reveal = (root, n) => root.querySelectorAll('[data-s]').forEach((e) => e.classList.toggle('on', +e.dataset.s <= n));

// ---------- frame ----------
// number shown in a cell ("67.06", "67,06", "−0.33", "<b>…</b>"); NaN when there is none
export const cellNum = (c) => {
  let x = String(c && typeof c === 'object' ? c.h : c ?? '').replace(/<[^>]*>/g, '').replace(/\s/g, '').replace(/[−–]/g, '-');
  if (x.includes(',')) x = x.replace(/\./g, '').replace(',', '.');
  const m = /^[+-]?\d+(\.\d+)?/.exec(x);
  return m ? parseFloat(m[0]) : NaN;
};
// best value in bold, second best underlined (ties share the mark). t.rank lists the compared
// columns: [{ c: column, lo: lower is better }] ranks down each column; t.rankRows = { cols, lo }
// ranks across those columns within each row; t.skip lists body rows left out (references, totals).
export function rankMarks(t) {
  const marks = t.rows.map(() => []);
  const mark = (cells, lo) => {
    const ok = cells.filter((p) => !Number.isNaN(p.v));
    const vs = [...new Set(ok.map((p) => p.v))].sort((a, b) => (lo ? a - b : b - a));
    for (const p of ok) marks[p.r][p.c] = p.v === vs[0] ? 'best' : p.v === vs[1] ? 'second' : '';
  };
  const live = t.rows.map((_, r) => r).filter((r) => !(t.skip || []).includes(r));
  for (const k of t.rank || []) mark(live.map((r) => ({ r, c: k.c, v: cellNum(t.rows[r][k.c]) })), k.lo);
  if (t.rankRows) for (const r of live) mark(t.rankRows.cols.map((c) => ({ r, c, v: cellNum(t.rows[r][c]) })), t.rankRows.lo);
  return marks;
}
function htmlTable(t) {
  const tb = document.createElement('table');
  tb.className = 't';
  const marks = rankMarks(t);
  const tr = (cells, tag, mk = []) => {
    const r = document.createElement('tr');
    cells.forEach((c, j) => {
      const d = document.createElement(tag);
      if (c && typeof c === 'object') d.innerHTML = c.h; else d.textContent = c == null ? '' : c;
      if (typeof c === 'string' && !/^[+−-]?\d/.test(c)) d.className = 'txt';
      if (mk[j]) d.classList.add(mk[j]);
      r.append(d);
    });
    return r;
  };
  tb.createTHead().append(tr(t.head, 'th'));
  const body = tb.createTBody();
  t.rows.forEach((r, i) => body.append(tr(r, 'td', marks[i])));
  return tb;
}

// el becomes the chart root. sub and controls are trusted HTML written in code; legend items
// are ['classes|inline style' of the swatch, text, reveal step], shown in the top row (or in a
// row of their own with legendRow); table() returns {head, rows} or a list of them.
export function frame(el, { cls, sub, legend, legendRow, controls = '', table, reduced, size }) {
  el.classList.add('ch', cls);
  el.classList.toggle('ch-instant', !!reduced);
  const sw = (x) => { const [k, st] = x.split('|'); return `<i class="sw ${k}" style="${st || ''}"></i>`; };
  const leg = legend ? `<div class="ch-leg">${legend.map(([x, t, st]) => `<span${st == null ? '' : ` class="o" data-s="${st}"`}>${sw(x)}${t}</span>`).join('')}</div>` : '';
  el.innerHTML = `${controls}<div class="ch-top"><p class="ch-sub"></p>${legendRow ? '' : leg}<button type="button" class="btn ch-tb" aria-pressed="false">Tabela</button></div>${legendRow ? leg : ''}
    <div class="ch-main"><svg class="chart" role="group"></svg><div class="ch-tbl" hidden></div></div>
    <div class="tip" hidden><b class="num"></b><span></span></div>`;
  const $ = (q) => el.querySelector(q);
  const main = $('.ch-main'), svg = $('svg'), tb = $('.ch-tb'), tbl = $('.ch-tbl'), tip = $('.tip');
  const W = main.clientWidth || size[0], H = main.clientHeight || size[1];
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);

  const setSub = (html) => { $('.ch-sub').innerHTML = html; svg.setAttribute('aria-label', $('.ch-sub').textContent); };
  setSub(sub);
  function showTable(on) {
    tb.setAttribute('aria-pressed', String(on));
    el.classList.toggle('ch-t', on);
    tbl.hidden = !on;
    tbl.replaceChildren(...(on ? [].concat(table()).map(htmlTable) : []));
  }
  tb.addEventListener('click', () => showTable(tb.getAttribute('aria-pressed') !== 'true'));

  function showTip(g) {
    const m = g.querySelector('.m') || g;
    const r = el.getBoundingClientRect(), k = r.width / el.offsetWidth || 1, b = m.getBoundingClientRect();
    tip.firstChild.textContent = g.dataset.tv;
    tip.lastChild.textContent = g.dataset.tl;
    tip.hidden = false;
    const tw = tip.offsetWidth, th = tip.offsetHeight, ew = el.offsetWidth, eh = el.offsetHeight;
    const L = (b.left - r.left) / k, R = (b.right - r.left) / k, T = (b.top - r.top) / k, B = (b.bottom - r.top) / k;
    // right of the mark; if it does not fit, above it; if that does not fit either, below it
    let x = R + 12, y = (T + B) / 2 - th / 2;
    if (x + tw > ew) { x = R - tw; y = T - th - 8 >= 0 ? T - th - 8 : B + 8; }
    x = Math.max(0, Math.min(x, ew - tw));
    y = Math.max(0, Math.min(y, eh - th));
    tip.style.left = `${x}px`;
    tip.style.top = `${y}px`;
  }
  const hideTip = () => { tip.hidden = true; };
  el.addEventListener('pointerover', (e) => { const g = e.target.closest('[data-tv]'); if (g) showTip(g); else hideTip(); });
  el.addEventListener('pointerleave', hideTip);
  el.addEventListener('focusin', (e) => { const g = e.target.closest('[data-tv]'); if (g) showTip(g); });
  el.addEventListener('focusout', hideTip);

  return {
    svg, W, H, $, setSub, showTable, hideTip,
    // the state every step starts from: chart view, no tooltip, marks revealed up to n
    step(n) { showTable(false); hideTip(); reveal(el, n); },
    destroy() { el.innerHTML = ''; el.classList.remove('ch', cls, 'ch-instant', 'ch-t'); },
  };
}
