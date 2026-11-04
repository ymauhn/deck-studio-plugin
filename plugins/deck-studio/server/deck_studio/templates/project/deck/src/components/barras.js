// BARRAS: horizontal bars to scale that grow step by step, the value counting at the tip, a tooltip on hover or focus
// and the Table button. opts: { itens: [{ rotulo, valor, cor?: "c1"|"c2"|"c3", passo? }], unidade?, casas?, min?, max?,
// largura? (px, the element width), rotulos? (px of the label column, 260), juntas? (all bars at step 1), coluna? (table header) }
COMPONENTS.BARRAS = (el, o) => {
  const itens = o.itens || [], casas = o.casas ?? 0, un = o.unidade ? ` ${o.unidade}` : '';
  const W = o.largura || el.clientWidth || 900, LW = o.rotulos || 260, RH = 58, BH = 30, TOP = 8;
  const vals = itens.map((i) => i.valor);
  const tk = K.ticks(Math.min(0, o.min ?? Math.min(...vals)), o.max ?? Math.max(...vals)), lo = Math.min(0, tk[0]);
  const hi = Math.max(o.max ?? 0, tk[tk.length - 1], ...vals);
  const x = K.lin(lo, hi, LW, W - 90), H = TOP + itens.length * RH + 36;
  el.classList.add('cp', 'cp-barras');
  const view = K.html(el, 'div', 'cp-view');
  const s = K.svg(view, 'svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': o.titulo || itens.map((i) => `${i.rotulo}: ${K.fmt(i.valor, casas)}${un}`).join('; ') });
  const axis = K.svg(s, 'g', { class: 'cp-axis' });
  for (const t of tk) {
    K.svg(axis, 'line', { class: 'grid', x1: x(t), x2: x(t), y1: TOP, y2: H - 30 });
    K.svg(axis, 'text', { class: 'tick', x: x(t), y: H - 6, 'text-anchor': 'middle' }, K.fmt(t, K.dec(t)));
  }
  K.svg(axis, 'line', { class: 'base', x1: x(0), x2: x(0), y1: TOP, y2: H - 30 });
  const rows = itens.map((it, i) => {
    const y = TOP + i * RH + (RH - BH) / 2, x0 = x(0), x1 = x(it.valor);
    const g = K.svg(s, 'g', { class: 'cp-row', tabindex: 0, 'data-interactive': '', 'data-tl': it.rotulo, 'data-tv': `${K.fmt(it.valor, casas)}${un}` });
    K.svg(g, 'text', { class: 'lab', x: LW - 14, y: y + BH / 2 + 7, 'text-anchor': 'end' }, it.rotulo);
    const bar = K.svg(g, 'rect', { class: 'bar', x: Math.min(x0, x1), y, width: Math.max(2, Math.abs(x1 - x0)), height: BH, rx: 4, fill: K.color(it.cor) });
    bar.style.transformOrigin = it.valor < 0 ? 'right' : 'left';
    const val = K.svg(g, 'text', { class: 'val', x: it.valor < 0 ? x1 - 10 : x1 + 10, y: y + BH / 2 + 7, 'text-anchor': it.valor < 0 ? 'end' : 'start' }, `${K.fmt(it.valor, casas)}${un}`);
    return { g, val, it, passo: it.passo ?? (o.juntas ? 1 : i + 1), on: false, stop: () => {} };
  });
  K.tips(view);
  K.table(el, view, [o.coluna || '', o.unidade ? `{{UI_VALUE}} (${o.unidade})` : '{{UI_VALUE}}'], itens.map((i) => [i.rotulo, K.fmt(i.valor, casas)]));
  return {
    step(n) {
      for (const r of rows) {
        const on = n >= r.passo;
        if (on === r.on) continue;
        r.on = on;
        r.g.classList.toggle('on', on);
        r.stop();
        r.stop = on ? K.count(o, 0, r.it.valor, 700, (v) => { r.val.textContent = `${K.fmt(v, casas)}${un}`; }) : () => {};
      }
    },
    pause() { for (const r of rows) { r.stop(); r.val.textContent = `${K.fmt(r.it.valor, casas)}${un}`; } },
  };
};
