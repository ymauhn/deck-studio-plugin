// INT-VV (S36): vector vs vision head, four stages × three ontologies (Table 6.15), with the
// stage margin on the mean.
import { frame, rows, col, lin, range, s, axisX, mark, fmt as fmtE, pp as ppE, C } from '../lib/chart.js';

// PT: decimal comma and p.p. on displayed numbers (idempotent if chart.js already does it)
const dc = (t) => String(t).replace(/(\d)\.(\d)/g, '$1,$2').replace(/ pp$/, ' p.p.');
const fmt = (...a) => dc(fmtE(...a)), pp = (...a) => dc(ppE(...a));
// PT: display names (data keys and state() stay in English)
const NAME = { 'First Generation': 'Primeira Geração', 'Fixed propagation': 'Propagação fixa', 'End-to-end GNN': 'GNN ponta a ponta', 'Early fusion': 'Fusão precoce', Vector: 'Vetorial', Vision: 'Visual' };
const tr = (n) => NAME[n] ?? n;

const ONT = ['BP', 'CC', 'MF'];

export function mount(el, { data, reduced }) {
  const t = rows(data, 'vector_vs_vision');
  const stages = [...new Set(t.body.map((r) => r[0]))].map((name) => {
    const row = (h) => t.body.find((r) => r[0] === name && r[1] === h);
    const [vec, vis] = [row('Vector'), row('Vision')];
    return {
      name, vec, vis, color: /fusion/i.test(name) ? C.fuse : C.net,
      o: ONT.map((o) => ({ o, vec: vec[col(t, o)], vis: vis[col(t, o)] })),
      margin: vec[col(t, 'AVG')] - vis[col(t, 'AVG')],
    };
  });

  const f = frame(el, {
    cls: 'ch-vv', reduced, size: [938, 514], legendRow: true,
    sub: 'Validação, wF<sub>max</sub>, melhor configuração de cada cabeça',
    legend: [['dot|background:var(--ink-2)', 'cabeça vetorial'], ['ring|border-color:var(--ink-2)', 'cabeça visual'], [`|background:${C.net}`, 'rota de rede'], [`|background:${C.fuse}`, 'rota de fusão']],
    table: () => ({
      rank: [2, 3, 4, 5].map((c) => ({ c })),
      head: ['Etapa', 'Cabeça', ...ONT, 'Média', 'Margem'],
      rows: stages.flatMap((g) => [g.vec, g.vis].map((r, i) => [i ? '' : tr(g.name), tr(r[1]), ...ONT.map((o) => fmt(r[col(t, o)])), fmt(r[col(t, 'AVG')]), i ? '' : pp(g.margin)])),
    }),
  });
  const { svg, W, H } = f;
  const L = 250, R = W - 150, top = 26, gap = 14, bot = H - 34;
  const pitch = (bot - top - 3 * gap) / 12;
  const x = lin(30, 80, L, R);
  axisX(s(svg, 'g'), x, range(30, 80, 10), top - 6, bot, String);
  s(svg, 'text', { class: 'cap o', 'data-s': 2, x: W - 62, y: 14, 'text-anchor': 'middle' }, 'margem média');
  stages.forEach((g, i) => {
    const y0 = top + i * (3 * pitch + gap);
    s(svg, 'text', { class: 'lab', x: 0, y: y0 + 1.5 * pitch + 7 }, tr(g.name));
    s(svg, 'text', { class: 'val b o', 'data-s': 2, x: W - 62, y: y0 + 1.5 * pitch + 7, 'text-anchor': 'middle' }, pp(g.margin));
    g.o.forEach((d, j) => {
      const y = y0 + j * pitch, cy = y + pitch / 2;
      s(svg, 'text', { class: 'sml', x: 200, y: cy + 6 }, d.o);
      const m = mark(svg, `${fmt(d.vec)} contra ${fmt(d.vis)}`, `${tr(g.name)} · ${d.o} · vetorial contra visual`, 1);
      s(m, 'rect', { class: 'hit', x: 190, y, width: R - 190 + 30, height: pitch });
      s(m, 'line', { x1: x(d.vis), x2: x(d.vec), y1: cy, y2: cy, style: `stroke:${C.tint(g.color, 55)};stroke-width:2` });
      s(m, 'circle', { cx: x(d.vis), cy, r: 7, style: `fill:var(--slide);stroke:${g.color};stroke-width:2.5` });
      s(m, 'circle', { class: 'm ring', cx: x(d.vec), cy, r: 8, style: `fill:${g.color}` });
    });
  });

  let cur = 0;
  return {
    step(n) { cur = n; f.step(n); },
    render() {}, play() {}, pause() {},
    destroy: f.destroy,
    state: () => ({
      step: cur,
      rows: stages.flatMap((g) => g.o.map((d) => ({ stage: g.name, ontology: d.o, vector: d.vec, vision: d.vis }))),
      margins: Object.fromEntries(stages.map((g) => [g.name, +g.margin.toFixed(2)])),
    }),
  };
}
