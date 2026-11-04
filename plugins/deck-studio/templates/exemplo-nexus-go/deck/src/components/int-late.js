// INT-LATE (S35): the eleven late-fusion rules (Table 6.14), the per-ontology gain of linear γ
// over the better of its two inputs (Tables 6.15 and 6.9), and the stacking importances (§6.3.4).
import { frame, rows, pick, col, lin, range, s, hbar, axisX, mark, fmt, pp, C } from '../lib/chart.js';

const ONT = ['BP', 'CC', 'MF'];
// importances: three decimals, scientific form below 0.001
function imp(parent, attrs, v) {
  const t = s(parent, 'text', attrs);
  if (v >= 0.001) { t.textContent = v.toFixed(3); return t; }
  const e = Math.floor(Math.log10(v));
  t.textContent = `${(v / 10 ** e).toFixed(1)} × 10`;
  s(t, 'tspan', { dy: -8, style: 'font-size:13px' }, fmt(e, 0));
  return t;
}
const impHtml = (v) => (v >= 0.001 ? v.toFixed(3) : { h: `${(v / 10 ** Math.floor(Math.log10(v))).toFixed(1)} × 10<sup>${fmt(Math.floor(Math.log10(v)), 0)}</sup>` });

export function mount(el, { data, reduced }) {
  const late = rows(data, 'late'), vv = rows(data, 'vector_vs_vision'), gnn = rows(data, 'gnn'), im = rows(data, 'importances');
  const ia = col(late, 'AVG');
  const rules = late.body.map((r) => ({ n: r[0], v: r[ia] }));
  const win = rules.reduce((a, b) => (b.v > a.v ? b : a));
  const lr = pick(late.body, 'Linear interpolation (γ)');
  const fixed = pick(vv.body, 'Fixed propagation', 'Vector'), gcn = pick(gnn.body, 'GCN (2 layers)', 'Vector');
  const gains = ONT.map((o) => {
    const a = fixed[col(vv, o)], b = gcn[col(gnn, o)], best = a >= b ? ['Fixed', a] : ['GCN', b];
    return { o, linear: lr[col(late, o)], better: best[0], base: best[1], gain: lr[col(late, o)] - best[1] };
  });

  const f = frame(el, {
    cls: 'ch-late', reduced, size: [817, 550],
    sub: 'Validation, mean wF<sub>max</sub> over BP, CC, MF, late fusion of Fixed and GCN',
    table: () => [
      { rank: [1, 2, 3, 4].map((c) => ({ c })), skip: [late.body.length], head: ['Rule', ...ONT, 'Mean'], rows: [...late.body.map((r) => [r[0], ...ONT.map((o) => fmt(r[col(late, o)])), fmt(r[ia])]), ['Linear γ minus better input', ...gains.map((g) => pp(g.gain)), '']] },
      { head: im.head, rows: im.body.map((r) => [r[0], ...r.slice(1).map(impHtml)]) },
    ],
  });
  const { svg, W, H } = f;

  // the eleven rules on a non-zero axis
  const L = 300, R = W - 70, pitch = 27, top = 6, bot = top + rules.length * pitch;
  const lo = Math.floor(Math.min(...rules.map((r) => r.v)) * 2) / 2, hi = Math.ceil(win.v * 2) / 2;
  const x = lin(lo, hi, L, R);
  axisX(s(svg, 'g'), x, range(lo, hi, 0.5), top, bot, (t) => t.toFixed(1));
  s(svg, 'line', { class: 'base', x1: L, x2: R, y1: bot, y2: bot });
  s(svg, 'path', { d: `M${L + 8},${bot + 7}l6,-14M${L + 15},${bot + 7}l6,-14`, style: 'stroke:var(--ink-2);stroke-width:1.5;fill:none' });
  s(svg, 'path', { d: `M${L + 10},${bot - 1}h9`, style: 'stroke:var(--slide);stroke-width:4' });
  const gr = s(svg, 'g', { class: 'o', 'data-s': 2 });
  rules.forEach((r, i) => {
    const y = top + i * pitch, cy = y + pitch / 2, hl = r === win;
    const m = mark(gr, fmt(r.v), `${r.n} · validation, mean wFmax`);
    s(m, 'rect', { class: 'hit', x: 0, y, width: W, height: pitch });
    s(m, 'text', { class: `lab sm${hl ? ' b' : ''}`, x: 0, y: cy + 6 }, r.n);
    s(m, 'circle', { class: 'm ring', cx: x(r.v), cy, r: hl ? 9 : 7, style: `fill:${hl ? C.fuse : C.tint(C.fuse, 60)}` });
    s(m, 'text', { class: `val${hl ? ' b' : ''}`, x: x(r.v) + 14, y: cy + 6 }, fmt(r.v));
  });

  // per-ontology gain of the winner over the better input
  const yg = bot + 44, gg = s(svg, 'g', { class: 'o', 'data-s': 3 });
  s(gg, 'text', { class: 'cap', x: 0, y: yg + 20 }, 'Linear γ over the better input');
  gains.forEach((g, i) => {
    const x0 = L + i * ((W - L) / 3);
    const m = mark(gg, pp(g.gain), `${g.o} · linear γ ${fmt(g.linear)} minus ${g.better} ${fmt(g.base)}`);
    s(m, 'rect', { class: 'hit', x: x0 - 8, y: yg, width: (W - L) / 3, height: 30 });
    s(m, 'text', { class: 'sml', x: x0, y: yg + 21 }, g.o);
    s(m, 'text', { class: 'val b m', x: x0 + 34, y: yg + 21 }, pp(g.gain));
  });

  // stacking importances: decision tree and random forest
  const yi = yg + 48, gi = s(svg, 'g', { class: 'o', 'data-s': 4 }), pw = (W - 40) / 2;
  s(gi, 'line', { class: 'grid', x1: 0, x2: W, y1: yi - 8, y2: yi - 8 });
  const fill = [C.net, C.tint(C.net, 60), C.n1, C.n1];
  im.body.forEach((r, k) => {
    const x0 = k * (pw + 40), xb = lin(0, 1, x0 + 124, x0 + 124 + 150);
    s(gi, 'text', { class: 'lab sm b', x: x0, y: yi + 18 }, `Stacking (${r[0].toLowerCase()}): importance`);
    r.slice(1).forEach((v, j) => {
      const y = yi + 28 + j * 24, m = mark(gi, v >= 0.001 ? v.toFixed(3) : v.toExponential(1), `${r[0]} · ${im.head[j + 1]}`);
      s(m, 'rect', { class: 'hit', x: x0, y, width: pw, height: 24 });
      s(m, 'text', { class: 'sml', x: x0, y: y + 18 }, im.head[j + 1]);
      s(m, 'path', { class: 'm', d: hbar(xb(0), xb(v), y + 5, 14), style: `fill:${fill[j]}` });
      imp(m, { class: 'val', x: xb(v) + 8, y: y + 18 }, v);
    });
  });

  let cur = 0;
  return {
    step(n) { cur = n; f.step(n); },
    render() {}, play() {}, pause() {},
    destroy: f.destroy,
    state: () => ({
      step: cur, rules: Object.fromEntries(rules.map((r) => [r.n, r.v])), winner: win.n,
      gains: Object.fromEntries(gains.map((g) => [g.o, +g.gain.toFixed(2)])),
      importances: Object.fromEntries(im.body.map((r) => [r[0], Object.fromEntries(im.head.slice(1).map((h, j) => [h, r[j + 1]]))])),
    }),
  };
}
