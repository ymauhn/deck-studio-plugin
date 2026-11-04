// INT-JOURNEY (S37): the validation journey, a staircase of six means (Tables 6.1, 6.3, 6.5,
// 6.15, 6.14). Each riser takes the colour of what it adds: sequence, graph or fusion.
import { frame, rows, pick, col, lin, range, s, mark, fmt, C } from '../lib/chart.js';

export function mount(el, { data, reduced }) {
  const T = (k) => rows(data, k);
  const avg = (k, ...key) => { const t = T(k); return pick(t.body, ...key)[col(t, 'AVG')]; };
  const st = [
    { n: 'Naive', v: avg('naive', 'Naive (term frequency)'), c: C.ink2, s: 1 },
    { n: 'First Generation', v: avg('gen1_arch', 'MLP', 'raw'), c: C.ink2, s: 1 },
    { n: 'ProtT5 only', v: avg('hops_vector', 0), c: C.seq, s: 2 },
    { n: 'NEXUS-GO/Fixed', v: avg('vector_vs_vision', 'Fixed propagation', 'Vector'), c: C.net, s: 3 },
    { n: 'NEXUS-GO/Early', v: avg('vector_vs_vision', 'Early fusion', 'Vector'), c: C.fuse, s: 3 },
    { n: 'NEXUS-GO/Late', v: avg('late', 'Linear interpolation (γ)'), c: C.fuse, s: 3 },
  ];

  const f = frame(el, {
    cls: 'ch-journey', reduced, size: [1424, 380],
    sub: 'Validation, mean wF<sub>max</sub> over BP, CC, MF',
    legend: [[`|background:${C.seq}`, 'gain from ProtT5', 2], [`|background:${C.net}`, 'gain from the graph', 3], [`|background:${C.fuse}`, 'gain from fusion', 3]],
    table: () => ({ rank: [{ c: 1 }], head: ['Stage', { h: 'Mean wF<sub>max</sub>' }], rows: st.map((d) => [d.n, fmt(d.v)]) }),
  });
  const { svg, W, H } = f;
  const L = 64, R = W - 8, top = 40, bot = H - 46, bw = (R - L) / st.length;
  const y = lin(40, 70, bot, top);
  const ax = s(svg, 'g');
  for (const t of range(40, 70, 10)) {
    s(ax, 'line', { class: 'grid', x1: L, x2: R, y1: y(t), y2: y(t) });
    s(ax, 'text', { class: 'tick', x: L - 12, y: y(t) + 6, 'text-anchor': 'end' }, String(t));
  }
  st.forEach((d, i) => {
    const x0 = L + i * bw, cx = x0 + bw / 2, yv = y(d.v), yp = i ? y(st[i - 1].v) : yv;
    const m = mark(svg, fmt(d.v), `${d.n} · validation, mean wFmax`, d.s);
    s(m, 'rect', { class: 'hit', x: x0, y: top - 34, width: bw, height: H - top + 34 });
    if (i) {
      s(m, 'rect', { x: x0, y: yv, width: bw, height: yp - yv, style: `fill:${d.c};fill-opacity:.16` });
      s(m, 'line', { x1: x0, x2: x0, y1: yp, y2: yv, style: `stroke:${d.c};stroke-width:2` });
    }
    s(m, 'line', { x1: x0, x2: x0 + bw, y1: yv, y2: yv, style: `stroke:${d.c};stroke-width:2` });
    s(m, 'circle', { class: 'm ring', cx, cy: yv, r: 6, style: `fill:${d.c}` });
    s(m, 'text', { class: 'val b', x: cx, y: yv - 14, 'text-anchor': 'middle', style: 'font-size:22px' }, fmt(d.v));
    s(m, 'text', { class: 'lab', x: cx, y: bot + 32, 'text-anchor': 'middle' }, d.n);
  });
  s(svg, 'line', { class: 'base', x1: L, x2: R, y1: bot, y2: bot });

  let cur = 0;
  return {
    step(n) { cur = n; f.step(n); },
    render() {}, play() {}, pause() {},
    destroy: f.destroy,
    state: () => ({ step: cur, stages: st.map((d) => ({ name: d.n, value: d.v, visible: d.s <= cur })) }),
  };
}
