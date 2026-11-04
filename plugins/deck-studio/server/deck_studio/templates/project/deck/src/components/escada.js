// ESCADA: a staircase chart. Each stair is a value drawn at its step (the first is the starting point), with the
// difference from the one before written on it ("+1.8"): gains that add up (ablation, versions, stages).
// opts: { degraus: [{ rotulo, valor, cor?, passo? }], unidade?, casas?, min?, max?, largura? (the element width), altura? (420) }
COMPONENTS.ESCADA = (el, o) => {
  const ds = o.degraus || [], casas = o.casas ?? 0, un = o.unidade ? ` ${o.unidade}` : '';
  const W = o.largura || el.clientWidth || 900, H = o.altura || 420, L = 70, B = H - 70, T = 46;
  const vals = ds.map((d) => d.valor);
  const span = Math.max(...vals) - Math.min(...vals) || 1;
  const tk = K.ticks(o.min ?? Math.min(...vals) - span * 0.15, o.max ?? Math.max(...vals) + span * 0.1, 4);
  const y = K.lin(tk[0], tk[tk.length - 1], B, T), cw = (W - L - 10) / ds.length;
  el.classList.add('cp', 'cp-escada');
  const view = K.html(el, 'div', 'cp-view');
  const s = K.svg(view, 'svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': o.titulo || ds.map((d) => `${d.rotulo}: ${K.fmt(d.valor, casas)}${un}`).join('; ') });
  for (const t of tk) {
    K.svg(s, 'line', { class: 'grid', x1: L, x2: W - 10, y1: y(t), y2: y(t) });
    K.svg(s, 'text', { class: 'tick', x: L - 10, y: y(t) + 6, 'text-anchor': 'end' }, K.fmt(t, K.dec(t)));
  }
  const steps = ds.map((d, i) => {
    const x0 = L + i * cw, x1 = x0 + cw, yv = y(d.valor), prev = i ? y(ds[i - 1].valor) : yv;
    const g = K.svg(s, 'g', { class: 'cp-step', tabindex: 0, 'data-interactive': '', 'data-tl': d.rotulo, 'data-tv': `${K.fmt(d.valor, casas)}${un}` });
    K.svg(g, 'path', { class: 'line', d: `M${x0} ${prev} V${yv} H${x1}`, pathLength: 1, stroke: K.color(d.cor || 'c1') });
    K.svg(g, 'rect', { class: 'area', x: x0, y: yv, width: cw, height: B - yv, fill: K.color(d.cor || 'c1') });
    K.svg(g, 'text', { class: 'val', x: x0 + cw / 2, y: yv - 14, 'text-anchor': 'middle' }, `${K.fmt(d.valor, casas)}${un}`);
    if (i) K.svg(g, 'text', { class: 'delta', x: x0 + 8, y: (prev + yv) / 2 + 6, fill: K.color(d.cor || 'c1') }, K.signed(d.valor - ds[i - 1].valor, casas));
    const lab = K.svg(g, 'text', { class: 'lab', x: x0 + cw / 2, y: B + 30, 'text-anchor': 'middle' }, d.rotulo);
    lab.style.fontSize = cw < 150 ? '17px' : '';
    return { g, passo: d.passo ?? i + 1 };
  });
  K.svg(s, 'line', { class: 'base', x1: L, x2: W - 10, y1: B, y2: B });
  K.tips(view);
  K.table(el, view, ['', o.unidade ? `{{UI_VALUE}} (${o.unidade})` : '{{UI_VALUE}}', '{{UI_DIFFERENCE}}'],
    ds.map((d, i) => [d.rotulo, K.fmt(d.valor, casas), i ? K.signed(d.valor - ds[i - 1].valor, casas) : '']));
  return { step(n) { for (const st of steps) st.g.classList.toggle('on', n >= st.passo); } };
};
