// INT-MP (S08): message passing and the receptive field, on an illustrative 18-node graph.
// Node fills are neutral ink tints standing for feature vectors (no semantic colour); messages
// travel in --net. The dots are SMIL animations, so render(t) is svg.setCurrentTime(t) and the
// DOM never changes between frames; everything else is CSS keyed on the g1..g4 classes.
// Steps: 0-1 target highlighted · 2 one hop · 3 two hops · 4 colours converge to their mean.

const W = 696, H = 400, P = 2.4; // P: one message cycle, seconds
// id: [x, y, ring (hops from the target), ink tint %]
const N = {
  T: [300, 178, 0, 50],
  A1: [225, 128, 1, 20], A2: [382, 138, 1, 78], A3: [358, 236, 1, 36], A4: [225, 226, 1, 64],
  B1: [150, 80, 2, 86], B2: [312, 42, 2, 30], B3: [465, 100, 2, 58], B4: [500, 225, 2, 14], B5: [335, 315, 2, 70], B6: [130, 262, 2, 42],
  C1: [30, 125, 3, 60], C2: [55, 22, 3, 26], C3: [588, 38, 3, 74], C4: [655, 118, 3, 40], C5: [618, 312, 3, 22], C6: [668, 222, 3, 82], C7: [70, 345, 3, 52],
};
const E = ('T-A1 T-A2 T-A3 T-A4 A2-A3 A1-B1 A1-B2 A2-B2 A2-B3 A3-B4 A3-B5 A4-B5 A4-B6 '
  + 'B1-C1 B1-C2 B6-C1 B6-C7 B3-C3 B3-C4 C3-C4 B4-C6 B4-C5 C4-C6').split(' ').map((e) => e.split('-'));
const R = (id) => (id === 'T' ? 19 : 15);
const RING = [[128, 92, '1 salto'], [250, 162, '2 saltos']];

// a dot travelling from node a to node b during the window [t0, t1] of the cycle
function dot(a, b, t0, t1) {
  const [x1, y1] = N[a], [x2, y2] = N[b];
  const d = Math.hypot(x2 - x1, y2 - y1), ux = (x2 - x1) / d, uy = (y2 - y1) / d;
  const s = R(a) + 9, e = R(b) + 11;
  const path = `M${(x1 + ux * s).toFixed(1)} ${(y1 + uy * s).toFixed(1)}L${(x2 - ux * e).toFixed(1)} ${(y2 - uy * e).toFixed(1)}`;
  return `<circle r="8" class="mp-msg" opacity="0">`
    + `<animateMotion dur="${P}s" repeatCount="indefinite" path="${path}" calcMode="spline" keyPoints="0;0;1;1" keyTimes="0;${t0};${t1};1" keySplines="0 0 1 1;.45 0 .55 1;0 0 1 1"/>`
    + `<animate attributeName="opacity" dur="${P}s" repeatCount="indefinite" values="0;0;1;1;0;0" keyTimes="0;${t0};${(t0 + 0.04).toFixed(2)};${(t1 - 0.04).toFixed(2)};${t1};1"/>`
    + '</circle>';
}

export function mount(el, { reduced = false } = {}) {
  const ids = Object.keys(N);
  const mean = ids.reduce((a, id) => a + N[id][3], 0) / ids.length;
  const ringOf = (id) => N[id][2];
  // message edges: one ring further out -> one ring in
  const inward = E.map(([a, b]) => (ringOf(a) > ringOf(b) ? [a, b] : [b, a])).filter(([a, b]) => ringOf(a) === ringOf(b) + 1);
  const hop1 = inward.filter(([, b]) => b === 'T');
  const hop2 = inward.filter(([a]) => ringOf(a) === 2);
  const [tx, ty] = N.T;

  el.classList.add('mp');
  el.style.setProperty('--mp-mean', `color-mix(in oklab, var(--ink) ${mean.toFixed(1)}%, var(--slide))`);
  el.innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Passagem de mensagens num grafo pequeno: um nó-alvo, suas vizinhanças de um e dois saltos, e oversmoothing">
      <g class="mp-rings">${RING.map(([rx, ry, lab], k) => `
        <g class="mp-ring mp-ring${k + 1}">
          <ellipse cx="${tx}" cy="${ty}" rx="${rx}" ry="${ry}"/>
          <text x="${tx + rx}" y="${ty + 6}" text-anchor="middle">${lab}</text>
        </g>`).join('')}
      </g>
      <g class="mp-edges">${E.map(([a, b]) => {
        const k = ringOf(a) === ringOf(b) ? 0 : Math.max(ringOf(a), ringOf(b));
        return `<line class="mp-e mp-e${k <= 2 ? k : 0}" x1="${N[a][0]}" y1="${N[a][1]}" x2="${N[b][0]}" y2="${N[b][1]}"/>`;
      }).join('')}</g>
      <g class="mp-h1">${hop1.map(([a, b]) => dot(a, b, 0.15, 0.75)).join('')}</g>
      <g class="mp-h2">${hop2.map(([a, b]) => dot(a, b, 0.05, 0.45)).join('')}${hop1.map(([a, b]) => dot(a, b, 0.55, 0.95)).join('')}</g>
      <circle class="mp-halo" cx="${tx}" cy="${ty}" r="27"/>
      <g class="mp-nodes">${ids.map((id) => `<circle class="mp-n mp-r${ringOf(id)}" cx="${N[id][0]}" cy="${N[id][1]}" r="${R(id)}" style="--own:color-mix(in oklab, var(--ink) ${N[id][3]}%, var(--slide))"/>`).join('')}</g>
      <text class="mp-lab" x="${tx}" y="${ty - 36}" text-anchor="middle">alvo</text>
      <text class="mp-conv" x="${W - 4}" y="${H - 10}" text-anchor="end">camadas demais: as representações convergem</text>
    </svg>`;
  const svg = el.querySelector('svg');
  svg.pauseAnimations();
  let cur = 0, playing = false;

  function step(n) {
    cur = n;
    for (let k = 1; k <= 4; k++) el.classList.toggle(`g${k}`, n >= k);
    el.dataset.hops = n >= 3 ? 2 : n >= 2 ? 1 : 0;
    // reduced motion: a still frame with the messages half-way along their edges
    if (reduced) { svg.pauseAnimations(); svg.setCurrentTime(n >= 3 ? 0.25 * P : 0.45 * P); }
  }
  el.classList.toggle('mp-still', reduced);
  step(0);

  return {
    step,
    render(t) { el.classList.add('mp-still'); svg.pauseAnimations(); svg.setCurrentTime(t); },
    play() { if (reduced) return; playing = true; el.classList.remove('mp-still'); svg.unpauseAnimations(); },
    pause() { playing = false; svg.pauseAnimations(); },
    destroy() { svg.pauseAnimations(); el.innerHTML = ''; },
    state() {
      const hops = +el.dataset.hops;
      const lit = cur >= 4 ? ids.length : ids.filter((id) => ringOf(id) <= hops || hops === 0).length;
      const dots = hops === 1 ? hop1.length : hops === 2 ? hop2.length + hop1.length : 0;
      return { step: cur, hops, lit, dots, converged: cur >= 4, playing };
    },
  };
}
