// INT-FUNNEL (S30): the selection funnel of §5.7. Ten stations left to right, each with its
// stage, winner and the size of the comparison where the dissertation states it. Counts, depth
// and retention winners are read from thesis_tables.json; the winner names are labels.
// Steps: 0-1 hidden · 2 stations 1-9 appear with the line (about 2.5 s) · 3 the test station.

const W = 1424, H = 360, Y = 180, X0 = 100, DX = 136, LINE_S = 2.2;

function stations(d) {
  const n = (k) => d[k].rows.length - 1;
  const best = (rows, c) => rows.slice(1).filter((r) => typeof r[c] === 'number').reduce((a, r) => (r[c] > a[c] ? r : a))[0];
  const hv = d.hops_vector.rows, av = d.alpha_vector.rows;
  const range = (rows) => `${rows[1][0]}–${rows[rows.length - 1][0]}`;
  const early = d.cost_runs.rows.filter((r) => /^Early fusion/.test(r[0])).reduce((a, r) => a + r[2], 0);
  const late = +String(d.fusion_grid.rows.find((r) => /Total/.test(r[0]))[2]).replace(/\D/g, '');
  const f1 = (x) => x.toFixed(1);
  return [
    [['objective'], 'ProteinLoss', `${n('loss')} compared`],
    [['vector architecture', '× pooling'], 'MLP raw', `${n('gen1_arch')} compared`],
    [['vision backbone', '× pooling'], 'ConvNeXt-Tiny', `${n('gen1_backbone')} compared`],
    [['depth T, BP/CC/MF'], `T = ${[1, 2, 3].map((c) => best(hv, c)).join('/')} (vector)`, `T = ${range(hv)}, per head`],
    [['retention α, BP/CC'], `α = ${[1, 2].map((c) => f1(best(av, c))).join('/')}`, `α = ${f1(av[1][0])}–${f1(av[av.length - 1][0])}`],
    [['learned encoder'], 'GCN', 'GCN vs GAT, 2 heads'],
    [['deduplication'], 'max', 'max vs sum'],
    [['early fusion'], 'add + GCN + vector', `${early}-run grid`],
    [['late fusion'], 'linear γ', `${late} per ontology`],
    [['test, read once'], 'NEXUS-GO/Late', ''],
  ];
}

export function mount(el, opts = {}) {
  const S = stations(opts.data);
  const x = (i) => X0 + i * DX;
  el.classList.add('fnl');
  const st = S.map(([lab, win, cnt], i) => {
    const up = i % 2 === 0, lines = [...lab, win, ...(cnt ? [cnt] : [])];
    const cls = [...lab.map(() => 'fnl-lab'), 'fnl-win', ...(cnt ? ['fnl-cnt'] : [])];
    // above the line: stacked upward from the line; below: downward
    const ys = up ? lines.map((_, k) => Y - 30 - (lines.length - 1 - k) * 28) : lines.map((_, k) => Y + 46 + k * 28);
    const test = i === S.length - 1;
    return `<g class="fnl-st${test ? ' fnl-test' : ''}" style="--d:${((i / (S.length - 2)) * LINE_S).toFixed(2)}s">
      <line class="fnl-tick" x1="${x(i)}" y1="${up ? Y - 14 : Y + 14}" x2="${x(i)}" y2="${up ? Y - 24 : Y + 24}"/>
      <circle class="fnl-mark" cx="${x(i)}" cy="${Y}" r="${test ? 13 : 9}"/>
      ${lines.map((t, k) => `<text class="${cls[k]}" x="${x(i)}" y="${ys[k]}" text-anchor="middle">${t}</text>`).join('')}
    </g>`;
  }).join('');
  el.innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Selection funnel: nine validation stages, each passing its winner on, then a single read of the test set">
      <path class="fnl-line" pathLength="1" d="M${x(0)} ${Y}H${x(S.length - 2)}"/>
      <path class="fnl-line fnl-last" pathLength="1" d="M${x(S.length - 2)} ${Y}H${x(S.length - 1)}"/>
      ${st}
    </svg>`;

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
      return { step: cur, visible: cur >= 3 ? S.length : cur >= 2 ? S.length - 1 : 0, test: cur >= 3, stations: S.map(([l, w, c]) => ({ stage: l.join(' '), winner: w, compared: c })) };
    },
  };
}
