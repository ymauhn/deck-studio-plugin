// INT-FOLD (S03): schematic folding of a 54-bead chain into a three-helix bundle.
// Geometry (Å): helices of 15 residues, radius 2.3, rise 1.5 per residue, 100° per residue,
// right-handed, antiparallel, axes on a triangle of side 10, loops of 4 and 3 residues,
// one tail bead at each end. Coordinates are procedural; nothing is downloaded.
//
// Cycle (CYCLE s): hold extended, fold N-terminal first with ease-in-out, hold folded while
// rotating at 15°/s about the vertical axis, unfold quickly. t = 0 is the extended chain.

const N = 54;
const T_HOLD0 = 0.5, T_FOLD = 2.6, T_HOLD = 4, T_UNFOLD = 0.8;
const CYCLE = T_HOLD0 + T_FOLD + T_HOLD + T_UNFOLD; // 7.9 s
const T_FOLDED = T_HOLD0 + T_FOLD; // rotation starts here
const WIN = 1.1; // per-bead fold window inside T_FOLD
const SPIN = (15 * Math.PI) / 180; // rad/s
// near 0° (and 60°) the front helix stands between the two back ones: the clearest view
const YAW0 = (-3 * Math.PI) / 180, PITCH = (14 * Math.PI) / 180;
const RAD = Math.PI / 180;

const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const lerp = (a, b, u) => a + (b - a) * u;

// ---------- folded coordinates ----------
function bundle() {
  const R = 2.3, RISE = 1.5, TURN = 100 * RAD, rho = 10 / Math.sqrt(3);
  const axes = [90, 210, 330].map((a) => [rho * Math.cos(a * RAD), rho * Math.sin(a * RAD)]);
  const dir = [1, -1, 1];
  // a right-handed helix along +y: x = R sin t, z = R cos t; the antiparallel one is that
  // helix turned 180° about x (y and z change sign), so handedness is kept
  const at = (h, k, t0) => {
    const t = t0 + k * TURN;
    return [axes[h][0] + R * Math.sin(t), dir[h] * RISE * (k - 7), axes[h][1] + dir[h] * R * Math.cos(t)];
  };
  // phases: helix 1 ends sideways to helix 2; each next helix starts about one loop span
  // (10.5 Å for 4 residues, 9 Å for 3) from the previous end, so loop beads stay apart
  const ux = axes[1][0] - axes[0][0], uz = axes[1][1] - axes[0][1];
  const ph = [Math.atan2(ux, uz) + Math.PI / 2 - 14 * TURN];
  const near = (h, end, d) => {
    let best = 0, err = Infinity;
    for (let a = 0; a < 360; a += 5) {
      const p = at(h, 0, a * RAD), e = Math.abs(Math.hypot(p[0] - end[0], p[1] - end[1], p[2] - end[2]) - d);
      if (e < err) { err = e; best = a * RAD; }
    }
    return best;
  };
  ph[1] = near(1, at(0, 14, ph[0]), 10.5);
  ph[2] = near(2, at(1, 14, ph[1]), 9);
  const helix = [0, 1, 2].map((h) => Array.from({ length: 15 }, (_, k) => at(h, k, ph[h])));
  // loop: quadratic Bezier from one helix end to the next start, bulging away from the bundle
  const loop = (a, b, n) => {
    const m = a.map((v, i) => (v + b[i]) / 2);
    const out = Math.hypot(m[0], m[2]) || 1;
    const c = [m[0] + (m[0] / out) * 3.5, m[1] + Math.sign(m[1]) * 8, m[2] + (m[2] / out) * 3.5];
    return Array.from({ length: n }, (_, j) => {
      const u = (j + 1) / (n + 1);
      return a.map((v, i) => (1 - u) * (1 - u) * v + 2 * u * (1 - u) * c[i] + u * u * b[i]);
    });
  };
  const tail = (p, q) => p.map((v, i) => v + (v - q[i]) * 1.1);
  const pts = [
    tail(helix[0][0], helix[0][1]),
    ...helix[0], ...loop(helix[0][14], helix[1][0], 4),
    ...helix[1], ...loop(helix[1][14], helix[2][0], 3),
    ...helix[2], tail(helix[2][14], helix[2][13]),
  ];
  const c = [0, 1, 2].map((i) => pts.reduce((s, p) => s + p[i], 0) / pts.length);
  return pts.map((p) => p.map((v, i) => v - c[i]));
}
const FOLD = bundle();
const RMAX = Math.max(...FOLD.map((p) => Math.hypot(p[0], p[2])));
const YMAX = Math.max(...FOLD.map((p) => Math.abs(p[1])));

// view transform of a folded bead: yaw about the vertical axis, then a slight pitch
function view(p, yaw) {
  const cy = Math.cos(yaw), sy = Math.sin(yaw);
  const x = p[0] * cy + p[2] * sy, z = -p[0] * sy + p[2] * cy;
  const cp = Math.cos(PITCH), sp = Math.sin(PITCH);
  return [x, p[1] * cp - z * sp, p[1] * sp + z * cp];
}

// phase of the cycle at time t: per-bead fold progress and the rotation angle
function pose(t) {
  t = ((t % CYCLE) + CYCLE) % CYCLE;
  const yaw = YAW0 + SPIN * Math.max(0, t - T_FOLDED);
  let prog, phase;
  if (t < T_HOLD0) { prog = () => 0; phase = 'extended'; }
  else if (t < T_FOLDED) {
    const s = t - T_HOLD0;
    prog = (i) => ease((s - (i / (N - 1)) * (T_FOLD - WIN)) / WIN);
    phase = 'folding';
  } else if (t < T_FOLDED + T_HOLD) { prog = () => 1; phase = 'folded'; }
  else { const u = 1 - ease((t - T_FOLDED - T_HOLD) / T_UNFOLD); prog = () => u; phase = 'unfolding'; }
  return { t, yaw, prog, phase };
}

function rgb(ctx, css, fallback) {
  ctx.fillStyle = fallback;
  ctx.fillStyle = css || fallback; // the canvas normalizes any CSS colour to #rrggbb
  const h = ctx.fillStyle;
  return [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
}
const mix = (a, b, u) => a.map((v, i) => Math.round(lerp(v, b[i], u)));
const css = (c) => `rgb(${c[0]},${c[1]},${c[2]})`;

export function mount(el, { reduced = false } = {}) {
  el.classList.add('fold');
  el.innerHTML = '<canvas class="fold-c" role="img" aria-label="Uma cadeia de 54 esferas se dobra num feixe de três hélices e gira devagar"></canvas><p class="cap">esquemático, não é uma estrutura real</p>';
  const cv = el.querySelector('canvas');
  const ctx = cv.getContext('2d');
  let W = 0, H = 0, k = 1, ext = [], col = null;
  let raf = 0, t0 = 0, now = 0, lastStep = 0, phase = 'extended', angle = YAW0;

  function fit() {
    const w = cv.clientWidth, h = cv.clientHeight;
    if (w === W && h === H && ext.length) return;
    W = w || 520; H = h || 400;
    cv.width = W * 2; cv.height = H * 2;
    k = Math.min((0.8 * H) / (2 * YMAX), (0.7 * W) / (2 * RMAX)); // px per Å for the bundle
    // extended chain in view space: a slightly wavy line across the width, a gentle depth wave
    ext = Array.from({ length: N }, (_, i) => {
      const u = i / (N - 1);
      return [((u - 0.5) * 0.9 * W) / k, (0.045 * H * Math.sin(Math.PI * 2 * 1.25 * u + 0.6)) / k, 0.3 * RMAX * Math.sin(Math.PI * 2 * 1.5 * u)];
    });
  }

  function theme() {
    const s = getComputedStyle(el);
    const v = (n) => s.getPropertyValue(n).trim();
    col = { seq: rgb(ctx, v('--seq'), '#2a78d6'), fuse: rgb(ctx, v('--fuse'), '#1baf7a'), bg: rgb(ctx, v('--slide'), '#fbfcfd') };
  }

  function draw(t, still = false) {
    fit();
    if (!col) theme();
    const p = still ? { yaw: YAW0, prog: () => 1, phase: 'folded' } : pose(t);
    phase = p.phase; angle = p.yaw;
    const us = FOLD.map((_, i) => p.prog(i));
    const pts = FOLD.map((f, i) => {
      const v = view(f, p.yaw), e = ext[i], u = us[i];
      return [lerp(e[0], v[0], u), lerp(e[1], v[1], u), lerp(e[2], v[2], u)];
    });
    ctx.setTransform(2, 0, 0, 2, 0, 0);
    ctx.clearRect(0, 0, W, H);
    const cx = W / 2, cy = H / 2, r0 = 0.7 * k;
    const sx = (q) => cx + q[0] * k, sy = (q) => cy - q[1] * k;
    const front = (z) => 0.5 + 0.5 * Math.tanh(z / 5); // 0 far, 1 near; steep enough to show each coil
    const shade = (i, z) => css(mix(col.bg, mix(col.seq, col.fuse, i / (N - 1)), 0.42 + 0.58 * front(z)));
    // painter's algorithm: bonds and beads sorted far to near; a bond sits just behind its beads
    const items = [];
    for (let i = 0; i < N; i++) items.push({ z: pts[i][2], i, bead: true });
    for (let i = 0; i < N - 1; i++) items.push({ z: Math.min(pts[i][2], pts[i + 1][2]) - 1e-3, i, bead: false });
    items.sort((a, b) => a.z - b.z);
    ctx.lineCap = 'round';
    for (const it of items) {
      const a = pts[it.i];
      if (it.bead) {
        // beads also gather size as they fold, so the extended chain reads as separate beads
        const r = r0 * (0.72 + 0.56 * front(a[2])) * lerp(0.55, 1, us[it.i]);
        ctx.beginPath();
        ctx.arc(sx(a), sy(a), r, 0, Math.PI * 2);
        ctx.fillStyle = shade(it.i, a[2]);
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = css(col.bg);
        ctx.stroke();
      } else {
        const b = pts[it.i + 1];
        ctx.beginPath();
        ctx.moveTo(sx(a), sy(a));
        ctx.lineTo(sx(b), sy(b));
        ctx.lineWidth = 2;
        ctx.strokeStyle = shade(it.i + 0.5, (a[2] + b[2]) / 2);
        ctx.stroke();
      }
    }
  }

  const frame = (ms) => { now = (ms - t0) / 1000; draw(now); raf = requestAnimationFrame(frame); };
  const pause = () => { cancelAnimationFrame(raf); raf = 0; };
  const play = () => { if (reduced || raf) return; t0 = performance.now() - now * 1000; raf = requestAnimationFrame(frame); };
  const still = () => (reduced ? draw(0, true) : draw(now));
  still();

  return {
    // the container is revealed by the slide at fragment 1; the fold restarts from the
    // extended chain when it first becomes visible, otherwise n changes nothing
    step(n) {
      if (lastStep < 1 && n >= 1) { now = 0; t0 = performance.now(); }
      lastStep = n;
      if (!raf) still();
    },
    render(t) { pause(); now = t; draw(t); },
    play, pause,
    destroy() { pause(); el.innerHTML = ''; },
    theme() { col = null; if (!raf) still(); },
    state() { return { t: +(((now % CYCLE) + CYCLE) % CYCLE).toFixed(3), cycle: CYCLE, phase, angle: Math.round((angle * 180) / Math.PI), playing: raf !== 0, beads: N, reduced }; },
  };
}
