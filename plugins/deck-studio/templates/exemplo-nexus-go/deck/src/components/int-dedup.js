// INT-DEDUP (S23): one protein, two neighbours, sum vs max deduplication.
// The example is the dissertation's own (§5.4.1): A has score 0.80 written five times,
// B has score 0.95 written once.

const REC = [
  { id: 'A', s: 0.80, c: 5 },
  { id: 'B', s: 0.95, c: 1 },
];
const RAW_AXIS = 4; // the sum rule reaches 4.00 for A
const f2 = (x) => x.toFixed(2);

export function mount(el, { reduced = false } = {}) {
  let mode = 'sum';
  el.classList.add('dd');
  el.innerHTML = `
    <div class="controls">
      <span class="lbl">rule</span>
      <span class="seg" role="group" aria-label="Deduplication rule">
        <button class="btn" type="button" id="dd-sum" data-mode="sum">sum</button>
        <button class="btn" type="button" id="dd-max" data-mode="max">max</button>
      </span>
    </div>
    <div class="dd-main">
      <svg class="dd-graph" viewBox="0 -10 330 320" role="img" aria-label="Protein i with neighbour A, five records of score 0.80, and neighbour B, one record of score 0.95">
        <g class="dd-edges"></g>
        <g class="dd-nodes">
          <circle cx="260" cy="150" r="30" class="dd-i"/><text x="260" y="158" text-anchor="middle">i</text>
          <circle cx="60" cy="62" r="26" class="dd-n"/><text x="60" y="70" text-anchor="middle">A</text>
          <circle cx="60" cy="238" r="26" class="dd-n"/><text x="60" y="246" text-anchor="middle">B</text>
        </g>
        <text x="96" y="30" class="dd-lab">0.80 × 5 records</text>
        <text x="96" y="290" class="dd-lab">0.95 × 1 record</text>
      </svg>
      <div class="dd-panels">
        <div class="dd-panel">
          <div class="dd-h">edge weight w<sub>ij</sub></div>
          ${REC.map((r) => `<div class="dd-row"><span class="dd-k">${r.id}</span><span class="dd-track"><i class="dd-bar" data-raw="${r.id}"></i></span><span class="dd-v num" data-raw-v="${r.id}"></span></div>`).join('')}
        </div>
        <div class="dd-panel">
          <div class="dd-h">share of i's column in P</div>
          ${REC.map((r) => `<div class="dd-row"><span class="dd-k">${r.id}</span><span class="dd-track"><i class="dd-bar" data-norm="${r.id}"></i></span><span class="dd-v num" data-norm-v="${r.id}"></span></div>`).join('')}
        </div>
      </div>
    </div>
    <p class="cap">Example from §5.4.1. Real file: mean multiplicity 3.06, maximum 170, no pair with divergent scores.</p>`;

  const q = (s) => el.querySelector(s);
  const edges = q('.dd-edges');

  function values() {
    const raw = REC.map((r) => (mode === 'sum' ? r.s * r.c : r.s));
    const tot = raw.reduce((a, b) => a + b, 0);
    return REC.map((r, i) => ({ id: r.id, raw: raw[i], norm: raw[i] / tot }));
  }

  function draw() {
    const v = values();
    el.dataset.mode = mode;
    for (const b of el.querySelectorAll('[data-mode]')) b.setAttribute('aria-pressed', String(b.dataset.mode === mode));
    for (const x of v) {
      q(`[data-raw="${x.id}"]`).style.width = `${(x.raw / RAW_AXIS) * 100}%`;
      q(`[data-norm="${x.id}"]`).style.width = `${x.norm * 100}%`;
      q(`[data-raw-v="${x.id}"]`).textContent = f2(x.raw);
      q(`[data-norm-v="${x.id}"]`).textContent = f2(x.norm);
    }
    // edges: the records of a pair, drawn as parallel strokes; under max they collapse to one
    const lines = [];
    REC.forEach((r, i) => {
      const y0 = i === 0 ? 62 : 238;
      const n = mode === 'sum' ? r.c : 1;
      for (let k = 0; k < n; k++) {
        const off = (k - (n - 1) / 2) * 7;
        lines.push(`<line x1="${86}" y1="${y0 + off}" x2="${232}" y2="${150 + off * 0.6}" style="stroke-width:${2 + r.s * 3}"/>`);
      }
    });
    edges.innerHTML = lines.join('');
  }

  el.addEventListener('click', (e) => {
    const b = e.target.closest('[data-mode]');
    if (!b) return;
    mode = b.dataset.mode;
    draw();
  });
  el.classList.toggle('dd-instant', reduced);
  draw();

  return {
    step() {},
    render() {},
    play() {}, pause() {}, destroy() { el.innerHTML = ''; },
    setMode(m) { mode = m; draw(); },
    state() { return { mode, ...Object.fromEntries(values().map((x) => [x.id, { raw: +f2(x.raw), norm: +f2(x.norm) }])) }; },
  };
}
