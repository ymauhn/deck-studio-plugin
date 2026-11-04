// INT-RULES (S29): the eleven late-fusion rules of §5.6.2 as a chip row. Hover or focus a chip:
// a popover above the row shows its formula (Eqs. eq:met_ens_*, pre-rendered from
// int-rules.math.json) and its validation AVG wFmax from Table 6.11 (opts.data.late).
// Steps: < 4 hidden (layout kept) · >= 4 visible.

// [id, chip text, row name in the late table, chip row, formula keys, one-line note]
const RULES = [
  ['linear', 'Linear (γ)', 'Linear interpolation (\\gamma)', 0, ['linear'], 'one coefficient γ per ontology'],
  ['max', 'Max', 'Maximum', 0, ['max'], 'element-wise, no parameter'],
  ['min', 'Min', 'Minimum', 0, ['min'], 'element-wise, no parameter'],
  ['ic', 'IC sigmoid', 'IC sigmoid', 0, ['gj', 'ic'], 'term-specific weight from information content'],
  ['degree', 'Degree sigmoid', 'Degree sigmoid', 0, ['beta', 'degree'], 'protein-specific weight from node degree'],
  ['master', 'Master equation', 'Master equation', 0, ['w', 'master'], 'blends the term and protein weights through λ'],
  ['dt', 'decision tree', 'Stacking (decision tree)', 1, ['stack'], 'stacking: a decision tree fitted on four features'],
  ['lr', 'logistic regression', 'Stacking (logistic regression)', 1, ['stack'], 'stacking: a logistic regression fitted on four features'],
  ['mlp', 'MLP', 'Stacking (MLP)', 1, ['stack'], 'stacking: a small MLP fitted on four features'],
  ['rf', 'random forest', 'Stacking (random forest)', 1, ['stack'], 'stacking: a random forest fitted on four features'],
  ['gb', 'gradient boosting', 'Stacking (gradient boosting)', 1, ['stack'], 'stacking: gradient boosting fitted on four features'],
];
const GROUP_BREAK = new Set(['max', 'ic', 'degree', 'master']); // a wider gap before a new family
const WINNER = 'linear';

export function mount(el, opts = {}) {
  const late = opts.data.late.rows;
  const avg = Object.fromEntries(RULES.map(([id, , row]) => {
    const r = late.find((x) => x[0] === row);
    if (!r) throw new Error(`INT-RULES: no row "${row}" in late`);
    return [id, r[late[0].indexOf('AVG')]];
  }));
  const math = (k) => {
    const s = opts.math?.[`rules:${k}`];
    if (!s) throw new Error(`INT-RULES: formula rules:${k} missing`);
    return s;
  };
  const chip = ([id, text]) => `${GROUP_BREAK.has(id) ? '<span class="rls-gap"></span>' : ''}<button type="button" class="btn rls-chip${id === WINNER ? ' rls-win' : ''}" id="rls-${id}" data-rule="${id}">${text}${id === WINNER ? '<span class="rls-tag">best</span>' : ''}</button>`;
  el.classList.add('rls');
  el.setAttribute('data-interactive', '');
  el.innerHTML = `
    <div class="rls-pop" id="rls-pop" role="tooltip" hidden></div>
    <div class="rls-row" role="group" aria-label="Late-fusion rules">${RULES.filter((r) => r[3] === 0).map(chip).join('')}</div>
    <div class="rls-row" role="group" aria-label="Stacking meta-classifiers"><span class="rls-fam">Stacking</span>${RULES.filter((r) => r[3] === 1).map(chip).join('')}</div>`;
  const pop = el.querySelector('.rls-pop');
  let cur = 0, active = null;

  function show(id) {
    const [, text, , , keys, note] = RULES.find((r) => r[0] === id);
    active = id;
    pop.innerHTML = `
      <div class="rls-pop-h"><b>${id === WINNER ? `${text}, best on validation` : text}</b><span>${note}</span></div>
      <div class="rls-pop-eq">${keys.map((k) => `<div>${math(k)}</div>`).join('')}</div>
      <div class="rls-pop-v"><span>Validation, AVG wF<sub>max</sub></span><b class="num">${avg[id].toFixed(2)}</b></div>`;
    pop.hidden = false;
    const b = el.querySelector(`#rls-${id}`);
    for (const c of el.querySelectorAll('.rls-chip')) c.toggleAttribute('aria-describedby', false);
    b.setAttribute('aria-describedby', 'rls-pop');
    const left = b.offsetLeft + b.offsetWidth / 2 - pop.offsetWidth / 2;
    pop.style.left = `${Math.max(0, Math.min(el.clientWidth - pop.offsetWidth, left))}px`;
  }
  function hide() {
    active = null;
    pop.hidden = true;
    for (const c of el.querySelectorAll('.rls-chip')) c.removeAttribute('aria-describedby');
  }
  const on = (e) => { const b = e.target.closest('.rls-chip'); if (b) show(b.dataset.rule); };
  const off = (e) => { const b = e.target.closest('.rls-chip'); if (b && !b.contains(e.relatedTarget)) hide(); };
  el.addEventListener('pointerover', on);
  el.addEventListener('pointerout', off);
  el.addEventListener('focusin', on);
  el.addEventListener('focusout', off);
  el.addEventListener('keydown', (e) => { if (e.key === 'Escape' && active) hide(); });

  function step(n) {
    cur = n;
    el.classList.toggle('rls-on', n >= 4);
    if (n < 4) hide();
  }
  step(0);
  return {
    step,
    render() {}, play() {}, pause() {},
    show, hide,
    destroy() { el.innerHTML = ''; },
    state() { return { visible: cur >= 4, active }; },
  };
}
