// FLUXO: the method's diagram, animated. Boxes on a (col, lin) grid joined by arrows where the flow runs; the columns
// come in step by step, and the route buttons light only one variant's path (the rest fade). Each box's tooltip shows
// on hover or Tab. opts: { nos: [{ id, rotulo, sub?, cor?, col, lin, dica?, passo? }], ligacoes: [{ de, para, cor? }],
//         rotas?: [{ nome, nos: [ids], nota? }], largura? (the element width), altura? (440) }
COMPONENTS.FLUXO = (el, o) => {
  const nos = o.nos || [], lig = o.ligacoes || [], rotas = o.rotas || [];
  const W = o.largura || el.clientWidth || 1400, H = o.altura || 440;
  const nc = Math.max(...nos.map((n) => n.col)) + 1, nl = Math.max(...nos.map((n) => n.lin)) + 1;
  const cw = W / nc, ch = H / nl, bw = Math.min(260, cw - 56);
  const box = Object.fromEntries(nos.map((n) => {
    const h = n.sub ? 70 : 52, cx = n.col * cw + cw / 2, cy = n.lin * ch + ch / 2;
    return [n.id, { n, x: cx - bw / 2, y: cy - h / 2, w: bw, h, cx, cy }];
  }));
  el.classList.add('cp', 'cp-fluxo');
  const bar = K.html(el, 'div', 'controls cp-controls');
  const nota = K.html(null, 'p', 'cp-nota');
  const stage = K.html(el, 'div', 'cp-stage');
  stage.style.width = `${W}px`;
  stage.style.height = `${H}px`;
  const s = K.svg(stage, 'svg', { class: 'cp-edges', viewBox: `0 0 ${W} ${H}`, width: W, height: H, 'aria-hidden': 'true' });
  const defs = K.svg(s, 'defs');
  const mk = K.svg(defs, 'marker', { id: `cp-arrow-${Math.random().toString(36).slice(2, 8)}`, viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse' });
  K.svg(mk, 'path', { d: 'M0 0L10 5L0 10z', fill: 'var(--ink-2)' });
  const edges = lig.map((l) => {
    const a = box[l.de], b = box[l.para];
    if (!a || !b) throw new Error(`FLUXO: link ${l.de} -> ${l.para} has no box`);
    let d;
    if (a.n.col === b.n.col) {
      const [y1, y2] = b.cy > a.cy ? [a.y + a.h, b.y] : [a.y, b.y + b.h];
      d = `M${a.cx} ${y1} V${y2}`;
    } else {
      const fw = b.cx > a.cx, x1 = fw ? a.x + a.w : a.x, x2 = fw ? b.x : b.x + b.w, m = (x1 + x2) / 2;
      d = `M${x1} ${a.cy} C${m} ${a.cy} ${m} ${b.cy} ${x2} ${b.cy}`;
    }
    const g = K.svg(s, 'g', { class: 'cp-edge' });
    const c = K.color(l.cor || a.n.cor);
    K.svg(g, 'path', { class: 'base', d, stroke: c, 'marker-end': `url(#${mk.id})` });
    K.svg(g, 'path', { class: 'flow', d, stroke: c });
    return { g, l };
  });
  const nodes = nos.map((n) => {
    const b = box[n.id];
    const e = K.html(stage, 'div', 'cp-node');
    Object.assign(e.style, { left: `${b.x}px`, top: `${b.y}px`, width: `${b.w}px`, height: `${b.h}px`, borderColor: K.color(n.cor) });
    K.html(e, 'span', 'l1', n.rotulo);
    if (n.sub) K.html(e, 'span', 'l2', n.sub);
    e.tabIndex = 0;
    e.dataset.interactive = '';
    e.dataset.tl = n.dica || n.rotulo;
    return { e, n, passo: n.passo ?? n.col + 1 };
  });
  el.append(nota);
  let n = 0, rota = null;
  const paint = () => {
    const vis = new Set(nodes.filter((x) => n >= x.passo).map((x) => x.n.id));
    const inRoute = rota ? new Set(rota.nos) : null;
    for (const x of nodes) {
      x.e.classList.toggle('on', vis.has(x.n.id));
      x.e.classList.toggle('dim', !!inRoute && !inRoute.has(x.n.id));
    }
    for (const x of edges) {
      const on = vis.has(x.l.de) && vis.has(x.l.para);
      x.g.classList.toggle('on', on);
      x.g.classList.toggle('dim', !!inRoute && !(inRoute.has(x.l.de) && inRoute.has(x.l.para)));
    }
    nota.textContent = rota?.nota || '';
  };
  if (rotas.length) {
    K.html(bar, 'span', 'lbl', '{{UI_ROUTE}}');
    const seg = K.html(bar, 'span', 'seg');
    const buttons = [{ nome: '{{UI_ALL}}', nos: null }, ...rotas].map((r) => {
      const b = K.html(seg, 'button', 'btn', r.nome);
      b.type = 'button';
      b.setAttribute('aria-pressed', String(!r.nos));
      b.addEventListener('click', () => {
        rota = r.nos ? r : null;
        for (const x of buttons) x.setAttribute('aria-pressed', String(x === b));
        paint();
      });
      return b;
    });
  } else bar.remove();
  K.tips(stage);
  if (K.still(o)) el.classList.add('cp-still');
  return { step(k) { n = k; paint(); }, pause() { el.classList.add('cp-still'); } };
};
