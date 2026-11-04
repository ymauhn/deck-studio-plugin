// INT-TEST (S38): NEXUS-GO against the literature on the test set (Tables 6.17–6.19).
// Ontology tabs × metric select; the naive baseline is a dashed reference, not a ranked bar.
import { frame, rows, lin, range, s, hbar, axisX, mark, fmt as fmtE, pp as ppE, C } from '../lib/chart.js';

// PT: decimal comma and p.p. on displayed numbers (idempotent if chart.js already does it)
const dc = (t) => String(t).replace(/(\d)\.(\d)/g, '$1,$2').replace(/ pp$/, ' p.p.');
const fmt = (...a) => dc(fmtE(...a)), pp = (...a) => dc(ppE(...a));
// PT: display names (data keys and state() stay in English)
const NAME = { 'Naive baseline': 'Baseline ingênuo', 'First Generation': 'Primeira Geração', 'ProtT5 baseline': 'Baseline ProtT5' };
const tr = (n) => NAME[n] ?? n;
const GROUP = { 'NEXUS-GO routes': 'Rotas NEXUS-GO', Controls: 'Controles', Literature: 'Literatura' };

const ONT = ['BP', 'CC', 'MF'];
const NAIVE = /^Naive/;
const group = (n) => (n.startsWith('NEXUS-GO') ? 'NEXUS-GO routes' : /^(First Generation|ProtT5 baseline)$/.test(n) ? 'Controls' : 'Literature');
const color = (n) => ({ 'ProtT5 baseline': C.seq, 'First Generation': C.net, 'NEXUS-GO/Fixed': C.net, 'NEXUS-GO/GNN': C.net, 'NEXUS-GO/Early': C.fuse, 'NEXUS-GO/Late': C.fuse }[n] || C.n1);
const subHtml = (m) => m.replace(/(max|min)$/, '<sub>$1</sub>');
// per step: [ontology, metric, emphasised methods, guide at the value of a (rows a to b), b, margin b − a]
const STEPS = [
  ['BP', 'wFmax'], ['BP', 'wFmax'],
  ['BP', 'wFmax', ['NEXUS-GO/Late', 'DeepGraphGO'], 'DeepGraphGO', 'NEXUS-GO/Late', true],
  ['BP', 'Smin', ['NEXUS-GO/Late', 'DeepGraphGO']],
  ['BP', 'wFmax', ['ProtT5 baseline', 'DeepGraphGO', 'SEGT-GO', 'Mashup', 'MELISSA', 'deepNF'], 'ProtT5 baseline', 'DeepGraphGO'],
];

export function mount(el, { data, reduced }) {
  const T = Object.fromEntries(ONT.map((o) => [o, rows(data, `test_${o}`)]));
  const metrics = T.BP.head.slice(1);
  let ont = 'BP', met = 'wFmax', emph = null, cur = 0;
  const vals = () => Object.fromEntries(T[ont].body.map((r) => [r[0], r[T[ont].head.indexOf(met)]]));
  // best value of a metric among the ranked methods (the naive reference excluded): Smin is lower-better
  const best = (m) => {
    const i = T[ont].head.indexOf(m), xs = T[ont].body.filter((r) => !NAIVE.test(r[0])).map((r) => r[i]);
    return m === 'Smin' ? Math.min(...xs) : Math.max(...xs);
  };

  const controls = `<div class="controls">
    <span class="lbl" id="test-ont-l">ontologia</span>
    <span class="seg" role="group" aria-labelledby="test-ont-l">${ONT.map((o) => `<button class="btn" type="button" id="test-${o}" data-o="${o}">${o}</button>`).join('')}</span>
    <label class="lbl" for="test-metric">métrica</label>
    <select class="btn" id="test-metric">${metrics.map((m) => `<option value="${m}">${m === 'Smin' ? 'Smin, menor é melhor' : m}</option>`).join('')}</select>
  </div>`;
  const f = frame(el, {
    cls: 'ch-test', reduced, size: [817, 488], controls, sub: '', legendRow: true,
    legend: [[`|background:${C.n1}`, 'literatura'], [`|background:${C.seq}`, 'só sequência'], [`|background:${C.net}`, 'rota de rede'], [`|background:${C.fuse}`, 'rota de fusão']],
    // every metric of the current ontology; the best value of each column in bold
    table: () => ({ rank: metrics.map((m, i) => ({ c: i + 2, lo: m === 'Smin' })), skip: T[ont].body.flatMap((r, i) => (NAIVE.test(r[0]) ? [i] : [])), head: [`Método, ${ont}`, 'Grupo', ...metrics.map((m) => ({ h: subHtml(m) }))], rows: T[ont].body.map((r) => [tr(r[0]), NAIVE.test(r[0]) ? 'referência' : GROUP[group(r[0])], ...metrics.map((m) => fmt(r[T[ont].head.indexOf(m)]))]) }),
  });
  const { svg, W, H } = f;
  const L = 185, R = W - 76, top = 10, bot = H - 34, bh = 22, head = 24, gap = 8;
  const plot = s(svg, 'g');

  function draw() {
    const v = vals(), smin = met === 'Smin', top1 = best(met);
    const methods = T[ont].body.map((r) => r[0]).filter((n) => !NAIVE.test(n));
    const naive = T[ont].body.find((r) => NAIVE.test(r[0]))[0];
    const max = Math.max(...Object.values(v));
    let hi = 100;
    if (smin) { hi = Math.ceil(max / 5) * 5; if ((hi - max) / hi < 0.12) hi += 5; }
    const x = smin ? lin(hi, 0, L, R) : lin(0, 100, L, R), x0 = x(0);
    f.setSub(`Teste, ${ont}, ${subHtml(met)}${smin ? ' em bits, menor é melhor, eixo invertido' : ' (%)'}`);
    for (const b of el.querySelectorAll('[data-o]')) b.setAttribute('aria-pressed', String(b.dataset.o === ont));
    el.querySelector('#test-metric').value = met;

    plot.replaceChildren();
    axisX(plot, x, range(0, hi, smin ? 5 : 20), top, bot, String);
    s(plot, 'text', { class: 'cap', x: W, y: top + 16, 'text-anchor': 'end' }, 'melhor →');
    const under = s(plot, 'g'); // reference and guide lines sit under the bars and labels
    const pitch = Math.min(36, (bot - top - 3 * head - 2 * gap) / methods.length);
    const ys = {};
    let y = top, g0 = '';
    for (const n of methods) {
      if (group(n) !== g0) {
        if (g0) y += gap;
        g0 = group(n);
        s(plot, 'text', { class: 'cap', x: 0, y: y + 17 }, GROUP[g0]);
        y += head;
      }
      ys[n] = y + pitch / 2;
      const m = mark(plot, fmt(v[n]), `${tr(n)} · ${ont} · ${met}`);
      if (emph && !emph[0].includes(n)) m.classList.add('dim');
      s(m, 'rect', { class: 'hit', x: 0, y, width: W, height: pitch });
      const b1 = v[n] === top1 ? ' b' : ''; // the best value of the column in bold
      s(m, 'text', { class: `lab${b1}`, x: 0, y: y + pitch / 2 + 7 }, tr(n));
      s(m, 'path', { class: 'm', d: hbar(x0, x(v[n]), y + (pitch - bh) / 2, bh), style: `fill:${color(n)}` });
      s(m, 'text', { class: `val${b1}`, 'data-v': n, x: x(v[n]) + (smin ? -8 : 8), y: y + pitch / 2 + 6, 'text-anchor': smin ? 'end' : 'start' }, fmt(v[n]));
      y += pitch;
    }
    s(under, 'line', { class: 'base', x1: x0, x2: x0, y1: top, y2: bot });
    s(under, 'line', { class: 'ref', x1: x(v[naive]), x2: x(v[naive]), y1: top, y2: bot });
    const nl = s(plot, 'text', { class: 'cap', x: x(v[naive]) + 6, y: top + 16 }, `${tr(naive)} `);
    s(nl, 'tspan', { 'data-v': naive }, fmt(v[naive]));
    if (emph && emph[1]) {
      const [, a, b, lab] = emph, ya = ys[a], yb = ys[b];
      s(under, 'line', { class: 'guide', x1: x(v[a]), x2: x(v[a]), y1: Math.min(ya, yb) - bh / 2, y2: Math.max(ya, yb) + bh / 2 });
      if (lab) s(plot, 'text', { class: 'val b', x: x(v[b]) + 76, y: yb + 6 }, pp(v[b] - v[a]));
    }
  }

  function set(o, m, e = null) {
    if (!ONT.includes(o) || !metrics.includes(m)) throw new Error(`INT-TEST: unknown ${o} / ${m}`);
    ont = o; met = m; emph = e;
    f.hideTip();
    draw();
  }
  el.addEventListener('click', (e) => { const b = e.target.closest('[data-o]'); if (b && !b.disabled) set(b.dataset.o, met); });
  el.querySelector('#test-metric').addEventListener('change', (e) => set(ont, e.target.value));
  draw();

  return {
    step(n) {
      cur = n;
      f.step(n);
      const [o, m, ...e] = STEPS[Math.min(n, STEPS.length - 1)];
      set(o, m, e.length ? e : null);
      for (const c of el.querySelectorAll('.controls button, .controls select')) c.disabled = n < 4;
    },
    set: (o, m) => set(o, m),
    render() {}, play() {}, pause() {},
    destroy: f.destroy,
    state: () => ({ ontology: ont, metric: met, values: vals(), step: cur, enabled: cur >= 4, emphasis: emph ? emph[0] : [] }),
  };
}
