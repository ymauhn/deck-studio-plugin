// INT-GBA (S05): guilt by association, one pass of the naive baseline (Eq. 5.3,
// eq:met_baseline): y_i = sum_j s_ij / (sum_u s_iu) * y_j over the training neighbours.
// Illustrative data: six neighbours, all in the training partition, edge scores as specified.
// Each term's score lies in [0, 1] and the three need not sum to one (multi-label), so each
// term gets its own bar on a 0 to 100% track. The neighbours vote one after another: when a
// neighbour's pulses land, every term it carries grows by s_j / sum(s), so the bars climb in
// visible steps; at the end the centre takes the three colours, sized by score.

const TERMS = ['A', 'B', 'C'];
const NB = [ // clockwise from the top
  { s: 0.88, t: 'A' }, { s: 0.45, t: 'ABC' }, { s: 0.99, t: 'AB' },
  { s: 0.62, t: 'BC' }, { s: 0.93, t: 'A' }, { s: 0.71, t: 'B' },
];
const SUM = NB.reduce((a, b) => a + b.s, 0);
const SCORE = Object.fromEntries(TERMS.map((k) => [k, NB.reduce((a, b) => a + (b.t.includes(k) ? b.s / SUM : 0), 0)]));
const PCT = Object.fromEntries(TERMS.map((k) => [k, Math.round(SCORE[k] * 100)]));

const VW = 520, VH = 290, CX = 260, CY = 145, RX = 190, RY = 118, RC = 32, RN = 22;
const DOT = 5.5, DOT_GAP = 13;
const T_GAP = 0.22, T_PULSE = 0.65, T_GROW = 0.3; // one neighbour every T_GAP s
const T_LAST = (NB.length - 1) * T_GAP + T_PULSE; // last pulses land
const T_CENTRE = T_LAST + T_GROW, DUR = T_CENTRE + 0.45;
const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const f1 = (x) => x.toFixed(1);

const pos = NB.map((_, j) => {
  const a = -Math.PI / 2 + (j * Math.PI) / 3;
  return { a, x: CX + RX * Math.cos(a), y: CY + RY * Math.sin(a) };
});
const dots = NB.flatMap((n, j) => [...n.t].map((k, d) => ({ j, k, dx: (d - (n.t.length - 1) / 2) * DOT_GAP })));
// centre: the three inherited colours in a small triangle, area proportional to the score
const CDOT = TERMS.map((k, i) => {
  const a = -Math.PI / 2 + (i * 2 * Math.PI) / 3;
  return { k, x: 11 * Math.cos(a), y: 11 * Math.sin(a), r: 10 * Math.sqrt(SCORE[k]) };
});

export function mount(el, { reduced = false } = {}) {
  el.classList.add('gb');
  const aria = `Uma proteína de função desconhecida ligada a seis vizinhos anotados por arestas de confiança ${NB.map((n) => n.s.toFixed(2).replace('.', ',')).join('; ')}. Uma passagem do baseline ingênuo dá ${TERMS.map((k) => `termo ${k} ${PCT[k]}%`).join(', ')}.`;
  el.innerHTML = `
    <svg class="gb-g" viewBox="0 0 ${VW} ${VH}" role="img" aria-label="${aria}">
      <g class="gb-edges">${NB.map((n, j) => `<line x1="${CX}" y1="${CY}" x2="${f1(pos[j].x)}" y2="${f1(pos[j].y)}" stroke-width="${(1.5 + 6 * n.s).toFixed(2)}"/>`).join('')}</g>
      <g>${NB.map((n, j) => {
        // label at the middle of the visible edge, between the centre and the neighbour rims
        const L = Math.hypot(pos[j].x - CX, pos[j].y - CY), u = (RC + (L - RN - RC) / 2) / L;
        const x = CX + (pos[j].x - CX) * u, y = CY + (pos[j].y - CY) * u;
        return `<rect class="gb-pill" x="${f1(x - 23)}" y="${f1(y - 12)}" width="46" height="24" rx="12"/><text class="gb-lab" x="${f1(x)}" y="${f1(y + 1)}" text-anchor="middle" dominant-baseline="central">${n.s.toFixed(2).replace('.', ',')}</text>`;
      }).join('')}</g>
      <g class="gb-pulses">${dots.map((d) => `<circle class="gb-t${d.k}" r="${f1(3 + 4 * NB[d.j].s)}"/>`).join('')}</g>
      <g>${NB.map((n, j) => `<circle class="gb-n" cx="${f1(pos[j].x)}" cy="${f1(pos[j].y)}" r="${RN}"/>`).join('')}
        ${dots.map((d) => `<circle class="gb-t${d.k}" cx="${f1(pos[d.j].x + d.dx)}" cy="${f1(pos[d.j].y)}" r="${DOT}"/>`).join('')}</g>
      <g transform="translate(${CX} ${CY})">
        <circle class="gb-c" r="${RC}"/>
        <text class="gb-q" text-anchor="middle" dominant-baseline="central" y="2">?</text>
        <g class="gb-cdots">${CDOT.map((c) => `<circle class="gb-t${c.k}" cx="${f1(c.x)}" cy="${f1(c.y)}" r="0"/>`).join('')}</g>
      </g>
    </svg>
    <div class="gb-bars">${TERMS.map((k) => `<div class="gb-row"><span class="gb-name"><i class="gb-sw gb-b${k}"></i>termo ${k}</span><span class="gb-track"><span class="gb-fill gb-b${k}"></span></span><b class="gb-pc num">0%</b></div>`).join('')}</div>
    <p class="gb-foot">uma diretriz probabilística, não uma regra</p>
    <p class="cap">valores ilustrativos</p>`;

  const q = (s) => el.querySelector(s);
  const pulses = [...el.querySelectorAll('.gb-pulses circle')];
  const edges = [...el.querySelectorAll('.gb-edges line')];
  const cdots = [...el.querySelectorAll('.gb-cdots circle')];
  const fills = [...el.querySelectorAll('.gb-fill')];
  const pcs = [...el.querySelectorAll('.gb-pc')];
  const mark = q('.gb-q');
  let n = 0, raf = 0, phase = 'question';

  // frame t of the reveal: 0 is the static graph with "?", DUR the filled centre
  function draw(t) {
    dots.forEach((d, i) => {
      const u = (t - d.j * T_GAP) / T_PULSE;
      const c = pulses[i];
      if (u <= 0 || u >= 1) { c.setAttribute('opacity', '0'); return; }
      const e = ease(u);
      c.setAttribute('opacity', '1');
      c.setAttribute('cx', f1(pos[d.j].x + d.dx + (CX - pos[d.j].x - d.dx) * e));
      c.setAttribute('cy', f1(pos[d.j].y + (CY - pos[d.j].y) * e));
    });
    // the edge carrying a vote lights up while its pulses travel
    edges.forEach((l, j) => {
      const u = (t - j * T_GAP) / T_PULSE;
      l.classList.toggle('on', u > 0 && u < 1);
    });
    TERMS.forEach((k, i) => {
      const v = NB.reduce((a, b, j) => a + (b.t.includes(k) ? (b.s / SUM) * ease((t - j * T_GAP - T_PULSE) / T_GROW) : 0), 0);
      fills[i].style.width = `${(v * 100).toFixed(2)}%`;
      pcs[i].textContent = `${Math.round(v * 100)}%`;
    });
    const c = ease((t - T_CENTRE) / 0.45);
    mark.setAttribute('opacity', (1 - c).toFixed(3));
    cdots.forEach((d, i) => d.setAttribute('r', f1(CDOT[i].r * c)));
    phase = t <= 0 ? 'question' : t >= DUR ? 'final' : 'animating';
  }

  const stop = () => { cancelAnimationFrame(raf); raf = 0; };
  function start() {
    stop();
    const t0 = performance.now();
    const frame = (ms) => {
      const t = (ms - t0) / 1000;
      draw(Math.max(0, Math.min(t, DUR)));
      raf = t < DUR ? requestAnimationFrame(frame) : 0;
    };
    draw(0);
    raf = requestAnimationFrame(frame);
  }
  draw(0);

  return {
    step(k) {
      const was = n; n = k;
      if (k < 2) { stop(); draw(0); return; }
      if (!reduced && was < 2) start();
      else if (!raf) draw(DUR);
    },
    render(t) { stop(); draw(Math.max(0, Math.min(t, DUR))); },
    play() {},
    pause() { if (raf) { stop(); draw(DUR); } },
    destroy() { stop(); el.innerHTML = ''; },
    state() {
      return {
        step: n, phase, duration: DUR,
        confidences: NB.map((x) => x.s),
        scores: Object.fromEntries(TERMS.map((k) => [k, +SCORE[k].toFixed(4)])),
        percent: { ...PCT },
      };
    },
  };
}
