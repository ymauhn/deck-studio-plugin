// INT-PROP (S24): fixed propagation on a toy graph, live.
// Iterates Eq. 5.11 (eq:met_recorrencia) with P = W Dc^-1 (Eq. 5.9, eq:met_P) and checks it
// against the closed form of Eq. 5.12 (eq:met_binomial). Graph and vectors are illustrative.

const NODES = [ // x, y, initial 3-d vector in [-1, 1]^3
  [205, 205, [0.10, -0.20, 0.30]], // 0 hub, degree 6
  [120, 120, [0.90, -0.60, -0.40]],
  [285, 115, [-0.70, 0.80, -0.50]],
  [305, 230, [0.60, 0.70, -0.80]],
  [250, 315, [-0.50, -0.80, 0.90]],
  [125, 300, [0.80, 0.50, 0.60]],
  [80, 205, [-0.90, -0.30, -0.70]],
  [340, 395, [0.30, 0.90, 0.80]], // chain 4-7-8-9
  [425, 345, [-0.60, 0.20, 0.95]],
  [440, 255, [0.95, -0.90, 0.20]],
  [55, 380, [-0.20, 0.95, 0.10]],
  [45, 70, [0.50, -0.95, 0.85]],
  [390, 60, [0.90, 0.30, -0.90]], // isolated
  [455, 120, [-0.80, 0.85, 0.70]], // isolated
];
const EDGES = [ // i, j, w in [0.40, 0.99]
  [0, 1, 0.91], [0, 2, 0.74], [0, 3, 0.88], [0, 4, 0.62], [0, 5, 0.55], [0, 6, 0.97],
  [1, 6, 0.48], [2, 3, 0.52], [3, 4, 0.70], [4, 7, 0.83], [7, 8, 0.66], [8, 9, 0.99],
  [5, 10, 0.44], [1, 11, 0.79],
];
const ISOLATED = [12, 13];
const N = NODES.length;
const TMAX = 10;
const R = 25;

// ---------- numerics ----------
const H0 = NODES.map((n) => n[2]);
const W = Array.from({ length: N }, () => new Float64Array(N));
for (const [i, j, w] of EDGES) { W[i][j] = w; W[j][i] = w; }
const EPS = 1e-12;
const colSum = Array.from({ length: N }, (_, j) => Math.max(W.reduce((s, row) => s + row[j], 0), EPS));
const P = W.map((row) => row.map((w, j) => w / colSum[j])); // column-stochastic, isolated columns stay zero
const PT = (H) => H.map((_, i) => [0, 1, 2].map((c) => H.reduce((s, h, j) => s + P[j][i] * h[c], 0)));
const step = (H, a) => { const m = PT(H); return H.map((h, i) => h.map((v, c) => a * v + (1 - a) * m[i][c])); };
const binom = (n, k) => { let r = 1; for (let q = 1; q <= k; q++) r = (r * (n - k + q)) / q; return r; };
const hopWeights = (T, a) => Array.from({ length: T + 1 }, (_, k) => binom(T, k) * a ** (T - k) * (1 - a) ** k);
const powers = [H0]; // (P^T)^k H0, k = 0..TMAX
for (let k = 1; k <= TMAX; k++) powers.push(PT(powers[k - 1]));
const iterate = (T, a) => { let H = H0; for (let h = 0; h < T; h++) H = step(H, a); return H; };
const closed = (T, a) => {
  const w = hopWeights(T, a);
  return H0.map((_, i) => [0, 1, 2].map((c) => w.reduce((s, wk, k) => s + wk * powers[k][i][c], 0)));
};
const norm = (v) => Math.hypot(...v);
const f2 = (x) => x.toFixed(2);

export function mount(el, { reduced = false, math = {} } = {}) {
  let T = 2, alpha = 0.5, timer = null, H = H0, check = 0, view = 0;
  el.classList.add('pp');
  el.innerHTML = `
    <div class="controls pp-controls">
      <label class="lbl" for="prop-T">steps ${math['i:prop-T'] || 'T'}</label>
      <input type="range" id="prop-T" min="0" max="${TMAX}" step="1" value="${T}">
      <output class="pp-out num" for="prop-T" id="prop-T-v"></output>
      <label class="lbl" for="prop-alpha">retention ${math['i:prop-alpha'] || 'α'}</label>
      <input type="range" id="prop-alpha" min="0.1" max="0.9" step="0.1" value="${alpha}">
      <output class="pp-out num" for="prop-alpha" id="prop-alpha-v"></output>
      <button class="btn" type="button" id="prop-play" aria-pressed="false">play</button>
    </div>
    <div class="pp-main">
      <div class="pp-graph">
        <svg viewBox="0 0 490 440" role="img" aria-label="Toy graph of 14 proteins: 12 connected around a hub and a chain, 2 isolated; node colours are 3-d vectors">
          <rect class="pp-iso-box" x="350" y="22" width="134" height="140" rx="10"/>
          <text class="pp-iso-lab" x="417" y="182" text-anchor="middle">isolated</text>
          <g class="pp-edges">${EDGES.map(([i, j, w]) => `<line x1="${NODES[i][0]}" y1="${NODES[i][1]}" x2="${NODES[j][0]}" y2="${NODES[j][1]}" style="stroke-width:${(1 + 7 * (w - 0.4) / 0.59).toFixed(2)}"/>`).join('')}</g>
          <g class="pp-nodes">${NODES.map(([x, y], i) => `<g class="pp-node" data-i="${i}" transform="translate(${x} ${y})"><circle r="${R}"/>${[0, 1, 2].map((c) => `<rect class="pp-bar" x="${-12 + c * 9}" width="6" rx="1"/>`).join('')}</g>`).join('')}</g>
        </svg>
        <div class="pp-iso-note">${math['i:prop-iso'] || 'α^T H(0)'}</div>
      </div>
      <div class="pp-panel">
        <div class="pp-h">weight of hop ${math['i:prop-k'] || 'k'}</div>
        <svg class="pp-hops" viewBox="0 0 300 220" role="img" aria-label="Binomial weights over hop counts">
          <line class="pp-axis" x1="10" y1="190" x2="294" y2="190"/>
          ${Array.from({ length: TMAX + 1 }, (_, k) => `<rect class="pp-hop" data-k="${k}" x="${14 + k * 25.5}" width="20" rx="3"/><text class="pp-k" x="${24 + k * 25.5}" y="214" text-anchor="middle">${k}</text>`).join('')}
        </svg>
        <dl class="pp-read">
          <dt>own weight ${math['i:prop-aT'] || 'α^T'}</dt><dd class="num" id="prop-own"></dd>
          <dt>mean hops ${math['i:prop-mean'] || 'T(1 − α)'}</dt><dd class="num" id="prop-mean"></dd>
          <dt>spread of connected nodes</dt><dd class="num" id="prop-spread"></dd>
        </dl>
      </div>
    </div>
    <p class="cap">Illustrative graph, 3-d vectors drawn as colour and as three bars; edge width follows the weight. Isolated nodes only shrink.</p>`;

  const q = (s) => el.querySelector(s);
  const sT = q('#prop-T'), sA = q('#prop-alpha'), bPlay = q('#prop-play');
  const nodes = [...el.querySelectorAll('.pp-node')];
  const hops = [...el.querySelectorAll('.pp-hop')];
  const fill = (v) => `rgb(${v.map((x) => Math.round(255 * (0.5 + 0.5 * Math.max(-1, Math.min(1, x))))).join(',')})`;

  function compute() {
    H = iterate(T, alpha);
    const C = closed(T, alpha);
    check = Math.max(...H.flatMap((h, i) => h.map((v, c) => Math.abs(v - C[i][c]))));
    const w = hopWeights(T, alpha);
    const s = w.reduce((a, b) => a + b, 0);
    if (check > 1e-9 || Math.abs(s - 1) > 1e-9) console.error(`INT-PROP check failed: closed form ${check}, sum ${s}`);
    return w;
  }

  function drawNodes(Hd) {
    nodes.forEach((g, i) => {
      g.querySelector('circle').style.fill = fill(Hd[i]);
      g.querySelectorAll('.pp-bar').forEach((b, c) => {
        const v = Hd[i][c], h = Math.max(0.8, Math.abs(v) * 17);
        b.setAttribute('y', v >= 0 ? -h : 0);
        b.setAttribute('height', h);
      });
    });
  }

  function draw() {
    const w = compute();
    drawNodes(H);
    hops.forEach((r, k) => {
      const h = k <= T ? w[k] * 180 : 0;
      r.setAttribute('y', 190 - h); r.setAttribute('height', h);
      r.classList.toggle('own', k === 0);
    });
    el.querySelectorAll('.pp-k').forEach((t, k) => t.classList.toggle('off', k > T));
    sT.value = T; sA.value = alpha;
    q('#prop-T-v').textContent = String(T);
    q('#prop-alpha-v').textContent = alpha.toFixed(1);
    q('#prop-own').textContent = f2(alpha ** T);
    q('#prop-mean').textContent = f2(T * (1 - alpha));
    q('#prop-spread').textContent = f2(spread(H));
  }

  function spread(Hs) {
    const c = Hs.slice(0, 12); let s = 0, n = 0;
    for (let i = 0; i < c.length; i++) for (let j = i + 1; j < c.length; j++) { s += norm(c[i].map((v, k) => v - c[j][k])); n++; }
    return s / n;
  }

  function stop() {
    clearInterval(timer); timer = null;
    bPlay.setAttribute('aria-pressed', 'false');
  }
  function sweep() {
    if (timer) { stop(); return; }
    if (reduced) { T = TMAX; draw(); return; }
    T = 0; draw();
    bPlay.setAttribute('aria-pressed', 'true');
    timer = setInterval(() => { if (T >= TMAX) { stop(); return; } T++; draw(); }, 600);
  }

  sT.addEventListener('input', () => { stop(); T = +sT.value; draw(); });
  sA.addEventListener('input', () => { stop(); alpha = Math.round(+sA.value * 10) / 10; draw(); });
  bPlay.addEventListener('click', sweep);
  el.classList.toggle('pp-instant', reduced);
  draw();

  // GIF timeline (docs/INTERACTIVES.md): alpha 0.5, T 0 -> 10 -> 0, then alpha 0.9 -> 0.1 at T = 7
  const SEG = 0.5; // seconds per unit step
  function at(t) {
    const up = TMAX * SEG;
    if (t < up) return { T: t / SEG, a: 0.5 };
    if (t < 2 * up) return { T: TMAX - (t - up) / SEG, a: 0.5 };
    const u = Math.min(8, (t - 2 * up) / SEG);
    return { T: 7, a: 0.9 - 0.1 * u };
  }

  return {
    step(n) { view = n; el.classList.toggle('pp-nohops', n < 3); },
    render(t) {
      stop();
      const s = at(t);
      const a = Math.round(s.a * 1000) / 1000;
      const lo = Math.floor(s.T), hi = Math.ceil(s.T), f = s.T - lo;
      T = Math.round(s.T); alpha = Math.round(a * 10) / 10;
      draw();
      if (hi !== lo) { // smooth colour between integer steps for the export
        const A = iterate(lo, a), B = iterate(hi, a);
        drawNodes(A.map((h, i) => h.map((v, c) => v + f * (B[i][c] - v))));
      }
    },
    duration: 2 * TMAX * SEG + 8 * SEG + 1,
    play() {}, pause() { stop(); },
    destroy() { stop(); el.innerHTML = ''; },
    set(t, a) { stop(); T = t; alpha = a; draw(); },
    state() {
      const w = hopWeights(T, alpha);
      return {
        T, alpha, view, weights: w, sumWeights: w.reduce((a, b) => a + b, 0), closedFormError: check,
        isolated: ISOLATED.map((i) => ({ node: i, norm: norm(H[i]), initial: norm(H0[i]) })),
        fills: nodes.map((g) => g.querySelector('circle').style.fill),
      };
    },
  };
}
