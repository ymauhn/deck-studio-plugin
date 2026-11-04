// PONTOS: a dot (dumbbell) chart. One row per item, one dot per series; each step brings a series, whose dot slides
// from the previous series' dot, showing how much each item changed (before and after, method A against B).
// opts: { series: [{ nome, cor?, passo? }], itens: [{ rotulo, valores: [one per series] }], unidade?, casas?, min?,
//         max?, largura? (the element width), rotulos? (260) }
COMPONENTS.PONTOS = (el, o) => {
  const ser = o.series || [], itens = o.itens || [], casas = o.casas ?? 0, un = o.unidade ? ` ${o.unidade}` : '';
  const W = o.largura || el.clientWidth || 900, LW = o.rotulos || 260, RH = 56, TOP = 54;
  const all = itens.flatMap((i) => i.valores);
  const span = Math.max(...all) - Math.min(...all) || 1;
  const tk = K.ticks(o.min ?? Math.min(...all) - span * 0.08, o.max ?? Math.max(...all) + span * 0.08, 5);
  const x = K.lin(tk[0], tk[tk.length - 1], LW, W - 30), H = TOP + itens.length * RH + 36;
  el.classList.add('cp', 'cp-pontos');
  const view = K.html(el, 'div', 'cp-view');
  const s = K.svg(view, 'svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': o.titulo || itens.map((i) => `${i.rotulo}: ${i.valores.map((v, j) => `${ser[j]?.nome} ${K.fmt(v, casas)}`).join(', ')}`).join('; ') });
  const legend = K.svg(s, 'g', { class: 'legend' });
  let lx = LW;
  const keys = ser.map((sr) => {
    const g = K.svg(legend, 'g', { class: 'key' });
    K.svg(g, 'circle', { cx: lx + 9, cy: 18, r: 9, fill: K.color(sr.cor) });
    K.svg(g, 'text', { x: lx + 26, y: 25 }, sr.nome);
    lx += 46 + sr.nome.length * 12;
    return g;
  });
  for (const t of tk) {
    K.svg(s, 'line', { class: 'grid', x1: x(t), x2: x(t), y1: TOP - 10, y2: H - 30 });
    K.svg(s, 'text', { class: 'tick', x: x(t), y: H - 6, 'text-anchor': 'middle' }, K.fmt(t, K.dec(t)));
  }
  const rows = itens.map((it, i) => {
    const cy = TOP + i * RH + RH / 2;
    K.svg(s, 'text', { class: 'lab', x: LW - 18, y: cy + 7, 'text-anchor': 'end' }, it.rotulo);
    const link = K.svg(s, 'line', { class: 'link', x1: x(it.valores[0]), x2: x(it.valores[0]), y1: cy, y2: cy });
    const dots = it.valores.map((v, j) => {
      const d = K.svg(s, 'circle', { class: 'dot', cx: x(it.valores[Math.max(0, j - 1)]), cy, r: 11, fill: K.color(ser[j]?.cor),
        tabindex: 0, 'data-interactive': '', 'data-tl': `${it.rotulo}, ${ser[j]?.nome}`, 'data-tv': `${K.fmt(v, casas)}${un}` });
      return d;
    });
    return { it, link, dots };
  });
  K.tips(view);
  K.table(el, view, ['', ...ser.map((sr) => sr.nome)], itens.map((i) => [i.rotulo, ...i.valores.map((v) => K.fmt(v, casas))]));
  const passo = (j) => ser[j]?.passo ?? j + 1;
  return {
    step(n) {
      ser.forEach((_, j) => keys[j].classList.toggle('on', n >= passo(j)));
      for (const r of rows) {
        const on = r.it.valores.map((_, j) => n >= passo(j));
        r.dots.forEach((d, j) => {
          d.classList.toggle('on', on[j]);
          d.style.cx = `${x(r.it.valores[on[j] ? j : Math.max(0, j - 1)])}px`;
        });
        const vis = r.it.valores.filter((_, j) => on[j]);
        r.link.classList.toggle('on', vis.length > 1);
        if (vis.length) {
          r.link.setAttribute("x1", x(Math.min(...vis)));
          r.link.setAttribute("x2", x(Math.max(...vis)));
        }
      }
    },
  };
};
