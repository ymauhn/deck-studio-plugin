// Components' base: the build joins deck/src/components/*.js in name order (this one first) before the engine.
// Each component registers COMPONENTS.NAME = (el, opts) => ({ step(n), pause() }); a slide carries only
// data-component="NAME" and data-opts='{...}' with the numbers of docs/FACTS.md. No script ever runs inside a slide.
const COMPONENTS = {};
const K = (() => {
  const NS = 'http://www.w3.org/2000/svg';
  const svg = (parent, tag, attrs = {}, text) => {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) if (v != null) e.setAttribute(k, v);
    if (text != null) e.textContent = text;
    parent?.append(e);
    return e;
  };
  const html = (parent, tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    parent?.append(e);
    return e;
  };
  const lang = () => document.documentElement.lang || 'pt-BR';
  // the number in the deck's language (decimal comma in Portuguese), with the source's decimals
  const fmt = (v, casas = 0) => new Intl.NumberFormat(lang(), { minimumFractionDigits: casas, maximumFractionDigits: casas }).format(v);
  const signed = (v, casas = 0) => `${v > 0 ? '+' : v < 0 ? '−' : ''}${fmt(Math.abs(v), casas)}`;
  const color = (c) => (/^c[123]$/.test(c || '') ? `var(--${c})` : c || 'var(--ink-2)');
  const still = (o) => o.reduced || document.documentElement.classList.contains('printing');
  // count from a to b in ms; no animation in the PDF nor with reduced motion
  function count(o, a, b, ms, draw) {
    if (still(o) || a === b) { draw(b); return () => {}; }
    let raf = 0;
    const t0 = performance.now();
    const tick = (t) => {
      const k = Math.min(1, (t - t0) / ms), e = 1 - (1 - k) ** 3;
      draw(a + (b - a) * e);
      if (k < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }
  // round axis ticks between min and max, about n
  function ticks(min, max, n = 5) {
    const raw = (max - min) / n, p = 10 ** Math.floor(Math.log10(raw)), m = raw / p;
    const st = (m >= 5 ? 10 : m >= 2 ? 5 : m >= 1 ? 2 : 1) * p;
    const out = [];
    for (let t = Math.floor(min / st + 1e-9) * st; t < max + st - st * 1e-9; t += st) out.push(+t.toFixed(10));
    if (out[out.length - 1] < max) out.push(+(out[out.length - 1] + st).toFixed(10));
    return out;
  }
  const lin = (d0, d1, r0, r1) => (v) => r0 + ((v - d0) * (r1 - r0)) / ((d1 - d0) || 1);
  // the tooltip: any element with data-tl (label) and data-tv (value) inside el, by mouse or keyboard
  function tips(el) {
    const tip = html(el, 'div', 'tip');
    tip.hidden = true;
    const show = (e) => {
      const m = e.target.closest?.('[data-tl]');
      if (!m || !el.contains(m)) return;
      tip.textContent = m.dataset.tv ? `${m.dataset.tl}: ${m.dataset.tv}` : m.dataset.tl;
      const r = m.getBoundingClientRect(), base = el.getBoundingClientRect(), s = base.width / el.offsetWidth || 1;
      tip.style.left = `${(r.left + r.width / 2 - base.left) / s}px`;
      tip.style.top = `${(r.top - base.top) / s - 46}px`;
      tip.hidden = false;
    };
    const hide = () => { tip.hidden = true; };
    el.addEventListener('pointerover', show);
    el.addEventListener('focusin', show);
    el.addEventListener('pointerleave', hide);
    el.addEventListener('focusout', hide);
  }
  // the Table button: swaps the chart for the same numbers in a table (to read the values, and for screen readers)
  function table(el, view, head, rows) {
    const bar = html(null, 'div', 'controls cp-controls');
    const btn = html(bar, 'button', 'btn', '{{UI_TABLE}}');
    btn.type = 'button';
    btn.setAttribute('aria-pressed', 'false');
    const t = html(null, 'table', 't cp-table');
    t.hidden = true;
    const tr = html(html(t, 'thead'), 'tr');
    for (const h of head) html(tr, 'th', null, h);
    const tb = html(t, 'tbody');
    for (const r of rows) { const row = html(tb, 'tr'); for (const c of r) html(row, 'td', null, c); }
    btn.addEventListener('click', () => {
      const on = btn.getAttribute('aria-pressed') !== 'true';
      btn.setAttribute('aria-pressed', String(on));
      t.hidden = !on;
      view.hidden = on;
    });
    el.prepend(bar);
    el.append(t);
  }
  const dec = (t) => (String(t).split(".")[1] || "").length; // a tick shows only the decimals it has
  return { svg, html, fmt, signed, color, still, count, ticks, lin, tips, table, dec };
})();
