// INT-GAIN (S41): gain of the best graph route over the T = 0 control by degree band
// (Table 6.27), as a heat strip. Cells read "+3.24 [h]": gain in pp and the winning route.
import { frame, rows, s, mark, sg, pp, C } from '../lib/chart.js';

const ONT = ['BP', 'CC', 'MF'];
const ROUTE = { f: 'fixed', g: 'GNN', h: 'early fusion' };

export function mount(el, { data, reduced }) {
  const t = rows(data, 'graph_gain_by_degree');
  const bands = t.body.map((r) => r[0]);
  const cells = Object.fromEntries(ONT.map((o) => [o, t.body.map((r) => {
    const m = /^([+\-−]?\d+(?:\.\d+)?)\s*\[(\w)\]$/.exec(r[t.head.indexOf(o)]);
    if (!m) throw new Error(`INT-GAIN: cannot parse ${r[t.head.indexOf(o)]}`);
    return { band: r[0], gain: +m[1].replace('−', '-'), route: m[2].toLowerCase() };
  })]));
  const max = Math.max(...ONT.flatMap((o) => cells[o].map((c) => c.gain)));

  const f = frame(el, {
    cls: 'ch-gain', reduced, size: [938, 132],
    sub: 'Test, gain of the best graph route over the T = 0 control, mean per-protein F<sub>1</sub>, pp',
    table: () => ({ head: ['Ontology', ...bands], rows: ONT.map((o) => [o, ...cells[o].map((c) => `${sg(c.gain)} (${c.route})`)]) }),
  });
  const { svg, W } = f;
  const L = 56, cw = (W - L) / bands.length, hh = 22, rh = 28;
  s(svg, 'text', { class: 'cap', x: 0, y: 16 }, 'degree');
  bands.forEach((b, j) => s(svg, 'text', { class: 'cap', x: L + (j + 0.5) * cw, y: 16, 'text-anchor': 'middle' }, b));
  ONT.forEach((o, i) => {
    const y = hh + i * rh;
    s(svg, 'text', { class: 'lab b', x: 0, y: y + rh / 2 + 7 }, o);
    cells[o].forEach((c, j) => {
      const m = mark(svg, pp(c.gain), `${o} · degree ${c.band} · best route: ${ROUTE[c.route] || c.route}`);
      const fill = c.gain > 0 ? C.tint(C.net, Math.round(14 + (66 * c.gain) / max)) : 'var(--hair)';
      s(m, 'rect', { class: 'm', x: L + j * cw + 1, y: y + 1, width: cw - 2, height: rh - 2, rx: 2, style: `fill:${fill}` });
      const lab = s(m, 'text', { class: 'val', x: L + (j + 0.5) * cw, y: y + rh / 2 + 6, 'text-anchor': 'middle' }, sg(c.gain));
      s(lab, 'tspan', { class: 'cap', dx: 8 }, c.route);
    });
  });
  s(svg, 'text', { class: 'cap', x: 0, y: hh + 3 * rh + 22 }, Object.entries(ROUTE).map(([k, v]) => `${k} ${v}`).join(' · '));

  let cur = 0;
  el.classList.add('ch-hide');
  return {
    step(n) { cur = n; f.step(n); el.classList.toggle('ch-hide', n < 3); },
    render() {}, play() {}, pause() {},
    destroy: f.destroy,
    state: () => ({ step: cur, visible: cur >= 3, cells }),
  };
}
