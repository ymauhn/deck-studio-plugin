// Deck engine: 1600×900 canvas, fragments, notes, overview, presenter view, themes,
// deep links and the window.deck test API (docs/BUILD.md §3).

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const reducedQuery = matchMedia('(prefers-reduced-motion: reduce)');
const INTERACTIVE = 'button, input, select, textarea, a, label, [data-interactive]';

export function startDeck(registry, ctx) {
  const deckEl = $('#deck');
  const stage = $('#stage');
  const slides = $$('section.slide', stage);
  const mainCount = slides.filter((s) => !s.classList.contains('backup')).length;
  let backupSeen = 0;
  const info = slides.map((s, i) => prepare(s, i));
  let cur = -1, frag = 0, digits = '', pv = null, pvTimer = null, pvStart = 0;

  function prepare(s, i) {
    const backup = s.classList.contains('backup');
    const label = backup ? `B${++backupSeen}` : String(i + 1);
    s.dataset.label = label;
    // header: part label, title, tri-colour rule
    const title = $(':scope > h2.title', s);
    if (title && !s.classList.contains('s-title')) {
      const hd = document.createElement('header');
      hd.className = 'hd';
      hd.innerHTML = `<div class="part">${s.dataset.part || ''}</div>`;
      title.replaceWith(hd);
      hd.append(title, Object.assign(document.createElement('div'), { className: 'rule', innerHTML: '<i></i><i></i><i></i>' }));
    }
    // fragment groups in DOM order; data-f pins a group, otherwise the next one
    let last = 0, max = 0;
    const frags = $$('.f, .fo', s).map((el) => {
      const g = el.dataset.f ? +el.dataset.f : last + 1;
      last = g; max = Math.max(max, g);
      return { el, g, out: el.classList.contains('fo') };
    });
    const steps = Math.max(max, +(s.dataset.steps || 0));
    const comps = $$('[data-component]', s).map((el) => ({
      el, id: el.dataset.component, opts: el.dataset.opts ? JSON.parse(el.dataset.opts) : {}, inst: null,
    }));
    const notes = $('aside.notes', s);
    return { s, label, backup, frags, steps, comps, notes: notes ? notes.innerHTML : '', title: title ? title.textContent : '' };
  }

  function mount(k) {
    for (const c of info[k].comps) {
      if (c.inst) continue;
      const fn = registry[c.id];
      if (!fn) { console.warn(`no component ${c.id}`); continue; }
      c.inst = fn(c.el, { ...ctx, ...c.opts, reduced: reducedQuery.matches, slide: k + 1 });
    }
  }

  // opts.at maps the slide's step to the component's own step (at[f], the last entry beyond
  // its end), so bullets can be split into more steps without touching the component
  const stepOf = (c, f) => (Array.isArray(c.opts.at) ? c.opts.at[Math.min(f, c.opts.at.length - 1)] : f);

  function applyFragments(k, f) {
    for (const { el, g, out } of info[k].frags) el.classList.toggle(out ? 'off' : 'on', g <= f);
  }

  function show(k, f = 0) {
    k = Math.max(0, Math.min(slides.length - 1, k));
    f = Math.max(0, Math.min(info[k].steps, f));
    if (k !== cur && cur >= 0) {
      slides[cur].classList.remove('active');
      for (const c of info[cur].comps) c.inst?.pause?.();
    }
    const entering = k !== cur;
    cur = k; frag = f;
    slides[k].classList.add('active');
    applyFragments(k, f);
    mount(k);
    for (const c of info[k].comps) {
      c.inst?.step?.(stepOf(c, f));
      if (entering && !document.hidden) c.inst?.play?.();
    }
    const it = info[k];
    $('#num').textContent = it.backup ? it.label : `${it.label} / ${mainCount}`;
    deckEl.classList.toggle('no-num', slides[k].classList.contains('s-title'));
    $('#bar i').style.width = `${it.backup ? 100 : ((k + 1) / mainCount) * 100}%`;
    try { if (location.hash !== `#${hashFor(k)}`) history.replaceState(null, '', `#${hashFor(k)}`); } catch (e) { /* sandboxed viewer */ }
    renderNotes();
    syncPresenter();
    document.dispatchEvent(new CustomEvent('deck:change', { detail: state() }));
  }

  const hashFor = (k) => (info[k].backup ? info[k].label.toLowerCase() : String(k + 1));
  function fromHash() {
    const h = location.hash.slice(1).toLowerCase();
    if (/^\d+$/.test(h)) return +h - 1;
    const b = /^b(\d+)$/.exec(h);
    if (b) { const k = info.findIndex((x) => x.label.toLowerCase() === `b${b[1]}`); return k < 0 ? null : k; }
    return null;
  }

  function next() {
    if (frag < info[cur].steps) show(cur, frag + 1);
    else if (cur < slides.length - 1) show(cur + 1, 0);
  }
  function prev() {
    if (frag > 0) show(cur, frag - 1);
    else if (cur > 0) show(cur - 1, info[cur - 1].steps);
  }

  // ---------- scaling ----------
  function fit() {
    const w = deckEl.clientWidth, h = deckEl.clientHeight;
    stage.style.setProperty('--s', Math.min(w / 1600, h / 900));
    if (deckEl.classList.contains('ov')) {
      const cols = w < 900 ? 2 : 6;
      deckEl.style.setProperty('--cols', cols);
      deckEl.style.setProperty('--z', (w - 24) / (cols * 1600 + (cols - 1) * 80 + 160));
    }
  }
  addEventListener('resize', fit);

  // ---------- overview ----------
  function toggleOverview(force) {
    const on = force ?? !deckEl.classList.contains('ov');
    if (on) {
      info.forEach((it, k) => {
        mount(k);
        for (const c of it.comps) { c.inst?.pause?.(); c.inst?.step?.(stepOf(c, it.steps)); }
      });
      deckEl.classList.add('ov');
      fit();
      slides[cur].scrollIntoView({ block: 'center' });
    } else {
      deckEl.classList.remove('ov');
      fit();
      info.forEach((it, k) => { if (k !== cur) applyFragments(k, 0); });
      show(cur, frag);
    }
  }
  stage.addEventListener('click', (e) => {
    if (!deckEl.classList.contains('ov')) return;
    const s = e.target.closest('section.slide');
    if (!s) return;
    e.stopPropagation();
    const k = slides.indexOf(s);
    deckEl.classList.remove('ov');
    fit();
    info.forEach((it, j) => { if (j !== k) applyFragments(j, 0); });
    show(k, 0);
  }, true);

  // ---------- notes, help, presenter ----------
  function renderNotes() {
    $('#notes-title').textContent = `${info[cur].label} · ${info[cur].title}`;
    $('#notes-body').innerHTML = info[cur].notes;
  }
  function toggle(id, force) {
    const el = $(`#${id}`);
    const open = force ?? el.hidden;
    el.hidden = !open;
    if (id === 'notes') { document.body.classList.toggle('notes-open', open); fit(); }
    if (id === 'presenter' && open) startClock();
  }
  document.addEventListener('click', (e) => {
    const b = e.target.closest('[data-close]');
    if (b) { toggle(b.dataset.close, false); if (b.dataset.close === 'presenter') stopClock(); }
  });

  function thumbOf(k) {
    const clone = slides[k].cloneNode(true);
    clone.classList.add('active');
    clone.removeAttribute('id');
    $$('[id]', clone).forEach((n) => n.removeAttribute('id'));
    $$('.fo', clone).forEach((n) => n.classList.add('off'));
    return clone;
  }
  function presenterHTML() {
    const nk = cur + 1 < slides.length ? cur + 1 : null;
    return {
      pos: `${info[cur].label} / ${mainCount} · step ${frag} of ${info[cur].steps}`,
      notes: `<h3 style="margin:0 0 .4em;font:650 30px/1.1 var(--font-display)">${info[cur].title}</h3>${info[cur].notes}`,
      next: nk === null ? null : thumbOf(nk),
    };
  }
  function placeThumb(box, node) {
    box.replaceChildren();
    if (!node) return;
    box.append(node);
    const sc = box.clientWidth / 1600;
    node.style.transform = `scale(${sc})`;
  }
  function syncPresenter() {
    const p = presenterHTML();
    if (!$('#presenter').hidden) {
      $('#pv-pos').textContent = p.pos;
      $('#pv-notes').innerHTML = p.notes;
      placeThumb($('#pv-thumb'), p.next);
    }
    if (pv && !pv.closed) {
      const d = pv.document;
      d.getElementById('pv-pos').textContent = p.pos;
      d.getElementById('pv-notes').innerHTML = p.notes;
      placeThumb(d.getElementById('pv-thumb'), p.next && d.importNode(p.next, true));
    }
  }
  function startClock() {
    pvStart = pvStart || Date.now();
    clearInterval(pvTimer);
    pvTimer = setInterval(() => {
      const s = Math.floor((Date.now() - pvStart) / 1000);
      const t = `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
      const a = $('#pv-clock'); if (a) a.textContent = t;
      if (pv && !pv.closed) pv.document.getElementById('pv-clock').textContent = t;
    }, 1000);
  }
  function stopClock() { if (!(pv && !pv.closed)) { clearInterval(pvTimer); pvStart = 0; } }
  function openPresenter() {
    try { pv = window.open('', 'nexusgo-presenter', 'width=1200,height=760'); } catch (e) { pv = null; }
    if (pv && pv.document) {
      const css = $$('style').map((s) => s.textContent).join('\n');
      pv.document.open();
      pv.document.write(`<!doctype html><html lang="en" data-theme="${document.documentElement.dataset.theme || ''}"><head><meta charset="utf-8"><title>Presenter · NEXUS-GO</title><style>${css}</style></head><body style="overflow:hidden"><div id="presenter">${$('#presenter').innerHTML}</div></body></html>`);
      pv.document.close();
      pv.document.querySelector('[data-close]')?.remove();
      pv.addEventListener('keydown', onKey);
      pv.addEventListener('resize', syncPresenter);
      startClock();
      syncPresenter();
    } else {
      toggle('presenter', true);
      syncPresenter();
    }
  }

  // ---------- theme, fullscreen ----------
  function toggleTheme() {
    const root = document.documentElement;
    const dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark';
    for (const it of info) for (const c of it.comps) c.inst?.theme?.();
    document.dispatchEvent(new CustomEvent('deck:theme'));
  }
  function toggleFullscreen() {
    try {
      if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
      else document.documentElement.requestFullscreen().catch(() => {});
    } catch (e) { /* not allowed here */ }
  }

  // ---------- input ----------
  function onKey(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const t = e.target;
    const field = t && t.closest && t.closest('input, select, textarea');
    const onButton = t && t.closest && t.closest('button');
    const k = e.key;
    if (field && !['PageDown', 'PageUp', 'Escape'].includes(k)) return;
    if (onButton && (k === ' ' || k === 'Enter') && !digits) return;
    if (/^[0-9]$/.test(k)) { digits += k; return; }
    if ((k === 'g' || k === 'G' || k === 'Enter') && digits) {
      e.preventDefault();
      const n = +digits; digits = '';
      if (n >= 1 && n <= slides.length) show(n - 1, 0);
      return;
    }
    digits = '';
    const act = {
      ArrowRight: next, ' ': next, PageDown: next, Enter: next, ArrowDown: next,
      ArrowLeft: prev, PageUp: prev, Backspace: prev, ArrowUp: prev,
      Home: () => show(0, 0), End: () => show(mainCount - 1, info[mainCount - 1].steps),
      o: () => toggleOverview(), O: () => toggleOverview(),
      n: () => toggle('notes'), N: () => toggle('notes'),
      p: openPresenter, P: openPresenter,
      t: toggleTheme, T: toggleTheme,
      f: toggleFullscreen, F: toggleFullscreen,
      b: () => mainCount < slides.length && show(mainCount, 0), B: () => mainCount < slides.length && show(mainCount, 0),
      '?': () => toggle('help'),
      Escape: () => { toggleOverview(false); toggle('help', false); toggle('presenter', false); },
    }[k];
    if (!act) return;
    e.preventDefault();
    if (deckEl.classList.contains('ov') && !['o', 'O', 'Escape', 't', 'T', 'f', 'F', '?'].includes(k)) toggleOverview(false);
    act();
  }
  addEventListener('keydown', onKey);

  deckEl.addEventListener('click', (e) => {
    if (deckEl.classList.contains('ov') || e.target.closest(INTERACTIVE)) return;
    if (e.clientX < innerWidth / 3) prev(); else next();
  });
  let touch = null;
  deckEl.addEventListener('touchstart', (e) => { const p = e.changedTouches[0]; touch = { x: p.clientX, y: p.clientY }; }, { passive: true });
  deckEl.addEventListener('touchend', (e) => {
    if (!touch || deckEl.classList.contains('ov')) return;
    const p = e.changedTouches[0], dx = p.clientX - touch.x, dy = p.clientY - touch.y;
    touch = null;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) { e.preventDefault(); dx < 0 ? next() : prev(); }
  });
  addEventListener('hashchange', () => { const k = fromHash(); if (k !== null && k !== cur) show(k, 0); });
  document.addEventListener('visibilitychange', () => {
    for (const c of info[cur]?.comps || []) document.hidden ? c.inst?.pause?.() : c.inst?.play?.();
  });

  // ---------- test API ----------
  function state() {
    return { slide: cur + 1, fragment: frag, fragmentsOnSlide: info[cur].steps, total: mainCount, backups: slides.length - mainCount, label: info[cur].label };
  }
  window.deck = {
    go: (n, f = 0) => show(n - 1, f),
    next, prev, state,
    steps: () => info.map((it) => it.steps),
    labels: () => info.map((it) => it.label),
    component: (id, n) => {
      for (const [k, it] of info.entries()) {
        if (n && k !== n - 1) continue;
        for (const c of it.comps) if (c.id === id) { if (!c.inst) mount(k); return c.inst; }
      }
      return null;
    },
    overview: toggleOverview,
    notes: (o) => toggle('notes', o),
    theme: toggleTheme,
  };

  fit();
  show(fromHash() ?? 0, 0);
}
