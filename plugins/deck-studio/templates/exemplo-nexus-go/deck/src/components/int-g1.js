// INT-G1 (S31): what Generation 1 settles. Mean validation wFmax, Tables 6.1–6.4.
import { frame, rows, pick, col, lin, range, s, hbar, axisX, mark, fmt, C } from '../lib/chart.js';

export function mount(el, { data, reduced }) {
  const T = Object.fromEntries(['naive', 'loss', 'gen1_arch', 'gen1_backbone'].map((k) => [k, rows(data, k)]));
  const avg = (k, ...key) => pick(T[k].body, ...key)[col(T[k], 'AVG')];
  const ia = col(T.gen1_arch, 'AVG');
  const cnn = T.gen1_arch.body.filter((r) => r[0] === 'CNN1D').reduce((a, b) => (b[ia] > a[ia] ? b : a));
  const naive = T.naive.body[0][col(T.naive, 'AVG')];
  const groups = [
    { s: 1, name: '', items: [['Naive', naive, C.n1]] },
    { s: 2, name: 'Loss, MLP with max pooling', items: [['BCE', avg('loss', 'Binary cross-entropy')], ['ProteinLoss', avg('loss', 'ProteinLoss')]] },
    { s: 3, name: 'Architecture and pooling', items: [['MLP avg', avg('gen1_arch', 'MLP', 'avg')], ['MLP raw', avg('gen1_arch', 'MLP', 'raw')], [`CNN1D ${cnn[1]}`, cnn[ia]]] },
    { s: 4, name: 'Vision backbone', items: [['ResNet-50 avg', avg('gen1_backbone', 'ResNet-50', 'avg')], ['ConvNeXt-Tiny avg', avg('gen1_backbone', 'ConvNeXt-Tiny', 'avg')]] },
  ];
  const all = groups.flatMap((g) => g.items.map(([n, v]) => ({ g: g.name || 'Baseline', n, v, s: g.s })));

  const f = frame(el, {
    cls: 'ch-g1', reduced, size: [817, 550],
    sub: 'Validation, mean wF<sub>max</sub> over BP, CC, MF',
    table: () => ({ rank: [{ c: 2 }], skip: [0], head: ['Group', 'Model', { h: 'Mean wF<sub>max</sub>' }], rows: all.map((r) => [r.g, r.n, fmt(r.v)]) }),
  });
  const { svg, W, H } = f;
  const L = 240, R = W - 76, top = 34, bot = H - 34, bh = 24, head = 28, gap = 10;
  const x = lin(0, 50, L, R);
  const pitch = Math.min(50, (bot - top - 3 * (head + gap)) / all.length);
  axisX(s(svg, 'g'), x, range(0, 50, 10), top - 10, bot, String);
  // reference lines under the marks, so value labels stay on top
  s(svg, 'line', { class: 'base', x1: L, x2: L, y1: top - 10, y2: bot });
  const ref = s(svg, 'g', { class: 'o', 'data-s': 1 });
  s(ref, 'line', { class: 'ref', x1: x(naive), x2: x(naive), y1: top - 10, y2: bot });
  s(ref, 'text', { class: 'cap', x: x(naive), y: top - 16, 'text-anchor': 'middle' }, 'naive');
  const gm = s(svg, 'g');
  let y = top;
  for (const g of groups) {
    if (g.name) { y += gap; s(gm, 'text', { class: 'cap o', 'data-s': g.s, x: 0, y: y + 19 }, g.name); y += head; }
    for (const [n, v, c = C.net] of g.items) {
      const m = mark(gm, fmt(v), `${n} · validation, mean wFmax`, g.s);
      s(m, 'rect', { class: 'hit', x: 0, y, width: W, height: pitch });
      s(m, 'text', { class: 'lab', x: 0, y: y + pitch / 2 + 7 }, n);
      s(m, 'path', { class: 'm', d: hbar(L, x(v), y + (pitch - bh) / 2, bh), style: `fill:${c}` });
      s(m, 'text', { class: 'val', x: x(v) + 8, y: y + pitch / 2 + 6 }, fmt(v));
      y += pitch;
    }
  }

  let cur = 0;
  return {
    step(n) { cur = n; f.step(n); },
    render() {}, play() {}, pause() {},
    destroy: f.destroy,
    state: () => ({ step: cur, naive, bars: Object.fromEntries(all.map((r) => [r.n, r.v])), visible: all.filter((r) => r.s <= cur).map((r) => r.n) }),
  };
}
