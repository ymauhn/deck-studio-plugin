// INT-PLM (S10): a protein language model, schematic. Residues as tokens, attention from one
// residue, three encoder layers read (22, 23, 24), each mean-pooled to 1024 and concatenated in
// the order 24 | 23 | 22 into the 3072-dimensional protein vector (dissertation §5.4.1).
// The attention weights and the per-residue shades are illustrative; the caption says so.
// Steps: 1 tokens · 2 attention arcs · 3 layer bands · 4 mean-pool and concatenation.

const W = 817, H = 560;
const SEQ = 'MKTAYIAKQRQISFVKSHFSRQ';
const SRC = 7; // the K at position 8
const ATT = [[1, 0.35], [3, 0.6], [5, 0.9], [9, 0.75], [12, 0.4], [15, 0.95], [18, 0.3], [20, 0.55]];
const PITCH = 28, CW = 25, TY = 112, TH = 44;
const BAND_W = (SEQ.length - 1) * PITCH + CW;
const LAYERS = [22, 23, 24];
const bandY = (k) => 214 + 64 * k; // top of the band of LAYERS[k]
const BH = 26, PX = 672, PW = 80; // pooled bar: x, width
const JY = 440, JX = 452, JW = PW; // joined bar: y, x, segment width
const JOIN = [24, 23, 22]; // concatenation order, deepest first (Eq. 5.6)
const cx = (i) => i * PITCH + CW / 2;
const shade = (l, i) => { const s = Math.sin(i * 12.9898 + l * 78.233) * 43758.5453; return 18 + 62 * (s - Math.floor(s)); };

export function mount(el) {
  el.classList.add('plm');
  const arcs = ATT.map(([j, w], k) => {
    const x1 = cx(SRC), x2 = cx(j), h = Math.min(120, 24 + Math.abs(x2 - x1) * 0.42);
    return `<path class="plm-arc" pathLength="1" d="M${x1} ${TY}C${x1} ${TY - h} ${x2} ${TY - h} ${x2} ${TY}" style="opacity:${w};stroke-width:${(1.5 + 2.5 * w).toFixed(2)};--k:${k}"/>`;
  }).join('');
  const toks = [...SEQ].map((c, i) => `
    <g class="plm-tok${i === SRC ? ' plm-src' : ''}" style="--i:${i}">
      <rect x="${i * PITCH}" y="${TY}" width="${CW}" height="${TH}" rx="4"/>
      <text x="${cx(i)}" y="${TY + 30}" text-anchor="middle">${c}</text>
    </g>`).join('');
  const bands = LAYERS.map((l, k) => {
    const y = bandY(k);
    const cells = [...SEQ].map((_, i) => `<rect x="${i * PITCH}" y="${y}" width="${CW}" height="${BH}" rx="3" style="fill:color-mix(in oklab, var(--seq) ${shade(l, i).toFixed(0)}%, var(--slide))"/>`).join('');
    return `
    <g class="plm-band" style="--k:${k}">
      <text class="plm-lab" x="0" y="${y - 9}">camada ${l}</text>
      <g class="plm-cells">${cells}</g>
      <rect class="plm-pool" x="0" y="${y}" width="${BAND_W}" height="${BH}" rx="3" style="--s:${(PW / BAND_W).toFixed(4)};--px:${PX}px"/>
      <g class="plm-arrow"><line x1="${BAND_W + 14}" y1="${y + BH / 2}" x2="${PX - 12}" y2="${y + BH / 2}"/><path d="M${PX - 6} ${y + BH / 2}l-9 -6v12z"/></g>
      <text class="plm-dim" x="${PX + PW + 8}" y="${y + 20}">1024</text>
    </g>`;
  }).join('');
  const joined = JOIN.map((l, j) => {
    const k = LAYERS.indexOf(l), x = JX + j * (JW + 2);
    return `<g class="plm-seg" style="--dx:${PX - x}px;--dy:${bandY(k) - JY}px;--j:${j}">
      <rect x="${x}" y="${JY}" width="${JW}" height="34" rx="3"/>
      <text x="${x + JW / 2}" y="${JY + 58}" text-anchor="middle">${l}</text>
    </g>`;
  }).join('');

  el.innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Modelo de linguagem de proteínas, esquemático: tokens de resíduos, atenção de um resíduo para os outros, camadas 22 a 24 com mean-pooling para 1.024 cada e concatenadas em 3.072">
      <g class="plm-arcs">${arcs}</g>
      <text class="plm-note plm-n2" x="640" y="60">autoatenção</text>
      <g class="plm-toks">${toks}</g>
      <text class="plm-note plm-n1" x="640" y="${TY + 29}">tokens de resíduos</text>
      ${bands}
      <text class="plm-note plm-n4" x="${BAND_W + 8}" y="${bandY(0) - 9}">mean-pooling</text>
      <g class="plm-join">${joined}
        <text class="plm-note plm-n4b" x="${JX - 14}" y="${JY + 24}" text-anchor="end">vetor da proteína</text>
        <text class="plm-dim plm-total" x="${JX + 3 * JW + 4 + 10}" y="${JY + 25}">3072</text>
      </g>
      <text class="cap plm-cap" x="0" y="${H - 8}">esquemático</text>
    </svg>`;

  let cur = 0;
  function step(n) {
    cur = n;
    for (let k = 1; k <= 4; k++) el.classList.toggle(`g${k}`, n >= k);
  }
  step(0);
  return {
    step,
    render() {}, play() {}, pause() {},
    destroy() { el.innerHTML = ''; },
    state() { return { step: cur, tokens: cur >= 1 ? SEQ.length : 0, arcs: cur >= 2 ? ATT.length : 0, layers: cur >= 3 ? LAYERS : [], pooled: cur >= 4, dims: cur >= 4 ? 3 * 1024 : 0 }; },
  };
}
