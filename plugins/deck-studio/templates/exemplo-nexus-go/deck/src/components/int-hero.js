// INT-HERO (S01, S45): ambient title composition. A short bead chain (sequence) at left, a
// small interaction graph (network) at right, the deck's tri-colour rule joining them.
// Decorative: no labels, no numbers. One seamless loop of CYCLE seconds; t = 0 is a full frame.

const W = 1424, H = 280, CY = 140, CYCLE = 12;
const TAU = Math.PI * 2;
const NS = 'http://www.w3.org/2000/svg';

// bead chain: base radii vary a little, like residues of different size
const BEAD_R = [10, 8.5, 11, 9.5, 10.5, 12, 9, 8.5, 11.5, 10, 9, 11, 10, 10.5];
const BX0 = 30, BDX = 24;
const BX1 = BX0 + BDX * (BEAD_R.length - 1); // 342: the last bead sits on the rule's axis
const RX0 = BX1 + 44, RX1 = 1046, RULE_H = 7; // rule, three equal segments

// graph: [x, y, r], hand placed; edge confidence is a fixed fake value (decorative)
const NODES = [
  [1092, 140, 10], [1160, 72, 9], [1170, 210, 9], [1248, 136, 12], [1256, 44, 7],
  [1288, 230, 8], [1332, 90, 10], [1346, 186, 9], [1398, 46, 7], [1394, 238, 7],
];
const EDGES = [
  [0, 1, .82], [0, 2, .64], [0, 3, .95], [1, 3, .71], [1, 4, .48], [2, 3, .88], [2, 5, .55],
  [3, 6, .97], [3, 7, .78], [4, 6, .60], [5, 7, .90], [6, 7, .66], [6, 8, .52], [7, 9, .74], [5, 9, .42],
];
// drift: amplitude in px and integer frequencies so the loop closes exactly
const DRIFT = NODES.map((_, k) => (k === 0 ? null : { m: 1 + (k % 2), p: k * 1.7, q: k * 0.9 }));

function el(tag, attrs, parent) {
  const n = document.createElementNS(NS, tag);
  for (const k in attrs) n.setAttribute(k, attrs[k]);
  if (parent) parent.append(n);
  return n;
}

export function mount(root, { reduced = false, calm = false } = {}) {
  const amp = calm ? 0.5 : 1;
  root.classList.add('hero');
  root.classList.toggle('hero-calm', calm);
  root.replaceChildren();
  const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, width: '100%', height: '100%', 'aria-hidden': 'true', focusable: 'false' }, root);

  // tri-colour rule
  const seg = (RX1 - RX0) / 3;
  ['seq', 'net', 'fuse'].forEach((c, i) => el('rect', { x: RX0 + i * seg, y: CY - RULE_H / 2, width: seg, height: RULE_H, class: `hero-${c}` }, svg));

  // chain
  const chain = el('g', { class: 'hero-chain' }, svg);
  const bonds = el('polyline', { class: 'hero-bond' }, chain);
  const beads = BEAD_R.map(() => el('circle', {}, chain));

  // graph
  const graph = el('g', { class: 'hero-graph' }, svg);
  const edges = EDGES.map(([, , c]) => el('line', { 'stroke-width': (5.2 * c).toFixed(2) }, graph));
  const nodes = NODES.map(([, , r]) => el('circle', { r }, graph));

  function draw(t) {
    const w = (TAU * t) / CYCLE;
    // chain: a travelling wave pinned at the right end; radius follows the wave's depth
    const pts = [];
    BEAD_R.forEach((r0, i) => {
      const u = 1 - i / (BEAD_R.length - 1);
      const a = 54 * amp * Math.pow(u, 1.1);
      const ph = i * 0.72 - w;
      const depth = u * Math.cos(ph); // a coil seen from the side: near beads larger and darker
      const x = BX0 + i * BDX - 3 * amp * u * Math.cos(ph);
      const y = CY + a * Math.sin(ph);
      beads[i].setAttribute('cx', x.toFixed(2));
      beads[i].setAttribute('cy', y.toFixed(2));
      beads[i].setAttribute('r', (r0 * (1 + 0.2 * depth)).toFixed(2));
      beads[i].setAttribute('fill-opacity', (1 - 0.19 * (u - depth)).toFixed(3));
      pts.push(`${x.toFixed(2)},${y.toFixed(2)}`);
    });
    bonds.setAttribute('points', pts.join(' '));
    // graph: each node drifts on a small closed orbit
    const pos = NODES.map(([x, y], k) => {
      const d = DRIFT[k];
      if (!d) return [x, y];
      return [x + 4 * amp * Math.sin(d.m * w + d.p), y + 4 * amp * Math.cos(w + d.q)];
    });
    pos.forEach(([x, y], k) => { nodes[k].setAttribute('cx', x.toFixed(2)); nodes[k].setAttribute('cy', y.toFixed(2)); });
    EDGES.forEach(([a, b], k) => {
      const e = edges[k];
      e.setAttribute('x1', pos[a][0].toFixed(2)); e.setAttribute('y1', pos[a][1].toFixed(2));
      e.setAttribute('x2', pos[b][0].toFixed(2)); e.setAttribute('y2', pos[b][1].toFixed(2));
      e.setAttribute('stroke-opacity', (0.62 + 0.12 * amp * Math.sin(w + k * 0.8)).toFixed(3));
    });
  }

  let raf = 0, t0 = 0, now = 0;
  const frame = (ms) => { now = (ms - t0) / 1000; draw(now % CYCLE); raf = requestAnimationFrame(frame); };
  const pause = () => { cancelAnimationFrame(raf); raf = 0; };
  draw(0);

  return {
    step() {},
    render(t) { pause(); now = t; draw(((t % CYCLE) + CYCLE) % CYCLE); },
    play() { if (reduced || raf) return; t0 = performance.now() - now * 1000; raf = requestAnimationFrame(frame); },
    pause,
    destroy() { pause(); root.replaceChildren(); },
    state() { return { t: +(now % CYCLE).toFixed(3), cycle: CYCLE, playing: raf !== 0, calm, beads: BEAD_R.length, nodes: NODES.length }; },
  };
}
