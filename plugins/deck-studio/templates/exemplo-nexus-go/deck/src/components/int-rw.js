// INT-RW (S11): related work as a timeline (years from references.bib) and, for the five
// retrained baselines plus NEXUS-GO/Fixed, where the trainable parameters sit (§3.2, §3.3,
// Appendix B, Table B.1). Solid box with a 3 x 3 dot grid: trained; dashed box: fixed.
// Steps: 1 timeline · 2 statement (opts.statement) · 3 heading (opts.stripTitle) and pipelines.

const W = 1424, H = 630, COL = W / 5;
const ERAS = [
  [['Neighbour voting'], [['Vazquez et al.', '2003'], ['Sharan et al.', '2007']]],
  [['Diffusion'], [['Zhou et al.', '2004'], ['random walk with restart', '2006'], ['APPNP', '2019']]],
  [['Node embeddings'], [['DeepWalk', '2014'], ['node2vec', '2016'], ['Mashup', '2016'], ['deepNF', '2018']]],
  [['Hybrids and GNNs'], [['DeepGO', '2018'], ['Graph2GO', '2020'], ['DeepGraphGO', '2021'], ['CFAGO', '2023']]],
  [['Graph transformers', 'and 2025 hybrids'], [['NAGphormer', '2023'], ['SEGT-GO', '2025'], ['GTPLM-GO, GOBeacon, MSNGO,', ''], ['SPACE, ProtHGT', '(2025)']]],
];
// [label, trained?, semantic colour of the box edge (NEXUS-GO row only)]
const PIPES = [
  ['Mashup', [['random walk with restart', 0], ['low-dimensional factorization', 1], ['weighted k-NN (here)', 0]]],
  ['deepNF', [['diffusion + PPMI', 0], ['autoencoder', 1], ['MLP (here)', 1]]],
  ['MELISSA', [['labels as bicluster nodes', 0], ['diffusion', 0], ['low-dimensional embedding', 1], ['weighted k-NN', 0]]],
  ['DeepGraphGO', [['InterPro vector', 0], ['GNN layers: learned transforms, fixed Â', 1], ['output layer', 1]]],
  ['SEGT-GO', [['Â^k × InterPro, 4 hops', 0], ['transformer', 1]]],
  ['NEXUS-GO/Fixed', [['ProtT5 (frozen)', 0, 'seq'], ['fixed multi-hop diffusion', 0, 'net'], ['MLP head', 1]]],
];
const ROW0 = 334, ROWH = 49, BOXH = 38, X0 = 200, GAP = 40, PAD = 14;
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
const label = (s) => esc(s).replace(/\^k(.*)$/, '<tspan class="rw-sup" dy="-8">k</tspan><tspan dy="8">$1</tspan>');
const dots = () => [0, 1, 2].flatMap((r) => [0, 1, 2].map((c) => `<circle cx="${c * 6}" cy="${r * 6}" r="1.9"/>`)).join('');

export function mount(el, opts = {}) {
  const statement = opts.statement || 'Each step added parameters, tuning surface and cost';
  const stripTitle = opts.stripTitle || 'Five methods retrained here: Mashup, deepNF, MELISSA, DeepGraphGO, SEGT-GO';
  el.classList.add('rw');
  const eras = ERAS.map(([title, ex], i) => {
    const x = i * COL;
    return `<g class="rw-era">
      <circle class="rw-mark" cx="${x + 7}" cy="14" r="7"/>
      ${title.map((t, k) => `<text class="rw-era-t" x="${x}" y="${52 + k * 26}">${t}</text>`).join('')}
      ${ex.map(([n, y], k) => `<text class="rw-ex" x="${x}" y="${113 + k * 27}">${esc(n)}${y ? ` <tspan class="rw-yr">${y}</tspan>` : ''}</text>`).join('')}
    </g>`;
  }).join('');
  const rows = PIPES.map(([name, boxes], r) => {
    const y = ROW0 + r * ROWH, last = r === PIPES.length - 1;
    return `<g class="rw-row${last ? ' rw-ours' : ''}">
      ${last ? `<rect class="rw-band" x="0" y="${y - 5}" width="${W}" height="${BOXH + 10}" rx="6"/>` : ''}
      <text class="rw-name" x="12" y="${y + 26}">${name}</text>
      ${boxes.map(([t, learned, sem]) => `<g class="rw-box ${learned ? 'rw-learned' : 'rw-fixed'}${sem ? ` rw-${sem}` : ''}" data-y="${y}">
        <rect y="${y}" height="${BOXH}" rx="6"/><text y="${y + 25}">${label(t)}</text>${learned ? `<g class="rw-w">${dots()}</g>` : ''}
      </g>`).join('<path class="rw-arrow"/>')}
    </g>`;
  }).join('');

  el.innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Timeline of network-based protein function prediction and where the trainable parameters of six methods sit">
      <g class="rw-r1">
        <line class="rw-axis" x1="0" y1="14" x2="${W - 12}" y2="14"/><path class="rw-head" d="M${W} 14l-14 -7v14z"/>
        ${eras}
      </g>
      <text class="rw-r2 rw-stmt" x="0" y="258">${esc(statement)}</text>
      <g class="rw-r3">
        <text class="rw-h" x="0" y="312">${esc(stripTitle)}</text>
        <g class="rw-legend">
          <g class="rw-box rw-learned"><rect width="44" height="26" rx="5"/><g class="rw-w" transform="translate(16 7)">${dots()}</g></g><text class="rw-lt">trained</text>
          <g class="rw-box rw-fixed"><rect width="44" height="26" rx="5"/></g><text class="rw-lt">fixed</text>
        </g>
        ${rows}
      </g>
    </svg>`;

  // box widths follow the rendered text, so lay out after the fonts are in
  function layout() {
    for (const row of el.querySelectorAll('.rw-row')) {
      let x = X0;
      const boxes = [...row.querySelectorAll('.rw-box')];
      const arrows = [...row.querySelectorAll('.rw-arrow')];
      boxes.forEach((b, i) => {
        const t = b.querySelector('text'), y = +b.dataset.y;
        const learned = b.classList.contains('rw-learned');
        const w = Math.ceil(t.getComputedTextLength()) + 2 * PAD + (learned ? 26 : 0);
        b.querySelector('rect').setAttribute('x', x);
        b.querySelector('rect').setAttribute('width', w);
        t.setAttribute('x', x + PAD);
        if (learned) b.querySelector('.rw-w').setAttribute('transform', `translate(${x + w - PAD - 12} ${y + 13})`);
        x += w;
        if (arrows[i]) { const m = y + BOXH / 2; arrows[i].setAttribute('d', `M${x + 6} ${m}H${x + GAP - 12}M${x + GAP - 5} ${m}l-9 -6v12z`); x += GAP; }
      });
    }
    // legend, right-aligned on the heading line
    const lg = el.querySelector('.rw-legend'), [b1, b2] = lg.querySelectorAll('.rw-box'), [t1, t2] = lg.querySelectorAll('.rw-lt');
    let x = W - Math.ceil(t2.getComputedTextLength());
    t2.setAttribute('x', x); t2.setAttribute('y', 312); x -= 54; b2.setAttribute('transform', `translate(${x} 293)`);
    x -= 28 + Math.ceil(t1.getComputedTextLength());
    t1.setAttribute('x', x); t1.setAttribute('y', 312); x -= 54; b1.setAttribute('transform', `translate(${x} 293)`);
  }
  layout();
  document.fonts?.ready.then(() => { if (el.isConnected) layout(); });

  let cur = 0;
  function step(n) {
    cur = n;
    for (let k = 1; k <= 3; k++) el.classList.toggle(`g${k}`, n >= k);
  }
  step(0);
  return {
    step,
    render() {}, play() {}, pause() {},
    destroy() { el.innerHTML = ''; },
    state() {
      return {
        step: cur, timeline: cur >= 1, statement: cur >= 2 ? statement : null, strip: cur >= 3,
        eras: ERAS.length, methods: PIPES.map(([n, b]) => ({ name: n, trained: b.filter((x) => x[1]).length, fixed: b.filter((x) => !x[1]).length })),
      };
    },
  };
}
