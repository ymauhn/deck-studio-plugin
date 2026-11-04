// INT-PIPE (S21): the NEXUS-GO pipeline. HTML nodes over an SVG edge layer, route buttons,
// flow dashes and particles in the semantic colours, and a toggle to the cropped Fig. 5.6.

const STAGE_W = 1424, STAGE_H = 470;
const A = 52, A2 = 140, B = 232, C = 330, D = 424; // row centres
// id: [x, yCentre, width, kind, lines, tooltip]; kind sets the outline colour
const NODES = {
  seq: [0, A, 140, 'seq', ['sequência', 'proteica'], 'Sequência de aminoácidos · toda proteína tem uma'],
  prott5: [165, A, 170, 'seq', ['ProtT5-XL-U50', 'congelado'], 'ProtT5-XL-U50 · codificador congelado · camadas 24, 23, 22 · trechos de até 1.022 resíduos'],
  h0: [360, A, 150, 'seq', ['@h0'], 'Mean-pooling por trecho, média entre trechos, 3 × 1.024 concatenadas'],
  string: [0, B, 140, 'net', ['STRING', 'registros'], 'STRING v11.5 · 2.422.234 registros · 791.011 pares distintos'],
  dedup: [165, B, 170, 'net', ['deduplicação', 'max'], 'Deduplicação · max preserva o escore; a soma o multiplica pelo número de registros'],
  W: [360, B, 150, 'net', ['grafo', 'ponderado @W'], 'Simétrico, sem autolaços, COO esparso'],
  P: [535, B, 130, 'net', ['@P'], 'Estocástica por coluna · colunas isoladas ficam nulas'],
  fixprop: [700, A2, 190, 'net', ['Propagação fixa', '@HT'], 'Propagação fixa · sem parâmetros · calculada uma vez e guardada em cache · T e α ajustados por ontologia'],
  edges: [535, C, 130, 'net', ['arestas', '+ escore'], 'Índice de arestas com o escore do STRING como atributo da aresta'],
  gnn: [700, C, 190, 'net', ['GCN / GAT', '2 camadas'], 'Propagação aprendida · largura 1.024 · recalculada a cada passo de otimização'],
  g: [925, C, 125, 'net', ['@g'], 'Saída armazenada do codificador treinado, lida do seu checkpoint'],
  headfix: [1080, A2, 110, 'head', ['cabeça', 'MLP'], 'MLP [1.024, 512] · normalização em lote · dropout 0,4'],
  headgnn: [1080, C, 110, 'head', ['cabeça', 'MLP'], 'MLP [1.024, 512] · normalização em lote · dropout 0,4'],
  pfix: [1215, A2, 70, 'fuse', ['@pfix'], 'Probabilidades dos termos do NEXUS-GO/Fixed'],
  pgnn: [1215, C, 70, 'fuse', ['@pgnn'], 'Probabilidades dos termos do NEXUS-GO/GNN'],
  late: [1304, B, 120, 'fuse', ['Fusão tardia', '@gamma linear'], 'Fusão tardia · γ = 0,50 BP, 0,55 CC e MF · escolhido na validação'],
  out: [1304, A, 120, 'fuse', ['termos GO'], 'Escores dos termos do NEXUS-GO/Late'],
  early: [700, D, 350, 'fuse', ['Fusão precoce', 'concat 4.096 | soma 3.072'], 'Fusão precoce · uma cabeça treinada na representação unida · a saída do codificador fica armazenada'],
  headearly: [1080, D, 110, 'head', ['cabeça', 'MLP'], 'MLP [1.024, 512] · normalização em lote · dropout 0,4'],
  outearly: [1215, D, 160, 'fuse', ['termos GO'], 'Escores dos termos do NEXUS-GO/Early'],
};
const BRANCH = { seq: ['seq', 'prott5', 'h0'], net: ['string', 'dedup', 'W', 'P'] };
const ROUTES = {
  all: Object.keys(NODES),
  fixed: ['seq', 'prott5', 'h0', 'string', 'dedup', 'W', 'P', 'fixprop', 'headfix', 'pfix'],
  gnn: ['seq', 'prott5', 'h0', 'string', 'dedup', 'W', 'edges', 'gnn', 'g', 'headgnn', 'pgnn'],
  early: ['seq', 'prott5', 'h0', 'string', 'dedup', 'W', 'P', 'fixprop', 'edges', 'gnn', 'g', 'early', 'headearly', 'outearly'],
};
ROUTES.late = [...new Set([...ROUTES.fixed, ...ROUTES.gnn, 'late', 'out'])];
const ROUTE_ORDER = ['all', 'fixed', 'gnn', 'early', 'late'];
const LABEL = { all: 'Todas', fixed: '/Fixed', gnn: '/GNN', early: '/Early', late: '/Late' };

const box = (id) => { const [x, y, w, , lines] = NODES[id]; const h = lines.length > 1 ? 64 : 48; return { x, y: y - h / 2, w, h, cx: x + w / 2, cy: y }; };
const R = (id) => { const b = box(id); return [b.x + b.w, b.cy]; };
const L = (id) => { const b = box(id); return [b.x, b.cy]; };
const T = (id, dx = 0) => { const b = box(id); return [b.cx + dx, b.y]; };
const Bt = (id, dx = 0) => { const b = box(id); return [b.cx + dx, b.y + b.h]; };
const hz = (a, b) => { const [x1, y1] = R(a), [x2, y2] = L(b); const m = (x1 + x2) / 2; return `M${x1} ${y1} C${m} ${y1} ${m} ${y2} ${x2} ${y2}`; };
// [from, to, colour, path]
const EDGES = [
  ['seq', 'prott5', 'seq', hz('seq', 'prott5')],
  ['prott5', 'h0', 'seq', hz('prott5', 'h0')],
  ['h0', 'fixprop', 'seq', (() => { const [x1, y1] = R('h0'), [x2, y2] = T('fixprop', -40); return `M${x1} ${y1 - 8} C${x2 - 60} ${y1 - 8} ${x2} ${y1} ${x2} ${y2}`; })()],
  ['h0', 'gnn', 'seq', (() => { const [x1] = R('h0'); const [, y2] = L('gnn'); return `M${x1} ${A + 16} H672 Q684 ${A + 16} 684 ${A + 28} V${y2 - 12} Q684 ${y2} 696 ${y2} H700`; })()],
  ['string', 'dedup', 'net', hz('string', 'dedup')],
  ['dedup', 'W', 'net', hz('dedup', 'W')],
  ['W', 'P', 'net', hz('W', 'P')],
  ['P', 'fixprop', 'net', (() => { const [x1, y1] = T('P'); const [x2, y2] = L('fixprop'); return `M${x1} ${y1} C${x1} ${y2 + 10} ${x1 + 20} ${y2} ${x2} ${y2}`; })()],
  ['W', 'edges', 'net', (() => { const [x1, y1] = Bt('W'); const [x2, y2] = L('edges'); return `M${x1} ${y1} C${x1} ${y2} ${x1 + 40} ${y2} ${x2} ${y2}`; })()],
  ['edges', 'gnn', 'net', hz('edges', 'gnn')],
  ['gnn', 'g', 'net', hz('gnn', 'g')],
  ['g', 'headgnn', 'net', hz('g', 'headgnn')],
  ['fixprop', 'headfix', 'net', hz('fixprop', 'headfix')],
  ['headfix', 'pfix', 'fuse', hz('headfix', 'pfix')],
  ['headgnn', 'pgnn', 'fuse', hz('headgnn', 'pgnn')],
  ['pfix', 'late', 'fuse', hz('pfix', 'late')],
  ['pgnn', 'late', 'fuse', hz('pgnn', 'late')],
  ['late', 'out', 'fuse', (() => { const [x1, y1] = T('late'); const [, y2] = Bt('out'); return `M${x1} ${y1} V${y2}`; })()],
  ['fixprop', 'early', 'net', (() => { const [x1, y1] = R('fixprop'); const [, y2] = T('early'); return `M${x1} ${y1 + 16} H898 Q908 ${y1 + 16} 908 ${y1 + 26} V${y2}`; })()],
  ['g', 'early', 'net', (() => { const [x1, y1] = Bt('g'); const [, y2] = T('early'); return `M${x1} ${y1} V${y2}`; })()],
  ['early', 'headearly', 'fuse', hz('early', 'headearly')],
  ['headearly', 'outearly', 'fuse', hz('headearly', 'outearly')],
];
const MATH = { h0: 'i:pipe-h0', W: 'i:pipe-W', P: 'i:pipe-P', HT: 'i:pipe-HT', g: 'i:pipe-g', pfix: 'i:pipe-pfix', pgnn: 'i:pipe-pgnn', gamma: 'i:pipe-gamma' };

export function mount(el, { reduced = false, math = {} } = {}) {
  const fig = el.querySelector('.pipe-fig');
  let n = 0, route = 'all', figMode = false, playing = false, raf = 0, t0 = 0, tNow = 0;
  const line = (s) => s.replace(/@(\w+)/g, (_, k) => math[MATH[k]] || k);
  el.classList.add('pi');
  el.innerHTML = `
    <div class="controls pi-controls">
      <span class="lbl">rota</span>
      <span class="seg" role="group" aria-label="Rota">${ROUTE_ORDER.map((r) => `<button class="btn" type="button" id="pipe-${r}" data-route="${r}">${LABEL[r]}</button>`).join('')}</span>
      <button class="btn pi-figbtn" type="button" id="pipe-fig" aria-pressed="false">Figura da dissertação</button>
    </div>
    <div class="pi-stage">
      <svg class="pi-edges" viewBox="0 0 ${STAGE_W} ${STAGE_H}" aria-hidden="true">
        ${EDGES.map(([a, b, c, d], i) => `<g class="pi-edge" data-i="${i}" data-a="${a}" data-b="${b}"><path class="pi-base ${c}" d="${d}"/><path class="pi-dash ${c}" d="${d}"/></g>`).join('')}
        <g class="pi-dots"></g>
      </svg>
      ${Object.entries(NODES).map(([id, [x, , w, kind, lines, tip]]) => {
        const b = box(id);
        return `<div class="pi-node ${kind}" data-id="${id}" data-interactive tabindex="0" role="img" aria-label="${tip}" data-tip="${tip}" style="left:${x}px; top:${b.y}px; width:${w}px; height:${b.h}px">${lines.map((s, k) => `<span class="${k ? 'l2' : 'l1'}">${line(s)}</span>`).join('')}</div>`;
      }).join('')}
      <div class="tip pi-tip" hidden></div>
    </div>
    <div class="pi-figwrap"><div class="plate"></div><p class="cap">Dissertação, Fig. 5.6, recortada acima do bloco de fusão tardia (sua lista de regras não confere com o texto; ver S29)</p></div>`;
  if (fig) el.querySelector('.pi-figwrap .plate').append(fig);

  const nodes = Object.fromEntries([...el.querySelectorAll('.pi-node')].map((d) => [d.dataset.id, d]));
  const edges = [...el.querySelectorAll('.pi-edge')];
  const dots = el.querySelector('.pi-dots');
  const tipEl = el.querySelector('.pi-tip');
  const lens = edges.map((g) => g.querySelector('.pi-base').getTotalLength());

  const visibleSet = () => (n === 0 ? new Set() : n === 1 ? new Set(BRANCH.seq) : n === 2 ? new Set([...BRANCH.seq, ...BRANCH.net]) : new Set(Object.keys(NODES)));
  const activeSet = () => new Set(n >= 3 ? ROUTES[route] : [...visibleSet()]);

  function apply(animateIn) {
    const vis = visibleSet(), act = activeSet();
    for (const [id, d] of Object.entries(nodes)) d.style.opacity = !vis.has(id) ? 0 : act.has(id) ? 1 : 0.15;
    edges.forEach((g, i) => {
      const { a, b } = g.dataset;
      const v = vis.has(a) && vis.has(b), on = v && act.has(a) && act.has(b);
      const was = g.classList.contains('vis');
      g.classList.toggle('vis', v); g.classList.toggle('on', on);
      g.style.opacity = !v ? 0 : on ? 1 : 0.12;
      if (animateIn && v && !was && !reduced) {
        const p = g.querySelector('.pi-base');
        // draw-in without touching inline styles, so the DOM is the same going forward or back
        p.animate([{ strokeDasharray: lens[i], strokeDashoffset: lens[i] }, { strokeDasharray: lens[i], strokeDashoffset: 0 }],
          { duration: 700, delay: 90 * (i % 6), easing: 'cubic-bezier(.2,.7,.2,1)', fill: 'backwards' });
      }
    });
    for (const r of ROUTE_ORDER) {
      const btn = el.querySelector(`#pipe-${r}`);
      btn.setAttribute('aria-pressed', String(n >= 3 && r === route));
      btn.disabled = n < 3;
    }
    el.classList.toggle('pi-figmode', figMode);
    el.querySelector('#pipe-fig').setAttribute('aria-pressed', String(figMode));
    drawDots(tNow);
  }

  // particles: two per active edge, 150 px/s, deterministic in t
  function drawDots(t) {
    if (reduced) { dots.innerHTML = ''; return; }
    let s = '';
    edges.forEach((g, i) => {
      if (!g.classList.contains('on')) return;
      const p = g.querySelector('.pi-base'), len = lens[i], col = EDGES[i][2];
      for (let k = 0; k < 2; k++) {
        const d = ((t * 150 + k * len / 2 + i * 37) % len + len) % len;
        const pt = p.getPointAtLength(d);
        s += `<circle class="${col}" cx="${pt.x.toFixed(1)}" cy="${pt.y.toFixed(1)}" r="4.5"/>`;
      }
    });
    dots.innerHTML = s;
  }
  function loop(ts) {
    if (!playing) return;
    if (!t0) t0 = ts;
    tNow = (ts - t0) / 1000;
    drawDots(tNow);
    raf = requestAnimationFrame(loop);
  }

  el.addEventListener('click', (e) => {
    const r = e.target.closest('[data-route]');
    if (r && !r.disabled) { route = r.dataset.route; apply(false); }
    if (e.target.closest('#pipe-fig')) { figMode = !figMode; apply(false); }
  });
  const showTip = (d) => {
    tipEl.textContent = d.dataset.tip; tipEl.hidden = false;
    const x = Math.min(parseFloat(d.style.left), STAGE_W - 520);
    const y = parseFloat(d.style.top) + parseFloat(d.style.height) + 8;
    tipEl.style.left = `${x}px`; tipEl.style.top = `${y > STAGE_H - 50 ? parseFloat(d.style.top) - 48 : y}px`;
  };
  for (const d of Object.values(nodes)) {
    d.addEventListener('mouseenter', () => showTip(d)); d.addEventListener('focus', () => showTip(d));
    d.addEventListener('mouseleave', () => { tipEl.hidden = true; }); d.addEventListener('blur', () => { tipEl.hidden = true; });
  }
  el.classList.toggle('pi-instant', reduced);
  apply(false);

  return {
    step(k) {
      const fwd = k > n; n = k;
      route = k >= 3 ? ROUTE_ORDER[k - 2] : 'all';
      apply(fwd);
    },
    render(t) { // GIF: All, /Fixed, /GNN, /Early, /Late, 2 s each
      playing = false; cancelAnimationFrame(raf);
      el.classList.add('pi-instant');
      n = 6; route = ROUTE_ORDER[Math.floor(t / 2) % ROUTE_ORDER.length]; tNow = t;
      apply(false);
    },
    duration: 10,
    play() { if (reduced || playing) return; playing = true; t0 = 0; raf = requestAnimationFrame(loop); },
    pause() { playing = false; cancelAnimationFrame(raf); },
    destroy() { playing = false; cancelAnimationFrame(raf); el.innerHTML = ''; },
    state() {
      return { step: n, route, figure: figMode, visible: [...visibleSet()], active: [...activeSet()],
        opacity: Object.fromEntries(Object.entries(nodes).map(([id, d]) => [id, +d.style.opacity])) };
    },
  };
}
