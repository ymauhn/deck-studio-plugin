// INT-FL (S34): fixed vs learned aggregation, vector head (Tables 6.15 and 6.9), with the
// deduplication strip (Table 6.11).
import { frame, rows, pick, col, lin, range, s, hbar, axisX, mark, fmt, sg, pp, C } from '../lib/chart.js';

// Noise reference of §6.3.3 (vision head, MF at T = 0; FACTS §5). Stated in the text, not in a table.
const NOISE = 0.64;
const ONT = ['BP', 'CC', 'MF'];

export function mount(el, { data, reduced }) {
  const vv = rows(data, 'vector_vs_vision'), gnn = rows(data, 'gnn'), dd = rows(data, 'dedup');
  const get = (t, ...k) => { const r = pick(t.body, ...k); return Object.fromEntries(ONT.map((o) => [o, r[col(t, o)]])); };
  const routes = [
    { id: 'Fixed', s: 2, v: get(vv, 'Fixed propagation', 'Vector'), fill: C.net },
    { id: 'GCN', s: 1, v: get(gnn, 'GCN (2 layers)', 'Vector'), fill: C.tint(C.net, 60) },
    { id: 'GAT', s: 1, v: get(gnn, 'GAT (2 layers, 4 heads)', 'Vector'), fill: 'var(--slide)', hollow: true },
  ];
  const margin = Object.fromEntries(ONT.map((o) => [o, routes[0].v[o] - routes[1].v[o]]));
  const delta = dd.body.filter((r) => typeof r.at(-1) === 'number')
    .map((r) => ({ n: r[0].replace('Fixed propagation', 'Fixed').replace('End-to-end ', '').replace(' head', ''), d: r.at(-1) }));

  const f = frame(el, {
    cls: 'ch-fl', reduced, size: [817, 550],
    sub: 'Validation, wF<sub>max</sub>, vector head',
    legend: [[`dot|background:${C.net}`, 'Fixed', 2], [`dot|background:${routes[1].fill}`, 'GCN', 1], [`ring|border-color:${C.net}`, 'GAT', 1]],
    table: () => [
      { rankRows: { cols: [1, 2, 3] }, head: ['Ontology', 'Fixed', 'GCN', 'GAT', 'Fixed − GCN'], rows: ONT.map((o) => [o, ...routes.map((r) => fmt(r.v[o])), pp(margin[o])]) },
      { head: ['Deduplication', 'Δ max − sum, mean'], rows: delta.map((r) => [r.n, pp(r.d)]) },
    ],
  });
  const { svg, W, H } = f;

  // main dot plot: ontology groups, one sub-row per route
  const L = 132, R = W - 150, top = 26, insetH = 192, bot = H - insetH - 44, gap = 14;
  const pitch = (bot - top - 2 * gap) / 9;
  const x = lin(40, 80, L, R);
  axisX(s(svg, 'g'), x, range(40, 80, 10), top - 6, bot, String);
  s(svg, 'text', { class: 'cap o', 'data-s': 3, x: W - 62, y: 14, 'text-anchor': 'middle' }, 'Fixed − GCN');
  const gm = s(svg, 'g');
  ONT.forEach((o, i) => {
    const y0 = top + i * (3 * pitch + gap);
    s(gm, 'text', { class: 'lab b', x: 0, y: y0 + 1.5 * pitch + 7 }, o);
    routes.forEach((r, j) => {
      const y = y0 + j * pitch, cy = y + pitch / 2, v = r.v[o];
      const m = mark(gm, fmt(v), `${r.id} · ${o} · validation wFmax`, r.s);
      s(m, 'rect', { class: 'hit', x: 50, y, width: R - 50 + 70, height: pitch });
      s(m, 'text', { class: 'sml', x: 52, y: cy + 6 }, r.id);
      s(m, 'circle', r.hollow
        ? { class: 'm', cx: x(v), cy, r: 7, style: `fill:var(--slide);stroke:${C.net};stroke-width:2.5` }
        : { class: 'm ring', cx: x(v), cy, r: 8, style: `fill:${r.fill}` });
      s(m, 'text', { class: 'val', x: x(v) + 14, y: cy + 6 }, fmt(v));
    });
    s(gm, 'text', { class: 'val b o', 'data-s': 3, x: W - 62, y: y0 + pitch + 6, 'text-anchor': 'middle' }, pp(margin[o]));
  });

  // inset: deduplication delta per route, with the noise band
  const g = s(svg, 'g', { class: 'o', 'data-s': 4 });
  const y1 = H - insetH, L2 = 190, R2 = W - 80, ip = 22, iy = y1 + 30, ib = iy + 6 * ip;
  const xd = lin(-1, 4, L2, R2);
  s(g, 'line', { class: 'grid', x1: 0, x2: W, y1: y1 - 8, y2: y1 - 8 });
  s(g, 'text', { class: 'cap', x: 0, y: y1 + 14 }, 'Deduplication: Δ = max − sum on the mean, pp');
  s(g, 'rect', { x: W - 14, y: y1 + 2, width: 14, height: 14, rx: 3, style: 'fill:var(--hair)' });
  s(g, 'text', { class: 'cap', x: W - 22, y: y1 + 14, 'text-anchor': 'end' }, `noise reference ±${fmt(NOISE)}`);
  s(g, 'rect', { x: xd(-NOISE), y: iy, width: xd(NOISE) - xd(-NOISE), height: ib - iy, style: 'fill:var(--hair)' });
  axisX(g, xd, range(-1, 4, 1), iy, ib, (t) => fmt(t, 0));
  s(g, 'line', { class: 'base', x1: xd(0), x2: xd(0), y1: iy, y2: ib });
  delta.forEach((r, i) => {
    const y = iy + i * ip, m = mark(g, pp(r.d), `${r.n} · deduplication Δ`);
    s(m, 'rect', { class: 'hit', x: 0, y, width: W, height: ip });
    s(m, 'text', { class: 'sml', x: 0, y: y + 17 }, r.n);
    s(m, 'path', { class: 'm', d: hbar(xd(0), xd(r.d), y + 4, 14), style: `fill:${C.net}` });
    s(m, 'text', { class: 'val', x: xd(r.d) + (r.d < 0 ? -6 : 6), y: y + 17, 'text-anchor': r.d < 0 ? 'end' : 'start' }, sg(r.d));
  });

  let cur = 0;
  return {
    step(n) { cur = n; f.step(n); },
    render() {}, play() {}, pause() {},
    destroy: f.destroy,
    state: () => ({
      step: cur, values: Object.fromEntries(routes.map((r) => [r.id, r.v])), margins: margin,
      dedup: Object.fromEntries(delta.map((r) => [r.n, r.d])), noise: NOISE,
    }),
  };
}
