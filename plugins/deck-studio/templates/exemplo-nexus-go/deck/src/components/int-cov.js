// INT-COV (S39): share of the test partition each method family can score (Table 6.28).
import { frame, rows, lin, range, s, hbar, axisX, mark, C } from '../lib/chart.js';

const ONT = ['BP', 'CC', 'MF'];
// Table 6.28 says "This work (all routes)", Table B.3 "NEXUS-GO (all routes)"; the deck uses the latter
const rename = (n) => n.replace(/^This work/, 'NEXUS-GO');
const FILL = [C.n1, C.n2, C.seq];
const pct = (v) => `${v.toFixed(1)}%`;

export function mount(el, { data, reduced }) {
  const t = rows(data, 'coverage');
  const order = t.head.slice(1).map((h) => ONT.find((o) => h.endsWith(o)));
  const unit = t.body[0];
  const pc = unit.map((u, i) => (u === '%' ? i : -1)).filter((i) => i > 0);
  const fam = t.body.filter((r) => typeof r[1] === 'number').map((r, k) => ({
    n: rename(r[0]), fill: FILL[k],
    v: Object.fromEntries(order.map((o, i) => [o, { p: r[pc[i]], n: r[pc[i] + 1] }])),
  }));

  const f = frame(el, {
    cls: 'ch-cov', reduced, size: [817, 434], legendRow: true,
    sub: 'Test, proteins with a prediction (%)',
    legend: fam.map((d) => [`|background:${d.fill}`, d.n]),
    table: () => ({ rank: ONT.map((_, i) => ({ c: i + 1 })), head: ['Method family', ...ONT], rows: fam.map((d) => [d.n, ...ONT.map((o) => pct(d.v[o].p))]) }),
  });
  const { svg, W, H } = f;
  const L = 64, R = W - 96, bot = H - 34, bh = 24, pitch = 27, gap = 48;
  const total = 3 * fam.length * pitch + 2 * gap, top = Math.max(10, (bot - total) / 2);
  const x = lin(0, 100, L, R);
  axisX(s(svg, 'g'), x, range(0, 100, 20), 0, bot, String);
  ONT.forEach((o, i) => {
    const y0 = top + i * (fam.length * pitch + gap);
    s(svg, 'text', { class: 'lab b', x: 0, y: y0 + (fam.length * pitch) / 2 + 7 }, o);
    fam.forEach((d, j) => {
      const y = y0 + j * pitch, { p, n } = d.v[o];
      const m = mark(svg, `${pct(p)}, n = ${n.toLocaleString('en-US')}`, `${d.n} · ${o} · test coverage`, 1);
      s(m, 'rect', { class: 'hit', x: 0, y, width: W, height: pitch });
      s(m, 'path', { class: 'm', d: hbar(L, x(p), y + (pitch - bh) / 2, bh), style: `fill:${d.fill}` });
      s(m, 'text', { class: 'val', x: x(p) + 8, y: y + pitch / 2 + 6 }, pct(p));
    });
  });
  s(svg, 'line', { class: 'base', x1: L, x2: L, y1: 0, y2: bot });

  let cur = 0;
  return {
    step(n) { cur = n; f.step(n); },
    render() {}, play() {}, pause() {},
    destroy: f.destroy,
    state: () => ({ step: cur, values: Object.fromEntries(fam.map((d) => [d.n, Object.fromEntries(ONT.map((o) => [o, d.v[o].p]))])) }),
  };
}
